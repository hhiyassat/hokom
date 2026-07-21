"""
Canonical SGA contracts for Hokom.
Taaqol owns: SlotGraph, TransitionGate, EvidenceContract, RankLattice, Gamma, TraceLedger.
Hokom owns: the Arabic linguistic domain layer defined here.
Bridge owns: the mapping between these contracts and Taaqol's public API.

HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 — Stage 1
Python 3.10+ compatible (str, Enum only — no StrEnum).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, Optional, Tuple


# ── Slot Identity ──────────────────────────────────────────────────────────────

class SlotId(str, Enum):
    # Surface layer (H0-H2)
    ORIGINAL_SURFACE       = "ORIGINAL_SURFACE"
    NORMALIZED_SURFACE     = "NORMALIZED_SURFACE"
    LETTER_SEQUENCE        = "LETTER_SEQUENCE"
    DIACRITIC_SEQUENCE     = "DIACRITIC_SEQUENCE"
    PHONOLOGICAL_CELLS     = "PHONOLOGICAL_CELLS"
    SHADDA_SLOT            = "SHADDA_SLOT"
    SUKUN_SLOT             = "SUKUN_SLOT"
    MADD_SLOT              = "MADD_SLOT"
    # Segmentation layer (H3-H4)
    PROCLITIC_SLOTS        = "PROCLITIC_SLOTS"
    SEGMENT_HOST           = "SEGMENT_HOST"
    ENCLITIC_SLOTS         = "ENCLITIC_SLOTS"
    ARTICLE_SLOT           = "ARTICLE_SLOT"
    SOLAR_ASSIMILATION_SLOT = "SOLAR_ASSIMILATION_SLOT"
    # Boundary layer (H5)
    BOUNDARY_TYPE_SLOT     = "BOUNDARY_TYPE_SLOT"
    PATH_DIRECTIVE_SLOT    = "PATH_DIRECTIVE_SLOT"
    # Lexical / functional identity (H5-H6)
    LEXICAL_IDENTITY_SLOT  = "LEXICAL_IDENTITY_SLOT"
    FUNCTIONAL_OWNER_SLOT  = "FUNCTIONAL_OWNER_SLOT"
    WORD_CLASS_SLOT        = "WORD_CLASS_SLOT"
    # Morphological layer (H7-H10)
    INFLECTION_PREFIX_SLOT     = "INFLECTION_PREFIX_SLOT"
    INFLECTION_SUFFIX_SLOT     = "INFLECTION_SUFFIX_SLOT"
    DERIVATIONAL_EXTENSION_SLOTS = "DERIVATIONAL_EXTENSION_SLOTS"
    WEAK_RADICAL_SLOT          = "WEAK_RADICAL_SLOT"
    GEMINATION_SLOT            = "GEMINATION_SLOT"
    RESTORATION_CANDIDATE_SET  = "RESTORATION_CANDIDATE_SET"
    # Radical layer (H8-H9)
    RADICAL_R1             = "RADICAL_R1"
    RADICAL_R2             = "RADICAL_R2"
    RADICAL_R3             = "RADICAL_R3"
    RADICAL_R4             = "RADICAL_R4"
    ROOT_CANDIDATE_SET     = "ROOT_CANDIDATE_SET"
    # Pattern layer (H10)
    PATTERN_CANDIDATE_SET  = "PATTERN_CANDIDATE_SET"
    PATTERN_ALIGNMENT      = "PATTERN_ALIGNMENT"
    PATTERN_EVIDENCE       = "PATTERN_EVIDENCE"
    # Morphosyntax (H11-H15)
    BAB_CANDIDATE_SET          = "BAB_CANDIDATE_SET"
    MASDAR_CANDIDATE_SET       = "MASDAR_CANDIDATE_SET"
    DERIVATIVE_CANDIDATE_SET   = "DERIVATIVE_CANDIDATE_SET"
    NUMBER_SLOT                = "NUMBER_SLOT"
    GENDER_SLOT                = "GENDER_SLOT"
    DEFINITENESS_SLOT          = "DEFINITENESS_SLOT"
    NISBA_SLOT                 = "NISBA_SLOT"
    COLLECTIVE_SLOT            = "COLLECTIVE_SLOT"
    UNIT_NOUN_SLOT             = "UNIT_NOUN_SLOT"
    LEMMA_SLOT                 = "LEMMA_SLOT"
    PARADIGM_SLOT              = "PARADIGM_SLOT"
    INFLECTIONAL_FAMILY_SLOT   = "INFLECTIONAL_FAMILY_SLOT"
    DERIVATIONAL_FAMILY_SLOT   = "DERIVATIONAL_FAMILY_SLOT"
    # Evidence / residual
    EVIDENCE_SLOT          = "EVIDENCE_SLOT"
    RESIDUAL_SLOT          = "RESIDUAL_SLOT"


class SlotSort(int, Enum):
    """Canonical processing order. Lower = earlier."""
    SURFACE_IDENTITY      = 0
    NORMALIZATION         = 10
    PHONOLOGICAL          = 20
    SEGMENTATION          = 30
    ARTICLE               = 35
    BOUNDARY              = 40
    LEXICAL_FUNCTIONAL    = 50
    WORD_CLASS            = 60
    INFLECTIONAL          = 70
    RADICAL               = 80
    PATTERN               = 90
    BAB                   = 100
    MASDAR                = 110
    DERIVATIVE            = 120
    MORPHOSYNTAX          = 130
    PARADIGM              = 140
    EVIDENCE              = 900
    RESIDUAL              = 910


class SlotState(str, Enum):
    FILLED          = "FILLED"
    UNKNOWN         = "UNKNOWN"
    AMBIGUOUS       = "AMBIGUOUS"
    NOT_APPLICABLE  = "NOT_APPLICABLE"
    BLOCKED         = "BLOCKED"


class GeminationType(str, Enum):
    ROOT_GEMINATION          = "ROOT_GEMINATION"
    DERIVATIONAL_GEMINATION  = "DERIVATIONAL_GEMINATION"
    ASSIMILATION_GEMINATION  = "ASSIMILATION_GEMINATION"
    UNKNOWN_GEMINATION       = "UNKNOWN_GEMINATION"


class BoundaryType(str, Enum):
    OPERATOR_BOUNDARY    = "OPERATOR_BOUNDARY"
    MABNI_BOUNDARY       = "MABNI_BOUNDARY"
    JAMID_AALAM_BOUNDARY = "JAMID_AALAM_BOUNDARY"
    OPEN_MORPHOLOGY      = "OPEN_MORPHOLOGY"


# ── Surface Provenance ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class NormalizationOp:
    op_code: str      # e.g. "REMOVE_TATWEEL", "NFC", "EXPAND_HAMZA"
    input_char: str
    output_char: str
    position: int


@dataclass(frozen=True)
class SurfaceProvenance:
    original_surface: str
    normalized_surface: str
    operations: Tuple[NormalizationOp, ...] = ()

    def assert_original_preserved(self) -> None:
        assert self.original_surface, "original_surface must never be empty"


# ── Candidates ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CandidateEntry:
    value: str
    evidence_code: str
    confidence: Optional[float] = None  # None = unscored


@dataclass(frozen=True)
class CandidateSet:
    candidates: Tuple[CandidateEntry, ...] = ()
    selected: Optional[str] = None          # None when state=AMBIGUOUS or UNKNOWN
    selection_evidence: Optional[str] = None

    def __post_init__(self) -> None:
        if len(self.candidates) > 1 and self.selected is not None:
            # selection_evidence is required when selecting from multiple candidates
            assert self.selection_evidence, (
                "selection_evidence required when selecting from multiple candidates"
            )


# ── Evidence ───────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EvidenceReference:
    evidence_id: str
    kind: str         # CATALOG_HIT | WAZN_MATCH | PATTERN_MATCH | LEXICAL | MORPHOLOGICAL | CONTEXTUAL
    source: str
    payload: Optional[str] = None
    is_negative: bool = False   # True = absence evidence


# ── Residuals ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class HokomResidualRecord:
    residual_id: str
    code: str
    kind: str          # BLOCKING | DEFERRABLE | NON_BLOCKING
    source_slot: SlotId
    candidate_set: Optional[CandidateSet] = None
    reason: str = ""
    visibility: str = "VISIBLE"   # VISIBLE | LATENT
    next_evidence_required: Optional[str] = None


# ── Typed Slot ────────────────────────────────────────────────────────────────

@dataclass
class TypedSlot:
    slot_id: SlotId
    sort: SlotSort
    state: SlotState = SlotState.UNKNOWN
    value: Optional[object] = None
    candidate_set: Optional[CandidateSet] = None
    evidence: Tuple[EvidenceReference, ...] = field(default_factory=tuple)
    provenance: Optional[SurfaceProvenance] = None
    residual: Optional[HokomResidualRecord] = None
    owner: str = "HOKOM"    # HOKOM or BRIDGE (never TAAQOL)

    def __post_init__(self) -> None:
        # UNKNOWN must never be coerced to a default value
        if self.state == SlotState.UNKNOWN:
            assert self.value is None, (
                f"Slot {self.slot_id}: UNKNOWN state must have value=None"
            )
        # AMBIGUOUS must preserve candidate_set with >1 candidates and selected=None
        if self.state == SlotState.AMBIGUOUS:
            assert self.candidate_set is not None and len(self.candidate_set.candidates) > 1, (
                f"Slot {self.slot_id}: AMBIGUOUS state requires candidate_set with >1 candidates"
            )
            assert self.candidate_set.selected is None, (
                f"Slot {self.slot_id}: AMBIGUOUS state must have selected=None"
            )


# ── DomainTransitionLicense ───────────────────────────────────────────────────

@dataclass(frozen=True)
class DomainTransitionLicense:
    """
    Hokom issues this for every major linguistic transition.
    It describes the facts; Taaqol TransitionGate issues constitutional verdict.
    """
    license_id: str
    cause: str
    input_slots: Tuple[SlotId, ...]
    output_slots: Tuple[SlotId, ...]
    condition_facts: Tuple[str, ...] = ()
    obstacle_facts: Tuple[str, ...] = ()
    defeater_facts: Tuple[str, ...] = ()
    evidence_refs: Tuple[str, ...] = ()
    residuals: Tuple[str, ...] = ()
    provenance: Optional[str] = None
    stage: str = ""

    def __post_init__(self) -> None:
        assert self.cause, "DomainTransitionLicense requires a cause"
        assert self.input_slots and self.output_slots, (
            "DomainTransitionLicense requires input_slots and output_slots"
        )


# ── Claim Profiles ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ClaimProfile:
    profile_id: str
    required_slots: FrozenSet[SlotId]
    optional_slots: FrozenSet[SlotId]
    not_applicable_slots: FrozenSet[SlotId]
    allowed_evidence_kinds: FrozenSet[str]
    minimum_evidence_count: int
    possible_residual_codes: FrozenSet[str]


CLAIM_PROFILES: dict[str, ClaimProfile] = {
    "ROOT_CLAIM": ClaimProfile(
        profile_id="ROOT_CLAIM",
        required_slots=frozenset({
            SlotId.SEGMENT_HOST, SlotId.RADICAL_R1,
            SlotId.RADICAL_R2, SlotId.RADICAL_R3,
        }),
        optional_slots=frozenset({
            SlotId.RADICAL_R4, SlotId.PATTERN_CANDIDATE_SET,
            SlotId.RESTORATION_CANDIDATE_SET, SlotId.WEAK_RADICAL_SLOT,
        }),
        not_applicable_slots=frozenset({
            SlotId.FUNCTIONAL_OWNER_SLOT,
        }),
        allowed_evidence_kinds=frozenset({
            "WAZN_MATCH", "PATTERN_MATCH", "LEXICAL", "MORPHOLOGICAL"
        }),
        minimum_evidence_count=1,
        possible_residual_codes=frozenset({"WEAK_RADICAL", "AMBIGUOUS_ROOT"}),
    ),
    "PATTERN_CLAIM": ClaimProfile(
        profile_id="PATTERN_CLAIM",
        required_slots=frozenset({
            SlotId.SEGMENT_HOST, SlotId.PATTERN_CANDIDATE_SET,
        }),
        optional_slots=frozenset({
            SlotId.PATTERN_ALIGNMENT, SlotId.PATTERN_EVIDENCE,
        }),
        not_applicable_slots=frozenset(),
        allowed_evidence_kinds=frozenset({"WAZN_MATCH", "PATTERN_MATCH"}),
        minimum_evidence_count=1,
        possible_residual_codes=frozenset({"AMBIGUOUS_PATTERN"}),
    ),
    "BAB_CLAIM": ClaimProfile(
        profile_id="BAB_CLAIM",
        required_slots=frozenset({SlotId.BAB_CANDIDATE_SET}),
        optional_slots=frozenset({SlotId.PARADIGM_SLOT}),
        not_applicable_slots=frozenset(),
        allowed_evidence_kinds=frozenset({"LEXICAL", "MORPHOLOGICAL"}),
        minimum_evidence_count=1,
        possible_residual_codes=frozenset({"AMBIGUOUS_BAB"}),
    ),
    "MASDAR_CLAIM": ClaimProfile(
        profile_id="MASDAR_CLAIM",
        required_slots=frozenset({SlotId.MASDAR_CANDIDATE_SET}),
        optional_slots=frozenset({SlotId.DERIVATIONAL_EXTENSION_SLOTS}),
        not_applicable_slots=frozenset(),
        allowed_evidence_kinds=frozenset({"PATTERN_MATCH", "LEXICAL"}),
        minimum_evidence_count=1,
        possible_residual_codes=frozenset({"AMBIGUOUS_MASDAR", "SAMI_MASDAR"}),
    ),
    "DERIVATIVE_CLAIM": ClaimProfile(
        profile_id="DERIVATIVE_CLAIM",
        required_slots=frozenset({SlotId.DERIVATIVE_CANDIDATE_SET}),
        optional_slots=frozenset({SlotId.PATTERN_CANDIDATE_SET}),
        not_applicable_slots=frozenset(),
        allowed_evidence_kinds=frozenset({"PATTERN_MATCH", "LEXICAL"}),
        minimum_evidence_count=1,
        possible_residual_codes=frozenset({"AMBIGUOUS_DERIVATIVE"}),
    ),
    "WORD_CLASS_CLAIM": ClaimProfile(
        profile_id="WORD_CLASS_CLAIM",
        required_slots=frozenset({SlotId.WORD_CLASS_SLOT}),
        optional_slots=frozenset({
            SlotId.LEXICAL_IDENTITY_SLOT, SlotId.FUNCTIONAL_OWNER_SLOT,
        }),
        not_applicable_slots=frozenset({
            SlotId.RADICAL_R1, SlotId.RADICAL_R2, SlotId.RADICAL_R3,
            SlotId.PATTERN_CANDIDATE_SET, SlotId.BAB_CANDIDATE_SET,
        }),
        allowed_evidence_kinds=frozenset({
            "CATALOG_HIT", "MORPHOLOGICAL", "LEXICAL"
        }),
        minimum_evidence_count=1,
        possible_residual_codes=frozenset({"AMBIGUOUS_WORD_CLASS"}),
    ),
    "FUNCTIONAL_OWNER_CLAIM": ClaimProfile(
        profile_id="FUNCTIONAL_OWNER_CLAIM",
        required_slots=frozenset({SlotId.FUNCTIONAL_OWNER_SLOT}),
        optional_slots=frozenset({SlotId.LEXICAL_IDENTITY_SLOT}),
        not_applicable_slots=frozenset({
            SlotId.RADICAL_R1, SlotId.RADICAL_R2, SlotId.RADICAL_R3,
        }),
        allowed_evidence_kinds=frozenset({"CATALOG_HIT", "LEXICAL"}),
        minimum_evidence_count=1,
        possible_residual_codes=frozenset({"FUNCTIONAL_COLLISION"}),
    ),
    # Reserved — not yet implemented
    "SYNTACTIC_RELATION_CLAIM": ClaimProfile(
        profile_id="SYNTACTIC_RELATION_CLAIM",
        required_slots=frozenset(),
        optional_slots=frozenset(),
        not_applicable_slots=frozenset(),
        allowed_evidence_kinds=frozenset(),
        minimum_evidence_count=0,
        possible_residual_codes=frozenset(),
    ),
    "SEMANTIC_RELATION_CLAIM": ClaimProfile(
        profile_id="SEMANTIC_RELATION_CLAIM",
        required_slots=frozenset(),
        optional_slots=frozenset(),
        not_applicable_slots=frozenset(),
        allowed_evidence_kinds=frozenset(),
        minimum_evidence_count=0,
        possible_residual_codes=frozenset(),
    ),
    "EXISTENCE_CLAIM": ClaimProfile(
        profile_id="EXISTENCE_CLAIM",
        required_slots=frozenset(),
        optional_slots=frozenset(),
        not_applicable_slots=frozenset(),
        allowed_evidence_kinds=frozenset(),
        minimum_evidence_count=0,
        possible_residual_codes=frozenset(),
    ),
}

RESERVED_CLAIM_PROFILES: frozenset[str] = frozenset({
    "SYNTACTIC_RELATION_CLAIM",
    "SEMANTIC_RELATION_CLAIM",
    "EXISTENCE_CLAIM",
    "PROPERTY_CLAIM",
    "CLASS_MEMBERSHIP_CLAIM",
    "CAPABILITY_CLAIM",
})


# ── Claim Key ─────────────────────────────────────────────────────────────────

def compute_claim_key(
    claim_kind: str,
    profile_id: str,
    slot_values: dict[str, object],
    evidence_codes: Tuple[str, ...],
) -> str:
    """Deterministic SHA-256 hash of canonical claim content."""
    canonical = json.dumps({
        "claim_kind": claim_kind,
        "profile_id": profile_id,
        "slot_values": {k: str(v) for k, v in sorted(slot_values.items())},
        "evidence_codes": sorted(evidence_codes),
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ── HokomClaimBundle ──────────────────────────────────────────────────────────

@dataclass
class HokomClaimBundle:
    """
    The structured payload Hokom prepares for the bridge to pass to Taaqol.
    Bridge maps this to Taaqol's public claim API; does NOT interpret it.
    """
    claim_key: str           # compute_claim_key(...)
    claim_kind: str
    profile_id: str
    surface: SurfaceProvenance
    typed_slots: Tuple[TypedSlot, ...]
    candidate_sets: dict[str, CandidateSet]
    evidence_refs: Tuple[EvidenceReference, ...]
    condition_facts: Tuple[str, ...]
    obstacle_facts: Tuple[str, ...]
    defeater_facts: Tuple[str, ...]
    domain_licenses: Tuple[DomainTransitionLicense, ...]
    residuals: Tuple[HokomResidualRecord, ...]

    def __post_init__(self) -> None:
        # original_surface can never be lost
        self.surface.assert_original_preserved()


# ── Serialization ─────────────────────────────────────────────────────────────

def _serialize_slot(s: TypedSlot) -> dict:
    return {
        "slot_id": s.slot_id.value,
        "sort": s.sort.value,
        "state": s.state.value,
        "value": str(s.value) if s.value is not None else None,
        "owner": s.owner,
    }


def _deserialize_slot(d: dict) -> TypedSlot:
    state = SlotState(d["state"])
    value = d.get("value")
    # UNKNOWN state requires value=None
    if state == SlotState.UNKNOWN:
        value = None
    return TypedSlot(
        slot_id=SlotId(d["slot_id"]),
        sort=SlotSort(d["sort"]),
        state=state,
        value=value,
        owner=d.get("owner", "HOKOM"),
    )


def serialize_claim_bundle(bundle: HokomClaimBundle) -> dict:
    return {
        "claim_key": bundle.claim_key,
        "claim_kind": bundle.claim_kind,
        "profile_id": bundle.profile_id,
        "original_surface": bundle.surface.original_surface,
        "normalized_surface": bundle.surface.normalized_surface,
        "typed_slots": [_serialize_slot(s) for s in bundle.typed_slots],
        "condition_facts": list(bundle.condition_facts),
        "obstacle_facts": list(bundle.obstacle_facts),
        "defeater_facts": list(bundle.defeater_facts),
        "residuals": [
            {
                "residual_id": r.residual_id,
                "code": r.code,
                "kind": r.kind,
                "source_slot": r.source_slot.value,
                "reason": r.reason,
            }
            for r in bundle.residuals
        ],
    }


def deserialize_claim_bundle(d: dict) -> HokomClaimBundle:
    return HokomClaimBundle(
        claim_key=d["claim_key"],
        claim_kind=d["claim_kind"],
        profile_id=d["profile_id"],
        surface=SurfaceProvenance(
            original_surface=d["original_surface"],
            normalized_surface=d["normalized_surface"],
        ),
        typed_slots=tuple(_deserialize_slot(s) for s in d.get("typed_slots", [])),
        candidate_sets={},
        evidence_refs=(),
        condition_facts=tuple(d.get("condition_facts", [])),
        obstacle_facts=tuple(d.get("obstacle_facts", [])),
        defeater_facts=tuple(d.get("defeater_facts", [])),
        domain_licenses=(),
        residuals=(),
    )


__all__ = [
    "BoundaryType",
    "CandidateEntry",
    "CandidateSet",
    "ClaimProfile",
    "CLAIM_PROFILES",
    "RESERVED_CLAIM_PROFILES",
    "compute_claim_key",
    "deserialize_claim_bundle",
    "DomainTransitionLicense",
    "EvidenceReference",
    "GeminationType",
    "HokomClaimBundle",
    "HokomResidualRecord",
    "NormalizationOp",
    "serialize_claim_bundle",
    "SlotId",
    "SlotSort",
    "SlotState",
    "SurfaceProvenance",
    "TypedSlot",
]
