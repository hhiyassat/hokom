from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class IfadahVerdict(str, Enum):
    IFADAH_APPROVED = "IFADAH_APPROVED"
    IFADAH_DEFERRED = "IFADAH_DEFERRED"
    IFADAH_BLOCKED = "IFADAH_BLOCKED"

class HukmVerdict(str, Enum):
    HUKM_APPROVED = "HUKM_APPROVED"
    HUKM_DEFERRED = "HUKM_DEFERRED"
    HUKM_BLOCKED = "HUKM_BLOCKED"
    HUKM_INVALID = "HUKM_INVALID"

class ManatVerdict(str, Enum):
    MANAT_APPROVED = "MANAT_APPROVED"
    MANAT_DEFERRED = "MANAT_DEFERRED"
    MANAT_BLOCKED = "MANAT_BLOCKED"

class TanzilVerdict(str, Enum):
    TANZIL_APPROVED = "TANZIL_APPROVED"
    TANZIL_DEFERRED = "TANZIL_DEFERRED"
    TANZIL_BLOCKED = "TANZIL_BLOCKED"

class AnswerAuditVerdict(str, Enum):
    ANSWER_AUDIT_APPROVED = "ANSWER_AUDIT_APPROVED"
    ANSWER_AUDIT_DEFERRED = "ANSWER_AUDIT_DEFERRED"
    ANSWER_AUDIT_BLOCKED = "ANSWER_AUDIT_BLOCKED"
    ANSWER_AUDIT_INVALID = "ANSWER_AUDIT_INVALID"

@dataclass(frozen=True)
class IfadahCandidate:
    """
    Ifadah (informativeness) candidate.
    NEVER opened from a single token.
    NEVER from grammatical appearance alone.
    Requires: licensed relation OR clause closure + licensed parties.
    """
    ifadah_id: str
    clause_id: str
    relation_refs: tuple[str, ...]    # relation IDs that ground this
    proposition_shape: str             # structural shape only (e.g., "V+Agent+Object")
    evidence_ids: tuple[str, ...]
    active_residuals: tuple[str, ...]
    closure_state: str                 # from RelationClosureState
    rank: int                          # Taaqol rank (0-6)
    verdict: IfadahVerdict
    stop_reason: Optional[str]

@dataclass(frozen=True)
class HukmCandidate:
    """
    Hukm carrier — constitutional carrier in Taaqol, NOT a fiqh ruling.
    NEVER opened without a licensed Ifadah.
    NEVER a fatwa, religious judgment, or legal opinion.
    """
    hukm_id: str
    ifadah_id: str                     # must reference a licensed IfadahCandidate
    subject_ref: str
    predicate_ref: str
    relation_ref: str
    polarity: str                      # POSITIVE | NEGATIVE
    modality: str                      # IMPERATIVE | DECLARATIVE | CONDITIONAL | ...
    temporal_scope: Optional[str]
    condition_scope: Optional[str]
    evidence_ids: tuple[str, ...]
    residuals: tuple[str, ...]
    rank: int
    verdict: HukmVerdict
    stop_reason: Optional[str]
    # CONSTITUTIONAL NOTE: This is a linguistic/structural carrier, not a fatwa.
    constitutional_note: str = "LINGUISTIC_STRUCTURAL_CARRIER_NOT_FIQH_RULING"

@dataclass(frozen=True)
class ManatCandidate:
    """Manat candidate — requires contract in Taaqol + sufficient evidence."""
    manat_id: str
    hukm_id: str
    linked_description: str
    condition_description: str
    scope: str
    evidence_ids: tuple[str, ...]
    contradictions: tuple[str, ...]
    residuals: tuple[str, ...]
    verdict: ManatVerdict

@dataclass(frozen=True)
class TanzilCandidate:
    """Tanzil (application) candidate. Requires: Hukm + Manat + target instance + applicability."""
    tanzil_id: str
    hukm_id: str
    manat_id: str
    target_instance: str
    applicability_evidence: tuple[str, ...]
    blocking_contradictions: tuple[str, ...]
    residuals: tuple[str, ...]
    verdict: TanzilVerdict

@dataclass
class AnswerAuditResult:
    """
    AnswerAudit — final endpoint of the chain.
    NOT a free answer generator.
    Audits: provenance, continuity, forbidden leaps, residuals, scope, overclaim.
    """
    audit_id: str
    claim_provenance_verified: bool
    evidence_continuity_verified: bool
    stage_continuity_verified: bool
    forbidden_leaps: list[str]
    unresolved_residuals: list[str]
    rank_ceiling: int
    scope_mismatch: bool
    unsupported_certainty: bool
    wording_overclaim: bool
    linguistic_vs_religious_distinction_clear: bool
    verdict: AnswerAuditVerdict
    stop_reason: Optional[str]
    trace_ids: tuple[str, ...]
