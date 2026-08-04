"""C13 Wave04 — native Ifadah chain runner.

Consumes the same Wave03 predecessor stages (FormalStyle, MufradSemanticSlot,
MaqamContext, Dalalah, MufradDalalahClosure, RelationClosure) but preserves
the FormalStyleVerdict as a first-class object so it can be passed to the
native `prove_ifadah_candidate` at PR-20.

The existing `vertical_chain_adapter.build_formal_style` returns the
CANDIDATE (unwrapped). Ifadah's boundary type guard requires the VERDICT
type itself. This module adds a verdict-preserving projection and wires
the full Wave03 → Ifadah chain per docs/41 (PR-D5 Ifadah Boundary Law).

Constitutional invariants preserved:
  - No verdicts are fabricated by Hokom (every verdict is a return value
    from a native vendor callable).
  - No SpeechForceKind is derived from form, maqam, or relation alone
    (docs/41 §15). It is supplied by the caller — this runner uses
    KHABAR (declarative style) which matches the Wave03 formal style
    setup (DECLARATIVE_STYLE_FORM).
  - IfadahCandidate is a speech-level closure candidate, never meaning,
    never hukm, never truth.
"""
from __future__ import annotations
from typing import Any, Optional

from .vertical_chain_adapter import (
    build_mufrad_semantic_slot,
    build_maqam_context,
    build_dalalah_candidate,
    build_mufrad_dalalah_closure,
    build_relation_closure,
)


def build_formal_style_verdict(token_id: str) -> Any:
    """Verdict-preserving variant of build_formal_style.

    Returns the full FormalStyleVerdict object (not just .candidate).
    The Ifadah adapter's boundary type guard requires FormalStyleVerdict.
    """
    from taaqqul_slot_geometry.weight.formal_style_candidate import (
        prove_formal_style_candidate, FormalStyleFamily,
    )
    from taaqqul_slot_geometry.weight.formal_shape import FormalShapeClosureState
    return prove_formal_style_candidate(
        style_family=FormalStyleFamily.DECLARATIVE_STYLE_FORM,
        composition_evidence_ref=f"ayat-composition:{token_id}",
        formal_closure_state=FormalShapeClosureState.CLOSED,
        formal_closure_ref="formal_shape_registry/word_class_domain/CLOSED",
    )


def execute_ayat_ifadah_chain(
    cu_map: dict,
    source_derived_spans: list[dict],
    speech_force: Optional[Any] = None,
) -> dict:
    """Run the full Wave03 + Ifadah chain over source-derived Ayat spans.

    Parameters
    ──────────
    cu_map              : token_id → cu_entry dict, from Wave03 setup
    source_derived_spans: list of span dicts with member_token_ids
    speech_force        : optional SpeechForceKind. Defaults to KHABAR
                          (declarative) which matches the Wave03 setup.

    Returns
    ───────
    Dict with per-stage counts including:
      formal_style_verdict_calls / _proven
      mufrad_semantic_slot_calls / _proven
      maqam_context_calls / _proven
      dalalah_candidate_calls / _proven
      mufrad_dalalah_closure_calls / _proven
      relation_closure_calls / _proven
      ifadah_calls / _proven / _refused / _adapter_returned_none
      ayat_ifadah_executed
      per_span_ifadah_results (list of typed per-span dicts)
    """
    # Ifadah adapter + SpeechForceKind lazy import (fail-closed on 3.10).
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate, _IFADAH_AVAILABLE,
    )

    if speech_force is None and _IFADAH_AVAILABLE:
        from taaqqul_slot_geometry.weight.ifadah_candidate import SpeechForceKind
        speech_force = SpeechForceKind.KHABAR

    result = {
        'formal_style_verdict_calls': 0, 'formal_style_verdict_proven': 0,
        'mufrad_semantic_slot_calls': 0, 'ms_verdicts_proven': 0,
        'maqam_context_calls': 0, 'maqam_verdicts_proven': 0,
        'dalalah_candidate_calls': 0, 'dalalah_verdicts_proven': 0,
        'mufrad_dalalah_closure_calls': 0, 'mufrad_dalalah_closure_verdicts_proven': 0,
        'relation_closure_calls': 0, 'relation_closure_verdicts_proven': 0,
        'ifadah_calls': 0,
        'ifadah_proven': 0,
        'ifadah_adapter_returned_none': 0,
        'ayat_ifadah_executed': 0,
        'per_span_ifadah_results': [],
        'ifadah_available': _IFADAH_AVAILABLE,
    }
    if not cu_map or not source_derived_spans:
        return result
    if not _IFADAH_AVAILABLE:
        # Python 3.10 or vendor missing — fail-closed per adapter contract.
        return result

    # Per-token chain up to MufradDalalahClosure — memoize verdicts so a
    # span with two tokens reuses shared computation.
    _mc_cache: dict[str, tuple] = {}

    def _run_up_to_mufrad_closure(tid: str):
        """Returns (mc_verdict, formal_style_verdict, maqam_verdict)
        or (None, None, None) on any refusal."""
        if tid in _mc_cache:
            return _mc_cache[tid]
        entry = cu_map.get(tid)
        if entry is None:
            _mc_cache[tid] = (None, None, None)
            return _mc_cache[tid]
        try:
            fs_verdict = build_formal_style_verdict(tid)
            result['formal_style_verdict_calls'] += 1
            if fs_verdict.verdict_state.value != "PROVEN":
                _mc_cache[tid] = (None, None, None)
                return _mc_cache[tid]
            result['formal_style_verdict_proven'] += 1
            ms = build_mufrad_semantic_slot(tid, entry, fs_verdict.candidate)
            result['mufrad_semantic_slot_calls'] += 1
            if ms.verdict_state.value != "PROVEN":
                _mc_cache[tid] = (None, None, None)
                return _mc_cache[tid]
            result['ms_verdicts_proven'] += 1
            maqam = build_maqam_context(tid, ms)
            result['maqam_context_calls'] += 1
            if maqam.verdict_state.value != "PROVEN":
                _mc_cache[tid] = (None, None, None)
                return _mc_cache[tid]
            result['maqam_verdicts_proven'] += 1
            dal = build_dalalah_candidate(tid, ms, maqam)
            result['dalalah_candidate_calls'] += 1
            if dal.verdict_state.value != "PROVEN":
                _mc_cache[tid] = (None, None, None)
                return _mc_cache[tid]
            result['dalalah_verdicts_proven'] += 1
            mc = build_mufrad_dalalah_closure(tid, ms, maqam, dal)
            result['mufrad_dalalah_closure_calls'] += 1
            if mc.verdict_state.value == "PROVEN":
                result['mufrad_dalalah_closure_verdicts_proven'] += 1
            _mc_cache[tid] = (mc, fs_verdict, maqam)
            return _mc_cache[tid]
        except Exception:  # noqa: BLE001 — fail-closed per adapter contract
            _mc_cache[tid] = (None, None, None)
            return _mc_cache[tid]

    for span in source_derived_spans:
        member_ids = span.get('member_token_ids') or []
        cu_members = [tid for tid in member_ids if tid in cu_map]
        if len(cu_members) < 2:
            continue
        gov_id = cu_members[0]
        dep_id = cu_members[-1]
        mc_gov, fs_gov, maqam_gov = _run_up_to_mufrad_closure(gov_id)
        mc_dep, fs_dep, maqam_dep = _run_up_to_mufrad_closure(dep_id)
        if mc_gov is None or mc_dep is None:
            continue
        if mc_gov.verdict_state.value != "PROVEN" \
                or mc_dep.verdict_state.value != "PROVEN":
            continue

        # RelationClosure over the two mufrad-dalalah closures.
        # docs/41 §6: the RelationClosure's `relation_maqam` must equal
        # the trace_ref of the maqam verdict later passed to Ifadah.
        # We use the governor's maqam trace_ref as the shared anchor.
        try:
            rc = build_relation_closure(
                span.get('span_id'), gov_id, dep_id, mc_gov, mc_dep,
                relation_maqam=maqam_gov.trace_ref,
            )
            result['relation_closure_calls'] += 1
        except Exception:  # noqa: BLE001
            continue
        if rc.verdict_state.value != "PROVEN":
            result['per_span_ifadah_results'].append({
                'span_id': span.get('span_id'),
                'stage': 'relation_closure',
                'verdict_state': rc.verdict_state.value,
            })
            continue
        result['relation_closure_verdicts_proven'] += 1

        # PR-20: Ifadah requires 3 parallel PROVEN verdicts + speech_force.
        # Use the GOVERNOR's formal_style_verdict and maqam_verdict, since
        # the docs/41 requires the SINGLE shared maqam verdict. In this
        # setup the governor's stage results are the primary anchor.
        result['ifadah_calls'] += 1
        ifadah_verdict = build_ifadah_candidate(
            relation_closure_verdict=rc,
            formal_style_verdict=fs_gov,
            ifadah_maqam_verdict=maqam_gov,
            speech_force=speech_force,
            ifadah_evidence=(
                f"ayat-ifadah-evidence:{span.get('span_id')}:"
                f"{gov_id}->{dep_id}"
            ),
            closure_scope=f"ayat-closure-scope:{span.get('span_id')}",
        )
        if ifadah_verdict is None:
            result['ifadah_adapter_returned_none'] += 1
            result['per_span_ifadah_results'].append({
                'span_id': span.get('span_id'),
                'stage': 'ifadah_adapter_returned_none',
                'gov_id': gov_id, 'dep_id': dep_id,
            })
            continue

        result['ifadah_proven'] += 1
        result['ayat_ifadah_executed'] += 1
        result['per_span_ifadah_results'].append({
            'span_id': span.get('span_id'),
            'gov_id': gov_id, 'dep_id': dep_id,
            'ifadah_state': ifadah_verdict.verdict_state.value,
            'ifadah_rank': str(ifadah_verdict.verdict_rank),
            'ifadah_trace_ref': ifadah_verdict.trace_ref,
            'ifadah_residual_count': len(ifadah_verdict.residuals),
            'verdict_type': type(ifadah_verdict).__name__,
        })

    return result


__all__ = [
    "build_formal_style_verdict",
    "execute_ayat_ifadah_chain",
]
