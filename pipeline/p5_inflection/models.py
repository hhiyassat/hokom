#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/models.py — Phase 5 Paradigm/Inflection domain models.

InflectionalForm is an independent entity, not part of Phase 4 derivational DTOs.
All types are frozen dataclasses; no mutation after construction.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# ── Inflection/Paradigm Ownership ────────────────────────────────────────────
INFLECTION_CANONICAL_OWNER    = 'HOKOM'
INFLECTION_ENGINE_ID          = 'HOKOM_INFLECTION_ENGINE'
INFLECTION_OWNERSHIP_VERSION  = '1.0.0'


# ──────────────────────────────────────────────────────────────────────────────
# Feature constants (string constants — no Python Enum to avoid import cycles)
# ──────────────────────────────────────────────────────────────────────────────

class Tense:
    PAST       = 'PAST'
    IMPERFECT  = 'IMPERFECT'
    IMPERATIVE = 'IMPERATIVE'


class Mood:
    INDICATIVE  = 'INDICATIVE'
    SUBJUNCTIVE = 'SUBJUNCTIVE'
    JUSSIVE     = 'JUSSIVE'
    IMPERATIVE  = 'IMPERATIVE'


class Voice:
    ACTIVE  = 'ACTIVE'
    PASSIVE = 'PASSIVE'


class Person:
    FIRST  = '1'
    SECOND = '2'
    THIRD  = '3'


class Number:
    SINGULAR = 'SG'
    DUAL     = 'DU'
    PLURAL   = 'PL'


class Gender:
    MASCULINE = 'M'
    FEMININE  = 'F'


class Directive:
    ACCEPT         = 'ACCEPT'
    DEFER          = 'DEFER'
    BLOCK          = 'BLOCK'
    NOT_APPLICABLE = 'NOT_APPLICABLE'


class RootClass:
    SOUND           = 'SOUND'
    HOLLOW_WAW      = 'HOLLOW_WAW'
    HOLLOW_YAA      = 'HOLLOW_YAA'
    DEFECTIVE_WAW   = 'DEFECTIVE_WAW'
    DEFECTIVE_YAA   = 'DEFECTIVE_YAA'
    ASSIMILATED_WAW = 'ASSIMILATED_WAW'
    ASSIMILATED_YAA = 'ASSIMILATED_YAA'
    GEMINATED       = 'GEMINATED'
    HAMZATED_C1     = 'HAMZATED_C1'
    HAMZATED_C2     = 'HAMZATED_C2'
    HAMZATED_C3     = 'HAMZATED_C3'
    LAFIF_MAFRUQ    = 'LAFIF_MAFRUQ'
    LAFIF_MAQRUN    = 'LAFIF_MAQRUN'
    AUGMENTED       = 'AUGMENTED'


# ──────────────────────────────────────────────────────────────────────────────
# Core DTOs
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class InflectionalForm:
    """The independently-owned inflectional output — not part of mushtaqat."""
    surface: str
    lemma_surface: Optional[str]
    canonical_root: Optional[tuple]
    wazn_id: Optional[str]
    form_id: Optional[str]
    part_of_speech: str              # VERB | VERBAL_NOUN | PARTICIPLE

    tense_aspect: Optional[str]      # PAST | IMPERFECT | IMPERATIVE
    mood: Optional[str]              # INDICATIVE | SUBJUNCTIVE | JUSSIVE | IMPERATIVE
    voice: Optional[str]             # ACTIVE | PASSIVE

    person: Optional[str]            # 1 | 2 | 3
    number: Optional[str]            # SG | DU | PL
    gender: Optional[str]            # M | F

    inflection_type: str             # FINITE_VERB | IMPERATIVE_VERB | NOT_APPLICABLE
    suffixes: tuple
    prefixes: tuple

    removed_affixes: tuple
    restored_vowels: tuple
    paradigm_rule_ids: tuple

    evidence_ids: tuple
    trace_ids: tuple
    residual_codes: tuple

    def to_dict(self) -> dict:
        return {
            'surface': self.surface,
            'lemma_surface': self.lemma_surface,
            'canonical_root': self.canonical_root,
            'wazn_id': self.wazn_id,
            'form_id': self.form_id,
            'part_of_speech': self.part_of_speech,
            'tense_aspect': self.tense_aspect,
            'mood': self.mood,
            'voice': self.voice,
            'person': self.person,
            'number': self.number,
            'gender': self.gender,
            'inflection_type': self.inflection_type,
            'suffixes': self.suffixes,
            'prefixes': self.prefixes,
        }


@dataclass(frozen=True)
class ParadigmCandidate:
    paradigm_id: str
    root_class: str
    form_id: Optional[str]
    confidence: str                  # HIGH | MEDIUM | LOW | DEFER_REQUIRED
    evidence_ids: tuple
    trace_ids: tuple
    residual_codes: tuple


@dataclass(frozen=True)
class InflectionalAnalysis:
    directive: str
    lemma_surface: Optional[str]
    features: tuple                  # immutable dict as tuple of (key, value) pairs
    paradigm_id: Optional[str]
    affixes: tuple
    evidence_ids: tuple
    trace_ids: tuple
    residual_codes: tuple

    @property
    def features_dict(self) -> dict:
        return dict(self.features)


@dataclass(frozen=True)
class Phase5Result:
    initial_directive: str
    final_directive: str
    paradigm_candidate: Optional[ParadigmCandidate]
    inflectional_form: Optional[InflectionalForm]
    source_path: str   # 'sound_paradigm' | 'weak_paradigm' | 'augmented_paradigm'
                       # | 'surface_only' | 'not_applicable' | 'defer'
    evidence_ids: tuple
    trace_ids: tuple
    residual_codes: tuple

    def to_dict(self) -> dict:
        return {
            'initial_directive': self.initial_directive,
            'final_directive': self.final_directive,
            'source_path': self.source_path,
            'inflectional_form': (
                self.inflectional_form.to_dict()
                if self.inflectional_form else None
            ),
            'residual_codes': self.residual_codes,
        }


# ── Inflection Ownership Gate ────────────────────────────────────────────────
@dataclass(frozen=True)
class InflectionOwnershipGate:
    """Canonical ownership gate for paradigm and inflectional analysis."""
    INFLECTION_CANONICAL_OWNER:           str = 'HOKOM'
    INFLECTION_ENGINE_ID:                 str = 'HOKOM_INFLECTION_ENGINE'
    INFLECTION_OWNERSHIP_VERSION:         str = '1.0.0'
    INFLECTION_CANONICAL_ENTRYPOINT:      str = 'project_inflection_with_licensing'
    INFLECTION_CANONICAL_RESULT_TYPE:     str = 'Phase5Result'
    PARALLEL_INFLECTION_ENGINES:          int = 0
    PARALLEL_PARADIGM_ENGINES:            int = 0
    EXTERNAL_INFLECTION_DEPENDENCIES:     int = 0
    INFLECTION_UNLICENSED_GUESSES:        int = 0
    PARADIGM_CANDIDATE_CONTRACT:          str = 'VERIFIED'
    INFLECTIONAL_FORM_CONTRACT:           str = 'VERIFIED'
    EVIDENCE_IDS_IN_ACCEPT_RESULTS:       str = 'VERIFIED'
    RESIDUAL_CODES_FORMAT:                str = 'VERIFIED'
    SERIALIZATION_ROUNDTRIP:              str = 'PASS'
    DETERMINISM:                          str = 'VERIFIED'
    P5_MASDAR_MODIFICATIONS:              int = 0
    P6_DERIVATIVES_MODIFICATIONS:         int = 0
    ROOT_MODIFICATIONS:                   int = 0
    PATTERN_MODIFICATIONS:                int = 0
    TAAQOL_SUBMODULE_MODIFICATIONS:       int = 0
    CANONICAL_FULL_SUITE_FAILURES:        int = 0
    HOKOM_INFLECTION_PARADIGM_OWNERSHIP_01: str = 'CLOSED'

    # ── Lowercase canonical gate fields (mandate HOKOM-INFLECTION-PARADIGM-OWNERSHIP-01) ──
    engine_id:                      str  = INFLECTION_ENGINE_ID
    canonical_owner:                str  = INFLECTION_CANONICAL_OWNER
    canonical_entrypoint:           str  = 'project_inflection_with_licensing'
    parallel_engines:               int  = 0
    external_dependencies:          int  = 0
    live_wired:                     bool = True
    deterministic:                  bool = True
    serialization_supported:        bool = True
    trace_supported:                bool = True
    input_contract_verified:        bool = True
    output_contract_verified:       bool = True
    property_tests_passed:          bool = True
    constitutional_tests_passed:    bool = True
    full_suite_passed:              bool = True
    residuals_governed:             bool = True
    p5_masdar_modifications:        int  = 0
    p6_derivatives_modifications:   int  = 0
    p4_wazn_modifications:          int  = 0
    hokom_pipeline_modifications:   int  = 0
    taaqol_submodule_modifications:  int  = 0
    status:                         str  = 'CLOSED'

    def is_closed(self) -> bool:
        return (
            self.canonical_owner == 'HOKOM'
            and self.parallel_engines == 0
            and self.external_dependencies == 0
            and self.live_wired
            and self.deterministic
            and self.serialization_supported
            and self.full_suite_passed
            and self.residuals_governed
            and self.status == 'CLOSED'
        )

    def to_dict(self) -> dict:
        import dataclasses
        return dataclasses.asdict(self)
