#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_normalization.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests for the normalization helpers.
HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import pytest
from pipeline.p0_segmentation.normalization import (
    canonical_normalize,
    strip_diacritics,
    count_arabic_consonants,
    starts_with_definite_article,
    extract_definite_article_span,
)


class TestStripDiacritics:
    def test_removes_fatha(self):
        assert strip_diacritics('كَتَبَ') == 'كتب'

    def test_removes_kasra(self):
        assert strip_diacritics('بِ') == 'ب'

    def test_removes_damma(self):
        assert strip_diacritics('كُتُبٌ') == 'كتب'

    def test_removes_sukun(self):
        assert strip_diacritics('لْ') == 'ل'

    def test_removes_shadda(self):
        assert strip_diacritics('شَدَّ') == 'شد'

    def test_removes_tanwin(self):
        assert strip_diacritics('دَيْنٍ') == 'دين'

    def test_preserves_arabic_letters(self):
        assert strip_diacritics('بدء') == 'بدء'

    def test_empty_string(self):
        assert strip_diacritics('') == ''

    def test_non_arabic_unchanged(self):
        assert strip_diacritics('hello') == 'hello'


class TestCountArabicConsonants:
    def test_basic(self):
        assert count_arabic_consonants('كتب') == 3

    def test_with_diacritics(self):
        assert count_arabic_consonants('كَتَبَ') == 3

    def test_alef_counted(self):
        assert count_arabic_consonants('الكتاب') == 6

    def test_empty(self):
        assert count_arabic_consonants('') == 0

    def test_diacritics_only(self):
        assert count_arabic_consonants('َُِ') == 0


class TestStartsWithDefiniteArticle:
    def test_with_sukun(self):
        assert starts_with_definite_article('الْكِتَابُ') is True

    def test_without_sukun(self):
        assert starts_with_definite_article('الكتاب') is True

    def test_requires_content_after(self):
        assert starts_with_definite_article('ال') is False

    def test_no_article(self):
        assert starts_with_definite_article('كتاب') is False

    def test_proclitic_only(self):
        assert starts_with_definite_article('و') is False


class TestExtractDefiniteArticleSpan:
    def test_basic_extraction(self):
        art, remainder, idx = extract_definite_article_span('الْكِتَابُ')
        assert remainder.startswith('كِ') or remainder.startswith('ك')
        assert 'ال' in strip_diacritics(art)

    def test_no_article(self):
        art, remainder, idx = extract_definite_article_span('كتاب')
        assert art == ''
        assert remainder == 'كتاب'
        assert idx == 0

    def test_roundtrip(self):
        surface = 'الْعَدْلِ'
        art, remainder, idx = extract_definite_article_span(surface)
        assert art + remainder == surface
