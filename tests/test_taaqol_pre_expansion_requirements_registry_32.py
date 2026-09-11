#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32 — guard test.

Foundational round: converts the ten manāṭ-application questions into REQUIREMENTS (not facts, not
sources, not canonical rules). Every requirement defers if its registry/source/owner-decision is missing.
No final manāṭ/tanzīl/final hukm/final answer; READY_FOR_EXPANSION=NO. Manager report obeys the
AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REG = OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json"
MD = OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.md"
GUARDS = OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_GUARDS_32.json"
MATRIX = OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_32_MATRIX.csv"
REPORT = OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_MANAGER_REPORT_AR_32.html"
REQ_FIELDS = ["requirement_id", "original_question", "requirement_type", "why_needed",
              "required_database_or_registry", "required_source_type", "required_owner_decision",
              "cause", "conditions", "preventers", "default_verdict_if_missing", "residuals",
              "expansion_blocker"]
TYPES = {"FACT_REQUIREMENT", "SOURCE_REQUIREMENT", "DATABASE_REQUIREMENT",
         "OWNER_DECISION_REQUIREMENT", "GATE_REQUIREMENT"}
REGISTRIES = {"factual_claim_registry", "owner_supplied_fact_registry", "source_requirement_registry",
              "normative_source_registry", "domain_candidate_registry", "hukm_candidate_registry",
              "manat_candidate_registry", "tanzil_requirement_registry", "proof_burden_registry",
              "possession_yad_registry", "inheritance_condition_registry", "residual_registry",
              "owner_ratification_registry"}
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
    for p in (REG, MD, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (REG, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_ten_questions_converted_to_requirements_not_facts():
    r = json.loads(REG.read_text(encoding="utf-8"))
    assert r["questions_from_agent_knowledge_canonical"] == "NO"
    assert r["questions_converted_to_requirements"] == "YES"
    reqs = r["requirements"]
    assert len(reqs) == 10
    assert r["requirement_count"] == 10
    for x in reqs:
        for k in REQ_FIELDS:
            assert k in x and x[k] not in (None, "", []), (x.get("requirement_id"), k)
        assert x["requirement_type"] in TYPES
        # a requirement, never a fact/source/rule value
        assert x["default_verdict_if_missing"] == "DEFER"
        assert x["expansion_blocker"] == "YES"


def test_each_requirement_has_cause_conditions_preventers():
    r = json.loads(REG.read_text(encoding="utf-8"))
    for x in r["requirements"]:
        for k in ("cause", "conditions", "preventers", "default_verdict_if_missing", "residuals"):
            assert x[k], (x["requirement_id"], k)


def test_all_five_requirement_kinds_present():
    r = json.loads(REG.read_text(encoding="utf-8"))
    kinds = {x["requirement_type"] for x in r["requirements"]}
    for needed in ("FACT_REQUIREMENT", "DATABASE_REQUIREMENT", "GATE_REQUIREMENT"):
        assert needed in kinds, needed
    m = _m()
    assert m["DATABASE_REQUIREMENTS_PRODUCED"] == "YES"
    assert m["SOURCE_REQUIREMENTS_PRODUCED"] == "YES"
    assert m["OWNER_DECISION_REQUIREMENTS_PRODUCED"] == "YES"
    assert m["GATE_REQUIREMENTS_PRODUCED"] == "YES"


def test_registries_to_build_listed():
    r = json.loads(REG.read_text(encoding="utf-8"))
    plan = r["registries_to_build_before_expansion"]
    ids = {p["registry_id"] for p in plan}
    assert REGISTRIES <= ids
    for p in plan:
        assert p["status"] == "MUST_BE_BUILT_BEFORE_EXPANSION"
        assert p["creates_fact"] == "NO"
        assert p["creates_source"] == "NO"
        assert p["owner_ratification_required"] == "YES"


def test_missing_requirement_defers():
    # decision rule: any requirement lacking registry/source/owner-decision defaults to DEFER
    r = json.loads(REG.read_text(encoding="utf-8"))
    assert all(x["default_verdict_if_missing"] == "DEFER" for x in r["requirements"])
    assert _m()["ALL_REQUIREMENTS_DEFER_IF_MISSING"] == "YES"


def test_no_final_manat_tanzil_hukm_answer_and_not_ready():
    m = _m()
    assert m["FINAL_MANAT"] == "NO"
    assert m["TANZIL"] == "NO"
    assert m["FINAL_HUKM"] == "NO"
    assert m["FINAL_ANSWER"] == "NO"
    assert m["READY_FOR_EXPANSION"] == "NO"
    r = json.loads(REG.read_text(encoding="utf-8"))
    assert r["ready_for_expansion"] == "NO"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("AGENT_QUESTION_IS_NOT_CANONICAL_RULE", "QUESTION_DOES_NOT_CREATE_FACT",
              "REQUIREMENT_DOES_NOT_CREATE_FACT", "SOURCE_REQUIREMENT_DOES_NOT_CREATE_SOURCE",
              "OWNER_RATIFICATION_REQUIRED", "NO_FINAL_MANAT", "NO_TANZIL", "NO_FINAL_HUKM",
              "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k
    assert g["READY_FOR_EXPANSION"] == "NO"


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
    assert "ROUND_32_TESTS = passed" in t
    assert "AGENT_QUESTION_IS_NOT_CANONICAL_RULE = YES" in t
    for stmt in ("READY_FOR_EXPANSION = NO", "FINAL_MANAT = NO", "TANZIL = NO",
                 "FINAL_HUKM = NO", "FINAL_ANSWER = NO"):
        assert stmt in t, stmt
    for rid in ("REQ01_NO_CHILD", "REQ06_HAND_CREDIBLE", "REQ09_EVIDENCE", "REQ10_QARINA_STRENGTH"):
        assert rid in t, rid


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_no_typos_no_noncanonical_no_commit():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + REG.read_text(encoding="utf-8")
    for bad in TYPOS:
        assert bad not in blob, bad
    assert "DOMAIN_ROUTING_LAYER" not in t
    m = _m()
    assert m["PRIOR_ROUND_VERDICTS_CHANGED"] == "NO"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert not re.search(r"https?://|www\.|//cdn", t)


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
