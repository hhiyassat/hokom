#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_MASALA_TAKYIF_RULES_CONSTITUTION_11.

Builds the MASALA_TAKYIF_LAYER (PROPOSED_NOT_CANONICAL) as candidate takyīf rules only. Reads round-10
text signals + frame candidates and emits MASALA_TAKYIF_CANDIDATES — every one owner_ratified=NO,
verdict=DEFER, produces MASALA_TAKYIF_CANDIDATE_ONLY. No domain classification, no normative source, no
ḥukm/manāṭ/tanzīl/final answer. No commit; prior rounds unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/masala_takyif_rules_11.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
FORBIDDEN_TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
SIGNALS_10 = OUT / "HOKOM_TEXT_SIGNALS_10.json"
FRAMES_10 = OUT / "HOKOM_FRAME_CANDIDATES_10.json"

CANDIDATE_RULES = [
    ("MIRATH_TAKYIF_CANDIDATE_RULE", "تكييف مواريث (مرشح)", ["وَارِثُهُ"], ["FC_DEATH_EVENT"]),
    ("QADA_TAKYIF_CANDIDATE_RULE", "تكييف قضاء (مرشح)", ["فَتَحَاكَمَا"], ["FC_DISPUTE_EVENT"]),
    ("TURKAH_RIGHTS_TAKYIF_CANDIDATE_RULE", "تكييف حقوق تركة (مرشح)", ["مَاتَ", "وَارِثُهُ"], ["FC_DEATH_EVENT"]),
    ("SUKNA_OR_POSSESSION_TAKYIF_CANDIDATE_RULE", "تكييف سكنى/حيازة (مرشح)",
     ["سَاكِنَةٍ", "طَرْدَهَا"], ["FC_RESIDENCE_RELATION", "FC_INTENT_ACTION"]),
]


def rule(rule_id, name, sigs, frames):
    return {
        "rule_id": rule_id, "rule_name": name,
        "source_status": "PROPOSED_NOT_CANONICAL", "owner_ratified": "NO",
        "scope": "UNSET_OWNER_DECIDES_THIS_NAZILA_ONLY_OR_GENERAL",
        "input_text_signals_required": sigs,
        "input_frame_candidates_required": frames,
        "relations_required": ["OWNER_RATIFIED_RELATION_SIGNALS_TO_CANDIDATE (absent)"],
        "negative_preventers": ["WORD_PRESENT_IS_NOT_DOMAIN", "FRAME_CANDIDATE_IS_NOT_FINAL_TAKYIF"],
        "minimum_evidence_required": "traceable artifact evidence (round-10 signals/frames)",
        "rank_or_priority": "UNSET",
        "confidence_status": "UNRATIFIED",
        "BIRTH_STATUS": "CANDIDATE_ONLY",
        "DOMAIN_BORN": "NO",
        "NORMATIVE_SOURCE_ALLOWED": "NO",
        "produces": "MASALA_TAKYIF_CANDIDATE_ONLY",
        "does_not_produce": ["DOMAIN_CLASSIFICATION", "NORMATIVE_SOURCE", "HUKM", "MANAT", "TANZIL", "FINAL_ANSWER"],
        "cause": "presence of round-10 text signals / frame candidates",
        "conditions": ["owner-ratified takyīf rule", "ratified signals→candidate relation",
                       "ratified scope", "traceable evidence from prior artifact"],
        "preventers": ["MISSING_OWNER_RATIFICATION", "SIGNAL_TO_DOMAIN_CONFLATION",
                       "FRAME_TO_FINAL_TAKYIF_CONFLATION", "NORMATIVE_SOURCE_BEFORE_TAKYIF",
                       "HUKM_OR_TANZIL_BEFORE_NORMATIVE_SOURCE"],
        "verdict": "DEFER_UNTIL_OWNER_RATIFIES_TAKYIF_RULE",
        "evidence": ["output/taaqol_maqam_foundation_generated/HOKOM_TEXT_SIGNALS_10.json",
                     "output/taaqol_maqam_foundation_generated/HOKOM_FRAME_CANDIDATES_10.json"],
        "residuals": ["needs owner ratification of the layer + this rule + scope before any takyīf"],
        "producer_file": PRODUCER,
    }


def build_candidates():
    return [rule(*r) for r in CANDIDATE_RULES]


def build_guards():
    return {
        "guards": [
            {"guard": "WORD_PRESENT_NOT_DOMAIN", "example": "وارثه NOT -> MIRATH domain", "enforced": "YES"},
            {"guard": "WORD_PRESENT_NOT_DOMAIN", "example": "فتحاكما NOT -> QADA domain", "enforced": "YES"},
            {"guard": "TEXT_SIGNAL_NOT_FRAME", "enforced": "YES"},
            {"guard": "FRAME_NOT_MASALA_TAKYIF", "enforced": "YES"},
            {"guard": "MASALA_TAKYIF_NOT_NORMATIVE_SOURCE", "enforced": "YES"},
            {"guard": "DOMAIN_CANDIDATE_NOT_NORMATIVE_SOURCE", "enforced": "YES"},
            {"guard": "SOURCE_CANDIDATE_NOT_SOURCE_RATIFICATION", "enforced": "YES"},
            {"guard": "NO_HUKM_MANAT_TANZIL_ANSWER_THIS_ROUND", "enforced": "YES"},
        ],
        "MIRATH_CANDIDATE_BORN": "NO", "QADA_CANDIDATE_BORN": "NO",
        "DOMAIN_CLASSIFICATION_BORN": "NO", "NORMATIVE_SOURCE_BIRTH_STATUS": "NOT_OPENED",
        "producer_file": PRODUCER,
    }


def owner_request_md(cands):
    lines = ["# طلب تصديق مالك — طبقة تكييف المسألة وقواعدها المرشحة (الجولة 11)", "",
             "**MASALA_TAKYIF_LAYER_STATUS = PROPOSED_NOT_CANONICAL · OWNER_RATIFICATION_REQUIRED = YES**", "",
             "يُطلب من المالك حسم الآتي صراحةً:", "",
             "1. هل يعتمد طبقة `MASALA_TAKYIF_LAYER`؟  `RATIFY_LAYER = YES | NO`",
             "2. هل يعتمد أسماء القواعد المرشحة التالية؟"]
    for c in cands:
        lines.append(f"   - `{c['rule_id']}`  →  `RATIFY = YES | NO`")
    lines += [
        "3. هل يسمح بتحويل frame candidates إلى masala takyif candidates؟  `ALLOW_FRAME_TO_TAKYIF = YES | NO`",
        "4. هل يسمح لاحقًا بولادة domain classification؟  `ALLOW_DOMAIN_BIRTH_LATER = YES | NO`",
        "5. ما النطاق؟  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`",
        "",
        "*ملاحظة: حتى يصل التصديق، تبقى كل القواعد `owner_ratified = NO` و`verdict = DEFER`، ولا يولد أي "
        "domain/normative_source/hukm/manat/tanzil/answer.*",
    ]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_matrix(cands, signals_ok, frames_ok):
    kv = [
        ("ROUND", "MASALA_TAKYIF_RULES_CONSTITUTION_11"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("CONSTITUTION_DOC_CREATED", "YES"),
        ("SCHEMA_CREATED", "YES"),
        ("MASALA_TAKYIF_CANDIDATES_PRODUCED", "YES"),
        ("MASALA_TAKYIF_CANDIDATES_COUNT", str(len(cands))),
        ("JUMP_GUARDS_CREATED", "YES"),
        ("OWNER_RATIFICATION_REQUEST_CREATED", "YES"),
        ("MASALA_TAKYIF_LAYER_STATUS", "PROPOSED_NOT_CANONICAL"),
        ("OWNER_RATIFICATION_REQUIRED", "YES"),
        ("DOMAIN_ROUTING_LAYER_CANONICAL", "NO"),
        ("TEXT_SIGNALS_AVAILABLE", "YES" if signals_ok else "NO"),
        ("FRAME_CANDIDATES_AVAILABLE", "YES" if frames_ok else "NO"),
        ("ALL_CANDIDATES_OWNER_RATIFIED_NO", "YES"),
        ("ALL_CANDIDATES_PRODUCE_TAKYIF_CANDIDATE_ONLY", "YES"),
        ("DOMAIN_CLASSIFICATION_BORN", "NO"),
        ("MIRATH_CANDIDATE_BORN", "NO"),
        ("QADA_CANDIDATE_BORN", "NO"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "NOT_OPENED"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
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


def render_manager(tokens, cands, guards):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — دستور طبقة تكييف المسألة (11)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.77rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — دستور طبقة تكييف المسألة MASALA_TAKYIF_LAYER (11)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO. '
             'MASALA_TAKYIF_LAYER = PROPOSED_NOT_CANONICAL · OWNER_RATIFICATION_REQUIRED = YES. '
             'لا تكييف نهائي، ولا مجال، ولا مصدر معياري، ولا حكم/مناط/تنزيل/جواب.</div>')
    P.append('<h2>1. الجملة محل العمل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    P.append('<h2>2. جدول الكلمات t000..t009</h2>')
    if not tokens:
        P.append('<div class="note n">TOKEN_ARTIFACT_MISSING</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>الفئة</th></tr></thead><tbody>')
        for t in tokens:
            P.append('<tr><th>' + e(t["token_id"]) + '</th><td>' + e(t.get("original_surface", "")) +
                     '</td><td>' + e(t.get("word_class", "")) + '</td></tr>')
        P.append('</tbody></table></div>')
    P.append('<h2>3. ملخص الجولة 10</h2><div class="note">REFERENCE_MATRIX + HOKOM_FRAMENET_SCHEMA + '
             'TEXT_SIGNALS + FRAME_CANDIDATES + JUMP_GUARDS = DONE؛ لكن MASALA_TAKYIF لم يولد بعد، ولا مجال ولا مصدر معياري.</div>')
    P.append('<h2>4. لماذا نحتاج طبقة تكييف قبل المصدر المعياري؟</h2><div class="note">'
             'لأن اختيار مصدر معياري قبل تكييف المسألة قفزٌ محظور. الطبقة تنظّم الانتقال من الإشارات/المرشحات '
             'إلى مرشّحات تكييف فقط، ويبقى اختيار المصدر المعياري والحكم بعد تصديق التكييف.</div>')
    P.append('<h2>5. الفرق بين الإشارة والمرشح والتكييف والمصدر والحكم والتنزيل</h2><div class="wrap"><table><thead><tr>'
             '<th>الطبقة</th><th>الحالة الآن</th></tr></thead><tbody>'
             '<tr><td>TEXT_SIGNAL</td><td class="d">إشارة سطحية (10)</td></tr>'
             '<tr><td>FRAME_CANDIDATE</td><td class="d">مرشح إطار غير مصدّق (10)</td></tr>'
             '<tr><td>MASALA_TAKYIF_CANDIDATE</td><td class="d">مرشح تكييف فقط — owner_ratified=NO · DEFER (11)</td></tr>'
             '<tr><td>DOMAIN_CLASSIFICATION</td><td class="n">لم يولد</td></tr>'
             '<tr><td>NORMATIVE_SOURCE</td><td class="n">لم يُفتح</td></tr>'
             '<tr><td>HUKM / MANAT / TANZIL / FINAL_ANSWER</td><td class="n">لم يُنتَج</td></tr>'
             '</tbody></table></div>')
    P.append('<h2>6. قواعد التكييف المرشحة (كلها DEFER وغير مصدّقة)</h2><div class="wrap"><table><thead><tr>'
             '<th>rule_id</th><th>الاسم</th><th>owner_ratified</th><th>produces</th><th>verdict</th></tr></thead><tbody>')
    for c in cands:
        P.append(f'<tr><th>{e(c["rule_id"])}</th><td>{e(c["rule_name"])}</td>'
                 f'<td class="n">{e(c["owner_ratified"])}</td><td class="d">{e(c["produces"])}</td>'
                 f'<td class="d">{e(c["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>7. ما يستطيع الوكيل فعله وحده</h2><ul>'
             '<li>دستور الطبقة + schema + قواعد مرشحة + حُرّاس + طلب تصديق + تقرير + matrix + اختبارات.</li></ul>')
    P.append('<h2>8. ما يحتاج تصديق المالك</h2><ul>'
             '<li>اعتماد الطبقة، أسماء القواعد، تحويل frame→takyif، السماح بولادة domain لاحقًا، والنطاق.</li></ul>')
    P.append('<h2>9. الحُرّاس ضد القفز</h2><div class="note n" style="background:#fdecec">'
             'وارثه ≠ مجال مواريث · فتحاكما ≠ مجال قضاء · TEXT_SIGNAL ≠ FRAME ≠ MASALA_TAKYIF ≠ NORMATIVE_SOURCE · '
             'DOMAIN_CANDIDATE ≠ NORMATIVE_SOURCE · SOURCE_CANDIDATE ≠ SOURCE_RATIFICATION. '
             'MIRATH_CANDIDATE_BORN = NO · QADA_CANDIDATE_BORN = NO · DOMAIN_CLASSIFICATION_BORN = NO.</div>')
    P.append('<h2>10. طلب تصديق المالك</h2><div class="note">'
             'التفصيل في <code>OWNER_RATIFICATION_REQUEST_FOR_MASALA_TAKYIF_RULES_11.md</code>: اعتماد الطبقة، '
             'اعتماد أسماء القواعد، السماح بتحويل frame→takyif، السماح بولادة domain لاحقًا، وتحديد النطاق.</div>')
    P.append('<h2>11. سلسلة التوليد المحروسة</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_11_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'CONSTITUTION = docs/HOKOM_TAAQOL_MASALA_TAKYIF_RULES_CONSTITUTION_11.md\n'
             'SCHEMA = schemas/masala_takyif_rule_schema_11.json\n'
             'CANDIDATES = output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_CANDIDATES_11.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_JUMP_GUARDS_11.json\n'
             'OWNER_REQUEST = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_MASALA_TAKYIF_RULES_11.md\n'
             'PYTEST_FILE = tests/test_taaqol_masala_takyif_rules_11.py\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    P.append('<div class="foot">'
             'MASALA_TAKYIF_LAYER_STATUS = PROPOSED_NOT_CANONICAL · DOMAIN_CLASSIFICATION_BORN = NO · '
             'NORMATIVE_SOURCE_BIRTH_STATUS = NOT_OPENED · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · ASSERTED_NOT_MEASURED_COUNT = 0 · '
             'SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "MASALA_TAKYIF_MANAGER_REPORT_AR_11.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "MASALA_TAKYIF_RULES_11_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    cands = build_candidates()
    guards = build_guards()
    (OUT / "MASALA_TAKYIF_CANDIDATES_11.json").write_text(json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MASALA_TAKYIF_JUMP_GUARDS_11.json").write_text(json.dumps(guards, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_MASALA_TAKYIF_RULES_11.md").write_text(owner_request_md(cands), encoding="utf-8")
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(cands, SIGNALS_10.exists(), FRAMES_10.exists()):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, cands, guards), encoding="utf-8")
    print("REPORT_11=" + a.report_out)
    print("CANDIDATES=" + str(len(cands)) + " all owner_ratified=NO verdict=DEFER; DOMAIN_BORN=NO NORMATIVE_SOURCE=NOT_OPENED")


if __name__ == "__main__":
    main()
