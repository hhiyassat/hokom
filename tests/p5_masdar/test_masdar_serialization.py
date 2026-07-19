#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_serialization.py — Serialization tests"""
import json
import pytest
from pipeline.p5_masdar.engine import analyze_masdar
from pipeline.p5_masdar.models import MasdarRequest, MASDAR_ENGINE_ID


def _req(ff='FORM_II', root=('ك', 'ت', 'ب'), pattern='FA33ALA', verbal_host='test'):
    return MasdarRequest(
        request_id='SER-TEST',
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


def test_to_dict_is_json_serializable():
    req = _req()
    result = analyze_masdar(req)
    d = result.to_dict()
    # Should not raise
    s = json.dumps(d, ensure_ascii=False)
    assert len(s) > 10


def test_json_loads_has_verdict():
    req = _req()
    result = analyze_masdar(req)
    d = json.loads(json.dumps(result.to_dict(), ensure_ascii=False))
    assert d['verdict'] == result.verdict


def test_json_loads_has_multiplicity():
    req = _req()
    result = analyze_masdar(req)
    d = json.loads(json.dumps(result.to_dict(), ensure_ascii=False))
    assert 'multiplicity' in d


def test_trace_length_preserved():
    req = _req()
    result = analyze_masdar(req)
    d = json.loads(json.dumps(result.to_dict(), ensure_ascii=False))
    assert len(d['trace']) == len(result.trace)


def test_nested_dicts_serializable():
    req = _req(ff='FORM_III', root=('ق', 'ت', 'ل'), pattern='FA3ALA')
    result = analyze_masdar(req)
    d = result.to_dict()
    # Ensure nested structures are dicts, not custom objects
    for lm in d.get('licensed_masdars', []):
        assert isinstance(lm, dict)
        assert isinstance(lm['candidate'], dict)
        for ev in lm.get('licensing_evidence', []):
            assert isinstance(ev, dict)


def test_blocked_serializable():
    req = MasdarRequest(
        request_id='SER-BLOCKED',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host=None,
        verbal_lemma=None,
        licensed_root=('ك', 'ت', 'ب'),
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
    d = result.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    assert 'verdict' in json.loads(s)


def test_deferred_serializable():
    req = MasdarRequest(
        request_id='SER-DEFERRED',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host='test',
        verbal_lemma=None,
        licensed_root=('ظ', 'م', 'أ'),
        licensed_root_class='SOUND',
        licensed_pattern='FA3ALA',
        verb_form_family='FORM_I',
        voice=None,
        available_context=(),
        requested_masdar_type=None,
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )
    result = analyze_masdar(req)
    d = result.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    d2 = json.loads(s)
    assert d2['verdict'] == 'MASDAR_DEFERRED'


def test_request_serializable():
    req = _req()
    d = req.to_dict()
    s = json.dumps(d, ensure_ascii=False)
    d2 = json.loads(s)
    assert d2['mode'] == 'GENERATE_FROM_VERB'
    assert d2['licensed_root'] == list(('ك', 'ت', 'ب'))
