"""
maqayis_constitutional_evidence_adapter.py — Constitutional evidence adapter
MAQAYIS-CONSTITUTIONAL-SOURCE-LEXICON-PRODUCTION-01  Commit 5

Produces enriched Taaqol EvidenceContract IDs with EvidenceStatus metadata.

New namespace schema:
  maqayis:source:{source_id}
  maqayis:passage:{passage_id}
  maqayis:root-identity-candidate:{root}:{idx}
  maqayis:source-root-claim:{root}:{idx}
  maqayis:lexical-origin-candidate:{root}:{origin_index}

Plus legacy namespace (still emitted for backward compat with evidence_adapter.py):
  maqayis:root:{root}:origin:{origin_type}:count:{n}
  maqayis:root:{root}:bab:{bab_letter}

Stage-0 Supplementary Constraints (unchanged from legacy adapter)
─────────────────────────────────────────────────────────────────
Constitutional evidence MUST NOT:
  • approve admission independently
  • increase token rank
  • suppress residual codes
  • assert roots not licensed by Hokom's canonical_root
  • produce Ifadah/Hukm/Manat/Tanzil/AnswerAudit

Evidence Status Contract
────────────────────────
FOUND_MACHINE_CANDIDATE_ONLY       → emit legacy origin ID + bab ID
FOUND_REVIEW_REQUIRED_UNRESOLVED  → emit bab ID only (origin suppressed)
FOUND_CONFLICT_REVIEW_REQUIRED    → emit bab ID only (conflict unresolved)
FOUND_IDENTITY_CANDIDATE+         → emit full namespace + legacy IDs
MISSING_VOLUME_COVERAGE_GAP       → emit nothing
NOT_FOUND_IN_COVERED_VOLUME       → emit nothing
REGISTRY_LOAD_FAILURE             → emit nothing

Accounting Counters (all must remain 0)
────────────────────────────────────────
REVIEW_REQUIRED_POSITIVE_ORIGIN_EVIDENCE_COUNT = 0
NONE_INTERPRETED_AS_NEGATIVE_SEMANTIC_CLAIM_COUNT = 0
MAQAYIS_LOOKUP_FROM_UNKNOWN_ROOT_COUNT = 0
CONSTITUTIONAL_EVIDENCE_APPROVED_ADMISSION_COUNT = 0
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from maqayis_constitutional_schemas import (
    LookupResultKind,
    EvidenceStatus,
    OriginType,
)
from maqayis_constitutional_registry import constitutional_lookup

if TYPE_CHECKING:
    from maqayis_constitutional_schemas import ConstitutionalLookupResult

# ── Accounting counters ───────────────────────────────────────────────────────
REVIEW_REQUIRED_POSITIVE_ORIGIN_EVIDENCE_COUNT:    int = 0
NONE_INTERPRETED_AS_NEGATIVE_SEMANTIC_CLAIM_COUNT: int = 0
MAQAYIS_LOOKUP_FROM_UNKNOWN_ROOT_COUNT:            int = 0
CONSTITUTIONAL_EVIDENCE_APPROVED_ADMISSION_COUNT:  int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# § 1 — EVIDENCE ID GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_constitutional_evidence_ids(root_letters: str) -> tuple[str, ...]:
    """
    Return constitutional + legacy Maqayis evidence IDs for *root_letters*.

    Parameters
    ──────────
    root_letters : str — undiacritized Arabic consonants

    Returns
    ───────
    Tuple of evidence ID strings (may be empty). Never raises.

    Evidence Status Contract
    ───────────────────────
    FOUND_MACHINE_CANDIDATE_ONLY     → origin ID + bab ID (legacy namespace)
    FOUND_REVIEW_REQUIRED_UNRESOLVED → bab ID only
    FOUND_CONFLICT_REVIEW_REQUIRED   → bab ID only
    MISSING_VOLUME_COVERAGE_GAP      → ()
    NOT_FOUND / REGISTRY_FAILURE     → ()
    """
    if not root_letters:
        return ()
    try:
        result = constitutional_lookup(root_letters)
        return _ids_from_constitutional_result(root_letters, result)
    except Exception:
        return ()


def _ids_from_constitutional_result(
    root: str,
    result: "ConstitutionalLookupResult",
) -> tuple[str, ...]:
    """Build evidence IDs from a ConstitutionalLookupResult."""
    ids: list[str] = []

    # Non-found kinds → no evidence
    if not result.found:
        return ()

    # Gather bab letter from candidate (if any)
    bab_letter = ""
    if result.identity_candidate:
        bab_letter = result.identity_candidate.bab_letter or ""

    # Legacy bab ID — emit for any found kind if bab valid
    if bab_letter:
        ids.append(f"maqayis:root:{root}:bab:{bab_letter}")

    # Origin ID — MACHINE_CANDIDATE_ONLY only (not for conflicts or review-required)
    if result.kind == LookupResultKind.FOUND_MACHINE_CANDIDATE_ONLY:
        # Collect best origin claim
        for claim in result.claims:
            if claim.origin_type not in (
                OriginType.NONE,
                OriginType.NOT_EXTRACTED,
                OriginType.UNKNOWN,
            ):
                # Build legacy origin ID
                # Use the claim's origin_type; count from origin_candidates
                n_origins = len([o for o in result.origin_candidates if o.claim_id == claim.id])
                cnt_str = str(n_origins) if n_origins > 0 else "none"
                origin_type_str = claim.origin_type.value
                ids.append(
                    f"maqayis:root:{root}:origin:{origin_type_str}:count:{cnt_str}"
                )
                break  # first non-NONE claim only

        # Constitutional namespace IDs
        if result.identity_candidate:
            ids.append(result.identity_candidate.id)
        for claim in result.claims:
            ids.append(claim.id)
        for origin in result.origin_candidates[:3]:  # cap at 3 for stage-0
            ids.append(origin.id)

    elif result.kind in (
        LookupResultKind.FOUND_CONFLICT_REVIEW_REQUIRED,
        LookupResultKind.FOUND_REVIEW_REQUIRED_UNRESOLVED,
    ):
        # Bab ID already added above; origin suppressed (review-required contract)
        pass  # REVIEW_REQUIRED_POSITIVE_ORIGIN_EVIDENCE_COUNT remains 0

    elif result.kind in (
        LookupResultKind.FOUND_IDENTITY_CANDIDATE,
        LookupResultKind.FOUND_IDENTITY_VERIFIED,
        LookupResultKind.FOUND_TEXT_VERIFIED,
        LookupResultKind.FOUND_LEXICALLY_REVIEWED,
    ):
        # Full evidence chain for higher-certainty results (V2+ territory)
        if result.identity_candidate:
            ids.append(result.identity_candidate.id)
        if result.identity_carrier:
            ids.append(result.identity_carrier.id)
        for claim in result.claims:
            ids.append(claim.id)
        for origin in result.origin_candidates:
            ids.append(origin.id)

    return tuple(ids)


# ═══════════════════════════════════════════════════════════════════════════════
# § 2 — EVIDENCE METADATA (per-ID EvidenceStatus)
# ═══════════════════════════════════════════════════════════════════════════════

def get_evidence_metadata(root_letters: str) -> dict[str, dict]:
    """
    Return per-ID evidence metadata for *root_letters*.

    Returns dict mapping evidence_id → {
        'evidence_status': EvidenceStatus.value,
        'review_state': ReviewState.value,
        'root_letters': str,
        'kind': LookupResultKind.value,
    }

    Empty dict if not found or error.
    """
    if not root_letters:
        return {}
    try:
        result = constitutional_lookup(root_letters)
        if not result.found:
            return {}
        ids = _ids_from_constitutional_result(root_letters, result)
        base_meta = {
            "evidence_status": result.evidence_status.name,
            "review_state":    result.review_state.value,
            "root_letters":    root_letters,
            "kind":            result.kind.value,
        }
        return {eid: dict(base_meta) for eid in ids}
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# § 3 — BUNDLE-LEVEL CONVENIENCE
# ═══════════════════════════════════════════════════════════════════════════════

def augment_evidence_from_bundle(bundle: object) -> tuple[str, ...]:
    """
    Extract root letters from a HokomLinguisticClaimBundle and return
    constitutional Maqayis evidence IDs.

    Identical contract to maqayis_evidence_adapter.augment_evidence_from_bundle:
    • Never modifies the bundle
    • Never raises
    • Returns () on any failure
    • MAQAYIS_LOOKUP_FROM_UNKNOWN_ROOT_COUNT = 0 enforced
      (root must come from bundle.root_claim.canonical_root only)
    """
    try:
        rc = getattr(bundle, "root_claim", None)
        if rc is None:
            return ()
        cr = getattr(rc, "canonical_root", None)
        if not cr:
            return ()
        root = "".join(str(c) for c in cr)
        if not root:
            return ()
        return get_constitutional_evidence_ids(root)
    except Exception:
        return ()


# ═══════════════════════════════════════════════════════════════════════════════
# § 4 — DIAGNOSTIC HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def explain_constitutional_lookup(root_letters: str) -> dict:
    """
    Diagnostic: return full lookup explanation for debugging/review tooling.
    Not called by the production pipeline.
    """
    try:
        result = constitutional_lookup(root_letters)
        out: dict = {
            "root":              root_letters,
            "kind":              result.kind.value,
            "evidence_status":   result.evidence_status.name,
            "review_state":      result.review_state.value,
            "found":             result.found,
            "is_machine_only":   result.is_machine_only,
            "has_conflict":      result.has_conflict,
            "coverage_gap":      result.coverage_gap,
            "evidence_ids":      list(get_constitutional_evidence_ids(root_letters)),
            "open_residuals":    len(result.open_residuals),
            "claims_count":      len(result.claims),
            "origins_count":     len(result.origin_candidates),
        }
        if result.identity_candidate:
            c = result.identity_candidate
            out["candidate"] = {
                "id":                   c.id,
                "candidate_letters":    c.candidate_letters,
                "bab_letter":           c.bab_letter,
                "original_bab_letter":  c.original_bab_letter,
                "bab_correction_version": c.bab_correction_version,
                "has_ocr_flags":        c.has_ocr_flags,
                "flagged_gates":        list(c.flagged_gates),
            }
        if result.conflict_notes:
            out["conflict_notes"] = result.conflict_notes
        if result.coverage_note:
            out["coverage_note"] = result.coverage_note
        return out
    except Exception as exc:
        return {"root": root_letters, "error": str(exc)}
