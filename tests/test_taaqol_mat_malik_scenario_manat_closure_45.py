#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOSE_MAT_MALIK_SCENARIO_MANAT_PACKAGE_45 — guard test.

Verifies the closure package: the neutral report accepts no facts and stays structural; the Round-44 report
reuses 5 text facts + 9 owner-scenario facts (not text, not code opinion) and produces a FULL_SCENARIO_MANAT
only; no tanzīl/final hukm/final answer; Round-44 artifacts unmodified. AR_45 report has the 14-section
Round-44 topology. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_45.json"
MD = OUT / "TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_45.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_GUARDS_45.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_MANAGER_REPORT_AR_45.html"
R44_JSON = OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.json"
R44_HTML = OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_MANAGER_REPORT_AR_44.html"


def test_all_files_exist():
    for p in (J, MD, GUARDS, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_what_closed_and_not_closed():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert d["what_closed"]["MAT_MALIK_TEXT_BOUND_MANAT"] == "CLOSED"
    assert d["what_closed"]["MAT_MALIK_OWNER_SCENARIO_MANAT"] == "CLOSED_FOR_SCENARIO_ONLY"
    nc = d["what_not_closed"]
    assert nc["MAT_MALIK_REAL_WORLD_FULL_MANAT"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_REAL_CASE_CLOSURE"):
        assert nc[k] == "NO", k


def test_verification_A_neutral_all_pass():
    d = json.loads(J.read_text(encoding="utf-8"))
    va = {c["check"]: c["PASS"] for c in d["verification_A_neutral"]}
    for k in ("NEUTRAL_REFLECTS_SENTENCE_ONLY", "NEUTRAL_FACT_ACCEPTED_COUNT_ZERO",
              "NEUTRAL_ACCEPTS_NO_FACTS", "NEUTRAL_ADDS_NO_SCENARIO_FACTS",
              "NEUTRAL_NO_FULL_MANAT", "NEUTRAL_NO_HUKM_NO_ANSWER", "NEUTRAL_ROLE_STRUCTURAL_ONLY"):
        assert va.get(k) is True, k


def test_verification_B_round44_all_pass():
    d = json.loads(J.read_text(encoding="utf-8"))
    vb = {c["check"]: c["PASS"] for c in d["verification_B_round44"]}
    for k in ("R44_REUSES_5_TEXT_FACTS", "R44_ADDS_9_AS_OWNER_SCENARIO", "R44_SCENARIO_NOT_FROM_TEXT",
              "R44_MANAT_NOT_CODE_OPINION", "R44_PRODUCES_FULL_SCENARIO_MANAT_ONLY",
              "R44_NO_TANZIL_HUKM_ANSWER_NO_REAL_GATE"):
        assert vb.get(k) is True, k
    assert d["ALL_VERIFICATION_CHECKS_PASS"] is True


def test_fact_tables():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert len(d["text_facts"]) == 5
    assert len(d["scenario_facts"]) == 9
    for c in d["scenario_facts"]:
        assert c["NOT_ORIGINAL_TEXT_FACT"] == "YES"
    ag = d["attribution_guards"]
    assert ag["RENDERING_ATTRIBUTION"] == "OWNER_SUPPLIED_SCENARIO_RENDERING"
    assert ag["NOT_CODE_OPINION"] == "YES"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    assert g["TEXT_ONLY_FULL_MANAT"] == "NO"
    assert g["SCENARIO_FULL_MANAT"] == "YES"
    for k in ("SCENARIO_FULL_MANAT_IS_NOT_FINAL_MANAT", "OWNER_SUPPLIED_SCENARIO_FACTS_ARE_NOT_TEXT_FACTS",
              "CODE_DID_NOT_INFER_SCENARIO_FACTS", "CODE_DID_NOT_OPINE_ON_YAD",
              "CODE_DID_NOT_OPINE_ON_BAYYINA", "NEUTRAL_REPORT_ACCEPTS_NO_FACTS",
              "NO_FRAMENET_WORD_TO_FRAME", "NO_EXTERNAL_REFERENCE_USED",
              "NO_TANZIL", "NO_FINAL_HUKM", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k
    assert g["FULL_REAL_CASE_CLOSURE"] == "NO"
    assert g["ROUND44_ARTIFACTS_MODIFIED"] == "NO"


def test_report_topology_matches_round44():
    t = REPORT.read_text(encoding="utf-8")
    numbered = re.findall(r"<h2>(\d+)\.\s", t)
    assert numbered == [str(i) for i in range(1, 15)], numbered  # 14 sections ordered
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "13. إثبات سلسلة التوليد" in t
    assert "14. الخلاصة التنفيذية" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "RENDERER=TAAQOL_STYLE" in t
    assert 'id="nazila-sentence"' in t


def test_report_closure_statements_and_no_livelinks():
    t = REPORT.read_text(encoding="utf-8")
    for stmt in ("MAT_MALIK_TEXT_BOUND_MANAT = CLOSED",
                 "MAT_MALIK_OWNER_SCENARIO_MANAT = CLOSED_FOR_SCENARIO_ONLY",
                 "MAT_MALIK_REAL_WORLD_FULL_MANAT = NO", "FINAL_MANAT = NO", "TANZIL = NO",
                 "FINAL_HUKM = NO", "FINAL_ANSWER = NO", "FULL_REAL_CASE_CLOSURE = NO"):
        assert stmt in t, stmt
    assert "http://" not in t and "https://" not in t


def test_round44_artifacts_not_modified():
    # closure only READS round-44; its signature content must remain intact.
    assert R44_JSON.exists() and R44_HTML.exists()
    rj = json.loads(R44_JSON.read_text(encoding="utf-8"))
    assert rj["full_scenario_manat"]["FULL_SCENARIO_MANAT_ID"] == \
        "FSM1_SISTER_RESIDENCE_IN_ESTATE_WITH_PERMISSION_AND_EXPULSION_DISPUTE"
    assert rj["full_scenario_manat"]["RENDERING_ATTRIBUTION"] == "OWNER_SUPPLIED_SCENARIO_RENDERING"
