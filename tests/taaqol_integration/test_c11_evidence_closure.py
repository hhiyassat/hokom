"""C11 Hokom evidence production closure — targeted tests.

Validates the artifacts produced under HOKOM-EVIDENCE-PRODUCTION-CLOSURE-01
without regressing C9 or C10.

Covers:
- Evidence production inventory shape.
- Lexical evidence closure (129 tokens).
- Clause evidence (source-derived, no gold leakage).
- Span/relation/maqam producer status (honestly 0 for Ayat where no producer exists).
- LCX-150 evidence production.
- Vertical anti-leap invariants.
- Determinism of clause segmenter output.
- Provenance/trace/source continuity.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
REPORTS = REPO / "reports" / "taaqol_full_integration"
TARGET_SHA = "05c6668dfb95d9238cff5df1d8bc73d0664bccb3"


def _load(name):
    p = REPORTS / name
    assert p.exists(), f"missing artifact: {name}"
    return json.loads(p.read_text())


# ── Evidence production inventory ────────────────────────────────────────


def test_evidence_inventory_shape() -> None:
    inv = _load("HOKOM_EVIDENCE_PRODUCTION_INVENTORY.json")
    assert inv["target_taaqol_sha"] == TARGET_SHA
    assert inv["totals"]["EVIDENCE_REQUIREMENT_UNREVIEWED"] == 0
    assert inv["totals"]["READY_EVIDENCE_PRODUCER_UNWIRED"] == 0
    for p in inv["producers"]:
        assert p["evidence_id"], "producer missing id"
        assert p["current_status"] in {
            "RUNTIME_EXECUTED", "READY_TO_WIRE", "READY_TO_IMPLEMENT_MECHANICALLY",
            "MISSING_SOURCE_EVIDENCE", "MISSING_TYPED_CARRIER", "MISSING_PRODUCER",
            "AMBIGUOUS_SOURCE", "NOT_APPLICABLE", "CARRIER_ONLY", "LAW_ONLY",
            "OWNER_SEMANTIC_DECISION_REQUIRED", "NOT_IMPLEMENTED_IN_TARGET",
        }


# ── Lexical evidence closure ─────────────────────────────────────────────


def test_lexical_closure_129_accounted() -> None:
    lex = _load("HOKOM_LEXICAL_EVIDENCE_CLOSURE.json")
    assert lex["totals"]["AYAT_TOTAL"] == 129
    assert lex["totals"]["AYAT_ACCOUNTED"] == 129
    assert lex["totals"]["AYAT_UNCLASSIFIED"] == 0
    assert lex["totals"]["UNRESOLVED_WITHOUT_REASON"] == 0
    assert lex["totals"]["LEXICAL_RUNTIME_DEFECTS"] == 0


def test_lexical_closure_no_invented_roots_for_harf() -> None:
    lex = _load("HOKOM_LEXICAL_EVIDENCE_CLOSURE.json")
    for row in lex["rows"]:
        if row["word_class"] == "HARF":
            assert row["root"] is None, f"{row['token_id']} HARF has invented root {row['root']}"


# ── Clause evidence ──────────────────────────────────────────────────────


def test_clause_evidence_shape() -> None:
    clauses = _load("AYAT_CLAUSE_EVIDENCE.json")
    assert clauses["totals"]["CLAUSE_WITHOUT_BOUNDARY_EVIDENCE"] == 0
    assert clauses["totals"]["CLAUSE_WITHOUT_PROVENANCE"] == 0
    assert clauses["totals"]["CLAUSE_WITHOUT_TRACE"] == 0
    assert clauses["totals"]["CLAUSE_DIRECTLY_FROM_TOKEN_MEANING"] == 0
    assert clauses["totals"]["DETERMINISTIC_ACROSS_RUNS"] is True
    for c in clauses["clauses"]:
        assert c["boundary_evidence_ids"], f"{c['clause_id']} has no evidence"
        assert c["provenance_ids"], f"{c['clause_id']} has no provenance"
        assert c["trace_ids"], f"{c['clause_id']} has no trace"


def test_clause_segmenter_uses_closed_class_only() -> None:
    """The segmenter must not read gold; boundaries must be from operator surfaces."""
    clauses = _load("AYAT_CLAUSE_EVIDENCE.json")
    for c in clauses["clauses"]:
        for eid in c["boundary_evidence_ids"]:
            assert eid.startswith("operator_surface:"), \
                f"{c['clause_id']} carries non-operator evidence: {eid}"


# ── Span / relation / maqam ──────────────────────────────────────────────


def test_ayat_spans_source_derived_only() -> None:
    spans = _load("AYAT_SOURCE_DERIVED_SPANS.json")
    assert spans["totals"]["ARBITRARY_ADJACENCY_SPAN_COUNT"] == 0
    assert spans["totals"]["SPAN_WITHOUT_PROVENANCE"] == 0
    assert spans["totals"]["SPAN_WITHOUT_TRACE"] == 0
    assert spans["totals"]["SPAN_WITH_UNKNOWN_BOUNDARIES"] == 0


def test_ayat_manifest_scope_counts() -> None:
    m = _load("AYAT_EVIDENCE_PRODUCTION_MANIFEST.json")
    t = m["totals"]
    assert t["TOKEN_SCOPE_COUNT"] == 129
    assert t["DUPLICATE_SCOPE_IDS"] == 0
    assert t["UNRESOLVED_SCOPE_REFERENCES"] == 0
    assert t["EVIDENCE_WITHOUT_SOURCE"] == 0
    assert t["PROVENANCE_WITHOUT_SOURCE"] == 0
    # No RELATION or MAQAM evidence without a producer
    assert t["RELATION_EVIDENCE_COUNT"] == 0
    assert t["MAQAM_EVIDENCE_COUNT"] == 0


# ── LCX-150 ──────────────────────────────────────────────────────────────


def test_lcx_150_evidence_production() -> None:
    lcx = _load("LCX_150_EVIDENCE_PRODUCTION.json")
    assert lcx["totals"]["LCX_TOTAL"] == 150
    assert lcx["totals"]["LCX_UNCLASSIFIED"] == 0
    assert lcx["totals"]["LCX_RUNTIME_DEFECTS"] == 0
    assert lcx["totals"]["LCX_READY_PROJECTOR_FAILURES"] == 0
    assert len(lcx["rows"]) == 150


# ── Vertical anti-leap ───────────────────────────────────────────────────


def test_no_token_direct_leap_to_relation() -> None:
    """Ayat manifest must not carry RELATION-scope entries constructed from TOKEN scope."""
    m = _load("AYAT_EVIDENCE_PRODUCTION_MANIFEST.json")
    for e in m["entries"]:
        if e["scope_type"] == "RELATION":
            # Would require SPAN predecessor; SPAN=0, so no RELATION should exist
            assert False, f"RELATION scope entry present without SPAN predecessor: {e}"


def test_no_gold_relation_leakage() -> None:
    """The Ayat gold relations file must not be referenced as a producer or evidence source."""
    inv = _load("HOKOM_EVIDENCE_PRODUCTION_INVENTORY.json")
    for p in inv["producers"]:
        for k in ("producer_module", "source_files", "source_contract"):
            v = p.get(k, "")
            if isinstance(v, list):
                for item in v:
                    assert "ayat_al_dayn_relations" not in item.lower(), \
                        f"{p['evidence_id']} references gold file: {item}"
            elif isinstance(v, str):
                assert "ayat_al_dayn_relations" not in v.lower(), \
                    f"{p['evidence_id']} references gold file: {v}"


def test_no_synthetic_provenance_in_clauses() -> None:
    clauses = _load("AYAT_CLAUSE_EVIDENCE.json")
    for c in clauses["clauses"]:
        for pid in c["provenance_ids"]:
            assert "SYNTHETIC" not in pid.upper()
            assert "FAKE" not in pid.upper()
            assert "GOLD" not in pid.upper()


# ── Clause segmenter determinism (positive re-run) ────────────────────────


def test_clause_segmenter_deterministic():
    """Import and rerun; must produce same boundary token indices."""
    import sys
    sys.path.insert(0, str(REPO))
    from pipeline.clause_graph.segmenter import detect_boundaries
    import csv
    tokens = []
    with open(REPO / "reports/taaqol_full_integration/c9_runtime_output/ayat_al_dayn_results.csv") as f:
        for row in csv.DictReader(f):
            tokens.append({"surface": row["original_surface"], "word_class": row["word_class"]})
    b1 = detect_boundaries(tokens)
    b2 = detect_boundaries(tokens)
    assert len(b1) == len(b2)
    for x, y in zip(b1, b2):
        assert x.token_index == y.token_index
        assert x.boundary_type == y.boundary_type
        assert x.operator_surface == y.operator_surface


# ── Provenance/trace continuity ──────────────────────────────────────────


def test_all_c11_artifacts_carry_target_sha() -> None:
    for name in [
        "HOKOM_EVIDENCE_PRODUCTION_INVENTORY.json",
        "HOKOM_LEXICAL_EVIDENCE_CLOSURE.json",
        "AYAT_CLAUSE_EVIDENCE.json",
        "AYAT_SOURCE_DERIVED_SPANS.json",
        "AYAT_EVIDENCE_PRODUCTION_MANIFEST.json",
        "LCX_150_EVIDENCE_PRODUCTION.json",
    ]:
        doc = _load(name)
        assert doc["target_taaqol_sha"] == TARGET_SHA, f"{name} SHA mismatch"


def test_requirement_docs_carry_c11_reconciliation() -> None:
    for fname in [
        "01_VENDOR_CURRENT_MAIN_DELTA_MANIFEST.json",
        "08_FORMAL_SHAPE_REQUIREMENTS.json",
        "09_RELATION_MULTI_TOKEN_SCOPE_REQUIREMENTS.json",
        "10_MAQAM_CONTEXT_REQUIREMENTS.json",
        "15_IMPLEMENTATION_DEPENDENCY_GRAPH.json",
    ]:
        p = REPO / "requirements" / "ayat_al_dayn_integration" / fname
        doc = json.loads(p.read_text())
        assert doc.get("c11_reconciled_at_utc"), f"{fname} missing c11_reconciled_at_utc"
        assert doc.get("c11_evidence_artifacts"), f"{fname} missing c11_evidence_artifacts"
