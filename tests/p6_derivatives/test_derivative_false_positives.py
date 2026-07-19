#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_false_positives.py — False positive guards"""
import pytest
from pipeline.p6_derivatives.engine import analyze_derivative
from pipeline.p6_derivatives.models import DerivativeRequest


def _make_request(dtype='ISM_FA3IL', **kwargs):
    defaults = dict(
        request_id='REQ-FP-001',
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
        derivative_type=dtype,
        supplied_derivative_surface=None,
        evidence=(),
        upstream_trace=(),
    )
    defaults.update(kwargs)
    return DerivativeRequest(**defaults)


# ── Missing licensed_root → BLOCKED ──────────────────────────────────────────

def test_missing_root_blocked():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_BLOCKED'

def test_missing_root_blocked_reason():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    assert result.blocked is not None
    assert 'ROOT_NOT_LICENSED' in result.blocked.reason

def test_missing_root_no_licensed_derivatives():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    assert len(result.licensed_derivatives) == 0


# ── Missing licensed_pattern → BLOCKED ───────────────────────────────────────

def test_missing_pattern_blocked():
    req = _make_request(licensed_pattern=None)
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_BLOCKED'

def test_missing_pattern_blocked_reason():
    req = _make_request(licensed_pattern=None)
    result = analyze_derivative(req)
    assert result.blocked is not None
    assert 'PATTERN_NOT_LICENSED' in result.blocked.reason


# ── Missing verbal_host AND verbal_lemma → DEFERRED ──────────────────────────

def test_missing_verbhood_deferred():
    req = _make_request(verbal_host=None, verbal_lemma=None)
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_DEFERRED'

def test_missing_verbhood_deferred_reason():
    req = _make_request(verbal_host=None, verbal_lemma=None)
    result = analyze_derivative(req)
    assert result.deferred is not None
    assert 'VERBHOOD_NOT_LICENSED' in result.deferred.reason

def test_missing_verbhood_no_licensed_derivatives():
    req = _make_request(verbal_host=None, verbal_lemma=None)
    result = analyze_derivative(req)
    assert len(result.licensed_derivatives) == 0


# ── SIFA surface pattern alone insufficient ───────────────────────────────────

def test_sifa_pattern_alone_insufficient():
    """Surface pattern match alone is insufficient for SIFA_MUSHABBAHA."""
    req = _make_request(
        dtype='SIFA_MUSHABBAHA',
        licensed_root=('خ', 'ض', 'ر'),  # no lexical entry
    )
    result = analyze_derivative(req)
    # Must not be ACCEPTED without lexical evidence
    assert result.verdict != 'DERIVATIVE_ACCEPTED'

def test_mubalgha_pattern_alone_insufficient():
    """Surface pattern match alone is insufficient for MUBALGHA."""
    req = _make_request(
        dtype='MUBALGHA',
        licensed_root=('خ', 'ض', 'ر'),  # no lexical entry
    )
    result = analyze_derivative(req)
    assert result.verdict != 'DERIVATIVE_ACCEPTED'


# ── Masdar surface does not leak into derivative result ───────────────────────

def test_masdar_surface_does_not_leak():
    """
    Derivative engine must not produce masdar surfaces.
    The MASDAR_MIMI_LEAKAGE_PREVENTION gate ensures this.
    """
    req = _make_request(dtype='ISM_FA3IL')
    result = analyze_derivative(req)
    # All licensed derivatives must be ISM_FA3IL, not masdar types
    for ld in result.licensed_derivatives:
        assert ld.candidate.derivative_type == 'ISM_FA3IL'
        assert ld.candidate.derivative_type not in (
            'MASDAR_ASLI', 'MASDAR_MIMI', 'MASDAR_MARRA', 'MASDAR_HAYAA', 'ISM_MASDAR'
        )

def test_masdar_leakage_blocked_result_has_no_masdar_candidates():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_BLOCKED'
    assert len(result.all_candidates) == 0


# ── ISM_ALA without evidence → RESIDUAL, not guessed ────────────────────────

def test_ism_ala_without_evidence_is_residual_not_accepted():
    req = _make_request(dtype='ISM_ALA', licensed_root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_RESIDUAL'
    assert len(result.licensed_derivatives) == 0


# ── blocked result structure ──────────────────────────────────────────────────

def test_blocked_result_has_no_deferred():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_BLOCKED'
    assert result.deferred is None

def test_blocked_result_has_contradictions():
    req = _make_request(licensed_root=None)
    result = analyze_derivative(req)
    assert result.blocked is not None
    assert len(result.blocked.contradictions) >= 1
