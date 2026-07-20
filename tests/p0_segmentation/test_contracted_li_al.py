#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_contracted_li_al.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Contracted لِل (lam preposition + definite article) tests.

In Arabic, لِ + الْ → لِلْ (lunar) or لِلـ (solar, with assimilation).
The alef of the definite article is elided; two consecutive lams appear.
The segmenter must recognise this and produce:
  proclitics=(لِ,), definite_article=لْ/لـ, host=<rest>

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


@pytest.mark.parametrize('surface,expected_host_bare', [
    ('لِلشَّهَادَةِ', 'شهادة'),   # solar ش — from Ayat al-Dayn (corrective case)
    ('لِلْكِتَابِ',  'كتاب'),    # lunar ك
    ('لِلرَّجُلِ',   'رجل'),     # solar ر
    ('لِلشَّمْسِ',   'شمس'),     # solar ش
    ('لِلنَّاسِ',    'ناس'),     # solar ن
    ('لِلْعَدْلِ',   'عدل'),     # lunar ع
    ('لِلْأَمْرِ',   'أمر'),     # lunar أ
])
def test_contracted_lil_splits_correctly(surface, expected_host_bare):
    """Contracted لِل must be split into lam proclitic + article + host."""
    bundle = segment_token(_req(surface))

    # Must have لِ as proclitic
    proc_bare = tuple(strip_diacritics(p) for p in bundle.proclitics)
    assert 'ل' in proc_bare, (
        f'{surface}: expected لِ proclitic, got proclitics={bundle.proclitics}'
    )

    # Must have a definite_article
    assert bundle.definite_article is not None, (
        f'{surface}: definite_article should not be None'
    )

    # Host bare must match expected
    host_bare = strip_diacritics(bundle.host or '')
    assert host_bare == expected_host_bare, (
        f'{surface}: expected host bare={expected_host_bare!r}, got {bundle.host!r}'
    )

    # The article lam should NOT appear in the host
    assert not host_bare.startswith('ل') or expected_host_bare.startswith('ل'), (
        f'{surface}: article lam leaked into host: {bundle.host!r}'
    )

    # Evidence must reference contracted article rule
    evidence_rules = [e.rule for e in bundle.evidence]
    assert any('CONTRACTED' in r for r in evidence_rules), (
        f'{surface}: no CONTRACTED evidence rule. Got: {evidence_rules}'
    )


def test_roundtrip_for_contracted_lil():
    """Contracted لِل segmentation must reconstruct the original surface."""
    for surface in ['لِلشَّهَادَةِ', 'لِلْكِتَابِ', 'لِلنَّاسِ', 'لِلْعَدْلِ']:
        bundle = segment_token(_req(surface))
        roundtrip_bare = strip_diacritics(bundle.roundtrip_surface)
        surface_bare = strip_diacritics(surface)
        assert roundtrip_bare == surface_bare, (
            f'{surface}: roundtrip failed. '
            f'Expected {surface_bare!r}, got {bundle.roundtrip_surface!r}'
        )


def test_non_contracted_lam_not_affected():
    """Tokens starting with a single لِ (not لِل) must not enter the contracted handler."""
    for surface in ['لِكِتَابٍ', 'لِرَجُلٍ', 'لِعَدْلٍ']:
        bundle = segment_token(_req(surface))
        # Should still have لِ proclitic but no contracted-article evidence
        evidence_rules = [e.rule for e in bundle.evidence]
        assert not any('CONTRACTED' in r for r in evidence_rules), (
            f'{surface}: contracted handler should NOT fire for non-لِل token. '
            f'Evidence: {evidence_rules}'
        )
