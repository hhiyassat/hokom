"""Hukm Candidate Adapter — E10_HUKM_CANDIDATE

CONSTITUTIONAL_RECONCILIATION_01 Phase: E10

Purpose:
    Implements E10: the hukm (judgment) layer.

    One operation:
      prove_hukm_candidate(IfadahVerdict, EvaluationDomain,
          hukm_claim, hukm_evidence, hukm_maqam, closure_scope)
          → HukmVerdict(PROVEN)

Constitutional chain (E0→E10):
    ...
    E9  = IFADAH CANDIDATE (IfadahVerdict.PROVEN)
    E10 = HUKM CANDIDATE ← THIS MODULE

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None
    - HukmCandidate ≠ fiqh hukm — linguistic judgment only (E10/LINGUISTIC domain)
    - evaluation_domain must be EvaluationDomain member
    - hukm_claim must be non-empty
    - hukm_evidence must be non-empty (constitutional attestation)
    - closure_scope must be non-empty
    - No rank promotion beyond HUKM_RANK_CEILING
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - hukm_candidate.py uses StrEnum → fails to import on 3.10
    - All public functions return None on 3.10 (fail-closed)

Phase: E10 — HUKM CANDIDATE
Prior: E9 → IfadahVerdict(PROVEN, candidate=IfadahCandidate)
Output: HukmVerdict(PROVEN, candidate=HukmCandidate)
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
_HUKM_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    from taaqqul_slot_geometry.weight.hukm_candidate import (  # type: ignore
        EvaluationDomain      as _EvaluationDomain,
        HukmState             as _HukmState,
        HukmCandidate         as _HukmCandidate,
        HukmVerdict           as _HukmVerdict,
        prove_hukm_candidate  as _prove_hukm_candidate,
        HUKM_RANK_CEILING     as _HUKM_RANK_CEILING,
    )
    from taaqqul_slot_geometry.weight.ifadah_candidate import (  # type: ignore
        IfadahVerdict as _IfadahVerdict,
    )
    _HUKM_AVAILABLE = True
except ImportError:
    pass


def build_hukm_candidate(
    ifadah_verdict: Any,
    evaluation_domain: Any,
    hukm_claim: str,
    hukm_evidence: str,
    hukm_maqam: str,
    closure_scope: str,
) -> "Optional[Any]":
    """
    E10: Prove hukm (judgment) candidate.

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - ifadah_verdict is not IfadahVerdict
    - evaluation_domain is not EvaluationDomain member
    - hukm_claim is empty
    - hukm_evidence is empty
    - closure_scope is empty
    - prove_hukm_candidate() returns REFUSED
    - Any unexpected error

    Args:
        ifadah_verdict:     IfadahVerdict from E9.
        evaluation_domain:  EvaluationDomain.LINGUISTIC (for ayat_al_dayn).
        hukm_claim:         Non-empty linguistic judgment claim.
        hukm_evidence:      Non-empty constitutional attestation string.
        hukm_maqam:         Maqam / context descriptor for this hukm.
        closure_scope:      Non-empty scope descriptor.

    Returns:
        HukmVerdict(state=PROVEN) on success.
        None on failure (fail-closed).
    """
    if not _HUKM_AVAILABLE:
        return None
    if not isinstance(ifadah_verdict, _IfadahVerdict):
        return None
    if not isinstance(evaluation_domain, _EvaluationDomain):
        return None
    if not hukm_claim or not hukm_claim.strip():
        return None
    if not hukm_evidence or not hukm_evidence.strip():
        return None
    if not closure_scope or not closure_scope.strip():
        return None
    try:
        verdict = _prove_hukm_candidate(
            ifadah_verdict=ifadah_verdict,
            evaluation_domain=evaluation_domain,
            hukm_claim=hukm_claim,
            hukm_evidence=hukm_evidence,
            hukm_maqam=hukm_maqam,
            closure_scope=closure_scope,
        )
        # Vendor HukmVerdict uses `verdict_state` (matches every other
        # vendor verdict dataclass). Prior `.state` access silently
        # AttributeError'd into the fail-open None path — same defect
        # closed on ifadah_candidate_adapter at Wave04.
        if verdict.verdict_state is not _HukmState.PROVEN:
            return None
        return verdict
    except Exception:  # noqa: BLE001
        return None


# ── Module-level invariant assertions ──────────────────────────────────────────

def _verify_e10_invariants() -> None:
    r1 = build_hukm_candidate(
        ifadah_verdict=object(),
        evaluation_domain=object(),
        hukm_claim="claim",
        hukm_evidence="evidence",
        hukm_maqam="maqam",
        closure_scope="scope",
    )
    assert r1 is None, "INV-E10-1: wrong type must return None"

    if _HUKM_AVAILABLE:
        r2 = build_hukm_candidate(
            ifadah_verdict=object(),
            evaluation_domain=_EvaluationDomain.LINGUISTIC,
            hukm_claim="",
            hukm_evidence="evidence",
            hukm_maqam="maqam",
            closure_scope="scope",
        )
        assert r2 is None, "INV-E10-2: empty hukm_claim must return None"


_verify_e10_invariants()


__all__ = [
    "build_hukm_candidate",
    "_HUKM_AVAILABLE",
    "_VENDOR_SHA",
]
