# Root conftest: exclude vendor directory from test collection
collect_ignore_glob = ["vendor/*"]

import sys, pathlib, os
# ensure repo root is on sys.path so `scripts.*` and top-level modules are importable
_root = str(pathlib.Path(__file__).parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

# ── SUITE-WIDE VENDOR AUTHORITY (owner decision 2026-08-14, governed upgrade) ──
# The APPROVED Taaqol vendor is the in-repo submodule vendor/Taaqol-GPT (pinned at
# the committed gitlink SHA bc9d1ea5). A developer editable install
# (`__editable__.taaqqul_slot_geometry*.pth` → an external clone) must NOT be able
# to shadow it — that masking is exactly what let stale/mismatched vendor state pass
# undetected. We put the in-repo vendor at sys.path[0] and evict any pre-cached
# external module so the submodule is the SOLE runtime vendor authority for the
# whole suite. A clean clone must: git submodule update --init --recursive.
_VENDOR_SRC = os.path.join(_root, "vendor", "Taaqol-GPT", "src")
if os.path.isdir(os.path.join(_VENDOR_SRC, "taaqqul_slot_geometry")):
    for _m in [m for m in list(sys.modules)
               if m == "taaqqul_slot_geometry" or m.startswith("taaqqul_slot_geometry.")]:
        del sys.modules[_m]
    while _VENDOR_SRC in sys.path:
        sys.path.remove(_VENDOR_SRC)
    sys.path.insert(0, _VENDOR_SRC)

import pytest

from pathlib import Path as _HokomPath
import pytest as _hokom_pytest

_HOKOM_CANONICAL_REPORT_PATHS = (
    _HokomPath(__file__).resolve().parent
    / "reports/ayat_al_dayn_demo/ayat_al_dayn_manager_report.html",
    _HokomPath(__file__).resolve().parent
    / "reports/ayat_al_dayn_demo/ayat_al_dayn_results.csv",
    _HokomPath(__file__).resolve().parent
    / "reports/ayat_al_dayn_demo/ayat_al_dayn_results_full.json",
)

_HOKOM_CANONICAL_REPORT_BASELINE = {
    artifact: artifact.read_bytes() if artifact.exists() else None
    for artifact in _HOKOM_CANONICAL_REPORT_PATHS
}

# Lang-suffixed files are ephemeral (written by subprocess tests or lang-mode runs).
# They are never tracked in git HEAD, so always treat baseline as None → always deleted
# after each test, preventing UNTRACKED_ARTIFACT_COUNT accumulation.
_HOKOM_EPHEMERAL_REPORT_PATHS = (
    _HokomPath(__file__).resolve().parent
    / "reports/ayat_al_dayn_demo/ayat_al_dayn_manager_report_en.html",
    _HokomPath(__file__).resolve().parent
    / "reports/ayat_al_dayn_demo/ayat_al_dayn_results_en.csv",
    _HokomPath(__file__).resolve().parent
    / "reports/ayat_al_dayn_demo/ayat_al_dayn_manager_report_ar.html",
    _HokomPath(__file__).resolve().parent
    / "reports/ayat_al_dayn_demo/ayat_al_dayn_results_ar.csv",
)
_HOKOM_CANONICAL_REPORT_BASELINE.update({
    artifact: None  # Always delete — never restore
    for artifact in _HOKOM_EPHEMERAL_REPORT_PATHS
})


def _restore_hokom_canonical_reports():
    for artifact, original in _HOKOM_CANONICAL_REPORT_BASELINE.items():
        if original is None:
            artifact.unlink(missing_ok=True)
        else:
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_bytes(original)


@_hokom_pytest.fixture(autouse=True)
def _isolate_hokom_canonical_reports():
    _restore_hokom_canonical_reports()
    yield
    _restore_hokom_canonical_reports()

