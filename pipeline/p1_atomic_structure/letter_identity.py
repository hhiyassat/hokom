#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p1_atomic_structure/letter_identity.py — هوية الحرف والحركة
Canonical location (R-5 refactoring).

المسؤولية:
  - ثوابت الحركات (FATHA, KASRA, ...)
  - gate_character(): C / VL — دور الحرف
  - gate_diacritic(): هل الحركات مرخصة؟
  - gate_cell(): ترميز الخلية C | CV | V
  - license_phone(): تشغيل البوابات الأربع على phone واحد

يعتمد على: pipeline.p0_unicode.unicode_candidate
"""

from pipeline.p0_unicode.unicode_candidate import (
    GateResult,
    LAYER_NAMES,
    _P0_CONSONANT_CHARS,
    VOWEL_LETTERS_ALWAYS,
    VOWEL_LETTERS_COND,
    gate_unicode,
)


# ══════════════════════════════════════════════════════════════════════════════
# 1.  ثوابت الحركات
# ══════════════════════════════════════════════════════════════════════════════

FATHA    = 'َ'
DAMMA    = 'ُ'
KASRA    = 'ِ'
SUKUN    = 'ْ'
SHADDA   = 'ّ'
TANWIN_F = 'ً'
TANWIN_D = 'ٌ'
TANWIN_K = 'ٍ'

SHORT_VOWELS      = {FATHA, DAMMA, KASRA}
TANWIN            = {TANWIN_F, TANWIN_D, TANWIN_K}
LICENSED_DIACRITICS = SHORT_VOWELS | TANWIN | {SUKUN, SHADDA}


# ══════════════════════════════════════════════════════════════════════════════
# 2.  البوابة P1: Character Licensing
# ══════════════════════════════════════════════════════════════════════════════

def gate_character(char: str, diacritics: list[str]) -> GateResult:
    """P1 — Character Licensing: دور الحرف C أو VL"""
    has_short = any(d in SHORT_VOWELS | TANWIN for d in diacritics)

    if char in VOWEL_LETTERS_ALWAYS:
        return GateResult(True, 'VL', f"[{char}] → VL ثابت",
                          layer='P1', name=LAYER_NAMES['P1'])
    if char in VOWEL_LETTERS_COND:
        role = 'C' if has_short else 'VL'
        reason = 'يحمل حركة → C' if has_short else 'بلا حركة → VL'
        return GateResult(True, role, f"[{char}] {reason}",
                          layer='P1', name=LAYER_NAMES['P1'])
    if char in _P0_CONSONANT_CHARS:
        return GateResult(True, 'C', f"[{char}] → C",
                          layer='P1', name=LAYER_NAMES['P1'])
    return GateResult(False, 'BLOCK', f"[{char!r}] ✗ خارج المنظومة",
                      layer='P1', name=LAYER_NAMES['P1'])


# ══════════════════════════════════════════════════════════════════════════════
# 3.  البوابة P2: Diacritic Licensing
# ══════════════════════════════════════════════════════════════════════════════

def gate_diacritic(char: str, diacritics: list[str]) -> GateResult:
    """P2 — Diacritic Licensing: هل الحركات مرخصة؟"""
    unlicensed = [d for d in diacritics if d not in LICENSED_DIACRITICS]
    if unlicensed:
        return GateResult(False, 'BLOCK',
            f"[{char}] ✗ حركات غير مرخصة: {unlicensed}",
            layer='P2', name=LAYER_NAMES['P2'])
    if any(d in SHORT_VOWELS | TANWIN for d in diacritics):
        return GateResult(True, 'mutaharrik', f"[{char}] متحرك",
                          layer='P2', name=LAYER_NAMES['P2'])
    if SUKUN in diacritics:
        return GateResult(True, 'sakin', f"[{char}] ساكن صريح",
                          layer='P2', name=LAYER_NAMES['P2'])
    if SHADDA in diacritics:
        return GateResult(True, 'shadda', f"[{char}] مشدد",
                          layer='P2', name=LAYER_NAMES['P2'])
    return GateResult(True, 'bare', f"[{char}] ساكن ضمني",
                      layer='P2', name=LAYER_NAMES['P2'])


# ══════════════════════════════════════════════════════════════════════════════
# 4.  البوابة P3: Cell Construction
# ══════════════════════════════════════════════════════════════════════════════

def gate_cell(char_role: str, diac_role: str) -> GateResult:
    """P3 — Cell Construction: C + V → خلية CV | C | V"""
    if char_role == 'VL':
        return GateResult(True, 'V',  "→ V  (مد النواة)",
                          layer='P3', name=LAYER_NAMES['P3'])
    if char_role == 'C':
        if diac_role == 'mutaharrik':
            return GateResult(True, 'CV', "→ CV (فتح خانة)",
                              layer='P3', name=LAYER_NAMES['P3'])
        if diac_role in ('sakin', 'bare'):
            return GateResult(True, 'C',  "→ C  (كودا)",
                              layer='P3', name=LAYER_NAMES['P3'])
        if diac_role == 'shadda':
            return GateResult(True, 'CV', "→ CV (شدة → سيُوسَّع)",
                              layer='P3', name=LAYER_NAMES['P3'])
    return GateResult(False, 'BLOCK',
        f"✗ دور غير محدد [{char_role}/{diac_role}]",
        layer='P3', name=LAYER_NAMES['P3'])


# ══════════════════════════════════════════════════════════════════════════════
# 5.  تشغيل الترخيص الكامل على phone واحد
# ══════════════════════════════════════════════════════════════════════════════

def license_phone(char: str, diacritics: list[str]) -> dict:
    """
    أجرِ المراحل الأربع على حرف واحد بحركاته.
    أعِد dict يحتوي على نتيجة كل بوابة وقرار الخلية النهائي.
    """
    g1 = gate_unicode(char)
    if not g1.passed:
        return {'char': char, 'passed': False,
                'cell': 'BLOCK', 'gates': [g1], 'note': g1.note}

    g2 = gate_character(char, diacritics)
    if not g2.passed:
        return {'char': char, 'passed': False,
                'cell': 'BLOCK', 'gates': [g1, g2], 'note': g2.note}

    g3 = gate_diacritic(char, diacritics)
    if not g3.passed:
        return {'char': char, 'passed': False,
                'cell': 'BLOCK', 'gates': [g1, g2, g3], 'note': g3.note}

    g4 = gate_cell(g2.role, g3.role)
    passed = g4.passed
    return {
        'char':   char,
        'passed': passed,
        'cell':   g4.role,
        'gates':  [g1, g2, g3, g4],
        'note':   g4.note,
    }
