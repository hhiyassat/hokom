#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52 — guard test.

Births FINAL_HUKM only from round-51 tanzīl. All 9 preconditions met => FINAL_HUKM=YES (ACCEPTED),
ACCEPT_FINAL_HUKM_ONLY, scoped to FNM1, built only on NS1+FNM1+TANZIL_ROUND51. FINAL_ANSWER=NO,
JUDICIAL_OUTCOME_PRODUCED=NO; not addressed to a questioner; no ownership/right/estate decision; no general
fatwa; no permissibility language. decide_hukm reversible (missing precondition => DEFER). Round-51 unchanged.
Round-44 topology; no neutral comparison.
"""
import importlib.util
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52.json"
MD = OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_GUARDS_52.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_MANAGER_REPORT_AR_52.html"
R51 = OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51.json"
GEN = ROOT / "scripts" / "taaqol_maqam_foundation" / "mat_malik_final_hukm_birth_52.py"
FHK_ID = "FHK1_MAT_MALIK_NO_EXPULSION_BEFORE_ADJUDICATION_UNDER_NS1"


def _mod():
    spec = importlib.util.spec_from_file_location("hukm52", GEN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_all_files_exist():
    for p in (J, MD, GUARDS, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_preconditions_all_met_with_round51_labels():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert len(d["preconditions"]) == 9
    labels = {c["precondition"] for c in d["preconditions"]}
    # the three round-51 status preconditions carry explicit ROUND51_ labels (no ambiguity with FINAL_HUKM=YES)
    for k in ("ROUND51_FINAL_HUKM", "ROUND51_FINAL_ANSWER", "ROUND51_JUDICIAL_OUTCOME_PRODUCED"):
        assert k in labels, k
    assert "FINAL_HUKM" not in labels  # not present as a bare precondition label
    for c in d["preconditions"]:
        assert c["met"] is True, c["precondition"]


def test_final_hukm_boolean_separated_from_text():
    d = json.loads(J.read_text(encoding="utf-8"))
    fh = d["final_hukm"]
    assert fh["FINAL_HUKM_ID"] == FHK_ID
    # boolean value separated from text
    assert fh["FINAL_HUKM"] == "YES"
    assert "مجلس الحكم المختص" not in fh["FINAL_HUKM"]
    assert "مجلس الحكم المختص" in fh["FINAL_HUKM_TEXT"]
    assert fh["FINAL_HUKM_STATUS"] == "ACCEPTED"
    assert fh["verdict"] == "ACCEPT_FINAL_HUKM_ONLY"
    assert fh["SOURCE"] == "NS1_APPLIED_TO_FNM1_BY_ROUND51"
    assert fh["SCOPE"] == "FNM1_ONLY"
    assert fh["hukm_type"] == "INTERNAL_NORMATIVE_RULING"
    assert fh["preventers"] == ["NONE_FOR_FINAL_HUKM_BIRTH"]
    for k in ("IS_FINAL_ANSWER", "ADDRESSES_QUESTIONER", "PRODUCES_JUDICIAL_ORDER", "DECIDES_OWNERSHIP",
              "DECIDES_SISTER_FINAL_RIGHT", "DECIDES_ESTATE_DIVISION", "GENERAL_FATWA_BEYOND_FNM1"):
        assert fh[k] == "NO", k
    for r in ("FINAL_ANSWER_NOT_OPENED", "JUDICIAL_OUTCOME_NOT_PRODUCED", "NO_EXECUTION_ORDER",
              "SCOPE_LIMITED_TO_FNM1"):
        assert r in fh["residuals"], r


def test_built_only_on_ns1_fnm1_tanzil51():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert d["final_manat_id"] == "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
    assert d["normative_source_id"] == "NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE"
    assert d["tanzil_source_round"] == "ROUND_51"
    assert d["final_hukm"]["SOURCE"] == "NS1_APPLIED_TO_FNM1_BY_ROUND51"


def test_recheck_decision_complete_and_closed():
    d = json.loads(J.read_text(encoding="utf-8"))
    rc = d["recheck"]
    assert rc["FINAL_HUKM"] == "YES"
    assert rc["FINAL_HUKM_STATUS"] == "ACCEPTED"
    assert rc["FINAL_ANSWER"] == "NO"
    assert rc["JUDICIAL_OUTCOME_PRODUCED"] == "NO"
    assert rc["FULL_TAAQOL_PROJECT_CLOSED"] == "NO"
    # decision now carries all five fields
    dec = rc["decision"]
    for k in ("cause", "conditions", "preventers", "verdict", "residuals"):
        assert dec.get(k), k


def test_decide_reversible_missing_precondition():
    m = _mod()
    # build a round-51-like recheck dict from PRECONDITIONS (label, r51_key, expected)
    good = {r51_key: expected for _label, r51_key, expected in m.PRECONDITIONS}
    full = m.check_preconditions(good)
    assert m.decide_hukm(full) == ("YES", "ACCEPT_FINAL_HUKM_ONLY")
    broken = dict(good)
    broken["TANZIL"] = "NO"
    chk = m.check_preconditions(broken)
    assert m.decide_hukm(chk) == ("NO", "DEFER_FINAL_HUKM_PRECONDITION_MISSING")


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("TANZIL_ACCEPTED_REQUIRED", "FINAL_HUKM_ONLY_AUTHORIZED", "FINAL_HUKM_IS_NOT_FINAL_ANSWER",
              "FINAL_HUKM_IS_NOT_JUDICIAL_OUTCOME", "NO_ANSWER_TO_QUESTIONER", "NO_PERMISSIBILITY_LANGUAGE",
              "NO_OWNERSHIP_DECISION", "NO_SISTER_FINAL_RIGHT_DECISION", "NO_ESTATE_DIVISION_DECISION",
              "NO_GENERAL_FATWA_BEYOND_FNM1", "NO_NEW_SOURCE_ADDED", "NO_EXTERNAL_REFERENCE_USED",
              "NO_FRAMENET", "ROUND51_UNCHANGED", "FINAL_HUKM_BOOLEAN_SEPARATED_FROM_TEXT"):
        assert g[k] == "YES", k


def test_round51_unchanged():
    rc = json.loads(R51.read_text(encoding="utf-8"))["recheck"]
    assert rc["TANZIL"] == "YES"
    assert rc["FINAL_HUKM"] == "NO"       # round 51 still did not open hukm
    assert rc["FINAL_ANSWER"] == "NO"


def test_report_topology_exactly_14_h2():
    t = REPORT.read_text(encoding="utf-8")
    numbered = re.findall(r"<h2>(\d+)\.\s", t)
    assert numbered == [str(i) for i in range(1, 15)], numbered
    # exactly 14 <h2> headings — the trace table is embedded in §12, not a 15th heading
    assert t.count("<h2") == 14, t.count("<h2")
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "13. إثبات سلسلة التوليد" in t
    assert "14. الخلاصة التنفيذية" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND52_TESTS = passed" in t
    assert FHK_ID in t


def test_report_no_answer_no_permissibility():
    t = REPORT.read_text(encoding="utf-8")
    assert "neutral_sentence_report" not in t
    assert "التقرير المحايد" not in t
    assert "http://" not in t and "https://" not in t
    for stmt in ("FINAL_HUKM = YES", "FINAL_ANSWER = NO", "JUDICIAL_OUTCOME_PRODUCED = NO",
                 "SCOPE = FNM1_ONLY"):
        assert stmt in t, stmt
    for banned in ("يجوز الطرد", "لا يجوز الطرد", "يحكم للأخت", "يحكم للوارث", "النتيجة القضائية",
                   "الجواب للسائل"):
        assert banned not in t, banned
