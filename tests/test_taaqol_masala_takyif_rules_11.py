#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_MASALA_TAKYIF_RULES_CONSTITUTION_11 — guard test.

The MASALA_TAKYIF_LAYER is PROPOSED_NOT_CANONICAL; all takyīf rules are candidate-only, owner_ratified
= NO, produce MASALA_TAKYIF_CANDIDATE_ONLY, verdict DEFER. No domain classification, no normative
source, no ḥukm/manāṭ/tanzīl/final answer. DOMAIN_ROUTING_LAYER is not canonical; old typos absent.
Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
DOCS = ROOT / "docs"
SCHEMAS = ROOT / "schemas"
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
CONSTITUTION = DOCS / "HOKOM_TAAQOL_MASALA_TAKYIF_RULES_CONSTITUTION_11.md"
SCHEMA = SCHEMAS / "masala_takyif_rule_schema_11.json"
CANDS = OUT / "MASALA_TAKYIF_CANDIDATES_11.json"
GUARDS = OUT / "MASALA_TAKYIF_JUMP_GUARDS_11.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_MASALA_TAKYIF_RULES_11.md"
MATRIX = OUT / "MASALA_TAKYIF_RULES_11_MATRIX.csv"
REPORT = OUT / "MASALA_TAKYIF_MANAGER_REPORT_AR_11.html"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (CONSTITUTION, SCHEMA, CANDS, GUARDS, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_schema_valid_json():
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert s["status"] == "PROPOSED_NOT_CANONICAL"
    assert "rule" in s and "guards" in s


def test_all_candidates_owner_ratified_no_and_candidate_only():
    cands = json.loads(CANDS.read_text(encoding="utf-8"))
    assert len(cands) >= 4
    for c in cands:
        assert c["owner_ratified"] == "NO", c["rule_id"]
        assert c["produces"] == "MASALA_TAKYIF_CANDIDATE_ONLY", c["rule_id"]
        assert c["BIRTH_STATUS"] == "CANDIDATE_ONLY"
        assert c["DOMAIN_BORN"] == "NO"
        assert c["NORMATIVE_SOURCE_ALLOWED"] == "NO"
        assert c["verdict"].startswith("DEFER")
        for forb in ("DOMAIN_CLASSIFICATION", "NORMATIVE_SOURCE", "HUKM", "MANAT", "TANZIL", "FINAL_ANSWER"):
            assert forb in c["does_not_produce"], (c["rule_id"], forb)


def test_domain_not_born():
    assert _m()["DOMAIN_CLASSIFICATION_BORN"] == "NO"
    assert _m()["MIRATH_CANDIDATE_BORN"] == "NO"
    assert _m()["QADA_CANDIDATE_BORN"] == "NO"
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    assert g["DOMAIN_CLASSIFICATION_BORN"] == "NO"


def test_normative_source_not_born():
    assert _m()["NORMATIVE_SOURCE_BIRTH_STATUS"] == "NOT_OPENED"


def test_no_hukm_manat_tanzil_final():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k


def test_report_has_sentence_tokens_guards_owner_request():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "الحُرّاس ضد القفز" in t
    assert "طلب تصديق المالك" in t


def test_domain_routing_not_canonical():
    assert _m()["DOMAIN_ROUTING_LAYER_CANONICAL"] == "NO"


def test_masala_takyif_proposed_not_canonical():
    assert _m()["MASALA_TAKYIF_LAYER_STATUS"] == "PROPOSED_NOT_CANONICAL"
    assert _m()["OWNER_RATIFICATION_REQUIRED"] == "YES"
    assert "PROPOSED_NOT_CANONICAL" in CONSTITUTION.read_text(encoding="utf-8")


def test_old_typos_absent():
    blob = REPORT.read_text(encoding="utf-8") + MATRIX.read_text(encoding="utf-8") + CANDS.read_text(encoding="utf-8")
    for bad in TYPOS:
        assert bad not in blob, bad


def test_owner_request_asks_the_five_questions():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("RATIFY_LAYER", "ALLOW_FRAME_TO_TAKYIF", "ALLOW_DOMAIN_BIRTH_LATER",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE"):
        assert q in t, q


def test_prior_rounds_unchanged_and_no_commit():
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
