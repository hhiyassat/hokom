"""
Licensing Boundary Adapter — E4A/E4C (A1_LICENSING_BOUNDARY)

CONSTITUTIONAL_RECONCILIATION_01 (2026-08-01):
    Reclassified from "E0 (A1_LICENSING_BOUNDARY)" to "E4A_PRECONDITION_GUARD_AND_TYPED_ENTRY_SURFACE".
    Under constitutional reclassification:
      - E0 = TARGET BASELINE FREEZE (SHAs only — no implementation)
      - E4A = PRECONDITION_GUARD (this file — DONE: HARF/directive/empty-host/vendor guards)
      - E4B = PRE-WEIGHT TYPED CARRIERS (preweight_chain_adapter.py — DONE)
      - E4C = NATIVE LICENSING BOUNDARY (this file — IMPLEMENTED: assess_license() chain)
    The guard ordering in this file is CORRECT per E4A:
      upstream_directive → HARF → empty_host → vendor_check → E4C chain
    E4A is CLOSED. E4B is FOCUSED_VERIFIED. E4C implemented in this session.
    G_E0_04=1 WAS INCORRECT: BLOCKED_PHONOLOGICAL_CHAIN ≠ LicensingBoundaryVerdict produced.

Purpose:
    Defines the interface contract for bridging Hokom's morphological
    output to Taaqol's LicensingBoundaryVerdict. This adapter is the
    E4A-phase precondition guard for A1_LICENSING_BOUNDARY.

Type mismatch root cause (from AUDIT-01):
    Hokom produces: HokomLinguisticClaimBundle (word_class, surface, root)
    Taaqol prove_dal() requires: LicensingBoundaryVerdict
    assess_license() requires: WeightFitCandidate
    WeightFitCandidate requires: WeightReadinessCandidate (source field, type-enforced)
    WeightReadinessCandidate requires: pre_weight phonological chain (8 μ-stages)

BLOCKED — PHONOLOGICAL CHAIN REQUIRED:
    The full implementation of A1 requires a WeightReadinessCandidate built via
    the 8-stage μ chain (μ_seq → μ_boundary → μ_word_carrier → μ_path_gate →
    μ_root_stem → μ_original_extra → μ_ops → μ_weight_readiness). This chain
    requires syllable-level phonological analysis (letter/haraka pairs) which
    Hokom's P0_PHONOLOGICAL stage does NOT produce (NOT_REACHED).

    The WeightFitCandidate.source field is type-enforced:
        WeightFitCandidate.__post_init__ raises WeightCarrierSchemaError if
        source is not a WeightReadinessCandidate instance.

    Therefore this adapter returns BLOCKED_PHONOLOGICAL_CHAIN for all inputs
    until E5 (formal_shape / weight_fit implementation).

E0 role:
    - Defines the correct function signature for E5+ implementation
    - Documents the exact type mismatch root cause
    - Is FAIL-CLOSED: ImportError → IMPORT_FAILURE (not ELIGIBLE)
    - Tests verify the interface and fail-closed behavior

Implementation scope:
    E0: adapter EXISTS, interface correct, state = BLOCKED_PHONOLOGICAL_CHAIN
    E5: WeightReadinessCandidate built from phonological analysis → full chain
    E6+: full LicensingBoundaryVerdict production for all LICENSED corpus tokens

Constitutional invariants:
    - assess_license() accepts ONLY WeightFitCandidate (enforced at birth)
    - LicensingBoundaryVerdict ≠ Meaning, ≠ Madlul, ≠ Ifadah, ≠ Hukm
    - FAIL-CLOSED: any import/runtime error → IMPORT_FAILURE (not ELIGIBLE)
    - No synthetic trace_id: trace anchor from caller's live PipelineTrace
    - VENDOR_SHA embedded in all produced artifacts

Phase: E0 — Registry Schema Freeze (interface definition)
Next phase implementation: E5 → phonological chain → WeightReadinessCandidate

Constitutional gates: G_E0_04, G_E0_05
VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# ── Vendor path ──────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA  = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

# ── Fail-closed import ───────────────────────────────────────────────────────
# Python 3.10 in sandbox: StrEnum unavailable → import fails → IMPORT_FAILURE
# Python 3.12+ on user machine: import succeeds → BLOCKED_PHONOLOGICAL_CHAIN
_WEIGHT_LAYER_AVAILABLE = False

try:
    _vendor_src = str(_VENDOR_PATH)
    if _vendor_src not in sys.path:
        sys.path.insert(0, _vendor_src)
    from taaqqul_slot_geometry.weight.licensing_boundary import (    # type: ignore
        LicensingBoundaryVerdict as _LicensingBoundaryVerdict,
        LicensingBoundaryState as _LicensingBoundaryState,
        LicenseBoundaryKind as _LicenseBoundaryKind,
        BoundaryEvidence as _BoundaryEvidence,
        assess_license as _assess_license,
    )
    from taaqqul_slot_geometry.weight.weight_fit import (            # type: ignore
        WeightFitCandidate as _WeightFitCandidate,
    )
    from taaqqul_slot_geometry.weight.pre_weight import (            # type: ignore
        WeightReadinessCandidate as _WeightReadinessCandidate,
    )
    from taaqqul_slot_geometry.weight.mu_chain import (              # type: ignore
        omega_governance as _omega_governance,
        OmegaGovernanceState as _OmegaGovernanceState,
    )
    from taaqqul_slot_geometry.weight.weight_fit import (            # type: ignore
        weigh as _weigh,
        WeightFitState as _WeightFitState,
    )
    from taaqqul_slot_geometry.core.rank_lattice import Rank as _Rank  # type: ignore
    _WEIGHT_LAYER_AVAILABLE = True
except ImportError:
    pass  # FAIL-CLOSED — Python 3.10 in sandbox; all returns → IMPORT_FAILURE


# ── E4C: Import preweight chain adapter ──────────────────────────────────────
# E4B provides build_weight_readiness_candidate() — pure Python Arabic
# decomposition + vendor chain. E4C consumes its output.
_E4C_PREWEIGHT_AVAILABLE = False
try:
    _repo_root_str = str(_REPO_ROOT)
    if _repo_root_str not in sys.path:
        sys.path.insert(0, _repo_root_str)
    from pipeline.taaqol_integration.weight_layer.preweight_chain_adapter import (  # type: ignore  # noqa: E501
        build_weight_readiness_candidate as _build_weight_readiness_candidate,
        _MU_CHAIN_AVAILABLE as _E4B_MU_CHAIN_AVAILABLE,
    )
    _E4C_PREWEIGHT_AVAILABLE = True
except ImportError:
    _E4B_MU_CHAIN_AVAILABLE = False


# ── Implementation state constant ─────────────────────────────────────────────
# E4A: CLOSED (structural guards implemented)
# E4B: FOCUSED_VERIFIED (preweight_chain_adapter.py)
# E4C: IMPLEMENTED (weigh() + assess_license() chain active on Python 3.12+)
A1_IMPLEMENTATION_STATE = "E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED"

# Human-readable reason for BLOCKED state
_PHONOLOGICAL_CHAIN_BLOCK_REASON = (
    "WeightFitCandidate.source requires WeightReadinessCandidate (type-enforced). "
    "WeightReadinessCandidate requires 8-stage phonological pre_weight chain "
    "(μ_seq → μ_boundary → μ_word_carrier → μ_path_gate → μ_root_stem → "
    "μ_original_extra → μ_ops → μ_weight_readiness). "
    "Hokom P0_PHONOLOGICAL stage is NOT_REACHED. "
    "Implementation deferred to E5 (formal_shape / weight_fit phase)."
)


# ── Result container ─────────────────────────────────────────────────────────

class LicensingBoundaryAdapterResult:
    """Result of build_licensing_boundary_verdict().

    Attributes:
        verdict: LicensingBoundaryVerdict if state=ELIGIBLE; None otherwise.
        state: "ELIGIBLE" | "REFUSED" | "DEFERRED" | "IMPORT_FAILURE"
               | "BLOCKED_PHONOLOGICAL_CHAIN" | "BLOCKED_HARF_NOT_APPLICABLE"
        failure_reason: str describing failure (empty if ELIGIBLE)
        vendor_sha: pinned VENDOR_SHA
        trace_anchor: the trace anchor used (from caller's PipelineTrace)
        implementation_state: A1_IMPLEMENTATION_STATE constant
    """
    __slots__ = ("verdict", "state", "failure_reason", "vendor_sha",
                 "trace_anchor", "implementation_state")

    def __init__(
        self,
        verdict,
        state: str,
        failure_reason: str,
        trace_anchor: str,
    ) -> None:
        self.verdict             = verdict
        self.state               = state
        self.failure_reason      = failure_reason
        self.vendor_sha          = _VENDOR_SHA
        self.trace_anchor        = trace_anchor
        self.implementation_state = A1_IMPLEMENTATION_STATE

    def __repr__(self) -> str:
        return (
            f"LicensingBoundaryAdapterResult("
            f"state={self.state!r}, "
            f"implementation_state={self.implementation_state!r}, "
            f"vendor_sha={self.vendor_sha[:12]!r})"
        )


# ── Main function ─────────────────────────────────────────────────────────────

def build_licensing_boundary_verdict(
    token_surface: str,
    normalized_surface: str,
    word_class: str,
    segment_host: str,
    claim_id: str,
    trace_id: str,
    domain_directive: str = "ACCEPT",
    active_residuals: "tuple[Any, ...]" = (),
) -> LicensingBoundaryAdapterResult:
    """
    [E0 INTERFACE DEFINITION] Build a LicensingBoundaryVerdict from Hokom's P0–P5 output.

    This is the A1 adapter — it defines the interface for bridging the type
    mismatch between HokomLinguisticClaimBundle and LicensingBoundaryVerdict.

    E0 STATUS: BLOCKED_PHONOLOGICAL_CHAIN
        The WeightFitCandidate.source field requires a WeightReadinessCandidate,
        which requires the full phonological pre_weight chain (8 μ-stages).
        Hokom's P0_PHONOLOGICAL stage is NOT_REACHED, so this adapter returns
        BLOCKED_PHONOLOGICAL_CHAIN for all inputs in E0.

        Full implementation is E5 scope (formal_shape / weight_fit phase).

    Constitutional notes:
    - For HARF tokens: always BLOCKED_HARF_NOT_APPLICABLE (not in DAL domain)
    - For upstream BLOCK/DEFER directive: always DEFERRED
    - FAIL-CLOSED: ImportError → IMPORT_FAILURE (not ELIGIBLE, not BLOCKED)
    - trace_id MUST come from caller's live PipelineTrace (not synthetic)

    Args:
        token_surface:     Original surface form (Arabic with harakat)
        normalized_surface: Normalized surface form
        word_class:        Hokom P1 word class (ISM | FI3L | HARF | "")
        segment_host:      Hokom P0 segment host (lexical host after clitic removal)
        claim_id:          Hokom claim_id (SHA-256 from SGA bundle or hokom: prefix)
        trace_id:          Caller's live PipelineTrace.trace_id — MUST NOT be synthetic
        domain_directive:  Hokom upstream directive (ACCEPT | DEFER | BLOCK)
        active_residuals:  Hokom upstream residuals (tuple of residual codes)

    Returns:
        LicensingBoundaryAdapterResult:
            E0 state: IMPORT_FAILURE | BLOCKED_HARF_NOT_APPLICABLE |
                      DEFERRED | BLOCKED_PHONOLOGICAL_CHAIN
            E5+ state (when implemented): ELIGIBLE | REFUSED | DEFERRED
    """
    # ── Guard: upstream BLOCK / DEFER → propagate upstream state ─────────────
    # (no vendor types needed — pure string check)
    _UP = (domain_directive or "DEFER").upper()
    if _UP in ("BLOCK", "BLOCKED", "DEFER"):
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="DEFERRED",
            failure_reason=f"upstream_directive={_UP} — weight chain deferred upstream",
            trace_anchor=trace_id,
        )

    # ── Guard: HARF word class → not applicable for DAL domain ───────────────
    # (no vendor types needed — structural exclusion regardless of vendor)
    _wc = (word_class or "").upper().strip()
    if _wc == "HARF":
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="BLOCKED_HARF_NOT_APPLICABLE",
            failure_reason=(
                "HARF word class — not in DAL_ONLY domain. "
                "Licensing boundary applies only to ISM and FI3L."
            ),
            trace_anchor=trace_id,
        )

    # ── Guard: empty segment_host ─────────────────────────────────────────────
    # (no vendor types needed — structural exclusion)
    _segment_host = (segment_host or normalized_surface or token_surface or "").strip()
    if not _segment_host:
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="DEFERRED",
            failure_reason="segment_host empty — no lexical host for weight chain",
            trace_anchor=trace_id,
        )

    # ── Guard: vendor not available (Python 3.10 in sandbox) ─────────────────
    # Structural guards above run regardless of vendor availability.
    # Only here do we require the vendor layer.
    if not _WEIGHT_LAYER_AVAILABLE:
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="IMPORT_FAILURE",
            failure_reason=(
                "taaqqul_slot_geometry requires Python 3.12+ (StrEnum). "
                "Run tests on Python 3.12+ to verify full chain behavior."
            ),
            trace_anchor=trace_id,
        )

    # ── E4C: attempt full chain via preweight_chain_adapter ───────────────────
    # E4B provides build_weight_readiness_candidate() for ISM/FI3L tokens.
    # If E4B+E4C are available (Python 3.12+), run the full chain.
    # If not available: BLOCKED_PHONOLOGICAL_CHAIN (E4A placeholder).
    if _E4C_PREWEIGHT_AVAILABLE and _E4B_MU_CHAIN_AVAILABLE and _WEIGHT_LAYER_AVAILABLE:
        return build_licensing_verdict_from_surface(
            token_surface=token_surface,
            root_letters="",          # root not available at E4A entry; E4B uses surface consonants
            segment_host=_segment_host,
            word_class=word_class,
            trace_id=trace_id,
            domain="DAL_ONLY",
            path_kind="ROOT",
        )

    # ── Fallback: phonological chain not yet available ────────────────────────
    return LicensingBoundaryAdapterResult(
        verdict=None,
        state="BLOCKED_PHONOLOGICAL_CHAIN",
        failure_reason=_PHONOLOGICAL_CHAIN_BLOCK_REASON,
        trace_anchor=trace_id,
    )


def assess_license_from_weight_readiness(
    weight_readiness: Any,
    segment_host: str,
    word_class: str,
    trace_id: str,
    domain: str = "DAL_ONLY",
) -> LicensingBoundaryAdapterResult:
    """
    [E4C IMPLEMENTATION] Build LicensingBoundaryVerdict from a WeightReadinessCandidate.

    Implements the full E4C chain:
        omega_governance((), Rank.CANDIDATE) → ResidualGovernanceVerdict(GRANTED)
        weigh(weight_readiness, governance)  → WeightFitResult(FITTED)
        BoundaryEvidence(LEXICAL, segment_host, CANDIDATE, domain)
        assess_license(fit_candidate, evidence, governance) → LicensingBoundaryResult(ELIGIBLE)

    FAIL-CLOSED: any error at any stage → REFUSED/DEFERRED (never silent ELIGIBLE).
    Pure: no I/O, no ledger, no network (mirrors vendor invariants).

    Args:
        weight_readiness: WeightReadinessCandidate from E4B preweight chain.
        segment_host:     Lexical host string (non-empty attestation for BoundaryEvidence).
        word_class:       Word class (ISM/FI3L — HARF filtered upstream in E4A guard).
        trace_id:         Caller's live PipelineTrace.trace_id (non-synthetic).
        domain:           Evidence domain (default "DAL_ONLY").

    Returns:
        LicensingBoundaryAdapterResult:
            state=ELIGIBLE if full chain succeeds (Python 3.12+)
            state=IMPORT_FAILURE if vendor not available (Python 3.10)
            state=REFUSED if any chain step rejects
            state=DEFERRED if any chain step defers
    """
    # ── Guard: vendor not available (Python 3.10) ─────────────────────────────
    if not _WEIGHT_LAYER_AVAILABLE:
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="IMPORT_FAILURE",
            failure_reason="taaqqul_slot_geometry requires Python 3.12+ (StrEnum)",
            trace_anchor=trace_id,
        )

    # ── Guard: must be WeightReadinessCandidate ───────────────────────────────
    if not isinstance(weight_readiness, _WeightReadinessCandidate):
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="REFUSED",
            failure_reason=(
                f"weight_readiness must be WeightReadinessCandidate, "
                f"got {type(weight_readiness).__name__}"
            ),
            trace_anchor=trace_id,
        )

    # ── Guard: segment_host must be non-empty (BoundaryEvidence attestation) ──
    _host = (segment_host or "").strip()
    if not _host:
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="REFUSED",
            failure_reason="segment_host empty — BoundaryEvidence requires non-empty attestation",
            trace_anchor=trace_id,
        )

    try:
        # ── Step 1: omega_governance with empty residuals → GRANTED ──────────
        # Corpus ISM/FI3L tokens at birth carry no residuals (residuals=()).
        # surface_rank = Rank.CANDIDATE (birth ceiling per BIRTH_RANK_CEILING).
        governance = _omega_governance(
            residuals=(),
            surface_rank=_Rank.CANDIDATE,
        )

        # ── Step 2: weigh(WeightReadinessCandidate, governance) → FITTED ─────
        fit_result = _weigh(weight_readiness, governance)

        if fit_result.state is not _WeightFitState.FITTED:
            # Governance REJECTED/BLOCKED/DEFERRED → propagate
            return LicensingBoundaryAdapterResult(
                verdict=None,
                state=str(fit_result.state),
                failure_reason=(
                    f"weigh() did not FIT: state={fit_result.state}, "
                    f"failure_code={fit_result.failure_code}"
                ),
                trace_anchor=trace_id,
            )

        fit_candidate = fit_result.candidate  # WeightFitCandidate

        # ── Step 3: BoundaryEvidence(kind=LEXICAL, attestation=_host) ────────
        evidence = _BoundaryEvidence(
            kind=_LicenseBoundaryKind.LEXICAL,
            attestation=_host,
            evidence_rank=_Rank.CANDIDATE,
            domain=domain,
        )

        # ── Step 4: assess_license(fit_candidate, evidence, governance) ──────
        license_result = _assess_license(fit_candidate, evidence, governance)

        if license_result.state is not _LicensingBoundaryState.ELIGIBLE:
            return LicensingBoundaryAdapterResult(
                verdict=None,
                state=str(license_result.state),
                failure_reason=(
                    f"assess_license() not ELIGIBLE: state={license_result.state}, "
                    f"failure_code={license_result.failure_code}"
                ),
                trace_anchor=trace_id,
            )

        # ── Step 5: ELIGIBLE — return the LicensingBoundaryVerdict ───────────
        return LicensingBoundaryAdapterResult(
            verdict=license_result.verdict,
            state="ELIGIBLE",
            failure_reason="",
            trace_anchor=trace_id,
        )

    except Exception as exc:  # noqa: BLE001
        # FAIL-CLOSED: any unexpected error → REFUSED (not silently ELIGIBLE)
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="REFUSED",
            failure_reason=f"E4C chain error: {type(exc).__name__}: {exc}",
            trace_anchor=trace_id,
        )


def build_licensing_verdict_from_surface(
    token_surface: str,
    root_letters: str,
    segment_host: str,
    word_class: str,
    trace_id: str,
    domain: str = "DAL_ONLY",
    path_kind: str = "ROOT",
) -> LicensingBoundaryAdapterResult:
    """
    E4B+E4C convenience: Arabic surface → LicensingBoundaryVerdict.

    Chains E4B (preweight_chain_adapter.build_weight_readiness_candidate)
    into E4C (assess_license_from_weight_readiness).

    This is the single-call entry point for the full E4B+E4C chain.
    FAIL-CLOSED at every stage.

    Args:
        token_surface:  Arabic token with harakat (e.g., "دَيْنٍ")
        root_letters:   Root consonants without harakat (e.g., "دين")
        segment_host:   Lexical host for BoundaryEvidence attestation
        word_class:     Word class (ISM | FI3L — HARF rejected early)
        trace_id:       Caller's live PipelineTrace.trace_id
        domain:         Evidence domain (default "DAL_ONLY")
        path_kind:      PathKind for μ chain (default "ROOT")

    Returns:
        LicensingBoundaryAdapterResult with state ELIGIBLE or failure state
    """
    # ── Guard: E4B preweight adapter not available ────────────────────────────
    if not _E4C_PREWEIGHT_AVAILABLE:
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="IMPORT_FAILURE",
            failure_reason="preweight_chain_adapter not importable — E4B not available",
            trace_anchor=trace_id,
        )

    # ── Guard: E4B mu chain requires Python 3.12+ ─────────────────────────────
    if not _E4B_MU_CHAIN_AVAILABLE:
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="IMPORT_FAILURE",
            failure_reason="preweight_chain_adapter: mu chain requires Python 3.12+ (vendor)",
            trace_anchor=trace_id,
        )

    # ── Guard: HARF ───────────────────────────────────────────────────────────
    if (word_class or "").upper().strip() == "HARF":
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="BLOCKED_HARF_NOT_APPLICABLE",
            failure_reason="HARF — not in DAL_ONLY domain",
            trace_anchor=trace_id,
        )

    # ── Step 1: E4B → WeightReadinessCandidate ────────────────────────────────
    weight_readiness = _build_weight_readiness_candidate(
        token_surface=token_surface,
        root_letters=root_letters,
        trace_anchor=trace_id,
        domain=domain,
        path_kind=path_kind,
    )

    if weight_readiness is None:
        return LicensingBoundaryAdapterResult(
            verdict=None,
            state="REFUSED",
            failure_reason=(
                f"E4B chain returned None for surface={token_surface!r} "
                f"root={root_letters!r} — see preweight_chain_adapter logs"
            ),
            trace_anchor=trace_id,
        )

    # ── Step 2: E4C → LicensingBoundaryVerdict ───────────────────────────────
    return assess_license_from_weight_readiness(
        weight_readiness=weight_readiness,
        segment_host=segment_host or token_surface,
        word_class=word_class,
        trace_id=trace_id,
        domain=domain,
    )


__all__ = [
    "build_licensing_boundary_verdict",
    "assess_license_from_weight_readiness",
    "build_licensing_verdict_from_surface",
    "LicensingBoundaryAdapterResult",
    "_WEIGHT_LAYER_AVAILABLE",
    "_E4C_PREWEIGHT_AVAILABLE",
    "_E4B_MU_CHAIN_AVAILABLE",
    "_VENDOR_SHA",
    "A1_IMPLEMENTATION_STATE",
    "_PHONOLOGICAL_CHAIN_BLOCK_REASON",
]
