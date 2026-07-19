"""
Typed domain models for the live Taaqol governance integration.

HOKOM-TAAQOL-LIVE-INTEGRATION-01

All types are frozen=True, deterministic. No UUIDs. No random values.
No Taaqol imports here — this module is pure Python 3.10+ compatible.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Optional

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Constitutional constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM_TAAQOL_BRIDGE_ID            = 'HOKOM_TAAQOL_LIVE_BRIDGE'
TAAQOL_INTEGRATION_OWNER          = 'HOKOM'
TAAQOL_INTEGRATION_MODE           = 'STRICT'
TAAQOL_LIVE_CANONICAL_ENTRYPOINT  = 'evaluate_hokom_claim_bundle'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Exceptions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TaaqolIntegrationError(Exception):
    """Raised when Taaqol integration fails in a non-recoverable way."""


class TaaqolRuntimeUnavailableError(TaaqolIntegrationError):
    """Raised when Taaqol cannot be invoked (import error, missing deps)."""


class TaaqolContractViolationError(TaaqolIntegrationError):
    """Raised when a contract invariant is violated."""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data types — all frozen, all deterministic
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class HokomClaimProjection:
    """
    A single Hokom claim projected into the Taaqol slot domain.
    Deterministic: claim_id is content-hash based, no random values.
    """
    claim_id: str               # deterministic from content hash
    token_id: str
    original_surface: str
    normalized_surface: str
    claim_layer: str            # 'P5_BOUNDARY' | 'ROOT' | 'PATTERN' | 'WORD_CLASS' | etc.
    claim_kind: str             # what kind of claim this is
    proposed_value: str         # the proposed linguistic value
    upstream_verdict: str       # Hokom's own verdict
    evidence_rank: int          # 0-based rank
    supporting_evidence: tuple  # of str
    contradictions: tuple       # of str
    boundaries_crossed: tuple   # of str (layer transitions already validated)
    source_engine: str
    source_owner: str           # = 'HOKOM'
    upstream_trace: tuple       # of str
    residuals: tuple            # of str
    provenance: str             # = f"hokom:{hokom_commit}:taaqol:{taaqol_commit}"


@dataclass(frozen=True)
class HokomTaaqolTraceEvent:
    """One step in the Taaqol evaluation trace."""
    step: str
    component: str      # 'SlotGraph' | 'Gamma' | 'TransitionGate'
    input_digest: str
    output: str
    strict_mode: bool


@dataclass(frozen=True)
class HokomTaaqolResidual:
    """A residual produced during Taaqol evaluation."""
    code: str
    claim_id: str
    reason: str


@dataclass(frozen=True)
class HokomTaaqolDecision:
    """
    The canonical output of evaluate_hokom_claim_bundle.
    Immutable, deterministic, fully traced.
    """
    bridge_id: str                  # = HOKOM_TAAQOL_BRIDGE_ID
    taaqol_commit: str              # vendor submodule commit
    hokom_commit: str               # Hokom HEAD
    strict_mode: bool               # = True
    slot_graph_digest: str          # deterministic digest of SlotGraph
    gamma_result: str               # ClosureState string or 'UNAVAILABLE'
    transition_gate_result: str     # TransitionState string or 'UNAVAILABLE'
    taaqol_verdict: str             # 'LICENSED' | 'DEFERRED' | 'BLOCKED' | 'RESIDUAL'
    reason_codes: tuple             # of str
    contradictions: tuple           # of str
    residuals: tuple                # of str
    trace: tuple                    # of HokomTaaqolTraceEvent
    upstream_verdict: str           # Hokom's verdict before Taaqol
    effective_verdict: str          # composed final verdict
    fail_closed: bool               # = True
    source_engine: str              # = 'TAAQOL'

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Ownership gate — the single governance invariant record
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class TaaqolIntegrationOwnershipGate:
    """
    Constitutional invariant record for the Taaqol live integration.
    All parallel_* counters are 0. fail_closed and strict_mode_active are True.
    status is 'CLOSED'.
    """
    bridge_id:                    str  = HOKOM_TAAQOL_BRIDGE_ID
    integration_owner:            str  = TAAQOL_INTEGRATION_OWNER
    integration_mode:             str  = TAAQOL_INTEGRATION_MODE
    canonical_entrypoint:         str  = TAAQOL_LIVE_CANONICAL_ENTRYPOINT
    parallel_bridges:             int  = 0
    parallel_decision_engines:    int  = 0
    silent_fallbacks:             int  = 0
    fail_closed:                  bool = True
    strict_mode_active:           bool = True
    slot_graph_wired:             bool = True
    gamma_wired:                  bool = True
    transition_gate_wired:        bool = True
    upstream_upgrades_forbidden:  bool = True
    vendor_unmodified:            bool = True
    status:                       str  = 'CLOSED'

    def is_closed(self) -> bool:
        return (
            self.status == 'CLOSED'
            and self.parallel_bridges == 0
            and self.parallel_decision_engines == 0
            and self.silent_fallbacks == 0
            and self.fail_closed
            and self.strict_mode_active
            and self.slot_graph_wired
            and self.gamma_wired
            and self.transition_gate_wired
        )

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


__all__ = [
    'HOKOM_TAAQOL_BRIDGE_ID',
    'TAAQOL_INTEGRATION_OWNER',
    'TAAQOL_INTEGRATION_MODE',
    'TAAQOL_LIVE_CANONICAL_ENTRYPOINT',
    'TaaqolIntegrationError',
    'TaaqolRuntimeUnavailableError',
    'TaaqolContractViolationError',
    'HokomClaimProjection',
    'HokomTaaqolTraceEvent',
    'HokomTaaqolResidual',
    'HokomTaaqolDecision',
    'TaaqolIntegrationOwnershipGate',
]
