#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_engine_form_i.py — FORM_I lexical masdar tests"""
import pytest
from pipeline.p5_masdar.engine import analyze_masdar
from pipeline.p5_masdar.models import MasdarRequest


def _req_form_i(root, pattern='FA3ALA', verbal_host='test', verbal_lemma=None):
    return MasdarRequest(
        request_id='TEST-F1',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host=verbal_host,
        verbal_lemma=verbal_lemma,
        licensed_root=tuple(root),
        licensed_root_class='SOUND',
        licensed_pattern=pattern,
        verb_form_family='FORM_I',
        voice=None,
        available_context=(),
        requested_masdar_type=None,
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )


# ── كَتَبَ → MASDAR_ACCEPTED ────────────────────────────────────────────────────

def test_kataba_accepted():
    req = _req_form_i(('ك', 'ت', 'ب'))
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_ACCEPTED'
    assert len(result.licensed_masdars) >= 1
    surfaces = [lm.candidate.surface for lm in result.licensed_masdars]
    assert 'كتابة' in surfaces


def test_kataba_single_multiplicity():
    req = _req_form_i(('ك', 'ت', 'ب'))
    result = analyze_masdar(req)
    assert result.multiplicity == 'SINGLE'


# ── عَلِمَ → MASDAR_ACCEPTED ────────────────────────────────────────────────────

def test_3alima_accepted():
    req = _req_form_i(('ع', 'ل', 'م'), pattern='FA3ILA')
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_ACCEPTED'
    surfaces = [lm.candidate.surface for lm in result.licensed_masdars]
    assert 'عِلْم' in surfaces


# ── unknown root → MASDAR_DEFERRED FORM_I_LEXICAL_EVIDENCE_REQUIRED ────────────

def test_unknown_root_deferred():
    req = _req_form_i(('ص', 'ع', 'ق'))
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_DEFERRED'
    assert result.deferred is not None
    assert 'FORM_I_LEXICAL_EVIDENCE_REQUIRED' in result.deferred.reason


# ── قَاتَلَ (FORM_III) → MULTIPLE_LICENSED ────────────────────────────────────

def test_qatala_form_iii_multiple():
    req = MasdarRequest(
        request_id='TEST-QATALA',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host='قَاتَلَ',
        verbal_lemma=None,
        licensed_root=('ق', 'ت', 'ل'),
        licensed_root_class='SOUND',
        licensed_pattern='FA3ALA',
        verb_form_family='FORM_III',
        voice=None,
        available_context=(),
        requested_masdar_type=None,
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_ACCEPTED'
    assert result.multiplicity == 'MULTIPLE_LICENSED'
    assert len(result.licensed_masdars) == 2
    patterns = {lm.candidate.canonical_pattern for lm in result.licensed_masdars}
    assert 'MUFA3ALA' in patterns
    assert 'FI3AL' in patterns


# ── deterministic ordering ─────────────────────────────────────────────────────

def test_form_i_deterministic_ordering():
    req = _req_form_i(('ك', 'ت', 'ب'))
    r1 = analyze_masdar(req)
    r2 = analyze_masdar(req)
    patterns1 = [lm.candidate.canonical_pattern for lm in r1.licensed_masdars]
    patterns2 = [lm.candidate.canonical_pattern for lm in r2.licensed_masdars]
    assert patterns1 == patterns2


# ── lexical_attestation flag set ───────────────────────────────────────────────

def test_form_i_lexical_attestation_flag():
    req = _req_form_i(('ك', 'ت', 'ب'))
    result = analyze_masdar(req)
    for lm in result.licensed_masdars:
        assert lm.candidate.lexical_attestation is True


# ── license_kind is LEXICAL_ATTESTATION ───────────────────────────────────────

def test_form_i_license_kind():
    req = _req_form_i(('ك', 'ت', 'ب'))
    result = analyze_masdar(req)
    for lm in result.licensed_masdars:
        assert lm.candidate.license_kind == 'LEXICAL_ATTESTATION'
