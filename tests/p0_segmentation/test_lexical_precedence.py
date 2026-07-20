#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_lexical_precedence.py
=================================================
Regression tests for lexical whole-token precedence in the segmenter.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01

Catalog entries in mabniyat_catalog_split_vocalized.csv must be returned as
unsplit hosts regardless of initial letters — even when those initial letters
match known proclitic operators (بِ, وَ, etc.).
"""
import pytest
from pipeline.p0_segmentation.models import SegmentationRequest, SegmentationVerdict
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics


def make_req(surface: str) -> SegmentationRequest:
    return SegmentationRequest(
        request_id=f'test:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )


# ── The three originally-failing corpus entries ───────────────────────────────

@pytest.mark.parametrize('surface', [
    'بِضْع',
    'وَشْكَانَ',
    'وَاهًا',
])
def test_mabni_catalog_not_split(surface):
    """MABNI/protected catalog entries must not be split on initial letters."""
    bundle = segment_token(make_req(surface))
    # Must be accepted
    assert bundle.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    # Must have no proclitics (whole token is host)
    assert bundle.proclitics == (), (
        f'{surface}: should have no proclitics, got {bundle.proclitics}'
    )
    # Host must be the whole token
    assert bundle.host is not None, f'{surface}: host should not be None'
    host_bare    = strip_diacritics(bundle.host)
    surface_bare = strip_diacritics(surface)
    assert host_bare == surface_bare, (
        f'{surface}: host {bundle.host!r} != surface {surface!r}'
    )
    # Evidence must cite lexical precedence
    evidence_rules = [e.rule for e in bundle.evidence]
    assert any(
        'LEXICAL' in r or 'CATALOG' in r or 'MABNI' in r or 'PROTECTED' in r
        for r in evidence_rules
    ), (
        f'{surface}: no lexical precedence evidence found. Evidence: {evidence_rules}'
    )


# ── Negative: words that must still split normally ────────────────────────────

def test_bidayn_still_splits():
    """بِدَيْنٍ must still split (not in protected catalog)."""
    bundle = segment_token(make_req('بِدَيْنٍ'))
    assert bundle.proclitics != (), 'بِدَيْنٍ should still have proclitic بِ after fix'
    assert bundle.host is not None
    assert strip_diacritics(bundle.host) == 'دين'


def test_walaktub_still_splits():
    """وَلْيَكْتُبْ must still split."""
    bundle = segment_token(make_req('وَلْيَكْتُبْ'))
    assert len(bundle.proclitics) >= 1, 'وَلْيَكْتُبْ should still split'


def test_bikum_still_clitic_only():
    """بِكُمْ must still be clitic-only."""
    bundle = segment_token(make_req('بِكُمْ'))
    assert bundle.clitic_only is True, 'بِكُمْ should still be clitic-only'
    assert bundle.host is None


def test_minhu_still_splits():
    """مِنْهُ must still have enclitic."""
    bundle = segment_token(make_req('مِنْهُ'))
    assert len(bundle.enclitics) >= 1, 'مِنْهُ should still have enclitic'


# ── Lexical initial letters are not always operators ─────────────────────────

def test_initial_waw_not_always_conjunction():
    """Lexical waw-initial words that are not in the catalog pass through normally."""
    bundle = segment_token(make_req('وَعَدَ'))
    bare = strip_diacritics(bundle.host or '')
    assert bare == 'وعد', (
        f'وَعَدَ root-initial waw was incorrectly split, host={bundle.host!r}'
    )


def test_initial_ba_not_always_preposition():
    """بِضْع is catalog-protected — initial بِ is lexical, not a preposition."""
    bundle = segment_token(make_req('بِضْع'))
    assert bundle.proclitics == ()


def test_mabni_license_survives_segmentation():
    """MABNI catalog entries survive segmentation as unsplit hosts."""
    for surface in ['بِضْع', 'وَشْكَانَ', 'وَاهًا']:
        bundle = segment_token(make_req(surface))
        assert bundle.host is not None and bundle.proclitics == (), (
            f'{surface} was split despite MABNI catalog entry'
        )
