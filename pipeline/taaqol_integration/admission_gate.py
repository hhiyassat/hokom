"""
Admission gate: uses native Taaqol SlotGraph, Gamma, ResidualPolicy,
EvidenceContract, and TransitionGate for claim admission.

Step 6 IMPLEMENTATION is COMPLETE. Step 6 ACTIVATION requires Python 3.11+.
Native taaqqul_slot_geometry uses StrEnum (enum.StrEnum, Python 3.11+).
No backport. No shim. Upgrade the Hokom runtime to Python 3.11 to activate.

Architecture:
  Steps 1-5: Hokom-side validation (bundle, provider, identity, evidence, residuals)
  Step 6: Native Taaqol SlotGraph -> Gamma -> EvidenceContract -> TransitionGate

Output ceiling: Layer.SLOT (ADMITTED_DOMAIN_CLAIM).
No CANDIDATE, no CERTIFICATE, no RelationClosure, no Meaning.
A single token cannot produce a binary RelationCandidate.
"""
from __future__ import annotations

import sys
import uuid

from .provider_models import (
    HokomLinguisticClaimBundle,
    HokomTaaqolAdmissionResult,
    ProviderAdmissionResult,
)
from .evidence_adapter import map_evidence
from .residual_adapter import map_residuals, ClassifiedResidual
from .identity_adapter import verify_identity_continuity
from .provider_guard import validate_bundle

# Native Taaqol requires Python 3.11+ (uses StrEnum from stdlib enum module).
# No shim. No backport. No conditional injection.
# Approved resolution: upgrade Hokom runtime to Python 3.11.
_RUNTIME = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
_NATIVE_AVAILABLE = False
_NATIVE_ERROR: str | None = None

try:
    from taaqqul_slot_geometry.core.slot_graph import (
        SlotGraph, Center, Slot, SlotBoundary, OpeningPolicy, SlotState,
        OutputBoundary, GenerationSource, Layer, TraceRef, EntryBoundary,
    )
    from taaqqul_slot_geometry.core.gamma import gamma
    from taaqqul_slot_geometry.core.rank_lattice import Rank, RankLattice
    from taaqqul_slot_geometry.core.residual_policy import (
        Residual, ResidualKind, ResidualPolicy,
    )
    from taaqqul_slot_geometry.core.evidence_contract import EvidenceContract, EvidenceSource
    from taaqqul_slot_geometry.core.transition_gate import TransitionGate
    from taaqqul_slot_geometry.core.closure_state import ClosureState
    from taaqqul_slot_geometry.core.failure_taxonomy import FailureCode
    from taaqqul_slot_geometry.core.transition_state import TransitionState

    _NATIVE_AVAILABLE = True
except Exception as _e:
    _NATIVE_ERROR = str(_e)


# The first lawful native entry for a Hokom morphological claim.
# A single token at the SLOT layer = ADMITTED_DOMAIN_CLAIM.
# NOT CANDIDATE (requires binary relation), NOT CERTIFICATE.
NATIVE_ADMISSION_ENTRY_STAGE = 'HOKOM_ADMITTED_DOMAIN_CLAIM'

# Gate name used for all Hokom -> Taaqol admission transitions
HOKOM_ADMISSION_GATE_NAME = 'HOKOM_MORPHOLOGY_ADMISSION_GATE'

# Gate rank: HYPOTHESIS -- Hokom domain claim is hypothetical without full semantic closure
HOKOM_GATE_RANK = None  # Set to Rank.HYPOTHESIS after import succeeds

if _NATIVE_AVAILABLE:
    HOKOM_GATE_RANK = Rank.HYPOTHESIS


def admit_claim(
    bundle: HokomLinguisticClaimBundle,
    provider_admission: ProviderAdmissionResult,
) -> HokomTaaqolAdmissionResult:
    """
    Admit a Hokom linguistic claim into Taaqol using native constitutional components.

    Steps 1-5 are Hokom-side validation.
    Step 6 is native Taaqol SlotGraph/Gamma/Gate.
    """
    # Step 0: BLOCK directive is fatal -- refuse immediately before any further processing
    if bundle.domain_directive == 'BLOCK':
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='BLOCKED',
            provider_admission=provider_admission,
            identity_continuity='BLOCK',
            evidence_verdict='MISSING',
            residual_verdict='BLOCKING',
            gate_verdict='ILLEGAL',
            native_entry_stage=None,
            stop_reason='domain_directive=BLOCK: admission refused at source',
            trace_refs=bundle.trace_ids,
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )

    # Step 1: Validate bundle
    bundle_violations = validate_bundle(bundle)
    if bundle_violations:
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='REJECTED',
            provider_admission=provider_admission,
            identity_continuity='BLOCK',
            evidence_verdict='MISSING',
            residual_verdict='BLOCKING',
            gate_verdict='ILLEGAL',
            native_entry_stage=None,
            stop_reason=f'bundle validation failed: {bundle_violations}',
            trace_refs=(),
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )

    # Step 2: Provider admission required
    if not provider_admission.admitted:
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='REJECTED',
            provider_admission=provider_admission,
            identity_continuity='BLOCK',
            evidence_verdict='MISSING',
            residual_verdict='BLOCKING',
            gate_verdict='ILLEGAL',
            native_entry_stage=None,
            stop_reason=f'provider not admitted: {provider_admission.violations}',
            trace_refs=(),
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )

    # Step 3: Identity continuity
    identity = verify_identity_continuity(bundle)
    if identity.verdict == 'BLOCK':
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='BLOCKED',
            provider_admission=provider_admission,
            identity_continuity='BLOCK',
            evidence_verdict='MISSING',
            residual_verdict='BLOCKING',
            gate_verdict='ILLEGAL',
            native_entry_stage=None,
            stop_reason=f'identity continuity blocked: {identity.violations}',
            trace_refs=(),
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )

    # Step 4: Evidence mapping
    evidence = map_evidence(bundle)

    # Step 5: Residual mapping
    residuals = map_residuals(bundle.active_residuals, bundle.resolved_residuals)
    if residuals.verdict == 'HIDDEN':
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='REJECTED',
            provider_admission=provider_admission,
            identity_continuity=identity.verdict,
            evidence_verdict=evidence.verdict,
            residual_verdict='HIDDEN',
            gate_verdict='ILLEGAL',
            native_entry_stage=None,
            stop_reason='hidden residual detected -- contract refusal',
            trace_refs=(),
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )
    if residuals.verdict == 'BLOCKING':
        blocking_codes = [c.code for c in residuals.classified if c.classification == 'BLOCKING']
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='BLOCKED',
            provider_admission=provider_admission,
            identity_continuity=identity.verdict,
            evidence_verdict=evidence.verdict,
            residual_verdict='BLOCKING',
            gate_verdict='ILLEGAL',
            native_entry_stage=None,
            stop_reason=f'blocking residual: {blocking_codes}',
            trace_refs=(),
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )

    # Step 6: Native Taaqol SlotGraph / Gamma / Gate
    return _try_native_admission(bundle, evidence, residuals, identity, provider_admission)


def _try_native_admission(
    bundle: HokomLinguisticClaimBundle,
    evidence,
    residuals,
    identity,
    provider_admission: ProviderAdmissionResult,
) -> HokomTaaqolAdmissionResult:
    """
    Step 6: Build SlotGraph, run Gamma, build EvidenceContract, run TransitionGate.
    Returns APPROVED, DEFERRED, or BLOCKED depending on gate verdict.

    If native Taaqol is not importable (e.g. first boot without backport),
    returns DEFERRED with a documented gap.
    """
    if not _NATIVE_AVAILABLE:
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='DEFERRED',
            provider_admission=provider_admission,
            identity_continuity=identity.verdict,
            evidence_verdict=evidence.verdict,
            residual_verdict=residuals.verdict,
            gate_verdict='PENDING',
            native_entry_stage=None,
            stop_reason=(
                f'DEFERRED: native taaqqul_slot_geometry not importable on {_RUNTIME}. '
                f'Error: {_NATIVE_ERROR}. '
                'Required: upgrade Hokom runtime to Python 3.11.'
            ),
            trace_refs=bundle.trace_ids,
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )

    # Runtime assertion: native components require 3.11 OR strenum backport
    import enum as _enum
    if not hasattr(_enum, 'StrEnum'):
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='DEFERRED',
            provider_admission=provider_admission,
            identity_continuity=identity.verdict,
            evidence_verdict=evidence.verdict,
            residual_verdict=residuals.verdict,
            gate_verdict='PENDING',
            native_entry_stage=None,
            stop_reason='DEFERRED: StrEnum not available in enum module. Cannot run native Taaqol.',
            trace_refs=bundle.trace_ids,
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )

    try:
        return _build_and_run_native_graph(bundle, evidence, residuals, identity, provider_admission)
    except Exception as e:
        # Native execution failed for a reason other than missing import
        return HokomTaaqolAdmissionResult(
            claim_id=bundle.claim_id,
            verdict='DEFERRED',
            provider_admission=provider_admission,
            identity_continuity=identity.verdict,
            evidence_verdict=evidence.verdict,
            residual_verdict=residuals.verdict,
            gate_verdict='PENDING',
            native_entry_stage=NATIVE_ADMISSION_ENTRY_STAGE,
            stop_reason=f'native execution error: {type(e).__name__}: {e}',
            trace_refs=bundle.trace_ids,
            active_residuals=bundle.active_residuals,
            resolved_residuals=bundle.resolved_residuals,
            taaqol_rank=None,
            gamma_result=None,
        )


def _build_and_run_native_graph(
    bundle: HokomLinguisticClaimBundle,
    evidence,
    residuals,
    identity,
    provider_admission: ProviderAdmissionResult,
) -> HokomTaaqolAdmissionResult:
    """
    Actually build the SlotGraph and run Gamma + TransitionGate.
    Called only when native components are confirmed importable.
    """
    # --- BUILD CENTER ---
    # Center identity = the token surface (immutable identity claim)
    trace_anchor = f'hokom:{bundle.token_id}:{bundle.claim_id}'
    trace_ref = TraceRef(anchor=trace_anchor, kind='HOKOM_MORPHOLOGY_CLAIM')
    center = Center(
        identity_claim=bundle.original_surface or bundle.normalized_surface or bundle.claim_id,
        domain='ARABIC_LINGUISTIC_CLAIM',
        scope='HOKOM_TO_TAAQOL_ADMISSION',
        trace_ref=trace_ref,
    )

    # --- BUILD SLOTS ---
    slots = _build_slots_from_bundle(bundle)

    # --- BUILD BOUNDARY ---
    graph_boundary = SlotBoundary(
        domain='ARABIC_LINGUISTIC_CLAIM',
        scope='HOKOM_TO_TAAQOL_ADMISSION',
        refusal_codes=(
            FailureCode.IDENTITY_BROKEN,
            FailureCode.BOUNDARY_MISSING,
            FailureCode.DOMAIN_MISSING,
        ),
        licensed_operations=('admit_domain_claim',),
    )

    # --- BUILD RESIDUALS ---
    native_residuals = _build_native_residuals(residuals)

    # --- DETERMINE RANK ---
    # Hokom domain claim enters at HYPOTHESIS rank:
    # - Not LICENSED (that requires gate passage)
    # - Not ZERO (we have evidence)
    # - HYPOTHESIS = evidential strength appropriate for a morphological hypothesis
    input_rank = Rank.HYPOTHESIS

    # If we have strong evidence (wazn + bab both accepted), allow LICENSED
    # but cap at HYPOTHESIS for admission (gate can only meet, not promote)
    if evidence.verdict == 'SUFFICIENT' and bundle.domain_directive == 'ACCEPT':
        input_rank = Rank.HYPOTHESIS  # admission ceiling, gate decide sets output

    # --- OUTPUT BOUNDARY ---
    # Output ceiling: Layer.SLOT = ADMITTED_DOMAIN_CLAIM
    # NOT Layer.CANDIDATE (requires binary relation)
    # NOT Layer.CERTIFICATE (requires full ontological chain)
    output_boundary = OutputBoundary(
        declared_layer=Layer.SLOT,
        output_layer=Layer.SLOT,
    )

    # --- ENTRY BOUNDARY (required for DECLARED_ENTRY source) ---
    entry_boundary = EntryBoundary(
        declared_entry_kind='ARABIC_MORPHOLOGICAL_CLAIM',
        representation_status='REPRESENTATIONAL',
        ontological_status='NOT_ONTOLOGICAL_ORIGIN',
        sound_status='NOT_SOUND',
        meaning_status='NOT_MEANING',
        prior_trace_status='TRACE_PRESERVED',
        produces_only='TextTraceCandidate',
    )

    # --- BUILD SLOT GRAPH ---
    graph = SlotGraph(
        center=center,
        slots=slots,
        boundary=graph_boundary,
        residuals=native_residuals,
        rank=input_rank,
        output_boundary=output_boundary,
        generation_source=GenerationSource.DECLARED_ENTRY,
        entry_boundary=entry_boundary,
    )

    # --- RUN GAMMA ---
    gamma_result = gamma(graph)

    # --- BUILD EVIDENCE CONTRACT ---
    ev_sources = _build_evidence_sources(bundle, evidence, trace_ref)
    evidence_contract = EvidenceContract(sources=ev_sources)

    # --- RUN TRANSITION GATE ---
    # Gate rank: HYPOTHESIS (admission gate cannot promote beyond morphological hypothesis)
    gate = TransitionGate(
        name=HOKOM_ADMISSION_GATE_NAME,
        gate_rank=Rank.HYPOTHESIS,
    )
    gate_verdict = gate.decide(graph, Layer.SLOT, evidence_contract)

    # --- MAP GATE VERDICT TO ADMISSION RESULT ---
    return _map_gate_verdict_to_admission(
        bundle=bundle,
        provider_admission=provider_admission,
        identity=identity,
        evidence=evidence,
        residuals=residuals,
        gamma_result=gamma_result,
        gate_verdict=gate_verdict,
        graph=graph,
    )


def _build_slots_from_bundle(bundle: HokomLinguisticClaimBundle) -> tuple:
    """Build SlotGraph slots from bundle fields."""
    slots = []

    # Slot 1: provider identity
    if bundle.source_engine:
        slots.append(_make_filled_slot(
            name='provider_identity',
            value=bundle.source_engine,
            allowed={'HOKOM_ROOT_ENGINE', 'HOKOM_AUGMENTED_ENGINE', bundle.source_engine},
            domain='ARABIC_LINGUISTIC_CLAIM',
            scope='PROVIDER_IDENTITY',
            required=True,
        ))
    else:
        slots.append(_make_empty_slot(
            name='provider_identity',
            domain='ARABIC_LINGUISTIC_CLAIM',
            scope='PROVIDER_IDENTITY',
            required=True,
        ))

    # Slot 2: original surface (if available)
    surface = bundle.original_surface or bundle.normalized_surface
    if surface:
        slots.append(_make_filled_slot(
            name='original_surface',
            value=surface,
            allowed={surface},
            domain='ARABIC_LINGUISTIC_CLAIM',
            scope='SURFACE_IDENTITY',
            required=True,
        ))

    # Slot 3: domain directive
    if bundle.domain_directive:
        slots.append(_make_filled_slot(
            name='domain_directive',
            value=bundle.domain_directive,
            allowed={'ACCEPT', 'DEFER', 'BLOCK', 'NOT_APPLICABLE'},
            domain='ARABIC_LINGUISTIC_CLAIM',
            scope='DOMAIN_DIRECTIVE',
            required=True,
        ))

    # Slot 4: stage coverage (which phases ran)
    stage_flags = []
    if bundle.wazn_claim is not None:
        stage_flags.append('phase4a')
    if bundle.form_claim is not None:
        stage_flags.append('phase4b')
    if bundle.masdar_claim is not None:
        stage_flags.append('phase4c')
    if bundle.mushtaq_claims:
        stage_flags.append('phase4d')
    if bundle.inflection_claim is not None:
        stage_flags.append('phase5')

    stage_value = ','.join(stage_flags) if stage_flags else 'none'
    slots.append(_make_filled_slot(
        name='stage_coverage',
        value=stage_value,
        allowed={stage_value, 'phase4a', 'phase4b', 'phase4c', 'phase4d', 'phase5',
                 'phase4a,phase4b', 'phase4a,phase4b,phase4c', 'phase4a,phase4b,phase4c,phase4d',
                 'phase4a,phase4b,phase4c,phase4d,phase5', 'none', stage_value},
        domain='ARABIC_LINGUISTIC_CLAIM',
        scope='STAGE_COVERAGE',
        required=False,
    ))

    return tuple(slots)


def _make_filled_slot(
    name: str,
    value: str,
    allowed: set,
    domain: str,
    scope: str,
    required: bool,
) -> 'Slot':
    boundary = SlotBoundary(
        domain=domain,
        scope=scope,
        refusal_codes=(FailureCode.IDENTITY_BROKEN,),
    )
    opening = OpeningPolicy(allowed_potentials=frozenset(s for s in allowed if s))
    return Slot(
        name=name,
        value_state=SlotState.FILLED,
        boundary=boundary,
        opening=opening,
        required=required,
        value=value,
    )


def _make_empty_slot(name: str, domain: str, scope: str, required: bool) -> 'Slot':
    boundary = SlotBoundary(
        domain=domain,
        scope=scope,
        refusal_codes=(FailureCode.IDENTITY_BROKEN,),
    )
    opening = OpeningPolicy(allowed_potentials=frozenset({'UNKNOWN', 'EMPTY_PROVIDER'}))
    return Slot(
        name=name,
        value_state=SlotState.EMPTY,
        boundary=boundary,
        opening=opening,
        required=required,
        value=None,
    )


def _build_native_residuals(residuals) -> tuple:
    """Convert Hokom residual classifications to native Taaqol Residual objects."""
    native = []
    cls_map = {
        'BLOCKING': ResidualKind.BLOCKING,
        'DEFERRABLE': ResidualKind.DEFERRABLE,
        'NON_BLOCKING': ResidualKind.NON_BLOCKING,
        'EXPLANATORY': ResidualKind.EXPLANATORY,
        'HIDDEN_FORBIDDEN': ResidualKind.HIDDEN_FORBIDDEN,
    }
    for cr in residuals.classified:
        if not cr.is_active:
            continue  # only active residuals go into the graph
        kind = cls_map.get(cr.classification, ResidualKind.NON_BLOCKING)
        native.append(Residual(
            name=cr.code,
            kind=kind,
            visible=True,
            note=f'hokom_residual:{cr.code}',
        ))
    return tuple(native)


def _build_evidence_sources(bundle: HokomLinguisticClaimBundle, evidence, trace_ref: 'TraceRef') -> tuple:
    """
    Build native EvidenceSource objects from the bundle's evidence records.
    Each evidence_id becomes one EvidenceSource with a rank proportional to its type.
    """
    if not _NATIVE_AVAILABLE:
        return ()

    sources = []
    rank_map = {
        'wazn_pattern_evidence': Rank.LICENSED,
        'form_catalog_evidence': Rank.HYPOTHESIS,
        'root_catalog_evidence': Rank.STRONG,
        'root_restoration_evidence': Rank.HYPOTHESIS,
        'masdar_derivation_evidence': Rank.CANDIDATE,
        'mushtaq_derivation_evidence': Rank.CANDIDATE,
        'inflection_paradigm_evidence': Rank.TRACE,
        'source_path_evidence': Rank.TRACE,
        'negative_contradiction_evidence': Rank.HYPOTHESIS,
        'root_slot_alignment': Rank.CANDIDATE,
        'attachment_evidence': Rank.TRACE,
    }

    seen_ids: set[str] = set()
    for er in evidence.records:
        if er.evidence_id in seen_ids:
            continue
        # Skip synthetic ACCEPT-directive evidence:
        # The ACCEPT directive is a Hokom-internal decision, not a
        # constitutional evidence source. Only real evidence_ids from the
        # bundle (from catalog, wazn, bab, masdar matches) count.
        if er.evidence_id.startswith('hokom:domain_directive:ACCEPT:'):
            continue
        seen_ids.add(er.evidence_id)
        ev_rank = rank_map.get(er.evidence_type, Rank.TRACE)
        ev_trace = TraceRef(
            anchor=f'evidence:{er.evidence_id}',
            kind=er.evidence_type,
        )
        sources.append(EvidenceSource(
            name=er.evidence_id[:100],  # cap length
            kind=er.evidence_type,
            rank=ev_rank,
            trace_ref=ev_trace,
        ))

    return tuple(sources)


def _map_gate_verdict_to_admission(
    bundle: HokomLinguisticClaimBundle,
    provider_admission: ProviderAdmissionResult,
    identity,
    evidence,
    residuals,
    gamma_result,
    gate_verdict,
    graph: 'SlotGraph',
) -> HokomTaaqolAdmissionResult:
    """
    Map native TransitionVerdict to HokomTaaqolAdmissionResult.

    TransitionState values: APPROVED, DEFERRED, REFUSED, FORBIDDEN, INVALID
    """
    tv_state = gate_verdict.state  # TransitionState enum value

    # Map TransitionState -> admission verdict string
    state_str = str(tv_state)
    if 'APPROVED' in state_str:
        verdict = 'APPROVED'
        gate_v = 'LEGAL'
        stop_reason = None
    elif 'DEFERRED' in state_str:
        verdict = 'DEFERRED'
        gate_v = 'PENDING'
        fc = gate_verdict.failure_code
        stop_reason = f'gate deferred: {fc.value if fc else "unknown"}'
    elif 'FORBIDDEN' in state_str:
        verdict = 'FORBIDDEN_LEAP'
        gate_v = 'ILLEGAL'
        fc = gate_verdict.failure_code
        stop_reason = f'forbidden: {fc.value if fc else "unknown"}'
    elif 'REFUSED' in state_str:
        verdict = 'BLOCKED'
        gate_v = 'ILLEGAL'
        fc = gate_verdict.failure_code
        stop_reason = f'gate refused: {fc.value if fc else "unknown"}'
    else:
        verdict = 'DEFERRED'
        gate_v = 'PENDING'
        stop_reason = f'gate returned unknown state: {tv_state}'

    # Determine native entry stage
    native_entry = NATIVE_ADMISSION_ENTRY_STAGE if verdict == 'APPROVED' else None

    # Determine taaqol_rank: only set when the gate APPROVED the transition.
    # A DEFERRED or REFUSED gate returns granted_rank=ZERO which must not be
    # exposed as a rank claim -- taaqol_rank stays None for non-APPROVED verdicts.
    granted_rank = gate_verdict.granted_rank
    taaqol_rank_str = str(granted_rank) if (granted_rank is not None and verdict == 'APPROVED') else None

    # Gamma state string -- record for audit, but do not convert to stop_reason for APPROVED
    gamma_state_str = str(gamma_result.state)
    # PERFORATED_CLOSED is a valid closure for admission (non-blocking residuals present)
    # Only annotate stop_reason when verdict is not APPROVED
    valid_closure_states = (
        'ClosureState.MINIMALLY_CLOSED', 'MINIMALLY_CLOSED',
        'ClosureState.PERFORATED_CLOSED', 'PERFORATED_CLOSED',
    )
    if stop_reason is None and gamma_state_str not in valid_closure_states:
        stop_reason = f'gamma state: {gamma_state_str}'

    return HokomTaaqolAdmissionResult(
        claim_id=bundle.claim_id,
        verdict=verdict,
        provider_admission=provider_admission,
        identity_continuity=identity.verdict,
        evidence_verdict=evidence.verdict,
        residual_verdict=residuals.verdict,
        gate_verdict=gate_v,
        native_entry_stage=native_entry,
        stop_reason=stop_reason,
        trace_refs=bundle.trace_ids,
        active_residuals=bundle.active_residuals,
        resolved_residuals=bundle.resolved_residuals,
        taaqol_rank=taaqol_rank_str,
        gamma_result=gamma_state_str,
    )
