"""
maqayis_claim_pipeline.py — Claims + origin segmentation pipeline
MAQAYIS-CONSTITUTIONAL-SOURCE-LEXICON-PRODUCTION-01  Commit 4

Produces:
  • SourceRootClaim      — one per imported entry (MACHINE extraction)
  • LexicalOriginCandidate — one per SINGULAR; N per DUAL/TRIPLE/MULTIPLE
  • Residuals            — SEGMENTATION_REQUIRED for multi-origin claims;
                           FOUND_CONFLICT_REVIEW_REQUIRED for conflicts
  • TraceEvents          — per extraction and segmentation

Segmentation Rules
──────────────────
SINGULAR  → 1 LexicalOriginCandidate (origin_index=0)
DUAL      → 2 LexicalOriginCandidates (origin_index=0,1)
TRIPLE    → 3 LexicalOriginCandidates (origin_index=0,1,2)
MULTIPLE  → 3 LexicalOriginCandidates (conservative; exact N requires human review)
SOUND_ROOTS → 1 candidate (special classification)
NONE      → 1 candidate (positive absence claim — NOT negative evidence)
NOT_EXTRACTED / UNKNOWN → 1 candidate with INCOMPLETE_CLAIM

Conflict Detection
──────────────────
FOUND_CONFLICT_REVIEW_REQUIRED is raised when:
  • Two separate import records for the SAME root_letters have
    conflicting origin_types (e.g. one AUTO_AGREED+SINGULAR, another AUTO_AGREED+DUAL)
  • Or when the same root appears with both AUTO_AGREED and REVIEW_REQUIRED
    and the origin_types differ
No conflict is raised for:
  • Same root, both with NONE origin type
  • Duplicates across PDFs with identical origin_type

Fail-Open Contract
──────────────────
All exceptions caught. Never raises. Returns partial result on failure.
"""
from __future__ import annotations

import datetime
from collections import defaultdict
from typing import Optional

from maqayis_constitutional_schemas import (
    SourceRootClaim,
    LexicalOriginCandidate,
    TraceEvent,
    TraceEventKind,
    Residual,
    ResidualType,
    ReviewState,
    ReviewerType,
    EvidenceStatus,
    OriginType,
    ClaimKind,
    enforce_tc_ir_03,
    enforce_tc_ro_04,
    TransitionContractViolation,
)
from maqayis_legacy_importer import LegacyCandidateImport, LegacyImportResult
from maqayis_identity_pipeline import IdentityPipelineResult


CLAIM_ACTOR_ID  = "maqayis_claim_pipeline_v1"


# ── Shared helpers (duplicated from identity_pipeline to avoid circular import) ─

def _normalize_origin_type(raw: Optional[str]) -> OriginType:
    if not raw:
        return OriginType.NOT_EXTRACTED
    mapping = {
        "SINGULAR":       OriginType.SINGULAR,
        "DUAL":           OriginType.DUAL,
        "TRIPLE":         OriginType.TRIPLE,
        "MULTIPLE":       OriginType.MULTIPLE,
        "SOUND_ROOTS":    OriginType.SOUND_ROOTS,
        "NONE":           OriginType.NONE,
        "NOT_ROOT":       OriginType.NOT_EXTRACTED,
        "CHAPTER_HEADER": OriginType.NOT_EXTRACTED,
        "CROSS_REFERENCE": OriginType.NOT_EXTRACTED,
        "UNKNOWN":        OriginType.UNKNOWN,
    }
    return mapping.get(raw.strip().upper(), OriginType.UNKNOWN)
_CLAIM_PREFIX   = "maqayis:source-root-claim"
_ORIGIN_PREFIX  = "maqayis:lexical-origin-candidate"
_TRACE_PREFIX   = "maqayis:trace"
_RESIDUAL_PREFIX = "maqayis:residual"


# ═══════════════════════════════════════════════════════════════════════════════
# § 1 — CLAIM BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def _build_claim(
    imp: LegacyCandidateImport,
    occurred_at: str,
) -> SourceRootClaim:
    """Build a SourceRootClaim from a LegacyCandidateImport."""
    origin_type = _normalize_origin_type(imp.legacy_semantic_origin_type)

    # Claims extracted from legacy data are MACHINE OCR extraction
    # review_state: MACHINE_CANDIDATE → TEXT_CANDIDATE (machine extraction)
    # Text is NOT verified, so we stay at TEXT_CANDIDATE
    claim_review_state = ReviewState.TEXT_CANDIDATE
    claim_evidence_status = EvidenceStatus.MACHINE_SOURCE_CLAIM_CANDIDATE

    return SourceRootClaim(
        id=imp.claim_id,
        passage_id=imp.passage_id,
        identity_id=imp.candidate_id,
        claim_kind=_claim_kind_from_legacy(imp),
        origin_type=origin_type,
        raw_claim_text=imp.legacy_root_letters,  # heading as proxy for claim text
        review_state=claim_review_state,
        evidence_status=claim_evidence_status,
        extraction_method="MACHINE_OCR",
        supersedes_id=None,
    )


def _claim_kind_from_legacy(imp: LegacyCandidateImport) -> ClaimKind:
    """Determine claim kind from legacy import."""
    sot = imp.legacy_semantic_origin_type.upper()
    if sot == "NOT_ROOT":
        return ClaimKind.NOT_ROOT_ENTRY
    if sot == "CHAPTER_HEADER":
        return ClaimKind.CHAPTER_HEADER
    if sot == "CROSS_REFERENCE":
        return ClaimKind.CROSS_REFERENCE
    if sot == "NONE":
        return ClaimKind.POSITIVE_ORIGIN  # "لا أصل له" is a positive absence claim
    if sot in ("SINGULAR", "DUAL", "TRIPLE", "MULTIPLE", "SOUND_ROOTS"):
        return ClaimKind.POSITIVE_ORIGIN
    return ClaimKind.INCOMPLETE_CLAIM


# ═══════════════════════════════════════════════════════════════════════════════
# § 2 — ORIGIN SEGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def _segment_origins(
    claim: SourceRootClaim,
    imp: LegacyCandidateImport,
    occurred_at: str,
) -> tuple[list[LexicalOriginCandidate], list[TraceEvent]]:
    """
    Segment a SourceRootClaim into LexicalOriginCandidate records.

    SINGULAR  → 1 candidate
    DUAL      → 2 candidates
    TRIPLE    → 3 candidates
    MULTIPLE  → 3 candidates (conservative; exact N from human review)
    SOUND_ROOTS, NONE, etc. → 1 candidate
    """
    root = imp.legacy_root_letters
    origin_type = claim.origin_type
    candidates: list[LexicalOriginCandidate] = []
    traces: list[TraceEvent] = []

    # Determine segmentation count
    if origin_type == OriginType.DUAL:
        n_origins = 2
        seg_desc = ["الأصل الأول", "الأصل الثاني"]
    elif origin_type == OriginType.TRIPLE:
        n_origins = 3
        seg_desc = ["الأصل الأول", "الأصل الثاني", "الأصل الثالث"]
    elif origin_type == OriginType.MULTIPLE:
        n_origins = 3  # conservative; exact N requires human review
        seg_desc = ["الأصل الأول", "الأصل الثاني", "الأصل الثالث (وأكثر)"]
    else:
        n_origins = 1
        seg_desc = [_origin_desc(origin_type)]

    # Each segmented origin is SINGULAR after segmentation
    per_origin_type = OriginType.SINGULAR if n_origins > 1 else origin_type

    for i in range(n_origins):
        origin_id = f"{_ORIGIN_PREFIX}:{root}:{i}"
        candidates.append(LexicalOriginCandidate(
            id=origin_id,
            claim_id=claim.id,
            identity_id=claim.identity_id,
            origin_index=i,
            origin_type=per_origin_type,
            origin_description=seg_desc[i] if i < len(seg_desc) else f"الأصل {i+1}",
            raw_origin_text=imp.legacy_root_letters,
            review_state=ReviewState.ORIGIN_CANDIDATE,
            evidence_status=EvidenceStatus.MACHINE_SOURCE_CLAIM_CANDIDATE,
            extraction_method="MACHINE_OCR",
            supersedes_id=None,
        ))

    # TraceEvent for segmentation (if multi-origin)
    if n_origins > 1:
        traces.append(TraceEvent(
            id=f"{_TRACE_PREFIX}:origin_segmented:{root}",
            kind=TraceEventKind.ORIGIN_SEGMENTED,
            target_id=claim.id,
            target_type="SourceRootClaim",
            actor_type=ReviewerType.MACHINE_ONLY,
            actor_id=CLAIM_ACTOR_ID,
            occurred_at=occurred_at,
            summary=f"Origin segmented: {root} ({origin_type.value}) → {n_origins} candidates",
            metadata=(
                ("origin_type", origin_type.value),
                ("n_origins", str(n_origins)),
            ),
        ))
    else:
        traces.append(TraceEvent(
            id=f"{_TRACE_PREFIX}:origin_extracted:{root}",
            kind=TraceEventKind.ORIGIN_EXTRACTED,
            target_id=claim.id,
            target_type="SourceRootClaim",
            actor_type=ReviewerType.MACHINE_ONLY,
            actor_id=CLAIM_ACTOR_ID,
            occurred_at=occurred_at,
            summary=f"Origin extracted: {root} ({origin_type.value})",
            metadata=(("origin_type", origin_type.value),),
        ))

    return candidates, traces


def _origin_desc(origin_type: OriginType) -> str:
    descs = {
        OriginType.SINGULAR:      "أصل واحد",
        OriginType.SOUND_ROOTS:   "أصول صحيحة",
        OriginType.NONE:          "لا أصل له",
        OriginType.UNKNOWN:       "غير معروف",
        OriginType.NOT_EXTRACTED: "لم يُستخرج",
    }
    return descs.get(origin_type, origin_type.value)


# ═══════════════════════════════════════════════════════════════════════════════
# § 3 — CONFLICT DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def _detect_conflicts(
    imports: list[LegacyCandidateImport],
    occurred_at: str,
) -> tuple[dict[str, str], list[Residual], list[TraceEvent]]:
    """
    Detect conflicting claims for the same root.

    Returns:
      conflict_map: dict[root_letters → conflict description]
      residuals:    Residual(ORIGIN_CLAIM_CONFLICT) for each conflict
      trace_events: TraceEvent(ORIGIN_CONFLICT) for each conflict
    """
    # Group by root_letters
    root_groups: dict[str, list[LegacyCandidateImport]] = defaultdict(list)
    for imp in imports:
        if not imp.noise_entry:
            root_groups[imp.legacy_root_letters].append(imp)

    conflict_map: dict[str, str] = {}
    residuals: list[Residual] = []
    trace_events: list[TraceEvent] = []

    for root, group in root_groups.items():
        if len(group) <= 1:
            continue

        # Collect unique (review_status, origin_type) pairs
        pairs = set(
            (imp.legacy_review_status, imp.legacy_semantic_origin_type)
            for imp in group
        )
        origin_types = set(imp.legacy_semantic_origin_type for imp in group)

        # No conflict if all have same origin_type
        if len(origin_types) == 1:
            continue

        # No conflict if all are NONE (all say "لا أصل له")
        if origin_types <= {"NONE"}:
            continue

        conflict_desc = (
            f"Root '{root}' has {len(group)} entries with conflicting origin types: "
            f"{', '.join(sorted(origin_types))}"
        )
        conflict_map[root] = conflict_desc

        # Residual on the first candidate for this root
        first_imp = group[0]
        res_id = f"{_RESIDUAL_PREFIX}:ORIGIN_CLAIM_CONFLICT:{root}"
        residuals.append(Residual(
            id=res_id,
            target_id=first_imp.claim_id,
            target_type="SourceRootClaim",
            residual_type=ResidualType.ORIGIN_CLAIM_CONFLICT,
            description=conflict_desc,
            blocking_until=ReviewState.ORIGIN_SEGMENTED,
            created_at=occurred_at,
        ))

        trace_events.append(TraceEvent(
            id=f"{_TRACE_PREFIX}:origin_conflict:{root}",
            kind=TraceEventKind.ORIGIN_CONFLICT,
            target_id=first_imp.claim_id,
            target_type="SourceRootClaim",
            actor_type=ReviewerType.MACHINE_ONLY,
            actor_id=CLAIM_ACTOR_ID,
            occurred_at=occurred_at,
            summary=conflict_desc,
            metadata=(
                ("conflict_origin_types", ",".join(sorted(origin_types))),
                ("entry_count", str(len(group))),
            ),
        ))

    return conflict_map, residuals, trace_events


# ═══════════════════════════════════════════════════════════════════════════════
# § 4 — FULL PIPELINE RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

class ClaimPipelineResult:
    """Result of running the claim pipeline."""
    __slots__ = (
        "claims",
        "origin_candidates",
        "conflict_map",
        "residuals",
        "trace_events",
        "summary",
    )

    def __init__(
        self,
        claims: list[SourceRootClaim],
        origin_candidates: list[LexicalOriginCandidate],
        conflict_map: dict[str, str],
        residuals: list[Residual],
        trace_events: list[TraceEvent],
        summary: dict,
    ) -> None:
        self.claims           = claims
        self.origin_candidates = origin_candidates
        self.conflict_map     = conflict_map
        self.residuals        = residuals
        self.trace_events     = trace_events
        self.summary          = summary


def run_claim_pipeline(import_result: LegacyImportResult) -> ClaimPipelineResult:
    """
    Run the full claim and origin segmentation pipeline.

    For each non-noise import:
    • Build SourceRootClaim
    • Segment into LexicalOriginCandidates
    • Detect cross-entry conflicts

    Returns ClaimPipelineResult — never raises (fail-open contract).
    """
    occurred_at = datetime.datetime.utcnow().isoformat() + "Z"

    claims:            list[SourceRootClaim]          = []
    origin_candidates: list[LexicalOriginCandidate]   = []
    residuals:         list[Residual]                 = []
    trace_events:      list[TraceEvent]               = []

    failed = 0
    skipped_noise = 0
    singular_count = 0
    multi_origin_segmented = 0
    total_origins = 0

    for imp in import_result.imports:
        try:
            if imp.noise_entry:
                skipped_noise += 1
                continue

            claim = _build_claim(imp, occurred_at)
            claims.append(claim)

            origins, origin_traces = _segment_origins(claim, imp, occurred_at)
            origin_candidates.extend(origins)
            trace_events.extend(origin_traces)

            total_origins += len(origins)
            if len(origins) == 1:
                singular_count += 1
            else:
                multi_origin_segmented += 1

        except Exception:
            failed += 1
            continue

    # Conflict detection
    conflict_map, conflict_residuals, conflict_traces = _detect_conflicts(
        import_result.imports, occurred_at
    )
    residuals.extend(conflict_residuals)
    trace_events.extend(conflict_traces)

    # Segmentation residuals (from import — already emitted; don't duplicate)
    # (These are in import_result.residuals already)

    summary = {
        "CLAIMS_PRODUCED":              len(claims),
        "ORIGIN_CANDIDATES_PRODUCED":   len(origin_candidates),
        "SINGULAR_CLAIMS":              singular_count,
        "MULTI_ORIGIN_SEGMENTED":       multi_origin_segmented,
        "TOTAL_ORIGINS":                total_origins,
        "CONFLICT_ROOTS":               len(conflict_map),
        "CONFLICT_RESIDUALS":           len(conflict_residuals),
        "SKIPPED_NOISE":                skipped_noise,
        "FAILED":                       failed,
        "TRACE_EVENTS":                 len(trace_events),
    }

    return ClaimPipelineResult(
        claims=claims,
        origin_candidates=origin_candidates,
        conflict_map=conflict_map,
        residuals=residuals,
        trace_events=trace_events,
        summary=summary,
    )
