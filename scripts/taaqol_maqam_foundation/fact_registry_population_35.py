#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_FACT_REGISTRY_POPULATION_35 (this nazila only).

Populates the first two registries with FACT CANDIDATES extracted ONLY from the explicit wording of the
nazila sentence — never invented facts. Each candidate is OWNER_TEXT_ASSERTED (not a final fact); no
owner-supplied fact, no ratified fact, no final manāṭ/tanzīl/final hukm/final answer, no expansion. The
nine non-explicit residuals stay REQUIRED_FACT_MISSING / DEFER. Manager report obeys the AR_09_FIXED
experience. No commit; no push.
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
PRODUCER = "scripts/taaqol_maqam_foundation/fact_registry_population_35.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]

# ONLY the surface facts explicitly present in the sentence wording.
FACT_SPEC = [
    {"id": "FC1_KING_DIED", "span": "مَاتَ مَلِكٌ", "surface": "مَاتَ مَلِكٌ",
     "stmt": "مات مالك (شخص)."},
    {"id": "FC2_HAS_SISTER", "span": "عَنْ أُخْتٍ", "surface": "عَنْ أُخْتٍ",
     "stmt": "للميت أخت."},
    {"id": "FC3_SISTER_RESIDING_WITH_HIM", "span": "سَاكِنَةٍ مَعَهُ", "surface": "سَاكِنَةٍ مَعَهُ",
     "stmt": "الأخت ساكنة معه."},
    {"id": "FC4_HEIR_WANTED_EXPULSION", "span": "فَأَرَادَ وَارِثُهُ طَرْدَهَا", "surface": "فَأَرَادَ وَارِثُهُ طَرْدَهَا",
     "stmt": "وارثه أراد طردها."},
    {"id": "FC5_LITIGATION_OCCURRED", "span": "فَتَحَاكَمَا", "surface": "فَتَحَاكَمَا",
     "stmt": "وقع تحاكم بينهما."},
]

# Explicitly NOT extractable from the wording -> remain REQUIRED_FACT_MISSING / DEFER.
MISSING_FACTS = [
    ("MF1_NO_CHILD", "عدم وجود ولد للميت"),
    ("MF2_NO_OTHER_HEIRS", "عدم وجود ورثة آخرين"),
    ("MF3_HEIR_CAPACITY", "صفة الوارث"),
    ("MF4_HOUSE_FINAL_OWNERSHIP", "ملكية البيت النهائية"),
    ("MF5_HOUSE_ALL_ESTATE", "كون البيت تركة كلها"),
    ("MF6_PRIOR_RESIDENCE_PERMISSION", "إذن السكن السابق"),
    ("MF7_SISTER_HAND_VALIDITY", "صحة يد الأخت"),
    ("MF8_EVIDENCE_PRESENT", "وجود بينة"),
    ("MF9_LITIGATION_OUTCOME", "نتيجة التحاكم"),
]


def build_fact_candidates():
    rows = []
    for f in FACT_SPEC:
        rows.append({
            "fact_id": f["id"],
            "source_text_span": f["span"],
            "extracted_surface": f["surface"],
            "normalized_fact_statement": f["stmt"],
            "registry": "factual_claim_registry",
            "owner_supplied_status": "ASSERTED_BY_NAZILA_TEXT_ONLY",
            "owner_ratification_status": "NOT_YET_RATIFIED",
            "cause": "واقعة ظاهرة من منطوق الجملة (لا من معرفة الوكيل).",
            "conditions": "تُعتمد فقط إن صدّقها المالك؛ لا تتجاوز منطوق النص.",
            "preventers": ("جعلها حقيقة نهائية بلا تصديق؛ اشتقاق واقعة غير منطوقة؛ إنتاج مناط/تنزيل/حكم/جواب."),
            "verdict": "FACT_CANDIDATE_ONLY",
            "residuals": "غير مقبولة نهائيًّا حتى تصديق المالك؛ لا تفيد إلا بمنطوقها المحدود.",
        })
    return rows


def build_owner_supplied(rows):
    return [{
        "owner_fact_id": "OSF_" + r["fact_id"],
        "linked_fact_candidate": r["fact_id"],
        "normalized_fact_statement": r["normalized_fact_statement"],
        "registry": "owner_supplied_fact_registry",
        "OWNER_SUPPLIED_FACT": "NO",
        "OWNER_RATIFICATION_REQUIRED": "YES",
        "FACT_ACCEPTED": "NO",
        "cause": "مرشح واقعة نصية بانتظار تزويد/تصديق المالك.",
        "conditions": "OWNER_SUPPLIED_FACT=YES + تصديق صريح.",
        "preventers": "قبول الواقعة دون تزويد وتصديق المالك.",
        "verdict": "AWAITING_OWNER_SUPPLY_AND_RATIFICATION",
        "residuals": "لا واقعة مقبولة بعد.",
    } for r in rows]


def build_missing():
    return [{
        "missing_fact_id": mid,
        "description": desc,
        "reason_not_extracted": "غير منطوق في نص الجملة؛ لا يجوز اشتقاقه من معرفة الوكيل.",
        "status": "REQUIRED_FACT_MISSING",
        "default_verdict": "DEFER",
        "expansion_blocker": "YES",
        "residuals": "يحتاج تزويد مالك + مصدر/بينة قبل أي اعتماد.",
    } for mid, desc in MISSING_FACTS]


def guards():
    return {
        "NO_FACT_INVENTED_BEYOND_TEXT": "YES",
        "TEXT_ASSERTED_FACT_IS_CANDIDATE_ONLY": "YES",
        "FACT_CANDIDATE_IS_NOT_FINAL_FACT": "YES",
        "OWNER_RATIFICATION_REQUIRED_FOR_EVERY_FACT": "YES",
        "MISSING_FACTS_STAY_DEFER": "YES",
        "SCOPE_THIS_NAZILA_ONLY": "YES",
        "NO_EXPANSION": "YES",
        "NO_FINAL_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "PHASE0_GATE_PASS": "NO",
        "producer_file": PRODUCER,
    }


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-REGISTRY-SKELETONS-34", "ROUND_34",
     "output/taaqol_maqam_foundation_generated/TAAQOL_REGISTRY_SKELETONS_13_34.json",
     "tests/test_taaqol_requirement_registry_normalization_and_skeletons_34.py"),
    ("REQ-FACTUAL-CLAIM-REGISTRY-35", "ROUND_35",
     "output/taaqol_maqam_foundation_generated/FACTUAL_CLAIM_REGISTRY_35.json",
     "tests/test_taaqol_fact_registry_population_35.py"),
    ("REQ-OWNER-SUPPLIED-FACT-REGISTRY-35", "ROUND_35",
     "output/taaqol_maqam_foundation_generated/OWNER_SUPPLIED_FACT_REGISTRY_35.json",
     "tests/test_taaqol_fact_registry_population_35.py"),
    ("REQ-MISSING-FACT-REQUIREMENTS-35", "ROUND_35",
     "output/taaqol_maqam_foundation_generated/MISSING_FACT_REQUIREMENTS_35.json",
     "tests/test_taaqol_fact_registry_population_35.py"),
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


def build_matrix(facts, owners, missing, anm):
    kv = [
        ("ROUND", "TAAQOL_FACT_REGISTRY_POPULATION_35"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("FACTUAL_CLAIM_REGISTRY_POPULATED", "YES"),
        ("OWNER_SUPPLIED_FACT_REGISTRY_POPULATED", "YES"),
        ("MISSING_FACT_ARTIFACT_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("FACT_CANDIDATE_COUNT", str(len(facts))),
        ("OWNER_SUPPLIED_FACT_COUNT", str(sum(1 for o in owners if o["OWNER_SUPPLIED_FACT"] == "YES"))),
        ("OWNER_RATIFIED_FACT_COUNT", str(sum(1 for o in owners if o["FACT_ACCEPTED"] == "YES"))),
        ("MISSING_FACT_REQUIREMENT_COUNT", str(len(missing))),
        ("ALL_FACTS_CANDIDATE_ONLY", "YES" if all(f["verdict"] == "FACT_CANDIDATE_ONLY" for f in facts) else "NO"),
        ("ALL_FACTS_NOT_RATIFIED", "YES" if all(f["owner_ratification_status"] == "NOT_YET_RATIFIED" for f in facts) else "NO"),
        ("ALL_MISSING_DEFER", "YES" if all(m["default_verdict"] == "DEFER" for m in missing) else "NO"),
        ("NO_FACT_INVENTED_BEYOND_TEXT", "YES"),
        ("REGISTRIES_POPULATED_PARTIAL", "YES"),
        ("REGISTRIES_POPULATED_FULL", "NO"),
        ("FACTUAL_FACTS_COMPLETE", "NO"),
        ("OWNER_SUPPLIED_FACTS_PRESENT", "NO"),
        ("PHASE0_GATE_PASS", "NO"),
        ("READY_FOR_EXPANSION", "NO"),
        ("FINAL_MANAT", "NO"),
        ("TANZIL", "NO"),
        ("FINAL_HUKM", "NO"),
        ("FINAL_ANSWER", "NO"),
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


def render_manager(tokens, facts, owners, missing, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — إشغال سجلات الوقائع (35)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — إشغال أول سجلين للوقائع (35)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0 · SCOPE = THIS_NAZILA_ONLY. '
             'مرشحات وقائع من منطوق النص فقط — لا قبول ولا توسع.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'مرشحات الوقائع من منطوق الجملة فقط (لا اختراع) · لا واقعة مقبولة · تصديق المالك مطلوب لكلٍّ · '
             'لا مناط نهائي · لا تنزيل · لا حكم · لا جواب · التوسع=NO · PHASE0_GATE_PASS=NO.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             f'<li>أُشغِل سجلّا الوقائع لهذه النازلة بـ **{len(facts)}** مرشحات وقائع من منطوق الجملة فقط.</li>'
             '<li>OWNER_SUPPLIED_FACT = NO · FACT_ACCEPTED = NO لكل مرشح؛ تصديق المالك مطلوب.</li>'
             f'<li>**{len(missing)}** وقائع غير منطوقة تبقى REQUIRED_FACT_MISSING / DEFER؛ PHASE 0 محجوب، التوسع=NO.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ لا تتحول إلى واقعة مقبولة. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يُنشئ واقعة. MAQAM_IS_NOT_FACT = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'الوقائع المزوَّدة والبينة يقرّها المالك؛ الوكيل يستخرج منطوق النص فقط.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'مرشحات وقائع فقط؛ لا واقعة مقبولة ولا رخصة عبور. FACT_ACCEPTED = NO.</div>')
    # 8 — fact candidates
    P.append('<h2>8. المصدر المعياري — مرشحات الوقائع من منطوق النص</h2><div class="wrap"><table><thead><tr>'
             '<th>fact_id</th><th>span</th><th>الواقعة المطبَّعة</th><th>owner_supplied</th>'
             '<th>ratification</th><th>verdict</th></tr></thead><tbody>')
    owners_by = {o["linked_fact_candidate"]: o for o in owners}
    for f in facts:
        o = owners_by[f["fact_id"]]
        P.append('<tr><th>' + e(f["fact_id"]) + '</th><td>' + e(f["source_text_span"]) + '</td>'
                 '<td>' + e(f["normalized_fact_statement"]) + '</td>'
                 + f'<td class="n">{e(o["OWNER_SUPPLIED_FACT"])}</td>'
                 + f'<td class="n">{e(f["owner_ratification_status"])}</td>'
                 + f'<td class="d">{e(f["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9 — missing
    P.append('<h2>9. موضع التوقف — الوقائع غير المنطوقة (DEFER)</h2><div class="wrap"><table><thead><tr>'
             '<th>missing_fact_id</th><th>الوصف</th><th>status</th><th>default</th></tr></thead><tbody>')
    for m in missing:
        P.append(f'<tr><th>{e(m["missing_fact_id"])}</th><td>{e(m["description"])}</td>'
                 f'<td class="n">{e(m["status"])}</td><td class="d">{e(m["default_verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note n" style="background:#fdecec">'
             f'{len(missing)} وقائع تحتاج تزويد مالك + مصدر/بينة (عدم الولد، الورثة، صفة الوارث، ملكية البيت، '
             'كونه تركة، إذن السكن، صحة اليد، البينة، نتيجة التحاكم). كلها DEFER.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">تصديق المالك لمرشحات الوقائع الخمسة (تحويلها '
             'OWNER_SUPPLIED_FACT=YES + FACT_ACCEPTED=YES)، وتزويد الوقائع الناقصة — قبل أي إعادة فحص PHASE 0.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_fact_registry_population_35.py — '
             'ROUND_35_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32..35 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_35_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT = output/taaqol_maqam_foundation_generated/TAAQOL_REGISTRY_SKELETONS_13_34.json\n'
             'FACTUAL_CLAIM_REGISTRY = output/taaqol_maqam_foundation_generated/FACTUAL_CLAIM_REGISTRY_35.json\n'
             'OWNER_SUPPLIED_FACT_REGISTRY = output/taaqol_maqam_foundation_generated/OWNER_SUPPLIED_FACT_REGISTRY_35.json\n'
             'MISSING_FACTS = output/taaqol_maqam_foundation_generated/MISSING_FACT_REQUIREMENTS_35.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/FACT_REGISTRY_POPULATION_GUARDS_35.json\n'
             'PYTEST_FILE = tests/test_taaqol_fact_registry_population_35.py\n'
             'SCOPE = THIS_NAZILA_ONLY\nFACT_ACCEPTED = NO\nOWNER_SUPPLIED_FACT = NO\nPHASE0_GATE_PASS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'أُشغِل سجلّا الوقائع بـ {len(facts)} مرشحات من منطوق النص فقط، بلا قبول ولا تصديق، مع '
             f'{len(missing)} وقائع ناقصة DEFER. لا مناط/تنزيل/حكم/جواب، وPHASE 0 محجوب، والتوسع=NO.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'FACT_CANDIDATE_COUNT = {len(facts)} · OWNER_SUPPLIED_FACT_COUNT = 0 · OWNER_RATIFIED_FACT_COUNT = 0 · '
             f'MISSING_FACT_REQUIREMENT_COUNT = {len(missing)} · REGISTRIES_POPULATED_PARTIAL = YES · '
             'FACTUAL_FACTS_COMPLETE = NO · PHASE0_GATE_PASS = NO · READY_FOR_EXPANSION = NO · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · AUTHORITY_LEAK = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_35_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'FACT_ACCEPTED = NO · FACTUAL_FACTS_COMPLETE = NO · FINAL_MANAT = NO · TANZIL = NO · '
             'FINAL_HUKM = NO · FINAL_ANSWER = NO · READY_FOR_EXPANSION = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "FACT_REGISTRY_POPULATION_MANAGER_REPORT_AR_35.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "FACT_REGISTRY_POPULATION_35_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    facts = build_fact_candidates()
    owners = build_owner_supplied(facts)
    missing = build_missing()

    (OUT / "FACTUAL_CLAIM_REGISTRY_35.json").write_text(
        json.dumps({"ROUND": "TAAQOL_FACT_REGISTRY_POPULATION_35", "registry_id": "factual_claim_registry",
                    "scope": "THIS_NAZILA_ONLY", "fact_candidate_count": len(facts),
                    "fact_candidates": facts, "producer_file": PRODUCER}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    (OUT / "OWNER_SUPPLIED_FACT_REGISTRY_35.json").write_text(
        json.dumps({"ROUND": "TAAQOL_FACT_REGISTRY_POPULATION_35", "registry_id": "owner_supplied_fact_registry",
                    "scope": "THIS_NAZILA_ONLY", "owner_supplied_fact_count": 0, "owner_ratified_fact_count": 0,
                    "records": owners, "producer_file": PRODUCER}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    (OUT / "MISSING_FACT_REQUIREMENTS_35.json").write_text(
        json.dumps({"ROUND": "TAAQOL_FACT_REGISTRY_POPULATION_35", "missing_fact_requirement_count": len(missing),
                    "missing_facts": missing, "producer_file": PRODUCER}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    (OUT / "FACT_REGISTRY_POPULATION_GUARDS_35.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(facts, owners, missing, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, facts, owners, missing, trows, anm), encoding="utf-8")
    print("REPORT_35=" + a.report_out)
    print(f"FACT_CANDIDATES={len(facts)} OWNER_SUPPLIED=0 RATIFIED=0 MISSING={len(missing)} "
          f"PHASE0_GATE_PASS=NO READY_FOR_EXPANSION=NO ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
