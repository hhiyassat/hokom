"""
Compatibility gate: pre-3.11 version-specific assertions for
Constitutional Amendment No. 1 (Step 6 native path / DEFERRED status).

These tests are only relevant on Python < 3.11, where the native
taaqqul_slot_geometry package is not available (it requires StrEnum
from stdlib enum, introduced in Python 3.11).

On Python 3.11+, the native path may be APPROVED; this assertion does
not apply. The canonical suite (tests/taaqol_integration/) holds the
version-agnostic contracts.

VERSION GATE: intentional — this is tests/compatibility/, not canonical core.
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.mark.skipif(
    sys.version_info >= (3, 11),
    reason="Python 3.11+ -- native path may be APPROVED, not testing deferral",
)
def test_step6_defers_on_python_310():
    """On Python 3.10, admission gate must report DEFERRED for native path."""
    from pipeline.taaqol_integration.admission_gate import _NATIVE_AVAILABLE
    assert not _NATIVE_AVAILABLE, (
        "On Python 3.10, native taaqqul_slot_geometry must not be available without backport"
    )
