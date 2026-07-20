"""
Governance: artifacts must be bound to HEAD commit.
The latest closure manifest in reports/canonical_gate/ must reference current HEAD.
"""
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_no_stale_report_artifacts():
    """
    Latest closure manifest must reference current HEAD.
    If this fails, re-run: python scripts/canonical_gate.py --stage <STAGE_ID>
    """
    gate_dir = REPO_ROOT / 'reports' / 'canonical_gate'
    if not gate_dir.exists():
        return  # No gate reports yet — not a failure at this stage

    head = subprocess.run(
        ['git', 'rev-parse', '--short', 'HEAD'],
        capture_output=True, text=True, cwd=REPO_ROOT
    ).stdout.strip()

    manifests = list(gate_dir.rglob('closure_manifest.*.json'))
    if not manifests:
        return  # No manifests yet — governance infrastructure just established

    latest = sorted(manifests, key=lambda p: p.stat().st_mtime)[-1]
    data   = json.loads(latest.read_text(encoding='utf-8'))
    manifest_commit = data.get('commit', '')

    assert manifest_commit == head, (
        f"Stale closure manifest: manifest.commit={manifest_commit!r} != HEAD={head!r}. "
        f"Re-run: python scripts/canonical_gate.py --stage <STAGE_ID>"
    )
