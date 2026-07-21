"""
SGA adapters: wrap existing Hokom pipeline outputs into typed slots.
These adapters are the boundary between Hokom's internal dicts and
the constitutional slot algebra.
No Arabic linguistic logic here — only structural wrapping.
"""
from __future__ import annotations
from typing import Any, Optional
from pipeline.sga.contracts import (
    TypedSlot, SlotId, SlotSort, SlotState,
    SurfaceProvenance, NormalizationOp, CandidateSet, CandidateEntry,
    EvidenceReference, HokomResidualRecord, DomainTransitionLicense,
    HokomClaimBundle, compute_claim_key, GeminationType, BoundaryType,
)

# ── H0: Surface Identity ───────────────────────────────────────────────────────

def adapt_surface_identity(hokom_result: dict) -> tuple[TypedSlot, TypedSlot, SurfaceProvenance]:
    """Extract ORIGINAL_SURFACE and NORMALIZED_SURFACE from pipeline result."""
    original = hokom_result.get("original_surface") or hokom_result.get("surface") or hokom_result.get("word", "")
    normalized = hokom_result.get("normalized_surface") or hokom_result.get("canonical_surface") or original

    prov = SurfaceProvenance(
        original_surface=original,
        normalized_surface=normalized,
        operations=(),
    )

    orig_slot = TypedSlot(
        slot_id=SlotId.ORIGINAL_SURFACE,
        sort=SlotSort.SURFACE_IDENTITY,
        state=SlotState.FILLED if original else SlotState.UNKNOWN,
        value=original if original else None,
        provenance=prov,
    )
    norm_slot = TypedSlot(
        slot_id=SlotId.NORMALIZED_SURFACE,
        sort=SlotSort.NORMALIZATION,
        state=SlotState.FILLED if normalized else SlotState.UNKNOWN,
        value=normalized if normalized else None,
        provenance=prov,
    )
    return orig_slot, norm_slot, prov


# ── H3: Segmentation ──────────────────────────────────────────────────────────

def adapt_segmentation(hokom_result: dict) -> tuple[TypedSlot, TypedSlot, TypedSlot]:
    """Extract proclitic, segment_host, enclitic from pipeline result."""
    host = hokom_result.get("segment_host")
    enclitics = hokom_result.get("enclitics") or hokom_result.get("enclitic") or []
    proclitics = hokom_result.get("proclitics") or hokom_result.get("proclitic") or []

    host_slot = TypedSlot(
        slot_id=SlotId.SEGMENT_HOST,
        sort=SlotSort.SEGMENTATION,
        state=SlotState.FILLED if host else SlotState.UNKNOWN,
        value=host,
    )

    enc_slot = TypedSlot(
        slot_id=SlotId.ENCLITIC_SLOTS,
        sort=SlotSort.SEGMENTATION,
        state=SlotState.FILLED if enclitics else SlotState.NOT_APPLICABLE,
        value=tuple(enclitics) if enclitics else None,
    )

    proc_slot = TypedSlot(
        slot_id=SlotId.PROCLITIC_SLOTS,
        sort=SlotSort.SEGMENTATION,
        state=SlotState.FILLED if proclitics else SlotState.NOT_APPLICABLE,
        value=tuple(proclitics) if proclitics else None,
    )

    return proc_slot, host_slot, enc_slot


# ── H4: Article ───────────────────────────────────────────────────────────────

def adapt_article(hokom_result: dict) -> tuple[TypedSlot, TypedSlot]:
    """Extract article and solar assimilation slots."""
    has_article = hokom_result.get("has_article") or hokom_result.get("article") or False
    solar = hokom_result.get("solar_assimilation") or hokom_result.get("is_solar") or False

    art_slot = TypedSlot(
        slot_id=SlotId.ARTICLE_SLOT,
        sort=SlotSort.ARTICLE,
        state=SlotState.FILLED if has_article else SlotState.NOT_APPLICABLE,
        value="AL" if has_article else None,
    )

    solar_slot = TypedSlot(
        slot_id=SlotId.SOLAR_ASSIMILATION_SLOT,
        sort=SlotSort.ARTICLE,
        state=SlotState.FILLED if (has_article and solar) else SlotState.NOT_APPLICABLE,
        value="SOLAR" if (has_article and solar) else None,
    )

    return art_slot, solar_slot


# ── H5: Boundary ──────────────────────────────────────────────────────────────

def adapt_boundary(hokom_result: dict) -> tuple[TypedSlot, TypedSlot]:
    """
    Extract boundary type and path directive.
    Closed boundaries: OPERATOR_BOUNDARY, MABNI_BOUNDARY, JAMID_AALAM_BOUNDARY
    -> pre_root=None, root_candidate=None, path=BLOCKED.
    """
    boundary = hokom_result.get("boundary_type") or hokom_result.get("pre_root")
    word_class = hokom_result.get("word_class", "")

    # Determine boundary type
    btype = None
    if boundary in ("OPERATOR_BOUNDARY",) or word_class in ("OPERATOR",):
        btype = BoundaryType.OPERATOR_BOUNDARY
    elif boundary in ("MABNI_BOUNDARY",) or word_class in ("MABNI", "MABNI_ISM"):
        btype = BoundaryType.MABNI_BOUNDARY
    elif boundary in ("JAMID_AALAM_BOUNDARY",):
        btype = BoundaryType.JAMID_AALAM_BOUNDARY

    # Path directive
    if btype is not None:
        path_state = SlotState.BLOCKED
        path_value = "ROOT_PATH_BLOCKED"
    else:
        path_state = SlotState.FILLED
        path_value = "OPEN_MORPHOLOGY"

    boundary_slot = TypedSlot(
        slot_id=SlotId.BOUNDARY_TYPE_SLOT,
        sort=SlotSort.BOUNDARY,
        state=SlotState.FILLED if btype else SlotState.NOT_APPLICABLE,
        value=btype.value if btype else None,
    )

    path_slot = TypedSlot(
        slot_id=SlotId.PATH_DIRECTIVE_SLOT,
        sort=SlotSort.BOUNDARY,
        state=path_state,
        value=path_value,
    )

    return boundary_slot, path_slot


# ── H6: Word Class ────────────────────────────────────────────────────────────

def adapt_word_class(hokom_result: dict) -> TypedSlot:
    wc = hokom_result.get("word_class")
    return TypedSlot(
        slot_id=SlotId.WORD_CLASS_SLOT,
        sort=SlotSort.WORD_CLASS,
        state=SlotState.FILLED if wc else SlotState.UNKNOWN,
        value=wc,
        evidence=(
            EvidenceReference(
                evidence_id=f"wc:{wc}",
                kind="MORPHOLOGICAL",
                source="hokom_pipeline",
            ),
        ) if wc else (),
    )


# ── H8-H9: Radicals ──────────────────────────────────────────────────────────

def adapt_root_radicals(hokom_result: dict) -> tuple[TypedSlot, TypedSlot, TypedSlot, TypedSlot]:
    """
    Extract R1/R2/R3/R4 from root_candidate.
    root_candidate format: "ك-ت-ب" or "ك ت ب" or "كتب"
    """
    root = hokom_result.get("root_candidate")

    if not root:
        # No root — UNKNOWN for all radicals
        return tuple(
            TypedSlot(
                slot_id=sid,
                sort=SlotSort.RADICAL,
                state=SlotState.UNKNOWN,
            )
            for sid in (SlotId.RADICAL_R1, SlotId.RADICAL_R2, SlotId.RADICAL_R3, SlotId.RADICAL_R4)
        )

    # Parse radicals
    if "-" in root:
        parts = root.split("-")
    elif " " in root:
        parts = root.split()
    else:
        parts = list(root)

    parts = [p.strip() for p in parts if p.strip()]

    slots = []
    for i, sid in enumerate(
        (SlotId.RADICAL_R1, SlotId.RADICAL_R2, SlotId.RADICAL_R3, SlotId.RADICAL_R4)
    ):
        if i < len(parts):
            state = SlotState.FILLED
            value = parts[i]
        elif i == 3:
            state = SlotState.NOT_APPLICABLE  # R4 only for quadrilateral
            value = None
        else:
            state = SlotState.UNKNOWN
            value = None

        slots.append(TypedSlot(
            slot_id=sid,
            sort=SlotSort.RADICAL,
            state=state,
            value=value,
            evidence=(
                EvidenceReference(
                    evidence_id=f"root:{root}:r{i+1}",
                    kind="MORPHOLOGICAL",
                    source="hokom_pipeline.root_candidate",
                ),
            ) if value else (),
        ))

    return tuple(slots)


# ── H10: Pattern ─────────────────────────────────────────────────────────────

def adapt_pattern(hokom_result: dict) -> TypedSlot:
    wazn = hokom_result.get("wazn") or hokom_result.get("pattern")
    return TypedSlot(
        slot_id=SlotId.PATTERN_CANDIDATE_SET,
        sort=SlotSort.PATTERN,
        state=SlotState.FILLED if wazn else SlotState.UNKNOWN,
        value=wazn,
        evidence=(
            EvidenceReference(
                evidence_id=f"wazn:{wazn}",
                kind="WAZN_MATCH",
                source="hokom_pipeline.wazn",
            ),
        ) if wazn else (),
    )


# ── Full Bundle Assembly ──────────────────────────────────────────────────────

def build_claim_bundle(hokom_result: dict, claim_kind: str, profile_id: str) -> HokomClaimBundle:
    """
    Assemble a HokomClaimBundle from a hokom_pipeline output dict.
    This is the canonical factory used by the bridge.
    """
    orig_slot, norm_slot, prov = adapt_surface_identity(hokom_result)
    proc_slot, host_slot, enc_slot = adapt_segmentation(hokom_result)
    art_slot, solar_slot = adapt_article(hokom_result)
    boundary_slot, path_slot = adapt_boundary(hokom_result)
    wc_slot = adapt_word_class(hokom_result)
    r1, r2, r3, r4 = adapt_root_radicals(hokom_result)
    pattern_slot = adapt_pattern(hokom_result)

    all_slots = (
        orig_slot, norm_slot, proc_slot, host_slot, enc_slot,
        art_slot, solar_slot, boundary_slot, path_slot,
        wc_slot, r1, r2, r3, r4, pattern_slot,
    )

    # Build slot_values for claim_key
    slot_values = {
        s.slot_id.value: s.value for s in all_slots if s.value is not None
    }

    # Collect evidence
    all_evidence: list[EvidenceReference] = []
    for s in all_slots:
        all_evidence.extend(s.evidence)

    claim_key = compute_claim_key(
        claim_kind=claim_kind,
        profile_id=profile_id,
        slot_values=slot_values,
        evidence_codes=tuple(e.evidence_id for e in all_evidence),
    )

    # Obstacles: closed boundary is an obstacle for ROOT_CLAIM
    obstacle_facts: list[str] = []
    if path_slot.state == SlotState.BLOCKED:
        obstacle_facts.append(f"CLOSED_BOUNDARY:{boundary_slot.value}")

    return HokomClaimBundle(
        claim_key=claim_key,
        claim_kind=claim_kind,
        profile_id=profile_id,
        surface=prov,
        typed_slots=all_slots,
        candidate_sets={},
        evidence_refs=tuple(all_evidence),
        condition_facts=(),
        obstacle_facts=tuple(obstacle_facts),
        defeater_facts=(),
        domain_licenses=(),
        residuals=(),
    )


__all__ = [
    "adapt_surface_identity",
    "adapt_segmentation",
    "adapt_article",
    "adapt_boundary",
    "adapt_word_class",
    "adapt_root_radicals",
    "adapt_pattern",
    "build_claim_bundle",
]
