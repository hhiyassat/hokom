"""
Claim projection: Hokom bundle fields → HokomClaimProjection.

HOKOM-TAAQOL-LIVE-INTEGRATION-01

Projection is pure (no Taaqol imports, no I/O, no random values).
All claim_ids are deterministic (content hash based).
Python 3.10+ compatible.
"""
from __future__ import annotations

import hashlib
from .models import HokomClaimProjection


def _deterministic_claim_id(surface: str, layer: str, value: str) -> str:
    """
    Deterministic claim ID from content hash.
    Same surface + layer + value → always same ID.
    No UUID, no random, no timestamp.
    """
    content = f'{surface}:{layer}:{value}'
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


def project_bundle_to_claim(
    bundle,
    claim_layer: str,
    *,
    hokom_commit: str = 'unknown',
    taaqol_commit: str = 'unknown',
) -> HokomClaimProjection:
    """
    Project a HokomLinguisticClaimBundle field to a HokomClaimProjection.

    claim_layer: 'P5_BOUNDARY' | 'ROOT' | 'PATTERN' | 'WORD_CLASS' |
                 'MASDAR' | 'MUSHTAQAT' | 'INFLECTION' | 'FINAL_TOKEN'
    """
    surface = getattr(bundle, 'original_surface', '') or ''
    normalized = getattr(bundle, 'normalized_surface', surface) or surface
    upstream_verdict = getattr(bundle, 'domain_directive', 'DEFER') or 'DEFER'
    source_engine = getattr(bundle, 'source_engine', 'HOKOM') or 'HOKOM'
    evidence_ids = tuple(getattr(bundle, 'evidence_ids', ()) or ())
    trace_ids = tuple(getattr(bundle, 'trace_ids', ()) or ())
    active_residuals = tuple(getattr(bundle, 'active_residuals', ()) or ())

    # Proposed value for this layer
    proposed_value = _extract_proposed_value(bundle, claim_layer)

    claim_id = _deterministic_claim_id(surface, claim_layer, proposed_value)

    provenance = f'hokom:{hokom_commit}:taaqol:{taaqol_commit}'

    return HokomClaimProjection(
        claim_id=claim_id,
        token_id=getattr(bundle, 'token_id', claim_id) or claim_id,
        original_surface=surface,
        normalized_surface=normalized,
        claim_layer=claim_layer,
        claim_kind=_claim_kind_for_layer(claim_layer),
        proposed_value=proposed_value,
        upstream_verdict=upstream_verdict,
        evidence_rank=_evidence_rank_for_layer(claim_layer, upstream_verdict),
        supporting_evidence=evidence_ids,
        contradictions=(),
        boundaries_crossed=_boundaries_crossed_for_layer(claim_layer),
        source_engine=source_engine,
        source_owner='HOKOM',
        upstream_trace=trace_ids,
        residuals=tuple(str(r) for r in active_residuals),
        provenance=provenance,
    )


def _extract_proposed_value(bundle, claim_layer: str) -> str:
    """Extract the proposed value for the given claim layer from bundle."""
    if claim_layer == 'P5_BOUNDARY':
        mabni = getattr(bundle, 'mabni_status', None) or getattr(bundle, 'lexical_class', None)
        return str(mabni or 'UNKNOWN')
    elif claim_layer == 'ROOT':
        rc = getattr(bundle, 'root_claim', None)
        if rc is not None:
            cr = getattr(rc, 'canonical_root', None)
            if cr:
                return '.'.join(str(c) for c in cr)
        return 'UNKNOWN'
    elif claim_layer == 'PATTERN':
        wazn = getattr(bundle, 'wazn_claim', None)
        if wazn is not None:
            fw = getattr(wazn, 'final_wazn', None)
            if fw:
                return str(fw)
        return 'UNKNOWN'
    elif claim_layer == 'WORD_CLASS':
        return str(getattr(bundle, 'part_of_speech', None) or
                   getattr(bundle, 'lexical_class', None) or 'UNKNOWN')
    elif claim_layer == 'MASDAR':
        mc = getattr(bundle, 'masdar_claim', None)
        if mc is not None:
            fm = getattr(mc, 'final_masdar', None)
            if fm:
                return str(fm)
        return 'UNKNOWN'
    elif claim_layer == 'MUSHTAQAT':
        mushtaq = getattr(bundle, 'mushtaq_claims', None)
        if mushtaq:
            mc = mushtaq[0] if mushtaq else None
            if mc is not None:
                acc = getattr(mc, 'accepted_mushtaqat', None)
                if acc:
                    return str(list(dict(acc).keys())[0]) if acc else 'UNKNOWN'
        return 'UNKNOWN'
    elif claim_layer == 'INFLECTION':
        ic = getattr(bundle, 'inflection_claim', None)
        if ic is not None:
            ifo = getattr(ic, 'inflectional_form', None)
            if ifo:
                ta = getattr(ifo, 'tense_aspect', None)
                if ta:
                    return str(ta)
        return 'UNKNOWN'
    elif claim_layer == 'FINAL_TOKEN':
        return str(getattr(bundle, 'domain_directive', 'UNKNOWN') or 'UNKNOWN')
    return 'UNKNOWN'


def _claim_kind_for_layer(claim_layer: str) -> str:
    _MAP = {
        'P5_BOUNDARY':  'LEXICAL_BOUNDARY_CLAIM',
        'ROOT':         'ROOT_IDENTIFICATION_CLAIM',
        'PATTERN':      'PATTERN_WAZN_CLAIM',
        'WORD_CLASS':   'WORD_CLASS_CLAIM',
        'MASDAR':       'MASDAR_DERIVATION_CLAIM',
        'MUSHTAQAT':    'MUSHTAQ_DERIVATION_CLAIM',
        'INFLECTION':   'INFLECTION_PARADIGM_CLAIM',
        'FINAL_TOKEN':  'FINAL_TOKEN_CLAIM',
    }
    return _MAP.get(claim_layer, 'UNKNOWN_CLAIM')


def _evidence_rank_for_layer(claim_layer: str, upstream_verdict: str) -> int:
    """
    Evidence rank for this layer (0-based).
    Higher = stronger evidence.
    ACCEPT verdict gets higher rank.
    """
    base = {
        'ROOT': 4,
        'PATTERN': 3,
        'WORD_CLASS': 3,
        'INFLECTION': 2,
        'MASDAR': 2,
        'MUSHTAQAT': 2,
        'P5_BOUNDARY': 1,
        'FINAL_TOKEN': 1,
    }.get(claim_layer, 1)

    if upstream_verdict in ('ACCEPT', 'LICENSED'):
        return base
    elif upstream_verdict == 'DEFER':
        return max(0, base - 1)
    else:
        return 0


def _boundaries_crossed_for_layer(claim_layer: str) -> tuple:
    """Boundaries already crossed by this claim layer."""
    _MAP = {
        'ROOT':         ('P5_BOUNDARY',),
        'PATTERN':      ('P5_BOUNDARY', 'ROOT'),
        'WORD_CLASS':   ('P5_BOUNDARY', 'ROOT', 'PATTERN'),
        'INFLECTION':   ('P5_BOUNDARY', 'ROOT', 'PATTERN', 'WORD_CLASS'),
        'MASDAR':       ('P5_BOUNDARY', 'ROOT', 'PATTERN'),
        'MUSHTAQAT':    ('P5_BOUNDARY', 'ROOT', 'PATTERN'),
        'FINAL_TOKEN':  ('P5_BOUNDARY', 'ROOT', 'PATTERN', 'WORD_CLASS'),
    }
    return _MAP.get(claim_layer, ())


__all__ = [
    '_deterministic_claim_id',
    'project_bundle_to_claim',
]
