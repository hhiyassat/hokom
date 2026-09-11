#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_NORMATIVE_HUKM_CANDIDATE_GATE_CONSTITUTION_23 — guard test.

Opens the hukm-CANDIDATE gate only. Candidates are candidate-form (never final hukm/fatwa). No final
hukm/manat/tanzil/answer, source ≠ hukm, possession ≠ final ownership, composite kept, no new source, no
agent ratification, no live links, EXTERNAL_REFS=0. Manager report obeys the AR_09_FIXED experience.
Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
CONST = OUT / "NORMATIVE_HUKM_CANDIDATE_GATE_CONSTITUTION_23.md"
SCHEMA = OUT / "NORMATIVE_HUKM_CANDIDATE_SCHEMA_23.json"
CANDS = OUT / "NORMATIVE_HUKM_CANDIDATES_23.json"
GUARDS = OUT / "NORMATIVE_HUKM_CANDIDATE_GUARDS_23.json"
RESID = OUT / "HUKM_CANDIDATE_RESIDUALS_23.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_APPLICATION_24.md"
MATRIX = OUT / "NORMATIVE_HUKM_CANDIDATE_GATE_23_MATRIX.csv"
REPORT = OUT / "NORMATIVE_HUKM_CANDIDATE_GATE_MANAGER_REPORT_AR_23.html"
CAND_FIELDS = ["hukm_candidate_id", "linked_domain_candidates", "linked_sources",
               "linked_masala_segments", "candidate_statement", "candidate_scope", "cause",
               "conditions", "preventers", "verdict", "evidence", "residuals", "final_hukm_allowed",
               "manat_allowed", "tanzil_allowed", "final_answer_allowed",
               "owner_ratification_required_for_final_hukm"]
ALLOWED_VERDICTS = {"ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY", "DEFER_HUKM_CANDIDATE", "BLOCK_HUKM_CANDIDATE"}
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
    for p in (CONST, SCHEMA, CANDS, GUARDS, RESID, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (SCHEMA, CANDS, GUARDS, RESID):
        json.loads(p.read_text(encoding="utf-8"))


def test_candidate_gate_opened_and_produced():
    m = _m()
    assert m["ALLOW_NORMATIVE_HUKM_CANDIDATE"] == "YES"
    assert m["NORMATIVE_HUKM_CANDIDATE_OPENED"] == "YES"
    assert m["NORMATIVE_HUKM_CANDIDATES_PRODUCED"] in {"YES", "DEFER"}
    c = json.loads(CANDS.read_text(encoding="utf-8"))
    assert c["normative_hukm_candidate_opened"] == "YES"
    assert c["candidate_form_only"] == "YES"
    assert c["hukm_candidate_count"] == 4


def test_four_composite_candidates_full_shape():
    c = json.loads(CANDS.read_text(encoding="utf-8"))
    cands = c["hukm_candidates"]
    ids = {x["hukm_candidate_id"] for x in cands}
    assert {"HC1_SISTER_SHARE", "HC2_CLAIM_BURDEN_OF_PROOF",
            "HC3_POSSESSION_STAYS_PENDING_EXAMINATION", "HC4_COMPOSITE_LINK_NO_OUTCOME"} == ids
    for x in cands:
        for k in CAND_FIELDS:
            assert k in x and x[k] not in (None, "", []), (x["hukm_candidate_id"], k)
        assert x["verdict"] in ALLOWED_VERDICTS
        assert x["verdict"] != "FINAL_HUKM"
        for g in ("final_hukm_allowed", "manat_allowed", "tanzil_allowed", "final_answer_allowed"):
            assert x[g] == "NO", (x["hukm_candidate_id"], g)
        assert x["owner_ratification_required_for_final_hukm"] == "YES"
        # candidate phrasing, not fatwa
        assert "مرشح حكم" in x["candidate_statement"] or "مرشّح حكم" in x["candidate_statement"]


def test_no_verdict_is_final_hukm():
    c = json.loads(CANDS.read_text(encoding="utf-8"))
    for x in c["hukm_candidates"]:
        assert x["verdict"] != "FINAL_HUKM"
    assert _m()["ANY_VERDICT_IS_FINAL_HUKM"] == "NO"
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert s["forbidden_verdict"] == "FINAL_HUKM"
    assert set(s["allowed_verdicts"]) == ALLOWED_VERDICTS


def test_no_final_hukm_manat_tanzil_answer():
    m = _m()
    for k in ("FINAL_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["SOURCE_ALONE_IS_HUKM"] == "NO"
    assert m["POSSESSION_IS_FINAL_OWNERSHIP"] == "NO"
    assert m["NEW_SOURCE_BORN"] == "NO"
    assert m["AGENT_RATIFIED_SOURCE"] == "NO"
    assert m["KEEP_COMPOSITE_REMAINS_ACTIVE"] == "YES"
    assert m["AUTHORITY_LEAK_PREVENTED"] == "YES"
    assert m["OWNER_RATIFICATION_REQUIRED_FOR_FINAL_HUKM"] == "YES"
    assert m["ALL_ROUND13_DOMAIN_CANDIDATES_COVERED"] == "YES"


def test_residuals_block_final_hukm_not_opening():
    r = json.loads(RESID.read_text(encoding="utf-8"))
    assert r["opening_candidate_blocked"] == "NO"
    assert r["final_hukm_blocked"] == "YES"
    assert len(r["open_residuals_before_final_hukm"]) >= 4
    assert r["unresolved_residuals_recorded"] == "YES"
    assert len(r["per_candidate_residuals"]) == 4


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("SOURCE_IS_NOT_HUKM", "SOURCE_MAPPING_IS_NOT_HUKM", "DOMAIN_CANDIDATE_IS_NOT_FINAL_DOMAIN",
              "HUKM_CANDIDATE_IS_NOT_FINAL_HUKM", "HUKM_CANDIDATE_IS_NOT_MANAT",
              "HUKM_CANDIDATE_IS_NOT_TANZIL", "HUKM_CANDIDATE_IS_NOT_FINAL_ANSWER",
              "SOURCE_ALONE_IS_NOT_HUKM", "POSSESSION_IS_NOT_FINAL_OWNERSHIP",
              "KEEP_COMPOSITE_REMAINS_ACTIVE", "NO_NEW_SOURCE_ADDED", "AGENT_DID_NOT_RATIFY_SOURCE",
              "AGENT_DID_NOT_SELECT_SOURCE", "AUTHORITY_LEAK_PREVENTED", "EVIDENCE_IS_CITATION_STRING_ONLY",
              "NO_LIVE_EXTERNAL_LINKS", "NO_FINAL_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_no_live_links_external_refs_zero():
    blob = (CANDS.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8")
            + RESID.read_text(encoding="utf-8") + CONST.read_text(encoding="utf-8"))
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
    assert "ROUND_23_TESTS = passed" in t
    for hc in ("HC1_SISTER_SHARE", "HC2_CLAIM_BURDEN_OF_PROOF",
               "HC3_POSSESSION_STAYS_PENDING_EXAMINATION", "HC4_COMPOSITE_LINK_NO_OUTCOME"):
        assert hc in t, hc
    # explicit statements
    assert "جولة مرشّح حكم فقط" in t
    assert "SOURCE ≠ HUKM" in t
    assert "POSSESSION ≠ FINAL_OWNERSHIP" in t
    for stmt in ("NORMATIVE_HUKM_CANDIDATE_OPENED = YES", "FINAL_HUKM_PRODUCED = NO",
                 "MANAT_PRODUCED = NO", "TANZIL_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_24_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_MANAT = YES | NO", "ALLOW_TANZIL = YES | NO",
              "ALLOW_FINAL_HUKM = YES | NO", "ALLOW_FINAL_ANSWER = YES | NO",
              "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE"):
        assert q in t, q


def test_no_typos_no_noncanonical_no_commit():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + CANDS.read_text(encoding="utf-8")
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
