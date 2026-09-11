#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36 — guard test.

Inventories supplied Arabic data from artifacts only into DATABASE_RECORD_CANDIDATE_ONLY records across 12
registries. No record becomes canonical without owner ratification; no example becomes a general rule; no
transition to final manāṭ/tanzīl/final hukm/final answer; generalization not ready. Manager report obeys
AR_09_FIXED. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
INV = OUT / "TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.json"
INV_MD = OUT / "TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.md"
DBC = OUT / "TAAQOL_GENERALIZATION_DATABASE_CANDIDATES_36.json"
BLK = OUT / "TAAQOL_GENERALIZATION_BLOCKERS_36.json"
REQ = OUT / "TAAQOL_DATABASE_RATIFICATION_REQUEST_36.md"
GUARDS = OUT / "TAAQOL_SUPPLIED_DATA_INVENTORY_GUARDS_36.json"
MATRIX = OUT / "TAAQOL_SUPPLIED_DATA_INVENTORY_36_MATRIX.csv"
REPORT = OUT / "TAAQOL_SUPPLIED_DATA_INVENTORY_MANAGER_REPORT_AR_36.html"
TWELVE = {"ARABIC_TEXT_REGISTRY_CANDIDATES", "LEXICAL_ITEM_REGISTRY_CANDIDATES",
          "DOMAIN_REGISTRY_CANDIDATES", "SOURCE_REGISTRY_CANDIDATES", "OWNER_RULE_REGISTRY_CANDIDATES",
          "REQUIREMENT_REGISTRY_CANDIDATES", "FACT_CANDIDATE_REGISTRY_CANDIDATES",
          "MISSING_FACT_REQUIREMENT_REGISTRY_CANDIDATES", "HUKM_CANDIDATE_REGISTRY_CANDIDATES",
          "MANAT_CANDIDATE_REGISTRY_CANDIDATES", "GUARD_AND_GATE_REGISTRY_CANDIDATES"}
REC_FIELDS = ["record_id", "record_type", "surface_or_text", "source_artifact_path", "source_round",
              "owner_supplied", "owner_ratified", "canonical_status", "generalization_status",
              "creates_fact", "creates_source", "creates_hukm", "creates_manat", "creates_tanzil",
              "creates_final_answer", "cause", "conditions", "preventers", "verdict", "residuals",
              "evidence_pointer"]
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
    for p in (INV, INV_MD, DBC, BLK, REQ, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (INV, DBC, BLK, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_twelve_registries_present_and_artifacts_only():
    inv = json.loads(INV.read_text(encoding="utf-8"))
    assert inv["report_source"] == "CODE_AND_ARTIFACTS_ONLY"
    assert TWELVE <= set(inv["registries"].keys())
    assert inv["data_sources_scanned"] > 0
    assert inv["database_candidate_records"] == sum(len(v) for v in inv["registries"].values())


def test_expected_counts_from_artifacts():
    inv = json.loads(INV.read_text(encoding="utf-8"))
    c = inv["registry_counts"]
    # grounded in real artifacts (rounds 23/24/35/32/34)
    assert c["FACT_CANDIDATE_REGISTRY_CANDIDATES"] == 5
    assert c["MISSING_FACT_REQUIREMENT_REGISTRY_CANDIDATES"] == 9
    assert c["HUKM_CANDIDATE_REGISTRY_CANDIDATES"] == 4
    assert c["MANAT_CANDIDATE_REGISTRY_CANDIDATES"] == 4
    assert c["SOURCE_REGISTRY_CANDIDATES"] == 4
    assert c["LEXICAL_ITEM_REGISTRY_CANDIDATES"] == 10
    assert c["OWNER_RULE_REGISTRY_CANDIDATES"] >= 8
    assert c["REQUIREMENT_REGISTRY_CANDIDATES"] == 50  # 10 parents + 40 normalized


def test_every_record_full_shape_candidate_only_defer():
    inv = json.loads(INV.read_text(encoding="utf-8"))
    for reg, recs in inv["registries"].items():
        for r in recs:
            for k in REC_FIELDS:
                assert k in r, (reg, r.get("record_id"), k)
            assert r["canonical_status"] == "CANDIDATE_ONLY"
            assert r["generalization_status"] == "NOT_READY_FOR_GENERALIZATION"
            assert r["verdict"] == "DEFER_FOR_OWNER_DATABASE_RATIFICATION"
            for c in ("creates_fact", "creates_source", "creates_hukm",
                      "creates_manat", "creates_tanzil", "creates_final_answer"):
                assert r[c] == "NO", (r["record_id"], c)


def test_no_record_canonical_without_owner_ratification():
    inv = json.loads(INV.read_text(encoding="utf-8"))
    for reg, recs in inv["registries"].items():
        for r in recs:
            # canonical_status is CANDIDATE_ONLY for ALL records regardless of owner_ratified
            assert r["canonical_status"] != "CANONICAL"


def test_lexical_examples_not_general_rules():
    inv = json.loads(INV.read_text(encoding="utf-8"))
    for r in inv["registries"]["LEXICAL_ITEM_REGISTRY_CANDIDATES"]:
        assert r["record_type"] == "LEXICAL_ITEM"
        assert r["generalization_status"] == "NOT_READY_FOR_GENERALIZATION"
        assert r["creates_hukm"] == "NO"


def test_no_transition_to_final_stages():
    m = _m()
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert m[k] == "NO", k
    assert m["GENERALIZATION_READY"] == "NO"
    assert m["OWNER_DATABASE_RATIFICATION_REQUIRED"] == "YES"
    assert m["AGENT_MEMORY_USED_AS_SOURCE"] == "NO"


def test_blockers_present():
    b = json.loads(BLK.read_text(encoding="utf-8"))
    assert b["generalization_ready"] == "NO"
    assert b["blocker_count"] >= 9
    for x in b["blockers"]:
        assert x["verdict"] == "BLOCK_GENERALIZATION"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("AGENT_MEMORY_USED_AS_SOURCE", "AGENT_QUESTION_CREATES_RULE",
              "TEXT_EXAMPLE_CREATES_GENERAL_RULE", "SOURCE_TEXT_CREATES_HUKM",
              "FACT_CANDIDATE_CREATES_FACT", "GENERALIZATION_READY", "FINAL_MANAT",
              "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert g[k] == "NO", k
    for k in ("OWNER_RATIFICATION_REQUIRED_FOR_GENERALIZATION", "DATABASE_RECORD_CANDIDATE_ONLY"):
        assert g[k] == "YES", k


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
    assert "ROUND_36_INV_TESTS = passed" in t
    for stmt in ("GENERALIZATION_READY = NO", "OWNER_DATABASE_RATIFICATION_REQUIRED = YES",
                 "FINAL_MANAT = NO", "TANZIL = NO", "FINAL_HUKM = NO", "FINAL_ANSWER = NO",
                 "FULL_TAAQOL_PROJECT_CLOSED = NO", "AGENT_MEMORY_USED_AS_SOURCE = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_no_typos_no_noncanonical_no_livelinks():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8")
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
