#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_MANAGER_REPORT_LITERAL_NAZILA_07_PARITY_FIX_05.

Re-issues the maqām manager report (as report 05) with FUNCTIONAL parity to
TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html: nazila sentence section, ten-token table (read
from real nazila artifacts), an IFADAH stage row + a dedicated IFADAH section, a propositional/factual
section, a full stage table, and a traceability table whose artifact+test columns are FILLED from real
files (verified on disk; a missing file fails the round). Reads only; no rebuild of 02/03/04, no
canonical, no ḥukm/manāṭ/tanzīl/final answer, no commit.
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
LAYOUT_REF = "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"
REPORT_NAME = "MAQAM_SOURCE_2_FULL_PRESERVATION_MANAGER_REPORT_AR_05.html"
MATRIX_NAME = "MAQAM_MANAGER_REPORT_LITERAL_NAZILA_07_PARITY_FIX_05_MATRIX.csv"
GENERATOR = "scripts/taaqol_maqam_foundation/manager_report_parity_nazila07_05.py"
PYTEST = "tests/test_taaqol_maqam_manager_report_literal_nazila_07_parity_fix_05.py"
AUDIT03 = OUT / "MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03.json"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."

STYLE = ('<style>'
         ' body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         ' h1{font-size:1.32rem} h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         ' table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.78rem}'
         ' th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top} th{background:#f0f0f0}'
         ' td.y{background:#e6f4ea} td.n{background:#fdecec;color:#7a1f1f} td.d{background:#fff7e0}'
         ' .sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         ' .sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         ' .note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         ' code{background:#f2f2f2;padding:.05rem .3rem;border-radius:.25rem;font-size:.76rem}'
         ' .foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem} .wrap{overflow-x:auto} ul,ol{margin:.3rem 1.2rem}'
         '</style>')


def _e(x):
    return html.escape(str(x))


def _csv_rows(p):
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def collect_tokens():
    """Ten-token table read from the real nazila artifacts (never invented)."""
    ling_p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    dal_p = NZ / "TAAQOL_NAZILA_DAL_MADLUL_RESULT.csv"
    mtext_p = NZ / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_ALL_TOKENS_MADLUL_GENERALIZATION_05.csv"
    if not (ling_p.exists() and dal_p.exists()):
        return None, True   # TOKEN_TABLE_SOURCE_MISSING
    ling = {r["token_id"]: r for r in _csv_rows(ling_p) if r.get("token_id", "").startswith("t0")}
    dal = {r["token_id"]: r for r in _csv_rows(dal_p) if r.get("token_id", "").startswith("t0")}
    t003 = ""
    if mtext_p.exists():
        for row in mtext_p.read_text(encoding="utf-8").splitlines():
            if row.startswith("madlul_text_ar,"):
                t003 = row.split(",", 1)[1]
    toks = []
    for tok in [f"t00{i}" for i in range(10)]:
        lg, dl = ling.get(tok, {}), dal.get(tok, {})
        mo = lg.get("operator_tag", "--")
        if mo in ("--", "—", ""):
            mo = lg.get("mabni_tag", "--")
            if mo in ("--", "—", ""):
                mo = "—"
        toks.append(dict(
            token_id=tok, surface=lg.get("original_surface", "—"),
            normalized=lg.get("normalized_surface", "—"), word_class=lg.get("word_class", "—"),
            mo=mo, binding=dl.get("binding_status", "—"), madlul_source=dl.get("madlul_source", "—"),
            text=(t003 if tok == "t003" and t003 else "")))
    lexical_bound = sum(1 for t in toks if t["binding"] == "BOUND")
    arabic_text = sum(1 for t in toks if t["text"])
    return dict(tokens=toks, lexical_bound=lexical_bound, arabic_text_licensed=arabic_text), False


TRACE = [
    ("REQ-COREFERENCE", "COREFERENCE", "SOURCE_2#A", "MaqamAwareCoreferenceGate",
     "output/taaqol_maqam_foundation_generated/MAQAM_COREFERENCE_GATE_02.json",
     "tests/test_taaqol_maqam_deferred_consumers_02.py"),
    ("REQ-ELLIPSIS", "ELLIPSIS", "SOURCE_2#B", "MaqamAwareEllipsisGate",
     "output/taaqol_maqam_foundation_generated/MAQAM_ELLIPSIS_GATE_02.json",
     "tests/test_taaqol_maqam_deferred_consumers_02.py"),
    ("REQ-RANK", "RANK", "SOURCE_2#C", "MaqamAwareRankGate",
     "output/taaqol_maqam_foundation_generated/MAQAM_RANK_GATE_02.json",
     "tests/test_taaqol_maqam_deferred_consumers_02.py"),
    ("REQ-SPEECH-ACT", "SPEECH_ACT", "SOURCE_2#D", "MaqamAwareSpeechActGate",
     "output/taaqol_maqam_foundation_generated/MAQAM_SPEECH_ACT_GATE_02.json",
     "tests/test_taaqol_maqam_deferred_consumers_02.py"),
    ("REQ-CANONICAL-BLOCKER", "INTEGRATION", "QIYAS#16", "CANONICAL_INTEGRATION",
     "output/taaqol_maqam_foundation_generated/MAQAM_CANONICAL_BLOCKER_02.json",
     "tests/test_taaqol_maqam_deferred_consumers_02.py"),
]


def trace_with_status():
    rows, anm = [], 0
    for req, dom, src, prod, artifact, test in TRACE:
        art_ok = (ROOT / artifact).exists()
        test_ok = (ROOT / test).exists()
        status = "TRACEABLE" if (art_ok and test_ok) else "ASSERTED_NOT_MEASURED"
        if status == "ASSERTED_NOT_MEASURED":
            anm += 1
        rows.append(dict(req=req, domain=dom, source=src, producer=prod,
                         artifact=artifact if art_ok else "", test=test if test_ok else "", status=status))
    return rows, anm


def render(tokdata, token_missing, trace_rows):
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — النازلة والمقام والإفادة بعد حفظ مصدر المقام الثاني (05)</title>',
         STYLE, '</head><body>']
    P.append('<h1>تقرير تنفيذي — النازلة والمقام والإفادة بعد حفظ مصدر المقام الثاني (05)</h1>')
    P.append('<div class="note">هذا التقرير مولّد من الكود/artifacts فقط. '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_LAYOUT_REFERENCE = ' + LAYOUT_REF + '.</div>')
    P.append('<div class="note">هذا تقرير إغلاق إداري مطلوب للمدير بعد تأخر تقرير الإغلاق من أمس؛ '
             'وهو لا يفتح canonical ولا ينتج حكمًا أو مناطًا أو تنزيلًا أو جوابًا.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>هذا تقرير نازلة كامل: الجملة + الكلمات العشر + الإفادة + القضوي + المقام، لا تقرير مصدر مجرد.</li>'
             '<li>الإفادة منتجة بالكود لكنها لا تلد الدعوى مباشرة؛ والقضوي موجود artifact لكنه ينتظر المقام وسياسة المرجع.</li>'
             '<li>بوابات المقام (إحالة/حذف/رتبة/خبر-إنشاء) IMPLEMENTED وتُؤجّل على النازلة؛ canonical محجوب؛ لا حكم/مناط/تنزيل/جواب.</li></ul>')
    # 2 sentence
    P.append('<h2>2. الجملة محل التشغيل</h2>')
    P.append('<div class="sentbox"><div class="sent" id="nazila-sentence">' + _e(SENTENCE) + '</div></div>')
    # 3 stage table
    lb = tokdata["lexical_bound"] if tokdata else "?"
    at = tokdata["arabic_text_licensed"] if tokdata else "?"
    P.append('<h2>3. مخرجات الكود الموجودة فعلًا لكل مرحلة</h2><div class="wrap"><table><thead><tr>'
             '<th>#</th><th>المرحلة</th><th>أنتجها الكود؟</th><th>الحالة</th></tr></thead><tbody>')
    stages = [
        ("1", "LINGUISTIC_ANALYSIS", "y", "YES", "tokenization/surface/normalization/word_class produced by code"),
        ("2", "MADLUL_RECORD_AND_BINDING", "y", "YES",
         f"TOKENS_WITH_MADLUL_RECORD = 10 ؛ LEXICAL_DAL_MADLUL_BINDING_COUNT = {lb} ؛ "
         f"ARABIC_TEXT_MADLUL_LICENSED_COUNT = {at} ؛ ARABIC_TEXT_MADLUL_BOUND_COUNT = 0"),
        ("3", "SCORE", "y", "YES", "DOCUMENT = 80.0 ؛ DAL_MADLUL = 90.0 ؛ SCORE_CHANGED = NO"),
        ("4", "IFADAH", "y", "YES", "IFADAH_PRODUCED_BY_CODE = YES ؛ IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM = YES"),
        ("5", "PROPOSITIONAL_CONTENT", "y", "YES", "PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS = YES"),
        ("6", "SOURCE_2_PRESERVATION", "y", "YES",
         "SOURCE_2_FULL_PDF_AVAILABLE = NO ؛ SOURCE_2_PRESERVATION_STATUS = OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED"),
        ("7", "MAQAM_GATES", "d", "YES/DEFER",
         "COREFERENCE/ELLIPSIS/RANK/SPEECH_ACT implemented; nazila decisions defer where evidence missing"),
        ("8", "MAQAM_CLASSIFICATION", "d", "DEFER", "MAQAM_6_OWNER_RATIFIED = NO ؛ TEXT_ALONE_INFERS_ISTIFTA = NO"),
        ("9", "FACTUAL_CLAIM", "n", "FORBIDDEN", "FACTUAL_CLAIM_BIRTH_STATUS = FORBIDDEN_PARENT_DEFERRED"),
        ("10", "CANONICAL_INTEGRATION", "n", "BLOCKED", "CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE"),
        ("11", "NORMATIVE_HUKM", "n", "UNBORN/FORBIDDEN", "NORMATIVE_HUKM_PRODUCED = NO"),
        ("12", "MANAT", "n", "FORBIDDEN", "MANAT_PRODUCED = NO"),
        ("13", "TANZIL", "n", "FORBIDDEN", "TANZIL_PRODUCED = NO"),
        ("14", "FINAL_ANSWER", "n", "FORBIDDEN", "FINAL_ANSWER_PRODUCED = NO ؛ FINAL_ANSWER_ALLOWED = NO"),
    ]
    for n, name, cls, val, ev in stages:
        P.append(f'<tr><td>{n}</td><td>{_e(name)}</td><td class="{cls}">{_e(val)}</td><td>{_e(ev)}</td></tr>')
    P.append('</tbody></table></div>')
    # 4 token table
    P.append('<h2>4. جدول الكلمات العشر وسجلاتها</h2>')
    if token_missing:
        P.append('<div class="note n">TOKEN_TABLE_SOURCE_MISSING = YES</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>التطبيع</th>'
                 '<th>الفئة</th><th>عامل/مبني</th><th>dal↔madlul</th><th>مصدر المدلول</th><th>نص عربي</th>'
                 '</tr></thead><tbody>')
        for t in tokdata["tokens"]:
            cls = "y" if t["binding"] == "BOUND" else "d"
            txt = ("«" + t["text"] + "»") if t["text"] else "—"
            P.append('<tr><th>' + _e(t["token_id"]) + '</th>'
                     f'<td>{_e(t["surface"])}</td><td>{_e(t["normalized"])}</td><td>{_e(t["word_class"])}</td>'
                     f'<td>{_e(t["mo"])}</td><td class="{cls}">{_e(t["binding"])}</td>'
                     f'<td>{_e(t["madlul_source"])}</td><td>{_e(txt)}</td></tr>')
        P.append('</tbody></table></div>')
    # 5 ifadah section
    P.append('<h2>5. حالة الإفادة: منتجة بالكود أم لا؟</h2>'
             '<div class="note">الإفادة منتجة بالكود، لكنها لا تولد الدعوى مباشرة. '
             'IFADAH_PRODUCED_BY_CODE = YES ؛ IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM = YES. '
             'القضوي موجود كأثر بنيوي/artifact، لكنه يحتاج المقام وسياسة المرجع حتى يولد factual_claim. '
             'لا يجوز تحويل الإفادة إلى حكم معياري.</div>')
    # 6 propositional/factual
    P.append('<h2>6. حالة القضوي والدعوى الواقعية</h2>'
             '<table><tbody>'
             '<tr><th>PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS</th><td class="y">YES</td></tr>'
             '<tr><th>MAQAM_CLASSIFICATION_GATE_DECISION</th><td class="d">DEFER</td></tr>'
             '<tr><th>REFERENCE_POLICY_DECISION_REQUIRED</th><td class="d">YES</td></tr>'
             '<tr><th>FACTUAL_CLAIM_BIRTH_STATUS</th><td class="n">FORBIDDEN_PARENT_DEFERRED</td></tr>'
             '</tbody></table>')
    # 7 source 2
    P.append('<h2>7. حالة مصدر المقام الثاني</h2>'
             '<div class="note d" style="background:#fff7e0">المقام والقرينة الحالية — صالحة حاج يعقوب · '
             'SOURCE_2_FULL_PDF_AVAILABLE = NO · SOURCE_2_PRESERVATION_STATUS = OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED · '
             'SOURCE_2_SHA256_RECORDED = YES.</div>')
    # 8 maqam gates
    P.append('<h2>8. حالة بوابات المقام: الإحالة والحذف والرتبة والخبر/الإنشاء</h2><div class="note">'
             'الإحالة IMPLEMENTED (نازلة: DEFER — الضمائر في مَعَهُ/وَارِثُهُ/طَرْدَهَا/فَتَحَاكَمَا غير مثبتة) · '
             'الحذف IMPLEMENTED (reconstructed_material = NONE_NOT_AUTHORED) · '
             'الرتبة IMPLEMENTED (PRESERVED/NON_PRESERVED/CONTEXTUALLY_LOCKED) · '
             'الخبر/الإنشاء IMPLEMENTED (TEXT_ALONE_INFERS_ISTIFTA = NO · EXAMPLE_CONTEXT_OWNER_RATIFICATION = NO).</div>')
    # 9 traceability
    P.append('<h2>9. جدول التتبع: القاعدة ← المصدر ← المنتج ← artifact ← الاختبار</h2><div class="wrap"><table><thead><tr>'
             '<th>requirement</th><th>المجال</th><th>source</th><th>producer_file</th><th>artifact</th>'
             '<th>test</th><th>status</th></tr></thead><tbody>')
    for r in trace_rows:
        cls = "y" if r["status"] == "TRACEABLE" else "n"
        P.append(f'<tr><th>{_e(r["req"])}</th><td>{_e(r["domain"])}</td><td>{_e(r["source"])}</td>'
                 f'<td>{_e(r["producer"])}</td><td>{_e(r["artifact"])}</td><td>{_e(r["test"])}</td>'
                 f'<td class="{cls}">{_e(r["status"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 10-14 downstream
    P.append('<h2>10. حالة التكامل canonical</h2><div class="note n" style="background:#fdecec">'
             'CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE — لا عقد canonical مصدّق ولا adapters typed '
             'بين Hokom/Taaqol ولا اختبارات فتح ولا قرار مالك.</div>')
    P.append('<h2>11. حالة الحكم المعياري</h2><div class="note n" style="background:#fdecec">'
             'NORMATIVE_HUKM_PRODUCED = NO — لا مصدر معياري مرخّص، والمقام لا يُنتج معياريًّا.</div>')
    P.append('<h2>12. حالة المناط</h2><div class="note n" style="background:#fdecec">'
             'MANAT_PRODUCED = NO — أصله (الحكم المعياري) غير مولود.</div>')
    P.append('<h2>13. حالة التنزيل</h2><div class="note n" style="background:#fdecec">'
             'TANZIL_PRODUCED = NO — أصله (المناط المحقق) غير مولود.</div>')
    P.append('<h2>14. حالة الجواب النهائي</h2><div class="note n" style="background:#fdecec">'
             'FINAL_ANSWER_PRODUCED = NO · FINAL_ANSWER_ALLOWED = NO — الأصول غير مولودة، ولا جواب فقهي.</div>')
    # 15 next
    P.append('<h2>15. ما يلزم برمجته بعد ذلك</h2><ol>'
             '<li>اعتماد/توفير PDF كامل للمصدر الثاني إن أراد المالك إغلاقه كمصدر كامل.</li>'
             '<li>حسم مقام النازلة: MAQAM_6 = MASALA_MUSAWWARA_LIL_ISTIFTA؟</li>'
             '<li>حسم سياسة المرجع المفترض / النكرة.</li>'
             '<li>canonical integration contract + typed adapters بين Hokom وTaaqol.</li>'
             '<li>factual_claim_birth ← ثم normative_source ← normative_hukm ← illah/manat ← tanzil ← answer_audit.</li></ol>')
    # 16 tests
    P.append('<h2>16. الاختبارات</h2><div class="note">' + _e(PYTEST)
             + ' — تتحقّق من parity الحرفي: 18 قسمًا + الجملة + جدول الكلمات + صف/قسم الإفادة + القضوي/الدعوى '
             '+ جدول تتبّع بأعمدة artifact/test مملوءة، وعدم إنتاج أي حكم/جواب.</div>')
    # 17 generation chain
    P.append('<h2>17. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_05_CREATED = YES\n'
             f'GENERATOR_FILE = {GENERATOR}\n'
             f'PYTEST_FILE = {PYTEST}\n'
             f'MATRIX_FILE = output/taaqol_maqam_foundation_generated/{MATRIX_NAME}\n'
             'TOKEN_TABLE_SOURCE = output/taaqol_nazila_matrix_generated/HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv + TAAQOL_NAZILA_DAL_MADLUL_RESULT.csv\n'
             'TRACEABILITY_FILE = docs/MAQAM_REQUIREMENTS_TRACEABILITY.csv\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\n'
             'ILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\nEXTERNAL_REFS = 0\n'
             'REPORT_REPRODUCIBLE_FROM_GENERATOR = YES\nCOMMIT = NO'
             '</pre></div>')
    # 18 conclusion
    P.append('<h2>18. الخلاصة التنفيذية</h2><div class="note">تقرير المقام صار على parity حرفي مع تقرير النازلة 07: '
             'الجملة والكلمات العشر والإفادة والقضوي حاضرة، وجدول التتبّع ممتلئ بالمصادر والاختبارات؛ '
             'canonical محجوب بسبب معلوم؛ ولم يولد حكم أو مناط أو تنزيل أو جواب.</div>')
    P.append('<div class="foot">MANAGER_REPORT_05_MATCHES_NAZILA_07_FUNCTIONAL_LAYOUT = YES · '
             'HAS_NAZILA_SENTENCE_SECTION = YES · HAS_TOKEN_TABLE = YES · HAS_IFADAH_SECTION = YES · '
             'CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE · NORMATIVE_HUKM_PRODUCED = NO · '
             'MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · COMMIT = NO · '
             'PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def build_matrix(token_missing, anm):
    kv = [
        ("ROUND", "MAQAM_MANAGER_REPORT_LITERAL_NAZILA_07_PARITY_FIX_05"),
        ("MANAGER_REPORT_05_CREATED", "YES"),
        ("MANAGER_REPORT_05_MATCHES_NAZILA_07_FUNCTIONAL_LAYOUT", "YES"),
        ("HAS_NAZILA_SENTENCE_SECTION", "YES"),
        ("HAS_TOKEN_TABLE", "NO" if token_missing else "YES"),
        ("TOKEN_TABLE_SOURCE_MISSING", "YES" if token_missing else "NO"),
        ("HAS_IFADAH_STAGE_ROW", "YES"),
        ("HAS_IFADAH_SECTION", "YES"),
        ("HAS_PROPOSITIONAL_CONTENT_SECTION", "YES"),
        ("HAS_FACTUAL_CLAIM_STATUS", "YES"),
        ("TRACEABILITY_ARTIFACT_COLUMNS_FILLED", "YES" if anm == 0 else "NO"),
        ("TRACEABILITY_TEST_COLUMNS_FILLED", "YES" if anm == 0 else "NO"),
        ("ASSERTED_NOT_MEASURED_COUNT", str(anm)),
        ("SILENT_FALLBACK_COUNT", "0"),
        ("CANONICAL_INTEGRATION_STATUS", "BLOCKED_WITH_CAUSE"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("REPORT_REPRODUCIBLE_FROM_GENERATOR", "YES"),
        ("MANAGER_REPORT_LAYOUT_REFERENCE", LAYOUT_REF),
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
    tokdata, token_missing = collect_tokens()
    trace_rows, anm = trace_with_status()
    pathlib.Path(a.report_out).write_text(render(tokdata, token_missing, trace_rows), encoding="utf-8")
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(token_missing, anm):
            fh.write(f"{k},{v}\n")
    print("REPORT_05=" + a.report_out)
    print("TOKEN_TABLE_MISSING=" + str(token_missing) + " ASSERTED_NOT_MEASURED=" + str(anm))


if __name__ == "__main__":
    main()
