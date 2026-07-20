"""
Structural integrity tests: no parallel bridge, no duplicate decision engines.

HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME
"""
from __future__ import annotations
import glob
import os


def test_single_canonical_bridge():
    """Only one bridge.py in the pipeline tree."""
    import pipeline.taaqol_integration.live.bridge as bridge_mod
    bridge_path = bridge_mod.__file__
    # bridge.py lives at: <project>/pipeline/taaqol_integration/live/bridge.py
    # 4 dirname() calls → project root
    project_root = bridge_path
    for _ in range(4):
        project_root = os.path.dirname(project_root)
    bridge_files = glob.glob(
        os.path.join(project_root, 'pipeline', '**', 'bridge.py'),
        recursive=True,
    )
    assert len(bridge_files) == 1, (
        f"Expected 1 bridge file, found {len(bridge_files)}: {bridge_files}"
    )


def test_no_taaqol_live_directory_duplicate():
    """pipeline/taaqol_live/ must not exist — canonical is pipeline/taaqol_integration/live/."""
    import pipeline
    pkg_dir = os.path.dirname(pipeline.__file__)
    duplicate = os.path.join(pkg_dir, 'taaqol_live')
    assert not os.path.exists(duplicate), (
        f"Duplicate taaqol directory: {duplicate}"
    )


def test_canonical_entrypoint_is_evaluate_hokom_claim_bundle():
    """The canonical entrypoint must be evaluate_hokom_claim_bundle."""
    from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
    from pipeline.taaqol_integration.live.models import TAAQOL_LIVE_CANONICAL_ENTRYPOINT
    assert TAAQOL_LIVE_CANONICAL_ENTRYPOINT == 'evaluate_hokom_claim_bundle'
    assert callable(evaluate_hokom_claim_bundle)


def test_no_parallel_decision_engines():
    """TaaqolIntegrationOwnershipGate must record 0 parallel engines."""
    from pipeline.taaqol_integration.live.models import TaaqolIntegrationOwnershipGate
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.parallel_bridges == 0
    assert gate.parallel_decision_engines == 0
    assert gate.silent_fallbacks == 0
    assert gate.is_closed()


def test_vendor_unchanged():
    """vendor/Taaqol-GPT must have no uncommitted changes."""
    import subprocess
    vendor_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'vendor', 'Taaqol-GPT',
    )
    if not os.path.exists(vendor_path):
        return  # no vendor dir in this environment
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=vendor_path, capture_output=True, text=True,
    )
    assert result.stdout.strip() == '', (
        f"vendor/Taaqol-GPT has uncommitted changes:\n{result.stdout}"
    )


def test_no_segmentation_files_in_bridge():
    """bridge.py must not import from p0_segmentation directly."""
    import pipeline.taaqol_integration.live.bridge as bridge_mod
    bridge_src = open(bridge_mod.__file__).read()
    assert 'p0_segmentation' not in bridge_src, (
        "bridge.py must not import from p0_segmentation — "
        "segmentation fields arrive pre-wired in the claim bundle"
    )
