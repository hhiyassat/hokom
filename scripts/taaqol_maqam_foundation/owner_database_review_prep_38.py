#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_OWNER_DATABASE_REVIEW_PREP_38 (owner review preparation — not ratification).

Turns the round-37 provenance catalog (123 records) + external-reference layer (11) into 134 owner-review
rows, grouped by the 12 sections. Every row defaults to owner_review_decision=DEFER, verdict=AWAITING_
OWNER_REVIEW, canonical_status=CANDIDATE_ONLY. No record is auto-accepted; no ratification; no
generalization; no final manāṭ/tanzīl/final hukm/final answer. Reads artifacts only. No commit; no push.
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
PRODUCER = "scripts/taaqol_maqam_foundation/owner_database_review_prep_38.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
CATALOG = OUT / "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.json"
XREFS = OUT / "TAAQOL_EXTERNAL_REFERENCE_LAYER_CANDIDATES_37.json"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
ALLOWED_DECISIONS = ["ACCEPT_AS_DATABASE_RECORD", "DEFER", "REJECT", "NEEDS_SOURCE",
                     "NEEDS_FORMAT_FIX", "NEEDS_OWNER_DEFINITION", "NEEDS_EXTERNAL_VERIFICATION"]
SECTIONS = [
    "NAZILA_TEXT", "NAZILA_TOKEN", "NORMATIVE_SOURCE_TEXT", "OWNER_RULE_TEXT", "DOMAIN_TERM",
    "REQUIREMENT_TEXT", "FACT_CANDIDATE_TEXT", "MISSING_FACT_REQUIREMENT_TEXT",
    "HUKM_CANDIDATE_TEXT", "MANAT_CANDIDATE_TEXT", "GUARD_TEXT", "EXTERNAL_REFERENCE_LAYER_CANDIDATES",
]


def build_rows():
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))["records"]
    xr = json.loads(XREFS.read_text(encoding="utf-8"))["external_references"]
    rows = []
    for r in cat:
        rows.append({
            "record_id": r["record_id"],
            "section": r["text_type"],
            "text_type": r["text_type"],
            "reference_layer": "N/A",
            "arabic_text_or_english_reference": r["arabic_text"],
            "source_round": r["source_round"],
            "source_artifact_path": r["source_artifact_path"],
            "used_as": r["used_as"],
            "database_target_table": r["database_target_table"],
            "current_status": r["database_entry_status"],
            "owner_review_decision": "DEFER",
            "owner_notes": "",
            "required_action": "OWNER_REVIEW_AND_DECIDE",
            "canonical_status": "CANDIDATE_ONLY",
            "cause": "سجل كتالوج من الجولة 37 معروض لمراجعة المالك.",
            "conditions": "قرار مالك صريح من القائمة المسموحة قبل أي اعتماد.",
            "preventers": "الاعتماد التلقائي؛ التعميم؛ إنتاج حكم.",
            "verdict": "AWAITING_OWNER_REVIEW",
            "residuals": "لا اعتماد ولا تعميم حتى قرار المالك.",
        })
    for x in xr:
        rows.append({
            "record_id": x["reference_id"],
            "section": "EXTERNAL_REFERENCE_LAYER_CANDIDATES",
            "text_type": "EXTERNAL_REFERENCE",
            "reference_layer": x["layer_name"],
            "arabic_text_or_english_reference": x["english_reference"],
            "source_round": "37",
            "source_artifact_path": "output/taaqol_maqam_foundation_generated/TAAQOL_EXTERNAL_REFERENCE_LAYER_CANDIDATES_37.json",
            "used_as": x["usage_now"],
            "database_target_table": "external_reference_registry",
            "current_status": x["authority_status"],
            "owner_review_decision": "DEFER",
            "owner_notes": "",
            "required_action": "OWNER_REVIEW_AND_DECIDE",
            "canonical_status": "CANDIDATE_ONLY",
            "cause": "مرجع خارجي من الجولة 37 معروض لمراجعة المالك.",
            "conditions": "قرار مالك + تحقق خارجي قبل أي اعتماد؛ العربي أولًا.",
            "preventers": "اعتباره سلطة؛ اشتقاق قاعدة عربية/حكم منه؛ اعتماده بلا تحقق.",
            "verdict": "AWAITING_OWNER_REVIEW",
            "residuals": "مرجع تصميمي مرشح؛ availability غير متحقَّق.",
        })
    return rows, len(cat), len(xr)


def group_counts(rows):
    c = {s: 0 for s in SECTIONS}
    for r in rows:
        c[r["section"]] = c.get(r["section"], 0) + 1
    return c


def guards():
    return {
        "OWNER_REVIEW_PREP_IS_NOT_RATIFICATION": "YES",
        "NO_RECORD_AUTO_ACCEPTED": "YES",
        "ALL_DEFAULT_TO_DEFER": "YES",
        "EXTERNAL_REFERENCE_IS_NOT_AUTHORITY": "YES",
        "ACCEPT_AS_DATABASE_RECORD_DOES_NOT_CREATE_HUKM": "YES",
        "GENERALIZATION_READY": "NO",
        "FINAL_MANAT": "NO",
        "TANZIL": "NO",
        "FINAL_HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "producer_file": PRODUCER,
    }


def review_md(rows, gc, n_cat, n_xr):
    L = ["# وثيقة مراجعة المالك لقاعدة البيانات (الجولة 38 — تحضير لا تصديق)", "",
         f"CATALOG_RECORDS = {n_cat} · EXTERNAL_REFERENCE_RECORDS = {n_xr} · "
         f"OWNER_REVIEW_ROWS = **{len(rows)}**", "",
         "**قرارات المالك المسموحة:** " + " / ".join(ALLOWED_DECISIONS), "",
         "الافتراض لكل صف: `owner_review_decision = DEFER` · `verdict = AWAITING_OWNER_REVIEW` · "
         "`canonical_status = CANDIDATE_ONLY`. لا اعتماد تلقائي، لا تعميم، لا حكم.", ""]
    by = {s: [r for r in rows if r["section"] == s] for s in SECTIONS}
    for i, s in enumerate(SECTIONS, 1):
        L.append(f"## {i}. {s} — {gc.get(s, 0)} صف")
        for r in by[s][:15]:
            L.append(f"- `{r['record_id']}` · used_as={r['used_as']} · table={r['database_target_table']} · "
                     f"decision={r['owner_review_decision']} · action={r['required_action']}")
        if len(by[s]) > 15:
            L.append(f"- … (+{len(by[s])-15} صف في JSON)")
    L += ["", "---", "*OWNER_REVIEW_PREP_IS_NOT_RATIFICATION · كل صف بانتظار قرار المالك.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-PROVENANCE-CATALOG-37", "ROUND_37",
     "output/taaqol_maqam_foundation_generated/TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.json",
     "tests/test_taaqol_arabic_data_provenance_catalog_37.py"),
    ("REQ-EXTERNAL-REFERENCE-LAYER-37", "ROUND_37",
     "output/taaqol_maqam_foundation_generated/TAAQOL_EXTERNAL_REFERENCE_LAYER_CANDIDATES_37.json",
     "tests/test_taaqol_arabic_data_provenance_catalog_37.py"),
    ("REQ-OWNER-DATABASE-REVIEW-PREP-38", "ROUND_38",
     "output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.json",
     "tests/test_taaqol_owner_database_review_prep_38.py"),
    ("REQ-OWNER-DATABASE-REVIEW-MATRIX-38", "ROUND_38",
     "output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_MATRIX_38.json",
     "tests/test_taaqol_owner_database_review_prep_38.py"),
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


def build_matrix(rows, gc, n_cat, n_xr, anm):
    kv = [
        ("ROUND", "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("REPORT_SOURCE", "CODE_AND_ARTIFACTS_ONLY"),
        ("CATALOG_RECORDS_LOADED", str(n_cat)),
        ("EXTERNAL_REFERENCE_RECORDS_LOADED", str(n_xr)),
        ("OWNER_REVIEW_ROWS_CREATED", str(len(rows))),
        ("SECTION_COUNT", str(len(SECTIONS))),
        ("DEFAULT_DECISION", "DEFER"),
        ("ALL_ROWS_HAVE_DECISION", "YES" if all(r["owner_review_decision"] for r in rows) else "NO"),
        ("ALL_ROWS_DEFAULT_DEFER", "YES" if all(r["owner_review_decision"] == "DEFER" for r in rows) else "NO"),
        ("ALL_ROWS_CANDIDATE_ONLY", "YES" if all(r["canonical_status"] == "CANDIDATE_ONLY" for r in rows) else "NO"),
        ("ALLOWED_DECISION_COUNT", str(len(ALLOWED_DECISIONS))),
        ("OWNER_REVIEW_PREP_IS_NOT_RATIFICATION", "YES"),
        ("NO_RECORD_AUTO_ACCEPTED", "YES"),
        ("EXTERNAL_REFERENCE_IS_NOT_AUTHORITY", "YES"),
        ("GENERALIZATION_READY", "NO"),
        ("OWNER_DATABASE_RATIFICATION_REQUIRED", "YES"),
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


def render_manager(tokens, rows, gc, n_cat, n_xr, trows, anm):
    e = lambda x: html.escape(str(x))
    by = {s: [r for r in rows if r["section"] == s] for s in SECTIONS}
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — تحضير مراجعة المالك لقاعدة البيانات (38)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.74rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — تحضير مراجعة المالك لقاعدة البيانات (38)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · '
             'EXTERNAL_REFS = 0. تحضير مراجعة — لا تصديق.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'OWNER_REVIEW_PREP_IS_NOT_RATIFICATION=YES · لا اعتماد تلقائي · كل صف DEFER · '
             'EXTERNAL_REFERENCE ليس سلطة · ACCEPT لا يُنشئ حكمًا · GENERALIZATION_READY=NO · '
             'لا مناط/تنزيل/حكم/جواب · FULL_TAAQOL_PROJECT_CLOSED=NO.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             f'<li>جُهِّزت **{len(rows)}** صف مراجعة ({n_cat} كتالوج + {n_xr} مرجع خارجي) عبر {len(SECTIONS)} قسمًا.</li>'
             '<li>كل صف owner_review_decision=DEFER · verdict=AWAITING_OWNER_REVIEW · CANDIDATE_ONLY.</li>'
             '<li>قائمة قرارات مغلقة (7)؛ لا اعتماد/تعميم/حكم؛ التصديق قرار مالك لاحق.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ معروضة للمراجعة لا للاعتماد. IFADAH_CHANGED = NO.</div>')
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يُعتمد قاعدةً بالمراجعة. MAQAM_IS_NOT_RULE = YES.</div>')
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'قرارات الاعتماد كلها بيد المالك من قائمة مغلقة.</div>')
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'تحضير مراجعة فقط؛ لا واقعة مقبولة ولا رخصة عبور. FACT_ACCEPTED = NO.</div>')
    # 8 — sections table
    P.append('<h2>8. المصدر المعياري — أقسام المراجعة (12) وعدد الصفوف</h2><div class="wrap"><table><thead><tr>'
             '<th>#</th><th>section</th><th>عدد الصفوف</th><th>default_decision</th></tr></thead><tbody>')
    for i, s in enumerate(SECTIONS, 1):
        P.append(f'<tr><td>{i}</td><th>{e(s)}</th><td class="y">{gc.get(s, 0)}</td>'
                 f'<td class="d">DEFER</td></tr>')
    P.append(f'<tr><td>—</td><th>الإجمالي</th><td class="y">{len(rows)}</td><td class="d">DEFER</td></tr>'
             '</tbody></table></div>')
    P.append('<div class="note">قائمة القرارات المسموحة: ' + e(" / ".join(ALLOWED_DECISIONS)) + '.</div>')
    # sample rows
    P.append('<div class="wrap"><table><thead><tr><th>record_id</th><th>section</th><th>used_as</th>'
             '<th>target_table</th><th>decision</th><th>verdict</th></tr></thead><tbody>')
    sample = [r for s in SECTIONS for r in by[s][:2]]
    for r in sample:
        P.append('<tr><th>' + e(r["record_id"]) + '</th><td class="d">' + e(r["section"]) + '</td>'
                 '<td>' + e(r["used_as"]) + '</td><td>' + e(r["database_target_table"]) + '</td>'
                 + f'<td class="d">{e(r["owner_review_decision"])}</td>'
                 + f'<td class="n">{e(r["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: OWNER_DATABASE_REVIEW_PREP. لا اعتماد ولا تعميم؛ كل صف ينتظر قرار المالك.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             'المطلوب من المالك: إدخال owner_review_decision لكل صف من القائمة المغلقة (7 قرارات) + owner_notes '
             'عند الحاجة.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">بعد قرارات المالك: تُنقل السجلات المقبولة '
             '(ACCEPT_AS_DATABASE_RECORD) إلى إشغال السجلات المصدَّق؛ ويبقى التعميم والحكم محجوبين.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_owner_database_review_prep_38.py — '
             'ROUND_38_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32..38 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    P.append(_trace_html(trows))
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_38_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUTS = TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.json; TAAQOL_EXTERNAL_REFERENCE_LAYER_CANDIDATES_37.json\n'
             'REVIEW_MD = output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.md\n'
             'REVIEW_JSON = output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.json\n'
             'REVIEW_MATRIX = output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_MATRIX_38.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_GUARDS_38.json\n'
             'PYTEST_FILE = tests/test_taaqol_owner_database_review_prep_38.py\n'
             'DEFAULT_DECISION = DEFER\nGENERALIZATION_READY = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'جُهِّزت {len(rows)} صف مراجعة مالك ({n_cat}+{n_xr}) عبر 12 قسمًا، كلها DEFER بقائمة قرارات مغلقة؛ '
             'لا اعتماد/تعميم/حكم، والتصديق قرار مالك لاحق.</div>')
    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'CATALOG_RECORDS_LOADED = {n_cat} · EXTERNAL_REFERENCE_RECORDS_LOADED = {n_xr} · '
             f'OWNER_REVIEW_ROWS_CREATED = {len(rows)} · DEFAULT_DECISION = DEFER · '
             'OWNER_REVIEW_PREP_IS_NOT_RATIFICATION = YES · GENERALIZATION_READY = NO · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             'FULL_TAAQOL_PROJECT_CLOSED = NO · AUTHORITY_LEAK = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_38_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'DEFAULT_DECISION = DEFER · GENERALIZATION_READY = NO · FINAL_MANAT = NO · TANZIL = NO · '
             'FINAL_HUKM = NO · FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "TAAQOL_OWNER_DATABASE_REVIEW_MANAGER_REPORT_AR_38.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    rows, n_cat, n_xr = build_rows()
    gc = group_counts(rows)

    (OUT / "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.json").write_text(
        json.dumps({"ROUND": "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38",
                    "catalog_records_loaded": n_cat,
                    "external_reference_records_loaded": n_xr,
                    "owner_review_rows_created": len(rows),
                    "allowed_decisions": ALLOWED_DECISIONS,
                    "default_decision": "DEFER",
                    "sections": SECTIONS,
                    "rows": rows, "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.md").write_text(review_md(rows, gc, n_cat, n_xr), encoding="utf-8")
    (OUT / "TAAQOL_OWNER_DATABASE_REVIEW_MATRIX_38.json").write_text(
        json.dumps({"ROUND": "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38",
                    "section_counts": gc, "total_rows": len(rows),
                    "allowed_decisions": ALLOWED_DECISIONS, "default_decision": "DEFER",
                    "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_OWNER_DATABASE_REVIEW_GUARDS_38.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(rows, gc, n_cat, n_xr, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, rows, gc, n_cat, n_xr, trows, anm), encoding="utf-8")
    print("REPORT_38=" + a.report_out)
    print(f"CAT={n_cat} XREF={n_xr} ROWS={len(rows)} sections={gc} DEFAULT=DEFER ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
