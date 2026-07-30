"""
p1.py — Stage adapters for SCG-P1: Dal Alone Atomic (الدال وحده ذريًا)

Five adapters:
    LetterIdentityAdapter         → P1_LETTER_IDENTITY_CARRIER
    HarakaMarkAdapter             → P1_HARAKA_MARK_IDENTITY_CARRIER
    ConditionedSequenceAdapter    → P1_CONDITIONED_TYPED_SEQUENCE
    PositionAdapter               → P1_POSITION_CARRIER
    SlotAdapter                   → P1_SLOT_CANDIDATE

Hokom evidence owner: src/pipeline/p1_atomic_structure/
Saleh contract: SCG-P1 layer specs in master_registry_seed.py
"""
from __future__ import annotations

from ..constitutional.contracts import (
    ConstitutionalStatus,
    ManiBlocker,
    QadihDefect,
    ShartRequirement,
)
from ..slot_algebra.types import (
    CanonicalCandidate,
    EvidenceAtom,
    EvidenceSet,
    ProvenanceRef,
    ResidualSeverity,
)
from .base import StageAdapter, StageInput


def _p1_prov(rule_id: str, layer_id: str) -> ProvenanceRef:
    return ProvenanceRef(
        owner="hokom",
        module_path="hokom.pipeline.p1_atomic_structure",
        rule_id=rule_id,
        stage_id=layer_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# P1_LETTER_IDENTITY_CARRIER
# ─────────────────────────────────────────────────────────────────────────────

class LetterIdentityAdapter(StageAdapter):
    """
    P1_LETTER_IDENTITY_CARRIER — identifies Arabic letter identity carriers.

    Saleh conditions: glyph_candidates_present
    Saleh blockers:   ambiguous_letter_identity

    Evidence keys (hokom_evidence):
        "letters": list[dict] with keys position, char, carrier_function
    """

    LAYER_ID = "P1_LETTER_IDENTITY_CARRIER"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _p1_prov("letter_identity_identification", self.LAYER_ID)
        letters = input.hokom_evidence.get("letters", [])
        atoms: list[EvidenceAtom] = []
        for letter in letters:
            cf = letter.get("carrier_function", "unknown")
            atoms.append(EvidenceAtom(
                key=f"letter_identity:{letter.get('position', 0)}",
                value=cf,
                confidence=0.95 if cf not in (None, "unknown", "unknown_carrier_function") else 0.3,
                provenance=prov,
            ))
        if not atoms:
            atoms.append(EvidenceAtom(
                key="glyph_candidates_present",
                value=bool(input.prior_output and input.prior_output.accepted),
                confidence=1.0 if input.prior_output and input.prior_output.accepted else 0.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        return (ShartRequirement(
            condition_id="glyph_candidates_present",
            layer_id=self.LAYER_ID,
            is_satisfied=bool(input.prior_output and input.prior_output.accepted),
            evidence_keys=("glyph_candidates_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        letters = input.hokom_evidence.get("letters", [])
        ambiguous = any(
            l.get("carrier_function") in ("unknown", "unknown_carrier_function")
            for l in letters
        )
        return (ManiBlocker(
            blocker_id="ambiguous_letter_identity",
            layer_id=self.LAYER_ID,
            is_active=ambiguous,
            severity=ResidualSeverity.WARNING,
            detail="One or more letters have ambiguous carrier function",
        ),)

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="LetterIdentityCarrier",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="letter_identity_identification",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P1_HARAKA_MARK_IDENTITY_CARRIER"


# ─────────────────────────────────────────────────────────────────────────────
# P1_HARAKA_MARK_IDENTITY_CARRIER
# ─────────────────────────────────────────────────────────────────────────────

class HarakaMarkAdapter(StageAdapter):
    """
    P1_HARAKA_MARK_IDENTITY_CARRIER — identifies Arabic diacritical mark identities.

    Evidence keys:
        "harakat": list[dict] with position, mark_function, diacritic_kind
    """

    LAYER_ID = "P1_HARAKA_MARK_IDENTITY_CARRIER"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _p1_prov("haraka_mark_identification", self.LAYER_ID)
        harakat = input.hokom_evidence.get("harakat", [])
        atoms: list[EvidenceAtom] = []
        for h in harakat:
            mf = h.get("mark_function", "unknown")
            atoms.append(EvidenceAtom(
                key=f"haraka_mark:{h.get('position', 0)}",
                value=mf,
                confidence=0.9 if mf not in (None, "unknown", "unknown_mark_function") else 0.4,
                provenance=prov,
            ))
        if not atoms:
            # No harakat is valid (unvoweled text): produce a zero-harakat evidence
            atoms.append(EvidenceAtom(
                key="haraka_mark_scan_complete",
                value=True,
                confidence=1.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        return (ShartRequirement(
            condition_id="letter_identities_present",
            layer_id=self.LAYER_ID,
            is_satisfied=bool(input.prior_output and input.prior_output.accepted),
            evidence_keys=("letter_identities_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        harakat = input.hokom_evidence.get("harakat", [])
        contradictory = any(h.get("mark_function") == "error" for h in harakat)
        return (ManiBlocker(
            blocker_id="contradictory_haraka_assignment",
            layer_id=self.LAYER_ID,
            is_active=contradictory,
            severity=ResidualSeverity.BLOCKER,
            detail="Contradictory haraka mark detected",
        ),)

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="HarakaMarkIdentityCarrier",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="haraka_mark_identification",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P1_CONDITIONED_TYPED_SEQUENCE"


# ─────────────────────────────────────────────────────────────────────────────
# P1_CONDITIONED_TYPED_SEQUENCE
# ─────────────────────────────────────────────────────────────────────────────

class ConditionedSequenceAdapter(StageAdapter):
    """
    P1_CONDITIONED_TYPED_SEQUENCE — builds conditioned typed sequences.

    Groups letter+haraka pairs into typed phonological sequences.
    Evidence keys: "sequences": list[dict] with position, sequence_type, chars
    """

    LAYER_ID = "P1_CONDITIONED_TYPED_SEQUENCE"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _p1_prov("conditioned_sequence_construction", self.LAYER_ID)
        seqs = input.hokom_evidence.get("sequences", [])
        atoms: list[EvidenceAtom] = []
        for s in seqs:
            st = s.get("sequence_type", "unknown")
            atoms.append(EvidenceAtom(
                key=f"sequence:{s.get('position', 0)}",
                value=st,
                confidence=0.9 if st != "unknown" else 0.5,
                provenance=prov,
            ))
        if not atoms:
            atoms.append(EvidenceAtom(
                key="identities_present",
                value=bool(input.prior_output and input.prior_output.accepted),
                confidence=1.0 if input.prior_output and input.prior_output.accepted else 0.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        return (ShartRequirement(
            condition_id="identities_present",
            layer_id=self.LAYER_ID,
            is_satisfied=bool(input.prior_output and input.prior_output.accepted),
            evidence_keys=("identities_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        seqs = input.hokom_evidence.get("sequences", [])
        conflict = any(s.get("sequence_type") == "conflict" for s in seqs)
        return (ManiBlocker(
            blocker_id="sequence_conditioning_conflict",
            layer_id=self.LAYER_ID,
            is_active=conflict,
            severity=ResidualSeverity.BLOCKER,
            detail="Sequence conditioning conflict detected",
        ),)

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="ConditionedTypedSequence",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="conditioned_sequence_construction",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P1_POSITION_CARRIER"


# ─────────────────────────────────────────────────────────────────────────────
# P1_POSITION_CARRIER
# ─────────────────────────────────────────────────────────────────────────────

class PositionAdapter(StageAdapter):
    """
    P1_POSITION_CARRIER — assigns ordered positions to conditioned sequences.

    Evidence keys: "positions": list[dict] with index, sequence_ref
    """

    LAYER_ID = "P1_POSITION_CARRIER"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _p1_prov("position_assignment", self.LAYER_ID)
        positions = input.hokom_evidence.get("positions", [])
        atoms: list[EvidenceAtom] = []
        for p in positions:
            atoms.append(EvidenceAtom(
                key=f"position:{p.get('index', 0)}",
                value=p.get("sequence_ref", ""),
                confidence=0.95 if p.get("sequence_ref") else 0.0,
                provenance=prov,
            ))
        if not atoms:
            atoms.append(EvidenceAtom(
                key="sequences_present",
                value=bool(input.prior_output and input.prior_output.accepted),
                confidence=1.0 if input.prior_output and input.prior_output.accepted else 0.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        return (ShartRequirement(
            condition_id="sequences_present",
            layer_id=self.LAYER_ID,
            is_satisfied=bool(input.prior_output and input.prior_output.accepted),
            evidence_keys=("sequences_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        positions = input.hokom_evidence.get("positions", [])
        duplicate = len(positions) != len({p.get("index") for p in positions})
        return (ManiBlocker(
            blocker_id="duplicate_position_assignment",
            layer_id=self.LAYER_ID,
            is_active=duplicate,
            severity=ResidualSeverity.BLOCKER,
            detail="Duplicate position indices detected",
        ),)

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="PositionCarrier",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="position_assignment",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P1_SLOT_CANDIDATE"


# ─────────────────────────────────────────────────────────────────────────────
# P1_SLOT_CANDIDATE
# ─────────────────────────────────────────────────────────────────────────────

class SlotCandidateAdapter(StageAdapter):
    """
    P1_SLOT_CANDIDATE — produces the initial slot geometry candidate.

    This is the first slot in Hokom's SGA SlotId model. Uses
    pipeline/p1_atomic_structure/slot_engineering.py evidence.

    Evidence keys: "slots": list[dict] with slot_id, state, host_ref
    """

    LAYER_ID = "P1_SLOT_CANDIDATE"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _p1_prov("slot_candidate_construction", self.LAYER_ID)
        slots = input.hokom_evidence.get("slots", [])
        atoms: list[EvidenceAtom] = []
        for s in slots:
            sid = s.get("slot_id", "unknown")
            atoms.append(EvidenceAtom(
                key=f"slot:{sid}",
                value=s.get("state", "unknown"),
                confidence=0.9 if s.get("state") not in (None, "unknown") else 0.3,
                provenance=prov,
            ))
        if not atoms:
            atoms.append(EvidenceAtom(
                key="positions_present",
                value=bool(input.prior_output and input.prior_output.accepted),
                confidence=1.0 if input.prior_output and input.prior_output.accepted else 0.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        return (ShartRequirement(
            condition_id="positions_present",
            layer_id=self.LAYER_ID,
            is_satisfied=bool(input.prior_output and input.prior_output.accepted),
            evidence_keys=("positions_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        slots = input.hokom_evidence.get("slots", [])
        missing_host = any(not s.get("host_ref") for s in slots)
        return (ManiBlocker(
            blocker_id="slot_missing_host",
            layer_id=self.LAYER_ID,
            is_active=missing_host and bool(slots),
            severity=ResidualSeverity.WARNING,
            detail="One or more slots missing host reference",
        ),)

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="SlotCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="slot_candidate_construction",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P2_REGISTRY_PROJECTION"
