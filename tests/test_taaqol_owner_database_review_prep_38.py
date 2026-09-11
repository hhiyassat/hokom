#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_OWNER_DATABASE_REVIEW_PREP_38 — guard test.

Owner review preparation (not ratification): 123 catalog records + 11 external references = 134 rows,
grouped in 12 sections, every row defaulting to DEFER with a closed decision vocabulary. No record
auto-accepted / canonical; no generalization; no final manāṭ/tanzīl/final hukm/final answer. Manager
report obeys AR_09_FIXED. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
PREP = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.json"
PREP_MD = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.md"
MTX = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_MATRIX_38.json"
GUARDS = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_GUARDS_38.json"
MATRIX = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38_MATRIX.csv"
REPORT = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_MANAGER_REPORT_AR_38.html"
ALLOWED = {"ACCEPT_AS_DATABASE_RECORD", "DEFER", "REJECT", "NEEDS_SOURCE",
           "NEEDS_FORMAT_FIX", "NEEDS_OWNER_DEFINITION", "NEEDS_EXTERNAL_VERIFICATION"}
SECTIONS = {"NAZILA_TEXT", "NAZILA_TOKEN", "NORMATIVE_SOURCE_TEXT", "OWNER_RULE_TEXT", "DOMAIN_TERM",
            "REQUIREMENT_TEXT", "FACT_CANDIDATE_TEXT", "MISSING_FACT_REQUIREMENT_TEXT",
            "HUKM_CANDIDATE_TEXT", "MANAT_CANDIDATE_TEXT", "GUARD_TEXT",
            "EXTERNAL_REFERENCE_LAYER_CANDIDATES"}
ROW_FIELDS = ["record_id", "section", "text_type", "reference_layer",
              "arabic_text_or_english_reference", "source_round", "source_artifact_path", "used_as",
              "database_target_table", "current_status", "owner_review_decision", "owner_notes",
              "required_action", "canonical_status", "cause", "conditions", "preventers", "verdict",
              "residuals"]
NUM_SECTIONS = [
    "1. NAZILA_TEXT", "2. NAZILA_TOKEN", "3. NORMATIVE_SOURCE_TEXT", "4. OWNER_RULE_TEXT",
    "5. DOMAIN_TERM", "6. REQUIREMENT_TEXT", "7. FACT_CANDIDATE_TEXT",
    "8. MISSING_FACT_REQUIREMENT_TEXT", "9. HUKM_CANDIDATE_TEXT", "10. MANAT_CANDIDATE_TEXT",
    "11. GUARD_TEXT", "12. EXTERNAL_REFERENCE_LAYER_CANDIDATES",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (PREP, PREP_MD, MTX, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (PREP, MTX, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_counts_123_plus_11_equals_134():
    d = json.loads(PREP.read_text(encoding="utf-8"))
    assert d["catalog_records_loaded"] == 123
    assert d["external_reference_records_loaded"] == 11
    assert d["owner_review_rows_created"] == 134
    assert len(d["rows"]) == 134


def test_every_row_full_shape_and_default_defer():
    d = json.loads(PREP.read_text(encoding="utf-8"))
    for r in d["rows"]:
        for k in ROW_FIELDS:
            assert k in r, (r.get("record_id"), k)
        assert r["section"] in SECTIONS
        assert r["owner_review_decision"] == "DEFER"
        assert r["owner_review_decision"] in ALLOWED
        assert r["verdict"] == "AWAITING_OWNER_REVIEW"
        assert r["canonical_status"] == "CANDIDATE_ONLY"
        assert r["source_artifact_path"]


def test_allowed_decision_vocab_closed():
    d = json.loads(PREP.read_text(encoding="utf-8"))
    assert set(d["allowed_decisions"]) == ALLOWED
    assert d["default_decision"] == "DEFER"


def test_section_coverage_and_external_layer():
    d = json.loads(PREP.read_text(encoding="utf-8"))
    secs = {}
    for r in d["rows"]:
        secs[r["section"]] = secs.get(r["section"], 0) + 1
    assert set(secs.keys()) == SECTIONS
    assert secs["EXTERNAL_REFERENCE_LAYER_CANDIDATES"] == 11
    assert secs["NAZILA_TOKEN"] == 10
    assert secs["REQUIREMENT_TEXT"] == 50
    # external rows must not be authorities
    for r in d["rows"]:
        if r["section"] == "EXTERNAL_REFERENCE_LAYER_CANDIDATES":
            assert r["text_type"] == "EXTERNAL_REFERENCE"
            assert r["canonical_status"] == "CANDIDATE_ONLY"


def test_no_record_becomes_canonical():
    d = json.loads(PREP.read_text(encoding="utf-8"))
    for r in d["rows"]:
        assert r["canonical_status"] != "CANONICAL"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("OWNER_REVIEW_PREP_IS_NOT_RATIFICATION", "NO_RECORD_AUTO_ACCEPTED", "ALL_DEFAULT_TO_DEFER",
              "EXTERNAL_REFERENCE_IS_NOT_AUTHORITY", "ACCEPT_AS_DATABASE_RECORD_DOES_NOT_CREATE_HUKM"):
        assert g[k] == "YES", k
    for k in ("GENERALIZATION_READY", "FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER",
              "FULL_TAAQOL_PROJECT_CLOSED"):
        assert g[k] == "NO", k


def test_matrix_flags():
    m = _m()
    assert m["CATALOG_RECORDS_LOADED"] == "123"
    assert m["EXTERNAL_REFERENCE_RECORDS_LOADED"] == "11"
    assert m["OWNER_REVIEW_ROWS_CREATED"] == "134"
    assert m["DEFAULT_DECISION"] == "DEFER"
    assert m["ALL_ROWS_DEFAULT_DEFER"] == "YES"
    assert m["ALL_ROWS_CANDIDATE_ONLY"] == "YES"
    assert m["OWNER_REVIEW_PREP_IS_NOT_RATIFICATION"] == "YES"
    assert m["GENERALIZATION_READY"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert m[k] == "NO", k


def test_report_sections_ordered_1_to_14():
    t = REPORT.read_text(encoding="utf-8")
    numbered = ["1. ملخص للمدير", "2. الجملة محل التشغيل", "3. جدول الكلمات العشر", "4. الإفادة",
                "5. المقام", "6. سياسة المرجع", "7. الدعوى الواقعية ورخصة العبور", "8. المصدر المعياري",
                "9. موضع التوقف", "10. المعلومات الناقصة / الطلب الأدق", "11. ما يلزم بعد الوصول",
                "12. الاختبارات", "13. إثبات سلسلة التوليد", "14. الخلاصة التنفيذية"]
    positions = []
    for s in numbered:
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
    assert "ROUND_38_TESTS = passed" in t
    assert "EXTERNAL_REFERENCE_LAYER_CANDIDATES" in t
    for stmt in ("OWNER_REVIEW_ROWS_CREATED = 134", "DEFAULT_DECISION = DEFER",
                 "GENERALIZATION_READY = NO", "FINAL_MANAT = NO", "TANZIL = NO",
                 "FINAL_HUKM = NO", "FINAL_ANSWER = NO", "FULL_TAAQOL_PROJECT_CLOSED = NO"):
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
