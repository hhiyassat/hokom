#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47 — guard test.

Owner supplies + ratifies the 9 real-case facts (independent source, not text, not round-44 scenario). All 9
ACCEPT via the reused round-46 decide(); the real-world full-manāṭ gate passes and READY=YES, while
FINAL_MANAT/TANZIL/FINAL_HUKM/FINAL_ANSWER remain NO. Report uses the Round-44 topology; no neutral
comparison. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47.json"
MD = OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_GUARDS_47.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_MANAGER_REPORT_AR_47.html"
NINE = {"MF1_NO_CHILD", "MF2_NO_OTHER_HEIRS", "MF3_HEIR_IDENTITY_AND_STATUS", "MF4_HOUSE_OWNERSHIP",
        "MF5_HOUSE_IS_ESTATE", "MF6_PRIOR_RESIDENCE_PERMISSION", "MF7_SISTER_YAD_STATUS",
        "MF8_EVIDENCE_OR_BAYYINA", "MF9_LITIGATION_OUTCOME"}
SOURCE = "OWNER_SUPPLIED_REAL_CASE_FACTS_ROUND_47"


def test_all_files_exist():
    for p in (J, MD, GUARDS, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_nine_facts_all_accepted_as_real_case():
    d = json.loads(J.read_text(encoding="utf-8"))
    facts = d["facts"]
    assert len(facts) == 9
    assert {f["fact_id"] for f in facts} == NINE
    for f in facts:
        assert f["SOURCE"] == SOURCE
        assert f["NOT_FROM_TEXT_INFERENCE"] == "YES"
        assert f["NOT_FROM_ROUND44_SCENARIO"] == "YES"
        assert f["owner_ratification"] == "YES"
        assert f["owner_value"] not in ("", "EMPTY")
        assert f["source_or_evidence"] not in ("", "EMPTY")
        assert f["fact_accepted"] == "YES"
        assert f["verdict"] == "ACCEPT_REAL_CASE_FACT"


def test_recheck_gate_pass_but_no_tanzil():
    d = json.loads(J.read_text(encoding="utf-8"))
    rc = d["recheck"]
    assert rc["NINE_FACTS_ACCEPTED_COUNT"] == 9
    assert rc["NINE_FACTS_DEFER_COUNT"] == 0
    assert rc["NINE_FACTS_BLOCK_COUNT"] == 0
    assert rc["REAL_WORLD_FULL_MANAT_GATE_PASS"] == "YES"
    assert rc["REAL_WORLD_FULL_MANAT_READY"] == "YES"
    assert rc["STOP_BEFORE_TANZIL"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER"):
        assert rc[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("NINE_FACTS_REVIEWED", "FACT_ACCEPTANCE_REQUIRES_OWNER_VALUE",
              "FACT_ACCEPTANCE_REQUIRES_EVIDENCE", "FACT_ACCEPTANCE_REQUIRES_OWNER_RATIFICATION",
              "OWNER_SUPPLIED_REAL_CASE_FACTS", "SCENARIO_FACT_IS_NOT_REAL_CASE_FACT",
              "REAL_CASE_FACTS_NOT_FROM_TEXT_INFERENCE", "REAL_CASE_FACTS_NOT_FROM_ROUND44_SCENARIO",
              "REAL_WORLD_FULL_MANAT_READY_DOES_NOT_OPEN_TANZIL", "NO_TANZIL_WITHOUT_SEPARATE_PERMISSION",
              "NO_FINAL_HUKM", "NO_FINAL_ANSWER", "NO_FRAMENET",
              "NO_EXTERNAL_REFERENCE_UNLESS_OWNER_SUPPLIED"):
        assert g[k] == "YES", k
    assert g["AGENT_KNOWLEDGE_CREATES_FACT"] == "NO"


def test_report_topology_matches_round44():
    t = REPORT.read_text(encoding="utf-8")
    numbered = re.findall(r"<h2>(\d+)\.\s", t)
    assert numbered == [str(i) for i in range(1, 15)], numbered
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "13. إثبات سلسلة التوليد" in t
    assert "14. الخلاصة التنفيذية" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND47_TESTS = passed" in t
    assert 'id="nazila-sentence"' in t
    for fid in NINE:
        assert fid in t, fid


def test_report_no_neutral_and_gate_statements():
    t = REPORT.read_text(encoding="utf-8")
    assert "neutral_sentence_report" not in t
    assert "التقرير المحايد" not in t
    assert "http://" not in t and "https://" not in t
    for stmt in ("REAL_WORLD_FULL_MANAT_GATE_PASS = YES", "REAL_WORLD_FULL_MANAT_READY = YES",
                 "FINAL_MANAT = NO", "TANZIL = NO", "FINAL_HUKM = NO", "FINAL_ANSWER = NO"):
        assert stmt in t, stmt


def test_mechanism_reused_from_round46():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert "ROUND_46" in d["mechanism_reused_from"]
    assert d["source"] == SOURCE
