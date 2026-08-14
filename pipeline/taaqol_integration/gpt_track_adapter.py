"""GPT Track Adapter — E15_GPT_REASONABLENESS

CONSTITUTIONAL_RECONCILIATION_01 Phase: E15

Purpose:
    Implements E15: the GPT reasonableness track (R1-R8 deterministic gates).

    R1: GPTAnswerInput — input contract validation
    R2: MaqamGPT — maqam boundary
    R3: MantuqGPT — mantuq boundary (explicit claims only)
    R4: MafhumGPT — mafhum boundary (licensed implication)
    R5: OriginBindingGateResult — origin binding gate
    R6: ReasonablenessGateReport — run_reasonableness_gates (six gates)
    R7: ReasonablenessVerdict — final deterministic verdict
    R8: AnswerAudit (audit/answer_audit.py) — full chain audit

    LIVE PROVIDER:
    - Live LLM provider is NOT used in deterministic R1-R8 track
    - Live provider integration = OWNER_DECISION_REQUIRED (documented, not blocking)
    - G_E15_02: Live provider authorization = OWNER_DECISION_REQUIRED

Constitutional invariants:
    - FAIL-CLOSED: any error → returns None
    - GPT track is DETERMINISTIC — no live LLM calls in this adapter
    - NO_LIVE_PROVIDER: PROVIDER_GUARD prevents live calls
    - SpeechForce inputs: KHABAR or INSHA only
    - All gate verdicts are read from OriginBindingGateResult (R5 output)
    - ReasonablenessGateReport does NOT promote verdicts
    - VENDOR_SHA embedded; AUTONOMOUS_COMMIT_MODE = 0

Python 3.10 compat:
    - gpt/ modules use StrEnum → fail to import on 3.10
    - All public functions return None on 3.10 (fail-closed)

OWNER_DECISION_REQUIRED:
    Live provider authentication and model selection require owner authorization.
    Documented here per G_E15_02. Does NOT block E15 deterministic closure.

Phase: E15 — GPT_REASONABLENESS (R1-R8)
VENDOR_SHA: bc9d1ea5ef45970f5f3ec132441e30fd54b3da52
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

# ── Vendor path ────────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[2]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA  = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

# ── Constitutional constants ────────────────────────────────────────────────────
LIVE_PROVIDER_AUTHORIZATION = "OWNER_DECISION_REQUIRED"
NO_LIVE_PROVIDER_IN_DETERMINISTIC_TRACK = True

# ── Fail-closed vendor imports — R1 through R7 ───────────────────────────────
_GPT_TRACK_AVAILABLE = False

try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)

    # R1: Input contract
    from taaqqul_slot_geometry.gpt.input_contract import (  # type: ignore
        GPTAnswerInput       as _GPTAnswerInput,
        InputRiskLevel       as _InputRiskLevel,
        InputEvidenceNeed    as _InputEvidenceNeed,
        InputTimeSensitivity as _InputTimeSensitivity,
    )
    # R2: Maqam boundary
    from taaqqul_slot_geometry.gpt.maqam_boundary import (  # type: ignore
        MaqamGPT                as _MaqamGPT,
        MaqamCommunicationMode  as _MaqamCommunicationMode,
    )
    # R3: Mantuq boundary
    from taaqqul_slot_geometry.gpt.mantuq_boundary import (  # type: ignore
        MantuqGPT    as _MantuqGPT,
        ExplicitClaim as _ExplicitClaim,
    )
    # R4: Mafhum boundary
    from taaqqul_slot_geometry.gpt.mafhum_boundary import (  # type: ignore
        MafhumGPT as _MafhumGPT,
    )
    # R5: Origin binding gate
    from taaqqul_slot_geometry.gpt.origin_binding_gate import (  # type: ignore
        OriginBindingGateResult as _OriginBindingGateResult,
    )
    # R6: Reasonableness gates
    from taaqqul_slot_geometry.gpt.reasonableness_gates import (  # type: ignore
        ReasonablenessGateReport      as _ReasonablenessGateReport,
        ReasonablenessGateReportState as _ReasonablenessGateReportState,
        run_reasonableness_gates      as _run_reasonableness_gates,
    )
    # R7: Reasonableness verdict
    from taaqqul_slot_geometry.gpt.reasonableness_verdict import (  # type: ignore
        ReasonablenessVerdict as _ReasonablenessVerdict,
    )
    _GPT_TRACK_AVAILABLE = True
except ImportError:
    pass

# ── Fail-closed vendor import — R8 answer audit ───────────────────────────────
_ANSWER_AUDIT_AVAILABLE = False
try:
    from taaqqul_slot_geometry.audit.answer_audit import (  # type: ignore
        AnswerAudit  as _AnswerAudit,
        AuditedAnswer as _AuditedAnswer,
    )
    _ANSWER_AUDIT_AVAILABLE = True
except ImportError:
    pass


# ── R6: run_reasonableness_gates wrapper ──────────────────────────────────────

def run_gpt_reasonableness_gates(
    origin_binding_result: Any,
) -> "Optional[Any]":
    """
    E15/R6: Run the six deterministic GPT reasonableness gates.

    Takes OriginBindingGateResult (R5 output) and returns a
    ReasonablenessGateReport. This is a DETERMINISTIC operation —
    no live LLM calls are made.

    FAIL-CLOSED: Returns None if:
    - Python 3.10 (vendor not available)
    - origin_binding_result is not OriginBindingGateResult or None
      (vendor accepts None for degenerate case)
    - run_reasonableness_gates() raises any exception

    Args:
        origin_binding_result: OriginBindingGateResult from R5, or None.

    Returns:
        ReasonablenessGateReport on success.
        None on failure (fail-closed).
    """
    if not _GPT_TRACK_AVAILABLE:
        return None
    # vendor accepts None (degenerate case produces REFUSED report)
    if origin_binding_result is not None and not isinstance(
        origin_binding_result, _OriginBindingGateResult
    ):
        return None
    try:
        return _run_reasonableness_gates(binding_result=origin_binding_result)
    except Exception:  # noqa: BLE001
        return None


# ── Live provider guard ────────────────────────────────────────────────────────

def get_live_provider_authorization_status() -> str:
    """
    E15/G_E15_02: Return live provider authorization status.

    Live LLM provider integration requires owner authorization.
    This function documents the status — it does NOT enable the provider.

    Returns:
        "OWNER_DECISION_REQUIRED" — always, per constitutional constraint.
    """
    return LIVE_PROVIDER_AUTHORIZATION


def is_deterministic_track_available() -> bool:
    """
    Check whether E15 deterministic R1-R8 track is available.

    Returns True when Python 3.12+ and vendor imports succeed.
    The deterministic track does NOT require live provider authorization.
    """
    return _GPT_TRACK_AVAILABLE


# ── Module-level invariant assertions ──────────────────────────────────────────

def _verify_e15_invariants() -> None:
    """Verify E15 adapter fail-closed invariants (import-time)."""
    # INV-E15-1: wrong type → None
    r1 = run_gpt_reasonableness_gates(origin_binding_result=object())
    assert r1 is None, "INV-E15-1: wrong type must return None"

    # INV-E15-2: live provider always OWNER_DECISION_REQUIRED
    status = get_live_provider_authorization_status()
    assert status == "OWNER_DECISION_REQUIRED", (
        f"INV-E15-2: live provider status must be OWNER_DECISION_REQUIRED, got {status}"
    )

    # INV-E15-3: available must be bool
    assert isinstance(is_deterministic_track_available(), bool), (
        "INV-E15-3: is_deterministic_track_available must return bool"
    )


_verify_e15_invariants()


__all__ = [
    "run_gpt_reasonableness_gates",
    "get_live_provider_authorization_status",
    "is_deterministic_track_available",
    "LIVE_PROVIDER_AUTHORIZATION",
    "NO_LIVE_PROVIDER_IN_DETERMINISTIC_TRACK",
    "_GPT_TRACK_AVAILABLE",
    "_ANSWER_AUDIT_AVAILABLE",
    "_VENDOR_SHA",
]
