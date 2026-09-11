#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_RATIFIED_SOURCE_BIRTH_ADMISSION_AUDIT_17 — guard test.

The owner supplied and ratified three normative sources and licensed birth. The agent runs a STRUCTURAL
admission audit only: it does not select or ratify a source, does not certify text verbatim, records
evidence as citation strings (no live links; EXTERNAL_REFS=0), and produces no ḥukm/manāṭ/tanzīl/answer.
Manager report obeys the AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REG = OUT / "RATIFIED_SOURCE_BIRTH_REGISTRY_17.json"
AUDIT = OUT / "RATIFIED_SOURCE_ADMISSION_AUDIT_17.json"
GUARDS = OUT / "RATIFIED_SOURCE_BIRTH_GUARDS_17.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_GATE_18.md"
MATRIX = OUT / "RATIFIED_SOURCE_BIRTH_ADMISSION_AUDIT_17_MATRIX.csv"
REPORT = OUT / "RATIFIED_SOURCE_BIRTH_ADMISSION_MANAGER_REPORT_AR_17.html"
SIDS = {"SOURCE_1", "SOURCE_2", "SOURCE_3"}
FIVE = ["authority_present", "text_present", "scope_present", "evidence_present", "link_license_present"]
SECTIONS = [
    "1. ملخص للمدير", "2. الجملة محل التشغيل", "3. جدول الكلمات العشر", "4. الإفادة", "5. المقام",
    "6. سياسة المرجع", "7. الدعوى الواقعية ورخصة العبور", "8. المصدر المعياري", "9. موضع التوقف",
    "10. المعلومات الناقصة / الطلب الأدق", "11. ما يلزم بعد الوصول", "12. الاختبارات",
    "13. إثبات سلسلة التوليد", "14. الخلاصة التنفيذية",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
VERBATIM = "ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT"


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (REG, AUDIT, GUARDS, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (REG, AUDIT, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_owner_ratified_birth_not_agent():
    r = json.loads(REG.read_text(encoding="utf-8"))
    assert r["ALLOW_NORMATIVE_SOURCE_BIRTH"] == "YES"
    assert r["PRIMARY_DOMAIN_CANDIDATE"] == "KEEP_COMPOSITE"
    assert r["NORMATIVE_SOURCE_SCOPE"] == "THIS_NAZILA_ONLY"
    assert r["normative_source_born"] == "YES"
    assert r["normative_source_ratified_by"] == "OWNER"
    assert r["normative_source_selected_by_agent"] == "NO"
    assert r["born_source_count"] == 3
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert a["agent_ratified_source"] == "NO"
    assert a["agent_selected_source"] == "NO"


def test_three_sources_admitted_full_shape():
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = a["audit"]
    assert len(rows) == 3
    assert {x["source_id"] for x in rows} == SIDS
    for x in rows:
        assert x["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE", x["source_id"]
        for k in FIVE:
            assert x[k] == "YES", (x["source_id"], k)
        assert x["owner_ratification_present"] == "YES"
        assert x["domain_link_coherent"] == "YES"
        assert x["scope_self_limits_hukm"] == "YES"
        assert x["evidence_is_citation_string"] == "YES"
        assert x["source_born"] == "YES"
        assert x["source_ratified_by"] == "OWNER"
        assert x["source_selected_by_agent"] == "NO"
        assert x["text_verbatim_status"] == VERBATIM


def test_multi_link_source_2():
    r = json.loads(REG.read_text(encoding="utf-8"))
    s2 = [s for s in r["owner_supplied_sources"] if s["source_id"] == "SOURCE_2"][0]
    assert set(s2["domain_link"]) == {"MIRATH_RELATED_DOMAIN_CANDIDATE", "TURKAH_RIGHTS_DOMAIN_CANDIDATE"}


def test_evidence_citation_only_no_links():
    r = json.loads(REG.read_text(encoding="utf-8"))
    assert r["EVIDENCE_POLICY"] == "CITATION_STRINGS_ONLY"
    assert r["LIVE_EXTERNAL_LINKS_IN_ARTIFACTS"] == "NO"
    for s in r["owner_supplied_sources"]:
        ev = s["EVIDENCE"]
        assert "http" not in ev.lower() and "//" not in ev, s["source_id"]
    blob = REG.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8")
    assert not re.search(r"https?://|www\.|//cdn|quran\.com|sunnah\.com", blob)
    assert _m()["EXTERNAL_REFS"] == "0"


def test_no_hukm_manat_tanzil_final():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["NORMATIVE_SOURCE_SELECTED_BY_AGENT"] == "NO"
    assert m["AGENT_RATIFIED_SOURCE"] == "NO"
    assert m["NORMATIVE_SOURCE_BORN"] == "YES"
    assert m["NORMATIVE_SOURCE_RATIFIED_BY"] == "OWNER"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("SOURCE_BIRTH_IS_OWNER_RATIFIED_NOT_AGENT_SELECTED", "AGENT_DID_NOT_RATIFY_SOURCE",
              "AGENT_DID_NOT_SELECT_SOURCE", "STRUCTURAL_ADMISSION_IS_NOT_HUKM", "SCOPE_SELF_LIMITS_HUKM",
              "EVIDENCE_IS_CITATION_STRING_ONLY", "NO_LIVE_EXTERNAL_LINKS",
              "TEXT_VERBATIM_ASSERTED_BY_OWNER_ONLY", "COMPOSITE_KEPT_NOT_COLLAPSED_TO_SINGLE_SOURCE",
              "NO_NORMATIVE_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
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
    assert "ROUND_17_TESTS = passed" in t
    for sid in SIDS:
        assert sid in t, sid
    assert VERBATIM in t
    for stmt in ("NORMATIVE_SOURCE_BORN = YES", "NORMATIVE_SOURCE_SELECTED_BY_AGENT = NO",
                 "NORMATIVE_HUKM_PRODUCED = NO", "MANAT_PRODUCED = NO",
                 "TANZIL_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_18_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_SOURCE_TO_MASALA_MAPPING = YES | NO",
              "ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE"):
        assert q in t, q
    assert VERBATIM in t


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
