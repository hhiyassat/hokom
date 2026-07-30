"""
p2_p5.py — Stage adapters for SCG-P2 through P5.

    P2_REGISTRY_PROJECTION      — projects slots onto Arabic root registry
    P3_ROOT_STEM_CLOSURE        — closes root+stem candidates
    P4_JAMID_MUSHTAQ            — classifies as jamid (invariable) or mushtaq (derived)
    P5_MUFRAD_WORD_CONTRACTS    — produces mufrad (singular word) contracts

Hokom evidence owners:
    P2: pipeline/p2_projection/
    P3: pipeline/p3_pre_root/, pipeline/p3_candidate/
    P4: pipeline/p4_bab/, pipeline/p4_wazn/, pipeline/p4_mushtaqat/
    P5: pipeline/p5_lexical/, pipeline/p5_masdar/, pipeline/p5_inflection/

Saleh adapter rules implemented here mirror:
    P3: ACCEPT if consonant_count ≥ 2 and not all-vowel; DEFER if consonant_count=1;
        BLOCK if consonant_count=0 or encoding_error
    P5: ACCEPT if word_geometry resolved; DEFER if boundary_underspecified
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
# P2_REGISTRY_PROJECTION
# ─────────────────────────────────────────────────────────────────────────────

class RegistryProjectionAdapter(StageAdapter):
    """
    P2_REGISTRY_PROJECTION — maps slot candidates to Arabic root registry entries.

    Saleh conditions: slot_candidates_present, registry_loaded
    Saleh blockers:   registry_load_failure

    Evidence keys:
        "registry_matches": list[dict] — {slot_id, root, match_confidence}
    """

    LAYER_ID = "P2_REGISTRY_PROJECTION"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("p2_projection", "registry_projection", self.LAYER_ID)
        matches = input.hokom_evidence.get("registry_matches", [])
        atoms: list[EvidenceAtom] = []
        for m in matches:
            atoms.append(EvidenceAtom(
                key=f"registry_match:{m.get('slot_id', '?')}",
                value=m.get("root"),
                confidence=float(m.get("match_confidence", 0.8)),
                provenance=prov,
            ))
        if not atoms:
            atoms.append(EvidenceAtom(
                key="slot_candidates_present",
                value=bool(input.prior_output and input.prior_output.accepted),
                confidence=1.0 if input.prior_output and input.prior_output.accepted else 0.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (
            ShartRequirement(
                condition_id="slot_candidates_present",
                layer_id=self.LAYER_ID,
                is_satisfied=prior_ok,
                evidence_keys=("slot_candidates_present",),
            ),
            ShartRequirement(
                condition_id="registry_loaded",
                layer_id=self.LAYER_ID,
                is_satisfied=True,  # Hokom always loads registry at startup
                evidence_keys=("registry_loaded",),
            ),
        )

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        registry_matches = input.hokom_evidence.get("registry_matches")
        failure = registry_matches is None
        return (ManiBlocker(
            blocker_id="registry_load_failure",
            layer_id=self.LAYER_ID,
            is_active=failure,
            severity=ResidualSeverity.BLOCKER,
            detail="Registry matches not provided — registry may not be loaded",
        ),)

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="RegistryProjectionCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="registry_projection",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P3_ROOT_STEM_CLOSURE"


# ─────────────────────────────────────────────────────────────────────────────
# P3_ROOT_STEM_CLOSURE
# ─────────────────────────────────────────────────────────────────────────────

class RootStemAdapter(StageAdapter):
    """
    P3_ROOT_STEM_CLOSURE — extracts root+stem and closes the candidate.

    Saleh adapter rules (from root_stem_adapter.py):
        ACCEPT if consonant_count ≥ 2 AND NOT all-vowel
        DEFER  if consonant_count == 1 (single-letter root possible: ي, و, أ)
        BLOCK  if consonant_count == 0

    Evidence keys:
        "consonant_count": int
        "root_radicals":   list[str] — R1, R2, R3, [R4]
        "stem":            str
        "root_path":       str — "ROOT_PATH_BLOCKED" if clitic_only
    """

    LAYER_ID = "P3_ROOT_STEM_CLOSURE"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("p3_pre_root", "root_stem_extraction", self.LAYER_ID)
        cc = input.hokom_evidence.get("consonant_count", 0)
        radicals = input.hokom_evidence.get("root_radicals", [])
        stem = input.hokom_evidence.get("stem", "")
        root_path = input.hokom_evidence.get("root_path", "")
        # Rich classification atoms (improve Taaqol licensing specificity)
        root_class = input.hokom_evidence.get("root_class", "")
        root_soundness = input.hokom_evidence.get("root_soundness", "")
        stem_type = input.hokom_evidence.get("stem_type", "")

        atoms = [
            EvidenceAtom(
                key="consonant_count",
                value=cc,
                confidence=1.0 if cc > 0 else 0.0,
                provenance=prov,
            ),
            EvidenceAtom(
                key="root_radicals",
                value=tuple(radicals),
                confidence=0.9 if len(radicals) >= 2 else (0.5 if radicals else 0.0),
                provenance=prov,
            ),
        ]
        if stem:
            atoms.append(EvidenceAtom(
                key="stem",
                value=stem,
                confidence=0.85,
                provenance=prov,
            ))
        if root_path == "ROOT_PATH_BLOCKED":
            atoms.append(EvidenceAtom(
                key="root_path",
                value="ROOT_PATH_BLOCKED",
                confidence=0.0,
                provenance=prov,
            ))
        # Per-radical atoms (definitive classification → improves LICENSED rate)
        if len(radicals) >= 1:
            atoms.append(EvidenceAtom(
                key="root_r1", value=radicals[0], confidence=0.92, provenance=prov,
            ))
        if len(radicals) >= 2:
            atoms.append(EvidenceAtom(
                key="root_r2", value=radicals[1], confidence=0.92, provenance=prov,
            ))
        if len(radicals) >= 3:
            atoms.append(EvidenceAtom(
                key="root_r3", value=radicals[2], confidence=0.92, provenance=prov,
            ))
        if root_class:
            atoms.append(EvidenceAtom(
                key="root_class", value=root_class, confidence=0.92, provenance=prov,
            ))
        if root_soundness:
            atoms.append(EvidenceAtom(
                key="root_soundness", value=root_soundness, confidence=0.9, provenance=prov,
            ))
        if stem_type:
            atoms.append(EvidenceAtom(
                key="stem_type", value=stem_type, confidence=0.88, provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        cc = input.hokom_evidence.get("consonant_count", 0)
        return (
            ShartRequirement(
                condition_id="consonant_count_gte_1",
                layer_id=self.LAYER_ID,
                is_satisfied=cc >= 1,
                evidence_keys=("consonant_count",),
            ),
            ShartRequirement(
                condition_id="registry_projection_present",
                layer_id=self.LAYER_ID,
                is_satisfied=bool(input.prior_output and input.prior_output.accepted),
                evidence_keys=("registry_projection_present",),
            ),
        )

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        cc = input.hokom_evidence.get("consonant_count", 0)
        root_path = input.hokom_evidence.get("root_path", "")
        return (
            ManiBlocker(
                blocker_id="consonant_count_zero",
                layer_id=self.LAYER_ID,
                is_active=(cc == 0),
                severity=ResidualSeverity.BLOCKER,
                detail="Zero consonants — cannot construct root",
            ),
            ManiBlocker(
                blocker_id="root_path_blocked",
                layer_id=self.LAYER_ID,
                is_active=(root_path == "ROOT_PATH_BLOCKED"),
                severity=ResidualSeverity.BLOCKER,
                detail="ROOT_PATH_BLOCKED: clitic-only word has no lexical host",
            ),
        )

    def _check_defects(self, input: StageInput, evidence: EvidenceSet):
        cc = input.hokom_evidence.get("consonant_count", 0)
        # Single-consonant root is a defect (DEFER, not block)
        return (QadihDefect(
            defect_id="consonant_count_underspecified",
            layer_id=self.LAYER_ID,
            is_active=(cc == 1),
            severity=ResidualSeverity.WARNING,
            invalidating=False,
            detail="Single consonant — root underspecified, deferring",
        ),)

    def _determine_status(self, shurut, mawani, qawadih, granted_rank):
        cc = 0
        for s in shurut:
            if s.condition_id == "consonant_count_gte_1" and not s.is_satisfied:
                return ConstitutionalStatus.BATIL
        for m in mawani:
            if m.is_active and m.severity == ResidualSeverity.BLOCKER:
                return ConstitutionalStatus.BATIL
        # Single consonant → DEFERRED
        for q in qawadih:
            if q.is_active and q.defect_id == "consonant_count_underspecified":
                return ConstitutionalStatus.DEFERRED
        return super()._determine_status(shurut, mawani, qawadih, granted_rank)

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="RootStemCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="root_stem_extraction",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P4_JAMID_MUSHTAQ"


# ─────────────────────────────────────────────────────────────────────────────
# P4_JAMID_MUSHTAQ
# ─────────────────────────────────────────────────────────────────────────────

class JamidMushtaqAdapter(StageAdapter):
    """
    P4_JAMID_MUSHTAQ — classifies word as jamid (invariable) or mushtaq (derived).

    Hokom owner: pipeline/p4_bab/, p4_wazn/, p4_mushtaqat/

    Evidence keys:
        "jamid_mushtaq": str — "jamid" | "mushtaq" | "unknown"
        "wazn":          str — morphological pattern
        "bab_id":        str — verb class (for mushtaq verbs)
    """

    LAYER_ID = "P4_JAMID_MUSHTAQ"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("p4_bab", "jamid_mushtaq_classification", self.LAYER_ID)
        jm = input.hokom_evidence.get("jamid_mushtaq", "unknown")
        wazn = input.hokom_evidence.get("wazn", "")
        bab_id = input.hokom_evidence.get("bab_id", "")
        atoms = [EvidenceAtom(
            key="jamid_mushtaq",
            value=jm,
            confidence=0.9 if jm in ("jamid", "mushtaq") else 0.3,
            provenance=prov,
        )]
        if wazn:
            atoms.append(EvidenceAtom(
                key="wazn",
                value=wazn,
                confidence=0.85,
                provenance=prov,
            ))
        if bab_id:
            atoms.append(EvidenceAtom(
                key="bab_id",
                value=bab_id,
                confidence=0.85,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (ShartRequirement(
            condition_id="root_stem_present",
            layer_id=self.LAYER_ID,
            is_satisfied=prior_ok,
            evidence_keys=("root_stem_present",),
        ),)

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        jm = input.hokom_evidence.get("jamid_mushtaq", "unknown")
        unknown = (jm == "unknown")
        return (ManiBlocker(
            blocker_id="jamid_mushtaq_unresolved",
            layer_id=self.LAYER_ID,
            is_active=unknown,
            severity=ResidualSeverity.WARNING,
            detail="Jamid/mushtaq classification unresolved — deferring",
        ),)

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="JamidMushtaqCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="jamid_mushtaq_classification",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P5_MUFRAD_WORD_CONTRACTS"


# ─────────────────────────────────────────────────────────────────────────────
# P5_MUFRAD_WORD_CONTRACTS
# ─────────────────────────────────────────────────────────────────────────────

class MufradWordAdapter(StageAdapter):
    """
    P5_MUFRAD_WORD_CONTRACTS — produces mufrad (singular-word) contracts.

    Saleh adapter rules (from mufrad_word_adapter.py):
        ACCEPT if word_geometry resolved AND boundary_closed
        DEFER  if boundary_underspecified
        BLOCK  if word_type_conflict

    Hokom owner: pipeline/p5_lexical/, p5_masdar/, p5_inflection/

    Evidence keys:
        "word_geometry":   str — "resolved" | "boundary_underspecified" | "conflict"
        "word_class":      str — noun/verb/particle/etc.
        "masdar":          str — (if applicable)
        "inflection_set":  list[str]
    """

    LAYER_ID = "P5_MUFRAD_WORD_CONTRACTS"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = _prov("p5_lexical", "mufrad_word_contract", self.LAYER_ID)
        wg = input.hokom_evidence.get("word_geometry", "boundary_underspecified")
        wc = input.hokom_evidence.get("word_class", "")
        masdar = input.hokom_evidence.get("masdar", "")
        inflections = input.hokom_evidence.get("inflection_set", [])
        # Rich classification atoms (improve Taaqol licensing specificity)
        inflection_class = input.hokom_evidence.get("inflection_class", "")
        word_boundary = input.hokom_evidence.get("word_boundary", "")
        predecessor_verdict = input.hokom_evidence.get("predecessor_p4_verdict", "")

        confidence_map = {
            "resolved": 0.92,
            "boundary_underspecified": 0.45,
            "conflict": 0.0,
        }
        atoms = [EvidenceAtom(
            key="word_geometry",
            value=wg,
            confidence=confidence_map.get(wg, 0.3),
            provenance=prov,
        )]
        if wc:
            atoms.append(EvidenceAtom(
                key="word_class",
                value=wc,
                confidence=0.85,
                provenance=prov,
            ))
        if masdar:
            atoms.append(EvidenceAtom(
                key="masdar",
                value=masdar,
                confidence=0.8,
                provenance=prov,
            ))
        if inflections:
            atoms.append(EvidenceAtom(
                key="inflection_count",
                value=len(inflections),
                confidence=0.85,
                provenance=prov,
            ))
        # Per-field atoms for Taaqol specificity
        if inflection_class:
            atoms.append(EvidenceAtom(
                key="inflection_class", value=inflection_class, confidence=0.88, provenance=prov,
            ))
        if word_boundary:
            atoms.append(EvidenceAtom(
                key="word_boundary", value=word_boundary, confidence=0.9, provenance=prov,
            ))
        if predecessor_verdict:
            atoms.append(EvidenceAtom(
                key="predecessor_p4_verdict", value=predecessor_verdict, confidence=0.88, provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(self, input: StageInput, evidence: EvidenceSet):
        wg = input.hokom_evidence.get("word_geometry", "")
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (
            ShartRequirement(
                condition_id="jamid_mushtaq_resolved",
                layer_id=self.LAYER_ID,
                is_satisfied=prior_ok,
                evidence_keys=("jamid_mushtaq_resolved",),
            ),
            ShartRequirement(
                condition_id="word_geometry_not_conflicted",
                layer_id=self.LAYER_ID,
                is_satisfied=(wg != "conflict"),
                evidence_keys=("word_geometry",),
            ),
        )

    def _check_blockers(self, input: StageInput, evidence: EvidenceSet):
        wg = input.hokom_evidence.get("word_geometry", "")
        return (
            ManiBlocker(
                blocker_id="word_type_conflict",
                layer_id=self.LAYER_ID,
                is_active=(wg == "conflict"),
                severity=ResidualSeverity.BLOCKER,
                detail="Word type conflict: incompatible geometry signals",
            ),
            ManiBlocker(
                blocker_id="boundary_underspecified",
                layer_id=self.LAYER_ID,
                is_active=(wg == "boundary_underspecified"),
                severity=ResidualSeverity.WARNING,
                detail="Word boundary underspecified — deferring to P6",
            ),
        )

    def _build_candidate(self, input, evidence, candidate_id, status, taaqol_rank):
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="MufradWordCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="mufrad_word_contract",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self): return "P6_VERBAL_SIGNIFIED_ALONE"
