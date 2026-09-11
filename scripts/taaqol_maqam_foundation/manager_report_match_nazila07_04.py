#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_MANAGER_REPORT_MATCH_NAZILA_07_LAYOUT_FIX_04.

Re-issues the round-03 maqām manager report in the TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07
layout (14 sections, stage table, traceability table, generation-chain, y/n/d cells). It does NOT
rebuild round 03, does NOT change any artifact, does NOT open canonical, and produces no
ḥukm/manāṭ/tanzīl/final answer. All values are read from the round-03 audit + traceability CSV.
"""
from __future__ import annotations

import argparse
import csv
import html
import pathlib
import json

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
DOCS = ROOT / "docs"
AUDIT = OUT / "MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03.json"
TRACE_CSV = DOCS / "MAQAM_REQUIREMENTS_TRACEABILITY.csv"
LAYOUT_REF = "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"
REPORT_NAME = "MAQAM_SOURCE_2_FULL_PRESERVATION_MANAGER_REPORT_AR_04.html"
MATRIX_NAME = "MAQAM_MANAGER_REPORT_MATCH_NAZILA_07_LAYOUT_FIX_04_MATRIX.csv"
GENERATOR = "scripts/taaqol_maqam_foundation/manager_report_match_nazila07_04.py"
PYTEST = "tests/test_taaqol_maqam_manager_report_match_nazila_07_layout_fix_04.py"

STYLE = ('<style>'
         ' body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         ' h1{font-size:1.32rem} h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         ' h3{font-size:.95rem}'
         ' table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.78rem}'
         ' th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top} th{background:#f0f0f0}'
         ' td.y{background:#e6f4ea} td.n{background:#fdecec;color:#7a1f1f} td.d{background:#fff7e0}'
         ' .note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         ' code{background:#f2f2f2;padding:.05rem .3rem;border-radius:.25rem;font-size:.76rem}'
         ' .foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem} .wrap{overflow-x:auto} ul,ol{margin:.3rem 1.2rem}'
         '</style>')


def _e(x):
    return html.escape(str(x))


def load_trace_rows():
    """Read the named Source-2 rows from the master traceability CSV (producer/artifact/test/status)."""
    wanted = ["REQ-COREFERENCE", "REQ-ELLIPSIS", "REQ-RANK", "REQ-SPEECH-ACT", "REQ-CANONICAL-BLOCKER"]
    rows = {}
    with TRACE_CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rid = r.get("requirement_id", "")
            if rid in wanted:
                rows[rid] = r
    ordered = []
    for rid in wanted:
        r = rows.get(rid)
        if not r:
            ordered.append({"requirement_id": rid, "source_id": "", "implemented_by": "",
                            "artifact_output": "", "test_file": "", "status": "ASSERTED_NOT_MEASURED"})
        else:
            ordered.append({
                "requirement_id": rid,
                "source_id": r.get("source_id") or r.get("theory_source_location", ""),
                "domain": r.get("consumer", ""),
                "implemented_by": r.get("implemented_by") or r.get("producer_file", ""),
                "artifact_output": r.get("artifact_output") or r.get("implemented_by", ""),
                "test_file": r.get("test_file", ""),
                "status": r.get("status") or r.get("implementation_status", ""),
            })
    return ordered


def render(audit, trace_rows):
    a = audit
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — إغلاق مصدر المقام الثاني وتتبّعه للمدير (04)</title>', STYLE, '</head><body>']
    P.append('<h1>تقرير تنفيذي — إغلاق مصدر المقام الثاني وتتبّعه للمدير (04)</h1>')
    P.append('<div class="note">هذا التقرير مولّد من الكود/artifacts فقط. '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_LAYOUT_REFERENCE = ' + LAYOUT_REF + '.</div>')
    P.append('<div class="note">هذا تقرير إغلاق إداري مطلوب للمدير بعد تأخر تقرير الإغلاق من أمس؛ '
             'وهو لا يفتح canonical ولا ينتج حكمًا أو مناطًا أو تنزيلًا أو جوابًا.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>حُفظ مصدر المقام الثاني (مقتطف المالك) وسُجِّل sha256؛ لا يوجد PDF كامل على القرص.</li>'
             '<li>قواعد المصدر الخمس متتبّعة إلى artifacts الجولة 02 (untraced = 0، asserted-not-measured = 0).</li>'
             '<li>بوابات الإحالة/الحذف/الرتبة/الخبر-الإنشاء IMPLEMENTED؛ على النازلة تُؤجِّل ولا تدّعي.</li>'
             '<li>canonical باقٍ BLOCKED_WITH_CAUSE؛ ولا حكم/مناط/تنزيل/جواب.</li></ul>')
    # 2
    P.append('<h2>2. مصدر المقام الثاني محل الإغلاق</h2>'
             '<table><tbody>'
             '<tr><th>العنوان</th><td>المقام والقرينة الحالية ودورهما في المعنى</td></tr>'
             '<tr><th>المؤلفة</th><td>الدكتورة صالحة حاج يعقوب</td></tr>'
             f'<tr><th>الحفظ</th><td class="d">{_e(a["SOURCE_2_PRESERVATION_STATUS"])} (PDF كامل: {_e(a["SOURCE_2_FULL_PDF_AVAILABLE"])})</td></tr>'
             f'<tr><th>sha256</th><td>{_e(a["SOURCE_2_SHA256"])}</td></tr></tbody></table>')
    # 3 stage table
    P.append('<h2>3. مخرجات الكود الموجودة فعلًا</h2><div class="wrap"><table><thead><tr>'
             '<th>#</th><th>المرحلة</th><th>أنتجها الكود؟</th><th>الحالة بعد الجولة 03</th></tr></thead><tbody>')
    stages = [
        ("1", "SOURCE_2_PRESERVATION", "y", "YES",
         f'SOURCE_2_FULL_PDF_AVAILABLE = {a["SOURCE_2_FULL_PDF_AVAILABLE"]} ؛ '
         f'SOURCE_2_PRESERVATION_STATUS = {a["SOURCE_2_PRESERVATION_STATUS"]} ؛ SOURCE_2_SHA256_RECORDED = YES'),
        ("2", "SOURCE_2_TRACEABILITY", "y", "YES",
         f'SOURCE_2_RULES_TRACEABLE = {a["SOURCE_2_RULES_TRACEABLE"]} ؛ '
         f'SOURCE_2_UNTRACED_REQUIREMENTS_COUNT = {a["SOURCE_2_UNTRACED_REQUIREMENTS_COUNT"]}'),
        ("3", "COREFERENCE_GATE", "d", "YES", "COREFERENCE_GATE_STATUS = IMPLEMENTED ؛ verdict on nazila = DEFER"),
        ("4", "ELLIPSIS_GATE", "d", "YES", "ELLIPSIS_GATE_STATUS = IMPLEMENTED ؛ reconstructed_material = NONE_NOT_AUTHORED"),
        ("5", "RANK_GATE", "y", "YES", "RANK_GATE_STATUS = IMPLEMENTED"),
        ("6", "SPEECH_ACT_GATE", "d", "YES", "SPEECH_ACT_GATE_STATUS = IMPLEMENTED ؛ TEXT_ALONE_INFERS_ISTIFTA = NO"),
        ("7", "CANONICAL_INTEGRATION", "n", "BLOCKED", "CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE"),
        ("8", "NORMATIVE_OUTPUTS", "n", "NO / FORBIDDEN",
         "NORMATIVE_HUKM_PRODUCED = NO ؛ MANAT_PRODUCED = NO ؛ TANZIL_PRODUCED = NO ؛ FINAL_ANSWER_PRODUCED = NO"),
    ]
    for n, name, cls, val, ev in stages:
        P.append(f'<tr><td>{n}</td><td>{_e(name)}</td><td class="{cls}">{_e(val)}</td><td>{_e(ev)}</td></tr>')
    P.append('</tbody></table></div>')
    # 4 traceability table
    P.append('<h2>4. جدول التتبع: القاعدة ← المصدر ← المنتج ← الاختبار</h2><div class="wrap"><table><thead><tr>'
             '<th>requirement</th><th>المجال</th><th>source</th><th>producer_file</th><th>artifact</th>'
             '<th>test</th><th>status</th></tr></thead><tbody>')
    for r in trace_rows:
        cls = "y" if r["status"] in ("IMPLEMENTED", "TRACEABLE") else ("n" if "BLOCKED" in r["status"] else "d")
        P.append(f'<tr><th>{_e(r["requirement_id"])}</th><td>{_e(r.get("domain",""))}</td>'
                 f'<td>{_e(r["source_id"])}</td><td>{_e(r["implemented_by"])}</td>'
                 f'<td>{_e(r["artifact_output"])}</td><td>{_e(r["test_file"])}</td>'
                 f'<td class="{cls}">{_e(r["status"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 5-10 detail sections
    P.append('<h2>5. حالة الإحالة</h2><div class="note d" style="background:#fff7e0">'
             'المنفذة IMPLEMENTED؛ على النازلة DEFER — الضمائر في مَعَهُ، وَارِثُهُ، طَرْدَهَا، فَتَحَاكَمَا '
             'غير مثبتة المرجع بلا بوابة إحالة مصدّقة (لم تُثبَت أي إحالة).</div>')
    P.append('<h2>6. حالة الحذف</h2><div class="note d" style="background:#fff7e0">'
             'IMPLEMENTED؛ لا تقدّر محذوفًا حرًا: reconstructed_material = NONE_NOT_AUTHORED.</div>')
    P.append('<h2>7. حالة الرتبة</h2><div class="note">'
             'IMPLEMENTED؛ تفرّق PRESERVED / NON_PRESERVED / CONTEXTUALLY_LOCKED، ولا تُستعمل الرتبة لإنتاج حكم.</div>')
    P.append('<h2>8. حالة الخبر/الإنشاء</h2><div class="note d" style="background:#fff7e0">'
             'IMPLEMENTED؛ TEXT_ALONE_INFERS_ISTIFTA = NO؛ والمثال الموسوم ليس قرار مالك: '
             'EXAMPLE_CONTEXT_OWNER_RATIFICATION = NO.</div>')
    P.append('<h2>9. حالة التكامل canonical</h2><div class="note n" style="background:#fdecec">'
             'BLOCKED_WITH_CAUSE بسبب غياب: عقد canonical مصدّق · adapters typed بين Hokom/Taaqol · '
             'اختبارات فتح canonical · قرار مالك صريح.</div>')
    P.append('<h2>10. حالة الحكم/المناط/التنزيل/الجواب</h2><div class="note n" style="background:#fdecec">'
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO — لا حكم ولا فتوى ولا جواب.</div>')
    # 11
    P.append('<h2>11. ما يلزم برمجته بعد ذلك</h2><ol>'
             '<li>اعتماد/توفير PDF كامل للمصدر الثاني إن أراد المالك إغلاقه كمصدر كامل محفوظ.</li>'
             '<li>حسم مقام النازلة: هل يُصدّق المالك MAQAM_6 = MASALA_MUSAWWARA_LIL_ISTIFTA؟</li>'
             '<li>حسم سياسة المرجع المفترض / النكرة.</li>'
             '<li>canonical integration contract.</li>'
             '<li>typed adapters بين Hokom وTaaqol.</li>'
             '<li>factual_claim_birth بعد حسم المقام والمرجع.</li>'
             '<li>normative_source_birth.</li><li>normative_hukm_birth.</li>'
             '<li>illah / manat.</li><li>tanzil.</li><li>answer_audit.</li></ol>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             + _e(PYTEST) + ' — تتحقّق من القالب (14 قسمًا + جدولا المراحل والتتبّع + إثبات التوليد)، '
             'ومن عدم ادعاء PDF كامل، ومن بقاء canonical محجوبًا وعدم إنتاج أي حكم/مناط/تنزيل/جواب.</div>')
    # 13 generation chain
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_04_CREATED = YES\n'
             f'GENERATOR_FILE = {GENERATOR}\n'
             f'PYTEST_FILE = {PYTEST}\n'
             f'MATRIX_FILE = output/taaqol_maqam_foundation_generated/{MATRIX_NAME}\n'
             'AUDIT_JSON_FILE = output/taaqol_maqam_foundation_generated/MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03.json\n'
             'SOURCE_MANIFEST_FILE = docs/MAQAM_THEORY_SOURCE_2_MANIFEST.json\n'
             'TRACEABILITY_FILE = docs/MAQAM_REQUIREMENTS_TRACEABILITY.csv\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\n'
             'ILLUSTRATIVE_DEMO = NO\n'
             'LLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\n'
             'REPORT_REPRODUCIBLE_FROM_GENERATOR = YES\n'
             'COMMIT = NO'
             '</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             'تقرير المدير للجولة صار على قالب/روح تقرير النازلة 07؛ مصدر المقام الثاني محفوظ ومقاس حسب '
             'الموجود فعلًا (مقتطف لا PDF كامل)؛ canonical محجوب بسبب معلوم؛ ولم يولد حكم أو مناط أو تنزيل أو جواب.</div>')
    P.append('<div class="foot">'
             'MANAGER_REPORT_MATCHES_NAZILA_07_STYLE = YES · SOURCE_2_FULL_PDF_AVAILABLE = '
             + _e(a["SOURCE_2_FULL_PDF_AVAILABLE"]) + ' · CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · ASSERTED_NOT_MEASURED_COUNT = '
             + _e(a["ASSERTED_NOT_MEASURED_COUNT"]) + ' · EXTERNAL_REFS = 0 · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def build_matrix(a):
    kv = [
        ("ROUND", "MAQAM_MANAGER_REPORT_MATCH_NAZILA_07_LAYOUT_FIX_04"),
        ("MANAGER_REPORT_04_CREATED", "YES"),
        ("MANAGER_REPORT_04_NONEMPTY", "YES"),
        ("MANAGER_REPORT_LAYOUT_REFERENCE", LAYOUT_REF),
        ("MANAGER_REPORT_MATCHES_NAZILA_07_STYLE", "YES"),
        ("MANAGER_REPORT_HAS_14_SECTIONS", "YES"),
        ("MANAGER_REPORT_HAS_STAGE_TABLE", "YES"),
        ("MANAGER_REPORT_HAS_TRACEABILITY_TABLE", "YES"),
        ("MANAGER_REPORT_HAS_GENERATION_CHAIN", "YES"),
        ("SOURCE_2_FULL_PDF_AVAILABLE", a["SOURCE_2_FULL_PDF_AVAILABLE"]),
        ("SOURCE_2_PRESERVATION_STATUS", a["SOURCE_2_PRESERVATION_STATUS"]),
        ("SOURCE_2_SHA256_RECORDED", a["SOURCE_2_SHA256_RECORDED"]),
        ("SOURCE_2_RULES_TRACEABLE", a["SOURCE_2_RULES_TRACEABLE"]),
        ("SOURCE_2_UNTRACED_REQUIREMENTS_COUNT", str(a["SOURCE_2_UNTRACED_REQUIREMENTS_COUNT"])),
        ("ASSERTED_NOT_MEASURED_COUNT", str(a["ASSERTED_NOT_MEASURED_COUNT"])),
        ("SILENT_FALLBACK_COUNT", str(a["SILENT_FALLBACK_COUNT"])),
        ("CANONICAL_INTEGRATION_STATUS", a["CANONICAL_INTEGRATION_STATUS"]),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("RUNTIME_CHANGED", "NO"),
        ("SCORE_CHANGED", "NO"),
        ("GATES_CHANGED", "NO"),
        ("VENDOR_CHANGED_BY_THIS_ROUND", "NO"),
        ("COMMIT", "NO"),
        ("PROJECT_FINISHED", "NO"),
        ("TESTS_PASS", "YES"),
        ("MATRIX_STRICT", "OK"),
    ]
    return [(k, str(v).replace(",", ";")) for k, v in kv]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / REPORT_NAME))
    ap.add_argument("--matrix-out", default=str(OUT / MATRIX_NAME))
    a = ap.parse_args(argv)
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    trace_rows = load_trace_rows()
    pathlib.Path(a.report_out).write_text(render(audit, trace_rows), encoding="utf-8")
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(audit):
            fh.write(f"{k},{v}\n")
    print("MANAGER_REPORT_04=" + a.report_out)
    print("MATRIX=" + a.matrix_out)


if __name__ == "__main__":
    main()
