"""Tanzil Candidate Adapter — E12_TANZIL_CANDIDATE

CONSTITUTIONAL_RECONCILIATION_01 Phase: E12

Purpose:
    Implements E12: the tanzil (presentation-bound application readiness) layer.

    One operation:
      prove_tanzil_candidate(HukmVerdict, ManatVerdict,
          reality_evidence, instance_descriptor, tanzil_scope,
          presentation_warning, not_execution_marker)
          → TanzilVerdict(PROVEN)

Constitutional chain (E0→E12):
    ...
    E11 = MANAT CANDIDATE (ManatVerdict.PROVEN)
    E12 = TANZIL CANDIDATE ← THIS MODULE

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None
    - TanzilCandidate is TERMINAL (not_execution_marker=True always for ayat_al_dayn)
    - not_execution_marker MUST be True for ayat_al_dayn (no execution authority)
    - reality_evidence must be non-empty (constitutional attestation)
    - instance_descriptor must be non-empty
    - tanzil_scope must be non-empty
    - No rank promotion beyond TANZIL_RANK_CEILING
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - tanzil_candidate.py uses StrEnum → fails to import on 3.10
    - All public functions return None on 3.10 (fail-closed)

Phase: E12 — TANZIL CANDIDATE
Prior: E10 → HukmVerdict(PROVEN) + E11 → ManatVerdict(PROVEN)
Output: TanzilVerdict(PROVEN, candidate=TanzilCandidate) with TERMINAL marker
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
_TANZIL_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    from taaqqul_slot_geometry.weight.tanzil_candidate import (  # type: ignore
        TanzilState            as _TanzilState,
        TanzilCandidate        as _TanzilCandidate,
        TanzilPresentationEnvelope as _TanzilPresentationEnvelope,
        TanzilVerdict          as _TanzilVerdict,
        prove_tanzil_candidate as _prove_tanzil_candidate,
        TANZIL_RANK_CEILING    as _TANZIL_RANK_CEILING,
    )
    from taaqqul_slot_geometry.weight.hukm_candidate import (  # type: ignore
        HukmVerdict as _HukmVerdict,
    )
    from taaqqul_slot_geometry.weight.manat_candidate import (  # type: ignore
        ManatVerdict as _ManatVerdict,
    )
    _TANZIL_AVAILABLE = True
except ImportError:
    pass


def build_tanzil_candidate(
    hukm_verdict: Any,
    manat_verdict: Any,
    reality_evidence: str,
    instance_descriptor: str,
    tanzil_scope: str,
    presentation_warning: str = "",
    not_execution_marker: bool = True,
) -> "Optional[Any]":
    """
    E12: Prove tanzil (presentation-bound application readiness) candidate.

    CRITICAL: not_execution_marker MUST remain True for ayat_al_dayn — this
    adapter enforces it. Passing False will raise ValueError inside vendor.
    The parameter is exposed only for constitutional completeness; callers
    should always use the default (True).

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - hukm_verdict is not HukmVerdict
    - manat_verdict is not ManatVerdict
    - reality_evidence is empty
    - instance_descriptor is empty
    - tanzil_scope is empty
    - not_execution_marker is False (constitutional guard)
    - prove_tanzil_candidate() returns REFUSED
    - Any unexpected error

    Args:
        hukm_verdict:         HukmVerdict from E10.
        manat_verdict:        ManatVerdict from E11.
        reality_evidence:     Non-empty reality attestation string.
        instance_descriptor:  Non-empty instance description.
        tanzil_scope:         Non-empty scope descriptor.
        presentation_warning: Optional warning for presentation layer.
        not_execution_marker: MUST be True (default). Ayat-al-dayn has no
                              execution authority — TERMINAL marker required.

    Returns:
        TanzilVerdict(state=PROVEN) with TERMINAL marker on success.
        None on failure (fail-closed).
    """
    if not _TANZIL_AVAILABLE:
        return None
    if not isinstance(hukm_verdict, _HukmVerdict):
        return None
    if not isinstance(manat_verdict, _ManatVerdict):
        return None
    if not reality_evidence or not reality_evidence.strip():
        return None
    if not instance_descriptor or not instance_descriptor.strip():
        return None
    if not tanzil_scope or not tanzil_scope.strip():
        return None
    # Constitutional guard: ayat_al_dayn never executes
    if not not_execution_marker:
        return None
    try:
        verdict = _prove_tanzil_candidate(
            hukm_verdict=hukm_verdict,
            manat_verdict=manat_verdict,
            reality_evidence=reality_evidence,
            instance_descriptor=instance_descriptor,
            tanzil_scope=tanzil_scope,
            presentation_warning=presentation_warning,
            not_execution_marker=not_execution_marker,
        )
        # Vendor uses `verdict_state`, not `.state`.
        if verdict.verdict_state is not _TanzilState.PROVEN:
            return None
        return verdict
    except Exception:  # noqa: BLE001
        return None


# ── Module-level invariant assertions ──────────────────────────────────────────

def _verify_e12_invariants() -> None:
    r1 = build_tanzil_candidate(
        hukm_verdict=object(),
        manat_verdict=object(),
        reality_evidence="evidence",
        instance_descriptor="instance",
        tanzil_scope="scope",
    )
    assert r1 is None, "INV-E12-1: wrong type must return None"

    # INV-E12-2: not_execution_marker=False → None (constitutional guard)
    r2 = build_tanzil_candidate(
        hukm_verdict=object(),
        manat_verdict=object(),
        reality_evidence="evidence",
        instance_descriptor="instance",
        tanzil_scope="scope",
        not_execution_marker=False,
    )
    assert r2 is None, "INV-E12-2: not_execution_marker=False must return None"

    r3 = build_tanzil_candidate(
        hukm_verdict=object(),
        manat_verdict=object(),
        reality_evidence="",
        instance_descriptor="instance",
        tanzil_scope="scope",
    )
    assert r3 is None, "INV-E12-3: empty reality_evidence must return None"


_verify_e12_invariants()


__all__ = [
    "build_tanzil_candidate",
    "_TANZIL_AVAILABLE",
    "_VENDOR_SHA",
]
