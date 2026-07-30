"""
p9_p12.py — Stage adapters for SCG-P9 through P12 (sentence-level stages).

    P9_SENTENCE_GEOMETRY    — hندسة الجملة: requires ≥2 distinct P8 units
    P10_RELATION_GEOMETRY   — hندسة العلاقة: grammatical relations
    P11_IRAB_GEOMETRY       — hندسة الإعراب: case/mood geometry (candidates only)
    P12_IFADAH_SPEECH_FORCE — قوة الإفادة الكلامية: TERMINAL (no P13)

CRITICAL:
    P9 DEFER condition: < 2 distinct AmilMamulCandidate units
    P12 is TERMINAL: target_boundary_opens=(), no P13, no HukmCandidate

Input for sentence-level stages:
    StageInput.hokom_evidence["amil_mamul_units"]: list[dict]
        Each: {unit_id, word_index, role, candidate_id}
    StageInput.word_index = None (sentence-level, not word-level)
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


def _prov(rule: str, layer_id: str) -> ProvenanceRef:
    return ProvenanceRef(
        owner="hokom",
        module_path="hokom.canonical.stages.sentence",
        rule_id=rule,
        stage_id=layer_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# P9_SENTENCE_GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────

class SentenceGeometryAdapter(StageAdapter):
    """
    P9_SENTENCE_GEOMETRY — builds sentence geometry from ≥2 P8 units.

    Saleh adapter rules (from sentence_geometry_adapter.py):
        ACCEPT if ≥2 distinct AmilMamulCandidate units present AND
                   adjacency relation can be established
        DEFER  if < 2 distinct units (single word — needs more input)
        DEFER  if adjacency_underspecified (units present but relation unclear)
        BLOCK  if sentence_boundary_conflict

    This is the first multi-unit / sentence-level stage.

    Evidence keys:
        "amil_mamul_units": list[dict]
            {unit_id, word_index, role, candidate_id}
        "adjacency_relation": str — "established" | "underspecified" | "conflict"
        "sentence_boundary":  str — "closed" | "open" | "conflict"
    """

    LAYER_ID = "P9_SENTENCE_GEOMETRY"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("sentence_geometry_construction", self.LAYER_ID)
        units = input.hokom_evidence.get("amil_mamul_units", [])
        adjacency = input.hokom_evidence.get("adjacency_relation", "underspecified")
        boundary = input.hokom_evidence.get("sentence_boundary", "open")
        unit_count = len(units)

        atoms = [
            EvidenceAtom(
                key="amil_mamul_unit_count",
                value=unit_count,
                confidence=1.0 if unit_count >= 2 else (0.5 if unit_count == 1 else 0.0),
                provenance=prov,
            ),
            EvidenceAtom(
                key="adjacency_relation",
                value=adjacency,
                confidence=0.9 if adjacency == "established" else
                           (0.4 if adjacency == "underspecified" else 0.0),
                provenance=prov,
            ),
            EvidenceAtom(
                key="sentence_boundary",
                value=boundary,
                confidence=0.85 if boundary in ("closed", "open") else 0.0,
                provenance=prov,
            ),
        ]
        # Add per-unit evidence
        for u in units[:4]:  # cap at 4 atoms for evidence set
            atoms.append(EvidenceAtom(
                key=f"unit:{u.get('unit_id', '?')}",
                value=u.get("role", "unknown"),
                confidence=0.9 if u.get("role") in ("amil", "mamul", "both") else 0.3,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        units = input.hokom_evidence.get("amil_mamul_units", [])
        unit_count = len(units)
        adjacency = input.hokom_evidence.get("adjacency_relation", "underspecified")
        return (
            ShartRequirement(
                condition_id="amil_mamul_unit_count_gte_2",
                layer_id=self.LAYER_ID,
                is_satisfied=(unit_count >= 2),
                evidence_keys=("amil_mamul_unit_count",),
            ),
            ShartRequirement(
                condition_id="adjacency_relation_not_conflict",
                layer_id=self.LAYER_ID,
                is_satisfied=(adjacency != "conflict"),
                evidence_keys=("adjacency_relation",),
            ),
        )

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        units = input.hokom_evidence.get("amil_mamul_units", [])
        adjacency = input.hokom_evidence.get("adjacency_relation", "underspecified")
        boundary = input.hokom_evidence.get("sentence_boundary", "open")
        unit_count = len(units)
        return (
            ManiBlocker(
                blocker_id="sentence_boundary_conflict",
                layer_id=self.LAYER_ID,
                is_active=(boundary == "conflict"),
                severity=ResidualSeverity.BLOCKER,
                detail="Sentence boundary conflict detected",
            ),
            ManiBlocker(
                blocker_id="adjacency_underspecified",
                layer_id=self.LAYER_ID,
                is_active=(adjacency == "underspecified" and unit_count >= 2),
                severity=ResidualSeverity.WARNING,
                detail=(
                    f"Adjacency underspecified with {unit_count} units — "
                    "sentence geometry deferred"
                ),
            ),
            ManiBlocker(
                blocker_id="insufficient_units",
                layer_id=self.LAYER_ID,
                is_active=(unit_count < 2),
                severity=ResidualSeverity.WARNING,
                detail=(
                    f"Only {unit_count} amil/mamul unit(s) — "
                    "sentence geometry requires ≥2; deferring"
                ),
            ),
        )

    def _determine_status(self, shurut, mawani, qawadih, granted_rank):
        # sentence_boundary_conflict → BATIL
        for m in mawani:
            if m.blocker_id == "sentence_boundary_conflict" and m.is_active:
                return ConstitutionalStatus.BATIL
        # < 2 units OR adjacency underspecified → DEFERRED
        for m in mawani:
            if m.blocker_id in ("insufficient_units", "adjacency_underspecified") and m.is_active:
                return ConstitutionalStatus.DEFERRED
        # Unsatisfied conditions → DEFERRED
        if any(not s.is_satisfied for s in shurut):
            return ConstitutionalStatus.DEFERRED
        if granted_rank < 4:
            return ConstitutionalStatus.DEFERRED
        return ConstitutionalStatus.SAHIH

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="SentenceGeometryCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="sentence_geometry_construction",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P10_RELATION_GEOMETRY"


# ─────────────────────────────────────────────────────────────────────────────
# P10_RELATION_GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────

class RelationGeometryAdapter(StageAdapter):
    """
    P10_RELATION_GEOMETRY — maps sentence geometry to grammatical relations.

    Saleh adapter rules (from relation_geometry_adapter.py):
        ACCEPT if ≥1 grammatical relation candidate derived from P9
        DEFER  if relation_underspecified (P9 deferred)
        BLOCK  if relation_conflict

    Evidence keys:
        "relations": list[dict] — {relation_type, amil_unit_id, mamul_unit_id}
        "relation_confidence": float
    """

    LAYER_ID = "P10_RELATION_GEOMETRY"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("relation_geometry_construction", self.LAYER_ID)
        relations = input.hokom_evidence.get("relations", [])
        conf = float(input.hokom_evidence.get("relation_confidence", 0.7))
        atoms = [EvidenceAtom(
            key="relation_count",
            value=len(relations),
            confidence=conf if relations else 0.0,
            provenance=prov,
        )]
        for r in relations[:3]:
            atoms.append(EvidenceAtom(
                key=f"relation:{r.get('relation_type', '?')}",
                value=f"{r.get('amil_unit_id')}→{r.get('mamul_unit_id')}",
                confidence=conf,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (ShartRequirement(
            condition_id="sentence_geometry_present",
            layer_id=self.LAYER_ID,
            is_satisfied=prior_ok,
            evidence_keys=("sentence_geometry_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        relations = input.hokom_evidence.get("relations", [])
        conflict = any(r.get("relation_type") == "conflict" for r in relations)
        underspecified = (not relations)
        return (
            ManiBlocker(
                blocker_id="relation_conflict",
                layer_id=self.LAYER_ID,
                is_active=conflict,
                severity=ResidualSeverity.BLOCKER,
                detail="Grammatical relation conflict detected",
            ),
            ManiBlocker(
                blocker_id="relation_underspecified",
                layer_id=self.LAYER_ID,
                is_active=underspecified and not conflict,
                severity=ResidualSeverity.WARNING,
                detail="No grammatical relations derived — P9 likely deferred",
            ),
        )

    def _determine_status(self, shurut, mawani, qawadih, granted_rank):
        # relation_conflict → BATIL
        for m in mawani:
            if m.blocker_id == "relation_conflict" and m.is_active:
                return ConstitutionalStatus.BATIL
        # relation_underspecified → DEFERRED (upstream P9 not yet producing relations)
        for m in mawani:
            if m.blocker_id == "relation_underspecified" and m.is_active:
                return ConstitutionalStatus.DEFERRED
        # Unsatisfied conditions → DEFERRED
        if any(not s.is_satisfied for s in shurut):
            return ConstitutionalStatus.DEFERRED
        if granted_rank < 4:
            return ConstitutionalStatus.DEFERRED
        return ConstitutionalStatus.SAHIH

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="RelationGeometryCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="relation_geometry_construction",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P11_IRAB_GEOMETRY"


# ─────────────────────────────────────────────────────────────────────────────
# P11_IRAB_GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────

class IrabGeometryAdapter(StageAdapter):
    """
    P11_IRAB_GEOMETRY — maps grammatical relations to irab (case/mood) possibilities.

    CRITICAL: Irab is candidate-only. P11 does NOT produce a final case judgment.
    It draws irab positions as possibilities (مواضع إعرابية كإمكانات).

    Saleh adapter rules (from irab_geometry_adapter.py):
        ACCEPT if ≥1 irab position candidate derived from P10 relations
        DEFER  if irab_underspecified (P10 deferred)
        BLOCK  if irab_conflict (contradictory position signals)

    Forbidden outputs (ABSOLUTE): HukmCandidate, RealityClaim, FinalMeaning
    Also forbidden: IfadahCandidate (produced only by P12)

    Evidence keys:
        "irab_positions": list[dict] — {word_id, possible_cases: list[str]}
        "irab_confidence": float
    """

    LAYER_ID = "P11_IRAB_GEOMETRY"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("irab_geometry_construction", self.LAYER_ID)
        positions = input.hokom_evidence.get("irab_positions", [])
        conf = float(input.hokom_evidence.get("irab_confidence", 0.75))
        atoms = [EvidenceAtom(
            key="irab_position_count",
            value=len(positions),
            confidence=conf if positions else 0.0,
            provenance=prov,
        )]
        for p in positions[:4]:
            cases = p.get("possible_cases", [])
            atoms.append(EvidenceAtom(
                key=f"irab_pos:{p.get('word_id', '?')}",
                value=tuple(cases),
                confidence=conf if cases else 0.2,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (ShartRequirement(
            condition_id="relation_geometry_present",
            layer_id=self.LAYER_ID,
            is_satisfied=prior_ok,
            evidence_keys=("relation_geometry_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        positions = input.hokom_evidence.get("irab_positions", [])
        conflict = any("conflict" in str(p.get("possible_cases", [])) for p in positions)
        underspecified = not positions
        return (
            ManiBlocker(
                blocker_id="irab_conflict",
                layer_id=self.LAYER_ID,
                is_active=conflict,
                severity=ResidualSeverity.BLOCKER,
                detail="Contradictory irab position signals detected",
            ),
            ManiBlocker(
                blocker_id="irab_underspecified",
                layer_id=self.LAYER_ID,
                is_active=underspecified and not conflict,
                severity=ResidualSeverity.WARNING,
                detail="No irab positions derived — P10 likely deferred",
            ),
        )

    def _check_defects(self, input: StageInput, evidence: EvidenceSet):
        positions = input.hokom_evidence.get("irab_positions", [])
        # Multiple case possibilities per word is not a defect — it's expected
        # A defect is if a position has 0 possible cases
        zero_case_positions = [
            p for p in positions if not p.get("possible_cases")
        ]
        return (QadihDefect(
            defect_id="irab_position_zero_cases",
            layer_id=self.LAYER_ID,
            is_active=bool(zero_case_positions),
            severity=ResidualSeverity.WARNING,
            invalidating=False,
            detail=(
                f"{len(zero_case_positions)} irab position(s) have no case "
                "candidates — irab geometry partial"
            ),
        ),)

    def _determine_status(self, shurut, mawani, qawadih, granted_rank):
        # irab_conflict → BATIL
        for m in mawani:
            if m.blocker_id == "irab_conflict" and m.is_active:
                return ConstitutionalStatus.BATIL
        # irab_underspecified → DEFERRED (upstream P10 not yet producing irab positions)
        for m in mawani:
            if m.blocker_id == "irab_underspecified" and m.is_active:
                return ConstitutionalStatus.DEFERRED
        # Non-invalidating defects → FASID (irab_position_zero_cases)
        for defect in qawadih:
            if defect.is_active and not defect.invalidating:
                return ConstitutionalStatus.FASID
        # Unsatisfied conditions → DEFERRED
        if any(not s.is_satisfied for s in shurut):
            return ConstitutionalStatus.DEFERRED
        if granted_rank < 4:
            return ConstitutionalStatus.DEFERRED
        return ConstitutionalStatus.SAHIH

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        # Enforce: NO IfadahCandidate, NO HukmCandidate, NO RealityClaim
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="IrabGeometryCandidate",   # NOT IfadahCandidate
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="irab_geometry_construction",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
            # output_flags must NOT contain IfadahCandidate
            output_flags=frozenset({"irab_geometry_candidate"}),
        )

    def _next_layer_id(self): return "P12_IFADAH_SPEECH_FORCE"


# ─────────────────────────────────────────────────────────────────────────────
# P12_IFADAH_SPEECH_FORCE — TERMINAL
# ─────────────────────────────────────────────────────────────────────────────

class IfadahAdapter(StageAdapter):
    """
    P12_IFADAH_SPEECH_FORCE — speech-force candidate from irab geometry.

    TERMINAL: target_boundary_opens = ()
              No P13. No HukmCandidate. No RealityClaim. No FinalMeaning.
              No FinalCaseJudgment. No truth value. No final interpretation.

    P12 produces IfadahSpeechForceCandidate — a CANDIDATE-ONLY speech force
    (khabar/insha'/talab) — not a completed speech act judgment.

    Saleh adapter rules (from ifadah_adapter.py):
        ACCEPT if ≥1 irab geometry candidate satisfies ifadah conditions
        DEFER  if irab_underspecified (P11 deferred or partial)
        BLOCK  if ifadah_conflict (contradictory speech force signals)

    Evidence keys:
        "speech_force":     str — "khabar" | "insha" | "talab" | "unknown"
        "ifadah_basis":     str — what irab geometry element licenses the force
        "force_confidence": float
    """

    LAYER_ID = "P12_IFADAH_SPEECH_FORCE"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("ifadah_speech_force_construction", self.LAYER_ID)
        force = input.hokom_evidence.get("speech_force", "unknown")
        basis = input.hokom_evidence.get("ifadah_basis", "")
        conf = float(input.hokom_evidence.get("force_confidence", 0.7))

        force_conf = {
            "khabar": conf,
            "insha": conf,
            "talab": conf,
            "unknown": 0.2,
        }
        atoms = [
            EvidenceAtom(
                key="speech_force",
                value=force,
                confidence=force_conf.get(force, 0.2),
                provenance=prov,
            ),
        ]
        if basis:
            atoms.append(EvidenceAtom(
                key="ifadah_basis",
                value=basis,
                confidence=conf,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (ShartRequirement(
            condition_id="irab_geometry_present",
            layer_id=self.LAYER_ID,
            is_satisfied=prior_ok,
            evidence_keys=("irab_geometry_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        force = input.hokom_evidence.get("speech_force", "")
        conflict = (force == "conflict")
        unknown = (force == "unknown")
        return (
            ManiBlocker(
                blocker_id="ifadah_conflict",
                layer_id=self.LAYER_ID,
                is_active=conflict,
                severity=ResidualSeverity.BLOCKER,
                detail="Contradictory speech force signals — cannot determine ifadah",
            ),
            ManiBlocker(
                blocker_id="irab_underspecified",
                layer_id=self.LAYER_ID,
                is_active=unknown and not conflict,
                severity=ResidualSeverity.WARNING,
                detail="Speech force unknown — P11 irab geometry insufficient",
            ),
        )

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        """
        TERMINAL candidate. Must not contain HukmCandidate, RealityClaim,
        FinalMeaning, or any post-P12 signals.

        candidate_type = "IfadahSpeechForceCandidate" (NOT HukmCandidate).
        """
        # Enforce TERMINAL output_flags (no forbidden flags, no P13 signals)
        allowed_flags: frozenset[str] = frozenset({"ifadah_speech_force_candidate"})

        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="IfadahSpeechForceCandidate",   # TERMINAL type
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="ifadah_speech_force_construction",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
            output_flags=allowed_flags,
        )

    def _next_layer_id(self) -> None:
        """TERMINAL: no next stage. No P13."""
        return None
