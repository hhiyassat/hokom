#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_MANAT_CANDIDATE_EXTRACTION_GATE_24 — guard test.

Extracts manāṭ CANDIDATES (candidate-form only) from the four round-23 hukm candidates. No final manat/
hukm/tanzil/answer, no share amount, no ownership, no final residence right, no judicial obligation,
source ≠ manat/hukm, possession ≠ final ownership, composite kept, no new source, no agent ratification,
no live links, EXTERNAL_REFS=0. Manager report obeys the AR_09_FIXED experience. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
CONST = OUT / "MANAT_CANDIDATE_EXTRACTION_CONSTITUTION_24.md"
SCHEMA = OUT / "MANAT_CANDIDATE_SCHEMA_24.json"
CANDS = OUT / "MANAT_CANDIDATES_24.json"
GUARDS = OUT / "MANAT_CANDIDATE_GUARDS_24.json"
RESID = OUT / "MANAT_CANDIDATE_RESIDUALS_24.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_MANAT_CANDIDATE_APPLICATION_25.md"
MATRIX = OUT / "MANAT_CANDIDATE_EXTRACTION_24_MATRIX.csv"
REPORT = OUT / "MANAT_CANDIDATE_EXTRACTION_MANAGER_REPORT_AR_24.html"
CAND_FIELDS = ["manat_candidate_id", "from_hukm_candidate_id", "linked_domain_candidates",
               "linked_sources", "linked_masala_segments", "candidate_manat_statement",
               "candidate_scope", "cause", "conditions", "preventers", "verdict", "evidence",
               "residuals", "final_manat_allowed", "tanzil_allowed", "final_hukm_allowed",
               "final_answer_allowed", "owner_ratification_required_for_final_manat"]
ALLOWED_VERDICTS = {"ACCEPT_AS_MANAT_CANDIDATE_ONLY", "DEFER_MANAT_CANDIDATE", "BLOCK_MANAT_CANDIDATE"}
FORBIDDEN = {"FINAL_MANAT", "FINAL_HUKM", "TANZIL", "FINAL_ANSWER"}
FROM_HC = {"HC1_SISTER_SHARE", "HC2_CLAIM_BURDEN_OF_PROOF",
           "HC3_POSSESSION_STAYS_PENDING_EXAMINATION", "HC4_COMPOSITE_LINK_NO_OUTCOME"}
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


def test_manat_gate_opened_and_produced():
    m = _m()
    assert m["ALLOW_MANAT_CANDIDATE"] == "YES"
    assert m["MANAT_CANDIDATE_OPENED"] == "YES"
    assert m["MANAT_CANDIDATES_PRODUCED"] in {"YES", "DEFER"}
    c = json.loads(CANDS.read_text(encoding="utf-8"))
    assert c["manat_candidate_opened"] == "YES"
    assert c["candidate_form_only"] == "YES"
    assert c["manat_candidate_count"] == 4


def test_four_manat_candidates_full_shape_and_lineage():
    c = json.loads(CANDS.read_text(encoding="utf-8"))
    cands = c["manat_candidates"]
    assert len(cands) == 4
    assert {x["from_hukm_candidate_id"] for x in cands} == FROM_HC
    for x in cands:
        for k in CAND_FIELDS:
            assert k in x and x[k] not in (None, "", []), (x["manat_candidate_id"], k)
        assert x["verdict"] in ALLOWED_VERDICTS
        assert x["verdict"] not in FORBIDDEN
        for g in ("final_manat_allowed", "tanzil_allowed", "final_hukm_allowed", "final_answer_allowed"):
            assert x[g] == "NO", (x["manat_candidate_id"], g)
        assert x["owner_ratification_required_for_final_manat"] == "YES"
        assert "مرشح مناط" in x["candidate_manat_statement"] or "مرشّح مناط" in x["candidate_manat_statement"]


def test_no_forbidden_verdict():
    c = json.loads(CANDS.read_text(encoding="utf-8"))
    for x in c["manat_candidates"]:
        assert x["verdict"] not in FORBIDDEN
    m = _m()
    assert m["ANY_VERDICT_FINAL_MANAT"] == "NO"
    assert m["ANY_VERDICT_FINAL_HUKM"] == "NO"
    assert m["ANY_VERDICT_TANZIL"] == "NO"
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(s["allowed_verdicts"]) == ALLOWED_VERDICTS
    assert set(s["forbidden_verdicts"]) == FORBIDDEN


def test_no_final_manat_hukm_tanzil_answer():
    m = _m()
    for k in ("FINAL_MANAT_PRODUCED", "FINAL_HUKM_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    for k in ("SISTER_SHARE_AMOUNT_DECIDED", "HOUSE_OWNERSHIP_ESTABLISHED",
              "FINAL_RESIDENCE_RIGHT_ESTABLISHED", "JUDICIAL_OBLIGATION_ISSUED",
              "SOURCE_ALONE_IS_MANAT", "POSSESSION_IS_FINAL_OWNERSHIP", "NEW_SOURCE_BORN",
              "AGENT_RATIFIED_SOURCE"):
        assert m[k] == "NO", k
    assert m["KEEP_COMPOSITE_REMAINS_ACTIVE"] == "YES"
    assert m["AUTHORITY_LEAK_PREVENTED"] == "YES"
    assert m["OWNER_RATIFICATION_REQUIRED_FOR_FINAL_MANAT"] == "YES"


def test_ten_fact_residuals_recorded():
    r = json.loads(RESID.read_text(encoding="utf-8"))
    assert r["opening_manat_candidate_blocked"] == "NO"
    assert r["final_manat_blocked"] == "YES"
    assert len(r["global_fact_residuals"]) == 10
    joined = " ".join(r["global_fact_residuals"])
    for probe in ("ولد", "ورثة", "الوارث", "تركة", "إذن", "يد", "الدعوى", "جواب", "البينة", "قرائن"):
        assert probe in joined, probe
    assert len(r["per_candidate_residuals"]) == 4
    assert r["unresolved_residuals_recorded"] == "YES"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("HUKM_CANDIDATE_IS_NOT_FINAL_HUKM", "HUKM_CANDIDATE_IS_NOT_FINAL_MANAT",
              "MANAT_CANDIDATE_IS_NOT_FINAL_MANAT", "MANAT_CANDIDATE_IS_NOT_TANZIL",
              "MANAT_CANDIDATE_IS_NOT_FINAL_ANSWER", "SOURCE_IS_NOT_MANAT", "SOURCE_IS_NOT_HUKM",
              "POSSESSION_IS_NOT_FINAL_OWNERSHIP", "KEEP_COMPOSITE_REMAINS_ACTIVE", "NO_NEW_SOURCE_ADDED",
              "AGENT_DID_NOT_RATIFY_SOURCE", "AGENT_DID_NOT_SELECT_SOURCE", "AUTHORITY_LEAK_PREVENTED",
              "EVIDENCE_IS_CITATION_STRING_ONLY", "NO_LIVE_EXTERNAL_LINKS", "NO_FINAL_MANAT",
              "NO_FINAL_HUKM", "NO_TANZIL", "NO_FINAL_ANSWER"):
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


def test_report_ar09_experience_and_statements():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    assert "ROUND_24_TESTS = passed" in t
    for mc in ("MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS", "MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN",
               "MC3_STANDING_HAND_STATE_BEFORE_EXPULSION", "MC4_COMPOSITE_MANAT_LINK_NO_OUTCOME"):
        assert mc in t, mc
    assert "جولة مرشّح مناط فقط" in t
    assert "POSSESSION ≠ FINAL_OWNERSHIP" in t
    for stmt in ("MANAT_CANDIDATE_OPENED = YES", "FINAL_MANAT_PRODUCED = NO", "FINAL_HUKM_PRODUCED = NO",
                 "TANZIL_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO",
                 "PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_25_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_MANAT_APPLICATION = YES | NO", "ALLOW_TANZIL = YES | NO",
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
