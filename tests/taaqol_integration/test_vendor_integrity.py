"""
HT30 -- Vendor integrity: verify that vendor/Taaqol-GPT has not been locally patched.
local_patch_count must be 0.

Provenance record location: docs/upstream-provenance/Taaqol-GPT.json
(outside the submodule, so the submodule stays clean)
"""
import json
import pathlib
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PROVENANCE_PATH = _REPO_ROOT / 'docs' / 'upstream-provenance' / 'Taaqol-GPT.json'

PINNED_SHA = 'ee56e369fb1e7eb402998c1f73e83642134a0f34'
EXPECTED_REPO_URL = 'https://github.com/sonaiso/Taaqol-GPT.git'


def _load() -> dict:
    assert PROVENANCE_PATH.is_file(), \
        f"Provenance record missing: {PROVENANCE_PATH}"
    with PROVENANCE_PATH.open() as f:
        return json.load(f)


def test_provenance_file_exists():
    assert PROVENANCE_PATH.is_file(), \
        f"docs/upstream-provenance/Taaqol-GPT.json must exist at {PROVENANCE_PATH}"


def test_local_patch_count_zero():
    p = _load()
    assert p.get('local_patch_count', -1) == 0, \
        f"Expected 0 local patches, got {p.get('local_patch_count')}"


def test_commit_sha_recorded():
    p = _load()
    sha = p.get('commit_sha', '')
    assert len(sha) == 40, f"commit_sha must be 40-char hex, got {sha!r}"
    assert sha == PINNED_SHA, \
        f"commit_sha must equal pinned SHA {PINNED_SHA!r}, got {sha!r}"


def test_license_recorded():
    p = _load()
    assert p.get('license'), "license must be recorded"


def test_python_requirement_and_native_runtime_recorded():
    """Native runtime requirement (>=3.11) and verified runtime must be recorded.

    Replaces the obsolete test_python_compatibility_gap_documented.
    The compatibility gap (Python 3.10 vs 3.11+) is a resolved historical fact:
    the Hokom runtime has been upgraded to Python 3.12.4.
    """
    p = _load()
    req = p.get('python_requirement', '')
    assert '3.11' in req, \
        f"python_requirement must reference 3.11+, got {req!r}"
    assert p.get('verified_runtime'), "verified_runtime must be recorded"
    assert p.get('native_taaqol_import') is True, \
        "native_taaqol_import must be true"


def test_repository_url_recorded():
    p = _load()
    assert p.get('repository_url') == EXPECTED_REPO_URL, \
        f"repository_url must equal {EXPECTED_REPO_URL!r}, got {p.get('repository_url')!r}"


def test_package_version_recorded():
    p = _load()
    assert p.get('package_version'), "package_version must be recorded"


def test_vendor_src_exists():
    vendor_src = _REPO_ROOT / 'vendor' / 'Taaqol-GPT' / 'src' / 'taaqqul_slot_geometry'
    assert vendor_src.is_dir(), \
        "vendor/Taaqol-GPT/src/taaqqul_slot_geometry must exist"


def test_vendor_core_files_present():
    core_dir = (
        _REPO_ROOT / 'vendor' / 'Taaqol-GPT' / 'src'
        / 'taaqqul_slot_geometry' / 'core'
    )
    assert core_dir.is_dir(), f"core dir missing: {core_dir}"
    required_files = [
        'slot_graph.py', 'gamma.py', 'rank_lattice.py',
        'residual_policy.py', 'evidence_contract.py',
        'transition_gate.py', 'trace_ledger.py',
    ]
    for fname in required_files:
        assert (core_dir / fname).is_file(), f"Missing core file: {fname}"
