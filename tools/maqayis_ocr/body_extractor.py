#!/usr/bin/env python3
"""
body_extractor.py — Maqayis OCR v2
Extracts the full body text of every Ibn Faris root entry from the per-page
JSON files produced by run_full.sh, and writes root_entries_full.jsonl.

Input  : data/maqaees/full/{01..06}/*_page.json   (existing OCR output)
         data/maqaees/full/root_entries.jsonl       (existing summary)
Output : data/maqaees/full/root_entries_full.jsonl  (enriched, one root per line)

Algorithm
─────────
1. Stream all page JSON files in PDF/page order.
2. Sort lines within each page by y-coordinate descending (top → bottom).
3. Maintain a "current entry" accumulator:
     • ROOT_ENTRY_START  → flush current, open new entry
     • MAIN_TEXT/POETRY  → append to body
     • FOOTNOTE          → append to footnotes
     • everything else   → skip
4. After all pages, flush the last entry.
5. Enrich with semantic fields from the existing root_entries.jsonl index
   (keyed by source_pdf + pdf_page of the heading).
6. Write root_entries_full.jsonl.

Output schema per line
──────────────────────
{
  "root_letters":          str,
  "bab_letter":            str,
  "semantic_origin_type":  str,   # SINGULAR|DUAL|TRIPLE|MULTIPLE|SOUND_ROOTS|NONE
  "origin_count":          int|null,
  "review_status":         str,
  "root_heading_text":     str,
  "body_text":             str,   # MAIN_TEXT + POETRY joined with space
  "footnotes":             str,   # FOOTNOTE lines joined with space
  "source_pdf":            str,
  "page_start":            int,
  "page_end":              int,
  "entry_id":              str,   # from root_entries.jsonl where available
  "body_word_count":       int
}
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# ── Repo layout ───────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[2]
_DATA_DIR    = _REPO_ROOT / "data" / "maqaees" / "full"
_SUMMARY_IN  = _DATA_DIR / "root_entries.jsonl"
_FULL_OUT    = _DATA_DIR / "root_entries_full.jsonl"

# region_types whose text goes into the main body
_BODY_TYPES = {"MAIN_TEXT", "POETRY"}
# region_types to capture as footnotes
_FOOT_TYPES = {"FOOTNOTE"}
# region_types that mark a new root entry
_HEAD_TYPE  = "ROOT_ENTRY_START"

PDF_ORDER = ["01", "02", "03", "04", "05", "06"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _page_number(path: Path) -> int:
    """Extract numeric page index from filename like 02_p137_page.json."""
    m = re.search(r"_p(\d+)_", path.name)
    return int(m.group(1)) if m else 0


def _load_summary_index(jsonl_path: Path) -> dict[tuple[str, int], dict]:
    """
    Build lookup: (source_pdf, pdf_page) → root_entries row.
    When multiple entries share the same (pdf, page) — shouldn't happen for
    ROOT_ENTRY_START — we keep the first.
    """
    index: dict[tuple[str, int], dict] = {}
    if not jsonl_path.exists():
        return index
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (row.get("source_pdf", ""), row.get("pdf_page", -1))
            if key not in index:
                index[key] = row
    return index


def _page_files(data_dir: Path) -> list[Path]:
    """Return all *_page.json paths in PDF/page order."""
    files: list[Path] = []
    for pdf_num in PDF_ORDER:
        pdf_dir = data_dir / pdf_num
        if not pdf_dir.exists():
            continue
        pages = sorted(pdf_dir.glob("*_page.json"), key=_page_number)
        files.extend(pages)
    return files


def _sorted_lines(page_data: dict) -> list[dict]:
    """Return lines sorted top→bottom (y descending in PDF coord space)."""
    return sorted(
        page_data.get("lines", []),
        key=lambda l: -l.get("bounding_box", {}).get("y", 0),
    )


def _flush(entry: Optional[dict]) -> Optional[dict]:
    """Finalise a pending entry dict and return it (or None)."""
    if entry is None:
        return None
    body = " ".join(entry["body_lines"]).strip()
    foot = " ".join(entry["footnote_lines"]).strip()
    entry["body_text"]       = body
    entry["footnotes"]       = foot
    entry["body_word_count"] = len(body.split()) if body else 0
    del entry["body_lines"]
    del entry["footnote_lines"]
    return entry


# ── Main extraction ───────────────────────────────────────────────────────────

def extract(data_dir: Path, verbose: bool = False) -> list[dict]:
    """Stream all pages and extract full entries. Returns list of entry dicts."""
    summary_index = _load_summary_index(data_dir / "root_entries.jsonl")

    entries: list[dict] = []
    current: Optional[dict] = None

    page_files = _page_files(data_dir)
    if not page_files:
        print("ERROR: no *_page.json files found under", data_dir, file=sys.stderr)
        return []

    for page_path in page_files:
        try:
            page_data = json.loads(page_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"WARN: could not read {page_path.name}: {exc}", file=sys.stderr)
            continue

        source_pdf = page_data.get("source_pdf", "")
        pdf_page   = page_data.get("pdf_page", 0)

        for line in _sorted_lines(page_data):
            region_type = line.get("region_type", "UNKNOWN")
            text        = (line.get("corrected_ocr") or "").strip()
            if not text:
                continue

            if region_type == _HEAD_TYPE:
                # Flush previous entry
                done = _flush(current)
                if done is not None:
                    entries.append(done)

                # Look up semantic metadata from summary
                meta = summary_index.get((source_pdf, pdf_page), {})

                current = {
                    # provenance
                    "source_pdf":  source_pdf,
                    "page_start":  pdf_page,
                    "page_end":    pdf_page,
                    # heading
                    "root_heading_text": text,
                    # from summary index
                    "root_letters":         meta.get("root_letters", ""),
                    "bab_letter":           meta.get("bab_letter", ""),
                    "semantic_origin_type": meta.get("semantic_origin_type", "NONE"),
                    "origin_count":         meta.get("origin_count"),
                    "review_status":        meta.get("review_status", ""),
                    "entry_id":             meta.get("entry_id", ""),
                    # accumulators (removed before output)
                    "body_lines":     [],
                    "footnote_lines": [],
                }
                if verbose:
                    print(f"  [{source_pdf} p{pdf_page}] {text[:60]}")

            elif region_type in _BODY_TYPES and current is not None:
                current["body_lines"].append(text)
                current["page_end"] = pdf_page

            elif region_type in _FOOT_TYPES and current is not None:
                current["footnote_lines"].append(text)

    # Flush the very last entry
    done = _flush(current)
    if done is not None:
        entries.append(done)

    return entries


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract full Ibn Faris entry bodies from page JSON files."
    )
    parser.add_argument(
        "--data-dir", default=str(_DATA_DIR),
        help=f"Path to data/maqaees/full/ (default: {_DATA_DIR})"
    )
    parser.add_argument(
        "--out", default=str(_FULL_OUT),
        help=f"Output JSONL path (default: {_FULL_OUT})"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print each root heading as it is processed"
    )
    parser.add_argument(
        "--sample", type=int, default=0,
        help="Print N sample entries to stdout instead of writing to disk"
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_path = Path(args.out)

    print(f"Extracting entry bodies from {data_dir} …")
    entries = extract(data_dir, verbose=args.verbose)
    print(f"Extracted {len(entries)} entries.")

    if not entries:
        print("Nothing to write.", file=sys.stderr)
        sys.exit(1)

    # ── Sample mode ───────────────────────────────────────────────────────────
    if args.sample:
        for e in entries[:args.sample]:
            print("\n" + "─" * 60)
            print(f"root    : {e['root_letters']}")
            print(f"source  : {e['source_pdf']} p{e['page_start']}–p{e['page_end']}")
            print(f"type    : {e['semantic_origin_type']} (count={e['origin_count']})")
            print(f"heading : {e['root_heading_text']}")
            print(f"body    : {e['body_text'][:300]}{'…' if len(e['body_text']) > 300 else ''}")
            if e['footnotes']:
                print(f"notes   : {e['footnotes'][:150]}")
            print(f"words   : {e['body_word_count']}")
        return

    # ── Write output ──────────────────────────────────────────────────────────
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(".jsonl.tmp")
    with open(tmp_path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    tmp_path.replace(out_path)

    # ── Stats ─────────────────────────────────────────────────────────────────
    total_words = sum(e["body_word_count"] for e in entries)
    with_body   = sum(1 for e in entries if e["body_word_count"] > 0)
    multi_page  = sum(1 for e in entries if e["page_end"] > e["page_start"])
    no_meta     = sum(1 for e in entries if not e["root_letters"])

    print(f"\n{'─'*50}")
    print(f"Output            : {out_path}")
    print(f"Total entries     : {len(entries)}")
    print(f"With body text    : {with_body}")
    print(f"Multi-page entries: {multi_page}")
    print(f"No metadata match : {no_meta}")
    print(f"Total body words  : {total_words:,}")
    avg = total_words // len(entries) if entries else 0
    print(f"Avg words/entry   : {avg}")
    print(f"{'─'*50}")
    print("✓ root_entries_full.jsonl written.")


if __name__ == "__main__":
    main()
