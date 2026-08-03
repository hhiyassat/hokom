"""
entry_parser.py — Maqayis OCR v2

Detects root-heading lines and extracts:
  * root letters  (حد), (كتب), (دين) …
  * bab letter    الحاء، الدال، الكاف …
  * semantic-origin type  أصل واحد / أصلان / ثلاثة أصول …
  * numeric count of origins

Also assembles RootEntry records by grouping the lines that belong to each
entry (from ROOT_ENTRY_START until the next ROOT_ENTRY_START or end-of-page).

Input  : a list of classified OcrLine dicts (output of page_regions.classify_lines)
Output : tuple( updated_lines, list[root_entry_dict] )

Root-entry dicts match schemas/root_entry.schema.json.
"""

from __future__ import annotations
import re
from typing import Any


# ── Arabic letter name → single letter map ───────────────────────────────────
# Maqayis uses the full name (الحاء) in headings.
BAB_LETTER_MAP: dict[str, str] = {
    "الهمزة": "أ", "الألف": "ا", "الباء": "ب", "التاء": "ت",
    "الثاء": "ث", "الجيم": "ج", "الحاء": "ح", "الخاء": "خ",
    "الدال": "د", "الذال": "ذ", "الراء": "ر", "الزاي": "ز",
    "السين": "س", "الشين": "ش", "الصاد": "ص", "الضاد": "ض",
    "الطاء": "ط", "الظاء": "ظ", "العين": "ع", "الغين": "غ",
    "الفاء": "ف", "القاف": "ق", "الكاف": "ك", "اللام": "ل",
    "الميم": "م", "النون": "ن", "الهاء": "ه", "الواو": "و",
    "الياء": "ي",
}

# ── patterns ──────────────────────────────────────────────────────────────────

# Extract root letters from heading: (حد), (كتب), ( حد ), (دين)
# Uses only Arabic letter ranges — excludes Arabic-Indic digits (٠-٩, U+0660–U+0669)
# and Extended Arabic-Indic digits (U+06F0–U+06F9).
# Vision often adds spaces inside parens: ( حد ) — handled with \s*
RE_ROOT_EXTRACT = re.compile(
    r"[\(\[（]\s*"
    # Arabic root letters plus interspersed diacritics (tashkeel U+064B–U+065F,
    # superscript alef U+0670, tatweel U+0640). Digits (U+0660–U+0669) excluded.
    # _strip_arabic() removes diacritics from the extracted result.
    r"([ء-يأ-ئٱ-ۓً-ٟـٰ]{1,15})"
    r"\s*[\)\]）]"
)

# Bab/chapter letter name in the heading line:  الحاء والدال / الحاء مع الدال
RE_BAB_LETTER = re.compile(
    r"(الهمزة|الألف|الباء|التاء|الثاء|الجيم|الحاء|الخاء|"
    r"الدال|الذال|الراء|الزاي|السين|الشين|الصاد|الضاد|"
    r"الطاء|الظاء|العين|الغين|الفاء|القاف|الكاف|اللام|"
    r"الميم|النون|الهاء|الواو|الياء)"
)

# Semantic origin phrases, ordered from most-specific to least.
# NOTE: patterns are matched on DIACRITIC-STRIPPED text (see extract_semantic_origin),
# so do NOT include tashkeel in the patterns — they are already removed.
SEMANTIC_PATTERNS: list[tuple[str, str, int | None]] = [
    # text pattern                    origin_type       count
    # ── explicit counts ────────────────────────────────────────────────────────
    (r"أصل\s+واحد",                  "SINGULAR",        1),
    (r"أصلان",                       "DUAL",            2),
    (r"كلمتان|كلتان",                "DUAL",            2),   # alternate "two words" forms
    (r"ثلاثة\s+أصول",               "TRIPLE",          3),
    (r"أربعة\s+أصول",               "MULTIPLE",        4),
    (r"خمسة\s+أصول",                "MULTIPLE",        5),
    (r"ستة\s+أصول",                 "MULTIPLE",        6),
    (r"سبعة\s+أصول",                "MULTIPLE",        7),
    # ── sound-root markers (صحيح + common OCR variants م/خ confusion) ─────────
    (r"أصول\s+صحيحة",               "SOUND_ROOTS",     None),
    (r"أصل\s+[صم][حخ]يح",          "SOUND_ROOTS",     None),
    # ── implied-singular phrasings (bare أصل + يدل / كلمة تدل) ───────────────
    (r"أصل[يى]?\s+يدل",             "SINGULAR",        1),
    (r"كلمة\s+تدل",                  "SINGULAR",        1),
    # ── generic plural fallback ────────────────────────────────────────────────
    (r"أصول",                       "MULTIPLE",        None),
]

COMPILED_SEMANTIC = [
    (re.compile(pat, re.UNICODE), ot, cnt)
    for pat, ot, cnt in SEMANTIC_PATTERNS
]


# ── strip utility ─────────────────────────────────────────────────────────────

def _strip_arabic(text: str) -> str:
    """Remove diacritics and directional marks."""
    # Unicode ranges: Arabic diacritics U+064B–U+065F, tatweel U+0640
    return re.sub(r"[ً-ٟـ‏‎‍‌]", "", text)


def _best_text(line: dict) -> str:
    return (line.get("corrected_ocr") or line.get("raw_ocr") or "").strip()


# ── extraction functions ──────────────────────────────────────────────────────

def extract_root_letters(text: str) -> str | None:
    """Return the root consonants from a heading line, or None."""
    m = RE_ROOT_EXTRACT.search(text)
    if m:
        raw = m.group(1)
        return _strip_arabic(raw)
    return None


def extract_bab_letter(text: str) -> str:
    """Return the full Arabic letter name (الحاء) from a heading line."""
    m = RE_BAB_LETTER.search(text)
    return m.group(1) if m else ""


def extract_semantic_origin(text: str) -> tuple[str | None, str, int | None]:
    """
    Returns (matched_phrase, origin_type, count).

    Diacritics are stripped from *text* before matching so SEMANTIC_PATTERNS
    need not include tashkeel variants.  The matched phrase returned is the
    stripped form (sufficient for human review; raw text is stored elsewhere).
    """
    stripped = _strip_arabic(text)
    for pattern, otype, cnt in COMPILED_SEMANTIC:
        m = pattern.search(stripped)
        if m:
            return m.group(0), otype, cnt
    return None, "NONE", None


# ── entry assembly ────────────────────────────────────────────────────────────

def build_root_entries(
    lines: list[dict],
    source_pdf: str,
    pdf_page: int,
) -> list[dict]:
    """
    Walk classified lines and build RootEntry records.

    A new entry begins each time a ROOT_ENTRY_START line is encountered.
    All subsequent non-entry lines are assigned to the current open entry
    until the next ROOT_ENTRY_START or end of page.
    """
    entries: list[dict] = []
    current: dict | None = None
    entry_n = 0

    def _close(e: dict) -> None:
        e["line_ids"] = (
            [e["_heading_line_id"]]
            + e["body_line_ids"]
            + e["poetry_line_ids"]
            + e["footnote_line_ids"]
        )
        del e["_heading_line_id"]
        entries.append(e)

    for line in lines:
        rt   = line.get("region_type", "UNKNOWN")
        text = _best_text(line)
        lid  = line["line_id"]

        if rt == "ROOT_ENTRY_START":
            if current is not None:
                _close(current)

            entry_n += 1
            root_letters = extract_root_letters(text) or ""
            bab_letter   = extract_bab_letter(text)
            phrase, otype, cnt = extract_semantic_origin(text)

            # Flag lines that need review
            review = "AUTO_AGREED"
            if not root_letters:
                review = "REVIEW_REQUIRED"
                line["review_status"] = "REVIEW_REQUIRED"
            if otype in ("NONE", "UNKNOWN"):
                # May be on the next line — we'll check body lines
                review = "REVIEW_REQUIRED"

            current = {
                "entry_id":              f"{source_pdf}:p{pdf_page}:r{entry_n:03d}",
                "source_pdf":            source_pdf,
                "pdf_page":              pdf_page,
                "root_heading_text":     text,
                "root_letters":          root_letters,
                "bab_letter":            bab_letter,
                "semantic_origin_text":  phrase,
                "semantic_origin_type":  otype,
                "origin_count":          cnt,
                "body_line_ids":         [],
                "poetry_line_ids":       [],
                "footnote_line_ids":     [],
                "_heading_line_id":      lid,
                "review_status":         review,
                "human_verified":        False,
                "reviewer":              None,
                "review_date":           None,
            }
            continue

        if current is None:
            continue   # pre-entry lines (book heading, page header, etc.)

        # If we haven't found the origin phrase yet, look in the first body lines
        if current["semantic_origin_type"] in ("NONE", "UNKNOWN", None):
            phrase, otype, cnt = extract_semantic_origin(text)
            if otype not in ("NONE", "UNKNOWN"):
                current["semantic_origin_text"] = phrase
                current["semantic_origin_type"] = otype
                current["origin_count"]         = cnt
                if current["review_status"] == "REVIEW_REQUIRED":
                    current["review_status"] = "AUTO_AGREED"

        if rt == "MAIN_TEXT":
            current["body_line_ids"].append(lid)
        elif rt == "POETRY":
            current["poetry_line_ids"].append(lid)
        elif rt == "FOOTNOTE":
            current["footnote_line_ids"].append(lid)
        # PAGE_HEADER, PAGE_NUMBER, BOOK_HEADING etc. are not assigned

    if current is not None:
        _close(current)

    return entries


# ── public API ────────────────────────────────────────────────────────────────

def parse_entries(
    lines: list[dict],
    source_pdf: str,
    pdf_page: int,
) -> tuple[list[dict], list[dict]]:
    """
    Run both root-entry detection and review-status flagging.

    Returns
    -------
    (updated_lines, root_entries)
    """
    entries = build_root_entries(lines, source_pdf, pdf_page)
    return lines, entries


# ── CLI self-test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json, sys
    if len(sys.argv) < 2:
        print("Usage: python entry_parser.py <classified_lines.json>")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        lines = json.load(f)

    if not lines:
        print("[]"); sys.exit(0)

    source_pdf = lines[0].get("source_pdf", "unknown.pdf")
    pdf_page   = lines[0].get("pdf_page", 0)

    lines, entries = parse_entries(lines, source_pdf, pdf_page)

    result = {"lines": lines, "root_entries": entries}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[entry_parser] {len(entries)} root entries detected", file=sys.stderr)
