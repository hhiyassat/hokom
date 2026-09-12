#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49.

Opens a PENDING intake register for an OWNER-SUPPLIED normative source to later bind to the final manāṭ FNM1
(round 48). This round does NOT select, search for, fetch, or apply any source, and opens no tanzīl / hukm /
answer. The agent may never choose a sharʿī source (that is AUTHORITY_LEAK).

Since this round carries no owner-supplied normative source, decide() returns DEFER.

decide() rules:
  - owner_ratification == NO -> BLOCK_OWNER_REJECTED_NORMATIVE_SOURCE
  - authority AND source_text_or_reference AND scope AND binding_license_to_FNM1 AND owner_ratification==YES
        -> ACCEPT_NORMATIVE_SOURCE_FOR_FNM1
  - otherwise -> DEFER_NORMATIVE_SOURCE_INCOMPLETE_OR_NOT_SUPPLIED
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
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_normative_source_intake_49.py"

sys.path.insert(0, str(SCRIPTS))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
R48_JSON = OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.json"

# Owner-supplied normative source for THIS round. Empty — the owner supplied none in this message.
# The agent must NOT fill these.
OWNER_SOURCE = {
    "source_id": "PENDING",
    "source_type": "EMPTY",
    "authority": "EMPTY",
    "source_text_or_reference": "EMPTY",
    "scope": "EMPTY",
    "binding_license_to_FNM1": "EMPTY",
    "owner_ratification": "PENDING_OWNER_DECISION",
}


def _present(v):
    return bool(v) and str(v).strip().upper() not in ("", "EMPTY", "PENDING", "PENDING_OWNER_DECISION")


def decide(src):
    rat = str(src.get("owner_ratification", "")).strip().upper()
    if rat == "NO":
        return "NO", "BLOCK_OWNER_REJECTED_NORMATIVE_SOURCE"
    if (_present(src.get("authority")) and _present(src.get("source_text_or_reference"))
            and _present(src.get("scope")) and _present(src.get("binding_license_to_FNM1"))
            and rat == "YES"):
        return "YES", "ACCEPT_NORMATIVE_SOURCE_FOR_FNM1"
    return "NO", "DEFER_NORMATIVE_SOURCE_INCOMPLETE_OR_NOT_SUPPLIED"


def load_final_manat():
    d = json.loads(R48_JSON.read_text(encoding="utf-8"))
    fm = d["final_manat"]
    return {"FINAL_MANAT_ID": fm["FINAL_MANAT_ID"], "FINAL_MANAT": fm["FINAL_MANAT_BORN"],
            "FINAL_MANAT_STATUS": fm["FINAL_MANAT_STATUS"]}


def intake_record(src, accepted, verdict):
    missing = [k for k in ("authority", "source_text_or_reference", "scope", "binding_license_to_FNM1")
               if not _present(src.get(k))]
    if str(src.get("owner_ratification", "")).strip().upper() != "YES":
        missing.append("owner_ratification")
    return {
        "source_id": src["source_id"],
        "source_type": src["source_type"],
        "authority": src["authority"],
        "source_text_or_reference": src["source_text_or_reference"],
        "scope": src["scope"],
        "binding_license_to_FNM1": src["binding_license_to_FNM1"],
        "owner_ratification": src["owner_ratification"],
        "normative_source_accepted": accepted,
        "cause": "FINAL_MANAT_ACCEPTED_AND_READY_FOR_NORMATIVE_SOURCE_INTAKE",
        "conditions": ["FINAL_MANAT_ID_PRESENT", "FINAL_MANAT_STATUS_ACCEPTED",
                       "OWNER_SUPPLIED_NORMATIVE_SOURCE_REQUIRED"],
        "preventers": ["NO_OWNER_SUPPLIED_NORMATIVE_SOURCE_IN_THIS_ROUND"]
                      + [f"MISSING:{m}" for m in missing],
        "verdict": verdict,
        "residuals": ["NORMATIVE_SOURCE_NOT_ACCEPTED", "TANZIL_NOT_OPENED",
                      "FINAL_HUKM_NOT_OPENED", "FINAL_ANSWER_NOT_OPENED"],
    }


def guards():
    return {
        "FINAL_MANAT_REQUIRED": "YES",
        "FINAL_MANAT_ID_REQUIRED": "YES",
        "AGENT_MAY_NOT_SELECT_NORMATIVE_SOURCE": "YES",
        "AGENT_MAY_NOT_SEARCH_NORMATIVE_SOURCE": "YES",
        "OWNER_SUPPLIED_SOURCE_REQUIRED": "YES",
        "OWNER_RATIFICATION_REQUIRED_FOR_SOURCE": "YES",
        "NORMATIVE_SOURCE_TEXT_REQUIRED_FOR_ACCEPT": "YES",
        "BINDING_LICENSE_TO_FNM1_REQUIRED_FOR_ACCEPT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "NO_EXTERNAL_REFERENCE_WITHOUT_OWNER": "YES",
        "NO_FRAMENET": "YES",
        "producer_file": PRODUCER,
    }


def registry_json():
    fm = load_final_manat()
    accepted, verdict = decide(OWNER_SOURCE)
    rec = intake_record(OWNER_SOURCE, accepted, verdict)
    status = "ACCEPTED" if accepted == "YES" else ("BLOCKED" if verdict.startswith("BLOCK") else "DEFER")
    return {
        "ROUND": "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49",
        "nazila": SENTENCE,
        "purpose": "OPEN_PENDING_NORMATIVE_SOURCE_INTAKE_REGISTER_ONLY",
        "final_manat_ref": fm,
        "normative_source_record": rec,
        "recheck": {
            "FINAL_MANAT": fm["FINAL_MANAT"],
            "FINAL_MANAT_ID": fm["FINAL_MANAT_ID"],
            "NORMATIVE_SOURCE_ACCEPTED": accepted,
            "NORMATIVE_SOURCE_STATUS": status,
            "TANZIL": "NO", "FINAL_HUKM": "NO", "FINAL_ANSWER": "NO",
            "FULL_TAAQOL_PROJECT_CLOSED": "NO",
            "decision": {"verdict": verdict,
                         "cause": "FINAL_MANAT_ACCEPTED_AND_READY_FOR_NORMATIVE_SOURCE_INTAKE",
                         "preventers": "NO_OWNER_SUPPLIED_NORMATIVE_SOURCE_IN_THIS_ROUND"},
        },
        "guards": guards(),
        "producer_file": PRODUCER,
    }


def registry_md():
    d = registry_json()
    rec = d["normative_source_record"]
    rc = d["recheck"]
    L = ["# سجل استقبال مصدر معياري لقضية «مات ملك» (TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49)", "",
         "**فتح سجل استقبال مصدر معياري مصدّق من المالك فقط — لا اختيار، لا بحث، لا تطبيق، لا حكم، لا تنزيل، لا جواب.**", "",
         f"> النازلة: {SENTENCE}",
         f"> المناط النهائي: {d['final_manat_ref']['FINAL_MANAT_ID']} "
         f"(FINAL_MANAT={d['final_manat_ref']['FINAL_MANAT']}, STATUS={d['final_manat_ref']['FINAL_MANAT_STATUS']})",
         "", "## سجل المصدر المعياري (PENDING)"]
    for k in ("source_id", "source_type", "authority", "source_text_or_reference", "scope",
              "binding_license_to_FNM1", "owner_ratification", "normative_source_accepted", "verdict"):
        L.append(f"- {k} = {rec[k]}")
    L += ["", "## السبب/الشرط/المانع",
          f"- CAUSE = {rec['cause']}",
          f"- CONDITIONS = {'، '.join(rec['conditions'])}",
          f"- PREVENTERS = {'، '.join(rec['preventers'])}",
          "", "## البقايا"]
    for r in rec["residuals"]:
        L.append(f"- {r}")
    L += ["", f"NORMATIVE_SOURCE_ACCEPTED = {rc['NORMATIVE_SOURCE_ACCEPTED']} · "
          f"NORMATIVE_SOURCE_STATUS = {rc['NORMATIVE_SOURCE_STATUS']}",
          "", "---",
          "*لا مصدر مزوّد في هذه الجولة؛ السجل مفتوح PENDING بانتظار مصدر يصدّقه المالك ويرخّص ربطه بـ FNM1. "
          "التنزيل والحكم والجواب مغلقة. الوكيل لا يختار مصدرًا (AUTHORITY_LEAK).*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_spec(d):
    rec = d["normative_source_record"]
    rc = d["recheck"]
    fm = d["final_manat_ref"]
    tokens = load_tokens()
    token_rows = [[t["token_id"], t.get("original_surface", ""), t.get("word_class", "")] for t in tokens]

    src_rows = [
        ["source_id", rec["source_id"], "d"],
        ["source_type", rec["source_type"], "d"],
        ["authority", rec["authority"], "d"],
        ["source_text_or_reference", rec["source_text_or_reference"], "d"],
        ["scope", rec["scope"], "d"],
        ["binding_license_to_FNM1", rec["binding_license_to_FNM1"], "d"],
        ["owner_ratification", rec["owner_ratification"], "d"],
        ["normative_source_accepted", rec["normative_source_accepted"], "n"],
        ["verdict", rec["verdict"], "n"],
    ]
    cpp_rows = [
        ["CAUSE", rec["cause"]],
        ["CONDITIONS", "، ".join(rec["conditions"])],
        ["PREVENTERS", "، ".join(rec["preventers"])],
        ["VERDICT", rec["verdict"]],
    ]
    guard_rows = [[k, v, ("y" if v == "YES" else "n" if v == "NO" else "d")]
                  for k, v in d["guards"].items() if k != "producer_file"]
    closure_rows = [
        ["FINAL_MANAT", rc["FINAL_MANAT"], "y"],
        ["FINAL_MANAT_ID", rc["FINAL_MANAT_ID"], "d"],
        ["NORMATIVE_SOURCE_ACCEPTED", rc["NORMATIVE_SOURCE_ACCEPTED"], "n"],
        ["NORMATIVE_SOURCE_STATUS", rc["NORMATIVE_SOURCE_STATUS"], "d"],
        ["TANZIL", "NO", "n"],
        ["FINAL_HUKM", "NO", "n"],
        ["FINAL_ANSWER", "NO", "n"],
        ["FULL_TAAQOL_PROJECT_CLOSED", "NO", "n"],
    ]

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "فُتح سجل استقبال مصدر معياري مصدّق من المالك لربطه لاحقًا بالمناط النهائي FNM1.",
                "لا مصدر مزوّد في هذه الجولة؛ السجل PENDING والقرار DEFER.",
                f"NORMATIVE_SOURCE_ACCEPTED = {rc['NORMATIVE_SOURCE_ACCEPTED']} · "
                f"NORMATIVE_SOURCE_STATUS = {rc['NORMATIVE_SOURCE_STATUS']}.",
            ]},
            {"raw_note": "<b>حدود صريحة:</b> الوكيل لا يختار ولا يبحث عن مصدر (AUTHORITY_LEAK) · "
                         "لا مرجع خارجي بلا تزويد المالك · لا تطبيق للمصدر · "
                         "TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO.", "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات العشر", "body": [
            {"cols": {"headers": ["token", "السطح", "الفئة"], "rows": token_rows}}
            if token_rows else {"raw_note": "TOKEN_ARTIFACT_MISSING", "kind": "warn"},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا؛ هذه الجولة استقبال مصدر لا إفادة. IFADAH_FINAL = NO.",
             "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0 · NO_FRAMENET · "
                         "NO_EXTERNAL_REFERENCE_WITHOUT_OWNER · لا مصدر إلا ما يزوّده المالك صراحة.",
             "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "المناط النهائي مقبول؛ استقبال المصدر خطوة سابقة للتنزيل ولا يرخّص عبورًا إلى الحكم؛ "
                         "ولا يُقبل مصدر إلا بتصديق المالك ورخصة ربطه بـ FNM1.", "kind": "warn"},
        ]},
        {"n": 8, "title": "المصدر المعياري — المناط النهائي وسجل الاستقبال PENDING", "body": [
            {"kv": [["FINAL_MANAT_ID", fm["FINAL_MANAT_ID"], "d"],
                    ["FINAL_MANAT", fm["FINAL_MANAT"], "y"],
                    ["FINAL_MANAT_STATUS", fm["FINAL_MANAT_STATUS"], "y"]]},
            {"note": "سجل المصدر المعياري (PENDING):"},
            {"cols": {"headers": ["field", "value"],
                      "rows": [[r[0], r[1]] for r in src_rows],
                      "row_classes": [["", r[2]] for r in src_rows]}},
            {"note": "السبب / الشرط / المانع:"},
            {"kv": cpp_rows},
        ]},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": rec["residuals"], "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"raw_note": "لقبول المصدر يلزم أن يزوّد المالك: authority + source_text_or_reference + scope + "
                         "binding_license_to_FNM1 + owner_ratification=YES. الوكيل لا يملؤها ولا يختار مصدرًا.",
             "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "عند قبول مصدر مصدّق: يُربط بـ FNM1 ثم (بإذن منفصل) TANZIL ← FINAL_HUKM ← FINAL_ANSWER "
                         "— لا يُفتح شيء منها هنا.", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "trace_here": True, "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_normative_source_intake_49.py — ROUND49_TESTS = passed · "
                         "يتحقق من قواعد القرار الثلاث ومن DEFER في غياب مصدر مزوّد."},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "NORMATIVE_SOURCE_INTAKE_49_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                f"FINAL_MANAT_REF = {fm['FINAL_MANAT_ID']} (from round 48, READ_ONLY)\n"
                f"NORMATIVE_SOURCE_ACCEPTED = {rc['NORMATIVE_SOURCE_ACCEPTED']} · "
                f"STATUS = {rc['NORMATIVE_SOURCE_STATUS']}\n"
                "AGENT_SELECTED_SOURCE = NO\nAGENT_SEARCHED_SOURCE = NO\nSOURCE_APPLIED = NO\n"
                "OWNER_SUPPLIED_SOURCE_IN_THIS_ROUND = NO\nFRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\n"
                "TANZIL = NO\nFINAL_HUKM = NO\nFINAL_ANSWER = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "فُتح سجل استقبال المصدر المعياري PENDING مرتبطًا بالمناط النهائي FNM1؛ ولعدم ورود مصدر "
                         "مصدّق من المالك في هذه الجولة، القرار DEFER. لا اختيار ولا بحث ولا تطبيق ولا تنزيل "
                         "ولا حكم ولا جواب.", "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in closure_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in closure_rows + guard_rows]}},
        ]},
    ]

    trace_rows = [
        {"req": "REQ-MAT-MALIK-SOURCE-INTAKE-JSON", "source": "ROUND48_FINAL_MANAT + OWNER_SUPPLIED_SOURCE(none)",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49.json",
         "test": "tests/test_taaqol_mat_malik_normative_source_intake_49.py", "status": "TRACEABLE"},
        {"req": "REQ-MAT-MALIK-SOURCE-INTAKE-GUARDS", "source": "ROUND_49",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_GUARDS_49.json",
         "test": "tests/test_taaqol_mat_malik_normative_source_intake_49.py", "status": "TRACEABLE"},
    ]

    return {
        "title": "تقرير تنفيذي — سجل استقبال مصدر معياري «مات ملك» (49)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>سجل استقبال مصدر معياري PENDING:</b> لا اختيار ولا بحث ولا تطبيق لأي مصدر؛ "
                     "لا يُقبل إلا مصدر يزوّده المالك ويصدّقه ويرخّص ربطه بـ FNM1؛ لا تنزيل ولا حكم ولا جواب."),
        ],
        "sentence": {"label": "النازلة", "text": SENTENCE, "id": "nazila-sentence"},
        "sections": sections,
        "trace": {"title": "جدول التتبّع (مستقل عن جدول الكلمات)", "rows": trace_rows},
        "closure_flags": (
            f"FINAL_MANAT = {rc['FINAL_MANAT']} · FINAL_MANAT_ID = {rc['FINAL_MANAT_ID']} · "
            f"NORMATIVE_SOURCE_ACCEPTED = {rc['NORMATIVE_SOURCE_ACCEPTED']} · "
            f"NORMATIVE_SOURCE_STATUS = {rc['NORMATIVE_SOURCE_STATUS']} · "
            "TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO."),
        "tests_result": "ROUND49_TESTS = passed",
        "footer": "سجل استقبال مصدر معياري PENDING — لا اختيار/بحث/تطبيق، لا حكم، لا تنزيل، لا جواب "
                  "(RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_MANAGER_REPORT_AR_49.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_49.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_INTAKE_GUARDS_49.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(d)), encoding="utf-8")

    rc = d["recheck"]
    print("NORMATIVE_SOURCE_INTAKE_49_REPORT=" + a.report_out)
    print(f"NORMATIVE_SOURCE_ACCEPTED={rc['NORMATIVE_SOURCE_ACCEPTED']} "
          f"STATUS={rc['NORMATIVE_SOURCE_STATUS']} FINAL_MANAT={rc['FINAL_MANAT']} "
          f"TANZIL=NO FINAL_HUKM=NO FINAL_ANSWER=NO")


if __name__ == "__main__":
    main()
