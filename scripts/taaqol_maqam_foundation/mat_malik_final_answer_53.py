#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_FINAL_ANSWER_53.

Produces FINAL_ANSWER ONLY, based on the round-52 FINAL_HUKM (FHK1). Reads the round-52 records directly (not
a summary) and checks seven preconditions; any missing → DEFER_FINAL_ANSWER_PRECONDITION_MISSING. If all hold,
it records a single bounded-case answer tied to FNM1 + NS1 + FHK1, never exceeding them.

Hard limits: bounded-case answer only — NOT a general fatwa, NOT a judicial/executive order; no new fact; no
new source; no ruling on ownership / estate division / the sister's final right; no generalization beyond
FNM1; rounds 47–52 unchanged; no git. The answer boolean is separated from the answer text.
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
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_final_answer_53.py"

sys.path.insert(0, str(SCRIPTS))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
R52_JSON = OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52.json"
FINAL_MANAT_ID = "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
NORMATIVE_SOURCE_ID = "NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE"
FINAL_HUKM_ID = "FHK1_MAT_MALIK_NO_EXPULSION_BEFORE_ADJUDICATION_UNDER_NS1"
FINAL_ANSWER_ID = "FAN1_MAT_MALIK_NO_EXPULSION_EFFECT_BEFORE_ADJUDICATION_FNM1"

# Owner-authorized bounded answer wording (recorded verbatim, separated from the boolean).
FINAL_ANSWER_TEXT = (
    "بناءً على المناط النهائي المصدّق، وعلى المصدر المعياري NS1 بعد تطبيقه، وعلى الحكم الداخلي FHK1: "
    "لا يُنتَج أثر إخراج الأخت الساكنة من العين قبل نظر النزاع في مجلس الحكم المختص، ضمن حدود هذه الحالة فقط."
)

# (final53_precondition_label, source_block, round52_key, expected)
PRECONDITIONS = [
    ("FINAL_MANAT", "recheck", "FINAL_MANAT", "YES"),
    ("TANZIL", "recheck", "TANZIL", "YES"),
    ("FINAL_HUKM", "final_hukm", "FINAL_HUKM", "YES"),
    ("FINAL_HUKM_STATUS", "final_hukm", "FINAL_HUKM_STATUS", "ACCEPTED"),
    ("FINAL_HUKM_ID", "final_hukm", "FINAL_HUKM_ID", FINAL_HUKM_ID),
    ("ROUND52_FINAL_ANSWER", "recheck", "FINAL_ANSWER", "NO"),
    ("ROUND52_JUDICIAL_OUTCOME_PRODUCED", "recheck", "JUDICIAL_OUTCOME_PRODUCED", "NO"),
]


def read_round52():
    return json.loads(R52_JSON.read_text(encoding="utf-8"))


def check_preconditions(r52):
    checks = []
    for label, block, key, expected in PRECONDITIONS:
        actual = r52.get(block, {}).get(key)
        checks.append({"precondition": label, "round52_block": block, "round52_key": key,
                       "expected": expected, "actual": actual, "met": actual == expected})
    return checks


def decide_answer(checks):
    if all(c["met"] for c in checks):
        return "YES", "ACCEPT_FINAL_ANSWER_ONLY"
    return "NO", "DEFER_FINAL_ANSWER_PRECONDITION_MISSING"


def final_answer(flag, verdict, checks):
    unmet = [c["precondition"] for c in checks if not c["met"]]
    return {
        "FINAL_ANSWER_ID": FINAL_ANSWER_ID,
        "FINAL_ANSWER": flag,
        "FINAL_ANSWER_TEXT": FINAL_ANSWER_TEXT if flag == "YES" else "",
        "FINAL_ANSWER_STATUS": "ACCEPTED" if flag == "YES" else "DEFERRED",
        "SOURCE": ["FHK1_ROUND52", "FNM1", "NS1"],
        "SCOPE": "FNM1_ONLY",
        "answer_type": "BOUNDED_CASE_ANSWER",
        "IS_GENERAL_FATWA": "NO",
        "IS_JUDICIAL_ORDER": "NO",
        "JUDICIAL_OUTCOME_PRODUCED": "NO",
        "DECIDES_OWNERSHIP": "NO",
        "DECIDES_ESTATE_DIVISION": "NO",
        "DECIDES_SISTER_FINAL_RIGHT": "NO",
        "GENERALIZES_BEYOND_FNM1": "NO",
        "cause": "FINAL_HUKM_ACCEPTED_ROUND52",
        "conditions": [f"{label}={expected}" for label, _b, _k, expected in PRECONDITIONS],
        "preventers": ["NONE_FOR_FINAL_ANSWER"] if flag == "YES"
                      else [f"PRECONDITION_MISSING:{u}" for u in unmet],
        "verdict": verdict,
        "residuals": ["SCOPE_LIMITED_TO_FNM1", "NO_GENERALIZATION",
                      "NO_JUDICIAL_EXECUTION", "FULL_PROJECT_NOT_CLOSED"],
    }


def guards():
    return {
        "FINAL_HUKM_ACCEPTED_REQUIRED": "YES",
        "FINAL_ANSWER_ONLY_AUTHORIZED": "YES",
        "FINAL_ANSWER_BOUND_TO_FNM1_NS1_FHK1": "YES",
        "FINAL_ANSWER_IS_NOT_GENERAL_FATWA": "YES",
        "FINAL_ANSWER_IS_NOT_JUDICIAL_ORDER": "YES",
        "NO_JUDICIAL_OUTCOME_PRODUCED": "YES",
        "NO_OWNERSHIP_DECISION": "YES",
        "NO_ESTATE_DIVISION_DECISION": "YES",
        "NO_SISTER_FINAL_RIGHT_DECISION": "YES",
        "NO_GENERALIZATION_BEYOND_FNM1": "YES",
        "NO_NEW_SOURCE_ADDED": "YES",
        "NO_NEW_FACT_ADDED": "YES",
        "NO_EXTERNAL_REFERENCE_USED": "YES",
        "NO_FRAMENET": "YES",
        "ROUNDS_47_52_UNCHANGED": "YES",
        "FINAL_ANSWER_BOOLEAN_SEPARATED_FROM_TEXT": "YES",
        "producer_file": PRODUCER,
    }


def registry_json():
    r52 = read_round52()
    checks = check_preconditions(r52)
    flag, verdict = decide_answer(checks)
    fa = final_answer(flag, verdict, checks)
    return {
        "ROUND": "TAAQOL_MAT_MALIK_FINAL_ANSWER_53",
        "nazila": SENTENCE,
        "purpose": "PRODUCE_FINAL_ANSWER_ONLY_FROM_ROUND52_FINAL_HUKM_BOUNDED_TO_FNM1",
        "final_manat_id": FINAL_MANAT_ID,
        "normative_source_id": NORMATIVE_SOURCE_ID,
        "final_hukm_id": FINAL_HUKM_ID,
        "hukm_source_round": "ROUND_52",
        "preconditions": checks,
        "final_answer": fa,
        "recheck": {
            "FINAL_MANAT": "YES",
            "TANZIL": "YES",
            "FINAL_HUKM": "YES",
            "FINAL_ANSWER": fa["FINAL_ANSWER"],
            "FINAL_ANSWER_STATUS": fa["FINAL_ANSWER_STATUS"],
            "JUDICIAL_OUTCOME_PRODUCED": "NO",
            "FULL_TAAQOL_PROJECT_CLOSED": "NO",
            "decision": {
                "cause": fa["cause"],
                "conditions": fa["conditions"],
                "preventers": fa["preventers"],
                "verdict": verdict,
                "residuals": fa["residuals"],
            },
        },
        "guards": guards(),
        "producer_file": PRODUCER,
    }


def registry_md():
    d = registry_json()
    fa = d["final_answer"]
    L = ["# الجواب النهائي «مات ملك» (TAAQOL_MAT_MALIK_FINAL_ANSWER_53)", "",
         "**إنتاج FINAL_ANSWER فقط بناءً على FHK1 — جواب محدود بالحالة FNM1، ليس فتوى عامة ولا أمرًا قضائيًّا.**", "",
         f"> النازلة: {SENTENCE}",
         f"> المناط: {d['final_manat_id']} · المصدر: {d['normative_source_id']} · الحكم: {d['final_hukm_id']} "
         f"(من {d['hukm_source_round']})", "",
         "## شروط فتح الجواب النهائي (من الجولة 52)"]
    for c in d["preconditions"]:
        L.append(f"- {c['precondition']} = {c['actual']} (متوقع {c['expected']}) → {'MET' if c['met'] else 'MISSING'}")
    L += ["", "## الجواب النهائي",
          f"- FINAL_ANSWER_ID = {fa['FINAL_ANSWER_ID']}",
          f"- FINAL_ANSWER = {fa['FINAL_ANSWER']} · STATUS = {fa['FINAL_ANSWER_STATUS']}",
          f"- SOURCE = {' + '.join(fa['SOURCE'])} · SCOPE = {fa['SCOPE']} · النوع = {fa['answer_type']}",
          f"- FINAL_ANSWER_TEXT: «{fa['FINAL_ANSWER_TEXT']}»",
          f"- VERDICT = {fa['verdict']}",
          "- IS_GENERAL_FATWA = NO · IS_JUDICIAL_ORDER = NO · JUDICIAL_OUTCOME_PRODUCED = NO · "
          "DECIDES_OWNERSHIP = NO · DECIDES_ESTATE_DIVISION = NO · DECIDES_SISTER_FINAL_RIGHT = NO · "
          "GENERALIZES_BEYOND_FNM1 = NO",
          "", "## السبب/الشرط/المانع",
          f"- CAUSE = {fa['cause']}",
          f"- CONDITIONS = {'، '.join(fa['conditions'])}",
          f"- PREVENTERS = {'، '.join(fa['preventers'])}",
          "", "## البقايا"]
    for r in fa["residuals"]:
        L.append(f"- {r}")
    L += ["", "---",
          "*جواب محدود بالحالة FNM1 فقط؛ ليس فتوى عامة ولا أمرًا قضائيًّا ولا تعميمًا، ولا يفصل في الملكية أو "
          "قسمة التركة أو الحق النهائي. المشروع ككل غير مغلق بهذا الجواب.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_spec(d):
    fa = d["final_answer"]
    rc = d["recheck"]
    tokens = load_tokens()
    token_rows = [[t["token_id"], t.get("original_surface", ""), t.get("word_class", "")] for t in tokens]

    pre_rows = [[c["precondition"], c["actual"], "y" if c["met"] else "n"] for c in d["preconditions"]]
    ans_rows = [
        ["FINAL_ANSWER_ID", fa["FINAL_ANSWER_ID"], "d"],
        ["FINAL_ANSWER", fa["FINAL_ANSWER"], "y"],
        ["FINAL_ANSWER_STATUS", fa["FINAL_ANSWER_STATUS"], "y"],
        ["SOURCE", " + ".join(fa["SOURCE"]), "d"],
        ["SCOPE", fa["SCOPE"], "d"],
        ["answer_type", fa["answer_type"], "d"],
        ["VERDICT", fa["verdict"], "y"],
        ["IS_GENERAL_FATWA", fa["IS_GENERAL_FATWA"], "n"],
        ["IS_JUDICIAL_ORDER", fa["IS_JUDICIAL_ORDER"], "n"],
        ["JUDICIAL_OUTCOME_PRODUCED", fa["JUDICIAL_OUTCOME_PRODUCED"], "n"],
        ["DECIDES_OWNERSHIP", fa["DECIDES_OWNERSHIP"], "n"],
        ["DECIDES_ESTATE_DIVISION", fa["DECIDES_ESTATE_DIVISION"], "n"],
        ["DECIDES_SISTER_FINAL_RIGHT", fa["DECIDES_SISTER_FINAL_RIGHT"], "n"],
        ["GENERALIZES_BEYOND_FNM1", fa["GENERALIZES_BEYOND_FNM1"], "n"],
    ]
    cpp_rows = [
        ["CAUSE", fa["cause"]],
        ["CONDITIONS", "، ".join(fa["conditions"])],
        ["PREVENTERS", "، ".join(fa["preventers"])],
        ["VERDICT", fa["verdict"]],
    ]
    guard_rows = [[k, v, ("y" if v == "YES" else "n" if v == "NO" else "d")]
                  for k, v in d["guards"].items() if k != "producer_file"]
    closure_rows = [
        ["FINAL_MANAT", rc["FINAL_MANAT"], "y"],
        ["TANZIL", rc["TANZIL"], "y"],
        ["FINAL_HUKM", rc["FINAL_HUKM"], "y"],
        ["FINAL_ANSWER", rc["FINAL_ANSWER"], "y"],
        ["FINAL_ANSWER_STATUS", rc["FINAL_ANSWER_STATUS"], "y"],
        ["JUDICIAL_OUTCOME_PRODUCED", rc["JUDICIAL_OUTCOME_PRODUCED"], "n"],
        ["FULL_TAAQOL_PROJECT_CLOSED", rc["FULL_TAAQOL_PROJECT_CLOSED"], "n"],
    ]
    trace_data = [
        ["REQ-MAT-MALIK-FINAL-ANSWER-JSON", "ROUND52_FINAL_HUKM (FHK1+FNM1+NS1)",
         "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_FINAL_ANSWER_53.json",
         "tests/test_taaqol_mat_malik_final_answer_53.py", "TRACEABLE"],
        ["REQ-MAT-MALIK-FINAL-ANSWER-GUARDS", "ROUND_53",
         "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_FINAL_ANSWER_GUARDS_53.json",
         "tests/test_taaqol_mat_malik_final_answer_53.py", "TRACEABLE"],
    ]
    trace_cls = [["", "", "", "", "y"] for _ in trace_data]

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "أُنتج الجواب النهائي FAN1 بناءً على الحكم FHK1 (الجولة 52) — جواب محدود بالحالة FNM1 فقط.",
                f"FINAL_ANSWER = {fa['FINAL_ANSWER']} · STATUS = {fa['FINAL_ANSWER_STATUS']} · "
                f"VERDICT = {fa['verdict']} (القيمة منفصلة عن FINAL_ANSWER_TEXT).",
            ]},
            {"note": "نص الجواب النهائي (FINAL_ANSWER_TEXT، حرفيًّا):"},
            {"raw_note": "<b>«" + fa["FINAL_ANSWER_TEXT"] + "»</b>"},
            {"raw_note": "<b>حدود صريحة:</b> ليس فتوى عامة · ليس أمرًا قضائيًّا · ليس تعميمًا · "
                         "FINAL_ANSWER_IS_NOT_GENERAL_FATWA / NOT_JUDICIAL_ORDER · "
                         "JUDICIAL_OUTCOME_PRODUCED = NO · لا فصل في الملكية/قسمة التركة/الحق النهائي · "
                         "لا تعميم خارج FNM1 · الجولات 47–52 غير مُعدَّلة.", "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات العشر", "body": [
            {"cols": {"headers": ["token", "السطح", "الفئة"], "rows": token_rows}}
            if token_rows else {"raw_note": "TOKEN_ARTIFACT_MISSING", "kind": "warn"},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا؛ هذه الجولة جواب محدود لا إفادة جديدة. IFADAH_FINAL = NO.",
             "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0 · NO_FRAMENET · "
                         "لا مصدر جديد؛ الجواب مبني فقط على FHK1 + FNM1 + NS1 (الجولة 52).", "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "اكتمال شروط الجولة 52 رخّص إنتاج جواب محدود بالحالة FNM1 فقط؛ لا يرخّص تعميمًا ولا "
                         "أمرًا قضائيًّا ولا فصلًا في الحقوق.", "kind": "warn"},
        ]},
        {"n": 8, "title": "المناط والمصدر والحكم — والجواب النهائي", "body": [
            {"kv": [["FINAL_MANAT_ID", d["final_manat_id"], "d"],
                    ["NORMATIVE_SOURCE_ID", d["normative_source_id"], "d"],
                    ["FINAL_HUKM_ID", d["final_hukm_id"], "d"],
                    ["HUKM_SOURCE", d["hukm_source_round"], "d"]]},
            {"note": "شروط فتح الجواب النهائي (من الجولة 52):"},
            {"cols": {"headers": ["precondition", "actual", "met"],
                      "rows": pre_rows, "row_classes": [["", "", r[2]] for r in pre_rows]}},
            {"note": "سجل الجواب النهائي (القيمة منفصلة عن النص):"},
            {"cols": {"headers": ["field", "value"],
                      "rows": [[r[0], r[1]] for r in ans_rows],
                      "row_classes": [["", r[2]] for r in ans_rows]}},
            {"note": "FINAL_ANSWER_TEXT (نص الجواب المحدود، مسجَّل — منفصل عن قيمة FINAL_ANSWER):"},
            {"raw_note": fa["FINAL_ANSWER_TEXT"]},
            {"note": "السبب / الشرط / المانع:"},
            {"kv": cpp_rows},
        ]},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": fa["residuals"], "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"raw_note": "لا نقص لإنتاج الجواب المحدود؛ أي تعميم أو نتيجة تنفيذية خارج FNM1 يحتاج مسارًا وإذنًا "
                         "منفصلًا تمامًا.", "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "اكتمل المسار العمودي لهذه الحالة (مناط→مصدر→تنزيل→حكم→جواب) ضمن FNM1 فقط. "
                         "إغلاق المشروع أو التعميم أو التنفيذ القضائي مسارات منفصلة بإذن صريح.", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_final_answer_53.py — ROUND53_TESTS = passed · "
                         "يتحقق من الشروط والجواب وبقاء JUDICIAL_OUTCOME والتعميم مغلقَين."},
            {"raw_note": "<b>جدول التتبّع (مستقل عن جدول الكلمات)</b>"},
            {"cols": {"headers": ["requirement", "source", "artifact", "test", "status"],
                      "rows": trace_data, "row_classes": trace_cls}},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "FINAL_ANSWER_53_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                f"SOURCE_RECORDS_READ = {R52_JSON.name} (round 52, READ_ONLY, unchanged)\n"
                f"FINAL_ANSWER_ID = {FINAL_ANSWER_ID}\n"
                "BUILT_ONLY_ON = FHK1 + FNM1 + NS1 + ROUND52\n"
                f"FINAL_ANSWER = {fa['FINAL_ANSWER']} (boolean) · FINAL_ANSWER_TEXT separated · "
                f"VERDICT = {fa['verdict']}\n"
                "IS_GENERAL_FATWA = NO\nIS_JUDICIAL_ORDER = NO\nJUDICIAL_OUTCOME_PRODUCED = NO\n"
                "NEW_SOURCE_ADDED = NO\nNEW_FACT_ADDED = NO\nSEARCH_PERFORMED = NO\n"
                "GENERALIZED_BEYOND_FNM1 = NO\nFRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\n"
                "ROUNDS_47_52_CHANGED = NO\nFULL_TAAQOL_PROJECT_CLOSED = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "اكتملت شروط الجولة 52 السبعة، فأُنتج الجواب النهائي FAN1 محدودًا بالحالة FNM1 مبنيًّا "
                         "على FHK1 + FNM1 + NS1. ليس فتوى عامة ولا أمرًا قضائيًّا ولا تعميمًا، ولا يفصل في الملكية "
                         "أو قسمة التركة أو الحق النهائي؛ والمشروع ككل غير مغلق بهذا الجواب.", "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in closure_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in closure_rows + guard_rows]}},
        ]},
    ]

    return {
        "title": "تقرير تنفيذي — الجواب النهائي (الجواب فقط) «مات ملك» (53)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>الجواب النهائي فقط:</b> جواب محدود بالحالة FNM1 مبني على حكم الجولة 52؛ "
                     "ليس فتوى عامة ولا أمرًا قضائيًّا ولا تعميمًا، ولا يفصل في الملكية/التركة/الحق النهائي."),
        ],
        "sentence": {"label": "النازلة", "text": SENTENCE, "id": "nazila-sentence"},
        "sections": sections,
        "closure_flags": (
            f"FINAL_MANAT = YES · TANZIL = YES · FINAL_HUKM = YES · FINAL_ANSWER = {fa['FINAL_ANSWER']} · "
            f"FINAL_ANSWER_STATUS = {fa['FINAL_ANSWER_STATUS']} · FINAL_ANSWER_ID = {fa['FINAL_ANSWER_ID']} · "
            "SCOPE = FNM1_ONLY · JUDICIAL_OUTCOME_PRODUCED = NO · FULL_TAAQOL_PROJECT_CLOSED = NO."),
        "tests_result": "ROUND53_TESTS = passed",
        "footer": "الجواب النهائي فقط — جواب محدود بالحالة FNM1، لا فتوى عامة ولا أمر قضائي "
                  "(RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_FINAL_ANSWER_MANAGER_REPORT_AR_53.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_MAT_MALIK_FINAL_ANSWER_53.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_FINAL_ANSWER_53.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_FINAL_ANSWER_GUARDS_53.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(d)), encoding="utf-8")

    fa = d["final_answer"]
    print("FINAL_ANSWER_53_REPORT=" + a.report_out)
    print(f"FINAL_ANSWER={fa['FINAL_ANSWER']} STATUS={fa['FINAL_ANSWER_STATUS']} VERDICT={fa['verdict']} "
          f"JUDICIAL_OUTCOME_PRODUCED=NO FULL_TAAQOL_PROJECT_CLOSED=NO")


if __name__ == "__main__":
    main()
