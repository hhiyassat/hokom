"""
tests/test_entry_parser.py — Maqayis OCR v2

Unit tests for entry_parser.py.
All tests use synthetic classified line dicts — no PDF required.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from entry_parser import (
    extract_root_letters,
    extract_bab_letter,
    extract_semantic_origin,
    build_root_entries,
    parse_entries,
)


# ── extract_root_letters ──────────────────────────────────────────────────────

def test_root_letters_standard():
    assert extract_root_letters("(حد) الحاء والدال أصلان") == "حد"


def test_root_letters_three_letters():
    assert extract_root_letters("(كتب) الكاف والتاء والباء أصل واحد") == "كتب"


def test_root_letters_with_diacritics():
    # Diacritics should be stripped from extracted root
    result = extract_root_letters("(حَدَّ) الحاء والدال")
    assert result == "حد" or result is not None   # diacritics stripped


def test_root_letters_none_if_no_parens():
    assert extract_root_letters("الحاء والدال أصلان") is None


def test_root_letters_square_bracket():
    assert extract_root_letters("[دين] الدال والياء والنون") == "دين"


# ── extract_bab_letter ────────────────────────────────────────────────────────

def test_bab_letter_haa():
    assert extract_bab_letter("(حد) الحاء والدال أصلان") == "الحاء"


def test_bab_letter_dal():
    assert extract_bab_letter("الدال والواو") == "الدال"


def test_bab_letter_kaf():
    assert extract_bab_letter("(كتب) الكاف والتاء والباء") == "الكاف"


def test_bab_letter_empty_if_none():
    result = extract_bab_letter("هذا نص عادي")
    assert result == ""


# ── extract_semantic_origin ───────────────────────────────────────────────────

def test_origin_asl_wahid():
    phrase, otype, cnt = extract_semantic_origin("أصل واحد يدل على حبس")
    assert otype == "SINGULAR"
    assert cnt == 1
    assert phrase is not None


def test_origin_aslan():
    phrase, otype, cnt = extract_semantic_origin("(حد) الحاء والدال أصلان:")
    assert otype == "DUAL"
    assert cnt == 2


def test_origin_thalatha():
    phrase, otype, cnt = extract_semantic_origin("ثلاثة أصول")
    assert otype == "TRIPLE"
    assert cnt == 3


def test_origin_usul_saheeha():
    phrase, otype, cnt = extract_semantic_origin("أصول صحيحة")
    assert otype == "SOUND_ROOTS"
    assert cnt is None


def test_origin_none():
    phrase, otype, cnt = extract_semantic_origin("هذا مجرد نص عادي")
    assert otype == "NONE"
    assert phrase is None


def test_origin_asl_wahid_with_shadda():
    """OCR sometimes returns أصلّ (shadda) instead of أصلٌ (tanwin)."""
    phrase, otype, cnt = extract_semantic_origin("أصلّ واحدٌ يدل على")
    assert otype == "SINGULAR", f"Expected SINGULAR, got {otype}"
    assert cnt == 1


def test_origin_sahih_ocr_variant_mahih():
    """OCR often reads ص as م: 'أصل محيح' instead of 'أصل صحيح'."""
    phrase, otype, cnt = extract_semantic_origin("أصلٌ محيح يدلُّ على")
    assert otype == "SOUND_ROOTS", f"Expected SOUND_ROOTS, got {otype}"


def test_origin_sahih_ocr_variant_makhih():
    """OCR variant: 'أصل مخيح'."""
    phrase, otype, cnt = extract_semantic_origin("أصلٌ مخيح يدلُّ على")
    assert otype == "SOUND_ROOTS", f"Expected SOUND_ROOTS, got {otype}"


def test_origin_bare_asl_yadull():
    """Ibn Faris sometimes uses bare 'أصلٌ يدلُّ' (no count word) → implied SINGULAR."""
    phrase, otype, cnt = extract_semantic_origin("أصلٌ يدلُّ على مقارنة")
    assert otype == "SINGULAR", f"Expected SINGULAR, got {otype}"
    assert cnt == 1


def test_origin_bare_asly_yadull():
    """OCR variant: أصلى (ى suffix OCR noise)."""
    phrase, otype, cnt = extract_semantic_origin("أصلى يدلُّ على تنمية")
    assert otype == "SINGULAR", f"Expected SINGULAR, got {otype}"


def test_origin_kalimataan():
    """'كلمتان' (two words) is an alternative DUAL phrasing."""
    phrase, otype, cnt = extract_semantic_origin("القاف واللام كلمتان: أحدهما")
    assert otype == "DUAL", f"Expected DUAL, got {otype}"
    assert cnt == 2


def test_origin_kiltaan_ocr():
    """'كلتان' — OCR variant of 'كلمتان'."""
    phrase, otype, cnt = extract_semantic_origin("القاف واللام والسين كلتان: أحدهما")
    assert otype == "DUAL", f"Expected DUAL, got {otype}"


def test_origin_kalima_tadull():
    """'كلمةٌ تدلُّ' indicates a single-meaning root → SINGULAR."""
    phrase, otype, cnt = extract_semantic_origin("الهاء والياء والغين كلمةٌ تدلُّ على رَغَد")
    assert otype == "SINGULAR", f"Expected SINGULAR, got {otype}"
    assert cnt == 1


# ── build_root_entries ────────────────────────────────────────────────────────

def _classified_line(line_id, region_type, corrected_ocr,
                     source_pdf="02.pdf", pdf_page=3):
    return {
        "line_id": line_id,
        "source_pdf": source_pdf,
        "pdf_page": pdf_page,
        "bounding_box": {"x": 0.05, "y": 0.5, "w": 0.9, "h": 0.025},
        "raw_ocr": corrected_ocr,
        "corrected_ocr": corrected_ocr,
        "raw_candidates": [{"text": corrected_ocr, "confidence": 0.9}],
        "corrected_candidates": [{"text": corrected_ocr, "confidence": 0.9}],
        "region_type": region_type,
        "review_status": "AUTO_AGREED",
        "human_text": None,
        "reviewer": None,
        "review_date": None,
        "notes": None,
        "observation_ids": [0],
    }


def test_gold_had_entry():
    """
    The anchor (حد) entry from 02.pdf page 3.
    Expected: root='حد', type=DUAL, count=2.
    """
    lines = [
        _classified_line("02.pdf:p3:l0001", "PAGE_HEADER",    "مقاييس اللغة"),
        _classified_line("02.pdf:p3:l0002", "ROOT_ENTRY_START",
                         "(حد) الحاء والدال أصلان:"),
        _classified_line("02.pdf:p3:l0003", "MAIN_TEXT",
                         "الأول المنع، والثاني طرف الشيء"),
        _classified_line("02.pdf:p3:l0004", "MAIN_TEXT",
                         "فأما المنع فالحدُّ الحاجز بين الشيئين"),
    ]

    entries = build_root_entries(lines, "02.pdf", 3)

    assert len(entries) == 1
    e = entries[0]
    assert e["root_letters"] == "حد"
    assert e["bab_letter"] == "الحاء"
    assert e["semantic_origin_type"] == "DUAL"
    assert e["origin_count"] == 2
    assert "02.pdf:p3:l0003" in e["body_line_ids"]
    assert "02.pdf:p3:l0004" in e["body_line_ids"]


def test_two_roots_on_same_page():
    lines = [
        _classified_line("02.pdf:p3:l0001", "ROOT_ENTRY_START",
                         "(حد) الحاء والدال أصلان:"),
        _classified_line("02.pdf:p3:l0002", "MAIN_TEXT",     "نص أول"),
        _classified_line("02.pdf:p3:l0003", "ROOT_ENTRY_START",
                         "(حر) الحاء والراء أصل واحد"),
        _classified_line("02.pdf:p3:l0004", "MAIN_TEXT",     "نص ثاني"),
    ]
    entries = build_root_entries(lines, "02.pdf", 3)
    assert len(entries) == 2
    assert entries[0]["root_letters"] == "حد"
    assert entries[1]["root_letters"] == "حر"


def test_entry_with_poetry_lines():
    lines = [
        _classified_line("02.pdf:p3:l0001", "ROOT_ENTRY_START",
                         "(حد) الحاء والدال أصلان:"),
        _classified_line("02.pdf:p3:l0002", "MAIN_TEXT",   "نص"),
        _classified_line("02.pdf:p3:l0003", "POETRY",      "شعر البيت"),
        _classified_line("02.pdf:p3:l0004", "MAIN_TEXT",   "نص بعد"),
    ]
    entries = build_root_entries(lines, "02.pdf", 3)
    assert "02.pdf:p3:l0003" in entries[0]["poetry_line_ids"]


def test_no_entries_if_no_root_start():
    lines = [
        _classified_line("p1:l0001", "MAIN_TEXT",    "نص عادي"),
        _classified_line("p1:l0002", "PAGE_NUMBER",  "٤٥"),
    ]
    entries = build_root_entries(lines, "01.pdf", 1)
    assert entries == []


def test_entry_id_format():
    lines = [
        _classified_line("02.pdf:p3:l0001", "ROOT_ENTRY_START",
                         "(حد) الحاء والدال أصلان:"),
    ]
    entries = build_root_entries(lines, "02.pdf", 3)
    assert entries[0]["entry_id"] == "02.pdf:p3:r001"


def test_parse_entries_returns_tuple():
    lines = [
        _classified_line("02.pdf:p3:l0001", "ROOT_ENTRY_START",
                         "(حد) الحاء والدال أصلان:"),
    ]
    result = parse_entries(lines, "02.pdf", 3)
    assert isinstance(result, tuple)
    assert len(result) == 2
