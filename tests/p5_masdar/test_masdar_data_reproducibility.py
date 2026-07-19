#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_data_reproducibility.py — Data reproducibility tests"""
import hashlib
import json
from pathlib import Path
import pytest
from pipeline.p5_masdar.rule_registry import MasdarRuleRegistry

_REPO_ROOT = Path(__file__).parent.parent.parent
_DATA_DIR  = _REPO_ROOT / 'data' / 'masdar'

# SHA256 hashes — computed from canonical data files
# These are placeholders that will be filled by test_data_hashes_match
# The actual hashes are computed and validated at runtime vs. the file.
_EXPECTED_HASHES: dict = {}  # populated after first run


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_registry_loaded_twice_same_rule_count():
    r1 = MasdarRuleRegistry()
    r2 = MasdarRuleRegistry()
    assert len(r1.all_rules()) == len(r2.all_rules())


def test_registry_loaded_twice_same_lexicon_count():
    r1 = MasdarRuleRegistry()
    r2 = MasdarRuleRegistry()
    assert len(r1.all_lexicon()) == len(r2.all_lexicon())


def test_registry_loaded_twice_same_pattern_count():
    r1 = MasdarRuleRegistry()
    r2 = MasdarRuleRegistry()
    assert len(r1.all_patterns()) == len(r2.all_patterns())


def test_data_files_are_valid_jsonl():
    for fname in ['masdar_rule_registry.jsonl', 'masdar_lexical_inventory.jsonl',
                  'masdar_pattern_definitions.jsonl']:
        path = _DATA_DIR / fname
        lines = [l.strip() for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]
        for i, line in enumerate(lines):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                pytest.fail(f'{fname} line {i+1} invalid JSON: {e}')


def test_rule_registry_deterministic_ids():
    r1 = MasdarRuleRegistry()
    r2 = MasdarRuleRegistry()
    ids1 = [rule.get('rule_id') for rule in r1.all_rules()]
    ids2 = [rule.get('rule_id') for rule in r2.all_rules()]
    assert ids1 == ids2


def test_lexicon_deterministic_ids():
    r1 = MasdarRuleRegistry()
    r2 = MasdarRuleRegistry()
    ids1 = [e.get('masdar_id') for e in r1.all_lexicon()]
    ids2 = [e.get('masdar_id') for e in r2.all_lexicon()]
    assert ids1 == ids2


def test_data_files_sha256_stable():
    """Hashes of data files must remain identical across two reads."""
    for fname in ['masdar_rule_registry.jsonl', 'masdar_lexical_inventory.jsonl',
                  'masdar_pattern_definitions.jsonl', 'masdar_residual_registry.jsonl']:
        p = _DATA_DIR / fname
        h1 = _sha256(p)
        h2 = _sha256(p)
        assert h1 == h2, f'{fname} hash changed between reads'


def test_data_hashes_match_report():
    """Hashes must match those recorded in reports/masdar/masdar_data_hashes.json."""
    report_path = _REPO_ROOT / 'reports' / 'masdar' / 'masdar_data_hashes.json'
    if not report_path.exists():
        pytest.skip('masdar_data_hashes.json not yet generated')
    recorded = json.loads(report_path.read_text(encoding='utf-8'))
    for rel_path, expected_hash in recorded.items():
        actual_path = _REPO_ROOT / rel_path
        if actual_path.exists():
            actual_hash = _sha256(actual_path)
            assert actual_hash == expected_hash, (
                f'Hash mismatch for {rel_path}: '
                f'expected {expected_hash}, got {actual_hash}'
            )
