"""Shared Hokom pipeline-identity boundary (C13 §6).

Guarantees that ``sys.modules['pipeline']`` resolves to the canonical
Hokom pipeline package (``/Users/husseinhiyassat/hokom/pipeline/__init__.py``)
regardless of pytest's default import-mode `prepend` behaviour, which
can otherwise insert ``tools/maqayis_ocr/`` into ``sys.path[0]`` and let
its bare ``pipeline.py`` utility script shadow the Hokom package.

Rationale (from C12-REPAIR-02 root-cause analysis):
    - pytest collects OCR test files under tools/maqayis_ocr/tests/
    - Its default import mode (prepend) adds the file's parent dir to sys.path[0]
    - The maqayis conftest.py executes sys.modules.pop("pipeline", None)
    - On next `import pipeline`, Python finds tools/maqayis_ocr/pipeline.py first
    - Downstream code sees the OCR utility instead of the Hokom package
    - 10 Ayat tokens' evidence enrichment changes (2 net early-stops difference)

This module is the SINGLE authoritative repair location. It must be
invoked at the start of every Hokom production entrypoint that
subsequently imports from `pipeline.*` and that may run in the same
Python process as pytest OCR collection.

Contract:
    - Never modifies tools/maqayis_ocr/
    - Never modifies vendor/
    - Never mutates test discovery
    - Deterministic under repeated import
    - Safe to call multiple times (idempotent)
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

# The canonical Hokom repo root — computed once at module load.
_HOKOM_ROOT: Path = Path(__file__).resolve().parents[3]
_CANONICAL_PIPELINE_INIT: str = str(_HOKOM_ROOT / "pipeline" / "__init__.py")


def ensure_hokom_pipeline_identity() -> None:
    """Guarantee ``sys.modules['pipeline']`` is the Hokom pipeline package.

    Steps:
      1. Check current ``sys.modules['pipeline'].__file__``.
      2. If absent, or if it does not point to the canonical Hokom
         pipeline/__init__.py, evict it and force re-import from the
         Hokom root.
      3. Ensure the Hokom root is at ``sys.path[0]`` before the re-import
         so Python resolves ``pipeline`` to the package, not a stray
         ``pipeline.py`` file elsewhere on the path.

    Idempotent. Safe to call from any Hokom entrypoint.
    """
    mod = sys.modules.get("pipeline")
    mod_file = getattr(mod, "__file__", None) if mod is not None else None
    if mod is None or mod_file != _CANONICAL_PIPELINE_INIT:
        sys.modules.pop("pipeline", None)
        hokom_root_str = str(_HOKOM_ROOT)
        # Move Hokom root to position 0 (evict any stale copy first)
        if hokom_root_str in sys.path:
            sys.path.remove(hokom_root_str)
        sys.path.insert(0, hokom_root_str)
        importlib.import_module("pipeline")


def verify_hokom_pipeline_identity() -> dict:
    """Return a diagnostic snapshot of the current pipeline identity state.

    Fields:
        canonical_origin: bool — True iff sys.modules['pipeline'] points
            to the canonical Hokom package init file.
        actual_file: current sys.modules['pipeline'].__file__ or None.
        canonical_file: the expected canonical init file path.
        shadowing_count: int — 1 if a shadowing pipeline.py exists on
            sys.path before the Hokom root, else 0.
    """
    mod = sys.modules.get("pipeline")
    actual_file = getattr(mod, "__file__", None) if mod is not None else None
    canonical_origin = (actual_file == _CANONICAL_PIPELINE_INIT)
    hokom_root_str = str(_HOKOM_ROOT)
    shadowing = 0
    for p in sys.path:
        if p == hokom_root_str:
            break
        candidate = os.path.join(p, "pipeline.py")
        if os.path.isfile(candidate):
            shadowing = 1
            break
    return {
        "canonical_origin": canonical_origin,
        "actual_file": actual_file,
        "canonical_file": _CANONICAL_PIPELINE_INIT,
        "shadowing_count": shadowing,
    }
