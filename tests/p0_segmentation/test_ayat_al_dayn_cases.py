#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_ayat_al_dayn_cases.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Targeted segmentation tests derived from Ayat al-Dayn boundary cases.

All expected values are bare (no diacritics) for robustness.

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
        request_id=f'ayat_dayn:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )


def b_bare(s):
    return bare(s) if s else None


# ─────────────────────────────────────────────────────────────────────────────
# Proclitic cases
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("surface,expected_prc,expected_art,expected_host,expected_enc", [
    # Core Ayat al-Dayn vocabulary
    ('بِدَيْنٍ',        ['ب'],      None,  'دين',    []),
    ('بِالْعَدْلِ',    ['ب'],      'ال',  'عدل',    []),
    ('وَلْيَكْتُبْ',   ['و', 'ل'], None,  'يكتب',   []),
    ('فَلْيَكْتُبْ',   ['ف', 'ل'], None,  'يكتب',   []),
    ('فَإِنْ',          ['ف'],      None,  'إن',     []),
    ('وَإِنْ',          ['و'],      None,  'إن',     []),
    ('وَلَا',           ['و'],      None,  'لا',     []),
    ('فَلَا',           ['ف'],      None,  'لا',     []),
])
def test_proclitic_cases(surface, expected_prc, expected_art, expected_host, expected_enc):
    """Core proclitic cases must segment correctly."""
    b = segment_token(make_req(surface))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED, \
        f'{surface}: expected ACCEPTED, got {b.verdict}'
    assert [bare(p) for p in b.proclitics] == expected_prc, \
        f'{surface}: proclitics {[bare(p) for p in b.proclitics]} != {expected_prc}'
    if expected_art:
        assert b.definite_article is not None, f'{surface}: expected definite article'
        assert bare(b.definite_article) == expected_art
    else:
        assert b.definite_article is None, f'{surface}: unexpected article {b.definite_article}'
    assert b_bare(b.host) == expected_host, \
        f'{surface}: host {b_bare(b.host)!r} != {expected_host!r}'
    assert [bare(e) for e in b.enclitics] == expected_enc, \
        f'{surface}: enclitics {[bare(e) for e in b.enclitics]} != {expected_enc}'


# ─────────────────────────────────────────────────────────────────────────────
# Operator + enclitic cases
# ─────────────────────────────────────────────────────────────────────────────

def test_minhu_operator_with_enclitic():
    """مِنْهُ: whole-token operator مِنْ + enclitic هُ."""
    b = segment_token(make_req('مِنْهُ'))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    assert b.host is not None, 'مِنْهُ: host must not be None'
    assert bare(b.host) == 'من', f'host={bare(b.host)!r}'
    assert len(b.enclitics) == 1
    assert bare(b.enclitics[0]) in ('ه', 'هـ')


def test_alayhim_operator_enclitic():
    """عَلَيْهِمْ: operator عَلَى + enclitic هِمْ."""
    b = segment_token(make_req('عَلَيْهِمْ'))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    # host should be the operator form
    assert b.host is not None
    # enclitics should contain the pronoun
    assert len(b.enclitics) == 1


# ─────────────────────────────────────────────────────────────────────────────
# Clitic-only cases (proclitic + enclitic, no host)
# ─────────────────────────────────────────────────────────────────────────────

def test_bikum_clitic_only():
    """بِكُمْ: preposition بِ + pronoun كُمْ — clitic-only, host=None."""
    b = segment_token(make_req('بِكُمْ'))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    assert b.host is None, f'بِكُمْ: host must be None, got {b.host!r}'
    assert b.clitic_only is True
    assert b.host_present is False
    assert len(b.proclitics) == 1
    assert bare(b.proclitics[0]) == 'ب'
    assert len(b.enclitics) == 1
    assert bare(b.enclitics[0]) == 'كم'


def test_host_not_empty_string():
    """Contract: host must never be empty string — must be None for clitic-only."""
    for surface in ['بِكُمْ', 'بِهِمْ', 'بِهَا']:
        b = segment_token(make_req(surface))
        assert b.host != '', f'{surface}: host is empty string, must be None'


# ─────────────────────────────────────────────────────────────────────────────
# Protected whole-token cases
# ─────────────────────────────────────────────────────────────────────────────

def test_wallahu_protected():
    """وَاللَّهُ: conjunction وَ + protected host اللَّهُ (no article split)."""
    b = segment_token(make_req('وَاللَّهُ'))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    # Proclitics must contain و
    assert any(bare(p) == 'و' for p in b.proclitics), \
        f'وَاللَّهُ: expected proclitic و, got {[bare(p) for p in b.proclitics]}'
    # Host must contain الله
    assert b.host is not None
    assert 'الله' in bare(b.host) or 'لله' in bare(b.host), \
        f'وَاللَّهُ: host {bare(b.host)!r} must contain الله'
    # The definite article inside اللَّهُ must NOT be separately extracted
    assert b.definite_article is None, \
        f'وَاللَّهُ: definite_article should be None (protected host), got {b.definite_article!r}'


def test_huwa_protected():
    """هُوَ: protected whole token — no decomposition."""
    b = segment_token(make_req('هُوَ'))
    assert b.host is not None
    assert bare(b.host) == 'هو'
    assert b.proclitics == ()
    assert b.enclitics == ()


def test_hadhihi_protected():
    """هَذِهِ: protected — no decomposition."""
    b = segment_token(make_req('هَذِهِ'))
    assert b.host is not None
    assert b.proclitics == ()


# ─────────────────────────────────────────────────────────────────────────────
# Definite article cases
# ─────────────────────────────────────────────────────────────────────────────

def test_alkitab_definite_article():
    """الْكِتَابُ: definite article + host, no proclitic."""
    b = segment_token(make_req('الْكِتَابُ'))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    assert b.definite_article is not None
    assert bare(b.definite_article) == 'ال'
    assert b.host is not None
    assert bare(b.host) == 'كتاب'
    assert b.proclitics == ()


def test_bi_with_article():
    """بِالْعَدْلِ: proclitic + article + host."""
    b = segment_token(make_req('بِالْعَدْلِ'))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    assert b.proclitics == ('بِ',) or bare(b.proclitics[0]) == 'ب'
    assert b.definite_article is not None
    assert b.host is not None
    assert bare(b.host) == 'عدل'


# ─────────────────────────────────────────────────────────────────────────────
# Enclitic cases
# ─────────────────────────────────────────────────────────────────────────────

def test_enclitic_standalone():
    """كَتَبَهُ: host كَتَبَ + enclitic هُ (3rd masc. singular)."""
    b = segment_token(make_req('كَتَبَهُ'))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    assert b.host is not None
    assert bare(b.host) == 'كتب'
    assert len(b.enclitics) == 1
    assert bare(b.enclitics[0]) == 'ه'


# ─────────────────────────────────────────────────────────────────────────────
# Round-trip contract
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("surface", [
    'بِدَيْنٍ', 'بِالْعَدْلِ', 'وَلْيَكْتُبْ', 'فَلْيَكْتُبْ',
    'مِنْهُ', 'فَإِنْ', 'وَإِنْ', 'وَاللَّهُ', 'كَتَبَهُ',
])
def test_roundtrip_invariant(surface):
    """Segment surfaces concatenated must equal the normalized surface."""
    b = segment_token(make_req(surface))
    assert b.roundtrip_surface == surface, \
        f'{surface}: roundtrip {b.roundtrip_surface!r} != {surface!r}'


# ─────────────────────────────────────────────────────────────────────────────
# Engine provenance
# ─────────────────────────────────────────────────────────────────────────────

def test_engine_id_in_bundle():
    """Every bundle must carry the canonical engine_id."""
    from pipeline.p0_segmentation.models import SEGMENTATION_ENGINE_ID
    b = segment_token(make_req('بِدَيْنٍ'))
    assert b.engine_id == SEGMENTATION_ENGINE_ID


def test_canonical_owner_in_bundle():
    """Every bundle must carry canonical_owner == 'HOKOM'."""
    b = segment_token(make_req('بِدَيْنٍ'))
    assert b.canonical_owner == 'HOKOM'


def test_no_hr2s_import():
    """Engine must NOT import HR2S at runtime (checks only NEW imports from this call)."""
    import sys
    before = set(sys.modules.keys())
    b = segment_token(make_req('وَلْيَكْتُبْ'))
    assert b.verdict == SegmentationVerdict.SEGMENTATION_ACCEPTED
    after = set(sys.modules.keys())
    new_mods = after - before
    hr2s_mods = {m for m in new_mods if 'hr2s' in m.lower()}
    assert not hr2s_mods, f'Engine imported HR2S at runtime: {hr2s_mods}'
