"""
tests/scg/test_taaqol_judgment_all_edges.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mandate: HOKOM-SCG-P0-P12-CANONICAL-CONFORMANCE-OWNERSHIP-AND-TAAQOL-JUDGMENT-CLOSURE-01
Section: §C — Taaqol judgment must be issued on every canonical edge.

Constitutional assertions tested here:
  1. DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT equals the edge sequence length.
  2. judge_transition() always sets taaqol_called=True for every edge.
  3. fallback_used is always False (constitutional invariant).
  4. gate_verdict is never None or empty.
  5. build_judgment_matrix_for_surface() records at least 1 judgment for a
     surface when Taaqol is unavailable (fail-closed produces BLOCKED, which
     stops traversal after the first edge — but taaqol_called is still True).
  6. When Taaqol vendor IS available, all 11 edges are judged (full traversal).
  7. TaaqolJudgmentMatrix.local_decisions == 0 always (no local decisions).
  8. TaaqolJudgmentMatrix.silent_fallbacks == 0 always.

Python compatibility note:
  Taaqol vendor requires Python 3.11+ (StrEnum).  On Python ≤ 3.10 the vendor
  import fails → BLOCKED (fail-closed).  All tests must pass in both Python
  versions — test logic accommodates the BLOCKED path explicitly.

Canonical test run: macOS / Python 3.12.4 / .venv-py312
"""
import sys
import pytest

from pipeline.governance.taaqol_judgment_enforcer import (
    CANONICAL_EDGE_SEQUENCE,
    DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT,
    TaaqolTransitionJudgment,
    TaaqolJudgmentMatrix,
    judge_transition,
    build_judgment_matrix_for_surface,
    discover_canonical_edge_count,
    SCGTransitionEnforcer,
    _try_import_taaqol,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _taaqol_available() -> bool:
    available, _, _ = _try_import_taaqol()
    return available


TAAQOL_AVAILABLE = _taaqol_available()


# ── §C-1  Edge count constant ──────────────────────────────────────────────────

class TestEdgeCountConstant:
    def test_constant_equals_sequence_length(self):
        assert DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT == len(CANONICAL_EDGE_SEQUENCE)

    def test_constant_is_11(self):
        assert DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT == 11

    def test_discover_function_matches_constant(self):
        assert discover_canonical_edge_count() == DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT

    def test_sequence_first_edge(self):
        assert CANONICAL_EDGE_SEQUENCE[0] == ("NORMALIZE", "SEGMENT")

    def test_sequence_last_edge(self):
        assert CANONICAL_EDGE_SEQUENCE[-1] == ("PHASE_5", "TAAQOL_SGA")

    def test_sequence_has_no_duplicate_edges(self):
        seen = set()
        for src, tgt in CANONICAL_EDGE_SEQUENCE:
            edge = (src, tgt)
            assert edge not in seen, f"Duplicate edge: {edge}"
            seen.add(edge)

    def test_sequence_covers_contiguous_stages(self):
        # The target of edge N must equal the source of edge N+1.
        for i in range(len(CANONICAL_EDGE_SEQUENCE) - 1):
            _, tgt = CANONICAL_EDGE_SEQUENCE[i]
            src_next, _ = CANONICAL_EDGE_SEQUENCE[i + 1]
            assert tgt == src_next, (
                f"Edge {i} target '{tgt}' does not match edge {i+1} source '{src_next}'"
            )


# ── §C-2  Per-edge judgment properties ────────────────────────────────────────

class TestPerEdgeJudgmentProperties:
    """Each call to judge_transition() must satisfy the constitutional invariants."""

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_taaqol_called_true(self, source, target):
        j = judge_transition(source, target)
        assert j.taaqol_called is True, (
            f"Edge {source}→{target}: taaqol_called must always be True"
        )

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_fallback_never_used(self, source, target):
        j = judge_transition(source, target)
        assert j.fallback_used is False, (
            f"Edge {source}→{target}: fallback_used=True is a constitutional violation"
        )

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_gate_verdict_non_empty(self, source, target):
        j = judge_transition(source, target)
        assert j.gate_verdict, (
            f"Edge {source}→{target}: gate_verdict must not be empty"
        )

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_edge_id_format(self, source, target):
        j = judge_transition(source, target)
        assert j.edge_id == f"{source}→{target}", (
            f"Edge {source}→{target}: edge_id format incorrect"
        )

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_source_stage_preserved(self, source, target):
        j = judge_transition(source, target)
        assert j.source_stage == source

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_target_stage_preserved(self, source, target):
        j = judge_transition(source, target)
        assert j.target_stage == target

    @pytest.mark.parametrize("source,target", CANONICAL_EDGE_SEQUENCE)
    def test_gamma_state_non_empty(self, source, target):
        j = judge_transition(source, target)
        assert j.gamma_closure_state, (
            f"Edge {source}→{target}: gamma_closure_state must not be empty"
        )


# ── §C-3  Fail-closed on unavailable Taaqol ───────────────────────────────────

class TestFailClosedVendorUnavailable:
    """When Taaqol vendor is unavailable, verdict must be BLOCKED — not a fallback."""

    @pytest.mark.skipif(TAAQOL_AVAILABLE, reason="Taaqol available — testing unavailable path only")
    def test_blocked_when_taaqol_unavailable(self):
        j = judge_transition("NORMALIZE", "SEGMENT")
        assert j.gate_verdict == "BLOCKED"
        assert j.failure_code == "TAAQOL_IMPORT_FAILURE"
        assert j.taaqol_runtime_active is False
        assert j.error_detail is not None

    @pytest.mark.skipif(TAAQOL_AVAILABLE, reason="Taaqol available — testing unavailable path only")
    def test_gamma_state_unavailable_when_vendor_absent(self):
        j = judge_transition("PHASE_5", "TAAQOL_SGA")
        assert j.gamma_closure_state == "UNAVAILABLE"


# ── §C-4  Matrix properties ────────────────────────────────────────────────────

class TestJudgmentMatrixProperties:
    """TaaqolJudgmentMatrix must always satisfy constitutional matrix invariants."""

    def test_matrix_surface_preserved(self):
        surface = "كَتَبَ"
        matrix = build_judgment_matrix_for_surface(surface)
        assert matrix.surface == surface

    def test_matrix_local_decisions_always_zero(self):
        matrix = build_judgment_matrix_for_surface("كَتَبَ")
        assert matrix.local_decisions == 0

    def test_matrix_silent_fallbacks_always_zero(self):
        matrix = build_judgment_matrix_for_surface("كَتَبَ")
        assert matrix.silent_fallbacks == 0

    def test_matrix_taaqol_called_count_equals_edge_count(self):
        matrix = build_judgment_matrix_for_surface("وَلَدَ")
        assert matrix.taaqol_called_count == matrix.edge_count

    def test_matrix_transitions_without_taaqol_always_zero(self):
        matrix = build_judgment_matrix_for_surface("قَرَأَ")
        assert matrix.transitions_without_taaqol == 0

    def test_matrix_at_least_one_judgment(self):
        matrix = build_judgment_matrix_for_surface("كَتَبَ")
        assert matrix.edge_count >= 1

    @pytest.mark.skipif(not TAAQOL_AVAILABLE, reason="Requires live Taaqol vendor (Python 3.11+)")
    def test_matrix_all_11_edges_judged_when_vendor_available(self):
        matrix = build_judgment_matrix_for_surface("كَتَبَ")
        assert matrix.edge_count == DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT, (
            f"Expected {DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT} judgments; "
            f"got {matrix.edge_count}"
        )

    @pytest.mark.skipif(not TAAQOL_AVAILABLE, reason="Requires live Taaqol vendor (Python 3.11+)")
    def test_matrix_no_blocked_verdicts_on_valid_token(self):
        # On a valid Arabic token with Taaqol available, no structural edge should block.
        matrix = build_judgment_matrix_for_surface("كَتَبَ")
        blocked = [j.edge_id for j in matrix.judgments if j.gate_verdict == "BLOCKED"]
        assert blocked == [], f"Unexpected BLOCKED edges on valid token: {blocked}"

    def test_matrix_to_dict_structure(self):
        matrix = build_judgment_matrix_for_surface("كَتَبَ")
        d = matrix.to_dict()
        assert "surface" in d
        assert "DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT" in d
        assert "edge_count" in d
        assert "taaqol_called_count" in d
        assert "transitions_without_taaqol" in d
        assert "local_decisions" in d
        assert "silent_fallbacks" in d
        assert "judgments" in d
        assert isinstance(d["judgments"], list)

    def test_matrix_to_dict_judgments_schema(self):
        matrix = build_judgment_matrix_for_surface("كَتَبَ")
        d = matrix.to_dict()
        required_keys = {
            "edge_id", "source_stage", "target_stage",
            "taaqol_called", "taaqol_runtime_active",
            "gamma_closure_state", "gate_verdict",
            "failure_code", "fallback_used", "error_detail",
        }
        for entry in d["judgments"]:
            missing = required_keys - set(entry.keys())
            assert not missing, f"Judgment entry missing keys: {missing}"


# ── §C-5  Enforcer class ───────────────────────────────────────────────────────

class TestSCGTransitionEnforcer:
    def test_enforcer_judge_records_judgment(self):
        enforcer = SCGTransitionEnforcer("كَتَبَ")
        j = enforcer.judge("NORMALIZE", "SEGMENT")
        matrix = enforcer.get_matrix()
        assert matrix.edge_count == 1
        assert matrix.judgments[0] is j

    def test_enforcer_judge_all_canonical_edges_stops_at_blocked(self):
        enforcer = SCGTransitionEnforcer("كَتَبَ")
        matrix = enforcer.judge_all_canonical_edges()
        # Whether Taaqol is available or not, taaqol_called must be True for all judgments.
        for j in matrix.judgments:
            assert j.taaqol_called is True
            assert j.fallback_used is False

    def test_enforcer_surface_preserved(self):
        surface = "يَكْتُبُ"
        enforcer = SCGTransitionEnforcer(surface)
        enforcer.judge_all_canonical_edges()
        assert enforcer.get_matrix().surface == surface
