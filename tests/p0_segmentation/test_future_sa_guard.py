#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_future_sa_guard.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Future particle سَ extraction guard tests.

The future particle سَ is ONLY licensed before imperfect verbs.
Imperfect verbs start with one of the 4 mudaraa' prefix letters: ي ت ن أ.
Any remainder starting with a non-mudaraa' letter must NOT trigger سَ extraction.

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


@pytest.mark.parametrize('surface,expected_host_start', [
    ('سَيَكْتُبُ', 'يكتب'),   # يَ = imperfect prefix ✓
    ('سَيَفْعَلُ', 'يفعل'),   # يَ = imperfect prefix ✓
    ('سَنَفْعَلُ', 'نفعل'),   # نَ = imperfect prefix ✓
    ('سَتَكْتُبُ', 'تكتب'),   # تَ = imperfect prefix ✓
    ('سَأَكْتُبُ', 'أكتب'),   # أَ = imperfect prefix ✓ (1st person singular)
])
def test_sa_extracted_from_imperfect(surface, expected_host_start):
    """سَ MUST be extracted when remainder starts with a mudaraa' prefix letter."""
    bundle = segment_token(_req(surface))
    has_sa = any(strip_diacritics(p) == 'س' for p in bundle.proclitics)
    assert has_sa, (
        f'{surface}: expected سَ proclitic, got proclitics={bundle.proclitics}'
    )
    host_bare = strip_diacritics(bundle.host or '')
    assert host_bare.startswith(expected_host_start), (
        f'{surface}: expected host starting with {expected_host_start!r}, '
        f'got host={bundle.host!r}'
    )


@pytest.mark.parametrize('surface', [
    'سَفِيهًا',   # nominal — فِ is not a mudaraa' prefix letter
    'سَمِعَ',     # past verb root-initial — مِ is not a mudaraa' prefix letter
    'سَبِيلٌ',   # nominal — بِ is not a mudaraa' prefix letter
    'سَعِيدٌ',   # proper name / adjective — عَ is not a mudaraa' prefix letter
    'سَلَامٌ',   # nominal — لَ is not a mudaraa' prefix letter
])
def test_sa_not_extracted_from_non_imperfect(surface):
    """سَ must NOT be extracted when remainder does not start with a mudaraa' prefix letter."""
    bundle = segment_token(_req(surface))
    has_sa = any(strip_diacritics(p) == 'س' for p in bundle.proclitics)
    assert not has_sa, (
        f'{surface}: سَ should NOT be extracted, got proclitics={bundle.proclitics}'
    )
    # Whole token must be preserved as host (no enclitic from tanwin endings)
    host_bare = strip_diacritics(bundle.host or '')
    surface_bare = strip_diacritics(surface)
    assert host_bare == surface_bare, (
        f'{surface}: host should be full token {surface_bare!r}, got {bundle.host!r}'
    )
