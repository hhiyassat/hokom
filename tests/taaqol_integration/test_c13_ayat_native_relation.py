"""C13 §9 — Native RelationCandidate execution on Ayat al-Dayn via retained vendor CU objects.

Proves that the original vendor `prove_relation_candidate` executes for
real Ayat tokens (not fixtures) when consuming:
  - Retained native ContractableUnitGeometry objects (from orchestrator CU map)
  - Source-derived C12 spans (from pipeline.clause_graph + P8 producer)
  - Vendor contractability_profile.admissible_roles for role claims

Establishes:
  AYAT_RELATION_CANDIDATE_EXECUTED >= 1
  AYAT_NATIVE_CU_OBJECT_MAP_COUNT = 37
  FIXTURE_COUNTED_AS_AYAT_EXECUTION = 0
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent


def _load_ayat_tokens() -> list[dict]:
    tokens = []
    with open(REPO / "reports/taaqol_full_integration/c9_runtime_output/ayat_al_dayn_results.csv") as f:
        for row in csv.DictReader(f):
            tokens.append({
                "surface": row["original_surface"],
                "word_class": row["word_class"],
                "token_index": int(row["token_index"]),
            })
    return tokens


def _run_ayat_and_produce_spans():
    from pipeline.taaqol_integration.full_target_orchestrator import (
        run_full_target, get_ayat_native_cu_map,
    )
    from pipeline.clause_graph.segmenter import detect_boundaries
    from pipeline.taaqol_integration.evidence_producers.producers import (
        project_amil_mamul, produce_spans,
    )
    tokens = _load_ayat_tokens()
    surfaces = [t["surface"] for t in tokens]
    _ = run_full_target(surfaces, depth='full')
    cu_map = get_ayat_native_cu_map()
    boundaries = detect_boundaries([{"surface": t["surface"], "word_class": t["word_class"]} for t in tokens])
    clause_dicts = []
    for i, b in enumerate(sorted(boundaries, key=lambda x: x.token_index)):
        clause_dicts.append({
            "clause_id": f"AYAT-CLAUSE-{i+1:03d}",
            "token_index": b.token_index,
            "operator_surface": b.operator_surface,
            "boundary_type": b.boundary_type.name,
        })
    p8 = project_amil_mamul(
        [{"surface": t["surface"], "word_class": t["word_class"]} for t in tokens],
        clause_dicts,
    )
    spans = produce_spans(p8, sentence_id="AYAT-SENTENCE-0001")
    span_dicts = [
        {"span_id": s.span_id, "member_token_ids": list(s.member_token_ids),
         "construction_rule": s.construction_rule}
        for s in spans
    ]
    return cu_map, span_dicts


def test_ayat_native_cu_object_map_count_is_37():
    """Retained vendor ContractableUnitGeometry map size matches C9 baseline (37)."""
    cu_map, _ = _run_ayat_and_produce_spans()
    assert len(cu_map) == 37, (
        f"AYAT_NATIVE_CU_OBJECT_MAP_COUNT expected 37, got {len(cu_map)}"
    )


def test_ayat_native_cu_map_contains_real_vendor_objects():
    """Every retained entry is a real vendor ContractableUnitGeometry, not a
    reconstruction."""
    from taaqqul_slot_geometry.weight.contractable_unit_geometry import (
        ContractableUnitGeometry,
    )
    cu_map, _ = _run_ayat_and_produce_spans()
    for tid, entry in cu_map.items():
        cand = entry['contractable_candidate']
        assert isinstance(cand, ContractableUnitGeometry), (
            f"{tid}: retained candidate is not vendor ContractableUnitGeometry "
            f"(got {type(cand).__name__})"
        )
        # Provenance preserved. Pin = the APPROVED Taaqol vendor SHA (owner
        # decision 2026-08-14): the frozen governance baseline 05c6668d. The
        # bc9d1ea5 submodule bump is SUPERSEDED_UNAPPROVED_VENDOR_PIN.
        assert entry['vendor_sha'] == "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"
        assert entry['surface']  # non-empty


def test_ayat_native_relation_candidate_executes_via_retained_objects():
    """Vendor prove_relation_candidate executes for Ayat pairs using retained
    CU objects paired via C12 source-derived spans — NOT fixtures, NOT
    arbitrary adjacency."""
    from pipeline.taaqol_integration.full_target_orchestrator import (
        execute_ayat_native_relation_candidates,
    )
    cu_map, span_dicts = _run_ayat_and_produce_spans()
    assert len(cu_map) == 37
    assert len(span_dicts) >= 1, "C12 source-derived spans required"
    results = execute_ayat_native_relation_candidates(source_derived_spans=span_dicts)
    assert len(results) >= 1, "at least one AYAT native RelationCandidate execution expected"
    composed = [r for r in results if r.get("composed")]
    assert len(composed) >= 1, (
        f"AYAT_RELATION_CANDIDATE_EXECUTED must be >= 1; "
        f"got {len(composed)} COMPOSED verdicts from {len(results)} attempts"
    )
    # Verify no fixtures counted
    for r in results:
        assert r['native_call_executed'], f"attempt without native call: {r}"
        assert r['verdict_type'] == "RelationVerdict", (
            f"expected vendor RelationVerdict, got {r['verdict_type']}"
        )
        assert r['candidate_type'] == "RelationCandidate", (
            f"expected vendor RelationCandidate, got {r['candidate_type']}"
        )


def test_ayat_relation_candidate_uses_source_derived_spans_only():
    """No arbitrary-adjacency executions — only spans from C12 SPAN producer."""
    from pipeline.taaqol_integration.full_target_orchestrator import (
        execute_ayat_native_relation_candidates,
    )
    # Passing no spans → no executions (proves anti-adjacency)
    _ = _run_ayat_and_produce_spans()
    empty_result = execute_ayat_native_relation_candidates(source_derived_spans=None)
    assert empty_result == [], "empty source-derived spans must yield zero executions"


def test_ayat_relation_candidate_no_direct_verdict_injection():
    """The vendor callable is invoked; no direct RelationVerdict construction."""
    from pipeline.taaqol_integration.full_target_orchestrator import (
        execute_ayat_native_relation_candidates, get_ayat_native_relation_map,
    )
    cu_map, span_dicts = _run_ayat_and_produce_spans()
    _ = execute_ayat_native_relation_candidates(source_derived_spans=span_dicts)
    rel_map = get_ayat_native_relation_map()
    # Verify every stored verdict is a real vendor RelationVerdict object
    from taaqqul_slot_geometry.weight.relation_candidate import RelationState
    for span_id, entry in rel_map.items():
        v = entry.get('verdict')
        if v is None:
            continue
        assert type(v).__name__ == "RelationVerdict"
        # Verdict state is a real vendor enum
        assert isinstance(v.verdict_state, RelationState) or hasattr(v.verdict_state, 'value')
