"""
Adapter: converts hokom() return dict -> HokomLinguisticClaimBundle.
This is the ONLY place hokom() output is consumed for Taaqol integration.
"""
from __future__ import annotations
import uuid
from .provider_models import HokomLinguisticClaimBundle
from .constitutional_contracts import ClaimProvenance, RealityDomain

HOKOM_ENGINE_VERSION = '2026.07.18'


def _build_provenance(result, surface, source_engine):
    """Build ClaimProvenance from hokom() result. Returns None if data is insufficient."""
    if not surface or not source_engine:
        return None
    claim_id = result.get("claim_id") or result.get("root_candidate_id") or ""
    if not claim_id:
        return None
    layer = "PRE_HOKOM"
    if result.get("phase5_result"):
        layer = "P5"
    elif result.get("phase4a_result"):
        layer = "P4A"
    return ClaimProvenance(
        claim_id=claim_id,
        source_identity=source_engine,
        source_type=source_engine,
        originating_layer=layer,
        carrier=surface,
        preserved_surface=surface,
        domain=RealityDomain.MORPHOLOGICAL,
        transformation_history=tuple(result.get("trace_ids", ())),
    )


def bundle_from_hokom_result(result: dict, token_id: str | None = None) -> HokomLinguisticClaimBundle:
    """
    Build a typed HokomLinguisticClaimBundle from a hokom() return dict.
    Never returns raw dict. Always returns typed bundle.
    """
    surface = result.get('original', '') or result.get('input_surface', '')
    normalized = result.get('normalized_surface', surface)

    # Root claim
    root_candidate = result.get('root_candidate')
    root_claim = root_candidate

    # Wazn claim
    phase4a = result.get('phase4a_result')
    wazn_claim = phase4a

    # Form/Bab claim
    phase4b = result.get('phase4b_result')
    form_claim = phase4b

    # Masdar claim
    phase4c = result.get('phase4c_result')
    masdar_claim = phase4c

    # Mushtaqat
    phase4d = result.get('phase4d_result')
    mushtaq_claims = (phase4d,) if phase4d else ()

    # Inflection
    phase5 = result.get('phase5_result')
    inflection_claim = phase5

    # Attachment
    attachment = result.get('attachment')
    attachment_claims = (attachment,) if attachment else ()

    # Evidence, trace, residuals
    evidence_ids = tuple(result.get('evidence_ids', ()))
    trace_ids = tuple(result.get('trace_ids', ()))
    active_residuals = tuple(result.get('active_residuals', ()))
    resolved_residuals = tuple(result.get('resolved_residuals', ()))

    # Collect from phases if top-level missing
    if not evidence_ids:
        collected = []
        for phase in [phase4a, phase4b, phase4c, phase4d, phase5]:
            if phase and hasattr(phase, 'evidence_ids'):
                collected.extend(phase.evidence_ids)
        evidence_ids = tuple(dict.fromkeys(collected))  # dedup, preserve order

    if not trace_ids:
        collected = []
        for phase in [phase4a, phase4b, phase4c, phase4d, phase5]:
            if phase and hasattr(phase, 'trace_ids'):
                collected.extend(phase.trace_ids)
        trace_ids = tuple(dict.fromkeys(collected))

    if not active_residuals:
        collected = []
        for phase in [phase4a, phase4b, phase4c, phase4d, phase5]:
            if phase and hasattr(phase, 'residual_codes'):
                collected.extend(phase.residual_codes)
        active_residuals = tuple(dict.fromkeys(collected))

    # Domain directive
    verdict = result.get('verdict', 'DEFER')
    if verdict in {'ACCEPT', 'LICENSED', 'COMPLETE'}:
        domain_directive = 'ACCEPT'
    elif verdict in {'BLOCK', 'BLOCKED', 'ILLEGAL'}:
        domain_directive = 'BLOCK'
    elif verdict in {'NOT_APPLICABLE'}:
        domain_directive = 'NOT_APPLICABLE'
    else:
        domain_directive = 'DEFER'

    # B-02 / B-03 fix: lexical_class and part_of_speech must come from the
    # canonical word class engine result, not from pre_root.morphology_path.
    # pre_root.morphology_path is a PIPELINE ROUTING value (verbal_root_path,
    # nominal_morphology_path, …), not a linguistic word class label.
    lexical_class = None
    part_of_speech = None
    word_class_result = result.get('word_class_result')
    if word_class_result is not None:
        # B-02: lexical_class = ISM_subclass or top-level word class
        _wc_subclass = getattr(word_class_result, 'subclass', None)
        _wc_class = getattr(word_class_result, 'word_class', None)
        if _wc_subclass is not None:
            lexical_class = str(_wc_subclass.value) if hasattr(_wc_subclass, 'value') else str(_wc_subclass)
        elif _wc_class is not None:
            lexical_class = str(_wc_class.value) if hasattr(_wc_class, 'value') else str(_wc_class)
        # B-03: part_of_speech = canonical top-level ISM / FI3L / HARF
        if _wc_class is not None:
            part_of_speech = str(_wc_class.value) if hasattr(_wc_class, 'value') else str(_wc_class)
    else:
        # Fallback to pre_root when word class engine did not run (should not
        # happen for normal tokens but keeps old behaviour for edge cases).
        pre_root = result.get('pre_root')
        if pre_root:
            if hasattr(pre_root, 'morphology_path'):
                lexical_class = str(pre_root.morphology_path.value) if hasattr(pre_root.morphology_path, 'value') else str(pre_root.morphology_path)
            if hasattr(pre_root, 'pos'):
                part_of_speech = str(pre_root.pos) if pre_root.pos else None

    # Source engine
    source_engine = 'HOKOM_ROOT_ENGINE'
    aug = result.get('augmented_analysis')
    if aug:
        source_engine = 'HOKOM_AUGMENTED_ENGINE'

    # Refined host
    refined_host = result.get('canonical_surface') or result.get('normalized_surface')

    provenance = _build_provenance(result, surface, source_engine)
    return HokomLinguisticClaimBundle(
        claim_id=f'hokom:{token_id or uuid.uuid4().hex[:12]}:{surface}',
        token_id=token_id or uuid.uuid4().hex[:16],
        original_surface=surface,
        normalized_surface=normalized,
        refined_host=refined_host,
        lexical_class=lexical_class,
        part_of_speech=part_of_speech,
        root_claim=root_claim,
        wazn_claim=wazn_claim,
        form_claim=form_claim,
        masdar_claim=masdar_claim,
        mushtaq_claims=mushtaq_claims,
        inflection_claim=inflection_claim,
        attachment_claims=attachment_claims,
        domain_directive=domain_directive,
        source_engine=source_engine,
        evidence_ids=evidence_ids,
        trace_ids=trace_ids,
        active_residuals=active_residuals,
        resolved_residuals=resolved_residuals,
        catalog_versions=(),
        engine_version=HOKOM_ENGINE_VERSION,
        provenance=provenance,
    )
