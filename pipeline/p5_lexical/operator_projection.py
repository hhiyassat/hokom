#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
operator_id_map.py — خريطة الهويات المعجمية للعوامل
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

القاعدة المعمارية:
  P5 تُحدِّد الرمز بهويته المعجمية، لا بأثره النحوي.
  operator_id   — هوية مستقرة، معجمية، سطحية (INNA / LAM / KAY …)
  lexical_family — أسرة معجمية حقيقية أو هوية ذاتية للرموز المنفردة

مصادر التجميع الحقيقي (أسر فعلية):
  INNA_SERIES        — إِنَّ أَنَّ كَأَنَّ لَكِنَّ لَيْتَ لَعَلَّ
  KANA_SERIES        — كَانَ وأخواتها (الأفعال الناقصة)
  APPROXIMATION_SERIES — عَسَى كَادَ كَرُبَ أَوْشَكَ (أفعال المقاربة)
  EVALUATION_SERIES  — نِعْمَ بِئْسَ سَاءَ حَبَّذَا (أفعال المدح والذم)

كل رمز آخر: lexical_family = operator_id (هوية ذاتية)

المفتاح: matched_surface كما يعيده lookup_canonical()
  أي surface_vocalized من عمود الكتالوج بعينه.
  للمداخل غير المشكولة (كم، أيا، كأين …) المفتاح هو الشكل غير المشكول.
"""

from __future__ import annotations
from dataclasses import dataclass

# ── حروف التشكيل (لحذفها عند اشتقاق الهوية الاحتياطية) ──────────────────────
# DEPRECATED (Phase A): parallel diacritic set — will consolidate into
# glyph_classification.MarkClass as the single source of truth.
# Do not expand this set; use build_glyph_traces() in new code.
_DIACRITICS: frozenset[str] = frozenset('ًٌٍَُِّْٰ')


# ══════════════════════════════════════════════════════════════════════════════
# هيكل ملف التعريف المعجمي
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class OperatorProfile:
    """
    الهوية المعجمية لعامل مبني.

    operator_id    — معرِّف مستقر: INNA | LAM | KAY | …
    lexical_family — الأسرة المعجمية: INNA_SERIES أو = operator_id للرموز المنفردة
    """
    operator_id:    str
    lexical_family: str


# ══════════════════════════════════════════════════════════════════════════════
# الخريطة الرئيسية
# المفتاح: matched_surface كما يُخزَّن في الكتالوج (مشكول أو غير مشكول)
# ══════════════════════════════════════════════════════════════════════════════

OPERATOR_PROFILE: dict[str, OperatorProfile] = {

    # ── المجموعة 1: حروف الجر (كل منها هوية مستقلة) ─────────────────────────
    'بِ':       OperatorProfile('BI',       'BI'),
    'مِنْ':     OperatorProfile('MIN',      'MIN'),
    'إِلَى':    OperatorProfile('ILA',      'ILA'),
    'فِي':      OperatorProfile('FI',       'FI'),
    'عَنْ':     OperatorProfile('AN_JAR',   'AN_JAR'),
    'وَ':       OperatorProfile('WA',       'WA'),    # وَ عطف/جر — نفس السطح
    'تَ':       OperatorProfile('TA_JAR',   'TA_JAR'),
    'لِ':       OperatorProfile('LI',       'LI'),    # لِ جر/أمر — نفس السطح
    'رُبَّ':    OperatorProfile('RUBBA',    'RUBBA'),
    'عَلَى':    OperatorProfile('ALA',      'ALA'),
    'كَ':       OperatorProfile('KA',       'KA'),
    'مُذْ':     OperatorProfile('MUDH',     'MUDH'),
    'مُنْذُ':   OperatorProfile('MUNDHU',   'MUNDHU'),
    'حَتَّى':   OperatorProfile('HATTA',    'HATTA'),
    'حَاشَا':   OperatorProfile('HASHA',    'HASHA'),
    'عَدَا':    OperatorProfile('ADA',      'ADA'),
    'خَلَا':    OperatorProfile('KHALA',    'KHALA'),

    # ── المجموعة 2: INNA_SERIES (أسرة معجمية حقيقية) ─────────────────────────
    'إِنَّ':    OperatorProfile('INNA',     'INNA_SERIES'),
    'أَنَّ':    OperatorProfile('ANNA',     'INNA_SERIES'),
    'كَأَنَّ':  OperatorProfile('KAANNA',   'INNA_SERIES'),
    'لَكِنَّ':  OperatorProfile('LAKINNA',  'INNA_SERIES'),
    'لَيْتَ':   OperatorProfile('LAYTA',    'INNA_SERIES'),
    'لَعَلَّ':  OperatorProfile('LAALLA',   'INNA_SERIES'),

    # ── المجموعة 3: النفي ─────────────────────────────────────────────────────
    'مَا':      OperatorProfile('MA',       'MA'),
    'لَا':      OperatorProfile('LA',       'LA'),   # نفي/نهي — نفس السطح

    # ── المجموعة 4: النداء والاستثناء ────────────────────────────────────────
    # وَ (عطف) موجودة أعلاه — نفس المعرِّف WA
    'إِلَّا':   OperatorProfile('ILLA',     'ILLA'),
    'يَا':      OperatorProfile('YA',       'YA'),
    'أيا':      OperatorProfile('AYA',      'AYA'),   # غير مشكول في الكتالوج
    'هيا':      OperatorProfile('HAYA',     'HAYA'),  # غير مشكول في الكتالوج
    'أي':       OperatorProfile('AY',       'AY'),    # غير مشكول في الكتالوج
    'أ':        OperatorProfile('A_NIDA',   'A_NIDA'),# غير مشكول في الكتالوج

    # ── المجموعة 5: النصب فقط (غائية ونافية) ────────────────────────────────
    'أَنْ':     OperatorProfile('AN',       'AN'),
    'لَنْ':     OperatorProfile('LAN',      'LAN'),
    'كَيْ':     OperatorProfile('KAY',      'KAY'),
    'إِذَاً':   OperatorProfile('IDHAN',    'IDHAN'),

    # ── المجموعة 6: الجزم فقط ────────────────────────────────────────────────
    'لَمْ':     OperatorProfile('LAM',      'LAM'),
    'لَمَّا':   OperatorProfile('LAMMA',    'LAMMA'),
    # لِ و لَا معرَّفتان أعلاه
    'إِنْ':     OperatorProfile('IN_SHART', 'IN_SHART'),

    # ── المجموعة 7: الشرط ────────────────────────────────────────────────────
    'مَنْ':     OperatorProfile('MAN',      'MAN'),
    'ما':       OperatorProfile('MA_COND',  'MA_COND'),   # غير مشكول — شرطية
    'أَيّ':     OperatorProfile('AYY',      'AYY'),
    'مَتَى':    OperatorProfile('MATA',     'MATA'),
    'مَهْمَا':  OperatorProfile('MAHMA',    'MAHMA'),
    'أَيْنَمَا': OperatorProfile('AYNAMA',  'AYNAMA'),
    'أنَّى':    OperatorProfile('ANNA_SHART','ANNA_SHART'),
    'حَيْثُمَا': OperatorProfile('HAYTHUMA','HAYTHUMA'),
    'إِذْمَا':  OperatorProfile('IDHMA',    'IDHMA'),
    'لو':       OperatorProfile('LAW',      'LAW'),   # غير مشكول في الكتالوج
    'إذا':      OperatorProfile('IDHA',     'IDHA'),  # غير مشكول في الكتالوج

    # ── المجموعة 8: التمييز ──────────────────────────────────────────────────
    'عَشَرَة':  OperatorProfile('ASHARA',   'ASHARA'),
    'كم':       OperatorProfile('KAM',      'KAM'),   # غير مشكول في الكتالوج
    'كأين':     OperatorProfile('KAAYYIN',  'KAAYYIN'), # غير مشكول
    'كذا':      OperatorProfile('KADHA',    'KADHA'),  # غير مشكول
    'مَائَة':   OperatorProfile('MIAA',     'MIAA'),
    'ألف':      OperatorProfile('ALF',      'ALF'),   # غير مشكول
    'ألوف':     OperatorProfile('ULUF',     'ULUF'),  # غير مشكول
    'ملايين':   OperatorProfile('MALAYIN',  'MALAYIN'),# غير مشكول
    'أيَّة':    OperatorProfile('AYYA_F',   'AYYA_F'),
    'كيت':      OperatorProfile('KAYT',     'KAYT'),  # غير مشكول
    'ذو':       OperatorProfile('DHU',      'DHU'),   # غير مشكول

    # ── المجموعة 9: الأوامر والتعجب ──────────────────────────────────────────
    'رُوَيْدَ':  OperatorProfile('RUWAYD',   'RUWAYD'),
    'بَلْهَ':   OperatorProfile('BALHA',    'BALHA'),
    'دُونَكَ':  OperatorProfile('DUNAKA',   'DUNAKA'),
    'عَلَيْكَ': OperatorProfile('ALAYKA',   'ALAYKA'),
    'هَاءَ':    OperatorProfile('HAA',      'HAA'),
    'حَيَّهَلَ': OperatorProfile('HAYYAHALA','HAYYAHALA'),
    'هَيْهَاتَ': OperatorProfile('HAYHATA', 'HAYHATA'),
    'شَتَّانَ': OperatorProfile('SHATTAN',  'SHATTAN'),
    'سُرْعَانَ': OperatorProfile('SURAAN',  'SURAAN'),

    # ── المجموعة 10: KANA_SERIES (أفعال ناقصة — أسرة معجمية حقيقية) ──────────
    'كَانَ':       OperatorProfile('KANA',      'KANA_SERIES'),
    'صَارَ':       OperatorProfile('SARA',      'KANA_SERIES'),
    'أَصْبَحَ':    OperatorProfile('ASBAHA',    'KANA_SERIES'),
    'أَمْسَى':     OperatorProfile('AMSA',      'KANA_SERIES'),
    'أَضْحَى':     OperatorProfile('ADHA',      'KANA_SERIES'),
    'ظَلَّ':       OperatorProfile('DALLA',     'KANA_SERIES'),
    'بَاتَ':       OperatorProfile('BATA',      'KANA_SERIES'),
    'مَا زَالَ':   OperatorProfile('MA_ZALA',   'KANA_SERIES'),
    'مَا بَرِحَ':  OperatorProfile('MA_BARIHA', 'KANA_SERIES'),
    'مَا فَتِئَ':  OperatorProfile('MA_FATIA',  'KANA_SERIES'),
    'مَا انْفَكَّ': OperatorProfile('MA_INFAKKA','KANA_SERIES'),
    'مَا دَامَ':   OperatorProfile('MA_DAMA',   'KANA_SERIES'),
    'لَيْسَ':      OperatorProfile('LAYSA',     'KANA_SERIES'),

    # ── المجموعة 11: APPROXIMATION_SERIES (أفعال المقاربة) ───────────────────
    'عَسَى':    OperatorProfile('ASA',      'APPROXIMATION_SERIES'),
    'كَادَ':    OperatorProfile('KADA',     'APPROXIMATION_SERIES'),
    'كَرُبَ':   OperatorProfile('KARUBA',   'APPROXIMATION_SERIES'),
    'أَوْشَكَ': OperatorProfile('AWSHAKA',  'APPROXIMATION_SERIES'),

    # ── المجموعة 12: EVALUATION_SERIES (أفعال التقييم) ──────────────────────
    'نِعْمَ':    OperatorProfile('NIMA',     'EVALUATION_SERIES'),
    'بِئْسَ':    OperatorProfile('BISA',     'EVALUATION_SERIES'),
    'سَاءَ':    OperatorProfile('SAA',      'EVALUATION_SERIES'),
    'حَبَّذَا':  OperatorProfile('HABBADHA', 'EVALUATION_SERIES'),

    # ── المجموعة 13: أفعال القلوب (غير مشكولة في الكتالوج — كل فعل هوية منفردة) ─
    'حسبت':     OperatorProfile('HASIBTU',   'HASIBTU'),
    'خلت':      OperatorProfile('KHILTU',    'KHILTU'),
    'ظننت':     OperatorProfile('ZANNANTU',  'ZANNANTU'),
    'رأيت':     OperatorProfile('RAAITU',    'RAAITU'),
    'علمت':     OperatorProfile('ALIMTU',    'ALIMTU'),
    'وجدت':     OperatorProfile('WAJADTU',   'WAJADTU'),
    'زعمت':     OperatorProfile('ZAAMTU',    'ZAAMTU'),
}


# ══════════════════════════════════════════════════════════════════════════════
# دالة الاستخراج
# ══════════════════════════════════════════════════════════════════════════════

_SHADDA = 'ّ'   # حرف الشدة — للتمييز بين إِنَّ و إِنْ


def _bare_key(s: str) -> str:
    """
    مفتاح ثانوي للبحث: الجذع العاري + علامة الشدة.

    المشكلة: الكتالوج يُخزِّن الشدة قبل الحركة (شدة + فتحة)
    بينما مفاتيح OPERATOR_PROFILE في مصدر Python مكتوبة بالترتيب العكسي
    (فتحة + شدة). الدالتان _bare_key() + _SHADDA_INDEX تحلّان هذا التعارض.

    المفتاح = الجذع العاري (بلا تشكيل) + '+' إن كانت الشدة موجودة.
    هذا يُمكِّن التمييز بين:
      إِنَّ (INNA)     → مفتاح 'إن+'
      إِنْ  (IN_SHART) → مفتاح 'إن'
      أَنَّ (ANNA)     → مفتاح 'أن+'
      أَنْ  (AN)       → مفتاح 'أن'
    """
    bare = ''.join(c for c in s if c not in _DIACRITICS)
    return bare + ('+' if _SHADDA in s else '')


# فهرس ثانوي مبني من OPERATOR_PROFILE بمفاتيح _bare_key()
# يُستخدَم عند فشل المطابقة المباشرة (بسبب اختلاف ترتيب حروف التشكيل)
_SHADDA_INDEX: dict[str, OperatorProfile] = {
    _bare_key(k): v
    for k, v in OPERATOR_PROFILE.items()
}


def _fallback_profile(matched_surface: str) -> OperatorProfile:
    """
    اشتقق هوية مستقرة للرمز غير الموجود في الخريطة الصريحة.
    نحذف التشكيل ونستخدم الجذع العربي كمعرِّف.
    الهوية ذاتية المرجع: lexical_family = operator_id.
    """
    bare = ''.join(c for c in matched_surface if c not in _DIACRITICS)
    op_id = bare if bare else 'UNKNOWN'
    return OperatorProfile(op_id, op_id)


def get_profile(matched_surface: str) -> OperatorProfile:
    """
    أعِد OperatorProfile للرمز المطابق.

    المرحلة 1: بحث مباشر في OPERATOR_PROFILE.
               يُصيب الرموز التي لا تحتوي على شدة (لا مشكلة ترتيب).
    المرحلة 2: بحث ثانوي عبر _SHADDA_INDEX بمفتاح _bare_key().
               يُصيب الرموز التي تختلف في ترتيب الشدة+الحركة بين الكتالوج والمصدر.
    المرحلة 3: هوية احتياطية مشتقة من الجذع العاري.

    Parameters:
      matched_surface — surface_vocalized من الكتالوج كما أعادته lookup_canonical()
    """
    # المرحلة 1: بحث مباشر (يُصيب الرموز بلا مشكلة ترتيب الشدة)
    if matched_surface in OPERATOR_PROFILE:
        return OPERATOR_PROFILE[matched_surface]

    # المرحلة 2: بحث ثانوي بمفتاح _bare_key (يُصيب الشدة+حركة بترتيب مختلف)
    key2 = _bare_key(matched_surface)
    if key2 in _SHADDA_INDEX:
        return _SHADDA_INDEX[key2]

    # المرحلة 3: هوية احتياطية
    return _fallback_profile(matched_surface)
