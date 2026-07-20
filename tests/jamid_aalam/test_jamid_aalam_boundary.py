"""
test_jamid_aalam_boundary.py
HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01

Unit tests for the jamid_aalam_boundary module in isolation.
Tests the dataclasses, lookup, and process_jamid_aalam function directly.
"""
import pytest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from pipeline.p5_lexical.jamid_aalam_boundary import (
    process_jamid_aalam,
    JamidAalamBoundary,
    JamidAalamOpen,
    _strip_vowels_keep_shadda,
    _strip_all_diacritics,
)


# ── Normalization helpers ─────────────────────────────────────────────────────

class TestStripVowelsKeepShadda:
    def test_allah_nom(self):
        assert _strip_vowels_keep_shadda('اللَّهُ') == 'اللّه'

    def test_allah_acc(self):
        assert _strip_vowels_keep_shadda('اللَّهَ') == 'اللّه'

    def test_allah_gen(self):
        assert _strip_vowels_keep_shadda('اللَّهِ') == 'اللّه'

    def test_lillah_host(self):
        # segment_host of لِلَّهِ after proclitic stripping
        assert _strip_vowels_keep_shadda('لَّهِ') == 'لّه'

    def test_no_shadda_word(self):
        assert _strip_vowels_keep_shadda('كَاتِبٌ') == 'كاتب'

    def test_verb(self):
        assert _strip_vowels_keep_shadda('يَكْتُبُ') == 'يكتب'

    def test_preserves_shadda(self):
        # shadda must survive stripping
        result = _strip_vowels_keep_shadda('اللَّهُ')
        assert 'ّ' in result, "shadda must be preserved"


class TestStripAllDiacritics:
    def test_allah(self):
        assert _strip_all_diacritics('اللَّهُ') == 'الله'

    def test_lillah_host(self):
        assert _strip_all_diacritics('لَّهِ') == 'له'


# ── JamidAalamBoundary dataclass ─────────────────────────────────────────────

class TestJamidAalamBoundaryDataclass:
    def test_frozen(self):
        b = JamidAalamBoundary(
            input_surface='اللَّهُ', matched_bare='اللّه',
            lexical_identity='الله', jamid_category='اسم علم',
            aalam_category='divine_name',
        )
        with pytest.raises((AttributeError, TypeError)):
            b.verdict = 'SOMETHING_ELSE'

    def test_default_verdict(self):
        b = JamidAalamBoundary(
            input_surface='اللَّهُ', matched_bare='اللّه',
            lexical_identity='الله', jamid_category='اسم علم',
            aalam_category='divine_name',
        )
        assert b.verdict == 'JAMID_AALAM_BOUNDARY'

    def test_default_blocks_root(self):
        b = JamidAalamBoundary(
            input_surface='اللَّهُ', matched_bare='اللّه',
            lexical_identity='الله', jamid_category='اسم علم',
            aalam_category='divine_name',
        )
        assert b.blocks_root_path is True

    def test_default_source(self):
        b = JamidAalamBoundary(
            input_surface='اللَّهُ', matched_bare='اللّه',
            lexical_identity='الله', jamid_category='اسم علم',
            aalam_category='divine_name',
        )
        assert b.source == 'jawamid_index'

    def test_requires_root_default_false(self):
        b = JamidAalamBoundary(
            input_surface='اللَّهُ', matched_bare='اللّه',
            lexical_identity='الله', jamid_category='اسم علم',
            aalam_category='divine_name',
        )
        assert b.requires_root_pattern is False


class TestJamidAalamOpenDataclass:
    def test_default_verdict(self):
        o = JamidAalamOpen(input_surface='كَاتِبٌ')
        assert o.verdict == 'JAMID_AALAM_OPEN'

    def test_frozen(self):
        o = JamidAalamOpen(input_surface='كَاتِبٌ')
        with pytest.raises((AttributeError, TypeError)):
            o.verdict = 'X'


# ── process_jamid_aalam ───────────────────────────────────────────────────────

class TestProcessJamidAalam:
    # Allah forms — must be BOUNDARY
    @pytest.mark.parametrize('host', [
        'اللَّهُ', 'اللَّهَ', 'اللَّهِ',
    ])
    def test_allah_forms_are_boundary(self, host):
        result = process_jamid_aalam(host)
        assert isinstance(result, JamidAalamBoundary), f"{host!r} must be BOUNDARY"
        assert result.verdict == 'JAMID_AALAM_BOUNDARY'
        assert result.aalam_category == 'divine_name'
        assert result.lexical_identity == 'الله'
        assert result.jamid_category == 'اسم علم'
        assert result.blocks_root_path is True

    def test_lillah_host_is_boundary(self):
        # لِلَّهِ → segment_host = 'لَّهِ'
        result = process_jamid_aalam('لَّهِ')
        assert isinstance(result, JamidAalamBoundary)
        assert result.aalam_category == 'divine_name'
        assert result.lexical_identity == 'الله'

    # Non-jamid forms — must be OPEN
    @pytest.mark.parametrize('host', [
        'كَاتِبٌ', 'مَكْتُوبٌ', 'يَكْتُبُ', 'دَيْنٌ', 'عَدْلٌ',
        'رَجُلٌ', 'فَرَسٌ', 'حَجَرٌ',
    ])
    def test_non_jamid_forms_are_open(self, host):
        result = process_jamid_aalam(host)
        assert isinstance(result, JamidAalamOpen), f"{host!r} must be OPEN"
        assert result.verdict == 'JAMID_AALAM_OPEN'

    def test_empty_string(self):
        result = process_jamid_aalam('')
        assert isinstance(result, JamidAalamOpen)

    def test_idempotent(self):
        # Calling twice with same input yields same result
        r1 = process_jamid_aalam('اللَّهُ')
        r2 = process_jamid_aalam('اللَّهُ')
        assert r1.verdict == r2.verdict
        assert r1.aalam_category == r2.aalam_category

    def test_input_surface_preserved(self):
        # segment_host is never mutated
        host = 'اللَّهُ'
        result = process_jamid_aalam(host)
        assert result.input_surface == host

    def test_verdict_names_are_distinct(self):
        # JAMID_AALAM_BOUNDARY must not reuse existing route names
        b = process_jamid_aalam('اللَّهُ')
        assert b.verdict not in ('MABNI_BOUNDARY', 'OPERATOR_BOUNDARY', 'OPEN', 'BLOCK', 'DEFER')
        assert b.verdict == 'JAMID_AALAM_BOUNDARY'
