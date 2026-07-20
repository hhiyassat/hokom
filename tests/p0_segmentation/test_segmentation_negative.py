#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_segmentation_negative.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Negative corpus: tokens that must NOT produce spurious proclitics or enclitics.

These tests guard against the over-segmentation that would incorrectly
treat root-initial letters as proclitics.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import pytest
from pipeline.p0_segmentation.models import (
    SegmentationRequest,
    SegmentationVerdict,
)
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics as bare


def make_req(surface: str) -> SegmentationRequest:
    return SegmentationRequest(
        request_id=f'neg:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Root-initial letter must NOT be treated as proclitic
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("surface,root_expected", [
    # ك initial — root-initial, NOT preposition
    ('كَاتِبٌ',   'كاتب'),
    ('كَبِيرٌ',   'كبير'),
    ('كِتَابٌ',   'كتاب'),
    # ف initial — root-initial, NOT conjunction
    ('فُسُوقٌ',   'فسوق'),
    ('فَقِيرٌ',   'فقير'),
    # و initial — root-initial, NOT conjunction
    ('وَعَدَ',    'وعد'),
    ('وَجَدَ',    'وجد'),
    ('وَلَدَ',    'ولد'),
    # ل initial — root-initial, NOT preposition
    ('لَبِسَ',    'لبس'),
    ('لَعِبَ',    'لعب'),
    # س initial — root-initial, NOT future particle
    ('سَأَلَ',    'سأل'),
    ('سَمِعَ',    'سمع'),
    # ب initial — root-initial, NOT preposition (when root)
    ('بَابٌ',     'باب'),
    # فَ initial — short 3-letter root (verb past)
    ('فَعَلَ',    'فعل'),
])
def test_no_spurious_proclitic_from_root_initial(surface, root_expected):
    """Root-initial letters must NOT be extracted as proclitics."""
    b = segment_token(make_req(surface))
    assert b.verdict in (
        SegmentationVerdict.SEGMENTATION_ACCEPTED,
        SegmentationVerdict.SEGMENTATION_DEFERRED,
    ), f'{surface}: unexpected verdict {b.verdict}'

    assert b.proclitics == (), \
        f'{surface}: spurious proclitics extracted: {[bare(p) for p in b.proclitics]}'
    assert b.host is not None, f'{surface}: host is None'
    assert bare(b.host) == root_expected, \
        f'{surface}: host {bare(b.host)!r} != {root_expected!r}'


# ─────────────────────────────────────────────────────────────────────────────
# Protected whole-tokens — never decomposed
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("surface,bare_expected", [
    ('هُوَ',      'هو'),
    ('هَذَا',     'هذا'),
    ('هَذِهِ',    'هذه'),
    ('الَّذِي',   'الذي'),
    ('ذَلِكَ',    'ذلك'),
])
def test_protected_tokens_not_decomposed(surface, bare_expected):
    """Protected whole-tokens must never have proclitics split off."""
    b = segment_token(make_req(surface))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    assert b.proclitics == (), \
        f'{surface}: should not have proclitics, got {b.proclitics}'
    assert b.host is not None
    assert bare(b.host) == bare_expected, \
        f'{surface}: host {bare(b.host)!r} != {bare_expected!r}'


# ─────────────────────────────────────────────────────────────────────────────
# Inflectional suffixes — NEVER separated as enclitics
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("surface,description", [
    # واو الجماعة — must never be treated as enclitic
    ('كَتَبُوا',  'واو الجماعة فعل ماضٍ'),
    ('يَكْتُبُونَ', 'واو الجماعة مضارع مرفوع'),
    # نون النسوة — must never be treated as enclitic
    # These would appear as standalone tokens in text
])
def test_inflectional_suffixes_not_enclitics(surface, description):
    """Inflectional suffixes (واو الجماعة, etc.) must not be separated as enclitics."""
    b = segment_token(make_req(surface))
    # Should not have an enclitic that is واو or نون النسوة
    for enc in b.enclitics:
        enc_bare = bare(enc)
        assert enc_bare not in ('وا', 'ون', 'ين', 'ن'), \
            f'{surface} ({description}): inflectional suffix {enc_bare!r} wrongly treated as enclitic'


# ─────────────────────────────────────────────────────────────────────────────
# Minimum host length invariant
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("surface", [
    'كَاتِبٌ', 'كَبِيرٌ', 'فُسُوقٌ', 'وَعَدَ',
    'وَجَدَ', 'لَبِسَ', 'سَأَلَ', 'بَابٌ',
    'هُوَ', 'هَذَا', 'الَّذِي',
])
def test_no_too_short_host(surface):
    """After any segmentation, the host must have at least 2 Arabic letters."""
    b = segment_token(make_req(surface))
    if b.host is not None:
        from pipeline.p0_segmentation.normalization import count_arabic_consonants
        assert count_arabic_consonants(b.host) >= 2, \
            f'{surface}: host {b.host!r} is too short (< 2 Arabic chars)'
    if b.proclitics:
        # If there are proclitics, there must be a host OR clitic-only is True
        if not b.clitic_only:
            assert b.host is not None, \
                f'{surface}: has proclitics {b.proclitics} but host is None and not clitic_only'
