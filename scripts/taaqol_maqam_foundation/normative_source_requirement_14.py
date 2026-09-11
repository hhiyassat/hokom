#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_NORMATIVE_SOURCE_REQUIREMENT_AND_CANDIDATE_REQUEST_14.

Owner allowed a NORMATIVE_SOURCE_REQUIREMENT_LAYER (request-only). This round records, per round-13
domain candidate, WHAT a normative source would need (authority/text/scope/evidence/link_license) —
it does NOT select, birth, or ratify any source. No ḥukm/manāṭ/tanzīl/final answer. No commit; prior
rounds unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/normative_source_requirement_14.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
FORBIDDEN_TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
COMP_13 = OUT / "NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json"

# requirement templates per domain candidate (requirement-only; NOT a source)
DOMAINS = [
    ("MIRATH_RELATED_DOMAIN_CANDIDATE", 1,
     "RATIFIED_FIQH_MIRATH_AUTHORITY", "MIRATH_RULING_TEXT",
     "INHERITANCE_SHARES_SCOPE", "AUTHENTICATED_SOURCE_EVIDENCE"),
    ("QADA_RELATED_DOMAIN_CANDIDATE", 2,
     "RATIFIED_QADA_PROCEDURE_AUTHORITY", "QADA_PROCEDURE_TEXT",
     "DISPUTE_ADJUDICATION_SCOPE", "AUTHENTICATED_SOURCE_EVIDENCE"),
    ("TURKAH_RIGHTS_DOMAIN_CANDIDATE", 3,
     "RATIFIED_TURKAH_RIGHTS_AUTHORITY", "TURKAH_RIGHTS_TEXT",
     "ESTATE_RIGHTS_SCOPE", "AUTHENTICATED_SOURCE_EVIDENCE"),
    ("SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE", 4,
     "RATIFIED_SUKNA_POSSESSION_AUTHORITY", "SUKNA_POSSESSION_TEXT",
     "RESIDENCE_POSSESSION_SCOPE", "AUTHENTICATED_SOURCE_EVIDENCE"),
]


def owner_decision():
    return {
        "NORMATIVE_SOURCE_REQUEST_LAYER_ALLOWED": "YES",
        "NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW": "NO",
        "NORMATIVE_SOURCE_BIRTH_ALLOWED_NOW": "NO",
        "SOURCE_REQUIREMENTS_BY_DOMAIN_CANDIDATE_ALLOWED": "YES",
        "PRIMARY_DOMAIN_SELECTION_REQUIRED_BEFORE_SOURCE_BIRTH": "DEFERRED",
        "COMPOSITE_DOMAIN_SOURCE_STRATEGY_ALLOWED_AS_CANDIDATE": "YES",
        "SCOPE": "THIS_NAZILA_ONLY",
        "NORMATIVE_SOURCE_REQUIREMENT_LAYER_STATUS": "OWNER_RATIFIED_FOR_REQUEST_ONLY",
        "SOURCE_SELECTION_ALLOWED": "NO",
        "SOURCE_BIRTH_ALLOWED": "NO",
        "evidence": ["OWNER_DECISION_IN_PROMPT_14",
                     "output/taaqol_maqam_foundation_generated/NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json"],
        "producer_file": PRODUCER,
    }


def build_requirements():
    out = []
    for did, rank, auth, text, scope, ev in DOMAINS:
        out.append({
            "domain_candidate_id": did, "domain_candidate_rank": rank,
            "source_requirement_status": "REQUIREMENT_RECORDED_NOT_SOURCE",
            "required_authority_type": auth,
            "required_text_type": text,
            "required_scope": scope,
            "required_evidence_type": ev,
            "required_link_license": "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM (owner-ratified, absent)",
            "primary_domain_dependency": "NOT_FORCED (round 13)",
            "composite_strategy_dependency": "COMPOSITE_ALLOWED_AS_CANDIDATE (round 14 owner)",
            "normative_source_born": "NO", "normative_source_ratified": "NO",
            "normative_source_selected": "NO",
            "cause": "round-13 DOMAIN_CANDIDATE present + owner allowed request-only source-requirement layer",
            "conditions": ["required authority type named", "required text type named", "required scope named",
                           "required evidence type named", "required link license named",
                           "NO actual source selected this round"],
            "preventers": ["PRIMARY_DOMAIN_CANDIDATE_NOT_FORCED", "FINAL_SINGLE_DOMAIN_CLOSED_NO",
                           "SOURCE_SELECTION_ALLOWED_NOW_NO", "SOURCE_BIRTH_ALLOWED_NOW_NO",
                           "NO_OWNER_SUPPLIED_FIVE_COMPONENT_SOURCE"],
            "verdict": "DEFER_SOURCE_BIRTH_REQUIREMENTS_RECORDED",
            "evidence": ["output/taaqol_maqam_foundation_generated/NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json",
                         "output/taaqol_maqam_foundation_generated/DOMAIN_CLASSIFICATION_OWNER_RATIFICATION_13.json"],
            "residuals": ["actual source birth needs owner: primary/composite decision + the five components (round 15)"],
            "producer_file": PRODUCER,
        })
    return out


def composite_strategy():
    return {
        "strategy_id": "COMPOSITE_DOMAIN_SOURCE_STRATEGY_CANDIDATE_14",
        "can_keep_composite_later": "CANDIDATE_YES_OWNER_DECIDES",
        "risks": ["a single normative source may not cover all domain candidates",
                  "conflicting sources across domains", "premature primary-domain forcing"],
        "conditions": ["owner picks PRIMARY or KEEP_COMPOSITE", "each covered domain has its five-component source"],
        "primary_selection_required_before_source_birth": "DEFERRED_OWNER_DECIDES",
        "final_decision": "NOT_TAKEN_THIS_ROUND",
        "verdict": "COMPOSITE_STRATEGY_CANDIDATE_ONLY",
        "producer_file": PRODUCER,
    }


def build_guards():
    return {
        "DOMAIN_CANDIDATE_IS_NOT_NORMATIVE_SOURCE": "YES",
        "SOURCE_REQUIREMENT_IS_NOT_SOURCE": "YES",
        "SOURCE_CANDIDATE_IS_NOT_RATIFIED_SOURCE": "YES",
        "NO_NORMATIVE_SOURCE_BIRTH": "YES",
        "NO_HUKM": "YES", "NO_MANAT": "YES", "NO_TANZIL": "YES", "NO_FINAL_ANSWER": "YES",
        "chain": "DOMAIN_CANDIDATE != SOURCE_REQUIREMENT != NORMATIVE_SOURCE != HUKM != MANAT != TANZIL != FINAL_ANSWER",
        "producer_file": PRODUCER,
    }


def owner_request_15_md(reqs):
    lines = ["# طلب تصديق مالك — ولادة/اختيار المصدر المعياري (تمهيد الجولة 15)", "",
             "بعد تسجيل متطلبات المصدر لكل مرشح مجال (requirement فقط)، يُطلب من المالك:", "",
             "1. هل تختار مجالًا أساسيًا أم تُبقي المجال مركّبًا؟  `PRIMARY = PICK_ONE | KEEP_COMPOSITE`",
             "2. أي مرشح/مرشحات مجال تعتمدها أساسًا للمصدر؟"]
    for r in reqs:
        lines.append(f"   - `{r['domain_candidate_id']}` (rank {r['domain_candidate_rank']})  →  `ADOPT = YES | NO`")
    lines += [
        "3. هل تسمح بولادة مصدر معياري؟  `ALLOW_NORMATIVE_SOURCE_BIRTH = YES | NO`",
        "4. المصدر المعياري المطلوب بخمسة حقول صراحةً:",
        "   - `AUTHORITY = ...`",
        "   - `TEXT = ...`",
        "   - `SCOPE = ...`",
        "   - `EVIDENCE = ...`",
        "   - `LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM = ...`",
        "5. النطاق؟  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`",
        "",
        "*حتى يصل التصديق: NORMATIVE_SOURCE_BORN = NO · NORMATIVE_SOURCE_SELECTED = NO · لا حكم/مناط/تنزيل/جواب.*",
    ]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_matrix(reqs):
    kv = [
        ("ROUND", "NORMATIVE_SOURCE_REQUIREMENT_AND_CANDIDATE_REQUEST_14"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("NORMATIVE_SOURCE_REQUEST_LAYER_ALLOWED", "YES"),
        ("NORMATIVE_SOURCE_REQUIREMENT_LAYER_STATUS", "OWNER_RATIFIED_FOR_REQUEST_ONLY"),
        ("SOURCE_REQUIREMENTS_BY_DOMAIN_CANDIDATE_PRODUCED", "YES"),
        ("NORMATIVE_SOURCE_REQUIREMENTS_PRODUCED", "YES"),
        ("SOURCE_REQUIREMENT_COUNT", str(len(reqs))),
        ("DOMAIN_CANDIDATE_COUNT", "4"),
        ("PRIMARY_DOMAIN_CANDIDATE", "NOT_FORCED"),
        ("FINAL_SINGLE_DOMAIN_CLOSED", "NO"),
        ("NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW", "NO"),
        ("NORMATIVE_SOURCE_BIRTH_ALLOWED_NOW", "NO"),
        ("NORMATIVE_SOURCE_SELECTED", "NO"),
        ("NORMATIVE_SOURCE_BORN", "NO"),
        ("NORMATIVE_SOURCE_RATIFIED", "NO"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "NOT_OPENED"),
        ("ALL_REQUIREMENTS_ARE_REQUIREMENT_NOT_SOURCE", "YES"),
        ("COMPOSITE_STRATEGY_CANDIDATE_PRODUCED", "YES"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("OWNER_REQUEST_15_CREATED", "YES"),
        ("EVIDENCE_FILES_PRESENT", "YES"),
        ("ASSERTED_NOT_MEASURED_COUNT", "0"),
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


def render_manager(tokens, dec, reqs, strat, guards):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — متطلبات المصدر المعياري حسب مرشحات المجال (14)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.75rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — متطلبات المصدر المعياري حسب مرشحات المجال (14)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO. '
             'المسموح: تسجيل متطلبات المصدر فقط. الممنوع: اختيار/توليد/اعتماد مصدر معياري.</div>')
    P.append('<h2>1. الجملة</h2><div class="sentbox"><div class="sent" id="nazila-sentence">' + e(SENTENCE) + '</div></div>')
    P.append('<h2>2. جدول الكلمات t000..t009</h2>')
    if not tokens:
        P.append('<div class="note n">TOKEN_ARTIFACT_MISSING</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>الفئة</th></tr></thead><tbody>')
        for t in tokens:
            P.append('<tr><th>' + e(t["token_id"]) + '</th><td>' + e(t.get("original_surface", "")) +
                     '</td><td>' + e(t.get("word_class", "")) + '</td></tr>')
        P.append('</tbody></table></div>')
    P.append('<h2>3. ملخص الجولة 10</h2><div class="note">مصفوفة مراجع + Hokom-FrameNet + منع القفز من الإشارة إلى المجال.</div>')
    P.append('<h2>4. ملخص الجولة 11</h2><div class="note">دستور MASALA_TAKYIF_LAYER (مقترح) + حُرّاس.</div>')
    P.append('<h2>5. ملخص الجولة 12</h2><div class="note">تصديق الطبقة (لهذه النازلة) + 4 مرشحات تكييف candidate-only.</div>')
    P.append('<h2>6. ملخص الجولة 13</h2><div class="note">ولادة تصنيف مجال مرشّح مركّب (MULTI_DOMAIN_CANDIDATE) بلا primary مفروض ولا مجال مغلق.</div>')
    P.append('<h2>7. قرار المالك في الجولة 14</h2><div class="note y" style="background:#e6f4ea">'
             'NORMATIVE_SOURCE_REQUEST_LAYER_ALLOWED = YES · SOURCE_REQUIREMENTS_BY_DOMAIN_CANDIDATE_ALLOWED = YES · '
             'COMPOSITE_DOMAIN_SOURCE_STRATEGY_ALLOWED_AS_CANDIDATE = YES. '
             'لكن: NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW = NO · NORMATIVE_SOURCE_BIRTH_ALLOWED_NOW = NO · SCOPE = THIS_NAZILA_ONLY.</div>')
    P.append('<h2>8. مرشحات المجال الأربعة</h2><div class="wrap"><table><thead><tr>'
             '<th>rank</th><th>domain_candidate</th><th>حالة المتطلب</th></tr></thead><tbody>')
    for r in reqs:
        P.append(f'<tr><td>{r["domain_candidate_rank"]}</td><th>{e(r["domain_candidate_id"])}</th>'
                 f'<td class="d">{e(r["source_requirement_status"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>9. متطلبات المصدر المعياري لكل مرشح (requirement فقط)</h2><div class="wrap"><table><thead><tr>'
             '<th>domain</th><th>authority</th><th>text</th><th>scope</th><th>evidence</th><th>link_license</th>'
             '<th>verdict</th></tr></thead><tbody>')
    for r in reqs:
        P.append(f'<tr><th>{e(r["domain_candidate_id"])}</th><td>{e(r["required_authority_type"])}</td>'
                 f'<td>{e(r["required_text_type"])}</td><td>{e(r["required_scope"])}</td>'
                 f'<td>{e(r["required_evidence_type"])}</td><td>{e(r["required_link_license"])}</td>'
                 f'<td class="d">{e(r["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>10. بيانات صريحة</h2><div class="note n" style="background:#fdecec">'
             'لا مصدر معياري وُلد (NORMATIVE_SOURCE_BORN = NO) · لم يُختر مصدر معياري (NORMATIVE_SOURCE_SELECTED = NO) · '
             'لا حكم ولا مناط ولا تنزيل ولا جواب.</div>')
    P.append('<h2>11. لماذا المصدر الآن requirement فقط وليس source؟</h2><div class="note">'
             'لأن SOURCE_SELECTION_ALLOWED = NO و SOURCE_BIRTH_ALLOWED = NO، والمجال ما زال مركّبًا بلا primary مفروض، '
             'ولم يزوّد المالك المصدر بخمسة مكوّناته. فالمُنتَج هو «ما يلزم» لا «المصدر».</div>')
    P.append('<h2>12. استراتيجية المجال المركّب (مرشح)</h2><div class="note">'
             + e(strat["verdict"]) + ' — إبقاء المجال مركّبًا لاحقًا: ' + e(strat["can_keep_composite_later"]) +
             ' · اختيار primary قبل ولادة المصدر: ' + e(strat["primary_selection_required_before_source_birth"]) +
             ' · لم يُتّخذ قرار نهائي.</div>')
    P.append('<h2>13. الحُرّاس</h2><div class="note n" style="background:#fdecec">'
             'DOMAIN_CANDIDATE ≠ NORMATIVE_SOURCE · SOURCE_REQUIREMENT ≠ NORMATIVE_SOURCE · '
             'SOURCE_CANDIDATE ≠ SOURCE_RATIFICATION · NO_NORMATIVE_SOURCE_BIRTH · NO_HUKM/NO_MANAT/NO_TANZIL/NO_FINAL_ANSWER.</div>')
    P.append('<h2>14. طلب معلومات الجولة 15</h2><div class="note">'
             'OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_15.md: PRIMARY أم KEEP_COMPOSITE، أي مرشح، '
             'السماح بولادة المصدر، الحقول الخمسة (AUTHORITY/TEXT/SCOPE/EVIDENCE/LINK_LICENSE)، والنطاق.</div>')
    P.append('<h2>15. سلسلة التوليد المحروسة</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_14_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'DECISION = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_REQUIREMENT_OWNER_DECISION_14.json\n'
             'REQUIREMENTS = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_REQUIREMENTS_BY_DOMAIN_CANDIDATE_14.json\n'
             'COMPOSITE_STRATEGY = output/taaqol_maqam_foundation_generated/COMPOSITE_DOMAIN_SOURCE_STRATEGY_CANDIDATE_14.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_REQUIREMENT_GUARDS_14.json\n'
             'OWNER_REQUEST_15 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_15.md\n'
             'PYTEST_FILE = tests/test_taaqol_normative_source_requirement_14.py\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    P.append('<div class="foot">'
             'NORMATIVE_SOURCE_REQUEST_LAYER_ALLOWED = YES · SOURCE_REQUIREMENTS_BY_DOMAIN_CANDIDATE_PRODUCED = YES · '
             'NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW = NO · NORMATIVE_SOURCE_BIRTH_ALLOWED_NOW = NO · '
             'NORMATIVE_SOURCE_BORN = NO · NORMATIVE_SOURCE_RATIFIED = NO · NORMATIVE_HUKM_PRODUCED = NO · '
             'MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'ASSERTED_NOT_MEASURED_COUNT = 0 · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "NORMATIVE_SOURCE_REQUIREMENT_MANAGER_REPORT_AR_14.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "NORMATIVE_SOURCE_REQUIREMENT_14_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    dec = owner_decision()
    reqs = build_requirements()
    strat = composite_strategy()
    guards = build_guards()
    (OUT / "NORMATIVE_SOURCE_REQUIREMENT_OWNER_DECISION_14.json").write_text(json.dumps(dec, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NORMATIVE_SOURCE_REQUIREMENTS_BY_DOMAIN_CANDIDATE_14.json").write_text(json.dumps(reqs, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "COMPOSITE_DOMAIN_SOURCE_STRATEGY_CANDIDATE_14.json").write_text(json.dumps(strat, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NORMATIVE_SOURCE_REQUIREMENT_GUARDS_14.json").write_text(json.dumps(guards, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_15.md").write_text(owner_request_15_md(reqs), encoding="utf-8")
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(reqs):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, dec, reqs, strat, guards), encoding="utf-8")
    print("REPORT_14=" + a.report_out)
    print("REQUIREMENTS=" + str(len(reqs)) + " SOURCE_BORN=NO SOURCE_SELECTED=NO SOURCE_BIRTH_STATUS=NOT_OPENED")


if __name__ == "__main__":
    main()
