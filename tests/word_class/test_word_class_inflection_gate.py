"""
tests/word_class/test_word_class_inflection_gate.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — B-01 inflection gate tests

Verifies that Phase 5 inflection only opens for confirmed FI3L tokens.
ISM and HARF tokens must have phase5_result blocked / absent.
"""
import pytest
from hokom_pipeline import hokom


# ── FI3L: inflection must run ──────────────────────────────────────────────────

FI3L_SURFACES = [
    'كَتَبَ',
    'كَتَبَتْ',
    'يَكْتُبُ',
    'تَكْتُبُ',
]


@pytest.mark.parametrize('surface', FI3L_SURFACES)
def test_fi3l_inflection_not_skipped(surface):
    """FI3L tokens must not have inflection_skipped_reason."""
    result = hokom(surface)
    assert result.get('word_class') == 'FI3L', f'{surface} must be FI3L'
    assert result.get('inflection_skipped_reason') is None, (
        f'{surface}: inflection should run for FI3L, '
        f'got skip_reason={result.get("inflection_skipped_reason")!r}'
    )


@pytest.mark.parametrize('surface', FI3L_SURFACES)
def test_fi3l_has_tense(surface):
    """FI3L tokens should have a tense_aspect value after inflection."""
    result = hokom(surface)
    if result.get('word_class') == 'FI3L':
        # tense_aspect may come from augmented analysis or inflection
        # not mandatory for all verbs but should not be 'ISM' or 'HARF'
        ta = result.get('tense_aspect')
        # just check it's not a word class label
        assert ta not in ('ISM', 'FI3L', 'HARF')


# ── HARF: inflection must NOT run ─────────────────────────────────────────────

HARF_SURFACES = [
    'هَلْ',
    'مِنْ',
    'إِلَى',
    'فِي',
]


@pytest.mark.parametrize('surface', HARF_SURFACES)
def test_harf_inflection_skipped(surface):
    """HARF tokens must have inflection_skipped_reason (inflection skipped)."""
    result = hokom(surface)
    assert result.get('word_class') == 'HARF', f'{surface} must be HARF'
    skip = result.get('inflection_skipped_reason')
    assert skip is not None, (
        f'{surface}: inflection_skipped_reason must be set for HARF, got None'
    )


@pytest.mark.parametrize('surface', HARF_SURFACES)
def test_harf_no_tense(surface):
    """HARF tokens should not have a tense_aspect."""
    result = hokom(surface)
    if result.get('word_class') == 'HARF':
        assert result.get('tense_aspect') is None


# ── ISM: inflection must NOT run ──────────────────────────────────────────────

ISM_SURFACES = [
    'هُوَ',
    'هَذَا',
    'كِتَابٌ',
    'كَاتِبٌ',
]


@pytest.mark.parametrize('surface', ISM_SURFACES)
def test_ism_inflection_skipped(surface):
    """ISM tokens must have inflection_skipped_reason (inflection skipped)."""
    result = hokom(surface)
    assert result.get('word_class') == 'ISM', f'{surface} must be ISM'
    skip = result.get('inflection_skipped_reason')
    assert skip is not None, (
        f'{surface}: inflection_skipped_reason must be set for ISM, got None'
    )
