#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_FACT_REGISTRY_POPULATION_35 — guard test.

First two registries populated with 5 fact CANDIDATES extracted only from the nazila wording. No accepted
facts, all owner-ratification-required, 9 non-explicit facts remain DEFER. No final manāṭ/tanzīl/final
hukm/final answer; PHASE0_GATE_PASS=NO; READY_FOR_EXPANSION=NO. Manager report obeys AR_09_FIXED.
Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
FCR = OUT / "FACTUAL_CLAIM_REGISTRY_35.json"
OSF = OUT / "OWNER_SUPPLIED_FACT_REGISTRY_35.json"
MISS = OUT / "MISSING_FACT_REQUIREMENTS_35.json"
GUARDS = OUT / "FACT_REGISTRY_POPULATION_GUARDS_35.json"
MATRIX = OUT / "FACT_REGISTRY_POPULATION_35_MATRIX.csv"
REPORT = OUT / "FACT_REGISTRY_POPULATION_MANAGER_REPORT_AR_35.html"
FACT_FIELDS = ["fact_id", "source_text_span", "extracted_surface", "normalized_fact_statement",
               "registry", "owner_supplied_status", "owner_ratification_status", "cause",
               "conditions", "preventers", "verdict", "residuals"]
FIVE = {"FC1_KING_DIED", "FC2_HAS_SISTER", "FC3_SISTER_RESIDING_WITH_HIM",
        "FC4_HEIR_WANTED_EXPULSION", "FC5_LITIGATION_OCCURRED"}
SECTIONS = [
    "1. ملخص للمدير", "2. الجملة محل التشغيل", "3. جدول الكلمات العشر", "4. الإفادة", "5. المقام",
    "6. سياسة المرجع", "7. الدعوى الواقعية ورخصة العبور", "8. المصدر المعياري", "9. موضع التوقف",
    "10. المعلومات الناقصة / الطلب الأدق", "11. ما يلزم بعد الوصول", "12. الاختبارات",
    "13. إثبات سلسلة التوليد", "14. الخلاصة التنفيذية",
]
# facts that must NOT be extracted (remain DEFER)
FORBIDDEN_EXTRACTIONS = ["عدم وجود ولد", "ورثة آخرين", "ملكية البيت النهائية", "تركة كلها",
                         "إذن السكن السابق", "نتيجة التحاكم"]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (FCR, OSF, MISS, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (FCR, OSF, MISS, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_five_fact_candidates_from_text_only():
    d = json.loads(FCR.read_text(encoding="utf-8"))
    facts = d["fact_candidates"]
    assert len(facts) == 5
    assert d["fact_candidate_count"] == 5
    assert {f["fact_id"] for f in facts} == FIVE
    for f in facts:
        for k in FACT_FIELDS:
            assert k in f and f[k] not in (None, "", []), (f.get("fact_id"), k)
        assert f["registry"] == "factual_claim_registry"
        assert f["owner_supplied_status"] == "ASSERTED_BY_NAZILA_TEXT_ONLY"
        assert f["owner_ratification_status"] == "NOT_YET_RATIFIED"
        assert f["verdict"] == "FACT_CANDIDATE_ONLY"


def test_owner_supplied_registry_none_accepted():
    d = json.loads(OSF.read_text(encoding="utf-8"))
    assert d["owner_supplied_fact_count"] == 0
    assert d["owner_ratified_fact_count"] == 0
    recs = d["records"]
    assert len(recs) == 5
    for r in recs:
        assert r["OWNER_SUPPLIED_FACT"] == "NO"
        assert r["OWNER_RATIFICATION_REQUIRED"] == "YES"
        assert r["FACT_ACCEPTED"] == "NO"


def test_missing_facts_remain_defer():
    d = json.loads(MISS.read_text(encoding="utf-8"))
    miss = d["missing_facts"]
    assert d["missing_fact_requirement_count"] == len(miss) >= 9
    for m in miss:
        assert m["status"] == "REQUIRED_FACT_MISSING"
        assert m["default_verdict"] == "DEFER"
        assert m["expansion_blocker"] == "YES"


def test_no_forbidden_fact_extracted():
    d = json.loads(FCR.read_text(encoding="utf-8"))
    blob = json.dumps(d, ensure_ascii=False)
    # none of the fact CANDIDATE statements assert a non-explicit fact
    stmts = " ".join(f["normalized_fact_statement"] for f in d["fact_candidates"])
    for bad in FORBIDDEN_EXTRACTIONS:
        assert bad not in stmts, bad


def test_matrix_flags():
    m = _m()
    assert m["SCOPE"] == "THIS_NAZILA_ONLY"
    assert m["FACT_CANDIDATE_COUNT"] == "5"
    assert m["OWNER_SUPPLIED_FACT_COUNT"] == "0"
    assert m["OWNER_RATIFIED_FACT_COUNT"] == "0"
    assert m["REGISTRIES_POPULATED_PARTIAL"] == "YES"
    assert m["FACTUAL_FACTS_COMPLETE"] == "NO"
    assert m["OWNER_SUPPLIED_FACTS_PRESENT"] == "NO"
    assert m["PHASE0_GATE_PASS"] == "NO"
    assert m["READY_FOR_EXPANSION"] == "NO"
    assert m["NO_FACT_INVENTED_BEYOND_TEXT"] == "YES"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER"):
        assert m[k] == "NO", k
    assert m["AUTHORITY_LEAK"] == "NO"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("NO_FACT_INVENTED_BEYOND_TEXT", "TEXT_ASSERTED_FACT_IS_CANDIDATE_ONLY",
              "FACT_CANDIDATE_IS_NOT_FINAL_FACT", "OWNER_RATIFICATION_REQUIRED_FOR_EVERY_FACT",
              "MISSING_FACTS_STAY_DEFER", "SCOPE_THIS_NAZILA_ONLY", "NO_EXPANSION",
              "NO_FINAL_MANAT", "NO_TANZIL", "NO_FINAL_HUKM", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k
    assert g["PHASE0_GATE_PASS"] == "NO"


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
    assert "ROUND_35_TESTS = passed" in t
    for fid in FIVE:
        assert fid in t, fid
    for stmt in ("FACT_CANDIDATE_COUNT = 5", "OWNER_SUPPLIED_FACT_COUNT = 0",
                 "PHASE0_GATE_PASS = NO", "READY_FOR_EXPANSION = NO",
                 "FINAL_MANAT = NO", "TANZIL = NO", "FINAL_HUKM = NO", "FINAL_ANSWER = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_no_typos_no_noncanonical():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + FCR.read_text(encoding="utf-8")
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
