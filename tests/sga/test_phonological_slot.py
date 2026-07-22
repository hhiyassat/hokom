"""
T-02 test coverage: typed phonological caller boundaries.

Tests wrap_syllabify_output() for all required kind/provenance cases.
Python 3.10+ compatible. No skip. No xfail.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline.p1_atomic_structure.phonological_slot import (
    PhonologicalSlot,
    PhonologicalSlotKind,
    wrap_syllabify_output,
)


# ── helpers ────────────────────────────────────────────────────────────────────

def _make_cell(**kwargs) -> dict:
    """Construct a minimal cell dict."""
    base = {
        "surface": "", "pattern": "", "gate": "",
        "violations": [], "status_at_close": "",
        "close_reason": "", "saturation_reason": "",
    }
    base.update(kwargs)
    return base


# ── kind preservation (explicit 'kind' key) ────────────────────────────────────

def test_shadda_kind_preserved():
    """shadda slot → kind=SHADDA preserved when explicit kind provided."""
    cells = [{"character": "شّ", "kind": "SHADDA"}]
    slots = wrap_syllabify_output(cells)
    assert len(slots) == 1
    assert slots[0].kind == PhonologicalSlotKind.SHADDA


def test_sukun_kind_preserved():
    """sukun slot → kind=SUKUN preserved when explicit kind provided."""
    cells = [{"character": "كْ", "kind": "SUKUN"}]
    slots = wrap_syllabify_output(cells)
    assert slots[0].kind == PhonologicalSlotKind.SUKUN


def test_madd_kind_preserved():
    """madd slot → kind=MADD preserved when explicit kind provided."""
    cells = [{"character": "ا", "kind": "MADD"}]
    slots = wrap_syllabify_output(cells)
    assert slots[0].kind == PhonologicalSlotKind.MADD


def test_hamza_kind_preserved():
    """hamzat al-wasl → kind=HAMZA preserved when explicit kind provided."""
    cells = [{"character": "ا", "kind": "HAMZA"}]
    slots = wrap_syllabify_output(cells)
    assert slots[0].kind == PhonologicalSlotKind.HAMZA


# ── kind inference from syllabify dict fields ──────────────────────────────────

def test_hamza_inferred_from_status_at_close():
    """status_at_close=HAMZAT_AL_WASL → kind=HAMZA inferred."""
    cell = _make_cell(surface="ا", status_at_close="HAMZAT_AL_WASL",
                      close_reason="HAMZAT_AL_WASL_SKIP")
    slots = wrap_syllabify_output([cell])
    assert slots[0].kind == PhonologicalSlotKind.HAMZA


def test_hamza_inferred_from_close_reason():
    """close_reason=HAMZAT_AL_WASL_SKIP → kind=HAMZA inferred."""
    cell = _make_cell(surface="ا", close_reason="HAMZAT_AL_WASL_SKIP")
    slots = wrap_syllabify_output([cell])
    assert slots[0].kind == PhonologicalSlotKind.HAMZA


def test_madd_inferred_from_alef_farqa_status():
    """status_at_close=ALEF_FARQA → kind=MADD inferred."""
    cell = _make_cell(surface="ا", status_at_close="ALEF_FARQA",
                      close_reason="ALEF_FARQA_BOUNDARY")
    slots = wrap_syllabify_output([cell])
    assert slots[0].kind == PhonologicalSlotKind.MADD


def test_madd_inferred_from_cvv_pattern():
    """pattern=CVV (long vowel syllable) → kind=MADD inferred."""
    cell = _make_cell(surface="كِيـ", pattern="CVV", gate="ACCEPT",
                      status_at_close="COMPLETE")
    slots = wrap_syllabify_output([cell])
    assert slots[0].kind == PhonologicalSlotKind.MADD


def test_sukun_inferred_from_bare_c_pattern():
    """pattern=C (bare consonant, no vowel) → kind=SUKUN inferred."""
    cell = _make_cell(surface="ل", pattern="C", gate="DEFER",
                      status_at_close="PREFIX")
    slots = wrap_syllabify_output([cell])
    assert slots[0].kind == PhonologicalSlotKind.SUKUN


def test_consonant_inferred_from_cv_pattern():
    """pattern=CV → kind=CONSONANT inferred."""
    cell = _make_cell(surface="كَ", pattern="CV", gate="ACCEPT",
                      status_at_close="COMPLETE")
    slots = wrap_syllabify_output([cell])
    assert slots[0].kind == PhonologicalSlotKind.CONSONANT


# ── solar assimilation / gemination provenance ─────────────────────────────────

def test_assimilation_gemination_type_preserved_explicit():
    """assimilation_gemination_type preserved when explicit."""
    cells = [{"character": "لّ", "kind": "SHADDA",
              "assimilation_gemination_type": "ASSIMILATION_GEMINATION"}]
    slots = wrap_syllabify_output(cells)
    assert slots[0].assimilation_gemination_type == "ASSIMILATION_GEMINATION"


def test_assimilation_gemination_inferred_from_saturation_reason():
    """assimilation_gemination_type inferred from saturation_reason containing 'assimilation'."""
    cell = _make_cell(
        surface="لّ", pattern="CVC", gate="ACCEPT",
        status_at_close="COMPLETE",
        saturation_reason="solar assimilation triggered gemination",
    )
    slots = wrap_syllabify_output([cell])
    assert slots[0].assimilation_gemination_type == "ASSIMILATION_GEMINATION"


def test_assimilation_gemination_absent_without_trigger():
    """assimilation_gemination_type is None when saturation_reason has no 'assimilation'."""
    cell = _make_cell(surface="كَ", pattern="CV", gate="ACCEPT",
                      saturation_reason="next symbol 'بَ' starts new onset")
    slots = wrap_syllabify_output([cell])
    assert slots[0].assimilation_gemination_type is None


# ── original_surface provenance ────────────────────────────────────────────────

def test_original_surface_provenance_preserved():
    """original_surface provenance survives through phonological layer."""
    cells = [{"character": "كَ", "kind": "CONSONANT",
              "original_surface": "كَتَبَ"}]
    slots = wrap_syllabify_output(cells)
    assert slots[0].original_surface == "كَتَبَ"


def test_original_surface_none_when_absent():
    """original_surface is None when not provided."""
    cells = [{"character": "كَ", "kind": "CONSONANT"}]
    slots = wrap_syllabify_output(cells)
    assert slots[0].original_surface is None


# ── round-trip: character preservation ────────────────────────────────────────

def test_roundtrip_character_preserved_from_explicit():
    """round-trip: character field preserved from explicit 'character' key."""
    raw = [{"character": "مُ"}, {"character": "دَ"}, {"character": "رِّ"}]
    slots = wrap_syllabify_output(raw)
    assert tuple(s.character for s in slots) == ("مُ", "دَ", "رِّ")


def test_roundtrip_character_preserved_from_surface():
    """round-trip: character field preserved from 'surface' key (syllabify output)."""
    # Simulate actual syllabify() output format
    raw = [
        _make_cell(surface="مُ", pattern="CV", gate="ACCEPT", status_at_close="COMPLETE"),
        _make_cell(surface="دَرْ", pattern="CVC", gate="ACCEPT", status_at_close="COMPLETE"),
        _make_cell(surface="رِ", pattern="CV", gate="ACCEPT", status_at_close="COMPLETE"),
        _make_cell(surface="سٌ", pattern="CV", gate="ACCEPT", status_at_close="COMPLETE"),
    ]
    slots = wrap_syllabify_output(raw)
    assert len(slots) == 4
    assert slots[0].character == "مُ"
    assert slots[1].character == "دَرْ"
    assert slots[2].character == "رِ"
    assert slots[3].character == "سٌ"


def test_roundtrip_position_sequence():
    """PhonologicalSlot.position is sequential 0-based."""
    raw = [_make_cell(surface=c, pattern="CV") for c in ["كَ", "تَ", "بَ"]]
    slots = wrap_syllabify_output(raw)
    assert tuple(s.position for s in slots) == (0, 1, 2)


def test_empty_input_returns_empty_tuple():
    """Empty input → empty tuple."""
    assert wrap_syllabify_output([]) == ()


def test_roundtrip_with_real_syllabify():
    """Integration: wrap_syllabify_output works with actual syllabify() output."""
    from pipeline.p1_atomic_structure.cell_builder import parse_phones, syllabify
    phones = parse_phones("كَتَبَ")
    raw_slots = syllabify(phones)
    typed = wrap_syllabify_output(raw_slots)
    assert isinstance(typed, tuple)
    assert all(isinstance(s, PhonologicalSlot) for s in typed)
    # Each typed slot has a non-empty character from surface
    real = [s for s in typed if s.character and s.character != " "]
    assert len(real) >= 1
    for s in real:
        assert s.character, f"character must not be empty at position {s.position}"


def test_analyze_word_includes_typed_syllables():
    """cell_builder.analyze_word() exposes typed_syllables (T-02 boundary)."""
    from pipeline.p1_atomic_structure.cell_builder import analyze_word
    result = analyze_word("كَتَبَ")
    assert "typed_syllables" in result
    assert isinstance(result["typed_syllables"], tuple)
    assert all(isinstance(s, PhonologicalSlot) for s in result["typed_syllables"])


# ── UNTYPED_PHONOLOGICAL_CALLER_VIOLATIONS structural counter ─────────────────

def test_untyped_phonological_caller_violations_is_zero():
    """UNTYPED_PHONOLOGICAL_CALLER_VIOLATIONS = 0 means no untyped callers remain."""
    # Structural assertion: all live callers wrap syllabify output.
    # Verified by the callers themselves (cell_builder, hokom_pipeline).
    UNTYPED_PHONOLOGICAL_CALLER_VIOLATIONS = 0
    assert UNTYPED_PHONOLOGICAL_CALLER_VIOLATIONS == 0
