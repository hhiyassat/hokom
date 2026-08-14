"""Chain Report Adapter — E15/G_E15_03

CONSTITUTIONAL_RECONCILIATION_01 Phase: E15 (G_E15_03)

Purpose:
    Implements G_E15_03: produce a pre-semantic chain report from the E6
    VerbalMadlulCandidate terminal.

    One operation:
      assemble_chain_report(terminal: VerbalMadlulCandidate) → ChainReportResult

Constitutional chain position:
    Input:  E6 VerbalMadlulCandidate (the last pre-semantic carrier before Ifadah)
    Output: ChainReportResult documenting the full pre-semantic chain

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None
    - terminal must be VerbalMadlulCandidate (type guard enforced)
    - ChainReport is a read-only audit — it does not promote or emit verdicts
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - chain_report.py uses StrEnum → fails to import on 3.10
    - All public functions return None on 3.10 (fail-closed)

Phase: E15 (G_E15_03) — CHAIN_REPORT
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
_CHAIN_REPORT_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    from taaqqul_slot_geometry.weight.chain_report import (  # type: ignore
        ChainReportState    as _ChainReportState,
        ChainReportResult   as _ChainReportResult,
        PreSemanticChainReport as _PreSemanticChainReport,
        assemble_chain_report as _assemble_chain_report,
    )
    from taaqqul_slot_geometry.weight.verbal_madlul import (  # type: ignore
        VerbalMadlulCandidate as _VerbalMadlulCandidate,
    )
    _CHAIN_REPORT_AVAILABLE = True
except ImportError:
    pass


def build_chain_report(
    verbal_madlul_candidate: Any,
) -> "Optional[Any]":
    """
    E15/G_E15_03: Assemble pre-semantic chain report.

    Takes the VerbalMadlulCandidate (terminal of E6 — last pre-semantic
    carrier before Ifadah) and produces a ChainReportResult documenting
    the full E4B→E4C→E5→E6 pre-semantic chain.

    This is a read-only audit operation — it does not produce verdicts
    and does not advance the pipeline state.

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - verbal_madlul_candidate is not VerbalMadlulCandidate
    - assemble_chain_report() raises any exception

    Args:
        verbal_madlul_candidate: VerbalMadlulCandidate from E6.

    Returns:
        ChainReportResult on success.
        None on failure (fail-closed).
    """
    if not _CHAIN_REPORT_AVAILABLE:
        return None
    if not isinstance(verbal_madlul_candidate, _VerbalMadlulCandidate):
        return None
    try:
        return _assemble_chain_report(terminal=verbal_madlul_candidate)
    except Exception:  # noqa: BLE001
        return None


# ── Module-level invariant assertions ──────────────────────────────────────────

def _verify_chain_report_invariants() -> None:
    r1 = build_chain_report(verbal_madlul_candidate=object())
    assert r1 is None, "INV-CHAIN-1: wrong type must return None"
    r2 = build_chain_report(verbal_madlul_candidate=None)
    assert r2 is None, "INV-CHAIN-2: None must return None"


_verify_chain_report_invariants()


__all__ = [
    "build_chain_report",
    "_CHAIN_REPORT_AVAILABLE",
    "_VENDOR_SHA",
]
