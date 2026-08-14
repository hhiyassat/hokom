"""Typed builders — invoke native vendor producers and return DownstreamStageOutcome.

Every builder here calls the exact native ``prove_*`` vendor function
(or ``bridge_tanzil_to_audit`` for the audit stage) and packages the
result into a :class:`DownstreamStageOutcome`. Vendor REFUSED
outcomes are preserved with their full ``failure_code``, ``trace_ref``,
and residuals — never collapsed to ``None``.

The existing None-returning adapters
(``hukm_candidate_adapter`` etc.) remain unchanged so prior tests
that assert ``build_x(...) is None`` continue to pass. These typed
builders are additive.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

from .typed_outcomes import (
    DownstreamStageOutcome,
    build_accept_outcome, build_refused_outcome,
)

# ── Vendor path ────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"

_VENDOR_AVAILABLE = False
try:
    _vs = str(_VENDOR_PATH)
    if _vs not in sys.path:
        sys.path.insert(0, _vs)
    from taaqqul_slot_geometry.weight.hukm_candidate import (  # type: ignore
        HukmVerdict as _HukmVerdict, HukmState as _HukmState,
        prove_hukm_candidate as _prove_hukm_candidate,
    )
    from taaqqul_slot_geometry.weight.manat_candidate import (  # type: ignore
        ManatVerdict as _ManatVerdict, ManatState as _ManatState,
        prove_manat_candidate as _prove_manat_candidate,
    )
    from taaqqul_slot_geometry.weight.tanzil_candidate import (  # type: ignore
        TanzilVerdict as _TanzilVerdict, TanzilState as _TanzilState,
        prove_tanzil_candidate as _prove_tanzil_candidate,
    )
    from taaqqul_slot_geometry.weight.mantuq_closure import (  # type: ignore
        MantuqClosureVerdict as _MantuqClosureVerdict,
        MantuqClosureState as _MantuqClosureState,
        prove_mantuq_closure as _prove_mantuq_closure,
    )
    from taaqqul_slot_geometry.weight.mafhum_closure import (  # type: ignore
        MafhumClosureVerdict as _MafhumClosureVerdict,
        MafhumClosureState as _MafhumClosureState,
        prove_mafhum_closure as _prove_mafhum_closure,
    )
    from taaqqul_slot_geometry.weight.ifadah_candidate import (  # type: ignore
        IfadahVerdict as _IfadahVerdict,
    )
    from taaqqul_slot_geometry.weight.maqam_context_boundary import (  # type: ignore
        MaqamContextBoundaryVerdict as _MaqamContextBoundaryVerdict,
    )
    from taaqqul_slot_geometry.audit.tanzil_bridge import (  # type: ignore
        AuditBridgeState as _AuditBridgeState,
        AuditedTanzilBridgeVerdict as _AuditedTanzilBridgeVerdict,
        bridge_tanzil_to_audit as _bridge_tanzil_to_audit,
    )
    _VENDOR_AVAILABLE = True
except ImportError:
    pass


# ── Small helper — never re-import inside hot loops ─────────────────────

def _verdict_trace_ref(verdict: Any) -> str:
    """Best-effort trace_ref extraction from any vendor verdict."""
    if verdict is None:
        return ""
    tr = getattr(verdict, "trace_ref", None)
    if isinstance(tr, str) and tr:
        return tr
    cand = getattr(verdict, "candidate", None)
    if cand is not None:
        tr = getattr(cand, "trace_ref", None)
        if isinstance(tr, str) and tr:
            return tr
    return ""


def _verdict_residuals(verdict: Any) -> tuple:
    if verdict is None:
        return ()
    r = getattr(verdict, "residuals", None)
    if r is None:
        cand = getattr(verdict, "candidate", None)
        if cand is not None:
            r = getattr(cand, "residuals", None)
    if r is None:
        return ()
    return tuple(r)


def _from_reasoning_verdict(
    verdict: Any, stage: str, proven_state: Any,
) -> DownstreamStageOutcome:
    """Package a reasoning-DAG verdict (has ``verdict_state``)."""
    state = getattr(verdict, "verdict_state", None)
    tr = _verdict_trace_ref(verdict)
    res = _verdict_residuals(verdict)
    if state is proven_state:
        return build_accept_outcome(
            stage=stage, verdict_state="PROVEN",
            native_verdict=verdict, trace_ref=tr, residuals=res,
        )
    return build_refused_outcome(
        stage=stage, native_verdict=verdict,
        failure_code=getattr(verdict, "failure_code", None),
        trace_ref=tr, residuals=res,
    )


# ── Hukm ────────────────────────────────────────────────────────────────

def build_hukm_outcome(
    *, ifadah_verdict: Any, evaluation_domain: Any,
    hukm_claim: str, hukm_evidence: str, hukm_maqam: str,
    closure_scope: str,
) -> Optional[DownstreamStageOutcome]:
    if not _VENDOR_AVAILABLE:
        return None
    if not isinstance(ifadah_verdict, _IfadahVerdict):
        return None
    try:
        v = _prove_hukm_candidate(
            ifadah_verdict=ifadah_verdict,
            evaluation_domain=evaluation_domain,
            hukm_claim=hukm_claim, hukm_evidence=hukm_evidence,
            hukm_maqam=hukm_maqam, closure_scope=closure_scope,
        )
    except Exception:  # noqa: BLE001
        return None
    return _from_reasoning_verdict(v, "hukm", _HukmState.PROVEN)


# ── Manat ───────────────────────────────────────────────────────────────

def build_manat_outcome(
    *, hukm_verdict: Any, manat_mode: Any,
    manat_description: str, effective_attribute_candidate: str,
    conditions: tuple = (), preventers: tuple = (),
    manat_evidence: str, manat_domain: str, closure_scope: str,
) -> Optional[DownstreamStageOutcome]:
    if not _VENDOR_AVAILABLE:
        return None
    if not isinstance(hukm_verdict, _HukmVerdict):
        return None
    try:
        v = _prove_manat_candidate(
            hukm_verdict=hukm_verdict, manat_mode=manat_mode,
            manat_description=manat_description,
            effective_attribute_candidate=effective_attribute_candidate,
            conditions=tuple(conditions), preventers=tuple(preventers),
            manat_evidence=manat_evidence,
            manat_domain=manat_domain, closure_scope=closure_scope,
        )
    except Exception:  # noqa: BLE001
        return None
    return _from_reasoning_verdict(v, "manat", _ManatState.PROVEN)


# ── Tanzil ──────────────────────────────────────────────────────────────

def build_tanzil_outcome(
    *, hukm_verdict: Any, manat_verdict: Any,
    reality_evidence: str, instance_descriptor: str,
    tanzil_scope: str, presentation_warning: str = "CANDIDATE",
    not_execution_marker: bool = True,
) -> Optional[DownstreamStageOutcome]:
    if not _VENDOR_AVAILABLE:
        return None
    if not isinstance(hukm_verdict, _HukmVerdict):
        return None
    if not isinstance(manat_verdict, _ManatVerdict):
        return None
    if not not_execution_marker:
        return None
    try:
        v = _prove_tanzil_candidate(
            hukm_verdict=hukm_verdict, manat_verdict=manat_verdict,
            reality_evidence=reality_evidence,
            instance_descriptor=instance_descriptor,
            tanzil_scope=tanzil_scope,
            presentation_warning=presentation_warning,
            not_execution_marker=not_execution_marker,
        )
    except Exception:  # noqa: BLE001
        return None
    return _from_reasoning_verdict(v, "tanzil", _TanzilState.PROVEN)


# ── Mantuq ──────────────────────────────────────────────────────────────

def build_mantuq_outcome(
    *, ifadah_verdict: Any, maqam_verdict: Any,
    mantuq_scope: str, spoken_surface_ref: str,
    mantuq_evidence: str, closure_scope: str,
) -> Optional[DownstreamStageOutcome]:
    if not _VENDOR_AVAILABLE:
        return None
    if not isinstance(ifadah_verdict, _IfadahVerdict):
        return None
    if not isinstance(maqam_verdict, _MaqamContextBoundaryVerdict):
        return None
    try:
        v = _prove_mantuq_closure(
            ifadah_verdict=ifadah_verdict, maqam_verdict=maqam_verdict,
            mantuq_scope=mantuq_scope, spoken_surface_ref=spoken_surface_ref,
            mantuq_evidence=mantuq_evidence, closure_scope=closure_scope,
        )
    except Exception:  # noqa: BLE001
        return None
    return _from_reasoning_verdict(v, "mantuq", _MantuqClosureState.PROVEN)


# ── Mafhum ──────────────────────────────────────────────────────────────

def build_mafhum_outcome(
    *, mantuq_verdict: Any, outside_boundary: str, branch_type: Any,
    branch_subtype: str, qayd: str, source_domain: str,
    cross_domain_transfer: str, mantuq_blocks: bool = False,
    residuals: tuple = (),
) -> Optional[DownstreamStageOutcome]:
    if not _VENDOR_AVAILABLE:
        return None
    if not isinstance(mantuq_verdict, _MantuqClosureVerdict):
        return None
    try:
        v = _prove_mafhum_closure(
            mantuq_verdict=mantuq_verdict,
            outside_boundary=outside_boundary,
            branch_type=branch_type, branch_subtype=branch_subtype,
            qayd=qayd, source_domain=source_domain,
            cross_domain_transfer=cross_domain_transfer,
            mantuq_blocks=mantuq_blocks, residuals=tuple(residuals),
        )
    except Exception:  # noqa: BLE001
        return None
    return _from_reasoning_verdict(v, "mafhum", _MafhumClosureState.PROVEN)


# ── Audit-layer Tanzil bridge (PR-22-AUDIT) ─────────────────────────────

def build_audited_tanzil_bridge_outcome(
    *, tanzil_verdict: Any,
) -> Optional[DownstreamStageOutcome]:
    """Invoke the native ``bridge_tanzil_to_audit`` audit-layer producer.

    Note: ``AuditedTanzilBridgeVerdict`` uses the field name ``state``
    (not ``verdict_state``) — vendor convention for audit-layer DTOs
    differs from reasoning-DAG DTOs. This is confirmed by independent
    reading of ``audit/tanzil_bridge.py``.
    """
    if not _VENDOR_AVAILABLE:
        return None
    if not isinstance(tanzil_verdict, _TanzilVerdict):
        return None
    try:
        v = _bridge_tanzil_to_audit(tanzil_verdict=tanzil_verdict)
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(v, _AuditedTanzilBridgeVerdict):
        return None
    # Audit bridge uses `state`, not `verdict_state`.
    state = v.state
    tr = v.trace_ref if isinstance(v.trace_ref, str) else ""
    res = tuple(v.residuals) if v.residuals is not None else ()
    if state is _AuditBridgeState.SURFACED:
        return build_accept_outcome(
            stage="audited_tanzil_bridge", verdict_state="SURFACED",
            native_verdict=v, trace_ref=tr, residuals=res,
        )
    return build_refused_outcome(
        stage="audited_tanzil_bridge", native_verdict=v,
        failure_code=v.failure_code, trace_ref=tr, residuals=res,
    )


__all__ = [
    "_VENDOR_AVAILABLE", "_VENDOR_SHA",
    "build_hukm_outcome",
    "build_manat_outcome",
    "build_tanzil_outcome",
    "build_mantuq_outcome",
    "build_mafhum_outcome",
    "build_audited_tanzil_bridge_outcome",
]
