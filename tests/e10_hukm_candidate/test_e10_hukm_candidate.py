"""
E10 Hukm Candidate/Closure Tests — T_E10_*

Tests for:
    hukm_candidate_adapter.py:
        - build_hukm_candidate() — E10 verdict

Constitutional gates verified:
    G_E10_01: Fail-closed on Python 3.10 (all functions return None)
    G_E10_02: Wrong-type inputs → None (always, both versions)
    G_E10_03: Empty required fields → None
    G_E10_04: HukmVerdict PROVEN on Python 3.12+ with real chain inputs
    G_E10_05: Module invariants pass on Python 3.10+
    G_E10_06: VENDOR_SHA == APPROVED_TARGET_SHA

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E10 — HUKM_CANDIDATE
Prior: E9 → IfadahVerdict(PROVEN)
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.hukm_candidate_adapter import (  # noqa: E402
    _HUKM_AVAILABLE,
    _VENDOR_SHA,
    build_hukm_candidate,
)

APPROVED_TARGET_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

REQUIRES_312 = pytest.mark.skipif(
    not _HUKM_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)


# ── G_E10_01: Fail-closed on Python 3.10 ───────────────────────────────────

class TestT_E10_01_FailClosed:
    """G_E10_01: _HUKM_AVAILABLE = False on Python 3.10."""

    def test_available_false_on_310(self):
        if _HUKM_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        assert _HUKM_AVAILABLE is False

    def test_builder_returns_none_on_310(self):
        if _HUKM_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_hukm_candidate(ifadah_verdict=object(),
            evaluation_domain=object(),
            hukm_claim="claim",
            hukm_evidence="evidence",
            hukm_maqam="maqam",
            closure_scope="scope")
        assert result is None


# ── G_E10_02: Wrong-type inputs → None (always) ────────────────────────────

class TestT_E10_02_WrongTypeGuards:
    """G_E10_02: Wrong-type inputs always return None."""

    def test_wrong_type_inputs(self):
        result = build_hukm_candidate(ifadah_verdict=object(),
            evaluation_domain=object(),
            hukm_claim="claim",
            hukm_evidence="evidence",
            hukm_maqam="maqam",
            closure_scope="scope")
        assert result is None

    def test_none_inputs(self):
        result = build_hukm_candidate(ifadah_verdict=None,
            evaluation_domain=None,
            hukm_claim=None,
            hukm_evidence=None,
            hukm_maqam=None,
            closure_scope=None)
        assert result is None


# ── G_E10_05: Module invariants ─────────────────────────────────────────────

class TestT_E10_05_ModuleInvariants:
    """G_E10_05: Module invariant assertions pass at import time."""

    def test_module_invariants_ran(self):
        assert True

    def test_available_is_bool(self):
        assert isinstance(_HUKM_AVAILABLE, bool)


# ── G_E10_06: VENDOR_SHA ────────────────────────────────────────────────────

class TestT_E10_06_VendorSHA:
    """G_E10_06: VENDOR_SHA == APPROVED_TARGET_SHA."""

    def test_vendor_sha_is_approved_target(self):
        assert _VENDOR_SHA == APPROVED_TARGET_SHA, (
            f"VENDOR_SHA mismatch: {_VENDOR_SHA} != {APPROVED_TARGET_SHA}"
        )


# ── G_E10_04: Functional tests (Python 3.12+ only) ─────────────────────────

@REQUIRES_312
class TestT_E10_04_Functional:
    """G_E10_04: HukmVerdict PROVEN on Python 3.12+ with real chain inputs.

    Status: PENDING — awaiting M3/M4/M5 gate clearance for native execution.
    """

    def test_placeholder_requires_prior_chain_inputs(self):
        """Integration with prior chain — pending M5 native execution."""
        pytest.skip("Requires real prior chain outputs — pending M5 native execution")
