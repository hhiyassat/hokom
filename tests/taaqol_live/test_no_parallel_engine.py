"""
Tests that verify the single-bridge, single-decision-engine invariant.
No Taaqol import required — passes on Python 3.10+.
"""
from __future__ import annotations

from pipeline.taaqol_integration.live.models import TaaqolIntegrationOwnershipGate


def test_no_parallel_bridges():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.parallel_bridges == 0


def test_no_parallel_decision_engines():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.parallel_decision_engines == 0


def test_no_silent_fallbacks():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.silent_fallbacks == 0


def test_gate_is_closed():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.is_closed()


def test_only_one_canonical_entrypoint():
    """
    Canonical entrypoints are evaluate_hokom_claim_bundle (legacy HokomLinguisticClaimBundle)
    and evaluate_sga_bundle (T-03 typed SGA boundary, requires HokomClaimBundle).
    No other evaluate_* functions are permitted.
    """
    from pipeline.taaqol_integration.live.bridge import (
        evaluate_hokom_claim_bundle,
        evaluate_sga_bundle,
    )
    assert callable(evaluate_hokom_claim_bundle)
    assert callable(evaluate_sga_bundle)
    import pipeline.taaqol_integration.live.bridge as _bridge
    eval_funcs = sorted(
        name for name in dir(_bridge)
        if name.startswith('evaluate_') and callable(getattr(_bridge, name))
    )
    _ALLOWED = sorted(['evaluate_hokom_claim_bundle', 'evaluate_sga_bundle'])
    assert eval_funcs == _ALLOWED, \
        f"Unexpected evaluate_* functions: got {eval_funcs}, expected {_ALLOWED}"


def test_no_shadow_mode_in_live_bridge():
    """Live bridge has no shadow mode — it's strict only."""
    import pipeline.taaqol_integration.live.bridge as _bridge
    assert not hasattr(_bridge, 'run_shadow_comparison'), \
        "Shadow mode must not exist in the live bridge"
    assert not hasattr(_bridge, 'shadow_mode'), \
        "Shadow mode must not exist in the live bridge"


def test_gate_to_dict_parallel_counts():
    gate = TaaqolIntegrationOwnershipGate()
    d = gate.to_dict()
    assert d['parallel_bridges'] == 0
    assert d['parallel_decision_engines'] == 0
    assert d['silent_fallbacks'] == 0


def test_gate_fail_closed_is_true():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.fail_closed is True


def test_gate_strict_mode_active():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.strict_mode_active is True


def test_all_pipeline_components_wired():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.slot_graph_wired, "SlotGraph not wired"
    assert gate.gamma_wired, "Gamma not wired"
    assert gate.transition_gate_wired, "TransitionGate not wired"


def test_integration_owner():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.integration_owner == 'HOKOM'


def test_integration_mode_strict():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.integration_mode == 'STRICT'
