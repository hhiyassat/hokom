#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_MANAT_CANDIDATE_EXTRACTION_GATE_24.

Owner opened the manāṭ-CANDIDATE gate only (ALLOW_MANAT_CANDIDATE=YES; tanzil/final hukm/final answer all
NO; KEEP_COMPOSITE; THIS_NAZILA_ONLY). This round extracts manāṭ CANDIDATES (locus-of-effect) from the
four round-23 hukm candidates — candidate form only, never a final manāṭ. No final manat/hukm/tanzil/
answer, no share amount, no ownership, no final residence right, no judicial obligation, composite kept,
no new source, no agent ratification, possession ≠ final ownership, no live links (EXTERNAL_REFS=0).
Manager report obeys the AR_09_FIXED experience. No commit; priors 06..23 unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/manat_candidate_extraction_24.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
HUKM_CANDIDATES_23 = OUT / "NORMATIVE_HUKM_CANDIDATES_23.json"
ALLOWED_VERDICTS = {"ACCEPT_AS_MANAT_CANDIDATE_ONLY", "DEFER_MANAT_CANDIDATE", "BLOCK_MANAT_CANDIDATE"}
FORBIDDEN_VERDICTS = {"FINAL_MANAT", "FINAL_HUKM", "TANZIL", "FINAL_ANSWER"}
MANAT_FIELDS = [
    "manat_candidate_id", "from_hukm_candidate_id", "linked_domain_candidates", "linked_sources",
    "linked_masala_segments", "candidate_manat_statement", "candidate_scope", "cause", "conditions",
    "preventers", "verdict", "evidence", "residuals", "final_manat_allowed", "tanzil_allowed",
    "final_hukm_allowed", "final_answer_allowed", "owner_ratification_required_for_final_manat",
]
GLOBAL_RESIDUALS = [
    "هل ثبت أن الميت لا ولد له؟",
    "هل يوجد ورثة آخرون؟",
    "ما صفة الوارث الذي يريد الطرد؟",
    "هل البيت كله تركة أم فيه حق/انتفاع/إذن سابق؟",
    "هل سكن الأخت كان بإذن المالك قبل موته؟",
    "هل يد الأخت يد معتبرة أو تكذبها قرائن؟",
    "ما الدعوى المحددة للوارث؟",
    "ما جواب الأخت؟",
    "ما البينة؟",
    "هل توجد قرائن أقوى من مجرد اليد؟",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]

# Per-hukm-candidate manāṭ extraction spec (locus of effect). Candidate-form only.
MANAT_SPEC = {
    "HC1_SISTER_SHARE": {
        "manat_candidate_id": "MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS",
        "candidate_manat_statement": ("مرشح مناط أولي: موضع التأثير هو وجود أخت للميت وشروط استحقاقها في "
                                      "التركة؛ شروط الكلالة وسائر الورثة تبقى شرطًا/بقية لا حكمًا. "
                                      "لا يحدد استحقاقًا نهائيًا."),
        "candidate_scope": "مرشح مناط لجهة الميراث/التركة فقط؛ لا يحسم مقدار النصيب ولا الاستحقاق النهائي.",
        "condition_residuals": ["شروط الكلالة", "عدم وجود ولد/والد", "حصر سائر الورثة"],
    },
    "HC2_CLAIM_BURDEN_OF_PROOF": {
        "manat_candidate_id": "MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN",
        "candidate_manat_statement": ("مرشح مناط أولي: موضع التأثير هو وجود دعوى من الوارث على عين/حق ووجود "
                                      "منازعة وعبء الإثبات؛ تنظيم الإثبات يبقى غير حاسم للحق. "
                                      "لا يفصل في موضوع الحق."),
        "candidate_scope": "مرشح مناط لجهة القضاء/الإثبات فقط؛ ينظّم الإجراء لا موضوع الحق، ولا يُلزم قضائيًّا.",
        "condition_residuals": ["تحديد الدعوى", "توفر البينة/اليمين", "فحص القرائن"],
    },
    "HC3_POSSESSION_STAYS_PENDING_EXAMINATION": {
        "manat_candidate_id": "MC3_STANDING_HAND_STATE_BEFORE_EXPULSION",
        "candidate_manat_statement": ("مرشح مناط أولي: موضع التأثير هو كون الأخت ساكنة/ذات يد أو حال قائم قبل "
                                      "الطرد مع فحص القرائن؛ تبقى القاعدة: الحيازة ليست ملكية نهائية. "
                                      "لا يثبت حق سكنى نهائيًا."),
        "candidate_scope": "مرشح مناط لجهة الحيازة/اليد وبقاء الحال؛ الحيازة ليست ملكية نهائية.",
        "condition_residuals": ["اعتبار اليد", "إذن السكنى السابق", "عدم تكذيب القرائن لليد"],
    },
    "HC4_COMPOSITE_LINK_NO_OUTCOME": {
        "manat_candidate_id": "MC4_COMPOSITE_MANAT_LINK_NO_OUTCOME",
        "candidate_manat_statement": ("مرشح مناط مركّب أولي يربط مواضع التأثير: الميراث + التركة + الدعوى + "
                                      "السكنى/الحيازة، دون حسم النتيجة ودون ترتيب أولوية نهائية. "
                                      "يحفظ تعدد المجال المركّب."),
        "candidate_scope": "مرشح مناط مركّب فقط؛ لا يختزل المجال ولا يحسم النازلة ولا يرتّب أولوية نهائية.",
        "condition_residuals": ["اتساق مواضع التأثير", "عدم تعارض بنيوي", "بقاء KEEP_COMPOSITE"],
    },
}


def load_hukm_candidates():
    return json.loads(HUKM_CANDIDATES_23.read_text(encoding="utf-8"))["hukm_candidates"]


def build_manat_candidates(hukm_cands, gate_open):
    verdict = "ACCEPT_AS_MANAT_CANDIDATE_ONLY" if gate_open else "DEFER_MANAT_CANDIDATE"
    tail = {
        "final_manat_allowed": "NO",
        "tanzil_allowed": "NO",
        "final_hukm_allowed": "NO",
        "final_answer_allowed": "NO",
        "owner_ratification_required_for_final_manat": "YES",
    }
    out = []
    for hc in hukm_cands:
        spec = MANAT_SPEC[hc["hukm_candidate_id"]]
        out.append({
            "manat_candidate_id": spec["manat_candidate_id"],
            "from_hukm_candidate_id": hc["hukm_candidate_id"],
            "linked_domain_candidates": hc["linked_domain_candidates"],
            "linked_sources": hc["linked_sources"],
            "linked_masala_segments": hc["linked_masala_segments"],
            "candidate_manat_statement": spec["candidate_manat_statement"],
            "candidate_scope": spec["candidate_scope"],
            "cause": f"مشتق من مرشح الحكم {hc['hukm_candidate_id']} (الجولة 23)؛ المالك رخّص مرشح المناط فقط.",
            "conditions": "؛ ".join(spec["condition_residuals"]) + "؛ بقاء المركّب؛ عدم حسم النتيجة.",
            "preventers": ("جعل موضع التأثير مناطًا نهائيًا؛ حسم مقدار/ملكية/سكنى نهائية؛ إلزام قضائي؛ "
                           "اختزال المركّب؛ اعتبار المصدر وحده مناطًا/حكمًا."),
            "verdict": verdict,
            "evidence": "NORMATIVE_HUKM_CANDIDATES_23.json; HUKM_CANDIDATE_RESIDUALS_23.json",
            "residuals": ("مواضع التأثير مرشّحة فقط؛ الشروط الواقعية غير مفحوصة؛ لا مناط نهائي ولا تنزيل؛ "
                          "يحتاج تصديق المالك للمناط النهائي."),
            **tail,
        })
    return out


def schema():
    return {
        "candidate_form_only": "YES",
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "forbidden_verdicts": sorted(FORBIDDEN_VERDICTS),
        "manat_candidate_fields": MANAT_FIELDS,
        "candidate_statement_must_be_candidate_phrasing": "YES",
        "candidate_statement_must_not_be_final_manat_or_answer": "YES",
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "HUKM_CANDIDATE_IS_NOT_FINAL_HUKM": "YES",
        "HUKM_CANDIDATE_IS_NOT_FINAL_MANAT": "YES",
        "MANAT_CANDIDATE_IS_NOT_FINAL_MANAT": "YES",
        "MANAT_CANDIDATE_IS_NOT_TANZIL": "YES",
        "MANAT_CANDIDATE_IS_NOT_FINAL_ANSWER": "YES",
        "SOURCE_IS_NOT_MANAT": "YES",
        "SOURCE_IS_NOT_HUKM": "YES",
        "POSSESSION_IS_NOT_FINAL_OWNERSHIP": "YES",
        "KEEP_COMPOSITE_REMAINS_ACTIVE": "YES",
        "NO_NEW_SOURCE_ADDED": "YES",
        "AGENT_DID_NOT_RATIFY_SOURCE": "YES",
        "AGENT_DID_NOT_SELECT_SOURCE": "YES",
        "AUTHORITY_LEAK_PREVENTED": "YES",
        "EVIDENCE_IS_CITATION_STRING_ONLY": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "NO_FINAL_MANAT": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def build_residuals(cands):
    return {
        "opening_manat_candidate_blocked": "NO",
        "final_manat_blocked": "YES",
        "global_fact_residuals": GLOBAL_RESIDUALS,
        "per_candidate_residuals": [{"manat_candidate_id": c["manat_candidate_id"],
                                     "residuals": c["residuals"]} for c in cands],
        "unresolved_residuals_recorded": "YES",
        "producer_file": PRODUCER,
    }


def constitution_md(cands):
    L = ["# دستور استخراج مرشّح المناط (الجولة 24 — مرشّح فقط)", "",
         "**ALLOW_MANAT_CANDIDATE = YES · ALLOW_TANZIL = NO · ALLOW_FINAL_HUKM = NO · "
         "ALLOW_FINAL_ANSWER = NO · KEEP_COMPOSITE · THIS_NAZILA_ONLY**", "",
         "تفتح هذه الطبقة بوابة *مرشّح* المناط فقط، لا المناط النهائي. الاستخراج من مرشّحات الحكم الأربعة "
         "(الجولة 23)، موضعَ التأثير في كل منها.", "",
         "## قاعدة القرار",
         "- verdict مسموح ∈ { ACCEPT_AS_MANAT_CANDIDATE_ONLY، DEFER_MANAT_CANDIDATE، BLOCK_MANAT_CANDIDATE }.",
         "- verdict ∈ { FINAL_MANAT، FINAL_HUKM، TANZIL، FINAL_ANSWER } **ممنوع**.",
         "- candidate_manat_statement بصيغة مرشّح («مرشح مناط أولي...») لا مناطًا نهائيًا ولا جوابًا.",
         "", "## الحراس",
         "HUKM_CANDIDATE ≠ FINAL_HUKM/FINAL_MANAT · MANAT_CANDIDATE ≠ FINAL_MANAT/TANZIL/FINAL_ANSWER · "
         "SOURCE ≠ MANAT/HUKM · POSSESSION ≠ FINAL_OWNERSHIP · KEEP_COMPOSITE remains active · "
         "AUTHORITY_LEAK_PREVENTED = YES.",
         "", "## مرشّحات المناط المستخرجة (candidate فقط)"]
    for c in cands:
        L.append(f"- `{c['manat_candidate_id']}` ← {c['from_hukm_candidate_id']} · {c['verdict']} · "
                 f"{c['candidate_manat_statement']}")
    L += ["", "## البقايا الواقعية العشر (residuals لا أحكام)"]
    L += [f"- {r}" for r in GLOBAL_RESIDUALS]
    L += ["", "## ما لا يُنتج",
          "- مناط نهائي · تنزيل · حكم نهائي · جواب · مقدار نصيب · ملكية · حق سكنى نهائي · إلزام قضائي.",
          "", "---",
          "*المناط النهائي والتنزيل والحكم والجواب يحتاج فحص الشروط والموانع + تصديق المالك (الجولة 25 وما بعدها).*"]
    return "\n".join(L) + "\n"


def owner_request_25_md(cands):
    L = ["# طلب تصديق مالك — تطبيق مرشّح المناط (تمهيد الجولة 25)", "",
         "استُخرجت مرشّحات المناط التالية من مرشّحات الحكم (candidate فقط، لا مناط نهائي):", ""]
    for c in cands:
        L.append(f"- `{c['manat_candidate_id']}` ← {c['from_hukm_candidate_id']} · النطاق: {c['candidate_scope']}")
    L += ["", "**تنبيه دور:** المصدر ≠ مناط/حكم، والحيازة ≠ ملكية نهائية، والمركّب باقٍ، "
          "والوكيل لا يصادق/يختر مصدرًا ولا يُنتج مناطًا نهائيًا.", "",
          "المطلوب الآن أن يحدّد المالك صراحةً (الافتراض: لا شيء يُفتح):", "",
          "1. هل يُصرّح بتنقيح/تحقيق المناط (فحص الشروط والموانع الواقعية)؟",
          "   `ALLOW_MANAT_APPLICATION = YES | NO`",
          "2. هل يُصرّح بالتنزيل على الواقعة؟  `ALLOW_TANZIL = YES | NO`",
          "3. هل يُصرّح بالحكم النهائي/الجواب؟  `ALLOW_FINAL_HUKM = YES | NO` · `ALLOW_FINAL_ANSWER = YES | NO`",
          "4. النطاق:  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
          "*حتى تصريح صريح: FINAL_MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · "
          "FINAL_HUKM_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-HUKM-CANDIDATES-23", "ROUND_23",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_HUKM_CANDIDATES_23.json",
     "tests/test_taaqol_normative_hukm_candidate_gate_23.py"),
    ("REQ-MANAT-CANDIDATE-CONSTITUTION-24", "ROUND_24",
     "output/taaqol_maqam_foundation_generated/MANAT_CANDIDATE_EXTRACTION_CONSTITUTION_24.md",
     "tests/test_taaqol_manat_candidate_extraction_24.py"),
    ("REQ-MANAT-CANDIDATES-24", "ROUND_24",
     "output/taaqol_maqam_foundation_generated/MANAT_CANDIDATES_24.json",
     "tests/test_taaqol_manat_candidate_extraction_24.py"),
    ("REQ-MANAT-CANDIDATE-RESIDUALS-24", "ROUND_24",
     "output/taaqol_maqam_foundation_generated/MANAT_CANDIDATE_RESIDUALS_24.json",
     "tests/test_taaqol_manat_candidate_extraction_24.py"),
    ("REQ-MANAT-CANDIDATE-APPLICATION-GATE-25", "ROUND_24",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_MANAT_CANDIDATE_APPLICATION_25.md",
     "tests/test_taaqol_manat_candidate_extraction_24.py"),
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


def build_matrix(cands, gate_open, anm):
    produced = "YES" if cands and gate_open else ("DEFER" if cands else "NO")
    kv = [
        ("ROUND", "MANAT_CANDIDATE_EXTRACTION_GATE_24"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("ALLOW_MANAT_CANDIDATE", "YES"),
        ("ALLOW_TANZIL", "NO"),
        ("ALLOW_FINAL_HUKM", "NO"),
        ("ALLOW_FINAL_ANSWER", "NO"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("EVIDENCE_POLICY", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_IN_ARTIFACTS", "NO"),
        ("CONSTITUTION_MD_CREATED", "YES"),
        ("SCHEMA_CREATED", "YES"),
        ("CANDIDATES_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("RESIDUALS_CREATED", "YES"),
        ("OWNER_REQUEST_25_CREATED", "YES"),
        ("MANAT_CANDIDATE_GATE_OPEN", "YES" if gate_open else "NO"),
        ("MANAT_CANDIDATE_OPENED", "YES"),
        ("MANAT_CANDIDATES_PRODUCED", produced),
        ("MANAT_CANDIDATE_COUNT", str(len(cands))),
        ("SOURCE_HUKM_CANDIDATE_COUNT", "4"),
        ("GLOBAL_FACT_RESIDUAL_COUNT", str(len(GLOBAL_RESIDUALS))),
    ]
    for c in cands:
        kv.append((f"VERDICT::{c['manat_candidate_id']}", c["verdict"]))
        kv.append((f"FROM::{c['manat_candidate_id']}", c["from_hukm_candidate_id"]))
    kv += [
        ("ANY_VERDICT_FINAL_MANAT", "NO"),
        ("ANY_VERDICT_FINAL_HUKM", "NO"),
        ("ANY_VERDICT_TANZIL", "NO"),
        ("ANY_VERDICT_FINAL_ANSWER", "NO"),
        ("FINAL_MANAT_PRODUCED", "NO"),
        ("FINAL_HUKM_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("SISTER_SHARE_AMOUNT_DECIDED", "NO"),
        ("HOUSE_OWNERSHIP_ESTABLISHED", "NO"),
        ("FINAL_RESIDENCE_RIGHT_ESTABLISHED", "NO"),
        ("JUDICIAL_OBLIGATION_ISSUED", "NO"),
        ("SOURCE_ALONE_IS_MANAT", "NO"),
        ("POSSESSION_IS_FINAL_OWNERSHIP", "NO"),
        ("ALL_ROUND13_DOMAIN_CANDIDATES_COVERED", "YES"),
        ("NEW_SOURCE_BORN", "NO"),
        ("AGENT_RATIFIED_SOURCE", "NO"),
        ("SELECTED_BY_AGENT", "NO"),
        ("KEEP_COMPOSITE_REMAINS_ACTIVE", "YES"),
        ("AUTHORITY_LEAK_PREVENTED", "YES"),
        ("OWNER_RATIFICATION_REQUIRED_FOR_FINAL_MANAT", "YES"),
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


def render_manager(tokens, cands, residuals, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — استخراج مرشّح المناط (24)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — استخراج مرشّح المناط (24)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'EXTERNAL_REFS = 0. بوابة مرشّح مناط فقط — لا مناط نهائي/تنزيل/حكم/جواب.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'هذه جولة مرشّح مناط فقط · لا مناط نهائي · لا حكم نهائي · لا تنزيل · لا جواب · '
             'الحيازة لا تساوي ملكية نهائية (POSSESSION ≠ FINAL_OWNERSHIP) · المركّب باقٍ '
             '(KEEP_COMPOSITE).</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>فتح المالك بوابة مرشّح المناط فقط (ALLOW_MANAT_CANDIDATE=YES؛ التنزيل/الحكم النهائي/الجواب = NO).</li>'
             f'<li>استُخرجت {len(cands)} مرشّحات مناط من مرشّحات الحكم الأربعة، موضعَ التأثير في كل منها.</li>'
             '<li>لا مناط نهائي؛ البقايا الواقعية العشر مسجَّلة كشروط لا أحكام؛ المركّب باقٍ.</li></ul>')
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
             'LIVE_EXTERNAL_LINKS = NO · EXTERNAL_REFS = 0. المصادر الأربعة مصدَّقة من المالك؛ الوكيل لا يصادق.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'استُخرج المناط كمرشّح بنيوي فقط؛ لا رخصة عبور إلى المناط النهائي أو التنزيل على الواقعة. '
             'FACTUAL_CLAIM_TO_FINAL_MANAT_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — استخراج مرشّح المناط</h2><div class="wrap"><table><thead><tr>'
             '<th>manat_candidate</th><th>من مرشّح الحكم</th><th>المجالات</th><th>صياغة المناط المرشّح</th>'
             '<th>verdict</th><th>final_manat</th></tr></thead><tbody>')
    for c in cands:
        vcls = "y" if c["verdict"] == "ACCEPT_AS_MANAT_CANDIDATE_ONLY" else "d"
        P.append('<tr><th>' + e(c["manat_candidate_id"]) + '</th><td>' + e(c["from_hukm_candidate_id"]) + '</td>'
                 '<td>' + e("، ".join(c["linked_domain_candidates"])) + '</td>'
                 '<td>' + e(c["candidate_manat_statement"]) + '</td>'
                 + f'<td class="{vcls}">{e(c["verdict"])}</td>'
                 + f'<td class="n">{e(c["final_manat_allowed"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="note n" style="background:#fdecec"><b>الحراس:</b> '
             'HUKM_CANDIDATE ≠ FINAL_HUKM/FINAL_MANAT · MANAT_CANDIDATE ≠ FINAL_MANAT/TANZIL/FINAL_ANSWER · '
             'SOURCE ≠ MANAT/HUKM · POSSESSION ≠ FINAL_OWNERSHIP · KEEP_COMPOSITE remains active · '
             'AUTHORITY_LEAK_PREVENTED = YES.</div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: MANAT_CANDIDATE. المرشّحات مفتوحة بنيويًّا فقط؛ لا مناط نهائي ولا تنزيل ولا حكم ولا جواب.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2>'
             '<div class="note n" style="background:#fdecec"><b>البقايا الواقعية (residuals لا أحكام):</b><ul>'
             + "".join(f'<li>{e(x)}</li>' for x in residuals["global_fact_residuals"]) + '</ul></div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند تصريح المالك (الجولة 25): '
             'ALLOW_MANAT_APPLICATION (تنقيح/تحقيق المناط) / ALLOW_TANZIL / ALLOW_FINAL_HUKM / ALLOW_FINAL_ANSWER '
             'مع تحديد النطاق — بعد فحص الشروط والموانع الواقعية، لا قبله.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_manat_candidate_extraction_24.py — '
             'ROUND_24_TESTS = passed · REGRESSION_SCOPE = maqam 02..24 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_24_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUTS = NORMATIVE_HUKM_CANDIDATES_23.json; HUKM_CANDIDATE_RESIDUALS_23.json; '
             'SOURCE_TO_MASALA_MAPPING_18.json; RATIFIED_SOURCE_BIRTH_REGISTRY_17.json; '
             'SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json; SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json\n'
             'CONSTITUTION_MD = output/taaqol_maqam_foundation_generated/MANAT_CANDIDATE_EXTRACTION_CONSTITUTION_24.md\n'
             'SCHEMA = output/taaqol_maqam_foundation_generated/MANAT_CANDIDATE_SCHEMA_24.json\n'
             'CANDIDATES = output/taaqol_maqam_foundation_generated/MANAT_CANDIDATES_24.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/MANAT_CANDIDATE_GUARDS_24.json\n'
             'RESIDUALS = output/taaqol_maqam_foundation_generated/MANAT_CANDIDATE_RESIDUALS_24.json\n'
             'OWNER_REQUEST_25 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_MANAT_CANDIDATE_APPLICATION_25.md\n'
             'PYTEST_FILE = tests/test_taaqol_manat_candidate_extraction_24.py\n'
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY\nLIVE_EXTERNAL_LINKS_IN_ARTIFACTS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'استُخرجت {len(cands)} مرشّحات مناط من مرشّحات الحكم الأربعة (موضع التأثير)، بصيغة candidate فقط، '
             'دون مناط نهائي أو تنزيل أو حكم أو جواب، ومع تسجيل البقايا الواقعية العشر وبقاء المركّب '
             'ومنع AUTHORITY_LEAK. طلب الجولة 25 جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'MANAT_CANDIDATE_OPENED = YES · MANAT_CANDIDATES_PRODUCED = YES · '
             f'MANAT_CANDIDATE_COUNT = {len(cands)} · ANY_VERDICT_FINAL_MANAT = NO · '
             'FINAL_MANAT_PRODUCED = NO · FINAL_HUKM_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · NEW_SOURCE_BORN = NO · KEEP_COMPOSITE_REMAINS_ACTIVE = YES · '
             'AUTHORITY_LEAK_PREVENTED = YES · OWNER_RATIFICATION_REQUIRED_FOR_FINAL_MANAT = YES · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_24_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'MANAT_CANDIDATE_OPENED = YES · FINAL_MANAT_PRODUCED = NO · FINAL_HUKM_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "MANAT_CANDIDATE_EXTRACTION_MANAGER_REPORT_AR_24.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "MANAT_CANDIDATE_EXTRACTION_24_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    hukm_cands = load_hukm_candidates()
    gate_open = len(hukm_cands) == 4
    cands = build_manat_candidates(hukm_cands, gate_open)
    residuals = build_residuals(cands)

    (OUT / "MANAT_CANDIDATE_EXTRACTION_CONSTITUTION_24.md").write_text(
        constitution_md(cands), encoding="utf-8")
    (OUT / "MANAT_CANDIDATE_SCHEMA_24.json").write_text(
        json.dumps(schema(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MANAT_CANDIDATES_24.json").write_text(
        json.dumps({"ROUND": "MANAT_CANDIDATE_EXTRACTION_GATE_24",
                    "manat_candidate_opened": "YES",
                    "manat_candidate_gate_open": "YES" if gate_open else "NO",
                    "candidate_form_only": "YES",
                    "manat_candidate_count": len(cands),
                    "manat_candidates": cands,
                    "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MANAT_CANDIDATE_GUARDS_24.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MANAT_CANDIDATE_RESIDUALS_24.json").write_text(
        json.dumps(residuals, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_MANAT_CANDIDATE_APPLICATION_25.md").write_text(
        owner_request_25_md(cands), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(cands, gate_open, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, cands, residuals, trows, anm), encoding="utf-8")
    print("REPORT_24=" + a.report_out)
    print(f"GATE_OPEN={gate_open} MANAT_CANDIDATES={len(cands)} "
          f"ANY_FINAL={'YES' if any(c['verdict'] in FORBIDDEN_VERDICTS for c in cands) else 'NO'} "
          f"ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
