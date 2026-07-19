#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_serialization.py — Serialization tests"""
import json
import pytest
from pipeline.p6_derivatives.engine import analyze_derivative
from pipeline.p6_derivatives.models import DerivativeRequest, DerivativeResult


def _make_request(dtype='ISM_FA3IL', root=('ك', 'ت', 'ب'), form_family='FORM_I', **kwargs):
    defaults = dict(
        request_id='REQ-SER-001',
        mode='GENERATE_FROM_VERB',
        original_surface='كَتَبَ',
        normalized_surface='كَتَبَ',
        verbal_host='كَتَبَ',
        verbal_lemma='كَتَبَ',
        licensed_root=root,
        licensed_root_class='SOUND',
        licensed_pattern='FA3ALA',
        verb_form_family=form_family,
        voice=None,
        available_context=(),
        derivative_type=dtype,
        supplied_derivative_surface=None,
        evidence=(),
        upstream_trace=(),
    )
    defaults.update(kwargs)
    return DerivativeRequest(**defaults)


def _roundtrip(result: DerivativeResult) -> dict:
    d = result.to_dict()
    return json.loads(json.dumps(d, ensure_ascii=False))


# ── Basic serialization ───────────────────────────────────────────────────────

def test_accepted_result_serializes():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    assert restored['verdict'] == 'DERIVATIVE_ACCEPTED'

def test_deferred_result_serializes():
    req = _make_request('MUBALGHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    assert restored['verdict'] == 'DERIVATIVE_DEFERRED'
    assert restored['deferred'] is not None
    assert restored['deferred']['reason'] is not None

def test_blocked_result_serializes():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    assert restored['verdict'] == 'DERIVATIVE_BLOCKED'
    assert restored['blocked'] is not None
    assert len(restored['blocked']['contradictions']) >= 1

def test_residual_result_serializes():
    req = _make_request('ISM_ALA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    assert restored['verdict'] == 'DERIVATIVE_RESIDUAL'
    assert len(restored['residuals']) >= 1


# ── Nested object serialization ───────────────────────────────────────────────

def test_licensed_derivatives_serialize():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    for ld in restored['licensed_derivatives']:
        assert 'derivative_id' in ld
        assert 'candidate' in ld
        assert 'licensing_evidence' in ld
        assert 'license_kind' in ld

def test_candidate_nested_serialization():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    for ld in restored['licensed_derivatives']:
        cand = ld['candidate']
        assert 'derivative_type' in cand
        assert 'canonical_pattern' in cand
        assert 'root' in cand
        assert 'supporting_evidence' in cand
        assert 'verdict' in cand

def test_evidence_nested_serialization():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    for ld in restored['licensed_derivatives']:
        for ev in ld['candidate']['supporting_evidence']:
            assert 'evidence_id' in ev
            assert 'evidence_type' in ev
            assert 'sufficiency' in ev


# ── Request serialization ─────────────────────────────────────────────────────

def test_request_serializes():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    req_d = restored['request']
    assert req_d['mode'] == 'GENERATE_FROM_VERB'
    assert req_d['derivative_type'] == 'ISM_FA3IL'
    assert req_d['licensed_root'] == ['ك', 'ت', 'ب']

def test_request_licensed_root_is_list_in_json():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    assert isinstance(restored['request']['licensed_root'], list)


# ── Trace serialization ───────────────────────────────────────────────────────

def test_trace_serializes():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    assert isinstance(restored['trace'], list)
    assert len(restored['trace']) > 0
    for t in restored['trace']:
        assert 'step' in t
        assert 'stage' in t
        assert 'action' in t


# ── Source engine ─────────────────────────────────────────────────────────────

def test_source_engine_in_serialized():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    assert restored['source_engine'] == 'HOKOM_DERIVATIVES_ENGINE'


# ── Full round-trip all derivative types ─────────────────────────────────────

@pytest.mark.parametrize('dtype', [
    'ISM_FA3IL', 'ISM_MAF3UL', 'MUBALGHA', 'ISM_ALA', 'ISM_ZAMAN', 'auto',
])
def test_full_roundtrip_all_types(dtype):
    req = _make_request(dtype)
    result = analyze_derivative(req)
    restored = _roundtrip(result)
    assert restored['verdict'] in (
        'DERIVATIVE_ACCEPTED', 'DERIVATIVE_DEFERRED',
        'DERIVATIVE_BLOCKED', 'DERIVATIVE_RESIDUAL'
    )
    assert restored['source_engine'] == 'HOKOM_DERIVATIVES_ENGINE'
