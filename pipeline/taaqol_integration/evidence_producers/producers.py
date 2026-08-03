"""C12 Hokom evidence producers — source-derived, fail-closed.

Each producer follows this discipline:
1. Consumes only canonical Hokom outputs or source-derived structural evidence.
2. Never invents linguistic content.
3. Emits typed carriers with a full ProvenanceEnvelope.
4. Returns None on missing/insufficient evidence (fail-closed).
"""
from __future__ import annotations

import hashlib
import subprocess
import uuid
from typing import Iterable, Optional

from .carriers import (
    AmilMamulCarrier,
    FormalShapeRegistryCarrier,
    MaqamEvidenceBundle,
    P9SentenceCarrier,
    P12IfadahCarrier,
    ProvenanceEnvelope,
    RelationCompatibilityCarrier,
    SpanCarrier,
)


def _hokom_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "UNKNOWN"


def _digest(payload: object) -> str:
    h = hashlib.sha256(repr(payload).encode("utf-8"))
    return h.hexdigest()[:16]


def _envelope(module: str, symbol: str, input_digest: str, output_digest: str) -> ProvenanceEnvelope:
    return ProvenanceEnvelope(
        producer_module=module,
        producer_symbol=symbol,
        producer_version="c12.v1",
        hokom_head=_hokom_head(),
        input_digest=input_digest,
        output_digest=output_digest,
    )


# ── Step 1: FormalShapeRegistry producer ─────────────────────────────────────


def build_formal_shape_registry(
    token_id: str,
    word_class: str,
    wazn: Optional[str],
    form_family: Optional[str],
    evidence_ids: Iterable[str] = (),
    trace_ids: Iterable[str] = (),
) -> Optional[FormalShapeRegistryCarrier]:
    """Emit a FormalShapeRegistry carrier only when all mandatory evidence present.

    Returns None if word_class is empty or if word_class is a licensing-inapplicable
    class (HARF) — the registry does not apply.
    """
    if not token_id or not word_class:
        return None
    if word_class == "HARF":
        # HARF is not a formal-shape-registry-applicable class.
        return None
    closure_state = "CLOSED" if (wazn and form_family) else "DEFERRED"
    input_digest = _digest((token_id, word_class, wazn, form_family))
    output_digest = _digest((closure_state, token_id, word_class, wazn, form_family))
    env = _envelope(
        "pipeline.taaqol_integration.evidence_producers.producers",
        "build_formal_shape_registry",
        input_digest, output_digest,
    )
    return FormalShapeRegistryCarrier(
        carrier_id=f"FSR-{token_id}-{output_digest[:8]}",
        token_id=token_id,
        word_class=word_class,
        wazn=wazn,
        form_family=form_family,
        closure_state=closure_state,
        evidence_ids=tuple(evidence_ids),
        provenance_ids=(f"HOKOM_HEAD::{env.hokom_head[:12]}",),
        trace_ids=tuple(trace_ids),
        envelope=env,
    )


# ── Step 3: P8 AMIL_MAMUL projector ──────────────────────────────────────────

# Closed-class operator surfaces recognized by pipeline.clause_graph.segmenter.
_OPERATOR_SURFACES = {
    "يَا": "vocative", "أَيُّهَا": "vocative",
    "إِذَا": "conditional", "إِنْ": "conditional", "لَوْ": "conditional",
    "الَّذِينَ": "relative_scope", "الَّذِي": "relative_scope",
    "لَا": "negation", "لَمْ": "negation", "لَنْ": "negation",
    "وَ": "conjunction", "فَ": "conjunction",
}


def project_amil_mamul(
    tokens: list[dict],
    clause_boundaries: list[dict],
) -> list[AmilMamulCarrier]:
    """Project AmilMamulCarrier records from clause boundaries + operator markers.

    Only opens a P8 record when a closed-class operator is present at the clause
    boundary AND at least one governed token exists within the same clause.
    Rejects arbitrary adjacency.
    """
    if not tokens or not clause_boundaries:
        return []
    carriers: list[AmilMamulCarrier] = []
    sorted_bounds = sorted(clause_boundaries, key=lambda b: b["token_index"])
    for i, b in enumerate(sorted_bounds):
        surface = b.get("operator_surface", "")
        if surface not in _OPERATOR_SURFACES:
            continue
        op_kind = _OPERATOR_SURFACES[surface]
        start = b["token_index"]
        end = sorted_bounds[i + 1]["token_index"] - 1 if i + 1 < len(sorted_bounds) else len(tokens) - 1
        governed = [f"TOKEN::{k+1:04d}" for k in range(start + 1, end + 1)]
        if not governed:
            continue
        input_digest = _digest((start, end, surface, tuple(governed)))
        output_digest = _digest(("AMIL_MAMUL", input_digest))
        env = _envelope(
            "pipeline.taaqol_integration.evidence_producers.producers",
            "project_amil_mamul",
            input_digest, output_digest,
        )
        carriers.append(AmilMamulCarrier(
            p8_id=f"P8-{b['clause_id']}-{output_digest[:8]}",
            clause_id=b["clause_id"],
            operator_id=f"OP-{surface}",
            amil_candidate_id=f"TOKEN::{start+1:04d}",
            mamul_candidate_ids=tuple(governed),
            structural_basis=f"{op_kind}_scope",
            direction="AMIL_TO_MAMUL",
            source_token_ids=(f"TOKEN::{start+1:04d}",) + tuple(governed),
            evidence_ids=(f"operator_surface:{surface}",
                          f"clause_boundary:{b['clause_id']}"),
            provenance_ids=(f"PRODUCER::project_amil_mamul", f"HOKOM_HEAD::{env.hokom_head[:12]}"),
            trace_ids=(f"P8::project_amil_mamul::{b['clause_id']}",),
            envelope=env,
        ))
    return carriers


# ── Step 4: SPAN producer ────────────────────────────────────────────────────


def produce_spans(
    amil_mamul_carriers: list[AmilMamulCarrier],
    sentence_id: str = "AYAT-SENTENCE-0001",
) -> list[SpanCarrier]:
    """Produce SpanCarrier records ONLY from P8 AmilMamul evidence.

    Rejects arbitrary adjacency. Every span carries construction_evidence_ids
    referencing the source P8 carrier.
    """
    if not amil_mamul_carriers:
        return []
    spans: list[SpanCarrier] = []
    for c in amil_mamul_carriers:
        # A span opens from amil→mamul: start = amil, end = last mamul.
        member_ids = (c.amil_candidate_id,) + c.mamul_candidate_ids
        start_id = c.amil_candidate_id
        end_id = c.mamul_candidate_ids[-1]
        input_digest = _digest((start_id, end_id, member_ids))
        output_digest = _digest(("SPAN", input_digest))
        env = _envelope(
            "pipeline.taaqol_integration.evidence_producers.producers",
            "produce_spans",
            input_digest, output_digest,
        )
        spans.append(SpanCarrier(
            span_id=f"SPAN-{c.clause_id}-{output_digest[:8]}",
            sentence_id=sentence_id,
            clause_id=c.clause_id,
            start_token_id=start_id,
            end_token_id=end_id,
            member_token_ids=member_ids,
            span_kind=c.structural_basis.upper().replace("_SCOPE", ""),
            construction_rule=f"opened_from_p8_amil_mamul::{c.structural_basis}",
            construction_evidence_ids=(c.p8_id,),
            operator_scope_ids=(c.operator_id,),
            provenance_ids=c.provenance_ids + (f"P8::{c.p8_id}",),
            trace_ids=c.trace_ids + (f"SPAN::produce_spans::{c.clause_id}",),
            closure_state="CLOSED",
            envelope=env,
        ))
    return spans


# ── Step 5: Relation compatibility carrier ───────────────────────────────────


def build_relation_compatibility(
    spans: list[SpanCarrier],
    contractable_unit_token_ids: set[str],
) -> list[RelationCompatibilityCarrier]:
    """Build RelationCompatibilityCarrier for pairs of ContractableUnit tokens within a span.

    Only tokens that have already reached ContractableUnitGeometry are eligible.
    Emits a compatibility carrier when at least 2 CU-eligible members exist.
    """
    compats: list[RelationCompatibilityCarrier] = []
    for span in spans:
        cu_members = [t for t in span.member_token_ids if t in contractable_unit_token_ids]
        if len(cu_members) < 2:
            continue
        left = cu_members[0]
        right = cu_members[-1]
        input_digest = _digest((span.span_id, left, right))
        output_digest = _digest(("REL_COMPAT", input_digest))
        env = _envelope(
            "pipeline.taaqol_integration.evidence_producers.producers",
            "build_relation_compatibility",
            input_digest, output_digest,
        )
        compats.append(RelationCompatibilityCarrier(
            compatibility_id=f"RCC-{span.clause_id}-{output_digest[:8]}",
            span_id=span.span_id,
            clause_id=span.clause_id,
            left_contractable_unit_id=left,
            right_contractable_unit_id=right,
            left_native_candidate_type="ContractableUnitGeometry",
            right_native_candidate_type="ContractableUnitGeometry",
            direction="LEFT_TO_RIGHT",
            structural_relation_hint="STRUCTURAL_PAIR_WITHIN_SPAN",
            compatibility_basis=span.construction_rule,
            p8_evidence_ids=span.construction_evidence_ids,
            clause_evidence_ids=(span.clause_id,),
            evidence_ids=(span.span_id,),
            provenance_ids=span.provenance_ids,
            trace_ids=span.trace_ids + (f"RCC::build_relation_compatibility::{span.span_id}",),
            ambiguity_state="UNAMBIGUOUS_STRUCTURAL",
            closure_state="COMPATIBLE",
            envelope=env,
        ))
    return compats


# ── Step 9: P9 sentence-geometry projector ───────────────────────────────────


def project_sentence_geometry(
    clause_boundaries: list[dict],
    orthographic_token_ids: list[str],
    sentence_id: str = "AYAT-SENTENCE-0001",
    source_offsets: tuple[int, int] = (0, 0),
) -> Optional[P9SentenceCarrier]:
    """Project one P9SentenceCarrier from existing clause boundaries + orthographic tokens.

    Sentence mode is populated only from explicit closed-class markers.
    """
    if not orthographic_token_ids:
        return None
    clause_ids = tuple(sorted({b["clause_id"] for b in clause_boundaries}))
    kind = "STRUCTURAL_CANDIDATE" if len(clause_ids) >= 2 else "ORTHOGRAPHIC"
    # Sentence mode: only from explicit markers at clause boundaries
    mode = None
    if any(b.get("boundary_type") == "JUXTAPOSITION" for b in clause_boundaries):
        mode = "VOCATIVE_ADDRESSEE_EVIDENCE_PRESENT"
    input_digest = _digest((sentence_id, clause_ids, orthographic_token_ids))
    output_digest = _digest(("P9", input_digest, kind, mode))
    env = _envelope(
        "pipeline.taaqol_integration.evidence_producers.producers",
        "project_sentence_geometry",
        input_digest, output_digest,
    )
    return P9SentenceCarrier(
        p9_id=f"P9-{sentence_id}-{output_digest[:8]}",
        sentence_id=sentence_id,
        member_clause_ids=clause_ids,
        member_token_ids=tuple(orthographic_token_ids),
        source_offsets=source_offsets,
        sentence_kind=kind,
        sentence_mode=mode,
        geometry_state="STRUCTURAL_MULTI_CLAUSE" if kind == "STRUCTURAL_CANDIDATE" else "ORTHOGRAPHIC_ONLY",
        boundary_evidence_ids=tuple(f"CLAUSE::{cid}" for cid in clause_ids),
        provenance_ids=(f"PRODUCER::project_sentence_geometry", f"HOKOM_HEAD::{env.hokom_head[:12]}"),
        trace_ids=(f"P9::project_sentence_geometry::{sentence_id}",),
        closure_state="STRUCTURAL_OPEN",
        envelope=env,
    )


# ── Step 10: Maqam evidence producer ─────────────────────────────────────────


def produce_maqam_evidence(
    p9_carrier: Optional[P9SentenceCarrier],
    clause_boundaries: list[dict],
) -> Optional[MaqamEvidenceBundle]:
    """Produce a MaqamEvidenceBundle only from explicit closed-class markers.

    Never infers speaker intention, historical circumstance, or unstated addressee.
    """
    if p9_carrier is None:
        return None
    markers: list[str] = []
    speaker_evidence = None
    addressee_evidence = None
    mode = None
    for b in clause_boundaries:
        bt = b.get("boundary_type", "")
        surface = b.get("operator_surface", "")
        if bt == "JUXTAPOSITION" and surface in ("يَا", "أَيُّهَا"):
            markers.append(f"vocative_marker:{surface}")
            addressee_evidence = "VOCATIVE_MARKER_PRESENT"
            mode = mode or "VOCATIVE_ADDRESS"
        elif bt == "CONDITIONAL":
            markers.append(f"conditional_marker:{surface}")
        elif bt == "NEGATION":
            markers.append(f"negation_marker:{surface}")
    if not markers:
        # Explicit-marker set empty — defer honestly
        input_digest = _digest((p9_carrier.p9_id, tuple(markers)))
        output_digest = _digest(("MAQAM_DEFERRED", input_digest))
        env = _envelope(
            "pipeline.taaqol_integration.evidence_producers.producers",
            "produce_maqam_evidence",
            input_digest, output_digest,
        )
        return MaqamEvidenceBundle(
            maqam_evidence_id=f"MAQAM-{p9_carrier.sentence_id}-DEFERRED",
            scope_type="SENTENCE",
            scope_id=p9_carrier.sentence_id,
            sentence_id=p9_carrier.sentence_id,
            clause_ids=p9_carrier.member_clause_ids,
            explicit_markers=(),
            closure_state="DEFERRED",
            evidence_ids=(),
            provenance_ids=(f"PRODUCER::produce_maqam_evidence",),
            trace_ids=(f"MAQAM::produce_maqam_evidence::{p9_carrier.sentence_id}",),
            envelope=env,
        )
    input_digest = _digest((p9_carrier.p9_id, tuple(markers)))
    output_digest = _digest(("MAQAM_DETECTED", input_digest))
    env = _envelope(
        "pipeline.taaqol_integration.evidence_producers.producers",
        "produce_maqam_evidence",
        input_digest, output_digest,
    )
    return MaqamEvidenceBundle(
        maqam_evidence_id=f"MAQAM-{p9_carrier.sentence_id}-{output_digest[:8]}",
        scope_type="SENTENCE",
        scope_id=p9_carrier.sentence_id,
        sentence_id=p9_carrier.sentence_id,
        clause_ids=p9_carrier.member_clause_ids,
        explicit_markers=tuple(markers),
        sentence_mode_evidence=mode,
        speaker_evidence=speaker_evidence,
        addressee_evidence=addressee_evidence,
        closure_state="DETECTED",
        evidence_ids=tuple(markers),
        provenance_ids=(f"PRODUCER::produce_maqam_evidence", f"HOKOM_HEAD::{env.hokom_head[:12]}"),
        trace_ids=(f"MAQAM::produce_maqam_evidence::{p9_carrier.sentence_id}",),
        envelope=env,
    )


# ── Step 12: P12 IfadahCandidate projector ───────────────────────────────────


def project_ifadah_candidate(
    relation_closure_id: Optional[str],
    formal_predecessor_ids: tuple[str, ...],
    maqam_boundary_id: Optional[str],
    sentence_id: str,
    clause_id: str,
) -> Optional[P12IfadahCarrier]:
    """Assemble P12 IfadahCandidate ONLY when all three predecessors present.

    Fail-closed otherwise. Never invents proposition shape.
    """
    if not (relation_closure_id and formal_predecessor_ids and maqam_boundary_id):
        return None
    input_digest = _digest((relation_closure_id, formal_predecessor_ids, maqam_boundary_id))
    output_digest = _digest(("P12", input_digest))
    env = _envelope(
        "pipeline.taaqol_integration.evidence_producers.producers",
        "project_ifadah_candidate",
        input_digest, output_digest,
    )
    return P12IfadahCarrier(
        p12_id=f"P12-{sentence_id}-{output_digest[:8]}",
        sentence_id=sentence_id,
        clause_id=clause_id,
        relation_closure_id=relation_closure_id,
        formal_predecessor_ids=formal_predecessor_ids,
        maqam_boundary_id=maqam_boundary_id,
        proposition_shape_source="STRUCTURAL_PREDECESSORS",
        scope_closure_state="CLOSED",
        rank="CANDIDATE",
        evidence_ids=(relation_closure_id, maqam_boundary_id) + formal_predecessor_ids,
        provenance_ids=(f"PRODUCER::project_ifadah_candidate", f"HOKOM_HEAD::{env.hokom_head[:12]}"),
        trace_ids=(f"P12::project_ifadah_candidate::{sentence_id}",),
        closure_state="READY_FOR_NATIVE_IFADAH",
        envelope=env,
    )
