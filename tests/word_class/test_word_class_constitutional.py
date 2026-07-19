"""
tests/word_class/test_word_class_constitutional.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — constitutional constraints

These tests enforce the mandate's absolute constraints:
- NEVER equate operator=HARF, mabni=HARF, morphologically_open=FI3L, pattern=word_class
- NEVER integrate Taaqol runtime
- Ownership gate is closed
- Engine is the sole authority
"""
import pytest

from pipeline.word_class import classify_word_class
from pipeline.word_class.models import (
    WordClass, WordClassVerdict, LexicalSubclass,
    WordClassRequest, WordClassResult,
    WordClassOwnershipGate, WORD_CLASS_ENGINE_ID,
)
from pipeline.word_class.catalog import (
    _HARF_OPERATOR_CLASSES, _VERBAL_OPERATOR_CLASSES,
)


def _make_request(**overrides) -> WordClassRequest:
    defaults = dict(
        request_id='const-test',
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


# ── §1: NEVER equate operator_status=True → HARF without lexical_class check ──

class TestOperatorIsNotAlwaysHarf:
    def test_verbal_operator_is_fi3l_not_harf(self):
        """A verbal operator (كاد، كان) must produce FI3L, not HARF."""
        for lex_class in _VERBAL_OPERATOR_CLASSES:
            res = classify_word_class(_make_request(
                p5_verdict='OPERATOR_BOUNDARY',
                p5_lexical_class=lex_class,
                operator_status=True,
                mabni_status='boundary',
            ))
            assert res.word_class != WordClass.HARF, (
                f'Verbal operator lexical_class={lex_class!r} must NOT produce HARF. '
                'Constitutional violation: operator≠HARF.'
            )

    def test_bound_nominal_operator_is_ism(self):
        """Bound Nominal operator (كل etc.) must produce ISM, not HARF."""
        res = classify_word_class(_make_request(
            p5_verdict='OPERATOR_BOUNDARY',
            p5_lexical_class='Bound Nominal',
            operator_status=True,
            mabni_status='boundary',
        ))
        assert res.word_class != WordClass.HARF, (
            'Bound Nominal must NOT produce HARF. '
            'Constitutional violation: operator≠HARF.'
        )


# ── §2: NEVER equate mabni=HARF ──────────────────────────────────────────────

class TestMabniIsNotAlwaysHarf:
    def test_mabni_boundary_pronouns_are_ism(self):
        """mabni=boundary for pronouns must produce ISM, not HARF."""
        for mabni_id, expected_subclass in [
            ('HUWA', LexicalSubclass.PRONOUN),
            ('HADHA', LexicalSubclass.DEMONSTRATIVE),
        ]:
            res = classify_word_class(_make_request(
                p5_verdict='MABNI_BOUNDARY',
                mabni_status='boundary',
                attachment_route='MABNI_BOUNDARY',
                attachment_notes=f'whole-token match: {mabni_id}',
                attachment_mabni_id=mabni_id,
            ))
            assert res.word_class == WordClass.ISM, (
                f'{mabni_id}: mabni boundary must produce ISM, not '
                f'{res.word_class}. Constitutional violation: mabni≠HARF.'
            )


# ── §3: NEVER equate morphologically_open → FI3L ─────────────────────────────

class TestMorphologicallyOpenIsNotFi3l:
    def test_mabni_open_nominal_path_is_ism(self):
        """mabni_status=open + nominal path → ISM, not FI3L."""
        res = classify_word_class(_make_request(
            mabni_status='open',
            morphology_path='nominal_morphology_path',
        ))
        assert res.word_class == WordClass.ISM, (
            'morphologically_open + nominal_morphology_path must give ISM. '
            'Constitutional violation: morphologically_open≠FI3L.'
        )

    def test_mabni_open_no_path_is_deferred(self):
        """mabni_status=open + no morphology evidence → DEFERRED, not FI3L."""
        res = classify_word_class(_make_request(mabni_status='open'))
        assert res.word_class != WordClass.FI3L, (
            'morphologically_open alone must NOT produce FI3L. '
            'Constitutional violation: morphologically_open≠FI3L.'
        )


# ── §4: NEVER equate pattern=word_class ───────────────────────────────────────

class TestPatternIsNotWordClass:
    def test_p4a_accept_without_verbal_path_is_not_fi3l(self):
        """
        p4a:accept alone on a nominal path should not override ISM classification.
        Pattern evidence does not equal word class.
        """
        res = classify_word_class(_make_request(
            morphology_path='nominal_morphology_path',
            available_evidence=('p4a:accept:FA3ALUN',),
        ))
        assert res.word_class == WordClass.ISM, (
            'p4a:accept on nominal_morphology_path must give ISM, not FI3L. '
            'Constitutional violation: pattern≠word_class.'
        )


# ── §5: No Taaqol runtime imported in engine modules ─────────────────────────

class TestNoTaaqolRuntime:
    def test_engine_does_not_import_taaqol(self):
        import pipeline.word_class.engine as engine_mod
        src = open(engine_mod.__file__).read()
        assert 'taaqol' not in src.lower() or 'taaqol_integration' not in src.lower(), (
            'engine.py must not import Taaqol runtime.'
        )

    def test_models_does_not_import_taaqol(self):
        import pipeline.word_class.models as models_mod
        src = open(models_mod.__file__).read()
        assert 'from vendor' not in src and 'import taaqol' not in src.lower()

    def test_catalog_does_not_import_taaqol(self):
        import pipeline.word_class.catalog as catalog_mod
        src = open(catalog_mod.__file__).read()
        assert 'from vendor' not in src and 'import taaqol' not in src.lower()


# ── §6: Ownership gate must be closed ────────────────────────────────────────

class TestOwnershipGateClosed:
    def test_gate_is_closed(self):
        gate = WordClassOwnershipGate()
        assert gate.is_closed(), (
            f'WordClassOwnershipGate.is_closed() returned False. '
            f'Gate state: {gate.to_dict()}'
        )

    def test_all_bugs_fixed(self):
        gate = WordClassOwnershipGate()
        for field, expected in [
            ('b01_inflection_gate', 'FIXED'),
            ('b02_lexical_class_source', 'FIXED'),
            ('b03_part_of_speech_source', 'FIXED'),
            ('b04_pronoun_demonstrative', 'FIXED'),
        ]:
            val = getattr(gate, field)
            assert val == expected, f'{field}={val!r}, expected "FIXED"'

    def test_no_parallel_engines(self):
        gate = WordClassOwnershipGate()
        assert gate.parallel_engines == 0

    def test_no_external_dependencies(self):
        gate = WordClassOwnershipGate()
        assert gate.external_dependencies == 0


# ── §7: Engine is the sole word class authority ───────────────────────────────

class TestSoleAuthority:
    def test_engine_id_is_canonical(self):
        res = classify_word_class(_make_request(morphology_path='verbal_root_path'))
        assert res.engine_id == WORD_CLASS_ENGINE_ID

    def test_result_is_typed_not_dict(self):
        """classify_word_class must return a typed object, not a raw dict."""
        res = classify_word_class(_make_request(morphology_path='verbal_root_path'))
        assert isinstance(res, WordClassResult)
        assert not isinstance(res, dict)
