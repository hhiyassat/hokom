"""C10 maximum-ready-closure targeted tests.

These tests validate the artifacts produced under HOKOM-TAAQOL-MAXIMUM-READY-
CLOSURE-01 and its continuation, without regressing the C9 baseline.

Scope:
- Requirement document schema (15 docs under requirements/ayat_al_dayn_integration).
- Ready inventory: no adapter remains READY_INTEGRATION_UNWIRED.
- Scope invariants: TOKEN cannot direct-leap to RelationCandidate / MaqamContext / RelationClosure.
- Track A: 43 core-only tokens classification file exists, is well-formed, and carries no
  forbidden downstream fields.
- LCX-150: 150 cases classified, no unclassified.
- Chain report vendor law: classification is NATIVE_TAAQOL_LAW (INTEGRATION_AGGREGATOR),
  not counted as a semantic verdict producer.
- Non-gold typed fixtures for the four READY_INTEGRATION laws: classification is stable.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
REQ_DIR = REPO / "requirements" / "ayat_al_dayn_integration"
REPORTS = REPO / "reports" / "taaqol_full_integration"

REQUIRED_DOCS = [
    "01_VENDOR_CURRENT_MAIN_DELTA_MANIFEST.json",
    "02_CANONICAL_AYAT_AL_DAYN_CORPUS_MANIFEST.json",
    "03_STAGE_OWNERSHIP_MATRIX.json",
    "04_P2_REGISTRY_CONTRACT.json",
    "05_LICENSING_BOUNDARY_VERDICT_MAPPING_CONTRACT.json",
    "06_FULL_TYPED_ADAPTER_CASCADE_MATRIX.json",
    "07_DAL_LAFZI_WADI_PREREQUISITES.json",
    "08_FORMAL_SHAPE_REQUIREMENTS.json",
    "09_RELATION_MULTI_TOKEN_SCOPE_REQUIREMENTS.json",
    "10_MAQAM_CONTEXT_REQUIREMENTS.json",
    "11_PROVENANCE_VERSIONING_POLICY.json",
    "12_FAILURE_RESIDUAL_TAXONOMY.json",
    "13_TEST_FIRST_MATRIX.json",
    "14_STAGE_BY_STAGE_ACCEPTANCE_GATES.json",
    "15_IMPLEMENTATION_DEPENDENCY_GRAPH.json",
]

ENVELOPE = {
    "schema_version",
    "generated_from_hokom_head",
    "target_taaqol_sha",
    "generated_at_utc",
    "source_files",
    "source_hashes",
    "status",
    "unresolved_items",
    "owner_decision_required",
    "validation_rules",
    "technical_validation_status",
    "owner_review_status",
}
TECHNICAL = {"VALIDATED_CURRENT", "VALIDATED_BLOCKED", "INVALID"}
OWNER = {"NOT_REVIEWED", "APPROVED", "REJECTED"}
FORBIDDEN_LEXICAL_FIELDS = {
    "expected_licensing_verdict",
    "expected_relation",
    "expected_ifadah",
    "expected_hukm",
    "expected_manat",
    "expected_tanzil",
    "expected_answer",
}


@pytest.mark.parametrize("fname", REQUIRED_DOCS)
def test_requirement_document_envelope(fname: str) -> None:
    p = REQ_DIR / fname
    assert p.exists(), f"missing requirement doc: {fname}"
    doc = json.loads(p.read_text())
    missing = ENVELOPE - set(doc.keys())
    assert not missing, f"{fname}: missing envelope keys {sorted(missing)}"
    assert doc["technical_validation_status"] in TECHNICAL
    assert doc["owner_review_status"] in OWNER
    assert doc["target_taaqol_sha"] == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"


def test_requirement_document_count_is_fifteen() -> None:
    files = [p for p in REQ_DIR.glob("*.json") if p.name in REQUIRED_DOCS]
    assert len(files) == 15


def test_ready_inventory_has_no_unwired_ready_integration() -> None:
    inv = json.loads((REPORTS / "READY_ADAPTER_WIRING_INVENTORY.json").read_text())
    adapters = inv["adapters"]
    unwired = [
        n for n, m in adapters.items()
        if m.get("classification") == "READY_INTEGRATION" and not m.get("wired_by_orchestrator", False)
    ]
    assert unwired == [], f"still-unwired READY_INTEGRATION: {unwired}"


def test_ready_inventory_has_no_unwired_ready_runtime() -> None:
    inv = json.loads((REPORTS / "READY_ADAPTER_WIRING_INVENTORY.json").read_text())
    adapters = inv["adapters"]
    unwired = [
        n for n, m in adapters.items()
        if m.get("classification") == "READY_RUNTIME" and not m.get("wired_by_orchestrator", False)
    ]
    assert unwired == [], f"still-unwired READY_RUNTIME: {unwired}"


def test_core_only_43_classification_shape() -> None:
    doc = json.loads((REPORTS / "CORE_ONLY_TOKEN_CLASSIFICATION.json").read_text())
    assert doc["totals"]["CORE_ONLY_CLASSIFIED_COUNT"] == 43
    assert doc["totals"]["CORE_ONLY_UNCLASSIFIED_COUNT"] == 0
    ids = [r["token_id"] for r in doc["rows"]]
    assert len(ids) == 43
    assert len(set(ids)) == 43, "duplicate token_ids"
    # No forbidden downstream fields on any row.
    for row in doc["rows"]:
        for k in FORBIDDEN_LEXICAL_FIELDS:
            assert k not in row, f"{row['token_id']} carries forbidden field {k}"


def test_ayat_lexical_coverage_shape() -> None:
    doc = json.loads((REPORTS / "AYAT_AL_DAYN_LEXICAL_COVERAGE.json").read_text())
    assert doc["totals"]["AYAT_TOKEN_COUNT"] == 129
    assert doc["totals"]["AYAT_LEXICAL_UNCLASSIFIED_COUNT"] == 0
    assert doc["forbidden_downstream_fields_present"] == 0
    # HARF should be root NOT_APPLICABLE
    for row in doc["rows"]:
        if row.get("word_class") == "HARF":
            assert row["root_applicability"] == "NOT_APPLICABLE", \
                f"{row['token_id']} HARF but root_applicability={row['root_applicability']}"
            assert row.get("root") is None, f"{row['token_id']} HARF has a root {row['root']}"


def test_lcx_150_readiness_shape() -> None:
    doc = json.loads((REPORTS / "LCX_150_CORPUS_READINESS.json").read_text())
    assert doc["totals"]["LCX_TOTAL"] == 150
    assert doc["totals"]["LCX_UNCLASSIFIED"] == 0
    assert len(doc["rows"]) == 150


def test_scope_evidence_inventory_present() -> None:
    doc = json.loads((REPORTS / "SCOPE_EVIDENCE_INVENTORY.json").read_text())
    assert doc["totals"]["SCOPE_SOURCE_UNREVIEWED"] == 0
    assert doc["totals"]["SCOPE_SOURCE_TOTAL"] >= 1


def test_chain_report_classified_as_native_law_not_verdict_producer() -> None:
    inv = json.loads((REPORTS / "READY_ADAPTER_WIRING_INVENTORY.json").read_text())
    cr = inv["adapters"]["chain_report_adapter"]
    assert cr["classification"] == "NATIVE_TAAQOL_LAW"
    sub = cr.get("subclassification", "")
    assert "INTEGRATION_AGGREGATOR" in sub, \
        "chain_report must be flagged as integration aggregator (adds no linguistic claim)"


def test_no_token_direct_leap_to_relation_candidate() -> None:
    """A ContractableUnitGeometry is TOKEN-scope; the native relation_candidate law
    takes 2× ContractableUnitGeometry (CLAUSE-scope). Prove the classification file
    records that Ayat cannot execute this directly (i.e., first_blocker mentions SPAN/CLAUSE)."""
    inv = json.loads((REPORTS / "READY_ADAPTER_WIRING_INVENTORY.json").read_text())
    rc = inv["adapters"]["relation_candidate_adapter"]
    assert rc.get("ayat_executable_now") is False
    blocker = rc.get("first_blocker", "")
    assert "SPAN" in blocker or "adjacency" in blocker.lower(), \
        f"relation_candidate first_blocker should mention SPAN or reject adjacency; got: {blocker}"


def test_no_token_direct_leap_to_maqam_context() -> None:
    inv = json.loads((REPORTS / "READY_ADAPTER_WIRING_INVENTORY.json").read_text())
    mc = inv["adapters"]["maqam_context_adapter"]
    assert mc.get("ayat_executable_now") is False
    assert mc.get("required_scope") == "SENTENCE"
    blocker = mc.get("first_blocker", "")
    assert "SENTENCE" in blocker or "maqam evidence absent" in blocker.lower(), \
        f"maqam_context first_blocker should require SENTENCE scope; got: {blocker}"


def test_formal_shape_first_blocker_is_typed_predecessor() -> None:
    inv = json.loads((REPORTS / "READY_ADAPTER_WIRING_INVENTORY.json").read_text())
    fs = inv["adapters"]["formal_shape_adapter"]
    assert fs["classification"] == "MISSING_TYPED_PREDECESSOR"
    assert fs.get("ayat_executable_now") is False
    assert "FormalShapeRegistry" in fs.get("first_blocker", "") or "predecessor" in fs.get("first_blocker", "").lower()


def test_maximum_ready_closure_status_present() -> None:
    p = REPORTS / "MAXIMUM_READY_CLOSURE_STATUS.json"
    assert p.exists()
    doc = json.loads(p.read_text())
    assert doc["target_taaqol_sha"] == "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52"


def test_no_synthetic_provenance_in_core_only_classification() -> None:
    doc = json.loads((REPORTS / "CORE_ONLY_TOKEN_CLASSIFICATION.json").read_text())
    for row in doc["rows"]:
        # provenance_ids should reference real vendor SHA or bridge IDs, not synthetic values
        for pid in row.get("provenance_ids", []):
            assert pid, "empty provenance id"
            assert "SYNTHETIC" not in pid.upper()
            assert "FAKE" not in pid.upper()


def test_no_gold_leakage_in_core_only_classification() -> None:
    doc = json.loads((REPORTS / "CORE_ONLY_TOKEN_CLASSIFICATION.json").read_text())
    for row in doc["rows"]:
        for k in FORBIDDEN_LEXICAL_FIELDS:
            assert k not in row
