#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_madda_normalization_contract.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Alef madda (U+0622) normalization contract.

Contract: آ (U+0622) → ءَ (U+0621 + U+064E, hamza + fatha)
NOT: آ → ءَا (no bare alef inserted)
Idempotent. original_surface unchanged.

HOKOM-NORMALIZATION-SEGMENTATION-POST-CLOSURE-DEFECT-01
"""
import pytest
from pipeline.p0_segmentation.normalization import canonical_normalize, strip_diacritics

# Explicit Unicode constants to avoid RTL display confusion
ALEF_WITH_MADDA = 'آ'   # آ  ARABIC LETTER ALEF WITH MADDA ABOVE
HAMZA           = 'ء'   # ء  ARABIC LETTER HAMZA
ALEF            = 'ا'   # ا  ARABIC LETTER ALEF
FATHA           = 'َ'   # َ   ARABIC FATHA


@pytest.mark.parametrize('surface', [
    'آمَنُوا',
    'آمَنَ',
    'آثَرَ',
    'آدَمُ',
])
def test_madda_not_in_norm(surface):
    """After canonical_normalize, U+0622 (آ) must be absent."""
    norm = canonical_normalize(surface)
    assert ALEF_WITH_MADDA not in norm, (
        f"{surface!r}: madda char (U+0622) still present in {norm!r}"
    )


@pytest.mark.parametrize('surface', [
    'آمَنُوا',
    'آمَنَ',
    'آثَرَ',
    'آدَمُ',
])
def test_hamza_present_in_norm(surface):
    """After canonical_normalize, U+0621 (ء) must be present for each آ."""
    norm = canonical_normalize(surface)
    assert HAMZA in norm, (
        f"{surface!r}: hamza (U+0621) missing in {norm!r}"
    )


@pytest.mark.parametrize('surface', [
    'آمَنُوا',
    'آمَنَ',
    'آثَرَ',
    'آدَمُ',
])
def test_no_hamza_alef_sequence(surface):
    """Expansion must NOT insert a bare alef after the hamza.
    ءَا (hamza + fatha + alef) must not appear — the alef is NOT part of the expansion.
    """
    norm = canonical_normalize(surface)
    # Check for hamza immediately followed by alef (with or without fatha between)
    hamza_alef     = HAMZA + ALEF          # ءا (2-char: no fatha)
    hamza_fat_alef = HAMZA + FATHA + ALEF  # ءَا (3-char: with fatha)
    assert hamza_alef not in norm, (
        f"{surface!r}: found ءا (hamza+alef) in {norm!r} — alef must not be inserted"
    )
    assert hamza_fat_alef not in norm, (
        f"{surface!r}: found ءَا (hamza+fatha+alef) in {norm!r} — alef must not be inserted"
    )


@pytest.mark.parametrize('surface', [
    'آمَنُوا',
    'آمَنَ',
    'آثَرَ',
    'آدَمُ',
])
def test_madda_count_one_hamza_per_madda(surface):
    """Each آ must produce exactly one ء — no duplication."""
    norm = canonical_normalize(surface)
    madda_count = surface.count(ALEF_WITH_MADDA)
    hamza_count = norm.count(HAMZA)
    assert hamza_count == madda_count, (
        f"{surface!r}: {madda_count} madda chars → {hamza_count} hamzas in {norm!r}; "
        f"expected 1-to-1 correspondence"
    )


@pytest.mark.parametrize('surface', [
    'آمَنُوا',
    'آمَنَ',
    'آثَرَ',
    'آدَمُ',
])
def test_madda_idempotent(surface):
    """canonical_normalize must be idempotent: applying twice == applying once."""
    once  = canonical_normalize(surface)
    twice = canonical_normalize(once)
    assert once == twice, (
        f"{surface!r}: not idempotent: {once!r} → {twice!r}"
    )


def test_original_surface_immutable():
    """original_surface must never be mutated — canonical_normalize returns a new string."""
    surface  = 'آمَنُوا'
    original = surface  # same object
    _ = canonical_normalize(surface)
    assert surface == original, "original_surface was mutated"


def test_non_madda_tokens_unchanged():
    """Tokens without آ must be unaffected by the expansion step."""
    unchanged = [
        'كَتَبَ', 'الرَّحِيمِ', 'بِسْمِ', 'أَهْلًا',
        'إِذَا', 'هُوَ', 'اللَّهُ',
    ]
    for s in unchanged:
        norm = canonical_normalize(s)
        assert ALEF_WITH_MADDA not in norm  # none had it to begin with
        # strip_diacritics bare form should be same (آ was not present)
        assert strip_diacritics(norm) == strip_diacritics(s), (
            f"{s!r}: bare form changed unexpectedly after normalize: {norm!r}"
        )


def test_madda_expansion_hamza_then_fatha():
    """Verify the exact expansion: آ → ء + َ (not ء + any other vowel)."""
    norm = canonical_normalize('آمَنُوا')
    # The character right after ء must be fatha (U+064E)
    hamza_pos = norm.index(HAMZA)
    assert hamza_pos + 1 < len(norm), "no char after hamza"
    next_char = norm[hamza_pos + 1]
    assert next_char == FATHA, (
        f"Expected fatha (U+064E) after hamza, got {hex(ord(next_char))!r}"
    )
