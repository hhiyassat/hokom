#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/weak_operations.py — العمليات الصرفية وقواعد السلامة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ثوابت وقواعد مشتركة لطبقة الوزن:
  - الحركات وحروف الزيادة.
  - قواعد السلامة: ا/ى لا تُقابلان هوية جذرية، والهمزة تُحفَظ كـ ء.
  - معرّفات العمليات الصرفية المرخّصة (إدغام المضاعف...).

Phase 4A لا تستعيد جذرًا مجهولًا؛ الواو/الياء الجذريتان تُؤخذان من
RootCandidate فقط. القلب/الحذف يحتاج operation مرخّصة صريحة.
"""

from __future__ import annotations

from typing import Optional


# ── حركات ─────────────────────────────────────────────────────────────────
FATHA  = "َ"  # َ
DAMMA  = "ُ"  # ُ
KASRA  = "ِ"  # ِ
SUKUN  = "ْ"  # ْ
SHADDA = "ّ"  # ّ
HAMZA  = "ء"  # ء
ALIF   = "ا"  # ا
ALIF_MAQSURA = "ى"  # ى
TAA_MARBUTA  = "ة"  # ة
TA           = "ت"  # ت
FATHATAN = "ً"  # ً
DAMMATAN = "ٌ"  # ٌ
KASRATAN = "ٍ"  # ٍ

SHORT_VOWELS = frozenset({FATHA, DAMMA, KASRA})
TANWIN       = frozenset({FATHATAN, DAMMATAN, KASRATAN})
VOWEL_MARKS  = frozenset({FATHA, DAMMA, KASRA, SUKUN})

# اسم الحركة ← الرمز، للمطابقة مع قوالب الأوزان.
VOWEL_NAME = {FATHA: "FATHA", DAMMA: "DAMMA", KASRA: "KASRA", SUKUN: "SUKUN"}


# ── حروف الزيادة (سألتمونيها) بصيغتها بعد التطبيع ────────────────────────────
# ملاحظة: الهمزات المحمولة (أ إ ؤ ئ) تُطبَّع إلى ء قبل هذه الطبقة.
ZIYADAH_LETTERS = frozenset({
    HAMZA,          # ء (بدل أ/إ/ؤ/ئ بعد التطبيع)
    ALIF,           # ا
    "و",       # و
    "ي",       # ي
    "ن",       # ن
    TA,             # ت
    "م",       # م
    "س",       # س
    "ل",       # ل
    "ه",       # ه
    ALIF_MAQSURA,   # ى
})

# ── قواعد السلامة ───────────────────────────────────────────────────────────
# ا و ى لا يجوز أن تكون هوية جذرية نهائية مقبولة.
# ء (المفردة) مسموحة كهوية جذرية — تُحفَظ كما هي (قَرَأَ → ء).
PROHIBITED_RADICAL_IDENTITIES = frozenset({
    ALIF, ALIF_MAQSURA,
    "أ", "إ", "ؤ", "ئ", "آ",  # أ إ ؤ ئ آ
    "?", "", None,
})

# صور الهمزة السطحية التي تُقابل هوية الجذر ء (allographs).
_HAMZA_ALLOGRAPHS = frozenset({HAMZA, "أ", "إ", "ؤ", "ئ", "آ"})


# ── معرّفات العمليات الصرفية المرخّصة ────────────────────────────────────────
OP_MUDAAF_GEMINATION = "op:weak:mudaaf_gemination_idghaam"   # إدغام المضاعف (مَدَّ)
OP_ZIYADAH_GEMINATION = "op:ziyadah:pattern_gemination"      # تضعيف عين الوزن (فَعَّل)


def is_prohibited_radical(identity: Optional[str]) -> bool:
    """هل الحرف ممنوع كهوية جذرية (ا/ى/همزة محمولة)؟ ء المفردة ليست ممنوعة."""
    return identity in PROHIBITED_RADICAL_IDENTITIES


def hamza_equivalent(a: Optional[str], b: Optional[str]) -> bool:
    """هل الحرفان متكافئان تحت هوية الهمزة ء؟ (allographs سطحية)."""
    if a is None or b is None:
        return False
    if a == b:
        return True
    return a in _HAMZA_ALLOGRAPHS and b in _HAMZA_ALLOGRAPHS


def letters_match(root_identity: Optional[str], surface_base: Optional[str]) -> bool:
    """هل يطابق حرف السطح هوية الحرف الجذري؟ مع تكافؤ الهمزة فقط.

    ا/ى في السطح لا تُقابل هوية جذرية مباشرة (قاعدة السلامة) — تُترك للزيادة
    أو للعمليات المرخّصة، لا للجذر.
    """
    if root_identity is None or surface_base is None:
        return False
    if is_prohibited_radical(root_identity):
        # لا يُسمح أصلًا بهوية جذرية من ا/ى.
        return False
    if root_identity == surface_base:
        return True
    return hamza_equivalent(root_identity, surface_base)


def is_ziyadah_letter(base: Optional[str]) -> bool:
    return base in ZIYADAH_LETTERS


def is_taa_marbuta(base: Optional[str]) -> bool:
    return base == TAA_MARBUTA
