"""
HOKOM-TAAQOL-LIVE-BRIDGE-RECOVERY-01

Tests verifying the path fix and liveness contract for the Taaqol live bridge.

Architecture: SlotGraph → Gamma → TransitionGate → TraceLedger (trace events)

Key invariants tested:
  1. _REPO_ROOT resolves to actual repo root (4 parents from bridge.py, not 3)
  2. vendor/Taaqol-GPT exists at the computed path
  3. Vendor submodule SHA matches the pinned commit
  4. taaqqul_slot_geometry imports successfully (requires Python 3.11+)
  5. SlotGraph, Gamma, TransitionGate, and trace events all execute
  6. Runtime failure is distinct from semantic DEFER (never silent fallback)
  7. hokom() exposes taaqol_runtime with active=True when chain executes

Tests that require taaqqul_slot_geometry are skipped on Python < 3.11
(where StrEnum is unavailable) rather than failing — the canonical runtime
is Python 3.12.4 on Darwin.
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

import pytest

# ── Repo root discovery (must not rely on the bridge's own _REPO_ROOT) ────────
_THIS_FILE   = Path(__file__).resolve()
_TESTS_DIR   = _THIS_FILE.parent.parent          # tests/
_REPO_ROOT   = _TESTS_DIR.parent                 # <repo>/
_VENDOR_PATH = _REPO_ROOT / 'vendor' / 'Taaqol-GPT'
_VENDOR_SRC  = _VENDOR_PATH / 'src'

EXPECTED_PIN = '35381739410071ac21dd96702ecbb2acb493f90d'

# ── Taaqol availability guard ─────────────────────────────────────────────────
_TAAQOL_AVAILABLE = False
try:
    if str(_VENDOR_SRC) not in sys.path:
        sys.path.insert(0, str(_VENDOR_SRC))
    import taaqqul_slot_geometry as _tsg  # noqa: F401
    _TAAQOL_AVAILABLE = True
except ImportError:
    pass

requires_taaqol = pytest.mark.skipif(
    not _TAAQOL_AVAILABLE,
    reason="taaqqul_slot_geometry not importable (requires Python 3.11+; "
           "canonical runtime is Python 3.12.4 on Darwin)",
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. _REPO_ROOT resolves correctly (path bug fix)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_repo_root_resolves_correctly():
    """
    _REPO_ROOT in bridge.py must point to the actual repo root, not pipeline/.

    bridge.py is at <repo>/pipeline/taaqol_integration/live/bridge.py.
    4 parents: live/ → taaqol_integration/ → pipeline/ → <repo>/
    The old code used Path(__file__).parent.parent.parent (3 parents → pipeline/).
    The fix uses Path(__file__).resolve().parents[3] (4 parents → repo root).

    We verify by reading the source and checking the _REPO_ROOT expression,
    and by computing what bridge.py's _REPO_ROOT should resolve to at runtime.
    """
    bridge_file = _REPO_ROOT / 'pipeline' / 'taaqol_integration' / 'live' / 'bridge.py'
    assert bridge_file.exists(), f"bridge.py not found at expected path: {bridge_file}"

    # Verify the source uses parents[3] (not parent.parent.parent)
    source = bridge_file.read_text(encoding='utf-8')
    assert 'parents[3]' in source, (
        "bridge.py does not use Path(__file__).resolve().parents[3]\n"
        "The _REPO_ROOT line must read: _REPO_ROOT = Path(__file__).resolve().parents[3]"
    )
    assert '_REPO_ROOT = Path(__file__).parent.parent.parent\n' not in source, (
        "bridge.py still has the old 3-parent path bug"
    )

    # Compute what bridge.py's _REPO_ROOT resolves to at runtime
    computed_root = bridge_file.resolve().parents[3]
    assert computed_root == _REPO_ROOT, (
        f"bridge._REPO_ROOT would resolve to {computed_root!r} != expected {_REPO_ROOT!r}"
    )

    # Must have vendor/ and pipeline/ at repo root
    assert (_REPO_ROOT / 'vendor').is_dir(), "vendor/ missing at _REPO_ROOT"
    assert (_REPO_ROOT / 'pipeline').is_dir(), "pipeline/ missing at _REPO_ROOT"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Vendor path exists
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_vendor_path_exists():
    """vendor/Taaqol-GPT must exist at the repo root computed by the bridge."""
    assert _VENDOR_PATH.exists(), (
        f"vendor/Taaqol-GPT not found at {_VENDOR_PATH}\n"
        f"Run: git submodule update --init --recursive"
    )
    assert _VENDOR_SRC.exists(), (
        f"vendor/Taaqol-GPT/src not found at {_VENDOR_SRC}"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Vendor SHA matches pinned commit
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_vendor_sha_matches_pin():
    """vendor/Taaqol-GPT must be at the exact pinned SHA."""
    result = subprocess.run(
        ['git', '-C', str(_VENDOR_PATH), 'rev-parse', 'HEAD'],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, (
        f"git rev-parse failed in vendor/Taaqol-GPT: {result.stderr}"
    )
    actual_sha = result.stdout.strip()
    assert actual_sha == EXPECTED_PIN, (
        f"vendor SHA drift detected!\n"
        f"  expected: {EXPECTED_PIN}\n"
        f"  actual:   {actual_sha}\n"
        f"vendor/Taaqol-GPT must be pinned to {EXPECTED_PIN[:8]}..."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Public entrypoint loads
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@requires_taaqol
def test_taaqol_public_entrypoint_loads():
    """taaqqul_slot_geometry must import without error."""
    import taaqqul_slot_geometry as tsg
    assert hasattr(tsg, 'SlotGraph'), "SlotGraph not exported from taaqqul_slot_geometry"
    assert hasattr(tsg, 'Gamma') or hasattr(tsg, 'TransitionGate'), (
        "Neither Gamma nor TransitionGate exported — unexpected API change"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. SlotGraph can be instantiated
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@requires_taaqol
def test_slot_graph_created():
    """A minimal SlotGraph must be constructible from the Taaqol API."""
    import taaqqul_slot_geometry as tsg

    trace_ref = tsg.TraceRef(anchor='test:يَكْتُبُ', kind='hokom_claim')
    center = tsg.Center(
        identity_claim='test:يَكْتُبُ',
        domain='hokom_morphology',
        scope='يَكْتُبُ',
        trace_ref=trace_ref,
    )
    boundary = tsg.SlotBoundary(
        domain='hokom_morphology',
        scope='arabic_morphology',
        refusal_codes=(tsg.FailureCode.BOUNDARY_MISSING,),
        licensed_operations=('morphological_analysis',),
    )
    slot = tsg.Slot(
        name='domain_claim',
        value_state=tsg.SlotState.FILLED,
        boundary=tsg.SlotBoundary(
            domain='hokom_domain_claim',
            scope='domain_directive',
            refusal_codes=(tsg.FailureCode.REQUIRED_SLOT_EMPTY,),
        ),
        opening=tsg.OpeningPolicy(
            allowed_potentials=frozenset({'ACCEPT', 'DEFER', 'BLOCK'}),
        ),
        required=True,
        value='ACCEPT',
    )
    output_boundary = tsg.OutputBoundary(
        declared_layer=tsg.Layer.TEXT_ENTRY,
        output_layer=tsg.Layer.TEXT_ENTRY,
    )
    entry_boundary = tsg.EntryBoundary(
        declared_entry_kind='HOKOM_MORPHOLOGICAL_ANALYSIS',
        representation_status='REPRESENTATIONAL',
        ontological_status='NOT_ONTOLOGICAL',
        sound_status='NOT_SOUND',
        meaning_status='NOT_MEANING',
        prior_trace_status='PRIOR_TRACE_PRESERVED',
        produces_only='TextTraceCandidate',
    )
    slot_graph = tsg.SlotGraph(
        center=center,
        slots=(slot,),
        boundary=boundary,
        residuals=(),
        rank=tsg.Rank.HYPOTHESIS,
        output_boundary=output_boundary,
        generation_source=tsg.GenerationSource.DECLARED_ENTRY,
        entry_boundary=entry_boundary,
    )
    assert slot_graph is not None
    assert slot_graph.center.scope == 'يَكْتُبُ'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Gamma executes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@requires_taaqol
def test_gamma_executes():
    """gamma(slot_graph) must execute and return a GammaResult."""
    import taaqqul_slot_geometry as tsg
    from taaqqul_slot_geometry.core.gamma import gamma

    trace_ref = tsg.TraceRef(anchor='test:gamma', kind='hokom_claim')
    center = tsg.Center(
        identity_claim='test:gamma',
        domain='hokom_morphology',
        scope='كَتَبَ',
        trace_ref=trace_ref,
    )
    slot = tsg.Slot(
        name='domain_claim',
        value_state=tsg.SlotState.FILLED,
        boundary=tsg.SlotBoundary(
            domain='hokom_domain_claim',
            scope='domain_directive',
            refusal_codes=(tsg.FailureCode.REQUIRED_SLOT_EMPTY,),
        ),
        opening=tsg.OpeningPolicy(
            allowed_potentials=frozenset({'ACCEPT', 'DEFER', 'BLOCK'}),
        ),
        required=True,
        value='ACCEPT',
    )
    slot_graph = tsg.SlotGraph(
        center=center,
        slots=(slot,),
        boundary=tsg.SlotBoundary(
            domain='hokom_morphology',
            scope='arabic_morphology',
            refusal_codes=(tsg.FailureCode.BOUNDARY_MISSING,),
            licensed_operations=('morphological_analysis',),
        ),
        residuals=(),
        rank=tsg.Rank.HYPOTHESIS,
        output_boundary=tsg.OutputBoundary(
            declared_layer=tsg.Layer.TEXT_ENTRY,
            output_layer=tsg.Layer.TEXT_ENTRY,
        ),
        generation_source=tsg.GenerationSource.DECLARED_ENTRY,
        entry_boundary=tsg.EntryBoundary(
            declared_entry_kind='HOKOM_MORPHOLOGICAL_ANALYSIS',
            representation_status='REPRESENTATIONAL',
            ontological_status='NOT_ONTOLOGICAL',
            sound_status='NOT_SOUND',
            meaning_status='NOT_MEANING',
            prior_trace_status='PRIOR_TRACE_PRESERVED',
            produces_only='TextTraceCandidate',
        ),
    )
    gamma_result = gamma(slot_graph)
    assert gamma_result is not None
    assert hasattr(gamma_result, 'state'), "GammaResult must have .state"
    assert hasattr(gamma_result, 'rank'), "GammaResult must have .rank"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. TransitionGate executes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@requires_taaqol
def test_gate_executes():
    """TransitionGate.decide() must execute and return a verdict with .state."""
    import taaqqul_slot_geometry as tsg
    from taaqqul_slot_geometry.core.gamma import gamma

    trace_ref = tsg.TraceRef(anchor='test:gate', kind='hokom_claim')
    center = tsg.Center(
        identity_claim='test:gate',
        domain='hokom_morphology',
        scope='كَتَبَ',
        trace_ref=trace_ref,
    )
    slot = tsg.Slot(
        name='domain_claim',
        value_state=tsg.SlotState.FILLED,
        boundary=tsg.SlotBoundary(
            domain='hokom_domain_claim',
            scope='domain_directive',
            refusal_codes=(tsg.FailureCode.REQUIRED_SLOT_EMPTY,),
        ),
        opening=tsg.OpeningPolicy(
            allowed_potentials=frozenset({'ACCEPT', 'DEFER', 'BLOCK'}),
        ),
        required=True,
        value='ACCEPT',
    )
    slot_graph = tsg.SlotGraph(
        center=center,
        slots=(slot,),
        boundary=tsg.SlotBoundary(
            domain='hokom_morphology',
            scope='arabic_morphology',
            refusal_codes=(tsg.FailureCode.BOUNDARY_MISSING,),
            licensed_operations=('morphological_analysis',),
        ),
        residuals=(),
        rank=tsg.Rank.HYPOTHESIS,
        output_boundary=tsg.OutputBoundary(
            declared_layer=tsg.Layer.TEXT_ENTRY,
            output_layer=tsg.Layer.TEXT_ENTRY,
        ),
        generation_source=tsg.GenerationSource.DECLARED_ENTRY,
        entry_boundary=tsg.EntryBoundary(
            declared_entry_kind='HOKOM_MORPHOLOGICAL_ANALYSIS',
            representation_status='REPRESENTATIONAL',
            ontological_status='NOT_ONTOLOGICAL',
            sound_status='NOT_SOUND',
            meaning_status='NOT_MEANING',
            prior_trace_status='PRIOR_TRACE_PRESERVED',
            produces_only='TextTraceCandidate',
        ),
    )
    evidence = tsg.EvidenceContract(sources=())
    gate = tsg.TransitionGate(name='TEST_GATE', gate_rank=tsg.Rank.STRONG)
    verdict = gate.decide(
        input_graph=slot_graph,
        target_layer=tsg.Layer.CANDIDATE,
        evidence=evidence,
    )
    assert verdict is not None
    assert hasattr(verdict, 'state'), "TransitionVerdict must have .state"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. TraceLedger has events after full evaluation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@requires_taaqol
def test_trace_ledger_has_event():
    """After full bridge evaluation, taaqol_runtime.trace_event_count must be > 0."""
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from hokom_pipeline import hokom
    r  = hokom('يَكْتُبُ')
    rt = r.get('taaqol_runtime') or {}
    assert rt.get('trace_event_count', 0) > 0, (
        f"trace_event_count={rt.get('trace_event_count')} — "
        f"bridge evaluation produced no trace events"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. Runtime failure is NOT a semantic DEFER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_runtime_failure_is_not_semantic_defer():
    """
    When taaqol_runtime.active=False, taaqol_verdict in hokom() must be None.

    This test exercises the liveness contract regardless of whether Taaqol
    is available. When the runtime is unavailable, the bridge must not
    silently return a semantic DEFER — it must set active=False and
    leave taaqol_verdict=None in the hokom() output.
    """
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from hokom_pipeline import hokom
    r  = hokom('يَكْتُبُ')
    rt = r.get('taaqol_runtime') or {}

    if not rt.get('active'):
        # Runtime unavailable: taaqol_verdict must be None (not a semantic string)
        verdict = r.get('taaqol_verdict')
        assert verdict is None, (
            f"SILENT FALLBACK DETECTED: taaqol_runtime.active=False but "
            f"taaqol_verdict={verdict!r} — runtime failure must not produce "
            f"a semantic verdict. Check that bridge failure_code is set and "
            f"hokom_pipeline.py gates taaqol_verdict on active=True."
        )
    else:
        # Runtime available: taaqol_verdict may be a semantic string
        failure_code = rt.get('failure_code')
        assert failure_code is None, (
            f"taaqol_runtime.active=True but failure_code={failure_code!r} — "
            f"active and failure_code are mutually exclusive"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. No silent fallback — wrong vendor path raises explicit error
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_no_silent_fallback():
    """
    When the vendor path is wrong, taaqol_runtime must record a failure_code,
    not silently return a semantic DEFER.

    We verify the contract via the real bridge with the correct path:
    if it returns active=False, failure_code must be non-None (explicit failure).
    There must be no path where active=False and failure_code=None simultaneously.
    """
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from hokom_pipeline import hokom
    r  = hokom('يَكْتُبُ')
    rt = r.get('taaqol_runtime') or {}

    if not rt.get('active'):
        # Silent fallback = active=False AND failure_code=None
        assert rt.get('failure_code') is not None, (
            "SILENT FALLBACK: taaqol_runtime.active=False but failure_code=None\n"
            "Every failed execution path must record a failure_code."
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 11. Taaqol vendor not modified (read-only SHA check)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_taaqol_not_modified():
    """vendor/Taaqol-GPT must be at the exact pinned SHA — no drift allowed."""
    if not _VENDOR_PATH.exists():
        pytest.skip("vendor/Taaqol-GPT not found — submodule not initialized")
    result = subprocess.run(
        ['git', '-C', str(_VENDOR_PATH), 'rev-parse', 'HEAD'],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"git rev-parse failed: {result.stderr}"
    actual_sha = result.stdout.strip()
    assert actual_sha == EXPECTED_PIN, (
        f"VENDOR SHA DRIFT: vendor/Taaqol-GPT is at {actual_sha[:8]}... "
        f"not pinned {EXPECTED_PIN[:8]}...\n"
        f"Run: git -C vendor/Taaqol-GPT checkout {EXPECTED_PIN}"
    )
    # Also verify working tree is clean inside vendor
    dirty = subprocess.run(
        ['git', '-C', str(_VENDOR_PATH), 'status', '--porcelain'],
        capture_output=True, text=True, timeout=10,
    )
    assert dirty.stdout.strip() == '', (
        f"vendor/Taaqol-GPT has uncommitted changes:\n{dirty.stdout}"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 12. Live pipeline integration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@requires_taaqol
def test_live_pipeline_integration():
    """
    hokom('يَكْتُبُ') must return taaqol_runtime.active=True and gate_executed=True.

    This is the integration smoke test: the full chain
    SlotGraph → Gamma → TransitionGate must execute end-to-end.
    """
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from hokom_pipeline import hokom

    r  = hokom('يَكْتُبُ')
    rt = r.get('taaqol_runtime') or {}

    assert rt.get('active') is True, (
        f"taaqol_runtime.active={rt.get('active')} — "
        f"failure_code={rt.get('failure_code')!r}, "
        f"failure_detail={rt.get('failure_detail')!r}"
    )
    assert rt.get('kernel_loaded') is True, "kernel_loaded must be True when active=True"
    assert rt.get('slot_graph_created') is True, "slot_graph_created must be True"
    assert rt.get('gamma_executed') is True, "gamma_executed must be True"
    assert rt.get('gate_executed') is True, "gate_executed must be True"
    assert rt.get('trace_event_count', 0) > 0, "trace_event_count must be > 0"
    assert rt.get('failure_code') is None, (
        f"failure_code must be None when active=True, got {rt.get('failure_code')!r}"
    )

    vendor_sha = rt.get('vendor_sha') or ''
    assert str(vendor_sha).startswith(EXPECTED_PIN[:8]), (
        f"vendor_sha={vendor_sha!r} does not start with {EXPECTED_PIN[:8]}"
    )

    # taaqol_verdict must be a semantic string (not None) when active
    verdict = r.get('taaqol_verdict')
    assert verdict is not None, (
        "taaqol_verdict must be set when taaqol_runtime.active=True"
    )
    assert verdict in ('LICENSED', 'DEFERRED', 'BLOCKED'), (
        f"Unexpected taaqol_verdict={verdict!r}"
    )
