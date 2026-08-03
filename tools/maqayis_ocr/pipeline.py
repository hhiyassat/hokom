"""
pipeline.py — Maqayis OCR v2

Orchestrates the Python processing stages for one page:
  1. Load vision_ocr.swift raw JSON
  2. Merge observations into visual lines  (line_merger)
  3. Classify line regions                 (page_regions)
  4. Detect root entries and origins       (entry_parser)
  5. Write combined page JSON

Usage:
  python pipeline.py <vision_raw.json> <output_page.json>
"""

from __future__ import annotations
import json
import sys
import os

# Allow importing sibling modules regardless of cwd
sys.path.insert(0, os.path.dirname(__file__))

from line_merger  import merge_observations
from page_regions import classify_lines
from entry_parser import parse_entries


def process_page(vision_json_path: str, output_path: str) -> dict:
    with open(vision_json_path, encoding="utf-8") as f:
        page_data: dict = json.load(f)

    source_pdf = page_data["source_pdf"]
    pdf_page   = page_data["pdf_page"]
    observations = page_data.get("observations", [])

    # Stage 1: merge
    lines = merge_observations(observations, source_pdf, pdf_page)
    print(f"[pipeline] merge: {len(observations)} obs → {len(lines)} lines",
          file=sys.stderr)

    # Stage 2: classify
    classify_lines(lines)
    counts: dict[str, int] = {}
    for ln in lines:
        rt = ln["region_type"]
        counts[rt] = counts.get(rt, 0) + 1
    print(f"[pipeline] classify: {counts}", file=sys.stderr)

    # Stage 3: parse entries
    lines, root_entries = parse_entries(lines, source_pdf, pdf_page)
    print(f"[pipeline] entries: {len(root_entries)} roots", file=sys.stderr)

    # Assemble page document
    page_doc: dict = {
        "source_pdf":    source_pdf,
        "pdf_page":      pdf_page,
        "dpi":           page_data.get("dpi", 400),
        "width_pt":      page_data.get("width_pt", 0),
        "height_pt":     page_data.get("height_pt", 0),
        "image_hash":    page_data.get("image_hash", ""),
        "png_tmp_path":  page_data.get("png_tmp_path", ""),
        "ocr_timestamp": page_data.get("ocr_timestamp", ""),
        "swift_version": page_data.get("swift_version", ""),
        "raw_count":     page_data.get("raw_count", 0),
        "corr_count":    page_data.get("corr_count", 0),
        "lines":         lines,
        "root_entries":  root_entries,
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(page_doc, f, ensure_ascii=False, indent=2)

    return page_doc


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pipeline.py <vision_raw.json> <output_page.json>")
        sys.exit(1)

    result = process_page(sys.argv[1], sys.argv[2])
    n_lines  = len(result["lines"])
    n_roots  = len(result["root_entries"])
    n_review = sum(1 for l in result["lines"] if l.get("review_status") == "REVIEW_REQUIRED")
    print(f"[pipeline] OK — {n_lines} lines, {n_roots} roots, {n_review} review-required")
