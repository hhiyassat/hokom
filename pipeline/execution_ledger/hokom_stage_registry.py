"""
hokom_stage_registry.py — Canonical Hokom 19-stage registry.

This file is the single source of truth for Hokom stage definitions.
It must contain exactly 19 StageDefinition entries matching
src/hokom/canonical/registry/saleh_snapshot.py CANONICAL_LAYER_IDS.

CONSTITUTIONAL CONSTRAINT: do not add or remove stages.
Any mismatch with CANONICAL_LAYER_IDS is HOKOM_STAGE_REGISTRY_COUNT_MISMATCH = BLOCKER.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .models import ExecutionScope, Engine

EXPECTED_HOKOM_STAGE_COUNT = 19

HOKOM_TOKEN_STAGES = frozenset({
    "P0_UNICODE_CANDIDATE",
    "P0_TYPED_CODEPOINT",
    "P0_GLYPH_CLASSIFICATION",
    "P1_LETTER_IDENTITY_CARRIER",
    "P1_HARAKA_MARK_IDENTITY_CARRIER",
    "P1_CONDITIONED_TYPED_SEQUENCE",
    "P1_POSITION_CARRIER",
    "P1_SLOT_CANDIDATE",
    "P2_REGISTRY_PROJECTION",
    "P3_ROOT_STEM_CLOSURE",
    "P4_JAMID_MUSHTAQ",
    "P5_MUFRAD_WORD_CONTRACTS",
})

HOKOM_SPAN_OR_HIGHER_STAGES = frozenset({
    "P6_VERBAL_SIGNIFIED_ALONE",
    "P7_COMPOSITION_READINESS",
    "P8_AMIL_MAMUL",
    "P9_SENTENCE_GEOMETRY",
    "P10_RELATION_GEOMETRY",
    "P11_IRAB_GEOMETRY",
    "P12_IFADAH_SPEECH_FORCE",
})

@dataclass(frozen=True)
class StageDefinition:
    stage_id: str
    canonical_name: str
    owner: str                     # "HOKOM" | "SALEH" | "TAAQOL"
    scope: ExecutionScope
    input_type: str
    output_type: str
    required_predecessors: tuple[str, ...]
    applicability_rule: str        # human-readable
    executor: str                  # module path
    evidence_requirement: str
    residual_policy: str
    successors: tuple[str, ...]
    terminal: bool
    source_module: str

HOKOM_STAGE_REGISTRY: tuple[StageDefinition, ...] = (
    StageDefinition(
        stage_id="P0_UNICODE_CANDIDATE",
        canonical_name="Dal Alone: Unicode Candidate",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="str (surface)",
        output_type="UnicodeCandidate",
        required_predecessors=(),
        applicability_rule="always applicable — first stage",
        executor="hokom.canonical.stages.p0.UnicodeAdapter",
        evidence_requirement="raw_input_not_empty",
        residual_policy="encoding_error → BATIL",
        successors=("P0_TYPED_CODEPOINT",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p0.py",
    ),
    StageDefinition(
        stage_id="P0_TYPED_CODEPOINT",
        canonical_name="Dal Alone: Typed Codepoint",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="UnicodeCandidate",
        output_type="TypedCodepoint",
        required_predecessors=("P0_UNICODE_CANDIDATE",),
        applicability_rule="P0_UNICODE_CANDIDATE APPROVED",
        executor="hokom.canonical.stages.p0.TypedCodepointAdapter",
        evidence_requirement="unicode_candidates_present",
        residual_policy="non_arabic_codepoints → FASID (WARNING, non-fatal)",
        successors=("P0_GLYPH_CLASSIFICATION",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p0.py",
    ),
    StageDefinition(
        stage_id="P0_GLYPH_CLASSIFICATION",
        canonical_name="Dal Alone: Glyph Classification",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="TypedCodepoint",
        output_type="GlyphCandidate",
        required_predecessors=("P0_TYPED_CODEPOINT",),
        applicability_rule="P0_TYPED_CODEPOINT APPROVED",
        executor="hokom.canonical.stages.p0.GlyphAdapter",
        evidence_requirement="typed_codepoints_present",
        residual_policy="glyph_resolution_failure → BATIL",
        successors=("P1_LETTER_IDENTITY_CARRIER",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p0.py",
    ),
    StageDefinition(
        stage_id="P1_LETTER_IDENTITY_CARRIER",
        canonical_name="Dal Alone Atomic: Letter Identity Carrier",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="GlyphCandidate",
        output_type="LetterIdentityCarrier",
        required_predecessors=("P0_GLYPH_CLASSIFICATION",),
        applicability_rule="P0_GLYPH_CLASSIFICATION APPROVED",
        executor="hokom.canonical.stages.p1.LetterIdentityAdapter",
        evidence_requirement="glyph_candidates_present",
        residual_policy="ambiguous_letter_identity → DEFERRED",
        successors=("P1_HARAKA_MARK_IDENTITY_CARRIER",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p1.py",
    ),
    StageDefinition(
        stage_id="P1_HARAKA_MARK_IDENTITY_CARRIER",
        canonical_name="Dal Alone Atomic: Haraka Mark Identity",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="LetterIdentityCarrier",
        output_type="HarakaMarkCarrier",
        required_predecessors=("P1_LETTER_IDENTITY_CARRIER",),
        applicability_rule="P1_LETTER_IDENTITY_CARRIER APPROVED",
        executor="hokom.canonical.stages.p1.HarakaMarkAdapter",
        evidence_requirement="letter_identity_present",
        residual_policy="haraka_ambiguity → DEFERRED",
        successors=("P1_CONDITIONED_TYPED_SEQUENCE",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p1.py",
    ),
    StageDefinition(
        stage_id="P1_CONDITIONED_TYPED_SEQUENCE",
        canonical_name="Dal Alone Atomic: Conditioned Typed Sequence",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="HarakaMarkCarrier",
        output_type="ConditionedTypedSequence",
        required_predecessors=("P1_HARAKA_MARK_IDENTITY_CARRIER",),
        applicability_rule="P1_HARAKA_MARK_IDENTITY_CARRIER APPROVED",
        executor="hokom.canonical.stages.p1.ConditionedSequenceAdapter",
        evidence_requirement="haraka_marks_present",
        residual_policy="sequence_gap → DEFERRED",
        successors=("P1_POSITION_CARRIER",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p1.py",
    ),
    StageDefinition(
        stage_id="P1_POSITION_CARRIER",
        canonical_name="Dal Alone Atomic: Position Carrier",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="ConditionedTypedSequence",
        output_type="PositionCarrier",
        required_predecessors=("P1_CONDITIONED_TYPED_SEQUENCE",),
        applicability_rule="P1_CONDITIONED_TYPED_SEQUENCE APPROVED",
        executor="hokom.canonical.stages.p1.PositionAdapter",
        evidence_requirement="typed_sequence_present",
        residual_policy="position_conflict → DEFERRED",
        successors=("P1_SLOT_CANDIDATE",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p1.py",
    ),
    StageDefinition(
        stage_id="P1_SLOT_CANDIDATE",
        canonical_name="Dal Alone Atomic: Slot Candidate",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="PositionCarrier",
        output_type="SlotCandidate",
        required_predecessors=("P1_POSITION_CARRIER",),
        applicability_rule="P1_POSITION_CARRIER APPROVED",
        executor="hokom.canonical.stages.p1.SlotAdapter",
        evidence_requirement="position_carrier_present",
        residual_policy="slot_unfillable → DEFERRED",
        successors=("P2_REGISTRY_PROJECTION",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p1.py",
    ),
    StageDefinition(
        stage_id="P2_REGISTRY_PROJECTION",
        canonical_name="Registry Projection",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="SlotCandidate",
        output_type="RegistryProjection",
        required_predecessors=("P1_SLOT_CANDIDATE",),
        applicability_rule="P1_SLOT_CANDIDATE APPROVED",
        executor="hokom.canonical.stages.p2_p5.RegistryProjectionAdapter",
        evidence_requirement="slot_candidate_present",
        residual_policy="no_registry_entry → DEFERRED",
        successors=("P3_ROOT_STEM_CLOSURE",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p2_p5.py",
    ),
    StageDefinition(
        stage_id="P3_ROOT_STEM_CLOSURE",
        canonical_name="Root Stem Closure",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="RegistryProjection",
        output_type="RootStemClosure",
        required_predecessors=("P2_REGISTRY_PROJECTION",),
        applicability_rule="P2_REGISTRY_PROJECTION APPROVED; not JAMID_AALAM_BOUNDARY",
        executor="hokom.canonical.stages.p2_p5.RootStemClosureAdapter",
        evidence_requirement="registry_projection_present",
        residual_policy="no_root → DEFERRED; ambiguous_root → DEFERRED",
        successors=("P4_JAMID_MUSHTAQ",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p2_p5.py",
    ),
    StageDefinition(
        stage_id="P4_JAMID_MUSHTAQ",
        canonical_name="Jamid / Mushtaq Classification",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="RootStemClosure",
        output_type="JamidMushtaqDecision",
        required_predecessors=("P3_ROOT_STEM_CLOSURE",),
        applicability_rule="P3_ROOT_STEM_CLOSURE APPROVED",
        executor="hokom.canonical.stages.p2_p5.JamidMushtaqAdapter",
        evidence_requirement="root_stem_present",
        residual_policy="ambiguous_class → DEFERRED",
        successors=("P5_MUFRAD_WORD_CONTRACTS",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p2_p5.py",
    ),
    StageDefinition(
        stage_id="P5_MUFRAD_WORD_CONTRACTS",
        canonical_name="Mufrad Word Contracts",
        owner="HOKOM",
        scope=ExecutionScope.TOKEN,
        input_type="JamidMushtaqDecision",
        output_type="MufradWordContract",
        required_predecessors=("P4_JAMID_MUSHTAQ",),
        applicability_rule="P4_JAMID_MUSHTAQ APPROVED; mufrad scope only",
        executor="hokom.canonical.stages.p2_p5.MufradWordContractsAdapter",
        evidence_requirement="jamid_mushtaq_decision_present",
        residual_policy="contract_unsatisfied → DEFERRED",
        successors=("P6_VERBAL_SIGNIFIED_ALONE",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p2_p5.py",
    ),
    StageDefinition(
        stage_id="P6_VERBAL_SIGNIFIED_ALONE",
        canonical_name="Verbal Signified Alone",
        owner="HOKOM",
        scope=ExecutionScope.SPAN,
        input_type="MufradWordContract",
        output_type="VerbalSignifiedAlone",
        required_predecessors=("P5_MUFRAD_WORD_CONTRACTS",),
        applicability_rule="P5_MUFRAD_WORD_CONTRACTS APPROVED; verb present; span scope",
        executor="hokom.canonical.stages.p6_p8.VerbalSignifiedAloneAdapter",
        evidence_requirement="mufrad_word_contract_present; verbal_evidence",
        residual_policy="no_verbal_evidence → DEFERRED",
        successors=("P7_COMPOSITION_READINESS",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p6_p8.py",
    ),
    StageDefinition(
        stage_id="P7_COMPOSITION_READINESS",
        canonical_name="Composition Readiness",
        owner="HOKOM",
        scope=ExecutionScope.SPAN,
        input_type="VerbalSignifiedAlone",
        output_type="CompositionReadiness",
        required_predecessors=("P6_VERBAL_SIGNIFIED_ALONE",),
        applicability_rule="P6_VERBAL_SIGNIFIED_ALONE APPROVED",
        executor="hokom.canonical.stages.p6_p8.CompositionReadinessAdapter",
        evidence_requirement="verbal_signified_present",
        residual_policy="composition_blocked → DEFERRED",
        successors=("P8_AMIL_MAMUL",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p6_p8.py",
    ),
    StageDefinition(
        stage_id="P8_AMIL_MAMUL",
        canonical_name="Amil / Mamul Governance",
        owner="HOKOM",
        scope=ExecutionScope.CLAUSE,
        input_type="CompositionReadiness",
        output_type="AmilMamulBinding",
        required_predecessors=("P7_COMPOSITION_READINESS",),
        applicability_rule="P7_COMPOSITION_READINESS APPROVED; clause scope",
        executor="hokom.canonical.stages.p6_p8.AmilMamulAdapter",
        evidence_requirement="composition_readiness_present",
        residual_policy="amil_unresolved → DEFERRED; mamul_missing → BLOCKED",
        successors=("P9_SENTENCE_GEOMETRY",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p6_p8.py",
    ),
    StageDefinition(
        stage_id="P9_SENTENCE_GEOMETRY",
        canonical_name="Sentence Geometry",
        owner="HOKOM",
        scope=ExecutionScope.SENTENCE,
        input_type="AmilMamulBinding",
        output_type="SentenceGeometry",
        required_predecessors=("P8_AMIL_MAMUL",),
        applicability_rule="P8_AMIL_MAMUL APPROVED; sentence scope",
        executor="hokom.canonical.stages.p9_p12.SentenceGeometryAdapter",
        evidence_requirement="amil_mamul_binding_present",
        residual_policy="sentence_incomplete → DEFERRED",
        successors=("P10_RELATION_GEOMETRY",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p9_p12.py",
    ),
    StageDefinition(
        stage_id="P10_RELATION_GEOMETRY",
        canonical_name="Relation Geometry",
        owner="HOKOM",
        scope=ExecutionScope.RELATION,
        input_type="SentenceGeometry",
        output_type="RelationGeometry",
        required_predecessors=("P9_SENTENCE_GEOMETRY",),
        applicability_rule="P9_SENTENCE_GEOMETRY APPROVED; relation scope",
        executor="hokom.canonical.stages.p9_p12.RelationGeometryAdapter",
        evidence_requirement="sentence_geometry_present",
        residual_policy="relation_unresolved → DEFERRED",
        successors=("P11_IRAB_GEOMETRY",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p9_p12.py",
    ),
    StageDefinition(
        stage_id="P11_IRAB_GEOMETRY",
        canonical_name="Irab Geometry",
        owner="HOKOM",
        scope=ExecutionScope.RELATION,
        input_type="RelationGeometry",
        output_type="IrabGeometry",
        required_predecessors=("P10_RELATION_GEOMETRY",),
        applicability_rule="P10_RELATION_GEOMETRY APPROVED",
        executor="hokom.canonical.stages.p9_p12.IrabGeometryAdapter",
        evidence_requirement="relation_geometry_present",
        residual_policy="irab_ambiguous → DEFERRED",
        successors=("P12_IFADAH_SPEECH_FORCE",),
        terminal=False,
        source_module="src/hokom/canonical/stages/p9_p12.py",
    ),
    StageDefinition(
        stage_id="P12_IFADAH_SPEECH_FORCE",
        canonical_name="Ifadah / Speech Force (TERMINAL)",
        owner="HOKOM",
        scope=ExecutionScope.DISCOURSE,
        input_type="IrabGeometry",
        output_type="IfadahSpeechForce",
        required_predecessors=("P11_IRAB_GEOMETRY",),
        applicability_rule="P11_IRAB_GEOMETRY APPROVED; discourse scope; TERMINAL",
        executor="hokom.canonical.stages.p9_p12.IfadahSpeechForceAdapter",
        evidence_requirement="irab_geometry_present",
        residual_policy="ifadah_incomplete → DEFERRED",
        successors=(),
        terminal=True,
        source_module="src/hokom/canonical/stages/p9_p12.py",
    ),
)

def validate_registry() -> list[str]:
    """Validate the registry. Returns list of error strings (empty = valid)."""
    errors = []
    ids = [s.stage_id for s in HOKOM_STAGE_REGISTRY]
    
    if len(ids) != EXPECTED_HOKOM_STAGE_COUNT:
        errors.append(
            f"HOKOM_STAGE_REGISTRY_COUNT_MISMATCH: expected {EXPECTED_HOKOM_STAGE_COUNT}, "
            f"actual {len(ids)}"
        )
    
    if len(set(ids)) != len(ids):
        dupes = [i for i in ids if ids.count(i) > 1]
        errors.append(f"DUPLICATE_STAGE_IDS: {list(set(dupes))}")
    
    terminals = [s for s in HOKOM_STAGE_REGISTRY if s.terminal]
    if len(terminals) != 1:
        errors.append(f"TERMINAL_COUNT_MISMATCH: expected 1, got {len(terminals)}")
    elif terminals[0].stage_id != "P12_IFADAH_SPEECH_FORCE":
        errors.append(f"WRONG_TERMINAL: {terminals[0].stage_id}")
    
    return errors

def get_stage(stage_id: str) -> StageDefinition:
    for s in HOKOM_STAGE_REGISTRY:
        if s.stage_id == stage_id:
            return s
    raise KeyError(f"Stage not found: {stage_id}")

def get_all_stage_ids() -> tuple[str, ...]:
    return tuple(s.stage_id for s in HOKOM_STAGE_REGISTRY)

def token_scope_stages() -> tuple[StageDefinition, ...]:
    return tuple(s for s in HOKOM_STAGE_REGISTRY if s.stage_id in HOKOM_TOKEN_STAGES)

def higher_scope_stages() -> tuple[StageDefinition, ...]:
    return tuple(s for s in HOKOM_STAGE_REGISTRY if s.stage_id in HOKOM_SPAN_OR_HIGHER_STAGES)
