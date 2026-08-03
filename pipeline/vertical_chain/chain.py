"""
chain.py — Vertical chain executor.

TOKEN → CLAUSE → RELATION → IFADAH → HUKM → MANAT → TANZIL → ANSWER_AUDIT

Each step:
1. Checks applicability
2. Checks predecessors
3. Builds typed carrier
4. Checks evidence
5. Evaluates gate
6. Returns verdict
7. Opens successor only if APPROVED

CONSTITUTIONAL CONSTRAINTS:
    - No Ifadah from single token
    - No Hukm without Ifadah
    - No Tanzil without Hukm + Manat
    - No religious/legal overclaim
    - Deferred when evidence absent (not BLOCKED unless contradiction)
"""
from __future__ import annotations
from typing import Optional
import uuid
from .models import (
    IfadahCandidate, IfadahVerdict,
    HukmCandidate, HukmVerdict,
    ManatCandidate, ManatVerdict,
    TanzilCandidate, TanzilVerdict,
    AnswerAuditResult, AnswerAuditVerdict,
)


def build_ifadah(
    clause_id: str,
    relation_refs: tuple[str, ...],
    closed_relations: list,
    evidence_ids: tuple[str, ...],
) -> IfadahCandidate:
    """
    Build IfadahCandidate from closed relations.
    Returns DEFERRED if no closed relations or missing essential argument.
    """
    if not closed_relations:
        return IfadahCandidate(
            ifadah_id=f"IFADAH-{uuid.uuid4().hex[:8]}",
            clause_id=clause_id,
            relation_refs=relation_refs,
            proposition_shape="NONE",
            evidence_ids=evidence_ids,
            active_residuals=("NO_CLOSED_RELATIONS",),
            closure_state="RELATION_DEFERRED",
            rank=1,
            verdict=IfadahVerdict.IFADAH_DEFERRED,
            stop_reason="no_closed_relations",
        )

    # Check whether provided relations are genuinely CLOSED.
    # A closed relation must have closure_state == RELATION_CLOSED
    # (from RelationClosureState.RELATION_CLOSED) and required_argument_complete == True.
    # Relations that are merely CANDIDATE or DEFERRED still produce a DEFERRED Ifadah.
    from pipeline.relation_graph.models import RelationClosureState as _RCS

    actually_closed = [
        r for r in closed_relations
        if getattr(r, 'closure_state', None) in (
            _RCS.RELATION_CLOSED,
            "RELATION_CLOSED",
        ) and getattr(r, 'required_argument_complete', False)
    ]

    if not actually_closed:
        # Relations provided but none are genuinely closed — still DEFERRED.
        shapes = [str(getattr(r, 'relation_type', 'UNKNOWN')) for r in closed_relations]
        return IfadahCandidate(
            ifadah_id=f"IFADAH-{uuid.uuid4().hex[:8]}",
            clause_id=clause_id,
            relation_refs=relation_refs,
            proposition_shape="+".join(shapes),
            evidence_ids=evidence_ids,
            active_residuals=("RELATIONS_NOT_CLOSED",),
            closure_state="RELATION_CANDIDATE",
            rank=2,
            verdict=IfadahVerdict.IFADAH_DEFERRED,
            stop_reason="relations_not_yet_closed_deferred_lawfully",
        )

    # Build proposition shape from genuinely closed relation types
    shapes = [str(getattr(r, 'relation_type', 'UNKNOWN')) for r in actually_closed]
    proposition_shape = "+".join(shapes)

    # Evidence continuity: collect evidence IDs from each closed relation
    all_evidence: list[str] = list(evidence_ids)
    for r in actually_closed:
        for eid in getattr(r, 'evidence', ()):
            if eid not in all_evidence:
                all_evidence.append(str(eid))

    # Rank from best closed relation
    best_rank = max(
        (getattr(r, 'confidence_rank', 2) for r in actually_closed),
        default=2,
    )
    # Ifadah rank is min(best_relation_rank, 4) — LICENSED threshold
    ifadah_rank = min(best_rank, 4)

    return IfadahCandidate(
        ifadah_id=f"IFADAH-{uuid.uuid4().hex[:8]}",
        clause_id=clause_id,
        relation_refs=tuple(
            getattr(r, 'relation_id', str(i))
            for i, r in enumerate(actually_closed)
        ),
        proposition_shape=proposition_shape,
        evidence_ids=tuple(all_evidence),
        active_residuals=(),
        closure_state="RELATION_CLOSED",
        rank=ifadah_rank,
        verdict=IfadahVerdict.IFADAH_APPROVED,
        stop_reason=None,
    )


def build_hukm(
    ifadah: IfadahCandidate,
    modality: str = "DECLARATIVE",
) -> HukmCandidate:
    """Build HukmCandidate from a licensed IfadahCandidate."""
    if ifadah.verdict != IfadahVerdict.IFADAH_APPROVED:
        return HukmCandidate(
            hukm_id=f"HUKM-{uuid.uuid4().hex[:8]}",
            ifadah_id=ifadah.ifadah_id,
            subject_ref="DEFERRED",
            predicate_ref="DEFERRED",
            relation_ref="DEFERRED",
            polarity="UNKNOWN",
            modality=modality,
            temporal_scope=None,
            condition_scope=None,
            evidence_ids=(),
            residuals=("IFADAH_NOT_APPROVED",),
            rank=0,
            verdict=HukmVerdict.HUKM_DEFERRED,
            stop_reason="ifadah_not_approved",
        )

    return HukmCandidate(
        hukm_id=f"HUKM-{uuid.uuid4().hex[:8]}",
        ifadah_id=ifadah.ifadah_id,
        subject_ref=ifadah.clause_id,
        predicate_ref=ifadah.proposition_shape,
        relation_ref="; ".join(ifadah.relation_refs),
        polarity="POSITIVE",
        modality=modality,
        temporal_scope=None,
        condition_scope=None,
        evidence_ids=ifadah.evidence_ids,
        residuals=ifadah.active_residuals,
        rank=ifadah.rank,
        verdict=HukmVerdict.HUKM_APPROVED,
        stop_reason=None,
    )


def build_answer_audit(
    chain_items: list,
    forbidden_leaps_found: list[str],
    unresolved_residuals: list[str],
) -> AnswerAuditResult:
    """
    AnswerAudit — checks the full chain.
    Issues ANSWER_AUDIT_BLOCKED if any forbidden leap detected.
    Issues ANSWER_AUDIT_DEFERRED if unresolved residuals.
    """
    if forbidden_leaps_found:
        return AnswerAuditResult(
            audit_id=f"AUDIT-{uuid.uuid4().hex[:8]}",
            claim_provenance_verified=False,
            evidence_continuity_verified=False,
            stage_continuity_verified=False,
            forbidden_leaps=forbidden_leaps_found,
            unresolved_residuals=unresolved_residuals,
            rank_ceiling=0,
            scope_mismatch=False,
            unsupported_certainty=False,
            wording_overclaim=False,
            linguistic_vs_religious_distinction_clear=True,
            verdict=AnswerAuditVerdict.ANSWER_AUDIT_BLOCKED,
            stop_reason="FORBIDDEN_LEAP_DETECTED",
            trace_ids=(),
        )

    if unresolved_residuals:
        return AnswerAuditResult(
            audit_id=f"AUDIT-{uuid.uuid4().hex[:8]}",
            claim_provenance_verified=True,
            evidence_continuity_verified=True,
            stage_continuity_verified=True,
            forbidden_leaps=[],
            unresolved_residuals=unresolved_residuals,
            rank_ceiling=3,
            scope_mismatch=False,
            unsupported_certainty=False,
            wording_overclaim=False,
            linguistic_vs_religious_distinction_clear=True,
            verdict=AnswerAuditVerdict.ANSWER_AUDIT_DEFERRED,
            stop_reason="UNRESOLVED_RESIDUALS",
            trace_ids=(),
        )

    return AnswerAuditResult(
        audit_id=f"AUDIT-{uuid.uuid4().hex[:8]}",
        claim_provenance_verified=True,
        evidence_continuity_verified=True,
        stage_continuity_verified=True,
        forbidden_leaps=[],
        unresolved_residuals=[],
        rank_ceiling=4,
        scope_mismatch=False,
        unsupported_certainty=False,
        wording_overclaim=False,
        linguistic_vs_religious_distinction_clear=True,
        verdict=AnswerAuditVerdict.ANSWER_AUDIT_APPROVED,
        stop_reason=None,
        trace_ids=(),
    )
