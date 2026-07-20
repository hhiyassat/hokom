#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_contracted_li_al_solar.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Contracted lam-preposition + definite article: solar and lunar letter cases.

In Arabic, لِ + الْ → لِلْ (or لِلـ before solar letters).
The alef of الْ is elided. The engine's Step 2.5 handles the bare لل pattern.

Contract:
- proclitic: لِ (the preposition)
- article: ل (contracted article)
- host: the noun/adjective following, WITHOUT duplicate initial consonant
- For solar letters: the host bare consonants must equal the lemma consonants
  (e.g., لِلشَّهَادَةِ → host bare شهادة, NOT شهشهادة or شش...)

HOKOM-NORMALIZATION-SEGMENTATION-POST-CLOSURE-DEFECT-01
"""
import pytest
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics


def seg(s: str):
    req = SegmentationRequest(request_id=f'x:{s}', original_surface=s, normalized_surface=s)
    return segment_token(req)


@pytest.mark.parametrize('surface,expected_host_bare', [
    # Solar letters (definite article assimilates: lam → letter of host)
    ('لِلشَّهَادَةِ',  'شهادة'),   # shin — solar
    ('لِلنَّاسِ',      'ناس'),     # nun — solar
    ('لِلرَّجُلِ',     'رجل'),     # ra — solar
    ('لِلسَّمَاءِ',    'سماء'),    # sin — solar
    # Lunar letters (article lam stays: no assimilation shadda on host)
    ('لِلْكِتَابِ',    'كتاب'),    # kaf — lunar
    ('لِلْعَدْلِ',     'عدل'),     # ayn — lunar
    ('لِلْمُسْلِمِينَ', 'مسلمين'), # mim — lunar
])
def test_contracted_lil_host_bare(surface, expected_host_bare):
    """Host bare consonants must exactly match the lemma consonants."""
    b = seg(surface)
    proc_bare = tuple(strip_diacritics(p) for p in b.proclitics)
    assert 'ل' in proc_bare, (
        f"{surface!r}: لِ should be proclitic, got {b.proclitics}"
    )
    host_bare = strip_diacritics(b.host or '')
    assert host_bare == expected_host_bare, (
        f"{surface!r}: host={b.host!r} (bare={host_bare!r}), "
        f"expected bare={expected_host_bare!r}"
    )


@pytest.mark.parametrize('surface,first_cons', [
    ('لِلشَّهَادَةِ', 'ش'),
    ('لِلنَّاسِ',     'ن'),
    ('لِلرَّجُلِ',    'ر'),
    ('لِلْكِتَابِ',   'ك'),
])
def test_no_duplicate_initial_consonant(surface, first_cons):
    """Host must not start with a duplicated consonant (solar assimilation leak)."""
    b = seg(surface)
    host_bare = strip_diacritics(b.host or '')
    doubled = first_cons + first_cons
    assert not host_bare.startswith(doubled), (
        f"{surface!r}: duplicated initial consonant in host: {b.host!r} "
        f"(bare={host_bare!r}). Solar assimilation shadda must not cause "
        f"consonant duplication in the extracted host."
    )


def test_contracted_lil_article_present():
    """لِلشَّهَادَةِ must have a definite_article field (the contracted ل)."""
    b = seg('لِلشَّهَادَةِ')
    assert b.definite_article is not None, (
        "لِلشَّهَادَةِ: definite_article must not be None — "
        "the contracted lam-article must be recorded"
    )
    art_bare = strip_diacritics(b.definite_article)
    assert art_bare in ('ل', 'ال'), (
        f"لِلشَّهَادَةِ: unexpected article bare {art_bare!r}"
    )


def test_contracted_lil_no_enclitic():
    """لِلشَّهَادَةِ must have no enclitics extracted."""
    b = seg('لِلشَّهَادَةِ')
    assert b.enclitics == (), (
        f"لِلشَّهَادَةِ: unexpected enclitics {b.enclitics}"
    )
