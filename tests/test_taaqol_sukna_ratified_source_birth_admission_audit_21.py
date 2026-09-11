#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_OWNER_SUPPLIED_SUKNA_SOURCE_BIRTH_ADMISSION_AUDIT_21 — guard test.

Structural admission audit of the owner-supplied+ratified sukna source. Agent does not select/ratify,
does not certify text verbatim, records citation-only evidence (no live links; EXTERNAL_REFS=0), never
lets the source alone be a ruling, keeps possession ≠ final ownership, keeps the composite, and produces
no ḥukm/manāṭ/tanzīl/answer. Coverage of round-13 candidates recorded. Automated-discovery planning is
deferred. Manager report obeys the AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REG = OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json"
AUDIT = OUT / "SUKNA_RATIFIED_SOURCE_ADMISSION_AUDIT_21.json"
GUARDS = OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_GUARDS_21.json"
COVERAGE = OUT / "SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_22.md"
MATRIX = OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_21_MATRIX.csv"
REPORT = OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_MANAGER_REPORT_AR_21.html"
FOUR = {"MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
        "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"}
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
    for p in (REG, AUDIT, GUARDS, COVERAGE, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (REG, AUDIT, GUARDS, COVERAGE):
        json.loads(p.read_text(encoding="utf-8"))


def test_owner_ratified_birth_not_agent():
    r = json.loads(REG.read_text(encoding="utf-8"))
    assert r["ALLOW_SUKNA_SOURCE_BIRTH"] == "YES"
    assert r["SUKNA_SOURCE_FIELDS_COMPLETE"] == "YES"
    assert r["ALLOW_NORMATIVE_HUKM_CANDIDATE"] == "NO"
    assert r["PRIMARY_DOMAIN_CANDIDATE"] == "KEEP_COMPOSITE"
    assert r["sukna_source_born"] == "YES"
    assert r["sukna_source_ratified_by"] == "OWNER"
    assert r["sukna_source_selected_by_agent"] == "NO"
    assert r["born_source"] is not None
    assert r["born_source"]["source_id"] == "SUKNA_SOURCE_1"
    assert r["born_source"]["possession_is_not_final_ownership"] == "YES"
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert a["agent_ratified_source"] == "NO"
    assert a["agent_selected_source"] == "NO"
    assert a["admitted_count"] == 1


def test_admission_full_shape_six_fields():
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    row = a["audit"]
    assert row["source_id"] == "SUKNA_SOURCE_1"
    assert row["domain_link"] == ["SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"]
    for k in ("authority_present", "text_present", "scope_present", "evidence_present",
              "link_license_present", "owner_ratification_present", "domain_link_coherent",
              "scope_has_explicit_preventers", "evidence_is_citation_string",
              "serves_sukna_or_possession_residual", "possession_is_not_final_ownership"):
        assert row[k] == "YES", k
    assert row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE"
    assert row["sukna_source_born"] == "YES"
    assert row["source_ratified_by"] == "OWNER"
    assert row["source_selected_by_agent"] == "NO"
    assert row["text_verbatim_status"] == VERBATIM
    assert row["missing_fields"] == []


def test_born_only_if_six_fields_complete():
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    row = a["audit"]
    six_ok = all(row[k] == "YES" for k in ("authority_present", "text_present", "scope_present",
                 "evidence_present", "link_license_present", "owner_ratification_present"))
    assert six_ok, "six fields must be present"
    assert row["sukna_source_born"] == ("YES" if six_ok else "NO")


def test_coverage_all_four_covered():
    c = json.loads(COVERAGE.read_text(encoding="utf-8"))
    assert c["sukna_or_possession_residual_covered"] == "YES"
    assert c["all_round13_candidates_covered"] == "YES"
    assert set(c["covered_domain_candidates"]) == FOUR
    assert c["uncovered_domain_candidates"] == []
    assert c["composite_kept"] == "YES"
    per = {p["domain_candidate_id"]: p for p in c["per_domain"]}
    assert set(per) == FOUR
    assert per["SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"]["source_ids"] == ["SUKNA_SOURCE_1"]


def test_evidence_citation_only_no_links():
    r = json.loads(REG.read_text(encoding="utf-8"))
    assert r["EVIDENCE_POLICY"] == "CITATION_STRINGS_ONLY"
    ev = r["born_source"]["EVIDENCE"]
    assert "http" not in ev.lower() and "//" not in ev
    blob = REG.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8") + COVERAGE.read_text(encoding="utf-8")
    assert not re.search(r"https?://|www\.|//cdn|quran\.com|sunnah\.com", blob)
    assert _m()["EXTERNAL_REFS"] == "0"


def test_no_hukm_manat_tanzil_final():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["NORMATIVE_HUKM_CANDIDATE_OPENED"] == "NO"
    assert m["AGENT_RATIFIED_SOURCE"] == "NO"
    assert m["SELECTED_BY_AGENT"] == "NO"
    assert m["SUKNA_SOURCE_BORN"] == "YES"
    assert m["RATIFIED_BY"] == "OWNER"
    assert m["POSSESSION_IS_NOT_FINAL_OWNERSHIP"] == "YES"
    assert m["KEEP_COMPOSITE_REMAINS_ACTIVE"] == "YES"
    assert m["AUTOMATED_SOURCE_DISCOVERY_PLANNING"] == "DEFERRED_TO_NEXT_PLANNING_ROUND"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("SOURCE_BIRTH_IS_OWNER_RATIFIED_NOT_AGENT_SELECTED", "AGENT_DID_NOT_RATIFY_SOURCE",
              "AGENT_DID_NOT_SELECT_SOURCE", "STRUCTURAL_ADMISSION_IS_NOT_HUKM", "SCOPE_SELF_LIMITS_HUKM",
              "SOURCE_ALONE_IS_NOT_HUKM", "POSSESSION_IS_NOT_FINAL_OWNERSHIP",
              "NO_NORMATIVE_HUKM_CANDIDATE_OPENED", "EVIDENCE_IS_CITATION_STRING_ONLY",
              "NO_LIVE_EXTERNAL_LINKS", "TEXT_VERBATIM_ASSERTED_BY_OWNER_ONLY",
              "COMPOSITE_KEPT_NOT_COLLAPSED_TO_SINGLE_SOURCE", "NO_NEW_AGENT_SUPPLIED_SOURCE",
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


def test_report_ar09_experience_and_statements():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND_21_TESTS = passed" in t
    assert "التوسعة الآلية مؤجلة" in t
    assert "AUTOMATED_SOURCE_DISCOVERY_PLANNING = DEFERRED_TO_NEXT_PLANNING_ROUND" in t
    assert "AUTHORITY_LEAK" in t
    assert "SUKNA_SOURCE_1" in t
    assert VERBATIM in t
    # explicit: agent did not ratify/select; source alone not a ruling
    assert "AGENT_RATIFIED_SOURCE = NO" in t
    assert "SELECTED_BY_AGENT = NO" in t
    assert "SOURCE_ALONE_IS_NOT_HUKM = YES" in t
    for stmt in ("SUKNA_SOURCE_BORN = YES", "NORMATIVE_HUKM_PRODUCED = NO", "MANAT_PRODUCED = NO",
                 "TANZIL_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO",
                 "SUKNA_OR_POSSESSION_RESIDUAL_COVERED = YES"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_22_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO",
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
