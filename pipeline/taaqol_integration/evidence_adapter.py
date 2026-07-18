"""
Evidence mapping: Hokom domain outputs -> evidence records for Taaqol admission.
"""
from __future__ import annotations
from dataclasses import dataclass
from .provider_models import HokomLinguisticClaimBundle


EVIDENCE_TYPES = [
    'root_catalog_evidence',
    'root_restoration_evidence',
    'root_slot_alignment',
    'wazn_pattern_evidence',
    'form_catalog_evidence',
    'masdar_derivation_evidence',
    'mushtaq_derivation_evidence',
    'inflection_paradigm_evidence',
    'attachment_evidence',
    'negative_contradiction_evidence',
    'source_path_evidence',
]


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_type: str
    evidence_id: str
    content: str
    is_negative: bool = False  # True for contradiction evidence


@dataclass(frozen=True)
class EvidenceMappingResult:
    records: tuple
    total_count: int
    missing_types: tuple
    verdict: str    # SUFFICIENT | INSUFFICIENT | MISSING


def map_evidence(bundle: HokomLinguisticClaimBundle) -> EvidenceMappingResult:
    """
    Map Hokom evidence_ids to typed evidence records.
    Domain ACCEPT alone is NOT evidence.
    """
    records = []

    for eid in bundle.evidence_ids:
        etype = _classify_evidence_id(eid)
        records.append(EvidenceRecord(
            evidence_type=etype,
            evidence_id=eid,
            content=eid,
            is_negative='contradict' in eid.lower() or 'negative' in eid.lower(),
        ))

    # Determine missing critical evidence types
    found_types = {r.evidence_type for r in records}

    missing = []
    if bundle.root_claim is not None and 'root_catalog_evidence' not in found_types:
        missing.append('root_catalog_evidence')
    if bundle.wazn_claim is not None and 'wazn_pattern_evidence' not in found_types:
        missing.append('wazn_pattern_evidence')

    # Add source-path evidence from domain_directive
    if bundle.domain_directive == 'ACCEPT':
        records.append(EvidenceRecord(
            evidence_type='source_path_evidence',
            evidence_id=f'hokom:domain_directive:ACCEPT:{bundle.claim_id}',
            content=f'Hokom domain directive: ACCEPT (engine: {bundle.source_engine})',
            is_negative=False,
        ))

    total = len(records)
    if total == 0:
        verdict = 'MISSING'
    elif missing:
        verdict = 'INSUFFICIENT'
    else:
        verdict = 'SUFFICIENT'

    return EvidenceMappingResult(
        records=tuple(records),
        total_count=total,
        missing_types=tuple(missing),
        verdict=verdict,
    )


def _classify_evidence_id(eid: str) -> str:
    eid_lower = eid.lower()
    if 'root' in eid_lower and 'catalog' in eid_lower:
        return 'root_catalog_evidence'
    if 'root' in eid_lower and ('restor' in eid_lower or 'host' in eid_lower):
        return 'root_restoration_evidence'
    if 'root' in eid_lower and 'align' in eid_lower:
        return 'root_slot_alignment'
    if 'wazn' in eid_lower or 'pattern' in eid_lower:
        return 'wazn_pattern_evidence'
    if 'bab' in eid_lower or 'form' in eid_lower:
        return 'form_catalog_evidence'
    if 'masdar' in eid_lower:
        return 'masdar_derivation_evidence'
    if 'mushtaq' in eid_lower or 'ism' in eid_lower:
        return 'mushtaq_derivation_evidence'
    if 'inflect' in eid_lower or 'paradigm' in eid_lower:
        return 'inflection_paradigm_evidence'
    if 'attach' in eid_lower or 'mabni' in eid_lower:
        return 'attachment_evidence'
    if 'negat' in eid_lower or 'contradict' in eid_lower:
        return 'negative_contradiction_evidence'
    return 'source_path_evidence'
