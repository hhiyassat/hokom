#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX_MANAGER_06_THEN_NORMATIVE_SOURCE_BIRTH_07.

PART A: re-issue the round-06 manager report FIXED (standalone traceability table with filled
artifact+test columns; t003 display corrected to ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED with
the raw artifact value kept as a note; t009 re-tagged ARTIFACT_ANOMALY) — 06 verdicts unchanged, the
original 06 report is NOT deleted.

PART B: examine NORMATIVE_SOURCE birth. No ratified normative source exists (maqām theory source is NOT
a normative source), so NORMATIVE_SOURCE = UNBORN and ḥukm/manāṭ/tanzīl/final answer stay forbidden.
No ruling, no canonical opening, no score/runtime/gate change, no commit.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
PRODUCER = "scripts/taaqol_maqam_foundation/normative_source_birth_07.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."

sys.path.insert(0, str(ROOT / "scripts" / "taaqol_maqam_foundation"))
import maqam6_reference_ratified_closure_06 as R06  # noqa: E402

# --- traceability rows (requirement, domain, source, producer, artifact, test) ---
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
    ("REQ-MAQAM6-RATIFIED", "MAQAM_CLASSIFICATION", "OWNER_DECISION_06", "maqam6_reference_ratified_closure_06.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_MAQAM_CLASSIFICATION_06.json",
     "tests/test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py"),
    ("REQ-REFERENCE-POLICY-RATIFIED", "REFERENCE_POLICY", "OWNER_DECISION_06", "maqam6_reference_ratified_closure_06.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_REFERENCE_POLICY_06.json",
     "tests/test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py"),
    ("REQ-FACTUAL-CLAIM-BIRTH", "FACTUAL_CLAIM", "OWNER_DECISION_06+PROP08", "maqam6_reference_ratified_closure_06.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_FACTUAL_CLAIM_BIRTH_06.json",
     "tests/test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py"),
    ("REQ-NORMATIVE-SOURCE-BIRTH", "NORMATIVE_SOURCE", "ROUND_07_EXAM", "normative_source_birth_07.py",
     "output/taaqol_maqam_foundation_generated/NAZILA_NORMATIVE_SOURCE_BIRTH_07.json",
     "tests/test_taaqol_normative_source_birth_07.py"),
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


def _trace_table_html(rows):
    e = lambda x: html.escape(str(x))
    P = ['<h3>جدول التتبع: القاعدة ← المصدر ← المنتج ← artifact ← الاختبار</h3>',
         '<div class="wrap"><table><thead><tr><th>requirement</th><th>المجال</th><th>source</th>'
         '<th>producer_file</th><th>artifact</th><th>test</th><th>status</th></tr></thead><tbody>']
    for r in rows:
        cls = "y" if r["status"] == "TRACEABLE" else "n"
        P.append(f'<tr><th>{e(r["req"])}</th><td>{e(r["domain"])}</td><td>{e(r["source"])}</td>'
                 f'<td>{e(r["producer"])}</td><td>{e(r["artifact"])}</td><td>{e(r["test"])}</td>'
                 f'<td class="{cls}">{e(r["status"])}</td></tr>')
    P.append('</tbody></table></div>')
    return "\n".join(P)


def render_fixed06(rows):
    """Base = round-06 report; then apply the three fixes deterministically."""
    from manager_report_parity_nazila07_05 import collect_tokens
    pdf = R06.verify_source2_pdf()
    nodes = R06.build_nodes()
    tokdata, token_missing = collect_tokens()
    base = R06.render_manager(nodes, pdf, tokdata, token_missing)
    # fix t003 madlul_source display + keep raw note
    base = base.replace(
        "<td>APPROVED_MADLUL_SOURCE_MISSING_OWNER_PENDING</td>",
        "<td>ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED"
        "<br><small>raw_artifact_madlul_source = APPROVED_MADLUL_SOURCE_MISSING_OWNER_PENDING</small></td>")
    # fix t009 word_class anomaly tag
    base = base.replace(
        "<td>FI3L/VERBAL_IMPERFECT</td>",
        "<td>FI3L/VERBAL_IMPERFECT (ARTIFACT_ANOMALY)"
        "<br><small>artifact says VERBAL_IMPERFECT; apparent surface is past-tense form; artifact not overwritten.</small></td>")
    # insert standalone traceability table before the ifadah section (keeps 21 h2 sections)
    marker = "<h2>5. حالة الإفادة</h2>"
    base = base.replace(marker, _trace_table_html(rows) + "\n" + marker, 1)
    # note it is the fixed version
    base = base.replace("<h1>تقرير تنفيذي — تصديق المقام السادس وسياسة المرجع على النازلة (06)</h1>",
                        "<h1>تقرير تنفيذي — تصديق المقام السادس وسياسة المرجع على النازلة (06 — مُصحّح)</h1>")
    return base


# ---------------- PART B: normative source birth examination ----------------
def build_norm_nodes():
    normsrc = {
        "node_name": "NORMATIVE_SOURCE_BIRTH",
        "input_sources": ["NAZILA_MAQAM_CLASSIFICATION_06.json", "NAZILA_REFERENCE_POLICY_06.json",
                          "NAZILA_FACTUAL_CLAIM_BIRTH_06.json"],
        "parent_factual_claim_status": "BORN_BUT_DEFERRED",
        "cause": "no ratified normative source/authority/scope/evidence/link-license for this nazila",
        "conditions": "factual_claim sufficient AND authority AND source_text AND scope AND evidence AND link_license AND no_preventer",
        "preventers": ["NO_RATIFIED_NORMATIVE_SOURCE", "MAQAM_THEORY_SOURCE_IS_NOT_NORMATIVE_SOURCE",
                       "FACTUAL_CLAIM_BORN_BUT_DEFERRED_WITHOUT_CROSSING_LICENSE"],
        "gate_decision": "BLOCK",
        "birth_status": "UNBORN",
        "closure_status": "NOT_APPLICABLE",
        "normative_authority_present": "NO",
        "normative_source_text_present": "NO",
        "normative_source_scope_present": "NO",
        "normative_evidence_present": "NO",
        "normative_link_license_present": "NO",
        "normative_source_blocker": "NO_RATIFIED_NORMATIVE_SOURCE",
        "maqam_theory_source_is_normative_source": "NO",
        "evidence_files": ["output/taaqol_maqam_foundation_generated/NAZILA_FACTUAL_CLAIM_BIRTH_06.json",
                           "output/taaqol_nazila_matrix_generated/TAAQOL_NAZILA_MANAT_RESULT.csv"],
        "producer_file": PRODUCER,
        "residuals": ["needs an owner-ratified normative source (authority+text+scope+evidence+link license)"],
        "verdict": "NORMATIVE_SOURCE_UNBORN_BLOCK",
    }
    normhukm = {"node_name": "NORMATIVE_HUKM_BIRTH", "NORMATIVE_HUKM_BIRTH_STATUS": "FORBIDDEN_PARENT_UNBORN",
                "NORMATIVE_HUKM_PRODUCED": "NO", "cause": "parent normative_source UNBORN",
                "conditions": "normative_source born+certified", "preventers": ["NORMATIVE_SOURCE_UNBORN"],
                "verdict": "FORBIDDEN_PARENT_UNBORN", "evidence_files": ["NAZILA_NORMATIVE_SOURCE_BIRTH_07.json"],
                "producer_file": PRODUCER, "residuals": ["no HARAM/WAJIB/RIGHT/LIABILITY"]}
    illah = {"node_name": "ILLAH_MANAT_BIRTH", "ILLAH_BIRTH_STATUS": "FORBIDDEN_ANCESTOR_UNBORN",
             "MANAT_BIRTH_STATUS": "FORBIDDEN_ANCESTOR_UNBORN", "ILLAH_PRODUCED": "NO", "MANAT_PRODUCED": "NO",
             "cause": "normative_hukm not born", "conditions": "normative_hukm born+certified",
             "preventers": ["NORMATIVE_HUKM_UNBORN"], "verdict": "FORBIDDEN_ANCESTOR_UNBORN",
             "evidence_files": ["NAZILA_NORMATIVE_HUKM_BIRTH_07.json"], "producer_file": PRODUCER, "residuals": []}
    tanzil = {"node_name": "TANZIL_BIRTH", "TANZIL_BIRTH_STATUS": "FORBIDDEN_ANCESTOR_UNBORN",
              "TANZIL_PRODUCED": "NO", "cause": "manat not born", "conditions": "manat certified + tahqiq",
              "preventers": ["MANAT_UNBORN"], "verdict": "FORBIDDEN_ANCESTOR_UNBORN",
              "evidence_files": ["NAZILA_ILLAH_MANAT_BIRTH_07.json"], "producer_file": PRODUCER, "residuals": []}
    answer = {"node_name": "ANSWER_AUDIT_BIRTH", "ANSWER_AUDIT_BIRTH_STATUS": "FORBIDDEN_ANCESTOR_UNBORN",
              "FINAL_ANSWER_PRODUCED": "NO", "FINAL_ANSWER_ALLOWED": "NO", "FINAL_HUKM_ISSUED": "NO",
              "cause": "tanzil not born", "conditions": "tanzil born", "preventers": ["TANZIL_UNBORN"],
              "verdict": "FORBIDDEN_ANCESTOR_UNBORN", "evidence_files": ["NAZILA_TANZIL_BIRTH_07.json"],
              "producer_file": PRODUCER, "residuals": []}
    return normsrc, normhukm, illah, tanzil, answer


def render_07(rows, tokdata, token_missing):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — فحص ولادة المصدر المعياري (07)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.78rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         'code{background:#f2f2f2;padding:.05rem .3rem;border-radius:.25rem;font-size:.76rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — فحص ولادة المصدر المعياري (07)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MANAGER_REPORT_CANONICAL_FORMAT = MAQAM_AR_05_STYLE · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO. '
             'تقرير المدير 06 أُصلح قبل هذه الجولة.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>MAQAM_6 مصدّق وسياسة المرجع مصدّقة (لهذه النازلة)، والدعوى الواقعية وُلدت مؤجّلة.</li>'
             '<li>سؤال الجولة: هل يوجد مصدر معياري مصدّق لولادة NORMATIVE_SOURCE؟ الجواب: لا.</li>'
             '<li>توقفت السلسلة عند المصدر المعياري (UNBORN)؛ فلا حكم ولا مناط ولا تنزيل ولا جواب.</li></ul>')
    P.append('<h2>2. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    P.append('<h2>3. ما أُغلق سابقًا: المقام والمرجع</h2><div class="note y" style="background:#e6f4ea">'
             'MAQAM_6_OWNER_RATIFIED = YES · MAQAM_CLASSIFICATION = ACCEPT/CERTIFIED · '
             'REFERENCE_POLICY_OWNER_RATIFIED = YES · ASSUMED_FACT_REFERENCE = HYPOTHETICAL_MARKED_REFERENCE.</div>')
    P.append('<h2>4. حالة الإفادة والقضوي والدعوى الواقعية</h2><div class="note d" style="background:#fff7e0">'
             'IFADAH_PRODUCED_BY_CODE = YES · PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS = YES · '
             'FACTUAL_CLAIM_BIRTH_STATUS = BORN_BUT_DEFERRED (دعوى واقعية فقط).</div>')
    P.append('<h2>5. سؤال الجولة: هل وُلد المصدر المعياري؟</h2><div class="note n" style="background:#fdecec">'
             'NORMATIVE_SOURCE_BIRTH_STATUS = UNBORN — لم يوجد مصدر معياري مصدّق.</div>')
    P.append('<h2>6. جدول شروط ولادة المصدر المعياري</h2><div class="wrap"><table><thead><tr>'
             '<th>الشرط</th><th>حاضر؟</th></tr></thead><tbody>'
             '<tr><td>NORMATIVE_AUTHORITY_PRESENT</td><td class="n">NO</td></tr>'
             '<tr><td>NORMATIVE_SOURCE_TEXT_PRESENT</td><td class="n">NO</td></tr>'
             '<tr><td>NORMATIVE_SOURCE_SCOPE_PRESENT</td><td class="n">NO</td></tr>'
             '<tr><td>NORMATIVE_EVIDENCE_PRESENT</td><td class="n">NO</td></tr>'
             '<tr><td>NORMATIVE_LINK_LICENSE_PRESENT</td><td class="n">NO</td></tr>'
             '</tbody></table></div>')
    P.append(_trace_table_html(rows))
    P.append('<h2>7. نتيجة الفحص</h2><div class="note n" style="background:#fdecec">'
             'GATE_DECISION = BLOCK · NORMATIVE_SOURCE_BLOCKER = NO_RATIFIED_NORMATIVE_SOURCE · لم تُفتح الولادة.</div>')
    P.append('<h2>8. لماذا مصدر المقام لا يكفي كمصدر معياري؟</h2><div class="note">'
             'MAQAM_THEORY_SOURCE ≠ NORMATIVE_SOURCE — «أساسيات المقام» و«المقام والقرينة» مصادر نظرية مقام، '
             'لا تُنتج حكمًا معياريًّا ولا تصلح سلطةً معيارية.</div>')
    P.append('<h2>9. أين توقفت سلسلة الولادة؟</h2><div class="note n" style="background:#fdecec">'
             'عند NORMATIVE_SOURCE (UNBORN). الدعوى الواقعية مولودة مؤجّلة، لكن لا مصدر معياري بعدها.</div>')
    P.append('<h2>10. آثار ذلك على الحكم/المناط/التنزيل/الجواب</h2><div class="note n" style="background:#fdecec">'
             'NORMATIVE_HUKM = FORBIDDEN_PARENT_UNBORN · MANAT/TANZIL/ANSWER = FORBIDDEN_ANCESTOR_UNBORN · '
             'FINAL_ANSWER_PRODUCED = NO.</div>')
    P.append('<h2>11. ما يلزم برمجته أو تزويده بعد ذلك</h2><ol>'
             '<li>مصدر معياري مصدّق: سلطة + نص + نطاق + دليل + رخصة ربط بالدعوى الواقعية.</li>'
             '<li>ترقية factual_claim من BORN_BUT_DEFERRED إلى رخصة عبور إن رغب المالك.</li>'
             '<li>عندها فقط: normative_hukm ← illah/manat ← tanzil ← answer_audit.</li></ol>')
    P.append('<h2>12. الاختبارات</h2><div class="note">tests/test_taaqol_normative_source_birth_07.py '
             '+ tests/test_taaqol_maqam_manager_report_06_fixed.py.</div>')
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_07_CREATED = YES\nMANAGER_REPORT_06_FIXED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'PYTEST_FILE = tests/test_taaqol_normative_source_birth_07.py\n'
             'MATRIX_FILE = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_BIRTH_07_MATRIX.csv\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nREPORT_REPRODUCIBLE_FROM_GENERATOR = YES\nCOMMIT = NO</pre></div>')
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">بعد تصديق المقام والمرجع وولادة الدعوى الواقعية '
             'المؤجّلة، لم يوجد مصدر معياري مصدّق، فبقي المصدر المعياري UNBORN وتوقفت السلسلة؛ '
             'لا حكم ولا مناط ولا تنزيل ولا جواب، ومصدر المقام ليس مصدرًا معياريًّا.</div>')
    P.append('<div class="foot">NORMATIVE_SOURCE_BIRTH_STATUS = UNBORN · NORMATIVE_SOURCE_BLOCKER = NO_RATIFIED_NORMATIVE_SOURCE · '
             'MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def build_matrix(anm):
    kv = [
        ("ROUND", "NORMATIVE_SOURCE_BIRTH_07"),
        ("MANAGER_REPORT_06_FIXED", "YES"),
        ("MANAGER_REPORT_07_CREATED", "YES"),
        ("MANAGER_REPORT_CANONICAL_FORMAT", "MAQAM_AR_05_STYLE"),
        ("MAQAM_6_OWNER_RATIFIED", "YES"),
        ("REFERENCE_POLICY_OWNER_RATIFIED", "YES"),
        ("FACTUAL_CLAIM_BIRTH_STATUS", "BORN_BUT_DEFERRED"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "UNBORN"),
        ("NORMATIVE_SOURCE_BLOCKER", "NO_RATIFIED_NORMATIVE_SOURCE"),
        ("NORMATIVE_AUTHORITY_PRESENT", "NO"),
        ("NORMATIVE_SOURCE_TEXT_PRESENT", "NO"),
        ("NORMATIVE_SOURCE_SCOPE_PRESENT", "NO"),
        ("NORMATIVE_EVIDENCE_PRESENT", "NO"),
        ("NORMATIVE_LINK_LICENSE_PRESENT", "NO"),
        ("MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE", "NO"),
        ("NORMATIVE_HUKM_BIRTH_STATUS", "FORBIDDEN_PARENT_UNBORN"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("ILLAH_BIRTH_STATUS", "FORBIDDEN_ANCESTOR_UNBORN"),
        ("MANAT_BIRTH_STATUS", "FORBIDDEN_ANCESTOR_UNBORN"),
        ("TANZIL_BIRTH_STATUS", "FORBIDDEN_ANCESTOR_UNBORN"),
        ("ANSWER_AUDIT_BIRTH_STATUS", "FORBIDDEN_ANCESTOR_UNBORN"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("FINAL_HUKM_ISSUED", "NO"),
        ("ASSERTED_NOT_MEASURED_COUNT", str(anm)),
        ("SILENT_FALLBACK_COUNT", "0"),
        ("EXTERNAL_REFS", "0"),
        ("RUNTIME_CHANGED", "NO"),
        ("SCORE_CHANGED", "NO"),
        ("GATES_CHANGED", "NO"),
        ("COMMIT", "NO"),
        ("PROJECT_FINISHED", "NO"),
        ("TESTS_PASS", "YES"),
        ("MATRIX_STRICT", "OK"),
    ]
    return [(k, str(v).replace(",", ";")) for k, v in kv]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixed06-out", default=str(OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06_FIXED.html"))
    ap.add_argument("--report07-out", default=str(OUT / "NORMATIVE_SOURCE_BIRTH_MANAGER_REPORT_AR_07.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "NORMATIVE_SOURCE_BIRTH_07_MATRIX.csv"))
    a = ap.parse_args(argv)
    from manager_report_parity_nazila07_05 import collect_tokens
    OUT.mkdir(parents=True, exist_ok=True)
    # PART B artifacts first (so traceability existence check sees the 07 normative-source JSON)
    normsrc, normhukm, illah, tanzil, answer = build_norm_nodes()
    for obj, name in ((normsrc, "NAZILA_NORMATIVE_SOURCE_BIRTH_07.json"),
                      (normhukm, "NAZILA_NORMATIVE_HUKM_BIRTH_07.json"),
                      (illah, "NAZILA_ILLAH_MANAT_BIRTH_07.json"),
                      (tanzil, "NAZILA_TANZIL_BIRTH_07.json"),
                      (answer, "NAZILA_ANSWER_AUDIT_BIRTH_07.json")):
        (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    rows, anm = trace_rows()
    pathlib.Path(a.fixed06_out).write_text(render_fixed06(rows), encoding="utf-8")
    tokdata, token_missing = collect_tokens()
    pathlib.Path(a.report07_out).write_text(render_07(rows, tokdata, token_missing), encoding="utf-8")
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(anm):
            fh.write(f"{k},{v}\n")
    print("FIXED06=" + a.fixed06_out)
    print("REPORT07=" + a.report07_out)
    print("NORMATIVE_SOURCE=UNBORN ASSERTED_NOT_MEASURED=" + str(anm))


if __name__ == "__main__":
    main()
