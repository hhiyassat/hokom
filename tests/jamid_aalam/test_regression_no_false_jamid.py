"""
test_regression_no_false_jamid.py
HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01

Negative regression: these tokens must NOT get JAMID_AALAM_BOUNDARY.
The jamid layer must not falsely intercept common nouns, verbs, or adjectives.
"""
import pytest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from hokom_pipeline import hokom

# Common nouns that are NOT jawamid in the aalam catalog
NOT_JAMID_TOKENS = [
    'كَاتِبٌ',      # active participle — mutable, has root
    'مَكْتُوبٌ',    # passive participle — mutable, has root
    'يَكْتُبُ',     # verb — FI3L, has root
    'دَيْنٌ',       # common noun (debt) — NOT aalam
    'عَدْلٌ',       # common noun (justice) — NOT aalam
    'رَجُلٌ',       # common noun (man)
    'فَرَسٌ',       # common noun (horse)
    'حَجَرٌ',       # common noun (stone)
    'جَبَلٌ',       # common noun (mountain)
    'شَمْسٌ',       # common noun (sun)
    'قَمَرٌ',       # common noun (moon)
    'كِتَابٌ',      # common noun (book)
    'مَسْجِدٌ',     # common noun (mosque)
    'عِلْمٌ',       # abstract noun (knowledge)
    'قَلَمٌ',       # common noun (pen)
    'بَيْتٌ',       # common noun (house)
]


class TestNoFalseJamid:
    """Common words must not be intercepted by the jamid layer."""

    @pytest.mark.parametrize('tok', NOT_JAMID_TOKENS)
    def test_not_jamid_aalam_boundary(self, tok):
        r = hokom(tok)
        verdict = r.get('jamid_verdict')
        assert verdict != 'JAMID_AALAM_BOUNDARY', (
            f"{tok}: must NOT be JAMID_AALAM_BOUNDARY. "
            f"Got jamid_verdict={verdict!r}"
        )

    @pytest.mark.parametrize('tok', NOT_JAMID_TOKENS)
    def test_jamid_verdict_is_none(self, tok):
        r = hokom(tok)
        assert r.get('jamid_verdict') is None, (
            f"{tok}: jamid_verdict must be None for non-jawamid tokens. "
            f"Got: {r.get('jamid_verdict')!r}"
        )

    @pytest.mark.parametrize('tok', NOT_JAMID_TOKENS)
    def test_aalam_category_is_none(self, tok):
        r = hokom(tok)
        assert r.get('aalam_category') is None, (
            f"{tok}: aalam_category must be None for non-aalam tokens"
        )

    @pytest.mark.parametrize('tok', NOT_JAMID_TOKENS)
    def test_jamid_boundary_object_is_none(self, tok):
        r = hokom(tok)
        # jamid_boundary should be None OR JamidAalamOpen, never JamidAalamBoundary
        jb = r.get('jamid_boundary')
        if jb is not None:
            from pipeline.p5_lexical.jamid_aalam_boundary import JamidAalamBoundary
            assert not isinstance(jb, JamidAalamBoundary), (
                f"{tok}: jamid_boundary must not be JamidAalamBoundary"
            )

    @pytest.mark.parametrize('tok', ['كَاتِبٌ', 'يَكْتُبُ', 'دَيْنٌ', 'عَدْلٌ'])
    def test_root_path_not_closed_by_jamid(self, tok):
        """
        For common words that should go through root analysis,
        the jamid layer must not close the pre_root path.
        pre_root may or may not be None for other reasons (e.g. mabni BLOCK),
        but jamid_verdict must not be the reason.
        """
        r = hokom(tok)
        assert r.get('jamid_verdict') is None, (
            f"{tok}: jamid_verdict must be None — jamid layer must not interfere "
            f"with common words that have roots"
        )


class TestNegativeLookup:
    """Direct unit-level negative tests for the jamid module."""

    def test_katib_is_open(self):
        from pipeline.p5_lexical.jamid_aalam_boundary import process_jamid_aalam, JamidAalamOpen
        r = process_jamid_aalam('كَاتِبٌ')
        assert isinstance(r, JamidAalamOpen)

    def test_yaktub_is_open(self):
        from pipeline.p5_lexical.jamid_aalam_boundary import process_jamid_aalam, JamidAalamOpen
        r = process_jamid_aalam('يَكْتُبُ')
        assert isinstance(r, JamidAalamOpen)

    def test_dayn_is_open(self):
        from pipeline.p5_lexical.jamid_aalam_boundary import process_jamid_aalam, JamidAalamOpen
        r = process_jamid_aalam('دَيْنٌ')
        assert isinstance(r, JamidAalamOpen)

    def test_adl_is_open(self):
        from pipeline.p5_lexical.jamid_aalam_boundary import process_jamid_aalam, JamidAalamOpen
        r = process_jamid_aalam('عَدْلٌ')
        assert isinstance(r, JamidAalamOpen)

    def test_hajar_is_open(self):
        from pipeline.p5_lexical.jamid_aalam_boundary import process_jamid_aalam, JamidAalamOpen
        r = process_jamid_aalam('حَجَرٌ')
        assert isinstance(r, JamidAalamOpen)

    def test_jabal_is_open(self):
        from pipeline.p5_lexical.jamid_aalam_boundary import process_jamid_aalam, JamidAalamOpen
        r = process_jamid_aalam('جَبَلٌ')
        assert isinstance(r, JamidAalamOpen)
