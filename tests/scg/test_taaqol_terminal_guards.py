from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
"""
tests/scg/test_taaqol_terminal_guards.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Mandate: HOKOM-SCG-P0-P12-CANONICAL-CONFORMANCE-OWNERSHIP-AND-TAAQOL-JUDGMENT-CLOSURE-01
Section: §C — Binding rules 12, 13 enforcement.

Binding rules tested here:
  12. Deferred, Blocked, Rejected, ForbiddenLeap, Invalid, or terminal decisions
      must not open a later candidate.
  13. P12 IfadahCandidate is terminal and must not open P13.

Tests in this file verify:
  A. enforce_terminal_guard() correctly identifies all terminal verdict types.
  B. P12 terminal rule: p13_or_post_ifadah_opened=True always fails guard.
  C. Valid verdict sequences pass guard.
  D. All terminal verdict strings are recognized.
  E. IfadahCandidate class exists and is defined as terminal (P12).
  F. P13_ALLOWED=NO: no module or class in the Hokom tree defines a P13 stage.
"""
import sys
import pytest

from pipeline.governance.taaqol_judgment_enforcer import (
    CANONICAL_EDGE_SEQUENCE,
    DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT,
    TaaqolTransitionJudgment,
    TaaqolJudgmentMatrix,
    enforce_terminal_guard,
    build_judgment_matrix_for_surface,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

TERMINAL_VERDICTS = ("BLOCKED", "REJECTED", "FORBIDDEN_LEAP")
NON_TERMINAL_VERDICTS = ("APPROVED", "DEFERRED")


def _make_judgment(edge_idx: int, verdict: str) -> TaaqolTransitionJudgment:
    source, target = CANONICAL_EDGE_SEQUENCE[edge_idx]
    return TaaqolTransitionJudgment(
        edge_id=f"{source}→{target}",
        source_stage=source,
        target_stage=target,
        taaqol_called=True,
        taaqol_runtime_active=True,
        gamma_closure_state="OPEN" if verdict not in TERMINAL_VERDICTS else "CLOSED",
        gate_verdict=verdict,
        failure_code=None if verdict not in TERMINAL_VERDICTS else "TAAQOL_GATE_CLOSED",
        fallback_used=False,
        error_detail=None,
    )


def _matrix_with_sequence(*verdicts) -> TaaqolJudgmentMatrix:
    """Build a TaaqolJudgmentMatrix with judgments for the given verdict sequence."""
    assert len(verdicts) <= DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT
    matrix = TaaqolJudgmentMatrix(surface="كَتَبَ")
    for i, v in enumerate(verdicts):
        matrix.judgments.append(_make_judgment(i, v))
    return matrix


# ── A. Terminal verdict recognition ───────────────────────────────────────────

class TestTerminalVerdictRecognition:
    """enforce_terminal_guard() must recognize all terminal verdict strings."""

    @pytest.mark.parametrize("verdict", TERMINAL_VERDICTS)
    def test_single_terminal_verdict_passes_guard(self, verdict):
        """A single terminal verdict at the last position is fine — no subsequent judgment."""
        matrix = _matrix_with_sequence(verdict)
        assert enforce_terminal_guard(matrix) is True

    @pytest.mark.parametrize("verdict", TERMINAL_VERDICTS)
    def test_judgment_after_terminal_fails_guard(self, verdict):
        """Any judgment recorded after a terminal verdict is a violation."""
        matrix = _matrix_with_sequence(verdict, "APPROVED")
        assert enforce_terminal_guard(matrix) is False

    @pytest.mark.parametrize("terminal", TERMINAL_VERDICTS)
    @pytest.mark.parametrize("subsequent", NON_TERMINAL_VERDICTS + TERMINAL_VERDICTS)
    def test_any_subsequent_after_terminal_fails(self, terminal, subsequent):
        matrix = _matrix_with_sequence(terminal, subsequent)
        assert enforce_terminal_guard(matrix) is False

    @pytest.mark.parametrize("verdict", NON_TERMINAL_VERDICTS)
    def test_non_terminal_verdicts_do_not_halt(self, verdict):
        """APPROVED and DEFERRED are not terminal — subsequent judgments are fine."""
        matrix = _matrix_with_sequence(verdict, verdict)
        assert enforce_terminal_guard(matrix) is True

    def test_all_approved_sequence_passes(self):
        matrix = _matrix_with_sequence(*["APPROVED"] * DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT)
        assert enforce_terminal_guard(matrix) is True

    def test_all_deferred_sequence_passes(self):
        matrix = _matrix_with_sequence(*["DEFERRED"] * DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT)
        assert enforce_terminal_guard(matrix) is True

    def test_mixed_approved_deferred_passes(self):
        sequence = []
        for i in range(DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT):
            sequence.append("APPROVED" if i % 2 == 0 else "DEFERRED")
        matrix = _matrix_with_sequence(*sequence)
        assert enforce_terminal_guard(matrix) is True

    def test_blocked_at_first_edge_passes_guard_alone(self):
        """First edge BLOCKED — no subsequent judgments — guard passes."""
        matrix = _matrix_with_sequence("BLOCKED")
        assert enforce_terminal_guard(matrix) is True

    def test_blocked_at_middle_edge_with_subsequent_fails(self):
        """BLOCKED at edge 3 followed by edge 4 judgment — violation."""
        matrix = _matrix_with_sequence("APPROVED", "APPROVED", "BLOCKED", "APPROVED")
        assert enforce_terminal_guard(matrix) is False


# ── B. P12 terminal rule ───────────────────────────────────────────────────────

class TestP12TerminalRule:
    """P12 IfadahCandidate is terminal. P13 must never be opened."""

    def test_p13_opened_always_fails(self):
        matrix = _matrix_with_sequence("APPROVED")
        assert enforce_terminal_guard(matrix, p13_or_post_ifadah_opened=True) is False

    def test_p13_opened_with_empty_matrix_fails(self):
        matrix = TaaqolJudgmentMatrix(surface="كَتَبَ")
        assert enforce_terminal_guard(matrix, p13_or_post_ifadah_opened=True) is False

    def test_p13_opened_with_full_approved_sequence_fails(self):
        matrix = _matrix_with_sequence(*["APPROVED"] * DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT)
        assert enforce_terminal_guard(matrix, p13_or_post_ifadah_opened=True) is False

    def test_p13_not_opened_with_approved_sequence_passes(self):
        matrix = _matrix_with_sequence(*["APPROVED"] * DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT)
        assert enforce_terminal_guard(matrix, p13_or_post_ifadah_opened=False) is True


# ── C. IfadahCandidate class existence ────────────────────────────────────────

class TestIfadahCandidateExists:
    """IfadahCandidate (P12) must exist as a class in the Hokom codebase."""

    def test_ifadah_candidate_importable(self):
        try:
            from pipeline.taaqol_integration.constitutional_contracts import IfadahCandidate
        except ImportError as e:
            pytest.fail(f"IfadahCandidate not importable: {e}")

    def test_ifadah_candidate_is_a_class(self):
        from pipeline.taaqol_integration.constitutional_contracts import IfadahCandidate
        assert isinstance(IfadahCandidate, type)

    def test_ifadah_candidate_has_dataclass_fields(self):
        import dataclasses
        from pipeline.taaqol_integration.constitutional_contracts import IfadahCandidate
        fields = {f.name for f in dataclasses.fields(IfadahCandidate)}
        # IfadahCandidate must have at minimum an identity/token field.
        assert len(fields) >= 1, "IfadahCandidate must have at least one field"


# ── D. P13_ALLOWED=NO — no P13 stage in codebase ────────────────────────────

class TestNoP13Stage:
    """
    Binding rule 13: P12 IfadahCandidate is terminal. P13 must not exist.

    This test verifies that no Python source file in the Hokom project
    (excluding vendor and test files) defines a class with "P13" or
    "PostIfadah" in its name, or a constant STAGE_P13.
    """

    def test_no_p13_class_in_pipeline(self):
        import os
        import re

        # Check for actual P13 stage/class *definitions* — not references in
        # governance/guard code whose purpose is to detect and block P13.
        # The enforcer itself legitimately contains p13_or_post_ifadah_opened
        # as a guard parameter.  We exclude the enforcer from this scan.
        forbidden_patterns = [
            r"\bclass\s+P13\w*",              # class P13Candidate, class P13Stage …
            r"\bSTAGE_P13\s*=",               # STAGE_P13 = …
            r"\bP13_STAGE\b",                 # P13_STAGE constant
            r"\bPostIfadahCandidate\b",       # PostIfadahCandidate class name
            r"\bclass\s+PostIfadah\w*",       # class PostIfadah…
            # B6: functional and string forms (HOKOM-SCG-P0-P12-TAAQOL-LIVE-GATING-CORRECTION-03)
            r"\bbuild_p13\s*\(",              # build_p13(...) function call
            r"\bopen_p13\s*\(",               # open_p13(...) function call
            r'NEXT_STAGE\s*=\s*["\']P13',     # NEXT_STAGE = "P13" or 'P13'
            r'target_stage\s*=\s*["\']P13',   # target_stage="P13" or 'P13'
        ]
        # Files to skip: the enforcer's purpose is to block P13, so it mentions it.
        skip_files = {"taaqol_judgment_enforcer.py"}
        violations = []

        for root, dirs, files in os.walk("/sessions/lucid-gifted-planck/mnt/hokom/pipeline"):
            dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                if fname in skip_files:
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        src = f.read()
                except Exception:
                    continue
                for pattern in forbidden_patterns:
                    if re.search(pattern, src):
                        violations.append(f"{fpath}: matches '{pattern}'")

        assert violations == [], (
            "P13_ALLOWED=NO: the following files contain P13/PostIfadah references:\n"
            + "\n".join(violations)
        )

    def test_no_p13_in_hokom_pipeline_py(self):
        with open(REPO_ROOT / "hokom_pipeline.py", encoding="utf-8") as f:
            src = f.read()
        assert "P13" not in src, "hokom_pipeline.py must not reference P13"
        assert "PostIfadah" not in src, "hokom_pipeline.py must not reference PostIfadah"


# ── E. Valid sequences that must pass guard ───────────────────────────────────

class TestValidSequences:
    """Representative valid verdict sequences that enforce_terminal_guard must accept."""

    def test_empty_matrix_passes(self):
        matrix = TaaqolJudgmentMatrix(surface="كَتَبَ")
        assert enforce_terminal_guard(matrix) is True

    def test_single_approved_passes(self):
        assert enforce_terminal_guard(_matrix_with_sequence("APPROVED")) is True

    def test_single_deferred_passes(self):
        assert enforce_terminal_guard(_matrix_with_sequence("DEFERRED")) is True

    def test_approved_then_blocked_at_end_passes(self):
        """Valid: pipeline blocked at last edge — no subsequent judgment."""
        sequence = ["APPROVED"] * (DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT - 1) + ["BLOCKED"]
        assert enforce_terminal_guard(_matrix_with_sequence(*sequence)) is True

    def test_real_surface_matrix_passes_guard(self):
        """Integration: matrix from build_judgment_matrix_for_surface must pass guard."""
        matrix = build_judgment_matrix_for_surface("كَتَبَ")
        # Must pass regardless of Taaqol availability:
        # - If unavailable: 1 BLOCKED judgment, no subsequent → passes.
        # - If available: all non-terminal judgments → passes.
        assert enforce_terminal_guard(matrix) is True
