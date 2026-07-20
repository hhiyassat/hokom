#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_morphology_surface_single_source.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

morphology_surface must be the single downstream host for all engines.

Contract:
- When segment_host is not None: morphology_surface == segment_host
- When segment_host is None (clitic-only): morphology_surface == None
- morphology_blocked == True iff morphology_surface is None
- No downstream engine must receive original_surface instead of
  morphology_surface when the two differ

HOKOM-NORMALIZATION-SEGMENTATION-POST-CLOSURE-DEFECT-01
"""
import pytest
from pipeline.p0_segmentation.normalization import strip_diacritics

try:
    from hokom_pipeline import hokom as _hokom
    _HOKOM_AVAILABLE = True
except Exception:
    _HOKOM_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not _HOKOM_AVAILABLE,
    reason='hokom_pipeline.hokom not importable in this environment',
)


def hokom(word):
    return _hokom(word)


@pytest.mark.parametrize('surface,expected_morph_bare', [
    ('بِدَيْنٍ',     'دين'),
    ('بِالْعَدْلِ', 'عدل'),
    ('مِنْهُ',      'من'),
])
def test_morphology_surface_is_segment_host(surface, expected_morph_bare):
    """morphology_surface must be the segment_host (not the full token)."""
    r = hokom(surface)
    ms = r.get('morphology_surface')
    assert ms is not None, (
        f"{surface!r}: morphology_surface is None — "
        f"segment must have found a lexical host"
    )
    ms_bare = strip_diacritics(ms)
    assert ms_bare == expected_morph_bare, (
        f"{surface!r}: morphology_surface={ms!r} (bare={ms_bare!r}), "
        f"expected bare={expected_morph_bare!r}"
    )
    # Confirm it differs from full token (otherwise the test is vacuous)
    orig_bare = strip_diacritics(surface)
    assert ms_bare != orig_bare, (
        f"{surface!r}: morphology_surface equals full token — "
        f"this test requires a case where they differ"
    )


def test_clitic_only_morphology_blocked():
    """بِكُمْ: clitic-only → morphology_surface=None, morphology_blocked=True."""
    r = hokom('بِكُمْ')
    assert r.get('morphology_surface') is None, (
        f"بِكُمْ: morphology_surface must be None for clitic-only, "
        f"got {r.get('morphology_surface')!r}"
    )
    assert r.get('morphology_blocked') is True, (
        f"بِكُمْ: morphology_blocked must be True, "
        f"got {r.get('morphology_blocked')!r}"
    )
    assert r.get('segment_host') is None, (
        f"بِكُمْ: segment_host must be None, got {r.get('segment_host')!r}"
    )


def test_clitic_only_no_p5_host_equals_original():
    """When morphology_blocked, P5 must not fall back to original_surface."""
    r = hokom('بِكُمْ')
    if not r.get('morphology_blocked'):
        pytest.skip("بِكُمْ is not morphology_blocked — skip fallback check")
    orig = r.get('input_surface') or 'بِكُمْ'
    # Check any P5-like keys that might exist
    for key in r:
        if 'host' in key.lower() and 'p5' in key.lower():
            val = r[key]
            if val is not None:
                assert strip_diacritics(str(val)) != strip_diacritics(orig), (
                    f"VIOLATION: {key}={val!r} equals original_surface on "
                    f"clitic-only token {orig!r}"
                )


def test_unsplit_morphology_surface_is_full():
    """For unsplit tokens, morphology_surface == normalized form of full token."""
    r = hokom('سَفِيهًا')
    ms = r.get('morphology_surface')
    # سَفِيهًا is unsplit (no proclitic, no enclitic)
    assert ms is not None, "سَفِيهًا: morphology_surface must not be None"
    ms_bare = strip_diacritics(ms)
    assert 'سفيه' in ms_bare, (
        f"سَفِيهًا: morphology_surface={ms!r} — must contain سفيه"
    )
