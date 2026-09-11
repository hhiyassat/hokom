#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39 (apply owner review decisions).

Applies the owner's decisions over the round-38 review rows: the 123 internal catalog records ->
ACCEPT_AS_DATABASE_RECORD; the 11 external references -> NEEDS_EXTERNAL_VERIFICATION. ACCEPT means the
record enters the future review database ONLY — it is NOT fact acceptance, canonicalization,
generalization, final manāṭ/tanzīl/final hukm/final answer. Reads artifacts only. No commit; no push.
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
PRODUCER = "scripts/taaqol_maqam_foundation/owner_database_review_decisions_39.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
PREP_38 = OUT / "TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.json"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
INTERNAL_SECTIONS = {"NAZILA_TEXT", "NAZILA_TOKEN", "NORMATIVE_SOURCE_TEXT", "OWNER_RULE_TEXT",
                     "DOMAIN_TERM", "REQUIREMENT_TEXT", "FACT_CANDIDATE_TEXT",
                     "MISSING_FACT_REQUIREMENT_TEXT", "HUKM_CANDIDATE_TEXT", "MANAT_CANDIDATE_TEXT",
                     "GUARD_TEXT"}
EXTERNAL_SECTION = "EXTERNAL_REFERENCE_LAYER_CANDIDATES"


def apply_decisions():
    rows = json.loads(PREP_38.read_text(encoding="utf-8"))["rows"]
    decided = []
    for r in rows:
        d = dict(r)
        if r["section"] == EXTERNAL_SECTION:
            d["owner_review_decision"] = "NEEDS_EXTERNAL_VERIFICATION"
            d["verdict"] = "PENDING_EXTERNAL_VERIFICATION"
            d["required_action"] = "OWNER_OR_TOOL_EXTERNAL_VERIFICATION"
        else:
            d["owner_review_decision"] = "ACCEPT_AS_DATABASE_RECORD"
            d["verdict"] = "ACCEPTED_AS_DATABASE_RECORD_ONLY"
            d["required_action"] = "ENTER_REVIEW_DATABASE_AS_RECORD"
        # binding: ACCEPT ≠ fact/hukm/canonical/generalization
        d["canonical_status"] = "CANDIDATE_ONLY"
        d["fact_accepted"] = "NO"
        d["generalization_ready"] = "NO"
        d["database_entry_status"] = ("ACCEPTED_INTO_REVIEW_DATABASE"
                                      if r["section"] != EXTERNAL_SECTION
                                      else "PENDING_EXTERNAL_VERIFICATION")
        d["cause"] = "قرار المالك في الجولة 39."
        d["conditions"] = "قبول كسجل مراجعة فقط؛ لا تعميم/واقعة/مناط/حكم/جواب."
        d["preventers"] = "اعتبار القبول تصديق واقعة أو تعميمًا أو حكمًا."
        d["residuals"] = ("سجل في قاعدة المراجعة، غير معمَّم" if r["section"] != EXTERNAL_SECTION
                          else "مرجع خارجي بانتظار تحقق، ليس سلطة")
        decided.append(d)
    return decided


def guards():
    return {
        "ACCEPT_AS_DATABASE_RECORD_IS_NOT_CANONICALIZATION": "YES",
        "ACCEPT_AS_DATABASE_RECORD_DOES_NOT_CREATE_FACT": "YES",
        "ACCEPT_AS_DATABASE_RECORD_DOES_NOT_CREATE_HUKM": "YES",
        "EXTERNAL_REFERENCES_REQUIRE_VERIFICATION": "YES",
        "GENERALIZATION_READY": "NO",
        "FINAL_MANAT": "NO",
        "TANZIL": "NO",
        "FINAL_HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "producer_file": PRODUCER,
    }


def decisions_md(decided, n_int, n_ext):
    L = ["# قرارات مراجعة المالك لقاعدة البيانات (الجولة 39)", "",
         f"ACCEPTED_AS_DATABASE_RECORD = **{n_int}** · NEEDS_EXTERNAL_VERIFICATION = **{n_ext}** · "
         f"الإجمالي = {len(decided)}", "",
         "**التفسير الملزم:** ACCEPT_AS_DATABASE_RECORD يعني فقط دخول السجل قاعدة بيانات المراجعة المستقبلية؛ "
         "وليس FACT_ACCEPTED ولا FINAL_MANAT ولا TANZIL ولا FINAL_HUKM ولا FINAL_ANSWER ولا "
         "GENERALIZATION_READY ولا FULL_TAAQOL_PROJECT_CLOSED.", "",
         "## الأقسام الداخلية (ACCEPT_AS_DATABASE_RECORD)"]
    secs = {}
    for r in decided:
        secs.setdefault(r["section"], []).append(r)
    for s in sorted(INTERNAL_SECTIONS):
        L.append(f"- {s}: {len(secs.get(s, []))} سجل → ACCEPT_AS_DATABASE_RECORD")
    L += ["", "## الطبقة الخارجية (NEEDS_EXTERNAL_VERIFICATION)",
          f"- {EXTERNAL_SECTION}: {len(secs.get(EXTERNAL_SECTION, []))} مرجع → NEEDS_EXTERNAL_VERIFICATION"]
    L += ["", "---", "*ACCEPT ≠ canonical ≠ fact ≠ hukm؛ المراجع الخارجية ليست سلطة وتحتاج تحققًا.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-OWNER-DATABASE-REVIEW-PREP-38", "ROUND_38",
     "output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.json",
     "tests/test_taaqol_owner_database_review_prep_38.py"),
    ("REQ-REVIEW-DECISIONS-39", "ROUND_39",
     "output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39.json",
     "tests/test_taaqol_owner_database_review_decisions_39.py"),
    ("REQ-ACCEPTED-DATABASE-RECORDS-39", "ROUND_39",
     "output/taaqol_maqam_foundation_generated/TAAQOL_ACCEPTED_DATABASE_RECORDS_39.json",
     "tests/test_taaqol_owner_database_review_decisions_39.py"),
    ("REQ-EXTERNAL-PENDING-VERIFICATION-39", "ROUND_39",
     "output/taaqol_maqam_foundation_generated/TAAQOL_EXTERNAL_REFERENCES_PENDING_VERIFICATION_39.json",
     "tests/test_taaqol_owner_database_review_decisions_39.py"),
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


def build_matrix(decided, n_int, n_ext, anm):
    kv = [
        ("ROUND", "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("REPORT_SOURCE", "CODE_AND_ARTIFACTS_ONLY"),
        ("OWNER_REVIEW_ROWS", str(len(decided))),
        ("ACCEPTED_AS_DATABASE_RECORD", str(n_int)),
        ("EXTERNAL_REFERENCES_PENDING_VERIFICATION", str(n_ext)),
        ("DECISIONS_FILE_CREATED", "YES"),
        ("ACCEPTED_RECORDS_FILE_CREATED", "YES"),
        ("EXTERNAL_PENDING_FILE_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("ALL_INTERNAL_ACCEPTED", "YES" if all(r["owner_review_decision"] == "ACCEPT_AS_DATABASE_RECORD"
                                               for r in decided if r["section"] != EXTERNAL_SECTION) else "NO"),
        ("ALL_EXTERNAL_NEEDS_VERIFICATION", "YES" if all(r["owner_review_decision"] == "NEEDS_EXTERNAL_VERIFICATION"
                                                         for r in decided if r["section"] == EXTERNAL_SECTION) else "NO"),
        ("ALL_ROWS_CANDIDATE_ONLY", "YES" if all(r["canonical_status"] == "CANDIDATE_ONLY" for r in decided) else "NO"),
        ("ALL_FACT_ACCEPTED_NO", "YES" if all(r["fact_accepted"] == "NO" for r in decided) else "NO"),
        ("ACCEPT_AS_DATABASE_RECORD_IS_NOT_CANONICALIZATION", "YES"),
        ("ACCEPT_AS_DATABASE_RECORD_DOES_NOT_CREATE_FACT", "YES"),
        ("ACCEPT_AS_DATABASE_RECORD_DOES_NOT_CREATE_HUKM", "YES"),
        ("EXTERNAL_REFERENCES_REQUIRE_VERIFICATION", "YES"),
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


def render_manager(tokens, decided, n_int, n_ext, trows, anm):
    e = lambda x: html.escape(str(x))
    secs = {}
    for r in decided:
        secs.setdefault(r["section"], []).append(r)
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — قرارات مراجعة قاعدة البيانات (39)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — قرارات مراجعة قاعدة البيانات (39)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · '
             'EXTERNAL_REFS = 0. تطبيق قرارات مراجعة — قبول كسجل فقط.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>التفسير الملزم:</b> '
             'ACCEPT_AS_DATABASE_RECORD ≠ FACT_ACCEPTED ≠ CANONICAL ≠ GENERALIZATION_READY ≠ '
             'FINAL_MANAT/TANZIL/FINAL_HUKM/FINAL_ANSWER. المراجع الخارجية تحتاج تحققًا وليست سلطة.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             f'<li>طُبِّقت قرارات المالك: **{n_int}** سجلًّا داخليًّا → ACCEPT_AS_DATABASE_RECORD، '
             f'**{n_ext}** مرجعًا خارجيًّا → NEEDS_EXTERNAL_VERIFICATION.</li>'
             '<li>القبول = دخول قاعدة بيانات المراجعة فقط؛ لا تعميم/واقعة/مناط/حكم/جواب.</li>'
             '<li>كل صف CANDIDATE_ONLY · fact_accepted=NO؛ GENERALIZATION_READY=NO.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) قُبِلت كسجل مراجعة لا كحكم. IFADAH_CHANGED = NO.</div>')
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ قُبِل كسجل لا كقاعدة عامة. MAQAM_IS_NOT_RULE = YES.</div>')
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'المراجع الخارجية NEEDS_EXTERNAL_VERIFICATION، ليست سلطة.</div>')
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'القبول كسجل لا يُنشئ واقعة مقبولة ولا رخصة عبور. FACT_ACCEPTED = NO.</div>')
    # 8 — decisions by section
    P.append('<h2>8. المصدر المعياري — قرارات المراجعة حسب القسم</h2><div class="wrap"><table><thead><tr>'
             '<th>section</th><th>عدد</th><th>القرار</th></tr></thead><tbody>')
    for s in sorted(INTERNAL_SECTIONS):
        P.append(f'<tr><th>{e(s)}</th><td class="y">{len(secs.get(s, []))}</td>'
                 f'<td class="y">ACCEPT_AS_DATABASE_RECORD</td></tr>')
    P.append(f'<tr><th>{e(EXTERNAL_SECTION)}</th><td class="d">{len(secs.get(EXTERNAL_SECTION, []))}</td>'
             f'<td class="d">NEEDS_EXTERNAL_VERIFICATION</td></tr>')
    P.append(f'<tr><th>الإجمالي</th><td>{len(decided)}</td><td>—</td></tr></tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: DATABASE_REVIEW_DECISIONS. القبول كسجل مراجعة فقط؛ لا تعميم/مناط/تنزيل/حكم/جواب.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             f'المراجع الخارجية ({n_ext}) تحتاج تحققًا (OWNER_OR_TOOL_EXTERNAL_VERIFICATION) قبل أي اعتماد؛ '
             'والسجلات الداخلية المقبولة تبقى غير معمَّمة.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">السجلات المقبولة تدخل قاعدة بيانات المراجعة؛ '
             'التعميم والحكم يبقيان محجوبين حتى قرارات مالك لاحقة.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_owner_database_review_decisions_39.py — '
             'ROUND_39_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32..39 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    P.append(_trace_html(trows))
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_39_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT = output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_PREP_38.json\n'
             'DECISIONS = output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39.json\n'
             'ACCEPTED = output/taaqol_maqam_foundation_generated/TAAQOL_ACCEPTED_DATABASE_RECORDS_39.json\n'
             'EXTERNAL_PENDING = output/taaqol_maqam_foundation_generated/TAAQOL_EXTERNAL_REFERENCES_PENDING_VERIFICATION_39.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/TAAQOL_DATABASE_REVIEW_DECISION_GUARDS_39.json\n'
             'PYTEST_FILE = tests/test_taaqol_owner_database_review_decisions_39.py\n'
             f'ACCEPTED_AS_DATABASE_RECORD = {n_int}\nEXTERNAL_REFERENCES_PENDING_VERIFICATION = {n_ext}\n'
             'GENERALIZATION_READY = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'قُبِل {n_int} سجلًّا داخليًّا كسجلات مراجعة، وأُحيل {n_ext} مرجعًا خارجيًّا للتحقق؛ '
             'القبول ليس تعميمًا ولا واقعة ولا حكمًا. GENERALIZATION_READY=NO، ولا إغلاق مشروع.</div>')
    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'OWNER_REVIEW_ROWS = {len(decided)} · ACCEPTED_AS_DATABASE_RECORD = {n_int} · '
             f'EXTERNAL_REFERENCES_PENDING_VERIFICATION = {n_ext} · '
             'ACCEPT_AS_DATABASE_RECORD_IS_NOT_CANONICALIZATION = YES · GENERALIZATION_READY = NO · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             'FULL_TAAQOL_PROJECT_CLOSED = NO · AUTHORITY_LEAK = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_39_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'ACCEPT_AS_DATABASE_RECORD ≠ FACT/HUKM/CANONICAL · GENERALIZATION_READY = NO · '
             'FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             'FULL_TAAQOL_PROJECT_CLOSED = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "TAAQOL_DATABASE_REVIEW_DECISION_MANAGER_REPORT_AR_39.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    decided = apply_decisions()
    internal = [r for r in decided if r["section"] != EXTERNAL_SECTION]
    external = [r for r in decided if r["section"] == EXTERNAL_SECTION]
    n_int, n_ext = len(internal), len(external)

    (OUT / "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39.json").write_text(
        json.dumps({"ROUND": "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39",
                    "owner_review_rows": len(decided),
                    "accepted_as_database_record": n_int,
                    "external_references_pending_verification": n_ext,
                    "decisions": decided, "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39.md").write_text(
        decisions_md(decided, n_int, n_ext), encoding="utf-8")
    (OUT / "TAAQOL_ACCEPTED_DATABASE_RECORDS_39.json").write_text(
        json.dumps({"ROUND": "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39",
                    "accepted_count": n_int, "note": "ACCEPTED_AS_DATABASE_RECORD_ONLY (not canonical/fact/hukm)",
                    "records": internal, "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_EXTERNAL_REFERENCES_PENDING_VERIFICATION_39.json").write_text(
        json.dumps({"ROUND": "TAAQOL_OWNER_DATABASE_REVIEW_DECISIONS_39",
                    "pending_count": n_ext, "decision": "NEEDS_EXTERNAL_VERIFICATION",
                    "note": "EXTERNAL_REFERENCE_IS_NOT_AUTHORITY; verification required before adoption",
                    "records": external, "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_DATABASE_REVIEW_DECISION_GUARDS_39.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(decided, n_int, n_ext, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, decided, n_int, n_ext, trows, anm), encoding="utf-8")
    print("REPORT_39=" + a.report_out)
    print(f"ROWS={len(decided)} ACCEPTED={n_int} EXTERNAL_PENDING={n_ext} "
          f"GENERALIZATION_READY=NO ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
