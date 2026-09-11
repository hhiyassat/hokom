#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOSE_NAZILA_FACT_TO_NORMATIVE_BIRTH_PATH_11 — closure guard test.

Verifies nodes 0..7: valid JSON, full measurement fields, the birth-law chain (no descendant born
while its parent/ancestor is not closed), GateDecision != ChildBirthStatus, every node MEASURED
(ProducerFile + existing EvidenceFile) so ASSERTED_NOT_MEASURED_COUNT == 0, and no final ruling.
Artifacts only; no score/gate/runtime change.
"""
import json
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
RM = GEN / "roadmap"
MATRIX = GEN / "TAAQOL_NAZILA_FACT_TO_NORMATIVE_BIRTH_CLOSURE_11_MATRIX.csv"
MANAGER = RM / "TAAQOL_NAZILA_FACT_TO_NORMATIVE_BIRTH_MANAGER_REPORT_AR_11.html"
NODE_FILES = [
    "NAZILA_MAQAM_CLASSIFICATION_11.json",
    "NAZILA_REFERENCE_POLICY_11.json",
    "NAZILA_FACTUAL_CLAIM_11.json",
    "NAZILA_NORMATIVE_SOURCE_11.json",
    "NAZILA_NORMATIVE_HUKM_BIRTH_11.json",
    "NAZILA_ILLAH_MANAT_BIRTH_11.json",
    "NAZILA_TANZIL_BIRTH_11.json",
    "NAZILA_ANSWER_AUDIT_BIRTH_11.json",
]
REQUIRED_FIELDS = ["NodeName", "ImplementationStatus", "BirthStatus", "GateEvaluation",
                   "GateDecision", "ChildBirthStatus", "ClosureStatus", "Cause", "Conditions",
                   "Preventers", "EvidenceFile", "ProducerFile", "Residuals", "Verdict"]


def _nodes():
    return {p: json.loads((GEN / p).read_text(encoding="utf-8")) for p in NODE_FILES}


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_eight_nodes_present_and_valid():
    n = _nodes()
    assert len(n) == 8
    for p, d in n.items():
        assert isinstance(d, dict), p


def test_every_node_has_required_fields():
    for p, d in _nodes().items():
        for f in REQUIRED_FIELDS:
            assert f in d and d[f] not in (None, ""), (p, f)


def test_every_node_measured_with_producer_and_evidence():
    for p, d in _nodes().items():
        assert d["ProducerFile"], p
        assert (GEN / d["EvidenceFile"]).exists(), (p, d["EvidenceFile"])
        assert d["measured"] == "MEASURED", p
    assert _matrix()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_gate_decision_not_equal_child_birth_status():
    for p, d in _nodes().items():
        assert d["GateDecision"] != d["ChildBirthStatus"], p


def test_maqam_and_reference_deferred():
    m = _matrix()
    assert m["MAQAM_6_OWNER_RATIFIED"] == "NO"
    assert m["MAQAM_CLASSIFICATION_GATE_DECISION"] == "DEFER"
    assert m["REFERENCE_POLICY_OWNER_RATIFIED"] == "NO"
    assert m["REFERENCE_POLICY_DECISION_REQUIRED"] == "YES"


def test_no_factual_claim_born_when_maqam_or_reference_defer():
    m = _matrix()
    assert m["FACTUAL_CLAIM_BIRTH_STATUS"] == "FORBIDDEN_PARENT_DEFERRED"


def test_no_normative_hukm_born_when_source_unborn():
    m = _matrix()
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "UNBORN"
    assert m["NORMATIVE_HUKM_CHILD_CANDIDATE"] == "UNBORN"


def test_no_manat_born_when_normative_hukm_unborn():
    assert _matrix()["MANAT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert _matrix()["ILLAH_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"


def test_no_tanzil_born_when_manat_unborn():
    assert _matrix()["TANZIL_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"


def test_no_final_answer_when_tanzil_or_answer_unborn():
    m = _matrix()
    assert m["ANSWER_AUDIT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["FINAL_ANSWER_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["FINAL_HUKM_ISSUED"] == "NO"
    assert m["FINAL_ANSWER_ALLOWED"] == "NO"


def test_no_asserted_not_measured_anywhere():
    for p, d in _nodes().items():
        assert "ASSERTED_NOT_MEASURED" not in json.dumps(d, ensure_ascii=False) or d["measured"] == "MEASURED", p
    assert _matrix()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_flags_no_change():
    m = _matrix()
    assert m["ILLUSTRATIVE_DEMO"] == "NO"
    assert m["LLM_FREE_TEXT_OUTPUT"] == "NO"
    assert m["REPORT_SOURCE"] == "CODE_AND_ARTIFACTS_ONLY"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_manager_no_external_refs():
    assert MANAGER.exists() and MANAGER.stat().st_size > 500
    assert not re.search(r"https?://|//cdn", MANAGER.read_text(encoding="utf-8"))


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
