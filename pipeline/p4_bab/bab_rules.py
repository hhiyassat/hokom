#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_bab/bab_rules.py — قواعد الباب وأولوية الدليل
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

أولوية الدليل (من الأقوى إلى الأضعف):
  1. دليل paradigm مرخَّص صريح (ماضٍ + مضارع بحركة معروفة)
  2. دليل ماضٍ/مضارع مزدوج من السياق
  3. إدخال معجمي مرخَّص
  4. وزن مزيد يُعيَّن بشكل فريد (مثل اِفْتَعَلَ → FORM_VIII)
  5. قيد هيكلي (حركة ع الماضي وحدها — غير كافٍ للمجرد أبدًا)
  6. fallback → DEFER

القاعدة الجوهرية للمجرد:
  فَعَلَ وحده → DEFER (يصلح لـ BAB_I أو BAB_II أو BAB_III)
  فَعِلَ وحده → DEFER (يصلح لـ BAB_IV أو BAB_VI)
  فَعُلَ وحده → DEFER (BAB_V هو الاحتمال الوحيد لكن يحتاج دليل)

للمزيد:
  وزن الماضي يُعيِّن الباب بشكل فريد → ACCEPT ممكن بالوزن وحده.

الأوزان الاسمية → NOT_APPLICABLE (ليس BLOCK).
"""

from __future__ import annotations

# ── حروف الدياكريتيك العربية ──────────────────────────────────────────────
_FATHA   = 'َ'   # َ
_KASRA   = 'ِ'   # ِ
_DAMMA   = 'ُ'   # ُ
_SUKUN   = 'ْ'   # ْ
_AYN     = 'ع'   # ع

# ── عائلات الأوزان الفعلية (من wazn_catalog) ──────────────────────────────
_VERBAL_FAMILIES: frozenset[str] = frozenset({
    "triliteral_bare_verb",
    "form_II_verb",
    "form_III_verb",
    "form_IV_verb",
    "form_V_verb",
    "form_VI_verb",
    "form_VII_verb",
    "form_VIII_verb",
    "form_X_verb",
})

# ── تعيين wazn_id الفريد للأبواب المزيدة ──────────────────────────────────
# هذه الأوزان تُعيِّن الباب بشكل فريد — لا يلزم دليل مضارع.
_MAZID_WAZN_TO_BAB: dict[str, str] = {
    "FA33ALA":  "BAB_FORM_II",
    "FA3ALA":   "BAB_FORM_III",
    "AF3AL":    "BAB_FORM_IV",
    "TAFA33ALA": "BAB_FORM_V",
    "TAFA3ALA": "BAB_FORM_VI",
    "INFA3ALA": "BAB_FORM_VII",
    "IFTA3ALA": "BAB_FORM_VIII",
    "ISTAF3ALA": "BAB_FORM_X",
}

# ── أوزان الماضي المجردة وعدد أبوابها الممكنة بدون مضارع ─────────────────
_MUJARRAD_PAST_WAZN_AMBIGUITY: dict[str, int] = {
    "FA_A_LA": 3,   # BAB_I, BAB_II, BAB_III
    "FA_I_LA": 2,   # BAB_IV, BAB_VI
    "FA_U_LA": 1,   # BAB_V فقط — لكن يحتاج دليل
}


def is_verbal_family(wazn_family: str | None) -> bool:
    """هل عائلة الوزن فعلية (وليست اسمية)؟"""
    return wazn_family in _VERBAL_FAMILIES


def is_mazid_wazn(past_wazn_id: str) -> bool:
    """هل wazn_id ينتمي لمزيد ذي تعيين فريد؟"""
    return past_wazn_id in _MAZID_WAZN_TO_BAB


def get_mazid_bab(past_wazn_id: str) -> str | None:
    """أعِد bab_id للوزن المزيد الفريد، أو None."""
    return _MAZID_WAZN_TO_BAB.get(past_wazn_id)


def mujarrad_ambiguity_count(past_wazn_id: str) -> int:
    """عدد الأبواب الممكنة للمجرد بدون دليل مضارع (0 إن لم يكن مجردًا)."""
    return _MUJARRAD_PAST_WAZN_AMBIGUITY.get(past_wazn_id, 0)


def extract_ayn_vowel_from_pattern(pattern: str) -> str | None:
    """
    استخرج حركة العين (ع) من نمط وزن عربي مُشكَّل.

    مثال:
      "يَفْعُلُ" → 'u'   (ضمة على ع)
      "يَفْعِلُ" → 'i'   (كسرة على ع)
      "يَفْعَلُ" → 'a'   (فتحة على ع)
      "فَعَلَ"   → 'a'   (فتحة على ع)
      "فَعِلَ"   → 'i'   (كسرة على ع)
      "فَعُلَ"   → 'u'   (ضمة على ع)
    """
    for i, ch in enumerate(pattern):
        if ch == _AYN and i + 1 < len(pattern):
            nxt = pattern[i + 1]
            if nxt == _FATHA:
                return 'a'
            if nxt == _KASRA:
                return 'i'
            if nxt == _DAMMA:
                return 'u'
    return None


def extract_imperfect_vowel_from_evidence(
    evidence_ids: tuple[str, ...],
) -> str | None:
    """
    استخرج حركة العين للمضارع من شواهد evidence_ids.

    التنسيقات المدعومة:
      "imperfect_ayn:u"           → 'u'
      "imperfect_ayn:i"           → 'i'
      "imperfect_ayn:a"           → 'a'
      "paired_paradigm:imperfect_ayn=u" → 'u'
      "paired:{x}:imperfect_ayn:{v}"   → v ∈ {'a','i','u'}
    """
    for ev in evidence_ids:
        # تنسيق مباشر: "imperfect_ayn:u"
        if ev.startswith("imperfect_ayn:"):
            v = ev.split(":", 1)[1].strip()
            if v in ('a', 'i', 'u'):
                return v

        # تنسيق مضمَّن: "paired_paradigm:imperfect_ayn=u"
        if "imperfect_ayn=" in ev:
            idx = ev.index("imperfect_ayn=") + len("imperfect_ayn=")
            v = ev[idx:idx+1]
            if v in ('a', 'i', 'u'):
                return v

        # تنسيق آخر: "paired:{x}:imperfect_ayn:{v}"
        if "imperfect_ayn" in ev and ":" in ev:
            parts = ev.split(":")
            for j, p in enumerate(parts):
                if p == "imperfect_ayn" and j + 1 < len(parts):
                    v = parts[j + 1].strip()
                    if v in ('a', 'i', 'u'):
                        return v

    return None


def normalize_imperfect_wazn(imperfect_wazn: str | None) -> str | None:
    """
    حوِّل imperfect_wazn إلى حركة العين ('a'|'i'|'u') أو None.

    يقبل:
      - حرف واحد: 'a', 'i', 'u'
      - نمط وزن عربي: "يَفْعُلُ" (يستخرج حركة ع)
      - None
    """
    if imperfect_wazn is None:
        return None
    if imperfect_wazn in ('a', 'i', 'u'):
        return imperfect_wazn
    return extract_ayn_vowel_from_pattern(imperfect_wazn)


def evaluate_evidence_sufficiency(
    past_wazn_id: str,
    imperfect_vowel: str | None,
    evidence_ids: tuple[str, ...],
    wazn_family: str | None,
) -> str:
    """
    قيِّم كفاية الدليل وأعِد أحد:
      'UNIQUE_ACCEPT'      — الباب محدَّد بشكل فريد + دليل كافٍ
      'MUJARRAD_AMBIGUOUS' — مجرد + لا دليل مضارع → DEFER
      'NO_CATALOG_MATCH'   — لا إدخال في catalog → DEFER
      'MAZID_ACCEPT'       — مزيد + وزن فريد → ACCEPT
    """
    # المزيد: وزن ماضٍ فريد يكفي
    if is_mazid_wazn(past_wazn_id):
        return 'MAZID_ACCEPT'

    # المجرد
    ambiguity = mujarrad_ambiguity_count(past_wazn_id)
    if ambiguity == 0:
        return 'NO_CATALOG_MATCH'

    if imperfect_vowel is not None:
        return 'UNIQUE_ACCEPT'

    # حتى فَعُلَ (ambiguity==1) يحتاج دليل صريح
    return 'MUJARRAD_AMBIGUOUS'
