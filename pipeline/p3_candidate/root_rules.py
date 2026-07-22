#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_candidate/root_rules.py — Local Root Analysis Rules
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

نطاق هذه الدفعة (HOKOM-ROOT-OWNERSHIP):

ACCEPT:
  1. الجذر الثلاثي السالم المباشر (ض ر ب، ك ت ب).
  2. المهموز — مع توحيد الهمزة إلى ء (ق ر ء).
  3. المضعَّف — مع فك الشدة هندسيًا (م د د).
  4. المضيف المنقَّح بعد فصل اللواحق الطرفية (تَرَكَتْ → تَرَكَ → ت ر ك).

DEFER:
  5. الأجوف المفرد: ألف/واو في موضع العين (قَالَ، بَاعَ، نَامَ).
  6. الناقص: ألف/ياء في موضع اللام (دَعَا، وَقَى).
  7. المثال المؤجَّل: واو/ياء في موضع الفاء (وَجَدَ — يؤجَّل).
  8. الأمر المضغوط: حرفان فقط (قُلْ).
  9. الرباعي — خارج النطاق الحالي.

BLOCK (من directive PreRoot فقط):
  10. الأدوات والمبنيات المغلقة — PreRoot يُحدد BLOCK؛ المحرك يُمرِّره.
      القاعدة: لا يحكم المحرك BLOCK من تلقاء نفسه إلا للبنى المستحيلة (0-1 حرف).

القيود:
  - لا مسارات مطلقة.
  - لا استيراد من hr2s الداخلي.
  - لا استثناءات نصية خاصة بكلمات.
  - الشدة تُفكّ هندسيًا فقط (normalize_shadda) — لا منطق تحليلي.
  - الهمزة تُوحَّد إلى ء (normalize_hamza) — لا منطق تحليلي.
"""

from __future__ import annotations

from typing import Optional

from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda
from pipeline.p3_candidate.root_profiles import build_root_profile


# ══════════════════════════════════════════════════════════════════════════════
# 1.  الثوابت
# ══════════════════════════════════════════════════════════════════════════════

# علامات التشكيل — تُحذف عند استخراج الحروف
_DIACRITICS = frozenset('ًٌٍَُِّْٰٕٓٔ')

# الحروف الضعيفة: ألف وواو وياء وألف مقصورة — تُنتج DEFER في المواضع الجذرية
_WEAK_ALIF  = 'ا'     # الألف الممدودة (في العين = أجوف، في اللام = ناقص)
_WEAK_YAA   = 'ي'     # الياء
_WEAK_WAW   = 'و'     # الواو
_ALIF_MAQSURA = 'ى'  # الألف المقصورة (في اللام = ناقص)

# الهويات الممنوعة كحرف جذري (بعد توحيد الهمزة، لا يبقى منها إلا ا/ى)
_PROHIBITED = frozenset({"ا", "ى", "أ", "إ", "ؤ", "ئ", "آ", "?", ""})

# المجموعة الكاملة للحروف الضعيفة التي قد تظهر في العين/اللام
_WEAK_AYN   = frozenset({_WEAK_ALIF, _WEAK_WAW})   # في العين → أجوف
_WEAK_LAM   = frozenset({_WEAK_ALIF, _ALIF_MAQSURA, _WEAK_YAA})  # في اللام → ناقص
_WEAK_FA    = frozenset({_WEAK_WAW, _WEAK_YAA})     # في الفاء → مثال (مؤجَّل)

# رموز التحفظ
_RESIDUAL_HOLLOW         = 'defer:root:hollow_underlying_radical_unresolved'
_RESIDUAL_DEFECT         = 'defer:root:defective_lam_unresolved'
_RESIDUAL_ASSIMIL        = 'defer:root:assimilated_fa_unresolved'
_RESIDUAL_LAFIF_MAFRUQ   = 'defer:root:lafif_mafruq_unresolved'
_RESIDUAL_LAFIF_MAQRUN   = 'defer:root:lafif_maqrun_unresolved'
_RESIDUAL_COMPRESS       = 'defer:root:two_consonant_form_unresolved'
_RESIDUAL_QUAD           = 'defer:root:quadriliteral_beyond_scope'
_RESIDUAL_NONSTAND       = 'defer:root:non_standard_consonant_count'
_RESIDUAL_INSUFFIC       = 'block:root:insufficient_consonants'


# ══════════════════════════════════════════════════════════════════════════════
# 2.  أدوات الاستخراج
# ══════════════════════════════════════════════════════════════════════════════

def extract_consonants(text: str) -> tuple:
    """استخرج الحروف الأساسية — يُبقي على حروف المد (و/ا/ي) للكشف عن الضعف.

    لا يحذف حروف المد لأنها هوية جذرية محتملة (عين الأجوف، لام الناقص).
    """
    return tuple(ch for ch in text if ch not in _DIACRITICS and ch != ' ')


def normalize_host(host: str) -> str:
    """طبّع المضيف: توحيد الهمزة ثم توسيع الشدة (بدون تغيير آخر)."""
    return normalize_shadda(normalize_hamza(host))


# ══════════════════════════════════════════════════════════════════════════════
# 3.  التحليل الرئيسي
# ══════════════════════════════════════════════════════════════════════════════

_Result = tuple[str, Optional[tuple], str, dict]
# (directive, canonical_root | None, residual_code | '', root_profile)


def analyze_host_consonants(refined_host: str) -> _Result:
    """حلِّل مضيفًا منقَّحًا واستخرج الجذر أو سبب التأجيل.

    Parameters
    ----------
    refined_host : المضيف بعد فصل اللواحق الطرفية (مثل تَرَكَ من تَرَكَتْ).

    Returns
    -------
    (directive, canonical_root, residual_code, root_profile)
      directive:      'ACCEPT' | 'DEFER' | 'BLOCK'
      canonical_root: tuple أو None
      residual_code:  سبب DEFER/BLOCK أو '' عند ACCEPT
      root_profile:   قاموس ملف الجذر
    """
    # ── التطبيع: همزة ثم شدة ─────────────────────────────────────────────────
    normalized = normalize_host(refined_host)
    consonants = extract_consonants(normalized)
    n = len(consonants)

    # ── 0 أو 1 حرف: بنية مستحيلة → BLOCK ─────────────────────────────────────
    if n < 2:
        return 'BLOCK', None, _RESIDUAL_INSUFFIC, {}

    # ── 2 حروف: مضغوط/أجوف قُلِص → DEFER ──────────────────────────────────
    if n == 2:
        return 'DEFER', None, _RESIDUAL_COMPRESS, {}

    # ── 3 حروف: التحليل الثلاثي ──────────────────────────────────────────────
    if n == 3:
        return _analyze_trilateral(consonants)

    # ── 4 حروف: رباعي خارج النطاق → DEFER ──────────────────────────────────
    if n == 4:
        return 'DEFER', None, _RESIDUAL_QUAD, {}

    # ── 5+ حروف: غير قياسي → DEFER ──────────────────────────────────────────
    return 'DEFER', None, _RESIDUAL_NONSTAND, {}


def _analyze_trilateral(consonants: tuple) -> _Result:
    """حلِّل ثلاثية الحروف وصنِّف: سالم / مضعَّف / أجوف / ناقص / مثال / مهموز / لفيف."""
    fa, ayn, lam = consonants

    # ── كشف اللفيف أولًا: موضعان ضعيفان أو أكثر ──────────────────────────────
    # اللفيف المفروق: فاء ضعيفة + لام ضعيفة (العين صحيحة) — وَقَى، وَفَى، وَعَى
    # اللفيف المقرون: عين ضعيفة + لام ضعيفة — طَوَى، نَوَى، حَوَى، رَوَى
    fa_weak  = fa  in _WEAK_FA
    ayn_weak = ayn in _WEAK_AYN
    lam_weak = lam in _WEAK_LAM

    if fa_weak and lam_weak and not ayn_weak:
        # لفيف مفروق: الفاء والّلام ضعيفتان، العين صحيحة
        return 'DEFER', None, _RESIDUAL_LAFIF_MAFRUQ, {}

    if ayn_weak and lam_weak:
        # لفيف مقرون: العين والّلام ضعيفتان (سواء كانت الفاء ضعيفة أم لا)
        return 'DEFER', None, _RESIDUAL_LAFIF_MAQRUN, {}

    # ── أجوف: ألف أو واو في العين (بعد استبعاد اللفيف) ─────────────────────
    # قَالَ (ق،ا،ل) / نَامَ (ن،ا،م) / بَاعَ (ب،ا،ع)
    if ayn_weak:
        return 'DEFER', None, _RESIDUAL_HOLLOW, {}

    # ── ناقص: ألف/ياء/ألف مقصورة في اللام (بعد استبعاد اللفيف) ─────────────
    # دَعَا (د،ع،ا) / رَمَى (ر،م،ى)
    if lam_weak:
        return 'DEFER', None, _RESIDUAL_DEFECT, {}

    # ── مثال: واو أو ياء في الفاء (مؤجَّل للمرحلة التالية) ─────────────────
    # وَجَدَ (و،ج،د) / يَسَرَ (ي،س،ر) — صحيح ومعروف لكن خارج نطاق هذه الدفعة
    if fa_weak:
        return 'DEFER', None, _RESIDUAL_ASSIMIL, {}

    # ── تحقق نهائي: لا هويات ممنوعة (لا ينبغي وصول ا/ى هنا بعد التطبيع) ────
    if any(c in _PROHIBITED for c in consonants):
        return 'DEFER', None, 'defer:root:prohibited_or_ambiguous_radical', {}

    # ── ACCEPT: سالم أو مضعَّف أو مهموز ─────────────────────────────────────
    profile = build_root_profile(consonants)
    return 'ACCEPT', consonants, '', profile
