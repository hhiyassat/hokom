#!/usr/bin/env bash
# run_full.sh — Maqayis OCR v2 full-corpus runner
#
# Processes ALL pages of 01.pdf–06.pdf (or a selected subset).
# Output goes to  data/maqaees/full/
#   full/01/  full/02/ … full/06/   ← per-PDF page JSONs + vision JSONs
#   full/pages.jsonl
#   full/lines.jsonl
#   full/root_entries.jsonl
#   full/run_manifest.json
#
# Usage:
#   cd /path/to/hokom
#   bash tools/maqayis_ocr/run_full.sh [options]
#
# Options:
#   --resume          Skip pages where *_page.json already exists
#   --pdf 02.pdf      Process only this PDF (may be repeated; default: all)
#   --page N          Process only page N (use with --pdf for a single page)
#   --html            Generate HTML review files (default: OFF at full scale)
#   --dry-run         Show what would be processed without doing it
#   --dpi N           Render DPI (default: 400)
#   --help            Show this message
#
# Prerequisites:
#   macOS 13+, swift in PATH, python3 in PATH
#   PDF files at: data/maqaees/*.pdf
#   python3 -m pip install pypdf  (for page-count discovery)
#
set -euo pipefail

# ── paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOKOM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

OCR_DIR="$HOKOM_ROOT/tools/maqayis_ocr"
PDF_DIR="$HOKOM_ROOT/data/maqaees"
FULL_DIR="$HOKOM_ROOT/data/maqaees/full"

SWIFT_OCR="$OCR_DIR/vision_ocr.swift"
PY_PIPELINE="$OCR_DIR/pipeline.py"

DPI=400

# ── CLI flags ──────────────────────────────────────────────────────────────────
DRY_RUN=0
RESUME=0
GENERATE_HTML=0
FILTER_PAGE=""
PDF_FILTER_LIST=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --resume)   RESUME=1; shift ;;
    --html)     GENERATE_HTML=1; shift ;;
    --dry-run)  DRY_RUN=1; shift ;;
    --pdf)      PDF_FILTER_LIST+=("$2"); shift 2 ;;
    --page)     FILTER_PAGE="$2"; shift 2 ;;
    --dpi)      DPI="$2"; shift 2 ;;
    --help)
      grep '^#' "$0" | head -30 | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

# Default: all 6 PDFs if no --pdf given
if [[ ${#PDF_FILTER_LIST[@]} -eq 0 ]]; then
  PDF_FILTER_LIST=("01.pdf" "02.pdf" "03.pdf" "04.pdf" "05.pdf" "06.pdf")
fi

# ── sanity checks ─────────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════╗"
echo "║   Maqayis OCR v2 — Full Corpus Runner   ║"
echo "╚══════════════════════════════════════════╝"
echo "HOKOM_ROOT : $HOKOM_ROOT"
echo "PDF_DIR    : $PDF_DIR"
echo "FULL_DIR   : $FULL_DIR"
echo "DPI        : $DPI"
[[ $RESUME -eq 1 ]]        && echo "MODE       : RESUME (skipping existing pages)"
[[ $GENERATE_HTML -eq 1 ]] && echo "HTML       : ON"
[[ $DRY_RUN -eq 1 ]]       && echo "DRY-RUN    : ON"
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

mkdir -p "$FULL_DIR"

# ── compile Swift OCR (reuse pilot binary if fresh; else compile to full/) ────
PILOT_BIN="$HOKOM_ROOT/data/maqaees/pilot/vision_ocr_bin"
FULL_BIN="$FULL_DIR/vision_ocr_bin"

# Use pilot binary if it's newer than the swift source; otherwise recompile
if [[ -f "$PILOT_BIN" ]] && [[ "$PILOT_BIN" -nt "$SWIFT_OCR" ]]; then
  SWIFT_BIN="$PILOT_BIN"
  echo "Reusing pilot binary: $PILOT_BIN"
elif [[ -f "$FULL_BIN" ]] && [[ "$FULL_BIN" -nt "$SWIFT_OCR" ]]; then
  SWIFT_BIN="$FULL_BIN"
  echo "Reusing full binary: $FULL_BIN"
else
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
      -o "$FULL_BIN"
    echo "Compiled → $FULL_BIN"
    SWIFT_BIN="$FULL_BIN"
  else
    echo "[DRY-RUN] Would compile vision_ocr.swift"
    SWIFT_BIN="${FULL_BIN}"
  fi
fi
echo ""

# ── helper: get page count ────────────────────────────────────────────────────
# Tries pypdf first (fast); falls back to probing the Swift binary.
get_page_count() {
  local pdf_path="$1"
  local count

  # Method 1: pypdf (if installed)
  count=$(python3 -c "
import sys
try:
    from pypdf import PdfReader
    r = PdfReader('$pdf_path')
    print(len(r.pages))
except Exception:
    print(0)
" 2>/dev/null)

  if [[ "$count" -gt 0 ]] 2>/dev/null; then
    echo "$count"
    return
  fi

  # Method 2: probe Swift binary with out-of-range page; binary prints
  #   "ERROR: page N not found (total=M)" to stderr
  local _tmp_err
  _tmp_err=$(mktemp)
  "$SWIFT_BIN" "$pdf_path" 9999 "$DPI" >/dev/null 2>"$_tmp_err" || true
  count=$(grep -oE 'total=[0-9]+' "$_tmp_err" 2>/dev/null | head -1 | cut -d= -f2 || true)
  rm -f "$_tmp_err"

  if [[ "$count" -gt 0 ]] 2>/dev/null; then
    echo "$count"
    return
  fi

  echo "0"
}

# ── helper: optional HTML review ─────────────────────────────────────────────
generate_review_html() {
  local page_json="$1"
  local review_html="$2"
  python3 - <<PYEOF 2>/dev/null || true
import json, sys
sys.path.insert(0, "$OCR_DIR")
from review_report import write_review_html
with open("$page_json") as f:
    doc = json.load(f)
write_review_html(
    "$review_html",
    page_data={k: doc[k] for k in doc if k not in ("lines","root_entries")},
    lines=doc.get("lines", []),
    root_entries=doc.get("root_entries", []),
)
PYEOF
}

# ── counters ──────────────────────────────────────────────────────────────────
TOTAL_PAGES_PROCESSED=0
TOTAL_PAGES_SKIPPED=0
TOTAL_LINES=0
TOTAL_ROOTS=0
TOTAL_REVIEW_REQUIRED=0
ERRORS=0

START_TIME=$SECONDS
GLOBAL_PAGE_IDX=0   # for ETA

# ── pre-flight: get page counts for all requested PDFs ────────────────────────
# Store as parallel arrays (bash 3 compatible — no declare -A)
PDF_NAMES_ARR=()
PDF_COUNTS_ARR=()
GRAND_TOTAL=0

echo "Scanning PDF page counts …"
for PDF_NAME in "${PDF_FILTER_LIST[@]}"; do
  PDF_PATH="$PDF_DIR/$PDF_NAME"
  if [[ ! -f "$PDF_PATH" ]]; then
    echo "  ⚠  NOT FOUND: $PDF_PATH"
    PDF_NAMES_ARR+=("$PDF_NAME")
    PDF_COUNTS_ARR+=(0)
    continue
  fi
  if [[ $DRY_RUN -eq 0 ]]; then
    COUNT=$(get_page_count "$PDF_PATH") || COUNT=0
    PDF_NAMES_ARR+=("$PDF_NAME")
    PDF_COUNTS_ARR+=("$COUNT")
    echo "  $PDF_NAME : $COUNT pages"
    (( GRAND_TOTAL += COUNT )) || true
  else
    PDF_NAMES_ARR+=("$PDF_NAME")
    PDF_COUNTS_ARR+=("??")
    echo "  $PDF_NAME : ?? pages [dry-run]"
  fi
done
echo ""
[[ $DRY_RUN -eq 0 ]] && echo "Grand total pages to process: $GRAND_TOTAL"
echo ""

# Helper: look up page count by PDF name from parallel arrays
lookup_page_count() {
  local name="$1"
  local i
  for (( i=0; i<${#PDF_NAMES_ARR[@]}; i++ )); do
    if [[ "${PDF_NAMES_ARR[$i]}" == "$name" ]]; then
      echo "${PDF_COUNTS_ARR[$i]}"
      return
    fi
  done
  echo "0"
}

# ══════════════════════════════════════════════════════════════════════════════
# Main loop — iterate PDFs then pages
# ══════════════════════════════════════════════════════════════════════════════
for PDF_NAME in "${PDF_FILTER_LIST[@]}"; do

  PDF_PATH="$PDF_DIR/$PDF_NAME"
  if [[ ! -f "$PDF_PATH" ]]; then
    echo "⚠  SKIP (not found): $PDF_PATH"
    ((ERRORS++)) || true
    continue
  fi

  PAGE_COUNT=$(lookup_page_count "$PDF_NAME")
  if [[ $DRY_RUN -eq 0 ]] && [[ "$PAGE_COUNT" -eq 0 ]]; then
    echo "⚠  SKIP (could not determine page count): $PDF_NAME"
    ((ERRORS++)) || true
    continue
  fi

  # Per-PDF output subdirectory:  full/01/  full/02/ …
  PDF_NUM="${PDF_NAME%.pdf}"          # "01", "02", …
  PDF_OUTDIR="$FULL_DIR/$PDF_NUM"
  mkdir -p "$PDF_OUTDIR"
  [[ $GENERATE_HTML -eq 1 ]] && mkdir -p "$PDF_OUTDIR/review"

  # Page range to process
  if [[ -n "$FILTER_PAGE" ]]; then
    PAGE_START="$FILTER_PAGE"
    PAGE_END="$FILTER_PAGE"
  else
    PAGE_START=1
    PAGE_END="${PAGE_COUNT:-1}"
  fi

  echo "━━━━  $PDF_NAME  ($PAGE_COUNT pages)  ━━━━"

  PDF_PAGES_DONE=0
  PDF_PAGES_SKIP=0
  PDF_ERRORS=0

  for (( PAGE_NUM=PAGE_START; PAGE_NUM<=PAGE_END; PAGE_NUM++ )); do

    SLUG="${PDF_NUM}_p${PAGE_NUM}"
    RAW_JSON="$PDF_OUTDIR/${SLUG}_vision.json"
    PAGE_JSON="$PDF_OUTDIR/${SLUG}_page.json"

    # Resume: skip if page JSON already exists
    if [[ $RESUME -eq 1 ]] && [[ -f "$PAGE_JSON" ]]; then
      ((PDF_PAGES_SKIP++))    || true
      ((TOTAL_PAGES_SKIPPED++)) || true
      ((GLOBAL_PAGE_IDX++))   || true
      continue
    fi

    if [[ $DRY_RUN -eq 1 ]]; then
      echo "  [DRY-RUN] $PDF_NAME page $PAGE_NUM → $PAGE_JSON"
      continue
    fi

    # Progress + ETA
    ((GLOBAL_PAGE_IDX++)) || true
    ELAPSED_NOW=$(( SECONDS - START_TIME ))
    if (( GLOBAL_PAGE_IDX > 1 && ELAPSED_NOW > 0 )); then
      RATE=$(( (GLOBAL_PAGE_IDX - 1) * 60 / ELAPSED_NOW ))   # pages/min
      if (( RATE > 0 )); then
        REMAINING=$(( (GRAND_TOTAL - GLOBAL_PAGE_IDX) * ELAPSED_NOW / (GLOBAL_PAGE_IDX - 1) ))
        ETA_H=$(( REMAINING / 3600 ))
        ETA_M=$(( (REMAINING % 3600) / 60 ))
        printf "\r  %-7s  p%4d/%-4s  ETA %dh%02dm   " \
          "$PDF_NAME" "$PAGE_NUM" "$PAGE_COUNT" "$ETA_H" "$ETA_M"
      else
        printf "\r  %-7s  p%4d/%-4s  …             " "$PDF_NAME" "$PAGE_NUM" "$PAGE_COUNT"
      fi
    else
      printf "\r  %-7s  p%4d/%-4s  …             " "$PDF_NAME" "$PAGE_NUM" "$PAGE_COUNT"
    fi

    # ── Step 1: Apple Vision OCR ─────────────────────────────────────────────
    if ! "$SWIFT_BIN" "$PDF_PATH" "$PAGE_NUM" "$DPI" > "$RAW_JSON" 2>/tmp/full_swift_err.txt; then
      printf "\n  ✗ p%d OCR failed\n" "$PAGE_NUM"
      cat /tmp/full_swift_err.txt >&2
      ((PDF_ERRORS++)) || true
      ((ERRORS++)) || true
      continue
    fi

    # ── Step 2–4: Python pipeline ────────────────────────────────────────────
    if ! python3 "$PY_PIPELINE" "$RAW_JSON" "$PAGE_JSON" 2>/tmp/full_py_err.txt; then
      printf "\n  ✗ p%d pipeline failed\n" "$PAGE_NUM"
      cat /tmp/full_py_err.txt >&2
      ((PDF_ERRORS++)) || true
      ((ERRORS++)) || true
      continue
    fi

    # ── Step 3: (Optional) HTML review ──────────────────────────────────────
    if [[ $GENERATE_HTML -eq 1 ]]; then
      generate_review_html "$PAGE_JSON" "$PDF_OUTDIR/review/${SLUG}_review.html"
    fi

    # ── Tally this page ──────────────────────────────────────────────────────
    read -r _NL _NR _NREV < <(python3 -c "
import json
d = json.load(open('$PAGE_JSON'))
lines = d.get('lines', [])
roots = d.get('root_entries', [])
nrev  = sum(1 for l in lines if l.get('review_status') == 'REVIEW_REQUIRED')
print(len(lines), len(roots), nrev)
")
    ((PDF_PAGES_DONE++))              || true
    ((TOTAL_PAGES_PROCESSED++))       || true
    ((TOTAL_LINES      += _NL))       || true
    ((TOTAL_ROOTS      += _NR))       || true
    ((TOTAL_REVIEW_REQUIRED += _NREV)) || true

  done   # pages

  printf "\r  ✓ %s — %d pages" "$PDF_NAME" "$PDF_PAGES_DONE"
  [[ $PDF_PAGES_SKIP -gt 0 ]] && printf "  (%d skipped)" "$PDF_PAGES_SKIP"
  [[ $PDF_ERRORS -gt 0 ]]     && printf "  ⚠ %d errors" "$PDF_ERRORS"
  printf "\n\n"

done   # PDFs

# ══════════════════════════════════════════════════════════════════════════════
# Rebuild JSONL from all *_page.json (atomic, safe for --resume)
# ══════════════════════════════════════════════════════════════════════════════
if [[ $DRY_RUN -eq 0 ]]; then
  echo "Rebuilding JSONL files from all page JSONs …"
  python3 - <<PYEOF
import json, os, glob, sys

full_dir  = "$FULL_DIR"
pages_out  = os.path.join(full_dir, "pages.jsonl")
lines_out  = os.path.join(full_dir, "lines.jsonl")
roots_out  = os.path.join(full_dir, "root_entries.jsonl")

page_files = sorted(glob.glob(os.path.join(full_dir, "**", "*_page.json"), recursive=True))
print(f"  Found {len(page_files)} page JSON files")

total_pages = total_lines = total_roots = 0
with open(pages_out, "w", encoding="utf-8") as fp, \
     open(lines_out, "w", encoding="utf-8") as fl, \
     open(roots_out, "w", encoding="utf-8") as fr:
  for path in page_files:
    try:
      with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    except Exception as e:
      print(f"  WARN: could not read {path}: {e}", file=sys.stderr)
      continue
    page_meta = {k: v for k, v in doc.items() if k not in ("lines","root_entries")}
    fp.write(json.dumps(page_meta, ensure_ascii=False) + "\n")
    total_pages += 1
    for line in doc.get("lines", []):
      fl.write(json.dumps(line, ensure_ascii=False) + "\n")
      total_lines += 1
    for entry in doc.get("root_entries", []):
      fr.write(json.dumps(entry, ensure_ascii=False) + "\n")
      total_roots += 1

print(f"  JSONL: {total_pages} pages, {total_lines} lines, {total_roots} root entries")
print(f"  → {pages_out}")
print(f"  → {lines_out}")
print(f"  → {roots_out}")
PYEOF
fi

# ── write run manifest ─────────────────────────────────────────────────────────
if [[ $DRY_RUN -eq 0 ]]; then
  ELAPSED=$(( SECONDS - START_TIME ))

  ORIGINS_DETECTED=$(python3 - <<PYEOF
import json
count = 0
try:
    with open("$FULL_DIR/root_entries.jsonl") as f:
        for line in f:
            e = json.loads(line)
            if e.get("semantic_origin_type") not in ("NONE","UNKNOWN","",None):
                count += 1
except FileNotFoundError:
    pass
print(count)
PYEOF
)

  PDF_LIST_JSON=$(python3 -c "
import json, sys
pdfs = sys.argv[1:]
print(json.dumps(pdfs))
" "${PDF_FILTER_LIST[@]}")

  python3 - <<PYEOF
import json, datetime

manifest = {
    "created":                   datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "version":                   "v2",
    "mode":                      "full",
    "dpi":                       $DPI,
    "resume":                    bool($RESUME),
    "html":                      bool($GENERATE_HTML),
    "pdfs":                      $PDF_LIST_JSON,
    "pages_processed":           $TOTAL_PAGES_PROCESSED,
    "pages_skipped_resumed":     $TOTAL_PAGES_SKIPPED,
    "lines_extracted":           $TOTAL_LINES,
    "roots_detected":            $TOTAL_ROOTS,
    "semantic_origins_detected": $ORIGINS_DETECTED,
    "review_required_lines":     $TOTAL_REVIEW_REQUIRED,
    "elapsed_seconds":           $ELAPSED,
    "errors":                    $ERRORS,
    "pages_jsonl":               "pages.jsonl",
    "lines_jsonl":               "lines.jsonl",
    "roots_jsonl":               "root_entries.jsonl",
}
with open("$FULL_DIR/run_manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("[manifest] Written → $FULL_DIR/run_manifest.json")
PYEOF
fi

# ── final report ───────────────────────────────────────────────────────────────
ELAPSED=$(( SECONDS - START_TIME ))
echo "╔══════════════════════════════════════════╗"
echo "║           Full Corpus — Summary          ║"
echo "╚══════════════════════════════════════════╝"
printf "PAGES PROCESSED       : %d\n"    "$TOTAL_PAGES_PROCESSED"
printf "PAGES SKIPPED/RESUMED : %d\n"    "$TOTAL_PAGES_SKIPPED"
printf "LINES EXTRACTED       : %d\n"    "$TOTAL_LINES"
printf "ROOT HEADINGS         : %d\n"    "$TOTAL_ROOTS"
printf "ERRORS                : %d\n"    "$ERRORS"
printf "ELAPSED               : %dh %dm %ds\n" \
  "$(( ELAPSED/3600 ))" "$(( (ELAPSED%3600)/60 ))" "$(( ELAPSED%60 ))"
echo "OUTPUT                : $FULL_DIR"

if [[ $ERRORS -gt 0 ]]; then
  echo "⚠  $ERRORS page(s) failed — see stderr above"
  exit 1
fi
echo "✓  Full corpus run complete"
