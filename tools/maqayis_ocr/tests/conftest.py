"""
conftest.py — Maqayis OCR v2 test configuration

Provides shared fixtures for the test suite.

Path ordering matters: tools/maqayis_ocr/pipeline.py must NOT shadow
the hokom pipeline/ package.  We aggressively remove the maqayis_ocr
directory from sys.path and pin the hokom repo root at position 0 so
that `import pipeline` resolves to pipeline/ (the Taaqol package).
The maqayis_ocr dir is re-added AFTER so its other modules remain
importable by tests that need them.
"""
import sys
import os
import pathlib

# Resolved (symlink-safe) paths
_SELF         = pathlib.Path(__file__).resolve()
_MAQAYIS_DIR  = str(_SELF.parents[1])   # tools/maqayis_ocr/
_HOKOM_ROOT   = str(_SELF.parents[3])   # hokom/

# --- 1. Strip every occurrence of _MAQAYIS_DIR from sys.path ---------------
# Use resolved comparison to handle symlink variants.
def _same_path(a: str, b: str) -> bool:
    try:
        return pathlib.Path(a).resolve() == pathlib.Path(b).resolve()
    except Exception:
        return a == b

sys.path[:] = [p for p in sys.path if not _same_path(p, _MAQAYIS_DIR)]

# --- 2. Ensure hokom root is at position 0 ----------------------------------
sys.path[:] = [p for p in sys.path if not _same_path(p, _HOKOM_ROOT)]
sys.path.insert(0, _HOKOM_ROOT)

# --- 3. Re-add maqayis_ocr dir AFTER hokom root ----------------------------
sys.path.insert(1, _MAQAYIS_DIR)

# --- 4. Evict any stale 'pipeline' module so the next import is fresh ------
sys.modules.pop("pipeline", None)
