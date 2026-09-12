#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_FINAL_ANSWER_53 — guard test.

Produces FINAL_ANSWER only from round-52 FINAL_HUKM. All 7 preconditions met => FINAL_ANSWER=YES (ACCEPTED),
bounded to FNM1, built only on FHK1+FNM1+NS1+round52. Not a general fatwa/judicial order; no judicial
outcome; no new source/fact; no generalization; rounds 47-52 unchanged. Boolean separated from text; report
has exactly 14 <h2>. decide_answer reversible (missing precondition => DEFER). No neutral comparison.
"""
import importlib.util
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_FINAL_ANSWER_53.json"
MD = OUT / "TAAQOL_MAT_MALIK_FINAL_ANSWER_53.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_FINAL_ANSWER_GUARDS_53.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_FINAL_ANSWER_MANAGER_REPORT_AR_53.html"
R52 = OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52.json"
GEN = ROOT / "scripts" / "taaqol_maqam_foundation" / "mat_malik_final_answer_53.py"
FAN_ID = "FAN1_MAT_MALIK_NO_EXPULSION_EFFECT_BEFORE_ADJUDICATION_FNM1"
FHK_ID = "FHK1_MAT_MALIK_NO_EXPULSION_BEFORE_ADJUDICATION_UNDER_NS1"


def _mod():
    spec = importlib.util.spec_from_file_location("answer53", GEN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_all_files_exist():
    for p in (J, MD, GUARDS, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_preconditions_all_met_with_round52_labels():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert len(d["preconditions"]) == 7
    labels = {c["precondition"] for c in d["preconditions"]}
    for k in ("ROUND52_FINAL_ANSWER", "ROUND52_JUDICIAL_OUTCOME_PRODUCED"):
        assert k in labels, k
    for c in d["preconditions"]:
        assert c["met"] is True, c["precondition"]


def test_final_answer_boolean_separated_from_text():
    d = json.loads(J.read_text(encoding="utf-8"))
    fa = d["final_answer"]
    assert fa["FINAL_ANSWER_ID"] == FAN_ID
    assert fa["FINAL_ANSWER"] == "YES"
    assert "مجلس الحكم المختص" not in fa["FINAL_ANSWER"]
    assert "مجلس الحكم المختص" in fa["FINAL_ANSWER_TEXT"]
    assert fa["FINAL_ANSWER_STATUS"] == "ACCEPTED"
    assert fa["verdict"] == "ACCEPT_FINAL_ANSWER_ONLY"
    assert fa["SCOPE"] == "FNM1_ONLY"
    assert fa["answer_type"] == "BOUNDED_CASE_ANSWER"
    assert fa["preventers"] == ["NONE_FOR_FINAL_ANSWER"]


def test_built_only_on_fhk1_fnm1_ns1_round52():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert d["final_manat_id"] == "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
    assert d["normative_source_id"] == "NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE"
    assert d["final_hukm_id"] == FHK_ID
    assert d["hukm_source_round"] == "ROUND_52"
    assert set(d["final_answer"]["SOURCE"]) == {"FHK1_ROUND52", "FNM1", "NS1"}


def test_not_fatwa_not_judicial_no_generalization():
    d = json.loads(J.read_text(encoding="utf-8"))
    fa = d["final_answer"]
    for k in ("IS_GENERAL_FATWA", "IS_JUDICIAL_ORDER", "JUDICIAL_OUTCOME_PRODUCED", "DECIDES_OWNERSHIP",
              "DECIDES_ESTATE_DIVISION", "DECIDES_SISTER_FINAL_RIGHT", "GENERALIZES_BEYOND_FNM1"):
        assert fa[k] == "NO", k
    for r in ("SCOPE_LIMITED_TO_FNM1", "NO_GENERALIZATION", "NO_JUDICIAL_EXECUTION",
              "FULL_PROJECT_NOT_CLOSED"):
        assert r in fa["residuals"], r


def test_recheck_decision_complete():
    d = json.loads(J.read_text(encoding="utf-8"))
    rc = d["recheck"]
    assert rc["FINAL_ANSWER"] == "YES"
    assert rc["FINAL_ANSWER_STATUS"] == "ACCEPTED"
    assert rc["JUDICIAL_OUTCOME_PRODUCED"] == "NO"
    assert rc["FULL_TAAQOL_PROJECT_CLOSED"] == "NO"
    for k in ("cause", "conditions", "preventers", "verdict", "residuals"):
        assert rc["decision"].get(k), k


def test_decide_reversible_missing_precondition():
    m = _mod()
    good = {"recheck": {"FINAL_MANAT": "YES", "TANZIL": "YES", "FINAL_ANSWER": "NO",
                        "JUDICIAL_OUTCOME_PRODUCED": "NO"},
            "final_hukm": {"FINAL_HUKM": "YES", "FINAL_HUKM_STATUS": "ACCEPTED",
                           "FINAL_HUKM_ID": FHK_ID}}
    assert m.decide_answer(m.check_preconditions(good)) == ("YES", "ACCEPT_FINAL_ANSWER_ONLY")
    broken = json.loads(json.dumps(good))
    broken["final_hukm"]["FINAL_HUKM"] = "NO"
    assert m.decide_answer(m.check_preconditions(broken)) == ("NO", "DEFER_FINAL_ANSWER_PRECONDITION_MISSING")


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("FINAL_HUKM_ACCEPTED_REQUIRED", "FINAL_ANSWER_ONLY_AUTHORIZED",
              "FINAL_ANSWER_BOUND_TO_FNM1_NS1_FHK1", "FINAL_ANSWER_IS_NOT_GENERAL_FATWA",
              "FINAL_ANSWER_IS_NOT_JUDICIAL_ORDER", "NO_JUDICIAL_OUTCOME_PRODUCED", "NO_OWNERSHIP_DECISION",
              "NO_ESTATE_DIVISION_DECISION", "NO_SISTER_FINAL_RIGHT_DECISION",
              "NO_GENERALIZATION_BEYOND_FNM1", "NO_NEW_SOURCE_ADDED", "NO_NEW_FACT_ADDED",
              "NO_EXTERNAL_REFERENCE_USED", "NO_FRAMENET", "ROUNDS_47_52_UNCHANGED",
              "FINAL_ANSWER_BOOLEAN_SEPARATED_FROM_TEXT"):
        assert g[k] == "YES", k


def test_rounds_47_52_unchanged():
    # round 52 must still say FINAL_ANSWER was NOT opened there
    rc = json.loads(R52.read_text(encoding="utf-8"))["recheck"]
    assert rc["FINAL_HUKM"] == "YES"
    assert rc["FINAL_ANSWER"] == "NO"
    assert rc["JUDICIAL_OUTCOME_PRODUCED"] == "NO"


def test_report_topology_exactly_14_h2():
    t = REPORT.read_text(encoding="utf-8")
    numbered = re.findall(r"<h2>(\d+)\.\s", t)
    assert numbered == [str(i) for i in range(1, 15)], numbered
    assert t.count("<h2") == 14, t.count("<h2")
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "13. إثبات سلسلة التوليد" in t
    assert "14. الخلاصة التنفيذية" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND53_TESTS = passed" in t
    assert FAN_ID in t


def test_final_answer_text_in_section_1_and_section_8():
    t = REPORT.read_text(encoding="utf-8")
    snippet = "لا يُنتَج أثر إخراج الأخت الساكنة من العين قبل نظر النزاع في مجلس الحكم المختص"
    # appears at least twice (section 1 + section 8)
    assert t.count(snippet) >= 2, t.count(snippet)
    # at least one occurrence is inside section 1 (before the §8 heading)
    i8 = t.find("<h2>8.")
    i1 = t.find("<h2>1.")
    assert i1 != -1 and i8 != -1
    assert 0 <= t.find(snippet) < i8, "FINAL_ANSWER_TEXT not present in section 1"
    # and still present inside/after section 8
    assert t.find(snippet, i8) != -1, "FINAL_ANSWER_TEXT missing from section 8"


def test_report_no_neutral_no_fatwa_no_judicial():
    t = REPORT.read_text(encoding="utf-8")
    assert "neutral_sentence_report" not in t
    assert "التقرير المحايد" not in t
    assert "http://" not in t and "https://" not in t
    for stmt in ("FINAL_ANSWER = YES", "SCOPE = FNM1_ONLY", "JUDICIAL_OUTCOME_PRODUCED = NO",
                 "FULL_TAAQOL_PROJECT_CLOSED = NO"):
        assert stmt in t, stmt
    for banned in ("يجوز الطرد", "لا يجوز الطرد", "يحكم للأخت", "يحكم للوارث", "النتيجة القضائية",
                   "فتوى عامة لكل", "أمر قضائي تنفيذي"):
        assert banned not in t, banned
