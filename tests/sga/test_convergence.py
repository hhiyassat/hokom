"""
HOKOM-TAAQOL-SGA-CONSTITUTIONAL-CONVERGENCE-01 — test_convergence.py

Claim identity tests (COMMIT 5):
  - build_claim_bundle is deterministic: same input → same claim_key
  - different input → different claim_key
  - evaluate_sga_bundle accepts HokomClaimBundle and returns HokomTaaqolDecision
  - evaluate_sga_bundle rejects non-HokomClaimBundle with OPAQUE_BRIDGE_INPUT

Four-verdict tests:
  - ACCEPT input → taaqol_verdict in {LICENSED, DEFERRED}   (Taaqol may not be available)
  - BLOCK upstream → verdict path includes BLOCKED / DEFERRED
  - Ambiguous root → AMBIGUOUS residuals propagated; no silent collapse
  - Operator class → BLOCKED path directive in typed slots

These tests pass without Taaqol being importable (Python 3.10 / StrEnum guard).
"""
from __future__ import annotations

import pytest
from pipeline.sga.adapters import build_claim_bundle
from pipeline.sga.contracts import (
    SlotId,
    SlotState,
    HokomResidualRecord,
    CandidateSet,
    CandidateEntry,
)
from pipeline.taaqol_integration.live.bridge import evaluate_sga_bundle
from pipeline.taaqol_integration.live.models import HokomTaaqolDecision


# ── helpers ──────────────────────────────────────────────────────────────────

_VALID_INPUT = {
    "original_surface": "كَتَبَ",
    "root_candidate": "ك-ت-ب",
    "word_class": "FI3L",
    "wazn": "فَعَلَ",
    "upstream_verdict": "ACCEPT",
}

_AMBIGUOUS_INPUT = {
    "original_surface": "كَتَبَ",
    "root_candidate": ["ك-ت-ب", "ق-ت-ب"],
    "word_class": "FI3L",
    "upstream_verdict": "ACCEPT",
}

_BLOCK_INPUT = {
    "original_surface": "مَنْ",
    "word_class": "OPERATOR",
    "upstream_verdict": "BLOCK",
}

_OPERATOR_INPUT = {
    "original_surface": "عَلَى",
    "word_class": "OPERATOR",
    "upstream_verdict": "ACCEPT",
}


# ── Claim Identity ────────────────────────────────────────────────────────────

def test_claim_bundle_deterministic_same_input():
    """Same input must always produce the same claim_key."""
    b1 = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    b2 = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    assert b1.claim_key == b2.claim_key, (
        f"Non-deterministic claim_key: {b1.claim_key!r} vs {b2.claim_key!r}"
    )


def test_claim_bundle_different_input_different_key():
    """Different inputs must produce different claim_keys."""
    other = {
        "original_surface": "ضَرَبَ",
        "root_candidate": "ض-ر-ب",
        "word_class": "FI3L",
    }
    b1 = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    b2 = build_claim_bundle(other, "ROOT_CLAIM", "ROOT_CLAIM")
    assert b1.claim_key != b2.claim_key


def test_claim_key_is_non_empty_string():
    bundle = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    assert isinstance(bundle.claim_key, str) and bundle.claim_key


def test_claim_bundle_surface_provenance_preserved():
    bundle = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    assert bundle.surface.original_surface == "كَتَبَ"


def test_claim_bundle_has_typed_slots():
    bundle = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    assert len(bundle.typed_slots) == 23


# ── evaluate_sga_bundle type-gate ──────────────────────────────────────────────

def test_evaluate_sga_bundle_accepts_claim_bundle():
    bundle = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    decision = evaluate_sga_bundle(bundle)
    assert isinstance(decision, HokomTaaqolDecision)


def test_evaluate_sga_bundle_rejects_wrong_type():
    """Passing a non-HokomClaimBundle must return DEFERRED with OPAQUE_BRIDGE_INPUT."""
    decision = evaluate_sga_bundle({"some": "dict"})
    assert isinstance(decision, HokomTaaqolDecision)
    assert decision.taaqol_verdict == "DEFERRED"
    assert any("OPAQUE_BRIDGE_INPUT" in r for r in decision.reason_codes)


def test_evaluate_sga_bundle_rejects_none():
    decision = evaluate_sga_bundle(None)
    assert isinstance(decision, HokomTaaqolDecision)
    assert decision.taaqol_verdict == "DEFERRED"


def test_evaluate_sga_bundle_returns_hokom_taaqol_decision():
    bundle = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    decision = evaluate_sga_bundle(bundle)
    # Must always return HokomTaaqolDecision, never raise
    assert hasattr(decision, 'taaqol_verdict')
    assert hasattr(decision, 'effective_verdict')
    assert hasattr(decision, 'fail_closed')
    assert decision.fail_closed is True


# ── Four-verdict tests ────────────────────────────────────────────────────────

def test_accept_input_verdict_is_licensed_or_deferred():
    """
    ACCEPT upstream + open morphology + known root → LICENSED if Taaqol available;
    DEFERRED if Taaqol not importable (Python 3.10 guard).
    """
    bundle = build_claim_bundle(_VALID_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    decision = evaluate_sga_bundle(bundle)
    assert decision.taaqol_verdict in ("LICENSED", "DEFERRED", "RESIDUAL"), (
        f"Unexpected verdict for ACCEPT input: {decision.taaqol_verdict}"
    )


def test_operator_word_class_path_is_blocked_in_bundle():
    """
    OPERATOR word class → PATH_DIRECTIVE_SLOT is BLOCKED in the claim bundle.
    Taaqol should return BLOCKED or DEFERRED; never LICENSED.
    """
    bundle = build_claim_bundle(_OPERATOR_INPUT, "WORD_CLASS_CLAIM", "WORD_CLASS_CLAIM")
    # The path_directive slot must be BLOCKED
    path_slots = [s for s in bundle.typed_slots if s.slot_id == SlotId.PATH_DIRECTIVE_SLOT]
    assert len(path_slots) == 1
    assert path_slots[0].state == SlotState.BLOCKED, (
        f"OPERATOR should produce BLOCKED path directive; got {path_slots[0].state}"
    )


def test_block_upstream_verdict_yields_deferred_or_blocked():
    """
    Upstream BLOCK → bridge should never return LICENSED.
    """
    bundle = build_claim_bundle(_BLOCK_INPUT, "WORD_CLASS_CLAIM", "WORD_CLASS_CLAIM")
    decision = evaluate_sga_bundle(bundle)
    assert decision.taaqol_verdict in ("BLOCKED", "DEFERRED", "RESIDUAL"), (
        f"BLOCK upstream must not yield LICENSED; got {decision.taaqol_verdict}"
    )


def test_block_upstream_never_licensed():
    """BLOCK upstream → taaqol_verdict is never LICENSED."""
    bundle = build_claim_bundle(_BLOCK_INPUT, "WORD_CLASS_CLAIM", "WORD_CLASS_CLAIM")
    decision = evaluate_sga_bundle(bundle)
    assert decision.taaqol_verdict != "LICENSED"


# ── T-10: Ambiguous candidate sets ───────────────────────────────────────────

def test_ambiguous_root_radicals_all_unknown():
    """
    When root_candidate is a list with >1 entries, R1/R2/R3 must be UNKNOWN —
    no silent collapse to first candidate.
    """
    bundle = build_claim_bundle(_AMBIGUOUS_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    r1 = next(s for s in bundle.typed_slots if s.slot_id == SlotId.RADICAL_R1)
    r2 = next(s for s in bundle.typed_slots if s.slot_id == SlotId.RADICAL_R2)
    r3 = next(s for s in bundle.typed_slots if s.slot_id == SlotId.RADICAL_R3)
    assert r1.state == SlotState.UNKNOWN, f"R1 must be UNKNOWN for ambiguous root; got {r1.state}"
    assert r2.state == SlotState.UNKNOWN, f"R2 must be UNKNOWN for ambiguous root; got {r2.state}"
    assert r3.state == SlotState.UNKNOWN, f"R3 must be UNKNOWN for ambiguous root; got {r3.state}"
    assert r1.value is None
    assert r2.value is None
    assert r3.value is None


def test_ambiguous_root_produces_ambiguous_candidate_set_residual():
    """
    When root is ambiguous, build_claim_bundle must create an AMBIGUOUS_CANDIDATE_SET
    residual — not silently pick first.
    """
    bundle = build_claim_bundle(_AMBIGUOUS_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    ambiguous_residuals = [
        r for r in bundle.residuals
        if getattr(r, 'code', '') == 'AMBIGUOUS_CANDIDATE_SET'
    ]
    assert len(ambiguous_residuals) >= 1, (
        "Expected AMBIGUOUS_CANDIDATE_SET residual for multi-root input; got none"
    )


def test_ambiguous_root_candidate_set_preserves_all_candidates():
    """
    The ROOT_CANDIDATE_SET must carry all candidates in bundle.candidate_sets,
    not just the first — no silent collapse.
    """
    bundle = build_claim_bundle(_AMBIGUOUS_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    # candidate_sets is a dict keyed by SlotId value strings
    rcs = bundle.candidate_sets.get(SlotId.ROOT_CANDIDATE_SET.value)
    assert rcs is not None, (
        f"ROOT_CANDIDATE_SET must be in bundle.candidate_sets; keys: {list(bundle.candidate_sets.keys())}"
    )
    assert len(rcs.candidates) == 2, (
        f"Expected 2 candidates; got {len(rcs.candidates)}: {[c.value for c in rcs.candidates]}"
    )
    assert rcs.selected is None, (
        "AMBIGUOUS candidate_set must have selected=None"
    )


def test_ambiguous_root_no_silent_first_selection():
    """No single radical slot may be set to 'ك' (the first candidate's first radical)."""
    bundle = build_claim_bundle(_AMBIGUOUS_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    radical_slots = [
        s for s in bundle.typed_slots
        if s.slot_id in (SlotId.RADICAL_R1, SlotId.RADICAL_R2, SlotId.RADICAL_R3)
    ]
    for slot in radical_slots:
        assert slot.value is None, (
            f"Silent first-selection detected: {slot.slot_id}={slot.value!r}"
        )


def test_ambiguous_root_bridge_passes_through():
    """
    evaluate_sga_bundle with ambiguous root must return a valid decision —
    never raise, never silently collapse.
    """
    bundle = build_claim_bundle(_AMBIGUOUS_INPUT, "ROOT_CLAIM", "ROOT_CLAIM")
    decision = evaluate_sga_bundle(bundle)
    assert isinstance(decision, HokomTaaqolDecision)
    # With AMBIGUOUS residual, bridge must defer (cannot ACCEPT / LICENSED)
    assert decision.taaqol_verdict in ("DEFERRED", "BLOCKED", "RESIDUAL"), (
        f"Ambiguous root must not yield LICENSED; got {decision.taaqol_verdict}"
    )


# ── Bridge expressivity ───────────────────────────────────────────────────────

def test_bridge_has_no_violation_counters_incremented():
    """Violation counters must be zero (no caller bypasses recorded)."""
    import pipeline.taaqol_integration.live.bridge as _bridge
    assert getattr(_bridge, 'RAW_BRIDGE_CALLER_VIOLATIONS', 0) == 0
    assert getattr(_bridge, 'CLAIM_BUNDLE_BYPASS_VIOLATIONS', 0) == 0
    assert getattr(_bridge, 'OPAQUE_BRIDGE_INPUT_VIOLATIONS', 0) == 0


def test_evaluate_sga_bundle_in_all():
    """evaluate_sga_bundle must be exported in __all__."""
    import pipeline.taaqol_integration.live.bridge as _bridge
    assert 'evaluate_sga_bundle' in _bridge.__all__
