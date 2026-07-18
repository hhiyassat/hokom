#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_mushtaqat/phase4d_orchestrator.py — منسّق Phase 4D (MushtaqProjection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

الدالة العامة: project_mushtaqat_with_licensing()

مسارات المشتق (source_path):
  partial_accept  — بعض المشتقات مقبولة وبعضها مؤجل.
  full_accept     — جميع المشتقات المحسوبة مقبولة.
  deferred        — لا مقبولات، بعضها مؤجل.
  blocked         — تناقض من Phase4B (BLOCK).
  not_opened      — Phase4A لم يقبل.
  not_applicable  — وزن اسمي لا فعلي.

الأمان:
  - لا استيراد لمحركات خارجية.
  - لا تعديل على canonical_root أو selected_wazn.
  - لا توليد مصادر أو تصريف.
  - Phase4C هو سياق فقط — لا يُبوّب هنا.
"""

from __future__ import annotations

from pipeline.p4_bab.phase4b_orchestrator import deduplicate_residuals, _partition_residuals
from pipeline.p4_mushtaqat.models import Phase4DResult
from pipeline.p4_mushtaqat.mushtaq_projection import project_mushtaqat


def project_mushtaqat_with_licensing(
    phase4a_result,
    phase4b_result=None,
    phase4c_result=None,
    root_refinement=None,
) -> Phase4DResult:
    """
    أنتِج Phase4DResult من Phase4AResult و Phase4BResult/C (الاختيارية).

    Args:
        phase4a_result : Phase4AResult — مطلوب.
        phase4b_result : Phase4BResult | None — اختياري.
        phase4c_result : Phase4CResult | None — للسياق (لا يُبوّب).
        root_refinement: RootRefinement | None — مُرسَل من الأنبوب (لا يُعدَّل هنا).

    Returns:
        Phase4DResult

    Security:
        - لا استيراد لمحركات خارجية.
        - لا يعدّل canonical_root أو selected_wazn.
        - لا يُنتِج مصادر (masdar generation).
        - لا يُنتِج تصريف (paradigm).
    """
    # ── الحكم الابتدائي من Phase4C ─────────────────────────────────────────
    if phase4c_result is not None:
        initial_masdar_directive = getattr(phase4c_result, 'final_directive', 'UNKNOWN')
    else:
        initial_masdar_directive = 'SKIP'

    # ── جمع الشواهد ────────────────────────────────────────────────────────
    p4a_evidence = getattr(phase4a_result, 'evidence_ids', ()) or ()
    p4a_traces   = getattr(phase4a_result, 'trace_ids', ()) or ()
    p4b_evidence = (getattr(phase4b_result, 'evidence_ids', ()) or ()
                    if phase4b_result is not None else ())
    p4b_traces   = (getattr(phase4b_result, 'trace_ids', ()) or ()
                    if phase4b_result is not None else ())

    evidence_ids = tuple(p4a_evidence) + tuple(p4b_evidence)
    trace_ids    = tuple(p4a_traces)   + tuple(p4b_traces)

    # ── Phase4A لم تُقبَل → NOT_OPENED مباشرة ───────────────────────────────
    p4a_directive = getattr(phase4a_result, 'final_directive', None)
    if p4a_directive != 'ACCEPT':
        return Phase4DResult(
            initial_masdar_directive = initial_masdar_directive,
            final_directive          = 'NOT_OPENED',
            mushtaq_projection       = None,
            accepted_mushtaqat       = (),
            source_path              = 'not_opened',
            evidence_ids             = evidence_ids,
            trace_ids                = trace_ids,
            residual_codes           = ('phase4a_not_accept',),
        )

    # ── إسقاط المشتقات ─────────────────────────────────────────────────────
    mp = project_mushtaqat(
        phase4a_result  = phase4a_result,
        phase4b_result  = phase4b_result,
        phase4c_result  = phase4c_result,
        root_refinement = root_refinement,
        evidence_ids    = evidence_ids,
        trace_ids       = trace_ids,
    )

    # ── تحديد مسار المشتق ──────────────────────────────────────────────────
    directive = mp.directive

    if directive == 'ACCEPT':
        source_path = 'full_accept'
    elif directive == 'PARTIAL_ACCEPT':
        source_path = 'partial_accept'
    elif directive == 'DEFER':
        source_path = 'deferred'
    elif directive == 'BLOCK':
        source_path = 'blocked'
    elif directive == 'NOT_APPLICABLE':
        source_path = 'not_applicable'
    else:
        source_path = 'not_opened'

    # Fix 9: Filter resolved residuals and deduplicate (order-preserving).
    final_residuals = _partition_residuals(mp.residual_codes, phase4a_result)
    final_residuals = deduplicate_residuals(final_residuals)

    return Phase4DResult(
        initial_masdar_directive = initial_masdar_directive,
        final_directive          = directive,
        mushtaq_projection       = mp,
        accepted_mushtaqat       = mp.accepted_mushtaqat,
        source_path              = source_path,
        evidence_ids             = mp.evidence_ids,
        trace_ids                = mp.trace_ids,
        residual_codes           = final_residuals,
    )
