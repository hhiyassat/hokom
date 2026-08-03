#!/usr/bin/env python3
"""Bisect the ordered test node list to find the smallest prefix that causes
scripts.demo_ayat_al_dayn.run_all() to produce EARLY_STOPS=94 instead of 96.

Usage:
  c12_bisect_early_stops.py                  # run full bisection
  c12_bisect_early_stops.py --prefix N       # run first N tests + snapshot only

Emits reports/taaqol_full_integration/c12_runtime_output/
  early_stop_pollution_bisect.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "reports/taaqol_full_integration/c12_runtime_output"
NODES_FILE = REPO / "tmp_c12_all_nodes.txt"


def _read_nodes() -> list[str]:
    if not NODES_FILE.exists():
        # Collect nodes
        cp = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=REPO, capture_output=True, text=True, check=False,
        )
        NODES_FILE.write_text(cp.stdout)
    lines = NODES_FILE.read_text().splitlines()
    return [ln for ln in lines if ln.startswith("tests/") or ln.startswith("tools/")]


def _run_prefix(prefix_nodes: list[str]) -> int:
    """Run a list of tests, then capture an early-stops snapshot in the same process.

    Returns the observed early_stop count.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = OUT_DIR / "early_stops_polluted.json"
    if snapshot_path.exists():
        snapshot_path.unlink()

    # Build a wrapper: import pytest, run given nodes with a fresh interpreter,
    # then in same process call the snapshot script.
    wrapper_code = f"""
import sys
from pathlib import Path
REPO = Path({str(REPO)!r})
sys.path.insert(0, str(REPO))
import pytest
nodes = {prefix_nodes!r}
# Run tests but suppress assertion failures — we only care about state side effects
pytest.main(['-q', '--tb=no', '-p', 'no:cacheprovider'] + nodes + ['--no-header', '-x', '--maxfail=99999'])
# Now snapshot the demo pipeline in the same process
from scripts import c12_diagnose_early_stop_state as diag
out = diag.snapshot(Path({str(OUT_DIR)!r}) / 'early_stops_polluted.json')
print('SNAPSHOT_TOTALS=' + str(out['totals']['early_stops']))
"""
    cp = subprocess.run(
        [sys.executable, "-c", wrapper_code], cwd=REPO,
        capture_output=True, text=True, check=False,
    )
    # Extract SNAPSHOT_TOTALS line
    for line in cp.stdout.splitlines():
        if line.startswith("SNAPSHOT_TOTALS="):
            return int(line.split("=", 1)[1])
    print("=== stdout ===", file=sys.stderr)
    print(cp.stdout, file=sys.stderr)
    print("=== stderr ===", file=sys.stderr)
    print(cp.stderr, file=sys.stderr)
    return -1


def bisect(nodes: list[str], target_node: str, expected: int, polluted: int) -> dict:
    """Binary search for the smallest prefix that produces `polluted` count."""
    idx_target = nodes.index(target_node)
    prefix = nodes[:idx_target]  # tests before the target
    lo, hi = 0, len(prefix)
    iterations = 0
    contaminating_range = (0, len(prefix))
    while lo < hi:
        iterations += 1
        mid = (lo + hi) // 2
        # Try FIRST HALF: does it alone contaminate?
        first_half = prefix[:mid] + [target_node]
        count = _run_prefix(first_half)
        print(f"iter {iterations}: prefix[:mid={mid}] → early_stops={count}")
        if count == polluted:
            # first half is enough to contaminate — search deeper into first half
            contaminating_range = (0, mid)
            hi = mid
        elif count == expected:
            # first half is NOT enough — contaminating test is in second half
            # Add second half to first half progressively — but simpler: search [mid, hi]
            contaminating_range = (mid, hi)
            lo = mid + 1
        else:
            print(f"unexpected count {count}; aborting bisect")
            break
    # contaminating_range now brackets the minimal culprit
    return {
        "iterations": iterations,
        "minimal_contaminating_range_start": contaminating_range[0],
        "minimal_contaminating_range_end": contaminating_range[1],
        "candidate_nodes": prefix[contaminating_range[0]:contaminating_range[1] + 1],
        "prefix_size": len(prefix),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if "--prefix" in sys.argv:
        n = int(sys.argv[sys.argv.index("--prefix") + 1])
        nodes = _read_nodes()
        target = "tests/demo/test_taaqol_layer_report.py::test_early_stops_count"
        subset = nodes[:n] + [target]
        count = _run_prefix(subset)
        print(f"prefix size {n} + target → early_stops={count}")
        return 0
    nodes = _read_nodes()
    target = "tests/demo/test_taaqol_layer_report.py::test_early_stops_count"
    assert target in nodes, f"target not found in {NODES_FILE}"
    result = bisect(nodes, target, expected=96, polluted=94)
    out = {
        "ordered_prefix_count": nodes.index(target),
        "bisect_iterations": result["iterations"],
        "minimal_contaminating_range": [result["minimal_contaminating_range_start"],
                                        result["minimal_contaminating_range_end"]],
        "candidate_nodes": result["candidate_nodes"],
        "fresh_early_stops": 96,
        "polluted_early_stops": 94,
    }
    (OUT_DIR / "early_stop_pollution_bisect.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
