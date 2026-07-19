"""Contract: StrEnum must come from the stdlib enum module (Python 3.11+)."""
import sys
import importlib
import pytest

def test_native_strenum_importable():
    from enum import StrEnum
    assert StrEnum is not None

def test_native_strenum_module():
    from enum import StrEnum
    assert StrEnum.__module__ == 'enum', (
        f"Expected StrEnum from 'enum', got '{StrEnum.__module__}' — "
        "shim or backport detected"
    )

def test_no_strenum_shim_in_sys_modules():
    """No compatibility shim should be injected into sys.modules."""
    import sys
    for key in sys.modules:
        # Skip test modules — their names may contain 'strenum' or 'compat'
        if key.startswith('tests.') or key.startswith('runtime.') or 'test_' in key:
            continue
        if 'compat' in key.lower() and 'enum' in key.lower():
            pytest.fail(f"Suspicious compat module found in sys.modules: {key}")
        if 'strenum' in key.lower() and key != 'enum':
            pytest.fail(f"StrEnum shim detected in sys.modules: {key}")

def test_strenum_works_natively():
    from enum import StrEnum
    class Color(StrEnum):
        RED = 'red'
    assert Color.RED == 'red'
    assert isinstance(Color.RED, str)
