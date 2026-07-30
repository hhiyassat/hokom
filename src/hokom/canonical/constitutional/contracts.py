"""
contracts.py — Constitutional judgment contracts for the 19-stage pipeline.

Maps Saleh's 10 constitutional LayerSpec questions onto Hokom's evaluation
of Arabic morphosyntactic evidence, with Taaqol as sole transition licensor.

Jurisprudential method:
    الوضع    (WadContract)        — conventional placement contract
    السبب    (SababEvidence)      — opening cause / trigger evidence
    الشرط    (ShartRequirement)   — conditions that must hold
    المانع   (ManiBlocker)        — blockers that prevent transition
    العلة    (IllahRationale)     — shared rationale / reason for qiyas
    القادح   (QadihDefect)        — defect that invalidates the qiyas
    الصحة    (SAHIH)              — valid, all conditions met, no blockers
    الفساد   (FASID)              — corrupt, conditions met but minor defect
    البطلان  (BATIL)              — null, essential condition missing
    التأجيل  (DEFERRED)           — insufficient evidence, retryable
    الأثر    (AtharEffect)        — licensed effect produced by SAHIH judgment
    البقايا  (BaqayaResidual)     — residuals carried forward
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..slot_algebra.types import EvidenceSet, Residual, ResidualSeverity


# ── Constitutional status ─────────────────────────────────────────────────────

class ConstitutionalStatus(Enum):
    """
    Constitutional judgment statuses.

    SAHIH    — صحيح: all conditions satisfied, no blockers, evidence licensed
    FASID    — فاسد: conditions satisfied but minor defect (non-fatal)
    BATIL    — باطل: essential condition missing (null judgment)
    DEFERRED — مؤجَّل: insufficient evidence; retry at later stage
    AMBIGUOUS — مبهم: multiple competing valid interpretations
    RESIDUAL  — بقايا: carries forward as residual evidence
    """
    SAHIH     = "sahih"
    FASID     = "fasid"
    BATIL     = "batil"
    DEFERRED  = "deferred"
    AMBIGUOUS = "ambiguous"
    RESIDUAL  = "residual"


# ── الوضع — WadContract ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class WadContract:
    """
    الوضع — conventional placement contract for a stage.

    Derived from the Saleh LayerSpec: captures what the stage is
    constitutionally placed to do (origin → branch via shared_cause).

    Fields:
        layer_id            — Saleh canonical layer ID
        placement_name      — Saleh LayerSpec.name
        placement_phase     — Saleh LayerSpec.phase
        shared_cause        — Saleh LayerSpec.shared_cause (العلة الجامعة)
        origin_output_type  — what the stage expects as input
        branch_output_type  — what the stage is contracted to produce
        is_terminal         — True only for P12_IFADAH_SPEECH_FORCE
    """
    layer_id: str
    placement_name: str
    placement_phase: str
    shared_cause: str
    origin_output_type: str
    branch_output_type: str
    is_terminal: bool = False

    def __post_init__(self) -> None:
        if not self.layer_id:
            raise ValueError("WadContract.layer_id is required")
        if not self.shared_cause:
            raise ValueError(
                "WadContract.shared_cause is required — لا مقايسة بلا علة جامعة"
            )

    @classmethod
    def from_layer_entry(cls, entry) -> WadContract:
        """Build from a registry.LayerEntry."""
        return cls(
            layer_id=entry.id,
            placement_name=entry.name,
            placement_phase=entry.phase,
            shared_cause=entry.shared_cause,
            origin_output_type=entry.origin_output_type,
            branch_output_type=entry.branch_output_type,
            is_terminal=entry.is_terminal,
        )


# ── السبب — SababEvidence ─────────────────────────────────────────────────────

@dataclass(frozen=True)
class SababEvidence:
    """
    السبب — the opening cause / trigger evidence for a stage transition.

    This is the Hokom-owned evidence (morphological facts from Arabic text)
    that triggers the stage. Taaqol licenses the transition; Hokom provides
    the cause.

    Fields:
        layer_id        — stage this evidence targets
        evidence        — EvidenceSet from Hokom pipeline
        trigger_rule    — the specific rule/condition that fired
        is_present      — True if the cause is actually present
    """
    layer_id: str
    evidence: EvidenceSet
    trigger_rule: str
    is_present: bool

    def __post_init__(self) -> None:
        if not self.layer_id:
            raise ValueError("SababEvidence.layer_id is required")
        if not self.trigger_rule:
            raise ValueError("SababEvidence.trigger_rule is required")


# ── الشرط — ShartRequirement ──────────────────────────────────────────────────

@dataclass(frozen=True)
class ShartRequirement:
    """
    الشرط — a condition that must hold for the stage transition to be valid.

    Conditions come from Saleh's LayerSpec.conditions. Each condition is
    checked against the Hokom-produced EvidenceSet.

    Fields:
        condition_id    — Saleh condition string (e.g. "raw_input_not_empty")
        layer_id        — stage this condition guards
        is_satisfied    — True if the condition holds for this input
        evidence_keys   — which EvidenceAtom keys satisfy / fail this condition
    """
    condition_id: str
    layer_id: str
    is_satisfied: bool
    evidence_keys: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.condition_id:
            raise ValueError("ShartRequirement.condition_id is required")


# ── المانع — ManiBlocker ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class ManiBlocker:
    """
    المانع — a blocker that prevents the stage transition.

    Blockers come from Saleh's LayerSpec.blockers. If any blocker fires,
    the stage outputs CandidateStatus.BLOCKED with a Residual.

    Fields:
        blocker_id      — Saleh blocker string (e.g. "encoding_error")
        layer_id        — stage this blocker guards
        is_active       — True if this blocker has fired
        severity        — ResidualSeverity (INFO/WARNING/BLOCKER)
        detail          — human-readable explanation
    """
    blocker_id: str
    layer_id: str
    is_active: bool
    severity: ResidualSeverity = ResidualSeverity.BLOCKER
    detail: str = ""

    def to_residual(self, residual_id: str) -> Residual:
        """Convert an active blocker to a Residual."""
        return Residual(
            residual_id=residual_id,
            stage_id=self.layer_id,
            reason_code=self.blocker_id,
            severity=self.severity,
            detail=self.detail or f"Blocker '{self.blocker_id}' fired at {self.layer_id}",
            carries_forward=True,
        )


# ── العلة — IllahRationale ────────────────────────────────────────────────────

@dataclass(frozen=True)
class IllahRationale:
    """
    العلة — the shared rationale / qiyas reason that licenses the analogy.

    In Saleh terms: shared_cause. In Taaqol terms: the basis for the
    granted_rank assignment by TransitionGate.

    Fields:
        layer_id        — stage being evaluated
        rationale       — Saleh LayerSpec.shared_cause (Arabic text)
        taaqol_gate_id  — Taaqol TransitionGate identifier
        granted_rank    — Taaqol granted_rank (0-6)
    """
    layer_id: str
    rationale: str
    taaqol_gate_id: str
    granted_rank: int

    def __post_init__(self) -> None:
        if not (0 <= self.granted_rank <= 6):
            raise ValueError(
                f"IllahRationale.granted_rank must be in [0,6], "
                f"got {self.granted_rank}"
            )


# ── القادح — QadihDefect ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class QadihDefect:
    """
    القادح — a defect that may invalidate or corrupt the qiyas.

    A BLOCKER-severity defect → BATIL (null judgment).
    A WARNING-severity defect → FASID (corrupt but non-null).
    No defects → clean path to SAHIH.

    Fields:
        defect_id       — identifier (e.g. "root_consonant_count_underspecified")
        layer_id        — stage where defect was detected
        is_active       — True if this defect actually applies
        severity        — ResidualSeverity
        invalidating    — True → forces BATIL; False → FASID only
        detail          — explanation
    """
    defect_id: str
    layer_id: str
    is_active: bool
    severity: ResidualSeverity
    invalidating: bool
    detail: str = ""


# ── الأثر — AtharEffect ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class AtharEffect:
    """
    الأثر — the licensed effect produced by a SAHIH constitutional judgment.

    This is the output type produced by the stage when all conditions are
    satisfied and Taaqol licenses the transition.

    Fields:
        layer_id        — stage that produced this effect
        effect_type     — Saleh branch_output_type (e.g. "RootStemCandidate")
        candidate_id    — CanonicalCandidate.candidate_id
        taaqol_rank     — final granted_rank from Taaqol
        carry_to_next   — which layer ID this effect flows to
    """
    layer_id: str
    effect_type: str
    candidate_id: str
    taaqol_rank: int
    carry_to_next: str | None = None   # None for P12 (TERMINAL)


# ── البقايا — BaqayaResidual ──────────────────────────────────────────────────

@dataclass(frozen=True)
class BaqayaResidual:
    """
    البقايا — residuals carried forward after a DEFERRED or partial judgment.

    Wraps Hokom's Residual type with constitutional context.

    Fields:
        layer_id        — stage that generated this residual
        residual        — underlying Residual
        constitutional_status — DEFERRED / RESIDUAL / FASID
        retry_at_layer  — which layer ID should retry this evidence
    """
    layer_id: str
    residual: Residual
    constitutional_status: ConstitutionalStatus
    retry_at_layer: str | None = None


# ── ConstitutionalJudgment ────────────────────────────────────────────────────

@dataclass(frozen=True)
class ConstitutionalJudgment:
    """
    The complete constitutional evaluation output for one stage.

    Captures the full jurisprudential chain:
        الوضع → السبب → الشرط → المانع → العلة → القادح
        → status → الأثر / البقايا

    This is the canonical inter-stage representation (Slot Algebra Engineering
    mandate: typed inter-stage representation that carries provenance through
    all 19 stages).
    """
    layer_id: str
    wad: WadContract
    sabab: SababEvidence
    shurut: tuple[ShartRequirement, ...]    # شروط
    mawani: tuple[ManiBlocker, ...]         # موانع
    illah: IllahRationale
    qawadih: tuple[QadihDefect, ...]        # قوادح
    status: ConstitutionalStatus
    athar: AtharEffect | None               # produced if SAHIH
    baqaya: tuple[BaqayaResidual, ...]      # produced if DEFERRED/FASID

    def __post_init__(self) -> None:
        # SAHIH requires an AtharEffect
        if self.status is ConstitutionalStatus.SAHIH and self.athar is None:
            raise ValueError(
                f"ConstitutionalJudgment at {self.layer_id}: "
                "SAHIH judgment must have an AtharEffect"
            )
        # BATIL must NOT have an AtharEffect
        if self.status is ConstitutionalStatus.BATIL and self.athar is not None:
            raise ValueError(
                f"ConstitutionalJudgment at {self.layer_id}: "
                "BATIL judgment must NOT have an AtharEffect"
            )
        # P12 terminal: athar.carry_to_next must be None
        if (
            self.athar is not None
            and self.wad.is_terminal
            and self.athar.carry_to_next is not None
        ):
            raise ValueError(
                f"Terminal layer {self.layer_id}: "
                "AtharEffect.carry_to_next must be None (no P13)"
            )
