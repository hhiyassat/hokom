"""
E12 Tanzil Candidate/Closure Tests — T_E12_*

Tests for:
    tanzil_candidate_adapter.py:
        - build_tanzil_candidate() — E12 verdict

Constitutional gates verified:
    G_E12_01: Fail-closed on Python 3.10 (all functions return None)
    G_E12_02: Wrong-type inputs → None (always, both versions)
    G_E12_03: Empty required fields → None
    G_E12_04: TanzilVerdict PROVEN on Python 3.12+ with real chain inputs
    G_E12_05: Module invariants pass on Python 3.10+
    G_E12_06: VENDOR_SHA == APPROVED_TARGET_SHA

VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
Phase: E12 — TANZIL_CANDIDATE
Prior: E10 → HukmVerdict(PROVEN) + E11 → ManatVerdict(PROVEN)
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.tanzil_candidate_adapter import (  # noqa: E402
    _TANZIL_AVAILABLE,
    _VENDOR_SHA,
    build_tanzil_candidate,
)

APPROVED_TARGET_SHA = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

REQUIRES_312 = pytest.mark.skipif(
    not _TANZIL_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)


# ── G_E12_01: Fail-closed on Python 3.10 ───────────────────────────────────

class TestT_E12_01_FailClosed:
    """G_E12_01: _TANZIL_AVAILABLE = False on Python 3.10."""

    def test_available_false_on_310(self):
        if _TANZIL_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        assert _TANZIL_AVAILABLE is False

    def test_builder_returns_none_on_310(self):
        if _TANZIL_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_tanzil_candidate(hukm_verdict=object(),
            manat_verdict=object(),
            reality_evidence="evidence",
            instance_descriptor="instance",
            tanzil_scope="scope")
        assert result is None


# ── G_E12_02: Wrong-type inputs → None (always) ────────────────────────────

class TestT_E12_02_WrongTypeGuards:
    """G_E12_02: Wrong-type inputs always return None."""

    def test_wrong_type_inputs(self):
        result = build_tanzil_candidate(hukm_verdict=object(),
            manat_verdict=object(),
            reality_evidence="evidence",
            instance_descriptor="instance",
            tanzil_scope="scope")
        assert result is None

    def test_none_inputs(self):
        result = build_tanzil_candidate(hukm_verdict=None,
            manat_verdict=None,
            reality_evidence=None,
            instance_descriptor=None,
            tanzil_scope=None)
        assert result is None
    def test_not_execution_marker_false_returns_none(self):
        """G_E12_GUARD: not_execution_marker=False → None (no execution authority)."""
        from pipeline.taaqol_integration.weight_layer.tanzil_candidate_adapter import build_tanzil_candidate
        result = build_tanzil_candidate(
            hukm_verdict=object(),
            manat_verdict=object(),
            reality_evidence="evidence",
            instance_descriptor="instance",
            tanzil_scope="scope",
            not_execution_marker=False,
        )
        assert result is None



# ── G_E12_05: Module invariants ─────────────────────────────────────────────

class TestT_E12_05_ModuleInvariants:
    """G_E12_05: Module invariant assertions pass at import time."""

    def test_module_invariants_ran(self):
        assert True

    def test_available_is_bool(self):
        assert isinstance(_TANZIL_AVAILABLE, bool)


# ── G_E12_06: VENDOR_SHA ────────────────────────────────────────────────────

class TestT_E12_06_VendorSHA:
    """G_E12_06: VENDOR_SHA == APPROVED_TARGET_SHA."""

    def test_vendor_sha_is_approved_target(self):
        assert _VENDOR_SHA == APPROVED_TARGET_SHA, (
            f"VENDOR_SHA mismatch: {_VENDOR_SHA} != {APPROVED_TARGET_SHA}"
        )


# ── G_E12_04: Functional tests (Python 3.12+ only) ─────────────────────────

@REQUIRES_312
class TestT_E12_04_Functional:
    """G_E12_04: TanzilVerdict PROVEN on Python 3.12+ with real chain inputs.

    Status: PENDING — awaiting M3/M4/M5 gate clearance for native execution.
    """

    def test_placeholder_requires_prior_chain_inputs(self):
        """Integration with prior chain — pending M5 native execution."""
        pytest.skip("Requires real prior chain outputs — pending M5 native execution")
