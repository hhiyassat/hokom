#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_engine_ism_fa3il.py — ISM_FA3IL engine tests"""
import pytest
from pipeline.p6_derivatives.engine import analyze_derivative
from pipeline.p6_derivatives.models import DerivativeRequest


def _make_request(form_family='FORM_I', dtype='ISM_FA3IL', **kwargs):
    defaults = dict(
        request_id='REQ-FA3IL-001',
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

def test_ism_fa3il_form_i_accepted():
    req = _make_request('FORM_I')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'
    assert result.source_engine == 'HOKOM_DERIVATIVES_ENGINE'

def test_ism_fa3il_form_i_pattern_fa3il():
    req = _make_request('FORM_I')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'FA3IL' in patterns

def test_ism_fa3il_form_i_root_preserved():
    req = _make_request('FORM_I')
    result = analyze_derivative(req)
    for ld in result.licensed_derivatives:
        assert ld.candidate.root is not None
        assert 'ك' in ld.candidate.root

def test_ism_fa3il_form_i_derivative_type():
    req = _make_request('FORM_I')
    result = analyze_derivative(req)
    for ld in result.licensed_derivatives:
        assert ld.candidate.derivative_type == 'ISM_FA3IL'


# ── FORM_II ───────────────────────────────────────────────────────────────────

def test_ism_fa3il_form_ii_accepted():
    req = _make_request('FORM_II', licensed_pattern='FA33ALA', verbal_lemma='عَلَّمَ',
                        verbal_host='عَلَّمَ', licensed_root=('ع', 'ل', 'م'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_form_ii_pattern_mufa33il():
    req = _make_request('FORM_II', licensed_pattern='FA33ALA', verbal_lemma='عَلَّمَ',
                        verbal_host='عَلَّمَ', licensed_root=('ع', 'ل', 'م'))
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUFA33IL' in patterns


# ── FORM_III ──────────────────────────────────────────────────────────────────

def test_ism_fa3il_form_iii_accepted():
    req = _make_request('FORM_III', licensed_pattern='FA3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_form_iii_pattern_mufa3il():
    req = _make_request('FORM_III', licensed_pattern='FA3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUFA3IL' in patterns


# ── FORM_IV ───────────────────────────────────────────────────────────────────

def test_ism_fa3il_form_iv_accepted():
    req = _make_request('FORM_IV', licensed_pattern='AF3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_form_iv_pattern_muf3il():
    req = _make_request('FORM_IV', licensed_pattern='AF3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUF3IL' in patterns


# ── FORM_V ────────────────────────────────────────────────────────────────────

def test_ism_fa3il_form_v_accepted():
    req = _make_request('FORM_V', licensed_pattern='TAFA33ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_form_v_pattern_mutafa33il():
    req = _make_request('FORM_V', licensed_pattern='TAFA33ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUTAFA33IL' in patterns


# ── FORM_VI ───────────────────────────────────────────────────────────────────

def test_ism_fa3il_form_vi_accepted():
    req = _make_request('FORM_VI', licensed_pattern='TAFA3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_form_vi_pattern_mutafa3il():
    req = _make_request('FORM_VI', licensed_pattern='TAFA3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUTAFA3IL' in patterns


# ── FORM_VII ──────────────────────────────────────────────────────────────────

def test_ism_fa3il_form_vii_accepted():
    req = _make_request('FORM_VII', licensed_pattern='INFA3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_form_vii_pattern_munfa3il():
    req = _make_request('FORM_VII', licensed_pattern='INFA3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUNFA3IL' in patterns


# ── FORM_VIII ─────────────────────────────────────────────────────────────────

def test_ism_fa3il_form_viii_accepted():
    req = _make_request('FORM_VIII', licensed_pattern='IFTA3ALA',
                        verbal_lemma='اِجْتَهَدَ', verbal_host='اِجْتَهَدَ',
                        licensed_root=('ج', 'ه', 'د'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_form_viii_pattern_mufta3il():
    req = _make_request('FORM_VIII', licensed_pattern='IFTA3ALA',
                        verbal_lemma='اِجْتَهَدَ', verbal_host='اِجْتَهَدَ',
                        licensed_root=('ج', 'ه', 'د'))
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUFTA3IL' in patterns


# ── FORM_X ────────────────────────────────────────────────────────────────────

def test_ism_fa3il_form_x_accepted():
    req = _make_request('FORM_X', licensed_pattern='ISTAF3ALA')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_form_x_pattern_mustaf3il():
    req = _make_request('FORM_X', licensed_pattern='ISTAF3ALA')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'MUSTAF3IL' in patterns


# ── FA3IL_PARTICIPLE treated as FORM_I (RULE-D-01) ──────────────────────────

def test_ism_fa3il_fa3il_participle_accepted():
    """FA3IL_PARTICIPLE routing tag → treated as FORM_I for ISM_FA3IL."""
    req = _make_request('FA3IL_PARTICIPLE')
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_fa3il_fa3il_participle_pattern_fa3il():
    req = _make_request('FA3IL_PARTICIPLE')
    result = analyze_derivative(req)
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert 'FA3IL' in patterns


# ── Parametrized coverage ──────────────────────────────────────────────────────

@pytest.mark.parametrize('form_family,expected_pattern', [
    ('FORM_I',   'FA3IL'),
    ('FORM_II',  'MUFA33IL'),
    ('FORM_III', 'MUFA3IL'),
    ('FORM_IV',  'MUF3IL'),
    ('FORM_V',   'MUTAFA33IL'),
    ('FORM_VI',  'MUTAFA3IL'),
    ('FORM_VII', 'MUNFA3IL'),
    ('FORM_VIII','MUFTA3IL'),
    ('FORM_X',   'MUSTAF3IL'),
    ('FA3IL_PARTICIPLE', 'FA3IL'),
])
def test_ism_fa3il_parametrized(form_family, expected_pattern):
    req = _make_request(form_family)
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED', \
        f'{form_family}: expected DERIVATIVE_ACCEPTED, got {result.verdict}'
    patterns = [ld.candidate.canonical_pattern for ld in result.licensed_derivatives]
    assert expected_pattern in patterns, \
        f'{form_family}: expected {expected_pattern} in {patterns}'
