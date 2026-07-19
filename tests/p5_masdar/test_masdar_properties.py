#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_properties.py — Property tests"""
import json
import pytest
from pipeline.p5_masdar.engine import analyze_masdar
from pipeline.p5_masdar.models import MasdarRequest, MASDAR_ENGINE_ID


def _req(ff='FORM_II', root=('ك', 'ت', 'ب'), verbal_host='test', pattern='FA33ALA'):
    return MasdarRequest(
        request_id='PROP-TEST',
        mode='GENERATE_FROM_VERB',
        original_surface='surface',
        normalized_surface='surface',
        verbal_host=verbal_host,
        verbal_lemma=None,
        licensed_root=tuple(root),
        licensed_root_class='SOUND',
        licensed_pattern=pattern,
        verb_form_family=ff,
        voice=None,
        available_context=(),
        requested_masdar_type=None,
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )


# ── PROPERTY 1: determinism ───────────────────────────────────────────────────

@pytest.mark.parametrize('ff,pattern', [
    ('FORM_I',  'FA3ALA'),
    ('FORM_II', 'FA33ALA'),
    ('FORM_X',  'ISTAF3ALA'),
])
def test_determinism_same_verdict(ff, pattern):
    req = _req(ff=ff, pattern=pattern)
    r1 = analyze_masdar(req)
    r2 = analyze_masdar(req)
    assert r1.verdict == r2.verdict


@pytest.mark.parametrize('ff,pattern', [
    ('FORM_II', 'FA33ALA'),
    ('FORM_X',  'ISTAF3ALA'),
])
def test_determinism_same_candidate_count(ff, pattern):
    req = _req(ff=ff, pattern=pattern)
    r1 = analyze_masdar(req)
    r2 = analyze_masdar(req)
    assert len(r1.licensed_masdars) == len(r2.licensed_masdars)


# ── PROPERTY 2: no ACCEPT after upstream block ────────────────────────────────

def test_no_accept_after_root_null():
    req = MasdarRequest(
        request_id='PROP-NULL-ROOT',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host='test',
        verbal_lemma=None,
        licensed_root=None,
        licensed_root_class='SOUND',
        licensed_pattern='FA33ALA',
        verb_form_family='FORM_II',
        voice=None,
        available_context=(),
        requested_masdar_type=None,
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )
    result = analyze_masdar(req)
    assert result.verdict != 'MASDAR_ACCEPTED'


# ── PROPERTY 3: root preserved in all licensed_masdars ───────────────────────

def test_root_preserved_in_licensed_masdars():
    root = ('ع', 'ل', 'م')
    req = _req(ff='FORM_II', root=root, pattern='FA33ALA')
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_ACCEPTED'
    for lm in result.licensed_masdars:
        assert lm.candidate.root == root


# ── PROPERTY 4: JSON round-trip ───────────────────────────────────────────────

def test_json_roundtrip_preserves_verdict():
    req = _req(ff='FORM_II', pattern='FA33ALA')
    result = analyze_masdar(req)
    d = result.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    d2 = json.loads(s)
    assert d2['verdict'] == result.verdict


def test_json_roundtrip_preserves_multiplicity():
    req = _req(ff='FORM_III', root=('ق', 'ت', 'ل'), pattern='FA3ALA')
    result = analyze_masdar(req)
    d = result.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    d2 = json.loads(s)
    assert d2['multiplicity'] == result.multiplicity


def test_json_roundtrip_preserves_source_engine():
    req = _req(ff='FORM_II', pattern='FA33ALA')
    result = analyze_masdar(req)
    d = result.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    d2 = json.loads(s)
    assert d2['source_engine'] == MASDAR_ENGINE_ID


# ── PROPERTY 5: trace always present ─────────────────────────────────────────

def test_trace_always_present():
    req = _req(ff='FORM_II', pattern='FA33ALA')
    result = analyze_masdar(req)
    assert len(result.trace) >= 1


def test_trace_steps_sequential():
    req = _req(ff='FORM_II', pattern='FA33ALA')
    result = analyze_masdar(req)
    steps = [t.step for t in result.trace]
    assert steps == list(range(1, len(steps) + 1))
