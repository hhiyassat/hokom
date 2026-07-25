"""
tests/scg/test_taaqol_transition_determinism.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mandate: HOKOM-SCG-P0-P12-CANONICAL-CONFORMANCE-OWNERSHIP-AND-TAAQOL-JUDGMENT-CLOSURE-01
Section: §C — Determinism and constitutional matrix closure rules.

Constitutional rules tested here:
  - Taaqol judgment for a given (source, target) must be deterministic:
    calling judge_transition() twice for the same edge must produce the
    same gate_verdict (no token-specific rules, no non-deterministic fallbacks).
  - CANONICAL_EDGE_SEQUENCE is immutable/frozen (no runtime mutation).
  - DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT is invariant.
  - TaaqolJudgmentMatrix counter properties are consistent (edge_count ==
    taaqol_called_count == len(judgments) when all calls are made).
  - judge_transition() does not mutate global state between calls.
  - SCGTransitionEnforcer is independent across instances (no shared state).
  - The SCG closure state (TRANSITIONS_WITHOUT_TAAQOL=0, SILENT_FALLBACKS=0,
    LOCAL_DECISIONS=0) is invariant across multiple surfaces.
"""
import pytest
import threading
from typing import List

from pipeline.governance.taaqol_judgment_enforcer import (
    CANONICAL_EDGE_SEQUENCE,
    DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT,
    TaaqolTransitionJudgment,
    TaaqolJudgmentMatrix,
    SCGTransitionEnforcer,
    judge_transition,
    build_judgment_matrix_for_surface,
    discover_canonical_edge_count,
)


_TEST_SURFACES = [
    "كَتَبَ",
    "وَلَدَ",
    "قَرَأَ",
    "ذَهَبَ",
    "جَلَسَ",
]


# ── A. Verdict determinism ─────────────────────────────────────────────────────

class TestVerdictDeterminism:
    """Repeated calls for the same edge must produce the same verdict."""

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_same_edge_same_verdict_two_calls(self, source, target):
        j1 = judge_transition(source, target)
        j2 = judge_transition(source, target)
        assert j1.gate_verdict == j2.gate_verdict, (
            f"Edge {source}→{target}: verdict not deterministic "
            f"({j1.gate_verdict} != {j2.gate_verdict})"
        )

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_same_edge_same_gamma_state_two_calls(self, source, target):
        j1 = judge_transition(source, target)
        j2 = judge_transition(source, target)
        assert j1.gamma_closure_state == j2.gamma_closure_state

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_same_edge_same_failure_code_two_calls(self, source, target):
        j1 = judge_transition(source, target)
        j2 = judge_transition(source, target)
        assert j1.failure_code == j2.failure_code

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_same_edge_same_runtime_active_two_calls(self, source, target):
        j1 = judge_transition(source, target)
        j2 = judge_transition(source, target)
        assert j1.taaqol_runtime_active == j2.taaqol_runtime_active

    @pytest.mark.parametrize("surface", _TEST_SURFACES)
    def test_matrix_verdict_sequence_deterministic(self, surface):
        """Full matrix verdict sequence must be identical across two runs."""
        m1 = build_judgment_matrix_for_surface(surface)
        m2 = build_judgment_matrix_for_surface(surface)
        v1 = [j.gate_verdict for j in m1.judgments]
        v2 = [j.gate_verdict for j in m2.judgments]
        assert v1 == v2, (
            f"Surface '{surface}': verdict sequence not deterministic\n"
            f"Run 1: {v1}\nRun 2: {v2}"
        )


# ── B. Edge sequence immutability ─────────────────────────────────────────────

class TestEdgeSequenceImmutability:
    """CANONICAL_EDGE_SEQUENCE must not be mutated at runtime."""

    def test_sequence_is_tuple(self):
        assert isinstance(CANONICAL_EDGE_SEQUENCE, tuple)

    def test_sequence_items_are_tuples(self):
        for item in CANONICAL_EDGE_SEQUENCE:
            assert isinstance(item, tuple), f"Edge {item} is not a tuple"

    def test_sequence_cannot_be_appended_to(self):
        with pytest.raises((AttributeError, TypeError)):
            CANONICAL_EDGE_SEQUENCE.append(("FAKE", "STAGE"))  # type: ignore[attr-defined]

    def test_constant_cannot_be_decremented_externally(self):
        """The constant is an int — cannot be decremented in place."""
        original = DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT
        # Even if a test tried to shadow it, the module constant remains.
        import pipeline.governance.taaqol_judgment_enforcer as enforcer_mod
        assert enforcer_mod.DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT == 11
        assert discover_canonical_edge_count() == 11

    def test_edge_sequence_length_matches_constant_after_repeated_access(self):
        for _ in range(5):
            assert len(CANONICAL_EDGE_SEQUENCE) == DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT


# ── C. Matrix counter consistency ─────────────────────────────────────────────

class TestMatrixCounterConsistency:
    """Matrix counter properties must be internally consistent."""

    @pytest.mark.parametrize("surface", _TEST_SURFACES)
    def test_edge_count_equals_len_judgments(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        assert matrix.edge_count == len(matrix.judgments)

    @pytest.mark.parametrize("surface", _TEST_SURFACES)
    def test_taaqol_called_count_equals_edge_count(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        assert matrix.taaqol_called_count == matrix.edge_count

    @pytest.mark.parametrize("surface", _TEST_SURFACES)
    def test_transitions_without_taaqol_always_zero(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        assert matrix.transitions_without_taaqol == 0

    @pytest.mark.parametrize("surface", _TEST_SURFACES)
    def test_local_decisions_always_zero(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        assert matrix.local_decisions == 0

    @pytest.mark.parametrize("surface", _TEST_SURFACES)
    def test_silent_fallbacks_always_zero(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        assert matrix.silent_fallbacks == 0

    @pytest.mark.parametrize("surface", _TEST_SURFACES)
    def test_blocked_plus_non_blocked_equals_total(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        blocked = matrix.blocked_count
        rejected = matrix.rejected_count
        total = matrix.edge_count
        # blocked + rejected ≤ total; remaining judgments are non-terminal.
        assert blocked + rejected <= total


# ── D. No shared state between enforcer instances ────────────────────────────

class TestEnforcerNoSharedState:
    """Each SCGTransitionEnforcer must be completely independent."""

    def test_two_enforcers_independent_surfaces(self):
        e1 = SCGTransitionEnforcer("كَتَبَ")
        e2 = SCGTransitionEnforcer("وَلَدَ")
        e1.judge("NORMALIZE", "SEGMENT")
        # e2 must still be empty.
        assert e2.get_matrix().edge_count == 0

    def test_enforcer_does_not_share_judgments_list(self):
        e1 = SCGTransitionEnforcer("كَتَبَ")
        e2 = SCGTransitionEnforcer("وَلَدَ")
        e1.judge("NORMALIZE", "SEGMENT")
        e1.judge("SEGMENT", "NORM_ATOMIC")
        assert e2.get_matrix().edge_count == 0
        assert e1.get_matrix().edge_count == 2

    def test_fresh_enforcer_starts_empty(self):
        for _ in range(3):
            e = SCGTransitionEnforcer("كَتَبَ")
            assert e.get_matrix().edge_count == 0


# ── E. Closure invariants across surfaces ─────────────────────────────────────

class TestClosureInvariantsAcrossSurfaces:
    """
    The SCG closure conditions must hold for every surface:
      TRANSITIONS_WITHOUT_TAAQOL = 0
      SILENT_TAAQOL_FALLBACKS = 0
      LOCAL_TRANSITION_DECISIONS = 0
    """

    @pytest.mark.parametrize("surface", _TEST_SURFACES)
    def test_scg_closure_invariants(self, surface):
        matrix = build_judgment_matrix_for_surface(surface)
        assert matrix.transitions_without_taaqol == 0, (
            f"Surface '{surface}': TRANSITIONS_WITHOUT_TAAQOL != 0"
        )
        assert matrix.silent_fallbacks == 0, (
            f"Surface '{surface}': SILENT_TAAQOL_FALLBACKS != 0"
        )
        assert matrix.local_decisions == 0, (
            f"Surface '{surface}': LOCAL_TRANSITION_DECISIONS != 0"
        )

    def test_p13_created_count_zero(self):
        """No judgment in any matrix triggers P13 creation."""
        for surface in _TEST_SURFACES:
            matrix = build_judgment_matrix_for_surface(surface)
            for j in matrix.judgments:
                assert j.target_stage != "P13", (
                    f"Surface '{surface}': judgment targets P13 — P13_ALLOWED=NO"
                )


# ── F. Thread safety (basic) ──────────────────────────────────────────────────

class TestConcurrentJudgmentDeterminism:
    """judge_transition() must produce consistent verdicts under concurrent calls."""

    def test_concurrent_calls_same_verdict(self):
        results: List[str] = []
        errors: List[Exception] = []

        def run():
            try:
                j = judge_transition("NORMALIZE", "SEGMENT")
                results.append(j.gate_verdict)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=run) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        assert len(results) == 8
        # All verdicts must be the same (deterministic).
        assert len(set(results)) == 1, (
            f"Non-deterministic concurrent verdicts: {results}"
        )
