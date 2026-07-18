#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_candidate/root_profiles.py — Root Type Profiles
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

تصنيفات أنواع الجذور المقبولة في هذه الدفعة:

  SOUND     — ثلاثي سالم: كل حروفه صحيحة (ض ر ب، ك ت ب)
  GEMINATE  — مضعّف: فاء = عين أو عين = لام (م د د، ر د د)
  HAMZA     — مهموز: يحتوي ء في أي موضع (ق ر ء، ء م ر)

غير مدعومة في هذه الدفعة (تُعاد لمراحل لاحقة):
  HOLLOW    — أجوف: عين ضعيفة (ق و ل → قَالَ)
  DEFECTIVE — ناقص: لام ضعيفة (د ع و → دَعَا)
  ASSIMIL.  — مثال: فاء ضعيفة (و ج د → وَجَدَ)
  QUADR.    — رباعي: أربعة حروف أصلية

القيود:
  - لا استثناءات خاصة بكلمات.
  - لا بيانات معجمية — تصنيف بنيوي فقط.
"""

from __future__ import annotations

from typing import Mapping, Any


# ══════════════════════════════════════════════════════════════════════════════
# 1.  ثوابت التصنيف
# ══════════════════════════════════════════════════════════════════════════════

# نوع الجذر
ROOT_TYPE_SOUND    = 'sound'
ROOT_TYPE_GEMINATE = 'geminate'
ROOT_TYPE_HAMZA    = 'hamza'

# الحرف القوي للهمزة المعيارية
_HAMZA = 'ء'

# الحروف الصحيحة (غير الضعيفة وغير الممنوعة)
# ء مدرجة كحرف جذري صالح
_STRONG_CONSONANTS = frozenset(
    'بتثجحخدذرزسشصضطظعغفقكلمنهوي'
) | {'ء'}

# الحروف الضعيفة كهوية جذرية
_WEAK_LETTERS = frozenset({'و', 'ي', 'ا', 'ى'})


# ══════════════════════════════════════════════════════════════════════════════
# 2.  التصنيف
# ══════════════════════════════════════════════════════════════════════════════

def classify_root_type(consonants: tuple) -> str:
    """صنِّف نوع الجذر بناءً على حروفه الأصلية.

    يُستدعى فقط للجذور التي اجتازت التحقق (ACCEPT) — لا ضعيف ممنوع.

    Returns
    -------
    'sound' | 'geminate' | 'hamza'
    """
    if len(consonants) != 3:
        return ROOT_TYPE_SOUND  # احتياطي

    fa, ayn, lam = consonants

    # مهموز: أي موضع يحتوي همزة
    if _HAMZA in consonants:
        return ROOT_TYPE_HAMZA

    # مضعّف: عين = لام (النوع الأشيع) أو فاء = عين
    if ayn == lam or fa == ayn:
        return ROOT_TYPE_GEMINATE

    return ROOT_TYPE_SOUND


def build_root_profile(
    consonants: tuple,
    *,
    source_engine: str = 'HOKOM_ROOT_ENGINE',
    extra: Mapping[str, Any] | None = None,
) -> dict:
    """أنشئ قاموس ملف الجذر لنتيجة ACCEPT.

    يُضاف إلى RootResolution.root_profile.
    """
    profile: dict = {
        'root_type':    classify_root_type(consonants),
        'source_engine': source_engine,
        'radical_count': len(consonants),
    }
    if extra:
        profile.update(extra)
    return profile
