"""
Vendor integrity tests: verify vendor/Taaqol-GPT is unmodified.
No Taaqol import required — passes on Python 3.10+.
"""
from __future__ import annotations

import subprocess


def test_vendor_taaqol_gpt_unchanged():
    """vendor/Taaqol-GPT must have no uncommitted changes."""
    result = subprocess.run(
        ['git', '-C', 'vendor/Taaqol-GPT', 'status', '--porcelain'],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, \
        f"git -C vendor/Taaqol-GPT status failed: {result.stderr}"
    assert result.stdout.strip() == '', \
        f"Taaqol vendor modified:\n{result.stdout}"


def test_taaqol_submodule_commit_stable():
    """vendor/Taaqol-GPT submodule should not show uncommitted drift (+)."""
    result = subprocess.run(
        ['git', 'submodule', 'status'],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, \
        f"git submodule status failed: {result.stderr}"
    for line in result.stdout.splitlines():
        if 'Taaqol-GPT' in line:
            # '+' means submodule commit differs from what .gitmodules records
            assert not line.startswith('+'), \
                f"Taaqol-GPT submodule commit changed unexpectedly: {line}"


def test_vendor_taaqol_gpt_commit_is_known():
    """The Taaqol commit must be deterministically readable."""
    result = subprocess.run(
        ['git', '-C', 'vendor/Taaqol-GPT', 'rev-parse', 'HEAD'],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, "Cannot read Taaqol-GPT HEAD"
    commit = result.stdout.strip()
    assert len(commit) == 40, f"Expected 40-char SHA, got {commit!r}"
    assert all(c in '0123456789abcdef' for c in commit), \
        f"Invalid commit hash: {commit!r}"


def test_vendor_taaqol_gpt_pyproject_exists():
    """vendor/Taaqol-GPT/pyproject.toml must exist (package metadata present)."""
    import os
    from pathlib import Path
    pyproject = Path('vendor/Taaqol-GPT/pyproject.toml')
    assert pyproject.exists(), "vendor/Taaqol-GPT/pyproject.toml not found"


def test_vendor_taaqol_gpt_package_name():
    """The Taaqol package name must be 'taaqqul_slot_geometry'."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            # tomllib not available on Python 3.10 without install
            # Fall back to basic string search
            with open('vendor/Taaqol-GPT/pyproject.toml', encoding='utf-8') as f:
                content = f.read()
            assert 'taaqqul_slot_geometry' in content, \
                "Package name 'taaqqul_slot_geometry' not found in pyproject.toml"
            return

    from pathlib import Path
    with open('vendor/Taaqol-GPT/pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
    assert data['project']['name'] == 'taaqqul_slot_geometry'


def test_vendor_core_files_present():
    """Critical Taaqol source files must be present."""
    from pathlib import Path
    required = [
        'vendor/Taaqol-GPT/src/taaqqul_slot_geometry/__init__.py',
        'vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/slot_graph.py',
        'vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/gamma.py',
        'vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/transition_gate.py',
        'vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/rank_lattice.py',
        'vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/residual_policy.py',
        'vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/evidence_contract.py',
    ]
    for path in required:
        assert Path(path).exists(), f"Required Taaqol file missing: {path}"
