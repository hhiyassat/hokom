"""
tests/word_class/test_word_class_models.py
HOKOM-WORD-CLASS-OWNERSHIP-01 — models & enums

Validates that all model constants, enums, and dataclasses are correctly
defined and importable.  No pipeline I/O is needed.
"""
import dataclasses
import pytest

from pipeline.word_class.models import (
    WORD_CLASS_ENGINE_ID,
    WORD_CLASS_CANONICAL_OWNER,
    WORD_CLASS_OWNERSHIP_VERSION,
    WORD_CLASS_CANONICAL_ENTRYPOINT,
    WordClass,
    WordClassVerdict,
    LexicalSubclass,
    EvidenceType,
    ContradictionType,
    WordClassEvidence,
    WordClassContradiction,
    WordClassCandidate,
    WordClassRequest,
    WordClassResult,
    WordClassTraceEvent,
    WordClassResidual,
    WordClassOwnershipGate,
)


# ── ownership constants ────────────────────────────────────────────────────────

class TestOwnershipConstants:
    def test_engine_id(self):
        assert WORD_CLASS_ENGINE_ID == 'HOKOM_WORD_CLASS_ENGINE'

    def test_canonical_owner(self):
        assert WORD_CLASS_CANONICAL_OWNER == 'HOKOM'

    def test_version_semver(self):
        parts = WORD_CLASS_OWNERSHIP_VERSION.split('.')
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_entrypoint(self):
        assert WORD_CLASS_CANONICAL_ENTRYPOINT == 'classify_word_class'


# ── WordClass enum ─────────────────────────────────────────────────────────────

class TestWordClassEnum:
    def test_three_members(self):
        assert {wc.value for wc in WordClass} == {'ISM', 'FI3L', 'HARF'}

    def test_is_str(self):
        assert isinstance(WordClass.ISM, str)

    def test_ism_value(self):
        assert WordClass.ISM == 'ISM'

    def test_fi3l_value(self):
        assert WordClass.FI3L == 'FI3L'

    def test_harf_value(self):
        assert WordClass.HARF == 'HARF'


# ── WordClassVerdict enum ──────────────────────────────────────────────────────

class TestWordClassVerdict:
    def test_accepted(self):
        assert WordClassVerdict.ACCEPTED == 'WORD_CLASS_ACCEPTED'

    def test_deferred(self):
        assert WordClassVerdict.DEFERRED == 'WORD_CLASS_DEFERRED'

    def test_blocked(self):
        assert WordClassVerdict.BLOCKED == 'WORD_CLASS_BLOCKED'

    def test_residual(self):
        assert WordClassVerdict.RESIDUAL == 'WORD_CLASS_RESIDUAL'

    def test_is_str(self):
        assert isinstance(WordClassVerdict.ACCEPTED, str)


# ── LexicalSubclass enum ───────────────────────────────────────────────────────

class TestLexicalSubclass:
    _ISM_SUBCLASSES = {
        'PRONOUN', 'DEMONSTRATIVE', 'RELATIVE', 'INTERROGATIVE_NOUN',
        'CONDITIONAL_NOUN', 'MASDAR', 'ISM_FA3IL', 'ISM_MAF3UL',
        'ISM_ZAMAN_MAKAN', 'ISM_ALA', 'SIFA_MUSHABBAHA', 'MUBALGHA',
        'LEXICAL_NOUN', 'ADVERBIAL_MABNI', 'VERB_NAME',
    }
    _HARF_SUBCLASSES = {
        'PREPOSITION', 'CONJUNCTION', 'INTERROGATIVE_PARTICLE',
        'CONDITIONAL_PARTICLE', 'ACCUSATIVE_PARTICLE', 'JUSSIVE_PARTICLE',
        'NEGATIVE_PARTICLE', 'EMPHASIS_PARTICLE', 'FUTURE_PARTICLE',
        'CLOSED_FUNCTION_WORD', 'NUMERICAL_OPERATOR',
    }
    _FI3L_SUBCLASSES = {
        'VERBAL_PAST', 'VERBAL_IMPERFECT', 'VERBAL_IMPERATIVE', 'VERBAL_OPERATOR',
    }

    def test_ism_subclasses_present(self):
        values = {m.value for m in LexicalSubclass}
        assert self._ISM_SUBCLASSES.issubset(values)

    def test_harf_subclasses_present(self):
        values = {m.value for m in LexicalSubclass}
        assert self._HARF_SUBCLASSES.issubset(values)

    def test_fi3l_subclasses_present(self):
        values = {m.value for m in LexicalSubclass}
        assert self._FI3L_SUBCLASSES.issubset(values)

    def test_unresolved_present(self):
        assert 'UNRESOLVED' in {m.value for m in LexicalSubclass}

    def test_is_str(self):
        assert isinstance(LexicalSubclass.PRONOUN, str)


# ── EvidenceType enum ──────────────────────────────────────────────────────────

class TestEvidenceType:
    def test_key_types_present(self):
        values = {m.value for m in EvidenceType}
        required = {
            'LEXICAL_HARF_ENTRY', 'LEXICAL_PRONOUN_ENTRY',
            'LEXICAL_DEMONSTRATIVE_ENTRY', 'ACCEPTED_MASDAR',
            'ACCEPTED_DERIVATIVE', 'LICENSED_VERBAL_HOST',
            'ROOT_PATTERN_VERBAL', 'ATTACHMENT_MABNI',
        }
        assert required.issubset(values)


# ── ContradictionType enum ─────────────────────────────────────────────────────

class TestContradictionType:
    def test_key_types_present(self):
        values = {m.value for m in ContradictionType}
        required = {
            'MASDAR_BLOCKS_FI3L', 'DERIVATIVE_BLOCKS_FI3L',
            'OPERATOR_BOUNDARY_HARF', 'NON_VERBAL_BLOCKS_FI3L',
        }
        assert required.issubset(values)


# ── WordClassEvidence frozen dataclass ─────────────────────────────────────────

class TestWordClassEvidence:
    def _make(self):
        return WordClassEvidence(
            evidence_type=EvidenceType.LEXICAL_HARF_ENTRY,
            source='test',
            value='هَلْ',
            confidence='HIGH',
        )

    def test_frozen(self):
        ev = self._make()
        with pytest.raises((AttributeError, TypeError, dataclasses.FrozenInstanceError)):
            ev.value = 'other'

    def test_fields(self):
        ev = self._make()
        assert ev.evidence_type == EvidenceType.LEXICAL_HARF_ENTRY
        assert ev.confidence == 'HIGH'


# ── WordClassRequest frozen dataclass ──────────────────────────────────────────

class TestWordClassRequest:
    def _make(self, **overrides):
        defaults = dict(
            request_id='test-001',
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

    def test_frozen(self):
        req = self._make()
        with pytest.raises((AttributeError, TypeError, dataclasses.FrozenInstanceError)):
            req.original_surface = 'other'

    def test_fields_present(self):
        req = self._make()
        assert req.original_surface == 'كَتَبَ'
        assert req.morphology_path == 'verbal_root_path'


# ── WordClassResult frozen dataclass ───────────────────────────────────────────

class TestWordClassResult:
    def _make(self):
        return WordClassResult(
            request_id='test-001',
            surface='كَتَبَ',
            verdict=WordClassVerdict.ACCEPTED,
            word_class=WordClass.FI3L,
            subclass=LexicalSubclass.VERBAL_PAST,
            candidates=(),
            primary_evidence=(),
            contradictions=(),
            reason_code='verbal_root_path',
            residuals=(),
            trace=(),
        )

    def test_frozen(self):
        res = self._make()
        with pytest.raises((AttributeError, TypeError, dataclasses.FrozenInstanceError)):
            res.verdict = WordClassVerdict.BLOCKED

    def test_engine_id_default(self):
        res = self._make()
        assert res.engine_id == WORD_CLASS_ENGINE_ID

    def test_to_dict_returns_dict(self):
        res = self._make()
        d = res.to_dict()
        assert isinstance(d, dict)
        assert d['surface'] == 'كَتَبَ'
        assert d['verdict'] == 'WORD_CLASS_ACCEPTED'
        assert d['word_class'] == 'FI3L'


# ── WordClassOwnershipGate ─────────────────────────────────────────────────────

class TestWordClassOwnershipGate:
    def test_default_is_closed(self):
        gate = WordClassOwnershipGate()
        assert gate.is_closed()

    def test_status_closed(self):
        gate = WordClassOwnershipGate()
        assert gate.status == 'CLOSED'

    def test_bugs_fixed(self):
        gate = WordClassOwnershipGate()
        assert gate.b01_inflection_gate == 'FIXED'
        assert gate.b02_lexical_class_source == 'FIXED'
        assert gate.b03_part_of_speech_source == 'FIXED'
        assert gate.b04_pronoun_demonstrative == 'FIXED'

    def test_live_wired(self):
        gate = WordClassOwnershipGate()
        assert gate.live_wired is True

    def test_to_dict(self):
        gate = WordClassOwnershipGate()
        d = gate.to_dict()
        assert isinstance(d, dict)
        assert d['status'] == 'CLOSED'
