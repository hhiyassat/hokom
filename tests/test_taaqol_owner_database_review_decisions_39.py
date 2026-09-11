#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39 — guard test.

Applies owner decisions: 123 internal records -> ACCEPT_AS_DATABASE_RECORD; 11 external references ->
NEEDS_EXTERNAL_VERIFICATION. ACCEPT is DB-record entry only (not canonical/fact/hukm/generalization). No
final manāṭ/tanzīl/final hukm/final answer. Manager report obeys AR_09_FIXED. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
DEC = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39.json"
DEC_MD = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39.md"
ACC = OUT / "TAAQOL_ACCEPTED_DATABASE_RECORDS_39.json"
EXT = OUT / "TAAQOL_EXTERNAL_REFERENCES_PENDING_VERIFICATION_39.json"
GUARDS = OUT / "TAAQOL_DATABASE_REVIEW_DECISION_GUARDS_39.json"
MATRIX = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39_MATRIX.csv"
REPORT = OUT / "TAAQOL_DATABASE_REVIEW_DECISION_MANAGER_REPORT_AR_39.html"
EXTERNAL_SECTION = "EXTERNAL_REFERENCE_LAYER_CANDIDATES"
NUMBERED = ["1. ملخص للمدير", "2. الجملة محل التشغيل", "3. جدول الكلمات العشر", "4. الإفادة", "5. المقام",
            "6. سياسة المرجع", "7. الدعوى الواقعية ورخصة العبور", "8. المصدر المعياري", "9. موضع التوقف",
            "10. المعلومات الناقصة / الطلب الأدق", "11. ما يلزم بعد الوصول", "12. الاختبارات",
            "13. إثبات سلسلة التوليد", "14. الخلاصة التنفيذية"]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (DEC, DEC_MD, ACC, EXT, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (DEC, ACC, EXT, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_counts_123_accepted_11_pending_134_total():
    d = json.loads(DEC.read_text(encoding="utf-8"))
    assert d["owner_review_rows"] == 134
    assert d["accepted_as_database_record"] == 123
    assert d["external_references_pending_verification"] == 11
    a = json.loads(ACC.read_text(encoding="utf-8"))
    assert a["accepted_count"] == 123 == len(a["records"])
    e = json.loads(EXT.read_text(encoding="utf-8"))
    assert e["pending_count"] == 11 == len(e["records"])
    assert e["decision"] == "NEEDS_EXTERNAL_VERIFICATION"


def test_internal_accepted_external_pending():
    d = json.loads(DEC.read_text(encoding="utf-8"))
    for r in d["decisions"]:
        if r["section"] == EXTERNAL_SECTION:
            assert r["owner_review_decision"] == "NEEDS_EXTERNAL_VERIFICATION"
            assert r["verdict"] == "PENDING_EXTERNAL_VERIFICATION"
        else:
            assert r["owner_review_decision"] == "ACCEPT_AS_DATABASE_RECORD"
            assert r["verdict"] == "ACCEPTED_AS_DATABASE_RECORD_ONLY"


def test_accept_is_not_canonical_fact_or_hukm():
    d = json.loads(DEC.read_text(encoding="utf-8"))
    for r in d["decisions"]:
        assert r["canonical_status"] == "CANDIDATE_ONLY"
        assert r["fact_accepted"] == "NO"
        assert r["generalization_ready"] == "NO"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("ACCEPT_AS_DATABASE_RECORD_IS_NOT_CANONICALIZATION",
              "ACCEPT_AS_DATABASE_RECORD_DOES_NOT_CREATE_FACT",
              "ACCEPT_AS_DATABASE_RECORD_DOES_NOT_CREATE_HUKM",
              "EXTERNAL_REFERENCES_REQUIRE_VERIFICATION"):
        assert g[k] == "YES", k
    for k in ("GENERALIZATION_READY", "FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER",
              "FULL_TAAQOL_PROJECT_CLOSED"):
        assert g[k] == "NO", k


def test_matrix_flags():
    m = _m()
    assert m["OWNER_REVIEW_ROWS"] == "134"
    assert m["ACCEPTED_AS_DATABASE_RECORD"] == "123"
    assert m["EXTERNAL_REFERENCES_PENDING_VERIFICATION"] == "11"
    assert m["ALL_INTERNAL_ACCEPTED"] == "YES"
    assert m["ALL_EXTERNAL_NEEDS_VERIFICATION"] == "YES"
    assert m["ALL_ROWS_CANDIDATE_ONLY"] == "YES"
    assert m["ALL_FACT_ACCEPTED_NO"] == "YES"
    assert m["GENERALIZATION_READY"] == "NO"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "FULL_TAAQOL_PROJECT_CLOSED"):
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
    assert "ROUND_39_TESTS = passed" in t
    assert "ACCEPT_AS_DATABASE_RECORD" in t
    assert "NEEDS_EXTERNAL_VERIFICATION" in t
    for stmt in ("ACCEPTED_AS_DATABASE_RECORD = 123", "EXTERNAL_REFERENCES_PENDING_VERIFICATION = 11",
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
