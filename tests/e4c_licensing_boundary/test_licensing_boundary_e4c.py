"""
E4C Native Licensing Boundary Tests — T_E4C_*

Tests for the E4C chain in licensing_boundary_adapter.py:
    - assess_license_from_weight_readiness() — full weigh() + assess_license() chain
    - build_licensing_verdict_from_surface() — E4B+E4C convenience function
    - E4A guard behavior still correct (no regressions)
    - Implementation state constant updated to E4C

Constitutional gates verified:
    G_E4C_01: assess_license_from_weight_readiness fail-closed on Python 3.10
    G_E4C_02: assess_license_from_weight_readiness returns ELIGIBLE on Python 3.12+
    G_E4C_03: build_licensing_verdict_from_surface E2E chain on Python 3.12+
    G_E4C_04: E4A guards (HARF, upstream DEFER/BLOCK, empty host) still correct
    G_E4C_05: ELIGIBLE result carries LicensingBoundaryVerdict (non-None) on 3.12+
    G_E4C_06: Implementation state constant documents E4C

Python 3.10 compat:
    - All guard tests run on 3.10 (pure string/structural guards — no vendor)
    - assess_license_from_weight_readiness returns IMPORT_FAILURE on 3.10
    - build_licensing_verdict_from_surface returns IMPORT_FAILURE on 3.10
    - REQUIRES_312 marks are skipped on 3.10

VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
Phase: E4C — NATIVE LICENSING BOUNDARY
"""
from __future__ import annotations

import sys
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from pipeline.taaqol_integration.weight_layer.licensing_boundary_adapter import (  # noqa: E402
    A1_IMPLEMENTATION_STATE,
    LicensingBoundaryAdapterResult,
    _E4B_MU_CHAIN_AVAILABLE,
    _E4C_PREWEIGHT_AVAILABLE,
    _VENDOR_SHA,
    _WEIGHT_LAYER_AVAILABLE,
    assess_license_from_weight_readiness,
    build_licensing_boundary_verdict,
    build_licensing_verdict_from_surface,
)

# Python 3.12+ marker (vendor StrEnum + mu chain)
REQUIRES_312 = pytest.mark.skipif(
    not (_WEIGHT_LAYER_AVAILABLE and _E4B_MU_CHAIN_AVAILABLE),
    reason="Requires Python 3.12+ (vendor StrEnum + mu chain)",
)

# Corpus samples from Ayat al-Dayn (2:282) with roots
_CORPUS_ISM = [
    ("دَيْنٍ",      "دين",  "دَيْنٍ"),   # debt — root: دين
    ("كَاتِبٌ",    "كتب",  "كَاتِبٌ"),  # scribe
    ("شَهِيدَيْنِ","شهد",  "شَهِيدَيْنِ"),  # two witnesses
    ("أَجَلٍ",     "أجل",  "أَجَلٍ"),   # appointed time
]

_CORPUS_HARF = ["إِلَى", "مِنْ", "فِي", "عَلَيْهِ"]


# ── G_E4C_01: Fail-closed on Python 3.10 ─────────────────────────────────────

class TestT_E4C_01_FailClosedOn310:
    """G_E4C_01: assess_license_from_weight_readiness returns IMPORT_FAILURE on Python 3.10."""

    def test_returns_import_failure_without_vendor(self):
        """Without vendor: assess_license_from_weight_readiness returns IMPORT_FAILURE."""
        if _WEIGHT_LAYER_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        result = assess_license_from_weight_readiness(
            weight_readiness=object(),
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t01:failclosed",
        )
        assert result.state == "IMPORT_FAILURE", (
            f"Expected IMPORT_FAILURE on 3.10, got {result.state!r}"
        )
        assert result.verdict is None

    def test_never_raises_on_310(self):
        """assess_license_from_weight_readiness never raises on Python 3.10."""
        if _WEIGHT_LAYER_AVAILABLE:
            pytest.skip("Python 3.12+ — vendor available")
        try:
            result = assess_license_from_weight_readiness(
                weight_readiness=None,
                segment_host="",
                word_class="ISM",
                trace_id="test:e4c:t01:never_raises",
            )
            assert result is not None
        except Exception as exc:
            pytest.fail(f"Should not raise on 3.10: {exc}")

    def test_build_licensing_verdict_from_surface_fails_closed_310(self):
        """build_licensing_verdict_from_surface returns IMPORT_FAILURE on 3.10."""
        if _E4B_MU_CHAIN_AVAILABLE:
            pytest.skip("Python 3.12+ — mu chain available")
        result = build_licensing_verdict_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t01:surface",
        )
        assert result.state == "IMPORT_FAILURE", (
            f"Expected IMPORT_FAILURE on 3.10, got {result.state!r}"
        )

    def test_e4c_preweight_available_on_310(self):
        """_E4C_PREWEIGHT_AVAILABLE = True on 3.10 (E4B module imports; mu chain absent)."""
        assert _E4C_PREWEIGHT_AVAILABLE is True, (
            "_E4C_PREWEIGHT_AVAILABLE should be True (E4B module imports on 3.10)"
        )

    def test_e4b_mu_chain_available_false_on_310(self):
        """_E4B_MU_CHAIN_AVAILABLE = False on 3.10 (vendor absent)."""
        if _E4B_MU_CHAIN_AVAILABLE:
            pytest.skip("Python 3.12+ — mu chain available")
        assert _E4B_MU_CHAIN_AVAILABLE is False


# ── G_E4C_02: assess_license_from_weight_readiness ELIGIBLE on Python 3.12+ ───

class TestT_E4C_02_EligibleOn312:
    """G_E4C_02: Full weigh() + assess_license() chain produces ELIGIBLE on Python 3.12+."""

    @REQUIRES_312
    def test_dayn_produces_eligible(self):
        """دَيْنٍ: full E4B+E4C chain produces ELIGIBLE."""
        from pipeline.taaqol_integration.weight_layer.preweight_chain_adapter import (
            build_weight_readiness_candidate,
        )
        wrc = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4c:t02:dayn",
        )
        assert wrc is not None, "E4B chain failed for دَيْنٍ"

        result = assess_license_from_weight_readiness(
            weight_readiness=wrc,
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t02:dayn:assess",
        )
        assert result.state == "ELIGIBLE", (
            f"Expected ELIGIBLE, got {result.state!r} — reason: {result.failure_reason!r}"
        )

    @REQUIRES_312
    def test_eligible_result_has_verdict(self):
        """ELIGIBLE result carries non-None LicensingBoundaryVerdict."""
        from pipeline.taaqol_integration.weight_layer.preweight_chain_adapter import (
            build_weight_readiness_candidate,
        )
        wrc = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4c:t02:verdict",
        )
        assert wrc is not None
        result = assess_license_from_weight_readiness(
            weight_readiness=wrc,
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t02:verdict:assess",
        )
        assert result.verdict is not None, "ELIGIBLE result must carry a verdict"

    @REQUIRES_312
    def test_verdict_has_boundary_kind_lexical(self):
        """ELIGIBLE verdict has boundary_kind=LEXICAL."""
        from pipeline.taaqol_integration.weight_layer.preweight_chain_adapter import (
            build_weight_readiness_candidate,
        )
        wrc = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4c:t02:bkind",
        )
        assert wrc is not None
        result = assess_license_from_weight_readiness(
            weight_readiness=wrc,
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t02:bkind:assess",
        )
        assert result.verdict is not None
        bk = str(result.verdict.boundary_kind)
        assert "LEXICAL" in bk, f"boundary_kind should be LEXICAL, got {bk!r}"

    @REQUIRES_312
    def test_refuse_non_weight_readiness_candidate(self):
        """assess_license_from_weight_readiness refuses non-WeightReadinessCandidate."""
        result = assess_license_from_weight_readiness(
            weight_readiness=object(),
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t02:refuse_wrong_type",
        )
        assert result.state == "REFUSED", (
            f"Expected REFUSED for wrong type, got {result.state!r}"
        )
        assert result.verdict is None

    @REQUIRES_312
    def test_refuse_empty_segment_host(self):
        """assess_license_from_weight_readiness refuses empty segment_host."""
        from pipeline.taaqol_integration.weight_layer.preweight_chain_adapter import (
            build_weight_readiness_candidate,
        )
        wrc = build_weight_readiness_candidate(
            token_surface="دَيْنٍ",
            root_letters="دين",
            trace_anchor="test:e4c:t02:empty_host",
        )
        assert wrc is not None
        result = assess_license_from_weight_readiness(
            weight_readiness=wrc,
            segment_host="",
            word_class="ISM",
            trace_id="test:e4c:t02:empty_host:assess",
        )
        assert result.state == "REFUSED", (
            f"Expected REFUSED for empty host, got {result.state!r}"
        )


# ── G_E4C_03: build_licensing_verdict_from_surface E2E chain ─────────────────

class TestT_E4C_03_E2EChain:
    """G_E4C_03: build_licensing_verdict_from_surface E4B+E4C chain on Python 3.12+."""

    @REQUIRES_312
    @pytest.mark.parametrize("token,root,host", _CORPUS_ISM)
    def test_corpus_ism_tokens_eligible(self, token, root, host):
        """Each corpus ISM token produces ELIGIBLE via full E4B+E4C chain."""
        result = build_licensing_verdict_from_surface(
            token_surface=token,
            root_letters=root,
            segment_host=host,
            word_class="ISM",
            trace_id=f"test:e4c:t03:corpus:{token}",
        )
        assert result.state == "ELIGIBLE", (
            f"Token {token!r}: expected ELIGIBLE, got {result.state!r} — {result.failure_reason!r}"
        )
        assert result.verdict is not None, (
            f"Token {token!r}: ELIGIBLE but verdict is None"
        )

    @REQUIRES_312
    def test_harf_blocked_before_e4b(self):
        """HARF tokens are blocked before reaching E4B chain."""
        result = build_licensing_verdict_from_surface(
            token_surface="إِلَى",
            root_letters="",
            segment_host="إِلَى",
            word_class="HARF",
            trace_id="test:e4c:t03:harf",
        )
        assert result.state == "BLOCKED_HARF_NOT_APPLICABLE", (
            f"Expected BLOCKED_HARF_NOT_APPLICABLE, got {result.state!r}"
        )
        assert result.verdict is None

    @REQUIRES_312
    def test_eligible_vendor_sha_embedded(self):
        """ELIGIBLE result always has vendor_sha embedded."""
        result = build_licensing_verdict_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t03:sha",
        )
        assert result.vendor_sha == _VENDOR_SHA, (
            f"vendor_sha mismatch: {result.vendor_sha!r}"
        )


# ── G_E4C_04: E4A guards still correct (no regressions) ─────────────────────

class TestT_E4C_04_E4AGuardsRegressionFree:
    """G_E4C_04: All E4A structural guards still work after E4C implementation."""

    def test_harf_guard_in_build_licensing_boundary_verdict(self):
        """HARF guard fires before vendor/E4C in build_licensing_boundary_verdict."""
        result = build_licensing_boundary_verdict(
            "إِلَى", "إِلَى", "HARF", "إِلَى", "claim:01", "trace:01"
        )
        assert result.state == "BLOCKED_HARF_NOT_APPLICABLE"
        assert result.vendor_sha == _VENDOR_SHA

    def test_upstream_block_guard(self):
        """Upstream BLOCK directive deferred before vendor/E4C."""
        result = build_licensing_boundary_verdict(
            "دَيْنٍ", "دَيْنٍ", "ISM", "دَيْنٍ", "claim:02", "trace:02",
            domain_directive="BLOCK",
        )
        assert result.state == "DEFERRED"

    def test_upstream_defer_guard(self):
        """Upstream DEFER directive deferred before vendor/E4C."""
        result = build_licensing_boundary_verdict(
            "دَيْنٍ", "دَيْنٍ", "ISM", "دَيْنٍ", "claim:03", "trace:03",
            domain_directive="DEFER",
        )
        assert result.state == "DEFERRED"

    def test_empty_segment_host_deferred(self):
        """Empty segment_host, normalized_surface, and token_surface → DEFERRED or IMPORT_FAILURE.

        The guard: _segment_host = (segment_host or normalized_surface or token_surface or "").strip()
        All three empty → _segment_host="" → DEFERRED guard fires (before vendor check).
        """
        result = build_licensing_boundary_verdict(
            "", "", "ISM", "", "claim:04", "trace:04",  # all surfaces empty
            domain_directive="ACCEPT",
        )
        # Either DEFERRED (guard fired — correct) or IMPORT_FAILURE (vendor check — also acceptable)
        # On 3.10: guard fires first since all three surfaces are empty → DEFERRED
        assert result.state in ("DEFERRED", "IMPORT_FAILURE"), (
            f"Expected DEFERRED or IMPORT_FAILURE for all-empty input, got {result.state!r}"
        )

    def test_vendor_sha_always_embedded_in_result(self):
        """vendor_sha is always accessible in LicensingBoundaryAdapterResult."""
        result = build_licensing_boundary_verdict(
            "إِلَى", "إِلَى", "HARF", "إِلَى", "claim:05", "trace:05"
        )
        assert result.vendor_sha == _VENDOR_SHA

    def test_trace_anchor_preserved(self):
        """trace_anchor is preserved in result."""
        anchor = "test:e4c:t04:trace_anchor"
        result = build_licensing_boundary_verdict(
            "إِلَى", "إِلَى", "HARF", "إِلَى", "claim:06", anchor
        )
        assert result.trace_anchor == anchor

    def test_result_is_licensing_boundary_adapter_result(self):
        """All guard paths return LicensingBoundaryAdapterResult."""
        for result in [
            build_licensing_boundary_verdict("إِلَى", "إِلَى", "HARF", "إِلَى", "c", "t"),
            build_licensing_boundary_verdict("دَيْنٍ", "دَيْنٍ", "ISM", "دَيْنٍ", "c", "t", domain_directive="DEFER"),
            build_licensing_verdict_from_surface("إِلَى", "", "إِلَى", "HARF", "t"),
        ]:
            assert isinstance(result, LicensingBoundaryAdapterResult), (
                f"Expected LicensingBoundaryAdapterResult, got {type(result)}"
            )


# ── G_E4C_05: ELIGIBLE result structure ──────────────────────────────────────

class TestT_E4C_05_EligibleResultStructure:
    """G_E4C_05: ELIGIBLE result carries correct LicensingBoundaryVerdict fields."""

    @REQUIRES_312
    def test_eligible_verdict_has_eligibility_verdict_string(self):
        """LicensingBoundaryVerdict.eligibility_verdict conforms to the exact
        native contract: `boundary_eligible:<kind>` with evidence + rank + no
        blocking residual. See vendor `weight/licensing_boundary.py:460`
        (source is frozen — assert the semantic form the vendor emits, not a
        loose case-insensitive substring)."""
        # Vendor-authoritative type import (kept inside the test so 3.10 runs
        # never hit the StrEnum import path — vendor kernel requires 3.11+).
        from taaqqul_slot_geometry.weight.licensing_boundary import (
            LicensingBoundaryVerdict,
        )
        result = build_licensing_verdict_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t05:eligibility_verdict",
        )
        # (a) outer envelope must be ELIGIBLE.
        assert result.state == "ELIGIBLE", (
            f"expected ELIGIBLE outer state, got {result.state!r} — "
            f"failure_reason={getattr(result, 'failure_reason', None)!r}"
        )
        # (b) verdict must exist and be the native vendor dataclass — not a
        #     hokom projection, not a dict, not None.
        verdict = result.verdict
        assert verdict is not None, "ELIGIBLE result must carry a verdict"
        assert type(verdict) is LicensingBoundaryVerdict, (
            f"verdict must be vendor LicensingBoundaryVerdict, "
            f"got {type(verdict).__name__}"
        )
        # (c) eligibility_verdict follows the exact vendor form
        #     `boundary_eligible:<boundary_kind.value>` (licensing_boundary.py:460).
        ev = verdict.eligibility_verdict
        assert isinstance(ev, str) and ev.strip(), (
            f"eligibility_verdict must be non-empty str, got {ev!r}"
        )
        assert ev.startswith("boundary_eligible:"), (
            f"eligibility_verdict must start with 'boundary_eligible:', "
            f"got {ev!r}"
        )
        # The suffix after the colon must match the verdict's own boundary_kind.
        suffix = ev.split(":", 1)[1]
        assert suffix == verdict.boundary_kind.value, (
            f"eligibility_verdict suffix {suffix!r} must equal "
            f"boundary_kind.value {verdict.boundary_kind.value!r}"
        )
        # (d) evidence continuity — evidence_summary is
        #     `<boundary_kind.value>:<attestation>` (licensing_boundary.py:462).
        es = verdict.evidence_summary
        assert isinstance(es, str) and ":" in es, (
            f"evidence_summary must be '<kind>:<attestation>', got {es!r}"
        )
        assert es.startswith(f"{verdict.boundary_kind.value}:"), (
            f"evidence_summary must be prefixed with boundary_kind.value, "
            f"got {es!r}"
        )
        # (e) residual behavior — the adapter's outer envelope collapses
        #     residual state into the outcome: ELIGIBLE ⇒ no blocking
        #     residual survived. Assert failure_reason is empty (the vendor
        #     `assess_license` puts BLOCKING residuals into
        #     failure_code/failure_reason before it can return ELIGIBLE).
        assert result.failure_reason == "", (
            f"ELIGIBLE result must have empty failure_reason, got {result.failure_reason!r}"
        )
        # (f) rank continuity — eligibility_rank is a real Rank member bounded
        #     by LICENSE_BOUNDARY_RANK_CEILING (vendor invariant enforced in
        #     LicensingBoundaryVerdict.__post_init__).
        from taaqqul_slot_geometry.weight.licensing_boundary import (
            LICENSE_BOUNDARY_RANK_CEILING,
        )
        from taaqqul_slot_geometry.core.rank_lattice import Rank
        assert isinstance(verdict.eligibility_rank, Rank), (
            f"eligibility_rank must be Rank, got {type(verdict.eligibility_rank).__name__}"
        )
        assert verdict.eligibility_rank <= LICENSE_BOUNDARY_RANK_CEILING, (
            f"eligibility_rank {verdict.eligibility_rank!r} exceeds ceiling "
            f"{LICENSE_BOUNDARY_RANK_CEILING!r}"
        )

    @REQUIRES_312
    def test_eligible_verdict_has_evidence_summary(self):
        """LicensingBoundaryVerdict.evidence_summary is a non-empty string."""
        result = build_licensing_verdict_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t05:evidence_summary",
        )
        assert result.state == "ELIGIBLE"
        es = result.verdict.evidence_summary
        assert isinstance(es, str) and es.strip(), (
            f"evidence_summary must be non-empty str, got {es!r}"
        )

    @REQUIRES_312
    def test_eligible_implementation_state(self):
        """implementation_state in ELIGIBLE result documents E4C."""
        result = build_licensing_verdict_from_surface(
            token_surface="دَيْنٍ",
            root_letters="دين",
            segment_host="دَيْنٍ",
            word_class="ISM",
            trace_id="test:e4c:t05:impl_state",
        )
        assert "E4C" in result.implementation_state or "IMPLEMENTED" in result.implementation_state, (
            f"implementation_state should reference E4C: {result.implementation_state!r}"
        )


# ── G_E4C_06: Implementation state constant ───────────────────────────────────

class TestT_E4C_06_ImplementationState:
    """G_E4C_06: A1_IMPLEMENTATION_STATE documents E4C phase."""

    def test_implementation_state_is_e4c(self):
        """A1_IMPLEMENTATION_STATE references E4C."""
        assert "E4C" in A1_IMPLEMENTATION_STATE, (
            f"Expected 'E4C' in A1_IMPLEMENTATION_STATE, got {A1_IMPLEMENTATION_STATE!r}"
        )

    def test_implementation_state_is_non_empty(self):
        """A1_IMPLEMENTATION_STATE is non-empty."""
        assert A1_IMPLEMENTATION_STATE and A1_IMPLEMENTATION_STATE.strip()

    def test_vendor_sha_constant(self):
        """_VENDOR_SHA matches pinned constitutional SHA."""
        assert _VENDOR_SHA == "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

    def test_e4c_preweight_available_true(self):
        """_E4C_PREWEIGHT_AVAILABLE = True (E4B preweight chain importable)."""
        assert _E4C_PREWEIGHT_AVAILABLE is True, (
            "E4B preweight adapter must be importable for E4C to work"
        )
