"""
pipeline.py — 19-stage canonical pipeline runner.

Wires all 19 stage adapters in canonical order (P0→P12) and produces
a typed PipelineTrace carrying ConstitutionalJudgment per stage.

Usage:

    from hokom.canonical.pipeline import CanonicalPipeline, WordInput

    pipeline = CanonicalPipeline.build()
    trace = pipeline.run_word(WordInput(
        surface="كَتَبَ",
        hokom_evidence_by_stage={...},
        pipeline_run_id="run-001",
        word_index=0,
    ))

    # For sentence-level stages (P9-P12):
    trace = pipeline.run_sentence(SentenceInput(
        words=[WordInput(...)],
        sentence_hokom_evidence={...},
        pipeline_run_id="run-001",
    ))

Ownership: HR2S/H2RS are FORBIDDEN everywhere in this module.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from .constitutional.contracts import ConstitutionalJudgment, ConstitutionalStatus
from .slot_algebra.types import CanonicalCandidateSet
from .stages.base import StageAdapter, StageInput, StageOutput

# ── Import all 19 stage adapters ──────────────────────────────────────────────
from .stages.p0 import UnicodeAdapter, TypedCodepointAdapter, GlyphAdapter
from .stages.p1 import (
    LetterIdentityAdapter,
    HarakaMarkAdapter,
    ConditionedSequenceAdapter,
    PositionAdapter,
    SlotCandidateAdapter,
)
from .stages.p2_p5 import (
    RegistryProjectionAdapter,
    RootStemAdapter,
    JamidMushtaqAdapter,
    MufradWordAdapter,
)
from .stages.p6_p8 import (
    VerbalSignifiedAdapter,
    CompositionReadinessAdapter,
    AmilMamulAdapter,
)
from .stages.p9_p12 import (
    SentenceGeometryAdapter,
    RelationGeometryAdapter,
    IrabGeometryAdapter,
    IfadahAdapter,
)


# ── Pipeline data classes ─────────────────────────────────────────────────────

@dataclass(frozen=True)
class StageTrace:
    """Record of one stage's execution in a pipeline run."""
    layer_id: str
    judgment: ConstitutionalJudgment
    candidate_set: CanonicalCandidateSet
    stage_status: ConstitutionalStatus


@dataclass(frozen=True)
class WordInput:
    """
    Input for the word-level stages (P0-P8) of the pipeline.

    Fields:
        surface                  — Arabic surface text (NFC-normalized)
        hokom_evidence_by_stage  — dict mapping layer_id → evidence dict
                                   (keys match each adapter's Evidence keys doc)
        pipeline_run_id          — unique ID for this run (auto-generated if empty)
        word_index               — 0-based position in sentence
    """
    surface: str
    hokom_evidence_by_stage: dict[str, dict[str, Any]]
    pipeline_run_id: str = ""
    word_index: int = 0

    def __post_init__(self) -> None:
        if not self.surface.strip():
            raise ValueError("WordInput.surface must not be empty")


@dataclass(frozen=True)
class SentenceInput:
    """
    Input for the sentence-level stages (P9-P12).

    Fields:
        words                   — list of WordInput in sentence order
        sentence_hokom_evidence — dict mapping layer_id → evidence dict
                                  for P9-P12 (sentence-level Hokom evidence)
        pipeline_run_id         — unique ID (auto-generated if empty)
    """
    words: tuple[WordInput, ...]
    sentence_hokom_evidence: dict[str, dict[str, Any]]
    pipeline_run_id: str = ""


@dataclass
class PipelineTrace:
    """
    Complete output of a 19-stage pipeline run.

    Fields:
        pipeline_run_id     — unique ID for this run
        surface             — original Arabic surface text
        word_stages         — StageTrace list for P0-P8 (word-level)
        sentence_stages     — StageTrace list for P9-P12 (sentence-level)
        terminal_judgment   — ConstitutionalJudgment for P12
        is_complete         — True if all 19 stages reached (even if DEFERRED)
        stages_by_id        — dict[layer_id → StageTrace] for fast lookup
    """
    pipeline_run_id: str
    surface: str
    word_stages: list[StageTrace] = field(default_factory=list)
    sentence_stages: list[StageTrace] = field(default_factory=list)
    terminal_judgment: ConstitutionalJudgment | None = None
    is_complete: bool = False
    stages_by_id: dict[str, StageTrace] = field(default_factory=dict)

    @property
    def all_stages(self) -> list[StageTrace]:
        return self.word_stages + self.sentence_stages

    def get_stage(self, layer_id: str) -> StageTrace | None:
        return self.stages_by_id.get(layer_id)

    def highest_reached_stage(self) -> str | None:
        """Return the layer_id of the last completed stage."""
        if self.sentence_stages:
            return self.sentence_stages[-1].layer_id
        if self.word_stages:
            return self.word_stages[-1].layer_id
        return None

    def licensed_count(self) -> int:
        """Number of stages with taaqol_rank >= 4 (LICENSED)."""
        return sum(
            1 for t in self.all_stages
            if t.candidate_set.is_licensed
        )


# ── Word-level stage order (P0-P8) ───────────────────────────────────────────
_WORD_STAGE_IDS: tuple[str, ...] = (
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
    "P6_VERBAL_SIGNIFIED_ALONE",
    "P7_COMPOSITION_READINESS",
    "P8_AMIL_MAMUL",
)

# ── Sentence-level stage order (P9-P12) ──────────────────────────────────────
_SENTENCE_STAGE_IDS: tuple[str, ...] = (
    "P9_SENTENCE_GEOMETRY",
    "P10_RELATION_GEOMETRY",
    "P11_IRAB_GEOMETRY",
    "P12_IFADAH_SPEECH_FORCE",
)


# ── Pipeline class ────────────────────────────────────────────────────────────

class CanonicalPipeline:
    """
    19-stage canonical pipeline wiring Saleh contracts, Hokom evidence,
    and Taaqol licensing.

    Build once; call run_word() or run_sentence() per input.
    """

    def __init__(self, adapters: dict[str, StageAdapter]) -> None:
        self._adapters = adapters

    @classmethod
    def build(cls) -> CanonicalPipeline:
        """
        Instantiate all 19 stage adapters and return a ready pipeline.

        This loads the registry snapshot (fails if not generated yet).
        """
        adapters: dict[str, StageAdapter] = {
            # P0
            "P0_UNICODE_CANDIDATE":      UnicodeAdapter(),
            "P0_TYPED_CODEPOINT":        TypedCodepointAdapter(),
            "P0_GLYPH_CLASSIFICATION":   GlyphAdapter(),
            # P1
            "P1_LETTER_IDENTITY_CARRIER":      LetterIdentityAdapter(),
            "P1_HARAKA_MARK_IDENTITY_CARRIER": HarakaMarkAdapter(),
            "P1_CONDITIONED_TYPED_SEQUENCE":   ConditionedSequenceAdapter(),
            "P1_POSITION_CARRIER":             PositionAdapter(),
            "P1_SLOT_CANDIDATE":               SlotCandidateAdapter(),
            # P2-P5
            "P2_REGISTRY_PROJECTION":    RegistryProjectionAdapter(),
            "P3_ROOT_STEM_CLOSURE":      RootStemAdapter(),
            "P4_JAMID_MUSHTAQ":          JamidMushtaqAdapter(),
            "P5_MUFRAD_WORD_CONTRACTS":  MufradWordAdapter(),
            # P6-P8
            "P6_VERBAL_SIGNIFIED_ALONE":  VerbalSignifiedAdapter(),
            "P7_COMPOSITION_READINESS":   CompositionReadinessAdapter(),
            "P8_AMIL_MAMUL":              AmilMamulAdapter(),
            # P9-P12
            "P9_SENTENCE_GEOMETRY":      SentenceGeometryAdapter(),
            "P10_RELATION_GEOMETRY":     RelationGeometryAdapter(),
            "P11_IRAB_GEOMETRY":         IrabGeometryAdapter(),
            "P12_IFADAH_SPEECH_FORCE":   IfadahAdapter(),
        }
        return cls(adapters)

    def run_word(self, word_input: WordInput) -> PipelineTrace:
        """
        Run the word-level stages (P0-P8) for a single Arabic word.

        Returns a PipelineTrace with word_stages populated.
        Sentence-level stages (P9-P12) are NOT run — call run_sentence()
        for multi-word sentence processing.
        """
        run_id = word_input.pipeline_run_id or str(uuid.uuid4())[:8]
        trace = PipelineTrace(
            pipeline_run_id=run_id,
            surface=word_input.surface,
        )

        prior_output: CanonicalCandidateSet | None = None

        for layer_id in _WORD_STAGE_IDS:
            adapter = self._adapters[layer_id]
            evidence = word_input.hokom_evidence_by_stage.get(layer_id, {})

            stage_input = StageInput(
                layer_id=layer_id,
                surface=word_input.surface,
                hokom_evidence=evidence,
                prior_output=prior_output,
                pipeline_run_id=run_id,
                word_index=word_input.word_index,
            )

            output: StageOutput = adapter.adapt(stage_input)

            st = StageTrace(
                layer_id=layer_id,
                judgment=output.judgment,
                candidate_set=output.candidate_set,
                stage_status=output.judgment.status,
            )
            trace.word_stages.append(st)
            trace.stages_by_id[layer_id] = st

            # Always forward the candidate set (even DEFERRED carries residuals)
            prior_output = output.candidate_set

            # If BATIL: cannot continue
            if output.judgment.status is ConstitutionalStatus.BATIL:
                break

        trace.is_complete = (len(trace.word_stages) == len(_WORD_STAGE_IDS))
        return trace

    def run_sentence(self, sentence_input: SentenceInput) -> PipelineTrace:
        """
        Run the full 19-stage pipeline for a multi-word Arabic sentence.

        1. Runs P0-P8 for each word in order.
        2. Collects P8 AmilMamulCandidates across words.
        3. Runs P9-P12 with sentence-level evidence.

        Returns a PipelineTrace with both word_stages and sentence_stages.
        """
        run_id = sentence_input.pipeline_run_id or str(uuid.uuid4())[:8]

        # Aggregate word traces
        all_word_stages: list[StageTrace] = []
        all_stages_by_id: dict[str, StageTrace] = {}

        # Surface for the whole sentence
        sentence_surface = " ".join(w.surface for w in sentence_input.words)

        # Run word-level stages for each word, collecting P8 outputs
        p8_candidates: list[dict] = []
        for word_input in sentence_input.words:
            wi = WordInput(
                surface=word_input.surface,
                hokom_evidence_by_stage=word_input.hokom_evidence_by_stage,
                pipeline_run_id=run_id,
                word_index=word_input.word_index,
            )
            word_trace = self.run_word(wi)
            # Collect stages (don't duplicate)
            for st in word_trace.word_stages:
                keyed = f"{st.layer_id}:w{word_input.word_index}"
                all_stages_by_id[keyed] = st
            all_word_stages.extend(word_trace.word_stages)

            # Extract P8 unit for sentence geometry
            p8_trace = word_trace.get_stage("P8_AMIL_MAMUL")
            if p8_trace and p8_trace.candidate_set.accepted:
                p8_candidates.append({
                    "unit_id": f"w{word_input.word_index}-p8",
                    "word_index": word_input.word_index,
                    "role": word_input.hokom_evidence_by_stage.get(
                        "P8_AMIL_MAMUL", {}
                    ).get("amil_role", "unknown"),
                    "candidate_id": (
                        p8_trace.candidate_set.accepted[0].candidate_id
                        if p8_trace.candidate_set.accepted
                        else ""
                    ),
                })

        # Build merged trace
        trace = PipelineTrace(
            pipeline_run_id=run_id,
            surface=sentence_surface,
            word_stages=all_word_stages,
            stages_by_id=all_stages_by_id,
        )

        # Run sentence-level stages P9-P12
        prior_output: CanonicalCandidateSet | None = None

        for layer_id in _SENTENCE_STAGE_IDS:
            adapter = self._adapters[layer_id]

            # Merge sentence evidence with P8 units
            base_evidence = sentence_input.sentence_hokom_evidence.get(layer_id, {})
            if layer_id == "P9_SENTENCE_GEOMETRY":
                # Inject P8 units if not already provided
                if "amil_mamul_units" not in base_evidence:
                    base_evidence = {**base_evidence, "amil_mamul_units": p8_candidates}

            stage_input = StageInput(
                layer_id=layer_id,
                surface=sentence_surface,
                hokom_evidence=base_evidence,
                prior_output=prior_output,
                pipeline_run_id=run_id,
                word_index=None,  # sentence-level
            )

            output: StageOutput = adapter.adapt(stage_input)

            st = StageTrace(
                layer_id=layer_id,
                judgment=output.judgment,
                candidate_set=output.candidate_set,
                stage_status=output.judgment.status,
            )
            trace.sentence_stages.append(st)
            trace.stages_by_id[layer_id] = st

            if layer_id == "P12_IFADAH_SPEECH_FORCE":
                trace.terminal_judgment = output.judgment

            prior_output = output.candidate_set

            if output.judgment.status is ConstitutionalStatus.BATIL:
                break

        trace.is_complete = (
            len(trace.sentence_stages) == len(_SENTENCE_STAGE_IDS)
        )
        return trace
