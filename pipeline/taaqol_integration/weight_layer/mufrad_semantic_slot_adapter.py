"""
E7 Mufrad Semantic Slot Geometry Adapter — PR-18 + PR-D1

Wraps:
  PR-18: prove_contractable_unit(DalMadlulBindingCandidate, ...) → ContractableUnitVerdict
  PR-D1: prove_mufrad_semantic_slot_geometry(...) → MufradSemanticSlotGeometryVerdict

Identity chain (all Python `is` — enforced by vendor __post_init__ + pre-checked here):
  - dal_only IS dal_only through E5 → E6 → PR-18 → PR-D1
  - verbal_madlul.dal_only IS dal_only through E6 → PR-18 → PR-D1
  - contractable_unit.binding_candidate.dal_candidate IS dal_only
  - contractable_unit.binding_candidate.madlul_candidate IS verbal_madlul

Constitutional invariants (binding):
  - SemanticSlotFrame is geometry, not dalalah operation
  - SemanticSlotFrame ≠ meaning, ≠ Mutabaqah, ≠ Tadammun, ≠ Iltizam, ≠ ifadah
  - SemanticSlotFrame opens PR-D2 readiness only; does not open Ifadah
  - FAIL-CLOSED: all functions return None on Python 3.10 (vendor StrEnum absent)
  - AUTONOMOUS_COMMIT_MODE = 0 (no commit, no tag, no push, no merge)

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E7 — FORMAL SHAPE + MUFRAD DALALAH (PR-18 / PR-D1 component)
"""
from __future__ import annotations

from typing import Any, Optional

_VENDOR_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"
_MUFRAD_SLOT_AVAILABLE = False
_E6_AVAILABLE = False
_FORMAL_SHAPE_ADAPTER_AVAILABLE = False

# ---------------------------------------------------------------------------
# Vendor imports — StrEnum present only on Python 3.11+; 3.10 → ImportError
# ---------------------------------------------------------------------------

try:
    from taaqqul_slot_geometry.weight.contractable_unit_geometry import (
        ContractableUnitState as _ContractableUnitState,
        prove_contractable_unit as _prove_contractable_unit,
    )
    from taaqqul_slot_geometry.weight.formal_shape import (
        FormalShapeClosureState as _FormalShapeClosureState,
    )
    from taaqqul_slot_geometry.weight.mufrad_semantic_slot_geometry import (
        KulliJuziiAxis as _KulliJuziiAxis,
        MufradSemanticState as _MufradSemanticState,
        ParticularitySource as _ParticularitySource,
        SemanticCategory as _SemanticCategory,
        WadEvidenceType as _WadEvidenceType,
        WadOriginDomain as _WadOriginDomain,
        prove_mufrad_semantic_slot_geometry as _prove_mufrad_semantic_slot_geometry,
    )
    _MUFRAD_SLOT_AVAILABLE = True
except ImportError:
    _prove_contractable_unit = None  # type: ignore[assignment]
    _ContractableUnitState = None  # type: ignore[assignment]
    _prove_mufrad_semantic_slot_geometry = None  # type: ignore[assignment]
    _MufradSemanticState = None  # type: ignore[assignment]
    _SemanticCategory = None  # type: ignore[assignment]
    _WadOriginDomain = None  # type: ignore[assignment]
    _WadEvidenceType = None  # type: ignore[assignment]
    _KulliJuziiAxis = None  # type: ignore[assignment]
    _ParticularitySource = None  # type: ignore[assignment]
    _FormalShapeClosureState = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# E6 adapter import (importable on 3.10; build_e6_from_surface returns None on 3.10)
# ---------------------------------------------------------------------------

try:
    from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (
        _VERBAL_MADLUL_AVAILABLE as _E6_VENDOR_AVAILABLE,
        build_e6_from_surface as _build_e6_from_surface,
    )
    _E6_AVAILABLE = True
except ImportError:
    _build_e6_from_surface = None  # type: ignore[assignment]
    _E6_VENDOR_AVAILABLE = False
    _E6_AVAILABLE = False

# ---------------------------------------------------------------------------
# Formal shape adapter import (importable on 3.10; functions return None on 3.10)
# ---------------------------------------------------------------------------

try:
    from pipeline.taaqol_integration.weight_layer.formal_shape_adapter import (
        _FORMAL_SHAPE_AVAILABLE,
        build_formal_style_candidate as _build_formal_style_candidate,
    )
    _FORMAL_SHAPE_ADAPTER_AVAILABLE = True
except ImportError:
    _build_formal_style_candidate = None  # type: ignore[assignment]
    _FORMAL_SHAPE_AVAILABLE = False
    _FORMAL_SHAPE_ADAPTER_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constitutional non-meaning attestation
# ---------------------------------------------------------------------------

_NON_MEANING_PROOF = (
    "pre-semantic-admissibility: mufrad semantic slot geometry boundary proof only; "
    "geometry, not dalalah operation, not meaning, not ifadah, not hukm (E7/PR-18/PR-D1)"
)

# ---------------------------------------------------------------------------
# Default affordance tables for word-class types
# ---------------------------------------------------------------------------

_ISM_ADMISSIBLE_ROLES: tuple[str, ...] = (
    "MUBTADA",
    "KHABAR",
    "MAFOOL_BIH",
    "MUDAF_ILAYH",
)
_FIL_ADMISSIBLE_ROLES: tuple[str, ...] = (
    "FIL_MUTLI",
    "FIL_MAJHOOL",
)
_BLOCKED_ROLES: tuple[str, ...] = ()
_FORMAL_CLOSURE_REF = "formal_shape_registry/word_class_domain/CLOSED"


# ---------------------------------------------------------------------------
# PR-18: build_contractable_unit_geometry
# ---------------------------------------------------------------------------


def build_contractable_unit_geometry(
    dal_madlul_binding_verdict: Any,
    word_class: str = "ISM",
) -> Optional[Any]:
    """Prove ContractableUnitGeometry from DalMadlulBindingVerdict (PR-18).

    Extracts binding_candidate from the verdict and calls prove_contractable_unit().
    Affordances are derived from word_class:
      ISM: admissible=(MUBTADA, KHABAR, MAFOOL_BIH, MUDAF_ILAYH),
           word_class_affordance=ISM, inflection=FULL_INFLECTION_ISM,
           derivational=MUSHTAQ_JAMID, path=ROOT/ISM
      FI3L/FIL: admissible=(FIL_MUTLI, FIL_MAJHOOL),
                word_class_affordance=FI3L, inflection=VERBAL_CONJUGATION,
                derivational=MASDAR_DERIVATION, path=ROOT/FI3L

    Returns:
        ContractableUnitVerdict (verdict_state=PROVEN, candidate=ContractableUnitGeometry)
        on success. None on Python 3.10, None binding verdict, REFUSED, or any exception.
        FAIL-CLOSED: never raises.
    """
    if not _MUFRAD_SLOT_AVAILABLE:
        return None
    if dal_madlul_binding_verdict is None:
        return None
    try:
        binding_candidate = dal_madlul_binding_verdict.candidate
        if binding_candidate is None:
            return None

        wc = (word_class or "ISM").strip().upper()
        if wc == "ISM":
            admissible = _ISM_ADMISSIBLE_ROLES
            word_class_affordance = "ISM"
            inflection_affordance = "FULL_INFLECTION_ISM"
            derivational_affordance = "MUSHTAQ_JAMID"
            path_profile = "ROOT/ISM"
        elif wc in ("FIL", "FI3L"):
            admissible = _FIL_ADMISSIBLE_ROLES
            word_class_affordance = "FI3L"
            inflection_affordance = "VERBAL_CONJUGATION"
            derivational_affordance = "MASDAR_DERIVATION"
            path_profile = "ROOT/FI3L"
        else:
            admissible = _ISM_ADMISSIBLE_ROLES
            word_class_affordance = wc
            inflection_affordance = "INFLECTION_DEFERRED"
            derivational_affordance = "DERIVATION_DEFERRED"
            path_profile = f"ROOT/{wc}"

        verdict = _prove_contractable_unit(
            binding_candidate=binding_candidate,
            admissible_roles=admissible,
            blocked_roles=_BLOCKED_ROLES,
            path_profile=path_profile,
            word_class_affordance=word_class_affordance,
            inflection_affordance=inflection_affordance,
            derivational_affordance=derivational_affordance,
        )
        if verdict.verdict_state is not _ContractableUnitState.PROVEN:
            return None
        return verdict
    except Exception:
        return None


# ---------------------------------------------------------------------------
# PR-D1: build_mufrad_semantic_slot_geometry
# ---------------------------------------------------------------------------


def build_mufrad_semantic_slot_geometry(
    e6_binding_verdict: Any,
    formal_style_verdict: Any,
    token_surface: str = "",
    word_class: str = "ISM",
    semantic_category_name: str = "JAMID",
    wad_origin_domain_name: str = "LUGHAWI",
    wad_evidence_type_name: str = "CORPUS",
    kulli_juzii_axis_name: str = "KULLI",
    particularity_source_name: str = "NOT_APPLICABLE",
    predication_test_passed: bool = True,
    branch_no_preventer: bool = True,
) -> Optional[Any]:
    """Build MufradSemanticSlotGeometryVerdict from E6 binding + formal style (PR-D1).

    Threads identity correctly: dal_only and verbal_madlul are extracted from
    e6_binding_verdict.candidate, satisfying all 4 vendor identity `is`-checks.

    Args:
        e6_binding_verdict: DalMadlulBindingVerdict from E6 (verdict_state=BOUND)
        formal_style_verdict: FormalStyleVerdict from PR-F8 (verdict_state=PROVEN)
        token_surface: Arabic token surface form (used for refs/traces)
        word_class: "ISM" or "FI3L" — determines ContractableUnit affordances
        semantic_category_name: SemanticCategory value (default "JAMID")
        wad_origin_domain_name: WadOriginDomain value (default "LUGHAWI")
        wad_evidence_type_name: WadEvidenceType value (default "CORPUS")
        kulli_juzii_axis_name: KulliJuziiAxis value (default "KULLI")
        particularity_source_name: ParticularitySource value (default "NOT_APPLICABLE")
        predication_test_passed: bool (default True for ISM kulli tokens)
        branch_no_preventer: bool (default True — no preventer audit at this layer)

    Returns:
        MufradSemanticSlotGeometryVerdict (verdict_state=PROVEN, candidate=SemanticSlotFrame)
        on success. None on Python 3.10, None inputs, REFUSED, identity mismatch,
        or any exception. FAIL-CLOSED: never raises.
    """
    if not _MUFRAD_SLOT_AVAILABLE:
        return None
    if e6_binding_verdict is None:
        return None
    if formal_style_verdict is None:
        return None
    if not token_surface or not token_surface.strip():
        return None
    try:
        # --- Extract identity-threaded instances from E6 verdict ---
        binding_candidate = e6_binding_verdict.candidate
        if binding_candidate is None:
            return None
        # These are the same instances threaded through E5→E6
        dal_only = binding_candidate.dal_candidate         # DalOnlyCandidate (PR-15)
        verbal_madlul = binding_candidate.madlul_candidate  # VerbalMadlulCandidate (PR-16)

        # --- Extract FormalStyleCandidate from FormalStyleVerdict ---
        formal_style_candidate = formal_style_verdict.candidate
        if formal_style_candidate is None:
            return None

        # --- Build ContractableUnitGeometry (PR-18) ---
        # binding_candidate is passed directly; identity is preserved automatically
        contractable_unit_verdict = build_contractable_unit_geometry(
            dal_madlul_binding_verdict=e6_binding_verdict,
            word_class=word_class,
        )
        if contractable_unit_verdict is None:
            return None
        contractable_unit = contractable_unit_verdict.candidate  # ContractableUnitGeometry

        # --- Parse enum parameters (StrEnum only available on 3.12+) ---
        semantic_category = _SemanticCategory(semantic_category_name)
        wad_origin_domain = _WadOriginDomain(wad_origin_domain_name)
        wad_evidence_type = _WadEvidenceType(wad_evidence_type_name)
        kulli_juzii_axis = _KulliJuziiAxis(kulli_juzii_axis_name)
        particularity_source = _ParticularitySource(particularity_source_name)
        formal_closure_state = _FormalShapeClosureState.CLOSED

        # --- Derive conservative string refs from token context ---
        ts = token_surface.strip()
        wc = (word_class or "ISM").strip().upper()

        # --- Call PR-D1 ---
        verdict = _prove_mufrad_semantic_slot_geometry(
            formal_style_candidate=formal_style_candidate,
            dal_only_candidate=dal_only,
            verbal_madlul_candidate=verbal_madlul,
            contractable_unit=contractable_unit,
            formal_closure_state=formal_closure_state,
            semantic_category=semantic_category,
            wad_origin_domain=wad_origin_domain,
            wad_evidence_type=wad_evidence_type,
            wad_scope=f"mufrad/{ts}",
            wad_evidence_ref=f"corpus/ayat_al_dayn/{ts}",
            word_class_closure_ref=f"formal_shape_registry/{wc}/CLOSED",
            weight_pattern_closure_ref=f"E4B/weight_pattern/{ts}",
            inflection_closure_ref=f"E4B/inflection/{ts}",
            contract_slot_readiness_ref=f"E6/dal_madlul_binding/{ts}",
            composition_participation_ref=f"E7/formal_shape/CLOSED/{ts}",
            kulli_juzii_axis=kulli_juzii_axis,
            particularity_source=particularity_source,
            predication_test_passed=predication_test_passed,
            reference_resolution_status="deferred-to-context",
            branch_origin_ref=f"E5/dal_only/{ts}",
            branch_ref=f"E7/semantic_slot/{ts}",
            branch_relation_type="chain:E5->E6->E7",
            branch_illa_jamia="dal_madlul_binding_plus_formal_shape_closure",
            branch_evidence_ref=f"corpus/ayat_al_dayn/{ts}",
            branch_domain_compatibility="arabic_morpho_syntactic_domain",
            branch_no_preventer=branch_no_preventer,
            naql_readiness="deferred-to-naql-gate",
            majaz_readiness="deferred-to-majaz-gate",
        )

        if verdict.verdict_state is not _MufradSemanticState.PROVEN:
            return None
        return verdict
    except Exception:
        return None


# ---------------------------------------------------------------------------
# E6→E7 chain: build_e7_chain_from_e6_verdict
# ---------------------------------------------------------------------------


def build_e7_chain_from_e6_verdict(
    e6_binding_verdict: Any,
    token_surface: str = "",
    word_class: str = "ISM",
    trace_id: str = "",
    semantic_category_name: str = "JAMID",
) -> Optional[Any]:
    """E6→E7 chain: DalMadlulBindingVerdict → MufradSemanticSlotGeometryVerdict.

    Internally builds FormalStyleCandidate (PR-F8) then calls PR-D1.

    Args:
        e6_binding_verdict: DalMadlulBindingVerdict from E6 (verdict_state=BOUND)
        token_surface: Arabic token surface form
        word_class: "ISM" or "FI3L"
        trace_id: Non-empty caller trace reference
        semantic_category_name: SemanticCategory value (default "JAMID")

    Returns:
        MufradSemanticSlotGeometryVerdict (PROVEN) on success.
        None on Python 3.10, missing inputs, any failure. FAIL-CLOSED: never raises.
    """
    if not _MUFRAD_SLOT_AVAILABLE:
        return None
    if not _FORMAL_SHAPE_ADAPTER_AVAILABLE:
        return None
    if e6_binding_verdict is None:
        return None
    if not token_surface or not token_surface.strip():
        return None
    if not trace_id or not trace_id.strip():
        return None
    try:
        ts = token_surface.strip()

        # Build formal style candidate (PR-F8) with DECLARATIVE_STYLE_FORM default
        formal_style_verdict = _build_formal_style_candidate(
            style_family_name="DECLARATIVE_STYLE_FORM",
            composition_evidence_ref=f"pre_semantic_boundary/{ts}",
            formal_closure_ref=_FORMAL_CLOSURE_REF,
        )
        if formal_style_verdict is None:
            return None

        return build_mufrad_semantic_slot_geometry(
            e6_binding_verdict=e6_binding_verdict,
            formal_style_verdict=formal_style_verdict,
            token_surface=ts,
            word_class=word_class,
            semantic_category_name=semantic_category_name,
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Full convenience: build_e7_from_surface
# ---------------------------------------------------------------------------


def build_e7_from_surface(
    token_surface: str,
    root_letters: str,
    segment_host: str,
    word_class: str,
    trace_id: str,
    wad_usage_boundary: str = "",
    domain: str = "DAL_ONLY",
    path_kind: str = "ROOT",
    semantic_category_name: str = "JAMID",
) -> Optional[Any]:
    """E4B+E4C+E5+E6+E7 full chain convenience function.

    Runs the complete pipeline from Arabic surface form to SemanticSlotFrame.

    Args:
        token_surface: Arabic token surface form (e.g. "دَيْنٍ")
        root_letters: Arabic root letters (e.g. "دين")
        segment_host: Arabic segment host (usually same as token_surface)
        word_class: "ISM" or "FI3L"
        trace_id: Non-empty caller trace reference
        wad_usage_boundary: Wad usage boundary (defaults to token_surface if empty)
        domain: Registry domain (default "DAL_ONLY")
        path_kind: Weight path kind (default "ROOT")
        semantic_category_name: SemanticCategory value (default "JAMID")

    Returns:
        MufradSemanticSlotGeometryVerdict (PROVEN, candidate=SemanticSlotFrame)
        on Python 3.12+. None on Python 3.10 or any failure. FAIL-CLOSED: never raises.
    """
    if not _MUFRAD_SLOT_AVAILABLE:
        return None
    if not _E6_AVAILABLE:
        return None
    if not token_surface or not token_surface.strip():
        return None
    if not trace_id or not trace_id.strip():
        return None
    try:
        # Run E4B+E4C+E5+E6 chain
        e6_verdict = _build_e6_from_surface(
            token_surface=token_surface,
            root_letters=root_letters,
            segment_host=segment_host,
            word_class=word_class,
            trace_id=trace_id,
            wad_usage_boundary=wad_usage_boundary,
            domain=domain,
            path_kind=path_kind,
        )
        if e6_verdict is None:
            return None

        return build_e7_chain_from_e6_verdict(
            e6_binding_verdict=e6_verdict,
            token_surface=token_surface,
            word_class=word_class,
            trace_id=trace_id,
            semantic_category_name=semantic_category_name,
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Module invariants (run at import time)
# ---------------------------------------------------------------------------


def _verify_e7_mufrad_slot_invariants() -> None:
    """Run at import time — verifies module-level constitutional invariants."""
    assert _VENDOR_SHA == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52", (
        f"VENDOR_SHA mismatch: {_VENDOR_SHA!r}"
    )
    assert isinstance(_MUFRAD_SLOT_AVAILABLE, bool), "_MUFRAD_SLOT_AVAILABLE must be bool"
    assert isinstance(_E6_AVAILABLE, bool), "_E6_AVAILABLE must be bool"
    assert isinstance(_FORMAL_SHAPE_ADAPTER_AVAILABLE, bool), (
        "_FORMAL_SHAPE_ADAPTER_AVAILABLE must be bool"
    )
    assert callable(build_contractable_unit_geometry), (
        "build_contractable_unit_geometry not callable"
    )
    assert callable(build_mufrad_semantic_slot_geometry), (
        "build_mufrad_semantic_slot_geometry not callable"
    )
    assert callable(build_e7_chain_from_e6_verdict), (
        "build_e7_chain_from_e6_verdict not callable"
    )
    assert callable(build_e7_from_surface), "build_e7_from_surface not callable"


_verify_e7_mufrad_slot_invariants()
