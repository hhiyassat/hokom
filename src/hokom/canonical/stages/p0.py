"""
p0.py — Stage adapters for SCG-P0: Unicode / TypedCodepoint / Glyph

Three adapters in this file:
    UnicodeAdapter          → P0_UNICODE_CANDIDATE
    TypedCodepointAdapter   → P0_TYPED_CODEPOINT
    GlyphAdapter            → P0_GLYPH_CLASSIFICATION

Hokom evidence owner: src/pipeline/p0_unicode/, src/pipeline/p0_segmentation/
Saleh contract: UnicodeCandidateLayer, TypedCodePointLayer, GlyphClassificationLayer
Taaqol: licenses each transition via TransitionGate.decide()

Evidence keys expected in StageInput.hokom_evidence (P0_UNICODE_CANDIDATE):
    "codepoints"     : list[dict] — [{"position": int, "codepoint": int, "char": str}]

Evidence keys (P0_TYPED_CODEPOINT):
    "typed_codepoints": list[dict] — [{"position": int, "type": str, "codepoint": int}]

Evidence keys (P0_GLYPH_CLASSIFICATION):
    "glyphs"         : list[dict] — [{"position": int, "glyph_class": str, "char": str}]
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
    CandidateStatus,
    EvidenceAtom,
    EvidenceSet,
    ProvenanceRef,
    Residual,
    ResidualSeverity,
    SlotState,
)
from .base import StageAdapter, StageInput


# ─────────────────────────────────────────────────────────────────────────────
# P0_UNICODE_CANDIDATE
# ─────────────────────────────────────────────────────────────────────────────

class UnicodeAdapter(StageAdapter):
    """
    P0_UNICODE_CANDIDATE — converts raw text input to Unicode codepoint sequence.

    Saleh conditions: raw_input_not_empty
    Saleh blockers:   encoding_error
    """

    LAYER_ID = "P0_UNICODE_CANDIDATE"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = ProvenanceRef(
            owner="hokom",
            module_path="hokom.pipeline.p0_unicode",
            rule_id="unicode_codepoint_extraction",
            stage_id=self.LAYER_ID,
        )
        codepoints = input.hokom_evidence.get("codepoints", [])
        atoms: list[EvidenceAtom] = []
        for cp in codepoints:
            atoms.append(EvidenceAtom(
                key=f"codepoint_value:{cp.get('position', 0)}",
                value=cp.get("codepoint"),
                confidence=1.0 if cp.get("codepoint") is not None else 0.0,
                provenance=prov,
            ))
        if not atoms:
            # Surface itself is the minimal evidence
            atoms.append(EvidenceAtom(
                key="raw_input_not_empty",
                value=bool(input.surface.strip()),
                confidence=1.0 if input.surface.strip() else 0.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[ShartRequirement, ...]:
        return (
            ShartRequirement(
                condition_id="raw_input_not_empty",
                layer_id=self.LAYER_ID,
                is_satisfied=bool(input.surface.strip()),
                evidence_keys=("raw_input_not_empty",),
            ),
        )

    def _check_blockers(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[ManiBlocker, ...]:
        # encoding_error: try to encode to UTF-8
        try:
            input.surface.encode("utf-8")
            encoding_ok = True
        except UnicodeEncodeError:
            encoding_ok = False
        return (
            ManiBlocker(
                blocker_id="encoding_error",
                layer_id=self.LAYER_ID,
                is_active=not encoding_ok,
                severity=ResidualSeverity.BLOCKER,
                detail="Surface text failed UTF-8 encoding check",
            ),
        )

    def _build_candidate(
        self,
        input: StageInput,
        evidence: EvidenceSet,
        candidate_id: str,
        status: ConstitutionalStatus,
        taaqol_rank: int,
    ) -> CanonicalCandidate:
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="UnicodeCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="unicode_codepoint_extraction",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self) -> str:
        return "P0_TYPED_CODEPOINT"


# ─────────────────────────────────────────────────────────────────────────────
# P0_TYPED_CODEPOINT
# ─────────────────────────────────────────────────────────────────────────────

class TypedCodepointAdapter(StageAdapter):
    """
    P0_TYPED_CODEPOINT — classifies Unicode codepoints by Arabic script type.

    Saleh conditions: unicode_candidates_present
    Saleh blockers:   non_arabic_codepoints (WARNING, non-fatal)
    """

    LAYER_ID = "P0_TYPED_CODEPOINT"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = ProvenanceRef(
            owner="hokom",
            module_path="hokom.pipeline.p0_unicode",
            rule_id="typed_codepoint_classification",
            stage_id=self.LAYER_ID,
        )
        typed = input.hokom_evidence.get("typed_codepoints", [])
        atoms: list[EvidenceAtom] = []
        for tc in typed:
            atoms.append(EvidenceAtom(
                key=f"typed_codepoint:{tc.get('position', 0)}",
                value=tc.get("type", "unknown"),
                confidence=0.95 if tc.get("type") not in (None, "unknown") else 0.5,
                provenance=prov,
            ))
        if not atoms:
            atoms.append(EvidenceAtom(
                key="unicode_candidates_present",
                value=bool(input.prior_output and input.prior_output.accepted),
                confidence=1.0 if input.prior_output and input.prior_output.accepted else 0.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[ShartRequirement, ...]:
        prior_ok = bool(
            input.prior_output and input.prior_output.accepted
        )
        return (
            ShartRequirement(
                condition_id="unicode_candidates_present",
                layer_id=self.LAYER_ID,
                is_satisfied=prior_ok,
                evidence_keys=("unicode_candidates_present",),
            ),
        )

    def _check_blockers(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[ManiBlocker, ...]:
        # Warn (non-fatal) if non-Arabic codepoints detected
        typed = input.hokom_evidence.get("typed_codepoints", [])
        non_arabic = any(
            tc.get("type", "") in ("latin", "numeric", "punctuation")
            for tc in typed
        )
        return (
            ManiBlocker(
                blocker_id="non_arabic_codepoints",
                layer_id=self.LAYER_ID,
                is_active=non_arabic,
                severity=ResidualSeverity.WARNING,
                detail="Non-Arabic codepoints detected (FASID, not BATIL)",
            ),
        )

    def _build_candidate(
        self,
        input: StageInput,
        evidence: EvidenceSet,
        candidate_id: str,
        status: ConstitutionalStatus,
        taaqol_rank: int,
    ) -> CanonicalCandidate:
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="TypedCodepoint",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="typed_codepoint_classification",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self) -> str:
        return "P0_GLYPH_CLASSIFICATION"


# ─────────────────────────────────────────────────────────────────────────────
# P0_GLYPH_CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

class GlyphAdapter(StageAdapter):
    """
    P0_GLYPH_CLASSIFICATION — classifies Arabic glyphs by phonetic function.

    Saleh conditions: typed_codepoints_present
    Saleh blockers:   glyph_resolution_failure

    Hokom module: pipeline/p0_segmentation/ (glyph classification step)
    """

    LAYER_ID = "P0_GLYPH_CLASSIFICATION"

    def _collect_evidence(self, input: StageInput) -> EvidenceSet:
        prov = ProvenanceRef(
            owner="hokom",
            module_path="hokom.pipeline.p0_segmentation",
            rule_id="glyph_classification",
            stage_id=self.LAYER_ID,
        )
        glyphs = input.hokom_evidence.get("glyphs", [])
        atoms: list[EvidenceAtom] = []
        for g in glyphs:
            gc = g.get("glyph_class", "unknown")
            atoms.append(EvidenceAtom(
                key=f"glyph_class:{g.get('position', 0)}",
                value=gc,
                confidence=0.95 if gc not in (None, "unknown") else 0.4,
                provenance=prov,
            ))
        if not atoms:
            atoms.append(EvidenceAtom(
                key="typed_codepoints_present",
                value=bool(input.prior_output and input.prior_output.accepted),
                confidence=1.0 if input.prior_output and input.prior_output.accepted else 0.0,
                provenance=prov,
            ))
        return EvidenceSet.from_atoms(self.LAYER_ID, tuple(atoms))

    def _check_conditions(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[ShartRequirement, ...]:
        prior_ok = bool(input.prior_output and input.prior_output.accepted)
        return (
            ShartRequirement(
                condition_id="typed_codepoints_present",
                layer_id=self.LAYER_ID,
                is_satisfied=prior_ok,
                evidence_keys=("typed_codepoints_present",),
            ),
        )

    def _check_blockers(
        self, input: StageInput, evidence: EvidenceSet
    ) -> tuple[ManiBlocker, ...]:
        glyphs = input.hokom_evidence.get("glyphs", [])
        failure = any(g.get("glyph_class") in (None, "error") for g in glyphs)
        return (
            ManiBlocker(
                blocker_id="glyph_resolution_failure",
                layer_id=self.LAYER_ID,
                is_active=failure,
                severity=ResidualSeverity.BLOCKER,
                detail="One or more glyphs could not be classified",
            ),
        )

    def _build_candidate(
        self,
        input: StageInput,
        evidence: EvidenceSet,
        candidate_id: str,
        status: ConstitutionalStatus,
        taaqol_rank: int,
    ) -> CanonicalCandidate:
        return CanonicalCandidate(
            candidate_id=candidate_id,
            candidate_type="GlyphCandidate",
            status=self._make_candidate_status(status),
            layer_id=self.LAYER_ID,
            source_rule_id="glyph_classification",
            evidence=evidence,
            slot_state=self._make_slot_state(status, taaqol_rank),
            taaqol_rank=taaqol_rank,
        )

    def _next_layer_id(self) -> str:
        return "P1_LETTER_IDENTITY_CARRIER"
