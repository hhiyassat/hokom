"""
Typed domain models for Hokom -> Taaqol claim handoff.
These are Hokom-side types -- independent of taaqqul_slot_geometry internals.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable


# Forward-declared import to avoid circular reference.
# Constitutional contracts are pure types with no pipeline dependencies.
def _get_claim_provenance_type():
    from .constitutional_contracts import ClaimProvenance  # noqa: F401
    return ClaimProvenance

def _get_assessment_type():
    from .constitutional_contracts import Assessment  # noqa: F401
    return Assessment


@dataclass(frozen=True)
class HokomLinguisticClaimBundle:
    """
    The complete linguistic claim produced by Hokom for one token.
    This is the primary output unit -- immutable, typed, fully documented.
    """
    claim_id: str
    token_id: str
    original_surface: str
    normalized_surface: str
    refined_host: str | None
    lexical_class: str | None
    part_of_speech: str | None
    root_claim: object | None
    wazn_claim: object | None
    form_claim: object | None
    masdar_claim: object | None
    mushtaq_claims: tuple
    inflection_claim: object | None
    attachment_claims: tuple
    domain_directive: str           # ACCEPT | DEFER | BLOCK | NOT_APPLICABLE
    source_engine: str              # 'HOKOM_ROOT_ENGINE' | 'HOKOM_AUGMENTED_ENGINE'
    evidence_ids: tuple
    trace_ids: tuple
    active_residuals: tuple
    resolved_residuals: tuple
    catalog_versions: tuple
    engine_version: str
    # Amendment No. 1: optional provenance field (backward-compatible)
    provenance: Optional[object] = field(default=None)  # ClaimProvenance | None

    # Amendment No. 2: segmentation boundary fields (HOKOM-TAAQOL-LIVE-INTEGRATION-01)
    # morphology_surface is the lexical host extracted by the clitic segmenter.
    # original_surface is provenance only — NEVER used for morphological analysis.
    morphology_surface: Optional[str] = field(default=None)      # segment_bundle.host
    morphology_blocked: bool = field(default=False)               # True for clitic-only tokens
    morphology_block_reason: Optional[str] = field(default=None)  # e.g. 'SEGMENTATION_NO_LEXICAL_HOST'
    segment_bundle: Optional[object] = field(default=None)        # SegmentBundle | None

    # Amendment No. 3: canonical SegmentBundle field pass-through
    # (HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME)
    # These fields mirror SegmentBundle for direct use by bridge without bundle inspection.
    segment_host: Optional[str] = field(default=None)             # canonical morphological host
    segment_proclitics: tuple = field(default=())                 # proclitic surfaces
    segment_definite_article: Optional[str] = field(default=None) # article boundary surface
    segment_enclitics: tuple = field(default=())                  # enclitic surfaces
    segment_clitic_only: bool = field(default=False)              # True when host is None
    segment_verdict: Optional[str] = field(default=None)          # SegmentationVerdict string

    def to_dict(self) -> dict:
        return {
            'claim_id': self.claim_id,
            'token_id': self.token_id,
            'original_surface': self.original_surface,
            'normalized_surface': self.normalized_surface,
            'refined_host': self.refined_host,
            'lexical_class': self.lexical_class,
            'part_of_speech': self.part_of_speech,
            'domain_directive': self.domain_directive,
            'source_engine': self.source_engine,
            'evidence_ids': self.evidence_ids,
            'trace_ids': self.trace_ids,
            'active_residuals': self.active_residuals,
            'resolved_residuals': self.resolved_residuals,
            'engine_version': self.engine_version,
        }


@dataclass(frozen=True)
class ProviderAdmissionResult:
    """Result of Provider Guard evaluation -- NOT a claim approval."""
    provider_id: str
    admitted: bool
    violations: tuple
    note: str

    # Explicit: provider admission != claim approval
    IS_CLAIM_APPROVAL: bool = False


@dataclass(frozen=True)
class HokomTaaqolAdmissionResult:
    """Result of Taaqol Claim Admission for a HokomLinguisticClaimBundle."""
    claim_id: str
    verdict: str                    # APPROVED | DEFERRED | BLOCKED | REJECTED | FORBIDDEN_LEAP
    provider_admission: ProviderAdmissionResult
    identity_continuity: str        # ACCEPT | DEFER | BLOCK
    evidence_verdict: str           # SUFFICIENT | INSUFFICIENT | MISSING
    residual_verdict: str           # CLEAR | DEFERRABLE | BLOCKING | HIDDEN
    gate_verdict: str               # LEGAL | ILLEGAL | PENDING
    native_entry_stage: object | None
    stop_reason: str | None
    trace_refs: tuple
    active_residuals: tuple
    resolved_residuals: tuple
    taaqol_rank: object | None      # native Taaqol rank object, never injected by Hokom
    gamma_result: object | None     # native Gamma closure, opaque to Hokom
    # Amendment No. 1: optional Assessment field (backward-compatible)
    # Separates intrinsic_verdict / operational_status / evidence_rank
    assessment: Optional[object] = field(default=None)  # Assessment | None


@dataclass(frozen=True)
class TaaqolVerticalContinuationResult:
    """Result of Taaqol vertical continuation after admission."""
    claim_id: str
    admission: HokomTaaqolAdmissionResult
    native_stage_results: tuple     # (stage_name, result) pairs
    highest_completed_stage: str | None
    stop_stage: str | None
    stop_reason: str | None
    constitutional_rank: object | None
    gate_verdicts: tuple            # (gate_name, verdict) pairs
    active_residuals: tuple
    resolved_residuals: tuple
    audited_output: object | None   # AnswerAudit result if lawfully available


@dataclass(frozen=True)
class HokomTaaqolResult:
    """Top-level result of analyze_token_constitutionally()."""
    surface: str
    mode: str                       # 'shadow' | 'strict'
    hokom_claim_bundle: HokomLinguisticClaimBundle
    admission: HokomTaaqolAdmissionResult
    continuation: TaaqolVerticalContinuationResult | None
    shadow_comparison: dict | None  # only in shadow mode
