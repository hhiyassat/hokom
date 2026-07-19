#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_rule_registry.py — Registry loader tests"""
import pytest
from pipeline.p6_derivatives.rule_registry import get_rule_registry, DerivativeRuleRegistry


def test_registry_loads():
    r = get_rule_registry()
    assert isinstance(r, DerivativeRuleRegistry)

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


# ── ISM_FA3IL rules ───────────────────────────────────────────────────────────

def test_ism_fa3il_form_i_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_I')
    assert len(rules) >= 1
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'FA3IL' in patterns

def test_ism_fa3il_form_ii_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_II')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUFA33IL' in patterns

def test_ism_fa3il_form_iii_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_III')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUFA3IL' in patterns

def test_ism_fa3il_form_iv_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_IV')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUF3IL' in patterns

def test_ism_fa3il_form_v_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_V')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUTAFA33IL' in patterns

def test_ism_fa3il_form_vi_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_VI')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUTAFA3IL' in patterns

def test_ism_fa3il_form_vii_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_VII')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUNFA3IL' in patterns

def test_ism_fa3il_form_viii_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_VIII')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUFTA3IL' in patterns

def test_ism_fa3il_form_x_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_X')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUSTAF3IL' in patterns


# ── ISM_MAF3UL rules ──────────────────────────────────────────────────────────

def test_ism_maf3ul_form_i_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_MAF3UL', 'FORM_I')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MAF3UL' in patterns

def test_ism_maf3ul_form_ii_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_MAF3UL', 'FORM_II')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUFA33AL' in patterns

def test_ism_maf3ul_form_x_rule_present():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_MAF3UL', 'FORM_X')
    patterns = [p for rule in rules for p in rule.get('masdar_patterns', [])]
    assert 'MUSTAF3AL' in patterns


# ── Deterministic ordering ────────────────────────────────────────────────────

def test_deterministic_ordering():
    r = get_rule_registry()
    rules1 = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_I')
    rules2 = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'FORM_I')
    assert [r['rule_id'] for r in rules1] == [r['rule_id'] for r in rules2]

def test_all_rules_sorted_deterministically():
    r = get_rule_registry()
    rules = r.all_rules()
    rule_ids_1 = [x['rule_id'] for x in rules]
    rule_ids_2 = [x['rule_id'] for x in r.all_rules()]
    assert rule_ids_1 == rule_ids_2


# ── Lexical entries ───────────────────────────────────────────────────────────

def test_lexical_entries_for_kataba():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root(('ك', 'ت', 'ب'))
    assert len(entries) >= 1

def test_lexical_entries_for_kataba_ism_fa3il():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root_ff_and_dtype(('ك', 'ت', 'ب'), 'FORM_I', 'ISM_FA3IL')
    assert len(entries) >= 1
    # Strip diacritics for comparison (entry may have full diacritics like كَاتِب)
    import unicodedata
    def strip_diacritics(s):
        if not s:
            return ''
        return ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    surfaces = [strip_diacritics(e.get('derivative_surface') or '') for e in entries]
    assert any('كاتب' in s for s in surfaces)

def test_lexical_entries_for_kataba_mubalgha():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root_ff_and_dtype(('ك', 'ت', 'ب'), 'FORM_I', 'MUBALGHA')
    assert len(entries) >= 1

def test_lexical_entries_for_unknown_root():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root(('خ', 'ض', 'ع'))
    assert entries == []

def test_lexical_entries_for_wrong_ff():
    r = get_rule_registry()
    entries = r.lexical_entries_for_root_and_ff(('ك', 'ت', 'ب'), 'FORM_IX')
    assert entries == []

def test_unknown_derivative_type_returns_empty():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('NONEXISTENT', 'FORM_I')
    assert rules == []

def test_unknown_form_family_returns_empty():
    r = get_rule_registry()
    rules = r.rules_for_derivative_type_and_form_family('ISM_FA3IL', 'NONEXISTENT_FF')
    assert rules == []
