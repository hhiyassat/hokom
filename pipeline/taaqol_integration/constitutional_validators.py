"""
Constitutional invariants -- executable guards for Amendment No. 1.
Import and call in tests and pipeline logic.
Pure validation functions with no external dependencies.
"""
from __future__ import annotations
from .constitutional_contracts import (
    Assessment, TransitionTrace, IfadahCandidate,
    ClaimProvenance, OperationalStatus, IntrinsicVerdict,
)


def assert_assessment_separation(a: Assessment) -> None:
    """
    Law: intrinsic_verdict, operational_status, evidence_rank must be
    distinct fields with distinct semantics. This guard validates the pairing.
    A claim may be SAHIH but DEFERRED (missing evidence, not invalid).
    A claim may be FASID but not BATIL (repairable).
    """
    valid_intrinsic = {
        IntrinsicVerdict.SAHIH,
        IntrinsicVerdict.FASID,
        IntrinsicVerdict.BATIL,
        IntrinsicVerdict.UNDETERMINED,
    }
    valid_operational = {
        OperationalStatus.LICENSED,
        OperationalStatus.BLOCKED,
        OperationalStatus.DEFERRED,
        OperationalStatus.RESIDUAL,
    }

    if a.intrinsic_verdict not in valid_intrinsic:
        raise ValueError(f"Invalid intrinsic_verdict: {a.intrinsic_verdict!r}")
    if a.operational_status not in valid_operational:
        raise ValueError(f"Invalid operational_status: {a.operational_status!r}")

    # Active blocker must cause BLOCKED, not LICENSED
    if a.active_blockers and a.operational_status == OperationalStatus.LICENSED:
        raise ValueError(
            f"Active blockers {a.active_blockers} present but status is LICENSED -- "
            "an active blocker must prevent LICENSED."
        )

    # BATIL + LICENSED is illegal
    if (a.intrinsic_verdict == IntrinsicVerdict.BATIL
            and a.operational_status == OperationalStatus.LICENSED):
        raise ValueError("BATIL claim cannot be LICENSED.")


def assert_no_direct_action_from_ifadah(
    source_type: str,
    target_type: str,
) -> None:
    """
    Law: IfadahCandidate -> Action is a forbidden leap.
    Law: Concept -> Action is a forbidden leap.
    Law: CandidateRule -> Action is a forbidden leap.
    """
    forbidden_sources = {'IfadahCandidate', 'ConceptContract', 'CandidateRule'}
    forbidden_targets = {'Action', 'AuthorizedAction', 'FinalMeaning', 'FinalJudgment'}
    if source_type in forbidden_sources and target_type in forbidden_targets:
        raise ValueError(
            f"Forbidden leap: {source_type} -> {target_type}. "
            f"Required path: {source_type} -> JudgmentCandidate -> HokomLicensing -> "
            f"LicensedJudgment -> AuthorityCheck -> {target_type}."
        )


def assert_rank_does_not_rise(
    rank_before: str,
    rank_after: str,
    same_evidence_repeated: bool = False,
) -> None:
    """
    Law: Rank(conclusion) <= min Rank(required premises).
    Repeating the same evidence cannot raise rank.
    """
    RANK_ORDER = [
        'NO_EVIDENCE', 'TRACE', 'CANDIDATE', 'HYPOTHESIS',
        'STRONG', 'LICENSED', 'CERTIFIED', 'MASS_TRANSMISSION',
    ]

    def rank_val(r: str) -> int:
        try:
            return RANK_ORDER.index(r)
        except ValueError:
            return -1

    if same_evidence_repeated and rank_val(rank_after) > rank_val(rank_before):
        raise ValueError(
            f"Rank rose from {rank_before!r} to {rank_after!r} by repeating same evidence. "
            "Rank law violated."
        )


def assert_transition_trace_complete(t: TransitionTrace) -> None:
    """Law: every transition must have a complete trace record."""
    required = [
        'trace_id', 'from_layer', 'to_layer', 'input_identity',
        'output_identity', 'transformation', 'verdict',
    ]
    for field_name in required:
        val = getattr(t, field_name, None)
        if not val:
            raise ValueError(
                f"TransitionTrace missing required field: {field_name!r}"
            )


def assert_no_domain_leap(
    evidence_domain: str,
    conclusion_domain: str,
    bridge_declared: bool,
) -> None:
    """
    Law: evidence from domain A cannot prove a conclusion in domain B
    without a declared DomainBridge.
    """
    if evidence_domain != conclusion_domain and not bridge_declared:
        raise ValueError(
            f"Domain leap from {evidence_domain!r} to {conclusion_domain!r} "
            "without a declared DomainBridge. This is a prohibited evidence transfer."
        )


def assert_provenance_not_empty(p: ClaimProvenance) -> None:
    """Law: no licensed claim without preserved origin."""
    if not p.claim_id or not p.source_identity or not p.preserved_surface:
        raise ValueError(
            f"ClaimProvenance incomplete: claim_id={p.claim_id!r}, "
            f"source_identity={p.source_identity!r}, "
            f"preserved_surface={p.preserved_surface!r}"
        )
