"""
tests/word_class/test_word_class_engine.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — engine unit tests

Tests classify_word_class() directly by crafting WordClassRequest objects
without going through hokom().  This isolates the engine logic.
"""
import pytest

from pipeline.word_class import classify_word_class
from pipeline.word_class.models import (
    WordClass, WordClassVerdict, LexicalSubclass,
    WordClassRequest, WordClassResult,
    WORD_CLASS_ENGINE_ID,
)


# ── helpers ────────────────────────────────────────────────────────────────────

def _make_request(**overrides) -> WordClassRequest:
    defaults = dict(
        request_id='test',
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


def _classify(**overrides) -> WordClassResult:
    return classify_word_class(_make_request(**overrides))


# ── return type ────────────────────────────────────────────────────────────────

class TestReturnType:
    def test_returns_word_class_result(self):
        res = _classify()
        assert isinstance(res, WordClassResult)

    def test_engine_id_set(self):
        res = _classify()
        assert res.engine_id == WORD_CLASS_ENGINE_ID

    def test_request_id_propagated(self):
        res = _classify(request_id='req-42')
        assert res.request_id == 'req-42'

    def test_surface_propagated(self):
        res = _classify(original_surface='كَتَبَ')
        assert res.surface == 'كَتَبَ'


# ── HARF classification ────────────────────────────────────────────────────────

class TestHarfClassification:
    def test_closed_function_word_via_operator_boundary(self):
        res = _classify(
            p5_verdict='OPERATOR_BOUNDARY',
            p5_lexical_class='Closed Function Word',
            operator_status=True,
            mabni_status='boundary',
        )
        assert res.verdict == WordClassVerdict.ACCEPTED
        assert res.word_class == WordClass.HARF

    def test_numerical_operator_is_harf(self):
        res = _classify(
            p5_verdict='OPERATOR_BOUNDARY',
            p5_lexical_class='Numerical Operator',
            operator_status=True,
            mabni_status='boundary',
        )
        assert res.word_class == WordClass.HARF

    def test_closed_function_word_via_mabni_boundary(self):
        res = _classify(
            p5_verdict='MABNI_BOUNDARY',
            p5_lexical_class='Closed Function Word',
            operator_status=False,
            mabni_status='boundary',
        )
        assert res.word_class == WordClass.HARF

    def test_harf_subclass_closed_function_word(self):
        res = _classify(
            p5_verdict='OPERATOR_BOUNDARY',
            p5_lexical_class='Closed Function Word',
            operator_status=True,
            mabni_status='boundary',
        )
        assert res.subclass == LexicalSubclass.CLOSED_FUNCTION_WORD

    def test_harf_subclass_numerical_operator(self):
        res = _classify(
            p5_verdict='OPERATOR_BOUNDARY',
            p5_lexical_class='Numerical Operator',
            operator_status=True,
            mabni_status='boundary',
        )
        assert res.subclass == LexicalSubclass.NUMERICAL_OPERATOR


# ── FI3L classification ────────────────────────────────────────────────────────

class TestFi3lClassification:
    def test_verbal_root_path_alone(self):
        """يَكْتُبُ — verbal_root_path alone implies FI3L (B-01 path)."""
        res = _classify(morphology_path='verbal_root_path')
        assert res.verdict == WordClassVerdict.ACCEPTED
        assert res.word_class == WordClass.FI3L

    def test_ambiguous_path_with_p4a_accept(self):
        """كَتَبَ — ambiguous path + p4a:accept → FI3L."""
        res = _classify(
            morphology_path='ambiguous_morphology_path',
            available_evidence=('p4a:accept:FA_A_LA',),
        )
        assert res.word_class == WordClass.FI3L

    def test_ambiguous_path_no_p4a_defers(self):
        """ambiguous path without p4a:accept should NOT produce FI3L via this route."""
        res = _classify(
            morphology_path='ambiguous_morphology_path',
            available_evidence=(),
        )
        # Should not classify as FI3L through this ambiguous path alone
        assert res.word_class != WordClass.FI3L or res.verdict != WordClassVerdict.ACCEPTED

    def test_licensed_verbal_host(self):
        """licensed_verbal_host (bab accepted) + verbal path → FI3L."""
        res = _classify(
            morphology_path='verbal_root_path',
            licensed_verbal_host=True,
            bab_id='FAA3ALA',
        )
        assert res.word_class == WordClass.FI3L

    def test_verbal_operator_is_fi3l(self):
        """Verbal Operator lexical class → FI3L."""
        res = _classify(
            p5_verdict='OPERATOR_BOUNDARY',
            p5_lexical_class='Verbal Operator',
            operator_status=True,
            mabni_status='boundary',
        )
        assert res.word_class == WordClass.FI3L


# ── ISM classification ─────────────────────────────────────────────────────────

class TestIsmClassification:
    def test_masdar_accepted(self):
        res = _classify(
            morphology_path='ambiguous_morphology_path',
            masdar_accepted=True,
            masdar_surface='كِتَابَةٌ',
        )
        assert res.word_class == WordClass.ISM
        assert res.subclass == LexicalSubclass.MASDAR

    def test_nominal_morphology_path(self):
        res = _classify(morphology_path='nominal_morphology_path')
        assert res.word_class == WordClass.ISM

    def test_derived_nominal_path(self):
        res = _classify(morphology_path='derived_nominal_path')
        assert res.word_class == WordClass.ISM

    def test_functional_path(self):
        res = _classify(morphology_path='functional_path')
        assert res.word_class == WordClass.ISM

    def test_derivative_accepted_nominal_path(self):
        res = _classify(
            morphology_path='nominal_morphology_path',
            derivative_accepted=True,
            derivative_type='ISM_FA3IL',
        )
        assert res.word_class == WordClass.ISM

    def test_mabni_boundary_pronoun(self):
        """B-04: attachment_route=MABNI_BOUNDARY + DETACHED_PRONOUN mabni_id → ISM/PRONOUN."""
        res = _classify(
            p5_verdict='MABNI_BOUNDARY',
            mabni_status='boundary',
            attachment_route='MABNI_BOUNDARY',
            attachment_notes='whole-token match: HUWA',
            attachment_mabni_id='HUWA',
        )
        assert res.word_class == WordClass.ISM
        assert res.subclass == LexicalSubclass.PRONOUN

    def test_mabni_boundary_demonstrative(self):
        """B-04: attachment_route=MABNI_BOUNDARY + DEMONSTRATIVE mabni_id → ISM/DEMONSTRATIVE."""
        res = _classify(
            p5_verdict='MABNI_BOUNDARY',
            mabni_status='boundary',
            attachment_route='MABNI_BOUNDARY',
            attachment_notes='whole-token match: HADHA',
            attachment_mabni_id='HADHA',
        )
        assert res.word_class == WordClass.ISM
        assert res.subclass == LexicalSubclass.DEMONSTRATIVE


# ── blocking ───────────────────────────────────────────────────────────────────

class TestBlocking:
    def test_upstream_block_propagates(self):
        res = _classify(
            p5_verdict='BLOCK',
            mabni_status='blocked',
            upstream_verdicts=('BLOCK',),
        )
        assert res.verdict == WordClassVerdict.BLOCKED

    def test_blocked_has_no_word_class(self):
        res = _classify(
            p5_verdict='BLOCK',
            mabni_status='blocked',
            upstream_verdicts=('BLOCK',),
        )
        assert res.word_class is None


# ── deferral ───────────────────────────────────────────────────────────────────

class TestDeferral:
    def test_empty_request_defers(self):
        """A request with no usable evidence defers."""
        res = _classify()
        assert res.verdict == WordClassVerdict.DEFERRED

    def test_deferred_reason_code_set(self):
        res = _classify()
        assert res.reason_code != ''
