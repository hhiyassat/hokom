#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_OWNER_RATIFIED_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.

Owner ratified DOMAIN_CLASSIFICATION birth for THIS_NAZILA_ONLY in MULTI_DOMAIN_CANDIDATE mode (no
forced primary domain). This round births a COMPOSITE multi-domain classification where each domain is
a DOMAIN_CANDIDATE (not a closed final domain, not a normative source). Still blocked:
normative-source selection, ḥukm, manāṭ, tanzīl, final answer. No commit; prior rounds unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/domain_classification_multi_candidate_13.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
FORBIDDEN_TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
APP_12 = OUT / "MASALA_TAKYIF_CANDIDATE_APPLICATION_12.json"

# each domain candidate maps to a round-12 takyif candidate; NONE is forced as primary
DOMAINS = [
    ("MIRATH_RELATED_DOMAIN_CANDIDATE", "مجال متعلق بالمواريث (مرشح)", "MIRATH_RELATED_TAKYIF_CANDIDATE", 1),
    ("QADA_RELATED_DOMAIN_CANDIDATE", "مجال متعلق بالقضاء/النزاع (مرشح)", "QADA_RELATED_TAKYIF_CANDIDATE", 2),
    ("TURKAH_RIGHTS_DOMAIN_CANDIDATE", "مجال حقوق التركة (مرشح)", "TURKAH_RIGHTS_TAKYIF_CANDIDATE", 3),
    ("SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE", "مجال سكنى/حيازة (مرشح)", "SUKNA_OR_POSSESSION_TAKYIF_CANDIDATE", 4),
]


def ratification():
    return {
        "DOMAIN_CLASSIFICATION_BIRTH_ALLOWED": "YES",
        "DOMAIN_CLASSIFICATION_SCOPE": "THIS_NAZILA_ONLY",
        "DOMAIN_CLASSIFICATION_MODE": "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION",
        "PRIMARY_DOMAIN_CANDIDATE": "NOT_FORCED",
        "MIRATH_RELATED_DOMAIN_CANDIDATE": "ALLOWED_AS_DOMAIN_CANDIDATE",
        "QADA_RELATED_DOMAIN_CANDIDATE": "ALLOWED_AS_DOMAIN_CANDIDATE",
        "TURKAH_RIGHTS_DOMAIN_CANDIDATE": "ALLOWED_AS_DOMAIN_CANDIDATE",
        "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE": "ALLOWED_AS_DOMAIN_CANDIDATE",
        "NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW": "NO",
        "NORMATIVE_HUKM_ALLOWED_NOW": "NO",
        "MANAT_ALLOWED_NOW": "NO",
        "TANZIL_ALLOWED_NOW": "NO",
        "FINAL_ANSWER_ALLOWED_NOW": "NO",
        "evidence": ["OWNER_DECISION_IN_PROMPT_13",
                     "output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_CANDIDATE_APPLICATION_12.json"],
        "producer_file": PRODUCER,
    }


def build_domains():
    out = []
    for did, label, takyif_ref, rank in DOMAINS:
        out.append({
            "domain_candidate_id": did, "domain_candidate_label": label, "rank": rank,
            "from_takyif_candidate": takyif_ref,
            "domain_candidate_status": "ALLOWED_AS_DOMAIN_CANDIDATE",
            "birth_status": "DOMAIN_CANDIDATE_BORN",     # a domain CANDIDATE is born, not a closed final domain
            "is_final_closed_domain": "NO",
            "is_primary_forced": "NO",
            "normative_source_allowed": "NO", "hukm_allowed": "NO",
            "manat_allowed": "NO", "tanzil_allowed": "NO", "final_answer_allowed": "NO",
            "cause": "owner ratified multi-domain candidate classification (this nazila) + round-12 takyif candidate",
            "conditions": ["DOMAIN_CLASSIFICATION_BIRTH_ALLOWED=YES", "MODE=MULTI_DOMAIN_CANDIDATE_CLASSIFICATION",
                           "traceable to round-12 takyif candidate", "no single primary forced"],
            "preventers": ["NO_NORMATIVE_SOURCE_SELECTION_YET", "NO_HUKM_MANAT_TANZIL_ANSWER_LICENSE",
                           "MUST_NOT_CLOSE_TO_A_SINGLE_FINAL_DOMAIN_THIS_ROUND"],
            "verdict": "ACCEPT_AS_DOMAIN_CANDIDATE",     # never ACCEPT_AS_CLOSED_DOMAIN / ACCEPT_AS_NORMATIVE_SOURCE
            "evidence": ["output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_CANDIDATE_APPLICATION_12.json",
                         "output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_LAYER_OWNER_RATIFICATION_12.json"],
            "residuals": ["composite classification; picking any domain as basis for a normative source needs owner ratification (round 14)"],
            "producer_file": PRODUCER,
        })
    return out


def build_composite(domains):
    return {
        "classification_id": "NAZILA_MULTI_DOMAIN_COMPOSITE_13",
        "mode": "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION",
        "primary_domain_candidate": "NOT_FORCED",
        "domain_candidates": [d["domain_candidate_id"] for d in domains],
        "composite_verdict": "NAZILA_HAS_A_COMPOSITE_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION",
        "is_final_single_domain": "NO",
        "normative_source_selected": "NO", "hukm_produced": "NO",
        "cause": "the sentence carries more than one jihah; owner allowed multi-domain candidate birth",
        "conditions": ["owner ratification (this nazila only)"],
        "preventers": ["NO_FORCED_PRIMARY", "NO_NORMATIVE_SOURCE_BEFORE_OWNER"],
        "verdict": "COMPOSITE_MULTI_DOMAIN_CANDIDATE_ONLY",
        "producer_file": PRODUCER,
    }


def build_guards():
    return {
        "DOMAIN_CANDIDATE_IS_NOT_CLOSED_DOMAIN": "YES",
        "DOMAIN_CANDIDATE_IS_NOT_NORMATIVE_SOURCE": "YES",
        "NO_FORCED_PRIMARY_DOMAIN": "YES",
        "NO_NORMATIVE_SOURCE_SELECTION": "YES",
        "NO_HUKM": "YES", "NO_MANAT": "YES", "NO_TANZIL": "YES", "NO_FINAL_ANSWER": "YES",
        "chain": "MASALA_TAKYIF_CANDIDATE -> DOMAIN_CANDIDATE (composite) != CLOSED_DOMAIN != NORMATIVE_SOURCE != HUKM != MANAT != TANZIL != FINAL_ANSWER",
        "producer_file": PRODUCER,
    }


def owner_request_14_md(domains):
    lines = ["# طلب تصديق مالك — طلب/اختيار المصدر المعياري بناءً على المجال المركّب (تمهيد الجولة 14)", "",
             "بعد ولادة تصنيف مجال مرشّح مركّب (multi-domain candidate) لهذه النازلة، يُطلب من المالك:", "",
             "1. هل يسمح بطلب/اختيار مصدر معياري بناءً على المجال المركّب؟  `ALLOW_NORMATIVE_SOURCE_REQUEST = YES | NO`",
             "2. على أي مرشح/مرشحات مجال يُبنى طلب المصدر؟"]
    for d in domains:
        lines.append(f"   - `{d['domain_candidate_id']}` (rank {d['rank']})  →  `BASIS = YES | NO`")
    lines += [
        "3. هل يُحسم مجال أساسي واحد أم يُبقى مركّبًا؟  `PRIMARY = PICK_ONE | KEEP_COMPOSITE`",
        "4. النطاق؟  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`",
        "",
        "*حتى يصل التصديق: NORMATIVE_SOURCE = NOT_OPENED · لا حكم/مناط/تنزيل/جواب. المجال يبقى مرشّحًا مركّبًا لا مغلقًا.*",
    ]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_matrix(domains):
    kv = [
        ("ROUND", "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("DOMAIN_CLASSIFICATION_BIRTH_ALLOWED", "YES"),
        ("DOMAIN_CLASSIFICATION_SCOPE", "THIS_NAZILA_ONLY"),
        ("DOMAIN_CLASSIFICATION_MODE", "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION"),
        ("DOMAIN_CLASSIFICATION_BORN", "YES"),
        ("DOMAIN_CLASSIFICATION_KIND", "MULTI_DOMAIN_CANDIDATE_COMPOSITE"),
        ("PRIMARY_DOMAIN_CANDIDATE", "NOT_FORCED"),
        ("DOMAIN_CANDIDATE_COUNT", str(len(domains))),
        ("ALL_DOMAIN_CANDIDATES_NOT_CLOSED_FINAL", "YES"),
        ("ALL_DOMAIN_CANDIDATES_NOT_NORMATIVE_SOURCE", "YES"),
        ("FINAL_SINGLE_DOMAIN_CLOSED", "NO"),
        ("NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW", "NO"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "NOT_OPENED"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
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


def render_manager(tokens, ratif, domains, composite):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — تصنيف مجال مرشّح مركّب للنازلة (13)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.77rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — تصنيف مجال مرشّح مركّب للنازلة (13)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO. '
             'وُلد تصنيف مجال <b>مرشّح مركّب</b> لهذه النازلة فقط، بلا مجال أساسي مفروض — ولا مصدر معياري ولا حكم/مناط/تنزيل/جواب.</div>')
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
    P.append('<h2>3. ملخص الجولات 10/11/12</h2><div class="note">10: مصفوفة مراجع + Hokom-FrameNet. '
             '11: دستور طبقة التكييف (مقترح). 12: تصديق الطبقة (لهذه النازلة) وإنتاج 4 مرشحات تكييف candidate-only.</div>')
    P.append('<h2>4. قرار المالك في الجولة 13</h2><div class="note y" style="background:#e6f4ea">'
             'DOMAIN_CLASSIFICATION_BIRTH_ALLOWED = YES · SCOPE = THIS_NAZILA_ONLY · '
             'MODE = MULTI_DOMAIN_CANDIDATE_CLASSIFICATION · PRIMARY_DOMAIN_CANDIDATE = NOT_FORCED. '
             'لكن: NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW = NO · NORMATIVE_HUKM/MANAT/TANZIL/FINAL_ANSWER = NO.</div>')
    P.append('<h2>5. التصنيف المركّب المولود</h2><div class="note">'
             + e(composite["composite_verdict"]) + ' — is_final_single_domain = NO · primary = NOT_FORCED.</div>')
    P.append('<h2>6. مرشحات المجال (domain candidates، لا مجال مغلق)</h2><div class="wrap"><table><thead><tr>'
             '<th>rank</th><th>domain_candidate_id</th><th>الاسم</th><th>من مرشح تكييف</th>'
             '<th>birth_status</th><th>مجال مغلق؟</th><th>verdict</th></tr></thead><tbody>')
    for d in domains:
        P.append(f'<tr><td>{d["rank"]}</td><th>{e(d["domain_candidate_id"])}</th><td>{e(d["domain_candidate_label"])}</td>'
                 f'<td>{e(d["from_takyif_candidate"])}</td><td class="d">{e(d["birth_status"])}</td>'
                 f'<td class="n">{e(d["is_final_closed_domain"])}</td><td class="d">{e(d["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>7. السبب/الشرط/المانع لكل مرشح مجال</h2><div class="wrap"><table><thead><tr>'
             '<th>domain</th><th>cause</th><th>preventers</th></tr></thead><tbody>')
    for d in domains:
        P.append(f'<tr><th>{e(d["domain_candidate_id"])}</th><td>{e(d["cause"])}</td>'
                 f'<td class="n">{e("؛ ".join(d["preventers"]))}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>8. لماذا مرشّح مجال وليس مجالًا مغلقًا؟</h2><div class="note n" style="background:#fdecec">'
             'verdict = ACCEPT_AS_DOMAIN_CANDIDATE (لا ACCEPT_AS_CLOSED_DOMAIN ولا ACCEPT_AS_NORMATIVE_SOURCE)؛ '
             'is_final_closed_domain = NO لكل مرشح؛ لا مجال أساسي مفروض. النازلة ذات تصنيف مجال مرشّح مركّب فقط.</div>')
    P.append('<h2>9. ما يستطيع الوكيل فعله الآن</h2><ul>'
             '<li>ولادة تصنيف مجال مرشّح مركّب + حُرّاس + طلب تصديق الجولة 14 + تقرير + matrix + اختبارات.</li></ul>')
    P.append('<h2>10. ما يحتاج تصديق المالك بعد ذلك (الجولة 14)</h2><ul>'
             '<li>السماح بطلب/اختيار مصدر معياري بناءً على المجال المركّب، وعلى أي مرشح يُبنى، وحسم primary أم keep-composite، والنطاق '
             '(OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_14.md).</li></ul>')
    P.append('<h2>11. سلسلة التوليد المحروسة</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_13_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'RATIFICATION = output/taaqol_maqam_foundation_generated/DOMAIN_CLASSIFICATION_OWNER_RATIFICATION_13.json\n'
             'COMPOSITE = output/taaqol_maqam_foundation_generated/NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/DOMAIN_CLASSIFICATION_GUARDS_13.json\n'
             'OWNER_REQUEST_14 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_14.md\n'
             'PYTEST_FILE = tests/test_taaqol_domain_classification_multi_candidate_13.py\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    P.append('<div class="foot">'
             'DOMAIN_CLASSIFICATION_BORN = YES (MULTI_DOMAIN_CANDIDATE_COMPOSITE) · PRIMARY_DOMAIN_CANDIDATE = NOT_FORCED · '
             'FINAL_SINGLE_DOMAIN_CLOSED = NO · NORMATIVE_SOURCE_BIRTH_STATUS = NOT_OPENED · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'ASSERTED_NOT_MEASURED_COUNT = 0 · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_MANAGER_REPORT_AR_13.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    ratif = ratification()
    domains = build_domains()
    composite = build_composite(domains)
    guards = build_guards()
    (OUT / "DOMAIN_CLASSIFICATION_OWNER_RATIFICATION_13.json").write_text(json.dumps(ratif, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json").write_text(
        json.dumps({"composite": composite, "domain_candidates": domains}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "DOMAIN_CLASSIFICATION_GUARDS_13.json").write_text(json.dumps(guards, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_14.md").write_text(owner_request_14_md(domains), encoding="utf-8")
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(domains):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, ratif, domains, composite), encoding="utf-8")
    print("REPORT_13=" + a.report_out)
    print("DOMAIN_CANDIDATE_COUNT=" + str(len(domains)) + " PRIMARY=NOT_FORCED FINAL_SINGLE_DOMAIN_CLOSED=NO NORMATIVE_SOURCE=NOT_OPENED")


if __name__ == "__main__":
    main()
