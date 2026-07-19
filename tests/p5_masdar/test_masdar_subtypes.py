#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_subtypes.py — Masdar subtype contract tests"""
import pytest
from pipeline.p5_masdar.engine import analyze_masdar
from pipeline.p5_masdar.models import MasdarRequest


def _req(masdar_type):
    return MasdarRequest(
        request_id='SUBTYPE-TEST',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host='كَتَبَ',
        verbal_lemma=None,
        licensed_root=('ك', 'ت', 'ب'),
        licensed_root_class='SOUND',
        licensed_pattern='FA3ALA',
        verb_form_family='FORM_I',
        voice=None,
        available_context=(),
        requested_masdar_type=masdar_type,
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )


def test_masdar_mimi_deferred():
    result = analyze_masdar(_req('MASDAR_MIMI'))
    assert result.verdict == 'MASDAR_DEFERRED'
    assert result.deferred is not None
    assert 'MIMI' in result.deferred.reason


def test_masdar_marra_deferred():
    result = analyze_masdar(_req('MASDAR_MARRA'))
    assert result.verdict == 'MASDAR_DEFERRED'
    assert result.deferred is not None
    assert 'MASDAR_SUBTYPE_CONTEXT_REQUIRED' in result.deferred.reason


def test_masdar_hayaa_deferred():
    result = analyze_masdar(_req('MASDAR_HAYAA'))
    assert result.verdict == 'MASDAR_DEFERRED'
    assert result.deferred is not None
    assert 'MASDAR_SUBTYPE_CONTEXT_REQUIRED' in result.deferred.reason


def test_ism_masdar_residual():
    result = analyze_masdar(_req('ISM_MASDAR'))
    assert result.verdict == 'MASDAR_RESIDUAL'
    assert len(result.residuals) >= 1
    assert result.residuals[0].residual_code == 'ISM_MASDAR_LEXICON_GAP'


def test_ism_masdar_has_no_licensed_masdars():
    result = analyze_masdar(_req('ISM_MASDAR'))
    assert result.licensed_masdars == ()


def test_mimi_has_no_licensed_masdars():
    result = analyze_masdar(_req('MASDAR_MIMI'))
    assert result.licensed_masdars == ()


def test_marra_has_no_licensed_masdars():
    result = analyze_masdar(_req('MASDAR_MARRA'))
    assert result.licensed_masdars == ()


def test_hayaa_has_no_licensed_masdars():
    result = analyze_masdar(_req('MASDAR_HAYAA'))
    assert result.licensed_masdars == ()


def test_mimi_missing_evidence_contains_lexical():
    result = analyze_masdar(_req('MASDAR_MIMI'))
    assert result.deferred is not None
    assert 'LEXICAL_MASDAR_ATTESTATION' in result.deferred.missing_evidence


def test_marra_missing_evidence_contains_paradigm():
    result = analyze_masdar(_req('MASDAR_MARRA'))
    assert result.deferred is not None
    assert 'PARADIGM_CROSS_FORM_EVIDENCE' in result.deferred.missing_evidence
