"""
pipeline/taaqol_live — live Taaqol governance for Hokom claims.

HOKOM-TAAQOL-LIVE-INTEGRATION-01

Canonical entrypoint: evaluate_hokom_claim_bundle
Architecture: SlotGraph → Gamma → TransitionGate → strict decision
Ownership: HOKOM
Mode: STRICT
Fail-closed: True (never returns LICENSED on Taaqol failure)
"""
from __future__ import annotations

from .models import (
    HOKOM_TAAQOL_BRIDGE_ID,
    TAAQOL_INTEGRATION_MODE,
    TAAQOL_INTEGRATION_OWNER,
    TAAQOL_LIVE_CANONICAL_ENTRYPOINT,
    HokomClaimProjection,
    HokomTaaqolDecision,
    HokomTaaqolResidual,
    HokomTaaqolTraceEvent,
    TaaqolContractViolationError,
    TaaqolIntegrationError,
    TaaqolIntegrationOwnershipGate,
    TaaqolRuntimeUnavailableError,
)
from .bridge import evaluate_hokom_claim_bundle
from .decision_composition import compose_effective_verdict

__all__ = [
    # Constants
    'HOKOM_TAAQOL_BRIDGE_ID',
    'TAAQOL_INTEGRATION_OWNER',
    'TAAQOL_INTEGRATION_MODE',
    'TAAQOL_LIVE_CANONICAL_ENTRYPOINT',
    # Data types
    'HokomClaimProjection',
    'HokomTaaqolTraceEvent',
    'HokomTaaqolResidual',
    'HokomTaaqolDecision',
    # Exceptions
    'TaaqolIntegrationError',
    'TaaqolRuntimeUnavailableError',
    'TaaqolContractViolationError',
    # Ownership gate
    'TaaqolIntegrationOwnershipGate',
    # Canonical entrypoint
    'evaluate_hokom_claim_bundle',
    # Composition
    'compose_effective_verdict',
]
