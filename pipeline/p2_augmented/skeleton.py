#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_augmented/skeleton.py — consonant skeleton extraction
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

استخلاص الهيكل العظمي (skeleton) للحروف من سطح عربي مُشكَّل.

الهيكل العظمي: قائمة من (حرف، له_شدة) حيث:
  - الحرف: حرف عربي بلا حركات
  - له_شدة: True إذا وُجدت شدة في كتلة التشكيل التالية للحرف
"""

from __future__ import annotations

# ── ثوابت يونيكود ────────────────────────────────────────────────────────────
SHADDA  = 'ّ'   # ّ
SUKUUN  = 'ْ'   # ْ
FATHA   = 'َ'   # َ
KASRA   = 'ِ'   # ِ
DAMMA   = 'ُ'   # ُ
FATHATAN = 'ً'  # ً
KASRATAN = 'ٍ'  # ٍ
DAMMATAN = 'ٌ'  # ٌ
ALIF    = 'ا'   # ا
ALIF_HAMZA_ABOVE = 'أ'  # أ
ALIF_HAMZA_BELOW = 'إ'  # إ
ALIF_MADDA       = 'آ'  # آ
ALIF_WASLA       = 'ٱ'  # ٱ (alif wasla — often used for اِ)

# جميع حروف الهجاء العربية (بما فيها الألف والهمزة وأشكالها)
ARABIC_LETTERS = frozenset(
    'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'   # حروف أصلية
    'أإآءةى'                           # أشكال الهمزة والألف والتاء المربوطة
    'ا'                           # ا
    'ٱ'                           # ٱ (alif wasla)
)

# حروف التشكيل (غير الشدة) — تُجاهَل في استخلاص الهيكل
DIACRITICS = frozenset({
    SHADDA, SUKUUN, FATHA, KASRA, DAMMA,
    FATHATAN, KASRATAN, DAMMATAN,
    'ٰ',   # ٰ superscript alif
    'ـ',   # ـ tatweel
})


# ══════════════════════════════════════════════════════════════════════════════
# الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def extract_skeleton(surface: str) -> list[tuple[str, bool]]:
    """
    استخلص الهيكل العظمي للحروف من سطح عربي مُشكَّل.

    تُعيد قائمة من (حرف، له_شدة) حيث:
      - الحرف: حرف عربي بلا أي تشكيل
      - له_شدة: True إذا احتوت كتلة التشكيل التالية على شدة (ّ)،
                أو إذا كان الحرف التالي مطابقًا (نمط التضعيف المُعيَّر: كرَّم → كَرْرَمَ)

    مثالان:
      extract_skeleton('يُعَوِّضُ')  = [('ي',F),('ع',F),('و',T),('ض',F)]  # شدة أصلية
      extract_skeleton('يُعَوْوِضُ') = [('ي',F),('ع',F),('و',T),('ض',F)]  # تعيير (doubled)
    """
    result: list[tuple[str, bool]] = []
    chars = list(surface)
    n = len(chars)
    i = 0

    while i < n:
        c = chars[i]

        if c in ARABIC_LETTERS:
            # امسح للأمام عبر كتلة التشكيل (كل شيء ليس حرفًا)
            j = i + 1
            has_shadda = False
            while j < n and chars[j] not in ARABIC_LETTERS:
                if chars[j] == SHADDA:
                    has_shadda = True
                j += 1

            # كشف التضعيف المُعيَّر: إذا كان الحرف التالي مطابقًا (normalization expands cّ → cْc)
            # مثال: وْو من يُعَوْوِضُ → حرف و مُضعَّف
            if not has_shadda and j < n and chars[j] == c:
                has_shadda = True
                # تخطَّ الحرف المكرر وكتلة تشكيله
                k = j + 1
                while k < n and chars[k] not in ARABIC_LETTERS:
                    k += 1
                j = k

            result.append((c, has_shadda))
            i = j   # انتقل إلى الحرف التالي

        elif c in DIACRITICS:
            # تشكيل لا حرف قبله (نادر) — تجاهل
            i += 1
        else:
            # أحرف أخرى (ترقيم، فراغ، ...) — تجاهل
            i += 1

    return result


def strip_diacritics(letter: str) -> str:
    """أزِل التشكيل من حرف واحد أو سلسلة قصيرة."""
    return ''.join(c for c in letter if c not in DIACRITICS)


def clean_root_letter(letter: str) -> str:
    """
    نظِّف حرف جذر: أزِل التشكيل وأعِد الحرف الأساسي.

    الهمزة على ألف (أ/إ/آ) تُحفظ كـ ء (hamza) عند الحاجة،
    لكن هنا نُعيد الحرف كما هو بلا تشكيل — القرار اللغوي
    للتعامل مع الهمزة يتم في طبقة أعلى.
    """
    return strip_diacritics(letter)


# ══════════════════════════════════════════════════════════════════════════════
# بادئات المضارع
# ══════════════════════════════════════════════════════════════════════════════

# رتِّب تنازليًا حسب الطول لضمان المطابقة الأطول أولاً
IMPERFECT_PREFIXES: list[str] = sorted(
    [
        'يُ', 'يَ', 'يِ',
        'تُ', 'تَ', 'تِ',
        'نُ', 'نَ', 'نِ',
        'أُ', 'أَ', 'أِ',
    ],
    key=len,
    reverse=True,
)


def strip_imperfect_prefix(surface: str) -> tuple[str, str | None]:
    """
    أزِل بادئة المضارع من بداية السطح.

    تُعيد (الجذع، البادئة_المُزالة_أو_None).

    ملاحظة: 'تَ' كبادئة مضارع تُزال هنا أيضًا لأنها جزء من المضارع
    في صيغة المخاطب (تَكْتُبُ) وكذلك Form V المضارع (تَتَفَعَّلُ بعد يَ).
    التمييز بين تَ-الفعلية وتَ-Form V يتم في detector.py.
    """
    for prefix in IMPERFECT_PREFIXES:
        if surface.startswith(prefix):
            return surface[len(prefix):], prefix
    return surface, None
