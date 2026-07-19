#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_models.py — Model validation tests"""
import pytest
from pipeline.p5_masdar.models import (
    MASDAR_CANONICAL_OWNER, MASDAR_ENGINE_ID, MASDAR_OWNERSHIP_VERSION,
    MASDAR_TYPES, MASDAR_VERDICTS, MASDAR_MODES, EVIDENCE_TYPES,
    EVIDENCE_SUFFICIENCY, CONTRADICTION_TYPES, REALIZATION_OPERATION_TYPES,
    MULTIPLICITY_VALUES,
    MasdarEvidence, MasdarContradiction, MasdarRealizationOperation,
    MasdarTraceEvent, MasdarRequest, MasdarCandidate, LicensedMasdar,
    DeferredMasdar, BlockedMasdar, MasdarResidual, MasdarResult,
    MasdarOwnershipGate,
)


# ── constants ─────────────────────────────────────────────────────────────────

def test_canonical_owner():
    assert MASDAR_CANONICAL_OWNER == 'HOKOM'

def test_engine_id():
    assert MASDAR_ENGINE_ID == 'HOKOM_MASDAR_ENGINE'

def test_ownership_version():
    assert MASDAR_OWNERSHIP_VERSION == '1.0.0'

def test_masdar_types():
    assert 'MASDAR_ASLI'  in MASDAR_TYPES
    assert 'MASDAR_MIMI'  in MASDAR_TYPES
    assert 'MASDAR_MARRA' in MASDAR_TYPES
    assert 'MASDAR_HAYAA' in MASDAR_TYPES
    assert 'ISM_MASDAR'   in MASDAR_TYPES

def test_masdar_verdicts():
    assert 'MASDAR_ACCEPTED' in MASDAR_VERDICTS
    assert 'MASDAR_DEFERRED' in MASDAR_VERDICTS
    assert 'MASDAR_BLOCKED'  in MASDAR_VERDICTS
    assert 'MASDAR_RESIDUAL' in MASDAR_VERDICTS


# ── MasdarEvidence ────────────────────────────────────────────────────────────

def test_masdar_evidence_valid():
    ev = MasdarEvidence('EV-001', 'ROOT_LICENSE_EVIDENCE', 'SUFFICIENT', 'test')
    assert ev.evidence_id == 'EV-001'
    assert ev.evidence_type == 'ROOT_LICENSE_EVIDENCE'
    assert ev.sufficiency == 'SUFFICIENT'
    assert ev.source == 'test'
    assert ev.detail is None

def test_masdar_evidence_with_detail():
    ev = MasdarEvidence('EV-002', 'FORM_FAMILY_EVIDENCE', 'CONTRIBUTORY', 'src', 'detail text')
    d = ev.to_dict()
    assert d['detail'] == 'detail text'

def test_masdar_evidence_invalid_type():
    with pytest.raises(ValueError, match='unknown evidence_type'):
        MasdarEvidence('EV-003', 'BAD_TYPE', 'SUFFICIENT', 'test')

def test_masdar_evidence_invalid_sufficiency():
    with pytest.raises(ValueError, match='unknown sufficiency'):
        MasdarEvidence('EV-004', 'ROOT_LICENSE_EVIDENCE', 'GREAT', 'test')

def test_masdar_evidence_to_dict():
    ev = MasdarEvidence('EV-005', 'VERB_PATTERN_EVIDENCE', 'SUFFICIENT', 'src', 'det')
    d = ev.to_dict()
    assert set(d.keys()) == {'evidence_id', 'evidence_type', 'sufficiency', 'source', 'detail'}


# ── MasdarContradiction ───────────────────────────────────────────────────────

def test_masdar_contradiction_valid():
    c = MasdarContradiction('C-001', 'ROOT_MISMATCH', 'locus', 'detail')
    assert c.contradiction_type == 'ROOT_MISMATCH'

def test_masdar_contradiction_invalid():
    with pytest.raises(ValueError, match='unknown contradiction_type'):
        MasdarContradiction('C-002', 'FAKE_TYPE', 'locus', 'detail')

def test_masdar_contradiction_to_dict():
    c = MasdarContradiction('C-003', 'NON_VERBAL_ORIGIN', 'form_family', 'det')
    d = c.to_dict()
    assert d['contradiction_type'] == 'NON_VERBAL_ORIGIN'
    assert d['locus'] == 'form_family'


# ── MasdarRealizationOperation ────────────────────────────────────────────────

def test_realization_operation_valid():
    op = MasdarRealizationOperation(
        'OP-001', 'MASDAR_WEAK_FINAL_REALIZATION', 'C3', 'ي', 'ة',
        'RULE-01', ('EV-1',), ('EV-1',), True, ('trace-1',)
    )
    assert op.operation_type == 'MASDAR_WEAK_FINAL_REALIZATION'
    d = op.to_dict()
    assert d['reversible'] is True

def test_realization_operation_invalid():
    with pytest.raises(ValueError, match='unknown operation_type'):
        MasdarRealizationOperation(
            'OP-002', 'FAKE_OP', 'C3', 'ي', 'ة',
            'RULE-01', (), (), True, ()
        )


# ── MasdarTraceEvent ──────────────────────────────────────────────────────────

def test_trace_event():
    t = MasdarTraceEvent(1, 'GATE', 'PASS', 'detail')
    d = t.to_dict()
    assert d['step'] == 1
    assert d['stage'] == 'GATE'
    assert d['action'] == 'PASS'

def test_trace_event_no_detail():
    t = MasdarTraceEvent(2, 'FORM_I', 'DEFER')
    assert t.detail is None
    assert t.to_dict()['detail'] is None


# ── MasdarOwnershipGate ───────────────────────────────────────────────────────

def test_ownership_gate_defaults():
    gate = MasdarOwnershipGate()
    assert gate.MASDAR_CANONICAL_OWNER == 'HOKOM'
    assert gate.PARALLEL_MASDAR_ENGINES == 0
    assert gate.EXTERNAL_MASDAR_DEPENDENCIES == 0
    assert gate.FORM_I_UNLICENSED_GUESSES == 0
    assert gate.UNLICENSED_MASDAR_GUESSES == 0
    assert gate.FORCED_SINGLE_MASDAR_RESULTS == 0
    assert gate.MULTIPLE_LICENSED_MASDARS == 'SUPPORTED'
    assert gate.MASDAR_MIMI_CONTRACT == 'VERIFIED'
    assert gate.MASDAR_MARRA_CONTRACT == 'VERIFIED'
    assert gate.MASDAR_HAYAA_CONTRACT == 'VERIFIED'
    assert gate.ISM_MASDAR_CONTRACT == 'VERIFIED'
    assert gate.P5_SEMANTIC_MODIFICATIONS == 0
    assert gate.ROOT_SEMANTIC_MODIFICATIONS == 0
    assert gate.PATTERN_SEMANTIC_MODIFICATIONS == 0
    assert gate.TAAQOL_SUBMODULE_MODIFICATIONS == 0

def test_ownership_gate_frozen():
    gate = MasdarOwnershipGate()
    with pytest.raises(Exception):
        gate.PARALLEL_MASDAR_ENGINES = 1
