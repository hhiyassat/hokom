#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_AND_SKELETONS_34 — guard test.

Verifies: 40 normalized requirement rows (10 per dimension), full governance shape, all DEFER; exactly 13
registry skeletons all SKELETON_ONLY_NOT_POPULATED that create no fact/source/hukm/tanzil/answer; PHASE-0
recheck still BLOCKED (registries unpopulated, no owner facts); no final manāṭ/tanzīl/hukm/answer. Manager
report obeys the AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
NORM = OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.json"
NORM_MD = OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.md"
SKEL = OUT / "TAAQOL_REGISTRY_SKELETONS_13_34.json"
SKEL_MD = OUT / "TAAQOL_REGISTRY_SKELETONS_13_34.md"
RECHECK = OUT / "TAAQOL_PHASE0_RECHECK_AFTER_NORMALIZATION_34.json"
GUARDS = OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_GUARDS_34.json"
MATRIX = OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_34_MATRIX.csv"
REPORT = OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_MANAGER_REPORT_AR_34.html"
DIMENSIONS = {"FACT_REQUIREMENT", "SOURCE_REQUIREMENT", "OWNER_DECISION_REQUIREMENT", "GATE_REQUIREMENT"}
ROW_FIELDS = ["normalized_requirement_id", "parent_requirement_id", "parent_question", "dimension_type",
              "requirement_statement", "required_registry", "required_source_type",
              "required_owner_decision", "cause", "conditions", "preventers",
              "default_verdict_if_missing", "creates_fact", "creates_source", "creates_hukm",
              "creates_tanzil", "creates_final_answer", "expansion_blocker", "residuals"]
SKEL_FIELDS = ["registry_id", "registry_name", "purpose", "allowed_record_types",
               "minimum_required_fields", "owner_ratification_required", "creates_fact",
               "creates_source", "creates_hukm", "creates_tanzil", "creates_final_answer",
               "gate_dependencies", "cause", "conditions", "preventers", "default_verdict_if_empty",
               "expansion_blocker_if_empty", "status"]
THIRTEEN = {"factual_claim_registry", "owner_supplied_fact_registry", "source_requirement_registry",
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
    for p in (NORM, NORM_MD, SKEL, SKEL_MD, RECHECK, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (NORM, SKEL, RECHECK, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_forty_normalized_rows_ten_per_dimension():
    d = json.loads(NORM.read_text(encoding="utf-8"))
    rows = d["normalized_requirements"]
    assert len(rows) == 40
    assert d["normalized_requirement_row_count"] == 40
    for dim in DIMENSIONS:
        assert sum(1 for r in rows if r["dimension_type"] == dim) == 10, dim
    # 10 distinct parents, each with 4 dimensions
    parents = {}
    for r in rows:
        parents.setdefault(r["parent_requirement_id"], set()).add(r["dimension_type"])
    assert len(parents) == 10
    for pid, dims in parents.items():
        assert dims == DIMENSIONS, (pid, dims)


def test_each_normalized_row_full_shape_and_defer():
    d = json.loads(NORM.read_text(encoding="utf-8"))
    ids = set()
    for r in d["normalized_requirements"]:
        for k in ROW_FIELDS:
            assert k in r and r[k] not in (None, "", []), (r.get("normalized_requirement_id"), k)
        assert r["default_verdict_if_missing"] == "DEFER"
        assert r["expansion_blocker"] == "YES"
        for c in ("creates_fact", "creates_source", "creates_hukm", "creates_tanzil", "creates_final_answer"):
            assert r[c] == "NO", (r["normalized_requirement_id"], c)
        ids.add(r["normalized_requirement_id"])
    assert len(ids) == 40  # unique ids


def test_thirteen_skeletons_not_populated():
    d = json.loads(SKEL.read_text(encoding="utf-8"))
    sk = d["registry_skeletons"]
    assert len(sk) == 13
    assert {s["registry_id"] for s in sk} == THIRTEEN
    for s in sk:
        for k in SKEL_FIELDS:
            assert k in s, (s.get("registry_id"), k)
        assert s["status"] == "SKELETON_ONLY_NOT_POPULATED"
        for c in ("creates_fact", "creates_source", "creates_hukm", "creates_tanzil", "creates_final_answer"):
            assert s[c] == "NO", (s["registry_id"], c)
        assert s["default_verdict_if_empty"] == "DEFER"
        assert s["expansion_blocker_if_empty"] == "YES"


def test_phase0_recheck_still_blocked():
    r = json.loads(RECHECK.read_text(encoding="utf-8"))
    assert r["requirements_registry_verified"] == "YES"
    assert r["requirements_normalized"] == "YES"
    assert r["registry_skeletons_built"] == "YES"
    assert r["registries_populated"] == "NO"
    assert r["owner_supplied_facts_present"] == "NO"
    assert r["factual_facts_complete"] == "NO"
    assert r["phase0_gate_pass"] == "NO"
    assert r["ready_for_expansion"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER"):
        assert r[k] == "NO", k
    assert r["decision"]["verdict"] == "STILL_BLOCKED_AT_PHASE_0_REGISTRIES_NOT_POPULATED"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("NORMALIZATION_DOES_NOT_CREATE_FACT", "NORMALIZATION_DOES_NOT_CREATE_SOURCE",
              "SKELETON_IS_NOT_POPULATED_RECORD", "SOURCE_REGISTRY_SKELETON_DOES_NOT_CREATE_SOURCE",
              "RATIFICATION_REGISTRY_SKELETON_DOES_NOT_CREATE_RATIFICATION",
              "AGENT_QUESTION_IS_NOT_CANONICAL_RULE", "OWNER_RATIFICATION_REQUIRED",
              "EVERYTHING_DEFER_UNTIL_OWNER_DATA", "NO_FINAL_MANAT", "NO_TANZIL", "NO_FINAL_HUKM",
              "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k
    assert g["READY_FOR_EXPANSION"] == "NO"
    assert g["PHASE0_GATE_PASS"] == "NO"


def test_matrix_flags():
    m = _m()
    assert m["NORMALIZED_REQUIREMENT_ROWS"] == "40"
    for k in ("FACT_REQUIREMENT_COUNT", "SOURCE_REQUIREMENT_COUNT",
              "OWNER_DECISION_REQUIREMENT_COUNT", "GATE_REQUIREMENT_COUNT"):
        assert m[k] == "10", k
    assert m["REGISTRY_SKELETON_COUNT"] == "13"
    assert m["REGISTRIES_POPULATED"] == "NO"
    assert m["OWNER_SUPPLIED_FACTS_PRESENT"] == "NO"
    assert m["PHASE0_RECHECK_DONE"] == "YES"
    assert m["PHASE0_GATE_PASS"] == "NO"
    assert m["READY_FOR_EXPANSION"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER"):
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
    assert "ROUND_34_TESTS = passed" in t
    for stmt in ("NORMALIZED_REQUIREMENT_ROWS = 40", "REGISTRY_SKELETON_COUNT = 13",
                 "REGISTRIES_POPULATED = NO", "PHASE0_GATE_PASS = NO", "READY_FOR_EXPANSION = NO",
                 "FINAL_MANAT = NO", "TANZIL = NO", "FINAL_HUKM = NO", "FINAL_ANSWER = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_no_typos_no_noncanonical():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + NORM.read_text(encoding="utf-8")
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
