"""
tests/word_class/test_word_class_serialization.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — serialization tests

Verifies that WordClassResult.to_dict() produces the correct structure and
that the pipeline result dict contains all expected word-class keys.
"""
import pytest
from hokom_pipeline import hokom
from pipeline.word_class import classify_word_class
from pipeline.word_class.models import (
    WordClass, WordClassVerdict, LexicalSubclass,
    WordClassRequest, WordClassResult, WORD_CLASS_ENGINE_ID,
)


def _make_request(**overrides) -> WordClassRequest:
    defaults = dict(
        request_id='ser-test',
        original_surface='كَتَبَ',
        normalized_surface='كَتَبَ',
        p5_verdict='OPEN',
        p5_lexical_class='',
        operator_status=False,
        mabni_status='open',
        morphology_path='verbal_root_path',
        masdar_accepted=False,
        masdar_surface='',
        derivative_accepted=False,
        derivative_type='',
        licensed_verbal_host=False,
        bab_id='',
        form_family='',
        attachment_route='',
        attachment_notes='',
        attachment_mabni_id='',
        available_evidence=(),
        upstream_verdicts=(),
        upstream_trace=(),
    )
    defaults.update(overrides)
    return WordClassRequest(**defaults)


class TestToDict:
    def _make_fi3l_result(self) -> WordClassResult:
        return classify_word_class(_make_request(morphology_path='verbal_root_path'))

    def test_to_dict_returns_dict(self):
        res = self._make_fi3l_result()
        assert isinstance(res.to_dict(), dict)

    def test_to_dict_surface_key(self):
        res = self._make_fi3l_result()
        d = res.to_dict()
        assert 'surface' in d

    def test_to_dict_verdict_is_string(self):
        res = self._make_fi3l_result()
        d = res.to_dict()
        assert isinstance(d['verdict'], str)
        assert d['verdict'] == 'WORD_CLASS_ACCEPTED'

    def test_to_dict_word_class_is_string(self):
        res = self._make_fi3l_result()
        d = res.to_dict()
        assert isinstance(d['word_class'], str)
        assert d['word_class'] == 'FI3L'

    def test_to_dict_engine_id(self):
        res = self._make_fi3l_result()
        d = res.to_dict()
        assert d['engine_id'] == WORD_CLASS_ENGINE_ID

    def test_to_dict_reason_code_str(self):
        res = self._make_fi3l_result()
        d = res.to_dict()
        assert isinstance(d['reason_code'], str)

    def test_to_dict_primary_evidence_sequence(self):
        res = self._make_fi3l_result()
        d = res.to_dict()
        # asdict keeps tuples as tuples (Python dataclasses behaviour)
        assert isinstance(d['primary_evidence'], (list, tuple))

    def test_to_dict_candidates_sequence(self):
        res = self._make_fi3l_result()
        d = res.to_dict()
        assert isinstance(d['candidates'], (list, tuple))


class TestPipelineResultKeys:
    """Verify hokom() return dict contains the new word-class keys."""

    @pytest.mark.parametrize('surface', ['كَتَبَ', 'هَلْ', 'هُوَ'])
    def test_word_class_key_present(self, surface):
        result = hokom(surface)
        assert 'word_class' in result

    @pytest.mark.parametrize('surface', ['كَتَبَ', 'هَلْ', 'هُوَ'])
    def test_word_class_verdict_key_present(self, surface):
        result = hokom(surface)
        assert 'word_class_verdict' in result

    @pytest.mark.parametrize('surface', ['كَتَبَ', 'هَلْ', 'هُوَ'])
    def test_word_class_subclass_key_present(self, surface):
        result = hokom(surface)
        assert 'word_class_subclass' in result

    @pytest.mark.parametrize('surface', ['كَتَبَ', 'هَلْ', 'هُوَ'])
    def test_word_class_result_key_present(self, surface):
        result = hokom(surface)
        assert 'word_class_result' in result

    @pytest.mark.parametrize('surface', ['كَتَبَ', 'هَلْ', 'هُوَ'])
    def test_word_class_value_is_valid(self, surface):
        result = hokom(surface)
        wc = result.get('word_class')
        assert wc in {'ISM', 'FI3L', 'HARF', None}

    @pytest.mark.parametrize('surface', ['كَتَبَ', 'هَلْ', 'هُوَ'])
    def test_word_class_verdict_is_valid(self, surface):
        result = hokom(surface)
        v = result.get('word_class_verdict')
        valid = {
            'WORD_CLASS_ACCEPTED', 'WORD_CLASS_DEFERRED',
            'WORD_CLASS_BLOCKED', 'WORD_CLASS_RESIDUAL', None,
        }
        assert v in valid
