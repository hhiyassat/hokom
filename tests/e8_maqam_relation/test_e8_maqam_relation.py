"""
E8 Maqam Context Boundary + Relation Candidate Tests — T_E8_*

Tests for:
    maqam_context_adapter.py:
        - build_maqam_context_boundary() — PR-D1.2 MaqamContextBoundaryVerdict
        - build_maqam_from_surface() — E7+E8 chain

    relation_candidate_adapter.py:
        - build_relation_candidate() — PR-19 RelationVerdict
        - build_e8_relation_from_surfaces() — E6+E8 full chain

Constitutional gates verified:
    G_E8_01: Fail-closed on Python 3.10 (all functions return None)
    G_E8_02: MaqamContextBoundaryVerdict PROVEN for corpus tokens on Python 3.12+
    G_E8_03: MaqamContextFrame fields correct on Python 3.12+
    G_E8_04: RelationVerdict COMPOSED for corpus ISM pairs on Python 3.12+
    G_E8_05: Role re-gating enforced (inadmissible role → None) on Python 3.12+
    G_E8_06: Module invariants pass on Python 3.10+

VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
Phase: E8 — MAQAM_CONTEXT_BOUNDARY + RELATION_CANDIDATE
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.maqam_context_adapter import (  # noqa: E402
    _E7_AVAILABLE,
    _MAQAM_CONTEXT_AVAILABLE,
    _VENDOR_SHA as _MCA_VENDOR_SHA,
    build_maqam_context_boundary,
    build_maqam_from_surface,
)
from pipeline.taaqol_integration.weight_layer.relation_candidate_adapter import (  # noqa: E402
    _E7_AVAILABLE as _RCA_E7_AVAILABLE,
    _RELATION_AVAILABLE,
    _VENDOR_SHA as _RCA_VENDOR_SHA,
    build_e8_relation_from_surfaces,
    build_relation_candidate,
)

REQUIRES_312 = pytest.mark.skipif(
    not _MAQAM_CONTEXT_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)

# Corpus ISM tokens (token_surface, root_letters)
_CORPUS_ISM = [
    ("دَيْنٍ",        "دين"),
    ("كَاتِبٌ",      "كتب"),
    ("شَهِيدَيْنِ",  "شهد"),
    ("أَجَلٍ",       "أجل"),
]

# Two corpus ISM pairs for relation tests (governor, dependent)
_CORPUS_ISM_PAIRS = [
    (("دَيْنٍ", "دين"), ("كَاتِبٌ", "كتب")),
    (("أَجَلٍ", "أجل"), ("شَهِيدَيْنِ", "شهد")),
]


# ── G_E8_01: Fail-closed on Python 3.10 ──────────────────────────────────────


class TestT_E8_01_FailClosed:
    """G_E8_01: All E8 functions return None on Python 3.10 (vendor absent)."""

    def test_maqam_context_available_false_on_310(self):
        """_MAQAM_CONTEXT_AVAILABLE = False on Python 3.10."""
        if _MAQAM_CONTEXT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        assert _MAQAM_CONTEXT_AVAILABLE is False

    def test_relation_available_false_on_310(self):
        """_RELATION_AVAILABLE = False on Python 3.10."""
        if _RELATION_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        assert _RELATION_AVAILABLE is False

    def test_build_maqam_context_boundary_returns_none_on_310(self):
        """build_maqam_context_boundary returns None without vendor."""
        if _MAQAM_CONTEXT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_maqam_context_boundary(object(), "دَيْنٍ")
        assert result is None

    def test_build_maqam_context_boundary_none_verdict_returns_none(self):
        """None e7_slot_verdict → None (fail-closed)."""
        result = build_maqam_context_boundary(None, "دَيْنٍ")
        assert result is None

    def test_build_maqam_context_boundary_empty_surface_returns_none(self):
        """Empty token_surface → None (fail-closed)."""
        result = build_maqam_context_boundary(object(), "")
        assert result is None

    def test_build_maqam_from_surface_returns_none_on_310(self):
        """build_maqam_from_surface returns None without vendor."""
        if _MAQAM_CONTEXT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e8:t01:surface",
        )
        assert result is None

    def test_build_relation_candidate_returns_none_on_310(self):
        """build_relation_candidate returns None without vendor."""
        if _RELATION_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_relation_candidate(
            e6_binding_verdict_governor=object(),
            e6_binding_verdict_dependent=object(),
            relation_basis="test:nominal_sentence",
        )
        assert result is None

    def test_build_relation_candidate_none_inputs_returns_none(self):
        """None governor/dependent → None (fail-closed)."""
        result = build_relation_candidate(
            e6_binding_verdict_governor=None,
            e6_binding_verdict_dependent=None,
            relation_basis="test:nominal_sentence",
        )
        assert result is None

    def test_build_relation_candidate_empty_basis_returns_none(self):
        """Empty relation_basis → None (fail-closed)."""
        result = build_relation_candidate(
            e6_binding_verdict_governor=object(),
            e6_binding_verdict_dependent=object(),
            relation_basis="",
        )
        assert result is None

    def test_build_e8_relation_from_surfaces_returns_none_on_310(self):
        """build_e8_relation_from_surfaces returns None without vendor."""
        if _RELATION_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_e8_relation_from_surfaces(
            gov_token_surface="دَيْنٍ",
            gov_root_letters="دين",
            gov_segment_host="دَيْنٍ",
            gov_word_class="ISM",
            gov_trace_id="test:e8:t01:gov",
            dep_token_surface="كَاتِبٌ",
            dep_root_letters="كتب",
            dep_segment_host="كَاتِبٌ",
            dep_word_class="ISM",
            dep_trace_id="test:e8:t01:dep",
        )
        assert result is None

    def test_never_raises_on_310(self):
        """E8 functions never raise on Python 3.10."""
        if _MAQAM_CONTEXT_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        for fn, args, kwargs in [
            (build_maqam_context_boundary, (None, ""), {}),
            (build_maqam_context_boundary, (object(), ""), {}),
            (build_maqam_from_surface, (), {
                "token_surface": "", "root_letters": "",
                "segment_host": "", "word_class": "", "trace_id": "",
            }),
            (build_relation_candidate, (), {
                "e6_binding_verdict_governor": None,
                "e6_binding_verdict_dependent": None,
                "relation_basis": "",
            }),
            (build_e8_relation_from_surfaces, (), {
                "gov_token_surface": "", "gov_root_letters": "",
                "gov_segment_host": "", "gov_word_class": "", "gov_trace_id": "",
                "dep_token_surface": "", "dep_root_letters": "",
                "dep_segment_host": "", "dep_word_class": "", "dep_trace_id": "",
            }),
        ]:
            try:
                result = fn(*args, **kwargs)
                assert result is None
            except Exception as exc:
                pytest.fail(f"{fn.__name__} raised on 3.10: {exc}")


# ── G_E8_02: MaqamContextBoundaryVerdict PROVEN on Python 3.12+ ──────────────


class TestT_E8_02_MaqamContextOn312:
    """G_E8_02: build_maqam_from_surface produces PROVEN MaqamContextBoundaryVerdict."""

    @REQUIRES_312
    def test_dayn_maqam_context_proven(self):
        """دَيْنٍ: full E7+E8 chain produces PROVEN MaqamContextBoundaryVerdict."""
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e8:t02:dayn",
        )
        assert result is not None, "E8 chain failed for دَيْنٍ — unexpected None"
        assert "PROVEN" in str(result.verdict_state), (
            f"Expected PROVEN, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_proven_verdict_carries_maqam_context_frame(self):
        """PROVEN verdict carries a MaqamContextFrame (not None)."""
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t02:frame",
        )
        assert result is not None
        assert result.candidate is not None, "PROVEN verdict must carry MaqamContextFrame"
        assert type(result.candidate).__name__ == "MaqamContextFrame", (
            f"Expected MaqamContextFrame, got {type(result.candidate).__name__}"
        )

    @REQUIRES_312
    @pytest.mark.parametrize("token,root", _CORPUS_ISM)
    def test_corpus_ism_all_maqam_proven(self, token, root):
        """All corpus ISM tokens produce PROVEN MaqamContextBoundaryVerdict."""
        result = build_maqam_from_surface(
            token_surface=token,
            root_letters=root,
            segment_host=token,
            word_class="ISM",
            trace_id=f"test:e8:t02:corpus:{token}",
        )
        assert result is not None, f"E8 chain failed for {token!r}"
        assert "PROVEN" in str(result.verdict_state), (
            f"Token {token!r}: expected PROVEN, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_none_e7_verdict_returns_none(self):
        """None e7_slot_verdict → None (fail-closed gate)."""
        result = build_maqam_context_boundary(None, "دَيْنٍ")
        assert result is None

    @REQUIRES_312
    def test_empty_surface_returns_none(self):
        """Empty token_surface → None (fail-closed gate)."""
        result = build_maqam_context_boundary(object(), "")
        assert result is None


# ── G_E8_03: MaqamContextFrame fields correct on Python 3.12+ ────────────────


class TestT_E8_03_MaqamContextFrameFieldsOn312:
    """G_E8_03: MaqamContextFrame fields are correctly populated."""

    @REQUIRES_312
    def test_semantic_slot_frame_ref_non_empty(self):
        """MaqamContextFrame.semantic_slot_frame_ref is non-empty string."""
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t03:ref",
        )
        assert result is not None
        frame = result.candidate
        assert isinstance(frame.semantic_slot_frame_ref, str), (
            "semantic_slot_frame_ref must be a str"
        )
        assert frame.semantic_slot_frame_ref.strip(), (
            "semantic_slot_frame_ref must be non-empty"
        )

    @REQUIRES_312
    def test_discourse_domain_is_lughawi(self):
        """MaqamContextFrame.discourse_domain.domain_type is LUGHAWI (default)."""
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t03:domain",
        )
        assert result is not None
        frame = result.candidate
        assert "LUGHAWI" in str(frame.discourse_domain.domain_type), (
            f"Expected LUGHAWI, got {frame.discourse_domain.domain_type!r}"
        )

    @REQUIRES_312
    def test_maqam_context_has_11_residuals(self):
        """MaqamContextFrame carries 11 deferred EXPLANATORY residuals."""
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t03:residuals",
        )
        assert result is not None
        frame = result.candidate
        assert len(frame.residuals) == 11, (
            f"Expected 11 residuals, got {len(frame.residuals)}"
        )

    @REQUIRES_312
    def test_no_blocking_residuals(self):
        """MaqamContextFrame has no BLOCKING or HIDDEN_FORBIDDEN residuals."""
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t03:noblocking",
        )
        assert result is not None
        frame = result.candidate
        for r in frame.residuals:
            assert "BLOCKING" not in str(r.kind), (
                f"Unexpected BLOCKING residual: {r.name!r}"
            )
            assert "HIDDEN_FORBIDDEN" not in str(r.kind), (
                f"Unexpected HIDDEN_FORBIDDEN residual: {r.name!r}"
            )

    @REQUIRES_312
    def test_trace_ref_contains_proven(self):
        """MaqamContextFrame.trace_ref contains 'proven'."""
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t03:trace",
        )
        assert result is not None
        frame = result.candidate
        assert "proven" in frame.trace_ref, (
            f"Expected 'proven' in trace_ref, got {frame.trace_ref!r}"
        )

    @REQUIRES_312
    def test_usage_register_is_haqiqi(self):
        """MaqamContextFrame.usage_register.register_type is HAQIQI (default)."""
        result = build_maqam_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t03:register",
        )
        assert result is not None
        frame = result.candidate
        assert "HAQIQI" in str(frame.usage_register.register_type), (
            f"Expected HAQIQI, got {frame.usage_register.register_type!r}"
        )


# ── G_E8_04: RelationVerdict COMPOSED on Python 3.12+ ────────────────────────


class TestT_E8_04_RelationCandidateOn312:
    """G_E8_04: build_e8_relation_from_surfaces produces COMPOSED RelationVerdict."""

    @REQUIRES_312
    def test_dayn_katib_relation_composed(self):
        """دَيْنٍ (MUBTADA) + كَاتِبٌ (KHABAR): RelationVerdict is COMPOSED."""
        result = build_e8_relation_from_surfaces(
            gov_token_surface="دَيْنٍ",
            gov_root_letters="دين",
            gov_segment_host="دَيْنٍ",
            gov_word_class="ISM",
            gov_trace_id="test:e8:t04:gov:dayn",
            dep_token_surface="كَاتِبٌ",
            dep_root_letters="كتب",
            dep_segment_host="كَاتِبٌ",
            dep_word_class="ISM",
            dep_trace_id="test:e8:t04:dep:katib",
            governor_role_claim="MUBTADA",
            dependent_role_claim="KHABAR",
            relation_basis="nominal_sentence/ayat_al_dayn",
        )
        assert result is not None, (
            "RelationCandidate chain failed for دَيْنٍ+كَاتِبٌ — unexpected None"
        )
        assert "COMPOSED" in str(result.verdict_state), (
            f"Expected COMPOSED, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_composed_verdict_carries_relation_candidate(self):
        """COMPOSED verdict carries a RelationCandidate (not None)."""
        result = build_e8_relation_from_surfaces(
            gov_token_surface="دَيْنٍ",
            gov_root_letters="دين",
            gov_segment_host="دَيْنٍ",
            gov_word_class="ISM",
            gov_trace_id="test:e8:t04:cand:gov",
            dep_token_surface="كَاتِبٌ",
            dep_root_letters="كتب",
            dep_segment_host="كَاتِبٌ",
            dep_word_class="ISM",
            dep_trace_id="test:e8:t04:cand:dep",
            governor_role_claim="MUBTADA",
            dependent_role_claim="KHABAR",
            relation_basis="nominal_sentence/debt_and_scribe",
        )
        assert result is not None
        assert result.candidate is not None, "COMPOSED verdict must carry RelationCandidate"
        assert type(result.candidate).__name__ == "RelationCandidate", (
            f"Expected RelationCandidate, got {type(result.candidate).__name__}"
        )

    @REQUIRES_312
    def test_relation_candidate_governor_role_correct(self):
        """RelationCandidate.governor_role == governor_role_claim."""
        result = build_e8_relation_from_surfaces(
            gov_token_surface="دَيْنٍ",
            gov_root_letters="دين",
            gov_segment_host="دَيْنٍ",
            gov_word_class="ISM",
            gov_trace_id="test:e8:t04:role:gov",
            dep_token_surface="كَاتِبٌ",
            dep_root_letters="كتب",
            dep_segment_host="كَاتِبٌ",
            dep_word_class="ISM",
            dep_trace_id="test:e8:t04:role:dep",
            governor_role_claim="MUBTADA",
            dependent_role_claim="KHABAR",
            relation_basis="nominal_sentence/role_test",
        )
        assert result is not None
        candidate = result.candidate
        assert candidate.governor_role == "MUBTADA", (
            f"governor_role={candidate.governor_role!r} != 'MUBTADA'"
        )
        assert candidate.dependent_role == "KHABAR", (
            f"dependent_role={candidate.dependent_role!r} != 'KHABAR'"
        )

    @REQUIRES_312
    def test_trace_ref_contains_composed_and_both_identities(self):
        """RelationCandidate.trace_ref contains 'composed' and both unit identities."""
        result = build_e8_relation_from_surfaces(
            gov_token_surface="دَيْنٍ",
            gov_root_letters="دين",
            gov_segment_host="دَيْنٍ",
            gov_word_class="ISM",
            gov_trace_id="test:e8:t04:trace:gov",
            dep_token_surface="كَاتِبٌ",
            dep_root_letters="كتب",
            dep_segment_host="كَاتِبٌ",
            dep_word_class="ISM",
            dep_trace_id="test:e8:t04:trace:dep",
            governor_role_claim="MUBTADA",
            dependent_role_claim="KHABAR",
            relation_basis="nominal_sentence/trace_test",
        )
        assert result is not None
        # trace_ref = "prove_relation_candidate/composed/{gov_id}+{dep_id}"
        assert "composed" in result.candidate.trace_ref, (
            f"Expected 'composed' in trace_ref, got {result.candidate.trace_ref!r}"
        )

    @REQUIRES_312
    @pytest.mark.parametrize("gov,dep", _CORPUS_ISM_PAIRS)
    def test_corpus_ism_pairs_all_composed(self, gov, dep):
        """All corpus ISM pairs produce COMPOSED RelationVerdict."""
        gov_surface, gov_root = gov
        dep_surface, dep_root = dep
        result = build_e8_relation_from_surfaces(
            gov_token_surface=gov_surface,
            gov_root_letters=gov_root,
            gov_segment_host=gov_surface,
            gov_word_class="ISM",
            gov_trace_id=f"test:e8:t04:pair:gov:{gov_surface}",
            dep_token_surface=dep_surface,
            dep_root_letters=dep_root,
            dep_segment_host=dep_surface,
            dep_word_class="ISM",
            dep_trace_id=f"test:e8:t04:pair:dep:{dep_surface}",
            governor_role_claim="MUBTADA",
            dependent_role_claim="KHABAR",
            relation_basis=f"nominal_sentence/{gov_surface}+{dep_surface}",
        )
        assert result is not None, (
            f"RelationCandidate failed for {gov_surface!r}+{dep_surface!r}"
        )
        assert "COMPOSED" in str(result.verdict_state), (
            f"Pair {gov_surface!r}+{dep_surface!r}: expected COMPOSED, "
            f"got {result.verdict_state!r}"
        )


# ── G_E8_05: Role re-gating enforced on Python 3.12+ ─────────────────────────


class TestT_E8_05_RoleRegatingOn312:
    """G_E8_05: prove_relation_candidate refuses inadmissible/blocked roles."""

    @REQUIRES_312
    def test_inadmissible_governor_role_returns_none(self):
        """An inadmissible governor_role_claim → None (vendor refuses)."""
        from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
            build_e6_from_surface,
        )
        e6_gov = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t05:gov:inadmissible",
        )
        e6_dep = build_e6_from_surface(
            token_surface="كَاتِبٌ", root_letters="كتب",
            segment_host="كَاتِبٌ", word_class="ISM",
            trace_id="test:e8:t05:dep:inadmissible",
        )
        assert e6_gov is not None, "E6 chain failed for governor"
        assert e6_dep is not None, "E6 chain failed for dependent"
        # "FIL_MUTLI" is an FI3L role, inadmissible for ISM governor
        result = build_relation_candidate(
            e6_binding_verdict_governor=e6_gov,
            e6_binding_verdict_dependent=e6_dep,
            governor_word_class="ISM",
            dependent_word_class="ISM",
            governor_role_claim="FIL_MUTLI",  # FI3L role — inadmissible for ISM
            dependent_role_claim="KHABAR",
            relation_basis="nominal_sentence/inadmissible_test",
        )
        assert result is None, (
            "Expected None for inadmissible governor_role_claim FIL_MUTLI on ISM unit"
        )

    @REQUIRES_312
    def test_inadmissible_dependent_role_returns_none(self):
        """An inadmissible dependent_role_claim → None (vendor refuses)."""
        from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
            build_e6_from_surface,
        )
        e6_gov = build_e6_from_surface(
            token_surface="دَيْنٍ", root_letters="دين",
            segment_host="دَيْنٍ", word_class="ISM",
            trace_id="test:e8:t05:gov2",
        )
        e6_dep = build_e6_from_surface(
            token_surface="كَاتِبٌ", root_letters="كتب",
            segment_host="كَاتِبٌ", word_class="ISM",
            trace_id="test:e8:t05:dep2",
        )
        assert e6_gov is not None
        assert e6_dep is not None
        # "FIL_MAJHOOL" is an FI3L role, inadmissible for ISM dependent
        result = build_relation_candidate(
            e6_binding_verdict_governor=e6_gov,
            e6_binding_verdict_dependent=e6_dep,
            governor_word_class="ISM",
            dependent_word_class="ISM",
            governor_role_claim="MUBTADA",
            dependent_role_claim="FIL_MAJHOOL",  # FI3L role — inadmissible for ISM
            relation_basis="nominal_sentence/inadmissible_dep_test",
        )
        assert result is None, (
            "Expected None for inadmissible dependent_role_claim FIL_MAJHOOL on ISM unit"
        )

    @REQUIRES_312
    def test_empty_relation_basis_returns_none(self):
        """Empty relation_basis → None (fail-closed)."""
        result = build_relation_candidate(
            e6_binding_verdict_governor=object(),
            e6_binding_verdict_dependent=object(),
            governor_role_claim="MUBTADA",
            dependent_role_claim="KHABAR",
            relation_basis="",
        )
        assert result is None


# ── G_E8_06: Module invariants pass on Python 3.10+ ──────────────────────────


class TestT_E8_06_ModuleInvariants:
    """G_E8_06: Module-level invariants hold on Python 3.10 and 3.12+."""

    def test_mca_vendor_sha_correct(self):
        """maqam_context_adapter._VENDOR_SHA is canonical."""
        assert _MCA_VENDOR_SHA == "05c6668dfb95d9238cff5df1d8bc73d0664bccb3", (
            f"VENDOR_SHA mismatch: {_MCA_VENDOR_SHA!r}"
        )

    def test_rca_vendor_sha_correct(self):
        """relation_candidate_adapter._VENDOR_SHA is canonical."""
        assert _RCA_VENDOR_SHA == "05c6668dfb95d9238cff5df1d8bc73d0664bccb3", (
            f"VENDOR_SHA mismatch: {_RCA_VENDOR_SHA!r}"
        )

    def test_maqam_context_available_is_bool(self):
        """_MAQAM_CONTEXT_AVAILABLE is a bool."""
        assert isinstance(_MAQAM_CONTEXT_AVAILABLE, bool)

    def test_relation_available_is_bool(self):
        """_RELATION_AVAILABLE is a bool."""
        assert isinstance(_RELATION_AVAILABLE, bool)

    def test_e7_available_is_bool_mca(self):
        """maqam_context_adapter._E7_AVAILABLE is a bool."""
        assert isinstance(_E7_AVAILABLE, bool)

    def test_e7_available_is_bool_rca(self):
        """relation_candidate_adapter._E7_AVAILABLE is a bool."""
        assert isinstance(_RCA_E7_AVAILABLE, bool)

    def test_e7_available_true(self):
        """_E7_AVAILABLE = True (E7 adapters importable on 3.10+)."""
        assert _E7_AVAILABLE is True
        assert _RCA_E7_AVAILABLE is True

    def test_build_maqam_context_boundary_callable(self):
        """build_maqam_context_boundary is callable."""
        assert callable(build_maqam_context_boundary)

    def test_build_maqam_from_surface_callable(self):
        """build_maqam_from_surface is callable."""
        assert callable(build_maqam_from_surface)

    def test_build_relation_candidate_callable(self):
        """build_relation_candidate is callable."""
        assert callable(build_relation_candidate)

    def test_build_e8_relation_from_surfaces_callable(self):
        """build_e8_relation_from_surfaces is callable."""
        assert callable(build_e8_relation_from_surfaces)

    def test_both_adapters_import_cleanly(self):
        """Both E8 adapters import without error on Python 3.10+."""
        import importlib
        try:
            importlib.import_module(
                "pipeline.taaqol_integration.weight_layer.maqam_context_adapter"
            )
            importlib.import_module(
                "pipeline.taaqol_integration.weight_layer.relation_candidate_adapter"
            )
        except ImportError as exc:
            pytest.fail(f"E8 adapter import failed: {exc}")
