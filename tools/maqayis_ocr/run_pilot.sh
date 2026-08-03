#!/usr/bin/env bash
# run_pilot.sh — Maqayis OCR v2 pilot runner
#
# Processes 30 pages defined in pilot_manifest.json.
# For each page:
#   1. Renders PDF page at 400 DPI and runs dual-pass Apple Vision OCR
#   2. Merges observations into visual lines
#   3. Classifies line regions
#   4. Detects root entries and semantic-origin phrases
#   5. Generates an HTML review page
#   6. Writes JSONL output to data/maqaees/pilot/
#
# Usage:
#   cd /path/to/hokom
#   bash tools/maqayis_ocr/run_pilot.sh [--dry-run] [--pdf 02.pdf] [--page 3]
#
# Prerequisites:
#   macOS 13+, swift in PATH, python3 in PATH
#   PDF files at: data/maqaees/*.pdf
#
set -euo pipefail

# ── paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOKOM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

OCR_DIR="$HOKOM_ROOT/tools/maqayis_ocr"
PDF_DIR="$HOKOM_ROOT/data/maqaees"
PILOT_DIR="$HOKOM_ROOT/data/maqaees/pilot"
REVIEW_DIR="$PILOT_DIR/review"

MANIFEST="$OCR_DIR/pilot_manifest.json"
SWIFT_OCR="$OCR_DIR/vision_ocr.swift"
PY_PIPELINE="$OCR_DIR/pipeline.py"

DPI=400

# ── CLI flags ──────────────────────────────────────────────────────────────────
DRY_RUN=0
FILTER_PDF=""
FILTER_PAGE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=1; shift ;;
    --pdf)     FILTER_PDF="$2"; shift 2 ;;
    --page)    FILTER_PAGE="$2"; shift 2 ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

# ── sanity checks ─────────────────────────────────────────────────────────────
echo "=== Maqayis OCR v2 Pilot Runner ==="
echo "HOKOM_ROOT : $HOKOM_ROOT"
echo "PDF_DIR    : $PDF_DIR"
echo "PILOT_DIR  : $PILOT_DIR"
echo ""

if [[ ! -f "$SWIFT_OCR" ]]; then
  echo "ERROR: vision_ocr.swift not found at $SWIFT_OCR" >&2; exit 1
fi

if ! command -v swift &>/dev/null; then
  echo "ERROR: swift not found in PATH — run on macOS" >&2; exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found in PATH" >&2; exit 1
fi

mkdir -p "$PILOT_DIR" "$REVIEW_DIR"

# ── compile Swift OCR once ────────────────────────────────────────────────────
SWIFT_BIN="$PILOT_DIR/vision_ocr_bin"
if [[ ! -f "$SWIFT_BIN" ]] || [[ "$SWIFT_OCR" -nt "$SWIFT_BIN" ]]; then
  echo "Compiling vision_ocr.swift …"
  if [[ $DRY_RUN -eq 0 ]]; then
    swiftc "$SWIFT_OCR" \
      -framework Foundation \
      -framework Vision \
      -framework PDFKit \
      -framework CoreGraphics \
      -framework AppKit \
      -framework CryptoKit \
      -O \
      -o "$SWIFT_BIN"
    echo "Compiled → $SWIFT_BIN"
  else
    echo "[DRY-RUN] Would compile vision_ocr.swift"
  fi
fi

# ── build page list from manifest ─────────────────────────────────────────────
# Extract (pdf, page, category, note) tuples using python3
PAGE_LIST=$(python3 - "$MANIFEST" <<'PYEOF'
import json, sys

with open(sys.argv[1]) as f:
    manifest = json.load(f)

pages = []
for category, cat_data in manifest["categories"].items():
    for p in cat_data["pages"]:
        pages.append({
            "pdf":      p["pdf"],
            "page":     p["page"],
            "category": category,
            "note":     p.get("note", "")
        })

# Print as TSV: pdf TAB page TAB category TAB note
for p in pages:
    print(f"{p['pdf']}\t{p['page']}\t{p['category']}\t{p['note']}")
PYEOF
)

TOTAL=$(echo "$PAGE_LIST" | wc -l | tr -d ' ')
echo "Pilot pages: $TOTAL"
[[ $DRY_RUN -eq 1 ]] && echo "[DRY-RUN mode — no actual processing]"
echo ""

# ── output JSONL files ────────────────────────────────────────────────────────
PAGES_JSONL="$PILOT_DIR/pages.jsonl"
LINES_JSONL="$PILOT_DIR/lines.jsonl"
ROOTS_JSONL="$PILOT_DIR/root_entries.jsonl"

# Truncate on fresh run (keep on resume if desired)
: > "$PAGES_JSONL"
: > "$LINES_JSONL"
: > "$ROOTS_JSONL"

# ── counters ──────────────────────────────────────────────────────────────────
PAGES_PROCESSED=0
LINES_EXTRACTED=0
ROOTS_DETECTED=0
ORIGINS_DETECTED=0
REVIEW_REQUIRED=0
ERRORS=0

# ── main loop ─────────────────────────────────────────────────────────────────
while IFS=$'\t' read -r PDF_NAME PAGE_NUM CATEGORY NOTE; do

  # Apply filters
  if [[ -n "$FILTER_PDF"  && "$PDF_NAME"  != "$FILTER_PDF"  ]]; then continue; fi
  if [[ -n "$FILTER_PAGE" && "$PAGE_NUM"  != "$FILTER_PAGE" ]]; then continue; fi

  PDF_PATH="$PDF_DIR/$PDF_NAME"
  if [[ ! -f "$PDF_PATH" ]]; then
    echo "  ⚠ SKIP (not found): $PDF_PATH"
    ((ERRORS++)) || true
    continue
  fi

  SLUG="${PDF_NAME%.pdf}_p${PAGE_NUM}"
  RAW_JSON="$PILOT_DIR/${SLUG}_vision.json"
  PAGE_JSON="$PILOT_DIR/${SLUG}_page.json"
  REVIEW_HTML="$REVIEW_DIR/${SLUG}_review.html"

  echo "▶ $PDF_NAME page $PAGE_NUM [$CATEGORY]"
  echo "  $NOTE"

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "  [DRY-RUN] Would process → $REVIEW_HTML"
    continue
  fi

  # Step 1: Apple Vision OCR
  echo -n "  OCR … "
  if "$SWIFT_BIN" "$PDF_PATH" "$PAGE_NUM" "$DPI" > "$RAW_JSON" 2>/tmp/swift_stderr.txt; then
    OBS_COUNT=$(python3 -c "import json; d=json.load(open('$RAW_JSON')); print(d.get('raw_count',0))")
    echo "✓ ($OBS_COUNT observations)"
  else
    echo "✗ FAILED"
    cat /tmp/swift_stderr.txt >&2
    ((ERRORS++)) || true
    continue
  fi

  # Step 2–4: Python pipeline (merge → classify → parse)
  echo -n "  Pipeline … "
  if python3 "$PY_PIPELINE" "$RAW_JSON" "$PAGE_JSON" 2>/tmp/py_stderr.txt; then
    NLINES=$(python3 -c "import json; d=json.load(open('$PAGE_JSON')); print(len(d.get('lines',[])))")
    NROOTS=$(python3 -c "import json; d=json.load(open('$PAGE_JSON')); print(len(d.get('root_entries',[])))")
    NREV=$(python3 -c "
import json
d=json.load(open('$PAGE_JSON'))
n=sum(1 for l in d.get('lines',[]) if l.get('review_status')=='REVIEW_REQUIRED')
print(n)")
    echo "✓ ($NLINES lines, $NROOTS roots, $NREV review-required)"
  else
    echo "✗ FAILED"
    cat /tmp/py_stderr.txt >&2
    ((ERRORS++)) || true
    continue
  fi

  # Step 5: Append to JSONL
  python3 - <<PYEOF
import json

with open("$PAGE_JSON") as f:
    page_doc = json.load(f)

page_meta = {k: page_doc[k] for k in page_doc if k != "lines" and k != "root_entries"}
page_meta["category"] = "$CATEGORY"

with open("$PAGES_JSONL", "a", encoding="utf-8") as f:
    f.write(json.dumps(page_meta, ensure_ascii=False) + "\n")

with open("$LINES_JSONL", "a", encoding="utf-8") as f:
    for line in page_doc.get("lines", []):
        f.write(json.dumps(line, ensure_ascii=False) + "\n")

with open("$ROOTS_JSONL", "a", encoding="utf-8") as f:
    for entry in page_doc.get("root_entries", []):
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
PYEOF

  # Step 6: HTML review
  echo -n "  Review HTML … "
  python3 - <<PYEOF
import json, sys
sys.path.insert(0, "$OCR_DIR")
from review_report import write_review_html

with open("$PAGE_JSON") as f:
    doc = json.load(f)

write_review_html(
    "$REVIEW_HTML",
    page_data={k: doc[k] for k in doc if k not in ("lines","root_entries")},
    lines=doc.get("lines", []),
    root_entries=doc.get("root_entries", []),
)
print("OK")
PYEOF

  ((PAGES_PROCESSED++)) || true
  ((LINES_EXTRACTED += NLINES)) || true
  ((ROOTS_DETECTED  += NROOTS)) || true
  ((REVIEW_REQUIRED += NREV))   || true

  echo ""

done <<< "$PAGE_LIST"

# ── count semantic origins from JSONL ─────────────────────────────────────────
ORIGINS_DETECTED=$(python3 - <<PYEOF
import json
count = 0
try:
    with open("$ROOTS_JSONL") as f:
        for line in f:
            e = json.loads(line)
            if e.get("semantic_origin_type") not in ("NONE","UNKNOWN",""):
                count += 1
except FileNotFoundError:
    pass
print(count)
PYEOF
)

# ── write review manifest ──────────────────────────────────────────────────────
python3 - <<PYEOF
import json, datetime

manifest = {
    "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "version": "v2",
    "dpi": $DPI,
    "pages_processed": $PAGES_PROCESSED,
    "lines_extracted": $LINES_EXTRACTED,
    "roots_detected":  $ROOTS_DETECTED,
    "semantic_origins_detected": $ORIGINS_DETECTED,
    "review_required_lines": $REVIEW_REQUIRED,
    "errors": $ERRORS,
    "pages_jsonl":    "pages.jsonl",
    "lines_jsonl":    "lines.jsonl",
    "roots_jsonl":    "root_entries.jsonl",
    "review_dir":     "review/",
}
with open("$PILOT_DIR/review_manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("[manifest] Written")
PYEOF

# ── final report ──────────────────────────────────────────────────────────────
echo "════════════════════════════════════"
echo "FILES_CREATED         : see $PILOT_DIR/"
echo "PAGES_PROCESSED       : $PAGES_PROCESSED"
echo "LINES_EXTRACTED       : $LINES_EXTRACTED"
echo "ROOT_HEADINGS_DETECTED: $ROOTS_DETECTED"
echo "SEMANTIC_ORIGINS_DETECTED: $ORIGINS_DETECTED"
echo "REVIEW_REQUIRED_LINES : $REVIEW_REQUIRED"
echo "ERRORS                : $ERRORS"
echo "OUTPUT_DIRECTORY      : $PILOT_DIR"
echo "REVIEW_HTMLS          : $REVIEW_DIR"
echo "════════════════════════════════════"

if [[ $ERRORS -gt 0 ]]; then
  echo "⚠ $ERRORS page(s) failed — see stderr above"
  exit 1
fi
echo "✓ Pilot complete"
