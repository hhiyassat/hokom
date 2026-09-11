#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_OWNER_FACT_RATIFICATION_AND_MISSING_FACT_SUPPLY_36 — guard test.

Owner ratification GATE only: 5 fact candidates presented (not auto-accepted), 9 missing-fact supply
template. No owner ratification values entered -> all DEFER, 0 accepted, factual facts incomplete, PHASE 0
still blocked. Agent knowledge/question/requirement create no fact. No final manāṭ/tanzīl/final hukm/final
answer; FULL_TAAQOL_PROJECT_CLOSED=NO; READY_FOR_EXPANSION=NO. Manager report obeys AR_09_FIXED.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REQ = OUT / "OWNER_FACT_RATIFICATION_REQUEST_36.md"
SCHEMA = OUT / "OWNER_FACT_RATIFICATION_SCHEMA_36.json"
DEC = OUT / "OWNER_FACT_RATIFICATION_DECISIONS_36.json"
TMPL = OUT / "MISSING_FACT_SUPPLY_TEMPLATE_36.md"
RECHECK = OUT / "PHASE0_RECHECK_AFTER_FACT_RATIFICATION_36.json"
GUARDS = OUT / "FACT_RATIFICATION_GUARDS_36.json"
MATRIX = OUT / "FACT_RATIFICATION_36_MATRIX.csv"
REPORT = OUT / "FACT_RATIFICATION_MANAGER_REPORT_AR_36.html"
FIVE = {"FC1_KING_DIED", "FC2_HAS_SISTER", "FC3_SISTER_RESIDING_WITH_HIM",
        "FC4_HEIR_WANTED_EXPULSION", "FC5_LITIGATION_OCCURRED"}
DEC_FIELDS = ["decision_id", "fact_id", "normalized_fact_statement", "OWNER_RATIFY", "FACT_ACCEPTED",
              "cause", "conditions", "preventers", "verdict", "residuals"]
SECTIONS = [
    "1. ملخص للمدير", "2. الجملة محل التشغيل", "3. جدول الكلمات العشر", "4. الإفادة", "5. المقام",
    "6. سياسة المرجع", "7. الدعوى الواقعية ورخصة العبور", "8. المصدر المعياري", "9. موضع التوقف",
    "10. المعلومات الناقصة / الطلب الأدق", "11. ما يلزم بعد الوصول", "12. الاختبارات",
    "13. إثبات سلسلة التوليد", "14. الخلاصة التنفيذية",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (REQ, SCHEMA, DEC, TMPL, RECHECK, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (SCHEMA, DEC, RECHECK, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_five_decisions_all_defer_none_accepted():
    d = json.loads(DEC.read_text(encoding="utf-8"))
    decs = d["decisions"]
    assert len(decs) == 5
    assert {x["fact_id"] for x in decs} == FIVE
    assert d["owner_ratified_fact_count"] == 0
    for x in decs:
        for k in DEC_FIELDS:
            assert k in x and x[k] not in (None, ""), (x.get("decision_id"), k)
        assert x["OWNER_RATIFY"] == "DEFER"
        assert x["FACT_ACCEPTED"] == "NO"
        assert x["verdict"] == "AWAITING_OWNER_RATIFICATION_DEFER"


def test_schema_rule():
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(s["OWNER_RATIFY_allowed_values"]) == {"YES", "NO", "DEFER"}
    assert s["FACT_ACCEPTED_rule"] == "YES only if OWNER_RATIFY==YES"
    assert s["default_if_absent"] == "DEFER"


def test_missing_supply_records_nine_defer():
    d = json.loads(DEC.read_text(encoding="utf-8"))
    ms = d["missing_fact_supply_records"]
    assert len(ms) == 9
    for m in ms:
        assert m["OWNER_RATIFY"] == "DEFER"
        assert m["FACT_ACCEPTED"] == "NO"
        assert m["OWNER_SUPPLIED_VALUE"] == ""
        assert m["verdict"] == "REQUIRED_FACT_MISSING_DEFER"


def test_phase0_recheck_still_blocked():
    r = json.loads(RECHECK.read_text(encoding="utf-8"))
    assert r["fact_candidates_reviewed"] == 5
    assert r["owner_ratified_fact_count"] == 0
    assert r["missing_fact_requirements_reviewed"] == 9
    assert r["missing_facts_supplied_count"] == 0
    assert r["factual_facts_complete"] == "NO"
    assert r["phase0_gate_pass"] == "NO"
    assert r["ready_for_expansion"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert r[k] == "NO", k
    assert r["decision"]["verdict"] == "STILL_BLOCKED_AT_PHASE_0_FACTS_NOT_RATIFIED"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    assert g["AGENT_KNOWLEDGE_CREATES_FACT"] == "NO"
    assert g["QUESTION_CREATES_FACT"] == "NO"
    assert g["REQUIREMENT_CREATES_FACT"] == "NO"
    for k in ("TEXT_FACT_CANDIDATE_IS_NOT_ACCEPTED_FACT",
              "OWNER_RATIFICATION_REQUIRED_FOR_FACT_ACCEPTANCE",
              "SKELETON_NOT_POPULATED_WITHOUT_OWNER"):
        assert g[k] == "YES", k
    assert g["MISSING_FACT_DEFAULT"] == "DEFER"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER",
              "FULL_TAAQOL_PROJECT_CLOSED", "READY_FOR_EXPANSION"):
        assert g[k] == "NO", k


def test_request_and_template_content():
    rq = REQ.read_text(encoding="utf-8")
    assert "OWNER_RATIFY = YES | NO | DEFER" in rq
    for fid in FIVE:
        assert fid in rq, fid
    tp = TMPL.read_text(encoding="utf-8")
    for token in ("OWNER_SUPPLIED_VALUE", "SOURCE_OR_EVIDENCE_REF", "MF1_NO_CHILD", "MF9_LITIGATION_OUTCOME"):
        assert token in tp, token


def test_matrix_flags():
    m = _m()
    assert m["FACT_CANDIDATES_REVIEWED"] == "5"
    assert m["OWNER_RATIFIED_FACT_COUNT"] == "0"
    assert m["MISSING_FACT_REQUIREMENTS_REVIEWED"] == "9"
    assert m["FACTUAL_FACTS_COMPLETE"] == "NO"
    assert m["PHASE0_RECHECK_DONE"] == "YES"
    assert m["PHASE0_GATE_PASS"] == "NO"
    assert m["READY_FOR_EXPANSION"] == "NO"
    assert m["AGENT_KNOWLEDGE_CREATES_FACT"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert m[k] == "NO", k
    assert m["AUTHORITY_LEAK"] == "NO"


def test_report_sections_ordered_1_to_14():
    t = REPORT.read_text(encoding="utf-8")
    positions = []
    for s in SECTIONS:
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
    assert "ROUND_36_TESTS = passed" in t
    for fid in FIVE:
        assert fid in t, fid
    for stmt in ("OWNER_RATIFIED_FACT_COUNT = 0", "PHASE0_GATE_PASS = NO", "READY_FOR_EXPANSION = NO",
                 "FINAL_MANAT = NO", "TANZIL = NO", "FINAL_HUKM = NO", "FINAL_ANSWER = NO",
                 "FULL_TAAQOL_PROJECT_CLOSED = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_no_typos_no_noncanonical():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + DEC.read_text(encoding="utf-8")
    for bad in TYPOS:
        assert bad not in blob, bad
    assert "DOMAIN_ROUTING_LAYER" not in t
    m = _m()
    assert m["PRIOR_ROUND_VERDICTS_CHANGED"] == "NO"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PUSH_EXECUTED"] == "NO"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert not re.search(r"https?://|www\.|//cdn", t)


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
