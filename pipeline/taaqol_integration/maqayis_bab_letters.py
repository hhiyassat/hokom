"""
maqayis_bab_letters.py — canonical single-source Arabic letter → bab-name map.

Prior to this module the same table lived in two places:
  - maqayis_bab_corrector.py (line 50)
  - maqayis_root_registry.py  (line 87)

Both definitions were identical in content but drifted in formatting. Tests
did not import either — they either duplicated the map or exercised the
behaviour indirectly. This module is now the ONLY definition; both call sites
and tests import from here.

Covers:
  - the 28 base Arabic consonants
  - four Hamza variants (أ إ آ ؤ) normalised to their base
  - ئ → الياء and ة → التاء (surface variants observed in OCR output)
"""
from __future__ import annotations
from types import MappingProxyType


_MUTABLE: dict[str, str] = {
    'ا': 'الألف', 'ب': 'الباء', 'ت': 'التاء', 'ث': 'الثاء',
    'ج': 'الجيم', 'ح': 'الحاء', 'خ': 'الخاء', 'د': 'الدال',
    'ذ': 'الذال', 'ر': 'الراء', 'ز': 'الزاي', 'س': 'السين',
    'ش': 'الشين', 'ص': 'الصاد', 'ض': 'الضاد', 'ط': 'الطاء',
    'ظ': 'الظاء', 'ع': 'العين', 'غ': 'الغين', 'ف': 'الفاء',
    'ق': 'القاف', 'ك': 'الكاف', 'ل': 'اللام', 'م': 'الميم',
    'ن': 'النون', 'ه': 'الهاء', 'و': 'الواو', 'ي': 'الياء',
    # Variant forms observed as first radicals after Hamza normalisation
    'أ': 'الألف', 'إ': 'الألف', 'آ': 'الألف',
    'ؤ': 'الواو',
    'ئ': 'الياء',
    'ة': 'التاء',
}

#: The single canonical bab-letter map. Read-only view — attempts to mutate
#: at runtime raise TypeError. This is the ONLY definition in the codebase.
BAB_LETTER_MAP: "MappingProxyType[str, str]" = MappingProxyType(_MUTABLE)


__all__ = ["BAB_LETTER_MAP"]
