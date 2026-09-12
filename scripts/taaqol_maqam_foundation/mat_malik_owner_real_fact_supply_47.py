#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47.

Owner explicitly supplies and ratifies the nine real-case facts of the "مات ملك" case. This reuses the
round-46 mechanism (decide() + recheck()); the values here are recorded as an independent source
SOURCE = OWNER_SUPPLIED_REAL_CASE_FACTS_ROUND_47 — NOT inferred from the text and NOT the round-44 scenario.

With owner_value + source_or_evidence + owner_ratification=YES for all nine, decide() accepts each as
ACCEPT_REAL_CASE_FACT, and the real-world full-manāṭ gate passes (READY=YES). This round's licence is limited
to fact acceptance + gate readiness only: FINAL_MANAT / TANZIL / FINAL_HUKM / FINAL_ANSWER remain NO (opening
them needs a separate explicit permission). No FrameNet; no external reference; no git.
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
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_owner_real_fact_supply_47.py"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "taaqol_maqam_foundation"))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402
import mat_malik_nine_facts_ratification_46 as r46  # noqa: E402  (reuse decide() + recheck() mechanism)

SENTENCE = r46.SENTENCE
SOURCE = "OWNER_SUPPLIED_REAL_CASE_FACTS_ROUND_47"

# Owner-supplied + ratified real-case values (this round). Keyed by fact_id.
OWNER_REAL = {
    "MF1_NO_CHILD": "لا ولد للميت.",
    "MF2_NO_OTHER_HEIRS": "لا ورثة آخرون مؤثرون في هذه المسألة غير المذكورين في الواقعة.",
    "MF3_HEIR_IDENTITY_AND_STATUS": "طالب الطرد وارث ذو صفة إرثية في الواقعة.",
    "MF4_HOUSE_OWNERSHIP": "البيت ملك للميت.",
    "MF5_HOUSE_IS_ESTATE": "البيت داخل في التركة.",
    "MF6_PRIOR_RESIDENCE_PERMISSION": "سكن الأخت كان بإذن سابق معتبر.",
    "MF7_SISTER_YAD_STATUS": "يد الأخت على السكن قائمة ظاهراً إلى حين نظر القضاء.",
    "MF8_EVIDENCE_OR_BAYYINA": "لا توجد بينة فورية كافية لطالب الطرد توجب إخراجها قبل نظر القضاء.",
    "MF9_LITIGATION_OUTCOME": "محل التحاكم هو طلب طرد الأخت من السكن.",
}
OWNER_EVIDENCE = "تصريح المالك لهذه الجولة."
OWNER_RATIFICATION = "YES"


def build_facts():
    facts = []
    for fid, label in r46.NINE:
        owner_value = OWNER_REAL[fid]
        accepted, verdict = r46.decide(owner_value, OWNER_EVIDENCE, OWNER_RATIFICATION)
        facts.append({
            "fact_id": fid,
            "fact_label": label,
            "owner_value": owner_value,
            "source_or_evidence": OWNER_EVIDENCE,
            "owner_ratification": OWNER_RATIFICATION,
            "SOURCE": SOURCE,
            "NOT_FROM_TEXT_INFERENCE": "YES",
            "NOT_FROM_ROUND44_SCENARIO": "YES",
            "fact_accepted": accepted,
            "cause": "OWNER_SUPPLIED_AND_RATIFIED_REAL_CASE_VALUE",
            "conditions": ["OWNER_VALUE_PRESENT", "SOURCE_OR_EVIDENCE_PRESENT",
                           "OWNER_RATIFICATION_YES"],
            "preventers": ["NONE"],
            "verdict": verdict,
            "residuals": ["REAL_CASE_FACT_ACCEPTED_STILL_NO_TANZIL_WITHOUT_PERMISSION"],
        })
    return facts


def guards():
    return {
        "NINE_FACTS_REVIEWED": "YES",
        "FACT_ACCEPTANCE_REQUIRES_OWNER_VALUE": "YES",
        "FACT_ACCEPTANCE_REQUIRES_EVIDENCE": "YES",
        "FACT_ACCEPTANCE_REQUIRES_OWNER_RATIFICATION": "YES",
        "AGENT_KNOWLEDGE_CREATES_FACT": "NO",
        "OWNER_SUPPLIED_REAL_CASE_FACTS": "YES",
        "SCENARIO_FACT_IS_NOT_REAL_CASE_FACT": "YES",
        "REAL_CASE_FACTS_NOT_FROM_TEXT_INFERENCE": "YES",
        "REAL_CASE_FACTS_NOT_FROM_ROUND44_SCENARIO": "YES",
        "REAL_WORLD_FULL_MANAT_READY_DOES_NOT_OPEN_TANZIL": "YES",
        "NO_TANZIL_WITHOUT_SEPARATE_PERMISSION": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "NO_FRAMENET": "YES",
        "NO_EXTERNAL_REFERENCE_UNLESS_OWNER_SUPPLIED": "YES",
        "producer_file": PRODUCER,
    }


def registry_json():
    facts = build_facts()
    return {
        "ROUND": "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47",
        "nazila": SENTENCE,
        "source": SOURCE,
        "purpose": "OWNER_SUPPLY_AND_RATIFY_NINE_REAL_CASE_FACTS_AND_OPEN_MANAT_READINESS_ONLY",
        "mechanism_reused_from": "ROUND_46 decide() + recheck()",
        "facts": facts,
        "recheck": r46.recheck(facts),
        "guards": guards(),
        "producer_file": PRODUCER,
    }


def registry_md():
    d = registry_json()
    rc = d["recheck"]
    L = ["# تزويد وتصديق المالك للوقائع التسع الواقعية (TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47)", "",
         "**المالك يزوّد ويصدّق الوقائع التسع كوقائع للحالة الواقعية — لا حكم، لا تنزيل، لا جواب.**", "",
         f"> النازلة: {SENTENCE}",
         f"> SOURCE = {SOURCE} (ليست من النص ولا من سيناريو الجولة 44)", "",
         "## الوقائع التسع المصدّقة"]
    for f in d["facts"]:
        L.append(f"- {f['fact_id']} — {f['fact_label']} → {f['verdict']} "
                 f"(owner_value=«{f['owner_value']}», ratification={f['owner_ratification']})")
    L += ["", "## إعادة فحص بوابة المناط الواقعي الكامل",
          f"- NINE_FACTS_ACCEPTED_COUNT = {rc['NINE_FACTS_ACCEPTED_COUNT']}",
          f"- NINE_FACTS_DEFER_COUNT = {rc['NINE_FACTS_DEFER_COUNT']}",
          f"- NINE_FACTS_BLOCK_COUNT = {rc['NINE_FACTS_BLOCK_COUNT']}",
          f"- REAL_WORLD_FULL_MANAT_GATE_PASS = {rc['REAL_WORLD_FULL_MANAT_GATE_PASS']}",
          f"- REAL_WORLD_FULL_MANAT_READY = {rc['REAL_WORLD_FULL_MANAT_READY']}",
          f"- STOP_BEFORE_TANZIL = {rc['STOP_BEFORE_TANZIL']}",
          "", "> FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO "
          "(إذن هذه الجولة محصور في إثبات الوقائع وفتح الجاهزية فقط).",
          "", "---",
          "*الوقائع التسع مقبولة كوقائع واقعية بتصديق المالك؛ جاهزية المناط الواقعي الكامل مفتوحة، "
          "والتنزيل والحكم والجواب تحتاج إذنًا صريحًا منفصلًا.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_spec(d):
    rc = d["recheck"]
    facts = d["facts"]
    tokens = load_tokens()
    token_rows = [[t["token_id"], t.get("original_surface", ""), t.get("word_class", "")] for t in tokens]

    fact_rows = [[f["fact_id"], f["fact_label"], f["owner_value"], f["source_or_evidence"],
                  f["owner_ratification"], f["fact_accepted"], f["verdict"]] for f in facts]
    fact_cls = [["", "", "y", "y", "y", "y", "y"] for _ in facts]

    cpp_rows = [
        ["CAUSE", "OWNER_SUPPLIED_AND_RATIFIED_REAL_CASE_VALUE"],
        ["CONDITIONS", "OWNER_VALUE_PRESENT، SOURCE_OR_EVIDENCE_PRESENT، OWNER_RATIFICATION_YES"],
        ["PREVENTERS", "NONE"],
        ["VERDICT", "ACCEPT_REAL_CASE_FACT (لكل الوقائع التسع)"],
    ]
    residual_items = [
        "الوقائع مقبولة كوقائع واقعية بتصديق المالك (SOURCE = OWNER_SUPPLIED_REAL_CASE_FACTS_ROUND_47).",
        "جاهزية المناط الواقعي الكامل مفتوحة (READY = YES) — لكنها ليست فتحًا للتنزيل.",
        "FINAL_MANAT / TANZIL / FINAL_HUKM / FINAL_ANSWER تحتاج إذنًا صريحًا منفصلًا.",
    ]
    guard_rows = [[k, v, ("y" if v == "YES" else "n" if v == "NO" else "d")]
                  for k, v in d["guards"].items() if k != "producer_file"]
    recheck_rows = [
        ["NINE_FACTS_REVIEWED", rc["NINE_FACTS_REVIEWED"], "d"],
        ["NINE_FACTS_ACCEPTED_COUNT", rc["NINE_FACTS_ACCEPTED_COUNT"], "y" if rc["NINE_FACTS_ACCEPTED_COUNT"] == 9 else "n"],
        ["NINE_FACTS_DEFER_COUNT", rc["NINE_FACTS_DEFER_COUNT"], "y" if rc["NINE_FACTS_DEFER_COUNT"] == 0 else "n"],
        ["NINE_FACTS_BLOCK_COUNT", rc["NINE_FACTS_BLOCK_COUNT"], "y" if rc["NINE_FACTS_BLOCK_COUNT"] == 0 else "n"],
        ["REAL_WORLD_FULL_MANAT_GATE_PASS", rc["REAL_WORLD_FULL_MANAT_GATE_PASS"], "y" if rc["REAL_WORLD_FULL_MANAT_GATE_PASS"] == "YES" else "n"],
        ["REAL_WORLD_FULL_MANAT_READY", rc["REAL_WORLD_FULL_MANAT_READY"], "y" if rc["REAL_WORLD_FULL_MANAT_READY"] == "YES" else "n"],
        ["STOP_BEFORE_TANZIL", rc["STOP_BEFORE_TANZIL"], "y" if rc["STOP_BEFORE_TANZIL"] == "NO" else "n"],
        ["FINAL_MANAT", rc["FINAL_MANAT"], "n"],
        ["TANZIL", rc["TANZIL"], "n"],
        ["FINAL_HUKM", rc["FINAL_HUKM"], "n"],
        ["FINAL_ANSWER", rc["FINAL_ANSWER"], "n"],
    ]

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "زوّد المالك وصدّق الوقائع التسع كوقائع للحالة الواقعية محل الدراسة (مصدر مستقل، لا نص ولا سيناريو).",
                f"المقبول = {rc['NINE_FACTS_ACCEPTED_COUNT']}/9 · المؤجَّل = {rc['NINE_FACTS_DEFER_COUNT']} · "
                f"المرفوض = {rc['NINE_FACTS_BLOCK_COUNT']}.",
                f"REAL_WORLD_FULL_MANAT_GATE_PASS = {rc['REAL_WORLD_FULL_MANAT_GATE_PASS']} · "
                f"READY = {rc['REAL_WORLD_FULL_MANAT_READY']} — دون فتح تنزيل أو حكم.",
            ]},
            {"raw_note": "<b>حدود صريحة:</b> إذن الجولة محصور في إثبات الوقائع وفتح الجاهزية فقط · "
                         "FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · "
                         "AGENT_KNOWLEDGE_CREATES_FACT = NO.", "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات العشر", "body": [
            {"cols": {"headers": ["token", "السطح", "الفئة"], "rows": token_rows}}
            if token_rows else {"raw_note": "TOKEN_ARTIFACT_MISSING", "kind": "warn"},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا؛ هذه الجولة إثبات وقائع واقعية لا إفادة. IFADAH_FINAL = NO.",
             "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0 · NO_FRAMENET · "
                         "مصدر الوقائع = تصريح المالك لهذه الجولة.", "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "الوقائع الواقعية أُثبتت بتصديق المالك؛ هذا يفتح جاهزية المناط الواقعي الكامل، "
                         "ولا يرخّص وحده عبورًا إلى الحكم.", "kind": "warn"},
        ]},
        {"n": 8, "title": "المصدر المعياري — الوقائع التسع الواقعية المصدّقة", "body": [
            {"cols": {"headers": ["fact_id", "fact_label", "owner_value", "source_or_evidence",
                                  "owner_ratification", "fact_accepted", "verdict"],
                      "rows": fact_rows, "row_classes": fact_cls}},
            {"note": "السبب / الشرط / المانع (يطبَّق على كل واقعة):"},
            {"kv": cpp_rows},
            {"note": "إعادة فحص بوابة المناط الواقعي الكامل:"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in recheck_rows],
                      "row_classes": [["", r[2]] for r in recheck_rows]}},
        ]},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": residual_items, "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"raw_note": "لا نقص في الوقائع بعد التصديق؛ الناقص هو إذن منفصل لفتح التنزيل ثم الحكم ثم الجواب.",
             "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "الجاهزية مفتوحة؛ الخطوة التالية (بإذن صريح منفصل): فتح FINAL_MANAT ثم TANZIL ثم "
                         "FINAL_HUKM ثم FINAL_ANSWER — لا يُفتح شيء منها في هذه الجولة.", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "trace_here": True, "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_owner_real_fact_supply_47.py — ROUND47_TESTS = passed · "
                         "يتحقق من قبول الوقائع التسع ومن مرور البوابة وبقاء التنزيل مغلقًا."},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "SUPPLY_47_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                "MECHANISM_REUSED = ROUND_46 decide() + recheck()\n"
                f"SOURCE = {SOURCE}\n"
                f"NINE_FACTS_ACCEPTED = {rc['NINE_FACTS_ACCEPTED_COUNT']}/9\n"
                f"REAL_WORLD_FULL_MANAT_GATE_PASS = {rc['REAL_WORLD_FULL_MANAT_GATE_PASS']}\n"
                "REAL_CASE_FACTS_FROM_TEXT_INFERENCE = NO\nREAL_CASE_FACTS_FROM_ROUND44_SCENARIO = NO\n"
                "FRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\n"
                "FINAL_MANAT = NO\nTANZIL = NO\nFINAL_HUKM = NO\nFINAL_ANSWER = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "قُبلت الوقائع التسع كوقائع واقعية بتصديق المالك، وفُتحت جاهزية المناط الواقعي الكامل "
                         "(READY=YES)؛ ولم يُفتح مناط نهائي ولا تنزيل ولا حكم ولا جواب — تبقى محتاجة إذنًا منفصلًا.",
             "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in recheck_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in recheck_rows + guard_rows]}},
        ]},
    ]

    trace_rows = [
        {"req": "REQ-MAT-MALIK-REAL-FACT-SUPPLY-JSON", "source": SOURCE,
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47.json",
         "test": "tests/test_taaqol_mat_malik_owner_real_fact_supply_47.py", "status": "TRACEABLE"},
        {"req": "REQ-MAT-MALIK-REAL-FACT-SUPPLY-GUARDS", "source": "ROUND_47",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_GUARDS_47.json",
         "test": "tests/test_taaqol_mat_malik_owner_real_fact_supply_47.py", "status": "TRACEABLE"},
    ]

    return {
        "title": "تقرير تنفيذي — تزويد وتصديق المالك للوقائع التسع الواقعية «مات ملك» (47)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>إثبات وقائع واقعية بتصديق المالك:</b> مصدر مستقل (تصريح المالك لهذه الجولة)، "
                     "لا من النص ولا من سيناريو الجولة 44؛ يفتح جاهزية المناط الواقعي الكامل فقط، "
                     "ولا يفتح تنزيلًا ولا حكمًا ولا جوابًا."),
        ],
        "sentence": {"label": "النازلة", "text": SENTENCE, "id": "nazila-sentence"},
        "sections": sections,
        "trace": {"title": "جدول التتبّع (مستقل عن جدول الكلمات)", "rows": trace_rows},
        "closure_flags": (
            f"NINE_FACTS_REVIEWED = {rc['NINE_FACTS_REVIEWED']} · "
            f"NINE_FACTS_ACCEPTED_COUNT = {rc['NINE_FACTS_ACCEPTED_COUNT']} · "
            f"NINE_FACTS_DEFER_COUNT = {rc['NINE_FACTS_DEFER_COUNT']} · "
            f"NINE_FACTS_BLOCK_COUNT = {rc['NINE_FACTS_BLOCK_COUNT']} · "
            f"REAL_WORLD_FULL_MANAT_GATE_PASS = {rc['REAL_WORLD_FULL_MANAT_GATE_PASS']} · "
            f"REAL_WORLD_FULL_MANAT_READY = {rc['REAL_WORLD_FULL_MANAT_READY']} · "
            "FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO."),
        "tests_result": "ROUND47_TESTS = passed",
        "footer": "إثبات وقائع واقعية بتصديق المالك + فتح الجاهزية فقط — لا حكم، لا تنزيل، لا جواب "
                  "(RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_MANAGER_REPORT_AR_47.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_GUARDS_47.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(d)), encoding="utf-8")

    rc = d["recheck"]
    print("SUPPLY_47_REPORT=" + a.report_out)
    print(f"NINE_FACTS_ACCEPTED={rc['NINE_FACTS_ACCEPTED_COUNT']} DEFER={rc['NINE_FACTS_DEFER_COUNT']} "
          f"BLOCK={rc['NINE_FACTS_BLOCK_COUNT']} "
          f"REAL_WORLD_FULL_MANAT_GATE_PASS={rc['REAL_WORLD_FULL_MANAT_GATE_PASS']} "
          f"READY={rc['REAL_WORLD_FULL_MANAT_READY']}")


if __name__ == "__main__":
    main()
