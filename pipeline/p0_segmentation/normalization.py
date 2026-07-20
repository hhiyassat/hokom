#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p0_segmentation/normalization.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Unicode normalization helpers for the Hokom Clitic Segmenter.
Deterministic, span-preserving, non-destructive.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import unicodedata


# Arabic diacritic range: U+064B (FATHATAN) through U+065F
# Also includes U+0670 (SUPERSCRIPT ALEF) and common combining marks
_DIACRITIC_RANGE_START = 'ً'
_DIACRITIC_RANGE_END   = 'ٟ'
_SUPERSCRIPT_ALEF      = 'ٰ'


def canonical_normalize(surface: str) -> str:
    """Apply NFC normalization to Arabic surface. Preserves diacritics."""
    return unicodedata.normalize('NFC', surface)


def strip_diacritics(surface: str) -> str:
    """
    Remove Arabic diacritics for comparison purposes only.
    Does NOT modify the canonical surface; used for lookup index only.

    Removes:
    - Arabic tashkeel (U+064B–U+065F): tanwin, short vowels, sukun, shadda, etc.
    - Superscript alef (U+0670)
    """
    result = []
    for ch in surface:
        if _DIACRITIC_RANGE_START <= ch <= _DIACRITIC_RANGE_END:
            continue
        if ch == _SUPERSCRIPT_ALEF:
            continue
        result.append(ch)
    return ''.join(result)


def count_arabic_consonants(surface: str) -> int:
    """
    Count Arabic letters (non-diacritic characters) in surface.
    Includes alef, waw, ya when used as consonants/carriers.
    """
    count = 0
    for ch in surface:
        code = ord(ch)
        # Arabic letter range: U+0621–U+063A and U+0641–U+064A (base letters)
        if 0x0621 <= code <= 0x063A or 0x0641 <= code <= 0x064A:
            count += 1
    return count


def starts_with_definite_article(surface: str) -> bool:
    """
    Check if a surface starts with the definite article ال.
    Works with fully vocalized and partially vocalized surfaces.
    Requires at least 3 characters after the article (2-letter article + 1+ host).
    """
    bare = strip_diacritics(surface)
    # Must start with ال and have at least one more consonant
    return bare.startswith('ال') and len(bare) > 2


def extract_definite_article_span(surface: str) -> tuple:
    """
    Extract the definite article from the start of surface.
    Returns (article_surface, remainder_surface, article_end_index).

    Handles:
    - اَلْ, الْ, ال (with or without diacritics)
    - Connecting hamzat al-wasl on alef
    """
    bare = strip_diacritics(surface)
    if not bare.startswith('ال'):
        return ('', surface, 0)

    # Walk through the original surface character by character.
    # We need to consume exactly 2 bare letters (alef + lam) plus any diacritics.
    bare_consumed = 0
    original_idx = 0

    while original_idx < len(surface) and bare_consumed < 2:
        ch = surface[original_idx]
        if not (_DIACRITIC_RANGE_START <= ch <= _DIACRITIC_RANGE_END or
                ch == _SUPERSCRIPT_ALEF):
            bare_consumed += 1
        original_idx += 1

    # Consume any trailing diacritics on the lam (e.g., sukun الْ)
    while (original_idx < len(surface) and
           (_DIACRITIC_RANGE_START <= surface[original_idx] <= _DIACRITIC_RANGE_END or
            surface[original_idx] == _SUPERSCRIPT_ALEF)):
        original_idx += 1

    article_surface   = surface[:original_idx]
    remainder_surface = surface[original_idx:]

    return (article_surface, remainder_surface, original_idx)
