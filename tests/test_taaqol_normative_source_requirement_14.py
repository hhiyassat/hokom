#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_NORMATIVE_SOURCE_REQUIREMENT_AND_CANDIDATE_REQUEST_14 — guard test.

Records normative-source REQUIREMENTS per round-13 domain candidate — never selects, births, or
ratifies a source. No ḥukm/manāṭ/tanzīl/final answer. Manager report present and explicit. Artifacts
only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
DEC = OUT / "NORMATIVE_SOURCE_REQUIREMENT_OWNER_DECISION_14.json"
REQ = OUT / "NORMATIVE_SOURCE_REQUIREMENTS_BY_DOMAIN_CANDIDATE_14.json"
STRAT = OUT / "COMPOSITE_DOMAIN_SOURCE_STRATEGY_CANDIDATE_14.json"
GUARDS = OUT / "NORMATIVE_SOURCE_REQUIREMENT_GUARDS_14.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_15.md"
MATRIX = OUT / "NORMATIVE_SOURCE_REQUIREMENT_14_MATRIX.csv"
REPORT = OUT / "NORMATIVE_SOURCE_REQUIREMENT_MANAGER_REPORT_AR_14.html"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
FOUR = {"MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
        "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"}


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (DEC, REQ, STRAT, GUARDS, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (DEC, REQ, STRAT, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_request_layer_only():
    d = json.loads(DEC.read_text(encoding="utf-8"))
    assert d["NORMATIVE_SOURCE_REQUEST_LAYER_ALLOWED"] == "YES"
    assert d["NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW"] == "NO"
    assert d["NORMATIVE_SOURCE_BIRTH_ALLOWED_NOW"] == "NO"
    assert d["SOURCE_SELECTION_ALLOWED"] == "NO"
    assert d["SOURCE_BIRTH_ALLOWED"] == "NO"


def test_requirements_for_all_four_candidates():
    q = json.loads(REQ.read_text(encoding="utf-8"))
    assert len(q) == 4
    assert {x["domain_candidate_id"] for x in q} == FOUR
    for x in q:
        assert x["source_requirement_status"] == "REQUIREMENT_RECORDED_NOT_SOURCE", x["domain_candidate_id"]
        for fld in ("required_authority_type", "required_text_type", "required_scope",
                    "required_evidence_type", "required_link_license"):
            assert x[fld], (x["domain_candidate_id"], fld)
        assert x["normative_source_born"] == "NO"
        assert x["normative_source_ratified"] == "NO"
        assert x["normative_source_selected"] == "NO"
        assert x["verdict"] == "DEFER_SOURCE_BIRTH_REQUIREMENTS_RECORDED"


def test_no_source_born_selected_or_ratified():
    m = _m()
    assert m["NORMATIVE_SOURCE_BORN"] == "NO"
    assert m["NORMATIVE_SOURCE_SELECTED"] == "NO"
    assert m["NORMATIVE_SOURCE_RATIFIED"] == "NO"
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "NOT_OPENED"


def test_no_hukm_manat_tanzil_final():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("DOMAIN_CANDIDATE_IS_NOT_NORMATIVE_SOURCE", "SOURCE_REQUIREMENT_IS_NOT_SOURCE",
              "SOURCE_CANDIDATE_IS_NOT_RATIFIED_SOURCE", "NO_NORMATIVE_SOURCE_BIRTH",
              "NO_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_report_explicit_and_complete():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "قرار المالك في الجولة 14" in t
    # explicit statements: source not born, not selected
    assert "NORMATIVE_SOURCE_BORN = NO" in t
    assert "NORMATIVE_SOURCE_SELECTED = NO" in t
    # requirement tables + owner request 15
    for did in FOUR:
        assert did in t, did
    assert "طلب معلومات الجولة 15" in t


def test_owner_request_15_five_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("PRIMARY = PICK_ONE | KEEP_COMPOSITE", "ALLOW_NORMATIVE_SOURCE_BIRTH",
              "AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"):
        assert q in t, q


def test_no_typos_no_external_refs_no_commit():
    blob = REPORT.read_text(encoding="utf-8") + MATRIX.read_text(encoding="utf-8") + REQ.read_text(encoding="utf-8")
    for bad in TYPOS:
        assert bad not in blob, bad
    assert "DOMAIN_ROUTING_LAYER" not in REPORT.read_text(encoding="utf-8")
    m = _m()
    assert m["PRIOR_ROUND_VERDICTS_CHANGED"] == "NO"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["ASSERTED_NOT_MEASURED_COUNT"] == "0"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert not re.search(r"https?://|//cdn", REPORT.read_text(encoding="utf-8"))


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
