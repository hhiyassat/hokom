#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_initial_waw_guard.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Initial وَ conjunction guard tests.

The conjunction وَ must only be extracted when the remainder (after potential
enclitic removal) has >= 3 Arabic consonants. This prevents root-initial وَ
from being extracted when the host would be inadequately short.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import pytest
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics


def _req(surface: str) -> SegmentationRequest:
    return SegmentationRequest(
        request_id=f'test:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )


@pytest.mark.parametrize('surface', [
    'وَعَدَ',    # root و-ع-د: remainder عَدَ = 2 consonants after و → rejected
    'وَجَدَ',    # root و-ج-د: remainder جَدَ = 2 consonants → rejected
    'وَلَدَ',    # root و-ل-د: remainder لَدَ = 2 consonants → rejected
])
def test_waw_not_extracted_from_short_remainder(surface):
    """وَ must NOT be extracted when remainder has < 3 consonants after enclitic check."""
    bundle = segment_token(_req(surface))
    assert bundle.proclitics == (), (
        f'{surface}: وَ should NOT be extracted, got {bundle.proclitics}'
    )
    host_bare = strip_diacritics(bundle.host or '')
    surface_bare = strip_diacritics(surface)
    assert host_bare == surface_bare, (
        f'{surface}: host should be full token, got {bundle.host!r}'
    )


def test_waliyyuhu_enclitic_only():
    """وَلِيُّهُ: only هُ is extracted (enclitic); وَ stays in host وَلِيُّ.

    After stripping هُ from وَلِيُّهُ, the remaining host وَلِيُّ → bare لِيُّ
    has only 2 consonants (ل ي) for the conjunction — below the 3-consonant minimum.
    Therefore وَ must NOT be extracted as a conjunction proclitic.
    """
    bundle = segment_token(_req('وَلِيُّهُ'))
    assert bundle.proclitics == (), (
        f'وَلِيُّهُ: وَ should not be proclitic, got {bundle.proclitics}'
    )
    enc_bare = tuple(strip_diacritics(e) for e in bundle.enclitics)
    assert 'ه' in enc_bare, (
        f'وَلِيُّهُ: هُ should be extracted as enclitic, got {bundle.enclitics}'
    )
    host_bare = strip_diacritics(bundle.host or '')
    assert host_bare.startswith('ولي'), (
        f'وَلِيُّهُ: host should be وَلِيُّ, got {bundle.host!r}'
    )


@pytest.mark.parametrize('surface,expected_host_contains', [
    ('وَالْكِتَابُ', 'كتاب'),   # waw + definite article + host
    ('وَأَقْوَمُ',  'اقوم'),    # waw + host starting with أ (legitimate)
    ('وَأَشْهِدُوا', 'اشهد'),   # waw + host starting with أ
])
def test_waw_extracted_from_legitimate_compounds(surface, expected_host_contains):
    """وَ MUST be extracted when the resulting host (after enclitic removal) has >= 3 consonants."""
    bundle = segment_token(_req(surface))
    has_waw = any(strip_diacritics(p) == 'و' for p in bundle.proclitics)
    assert has_waw, (
        f'{surface}: وَ should be extracted, got proclitics={bundle.proclitics}'
    )


def test_waw_with_protected_remainder():
    """وَاللَّهُ: وَ is extracted; remainder is the protected لفظ الجلالة."""
    bundle = segment_token(_req('وَاللَّهُ'))
    proc_bare = tuple(strip_diacritics(p) for p in bundle.proclitics)
    assert 'و' in proc_bare, (
        f'وَاللَّهُ: وَ should be extracted, got {bundle.proclitics}'
    )
