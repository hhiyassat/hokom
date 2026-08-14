"""
tests/p2_augmented/test_licensing_boundary_adapter_e0.py

E0 acceptance tests for A1_LICENSING_BOUNDARY adapter.

Tests:
    T05_LICENSING_BOUNDARY_ADAPTER — interface contract and fail-closed behavior
    T05a — IMPORT_FAILURE on Python 3.10 (sandbox)
    T05b — BLOCKED_HARF_NOT_APPLICABLE for HARF tokens
    T05c — DEFERRED on upstream BLOCK/DEFER directive
    T05d — BLOCKED_PHONOLOGICAL_CHAIN for ISM/FI3L (phonological chain required)
    T05e — VENDOR_SHA embedded in all results
    T05f — vendor layer API surface correct (Python 3.12+ only)
    T05g — assess_license_from_weight_readiness entry point exists

Constitutional references:
    - 05_P2_REGISTRY_CONTRACT.md: type mismatch root cause
    - 08_HOKOM_TAAQOL_ADAPTER_MATRIX.csv: A1_LICENSING_BOUNDARY
    - 10_FAILURE_AND_RESIDUAL_TAXONOMY.md: FAIL-CLOSED contract
    - 13_STAGE_ACCEPTANCE_GATES.md: G_E0_04, G_E0_05

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
"""
from __future__ import annotations

import sys
import pytest
from pathlib import Path

# Ensure repo on path
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"))

# ── Import adapter ───────────────────────────────────────────────────────────
from pipeline.taaqol_integration.weight_layer.licensing_boundary_adapter import (
    build_licensing_boundary_verdict,
    assess_license_from_weight_readiness,
    LicensingBoundaryAdapterResult,
    _WEIGHT_LAYER_AVAILABLE,
    _VENDOR_SHA,
    A1_IMPLEMENTATION_STATE,
    _PHONOLOGICAL_CHAIN_BLOCK_REASON,
)

PINNED_VENDOR_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"
_PY312_PLUS = sys.version_info >= (3, 12)

_VENDOR_SKIP = pytest.mark.skipif(
    not _WEIGHT_LAYER_AVAILABLE,
    reason="taaqqul_slot_geometry requires Python 3.12+ (StrEnum)"
)

# Shared test fixtures
_ISM_SURFACE   = "بِدَيْنٍ"
_FI3L_SURFACE  = "تَدَايَنْتُمْ"
_HARF_SURFACE  = "إِلَى"
_TRACE_ID      = "hokom:test-trace-001"


# ─────────────────────────────────────────────────────────────────────────────
# T05a — FAIL-CLOSED: IMPORT_FAILURE on Python 3.10
# ─────────────────────────────────────────────────────────────────────────────

class TestT05aFailClosed:
    """T05a: adapter is fail-closed — returns non-ELIGIBLE on import failure."""

    def test_result_type_always_returned(self):
        """build_licensing_boundary_verdict always returns LicensingBoundaryAdapterResult."""
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test-001",
            trace_id=_TRACE_ID,
        )
        assert isinstance(result, LicensingBoundaryAdapterResult), (
            "build_licensing_boundary_verdict must always return "
            "LicensingBoundaryAdapterResult (fail-closed)"
        )

    def test_never_eligible_on_import_failure(self):
        """If vendor unavailable, state must not be ELIGIBLE."""
        if _WEIGHT_LAYER_AVAILABLE:
            pytest.skip("vendor available — testing fail-closed path")
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test-001",
            trace_id=_TRACE_ID,
        )
        assert result.state == "IMPORT_FAILURE", (
            f"expected IMPORT_FAILURE on import failure, got {result.state!r}"
        )
        assert result.verdict is None, "verdict must be None on IMPORT_FAILURE"

    def test_never_raises_exception(self):
        """build_licensing_boundary_verdict must never raise an exception."""
        # test with all edge cases
        for surface, wc, host in [
            ("", "ISM", ""),
            (_HARF_SURFACE, "HARF", "إِلَى"),
            (_ISM_SURFACE, "ISM", "دَيْن"),
            (_FI3L_SURFACE, "FI3L", "دَايَن"),
            ("", "", ""),
            ("unknown_token", "UNKNOWN", "unknown"),
        ]:
            try:
                result = build_licensing_boundary_verdict(
                    token_surface=surface,
                    normalized_surface=surface,
                    word_class=wc,
                    segment_host=host,
                    claim_id="hokom:test",
                    trace_id=_TRACE_ID,
                )
                assert isinstance(result, LicensingBoundaryAdapterResult), (
                    f"expected LicensingBoundaryAdapterResult for {surface!r}/{wc!r}"
                )
            except Exception as e:
                pytest.fail(
                    f"build_licensing_boundary_verdict raised {type(e).__name__} "
                    f"for surface={surface!r} wc={wc!r}: {e}"
                )


# ─────────────────────────────────────────────────────────────────────────────
# T05b — HARF tokens: BLOCKED_HARF_NOT_APPLICABLE
# ─────────────────────────────────────────────────────────────────────────────

class TestT05bHarfBlocked:
    """T05b: HARF tokens are not in DAL domain — BLOCKED_HARF_NOT_APPLICABLE."""

    @pytest.mark.parametrize("surface,host", [
        ("إِلَى", "إِلَى"),
        ("يَا", "يَا"),
        ("أَنْ", "أَنْ"),
        ("لَمْ", "لَمْ"),
        ("مِنْ", "مِنْ"),
    ])
    def test_harf_blocked_not_applicable(self, surface, host):
        """HARF word class returns BLOCKED_HARF_NOT_APPLICABLE, not ELIGIBLE."""
        result = build_licensing_boundary_verdict(
            token_surface=surface,
            normalized_surface=surface,
            word_class="HARF",
            segment_host=host,
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
        )
        assert result.state == "BLOCKED_HARF_NOT_APPLICABLE", (
            f"HARF surface={surface!r} should be BLOCKED_HARF_NOT_APPLICABLE, "
            f"got {result.state!r}"
        )
        assert result.verdict is None

    def test_harf_verdict_always_none(self):
        """HARF verdict must always be None (no weight chain for HARF)."""
        result = build_licensing_boundary_verdict(
            token_surface=_HARF_SURFACE,
            normalized_surface=_HARF_SURFACE,
            word_class="HARF",
            segment_host=_HARF_SURFACE,
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
        )
        assert result.verdict is None


# ─────────────────────────────────────────────────────────────────────────────
# T05c — Upstream directive: DEFERRED on BLOCK/DEFER
# ─────────────────────────────────────────────────────────────────────────────

class TestT05cUpstreamDirective:
    """T05c: upstream BLOCK/DEFER directive propagates as DEFERRED."""

    @pytest.mark.parametrize("directive", ["BLOCK", "BLOCKED", "DEFER", "block", "defer"])
    def test_upstream_block_defer_returns_deferred(self, directive):
        """BLOCK/DEFER directive from upstream → DEFERRED result."""
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive=directive,
        )
        assert result.state == "DEFERRED", (
            f"upstream_directive={directive!r} should produce DEFERRED, "
            f"got {result.state!r}"
        )
        assert result.verdict is None

    def test_accept_directive_passes_through_to_downstream_checks(self):
        """ACCEPT directive passes to E4C chain (not intercepted by directive guard).

        CONSTITUTIONAL_RECONCILIATION_01 (2026-08-01):
        E4C implements the full omega_governance→weigh→assess_license chain.
        On Python 3.12+: ACCEPT+ISM reaches the chain and returns ELIGIBLE.
        On Python 3.10: IMPORT_FAILURE (vendor not available).
        """
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive="ACCEPT",
        )
        # Directive guard must NOT intercept ACCEPT.
        assert result.state != "DEFERRED", (
            f"ACCEPT directive must not be caught by directive guard, "
            f"got {result.state!r}: {result.failure_reason!r}"
        )
        if _WEIGHT_LAYER_AVAILABLE:
            # E4C: ACCEPT+ISM reaches full assess_license chain → ELIGIBLE
            assert result.state == "ELIGIBLE", (
                f"E4C: ACCEPT+ISM should return ELIGIBLE on Python 3.12+, "
                f"got {result.state!r}"
            )
        else:
            # Python 3.10: vendor absent → IMPORT_FAILURE
            assert result.state == "IMPORT_FAILURE", (
                f"Python 3.10: ACCEPT+ISM should return IMPORT_FAILURE, "
                f"got {result.state!r}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# T05d — ISM/FI3L: BLOCKED_PHONOLOGICAL_CHAIN (E0 state)
# ─────────────────────────────────────────────────────────────────────────────

@_VENDOR_SKIP
class TestT05dPhonologicalChainBlocked:
    """T05d: ISM/FI3L E4C behavior — ELIGIBLE via assess_license chain (Python 3.12+).

    MIGRATION RECORD (CONSTITUTIONAL_RECONCILIATION_01, 2026-08-01):
    Originally tested BLOCKED_PHONOLOGICAL_CHAIN (E0 state).
    E4C (A1_IMPLEMENTATION_STATE = E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED) now routes
    ISM/FI3L+ACCEPT through the full omega_governance→weigh→assess_license chain,
    returning ELIGIBLE for valid corpus tokens. Node IDs preserved for canonical gate.
    """

    @pytest.mark.parametrize("surface,wc,host", [
        ("بِدَيْنٍ",      "ISM",  "دَيْن"),
        ("تَدَايَنْتُمْ", "FI3L", "دَايَن"),
        ("كَاتِبٌ",       "ISM",  "كَاتِب"),
        ("يَكْتُبْ",      "FI3L", "كَتَب"),
    ])
    def test_ism_fi3l_blocked_phonological_chain(self, surface, wc, host):
        """ISM/FI3L tokens return ELIGIBLE via E4C assess_license chain (Python 3.12+).

        MIGRATION: was BLOCKED_PHONOLOGICAL_CHAIN in E0; E4C routes through full chain.
        """
        result = build_licensing_boundary_verdict(
            token_surface=surface,
            normalized_surface=surface,
            word_class=wc,
            segment_host=host,
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive="ACCEPT",
        )
        assert result.state == "ELIGIBLE", (
            f"E4C: ISM/FI3L surface={surface!r} should be ELIGIBLE via assess_license chain, "
            f"got {result.state!r}"
        )
        assert result.verdict is not None, (
            f"ELIGIBLE result must carry a verdict (not None) for {surface!r}"
        )
        assert type(result.verdict).__name__ == "LicensingBoundaryVerdict", (
            f"verdict type must be LicensingBoundaryVerdict, "
            f"got {type(result.verdict).__name__!r} for {surface!r}"
        )

    def test_blocked_reason_documents_pre_weight_requirement(self):
        """E4C: ELIGIBLE result carries no failure_reason (chain succeeded).

        MIGRATION: was asserting failure_reason contains phonological/WeightReadinessCandidate.
        E4C chain succeeds → failure_reason is None or empty string.
        """
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive="ACCEPT",
        )
        assert result.state == "ELIGIBLE", (
            f"E4C: ACCEPT+ISM should be ELIGIBLE, got {result.state!r}"
        )
        assert not result.failure_reason, (
            f"ELIGIBLE result must not carry failure_reason, "
            f"got {result.failure_reason!r}"
        )

    def test_implementation_state_documents_e5_scope(self):
        """implementation_state documents E4C scope (E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED).

        MIGRATION: was asserting E0/BLOCKED/PHONOLOGICAL in implementation_state.
        E4C changes this to E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED.
        """
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
        )
        assert result.implementation_state == "E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED", (
            f"implementation_state must be E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED, "
            f"got {result.implementation_state!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# T05i — E4C native assess_license chain invariants (Python 3.12+ only)
# ─────────────────────────────────────────────────────────────────────────────

@_VENDOR_SKIP
class TestT05iE4cNativeChain:
    """T05i: E4C native assess_license chain produces correct invariants (Python 3.12+).

    Verifies:
        NATIVE_ASSESS_LICENSE_CALLED = 1  (state == ELIGIBLE)
        EXACT_OUTPUT_TYPE = LicensingBoundaryVerdict
        TRACE_CONTINUITY = 1  (trace_anchor preserved)
        RESIDUAL_CONTINUITY = 1  (empty residuals passed → chain completes)
        RANK_VALID = 1  (verdict carries LicensingBoundaryState.ELIGIBLE)
    """

    def test_native_assess_license_called(self):
        """NATIVE_ASSESS_LICENSE_CALLED=1: ELIGIBLE state proves chain was invoked."""
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive="ACCEPT",
        )
        assert result.state == "ELIGIBLE", (
            f"NATIVE_ASSESS_LICENSE_CALLED: state must be ELIGIBLE, got {result.state!r}"
        )

    def test_exact_output_type_licensing_boundary_verdict(self):
        """EXACT_OUTPUT_TYPE=LicensingBoundaryVerdict: verdict carries the vendor type."""
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive="ACCEPT",
        )
        assert result.verdict is not None, "verdict must not be None for ELIGIBLE"
        assert type(result.verdict).__name__ == "LicensingBoundaryVerdict", (
            f"EXACT_OUTPUT_TYPE: expected LicensingBoundaryVerdict, "
            f"got {type(result.verdict).__name__!r}"
        )

    def test_trace_continuity(self):
        """TRACE_CONTINUITY=1: trace_anchor from caller is preserved in ELIGIBLE result."""
        custom_trace = "hokom:e4c-trace-continuity-test"
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=custom_trace,
            domain_directive="ACCEPT",
        )
        assert result.trace_anchor == custom_trace, (
            f"TRACE_CONTINUITY: trace_anchor not preserved; "
            f"expected {custom_trace!r}, got {result.trace_anchor!r}"
        )

    def test_residual_continuity_empty_passthrough(self):
        """RESIDUAL_CONTINUITY=1: empty active_residuals produces ELIGIBLE (chain completes)."""
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive="ACCEPT",
            active_residuals=(),
        )
        assert result.state == "ELIGIBLE", (
            f"RESIDUAL_CONTINUITY: empty residuals should produce ELIGIBLE, "
            f"got {result.state!r}"
        )

    def test_rank_valid_eligible_state(self):
        """RANK_VALID=1: ELIGIBLE verdict carries a LicensingBoundaryVerdict with state."""
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive="ACCEPT",
        )
        assert result.state == "ELIGIBLE", (
            f"RANK_VALID: state must be ELIGIBLE, got {result.state!r}"
        )
        assert result.verdict is not None, "RANK_VALID: verdict must not be None"
        # LicensingBoundaryVerdict.eligibility_verdict encodes the licensing decision
        # Value is "boundary_eligible:<kind>" — check for "eligible" (case-insensitive)
        verdict_state = str(result.verdict.eligibility_verdict)
        assert "eligible" in verdict_state.lower(), (
            f"RANK_VALID: verdict.eligibility_verdict must encode eligible, got {verdict_state!r}"
        )

    def test_implementation_state_e4c(self):
        """implementation_state = E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED on all E4C results."""
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
        )
        assert result.implementation_state == "E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED", (
            f"E4C: implementation_state must be E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED, "
            f"got {result.implementation_state!r}"
        )

    def test_fi3l_also_eligible_via_e4c(self):
        """FI3L tokens also reach ELIGIBLE via E4C chain (not just ISM)."""
        result = build_licensing_boundary_verdict(
            token_surface=_FI3L_SURFACE,
            normalized_surface=_FI3L_SURFACE,
            word_class="FI3L",
            segment_host="دَايَن",
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive="ACCEPT",
        )
        assert result.state == "ELIGIBLE", (
            f"E4C: FI3L should be ELIGIBLE via assess_license chain, "
            f"got {result.state!r}"
        )
        assert result.verdict is not None, "FI3L ELIGIBLE must carry verdict"


# ─────────────────────────────────────────────────────────────────────────────
# T05e — VENDOR_SHA embedded in all results
# ─────────────────────────────────────────────────────────────────────────────

class TestT05eVendorSha:
    """T05e: VENDOR_SHA is always embedded in all adapter results."""

    @pytest.mark.parametrize("surface,wc,host,directive", [
        (_ISM_SURFACE,  "ISM",  "دَيْن",   "ACCEPT"),
        (_HARF_SURFACE, "HARF", "إِلَى",   "ACCEPT"),
        (_FI3L_SURFACE, "FI3L", "دَايَن",  "DEFER"),
        ("",            "ISM",  "",          "BLOCK"),
    ])
    def test_vendor_sha_always_embedded(self, surface, wc, host, directive):
        """VENDOR_SHA is embedded in every result regardless of state."""
        result = build_licensing_boundary_verdict(
            token_surface=surface,
            normalized_surface=surface,
            word_class=wc,
            segment_host=host,
            claim_id="hokom:test",
            trace_id=_TRACE_ID,
            domain_directive=directive,
        )
        assert result.vendor_sha == PINNED_VENDOR_SHA, (
            f"vendor_sha mismatch: expected {PINNED_VENDOR_SHA!r}, "
            f"got {result.vendor_sha!r} for surface={surface!r} state={result.state!r}"
        )

    def test_module_vendor_sha_pinned(self):
        """Module-level _VENDOR_SHA matches pinned value."""
        assert _VENDOR_SHA == PINNED_VENDOR_SHA

    def test_trace_anchor_propagated(self):
        """trace_anchor from caller is preserved in result."""
        custom_trace = "hokom:caller-trace-99"
        result = build_licensing_boundary_verdict(
            token_surface=_ISM_SURFACE,
            normalized_surface=_ISM_SURFACE,
            word_class="ISM",
            segment_host="دَيْن",
            claim_id="hokom:test",
            trace_id=custom_trace,
        )
        assert result.trace_anchor == custom_trace, (
            f"trace_anchor not propagated: expected {custom_trace!r}, "
            f"got {result.trace_anchor!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# T05f — Vendor API surface (Python 3.12+ only)
# ─────────────────────────────────────────────────────────────────────────────

@_VENDOR_SKIP
class TestT05fVendorApiSurface:
    """T05f: correct vendor types are importable and have expected interface (Python 3.12+)."""

    def test_weight_fit_candidate_requires_source(self):
        """WeightFitCandidate.source must be WeightReadinessCandidate — confirms blocker."""
        from taaqqul_slot_geometry.weight.weight_fit import WeightFitCandidate
        from taaqqul_slot_geometry.weight.pre_weight import WeightReadinessCandidate
        from taaqqul_slot_geometry.weight.carrier_core import WeightCarrierSchemaError
        from taaqqul_slot_geometry.core.rank_lattice import Rank
        from taaqqul_slot_geometry.core.slot_graph import TraceRef
        from taaqqul_slot_geometry.core.residual_policy import Residual, ResidualKind

        # This must raise because source is not a WeightReadinessCandidate
        with pytest.raises((WeightCarrierSchemaError, TypeError)):
            WeightFitCandidate(
                value="دَيْن",
                type="ISM",
                origin="BYPASS",
                identity="hokom:test",
                domain="arabic_morphology",
                scope="دَيْن",
                rank=Rank.CANDIDATE,
                residuals=(),
                trace=TraceRef(anchor="hokom:test", kind="hokom_claim"),
                source=None,          # Not a WeightReadinessCandidate → must raise
                fit_verdict="test",
                fit_rank=Rank.CANDIDATE,
            )

    def test_assess_license_callable(self):
        """assess_license is callable (confirming import succeeded)."""
        from taaqqul_slot_geometry.weight.licensing_boundary import assess_license
        assert callable(assess_license)

    def test_licensing_boundary_verdict_importable(self):
        """LicensingBoundaryVerdict is importable (confirming vendor layer)."""
        from taaqqul_slot_geometry.weight.licensing_boundary import (
            LicensingBoundaryVerdict,
            LicensingBoundaryState,
            LicenseBoundaryKind,
            BoundaryEvidence,
        )
        assert LicensingBoundaryVerdict is not None
        assert "ELIGIBLE" in [s.value for s in LicensingBoundaryState]

    def test_omega_governance_callable(self):
        """omega_governance is callable with correct signature."""
        from taaqqul_slot_geometry.weight.mu_chain import omega_governance
        from taaqqul_slot_geometry.core.rank_lattice import Rank
        # omega_governance with empty residuals should grant
        result = omega_governance(residuals=(), surface_rank=Rank.CANDIDATE)
        from taaqqul_slot_geometry.weight.mu_chain import OmegaGovernanceState
        assert result.state is OmegaGovernanceState.GRANTED


# ─────────────────────────────────────────────────────────────────────────────
# T05g — assess_license_from_weight_readiness entry point
# ─────────────────────────────────────────────────────────────────────────────

class TestT05gE5EntryPoint:
    """T05g: assess_license_from_weight_readiness entry point exists and is callable."""

    def test_entry_point_is_callable(self):
        """assess_license_from_weight_readiness must be callable."""
        assert callable(assess_license_from_weight_readiness)

    def test_entry_point_rejects_non_weight_readiness(self):
        """E5 entry point rejects non-WeightReadinessCandidate input."""
        if not _WEIGHT_LAYER_AVAILABLE:
            # On Python 3.10: returns IMPORT_FAILURE
            result = assess_license_from_weight_readiness(
                weight_readiness="not_a_carrier",
                segment_host="دَيْن",
                word_class="ISM",
                trace_id=_TRACE_ID,
            )
            assert result.state == "IMPORT_FAILURE"
        else:
            # On Python 3.12+: returns REFUSED (wrong type)
            result = assess_license_from_weight_readiness(
                weight_readiness="not_a_carrier",
                segment_host="دَيْن",
                word_class="ISM",
                trace_id=_TRACE_ID,
            )
            assert result.state == "REFUSED", (
                f"non-WeightReadinessCandidate input should be REFUSED, "
                f"got {result.state!r}"
            )

    def test_entry_point_never_raises(self):
        """assess_license_from_weight_readiness must never raise an exception."""
        for weight_readiness in [None, "string", 42, object(), []]:
            try:
                result = assess_license_from_weight_readiness(
                    weight_readiness=weight_readiness,
                    segment_host="دَيْن",
                    word_class="ISM",
                    trace_id=_TRACE_ID,
                )
                assert isinstance(result, LicensingBoundaryAdapterResult)
            except Exception as e:
                pytest.fail(
                    f"assess_license_from_weight_readiness raised {type(e).__name__} "
                    f"for weight_readiness={weight_readiness!r}: {e}"
                )

    def test_entry_point_embeds_vendor_sha(self):
        """E5 entry point embeds VENDOR_SHA in all results."""
        result = assess_license_from_weight_readiness(
            weight_readiness="not_a_carrier",
            segment_host="دَيْن",
            word_class="ISM",
            trace_id=_TRACE_ID,
        )
        assert result.vendor_sha == PINNED_VENDOR_SHA


# ─────────────────────────────────────────────────────────────────────────────
# T05h — Implementation state constants correct
# ─────────────────────────────────────────────────────────────────────────────

class TestT05hImplementationConstants:
    """T05h: module constants are correct for E0 phase."""

    def test_implementation_state_constant_documents_phase(self):
        """A1_IMPLEMENTATION_STATE must be non-empty and document a phase state.

        Updated in E4C: value changed from E0_INTERFACE_DEFINED_BLOCKED_PHONOLOGICAL_CHAIN
        to E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED (constitutional_reconciliation_01).
        """
        assert A1_IMPLEMENTATION_STATE, "A1_IMPLEMENTATION_STATE must be non-empty"
        # Must mention a phase marker (E0, E4, BLOCKED, PHONOLOGICAL, or IMPLEMENTED)
        assert any(k in A1_IMPLEMENTATION_STATE.upper() for k in
                   ["E0", "E4", "BLOCKED", "PHONOLOGICAL", "IMPLEMENTED"]), (
            f"A1_IMPLEMENTATION_STATE should document implementation phase, "
            f"got {A1_IMPLEMENTATION_STATE!r}"
        )

    def test_phonological_block_reason_documents_requirement(self):
        """_PHONOLOGICAL_CHAIN_BLOCK_REASON documents WeightReadinessCandidate requirement."""
        assert "WeightReadinessCandidate" in _PHONOLOGICAL_CHAIN_BLOCK_REASON or \
               "WeightFitCandidate" in _PHONOLOGICAL_CHAIN_BLOCK_REASON, (
            "_PHONOLOGICAL_CHAIN_BLOCK_REASON must name the required type"
        )
        assert "phonological" in _PHONOLOGICAL_CHAIN_BLOCK_REASON.lower(), (
            "_PHONOLOGICAL_CHAIN_BLOCK_REASON must mention phonological chain"
        )

    def test_weight_layer_available_reflects_python_version(self):
        """_WEIGHT_LAYER_AVAILABLE reflects vendor import success."""
        if _PY312_PLUS:
            # On Python 3.12+, vendor should be available
            assert _WEIGHT_LAYER_AVAILABLE, (
                "taaqqul_slot_geometry should be importable on Python 3.12+"
            )
        else:
            # On Python 3.10 (sandbox), vendor is not available
            assert not _WEIGHT_LAYER_AVAILABLE, (
                "taaqqul_slot_geometry should NOT be importable on Python 3.10"
            )
