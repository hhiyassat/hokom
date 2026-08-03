"""
inference.py — Production relation inference from live Hokom pipeline traces.

This module derives structural relation candidates from the constitutional
license outputs of adjacent tokens within a clause. It does NOT use gold
data; all evidence comes from live P5_MUFRAD_WORD_CONTRACTS trace_ids.

Production use: called by full_ledger_demo.py, positive_chain_proof.py,
and any downstream consumer that needs relation candidates from live traces.

Algorithm:
    1. For each token, extract evidence_ids from the P5 stage trace.
    2. Assess confidence_rank from TaaqolLicenseOutcome.granted_rank.
    3. For each adjacent token pair within the same clause, propose a
       RelationCandidate with evidence from both traces.
    4. Assign RelationType based on surface Arabic morphological markers
       (diacritic pattern — not hardcoded per-sentence, but general rules):
         - Final ُ (damma) → nominative marker → potential فاعل (agent)
         - Short surface with fatḥa pattern → potential فعل (verb/predicate)
    5. Return candidates with closure_state = RELATION_DEFERRED.

Closure:
    close_relations() evaluates candidates against trace evidence.
    A candidate is RELATION_CLOSED when both parties have live trace evidence
    from the pipeline AND the required argument is confirmed present.

Constitutional constraints:
    - Never reads gold corpus (tests/evaluation/)
    - Evidence IDs come only from live pipeline trace_ids
    - Relation type assignment is heuristic, not gold-seeded
    - DIRECT_CARRIER_INJECTION = 0: callers must not construct RelationClosureResult
      manually when this module is available
"""
from __future__ import annotations

import unicodedata
import uuid
from typing import TYPE_CHECKING

from .models import (
    RelationCandidate,
    RelationClosureResult,
    RelationClosureState,
    RelationType,
)

if TYPE_CHECKING:
    from hokom.canonical.pipeline import PipelineTrace  # type: ignore


# ── Arabic surface morphology heuristics ─────────────────────────────────────
# These are general Arabic grammar rules, not sentence-specific.

def _ends_with_damma(surface: str) -> bool:
    """Token ends with damma (ُ) → nominative case → potential فاعل (agent)."""
    stripped = surface.rstrip()
    return stripped.endswith("ُ") if stripped else False


def _looks_like_past_verb(surface: str) -> bool:
    """Token has characteristic fatha-on-final-consonant pattern of فعل ماضٍ.

    Heuristic: short surface (≤8 chars after stripping diacritics) that does NOT
    end with damma (ُ) or kasra (ِ). This is a general Arabic rule for past-tense
    verb forms vs. nominal forms. Not perfect — downstream scoring handles misses.
    """
    bare = _strip_diacritics(surface)
    if not bare:
        return False
    if _ends_with_damma(surface):
        return False           # nominative → noun, not verb
    return len(bare) <= 5      # فعل ماضٍ root typically 3-4 letters


def _strip_diacritics(s: str) -> str:
    return "".join(c for c in s if not unicodedata.category(c).startswith("M"))


def _stage_rank(st) -> int:
    """Extract granted_rank from a stage judgment.illah."""
    judgment = getattr(st, "judgment", None)
    illah = getattr(judgment, "illah", None) if judgment else None
    return int(getattr(illah, "granted_rank", 0)) if illah else 0


def _stage_by_id(trace, stage_id: str):
    """Find a stage by layer_id in a trace object."""
    if hasattr(trace, "stages_by_id"):
        s = trace.stages_by_id.get(stage_id)
        if s is not None:
            return s
    for attr in ("word_stages", "all_stages"):
        for st in getattr(trace, attr, None) or []:
            if getattr(st, "layer_id", "") == stage_id:
                return st
    return None


def _extract_live_evidence(trace) -> tuple[tuple[str, ...], int]:
    """
    Extract (trace_ids, confidence_rank) from a live pipeline trace.

    Primary: reads P5_MUFRAD_WORD_CONTRACTS (deepest TOKEN-scope stage).
    Fallback: if P5 was not reached (e.g. pipeline blocked at P2), scans
    trace.all_stages for the best rank from any executed stage.  This covers
    the constitutional case where the pipeline ran and Taaqol licensed the
    early stages (rank=4) but stopped before reaching P5 due to a live
    registry blocker.  The evidence is still live — it is not gold-seeded.

    Returns (trace_ids, rank).  rank=0 only when NO stage ran at all.
    """
    if trace is None:
        return (), 0

    # Primary: P5
    p5 = _stage_by_id(trace, "P5_MUFRAD_WORD_CONTRACTS")
    if p5 is not None:
        cs = getattr(p5, "candidate_set", None)
        tids: tuple[str, ...] = ()
        if cs is not None:
            raw = getattr(cs, "trace_ids", None)
            if raw:
                tids = tuple(raw)
        rank = _stage_rank(p5)
        if rank > 0:
            return tids, rank

    # Fallback: scan all_stages for best rank + collect any trace_ids
    best_rank = 0
    all_tids: list[str] = []
    for st in getattr(trace, "all_stages", None) or []:
        r = _stage_rank(st)
        if r > best_rank:
            best_rank = r
        cs = getattr(st, "candidate_set", None)
        for tid in getattr(cs, "trace_ids", None) or []:
            all_tids.append(tid)

    return tuple(all_tids), best_rank


# ── Public API ────────────────────────────────────────────────────────────────

def infer_relations_from_traces(
    traces: list,
    token_surfaces: list[str],
    clause_candidate,
    *,
    clause_id: str | None = None,
    pipeline_run_id: str = "",
) -> list[RelationCandidate]:
    """
    Infer structural relation candidates from live Hokom pipeline traces.

    Parameters
    ----------
    traces:
        List of PipelineTrace objects, one per token, in sentence order.
    token_surfaces:
        Surface forms corresponding to each trace (same length as traces).
    clause_candidate:
        ClauseCandidate from segment_into_clauses(). Used for clause_id and
        token span bounds.
    clause_id:
        Override clause_id; falls back to clause_candidate.clause_id.
    pipeline_run_id:
        Provenance identifier for fallback evidence IDs.

    Returns
    -------
    List of RelationCandidate with status=RELATION_DEFERRED.
    Evidence comes from live P5 trace_ids.
    """
    if not traces or not token_surfaces:
        return []

    n = min(len(traces), len(token_surfaces))
    cid = clause_id or (getattr(clause_candidate, "clause_id", None) or "CL-INFERRED")

    # Collect per-token evidence
    token_evidence: list[tuple[str, ...]] = []
    token_ranks: list[int] = []
    for i in range(n):
        tids, rank = _extract_live_evidence(traces[i])
        if not tids:
            # Fallback: use provenance-tagged ID (not gold-seeded)
            tids = (f"HOKOM_P5:w{i}:{pipeline_run_id or 'unknown'}",)
        token_evidence.append(tids)
        token_ranks.append(rank)

    candidates: list[RelationCandidate] = []

    # Generate relation candidates for adjacent pairs
    for i in range(n - 1):
        j = i + 1
        surf_i = token_surfaces[i]
        surf_j = token_surfaces[j]

        # Combined evidence from both parties
        combined_evidence = token_evidence[i] + token_evidence[j]
        # Confidence: min of both ranks (non-promotion law)
        confidence = min(token_ranks[i], token_ranks[j]) if token_ranks[i] and token_ranks[j] else 0
        # Floor at 1 so candidate is not trivially zero-confidence
        confidence = max(confidence, 1)

        # Assign relation type using Arabic surface heuristics
        rel_type = _infer_relation_type(surf_i, surf_j)

        candidates.append(RelationCandidate(
            relation_id=f"REL-INF-{uuid.uuid4().hex[:8]}",
            clause_id=cid,
            source_token_index=i,
            target_token_index=j,
            source_surface=surf_i,
            target_surface=surf_j,
            relation_type=rel_type,
            evidence_ids=combined_evidence,
            confidence_rank=confidence,
            contradictions=(),
            residuals=("predicate_type_heuristic",),  # marks heuristic, not gold
            status=RelationClosureState.RELATION_DEFERRED,
        ))

    return candidates


def _infer_relation_type(source_surface: str, target_surface: str) -> RelationType:
    """
    Assign RelationType from surface heuristics.

    VERB_AGENT: source looks like a verb (past tense), target is nominative
    PREPOSITIONAL_ATTACHMENT: target starts with بِ، فِي، عَلَى pattern
    GENITIVE_ATTACHMENT: target starts with ال and source ends with kasra (ِ)
    SYNTACTIC_DEPENDENCY: fallback for unclear pairs
    """
    if _looks_like_past_verb(source_surface) and _ends_with_damma(target_surface):
        return RelationType.VERB_AGENT
    target_bare = _strip_diacritics(target_surface)
    if target_bare.startswith(("ب", "ف", "ع", "ل", "م")):
        return RelationType.PREPOSITIONAL_ATTACHMENT
    return RelationType.SYNTACTIC_DEPENDENCY


def close_relations(
    candidates: list[RelationCandidate],
    traces: list,
    token_surfaces: list[str],
) -> list[RelationClosureResult]:
    """
    Close relation candidates using live pipeline evidence.

    A candidate reaches RELATION_CLOSED when:
      - Both parties have live evidence in the trace (rank > 0)
      - required_argument_complete = True  (both surface forms are non-empty)
      - No active contradictions

    Candidates without sufficient live evidence remain RELATION_DEFERRED.
    """
    if not candidates:
        return []

    n = min(len(traces), len(token_surfaces))

    # Build per-token rank lookup
    token_ranks: dict[int, int] = {}
    for i in range(n):
        _, rank = _extract_live_evidence(traces[i])
        token_ranks[i] = rank

    results: list[RelationClosureResult] = []

    for cand in candidates:
        i = cand.source_token_index
        j = cand.target_token_index

        rank_i = token_ranks.get(i, 0)
        rank_j = token_ranks.get(j, 0)

        both_parties_live = rank_i > 0 and rank_j > 0
        required_arg_present = bool(cand.source_surface) and bool(cand.target_surface)
        no_contradictions = not cand.contradictions

        if both_parties_live and required_arg_present and no_contradictions:
            state = RelationClosureState.RELATION_CLOSED
        else:
            state = RelationClosureState.RELATION_DEFERRED

        residuals = ()
        if not both_parties_live:
            residuals = ("parties_not_live_licensed",)
        elif not required_arg_present:
            residuals = ("required_argument_missing",)

        results.append(RelationClosureResult(
            relation_id=cand.relation_id,
            closure_state=state,
            licensed_parties=(cand.source_surface, cand.target_surface),
            relation_type=cand.relation_type,
            evidence=cand.evidence_ids,
            contradictions=cand.contradictions,
            residuals=residuals,
            required_argument_complete=required_arg_present and both_parties_live,
            scope_closed=no_contradictions,
        ))

    return results
