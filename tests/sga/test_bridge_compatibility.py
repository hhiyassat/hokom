"""
Bridge compatibility tests — ensure live bridge never accepts legacy payloads.
HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-06
"""
import pytest
from pipeline.sga.contracts import HokomClaimBundle, SlotId, SlotState
from pipeline.sga.adapters import build_claim_bundle
from pipeline.sga.bundle_contract import assert_valid_bundle_input


# ── Positive: valid HokomClaimBundle accepted ──────────────────────────────────

def test_valid_bundle_accepted():
    bundle = build_claim_bundle(
        {"word": "كَتَبَ", "segment_host": "كَتَبَ", "word_class": "VERB",
         "root_candidate": "ك-ت-ب", "wazn": "فَعَلَ"},
        "ROOT_CLAIM", "ROOT_CLAIM",
    )
    assert isinstance(bundle, HokomClaimBundle)
    assert_valid_bundle_input(bundle)  # must not raise


def test_functional_owner_bundle_accepted():
    bundle = build_claim_bundle(
        {"word": "مَنْ", "segment_host": "مَنْ", "word_class": "MABNI"},
        "FUNCTIONAL_OWNER_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
    )
    assert isinstance(bundle, HokomClaimBundle)
    assert_valid_bundle_input(bundle)


def test_word_class_bundle_accepted():
    bundle = build_claim_bundle(
        {"word": "اللَّهُ", "segment_host": "اللَّهُ", "word_class": "ISM"},
        "WORD_CLASS_CLAIM", "WORD_CLASS_CLAIM",
    )
    assert isinstance(bundle, HokomClaimBundle)
    assert_valid_bundle_input(bundle)


def test_derivative_bundle_accepted():
    bundle = build_claim_bundle(
        {"word": "كَاتِبٌ", "segment_host": "كَاتِبٌ",
         "word_class": "ISM", "root_candidate": "ك-ت-ب",
         "derivative": "ism_fa3il", "number": "SINGULAR", "gender": "MASCULINE"},
        "DERIVATIVE_CLAIM", "DERIVATIVE_CLAIM",
    )
    assert isinstance(bundle, HokomClaimBundle)
    assert_valid_bundle_input(bundle)


# ── Negative: all forbidden types rejected ─────────────────────────────────────

@pytest.mark.parametrize("bad_input", [
    {"word": "كَتَبَ", "root": "ك-ت-ب"},   # dict
    ("كَتَبَ", "ك-ت-ب"),                      # tuple
    "كَتَبَ",                                  # str
    b"raw bytes",                              # bytes
    ["list"],                                  # list
    42,                                        # int
    None,                                      # None
    3.14,                                      # float
])
def test_forbidden_input_rejected(bad_input):
    with pytest.raises(TypeError):
        assert_valid_bundle_input(bad_input)


# ── Preservation: H11-H15 slots survive through bundle ────────────────────────

def test_h11_h15_slots_present():
    bundle = build_claim_bundle(
        {"word": "ضَارِبٌ", "segment_host": "ضَارِبٌ",
         "word_class": "ISM", "root_candidate": "ض-ر-ب",
         "bab": "نَصَرَ", "masdar": "ضَرْبٌ", "derivative": "ism_fa3il",
         "number": "SINGULAR", "gender": "MASCULINE"},
        "DERIVATIVE_CLAIM", "DERIVATIVE_CLAIM",
    )
    slot_ids = {s.slot_id for s in bundle.typed_slots}
    assert SlotId.BAB_CANDIDATE_SET in slot_ids
    assert SlotId.MASDAR_CANDIDATE_SET in slot_ids
    assert SlotId.DERIVATIVE_CANDIDATE_SET in slot_ids
    assert SlotId.NUMBER_SLOT in slot_ids
    assert SlotId.GENDER_SLOT in slot_ids


def test_bab_slot_filled_when_provided():
    bundle = build_claim_bundle(
        {"word": "نَصَرَ", "segment_host": "نَصَرَ",
         "word_class": "VERB", "bab": "نَصَرَ"},
        "BAB_CLAIM", "BAB_CLAIM",
    )
    bab_slot = next((s for s in bundle.typed_slots if s.slot_id == SlotId.BAB_CANDIDATE_SET), None)
    assert bab_slot is not None
    assert bab_slot.state == SlotState.FILLED


# ── Ambiguity preservation ──────────────────────────────────────────────────────

def test_ambiguous_root_preserved():
    bundle = build_claim_bundle(
        {"word": "وَجَدَ", "segment_host": "وَجَدَ",
         "root_candidate": ["و-ج-د", "ج-ي-د"]},
        "ROOT_CLAIM", "ROOT_CLAIM",
    )
    # R1/R2/R3 must be UNKNOWN when ambiguous
    r1 = next((s for s in bundle.typed_slots if s.slot_id == SlotId.RADICAL_R1), None)
    assert r1 is not None
    assert r1.state == SlotState.UNKNOWN, "R1 must be UNKNOWN for ambiguous root (T-10)"

    # ROOT_CANDIDATE_SET must be in candidate_sets
    assert SlotId.ROOT_CANDIDATE_SET.value in bundle.candidate_sets, \
        "ROOT_CANDIDATE_SET must be preserved in candidate_sets"
    cset = bundle.candidate_sets[SlotId.ROOT_CANDIDATE_SET.value]
    assert cset.selected is None, "selected must be None for AMBIGUOUS root (T-10)"
    assert len(cset.candidates) == 2, "Both root candidates must be preserved"


def test_ambiguous_selected_is_always_none():
    """No AMBIGUOUS slot should have selected != None."""
    bundle = build_claim_bundle(
        {"word": "وَجَدَ", "segment_host": "وَجَدَ",
         "root_candidate": ["و-ج-د", "ج-ي-د"],
         "bab": ["نَصَرَ", "ضَرَبَ"],
         "masdar": ["وُجُودٌ", "وَجْدٌ"]},
        "ROOT_CLAIM", "ROOT_CLAIM",
    )
    for slot in bundle.typed_slots:
        if slot.state == SlotState.AMBIGUOUS:
            assert slot.candidate_set is not None
            assert slot.candidate_set.selected is None, \
                f"AMBIGUOUS slot {slot.slot_id} has non-None selected (AMBIGUITY_COLLAPSE)"


# ── claim_key determinism ─────────────────────────────────────────────────────

def test_claim_key_deterministic():
    result = {"word": "كَتَبَ", "segment_host": "كَتَبَ", "root_candidate": "ك-ت-ب"}
    b1 = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    b2 = build_claim_bundle(result, "ROOT_CLAIM", "ROOT_CLAIM")
    assert b1.claim_key == b2.claim_key


def test_claim_key_is_64_hex_chars():
    bundle = build_claim_bundle(
        {"word": "كَتَبَ", "segment_host": "كَتَبَ"},
        "ROOT_CLAIM", "ROOT_CLAIM",
    )
    assert len(bundle.claim_key) == 64
    int(bundle.claim_key, 16)  # must be valid hex


# ── Residual preservation ─────────────────────────────────────────────────────

def test_residuals_not_dropped():
    bundle = build_claim_bundle(
        {"word": "رَبَّهُ", "segment_host": "رَبَّ",
         "enclitics": ["هُ"], "word_class": "VERB"},
        "ROOT_CLAIM", "ROOT_CLAIM",
    )
    enc_slot = next((s for s in bundle.typed_slots if s.slot_id == SlotId.ENCLITIC_SLOTS), None)
    assert enc_slot is not None, "ENCLITIC_SLOTS must not be dropped"


def test_proclitic_not_dropped():
    bundle = build_claim_bundle(
        {"word": "وَكَتَبَ", "segment_host": "كَتَبَ",
         "proclitics": ["وَ"], "word_class": "VERB"},
        "ROOT_CLAIM", "ROOT_CLAIM",
    )
    proc_slot = next((s for s in bundle.typed_slots if s.slot_id == SlotId.PROCLITIC_SLOTS), None)
    assert proc_slot is not None
    assert proc_slot.state == SlotState.FILLED


# ── Provenance survival ───────────────────────────────────────────────────────

def test_original_surface_preserved():
    original = "وَاللَّهُ"
    bundle = build_claim_bundle(
        {"word": original, "segment_host": "اللَّهُ"},
        "WORD_CLASS_CLAIM", "WORD_CLASS_CLAIM",
    )
    assert bundle.surface.original_surface == original


def test_original_surface_never_replaced_by_normalized():
    original = "وَاللَّهُ"
    bundle = build_claim_bundle(
        {"word": original, "segment_host": "اللَّهُ",
         "normalized_surface": "اللَّهُ"},
        "WORD_CLASS_CLAIM", "WORD_CLASS_CLAIM",
    )
    assert bundle.surface.original_surface == original


# ── No silent fallback ────────────────────────────────────────────────────────

def test_evaluate_sga_bundle_rejects_dict():
    """evaluate_sga_bundle() must return DEFERRED (not raise) for dict input."""
    from pipeline.taaqol_integration.live.bridge import evaluate_sga_bundle
    result = evaluate_sga_bundle({"word": "كَتَبَ"})
    # Bridge returns DEFERRED with OPAQUE_BRIDGE_INPUT, never raises silently
    assert result is not None
    # Effective verdict must not be LICENSED for opaque input
    assert result.effective_verdict != "LICENSED", \
        "evaluate_sga_bundle must not return LICENSED for dict input"
    # Must contain OPAQUE marker in reason_codes or effective_verdict
    reason_str = str(result.reason_codes)
    assert "OPAQUE" in reason_str or result.effective_verdict == "DEFERRED", \
        f"No OPAQUE marker in reason_codes for dict input: {result.reason_codes}"


def test_evaluate_sga_bundle_rejects_string():
    from pipeline.taaqol_integration.live.bridge import evaluate_sga_bundle
    result = evaluate_sga_bundle("كَتَبَ")
    assert result is not None
    assert result.effective_verdict != "LICENSED"


# ── Bundle is a dataclass with expected fields ────────────────────────────────

def test_bundle_has_required_fields():
    bundle = build_claim_bundle(
        {"word": "كَتَبَ", "segment_host": "كَتَبَ"},
        "ROOT_CLAIM", "ROOT_CLAIM",
    )
    assert hasattr(bundle, 'claim_key')
    assert hasattr(bundle, 'claim_kind')
    assert hasattr(bundle, 'profile_id')
    assert hasattr(bundle, 'surface')
    assert hasattr(bundle, 'typed_slots')
    assert hasattr(bundle, 'candidate_sets')
    assert hasattr(bundle, 'evidence_refs')
    assert hasattr(bundle, 'residuals')
    assert hasattr(bundle, 'domain_licenses')


# ── Closed boundary tokens ────────────────────────────────────────────────────

def test_closed_boundary_blocks_root_path():
    bundle = build_claim_bundle(
        {"word": "مَنْ", "segment_host": "مَنْ", "word_class": "MABNI"},
        "FUNCTIONAL_OWNER_CLAIM", "FUNCTIONAL_OWNER_CLAIM",
    )
    path_slot = next((s for s in bundle.typed_slots if s.slot_id == SlotId.PATH_DIRECTIVE_SLOT), None)
    assert path_slot is not None
    # MABNI word class should result in BLOCKED path
    assert path_slot.state == SlotState.BLOCKED, \
        f"MABNI token should have BLOCKED path, got {path_slot.state}"

    # obstacle_facts should record the closed boundary
    assert any("CLOSED_BOUNDARY" in str(f) for f in bundle.obstacle_facts), \
        "CLOSED_BOUNDARY must be in obstacle_facts for MABNI token"
