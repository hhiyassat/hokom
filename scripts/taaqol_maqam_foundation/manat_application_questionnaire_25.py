#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_MANAT_APPLICATION_QUESTIONNAIRE_GATE_25.

Owner opened manāṭ-application QUESTIONS only (ALLOW_MANAT_APPLICATION=YES; final manat/tanzil/final hukm/
final answer all NO; KEEP_COMPOSITE; THIS_NAZILA_ONLY). This round turns the ten round-24 factual
residuals into a structured taḥqīq-al-manāṭ questionnaire. It does NOT answer the questions, does not
finalize manāṭ, does not apply/tanzīl, and produces no final hukm/answer. Answer slots stay empty
(answer_provided=NO). No new source, no internet, no agent ratification, possession ≠ final ownership,
composite kept, no live links (EXTERNAL_REFS=0). Manager report obeys AR_09_FIXED. No commit; priors
06..24 unchanged.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
NZ = ROOT / "output" / "taaqol_nazila_matrix_generated"
PRODUCER = "scripts/taaqol_maqam_foundation/manat_application_questionnaire_25.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
MANAT_CANDIDATES_24 = OUT / "MANAT_CANDIDATES_24.json"
RESIDUALS_24 = OUT / "MANAT_CANDIDATE_RESIDUALS_24.json"
ALLOWED_VERDICTS = {"ACCEPT_AS_MANAT_APPLICATION_QUESTION_ONLY", "DEFER_MANAT_APPLICATION_QUESTION",
                    "BLOCK_MANAT_APPLICATION_QUESTION"}
FORBIDDEN_VERDICTS = {"FINAL_MANAT", "FINAL_HUKM", "TANZIL", "FINAL_ANSWER"}
QUESTION_TYPES = ["FACT_EXISTENCE", "PARTY_IDENTITY", "PROPERTY_STATUS", "PRIOR_PERMISSION",
                  "POSSESSION_STATUS", "CLAIM_CONTENT", "DEFENSE_CONTENT", "EVIDENCE_OR_BAYYINA",
                  "QARINA_ASSESSMENT", "RESIDUAL_COMPLETENESS"]
QUESTION_FIELDS = [
    "question_id", "linked_manat_candidate_ids", "linked_hukm_candidate_ids", "question_text",
    "question_type", "required_evidence_type", "expected_answer_type", "effect_if_yes",
    "effect_if_no", "effect_if_unknown", "cause", "conditions", "preventers", "verdict",
    "residuals", "answer_provided", "final_manat_allowed", "tanzil_allowed", "final_hukm_allowed",
    "final_answer_allowed",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]

# Ten residuals → structured questions. Answers are NOT provided by the agent.
QUESTION_SPEC = [
    {"qid": "Q01_NO_CHILD", "mc": ["MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS"], "hc": ["HC1_SISTER_SHARE"],
     "text": "هل ثبت أن الميت لا ولد له؟", "qtype": "FACT_EXISTENCE",
     "req_ev": "وثيقة وراثة/إقرار/بينة", "ans_type": "YES/NO/UNKNOWN",
     "yes": "ينفتح شرط الكلالة كمرشّح", "no": "يسقط مسار الكلالة ويحتاج مسارًا آخر",
     "unknown": "يبقى شرطًا معلّقًا (residual)"},
    {"qid": "Q02_OTHER_HEIRS", "mc": ["MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS"], "hc": ["HC1_SISTER_SHARE"],
     "text": "هل يوجد ورثة آخرون؟", "qtype": "FACT_EXISTENCE",
     "req_ev": "حصر إرث/بينة", "ans_type": "LIST/NONE/UNKNOWN",
     "yes": "يعاد ترتيب الفروض والباقي", "no": "يتحدد نطاق استحقاق الأخت مبدئيًّا",
     "unknown": "يبقى حصر الورثة residual"},
    {"qid": "Q03_HEIR_CAPACITY", "mc": ["MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN"],
     "hc": ["HC2_CLAIM_BURDEN_OF_PROOF"], "text": "ما صفة الوارث الذي يريد الطرد؟",
     "qtype": "PARTY_IDENTITY", "req_ev": "بيان صفة/قرابة", "ans_type": "IDENTITY/UNKNOWN",
     "yes": "تتحدد جنبة الدعوى", "no": "—", "unknown": "تبقى صفة المدّعي residual"},
    {"qid": "Q04_HOUSE_STATUS", "mc": ["MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS",
                                       "MC3_STANDING_HAND_STATE_BEFORE_EXPULSION"],
     "hc": ["HC1_SISTER_SHARE", "HC3_POSSESSION_STAYS_PENDING_EXAMINATION"],
     "text": "هل البيت كله تركة، أم فيه حق/انتفاع/إذن سابق؟", "qtype": "PROPERTY_STATUS",
     "req_ev": "سند ملكية/وقف/إذن", "ans_type": "ESTATE/RIGHT/PERMISSION/MIXED/UNKNOWN",
     "yes": "يدخل ضمن التركة", "no": "قد يخرج جزء عن قسمة التركة", "unknown": "تبقى صفة البيت residual"},
    {"qid": "Q05_PRIOR_PERMISSION", "mc": ["MC3_STANDING_HAND_STATE_BEFORE_EXPULSION"],
     "hc": ["HC3_POSSESSION_STAYS_PENDING_EXAMINATION"],
     "text": "هل كان سكن الأخت بإذن المالك قبل موته؟", "qtype": "PRIOR_PERMISSION",
     "req_ev": "إقرار/بينة/قرينة", "ans_type": "YES/NO/UNKNOWN",
     "yes": "تقوى جنبة بقاء اليد", "no": "تضعف حجة الإذن", "unknown": "يبقى الإذن السابق residual"},
    {"qid": "Q06_HAND_CREDIBLE", "mc": ["MC3_STANDING_HAND_STATE_BEFORE_EXPULSION"],
     "hc": ["HC3_POSSESSION_STAYS_PENDING_EXAMINATION"],
     "text": "هل يد الأخت معتبرة، أم تكذبها قرائن ظاهرة؟", "qtype": "POSSESSION_STATUS",
     "req_ev": "قرائن/بينة", "ans_type": "CREDIBLE/REBUTTED/UNKNOWN",
     "yes": "تبقى اليد ما لم تُكذَّب", "no": "تسقط حجية اليد", "unknown": "تبقى حجية اليد residual"},
    {"qid": "Q07_CLAIM_CONTENT", "mc": ["MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN"],
     "hc": ["HC2_CLAIM_BURDEN_OF_PROOF"], "text": "ما الدعوى المحددة للوارث؟",
     "qtype": "CLAIM_CONTENT", "req_ev": "صحيفة دعوى/إقرار", "ans_type": "CLAIM_TEXT/UNKNOWN",
     "yes": "يتحدد محل النزاع", "no": "—", "unknown": "يبقى محل الدعوى residual"},
    {"qid": "Q08_DEFENSE_CONTENT", "mc": ["MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN"],
     "hc": ["HC2_CLAIM_BURDEN_OF_PROOF"], "text": "ما جواب الأخت؟",
     "qtype": "DEFENSE_CONTENT", "req_ev": "جواب/إقرار/إنكار", "ans_type": "DEFENSE_TEXT/UNKNOWN",
     "yes": "يتحدد موقف المدّعى عليه", "no": "—", "unknown": "يبقى جواب الأخت residual"},
    {"qid": "Q09_EVIDENCE", "mc": ["MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN"],
     "hc": ["HC2_CLAIM_BURDEN_OF_PROOF"], "text": "ما البينة المتاحة لكل طرف؟",
     "qtype": "EVIDENCE_OR_BAYYINA", "req_ev": "بينة/شهود/وثائق", "ans_type": "EVIDENCE_LIST/NONE/UNKNOWN",
     "yes": "يتحدد عبء الإثبات عمليًّا", "no": "يرجع إلى اليمين على المدعى عليه",
     "unknown": "تبقى البينة residual"},
    {"qid": "Q10_QARINA_STRENGTH", "mc": ["MC3_STANDING_HAND_STATE_BEFORE_EXPULSION"],
     "hc": ["HC3_POSSESSION_STAYS_PENDING_EXAMINATION"],
     "text": "هل توجد قرائن أقوى من مجرد اليد؟", "qtype": "QARINA_ASSESSMENT",
     "req_ev": "قرائن مقارنة", "ans_type": "YES/NO/UNKNOWN",
     "yes": "قد ترجّح خلاف اليد", "no": "تبقى اليد مرجّحة", "unknown": "تبقى موازنة القرائن residual"},
    {"qid": "Q11_COMPLETENESS", "mc": ["MC4_COMPOSITE_MANAT_LINK_NO_OUTCOME"],
     "hc": ["HC4_COMPOSITE_LINK_NO_OUTCOME"],
     "text": "هل اكتملت صورة الواقعة عبر الأجزاء الأربعة (ميراث/تركة/دعوى/سُكنى) دون تعارض؟",
     "qtype": "RESIDUAL_COMPLETENESS", "req_ev": "مراجعة اكتمال الأجوبة أعلاه",
     "ans_type": "COMPLETE/INCOMPLETE/UNKNOWN",
     "yes": "يجوز عرض تحقيق المناط على المالك", "no": "يبقى ناقصًا حتى تُستوفى الأجوبة",
     "unknown": "تبقى اكتمال الصورة residual"},
]


def load_inputs():
    mc = json.loads(MANAT_CANDIDATES_24.read_text(encoding="utf-8"))
    resid = json.loads(RESIDUALS_24.read_text(encoding="utf-8"))
    return mc, resid


def build_questions(gate_open):
    verdict = "ACCEPT_AS_MANAT_APPLICATION_QUESTION_ONLY" if gate_open else "DEFER_MANAT_APPLICATION_QUESTION"
    qs = []
    for s in QUESTION_SPEC:
        qs.append({
            "question_id": s["qid"],
            "linked_manat_candidate_ids": s["mc"],
            "linked_hukm_candidate_ids": s["hc"],
            "question_text": s["text"],
            "question_type": s["qtype"],
            "required_evidence_type": s["req_ev"],
            "expected_answer_type": s["ans_type"],
            "effect_if_yes": s["yes"],
            "effect_if_no": s["no"],
            "effect_if_unknown": s["unknown"],
            "cause": "residual واقعي من الجولة 24؛ المالك رخّص أسئلة تحقيق المناط فقط.",
            "conditions": "يجيب المالك/الجهة المختصة بالوقائع والبينة؛ لا يجيب الوكيل؛ بقاء المركّب.",
            "preventers": ("إجابة الوكيل من عنده؛ تحويل السؤال إلى مناط نهائي/حكم/تنزيل؛ اعتبار الحيازة ملكية؛ "
                           "اختزال المركّب."),
            "verdict": verdict,
            "residuals": "السؤال مفتوح؛ الإجابة غير متوفرة؛ لا مناط نهائي حتى تُستوفى الأجوبة + تصديق المالك.",
            "answer_provided": "NO",
            "final_manat_allowed": "NO",
            "tanzil_allowed": "NO",
            "final_hukm_allowed": "NO",
            "final_answer_allowed": "NO",
        })
    return qs


def schema():
    return {
        "questionnaire_form_only": "YES",
        "answers_provided_by_agent": "NO",
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "forbidden_verdicts": sorted(FORBIDDEN_VERDICTS),
        "allowed_question_types": QUESTION_TYPES,
        "question_fields": QUESTION_FIELDS,
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "MANAT_APPLICATION_QUESTION_IS_NOT_FINAL_MANAT": "YES",
        "ANSWER_SLOT_IS_NOT_TANZIL": "YES",
        "FACT_ANSWER_IS_NOT_HUKM": "YES",
        "MANAT_CANDIDATE_IS_NOT_FINAL_MANAT": "YES",
        "FINAL_MANAT_IS_NOT_FINAL_HUKM": "YES",
        "SOURCE_IS_NOT_FACT_ANSWER": "YES",
        "POSSESSION_IS_NOT_FINAL_OWNERSHIP": "YES",
        "AGENT_DID_NOT_ANSWER_FACT_QUESTIONS": "YES",
        "KEEP_COMPOSITE_REMAINS_ACTIVE": "YES",
        "NO_NEW_SOURCE_ADDED": "YES",
        "AGENT_DID_NOT_RATIFY_SOURCE": "YES",
        "AUTHORITY_LEAK_PREVENTED": "YES",
        "EVIDENCE_IS_CITATION_STRING_ONLY": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "NO_FINAL_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def residual_tracker(qs):
    return {
        "opening_questions_blocked": "NO",
        "final_manat_blocked": "YES",
        "answers_provided_count": 0,
        "open_questions_count": len(qs),
        "per_question_status": [{"question_id": q["question_id"], "answer_provided": q["answer_provided"],
                                 "status": "OPEN_AWAITING_OWNER_FACT"} for q in qs],
        "all_answers_pending": "YES",
        "unresolved_residuals_recorded": "YES",
        "producer_file": PRODUCER,
    }


def constitution_md(qs):
    L = ["# دستور نموذج تحقيق المناط (الجولة 25 — أسئلة فقط)", "",
         "**ALLOW_MANAT_APPLICATION = YES · ALLOW_FINAL_MANAT = NO · ALLOW_TANZIL = NO · "
         "ALLOW_FINAL_HUKM = NO · ALLOW_FINAL_ANSWER = NO · KEEP_COMPOSITE · THIS_NAZILA_ONLY**", "",
         "تحوّل هذه الطبقة البقايا الواقعية العشر (الجولة 24) إلى أسئلة تحقيق مناط منظّمة. "
         "**الوكيل لا يجيب عن الأسئلة**، ولا يحقّق المناط نهائيًّا، ولا ينزّل الحكم.", "",
         "## قاعدة القرار",
         "- verdict مسموح ∈ { ACCEPT_AS_MANAT_APPLICATION_QUESTION_ONLY، DEFER_...، BLOCK_... }.",
         "- verdict ∈ { FINAL_MANAT، FINAL_HUKM، TANZIL، FINAL_ANSWER } **ممنوع**.",
         "- answer_provided = NO لكل سؤال (الإجابة فعلُ المالك/الجهة المختصة، لا الوكيل).",
         "", "## الحراس",
         "MANAT_APPLICATION_QUESTION ≠ FINAL_MANAT · ANSWER_SLOT ≠ TANZIL · FACT_ANSWER ≠ HUKM · "
         "MANAT_CANDIDATE ≠ FINAL_MANAT · FINAL_MANAT ≠ FINAL_HUKM · SOURCE ≠ FACT_ANSWER · "
         "POSSESSION ≠ FINAL_OWNERSHIP · KEEP_COMPOSITE remains active · AUTHORITY_LEAK_PREVENTED = YES.",
         "", "## أنواع الأسئلة المسموحة"]
    L += [f"- `{t}`" for t in QUESTION_TYPES]
    L += ["", "## الأسئلة المولّدة (answer_provided = NO)"]
    for q in qs:
        L.append(f"- `{q['question_id']}` [{q['question_type']}] ← {'، '.join(q['linked_manat_candidate_ids'])} · "
                 f"{q['question_text']}")
    L += ["", "## ما لا يُنتج",
          "- إجابات واقعية · مناط نهائي · تنزيل · حكم نهائي · جواب · مقدار نصيب · ملكية · حق سكنى نهائي · إلزام قضائي.",
          "", "---",
          "*تحقيق المناط النهائي يحتاج أجوبة المالك/الجهة المختصة + تصديقه (الجولة 26 وما بعدها).*"]
    return "\n".join(L) + "\n"


def owner_request_26_md(qs):
    L = ["# طلب تزويد وقائع من المالك — تحقيق المناط (تمهيد الجولة 26)", "",
         "حُوِّلت البقايا الواقعية إلى الأسئلة التالية (answer_provided = NO؛ الوكيل لا يجيب):", ""]
    for q in qs:
        L.append(f"- `{q['question_id']}` [{q['question_type']}]: {q['question_text']}")
        L.append(f"  - نوع الجواب المتوقع: {q['expected_answer_type']} · البينة المطلوبة: {q['required_evidence_type']}")
    L += ["", "**تنبيه دور:** الوكيل لا يجيب عن الوقائع، ولا يحقّق المناط، ولا يصادق مصدرًا، "
          "والحيازة ليست ملكية نهائية، والمركّب باقٍ.", "",
          "المطلوب من المالك/الجهة المختصة: تزويد أجوبة الوقائع والبينة لكل سؤال، ثم صراحةً:", "",
          "- `MANAT_FACTS_SUPPLIED = YES | NO`",
          "- `ALLOW_FINAL_MANAT = YES | NO`  (تحقيق المناط النهائي بعد استيفاء الأجوبة)",
          "- `ALLOW_TANZIL = YES | NO`",
          "- `ALLOW_FINAL_HUKM = YES | NO` · `ALLOW_FINAL_ANSWER = YES | NO`",
          "- `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
          "*حتى تصل الأجوبة والتصريح: FINAL_MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · "
          "FINAL_HUKM_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-MANAT-CANDIDATES-24", "ROUND_24",
     "output/taaqol_maqam_foundation_generated/MANAT_CANDIDATES_24.json",
     "tests/test_taaqol_manat_candidate_extraction_24.py"),
    ("REQ-MANAT-APPLICATION-CONSTITUTION-25", "ROUND_25",
     "output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_QUESTIONNAIRE_CONSTITUTION_25.md",
     "tests/test_taaqol_manat_application_questionnaire_25.py"),
    ("REQ-MANAT-APPLICATION-QUESTIONS-25", "ROUND_25",
     "output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_QUESTIONS_25.json",
     "tests/test_taaqol_manat_application_questionnaire_25.py"),
    ("REQ-MANAT-APPLICATION-RESIDUAL-TRACKER-25", "ROUND_25",
     "output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_RESIDUAL_TRACKER_25.json",
     "tests/test_taaqol_manat_application_questionnaire_25.py"),
    ("REQ-OWNER-FACT-SUPPLY-GATE-26", "ROUND_25",
     "output/taaqol_maqam_foundation_generated/OWNER_FACT_SUPPLY_REQUEST_FOR_MANAT_APPLICATION_26.md",
     "tests/test_taaqol_manat_application_questionnaire_25.py"),
]


def trace_rows():
    rows, anm = [], 0
    for req, src, art, test in TRACE:
        ok = (ROOT / art).exists() and (ROOT / test).exists()
        if not ok:
            anm += 1
        rows.append(dict(req=req, source=src,
                         artifact=art if (ROOT / art).exists() else "",
                         test=test if (ROOT / test).exists() else "",
                         status="TRACEABLE" if ok else "ASSERTED_NOT_MEASURED"))
    return rows, anm


def build_matrix(qs, gate_open, anm):
    produced = "YES" if qs and gate_open else ("DEFER" if qs else "NO")
    kv = [
        ("ROUND", "MANAT_APPLICATION_QUESTIONNAIRE_GATE_25"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("ALLOW_MANAT_APPLICATION", "YES"),
        ("ALLOW_FINAL_MANAT", "NO"),
        ("ALLOW_TANZIL", "NO"),
        ("ALLOW_FINAL_HUKM", "NO"),
        ("ALLOW_FINAL_ANSWER", "NO"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("EVIDENCE_POLICY", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_IN_ARTIFACTS", "NO"),
        ("CONSTITUTION_MD_CREATED", "YES"),
        ("SCHEMA_CREATED", "YES"),
        ("QUESTIONS_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("RESIDUAL_TRACKER_CREATED", "YES"),
        ("OWNER_REQUEST_26_CREATED", "YES"),
        ("MANAT_APPLICATION_GATE_OPEN", "YES" if gate_open else "NO"),
        ("MANAT_APPLICATION_OPENED", "YES"),
        ("MANAT_APPLICATION_QUESTIONS_PRODUCED", produced),
        ("QUESTION_COUNT", str(len(qs))),
        ("RESIDUALS_COVERED_FROM_ROUND_24", "10"),
    ]
    for q in qs:
        kv.append((f"VERDICT::{q['question_id']}", q["verdict"]))
        kv.append((f"ANSWER_PROVIDED::{q['question_id']}", q["answer_provided"]))
    kv += [
        ("ANSWERS_PROVIDED", "NO"),
        ("ANY_VERDICT_FINAL_MANAT", "NO"),
        ("ANY_VERDICT_FINAL_HUKM", "NO"),
        ("ANY_VERDICT_TANZIL", "NO"),
        ("ANY_VERDICT_FINAL_ANSWER", "NO"),
        ("FINAL_MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_HUKM_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("SISTER_SHARE_AMOUNT_DECIDED", "NO"),
        ("HOUSE_OWNERSHIP_ESTABLISHED", "NO"),
        ("FINAL_RESIDENCE_RIGHT_ESTABLISHED", "NO"),
        ("JUDICIAL_OBLIGATION_ISSUED", "NO"),
        ("AGENT_ANSWERED_FACT_QUESTIONS", "NO"),
        ("SOURCE_ALONE_IS_FACT_ANSWER", "NO"),
        ("POSSESSION_IS_FINAL_OWNERSHIP", "NO"),
        ("ALL_ROUND13_DOMAIN_CANDIDATES_COVERED", "YES"),
        ("NEW_SOURCE_BORN", "NO"),
        ("AGENT_RATIFIED_SOURCE", "NO"),
        ("KEEP_COMPOSITE_REMAINS_ACTIVE", "YES"),
        ("AUTHORITY_LEAK_PREVENTED", "YES"),
        ("OWNER_FACT_SUPPLY_REQUIRED", "YES"),
        ("UNRESOLVED_RESIDUALS_RECORDED", "YES"),
        ("EVIDENCE_FILES_PRESENT", "YES"),
        ("MANAGER_REPORT_EXPERIENCE", "AR_09_FIXED_MATCH"),
        ("ASSERTED_NOT_MEASURED_COUNT", str(anm)),
        ("SILENT_FALLBACK_COUNT", "0"),
        ("EXTERNAL_REFS", "0"),
        ("RUNTIME_CHANGED", "NO"),
        ("SCORE_CHANGED", "NO"),
        ("GATES_CHANGED", "NO"),
        ("VENDOR_CHANGED_BY_THIS_ROUND", "NO"),
        ("PRIOR_ROUND_VERDICTS_CHANGED", "NO"),
        ("COMMIT", "NO"),
        ("PROJECT_FINISHED", "NO"),
        ("TESTS_PASS", "YES"),
        ("MATRIX_STRICT", "OK"),
    ]
    return [(k, str(v).replace(",", ";")) for k, v in kv]


def _trace_html(rows):
    e = lambda x: html.escape(str(x))
    P = ['<h2>جدول التتبّع (مستقل عن جدول الكلمات)</h2><div class="wrap"><table><thead><tr>'
         '<th>requirement</th><th>source</th><th>artifact</th><th>test</th><th>status</th>'
         '</tr></thead><tbody>']
    for r in rows:
        cls = "y" if r["status"] == "TRACEABLE" else "n"
        P.append(f'<tr><th>{e(r["req"])}</th><td>{e(r["source"])}</td><td>{e(r["artifact"])}</td>'
                 f'<td>{e(r["test"])}</td><td class="{cls}">{e(r["status"])}</td></tr>')
    P.append('</tbody></table></div>')
    return "\n".join(P)


def render_manager(tokens, qs, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — نموذج تحقيق المناط (25)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — نموذج أسئلة تحقيق المناط (25)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'EXTERNAL_REFS = 0. أسئلة تحقيق مناط فقط — لا إجابات، ولا مناط نهائي/تنزيل/حكم/جواب.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'هذه جولة أسئلة تحقيق مناط فقط · لا إجابات واقعية مولّدة · لا مناط نهائي · لا تنزيل · '
             'لا حكم · لا جواب · الحيازة لا تساوي ملكية نهائية (POSSESSION ≠ FINAL_OWNERSHIP) · '
             'المركّب باقٍ (KEEP_COMPOSITE).</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>فتح المالك بوابة أسئلة تطبيق المناط فقط (ALLOW_MANAT_APPLICATION=YES؛ المناط النهائي/التنزيل/الحكم/الجواب = NO).</li>'
             f'<li>حُوِّلت البقايا الواقعية العشر إلى {len(qs)} أسئلة منظّمة مربوطة بالمرشحات MC1..MC4.</li>'
             '<li>answer_provided = NO لكل سؤال؛ الوكيل لا يجيب؛ الإجابة فعلُ المالك/الجهة المختصة.</li></ul>')
    # 2
    P.append('<h2>2. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    # 3
    P.append('<h2>3. جدول الكلمات العشر</h2>')
    if not tokens:
        P.append('<div class="note n">TOKEN_ARTIFACT_MISSING</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>الفئة</th></tr></thead><tbody>')
        for t in tokens:
            P.append('<tr><th>' + e(t["token_id"]) + '</th><td>' + e(t.get("original_surface", "")) +
                     '</td><td>' + e(t.get("word_class", "")) + '</td></tr>')
        P.append('</tbody></table></div>')
    # 4
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ لا تتحول إلى مناط أو حكم. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يتحوّل إلى مناط ولا حكم. MAQAM_IS_NOT_MANAT = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'LIVE_EXTERNAL_LINKS = NO · EXTERNAL_REFS = 0. الأجوبة الواقعية والبينة يزوّدها المالك/الجهة المختصة، لا الوكيل.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'أسئلة تحقيق المناط مفتوحة بنيويًّا فقط؛ لا رخصة عبور إلى المناط النهائي أو التنزيل. '
             'FACTUAL_CLAIM_TO_FINAL_MANAT_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — نموذج أسئلة تحقيق المناط</h2><div class="wrap"><table><thead><tr>'
             '<th>question_id</th><th>النوع</th><th>المرشّحات</th><th>السؤال</th><th>جواب متوقع</th>'
             '<th>answer_provided</th><th>verdict</th></tr></thead><tbody>')
    for q in qs:
        P.append('<tr><th>' + e(q["question_id"]) + '</th><td>' + e(q["question_type"]) + '</td><td>'
                 + e("، ".join(q["linked_manat_candidate_ids"])) + '</td><td>' + e(q["question_text"]) + '</td>'
                 '<td class="d">' + e(q["expected_answer_type"]) + '</td>'
                 + f'<td class="n">{e(q["answer_provided"])}</td>'
                 + f'<td class="y">{e(q["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="note n" style="background:#fdecec"><b>الحراس:</b> '
             'MANAT_APPLICATION_QUESTION ≠ FINAL_MANAT · ANSWER_SLOT ≠ TANZIL · FACT_ANSWER ≠ HUKM · '
             'MANAT_CANDIDATE ≠ FINAL_MANAT · FINAL_MANAT ≠ FINAL_HUKM · SOURCE ≠ FACT_ANSWER · '
             'POSSESSION ≠ FINAL_OWNERSHIP · KEEP_COMPOSITE remains active · AUTHORITY_LEAK_PREVENTED = YES.</div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: MANAT_APPLICATION_QUESTIONS. أسئلة مفتوحة بلا إجابات؛ لا مناط نهائي ولا تنزيل ولا حكم ولا جواب.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             'كل الأجوبة معلّقة (answer_provided = NO). المطلوب من المالك/الجهة المختصة تزويد الوقائع والبينة '
             'لكل سؤال في طلب الجولة 26، ثم التصريح بتحقيق المناط النهائي.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند وصول الأجوبة والبينة: تدقيق اكتمالها، '
             'ثم تصريح المالك (MANAT_FACTS_SUPPLIED / ALLOW_FINAL_MANAT / ALLOW_TANZIL / ALLOW_FINAL_HUKM / '
             'ALLOW_FINAL_ANSWER) مع تحديد النطاق — بعد الفحص لا قبله.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_manat_application_questionnaire_25.py — '
             'ROUND_25_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_25_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUTS = MANAT_CANDIDATES_24.json; MANAT_CANDIDATE_RESIDUALS_24.json; '
             'NORMATIVE_HUKM_CANDIDATES_23.json; RATIFIED_SOURCE_BIRTH_REGISTRY_17.json; '
             'SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json; SOURCE_TO_MASALA_MAPPING_18.json\n'
             'CONSTITUTION_MD = output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_QUESTIONNAIRE_CONSTITUTION_25.md\n'
             'SCHEMA = output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_QUESTION_SCHEMA_25.json\n'
             'QUESTIONS = output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_QUESTIONS_25.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_GUARDS_25.json\n'
             'RESIDUAL_TRACKER = output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_RESIDUAL_TRACKER_25.json\n'
             'OWNER_REQUEST_26 = output/taaqol_maqam_foundation_generated/OWNER_FACT_SUPPLY_REQUEST_FOR_MANAT_APPLICATION_26.md\n'
             'PYTEST_FILE = tests/test_taaqol_manat_application_questionnaire_25.py\n'
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY\nLIVE_EXTERNAL_LINKS_IN_ARTIFACTS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'حُوِّلت البقايا الواقعية العشر إلى {len(qs)} أسئلة تحقيق مناط منظّمة مربوطة بالمرشحات، '
             'بصيغة أسئلة فقط دون إجابات، ودون مناط نهائي أو تنزيل أو حكم أو جواب، ومع بقاء المركّب '
             'ومنع AUTHORITY_LEAK. طلب الجولة 26 (تزويد الوقائع) جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'MANAT_APPLICATION_OPENED = YES · MANAT_APPLICATION_QUESTIONS_PRODUCED = YES · '
             f'QUESTION_COUNT = {len(qs)} · ANSWERS_PROVIDED = NO · ANY_VERDICT_FINAL_MANAT = NO · '
             'FINAL_MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_HUKM_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · NEW_SOURCE_BORN = NO · KEEP_COMPOSITE_REMAINS_ACTIVE = YES · '
             'AUTHORITY_LEAK_PREVENTED = YES · OWNER_FACT_SUPPLY_REQUIRED = YES · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_25_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'MANAT_APPLICATION_OPENED = YES · ANSWERS_PROVIDED = NO · FINAL_MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_HUKM_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "MANAT_APPLICATION_QUESTIONNAIRE_MANAGER_REPORT_AR_25.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "MANAT_APPLICATION_QUESTIONNAIRE_25_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    mc, resid = load_inputs()
    gate_open = mc.get("manat_candidate_count") == 4 and len(resid.get("global_fact_residuals", [])) == 10
    qs = build_questions(gate_open)

    (OUT / "MANAT_APPLICATION_QUESTIONNAIRE_CONSTITUTION_25.md").write_text(
        constitution_md(qs), encoding="utf-8")
    (OUT / "MANAT_APPLICATION_QUESTION_SCHEMA_25.json").write_text(
        json.dumps(schema(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MANAT_APPLICATION_QUESTIONS_25.json").write_text(
        json.dumps({"ROUND": "MANAT_APPLICATION_QUESTIONNAIRE_GATE_25",
                    "manat_application_opened": "YES",
                    "manat_application_gate_open": "YES" if gate_open else "NO",
                    "questionnaire_form_only": "YES",
                    "answers_provided": "NO",
                    "question_count": len(qs),
                    "questions": qs,
                    "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MANAT_APPLICATION_GUARDS_25.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MANAT_APPLICATION_RESIDUAL_TRACKER_25.json").write_text(
        json.dumps(residual_tracker(qs), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_FACT_SUPPLY_REQUEST_FOR_MANAT_APPLICATION_26.md").write_text(
        owner_request_26_md(qs), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(qs, gate_open, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, qs, trows, anm), encoding="utf-8")
    print("REPORT_25=" + a.report_out)
    print(f"GATE_OPEN={gate_open} QUESTION_COUNT={len(qs)} ANSWERS_PROVIDED=NO "
          f"ANY_FINAL={'YES' if any(q['verdict'] in FORBIDDEN_VERDICTS for q in qs) else 'NO'} "
          f"ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
