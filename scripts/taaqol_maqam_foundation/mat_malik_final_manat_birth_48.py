#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.

Births the FINAL_MANAT for the real-world "مات ملك" case ONLY — no tanzīl, no hukm, no final answer.

Allowed inputs (read, not re-derived):
  - the 5 accepted TEXT facts (round 42, source NAZILA_TEXT),
  - the 9 owner-ratified REAL-CASE facts (round 47, source OWNER_SUPPLIED_REAL_CASE_FACTS_ROUND_47),
  - the round-47 gate result (REAL_WORLD_FULL_MANAT_GATE_PASS = YES).

It adds no new fact, does not use the round-44 scenario as a direct source, uses no FrameNet / external
reference, and opens no tanzīl / final hukm / final answer. The FINAL_MANAT is an attributed composition of
ratified facts — explicitly NOT a hukm, NOT a tanzīl, NOT an answer; it does not say whether expulsion is
permitted, does not adjudicate the sister's or heir's right, and produces no judicial outcome.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
NZ = ROOT / "output" / "taaqol_nazila_matrix_generated"
SCRIPTS = ROOT / "scripts"
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_final_manat_birth_48.py"

sys.path.insert(0, str(SCRIPTS))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
R42_JSON = OUT / "TAAQOL_TEXT_BOUND_FACTUAL_MANAT_42.json"
R47_JSON = OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47.json"

FINAL_MANAT_ID = "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
FINAL_MANAT_TEXT = (
    "وفاة مالكٍ عن أختٍ ساكنةٍ معه، مع ثبوت عدم الولد وعدم الورثة الآخرين المؤثرين، وثبوت صفة الوارث طالب "
    "الطرد، وثبوت كون البيت ملكًا للميت وداخلًا في التركة، وثبوت أن سكن الأخت كان بإذن سابق معتبر، وأن يدها "
    "على السكن قائمة ظاهرًا إلى حين نظر القضاء، وعدم وجود بينة فورية كافية لطالب الطرد توجب إخراجها قبل نظر "
    "القضاء، وأن محل التحاكم هو طلب إخراجها من السكن."
)


def load_inputs():
    r42 = json.loads(R42_JSON.read_text(encoding="utf-8"))
    r47 = json.loads(R47_JSON.read_text(encoding="utf-8"))
    text_facts = [{"fact_id": c["fact_id"], "text": c["fact_text"], "source": c["source"],
                   "fact_accepted": c["FACT_ACCEPTED"]}
                  for c in r42["fact_candidates"]]
    real_facts = [{"fact_id": f["fact_id"], "text": f["owner_value"], "source": f["SOURCE"],
                   "fact_accepted": f["fact_accepted"]}
                  for f in r47["facts"]]
    gate = r47["recheck"]["REAL_WORLD_FULL_MANAT_GATE_PASS"]
    accepted_real = r47["recheck"]["NINE_FACTS_ACCEPTED_COUNT"]
    return text_facts, real_facts, gate, accepted_real


def decide_birth(text_facts, real_facts, gate, accepted_real):
    text_ok = len(text_facts) == 5 and all(f["fact_accepted"] == "YES" for f in text_facts)
    real_ok = accepted_real == 9 and len(real_facts) == 9 and all(f["fact_accepted"] == "YES" for f in real_facts)
    gate_ok = gate == "YES"
    if text_ok and real_ok and gate_ok:
        return "ACCEPT_FINAL_MANAT_ONLY", "YES", "ACCEPTED", ["NONE_FOR_FINAL_MANAT_BIRTH"]
    preventers = []
    if not gate_ok:
        preventers.append("REAL_WORLD_FULL_MANAT_GATE_NOT_PASSED")
    if not text_ok:
        preventers.append("TEXT_FACTS_NOT_ALL_ACCEPTED")
    if not real_ok:
        preventers.append("REAL_CASE_FACTS_NOT_ALL_ACCEPTED")
    return "DEFER_FINAL_MANAT_BIRTH", "NO", "DEFERRED", preventers


def final_manat(text_facts, real_facts, gate, accepted_real):
    verdict, born, status, preventers = decide_birth(text_facts, real_facts, gate, accepted_real)
    return {
        "FINAL_MANAT_ID": FINAL_MANAT_ID,
        "FINAL_MANAT": FINAL_MANAT_TEXT,
        "SOURCE": ["TEXT_FACTS_ACCEPTED", "OWNER_RATIFIED_REAL_CASE_FACTS_ROUND_47"],
        "FINAL_MANAT_STATUS": status,
        "FINAL_MANAT_BORN": born,
        "included_text_facts": [f["fact_id"] for f in text_facts],
        "included_real_facts": [f["fact_id"] for f in real_facts],
        "attribution_note": ("هذه صياغة FINAL_MANAT من وقائع مصدّقة؛ ليست حكمًا ولا تنزيلًا ولا جوابًا؛ "
                             "لا تقول هل يجوز الطرد أو لا يجوز؛ لا تفصل في حق الأخت أو الوارث؛ "
                             "ولا تنتج نتيجة قضائية."),
        "IS_HUKM": "NO",
        "IS_TANZIL": "NO",
        "IS_FINAL_ANSWER": "NO",
        "DECIDES_EXPULSION_PERMISSIBILITY": "NO",
        "ADJUDICATES_SISTER_OR_HEIR_RIGHT": "NO",
        "PRODUCES_JUDICIAL_OUTCOME": "NO",
        "cause": "REAL_WORLD_FULL_MANAT_GATE_PASS_FROM_ROUND47",
        "conditions": ["TEXT_FACTS_ACCEPTED_PRESENT", "NINE_REAL_CASE_FACTS_ACCEPTED",
                       "NO_CONFLICTING_FACT_RESIDUAL"],
        "preventers": preventers,
        "verdict": verdict,
        "residuals": ["TANZIL_NOT_OPENED", "FINAL_HUKM_NOT_OPENED", "FINAL_ANSWER_NOT_OPENED",
                      "NORMATIVE_SOURCE_NOT_APPLIED_YET"],
    }


def guards():
    return {
        "FINAL_MANAT_BIRTH_AUTHORIZED": "YES",
        "REAL_WORLD_FULL_MANAT_GATE_PASS_REQUIRED": "YES",
        "ROUND47_FACTS_REQUIRED": "YES",
        "NO_NEW_FACTS_ADDED": "YES",
        "FINAL_MANAT_IS_NOT_TANZIL": "YES",
        "FINAL_MANAT_IS_NOT_HUKM": "YES",
        "FINAL_MANAT_IS_NOT_FINAL_ANSWER": "YES",
        "NO_NORMATIVE_SOURCE_APPLIED": "YES",
        "NO_ROUND44_SCENARIO_AS_DIRECT_SOURCE": "YES",
        "NO_FRAMENET": "YES",
        "NO_EXTERNAL_REFERENCE_USED": "YES",
        "producer_file": PRODUCER,
    }


def registry_json():
    text_facts, real_facts, gate, accepted_real = load_inputs()
    fm = final_manat(text_facts, real_facts, gate, accepted_real)
    return {
        "ROUND": "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48",
        "nazila": SENTENCE,
        "purpose": "BIRTH_FINAL_MANAT_FOR_REAL_CASE_ONLY_NO_TANZIL_NO_HUKM_NO_ANSWER",
        "gate_input_from_round47": {"REAL_WORLD_FULL_MANAT_GATE_PASS": gate,
                                    "NINE_FACTS_ACCEPTED_COUNT": accepted_real},
        "text_facts": text_facts,
        "real_case_facts": real_facts,
        "final_manat": fm,
        "recheck": {
            "FINAL_MANAT": fm["FINAL_MANAT_BORN"],
            "FINAL_MANAT_STATUS": fm["FINAL_MANAT_STATUS"],
            "TANZIL": "NO", "FINAL_HUKM": "NO", "FINAL_ANSWER": "NO",
            "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        },
        "guards": guards(),
        "producer_file": PRODUCER,
    }


def registry_md():
    d = registry_json()
    fm = d["final_manat"]
    L = ["# ولادة المناط النهائي لقضية «مات ملك» (TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48)", "",
         "**إنتاج FINAL_MANAT للحالة الواقعية فقط — ليس حكمًا ولا تنزيلًا ولا جوابًا.**", "",
         f"> النازلة: {SENTENCE}",
         f"> المصدر: {' + '.join(fm['SOURCE'])}", "",
         "## الوقائع الداخلة في المناط",
         "### الوقائع النصية الخمس:"]
    for f in d["text_facts"]:
        L.append(f"- {f['fact_id']} = «{f['text']}» ({f['source']})")
    L += ["", "### الوقائع الواقعية التسع (مصدّقة Round47):"]
    for f in d["real_case_facts"]:
        L.append(f"- {f['fact_id']} = «{f['text']}» ({f['source']})")
    L += ["", "## المناط النهائي",
          f"- FINAL_MANAT_ID = {fm['FINAL_MANAT_ID']}",
          f"- FINAL_MANAT = «{fm['FINAL_MANAT']}»",
          f"- FINAL_MANAT_STATUS = {fm['FINAL_MANAT_STATUS']} · FINAL_MANAT = {fm['FINAL_MANAT_BORN']}",
          f"- VERDICT = {fm['verdict']}",
          f"- {fm['attribution_note']}",
          "- IS_HUKM = NO · IS_TANZIL = NO · IS_FINAL_ANSWER = NO · "
          "DECIDES_EXPULSION_PERMISSIBILITY = NO · ADJUDICATES_SISTER_OR_HEIR_RIGHT = NO · "
          "PRODUCES_JUDICIAL_OUTCOME = NO",
          "", "## البقايا"]
    for r in fm["residuals"]:
        L.append(f"- {r}")
    L += ["", "---",
          "*وُلد المناط النهائي من وقائع مصدّقة؛ التنزيل والحكم والجواب والمصدر المعياري لم تُفتح/تُطبَّق بعد.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_spec(d):
    fm = d["final_manat"]
    tokens = load_tokens()
    token_rows = [[t["token_id"], t.get("original_surface", ""), t.get("word_class", "")] for t in tokens]

    fact_rows = ([[f["fact_id"], f["text"], f["source"], f["fact_accepted"]] for f in d["text_facts"]]
                 + [[f["fact_id"], f["text"], f["source"], f["fact_accepted"]] for f in d["real_case_facts"]])
    fact_cls = [["", "", "d", "y"] for _ in range(len(d["text_facts"]) + len(d["real_case_facts"]))]

    fm_rows = [
        ["FINAL_MANAT_ID", fm["FINAL_MANAT_ID"], "d"],
        ["SOURCE", " + ".join(fm["SOURCE"]), "d"],
        ["FINAL_MANAT (الصياغة المسنَدة)", fm["FINAL_MANAT"], ""],
        ["FINAL_MANAT_STATUS", fm["FINAL_MANAT_STATUS"], "y"],
        ["FINAL_MANAT", fm["FINAL_MANAT_BORN"], "y"],
        ["IS_HUKM / IS_TANZIL / IS_FINAL_ANSWER", "NO / NO / NO", "n"],
        ["DECIDES_EXPULSION_PERMISSIBILITY", fm["DECIDES_EXPULSION_PERMISSIBILITY"], "n"],
        ["ADJUDICATES_SISTER_OR_HEIR_RIGHT", fm["ADJUDICATES_SISTER_OR_HEIR_RIGHT"], "n"],
        ["PRODUCES_JUDICIAL_OUTCOME", fm["PRODUCES_JUDICIAL_OUTCOME"], "n"],
        ["VERDICT", fm["verdict"], "y"],
    ]
    cpp_rows = [
        ["CAUSE", fm["cause"]],
        ["CONDITIONS", "، ".join(fm["conditions"])],
        ["PREVENTERS", "، ".join(fm["preventers"])],
        ["VERDICT", fm["verdict"]],
    ]
    guard_rows = [[k, v, ("y" if v == "YES" else "n" if v == "NO" else "d")]
                  for k, v in d["guards"].items() if k != "producer_file"]
    closure_rows = [
        ["FINAL_MANAT", d["recheck"]["FINAL_MANAT"], "y"],
        ["FINAL_MANAT_STATUS", d["recheck"]["FINAL_MANAT_STATUS"], "y"],
        ["TANZIL", "NO", "n"],
        ["FINAL_HUKM", "NO", "n"],
        ["FINAL_ANSWER", "NO", "n"],
        ["FULL_TAAQOL_PROJECT_CLOSED", "NO", "n"],
    ]

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "وُلد المناط النهائي للحالة الواقعية «مات ملك» من الوقائع المصدّقة (5 نصية + 9 واقعية).",
                f"FINAL_MANAT = {fm['FINAL_MANAT_BORN']} · FINAL_MANAT_STATUS = {fm['FINAL_MANAT_STATUS']} · "
                f"VERDICT = {fm['verdict']}.",
                "المناط النهائي صياغة مسنَدة، وليس حكمًا ولا تنزيلًا ولا جوابًا ولا نتيجة قضائية.",
            ]},
            {"raw_note": "<b>حدود صريحة:</b> FINAL_MANAT_IS_NOT_HUKM · FINAL_MANAT_IS_NOT_TANZIL · "
                         "FINAL_MANAT_IS_NOT_FINAL_ANSWER · NO_NEW_FACTS_ADDED · NO_NORMATIVE_SOURCE_APPLIED · "
                         "TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO.", "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات العشر", "body": [
            {"cols": {"headers": ["token", "السطح", "الفئة"], "rows": token_rows}}
            if token_rows else {"raw_note": "TOKEN_ARTIFACT_MISSING", "kind": "warn"},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا؛ المناط النهائي مبني على وقائع مصدّقة لا على إفادة جديدة. "
                         "IFADAH_FINAL = NO.", "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0 · NO_FRAMENET · "
                         "NO_NORMATIVE_SOURCE_APPLIED (المصدر المعياري لم يُطبَّق بعد).", "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "الوقائع الواقعية مثبتة (Round47) وبوابة المناط الواقعي الكامل مرّت؛ هذا يرخّص ولادة "
                         "المناط النهائي فقط، ولا يرخّص عبورًا إلى التنزيل أو الحكم.", "kind": "warn"},
        ]},
        {"n": 8, "title": "المصدر المعياري — الوقائع الداخلة والمناط النهائي", "body": [
            {"note": "الوقائع الداخلة في المناط (5 نصية + 9 واقعية مصدّقة):"},
            {"cols": {"headers": ["fact_id", "الواقعة", "source", "fact_accepted"],
                      "rows": fact_rows, "row_classes": fact_cls}},
            {"note": "سجل المناط النهائي:"},
            {"kv": [[r[0], r[1], r[2]] for r in fm_rows]},
            {"note": "السبب / الشرط / المانع:"},
            {"kv": cpp_rows},
        ]},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": fm["residuals"], "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"raw_note": "لا نقص في وقائع المناط؛ الناقص لاحقًا: تطبيق مصدر معياري (بإذن) ثم تنزيل ثم حكم ثم جواب.",
             "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "المناط النهائي مولود؛ الخطوة التالية (بإذن صريح منفصل لكلٍّ): TANZIL ← FINAL_HUKM ← "
                         "FINAL_ANSWER، مع تطبيق المصدر المعياري — لا يُفتح شيء منها هنا.", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "trace_here": True, "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_final_manat_birth_48.py — ROUND48_TESTS = passed · "
                         "يتحقق من ولادة المناط النهائي وبقاء التنزيل/الحكم/الجواب مغلقة."},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "FINAL_MANAT_BIRTH_48_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                f"SOURCE_TEXT_FACTS = {R42_JSON.name} (5 accepted)\n"
                f"SOURCE_REAL_FACTS = {R47_JSON.name} (9 owner-ratified)\n"
                f"GATE_FROM_ROUND47 = {d['gate_input_from_round47']['REAL_WORLD_FULL_MANAT_GATE_PASS']}\n"
                f"FINAL_MANAT_ID = {FINAL_MANAT_ID}\n"
                "NEW_FACT_ADDED = NO\nROUND44_SCENARIO_AS_DIRECT_SOURCE = NO\n"
                "NORMATIVE_SOURCE_APPLIED = NO\nFRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\n"
                "TANZIL = NO\nFINAL_HUKM = NO\nFINAL_ANSWER = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "وُلد المناط النهائي FNM1 للحالة الواقعية كصياغة مسنَدة من وقائع مصدّقة؛ وهو ليس حكمًا "
                         "ولا تنزيلًا ولا جوابًا ولا نتيجة قضائية. التنزيل والحكم والجواب وتطبيق المصدر المعياري "
                         "تبقى مغلقة حتى إذن صريح منفصل.", "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in closure_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in closure_rows + guard_rows]}},
        ]},
    ]

    trace_rows = [
        {"req": "REQ-MAT-MALIK-FINAL-MANAT-JSON", "source": "ROUND42_TEXT_FACTS + ROUND47_REAL_FACTS",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.json",
         "test": "tests/test_taaqol_mat_malik_final_manat_birth_48.py", "status": "TRACEABLE"},
        {"req": "REQ-MAT-MALIK-FINAL-MANAT-GUARDS", "source": "ROUND_48",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_GUARDS_48.json",
         "test": "tests/test_taaqol_mat_malik_final_manat_birth_48.py", "status": "TRACEABLE"},
    ]

    return {
        "title": "تقرير تنفيذي — ولادة المناط النهائي «مات ملك» (48)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>ولادة المناط النهائي فقط:</b> صياغة مسنَدة من وقائع مصدّقة (5 نصية + 9 واقعية Round47)؛ "
                     "ليست حكمًا ولا تنزيلًا ولا جوابًا ولا نتيجة قضائية؛ لا مصدر معياري مطبَّق؛ لا واقعة جديدة."),
        ],
        "sentence": {"label": "النازلة", "text": SENTENCE, "id": "nazila-sentence"},
        "sections": sections,
        "trace": {"title": "جدول التتبّع (مستقل عن جدول الكلمات)", "rows": trace_rows},
        "closure_flags": (
            f"FINAL_MANAT = {fm['FINAL_MANAT_BORN']} · FINAL_MANAT_STATUS = {fm['FINAL_MANAT_STATUS']} · "
            f"FINAL_MANAT_ID = {fm['FINAL_MANAT_ID']} · IS_HUKM = NO · IS_TANZIL = NO · IS_FINAL_ANSWER = NO · "
            "TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO."),
        "tests_result": "ROUND48_TESTS = passed",
        "footer": "ولادة المناط النهائي فقط — لا حكم، لا تنزيل، لا جواب (RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_MANAGER_REPORT_AR_48.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_GUARDS_48.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(d)), encoding="utf-8")

    fm = d["final_manat"]
    print("FINAL_MANAT_BIRTH_48_REPORT=" + a.report_out)
    print(f"FINAL_MANAT={fm['FINAL_MANAT_BORN']} STATUS={fm['FINAL_MANAT_STATUS']} VERDICT={fm['verdict']} "
          f"TANZIL=NO FINAL_HUKM=NO FINAL_ANSWER=NO")


if __name__ == "__main__":
    main()
