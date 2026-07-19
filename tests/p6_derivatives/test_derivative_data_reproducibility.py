#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_data_reproducibility.py — Data reproducibility"""
import hashlib
import json
from pathlib import Path
import pytest
from pipeline.p6_derivatives.rule_registry import get_rule_registry, DerivativeRuleRegistry

_REPO_ROOT = Path(__file__).parent.parent.parent
_DATA_DIR  = _REPO_ROOT / 'data' / 'derivatives'


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── Registry loads twice → same results ──────────────────────────────────────

def test_registry_loads_twice_same_rules():
    """Two separate instantiations produce the same rule list."""
    r1 = DerivativeRuleRegistry()
    r2 = DerivativeRuleRegistry()
    ids1 = [x['rule_id'] for x in r1.all_rules()]
    ids2 = [x['rule_id'] for x in r2.all_rules()]
    assert ids1 == ids2

def test_registry_loads_twice_same_lexicon():
    r1 = DerivativeRuleRegistry()
    r2 = DerivativeRuleRegistry()
    ids1 = [x['deriv_id'] for x in r1.all_lexicon()]
    ids2 = [x['deriv_id'] for x in r2.all_lexicon()]
    assert ids1 == ids2

def test_registry_singleton_stable():
    """Singleton always returns same object."""
    r1 = get_rule_registry()
    r2 = get_rule_registry()
    assert r1 is r2

def test_registry_rule_order_deterministic():
    r = get_rule_registry()
    order1 = [x['rule_id'] for x in r.all_rules()]
    order2 = [x['rule_id'] for x in r.all_rules()]
    assert order1 == order2

def test_registry_lexicon_order_deterministic():
    r = get_rule_registry()
    order1 = [x['deriv_id'] for x in r.all_lexicon()]
    order2 = [x['deriv_id'] for x in r.all_lexicon()]
    assert order1 == order2


# ── SHA256 of data files ──────────────────────────────────────────────────────

def test_rule_registry_file_stable():
    """File must exist, be non-empty, and have a consistent SHA256."""
    path = _DATA_DIR / 'derivative_rule_registry.jsonl'
    assert path.exists()
    assert path.stat().st_size > 0
    h = _sha256(path)
    # Verify same on second read
    assert _sha256(path) == h

def test_lexical_inventory_file_stable():
    path = _DATA_DIR / 'derivative_lexical_inventory.jsonl'
    assert path.exists()
    assert path.stat().st_size > 0
    h = _sha256(path)
    assert _sha256(path) == h

def test_pattern_definitions_file_stable():
    path = _DATA_DIR / 'derivative_pattern_definitions.jsonl'
    assert path.exists()
    assert path.stat().st_size > 0
    h = _sha256(path)
    assert _sha256(path) == h


# ── Data file content validity ────────────────────────────────────────────────

def test_rule_registry_is_valid_jsonl():
    path = _DATA_DIR / 'derivative_rule_registry.jsonl'
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line:
            obj = json.loads(line)
            assert 'rule_id' in obj
            assert 'derivative_type' in obj

def test_lexical_inventory_is_valid_jsonl():
    path = _DATA_DIR / 'derivative_lexical_inventory.jsonl'
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line:
            obj = json.loads(line)
            assert 'deriv_id' in obj
            assert 'derivative_type' in obj
            assert 'root' in obj

def test_pattern_definitions_is_valid_jsonl():
    path = _DATA_DIR / 'derivative_pattern_definitions.jsonl'
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line:
            obj = json.loads(line)
            assert 'pattern_id' in obj
            assert 'arabic_template' in obj


# ── Required rules present ────────────────────────────────────────────────────

_REQUIRED_RULE_IDS = [
    'RULE_ISM_FA3IL_FORM_I',
    'RULE_ISM_FA3IL_FORM_II',
    'RULE_ISM_FA3IL_FORM_III',
    'RULE_ISM_FA3IL_FORM_IV',
    'RULE_ISM_FA3IL_FORM_V',
    'RULE_ISM_FA3IL_FORM_VI',
    'RULE_ISM_FA3IL_FORM_VII',
    'RULE_ISM_FA3IL_FORM_VIII',
    'RULE_ISM_FA3IL_FORM_X',
    'RULE_ISM_MAF3UL_FORM_I',
    'RULE_ISM_MAF3UL_FORM_II',
    'RULE_ISM_MAF3UL_FORM_III',
    'RULE_ISM_MAF3UL_FORM_IV',
    'RULE_ISM_MAF3UL_FORM_V',
    'RULE_ISM_MAF3UL_FORM_VI',
    'RULE_ISM_MAF3UL_FORM_VII',
    'RULE_ISM_MAF3UL_FORM_VIII',
    'RULE_ISM_MAF3UL_FORM_X',
    'RULE_SIFA_FA3IL',
    'RULE_SIFA_FA3LAN',
    'RULE_SIFA_AF3AL',
    'RULE_MUBALGHA_FA33AL',
    'RULE_MUBALGHA_MIFA3L',
    'RULE_MUBALGHA_FA3UL',
    'RULE_ISM_ZM_MAF3AL',
    'RULE_ISM_ZM_MAF3IL',
    'RULE_ISM_ALA_MIFA3L',
    'RULE_ISM_ALA_MIFA3LA',
    'RULE_ISM_ALA_MIFA3AL',
]

@pytest.mark.parametrize('rule_id', _REQUIRED_RULE_IDS)
def test_required_rule_present(rule_id):
    r = get_rule_registry()
    all_rule_ids = {x['rule_id'] for x in r.all_rules()}
    assert rule_id in all_rule_ids, f'Required rule missing: {rule_id}'


# ── Required lexical entries ──────────────────────────────────────────────────

_REQUIRED_DERIV_IDS = [
    'DRV_001', 'DRV_002', 'DRV_003', 'DRV_004', 'DRV_005',
    'DRV_006', 'DRV_007', 'DRV_008', 'DRV_009', 'DRV_010',
]

@pytest.mark.parametrize('deriv_id', _REQUIRED_DERIV_IDS)
def test_required_lexical_entry_present(deriv_id):
    r = get_rule_registry()
    all_ids = {x['deriv_id'] for x in r.all_lexicon()}
    assert deriv_id in all_ids, f'Required lexical entry missing: {deriv_id}'
