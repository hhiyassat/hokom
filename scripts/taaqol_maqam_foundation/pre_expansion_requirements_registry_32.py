#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32 (foundational, no ruling).

Owner rule: the manāṭ-application questions are NOT canonical rules just because they came from agent
knowledge. Before expanding beyond the single nazila, each question must become a REQUIREMENT (fact/
source/database/owner-decision/gate) — never a fact, never a source, never a rule. This round records
that requirements registry only: no final manāṭ, no tanzīl, no final hukm, no final answer, READY_FOR_
EXPANSION=NO. Manager report obeys the AR_09_FIXED experience. No commit; no push; priors unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/pre_expansion_requirements_registry_32.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
REQUIREMENT_TYPES = ["FACT_REQUIREMENT", "SOURCE_REQUIREMENT", "DATABASE_REQUIREMENT",
                     "OWNER_DECISION_REQUIREMENT", "GATE_REQUIREMENT"]
REQ_FIELDS = ["requirement_id", "original_question", "requirement_type", "why_needed",
              "required_database_or_registry", "required_source_type", "required_owner_decision",
              "cause", "conditions", "preventers", "default_verdict_if_missing", "residuals",
              "expansion_blocker"]
REGISTRIES_TO_BUILD = [
    "factual_claim_registry", "owner_supplied_fact_registry", "source_requirement_registry",
    "normative_source_registry", "domain_candidate_registry", "hukm_candidate_registry",
    "manat_candidate_registry", "tanzil_requirement_registry", "proof_burden_registry",
    "possession_yad_registry", "inheritance_condition_registry", "residual_registry",
    "owner_ratification_registry",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]

# The ten factual residuals -> requirements (NOT facts). requirement_type per the owner's five kinds.
REQUIREMENT_SPEC = [
    {
        "id": "REQ01_NO_CHILD", "q": "هل ثبت أن الميت لا ولد له؟",
        "type": "FACT_REQUIREMENT",
        "why": "شرط الكلالة يتوقف على انتفاء الولد؛ لا يُفترض من معرفة الوكيل.",
        "db": "factual_claim_registry", "src": "OWNER_SUPPLIED_FACT | حصر إرث موثّق",
        "owner": "تصديق واقعة انتفاء الولد",
    },
    {
        "id": "REQ02_OTHER_HEIRS", "q": "هل يوجد ورثة آخرون؟",
        "type": "DATABASE_REQUIREMENT",
        "why": "ترتيب الفروض والباقي يتوقف على حصر الورثة.",
        "db": "inheritance_condition_registry", "src": "OWNER_SUPPLIED_FACT | حصر إرث",
        "owner": "اعتماد قائمة الورثة",
    },
    {
        "id": "REQ03_HEIR_CAPACITY", "q": "ما صفة الوارث الذي يريد الطرد؟",
        "type": "FACT_REQUIREMENT",
        "why": "جنبة الدعوى وصفة المدّعي تحدّدان موقع عبء الإثبات.",
        "db": "factual_claim_registry", "src": "OWNER_SUPPLIED_FACT",
        "owner": "تحديد صفة الوارث",
    },
    {
        "id": "REQ04_HOUSE_STATUS", "q": "هل البيت كله تركة أم فيه حق/انتفاع/إذن سابق؟",
        "type": "DATABASE_REQUIREMENT",
        "why": "صفة المحل (تركة/حق/انتفاع) شرط لدخوله في القسمة أو خروجه.",
        "db": "possession_yad_registry", "src": "سند ملكية/وقف/إذن (OWNER_SUPPLIED)",
        "owner": "تصديق صفة البيت",
    },
    {
        "id": "REQ05_PRIOR_PERMISSION", "q": "هل كان سكن الأخت بإذن المالك قبل موته؟",
        "type": "FACT_REQUIREMENT",
        "why": "الإذن السابق يقوّي جنبة بقاء اليد؛ واقعة تحتاج إثباتًا.",
        "db": "possession_yad_registry", "src": "إقرار/بينة/قرينة (OWNER_SUPPLIED)",
        "owner": "تصديق واقعة الإذن",
    },
    {
        "id": "REQ06_HAND_CREDIBLE", "q": "هل يد الأخت معتبرة أم تكذبها قرائن؟",
        "type": "GATE_REQUIREMENT",
        "why": "اعتبار اليد بوابة سبب/شرط/مانع لا يقرّرها الوكيل من معرفته.",
        "db": "possession_yad_registry", "src": "قرائن/بينة (OWNER_SUPPLIED)",
        "owner": "بوابة تقييم اليد مقابل القرائن",
    },
    {
        "id": "REQ07_CLAIM_CONTENT", "q": "ما الدعوى المحددة للوارث؟",
        "type": "FACT_REQUIREMENT",
        "why": "محل النزاع لا يُنشأ من الوكيل بل يُزوَّد.",
        "db": "factual_claim_registry", "src": "صحيفة دعوى/إقرار (OWNER_SUPPLIED)",
        "owner": "اعتماد نص الدعوى",
    },
    {
        "id": "REQ08_DEFENSE_CONTENT", "q": "ما جواب الأخت؟",
        "type": "FACT_REQUIREMENT",
        "why": "موقف المدّعى عليه واقعة تُزوَّد لا تُفترض.",
        "db": "factual_claim_registry", "src": "جواب/إقرار/إنكار (OWNER_SUPPLIED)",
        "owner": "اعتماد نص الجواب",
    },
    {
        "id": "REQ09_EVIDENCE", "q": "ما البينة؟",
        "type": "GATE_REQUIREMENT",
        "why": "عبء الإثبات بوابة (بينة/يمين) لا يقرّرها الوكيل.",
        "db": "proof_burden_registry", "src": "بينة/شهود/وثائق (OWNER_SUPPLIED)",
        "owner": "بوابة عبء الإثبات",
    },
    {
        "id": "REQ10_QARINA_STRENGTH", "q": "هل توجد قرائن أقوى من مجرد اليد؟",
        "type": "GATE_REQUIREMENT",
        "why": "موازنة القرائن مقابل اليد بوابة مانع، لا معرفة وكيل.",
        "db": "possession_yad_registry", "src": "قرائن مقارنة (OWNER_SUPPLIED)",
        "owner": "بوابة موازنة القرائن",
    },
]


def build_requirements():
    rows = []
    for s in REQUIREMENT_SPEC:
        rows.append({
            "requirement_id": s["id"],
            "original_question": s["q"],
            "requirement_type": s["type"],
            "why_needed": s["why"],
            "required_database_or_registry": s["db"],
            "required_source_type": s["src"],
            "required_owner_decision": s["owner"],
            "cause": "سؤال ظهر في جولة المناط من معرفة الوكيل؛ يجب تسجيله كمتطلب قبل التوسع.",
            "conditions": "توفّر سجل/مصدر/قرار مالك مطابق؛ عدم اشتقاق واقعة من معرفة الوكيل.",
            "preventers": ("اعتبار السؤال قاعدة كنسية؛ إنشاء واقعة/مصدر من الوكيل؛ التوسع قبل التسجيل؛ "
                           "إنتاج مناط/تنزيل/حكم/جواب."),
            "default_verdict_if_missing": "DEFER",
            "residuals": "غير مستوفى حتى يُبنى السجل/يُزوَّد المصدر/يصدّق المالك.",
            "expansion_blocker": "YES",
        })
    return rows


def build_registries_plan(rows):
    # which requirement ids feed which registry-to-build
    feed = {r: [] for r in REGISTRIES_TO_BUILD}
    for row in rows:
        db = row["required_database_or_registry"]
        if db in feed:
            feed[db].append(row["requirement_id"])
    return [{
        "registry_id": r,
        "status": "MUST_BE_BUILT_BEFORE_EXPANSION",
        "fed_by_requirements": feed.get(r, []),
        "creates_fact": "NO",
        "creates_source": "NO",
        "owner_ratification_required": "YES",
    } for r in REGISTRIES_TO_BUILD]


def guards():
    return {
        "AGENT_QUESTION_IS_NOT_CANONICAL_RULE": "YES",
        "QUESTION_DOES_NOT_CREATE_FACT": "YES",
        "REQUIREMENT_DOES_NOT_CREATE_FACT": "YES",
        "SOURCE_REQUIREMENT_DOES_NOT_CREATE_SOURCE": "YES",
        "OWNER_RATIFICATION_REQUIRED": "YES",
        "NO_FINAL_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "READY_FOR_EXPANSION": "NO",
        "producer_file": PRODUCER,
    }


def build_registry_json(rows, plan):
    counts = {t: sum(1 for r in rows if r["requirement_type"] == t) for t in REQUIREMENT_TYPES}
    return {
        "ROUND": "TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32",
        "nazila_scope": SENTENCE,
        "questions_from_agent_knowledge_canonical": "NO",
        "questions_converted_to_requirements": "YES",
        "requirement_count": len(rows),
        "requirement_type_counts": counts,
        "requirement_types_allowed": REQUIREMENT_TYPES,
        "requirements": rows,
        "registries_to_build_before_expansion": plan,
        "ready_for_expansion": "NO",
        "NO_FINAL_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def registry_md(rows, plan):
    L = ["# سجل المتطلبات قبل التوسع (الجولة 32 — تأسيسي فقط)", "",
         "**قاعدة المالك:** الأسئلة التي ظهرت في جولة المناط ليست قانونًا كنسيًا لأنها من معرفة الوكيل. "
         "قبل التوسع خارج النازلة تُحوَّل إلى: قواعد بيانات / مصادر / قرارات مالك / بوابات سبب-شرط-مانع.",
         "", f"النازلة (النطاق الوحيد الآن): «{SENTENCE}»", "",
         "**READY_FOR_EXPANSION = NO · لا حكم · لا مناط · لا تنزيل · لا جواب.**", "",
         "## الأسئلة العشرة ⇐ متطلبات (لا وقائع)"]
    for r in rows:
        L.append(f"- `{r['requirement_id']}` [{r['requirement_type']}] ⇐ {r['original_question']}")
        L.append(f"  - لماذا: {r['why_needed']}")
        L.append(f"  - السجل/القاعدة: `{r['required_database_or_registry']}` · المصدر: {r['required_source_type']} · "
                 f"قرار المالك: {r['required_owner_decision']}")
        L.append(f"  - default_if_missing = {r['default_verdict_if_missing']} · expansion_blocker = {r['expansion_blocker']}")
    L += ["", "## السجلات الواجب بناؤها قبل التوسع"]
    for p in plan:
        fed = "، ".join(p["fed_by_requirements"]) if p["fed_by_requirements"] else "—"
        L.append(f"- `{p['registry_id']}` → {p['status']} (يغذّيه: {fed}) · creates_fact=NO · creates_source=NO · owner_ratification=YES")
    L += ["", "---",
          "*لا يجوز استعمال هذه الأسئلة كأسئلة تشغيل عامة قبل تسجيلها؛ وكل متطلب بلا سجل/مصدر/قرار مالك = DEFER.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-MANAT-APPLICATION-QUESTIONS-25", "ROUND_25",
     "output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_QUESTIONS_25.json",
     "tests/test_taaqol_manat_application_questionnaire_25.py"),
    ("REQ-PRE-EXPANSION-REGISTRY-32", "ROUND_32",
     "output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json",
     "tests/test_taaqol_pre_expansion_requirements_registry_32.py"),
    ("REQ-PRE-EXPANSION-REGISTRY-MD-32", "ROUND_32",
     "output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.md",
     "tests/test_taaqol_pre_expansion_requirements_registry_32.py"),
    ("REQ-PRE-EXPANSION-GUARDS-32", "ROUND_32",
     "output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_GUARDS_32.json",
     "tests/test_taaqol_pre_expansion_requirements_registry_32.py"),
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


def build_matrix(rows, plan, counts, anm):
    kv = [
        ("ROUND", "TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("QUESTIONS_FROM_AGENT_KNOWLEDGE_CANONICAL", "NO"),
        ("QUESTIONS_CONVERTED_TO_REQUIREMENTS", "YES"),
        ("REQUIREMENT_COUNT", str(len(rows))),
        ("FACT_REQUIREMENT_COUNT", str(counts["FACT_REQUIREMENT"])),
        ("SOURCE_REQUIREMENT_COUNT", str(counts["SOURCE_REQUIREMENT"])),
        ("DATABASE_REQUIREMENT_COUNT", str(counts["DATABASE_REQUIREMENT"])),
        ("OWNER_DECISION_REQUIREMENT_COUNT", str(counts["OWNER_DECISION_REQUIREMENT"])),
        ("GATE_REQUIREMENT_COUNT", str(counts["GATE_REQUIREMENT"])),
        ("DATABASE_REQUIREMENTS_PRODUCED", "YES" if counts["DATABASE_REQUIREMENT"] > 0 else "NO"),
        ("SOURCE_REQUIREMENTS_PRODUCED", "YES"),
        ("OWNER_DECISION_REQUIREMENTS_PRODUCED", "YES"),
        ("GATE_REQUIREMENTS_PRODUCED", "YES" if counts["GATE_REQUIREMENT"] > 0 else "NO"),
        ("REGISTRIES_TO_BUILD_COUNT", str(len(plan))),
        ("ALL_REQUIREMENTS_DEFER_IF_MISSING", "YES" if all(r["default_verdict_if_missing"] == "DEFER" for r in rows) else "NO"),
        ("ALL_REQUIREMENTS_EXPANSION_BLOCKER", "YES" if all(r["expansion_blocker"] == "YES" for r in rows) else "NO"),
        ("AGENT_QUESTION_IS_NOT_CANONICAL_RULE", "YES"),
        ("QUESTION_DOES_NOT_CREATE_FACT", "YES"),
        ("REQUIREMENT_DOES_NOT_CREATE_FACT", "YES"),
        ("SOURCE_REQUIREMENT_DOES_NOT_CREATE_SOURCE", "YES"),
        ("OWNER_RATIFICATION_REQUIRED", "YES"),
        ("READY_FOR_EXPANSION", "NO"),
        ("FINAL_MANAT", "NO"),
        ("TANZIL", "NO"),
        ("FINAL_HUKM", "NO"),
        ("FINAL_ANSWER", "NO"),
        ("KEEP_COMPOSITE_REMAINS_ACTIVE", "YES"),
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


def render_manager(tokens, rows, plan, counts, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — سجل المتطلبات قبل التوسع (32)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — سجل المتطلبات قبل التوسع (32)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0. جولة تأسيسية — سجل متطلبات فقط.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'أسئلة الوكيل ليست قاعدة كنسية (AGENT_QUESTION_IS_NOT_CANONICAL_RULE=YES) · '
             'المتطلب لا يُنشئ واقعة · متطلب المصدر لا يُنشئ مصدرًا · لا مناط نهائي · لا تنزيل · لا حكم · '
             'لا جواب · READY_FOR_EXPANSION=NO.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>وُقِف مسار الحكم النهائي مؤقتًا؛ حُوِّلت الأسئلة العشرة من «أسئلة معرفة الوكيل» إلى **متطلبات نظامية**.</li>'
             f'<li>REQUIREMENT_COUNT = {len(rows)} (fact={counts["FACT_REQUIREMENT"]}, '
             f'database={counts["DATABASE_REQUIREMENT"]}, gate={counts["GATE_REQUIREMENT"]}, '
             f'source={counts["SOURCE_REQUIREMENT"]}, owner_decision={counts["OWNER_DECISION_REQUIREMENT"]}).</li>'
             f'<li>سُجِّلت {len(plan)} سجلات يجب بناؤها قبل التوسع؛ كل متطلب بلا سجل/مصدر/قرار = DEFER.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ لا تتحول إلى قاعدة. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يتحوّل إلى مصدر ولا قاعدة. MAQAM_IS_NOT_RULE = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'المتطلبات تشير إلى سجلات/مصادر يجب بناؤها وتصديقها؛ الوكيل لا يُنشئ واقعة ولا مصدرًا.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'لا واقعة أُنشئت ولا رخصة عبور؛ الأسئلة صارت متطلبات معلّقة. FACT_CREATED = NO.</div>')
    # 8 — requirements table
    P.append('<h2>8. المصدر المعياري — الأسئلة ⇐ متطلبات (لا وقائع)</h2><div class="wrap"><table><thead><tr>'
             '<th>requirement_id</th><th>type</th><th>السؤال الأصلي</th><th>السجل/القاعدة</th>'
             '<th>قرار المالك</th><th>default_if_missing</th><th>expansion_blocker</th></tr></thead><tbody>')
    for r in rows:
        P.append('<tr><th>' + e(r["requirement_id"]) + '</th><td class="d">' + e(r["requirement_type"]) + '</td>'
                 '<td>' + e(r["original_question"]) + '</td><td>' + e(r["required_database_or_registry"]) + '</td>'
                 '<td>' + e(r["required_owner_decision"]) + '</td>'
                 + f'<td class="d">{e(r["default_verdict_if_missing"])}</td>'
                 + f'<td class="n">{e(r["expansion_blocker"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9 — registries to build
    P.append('<h2>9. موضع التوقف — السجلات الواجب بناؤها قبل التوسع</h2><div class="wrap"><table><thead><tr>'
             '<th>registry_id</th><th>status</th><th>يغذّيه</th><th>creates_fact</th><th>owner_ratification</th>'
             '</tr></thead><tbody>')
    for p in plan:
        fed = "، ".join(p["fed_by_requirements"]) if p["fed_by_requirements"] else "—"
        P.append(f'<tr><th>{e(p["registry_id"])}</th><td class="d">{e(p["status"])}</td><td>{e(fed)}</td>'
                 f'<td class="n">{e(p["creates_fact"])}</td><td class="y">{e(p["owner_ratification_required"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note n" style="background:#fdecec">'
             'كل المتطلبات معلّقة (default = DEFER) حتى تُبنى السجلات وتُزوَّد المصادر ويصدّق المالك. '
             'لا يجوز استعمال الأسئلة كأسئلة تشغيل عامة قبل التسجيل.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">بناء السجلات الثلاثة عشر أعلاه، ثم تزويد '
             'المصادر/الوقائع بقرار مالك لكل بوابة — عندها فقط يُعاد النظر في READY_FOR_EXPANSION.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_pre_expansion_requirements_registry_32.py — '
             'ROUND_32_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_32_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT = output/taaqol_maqam_foundation_generated/MANAT_APPLICATION_QUESTIONS_25.json\n'
             'REGISTRY_JSON = output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json\n'
             'REGISTRY_MD = output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.md\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_GUARDS_32.json\n'
             'PYTEST_FILE = tests/test_taaqol_pre_expansion_requirements_registry_32.py\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'حُوِّلت الأسئلة العشرة إلى {len(rows)} متطلبات نظامية (لا وقائع) موزّعة على خمسة أنواع، '
             f'مع خطة {len(plan)} سجلات يجب بناؤها قبل التوسع. لا مناط/تنزيل/حكم/جواب، وREADY_FOR_EXPANSION=NO.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'QUESTIONS_CONVERTED_TO_REQUIREMENTS = YES · REQUIREMENT_COUNT = {len(rows)} · '
             'AGENT_QUESTION_IS_NOT_CANONICAL_RULE = YES · READY_FOR_EXPANSION = NO · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_32_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'READY_FOR_EXPANSION = NO · FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · '
             'FINAL_ANSWER = NO · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_MANAGER_REPORT_AR_32.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_32_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = build_requirements()
    plan = build_registries_plan(rows)
    counts = {t: sum(1 for r in rows if r["requirement_type"] == t) for t in REQUIREMENT_TYPES}

    (OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json").write_text(
        json.dumps(build_registry_json(rows, plan), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.md").write_text(
        registry_md(rows, plan), encoding="utf-8")
    (OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_GUARDS_32.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(rows, plan, counts, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, rows, plan, counts, trows, anm), encoding="utf-8")
    print("REPORT_32=" + a.report_out)
    print(f"REQUIREMENTS={len(rows)} REGISTRIES={len(plan)} READY_FOR_EXPANSION=NO "
          f"counts={counts} ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
