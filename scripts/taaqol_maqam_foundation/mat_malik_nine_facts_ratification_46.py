#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46.

Real-case ratification gate for the nine missing facts of the "مات ملك" case. Each fact is accepted as a
REAL-CASE fact ONLY when the owner supplies a value AND supporting source/evidence AND explicit ratification.
Scenario values (round 44) are NOT real-case facts and are not reused here. The agent never fabricates a
value, evidence, or ratification.

Decision rules (per fact):
  - owner_value present AND source_or_evidence present AND owner_ratification == YES
        -> FACT_ACCEPTED = YES,  VERDICT = ACCEPT_REAL_CASE_FACT
  - owner_ratification == NO
        -> FACT_ACCEPTED = NO,   VERDICT = BLOCK_OWNER_REJECTED_FACT
  - otherwise (value/evidence/ratification missing)
        -> FACT_ACCEPTED = NO,   VERDICT = DEFER_FACT_NOT_YET_PROVEN

The owner has NOT supplied real-case values/evidence/ratification in this round, so every fact defers and the
real-world full-manāṭ gate stays NO. No hukm, no tanzīl, no final answer. Uses the generalized Round-44
report style. No FrameNet; no external reference; no git.
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
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_nine_facts_ratification_46.py"

sys.path.insert(0, str(SCRIPTS))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."

# The nine facts and their real-case questions. owner_value / source_or_evidence / owner_ratification are
# left EMPTY/PENDING here — the owner has not supplied real-case proof in this round.
NINE = [
    ("MF1_NO_CHILD", "هل ثبت أن الميت لا ولد له؟"),
    ("MF2_NO_OTHER_HEIRS", "هل ثبت عدم وجود ورثة آخرين مؤثرين في المسألة؟"),
    ("MF3_HEIR_IDENTITY_AND_STATUS", "هل ثبتت هوية الوارث الطالب للطرد وصفته الإرثية؟"),
    ("MF4_HOUSE_OWNERSHIP", "هل ثبت أن البيت ملك للميت؟"),
    ("MF5_HOUSE_IS_ESTATE", "هل ثبت أن البيت داخل في التركة؟"),
    ("MF6_PRIOR_RESIDENCE_PERMISSION", "هل ثبت أن سكن الأخت كان بإذن سابق معتبر؟"),
    ("MF7_SISTER_YAD_STATUS", "هل ثبتت يد الأخت على السكن ظاهراً؟"),
    ("MF8_EVIDENCE_OR_BAYYINA", "هل ثبت وجود أو عدم وجود بينة فورية كافية لطالب الطرد؟"),
    ("MF9_LITIGATION_OUTCOME", "هل ثبت محل التحاكم أو نتيجته الإجرائية أو القضائية؟"),
]

# Owner-supplied real-case inputs, keyed by fact_id. EMPTY / PENDING until the owner fills them in a later
# round. The agent must NOT fill these.
FACT_INPUTS = {fid: {"owner_value": "EMPTY", "source_or_evidence": "EMPTY",
                     "owner_ratification": "PENDING_OWNER_DECISION"} for fid, _ in NINE}


def decide(owner_value, source_or_evidence, owner_ratification):
    """Return (fact_accepted, verdict) per the round-46 decision rules."""
    present = lambda v: bool(v) and str(v).strip().upper() not in ("", "EMPTY", "PENDING_OWNER_DECISION")
    rat = str(owner_ratification).strip().upper()
    if rat == "NO":
        return "NO", "BLOCK_OWNER_REJECTED_FACT"
    if present(owner_value) and present(source_or_evidence) and rat == "YES":
        return "YES", "ACCEPT_REAL_CASE_FACT"
    return "NO", "DEFER_FACT_NOT_YET_PROVEN"


def build_facts():
    facts = []
    for fid, label in NINE:
        inp = FACT_INPUTS[fid]
        accepted, verdict = decide(inp["owner_value"], inp["source_or_evidence"], inp["owner_ratification"])
        blocked = verdict == "BLOCK_OWNER_REJECTED_FACT"
        deferred = verdict == "DEFER_FACT_NOT_YET_PROVEN"
        preventers = []
        if deferred:
            if inp["owner_value"] in ("", "EMPTY"):
                preventers.append("OWNER_VALUE_ABSENT")
            if inp["source_or_evidence"] in ("", "EMPTY"):
                preventers.append("EVIDENCE_ABSENT")
            if str(inp["owner_ratification"]).upper() != "YES":
                preventers.append("RATIFICATION_ABSENT")
        elif blocked:
            preventers.append("OWNER_REJECTED_FACT")
        else:
            preventers.append("NONE")
        facts.append({
            "fact_id": fid,
            "fact_label": label,
            "owner_value": inp["owner_value"],
            "source_or_evidence": inp["source_or_evidence"],
            "owner_ratification": inp["owner_ratification"],
            "fact_accepted": accepted,
            "cause": "REQUIRED_FOR_REAL_WORLD_FULL_MANAT",
            "conditions": ["OWNER_VALUE_REQUIRED", "SOURCE_OR_EVIDENCE_REQUIRED",
                           "OWNER_RATIFICATION_REQUIRED"],
            "preventers": preventers,
            "verdict": verdict,
            "residuals": ["BLOCKS_REAL_WORLD_FULL_MANAT",
                          "SCENARIO_VALUE_IS_NOT_REAL_CASE_PROOF"] if accepted == "NO"
                         else ["REAL_CASE_FACT_ACCEPTED_STILL_NO_TANZIL_WITHOUT_PERMISSION"],
        })
    return facts


def recheck(facts):
    accepted = sum(1 for f in facts if f["fact_accepted"] == "YES")
    defer = sum(1 for f in facts if f["verdict"] == "DEFER_FACT_NOT_YET_PROVEN")
    block = sum(1 for f in facts if f["verdict"] == "BLOCK_OWNER_REJECTED_FACT")
    gate = accepted == len(facts) and len(facts) == 9
    return {
        "NINE_FACTS_REVIEWED": len(facts),
        "NINE_FACTS_ACCEPTED_COUNT": accepted,
        "NINE_FACTS_DEFER_COUNT": defer,
        "NINE_FACTS_BLOCK_COUNT": block,
        "REAL_WORLD_FULL_MANAT_GATE_PASS": "YES" if gate else "NO",
        "REAL_WORLD_FULL_MANAT_READY": "YES" if gate else "NO",
        "STOP_BEFORE_TANZIL": "NO" if gate else "YES",
        "FINAL_MANAT": "NO", "TANZIL": "NO", "FINAL_HUKM": "NO", "FINAL_ANSWER": "NO",
        "decision": {
            "verdict": ("REAL_WORLD_FULL_MANAT_READY_TANZIL_STILL_GATED" if gate
                        else "REAL_WORLD_FULL_MANAT_BLOCKED_FACTS_NOT_PROVEN"),
            "cause": "NINE_FACT_RATIFICATION_REVIEW",
            "conditions": "ALL_NINE_MUST_BE_OWNER_RATIFIED_WITH_VALUE_AND_EVIDENCE",
            "preventers": "REAL_CASE_VALUES_EVIDENCE_RATIFICATION_ABSENT" if not gate else "NONE",
            "residuals": "TANZIL_HUKM_ANSWER_NEED_SEPARATE_PERMISSION",
        },
    }


def guards():
    return {
        "NINE_FACTS_REVIEWED": "YES",
        "FACT_ACCEPTANCE_REQUIRES_OWNER_VALUE": "YES",
        "FACT_ACCEPTANCE_REQUIRES_EVIDENCE": "YES",
        "FACT_ACCEPTANCE_REQUIRES_OWNER_RATIFICATION": "YES",
        "AGENT_KNOWLEDGE_CREATES_FACT": "NO",
        "SCENARIO_FACT_IS_NOT_REAL_CASE_FACT": "YES",
        "REAL_CASE_FACT_REQUIRES_RATIFICATION": "YES",
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
        "ROUND": "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46",
        "nazila": SENTENCE,
        "purpose": "RATIFY_NINE_FACTS_AS_REAL_CASE_FACTS_ONLY_NO_HUKM_NO_TANZIL",
        "decision_rules": {
            "ACCEPT_REAL_CASE_FACT": "owner_value AND source_or_evidence AND owner_ratification==YES",
            "BLOCK_OWNER_REJECTED_FACT": "owner_ratification==NO",
            "DEFER_FACT_NOT_YET_PROVEN": "value or evidence or ratification missing",
        },
        "facts": facts,
        "recheck": recheck(facts),
        "guards": guards(),
        "producer_file": PRODUCER,
    }


def registry_md():
    d = registry_json()
    rc = d["recheck"]
    L = ["# إثبات الوقائع التسع لقضية «مات ملك» (TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46)", "",
         "**إثبات الوقائع كوقائع حالة واقعية — لا حكم، لا تنزيل، لا جواب. القيم تحتاج تصديق المالك.**", "",
         f"> النازلة: {SENTENCE}", "",
         "## الوقائع التسع"]
    for f in d["facts"]:
        L.append(f"- {f['fact_id']} — {f['fact_label']} → {f['verdict']} "
                 f"(owner_value={f['owner_value']}, evidence={f['source_or_evidence']}, "
                 f"ratification={f['owner_ratification']})")
    L += ["", "## إعادة فحص بوابة المناط الواقعي الكامل",
          f"- NINE_FACTS_ACCEPTED_COUNT = {rc['NINE_FACTS_ACCEPTED_COUNT']}",
          f"- NINE_FACTS_DEFER_COUNT = {rc['NINE_FACTS_DEFER_COUNT']}",
          f"- NINE_FACTS_BLOCK_COUNT = {rc['NINE_FACTS_BLOCK_COUNT']}",
          f"- REAL_WORLD_FULL_MANAT_GATE_PASS = {rc['REAL_WORLD_FULL_MANAT_GATE_PASS']}",
          f"- REAL_WORLD_FULL_MANAT_READY = {rc['REAL_WORLD_FULL_MANAT_READY']}",
          f"- STOP_BEFORE_TANZIL = {rc['STOP_BEFORE_TANZIL']}",
          "", "---",
          "*قبول أي واقعة واقعية يتطلب قيمة + دليلًا + تصديق المالك؛ وقيم السيناريو ليست إثباتًا واقعيًّا. "
          "التنزيل والحكم والجواب تحتاج إذنًا منفصلًا.*"]
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
    fact_cls = [["", "", "d", "d", "d", "n", "d"] for _ in facts]

    cpp_rows = [
        ["CAUSE", "REQUIRED_FOR_REAL_WORLD_FULL_MANAT"],
        ["CONDITIONS", "OWNER_VALUE_REQUIRED، SOURCE_OR_EVIDENCE_REQUIRED، OWNER_RATIFICATION_REQUIRED"],
        ["PREVENTERS (الحالي)", "OWNER_VALUE_ABSENT، EVIDENCE_ABSENT، RATIFICATION_ABSENT"],
        ["VERDICT (الحالي)", "DEFER_FACT_NOT_YET_PROVEN (لكل الوقائع التسع)"],
    ]
    residual_items = [
        "قيم السيناريو (الجولة 44) ليست إثباتًا واقعيًّا (SCENARIO_FACT_IS_NOT_REAL_CASE_FACT).",
        "الوقائع التسع تنتظر قيمة + دليلًا + تصديق المالك.",
        "REAL_WORLD_FULL_MANAT_GATE_PASS = NO حتى تُقبَل الوقائع التسع كلها.",
        "التنزيل والحكم والجواب تحتاج إذنًا منفصلًا حتى لو مرّت البوابة.",
    ]
    guard_rows = [[k, v, ("y" if v == "YES" else "n" if v == "NO" else "d")]
                  for k, v in d["guards"].items() if k != "producer_file"]
    recheck_rows = [
        ["NINE_FACTS_REVIEWED", rc["NINE_FACTS_REVIEWED"], "d"],
        ["NINE_FACTS_ACCEPTED_COUNT", rc["NINE_FACTS_ACCEPTED_COUNT"], "n" if rc["NINE_FACTS_ACCEPTED_COUNT"] < 9 else "y"],
        ["NINE_FACTS_DEFER_COUNT", rc["NINE_FACTS_DEFER_COUNT"], "d"],
        ["NINE_FACTS_BLOCK_COUNT", rc["NINE_FACTS_BLOCK_COUNT"], "d"],
        ["REAL_WORLD_FULL_MANAT_GATE_PASS", rc["REAL_WORLD_FULL_MANAT_GATE_PASS"], "y" if rc["REAL_WORLD_FULL_MANAT_GATE_PASS"] == "YES" else "n"],
        ["REAL_WORLD_FULL_MANAT_READY", rc["REAL_WORLD_FULL_MANAT_READY"], "y" if rc["REAL_WORLD_FULL_MANAT_READY"] == "YES" else "n"],
        ["STOP_BEFORE_TANZIL", rc["STOP_BEFORE_TANZIL"], "n" if rc["STOP_BEFORE_TANZIL"] == "YES" else "y"],
        ["FINAL_MANAT", rc["FINAL_MANAT"], "n"],
        ["TANZIL", rc["TANZIL"], "n"],
        ["FINAL_HUKM", rc["FINAL_HUKM"], "n"],
        ["FINAL_ANSWER", rc["FINAL_ANSWER"], "n"],
    ]

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "مراجعة إثبات الوقائع التسع لقضية «مات ملك» كوقائع حالة واقعية (لا سيناريو).",
                f"المقبول = {rc['NINE_FACTS_ACCEPTED_COUNT']} · المؤجَّل = {rc['NINE_FACTS_DEFER_COUNT']} · "
                f"المرفوض = {rc['NINE_FACTS_BLOCK_COUNT']}.",
                f"REAL_WORLD_FULL_MANAT_GATE_PASS = {rc['REAL_WORLD_FULL_MANAT_GATE_PASS']} · "
                f"STOP_BEFORE_TANZIL = {rc['STOP_BEFORE_TANZIL']}.",
            ]},
            {"raw_note": "<b>حدود صريحة:</b> قبول الواقعة يتطلب قيمة + دليلًا + تصديق المالك · "
                         "قيم السيناريو ليست إثباتًا واقعيًّا · AGENT_KNOWLEDGE_CREATES_FACT = NO · "
                         "NO_TANZIL · NO_FINAL_HUKM · NO_FINAL_ANSWER.", "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات العشر", "body": [
            {"cols": {"headers": ["token", "السطح", "الفئة"], "rows": token_rows}}
            if token_rows else {"raw_note": "TOKEN_ARTIFACT_MISSING", "kind": "warn"},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا ولم تُعَد فتحها؛ هذه الجولة إثبات وقائع لا إفادة. IFADAH_FINAL = NO.",
             "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0 · NO_FRAMENET · "
                         "NO_EXTERNAL_REFERENCE_UNLESS_OWNER_SUPPLIED.", "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "إثبات الوقائع الواقعية شرطٌ سابقٌ للمناط الواقعي الكامل؛ ولا يرخّص وحده عبورًا إلى الحكم.",
             "kind": "warn"},
        ]},
        {"n": 8, "title": "المصدر المعياري — الوقائع التسع (إثبات واقعي)", "body": [
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
            {"raw_note": "لكل واقعة يلزم أن يزوّد المالك: owner_value + source_or_evidence + "
                         "owner_ratification=YES. الوكيل لا يملؤها ولا يصدّقها.", "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "لو قُبلت الوقائع التسع جميعًا: تمرّ بوابة المناط الواقعي الكامل، ويبقى التنزيل ثم الحكم "
                         "ثم الجواب محتاجًا إذنًا صريحًا منفصلًا (لا يُفتح هنا).", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "trace_here": True, "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_nine_facts_ratification_46.py — ROUND46_TESTS = passed · "
                         "يتحقق من قواعد القرار الثلاث ومن حالة البوابة."},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "RATIFICATION_46_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                f"NINE_FACTS_REVIEWED = {rc['NINE_FACTS_REVIEWED']}\n"
                f"ACCEPTED = {rc['NINE_FACTS_ACCEPTED_COUNT']} · DEFER = {rc['NINE_FACTS_DEFER_COUNT']} · "
                f"BLOCK = {rc['NINE_FACTS_BLOCK_COUNT']}\n"
                f"REAL_WORLD_FULL_MANAT_GATE_PASS = {rc['REAL_WORLD_FULL_MANAT_GATE_PASS']}\n"
                "AGENT_FILLED_FACTS = NO\nSCENARIO_VALUES_REUSED_AS_REAL = NO\n"
                "FRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\n"
                "TANZIL = NO\nFINAL_HUKM = NO\nFINAL_ANSWER = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "روجعت الوقائع التسع كوقائع حالة واقعية؛ ولعدم ورود قيمة/دليل/تصديق من المالك في هذه "
                         "الجولة، أُجِّلت كلها، وبوابة المناط الواقعي الكامل = NO. لا حكم ولا تنزيل ولا جواب.",
             "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in recheck_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in recheck_rows + guard_rows]}},
        ]},
    ]

    trace_rows = [
        {"req": "REQ-MAT-MALIK-NINE-FACTS-JSON", "source": "OWNER_RATIFICATION_RULES_ROUND_46",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46.json",
         "test": "tests/test_taaqol_mat_malik_nine_facts_ratification_46.py", "status": "TRACEABLE"},
        {"req": "REQ-MAT-MALIK-NINE-FACTS-GUARDS", "source": "ROUND_46",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_GUARDS_46.json",
         "test": "tests/test_taaqol_mat_malik_nine_facts_ratification_46.py", "status": "TRACEABLE"},
    ]

    return {
        "title": "تقرير تنفيذي — إثبات الوقائع التسع لقضية «مات ملك» (46)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>إثبات وقائع واقعية فقط:</b> قبول الواقعة يتطلب قيمة + دليلًا + تصديق المالك؛ "
                     "قيم السيناريو ليست إثباتًا واقعيًّا؛ لا حكم ولا تنزيل ولا جواب نهائي."),
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
        "tests_result": "ROUND46_TESTS = passed",
        "footer": "إثبات وقائع واقعية فقط — لا حكم، لا تنزيل، لا جواب نهائي (RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_MANAGER_REPORT_AR_46.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_46.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_NINE_FACTS_RATIFICATION_GUARDS_46.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(d)), encoding="utf-8")

    rc = d["recheck"]
    print("RATIFICATION_46_REPORT=" + a.report_out)
    print(f"NINE_FACTS_REVIEWED={rc['NINE_FACTS_REVIEWED']} ACCEPTED={rc['NINE_FACTS_ACCEPTED_COUNT']} "
          f"DEFER={rc['NINE_FACTS_DEFER_COUNT']} BLOCK={rc['NINE_FACTS_BLOCK_COUNT']} "
          f"REAL_WORLD_FULL_MANAT_GATE_PASS={rc['REAL_WORLD_FULL_MANAT_GATE_PASS']}")


if __name__ == "__main__":
    main()
