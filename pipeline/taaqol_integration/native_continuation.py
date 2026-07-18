"""
Native Taaqol vertical continuation after admission.
Uses actual Taaqol core API (SlotGraph, Gamma, TransitionGate).

STOP RULE (constitutionally mandated):
  A single token cannot produce a binary RelationCandidate.
  RelationCandidate requires 2+ ContractableUnitGeometry instances.
  Vertical continuation STOPS before RelationCandidate stage.

DEFERRED weight-layer stages (require Hokom pipeline integration):
  - DalOnly: requires LicensingBoundaryVerdict (weight/licensing_boundary PR-14)
  - VerbalMadlul: requires DalOnlyCandidate
  - ContractableUnit: requires VerbalMadlulCandidate
  These stages bypass Hokom's morphology layer -- Hokom produces claim bundles,
  not LicensingBoundaryVerdict objects.

CURRENT IMPLEMENTATION:
  Stage 0 (HOKOM_ADMITTED_DOMAIN_CLAIM) is COMPLETE -- done in admission_gate.py.
  Stages 1-3 (DalOnly, VerbalMadlul, ContractableUnit) are DEFERRED --
  require weight-layer input objects Hokom does not produce.
  Stage 4+ (RelationCandidate onwards) are FORBIDDEN for single token.
"""
from __future__ import annotations

import sys
import enum as _enum_module

from .provider_models import HokomTaaqolAdmissionResult, TaaqolVerticalContinuationResult
from .native_stage_registry import NATIVE_STAGE_REGISTRY, get_forbidden_stages, get_deferred_stages

# Determine if native core is accessible
_NATIVE_CORE_AVAILABLE = False
try:
    from taaqqul_slot_geometry.core.rank_lattice import Rank
    _NATIVE_CORE_AVAILABLE = True
except Exception:
    pass

# The stop point for single-token analysis:
# Stage 4 (RelationCandidate) is constitutionally forbidden.
# Stages 1-3 are DEFERRED pending weight-layer integration.
_SINGLE_TOKEN_STOP_STAGE = 'RelationCandidate'
_SINGLE_TOKEN_STOP_REASON = (
    'Constitutional stop: single token cannot produce binary RelationCandidate '
    '(requires 2+ ContractableUnitGeometry instances -- docs/11 §1, weight/relation_candidate.py). '
    'Stages 1-3 (DalOnly, VerbalMadlul, ContractableUnit) are DEFERRED: '
    'require LicensingBoundaryVerdict from weight/licensing_boundary PR-14, '
    'which Hokom does not produce.'
)


def continue_vertical(admission: HokomTaaqolAdmissionResult) -> TaaqolVerticalContinuationResult:
    """
    Continue Taaqol vertical pipeline after successful admission.

    For a single token, the continuation result is:
    - Stage 0 (HOKOM_ADMITTED_DOMAIN_CLAIM): COMPLETED in admission_gate
    - Stages 1-3 (DalOnly, VerbalMadlul, ContractableUnit): DEFERRED
    - Stage 4+ (RelationCandidate, RelationClosure, Ifadah, Hukm): FORBIDDEN
    """
    if admission.verdict != 'APPROVED':
        return TaaqolVerticalContinuationResult(
            claim_id=admission.claim_id,
            admission=admission,
            native_stage_results=(),
            highest_completed_stage=None,
            stop_stage='ADMISSION',
            stop_reason=f'admission verdict: {admission.verdict} -- cannot continue',
            constitutional_rank=None,
            gate_verdicts=(),
            active_residuals=admission.active_residuals,
            resolved_residuals=admission.resolved_residuals,
            audited_output=None,
        )

    # Stage 0 is already complete (admission gate ran SlotGraph + Gamma + TransitionGate)
    stage_0_result = (
        'HOKOM_ADMITTED_DOMAIN_CLAIM',
        {
            'status': 'COMPLETE',
            'gamma_result': admission.gamma_result,
            'taaqol_rank': admission.taaqol_rank,
            'gate_verdict': admission.gate_verdict,
        }
    )

    # Stages 1-3: DEFERRED -- weight-layer objects not available from Hokom
    deferred_stages = get_deferred_stages()
    weight_layer_stages = [s for s in deferred_stages if s.vertical_position in (1, 2, 3)]
    deferred_results = tuple(
        (s.stage_name, {'status': 'DEFERRED', 'reason': s.deferred_reason})
        for s in weight_layer_stages
    )

    # Stage 4+: FORBIDDEN for single token
    forbidden_stages = get_forbidden_stages()
    forbidden_results = tuple(
        (s.stage_name, {'status': 'FORBIDDEN', 'reason': s.deferred_reason})
        for s in forbidden_stages
        if s.vertical_position <= 10
    )

    # Constitutional rank: HYPOTHESIS (the admission gate's granted rank)
    constitutional_rank = admission.taaqol_rank  # e.g. 'Rank.HYPOTHESIS'

    return TaaqolVerticalContinuationResult(
        claim_id=admission.claim_id,
        admission=admission,
        native_stage_results=(stage_0_result,) + deferred_results + forbidden_results,
        highest_completed_stage='HOKOM_ADMITTED_DOMAIN_CLAIM',
        stop_stage=_SINGLE_TOKEN_STOP_STAGE,
        stop_reason=_SINGLE_TOKEN_STOP_REASON,
        constitutional_rank=constitutional_rank,
        gate_verdicts=(
            (admission.gate_verdict, 'HOKOM_MORPHOLOGY_ADMISSION_GATE'),
        ),
        active_residuals=admission.active_residuals,
        resolved_residuals=admission.resolved_residuals,
        audited_output=None,  # AnswerAudit requires ModelClient -- DEFERRED
    )
