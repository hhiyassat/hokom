"""
tools/maqayis_ocr — Maqayis OCR v2
====================================

Apple Vision dual-pass Arabic OCR pipeline for Maqayis al-Lugha (ابن فارس).

Modules
-------
vision_ocr.swift   Swift CLI: renders PDF pages at 400 DPI, runs two Vision passes
pipeline.py        Python orchestrator: merge → classify → parse
line_merger.py     Groups Vision observations into visual lines
page_regions.py    Classifies lines (BOOK_HEADING, ROOT_ENTRY_START, POETRY …)
entry_parser.py    Detects root headings, extracts semantic-origin phrases
review_report.py   Generates HTML review page per processed page

Entry points
------------
  bash tools/maqayis_ocr/run_pilot.sh            # process 30-page pilot
  bash tools/maqayis_ocr/run_pilot.sh --dry-run  # preview only
  bash tools/maqayis_ocr/run_pilot.sh --pdf 02.pdf --page 3  # single page

Output
------
  data/maqaees/pilot/
    pages.jsonl
    lines.jsonl
    root_entries.jsonl
    review_manifest.json
    review/
      <pdf>_p<N>_review.html   (one per page)
"""

__version__ = "2.0.0"
