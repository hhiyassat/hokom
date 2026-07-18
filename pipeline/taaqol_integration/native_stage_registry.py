"""
Native Taaqol Stage Registry -- documents each stage and its requirements.

Updated: Python 3.11 migration batch (R16-R17).
Status: Native core (SlotGraph, Gamma, TransitionGate) is NOW accessible
via strenum backport on Python 3.10. Weight layer stages remain DEFERRED
pending Hokom-side input pipeline integration.

Source: vendor/Taaqol-GPT/src/taaqqul_slot_geometry/weight/
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class NativeStageEntry:
    stage_name: str
    module: str
    function: str
    input_type: str
    required_predecessor: str
    required_evidence: str
    required_gate: str
    required_rank: str
    output_type: str
    hokom_eligibility: str   # ELIGIBLE | ELIGIBLE_WITH_BACKPORT | DEFERRED | FORBIDDEN
    deferred_reason: str | None
    hokom_bundle_qualifies: bool
    vertical_position: int


NATIVE_STAGE_REGISTRY: tuple[NativeStageEntry, ...] = (
    NativeStageEntry(
        stage_name='CoreSlotGraph_Gamma',
        module='taaqqul_slot_geometry.core.slot_graph + .gamma',
        function='SlotGraph() + gamma()',
        input_type='HokomLinguisticClaimBundle',
        required_predecessor='None (entry point)',
        required_evidence='evidence_ids from Phase4A/4B/4C/4D/5',
        required_gate='TransitionGate(HOKOM_MORPHOLOGY_ADMISSION_GATE, Rank.HYPOTHESIS)',
        required_rank='HYPOTHESIS (input); HYPOTHESIS (output ceiling)',
        output_type='GammaResult + TransitionVerdict -> HokomTaaqolAdmissionResult',
        hokom_eligibility='ELIGIBLE_WITH_BACKPORT',
        deferred_reason=None,
        hokom_bundle_qualifies=True,
        vertical_position=0,
    ),
    NativeStageEntry(
        stage_name='DalOnly',
        module='taaqqul_slot_geometry.weight.dal_only',
        function='prove_dal',
        input_type='LicensingBoundaryVerdict (from licensing_boundary module)',
        required_predecessor='LicensingBoundaryVerdict (PR-14 output)',
        required_evidence='syllable/phoneme level evidence',
        required_gate='HOKOM_MORPHOLOGY_ADMISSION_GATE or equivalent',
        required_rank='DAL_BOUNDARY_RANK_CEILING (same as LICENSE_BOUNDARY_RANK_CEILING)',
        output_type='DalOnlyCandidate / DalBoundaryVerdict',
        hokom_eligibility='DEFERRED',
        deferred_reason='Requires LicensingBoundaryVerdict from weight/licensing_boundary PR-14; Hokom does not produce this object',
        hokom_bundle_qualifies=False,
        vertical_position=1,
    ),
    NativeStageEntry(
        stage_name='VerbalMadlul',
        module='taaqqul_slot_geometry.weight.verbal_madlul',
        function='prove_verbal_madlul',
        input_type='DalOnlyCandidate',
        required_predecessor='DalOnlyCandidate (Stage 1 output)',
        required_evidence='phoneme/morpheme evidence from DalOnly',
        required_gate='VerbalMadlulGate',
        required_rank='HYPOTHESIS or above',
        output_type='VerbalMadlulCandidate / VerbalMadlulBoundaryVerdict',
        hokom_eligibility='DEFERRED',
        deferred_reason='Requires DalOnlyCandidate; Hokom bypasses the weight phoneme layer',
        hokom_bundle_qualifies=False,
        vertical_position=2,
    ),
    NativeStageEntry(
        stage_name='ContractableUnit',
        module='taaqqul_slot_geometry.weight.contractable_unit_geometry',
        function='prove_contractable_unit',
        input_type='VerbalMadlulCandidate',
        required_predecessor='VerbalMadlulCandidate (Stage 2 output)',
        required_evidence='verbal madlul evidence',
        required_gate='ContractableUnitGate',
        required_rank='HYPOTHESIS',
        output_type='ContractableUnitGeometry / ContractableUnitVerdict',
        hokom_eligibility='DEFERRED',
        deferred_reason='Requires VerbalMadlulCandidate; Hokom bypasses weight/verbal_madlul layer',
        hokom_bundle_qualifies=False,
        vertical_position=3,
    ),
    NativeStageEntry(
        stage_name='RelationCandidate',
        module='taaqqul_slot_geometry.weight.relation_candidate',
        function='prove_relation_candidate',
        input_type='ContractableUnitGeometry (two or more)',
        required_predecessor='Two ContractableUnitGeometry instances (binary)',
        required_evidence='two-unit relation evidence',
        required_gate='RelationGate',
        required_rank='LICENSED',
        output_type='RelationCandidate / RelationVerdict',
        hokom_eligibility='FORBIDDEN',
        deferred_reason='Single token cannot produce binary RelationCandidate (requires 2+ tokens with ContractableUnitGeometry)',
        hokom_bundle_qualifies=False,
        vertical_position=4,
    ),
    NativeStageEntry(
        stage_name='MufradDalalahClosure',
        module='taaqqul_slot_geometry.weight.mufrad_dalalah_closure',
        function='prove_mufrad_dalalah_closure',
        input_type='MufradDalalahClosureCandidate',
        required_predecessor='ContractableUnitGeometry (Stage 3)',
        required_evidence='dalalah evidence chain',
        required_gate='MufradDalalahGate',
        required_rank='STRONG',
        output_type='MufradDalalahClosureVerdict',
        hokom_eligibility='DEFERRED',
        deferred_reason='Requires ContractableUnitGeometry; Hokom bypasses weight layer',
        hokom_bundle_qualifies=False,
        vertical_position=5,
    ),
    NativeStageEntry(
        stage_name='RelationClosure',
        module='taaqqul_slot_geometry.weight.relation_closure',
        function='prove_relation_closure',
        input_type='RelationClosureCandidate (requires RelationCandidate)',
        required_predecessor='RelationCandidate (requires 2+ tokens)',
        required_evidence='relation closure evidence',
        required_gate='RelationClosureGate',
        required_rank='STRONG',
        output_type='RelationClosureVerdict',
        hokom_eligibility='FORBIDDEN',
        deferred_reason='Requires RelationCandidate which requires 2+ tokens; forbidden for single-token analysis',
        hokom_bundle_qualifies=False,
        vertical_position=6,
    ),
    NativeStageEntry(
        stage_name='Ifadah',
        module='taaqqul_slot_geometry.weight.ifadah_candidate',
        function='prove_ifadah_candidate',
        input_type='IfadahCandidate (requires RelationClosure)',
        required_predecessor='RelationClosure output',
        required_evidence='full sentence-level evidence',
        required_gate='IfadahGate',
        required_rank='STRONG',
        output_type='IfadahVerdict',
        hokom_eligibility='FORBIDDEN',
        deferred_reason='Ifadah requires RelationClosure which requires 2+ tokens',
        hokom_bundle_qualifies=False,
        vertical_position=7,
    ),
    NativeStageEntry(
        stage_name='Hukm',
        module='taaqqul_slot_geometry.weight.hukm_candidate',
        function='prove_hukm_candidate',
        input_type='HukmCandidate (requires Ifadah)',
        required_predecessor='Ifadah output',
        required_evidence='judgment-level evidence chain',
        required_gate='HukmGate',
        required_rank='CERTIFICATE',
        output_type='HukmVerdict',
        hokom_eligibility='FORBIDDEN',
        deferred_reason='Hukm requires Ifadah; forbidden for single token',
        hokom_bundle_qualifies=False,
        vertical_position=8,
    ),
    NativeStageEntry(
        stage_name='AnswerAudit',
        module='taaqqul_slot_geometry.audit.answer_audit',
        function='AnswerAudit.run',
        input_type='SlotGraph + EvidenceContract + ModelClient',
        required_predecessor='CoreSlotGraph_Gamma (Stage 0)',
        required_evidence='All evidence from Hokom bundle',
        required_gate='AuditGate (requires ModelClient)',
        required_rank='N/A (audit wrapper)',
        output_type='AuditedAnswer',
        hokom_eligibility='DEFERRED',
        deferred_reason='Requires ModelClient (external LLM); Hokom is not a ModelClient',
        hokom_bundle_qualifies=False,
        vertical_position=99,
    ),
)


def get_eligible_stages() -> tuple[NativeStageEntry, ...]:
    """Return stages that are ELIGIBLE (including with backport)."""
    return tuple(s for s in NATIVE_STAGE_REGISTRY
                 if s.hokom_eligibility in ('ELIGIBLE', 'ELIGIBLE_WITH_BACKPORT'))


def get_deferred_stages() -> tuple[NativeStageEntry, ...]:
    """Return stages deferred (not forbidden, but not yet reachable)."""
    return tuple(s for s in NATIVE_STAGE_REGISTRY if s.hokom_eligibility == 'DEFERRED')


def get_forbidden_stages() -> tuple[NativeStageEntry, ...]:
    """Return stages permanently forbidden for single-token analysis."""
    return tuple(s for s in NATIVE_STAGE_REGISTRY if s.hokom_eligibility == 'FORBIDDEN')


def first_lawful_native_entry_for_hokom() -> NativeStageEntry:
    """
    The first (and currently only) lawful native entry stage for a Hokom bundle.
    Stage 0: CoreSlotGraph_Gamma (admission at SLOT layer).
    """
    return NATIVE_STAGE_REGISTRY[0]
