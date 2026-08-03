"""
E6 Verbal Madlul Tests — T_E6_*

Tests for verbal_madlul_adapter.py:
    - build_verbal_madlul_candidate()  — prove_verbal_madlul() wrapper
    - build_dal_madlul_binding()       — bind_dal_madlul() wrapper (PR-17)
    - build_e6_chain_from_dal_verdict() — E5→E6 chain
    - build_e6_from_surface()          — E4B+E4C+E5+E6 full chain
    - Module invariants (run at import time)

Constitutional gates verified:
    G_E6_01: Fail-closed on Python 3.10 (vendor absent → None)
    G_E6_02: build_e6_from_surface → BOUND on Python 3.12+
    G_E6_03: DalMadlulBindingCandidate fields correct on Python 3.12+
    G_E6_04: prove_verbal_madlul refusals (empty wad, wrong type)
    G_E6_05: bind_dal_madlul identity constraint enforced
    G_E6_06: Module invariants and implementation state

VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
Phase: E6 — VERBAL MADLUL
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (  # noqa: E402
    _VERBAL_MADLUL_AVAILABLE,
    _E5_AVAILABLE,
    _VENDOR_SHA,
    build_verbal_madlul_candidate,
    build_dal_madlul_binding,
    build_e6_chain_from_dal_verdict,
    build_e6_from_surface,
)

REQUIRES_312 = pytest.mark.skipif(
    not _VERBAL_MADLUL_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)

_CORPUS_ISM = [
    ("دَيْنٍ",       "دين"),
    ("كَاتِبٌ",     "كتب"),
    ("شَهِيدَيْنِ", "شهد"),
    ("أَجَلٍ",      "أجل"),
]


# ── G_E6_01: Fail-closed on Python 3.10 ──────────────────────────────────────

class TestT_E6_01_FailClosed:
    """G_E6_01: E6 returns None on Python 3.10 (vendor absent)."""

    def test_build_verbal_madlul_returns_none_on_310(self):
        if _VERBAL_MADLUL_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_verbal_madlul_candidate(
            dal_only_candidate=object(),
            wad_usage_boundary="dayn",
        )
        assert result is None

    def test_build_binding_returns_none_on_310(self):
        if _VERBAL_MADLUL_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_dal_madlul_binding(
            dal_only_candidate=object(),
            verbal_madlul_candidate=object(),
            registry_key="دَيْنٍ",
            trace_id="test:e6:t01:310",
        )
        assert result is None

    def test_build_chain_returns_none_on_310(self):
        if _VERBAL_MADLUL_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_e6_chain_from_dal_verdict(
            dal_boundary_verdict=object(),
            token_surface="دَيْنٍ",
            trace_id="test:e6:t01:chain_310",
        )
        assert result is None

    def test_build_from_surface_returns_none_on_310(self):
        if _VERBAL_MADLUL_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_e6_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e6:t01:surface_310",
        )
        assert result is None

    def test_never_raises_on_310(self):
        if _VERBAL_MADLUL_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        fns_args = [
            (build_verbal_madlul_candidate, (None, "")),
            (build_dal_madlul_binding, (None, None, "", "")),
            (build_e6_chain_from_dal_verdict, (None,)),
            (build_e6_from_surface, ("", "", "", "", "")),
        ]
        for fn, args in fns_args:
            try:
                result = fn(*args)
                assert result is None
            except Exception as exc:
                pytest.fail(f"{fn.__name__} raised on 3.10: {exc}")

    def test_verbal_madlul_available_false_on_310(self):
        if _VERBAL_MADLUL_AVAILABLE:
            pytest.skip("Python 3.12+")
        assert _VERBAL_MADLUL_AVAILABLE is False

    def test_e5_available_true(self):
        assert _E5_AVAILABLE is True

    def test_vendor_sha_constant(self):
        assert _VENDOR_SHA == "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

    def test_fail_closed_empty_token_surface(self):
        result = build_e6_chain_from_dal_verdict(
            dal_boundary_verdict=None,
            token_surface="",
            trace_id="test:e6:t01:empty_surface",
        )
        assert result is None

    def test_fail_closed_empty_trace_id(self):
        result = build_e6_chain_from_dal_verdict(
            dal_boundary_verdict=None,
            token_surface="دَيْنٍ",
            trace_id="",
        )
        assert result is None


# ── G_E6_02: Full E4B+E4C+E5+E6 chain → BOUND on Python 3.12+ ───────────────

class TestT_E6_02_BoundOn312:
    """G_E6_02: build_e6_from_surface produces BOUND DalMadlulBindingVerdict on 3.12+."""

    @REQUIRES_312
    def test_dayn_produces_bound_verdict(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e6:t02:dayn",
        )
        assert result is not None, "E6 chain failed for دَيْنٍ — unexpected None"
        assert "BOUND" in str(result.verdict_state), (
            f"Expected BOUND, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_bound_verdict_has_candidate(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e6:t02:candidate",
        )
        assert result is not None
        assert result.candidate is not None, "BOUND verdict must carry a candidate"
        assert type(result.candidate).__name__ == "DalMadlulBindingCandidate", (
            f"Expected DalMadlulBindingCandidate, got {type(result.candidate).__name__}"
        )

    @REQUIRES_312
    @pytest.mark.parametrize("token,root", _CORPUS_ISM)
    def test_corpus_ism_all_bound(self, token, root):
        result = build_e6_from_surface(
            token_surface=token,
            root_letters=root,
            segment_host=token,
            word_class="ISM",
            trace_id=f"test:e6:t02:corpus:{token}",
        )
        assert result is not None, f"E6 chain failed for {token!r}"
        assert "BOUND" in str(result.verdict_state), (
            f"Token {token!r}: expected BOUND, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_harf_returns_none(self):
        """HARF tokens return None (E4A guard fires before E6 even starts)."""
        result = build_e6_from_surface(
            token_surface="إِلَى",
            root_letters="",
            segment_host="إِلَى",
            word_class="HARF",
            trace_id="test:e6:t02:harf",
        )
        assert result is None, f"Expected None for HARF, got {result!r}"

    @REQUIRES_312
    def test_prove_verbal_madlul_step_proven(self):
        """Intermediate prove_verbal_madlul step produces PROVEN verdict."""
        from pipeline.taaqol_integration.weight_layer.dal_only_adapter import (
            build_dal_only_from_surface,
        )
        dal_verdict = build_dal_only_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e6:t02:prove_step",
        )
        assert dal_verdict is not None
        dal_only = dal_verdict.candidate

        verbal_verdict = build_verbal_madlul_candidate(
            dal_only_candidate=dal_only,
            wad_usage_boundary="دَيْنٍ",
        )
        assert verbal_verdict is not None, "prove_verbal_madlul failed"
        assert "PROVEN" in str(verbal_verdict.verdict_state), (
            f"Expected PROVEN, got {verbal_verdict.verdict_state!r}"
        )
        assert verbal_verdict.candidate is not None
        assert type(verbal_verdict.candidate).__name__ == "VerbalMadlulCandidate"


# ── G_E6_03: DalMadlulBindingCandidate fields ────────────────────────────────

class TestT_E6_03_BindingCandidateFields:
    """G_E6_03: DalMadlulBindingCandidate carries correct fields (Python 3.12+)."""

    @REQUIRES_312
    def test_dal_candidate_is_dal_only(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t03:dal_candidate",
        )
        assert result is not None
        assert type(result.candidate.dal_candidate).__name__ == "DalOnlyCandidate"

    @REQUIRES_312
    def test_madlul_candidate_is_verbal_madlul(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t03:madlul_candidate",
        )
        assert result is not None
        assert type(result.candidate.madlul_candidate).__name__ == "VerbalMadlulCandidate"

    @REQUIRES_312
    def test_identity_invariant_holds(self):
        """madlul_candidate.dal_only is dal_candidate (Python is-identity)."""
        result = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t03:identity",
        )
        assert result is not None
        cand = result.candidate
        assert cand.madlul_candidate.dal_only is cand.dal_candidate, (
            "Identity invariant violated: madlul.dal_only is not dal_candidate"
        )

    @REQUIRES_312
    def test_dal_registry_proof_found(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t03:dal_registry",
        )
        assert result is not None
        assert "FOUND" in str(result.candidate.dal_registry_proof.state)

    @REQUIRES_312
    def test_madlul_registry_proof_found(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t03:madlul_registry",
        )
        assert result is not None
        assert "FOUND" in str(result.candidate.madlul_registry_proof.state)

    @REQUIRES_312
    def test_binding_rank_is_candidate(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t03:rank",
        )
        assert result is not None
        # Python 3.12 changed IntEnum.__str__: str(Rank.CANDIDATE) == "2", not "CANDIDATE".
        assert result.candidate.binding_rank.name == "CANDIDATE", (
            f"binding_rank must be CANDIDATE, got {result.candidate.binding_rank!r} "
            f"(name={result.candidate.binding_rank.name!r})"
        )

    @REQUIRES_312
    def test_residuals_empty_tuple(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t03:residuals",
        )
        assert result is not None
        assert result.candidate.residuals == ()

    @REQUIRES_312
    def test_no_failure_code_on_bound(self):
        result = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t03:failure_code",
        )
        assert result is not None
        assert result.failure_code is None


# ── G_E6_04: prove_verbal_madlul refusals ────────────────────────────────────

class TestT_E6_04_VerbalMadlulRefusals:
    """G_E6_04: prove_verbal_madlul refuses invalid inputs (fail-closed)."""

    def test_none_dal_candidate_returns_none(self):
        result = build_verbal_madlul_candidate(
            dal_only_candidate=None,
            wad_usage_boundary="boundary",
        )
        assert result is None

    def test_string_dal_candidate_returns_none(self):
        result = build_verbal_madlul_candidate(
            dal_only_candidate="not_a_dal_candidate",
            wad_usage_boundary="boundary",
        )
        assert result is None

    def test_object_dal_candidate_returns_none(self):
        result = build_verbal_madlul_candidate(
            dal_only_candidate=object(),
            wad_usage_boundary="boundary",
        )
        assert result is None

    def test_empty_wad_usage_boundary_returns_none(self):
        result = build_verbal_madlul_candidate(
            dal_only_candidate=object(),
            wad_usage_boundary="",
        )
        assert result is None

    def test_whitespace_wad_usage_boundary_returns_none(self):
        result = build_verbal_madlul_candidate(
            dal_only_candidate=object(),
            wad_usage_boundary="   ",
        )
        assert result is None


# ── G_E6_05: bind_dal_madlul identity constraint ─────────────────────────────

class TestT_E6_05_BindingIdentityConstraint:
    """G_E6_05: bind_dal_madlul identity constraint is enforced (fail-closed)."""

    def test_empty_registry_key_returns_none(self):
        result = build_dal_madlul_binding(
            dal_only_candidate=object(),
            verbal_madlul_candidate=object(),
            registry_key="",
            trace_id="test:e6:t05:empty_key",
        )
        assert result is None

    def test_empty_trace_id_returns_none(self):
        result = build_dal_madlul_binding(
            dal_only_candidate=object(),
            verbal_madlul_candidate=object(),
            registry_key="key",
            trace_id="",
        )
        assert result is None

    def test_none_candidates_return_none(self):
        result = build_dal_madlul_binding(
            dal_only_candidate=None,
            verbal_madlul_candidate=None,
            registry_key="key",
            trace_id="test:e6:t05:none",
        )
        assert result is None

    @REQUIRES_312
    def test_identity_mismatch_returns_none(self):
        """Two separately constructed DalOnlyCandidate instances → identity mismatch → None."""
        from pipeline.taaqol_integration.weight_layer.dal_only_adapter import (
            build_dal_only_from_surface,
        )
        dal_verdict_1 = build_dal_only_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t05:id1",
        )
        dal_verdict_2 = build_dal_only_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e6:t05:id2",
        )
        assert dal_verdict_1 is not None and dal_verdict_2 is not None
        dal_only_1 = dal_verdict_1.candidate
        dal_only_2 = dal_verdict_2.candidate
        # Prove verbal madlul from instance 1
        verbal_verdict = build_verbal_madlul_candidate(
            dal_only_candidate=dal_only_1,
            wad_usage_boundary="دَيْنٍ",
        )
        assert verbal_verdict is not None
        verbal_candidate = verbal_verdict.candidate
        # Attempt binding with instance 2 (different object) → must fail
        result = build_dal_madlul_binding(
            dal_only_candidate=dal_only_2,  # wrong instance
            verbal_madlul_candidate=verbal_candidate,
            registry_key="دَيْنٍ",
            trace_id="test:e6:t05:mismatch",
        )
        assert result is None, (
            "Expected None for identity mismatch, got BOUND — "
            "madlul.dal_only is not dal_candidate should be enforced"
        )


# ── G_E6_06: Module invariants ────────────────────────────────────────────────

class TestT_E6_06_ModuleInvariants:
    """G_E6_06: Module invariants hold at import time."""

    def test_module_imports_without_error(self):
        assert True  # import at top of file already confirmed

    def test_vendor_sha_matches_pinned(self):
        assert _VENDOR_SHA == "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

    def test_all_functions_callable(self):
        assert callable(build_verbal_madlul_candidate)
        assert callable(build_dal_madlul_binding)
        assert callable(build_e6_chain_from_dal_verdict)
        assert callable(build_e6_from_surface)

    def test_verbal_madlul_available_is_bool(self):
        assert isinstance(_VERBAL_MADLUL_AVAILABLE, bool)

    def test_e5_available_is_bool(self):
        assert isinstance(_E5_AVAILABLE, bool)

    def test_e5_available_true(self):
        assert _E5_AVAILABLE is True
