#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_masdar/phase4c_orchestrator.py — منسّق Phase 4C (MasdarProjection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

الدالة العامة: project_masdar_with_licensing()

مسارات المصدر (source_path):
  structural_accept — صيغة مزيدة، استنتاج هيكلي ناجح.
  lexical_accept    — مدخل معجمي مرخّص (محجوز للمستقبل).
  deferred          — مجرد أو باب غامض → يتطلب بحثًا معجميًا.
  blocked           — تناقض من طبقة أعلى (Phase4B BLOCK).
  not_opened        — Phase4A لم يقبل.
  not_applicable    — وزن اسمي لا فعلي.
"""

from __future__ import annotations

from pipeline.p4_bab.phase4b_orchestrator import deduplicate_residuals, _partition_residuals
from pipeline.p4_masdar.masdar_projection import project_masdar
from pipeline.p4_masdar.models import Phase4CResult


def project_masdar_with_licensing(
    phase4a_result,
    phase4b_result=None,
    root_refinement=None,
) -> Phase4CResult:
    """
    أنتِج Phase4CResult من Phase4AResult و Phase4BResult (الاختياري).

    Args:
        phase4a_result  : Phase4AResult — مطلوب.
        phase4b_result  : Phase4BResult | None — اختياري.
        root_refinement : RootRefinement | None — مُرسَل من الأنبوب (لا يُعدَّل هنا).

    Returns:
        Phase4CResult

    Security:
        - لا استيراد لمحركات خارجية (local engine only).
        - لا يعدّل canonical_root أو selected_wazn.
        - لا يُنتِج حقول مشتقات (mushtaqat).
        - لا يُنتِج تصريف (paradigm).
    """
    # ── الحكم الابتدائي من Phase4B ──────────────────────────────────────────
    if phase4b_result is not None:
        initial_bab_directive = getattr(phase4b_result, 'final_directive', 'UNKNOWN')
    else:
        initial_bab_directive = 'SKIP'

    # ── جمع الشواهد الأولية ─────────────────────────────────────────────────
    p4a_evidence = getattr(phase4a_result, 'evidence_ids', ()) or ()
    p4a_traces   = getattr(phase4a_result, 'trace_ids', ()) or ()
    p4b_evidence = (getattr(phase4b_result, 'evidence_ids', ()) or ()
                    if phase4b_result is not None else ())
    p4b_traces   = (getattr(phase4b_result, 'trace_ids', ()) or ()
                    if phase4b_result is not None else ())

    evidence_ids = tuple(p4a_evidence) + tuple(p4b_evidence)
    trace_ids    = tuple(p4a_traces)   + tuple(p4b_traces)

    # ── Phase4A لم تُقبَل → NOT_OPENED مباشرة ────────────────────────────────
    p4a_directive = getattr(phase4a_result, 'final_directive', None)
    if p4a_directive != 'ACCEPT':
        return Phase4CResult(
            initial_bab_directive = initial_bab_directive,
            final_directive       = 'NOT_OPENED',
            masdar_projection     = None,
            final_masdar          = None,
            final_masdar_pattern  = None,
            source_path           = 'not_opened',
            evidence_ids          = evidence_ids,
            trace_ids             = trace_ids,
            residual_codes        = ('phase4a_not_accept',),
        )

    # ── إسقاط المصدر ────────────────────────────────────────────────────────
    mp = project_masdar(
        phase4a_result = phase4a_result,
        phase4b_result = phase4b_result,
        evidence_ids   = evidence_ids,
        trace_ids      = trace_ids,
    )

    # ── تحديد مسار المصدر ───────────────────────────────────────────────────
    directive = mp.directive

    if directive == 'ACCEPT':
        # هل المصدر معجمي أم هيكلي؟
        if mp.source_type == 'LEXICAL_LICENSED':
            source_path = 'lexical_accept'
        else:
            source_path = 'structural_accept'
    elif directive == 'DEFER':
        source_path = 'deferred'
    elif directive == 'BLOCK':
        source_path = 'blocked'
    elif directive == 'NOT_APPLICABLE':
        source_path = 'not_applicable'
    else:
        source_path = 'not_opened'

    # Fix 8/9: Filter resolved residuals and deduplicate.
    final_residuals = _partition_residuals(mp.residual_codes, phase4a_result)
    final_residuals = deduplicate_residuals(final_residuals)

    return Phase4CResult(
        initial_bab_directive = initial_bab_directive,
        final_directive       = directive,
        masdar_projection     = mp,
        final_masdar          = mp.selected_masdar,
        final_masdar_pattern  = mp.selected_masdar_pattern,
        source_path           = source_path,
        evidence_ids          = mp.evidence_ids,
        trace_ids             = mp.trace_ids,
        residual_codes        = final_residuals,
    )
