"""
tests/test_page_regions.py — Maqayis OCR v2

Unit tests for page_regions.classify_lines.
All tests use synthetic line dicts — no PDF required.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from page_regions import classify_lines


def _line(corrected_ocr, x=0.05, y=0.4, w=0.9, h=0.025, corr_conf=0.9):
    return {
        "line_id": "test:p1:l0001",
        "source_pdf": "test.pdf",
        "pdf_page": 1,
        "bounding_box": {"x": x, "y": y, "w": w, "h": h},
        "raw_ocr": corrected_ocr,
        "corrected_ocr": corrected_ocr,
        "raw_candidates": [{"text": corrected_ocr, "confidence": corr_conf}],
        "corrected_candidates": [{"text": corrected_ocr, "confidence": corr_conf}],
        "region_type": "UNKNOWN",
        "review_status": "AUTO_AGREED",
        "human_text": None,
        "reviewer": None,
        "review_date": None,
        "notes": None,
        "observation_ids": [0],
    }


# ── book / chapter headings ───────────────────────────────────────────────────

def test_book_heading_detected():
    lines = [_line("كتاب الحاء")]
    classify_lines(lines)
    assert lines[0]["region_type"] == "BOOK_HEADING"


def test_chapter_heading_detected():
    lines = [_line("باب الحاء مع الدال")]
    classify_lines(lines)
    assert lines[0]["region_type"] == "CHAPTER_HEADING"


# ── root entry ────────────────────────────────────────────────────────────────

def test_root_entry_with_parens():
    lines = [_line("(حد) الحاء والدال أصلان")]
    classify_lines(lines)
    assert lines[0]["region_type"] == "ROOT_ENTRY_START"


def test_root_entry_arabic_parens():
    """Test with Arabic full-width parentheses."""
    lines = [_line("（كتب） الكاف والتاء والباء أصل واحد")]
    classify_lines(lines)
    assert lines[0]["region_type"] == "ROOT_ENTRY_START"


def test_semantic_origin_alone_is_root_entry_start():
    """A short line containing only an origin phrase is treated as root entry start."""
    lines = [_line("أصل واحد", w=0.3)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "ROOT_ENTRY_START"


# ── page structure ────────────────────────────────────────────────────────────

def test_page_number_at_bottom():
    """Digit-only line in bottom strip → PAGE_NUMBER."""
    lines = [_line("٢٣", x=0.45, y=0.02, w=0.1, h=0.025)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "PAGE_NUMBER"


def test_page_header_at_top():
    """Non-digit line in top strip → PAGE_HEADER."""
    lines = [_line("مقاييس اللغة", x=0.1, y=0.94, w=0.8, h=0.025)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "PAGE_HEADER"


def test_footnote_in_bottom_strip():
    """Any text in bottom 20 % strip → FOOTNOTE."""
    lines = [_line("هذا تعليق في الحاشية", x=0.05, y=0.03, w=0.9, h=0.025)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "FOOTNOTE"


def test_footnote_marker_arabic_digit():
    """(١) style footnote reference must be FOOTNOTE, never ROOT_ENTRY_START."""
    lines = [_line("(١) فى الأصل : ( من الشيئين ) .", x=0.58, y=0.16, w=0.28, h=0.020)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "FOOTNOTE", (
        f"Footnote marker (١) was misclassified as {lines[0]['region_type']}"
    )


def test_footnote_marker_western_digit():
    """(1) style footnote reference must also be FOOTNOTE."""
    lines = [_line("(1) See Ibn Faris.", x=0.58, y=0.16, w=0.28, h=0.020)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "FOOTNOTE"


def test_root_entry_with_spaces_inside_parens():
    """Vision often returns ( حد ) with spaces — must still be ROOT_ENTRY_START."""
    lines = [_line("( حد ) الحاء والدال أصلان : الأول المنع ، والثانى طرف الشيء")]
    classify_lines(lines)
    assert lines[0]["region_type"] == "ROOT_ENTRY_START", (
        f"Space-padded root ( حد ) was classified as {lines[0]['region_type']}"
    )


def test_bab_with_leading_paren_is_chapter_heading():
    """Vision sometimes returns (باب ...) with a leading paren."""
    lines = [_line("(باب ما جاء من كلام العرب في المضاعف)")]
    classify_lines(lines)
    assert lines[0]["region_type"] == "CHAPTER_HEADING"


# ── main text ──────────────────────────────────────────────────────────────────

def test_wide_mid_page_text_is_main_text():
    lines = [_line("المنع والثاني طرف الشيء", x=0.05, y=0.5, w=0.9, h=0.025)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "MAIN_TEXT"


# ── low-confidence fallback ───────────────────────────────────────────────────

def test_very_low_confidence_becomes_unknown():
    lines = [_line("???", corr_conf=0.1)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "UNKNOWN"
    assert lines[0]["review_status"] == "REVIEW_REQUIRED"


# ── gold anchor verification ─────────────────────────────────────────────────

def test_gold_had_line():
    """
    The anchor entry from 02.pdf page 3:
      (حد) الحاء والدال أصلان:
    must be classified as ROOT_ENTRY_START.
    """
    gold_text = "(حد) الحاء والدال أصلان:"
    lines = [_line(gold_text)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "ROOT_ENTRY_START", (
        f"Gold anchor line classified as {lines[0]['region_type']} — expected ROOT_ENTRY_START"
    )


def test_gold_second_line():
    """
    'الأول المنع، والثاني طرف الشيء'
    is main body text — must NOT be ROOT_ENTRY_START.
    """
    gold_text = "الأول المنع، والثاني طرف الشيء"
    lines = [_line(gold_text)]
    classify_lines(lines)
    assert lines[0]["region_type"] == "MAIN_TEXT", (
        f"Gold body line classified as {lines[0]['region_type']} — expected MAIN_TEXT"
    )
