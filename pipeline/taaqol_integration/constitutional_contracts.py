"""
Constitutional Amendment No. 1 contracts for Hokom-Taaqol.
These types define the epistemic zones and transition contracts.
They do NOT create a parallel SCG registry.
They do NOT open P6-P12.
They do NOT replace HokomLinguisticClaimBundle or HokomTaaqolAdmissionResult.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional


# --- REALITY DOMAINS --------------------------------------------------------

class RealityDomain:
    """
    Canonical reality domain identifiers.
    No claim may use evidence from one domain to prove a conclusion in another
    without a declared DomainBridge.
    """
    SURFACE       = 'SURFACE'
    ORTHOGRAPHIC  = 'ORTHOGRAPHIC'
    PHONOLOGICAL  = 'PHONOLOGICAL'
    MORPHOLOGICAL = 'MORPHOLOGICAL'
    SYNTACTIC     = 'SYNTACTIC'
    SEMANTIC      = 'SEMANTIC'
    TEXTUAL       = 'TEXTUAL'
    LEGAL         = 'LEGAL'
    SHARI         = 'SHARI'
    EMPIRICAL     = 'EMPIRICAL'
    SOCIAL        = 'SOCIAL'
    HISTORICAL    = 'HISTORICAL'
    MATHEMATICAL  = 'MATHEMATICAL'
    HYPOTHETICAL  = 'HYPOTHETICAL'


# --- INTRINSIC VERDICT ------------------------------------------------------

class IntrinsicVerdict:
    """Verdict about the claim's internal validity. Separate from operational status."""
    SAHIH        = 'SAHIH'       # internally sound
    FASID        = 'FASID'       # defective but potentially repairable
    BATIL        = 'BATIL'       # null and void
    UNDETERMINED = 'UNDETERMINED'


# --- OPERATIONAL STATUS (Verifier output) -----------------------------------

class OperationalStatus:
    """External status issued by Verifier. Separate from intrinsic verdict."""
    LICENSED = 'LICENSED'
    BLOCKED  = 'BLOCKED'
    DEFERRED = 'DEFERRED'
    RESIDUAL = 'RESIDUAL'


# --- CLAIM PROVENANCE -------------------------------------------------------

@dataclass(frozen=True)
class ClaimProvenance:
    """
    Lineage record for every claim entering Hokom.
    Law: no licensed claim without preserved origin.
    Law: no transition without declared input source and transformation history.
    """
    claim_id:               str
    source_identity:        str
    source_type:            str   # HOKOM_ROOT_ENGINE | HOKOM_AUGMENTED_ENGINE | EXTERNAL | UNKNOWN
    originating_layer:      str   # e.g. 'P4A' | 'P5' | 'PRE_HOKOM'
    carrier:                str   # token surface or entity that carries the claim
    preserved_surface:      str
    prior_information:      Tuple[str, ...] = field(default_factory=tuple)
    domain:                 str = RealityDomain.MORPHOLOGICAL
    transformation_history: Tuple[str, ...] = field(default_factory=tuple)
    provenance_residuals:   Tuple[str, ...] = field(default_factory=tuple)


# --- CONCEPT CONTRACT -------------------------------------------------------

@dataclass(frozen=True)
class ConceptContract:
    """
    Constitutional contract for any concept entering the system.
    Law: no concept without a boundary.
    Law: no boundary without a differentiator.
    Law: no licensed concept with hidden residuals.
    Fields may carry Unknown/Deferred/NotApplicable -- never fabricated values.
    """
    concept_id:   str
    identity:     str
    boundary:     str               # what delimits this concept
    domain:       str               # RealityDomain value
    intension:    str               # defining properties
    extension:    str               # set of instances / 'Unknown' / 'Deferred'
    conditions:   Tuple[str, ...] = field(default_factory=tuple)
    implications: Tuple[str, ...] = field(default_factory=tuple)
    exclusions:   Tuple[str, ...] = field(default_factory=tuple)
    evidence:     Tuple[str, ...] = field(default_factory=tuple)
    evidence_rank: str = 'TRACE'   # NO_EVIDENCE -> TRACE -> CANDIDATE -> ... -> MASS_TRANSMISSION
    residuals:    Tuple[str, ...] = field(default_factory=tuple)
    review_trace: Tuple[str, ...] = field(default_factory=tuple)


# --- IFADAH CANDIDATE -------------------------------------------------------

@dataclass(frozen=True)
class IfadahCandidate:
    """
    A licensed candidate proposition extracted from an utterance and its relations.
    This is P12's output type -- a CANDIDATE, not a final meaning.
    Law: IfadahCandidate -> JudgmentCandidate (never -> Action directly).
    Law: IfadahCandidate is not a rule, not an action, not a final meaning.
    """
    proposition:           str
    source_utterance:      str
    licensed_relations:    Tuple[str, ...] = field(default_factory=tuple)
    domain:                str = RealityDomain.SEMANTIC
    beneficiaries:         Tuple[str, ...] = field(default_factory=tuple)
    evidence:              Tuple[str, ...] = field(default_factory=tuple)
    evidence_rank:         str = 'TRACE'
    assumptions:           Tuple[str, ...] = field(default_factory=tuple)
    blockers:              Tuple[str, ...] = field(default_factory=tuple)
    residuals:             Tuple[str, ...] = field(default_factory=tuple)
    prohibited_inferences: Tuple[str, ...] = field(default_factory=tuple)


# --- DOMAIN BRIDGE ----------------------------------------------------------

@dataclass(frozen=True)
class DomainBridge:
    """
    Declared contract for evidence transfer between domains.
    Law: no evidence from domain A may prove a claim in domain B without a DomainBridge.
    Example: morphological match alone cannot prove a legal ruling.
    """
    bridge_id:     str
    from_domain:   str
    to_domain:     str
    bridge_law:    str            # the rule permitting the transfer
    conditions:    Tuple[str, ...] = field(default_factory=tuple)
    residuals:     Tuple[str, ...] = field(default_factory=tuple)
    evidence_rank: str = 'TRACE'  # rank of the bridge itself


# --- ASSESSMENT -------------------------------------------------------------

@dataclass(frozen=True)
class Assessment:
    """
    Full separation of intrinsic verdict, operational status, and evidence rank.
    Law: these three must never be merged into one field.
    Example: claim may be SAHIH but DEFERRED (insufficient evidence, not invalid).
    Example: claim may be FASID but not BATIL (repairable).
    """
    claim_id:          str
    intrinsic_verdict: str   # IntrinsicVerdict value
    operational_status: str  # OperationalStatus value
    evidence_rank:     str   # e.g. 'NO_EVIDENCE' .. 'LICENSED' .. 'MASS_TRANSMISSION'
    active_blockers:   Tuple[str, ...] = field(default_factory=tuple)
    active_residuals:  Tuple[str, ...] = field(default_factory=tuple)
    repair_available:  bool = False
    notes:             str = ''


# --- TRANSITION TRACE -------------------------------------------------------

@dataclass(frozen=True)
class TransitionTrace:
    """
    Immutable audit record for every layer transition.
    Law: no review without a preserved trace.
    Law: conditions, blockers, defeaters that were checked may not be silently removed later.
    """
    trace_id:            str
    from_layer:          str
    to_layer:            str
    input_identity:      str
    output_identity:     str
    transformation:      str
    evidence_used:       Tuple[str, ...] = field(default_factory=tuple)
    conditions_checked:  Tuple[str, ...] = field(default_factory=tuple)
    blockers_checked:    Tuple[str, ...] = field(default_factory=tuple)
    defeaters_checked:   Tuple[str, ...] = field(default_factory=tuple)
    rank_before:         str = 'UNKNOWN'
    rank_after:          str = 'UNKNOWN'
    verdict:             str = 'UNKNOWN'
    residuals:           Tuple[str, ...] = field(default_factory=tuple)
    implementation_version: str = '1.1'
    timestamp:           str = ''


# --- REPAIR DIRECTIVE -------------------------------------------------------

@dataclass(frozen=True)
class RepairDirective:
    """
    Actionable repair instruction for every Blocked/Deferred/Residual result.
    Law: failure declaration is insufficient; must specify layer, owner, and retry path.
    """
    directive_id:        str
    failure_layer:       str
    return_to_layer:     str
    failed_gate:         str
    missing_condition:   str = 'Unknown'
    missing_evidence:    str = 'Unknown'
    active_blocker:      str = 'Unknown'
    challenged_cause:    str = 'Unknown'
    required_correction: str = ''
    retry_from:          str = ''
    retry_scope:         str = ''


# --- APPLICATION ASSESSMENT -------------------------------------------------

@dataclass(frozen=True)
class ApplicationAssessment:
    """
    Assessment of whether a licensed judgment applies to a specific case.
    This is POST-judgment -- after LicensedJudgment has been issued.
    Belongs to the Correspondence zone. Does not open new SCG layers.
    """
    assessment_id:   str
    judgment_id:     str
    case_description: str
    applies:         str = 'UNKNOWN'    # YES / NO / PARTIAL / UNKNOWN / DEFERRED
    conditions_met:  Tuple[str, ...] = field(default_factory=tuple)
    conditions_unmet: Tuple[str, ...] = field(default_factory=tuple)
    blockers:        Tuple[str, ...] = field(default_factory=tuple)
    residuals:       Tuple[str, ...] = field(default_factory=tuple)
    notes:           str = ''


# --- AUTHORITY CHECK --------------------------------------------------------

@dataclass(frozen=True)
class AuthorityCheck:
    """
    Verification that the agent/actor has authority to execute a licensed action.
    Law: IfadahCandidate -> JudgmentCandidate -> LicensedJudgment -> AuthorityCheck -> AuthorizedAction.
    No authorized action without authority check.
    """
    check_id:         str
    actor_id:         str
    action_type:      str
    domain:           str
    authority_source: str = 'Unknown'
    verdict:          str = 'UNKNOWN'   # AUTHORIZED / UNAUTHORIZED / DEFERRED / PARTIAL
    conditions:       Tuple[str, ...] = field(default_factory=tuple)
    blockers:         Tuple[str, ...] = field(default_factory=tuple)
    residuals:        Tuple[str, ...] = field(default_factory=tuple)


# --- CORRESPONDENCE ASSESSMENT ----------------------------------------------

@dataclass(frozen=True)
class CorrespondenceAssessment:
    """
    Comparison of expected vs. observed reality after an action is executed.
    Non-correspondence does not necessarily invalidate the rule.
    The failure may be in data, case, application, actor, execution, or measurement.
    """
    assessment_id:         str
    expected_reality:      str
    observed_reality:      str
    domain:                str      # RealityDomain value
    comparison_criteria:   Tuple[str, ...] = field(default_factory=tuple)
    matched_elements:      Tuple[str, ...] = field(default_factory=tuple)
    mismatched_elements:   Tuple[str, ...] = field(default_factory=tuple)
    unobservable:          Tuple[str, ...] = field(default_factory=tuple)
    correspondence_status: str = 'UNKNOWN'   # FULL / PARTIAL / NONE / UNOBSERVABLE
    contrary_evidence:     Tuple[str, ...] = field(default_factory=tuple)
    residuals:             Tuple[str, ...] = field(default_factory=tuple)
    review_required:       bool = False
    failure_attribution:   str = 'UNATTRIBUTED'  # DATA/CASE/APPLICATION/ACTOR/EXECUTION/MEASUREMENT
