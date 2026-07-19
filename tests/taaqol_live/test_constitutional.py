"""
Constitutional invariants for HOKOM-TAAQOL-LIVE-INTEGRATION-01.

Tests that do NOT import taaqqul_slot_geometry: pass on Python 3.10+.
Tests that DO import taaqqul_slot_geometry: skipped on Python < 3.11.
"""
from __future__ import annotations

import subprocess
import sys

from pipeline.taaqol_integration.live.models import (
    HOKOM_TAAQOL_BRIDGE_ID,
    TAAQOL_INTEGRATION_MODE,
    TAAQOL_INTEGRATION_OWNER,
    TAAQOL_LIVE_CANONICAL_ENTRYPOINT,
    TaaqolIntegrationOwnershipGate,
)


# ── Constants ─────────────────────────────────────────────────────────────────

def test_bridge_id():
    assert HOKOM_TAAQOL_BRIDGE_ID == 'HOKOM_TAAQOL_LIVE_BRIDGE'


def test_integration_owner():
    assert TAAQOL_INTEGRATION_OWNER == 'HOKOM'


def test_strict_mode():
    assert TAAQOL_INTEGRATION_MODE == 'STRICT'


def test_canonical_entrypoint_name():
    assert TAAQOL_LIVE_CANONICAL_ENTRYPOINT == 'evaluate_hokom_claim_bundle'


# ── Canonical entrypoint callable ─────────────────────────────────────────────

def test_canonical_entrypoint_callable():
    from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
    assert callable(evaluate_hokom_claim_bundle)


def test_canonical_entrypoint_is_named_correctly():
    from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
    assert evaluate_hokom_claim_bundle.__name__ == TAAQOL_LIVE_CANONICAL_ENTRYPOINT


# ── Ownership gate ────────────────────────────────────────────────────────────

def test_ownership_gate_closed():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.is_closed(), f"Gate is not closed: {gate}"


def test_fail_closed_invariant():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.fail_closed is True


def test_strict_mode_active():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.strict_mode_active is True


def test_no_parallel_bridges_in_gate():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.parallel_bridges == 0


def test_no_parallel_decision_engines_in_gate():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.parallel_decision_engines == 0


def test_no_silent_fallbacks_in_gate():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.silent_fallbacks == 0


def test_gate_status_closed():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.status == 'CLOSED'


def test_slot_graph_wired():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.slot_graph_wired is True


def test_gamma_wired():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.gamma_wired is True


def test_transition_gate_wired():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.transition_gate_wired is True


def test_upstream_upgrades_forbidden():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.upstream_upgrades_forbidden is True


def test_vendor_unmodified_flag():
    gate = TaaqolIntegrationOwnershipGate()
    assert gate.vendor_unmodified is True


def test_gate_to_dict_complete():
    gate = TaaqolIntegrationOwnershipGate()
    d = gate.to_dict()
    assert d['bridge_id'] == HOKOM_TAAQOL_BRIDGE_ID
    assert d['integration_mode'] == 'STRICT'
    assert d['fail_closed'] is True
    assert d['parallel_bridges'] == 0
    assert d['parallel_decision_engines'] == 0
    assert d['silent_fallbacks'] == 0


# ── Vendor integrity ──────────────────────────────────────────────────────────

def test_no_vendor_modification():
    """Verify vendor/Taaqol-GPT is unmodified."""
    result = subprocess.run(
        ['git', '-C', 'vendor/Taaqol-GPT', 'status', '--porcelain'],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"git failed: {result.stderr}"
    assert result.stdout.strip() == '', \
        f"vendor/Taaqol-GPT has been modified:\n{result.stdout}"


def test_integration_owner_is_hokom():
    """Bridge ID must start with HOKOM — no other owner."""
    assert HOKOM_TAAQOL_BRIDGE_ID.startswith('HOKOM_')


def test_bridge_id_unique_per_mandate():
    """Bridge ID must contain LIVE to distinguish from shadow mode."""
    assert 'LIVE' in HOKOM_TAAQOL_BRIDGE_ID
