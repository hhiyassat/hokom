"""
hokom.canonical.slot_algebra — Slot Algebra Engineering typed core types.

All types here align with the Saleh/Qiyas Candidate/CandidateSet contracts
and the Taaqol EvidenceContract / RankLattice interfaces.

Public API:
    SlotId, SlotState, SlotVector, SlotDelta
    EvidenceAtom, EvidenceSet, ProvenanceRef
    CanonicalCandidate, CanonicalCandidateSet
    Residual, ResidualSeverity
    claim_key(...)  → str
"""
from .types import (
    SlotState,
    EvidenceAtom,
    EvidenceSet,
    ProvenanceRef,
    Residual,
    ResidualSeverity,
    CanonicalCandidate,
    CanonicalCandidateSet,
    CandidateStatus,
)
from .claim_key import claim_key, evaluation_id

__all__ = [
    "SlotState",
    "EvidenceAtom",
    "EvidenceSet",
    "ProvenanceRef",
    "Residual",
    "ResidualSeverity",
    "CanonicalCandidate",
    "CanonicalCandidateSet",
    "CandidateStatus",
    "claim_key",
    "evaluation_id",
]
