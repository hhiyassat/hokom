#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_false_positives.py — False positive guard tests"""
import pytest
from pipeline.p5_masdar.engine import analyze_masdar
from pipeline.p5_masdar.models import MasdarRequest


def _req(**kw):
    defaults = dict(
        request_id='FP-TEST',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host=None,
        verbal_lemma=None,
        licensed_root=('ك', 'ت', 'ب'),
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
    defaults.update(kw)
    return MasdarRequest(**defaults)


# ── no verbal host or lemma → MASDAR_DEFERRED (not ACCEPTED) ─────────────────

def test_no_verbal_anchor_not_accepted():
    req = _req(verbal_host=None, verbal_lemma=None)
    result = analyze_masdar(req)
    assert result.verdict != 'MASDAR_ACCEPTED'
    assert result.verdict in ('MASDAR_DEFERRED', 'MASDAR_BLOCKED')


# ── non-verbal form_family → MASDAR_BLOCKED ───────────────────────────────────

def test_fa3il_participle_blocked():
    req = _req(verb_form_family='FA3IL_PARTICIPLE', verbal_host='كَاتِب',
               licensed_pattern='FA3IL')
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_BLOCKED'
    assert result.licensed_masdars == ()


# ── VALIDATE mode with ROOT_MISMATCH → MASDAR_DEFERRED ───────────────────────

def test_validate_mode_root_mismatch_deferred():
    req = _req(
        mode='VALIDATE_SUPPLIED_MASDAR',
        verbal_host='test',
        licensed_root=('م', 'ج', 'ه'),  # root not in lexicon
        verb_form_family='FORM_I',
        supplied_masdar_surface='مجهة',
    )
    result = analyze_masdar(req)
    # Not MASDAR_ACCEPTED — either DEFERRED or BLOCKED
    assert result.verdict in ('MASDAR_DEFERRED', 'MASDAR_BLOCKED')
    assert result.licensed_masdars == ()


# ── licensed_root=None → always blocked, never accepted ──────────────────────

def test_null_root_never_accepted():
    req = _req(licensed_root=None, verbal_host='test')
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_BLOCKED'
    assert result.licensed_masdars == ()


# ── licensed_pattern=None → always blocked ────────────────────────────────────

def test_null_pattern_never_accepted():
    req = _req(licensed_pattern=None, verbal_host='test')
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_BLOCKED'
    assert result.licensed_masdars == ()


# ── no licensed_masdars on BLOCKED result ─────────────────────────────────────

def test_blocked_has_no_licensed_masdars():
    req = _req(licensed_root=None, verbal_host='test')
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_BLOCKED'
    assert len(result.licensed_masdars) == 0


# ── no licensed_masdars on DEFERRED result ────────────────────────────────────

def test_deferred_has_no_licensed_masdars():
    req = _req(verbal_host=None, verbal_lemma=None)
    result = analyze_masdar(req)
    assert result.verdict != 'MASDAR_ACCEPTED'
    assert len(result.licensed_masdars) == 0


# ── unknown root for FORM_I never guessed ─────────────────────────────────────

def test_form_i_unknown_root_never_guessed():
    req = _req(licensed_root=('ظ', 'م', 'أ'), verbal_host='ظَمَأَ')
    result = analyze_masdar(req)
    # Should DEFER, not guess a masdar
    assert result.verdict == 'MASDAR_DEFERRED'
    assert len(result.licensed_masdars) == 0


# ── ANALYZE_MASDAR_SURFACE → always deferred (needs verbal anchor) ────────────

def test_analyze_surface_mode_deferred():
    req = _req(
        mode='ANALYZE_MASDAR_SURFACE',
        verbal_host='test',
        original_surface='كِتَابَة',
    )
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_DEFERRED'
