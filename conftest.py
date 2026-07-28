# Root conftest: exclude vendor directory from test collection
collect_ignore_glob = ["vendor/*"]

import sys, pathlib
# ensure repo root is on sys.path so `scripts.*` and top-level modules are importable
_root = str(pathlib.Path(__file__).parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

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

