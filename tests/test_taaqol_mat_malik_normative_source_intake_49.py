#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49 — guard test.

Opens a PENDING owner-supplied normative-source intake register bound to FNM1. No source supplied this round
=> DEFER. The three decision rules are proven directly. No source selection/search/application; no
tanzīl/hukm/answer. Round-44 topology; no neutral comparison. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49.json"
MD = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_GUARDS_49.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_MANAGER_REPORT_AR_49.html"
GEN = ROOT / "scripts" / "taaqol_maqam_foundation" / "mat_malik_normative_source_intake_49.py"
FNM_ID = "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
REQ = ("source_id", "source_type", "authority", "source_text_or_reference", "scope",
       "binding_license_to_FNM1", "owner_ratification", "normative_source_accepted",
       "cause", "conditions", "preventers", "verdict", "residuals")


def _mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("intake49", GEN)
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
    full = {"authority": "A", "source_text_or_reference": "T", "scope": "S",
            "binding_license_to_FNM1": "L", "owner_ratification": "YES"}
    assert decide(full) == ("YES", "ACCEPT_NORMATIVE_SOURCE_FOR_FNM1")
    assert decide({**full, "owner_ratification": "NO"}) == ("NO", "BLOCK_OWNER_REJECTED_NORMATIVE_SOURCE")
    assert decide({**full, "scope": "EMPTY"})[1] == "DEFER_NORMATIVE_SOURCE_INCOMPLETE_OR_NOT_SUPPLIED"
    assert decide({"owner_ratification": "PENDING_OWNER_DECISION"})[1] == \
        "DEFER_NORMATIVE_SOURCE_INCOMPLETE_OR_NOT_SUPPLIED"


def test_record_is_pending_defer_this_round():
    d = json.loads(J.read_text(encoding="utf-8"))
    rec = d["normative_source_record"]
    for k in REQ:
        assert k in rec, k
    assert rec["authority"] == "EMPTY"
    assert rec["source_text_or_reference"] == "EMPTY"
    assert rec["scope"] == "EMPTY"
    assert rec["binding_license_to_FNM1"] == "EMPTY"
    assert rec["owner_ratification"] == "PENDING_OWNER_DECISION"
    assert rec["normative_source_accepted"] == "NO"
    assert rec["verdict"] == "DEFER_NORMATIVE_SOURCE_INCOMPLETE_OR_NOT_SUPPLIED"
    assert "NO_OWNER_SUPPLIED_NORMATIVE_SOURCE_IN_THIS_ROUND" in rec["preventers"]


def test_final_manat_ref_and_recheck():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert d["final_manat_ref"]["FINAL_MANAT_ID"] == FNM_ID
    assert d["final_manat_ref"]["FINAL_MANAT"] == "YES"
    rc = d["recheck"]
    assert rc["NORMATIVE_SOURCE_ACCEPTED"] == "NO"
    assert rc["NORMATIVE_SOURCE_STATUS"] == "DEFER"
    for k in ("TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert rc[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("FINAL_MANAT_REQUIRED", "FINAL_MANAT_ID_REQUIRED", "AGENT_MAY_NOT_SELECT_NORMATIVE_SOURCE",
              "AGENT_MAY_NOT_SEARCH_NORMATIVE_SOURCE", "OWNER_SUPPLIED_SOURCE_REQUIRED",
              "OWNER_RATIFICATION_REQUIRED_FOR_SOURCE", "NORMATIVE_SOURCE_TEXT_REQUIRED_FOR_ACCEPT",
              "BINDING_LICENSE_TO_FNM1_REQUIRED_FOR_ACCEPT", "NO_TANZIL", "NO_FINAL_HUKM",
              "NO_FINAL_ANSWER", "NO_EXTERNAL_REFERENCE_WITHOUT_OWNER", "NO_FRAMENET"):
        assert g[k] == "YES", k


def test_report_topology_matches_round44():
    t = REPORT.read_text(encoding="utf-8")
    numbered = re.findall(r"<h2>(\d+)\.\s", t)
    assert numbered == [str(i) for i in range(1, 15)], numbered
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "13. إثبات سلسلة التوليد" in t
    assert "14. الخلاصة التنفيذية" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND49_TESTS = passed" in t
    assert FNM_ID in t


def test_report_no_neutral_and_statements():
    t = REPORT.read_text(encoding="utf-8")
    assert "neutral_sentence_report" not in t
    assert "التقرير المحايد" not in t
    assert "http://" not in t and "https://" not in t
    for stmt in ("NORMATIVE_SOURCE_ACCEPTED = NO", "NORMATIVE_SOURCE_STATUS = DEFER",
                 "TANZIL = NO", "FINAL_HUKM = NO", "FINAL_ANSWER = NO", "FINAL_MANAT = YES"):
        assert stmt in t, stmt


def test_accept_would_pass_if_owner_supplied():
    m = _mod()
    full = {"authority": "A", "source_text_or_reference": "نص", "scope": "هذه النازلة",
            "binding_license_to_FNM1": "YES", "owner_ratification": "YES"}
    accepted, verdict = m.decide(full)
    assert accepted == "YES" and verdict == "ACCEPT_NORMATIVE_SOURCE_FOR_FNM1"
