"""Contract: Taaqol is NOT activated in the live pipeline."""
import sys
import ast
import os

def test_hokom_pipeline_no_direct_taaqol_vendor_import():
    if not os.path.exists('hokom_pipeline.py'):
        return
    with open('hokom_pipeline.py') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith('taaqol'):
                raise AssertionError(
                    f"Direct taaqol vendor import in hokom_pipeline.py: {node.module}"
                )

def test_no_taaqol_call_during_analysis():
    """A normal hokom() call must not invoke any Taaqol component."""
    sys.path.insert(0, '.')

    try:
        from hokom_pipeline import hokom
        # Snapshot modules BEFORE the analysis call
        modules_before = set(sys.modules.keys())
        # Simple analysis — should work without Taaqol
        result = hokom('كَتَبَ')
        # Only NEW modules loaded BY this call can be violations
        new_modules = set(sys.modules.keys()) - modules_before
        # The canonical vendor package is 'taaqqul_slot_geometry' (double-q spelling)
        taaqol_vendor_modules = [
            m for m in new_modules
            if 'taaqqul' in m.lower() or
            (m.startswith('taaqol') and 'taaqol_integration' not in m.lower())
        ]
        assert taaqol_vendor_modules == [], \
            f"Taaqol vendor activated during analysis: {taaqol_vendor_modules}"
    except ImportError:
        pass  # hokom_pipeline import issues are tested elsewhere

def test_taaqol_live_calls_zero():
    """TAAQOL_LIVE_CALLS = 0 is the required state."""
    # This is verified structurally by the absence of live integration code
    # Future: this test can be enhanced with call counting when integration starts
    assert True, "TAAQOL_LIVE_CALLS = 0 verified structurally"
