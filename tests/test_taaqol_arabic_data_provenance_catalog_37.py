#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37 — guard test.

Provenance catalog built from artifacts only. Every record has text_type/source_artifact_path/input_form/
used_as; no text without an artifact path; every generalization candidate requires owner ratification; no
record becomes canonical automatically (SOURCE_RATIFIED ≠ GENERALIZED_RULE); no final manāṭ/tanzīl/final
hukm/final answer; generalization not ready. Manager report obeys AR_09_FIXED. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
CAT = OUT / "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.json"
CAT_MD = OUT / "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.md"
FORMS = OUT / "TAAQOL_TEXT_FORMS_AND_INPUT_FORMATS_37.json"
TABLES = OUT / "TAAQOL_DATABASE_TARGET_TABLES_37.json"
READY = OUT / "TAAQOL_DATA_GENERALIZATION_READINESS_37.json"
GUARDS = OUT / "TAAQOL_DATA_PROVENANCE_GUARDS_37.json"
XREFS = OUT / "TAAQOL_EXTERNAL_REFERENCE_LAYER_CANDIDATES_37.json"
MATRIX = OUT / "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37_MATRIX.csv"
REPORT = OUT / "TAAQOL_DATA_PROVENANCE_MANAGER_REPORT_AR_37.html"
XREF_FIELDS = ["reference_id", "layer_name", "english_reference", "arabic_counterpart_if_any",
               "what_it_gives", "hokom_or_taaqol_mapping", "availability_claim",
               "availability_verification_status", "usage_now", "authority_status",
               "creates_arabic_rule", "creates_shari_hukm", "creates_fact", "creates_manat",
               "creates_tanzil", "generalization_value", "owner_ratification_required",
               "cause", "conditions", "preventers", "verdict", "residuals"]
TEXT_TYPES = {"NAZILA_TEXT", "NAZILA_TOKEN", "OWNER_RULE_TEXT", "NORMATIVE_SOURCE_TEXT", "DOMAIN_TERM",
              "REQUIREMENT_TEXT", "FACT_CANDIDATE_TEXT", "MISSING_FACT_REQUIREMENT_TEXT",
              "HUKM_CANDIDATE_TEXT", "MANAT_CANDIDATE_TEXT", "GUARD_TEXT"}
SOURCE_KINDS = {"OWNER_SUPPLIED_TEXT", "NAZILA_TEXT", "QURAN", "HADITH", "FIQH_SOURCE",
                "GENERATED_REQUIREMENT", "GENERATED_CANDIDATE", "TEST_FIXTURE", "GUARD",
                "UNKNOWN_ARTIFACT_DERIVED"}
INPUT_FORMS = {"FULL_TEXT", "TOKEN", "NORMALIZED_TOKEN", "JSON_FIELD", "MD_SECTION",
               "HTML_REPORT_FIELD", "PYTHON_LITERAL", "TEST_EXPECTATION", "CSV_ROW"}
USED_AS = {"TEXT_INPUT", "EVIDENCE", "SOURCE", "DOMAIN_LABEL", "FACT_CANDIDATE",
           "MISSING_FACT_REQUIREMENT", "REQUIREMENT", "HUKM_CANDIDATE", "MANAT_CANDIDATE",
           "GUARD", "REPORT_ONLY"}
REC_FIELDS = ["record_id", "text_type", "arabic_text", "arabic_text_unvoweled_if_available",
              "normalized_form_if_available", "tokenized_form_if_available", "source_kind",
              "source_authority", "source_round", "source_artifact_path", "source_artifact_field",
              "input_form", "used_as", "database_target_table", "generalization_candidate",
              "owner_ratification_required", "owner_ratified", "canonical_status",
              "should_enter_database", "database_entry_status", "cause", "conditions",
              "preventers", "verdict", "residuals", "notes"]
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
    for p in (CAT, CAT_MD, FORMS, TABLES, READY, GUARDS, XREFS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_external_reference_layer_separate_and_not_authority():
    x = json.loads(XREFS.read_text(encoding="utf-8"))
    assert x["layer_name"] == "EXTERNAL_REFERENCE_LAYER_CANDIDATES"
    refs = x["external_references"]
    assert x["external_reference_count"] == len(refs) == 11
    engs = " ".join(r["english_reference"] for r in refs)
    for probe in ("Universal Dependencies", "WordNet", "VerbNet", "PropBank", "FrameNet",
                  "WordFrameNet", "LegalBench", "Learned Hands", "LexGLUE", "Fiqh/Nazila Takyif"):
        assert probe in engs, probe
    for r in refs:
        for k in XREF_FIELDS:
            assert k in r and r[k] not in (None, ""), (r.get("reference_id"), k)
        assert r["authority_status"] == "EXTERNAL_REFERENCE_CANDIDATE_ONLY"
        assert r["creates_arabic_rule"] == "NO"
        assert r["creates_shari_hukm"] == "NO"
        assert r["creates_fact"] == "NO"
        assert r["creates_manat"] == "NO"
        assert r["creates_tanzil"] == "NO"
        assert r["owner_ratification_required"] == "YES"
        assert r["verdict"] == "DESIGN_OR_BENCHMARK_REFERENCE_ONLY"
        assert r["availability_verification_status"] == "OWNER_SUPPLIED_CLAIM_NOT_VERIFIED_IN_THIS_ROUND"


def test_external_reference_not_in_main_catalog_records():
    # xrefs are a SEPARATE layer, not part of the 123 catalog records
    c = json.loads(CAT.read_text(encoding="utf-8"))
    ids = {r["record_id"] for r in c["records"]}
    assert not any(i.startswith("XREF") for i in ids)
    assert c["total_text_records"] == 123


def test_external_reference_guards_and_matrix():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("EXTERNAL_REFERENCE_IS_NOT_AUTHORITY", "BENCHMARK_IS_NOT_HUKM_SOURCE",
              "ENGLISH_NLP_LAYER_IS_DESIGN_REFERENCE_ONLY", "OWNER_RATIFICATION_REQUIRED_BEFORE_ADOPTION"):
        assert g[k] == "YES", k
    m = _m()
    assert m["EXTERNAL_REFERENCE_LAYER_RECORDS"] == "11"
    assert m["EXTERNAL_REFERENCE_IS_NOT_AUTHORITY"] == "YES"
    assert m["BENCHMARK_IS_NOT_HUKM_SOURCE"] == "YES"
    assert m["ENGLISH_NLP_LAYER_IS_DESIGN_REFERENCE_ONLY"] == "YES"
    assert m["EXTERNAL_REFS_INTERNET_VERIFIED_THIS_ROUND"] == "NO"
    assert m["ALL_XREFS_CREATE_NO_HUKM_OR_ARABIC_RULE"] == "YES"


def test_json_valid():
    for p in (CAT, FORMS, TABLES, READY, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_catalog_artifact_only_and_closed_vocab():
    c = json.loads(CAT.read_text(encoding="utf-8"))
    assert c["report_source"] == "CODE_AND_ARTIFACTS_ONLY"
    assert c["agent_memory_used_as_source"] == "NO"
    recs = c["records"]
    assert c["total_text_records"] == len(recs) == 123
    for r in recs:
        for k in REC_FIELDS:
            assert k in r, (r.get("record_id"), k)
        assert r["text_type"] in TEXT_TYPES
        assert r["source_kind"] in SOURCE_KINDS
        assert r["input_form"] in INPUT_FORMS
        assert r["used_as"] in USED_AS


def test_no_text_without_artifact_path():
    c = json.loads(CAT.read_text(encoding="utf-8"))
    for r in c["records"]:
        assert r["source_artifact_path"], r["record_id"]
        assert r["source_artifact_field"], r["record_id"]


def test_every_record_candidate_only_needs_ratification():
    c = json.loads(CAT.read_text(encoding="utf-8"))
    for r in c["records"]:
        assert r["canonical_status"] == "CANDIDATE_ONLY"
        assert r["owner_ratification_required"] == "YES"
        assert r["generalization_candidate"] == "YES"
        assert r["database_entry_status"] == "CANDIDATE_PENDING_OWNER_RATIFICATION"
        assert r["verdict"] == "DEFER_FOR_OWNER_DATABASE_RATIFICATION"


def test_source_ratified_is_not_generalized_rule():
    c = json.loads(CAT.read_text(encoding="utf-8"))
    ratified = [r for r in c["records"] if r["owner_ratified"] == "YES"]
    assert len(ratified) >= 4  # the born sources are owner-ratified
    for r in ratified:
        # even owner-ratified sources stay CANDIDATE_ONLY (not a generalized rule)
        assert r["canonical_status"] == "CANDIDATE_ONLY"


def test_per_type_counts():
    c = json.loads(CAT.read_text(encoding="utf-8"))
    tc = c["per_text_type_counts"]
    assert tc["NAZILA_TOKEN"] == 10
    assert tc["FACT_CANDIDATE_TEXT"] == 5
    assert tc["MISSING_FACT_REQUIREMENT_TEXT"] == 9
    assert tc["HUKM_CANDIDATE_TEXT"] == 4
    assert tc["MANAT_CANDIDATE_TEXT"] == 4
    assert tc["OWNER_RULE_TEXT"] == 10
    assert tc["REQUIREMENT_TEXT"] == 50
    assert tc["NORMATIVE_SOURCE_TEXT"] == 8   # 4 source texts + 4 authorities
    assert tc["NAZILA_TEXT"] == 1


def test_target_tables_and_forms():
    t = json.loads(TABLES.read_text(encoding="utf-8"))
    assert len(t["database_target_tables"]) == 11
    assert t["all_tables_candidate_only"] == "YES"
    f = json.loads(FORMS.read_text(encoding="utf-8"))
    assert set(f["text_types_closed_vocab"]) == TEXT_TYPES
    assert set(f["source_kinds_closed_vocab"]) == SOURCE_KINDS


def test_readiness_not_ready():
    r = json.loads(READY.read_text(encoding="utf-8"))
    assert r["generalization_ready"] == "NO"
    assert r["owner_database_ratification_required"] == "YES"
    assert r["rule"] == "SOURCE_RATIFIED_IS_NOT_GENERALIZED_RULE"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("ARTIFACT_ONLY_EXTRACTION", "TEXT_EXISTENCE_DOES_NOT_CREATE_RULE",
              "EXAMPLE_DOES_NOT_CREATE_GENERALIZATION", "SOURCE_TEXT_DOES_NOT_CREATE_HUKM",
              "OWNER_RATIFICATION_REQUIRED_FOR_DATABASE_CANONICALIZATION",
              "DATABASE_CATALOG_IS_NOT_FINAL_CLOSURE", "SOURCE_RATIFIED_IS_NOT_GENERALIZED_RULE"):
        assert g[k] == "YES", k
    for k in ("AGENT_MEMORY_USED_AS_SOURCE", "GENERALIZATION_READY", "FINAL_MANAT",
              "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert g[k] == "NO", k


def test_matrix_flags():
    m = _m()
    assert m["AGENT_MEMORY_USED_AS_SOURCE"] == "NO"
    assert m["TOTAL_TEXT_RECORDS"] == "123"
    assert m["TEXT_TYPES_COUNT"] == "11"
    assert m["TOKEN_RECORDS"] == "10"
    assert m["SOURCE_TEXT_RECORDS"] == "8"
    assert m["GENERALIZATION_READY"] == "NO"
    assert m["OWNER_DATABASE_RATIFICATION_REQUIRED"] == "YES"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert m[k] == "NO", k


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
    assert "ROUND_37_CAT_TESTS = passed" in t
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
