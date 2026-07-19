#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_rule_registry.py — Registry loader tests"""
import pytest
from pipeline.p5_masdar.rule_registry import get_rule_registry, MasdarRuleRegistry


def test_registry_loads():
    r = get_rule_registry()
    assert isinstance(r, MasdarRuleRegistry)

def test_registry_singleton():
    r1 = get_rule_registry()
    r2 = get_rule_registry()
    assert r1 is r2

def test_all_rules_nonzero():
    r = get_rule_registry()
    assert len(r.all_rules()) > 0

def test_all_lexicon_nonzero():
    r = get_rule_registry()
    assert len(r.all_lexicon()) > 0

def test_all_patterns_nonzero():
    r = get_rule_registry()
    assert len(r.all_patterns()) > 0

def test_rules_for_form_ii():
    r = get_rule_registry()
    rules = r.rules_for_form_family('FORM_II')
    assert len(rules) >= 1
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'TAF3IL' in patterns

def test_rules_for_form_iii():
    r = get_rule_registry()
    rules = r.rules_for_form_family('FORM_III')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUFA3ALA' in patterns
    assert 'FI3AL' in patterns

def test_rules_for_form_iv():
    r = get_rule_registry()
    rules = r.rules_for_form_family('FORM_IV')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'IF3AL' in patterns

def test_rules_for_form_x():
    r = get_rule_registry()
    rules = r.rules_for_form_family('FORM_X')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'ISTIF3AL' in patterns

def test_rules_for_quadriliteral():
    r = get_rule_registry()
    rules = r.rules_for_form_family('QUADRILITERAL_FORM_I')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'FA3LALA' in patterns

def test_rules_for_unknown_family():
    r = get_rule_registry()
    rules = r.rules_for_form_family('NONEXISTENT_FAMILY')
    assert rules == []

def test_lexical_entries_for_root_kataba():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root(('ك', 'ت', 'ب'))
    assert len(entries) >= 1
    surfaces = [e.get('masdar_surface') for e in entries]
    assert 'كتابة' in surfaces

def test_lexical_entries_for_root_and_ff():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root_and_ff(('ك', 'ت', 'ب'), 'FORM_I')
    assert len(entries) >= 1

def test_lexical_entries_for_root_and_ff_wrong_ff():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root_and_ff(('ك', 'ت', 'ب'), 'FORM_II')
    assert entries == []

def test_lexical_entries_for_unknown_root():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root(('x', 'y', 'z'))
    assert entries == []

def test_pattern_for_taf3il():
    r = get_rule_registry()
    p = r.pattern_for_id('TAF3IL')
    assert p is not None
    assert p['arabic_template'] == 'تَفْعِيل'

def test_pattern_for_nonexistent():
    r = get_rule_registry()
    p = r.pattern_for_id('NONEXISTENT_PATTERN')
    assert p is None

def test_deterministic_rule_ordering():
    """Same call twice returns same ordering."""
    r = get_rule_registry()
    rules1 = r.rules_for_form_family('FORM_III')
    rules2 = r.rules_for_form_family('FORM_III')
    assert [x['rule_id'] for x in rules1] == [x['rule_id'] for x in rules2]

def test_deterministic_lexicon_ordering():
    """Same root query returns same order twice."""
    r = get_rule_registry()
    e1 = r.lexical_entries_for_root(('ق', 'ت', 'ل'))
    e2 = r.lexical_entries_for_root(('ق', 'ت', 'ل'))
    assert [x['masdar_id'] for x in e1] == [x['masdar_id'] for x in e2]

def test_fa3il_participle_blocked():
    r = get_rule_registry()
    rules = r.rules_for_form_family('FA3IL_PARTICIPLE')
    assert len(rules) >= 1
    statuses = [rule.get('status') for rule in rules]
    assert 'BLOCKED' in statuses

def test_rule_count():
    """Expect at least 13 rules loaded."""
    r = get_rule_registry()
    assert len(r.all_rules()) >= 13

def test_lexicon_count():
    """Expect exactly 15 lexical entries."""
    r = get_rule_registry()
    assert len(r.all_lexicon()) == 15

def test_pattern_count():
    """Expect at least 12 patterns."""
    r = get_rule_registry()
    assert len(r.all_patterns()) >= 12
