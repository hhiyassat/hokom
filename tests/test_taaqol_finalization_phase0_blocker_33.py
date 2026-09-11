#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_FINALIZATION_CHAIN PHASE 0 blocker — guard test.

The finalization chain must STOP at PHASE 0 because the normalized requirement registry (round 33) is
absent, none of the 13 registries are built, and no owner-supplied facts exist. No local sync (later
phase), no final manāṭ/tanzīl/final hukm/final answer, no full-project closure claim. Manager report
obeys the AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
BLOCKER = OUT / "TAAQOL_FINALIZATION_PHASE0_BLOCKER_33.json"
REQ = OUT / "TAAQOL_REQUIREMENT_NORMALIZATION_REQUEST_33.md"
GUARDS = OUT / "TAAQOL_FINALIZATION_PHASE0_GUARDS_33.json"
MATRIX = OUT / "TAAQOL_FINALIZATION_PHASE0_BLOCKER_33_MATRIX.csv"
REPORT = OUT / "TAAQOL_FINALIZATION_PHASE0_BLOCKER_MANAGER_REPORT_AR_33.html"
NORMALIZED_33 = OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_33.json"
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
    for p in (BLOCKER, REQ, GUARDS, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (BLOCKER, GUARDS):
        json.loads(p.read_text(encoding="utf-8"))


def test_stopped_at_phase0():
    b = json.loads(BLOCKER.read_text(encoding="utf-8"))
    assert b["STOPPED_AT_PHASE"] == "PHASE_0"
    assert b["STOP_REASON"] == "REQUIREMENTS_REGISTRY_OR_NORMALIZATION_REQUIRED"
    assert b["phase0_gate_pass"] == "NO"
    assert b["requirements_registry_verified"] == "YES"
    assert b["requirements_normalized"] == "NO"
    assert b["registries_built"] == 0
    assert b["registries_required"] == 13
    assert b["owner_supplied_facts_present"] == "NO"
    assert b["ready_for_expansion"] == "NO"


def test_no_leap_flags():
    b = json.loads(BLOCKER.read_text(encoding="utf-8"))
    for k in ("LOCAL_SYNC_DONE",):
        assert b[k] == "NO", k
    assert b["SYNC_MODE"] == "SKIPPED"
    for k in ("FACTUAL_MANAT_APPLICATION_DONE", "FACTUAL_FACTS_COMPLETE", "FINAL_MANAT",
              "TANZIL", "FINAL_HUKM", "FINAL_ANSWER", "TAAQOL_NAZILA_PIPELINE_CLOSED",
              "FULL_TAAQOL_PROJECT_CLOSED"):
        assert b[k] == "NO", k


def test_decision_has_governance_fields():
    b = json.loads(BLOCKER.read_text(encoding="utf-8"))
    d = b["decision"]
    for k in ("cause", "conditions", "preventers", "verdict", "residuals"):
        assert d[k], k
    assert d["verdict"] == "STOP_AT_PHASE_0_DEFER_FINALIZATION"
    # every phase0 check carries governance fields
    for c in b["phase0_checks"]:
        for k in ("cause", "conditions", "preventers", "verdict", "residuals"):
            assert c[k], (c["check_id"], k)
    # the normalization check must FAIL (33 absent)
    c5 = [c for c in b["phase0_checks"] if c["check_id"] == "C5_NORMALIZED_REGISTRY_33_PRESENT"][0]
    assert c5["verdict"] == "FAIL"


def test_normalized_33_actually_absent():
    # the blocker's premise must match reality
    assert not NORMALIZED_33.exists()


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("PHASE0_GATE_BLOCKS_FINALIZATION", "NO_LEAP_TO_FINAL_MANAT",
              "AGENT_QUESTION_IS_NOT_CANONICAL_RULE", "REQUIREMENT_DOES_NOT_CREATE_FACT",
              "SOURCE_REQUIREMENT_DOES_NOT_CREATE_SOURCE", "SOURCE_DOES_NOT_CREATE_HUKM",
              "POSSESSION_DOES_NOT_CREATE_FINAL_OWNERSHIP", "PROOF_BURDEN_DOES_NOT_DECIDE_SUBSTANTIVE_RIGHT",
              "OWNER_RATIFICATION_REQUIRED", "NO_FINAL_MANAT", "NO_TANZIL", "NO_FINAL_HUKM",
              "NO_FINAL_ANSWER", "NO_FULL_PROJECT_CLOSURE_FROM_ONE_NAZILA"):
        assert g[k] == "YES", k
    assert g["READY_FOR_EXPANSION"] == "NO"
    assert g["AUTHORITY_LEAK"] == "NO"


def test_normalization_request_content():
    t = REQ.read_text(encoding="utf-8")
    for token in ("factual_claim_registry", "owner_ratification_registry",
                  "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_33.json",
                  "ALLOW_REQUIREMENT_NORMALIZATION_33 = YES | NO",
                  "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE"):
        assert token in t, token


def test_matrix_flags():
    m = _m()
    assert m["STOPPED_AT_PHASE"] == "PHASE_0"
    assert m["LOCAL_SYNC_DONE"] == "NO"
    assert m["SYNC_MODE"] == "SKIPPED"
    for k in ("FINAL_MANAT", "TANZIL", "FINAL_HUKM", "FINAL_ANSWER",
              "TAAQOL_NAZILA_PIPELINE_CLOSED", "FULL_TAAQOL_PROJECT_CLOSED"):
        assert m[k] == "NO", k
    assert m["AUTHORITY_LEAK"] == "NO"
    assert m["READY_FOR_EXPANSION"] == "NO"
    assert m["COMMIT"] == "NO"
    assert m["PUSH_EXECUTED"] == "NO"


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
    assert "ROUND_33_TESTS = passed" in t
    for stmt in ("STOPPED_AT_PHASE = PHASE_0", "FINAL_MANAT = NO", "TANZIL = NO",
                 "FINAL_HUKM = NO", "FINAL_ANSWER = NO", "FULL_TAAQOL_PROJECT_CLOSED = NO",
                 "AUTHORITY_LEAK = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_no_typos_no_noncanonical_no_commit():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + BLOCKER.read_text(encoding="utf-8")
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
    assert not re.search(r"https?://|www\.|//cdn", t)


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
