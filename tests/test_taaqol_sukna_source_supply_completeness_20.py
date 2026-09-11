#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_SUKNA_SOURCE_SUPPLY_COMPLETENESS_GATE_20 — guard test.

Completeness-only audit of the round-19 sukna/possession supply request. No source birth/selection/
ratification, no hukm candidate, no ḥukm/manāṭ/tanzīl/answer, no composite collapse, no live links,
EXTERNAL_REFS=0. Round-19 template is empty → NO_OWNER_SUPPLIED_SOURCE, fields incomplete. Manager report
obeys the AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
AUDIT = OUT / "SUKNA_SOURCE_SUPPLY_COMPLETENESS_AUDIT_20.json"
MISSING = OUT / "SUKNA_SOURCE_MISSING_FIELDS_20.json"
GUARDS = OUT / "SUKNA_SOURCE_COMPLETENESS_GUARDS_20.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_SUKNA_SOURCE_BIRTH_21.md"
MATRIX = OUT / "SUKNA_SOURCE_SUPPLY_COMPLETENESS_20_MATRIX.csv"
REPORT = OUT / "SUKNA_SOURCE_SUPPLY_COMPLETENESS_MANAGER_REPORT_AR_20.html"
TARGET = "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"
ROW_FIELDS = ["domain_candidate_id", "authority_present", "text_present", "scope_present",
              "evidence_present", "link_license_present", "owner_ratification_present",
              "complete", "missing_fields", "cause", "conditions", "preventers", "verdict",
              "sukna_source_born", "sukna_source_fields_complete", "evidence", "residuals"]
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


def test_audit_shape_incomplete():
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert a["ALLOW_SUKNA_SOURCE_BIRTH"] == "NO"
    assert a["ALLOW_NORMATIVE_HUKM_CANDIDATE"] == "NO"
    assert a["audit_mode"] == "COMPLETENESS_ONLY"
    assert a["agent_ratified_source"] == "NO"
    assert a["sukna_source_born"] == "NO"
    row = a["audit"]
    for k in ROW_FIELDS:
        assert k in row, k
    assert row["domain_candidate_id"] == TARGET
    assert row["verdict"] in {"NO_OWNER_SUPPLIED_SOURCE", "INCOMPLETE_SOURCE_SUPPLY"}
    assert row["complete"] == "NO"
    assert row["sukna_source_fields_complete"] == "NO"


def test_missing_fields_recorded():
    m = json.loads(MISSING.read_text(encoding="utf-8"))
    assert m["domain_candidate_id"] == TARGET
    assert isinstance(m["missing_fields"], list)
    assert m["missing_count"] >= 1


def test_matrix_no_birth_no_hukm():
    m = _m()
    assert m["SUKNA_SOURCE_FIELDS_COMPLETE"] == "NO"
    assert m["SUKNA_SOURCE_BORN"] == "NO"
    assert m["SUKNA_SOURCE_BIRTH_STATUS"] == "NOT_OPENED"
    assert m["ALLOW_NORMATIVE_HUKM_CANDIDATE"] == "NO"
    assert m["NORMATIVE_HUKM_CANDIDATE_OPENED"] == "NO"
    assert m["COMPLETENESS_AUDIT_IS_NOT_SOURCE_BIRTH"] == "YES"
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["AGENT_RATIFIED_SOURCE"] == "NO"
    assert m["SELECTED_BY_AGENT"] == "NO"
    assert m["KEEP_COMPOSITE_REMAINS_ACTIVE"] == "YES"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("COMPLETENESS_AUDIT_IS_NOT_SOURCE_BIRTH", "COMPLETE_FIELDS_DO_NOT_BIRTH_SOURCE_WITHOUT_LICENSE",
              "SUKNA_SOURCE_REQUIREMENT_IS_NOT_SOURCE", "NO_SUKNA_SOURCE_BIRTH",
              "NO_NORMATIVE_HUKM_CANDIDATE_OPENED", "AGENT_DID_NOT_RATIFY_SOURCE",
              "AGENT_DID_NOT_SELECT_SOURCE", "COMPOSITE_KEPT_NOT_COLLAPSED",
              "EVIDENCE_IS_CITATION_STRING_ONLY", "NO_LIVE_EXTERNAL_LINKS",
              "NO_NORMATIVE_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_no_live_links_external_refs_zero():
    blob = AUDIT.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8")
    assert not re.search(r"https?://|www\.|//cdn|quran\.com|sunnah\.com", blob)
    assert _m()["EXTERNAL_REFS"] == "0"
    assert _m()["LIVE_EXTERNAL_LINKS_IN_ARTIFACTS"] == "NO"


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
    assert "ROUND_20_TESTS = passed" in t
    assert TARGET in t
    for stmt in ("SUKNA_SOURCE_BORN = NO", "ALLOW_NORMATIVE_HUKM_CANDIDATE = NO",
                 "NORMATIVE_HUKM_PRODUCED = NO", "MANAT_PRODUCED = NO",
                 "TANZIL_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_21_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_SUKNA_SOURCE_BIRTH = YES | NO",
              "SUKNA_SOURCE_FIELDS_COMPLETE = YES",
              "ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE",
              "AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"):
        assert q in t, q


def test_no_typos_no_noncanonical_no_commit():
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


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
