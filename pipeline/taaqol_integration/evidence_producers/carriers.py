"""Typed carriers for the C12 Hokom evidence producers.

Each carrier is a frozen dataclass with a mandatory provenance envelope.
Carriers are Hokom-owned; they must not be relabelled as vendor verdicts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ProvenanceEnvelope:
    """Mandatory provenance for every C12 carrier."""
    producer_module: str
    producer_symbol: str
    producer_version: str
    schema_version: str = "1.0.0"
    registry_version: str = "c12.v1"
    hokom_head: str = ""
    target_taaqol_sha: str = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
    input_digest: str = ""
    output_digest: str = ""

    def is_complete(self) -> bool:
        return bool(self.producer_module and self.producer_symbol
                    and self.output_digest and self.hokom_head)


@dataclass(frozen=True)
class FormalShapeRegistryCarrier:
    """Hokom-owned FormalShapeRegistry-compatible carrier.

    Emitted only when word_class + wazn + form_family are all present
    from canonical Hokom evidence. Otherwise returns None from the producer.
    """
    carrier_id: str
    token_id: str
    word_class: str
    wazn: Optional[str]
    form_family: Optional[str]
    closure_state: str  # "CLOSED" | "DEFERRED" | "NOT_APPLICABLE"
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_ids: tuple[str, ...] = field(default_factory=tuple)
    trace_ids: tuple[str, ...] = field(default_factory=tuple)
    residual_codes: tuple[str, ...] = field(default_factory=tuple)
    ambiguity_codes: tuple[str, ...] = field(default_factory=tuple)
    envelope: Optional[ProvenanceEnvelope] = None


@dataclass(frozen=True)
class AmilMamulCarrier:
    """P8 amil/mamul span carrier — source-derived only.

    Constructed from explicit clause boundary + operator markers.
    Rejects arbitrary adjacency.
    """
    p8_id: str
    clause_id: str
    operator_id: str
    amil_candidate_id: str
    mamul_candidate_ids: tuple[str, ...]
    structural_basis: str  # e.g. "conditional_scope", "vocative_scope"
    direction: str  # "AMIL_TO_MAMUL" | "MAMUL_TO_AMIL" | "UNDETERMINED"
    source_token_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_ids: tuple[str, ...] = field(default_factory=tuple)
    trace_ids: tuple[str, ...] = field(default_factory=tuple)
    residual_codes: tuple[str, ...] = field(default_factory=tuple)
    ambiguity_state: str = "UNAMBIGUOUS"
    closure_state: str = "DETECTED"
    envelope: Optional[ProvenanceEnvelope] = None


@dataclass(frozen=True)
class SpanCarrier:
    """Source-derived span carrier.

    A span opens only from a valid P8 AmilMamulCarrier or explicit
    operator scope. Never from adjacency alone.
    """
    span_id: str
    sentence_id: str
    clause_id: str
    start_token_id: str
    end_token_id: str
    member_token_ids: tuple[str, ...]
    span_kind: str  # "AMIL_MAMUL" | "OPERATOR_SCOPE" | "CONJUNCTION"
    construction_rule: str
    construction_evidence_ids: tuple[str, ...]
    operator_scope_ids: tuple[str, ...] = field(default_factory=tuple)
    conjunction_scope_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_ids: tuple[str, ...] = field(default_factory=tuple)
    trace_ids: tuple[str, ...] = field(default_factory=tuple)
    residual_codes: tuple[str, ...] = field(default_factory=tuple)
    ambiguity_codes: tuple[str, ...] = field(default_factory=tuple)
    closure_state: str = "CLOSED"
    envelope: Optional[ProvenanceEnvelope] = None


@dataclass(frozen=True)
class RelationCompatibilityCarrier:
    """Structural compatibility carrier for two ContractableUnits within a span.

    `structural_relation_hint` is a Hokom structural label — NOT the
    vendor's expected relation verdict.
    """
    compatibility_id: str
    span_id: str
    clause_id: str
    left_contractable_unit_id: str
    right_contractable_unit_id: str
    left_native_candidate_type: str
    right_native_candidate_type: str
    direction: str
    structural_relation_hint: str  # "VERB_ARGUMENT" | "MODIFIER_HEAD" etc — structural only
    compatibility_basis: str
    operator_evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    p8_evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    clause_evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_ids: tuple[str, ...] = field(default_factory=tuple)
    trace_ids: tuple[str, ...] = field(default_factory=tuple)
    residual_codes: tuple[str, ...] = field(default_factory=tuple)
    ambiguity_state: str = "UNAMBIGUOUS"
    closure_state: str = "COMPATIBLE"
    envelope: Optional[ProvenanceEnvelope] = None


@dataclass(frozen=True)
class P9SentenceCarrier:
    """P9 sentence-geometry projector output."""
    p9_id: str
    sentence_id: str
    member_clause_ids: tuple[str, ...]
    member_token_ids: tuple[str, ...]
    source_offsets: tuple[int, int]
    sentence_kind: str  # "ORTHOGRAPHIC" | "STRUCTURAL_CANDIDATE" | "STRUCTURAL_CLOSED" | "COMPOUND_UNRESOLVED"
    sentence_mode: Optional[str] = None  # populated only from explicit markers
    geometry_state: str = "OPEN"
    operator_scope_ids: tuple[str, ...] = field(default_factory=tuple)
    conjunction_scope_ids: tuple[str, ...] = field(default_factory=tuple)
    boundary_evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_ids: tuple[str, ...] = field(default_factory=tuple)
    trace_ids: tuple[str, ...] = field(default_factory=tuple)
    residual_codes: tuple[str, ...] = field(default_factory=tuple)
    ambiguity_codes: tuple[str, ...] = field(default_factory=tuple)
    closure_state: str = "OPEN"
    envelope: Optional[ProvenanceEnvelope] = None


@dataclass(frozen=True)
class MaqamEvidenceBundle:
    """Explicit-context evidence for maqam.

    Only populated from explicit clause markers (vocative, conditional,
    negation, relative). Never inferred.
    """
    maqam_evidence_id: str
    scope_type: str  # "SENTENCE" | "CLAUSE"
    scope_id: str
    sentence_id: str
    clause_ids: tuple[str, ...]
    explicit_markers: tuple[str, ...]
    sentence_mode_evidence: Optional[str] = None
    speaker_evidence: Optional[str] = None
    addressee_evidence: Optional[str] = None
    preceding_scope_ids: tuple[str, ...] = field(default_factory=tuple)
    following_scope_ids: tuple[str, ...] = field(default_factory=tuple)
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_ids: tuple[str, ...] = field(default_factory=tuple)
    trace_ids: tuple[str, ...] = field(default_factory=tuple)
    residual_codes: tuple[str, ...] = field(default_factory=tuple)
    ambiguity_codes: tuple[str, ...] = field(default_factory=tuple)
    closure_state: str = "DETECTED"  # "DETECTED" | "DEFERRED"
    envelope: Optional[ProvenanceEnvelope] = None


@dataclass(frozen=True)
class P12IfadahCarrier:
    """P12 IfadahCandidate projector output.

    Assembles RelationClosureVerdict + FormalStyleVerdict + MaqamContextBoundaryVerdict.
    Fail-closed if any predecessor is missing.
    """
    p12_id: str
    sentence_id: str
    clause_id: str
    relation_closure_id: Optional[str]
    formal_predecessor_ids: tuple[str, ...]
    maqam_boundary_id: Optional[str]
    proposition_shape_source: str
    scope_closure_state: str
    rank: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_ids: tuple[str, ...] = field(default_factory=tuple)
    trace_ids: tuple[str, ...] = field(default_factory=tuple)
    residual_codes: tuple[str, ...] = field(default_factory=tuple)
    ambiguity_codes: tuple[str, ...] = field(default_factory=tuple)
    closure_state: str = "READY_FOR_NATIVE_IFADAH"
    envelope: Optional[ProvenanceEnvelope] = None


@dataclass(frozen=True)
class VendorAdapterResult:
    """Result of invoking a vendor native law via a Hokom adapter."""
    adapter_module: str
    adapter_symbol: str
    native_module: str
    native_symbol: str
    native_source_path: str
    native_source_sha256: str
    vendor_commit: str
    exact_input_type: str
    exact_output_type: str
    native_call_executed: bool
    duration_ms: float
    native_output: object = None
    failure_code: Optional[str] = None
    residual_codes: tuple[str, ...] = field(default_factory=tuple)
    provenance_ids: tuple[str, ...] = field(default_factory=tuple)
    trace_ids: tuple[str, ...] = field(default_factory=tuple)
