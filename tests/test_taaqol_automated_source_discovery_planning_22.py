#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_AUTOMATED_NORMATIVE_SOURCE_DISCOVERY_PLANNING_22 — guard test.

Planning-only round: records the future automated source-discovery architecture. It executes no search,
produces no source candidate, births no source, ratifies/selects no source, opens no hukm candidate, and
produces no ḥukm/manāṭ/tanzīl/answer. No live links; EXTERNAL_REFS=0. Manager report obeys the
AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
PLAN = OUT / "AUTOMATED_NORMATIVE_SOURCE_DISCOVERY_PLANNING_22.md"
SCHEMA = OUT / "AUTOMATED_SOURCE_DISCOVERY_SCHEMA_DRAFT_22.json"
GUARDS = OUT / "AUTOMATED_SOURCE_DISCOVERY_GUARDS_22.json"
ROADMAP = OUT / "AUTOMATED_SOURCE_DISCOVERY_ROADMAP_22.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_23.md"
MATRIX = OUT / "AUTOMATED_SOURCE_DISCOVERY_PLANNING_22_MATRIX.csv"
REPORT = OUT / "AUTOMATED_SOURCE_DISCOVERY_MANAGER_REPORT_AR_22.html"
SOURCE_TYPES = {"QURAN_AYAH", "HADITH", "FIQH_TEXT", "QADA_TEXT", "QAIDA_FIQHIYYA",
                "USUL_TEXT", "OWNER_SUPPLIED_TEXT"}
CANDIDATE_FIELDS = {"source_candidate_id", "source_type", "authority_candidate", "text_candidate",
                    "scope_candidate", "evidence_candidate", "domain_candidate_links", "served_needs",
                    "not_served_needs", "confidence_basis", "risk_flags", "cause", "conditions",
                    "preventers", "verdict", "residuals"}
VERBATIM_STATUSES = {"ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT", "VERIFIED_BY_AUTHORIZED_SOURCE_TOOL",
                     "NOT_VERIFIED"}
FUTURE_ROUNDS = {"FUTURE_ROUND_A", "FUTURE_ROUND_B", "FUTURE_ROUND_C", "FUTURE_ROUND_D", "FUTURE_ROUND_E"}
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
    for p in (PLAN, SCHEMA, GUARDS, ROADMAP, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (SCHEMA, GUARDS, ROADMAP):
        json.loads(p.read_text(encoding="utf-8"))


def test_schema_planning_only():
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert s["planning_only"] == "YES"
    assert s["automated_source_discovery_executed"] == "NO"
    assert s["candidacy_stage_output"] == "SOURCE_CANDIDATE_ONLY"
    assert set(s["source_types"]) == SOURCE_TYPES
    assert set(s["source_candidate_fields"]) == CANDIDATE_FIELDS
    assert set(s["text_verbatim_status_allowed"]) == VERBATIM_STATUSES
    assert s["evidence_policy_default"] == "CITATION_STRINGS_ONLY"
    assert s["live_external_links_default"] == "NO"
    assert s["external_refs_default"] == 0
    assert len(s["future_search_sources"]) == 8
    assert len(s["ranking_criteria"]) == 7


def test_roadmap_future_rounds_and_prior_links():
    r = json.loads(ROADMAP.read_text(encoding="utf-8"))
    assert {x["future_round"] for x in r["future_roadmap"]} == FUTURE_ROUNDS
    rounds = {x["round"] for x in r["prior_round_links"]}
    for needed in ("ROUND_10", "ROUND_13", "ROUND_17", "ROUND_18", "ROUND_21"):
        assert needed in rounds, needed
    assert r["current_state"]["ALL_ROUND13_DOMAIN_CANDIDATES_COVERED"] == "YES"
    assert r["current_state"]["NORMATIVE_HUKM_CANDIDATE_OPENED"] == "NO"


def test_planning_does_not_birth_or_open_hukm():
    m = _m()
    assert m["PLANNING_ONLY"] == "YES"
    assert m["AUTOMATED_SOURCE_DISCOVERY_EXECUTED"] == "NO"
    assert m["NEW_SOURCE_BORN"] == "NO"
    assert m["SOURCE_CANDIDATE_PRODUCED"] == "NO"
    assert m["NORMATIVE_HUKM_CANDIDATE_OPENED"] == "NO"
    assert m["NO_INTERNET_SEARCH"] == "YES"
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["ALL_ROUND13_DOMAIN_CANDIDATES_COVERED"] == "YES"
    assert m["PRIMARY_DOMAIN_CANDIDATE"] == "KEEP_COMPOSITE"


def test_agent_cannot_ratify_owner_required_authority_leak():
    m = _m()
    assert m["AGENT_CANNOT_RATIFY_SOURCE"] == "YES"
    assert m["OWNER_RATIFICATION_REQUIRED"] == "YES"
    assert m["OWNER_RATIFICATION_REQUIRED_FOR_FUTURE_SOURCE_BIRTH"] == "YES"
    assert m["AUTHORITY_LEAK_PREVENTED"] == "YES"
    assert m["AGENT_RATIFIED_SOURCE"] == "NO"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("TEXT_SIGNAL_IS_NOT_SOURCE_CANDIDATE", "SOURCE_CANDIDATE_IS_NOT_NORMATIVE_SOURCE",
              "NORMATIVE_SOURCE_IS_NOT_HUKM", "SOURCE_DISCOVERY_IS_NOT_SOURCE_RATIFICATION",
              "AGENT_CANNOT_RATIFY_SOURCE", "OWNER_RATIFICATION_REQUIRED", "AUTHORITY_LEAK_PREVENTED",
              "PLANNING_ONLY_NOT_EXECUTION", "NO_NEW_SOURCE_BORN", "NO_SOURCE_CANDIDATE_PRODUCED_THIS_ROUND",
              "NO_NORMATIVE_HUKM_CANDIDATE_OPENED", "NO_LIVE_EXTERNAL_LINKS", "NO_INTERNET_SEARCH",
              "COMPOSITE_KEPT_NOT_COLLAPSED", "POSSESSION_IS_NOT_FINAL_OWNERSHIP",
              "NO_NORMATIVE_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k
    assert len(g["prohibition_rules"]) == 8


def test_planning_md_contents():
    t = PLAN.read_text(encoding="utf-8")
    for st in SOURCE_TYPES:
        assert st in t, st
    for fr in FUTURE_ROUNDS:
        assert fr in t, fr
    assert "SOURCE_CANDIDATE_ONLY" in t
    assert "AUTHORITY_LEAK_PREVENTED = YES" in t


def test_no_live_links_external_refs_zero():
    blob = (SCHEMA.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8")
            + ROADMAP.read_text(encoding="utf-8") + PLAN.read_text(encoding="utf-8"))
    assert not re.search(r"https?://|www\.|//cdn|quran\.com|sunnah\.com", blob)
    assert _m()["EXTERNAL_REFS"] == "0"


def test_report_sections_ordered_1_to_14():
    t = REPORT.read_text(encoding="utf-8")
    positions = []
    for s in SECTIONS:
        idx = t.find(s)
        assert idx != -1, s
        positions.append(idx)
    assert positions == sorted(positions), "sections not in order"


def test_report_ar09_experience_and_explicit_statements():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND_22_TESTS = passed" in t
    # explicit: planning not execution / no hukm-manat-tanzil-answer / no new source
    assert "جولة تخطيط لا تنفيذ" in t
    assert "لا مصدر جديد وُلد" in t
    for stmt in ("PLANNING_ONLY = YES", "NEW_SOURCE_BORN = NO", "NORMATIVE_HUKM_CANDIDATE_OPENED = NO",
                 "NORMATIVE_HUKM_PRODUCED = NO", "MANAT_PRODUCED = NO", "TANZIL_PRODUCED = NO",
                 "FINAL_ANSWER_PRODUCED = NO", "AUTHORITY_LEAK_PREVENTED = YES"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_23_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE",
              "FUTURE_ROUND_A"):
        assert q in t, q


def test_no_typos_no_noncanonical_no_commit():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + SCHEMA.read_text(encoding="utf-8")
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
