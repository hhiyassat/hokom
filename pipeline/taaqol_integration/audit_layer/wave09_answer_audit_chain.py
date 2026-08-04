"""Wave09 real 5-span AnswerAudit vertical execution.

Extends Wave07's typed downstream chain (which already reaches
`AuditedTanzilBridgeVerdict`) with the native `AnswerAudit` engine
call. Every audit invocation:

* receives its span's ACTUAL `AuditedTanzilBridgeVerdict` predecessor
  (never a fixture);
* uses a deterministic `ModelClient` that returns a per-span
  fingerprint-derived response (no live provider);
* records the full outcome (predecessor trace, prompt/response
  fingerprints, native verdict fields, certificate policy) for the
  Wave09 evidence artifact.

The chain is a THIN bridge — no semantic decision is made in Hokom.
"""
from __future__ import annotations

import hashlib
from typing import Any

from pipeline.taaqol_integration.audit_layer.answer_audit_adapter import (
    _VENDOR_AUDIT_AVAILABLE,
    audit_bridge_verdict,
)
from pipeline.taaqol_integration.audit_layer.deterministic_model_client import (
    DeterministicModelClient,
)


def _prompt_for_span(span_id: str, atb_trace_ref: str) -> str:
    """Deterministic Hokom-owned integration prompt for a span.

    Encodes the span_id and the predecessor trace ref only — never the
    raw Quranic surface. The prompt is opaque data at the docs/01
    boundary; the vendor's audit judges the claim graph, not the prompt.
    """
    return (
        f"hokom.integration.answer_audit\n"
        f"span_id={span_id}\n"
        f"predecessor_trace={atb_trace_ref}\n"
    )


def _deterministic_response_for(span_id: str) -> str:
    """Deterministic response text derived from span_id.

    The response is opaque bytes; vendor audit does not read it as
    semantic content. Using span_id as the entropy source ensures
    two identical runs produce identical response fingerprints.
    """
    h = hashlib.sha256(f"wave09.deterministic.{span_id}".encode()).hexdigest()
    return f"integration:deterministic:{h[:16]}"


def _record_from_outcome(outcome, span_id: str) -> dict:
    """Serialise a Hokom AnswerAuditOutcome for the per-span artifact.

    All fields are JSON-serialisable primitives; enum values are
    converted via .value. No native object crosses the artifact
    boundary.
    """
    native = outcome.native_verdict
    return {
        "span_id": span_id,
        "predecessor_type": "AuditedTanzilBridgeVerdict",
        "predecessor_trace": outcome.predecessor_trace,
        "prompt_fingerprint": outcome.prompt_fingerprint,
        "response_fingerprint": outcome.response_fingerprint,
        "native_result_type": (
            type(native).__name__ if native is not None else "NoneType"
        ),
        "gamma_state": (
            native.gamma_state.value if native is not None else None
        ),
        "gate_state": (
            native.gate_state.value if native is not None else None
        ),
        "gamma_result": (
            native.gamma_state.value if native is not None else None
        ),
        "gate_result": (
            native.gate_state.value if native is not None else None
        ),
        "verdict_state": (
            native.gate_state.value if native is not None else "REFUSED"
        ),
        "failure_code": (
            (native.failure_code.value if native.failure_code is not None
             else None)
            if native is not None else outcome.integration_failure_code
        ),
        "rank": (
            native.rank.name if native is not None else "ZERO"
        ),
        "successor_present": (
            native is not None and native.successor is not None
        ),
        "certificate_allowed": outcome.certificate_allowed,
        "reasonableness_status": outcome.reasonableness_status,
        "trace_ids": list(outcome.trace_ids),
        "residual_ids": list(outcome.residual_ids),
        "integration_failure_code": outcome.integration_failure_code,
        "integration_failure_detail": outcome.integration_failure_detail,
        "accepted": outcome.accepted,
        "output_fingerprint": hashlib.sha256(
            f"{outcome.prompt_fingerprint}|{outcome.response_fingerprint}"
            f"|{outcome.accepted}|{outcome.certificate_allowed}".encode()
        ).hexdigest(),
    }


def execute_wave09_answer_audit_chain(
    cu_map: dict,
    source_derived_spans: list[dict],
    speech_force=None,
) -> dict:
    """Run the Wave06 chain plus a native AnswerAudit call per span.

    Returns a dict with:
    * ``vendor_available`` — bool
    * ``wave06_result`` — the raw Wave06 result (unchanged)
    * ``answer_audit_per_span`` — list of per-span dicts
    * ``counters`` — AnswerAudit-specific counters (see below)

    Counters (see §F integrity):
    * ``answer_audit_native_call_count``
    * ``answer_audit_success_count``
    * ``answer_audit_integration_failure_count``
    * ``answer_audit_predecessor_present_count``
    * ``answer_audit_predecessor_absent_count`` (span had no
      audited_tanzil_bridge_accept)
    """
    from pipeline.taaqol_integration.evidence_producers.wave06_downstream_chain_typed import (
        execute_ayat_full_downstream_chain_typed,
    )
    from pipeline.taaqol_integration.weight_layer.typed_stage_builders import (
        build_audited_tanzil_bridge_outcome, build_hukm_outcome,
        build_manat_outcome, build_tanzil_outcome,
        _VENDOR_AVAILABLE,
    )
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate,
    )
    from pipeline.taaqol_integration.evidence_producers.wave04_ifadah_chain import (
        build_formal_style_verdict,
    )
    from pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter import (
        build_mufrad_semantic_slot, build_maqam_context,
        build_dalalah_candidate, build_mufrad_dalalah_closure,
        build_relation_closure,
    )

    counters = {
        "answer_audit_native_call_count": 0,
        "answer_audit_success_count": 0,
        "answer_audit_integration_failure_count": 0,
        "answer_audit_predecessor_present_count": 0,
        "answer_audit_predecessor_absent_count": 0,
        "answer_audit_certificate_allowed_count": 0,  # must remain 0
    }
    per_span: list[dict] = []
    result = {
        "vendor_available": _VENDOR_AVAILABLE and _VENDOR_AUDIT_AVAILABLE,
        "counters": counters,
        "answer_audit_per_span": per_span,
    }
    if not result["vendor_available"]:
        return result

    # Re-drive the wave06 chain from scratch here so we can obtain the
    # ACTUAL AuditedTanzilBridgeVerdict native object per span (the
    # wave06 dict only carries stringified fields).
    from taaqqul_slot_geometry.weight.ifadah_candidate import SpeechForceKind
    from taaqqul_slot_geometry.weight.hukm_candidate import EvaluationDomain
    from taaqqul_slot_geometry.weight.manat_candidate import ManatMode
    if speech_force is None:
        speech_force = SpeechForceKind.KHABAR
    eval_domain = EvaluationDomain.LINGUISTIC

    _cache: dict = {}

    def _upto_mc(tid: str):
        if tid in _cache:
            return _cache[tid]
        entry = cu_map.get(tid)
        if entry is None:
            _cache[tid] = (None, None, None); return _cache[tid]
        try:
            fs = build_formal_style_verdict(tid)
            if fs.verdict_state.value != "PROVEN":
                _cache[tid] = (None, None, None); return _cache[tid]
            ms = build_mufrad_semantic_slot(tid, entry, fs.candidate)
            if ms.verdict_state.value != "PROVEN":
                _cache[tid] = (None, None, None); return _cache[tid]
            mq = build_maqam_context(tid, ms)
            if mq.verdict_state.value != "PROVEN":
                _cache[tid] = (None, None, None); return _cache[tid]
            dal = build_dalalah_candidate(tid, ms, mq)
            if dal.verdict_state.value != "PROVEN":
                _cache[tid] = (None, None, None); return _cache[tid]
            mc = build_mufrad_dalalah_closure(tid, ms, mq, dal)
            _cache[tid] = (mc, fs, mq); return _cache[tid]
        except Exception:  # noqa: BLE001
            _cache[tid] = (None, None, None); return _cache[tid]

    for span in source_derived_spans:
        member_ids = span.get("member_token_ids") or []
        cu_members = [tid for tid in member_ids if tid in cu_map]
        if len(cu_members) < 2:
            continue
        gov, dep = cu_members[0], cu_members[-1]
        mc_g, fs_g, mq_g = _upto_mc(gov)
        mc_d, _, _ = _upto_mc(dep)
        if mc_g is None or mc_d is None:
            continue
        if mc_g.verdict_state.value != "PROVEN" \
                or mc_d.verdict_state.value != "PROVEN":
            continue

        span_id = span.get("span_id")
        try:
            rc = build_relation_closure(
                span_id, gov, dep, mc_g, mc_d,
                relation_maqam=mq_g.trace_ref,
            )
        except Exception:  # noqa: BLE001
            continue
        if rc.verdict_state.value != "PROVEN":
            continue

        ifv = build_ifadah_candidate(
            relation_closure_verdict=rc,
            formal_style_verdict=fs_g, ifadah_maqam_verdict=mq_g,
            speech_force=speech_force,
            ifadah_evidence=f"ayat-ifadah:{span_id}",
            closure_scope=f"ayat-scope:{span_id}",
        )
        if ifv is None:
            continue

        hukm = build_hukm_outcome(
            ifadah_verdict=ifv, evaluation_domain=eval_domain,
            hukm_claim=f"ayat-hukm-claim:{span_id}",
            hukm_evidence=f"ayat-hukm-evidence:{span_id}",
            hukm_maqam=mq_g.trace_ref,
            closure_scope=f"ayat-hukm-scope:{span_id}",
        )
        if hukm is None or not hukm.accepted:
            counters["answer_audit_predecessor_absent_count"] += 1
            continue

        mv = build_manat_outcome(
            hukm_verdict=hukm.native_verdict,
            manat_mode=ManatMode.TAHQIQ_READINESS_ONLY,
            manat_description=f"ayat-manat-desc:{span_id}",
            effective_attribute_candidate=(
                f"ayat-effective-attribute:{gov}"
            ),
            conditions=(), preventers=(),
            manat_evidence=f"ayat-manat-ev:{span_id}",
            manat_domain="lughawi",
            closure_scope=f"ayat-manat-scope:{span_id}",
        )
        if mv is None or not mv.accepted:
            counters["answer_audit_predecessor_absent_count"] += 1
            continue

        tv = build_tanzil_outcome(
            hukm_verdict=hukm.native_verdict,
            manat_verdict=mv.native_verdict,
            reality_evidence=f"ayat-tanzil-reality:{span_id}",
            instance_descriptor=f"ayat-tanzil-instance:{span_id}",
            tanzil_scope=f"ayat-tanzil-scope:{span_id}",
            presentation_warning="CANDIDATE",
            not_execution_marker=True,
        )
        if tv is None or not tv.accepted:
            counters["answer_audit_predecessor_absent_count"] += 1
            continue

        atb = build_audited_tanzil_bridge_outcome(
            tanzil_verdict=tv.native_verdict,
        )
        if atb is None or not atb.accepted:
            counters["answer_audit_predecessor_absent_count"] += 1
            continue

        # We now hold the real AuditedTanzilBridgeVerdict — feed to
        # the AnswerAudit adapter with a deterministic ModelClient.
        counters["answer_audit_predecessor_present_count"] += 1
        atb_native = atb.native_verdict
        atb_trace = (
            atb_native.trace_ref if isinstance(atb_native.trace_ref, str)
            else ""
        )
        prompt = _prompt_for_span(span_id, atb_trace)
        model_client = DeterministicModelClient(
            default_response=_deterministic_response_for(span_id),
        )
        outcome = audit_bridge_verdict(
            audited_tanzil_verdict=atb_native,
            span_id=span_id,
            prompt=prompt,
            model_client=model_client,
        )
        counters["answer_audit_native_call_count"] += 1
        if outcome.native_verdict is not None:
            counters["answer_audit_success_count"] += 1
        if outcome.integration_failure_code is not None:
            counters["answer_audit_integration_failure_count"] += 1
        if outcome.certificate_allowed:
            # Constitutional invariant — must remain 0.
            counters["answer_audit_certificate_allowed_count"] += 1

        per_span.append(_record_from_outcome(outcome, span_id))

    return result


__all__ = [
    "execute_wave09_answer_audit_chain",
    "_prompt_for_span",
    "_deterministic_response_for",
]
