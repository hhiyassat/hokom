"""Manat Candidate Adapter — E11_MANAT_CANDIDATE

CONSTITUTIONAL_RECONCILIATION_01 Phase: E11

Purpose:
    Implements E11: the manāṭ (locus-of-application) layer.

    One operation:
      prove_manat_candidate(HukmVerdict, ManatMode, manat_description,
          effective_attribute_candidate, conditions, preventers,
          manat_evidence, manat_domain, closure_scope)
          → ManatVerdict(PROVEN)

Constitutional chain (E0→E11):
    ...
    E10 = HUKM CANDIDATE (HukmVerdict.PROVEN)
    E11 = MANAT CANDIDATE ← THIS MODULE

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None
    - ManatCandidate ≠ tahqiq execution — readiness only for ayat_al_dayn scope
    - manat_mode must be ManatMode member
    - manat_description must be non-empty
    - manat_evidence must be non-empty (constitutional attestation)
    - closure_scope must be non-empty
    - TAHQIQ_OVERCLAIM guard: vendor rejects overclaim keywords in TAHQIQ_READINESS_ONLY mode
    - No rank promotion beyond MANAT_RANK_CEILING
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - manat_candidate.py uses StrEnum → fails to import on 3.10
    - All public functions return None on 3.10 (fail-closed)

Phase: E11 — MANAT CANDIDATE
Prior: E10 → HukmVerdict(PROVEN, candidate=HukmCandidate)
Output: ManatVerdict(PROVEN, candidate=ManatCandidate)
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
_MANAT_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    from taaqqul_slot_geometry.weight.manat_candidate import (  # type: ignore
        ManatMode             as _ManatMode,
        ManatState            as _ManatState,
        ManatCandidate        as _ManatCandidate,
        ManatVerdict          as _ManatVerdict,
        prove_manat_candidate as _prove_manat_candidate,
        MANAT_RANK_CEILING    as _MANAT_RANK_CEILING,
    )
    from taaqqul_slot_geometry.weight.hukm_candidate import (  # type: ignore
        HukmVerdict as _HukmVerdict,
    )
    _MANAT_AVAILABLE = True
except ImportError:
    pass


def build_manat_candidate(
    hukm_verdict: Any,
    manat_mode: Any,
    manat_description: str,
    effective_attribute_candidate: str,
    conditions: tuple,
    preventers: tuple,
    manat_evidence: str,
    manat_domain: str,
    closure_scope: str,
) -> "Optional[Any]":
    """
    E11: Prove manāṭ (locus-of-application) candidate.

    For ayat_al_dayn, use ManatMode.TAHQIQ_READINESS_ONLY — this avoids overclaim.
    TAKHRIJ_CANDIDATE and TANQIH_CANDIDATE modes require additional evidence.

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - hukm_verdict is not HukmVerdict
    - manat_mode is not ManatMode member
    - manat_description is empty
    - manat_evidence is empty
    - closure_scope is empty
    - prove_manat_candidate() returns REFUSED (incl. TAHQIQ overclaim rejection)
    - Any unexpected error

    Args:
        hukm_verdict:                  HukmVerdict from E10.
        manat_mode:                    ManatMode.TAHQIQ_READINESS_ONLY (safe default).
        manat_description:             Non-empty locus description.
        effective_attribute_candidate: Effective attribute candidate (may be empty string).
        conditions:                    Tuple of condition strings (may be empty tuple).
        preventers:                    Tuple of preventer strings (may be empty tuple).
        manat_evidence:                Non-empty constitutional attestation string.
        manat_domain:                  Domain descriptor.
        closure_scope:                 Non-empty scope descriptor.

    Returns:
        ManatVerdict(state=PROVEN) on success.
        None on failure (fail-closed).
    """
    if not _MANAT_AVAILABLE:
        return None
    if not isinstance(hukm_verdict, _HukmVerdict):
        return None
    if not isinstance(manat_mode, _ManatMode):
        return None
    if not manat_description or not manat_description.strip():
        return None
    if not manat_evidence or not manat_evidence.strip():
        return None
    if not closure_scope or not closure_scope.strip():
        return None
    try:
        verdict = _prove_manat_candidate(
            hukm_verdict=hukm_verdict,
            manat_mode=manat_mode,
            manat_description=manat_description,
            effective_attribute_candidate=effective_attribute_candidate,
            conditions=tuple(conditions),
            preventers=tuple(preventers),
            manat_evidence=manat_evidence,
            manat_domain=manat_domain,
            closure_scope=closure_scope,
        )
        # Vendor uses `verdict_state`, not `.state` — same defect fixed
        # on ifadah/hukm/mafhum/mantuq/tanzil adapters at Wave04.
        if verdict.verdict_state is not _ManatState.PROVEN:
            return None
        return verdict
    except Exception:  # noqa: BLE001
        return None


# ── Module-level invariant assertions ──────────────────────────────────────────

def _verify_e11_invariants() -> None:
    r1 = build_manat_candidate(
        hukm_verdict=object(),
        manat_mode=object(),
        manat_description="desc",
        effective_attribute_candidate="",
        conditions=(),
        preventers=(),
        manat_evidence="evidence",
        manat_domain="domain",
        closure_scope="scope",
    )
    assert r1 is None, "INV-E11-1: wrong type must return None"

    if _MANAT_AVAILABLE:
        r2 = build_manat_candidate(
            hukm_verdict=object(),
            manat_mode=_ManatMode.TAHQIQ_READINESS_ONLY,
            manat_description="",
            effective_attribute_candidate="",
            conditions=(),
            preventers=(),
            manat_evidence="evidence",
            manat_domain="domain",
            closure_scope="scope",
        )
        assert r2 is None, "INV-E11-2: empty description must return None"


_verify_e11_invariants()


__all__ = [
    "build_manat_candidate",
    "_MANAT_AVAILABLE",
    "_VENDOR_SHA",
]
