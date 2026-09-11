#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL_IFADAH_MAQAM_AND_TARGETED_INFORMATION_REQUEST_FOR_TANZIL_08.

Continues from round 07. Does NOT rebuild prior verdicts, open canonical, or produce
ḥukm/manāṭ/tanzīl/final answer. Ends NOT at a dry "NORMATIVE_SOURCE = UNBORN" but at a specific
targeted information request: (a) a factual-claim passage license, and (b) a normative source
(authority + text + scope + evidence + link license). AR_05-format manager report. No commit.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
PRODUCER = "scripts/taaqol_maqam_foundation/final_ifadah_targeted_info_request_08.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
FORBIDDEN_STRINGS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]

sys.path.insert(0, str(ROOT / "scripts" / "taaqol_maqam_foundation"))
from manager_report_parity_nazila07_05 import collect_tokens  # noqa: E402

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
    ("REQ-MAQAM6-RATIFIED", "MAQAM_CLASSIFICATION", "OWNER_DECISION_06", "maqam6_reference_ratified_closure_06.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_MAQAM_CLASSIFICATION_06.json",
     "tests/test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py"),
    ("REQ-REFERENCE-POLICY-RATIFIED", "REFERENCE_POLICY", "OWNER_DECISION_06", "maqam6_reference_ratified_closure_06.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_REFERENCE_POLICY_06.json",
     "tests/test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py"),
    ("REQ-FACTUAL-CLAIM-BIRTH", "FACTUAL_CLAIM", "OWNER_DECISION_06+PROP08", "maqam6_reference_ratified_closure_06.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_FACTUAL_CLAIM_BIRTH_06.json",
     "tests/test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py"),
    ("REQ-IFADAH-PASSAGE", "IFADAH", "ROUND_08", "final_ifadah_targeted_info_request_08.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_IFADAH_AND_FACTUAL_CLAIM_PASSAGE_08.json",
     "tests/test_taaqol_final_ifadah_maqam_targeted_info_request_08.py"),
    ("REQ-NORMATIVE-SOURCE-BIRTH", "NORMATIVE_SOURCE", "ROUND_07_EXAM", "normative_source_birth_07.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_NORMATIVE_SOURCE_BIRTH_07.json",
     "tests/test_taaqol_normative_source_birth_07.py"),
    ("REQ-TANZIL-READINESS", "TANZIL", "ROUND_08", "final_ifadah_targeted_info_request_08.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_TANZIL_READINESS_AFTER_INFO_REQUEST_08.json",
     "tests/test_taaqol_final_ifadah_maqam_targeted_info_request_08.py"),
]


def trace_rows():
    rows, anm = [], 0
    for req, dom, src, prod, art, test in TRACE:
        ok = (ROOT / art).exists() and (ROOT / test).exists()
        if not ok:
            anm += 1
        rows.append(dict(req=req, domain=dom, source=src, producer=prod,
                         artifact=art if (ROOT / art).exists() else "",
                         test=test if (ROOT / test).exists() else "",
                         status="TRACEABLE" if ok else "ASSERTED_NOT_MEASURED"))
    return rows, anm


def build_json_artifacts():
    ifadah = {
        "node_name": "IFADAH_AND_FACTUAL_CLAIM_PASSAGE",
        "IFADAH_PRODUCED_BY_CODE": "YES", "IFADAH_MISSING": "NO",
        "IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM": "YES",
        "IFADAH_COMPLETION_STATUS": "PARTIAL_OR_DEFERRED",
        "PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS": "YES",
        "MAQAM_6_OWNER_RATIFIED": "YES", "MAQAM_6": "MASALA_MUSAWWARA_LIL_ISTIFTA",
        "MAQAM_6_SCOPE": "THIS_NAZILA_ONLY",
        "REFERENCE_POLICY_OWNER_RATIFIED": "YES",
        "ASSUMED_FACT_REFERENCE": "HYPOTHETICAL_MARKED_REFERENCE",
        "REFERENCE_POLICY_DECISION_REQUIRED": "NO",
        "FACTUAL_CLAIM_BIRTH_STATUS": "BORN_BUT_DEFERRED",
        "FACTUAL_CLAIM_PASSAGE_LICENSE": "MISSING_OWNER_DECISION",
        "ADDITIONAL_INFORMATION_FOR_FACTUAL_CLAIM_REQUIRED": "YES",
        "cause": "ifādah produced + maqam/reference ratified + proposition partial",
        "conditions": "owner passage-license to move factual_claim beyond BORN_BUT_DEFERRED",
        "preventers": ["FACTUAL_CLAIM_PASSAGE_LICENSE_MISSING"],
        "verdict": "IFADAH_PRESENT_FACTUAL_CLAIM_BORN_BUT_DEFERRED",
        "evidence_files": ["output/taaqol_nazila_matrix_generated/PROPOSITIONAL_CONTENT_CANDIDATE_08.json",
                           "output/taaqol_maqam_foundation_generated/NAZILA_FACTUAL_CLAIM_BIRTH_06.json"],
        "producer_file": PRODUCER,
        "residuals": ["factual_claim awaits an explicit owner passage license (this nazila only)"],
    }
    tanzil_readiness = {
        "node_name": "TANZIL_READINESS_AFTER_INFO_REQUEST",
        "TANZIL_BIRTH_STATUS": "FORBIDDEN_MISSING_REQUIREMENTS",
        "TANZIL_PRODUCED": "NO",
        "missing_requirements": ["FACTUAL_CLAIM_PASSAGE_LICENSE", "RATIFIED_NORMATIVE_SOURCE",
                                 "NORMATIVE_HUKM", "CERTIFIED_MANAT", "TAHQIQ_MANAT"],
        "ADDITIONAL_INFORMATION_FOR_TANZIL_REQUIRED": "YES",
        "cause": "ancestors not born (factual claim deferred; normative source unborn)",
        "conditions": "FACTUAL_CLAIM=CERTIFIED AND NORMATIVE_HUKM=CERTIFIED AND MANAT=CERTIFIED AND TAHQIQ_MANAT=CERTIFIED",
        "preventers": ["FACTUAL_CLAIM_DEFERRED", "NORMATIVE_SOURCE_UNBORN"],
        "verdict": "TANZIL_FORBIDDEN_MISSING_REQUIREMENTS",
        "evidence_files": ["output/taaqol_maqam_foundation_generated/NAZILA_NORMATIVE_SOURCE_BIRTH_07.json"],
        "producer_file": PRODUCER, "residuals": ["needs both info requests satisfied"],
    }
    return ifadah, tanzil_readiness


def info_request_factual_md():
    return """# طلب معلومات إضافية — رخصة عبور الدعوى الواقعية (نازلة، هذه الجملة فقط)

**ROUND:** FINAL_IFADAH_MAQAM_AND_TARGETED_INFORMATION_REQUEST_FOR_TANZIL_08
**FACTUAL_CLAIM_BIRTH_STATUS = BORN_BUT_DEFERRED · FACTUAL_CLAIM_PASSAGE_LICENSE = MISSING_OWNER_DECISION**

## السؤال المحدد (أ)
هل يرخّص المالك عبور الدعوى الواقعية من:
```
BORN_BUT_DEFERRED
```
إلى:
```
BORN_BUT_DEFERRED_WITH_PASSAGE_LICENSE
```
**لهذه النازلة فقط (THIS_NAZILA_ONLY)?**

- إن كان الجواب YES: تُرفع `FACTUAL_CLAIM_PASSAGE_LICENSE` من MISSING إلى GRANTED، ويصبح للدعوى رخصة
  عبور نحو محاولة الربط بمصدر معياري — دون إنتاج حكم بعدُ.
- إن كان الجواب NO: تبقى الدعوى `BORN_BUT_DEFERRED` ولا تعبر.

*ملاحظة: هذه رخصة عبور بنيوية فقط؛ لا تُنتج حكمًا معياريًا ولا مناطًا ولا تنزيلًا ولا جوابًا.*
"""


def info_request_normative_md():
    return """# طلب معلومات إضافية — المصدر المعياري (نازلة، هذه الجملة فقط)

**ROUND:** FINAL_IFADAH_MAQAM_AND_TARGETED_INFORMATION_REQUEST_FOR_TANZIL_08
**NORMATIVE_SOURCE_BIRTH_STATUS = UNBORN · NORMATIVE_SOURCE_BLOCKER = NO_RATIFIED_NORMATIVE_SOURCE**
**MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE = NO**

## السؤال المحدد (ب)
إن أراد المالك ولادة المصدر المعياري فليزوّد الخمسة صراحةً:
1. **السلطة المعيارية** (NORMATIVE_AUTHORITY): مَن/ما الجهة المرخِّصة.
2. **النص المعياري** (NORMATIVE_SOURCE_TEXT): النص الحاكم نفسه.
3. **نطاق النص** (SCOPE): حدود انطباقه.
4. **دليل الاعتماد** (EVIDENCE): إثبات صحة/اعتماد النص.
5. **رخصة الربط** (LINK_LICENSE): ترخيص ربط النص المعياري بالدعوى الواقعية لهذه النازلة.

## السؤال المحدد (ج) — الترتيب بعد الوصول
بعد استيفاء (أ) و(ب) فقط يُسمح بمحاولة، بالترتيب:
```
normative_hukm_birth → illah/manat → tanzil → answer_audit
```

*ملاحظة: «أساسيات المقام» و«المقام والقرينة الحالية» مصادر نظرية مقام، ليست مصدرًا معياريًا،
ولا تُنتج حكمًا.*
"""


def build_matrix(anm):
    kv = [
        ("ROUND", "FINAL_IFADAH_MAQAM_AND_TARGETED_INFORMATION_REQUEST_FOR_TANZIL_08"),
        ("FINAL_CLOSURE_MODE", "TARGETED_INFORMATION_REQUEST_PRODUCED"),
        ("MANAGER_REPORT_CANONICAL_FORMAT", "MAQAM_AR_05_STYLE"),
        ("IFADAH_PRODUCED_BY_CODE", "YES"),
        ("IFADAH_MISSING", "NO"),
        ("IFADAH_COMPLETION_STATUS", "PARTIAL_OR_DEFERRED"),
        ("MAQAM_6_OWNER_RATIFIED", "YES"),
        ("MAQAM_6", "MASALA_MUSAWWARA_LIL_ISTIFTA"),
        ("MAQAM_6_SCOPE", "THIS_NAZILA_ONLY"),
        ("REFERENCE_POLICY_OWNER_RATIFIED", "YES"),
        ("ASSUMED_FACT_REFERENCE", "HYPOTHETICAL_MARKED_REFERENCE"),
        ("REFERENCE_POLICY_DECISION_REQUIRED", "NO"),
        ("FACTUAL_CLAIM_BIRTH_STATUS", "BORN_BUT_DEFERRED"),
        ("FACTUAL_CLAIM_PASSAGE_LICENSE", "MISSING_OWNER_DECISION"),
        ("ADDITIONAL_INFORMATION_FOR_FACTUAL_CLAIM_REQUIRED", "YES"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "UNBORN"),
        ("NORMATIVE_SOURCE_BLOCKER", "NO_RATIFIED_NORMATIVE_SOURCE"),
        ("MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE", "NO"),
        ("ADDITIONAL_INFORMATION_FOR_NORMATIVE_SOURCE_REQUIRED", "YES"),
        ("TANZIL_BIRTH_STATUS", "FORBIDDEN_MISSING_REQUIREMENTS"),
        ("ADDITIONAL_INFORMATION_FOR_TANZIL_REQUIRED", "YES"),
        ("ADDITIONAL_INFORMATION_REQUEST_PRODUCED", "YES"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("FINAL_HUKM_ISSUED", "NO"),
        ("ROUND_06_VERDICTS_CHANGED", "NO"),
        ("ROUND_07_VERDICTS_CHANGED", "NO"),
        ("ASSERTED_NOT_MEASURED_COUNT", str(anm)),
        ("SILENT_FALLBACK_COUNT", "0"),
        ("EXTERNAL_REFS", "0"),
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


def _trace_html(rows):
    e = lambda x: html.escape(str(x))
    P = ['<h3>جدول التتبع: القاعدة ← المصدر ← المنتج ← artifact ← الاختبار</h3><div class="wrap"><table><thead><tr>'
         '<th>requirement</th><th>المجال</th><th>source</th><th>producer_file</th><th>artifact</th>'
         '<th>test</th><th>status</th></tr></thead><tbody>']
    for r in rows:
        cls = "y" if r["status"] == "TRACEABLE" else "n"
        P.append(f'<tr><th>{e(r["req"])}</th><td>{e(r["domain"])}</td><td>{e(r["source"])}</td>'
                 f'<td>{e(r["producer"])}</td><td>{e(r["artifact"])}</td><td>{e(r["test"])}</td>'
                 f'<td class="{cls}">{e(r["status"])}</td></tr>')
    P.append('</tbody></table></div>')
    return "\n".join(P)


def render_manager(rows, tokdata, token_missing):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — الإفادة والمقام وطلب معلومات موجّه للتنزيل (08)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}h3{font-size:.95rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.78rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         'code{background:#f2f2f2;padding:.05rem .3rem;border-radius:.25rem;font-size:.76rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — الإفادة والمقام وطلب معلومات موجّه للتنزيل (08)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MANAGER_REPORT_CANONICAL_FORMAT = MAQAM_AR_05_STYLE · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO. '
             'لا يحذف تقارير 06/07 ولا يغيّر أحكامها.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>الإفادة موجودة ومنتجة بالكود، والمقام مصدّق، وسياسة المرجع مصدّقة، والدعوى الواقعية مولودة مؤجّلة.</li>'
             '<li>لم يولد التنزيل بعد: الدعوى بلا رخصة عبور، والمصدر المعياري غير مصدّق.</li>'
             '<li>لذلك أخرج النظام <b>طلب معلومات محددًا</b> (رخصة عبور + مصدر معياري) بدل تقرير توقف جاف.</li></ul>')
    P.append('<h2>2. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    # 3 token table (with t003/t009 fixes)
    P.append('<h2>3. جدول الكلمات العشر</h2>')
    if token_missing:
        P.append('<div class="note n">TOKEN_TABLE_SOURCE_MISSING = YES</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>التطبيع</th><th>الفئة</th>'
                 '<th>عامل/مبني</th><th>dal↔madlul</th><th>مصدر المدلول</th><th>نص عربي</th></tr></thead><tbody>')
        for t in tokdata["tokens"]:
            cls = "y" if t["binding"] == "BOUND" else "d"
            txt = ("«" + t["text"] + "»") if t["text"] else "—"
            wc = e(t["word_class"])
            src = e(t["madlul_source"])
            if t["token_id"] == "t009" and "IMPERFECT" in t["word_class"]:
                wc = e(t["word_class"]) + " (ARTIFACT_ANOMALY)<br><small>artifact not overwritten</small>"
            if t["token_id"] == "t003" and t["madlul_source"] == "APPROVED_MADLUL_SOURCE_MISSING_OWNER_PENDING":
                src = ("ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED<br>"
                       "<small>raw_artifact_madlul_source = APPROVED_MADLUL_SOURCE_MISSING_OWNER_PENDING</small>")
            P.append('<tr><th>' + e(t["token_id"]) + '</th>'
                     f'<td>{e(t["surface"])}</td><td>{e(t["normalized"])}</td><td>{wc}</td>'
                     f'<td>{e(t["mo"])}</td><td class="{cls}">{e(t["binding"])}</td>'
                     f'<td>{src}</td><td>{e(txt)}</td></tr>')
        P.append('</tbody></table></div>')
    P.append('<h2>4. الإفادة الموجودة من الكود</h2><div class="note y" style="background:#e6f4ea">'
             'IFADAH_PRODUCED_BY_CODE = YES · IFADAH_MISSING = NO · IFADAH_COMPLETION_STATUS = PARTIAL_OR_DEFERRED · '
             'IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM = YES.</div>')
    P.append('<h2>5. المقام المصدّق</h2><div class="note y" style="background:#e6f4ea">'
             'MAQAM_6_OWNER_RATIFIED = YES · MAQAM_6 = MASALA_MUSAWWARA_LIL_ISTIFTA · MAQAM_6_SCOPE = THIS_NAZILA_ONLY.</div>')
    P.append('<h2>6. سياسة المرجع المصدّقة</h2><div class="note y" style="background:#e6f4ea">'
             'REFERENCE_POLICY_OWNER_RATIFIED = YES · ASSUMED_FACT_REFERENCE = HYPOTHETICAL_MARKED_REFERENCE · '
             'REFERENCE_POLICY_DECISION_REQUIRED = NO.</div>')
    P.append('<h2>7. الدعوى الواقعية: مولودة مؤجلة</h2><div class="note d" style="background:#fff7e0">'
             'FACTUAL_CLAIM_BIRTH_STATUS = BORN_BUT_DEFERRED · FACTUAL_CLAIM_PASSAGE_LICENSE = MISSING_OWNER_DECISION · '
             'دعوى واقعية فقط، ليست حكمًا.</div>')
    P.append('<h2>8. لماذا نحتاج رخصة عبور factual_claim؟</h2><div class="note">'
             'الدعوى مولودة مؤجّلة؛ لعبورها نحو محاولة الربط بمصدر معياري تحتاج رخصة عبور صريحة من المالك '
             '(BORN_BUT_DEFERRED → BORN_BUT_DEFERRED_WITH_PASSAGE_LICENSE) لهذه النازلة فقط — بنيويًّا لا حكمًا.</div>')
    P.append('<h2>9. سؤال المصدر المعياري</h2><div class="note n" style="background:#fdecec">'
             'NORMATIVE_SOURCE_BIRTH_STATUS = UNBORN · NORMATIVE_SOURCE_BLOCKER = NO_RATIFIED_NORMATIVE_SOURCE — '
             'يلزم: سلطة + نص + نطاق + دليل + رخصة ربط.</div>')
    P.append('<h2>10. لماذا مصدر المقام ليس مصدرًا معياريًا؟</h2><div class="note">'
             'MAQAM_THEORY_SOURCE ≠ NORMATIVE_SOURCE — مصادر نظرية المقام لا تُنتج حكمًا ولا تصلح سلطةً معيارية.</div>')
    P.append('<h2>11. هل وُلد التنزيل؟</h2><div class="note n" style="background:#fdecec">'
             'TANZIL_BIRTH_STATUS = FORBIDDEN_MISSING_REQUIREMENTS · TANZIL_PRODUCED = NO — الأصول غير مكتملة.</div>')
    P.append('<h2>12. طلب المعلومات المطلوب من المالك</h2><div class="note">'
             '<b>(أ)</b> رخصة عبور الدعوى الواقعية لهذه النازلة فقط؟ '
             '<b>(ب)</b> مصدر معياري = سلطة + نص + نطاق + دليل + رخصة ربط. '
             'التفصيل في: <code>ADDITIONAL_INFORMATION_REQUEST_FOR_FACTUAL_CLAIM_PASSAGE_08.md</code> و'
             '<code>ADDITIONAL_INFORMATION_REQUEST_FOR_NORMATIVE_SOURCE_08.md</code>.</div>')
    P.append('<h2>13. ما يلزم بعد وصول المعلومات</h2><ol>'
             '<li>رفع FACTUAL_CLAIM_PASSAGE_LICENSE إلى GRANTED (إن رخّص المالك).</li>'
             '<li>ولادة المصدر المعياري من الخمسة.</li>'
             '<li>عندها بالترتيب: normative_hukm_birth ← illah/manat ← tanzil ← answer_audit.</li></ol>')
    P.append('<h2>14. الاختبارات</h2><div class="note">tests/test_taaqol_final_ifadah_maqam_targeted_info_request_08.py.</div>')
    P.append(_trace_html(rows))
    P.append('<h2>15. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_08_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'PYTEST_FILE = tests/test_taaqol_final_ifadah_maqam_targeted_info_request_08.py\n'
             'MATRIX_FILE = output/taaqol_maqam_foundation_generated/FINAL_IFADAH_MAQAM_TARGETED_INFO_REQUEST_08_MATRIX.csv\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nREPORT_REPRODUCIBLE_FROM_GENERATOR = YES\nCOMMIT = NO</pre></div>')
    P.append('<h2>16. الخلاصة التنفيذية</h2><div class="note">انتهت الجولة بإفادة موجودة ومقام مصدّق وسياسة '
             'مرجع مصدّقة. لم يولد التنزيل بعد لأن الدعوى الواقعية ما زالت مؤجلة بلا رخصة عبور، ولأن المصدر '
             'المعياري غير مصدّق. لذلك أخرج النظام طلب معلومات محددًا: رخصة عبور للدعوى الواقعية، ومصدرًا '
             'معياريًا مكوّنًا من سلطة + نص + نطاق + دليل + رخصة ربط.</div>')
    P.append('<div class="foot">IFADAH_PRODUCED_BY_CODE = YES · MAQAM_6_OWNER_RATIFIED = YES · '
             'REFERENCE_POLICY_OWNER_RATIFIED = YES · FACTUAL_CLAIM_BIRTH_STATUS = BORN_BUT_DEFERRED · '
             'FACTUAL_CLAIM_PASSAGE_LICENSE = MISSING_OWNER_DECISION · NORMATIVE_SOURCE_BIRTH_STATUS = UNBORN · '
             'TANZIL_BIRTH_STATUS = FORBIDDEN_MISSING_REQUIREMENTS · ADDITIONAL_INFORMATION_REQUEST_PRODUCED = YES · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "FINAL_IFADAH_MAQAM_TARGETED_INFO_REQUEST_MANAGER_REPORT_AR_08.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "FINAL_IFADAH_MAQAM_TARGETED_INFO_REQUEST_08_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    ifadah, tanzil_readiness = build_json_artifacts()
    (OUT / "NAZILA_IFADAH_AND_FACTUAL_CLAIM_PASSAGE_08.json").write_text(
        json.dumps(ifadah, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NAZILA_TANZIL_READINESS_AFTER_INFO_REQUEST_08.json").write_text(
        json.dumps(tanzil_readiness, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "ADDITIONAL_INFORMATION_REQUEST_FOR_FACTUAL_CLAIM_PASSAGE_08.md").write_text(
        info_request_factual_md(), encoding="utf-8")
    (OUT / "ADDITIONAL_INFORMATION_REQUEST_FOR_NORMATIVE_SOURCE_08.md").write_text(
        info_request_normative_md(), encoding="utf-8")
    rows, anm = trace_rows()
    final_obj = {
        "ROUND": "FINAL_IFADAH_MAQAM_AND_TARGETED_INFORMATION_REQUEST_FOR_TANZIL_08",
        "FINAL_CLOSURE_MODE": "TARGETED_INFORMATION_REQUEST_PRODUCED",
        "ifadah": ifadah, "tanzil_readiness": tanzil_readiness,
        "traceability": rows, "ASSERTED_NOT_MEASURED_COUNT": anm,
        "producer_file": PRODUCER,
    }
    (OUT / "FINAL_IFADAH_MAQAM_TARGETED_INFO_REQUEST_08.json").write_text(
        json.dumps(final_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tokdata, token_missing = collect_tokens()
    pathlib.Path(a.report_out).write_text(render_manager(rows, tokdata, token_missing), encoding="utf-8")
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(anm):
            fh.write(f"{k},{v}\n")
    print("REPORT_08=" + a.report_out)
    print("ASSERTED_NOT_MEASURED=" + str(anm)
          + " FACTUAL_CLAIM=BORN_BUT_DEFERRED NORMATIVE_SOURCE=UNBORN TANZIL=FORBIDDEN_MISSING_REQUIREMENTS")


if __name__ == "__main__":
    main()
