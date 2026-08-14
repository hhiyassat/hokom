"""
E5 Dal-Only Candidate Tests — T_E5_*

Tests for dal_only_adapter.py:
    - build_dal_only_candidate() — prove_dal() wrapper
    - build_dal_only_from_surface() — E4B+E4C+E5 full chain
    - Module invariants (run at import time)

Constitutional gates verified:
    G_E5_01: Fail-closed on Python 3.10 (vendor absent → None)
    G_E5_02: build_dal_only_from_surface E2E chain → PROVEN on Python 3.12+
    G_E5_03: DalOnlyCandidate fields correct on Python 3.12+
    G_E5_04: prove_dal refuses non-LicensingBoundaryVerdict input
    G_E5_05: Implementation state + module invariants

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E5 — DAL-ONLY CANDIDATE
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.dal_only_adapter import (  # noqa: E402
    _DAL_ONLY_AVAILABLE,
    _E4C_AVAILABLE,
    _VENDOR_SHA,
    build_dal_only_candidate,
    build_dal_only_from_surface,
)

REQUIRES_312 = pytest.mark.skipif(
    not _DAL_ONLY_AVAILABLE,
    reason="Requires Python 3.12+ (vendor StrEnum / taaqqul_slot_geometry)",
)

_CORPUS_ISM = [
    ("دَيْنٍ",      "دين"),
    ("كَاتِبٌ",    "كتب"),
    ("شَهِيدَيْنِ","شهد"),
    ("أَجَلٍ",     "أجل"),
]


# ── G_E5_01: Fail-closed on Python 3.10 ──────────────────────────────────────

class TestT_E5_01_FailClosed:
    """G_E5_01: E5 returns None on Python 3.10 (vendor absent)."""

    def test_build_dal_only_candidate_returns_none_on_310(self):
        """Without vendor: build_dal_only_candidate returns None."""
        if _DAL_ONLY_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_dal_only_candidate(
            licensing_verdict=object(),
            token_surface="دَيْنٍ",
            trace_id="test:e5:t01:310",
        )
        assert result is None

    def test_build_dal_only_from_surface_returns_none_on_310(self):
        """Without vendor: build_dal_only_from_surface returns None."""
        if _DAL_ONLY_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = build_dal_only_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e5:t01:surface_310",
        )
        assert result is None

    def test_never_raises_on_310(self):
        """E5 never raises on Python 3.10."""
        if _DAL_ONLY_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        for fn, args in [
            (build_dal_only_candidate, (None, "", "")),
            (build_dal_only_from_surface, ("", "", "", "", "")),
        ]:
            try:
                result = fn(*args)
                assert result is None
            except Exception as exc:
                pytest.fail(f"{fn.__name__} raised on 3.10: {exc}")

    def test_dal_only_available_false_on_310(self):
        """_DAL_ONLY_AVAILABLE = False on Python 3.10."""
        if _DAL_ONLY_AVAILABLE:
            pytest.skip("Python 3.12+")
        assert _DAL_ONLY_AVAILABLE is False

    def test_e4c_available_true(self):
        """_E4C_AVAILABLE = True (licensing_boundary_adapter importable)."""
        assert _E4C_AVAILABLE is True

    def test_vendor_sha_constant(self):
        """_VENDOR_SHA matches pinned constitutional SHA."""
        assert _VENDOR_SHA == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

    def test_fail_closed_on_empty_surface(self):
        """Empty token_surface → None (fail-closed, no crash)."""
        result = build_dal_only_candidate(
            licensing_verdict=object(),
            token_surface="",
            trace_id="test:e5:t01:empty_surface",
        )
        assert result is None

    def test_fail_closed_on_empty_trace_id(self):
        """Empty trace_id → None (fail-closed, no crash)."""
        result = build_dal_only_candidate(
            licensing_verdict=object(),
            token_surface="دَيْنٍ",
            trace_id="",
        )
        assert result is None


# ── G_E5_02: Full E4B+E4C+E5 chain → PROVEN on Python 3.12+ ─────────────────

class TestT_E5_02_ProvenOn312:
    """G_E5_02: build_dal_only_from_surface produces PROVEN DalBoundaryVerdict on Python 3.12+."""

    @REQUIRES_312
    def test_dayn_produces_proven_verdict(self):
        """دَيْنٍ: full E4B+E4C+E5 chain produces PROVEN DalBoundaryVerdict."""
        result = build_dal_only_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e5:t02:dayn",
        )
        assert result is not None, "E5 chain failed for دَيْنٍ — unexpected None"
        verdict_state = str(result.verdict_state)
        assert "PROVEN" in verdict_state, (
            f"Expected PROVEN, got verdict_state={verdict_state!r}"
        )

    @REQUIRES_312
    def test_proven_verdict_has_candidate(self):
        """PROVEN DalBoundaryVerdict carries a DalOnlyCandidate."""
        result = build_dal_only_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e5:t02:candidate",
        )
        assert result is not None
        assert result.candidate is not None, "PROVEN verdict must carry a DalOnlyCandidate"
        assert type(result.candidate).__name__ == "DalOnlyCandidate", (
            f"Expected DalOnlyCandidate, got {type(result.candidate).__name__}"
        )

    @REQUIRES_312
    @pytest.mark.parametrize("token,root", _CORPUS_ISM)
    def test_corpus_ism_all_proven(self, token, root):
        """All corpus ISM tokens produce PROVEN DalBoundaryVerdict via full chain."""
        result = build_dal_only_from_surface(
            token_surface=token,
            root_letters=root,
            segment_host=token,
            word_class="ISM",
            trace_id=f"test:e5:t02:corpus:{token}",
        )
        assert result is not None, f"E5 chain failed for {token!r}"
        assert "PROVEN" in str(result.verdict_state), (
            f"Token {token!r}: expected PROVEN, got {result.verdict_state!r}"
        )

    @REQUIRES_312
    def test_harf_returns_none(self):
        """HARF tokens return None from build_dal_only_from_surface (E4A guard)."""
        result = build_dal_only_from_surface(
            token_surface="إِلَى",
            root_letters="",
            segment_host="إِلَى",
            word_class="HARF",
            trace_id="test:e5:t02:harf",
        )
        assert result is None, (
            f"Expected None for HARF, got {result!r}"
        )

    @REQUIRES_312
    def test_wrong_licensing_verdict_type_returns_none(self):
        """build_dal_only_candidate refuses non-LicensingBoundaryVerdict."""
        result = build_dal_only_candidate(
            licensing_verdict=object(),
            token_surface="دَيْنٍ",
            trace_id="test:e5:t02:wrong_type",
        )
        assert result is None, "Expected None for wrong verdict type"


# ── G_E5_03: DalOnlyCandidate fields ─────────────────────────────────────────

class TestT_E5_03_DalOnlyCandidateFields:
    """G_E5_03: DalOnlyCandidate carries correct fields (Python 3.12+)."""

    @REQUIRES_312
    def test_signifier_identity_is_token_surface(self):
        """DalOnlyCandidate.signifier_identity == token_surface."""
        token = "دَيْنٍ"
        result = build_dal_only_from_surface(
            token_surface=token, root_letters="دين", segment_host=token,
            word_class="ISM", trace_id="test:e5:t03:identity",
        )
        assert result is not None
        assert result.candidate.signifier_identity == token, (
            f"signifier_identity={result.candidate.signifier_identity!r} != {token!r}"
        )

    @REQUIRES_312
    def test_phonetic_trace_ref_is_trace_id(self):
        """DalOnlyCandidate.phonetic_trace_ref == trace_id."""
        trace = "test:e5:t03:phonetic"
        result = build_dal_only_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id=trace,
        )
        assert result is not None
        assert result.candidate.phonetic_trace_ref == trace, (
            f"phonetic_trace_ref={result.candidate.phonetic_trace_ref!r} != {trace!r}"
        )

    @REQUIRES_312
    def test_prior_licensing_verdict_set(self):
        """DalOnlyCandidate.prior_licensing_verdict is a LicensingBoundaryVerdict."""
        result = build_dal_only_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e5:t03:prior",
        )
        assert result is not None
        assert result.candidate.prior_licensing_verdict is not None
        assert type(result.candidate.prior_licensing_verdict).__name__ == "LicensingBoundaryVerdict", (
            f"Expected LicensingBoundaryVerdict, got "
            f"{type(result.candidate.prior_licensing_verdict).__name__}"
        )

    @REQUIRES_312
    def test_dal_rank_is_candidate(self):
        """DalOnlyCandidate.dal_rank == Rank.CANDIDATE (birth ceiling)."""
        result = build_dal_only_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e5:t03:rank",
        )
        assert result is not None
        # Python 3.12 changed IntEnum.__str__: str(Rank.CANDIDATE) == "2", not "CANDIDATE".
        # Use .name for string check; identity check is semantically stronger.
        assert result.candidate.dal_rank.name == "CANDIDATE", (
            f"dal_rank should be CANDIDATE, got {result.candidate.dal_rank!r} "
            f"(name={result.candidate.dal_rank.name!r})"
        )

    @REQUIRES_312
    def test_residuals_empty_tuple(self):
        """DalOnlyCandidate.residuals == () (clean chain, no fiqhi residuals)."""
        result = build_dal_only_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e5:t03:residuals",
        )
        assert result is not None
        assert result.candidate.residuals == (), (
            f"Expected empty residuals, got {result.candidate.residuals!r}"
        )

    @REQUIRES_312
    def test_no_failure_code_on_proven(self):
        """PROVEN DalBoundaryVerdict has failure_code=None."""
        result = build_dal_only_from_surface(
            token_surface="دَيْنٍ", root_letters="دين", segment_host="دَيْنٍ",
            word_class="ISM", trace_id="test:e5:t03:failure_code",
        )
        assert result is not None
        assert result.failure_code is None, (
            f"PROVEN verdict must not carry failure_code: {result.failure_code!r}"
        )


# ── G_E5_04: prove_dal refusals ───────────────────────────────────────────────

class TestT_E5_04_ProvedalRefusals:
    """G_E5_04: prove_dal refuses invalid inputs (fail-closed)."""

    def test_none_licensing_verdict_returns_none(self):
        """None as licensing_verdict → None (fail-closed)."""
        result = build_dal_only_candidate(
            licensing_verdict=None,
            token_surface="دَيْنٍ",
            trace_id="test:e5:t04:none",
        )
        assert result is None

    def test_string_licensing_verdict_returns_none(self):
        """str as licensing_verdict → None (fail-closed)."""
        result = build_dal_only_candidate(
            licensing_verdict="not_a_verdict",
            token_surface="دَيْنٍ",
            trace_id="test:e5:t04:str",
        )
        assert result is None

    def test_whitespace_token_surface_returns_none(self):
        """Whitespace token_surface → None."""
        result = build_dal_only_candidate(
            licensing_verdict=object(),
            token_surface="   ",
            trace_id="test:e5:t04:whitespace",
        )
        assert result is None

    def test_whitespace_trace_id_returns_none(self):
        """Whitespace trace_id → None."""
        result = build_dal_only_candidate(
            licensing_verdict=object(),
            token_surface="دَيْنٍ",
            trace_id="   ",
        )
        assert result is None


# ── G_E5_05: Module invariants ────────────────────────────────────────────────

class TestT_E5_05_ModuleInvariants:
    """G_E5_05: Module invariants hold at import time."""

    def test_module_imports_without_error(self):
        """Module imports cleanly (invariants run at import time)."""
        assert True

    def test_vendor_sha_matches_pinned(self):
        """_VENDOR_SHA matches pinned constitutional SHA."""
        assert _VENDOR_SHA == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

    def test_build_dal_only_candidate_callable(self):
        """build_dal_only_candidate is callable."""
        assert callable(build_dal_only_candidate)

    def test_build_dal_only_from_surface_callable(self):
        """build_dal_only_from_surface is callable."""
        assert callable(build_dal_only_from_surface)

    def test_dal_only_available_is_bool(self):
        """_DAL_ONLY_AVAILABLE is a bool."""
        assert isinstance(_DAL_ONLY_AVAILABLE, bool)

    def test_e4c_available_is_bool(self):
        """_E4C_AVAILABLE is a bool."""
        assert isinstance(_E4C_AVAILABLE, bool)
