"""
tests/scg/test_taaqol_fail_closed.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mandate: HOKOM-SCG-P0-P12-CANONICAL-CONFORMANCE-OWNERSHIP-AND-TAAQOL-JUDGMENT-CLOSURE-01
Section: §C — Binding rules 11, 12, 18 enforcement.

Binding rules tested here:
  11. Absence or failure of the Taaqol runtime must fail closed.
  12. Deferred, Blocked, Rejected, ForbiddenLeap, Invalid, or terminal decisions
      must not open a later candidate.
  18. No silent fallbacks, token-specific rules, planted verdicts, or mocked
      final integration decisions.

Tests in this file verify the FAIL_CLOSED architecture:
  A. TaaqolTransitionJudgment rejects construction with fallback_used=True.
  B. When Taaqol is unavailable (import fails), verdict is BLOCKED, not
     LICENSED or any local approximation.
  C. Silent fallbacks are constitutionally impossible to construct.
  D. judge_transition() never returns an empty or None verdict.
  E. SCGTransitionEnforcer.judge_all_canonical_edges() halts after BLOCKED.
  F. No judgment in the matrix has fallback_used=True.
  G. Under simulated import failure, all per-edge calls set
     taaqol_runtime_active=False and gate_verdict="BLOCKED".
"""
import sys
import unittest.mock as mock
import pytest

from pipeline.governance.taaqol_judgment_enforcer import (
    CANONICAL_EDGE_SEQUENCE,
    DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT,
    TaaqolTransitionJudgment,
    TaaqolJudgmentMatrix,
    SCGTransitionEnforcer,
    enforce_terminal_guard,
    judge_transition,
    build_judgment_matrix_for_surface,
    _try_import_taaqol,
)


# ── A. Constitutional invariant — fallback_used=True raises immediately ────────

class TestFallbackNeverAllowed:
    def test_construction_with_fallback_true_raises(self):
        with pytest.raises(ValueError, match="constitutional violation"):
            TaaqolTransitionJudgment(
                edge_id="NORMALIZE→SEGMENT",
                source_stage="NORMALIZE",
                target_stage="SEGMENT",
                taaqol_called=True,
                taaqol_runtime_active=False,
                gamma_closure_state="UNAVAILABLE",
                gate_verdict="LICENSED",  # attempted silent fallback verdict
                failure_code=None,
                fallback_used=True,       # ← this must raise
                error_detail=None,
            )

    def test_construction_with_fallback_false_is_fine(self):
        j = TaaqolTransitionJudgment(
            edge_id="NORMALIZE→SEGMENT",
            source_stage="NORMALIZE",
            target_stage="SEGMENT",
            taaqol_called=True,
            taaqol_runtime_active=False,
            gamma_closure_state="UNAVAILABLE",
            gate_verdict="BLOCKED",
            failure_code="TAAQOL_IMPORT_FAILURE",
            fallback_used=False,
            error_detail="ImportError: no module named taaqqul_slot_geometry",
        )
        assert j.fallback_used is False


# ── B. Taaqol unavailable → BLOCKED verdict ───────────────────────────────────

class TestVendorUnavailableFailClosed:
    """
    Simulate Taaqol vendor import failure by patching _try_import_taaqol.
    This tests the fail-closed path regardless of the actual Python version.
    """

    def _mock_unavailable(self):
        return (False, None, "ImportError: simulated vendor absence")

    def test_blocked_on_import_failure_normalize_segment(self):
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_unavailable,
        ):
            j = judge_transition("NORMALIZE", "SEGMENT")
        assert j.gate_verdict == "BLOCKED"
        assert j.taaqol_called is True
        assert j.taaqol_runtime_active is False
        assert j.fallback_used is False
        assert j.failure_code == "TAAQOL_IMPORT_FAILURE"
        assert j.error_detail is not None

    def test_blocked_on_import_failure_phase5_taaqol(self):
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_unavailable,
        ):
            j = judge_transition("PHASE_5", "TAAQOL_SGA")
        assert j.gate_verdict == "BLOCKED"
        assert j.gamma_closure_state == "UNAVAILABLE"

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_all_edges_blocked_on_import_failure(self, source, target):
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_unavailable,
        ):
            j = judge_transition(source, target)
        assert j.gate_verdict == "BLOCKED", (
            f"Edge {source}→{target}: expected BLOCKED on vendor unavailable, got {j.gate_verdict}"
        )
        assert j.fallback_used is False

    def test_matrix_first_judgment_blocks_traversal(self):
        """When vendor is unavailable, judge_all_canonical_edges stops at first BLOCKED."""
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_unavailable,
        ):
            matrix = build_judgment_matrix_for_surface("كَتَبَ")
        # Only the first edge is judged (traversal stops at BLOCKED).
        assert matrix.edge_count == 1
        assert matrix.judgments[0].gate_verdict == "BLOCKED"
        assert matrix.local_decisions == 0
        assert matrix.silent_fallbacks == 0

    def test_no_licensed_verdict_on_vendor_absence(self):
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_unavailable,
        ):
            for source, target in CANONICAL_EDGE_SEQUENCE:
                j = judge_transition(source, target)
                assert j.gate_verdict != "LICENSED", (
                    f"Edge {source}→{target}: LICENSED verdict without live Taaqol "
                    "is a constitutional violation"
                )


# ── C. Runtime error → BLOCKED, not silent fallback ───────────────────────────

class TestRuntimeErrorFailClosed:
    """
    When Taaqol vendor is importable but gamma()/decide() raises at runtime,
    verdict must be BLOCKED (not a silent fallback).
    """

    class _FakeHandles:
        class SlotBoundary:
            def __init__(self, **kwargs): pass
        class Center:
            def __init__(self, **kwargs): pass
        class SlotGraph:
            def __init__(self, **kwargs): pass

        @staticmethod
        def gamma(_slot_graph):
            raise RuntimeError("simulated Taaqol runtime failure")

        class TransitionGate:
            def __init__(self, **kwargs): pass
            def decide(self, _gamma_result):
                raise RuntimeError("should not reach TransitionGate.decide")

        class Rank:
            def __new__(cls, *args, **kwargs):
                raise RuntimeError("simulated Rank failure")
            HYPOTHESIS = 3

    def _mock_available_runtime_fails(self):
        return (True, self._FakeHandles(), None)

    def test_runtime_error_produces_blocked(self):
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_available_runtime_fails,
        ):
            j = judge_transition("NORMALIZE", "SEGMENT")
        assert j.gate_verdict == "BLOCKED"
        assert j.failure_code == "TAAQOL_RUNTIME_ERROR"
        assert j.taaqol_runtime_active is True  # vendor was available
        assert j.fallback_used is False
        assert j.error_detail is not None
        assert "RuntimeError" in j.error_detail or "simulated" in j.error_detail

    def test_runtime_error_gamma_state_is_runtime_error(self):
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_available_runtime_fails,
        ):
            j = judge_transition("PHASE_4A", "PHASE_4B")
        assert j.gamma_closure_state == "RUNTIME_ERROR"


# ── D. No empty/None verdict ──────────────────────────────────────────────────

class TestVerdictNeverEmpty:
    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_verdict_not_none(self, source, target):
        j = judge_transition(source, target)
        assert j.gate_verdict is not None

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_verdict_not_empty_string(self, source, target):
        j = judge_transition(source, target)
        assert j.gate_verdict != ""


# ── E. Traversal halts after BLOCKED ──────────────────────────────────────────

class TestTraversalHaltsAfterBlocked:
    def _mock_unavailable(self):
        return (False, None, "ImportError: simulated")

    def test_enforcer_stops_at_first_blocked(self):
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_unavailable,
        ):
            enforcer = SCGTransitionEnforcer("كَتَبَ")
            matrix = enforcer.judge_all_canonical_edges()
        # First edge is BLOCKED → only 1 judgment recorded.
        assert matrix.edge_count == 1
        assert matrix.judgments[0].gate_verdict == "BLOCKED"

    def test_no_judgment_after_blocked_in_matrix(self):
        with mock.patch(
            "pipeline.governance.taaqol_judgment_enforcer._try_import_taaqol",
            side_effect=self._mock_unavailable,
        ):
            matrix = build_judgment_matrix_for_surface("وَلَدَ")
        # Verify no judgment was added after the BLOCKED one.
        blocked_seen = False
        for j in matrix.judgments:
            if blocked_seen:
                pytest.fail(f"Judgment {j.edge_id} recorded after BLOCKED verdict")
            if j.gate_verdict in ("BLOCKED", "REJECTED", "FORBIDDEN_LEAP"):
                blocked_seen = True


# ── F. Matrix — all judgments have fallback_used=False ────────────────────────

class TestMatrixNoFallbacks:
    @pytest.mark.parametrize("surface", ["كَتَبَ", "وَلَدَ", "قَرَأَ", "ذَهَبَ"])
    def test_no_fallbacks_in_matrix(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        for j in matrix.judgments:
            assert j.fallback_used is False, (
                f"Surface '{surface}', edge {j.edge_id}: fallback_used=True found"
            )

    @pytest.mark.parametrize("surface", ["كَتَبَ", "وَلَدَ"])
    def test_no_local_decisions_in_matrix(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        assert matrix.local_decisions == 0


# ── G. enforce_terminal_guard ─────────────────────────────────────────────────

class TestTerminalGuard:
    def test_guard_passes_when_p13_not_opened(self):
        matrix = TaaqolJudgmentMatrix(surface="كَتَبَ")
        matrix.judgments.append(TaaqolTransitionJudgment(
            edge_id="NORMALIZE→SEGMENT",
            source_stage="NORMALIZE", target_stage="SEGMENT",
            taaqol_called=True, taaqol_runtime_active=True,
            gamma_closure_state="OPEN", gate_verdict="APPROVED",
            failure_code=None, fallback_used=False, error_detail=None,
        ))
        assert enforce_terminal_guard(matrix, p13_or_post_ifadah_opened=False) is True

    def test_guard_fails_when_p13_opened(self):
        matrix = TaaqolJudgmentMatrix(surface="كَتَبَ")
        assert enforce_terminal_guard(matrix, p13_or_post_ifadah_opened=True) is False

    def test_guard_fails_when_judgment_after_blocked(self):
        matrix = TaaqolJudgmentMatrix(surface="كَتَبَ")
        matrix.judgments.append(TaaqolTransitionJudgment(
            edge_id="NORMALIZE→SEGMENT",
            source_stage="NORMALIZE", target_stage="SEGMENT",
            taaqol_called=True, taaqol_runtime_active=False,
            gamma_closure_state="UNAVAILABLE", gate_verdict="BLOCKED",
            failure_code="TAAQOL_IMPORT_FAILURE", fallback_used=False,
            error_detail="simulated",
        ))
        # This second judgment should not exist — guard must catch it.
        matrix.judgments.append(TaaqolTransitionJudgment(
            edge_id="SEGMENT→NORM_ATOMIC",
            source_stage="SEGMENT", target_stage="NORM_ATOMIC",
            taaqol_called=True, taaqol_runtime_active=True,
            gamma_closure_state="OPEN", gate_verdict="APPROVED",
            failure_code=None, fallback_used=False, error_detail=None,
        ))
        assert enforce_terminal_guard(matrix) is False

    def test_guard_passes_empty_matrix(self):
        matrix = TaaqolJudgmentMatrix(surface="كَتَبَ")
        assert enforce_terminal_guard(matrix) is True

    def test_p13_allowed_false_is_enforced(self):
        """P13_ALLOWED = NO — guard must return False if p13 opened."""
        matrix = TaaqolJudgmentMatrix(surface="كَتَبَ")
        # Even with no judgments, if p13 is opened it's a violation.
        assert enforce_terminal_guard(matrix, p13_or_post_ifadah_opened=True) is False
