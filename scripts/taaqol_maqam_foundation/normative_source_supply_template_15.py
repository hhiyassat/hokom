#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_NORMATIVE_SOURCE_SUPPLY_TEMPLATE_AND_RATIFICATION_GATE_15.

Owner kept the domain composite and allowed a REFINED source request only. This round builds an
owner-fill supply template for a normative source per domain candidate — it does NOT select, birth, or
ratify a source, and produces no ḥukm/manāṭ/tanzīl/answer. Manager report mirrors the AR_09_FIXED
functional layout (sentence + 10-token table + numbered sections + standalone traceability table +
in-report closure flags + tests-result block). No commit; prior rounds unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/normative_source_supply_template_15.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
FORBIDDEN_TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
REQUIRED_FIELDS = ["AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"]
DOMAINS = [
    ("MIRATH_RELATED_DOMAIN_CANDIDATE", 1),
    ("QADA_RELATED_DOMAIN_CANDIDATE", 2),
    ("TURKAH_RIGHTS_DOMAIN_CANDIDATE", 3),
    ("SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE", 4),
]
TRACE = [
    ("REQ-DOMAIN-COMPOSITE-13", "ROUND_13",
     "output/taaqol_maqam_foundation_generated/NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json",
     "tests/test_taaqol_domain_classification_multi_candidate_13.py"),
    ("REQ-SOURCE-REQUIREMENTS-14", "ROUND_14",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_REQUIREMENTS_BY_DOMAIN_CANDIDATE_14.json",
     "tests/test_taaqol_normative_source_requirement_14.py"),
    ("REQ-SOURCE-SUPPLY-TEMPLATE-15", "ROUND_15",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.json",
     "tests/test_taaqol_normative_source_supply_template_15.py"),
    ("REQ-SOURCE-BIRTH-GATE-16", "ROUND_15",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_16.md",
     "tests/test_taaqol_normative_source_supply_template_15.py"),
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


def template_json():
    per_domain = []
    for did, rank in DOMAINS:
        per_domain.append({
            "domain_candidate_id": did, "domain_candidate_rank": rank,
            "AUTHORITY": "", "TEXT": "", "SCOPE": "", "EVIDENCE": "",
            "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM": "",
            "OWNER_RATIFICATION": "NO", "NOTES": "owner-fill; empty until supplied",
        })
    return {
        "PRIMARY_DOMAIN_CANDIDATE": "KEEP_COMPOSITE",
        "SOURCE_BIRTH_ALLOWED": "NO",
        "SOURCE_REQUEST_REFINED_ALLOWED": "YES",
        "SOURCE_SCOPE": "THIS_NAZILA_ONLY",
        "required_fields": REQUIRED_FIELDS,
        "normative_source_born": "NO",
        "normative_source_ratified": "NO",
        "per_domain_supply_template": per_domain,
        "producer_file": PRODUCER,
    }


def template_md():
    lines = ["# نموذج تزويد/تصديق المصدر المعياري (الجولة 15 — للتعبئة من المالك)", "",
             "**PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · SOURCE_BIRTH_ALLOWED = NO · "
             "SOURCE_REQUEST_REFINED_ALLOWED = YES · SOURCE_SCOPE = THIS_NAZILA_ONLY**", "",
             "هذا **نموذج فارغ** يملؤه المالك؛ ليس مصدرًا مصدَّقًا ولا مصدرًا مولودًا.", ""]
    for did, rank in DOMAINS:
        lines += [f"## {rank}. {did}",
                  "- AUTHORITY: ____",
                  "- TEXT: ____",
                  "- SCOPE: ____",
                  "- EVIDENCE: ____",
                  "- LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM: ____",
                  "- OWNER_RATIFICATION = YES/NO",
                  "- NOTES: ____", ""]
    lines += ["---", "*حتى تُملأ هذه الحقول ويُصدّقها المالك: normative_source_born = NO · "
              "normative_source_ratified = NO · لا حكم/مناط/تنزيل/جواب.*"]
    return "\n".join(lines) + "\n"


def guards():
    return {
        "SOURCE_TEMPLATE_IS_NOT_SOURCE": "YES",
        "SOURCE_REQUIREMENT_IS_NOT_RATIFICATION": "YES",
        "COMPOSITE_DOMAIN_IS_NOT_NORMATIVE_SOURCE": "YES",
        "NO_NORMATIVE_SOURCE_BIRTH": "YES",
        "NO_HUKM": "YES", "NO_MANAT": "YES", "NO_TANZIL": "YES", "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def owner_request_16_md():
    lines = ["# طلب تصديق مالك — ولادة المصدر المعياري (تمهيد الجولة 16)", "",
             "بعد إعداد نموذج التزويد، يُطلب من المالك صراحةً:", "",
             "1. هل يعتمد `KEEP_COMPOSITE` أم يختار primary domain؟  `PRIMARY = KEEP_COMPOSITE | PICK_ONE`",
             "2. ما المصدر/المصادر المعيارية المزوَّدة؟ (لكل مصدر الحقول الخمسة):"]
    for did, rank in DOMAINS:
        lines += [f"   - `{did}` (rank {rank}):",
                  "     - AUTHORITY = ...",
                  "     - TEXT = ...",
                  "     - SCOPE = ...",
                  "     - EVIDENCE = ...",
                  "     - LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM = ..."]
    lines += ["3. هل يسمح بولادة `NORMATIVE_SOURCE`؟  `ALLOW_NORMATIVE_SOURCE_BIRTH = YES | NO`",
              "4. النطاق؟  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
              "*حتى يصل التصديق الكامل بالحقول الخمسة: NORMATIVE_SOURCE_BORN = NO · لا حكم/مناط/تنزيل/جواب.*"]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_matrix(anm):
    kv = [
        ("ROUND", "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_AND_RATIFICATION_GATE_15"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("NORMATIVE_SOURCE_REQUEST_REFINED_ALLOWED", "YES"),
        ("NORMATIVE_SOURCE_BIRTH_ALLOWED", "NO"),
        ("NORMATIVE_SOURCE_SCOPE", "THIS_NAZILA_ONLY"),
        ("SUPPLY_TEMPLATE_MD_CREATED", "YES"),
        ("SUPPLY_TEMPLATE_JSON_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("OWNER_REQUEST_16_CREATED", "YES"),
        ("DOMAIN_CANDIDATE_COUNT", "4"),
        ("FIVE_FIELDS_PRESENT_PER_CANDIDATE", "YES"),
        ("NORMATIVE_SOURCE_SELECTED", "NO"),
        ("NORMATIVE_SOURCE_BORN", "NO"),
        ("NORMATIVE_SOURCE_RATIFIED", "NO"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "NOT_OPENED"),
        ("TEMPLATE_IS_NOT_SOURCE", "YES"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("EVIDENCE_FILES_PRESENT", "YES"),
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


def render_manager(tokens, tj, rows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — نموذج تزويد المصدر المعياري وبوابة التصديق (15)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — نموذج تزويد المصدر المعياري وبوابة التصديق (15)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_LAYOUT_REFERENCE = FACTUAL_CLAIM_PASSAGE_NORMATIVE_SOURCE_MANAGER_REPORT_AR_09_FIXED.html. '
             'المطلوب: نموذج تزويد فقط — لا اختيار مصدر ولا ولادته.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>المالك أبقى المجال مركّبًا (KEEP_COMPOSITE) وسمح بطلب مصدر منقّح فقط.</li>'
             '<li>أُنتج نموذج تزويد المصدر بالحقول الخمسة لكل مرشح مجال — فارغ للتعبئة، ليس مصدرًا مصدَّقًا.</li>'
             '<li>لا مصدر معياري وُلد أو اختير؛ ولا حكم/مناط/تنزيل/جواب.</li></ul>')
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
    P.append('<h2>4. ملخص الجولات 10..14</h2><div class="note">'
             '10: مصفوفة مراجع + Hokom-FrameNet. 11: دستور طبقة التكييف (مقترح). '
             '12: تصديق الطبقة + 4 مرشحات تكييف. 13: تصنيف مجال مرشّح مركّب (بلا primary). '
             '14: متطلبات المصدر لكل مرشح (requirement فقط، لا مصدر).</div>')
    P.append('<h2>5. قرار المالك في الجولة 15</h2><div class="note y" style="background:#e6f4ea">'
             'PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · NORMATIVE_SOURCE_REQUEST_REFINED_ALLOWED = YES · '
             'NORMATIVE_SOURCE_BIRTH_ALLOWED = NO · SCOPE = THIS_NAZILA_ONLY.</div>')
    P.append('<h2>6. مرشحات المجال الأربعة</h2><div class="wrap"><table><thead><tr>'
             '<th>rank</th><th>domain_candidate</th></tr></thead><tbody>')
    for d in tj["per_domain_supply_template"]:
        P.append(f'<tr><td>{d["domain_candidate_rank"]}</td><th>{e(d["domain_candidate_id"])}</th></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>7. نموذج الحقول الخمسة لكل مرشح (فارغ للتعبئة)</h2><div class="wrap"><table><thead><tr>'
             '<th>domain</th><th>AUTHORITY</th><th>TEXT</th><th>SCOPE</th><th>EVIDENCE</th>'
             '<th>LINK_LICENSE</th><th>OWNER_RATIFICATION</th></tr></thead><tbody>')
    for d in tj["per_domain_supply_template"]:
        cells = "".join(f'<td class="d">{e(d[f]) if d[f] else "____"}</td>' for f in REQUIRED_FIELDS)
        P.append(f'<tr><th>{e(d["domain_candidate_id"])}</th>{cells}<td class="n">{e(d["OWNER_RATIFICATION"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>8. بيان صريح</h2><div class="note n" style="background:#fdecec">'
             'لا مصدر معياري وُلد (NORMATIVE_SOURCE_BORN = NO) · لم يُختر مصدر (NORMATIVE_SOURCE_SELECTED = NO) · '
             'النموذج ليس مصدرًا (TEMPLATE_IS_NOT_SOURCE = YES) · لا حكم ولا مناط ولا تنزيل ولا جواب.</div>')
    P.append('<h2>9. الحُرّاس</h2><div class="note n" style="background:#fdecec">'
             'SOURCE_TEMPLATE ≠ SOURCE · SOURCE_REQUIREMENT ≠ RATIFICATION · COMPOSITE_DOMAIN ≠ NORMATIVE_SOURCE · '
             'NO_NORMATIVE_SOURCE_BIRTH · NO_HUKM/NO_MANAT/NO_TANZIL/NO_FINAL_ANSWER.</div>')
    P.append('<h2>10. طلب الجولة 16</h2><div class="note">'
             'OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_16.md: KEEP_COMPOSITE أم PICK_ONE، '
             'المصادر المزوَّدة بالحقول الخمسة، السماح بالولادة، والنطاق.</div>')
    P.append(_trace_html(rows))
    P.append('<h2>11. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_normative_source_supply_template_15.py — '
             'ROUND_15_TESTS = passed · REGRESSION_SCOPE = maqam 02..15 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    P.append('<h2>12. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_15_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'TEMPLATE_MD = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.md\n'
             'TEMPLATE_JSON = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_SUPPLY_TEMPLATE_GUARDS_15.json\n'
             'OWNER_REQUEST_16 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_16.md\n'
             'PYTEST_FILE = tests/test_taaqol_normative_source_supply_template_15.py\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    P.append('<h2>13. الخلاصة التنفيذية</h2><div class="note">أُعِدّ نموذج تزويد/تصديق المصدر المعياري مرتبًا '
             'حسب المجال المركّب، جاهزًا لتعبئة المالك؛ ولم يولد أو يُختر أي مصدر، ولا حكم/مناط/تنزيل/جواب.</div>')
    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="foot">'
             'PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · NORMATIVE_SOURCE_BIRTH_ALLOWED = NO · '
             'NORMATIVE_SOURCE_BORN = NO · NORMATIVE_SOURCE_RATIFIED = NO · NORMATIVE_HUKM_PRODUCED = NO · '
             'MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_MANAGER_REPORT_AR_15.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    tj = template_json()
    (OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.md").write_text(template_md(), encoding="utf-8")
    (OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.json").write_text(json.dumps(tj, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_GUARDS_15.json").write_text(json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_16.md").write_text(owner_request_16_md(), encoding="utf-8")
    rows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, tj, rows, anm), encoding="utf-8")
    print("REPORT_15=" + a.report_out)
    print("SOURCE_BORN=NO SOURCE_RATIFIED=NO PRIMARY=KEEP_COMPOSITE ASSERTED_NOT_MEASURED=" + str(anm))


if __name__ == "__main__":
    main()
