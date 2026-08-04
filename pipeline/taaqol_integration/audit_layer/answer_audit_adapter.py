"""Thin Hokom adapter around the native ``AnswerAudit`` engine.

Boundary discipline (per Wave09 directive §C — AnswerAudit ownership):

Hokom owns only:
  * input adapter from the audited-Tanzil span predecessor;
  * provider configuration injection (``ModelClient`` construction);
  * transport-exception lifecycle (converting provider timeouts / transport
    errors / malformed responses into typed integration outcomes);
  * persistence of the returned native ``AuditedAnswer``;
  * cross-component trace linkage for the artifact.

Hokom does NOT:
  * construct :class:`AuditedAnswer` directly (vendor's job);
  * decide gamma, gate, or successor emission (pure kernel's job);
  * infer approval from provider text;
  * map expected answers to verdicts;
  * fabricate traces or residuals;
  * produce reasonableness certificates.

The adapter builds a claim :class:`SlotGraph` from the audited-Tanzil
predecessor using ``GenerationSource.TRANSITION_VERDICT`` — the vendor's
own third licensed generation source (docs/17 §1) — because the
predecessor IS a licensed vendor verdict. It does not synthesise the
graph from raw text.

Every adapter call returns a :class:`AnswerAuditOutcome` — a Hokom-side
typed carrier that wraps either:
  * ``native_verdict`` — the vendor :class:`AuditedAnswer`, when the
    engine completed (regardless of gate approval or refusal); or
  * ``integration_failure_code`` — a Hokom-side transport-layer failure
    marker when the provider raised before AnswerAudit could complete
    (timeout, connection error, malformed non-string response). The
    outcome is fail-closed with ``accepted=False`` and a named marker
    residual; no fabricated AuditedAnswer is ever constructed.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ── Vendor path ────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[3]
_VENDOR_PATH = _REPO_ROOT / "vendor" / "Taaqol-GPT" / "src"
_VENDOR_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"

_vs = str(_VENDOR_PATH)
if _vs not in sys.path:
    sys.path.insert(0, _vs)

_VENDOR_AUDIT_AVAILABLE = False
try:
    from taaqqul_slot_geometry.audit.answer_audit import (  # type: ignore
        AnswerAudit as _AnswerAudit,
        AuditedAnswer as _AuditedAnswer,
    )
    from taaqqul_slot_geometry.audit.model_client import (  # type: ignore
        ModelClient as _ModelClient,
    )
    from taaqqul_slot_geometry.audit.tanzil_bridge import (  # type: ignore
        AuditedTanzilBridgeVerdict as _AuditedTanzilBridgeVerdict,
        AuditBridgeState as _AuditBridgeState,
    )
    from taaqqul_slot_geometry.core.closure_state import (  # type: ignore
        ClosureState as _ClosureState,
    )
    from taaqqul_slot_geometry.core.evidence_contract import (  # type: ignore
        EvidenceContract as _EvidenceContract,
        EvidenceSource as _EvidenceSource,
    )
    from taaqqul_slot_geometry.core.failure_taxonomy import (  # type: ignore
        FailureCode as _FailureCode,
    )
    from taaqqul_slot_geometry.core.rank_lattice import Rank as _Rank  # type: ignore
    from taaqqul_slot_geometry.core.residual_policy import (  # type: ignore
        Residual as _Residual, ResidualKind as _ResidualKind,
    )
    from taaqqul_slot_geometry.core.slot_graph import (  # type: ignore
        Center as _Center,
        GenerationSource as _GenerationSource,
        Layer as _Layer,
        OpeningPolicy as _OpeningPolicy,
        OutputBoundary as _OutputBoundary,
        Slot as _Slot,
        SlotBoundary as _SlotBoundary,
        SlotGraph as _SlotGraph,
        SlotState as _SlotState,
        TraceRef as _TraceRef,
    )
    from taaqqul_slot_geometry.core.trace_ledger import (  # type: ignore
        TraceLedger as _TraceLedger,
    )
    from taaqqul_slot_geometry.core.transition_gate import (  # type: ignore
        TransitionGate as _TransitionGate,
    )
    from taaqqul_slot_geometry.core.transition_state import (  # type: ignore
        TransitionState as _TransitionState,
    )
    _VENDOR_AUDIT_AVAILABLE = True
except ImportError:
    pass


# ── Hokom-side integration failure vocabulary ──────────────────────────

# These names describe TRANSPORT-LAYER conditions the Hokom adapter
# observes before the vendor AnswerAudit engine can execute. They are
# NOT vendor FailureCode members — the vendor's failure taxonomy governs
# semantic refusals only. Hokom-side integration failures are named
# separately so they cannot be confused with a native audit verdict.
INTEGRATION_PROVIDER_TIMEOUT = "INTEGRATION_PROVIDER_TIMEOUT"
INTEGRATION_PROVIDER_TRANSPORT_FAILURE = "INTEGRATION_PROVIDER_TRANSPORT_FAILURE"
INTEGRATION_PROVIDER_MALFORMED_RESPONSE = "INTEGRATION_PROVIDER_MALFORMED_RESPONSE"
INTEGRATION_PROVIDER_EMPTY_RESPONSE = "INTEGRATION_PROVIDER_EMPTY_RESPONSE"
INTEGRATION_PROVIDER_EXCEPTION_UNEXPECTED = "INTEGRATION_PROVIDER_EXCEPTION_UNEXPECTED"


@dataclass(frozen=True, slots=True)
class AnswerAuditOutcome:
    """Hokom-side typed carrier for one AnswerAudit adapter invocation.

    Exactly one of ``native_verdict`` / ``integration_failure_code`` is
    populated:

    * ``native_verdict`` is a vendor :class:`AuditedAnswer` — the engine
      completed. ``accepted`` reflects vendor's own gate outcome
      (``gate_state is APPROVED``); a refused AuditedAnswer is still a
      completed engine call, not a Hokom failure.
    * ``integration_failure_code`` is set when the provider raised or
      returned a malformed payload before AnswerAudit could complete.
      ``native_verdict`` is None; ``accepted`` is False; a named marker
      residual describes the transport failure.
    """

    span_id: str
    predecessor_trace: str
    prompt_fingerprint: str
    response_fingerprint: str | None
    native_verdict: Any | None            # AuditedAnswer or None
    integration_failure_code: str | None  # INTEGRATION_* name or None
    integration_failure_detail: str
    accepted: bool
    reasonableness_status: str            # NOT_RUN / CARRIED / DEFERRED / R7_NOT_CONSUMED
    certificate_allowed: bool             # always False by law
    trace_ids: tuple[str, ...]
    residual_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        # Constitutional invariant: exactly one of native_verdict /
        # integration_failure_code is populated.
        if (self.native_verdict is None) == (self.integration_failure_code is None):
            raise ValueError(
                "AnswerAuditOutcome: exactly one of native_verdict / "
                "integration_failure_code must be populated (got both or "
                "neither)"
            )
        if self.accepted and self.integration_failure_code is not None:
            raise ValueError(
                "AnswerAuditOutcome: accepted=True is incompatible with "
                "an integration failure"
            )
        if self.certificate_allowed:
            raise ValueError(
                "AnswerAuditOutcome: certificate_allowed must be False "
                "(docs/56 §2 B4 — no certificate, no authority, no truth)"
            )


# ── Claim graph construction from audited-Tanzil predecessor ──────────

# Reserved constant strings — no per-input semantic inference.
_HOKOM_DOMAIN = "hokom.taaqol_integration.answer_audit"
_HOKOM_SCOPE = "wave09.audited_tanzil_bridge"


def _make_claim_graph_from_audited_tanzil(
    verdict: Any,
    *,
    span_id: str,
) -> Any:
    """Construct a claim :class:`SlotGraph` from an AuditedTanzilBridgeVerdict.

    Uses ``GenerationSource.TRANSITION_VERDICT`` because the predecessor
    IS a licensed vendor verdict — docs/17 §1 source 3. The graph
    carries the predecessor's trace anchor (identity continuity per
    docs/16 link 2) and preserves the predecessor's residuals verbatim.

    The claim graph is deliberately minimal: one filled slot representing
    the audited outcome plus the predecessor's residuals. No slot value
    is inferred from Quranic text; the value is the vendor's own audit
    bridge state string.
    """
    if not _VENDOR_AUDIT_AVAILABLE:
        raise RuntimeError(
            "vendor audit modules unavailable at "
            f"{_VENDOR_PATH}; ensure the pin is bc9d1ea+"
        )
    if not isinstance(verdict, _AuditedTanzilBridgeVerdict):
        raise TypeError(
            "predecessor must be AuditedTanzilBridgeVerdict, got "
            f"{type(verdict).__name__}"
        )
    if not isinstance(span_id, str) or not span_id.strip():
        raise ValueError("span_id must be a non-empty string")

    # Anchor: chain the predecessor's own trace_ref for identity continuity.
    predecessor_anchor = (
        verdict.trace_ref if isinstance(verdict.trace_ref, str)
        and verdict.trace_ref.strip()
        else f"hokom:audited_tanzil:{span_id}"
    )
    trace_ref = _TraceRef(
        anchor=predecessor_anchor,
        kind="TRANSITION_VERDICT",
    )

    boundary = _SlotBoundary(
        domain=_HOKOM_DOMAIN,
        scope=_HOKOM_SCOPE,
        refusal_codes=(_FailureCode.BOUNDARY_MISSING,),
    )
    opening = _OpeningPolicy(allowed_potentials=frozenset({"SURFACED", "REFUSED"}))
    slot = _Slot(
        name="audited_tanzil_bridge_state",
        value_state=_SlotState.FILLED,
        boundary=boundary,
        opening=opening,
        required=True,
        value=verdict.state.value if hasattr(verdict.state, "value")
              else str(verdict.state),
    )
    center = _Center(
        identity_claim=f"span:{span_id}",
        domain=_HOKOM_DOMAIN,
        scope=_HOKOM_SCOPE,
        trace_ref=trace_ref,
    )
    output_boundary = _OutputBoundary(
        declared_layer=_Layer.CANDIDATE,
        output_layer=_Layer.SLOT,
    )
    # Preserve the predecessor's residuals verbatim (rule 4 — no
    # residual deletion at the Hokom seam).
    predecessor_residuals: tuple = ()
    src = getattr(verdict, "residuals", None)
    if src is not None:
        predecessor_residuals = tuple(
            r for r in src if isinstance(r, _Residual)
        )
    return _SlotGraph(
        center=center,
        slots=(slot,),
        boundary=boundary,
        residuals=predecessor_residuals,
        rank=_Rank.HYPOTHESIS,
        output_boundary=output_boundary,
        generation_source=_GenerationSource.TRANSITION_VERDICT,
    )


def _make_evidence_from_audited_tanzil(verdict: Any, *, span_id: str) -> Any:
    """Build an :class:`EvidenceContract` from the predecessor.

    The audited-Tanzil bridge's own trace_ref is the licensed evidence
    source — Hokom does not fabricate evidence text. Rank.STRONG is
    the vendor's convention for a well-formed prior verdict in the
    reasoning-DAG's audit layer (matches vendor test _strong_evidence()).
    """
    predecessor_anchor = (
        verdict.trace_ref if isinstance(verdict.trace_ref, str)
        and verdict.trace_ref.strip()
        else f"hokom:audited_tanzil:{span_id}"
    )
    source = _EvidenceSource(
        name=f"audited_tanzil_bridge:{span_id}",
        kind="prior-audited-verdict",
        rank=_Rank.STRONG,
        trace_ref=_TraceRef(anchor=predecessor_anchor, kind="TRANSITION_VERDICT"),
    )
    return _EvidenceContract(sources=(source,))


def _make_gate() -> Any:
    """Build a Wave09 audit gate.

    The gate name and rank are Hokom-side integration configuration; the
    gate's decision function is vendor-provided and pure.
    """
    return _TransitionGate(
        name="wave09-audit-integration",
        gate_rank=_Rank.LICENSED,
    )


# ── Main entrypoint ────────────────────────────────────────────────────

def _fingerprint(payload: object) -> str:
    """Deterministic SHA-256 fingerprint of a string or bytes payload."""
    import hashlib
    if isinstance(payload, bytes):
        return hashlib.sha256(payload).hexdigest()
    return hashlib.sha256(str(payload).encode("utf-8")).hexdigest()


def audit_bridge_verdict(
    audited_tanzil_verdict: Any,
    *,
    span_id: str,
    prompt: str,
    model_client: Any,
    ledger: Any | None = None,
) -> AnswerAuditOutcome:
    """Adapter — audit a real audited-Tanzil predecessor through vendor AnswerAudit.

    Parameters
    ----------
    audited_tanzil_verdict
        A real vendor :class:`AuditedTanzilBridgeVerdict` (from the
        upstream span's ``bridge_tanzil_to_audit`` invocation). Wrong
        type → raises TypeError (structural fail-closed).
    span_id
        The Ayat span identifier for artifact traceability. Non-empty
        string required.
    prompt
        The prompt string handed to the model client. Never the raw
        Quranic surface — it should be an integration prompt derived
        from the predecessor's trace (Hokom-owned).
    model_client
        Any object implementing the vendor's ``ModelClient`` protocol
        (single ``complete(prompt: str) -> str`` method). The client
        may raise; the adapter catches and converts to a typed
        integration outcome.
    ledger
        Optional pre-existing :class:`TraceLedger`. When None, a fresh
        ledger is constructed per call — safe for deterministic tests.

    Returns
    -------
    AnswerAuditOutcome
        The Hokom typed carrier. Exactly one of ``native_verdict`` /
        ``integration_failure_code`` is populated.

    Raises
    ------
    TypeError
        Wrong-type predecessor (programmer mistake, not a runtime
        refusal; caught at the boundary per vendor convention).
    RuntimeError
        Vendor audit modules unavailable at the pinned SHA.
    """
    if not _VENDOR_AUDIT_AVAILABLE:
        raise RuntimeError(
            "vendor audit modules unavailable — check vendor pin"
        )
    if not isinstance(audited_tanzil_verdict, _AuditedTanzilBridgeVerdict):
        raise TypeError(
            "audit_bridge_verdict requires an AuditedTanzilBridgeVerdict "
            f"predecessor, got {type(audited_tanzil_verdict).__name__}"
        )
    if not isinstance(span_id, str) or not span_id.strip():
        raise ValueError("span_id must be a non-empty string")
    if not isinstance(prompt, str):
        raise TypeError("prompt must be a str")
    if not isinstance(model_client, _ModelClient):
        raise TypeError(
            "model_client must implement the ModelClient protocol "
            "(complete(prompt: str) -> str)"
        )

    # Build the claim graph, evidence, and gate from real predecessor data.
    claim_graph = _make_claim_graph_from_audited_tanzil(
        audited_tanzil_verdict, span_id=span_id,
    )
    evidence = _make_evidence_from_audited_tanzil(
        audited_tanzil_verdict, span_id=span_id,
    )
    gate = _make_gate()

    ledger = ledger if ledger is not None else _TraceLedger()
    audit = _AnswerAudit(client=model_client, ledger=ledger)

    prompt_fp = _fingerprint(prompt)
    predecessor_trace = (
        audited_tanzil_verdict.trace_ref if isinstance(
            audited_tanzil_verdict.trace_ref, str
        ) else ""
    )

    # Try to run the native audit; convert provider-layer exceptions to
    # typed integration outcomes. Vendor's own TypeError on a malformed
    # response is converted to INTEGRATION_PROVIDER_MALFORMED_RESPONSE
    # (with the vendor's exception message preserved in detail).
    integration_failure_code: str | None = None
    integration_failure_detail = ""
    native_verdict: Any | None = None
    response_fp: str | None = None
    try:
        native_verdict = audit.audit(
            prompt=prompt,
            claim_graph=claim_graph,
            gate=gate,
            target_layer=_Layer.CANDIDATE,
            evidence=evidence,
        )
    except TimeoutError as e:
        integration_failure_code = INTEGRATION_PROVIDER_TIMEOUT
        integration_failure_detail = f"provider timeout: {e}"[:200]
    except (ConnectionError, OSError) as e:
        integration_failure_code = INTEGRATION_PROVIDER_TRANSPORT_FAILURE
        integration_failure_detail = f"transport failure: {e}"[:200]
    except TypeError as e:
        # Vendor raises TypeError on non-string ModelClient response;
        # Hokom converts to typed integration DEFER rather than
        # letting the raw exception cross the adapter boundary.
        integration_failure_code = INTEGRATION_PROVIDER_MALFORMED_RESPONSE
        integration_failure_detail = f"malformed provider response: {e}"[:200]

    # Fingerprint the response if available (via the client's call log
    # when present; otherwise from the native audited answer).
    call_log = getattr(model_client, "call_log", None)
    if call_log and len(call_log) > 0:
        last = call_log[-1]
        response = getattr(last, "response", None)
        if response is not None:
            response_fp = _fingerprint(response)

    if native_verdict is not None:
        # Empty-string response is deterministic but semantically empty —
        # audit still completes with vendor's own decision; do NOT
        # override the vendor verdict here.
        accepted = (
            native_verdict.gate_state is _TransitionState.APPROVED
            and native_verdict.successor is not None
        )
        residual_ids = tuple(
            f"{r.kind.value}:{r.name}" for r in native_verdict.residuals
        )
        trace_ids = (
            native_verdict.trace_anchor,
            *native_verdict.evidence_refs,
        )
        # Certificate policy re-asserted at the Hokom seam.
        certificate_allowed = False
        # Reasonableness status: vendor default is NOT_RUN (this
        # adapter does not currently invoke audit_with_reasonableness).
        reasonableness_status = str(
            getattr(native_verdict.reasonableness_status, "value",
                    native_verdict.reasonableness_status)
        )
    else:
        # Integration failure — no native verdict. Construct a marker
        # residual set so downstream artifacts can detect the failure
        # without introspecting the enum. No certificate allowed
        # regardless of failure mode.
        accepted = False
        residual_ids = (f"INTEGRATION_MARKER:{integration_failure_code}",)
        trace_ids = (predecessor_trace,)
        certificate_allowed = False
        reasonableness_status = "NOT_RUN"

    return AnswerAuditOutcome(
        span_id=span_id,
        predecessor_trace=predecessor_trace,
        prompt_fingerprint=prompt_fp,
        response_fingerprint=response_fp,
        native_verdict=native_verdict,
        integration_failure_code=integration_failure_code,
        integration_failure_detail=integration_failure_detail,
        accepted=accepted,
        reasonableness_status=reasonableness_status,
        certificate_allowed=certificate_allowed,
        trace_ids=trace_ids,
        residual_ids=residual_ids,
    )


__all__ = [
    "_VENDOR_AUDIT_AVAILABLE",
    "_VENDOR_SHA",
    "AnswerAuditOutcome",
    "audit_bridge_verdict",
    "INTEGRATION_PROVIDER_TIMEOUT",
    "INTEGRATION_PROVIDER_TRANSPORT_FAILURE",
    "INTEGRATION_PROVIDER_MALFORMED_RESPONSE",
    "INTEGRATION_PROVIDER_EMPTY_RESPONSE",
    "INTEGRATION_PROVIDER_EXCEPTION_UNEXPECTED",
]
