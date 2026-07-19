#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_engine_ism_maf3ul.py — ISM_MAF3UL engine tests"""
import pytest
from pipeline.p6_derivatives.engine import analyze_derivative
from pipeline.p6_derivatives.models import DerivativeRequest


def _make_request(form_family='FORM_I', dtype='ISM_MAF3UL', **kwargs):
    defaults = dict(
        request_id='REQ-MAF3UL-001',
        mode='GENERATE_FROM_VERB',
        original_surface='كَتَبَ',
        normalized_surface='كَتَبَ',
        verbal_host='كَتَبَ',
        verbal_lemma='كَتَبَ',
        licensed_root=('ك', 'ت', 'ب'),
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


# ── FORM_I ────────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_i_accepted():
    req = _make_request('FORM_I')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'
    assert result.source_engine == 'HOKOM_DERIVATIVES_ENGINE'

def test_ism_maf3ul_form_i_pattern_maf3ul():
    req = _make_request('FORM_I')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MAF3UL' in patterns

def test_ism_maf3ul_form_i_root_preserved():
    req = _make_request('FORM_I')
    result = analyze_derivative(req)
    for ld in result.licensed_derivatives:
        assert ld.candidate.root is not None
        assert 'ك' in ld.candidate.root

def test_ism_maf3ul_form_i_derivative_type():
    req = _make_request('FORM_I')
    result = analyze_derivative(req)
    for ld in result.licensed_derivatives:
        assert ld.candidate.derivative_type == 'ISM_MAF3UL'


# ── FORM_II ───────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_ii_accepted():
    req = _make_request('FORM_II', licensed_pattern='FA33ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_maf3ul_form_ii_pattern_mufa33al():
    req = _make_request('FORM_II', licensed_pattern='FA33ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUFA33AL' in patterns


# ── FORM_III ──────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_iii_accepted():
    req = _make_request('FORM_III', licensed_pattern='FA3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_maf3ul_form_iii_pattern_mufa3al():
    req = _make_request('FORM_III', licensed_pattern='FA3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUFA3AL' in patterns


# ── FORM_IV ───────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_iv_accepted():
    req = _make_request('FORM_IV', licensed_pattern='AF3ALA',
                        verbal_lemma='أَرْسَلَ', verbal_host='أَرْسَلَ',
                        licensed_root=('ر', 'س', 'ل'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_maf3ul_form_iv_pattern_muf3al():
    req = _make_request('FORM_IV', licensed_pattern='AF3ALA',
                        verbal_lemma='أَرْسَلَ', verbal_host='أَرْسَلَ',
                        licensed_root=('ر', 'س', 'ل'))
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUF3AL' in patterns


# ── FORM_V ────────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_v_accepted():
    req = _make_request('FORM_V', licensed_pattern='TAFA33ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_maf3ul_form_v_pattern_mutafa33al():
    req = _make_request('FORM_V', licensed_pattern='TAFA33ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUTAFA33AL' in patterns


# ── FORM_VI ───────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_vi_accepted():
    req = _make_request('FORM_VI', licensed_pattern='TAFA3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_maf3ul_form_vi_pattern_mutafa3al():
    req = _make_request('FORM_VI', licensed_pattern='TAFA3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUTAFA3AL' in patterns


# ── FORM_VII ──────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_vii_accepted():
    req = _make_request('FORM_VII', licensed_pattern='INFA3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_maf3ul_form_vii_pattern_munfa3al():
    req = _make_request('FORM_VII', licensed_pattern='INFA3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUNFA3AL' in patterns


# ── FORM_VIII ─────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_viii_accepted():
    req = _make_request('FORM_VIII', licensed_pattern='IFTA3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_maf3ul_form_viii_pattern_mufta3al():
    req = _make_request('FORM_VIII', licensed_pattern='IFTA3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUFTA3AL' in patterns


# ── FORM_X ────────────────────────────────────────────────────────────────────

def test_ism_maf3ul_form_x_accepted():
    req = _make_request('FORM_X', licensed_pattern='ISTAF3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_maf3ul_form_x_pattern_mustaf3al():
    req = _make_request('FORM_X', licensed_pattern='ISTAF3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUSTAF3AL' in patterns


# ── Parametrized coverage ──────────────────────────────────────────────────────

@pytest.mark.parametrize('form_family,expected_pattern', [
    ('FORM_I',   'MAF3UL'),
    ('FORM_II',  'MUFA33AL'),
    ('FORM_III', 'MUFA3AL'),
    ('FORM_IV',  'MUF3AL'),
    ('FORM_V',   'MUTAFA33AL'),
    ('FORM_VI',  'MUTAFA3AL'),
    ('FORM_VII', 'MUNFA3AL'),
    ('FORM_VIII','MUFTA3AL'),
    ('FORM_X',   'MUSTAF3AL'),
])
def test_ism_maf3ul_parametrized(form_family, expected_pattern):
    req = _make_request(form_family)
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED', \
        f'{form_family}: expected DERIVATIVE_ACCEPTED, got {result.verdict}'
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert expected_pattern in patterns, \
        f'{form_family}: expected {expected_pattern} in {patterns}'
