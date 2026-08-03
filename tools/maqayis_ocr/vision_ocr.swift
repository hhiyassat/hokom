#!/usr/bin/env swift
//
// vision_ocr.swift — Maqayis OCR v2
//
// Renders one PDF page at 400 DPI and runs two Apple Vision passes:
//   pass 1: ar-SA, usesLanguageCorrection = false  → "raw"
//   pass 2: ar-SA, usesLanguageCorrection = true   → "corrected"
//
// Outputs a single JSON object to stdout matching schemas/page.schema.json
//
// Usage:
//   swift vision_ocr.swift <pdf_path> <page_number_1based> [dpi]
//
// Requires macOS 13+ (VNRecognizeTextRequest with candidateCount)
//

import Foundation
import Vision
import PDFKit
import CoreGraphics
import CryptoKit

// ── helpers ──────────────────────────────────────────────────────────────────

func sha256(of url: URL) -> String {
    guard let data = try? Data(contentsOf: url) else { return "" }
    let digest = SHA256.hash(data: data)
    return digest.map { String(format: "%02x", $0) }.joined()
}

func normalizedBBox(_ obs: VNRecognizedTextObservation) -> [String: Double] {
    let b = obs.boundingBox          // origin = bottom-left, [0,1]
    return ["x": b.origin.x, "y": b.origin.y, "w": b.width, "h": b.height]
}

/// Normalise Arabic text for near-duplicate detection only.
/// We collapse whitespace and remove decorative spaces around
/// punctuation (، . : ؟ ) ( ) so that candidates that differ
/// only in those trivial ways are treated as identical.
/// The *original* text is still stored — we only use the normalised
/// form as a dedup key.
func normalizeForDedup(_ text: String) -> String {
    var s = text
    // Collapse runs of whitespace → single space
    while s.contains("  ") { s = s.replacingOccurrences(of: "  ", with: " ") }
    // Drop space immediately BEFORE closing punctuation / Arabic comma
    for p in ["،", ".", ":", "؟", ")", "]"] {
        s = s.replacingOccurrences(of: " \(p)", with: p)
    }
    // Drop space immediately AFTER opening punctuation
    for p in ["(", "["] {
        s = s.replacingOccurrences(of: "\(p) ", with: p)
    }
    return s.trimmingCharacters(in: .whitespaces)
}

func candidateList(from obs: VNRecognizedTextObservation, count: Int = 3)
    -> [[String: Any]]
{
    // Ask Vision for more candidates than we need so dedup doesn't
    // reduce the final list below `count` unnecessarily.
    let ask = min(count * 2, 10)
    guard let candidates = try? obs.topCandidates(ask) else { return [] }

    var seen  = Set<String>()
    var result: [[String: Any]] = []
    for c in candidates {
        let key = normalizeForDedup(c.string)
        guard !seen.contains(key) else { continue }
        seen.insert(key)
        result.append(["text": c.string, "confidence": Double(c.confidence)])
        if result.count == count { break }
    }
    return result
}

// ── OCR pass ──────────────────────────────────────────────────────────────────

struct OCRObservation {
    let index: Int
    let bbox: [String: Double]
    let candidates: [[String: Any]]
    var topText: String { (candidates.first?["text"] as? String) ?? "" }
}

func runVisionPass(image cgImage: CGImage,
                   corrected: Bool,
                   count: Int = 3) -> [OCRObservation]
{
    var results: [VNRecognizedTextObservation] = []
    let request = VNRecognizeTextRequest { req, _ in
        results = (req.results as? [VNRecognizedTextObservation]) ?? []
    }
    request.recognitionLevel      = .accurate
    request.recognitionLanguages  = ["ar-SA"]
    request.usesLanguageCorrection = corrected
    request.minimumTextHeight     = 0.005   // ~4 px at 800 px height — catch footnotes

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try? handler.perform([request])

    // Vision returns results top→bottom for LTR but we keep natural order
    return results.enumerated().map { (i, obs) in
        OCRObservation(index: i,
                       bbox: normalizedBBox(obs),
                       candidates: candidateList(from: obs, count: count))
    }
}

// ── PDF rendering ─────────────────────────────────────────────────────────────

func renderPage(_ page: PDFPage, dpi: Int) -> CGImage? {
    let mediaBox = page.bounds(for: .mediaBox)
    let scale    = CGFloat(dpi) / 72.0          // PDF points → pixels
    let w = Int(mediaBox.width  * scale)
    let h = Int(mediaBox.height * scale)

    guard let ctx = CGContext(
        data: nil,
        width: w, height: h,
        bitsPerComponent: 8,
        bytesPerRow: w * 4,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
    ) else { return nil }

    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)

    NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: false)
    page.draw(with: .mediaBox, to: ctx)
    NSGraphicsContext.current = nil

    return ctx.makeImage()
}

func savePNG(_ image: CGImage, to url: URL) {
    guard let dest = CGImageDestinationCreateWithURL(url as CFURL,
                                                      kUTTypePNG, 1, nil) else { return }
    CGImageDestinationAddImage(dest, image, nil)
    CGImageDestinationFinalize(dest)
}

// ── merge raw + corrected into line rows ──────────────────────────────────────

// Each output line corresponds to one raw observation (index-aligned).
// We attempt to match corrected observations by nearest bounding-box centre.

func bboxCentreY(_ b: [String: Double]) -> Double {
    (b["y"] ?? 0) + (b["h"] ?? 0) / 2
}

func matchCorrected(_ rawObs: [OCRObservation],
                    _ corrObs: [OCRObservation])
    -> [Int: [OCRObservation]]   // rawIndex → corrected obs (1-to-1 greedy)
{
    var mapping: [Int: [OCRObservation]] = [:]
    var used = Set<Int>()

    for raw in rawObs {
        let rawCy = bboxCentreY(raw.bbox)
        var bestDist = Double.infinity
        var bestIdx  = -1

        for corr in corrObs {
            if used.contains(corr.index) { continue }
            let dist = abs(bboxCentreY(corr.bbox) - rawCy)
            if dist < bestDist { bestDist = dist; bestIdx = corr.index }
        }

        // Accept if centres are within 1% of page height
        if bestDist < 0.01, bestIdx >= 0 {
            mapping[raw.index] = [corrObs[bestIdx]]
            used.insert(bestIdx)
        }
    }
    return mapping
}

// ── main ──────────────────────────────────────────────────────────────────────

let args = CommandLine.arguments
guard args.count >= 3 else {
    fputs("Usage: vision_ocr.swift <pdf_path> <page_1based> [dpi]\n", stderr)
    exit(1)
}

let pdfPath  = args[1]
let pageNum  = Int(args[2]) ?? 1
let dpi      = args.count >= 4 ? (Int(args[3]) ?? 400) : 400

guard let pdfDoc = PDFDocument(url: URL(fileURLWithPath: pdfPath)) else {
    fputs("ERROR: cannot open \(pdfPath)\n", stderr)
    exit(2)
}

let pageIndex = pageNum - 1  // 0-based
guard pageIndex >= 0, pageIndex < pdfDoc.pageCount,
      let pdfPage = pdfDoc.page(at: pageIndex) else {
    fputs("ERROR: page \(pageNum) not found (total=\(pdfDoc.pageCount))\n", stderr)
    exit(3)
}

let mediaBox   = pdfPage.bounds(for: .mediaBox)
let widthPt    = Double(mediaBox.width)
let heightPt   = Double(mediaBox.height)

guard let cgImage = renderPage(pdfPage, dpi: dpi) else {
    fputs("ERROR: failed to render page\n", stderr)
    exit(4)
}

// Save temporary PNG for hashing and for the review HTML
let tmpDir  = URL(fileURLWithPath: NSTemporaryDirectory())
let pngName = "maqaees_\(URL(fileURLWithPath: pdfPath).lastPathComponent)_p\(pageNum).png"
let pngURL  = tmpDir.appendingPathComponent(pngName)
savePNG(cgImage, to: pngURL)
let imgHash = sha256(of: pngURL)

fputs("OCR pass 1 (raw) …\n", stderr)
let rawObs  = runVisionPass(image: cgImage, corrected: false)

fputs("OCR pass 2 (corrected) …\n", stderr)
let corrObs = runVisionPass(image: cgImage, corrected: true)
let corrMap = matchCorrected(rawObs, corrObs)

fputs("Building output JSON …\n", stderr)

// Build observation records
var observations: [[String: Any]] = []
for raw in rawObs.sorted(by: {
    // Sort top → bottom (highest y first; Vision origin = bottom-left)
    bboxCentreY($0.bbox) > bboxCentreY($1.bbox)
}) {
    let corrCandidates: [[String: Any]] = corrMap[raw.index]?.first?.candidates ?? []
    let corrTop = (corrCandidates.first?["text"] as? String) ?? ""

    let obs: [String: Any] = [
        "observation_index":     raw.index,
        "bounding_box":          raw.bbox,
        "raw_candidates":        raw.candidates,
        "corrected_candidates":  corrCandidates,
        "raw_ocr":               raw.topText,
        "corrected_ocr":         corrTop
    ]
    observations.append(obs)
}

let pdfBasename = URL(fileURLWithPath: pdfPath).lastPathComponent

let now = ISO8601DateFormatter().string(from: Date())

let output: [String: Any] = [
    "source_pdf":    pdfBasename,
    "pdf_page":      pageNum,
    "dpi":           dpi,
    "width_pt":      widthPt,
    "height_pt":     heightPt,
    "image_hash":    imgHash,
    "png_tmp_path":  pngURL.path,
    "ocr_timestamp": now,
    "swift_version": "vision_ocr_v2",
    "observations":  observations,
    "raw_count":     rawObs.count,
    "corr_count":    corrObs.count
]

let jsonData = try! JSONSerialization.data(withJSONObject: output,
                                            options: [.prettyPrinted, .sortedKeys])
print(String(data: jsonData, encoding: .utf8)!)
