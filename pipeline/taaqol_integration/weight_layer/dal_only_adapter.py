"""
Dal-Only Adapter — E5_DAL_ONLY_CANDIDATE

CONSTITUTIONAL_RECONCILIATION_01 Phase: E5

Purpose:
    Implements E5: prove_dal(LicensingBoundaryVerdict) → DalBoundaryVerdict.
    This is the terminal phase of the E0→E5 integration chain. A PROVEN
    DalBoundaryVerdict with a DalOnlyCandidate object is the full output of the
    Ayat al-Dayn lexical integration run.

Full constitutional chain (E0→E5):
    E0  = TARGET BASELINE FREEZE (SHAs confirmed)
    E1  = AYAT_AL_DAYN_REGISTRY (74 ISM/FI3L entries)
    E2  = P2 REGISTRY PROJECTION (registry_matches non-None)
    E3  = HOKOM P3/P4/P5 CONTINUITY (REQUIREMENTS_DOCUMENTED)
    E4A = PRECONDITION GUARD (HARF / upstream directive / empty host)
    E4B = PRE-WEIGHT TYPED CARRIERS (decompose_arabic → WeightReadinessCandidate)
    E4C = NATIVE LICENSING BOUNDARY (weigh() + assess_license() → LicensingBoundaryVerdict)
    E5  = DAL-ONLY CANDIDATE (prove_dal() → DalBoundaryVerdict) ← THIS MODULE

prove_dal signature (docs/26):
    prove_dal(
        prior_verdict: LicensingBoundaryVerdict,
        signifier_identity: str,   — token surface (e.g., "دَيْنٍ")
        phonetic_trace_ref: str,   — caller's trace_id (non-empty, non-synthetic)
        graphic_trace_ref: str = "", — optional (empty for Unicode input)
    ) → DalBoundaryVerdict(verdict_state=PROVEN, candidate=DalOnlyCandidate)

DalOnlyCandidate fields (docs/26 §2):
    signifier_identity:       token_surface
    phonetic_trace_ref:       trace_id
    graphic_trace_ref:        "" (Unicode form; no separate graphic trace required)
    prior_licensing_verdict:  LicensingBoundaryVerdict (from E4C)
    dal_rank:                 RankLattice.meet(eligibility_rank, DAL_BOUNDARY_RANK_CEILING)
    residuals:                inherited from prior_verdict.source.residuals (= () for clean E4C)
    trace_ref:                "prove_dal/proven/{signifier_identity}"

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None (not silently PROVEN)
    - prove_dal() accepts ONLY LicensingBoundaryVerdict (enforced at __post_init__)
    - DalOnlyCandidate ≠ meaning, ≠ madlul, ≠ ifadah, ≠ hukm
    - No rank promotion beyond DAL_BOUNDARY_RANK_CEILING (= Rank.CANDIDATE)
    - VENDOR_SHA embedded in module

Python 3.10 compat:
    - build_dal_only_candidate() returns None on Python 3.10 (vendor absent)
    - build_dal_only_from_surface() returns None on Python 3.10
    - No pure-Python stage: E5 is vendor-only (no 3.10-compatible decomposition)

Phase: E5 — DAL-ONLY CANDIDATE
Prior: E4C → LicensingBoundaryVerdict
Terminal: DalBoundaryVerdict(verdict_state=PROVEN, candidate=DalOnlyCandidate)
VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

# ── Vendor path ───────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA  = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

# ── Fail-closed vendor import ─────────────────────────────────────────────────
_DAL_ONLY_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)
    from taaqqul_slot_geometry.weight.dal_only import (  # type: ignore
        DalBoundaryState  as _DalBoundaryState,
        DalBoundaryVerdict as _DalBoundaryVerdict,
        DalOnlyCandidate  as _DalOnlyCandidate,
        prove_dal         as _prove_dal,
    )
    from taaqqul_slot_geometry.weight.licensing_boundary import (  # type: ignore
        LicensingBoundaryVerdict as _LicensingBoundaryVerdict,
    )
    _DAL_ONLY_AVAILABLE = True
except ImportError:
    pass


# ── E4C adapter (for build_dal_only_from_surface convenience) ─────────────────
_E4C_AVAILABLE = False
try:
    _repo_root_str = str(_REPO_ROOT)
    if _repo_root_str not in sys.path:
        sys.path.insert(0, _repo_root_str)
    from pipeline.taaqol_integration.weight_layer.licensing_boundary_adapter import (  # type: ignore  # noqa: E501
        build_licensing_verdict_from_surface as _build_licensing_verdict_from_surface,
    )
    _E4C_AVAILABLE = True
except ImportError:
    pass


# ── E5 core function ──────────────────────────────────────────────────────────

def build_dal_only_candidate(
    licensing_verdict: Any,
    token_surface: str,
    trace_id: str,
    graphic_trace_ref: str = "",
) -> "Optional[Any]":
    """
    E5: Build DalBoundaryVerdict from a LicensingBoundaryVerdict.

    Calls prove_dal(prior_verdict, signifier_identity, phonetic_trace_ref).

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - licensing_verdict is not a LicensingBoundaryVerdict
    - token_surface is empty
    - trace_id is empty
    - prove_dal() refuses (verdict_state=REFUSED)
    - Any unexpected error

    Args:
        licensing_verdict: LicensingBoundaryVerdict from E4C assess_license_from_weight_readiness().
        token_surface:     Arabic token surface (e.g., "دَيْنٍ"). Used as signifier_identity.
        trace_id:          Caller's live PipelineTrace.trace_id (non-empty, non-synthetic).
        graphic_trace_ref: Graphic trace reference (default "" — Unicode text needs no separate graphic trace).

    Returns:
        DalBoundaryVerdict(verdict_state=PROVEN, candidate=DalOnlyCandidate) on success.
        None on failure (fail-closed).
    """
    if not _DAL_ONLY_AVAILABLE:
        return None

    if not token_surface or not token_surface.strip():
        return None

    if not trace_id or not trace_id.strip():
        return None

    if not isinstance(licensing_verdict, _LicensingBoundaryVerdict):
        return None

    try:
        verdict = _prove_dal(
            prior_verdict=licensing_verdict,
            signifier_identity=token_surface,
            phonetic_trace_ref=trace_id,
            graphic_trace_ref=graphic_trace_ref,
        )
        # FAIL-CLOSED: only return a PROVEN verdict
        if verdict.verdict_state is not _DalBoundaryState.PROVEN:
            return None
        return verdict
    except Exception:  # noqa: BLE001
        return None


def build_dal_only_from_surface(
    token_surface: str,
    root_letters: str,
    segment_host: str,
    word_class: str,
    trace_id: str,
    domain: str = "DAL_ONLY",
    path_kind: str = "ROOT",
    graphic_trace_ref: str = "",
) -> "Optional[Any]":
    """
    E4B+E4C+E5 convenience: Arabic surface → DalBoundaryVerdict.

    Chains:
        E4B: build_weight_readiness_candidate(token_surface, root_letters, trace_id)
        E4C: assess_license_from_weight_readiness(weight_readiness, segment_host, ...)
        E5:  prove_dal(licensing_verdict, token_surface, trace_id)

    FAIL-CLOSED at every stage.

    Args:
        token_surface:   Arabic token with harakat (e.g., "دَيْنٍ")
        root_letters:    Root consonants without harakat (e.g., "دين")
        segment_host:    Lexical host for BoundaryEvidence attestation
        word_class:      Word class (ISM | FI3L — HARF rejected in E4A guard)
        trace_id:        Caller's live PipelineTrace.trace_id
        domain:          Evidence domain (default "DAL_ONLY")
        path_kind:       PathKind for μ chain (default "ROOT")
        graphic_trace_ref: Optional graphic trace ref for DalOnlyCandidate

    Returns:
        DalBoundaryVerdict(verdict_state=PROVEN) if full chain succeeds (Python 3.12+)
        None if any stage fails (fail-closed)
    """
    if not _DAL_ONLY_AVAILABLE or not _E4C_AVAILABLE:
        return None

    # ── E4B+E4C: Arabic surface → LicensingBoundaryVerdict ───────────────────
    try:
        licensing_result = _build_licensing_verdict_from_surface(
            token_surface=token_surface,
            root_letters=root_letters,
            segment_host=segment_host or token_surface,
            word_class=word_class,
            trace_id=trace_id,
            domain=domain,
            path_kind=path_kind,
        )
    except Exception:  # noqa: BLE001
        return None

    if licensing_result.state != "ELIGIBLE":
        return None

    if licensing_result.verdict is None:
        return None

    # ── E5: LicensingBoundaryVerdict → DalBoundaryVerdict ────────────────────
    return build_dal_only_candidate(
        licensing_verdict=licensing_result.verdict,
        token_surface=token_surface,
        trace_id=trace_id,
        graphic_trace_ref=graphic_trace_ref,
    )


# ── Module-level invariant assertions ─────────────────────────────────────────

def _verify_e5_invariants() -> None:
    """Verify E5 adapter invariants (import-time)."""
    # INV-E5-1: build_dal_only_candidate returns None on 3.10 (fail-closed)
    result = build_dal_only_candidate(
        licensing_verdict=object(),
        token_surface="دَيْنٍ",
        trace_id="test:e5:invariant",
    )
    if _DAL_ONLY_AVAILABLE:
        # On 3.12+: object() is not LicensingBoundaryVerdict → None
        assert result is None, f"INV-E5-1: expected None for wrong type, got {result!r}"
    else:
        assert result is None, "INV-E5-1: must return None when vendor absent"

    # INV-E5-2: empty token_surface → None
    result2 = build_dal_only_candidate(
        licensing_verdict=object(),
        token_surface="",
        trace_id="test:e5:invariant",
    )
    assert result2 is None, "INV-E5-2: empty token_surface must return None"

    # INV-E5-3: empty trace_id → None
    result3 = build_dal_only_candidate(
        licensing_verdict=object(),
        token_surface="دَيْنٍ",
        trace_id="",
    )
    assert result3 is None, "INV-E5-3: empty trace_id must return None"


_verify_e5_invariants()


__all__ = [
    "build_dal_only_candidate",
    "build_dal_only_from_surface",
    "_DAL_ONLY_AVAILABLE",
    "_E4C_AVAILABLE",
    "_VENDOR_SHA",
]
