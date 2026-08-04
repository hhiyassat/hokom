"""
E8 Relation Candidate Adapter — PR-19

Wraps:
  PR-19: prove_relation_candidate() → RelationVerdict (COMPOSED)

Constitutional invariants (binding):
  - RelationCandidate requires two proven ContractableUnitGeometry instances (PR-18 output)
  - governor_role_claim must be in governor.contractability_profile.admissible_roles
  - dependent_role_claim must be in dependent.contractability_profile.admissible_roles
  - Role claims must NOT be in blocked_roles of the respective unit
  - RelationCandidate is compositional structure — NOT meaning, NOT ifadah, NOT hukm
  - FAIL-CLOSED: all functions return None on Python 3.10 (vendor StrEnum absent)
  - AUTONOMOUS_COMMIT_MODE = 0 (no commit, no tag, no push, no merge)

Default roles for ISM tokens (Ayat al-Dayn corpus):
  - governor_role_claim: "MUBTADA" (subject of nominal sentence)
  - dependent_role_claim: "KHABAR" (predicate of nominal sentence)
  Both are in ISM admissible_roles = ("MUBTADA","KHABAR","MAFOOL_BIH","MUDAF_ILAYH").

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E8 — MAQAM_CONTEXT_BOUNDARY + RELATION_CANDIDATE (PR-19 component)
"""
from __future__ import annotations

from typing import Any, Optional

_VENDOR_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"
_RELATION_AVAILABLE = False
_E7_AVAILABLE = False

# ---------------------------------------------------------------------------
# Vendor imports — StrEnum present only on Python 3.11+; 3.10 → ImportError
# ---------------------------------------------------------------------------

try:
    from taaqqul_slot_geometry.weight.relation_candidate import (
        RelationState as _RelationState,
        prove_relation_candidate as _prove_relation_candidate,
    )
    _RELATION_AVAILABLE = True
except ImportError:
    _RelationState = None  # type: ignore[assignment]
    _prove_relation_candidate = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# E7 + E6 adapter imports (always importable on 3.10; functions return None)
# ---------------------------------------------------------------------------

_build_contractable_unit_geometry: Any = None
_build_e6_from_surface: Any = None

try:
    from pipeline.taaqol_integration.weight_layer.mufrad_semantic_slot_adapter import (
        _VENDOR_SHA as _E7_VENDOR_SHA,
        build_contractable_unit_geometry as _build_contractable_unit_geometry,
    )
    from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
        build_e6_from_surface as _build_e6_from_surface,
    )
    _E7_AVAILABLE = True
except ImportError:
    _E7_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constitutional non-meaning attestation
# ---------------------------------------------------------------------------

_NON_MEANING_PROOF = (
    "relation-candidate: compositional structure proof only; "
    "not meaning, not ifadah, not hukm (E8/PR-19)"
)


# ---------------------------------------------------------------------------
# PR-19: build_relation_candidate
# ---------------------------------------------------------------------------


def build_relation_candidate(
    e6_binding_verdict_governor: Any,
    e6_binding_verdict_dependent: Any,
    governor_word_class: str = "ISM",
    dependent_word_class: str = "ISM",
    governor_role_claim: str = "MUBTADA",
    dependent_role_claim: str = "KHABAR",
    relation_basis: str = "",
) -> Optional[Any]:
    """Prove a RelationCandidate via prove_relation_candidate() (PR-19).

    Accepts two E6 DalMadlulBindingVerdicts, builds ContractableUnitGeometry
    for each via PR-18, then proves the compositional relation.

    Constitutional constraint (re-gated by vendor):
      governor_role_claim in governor.contractability_profile.admissible_roles
      dependent_role_claim in dependent.contractability_profile.admissible_roles
      Neither role claim in blocked_roles of the respective unit.

    Default roles: MUBTADA (governor/subject) + KHABAR (dependent/predicate)
    — canonical nominal sentence (جملة اسمية) relation for ISM corpus tokens.

    Args:
        e6_binding_verdict_governor: DalMadlulBindingVerdict for the governor unit.
        e6_binding_verdict_dependent: DalMadlulBindingVerdict for the dependent unit.
        governor_word_class: "ISM" or "FI3L". Default: "ISM".
        dependent_word_class: "ISM" or "FI3L". Default: "ISM".
        governor_role_claim: Role claimed for the governor. Default: "MUBTADA".
        dependent_role_claim: Role claimed for the dependent. Default: "KHABAR".
        relation_basis: Non-empty string describing the compositional basis.

    Returns:
        RelationVerdict (verdict_state=COMPOSED, candidate=RelationCandidate)
        on success. None on Python 3.10, None inputs, empty relation_basis,
        inadmissible role claim, REFUSED verdict, or any exception.
        FAIL-CLOSED: never raises.
    """
    if not _RELATION_AVAILABLE:
        return None
    if _build_contractable_unit_geometry is None:
        return None
    if e6_binding_verdict_governor is None or e6_binding_verdict_dependent is None:
        return None
    if not relation_basis or not relation_basis.strip():
        return None
    if not governor_role_claim or not governor_role_claim.strip():
        return None
    if not dependent_role_claim or not dependent_role_claim.strip():
        return None
    try:
        gov_unit_verdict = _build_contractable_unit_geometry(
            e6_binding_verdict_governor, governor_word_class
        )
        if gov_unit_verdict is None:
            return None
        if gov_unit_verdict.candidate is None:
            return None

        dep_unit_verdict = _build_contractable_unit_geometry(
            e6_binding_verdict_dependent, dependent_word_class
        )
        if dep_unit_verdict is None:
            return None
        if dep_unit_verdict.candidate is None:
            return None

        governor = gov_unit_verdict.candidate
        dependent = dep_unit_verdict.candidate

        verdict = _prove_relation_candidate(
            governor=governor,
            dependent=dependent,
            relation_basis=relation_basis.strip(),
            governor_role_claim=governor_role_claim.strip(),
            dependent_role_claim=dependent_role_claim.strip(),
        )

        if verdict.verdict_state is not _RelationState.COMPOSED:
            return None
        return verdict
    except Exception:
        return None


def build_e8_relation_from_surfaces(
    gov_token_surface: str,
    gov_root_letters: str,
    gov_segment_host: str,
    gov_word_class: str,
    gov_trace_id: str,
    dep_token_surface: str,
    dep_root_letters: str,
    dep_segment_host: str,
    dep_word_class: str,
    dep_trace_id: str,
    governor_role_claim: str = "MUBTADA",
    dependent_role_claim: str = "KHABAR",
    relation_basis: str = "",
    gov_wad_usage_boundary: str = "",
    dep_wad_usage_boundary: str = "",
    domain: str = "DAL_ONLY",
    path_kind: str = "ROOT",
) -> Optional[Any]:
    """E6+E8 full chain: two Arabic surfaces → RelationVerdict (COMPOSED) | None.

    Runs: E4B+E4C+E5+E6 for each surface (via build_e6_from_surface),
    builds ContractableUnitGeometry for each (via PR-18), then proves
    the compositional relation (PR-19).

    Args:
        gov_token_surface: Arabic surface for the governor unit.
        gov_root_letters: Root consonants for the governor.
        gov_segment_host: Lexical host for the governor.
        gov_word_class: "ISM" or "FI3L" for the governor.
        gov_trace_id: Trace reference for the governor chain.
        dep_token_surface: Arabic surface for the dependent unit.
        dep_root_letters: Root consonants for the dependent.
        dep_segment_host: Lexical host for the dependent.
        dep_word_class: "ISM" or "FI3L" for the dependent.
        dep_trace_id: Trace reference for the dependent chain.
        governor_role_claim: Role for governor. Default: "MUBTADA".
        dependent_role_claim: Role for dependent. Default: "KHABAR".
        relation_basis: Compositional basis. Auto-derived from surfaces if empty.
        gov_wad_usage_boundary: Wad boundary for governor (defaults to surface).
        dep_wad_usage_boundary: Wad boundary for dependent (defaults to surface).
        domain: Registry domain (default "DAL_ONLY").
        path_kind: Weight path kind (default "ROOT").

    Returns:
        RelationVerdict (COMPOSED) | None. FAIL-CLOSED: never raises.
    """
    if not _RELATION_AVAILABLE:
        return None
    if _build_e6_from_surface is None:
        return None
    if not gov_token_surface or not gov_token_surface.strip():
        return None
    if not dep_token_surface or not dep_token_surface.strip():
        return None
    gov_ts = gov_token_surface.strip()
    dep_ts = dep_token_surface.strip()
    try:
        e6_gov = _build_e6_from_surface(
            token_surface=gov_ts,
            root_letters=gov_root_letters,
            segment_host=gov_segment_host,
            word_class=gov_word_class,
            trace_id=gov_trace_id,
            wad_usage_boundary=gov_wad_usage_boundary,
            domain=domain,
            path_kind=path_kind,
        )
        if e6_gov is None:
            return None

        e6_dep = _build_e6_from_surface(
            token_surface=dep_ts,
            root_letters=dep_root_letters,
            segment_host=dep_segment_host,
            word_class=dep_word_class,
            trace_id=dep_trace_id,
            wad_usage_boundary=dep_wad_usage_boundary,
            domain=domain,
            path_kind=path_kind,
        )
        if e6_dep is None:
            return None

        rb = (
            relation_basis.strip()
            if relation_basis and relation_basis.strip()
            else f"nominal_sentence/{gov_ts}+{dep_ts}"
        )

        return build_relation_candidate(
            e6_binding_verdict_governor=e6_gov,
            e6_binding_verdict_dependent=e6_dep,
            governor_word_class=gov_word_class,
            dependent_word_class=dep_word_class,
            governor_role_claim=governor_role_claim,
            dependent_role_claim=dependent_role_claim,
            relation_basis=rb,
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Module invariants (run at import time)
# ---------------------------------------------------------------------------


def _verify_e8_relation_candidate_invariants() -> None:
    """Run at import time — verifies module-level constitutional invariants."""
    assert _VENDOR_SHA == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52", (
        f"VENDOR_SHA mismatch: {_VENDOR_SHA!r}"
    )
    assert isinstance(_RELATION_AVAILABLE, bool), "_RELATION_AVAILABLE must be bool"
    assert isinstance(_E7_AVAILABLE, bool), "_E7_AVAILABLE must be bool"
    assert callable(build_relation_candidate), "build_relation_candidate not callable"
    assert callable(build_e8_relation_from_surfaces), (
        "build_e8_relation_from_surfaces not callable"
    )


_verify_e8_relation_candidate_invariants()
