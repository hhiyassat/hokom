"""
tests/word_class/test_word_class_corpus.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — end-to-end corpus tests via hokom()

Each row verifies that hokom(surface) produces the expected word_class and,
where specified, the expected subclass.
"""
import pytest
from hokom_pipeline import hokom


# ── corpus ─────────────────────────────────────────────────────────────────────
# (surface, expected_word_class, expected_subclass_or_None)
CORPUS = [
    # HARF — closed function words / particles
    ('هَلْ',  'HARF', 'CLOSED_FUNCTION_WORD'),
    ('مِنْ',  'HARF', 'CLOSED_FUNCTION_WORD'),
    ('إِلَى', 'HARF', 'CLOSED_FUNCTION_WORD'),
    ('عَلَى', 'HARF', 'CLOSED_FUNCTION_WORD'),
    ('فِي',   'HARF', 'CLOSED_FUNCTION_WORD'),
    ('وَ',    'HARF', None),
    ('لَمْ',  'HARF', None),
    # ISM — pronouns (B-04)
    ('هُوَ',  'ISM',  'PRONOUN'),
    ('هِيَ',  'ISM',  'PRONOUN'),
    # ISM — demonstratives (B-04)
    ('هَذَا', 'ISM',  'DEMONSTRATIVE'),
    ('هَذِهِ', 'ISM', 'DEMONSTRATIVE'),
    # ISM — nominals via morphology path
    ('كِتَابٌ', 'ISM', None),
    ('كَاتِبٌ', 'ISM', None),
    # FI3L — past tense
    ('كَتَبَ',  'FI3L', None),
    ('كَتَبَتْ', 'FI3L', None),
    # FI3L — imperfect
    ('يَكْتُبُ', 'FI3L', None),
    ('تَكْتُبُ', 'FI3L', None),
]


@pytest.mark.parametrize('surface,expected_wc,expected_sc', CORPUS)
def test_corpus_word_class(surface, expected_wc, expected_sc):
    result = hokom(surface)
    assert result.get('word_class') == expected_wc, (
        f'{surface}: expected word_class={expected_wc!r}, '
        f'got {result.get("word_class")!r}  '
        f'(verdict={result.get("word_class_verdict")})'
    )
    if expected_sc is not None:
        assert result.get('word_class_subclass') == expected_sc, (
            f'{surface}: expected subclass={expected_sc!r}, '
            f'got {result.get("word_class_subclass")!r}'
        )


@pytest.mark.parametrize('surface,expected_wc,_', CORPUS)
def test_corpus_verdict_accepted(surface, expected_wc, _):
    result = hokom(surface)
    assert result.get('word_class_verdict') == 'WORD_CLASS_ACCEPTED', (
        f'{surface}: expected WORD_CLASS_ACCEPTED, '
        f'got {result.get("word_class_verdict")!r}'
    )
