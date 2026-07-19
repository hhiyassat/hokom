#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_engine_augmented.py — Augmented form masdar tests"""
import pytest
from pipeline.p5_masdar.engine import analyze_masdar
from pipeline.p5_masdar.models import MasdarRequest, MASDAR_ENGINE_ID


def _req(ff, root=('ك', 'س', 'ر'), pattern='FA33ALA', verbal_host='test', **kw):
    return MasdarRequest(
        request_id='TEST-001',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host=verbal_host,
        verbal_lemma=None,
        licensed_root=tuple(root),
        licensed_root_class=kw.get('root_class', 'SOUND'),
        licensed_pattern=pattern,
        verb_form_family=ff,
        voice=None,
        available_context=(),
        requested_masdar_type=kw.get('masdar_type', None),
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )


# ── augmented forms → MASDAR_ACCEPTED ────────────────────────────────────────

@pytest.mark.parametrize('ff,pattern,expected_masdar_pattern', [
    ('FORM_II',  'FA33ALA',  'TAF3IL'),
    ('FORM_IV',  'AF3AL',    'IF3AL'),
    ('FORM_V',   'TAFA33ALA','TAFA33UL'),
    ('FORM_VI',  'TAFA3ALA', 'TAFA3UL'),
    ('FORM_VII', 'INFA3ALA', 'INFI3AL'),
    ('FORM_VIII','IFTA3ALA', 'IFTI3AL'),
    ('FORM_IX',  'IF3ALLA',  'IF3ILAL'),
    ('FORM_X',   'ISTAF3ALA','ISTIF3AL'),
    ('QUADRILITERAL_FORM_I', 'FA3LALA', 'FA3LALA'),
])
def test_augmented_accepted(ff, pattern, expected_masdar_pattern):
    req = _req(ff, pattern=pattern)
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_ACCEPTED', (
        f'{ff}: expected MASDAR_ACCEPTED, got {result.verdict}'
    )
    assert len(result.licensed_masdars) >= 1
    patterns = [lm.candidate.canonical_pattern for lm in result.licensed_masdars]
    assert expected_masdar_pattern in patterns, (
        f'{ff}: expected {expected_masdar_pattern} in {patterns}'
    )
    assert result.source_engine == MASDAR_ENGINE_ID


def test_form_iii_multiple_masdars():
    """FORM_III should produce MULTIPLE_LICENSED (MUFA3ALA + FI3AL)."""
    req = _req('FORM_III', root=('ق', 'ت', 'ل'), pattern='FA3ALA')
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_ACCEPTED'
    assert result.multiplicity == 'MULTIPLE_LICENSED'
    assert len(result.licensed_masdars) == 2
    patterns = {lm.candidate.canonical_pattern for lm in result.licensed_masdars}
    assert 'MUFA3ALA' in patterns
    assert 'FI3AL' in patterns


# ── FA3IL_PARTICIPLE → MASDAR_BLOCKED ─────────────────────────────────────────

def test_fa3il_participle_blocked():
    req = _req('FA3IL_PARTICIPLE', pattern='FA3IL', root=('ك', 'ت', 'ب'))
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_BLOCKED'
    assert result.blocked is not None


# ── missing licensed_root → MASDAR_BLOCKED ────────────────────────────────────

def test_missing_licensed_root_blocked():
    req = MasdarRequest(
        request_id='TEST-NO-ROOT',
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
    assert result.verdict == 'MASDAR_BLOCKED'


# ── missing licensed_pattern → MASDAR_BLOCKED ────────────────────────────────

def test_missing_licensed_pattern_blocked():
    req = MasdarRequest(
        request_id='TEST-NO-PAT',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host='test',
        verbal_lemma=None,
        licensed_root=('ك', 'ت', 'ب'),
        licensed_root_class='SOUND',
        licensed_pattern=None,
        verb_form_family='FORM_II',
        voice=None,
        available_context=(),
        requested_masdar_type=None,
        supplied_masdar_surface=None,
        evidence=(),
        upstream_trace=(),
    )
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_BLOCKED'


# ── missing verbal_host AND verbal_lemma → MASDAR_DEFERRED VERBHOOD ───────────

def test_missing_verbhood_deferred():
    req = MasdarRequest(
        request_id='TEST-NO-VERB',
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
    assert result.verdict == 'MASDAR_DEFERRED'
    assert result.deferred is not None
    assert 'VERBHOOD' in result.deferred.reason


# ── verbal_lemma provided (no verbal_host) → gate passes ──────────────────────

def test_verbal_lemma_no_host_passes():
    req = MasdarRequest(
        request_id='TEST-LEMMA',
        mode='GENERATE_FROM_VERB',
        original_surface='',
        normalized_surface='',
        verbal_host=None,
        verbal_lemma='عَلَّمَ',
        licensed_root=('ع', 'ل', 'م'),
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
    assert result.verdict == 'MASDAR_ACCEPTED'


# ── weak root → MASDAR_DEFERRED (surface realization gap) ─────────────────────

def test_weak_root_form_ii_deferred():
    req = _req('FORM_II', root=('ق', 'و', 'ل'), pattern='FA33ALA', root_class='HOLLOW')
    result = analyze_masdar(req)
    assert result.verdict == 'MASDAR_DEFERRED'


# ── source_engine always HOKOM_MASDAR_ENGINE ──────────────────────────────────

@pytest.mark.parametrize('ff,pattern', [
    ('FORM_II', 'FA33ALA'),
    ('FORM_X',  'ISTAF3ALA'),
])
def test_source_engine_always_hokom(ff, pattern):
    req = _req(ff, pattern=pattern)
    result = analyze_masdar(req)
    assert result.source_engine == MASDAR_ENGINE_ID
