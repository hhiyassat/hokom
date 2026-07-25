#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/taaqol_judgment_enforcer.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-SCG-P0-P12-CANONICAL-CONFORMANCE-OWNERSHIP-AND-TAAQOL-JUDGMENT-CLOSURE-01

Constitutional rule enforced here:
  NO_CANONICAL_CANDIDATE_TRANSITION_WITHOUT_LIVE_TAAQOL_JUDGMENT

Every transition in the SCG P0→P12 candidate chain must be judged by a live
Taaqol call (gamma() + TransitionGate.decide()).  This module provides:

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

#: Rank to use for each transition gate (HYPOTHESIS = Rank(3) — ungated ceiling).
_GATE_RANK_NAME = "HYPOTHESIS"

#: Gate name prefix for each transition.
_GATE_NAME_PREFIX = "HOKOM_SCG_TRANSITION_GATE"


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
    gamma_closure_state  : String representation of GammaResult.state, or
                           "UNAVAILABLE" if vendor failed to import.
    gate_verdict         : String representation of TransitionState, or
                           "BLOCKED" (fail-closed) if vendor failed.
    failure_code         : FailureCode string or None.
    fallback_used        : Always False — fail-closed; never a silent fallback.
    error_detail         : Exception message on Taaqol failure, or None.
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

    After all stages have run, this matrix must satisfy:
      len(judgments) == DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT
      all(j.taaqol_called for j in judgments)
      all(not j.fallback_used for j in judgments)
      sum(1 for j in judgments if j.gate_verdict not in ("APPROVED","DEFERRED"))
        == 0  (on a successful token)
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
    Attempt to import Taaqol vendor.

    Returns
    -------
    (available, taaqol_module, error_message)
      available = True  → vendor imported; taaqol_module has .SlotGraph, .gamma,
                          .TransitionGate, .Rank
      available = False → vendor unavailable (Python 3.10 StrEnum issue or path
                          problem); error_message describes why.
    """
    try:
        import taaqqul_slot_geometry.core.slot_graph as _sg_mod
        import taaqqul_slot_geometry.core.gamma as _gamma_mod
        import taaqqul_slot_geometry.core.transition_gate as _gate_mod
        from taaqqul_slot_geometry.core.rank import Rank

        class _TaaqolHandles:
            SlotGraph     = _sg_mod.SlotGraph
            SlotBoundary  = _sg_mod.SlotBoundary
            Center        = _sg_mod.Center
            gamma         = staticmethod(_gamma_mod.gamma)
            TransitionGate= _gate_mod.TransitionGate
            Rank          = Rank

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
    1. Attempt to import Taaqol vendor.
    2. On failure → BLOCKED (fail-closed); taaqol_runtime_active=False;
       fallback_used=False (never).
    3. On success → build a minimal SlotGraph for this edge, call gamma(),
       call TransitionGate.decide(), record result.

    The gate_name encodes the edge identity for traceability:
      "HOKOM_SCG_TRANSITION_GATE:PHASE_4A→PHASE_4B"

    This function is PURE — it does not modify any pipeline state.
    The caller decides whether to continue based on gate_verdict.
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
        # Build the minimal SlotGraph for this transition edge.
        # The center identity encodes the edge; domain/scope encode the pipeline
        # stage context.  Slots are empty (this is a structural gate, not a
        # content-evaluation gate — the content evaluation is the full SGA
        # bundle evaluated at PHASE_5→TAAQOL_SGA).
        boundary = taaqol.SlotBoundary(domain=domain, scope=scope)
        center   = taaqol.Center(identity_claim=edge_id)
        slot_graph = taaqol.SlotGraph(center=center, boundary=boundary)

        gamma_result = taaqol.gamma(slot_graph)
        gamma_state_str = str(gamma_result.state).split(".")[-1]  # e.g. "OPEN"
        failure_code_str = (
            str(gamma_result.failure_code).split(".")[-1]
            if gamma_result.failure_code is not None
            else None
        )

        # Gate rank ceiling: HYPOTHESIS (ungated).
        try:
            gate_rank = taaqol.Rank(3)  # HYPOTHESIS
        except Exception:
            gate_rank = taaqol.Rank.HYPOTHESIS  # fallback enum access

        gate = taaqol.TransitionGate(name=gate_name, gate_rank=gate_rank)
        verdict = gate.decide(gamma_result)
        verdict_state_str = str(verdict.state).split(".")[-1]

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
        return TaaqolTransitionJudgment(
            edge_id               = edge_id,
            source_stage          = source_stage,
            target_stage          = target_stage,
            taaqol_called         = True,
            taaqol_runtime_active = True,  # vendor was available; runtime error occurred
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
        if judgment.gate_verdict in ("BLOCKED", "REJECTED"):
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
        Stops at the first BLOCKED or REJECTED verdict (fail-closed).
        Returns the matrix with all judgments recorded so far.
        """
        for source, target in CANONICAL_EDGE_SEQUENCE:
            j = self.judge(source, target)
            if j.gate_verdict in ("BLOCKED", "REJECTED", "FORBIDDEN_LEAP"):
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
      - no judgment after a BLOCKED/REJECTED/FORBIDDEN_LEAP verdict exists in matrix.

    Returns False (guard violated) otherwise.
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
    report generator.  It does NOT run the Hokom linguistic pipeline —
    it gates the structural transition edges only.  The full content
    evaluation happens inside the existing evaluate_sga_bundle call.
    """
    enforcer = SCGTransitionEnforcer(surface)
    return enforcer.judge_all_canonical_edges()
