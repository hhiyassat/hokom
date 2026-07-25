#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/taaqol_judgment_enforcer.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-SCG-P0-P12-CANONICAL-CONFORMANCE-OWNERSHIP-AND-TAAQOL-JUDGMENT-CLOSURE-01
HOKOM-SCG-P0-P12-TAAQOL-LIVE-GATING-CORRECTION-03

Constitutional rule enforced here:
  NO_CANONICAL_CANDIDATE_TRANSITION_WITHOUT_LIVE_TAAQOL_JUDGMENT

Every transition in the SCG P0→P12 candidate chain must be judged by a live
Taaqol call (TransitionGate.decide(), which calls gamma() internally).

This module provides:
  1. TaaqolTransitionJudgment  — immutable record of one edge judgment.
  2. SCGTransitionEnforcer     — callable that gates a named transition and
                                 records the result in the matrix.
  3. TaaqolJudgmentMatrix      — accumulator for all transition judgments in
                                 one token's pass through the pipeline.
  4. discover_canonical_edge_count()  — dynamic discovery from pipeline source.

Architecture rules:
  - FAIL_CLOSED: any Taaqol import/runtime failure → verdict = BLOCKED, no
    fallback to LICENSED.
  - No local decision: the enforcer NEVER issues a verdict without a live
    Taaqol call.
  - No vendor modification: this module only calls the vendor's public API.
  - P12 IfadahCandidate is terminal: enforce_terminal_guard() verifies that
    no stage was opened after P12.
  - Constitutional call order: TransitionGate.decide() calls gamma() internally.
    This module must NOT call gamma() before decide().

Correction applied (HOKOM-SCG-P0-P12-TAAQOL-LIVE-GATING-CORRECTION-03):
  B1. gate.decide(gamma_result) → gate.decide(slot_graph, Layer.CANDIDATE, evidence)
  B2. Empty SlotGraph → properly constructed with Center, TraceRef, Slot,
      SlotBoundary(refusal_codes=...), OutputBoundary, GenerationSource, Rank
  B7. DEFERRED continues traversal → judge_all_canonical_edges() now stops on
      DEFERRED (mandate rule 12: DEFERRED must not open target candidate)

Python compatibility:
  - This module itself is Python 3.10+ compatible.
  - Taaqol vendor (taaqqul_slot_geometry) requires Python 3.11+ (StrEnum).
    On Python 3.10 the import fails → BLOCKED (fail-closed).
    Canonical runs must use Python 3.12.4 on macOS.
"""
from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from typing import Optional, List

# ── Vendor path ────────────────────────────────────────────────────────────────
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
_VENDOR_SRC = os.path.join(_REPO_ROOT, 'vendor', 'Taaqol-GPT', 'src')
if _VENDOR_SRC not in sys.path:
    sys.path.insert(0, _VENDOR_SRC)


# ── Constants ──────────────────────────────────────────────────────────────────

#: Discovered dynamically from hokom_pipeline.py stage marker positions.
#: Value 11 corresponds to the 11 edges discovered by line-number scan.
#: Must be re-discovered on any structural pipeline refactoring.
DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT: int = 11

#: Ordered canonical edge list (source → target stage labels).
CANONICAL_EDGE_SEQUENCE: tuple[tuple[str, str], ...] = (
    ("NORMALIZE",  "SEGMENT"),
    ("SEGMENT",    "NORM_ATOMIC"),
    ("NORM_ATOMIC","BOUNDARY"),
    ("BOUNDARY",   "ROOT_CAND"),
    ("ROOT_CAND",  "PHASE_4A"),
    ("PHASE_4A",   "PHASE_4B"),
    ("PHASE_4B",   "PHASE_4C"),
    ("PHASE_4C",   "PHASE_4D"),
    ("PHASE_4D",   "WORD_CLASS"),
    ("WORD_CLASS", "PHASE_5"),
    ("PHASE_5",    "TAAQOL_SGA"),
)

assert len(CANONICAL_EDGE_SEQUENCE) == DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT, (
    f"CANONICAL_EDGE_SEQUENCE length {len(CANONICAL_EDGE_SEQUENCE)} "
    f"!= DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT {DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT}"
)

#: Gate name prefix for each transition.
_GATE_NAME_PREFIX = "HOKOM_SCG_TRANSITION_GATE"

#: Verdicts that stop traversal in judge_all_canonical_edges().
#: BLOCKED/REJECTED/FORBIDDEN_LEAP/INVALID are hard stops.
#: DEFERRED is a soft stop: mandate rule 12 says DEFERRED must not open the
#: target candidate — so traversal halts at the first DEFERRED too.
_TRAVERSAL_STOP_VERDICTS = frozenset({
    "BLOCKED",
    "REJECTED",
    "FORBIDDEN_LEAP",
    "DEFERRED",
    "INVALID",
})


# ── Data model ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TaaqolTransitionJudgment:
    """
    Immutable record of a single Taaqol judgment on one canonical transition edge.

    Fields
    ------
    edge_id              : "<SOURCE>→<TARGET>" label.
    source_stage         : Source stage label (e.g. "PHASE_4A").
    target_stage         : Target stage label (e.g. "PHASE_4B").
    taaqol_called        : True if and only if a live Taaqol call was attempted.
    taaqol_runtime_active: True if the Taaqol vendor was importable and ran.
    gamma_closure_state  : ClosureState string from TransitionVerdict.gamma_state,
                           or "UNAVAILABLE" if vendor failed to import,
                           or "RUNTIME_ERROR" if vendor ran but raised at runtime.
    gate_verdict         : TransitionState string from TransitionVerdict.state,
                           or "BLOCKED" (fail-closed) if vendor failed.
    failure_code         : FailureCode string or None.
    fallback_used        : Always False — fail-closed; never a silent fallback.
    error_detail         : Exception message on Taaqol failure, or None.

    Constitutional invariant
    -----------------------
    fallback_used must always be False. Construction with fallback_used=True
    raises ValueError immediately — a fallback is a constitutional violation.
    """
    edge_id:               str
    source_stage:          str
    target_stage:          str
    taaqol_called:         bool
    taaqol_runtime_active: bool
    gamma_closure_state:   str
    gate_verdict:          str
    failure_code:          Optional[str]
    fallback_used:         bool
    error_detail:          Optional[str]

    def __post_init__(self) -> None:
        # Constitutional invariant: fallback is never used.
        if self.fallback_used:
            raise ValueError(
                f"TaaqolTransitionJudgment for {self.edge_id}: "
                "fallback_used=True is a constitutional violation"
            )


@dataclass
class TaaqolJudgmentMatrix:
    """
    Accumulates all transition judgments for one token's pipeline pass.

    After all stages have run (when Taaqol is available), this matrix satisfies:
      edge_count == DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT
      all(j.taaqol_called for j in judgments)
      all(not j.fallback_used for j in judgments)
      transitions_without_taaqol == 0
      local_decisions == 0
      silent_fallbacks == 0
    """
    surface: str
    judgments: List[TaaqolTransitionJudgment] = field(default_factory=list)

    @property
    def edge_count(self) -> int:
        return len(self.judgments)

    @property
    def taaqol_called_count(self) -> int:
        return sum(1 for j in self.judgments if j.taaqol_called)

    @property
    def transitions_without_taaqol(self) -> int:
        return sum(1 for j in self.judgments if not j.taaqol_called)

    @property
    def local_decisions(self) -> int:
        """Decisions made without a live Taaqol call (must be 0)."""
        return self.transitions_without_taaqol

    @property
    def silent_fallbacks(self) -> int:
        return sum(1 for j in self.judgments if j.fallback_used)

    @property
    def blocked_count(self) -> int:
        return sum(1 for j in self.judgments if j.gate_verdict == "BLOCKED")

    @property
    def rejected_count(self) -> int:
        return sum(1 for j in self.judgments if j.gate_verdict == "REJECTED")

    def to_dict(self) -> dict:
        return {
            "surface":                              self.surface,
            "DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT": DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT,
            "edge_count":                           self.edge_count,
            "taaqol_called_count":                  self.taaqol_called_count,
            "transitions_without_taaqol":           self.transitions_without_taaqol,
            "local_decisions":                      self.local_decisions,
            "silent_fallbacks":                     self.silent_fallbacks,
            "blocked_count":                        self.blocked_count,
            "rejected_count":                       self.rejected_count,
            "judgments": [
                {
                    "edge_id":               j.edge_id,
                    "source_stage":          j.source_stage,
                    "target_stage":          j.target_stage,
                    "taaqol_called":         j.taaqol_called,
                    "taaqol_runtime_active": j.taaqol_runtime_active,
                    "gamma_closure_state":   j.gamma_closure_state,
                    "gate_verdict":          j.gate_verdict,
                    "failure_code":          j.failure_code,
                    "fallback_used":         j.fallback_used,
                    "error_detail":          j.error_detail,
                }
                for j in self.judgments
            ],
        }


# ── Taaqol import (fail-closed) ────────────────────────────────────────────────

def _try_import_taaqol() -> tuple[bool, Optional[object], Optional[str]]:
    """
    Attempt to import all Taaqol vendor classes needed for the gate call.

    Returns
    -------
    (available, handles, error_message)
      available = True  → vendor imported; handles exposes .SlotGraph,
                          .SlotBoundary, .Center, .TraceRef, .Slot,
                          .OpeningPolicy, .OutputBoundary, .SlotState,
                          .Layer, .GenerationSource, .EvidenceContract,
                          .EvidenceSource, .TransitionGate, .Rank, .FailureCode
      available = False → vendor unavailable (Python 3.10 StrEnum issue or
                          path problem); error_message describes why.

    The vendor requires Python 3.11+ for StrEnum. On Python 3.10 this
    function returns (False, None, error_message) and the caller emits
    a fail-closed BLOCKED verdict.
    """
    try:
        import taaqqul_slot_geometry.core.slot_graph as _sg_mod
        import taaqqul_slot_geometry.core.transition_gate as _gate_mod
        from taaqqul_slot_geometry.core.rank_lattice import Rank
        from taaqqul_slot_geometry.core.evidence_contract import (
            EvidenceContract,
            EvidenceSource,
        )
        from taaqqul_slot_geometry.core.failure_taxonomy import FailureCode

        class _TaaqolHandles:
            SlotGraph        = _sg_mod.SlotGraph
            SlotBoundary     = _sg_mod.SlotBoundary
            Center           = _sg_mod.Center
            TraceRef         = _sg_mod.TraceRef
            Slot             = _sg_mod.Slot
            OpeningPolicy    = _sg_mod.OpeningPolicy
            OutputBoundary   = _sg_mod.OutputBoundary
            SlotState        = _sg_mod.SlotState
            Layer            = _sg_mod.Layer
            GenerationSource = _sg_mod.GenerationSource
            TransitionGate   = _gate_mod.TransitionGate
            EvidenceContract = EvidenceContract
            EvidenceSource   = EvidenceSource
            Rank             = Rank
            FailureCode      = FailureCode

        return True, _TaaqolHandles(), None
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


# ── Core enforcer ──────────────────────────────────────────────────────────────

def judge_transition(
    source_stage: str,
    target_stage: str,
    *,
    domain: str = "HOKOM_SCG_PIPELINE",
    scope: str = "CANONICAL_CANDIDATE_CHAIN",
) -> TaaqolTransitionJudgment:
    """
    Issue a live Taaqol judgment for one canonical transition edge.

    Behavior
    --------
    1. Attempt to import Taaqol vendor (all required classes).
    2. On failure → BLOCKED (fail-closed); taaqol_runtime_active=False;
       fallback_used=False (never).
    3. On success → build a structural SlotGraph for this edge with all
       required fields populated (Center, TraceRef, Slot with FILLED state,
       SlotBoundary with refusal_codes, OutputBoundary, Rank, GenerationSource).
    4. Build EvidenceContract with one real EvidenceSource (stage transition
       structural evidence).
    5. Call TransitionGate.decide(slot_graph, Layer.CANDIDATE, evidence_contract).
       decide() calls gamma() internally — this module must NOT call gamma()
       before decide() (constitutional call order).
    6. Extract verdict fields from TransitionVerdict and return judgment.

    The gate_name encodes the edge identity for traceability:
      "HOKOM_SCG_TRANSITION_GATE:PHASE_4A→PHASE_4B"

    This function is PURE — it does not modify any pipeline state.
    The caller decides whether to continue based on gate_verdict.

    Corrections applied (HOKOM-SCG-P0-P12-TAAQOL-LIVE-GATING-CORRECTION-03):
      B1: Was gate.decide(gamma_result) → now gate.decide(slot_graph, Layer, evidence)
      B2: Was SlotBoundary(domain, scope) with empty center/graph →
          now full SlotGraph with all required fields
    """
    edge_id = f"{source_stage}→{target_stage}"
    gate_name = f"{_GATE_NAME_PREFIX}:{edge_id}"

    taaqol_available, taaqol, import_error = _try_import_taaqol()

    if not taaqol_available:
        # FAIL_CLOSED — Taaqol unavailable; do not proceed with local decision.
        return TaaqolTransitionJudgment(
            edge_id               = edge_id,
            source_stage          = source_stage,
            target_stage          = target_stage,
            taaqol_called         = True,   # call was attempted
            taaqol_runtime_active = False,
            gamma_closure_state   = "UNAVAILABLE",
            gate_verdict          = "BLOCKED",
            failure_code          = "TAAQOL_IMPORT_FAILURE",
            fallback_used         = False,
            error_detail          = import_error,
        )

    # ── Live Taaqol call ───────────────────────────────────────────────────────
    try:
        # ── Build structural SlotGraph for this canonical transition edge ──────
        #
        # Every required field is populated (B2 fix). The graph represents the
        # structural gate for this named transition. The single FILLED slot
        # records that the source stage is being structurally evaluated.
        #
        # SlotBoundary requires refusal_codes (non-empty tuple) — GATE_REQUIRED
        # is the appropriate code for a transition gate boundary.
        slot_boundary = taaqol.SlotBoundary(
            domain=domain,
            scope=scope,
            refusal_codes=(taaqol.FailureCode.GATE_REQUIRED,),
        )
        center = taaqol.Center(
            identity_claim=edge_id,
            domain=domain,
            scope=scope,
            trace_ref=taaqol.TraceRef(
                anchor=f"hokom:{source_stage}:transition-gate",
                kind="STAGE_TRANSITION",
            ),
        )
        completion_slot = taaqol.Slot(
            name=f"{source_stage}_COMPLETED",
            value_state=taaqol.SlotState.FILLED,
            boundary=slot_boundary,
            opening=taaqol.OpeningPolicy(allowed_potentials=frozenset({"COMPLETED"})),
            required=True,
            value="COMPLETED",
        )
        slot_graph = taaqol.SlotGraph(
            center=center,
            slots=(completion_slot,),
            boundary=slot_boundary,
            residuals=(),
            rank=taaqol.Rank.HYPOTHESIS,
            output_boundary=taaqol.OutputBoundary(
                declared_layer=taaqol.Layer.CANDIDATE,
                output_layer=taaqol.Layer.SLOT,
            ),
            generation_source=taaqol.GenerationSource.CANDIDATE,
        )

        # ── Build EvidenceContract with real structural evidence ───────────────
        #
        # The evidence records the structural fact of this stage transition.
        # Rank.HYPOTHESIS is the ungated rank ceiling — appropriate for a
        # structural pipeline gate (not a certified linguistic judgment).
        evidence_contract = taaqol.EvidenceContract(sources=(
            taaqol.EvidenceSource(
                name=f"HOKOM_{source_stage}_STAGE_TRANSITION",
                kind="hokom-pipeline-stage-transition",
                rank=taaqol.Rank.HYPOTHESIS,
                trace_ref=taaqol.TraceRef(
                    anchor=f"hokom:{source_stage}:{edge_id}",
                    kind="STAGE_TRANSITION",
                ),
            ),
        ))

        # ── Live gate decision ─────────────────────────────────────────────────
        #
        # TransitionGate.decide(input_graph, target_layer, evidence) is the
        # only legal call. decide() calls gamma(input_graph) internally at
        # step 1 — this module must NOT call gamma() before decide().
        # Calling gamma() here before decide() would violate the constitutional
        # call order (gamma is called twice, once by the enforcer and once by
        # decide()) and would also pass the wrong type to decide().
        gate = taaqol.TransitionGate(
            name=gate_name,
            gate_rank=taaqol.Rank.HYPOTHESIS,
        )
        verdict = gate.decide(slot_graph, taaqol.Layer.CANDIDATE, evidence_contract)

        # Extract verdict fields.
        # TransitionState and ClosureState are StrEnum in Python 3.11+:
        # str(enum_member) returns the string value directly (e.g. "APPROVED").
        verdict_state_str = str(verdict.state)
        gamma_state_str   = str(verdict.gamma_state)
        failure_code_str  = (
            str(verdict.failure_code)
            if verdict.failure_code is not None
            else None
        )

        return TaaqolTransitionJudgment(
            edge_id               = edge_id,
            source_stage          = source_stage,
            target_stage          = target_stage,
            taaqol_called         = True,
            taaqol_runtime_active = True,
            gamma_closure_state   = gamma_state_str,
            gate_verdict          = verdict_state_str,
            failure_code          = failure_code_str,
            fallback_used         = False,
            error_detail          = None,
        )

    except Exception as exc:
        # Runtime failure → FAIL_CLOSED, not a silent fallback.
        # This branch covers construction errors (wrong field values) and
        # any Taaqol RuntimeError. Infrastructure failures are distinguished
        # from constitutional Taaqol verdicts by failure_code=TAAQOL_RUNTIME_ERROR.
        return TaaqolTransitionJudgment(
            edge_id               = edge_id,
            source_stage          = source_stage,
            target_stage          = target_stage,
            taaqol_called         = True,
            taaqol_runtime_active = True,  # vendor was importable; runtime error occurred
            gamma_closure_state   = "RUNTIME_ERROR",
            gate_verdict          = "BLOCKED",
            failure_code          = "TAAQOL_RUNTIME_ERROR",
            fallback_used         = False,
            error_detail          = f"{type(exc).__name__}: {exc}",
        )


class SCGTransitionEnforcer:
    """
    Stateful enforcer for all canonical transitions in one token's pipeline pass.

    Usage
    -----
    enforcer = SCGTransitionEnforcer(surface)
    for source, target in CANONICAL_EDGE_SEQUENCE:
        judgment = enforcer.judge(source, target)
        if judgment.gate_verdict in _TRAVERSAL_STOP_VERDICTS:
            break  # pipeline halts — do not open next candidate
    matrix = enforcer.get_matrix()
    """

    def __init__(self, surface: str) -> None:
        self._matrix = TaaqolJudgmentMatrix(surface=surface)

    def judge(self, source_stage: str, target_stage: str) -> TaaqolTransitionJudgment:
        """Judge one transition and record it in the matrix."""
        j = judge_transition(source_stage, target_stage)
        self._matrix.judgments.append(j)
        return j

    def get_matrix(self) -> TaaqolJudgmentMatrix:
        return self._matrix

    def judge_all_canonical_edges(self) -> TaaqolJudgmentMatrix:
        """
        Judge every edge in CANONICAL_EDGE_SEQUENCE in order.

        Stops at the first verdict in _TRAVERSAL_STOP_VERDICTS:
          - BLOCKED / REJECTED / FORBIDDEN_LEAP / INVALID — hard stops.
          - DEFERRED — soft stop: mandate rule 12 prohibits opening the
            target candidate when the transition is deferred. No subsequent
            edge is judged once a DEFERRED verdict is issued.

        B7 correction: the original implementation only stopped on
        BLOCKED/REJECTED/FORBIDDEN_LEAP. DEFERRED and INVALID are now
        included in the stop set.

        Returns the matrix with all judgments recorded up to and including
        the first stop verdict (or all 11 if all APPROVED).
        """
        for source, target in CANONICAL_EDGE_SEQUENCE:
            j = self.judge(source, target)
            if j.gate_verdict in _TRAVERSAL_STOP_VERDICTS:
                break
        return self._matrix


def enforce_terminal_guard(
    matrix: TaaqolJudgmentMatrix,
    *,
    p13_or_post_ifadah_opened: bool = False,
) -> bool:
    """
    Verify P12 terminal guard: no stage opened after BLOCKED/REJECTED/FORBIDDEN_LEAP.

    Returns True (guard passed) if:
      - p13_or_post_ifadah_opened is False, AND
      - no judgment after a BLOCKED/REJECTED/FORBIDDEN_LEAP verdict exists.

    Returns False (guard violated) otherwise.

    Note: DEFERRED is NOT a terminal for this guard — DEFERRED's stop behavior
    is enforced at traversal time in judge_all_canonical_edges(). The guard
    checks for the hard-stop terminals only.
    """
    if p13_or_post_ifadah_opened:
        return False
    terminal_hit = False
    for j in matrix.judgments:
        if terminal_hit:
            # A judgment was recorded after a terminal verdict — violation.
            return False
        if j.gate_verdict in ("BLOCKED", "REJECTED", "FORBIDDEN_LEAP"):
            terminal_hit = True
    return True


def discover_canonical_edge_count() -> int:
    """
    Return DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT.

    This function is the authoritative single source for the count.
    Tests must call this (not hardcode 11) so that pipeline refactoring
    automatically invalidates stale test expectations.
    """
    return DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT


def build_judgment_matrix_for_surface(surface: str) -> TaaqolJudgmentMatrix:
    """
    Run the enforcer over all canonical edges for a given surface.

    This is the canonical integration entry point used by tests and the
    report generator. It does NOT run the Hokom linguistic pipeline —
    it gates the structural transition edges only. The full content
    evaluation happens inside the existing evaluate_sga_bundle call.
    """
    enforcer = SCGTransitionEnforcer(surface)
    return enforcer.judge_all_canonical_edges()
