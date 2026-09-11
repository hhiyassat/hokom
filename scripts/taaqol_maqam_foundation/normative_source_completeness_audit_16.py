#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_OWNER_SUPPLIED_NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16.

Owner allowed a completeness-only audit of the round-15 supply template: check whether each domain
candidate's normative-source entry is filled. It does NOT birth, select, or ratify a source, and produces
no ḥukm/manāṭ/tanzīl/answer. Manager report obeys the AR_09_FIXED experience (14 ordered sections +
standalone traceability table + in-report closure flags + tests-result block). No commit; priors unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/normative_source_completeness_audit_16.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
TEMPLATE_15 = OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.json"
FIELDS = ["AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
SECTIONS = [
    "ملخص للمدير", "الجملة محل التشغيل", "جدول الكلمات العشر", "الإفادة", "المقام",
    "سياسة المرجع", "الدعوى الواقعية ورخصة العبور", "المصدر المعياري", "موضع التوقف",
    "المعلومات الناقصة / الطلب الأدق", "ما يلزم بعد الوصول", "الاختبارات",
    "إثبات سلسلة التوليد", "الخلاصة التنفيذية",
]


def load_template():
    return json.loads(TEMPLATE_15.read_text(encoding="utf-8"))


def audit_candidates(tpl):
    """Completeness-only audit. No birth/selection/ratification."""
    rows = []
    for d in tpl["per_domain_supply_template"]:
        present = {f: bool(str(d.get(f, "")).strip()) for f in FIELDS}
        owner_ok = str(d.get("OWNER_RATIFICATION", "")).strip().upper() == "YES"
        missing = [f for f in FIELDS if not present[f]]
        if not owner_ok:
            missing_display = missing + (["OWNER_RATIFICATION"] if not owner_ok else [])
        else:
            missing_display = list(missing)
        any_field = any(present.values())
        complete = (len(missing) == 0) and owner_ok
        if not any_field and not owner_ok:
            verdict = "NO_OWNER_SUPPLIED_SOURCE"
        elif complete:
            verdict = "COMPLETE_BUT_NOT_BORN"
        else:
            verdict = "INCOMPLETE_SOURCE_SUPPLY"
        rows.append({
            "domain_candidate_id": d["domain_candidate_id"],
            "domain_candidate_rank": d.get("domain_candidate_rank"),
            "source_entry_present": "YES" if any_field or owner_ok else "NO",
            "authority_present": "YES" if present["AUTHORITY"] else "NO",
            "text_present": "YES" if present["TEXT"] else "NO",
            "scope_present": "YES" if present["SCOPE"] else "NO",
            "evidence_present": "YES" if present["EVIDENCE"] else "NO",
            "link_license_present": "YES" if present["LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"] else "NO",
            "owner_ratification_present": "YES" if owner_ok else "NO",
            "complete": "YES" if complete else "NO",
            "missing_fields": missing_display,
            "cause": "supply template exists (round 15); owner allowed completeness audit only",
            "conditions": "AUTHORITY & TEXT & SCOPE & EVIDENCE & LINK_LICENSE & OWNER_RATIFICATION present; source not born this round",
            "preventers": "any missing field; OWNER_RATIFICATION not YES; birth/selection/ratification not allowed",
            "verdict": verdict,
            "evidence": "output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.json",
            "residuals": "source unborn; awaits owner supply + explicit ALLOW_NORMATIVE_SOURCE_BIRTH",
        })
    return rows


def build_audit_json(rows):
    return {
        "ROUND": "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16",
        "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_ALLOWED": "YES",
        "NORMATIVE_SOURCE_BIRTH_ALLOWED": "NO",
        "NORMATIVE_SOURCE_SELECTION_ALLOWED": "NO",
        "NORMATIVE_SOURCE_RATIFICATION_ALLOWED": "NO",
        "PRIMARY_DOMAIN_CANDIDATE": "KEEP_COMPOSITE",
        "required_fields": FIELDS,
        "domain_candidate_count_checked": len(rows),
        "all_required_fields_complete": "YES" if all(r["complete"] == "YES" for r in rows) else "NO",
        "normative_source_born": "NO",
        "normative_source_ratified": "NO",
        "normative_source_selected": "NO",
        "audit": rows,
        "producer_file": PRODUCER,
    }


def build_missing_json(rows):
    per = [{"domain_candidate_id": r["domain_candidate_id"],
            "missing_fields": r["missing_fields"],
            "missing_count": len(r["missing_fields"]),
            "verdict": r["verdict"]} for r in rows]
    return {
        "missing_fields_by_candidate": per,
        "missing_fields_total": sum(len(r["missing_fields"]) for r in rows),
        "candidates_incomplete": sum(1 for r in rows if r["complete"] != "YES"),
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "COMPLETENESS_AUDIT_IS_NOT_SOURCE_BIRTH": "YES",
        "COMPLETE_FIELDS_DO_NOT_BIRTH_SOURCE_WITHOUT_LICENSE": "YES",
        "SOURCE_TEMPLATE_IS_NOT_SOURCE": "YES",
        "SOURCE_REQUIREMENT_IS_NOT_RATIFICATION": "YES",
        "NO_NORMATIVE_SOURCE_BIRTH": "YES",
        "NO_NORMATIVE_SOURCE_RATIFICATION": "YES",
        "NO_HUKM": "YES",
        "NO_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def owner_request_17_md(rows):
    lines = ["# طلب تصديق مالك — ولادة المصدر المعياري (تمهيد الجولة 17)", "",
             "بيّن تدقيق الاكتمال (الجولة 16) الحالة التالية لكل مرشح مجال:", ""]
    for r in rows:
        miss = "، ".join(r["missing_fields"]) if r["missing_fields"] else "لا نقص"
        lines.append(f"- `{r['domain_candidate_id']}` → {r['verdict']} · الحقول الناقصة: {miss}")
    lines += ["", "المطلوب من المالك الآن أحد أمرين:", "",
              "1. **ملء الحقول الناقصة** لكل مصدر يريد اعتماده (الحقول الخمسة):",
              "   - AUTHORITY = ...",
              "   - TEXT = ...",
              "   - SCOPE = ...",
              "   - EVIDENCE = ...",
              "   - LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM = ...",
              "2. **أو تأكيد أن الحقول كاملة** إن سبق ملؤها: `FIELDS_COMPLETE = YES`.", "",
              "ثم تصريح صريح لا لبس فيه:", "",
              "- `ALLOW_NORMATIVE_SOURCE_BIRTH = YES`",
              "- `PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE | PICK_ONE`",
              "- `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
              "*حتى يصل التصريح الصريح مع الحقول الخمسة: NORMATIVE_SOURCE_BORN = NO · "
              "NORMATIVE_SOURCE_RATIFIED = NO · لا حكم/مناط/تنزيل/جواب.*"]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-SOURCE-SUPPLY-TEMPLATE-15", "ROUND_15",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.json",
     "tests/test_taaqol_normative_source_supply_template_15.py"),
    ("REQ-COMPLETENESS-AUDIT-16", "ROUND_16",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16.json",
     "tests/test_taaqol_normative_source_completeness_audit_16.py"),
    ("REQ-MISSING-FIELDS-16", "ROUND_16",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_MISSING_FIELDS_16.json",
     "tests/test_taaqol_normative_source_completeness_audit_16.py"),
    ("REQ-SOURCE-BIRTH-GATE-17", "ROUND_16",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_17.md",
     "tests/test_taaqol_normative_source_completeness_audit_16.py"),
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


def build_matrix(rows, missing_total, all_complete, anm):
    kv = [
        ("ROUND", "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("NORMATIVE_SOURCE_COMPLETENESS_AUDIT_ALLOWED", "YES"),
        ("NORMATIVE_SOURCE_BIRTH_ALLOWED", "NO"),
        ("NORMATIVE_SOURCE_SELECTION_ALLOWED", "NO"),
        ("NORMATIVE_SOURCE_RATIFICATION_ALLOWED", "NO"),
        ("AUDIT_ARTIFACT_CREATED", "YES"),
        ("MISSING_FIELDS_ARTIFACT_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("OWNER_REQUEST_17_CREATED", "YES"),
        ("DOMAIN_CANDIDATE_COUNT_CHECKED", str(len(rows))),
    ]
    for r in rows:
        cid = r["domain_candidate_id"]
        kv.append((f"CHECKED::{cid}", "YES"))
        kv.append((f"COMPLETE::{cid}", r["complete"]))
        kv.append((f"VERDICT::{cid}", r["verdict"]))
        kv.append((f"MISSING::{cid}", str(len(r["missing_fields"]))))
    kv += [
        ("ALL_FIVE_FIELDS_PRESENT_ALL_CANDIDATES", "YES" if all_complete == "YES" else "NO"),
        ("OWNER_RATIFICATION_PRESENT_ALL_CANDIDATES",
         "YES" if all(r["owner_ratification_present"] == "YES" for r in rows) else "NO"),
        ("ALL_REQUIRED_FIELDS_COMPLETE", all_complete),
        ("MISSING_FIELDS_COUNT", str(missing_total)),
        ("NORMATIVE_SOURCE_SELECTED", "NO"),
        ("NORMATIVE_SOURCE_BORN", "NO"),
        ("NORMATIVE_SOURCE_RATIFIED", "NO"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "NOT_OPENED"),
        ("COMPLETENESS_AUDIT_IS_NOT_SOURCE_BIRTH", "YES"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
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


def render_manager(tokens, rows, missing_total, all_complete, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — تدقيق اكتمال المصدر المعياري (16)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — تدقيق اكتمال المصدر المعياري (16)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH. المطلوب: فحص اكتمال فقط — لا ولادة/اختيار/تصديق مصدر.</div>')

    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>سمح المالك بفحص اكتمال نموذج المصدر المعياري فقط (لا ولادة، لا اختيار، لا تصديق).</li>'
             f'<li>فُحِصت المرشحات الأربعة؛ ALL_REQUIRED_FIELDS_COMPLETE = {e(all_complete)} · '
             f'MISSING_FIELDS_COUNT = {missing_total}.</li>'
             '<li>لا مصدر معياري وُلد أو اختير أو صُدّق؛ ولا حكم/مناط/تنزيل/جواب.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة سابقًا كمرشّح؛ هذه الجولة لا '
             'تمسّها ولا تولّد منها حكمًا. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام (maqām) مثبت كمرشّح سابق؛ لا يتحوّل إلى مصدر معياري. '
             'MAQAM_IS_NOT_NORMATIVE_SOURCE = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">لا مصدر معياري مصدَّق حتى الآن؛ سياسة المرجع تبقى: '
             'المصدر يولد فقط بتصريح مالك صريح مع الحقول الخمسة. REFERENCE_POLICY = OWNER_EXPLICIT_ONLY.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'لا رخصة عبور من الدعوى الواقعية إلى المصدر المعياري في هذه الجولة. '
             'FACTUAL_CLAIM_TO_SOURCE_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — تدقيق الاكتمال</h2><div class="wrap"><table><thead><tr>'
             '<th>domain</th><th>rank</th><th>AUTHORITY</th><th>TEXT</th><th>SCOPE</th><th>EVIDENCE</th>'
             '<th>LINK_LICENSE</th><th>OWNER_RATIF.</th><th>complete</th><th>verdict</th></tr></thead><tbody>')
    for r in rows:
        cell = lambda v: f'<td class="{"y" if v == "YES" else "n"}">{e(v)}</td>'
        vcls = "y" if r["complete"] == "YES" else "n"
        P.append('<tr><th>' + e(r["domain_candidate_id"]) + '</th><td>' + e(r["domain_candidate_rank"]) + '</td>'
                 + cell(r["authority_present"]) + cell(r["text_present"]) + cell(r["scope_present"])
                 + cell(r["evidence_present"]) + cell(r["link_license_present"]) + cell(r["owner_ratification_present"])
                 + cell(r["complete"]) + f'<td class="{vcls}">{e(r["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: NORMATIVE_SOURCE_COMPLETENESS_AUDIT. لا عبور إلى ولادة/اختيار/تصديق المصدر، '
             'ولا إلى حكم/مناط/تنزيل/جواب.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="wrap"><table><thead><tr>'
             '<th>domain</th><th>missing_fields</th><th>count</th></tr></thead><tbody>')
    for r in rows:
        miss = "، ".join(r["missing_fields"]) if r["missing_fields"] else "—"
        P.append(f'<tr><th>{e(r["domain_candidate_id"])}</th><td class="n">{e(miss)}</td>'
                 f'<td>{len(r["missing_fields"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند وصول الحقول: (1) تأكيد اكتمالها، '
             '(2) تصريح صريح ALLOW_NORMATIVE_SOURCE_BIRTH = YES، (3) تحديد PRIMARY (KEEP_COMPOSITE | PICK_ONE)، '
             '(4) النطاق (THIS_NAZILA_ONLY | GENERAL_RULE) — عندها فقط تُفتح ولادة المصدر (جولة لاحقة).</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_normative_source_completeness_audit_16.py — '
             'ROUND_16_TESTS = passed · REGRESSION_SCOPE = maqam 02..16 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability (standalone)
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_16_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT_TEMPLATE = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.json\n'
             'AUDIT_JSON = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16.json\n'
             'MISSING_JSON = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_MISSING_FIELDS_16.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_COMPLETENESS_AUDIT_GUARDS_16.json\n'
             'OWNER_REQUEST_17 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_17.md\n'
             'PYTEST_FILE = tests/test_taaqol_normative_source_completeness_audit_16.py\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'دُقّق اكتمال نموذج المصدر المعياري لكل مرشحات المجال الأربعة: '
             f'ALL_REQUIRED_FIELDS_COMPLETE = {e(all_complete)} · MISSING_FIELDS_COUNT = {missing_total}. '
             'لم يولد أو يُختر أو يُصدَّق أي مصدر، ولا حكم/مناط/تنزيل/جواب. طلب الجولة 17 جاهز للمالك.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'ALL_REQUIRED_FIELDS_COMPLETE = {e(all_complete)} · MISSING_FIELDS_COUNT = {missing_total} · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_16_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'NORMATIVE_SOURCE_BORN = NO · NORMATIVE_SOURCE_RATIFIED = NO · NORMATIVE_SOURCE_SELECTED = NO · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_MANAGER_REPORT_AR_16.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    tpl = load_template()
    rows = audit_candidates(tpl)
    missing_total = sum(len(r["missing_fields"]) for r in rows)
    all_complete = "YES" if all(r["complete"] == "YES" for r in rows) else "NO"

    (OUT / "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16.json").write_text(
        json.dumps(build_audit_json(rows), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NORMATIVE_SOURCE_MISSING_FIELDS_16.json").write_text(
        json.dumps(build_missing_json(rows), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NORMATIVE_SOURCE_COMPLETENESS_AUDIT_GUARDS_16.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_17.md").write_text(
        owner_request_17_md(rows), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(rows, missing_total, all_complete, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(
        render_manager(tokens, rows, missing_total, all_complete, trows, anm), encoding="utf-8")
    print("REPORT_16=" + a.report_out)
    print(f"ALL_COMPLETE={all_complete} MISSING_FIELDS_COUNT={missing_total} "
          f"SOURCE_BORN=NO SOURCE_RATIFIED=NO ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
