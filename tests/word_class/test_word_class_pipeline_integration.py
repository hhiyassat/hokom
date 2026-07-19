"""
tests/word_class/test_word_class_pipeline_integration.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — pipeline integration tests

Verifies that hokom() correctly wires the word class engine and that
downstream pipeline stages behave consistently with the word class verdict.
"""
import pytest
from hokom_pipeline import hokom


# ── sanity: hokom() runs without error ────────────────────────────────────────

class TestHokomRunsClean:
    @pytest.mark.parametrize('surface', [
        'كَتَبَ', 'يَكْتُبُ', 'كَتَبَتْ', 'تَكْتُبُ',
        'هَلْ', 'مِنْ', 'إِلَى', 'فِي', 'عَلَى',
        'هُوَ', 'هِيَ', 'هَذَا', 'هَذِهِ',
        'كِتَابٌ', 'كَاتِبٌ',
    ])
    def test_no_exception(self, surface):
        result = hokom(surface)
        assert isinstance(result, dict)

    @pytest.mark.parametrize('surface', [
        'كَتَبَ', 'هَلْ', 'هُوَ',
    ])
    def test_word_class_result_is_present(self, surface):
        result = hokom(surface)
        assert result.get('word_class_result') is not None


# ── word_class key consistency ────────────────────────────────────────────────

class TestWordClassKeyConsistency:
    def test_word_class_matches_result_object(self):
        """result['word_class'] must match result['word_class_result'].word_class.value."""
        for surface in ['كَتَبَ', 'هَلْ', 'هُوَ', 'هَذَا', 'كِتَابٌ']:
            r = hokom(surface)
            wc_str = r.get('word_class')
            wc_obj = r.get('word_class_result')
            if wc_obj is not None and wc_obj.word_class is not None:
                assert wc_str == wc_obj.word_class.value, (
                    f'{surface}: word_class key={wc_str!r} does not match '
                    f'result object word_class={wc_obj.word_class.value!r}'
                )

    def test_word_class_verdict_matches_result_object(self):
        for surface in ['كَتَبَ', 'هَلْ', 'هُوَ']:
            r = hokom(surface)
            v_str = r.get('word_class_verdict')
            wc_obj = r.get('word_class_result')
            if wc_obj is not None:
                assert v_str == wc_obj.verdict.value, (
                    f'{surface}: word_class_verdict key={v_str!r} '
                    f'!= result.verdict={wc_obj.verdict.value!r}'
                )


# ── inflection gate integration ───────────────────────────────────────────────

class TestInflectionGateIntegration:
    def test_fi3l_kataba_inflection_runs(self):
        r = hokom('كَتَبَ')
        assert r.get('word_class') == 'FI3L'
        assert r.get('inflection_skipped_reason') is None

    def test_fi3l_yaktabu_inflection_runs(self):
        r = hokom('يَكْتُبُ')
        assert r.get('word_class') == 'FI3L'
        assert r.get('inflection_skipped_reason') is None

    def test_harf_hal_inflection_skipped(self):
        r = hokom('هَلْ')
        assert r.get('word_class') == 'HARF'
        assert r.get('inflection_skipped_reason') is not None

    def test_ism_kitab_inflection_skipped(self):
        r = hokom('كِتَابٌ')
        assert r.get('word_class') == 'ISM'
        assert r.get('inflection_skipped_reason') is not None

    def test_ism_huwa_inflection_skipped(self):
        r = hokom('هُوَ')
        assert r.get('word_class') == 'ISM'
        assert r.get('inflection_skipped_reason') is not None


# ── claim adapter integration ─────────────────────────────────────────────────

class TestClaimAdapterIntegration:
    def test_bundle_builds_from_result(self):
        from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
        for surface in ['كَتَبَ', 'هَلْ', 'هُوَ']:
            r = hokom(surface)
            bundle = bundle_from_hokom_result(r)
            assert bundle is not None
            assert bundle.part_of_speech in ('ISM', 'FI3L', 'HARF')

    def test_b02_lexical_class_not_morphology_path(self):
        from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
        BAD_VALUES = {
            'verbal_root_path', 'nominal_morphology_path',
            'derived_nominal_path', 'functional_path',
            'ambiguous_morphology_path', 'no_morphology_path',
        }
        for surface in ['كَتَبَ', 'هَلْ', 'هُوَ', 'هَذَا']:
            r = hokom(surface)
            bundle = bundle_from_hokom_result(r)
            assert bundle.lexical_class not in BAD_VALUES, (
                f'{surface}: lexical_class={bundle.lexical_class!r} is a '
                'morphology_path value — B-02 violation.'
            )


# ── determinism ───────────────────────────────────────────────────────────────

class TestDeterminism:
    @pytest.mark.parametrize('surface', ['كَتَبَ', 'هَلْ', 'هُوَ', 'يَكْتُبُ'])
    def test_same_result_twice(self, surface):
        r1 = hokom(surface)
        r2 = hokom(surface)
        assert r1.get('word_class') == r2.get('word_class')
        assert r1.get('word_class_verdict') == r2.get('word_class_verdict')
        assert r1.get('word_class_subclass') == r2.get('word_class_subclass')
