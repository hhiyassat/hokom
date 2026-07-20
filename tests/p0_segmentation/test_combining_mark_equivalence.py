#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_combining_mark_equivalence.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Unicode combining mark equivalence tests.

Arabic vowels (fatha, damma, kasra) and shadda can appear in either order
before or after each other in encoded text. NFC normalization must make
all orderings produce the same canonical form.

HOKOM-NORMALIZATION-SEGMENTATION-POST-CLOSURE-DEFECT-01
"""
import unicodedata
import pytest
from pipeline.p0_segmentation.normalization import canonical_normalize, strip_diacritics
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.engine import segment_token

FATHA  = 'َ'   # َ
DAMMA  = 'ُ'   # ُ
KASRA  = 'ِ'   # ِ
SHADDA = 'ّ'   # ّ

ARABIC_CONSONANTS = ['ب', 'ت', 'ك', 'م', 'ن', 'ل', 'ع', 'ش', 'ر', 'د']
VOWELS = [FATHA, DAMMA, KASRA]


@pytest.mark.parametrize('base,vowel', [
    (cons, v)
    for cons in ARABIC_CONSONANTS[:5]
    for v in VOWELS
])
def test_shadda_vowel_order_normalized(base, vowel):
    """consonant + vowel + shadda must equal consonant + shadda + vowel after NFC."""
    v1 = base + vowel  + SHADDA  # vowel then shadda
    v2 = base + SHADDA + vowel   # shadda then vowel
    n1 = canonical_normalize(v1)
    n2 = canonical_normalize(v2)
    assert n1 == n2, (
        f"Combining mark order matters after canonical_normalize: "
        f"{v1!r}→{n1!r} vs {v2!r}→{n2!r}"
    )


def test_lil_shahada_shadda_invariant():
    """لِلشَّهَادَةِ: different shadda orderings on shin must yield same segmentation."""
    # Standard form: shin + fatha + shadda
    surface1 = 'لِلشَّهَادَةِ'
    # Reordered: shin + shadda + fatha  (some encoders produce this)
    # Build the alternate encoding manually
    chars = list(surface1)
    # Find the fatha+shadda after shin (chars[3]=ش, chars[4]=َ, chars[5]=ّ)
    alt_chars = chars.copy()
    # Swap fatha and shadda on the shin
    if (len(alt_chars) >= 6 and
            alt_chars[4] == FATHA and alt_chars[5] == SHADDA):
        alt_chars[4] = SHADDA
        alt_chars[5] = FATHA
    surface2 = ''.join(alt_chars)

    req1 = SegmentationRequest(request_id='t1', original_surface=surface1, normalized_surface=surface1)
    req2 = SegmentationRequest(request_id='t2', original_surface=surface2, normalized_surface=surface2)
    b1 = segment_token(req1)
    b2 = segment_token(req2)

    assert strip_diacritics(b1.host or '') == strip_diacritics(b2.host or ''), (
        f"Different shadda orderings give different host: "
        f"{b1.host!r} vs {b2.host!r}"
    )
    assert b1.proclitics and b2.proclitics, (
        f"Both forms should have proclitics: {b1.proclitics} vs {b2.proclitics}"
    )


def test_allah_shadda_invariant():
    """اللَّهُ: shadda+fatha and fatha+shadda on lam must both be protected."""
    # Standard form
    surface1 = 'اللَّهُ'
    # Build alternate encoding (swap shadda and fatha on the second lam)
    chars = list(surface1)
    # Find لَّ pattern: chars[2]=ل chars[3]=َ chars[4]=ّ
    alt_chars = chars.copy()
    if len(alt_chars) >= 5 and alt_chars[3] == FATHA and alt_chars[4] == SHADDA:
        alt_chars[3] = SHADDA
        alt_chars[4] = FATHA
    surface2 = ''.join(alt_chars)

    req1 = SegmentationRequest(request_id='t1', original_surface=surface1, normalized_surface=surface1)
    req2 = SegmentationRequest(request_id='t2', original_surface=surface2, normalized_surface=surface2)
    b1 = segment_token(req1)
    b2 = segment_token(req2)

    # Both must be unsplit (protected token — no enclitics)
    assert b1.enclitics == (), f"Standard form: unexpected enclitics {b1.enclitics}"
    assert b2.enclitics == (), f"Alternate form: unexpected enclitics {b2.enclitics}"


def test_nfc_canonical_is_deterministic():
    """canonical_normalize applied to same input always yields same output."""
    tokens = ['اللَّهُ', 'لِلشَّهَادَةِ', 'الَّذِي', 'آمَنُوا']
    for t in tokens:
        r1 = canonical_normalize(t)
        r2 = canonical_normalize(t)
        assert r1 == r2, f"{t!r}: non-deterministic normalize output"
