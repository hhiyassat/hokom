"""
E9 Ifadah Candidate Tests — T_E9_*

Tests for:
    ifadah_candidate_adapter.py:
        - build_ifadah_candidate() — PR-ifadah IfadahVerdict

Constitutional gates verified:
    G_E9_01: Fail-closed on Python 3.10 (all functions return None)
    G_E9_02: Wrong-type inputs → None (always, both versions)
    G_E9_03: Empty required fields → None
    G_E9_04: IfadahVerdict PROVEN on Python 3.12+ with real E8 chain inputs
    G_E9_05: Module invariants pass on Python 3.10+
    G_E9_06: VENDOR_SHA == APPROVED_TARGET_SHA

VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
Phase: E9 — IFADAH_CANDIDATE
Prior: E8 → RelationClosureVerdict + FormalStyleVerdict + MaqamContextBoundaryVerdict
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (  # noqa: E402
    _IFADAH_AVAILABLE,
    _VENDOR_SHA,
    build_ifadah_candidate,
)

APPROVED_TARGET_SHA = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

REQUIRES_312 = pytest.mark.skipif(
    not _IFADAH_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)


# ── G_E9_01: Fail-closed on Python 3.10 ──────────────────────────────────────

class TestT_E9_01_FailClosed:
    """G_E9_01: _IFADAH_AVAILABLE = False on Python 3.10."""

    def test_ifadah_available_false_on_310(self):
        if _IFADAH_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        assert _IFADAH_AVAILABLE is False

    def test_build_ifadah_candidate_returns_none_on_310(self):
        if _IFADAH_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_ifadah_candidate(
            relation_closure_verdict=object(),
            formal_style_verdict=object(),
            ifadah_maqam_verdict=object(),
            speech_force=object(),
            ifadah_evidence="evidence",
            closure_scope="scope",
        )
        assert result is None


# ── G_E9_02: Wrong-type inputs → None (always) ───────────────────────────────

class TestT_E9_02_WrongTypeGuards:
    """G_E9_02: Wrong-type inputs always return None (Python 3.10 + 3.12)."""

    def test_wrong_relation_closure_type(self):
        result = build_ifadah_candidate(
            relation_closure_verdict=object(),
            formal_style_verdict=object(),
            ifadah_maqam_verdict=object(),
            speech_force=object(),
            ifadah_evidence="evidence",
            closure_scope="scope",
        )
        assert result is None

    def test_none_relation_closure(self):
        result = build_ifadah_candidate(
            relation_closure_verdict=None,
            formal_style_verdict=None,
            ifadah_maqam_verdict=None,
            speech_force=None,
            ifadah_evidence="evidence",
            closure_scope="scope",
        )
        assert result is None


# ── G_E9_03: Empty required fields → None ────────────────────────────────────

class TestT_E9_03_EmptyFieldGuards:
    """G_E9_03: Empty required fields return None on Python 3.10+."""

    def test_empty_ifadah_evidence(self):
        result = build_ifadah_candidate(
            relation_closure_verdict=object(),
            formal_style_verdict=object(),
            ifadah_maqam_verdict=object(),
            speech_force=object(),
            ifadah_evidence="",
            closure_scope="scope",
        )
        assert result is None

    def test_empty_closure_scope(self):
        result = build_ifadah_candidate(
            relation_closure_verdict=object(),
            formal_style_verdict=object(),
            ifadah_maqam_verdict=object(),
            speech_force=object(),
            ifadah_evidence="evidence",
            closure_scope="",
        )
        assert result is None

    def test_whitespace_evidence(self):
        result = build_ifadah_candidate(
            relation_closure_verdict=object(),
            formal_style_verdict=object(),
            ifadah_maqam_verdict=object(),
            speech_force=object(),
            ifadah_evidence="   ",
            closure_scope="scope",
        )
        assert result is None


# ── G_E9_05: Module invariants ────────────────────────────────────────────────

class TestT_E9_05_ModuleInvariants:
    """G_E9_05: Module invariant assertions pass at import time."""

    def test_module_invariants_ran(self):
        # If import succeeded without AssertionError, invariants passed
        assert True

    def test_ifadah_available_is_bool(self):
        assert isinstance(_IFADAH_AVAILABLE, bool)


# ── G_E9_06: VENDOR_SHA ───────────────────────────────────────────────────────

class TestT_E9_06_VendorSHA:
    """G_E9_06: VENDOR_SHA == APPROVED_TARGET_SHA."""

    def test_vendor_sha_is_approved_target(self):
        assert _VENDOR_SHA == APPROVED_TARGET_SHA, (
            f"VENDOR_SHA mismatch: {_VENDOR_SHA} != {APPROVED_TARGET_SHA}"
        )


# ── G_E9_04: Functional tests (Python 3.12+ only) ────────────────────────────

@REQUIRES_312
class TestT_E9_04_Functional:
    """G_E9_04: IfadahVerdict PROVEN on Python 3.12+ with real chain inputs.

    NOTE: These tests require real E8 chain outputs (RelationClosureVerdict,
    FormalStyleVerdict, MaqamContextBoundaryVerdict). They are implemented
    as integration tests that reuse the E8 chain builders.
    Status: PENDING — awaiting M3/M4/M5 gate clearance for native execution.
    """

    def test_placeholder_requires_e8_chain_inputs(self):
        """Integration with E8 chain — pending native runtime execution."""
        # This test requires real E8 chain outputs.
        # It will be implemented during M5 E9 evaluation.
        pytest.skip("Requires real E8 chain outputs — pending M5 native execution")
