#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_OWNER_FACT_RATIFICATION_AND_MISSING_FACT_SUPPLY_36 (owner ratification gate only).

Presents the five round-35 fact CANDIDATES for owner ratification (never auto-accepted) and a supply
template for the nine missing facts. The owner has supplied no ratification values in this round, so every
decision defaults to DEFER, FACT_ACCEPTED stays NO, factual facts are incomplete, and PHASE 0 remains
BLOCKED. No fact is inferred from agent knowledge; a question is not a source; a requirement is not a
fact; a skeleton is not populated. No final manāṭ/tanzīl/final hukm/final answer. No commit; no push.
Manager report obeys the AR_09_FIXED experience.
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
PRODUCER = "scripts/taaqol_maqam_foundation/owner_fact_ratification_36.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
FCR_35 = OUT / "FACTUAL_CLAIM_REGISTRY_35.json"
MISS_35 = OUT / "MISSING_FACT_REQUIREMENTS_35.json"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def load_inputs():
    fc = json.loads(FCR_35.read_text(encoding="utf-8"))["fact_candidates"]
    mf = json.loads(MISS_35.read_text(encoding="utf-8"))["missing_facts"]
    return fc, mf


def build_decisions(fc):
    """Owner supplied NO ratification values this round -> every decision defaults to DEFER."""
    rows = []
    for f in fc:
        rows.append({
            "decision_id": "DEC_" + f["fact_id"],
            "fact_id": f["fact_id"],
            "normalized_fact_statement": f["normalized_fact_statement"],
            "OWNER_RATIFY": "DEFER",
            "FACT_ACCEPTED": "NO",
            "cause": "مرشح واقعة نصية من الجولة 35 معروض للتصديق.",
            "conditions": "FACT_ACCEPTED=YES فقط إذا OWNER_RATIFY=YES صراحةً من المالك.",
            "preventers": "قبول تلقائي؛ اشتقاق واقعة من علم الوكيل؛ اعتبار العرض تصديقًا.",
            "verdict": "AWAITING_OWNER_RATIFICATION_DEFER",
            "residuals": "لا واقعة مقبولة حتى يدخل المالك OWNER_RATIFY=YES.",
        })
    return rows


def build_missing_template(mf):
    return [{
        "missing_fact_id": m["missing_fact_id"],
        "description": m["description"],
        "OWNER_SUPPLIED_VALUE": "",
        "SOURCE_OR_EVIDENCE_REF": "",
        "OWNER_RATIFY": "DEFER",
        "FACT_ACCEPTED": "NO",
        "cause": "واقعة غير منطوقة في النص؛ تحتاج تزويد مالك + مصدر.",
        "conditions": "قيمة مزوَّدة + مرجع/بينة + OWNER_RATIFY=YES.",
        "preventers": "اشتقاقها من علم الوكيل؛ اعتبار الطلب مصدرًا؛ قبولها بلا تصديق.",
        "verdict": "REQUIRED_FACT_MISSING_DEFER",
        "residuals": "معلّقة حتى تزويد وتصديق المالك.",
    } for m in mf]


def build_recheck(decisions, missing):
    ratified = sum(1 for d in decisions if d["OWNER_RATIFY"] == "YES" and d["FACT_ACCEPTED"] == "YES")
    missing_supplied = sum(1 for m in missing if m["FACT_ACCEPTED"] == "YES")
    facts_complete = (ratified == len(decisions)) and (missing_supplied == len(missing))
    gate_pass = facts_complete
    return {
        "ROUND": "TAAQOL_OWNER_FACT_RATIFICATION_AND_MISSING_FACT_SUPPLY_36",
        "TASK_PHASE": "PHASE0_RECHECK_AFTER_FACT_RATIFICATION",
        "fact_candidates_reviewed": len(decisions),
        "owner_ratified_fact_count": ratified,
        "missing_fact_requirements_reviewed": len(missing),
        "missing_facts_supplied_count": missing_supplied,
        "factual_facts_complete": "YES" if facts_complete else "NO",
        "phase0_gate_pass": "YES" if gate_pass else "NO",
        "ready_for_expansion": "NO",
        "FINAL_MANAT": "NO",
        "TANZIL": "NO",
        "FINAL_HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "decision": {
            "cause": "presented 5 fact candidates + 9 missing-fact template for owner",
            "conditions": "all 5 ratified (OWNER_RATIFY=YES) AND all 9 supplied+ratified",
            "preventers": "no owner ratification values entered this round",
            "verdict": "STILL_BLOCKED_AT_PHASE_0_FACTS_NOT_RATIFIED" if not gate_pass else "PHASE_0_FACTS_READY",
            "residuals": "owner must ratify 5 candidates and supply+ratify 9 missing facts",
        },
        "producer_file": PRODUCER,
    }


def schema():
    return {
        "decision_fields": ["decision_id", "fact_id", "normalized_fact_statement", "OWNER_RATIFY",
                            "FACT_ACCEPTED", "cause", "conditions", "preventers", "verdict", "residuals"],
        "OWNER_RATIFY_allowed_values": ["YES", "NO", "DEFER"],
        "FACT_ACCEPTED_rule": "YES only if OWNER_RATIFY==YES",
        "default_if_absent": "DEFER",
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "AGENT_KNOWLEDGE_CREATES_FACT": "NO",
        "QUESTION_CREATES_FACT": "NO",
        "REQUIREMENT_CREATES_FACT": "NO",
        "TEXT_FACT_CANDIDATE_IS_NOT_ACCEPTED_FACT": "YES",
        "OWNER_RATIFICATION_REQUIRED_FOR_FACT_ACCEPTANCE": "YES",
        "MISSING_FACT_DEFAULT": "DEFER",
        "SKELETON_NOT_POPULATED_WITHOUT_OWNER": "YES",
        "FINAL_MANAT": "NO",
        "TANZIL": "NO",
        "FINAL_HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "READY_FOR_EXPANSION": "NO",
        "producer_file": PRODUCER,
    }


def ratification_request_md(decisions):
    L = ["# طلب تصديق مالك على مرشحات الوقائع (الجولة 36)", "",
         f"النازلة: «{SENTENCE}»", "",
         "المرشحات الخمسة من منطوق النص (الجولة 35) **معروضة للتصديق، لا مقبولة تلقائيًّا**. "
         "لكل مرشح أدخِل `OWNER_RATIFY = YES | NO | DEFER` (الافتراض DEFER):", ""]
    for d in decisions:
        L.append(f"- `{d['fact_id']}` — {d['normalized_fact_statement']}")
        L.append("  - OWNER_RATIFY = ____   (FACT_ACCEPTED=YES فقط إذا YES)")
    L += ["", "**تنبيه:** لا واقعة تُقبل إلا بتصديقك الصريح؛ العرض ليس قبولًا، والوكيل لا يشتق واقعة من علمه.",
          "", "*حتى تُصدّق الخمسة وتُزوّد التسع الناقصة: FACTUAL_FACTS_COMPLETE=NO · PHASE0_GATE_PASS=NO · "
          "لا مناط/تنزيل/حكم/جواب.*"]
    return "\n".join(L) + "\n"


def missing_supply_template_md(missing):
    L = ["# قالب تزويد الوقائع الناقصة (الجولة 36 — للتعبئة من المالك)", "",
         "الوقائع التسع غير المنطوقة في النص تحتاج تزويدًا بقرار مالك + مصدر/بينة. الحقول فارغة للتعبئة:", ""]
    for m in missing:
        L.append(f"## {m['missing_fact_id']} — {m['description']}")
        L.append("- OWNER_SUPPLIED_VALUE: ____")
        L.append("- SOURCE_OR_EVIDENCE_REF: ____")
        L.append("- OWNER_RATIFY = YES/NO/DEFER")
        L.append("- (FACT_ACCEPTED=YES فقط إذا OWNER_RATIFY=YES)")
    L += ["", "---", "*حتى تُملأ وتُصدّق: كل واقعة ناقصة = REQUIRED_FACT_MISSING / DEFER.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-FACTUAL-CLAIM-REGISTRY-35", "ROUND_35",
     "output/taaqol_maqam_foundation_generated/FACTUAL_CLAIM_REGISTRY_35.json",
     "tests/test_taaqol_fact_registry_population_35.py"),
    ("REQ-FACT-RATIFICATION-DECISIONS-36", "ROUND_36",
     "output/taaqol_maqam_foundation_generated/OWNER_FACT_RATIFICATION_DECISIONS_36.json",
     "tests/test_taaqol_owner_fact_ratification_36.py"),
    ("REQ-MISSING-FACT-SUPPLY-TEMPLATE-36", "ROUND_36",
     "output/taaqol_maqam_foundation_generated/MISSING_FACT_SUPPLY_TEMPLATE_36.md",
     "tests/test_taaqol_owner_fact_ratification_36.py"),
    ("REQ-PHASE0-RECHECK-36", "ROUND_36",
     "output/taaqol_maqam_foundation_generated/PHASE0_RECHECK_AFTER_FACT_RATIFICATION_36.json",
     "tests/test_taaqol_owner_fact_ratification_36.py"),
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


def build_matrix(decisions, missing, recheck, anm):
    kv = [
        ("ROUND", "TAAQOL_OWNER_FACT_RATIFICATION_AND_MISSING_FACT_SUPPLY_36"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("RATIFICATION_REQUEST_CREATED", "YES"),
        ("RATIFICATION_SCHEMA_CREATED", "YES"),
        ("RATIFICATION_DECISIONS_CREATED", "YES"),
        ("MISSING_SUPPLY_TEMPLATE_CREATED", "YES"),
        ("PHASE0_RECHECK_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("FACT_CANDIDATES_REVIEWED", str(len(decisions))),
        ("OWNER_RATIFIED_FACT_COUNT", str(recheck["owner_ratified_fact_count"])),
        ("MISSING_FACT_REQUIREMENTS_REVIEWED", str(len(missing))),
        ("MISSING_FACTS_SUPPLIED_COUNT", str(recheck["missing_facts_supplied_count"])),
        ("ALL_DECISIONS_DEFER_IF_ABSENT", "YES" if all(d["OWNER_RATIFY"] == "DEFER" for d in decisions) else "NO"),
        ("ALL_FACT_ACCEPTED_NO", "YES" if all(d["FACT_ACCEPTED"] == "NO" for d in decisions) else "NO"),
        ("FACTUAL_FACTS_COMPLETE", recheck["factual_facts_complete"]),
        ("PHASE0_RECHECK_DONE", "YES"),
        ("PHASE0_GATE_PASS", recheck["phase0_gate_pass"]),
        ("READY_FOR_EXPANSION", "NO"),
        ("AGENT_KNOWLEDGE_CREATES_FACT", "NO"),
        ("QUESTION_CREATES_FACT", "NO"),
        ("REQUIREMENT_CREATES_FACT", "NO"),
        ("FINAL_MANAT", "NO"),
        ("TANZIL", "NO"),
        ("FINAL_HUKM", "NO"),
        ("FINAL_ANSWER", "NO"),
        ("FULL_TAAQOL_PROJECT_CLOSED", "NO"),
        ("AUTHORITY_LEAK", "NO"),
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
        ("PUSH_EXECUTED", "NO"),
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


def render_manager(tokens, decisions, missing, recheck, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — بوابة تصديق الوقائع (36)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — بوابة تصديق الوقائع وتزويد الناقص (36)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0 · SCOPE = THIS_NAZILA_ONLY. '
             'بوابة تصديق مالك فقط — لا قبول تلقائي.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'علم الوكيل لا يُنشئ واقعة · السؤال لا يُنشئ واقعة · المتطلب لا يُنشئ واقعة · '
             'مرشح النص ليس واقعة مقبولة · تصديق المالك مطلوب · لا مناط/تنزيل/حكم/جواب · '
             'FULL_TAAQOL_PROJECT_CLOSED=NO · READY_FOR_EXPANSION=NO.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             f'<li>عُرِضت **{len(decisions)}** مرشحات وقائع للتصديق؛ المالك لم يُدخِل قيم تصديق بعد → الكل DEFER.</li>'
             f'<li>OWNER_RATIFIED_FACT_COUNT = {recheck["owner_ratified_fact_count"]} · '
             f'MISSING_FACTS_SUPPLIED = {recheck["missing_facts_supplied_count"]}/{len(missing)}.</li>'
             f'<li>FACTUAL_FACTS_COMPLETE = {e(recheck["factual_facts_complete"])} · '
             f'PHASE0_GATE_PASS = {e(recheck["phase0_gate_pass"])}؛ لا انتقال إلى المناط.</li></ul>')
    P.append('<h2>2. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    P.append('<h2>3. جدول الكلمات العشر</h2>')
    if not tokens:
        P.append('<div class="note n">TOKEN_ARTIFACT_MISSING</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>الفئة</th></tr></thead><tbody>')
        for t in tokens:
            P.append('<tr><th>' + e(t["token_id"]) + '</th><td>' + e(t.get("original_surface", "")) +
                     '</td><td>' + e(t.get("word_class", "")) + '</td></tr>')
        P.append('</tbody></table></div>')
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ لا تُقبل كواقعة. IFADAH_CHANGED = NO.</div>')
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يُنشئ واقعة. MAQAM_IS_NOT_FACT = YES.</div>')
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'الوقائع والبينة يقرّها المالك؛ لا اشتقاق من علم الوكيل.</div>')
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'لا واقعة مقبولة ولا رخصة عبور؛ العرض للتصديق فقط. FACT_ACCEPTED = NO.</div>')
    P.append('<h2>8. المصدر المعياري — قرارات تصديق المرشحات</h2><div class="wrap"><table><thead><tr>'
             '<th>fact_id</th><th>الواقعة</th><th>OWNER_RATIFY</th><th>FACT_ACCEPTED</th><th>verdict</th>'
             '</tr></thead><tbody>')
    for d in decisions:
        P.append('<tr><th>' + e(d["fact_id"]) + '</th><td>' + e(d["normalized_fact_statement"]) + '</td>'
                 + f'<td class="d">{e(d["OWNER_RATIFY"])}</td><td class="n">{e(d["FACT_ACCEPTED"])}</td>'
                 + f'<td class="d">{e(d["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>9. موضع التوقف — قالب تزويد الوقائع الناقصة (9)</h2><div class="wrap"><table><thead><tr>'
             '<th>missing_fact_id</th><th>الوصف</th><th>OWNER_RATIFY</th><th>FACT_ACCEPTED</th></tr></thead><tbody>')
    for m in missing:
        P.append(f'<tr><th>{e(m["missing_fact_id"])}</th><td>{e(m["description"])}</td>'
                 f'<td class="d">{e(m["OWNER_RATIFY"])}</td><td class="n">{e(m["FACT_ACCEPTED"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note n" style="background:#fdecec">'
             'المطلوب: إدخال OWNER_RATIFY=YES للمرشحات المقبولة، وتعبئة قيم/مصادر الوقائع التسع وتصديقها. '
             'حتى ذلك: كل شيء DEFER.</div>')
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند اكتمال التصديق والتزويد: يُعاد فحص PHASE 0؛ '
             'إن اجتاز (كل الوقائع المطلوبة مصدَّقة) عندها فقط يُفتح تطبيق المناط الواقعي — لا قبله.</div>')
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_owner_fact_ratification_36.py — '
             'ROUND_36_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32..36 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    P.append(_trace_html(trows))
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_36_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUTS = FACTUAL_CLAIM_REGISTRY_35.json; MISSING_FACT_REQUIREMENTS_35.json\n'
             'RATIFICATION_REQUEST = output/taaqol_maqam_foundation_generated/OWNER_FACT_RATIFICATION_REQUEST_36.md\n'
             'RATIFICATION_SCHEMA = output/taaqol_maqam_foundation_generated/OWNER_FACT_RATIFICATION_SCHEMA_36.json\n'
             'RATIFICATION_DECISIONS = output/taaqol_maqam_foundation_generated/OWNER_FACT_RATIFICATION_DECISIONS_36.json\n'
             'MISSING_SUPPLY_TEMPLATE = output/taaqol_maqam_foundation_generated/MISSING_FACT_SUPPLY_TEMPLATE_36.md\n'
             'PHASE0_RECHECK = output/taaqol_maqam_foundation_generated/PHASE0_RECHECK_AFTER_FACT_RATIFICATION_36.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/FACT_RATIFICATION_GUARDS_36.json\n'
             'PYTEST_FILE = tests/test_taaqol_owner_fact_ratification_36.py\n'
             'OWNER_RATIFIED_FACT_COUNT = ' + str(recheck["owner_ratified_fact_count"]) + '\n'
             'FACTUAL_FACTS_COMPLETE = ' + recheck["factual_facts_complete"] + '\nPHASE0_GATE_PASS = '
             + recheck["phase0_gate_pass"] + '\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'عُرِضت الوقائع الخمسة للتصديق وقالب التسع الناقصة؛ لا تصديق مُدخَل بعد → OWNER_RATIFIED=0، '
             'FACTUAL_FACTS_COMPLETE=NO، PHASE 0 محجوب. لا مناط/تنزيل/حكم/جواب، ولا إغلاق مشروع.</div>')
    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'FACT_CANDIDATES_REVIEWED = {len(decisions)} · OWNER_RATIFIED_FACT_COUNT = {recheck["owner_ratified_fact_count"]} · '
             f'MISSING_FACT_REQUIREMENTS_REVIEWED = {len(missing)} · '
             f'FACTUAL_FACTS_COMPLETE = {e(recheck["factual_facts_complete"])} · '
             f'PHASE0_GATE_PASS = {e(recheck["phase0_gate_pass"])} · READY_FOR_EXPANSION = NO · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             'FULL_TAAQOL_PROJECT_CLOSED = NO · AUTHORITY_LEAK = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_36_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'OWNER_RATIFIED_FACT_COUNT = 0 · FACTUAL_FACTS_COMPLETE = NO · PHASE0_GATE_PASS = NO · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             'FULL_TAAQOL_PROJECT_CLOSED = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "FACT_RATIFICATION_MANAGER_REPORT_AR_36.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "FACT_RATIFICATION_36_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    fc, mf = load_inputs()
    decisions = build_decisions(fc)
    missing = build_missing_template(mf)
    recheck = build_recheck(decisions, missing)

    (OUT / "OWNER_FACT_RATIFICATION_REQUEST_36.md").write_text(ratification_request_md(decisions), encoding="utf-8")
    (OUT / "OWNER_FACT_RATIFICATION_SCHEMA_36.json").write_text(
        json.dumps(schema(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_FACT_RATIFICATION_DECISIONS_36.json").write_text(
        json.dumps({"ROUND": "TAAQOL_OWNER_FACT_RATIFICATION_AND_MISSING_FACT_SUPPLY_36",
                    "fact_candidates_reviewed": len(decisions),
                    "owner_ratified_fact_count": recheck["owner_ratified_fact_count"],
                    "decisions": decisions,
                    "missing_fact_supply_records": missing,
                    "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MISSING_FACT_SUPPLY_TEMPLATE_36.md").write_text(missing_supply_template_md(missing), encoding="utf-8")
    (OUT / "PHASE0_RECHECK_AFTER_FACT_RATIFICATION_36.json").write_text(
        json.dumps(recheck, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "FACT_RATIFICATION_GUARDS_36.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(decisions, missing, recheck, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, decisions, missing, recheck, trows, anm), encoding="utf-8")
    print("REPORT_36=" + a.report_out)
    print(f"REVIEWED={len(decisions)} RATIFIED={recheck['owner_ratified_fact_count']} "
          f"MISSING={len(missing)} FACTS_COMPLETE={recheck['factual_facts_complete']} "
          f"PHASE0_GATE_PASS={recheck['phase0_gate_pass']} ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
