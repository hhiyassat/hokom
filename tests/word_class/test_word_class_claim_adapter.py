"""
tests/word_class/test_word_class_claim_adapter.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — B-02 / B-03 claim adapter tests

Verifies that bundle_from_hokom_result() derives lexical_class and
part_of_speech from the canonical word class engine result, not from
pre_root.morphology_path (B-02) or pre_root.pos (B-03).
"""
import pytest
from hokom_pipeline import hokom
from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result


# ── fixtures ────────────────────────────────────────────────────────────────────

def _bundle(surface: str):
    result = hokom(surface)
    return bundle_from_hokom_result(result)


# ── B-02: lexical_class must come from word class engine ──────────────────────

class TestB02LexicalClass:
    def test_harf_lexical_class(self):
        """هَلْ → lexical_class must be subclass, not morphology_path value."""
        bundle = _bundle('هَلْ')
        assert bundle.lexical_class == 'CLOSED_FUNCTION_WORD', (
            f'Expected CLOSED_FUNCTION_WORD, got {bundle.lexical_class!r}. '
            'B-02: lexical_class must come from word_class_result, not morphology_path.'
        )

    def test_ism_pronoun_lexical_class(self):
        bundle = _bundle('هُوَ')
        assert bundle.lexical_class == 'PRONOUN', (
            f'Expected PRONOUN, got {bundle.lexical_class!r}. B-02 violation.'
        )

    def test_ism_demonstrative_lexical_class(self):
        bundle = _bundle('هَذَا')
        assert bundle.lexical_class == 'DEMONSTRATIVE', (
            f'Expected DEMONSTRATIVE, got {bundle.lexical_class!r}. B-02 violation.'
        )

    def test_fi3l_lexical_class(self):
        bundle = _bundle('كَتَبَ')
        assert bundle.lexical_class == 'VERBAL_PAST', (
            f'Expected VERBAL_PAST, got {bundle.lexical_class!r}. B-02 violation.'
        )

    def test_lexical_class_not_morphology_path(self):
        """lexical_class must NEVER be a morphology_path value."""
        MORPHOLOGY_PATH_VALUES = {
            'verbal_root_path', 'nominal_morphology_path',
            'derived_nominal_path', 'functional_path',
            'ambiguous_morphology_path', 'no_morphology_path',
        }
        for surface in ['كَتَبَ', 'هَلْ', 'هُوَ', 'هَذَا', 'كِتَابٌ']:
            bundle = _bundle(surface)
            assert bundle.lexical_class not in MORPHOLOGY_PATH_VALUES, (
                f'{surface}: lexical_class={bundle.lexical_class!r} is a '
                'morphology_path value — B-02 violation.'
            )


# ── B-03: part_of_speech must be canonical ISM/FI3L/HARF ─────────────────────

class TestB03PartOfSpeech:
    def test_harf_part_of_speech(self):
        bundle = _bundle('هَلْ')
        assert bundle.part_of_speech == 'HARF', (
            f'Expected HARF, got {bundle.part_of_speech!r}. B-03 violation.'
        )

    def test_ism_pronoun_part_of_speech(self):
        bundle = _bundle('هُوَ')
        assert bundle.part_of_speech == 'ISM', (
            f'Expected ISM, got {bundle.part_of_speech!r}. B-03 violation.'
        )

    def test_ism_demonstrative_part_of_speech(self):
        bundle = _bundle('هَذَا')
        assert bundle.part_of_speech == 'ISM', (
            f'Expected ISM, got {bundle.part_of_speech!r}. B-03 violation.'
        )

    def test_fi3l_part_of_speech(self):
        bundle = _bundle('كَتَبَ')
        assert bundle.part_of_speech == 'FI3L', (
            f'Expected FI3L, got {bundle.part_of_speech!r}. B-03 violation.'
        )

    def test_ism_nominal_part_of_speech(self):
        bundle = _bundle('كِتَابٌ')
        assert bundle.part_of_speech == 'ISM', (
            f'Expected ISM, got {bundle.part_of_speech!r}. B-03 violation.'
        )

    @pytest.mark.parametrize('surface,expected_pos', [
        ('هَلْ',   'HARF'),
        ('مِنْ',   'HARF'),
        ('هُوَ',   'ISM'),
        ('هَذَا',  'ISM'),
        ('كَتَبَ', 'FI3L'),
        ('يَكْتُبُ', 'FI3L'),
        ('كِتَابٌ', 'ISM'),
    ])
    def test_part_of_speech_canonical(self, surface, expected_pos):
        bundle = _bundle(surface)
        assert bundle.part_of_speech == expected_pos, (
            f'{surface}: expected part_of_speech={expected_pos!r}, '
            f'got {bundle.part_of_speech!r}. B-03 violation.'
        )

    def test_part_of_speech_only_three_values(self):
        """part_of_speech must be one of ISM/FI3L/HARF or None (not a raw path)."""
        VALID = {'ISM', 'FI3L', 'HARF', None}
        for surface in ['كَتَبَ', 'هَلْ', 'هُوَ', 'هَذَا', 'كِتَابٌ', 'يَكْتُبُ']:
            bundle = _bundle(surface)
            assert bundle.part_of_speech in VALID, (
                f'{surface}: part_of_speech={bundle.part_of_speech!r} is not '
                'in {{ISM, FI3L, HARF, None}}. B-03 violation.'
            )
