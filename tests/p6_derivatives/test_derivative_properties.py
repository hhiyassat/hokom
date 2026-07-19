#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_properties.py — Property tests"""
import json
import pytest
from pipeline.p6_derivatives.engine import analyze_derivative
from pipeline.p6_derivatives.models import DerivativeRequest


def _make_request(dtype='ISM_FA3IL', form_family='FORM_I', root=('ك', 'ت', 'ب'), **kwargs):
    defaults = dict(
        request_id='REQ-PROP-001',
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


# ── Determinism ───────────────────────────────────────────────────────────────

def test_determinism_ism_fa3il():
    """Same input → same output twice."""
    req = _make_request('ISM_FA3IL')
    r1  = analyze_derivative(req)
    r2  = analyze_derivative(req)
    assert r1.verdict == r2.verdict
    assert r1.multiplicity == r2.multiplicity
    assert len(r1.licensed_derivatives) == len(r2.licensed_derivatives)
    p1 = [ld.candidate.canonical_pattern for ld in r1.licensed_derivatives]
    p2 = [ld.candidate.canonical_pattern for ld in r2.licensed_derivatives]
    assert p1 == p2

def test_determinism_ism_maf3ul():
    req = _make_request('ISM_MAF3UL')
    r1  = analyze_derivative(req)
    r2  = analyze_derivative(req)
    assert r1.verdict == r2.verdict

def test_determinism_deferred():
    req = _make_request('MUBALGHA', root=('خ', 'ض', 'ر'))
    r1  = analyze_derivative(req)
    r2  = analyze_derivative(req)
    assert r1.verdict == r2.verdict
    assert r1.verdict == 'DERIVATIVE_DEFERRED'

@pytest.mark.parametrize('dtype', [
    'ISM_FA3IL', 'ISM_MAF3UL', 'SIFA_MUSHABBAHA', 'MUBALGHA',
    'ISM_ZAMAN', 'ISM_MAKAN', 'ISM_ALA', 'auto',
])
def test_determinism_all_types(dtype):
    req = _make_request(dtype)
    r1  = analyze_derivative(req)
    r2  = analyze_derivative(req)
    assert r1.verdict == r2.verdict


# ── No ACCEPTED after upstream block ─────────────────────────────────────────

def test_no_accepted_after_root_block():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    assert result.verdict != 'DERIVATIVE_ACCEPTED'
    assert len(result.licensed_derivatives) == 0

def test_no_accepted_after_pattern_block():
    req = _make_request(licensed_pattern=None)
    result = analyze_derivative(req)
    assert result.verdict != 'DERIVATIVE_ACCEPTED'


# ── Root preserved in licensed derivatives ───────────────────────────────────

def test_root_preserved_in_licensed_fa3il():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    for ld in result.licensed_derivatives:
        assert ld.candidate.root is not None
        root_set = set(ld.candidate.root)
        assert root_set & {'ك', 'ت', 'ب'}  # all three should be present

def test_root_preserved_in_licensed_maf3ul():
    req = _make_request('ISM_MAF3UL')
    result = analyze_derivative(req)
    for ld in result.licensed_derivatives:
        assert ld.candidate.root is not None


# ── JSON round-trip preserves verdict ────────────────────────────────────────

def test_json_roundtrip_verdict_fa3il():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    d = result.to_dict()
    serialized = json.dumps(d, ensure_ascii=False)
    restored = json.loads(serialized)
    assert restored['verdict'] == result.verdict

def test_json_roundtrip_verdict_deferred():
    req = _make_request('MUBALGHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    d = result.to_dict()
    serialized = json.dumps(d, ensure_ascii=False)
    restored = json.loads(serialized)
    assert restored['verdict'] == 'DERIVATIVE_DEFERRED'

def test_json_roundtrip_verdict_blocked():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    d = result.to_dict()
    serialized = json.dumps(d, ensure_ascii=False)
    restored = json.loads(serialized)
    assert restored['verdict'] == 'DERIVATIVE_BLOCKED'

def test_json_roundtrip_verdict_residual():
    req = _make_request('ISM_ALA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    d = result.to_dict()
    serialized = json.dumps(d, ensure_ascii=False)
    restored = json.loads(serialized)
    assert restored['verdict'] == 'DERIVATIVE_RESIDUAL'


# ── Trace completeness ────────────────────────────────────────────────────────

def test_trace_non_empty():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    assert len(result.trace) > 0

def test_trace_events_have_steps():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    steps = [t.step for t in result.trace]
    assert steps == sorted(steps)

def test_trace_starts_at_gate():
    req = _make_request('ISM_FA3IL')
    result = analyze_derivative(req)
    assert result.trace[0].stage == 'GATE'
