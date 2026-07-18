#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p0_unicode/unicode_candidate.py — P0 Unicode Candidate
Canonical location (R-5 refactoring).

المسؤولية:
  - تعريف GateResult وأسماء الطبقات LAYER_NAMES
  - مجموعات الحروف المرخصة P0
  - gate_unicode(): هل الحرف مرشح Unicode مرخص؟

يعتمد على: pipeline.p0_unicode.glyph_classification (الموقع الأصلي، لا shim)
"""

from dataclasses import dataclass

from pipeline.p0_unicode.glyph_classification import (
    BaseGlyphClass,
    classify_base_glyph,
    p0_licensed as _p0_licensed,
)


# ══════════════════════════════════════════════════════════════════════════════
# 1.  هيكل GateResult وأسماء الطبقات
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class GateResult:
    passed: bool
    role:   str    # 'C' | 'VL' | 'CV' | 'V' | 'BLOCK'
    note:   str    # وصف القرار
    layer:  str = ''   # 'P0' | 'P1' | 'P2' | 'P3'
    name:   str = ''   # 'Unicode Candidate' | 'Character Licensing' | ...

LAYER_NAMES: dict[str, str] = {
    'P0': 'Unicode Candidate',
    'P1': 'Character Licensing',
    'P2': 'Diacritic Licensing',
    'P3': 'Cell Construction',
    'P4': 'Syllable Slot Engineering',
}


# ══════════════════════════════════════════════════════════════════════════════
# 2.  مجموعات الحروف P0
# ══════════════════════════════════════════════════════════════════════════════

# DEPRECATED: use glyph_classification.p0_licensed() instead.
# Kept for backwards compatibility only — do not add to this set.
CONSONANTS_25 = {
    'ء','ب','ت','ث','ج','ح','خ',
    'د','ذ','ر','ز','س','ش','ص',
    'ض','ط','ظ','ع','غ','ف','ق',
    'ك','ل','م','ن','ه',
    'و', 'ي',
}

# P0_LICENSED_BASE_GLYPHS — المجموعة المرجعية من glyph_classification
_P0_LICENSED_BASE_GLYPHS: frozenset[BaseGlyphClass] = _p0_licensed()

# مجموعة الصوامت المسطحة — تشمل ة (إصلاح المرحلة A)
_P0_CONSONANT_CHARS = frozenset({
    'ء','ب','ة','ت','ث','ج','ح','خ',
    'د','ذ','ر','ز','س','ش','ص',
    'ض','ط','ظ','ع','غ','ف','ق',
    'ك','ل','م','ن','ه',
})

VOWEL_LETTERS_ALWAYS = {'ا', 'ى'}
VOWEL_LETTERS_COND   = {'و', 'ي'}
VOWEL_LETTERS_ALL    = VOWEL_LETTERS_ALWAYS | VOWEL_LETTERS_COND

LICENSED_CHARS = CONSONANTS_25 | VOWEL_LETTERS_ALWAYS


# ══════════════════════════════════════════════════════════════════════════════
# 3.  البوابة P0: Unicode Candidate
# ══════════════════════════════════════════════════════════════════════════════

def gate_unicode(char: str) -> GateResult:
    """
    P0 — Unicode Candidate: هل الحرف مرخص في المستوى الصوتي؟

    يُفوِّض إلى classify_base_glyph() — المرجع الوحيد.
    ة (CONSONANT_TA_MARBUTA) تجتاز. صور الهمزة قبل التطبيع تُحجب.
    """
    bc = classify_base_glyph(char)
    if bc in _P0_LICENSED_BASE_GLYPHS:
        return GateResult(True, '?', f"[{char}] ✓ ({bc.value})",
                          layer='P0', name=LAYER_NAMES['P0'])
    return GateResult(False, 'BLOCK',
        f"[{char!r}] ✗ حرف خارج المنظومة ({bc.value})",
        layer='P0', name=LAYER_NAMES['P0'])
