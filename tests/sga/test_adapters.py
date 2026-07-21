"""
Tests for pipeline/sga/adapters.py — H0-H10 surface-to-boundary adapters.
"""
import pytest
from pipeline.sga.adapters import (
    adapt_surface_identity,
    adapt_segmentation,
    adapt_article,
    adapt_boundary,
    adapt_word_class,
    adapt_root_radicals,
    adapt_pattern,
    build_claim_bundle,
)
from pipeline.sga.contracts import SlotId, SlotSort, SlotState, BoundaryType


# ── adapt_surface_identity ────────────────────────────────────────────────────

def test_adapt_surface_identity_preserves_original():
    result = {"original_surface": "كَتَبَ", "normalized_surface": "كتب"}
    orig, norm, prov = adapt_surface_identity(result)
    assert orig.value == "كَتَبَ"
    assert orig.slot_id == SlotId.ORIGINAL_SURFACE
    assert orig.state == SlotState.FILLED


def test_adapt_surface_identity_fallback_to_word():
    result = {"word": "مَنْ"}
    orig, norm, prov = adapt_surface_identity(result)
    assert orig.value == "مَنْ"
    assert prov.original_surface == "مَنْ"


def test_adapt_surface_identity_normalized_falls_back_to_original():
    result = {"original_surface": "كَتَبَ"}
    orig, norm, prov = adapt_surface_identity(result)
    # normalized should fall back to original when not provided
    assert norm.value == "كَتَبَ"


def test_adapt_surface_identity_empty_surface():
    result = {}
    orig, norm, prov = adapt_surface_identity(result)
    assert orig.state == SlotState.UNKNOWN
    assert orig.value is None


# ── adapt_boundary ────────────────────────────────────────────────────────────

def test_adapt_boundary_operator_gives_blocked_path():
    result = {"word_class": "OPERATOR"}
    boundary_slot, path_slot = adapt_boundary(result)
    assert path_slot.state == SlotState.BLOCKED
    assert path_slot.value == "ROOT_PATH_BLOCKED"
    assert boundary_slot.value == BoundaryType.OPERATOR_BOUNDARY.value


def test_adapt_boundary_mabni_gives_blocked_path():
    result = {"word_class": "MABNI"}
    boundary_slot, path_slot = adapt_boundary(result)
    assert path_slot.state == SlotState.BLOCKED
    assert boundary_slot.value == BoundaryType.MABNI_BOUNDARY.value


def test_adapt_boundary_explicit_operator_boundary():
    result = {"boundary_type": "OPERATOR_BOUNDARY"}
    boundary_slot, path_slot = adapt_boundary(result)
    assert path_slot.state == SlotState.BLOCKED
    assert boundary_slot.value == "OPERATOR_BOUNDARY"


def test_adapt_boundary_open_morphology_gives_filled_path():
    result = {"word_class": "FI3L"}
    boundary_slot, path_slot = adapt_boundary(result)
    assert path_slot.state == SlotState.FILLED
    assert path_slot.value == "OPEN_MORPHOLOGY"
    assert boundary_slot.state == SlotState.NOT_APPLICABLE


def test_adapt_boundary_no_word_class_gives_open_path():
    result = {}
    boundary_slot, path_slot = adapt_boundary(result)
    assert path_slot.state == SlotState.FILLED
    assert path_slot.value == "OPEN_MORPHOLOGY"


# ── adapt_root_radicals ───────────────────────────────────────────────────────

def test_adapt_root_radicals_dash_separated():
    result = {"root_candidate": "ك-ت-ب"}
    r1, r2, r3, r4 = adapt_root_radicals(result)
    assert r1.value == "ك"
    assert r1.slot_id == SlotId.RADICAL_R1
    assert r2.value == "ت"
    assert r2.slot_id == SlotId.RADICAL_R2
    assert r3.value == "ب"
    assert r3.slot_id == SlotId.RADICAL_R3
    assert r4.state == SlotState.NOT_APPLICABLE
    assert r4.value is None


def test_adapt_root_radicals_space_separated():
    result = {"root_candidate": "ك ت ب"}
    r1, r2, r3, r4 = adapt_root_radicals(result)
    assert r1.value == "ك"
    assert r2.value == "ت"
    assert r3.value == "ب"
    assert r4.state == SlotState.NOT_APPLICABLE


def test_adapt_root_radicals_concatenated():
    result = {"root_candidate": "كتب"}
    r1, r2, r3, r4 = adapt_root_radicals(result)
    assert r1.value == "ك"
    assert r2.value == "ت"
    assert r3.value == "ب"
    assert r4.state == SlotState.NOT_APPLICABLE


def test_adapt_root_radicals_no_root_all_unknown():
    result = {}
    r1, r2, r3, r4 = adapt_root_radicals(result)
    assert r1.state == SlotState.UNKNOWN
    assert r2.state == SlotState.UNKNOWN
    assert r3.state == SlotState.UNKNOWN
    assert r4.state == SlotState.UNKNOWN
    assert r1.value is None


def test_adapt_root_radicals_quadrilateral():
    result = {"root_candidate": "د-ح-ر-ج"}
    r1, r2, r3, r4 = adapt_root_radicals(result)
    assert r1.value == "د"
    assert r4.value == "ج"
    assert r4.state == SlotState.FILLED


def test_adapt_root_radicals_evidence_attached():
    result = {"root_candidate": "ك-ت-ب"}
    r1, r2, r3, r4 = adapt_root_radicals(result)
    assert len(r1.evidence) == 1
    assert r1.evidence[0].kind == "MORPHOLOGICAL"
    assert "ك-ت-ب" in r1.evidence[0].evidence_id


# ── build_claim_bundle ────────────────────────────────────────────────────────

def test_build_claim_bundle_deterministic():
    result = {
        "original_surface": "كَتَبَ",
        "root_candidate": "ك-ت-ب",
        "word_class": "FI3L",
        "wazn": "فَعَلَ",
    }
    b1 = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    b2 = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    assert b1.claim_key == b2.claim_key


def test_build_claim_bundle_different_input_different_key():
    r1 = {
        "original_surface": "كَتَبَ",
        "root_candidate": "ك-ت-ب",
    }
    r2 = {
        "original_surface": "ضَرَبَ",
        "root_candidate": "ض-ر-ب",
    }
    b1 = build_claim_bundle(r1, "ROOT_CLAIM", "ROOT_CLAIM")
    b2 = build_claim_bundle(r2, "ROOT_CLAIM", "ROOT_CLAIM")
    assert b1.claim_key != b2.claim_key


def test_build_claim_bundle_obstacle_for_closed_boundary():
    result = {
        "original_surface": "مَنْ",
        "word_class": "OPERATOR",
    }
    bundle = build_claim_bundle(result, "WORD_CLASS_CLAIM", "WORD_CLASS_CLAIM")
    assert len(bundle.obstacle_facts) > 0
    assert any("CLOSED_BOUNDARY" in f for f in bundle.obstacle_facts)


def test_build_claim_bundle_no_obstacle_for_open_morphology():
    result = {
        "original_surface": "كَتَبَ",
        "word_class": "FI3L",
        "root_candidate": "ك-ت-ب",
    }
    bundle = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    assert len(bundle.obstacle_facts) == 0


def test_build_claim_bundle_slots_sorted_by_sort_order():
    result = {
        "original_surface": "كَتَبَ",
        "root_candidate": "ك-ت-ب",
        "word_class": "FI3L",
    }
    bundle = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    sort_values = [s.sort.value for s in bundle.typed_slots]
    assert sort_values == sorted(sort_values), (
        f"Slots not in sort order: {sort_values}"
    )


def test_build_claim_bundle_surface_preserved():
    result = {"original_surface": "اسْتَغْفَرَ"}
    bundle = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    assert bundle.surface.original_surface == "اسْتَغْفَرَ"


def test_build_claim_bundle_contains_15_slots():
    result = {
        "original_surface": "كَتَبَ",
        "root_candidate": "ك-ت-ب",
        "word_class": "FI3L",
        "wazn": "فَعَلَ",
    }
    bundle = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    # 2 surface + 3 segmentation + 2 article + 2 boundary + 1 word_class + 4 radicals + 1 pattern
    assert len(bundle.typed_slots) == 15
