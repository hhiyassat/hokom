"""Contract: No monkey patches, shims, sitecustomize, or conftest compat."""
import sys
import inspect
import pathlib

def test_no_sitecustomize():
    """No project-created sitecustomize compat shim."""
    if 'sitecustomize' not in sys.modules:
        return  # Ideal: no sitecustomize at all
    sc = sys.modules['sitecustomize']
    sc_file = getattr(sc, '__file__', '') or ''
    # System-level sitecustomize (e.g. Ubuntu apport) is acceptable;
    # a project-created shim inside the repo would be a violation.
    repo_root = str(pathlib.Path(__file__).parent.parent.parent.resolve())
    assert repo_root not in str(pathlib.Path(sc_file).resolve()), (
        f"Project-created sitecustomize detected at {sc_file} — "
        "forbidden compatibility injection"
    )

def test_no_usercustomize():
    assert 'usercustomize' not in sys.modules, (
        "usercustomize is loaded — forbidden compatibility injection"
    )

def test_enum_module_not_replaced():
    import enum
    # enum module should be from the stdlib, not replaced
    assert enum.__spec__.origin is not None
    # Should be in the stdlib path, not in a project path
    origin = str(enum.__spec__.origin)
    assert 'hokom' not in origin.lower(), (
        f"enum module appears to be replaced: {origin}"
    )
    assert 'vendor' not in origin.lower(), (
        f"enum module appears to come from vendor: {origin}"
    )

def test_no_enum_strenum_monkey_patch():
    """StrEnum in enum module should be the real stdlib one."""
    import enum
    from enum import StrEnum
    assert hasattr(enum, 'StrEnum'), "StrEnum not in enum module"
    # Should be Python 3.11+ native
    assert enum.StrEnum.__qualname__ == 'StrEnum'
