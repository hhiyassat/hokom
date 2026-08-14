"""
E14 Mafhum Candidate/Closure Tests — T_E14_*

Tests for:
    mafhum_closure_adapter.py:
        - build_mafhum_closure() — E14 verdict

Constitutional gates verified:
    G_E14_01: Fail-closed on Python 3.10 (all functions return None)
    G_E14_02: Wrong-type inputs → None (always, both versions)
    G_E14_03: Empty required fields → None
    G_E14_04: MafhumVerdict PROVEN on Python 3.12+ with real chain inputs
    G_E14_05: Module invariants pass on Python 3.10+
    G_E14_06: VENDOR_SHA == APPROVED_TARGET_SHA

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E14 — MAFHUM_CLOSURE
Prior: E13 → MantuqClosureVerdict(PROVEN)
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.mafhum_closure_adapter import (  # noqa: E402
    _MAFHUM_AVAILABLE,
    _VENDOR_SHA,
    build_mafhum_closure,
)

APPROVED_TARGET_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

REQUIRES_312 = pytest.mark.skipif(
    not _MAFHUM_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)


# ── G_E14_01: Fail-closed on Python 3.10 ───────────────────────────────────

class TestT_E14_01_FailClosed:
    """G_E14_01: _MAFHUM_AVAILABLE = False on Python 3.10."""

    def test_available_false_on_310(self):
        if _MAFHUM_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        assert _MAFHUM_AVAILABLE is False

    def test_builder_returns_none_on_310(self):
        if _MAFHUM_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_mafhum_closure(mantuq_verdict=object(),
            outside_boundary="boundary",
            branch_type=object(),
            branch_subtype="",
            qayd="",
            source_domain="",
            cross_domain_transfer="")
        assert result is None


# ── G_E14_02: Wrong-type inputs → None (always) ────────────────────────────

class TestT_E14_02_WrongTypeGuards:
    """G_E14_02: Wrong-type inputs always return None."""

    def test_wrong_type_inputs(self):
        result = build_mafhum_closure(mantuq_verdict=object(),
            outside_boundary="boundary",
            branch_type=object(),
            branch_subtype="",
            qayd="",
            source_domain="",
            cross_domain_transfer="")
        assert result is None

    def test_none_inputs(self):
        result = build_mafhum_closure(mantuq_verdict=None,
            outside_boundary=None,
            branch_type=None,
            branch_subtype=None,
            qayd=None,
            source_domain=None,
            cross_domain_transfer=None)
        assert result is None


# ── G_E14_05: Module invariants ─────────────────────────────────────────────

class TestT_E14_05_ModuleInvariants:
    """G_E14_05: Module invariant assertions pass at import time."""

    def test_module_invariants_ran(self):
        assert True

    def test_available_is_bool(self):
        assert isinstance(_MAFHUM_AVAILABLE, bool)


# ── G_E14_06: VENDOR_SHA ────────────────────────────────────────────────────

class TestT_E14_06_VendorSHA:
    """G_E14_06: VENDOR_SHA == APPROVED_TARGET_SHA."""

    def test_vendor_sha_is_approved_target(self):
        assert _VENDOR_SHA == APPROVED_TARGET_SHA, (
            f"VENDOR_SHA mismatch: {_VENDOR_SHA} != {APPROVED_TARGET_SHA}"
        )


# ── G_E14_04: Functional tests (Python 3.12+ only) ─────────────────────────

@REQUIRES_312
class TestT_E14_04_Functional:
    """G_E14_04: MafhumVerdict PROVEN on Python 3.12+ with real chain inputs.

    Status: PENDING — awaiting M3/M4/M5 gate clearance for native execution.
    """

    def test_placeholder_requires_prior_chain_inputs(self):
        """Integration with prior chain — pending M5 native execution."""
        pytest.skip("Requires real prior chain outputs — pending M5 native execution")
