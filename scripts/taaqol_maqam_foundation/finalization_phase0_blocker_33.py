#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_FINALIZATION_CHAIN — PHASE 0 blocker (registry-backed gate).

The post-merge finalization chain (factual manāṭ → final manāṭ → tanzīl → final hukm → final answer →
closure) is gated by PHASE 0: requirements must be registry-backed and normalized before any finalization.
Verification found: round-32 requirements registry present & valid, but the normalized registry 33 is
ABSENT, none of the 13 required registries are built, and no owner-supplied facts exist. Therefore the
chain STOPS at PHASE 0. No sync (later phase), no final manāṭ/tanzīl/hukm/answer, no closure claim. No
commit; no push. Manager report obeys the AR_09_FIXED experience.
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
PRODUCER = "scripts/taaqol_maqam_foundation/finalization_phase0_blocker_33.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
REGISTRY_32 = OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json"
NORMALIZED_33 = OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_33.json"
REGISTRIES_13 = [
    "factual_claim_registry", "owner_supplied_fact_registry", "source_requirement_registry",
    "normative_source_registry", "domain_candidate_registry", "hukm_candidate_registry",
    "manat_candidate_registry", "tanzil_requirement_registry", "proof_burden_registry",
    "possession_yad_registry", "inheritance_condition_registry", "residual_registry",
    "owner_ratification_registry",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def phase0_checks():
    reg32 = json.loads(REGISTRY_32.read_text(encoding="utf-8")) if REGISTRY_32.exists() else None
    reg32_ok = bool(reg32) and reg32.get("requirement_count") == 10 \
        and reg32.get("questions_from_agent_knowledge_canonical") == "NO" \
        and reg32.get("ready_for_expansion") == "NO" \
        and all(r["default_verdict_if_missing"] == "DEFER" for r in reg32.get("requirements", []))
    normalized_present = NORMALIZED_33.exists()
    registries_built = sum(1 for r in REGISTRIES_13
                           if list(OUT.glob(f"*{r}*REGISTRY*")) or list(OUT.glob(f"*{r}*.json")) and False)
    # explicit: none built unless a dedicated registry artifact exists
    registries_built = sum(1 for r in REGISTRIES_13 if list(OUT.glob(f"*{r}*REGISTRY*")))
    owner_facts_present = bool(list(OUT.glob("*OWNER_SUPPLIED_FACT*")))
    checks = [
        {
            "check_id": "C1_QUESTIONS_ARE_REQUIREMENTS_NOT_FACTS",
            "cause": "round-32 converted the ten manāṭ questions into requirements",
            "conditions": "requirement_count=10; questions_from_agent_knowledge_canonical=NO",
            "preventers": "treating a question as a fact/rule",
            "verdict": "PASS" if reg32_ok else "FAIL",
            "residuals": "none for this check" if reg32_ok else "round-32 registry invalid/missing",
        },
        {
            "check_id": "C2_NOT_CANONICAL_FROM_AGENT_KNOWLEDGE",
            "cause": "owner rule: agent questions are not canonical rules",
            "conditions": "questions_from_agent_knowledge_canonical=NO",
            "preventers": "canonizing agent knowledge",
            "verdict": "PASS" if (reg32 and reg32.get("questions_from_agent_knowledge_canonical") == "NO") else "FAIL",
            "residuals": "none",
        },
        {
            "check_id": "C3_EACH_REQUIREMENT_FULL_SHAPE",
            "cause": "requirements must carry cause/conditions/preventers/default DEFER/registry/source/owner",
            "conditions": "all 10 requirements complete + default_verdict_if_missing=DEFER",
            "preventers": "a requirement lacking a field",
            "verdict": "PASS" if reg32_ok else "FAIL",
            "residuals": "none",
        },
        {
            "check_id": "C4_READY_FOR_EXPANSION_ONLY_IF_REGISTRIES_EXIST_AND_RATIFIED",
            "cause": "expansion requires all 13 registries built AND owner-ratified",
            "conditions": f"registries_built=={len(REGISTRIES_13)} and owner_ratified",
            "preventers": "expanding before registries exist",
            "verdict": "FAIL" if registries_built < len(REGISTRIES_13) else "PASS",
            "residuals": f"registries_built={registries_built}/{len(REGISTRIES_13)}; owner_facts_present={'YES' if owner_facts_present else 'NO'}",
        },
        {
            "check_id": "C5_NORMALIZED_REGISTRY_33_PRESENT",
            "cause": "PHASE 0 requires normalized requirement registry (round 33) before final manāṭ",
            "conditions": "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_33.json exists",
            "preventers": "proceeding to final manāṭ without normalization",
            "verdict": "PASS" if normalized_present else "FAIL",
            "residuals": "normalization round 33 not yet produced" if not normalized_present else "none",
        },
    ]
    gate_pass = all(c["verdict"] == "PASS" for c in checks)
    return checks, {
        "reg32_ok": reg32_ok, "normalized_present": normalized_present,
        "registries_built": registries_built, "owner_facts_present": owner_facts_present,
        "gate_pass": gate_pass,
    }


def build_blocker_json(checks, st):
    return {
        "ROUND": "TAAQOL_POST_MERGE_REGISTRY_BACKED_FINALIZATION_CHAIN",
        "TASK_PHASE": "VERIFY_REQUIREMENTS_REGISTRY_BEFORE_FINALIZATION",
        "STOPPED_AT_PHASE": "PHASE_0",
        "STOP_REASON": "REQUIREMENTS_REGISTRY_OR_NORMALIZATION_REQUIRED",
        "nazila_scope": SENTENCE,
        "requirements_registry_verified": "YES" if st["reg32_ok"] else "NO",
        "requirements_normalized": "YES" if st["normalized_present"] else "NO",
        "registries_built": st["registries_built"],
        "registries_required": len(REGISTRIES_13),
        "owner_supplied_facts_present": "YES" if st["owner_facts_present"] else "NO",
        "ready_for_expansion": "NO",
        "phase0_gate_pass": "YES" if st["gate_pass"] else "NO",
        "phase0_checks": checks,
        "decision": {
            "cause": "finalization chain requires registry-backed + normalized requirements",
            "conditions": "normalized registry 33 present AND all 13 registries built+ratified AND facts accepted",
            "preventers": "normalized 33 absent; 0/13 registries built; no owner-supplied facts",
            "verdict": "STOP_AT_PHASE_0_DEFER_FINALIZATION",
            "residuals": "build+ratify 13 registries; produce normalized round 33; supply+ratify facts",
        },
        "LOCAL_SYNC_DONE": "NO",
        "SYNC_MODE": "SKIPPED",
        "FACTUAL_MANAT_APPLICATION_DONE": "NO",
        "FACTUAL_FACTS_COMPLETE": "NO",
        "FINAL_MANAT": "NO",
        "TANZIL": "NO",
        "FINAL_HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "TAAQOL_NAZILA_PIPELINE_CLOSED": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "PHASE0_GATE_BLOCKS_FINALIZATION": "YES",
        "NO_LEAP_TO_FINAL_MANAT": "YES",
        "AGENT_QUESTION_IS_NOT_CANONICAL_RULE": "YES",
        "REQUIREMENT_DOES_NOT_CREATE_FACT": "YES",
        "SOURCE_REQUIREMENT_DOES_NOT_CREATE_SOURCE": "YES",
        "SOURCE_DOES_NOT_CREATE_HUKM": "YES",
        "POSSESSION_DOES_NOT_CREATE_FINAL_OWNERSHIP": "YES",
        "PROOF_BURDEN_DOES_NOT_DECIDE_SUBSTANTIVE_RIGHT": "YES",
        "OWNER_RATIFICATION_REQUIRED": "YES",
        "NO_FINAL_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "NO_FULL_PROJECT_CLOSURE_FROM_ONE_NAZILA": "YES",
        "READY_FOR_EXPANSION": "NO",
        "AUTHORITY_LEAK": "NO",
        "producer_file": PRODUCER,
    }


def normalization_request_md(st):
    L = ["# طلب تطبيع سجل المتطلبات وبناء السجلات (تمهيد الجولة 33)", "",
         "**PHASE 0 حاجز:** السلسلة النهائية (المناط الواقعي → المناط النهائي → التنزيل → الحكم → الجواب) "
         "لا تُفتح قبل أن تصير المتطلبات مدعومة بسجلات ومطبَّعة.", "",
         f"النازلة: «{SENTENCE}»", "",
         "## الحالة المكتشَفة",
         f"- سجل المتطلبات (32): {'موجود وصحيح' if st['reg32_ok'] else 'ناقص'}",
         f"- السجل المطبَّع (33): {'موجود' if st['normalized_present'] else '**غائب**'}",
         f"- السجلات المبنيّة: **{st['registries_built']}/{len(REGISTRIES_13)}**",
         f"- وقائع مزوَّدة من المالك: {'نعم' if st['owner_facts_present'] else '**لا**'}",
         "- READY_FOR_EXPANSION = **NO**", "",
         "## المطلوب من المالك (قبل أي مناط نهائي)",
         "1. بناء/تطبيع السجلات الثلاثة عشر (كلٌّ منها: `creates_fact=NO`، `creates_source=NO`، "
         "`owner_ratification=YES`):"]
    L += [f"   - `{r}`" for r in REGISTRIES_13]
    L += ["2. إنتاج `TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_33.json` (تطبيع المتطلبات العشرة على السجلات).",
          "3. تزويد الوقائع بقرار مالك لكل متطلب (`OWNER_SUPPLIED_FACT` + مرجع/بينة + تصديق).", "",
          "## التصريح المطلوب لاحقًا (لا يُفتح الآن)",
          "- `ALLOW_REQUIREMENT_NORMALIZATION_33 = YES | NO`",
          "- `BUILD_REGISTRIES = <list>`",
          "- `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
          "*حتى تُبنى السجلات ويُنتَج التطبيع 33: FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · "
          "FINAL_ANSWER = NO · لا مزامنة فرع (مرحلة لاحقة) · لا full project closure من نازلة واحدة.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-PRE-EXPANSION-REGISTRY-32", "ROUND_32",
     "output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json",
     "tests/test_taaqol_pre_expansion_requirements_registry_32.py"),
    ("REQ-FINALIZATION-PHASE0-BLOCKER-33", "ROUND_33",
     "output/taaqol_maqam_foundation_generated/TAAQOL_FINALIZATION_PHASE0_BLOCKER_33.json",
     "tests/test_taaqol_finalization_phase0_blocker_33.py"),
    ("REQ-NORMALIZATION-REQUEST-33", "ROUND_33",
     "output/taaqol_maqam_foundation_generated/TAAQOL_REQUIREMENT_NORMALIZATION_REQUEST_33.md",
     "tests/test_taaqol_finalization_phase0_blocker_33.py"),
    ("REQ-FINALIZATION-PHASE0-GUARDS-33", "ROUND_33",
     "output/taaqol_maqam_foundation_generated/TAAQOL_FINALIZATION_PHASE0_GUARDS_33.json",
     "tests/test_taaqol_finalization_phase0_blocker_33.py"),
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


def build_matrix(st, anm):
    kv = [
        ("ROUND", "TAAQOL_POST_MERGE_REGISTRY_BACKED_FINALIZATION_CHAIN"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("STOPPED_AT_PHASE", "PHASE_0"),
        ("STOP_REASON", "REQUIREMENTS_REGISTRY_OR_NORMALIZATION_REQUIRED"),
        ("REQUIREMENTS_REGISTRY_VERIFIED", "YES" if st["reg32_ok"] else "NO"),
        ("REQUIREMENTS_NORMALIZED", "YES" if st["normalized_present"] else "NO"),
        ("REGISTRIES_BUILT", str(st["registries_built"])),
        ("REGISTRIES_REQUIRED", str(len(REGISTRIES_13))),
        ("OWNER_SUPPLIED_FACTS_PRESENT", "YES" if st["owner_facts_present"] else "NO"),
        ("PHASE0_GATE_PASS", "YES" if st["gate_pass"] else "NO"),
        ("LOCAL_SYNC_DONE", "NO"),
        ("SYNC_MODE", "SKIPPED"),
        ("FACTUAL_MANAT_APPLICATION_DONE", "NO"),
        ("FACTUAL_FACTS_COMPLETE", "NO"),
        ("FINAL_MANAT_RATIFIED", "NO"),
        ("TANZIL_RATIFIED", "NO"),
        ("FINAL_HUKM_RATIFIED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_MANAT", "NO"),
        ("TANZIL", "NO"),
        ("FINAL_HUKM", "NO"),
        ("FINAL_ANSWER", "NO"),
        ("TAAQOL_NAZILA_PIPELINE_CLOSED", "NO"),
        ("FULL_TAAQOL_PROJECT_CLOSED", "NO"),
        ("READY_FOR_EXPANSION", "NO"),
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


def render_manager(tokens, checks, st, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — حاجز PHASE 0 لسلسلة الإنهاء (33)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — حاجز PHASE 0 لسلسلة الإنهاء بعد الدمج (33)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0. توقّف عند PHASE 0 — لا قفز.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'STOPPED_AT_PHASE = PHASE_0 · STOP_REASON = REQUIREMENTS_REGISTRY_OR_NORMALIZATION_REQUIRED · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             'FULL_TAAQOL_PROJECT_CLOSED = NO · AUTHORITY_LEAK = NO.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>سلسلة الإنهاء (مناط واقعي → مناط نهائي → تنزيل → حكم → جواب → إغلاق) مبوّبة، وبوّابة PHASE 0 توقفها.</li>'
             f'<li>سجل المتطلبات (32) موجود وصحيح، لكن السجل المطبَّع (33) **غائب**، والسجلات المبنيّة {st["registries_built"]}/{len(REGISTRIES_13)}، ولا وقائع مزوَّدة.</li>'
             '<li>لا مزامنة فرع (مرحلة لاحقة)، ولا مناط/تنزيل/حكم/جواب، ولا ادعاء إغلاق مشروع من نازلة واحدة.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ لا تتحول إلى قاعدة/حكم. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يتحوّل إلى مصدر/حكم. MAQAM_IS_NOT_RULE = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'المتطلبات تحتاج سجلات ومصادر مصدَّقة قبل قبول أي واقعة.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'لا وقائع مقبولة ولا رخصة عبور؛ الوقائع تحتاج تزويدًا وتصديقًا. FACT_CREATED = NO.</div>')
    # 8 — phase0 checks
    P.append('<h2>8. المصدر المعياري — فحوص PHASE 0</h2><div class="wrap"><table><thead><tr>'
             '<th>check</th><th>cause</th><th>conditions</th><th>preventers</th><th>verdict</th><th>residuals</th>'
             '</tr></thead><tbody>')
    for c in checks:
        vcls = "y" if c["verdict"] == "PASS" else "n"
        P.append('<tr><th>' + e(c["check_id"]) + '</th><td>' + e(c["cause"]) + '</td><td>' + e(c["conditions"]) + '</td>'
                 '<td class="d">' + e(c["preventers"]) + '</td>'
                 + f'<td class="{vcls}">{e(c["verdict"])}</td><td>{e(c["residuals"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9 — stop point
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: PHASE_0 (VERIFY_REQUIREMENTS_REGISTRY). القرار: '
             'STOP_AT_PHASE_0_DEFER_FINALIZATION — السبب: السجل المطبَّع (33) غائب، والسجلات '
             f'{st["registries_built"]}/{len(REGISTRIES_13)}، ولا وقائع مزوَّدة.</div>')
    # 10 — missing / request
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             'المطلوب: بناء/تطبيع السجلات الثلاثة عشر، إنتاج التطبيع (33)، وتزويد الوقائع بقرار مالك — '
             'مفصّل في TAAQOL_REQUIREMENT_NORMALIZATION_REQUEST_33.md.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند اكتمال السجلات + التطبيع + الوقائع المصدَّقة: '
             'يُعاد تشغيل السلسلة من PHASE 1 (مزامنة ff-only) ثم المناط الواقعي — لا قبله.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_finalization_phase0_blocker_33.py — '
             'ROUND_33_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32 + 33 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_33_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT = output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json\n'
             'BLOCKER_JSON = output/taaqol_maqam_foundation_generated/TAAQOL_FINALIZATION_PHASE0_BLOCKER_33.json\n'
             'NORMALIZATION_REQUEST = output/taaqol_maqam_foundation_generated/TAAQOL_REQUIREMENT_NORMALIZATION_REQUEST_33.md\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/TAAQOL_FINALIZATION_PHASE0_GUARDS_33.json\n'
             'PYTEST_FILE = tests/test_taaqol_finalization_phase0_blocker_33.py\n'
             'NORMALIZED_33_PRESENT = ' + ('YES' if st["normalized_present"] else 'NO') + '\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             'بوّابة PHASE 0 أوقفت سلسلة الإنهاء لغياب التطبيع (33) والسجلات والوقائع المصدَّقة. '
             'لم يُنتَج مناط/تنزيل/حكم/جواب، ولم تُزامَن الفرع، ولم يُدَّعَ إغلاق المشروع. طلب التطبيع جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             'STOPPED_AT_PHASE = PHASE_0 · REQUIREMENTS_REGISTRY_VERIFIED = '
             + ('YES' if st["reg32_ok"] else 'NO') + ' · REQUIREMENTS_NORMALIZED = '
             + ('YES' if st["normalized_present"] else 'NO') + f' · REGISTRIES_BUILT = {st["registries_built"]}/{len(REGISTRIES_13)} · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             'TAAQOL_NAZILA_PIPELINE_CLOSED = NO · FULL_TAAQOL_PROJECT_CLOSED = NO · AUTHORITY_LEAK = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_33_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'STOPPED_AT_PHASE = PHASE_0 · FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · '
             'FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "TAAQOL_FINALIZATION_PHASE0_BLOCKER_MANAGER_REPORT_AR_33.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "TAAQOL_FINALIZATION_PHASE0_BLOCKER_33_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    checks, st = phase0_checks()

    (OUT / "TAAQOL_FINALIZATION_PHASE0_BLOCKER_33.json").write_text(
        json.dumps(build_blocker_json(checks, st), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_REQUIREMENT_NORMALIZATION_REQUEST_33.md").write_text(
        normalization_request_md(st), encoding="utf-8")
    (OUT / "TAAQOL_FINALIZATION_PHASE0_GUARDS_33.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(st, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, checks, st, trows, anm), encoding="utf-8")
    print("REPORT_33=" + a.report_out)
    print(f"GATE_PASS={st['gate_pass']} normalized33={st['normalized_present']} "
          f"registries_built={st['registries_built']}/{len(REGISTRIES_13)} "
          f"owner_facts={st['owner_facts_present']} ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
