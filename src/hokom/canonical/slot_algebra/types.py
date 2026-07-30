"""
types.py — Slot Algebra Engineering core types for the 19-stage canonical
pipeline.

Design constraints:
    - All types are frozen (immutable) dataclasses.
    - No HR2S / H2RS imports anywhere in this file or its callers.
    - CandidateStatus mirrors Saleh's CandidateStatus (ACCEPTED/DEFERRED/BLOCKED).
    - SlotState is Hokom's typed extension for SGA-layer slot tracking.
    - EvidenceAtom aligns with Taaqol's EvidenceContract sources field.
    - Forbidden output flags match Saleh's candidate.py __post_init__ check.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Candidate status (mirrors Saleh qiyas_core.enums.CandidateStatus) ────────

class CandidateStatus(Enum):
    ACCEPTED = "accepted"
    DEFERRED = "deferred"
    BLOCKED  = "blocked"


# ── Slot state (Hokom SGA-layer extension) ────────────────────────────────────

class SlotState(Enum):
    """
    Typed slot lifecycle states used by Hokom's SGA bridge.

    UNKNOWN         — not yet evaluated
    CANDIDATE       — nominated, pending Taaqol licensing
    SUPPORTED       — evidence present but below LICENSE threshold
    LICENSED        — Taaqol granted_rank ≥ LICENSED (rank 4)
    DEFERRED        — insufficient evidence; will retry at next stage
    BLOCKED         — blocker condition fired; cannot advance
    AMBIGUOUS       — multiple competing licensed candidates
    RESIDUAL        — carries into next stage as residual evidence
    NOT_APPLICABLE  — stage not applicable for this input type
    """
    UNKNOWN        = "unknown"
    CANDIDATE      = "candidate"
    SUPPORTED      = "supported"
    LICENSED       = "licensed"
    DEFERRED       = "deferred"
    BLOCKED        = "blocked"
    AMBIGUOUS      = "ambiguous"
    RESIDUAL       = "residual"
    NOT_APPLICABLE = "not_applicable"


# ── Residual severity (mirrors Saleh qiyas_core.enums.ResidualSeverity) ──────

class ResidualSeverity(Enum):
    INFO    = "info"
    WARNING = "warning"
    BLOCKER = "blocker"


# ── Provenance reference ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProvenanceRef:
    """
    Typed reference to the source of an evidence atom.

    Fields:
        owner       — "hokom" | "saleh" | "taaqol"
        module_path — dotted Python module path
        rule_id     — rule or function identifier within the module
        stage_id    — Saleh canonical layer ID (e.g. "P3_ROOT_STEM_CLOSURE")
    """
    owner: str          # "hokom" | "saleh" | "taaqol"
    module_path: str
    rule_id: str
    stage_id: str

    def __post_init__(self) -> None:
        valid_owners = {"hokom", "saleh", "taaqol"}
        if self.owner not in valid_owners:
            raise ValueError(
                f"ProvenanceRef.owner must be one of {valid_owners}, "
                f"got '{self.owner}'"
            )
        if not self.stage_id:
            raise ValueError("ProvenanceRef.stage_id is required")


# ── Evidence atom ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EvidenceAtom:
    """
    Single unit of morphological evidence produced by Hokom and consumed
    by Taaqol's TransitionGate.

    Fields:
        key         — slot or property identifier (e.g. "ROOT_R1", "BAB_ID")
        value       — typed value (str | int | bool | None)
        confidence  — float [0.0, 1.0]; maps to Taaqol EvidenceRank tier
        provenance  — ProvenanceRef tracking the generating module/rule
        trace_id    — unique trace ID for ledger; None if not yet assigned
    """
    key: str
    value: Any
    confidence: float
    provenance: ProvenanceRef
    trace_id: str | None = None

    def __post_init__(self) -> None:
        # Provenance is required — fail at construction, not later in as_taaqol_sources()
        if self.provenance is None:
            raise ValueError(
                "EvidenceAtom.provenance is required; got None. "
                "Supply a ProvenanceRef with owner, module_path, rule_id, stage_id."
            )
        if not isinstance(self.provenance, ProvenanceRef):
            raise TypeError(
                f"EvidenceAtom.provenance must be a ProvenanceRef instance, "
                f"got {type(self.provenance)!r}"
            )
        # Provenance field guards
        if not self.provenance.stage_id:
            raise ValueError(
                "EvidenceAtom.provenance.stage_id is required"
            )
        if not self.provenance.owner:
            raise ValueError(
                "EvidenceAtom.provenance.owner is required"
            )
        # Existing guards
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"EvidenceAtom.confidence must be in [0.0, 1.0], "
                f"got {self.confidence}"
            )
        if not self.key:
            raise ValueError("EvidenceAtom.key is required")


# ── Evidence set ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EvidenceSet:
    """
    Collection of EvidenceAtoms for one stage evaluation.

    Aligns with Taaqol EvidenceContract (sources: list[str]).
    """
    stage_id: str
    atoms: tuple[EvidenceAtom, ...]
    aggregate_confidence: float   # min(atom.confidence for atom in atoms)

    def __post_init__(self) -> None:
        if not self.stage_id:
            raise ValueError("EvidenceSet.stage_id is required")
        if self.atoms:
            expected = min(a.confidence for a in self.atoms)
            if abs(self.aggregate_confidence - expected) > 1e-6:
                raise ValueError(
                    f"EvidenceSet.aggregate_confidence ({self.aggregate_confidence}) "
                    f"must equal min(atom.confidence) = {expected}"
                )

    @classmethod
    def from_atoms(cls, stage_id: str, atoms: tuple[EvidenceAtom, ...]) -> EvidenceSet:
        agg = min((a.confidence for a in atoms), default=0.0)
        return cls(stage_id=stage_id, atoms=atoms, aggregate_confidence=agg)

    def as_taaqol_sources(self) -> list[str]:
        """Produce source strings for Taaqol EvidenceContract."""
        return [
            f"{a.provenance.stage_id}:{a.key}={a.value}"
            for a in self.atoms
        ]


# ── Residual ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Residual:
    """
    Typed residual produced when a stage DEFERs or BLOCKs.

    Mirrors Saleh's residual.Residual structure.
    """
    residual_id: str
    stage_id: str
    reason_code: str
    severity: ResidualSeverity
    detail: str
    carries_forward: bool = True

    def __post_init__(self) -> None:
        if not self.residual_id:
            raise ValueError("Residual.residual_id is required")
        if not self.reason_code:
            raise ValueError("Residual.reason_code is required")


# ── CanonicalCandidate ────────────────────────────────────────────────────────

# Output flags absolutely forbidden in ANY candidate (Saleh law).
_FORBIDDEN_OUTPUT_FLAGS: frozenset[str] = frozenset({
    "HukmCandidate",
    "RealityClaim",
    "FinalMeaning",
    "FinalCaseJudgment",
})


@dataclass(frozen=True)
class CanonicalCandidate:
    """
    Typed candidate produced by a stage adapter and submitted to Taaqol
    for licensing.

    Mirrors Saleh's Candidate dataclass; adds Taaqol-facing fields.

    Fields:
        candidate_id    — unique within one stage evaluation
        candidate_type  — Saleh branch_output_type (e.g. "UnicodeCandidate")
        status          — CandidateStatus.ACCEPTED / DEFERRED / BLOCKED
        layer_id        — Saleh canonical layer ID
        source_rule_id  — generating rule/function name
        evidence        — EvidenceSet that supports this candidate
        slot_state      — Hokom SGA slot lifecycle state
        taaqol_rank     — Taaqol granted_rank (int, 0-6; 0 until licensed)
        residuals       — tuple of Residuals if DEFERRED/BLOCKED
        trace_ids       — trace ledger IDs
        output_flags    — frozenset; MUST NOT contain forbidden flags
    """
    candidate_id: str
    candidate_type: str
    status: CandidateStatus
    layer_id: str
    source_rule_id: str
    evidence: EvidenceSet
    slot_state: SlotState = SlotState.CANDIDATE
    taaqol_rank: int = 0
    residuals: tuple[Residual, ...] = ()
    trace_ids: tuple[str, ...] = ()
    output_flags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        bad_flags = self.output_flags & _FORBIDDEN_OUTPUT_FLAGS
        if bad_flags:
            raise ValueError(
                f"CanonicalCandidate.output_flags contains forbidden flags: "
                f"{bad_flags}"
            )
        if not (0 <= self.taaqol_rank <= 6):
            raise ValueError(
                f"taaqol_rank must be in [0, 6], got {self.taaqol_rank}"
            )
        if not self.candidate_id:
            raise ValueError("CanonicalCandidate.candidate_id is required")
        if not self.layer_id:
            raise ValueError("CanonicalCandidate.layer_id is required")


# ── CanonicalCandidateSet ─────────────────────────────────────────────────────

@dataclass(frozen=True)
class CanonicalCandidateSet:
    """
    Output of one stage adapter: a set of CanonicalCandidates.

    Mirrors Saleh's CandidateSet with Hokom evidence and Taaqol rank fields.
    """
    set_id: str
    layer_id: str
    candidates: tuple[CanonicalCandidate, ...]
    residuals: tuple[Residual, ...]
    trace_ids: tuple[str, ...]

    @property
    def accepted(self) -> tuple[CanonicalCandidate, ...]:
        return tuple(
            c for c in self.candidates if c.status is CandidateStatus.ACCEPTED
        )

    @property
    def deferred(self) -> tuple[CanonicalCandidate, ...]:
        return tuple(
            c for c in self.candidates if c.status is CandidateStatus.DEFERRED
        )

    @property
    def blocked(self) -> tuple[CanonicalCandidate, ...]:
        return tuple(
            c for c in self.candidates if c.status is CandidateStatus.BLOCKED
        )

    @property
    def highest_taaqol_rank(self) -> int:
        """Greatest Taaqol rank among all candidates (0 if empty)."""
        if not self.candidates:
            return 0
        return max(c.taaqol_rank for c in self.candidates)

    @property
    def is_licensed(self) -> bool:
        """True if at least one candidate has taaqol_rank >= 4 (LICENSED)."""
        return any(c.taaqol_rank >= 4 for c in self.candidates)
