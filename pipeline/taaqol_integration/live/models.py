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
    # Amendment No. 3: split output into structured fields (T-05 partial closure)
    # These are optional to preserve backward compat with existing trace events.
    gamma_state: Optional[str] = None    # GammaResult.state when component='Gamma'
    gate_verdict: Optional[str] = None  # TransitionVerdict.state when component='TransitionGate'


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

    # Amendment No. 1 (RESUME): expose center scope for provenance tracing
    # Never None when Taaqol runs; None when DEFERRED before SlotGraph build.
    taaqol_center_scope: Optional[str] = None  # = morphological center used in Center.scope

    # Amendment No. 2 (HOKOM-TAAQOL-LIVE-BRIDGE-RECOVERY-01): liveness contract
    # Distinguishes runtime infrastructure failure from semantic evaluation outcome.
    # active=True means the full chain (SlotGraph→Gamma→Gate→Trace) executed.
    # active=False with failure_code="TAAQOL_RUNTIME_UNAVAILABLE" means import failed.
    # taaqol_verdict in hokom() output is None when active=False (never a semantic verdict).
    taaqol_runtime: Optional[dict] = None  # liveness contract dict; None if not populated

    # Amendment No. 3 (HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01):
    # typed slot payload, structured trace, and evidence contract.
    # All Optional for backward compatibility — None when SGA not available.
    typed_slots: Optional[tuple] = None        # tuple[dict, ...] — serialized TypedSlots
    taaqol_trace: Optional[tuple] = None       # tuple[dict, ...] — structured trace events
    evidence_contract: Optional[dict] = None   # EvidenceContract summary

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'HokomTaaqolDecision':
        """
        Reconstruct a HokomTaaqolDecision from to_dict() output.
        Handles both legacy (no typed_slots) and current format.
        """
        trace_raw = d.get('trace') or ()
        trace = tuple(
            HokomTaaqolTraceEvent(
                step=t.get('step', ''),
                component=t.get('component', ''),
                input_digest=t.get('input_digest', ''),
                output=t.get('output', ''),
                strict_mode=bool(t.get('strict_mode', True)),
                gamma_state=t.get('gamma_state'),
                gate_verdict=t.get('gate_verdict'),
            )
            if isinstance(t, dict) else t
            for t in trace_raw
        )
        return cls(
            bridge_id=d.get('bridge_id', HOKOM_TAAQOL_BRIDGE_ID),
            taaqol_commit=d.get('taaqol_commit', 'unknown'),
            hokom_commit=d.get('hokom_commit', 'unknown'),
            strict_mode=bool(d.get('strict_mode', True)),
            slot_graph_digest=d.get('slot_graph_digest', 'UNAVAILABLE'),
            gamma_result=d.get('gamma_result', 'UNAVAILABLE'),
            transition_gate_result=d.get('transition_gate_result', 'UNAVAILABLE'),
            taaqol_verdict=d.get('taaqol_verdict', 'DEFERRED'),
            reason_codes=tuple(d.get('reason_codes') or ()),
            contradictions=tuple(d.get('contradictions') or ()),
            residuals=tuple(d.get('residuals') or ()),
            trace=trace,
            upstream_verdict=d.get('upstream_verdict', 'DEFER'),
            effective_verdict=d.get('effective_verdict', 'DEFERRED'),
            fail_closed=bool(d.get('fail_closed', True)),
            source_engine=d.get('source_engine', 'TAAQOL'),
            taaqol_center_scope=d.get('taaqol_center_scope'),
            taaqol_runtime=d.get('taaqol_runtime'),
            typed_slots=tuple(d['typed_slots']) if d.get('typed_slots') else None,
            taaqol_trace=tuple(d['taaqol_trace']) if d.get('taaqol_trace') else None,
            evidence_contract=d.get('evidence_contract'),
        )


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
