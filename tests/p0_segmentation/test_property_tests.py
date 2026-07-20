#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_property_tests.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Property-based tests for the segmentation engine.

These tests verify structural invariants that must hold for ANY input,
without relying on specific linguistic knowledge.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import pytest
from pipeline.p0_segmentation.models import (
    SegmentationRequest,
    SegmentationVerdict,
    SEGMENTATION_ENGINE_ID,
    SEGMENTATION_CANONICAL_OWNER,
)
from pipeline.p0_segmentation.engine import segment_token
from pipeline.p0_segmentation.normalization import strip_diacritics as bare


_CORPUS = [
    # Ayat al-Dayn core vocabulary
    'بِدَيْنٍ', 'بِالْعَدْلِ', 'وَلْيَكْتُبْ', 'فَلْيَكْتُبْ',
    'مِنْهُ', 'بِكُمْ', 'وَاللَّهُ', 'فَإِنْ', 'وَإِنْ',
    # Root-initial (should not be split)
    'كَاتِبٌ', 'وَعَدَ', 'فُسُوقٌ', 'فَعَلَ', 'وَجَدَ',
    'سَأَلَ', 'لَبِسَ', 'بَابٌ',
    # Protected
    'هُوَ', 'هَذَا', 'الَّذِي',
    # Definite article
    'الْكِتَابُ', 'الْعَدْلُ', 'الْعُلَمَاءُ',
    # Operators
    'مِنَ', 'عَلَى', 'إِلَى', 'فِي',
    # Other segmented
    'وَلَا', 'فَلَا', 'وَاللَّهِ',
    # Enclitic only
    'كَتَبَهُ', 'عَلَيْهِمْ',
]


def make_req(surface: str) -> SegmentationRequest:
    return SegmentationRequest(
        request_id=f'prop:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )


class TestStructuralInvariants:
    """Every bundle must satisfy these structural invariants regardless of input."""

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_engine_id_invariant(self, surface):
        b = segment_token(make_req(surface))
        assert b.engine_id == SEGMENTATION_ENGINE_ID

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_canonical_owner_invariant(self, surface):
        b = segment_token(make_req(surface))
        assert b.canonical_owner == SEGMENTATION_CANONICAL_OWNER

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_host_not_empty_string(self, surface):
        b = segment_token(make_req(surface))
        assert b.host != '', f'{surface}: host is empty string'

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_original_surface_preserved(self, surface):
        b = segment_token(make_req(surface))
        assert b.original_surface == surface

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_verdict_is_enum(self, surface):
        b = segment_token(make_req(surface))
        assert isinstance(b.verdict, SegmentationVerdict)

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_provenance_non_empty(self, surface):
        b = segment_token(make_req(surface))
        assert b.provenance
        assert len(b.provenance) == 16  # SHA256 truncated to 16 hex chars

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_clitic_only_consistent(self, surface):
        """clitic_only must be True iff host is None and there are clitics."""
        b = segment_token(make_req(surface))
        has_clitics = len(b.proclitics) > 0 or len(b.enclitics) > 0
        if b.clitic_only:
            assert b.host is None, f'{surface}: clitic_only=True but host={b.host!r}'
            assert has_clitics, f'{surface}: clitic_only=True but no clitics'
        if b.host is None and has_clitics:
            assert b.clitic_only is True, f'{surface}: host=None with clitics but clitic_only=False'

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_host_present_consistent(self, surface):
        """host_present must equal (host is not None)."""
        b = segment_token(make_req(surface))
        assert b.host_present == (b.host is not None)

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_input_span_correct(self, surface):
        b = segment_token(make_req(surface))
        assert b.input_span == (0, len(surface))

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_contract_version(self, surface):
        b = segment_token(make_req(surface))
        assert b.contract_version == '1'

    @pytest.mark.parametrize("surface", _CORPUS)
    def test_proclitic_legal_host_or_clitic_only(self, surface):
        """If there are proclitics, there must be a legal host OR clitic_only=True."""
        from pipeline.p0_segmentation.normalization import count_arabic_consonants
        b = segment_token(make_req(surface))
        if b.proclitics:
            if b.clitic_only:
                assert b.host is None
            else:
                assert b.host is not None, \
                    f'{surface}: proclitics present but host=None and not clitic_only'
                assert count_arabic_consonants(b.host) >= 2, \
                    f'{surface}: host {b.host!r} too short after proclitic extraction'


class TestDeterminism:
    """Same input must always produce the same output."""

    @pytest.mark.parametrize("surface", ['بِدَيْنٍ', 'وَلْيَكْتُبْ', 'مِنْهُ', 'فُسُوقٌ'])
    def test_deterministic(self, surface):
        req = make_req(surface)
        b1 = segment_token(req)
        b2 = segment_token(req)
        assert b1.host == b2.host
        assert b1.proclitics == b2.proclitics
        assert b1.enclitics == b2.enclitics
        assert b1.verdict == b2.verdict
        assert b1.provenance == b2.provenance
