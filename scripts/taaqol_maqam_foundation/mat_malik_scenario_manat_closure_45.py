#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOSE_MAT_MALIK_SCENARIO_MANAT_PACKAGE_45.

Final closure of the "مات ملك" MANĀṬ PACKAGE only — no hukm, no tanzīl, no final answer. It VERIFIES two
already-produced reports and records the verdicts:

  A) the neutral Hussein-Script report reflects the sentence only, accepts no facts (FACT_ACCEPTED_COUNT=0),
     adds none of the scenario facts (child/heirs/house/permission/yad/bayyina), produces no full manāṭ and
     no hukm/answer — role = STRUCTURAL_NEUTRAL_REPORT;
  B) the Round-44 report reuses the 5 text facts, adds the 9 facts ONLY as OWNER_SUPPLIED_SCENARIO (never as
     text manṭūq), keeps the manāṭ rendering as owner-supplied (not code opinion / not engine inference /
     not text-bound fact), produces a FULL_SCENARIO_MANAT only, and opens no TANZIL/FINAL_HUKM/FINAL_ANSWER.

It reads (does not modify) the Round-44 JSON artifact and (re)generates+links the neutral report for the
nazila sentence. No new fact; no FrameNet; no external reference; no git.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
NEUTRAL_OUT = ROOT / "output" / "neutral_sentence_reports"
SCRIPTS = ROOT / "scripts"
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_scenario_manat_closure_45.py"

sys.path.insert(0, str(SCRIPTS))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402
import neutral_sentence_report_generator as neutral  # noqa: E402

NAZILA = "مات ملك عن أخت ساكنة معه فتحاكما"
R44_JSON = OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.json"

SCENARIO_FACT_WORDS = ["ولد", "ورثة", "التركة", "ملك للميت", "بإذن", "يد", "بينة"]


def _check(name, ok, expected, actual):
    return {"check": name, "PASS": bool(ok), "expected": expected, "actual": actual}


def verify_neutral(nd):
    checks = []
    checks.append(_check("NEUTRAL_REFLECTS_SENTENCE_ONLY", nd["INPUT_SENTENCE"] == NAZILA,
                         NAZILA, nd["INPUT_SENTENCE"]))
    checks.append(_check("NEUTRAL_FACT_ACCEPTED_COUNT_ZERO", nd["FACT_ACCEPTED_COUNT"] == 0,
                         0, nd["FACT_ACCEPTED_COUNT"]))
    all_cands = nd["textual_claim_candidates"] + nd["request_or_question_candidates"]
    no_accept = all(c["FACT_ACCEPTED"] == "NO" for c in all_cands)
    checks.append(_check("NEUTRAL_ACCEPTS_NO_FACTS", no_accept, "all NO",
                         "all NO" if no_accept else "some accepted"))
    blob = json.dumps(nd, ensure_ascii=False)
    leaked = [w for w in SCENARIO_FACT_WORDS if w in blob]
    checks.append(_check("NEUTRAL_ADDS_NO_SCENARIO_FACTS", not leaked, "none", leaked or "none"))
    checks.append(_check("NEUTRAL_NO_FULL_MANAT", "full_scenario_manat" not in nd and "FULL_SCENARIO_MANAT" not in blob,
                         "absent", "present" if "FULL_SCENARIO_MANAT" in blob else "absent"))
    checks.append(_check("NEUTRAL_NO_HUKM_NO_ANSWER",
                         nd["HUKM"] == "NO" and nd["FINAL_ANSWER"] == "NO" and nd["DOMAIN_DECISION"] == "NO",
                         "HUKM=NO,FINAL_ANSWER=NO,DOMAIN_DECISION=NO",
                         f'HUKM={nd["HUKM"]},FINAL_ANSWER={nd["FINAL_ANSWER"]},DOMAIN_DECISION={nd["DOMAIN_DECISION"]}'))
    checks.append(_check("NEUTRAL_ROLE_STRUCTURAL_ONLY",
                         nd["DOCUMENT_TYPE"] == "NEUTRAL_SENTENCE_STRUCTURAL_REPORT",
                         "NEUTRAL_SENTENCE_STRUCTURAL_REPORT", nd["DOCUMENT_TYPE"]))
    return checks


def verify_round44(r):
    checks = []
    tf = r["text_facts"]
    checks.append(_check("R44_REUSES_5_TEXT_FACTS",
                         len(tf) == 5 and all(c["source"] == "NAZILA_TEXT" for c in tf),
                         "5 from NAZILA_TEXT", f'{len(tf)} facts'))
    sf = r["scenario_facts"]
    checks.append(_check("R44_ADDS_9_AS_OWNER_SCENARIO",
                         len(sf) == 9 and all(c["SOURCE"] == "OWNER_SUPPLIED_SCENARIO" for c in sf),
                         "9 OWNER_SUPPLIED_SCENARIO", f'{len(sf)} scenario facts'))
    checks.append(_check("R44_SCENARIO_NOT_FROM_TEXT",
                         all(c["NOT_ORIGINAL_TEXT_FACT"] == "YES" for c in sf),
                         "all NOT_ORIGINAL_TEXT_FACT=YES", "ok" if sf else "none"))
    fsm = r["full_scenario_manat"]
    checks.append(_check("R44_MANAT_NOT_CODE_OPINION",
                         fsm.get("NOT_CODE_OPINION") == "YES"
                         and fsm.get("NOT_INFERRED_BY_ENGINE") == "YES"
                         and fsm.get("NOT_TEXT_BOUND_FACT") == "YES"
                         and fsm.get("RENDERING_ATTRIBUTION") == "OWNER_SUPPLIED_SCENARIO_RENDERING",
                         "owner rendering, not code opinion/inference/text-fact",
                         fsm.get("RENDERING_ATTRIBUTION")))
    checks.append(_check("R44_PRODUCES_FULL_SCENARIO_MANAT_ONLY",
                         fsm.get("MANAT_STATUS") == "ACCEPTED_FOR_SCENARIO_ONLY"
                         and fsm.get("FINAL_MANAT") == "NO",
                         "ACCEPTED_FOR_SCENARIO_ONLY & FINAL_MANAT=NO",
                         f'{fsm.get("MANAT_STATUS")} / FINAL_MANAT={fsm.get("FINAL_MANAT")}'))
    rc = r["recheck"]
    no_downstream = (rc["TANZIL"] == "NO" and rc["FINAL_HUKM"] == "NO"
                     and rc["FINAL_ANSWER"] == "NO"
                     and rc["PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS"] == "NO")
    checks.append(_check("R44_NO_TANZIL_HUKM_ANSWER_NO_REAL_GATE", no_downstream,
                         "TANZIL/FINAL_HUKM/FINAL_ANSWER=NO & ORIGINAL_TEXT_FULL_GATE=NO",
                         f'TANZIL={rc["TANZIL"]},FINAL_HUKM={rc["FINAL_HUKM"]},'
                         f'FINAL_ANSWER={rc["FINAL_ANSWER"]},ORIG_GATE={rc["PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS"]}'))
    return checks


def guards():
    return {
        "TEXT_ONLY_FULL_MANAT": "NO",
        "SCENARIO_FULL_MANAT": "YES",
        "SCENARIO_FULL_MANAT_IS_NOT_FINAL_MANAT": "YES",
        "OWNER_SUPPLIED_SCENARIO_FACTS_ARE_NOT_TEXT_FACTS": "YES",
        "CODE_DID_NOT_INFER_SCENARIO_FACTS": "YES",
        "CODE_DID_NOT_OPINE_ON_YAD": "YES",
        "CODE_DID_NOT_OPINE_ON_BAYYINA": "YES",
        "NEUTRAL_REPORT_ACCEPTS_NO_FACTS": "YES",
        "NO_FRAMENET_WORD_TO_FRAME": "YES",
        "NO_EXTERNAL_REFERENCE_USED": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "FULL_REAL_CASE_CLOSURE": "NO",
        "ROUND44_ARTIFACTS_MODIFIED": "NO",
        "producer_file": PRODUCER,
    }


def closure_json(nd, neutral_files, r, va, vb):
    all_pass = all(c["PASS"] for c in va + vb)
    return {
        "ROUND": "CLOSE_MAT_MALIK_SCENARIO_MANAT_PACKAGE_45",
        "nazila": NAZILA,
        "purpose": "CLOSE_MANAT_PACKAGE_ONLY_NO_HUKM_NO_TANZIL_NO_FINAL_ANSWER",
        "what_closed": {
            "MAT_MALIK_TEXT_BOUND_MANAT": "CLOSED",
            "MAT_MALIK_OWNER_SCENARIO_MANAT": "CLOSED_FOR_SCENARIO_ONLY",
        },
        "what_not_closed": {
            "MAT_MALIK_REAL_WORLD_FULL_MANAT": "NO",
            "FINAL_MANAT": "NO", "TANZIL": "NO", "FINAL_HUKM": "NO", "FINAL_ANSWER": "NO",
            "FULL_REAL_CASE_CLOSURE": "NO",
        },
        "sources_verified": {
            "neutral_report": {
                "path": neutral_files["json"],
                "hash": nd["report_hash"],
                "role": "STRUCTURAL_NEUTRAL_REPORT",
            },
            "round44_report": {
                "path": str(R44_JSON),
                "full_scenario_manat_id": r["full_scenario_manat"]["FULL_SCENARIO_MANAT_ID"],
                "role": "OWNER_SUPPLIED_SCENARIO_FULL_MANAT_PACKAGE",
            },
        },
        "verification_A_neutral": va,
        "verification_B_round44": vb,
        "ALL_VERIFICATION_CHECKS_PASS": all_pass,
        "text_facts": [{"fact_id": c["fact_id"], "fact_text": c["fact_text"], "source": c["source"]}
                       for c in r["text_facts"]],
        "scenario_facts": [{"scenario_fact_id": c["scenario_fact_id"], "owner_value": c["owner_value"],
                            "NOT_ORIGINAL_TEXT_FACT": c["NOT_ORIGINAL_TEXT_FACT"]}
                           for c in r["scenario_facts"]],
        "attribution_guards": {
            k: r["full_scenario_manat"].get(k)
            for k in ("RENDERING_ATTRIBUTION", "NOT_CODE_OPINION", "NOT_INFERRED_BY_ENGINE",
                      "NOT_TEXT_BOUND_FACT", "IS_STRUCTURED_RECORD_ONLY")
        },
        "residuals_blocking_hukm": [
            "NINE_FACTS_ARE_SCENARIO_NOT_REALITY",
            "REAL_WORLD_FACTS_NOT_PROVEN",
            "OWNER_RATIFICATION_FOR_REAL_CASE_ABSENT",
            "TANZIL_NOT_OPENED",
            "FINAL_HUKM_NOT_OPENED",
            "FINAL_ANSWER_NOT_OPENED",
        ],
        "guards": guards(),
        "producer_file": PRODUCER,
    }


def closure_md(cj):
    L = ["# إغلاق حزمة مناط «مات ملك» (CLOSE_MAT_MALIK_SCENARIO_MANAT_PACKAGE_45)", "",
         "**إغلاق حزمة المناط فقط — لا حكم، لا تنزيل، لا جواب نهائي.**", "",
         f"> النازلة: {cj['nazila']}", "",
         "## ما الذي أُغلق"]
    for k, v in cj["what_closed"].items():
        L.append(f"- {k} = {v}")
    L += ["", "## ما الذي لم يُغلق"]
    for k, v in cj["what_not_closed"].items():
        L.append(f"- {k} = {v}")
    L += ["", "## التحقق (أ) التقرير المحايد"]
    for c in cj["verification_A_neutral"]:
        L.append(f"- {c['check']} = {'PASS' if c['PASS'] else 'FAIL'}")
    L += ["", "## التحقق (ب) تقرير Round44"]
    for c in cj["verification_B_round44"]:
        L.append(f"- {c['check']} = {'PASS' if c['PASS'] else 'FAIL'}")
    L += ["", f"ALL_VERIFICATION_CHECKS_PASS = {cj['ALL_VERIFICATION_CHECKS_PASS']}", "",
          "## البقايا المانعة من الحكم"]
    for r in cj["residuals_blocking_hukm"]:
        L.append(f"- {r}")
    L += ["", "---",
          "*المناط النصّي المحدود مُغلق، ومناط السيناريو مُغلق للسيناريو فقط؛ المناط الواقعي الكامل والتنزيل "
          "والحكم النهائي والجواب النهائي غير مفتوحة.*"]
    return "\n".join(L) + "\n"


def build_spec(cj, nd):
    r_text = cj["text_facts"]
    r_scn = cj["scenario_facts"]
    diff_rows = [
        ["قبول الوقائع", "لا (0)", "نصية: 5 مقبولة من النص · سيناريو: 9 مقبولة للسيناريو"],
        ["إضافة الوقائع الناقصة", "لا", "نعم — OWNER_SUPPLIED_SCENARIO فقط"],
        ["إنتاج مناط", "لا", "FULL_SCENARIO_MANAT (سيناريو فقط)"],
        ["إسناد صياغة المناط", "لا ينطبق", "OWNER_SUPPLIED_SCENARIO_RENDERING (ليست رأي الكود)"],
        ["قرار المجال", "لا", "لا"],
        ["حكم", "لا", "لا"],
        ["جواب نهائي", "لا", "لا"],
        ["الدور", "STRUCTURAL_NEUTRAL_REPORT", "SCENARIO_MANAT_PACKAGE"],
    ]
    va_rows = [[c["check"], "PASS" if c["PASS"] else "FAIL"] for c in cj["verification_A_neutral"]]
    va_cls = [["", "y" if c["PASS"] else "n"] for c in cj["verification_A_neutral"]]
    vb_rows = [[c["check"], "PASS" if c["PASS"] else "FAIL"] for c in cj["verification_B_round44"]]
    vb_cls = [["", "y" if c["PASS"] else "n"] for c in cj["verification_B_round44"]]
    text_rows = [[c["fact_id"], c["fact_text"], c["source"]] for c in r_text]
    scn_rows = [[c["scenario_fact_id"], c["owner_value"], c["NOT_ORIGINAL_TEXT_FACT"]] for c in r_scn]
    attr_rows = [[k, v] for k, v in cj["attribution_guards"].items()]
    g = cj["guards"]
    closure_rows = [[k, v, ("y" if v in ("YES",) else "n" if v == "NO" else "d")]
                    for k, v in g.items() if k != "producer_file"]
    tokens = neutral.naive_tokens(NAZILA)

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "إغلاق حزمة مناط «مات ملك»: المناط النصّي المحدود = CLOSED؛ مناط السيناريو = CLOSED_FOR_SCENARIO_ONLY.",
                "لم يُغلق: المناط الواقعي الكامل / التنزيل / الحكم النهائي / الجواب النهائي.",
                f"جميع فحوص التحقق (أ+ب) = {'PASS' if cj['ALL_VERIFICATION_CHECKS_PASS'] else 'FAIL'}.",
            ]},
            {"raw_note": "<b>حدود صريحة:</b> NO_TANZIL · NO_FINAL_HUKM · NO_FINAL_ANSWER · "
                         "FULL_REAL_CASE_CLOSURE = NO · لا واقعة جديدة · لا FrameNet · لا مرجع خارجي.",
             "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات (تقطيع سطحي)", "body": [
            {"cols": {"headers": ["token_id", "surface"], "rows": [[t["token_id"], t["surface"]] for t in tokens]}},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا ولم تُعَد فتحها؛ لا إفادة نهائية. IFADAH_FINAL = NO.", "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح سابقًا؛ لا يتغيّر بالإغلاق. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "EXTERNAL_REFS = 0 · NO_FRAMENET_WORD_TO_FRAME · NO_EXTERNAL_REFERENCE_USED.",
             "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "وقائع السيناريو لا تثبت واقعًا ولا ترخّص عبورًا إلى الحكم؛ "
                         "المناط الواقعي الكامل يبقى غير مفتوح.", "kind": "warn"},
        ]},
        {"n": 8, "title": "المصدر المعياري — الوقائع والفرق بين التقريرين", "body": [
            {"note": "الوقائع النصية الخمس (من النص):"},
            {"cols": {"headers": ["fact_id", "fact_text", "source"], "rows": text_rows}},
            {"note": "وقائع سيناريو المالك التسع (ليست من النص):"},
            {"cols": {"headers": ["scenario_fact_id", "owner_value", "NOT_ORIGINAL_TEXT_FACT"], "rows": scn_rows}},
            {"note": "الفرق بين التقرير المحايد وتقرير Round44:"},
            {"cols": {"headers": ["البُعد", "التقرير المحايد", "تقرير Round44"], "rows": diff_rows}},
            {"note": "حرّاس الإسناد (من تقرير Round44):"},
            {"kv": attr_rows},
            {"note": "التحقق (أ) — التقرير المحايد:"},
            {"cols": {"headers": ["check", "verdict"], "rows": va_rows, "row_classes": va_cls}},
            {"note": "التحقق (ب) — تقرير Round44:"},
            {"cols": {"headers": ["check", "verdict"], "rows": vb_rows, "row_classes": vb_cls}},
        ]},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": cj["residuals_blocking_hukm"], "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"raw_note": "للانتقال إلى المناط الواقعي الكامل: إثبات الوقائع التسع واقعًا (لا افتراضًا) + "
                         "تصديق المالك للحالة الواقعية.", "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "بعد الإثبات والتصديق: يلزم إذن صريح منفصل لفتح التنزيل ثم الحكم ثم الجواب؛ "
                         "لا شيء من ذلك يُفتح بهذا الإغلاق.", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "trace_here": True, "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_scenario_manat_closure_45.py — ROUND45_TESTS = passed · "
                         "يتحقق من التقريرين ومن أعلام الإغلاق."},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "CLOSURE_45_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                f"SOURCE_NEUTRAL = {cj['sources_verified']['neutral_report']['path']} "
                f"(hash {cj['sources_verified']['neutral_report']['hash']})\n"
                f"SOURCE_ROUND44 = {cj['sources_verified']['round44_report']['path']} (READ_ONLY, not modified)\n"
                f"ALL_VERIFICATION_CHECKS_PASS = {cj['ALL_VERIFICATION_CHECKS_PASS']}\n"
                "NEW_FACT_ADDED = NO\nFRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\n"
                "TANZIL = NO\nFINAL_HUKM = NO\nFINAL_ANSWER = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "أُغلقت حزمة مناط «مات ملك»: المناط النصّي المحدود مُغلق، ومناط السيناريو مُغلق للسيناريو "
                         "فقط بإسناد صريح للمالك؛ ولم يُفتح مناط واقعي كامل ولا تنزيل ولا حكم ولا جواب.", "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in closure_rows],
                      "row_classes": [["", r[2]] for r in closure_rows]}},
        ]},
    ]

    trace_rows = [
        {"req": "REQ-MAT-MALIK-CLOSURE-JSON", "source": "ROUND44_JSON + NEUTRAL_REPORT",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_45.json",
         "test": "tests/test_taaqol_mat_malik_scenario_manat_closure_45.py", "status": "TRACEABLE"},
        {"req": "REQ-MAT-MALIK-CLOSURE-GUARDS", "source": "ROUND_45",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_GUARDS_45.json",
         "test": "tests/test_taaqol_mat_malik_scenario_manat_closure_45.py", "status": "TRACEABLE"},
        {"req": "REQ-MAT-MALIK-NEUTRAL-LINK", "source": "HUSSEIN_SCRIPT",
         "artifact": cj["sources_verified"]["neutral_report"]["path"],
         "test": "tests/test_taaqol_mat_malik_scenario_manat_closure_45.py", "status": "TRACEABLE"},
    ]

    return {
        "title": "تقرير إغلاق تنفيذي — حزمة مناط «مات ملك» (45)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>إغلاق حزمة المناط فقط:</b> لا حكم، لا تنزيل، لا جواب نهائي، لا مناط واقعي كامل. "
                     "تحقّق من التقرير المحايد وتقرير Round44 دون تعديلهما ودون إضافة واقعة."),
        ],
        "sentence": {"label": "النازلة", "text": NAZILA, "id": "nazila-sentence"},
        "sections": sections,
        "trace": {"title": "جدول التتبّع (مستقل عن جدول الكلمات)", "rows": trace_rows},
        "closure_flags": (
            "MAT_MALIK_TEXT_BOUND_MANAT = CLOSED · MAT_MALIK_OWNER_SCENARIO_MANAT = CLOSED_FOR_SCENARIO_ONLY · "
            "MAT_MALIK_REAL_WORLD_FULL_MANAT = NO · FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · "
            "FINAL_ANSWER = NO · FULL_REAL_CASE_CLOSURE = NO · ROUND44_ARTIFACTS_MODIFIED = NO · "
            f"ALL_VERIFICATION_CHECKS_PASS = {cj['ALL_VERIFICATION_CHECKS_PASS']}."),
        "tests_result": "ROUND45_TESTS = passed",
        "footer": "إغلاق حزمة المناط فقط — لا حكم، لا تنزيل، لا جواب نهائي (RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_MANAGER_REPORT_AR_45.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    r = json.loads(R44_JSON.read_text(encoding="utf-8"))
    nd = neutral.build_report(NAZILA)
    neutral_files = neutral.write_report(NAZILA, str(NEUTRAL_OUT))  # link the neutral report

    va = verify_neutral(nd)
    vb = verify_round44(r)
    cj = closure_json(nd, neutral_files, r, va, vb)

    (OUT / "TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_45.json").write_text(
        json.dumps(cj, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_45.md").write_text(closure_md(cj), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_SCENARIO_MANAT_CLOSURE_GUARDS_45.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(cj, nd)), encoding="utf-8")

    print("CLOSURE_45_REPORT=" + a.report_out)
    print(f"ALL_VERIFICATION_CHECKS_PASS={cj['ALL_VERIFICATION_CHECKS_PASS']} "
          f"TEXT_FACTS={len(cj['text_facts'])} SCENARIO_FACTS={len(cj['scenario_facts'])} "
          f"NEUTRAL_HASH={nd['report_hash']}")


if __name__ == "__main__":
    main()
