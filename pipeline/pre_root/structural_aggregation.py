#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/pre_root/structural_aggregation.py — تجميع الأحكام البنيوية (Axis 3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

القانون المركزي: BLOCK > DEFER > ACCEPT

  إذا كان أيّ حكم BLOCK  → النتيجة الكلية BLOCK
  إذا كان أيّ حكم DEFER  (ولا BLOCK)  → DEFER
  غير ذلك → ACCEPT

هذا الملف مسؤول فقط عن التجميع — لا يصدر أحكامًا بنيوية بنفسه.

تكامل مع HR2S:
  الحكم المُجمَّع DEFER يعني «مسار الصرف NOT_OPENED».
  رمز التحفظ: 'defer:pre_root:structural_prerequisite_not_closed'
  لا يُفتح مسار الجذر عند DEFER — لا يُستدعى HR2S.
"""

from __future__ import annotations

from typing import Sequence


# ══════════════════════════════════════════════════════════════════════════════
# 1.  أولوية الأحكام
# ══════════════════════════════════════════════════════════════════════════════

_VERDICT_PRIORITY: dict[str, int] = {
    'ACCEPT': 0,
    'DEFER':  1,
    'BLOCK':  2,
}

#: رمز التحفظ المعياري عند التأجيل البنيوي
STRUCTURAL_DEFER_RESIDUAL = 'defer:pre_root:structural_prerequisite_not_closed'

#: رمز التحفظ عند الحجب البنيوي
STRUCTURAL_BLOCK_RESIDUAL = 'block:pre_root:structural_impossibility'


# ══════════════════════════════════════════════════════════════════════════════
# 2.  aggregate_structural_verdict — الدالة المركزية
# ══════════════════════════════════════════════════════════════════════════════

def aggregate_structural_verdict(verdicts: Sequence[str]) -> str:
    """
    ادمج أحكامًا بنيوية متعددة وفق القانون: BLOCK > DEFER > ACCEPT.

    Parameters
    ----------
    verdicts : مجموعة أحكام، كل منها 'ACCEPT' | 'DEFER' | 'BLOCK'
               قائمة فارغة → 'ACCEPT' (لا شيء يمنع)
               قيمة غير معروفة → تُعامَل كـ DEFER حفظًا

    Returns
    -------
    str : 'ACCEPT' | 'DEFER' | 'BLOCK'

    Examples
    --------
    >>> aggregate_structural_verdict([])
    'ACCEPT'
    >>> aggregate_structural_verdict(['ACCEPT', 'ACCEPT'])
    'ACCEPT'
    >>> aggregate_structural_verdict(['ACCEPT', 'DEFER'])
    'DEFER'
    >>> aggregate_structural_verdict(['DEFER', 'BLOCK'])
    'BLOCK'
    >>> aggregate_structural_verdict(['ACCEPT', 'ACCEPT', 'BLOCK'])
    'BLOCK'
    >>> aggregate_structural_verdict(['UNKNOWN_VERDICT'])
    'DEFER'
    """
    if not verdicts:
        return 'ACCEPT'

    best = 'ACCEPT'
    for v in verdicts:
        prio_v    = _VERDICT_PRIORITY.get(v)
        prio_best = _VERDICT_PRIORITY[best]

        if prio_v is None:
            # قيمة غير معروفة → حفظ بـ DEFER إن لم يكن هناك BLOCK
            if prio_best < _VERDICT_PRIORITY['DEFER']:
                best = 'DEFER'
        elif prio_v > prio_best:
            best = v

    return best


def verdicts_from_directive(directive_value: str) -> list[str]:
    """
    حوّل قيمة RootPathDirective إلى حكم يمكن إدراجه في aggregate_structural_verdict.

    Parameters
    ----------
    directive_value : 'OPEN' | 'DEFER' | 'BLOCK'

    Returns
    -------
    list[str] : قائمة تحتوي على الحكم المقابل
    """
    mapping = {
        'OPEN':  'ACCEPT',
        'DEFER': 'DEFER',
        'BLOCK': 'BLOCK',
    }
    return [mapping.get(directive_value, 'DEFER')]


def residuals_for_verdict(verdict: str) -> tuple[str, ...]:
    """
    أعطِ رموز التحفظ المناسبة للحكم المُجمَّع.

    Parameters
    ----------
    verdict : 'ACCEPT' | 'DEFER' | 'BLOCK'

    Returns
    -------
    tuple[str, ...] : رموز التحفظ (فارغة عند ACCEPT)
    """
    if verdict == 'DEFER':
        return (STRUCTURAL_DEFER_RESIDUAL,)
    if verdict == 'BLOCK':
        return (STRUCTURAL_BLOCK_RESIDUAL,)
    return ()
