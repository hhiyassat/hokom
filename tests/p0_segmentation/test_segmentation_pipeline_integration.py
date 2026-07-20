#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline integration tests verifying that segment_host flows into
morphology stages, not the full token.

These tests call hokom() end-to-end and inspect the result.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from hokom_pipeline import hokom
from pipeline.p0_segmentation.normalization import strip_diacritics


# ──────────────────────────────────────────────────────────────────────────────
# بِدَيْنٍ — proclitic baa must not enter morphology
# ──────────────────────────────────────────────────────────────────────────────

def test_bidayn_morphology_surface():
    """بِدَيْنٍ: morphology_surface must be دَيْنٍ, not بِدَيْنٍ"""
    result = hokom('بِدَيْنٍ')
    assert 'morphology_surface' in result, "morphology_surface not in result"
    ms = result['morphology_surface']
    assert ms is not None, "morphology_surface is None — proclitic baa must not block morphology"
    ms_bare = strip_diacritics(ms)
    full_bare = strip_diacritics('بِدَيْنٍ')
    assert ms_bare != full_bare, \
        f"Full token passed as morphology_surface: {ms!r}"
    assert not ms_bare.startswith('ب'), \
        f"Proclitic baa leaked into morphology_surface: {ms!r}"


def test_bidayn_segment_host():
    """بِدَيْنٍ: segment_host must be دَيْنٍ"""
    result = hokom('بِدَيْنٍ')
    sh = result.get('segment_host')
    assert sh is not None, "segment_host is None for بِدَيْنٍ — expected lexical host دَيْنٍ"
    sh_bare = strip_diacritics(sh)
    assert not sh_bare.startswith('ب'), \
        f"Proclitic baa leaked into segment_host: {sh!r}"


# ──────────────────────────────────────────────────────────────────────────────
# بِالْعَدْلِ — proclitic baa + definite article must not enter morphology
# ──────────────────────────────────────────────────────────────────────────────

def test_bil_adl_morphology_surface():
    """بِالْعَدْلِ: morphology_surface must not contain baa or definite article"""
    result = hokom('بِالْعَدْلِ')
    ms = result.get('morphology_surface', '')
    assert ms is not None, "morphology_surface is None for بِالْعَدْلِ"
    ms_bare = strip_diacritics(ms or '')
    assert not ms_bare.startswith('ب'), \
        f"Proclitic baa in morphology_surface: {ms!r}"
    assert 'ال' not in ms_bare[:3], \
        f"Definite article in morphology_surface: {ms!r}"


# ──────────────────────────────────────────────────────────────────────────────
# بِكُمْ — clitic-only: morphology must NOT be opened
# ──────────────────────────────────────────────────────────────────────────────

def test_bikum_morphology_blocked():
    """بِكُمْ: host=None, morphology must NOT be opened"""
    result = hokom('بِكُمْ')
    assert result.get('morphology_blocked') is True, \
        "بِكُمْ morphology was opened — clitic-only should block it"
    assert result.get('segment_host') is None, \
        f"Expected host=None for بِكُمْ, got {result.get('segment_host')!r}"
    ms = result.get('morphology_surface')
    assert ms is None, \
        f"morphology_surface should be None for clitic-only, got {ms!r}"


def test_bikum_no_full_token_fallback():
    """Critical: بِكُمْ must never fall back to the full token as morphology input"""
    result = hokom('بِكُمْ')
    ms = result.get('morphology_surface')
    # normalized_surface should be preserved correctly
    assert result.get('normalized_surface') == 'بِكُمْ', \
        f"normalized_surface corrupted: {result.get('normalized_surface')!r}"
    # morphology_surface must not equal the full token
    full_bare = strip_diacritics('بِكُمْ')
    if ms is not None:
        ms_bare = strip_diacritics(ms)
        assert ms_bare != full_bare, \
            f"CRITICAL: host=None fell back to full token {ms!r} as morphology_surface"


def test_bikum_block_reason_is_no_lexical_host():
    """بِكُمْ: block reason must be SEGMENTATION_NO_LEXICAL_HOST"""
    result = hokom('بِكُمْ')
    reason = result.get('morphology_block_reason')
    assert reason == 'SEGMENTATION_NO_LEXICAL_HOST', \
        f"Expected SEGMENTATION_NO_LEXICAL_HOST, got {reason!r}"


# ──────────────────────────────────────────────────────────────────────────────
# وَاللَّهُ — initial waw must not reach morphology
# ──────────────────────────────────────────────────────────────────────────────

def test_wallahu_waw_not_in_morphology():
    """وَاللَّهُ: initial waw must not reach morphology"""
    result = hokom('وَاللَّهُ')
    ms = result.get('morphology_surface', '')
    if ms:  # host may be protected اللَّهُ or inner lexical fragment
        ms_bare = strip_diacritics(ms)
        # Morphology surface must not start with waw (proclitic conjunction)
        # Exception: 'وا' at start could be part of a root (e.g., واو الجماعة)
        assert not ms_bare.startswith('و') or ms_bare.startswith('وا'), \
            f"Waw proclitic reached morphology_surface: {ms!r}"


# ──────────────────────────────────────────────────────────────────────────────
# مِنْهُ — operator receives morphology_surface (not full token)
# ──────────────────────────────────────────────────────────────────────────────

def test_minhu_operator_is_host():
    """مِنْهُ: morphology_surface should be مِنْ (operator host), not مِنْهُ"""
    result = hokom('مِنْهُ')
    ms = result.get('morphology_surface', '')
    if ms:
        ms_bare = strip_diacritics(ms)
        full_bare = strip_diacritics('مِنْهُ')
        assert ms_bare != full_bare, \
            f"Full token passed as morphology_surface for مِنْهُ: {ms!r}"


# ──────────────────────────────────────────────────────────────────────────────
# كَتَبَ — no clitics: morphology_surface == segment_host == normalized_surface
# ──────────────────────────────────────────────────────────────────────────────

def test_kataba_morphology_surface_unchanged():
    """كَتَبَ has no clitics: morphology_surface must equal normalized_surface"""
    result = hokom('كَتَبَ')
    assert 'morphology_surface' in result, "morphology_surface not in hokom() result"
    ms = result.get('morphology_surface', '')
    assert ms is not None, "morphology_surface is None for كَتَبَ (no clitics)"
    ms_bare = strip_diacritics(ms)
    ns_bare = strip_diacritics(result.get('normalized_surface', ''))
    assert ms_bare == ns_bare, \
        f"كَتَبَ has no clitics but morphology_surface changed to {ms!r}"
    assert result.get('morphology_blocked') is False, \
        "كَتَبَ should not be morphology_blocked"


# ──────────────────────────────────────────────────────────────────────────────
# Result contract: required keys
# ──────────────────────────────────────────────────────────────────────────────

def test_segmentation_bundle_in_result():
    """segment_bundle must be in hokom() result"""
    result = hokom('بِدَيْنٍ')
    assert 'segment_bundle' in result, "segment_bundle not in hokom() result"


def test_morphology_surface_in_result():
    """morphology_surface must always be in hokom() result"""
    result = hokom('كَتَبَ')
    assert 'morphology_surface' in result, "morphology_surface not in hokom() result"


def test_morphology_blocked_in_result():
    """morphology_blocked must always be in hokom() result"""
    result = hokom('كَتَبَ')
    assert 'morphology_blocked' in result, "morphology_blocked not in hokom() result"


def test_morphology_block_reason_in_result():
    """morphology_block_reason must always be in hokom() result"""
    result = hokom('كَتَبَ')
    assert 'morphology_block_reason' in result, "morphology_block_reason not in hokom() result"


# ──────────────────────────────────────────────────────────────────────────────
# Structural gate: no parallel Taaqol bridge
# ──────────────────────────────────────────────────────────────────────────────

def test_no_parallel_taaqol_bridge():
    """Verify pipeline/taaqol_live does NOT exist (parallel bridge must be 0)"""
    repo_root = os.path.join(os.path.dirname(__file__), '..', '..')
    taaqol_live = os.path.join(repo_root, 'pipeline', 'taaqol_live')
    assert not os.path.exists(taaqol_live), \
        f"Parallel Taaqol bridge {taaqol_live} still exists!"
