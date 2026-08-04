"""Mantuq Closure Adapter — E13_MANTUQ_CLOSURE

CONSTITUTIONAL_RECONCILIATION_01 Phase: E13

Purpose:
    Implements E13: the mantuq (preserved spoken/textual origin) closure layer.

    One operation:
      prove_mantuq_closure(IfadahVerdict, MaqamContextBoundaryVerdict,
          mantuq_scope, spoken_surface_ref, mantuq_evidence, closure_scope)
          → MantuqClosureVerdict(PROVEN)

Constitutional chain (E0→E13):
    ...
    E12 = TANZIL CANDIDATE (TanzilVerdict.PROVEN, weight-layer terminal;
                             audit-layer continues via bridge_tanzil_to_audit
                             — see Wave06 typed_stage_builders.py)
    E13 = MANTUQ CLOSURE ← THIS MODULE

    NOTE: MantuqClosure branches from IfadahVerdict (E9), not TanzilVerdict.
    Both E12 and E13 receive their inputs from the E9/E10 chain — they are
    parallel closure paths, not sequential.

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None
    - MantuqClosure preserves spoken/textual origin — no semantic extension
    - spoken_surface_ref must be non-empty (constitutional anchor)
    - mantuq_evidence must be non-empty (constitutional attestation)
    - closure_scope must be non-empty
    - No rank promotion beyond MANTUQ_RANK_CEILING
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - mantuq_closure.py uses StrEnum → fails to import on 3.10
    - All public functions return None on 3.10 (fail-closed)

Phase: E13 — MANTUQ CLOSURE
Prior: E9 → IfadahVerdict(PROVEN) + E8 → MaqamContextBoundaryVerdict
Output: MantuqClosureVerdict(PROVEN, candidate=MantuqClosureCandidate)
VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

# ── Vendor path ────────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA  = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

# ── Fail-closed vendor imports ─────────────────────────────────────────────────
_MANTUQ_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    from taaqqul_slot_geometry.weight.mantuq_closure import (  # type: ignore
        MantuqClosureState    as _MantuqClosureState,
        MantuqClosureCandidate as _MantuqClosureCandidate,
        MantuqClosureVerdict  as _MantuqClosureVerdict,
        prove_mantuq_closure  as _prove_mantuq_closure,
        MANTUQ_RANK_CEILING   as _MANTUQ_RANK_CEILING,
    )
    from taaqqul_slot_geometry.weight.ifadah_candidate import (  # type: ignore
        IfadahVerdict as _IfadahVerdict,
    )
    from taaqqul_slot_geometry.weight.maqam_context_boundary import (  # type: ignore
        MaqamContextBoundaryVerdict as _MaqamContextBoundaryVerdict,
    )
    _MANTUQ_AVAILABLE = True
except ImportError:
    pass


def build_mantuq_closure(
    ifadah_verdict: Any,
    maqam_verdict: Any,
    mantuq_scope: str,
    spoken_surface_ref: str,
    mantuq_evidence: str,
    closure_scope: str,
) -> "Optional[Any]":
    """
    E13: Prove mantuq closure (preserved spoken/textual origin).

    Takes IfadahVerdict (E9) and MaqamContextBoundaryVerdict (E8) as inputs —
    NOT TanzilVerdict. MantuqClosure is a parallel branch from Ifadah, not
    sequential to Tanzil.

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - ifadah_verdict is not IfadahVerdict
    - maqam_verdict is not MaqamContextBoundaryVerdict
    - spoken_surface_ref is empty
    - mantuq_evidence is empty
    - mantuq_scope or closure_scope is empty
    - prove_mantuq_closure() returns REFUSED
    - Any unexpected error

    Args:
        ifadah_verdict:     IfadahVerdict from E9.
        maqam_verdict:      MaqamContextBoundaryVerdict from E8.
        mantuq_scope:       Non-empty mantuq scope descriptor.
        spoken_surface_ref: Non-empty reference to spoken/textual surface anchor.
        mantuq_evidence:    Non-empty constitutional attestation string.
        closure_scope:      Non-empty closure scope descriptor.

    Returns:
        MantuqClosureVerdict(state=PROVEN) on success.
        None on failure (fail-closed).
    """
    if not _MANTUQ_AVAILABLE:
        return None
    if not isinstance(ifadah_verdict, _IfadahVerdict):
        return None
    if not isinstance(maqam_verdict, _MaqamContextBoundaryVerdict):
        return None
    if not spoken_surface_ref or not spoken_surface_ref.strip():
        return None
    if not mantuq_evidence or not mantuq_evidence.strip():
        return None
    if not mantuq_scope or not mantuq_scope.strip():
        return None
    if not closure_scope or not closure_scope.strip():
        return None
    try:
        verdict = _prove_mantuq_closure(
            ifadah_verdict=ifadah_verdict,
            maqam_verdict=maqam_verdict,
            mantuq_scope=mantuq_scope,
            spoken_surface_ref=spoken_surface_ref,
            mantuq_evidence=mantuq_evidence,
            closure_scope=closure_scope,
        )
        # Vendor uses `verdict_state`, not `.state`.
        if verdict.verdict_state is not _MantuqClosureState.PROVEN:
            return None
        return verdict
    except Exception:  # noqa: BLE001
        return None


# ── Module-level invariant assertions ──────────────────────────────────────────

def _verify_e13_invariants() -> None:
    r1 = build_mantuq_closure(
        ifadah_verdict=object(),
        maqam_verdict=object(),
        mantuq_scope="scope",
        spoken_surface_ref="surface",
        mantuq_evidence="evidence",
        closure_scope="closure",
    )
    assert r1 is None, "INV-E13-1: wrong type must return None"

    if _MANTUQ_AVAILABLE:
        r2 = build_mantuq_closure(
            ifadah_verdict=object(),
            maqam_verdict=object(),
            mantuq_scope="scope",
            spoken_surface_ref="",
            mantuq_evidence="evidence",
            closure_scope="closure",
        )
        assert r2 is None, "INV-E13-2: empty spoken_surface_ref must return None"


_verify_e13_invariants()


__all__ = [
    "build_mantuq_closure",
    "_MANTUQ_AVAILABLE",
    "_VENDOR_SHA",
]
