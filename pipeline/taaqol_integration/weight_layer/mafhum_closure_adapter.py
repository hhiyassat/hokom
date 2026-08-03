"""Mafhum Closure Adapter — E14_MAFHUM_CLOSURE

CONSTITUTIONAL_RECONCILIATION_01 Phase: E14

Purpose:
    Implements E14: the mafhum (implied/understood meaning closure) layer.

    One operation:
      prove_mafhum_closure(MantuqClosureVerdict, outside_boundary,
          branch_type, branch_subtype, qayd, source_domain,
          cross_domain_transfer, mantuq_blocks, residuals)
          → MafhumClosureVerdict(PROVEN)

Constitutional chain (E0→E14):
    ...
    E13 = MANTUQ CLOSURE (MantuqClosureVerdict.PROVEN)
    E14 = MAFHUM CLOSURE ← THIS MODULE

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None
    - MafhumClosure = implied meaning from mantuq (NOT free semantic inference)
    - branch_type must be MafhumBranchType (MUWAFAQAH or MUKHALAFAH)
    - outside_boundary must be non-empty (constitutional anchor)
    - For ayat_al_dayn: mantuq_blocks=True is the conservative safe default
    - No rank promotion beyond MAFHUM_RANK_CEILING
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - mafhum_closure.py uses StrEnum → fails to import on 3.10
    - All public functions return None on 3.10 (fail-closed)

Phase: E14 — MAFHUM CLOSURE
Prior: E13 → MantuqClosureVerdict(PROVEN, candidate=MantuqClosureCandidate)
Output: MafhumClosureVerdict(PROVEN, candidate=MafhumClosureCandidate)
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
_MAFHUM_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    from taaqqul_slot_geometry.weight.mafhum_closure import (  # type: ignore
        MafhumBranchType        as _MafhumBranchType,
        MafhumClosureState      as _MafhumClosureState,
        MafhumClosureCandidate  as _MafhumClosureCandidate,
        MafhumClosureVerdict    as _MafhumClosureVerdict,
        prove_mafhum_closure    as _prove_mafhum_closure,
        MAFHUM_RANK_CEILING     as _MAFHUM_RANK_CEILING,
    )
    from taaqqul_slot_geometry.weight.mantuq_closure import (  # type: ignore
        MantuqClosureVerdict as _MantuqClosureVerdict,
    )
    _MAFHUM_AVAILABLE = True
except ImportError:
    pass


def build_mafhum_closure(
    mantuq_verdict: Any,
    outside_boundary: str,
    branch_type: Any,
    branch_subtype: str,
    qayd: str,
    source_domain: str,
    cross_domain_transfer: str,
    mantuq_blocks: bool = True,
    residuals: tuple = (),
) -> "Optional[Any]":
    """
    E14: Prove mafhum closure (implied meaning from mantuq).

    MafhumClosure derives implied meaning solely from mantuq — NOT free inference.
    For ayat_al_dayn, mantuq_blocks=True is the constitutional safe default:
    the mantuq blocks promotion of mafhum beyond its boundary.

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - mantuq_verdict is not MantuqClosureVerdict
    - branch_type is not MafhumBranchType member
    - outside_boundary is empty
    - prove_mafhum_closure() returns REFUSED
    - Any unexpected error

    Args:
        mantuq_verdict:       MantuqClosureVerdict from E13.
        outside_boundary:     Non-empty boundary description for mafhum.
        branch_type:          MafhumBranchType.MUWAFAQAH or MUKHALAFAH.
        branch_subtype:       Branch subtype descriptor (may be empty).
        qayd:                 Qayd (condition/restriction) descriptor.
        source_domain:        Source domain for mafhum derivation.
        cross_domain_transfer: Cross-domain transfer description (may be empty).
        mantuq_blocks:        Whether mantuq blocks mafhum extension (default True).
        residuals:            Tuple of Residual objects (may be empty tuple).

    Returns:
        MafhumClosureVerdict(state=PROVEN) on success.
        None on failure (fail-closed).
    """
    if not _MAFHUM_AVAILABLE:
        return None
    if not isinstance(mantuq_verdict, _MantuqClosureVerdict):
        return None
    if not isinstance(branch_type, _MafhumBranchType):
        return None
    if not outside_boundary or not outside_boundary.strip():
        return None
    try:
        verdict = _prove_mafhum_closure(
            mantuq_verdict=mantuq_verdict,
            outside_boundary=outside_boundary,
            branch_type=branch_type,
            branch_subtype=branch_subtype,
            qayd=qayd,
            source_domain=source_domain,
            cross_domain_transfer=cross_domain_transfer,
            mantuq_blocks=mantuq_blocks,
            residuals=tuple(residuals),
        )
        if verdict.state is not _MafhumClosureState.PROVEN:
            return None
        return verdict
    except Exception:  # noqa: BLE001
        return None


# ── Module-level invariant assertions ──────────────────────────────────────────

def _verify_e14_invariants() -> None:
    r1 = build_mafhum_closure(
        mantuq_verdict=object(),
        outside_boundary="boundary",
        branch_type=object(),
        branch_subtype="",
        qayd="",
        source_domain="",
        cross_domain_transfer="",
    )
    assert r1 is None, "INV-E14-1: wrong type must return None"

    if _MAFHUM_AVAILABLE:
        r2 = build_mafhum_closure(
            mantuq_verdict=object(),
            outside_boundary="",
            branch_type=_MafhumBranchType.MUWAFAQAH,
            branch_subtype="",
            qayd="",
            source_domain="",
            cross_domain_transfer="",
        )
        assert r2 is None, "INV-E14-2: empty outside_boundary must return None"


_verify_e14_invariants()


__all__ = [
    "build_mafhum_closure",
    "_MAFHUM_AVAILABLE",
    "_VENDOR_SHA",
]
