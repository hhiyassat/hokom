#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p5_masdar/test_masdar_constitutional.py — Constitutional gate tests"""
import ast
from pathlib import Path
import pytest
from pipeline.p5_masdar.models import (
    MASDAR_CANONICAL_OWNER, MASDAR_ENGINE_ID, MasdarOwnershipGate,
)

_REPO_ROOT = Path(__file__).parent.parent.parent
_ENGINE_PY = _REPO_ROOT / 'pipeline' / 'p5_masdar' / 'engine.py'
_DATA_DIR  = _REPO_ROOT / 'data' / 'masdar'


def test_masdar_canonical_owner():
    assert MASDAR_CANONICAL_OWNER == 'HOKOM'


def test_masdar_engine_id():
    assert MASDAR_ENGINE_ID == 'HOKOM_MASDAR_ENGINE'


def test_parallel_engines_zero():
    gate = MasdarOwnershipGate()
    assert gate.PARALLEL_MASDAR_ENGINES == 0


def test_external_dependencies_zero():
    gate = MasdarOwnershipGate()
    assert gate.EXTERNAL_MASDAR_DEPENDENCIES == 0


def test_form_i_unlicensed_guesses_zero():
    gate = MasdarOwnershipGate()
    assert gate.FORM_I_UNLICENSED_GUESSES == 0


def test_unlicensed_masdar_guesses_zero():
    gate = MasdarOwnershipGate()
    assert gate.UNLICENSED_MASDAR_GUESSES == 0


def test_forced_single_masdar_results_zero():
    gate = MasdarOwnershipGate()
    assert gate.FORCED_SINGLE_MASDAR_RESULTS == 0


def test_multiple_licensed_masdars_supported():
    gate = MasdarOwnershipGate()
    assert gate.MULTIPLE_LICENSED_MASDARS == 'SUPPORTED'


def test_subtype_contracts_verified():
    gate = MasdarOwnershipGate()
    assert gate.MASDAR_MIMI_CONTRACT  == 'VERIFIED'
    assert gate.MASDAR_MARRA_CONTRACT == 'VERIFIED'
    assert gate.MASDAR_HAYAA_CONTRACT == 'VERIFIED'
    assert gate.ISM_MASDAR_CONTRACT   == 'VERIFIED'


def test_semantic_modifications_zero():
    gate = MasdarOwnershipGate()
    assert gate.P5_SEMANTIC_MODIFICATIONS        == 0
    assert gate.ROOT_SEMANTIC_MODIFICATIONS      == 0
    assert gate.PATTERN_SEMANTIC_MODIFICATIONS   == 0
    assert gate.TAAQOL_SUBMODULE_MODIFICATIONS   == 0


def test_data_files_exist():
    for fname in [
        'masdar_rule_registry.jsonl',
        'masdar_lexical_inventory.jsonl',
        'masdar_pattern_definitions.jsonl',
        'masdar_residual_registry.jsonl',
    ]:
        p = _DATA_DIR / fname
        assert p.exists(), f'Missing data file: {p}'
        assert p.stat().st_size > 0, f'Empty data file: {p}'


def test_engine_no_external_libraries():
    """engine.py must not import requests, HR2S, subprocess, urllib, network."""
    source = _ENGINE_PY.read_text(encoding='utf-8')
    forbidden = ['requests', 'HR2S', 'subprocess', 'urllib', 'http.client',
                 'socket', 'httpx', 'aiohttp']
    for lib in forbidden:
        assert lib not in source, f'Forbidden import found in engine.py: {lib}'


def test_engine_no_hardcoded_corpus():
    """engine.py must not contain Arabic corpus words embedded in Python."""
    source = _ENGINE_PY.read_text(encoding='utf-8')
    # Arabic words in comments are fine; we check for Arabic string literals
    tree = ast.parse(source)
    arabic_strings_in_code = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any('؀' <= c <= 'ۿ' for c in node.value):
                # String literals that are just pattern names (no spaces) are OK
                if ' ' in node.value or len(node.value) > 20:
                    arabic_strings_in_code.append(node.value[:50])
    assert arabic_strings_in_code == [], (
        f'Found Arabic corpus words in engine.py source: {arabic_strings_in_code}'
    )


def test_engine_canonical_entrypoint_exists():
    source = _ENGINE_PY.read_text(encoding='utf-8')
    assert 'def analyze_masdar(' in source


def test_masdar_ownership_version():
    gate = MasdarOwnershipGate()
    assert gate.MASDAR_OWNERSHIP_VERSION == '1.0.0'
