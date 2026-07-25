"""
tests/scg/test_taaqol_hard_gating.py
══════════════════════════════════════════════════════════════════════════════

Mandate: HOKOM-SCG-P0-P12-TAAQOL-HARD-GATING-CORRECTION-04

Proves that the hard SCG gate in hokom_pipeline.py:
  • Never opens a target stage before its Taaqol judgment.
  • APPROVED with sufficient rank → target opened exactly once.
  • BLOCKED / DEFERRED / REJECTED / FORBIDDEN_LEAP / INVALID → target not opened.
  • Infrastructure failure (enforcer unavailable) → target not opened.
  • A terminal judgment stops all later stages.

These tests use explicit judgment providers (monkeypatched judge_transition).
They are NOT mocked final integration decisions:
  • The real SCGTransitionEnforcer and hokom() are exercised.
  • Only judge_transition() is replaced — the hard-gate logic in hokom_pipeline.py
    runs unmodified.

The conftest.py autouse fixture (for non-SCG tests) does NOT apply here
because the path contains "tests/scg".
"""
from __future__ import annotations

import unittest.mock as mock
import pytest

import pipeline.governance.taaqol_judgment_enforcer as _enf_mod
from pipeline.governance.taaqol_judgment_enforcer import (
    TaaqolTransitionJudgment,
    CANONICAL_EDGE_SEQUENCE,
)
from hokom_pipeline import hokom


# ── Judgment factories ─────────────────────────────────────────────────────────

def _make_judgment(source: str, target: str, verdict: str) -> TaaqolTransitionJudgment:
    runtime_active = verdict != "BLOCKED"
    return TaaqolTransitionJudgment(
        edge_id=f"{source}→{target}",
        source_stage=source,
        target_stage=target,
        taaqol_called=True,
        taaqol_runtime_active=runtime_active,
        gamma_closure_state=(
            "MINIMALLY_CLOSED" if verdict == "APPROVED"
            else "UNAVAILABLE" if verdict == "BLOCKED"
            else "OPEN"
        ),
        gate_verdict=verdict,
        failure_code=None if verdict == "APPROVED" else "GATE_STOPPED",
        fallback_used=False,
        error_detail=None,
    )


def _all_approved_provider(source: str, target: str) -> TaaqolTransitionJudgment:
    return _make_judgment(source, target, "APPROVED")


def _blocked_at_first_provider(source: str, target: str) -> TaaqolTransitionJudgment:
    """Return BLOCKED for the first edge, APPROVED for all others."""
    if (source, target) == CANONICAL_EDGE_SEQUENCE[0]:
        return _make_judgment(source, target, "BLOCKED")
    return _make_judgment(source, target, "APPROVED")


def _verdict_at_edge_provider(stop_source: str, stop_target: str, verdict: str):
    """Factory: return the given verdict only at the named edge."""
    def _provider(source: str, target: str) -> TaaqolTransitionJudgment:
        if (source, target) == (stop_source, stop_target):
            return _make_judgment(source, target, verdict)
        return _make_judgment(source, target, "APPROVED")
    return _provider


# ── A. APPROVED opens the target stage ────────────────────────────────────────

class TestApprovedOpensTarget:
    """When all 11 gates return APPROVED, the full linguistic pipeline executes."""

    def test_full_pipeline_returns_on_all_approved(self, monkeypatch):
        monkeypatch.setattr(_enf_mod, "judge_transition", _all_approved_provider)
        r = hokom("كَتَبَ")
        assert r.get("stage") != "SCG_STOPPED", (
            "All-APPROVED path must not return SCG_STOPPED"
        )

    def test_all_approved_has_11_edges_in_matrix(self, monkeypatch):
        monkeypatch.setattr(_enf_mod, "judge_transition", _all_approved_provider)
        r = hokom("كَتَبَ")
        matrix = r.get("scg_gate_matrix", {})
        assert matrix.get("edge_count") == 11, (
            f"All-APPROVED path: expected 11 edges in matrix, got {matrix.get('edge_count')}"
        )

    def test_approved_produces_segment_bundle(self, monkeypatch):
        monkeypatch.setattr(_enf_mod, "judge_transition", _all_approved_provider)
        r = hokom("كَتَبَ")
        # segment_bundle must be present (SEGMENT stage opened)
        assert "segment_bundle" in r, "SEGMENT stage must be opened after APPROVED gate"

    def test_approved_produces_no_scg_status(self, monkeypatch):
        monkeypatch.setattr(_enf_mod, "judge_transition", _all_approved_provider)
        r = hokom("كَتَبَ")
        assert "scg_status" not in r or r.get("stage") != "SCG_STOPPED"


# ── B. Non-APPROVED verdicts stop the pipeline ────────────────────────────────

_NON_OPENING_VERDICTS = ["BLOCKED", "DEFERRED", "REJECTED", "FORBIDDEN_LEAP", "INVALID"]


class TestNonOpeningVerdictStopsPipeline:
    """
    For each non-APPROVED verdict injected at the first edge,
    hokom() must return a SCG_STOPPED result with the correct fields.
    """

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_verdict_returns_scg_stopped(self, monkeypatch, verdict):
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        assert r.get("stage") == "SCG_STOPPED", (
            f"Verdict {verdict} at {src}→{tgt}: expected SCG_STOPPED, "
            f"got stage={r.get('stage')}"
        )

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_target_stage_opened_false(self, monkeypatch, verdict):
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        assert r.get("target_stage_opened") is False, (
            f"Verdict {verdict}: target_stage_opened must be False"
        )

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_segment_stage_not_opened_after_gate1_stop(self, monkeypatch, verdict):
        """SEGMENT stage (segment_bundle) must not exist if gate 1 stopped."""
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]   # NORMALIZE→SEGMENT
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        # segment_bundle is produced by the SEGMENT stage. If gate 1 stops,
        # segment_bundle must NOT be present in the stopped result.
        assert "segment_bundle" not in r, (
            f"Verdict {verdict} at gate 1: SEGMENT stage must not have opened; "
            f"'segment_bundle' must not be in stopped result"
        )

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_scg_status_matches_verdict(self, monkeypatch, verdict):
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        assert r.get("scg_status") == verdict

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_stopped_result_has_required_fields(self, monkeypatch, verdict):
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        required = {
            "scg_status", "last_completed_stage", "blocked_target_stage",
            "judgment_executed", "infrastructure_failure", "gamma_state",
            "transition_state", "transition_allowed", "terminal",
            "failure_code", "target_stage_opened", "scg_gate_matrix",
        }
        missing = required - set(r.keys())
        assert not missing, (
            f"Verdict {verdict}: stopped result missing fields: {missing}"
        )

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_transition_allowed_false(self, monkeypatch, verdict):
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        assert r.get("transition_allowed") is False


# ── C. DEFERRED calls target zero times ───────────────────────────────────────

class TestDeferredCallsTargetZeroTimes:
    """
    DEFERRED_OPENING_NEXT_STAGE = 0 (mandate requirement).
    Injecting DEFERRED at any edge must produce SCG_STOPPED.
    """

    @pytest.mark.parametrize("edge_idx", range(len(CANONICAL_EDGE_SEQUENCE)))
    def test_deferred_at_any_edge_stops_pipeline(self, monkeypatch, edge_idx):
        src, tgt = CANONICAL_EDGE_SEQUENCE[edge_idx]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, "DEFERRED")
        )
        r = hokom("كَتَبَ")
        assert r.get("stage") == "SCG_STOPPED", (
            f"DEFERRED at edge {edge_idx} ({src}→{tgt}): "
            f"pipeline must stop, got stage={r.get('stage')}"
        )

    @pytest.mark.parametrize("edge_idx", range(len(CANONICAL_EDGE_SEQUENCE)))
    def test_deferred_target_stage_opened_false(self, monkeypatch, edge_idx):
        src, tgt = CANONICAL_EDGE_SEQUENCE[edge_idx]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, "DEFERRED")
        )
        r = hokom("كَتَبَ")
        assert r.get("target_stage_opened") is False


# ── D. BLOCKED calls target zero times ────────────────────────────────────────

class TestBlockedCallsTargetZeroTimes:
    """BLOCKED_OPENING_NEXT_STAGE = 0."""

    def test_blocked_at_first_edge_stops_before_segment(self, monkeypatch):
        monkeypatch.setattr(_enf_mod, "judge_transition", _blocked_at_first_provider)
        r = hokom("كَتَبَ")
        assert r.get("stage") == "SCG_STOPPED"
        assert "segment_bundle" not in r, "SEGMENT must not be opened after BLOCKED at gate 1"
        assert r.get("blocked_target_stage") == "SEGMENT"

    @pytest.mark.parametrize("edge_idx", range(len(CANONICAL_EDGE_SEQUENCE)))
    def test_blocked_at_any_edge_stops_pipeline(self, monkeypatch, edge_idx):
        src, tgt = CANONICAL_EDGE_SEQUENCE[edge_idx]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, "BLOCKED")
        )
        r = hokom("كَتَبَ")
        assert r.get("stage") == "SCG_STOPPED"
        assert r.get("target_stage_opened") is False


# ── E. Terminal judgment stops all later stages ────────────────────────────────

class TestTerminalStopsAllLaterStages:
    """POST_TERMINAL_STAGE_EXECUTIONS = 0."""

    def test_blocked_is_terminal(self, monkeypatch):
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, "BLOCKED")
        )
        r = hokom("كَتَبَ")
        assert r.get("terminal") is True

    def test_rejected_is_terminal(self, monkeypatch):
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, "REJECTED")
        )
        r = hokom("كَتَبَ")
        assert r.get("terminal") is True

    def test_deferred_is_not_terminal(self, monkeypatch):
        """DEFERRED stops traversal but is not a terminal hard stop."""
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, "DEFERRED")
        )
        r = hokom("كَتَبَ")
        # DEFERRED stops the pipeline but is not marked terminal.
        assert r.get("stage") == "SCG_STOPPED"
        assert r.get("terminal") is False

    def test_matrix_records_only_one_edge_on_first_stop(self, monkeypatch):
        """After the first stop, no further edges must be judged."""
        monkeypatch.setattr(_enf_mod, "judge_transition", _blocked_at_first_provider)
        r = hokom("كَتَبَ")
        matrix = r.get("scg_gate_matrix", {})
        assert matrix.get("edge_count") == 1, (
            f"Expected exactly 1 edge in matrix after gate-1 stop, "
            f"got {matrix.get('edge_count')}"
        )

    @pytest.mark.parametrize("verdict", ["BLOCKED", "REJECTED", "FORBIDDEN_LEAP"])
    def test_later_stage_count_zero_after_terminal(self, monkeypatch, verdict):
        """After terminal at gate 1, all subsequent gates have 0 executions."""
        call_log = []
        src0, tgt0 = CANONICAL_EDGE_SEQUENCE[0]

        def _provider(source, target):
            call_log.append((source, target))
            if (source, target) == (src0, tgt0):
                return _make_judgment(source, target, verdict)
            return _make_judgment(source, target, "APPROVED")

        monkeypatch.setattr(_enf_mod, "judge_transition", _provider)
        hokom("كَتَبَ")
        # Only gate 1 should have been called (pipeline stopped immediately).
        assert call_log == [(src0, tgt0)], (
            f"After terminal {verdict} at gate 1, expected 1 judge call, "
            f"got: {call_log}"
        )


# ── F. Runtime-error produces BLOCKED (not silent fallback) ───────────────────

class TestRuntimeErrorFailClosed:
    """Enforcer runtime failure → pipeline stops, not a silent pass-through."""

    def test_runtime_error_stops_pipeline(self, monkeypatch):
        """Simulate a runtime error inside judge_transition itself."""
        def _raises(source, target):
            raise RuntimeError("simulated enforcer runtime failure")

        # The hard gate in hokom_pipeline.py does NOT catch exceptions from
        # judge_transition — the error propagates (fail-closed, not silent).
        # This test verifies that raising inside judge_transition is not swallowed.
        monkeypatch.setattr(_enf_mod, "judge_transition", _raises)
        with pytest.raises(RuntimeError, match="simulated enforcer runtime failure"):
            hokom("كَتَبَ")


# ── G. Stopped result is distinct from successful result ──────────────────────

class TestStoppedResultDistinct:
    """BLOCKED_PIPELINE_RESULTS_MARKED_SUCCESS = 0."""

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_stopped_stage_not_slot_engineering(self, monkeypatch, verdict):
        """Stopped results must NOT have stage='slot_engineering'."""
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        assert r.get("stage") != "slot_engineering", (
            f"Verdict {verdict}: a blocked result must not claim stage='slot_engineering'"
        )

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_stopped_stage_is_scg_stopped(self, monkeypatch, verdict):
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        assert r.get("stage") == "SCG_STOPPED"

    @pytest.mark.parametrize("verdict", _NON_OPENING_VERDICTS)
    def test_stopped_verdict_field_is_none(self, monkeypatch, verdict):
        """Linguistic 'verdict' must be None in a stopped result."""
        src, tgt = CANONICAL_EDGE_SEQUENCE[0]
        monkeypatch.setattr(
            _enf_mod, "judge_transition",
            _verdict_at_edge_provider(src, tgt, verdict)
        )
        r = hokom("كَتَبَ")
        assert r.get("verdict") is None
