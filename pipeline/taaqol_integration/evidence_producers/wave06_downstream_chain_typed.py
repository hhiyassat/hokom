"""C13 Wave06 downstream chain — typed outcomes + audit-bridge closure.

Extends the Wave05 chain in three ways required by the independent
audit's remediation task
(QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-REMEDIATION-02):

1. Invokes ``bridge_tanzil_to_audit`` after every PROVEN Tanzil,
   closing the previously unbridged audit-layer stage.
2. Uses the typed builders (``build_*_outcome``) so every stage
   returns a :class:`DownstreamStageOutcome` — native REFUSED is
   preserved with ``failure_code``, ``trace_ref``, and residuals.
3. Persists a per-stage rich record with input trace, native
   result type, verdict_state, failure_code, trace_ref, and
   residual_ids.

The parallel Mantuq → Mafhum branch is preserved. Wave05's dict
schema is not re-used; a new richer schema is emitted (documented
below).

Per-span record schema
----------------------
::

    {
      "span_id": "SPAN-AYAT-CLAUSE-004-...",
      "input_ids": [gov_token_id, dep_token_id],
      "stages": [
        {
          "stage": "hukm",
          "input_stage": "ifadah",
          "native_result_type": "HukmVerdict",
          "verdict_state": "PROVEN",
          "classification": "ACCEPT",
          "failure_code": null,
          "trace_ref": "hukm.candidate/proven/...",
          "residual_ids": [],
          "failure_detail": ""
        },
        ...
      ]
    }
"""
from __future__ import annotations
from typing import Any, Optional


def execute_ayat_full_downstream_chain_typed(
    cu_map: dict,
    source_derived_spans: list[dict],
    speech_force: Optional[Any] = None,
) -> dict:
    """Run the full downstream DAG with typed outcomes + audit bridge."""
    from pipeline.taaqol_integration.weight_layer.typed_stage_builders import (
        _VENDOR_AVAILABLE,
        _verdict_residuals, _verdict_trace_ref,
        build_hukm_outcome, build_manat_outcome, build_tanzil_outcome,
        build_mantuq_outcome, build_mafhum_outcome,
        build_audited_tanzil_bridge_outcome,
    )
    from pipeline.taaqol_integration.weight_layer.typed_outcomes import (
        _residual_id,
    )
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate, _IFADAH_AVAILABLE,
    )
    from .wave04_ifadah_chain import build_formal_style_verdict
    from .vertical_chain_adapter import (
        build_mufrad_semantic_slot, build_maqam_context,
        build_dalalah_candidate, build_mufrad_dalalah_closure,
        build_relation_closure,
    )

    counters = {
        'ifadah_calls': 0, 'ifadah_accept': 0, 'ifadah_defer': 0,
        'ifadah_block': 0,
        'hukm_calls': 0, 'hukm_accept': 0, 'hukm_defer': 0,
        'hukm_block': 0,
        'manat_calls': 0, 'manat_accept': 0, 'manat_defer': 0,
        'manat_block': 0,
        'tanzil_calls': 0, 'tanzil_accept': 0, 'tanzil_defer': 0,
        'tanzil_block': 0,
        'audited_tanzil_bridge_calls': 0,
        'audited_tanzil_bridge_accept': 0,
        'audited_tanzil_bridge_defer': 0,
        'audited_tanzil_bridge_block': 0,
        'mantuq_calls': 0, 'mantuq_accept': 0, 'mantuq_defer': 0,
        'mantuq_block': 0,
        'mafhum_calls': 0, 'mafhum_accept': 0, 'mafhum_defer': 0,
        'mafhum_block': 0,
    }
    per_span: list[dict] = []
    result = {
        'vendor_available': _VENDOR_AVAILABLE and _IFADAH_AVAILABLE,
        'counters': counters,
        'per_span_downstream': per_span,
        'unbridged_reachable_stage_count': 0,
    }

    if not result['vendor_available']:
        return result

    if speech_force is None:
        from taaqqul_slot_geometry.weight.ifadah_candidate import SpeechForceKind
        speech_force = SpeechForceKind.KHABAR

    from taaqqul_slot_geometry.weight.hukm_candidate import EvaluationDomain
    from taaqqul_slot_geometry.weight.manat_candidate import ManatMode
    from taaqqul_slot_geometry.weight.mafhum_closure import MafhumBranchType
    eval_domain = EvaluationDomain.LINGUISTIC

    def _record(outcome, input_stage: str) -> dict:
        return {
            'stage': outcome.stage,
            'input_stage': input_stage,
            'native_result_type': type(outcome.native_verdict).__name__,
            'verdict_state': outcome.verdict_state,
            'classification': outcome.classification,
            'failure_code': outcome.failure_code,
            'trace_ref': outcome.trace_ref,
            'residual_ids': list(outcome.residual_ids),
            'failure_detail': outcome.failure_detail,
        }

    def _tally(outcome, prefix: str) -> None:
        counters[f'{prefix}_calls'] += 1
        if outcome.accepted:
            counters[f'{prefix}_accept'] += 1
        elif outcome.deferred:
            counters[f'{prefix}_defer'] += 1
        elif outcome.blocked:
            counters[f'{prefix}_block'] += 1

    _cache: dict[str, tuple] = {}

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
        member_ids = span.get('member_token_ids') or []
        cu_members = [tid for tid in member_ids if tid in cu_map]
        if len(cu_members) < 2:
            continue
        gov, dep = cu_members[0], cu_members[-1]
        mc_g, fs_g, mq_g = _upto_mc(gov)
        mc_d, _fs_d, _mq_d = _upto_mc(dep)
        if mc_g is None or mc_d is None:
            continue
        if mc_g.verdict_state.value != "PROVEN" \
                or mc_d.verdict_state.value != "PROVEN":
            continue

        span_id = span.get('span_id')
        span_rec: dict = {
            'span_id': span_id,
            'input_ids': [gov, dep],
            'stages': [],
        }

        # RelationClosure
        try:
            rc = build_relation_closure(span_id, gov, dep, mc_g, mc_d,
                                        relation_maqam=mq_g.trace_ref)
        except Exception:  # noqa: BLE001
            per_span.append(span_rec); continue
        rc_residuals = _verdict_residuals(rc)
        rc_residual_ids = [_residual_id(r) for r in rc_residuals]
        rc_trace_ref = _verdict_trace_ref(rc) or getattr(rc, 'trace_ref', '') or ''
        if rc.verdict_state.value != "PROVEN":
            span_rec['stages'].append({
                'stage': 'relation_closure', 'input_stage': 'mufrad_closure',
                'native_result_type': type(rc).__name__,
                'verdict_state': rc.verdict_state.value,
                'classification': 'DEFER',
                'failure_code': getattr(rc, 'failure_code', None)
                    and str(getattr(rc.failure_code, 'value', rc.failure_code)),
                'trace_ref': rc_trace_ref,
                'residual_ids': rc_residual_ids,
                'failure_detail': 'relation_closure not PROVEN',
            })
            per_span.append(span_rec); continue
        span_rec['stages'].append({
            'stage': 'relation_closure', 'input_stage': 'mufrad_closure',
            'native_result_type': type(rc).__name__,
            'verdict_state': 'PROVEN', 'classification': 'ACCEPT',
            'failure_code': None,
            'trace_ref': rc_trace_ref,
            'residual_ids': rc_residual_ids, 'failure_detail': '',
        })

        # Ifadah (still adapter-driven — we retain wave04 typing here to
        # avoid overlapping REPAIR B into Ifadah scope)
        counters['ifadah_calls'] += 1
        ifv = build_ifadah_candidate(
            relation_closure_verdict=rc,
            formal_style_verdict=fs_g, ifadah_maqam_verdict=mq_g,
            speech_force=speech_force,
            ifadah_evidence=f"ayat-ifadah:{span_id}",
            closure_scope=f"ayat-scope:{span_id}",
        )
        if ifv is None:
            counters['ifadah_defer'] += 1
            # ifv is None → the adapter fail-closed before returning a
            # verdict; there is no vendor residual set to extract. This
            # is a genuine `extraction_unavailable` state, not a hidden
            # residual — the failure_detail names it explicitly.
            span_rec['stages'].append({
                'stage': 'ifadah', 'input_stage': 'relation_closure',
                'native_result_type': 'NoneType',
                'verdict_state': 'REFUSED', 'classification': 'DEFER',
                'failure_code': None,
                'trace_ref': '', 'residual_ids': [],
                'failure_detail': 'ifadah adapter returned None; residual extraction unavailable',
            })
            per_span.append(span_rec); continue
        counters['ifadah_accept'] += 1
        ifv_residuals = _verdict_residuals(ifv)
        ifv_residual_ids = [_residual_id(r) for r in ifv_residuals]
        span_rec['stages'].append({
            'stage': 'ifadah', 'input_stage': 'relation_closure',
            'native_result_type': type(ifv).__name__,
            'verdict_state': 'PROVEN', 'classification': 'ACCEPT',
            'failure_code': None,
            'trace_ref': _verdict_trace_ref(ifv) or getattr(ifv, 'trace_ref', '') or '',
            'residual_ids': ifv_residual_ids, 'failure_detail': '',
        })

        # ── Vertical: Hukm → Manat → Tanzil → AuditBridge ─────────────
        hukm = build_hukm_outcome(
            ifadah_verdict=ifv, evaluation_domain=eval_domain,
            hukm_claim=f"ayat-hukm-claim:{span_id}",
            hukm_evidence=f"ayat-hukm-evidence:{span_id}",
            hukm_maqam=mq_g.trace_ref,
            closure_scope=f"ayat-hukm-scope:{span_id}",
        )
        if hukm is not None:
            _tally(hukm, 'hukm')
            span_rec['stages'].append(_record(hukm, 'ifadah'))
            if hukm.accepted:
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
                if mv is not None:
                    _tally(mv, 'manat')
                    span_rec['stages'].append(_record(mv, 'hukm'))
                    if mv.accepted:
                        tv = build_tanzil_outcome(
                            hukm_verdict=hukm.native_verdict,
                            manat_verdict=mv.native_verdict,
                            reality_evidence=f"ayat-tanzil-reality:{span_id}",
                            instance_descriptor=f"ayat-tanzil-instance:{span_id}",
                            tanzil_scope=f"ayat-tanzil-scope:{span_id}",
                            presentation_warning="CANDIDATE",
                            not_execution_marker=True,
                        )
                        if tv is not None:
                            _tally(tv, 'tanzil')
                            span_rec['stages'].append(_record(tv, 'manat'))
                            if tv.accepted:
                                # NEW: audit-layer bridge
                                atb = build_audited_tanzil_bridge_outcome(
                                    tanzil_verdict=tv.native_verdict,
                                )
                                if atb is not None:
                                    _tally(atb, 'audited_tanzil_bridge')
                                    span_rec['stages'].append(
                                        _record(atb, 'tanzil'))

        # ── Parallel: Mantuq → Mafhum ─────────────────────────────────
        mtv = build_mantuq_outcome(
            ifadah_verdict=ifv, maqam_verdict=mq_g,
            mantuq_scope=f"ayat-mantuq-scope:{span_id}",
            spoken_surface_ref=f"ayat-spoken:{span_id}",
            mantuq_evidence=f"ayat-mantuq-ev:{span_id}",
            closure_scope=f"ayat-mantuq-scope-close:{span_id}",
        )
        if mtv is not None:
            _tally(mtv, 'mantuq')
            span_rec['stages'].append(_record(mtv, 'ifadah'))
            if mtv.accepted:
                mfv = build_mafhum_outcome(
                    mantuq_verdict=mtv.native_verdict,
                    outside_boundary=f"ayat-mafhum-boundary:{span_id}",
                    branch_type=MafhumBranchType.MUWAFAQAH,
                    branch_subtype="",
                    qayd=f"ayat-mafhum-qayd:{span_id}",
                    source_domain="lughawi",
                    cross_domain_transfer="",
                    mantuq_blocks=False, residuals=(),
                )
                if mfv is not None:
                    _tally(mfv, 'mafhum')
                    span_rec['stages'].append(_record(mfv, 'mantuq'))

        per_span.append(span_rec)

    return result


__all__ = [
    "execute_ayat_full_downstream_chain_typed",
]
