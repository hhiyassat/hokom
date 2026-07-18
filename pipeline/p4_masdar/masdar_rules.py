#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_masdar/masdar_rules.py — قواعد تطبيق Phase 4C
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

تُحدَّد قابلية تطبيق تحليل المصدر بناءً على نتائج Phase4A و Phase4B.

قواعد APPLICABLE:
  - Phase4A final_directive == ACCEPT
  - الوزن من عائلة فعلية (verbal)
  - Phase4B إما ACCEPT (بـ bab_id) أو DEFER (باب غامض لكن وزن مقبول) أو None

قواعد NOT_APPLICABLE:
  - الوزن من عائلة اسمية (لا فعلية)
  - Phase4A لم يكن ACCEPT

عائلات الأوزان الفعلية:
  triliteral_bare_verb, form_II_verb, form_III_verb, form_IV_verb,
  form_V_verb, form_VI_verb, form_VII_verb, form_VIII_verb,
  form_IX_verb, form_X_verb
"""

from __future__ import annotations

# عائلات الأوزان الفعلية المعروفة
_VERBAL_WAZN_FAMILIES = frozenset({
    "triliteral_bare_verb",
    "form_II_verb",
    "form_III_verb",
    "form_IV_verb",
    "form_V_verb",
    "form_VI_verb",
    "form_VII_verb",
    "form_VIII_verb",
    "form_IX_verb",
    "form_X_verb",
})

# عائلات الأوزان الاسمية (غير الفعلية)
_NOMINAL_WAZN_FAMILIES = frozenset({
    "triliteral_noun",
    "active_participle",
    "passive_participle",
    "intensive_noun",
    "noun_of_place_or_masdar",
    "instrument_noun",
    "broken_plural",
    "deverbal_noun",
})


def is_verbal_wazn_family(wazn_family: str | None) -> bool:
    """أعِد True إن كانت عائلة الوزن فعلية."""
    if wazn_family is None:
        return False
    return wazn_family in _VERBAL_WAZN_FAMILIES


def is_nominal_wazn_family(wazn_family: str | None) -> bool:
    """أعِد True إن كانت عائلة الوزن اسمية (لا فعلية)."""
    if wazn_family is None:
        return False
    return wazn_family in _NOMINAL_WAZN_FAMILIES


def assess_masdar_applicability(
    phase4a_directive: str | None,
    wazn_family: str | None,
    phase4b_directive: str | None,
) -> str:
    """
    قيّم قابلية تطبيق تحليل المصدر.

    Returns:
        'APPLICABLE'     — يمكن تطبيق تحليل المصدر.
        'NOT_APPLICABLE' — الوزن اسمي لا فعلي.
        'NOT_OPENED'     — Phase4A لم يقبل → لا يُفتح تحليل المصدر.
        'UNKNOWN'        — لا يمكن تحديد القابلية (بيانات ناقصة).
    """
    # Phase4A لم تُقبَل → لا يُفتح تحليل المصدر
    if phase4a_directive != 'ACCEPT':
        return 'NOT_OPENED'

    # الوزن غير معروف → UNKNOWN
    if wazn_family is None:
        return 'UNKNOWN'

    # الوزن اسمي → NOT_APPLICABLE
    if is_nominal_wazn_family(wazn_family):
        return 'NOT_APPLICABLE'

    # الوزن فعلي → APPLICABLE
    if is_verbal_wazn_family(wazn_family):
        return 'APPLICABLE'

    # عائلة غير مصنّفة → UNKNOWN
    return 'UNKNOWN'


def get_wazn_family_from_wazn_id(wazn_id: str | None) -> str | None:
    """
    أعِد عائلة الوزن من wazn_id بدون تحميل الـ catalog الكامل.
    يُستخدم كبديل سريع عندما لا يكون WaznProjection متاحًا.
    """
    if wazn_id is None:
        return None

    _WAZN_ID_TO_FAMILY: dict[str, str] = {
        # مجرد فعلي
        "FA_A_LA":   "triliteral_bare_verb",
        "FA_I_LA":   "triliteral_bare_verb",
        "FA_U_LA":   "triliteral_bare_verb",
        # مجرد اسمي
        "FA3L":      "triliteral_noun",
        "FI3L":      "triliteral_noun",
        "FU3L":      "triliteral_noun",
        "FA3IL":     "active_participle",
        "MAF3UL":    "passive_participle",
        "FA33AL":    "intensive_noun",
        # مزيد فعلي
        "FA33ALA":   "form_II_verb",
        "FA3ALA":    "form_III_verb",
        "AF3AL":     "form_IV_verb",
        "TAFA33ALA": "form_V_verb",
        "TAFA3ALA":  "form_VI_verb",
        "INFA3ALA":  "form_VII_verb",
        "IFTA3ALA":  "form_VIII_verb",
        "IFA3LAL":   "form_IX_verb",   # رباعي مزيد
        "IF3ALLA":   "form_IX_verb",   # اِفْعَلَّ — ثلاثي مزيد FORM_IX
        "ISTAF3ALA": "form_X_verb",
        # اسمية أخرى
        "MAF3AL":    "noun_of_place_or_masdar",
        "MAF3IL":    "noun_of_place_or_masdar",
        "MIF3AL":    "instrument_noun",
    }
    return _WAZN_ID_TO_FAMILY.get(wazn_id)
