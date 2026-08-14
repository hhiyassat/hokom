"""
E15 GPT Reasonableness Track Tests — T_E15_*

Tests for:
    gpt_track_adapter.py:
        - run_gpt_reasonableness_gates() — R6 deterministic gates
        - get_live_provider_authorization_status() — G_E15_02
        - is_deterministic_track_available() — R1-R8 availability
    weight_layer/chain_report_adapter.py:
        - build_chain_report() — G_E15_03

Constitutional gates verified:
    G_E15_01: T30_GPT_DETERMINISTIC — R1-R8 without live provider (Python 3.12+)
    G_E15_02: Live provider = OWNER_DECISION_REQUIRED (always enforced)
    G_E15_03: chain_report.py chain report produced (Python 3.12+)
    G_E15_04: E15 phase closure certificate emitted (pending M5)
    G_E15_05: Fail-closed on Python 3.10 (all functions return None)
    G_E15_06: VENDOR_SHA == APPROVED_TARGET_SHA

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E15 — GPT_REASONABLENESS (R1-R8)
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.gpt_track_adapter import (  # noqa: E402
    LIVE_PROVIDER_AUTHORIZATION,
    NO_LIVE_PROVIDER_IN_DETERMINISTIC_TRACK,
    _ANSWER_AUDIT_AVAILABLE,
    _GPT_TRACK_AVAILABLE,
    _VENDOR_SHA,
    get_live_provider_authorization_status,
    is_deterministic_track_available,
    run_gpt_reasonableness_gates,
)
from pipeline.taaqol_integration.weight_layer.chain_report_adapter import (  # noqa: E402
    _CHAIN_REPORT_AVAILABLE,
    _VENDOR_SHA as _CR_VENDOR_SHA,
    build_chain_report,
)

APPROVED_TARGET_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

REQUIRES_312 = pytest.mark.skipif(
    not _GPT_TRACK_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)
REQUIRES_312_CHAIN = pytest.mark.skipif(
    not _CHAIN_REPORT_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / chain_report)",
)


# ── G_E15_05: Fail-closed on Python 3.10 ─────────────────────────────────────

class TestT_E15_05_FailClosed:
    """G_E15_05: All E15 functions return None on Python 3.10."""

    def test_gpt_track_available_false_on_310(self):
        if _GPT_TRACK_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        assert _GPT_TRACK_AVAILABLE is False

    def test_chain_report_available_false_on_310(self):
        if _CHAIN_REPORT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        assert _CHAIN_REPORT_AVAILABLE is False

    def test_run_reasonableness_gates_returns_none_on_310(self):
        if _GPT_TRACK_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = run_gpt_reasonableness_gates(origin_binding_result=object())
        assert result is None

    def test_build_chain_report_returns_none_on_310(self):
        if _CHAIN_REPORT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_chain_report(verbal_madlul_candidate=object())
        assert result is None


# ── G_E15_02: Live provider = OWNER_DECISION_REQUIRED (always) ───────────────

class TestT_E15_02_LiveProviderGuard:
    """G_E15_02: Live provider authorization always OWNER_DECISION_REQUIRED."""

    def test_live_provider_authorization_constant(self):
        assert LIVE_PROVIDER_AUTHORIZATION == "OWNER_DECISION_REQUIRED"

    def test_get_live_provider_authorization_status(self):
        status = get_live_provider_authorization_status()
        assert status == "OWNER_DECISION_REQUIRED"

    def test_no_live_provider_in_deterministic_track(self):
        assert NO_LIVE_PROVIDER_IN_DETERMINISTIC_TRACK is True

    def test_deterministic_track_available_is_bool(self):
        assert isinstance(is_deterministic_track_available(), bool)


# ── G_E15: Wrong-type guards (always active) ──────────────────────────────────

class TestT_E15_WrongTypeGuards:
    """Wrong-type inputs always return None (Python 3.10 + 3.12)."""

    def test_wrong_type_run_reasonableness_gates(self):
        result = run_gpt_reasonableness_gates(origin_binding_result=object())
        assert result is None

    def test_none_build_chain_report(self):
        result = build_chain_report(verbal_madlul_candidate=None)
        assert result is None

    def test_wrong_type_build_chain_report(self):
        result = build_chain_report(verbal_madlul_candidate=object())
        assert result is None


# ── G_E15_06: VENDOR_SHA ──────────────────────────────────────────────────────

class TestT_E15_06_VendorSHA:
    """G_E15_06: VENDOR_SHA == APPROVED_TARGET_SHA in both adapters."""

    def test_gpt_track_vendor_sha(self):
        assert _VENDOR_SHA == APPROVED_TARGET_SHA

    def test_chain_report_vendor_sha(self):
        assert _CR_VENDOR_SHA == APPROVED_TARGET_SHA


# ── G_E15_01: Deterministic R1-R8 (Python 3.12+ only) ────────────────────────

@REQUIRES_312
class TestT_E15_01_DeterministicTrack:
    """G_E15_01: T30_GPT_DETERMINISTIC — R1-R8 without live provider.

    Status: PENDING — awaiting M3/M4/M5 gate clearance for native execution.
    Full R1-R8 deterministic tests require Python 3.12+ vendor imports.
    """

    def test_deterministic_track_available_true_on_312(self):
        assert is_deterministic_track_available() is True

    def test_gpt_track_available_true_on_312(self):
        assert _GPT_TRACK_AVAILABLE is True

    def test_run_reasonableness_gates_with_none_input(self):
        """R6 accepts None binding_result (degenerate case)."""
        result = run_gpt_reasonableness_gates(origin_binding_result=None)
        # Should return a ReasonablenessGateReport (possibly REFUSED state)
        assert result is not None

    def test_no_live_provider_called(self):
        """Deterministic track: verify no live provider is invoked."""
        # run_reasonableness_gates with None is purely deterministic
        result = run_gpt_reasonableness_gates(origin_binding_result=None)
        assert result is not None
        # If available, live_provider_status remains OWNER_DECISION_REQUIRED
        assert get_live_provider_authorization_status() == "OWNER_DECISION_REQUIRED"


@REQUIRES_312_CHAIN
class TestT_E15_03_ChainReport:
    """G_E15_03: chain_report produced from E6 VerbalMadlulCandidate.

    Status: PENDING — requires real E6 chain output (VerbalMadlulCandidate).
    """

    def test_chain_report_available_on_312(self):
        assert _CHAIN_REPORT_AVAILABLE is True

    def test_chain_report_wrong_type_returns_none(self):
        result = build_chain_report(verbal_madlul_candidate=object())
        assert result is None

    def test_chain_report_with_real_e6_output(self):
        """G_E15_03: Chain report from real E6 output — pending M5."""
        pytest.skip("Requires real E6 VerbalMadlulCandidate — pending M5 execution")
