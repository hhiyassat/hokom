"""
p6_p8.py — Stage adapters for SCG-P6 through P8.

    P6_VERBAL_SIGNIFIED_ALONE   — extracts verbal signified (المدلول الفعلي)
    P7_COMPOSITION_READINESS    — checks composition readiness
    P8_AMIL_MAMUL               — produces amil/mamul (governor/governed) candidates

Hokom evidence owners:
    P6: pipeline/p6_derivatives/
    P7: (new integration level — checks P6 output for composition signals)
    P8: (new integration level — amil/mamul detection)

Saleh adapter rules:
    P6: ACCEPT if short-vowel cadence matches verbal pattern; DEFER if ambiguous
    P7: ACCEPT if all prior amil/mamul signals consistent; DEFER if underspecified
    P8: ACCEPT if ≥1 amil + ≥1 mamul identified; DEFER if only 1 unit
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


def _prov(module: str, rule: str, layer_id: str) -> ProvenanceRef:
    return ProvenanceRef(
        owner="hokom",
        module_path=f"hokom.pipeline.{module}",
        rule_id=rule,
        stage_id=layer_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# P6_VERBAL_SIGNIFIED_ALONE
# ─────────────────────────────────────────────────────────────────────────────

class VerbalSignifiedAdapter(StageAdapter):
    """
    P6_VERBAL_SIGNIFIED_ALONE — detects verbal signified from short-vowel cadence.

    Saleh adapter rules (from verbal_signified_adapter.py):
        ACCEPT if cadence matches known verbal pattern (فَعَلَ، فَعَّلَ، etc.)
        DEFER  if cadence is ambiguous (multiple pattern matches)
        BLOCK  if cadence clearly non-verbal (pure nominal/particle)

    Hokom owner: pipeline/p6_derivatives/

    Evidence keys:
        "verbal_cadence":     str — e.g. "fa3ala", "ambiguous", "non_verbal"
        "signified_type":     str — "verb" | "participle" | "masdar" | "unknown"
        "cadence_confidence": float [0,1]
    """

    LAYER_ID = "P6_VERBAL_SIGNIFIED_ALONE"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("p6_derivatives", "verbal_signified_detection", self.LAYER_ID)
        cadence = input.hokom_evidence.get("verbal_cadence", "unknown")
        sig_type = input.hokom_evidence.get("signified_type", "unknown")
        conf = float(input.hokom_evidence.get("cadence_confidence", 0.5))
        # Rich classification atoms
        signified_class = input.hokom_evidence.get("signified_class", "")
        verbal_form = input.hokom_evidence.get("verbal_form", "")
        atoms = [
            EvidenceAtom(
                key="verbal_cadence",
                value=cadence,
                confidence=conf if cadence != "non_verbal" else 0.0,
                provenance=prov,
            ),
            EvidenceAtom(
                key="signified_type",
                value=sig_type,
                confidence=0.85 if sig_type not in (None, "unknown") else 0.3,
                provenance=prov,
            ),
        ]
        # cadence_type as a named classification atom (alias for Taaqol gate clarity)
        if cadence and cadence not in ("unknown", "non_verbal", "ambiguous"):
            atoms.append(EvidenceAtom(
                key="cadence_type", value=cadence, confidence=conf, provenance=prov,
            ))
        if signified_class:
            atoms.append(EvidenceAtom(
                key="signified_class", value=signified_class, confidence=0.88, provenance=prov,
            ))
        if verbal_form:
            atoms.append(EvidenceAtom(
                key="verbal_form", value=verbal_form, confidence=0.88, provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (ShartRequirement(
            condition_id="mufrad_word_present",
            layer_id=self.LAYER_ID,
            is_satisfied=prior_ok,
            evidence_keys=("mufrad_word_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        cadence = input.hokom_evidence.get("verbal_cadence", "")
        non_verbal = (cadence == "non_verbal")
        ambiguous = (cadence == "ambiguous")
        return (
            ManiBlocker(
                blocker_id="non_verbal_cadence",
                layer_id=self.LAYER_ID,
                is_active=non_verbal,
                severity=ResidualSeverity.BLOCKER,
                detail="Cadence clearly non-verbal — cannot produce verbal signified",
            ),
            ManiBlocker(
                blocker_id="ambiguous_verbal_cadence",
                layer_id=self.LAYER_ID,
                is_active=ambiguous,
                severity=ResidualSeverity.WARNING,
                detail="Ambiguous cadence — deferring verbal signified",
            ),
        )

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="VerbalSignifiedCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="verbal_signified_detection",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P7_COMPOSITION_READINESS"


# ─────────────────────────────────────────────────────────────────────────────
# P7_COMPOSITION_READINESS
# ─────────────────────────────────────────────────────────────────────────────

class CompositionReadinessAdapter(StageAdapter):
    """
    P7_COMPOSITION_READINESS — checks if a word is ready to participate in
    multi-word composition (amil/mamul binding).

    Saleh adapter rules (from composition_readiness_adapter.py):
        ACCEPT if word_class determined AND closure_readiness is MABNI or MURAB
        DEFER  if closure_readiness is CONTINUATION_CLOSURE_DEFERRED
        BLOCK  if composition_conflict

    Evidence keys:
        "closure_readiness":  str — mabni_closure_ready | murab_closure_deferred |
                                    continuation_closure_deferred | unknown_closure
        "composition_ready":  bool
        "word_class":         str
    """

    LAYER_ID = "P7_COMPOSITION_READINESS"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("p6_derivatives", "composition_readiness_check", self.LAYER_ID)
        cr = input.hokom_evidence.get("closure_readiness", "unknown_closure")
        ready = input.hokom_evidence.get("composition_ready", False)
        wc = input.hokom_evidence.get("word_class", "")

        cr_conf = {
            "mabni_closure_ready": 0.95,
            "murab_closure_deferred": 0.85,
            "pause_closure_ready": 0.9,
            "continuation_closure_deferred": 0.4,
            "unknown_closure": 0.2,
        }
        atoms = [
            EvidenceAtom(
                key="closure_readiness",
                value=cr,
                confidence=cr_conf.get(cr, 0.3),
                provenance=prov,
            ),
            EvidenceAtom(
                key="composition_ready",
                value=ready,
                confidence=0.9 if ready else 0.4,
                provenance=prov,
            ),
        ]
        if wc:
            atoms.append(EvidenceAtom(
                key="word_class",
                value=wc,
                confidence=0.9,
                provenance=prov,
            ))
        # Rich classification atoms for Taaqol gate specificity
        if cr and cr != "unknown_closure":
            atoms.append(EvidenceAtom(
                key="readiness_class", value=cr, confidence=cr_conf.get(cr, 0.3), provenance=prov,
            ))
        atoms.append(EvidenceAtom(
            key="composition_gate", value=str(ready), confidence=0.88, provenance=prov,
        ))
        if wc:
            atoms.append(EvidenceAtom(
                key="word_class_boundary", value=wc, confidence=0.9, provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (ShartRequirement(
            condition_id="verbal_signified_evaluated",
            layer_id=self.LAYER_ID,
            is_satisfied=prior_ok,
            evidence_keys=("verbal_signified_evaluated",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        cr = input.hokom_evidence.get("closure_readiness", "")
        deferred = (cr == "continuation_closure_deferred")
        unknown = (cr in ("unknown_closure", ""))
        return (
            ManiBlocker(
                blocker_id="composition_not_ready",
                layer_id=self.LAYER_ID,
                is_active=deferred or unknown,
                severity=ResidualSeverity.WARNING,
                detail=f"Composition not ready: closure_readiness={cr}",
            ),
        )

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="CompositionReadinessCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="composition_readiness_check",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P8_AMIL_MAMUL"


# ─────────────────────────────────────────────────────────────────────────────
# P8_AMIL_MAMUL
# ─────────────────────────────────────────────────────────────────────────────

class AmilMamulAdapter(StageAdapter):
    """
    P8_AMIL_MAMUL — produces amil (governor) / mamul (governed) candidates.

    Saleh adapter rules (from amil_mamul_adapter.py):
        ACCEPT if ≥1 amil unit + ≥1 mamul unit identified
        DEFER  if only 1 unit (single word — no governor/governed pair yet)
        BLOCK  if amil/mamul role conflict

    Note: P9 requires ≥2 DISTINCT AmilMamulCandidate units (sentence geometry).
    P8 provides the per-word AmilMamulCandidate; P9 checks for ≥2 across words.

    Evidence keys:
        "amil_role":    str — "amil" | "mamul" | "both" | "unknown"
        "amil_unit_id": str — identifier of this word's amil/mamul unit
        "unit_count":   int — number of composition-ready units seen so far
    """

    LAYER_ID = "P8_AMIL_MAMUL"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("sga", "amil_mamul_detection", self.LAYER_ID)
        role = input.hokom_evidence.get("amil_role", "unknown")
        unit_id = input.hokom_evidence.get("amil_unit_id", "")
        unit_count = int(input.hokom_evidence.get("unit_count", 1))
        # Rich classification atoms
        relation_class = input.hokom_evidence.get("relation_class", "")
        domain_class = input.hokom_evidence.get("domain", "")

        role_conf = {
            "amil": 0.9,
            "mamul": 0.9,
            "both": 0.7,   # ambiguous — governor that is also governed
            "unknown": 0.2,
        }
        atoms = [
            EvidenceAtom(
                key="amil_role",
                value=role,
                confidence=role_conf.get(role, 0.2),
                provenance=prov,
            ),
            EvidenceAtom(
                key="unit_count",
                value=unit_count,
                confidence=1.0,
                provenance=prov,
            ),
        ]
        if unit_id:
            atoms.append(EvidenceAtom(
                key="amil_unit_id",
                value=unit_id,
                confidence=0.95,
                provenance=prov,
            ))
        # mamul_role constant: P8 always involves a mamul relationship
        atoms.append(EvidenceAtom(
            key="mamul_role", value="mamul", confidence=0.88, provenance=prov,
        ))
        if relation_class:
            atoms.append(EvidenceAtom(
                key="relation_class", value=relation_class, confidence=0.88, provenance=prov,
            ))
        if domain_class:
            atoms.append(EvidenceAtom(
                key="domain_class", value=domain_class, confidence=0.88, provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (ShartRequirement(
            condition_id="composition_readiness_present",
            layer_id=self.LAYER_ID,
            is_satisfied=prior_ok,
            evidence_keys=("composition_readiness_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        role = input.hokom_evidence.get("amil_role", "")
        conflict = (role == "conflict")
        single_unit = (int(input.hokom_evidence.get("unit_count", 1)) < 2)
        return (
            ManiBlocker(
                blocker_id="amil_mamul_role_conflict",
                layer_id=self.LAYER_ID,
                is_active=conflict,
                severity=ResidualSeverity.BLOCKER,
                detail="Amil/mamul role conflict detected",
            ),
            ManiBlocker(
                blocker_id="adjacency_underspecified",
                layer_id=self.LAYER_ID,
                is_active=single_unit and not conflict,
                severity=ResidualSeverity.WARNING,
                detail=(
                    "Only 1 composition-ready unit — "
                    "amil/mamul pair requires ≥2; deferring to P9"
                ),
            ),
        )

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="AmilMamulCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="amil_mamul_detection",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P9_SENTENCE_GEOMETRY"
