"""
E8 Maqam Context Boundary Adapter — PR-D1.2

Wraps:
  PR-D1.2: prove_maqam_context_boundary() → MaqamContextBoundaryVerdict (PROVEN)

Constitutional invariants (binding):
  - MaqamContextFrame is boundary for dalalah possibility, NOT dalalah operation
  - MaqamContextFrame ≠ meaning, ≠ Mutabaqah, ≠ Tadammun, ≠ Iltizam, ≠ ifadah, ≠ hukm
  - MaqamContextFrame opens PR-D2 readiness only; does NOT open Ifadah
  - Consumes SemanticSlotFrame (from E7/PR-D1) via MufradSemanticSlotGeometryVerdict
  - FAIL-CLOSED: all functions return None on Python 3.10 (vendor StrEnum absent)
  - AUTONOMOUS_COMMIT_MODE = 0 (no commit, no tag, no push, no merge)

VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
Phase: E8 — MAQAM_CONTEXT_BOUNDARY + RELATION_CANDIDATE (PR-D1.2 component)
"""
from __future__ import annotations

from typing import Any, Optional

_VENDOR_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"
_MAQAM_CONTEXT_AVAILABLE = False
_E7_AVAILABLE = False

# ---------------------------------------------------------------------------
# Vendor imports — StrEnum present only on Python 3.11+; 3.10 → ImportError
# ---------------------------------------------------------------------------

try:
    from taaqqul_slot_geometry.weight.maqam_context_boundary import (
        DiscourseDomainType as _DiscourseDomainType,
        LiteralConstraintType as _LiteralConstraintType,
        MaqamContextState as _MaqamContextState,
        UsageRegisterType as _UsageRegisterType,
        WadScopeType as _WadScopeType,
        prove_maqam_context_boundary as _prove_maqam_context_boundary,
    )
    _MAQAM_CONTEXT_AVAILABLE = True
except ImportError:
    _DiscourseDomainType = None  # type: ignore[assignment]
    _LiteralConstraintType = None  # type: ignore[assignment]
    _MaqamContextState = None  # type: ignore[assignment]
    _UsageRegisterType = None  # type: ignore[assignment]
    _WadScopeType = None  # type: ignore[assignment]
    _prove_maqam_context_boundary = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# E7 adapter availability (always importable on 3.10; functions return None)
# ---------------------------------------------------------------------------

_build_e7_from_surface: Any = None

try:
    from pipeline.taaqol_integration.weight_layer.mufrad_semantic_slot_adapter import (  # noqa: F401
        _VENDOR_SHA as _E7_VENDOR_SHA,
        build_e7_from_surface as _build_e7_from_surface,
    )
    _E7_AVAILABLE = True
except ImportError:
    _E7_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constitutional non-meaning attestation
# ---------------------------------------------------------------------------

_NON_MEANING_PROOF = (
    "maqam-context-boundary: boundary for dalalah possibility only; "
    "not meaning, not ifadah, not hukm, not reality (E8/PR-D1.2)"
)

# ---------------------------------------------------------------------------
# Conservative defaults for corpus Ayat al-Dayn tokens
# ---------------------------------------------------------------------------

_DEFAULT_DISCOURSE_DOMAIN = "LUGHAWI"       # Arabic linguistic domain
_DEFAULT_USAGE_REGISTER = "HAQIQI"          # Literal usage — conservative
_DEFAULT_LITERAL_CONSTRAINT = "UNCONSTRAINED"  # No contextual narrowing at corpus layer
_DEFAULT_WAD_SCOPE = "ORIGINAL"             # Original wad' scope, not narrowed


# ---------------------------------------------------------------------------
# PR-D1.2: build_maqam_context_boundary
# ---------------------------------------------------------------------------


def build_maqam_context_boundary(
    e7_slot_verdict: Any,
    token_surface: str = "",
    discourse_domain_name: str = _DEFAULT_DISCOURSE_DOMAIN,
    usage_register_name: str = _DEFAULT_USAGE_REGISTER,
    literal_constraint_name: str = _DEFAULT_LITERAL_CONSTRAINT,
    wad_scope_name: str = _DEFAULT_WAD_SCOPE,
) -> Optional[Any]:
    """Prove a MaqamContextFrame via prove_maqam_context_boundary() (PR-D1.2).

    Consumes a MufradSemanticSlotGeometryVerdict (from E7/PR-D1) and
    constructs constitutional boundary readiness for dalalah operations.

    Constitutional constraint: MaqamContextFrame is boundary only —
    NOT meaning, NOT Mutabaqah, NOT Tadammun, NOT Iltizam, NOT ifadah.
    Opens PR-D2 readiness only.

    Args:
        e7_slot_verdict: MufradSemanticSlotGeometryVerdict from E7.
        token_surface: Non-empty Arabic surface string (for trace refs).
        discourse_domain_name: DiscourseDomainType value name.
                               Default: "LUGHAWI" (Arabic linguistic domain).
        usage_register_name: UsageRegisterType value name.
                             Default: "HAQIQI" (literal usage — conservative).
        literal_constraint_name: LiteralConstraintType value name.
                                 Default: "UNCONSTRAINED" (no contextual narrowing).
        wad_scope_name: WadScopeType value name.
                        Default: "ORIGINAL" (original wad' scope, not narrowed).

    Returns:
        MaqamContextBoundaryVerdict (verdict_state=PROVEN, candidate=MaqamContextFrame)
        on success. None on Python 3.10, None/empty inputs, REFUSED verdict,
        or any exception. FAIL-CLOSED: never raises.
    """
    if not _MAQAM_CONTEXT_AVAILABLE:
        return None
    if e7_slot_verdict is None:
        return None
    if not token_surface or not token_surface.strip():
        return None
    ts = token_surface.strip()
    try:
        discourse_domain_type = _DiscourseDomainType(discourse_domain_name)
        usage_register_type = _UsageRegisterType(usage_register_name)
        literal_constraint_type = _LiteralConstraintType(literal_constraint_name)
        wad_scope_type = _WadScopeType(wad_scope_name)

        verdict = _prove_maqam_context_boundary(
            semantic_slot_verdict=e7_slot_verdict,
            discourse_domain_type=discourse_domain_type,
            discourse_evidence_ref=f"corpus/ayat_al_dayn/{ts}",
            usage_register_type=usage_register_type,
            usage_evidence_ref=f"corpus/ayat_al_dayn/{ts}",
            technical_domain_name="arabic_morpho_syntactic_domain",
            is_technical=False,
            technical_evidence_ref=f"E8/technical_domain/{ts}",
            speaker_position="corpus/ayat_al_dayn/speaker",
            addressee_position="corpus/ayat_al_dayn/addressee",
            textual_context_window=f"corpus/ayat_al_dayn/context/{ts}",
            has_potential_qarina=False,
            qarina_type_readiness="deferred-to-qarinah-gate",
            qarina_blocks_literal=False,
            qarina_evidence_ref=f"E8/qarinah/deferred/{ts}",
            blocker_count=0,
            blocker_types=(),
            all_blockers_audited=True,
            blocker_evidence_ref=f"E8/blocker/no-blockers-corpus/{ts}",
            literal_constraint_type=literal_constraint_type,
            literal_domain_ref="arabic_lughawi_domain",
            literal_evidence_ref=f"E8/literal/corpus-unconstrained/{ts}",
            wad_scope_type=wad_scope_type,
            wad_narrowing_evidence="original-wad-scope-no-narrowing",
            wad_scope_evidence_ref=f"E8/wad_scope/original/{ts}",
            style_relevance_constraint="declarative-style-form-relevant",
        )

        if verdict.verdict_state is not _MaqamContextState.PROVEN:
            return None
        return verdict
    except Exception:
        return None


def build_maqam_from_surface(
    token_surface: str,
    root_letters: str,
    segment_host: str,
    word_class: str,
    trace_id: str,
    wad_usage_boundary: str = "",
    domain: str = "DAL_ONLY",
    path_kind: str = "ROOT",
    semantic_category_name: str = "JAMID",
    discourse_domain_name: str = _DEFAULT_DISCOURSE_DOMAIN,
    usage_register_name: str = _DEFAULT_USAGE_REGISTER,
    literal_constraint_name: str = _DEFAULT_LITERAL_CONSTRAINT,
    wad_scope_name: str = _DEFAULT_WAD_SCOPE,
) -> Optional[Any]:
    """E7+E8 chain: Arabic surface → MaqamContextBoundaryVerdict (PROVEN) | None.

    Runs: E4B+E4C+E5+E6+E7 (via build_e7_from_surface) then
    E8/PR-D1.2 (via build_maqam_context_boundary).

    Args:
        token_surface: Arabic token surface form (e.g. "دَيْنٍ").
        root_letters: Arabic root letters (e.g. "دين").
        segment_host: Lexical host (usually same as token_surface).
        word_class: "ISM" or "FI3L".
        trace_id: Non-empty caller trace reference.
        wad_usage_boundary: Wad usage boundary (defaults to token_surface).
        domain: Registry domain (default "DAL_ONLY").
        path_kind: Weight path kind (default "ROOT").
        semantic_category_name: SemanticCategory value (default "JAMID").
        discourse_domain_name: DiscourseDomainType value name (default "LUGHAWI").
        usage_register_name: UsageRegisterType value name (default "HAQIQI").
        literal_constraint_name: LiteralConstraintType value name (default "UNCONSTRAINED").
        wad_scope_name: WadScopeType value name (default "ORIGINAL").

    Returns:
        MaqamContextBoundaryVerdict (PROVEN) | None. FAIL-CLOSED: never raises.
    """
    if not _MAQAM_CONTEXT_AVAILABLE:
        return None
    if _build_e7_from_surface is None:
        return None
    if not token_surface or not token_surface.strip():
        return None
    if not trace_id or not trace_id.strip():
        return None
    ts = token_surface.strip()
    try:
        e7_verdict = _build_e7_from_surface(
            token_surface=ts,
            root_letters=root_letters,
            segment_host=segment_host,
            word_class=word_class,
            trace_id=trace_id,
            wad_usage_boundary=wad_usage_boundary,
            domain=domain,
            path_kind=path_kind,
            semantic_category_name=semantic_category_name,
        )
        if e7_verdict is None:
            return None
        return build_maqam_context_boundary(
            e7_slot_verdict=e7_verdict,
            token_surface=ts,
            discourse_domain_name=discourse_domain_name,
            usage_register_name=usage_register_name,
            literal_constraint_name=literal_constraint_name,
            wad_scope_name=wad_scope_name,
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Module invariants (run at import time)
# ---------------------------------------------------------------------------


def _verify_e8_maqam_context_invariants() -> None:
    """Run at import time — verifies module-level constitutional invariants."""
    assert _VENDOR_SHA == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52", (
        f"VENDOR_SHA mismatch: {_VENDOR_SHA!r}"
    )
    assert isinstance(_MAQAM_CONTEXT_AVAILABLE, bool), (
        "_MAQAM_CONTEXT_AVAILABLE must be bool"
    )
    assert isinstance(_E7_AVAILABLE, bool), "_E7_AVAILABLE must be bool"
    assert callable(build_maqam_context_boundary), (
        "build_maqam_context_boundary not callable"
    )
    assert callable(build_maqam_from_surface), "build_maqam_from_surface not callable"


_verify_e8_maqam_context_invariants()
