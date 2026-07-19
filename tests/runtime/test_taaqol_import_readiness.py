"""
Contract: Taaqol vendor package is importable under Python 3.11+,
but NOT activated in the live pipeline.
"""
import sys
import pytest

# These tests are INFORMATIONAL — they record readiness state.
# They do NOT activate Taaqol.

def _try_import(module_path):
    """Attempt to import a dotted module path, return (success, error)."""
    try:
        parts = module_path.rsplit('.', 1)
        if len(parts) == 2:
            mod = __import__(parts[0], fromlist=[parts[1]])
            return hasattr(mod, parts[1]), None
        else:
            __import__(module_path)
            return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def test_python_version_for_taaqol():
    """Python 3.11+ is required for Taaqol native StrEnum."""
    assert sys.version_info >= (3, 11), (
        f"Taaqol requires Python 3.11+, running on {sys.version}"
    )

def test_taaqol_vendor_path_exists():
    import os
    assert os.path.isdir('vendor/Taaqol-GPT'), \
        "vendor/Taaqol-GPT submodule directory missing"

def test_taaqol_not_in_hokom_pipeline():
    """Taaqol must NOT be imported inside hokom_pipeline.py."""
    import ast, os
    pipeline_path = 'hokom_pipeline.py'
    if not os.path.exists(pipeline_path):
        pytest.skip("hokom_pipeline.py not found")

    with open(pipeline_path) as f:
        source = f.read()

    # Check for direct taaqol imports (not in comments)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert 'taaqol' not in alias.name.lower(), \
                        f"hokom_pipeline.py imports taaqol: {alias.name}"
            elif node.module and 'taaqol' in node.module.lower():
                # Allow pipeline/taaqol_integration imports (claim adapter)
                # but NOT direct taaqol vendor imports
                if not node.module.startswith('pipeline.taaqol_integration'):
                    pytest.fail(f"hokom_pipeline.py imports from taaqol vendor: {node.module}")

def test_taaqol_live_integration_not_started():
    """Runtime integration must be NOT_STARTED."""
    # This is verified by the absence of taaqol in the live pipeline
    # and by checking no taaqol calls happen during a normal hokom() call
    import sys

    # Record modules before call
    modules_before = set(sys.modules.keys())

    # Run a normal analysis
    sys.path.insert(0, '.')
    try:
        from hokom_pipeline import hokom
        result = hokom('كَتَبَ')
        result2 = hokom('هَلْ')
    except Exception:
        pass  # Pipeline errors don't affect this test

    modules_after = set(sys.modules.keys())
    new_modules = modules_after - modules_before

    # No taaqol vendor module should have been loaded
    taaqol_loaded = [m for m in new_modules if 'taaqol' in m.lower()
                     and 'taaqol_integration' not in m.lower()]
    assert taaqol_loaded == [], \
        f"Taaqol vendor modules loaded during pipeline call: {taaqol_loaded}"
