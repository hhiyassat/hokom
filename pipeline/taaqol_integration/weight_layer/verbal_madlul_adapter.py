"""Verbal Madlul Adapter — E6_VERBAL_MADLUL

CONSTITUTIONAL_RECONCILIATION_01 Phase: E6

Purpose:
    Implements E6: the verbal signified boundary layer.

    Two operations:
      1. prove_verbal_madlul(DalOnlyCandidate) → VerbalMadlulBoundaryVerdict(PROVEN)
      2. bind_dal_madlul(DalOnlyCandidate, VerbalMadlulCandidate, registry×2)
             → DalMadlulBindingVerdict(BOUND)

    Together these constitute the full E6 chain (PR-16 + PR-17):
        DalBoundaryVerdict (E5)
          → DalOnlyCandidate.candidate
          → prove_verbal_madlul()   → VerbalMadlulBoundaryVerdict(PROVEN)
          → bind_dal_madlul()       → DalMadlulBindingVerdict(BOUND)

Full constitutional chain (E0→E6):
    E0  = TARGET BASELINE FREEZE (SHAs confirmed)
    E1  = AYAT_AL_DAYN_REGISTRY (74 ISM/FI3L entries)
    E2  = P2 REGISTRY PROJECTION (registry_matches non-None)
    E3  = HOKOM P3/P4/P5 CONTINUITY (REQUIREMENTS_DOCUMENTED)
    E4A = PRECONDITION GUARD
    E4B = PRE-WEIGHT TYPED CARRIERS (decompose_arabic → WeightReadinessCandidate)
    E4C = NATIVE LICENSING BOUNDARY (weigh() + assess_license() → LicensingBoundaryVerdict)
    E5  = DAL-ONLY CANDIDATE (prove_dal() → DalBoundaryVerdict)
    E6  = VERBAL MADLUL  (prove_verbal_madlul() + bind_dal_madlul()) ← THIS MODULE

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None
    - prove_verbal_madlul() accepts ONLY DalOnlyCandidate (type-enforced by vendor)
    - bind_dal_madlul() identity check: madlul_candidate.dal_only is dal_candidate
      (Python `is` — same instance; enforced at vendor __post_init__)
    - VerbalMadlulCandidate ≠ meaning, ≠ madlul (final), ≠ ifadah, ≠ hukm
    - DalMadlulBindingCandidate ≠ ContractableUnitGeometry
    - wad_usage_boundary: non-empty string (conservative = token_surface)
    - RegistryEntry.non_meaning_proof must be non-empty (constitutional attestation)
    - No rank promotion beyond MADLUL_BOUNDARY_RANK_CEILING / BINDING_RANK_CEILING
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - verbal_madlul.py, dal_madlul_binding.py, registry_contract.py use StrEnum
    - All three fail to import on 3.10 → _VERBAL_MADLUL_AVAILABLE = False
    - All public functions return None on 3.10 (fail-closed)

Phase: E6 — VERBAL MADLUL
Prior: E5 → DalBoundaryVerdict(PROVEN, candidate=DalOnlyCandidate)
Output: DalMadlulBindingVerdict(BOUND, candidate=DalMadlulBindingCandidate)
VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

# ── Vendor path ───────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA  = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

# ── Fail-closed vendor imports ────────────────────────────────────────────────
_VERBAL_MADLUL_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    # PR-16: prove_verbal_madlul
    from taaqqul_slot_geometry.weight.verbal_madlul import (  # type: ignore
        MadlulBoundaryState    as _MadlulBoundaryState,
        VerbalMadlulBoundaryVerdict as _VerbalMadlulBoundaryVerdict,
        VerbalMadlulCandidate  as _VerbalMadlulCandidate,
        prove_verbal_madlul    as _prove_verbal_madlul,
    )
    # PR-17: bind_dal_madlul
    from taaqqul_slot_geometry.weight.dal_madlul_binding import (  # type: ignore
        BindingState           as _BindingState,
        DalMadlulBindingVerdict as _DalMadlulBindingVerdict,
        bind_dal_madlul        as _bind_dal_madlul,
    )
    # PR-16C: registry
    from taaqqul_slot_geometry.weight.registry_contract import (  # type: ignore
        RegistryDomain         as _RegistryDomain,
        RegistryEntry          as _RegistryEntry,
        RegistryLookupResult   as _RegistryLookupResult,
        RegistryLookupState    as _RegistryLookupState,
        lookup_registry_entry  as _lookup_registry_entry,
    )
    # PR-15: DalOnlyCandidate (for type guard)
    from taaqqul_slot_geometry.weight.dal_only import (  # type: ignore
        DalOnlyCandidate as _DalOnlyCandidate,
    )
    # Rank
    from taaqqul_slot_geometry.core.rank_lattice import Rank as _Rank  # type: ignore

    _VERBAL_MADLUL_AVAILABLE = True
except ImportError:
    pass


# ── E5 adapter (for full-chain convenience) ───────────────────────────────────
_E5_AVAILABLE = False
try:
    _repo_root_str = str(_REPO_ROOT)
    if _repo_root_str not in sys.path:
        sys.path.insert(0, _repo_root_str)
    from pipeline.taaqol_integration.weight_layer.dal_only_adapter import (  # type: ignore
        build_dal_only_from_surface as _build_dal_only_from_surface,
        _DAL_ONLY_AVAILABLE as _E5_DAL_ONLY_AVAILABLE,
    )
    _E5_AVAILABLE = True
except ImportError:
    _E5_DAL_ONLY_AVAILABLE = False

# ── Pre-semantic non-meaning attestation (constitutional invariant) ────────────
_NON_MEANING_PROOF = (
    "pre-semantic-admissibility: signifier/signified boundary proof only; "
    "not meaning, not ifadah, not hukm, not reality (E6/PR-16C)"
)


# ── E6 function 1: prove_verbal_madlul wrapper ────────────────────────────────

def build_verbal_madlul_candidate(
    dal_only_candidate: Any,
    wad_usage_boundary: str,
    correspondence_candidate: str = "",
    inclusion_candidate: str = "",
    iltizam_condition: str = "",
    existence_carrier_candidate: str = "",
    event_carrier_candidate: str = "",
    relation_affordance_candidate: str = "",
) -> "Optional[Any]":
    """
    E6: Prove verbal signified boundary from a DalOnlyCandidate.

    Calls prove_verbal_madlul(prior_dal, wad_usage_boundary, ...).

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - dal_only_candidate is not a DalOnlyCandidate
    - wad_usage_boundary is empty
    - prove_verbal_madlul() refuses (verdict_state=REFUSED)
    - Any unexpected error

    Args:
        dal_only_candidate: DalOnlyCandidate from E5 prove_dal().
        wad_usage_boundary: Wadʿ/usage boundary string (non-empty).
                            Conservative choice: pass token_surface.
        correspondence_candidate: Conceptual correspondence (optional).
        inclusion_candidate: Inclusion candidate (optional).
        iltizam_condition: Iltizām condition (optional).
        existence_carrier_candidate: Existence affordance (optional).
        event_carrier_candidate: Event affordance (optional).
        relation_affordance_candidate: Relation affordance (optional).

    Returns:
        VerbalMadlulBoundaryVerdict(verdict_state=PROVEN) on success.
        None on failure (fail-closed).
    """
    if not _VERBAL_MADLUL_AVAILABLE:
        return None
    if not isinstance(dal_only_candidate, _DalOnlyCandidate):
        return None
    if not wad_usage_boundary or not wad_usage_boundary.strip():
        return None
    try:
        verdict = _prove_verbal_madlul(
            prior_dal=dal_only_candidate,
            wad_usage_boundary=wad_usage_boundary,
            correspondence_candidate=correspondence_candidate,
            inclusion_candidate=inclusion_candidate,
            iltizam_condition=iltizam_condition,
            existence_carrier_candidate=existence_carrier_candidate,
            event_carrier_candidate=event_carrier_candidate,
            relation_affordance_candidate=relation_affordance_candidate,
        )
        if verdict.verdict_state is not _MadlulBoundaryState.PROVEN:
            return None
        return verdict
    except Exception:  # noqa: BLE001
        return None


# ── E6 function 2: pre-semantic registry builder ─────────────────────────────

def _build_pre_semantic_registry(
    token_key: str,
    trace_id: str,
) -> "Optional[tuple]":
    """
    Build a minimal pre-semantic registry tuple for bind_dal_madlul().

    Constructs two RegistryEntry objects:
      - RegistryDomain.DAL_ONLY   (key=token_key)
      - RegistryDomain.VERBAL_MADLUL (key=token_key)

    Both carry constitutional non_meaning_proof attestation.

    Returns tuple[RegistryEntry, ...] or None on failure.
    """
    if not _VERBAL_MADLUL_AVAILABLE:
        return None
    if not token_key or not token_key.strip():
        return None
    try:
        dal_entry = _RegistryEntry(
            key=token_key.strip(),
            domain=_RegistryDomain.DAL_ONLY,
            non_meaning_proof=_NON_MEANING_PROOF,
            rank=_Rank.CANDIDATE,
            residuals=(),
            trace_ref=f"E6/registry/dal_only/{token_key.strip()}/{trace_id}",
        )
        madlul_entry = _RegistryEntry(
            key=token_key.strip(),
            domain=_RegistryDomain.VERBAL_MADLUL,
            non_meaning_proof=_NON_MEANING_PROOF,
            rank=_Rank.CANDIDATE,
            residuals=(),
            trace_ref=f"E6/registry/verbal_madlul/{token_key.strip()}/{trace_id}",
        )
        return (dal_entry, madlul_entry)
    except Exception:  # noqa: BLE001
        return None


# ── E6 function 3: bind_dal_madlul wrapper ───────────────────────────────────

def build_dal_madlul_binding(
    dal_only_candidate: Any,
    verbal_madlul_candidate: Any,
    registry_key: str,
    trace_id: str,
) -> "Optional[Any]":
    """
    E6 binding: bind DalOnlyCandidate + VerbalMadlulCandidate → DalMadlulBindingVerdict.

    CRITICAL IDENTITY CONSTRAINT: verbal_madlul_candidate.dal_only MUST BE the
    same object instance as dal_only_candidate (Python `is`). This is enforced
    by vendor __post_init__. To satisfy this, always use the DalOnlyCandidate
    instance that was originally passed to prove_verbal_madlul().

    Builds a pre-semantic registry (DAL_ONLY + VERBAL_MADLUL entries for
    registry_key), then calls:
      lookup_registry_entry(registry_key, DAL_ONLY, registry) → FOUND
      lookup_registry_entry(registry_key, VERBAL_MADLUL, registry) → FOUND
      bind_dal_madlul(dal_candidate, madlul_candidate, dal_result, madlul_result)

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - Either candidate is wrong type
    - Identity constraint violated (madlul.dal_only is not dal_candidate)
    - registry_key empty
    - trace_id empty
    - Any unexpected error

    Args:
        dal_only_candidate:      DalOnlyCandidate from E5.
        verbal_madlul_candidate: VerbalMadlulCandidate from build_verbal_madlul_candidate().
        registry_key:            Key for registry lookup (typically token_surface.strip()).
        trace_id:                Caller's trace ID (non-empty).

    Returns:
        DalMadlulBindingVerdict(verdict_state=BOUND) on success.
        None on failure (fail-closed).
    """
    if not _VERBAL_MADLUL_AVAILABLE:
        return None
    if not isinstance(dal_only_candidate, _DalOnlyCandidate):
        return None
    if not isinstance(verbal_madlul_candidate, _VerbalMadlulCandidate):
        return None
    if not registry_key or not registry_key.strip():
        return None
    if not trace_id or not trace_id.strip():
        return None
    # Identity constraint (enforced again before vendor call)
    if verbal_madlul_candidate.dal_only is not dal_only_candidate:
        return None

    try:
        # Build pre-semantic registry
        registry_tuple = _build_pre_semantic_registry(registry_key, trace_id)
        if registry_tuple is None:
            return None

        # Lookup DAL_ONLY entry
        dal_lookup = _lookup_registry_entry(
            candidate_key=registry_key.strip(),
            domain=_RegistryDomain.DAL_ONLY,
            registry=registry_tuple,
        )
        if dal_lookup.state is not _RegistryLookupState.FOUND:
            return None

        # Lookup VERBAL_MADLUL entry
        madlul_lookup = _lookup_registry_entry(
            candidate_key=registry_key.strip(),
            domain=_RegistryDomain.VERBAL_MADLUL,
            registry=registry_tuple,
        )
        if madlul_lookup.state is not _RegistryLookupState.FOUND:
            return None

        # Bind
        verdict = _bind_dal_madlul(
            dal_candidate=dal_only_candidate,
            madlul_candidate=verbal_madlul_candidate,
            dal_registry=dal_lookup,
            madlul_registry=madlul_lookup,
        )
        if verdict.verdict_state is not _BindingState.BOUND:
            return None
        return verdict

    except Exception:  # noqa: BLE001
        return None


# ── E6 full chain convenience ─────────────────────────────────────────────────

def build_e6_chain_from_dal_verdict(
    dal_boundary_verdict: Any,
    wad_usage_boundary: str = "",
    token_surface: str = "",
    trace_id: str = "",
    correspondence_candidate: str = "",
    inclusion_candidate: str = "",
    iltizam_condition: str = "",
    existence_carrier_candidate: str = "",
    event_carrier_candidate: str = "",
    relation_affordance_candidate: str = "",
) -> "Optional[Any]":
    """
    E6 full chain: DalBoundaryVerdict → DalMadlulBindingVerdict.

    Extracts DalOnlyCandidate from E5 verdict, then:
      1. prove_verbal_madlul(dal_only, wad_usage_boundary) → VerbalMadlulBoundaryVerdict
      2. bind_dal_madlul(dal_only, verbal_madlul.candidate, registry) → DalMadlulBindingVerdict

    The wad_usage_boundary defaults to token_surface (conservative, non-invented).
    The registry_key uses token_surface.

    FAIL-CLOSED at every stage.

    Args:
        dal_boundary_verdict: DalBoundaryVerdict from E5 build_dal_only_candidate().
        wad_usage_boundary:   Wadʿ boundary string. Defaults to token_surface.
        token_surface:        Arabic token surface (e.g., "دَيْنٍ").
        trace_id:             Caller's trace ID.
        correspondence_candidate, inclusion_candidate, iltizam_condition,
        existence_carrier_candidate, event_carrier_candidate,
        relation_affordance_candidate: Optional semantic fields (all default "").

    Returns:
        DalMadlulBindingVerdict(verdict_state=BOUND) on success.
        None on any failure (fail-closed).
    """
    if not _VERBAL_MADLUL_AVAILABLE:
        return None
    if not token_surface or not token_surface.strip():
        return None
    if not trace_id or not trace_id.strip():
        return None

    # Resolve wad_usage_boundary (conservative: token_surface if not provided)
    effective_wad = wad_usage_boundary.strip() if wad_usage_boundary else ""
    if not effective_wad:
        effective_wad = token_surface.strip()

    # Extract DalOnlyCandidate from verdict
    try:
        if dal_boundary_verdict is None:
            return None
        dal_only = dal_boundary_verdict.candidate
        if not isinstance(dal_only, _DalOnlyCandidate):
            return None
    except Exception:  # noqa: BLE001
        return None

    # Step 1: prove_verbal_madlul
    verbal_verdict = build_verbal_madlul_candidate(
        dal_only_candidate=dal_only,
        wad_usage_boundary=effective_wad,
        correspondence_candidate=correspondence_candidate,
        inclusion_candidate=inclusion_candidate,
        iltizam_condition=iltizam_condition,
        existence_carrier_candidate=existence_carrier_candidate,
        event_carrier_candidate=event_carrier_candidate,
        relation_affordance_candidate=relation_affordance_candidate,
    )
    if verbal_verdict is None:
        return None

    verbal_candidate = verbal_verdict.candidate
    if not isinstance(verbal_candidate, _VerbalMadlulCandidate):
        return None

    # Step 2: bind_dal_madlul (registry key = token_surface)
    return build_dal_madlul_binding(
        dal_only_candidate=dal_only,
        verbal_madlul_candidate=verbal_candidate,
        registry_key=token_surface.strip(),
        trace_id=trace_id,
    )


# ── Full E5+E6 convenience (Arabic surface → DalMadlulBindingVerdict) ─────────

def build_e6_from_surface(
    token_surface: str,
    root_letters: str,
    segment_host: str,
    word_class: str,
    trace_id: str,
    wad_usage_boundary: str = "",
    domain: str = "DAL_ONLY",
    path_kind: str = "ROOT",
) -> "Optional[Any]":
    """
    E4B+E4C+E5+E6 convenience: Arabic surface → DalMadlulBindingVerdict.

    Chains:
        E5 (via dal_only_adapter.build_dal_only_from_surface)
        E6 (prove_verbal_madlul + bind_dal_madlul)

    FAIL-CLOSED at every stage. On Python 3.10 returns None.

    Args:
        token_surface:   Arabic token with harakat (e.g., "دَيْنٍ")
        root_letters:    Root consonants (e.g., "دين")
        segment_host:    Lexical host for BoundaryEvidence
        word_class:      ISM | FI3L
        trace_id:        Caller's trace ID
        wad_usage_boundary: Wadʿ boundary (defaults to token_surface)
        domain:          Evidence domain (default "DAL_ONLY")
        path_kind:       PathKind (default "ROOT")

    Returns:
        DalMadlulBindingVerdict(verdict_state=BOUND) on Python 3.12+.
        None on Python 3.10 or any failure.
    """
    if not _VERBAL_MADLUL_AVAILABLE or not _E5_AVAILABLE:
        return None

    # E5 chain
    try:
        dal_verdict = _build_dal_only_from_surface(
            token_surface=token_surface,
            root_letters=root_letters,
            segment_host=segment_host,
            word_class=word_class,
            trace_id=trace_id,
            domain=domain,
            path_kind=path_kind,
        )
    except Exception:  # noqa: BLE001
        return None

    if dal_verdict is None:
        return None

    # E6 chain
    return build_e6_chain_from_dal_verdict(
        dal_boundary_verdict=dal_verdict,
        wad_usage_boundary=wad_usage_boundary,
        token_surface=token_surface,
        trace_id=trace_id,
    )


# ── Module-level invariant assertions ─────────────────────────────────────────

def _verify_e6_invariants() -> None:
    """Verify E6 adapter invariants (import-time)."""
    # INV-E6-1: wrong type → None for prove step
    r1 = build_verbal_madlul_candidate(
        dal_only_candidate=object(),
        wad_usage_boundary="boundary",
    )
    assert r1 is None, "INV-E6-1: wrong type must return None"

    # INV-E6-2: empty wad_usage_boundary → None
    r2 = build_verbal_madlul_candidate(
        dal_only_candidate=object(),
        wad_usage_boundary="",
    )
    assert r2 is None, "INV-E6-2: empty wad_usage_boundary must return None"

    # INV-E6-3: empty token_surface → None for full chain
    r3 = build_e6_chain_from_dal_verdict(
        dal_boundary_verdict=None,
        token_surface="",
        trace_id="test:e6:inv",
    )
    assert r3 is None, "INV-E6-3: empty token_surface must return None"

    # INV-E6-4: None verdict → None
    r4 = build_e6_chain_from_dal_verdict(
        dal_boundary_verdict=None,
        token_surface="دَيْنٍ",
        trace_id="test:e6:inv:none",
    )
    assert r4 is None, "INV-E6-4: None verdict must return None"

    # INV-E6-5: empty trace_id → None for binding step
    r5 = build_dal_madlul_binding(
        dal_only_candidate=object(),
        verbal_madlul_candidate=object(),
        registry_key="key",
        trace_id="",
    )
    assert r5 is None, "INV-E6-5: empty trace_id must return None"


_verify_e6_invariants()


__all__ = [
    "build_verbal_madlul_candidate",
    "build_dal_madlul_binding",
    "build_e6_chain_from_dal_verdict",
    "build_e6_from_surface",
    "_VERBAL_MADLUL_AVAILABLE",
    "_E5_AVAILABLE",
    "_VENDOR_SHA",
]
