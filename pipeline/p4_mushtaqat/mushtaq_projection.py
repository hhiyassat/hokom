#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_mushtaqat/mushtaq_projection.py — إسقاط المشتقات (Phase 4D)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ينتج MushtaqProjection من Phase4AResult و Phase4BResult و Phase4CResult
(الاختيارية).

شروط الفتح:
  - Phase4A ACCEPT مطلوب.
  - Phase4B و Phase4C: سياق (قد يكون None أو أي directive).
  - Phase4B BLOCK → ينتشر BLOCK إلى المشتقات (يجب الحجب الإجمالي).

التوجيه الكلي:
  ACCEPT         — جميع المشتقات المحسوبة مقبولة (لا دفرات).
  PARTIAL_ACCEPT — بعض مقبولة وبعض مؤجلة/محجوبة.
  DEFER          — لا مقبولات، بعضها مؤجل.
  BLOCK          — Phase4B BLOCK انتشر، أو جميع المشتقات محجوبة.
  NOT_OPENED     — Phase4A لم يقبل.
  NOT_APPLICABLE — الوزن اسمي.
"""

from __future__ import annotations

from pipeline.p4_mushtaqat.models import (
    MUSHTAQ_TYPES,
    MushtaqCandidate,
    MushtaqProjection,
)
from pipeline.p4_mushtaqat.mushtaq_hypothesis import generate_mushtaq_candidates
from pipeline.p4_mushtaqat.mushtaq_rules import (
    check_eligibility,
    get_wazn_family_from_wazn_id,
    infer_root_class_from_profile,
    infer_transitivity_from_bab,
    _is_nominal,
    _is_verbal,
)


def project_mushtaqat(
    phase4a_result,
    phase4b_result=None,
    phase4c_result=None,
    root_refinement=None,
    evidence_ids: tuple = (),
    trace_ids: tuple = (),
) -> MushtaqProjection:
    """
    أنتِج MushtaqProjection من نتائج Phase4A/B/C.

    Args:
        phase4a_result : Phase4AResult — مطلوب.
        phase4b_result : Phase4BResult | None — اختياري.
        phase4c_result : Phase4CResult | None — اختياري (للسياق).
        root_refinement: RootRefinement | None.
        evidence_ids   : شواهد إضافية.
        trace_ids      : مسار إضافي.

    Returns:
        MushtaqProjection
    """
    # ── استخراج البيانات من Phase4A ────────────────────────────────────────
    p4a_directive = getattr(phase4a_result, 'final_directive', None)

    wazn_projection = getattr(phase4a_result, 'wazn_projection', None)
    selected_wazn   = getattr(wazn_projection, 'selected_wazn', None) if wazn_projection else None
    wazn_id         = getattr(selected_wazn, 'wazn_id', None) if selected_wazn else None
    canonical_root  = getattr(wazn_projection, 'canonical_root', None) if wazn_projection else None

    # استرجاع عائلة الوزن
    wazn_family = None
    if selected_wazn is not None:
        wazn_family = getattr(selected_wazn, 'wazn_family', None)
    if wazn_family is None and wazn_id is not None:
        wazn_family = get_wazn_family_from_wazn_id(wazn_id)

    # ── استخراج البيانات من Phase4B ────────────────────────────────────────
    p4b_directive = None
    bab_id        = None
    if phase4b_result is not None:
        p4b_directive = getattr(phase4b_result, 'final_directive', None)
        bab_id        = getattr(phase4b_result, 'final_bab', None)

    # ── Phase4A لم تُقبَل → NOT_OPENED ─────────────────────────────────────
    if p4a_directive != 'ACCEPT':
        return MushtaqProjection(
            directive          = 'NOT_OPENED',
            stage_state        = 'NOT_OPENED',
            applicability      = 'NOT_OPENED',
            all_candidates     = (),
            accepted_mushtaqat = (),
            deferred_mushtaqat = (),
            blocked_mushtaqat  = (),
            source_wazn        = wazn_id,
            bab_id             = bab_id,
            canonical_root     = canonical_root,
            evidence_ids       = evidence_ids,
            trace_ids          = trace_ids,
            residual_codes     = ('phase4a_not_accept',),
        )

    # ── الوزن اسمي → NOT_APPLICABLE ────────────────────────────────────────
    if wazn_family is not None and _is_nominal(wazn_family):
        return MushtaqProjection(
            directive          = 'NOT_APPLICABLE',
            stage_state        = 'NOT_APPLICABLE',
            applicability      = 'NOT_APPLICABLE',
            all_candidates     = (),
            accepted_mushtaqat = (),
            deferred_mushtaqat = (),
            blocked_mushtaqat  = (),
            source_wazn        = wazn_id,
            bab_id             = bab_id,
            canonical_root     = canonical_root,
            evidence_ids       = evidence_ids,
            trace_ids          = trace_ids,
            residual_codes     = ('non_verbal_wazn',),
        )

    # ── Phase4B BLOCK ينتشر → BLOCK ─────────────────────────────────────────
    if p4b_directive == 'BLOCK':
        return MushtaqProjection(
            directive          = 'BLOCK',
            stage_state        = 'OPENED',
            applicability      = 'APPLICABLE',
            all_candidates     = (),
            accepted_mushtaqat = (),
            deferred_mushtaqat = (),
            blocked_mushtaqat  = tuple(MUSHTAQ_TYPES),
            source_wazn        = wazn_id,
            bab_id             = bab_id,
            canonical_root     = canonical_root,
            evidence_ids       = evidence_ids,
            trace_ids          = trace_ids,
            residual_codes     = ('phase4b_block_propagated',),
        )

    # ── استنتاج التعدية ────────────────────────────────────────────────────
    # نستنتج من bab_id؛ معظم الأبواب المجردة UNKNOWN
    transitivity = infer_transitivity_from_bab(bab_id)

    # ── استنتاج نوع الجذر ─────────────────────────────────────────────────
    # من root_profile في Phase4A إن وجد
    root_profile = None
    if wazn_projection is not None:
        root_profile = getattr(wazn_projection, 'root_profile', None)
    root_class = infer_root_class_from_profile(root_profile)

    # ── معالجة كل نوع مشتق ───────────────────────────────────────────────
    all_candidates: list = []
    accepted_pairs: list = []     # (type_str, pattern_str)
    deferred_types: list = []
    blocked_types:  list = []

    for mtype in sorted(MUSHTAQ_TYPES):  # sorted للثبات
        directive_m, reason_m = check_eligibility(
            mushtaq_type = mtype,
            wazn_family  = wazn_family,
            bab_id       = bab_id,
            transitivity = transitivity,
            root_class   = root_class,
        )

        candidates_m = generate_mushtaq_candidates(
            mushtaq_type          = mtype,
            wazn_family           = wazn_family,
            eligibility_directive = directive_m,
            eligibility_reason    = reason_m,
            evidence_ids          = evidence_ids,
            trace_ids             = trace_ids,
        )
        all_candidates.extend(candidates_m)

        if directive_m == 'ACCEPT':
            if candidates_m:
                # للأنواع ذات المرشحات المتعددة (SIYAG, ISM_ZAMAN, ISM_MAKAN, ISM_ALA)
                # نُدرج أول مرشح في القاموس المقبول، والبقية تبقى في all_candidates
                accepted_pairs.append((mtype, candidates_m[0].mushtaq_pattern))
            else:
                # أُهّل لكن لا مرشح في catalog → DEFER
                deferred_types.append(mtype)
        elif directive_m == 'DEFER':
            deferred_types.append(mtype)
        elif directive_m == 'BLOCK':
            blocked_types.append(mtype)
        # NOT_APPLICABLE: لا تُدرج في أي قائمة

    # ── تحديد التوجيه الكلي ─────────────────────────────────────────────
    n_accept  = len(accepted_pairs)
    n_defer   = len(deferred_types)
    n_block   = len(blocked_types)
    n_total   = n_accept + n_defer + n_block

    if n_total == 0:
        # جميع أنواع NOT_APPLICABLE
        overall = 'NOT_APPLICABLE'
        applicability = 'NOT_APPLICABLE'
    elif n_accept > 0 and n_defer == 0 and n_block == 0:
        overall = 'ACCEPT'
        applicability = 'APPLICABLE'
    elif n_accept > 0:
        overall = 'PARTIAL_ACCEPT'
        applicability = 'APPLICABLE'
    elif n_defer > 0:
        overall = 'DEFER'
        applicability = 'APPLICABLE'
    else:
        # كل شيء محجوب
        overall = 'BLOCK'
        applicability = 'APPLICABLE'

    # بناء residual_codes
    residuals: list = []
    if wazn_family is None:
        residuals.append('wazn_family_unknown')
    if transitivity == 'UNKNOWN':
        residuals.append('transitivity_unknown')
    if root_class == 'UNKNOWN':
        residuals.append('root_class_unknown')

    return MushtaqProjection(
        directive          = overall,
        stage_state        = 'OPENED',
        applicability      = applicability,
        all_candidates     = tuple(all_candidates),
        accepted_mushtaqat = tuple(accepted_pairs),
        deferred_mushtaqat = tuple(deferred_types),
        blocked_mushtaqat  = tuple(blocked_types),
        source_wazn        = wazn_id,
        bab_id             = bab_id,
        canonical_root     = canonical_root,
        evidence_ids       = evidence_ids,
        trace_ids          = trace_ids,
        residual_codes     = tuple(residuals),
    )
