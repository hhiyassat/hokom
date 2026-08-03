"""
test_b3_verifier.py — Structural integrity test for verify_taaqol_native.py.

Tests:
  1. No Traceback in stdout or stderr.
  2. No AttributeError in stdout or stderr.
  3. No TypeError in stdout or stderr.
  4. Summary is consistent with detail lines (B3_CLOSED matches all-7 pass).
  5. Any internal failure causes B3_CLOSED=0 and non-zero exit code.
  6. _INTERNAL_EXCEPTIONS is gated — B3_CLOSED=1 requires INTERNAL_EXCEPTIONS=0.

These tests run the verifier as a subprocess so the test harness is independent
of vendor import state. Must run under Python 3.12.4 (canonical runtime).
"""
from __future__ import annotations
import subprocess
import sys
import os
import re

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_VERIFIER = os.path.join(_REPO_ROOT, 'scripts', 'verify_taaqol_native.py')


def _run_verifier() -> subprocess.CompletedProcess:
    """Run verify_taaqol_native.py and return the CompletedProcess."""
    env = os.environ.copy()
    env['PYTHONPATH'] = (
        os.path.join(_REPO_ROOT, 'src') + os.pathsep +
        _REPO_ROOT + os.pathsep +
        os.path.join(_REPO_ROOT, 'vendor', 'Taaqol-GPT', 'src') +
        (os.pathsep + env.get('PYTHONPATH', '') if env.get('PYTHONPATH') else '')
    )
    return subprocess.run(
        [sys.executable, _VERIFIER],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
        env=env,
    )


def test_b3_verifier_no_traceback():
    """No Traceback should appear in verifier stdout or stderr."""
    result = _run_verifier()
    combined = result.stdout + result.stderr
    assert 'Traceback (most recent call last)' not in combined, (
        f"B3_VERIFIER_TRACEBACK: Traceback appeared in output.\n"
        f"STDOUT tail:\n{result.stdout[-600:]}\n"
        f"STDERR tail:\n{result.stderr[-300:]}"
    )


def test_b3_verifier_no_attribute_error():
    """No AttributeError should appear in verifier output."""
    result = _run_verifier()
    combined = result.stdout + result.stderr
    # Exclude AttributeError appearing as a class name in import list
    assert 'AttributeError:' not in combined, (
        f"B3_VERIFIER_ATTRIBUTE_ERROR: AttributeError in output.\n"
        f"STDOUT tail:\n{result.stdout[-600:]}"
    )


def test_b3_verifier_no_type_error():
    """No TypeError should appear in verifier output."""
    result = _run_verifier()
    combined = result.stdout + result.stderr
    assert 'TypeError:' not in combined, (
        f"B3_VERIFIER_TYPE_ERROR: TypeError in output.\n"
        f"STDOUT tail:\n{result.stdout[-600:]}"
    )


def test_b3_verifier_summary_consistent_with_details():
    """
    B3_CLOSED=1 in summary iff:
      - All 7 ✅ in PART B detail lines, AND
      - INTERNAL_EXCEPTIONS = 0.
    B3_CLOSED=0 in summary iff any ❌ in PART B OR INTERNAL_EXCEPTIONS > 0.
    """
    result = _run_verifier()
    stdout = result.stdout

    # Count ✅ and ❌ in Part B detail lines
    part_b_section = re.search(
        r'PART B — DIRECT CORE MODULES.*?(?=TAAQOL_NATIVE_STAGE_COUNT|$)',
        stdout, re.DOTALL,
    )
    if part_b_section:
        part_b_text = part_b_section.group(0)
        pass_count = part_b_text.count('✅')
        fail_count = part_b_text.count('❌')
    else:
        pass_count = fail_count = -1

    # Parse INTERNAL_EXCEPTIONS from summary
    exc_match = re.search(r'INTERNAL_EXCEPTIONS\s*=\s*(\d+)', stdout)
    internal_exceptions = int(exc_match.group(1)) if exc_match else -1

    b3_closed_1 = 'B3_CLOSED = 1' in stdout
    b3_closed_0 = 'B3_CLOSED = 0' in stdout

    if pass_count == 7 and internal_exceptions == 0:
        assert b3_closed_1, (
            f"B3_VERIFIER_SUMMARY_MISMATCH: All 7 ops passed and INTERNAL_EXCEPTIONS=0 "
            f"but B3_CLOSED != 1.\nSTDOUT tail:\n{stdout[-800:]}"
        )
        assert not b3_closed_0, (
            f"B3_VERIFIER_SUMMARY_MISMATCH: B3_CLOSED=0 printed alongside B3_CLOSED=1.\n"
            f"STDOUT tail:\n{stdout[-800:]}"
        )
    else:
        assert b3_closed_0 or (not b3_closed_1), (
            f"B3_VERIFIER_SUMMARY_MISMATCH: ops_passed={pass_count}, "
            f"internal_exceptions={internal_exceptions} but B3_CLOSED=1 was printed.\n"
            f"STDOUT tail:\n{stdout[-800:]}"
        )


def test_b3_verifier_exit_code_matches_b3_closed():
    """
    exit code 0  ↔  B3_CLOSED=1 (all ops passed, zero exceptions).
    exit code !=0 ↔  B3_CLOSED=0 or any internal exception.
    """
    result = _run_verifier()
    b3_closed_1 = 'B3_CLOSED = 1' in result.stdout

    if b3_closed_1:
        assert result.returncode == 0, (
            f"B3_EXIT_CODE_MISMATCH: B3_CLOSED=1 but exit code={result.returncode}.\n"
            f"STDOUT tail:\n{result.stdout[-400:]}"
        )
    else:
        assert result.returncode != 0, (
            f"B3_EXIT_CODE_MISMATCH: B3_CLOSED=0 but exit code=0 (should be non-zero).\n"
            f"STDOUT tail:\n{result.stdout[-400:]}"
        )


def test_b3_verifier_internal_exception_contract():
    """
    Unit test: _INTERNAL_EXCEPTIONS gating contract.
    If _INTERNAL_EXCEPTIONS is non-empty, B3_CLOSED must be 0 regardless of op metrics.
    Verified by importing the module and inspecting _print_summary logic.
    """
    # Ensure module is importable (fails gracefully on Python < 3.11 due to StrEnum)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            '_b3_verify_module', _VERIFIER
        )
        mod = importlib.util.module_from_spec(spec)
        # We can't fully exec it (it modifies sys.path etc.) so just check source.
    except Exception:
        pass  # OK on incompatible Python — subprocess tests cover the contract

    with open(_VERIFIER) as f:
        src = f.read()

    # The gate condition must reference _INTERNAL_EXCEPTIONS
    assert 'not _INTERNAL_EXCEPTIONS' in src, (
        "B3_FAIL_CLOSED_GATE_MISSING: _print_summary must gate B3_CLOSED=1 "
        "on 'not _INTERNAL_EXCEPTIONS'"
    )
    # The exit code must reference _INTERNAL_EXCEPTIONS
    assert '_INTERNAL_EXCEPTIONS' in src.split('def main')[1], (
        "B3_EXIT_CODE_GATE_MISSING: main() must factor _INTERNAL_EXCEPTIONS "
        "into the return code"
    )
    # .transition_state must NOT appear (wrong attribute)
    assert 'verdict.transition_state' not in src, (
        "B3_WRONG_FIELD: verdict.transition_state used — correct field is verdict.state"
    )
    # .entries() must NOT appear as a call (it's a property)
    assert 'ledger.entries()' not in src, (
        "B3_WRONG_CALL: ledger.entries() used — entries is a @property, use ledger.entries[i]"
    )
