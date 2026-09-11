#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_OWNER_SUPPLIED_NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16 — guard test.

Completeness-only audit of the round-15 supply template. It never births, selects, or ratifies a source,
and produces no ḥukm/manāṭ/tanzīl/final answer. Manager report obeys the AR_09_FIXED experience (14
ordered sections + standalone traceability table + closure flags + tests-result block). Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
AUDIT = OUT / "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16.json"
MISSING = OUT / "NORMATIVE_SOURCE_MISSING_FIELDS_16.json"
GUARDS = OUT / "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_GUARDS_16.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_17.md"
MATRIX = OUT / "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16_MATRIX.csv"
REPORT = OUT / "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_MANAGER_REPORT_AR_16.html"
FOUR = {"MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
        "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"}
PER_ROW = ["domain_candidate_id", "source_entry_present", "authority_present", "text_present",
           "scope_present", "evidence_present", "link_license_present", "owner_ratification_present",
           "complete", "missing_fields", "cause", "conditions", "preventers", "verdict",
           "evidence", "residuals"]
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
    for p in (AUDIT, MISSING, GUARDS, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (AUDIT, MISSING, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_all_four_candidates_checked_with_full_shape():
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert a["NORMATIVE_SOURCE_COMPLETENESS_AUDIT_ALLOWED"] == "YES"
    assert a["NORMATIVE_SOURCE_BIRTH_ALLOWED"] == "NO"
    assert a["NORMATIVE_SOURCE_SELECTION_ALLOWED"] == "NO"
    assert a["NORMATIVE_SOURCE_RATIFICATION_ALLOWED"] == "NO"
    assert a["domain_candidate_count_checked"] == 4
    rows = a["audit"]
    assert len(rows) == 4
    assert {r["domain_candidate_id"] for r in rows} == FOUR
    for r in rows:
        for k in PER_ROW:
            assert k in r, (r["domain_candidate_id"], k)
        assert r["verdict"] in {"COMPLETE_BUT_NOT_BORN", "INCOMPLETE_SOURCE_SUPPLY", "NO_OWNER_SUPPLIED_SOURCE"}


def test_missing_fields_present():
    m = json.loads(MISSING.read_text(encoding="utf-8"))
    per = m["missing_fields_by_candidate"]
    assert len(per) == 4
    assert {p["domain_candidate_id"] for p in per} == FOUR
    for p in per:
        assert "missing_fields" in p and isinstance(p["missing_fields"], list)
    # round-15 template is empty → every candidate is missing fields (audit, not birth)
    assert m["missing_fields_total"] >= 1


def test_source_not_born_selected_ratified():
    m = _m()
    assert m["NORMATIVE_SOURCE_BORN"] == "NO"
    assert m["NORMATIVE_SOURCE_SELECTED"] == "NO"
    assert m["NORMATIVE_SOURCE_RATIFIED"] == "NO"
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "NOT_OPENED"
    assert m["COMPLETENESS_AUDIT_IS_NOT_SOURCE_BIRTH"] == "YES"


def test_no_hukm_manat_tanzil_final():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("COMPLETENESS_AUDIT_IS_NOT_SOURCE_BIRTH",
              "COMPLETE_FIELDS_DO_NOT_BIRTH_SOURCE_WITHOUT_LICENSE",
              "SOURCE_TEMPLATE_IS_NOT_SOURCE", "SOURCE_REQUIREMENT_IS_NOT_RATIFICATION",
              "NO_NORMATIVE_SOURCE_BIRTH", "NO_NORMATIVE_SOURCE_RATIFICATION",
              "NO_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_report_sections_ordered_1_to_14():
    t = REPORT.read_text(encoding="utf-8")
    positions = []
    for s in SECTIONS:
        idx = t.find(s)
        assert idx != -1, s
        positions.append(idx)
    assert positions == sorted(positions), "sections not in order"


def test_report_ar09_experience():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND_16_TESTS = passed" in t
    for did in FOUR:
        assert did in t, did
    for stmt in ("NORMATIVE_SOURCE_BORN = NO", "NORMATIVE_SOURCE_RATIFIED = NO",
                 "NORMATIVE_SOURCE_SELECTED = NO", "NORMATIVE_HUKM_PRODUCED = NO",
                 "MANAT_PRODUCED = NO", "TANZIL_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_17_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_NORMATIVE_SOURCE_BIRTH = YES",
              "PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE | PICK_ONE",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE",
              "AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"):
        assert q in t, q


def test_no_typos_no_external_refs_no_commit():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + AUDIT.read_text(encoding="utf-8")
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
    assert m["EXTERNAL_REFS"] == "0"
    assert not re.search(r"https?://|//cdn", t)


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
