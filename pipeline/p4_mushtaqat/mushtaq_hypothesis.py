#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_mushtaqat/mushtaq_hypothesis.py — توليد مرشحات المشتقات
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يولّد قائمة MushtaqCandidate من:
  - mushtaq_type   : نوع المشتق المطلوب.
  - wazn_family    : عائلة الوزن (من Phase4A).
  - eligibility    : نتيجة check_eligibility().
  - evidence_ids   : شواهد تُمرَّر للمرشحات.
  - trace_ids      : مسار يُمرَّر للمرشحات.

المنطق:
  - إن كانت الأهلية ACCEPT:
      ابحث في catalog عن تعريفات (mushtaq_type, wazn_family) → توليد مرشحات.
  - إن كانت DEFER: لا مرشحات (أو مرشح DEFER_REQUIRED وهمي).
  - إن كانت BLOCK / NOT_APPLICABLE: لا مرشحات.
"""

from __future__ import annotations

from pipeline.p4_mushtaqat.models import MushtaqCandidate, MUSHTAQ_TYPES
from pipeline.p4_mushtaqat.mushtaq_catalog import get_mushtaq_definitions


def generate_mushtaq_candidates(
    mushtaq_type: str,
    wazn_family: str | None,
    eligibility_directive: str,
    eligibility_reason: str,
    evidence_ids: tuple,
    trace_ids: tuple,
) -> list:
    """
    ولّد مرشحات المشتق بناءً على الأهلية والوزن.

    Args:
        mushtaq_type          : نوع المشتق.
        wazn_family           : عائلة الوزن من Phase4A.
        eligibility_directive : 'ACCEPT' | 'DEFER' | 'BLOCK' | 'NOT_APPLICABLE'.
        eligibility_reason    : سبب الحكم.
        evidence_ids          : شواهد لتمريرها.
        trace_ids             : مسار لتمريره.

    Returns:
        list[MushtaqCandidate] — قائمة المرشحات (قد تكون فارغة).
    """
    if mushtaq_type not in MUSHTAQ_TYPES:
        return []

    if eligibility_directive in ('BLOCK', 'NOT_APPLICABLE'):
        # لا مرشحات عند الحجب أو عدم الانطباق
        return []

    if eligibility_directive == 'DEFER':
        # لا مرشحات هيكلية — الأهلية غير محسومة
        return []

    # eligibility_directive == 'ACCEPT'
    if wazn_family is None:
        return []

    definitions = get_mushtaq_definitions(mushtaq_type, wazn_family)
    if not definitions:
        return []

    candidates = []
    for defn in definitions:
        candidates.append(MushtaqCandidate(
            mushtaq_type            = defn.mushtaq_type,
            mushtaq_pattern         = defn.pattern,
            source_type             = defn.source_type,
            transitivity_constraint = defn.transitivity_constraint,
            confidence              = 'HIGH',
            evidence_ids            = evidence_ids + tuple(defn.evidence_required),
            trace_ids               = trace_ids,
            residual_codes          = (),
        ))

    return candidates
