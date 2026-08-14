"""
Clean-room reproducibility harness for the Taaqol canonical integration tests
(RC-B). Two guarantees, established BEFORE any test in this package imports the
vendor or opens a runtime artifact:

  1. VENDOR AUTHORITY — the in-repo submodule vendor (vendor/Taaqol-GPT/src,
     pinned at the committed gitlink SHA) is the ONE authority. On a developer
     machine an editable install (`pip install -e` of an external Taaqol clone)
     can shadow it via a site-packages `.pth`; we defeat that by putting the
     in-repo vendor at sys.path[0] and evicting any pre-cached external module.
     A genuinely clean clone must run `git submodule update --init --recursive`.

  2. ARTIFACT REGENERATION — `reports/taaqol_full_integration/c9_runtime_output/
     ayat_al_dayn_results.csv` is a DETERMINISTIC OUTPUT of the canonical
     generator (scripts/demo_ayat_al_dayn.py over the in-repo Ayat al-Dayn
     corpus), NOT a hand-authored fixture. It is git-ignored, so a clean
     checkout lacks it. We regenerate it from canonical source and verify its
     schema — we never depend on a stale committed copy.

Neither action touches production source; both are test-harness setup.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── 1. In-repo vendor authority (runs at conftest import, before test modules) ──
_VENDOR_SRC = os.path.join(_REPO, "vendor", "Taaqol-GPT", "src")
if os.path.isdir(os.path.join(_VENDOR_SRC, "taaqqul_slot_geometry")):
    for _m in [m for m in list(sys.modules)
               if m == "taaqqul_slot_geometry" or m.startswith("taaqqul_slot_geometry.")]:
        del sys.modules[_m]
    while _VENDOR_SRC in sys.path:
        sys.path.remove(_VENDOR_SRC)
    sys.path.insert(0, _VENDOR_SRC)


# ── 2. Regenerate the ephemeral canonical CSV from source + verify schema ──────
_C9_DIR = os.path.join(_REPO, "reports", "taaqol_full_integration", "c9_runtime_output")
_C9_CSV = os.path.join(_C9_DIR, "ayat_al_dayn_results.csv")
_REQUIRED_COLUMNS = ("token_index", "original_surface", "word_class")


def _regenerate_c9_csv() -> None:
    """Deterministically regenerate the C9 runtime CSV from the canonical
    generator (no --taaqol: the consumed columns are P0–P5 facts only)."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    subprocess.run(
        [sys.executable, os.path.join(_REPO, "scripts", "demo_ayat_al_dayn.py"),
         "--output-dir", _C9_DIR],
        cwd=_REPO, env=env, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )


@pytest.fixture(scope="session", autouse=True)
def canonical_c9_runtime_csv():
    """Session fixture: regenerate the canonical C9 CSV from source and verify
    its schema. Autouse so every test in this package sees a fresh artifact."""
    _regenerate_c9_csv()
    assert os.path.isfile(_C9_CSV), f"canonical generator did not write {_C9_CSV}"
    with open(_C9_CSV, encoding="utf-8") as f:
        header = f.readline()
        rows = sum(1 for _ in f)
    missing = [c for c in _REQUIRED_COLUMNS if c not in header]
    assert not missing, f"C9 CSV missing required columns: {missing}"
    assert rows > 0, "C9 CSV has no data rows"
    return _C9_CSV
