#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_engine_other_types.py — Other derivative types"""
import pytest
from pipeline.p6_derivatives.engine import analyze_derivative
from pipeline.p6_derivatives.models import DerivativeRequest


def _make_request(dtype, form_family='FORM_I', root=('ك', 'ت', 'ب'), **kwargs):
    defaults = dict(
        request_id=f'REQ-{dtype}-001',
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


# ── SIFA_MUSHABBAHA ───────────────────────────────────────────────────────────

def test_sifa_without_lexical_evidence_deferred():
    """SIFA_MUSHABBAHA without lexical attestation → DERIVATIVE_DEFERRED."""
    # Use an unknown root with no lexical entry
    req = _make_request('SIFA_MUSHABBAHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_DEFERRED'

def test_sifa_deferred_reason():
    req = _make_request('SIFA_MUSHABBAHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.deferred is not None
    assert 'SIFA' in result.deferred.reason or 'VERBAL_EVIDENCE' in result.deferred.reason

def test_sifa_missing_evidence_attestation():
    req = _make_request('SIFA_MUSHABBAHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert 'LEXICAL_DERIVATIVE_ATTESTATION' in (result.deferred.missing_evidence if result.deferred else ())

def test_sifa_source_engine():
    req = _make_request('SIFA_MUSHABBAHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.source_engine == 'HOKOM_DERIVATIVES_ENGINE'


# ── MUBALGHA ─────────────────────────────────────────────────────────────────

def test_mubalgha_without_lexical_evidence_deferred():
    """MUBALGHA without lexical attestation → DERIVATIVE_DEFERRED."""
    req = _make_request('MUBALGHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_DEFERRED'

def test_mubalgha_deferred_reason():
    req = _make_request('MUBALGHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.deferred is not None
    assert 'MUBALGHA' in result.deferred.reason

def test_mubalgha_with_lexical_evidence_accepted():
    """كَتَبَ has a MUBALGHA entry (كَتَّاب)."""
    req = _make_request('MUBALGHA', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_mubalgha_source_engine():
    req = _make_request('MUBALGHA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.source_engine == 'HOKOM_DERIVATIVES_ENGINE'


# ── ISM_ZAMAN ─────────────────────────────────────────────────────────────────

def test_ism_zaman_without_lexical_evidence_deferred():
    """ISM_ZAMAN without lexical discriminator → DERIVATIVE_DEFERRED (RULE-D-02)."""
    req = _make_request('ISM_ZAMAN', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_DEFERRED'

def test_ism_zaman_ambiguity_reason():
    req = _make_request('ISM_ZAMAN', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.deferred is not None
    assert 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY' in result.deferred.reason

def test_ism_zaman_with_lexical_discriminator_accepted():
    """كَتَبَ has ISM_ZAMAN lexical entry with lexical_discriminator=ISM_ZAMAN."""
    req = _make_request('ISM_ZAMAN', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_zaman_accepted_type():
    req = _make_request('ISM_ZAMAN', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    for ld in result.licensed_derivatives:
        assert ld.candidate.derivative_type == 'ISM_ZAMAN'


# ── ISM_MAKAN ─────────────────────────────────────────────────────────────────

def test_ism_makan_without_lexical_evidence_deferred():
    req = _make_request('ISM_MAKAN', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_DEFERRED'

def test_ism_makan_ambiguity_reason():
    req = _make_request('ISM_MAKAN', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.deferred is not None
    assert 'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY' in result.deferred.reason

def test_ism_makan_with_lexical_discriminator_accepted():
    """كَتَبَ has ISM_MAKAN entry with lexical_discriminator=ISM_MAKAN."""
    req = _make_request('ISM_MAKAN', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_makan_accepted_type():
    req = _make_request('ISM_MAKAN', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    for ld in result.licensed_derivatives:
        assert ld.candidate.derivative_type == 'ISM_MAKAN'


# ── ISM_ALA ───────────────────────────────────────────────────────────────────

def test_ism_ala_without_lexical_evidence_residual():
    """ISM_ALA without lexical entry → DERIVATIVE_RESIDUAL (RULE-D-03)."""
    req = _make_request('ISM_ALA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_RESIDUAL'

def test_ism_ala_residual_code():
    req = _make_request('ISM_ALA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert len(result.residuals) >= 1
    assert result.residuals[0].residual_code == 'ISM_ALA_LEXICON_GAP'

def test_ism_ala_with_lexical_evidence_accepted():
    """كَتَبَ has an ISM_ALA lexical entry (مِكْتَاب)."""
    req = _make_request('ISM_ALA', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_ism_ala_source_engine():
    req = _make_request('ISM_ALA', root=('خ', 'ض', 'ر'))
    result = analyze_derivative(req)
    assert result.source_engine == 'HOKOM_DERIVATIVES_ENGINE'


# ── auto mode ─────────────────────────────────────────────────────────────────

def test_auto_mode_accepted():
    req = _make_request('auto', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    assert result.verdict == 'DERIVATIVE_ACCEPTED'

def test_auto_mode_generates_both_types():
    req = _make_request('auto', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    types = {ld.candidate.derivative_type for ld in result.licensed_derivatives}
    assert 'ISM_FA3IL' in types
    assert 'ISM_MAF3UL' in types

def test_auto_mode_multiple_licensed():
    req = _make_request('auto', root=('ك', 'ت', 'ب'))
    result = analyze_derivative(req)
    assert result.multiplicity == 'MULTIPLE_LICENSED'
