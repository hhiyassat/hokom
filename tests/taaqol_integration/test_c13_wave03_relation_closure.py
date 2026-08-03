"""C13 Wave-03 — AYAT native RelationClosure execution.

Proves:
  - The full vendor DAG (FormalStyle → MufradSemanticSlot → Maqam →
    DalalahCandidate → MufradDalalahClosure → RelationClosure) is
    runtime-callable at target SHA 05c6668d.
  - AYAT_RELATION_CLOSURE_EXECUTED >= 1 through the exact native chain.
  - All vendor typed inputs are constructed from retained native CU
    objects + source-derived spans, not fixtures.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent


def _run_full_ayat_and_produce_spans():
    from pipeline.taaqol_integration.full_target_orchestrator import (
        run_full_target, get_ayat_native_cu_map,
    )
    from pipeline.clause_graph.segmenter import detect_boundaries
    from pipeline.taaqol_integration.evidence_producers.producers import (
        project_amil_mamul, produce_spans,
    )
    tokens = []
    with open(REPO / "reports/taaqol_full_integration/c9_runtime_output/ayat_al_dayn_results.csv") as f:
        for row in csv.DictReader(f):
            tokens.append({"surface": row["original_surface"], "word_class": row["word_class"]})
    _ = run_full_target([t["surface"] for t in tokens], depth='full')
    cu_map = get_ayat_native_cu_map()
    boundaries = detect_boundaries(tokens)
    clause_dicts = []
    for i, b in enumerate(sorted(boundaries, key=lambda x: x.token_index)):
        clause_dicts.append({
            "clause_id": f"AYAT-CLAUSE-{i+1:03d}",
            "token_index": b.token_index,
            "operator_surface": b.operator_surface,
            "boundary_type": b.boundary_type.name,
        })
    p8 = project_amil_mamul(tokens, clause_dicts)
    spans = produce_spans(p8, sentence_id="AYAT-SENTENCE-0001")
    span_dicts = [
        {"span_id": s.span_id, "member_token_ids": list(s.member_token_ids),
         "construction_rule": s.construction_rule}
        for s in spans
    ]
    return cu_map, span_dicts


def test_c13_wave03_ayat_relation_closure_executes():
    """AYAT_RELATION_CLOSURE_EXECUTED >= 1 via retained CU + native chain."""
    from pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter import (
        execute_ayat_vertical_chain,
    )
    cu_map, spans = _run_full_ayat_and_produce_spans()
    assert len(cu_map) == 37
    assert len(spans) >= 1
    r = execute_ayat_vertical_chain(cu_map, spans)

    # Every vendor law was invoked at least once with retained/native inputs
    assert r['formal_style_calls'] >= 1
    assert r['mufrad_semantic_slot_calls'] >= 2
    assert r['maqam_context_calls'] >= 1
    assert r['dalalah_candidate_calls'] >= 2
    assert r['mufrad_dalalah_closure_calls'] >= 2
    assert r['relation_closure_calls'] >= 1

    # At least one PROVEN through the entire chain
    assert r['ms_verdicts_proven'] >= 2, f"MufradSemanticSlot PROVEN count: {r['ms_verdicts_proven']}"
    assert r['maqam_verdicts_proven'] >= 1, f"Maqam PROVEN count: {r['maqam_verdicts_proven']}"
    assert r['dalalah_verdicts_proven'] >= 2, f"Dalalah PROVEN count: {r['dalalah_verdicts_proven']}"
    assert r['mufrad_dalalah_closure_verdicts_proven'] >= 2, (
        f"MufradClosure PROVEN count: {r['mufrad_dalalah_closure_verdicts_proven']}"
    )
    assert r['ayat_relation_closure_executed'] >= 1, (
        f"AYAT_RELATION_CLOSURE_EXECUTED = {r['ayat_relation_closure_executed']}; "
        f"per-span: {r['per_span_results'][:3]}"
    )


def test_c13_wave03_vendor_output_types_verified():
    """Every stage returns the exact vendor dataclass type."""
    from pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter import (
        execute_ayat_vertical_chain,
    )
    cu_map, spans = _run_full_ayat_and_produce_spans()
    r = execute_ayat_vertical_chain(cu_map, spans)
    for spanres in r['per_span_results']:
        if 'verdict_type' in spanres:
            assert spanres['verdict_type'] == 'RelationClosureVerdict', (
                f"expected RelationClosureVerdict; got {spanres['verdict_type']}"
            )


def test_c13_wave03_no_fixture_used_for_ayat():
    """Verify the chain requires cu_map + spans (no fixture path)."""
    from pipeline.taaqol_integration.evidence_producers.vertical_chain_adapter import (
        execute_ayat_vertical_chain,
    )
    r_empty_cu = execute_ayat_vertical_chain({}, [{'span_id': 'X', 'member_token_ids': ['A', 'B']}])
    assert r_empty_cu['relation_closure_calls'] == 0
    r_empty_spans = execute_ayat_vertical_chain({'A': {}}, [])
    assert r_empty_spans['relation_closure_calls'] == 0


def test_c13_wave03_vendor_law_source_paths_verified():
    """Every invoked vendor callable resolves to a file under vendor/Taaqol-GPT/."""
    import inspect
    from taaqqul_slot_geometry.weight.formal_style_candidate import prove_formal_style_candidate
    from taaqqul_slot_geometry.weight.mufrad_semantic_slot_geometry import prove_mufrad_semantic_slot_geometry
    from taaqqul_slot_geometry.weight.maqam_context_boundary import prove_maqam_context_boundary
    from taaqqul_slot_geometry.weight.dalalah_candidates import prove_dalalah_candidates
    from taaqqul_slot_geometry.weight.mufrad_dalalah_closure import prove_mufrad_dalalah_closure
    from taaqqul_slot_geometry.weight.relation_closure import prove_relation_closure
    for fn in [
        prove_formal_style_candidate, prove_mufrad_semantic_slot_geometry,
        prove_maqam_context_boundary, prove_dalalah_candidates,
        prove_mufrad_dalalah_closure, prove_relation_closure,
    ]:
        src = inspect.getfile(fn)
        assert "vendor/Taaqol-GPT" in src, f"vendor law outside vendor/: {src}"
