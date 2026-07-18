#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_mushtaqat/mushtaq_rules.py — قواعد أهلية المشتقات (Phase 4D)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

تُحدَّد أهلية كل نوع من المشتقات بناءً على:
  - wazn_family  : عائلة الوزن (triliteral_bare_verb | form_II_verb | ...)
  - transitivity : تعدية الفعل (TRANSITIVE | INTRANSITIVE | UNCONSTRAINED | UNKNOWN)
  - root_class   : نوع الجذر (SOUND | HOLLOW | DEFECTIVE | DOUBLED | QUADRILATERAL | UNKNOWN)
  - bab_id       : الباب من Phase4B (قد يكون None)

مخرج check_eligibility():
  'ACCEPT'         — أهلية مؤكدة.
  'DEFER'          — غير محسوم (معلومات ناقصة).
  'BLOCK'          — ممنوع صريحًا.
  'NOT_APPLICABLE' — لا ينطبق على هذا الوزن/النوع.

قواعد التعدية:
  ISM_MAF3UL   : BLOCK إن لازم، DEFER إن مجهول، ACCEPT إن متعدٍّ.
  SIFA_MUSHABBAHA : BLOCK إن متعدٍّ، DEFER إن مجهول، ACCEPT إن لازم.
  ISM_ALA      : DEFER إن مجهول، ACCEPT إن متعدٍّ، DEFER إن لازم.
  ISM_FA3IL    : UNCONSTRAINED — لا قيد.
  SIYAG_MUBALAGHAH : UNCONSTRAINED — أي فعل مجرد.
  ISM_ZAMAN    : UNCONSTRAINED.
  ISM_MAKAN    : UNCONSTRAINED.
  TAFDHIL      : قيود متعددة (شكل I فقط، جذر غير مجوّف، غير رباعي، ...).
"""

from __future__ import annotations

# عائلات الأوزان الفعلية المدعومة (Form I)
_FORM_I_FAMILIES = frozenset({
    "triliteral_bare_verb",
})

# عائلات الأوزان المزيدة (Forms II–X)
_MAZID_FAMILIES = frozenset({
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

_VERBAL_FAMILIES = _FORM_I_FAMILIES | _MAZID_FAMILIES

# عائلات الأوزان الاسمية
_NOMINAL_FAMILIES = frozenset({
    "triliteral_noun",
    "active_participle",
    "passive_participle",
    "intensive_noun",
    "noun_of_place_or_masdar",
    "instrument_noun",
    "broken_plural",
    "deverbal_noun",
})

# أنواع الجذور المانعة لـ TAFDHIL
_TAFDHIL_BLOCKED_ROOT_CLASSES = frozenset({
    "HOLLOW",
    "QUADRILATERAL",
    "DEFECTIVE",
})

# أبواب الصفة المشبهة المفضلة (سماعية — لكنها مؤشرات)
_SIFA_PREFERRED_BABS = frozenset({
    "BAB_IV_SAMIA",   # فَعِلَ — الوزن الاحتمالي للصفة المشبهة
    "BAB_V_KARUMA",   # فَعُلَ — الوزن الاحتمالي للصفة المشبهة
})


def _is_verbal(wazn_family: str | None) -> bool:
    """أعِد True إن كانت عائلة الوزن فعلية."""
    return wazn_family in _VERBAL_FAMILIES if wazn_family else False


def _is_form_i(wazn_family: str | None) -> bool:
    """أعِد True إن كانت عائلة الوزن مجردة (Form I)."""
    return wazn_family in _FORM_I_FAMILIES if wazn_family else False


def _is_mazid(wazn_family: str | None) -> bool:
    """أعِد True إن كانت عائلة الوزن مزيدة (Forms II–X)."""
    return wazn_family in _MAZID_FAMILIES if wazn_family else False


def _is_nominal(wazn_family: str | None) -> bool:
    """أعِد True إن كانت عائلة الوزن اسمية."""
    return wazn_family in _NOMINAL_FAMILIES if wazn_family else False


def check_eligibility(
    mushtaq_type: str,
    wazn_family: str | None,
    bab_id: str | None,
    transitivity: str,
    root_class: str,
) -> tuple:
    """
    تحقق من أهلية مشتق لعائلة وزن وتعدية وجذر معينة.

    Args:
        mushtaq_type : نوع المشتق (ISM_FA3IL | ISM_MAF3UL | ...).
        wazn_family  : عائلة الوزن من Phase4A.
        bab_id       : الباب من Phase4B أو None.
        transitivity : TRANSITIVE | INTRANSITIVE | UNCONSTRAINED | UNKNOWN.
        root_class   : SOUND | HOLLOW | DEFECTIVE | DOUBLED | QUADRILATERAL | UNKNOWN.

    Returns:
        (directive: str, reason: str)
        directive ∈ {'ACCEPT', 'DEFER', 'BLOCK', 'NOT_APPLICABLE'}
    """
    # ── الوزن اسمي → NOT_APPLICABLE لجميع الأنواع ──────────────────────────
    if _is_nominal(wazn_family):
        return ('NOT_APPLICABLE', 'nominal_wazn')

    # ── الوزن غير معروف → DEFER ─────────────────────────────────────────────
    if wazn_family is None:
        return ('DEFER', 'wazn_family_unknown')

    # ── الوزن ليس في القوائم المعروفة → DEFER ────────────────────────────────
    if not _is_verbal(wazn_family):
        return ('DEFER', 'wazn_family_unclassified')

    # ══ قواعد كل نوع ══════════════════════════════════════════════════════════

    if mushtaq_type == 'ISM_FA3IL':
        # أي فعل (متعدٍّ أو لازم) → أهل
        return ('ACCEPT', 'fa3il_unconstrained')

    elif mushtaq_type == 'ISM_MAF3UL':
        if not _is_verbal(wazn_family):
            return ('NOT_APPLICABLE', 'non_verbal_wazn')
        # الصيغ المزيدة (Forms II–X): اسم المفعول قياسي هيكليًا بغض النظر عن التعدية
        # لأن الوزن المزيد يحدد النمط بشكل فريد.
        if _is_mazid(wazn_family):
            return ('ACCEPT', 'mazid_structural_maf3ul')
        # Form I: يعتمد على التعدية
        if transitivity == 'INTRANSITIVE':
            return ('BLOCK', 'intransitive_verb')
        if transitivity == 'UNKNOWN':
            return ('DEFER', 'transitivity_unknown')
        # TRANSITIVE أو UNCONSTRAINED → ACCEPT
        return ('ACCEPT', 'transitive_verb')

    elif mushtaq_type == 'SIFA_MUSHABBAHA':
        # الصفة المشبهة: مجرد فقط (Form I)
        if not _is_form_i(wazn_family):
            return ('NOT_APPLICABLE', 'augmented_not_standard_for_sifa')
        if transitivity == 'TRANSITIVE':
            return ('BLOCK', 'transitive_verb')
        if transitivity == 'UNKNOWN':
            return ('DEFER', 'transitivity_unknown')
        # INTRANSITIVE أو UNCONSTRAINED → ACCEPT
        return ('ACCEPT', 'intransitive_stative_verb')

    elif mushtaq_type == 'SIYAG_MUBALAGHAH':
        # صيغ المبالغة: Form I فقط (معيار)
        if not _is_form_i(wazn_family):
            return ('DEFER', 'mazid_not_standard_for_mubalaghah')
        # أي فعل → أهل
        return ('ACCEPT', 'verbal_root_form_i')

    elif mushtaq_type == 'ISM_ZAMAN':
        # اسم الزمان: أي فعل
        if not _is_form_i(wazn_family):
            return ('DEFER', 'augmented_ism_zaman_masdar_based')
        return ('ACCEPT', 'verbal_wazn_form_i')

    elif mushtaq_type == 'ISM_MAKAN':
        # اسم المكان: أي فعل (نفس اسم الزمان)
        if not _is_form_i(wazn_family):
            return ('DEFER', 'augmented_ism_makan_masdar_based')
        return ('ACCEPT', 'verbal_wazn_form_i')

    elif mushtaq_type == 'ISM_ALA':
        # اسم الآلة: Form I ومتعدٍّ
        if not _is_form_i(wazn_family):
            return ('NOT_APPLICABLE', 'augmented_not_standard_for_ism_ala')
        if transitivity == 'INTRANSITIVE':
            return ('DEFER', 'intransitive_ism_ala_unusual')
        if transitivity == 'UNKNOWN':
            return ('DEFER', 'transitivity_unknown')
        return ('ACCEPT', 'transitive_form_i')

    elif mushtaq_type == 'TAFDHIL':
        # أفعل التفضيل: قيود متعددة
        if not _is_form_i(wazn_family):
            return ('NOT_APPLICABLE', 'augmented_not_eligible_for_tafdhil')
        if root_class in _TAFDHIL_BLOCKED_ROOT_CLASSES:
            return ('NOT_APPLICABLE', f'root_class_incompatible:{root_class}')
        if root_class == 'UNKNOWN':
            return ('DEFER', 'root_class_ambiguous')
        # Form I، جذر سليم → DEFER إن bab_id غير معروف (لتجنب الخلط مع صيغ اللون/العيب)
        if bab_id is None:
            return ('DEFER', 'bab_unknown_tafdhil_ambiguous')
        # بعض الأبواب لا تدعم TAFDHIL (BAB_IX color/defect — تستخدم أفعل للصفة لا للتفضيل)
        if bab_id == 'BAB_FORM_IX':
            return ('NOT_APPLICABLE', 'form_ix_uses_afal_for_sifa_not_tafdhil')
        return ('ACCEPT', 'mujarrad_tafdhil_eligible')

    # نوع غير معروف → DEFER
    return ('DEFER', f'unknown_mushtaq_type:{mushtaq_type}')


def get_wazn_family_from_wazn_id(wazn_id: str | None) -> str | None:
    """
    أعِد عائلة الوزن من wazn_id.
    تطابق ما في masdar_rules.py للاتساق.
    """
    if wazn_id is None:
        return None

    _MAP: dict = {
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
        "IFA3LAL":   "form_IX_verb",
        "ISTAF3ALA": "form_X_verb",
        # اسمية أخرى
        "MAF3AL":    "noun_of_place_or_masdar",
        "MAF3IL":    "noun_of_place_or_masdar",
        "MIF3AL":    "instrument_noun",
    }
    return _MAP.get(wazn_id)


def infer_transitivity_from_bab(bab_id: str | None) -> str:
    """
    استنتج التعدية من bab_id إن أمكن.
    معظم الأبواب لها تعدية غامضة على مستوى الشكل — سماعي.

    Returns:
        'TRANSITIVE' | 'INTRANSITIVE' | 'UNKNOWN'
    """
    if bab_id is None:
        return 'UNKNOWN'

    # الصيغ المزيدة Form II, III, IV عادةً متعدية
    _TYPICALLY_TRANSITIVE = frozenset({
        "BAB_FORM_II",
        "BAB_FORM_IV",
        "BAB_FORM_X",
    })
    # الصيغ المزيدة V, VI, VII, IX عادةً لازمة
    _TYPICALLY_INTRANSITIVE = frozenset({
        "BAB_FORM_V",
        "BAB_FORM_VI",
        "BAB_FORM_VII",
        "BAB_FORM_IX",
    })

    if bab_id in _TYPICALLY_TRANSITIVE:
        return 'TRANSITIVE'
    if bab_id in _TYPICALLY_INTRANSITIVE:
        return 'INTRANSITIVE'

    # الأبواب المجردة (I–VI): سماعي — لا تنبؤ هيكلي
    return 'UNKNOWN'


def infer_root_class_from_profile(root_profile: object | None) -> str:
    """
    استنتج نوع الجذر من root_profile (من Phase4A أو P3).

    Returns:
        'SOUND' | 'HOLLOW' | 'DEFECTIVE' | 'DOUBLED' | 'QUADRILATERAL' | 'UNKNOWN'
    """
    if root_profile is None:
        return 'UNKNOWN'

    if isinstance(root_profile, dict):
        rc = root_profile.get('root_class')
    else:
        rc = getattr(root_profile, 'root_class', None)

    if rc is None:
        return 'UNKNOWN'

    # توحيد التسميات
    rc_upper = str(rc).upper()
    _KNOWN = frozenset({'SOUND', 'HOLLOW', 'DEFECTIVE', 'DOUBLED', 'QUADRILATERAL'})
    if rc_upper in _KNOWN:
        return rc_upper

    return 'UNKNOWN'
