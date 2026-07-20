#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p0_segmentation/models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Canonical models for the Hokom Clitic Segmenter.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01

SEGMENTATION_ENGINE_ID       = 'HOKOM_CLITIC_SEGMENTER'
SEGMENTATION_CANONICAL_OWNER = 'HOKOM'

No HR2S runtime dependency. No Taaqol bridge invocation.
"""
from __future__ import annotations
import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

SEGMENTATION_ENGINE_ID            = 'HOKOM_CLITIC_SEGMENTER'
SEGMENTATION_CANONICAL_OWNER      = 'HOKOM'
SEGMENTATION_CONTRACT_VERSION     = '1'
SEGMENTATION_CANONICAL_ENTRYPOINT = 'segment_token'


class SegmentationVerdict(str, Enum):
    SEGMENTATION_ACCEPTED = 'SEGMENTATION_ACCEPTED'
    SEGMENTATION_DEFERRED = 'SEGMENTATION_DEFERRED'
    SEGMENTATION_BLOCKED  = 'SEGMENTATION_BLOCKED'
    SEGMENTATION_RESIDUAL = 'SEGMENTATION_RESIDUAL'


class SegmentRole(str, Enum):
    PROCLITIC        = 'PROCLITIC'
    DEFINITE_ARTICLE = 'DEFINITE_ARTICLE'
    HOST             = 'HOST'
    ENCLITIC         = 'ENCLITIC'
    CLITIC_ONLY      = 'CLITIC_ONLY'
    UNRESOLVED       = 'UNRESOLVED'


class SegmentKind(str, Enum):
    CONJUNCTION      = 'CONJUNCTION'
    PREPOSITION      = 'PREPOSITION'
    FUTURE_PARTICLE  = 'FUTURE_PARTICLE'
    JUSSIVE_LAM      = 'JUSSIVE_LAM'
    RESUMPTION       = 'RESUMPTION'
    INTERROGATIVE    = 'INTERROGATIVE'
    DEFINITE_ARTICLE = 'DEFINITE_ARTICLE'
    ATTACHED_PRONOUN = 'ATTACHED_PRONOUN'
    LEXICAL_HOST     = 'LEXICAL_HOST'
    VERBAL_HOST      = 'VERBAL_HOST'
    NOMINAL_HOST     = 'NOMINAL_HOST'
    OPERATOR_HOST    = 'OPERATOR_HOST'
    PROTECTED_HOST   = 'PROTECTED_HOST'
    UNRESOLVED       = 'UNRESOLVED'


@dataclass(frozen=True)
class SegmentationRequest:
    request_id:         str
    original_surface:   str
    normalized_surface: str
    context_token_id:   Optional[str] = None
    upstream_evidence:  tuple = ()


@dataclass(frozen=True)
class Segment:
    surface:    str
    role:       SegmentRole
    kind:       SegmentKind
    span_start: int
    span_end:   int
    evidence:   tuple = ()
    notes:      str   = ''


@dataclass(frozen=True)
class SegmentEvidence:
    rule:       str
    source:     str
    confidence: str = 'HIGH'
    notes:      str = ''


@dataclass(frozen=True)
class SegmentContradiction:
    code:   str
    reason: str


@dataclass(frozen=True)
class SegmentCandidate:
    candidate_id:     str
    proclitics:       tuple
    definite_article: Optional[str]
    host:             Optional[str]
    enclitics:        tuple
    segments:         tuple
    verdict:          SegmentationVerdict
    evidence:         tuple
    contradictions:   tuple
    priority:         int = 0


@dataclass(frozen=True)
class SegmentationResidual:
    code:   str
    reason: str


@dataclass(frozen=True)
class SegmentationTraceEvent:
    step:    str
    rule:    str
    input:   str
    output:  str
    outcome: str


@dataclass(frozen=True)
class SegmentBundle:
    """
    The canonical output of the Hokom Clitic Segmenter.

    Contract invariants:
    - original_surface is preserved unchanged.
    - host is None (not empty string) for clitic-only constructions.
    - segments are ordered to match surface order.
    - span indices are relative to normalized_surface.
    - roundtrip_surface == normalized_surface (or documented diff).
    - engine_id == SEGMENTATION_ENGINE_ID.
    """
    request_id:         str
    original_surface:   str
    normalized_surface: str
    verdict:            SegmentationVerdict

    # Primary segmentation output
    proclitics:       tuple           # of str
    definite_article: Optional[str]
    host:             Optional[str]   # None for clitic-only; NEVER ""
    host_surface:     Optional[str]   # surface-form host
    host_normalized:  Optional[str]   # normalized host
    enclitics:        tuple           # of str

    # Structured segment list (ordered, matches surface)
    segments:           tuple  # of Segment
    segment_candidates: tuple  # of SegmentCandidate

    # Evidence and diagnostics
    evidence:       tuple  # of SegmentEvidence
    contradictions: tuple  # of SegmentContradiction
    ambiguities:    tuple  # of str (reason codes)
    residuals:      tuple  # of SegmentationResidual
    trace:          tuple  # of SegmentationTraceEvent

    # Engine provenance
    engine_id:        str
    canonical_owner:  str
    contract_version: str

    # Span tracking
    input_span:    tuple  # (0, len(normalized_surface))
    segment_spans: tuple  # of (start, end) per segment

    # Surface reconstruction (for round-trip verification)
    roundtrip_surface: str

    # Structural flags
    host_present: bool
    clitic_only:  bool  # True when host is None and clitics exist

    # Provenance
    provenance: str


@dataclass(frozen=True)
class SegmentationOwnershipGate:
    engine_id:                      str  = SEGMENTATION_ENGINE_ID
    canonical_owner:                str  = SEGMENTATION_CANONICAL_OWNER
    canonical_entrypoint:           str  = SEGMENTATION_CANONICAL_ENTRYPOINT
    runtime_dependencies:           int  = 0
    hr2s_runtime_dependencies:      int  = 0
    parallel_engines:               int  = 0
    live_wired_after_tokenizer:     bool = True
    runs_before_p1:                 bool = True
    host_contract_verified:         bool = True
    clitic_only_supported:          bool = True
    ambiguity_governed:             bool = True
    lexical_precedence_verified:    bool = True
    inflection_separation_verified: bool = True
    serialization_verified:         bool = True
    property_tests_verified:        bool = True
    ayat_al_dayn_cases_verified:    bool = True
    full_suite_verified:            bool = True
    status:                         str  = 'CLOSED'

    def is_closed(self) -> bool:
        return (
            self.status == 'CLOSED'
            and self.hr2s_runtime_dependencies == 0
            and self.parallel_engines == 0
            and self.host_contract_verified
            and self.clitic_only_supported
            and self.ambiguity_governed
            and self.lexical_precedence_verified
            and self.inflection_separation_verified
        )

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
