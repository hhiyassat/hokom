"""C13 downstream Taaqol chain — Hukm → Manat → Tanzil (vertical) plus
Mantuq → Mafhum (parallel branch), all from PROVEN Ifadah verdicts.

Runs the full downstream reasoning DAG documented in vendor CLAUDE.md
PR chain roadmap:

  Ifadah (PR-20, docs/41)
    ├── Hukm     (PR-21,  docs/43) → Manat (PR-21M, docs/44) → Tanzil (PR-22, docs/45)
    └── Mantuq   (PV-A2, docs/48) → Mafhum (PV-A4, docs/50)

Every downstream verdict is a native vendor dataclass — no Hokom-side
verdict construction. The chain preserves the FormalStyle / Maqam /
RelationClosure trace anchors for docs/41-45 single-shared-maqam
enforcement.
"""
from __future__ import annotations
from typing import Any, Optional

from .wave04_ifadah_chain import execute_ayat_ifadah_chain


def execute_ayat_full_downstream_chain(
    cu_map: dict,
    source_derived_spans: list[dict],
    speech_force: Optional[Any] = None,
) -> dict:
    """Run the Ayat vertical through Ifadah → Hukm → Manat → Tanzil AND
    the parallel Mantuq → Mafhum branch.

    Returns per-stage counts, per-span vertical trace, and typed
    residual accounting. Fail-open: any stage returning None short-
    circuits the per-span downstream while other spans continue.
    """
    from pipeline.taaqol_integration.weight_layer.hukm_candidate_adapter import (
        build_hukm_candidate, _HUKM_AVAILABLE,
    )
    from pipeline.taaqol_integration.weight_layer.manat_candidate_adapter import (
        build_manat_candidate, _MANAT_AVAILABLE,
    )
    from pipeline.taaqol_integration.weight_layer.tanzil_candidate_adapter import (
        build_tanzil_candidate, _TANZIL_AVAILABLE,
    )
    from pipeline.taaqol_integration.weight_layer.mantuq_closure_adapter import (
        build_mantuq_closure, _MANTUQ_AVAILABLE,
    )
    from pipeline.taaqol_integration.weight_layer.mafhum_closure_adapter import (
        build_mafhum_closure, _MAFHUM_AVAILABLE,
    )

    # Re-run the Wave04 chain — the ifadah result includes per-span
    # verdicts. We need to preserve the (rc, fs, maqam) triples to build
    # Hukm etc.; but wave04_ifadah_chain currently only returns summary
    # dicts. For a full downstream run we re-execute inside this module
    # with a memoization-aware loop.

    from .wave04_ifadah_chain import build_formal_style_verdict
    from .vertical_chain_adapter import (
        build_mufrad_semantic_slot, build_maqam_context,
        build_dalalah_candidate, build_mufrad_dalalah_closure,
        build_relation_closure,
    )
    from pipeline.taaqol_integration.weight_layer.ifadah_candidate_adapter import (
        build_ifadah_candidate, _IFADAH_AVAILABLE,
    )

    if speech_force is None and _IFADAH_AVAILABLE:
        from taaqqul_slot_geometry.weight.ifadah_candidate import SpeechForceKind
        speech_force = SpeechForceKind.KHABAR

    # Evaluation domain for Hukm — LINGUISTIC is the only domain that
    # matches the current vertical's constitutional scope (Ayat corpus
    # under lughawi discourse). LOGICAL and NORMATIVE_CANDIDATE would
    # require external evidence.
    _evaluation_domain = None
    if _HUKM_AVAILABLE:
        from taaqqul_slot_geometry.weight.hukm_candidate import EvaluationDomain
        _evaluation_domain = EvaluationDomain.LINGUISTIC

    result = {
        'ifadah_proven': 0,
        'hukm_available': _HUKM_AVAILABLE,
        'hukm_calls': 0, 'hukm_proven': 0,
        'manat_available': _MANAT_AVAILABLE,
        'manat_calls': 0, 'manat_proven': 0,
        'tanzil_available': _TANZIL_AVAILABLE,
        'tanzil_calls': 0, 'tanzil_proven': 0,
        'mantuq_available': _MANTUQ_AVAILABLE,
        'mantuq_calls': 0, 'mantuq_proven': 0,
        'mafhum_available': _MAFHUM_AVAILABLE,
        'mafhum_calls': 0, 'mafhum_proven': 0,
        'last_reached_stage_per_span': [],
        'per_span_downstream': [],
    }

    if not (_IFADAH_AVAILABLE and _HUKM_AVAILABLE and _MANAT_AVAILABLE
             and _TANZIL_AVAILABLE and _MANTUQ_AVAILABLE and _MAFHUM_AVAILABLE):
        return result

    _cache: dict[str, tuple] = {}

    def _upto_mufrad_closure(tid: str):
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
            _cache[tid] = (mc, fs, mq)
            return _cache[tid]
        except Exception:  # noqa: BLE001
            _cache[tid] = (None, None, None); return _cache[tid]

    for span in source_derived_spans:
        member_ids = span.get('member_token_ids') or []
        cu_members = [tid for tid in member_ids if tid in cu_map]
        if len(cu_members) < 2:
            continue
        gov, dep = cu_members[0], cu_members[-1]
        mc_g, fs_g, mq_g = _upto_mufrad_closure(gov)
        mc_d, _fs_d, _mq_d = _upto_mufrad_closure(dep)
        if mc_g is None or mc_d is None:
            continue
        if mc_g.verdict_state.value != "PROVEN" \
                or mc_d.verdict_state.value != "PROVEN":
            continue

        span_id = span.get('span_id')
        span_record = {'span_id': span_id, 'stages': []}

        # RelationClosure with shared-maqam anchor
        try:
            rc = build_relation_closure(
                span_id, gov, dep, mc_g, mc_d,
                relation_maqam=mq_g.trace_ref,
            )
        except Exception:  # noqa: BLE001
            continue
        if rc.verdict_state.value != "PROVEN":
            result['last_reached_stage_per_span'].append('relation_closure_refused')
            span_record['stages'].append(('relation_closure', 'REFUSED'))
            result['per_span_downstream'].append(span_record)
            continue
        span_record['stages'].append(('relation_closure', 'PROVEN'))

        # Ifadah
        ifv = build_ifadah_candidate(
            relation_closure_verdict=rc,
            formal_style_verdict=fs_g, ifadah_maqam_verdict=mq_g,
            speech_force=speech_force,
            ifadah_evidence=f"ayat-ifadah:{span_id}",
            closure_scope=f"ayat-scope:{span_id}",
        )
        if ifv is None:
            result['last_reached_stage_per_span'].append('ifadah_refused')
            span_record['stages'].append(('ifadah', 'REFUSED'))
            result['per_span_downstream'].append(span_record)
            continue
        result['ifadah_proven'] += 1
        span_record['stages'].append(('ifadah', 'PROVEN'))

        # ── Vertical branch: Hukm → Manat → Tanzil ──────────────────
        result['hukm_calls'] += 1
        hukm_maqam = mq_g.trace_ref
        hv = build_hukm_candidate(
            ifadah_verdict=ifv, evaluation_domain=_evaluation_domain,
            hukm_claim=f"ayat-hukm-claim:{span_id}",
            hukm_evidence=f"ayat-hukm-evidence:{span_id}",
            hukm_maqam=hukm_maqam,
            closure_scope=f"ayat-hukm-scope:{span_id}",
        )
        if hv is None:
            result['last_reached_stage_per_span'].append('hukm_refused')
            span_record['stages'].append(('hukm', 'REFUSED'))
        else:
            result['hukm_proven'] += 1
            span_record['stages'].append(('hukm', 'PROVEN'))

            # Manat: requires HukmVerdict + manat inputs
            result['manat_calls'] += 1
            mv = _try_build_manat(build_manat_candidate, hv, span_id,
                                  hukm_maqam, gov)
            if mv is None:
                result['last_reached_stage_per_span'].append('manat_refused')
                span_record['stages'].append(('manat', 'REFUSED'))
            else:
                result['manat_proven'] += 1
                span_record['stages'].append(('manat', 'PROVEN'))
                # Tanzil — takes both HukmVerdict and ManatVerdict
                result['tanzil_calls'] += 1
                tv = _try_build_tanzil(build_tanzil_candidate, hv, mv, span_id)
                if tv is None:
                    result['last_reached_stage_per_span'].append('tanzil_refused')
                    span_record['stages'].append(('tanzil', 'REFUSED'))
                else:
                    result['tanzil_proven'] += 1
                    span_record['stages'].append(('tanzil', 'PROVEN'))
                    result['last_reached_stage_per_span'].append('tanzil_proven')

        # ── Parallel branch: Mantuq → Mafhum ────────────────────────
        result['mantuq_calls'] += 1
        mtv = _try_build_mantuq(build_mantuq_closure, ifv, mq_g, span_id)
        if mtv is None:
            span_record['stages'].append(('mantuq', 'REFUSED'))
        else:
            result['mantuq_proven'] += 1
            span_record['stages'].append(('mantuq', 'PROVEN'))
            result['mafhum_calls'] += 1
            mfv = _try_build_mafhum(build_mafhum_closure, mtv, span_id)
            if mfv is None:
                span_record['stages'].append(('mafhum', 'REFUSED'))
            else:
                result['mafhum_proven'] += 1
                span_record['stages'].append(('mafhum', 'PROVEN'))

        result['per_span_downstream'].append(span_record)

    return result


# ── Per-stage builders (encapsulate constructor kwargs so the main loop
#    stays readable). Each returns the vendor verdict or None. ──────────

def _try_build_manat(builder, hukm_verdict, span_id: str,
                     hukm_maqam: str, gov_token_id: str) -> Optional[Any]:
    from taaqqul_slot_geometry.weight.manat_candidate import ManatMode
    try:
        return builder(
            hukm_verdict=hukm_verdict,
            manat_mode=ManatMode.TAHQIQ_READINESS_ONLY,
            manat_description=f"ayat-manat-desc:{span_id}",
            effective_attribute_candidate=(
                f"ayat-effective-attribute:{gov_token_id}"
            ),
            conditions=(),
            preventers=(),
            manat_evidence=f"ayat-manat-ev:{span_id}",
            manat_domain="lughawi",
            closure_scope=f"ayat-manat-scope:{span_id}",
        )
    except Exception:  # noqa: BLE001
        return None


def _try_build_tanzil(builder, hukm_verdict, manat_verdict,
                      span_id: str) -> Optional[Any]:
    try:
        return builder(
            hukm_verdict=hukm_verdict,
            manat_verdict=manat_verdict,
            reality_evidence=f"ayat-tanzil-reality:{span_id}",
            instance_descriptor=f"ayat-tanzil-instance:{span_id}",
            tanzil_scope=f"ayat-tanzil-scope:{span_id}",
            presentation_warning="CANDIDATE",
            not_execution_marker=True,
        )
    except Exception:  # noqa: BLE001
        return None


def _try_build_mantuq(builder, ifadah_verdict, maqam_verdict,
                      span_id: str) -> Optional[Any]:
    try:
        return builder(
            ifadah_verdict=ifadah_verdict,
            maqam_verdict=maqam_verdict,
            mantuq_scope=f"ayat-mantuq-scope:{span_id}",
            spoken_surface_ref=f"ayat-spoken:{span_id}",
            mantuq_evidence=f"ayat-mantuq-ev:{span_id}",
            closure_scope=f"ayat-mantuq-scope-close:{span_id}",
        )
    except Exception:  # noqa: BLE001
        return None


def _try_build_mafhum(builder, mantuq_verdict, span_id: str) -> Optional[Any]:
    from taaqqul_slot_geometry.weight.mafhum_closure import MafhumBranchType
    try:
        return builder(
            mantuq_verdict=mantuq_verdict,
            outside_boundary=f"ayat-mafhum-boundary:{span_id}",
            branch_type=MafhumBranchType.MUWAFAQAH,
            branch_subtype="",
            qayd=f"ayat-mafhum-qayd:{span_id}",
            source_domain="lughawi",
            cross_domain_transfer="",
            # mantuq_blocks=False: we have a valid qayd + branch_type, so
            # the mafhum-from-mantuq closure is derivable. The
            # constitutional promotion ceiling (MAFHUM_RANK_CEILING) still
            # applies inside the vendor.
            mantuq_blocks=False,
            residuals=(),
        )
    except Exception:  # noqa: BLE001
        return None


__all__ = [
    "execute_ayat_full_downstream_chain",
]
