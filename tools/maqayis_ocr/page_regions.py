"""
page_regions.py — Maqayis OCR v2

Classifies each merged OcrLine into one of:

    BOOK_HEADING      كتاب الحاء / كتاب الدال …
    CHAPTER_HEADING   باب الحاء مع الدال …
    ROOT_ENTRY_START  (حد) الحاء والدال أصلان …
    MAIN_TEXT         normal dictionary body text
    POETRY            indented verse / شعر / hemistiches
    FOOTNOTE          small text in bottom strip
    PAGE_HEADER       running header at top strip
    PAGE_NUMBER       lone digit(s)
    UNKNOWN

Classification uses a combination of:
  * bounding-box position on the page (Y normalised, origin = bottom-left)
  * line width relative to page width
  * Arabic text patterns (regex)
  * confidence scores (low-confidence short lines → FOOTNOTE or UNKNOWN)

The function adds/overwrites the "region_type" and "review_status" fields
on each line dict in-place and also returns the modified list.
"""

from __future__ import annotations
import re


# ── Arabic pattern library ────────────────────────────────────────────────────

# Arabic root letters only — explicitly excludes Arabic-Indic digits (U+0660–U+0669)
# and Extended Arabic-Indic digits (U+06F0–U+06F9).
# We use the named letter ranges: ء-ي (U+0621–U+064A) plus extended letter forms.
_AR_LETTERS = r"[ء-يأ-ئٱ-ۓ]"

# Book-level heading:  كتاب الحاء / كتاب الألف …
RE_BOOK_HEADING = re.compile(
    r"^كتاب\s+ال",   # كتاب ال…
)

# Chapter heading:  باب … / (باب ما جاء …)
# Vision sometimes returns a leading ( before باب
RE_CHAPTER_HEADING = re.compile(
    r"^[\(\s]*باب\s+",
)

# Root entry start:  parenthesised root letters (حد), ( حد ), (كتب), etc.
# Key fixes vs v1:
#   • \s* inside brackets — Vision adds spaces: ( حد )
#   • Use _AR_LETTERS (not full ؀-ۿ range) to exclude Arabic digits (١), (٢)
RE_ROOT_PAREN = re.compile(
    r"^[\(\[（‏‎\s]*"       # optional leading bracket / whitespace / RLM
    + _AR_LETTERS + r"{1,5}"  # 1–5 Arabic root letters (no digits)
    + r"\s*[\)\]）]"          # optional space then closing bracket
)

# Semantic-origin phrases that often appear on the root-entry line or nearby
RE_SEMANTIC_ORIGIN = re.compile(
    r"(أصل\s+واحد|أصلان|ثلاثة\s+أصول|أربعة\s+أصول|أصول\s+صحيحة|"
    r"أصل\s+صحيح|أصلٌ\s+واحدٌ)"
)

# Page-number: short line containing only digits / Arabic numerals
RE_PAGE_NUMBER = re.compile(r"^[\d٠-٩۰-۹\s\-\/]+$")

# Footnote reference marker: (١), (٢), (٣) … at start of line.
# Arabic-Indic digits are U+0660–U+0669; Western digits also accepted.
# These are footnote anchors, never root letters — must be caught BEFORE RE_ROOT_PAREN.
RE_FOOTNOTE_MARKER = re.compile(
    r"^[\(\[]\s*[\d٠-٩۰-۹]{1,3}\s*[\)\]]"
)

# Poetry indicators:  a short line centred / wide gap / starts with measure
RE_POETRY_MARKER = re.compile(
    r"(^[\*•◦]\s|وزن\s|بحر\s|قال\s+شاعر|^على\s+وزن|"
    r"قال\s+[اأ]ل|^فَ|^وَ)"   # قال الأعشى / قال النابغة / hemistich openings
)

# Short poetry attribution lines: "قال الأعشى:" / "وقال النابغة فى الحد والمنّع:"
RE_POETRY_INTRO = re.compile(
    r"^وقال\s|^قال\s"
)


# ── positional heuristics ─────────────────────────────────────────────────────

FOOTNOTE_Y_THRESHOLD    = 0.20    # bottom 20 % of page (footnotes often start at ~16%)
PAGE_HEADER_Y_THRESHOLD = 0.92    # top 8 % of page
NARROW_WIDTH_RATIO      = 0.40    # line narrower than 40 % → likely marginal
SHORT_TEXT_LEN          = 6       # text shorter than N chars → suspect


def _is_wide(line: dict, page_width_ratio: float = 0.55) -> bool:
    """Line spans more than 55 % of page width → likely body text."""
    return line["bounding_box"]["w"] >= page_width_ratio


def _bbox_top_y(line: dict) -> float:
    """Top edge of bounding box (in Vision normalised coords, origin bottom-left)."""
    bb = line["bounding_box"]
    return bb["y"] + bb["h"]


def _bbox_bottom_y(line: dict) -> float:
    return line["bounding_box"]["y"]


def _best_text(line: dict) -> str:
    """Return corrected_ocr if non-empty, else raw_ocr."""
    return (line.get("corrected_ocr") or line.get("raw_ocr") or "").strip()


def _top_confidence(line: dict) -> float:
    cands = line.get("corrected_candidates") or line.get("raw_candidates") or []
    if cands:
        return float(cands[0].get("confidence", 0))
    return 0.0


# ── main classifier ───────────────────────────────────────────────────────────

def classify_lines(lines: list[dict]) -> list[dict]:
    """
    Classify each line in-place.  Returns the same list.

    Uses page-relative Y only (no absolute pixel sizes needed).
    """
    for line in lines:
        text = _best_text(line)
        conf = _top_confidence(line)
        by   = _bbox_bottom_y(line)   # normalised, 0 = bottom of page
        ty   = _bbox_top_y(line)

        # ── 1. positional: page header / footer ──────────────────────────────
        if ty >= PAGE_HEADER_Y_THRESHOLD:
            if RE_PAGE_NUMBER.match(text):
                line["region_type"] = "PAGE_NUMBER"
            else:
                line["region_type"] = "PAGE_HEADER"
            continue

        if by <= FOOTNOTE_Y_THRESHOLD:
            if len(text) > 0 and conf < 0.4:
                line["region_type"] = "FOOTNOTE"
                line["review_status"] = "REVIEW_REQUIRED"
            elif len(text) <= SHORT_TEXT_LEN and RE_PAGE_NUMBER.match(text):
                line["region_type"] = "PAGE_NUMBER"
            else:
                line["region_type"] = "FOOTNOTE"
                if conf < 0.5:
                    line["review_status"] = "REVIEW_REQUIRED"
            continue

        # ── 2. pattern-based ─────────────────────────────────────────────────

        # Footnote reference marker MUST be checked before RE_ROOT_PAREN
        # because (١), (٢) look like root brackets to the paren regex.
        if RE_FOOTNOTE_MARKER.match(text):
            line["region_type"] = "FOOTNOTE"
            line["review_status"] = "REVIEW_REQUIRED"
            continue

        if RE_BOOK_HEADING.search(text):
            line["region_type"] = "BOOK_HEADING"
            continue

        if RE_CHAPTER_HEADING.search(text):
            line["region_type"] = "CHAPTER_HEADING"
            continue

        # Root entry: starts with parenthesised root letters
        if RE_ROOT_PAREN.match(text):
            line["region_type"] = "ROOT_ENTRY_START"
            continue

        # Semantic origin without explicit root bracket (can appear as its own line)
        if RE_SEMANTIC_ORIGIN.search(text) and len(text) < 40:
            line["region_type"] = "ROOT_ENTRY_START"
            continue

        # Poetry attribution ("وقال النابغة ...") — narrow lines that introduce a verse
        if RE_POETRY_INTRO.match(text) and not _is_wide(line):
            line["region_type"] = "POETRY"
            line["review_status"] = "REVIEW_REQUIRED"
            continue

        if RE_POETRY_MARKER.search(text) or (
            not _is_wide(line) and line["bounding_box"]["w"] < NARROW_WIDTH_RATIO
            and len(text) > 10
        ):
            line["region_type"] = "POETRY"
            line["review_status"] = "REVIEW_REQUIRED"
            continue

        if RE_PAGE_NUMBER.match(text) and len(text) < 6:
            line["region_type"] = "PAGE_NUMBER"
            continue

        # ── 3. fallback: confidence-gated ────────────────────────────────────
        if conf < 0.35:
            line["region_type"] = "UNKNOWN"
            line["review_status"] = "REVIEW_REQUIRED"
            continue

        line["region_type"] = "MAIN_TEXT"

    return lines


# ── CLI self-test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json, sys
    if len(sys.argv) < 2:
        print("Usage: python page_regions.py <lines.json>")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        lines = json.load(f)

    classify_lines(lines)
    print(json.dumps(lines, ensure_ascii=False, indent=2))

    counts: dict[str, int] = {}
    for ln in lines:
        rt = ln["region_type"]
        counts[rt] = counts.get(rt, 0) + 1
    print("\nRegion counts:", counts, file=sys.stderr)
