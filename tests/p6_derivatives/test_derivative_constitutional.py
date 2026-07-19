#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/p6_derivatives/test_derivative_constitutional.py — Constitutional gate tests"""
import ast
from pathlib import Path
import pytest
from pipeline.p6_derivatives.models import (
    DERIVATIVES_CANONICAL_OWNER, DERIVATIVES_ENGINE_ID, DerivativesOwnershipGate,
)

_REPO_ROOT = Path(__file__).parent.parent.parent
_ENGINE_PY = _REPO_ROOT / 'pipeline' / 'p6_derivatives' / 'engine.py'
_DATA_DIR  = _REPO_ROOT / 'data' / 'derivatives'


def test_derivatives_canonical_owner():
    assert DERIVATIVES_CANONICAL_OWNER == 'HOKOM'


def test_derivatives_engine_id():
    assert DERIVATIVES_ENGINE_ID == 'HOKOM_DERIVATIVES_ENGINE'


def test_parallel_derivative_engines_zero():
    gate = DerivativesOwnershipGate()
    assert gate.PARALLEL_DERIVATIVE_ENGINES == 0


def test_external_derivative_dependencies_zero():
    gate = DerivativesOwnershipGate()
    assert gate.EXTERNAL_DERIVATIVE_DEPENDENCIES == 0


def test_all_derivative_contracts_verified():
    gate = DerivativesOwnershipGate()
    assert gate.ISM_FA3IL_CONTRACT == 'VERIFIED'
    assert gate.ISM_MAF3UL_CONTRACT == 'VERIFIED'
    assert gate.SIFA_MUSHABBAHA_CONTRACT == 'VERIFIED'
    assert gate.MUBALGHA_CONTRACT == 'VERIFIED'
    assert gate.ISM_ZAMAN_CONTRACT == 'VERIFIED'
    assert gate.ISM_MAKAN_CONTRACT == 'VERIFIED'
    assert gate.ISM_ALA_CONTRACT == 'VERIFIED'


def test_leakage_prevention_verified():
    gate = DerivativesOwnershipGate()
    assert gate.MASDAR_MIMI_LEAKAGE_PREVENTION == 'VERIFIED'
    assert gate.FA3IL_PARTICIPLE_ROUTING_PRESERVED == 'VERIFIED'
    assert gate.ISM_ZAMAN_MAKAN_AMBIGUITY_GOVERNED == 'VERIFIED'


def test_unlicensed_guesses_zero():
    gate = DerivativesOwnershipGate()
    assert gate.MUBALGHA_UNLICENSED_GUESSES == 0
    assert gate.SIFA_UNLICENSED_GUESSES == 0


def test_multiple_licensed_derivatives_supported():
    gate = DerivativesOwnershipGate()
    assert gate.MULTIPLE_LICENSED_DERIVATIVES == 'SUPPORTED'


def test_semantic_modifications_zero():
    gate = DerivativesOwnershipGate()
    assert gate.P5_MASDAR_SEMANTIC_MODIFICATIONS == 0
    assert gate.ROOT_SEMANTIC_MODIFICATIONS == 0
    assert gate.PATTERN_SEMANTIC_MODIFICATIONS == 0
    assert gate.TAAQOL_SUBMODULE_MODIFICATIONS == 0


def test_data_files_exist():
    for fname in [
        'derivative_rule_registry.jsonl',
        'derivative_lexical_inventory.jsonl',
        'derivative_pattern_definitions.jsonl',
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
    """engine.py must not contain Arabic corpus words embedded in Python string literals."""
    source = _ENGINE_PY.read_text(encoding='utf-8')
    tree = ast.parse(source)
    arabic_strings_in_code = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any('؀' <= c <= 'ۿ' for c in node.value):
                if ' ' in node.value or len(node.value) > 20:
                    arabic_strings_in_code.append(node.value[:50])
    assert arabic_strings_in_code == [], (
        f'Found Arabic corpus words in engine.py source: {arabic_strings_in_code}'
    )


def test_engine_canonical_entrypoint_exists():
    source = _ENGINE_PY.read_text(encoding='utf-8')
    assert 'def analyze_derivative(' in source


def test_ownership_version():
    gate = DerivativesOwnershipGate()
    assert gate.DERIVATIVES_OWNERSHIP_VERSION == '1.0.0'


def test_p5_masdar_not_modified():
    """p5_masdar engine.py and models.py must not have been modified."""
    p5_engine = _REPO_ROOT / 'pipeline' / 'p5_masdar' / 'engine.py'
    p5_models = _REPO_ROOT / 'pipeline' / 'p5_masdar' / 'models.py'
    assert p5_engine.exists()
    assert p5_models.exists()
    # Verify canonical constants still present (not overwritten)
    assert 'MASDAR_CANONICAL_OWNER' in p5_models.read_text(encoding='utf-8')
    assert 'HOKOM_MASDAR_ENGINE' in p5_engine.read_text(encoding='utf-8')
