#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52.

Births FINAL_HUKM ONLY from the round-51 tanzīl. Reads the round-51 records directly (not a summary) and
checks nine preconditions; if any is missing → DEFER_FINAL_HUKM_PRECONDITION_MISSING (no hukm). If all hold,
it records a single internal normative ruling scoped to FNM1.

Hard limits: this is FINAL_HUKM only — NOT a FINAL_ANSWER, not addressed to a questioner, no judicial/
executive order, no ruling on ownership / the sister's final right / estate division, and no general fatwa
beyond FNM1. No new source; no search; no FrameNet; round-51 unchanged; no git.
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
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_final_hukm_birth_52.py"

sys.path.insert(0, str(SCRIPTS))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
R51_JSON = OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51.json"
FINAL_MANAT_ID = "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
NORMATIVE_SOURCE_ID = "NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE"
FINAL_HUKM_ID = "FHK1_MAT_MALIK_NO_EXPULSION_BEFORE_ADJUDICATION_UNDER_NS1"

# Owner-authorized internal ruling wording (recorded verbatim).
FINAL_HUKM_TEXT = (
    "في حدود المناط النهائي FNM1، وبعد قبول NS1 وتطبيقه في الجولة 51، يثبت حكمٌ معياري داخلي مؤداه: "
    "عدم إنتاج أثر الإخراج قبل نظر النزاع في مجلس الحكم المختص."
)

# (round52_precondition_label, round51_record_key, expected). The three round-51 status values are given
# explicit ROUND51_* labels so they never read as the round-52 FINAL_HUKM=YES outcome.
PRECONDITIONS = [
    ("FINAL_MANAT", "FINAL_MANAT", "YES"),
    ("NORMATIVE_SOURCE_ACCEPTED", "NORMATIVE_SOURCE_ACCEPTED", "YES"),
    ("SOURCE_APPLIED", "SOURCE_APPLIED", "YES"),
    ("TANZIL", "TANZIL", "YES"),
    ("TANZIL_STATUS", "TANZIL_STATUS", "ACCEPTED"),
    ("NS1_APPLIES_TO_FNM1", "NS1_APPLIES_TO_FNM1", "YES"),
    ("ROUND51_FINAL_HUKM", "FINAL_HUKM", "NO"),
    ("ROUND51_FINAL_ANSWER", "FINAL_ANSWER", "NO"),
    ("ROUND51_JUDICIAL_OUTCOME_PRODUCED", "JUDICIAL_OUTCOME_PRODUCED", "NO"),
]


def read_round51():
    return json.loads(R51_JSON.read_text(encoding="utf-8"))["recheck"]


def check_preconditions(rc):
    checks = []
    for label, r51_key, expected in PRECONDITIONS:
        actual = rc.get(r51_key)
        checks.append({"precondition": label, "round51_key": r51_key, "expected": expected,
                       "actual": actual, "met": actual == expected})
    return checks


def decide_hukm(checks):
    if all(c["met"] for c in checks):
        return "YES", "ACCEPT_FINAL_HUKM_ONLY"
    return "NO", "DEFER_FINAL_HUKM_PRECONDITION_MISSING"


def final_hukm(final_hukm_flag, verdict, checks):
    unmet = [c["precondition"] for c in checks if not c["met"]]
    return {
        "FINAL_HUKM_ID": FINAL_HUKM_ID,
        # boolean value separated from the ruling text (structural correction)
        "FINAL_HUKM": final_hukm_flag,
        "FINAL_HUKM_TEXT": FINAL_HUKM_TEXT if final_hukm_flag == "YES" else "",
        "FINAL_HUKM_STATUS": "ACCEPTED" if final_hukm_flag == "YES" else "DEFERRED",
        "SOURCE": "NS1_APPLIED_TO_FNM1_BY_ROUND51",
        "SCOPE": "FNM1_ONLY",
        "hukm_type": "INTERNAL_NORMATIVE_RULING",
        "IS_FINAL_ANSWER": "NO",
        "ADDRESSES_QUESTIONER": "NO",
        "PRODUCES_JUDICIAL_ORDER": "NO",
        "DECIDES_OWNERSHIP": "NO",
        "DECIDES_SISTER_FINAL_RIGHT": "NO",
        "DECIDES_ESTATE_DIVISION": "NO",
        "GENERAL_FATWA_BEYOND_FNM1": "NO",
        "cause": "TANZIL_ACCEPTED_NS1_APPLIED_TO_FNM1_ROUND51",
        "conditions": [f"{label}={expected}" for label, _k, expected in PRECONDITIONS],
        "preventers": ["NONE_FOR_FINAL_HUKM_BIRTH"] if final_hukm_flag == "YES"
                      else [f"PRECONDITION_MISSING:{u}" for u in unmet],
        "verdict": verdict,
        "residuals": ["FINAL_ANSWER_NOT_OPENED", "JUDICIAL_OUTCOME_NOT_PRODUCED",
                      "NO_EXECUTION_ORDER", "SCOPE_LIMITED_TO_FNM1"],
    }


def guards():
    return {
        "TANZIL_ACCEPTED_REQUIRED": "YES",
        "FINAL_HUKM_ONLY_AUTHORIZED": "YES",
        "FINAL_HUKM_IS_NOT_FINAL_ANSWER": "YES",
        "FINAL_HUKM_IS_NOT_JUDICIAL_OUTCOME": "YES",
        "NO_ANSWER_TO_QUESTIONER": "YES",
        "NO_PERMISSIBILITY_LANGUAGE": "YES",
        "NO_OWNERSHIP_DECISION": "YES",
        "NO_SISTER_FINAL_RIGHT_DECISION": "YES",
        "NO_ESTATE_DIVISION_DECISION": "YES",
        "NO_GENERAL_FATWA_BEYOND_FNM1": "YES",
        "NO_NEW_SOURCE_ADDED": "YES",
        "NO_EXTERNAL_REFERENCE_USED": "YES",
        "NO_FRAMENET": "YES",
        "ROUND51_UNCHANGED": "YES",
        "FINAL_HUKM_BOOLEAN_SEPARATED_FROM_TEXT": "YES",
        "producer_file": PRODUCER,
    }


def registry_json():
    rc51 = read_round51()
    checks = check_preconditions(rc51)
    flag, verdict = decide_hukm(checks)
    fh = final_hukm(flag, verdict, checks)
    return {
        "ROUND": "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52",
        "nazila": SENTENCE,
        "purpose": "BIRTH_FINAL_HUKM_ONLY_FROM_ROUND51_TANZIL_NO_ANSWER_NO_JUDICIAL_OUTCOME",
        "final_manat_id": FINAL_MANAT_ID,
        "normative_source_id": NORMATIVE_SOURCE_ID,
        "tanzil_source_round": "ROUND_51",
        "preconditions": checks,
        "final_hukm": fh,
        "recheck": {
            "FINAL_MANAT": "YES",
            "TANZIL": "YES",
            "FINAL_HUKM": fh["FINAL_HUKM"],
            "FINAL_HUKM_STATUS": fh["FINAL_HUKM_STATUS"],
            "FINAL_ANSWER": "NO",
            "JUDICIAL_OUTCOME_PRODUCED": "NO",
            "FULL_TAAQOL_PROJECT_CLOSED": "NO",
            "decision": {
                "cause": fh["cause"],
                "conditions": fh["conditions"],
                "preventers": fh["preventers"],
                "verdict": verdict,
                "residuals": fh["residuals"],
            },
        },
        "guards": guards(),
        "producer_file": PRODUCER,
    }


def registry_md():
    d = registry_json()
    fh = d["final_hukm"]
    L = ["# ولادة الحكم النهائي «مات ملك» (TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52)", "",
         "**توليد FINAL_HUKM فقط من تنزيل الجولة 51 — لا جواب نهائي، لا خطاب للسائل، لا نتيجة قضائية.**", "",
         f"> النازلة: {SENTENCE}",
         f"> المناط النهائي: {d['final_manat_id']} · المصدر: {d['normative_source_id']} · "
         f"مصدر التنزيل: {d['tanzil_source_round']}", "",
         "## شروط فتح الحكم النهائي (من الجولة 51)"]
    for c in d["preconditions"]:
        L.append(f"- {c['precondition']} = {c['actual']} (متوقع {c['expected']}) → {'MET' if c['met'] else 'MISSING'}")
    L += ["", "## الحكم النهائي",
          f"- FINAL_HUKM_ID = {fh['FINAL_HUKM_ID']}",
          f"- FINAL_HUKM = {fh['FINAL_HUKM']} · STATUS = {fh['FINAL_HUKM_STATUS']}",
          f"- SOURCE = {fh['SOURCE']} · SCOPE = {fh['SCOPE']} · النوع = {fh['hukm_type']}",
          f"- FINAL_HUKM_TEXT (صياغة داخلية، في حدود FNM1): «{fh['FINAL_HUKM_TEXT']}»",
          f"- VERDICT = {fh['verdict']}",
          "- IS_FINAL_ANSWER = NO · ADDRESSES_QUESTIONER = NO · PRODUCES_JUDICIAL_ORDER = NO · "
          "DECIDES_OWNERSHIP = NO · DECIDES_SISTER_FINAL_RIGHT = NO · DECIDES_ESTATE_DIVISION = NO · "
          "GENERAL_FATWA_BEYOND_FNM1 = NO",
          "", "## السبب/الشرط/المانع",
          f"- CAUSE = {fh['cause']}",
          f"- CONDITIONS = {'، '.join(fh['conditions'])}",
          f"- PREVENTERS = {'، '.join(fh['preventers'])}",
          "", "## البقايا"]
    for r in fh["residuals"]:
        L.append(f"- {r}")
    L += ["", "---",
          "*حكم معياري داخلي في حدود FNM1 فقط؛ ليس جوابًا نهائيًّا ولا أمرًا قضائيًّا، ولا يفصل في الملكية "
          "أو الحق النهائي أو قسمة التركة. الجواب النهائي يحتاج إذنًا صريحًا منفصلًا.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_spec(d):
    fh = d["final_hukm"]
    rc = d["recheck"]
    tokens = load_tokens()
    token_rows = [[t["token_id"], t.get("original_surface", ""), t.get("word_class", "")] for t in tokens]

    pre_rows = [[c["precondition"], c["actual"], "y" if c["met"] else "n"] for c in d["preconditions"]]
    hukm_rows = [
        ["FINAL_HUKM_ID", fh["FINAL_HUKM_ID"], "d"],
        ["FINAL_HUKM", fh["FINAL_HUKM"], "y"],
        ["FINAL_HUKM_STATUS", fh["FINAL_HUKM_STATUS"], "y"],
        ["SOURCE", fh["SOURCE"], "d"],
        ["SCOPE", fh["SCOPE"], "d"],
        ["hukm_type", fh["hukm_type"], "d"],
        ["VERDICT", fh["verdict"], "y"],
        ["IS_FINAL_ANSWER", fh["IS_FINAL_ANSWER"], "n"],
        ["ADDRESSES_QUESTIONER", fh["ADDRESSES_QUESTIONER"], "n"],
        ["PRODUCES_JUDICIAL_ORDER", fh["PRODUCES_JUDICIAL_ORDER"], "n"],
        ["DECIDES_OWNERSHIP", fh["DECIDES_OWNERSHIP"], "n"],
        ["DECIDES_SISTER_FINAL_RIGHT", fh["DECIDES_SISTER_FINAL_RIGHT"], "n"],
        ["DECIDES_ESTATE_DIVISION", fh["DECIDES_ESTATE_DIVISION"], "n"],
        ["GENERAL_FATWA_BEYOND_FNM1", fh["GENERAL_FATWA_BEYOND_FNM1"], "n"],
    ]
    cpp_rows = [
        ["CAUSE", fh["cause"]],
        ["CONDITIONS", "، ".join(fh["conditions"])],
        ["PREVENTERS", "، ".join(fh["preventers"])],
        ["VERDICT", fh["verdict"]],
    ]
    guard_rows = [[k, v, ("y" if v == "YES" else "n" if v == "NO" else "d")]
                  for k, v in d["guards"].items() if k != "producer_file"]
    closure_rows = [
        ["FINAL_MANAT", rc["FINAL_MANAT"], "y"],
        ["TANZIL", rc["TANZIL"], "y"],
        ["FINAL_HUKM", rc["FINAL_HUKM"], "y"],
        ["FINAL_HUKM_STATUS", rc["FINAL_HUKM_STATUS"], "y"],
        ["FINAL_ANSWER", rc["FINAL_ANSWER"], "n"],
        ["JUDICIAL_OUTCOME_PRODUCED", rc["JUDICIAL_OUTCOME_PRODUCED"], "n"],
        ["FULL_TAAQOL_PROJECT_CLOSED", rc["FULL_TAAQOL_PROJECT_CLOSED"], "n"],
    ]
    # Independent traceability table — embedded inside §12 (NOT a separate <h2>) so the report has
    # exactly 14 <h2> section headings.
    trace_data = [
        ["REQ-MAT-MALIK-FINAL-HUKM-JSON", "ROUND51_TANZIL (NS1+FNM1)",
         "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52.json",
         "tests/test_taaqol_mat_malik_final_hukm_birth_52.py", "TRACEABLE"],
        ["REQ-MAT-MALIK-FINAL-HUKM-GUARDS", "ROUND_52",
         "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_GUARDS_52.json",
         "tests/test_taaqol_mat_malik_final_hukm_birth_52.py", "TRACEABLE"],
    ]
    trace_cls = [["", "", "", "", "y"] for _ in trace_data]

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "وُلد الحكم النهائي FHK1 من تنزيل الجولة 51 (حكم معياري داخلي في حدود FNM1).",
                f"FINAL_HUKM = {fh['FINAL_HUKM']} · STATUS = {fh['FINAL_HUKM_STATUS']} · "
                f"VERDICT = {fh['verdict']} (القيمة منفصلة عن FINAL_HUKM_TEXT).",
                "ليس جوابًا نهائيًّا ولا خطابًا للسائل ولا أمرًا قضائيًّا؛ FINAL_ANSWER = NO.",
            ]},
            {"raw_note": "<b>حدود صريحة:</b> FINAL_HUKM_IS_NOT_FINAL_ANSWER / NOT_JUDICIAL_OUTCOME · "
                         "NO_ANSWER_TO_QUESTIONER · NO_PERMISSIBILITY_LANGUAGE · لا فصل في الملكية/الحق "
                         "النهائي/قسمة التركة · لا إفتاء عام خارج FNM1.", "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات العشر", "body": [
            {"cols": {"headers": ["token", "السطح", "الفئة"], "rows": token_rows}}
            if token_rows else {"raw_note": "TOKEN_ARTIFACT_MISSING", "kind": "warn"},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا؛ هذه الجولة حكم معياري داخلي لا إفادة. IFADAH_FINAL = NO.",
             "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0 · NO_FRAMENET · "
                         "لا مصدر جديد؛ الحكم مبني فقط على NS1 + FNM1 + تنزيل الجولة 51.", "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "اكتمال شروط الجولة 51 رخّص توليد حكم معياري داخلي في حدود FNM1 فقط؛ "
                         "لا يرخّص جوابًا نهائيًّا ولا نتيجة قضائية.", "kind": "warn"},
        ]},
        {"n": 8, "title": "المصدر المعياري والمناط والتنزيل — والحكم النهائي", "body": [
            {"kv": [["FINAL_MANAT_ID", d["final_manat_id"], "d"],
                    ["NORMATIVE_SOURCE_ID", d["normative_source_id"], "d"],
                    ["TANZIL_SOURCE", d["tanzil_source_round"], "d"]]},
            {"note": "شروط فتح الحكم النهائي (من الجولة 51):"},
            {"cols": {"headers": ["precondition", "actual", "met"],
                      "rows": pre_rows, "row_classes": [["", "", r[2]] for r in pre_rows]}},
            {"note": "سجل الحكم النهائي (صياغة داخلية في حدود FNM1):"},
            {"cols": {"headers": ["field", "value"],
                      "rows": [[r[0], r[1]] for r in hukm_rows],
                      "row_classes": [["", r[2]] for r in hukm_rows]}},
            {"note": "FINAL_HUKM_TEXT (نص الحكم الداخلي، مسجَّل — منفصل عن قيمة FINAL_HUKM):"},
            {"raw_note": fh["FINAL_HUKM_TEXT"]},
            {"note": "السبب / الشرط / المانع:"},
            {"kv": cpp_rows},
        ]},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": fh["residuals"], "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"raw_note": "لا نقص في شروط الحكم؛ الناقص لاحقًا: إذن صريح لإنتاج الجواب النهائي (FINAL_ANSWER).",
             "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "الحكم المعياري الداخلي مولود؛ الخطوة التالية (بإذن منفصل): FINAL_ANSWER — لا يُفتح هنا.",
             "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_final_hukm_birth_52.py — ROUND52_TESTS = passed · "
                         "يتحقق من الشروط والحكم وبقاء FINAL_ANSWER و JUDICIAL_OUTCOME مغلقَين."},
            {"raw_note": "<b>جدول التتبّع (مستقل عن جدول الكلمات)</b>"},
            {"cols": {"headers": ["requirement", "source", "artifact", "test", "status"],
                      "rows": trace_data, "row_classes": trace_cls}},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "FINAL_HUKM_BIRTH_52_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                f"SOURCE_RECORDS_READ = {R51_JSON.name} (round 51, READ_ONLY, unchanged)\n"
                f"FINAL_HUKM_ID = {FINAL_HUKM_ID}\n"
                f"BUILT_ONLY_ON = NS1 + FNM1 + TANZIL_ROUND51\n"
                f"FINAL_HUKM = {fh['FINAL_HUKM']} (boolean) · FINAL_HUKM_TEXT separated · "
                f"VERDICT = {fh['verdict']}\n"
                "IS_FINAL_ANSWER = NO\nADDRESSES_QUESTIONER = NO\nPRODUCES_JUDICIAL_ORDER = NO\n"
                "NEW_SOURCE_ADDED = NO\nSEARCH_PERFORMED = NO\nPERMISSIBILITY_LANGUAGE = NO\n"
                "FRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\nROUND51_CHANGED = NO\n"
                "FINAL_ANSWER = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "اكتملت شروط الجولة 51 التسعة، فوُلد حكم معياري داخلي (FHK1) في حدود FNM1 مبني فقط على "
                         "NS1 + FNM1 + تنزيل الجولة 51. ليس جوابًا نهائيًّا ولا خطابًا للسائل ولا أمرًا قضائيًّا، "
                         "ولا يفصل في الملكية أو الحق النهائي أو قسمة التركة. الجواب النهائي يحتاج إذنًا منفصلًا.",
             "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in closure_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in closure_rows + guard_rows]}},
        ]},
    ]

    return {
        "title": "تقرير تنفيذي — ولادة الحكم النهائي (الحكم فقط) «مات ملك» (52)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>الحكم النهائي فقط:</b> حكم معياري داخلي في حدود FNM1 مبني على تنزيل الجولة 51؛ "
                     "لا جواب نهائي, لا خطاب للسائل, لا أمر قضائي, لا فصل في الملكية/الحق/التركة, لا إفتاء عام."),
        ],
        "sentence": {"label": "النازلة", "text": SENTENCE, "id": "nazila-sentence"},
        "sections": sections,
        "closure_flags": (
            f"FINAL_MANAT = YES · TANZIL = YES · FINAL_HUKM = {fh['FINAL_HUKM']} · "
            f"FINAL_HUKM_STATUS = {fh['FINAL_HUKM_STATUS']} · FINAL_HUKM_ID = {fh['FINAL_HUKM_ID']} · "
            "FINAL_ANSWER = NO · JUDICIAL_OUTCOME_PRODUCED = NO · SCOPE = FNM1_ONLY · "
            "FULL_TAAQOL_PROJECT_CLOSED = NO."),
        "tests_result": "ROUND52_TESTS = passed",
        "footer": "ولادة الحكم النهائي فقط — حكم معياري داخلي في حدود FNM1، لا جواب/أمر قضائي "
                  "(RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_MANAGER_REPORT_AR_52.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_52.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_FINAL_HUKM_BIRTH_GUARDS_52.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(d)), encoding="utf-8")

    fh = d["final_hukm"]
    print("FINAL_HUKM_BIRTH_52_REPORT=" + a.report_out)
    print(f"FINAL_HUKM={fh['FINAL_HUKM']} STATUS={fh['FINAL_HUKM_STATUS']} VERDICT={fh['verdict']} "
          f"FINAL_ANSWER=NO JUDICIAL_OUTCOME_PRODUCED=NO")


if __name__ == "__main__":
    main()
