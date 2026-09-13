#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48 — guard test.

Births FINAL_MANAT for the real-world case from the 5 accepted text facts + 9 owner-ratified real-case facts
(round 47 gate=YES). FINAL_MANAT=YES/ACCEPTED, but it is not a hukm/tanzīl/answer and opens none of them; no
new fact added; no round-44 scenario as direct source; no normative source applied. Round-44 topology; no
neutral comparison. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.json"
MD = OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.md"
GUARDS = OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_GUARDS_48.json"
REPORT = OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_MANAGER_REPORT_AR_48.html"
FIVE = {"FC1_KING_DIED", "FC2_HAS_SISTER", "FC3_SISTER_RESIDING_WITH_HIM",
        "FC4_HEIR_WANTED_EXPULSION", "FC5_LITIGATION_OCCURRED"}
NINE = {"MF1_NO_CHILD", "MF2_NO_OTHER_HEIRS", "MF3_HEIR_IDENTITY_AND_STATUS", "MF4_HOUSE_OWNERSHIP",
        "MF5_HOUSE_IS_ESTATE", "MF6_PRIOR_RESIDENCE_PERMISSION", "MF7_SISTER_YAD_STATUS",
        "MF8_EVIDENCE_OR_BAYYINA", "MF9_LITIGATION_OUTCOME"}
FNM_ID = "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"


def test_all_files_exist():
    for p in (J, MD, GUARDS, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_inputs_are_5_text_and_9_real():
    d = json.loads(J.read_text(encoding="utf-8"))
    assert {f["fact_id"] for f in d["text_facts"]} == FIVE
    assert {f["fact_id"] for f in d["real_case_facts"]} == NINE
    for f in d["text_facts"]:
        assert f["source"] == "NAZILA_TEXT" and f["fact_accepted"] == "YES"
    for f in d["real_case_facts"]:
        assert f["source"] == "OWNER_SUPPLIED_REAL_CASE_FACTS_ROUND_47" and f["fact_accepted"] == "YES"
    assert d["gate_input_from_round47"]["REAL_WORLD_FULL_MANAT_GATE_PASS"] == "YES"


def test_final_manat_born_but_not_hukm():
    d = json.loads(J.read_text(encoding="utf-8"))
    fm = d["final_manat"]
    assert fm["FINAL_MANAT_ID"] == FNM_ID
    assert fm["FINAL_MANAT_BORN"] == "YES"
    assert fm["FINAL_MANAT_STATUS"] == "ACCEPTED"
    assert fm["verdict"] == "ACCEPT_FINAL_MANAT_ONLY"
    assert fm["SOURCE"] == ["TEXT_FACTS_ACCEPTED", "OWNER_RATIFIED_REAL_CASE_FACTS_ROUND_47"]
    assert set(fm["included_text_facts"]) == FIVE
    assert set(fm["included_real_facts"]) == NINE
    for k in ("IS_HUKM", "IS_TANZIL", "IS_FINAL_ANSWER", "DECIDES_EXPULSION_PERMISSIBILITY",
              "ADJUDICATES_SISTER_OR_HEIR_RIGHT", "PRODUCES_JUDICIAL_OUTCOME"):
        assert fm[k] == "NO", k
    assert fm["preventers"] == ["NONE_FOR_FINAL_MANAT_BIRTH"]
    for r in ("TANZIL_NOT_OPENED", "FINAL_HUKM_NOT_OPENED", "FINAL_ANSWER_NOT_OPENED",
              "NORMATIVE_SOURCE_NOT_APPLIED_YET"):
        assert r in fm["residuals"], r
    assert "وفاة مالكٍ عن أختٍ" in fm["FINAL_MANAT"]


def test_recheck_downstream_all_closed():
    d = json.loads(J.read_text(encoding="utf-8"))
    rc = d["recheck"]
    assert rc["FINAL_MANAT"] == "YES"
    assert rc["FINAL_MANAT_STATUS"] == "ACCEPTED"
    for k in ("TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert rc[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("FINAL_MANAT_BIRTH_AUTHORIZED", "REAL_WORLD_FULL_MANAT_GATE_PASS_REQUIRED",
              "ROUND47_FACTS_REQUIRED", "NO_NEW_FACTS_ADDED", "FINAL_MANAT_IS_NOT_TANZIL",
              "FINAL_MANAT_IS_NOT_HUKM", "FINAL_MANAT_IS_NOT_FINAL_ANSWER", "NO_NORMATIVE_SOURCE_APPLIED",
              "NO_ROUND44_SCENARIO_AS_DIRECT_SOURCE", "NO_FRAMENET", "NO_EXTERNAL_REFERENCE_USED"):
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
    assert "ROUND48_TESTS = passed" in t
    assert 'id="nazila-sentence"' in t
    assert FNM_ID in t


def test_report_no_neutral_no_hukm_statements():
    t = REPORT.read_text(encoding="utf-8")
    assert "neutral_sentence_report" not in t
    assert "التقرير المحايد" not in t
    assert "http://" not in t and "https://" not in t
    for stmt in ("FINAL_MANAT = YES", "TANZIL = NO", "FINAL_HUKM = NO", "FINAL_ANSWER = NO",
                 "FULL_TAAQOL_PROJECT_CLOSED = NO"):
        assert stmt in t, stmt
    # must not assert a ruling / permissibility
    for banned in ("يجوز الطرد", "لا يجوز الطرد", "الحكم النهائي هو"):
        assert banned not in t, banned
