"""C12 import-isolation regression tests.

Proves that run_all() is idempotent under sys.modules['pipeline'] mutation,
which occurs when pytest collects tools/maqayis_ocr/tests/ (its default
import mode adds the OCR test file's parent to sys.path[0], where a bare
`pipeline.py` shadows Hokom's `pipeline/` package).

Repair location:
    scripts/demo_ayat_al_dayn.py::_ensure_hokom_pipeline_module()

These tests must never modify tools/maqayis_ocr.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
CANONICAL_PIPELINE_INIT = str(REPO / "pipeline" / "__init__.py")


def _snapshot_early_stops(subprocess_code: str, timeout: int = 180) -> int:
    """Run `subprocess_code`, then snapshot demo early_stops, in a fresh subprocess."""
    full = f"""
import sys
sys.path.insert(0, '/Users/husseinhiyassat/hokom')
{subprocess_code}
from scripts import c12_diagnose_early_stop_state as diag
from pathlib import Path
out = diag.snapshot(Path('/tmp/_iso_test.json'))
print('EARLY_STOPS=' + str(out['totals']['early_stops']))
"""
    r = subprocess.run(
        [sys.executable, "-c", full], cwd=REPO,
        capture_output=True, text=True, timeout=timeout,
    )
    for line in r.stdout.splitlines():
        if line.startswith("EARLY_STOPS="):
            return int(line.split("=", 1)[1])
    raise RuntimeError(f"snapshot failed:\nSTDOUT:{r.stdout[-400:]}\nSTDERR:{r.stderr[-400:]}")


def test_fresh_process_early_stops_is_96():
    """Baseline: fresh process must always give 96 early stops."""
    assert _snapshot_early_stops("") == 96


def test_pipeline_pop_alone_does_not_change_result():
    """sys.modules.pop('pipeline', None) alone must not change the result."""
    assert _snapshot_early_stops("sys.modules.pop('pipeline', None)") == 96


def test_full_pytest_collection_then_demo_is_still_96():
    """The former failure mode: full pytest collect-only then demo.

    Before repair: 94. After repair: 96.
    """
    code = "import pytest; pytest.main(['--collect-only', '-q', '--no-header'])"
    assert _snapshot_early_stops(code, timeout=240) == 96


def test_ensure_hokom_pipeline_module_pins_canonical_package():
    """_ensure_hokom_pipeline_module() must pin sys.modules['pipeline'] to Hokom's package."""
    # Simulate the polluted state: replace sys.modules['pipeline'] with a fake
    import sys as _sys
    original = _sys.modules.get("pipeline")
    try:
        # Create a fake module object pointing to a different file
        import types
        fake = types.ModuleType("pipeline")
        fake.__file__ = "/tmp/fake_pipeline.py"
        _sys.modules["pipeline"] = fake
        # Now invoke the repair
        from scripts.demo_ayat_al_dayn import _ensure_hokom_pipeline_module
        _ensure_hokom_pipeline_module()
        # Verify sys.modules['pipeline'] is now Hokom's package
        current = _sys.modules["pipeline"]
        assert current is not fake
        assert current.__file__ == CANONICAL_PIPELINE_INIT, \
            f"pipeline module file wrong: {current.__file__}"
    finally:
        # Restore original
        if original is not None:
            _sys.modules["pipeline"] = original
        else:
            _sys.modules.pop("pipeline", None)


def test_canonical_pipeline_file_exists():
    """Sanity: the canonical Hokom pipeline package init file exists."""
    assert Path(CANONICAL_PIPELINE_INIT).is_file()


def test_ocr_bare_pipeline_py_file_still_exists_and_untouched():
    """The OCR utility pipeline.py must remain unmodified (user-owned WIP)."""
    ocr_pipeline = REPO / "tools" / "maqayis_ocr" / "pipeline.py"
    assert ocr_pipeline.is_file(), "OCR utility pipeline.py should exist"
    # Verify we haven't accidentally modified it
    content = ocr_pipeline.read_text()
    assert "Maqayis OCR" in content, "OCR pipeline.py content signature missing"
