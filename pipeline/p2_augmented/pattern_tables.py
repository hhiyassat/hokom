#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_augmented/pattern_tables.py — augmented form pattern definitions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

جداول الأنماط الهيكلية لأفعال المزيد (Form II–X).

كل نمط يُعرَّف بـ:
  - اسم العائلة
  - توصيف الهيكل العظمي (skeleton signature)
  - وصف حروف الزيادة
  - مثال الماضي
"""

# ── حروف الزيادة (mnemonic: سَأَلْتُمُونِيهَا) ─────────────────────────────
ZIYADAH_LETTERS = frozenset('سألتمونيها' + 'أإآءةى')

# ── حروف الهجاء الأصلية (consonant letters) ──────────────────────────────────
ARABIC_CONSONANTS = frozenset(
    'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
    'أإآءةى'
)

# ── حروف العلة كجذر (الجذر الأجوف/المعتل) ───────────────────────────────────
WEAK_ROOT_LETTERS = frozenset('وي')

# ── أشكال الألف ──────────────────────────────────────────────────────────────
ALIF_FORMS = frozenset('اأإآ')
HAMZA_ALIF_FORMS = frozenset('أإآ')   # الهمزة كزيادة (Form IV prefix)

# ── توصيفات الأنماط ───────────────────────────────────────────────────────────
#
# كل نمط: dict يصف:
#   form_family : اسم العائلة
#   min_skel    : أقل عدد حروف في الهيكل العظمي
#   max_skel    : أكثر عدد حروف
#   past_example: مثال الماضي
#   ziyadah     : وصف الزيادة
#
# الكشف الفعلي يتم في detector.py بمنطق أكثر تفصيلاً.

FORM_PATTERNS = {
    'FORM_II': {
        'form_family':   'FORM_II',
        'ziyadah':       'shadda on C2 (ain)',
        'past_example':  'فَعَّلَ',
        'past_skeleton': 'C1-(C2+shadda)-C3',
        'min_skel':      3,
        'max_skel':      3,
    },
    'FORM_III': {
        'form_family':   'FORM_III',
        'ziyadah':       'alif between C1 and C2',
        'past_example':  'فَاعَلَ',
        'past_skeleton': 'C1-alif-C2-C3',
        'min_skel':      4,
        'max_skel':      4,
    },
    'FORM_IV': {
        'form_family':   'FORM_IV',
        'ziyadah':       'initial hamza prefix',
        'past_example':  'أَفْعَلَ',
        'past_skeleton': 'hamza-C1-C2-C3',
        'min_skel':      4,
        'max_skel':      4,
    },
    'FORM_V': {
        'form_family':   'FORM_V',
        'ziyadah':       'ta prefix + shadda on C2',
        'past_example':  'تَفَعَّلَ',
        'past_skeleton': 'ta-C1-(C2+shadda)-C3',
        'min_skel':      4,
        'max_skel':      4,
    },
    'FORM_VI': {
        'form_family':   'FORM_VI',
        'ziyadah':       'ta prefix + alif between C1 and C2',
        'past_example':  'تَفَاعَلَ',
        'past_skeleton': 'ta-C1-alif-C2-C3',
        'min_skel':      5,
        'max_skel':      5,
    },
    'FORM_VII': {
        'form_family':   'FORM_VII',
        'ziyadah':       'alif+nun prefix',
        'past_example':  'اِنْفَعَلَ',
        'past_skeleton': 'alif-nun-C1-C2-C3',
        'min_skel':      5,
        'max_skel':      5,
    },
    'FORM_VIII': {
        'form_family':   'FORM_VIII',
        'ziyadah':       'ta infix between C1 and C2',
        'past_example':  'اِفْتَعَلَ',
        'past_skeleton': 'alif-C1-ta-C2-C3',
        'min_skel':      5,
        'max_skel':      5,
    },
    'FORM_IX': {
        'form_family':   'FORM_IX',
        'ziyadah':       'doubled last consonant (shadda on C3)',
        'past_example':  'اِفْعَلَّ',
        'past_skeleton': 'alif-C1-C2-(C3+shadda)',
        'min_skel':      4,
        'max_skel':      4,
    },
    'FORM_X': {
        'form_family':   'FORM_X',
        'ziyadah':       'alif+sin+ta prefix',
        'past_example':  'اِسْتَفْعَلَ',
        'past_skeleton': 'alif-sin-ta-C1-C2-C3',
        'min_skel':      6,
        'max_skel':      6,
    },
}
