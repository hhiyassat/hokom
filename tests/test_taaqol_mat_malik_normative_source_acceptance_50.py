#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50 (owner-canonical) — guard test.

Owner-supplied + ratified source NS1 accepted and bound to FNM1 (reuses round-49 decide()). Accept/bind is
not application: SOURCE_APPLIED=NO, binding is source-license only, no tanzīl/hukm/answer, no
permitted/not-permitted, no adjudication, no judicial outcome; FINAL_MANAT unchanged; agent did not
select/search/judge the source. Round-44 topology; no neutral comparison.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50.json"
MD = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_GUARDS_50.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_MANAGER_REPORT_AR_50.html"
FNM_ID = "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
NS_ID = "NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE"


def test_all_files_exist():
    for p in (J, MD, GUARDS, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_source_accepted_bound_not_applied():
    d = json.loads(J.read_text(encoding="utf-8"))
    rec = d["normative_source_record"]
    assert rec["source_id"] == NS_ID
    assert rec["authority"] == "RULE_OWNER_DR_HUSSEIN"
    assert rec["source_type"] == "OWNER_RATIFIED_NORMATIVE_RULE"
    assert rec["owner_ratification"] == "YES"
    assert rec["normative_source_accepted"] == "YES"
    assert rec["verdict"] == "ACCEPT_NORMATIVE_SOURCE_FOR_FNM1"
    assert rec["bound_to_FNM1"] == "YES"
    assert rec["source_applied"] == "NO"
    assert rec["binding_is_source_license_only"] == "YES"
    assert rec["agent_judged_source_correctness"] == "NO"
    for k in ("says_permitted_or_not", "adjudicates_right", "produces_judicial_outcome"):
        assert rec[k] == "NO", k
    assert "لا يُخرج ساكنٌ" in rec["source_text_or_reference"]
    assert rec["scope"] and rec["binding_license_to_FNM1"]


def test_recheck():
    d = json.loads(J.read_text(encoding="utf-8"))
    rc = d["recheck"]
    assert rc["NORMATIVE_SOURCE_ACCEPTED"] == "YES"
    assert rc["NORMATIVE_SOURCE_STATUS"] == "ACCEPTED"
    assert rc["NORMATIVE_SOURCE_ID"] == NS_ID
    assert rc["BOUND_TO_FNM1"] == "YES"
    assert rc["SOURCE_APPLIED"] == "NO"
    assert rc["FINAL_MANAT"] == "YES"
    assert rc["FINAL_MANAT_ID"] == FNM_ID
    for k in ("TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert rc[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("FINAL_MANAT_REQUIRED", "FINAL_MANAT_ID_REQUIRED", "OWNER_SUPPLIED_SOURCE_PRESENT",
              "OWNER_RATIFICATION_REQUIRED_FOR_SOURCE", "NORMATIVE_SOURCE_ACCEPTED_FOR_FNM1_ONLY",
              "BINDING_LICENSE_TO_FNM1_PRESENT", "SOURCE_ACCEPTANCE_IS_NOT_TANZIL",
              "SOURCE_ACCEPTANCE_IS_NOT_FINAL_HUKM", "SOURCE_ACCEPTANCE_IS_NOT_FINAL_ANSWER",
              "NO_EXTERNAL_REFERENCE_USED", "NO_FRAMENET", "NO_AGENT_SELECTED_SOURCE",
              "NO_AGENT_SEARCHED_SOURCE"):
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
    assert "ROUND50_TESTS = passed" in t
    assert FNM_ID in t and NS_ID in t
    assert "لا يُخرج ساكنٌ" in t
    assert "رخصة الربط بـ FNM1" in t


def test_report_no_neutral_no_ruling():
    t = REPORT.read_text(encoding="utf-8")
    assert "neutral_sentence_report" not in t
    assert "التقرير المحايد" not in t
    assert "http://" not in t and "https://" not in t
    for stmt in ("NORMATIVE_SOURCE_ACCEPTED = YES", "BOUND_TO_FNM1 = YES", "SOURCE_APPLIED = NO",
                 "TANZIL = NO", "FINAL_HUKM = NO", "FINAL_ANSWER = NO"):
        assert stmt in t, stmt
    for banned in ("يجوز الطرد", "لا يجوز الطرد", "الحكم النهائي هو"):
        assert banned not in t, banned
