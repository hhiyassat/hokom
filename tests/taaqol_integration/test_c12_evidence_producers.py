"""C12 Hokom evidence producers — targeted tests.

Validates the seven Hokom producers + Hokom→vendor relation adapter
implemented under HOKOM-MISSING-EVIDENCE-PRODUCERS-IMPLEMENTATION-01,
plus the shape of C12 artifacts.

Anti-invention discipline:
- No producer may emit a carrier without source-derived evidence.
- No adapter may fabricate a vendor verdict.
- Fail-closed on missing predecessors.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
REPORTS = REPO / "reports" / "taaqol_full_integration"
TARGET_SHA = "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"


def _load(name):
    p = REPORTS / name
    assert p.exists(), f"missing artifact: {name}"
    return json.loads(p.read_text())


# ── Contracts manifest ────────────────────────────────────────────────────


def test_c12_contracts_manifest_shape() -> None:
    doc = _load("C12_NATIVE_VERTICAL_CONTRACTS.json")
    assert doc["target_taaqol_sha"] == TARGET_SHA
    assert doc["totals"]["C12_CONTRACTS_TOTAL"] == 21
    assert doc["totals"]["C12_CONTRACTS_UNREVIEWED"] == 0
    assert len(doc["steps"]) == 21


# ── Producer implementations ─────────────────────────────────────────────


def test_formal_shape_registry_producer() -> None:
    from pipeline.taaqol_integration.evidence_producers.producers import (
        build_formal_shape_registry,
    )
    # Positive: word_class + wazn + form_family present → CLOSED
    c = build_formal_shape_registry("TOKEN::0007", "ISM", "FA3L", "FORM_I",
                                    evidence_ids=("P3::word_class::ISM",))
    assert c is not None
    assert c.closure_state == "CLOSED"
    assert c.token_id == "TOKEN::0007"
    assert c.envelope is not None
    assert c.envelope.hokom_head
    # Negative: missing wazn → DEFERRED (not CLOSED)
    d = build_formal_shape_registry("TOKEN::0006", "FI3L", None, None)
    assert d is not None
    assert d.closure_state == "DEFERRED"
    # Negative: HARF → None (NOT_APPLICABLE)
    h = build_formal_shape_registry("TOKEN::0001", "HARF", None, None)
    assert h is None
    # Negative: empty token_id → None
    e = build_formal_shape_registry("", "ISM", "FA3L", "FORM_I")
    assert e is None


def test_p8_amil_mamul_projector() -> None:
    from pipeline.taaqol_integration.evidence_producers.producers import project_amil_mamul
    tokens = [
        {"surface": "يَا", "word_class": "HARF"},
        {"surface": "زَيْدُ", "word_class": "ISM"},
        {"surface": "قَامَ", "word_class": "FI3L"},
    ]
    boundaries = [{"clause_id": "TEST-CLAUSE-001", "token_index": 0,
                   "operator_surface": "يَا", "boundary_type": "JUXTAPOSITION"}]
    carriers = project_amil_mamul(tokens, boundaries)
    assert len(carriers) == 1
    assert carriers[0].structural_basis == "vocative_scope"
    assert carriers[0].amil_candidate_id == "TOKEN::0001"
    assert len(carriers[0].mamul_candidate_ids) >= 1
    # Empty input → empty output
    assert project_amil_mamul([], []) == []
    # Unknown operator → no carrier
    boundaries2 = [{"clause_id": "X", "token_index": 0, "operator_surface": "unknown", "boundary_type": "X"}]
    assert project_amil_mamul(tokens, boundaries2) == []


def test_span_producer_source_derived_only() -> None:
    from pipeline.taaqol_integration.evidence_producers.producers import (
        project_amil_mamul, produce_spans,
    )
    # Empty P8 → 0 spans (rejects arbitrary adjacency)
    assert produce_spans([]) == []
    # Positive: P8 exists → span opens
    tokens = [{"surface": "يَا", "word_class": "HARF"},
              {"surface": "زَيْدُ", "word_class": "ISM"}]
    b = [{"clause_id": "TC-1", "token_index": 0, "operator_surface": "يَا", "boundary_type": "JUXTAPOSITION"}]
    p8 = project_amil_mamul(tokens, b)
    spans = produce_spans(p8)
    assert len(spans) == 1
    assert spans[0].construction_evidence_ids == (p8[0].p8_id,)
    assert spans[0].closure_state == "CLOSED"


def test_relation_compatibility_needs_two_cu_tokens() -> None:
    from pipeline.taaqol_integration.evidence_producers.producers import (
        build_relation_compatibility, project_amil_mamul, produce_spans,
    )
    tokens = [{"surface": "يَا"}, {"surface": "زَيْدُ"}, {"surface": "قَامَ"}]
    b = [{"clause_id": "TC-1", "token_index": 0,
          "operator_surface": "يَا", "boundary_type": "JUXTAPOSITION"}]
    p8 = project_amil_mamul(tokens, b)
    spans = produce_spans(p8)
    # No CU tokens → no compatibility carrier
    assert build_relation_compatibility(spans, set()) == []
    # Only 1 CU → no compatibility carrier
    assert build_relation_compatibility(spans, {"TOKEN::0002"}) == []
    # 2+ CU tokens within span → compatibility carrier
    compat = build_relation_compatibility(spans, {"TOKEN::0002", "TOKEN::0003"})
    assert len(compat) == 1
    assert compat[0].left_contractable_unit_id == "TOKEN::0002"
    assert compat[0].right_contractable_unit_id == "TOKEN::0003"
    assert compat[0].structural_relation_hint == "STRUCTURAL_PAIR_WITHIN_SPAN"
    # Anti-invention: hint must NOT be a vendor verdict term
    forbidden_verdict_terms = ("PROVEN", "COMPOSED", "CLOSED_VERDICT", "IFADAH", "HUKM")
    for term in forbidden_verdict_terms:
        assert term not in compat[0].structural_relation_hint


def test_p9_sentence_geometry_projector() -> None:
    from pipeline.taaqol_integration.evidence_producers.producers import (
        project_sentence_geometry,
    )
    # Empty tokens → None
    assert project_sentence_geometry([], []) is None
    # Positive: multi-clause → STRUCTURAL_CANDIDATE
    clauses = [{"clause_id": "C1", "token_index": 0, "operator_surface": "يَا",
                "boundary_type": "JUXTAPOSITION"},
               {"clause_id": "C2", "token_index": 3, "operator_surface": "إِذَا",
                "boundary_type": "CONDITIONAL"}]
    tokens = ["T1", "T2", "T3", "T4"]
    p9 = project_sentence_geometry(clauses, tokens)
    assert p9 is not None
    assert p9.sentence_kind == "STRUCTURAL_CANDIDATE"
    assert len(p9.member_clause_ids) == 2
    # sentence_mode should only be populated from explicit markers
    assert p9.sentence_mode == "VOCATIVE_ADDRESSEE_EVIDENCE_PRESENT"


def test_maqam_evidence_only_from_explicit_markers() -> None:
    from pipeline.taaqol_integration.evidence_producers.producers import (
        project_sentence_geometry, produce_maqam_evidence,
    )
    # No P9 → None
    assert produce_maqam_evidence(None, []) is None
    # P9 with no marker clauses → DEFERRED (not fabricated positive)
    p9 = project_sentence_geometry([{"clause_id": "C1", "token_index": 0,
                                     "operator_surface": "X", "boundary_type": "OTHER"}],
                                    ["T1"])
    maqam = produce_maqam_evidence(p9, [])
    assert maqam is not None
    assert maqam.closure_state == "DEFERRED"
    assert len(maqam.explicit_markers) == 0
    # P9 with explicit vocative → DETECTED
    p9b = project_sentence_geometry([{"clause_id": "C1", "token_index": 0,
                                       "operator_surface": "يَا", "boundary_type": "JUXTAPOSITION"}],
                                     ["T1", "T2"])
    maqam2 = produce_maqam_evidence(p9b, [{"clause_id": "C1", "token_index": 0,
                                            "operator_surface": "يَا", "boundary_type": "JUXTAPOSITION"}])
    assert maqam2.closure_state == "DETECTED"
    assert any("vocative_marker" in m for m in maqam2.explicit_markers)


def test_p12_ifadah_fail_closed() -> None:
    from pipeline.taaqol_integration.evidence_producers.producers import project_ifadah_candidate
    # Missing any predecessor → None
    assert project_ifadah_candidate(None, ("F1",), "M1", "S1", "C1") is None
    assert project_ifadah_candidate("R1", (), "M1", "S1", "C1") is None
    assert project_ifadah_candidate("R1", ("F1",), None, "S1", "C1") is None
    # All present → carrier
    c = project_ifadah_candidate("R1", ("F1",), "M1", "S1", "C1")
    assert c is not None
    assert c.closure_state == "READY_FOR_NATIVE_IFADAH"


# ── Hokom→vendor relation adapter ────────────────────────────────────────


def test_vendor_relation_adapter_import_ok() -> None:
    """The vendor RelationCandidate law must be import-callable at target SHA."""
    from taaqqul_slot_geometry.weight.relation_candidate import prove_relation_candidate
    import inspect
    src = inspect.getfile(prove_relation_candidate)
    assert "vendor/Taaqol-GPT" in src, f"native symbol outside vendor: {src}"


def test_vendor_relation_adapter_fails_closed_without_cu() -> None:
    from pipeline.taaqol_integration.evidence_producers.carriers import (
        RelationCompatibilityCarrier, ProvenanceEnvelope,
    )
    from pipeline.taaqol_integration.evidence_producers.vendor_relation_adapter import (
        invoke_native_relation_candidate,
    )
    rcc = RelationCompatibilityCarrier(
        compatibility_id="TEST-RCC-001",
        span_id="TEST-SPAN-001",
        clause_id="TEST-C-001",
        left_contractable_unit_id="TOKEN::0007",
        right_contractable_unit_id="TOKEN::0009",
        left_native_candidate_type="ContractableUnitGeometry",
        right_native_candidate_type="ContractableUnitGeometry",
        direction="LEFT_TO_RIGHT",
        structural_relation_hint="STRUCTURAL_PAIR_WITHIN_SPAN",
        compatibility_basis="test",
    )
    # Empty CU lookup → fail-closed with MISSING_NATIVE_CONTRACTABLE_UNIT
    r = invoke_native_relation_candidate(rcc, contractable_unit_lookup={})
    assert r.native_call_executed is False
    assert r.failure_code == "MISSING_NATIVE_CONTRACTABLE_UNIT"
    assert r.vendor_commit == TARGET_SHA


def test_vendor_relation_adapter_rejects_wrong_type() -> None:
    from pipeline.taaqol_integration.evidence_producers.carriers import (
        RelationCompatibilityCarrier,
    )
    from pipeline.taaqol_integration.evidence_producers.vendor_relation_adapter import (
        invoke_native_relation_candidate,
    )
    rcc = RelationCompatibilityCarrier(
        compatibility_id="TEST-RCC-002",
        span_id="TEST-SPAN-002", clause_id="TEST-C-002",
        left_contractable_unit_id="A", right_contractable_unit_id="B",
        left_native_candidate_type="ContractableUnitGeometry",
        right_native_candidate_type="ContractableUnitGeometry",
        direction="LEFT_TO_RIGHT",
        structural_relation_hint="X", compatibility_basis="X",
    )
    # Wrong type in CU lookup → adapter passes to vendor which will refuse
    r = invoke_native_relation_candidate(rcc, contractable_unit_lookup={
        "A": "not a real CU", "B": "not a real CU",
    })
    # Vendor rejects with type error; native_call_executed=False, failure_code populated
    assert r.native_call_executed is False
    assert r.failure_code is not None
    assert "VENDOR_CALL_FAILED" in r.failure_code


# ── Artifact-level integrity ─────────────────────────────────────────────


def test_c12_artifacts_shape() -> None:
    for name in [
        "C12_NATIVE_VERTICAL_CONTRACTS.json",
        "C12_HOKOM_EVIDENCE_PRODUCERS.json",
        "C12_AYAT_SOURCE_DERIVED_SPANS.json",
        "C12_RELATION_COMPATIBILITY.json",
        "C12_SENTENCE_MAQAM_EVIDENCE.json",
        "C12_VERTICAL_STAGE_RECORDS.json",
    ]:
        doc = _load(name)
        assert doc["target_taaqol_sha"] == TARGET_SHA, f"{name} SHA mismatch"


def test_ayat_spans_carry_provenance() -> None:
    doc = _load("C12_AYAT_SOURCE_DERIVED_SPANS.json")
    assert doc["totals"]["ARBITRARY_ADJACENCY_SPAN_COUNT"] == 0
    assert doc["totals"]["SPAN_WITHOUT_PROVENANCE"] == 0
    assert doc["totals"]["SPAN_WITHOUT_TRACE"] == 0
    for span in doc["spans"]:
        assert span["provenance_ids"], f"{span['span_id']} missing provenance"
        assert span["trace_ids"], f"{span['span_id']} missing trace"
        assert span["construction_evidence_ids"], f"{span['span_id']} missing evidence"


def test_relation_compatibility_no_vendor_verdict_fields() -> None:
    doc = _load("C12_RELATION_COMPATIBILITY.json")
    assert doc["totals"]["RELATION_EXPECTED_VERDICT_FIELDS"] == 0
    for rcc in doc["compatibility_carriers"]:
        # Anti-invention: hint must be structural only, not a vendor verdict
        hint = rcc["structural_relation_hint"]
        for forbidden in ("PROVEN", "COMPOSED", "CLOSED_VERDICT", "IFADAH_VERDICT"):
            assert forbidden not in hint, f"vendor verdict term in structural hint: {hint}"


def test_vertical_stage_records_no_synthetic_ayat_execution() -> None:
    doc = _load("C12_VERTICAL_STAGE_RECORDS.json")
    # Vendor stages must not report AYAT execution unless upstream chain is proven
    for s in doc["stages"]:
        if s["layer"] == "TAAQOL_NATIVE" and s["ayat_executed"] > 0:
            # If any vendor stage reports Ayat execution, RelationClosure must have too
            rc = next((x for x in doc["stages"] if x["stage"] == "RelationClosure (native)"), None)
            assert rc is not None and rc["ayat_executed"] > 0, \
                f"vendor stage {s['stage']} reports ayat_executed>0 but RelationClosure did not"
    assert doc["totals"]["LIVE_PROVIDER_CALL_COUNT"] == 0
    assert doc["totals"]["NETWORK_PROVIDER_CALL_COUNT"] == 0


def test_c12_producers_no_direct_verdict_injection() -> None:
    doc = _load("C12_HOKOM_EVIDENCE_PRODUCERS.json")
    prods = doc["producers"]
    assert prods["formal_shape_registry"]["direct_verdict_injections"] == 0
    assert prods["p8_amil_mamul"]["false_positives"] == 0
    assert prods["span_producer"]["arbitrary_adjacency_spans"] == 0
    assert prods["relation_compatibility"]["expected_verdict_fields"] == 0
    assert prods["maqam_evidence"]["token_only_maqam_count"] == 0
    assert prods["maqam_evidence"]["inferred_intention_count"] == 0
    assert prods["p12_ifadah_candidate"]["direct_injection_count"] == 0
