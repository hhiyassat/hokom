#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_models.py — Model validation tests"""
import pytest
from pipeline.p6_derivatives.models import (
    DERIVATIVES_CANONICAL_OWNER, DERIVATIVES_ENGINE_ID, DERIVATIVES_OWNERSHIP_VERSION,
    DERIVATIVE_TYPES, DERIVATIVE_VERDICTS, DERIVATIVE_MODES, EVIDENCE_TYPES,
    EVIDENCE_SUFFICIENCY, CONTRADICTION_TYPES, REALIZATION_OPERATION_TYPES,
    MULTIPLICITY_VALUES,
    DerivativeEvidence, DerivativeContradiction, DerivativeRealizationOperation,
    DerivativeTraceEvent, DerivativeRequest, DerivativeCandidate, LicensedDerivative,
    DeferredDerivative, BlockedDerivative, DerivativeResidual, DerivativeResult,
    DerivativesOwnershipGate,
)


# ── constants ─────────────────────────────────────────────────────────────────

def test_canonical_owner():
    assert DERIVATIVES_CANONICAL_OWNER == 'HOKOM'

def test_engine_id():
    assert DERIVATIVES_ENGINE_ID == 'HOKOM_DERIVATIVES_ENGINE'

def test_ownership_version():
    assert DERIVATIVES_OWNERSHIP_VERSION == '1.0.0'

def test_derivative_types():
    assert 'ISM_FA3IL'      in DERIVATIVE_TYPES
    assert 'ISM_MAF3UL'     in DERIVATIVE_TYPES
    assert 'SIFA_MUSHABBAHA' in DERIVATIVE_TYPES
    assert 'MUBALGHA'       in DERIVATIVE_TYPES
    assert 'ISM_ZAMAN'      in DERIVATIVE_TYPES
    assert 'ISM_MAKAN'      in DERIVATIVE_TYPES
    assert 'ISM_ALA'        in DERIVATIVE_TYPES
    assert len(DERIVATIVE_TYPES) == 7

def test_derivative_verdicts():
    assert 'DERIVATIVE_ACCEPTED'  in DERIVATIVE_VERDICTS
    assert 'DERIVATIVE_DEFERRED'  in DERIVATIVE_VERDICTS
    assert 'DERIVATIVE_BLOCKED'   in DERIVATIVE_VERDICTS
    assert 'DERIVATIVE_RESIDUAL'  in DERIVATIVE_VERDICTS

def test_derivative_modes():
    assert 'GENERATE_FROM_VERB'         in DERIVATIVE_MODES
    assert 'VALIDATE_SUPPLIED_DERIVATIVE' in DERIVATIVE_MODES
    assert 'ANALYZE_DERIVATIVE_SURFACE' in DERIVATIVE_MODES

def test_fa3il_participle_not_in_derivative_types():
    """FA3IL_PARTICIPLE is a routing tag, not a derivative_type."""
    assert 'FA3IL_PARTICIPLE' not in DERIVATIVE_TYPES


# ── DerivativeEvidence ────────────────────────────────────────────────────────

def test_derivative_evidence_valid():
    ev = DerivativeEvidence('EV-001', 'ROOT_LICENSE_EVIDENCE', 'SUFFICIENT', 'test')
    assert ev.evidence_id == 'EV-001'
    assert ev.evidence_type == 'ROOT_LICENSE_EVIDENCE'
    assert ev.sufficiency == 'SUFFICIENT'
    assert ev.source == 'test'
    assert ev.detail is None

def test_derivative_evidence_with_detail():
    ev = DerivativeEvidence('EV-002', 'FORM_FAMILY_EVIDENCE', 'CONTRIBUTORY', 'src', 'detail text')
    d = ev.to_dict()
    assert d['detail'] == 'detail text'

def test_derivative_evidence_invalid_type():
    with pytest.raises(ValueError, match='unknown evidence_type'):
        DerivativeEvidence('EV-003', 'BAD_TYPE', 'SUFFICIENT', 'test')

def test_derivative_evidence_invalid_sufficiency():
    with pytest.raises(ValueError, match='unknown sufficiency'):
        DerivativeEvidence('EV-004', 'ROOT_LICENSE_EVIDENCE', 'GREAT', 'test')

def test_derivative_evidence_to_dict():
    ev = DerivativeEvidence('EV-005', 'VERB_PATTERN_EVIDENCE', 'SUFFICIENT', 'src', 'det')
    d = ev.to_dict()
    assert set(d.keys()) == {'evidence_id', 'evidence_type', 'sufficiency', 'source', 'detail'}


# ── DerivativeContradiction ───────────────────────────────────────────────────

def test_derivative_contradiction_valid():
    c = DerivativeContradiction('C-001', 'ROOT_MISMATCH', 'locus', 'detail')
    assert c.contradiction_type == 'ROOT_MISMATCH'

def test_derivative_contradiction_invalid():
    with pytest.raises(ValueError, match='unknown contradiction_type'):
        DerivativeContradiction('C-002', 'FAKE_TYPE', 'locus', 'detail')

def test_derivative_contradiction_to_dict():
    c = DerivativeContradiction('C-003', 'NON_VERBAL_ORIGIN', 'form_family', 'det')
    d = c.to_dict()
    assert d['contradiction_type'] == 'NON_VERBAL_ORIGIN'
    assert d['locus'] == 'form_family'

def test_masdar_surface_leakage_in_contradiction_types():
    assert 'MASDAR_SURFACE_LEAKAGE' in CONTRADICTION_TYPES

def test_ism_zaman_makan_mimi_in_contradiction_types():
    assert 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY' in CONTRADICTION_TYPES


# ── DerivativeRealizationOperation ───────────────────────────────────────────

def test_realization_operation_valid():
    op = DerivativeRealizationOperation(
        'OP-001', 'DERIV_WEAK_FINAL_REALIZATION', 'C3', 'ي', 'ة',
        'RULE-01', ('EV-1',), ('EV-1',), True, ('trace-1',)
    )
    assert op.operation_type == 'DERIV_WEAK_FINAL_REALIZATION'
    d = op.to_dict()
    assert d['reversible'] is True

def test_realization_operation_invalid():
    with pytest.raises(ValueError, match='unknown operation_type'):
        DerivativeRealizationOperation(
            'OP-002', 'FAKE_OP', 'C3', 'ي', 'ة',
            'RULE-01', (), (), True, ()
        )

def test_realization_operation_to_dict_keys():
    op = DerivativeRealizationOperation(
        'OP-003', 'DERIV_GEMINATION_REALIZATION', 'C2', 'ل', 'لّ',
        'RULE-02', (), (), False, ()
    )
    d = op.to_dict()
    expected_keys = {'operation_id', 'operation_type', 'locus', 'before', 'after',
                     'rule_id', 'required_evidence', 'actual_evidence', 'reversible', 'trace'}
    assert set(d.keys()) == expected_keys


# ── DerivativeTraceEvent ──────────────────────────────────────────────────────

def test_trace_event():
    t = DerivativeTraceEvent(1, 'GATE', 'PASS', 'detail')
    d = t.to_dict()
    assert d['step'] == 1
    assert d['stage'] == 'GATE'
    assert d['action'] == 'PASS'

def test_trace_event_no_detail():
    t = DerivativeTraceEvent(2, 'ISM_FA3IL', 'DEFER')
    assert t.detail is None
    assert t.to_dict()['detail'] is None


# ── DerivativeRequest ─────────────────────────────────────────────────────────

def _make_request(**kwargs):
    defaults = dict(
        request_id='REQ-001',
        mode='GENERATE_FROM_VERB',
        original_surface='كَتَبَ',
        normalized_surface='كَتَبَ',
        verbal_host='كَتَبَ',
        verbal_lemma='كَتَبَ',
        licensed_root=('ك', 'ت', 'ب'),
        licensed_root_class='SOUND',
        licensed_pattern='FA3ALA',
        verb_form_family='FORM_I',
        voice=None,
        available_context=(),
        derivative_type='ISM_FA3IL',
        supplied_derivative_surface=None,
        evidence=(),
        upstream_trace=(),
    )
    defaults.update(kwargs)
    return DerivativeRequest(**defaults)

def test_request_valid():
    req = _make_request()
    assert req.derivative_type == 'ISM_FA3IL'

def test_request_invalid_mode():
    with pytest.raises(ValueError, match='unknown mode'):
        _make_request(mode='BAD_MODE')

def test_request_invalid_derivative_type():
    with pytest.raises(ValueError, match='unknown derivative_type'):
        _make_request(derivative_type='FA3IL_PARTICIPLE')

def test_request_auto_type_valid():
    req = _make_request(derivative_type='auto')
    assert req.derivative_type == 'auto'

def test_request_none_type_valid():
    req = _make_request(derivative_type=None)
    assert req.derivative_type is None

def test_request_to_dict():
    req = _make_request()
    d = req.to_dict()
    assert d['mode'] == 'GENERATE_FROM_VERB'
    assert d['derivative_type'] == 'ISM_FA3IL'
    assert d['licensed_root'] == ['ك', 'ت', 'ب']


# ── DerivativesOwnershipGate ──────────────────────────────────────────────────

def test_ownership_gate_defaults():
    gate = DerivativesOwnershipGate()
    assert gate.DERIVATIVES_CANONICAL_OWNER == 'HOKOM'
    assert gate.PARALLEL_DERIVATIVE_ENGINES == 0
    assert gate.EXTERNAL_DERIVATIVE_DEPENDENCIES == 0
    assert gate.ISM_FA3IL_CONTRACT == 'VERIFIED'
    assert gate.ISM_MAF3UL_CONTRACT == 'VERIFIED'
    assert gate.SIFA_MUSHABBAHA_CONTRACT == 'VERIFIED'
    assert gate.MUBALGHA_CONTRACT == 'VERIFIED'
    assert gate.ISM_ZAMAN_CONTRACT == 'VERIFIED'
    assert gate.ISM_MAKAN_CONTRACT == 'VERIFIED'
    assert gate.ISM_ALA_CONTRACT == 'VERIFIED'
    assert gate.MASDAR_MIMI_LEAKAGE_PREVENTION == 'VERIFIED'
    assert gate.FA3IL_PARTICIPLE_ROUTING_PRESERVED == 'VERIFIED'
    assert gate.ISM_ZAMAN_MAKAN_AMBIGUITY_GOVERNED == 'VERIFIED'
    assert gate.MUBALGHA_UNLICENSED_GUESSES == 0
    assert gate.SIFA_UNLICENSED_GUESSES == 0
    assert gate.MULTIPLE_LICENSED_DERIVATIVES == 'SUPPORTED'
    assert gate.DERIVATIVE_RESIDUALS_GOVERNED == 'VERIFIED'
    assert gate.DERIVATIVE_TRACE_COMPLETE == 'VERIFIED'
    assert gate.DERIVATIVE_SERIALIZATION_ROUNDTRIP == 'PASS'
    assert gate.P5_MASDAR_SEMANTIC_MODIFICATIONS == 0
    assert gate.ROOT_SEMANTIC_MODIFICATIONS == 0
    assert gate.PATTERN_SEMANTIC_MODIFICATIONS == 0
    assert gate.TAAQOL_SUBMODULE_MODIFICATIONS == 0

def test_ownership_gate_frozen():
    gate = DerivativesOwnershipGate()
    with pytest.raises(Exception):
        gate.PARALLEL_DERIVATIVE_ENGINES = 1
