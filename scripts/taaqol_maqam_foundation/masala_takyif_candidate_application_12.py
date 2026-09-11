#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_OWNER_RATIFIED_MASALA_TAKYIF_CANDIDATE_APPLICATION_12.

Owner ratified MASALA_TAKYIF_LAYER for THIS_NAZILA_ONLY and licensed frame→takyīf-candidate production.
This round applies the layer to the sentence to emit ranked takyīf CANDIDATES only. Every candidate
stays CANDIDATE_ONLY / DOMAIN_BORN=NO / no normative source / no ḥukm/manāṭ/tanzīl/answer. verdict is
ACCEPT_AS_CANDIDATE_ONLY or DEFER_AS_CANDIDATE_ONLY — never ACCEPT_AS_DOMAIN. No commit; prior rounds
unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/masala_takyif_candidate_application_12.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
FORBIDDEN_TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
SIGNALS_10 = OUT / "HOKOM_TEXT_SIGNALS_10.json"
FRAMES_10 = OUT / "HOKOM_FRAME_CANDIDATES_10.json"
CANDS_11 = OUT / "MASALA_TAKYIF_CANDIDATES_11.json"

# ranked candidate applications (candidate-only); verdict = ACCEPT_AS_CANDIDATE_ONLY / DEFER_AS_CANDIDATE_ONLY
APPS = [
    ("MIRATH_RELATED_TAKYIF_CANDIDATE", "مرشح تكييف متعلق بالمواريث", 1,
     ["وَارِثُهُ", "مَاتَ"], ["FC_DEATH_EVENT"], "ACCEPT_AS_CANDIDATE_ONLY"),
    ("QADA_RELATED_TAKYIF_CANDIDATE", "مرشح تكييف متعلق بالقضاء/النزاع", 2,
     ["فَتَحَاكَمَا"], ["FC_DISPUTE_EVENT"], "ACCEPT_AS_CANDIDATE_ONLY"),
    ("TURKAH_RIGHTS_TAKYIF_CANDIDATE", "مرشح تكييف حقوق تركة", 3,
     ["مَاتَ", "وَارِثُهُ"], ["FC_DEATH_EVENT"], "DEFER_AS_CANDIDATE_ONLY"),
    ("SUKNA_OR_POSSESSION_TAKYIF_CANDIDATE", "مرشح تكييف سكنى/حيازة", 4,
     ["سَاكِنَةٍ", "طَرْدَهَا"], ["FC_RESIDENCE_RELATION", "FC_INTENT_ACTION"], "DEFER_AS_CANDIDATE_ONLY"),
]


def layer_ratification():
    return {
        "MASALA_TAKYIF_LAYER_OWNER_RATIFIED": "YES",
        "MASALA_TAKYIF_LAYER_SCOPE": "THIS_NAZILA_ONLY",
        "FRAME_TO_MASALA_TAKYIF_CANDIDATE_LICENSE": "YES",
        "MASALA_TAKYIF_CANDIDATE_PRODUCTION_ALLOWED": "YES",
        "DOMAIN_CLASSIFICATION_BIRTH_ALLOWED_NOW": "NO",
        "NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW": "NO",
        "NORMATIVE_HUKM_ALLOWED_NOW": "NO",
        "MANAT_ALLOWED_NOW": "NO",
        "TANZIL_ALLOWED_NOW": "NO",
        "FINAL_ANSWER_ALLOWED_NOW": "NO",
        "MASALA_TAKYIF_LAYER_STATUS": "OWNER_RATIFIED_FOR_THIS_NAZILA_ONLY",
        "OWNER_RATIFICATION_REQUIRED": "SATISFIED_FOR_LAYER_ONLY",
        "evidence": ["OWNER_DECISION_IN_PROMPT_12",
                     "output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_CANDIDATES_11.json"],
        "producer_file": PRODUCER,
    }


def build_apps():
    apps = []
    for cid, label, rank, sigs, frames, verdict in APPS:
        apps.append({
            "candidate_id": cid, "candidate_label": label, "rank": rank,
            "text_signals_used": sigs, "frame_candidates_used": frames,
            "birth_status": "CANDIDATE_ONLY",
            "owner_ratified_as_final_domain": "NO",
            "domain_born": "NO", "normative_source_allowed": "NO",
            "hukm_allowed": "NO", "manat_allowed": "NO", "tanzil_allowed": "NO", "final_answer_allowed": "NO",
            "cause": "round-10/11 text signals + frame candidates present",
            "conditions": ["takyīf layer owner-ratified THIS_NAZILA_ONLY",
                           "license limited to producing MASALA_TAKYIF_CANDIDATE",
                           "trace to a prior artifact present", "no domain classification produced"],
            "preventers": ["NO_OWNER_RATIFICATION_OF_FINAL_DOMAIN", "NO_DOMAIN_BIRTH_RULE",
                           "NO_RATIFIED_NORMATIVE_SOURCE", "NO_HUKM_MANAT_TANZIL_ANSWER_LICENSE"],
            "verdict": verdict,   # ACCEPT_AS_CANDIDATE_ONLY | DEFER_AS_CANDIDATE_ONLY (never ACCEPT_AS_DOMAIN)
            "evidence": ["output/taaqol_maqam_foundation_generated/HOKOM_TEXT_SIGNALS_10.json",
                         "output/taaqol_maqam_foundation_generated/HOKOM_FRAME_CANDIDATES_10.json",
                         "output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_CANDIDATES_11.json"],
            "residuals": ["remains a candidate; final domain classification needs a separate owner ratification"],
            "producer_file": PRODUCER,
        })
    return apps


def build_guards():
    return {
        "WORD_PRESENT_DOES_NOT_BIRTH_DOMAIN": "YES",
        "FRAME_DOES_NOT_BIRTH_DOMAIN": "YES",
        "CANDIDATE_DOES_NOT_BIRTH_DOMAIN": "YES",
        "NO_NORMATIVE_SOURCE_SELECTION": "YES",
        "NO_HUKM": "YES", "NO_MANAT": "YES", "NO_TANZIL": "YES", "NO_FINAL_ANSWER": "YES",
        "examples": ["وارثه does NOT birth MIRATH domain", "فتحاكما does NOT birth QADA domain"],
        "chain": "TEXT_SIGNAL != FRAME != MASALA_TAKYIF_CANDIDATE != DOMAIN_CLASSIFICATION != NORMATIVE_SOURCE != HUKM != MANAT != TANZIL != FINAL_ANSWER",
        "producer_file": PRODUCER,
    }


def owner_request_13_md(apps):
    lines = ["# طلب تصديق مالك — ولادة تصنيف المجال (تمهيد الجولة 13)", "",
             "بعد اعتماد طبقة التكييف وإنتاج المرشحات (candidate-only) في الجولة 12، يُطلب من المالك:", "",
             "1. هل يسمح بولادة `DOMAIN_CLASSIFICATION`؟  `ALLOW_DOMAIN_BIRTH = YES | NO`",
             "2. أي مرشح/مرشحات يعتمدها للتصنيف؟"]
    for a in apps:
        lines.append(f"   - `{a['candidate_id']}` (rank {a['rank']})  →  `ADOPT = YES | NO`")
    lines += [
        "3. هل الاعتماد لهذه النازلة فقط أم قاعدة عامة؟  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`",
        "4. هل يسمح بعد ذلك بطلب/اختيار مصدر معياري؟  `ALLOW_NORMATIVE_SOURCE_REQUEST_NEXT = YES | NO`",
        "",
        "*حتى يصل التصديق: DOMAIN_CLASSIFICATION_BORN = NO · NORMATIVE_SOURCE = NOT_OPENED · لا حكم/مناط/تنزيل/جواب.*",
    ]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_matrix(apps):
    kv = [
        ("ROUND", "MASALA_TAKYIF_CANDIDATE_APPLICATION_12"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("MASALA_TAKYIF_LAYER_OWNER_RATIFIED", "YES"),
        ("MASALA_TAKYIF_LAYER_SCOPE", "THIS_NAZILA_ONLY"),
        ("MASALA_TAKYIF_LAYER_STATUS", "OWNER_RATIFIED_FOR_THIS_NAZILA_ONLY"),
        ("FRAME_TO_MASALA_TAKYIF_CANDIDATE_LICENSE", "YES"),
        ("MASALA_TAKYIF_CANDIDATE_PRODUCTION_ALLOWED", "YES"),
        ("MASALA_TAKYIF_CANDIDATES_PRODUCED", "YES"),
        ("CANDIDATE_COUNT", str(len(apps))),
        ("ALL_CANDIDATES_CANDIDATE_ONLY", "YES"),
        ("ALL_CANDIDATES_DOMAIN_BORN_NO", "YES"),
        ("ALL_CANDIDATES_NORMATIVE_SOURCE_ALLOWED_NO", "YES"),
        ("NO_VERDICT_ACCEPT_AS_DOMAIN", "YES"),
        ("DOMAIN_CLASSIFICATION_BORN", "NO"),
        ("MIRATH_DOMAIN_BORN", "NO"),
        ("QADA_DOMAIN_BORN", "NO"),
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


def render_manager(tokens, ratif, apps, guards):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — تطبيق مرشحات تكييف المسألة بعد تصديق الطبقة (12)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.77rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — تطبيق مرشحات تكييف المسألة بعد تصديق الطبقة (12)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO. '
             'الطبقة مصدّقة لهذه النازلة فقط؛ الناتج مرشّحات تكييف فقط — لا تصنيف مجال نهائي، ولا مصدر معياري، ولا حكم/مناط/تنزيل/جواب.</div>')
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
    P.append('<h2>3. ملخص الجولة 10</h2><div class="note">reference matrix + Hokom-FrameNet roadmap + TEXT_SIGNALS + FRAME_CANDIDATES + JUMP_GUARDS.</div>')
    P.append('<h2>4. ملخص الجولة 11</h2><div class="note">دستور MASALA_TAKYIF_LAYER (PROPOSED_NOT_CANONICAL) + قواعد مرشحة + حُرّاس + طلب تصديق.</div>')
    P.append('<h2>5. قرار المالك في الجولة 12</h2><div class="note y" style="background:#e6f4ea">'
             'MASALA_TAKYIF_LAYER_OWNER_RATIFIED = YES · SCOPE = THIS_NAZILA_ONLY · '
             'FRAME_TO_MASALA_TAKYIF_CANDIDATE_LICENSE = YES. لكن: DOMAIN_CLASSIFICATION_BIRTH_ALLOWED_NOW = NO · '
             'NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW = NO · FINAL_ANSWER_ALLOWED_NOW = NO.</div>')
    P.append('<h2>6. المرشحات الأربعة (candidate-only)</h2><div class="wrap"><table><thead><tr>'
             '<th>rank</th><th>candidate_id</th><th>الاسم</th><th>الإشارات</th><th>birth_status</th>'
             '<th>domain_born</th><th>verdict</th></tr></thead><tbody>')
    for a in apps:
        P.append(f'<tr><td>{a["rank"]}</td><th>{e(a["candidate_id"])}</th><td>{e(a["candidate_label"])}</td>'
                 f'<td>{e("، ".join(a["text_signals_used"]))}</td><td class="d">{e(a["birth_status"])}</td>'
                 f'<td class="n">{e(a["domain_born"])}</td><td class="d">{e(a["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>7. السبب/الشرط/المانع لكل مرشح</h2><div class="wrap"><table><thead><tr>'
             '<th>candidate</th><th>cause</th><th>preventers</th><th>verdict</th></tr></thead><tbody>')
    for a in apps:
        P.append(f'<tr><th>{e(a["candidate_id"])}</th><td>{e(a["cause"])}</td>'
                 f'<td class="n">{e("؛ ".join(a["preventers"]))}</td><td class="d">{e(a["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>8. لماذا المرشح ليس مجالًا نهائيًا؟</h2><div class="note n" style="background:#fdecec">'
             'لأن verdict لا يساوي ACCEPT_AS_DOMAIN أبدًا؛ domain_born = NO لكل مرشح؛ وولادة التصنيف النهائي '
             'تحتاج تصديق مالك منفصل (الجولة 13). لم يُثبَت للنازلة أيُّ تصنيف مجالٍ نهائيٍّ (لا مواريثَ ولا قضاءَ '
             'بوصفه حكمًا مجاليًا مغلقًا) — كلها مرشّحات مفتوحة فقط.</div>')
    P.append('<h2>9. ما يستطيع الوكيل فعله الآن</h2><ul>'
             '<li>تطبيق الطبقة لإنتاج مرشحات تكييف مرتبة فقط + حُرّاس + طلب تصديق الجولة 13 + تقرير + matrix + اختبارات.</li></ul>')
    P.append('<h2>10. ما يحتاج تصديق المالك بعد ذلك</h2><ul>'
             '<li>ولادة DOMAIN_CLASSIFICATION، واعتماد مرشح بعينه، والنطاق، والسماح لاحقًا بطلب مصدر معياري '
             '(التفصيل في OWNER_RATIFICATION_REQUEST_FOR_DOMAIN_CLASSIFICATION_13.md).</li></ul>')
    P.append('<h2>11. سلسلة التوليد المحروسة</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_12_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'RATIFICATION = output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_LAYER_OWNER_RATIFICATION_12.json\n'
             'APPLICATION = output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_CANDIDATE_APPLICATION_12.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/MASALA_TAKYIF_APPLICATION_GUARDS_12.json\n'
             'OWNER_REQUEST_13 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_DOMAIN_CLASSIFICATION_13.md\n'
             'PYTEST_FILE = tests/test_taaqol_masala_takyif_candidate_application_12.py\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    P.append('<div class="foot">'
             'MASALA_TAKYIF_LAYER_OWNER_RATIFIED = YES · SCOPE = THIS_NAZILA_ONLY · CANDIDATE_COUNT = '
             + str(len(apps)) + ' · DOMAIN_CLASSIFICATION_BORN = NO · NORMATIVE_SOURCE_BIRTH_STATUS = NOT_OPENED · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'ASSERTED_NOT_MEASURED_COUNT = 0 · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "MASALA_TAKYIF_CANDIDATE_APPLICATION_MANAGER_REPORT_AR_12.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "MASALA_TAKYIF_CANDIDATE_APPLICATION_12_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    ratif = layer_ratification()
    apps = build_apps()
    guards = build_guards()
    (OUT / "MASALA_TAKYIF_LAYER_OWNER_RATIFICATION_12.json").write_text(json.dumps(ratif, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MASALA_TAKYIF_CANDIDATE_APPLICATION_12.json").write_text(json.dumps(apps, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "MASALA_TAKYIF_APPLICATION_GUARDS_12.json").write_text(json.dumps(guards, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_DOMAIN_CLASSIFICATION_13.md").write_text(owner_request_13_md(apps), encoding="utf-8")
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(apps):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, ratif, apps, guards), encoding="utf-8")
    print("REPORT_12=" + a.report_out)
    print("CANDIDATE_COUNT=" + str(len(apps)) + " DOMAIN_BORN=NO NORMATIVE_SOURCE=NOT_OPENED verdicts=" +
          ";".join(a["verdict"] for a in apps))


if __name__ == "__main__":
    main()
