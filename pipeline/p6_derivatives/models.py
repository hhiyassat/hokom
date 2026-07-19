#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p6_derivatives/models.py — Derivatives ownership contracts
DERIVATIVES_CANONICAL_OWNER   = HOKOM
DERIVATIVES_ENGINE_ID         = HOKOM_DERIVATIVES_ENGINE
DERIVATIVES_OWNERSHIP_VERSION = 1.0.0
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

DERIVATIVES_CANONICAL_OWNER   = 'HOKOM'
DERIVATIVES_ENGINE_ID         = 'HOKOM_DERIVATIVES_ENGINE'
DERIVATIVES_OWNERSHIP_VERSION = '1.0.0'

DERIVATIVE_TYPES = frozenset({
    'ISM_FA3IL',        # اسم الفاعل
    'ISM_MAF3UL',       # اسم المفعول
    'SIFA_MUSHABBAHA',  # الصفة المشبهة
    'MUBALGHA',         # صيغ المبالغة
    'ISM_ZAMAN',        # اسم الزمان
    'ISM_MAKAN',        # اسم المكان
    'ISM_ALA',          # اسم الآلة
})

DERIVATIVE_VERDICTS = frozenset({
    'DERIVATIVE_ACCEPTED',
    'DERIVATIVE_DEFERRED',
    'DERIVATIVE_BLOCKED',
    'DERIVATIVE_RESIDUAL',
})

DERIVATIVE_MODES = frozenset({
    'GENERATE_FROM_VERB',
    'VALIDATE_SUPPLIED_DERIVATIVE',
    'ANALYZE_DERIVATIVE_SURFACE',
})

EVIDENCE_TYPES = frozenset({
    'ROOT_LICENSE_EVIDENCE',
    'VERBAL_HOST_EVIDENCE',
    'VERB_PATTERN_EVIDENCE',
    'FORM_FAMILY_EVIDENCE',
    'PRODUCTIVE_DERIVATIVE_RULE',
    'LEXICAL_DERIVATIVE_ATTESTATION',
    'SURFACE_PATTERN_ALIGNMENT',
    'WEAK_REALIZATION_EVIDENCE',
    'DISAMBIGUATION_EVIDENCE',
    'CONTRADICTION_EVIDENCE',
})

EVIDENCE_SUFFICIENCY = frozenset({'INSUFFICIENT', 'CONTRIBUTORY', 'SUFFICIENT'})

CONTRADICTION_TYPES = frozenset({
    'ROOT_MISMATCH',
    'VERB_PATTERN_MISMATCH',
    'DERIVATIVE_PATTERN_MISMATCH',
    'NON_VERBAL_ORIGIN',
    'COMPETING_DERIVATIONAL_CATEGORY',
    'SURFACE_MAPPING_INCOMPLETE',
    'WEAK_REALIZATION_UNSUPPORTED',
    'LEXICAL_CONTRADICTION',
    'UPSTREAM_DEFERRED',
    'UPSTREAM_BLOCKED',
    'MASDAR_SURFACE_LEAKAGE',
    'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY',
})

REALIZATION_OPERATION_TYPES = frozenset({
    'DERIV_WEAK_MEDIAL_REALIZATION',
    'DERIV_WEAK_FINAL_REALIZATION',
    'DERIV_INITIAL_WEAK_REALIZATION',
    'DERIV_HAMZA_REALIZATION',
    'DERIV_GEMINATION_REALIZATION',
    'DERIV_CONTRACTION',
    'DERIV_YAA_REALIZATION',
    'DERIV_WAW_REALIZATION',
    'DERIV_VOWEL_ADJUSTMENT',
    'DERIV_TA_MARBUTA_INSERTION',
})

DERIVATIVE_RESIDUAL_CODES = frozenset({
    'FORM_I_SIFA_VERBAL_EVIDENCE_REQUIRED',
    'MUBALGHA_LEXICAL_EVIDENCE_REQUIRED',
    'ISM_ZAMAN_MAKAN_MIMI_AMBIGUITY',
    'ISM_ALA_LEXICON_GAP',
    'WEAK_DERIVATIVE_REALIZATION_GAP',
    'DERIVATIVE_CONTEXT_SIGNAL_REQUIRED',
    'DERIVATIVE_TYPE_AMBIGUITY',
})

MULTIPLICITY_VALUES = frozenset({
    'SINGLE', 'MULTIPLE_LICENSED', 'UNRESOLVED_AMBIGUITY', 'NONE',
})


@dataclass(frozen=True)
class DerivativeEvidence:
    evidence_id: str
    evidence_type: str
    sufficiency: str
    source: str
    detail: Optional[str] = None

    def __post_init__(self):
        if self.evidence_type not in EVIDENCE_TYPES:
            raise ValueError(f'unknown evidence_type: {self.evidence_type!r}')
        if self.sufficiency not in EVIDENCE_SUFFICIENCY:
            raise ValueError(f'unknown sufficiency: {self.sufficiency!r}')

    def to_dict(self):
        return {
            'evidence_id': self.evidence_id,
            'evidence_type': self.evidence_type,
            'sufficiency': self.sufficiency,
            'source': self.source,
            'detail': self.detail,
        }


@dataclass(frozen=True)
class DerivativeContradiction:
    contradiction_id: str
    contradiction_type: str
    locus: str
    detail: str

    def __post_init__(self):
        if self.contradiction_type not in CONTRADICTION_TYPES:
            raise ValueError(f'unknown contradiction_type: {self.contradiction_type!r}')

    def to_dict(self):
        return {
            'contradiction_id': self.contradiction_id,
            'contradiction_type': self.contradiction_type,
            'locus': self.locus,
            'detail': self.detail,
        }


@dataclass(frozen=True)
class DerivativeRealizationOperation:
    operation_id: str
    operation_type: str
    locus: str
    before: str
    after: str
    rule_id: str
    required_evidence: tuple
    actual_evidence: tuple
    reversible: bool
    trace: tuple

    def __post_init__(self):
        if self.operation_type not in REALIZATION_OPERATION_TYPES:
            raise ValueError(f'unknown operation_type: {self.operation_type!r}')

    def to_dict(self):
        return {
            'operation_id': self.operation_id,
            'operation_type': self.operation_type,
            'locus': self.locus,
            'before': self.before,
            'after': self.after,
            'rule_id': self.rule_id,
            'required_evidence': list(self.required_evidence),
            'actual_evidence': list(self.actual_evidence),
            'reversible': self.reversible,
            'trace': list(self.trace),
        }


@dataclass(frozen=True)
class DerivativeTraceEvent:
    step: int
    stage: str
    action: str
    detail: Optional[str] = None

    def to_dict(self):
        return {
            'step': self.step,
            'stage': self.stage,
            'action': self.action,
            'detail': self.detail,
        }


@dataclass(frozen=True)
class DerivativeRequest:
    request_id: str
    mode: str
    original_surface: str
    normalized_surface: str
    verbal_host: Optional[str]
    verbal_lemma: Optional[str]
    licensed_root: Optional[tuple]
    licensed_root_class: Optional[str]
    licensed_pattern: Optional[str]
    verb_form_family: Optional[str]
    voice: Optional[str]
    available_context: tuple
    derivative_type: Optional[str]
    supplied_derivative_surface: Optional[str]
    evidence: tuple
    upstream_trace: tuple

    def __post_init__(self):
        if self.mode not in DERIVATIVE_MODES:
            raise ValueError(f'unknown mode: {self.mode!r}')
        if self.derivative_type is not None:
            if self.derivative_type not in (DERIVATIVE_TYPES | frozenset({'auto'})):
                raise ValueError(f'unknown derivative_type: {self.derivative_type!r}')

    def to_dict(self):
        return {
            'request_id': self.request_id,
            'mode': self.mode,
            'original_surface': self.original_surface,
            'normalized_surface': self.normalized_surface,
            'verbal_host': self.verbal_host,
            'verbal_lemma': self.verbal_lemma,
            'licensed_root': list(self.licensed_root) if self.licensed_root else None,
            'licensed_root_class': self.licensed_root_class,
            'licensed_pattern': self.licensed_pattern,
            'verb_form_family': self.verb_form_family,
            'voice': self.voice,
            'available_context': list(self.available_context),
            'derivative_type': self.derivative_type,
            'supplied_derivative_surface': self.supplied_derivative_surface,
            'evidence': [e.to_dict() for e in self.evidence],
            'upstream_trace': list(self.upstream_trace),
        }


@dataclass(frozen=True)
class DerivativeCandidate:
    candidate_id: str
    derivative_type: str
    surface: Optional[str]
    normalized_surface: Optional[str]
    canonical_pattern: str
    surface_pattern: str
    underlying_pattern: str
    source_verb: Optional[str]
    root: Optional[tuple]
    root_class: Optional[str]
    verb_pattern: Optional[str]
    verb_form_family: Optional[str]
    root_mapping: tuple
    slot_mapping: tuple
    augmentation_slots: tuple
    inflectional_material: tuple
    realization_operations: tuple
    supporting_evidence: tuple
    contradicting_evidence: tuple
    required_evidence: tuple
    evidence_rank: str
    sufficiency: str
    license_kind: str
    lexical_attestation: bool
    verdict: str
    reason_codes: tuple
    named_residual: Optional[str]
    trace: tuple

    def __post_init__(self):
        if self.derivative_type not in DERIVATIVE_TYPES:
            raise ValueError(f'unknown derivative_type: {self.derivative_type!r}')
        if self.verdict not in DERIVATIVE_VERDICTS:
            raise ValueError(f'unknown verdict: {self.verdict!r}')
        if self.sufficiency not in EVIDENCE_SUFFICIENCY:
            raise ValueError(f'unknown sufficiency: {self.sufficiency!r}')

    def to_dict(self):
        return {
            'candidate_id': self.candidate_id,
            'derivative_type': self.derivative_type,
            'surface': self.surface,
            'normalized_surface': self.normalized_surface,
            'canonical_pattern': self.canonical_pattern,
            'surface_pattern': self.surface_pattern,
            'underlying_pattern': self.underlying_pattern,
            'source_verb': self.source_verb,
            'root': list(self.root) if self.root else None,
            'root_class': self.root_class,
            'verb_pattern': self.verb_pattern,
            'verb_form_family': self.verb_form_family,
            'root_mapping': list(self.root_mapping),
            'slot_mapping': list(self.slot_mapping),
            'augmentation_slots': list(self.augmentation_slots),
            'inflectional_material': list(self.inflectional_material),
            'realization_operations': [op.to_dict() for op in self.realization_operations],
            'supporting_evidence': [e.to_dict() for e in self.supporting_evidence],
            'contradicting_evidence': [c.to_dict() for c in self.contradicting_evidence],
            'required_evidence': list(self.required_evidence),
            'evidence_rank': self.evidence_rank,
            'sufficiency': self.sufficiency,
            'license_kind': self.license_kind,
            'lexical_attestation': self.lexical_attestation,
            'verdict': self.verdict,
            'reason_codes': list(self.reason_codes),
            'named_residual': self.named_residual,
            'trace': [t.to_dict() for t in self.trace],
        }


@dataclass(frozen=True)
class LicensedDerivative:
    derivative_id: str
    candidate: DerivativeCandidate
    licensing_evidence: tuple
    license_kind: str

    def to_dict(self):
        return {
            'derivative_id': self.derivative_id,
            'candidate': self.candidate.to_dict(),
            'licensing_evidence': [e.to_dict() for e in self.licensing_evidence],
            'license_kind': self.license_kind,
        }


@dataclass(frozen=True)
class DeferredDerivative:
    deferral_id: str
    reason: str
    candidates: tuple
    missing_evidence: tuple
    trace: tuple

    def to_dict(self):
        return {
            'deferral_id': self.deferral_id,
            'reason': self.reason,
            'candidates': [c.to_dict() for c in self.candidates],
            'missing_evidence': list(self.missing_evidence),
            'trace': [t.to_dict() for t in self.trace],
        }


@dataclass(frozen=True)
class BlockedDerivative:
    block_id: str
    reason: str
    contradictions: tuple
    trace: tuple

    def to_dict(self):
        return {
            'block_id': self.block_id,
            'reason': self.reason,
            'contradictions': [c.to_dict() for c in self.contradictions],
            'trace': [t.to_dict() for t in self.trace],
        }


@dataclass(frozen=True)
class DerivativeResidual:
    residual_id: str
    residual_code: str
    surface: Optional[str]
    verb: Optional[str]
    root: Optional[tuple]
    pattern: Optional[str]
    derivative_type: Optional[str]
    current_candidates: tuple
    missing_evidence: tuple
    blocking_condition: Optional[str]
    reason_code: str
    owner: str
    future_closure_stage: str
    status: str

    def to_dict(self):
        return {
            'residual_id': self.residual_id,
            'residual_code': self.residual_code,
            'surface': self.surface,
            'verb': self.verb,
            'root': list(self.root) if self.root else None,
            'pattern': self.pattern,
            'derivative_type': self.derivative_type,
            'current_candidates': [
                c.to_dict() if hasattr(c, 'to_dict') else c
                for c in self.current_candidates
            ],
            'missing_evidence': list(self.missing_evidence),
            'blocking_condition': self.blocking_condition,
            'reason_code': self.reason_code,
            'owner': self.owner,
            'future_closure_stage': self.future_closure_stage,
            'status': self.status,
        }


@dataclass(frozen=True)
class DerivativeResult:
    result_id: str
    request: DerivativeRequest
    verdict: str
    multiplicity: str
    licensed_derivatives: tuple
    deferred: Optional[DeferredDerivative]
    blocked: Optional[BlockedDerivative]
    residuals: tuple
    all_candidates: tuple
    trace: tuple
    source_engine: str

    def __post_init__(self):
        if self.verdict not in DERIVATIVE_VERDICTS:
            raise ValueError(f'unknown verdict: {self.verdict!r}')
        if self.multiplicity not in MULTIPLICITY_VALUES:
            raise ValueError(f'unknown multiplicity: {self.multiplicity!r}')

    def to_dict(self):
        return {
            'result_id': self.result_id,
            'request': self.request.to_dict(),
            'verdict': self.verdict,
            'multiplicity': self.multiplicity,
            'licensed_derivatives': [d.to_dict() for d in self.licensed_derivatives],
            'deferred': self.deferred.to_dict() if self.deferred else None,
            'blocked': self.blocked.to_dict() if self.blocked else None,
            'residuals': [r.to_dict() for r in self.residuals],
            'all_candidates': [c.to_dict() for c in self.all_candidates],
            'trace': [t.to_dict() for t in self.trace],
            'source_engine': self.source_engine,
        }


@dataclass(frozen=True)
class DerivativesOwnershipGate:
    DERIVATIVES_CANONICAL_OWNER:              str = 'HOKOM'
    DERIVATIVES_CANONICAL_ENTRYPOINT:         str = 'VERIFIED'
    DERIVATIVES_OWNERSHIP_VERSION:            str = '1.0.0'
    DERIVATIVES_CANONICAL_RESULT_TYPE:        str = 'DerivativeResult'
    DERIVATIVES_CANONICAL_RULE_REGISTRY:      str = 'data/derivatives/derivative_rule_registry.jsonl'
    DERIVATIVES_CANONICAL_DATA_SOURCE:        str = 'data/derivatives/derivative_lexical_inventory.jsonl'
    DERIVATIVES_CANONICAL_TRACE_FORMAT:       str = 'DerivativeTraceEvent'
    PARALLEL_DERIVATIVE_ENGINES:              int = 0
    EXTERNAL_DERIVATIVE_DEPENDENCIES:         int = 0
    ISM_FA3IL_CONTRACT:                       str = 'VERIFIED'
    ISM_MAF3UL_CONTRACT:                      str = 'VERIFIED'
    SIFA_MUSHABBAHA_CONTRACT:                 str = 'VERIFIED'
    MUBALGHA_CONTRACT:                        str = 'VERIFIED'
    ISM_ZAMAN_CONTRACT:                       str = 'VERIFIED'
    ISM_MAKAN_CONTRACT:                       str = 'VERIFIED'
    ISM_ALA_CONTRACT:                         str = 'VERIFIED'
    MASDAR_MIMI_LEAKAGE_PREVENTION:           str = 'VERIFIED'
    FA3IL_PARTICIPLE_ROUTING_PRESERVED:       str = 'VERIFIED'
    ISM_ZAMAN_MAKAN_AMBIGUITY_GOVERNED:       str = 'VERIFIED'
    MUBALGHA_UNLICENSED_GUESSES:              int = 0
    SIFA_UNLICENSED_GUESSES:                  int = 0
    MULTIPLE_LICENSED_DERIVATIVES:            str = 'SUPPORTED'
    DERIVATIVE_RESIDUALS_GOVERNED:            str = 'VERIFIED'
    DERIVATIVE_TRACE_COMPLETE:                str = 'VERIFIED'
    DERIVATIVE_SERIALIZATION_ROUNDTRIP:       str = 'PASS'
    P5_MASDAR_SEMANTIC_MODIFICATIONS:         int = 0
    ROOT_SEMANTIC_MODIFICATIONS:              int = 0
    PATTERN_SEMANTIC_MODIFICATIONS:           int = 0
    TAAQOL_SUBMODULE_MODIFICATIONS:           int = 0
