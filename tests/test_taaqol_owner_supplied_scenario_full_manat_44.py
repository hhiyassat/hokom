#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44 — guard test.

Full manāṭ for an OWNER-SUPPLIED SCENARIO only: 5 text facts + 9 scenario facts (NOT_ORIGINAL_TEXT_FACT=YES);
scenario PHASE0 passes but the original-text full gate stays NO; one FULL_SCENARIO_MANAT
(ACCEPTED_FOR_SCENARIO_ONLY, not final); CMR1..CMR4 SATISFIED_FOR_SCENARIO only. No scenario fact treated as a
text fact; no reality proven; no tanzīl/final hukm/final answer; no closure. Manager report obeys AR_09_FIXED.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
J = OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.json"
MD = OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.md"
SREG = OUT / "TAAQOL_SCENARIO_FACT_REGISTRY_44.json"
RECHECK = OUT / "TAAQOL_SCENARIO_MANAT_RECHECK_44.json"
GUARDS = OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_GUARDS_44.json"
MATRIX = OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44_MATRIX.csv"
REPORT = OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_MANAGER_REPORT_AR_44.html"
FIVE = {"FC1_KING_DIED", "FC2_HAS_SISTER", "FC3_SISTER_RESIDING_WITH_HIM",
        "FC4_HEIR_WANTED_EXPULSION", "FC5_LITIGATION_OCCURRED"}
NINE = {"MF1_NO_CHILD", "MF2_NO_OTHER_HEIRS", "MF3_HEIR_IDENTITY_AND_STATUS", "MF4_HOUSE_OWNERSHIP",
        "MF5_HOUSE_IS_ESTATE", "MF6_PRIOR_RESIDENCE_PERMISSION", "MF7_SISTER_YAD_STATUS",
        "MF8_EVIDENCE_OR_BAYYINA", "MF9_LITIGATION_OUTCOME"}
CMR_IDS = {"CMR1_INHERITANCE_MANAT_REQUIREMENT", "CMR2_PROPERTY_ESTATE_MANAT_REQUIREMENT",
           "CMR3_RESIDENCE_YAD_MANAT_REQUIREMENT", "CMR4_PROOF_DISPUTE_MANAT_REQUIREMENT"}
SCENARIO_ID = "SCN1_NO_CHILD_NO_OTHER_HEIRS_ESTATE_PERMISSION_NO_EXPULSION_EVIDENCE"
FSM_ID = "FSM1_SISTER_RESIDENCE_IN_ESTATE_WITH_PERMISSION_AND_EXPULSION_DISPUTE"
NUMBERED = ["1. ملخص للمدير", "2. الجملة محل التشغيل", "3. جدول الكلمات العشر", "4. الإفادة", "5. المقام",
            "6. سياسة المرجع", "7. الدعوى الواقعية ورخصة العبور", "8. المصدر المعياري", "9. موضع التوقف",
            "10. المعلومات الناقصة", "11. ما يلزم بعد الوصول", "12. الاختبارات",
            "13. إثبات سلسلة التوليد", "14. الخلاصة التنفيذية"]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (J, MD, SREG, RECHECK, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (J, SREG, RECHECK, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_text_facts_reused():
    d = json.loads(J.read_text(encoding="utf-8"))
    tf = d["text_facts"]
    assert {c["fact_id"] for c in tf} == FIVE
    for c in tf:
        assert c["source"] == "NAZILA_TEXT"
        assert c["FACT_ACCEPTED"] == "YES"


def test_scenario_facts_not_text_facts():
    d = json.loads(J.read_text(encoding="utf-8"))
    sf = d["scenario_facts"]
    assert len(sf) == 9
    assert {s["scenario_fact_id"] for s in sf} == NINE
    for s in sf:
        assert s["SOURCE"] == "OWNER_SUPPLIED_SCENARIO"
        assert s["SCENARIO_ID"] == SCENARIO_ID
        assert s["NOT_ORIGINAL_TEXT_FACT"] == "YES"
        assert s["FACT_ACCEPTED_FOR_SCENARIO"] == "YES"
        assert s["verdict"] == "ACCEPT_FOR_SCENARIO_MANAT_ONLY"
        assert s["cause"] == "OWNER_SUPPLIED_SCENARIO_VALUE"
        assert "NOT_USED_AS_ORIGINAL_TEXT_FACT" in s["conditions"]
        assert s["residuals"] == "DOES_NOT_PROVE_ACTUAL_REAL_WORLD_FACT_OUTSIDE_SCENARIO"
        assert s["owner_value"] not in ("", "EMPTY")


def test_scenario_registry():
    d = json.loads(SREG.read_text(encoding="utf-8"))
    assert d["SCENARIO_ID"] == SCENARIO_ID
    assert d["NOT_ORIGINAL_TEXT_FACT"] == "YES"
    assert d["SOURCE"] == "OWNER_SUPPLIED_SCENARIO"
    assert d["scenario_fact_count"] == 9
    assert {s["scenario_fact_id"] for s in d["scenario_facts"]} == NINE


def test_full_scenario_manat_not_final():
    d = json.loads(J.read_text(encoding="utf-8"))
    fsm = d["full_scenario_manat"]
    assert fsm["FULL_SCENARIO_MANAT_ID"] == FSM_ID
    assert fsm["MANAT_TYPE"] == "OWNER_SUPPLIED_SCENARIO_FULL_FACTUAL_MANAT"
    assert fsm["MANAT_STATUS"] == "ACCEPTED_FOR_SCENARIO_ONLY"
    assert fsm["SCENARIO_ID"] == SCENARIO_ID
    # attribution correction
    assert fsm["RENDERING_ATTRIBUTION"] == "OWNER_SUPPLIED_SCENARIO_RENDERING"
    assert fsm["NOT_CODE_OPINION"] == "YES"
    assert fsm["NOT_INFERRED_BY_ENGINE"] == "YES"
    assert fsm["NOT_TEXT_BOUND_FACT"] == "YES"
    assert fsm["IS_STRUCTURED_RECORD_ONLY"] == "YES"
    assert fsm["RENDERING_NOTE"]
    assert set(fsm["SUPPORTED_TEXT_FACTS"]) == FIVE
    assert set(fsm["SUPPORTED_SCENARIO_FACTS"]) == NINE
    assert fsm["FINAL_MANAT"] == "NO"
    assert fsm["LICENSES_TANZIL"] == "NO"
    assert fsm["verdict"] == "ACCEPT_FULL_SCENARIO_MANAT_ONLY"
    for r in ("NOT_FINAL_MANAT_FOR_ACTUAL_CASE", "DOES_NOT_LICENSE_TANZIL",
              "DOES_NOT_LICENSE_FINAL_HUKM", "DOES_NOT_LICENSE_FINAL_ANSWER"):
        assert r in fsm["residuals"], r
    assert "وفاة مالك" in fsm["FULL_SCENARIO_MANAT"]


def test_conditional_updates_scenario_only():
    d = json.loads(J.read_text(encoding="utf-8"))
    ups = d["conditional_manat_updates"]
    assert {r["requirement_id"] for r in ups} == CMR_IDS
    covered = set()
    for r in ups:
        assert r["STATUS"] == "SATISFIED_FOR_SCENARIO"
        assert r["NOT_SATISFIED_FOR_ACTUAL_TEXT_ONLY"] == "YES"
        covered |= set(r["needs"])
    assert covered == NINE


def test_recheck_gates():
    r = json.loads(RECHECK.read_text(encoding="utf-8"))
    assert r["TEXT_FACTS_ACCEPTED"] == 5
    assert r["SCENARIO_FACTS_ACCEPTED"] == 9
    assert r["TOTAL_FACTS_AVAILABLE_FOR_SCENARIO_MANAT"] == 14
    assert r["MISSING_FACTS_DEFER_FOR_SCENARIO"] == 0
    assert r["SCENARIO_FACTUAL_FACTS_COMPLETE"] == "YES"
    assert r["PHASE0_SCENARIO_GATE_PASS"] == "YES"
    assert r["PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS"] == "NO"
    assert r["OPEN_TANZIL"] == "NO"
    assert r["PRODUCE_HUKM"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert r[k] == "NO", k
    assert r["decision"]["verdict"] == "FULL_SCENARIO_MANAT_ACCEPTED_ORIGINAL_TEXT_GATE_STILL_NO"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("SCENARIO_FACT_IS_NOT_TEXT_FACT", "OWNER_SUPPLIED_SCENARIO_DOES_NOT_PROVE_REALITY",
              "FULL_SCENARIO_MANAT_IS_NOT_FINAL_MANAT", "FULL_SCENARIO_MANAT_DOES_NOT_LICENSE_TANZIL",
              "FULL_SCENARIO_MANAT_DOES_NOT_LICENSE_HUKM", "TEXT_BOUND_MANAT_REMAINS_VALID",
              "ORIGINAL_TEXT_FULL_GATE_PASS_REMAINS_NO", "NO_SCENARIO_FACT_INVENTED_BY_AGENT",
              "SCENARIO_RENDERING_IS_OWNER_SUPPLIED", "CODE_DID_NOT_INFER_SCENARIO_FACTS",
              "CODE_DID_NOT_OPINE_ON_BAYYINA", "CODE_DID_NOT_OPINE_ON_YAD",
              "SCENARIO_MANAT_IS_STRUCTURED_RECORD_ONLY", "NO_TANZIL_UNTIL_ATTRIBUTION_CORRECTED"):
        assert g[k] == "YES", k
    for k in ("FRAMENET_WORD_TO_FRAME_BINDING_USED", "EXTERNAL_REFERENCE_USED", "FINAL_MANAT",
              "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert g[k] == "NO", k


def test_matrix_flags():
    m = _m()
    assert m["TEXT_FACTS_ACCEPTED"] == "5"
    assert m["SCENARIO_FACTS_ACCEPTED"] == "9"
    assert m["SCENARIO_ID"] == SCENARIO_ID
    assert m["NOT_ORIGINAL_TEXT_FACT"] == "YES"
    assert m["MISSING_FACTS_DEFER_FOR_SCENARIO"] == "0"
    assert m["SCENARIO_FACTUAL_FACTS_COMPLETE"] == "YES"
    assert m["PHASE0_SCENARIO_GATE_PASS"] == "YES"
    assert m["PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS"] == "NO"
    assert m["FULL_SCENARIO_MANAT_CREATED"] == "YES"
    assert m["FULL_SCENARIO_MANAT_STATUS"] == "ACCEPTED_FOR_SCENARIO_ONLY"
    assert m["RENDERING_ATTRIBUTION"] == "OWNER_SUPPLIED_SCENARIO_RENDERING"
    assert m["ROUND44_ATTRIBUTION_CORRECTED"] == "YES"
    assert m["NOT_CODE_OPINION"] == "YES"
    assert m["NOT_INFERRED_BY_ENGINE"] == "YES"
    assert m["OWNER_SUPPLIED_SCENARIO_ONLY"] == "YES"
    assert m["SCENARIO_MANAT_IS_STRUCTURED_RECORD_ONLY"] == "YES"
    assert m["NO_TANZIL_UNTIL_ATTRIBUTION_CORRECTED"] == "YES"
    assert m["CONDITIONAL_MANAT_SATISFIED_FOR_SCENARIO"] == "4"
    assert m["SCENARIO_FACT_IS_NOT_TEXT_FACT"] == "YES"
    assert m["OWNER_SUPPLIED_SCENARIO_DOES_NOT_PROVE_REALITY"] == "YES"
    assert m["FRAMENET_WORD_TO_FRAME_BINDING_USED"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER",
              "FULL_TAAQOL_PROJECT_CLOSED", "AUTHORITY_LEAK"):
        assert m[k] == "NO", k


def test_report_sections_ordered_1_to_14():
    t = REPORT.read_text(encoding="utf-8")
    positions = []
    for s in NUMBERED:
        idx = t.find(s)
        assert idx != -1, s
        positions.append(idx)
    assert positions == sorted(positions), "sections not in order"


def test_report_ar09_experience_and_statements():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND_44_TESTS = passed" in t
    for fid in FIVE:
        assert fid in t, fid
    for mid in NINE:
        assert mid in t, mid
    for cid in CMR_IDS:
        assert cid in t, cid
    for stmt in ("TEXT_FACTS_ACCEPTED = 5", "SCENARIO_FACTS_ACCEPTED = 9",
                 "SCENARIO_FACTUAL_FACTS_COMPLETE = YES", "PHASE0_SCENARIO_GATE_PASS = YES",
                 "PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS = NO", "FULL_SCENARIO_MANAT_CREATED = YES",
                 "FULL_SCENARIO_MANAT_STATUS = ACCEPTED_FOR_SCENARIO_ONLY",
                 "RENDERING_ATTRIBUTION = OWNER_SUPPLIED_SCENARIO_RENDERING",
                 "ROUND44_ATTRIBUTION_CORRECTED = YES", "NOT_CODE_OPINION = YES",
                 "NOT_INFERRED_BY_ENGINE = YES", "OWNER_SUPPLIED_SCENARIO_ONLY = YES",
                 "SCENARIO_MANAT_IS_STRUCTURED_RECORD_ONLY = YES",
                 "NO_TANZIL_UNTIL_ATTRIBUTION_CORRECTED = YES",
                 "SCENARIO_FACT_IS_NOT_TEXT_FACT = YES", "FINAL_MANAT = NO", "TANZIL = NO",
                 "FINAL_HUKM = NO", "FINAL_ANSWER = NO", "FULL_TAAQOL_PROJECT_CLOSED = NO"):
        assert stmt in t, stmt
    # nothing should read as engine opinion/inference/ruling
    assert "استنتج الكود" not in t
    assert "رأي الكود" in t  # only ever as a negation ("ليست رأي الكود")


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_no_typos_no_noncanonical_no_livelinks():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + J.read_text(encoding="utf-8")
    for bad in TYPOS:
        assert bad not in blob, bad
    assert "DOMAIN_ROUTING_LAYER" not in t
    assert not re.search(r"https?://|www\.|//cdn", t)
    m = _m()
    assert m["PRIOR_ROUND_VERDICTS_CHANGED"] == "NO"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PUSH_EXECUTED"] == "NO"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert m["EXTERNAL_REFS"] == "0"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
