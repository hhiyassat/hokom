"""
tests/word_class/test_word_class_properties.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — property / invariant tests

These tests verify structural invariants of classify_word_class() that must
hold for every possible input combination, not just specific surface forms.
"""
import pytest

from pipeline.word_class import classify_word_class
from pipeline.word_class.models import (
    WordClass, WordClassVerdict, LexicalSubclass,
    WordClassRequest, WordClassResult,
    WORD_CLASS_ENGINE_ID,
)


def _make_request(**overrides) -> WordClassRequest:
    defaults = dict(
        request_id='prop-test',
        original_surface='X',
        normalized_surface='X',
        p5_verdict='OPEN',
        p5_lexical_class='',
        operator_status=False,
        mabni_status='open',
        morphology_path='',
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


# ── invariant: engine_id always set ───────────────────────────────────────────

class TestEngineIdInvariant:
    @pytest.mark.parametrize('morphology_path', [
        '', 'verbal_root_path', 'nominal_morphology_path',
        'derived_nominal_path', 'functional_path', 'ambiguous_morphology_path',
    ])
    def test_engine_id_constant(self, morphology_path):
        res = classify_word_class(_make_request(morphology_path=morphology_path))
        assert res.engine_id == WORD_CLASS_ENGINE_ID


# ── invariant: accepted result always has word_class ──────────────────────────

class TestAcceptedHasWordClass:
    @pytest.mark.parametrize('morphology_path,expected_wc', [
        ('verbal_root_path',      WordClass.FI3L),
        ('nominal_morphology_path', WordClass.ISM),
        ('derived_nominal_path',  WordClass.ISM),
        ('functional_path',       WordClass.ISM),
    ])
    def test_accepted_has_word_class(self, morphology_path, expected_wc):
        res = classify_word_class(_make_request(morphology_path=morphology_path))
        assert res.verdict == WordClassVerdict.ACCEPTED
        assert res.word_class == expected_wc


# ── invariant: blocked result always has word_class=None ──────────────────────

class TestBlockedHasNoWordClass:
    def test_blocked_no_word_class(self):
        res = classify_word_class(_make_request(
            p5_verdict='BLOCK',
            mabni_status='blocked',
            upstream_verdicts=('BLOCK',),
        ))
        assert res.verdict == WordClassVerdict.BLOCKED
        assert res.word_class is None


# ── invariant: subclass is valid member or None ────────────────────────────────

class TestSubclassIsValidOrNone:
    @pytest.mark.parametrize('morphology_path', [
        'verbal_root_path', 'nominal_morphology_path',
        'ambiguous_morphology_path', '',
    ])
    def test_subclass_valid_or_none(self, morphology_path):
        res = classify_word_class(_make_request(morphology_path=morphology_path))
        if res.subclass is not None:
            assert isinstance(res.subclass, LexicalSubclass)


# ── invariant: reason_code always non-empty ────────────────────────────────────

class TestReasonCodeNonEmpty:
    @pytest.mark.parametrize('morphology_path', [
        '', 'verbal_root_path', 'nominal_morphology_path', 'ambiguous_morphology_path',
    ])
    def test_reason_code_set(self, morphology_path):
        res = classify_word_class(_make_request(morphology_path=morphology_path))
        assert res.reason_code != ''


# ── invariant: FI3L ∩ HARF = ∅ ────────────────────────────────────────────────

class TestMutualExclusion:
    def test_fi3l_and_harf_mutually_exclusive(self):
        """HARF operator boundary must never produce FI3L."""
        harf_res = classify_word_class(_make_request(
            p5_verdict='OPERATOR_BOUNDARY',
            p5_lexical_class='Closed Function Word',
            operator_status=True,
            mabni_status='boundary',
        ))
        verbal_res = classify_word_class(_make_request(
            morphology_path='verbal_root_path',
        ))
        assert harf_res.word_class == WordClass.HARF
        assert verbal_res.word_class == WordClass.FI3L

    def test_masdar_blocks_fi3l_on_ambiguous(self):
        """masdar_accepted on ambiguous path → ISM, not FI3L."""
        res = classify_word_class(_make_request(
            morphology_path='ambiguous_morphology_path',
            masdar_accepted=True,
            masdar_surface='كِتَابَةٌ',
        ))
        assert res.word_class != WordClass.FI3L


# ── invariant: derivative on verbal path does not imply ISM ───────────────────

class TestDerivativeOnVerbalPath:
    def test_derivative_accepted_on_verbal_path_does_not_give_ism(self):
        """
        phase4d PARTIAL_ACCEPT on a verb root enumerates theoretical derivatives
        but the token itself stays FI3L if morphology_path=verbal_root_path.
        """
        res = classify_word_class(_make_request(
            morphology_path='verbal_root_path',
            derivative_accepted=True,
            derivative_type='ISM_FA3IL',
        ))
        # Must remain FI3L — derivative listing does not re-classify the verb
        assert res.word_class == WordClass.FI3L


# ── invariant: trace is non-empty ─────────────────────────────────────────────

class TestTraceNonEmpty:
    @pytest.mark.parametrize('morphology_path', [
        'verbal_root_path', 'nominal_morphology_path', '',
    ])
    def test_trace_has_entries(self, morphology_path):
        res = classify_word_class(_make_request(morphology_path=morphology_path))
        assert len(res.trace) > 0
