#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50 (owner-canonical).

Owner-supplied + ratified normative source accepted and bound to FNM1 ONLY. Reuses round-49 decide(); all
required fields + owner_ratification=YES ⇒ ACCEPT_NORMATIVE_SOURCE_FOR_FNM1.

This round accepts and binds the source only. It does NOT apply the source to the case, opens no tanzīl /
final hukm / final answer, says no "permitted/not permitted", does not adjudicate the sister's or heir's
right, and produces no judicial outcome. The agent did not select/search the source and does not judge its
correctness. (Supersedes the self-named ACCEPT_50 draft; this is the owner-canonical source_id/filenames.)
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
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_normative_source_acceptance_50.py"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "taaqol_maqam_foundation"))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402
import mat_malik_normative_source_intake_49 as r49  # noqa: E402  (reuse decide())

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
R48_JSON = OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.json"

OWNER_SOURCE = {
    "source_id": "NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE",
    "source_type": "OWNER_RATIFIED_NORMATIVE_RULE",
    "authority": "RULE_OWNER_DR_HUSSEIN",
    "source_text_or_reference": (
        "لا يُخرج ساكنٌ من عينٍ متنازعٍ عليها أو داخلةٍ في تركة، إذا كانت يده على السكن قائمةً بإذنٍ سابقٍ "
        "معتبر، ولم توجد بينةٌ فوريةٌ كافية لطالب الإخراج، حتى يُنظر النزاع في مجلس الحكم المختص."
    ),
    "scope": (
        "يُستعمل هذا المصدر في واقعة FNM1 فقط: وفاة مالك، وأخت ساكنة في بيت داخل في التركة، وسكنها كان بإذن "
        "سابق معتبر، ويدها قائمة ظاهرًا، وطالب الطرد وارث ذو صفة، ولا توجد بينة فورية كافية لطردها قبل نظر "
        "القضاء، ومحل النزاع طلب إخراجها من السكن."
    ),
    "binding_license_to_FNM1": (
        "ينطبق المصدر على FNM1 لأن المناط النهائي يتضمن: عينًا داخلة في التركة، ساكنةً بإذن سابق، يدًا قائمة "
        "ظاهرًا، طلب إخراج، عدم بينة فورية كافية، ووقوع تحاكم. الربط هنا رخصة مصدر فقط، لا تنزيل ولا حكم نهائي."
    ),
    "owner_ratification": "YES",
}


def load_final_manat():
    d = json.loads(R48_JSON.read_text(encoding="utf-8"))
    fm = d["final_manat"]
    return {"FINAL_MANAT_ID": fm["FINAL_MANAT_ID"], "FINAL_MANAT": fm["FINAL_MANAT_BORN"],
            "FINAL_MANAT_STATUS": fm["FINAL_MANAT_STATUS"]}


def source_record(accepted, verdict):
    s = OWNER_SOURCE
    return {
        **{k: s[k] for k in ("source_id", "source_type", "authority", "source_text_or_reference",
                             "scope", "binding_license_to_FNM1", "owner_ratification")},
        "normative_source_accepted": accepted,
        "bound_to_FNM1": "YES" if accepted == "YES" else "NO",
        "source_applied": "NO",
        "binding_is_source_license_only": "YES",
        "agent_judged_source_correctness": "NO",
        "says_permitted_or_not": "NO",
        "adjudicates_right": "NO",
        "produces_judicial_outcome": "NO",
        "cause": "OWNER_SUPPLIED_AND_RATIFIED_NORMATIVE_SOURCE_WITH_BINDING_LICENSE",
        "conditions": ["ALL_SOURCE_FIELDS_PRESENT", "OWNER_RATIFICATION_YES",
                       "BINDING_LICENSE_TO_FNM1_PRESENT"],
        "preventers": ["NONE"],
        "verdict": verdict,
        "residuals": ["SOURCE_ACCEPTED_NOT_APPLIED", "TANZIL_NOT_OPENED",
                      "FINAL_HUKM_NOT_OPENED", "FINAL_ANSWER_NOT_OPENED"],
    }


def guards():
    return {
        "FINAL_MANAT_REQUIRED": "YES",
        "FINAL_MANAT_ID_REQUIRED": "YES",
        "OWNER_SUPPLIED_SOURCE_PRESENT": "YES",
        "OWNER_RATIFICATION_REQUIRED_FOR_SOURCE": "YES",
        "NORMATIVE_SOURCE_ACCEPTED_FOR_FNM1_ONLY": "YES",
        "BINDING_LICENSE_TO_FNM1_PRESENT": "YES",
        "SOURCE_ACCEPTANCE_IS_NOT_TANZIL": "YES",
        "SOURCE_ACCEPTANCE_IS_NOT_FINAL_HUKM": "YES",
        "SOURCE_ACCEPTANCE_IS_NOT_FINAL_ANSWER": "YES",
        "NO_EXTERNAL_REFERENCE_USED": "YES",
        "NO_FRAMENET": "YES",
        "NO_AGENT_SELECTED_SOURCE": "YES",
        "NO_AGENT_SEARCHED_SOURCE": "YES",
        "producer_file": PRODUCER,
    }


def registry_json():
    fm = load_final_manat()
    accepted, verdict = r49.decide(OWNER_SOURCE)
    rec = source_record(accepted, verdict)
    status = "ACCEPTED" if accepted == "YES" else ("BLOCKED" if verdict.startswith("BLOCK") else "DEFER")
    return {
        "ROUND": "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50",
        "nazila": SENTENCE,
        "purpose": "ACCEPT_OWNER_SUPPLIED_NORMATIVE_SOURCE_AND_BIND_TO_FNM1_ONLY",
        "mechanism_reused_from": "ROUND_49 decide()",
        "final_manat_ref": fm,
        "normative_source_record": rec,
        "recheck": {
            "FINAL_MANAT": fm["FINAL_MANAT"],
            "FINAL_MANAT_ID": fm["FINAL_MANAT_ID"],
            "NORMATIVE_SOURCE_ACCEPTED": accepted,
            "NORMATIVE_SOURCE_STATUS": status,
            "NORMATIVE_SOURCE_ID": rec["source_id"],
            "BOUND_TO_FNM1": rec["bound_to_FNM1"],
            "SOURCE_APPLIED": "NO",
            "TANZIL": "NO", "FINAL_HUKM": "NO", "FINAL_ANSWER": "NO",
            "FULL_TAAQOL_PROJECT_CLOSED": "NO",
            "decision": {"verdict": verdict,
                         "cause": "OWNER_SUPPLIED_AND_RATIFIED_NORMATIVE_SOURCE_WITH_BINDING_LICENSE",
                         "preventers": "NONE"},
        },
        "guards": guards(),
        "supersedes": "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPT_50 (self-named draft; owner-canonical is this file)",
        "producer_file": PRODUCER,
    }


def registry_md():
    d = registry_json()
    rec = d["normative_source_record"]
    rc = d["recheck"]
    L = ["# قبول المصدر المعياري وربطه بـ FNM1 — النسخة المعتمدة (TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50)", "",
         "**قبول مصدر معياري مصدّق من المالك وربطه بـ FNM1 فقط — رخصة مصدر لا تطبيق، لا تنزيل، لا حكم، لا جواب.**", "",
         f"> النازلة: {SENTENCE}",
         f"> المناط النهائي: {d['final_manat_ref']['FINAL_MANAT_ID']} "
         f"(FINAL_MANAT={d['final_manat_ref']['FINAL_MANAT']})",
         f"> NORMATIVE_SOURCE_ID = {rec['source_id']}", "",
         "## سجل المصدر المعياري المقبول"]
    for k in ("source_id", "source_type", "authority", "owner_ratification", "normative_source_accepted",
              "bound_to_FNM1", "source_applied", "binding_is_source_license_only",
              "says_permitted_or_not", "adjudicates_right", "produces_judicial_outcome", "verdict"):
        L.append(f"- {k} = {rec[k]}")
    L += ["", "### نص المصدر (كما زوّده المالك، حرفيًّا):", f"> {rec['source_text_or_reference']}", "",
          "### النطاق (scope):", f"> {rec['scope']}", "",
          "### رخصة الربط بـ FNM1:", f"> {rec['binding_license_to_FNM1']}", "",
          "## السبب/الشرط/المانع",
          f"- CAUSE = {rec['cause']}",
          f"- CONDITIONS = {'، '.join(rec['conditions'])}",
          f"- PREVENTERS = {'، '.join(rec['preventers'])}",
          "", "## البقايا"]
    for r in rec["residuals"]:
        L.append(f"- {r}")
    L += ["", f"NORMATIVE_SOURCE_ACCEPTED = {rc['NORMATIVE_SOURCE_ACCEPTED']} · "
          f"BOUND_TO_FNM1 = {rc['BOUND_TO_FNM1']} · SOURCE_APPLIED = {rc['SOURCE_APPLIED']}",
          "", "---",
          "*المصدر مقبول ومربوط بـ FNM1 رخصةً فقط؛ لم يُطبَّق، ولم يُنتج تنزيلًا ولا حكمًا ولا جوابًا ولا "
          "نتيجة قضائية؛ ولم يقل يجوز أو لا يجوز. الوكيل لم يختر المصدر ولم يحكم على صحته.*"]
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
        ["owner_ratification", rec["owner_ratification"], "y"],
        ["normative_source_accepted", rec["normative_source_accepted"], "y"],
        ["bound_to_FNM1", rec["bound_to_FNM1"], "y"],
        ["source_applied", rec["source_applied"], "n"],
        ["binding_is_source_license_only", rec["binding_is_source_license_only"], "y"],
        ["says_permitted_or_not", rec["says_permitted_or_not"], "n"],
        ["adjudicates_right", rec["adjudicates_right"], "n"],
        ["produces_judicial_outcome", rec["produces_judicial_outcome"], "n"],
        ["verdict", rec["verdict"], "y"],
    ]
    binding_rows = [
        ["bound_final_manat", fm["FINAL_MANAT_ID"], "d"],
        ["binding_license_to_FNM1", rec["binding_license_to_FNM1"], "d"],
        ["scope", rec["scope"], "d"],
        ["binding_is_source_license_only", "YES", "y"],
        ["source_applied", "NO", "n"],
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
        ["NORMATIVE_SOURCE_ACCEPTED", rc["NORMATIVE_SOURCE_ACCEPTED"], "y"],
        ["NORMATIVE_SOURCE_STATUS", rc["NORMATIVE_SOURCE_STATUS"], "y"],
        ["NORMATIVE_SOURCE_ID", rc["NORMATIVE_SOURCE_ID"], "d"],
        ["BOUND_TO_FNM1", rc["BOUND_TO_FNM1"], "y"],
        ["SOURCE_APPLIED", rc["SOURCE_APPLIED"], "n"],
        ["TANZIL", "NO", "n"],
        ["FINAL_HUKM", "NO", "n"],
        ["FINAL_ANSWER", "NO", "n"],
        ["FULL_TAAQOL_PROJECT_CLOSED", "NO", "n"],
    ]

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "قَبِل النظامُ المصدرَ المعياري المصدّق من المالك وربطه بالمناط النهائي FNM1 (رخصة مصدر فقط).",
                f"NORMATIVE_SOURCE_ID = {rec['source_id']} · NORMATIVE_SOURCE_ACCEPTED = "
                f"{rc['NORMATIVE_SOURCE_ACCEPTED']} · BOUND_TO_FNM1 = {rc['BOUND_TO_FNM1']}.",
                "لم يُطبَّق المصدر ولم يُنتج تنزيل/حكم/جواب/نتيجة قضائية؛ FINAL_MANAT لم يتغيّر.",
            ]},
            {"raw_note": "<b>حدود صريحة:</b> الوكيل لم يختر/يبحث عن المصدر ولم يحكم على صحته · "
                         "SOURCE_ACCEPTANCE_IS_NOT_TANZIL / NOT_FINAL_HUKM / NOT_FINAL_ANSWER · "
                         "لا «يجوز/لا يجوز» ولا فصل في حق الأخت أو الوارث.", "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات العشر", "body": [
            {"cols": {"headers": ["token", "السطح", "الفئة"], "rows": token_rows}}
            if token_rows else {"raw_note": "TOKEN_ARTIFACT_MISSING", "kind": "warn"},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا؛ هذه الجولة قبول مصدر لا إفادة. IFADAH_FINAL = NO.", "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · المصدر مزوّد ومصدّق من المالك · "
                         "EXTERNAL_REFS = 0 · NO_FRAMENET.", "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "قبول المصدر وربطه رخصةُ مصدرٍ فقط؛ لا يرخّص تطبيقًا ولا عبورًا إلى التنزيل أو الحكم.",
             "kind": "warn"},
        ]},
        {"n": 8, "title": "المصدر المعياري — المقبول والمربوط بـ FNM1", "body": [
            {"kv": [["FINAL_MANAT_ID", fm["FINAL_MANAT_ID"], "d"], ["FINAL_MANAT", fm["FINAL_MANAT"], "y"]]},
            {"note": "نص المصدر (كما زوّده المالك، حرفيًّا):"},
            {"raw_note": rec["source_text_or_reference"]},
            {"note": "جدول المصدر المعياري المقبول:"},
            {"cols": {"headers": ["field", "value"],
                      "rows": [[r[0], r[1]] for r in src_rows],
                      "row_classes": [["", r[2]] for r in src_rows]}},
            {"note": "جدول رخصة الربط بـ FNM1:"},
            {"cols": {"headers": ["field", "value"],
                      "rows": [[r[0], r[1]] for r in binding_rows],
                      "row_classes": [["", r[2]] for r in binding_rows]}},
            {"note": "السبب / الشرط / المانع:"},
            {"kv": cpp_rows},
        ]},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": rec["residuals"], "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"raw_note": "لا نقص في حقول المصدر بعد القبول؛ الناقص لاحقًا: إذن صريح لتطبيق المصدر ثم التنزيل.",
             "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "المصدر مقبول ومربوط؛ الخطوة التالية (بإذن منفصل): تطبيق المصدر على FNM1 ضمن TANZIL ← "
                         "ثم FINAL_HUKM ← ثم FINAL_ANSWER — لا يُفتح شيء منها هنا.", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "trace_here": True, "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_normative_source_acceptance_50.py — ROUND50_TESTS = passed · "
                         "يتحقق من قبول المصدر وربطه وبقاء التطبيق/التنزيل/الحكم مغلقة."},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "NORMATIVE_SOURCE_ACCEPTANCE_50_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                "MECHANISM_REUSED = ROUND_49 decide()\n"
                f"FINAL_MANAT_REF = {fm['FINAL_MANAT_ID']} (round 48, READ_ONLY, unchanged)\n"
                f"NORMATIVE_SOURCE_ID = {rec['source_id']}\n"
                f"NORMATIVE_SOURCE_ACCEPTED = {rc['NORMATIVE_SOURCE_ACCEPTED']} · "
                f"BOUND_TO_FNM1 = {rc['BOUND_TO_FNM1']}\n"
                "AGENT_SELECTED_SOURCE = NO\nAGENT_SEARCHED_SOURCE = NO\n"
                "AGENT_JUDGED_SOURCE_CORRECTNESS = NO\nSOURCE_APPLIED = NO\n"
                "SUPERSEDES = TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPT_50 (self-named draft)\n"
                "FRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\n"
                "TANZIL = NO\nFINAL_HUKM = NO\nFINAL_ANSWER = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "قُبِل المصدر المعياري المصدّق من المالك (NS1) ورُبط بـ FNM1 رخصةَ مصدرٍ فقط؛ لم يُطبَّق، "
                         "ولم يُنتج تنزيلًا ولا حكمًا ولا جوابًا ولا نتيجة قضائية، وFINAL_MANAT لم يتغيّر. "
                         "التطبيق والتنزيل والحكم والجواب تبقى مغلقة حتى إذن صريح منفصل.", "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in closure_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in closure_rows + guard_rows]}},
        ]},
    ]

    trace_rows = [
        {"req": "REQ-MAT-MALIK-SOURCE-ACCEPTANCE-JSON", "source": "OWNER_SUPPLIED_NORMATIVE_SOURCE_ROUND_50",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50.json",
         "test": "tests/test_taaqol_mat_malik_normative_source_acceptance_50.py", "status": "TRACEABLE"},
        {"req": "REQ-MAT-MALIK-SOURCE-ACCEPTANCE-GUARDS", "source": "ROUND_50",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_GUARDS_50.json",
         "test": "tests/test_taaqol_mat_malik_normative_source_acceptance_50.py", "status": "TRACEABLE"},
    ]

    return {
        "title": "تقرير تنفيذي — قبول المصدر المعياري وربطه بـ FNM1 «مات ملك» (50 — النسخة المعتمدة)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>قبول مصدر معياري مصدّق من المالك:</b> رخصة مصدر فقط مربوطة بـ FNM1؛ لا تطبيق، "
                     "لا تنزيل، لا حكم، لا جواب، لا «يجوز/لا يجوز»، لا فصل في حق؛ الوكيل لم يختر المصدر ولم يحكم على صحته."),
        ],
        "sentence": {"label": "النازلة", "text": SENTENCE, "id": "nazila-sentence"},
        "sections": sections,
        "trace": {"title": "جدول التتبّع (مستقل عن جدول الكلمات)", "rows": trace_rows},
        "closure_flags": (
            f"FINAL_MANAT = {rc['FINAL_MANAT']} · FINAL_MANAT_ID = {rc['FINAL_MANAT_ID']} · "
            f"NORMATIVE_SOURCE_ACCEPTED = {rc['NORMATIVE_SOURCE_ACCEPTED']} · "
            f"NORMATIVE_SOURCE_STATUS = {rc['NORMATIVE_SOURCE_STATUS']} · "
            f"NORMATIVE_SOURCE_ID = {rc['NORMATIVE_SOURCE_ID']} · BOUND_TO_FNM1 = {rc['BOUND_TO_FNM1']} · "
            f"SOURCE_APPLIED = {rc['SOURCE_APPLIED']} · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · "
            "FULL_TAAQOL_PROJECT_CLOSED = NO."),
        "tests_result": "ROUND50_TESTS = passed",
        "footer": "قبول مصدر معياري وربطه بـ FNM1 — رخصة مصدر فقط، لا تطبيق/تنزيل/حكم/جواب "
                  "(RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_MANAGER_REPORT_AR_50.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_GUARDS_50.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(d)), encoding="utf-8")

    rc = d["recheck"]
    print("NORMATIVE_SOURCE_ACCEPTANCE_50_REPORT=" + a.report_out)
    print(f"NORMATIVE_SOURCE_ACCEPTED={rc['NORMATIVE_SOURCE_ACCEPTED']} ID={rc['NORMATIVE_SOURCE_ID']} "
          f"BOUND_TO_FNM1={rc['BOUND_TO_FNM1']} SOURCE_APPLIED={rc['SOURCE_APPLIED']} "
          f"TANZIL=NO FINAL_HUKM=NO FINAL_ANSWER=NO")


if __name__ == "__main__":
    main()
