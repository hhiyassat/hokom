"""
E7 Formal Shape Adapter — PR-F2 + PR-F8

Wraps:
  PR-F2: build_word_class_registry() → FormalShapeRegistry (closure_state=CLOSED)
  PR-F8: prove_formal_style_candidate() → FormalStyleVerdict (PROVEN)

Constitutional invariants (binding):
  - FormalShapeRegistry.closure_state IS FormalShapeClosureState.CLOSED (required for PR-D1)
  - FormalStyleCandidate is formal structural classification ONLY
  - FormalStyleCandidate ≠ meaning, ≠ ifadah, ≠ hukm, ≠ dalalah operation
  - FormalStyleCandidate opens PR-D1 readiness only; does not open Ifadah
  - FAIL-CLOSED: all functions return None on Python 3.10 (vendor StrEnum absent)
  - AUTONOMOUS_COMMIT_MODE = 0 (no commit, no tag, no push, no merge)

VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
Phase: E7 — FORMAL SHAPE + MUFRAD DALALAH (PR-F2 / PR-F8 component)
"""
from __future__ import annotations

from typing import Any, Optional

_VENDOR_SHA = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
_FORMAL_SHAPE_AVAILABLE = False
_E6_AVAILABLE = False

# ---------------------------------------------------------------------------
# Vendor imports — StrEnum present only on Python 3.11+; 3.10 → ImportError
# ---------------------------------------------------------------------------

try:
    from taaqqul_slot_geometry.weight.formal_shape import (
        FormalShapeClosureState as _FormalShapeClosureState,
        build_word_class_registry as _build_word_class_registry,
    )
    from taaqqul_slot_geometry.weight.formal_style_candidate import (
        FormalStyleFamily as _FormalStyleFamily,
        FormalStyleState as _FormalStyleState,
        prove_formal_style_candidate as _prove_formal_style_candidate,
    )
    _FORMAL_SHAPE_AVAILABLE = True
except ImportError:
    _build_word_class_registry = None  # type: ignore[assignment]
    _FormalShapeClosureState = None  # type: ignore[assignment]
    _prove_formal_style_candidate = None  # type: ignore[assignment]
    _FormalStyleFamily = None  # type: ignore[assignment]
    _FormalStyleState = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# E6 adapter availability check (importable on 3.10, returns None at runtime)
# ---------------------------------------------------------------------------

try:
    from pipeline.taaqol_integration.weight_layer.verbal_madlul_adapter import (  # noqa: F401
        _VENDOR_SHA as _E6_VENDOR_SHA,
    )
    _E6_AVAILABLE = True
except ImportError:
    _E6_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constitutional non-meaning attestation
# ---------------------------------------------------------------------------

_NON_MEANING_PROOF = (
    "pre-semantic-admissibility: formal shape / formal style boundary proof only; "
    "not meaning, not ifadah, not hukm, not reality (E7/PR-F2/PR-F8)"
)

# ---------------------------------------------------------------------------
# Registry singleton — built once, cached
# ---------------------------------------------------------------------------

_REGISTRY_SINGLETON: Any = None


def get_formal_shape_registry() -> Optional[Any]:
    """Return the canonical FormalShapeRegistry (closure_state=CLOSED).

    The registry is built from canonical ISM/FI3L/HARF definitions with all
    required subfamilies — closure_state will be CLOSED after build.

    Returns:
        FormalShapeRegistry on success (Python 3.12+).
        None on Python 3.10 (vendor absent) or any error. FAIL-CLOSED: never raises.
    """
    global _REGISTRY_SINGLETON  # noqa: PLW0603
    if not _FORMAL_SHAPE_AVAILABLE:
        return None
    try:
        if _REGISTRY_SINGLETON is None:
            _REGISTRY_SINGLETON = _build_word_class_registry()
        return _REGISTRY_SINGLETON
    except Exception:
        return None


def get_formal_closure_state() -> Optional[Any]:
    """Return FormalShapeClosureState.CLOSED.

    Returns:
        FormalShapeClosureState.CLOSED on Python 3.12+.
        None on Python 3.10 or any error. FAIL-CLOSED: never raises.
    """
    if not _FORMAL_SHAPE_AVAILABLE:
        return None
    try:
        return _FormalShapeClosureState.CLOSED
    except Exception:
        return None


# ---------------------------------------------------------------------------
# PR-F8: build_formal_style_candidate
# ---------------------------------------------------------------------------


def build_formal_style_candidate(
    style_family_name: str = "DECLARATIVE_STYLE_FORM",
    composition_evidence_ref: str = "",
    formal_closure_ref: str = "",
) -> Optional[Any]:
    """Prove a FormalStyleCandidate via prove_formal_style_candidate() (PR-F8).

    Constitutional constraint: prove_formal_style_candidate() requires
    FormalShapeClosureState.CLOSED — this is always passed internally.

    Args:
        style_family_name: FormalStyleFamily enum value name.
                           Default: "DECLARATIVE_STYLE_FORM".
        composition_evidence_ref: Non-empty reference to composition evidence.
        formal_closure_ref: Non-empty reference to the formal shape closure proof.
                            This becomes FormalStyleCandidate.formal_closure_ref
                            and SemanticSlotFrame.formal_shape_ref downstream.

    Returns:
        FormalStyleVerdict (verdict_state=PROVEN, candidate=FormalStyleCandidate)
        on success. None on Python 3.10, empty inputs, REFUSED verdict, or any
        exception. FAIL-CLOSED: never raises.
    """
    if not _FORMAL_SHAPE_AVAILABLE:
        return None
    if not style_family_name or not style_family_name.strip():
        return None
    if not composition_evidence_ref or not composition_evidence_ref.strip():
        return None
    if not formal_closure_ref or not formal_closure_ref.strip():
        return None
    try:
        style_family = _FormalStyleFamily(style_family_name)
        closure_state = _FormalShapeClosureState.CLOSED
        verdict = _prove_formal_style_candidate(
            style_family=style_family,
            composition_evidence_ref=composition_evidence_ref,
            formal_closure_state=closure_state,
            formal_closure_ref=formal_closure_ref,
        )
        if verdict.verdict_state is not _FormalStyleState.PROVEN:
            return None
        return verdict
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Module invariants (run at import time)
# ---------------------------------------------------------------------------


def _verify_e7_formal_shape_invariants() -> None:
    """Run at import time — verifies module-level constitutional invariants."""
    assert _VENDOR_SHA == "05c6668dfb95d9238cff5df1d8bc73d0664bccb3", (
        f"VENDOR_SHA mismatch: {_VENDOR_SHA!r}"
    )
    assert isinstance(_FORMAL_SHAPE_AVAILABLE, bool), (
        "_FORMAL_SHAPE_AVAILABLE must be bool"
    )
    assert isinstance(_E6_AVAILABLE, bool), "_E6_AVAILABLE must be bool"
    assert callable(get_formal_shape_registry), "get_formal_shape_registry not callable"
    assert callable(get_formal_closure_state), "get_formal_closure_state not callable"
    assert callable(build_formal_style_candidate), (
        "build_formal_style_candidate not callable"
    )


_verify_e7_formal_shape_invariants()
