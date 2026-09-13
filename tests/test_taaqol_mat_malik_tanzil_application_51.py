#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51 — guard test.

Applies NS1 to FNM1: the 8 binding elements are checked against round-48 accepted facts. All present =>
SOURCE_APPLIED=YES, TANZIL=YES (ACCEPTED), ACCEPT_TANZIL_ONLY; no final hukm/answer; no judicial outcome; no
permissibility language. decide_tanzil reversible (missing element => DEFER). Round-44 topology; no neutral
comparison.
"""
import importlib.util
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51.json"
MD = OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_GUARDS_51.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_MANAGER_REPORT_AR_51.html"
GEN = ROOT / "scripts" / "taaqol_maqam_foundation" / "mat_malik_tanzil_application_51.py"
FNM_ID = "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
NS_ID = "NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE"


def _mod():
    spec = importlib.util.spec_from_file_location("tanzil51", GEN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_all_files_exist():
    for p in (J, MD, GUARDS, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_eight_binding_elements_all_present():
    d = json.loads(J.read_text(encoding="utf-8"))
    els = d["binding_elements"]
    assert len(els) == 8
    for e in els:
        assert e["required_fact_ids"]
        assert e["missing_fact_ids"] == []
        assert e["present"] == "YES", e["element_id"]


def test_tanzil_accepted_only():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert d["NS1_APPLIES_TO_FNM1"] == "YES"
    assert d["final_manat_id"] == FNM_ID
    assert d["normative_source_id"] == NS_ID
    tr = d["tanzil_result"]
    assert tr["SOURCE_APPLIED"] == "YES"
    assert tr["TANZIL"] == "YES"
    assert tr["TANZIL_STATUS"] == "ACCEPTED"
    assert tr["verdict"] == "ACCEPT_TANZIL_ONLY"
    assert tr["preventers"] == ["NONE_FOR_TANZIL_ONLY"]
    for r in ("FINAL_HUKM_NOT_OPENED", "FINAL_ANSWER_NOT_OPENED", "JUDICIAL_OUTCOME_NOT_PRODUCED"):
        assert r in tr["residuals"], r


def test_recheck_hukm_answer_closed():
    d = json.loads(J.read_text(encoding="utf-8"))
    rc = d["recheck"]
    assert rc["NS1_APPLIES_TO_FNM1"] == "YES"
    assert rc["SOURCE_APPLIED"] == "YES"
    assert rc["TANZIL"] == "YES"
    assert rc["TANZIL_STATUS"] == "ACCEPTED"
    for k in ("FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert rc[k] == "NO", k
    assert rc["JUDICIAL_OUTCOME_PRODUCED"] == "NO"


def test_decide_reversible():
    m = _mod()
    els_all = [{"present": "YES"} for _ in range(8)]
    out = m.decide_tanzil(els_all, True, True)
    assert out[:4] == ("YES", "YES", "ACCEPTED", "ACCEPT_TANZIL_ONLY")
    els_missing = [{"present": "YES"} for _ in range(7)] + [{"present": "NO"}]
    out2 = m.decide_tanzil(els_missing, True, True)
    assert out2[3] == "DEFER_TANZIL_MISSING_BINDING_ELEMENT"
    # preventer path
    out3 = m.decide_tanzil(els_all, True, True, preventers=["SOME_PREVENTER"])
    assert out3[3] == "BLOCK_TANZIL_PREVENTER_PRESENT"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("FINAL_MANAT_REQUIRED", "NORMATIVE_SOURCE_ACCEPTED_REQUIRED", "SOURCE_BOUND_TO_FNM1_REQUIRED",
              "TANZIL_ONLY_AUTHORIZED", "SOURCE_APPLICATION_IS_NOT_FINAL_HUKM",
              "SOURCE_APPLICATION_IS_NOT_FINAL_ANSWER", "NO_JUDICIAL_OUTCOME_PRODUCED",
              "NO_PERMISSIBILITY_LANGUAGE", "NO_EXTERNAL_REFERENCE_USED", "NO_FRAMENET"):
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
    assert "ROUND51_TESTS = passed" in t
    assert FNM_ID in t and NS_ID in t
    assert "جدول عناصر الربط" in t


def test_report_no_ruling_no_permissibility():
    t = REPORT.read_text(encoding="utf-8")
    assert "neutral_sentence_report" not in t
    assert "التقرير المحايد" not in t
    assert "http://" not in t and "https://" not in t
    for stmt in ("NS1_APPLIES_TO_FNM1 = YES", "SOURCE_APPLIED = YES", "TANZIL = YES",
                 "FINAL_HUKM = NO", "FINAL_ANSWER = NO"):
        assert stmt in t, stmt
    for banned in ("يجوز الطرد", "لا يجوز الطرد", "يحكم للأخت", "يحكم للوارث", "النتيجة القضائية"):
        assert banned not in t, banned
