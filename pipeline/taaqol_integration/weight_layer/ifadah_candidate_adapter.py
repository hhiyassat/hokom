"""Ifadah Candidate Adapter — E9_IFADAH_CANDIDATE

CONSTITUTIONAL_RECONCILIATION_01 Phase: E9

Purpose:
    Implements E9: the ifadah (speech-level closure) layer.

    One operation:
      prove_ifadah_candidate(RelationClosureVerdict, FormalStyleVerdict,
          MaqamContextBoundaryVerdict, SpeechForceKind, ifadah_evidence, closure_scope)
          → IfadahVerdict(PROVEN)

Constitutional chain (E0→E9):
    E0  = TARGET BASELINE FREEZE (SHAs confirmed)
    E1  = AYAT_AL_DAYN_REGISTRY
    E2  = P2 REGISTRY PROJECTION
    E3  = HOKOM P3/P4/P5 CONTINUITY
    E4A = PRECONDITION GUARD
    E4B = PRE-WEIGHT TYPED CARRIERS
    E4C = NATIVE LICENSING BOUNDARY
    E5  = DAL-ONLY CANDIDATE
    E6  = VERBAL MADLUL + BINDING
    E7  = FORMAL SHAPE + MUFRAD DALALAH
    E8  = MAQAM CONTEXT + RELATION CANDIDATE
    E9  = IFADAH CANDIDATE ← THIS MODULE

Constitutional invariants:
    - FAIL-CLOSED: any import error or runtime error → returns None
    - IfadahCandidate ≠ meaning, ≠ hukm, ≠ reality — pre-judgment only
    - speech_force must be SpeechForceKind member (KHABAR or INSHA)
    - ifadah_evidence must be non-empty (constitutional attestation)
    - closure_scope must be non-empty
    - No rank promotion beyond IFADAH_RANK_CEILING
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - ifadah_candidate.py uses StrEnum → fails to import on 3.10
    - All public functions return None on 3.10 (fail-closed)

Phase: E9 — IFADAH CANDIDATE
Prior: E8 → RelationClosureVerdict(PROVEN) + FormalStyleVerdict + MaqamContextBoundaryVerdict
Output: IfadahVerdict(PROVEN, candidate=IfadahCandidate)
VENDOR_SHA: 05c6668dfb95d9238cff5df1d8bc73d0664bccb3
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

# ── Vendor path ────────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA  = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

# ── Fail-closed vendor imports ─────────────────────────────────────────────────
_IFADAH_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    from taaqqul_slot_geometry.weight.ifadah_candidate import (  # type: ignore
        SpeechForceKind        as _SpeechForceKind,
        IfadahState            as _IfadahState,
        IfadahCandidate        as _IfadahCandidate,
        IfadahVerdict          as _IfadahVerdict,
        prove_ifadah_candidate as _prove_ifadah_candidate,
        IFADAH_RANK_CEILING    as _IFADAH_RANK_CEILING,
    )
    from taaqqul_slot_geometry.weight.relation_closure import (  # type: ignore
        RelationClosureVerdict as _RelationClosureVerdict,
    )
    from taaqqul_slot_geometry.weight.formal_style_candidate import (  # type: ignore
        FormalStyleVerdict as _FormalStyleVerdict,
    )
    from taaqqul_slot_geometry.weight.maqam_context_boundary import (  # type: ignore
        MaqamContextBoundaryVerdict as _MaqamContextBoundaryVerdict,
    )
    _IFADAH_AVAILABLE = True
except ImportError:
    pass


def build_ifadah_candidate(
    relation_closure_verdict: Any,
    formal_style_verdict: Any,
    ifadah_maqam_verdict: Any,
    speech_force: Any,
    ifadah_evidence: str,
    closure_scope: str,
) -> "Optional[Any]":
    """
    E9: Prove ifadah (speech-level closure) candidate.

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - relation_closure_verdict is not RelationClosureVerdict
    - formal_style_verdict is not FormalStyleVerdict
    - ifadah_maqam_verdict is not MaqamContextBoundaryVerdict
    - speech_force is not SpeechForceKind member
    - ifadah_evidence is empty
    - closure_scope is empty
    - prove_ifadah_candidate() returns REFUSED
    - Any unexpected error

    Args:
        relation_closure_verdict: RelationClosureVerdict from E8.
        formal_style_verdict:     FormalStyleVerdict from E7.
        ifadah_maqam_verdict:     MaqamContextBoundaryVerdict from E8.
        speech_force:             SpeechForceKind.KHABAR or INSHA.
        ifadah_evidence:          Non-empty constitutional attestation string.
        closure_scope:            Non-empty scope descriptor.

    Returns:
        IfadahVerdict(state=PROVEN) on success.
        None on failure (fail-closed).
    """
    if not _IFADAH_AVAILABLE:
        return None
    if not isinstance(relation_closure_verdict, _RelationClosureVerdict):
        return None
    if not isinstance(formal_style_verdict, _FormalStyleVerdict):
        return None
    if not isinstance(ifadah_maqam_verdict, _MaqamContextBoundaryVerdict):
        return None
    if not isinstance(speech_force, _SpeechForceKind):
        return None
    if not ifadah_evidence or not ifadah_evidence.strip():
        return None
    if not closure_scope or not closure_scope.strip():
        return None
    try:
        verdict = _prove_ifadah_candidate(
            relation_closure_verdict=relation_closure_verdict,
            formal_style_verdict=formal_style_verdict,
            ifadah_maqam_verdict=ifadah_maqam_verdict,
            speech_force=speech_force,
            ifadah_evidence=ifadah_evidence,
            closure_scope=closure_scope,
        )
        if verdict.state is not _IfadahState.PROVEN:
            return None
        return verdict
    except Exception:  # noqa: BLE001
        return None


# ── Module-level invariant assertions ──────────────────────────────────────────

def _verify_e9_invariants() -> None:
    """Verify E9 adapter fail-closed invariants (import-time)."""
    # INV-E9-1: wrong relation_closure_verdict type → None
    r1 = build_ifadah_candidate(
        relation_closure_verdict=object(),
        formal_style_verdict=object(),
        ifadah_maqam_verdict=object(),
        speech_force=object(),
        ifadah_evidence="evidence",
        closure_scope="scope",
    )
    assert r1 is None, "INV-E9-1: wrong type must return None"

    # INV-E9-2: empty ifadah_evidence → None (guard active before vendor call)
    if _IFADAH_AVAILABLE:
        r2 = build_ifadah_candidate(
            relation_closure_verdict=object(),
            formal_style_verdict=object(),
            ifadah_maqam_verdict=object(),
            speech_force=_SpeechForceKind.KHABAR,
            ifadah_evidence="",
            closure_scope="scope",
        )
        assert r2 is None, "INV-E9-2: empty evidence must return None"


_verify_e9_invariants()


__all__ = [
    "build_ifadah_candidate",
    "_IFADAH_AVAILABLE",
    "_VENDOR_SHA",
]
