"""
segmenter.py — Generic Arabic clause segmenter.

Detects clause boundaries using structural operator markers.
Does NOT hardcode any specific text, token indices, or surfaces.
Does NOT read from gold corpus.

Production use: feed any Arabic token list.
Evaluation use: compare output against gold corpus in tests/evaluation/.
"""
from __future__ import annotations
from .models import ClauseBoundary, ClauseBoundaryType, ClauseCandidate, ClauseStatus
import uuid

# Structural operator markers — closed-class Arabic particles
# These are general Arabic grammar markers, not specific to any test sentence
CONJUNCTION_SURFACES = frozenset({"وَ", "فَ", "ثُمَّ", "أَوْ", "أَمْ", "بَلْ", "لَكِنْ", "و", "ف"})
CONDITIONAL_SURFACES = frozenset({"إِذَا", "إِنْ", "لَوْ", "مَتَى", "كُلَّمَا", "اذا", "ان", "لو"})
NEGATION_SURFACES    = frozenset({"لَا", "لَمْ", "لَنْ", "لَيْسَ", "مَا", "لا", "لم", "لن"})
VOCATIVE_SURFACES    = frozenset({"يَا", "أَيُّهَا", "أَيَّتُهَا", "يا"})
RELATIVE_SURFACES    = frozenset({"الَّذِي", "الَّتِي", "الَّذِينَ", "اللَّاتِي"})

BOUNDARY_MAP: dict[frozenset, ClauseBoundaryType] = {
    CONJUNCTION_SURFACES: ClauseBoundaryType.CONJUNCTION,
    CONDITIONAL_SURFACES: ClauseBoundaryType.CONDITIONAL,
    NEGATION_SURFACES:    ClauseBoundaryType.NEGATION,
    VOCATIVE_SURFACES:    ClauseBoundaryType.JUXTAPOSITION,
    RELATIVE_SURFACES:    ClauseBoundaryType.RELATIVE_ATTACHMENT,
}


def detect_boundaries(tokens: list[dict]) -> list[ClauseBoundary]:
    """
    Detect clause boundaries from a token list.
    Each token dict must have at least 'surface' key and optionally 'word_class'.
    Returns ClauseBoundary instances, one per detected boundary marker.
    Does NOT read from any gold corpus.
    """
    import unicodedata

    def strip_diacritics(s: str) -> str:
        return ''.join(c for c in s if not unicodedata.category(c).startswith('M'))

    boundaries = []
    for i, tok in enumerate(tokens):
        surface = tok.get("surface", "") or tok.get("original_surface", "")
        bare = strip_diacritics(surface)
        for marker_set, boundary_type in BOUNDARY_MAP.items():
            if surface in marker_set or bare in marker_set:
                boundaries.append(ClauseBoundary(
                    boundary_id=f"BOUND-{i:04d}-{uuid.uuid4().hex[:6]}",
                    token_index=i,
                    boundary_type=boundary_type,
                    operator_surface=surface,
                    evidence_ids=(f"operator_surface:{surface}",),
                    confidence=0.85,
                    residuals=(),
                ))
                break
    return boundaries


def segment_into_clauses(tokens: list[dict]) -> list[ClauseCandidate]:
    """
    Segment token list into clause candidates based on detected boundaries.
    Generic: works on any Arabic token list.
    """
    if not tokens:
        return []

    boundaries = detect_boundaries(tokens)
    boundary_indices = {b.token_index for b in boundaries}
    boundary_by_index = {b.token_index: b for b in boundaries}

    clauses = []
    clause_start = 0
    clause_index = 0

    for i, tok in enumerate(tokens):
        # A boundary at position i starts a NEW clause (operator is first token of new clause)
        if i > 0 and i in boundary_indices:
            # Close previous clause
            clause_tokens = tokens[clause_start:i]
            if clause_tokens:
                surfaces = [t.get("surface") or t.get("original_surface", "") for t in clause_tokens]
                preds = [s for s, t in zip(surfaces, clause_tokens)
                         if t.get("word_class", {}).get("word_class", "").startswith("FI3L")]
                clauses.append(ClauseCandidate(
                    clause_id=f"CL-{clause_index:03d}",
                    token_start=clause_start + 1,   # 1-based
                    token_end=i,                     # 1-based, inclusive
                    surface=" ".join(s for s in surfaces if s),
                    boundary_evidence=(f"operator_at_token_{i}",),
                    operators=tuple(boundary_by_index[i].operator_surface for _ in [1]),
                    main_predicate_candidates=tuple(preds),
                    argument_candidates=(),
                    references=(),
                    active_residuals=("predicate_candidates_unverified",) if not preds else (),
                    status=ClauseStatus.CANDIDATE,
                ))
                clause_index += 1
            clause_start = i

    # Final clause
    clause_tokens = tokens[clause_start:]
    if clause_tokens:
        surfaces = [t.get("surface") or t.get("original_surface", "") for t in clause_tokens]
        preds = [s for s, t in zip(surfaces, clause_tokens)
                 if t.get("word_class", {}).get("word_class", "").startswith("FI3L")]
        clauses.append(ClauseCandidate(
            clause_id=f"CL-{clause_index:03d}",
            token_start=clause_start + 1,
            token_end=len(tokens),
            surface=" ".join(s for s in surfaces if s),
            boundary_evidence=("final_clause_no_trailing_boundary",),
            operators=(),
            main_predicate_candidates=tuple(preds),
            argument_candidates=(),
            references=(),
            active_residuals=("predicate_candidates_unverified",) if not preds else (),
            status=ClauseStatus.CANDIDATE,
        ))

    return clauses
