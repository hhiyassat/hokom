#!/usr/bin/env python3
"""
post_classifier.py — Maqayis OCR v2
Re-classifies REVIEW_REQUIRED root entries using pattern matching on the
heading text, without re-running OCR.

Adds three new semantic_origin_type values beyond the existing set:
  NOT_ROOT        — explicitly marked by Ibn Faris as not an independent root
                    ("ليس بأصل", "ليس أصلًا", "ليس بشىء")
  CROSS_REFERENCE — root content covered under another entry
                    ("قد مضى", "قد تقدّم", "مضى ذكره")
  CHAPTER_HEADER  — single Arabic letter or chapter marker, not a root entry

Existing types that get better recall:
  SINGULAR        — catches "كلمةٌ واحدةٌ" / "كلمة واحدة" alongside "أصل واحد"
  MULTIPLE        — catches "أصول" (plural, unspecified count)

Input : data/maqaees/full/root_entries.jsonl
Output: data/maqaees/full/root_entries.jsonl   (updated in-place, atomic)
        data/maqaees/full/post_classify_report.json

Usage:
    python3 tools/maqayis_ocr/post_classifier.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Arabic diacritics (harakat, tanwin, shadda, sukun, superscript alef)
# U+064B–U+065F = fathatan … wavy hamza below
# U+0670 = superscript alef
_DIACRITICS_RE = re.compile(r"[ً-ٰٟ]")

_REPO_ROOT  = Path(__file__).resolve().parents[2]
_JSONL_IN   = _REPO_ROOT / "data" / "maqaees" / "full" / "root_entries.jsonl"
_REPORT_OUT = _REPO_ROOT / "data" / "maqaees" / "full" / "post_classify_report.json"

# ── pattern library ───────────────────────────────────────────────────────────

# Each rule: (new_type, new_status, compiled_regex)
# Rules are tried in order; first match wins.
_RULES: list[tuple[str, str, re.Pattern]] = [

    # ── CHAPTER_HEADER ────────────────────────────────────────────────────────
    # Single Arabic letter (possibly with parens/spaces) — chapter markers
    (
        "CHAPTER_HEADER", "AUTO_AGREED",
        re.compile(r"^\s*[\(\)]*\s*[؀-ۿ]\s*[\(\)]*\s*$"),
    ),

    # ── NOT_ROOT ──────────────────────────────────────────────────────────────
    # Ibn Faris explicitly says this is not an independent root.
    # Patterns match AFTER diacritics are stripped (so أصلًا → أصلا).
    (
        "NOT_ROOT", "AUTO_AGREED",
        re.compile(
            r"[لن]ي[سش]\s*(ب)?أصل"        # ليس/نيس بأصل
            r"|[لن]ي[سش]\s*بش[يى]?[ءئ]"  # ليس بشيء / بشئ
            r"|[لن]ي[سش]\s*بشم"            # ليس بشم (OCR of بشيء)
            r"|[لن]ي[سش]\s*من\s*الباب"    # ليس من الباب
            r"|مقلوب"                       # مقلوب (transposition)
            r"|مبدل[ةه]?\s*من"             # مبدلة من
            r"|ليست?\s*اصلا"               # ليست أصلًا (after stripping)
            r"|كلمات?\s+غير\s+موضوع"       # كلمات غير موضوعة على قياس = irregular
            r"|كل[ةمه]?\s+لا\s+معن",      # كلة/كلمة لا معنى لها = unrecognized word
            re.UNICODE,
        ),
    ),

    # ── CROSS_REFERENCE ──────────────────────────────────────────────────────
    # Content covered under a different entry
    (
        "CROSS_REFERENCE", "AUTO_AGREED",
        re.compile(
            r"قد\s+مضى"                   # قد مضى (ذكره / الكلام)
            r"|قد\s+تقدّ?م"               # قد تقدّم
            r"|مضى\s+ذكر"                 # مضى ذكره
            r"|ذكرن?اه?\s+في"             # ذكرناه في / ذكرنا في
            r"|انظر\s+باب"                # انظر باب
            r"|ذلك\s+قد\s+مضى"
            r"|مكرر",                     # (مكرر) = repeated/duplicate entry
            re.UNICODE,
        ),
    ),

    # ── DUAL (OCR variants) ───────────────────────────────────────────────────
    # "كامتان" = OCR corruption of "كلمتان" (two words/senses)
    # After diacritic stripping these forms are unchanged (no diacritics in them).
    (
        "DUAL", "AUTO_AGREED",
        re.compile(
            r"كامت[اأ]ن"                  # كامتان → كلمتان (OCR corruption)
            r"|كلمت[اأ]ن",               # كلمتان (clean form)
            re.UNICODE,
        ),
    ),

    # ── SINGULAR (extended) ───────────────────────────────────────────────────
    # All patterns match AFTER diacritics are stripped, so ًٌٍ chars are absent.
    (
        "SINGULAR", "AUTO_AGREED",
        re.compile(
            # --- clean forms (diacritics stripped, so ًا→ا) ---
            r"كلم[ةه]\s+واحد[ةه]"         # كلمة واحدة
            r"|أصل\s+واحد"                 # أصل واحد
            r"|أصل\s+[مص]حي[حخ]?\s+واحد"  # أصل صحيح/محيح واحد
            r"|اصلا\s+واحدا"               # أصلًا واحدًا (after stripping)
            r"|أصل\s+صحيح\s+(?!ان)"        # أصل صحيح (not أصلان)
            # --- كلمة / كلة OCR variants (diacritics stripped) ---
            r"|كل[ةه]\s+واحد[ةه]"          # كلة واحدة (missing م from كلمة)
            r"|كام[ةه]\s+واحد[ةه]"         # كامة واحدة (OCR corruption)
            r"|كلم[ةه]\s+(تدل|يدل|تدك|يدك)"  # كلمة تدل على
            r"|كل[ةه]\s+(تدل|يدل|تدك|يدك)"   # كلة تدل على (missing م)
            # --- أصيل (diminutive of أصل = minor/single root) ---
            r"|[أا]صيل"                    # أُصَيْل (after stripping: hamza or plain alef)
            # --- أصل + يدل/يدك على (one meaning = SINGULAR) ---
            r"|أصل\s+يد[لك]"               # أصل يدل/يدك على
            # --- أصل مطّرد (regular productive root = one root class) ---
            r"|أصل\s+مطرد"                  # أصل مطرد (after stripping shadda)
            # --- حرف يدل / bare يدل (one sense = SINGULAR) ---
            r"|حرف\s+يد[لك]"               # حرف يدل على X
            r"|يد[لك]\s+على"               # bare يدل على (no count prefix = SINGULAR)
            # --- بناء/قياس صحيح ---
            r"|بناء\s+[مص]حي[حخ]"          # بناء صحيح/محيح
            r"|قياس\s+[مص]حي[حخ]"          # قياس صحيح/محيح
            # --- في معنى واحد ---
            r"|في[هةه]?\s+معن[ىي]\s+واحد",  # فيه/في معنى واحد
            re.UNICODE,
        ),
    ),

    # ── MULTIPLE (extended) ───────────────────────────────────────────────────
    # "أصول" = multiple unspecified roots
    (
        "MULTIPLE", "AUTO_AGREED",
        re.compile(
            r"\bأصول\b"                   # أصول (plural)
            r"|أصول\s+كثير",
            re.UNICODE,
        ),
    ),
]


def _strip_diacritics(text: str) -> str:
    """Remove Arabic harakat/tanwin/shadda so patterns match regardless of vowelling."""
    return _DIACRITICS_RE.sub("", text)


def _classify_heading(heading: str) -> tuple[str | None, str | None]:
    """
    Apply rules to heading text (after stripping diacritics).
    Returns (new_type, new_status) or (None, None) if no rule matches.
    """
    normalized = _strip_diacritics(heading)
    for new_type, new_status, pattern in _RULES:
        if pattern.search(normalized):
            return new_type, new_status
    return None, None


def _process(jsonl_path: Path, dry_run: bool) -> dict:
    entries: list[dict] = []
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))

    changes: dict[str, int] = {}
    changed_entries: list[dict] = []
    skipped = 0

    for entry in entries:
        if entry.get("review_status") != "REVIEW_REQUIRED":
            skipped += 1
            continue

        heading = (entry.get("root_heading_text") or "").strip()
        new_type, new_status = _classify_heading(heading)

        if new_type is None:
            continue  # still REVIEW_REQUIRED — no pattern matched

        old_type = entry.get("semantic_origin_type", "NONE")
        key = f"{old_type} → {new_type}"
        changes[key] = changes.get(key, 0) + 1

        changed_entries.append({
            "entry_id":   entry.get("entry_id"),
            "root":       entry.get("root_letters"),
            "heading":    heading[:80],
            "old_type":   old_type,
            "new_type":   new_type,
        })

        if not dry_run:
            entry["semantic_origin_type"] = new_type
            entry["review_status"]        = new_status
            entry["post_classified"]      = True

    # ── report ────────────────────────────────────────────────────────────────
    remaining_rr = sum(
        1 for e in entries if e.get("review_status") == "REVIEW_REQUIRED"
    )
    report = {
        "total_entries":         len(entries),
        "auto_agreed_before":    skipped,
        "reclassified":          len(changed_entries),
        "remaining_review":      remaining_rr if not dry_run
                                 else (sum(1 for e in entries
                                           if e.get("review_status") == "REVIEW_REQUIRED")
                                       - len(changed_entries)),
        "changes_by_transition": changes,
        "dry_run":               dry_run,
        "sample_changes":        changed_entries[:20],
    }

    if not dry_run:
        tmp = jsonl_path.with_suffix(".jsonl.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            for e in entries:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
        tmp.replace(jsonl_path)

        with open(_REPORT_OUT, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-classify REVIEW_REQUIRED root entries by heading patterns."
    )
    parser.add_argument(
        "--jsonl", default=str(_JSONL_IN),
        help=f"Path to root_entries.jsonl (default: {_JSONL_IN})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without writing files"
    )
    args = parser.parse_args()

    jsonl_path = Path(args.jsonl)
    if not jsonl_path.exists():
        print(f"ERROR: {jsonl_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"{'DRY RUN — ' if args.dry_run else ''}Processing {jsonl_path} …")
    report = _process(jsonl_path, dry_run=args.dry_run)

    print(f"\nTotal entries     : {report['total_entries']}")
    print(f"Already agreed    : {report['auto_agreed_before']}")
    print(f"Reclassified      : {report['reclassified']}")
    print(f"Still REVIEW_REQ  : {report['remaining_review']}")
    print(f"\nTransitions:")
    for t, c in sorted(report["changes_by_transition"].items(),
                        key=lambda x: -x[1]):
        print(f"  {t:30s} ×{c}")

    if args.dry_run:
        print("\n(dry run — no files written)")
    else:
        print(f"\n✓ root_entries.jsonl updated.")
        print(f"  Report → {_REPORT_OUT}")


if __name__ == "__main__":
    main()
