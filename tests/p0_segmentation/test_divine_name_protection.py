#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_divine_name_protection.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

لفظ الجلالة protection tests.

All three grammatical case forms — اللَّهُ (nominative), اللَّهَ (accusative),
اللَّهِ (genitive) — must be protected from enclitic extraction.
In particular, the case vowel on ه must never be treated as part of an
attached pronoun.

Also tests the prefixed form وَاللَّهُ: only وَ splits off, the divine name
is kept whole as host.

HOKOM-NORMALIZATION-SEGMENTATION-POST-CLOSURE-DEFECT-01
"""
import pytest
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics
from pipeline.p0_segmentation.inventory import PROTECTED_WHOLE_TOKENS


def seg(s: str):
    req = SegmentationRequest(request_id=f'x:{s}', original_surface=s, normalized_surface=s)
    return segment_token(req)


# ── Inventory presence ───────────────────────────────────────────────────────

@pytest.mark.parametrize('surface', ['اللَّهُ', 'اللَّهَ', 'اللَّهِ'])
def test_divine_name_in_protected_set(surface):
    """All three case forms must be in PROTECTED_WHOLE_TOKENS or bare-lookup."""
    bare = strip_diacritics(surface)
    in_exact = surface in PROTECTED_WHOLE_TOKENS
    in_bare  = any(strip_diacritics(p) == bare for p in PROTECTED_WHOLE_TOKENS)
    assert in_exact or in_bare, (
        f"{surface!r}: not found in PROTECTED_WHOLE_TOKENS (bare={bare!r})"
    )


# ── No enclitic extraction ───────────────────────────────────────────────────

@pytest.mark.parametrize('surface', ['اللَّهُ', 'اللَّهَ', 'اللَّهِ'])
def test_divine_name_no_enclitic(surface):
    """Case vowel on هَ / هُ / هِ must NOT be extracted as attached pronoun."""
    b = seg(surface)
    assert b.enclitics == (), (
        f"{surface!r}: ha (ه) must not be extracted as enclitic, "
        f"got enclitics={b.enclitics}. "
        f"The case vowel on ه is grammatical inflection, not a pronoun."
    )


@pytest.mark.parametrize('surface', ['اللَّهُ', 'اللَّهَ', 'اللَّهِ'])
def test_divine_name_no_proclitic(surface):
    """Divine name forms must not have any proclitic extracted."""
    b = seg(surface)
    assert b.proclitics == (), (
        f"{surface!r}: must not have proclitics, got {b.proclitics}"
    )


@pytest.mark.parametrize('surface', ['اللَّهُ', 'اللَّهَ', 'اللَّهِ'])
def test_divine_name_is_host(surface):
    """The whole divine name must be the host."""
    b = seg(surface)
    assert b.host is not None, f"{surface!r}: host must not be None"
    host_bare = strip_diacritics(b.host)
    assert 'لله' in host_bare or host_bare == 'الله', (
        f"{surface!r}: host must contain لله, got {b.host!r}"
    )
    assert b.clitic_only is False


# ── Prefixed form وَاللَّهُ ──────────────────────────────────────────────────

def test_wa_allah_splits_only_wa():
    """وَاللَّهُ: conjunction وَ splits off; اللَّهُ remains as protected host."""
    b = seg('وَاللَّهُ')
    proc_bare = tuple(strip_diacritics(p) for p in b.proclitics)
    assert 'و' in proc_bare, (
        f"وَاللَّهُ: وَ should be extracted as conjunction proclitic, "
        f"got {b.proclitics}"
    )
    assert b.enclitics == (), (
        f"وَاللَّهُ: no enclitic expected, got {b.enclitics}"
    )
    host_bare = strip_diacritics(b.host or '')
    assert 'لله' in host_bare, (
        f"وَاللَّهُ: host must be اللَّهُ (bare=الله), got {b.host!r}"
    )
    assert b.clitic_only is False
