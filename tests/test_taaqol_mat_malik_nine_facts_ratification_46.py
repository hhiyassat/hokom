#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46 — guard test.

Real-case ratification of the nine facts. The three decision rules are proven directly; with no owner-supplied
values this round, all nine DEFER, the real-world full-manāṭ gate stays NO, and no tanzīl/hukm/answer opens.
Report uses the Round-44 14-section topology; no neutral-report comparison. Artifacts only.
"""
import importlib.util
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46.json"
MD = OUT / "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_GUARDS_46.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_MANAGER_REPORT_AR_46.html"
GEN = ROOT / "scripts" / "taaqol_maqam_foundation" / "mat_malik_nine_facts_ratification_46.py"
NINE = {"MF1_NO_CHILD", "MF2_NO_OTHER_HEIRS", "MF3_HEIR_IDENTITY_AND_STATUS", "MF4_HOUSE_OWNERSHIP",
        "MF5_HOUSE_IS_ESTATE", "MF6_PRIOR_RESIDENCE_PERMISSION", "MF7_SISTER_YAD_STATUS",
        "MF8_EVIDENCE_OR_BAYYINA", "MF9_LITIGATION_OUTCOME"}


def _mod():
    spec = importlib.util.spec_from_file_location("ratif46", GEN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_all_files_exist():
    for p in (J, MD, GUARDS, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_decision_rules_directly():
    decide = _mod().decide
    # ACCEPT when value + evidence + ratification=YES
    assert decide("لا ولد", "إقرار ورثة موثّق", "YES") == ("YES", "ACCEPT_REAL_CASE_FACT")
    # BLOCK when owner explicitly rejects
    assert decide("لا ولد", "إقرار", "NO") == ("NO", "BLOCK_OWNER_REJECTED_FACT")
    # DEFER when anything missing
    assert decide("EMPTY", "EMPTY", "PENDING_OWNER_DECISION") == ("NO", "DEFER_FACT_NOT_YET_PROVEN")
    assert decide("لا ولد", "EMPTY", "YES") == ("NO", "DEFER_FACT_NOT_YET_PROVEN")
    assert decide("لا ولد", "دليل", "PENDING_OWNER_DECISION") == ("NO", "DEFER_FACT_NOT_YET_PROVEN")


def test_nine_facts_all_defer_this_round():
    d = json.loads(J.read_text(encoding="utf-8"))
    facts = d["facts"]
    assert len(facts) == 9
    assert {f["fact_id"] for f in facts} == NINE
    for f in facts:
        assert f["owner_value"] == "EMPTY"
        assert f["source_or_evidence"] == "EMPTY"
        assert f["owner_ratification"] == "PENDING_OWNER_DECISION"
        assert f["fact_accepted"] == "NO"
        assert f["verdict"] == "DEFER_FACT_NOT_YET_PROVEN"
        assert f["fact_label"]
        for k in ("cause", "conditions", "preventers", "residuals"):
            assert f[k]


def test_recheck_gate_blocked():
    d = json.loads(J.read_text(encoding="utf-8"))
    rc = d["recheck"]
    assert rc["NINE_FACTS_REVIEWED"] == 9
    assert rc["NINE_FACTS_ACCEPTED_COUNT"] == 0
    assert rc["NINE_FACTS_DEFER_COUNT"] == 9
    assert rc["NINE_FACTS_BLOCK_COUNT"] == 0
    assert rc["REAL_WORLD_FULL_MANAT_GATE_PASS"] == "NO"
    assert rc["REAL_WORLD_FULL_MANAT_READY"] == "NO"
    assert rc["STOP_BEFORE_TANZIL"] == "YES"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER"):
        assert rc[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("NINE_FACTS_REVIEWED", "FACT_ACCEPTANCE_REQUIRES_OWNER_VALUE",
              "FACT_ACCEPTANCE_REQUIRES_EVIDENCE", "FACT_ACCEPTANCE_REQUIRES_OWNER_RATIFICATION",
              "SCENARIO_FACT_IS_NOT_REAL_CASE_FACT", "REAL_CASE_FACT_REQUIRES_RATIFICATION",
              "NO_TANZIL_WITHOUT_SEPARATE_PERMISSION", "NO_FINAL_HUKM", "NO_FINAL_ANSWER",
              "NO_FRAMENET", "NO_EXTERNAL_REFERENCE_UNLESS_OWNER_SUPPLIED"):
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
    assert "ROUND46_TESTS = passed" in t
    assert 'id="nazila-sentence"' in t
    for fid in NINE:
        assert fid in t, fid


def test_report_no_neutral_comparison_and_no_livelinks():
    t = REPORT.read_text(encoding="utf-8")
    # No neutral-report comparison anywhere.
    assert "neutral_sentence_report" not in t
    assert "التقرير المحايد" not in t
    assert "STRUCTURAL_NEUTRAL_REPORT" not in t
    # No live links.
    assert "http://" not in t and "https://" not in t
    # Closure statements present.
    for stmt in ("REAL_WORLD_FULL_MANAT_GATE_PASS = NO", "FINAL_MANAT = NO", "TANZIL = NO",
                 "FINAL_HUKM = NO", "FINAL_ANSWER = NO"):
        assert stmt in t, stmt


def test_gate_would_pass_if_all_ratified(monkeypatch=None):
    # Prove the gate logic is real: if all nine are accepted, the gate passes (still no tanzil).
    m = _mod()
    facts = [{"fact_accepted": "YES", "verdict": "ACCEPT_REAL_CASE_FACT"} for _ in range(9)]
    rc = m.recheck(facts)
    assert rc["REAL_WORLD_FULL_MANAT_GATE_PASS"] == "YES"
    assert rc["REAL_WORLD_FULL_MANAT_READY"] == "YES"
    assert rc["STOP_BEFORE_TANZIL"] == "NO"
    assert rc["TANZIL"] == "NO" and rc["FINAL_HUKM"] == "NO" and rc["FINAL_ANSWER"] == "NO"
