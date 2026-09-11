#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_OWNER_RATIFIED_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13 — guard test.

Owner ratified a multi-domain candidate classification (this nazila only, no forced primary). A
composite classification is born where every domain is a DOMAIN_CANDIDATE (not a closed final domain,
not a normative source). No normative source, no ḥukm/manāṭ/tanzīl/final answer. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
RATIF = OUT / "DOMAIN_CLASSIFICATION_OWNER_RATIFICATION_13.json"
COMP = OUT / "NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json"
GUARDS = OUT / "DOMAIN_CLASSIFICATION_GUARDS_13.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_14.md"
MATRIX = OUT / "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13_MATRIX.csv"
REPORT = OUT / "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_MANAGER_REPORT_AR_13.html"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (RATIF, COMP, GUARDS, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_ratification_multi_domain_this_nazila():
    r = json.loads(RATIF.read_text(encoding="utf-8"))
    assert r["DOMAIN_CLASSIFICATION_BIRTH_ALLOWED"] == "YES"
    assert r["DOMAIN_CLASSIFICATION_SCOPE"] == "THIS_NAZILA_ONLY"
    assert r["DOMAIN_CLASSIFICATION_MODE"] == "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION"
    assert r["PRIMARY_DOMAIN_CANDIDATE"] == "NOT_FORCED"
    assert r["NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW"] == "NO"
    assert r["FINAL_ANSWER_ALLOWED_NOW"] == "NO"


def test_composite_born_no_primary_no_final_single():
    c = json.loads(COMP.read_text(encoding="utf-8"))["composite"]
    assert c["mode"] == "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION"
    assert c["primary_domain_candidate"] == "NOT_FORCED"
    assert c["is_final_single_domain"] == "NO"
    assert c["normative_source_selected"] == "NO"
    assert c["verdict"] == "COMPOSITE_MULTI_DOMAIN_CANDIDATE_ONLY"
    assert _m()["DOMAIN_CLASSIFICATION_BORN"] == "YES"
    assert _m()["FINAL_SINGLE_DOMAIN_CLOSED"] == "NO"


def test_four_domain_candidates_not_closed_not_source():
    dc = json.loads(COMP.read_text(encoding="utf-8"))["domain_candidates"]
    assert len(dc) == 4
    ids = {d["domain_candidate_id"] for d in dc}
    assert {"MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
            "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"} <= ids
    for d in dc:
        assert d["birth_status"] == "DOMAIN_CANDIDATE_BORN", d["domain_candidate_id"]
        assert d["is_final_closed_domain"] == "NO", d["domain_candidate_id"]
        assert d["is_primary_forced"] == "NO", d["domain_candidate_id"]
        assert d["normative_source_allowed"] == "NO", d["domain_candidate_id"]
        assert d["verdict"] == "ACCEPT_AS_DOMAIN_CANDIDATE", d["domain_candidate_id"]
        assert "ACCEPT_AS_CLOSED_DOMAIN" not in d["verdict"]
        assert "NORMATIVE_SOURCE" not in d["verdict"]
        for f in ("cause", "conditions", "preventers", "evidence", "residuals", "from_takyif_candidate"):
            assert d[f], (d["domain_candidate_id"], f)


def test_no_normative_source_or_ruling():
    m = _m()
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "NOT_OPENED"
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("DOMAIN_CANDIDATE_IS_NOT_CLOSED_DOMAIN", "DOMAIN_CANDIDATE_IS_NOT_NORMATIVE_SOURCE",
              "NO_FORCED_PRIMARY_DOMAIN", "NO_NORMATIVE_SOURCE_SELECTION",
              "NO_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_report_sentence_tokens_owner_decision_composite():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "قرار المالك في الجولة 13" in t
    assert "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION" in t
    assert "MIRATH_RELATED_DOMAIN_CANDIDATE" in t and "QADA_RELATED_DOMAIN_CANDIDATE" in t


def test_owner_request_14_questions():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_NORMATIVE_SOURCE_REQUEST", "PRIMARY = PICK_ONE | KEEP_COMPOSITE",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE"):
        assert q in t, q


def test_no_typos_no_external_refs_no_commit():
    blob = REPORT.read_text(encoding="utf-8") + MATRIX.read_text(encoding="utf-8") + COMP.read_text(encoding="utf-8")
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
