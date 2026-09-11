#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_MANAT_APPLICATION_QUESTIONNAIRE_GATE_25 — guard test.

Turns the ten round-24 factual residuals into a taḥqīq-al-manāṭ questionnaire (questions only). The agent
does NOT answer, does not finalize manāṭ, does not tanzīl, and produces no final hukm/answer. answer_
provided=NO for every question. No new source, no agent ratification, possession ≠ final ownership,
composite kept, no live links, EXTERNAL_REFS=0. Manager report obeys the AR_09_FIXED experience.
Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
CONST = OUT / "MANAT_APPLICATION_QUESTIONNAIRE_CONSTITUTION_25.md"
SCHEMA = OUT / "MANAT_APPLICATION_QUESTION_SCHEMA_25.json"
QUESTIONS = OUT / "MANAT_APPLICATION_QUESTIONS_25.json"
GUARDS = OUT / "MANAT_APPLICATION_GUARDS_25.json"
TRACKER = OUT / "MANAT_APPLICATION_RESIDUAL_TRACKER_25.json"
OWNER_REQ = OUT / "OWNER_FACT_SUPPLY_REQUEST_FOR_MANAT_APPLICATION_26.md"
MATRIX = OUT / "MANAT_APPLICATION_QUESTIONNAIRE_25_MATRIX.csv"
REPORT = OUT / "MANAT_APPLICATION_QUESTIONNAIRE_MANAGER_REPORT_AR_25.html"
Q_FIELDS = ["question_id", "linked_manat_candidate_ids", "linked_hukm_candidate_ids", "question_text",
            "question_type", "required_evidence_type", "expected_answer_type", "effect_if_yes",
            "effect_if_no", "effect_if_unknown", "cause", "conditions", "preventers", "verdict",
            "residuals", "answer_provided", "final_manat_allowed", "tanzil_allowed",
            "final_hukm_allowed", "final_answer_allowed"]
ALLOWED_VERDICTS = {"ACCEPT_AS_MANAT_APPLICATION_QUESTION_ONLY", "DEFER_MANAT_APPLICATION_QUESTION",
                    "BLOCK_MANAT_APPLICATION_QUESTION"}
FORBIDDEN = {"FINAL_MANAT", "FINAL_HUKM", "TANZIL", "FINAL_ANSWER"}
QUESTION_TYPES = {"FACT_EXISTENCE", "PARTY_IDENTITY", "PROPERTY_STATUS", "PRIOR_PERMISSION",
                  "POSSESSION_STATUS", "CLAIM_CONTENT", "DEFENSE_CONTENT", "EVIDENCE_OR_BAYYINA",
                  "QARINA_ASSESSMENT", "RESIDUAL_COMPLETENESS"}
MC_IDS = {"MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS", "MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN",
          "MC3_STANDING_HAND_STATE_BEFORE_EXPULSION", "MC4_COMPOSITE_MANAT_LINK_NO_OUTCOME"}
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
    for p in (CONST, SCHEMA, QUESTIONS, GUARDS, TRACKER, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    for p in (SCHEMA, QUESTIONS, GUARDS, TRACKER):
        json.loads(p.read_text(encoding="utf-8"))


def test_application_opened_and_produced():
    m = _m()
    assert m["ALLOW_MANAT_APPLICATION"] == "YES"
    assert m["MANAT_APPLICATION_OPENED"] == "YES"
    assert m["MANAT_APPLICATION_QUESTIONS_PRODUCED"] in {"YES", "DEFER"}
    q = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    assert q["manat_application_opened"] == "YES"
    assert q["questionnaire_form_only"] == "YES"
    assert q["answers_provided"] == "NO"


def test_question_count_at_least_ten():
    q = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    qs = q["questions"]
    assert len(qs) >= 10
    assert int(_m()["QUESTION_COUNT"]) >= 10


def test_each_question_full_shape_and_unanswered():
    q = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    for x in q["questions"]:
        for k in Q_FIELDS:
            assert k in x and x[k] not in (None, "", []), (x["question_id"], k)
        assert x["question_type"] in QUESTION_TYPES
        assert x["verdict"] in ALLOWED_VERDICTS
        assert x["verdict"] not in FORBIDDEN
        assert x["answer_provided"] == "NO"
        for g in ("final_manat_allowed", "tanzil_allowed", "final_hukm_allowed", "final_answer_allowed"):
            assert x[g] == "NO", (x["question_id"], g)
        assert set(x["linked_manat_candidate_ids"]) <= MC_IDS


def test_candidate_linkage_coverage():
    q = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    linked = set()
    for x in q["questions"]:
        linked.update(x["linked_manat_candidate_ids"])
    assert MC_IDS <= linked, "each MC1..MC4 must be linked by at least one question"


def test_no_answers_no_final():
    m = _m()
    assert m["ANSWERS_PROVIDED"] == "NO"
    assert m["AGENT_ANSWERED_FACT_QUESTIONS"] == "NO"
    for k in ("FINAL_MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_HUKM_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    for k in ("SISTER_SHARE_AMOUNT_DECIDED", "HOUSE_OWNERSHIP_ESTABLISHED",
              "FINAL_RESIDENCE_RIGHT_ESTABLISHED", "JUDICIAL_OBLIGATION_ISSUED",
              "POSSESSION_IS_FINAL_OWNERSHIP", "NEW_SOURCE_BORN", "AGENT_RATIFIED_SOURCE"):
        assert m[k] == "NO", k
    assert m["KEEP_COMPOSITE_REMAINS_ACTIVE"] == "YES"
    assert m["AUTHORITY_LEAK_PREVENTED"] == "YES"
    assert m["OWNER_FACT_SUPPLY_REQUIRED"] == "YES"


def test_no_forbidden_verdict():
    q = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    for x in q["questions"]:
        assert x["verdict"] not in FORBIDDEN
    m = _m()
    assert m["ANY_VERDICT_FINAL_MANAT"] == "NO"
    assert m["ANY_VERDICT_FINAL_HUKM"] == "NO"
    assert m["ANY_VERDICT_TANZIL"] == "NO"
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(s["allowed_verdicts"]) == ALLOWED_VERDICTS
    assert set(s["forbidden_verdicts"]) == FORBIDDEN
    assert s["answers_provided_by_agent"] == "NO"


def test_tracker_all_pending():
    t = json.loads(TRACKER.read_text(encoding="utf-8"))
    assert t["opening_questions_blocked"] == "NO"
    assert t["final_manat_blocked"] == "YES"
    assert t["answers_provided_count"] == 0
    assert t["all_answers_pending"] == "YES"
    assert len(t["per_question_status"]) >= 10
    for p in t["per_question_status"]:
        assert p["answer_provided"] == "NO"


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("MANAT_APPLICATION_QUESTION_IS_NOT_FINAL_MANAT", "ANSWER_SLOT_IS_NOT_TANZIL",
              "FACT_ANSWER_IS_NOT_HUKM", "MANAT_CANDIDATE_IS_NOT_FINAL_MANAT",
              "FINAL_MANAT_IS_NOT_FINAL_HUKM", "SOURCE_IS_NOT_FACT_ANSWER",
              "POSSESSION_IS_NOT_FINAL_OWNERSHIP", "AGENT_DID_NOT_ANSWER_FACT_QUESTIONS",
              "KEEP_COMPOSITE_REMAINS_ACTIVE", "NO_NEW_SOURCE_ADDED", "AGENT_DID_NOT_RATIFY_SOURCE",
              "AUTHORITY_LEAK_PREVENTED", "EVIDENCE_IS_CITATION_STRING_ONLY", "NO_LIVE_EXTERNAL_LINKS",
              "NO_FINAL_MANAT", "NO_TANZIL", "NO_FINAL_HUKM", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_no_live_links_external_refs_zero():
    blob = (QUESTIONS.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8")
            + TRACKER.read_text(encoding="utf-8") + CONST.read_text(encoding="utf-8"))
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
    assert "ROUND_25_TESTS = passed" in t
    for qid in ("Q01_NO_CHILD", "Q05_PRIOR_PERMISSION", "Q10_QARINA_STRENGTH", "Q11_COMPLETENESS"):
        assert qid in t, qid
    assert "جولة أسئلة تحقيق مناط فقط" in t
    assert "لا إجابات واقعية مولّدة" in t
    assert "POSSESSION ≠ FINAL_OWNERSHIP" in t
    for stmt in ("MANAT_APPLICATION_OPENED = YES", "ANSWERS_PROVIDED = NO", "FINAL_MANAT_PRODUCED = NO",
                 "TANZIL_PRODUCED = NO", "FINAL_HUKM_PRODUCED = NO", "FINAL_ANSWER_PRODUCED = NO"):
        assert stmt in t, stmt


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_26_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("MANAT_FACTS_SUPPLIED = YES | NO", "ALLOW_FINAL_MANAT = YES | NO",
              "ALLOW_TANZIL = YES | NO", "ALLOW_FINAL_HUKM = YES | NO",
              "ALLOW_FINAL_ANSWER = YES | NO", "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE"):
        assert q in t, q


def test_no_typos_no_noncanonical_no_commit():
    t = REPORT.read_text(encoding="utf-8")
    blob = t + MATRIX.read_text(encoding="utf-8") + QUESTIONS.read_text(encoding="utf-8")
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
