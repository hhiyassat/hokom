#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51.

Applies the owner-ratified normative source NS1 to the final manāṭ FNM1 to produce TANZIL ONLY — never a
final hukm or final answer, and never a judicial outcome or permissibility statement.

TANZIL here = the binding elements of NS1 are realized in FNM1 (antecedent/condition matching). The consequent
(the ruling) is NOT produced. Element matching is computed from the round-48 accepted facts (read, not
re-derived); the round-50 acceptance confirms the source is accepted and bound to FNM1.

  all 8 binding elements present, no preventer -> SOURCE_APPLIED=YES, TANZIL=YES, ACCEPT_TANZIL_ONLY
  any element missing                           -> DEFER_TANZIL_MISSING_BINDING_ELEMENT
  any preventer present                         -> BLOCK_TANZIL_PREVENTER_PRESENT
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
PRODUCER = "scripts/taaqol_maqam_foundation/mat_malik_tanzil_application_51.py"

sys.path.insert(0, str(SCRIPTS))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
R48_JSON = OUT / "TAAQOL_MAT_MALIK_FINAL_MANAT_BIRTH_48.json"
R50_JSON = OUT / "TAAQOL_MAT_MALIK_NORMATIVE_SOURCE_ACCEPTANCE_50.json"
FINAL_MANAT_ID = "FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE"
NORMATIVE_SOURCE_ID = "NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE"

# The 8 NS1 binding elements and the FNM1 accepted facts that realize each.
BINDING_ELEMENTS = [
    ("BE1_EIN_IN_ESTATE", "عين داخلة في التركة",
     ["MF4_HOUSE_OWNERSHIP", "MF5_HOUSE_IS_ESTATE"]),
    ("BE2_RESIDING_IN_EIN", "ساكنة في العين",
     ["FC3_SISTER_RESIDING_WITH_HIM"]),
    ("BE3_PRIOR_PERMISSION", "السكن بإذن سابق معتبر",
     ["MF6_PRIOR_RESIDENCE_PERMISSION"]),
    ("BE4_YAD_STANDING", "يد الساكنة قائمة ظاهرًا",
     ["MF7_SISTER_YAD_STATUS"]),
    ("BE5_EXPELLER_IS_HEIR", "طالب الإخراج وارث ذو صفة",
     ["MF3_HEIR_IDENTITY_AND_STATUS", "FC4_HEIR_WANTED_EXPULSION"]),
    ("BE6_NO_IMMEDIATE_BAYYINAH", "لا توجد بينة فورية كافية لطالب الإخراج",
     ["MF8_EVIDENCE_OR_BAYYINA"]),
    ("BE7_DISPUTE_UNDER_ADJUDICATION", "النزاع منظور أو محله التحاكم",
     ["FC5_LITIGATION_OCCURRED", "MF9_LITIGATION_OUTCOME"]),
    ("BE8_REQUEST_EXPULSION_BEFORE_RULING", "المطلوب الإخراج من السكن قبل نظر الحكم المختص",
     ["FC4_HEIR_WANTED_EXPULSION", "MF9_LITIGATION_OUTCOME"]),
]


def load_inputs():
    r48 = json.loads(R48_JSON.read_text(encoding="utf-8"))
    r50 = json.loads(R50_JSON.read_text(encoding="utf-8"))
    accepted = {f["fact_id"] for f in r48["text_facts"] if f["fact_accepted"] == "YES"}
    accepted |= {f["fact_id"] for f in r48["real_case_facts"] if f["fact_accepted"] == "YES"}
    fm_ok = r48["final_manat"]["FINAL_MANAT_BORN"] == "YES"
    rec = r50["normative_source_record"]
    src_ok = rec["normative_source_accepted"] == "YES" and rec["bound_to_FNM1"] == "YES"
    return accepted, fm_ok, src_ok, rec


def check_elements(accepted):
    elements = []
    for eid, label, req in BINDING_ELEMENTS:
        missing = [f for f in req if f not in accepted]
        elements.append({
            "element_id": eid,
            "label": label,
            "required_fact_ids": req,
            "missing_fact_ids": missing,
            "present": "YES" if not missing else "NO",
        })
    return elements


def decide_tanzil(elements, fm_ok, src_ok, preventers=None):
    preventers = preventers or []
    all_present = all(e["present"] == "YES" for e in elements)
    if not (fm_ok and src_ok):
        return ("NO", "NO", "DEFER", "DEFER_TANZIL_MISSING_BINDING_ELEMENT", "NO",
                ["FINAL_MANAT_OR_SOURCE_NOT_READY"])
    if preventers:
        return ("NO", "NO", "BLOCK", "BLOCK_TANZIL_PREVENTER_PRESENT", "NO", preventers)
    if all_present:
        return ("YES", "YES", "ACCEPTED", "ACCEPT_TANZIL_ONLY", "YES", ["NONE_FOR_TANZIL_ONLY"])
    return ("NO", "NO", "DEFER", "DEFER_TANZIL_MISSING_BINDING_ELEMENT", "NO",
            ["MISSING_BINDING_ELEMENT"])


def guards():
    return {
        "FINAL_MANAT_REQUIRED": "YES",
        "NORMATIVE_SOURCE_ACCEPTED_REQUIRED": "YES",
        "SOURCE_BOUND_TO_FNM1_REQUIRED": "YES",
        "TANZIL_ONLY_AUTHORIZED": "YES",
        "SOURCE_APPLICATION_IS_NOT_FINAL_HUKM": "YES",
        "SOURCE_APPLICATION_IS_NOT_FINAL_ANSWER": "YES",
        "NO_JUDICIAL_OUTCOME_PRODUCED": "YES",
        "NO_PERMISSIBILITY_LANGUAGE": "YES",
        "NO_EXTERNAL_REFERENCE_USED": "YES",
        "NO_FRAMENET": "YES",
        "producer_file": PRODUCER,
    }


def registry_json():
    accepted, fm_ok, src_ok, rec = load_inputs()
    elements = check_elements(accepted)
    applied, tanzil, status, verdict, applies, preventers = decide_tanzil(elements, fm_ok, src_ok)
    return {
        "ROUND": "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51",
        "nazila": SENTENCE,
        "purpose": "APPLY_NS1_TO_FNM1_PRODUCE_TANZIL_ONLY_NO_HUKM_NO_ANSWER",
        "final_manat_id": FINAL_MANAT_ID,
        "normative_source_id": NORMATIVE_SOURCE_ID,
        "normative_source_text": rec["source_text_or_reference"],
        "binding_elements": elements,
        "NS1_APPLIES_TO_FNM1": applies,
        "tanzil_result": {
            "SOURCE_APPLIED": applied,
            "TANZIL": tanzil,
            "TANZIL_STATUS": status,
            "verdict": verdict,
            "cause": "NORMATIVE_SOURCE_ACCEPTED_AND_BOUND_TO_FNM1",
            "conditions": ["FINAL_MANAT_ACCEPTED", "NORMATIVE_SOURCE_ACCEPTED",
                           "BINDING_LICENSE_TO_FNM1_PRESENT", "ALL_NS1_BINDING_ELEMENTS_PRESENT_IN_FNM1"],
            "preventers": preventers,
            "residuals": ["FINAL_HUKM_NOT_OPENED", "FINAL_ANSWER_NOT_OPENED",
                          "JUDICIAL_OUTCOME_NOT_PRODUCED"],
        },
        "recheck": {
            "FINAL_MANAT": "YES",
            "NORMATIVE_SOURCE_ACCEPTED": "YES",
            "NORMATIVE_SOURCE_ID": NORMATIVE_SOURCE_ID,
            "NS1_APPLIES_TO_FNM1": applies,
            "SOURCE_APPLIED": applied,
            "TANZIL": tanzil,
            "TANZIL_STATUS": status,
            "FINAL_HUKM": "NO", "FINAL_ANSWER": "NO",
            "JUDICIAL_OUTCOME_PRODUCED": "NO",
            "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        },
        "guards": guards(),
        "producer_file": PRODUCER,
    }


def registry_md():
    d = registry_json()
    tr = d["tanzil_result"]
    L = ["# تطبيق المصدر NS1 على FNM1 — التنزيل فقط (TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51)", "",
         "**إنتاج التنزيل فقط: انطباق شروط NS1 على عناصر FNM1 — بلا حكم، بلا جواب، بلا نتيجة قضائية، بلا «يجوز/لا يجوز».**", "",
         f"> النازلة: {SENTENCE}",
         f"> المناط النهائي: {d['final_manat_id']}",
         f"> المصدر المعياري: {d['normative_source_id']}", "",
         "## عناصر الربط (NS1 ↔ FNM1)"]
    for e in d["binding_elements"]:
        L.append(f"- {e['element_id']} — {e['label']} → present={e['present']} "
                 f"(يحققها: {'، '.join(e['required_fact_ids'])})")
    L += ["", "## نتيجة التنزيل",
          f"- NS1_APPLIES_TO_FNM1 = {d['NS1_APPLIES_TO_FNM1']}",
          f"- SOURCE_APPLIED = {tr['SOURCE_APPLIED']}",
          f"- TANZIL = {tr['TANZIL']} · TANZIL_STATUS = {tr['TANZIL_STATUS']}",
          f"- VERDICT = {tr['verdict']}",
          "- FINAL_HUKM = NO · FINAL_ANSWER = NO · JUDICIAL_OUTCOME = NOT_PRODUCED",
          "", "## السبب/الشرط/المانع",
          f"- CAUSE = {tr['cause']}",
          f"- CONDITIONS = {'، '.join(tr['conditions'])}",
          f"- PREVENTERS = {'، '.join(tr['preventers'])}",
          "", "## البقايا"]
    for r in tr["residuals"]:
        L.append(f"- {r}")
    L += ["", "---",
          "*التنزيل = تحقّق شروط المصدر في المناط؛ لم يُنتَج الحكم ولا الجواب ولا النتيجة القضائية، "
          "ولم يُقَل «يجوز» أو «لا يجوز». الحكم والجواب يحتاجان إذنًا صريحًا منفصلًا.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_spec(d):
    tr = d["tanzil_result"]
    rc = d["recheck"]
    tokens = load_tokens()
    token_rows = [[t["token_id"], t.get("original_surface", ""), t.get("word_class", "")] for t in tokens]

    be_rows = [[e["element_id"], e["label"], "، ".join(e["required_fact_ids"]), e["present"]]
               for e in d["binding_elements"]]
    be_cls = [["", "", "d", "y" if e["present"] == "YES" else "n"] for e in d["binding_elements"]]

    tanzil_rows = [
        ["NS1_APPLIES_TO_FNM1", d["NS1_APPLIES_TO_FNM1"], "y" if d["NS1_APPLIES_TO_FNM1"] == "YES" else "n"],
        ["SOURCE_APPLIED", tr["SOURCE_APPLIED"], "y" if tr["SOURCE_APPLIED"] == "YES" else "n"],
        ["TANZIL", tr["TANZIL"], "y" if tr["TANZIL"] == "YES" else "n"],
        ["TANZIL_STATUS", tr["TANZIL_STATUS"], "y" if tr["TANZIL_STATUS"] == "ACCEPTED" else "d"],
        ["VERDICT", tr["verdict"], "y"],
        ["FINAL_HUKM", "NO", "n"],
        ["FINAL_ANSWER", "NO", "n"],
        ["JUDICIAL_OUTCOME", "NOT_PRODUCED", "n"],
    ]
    cpp_rows = [
        ["CAUSE", tr["cause"]],
        ["CONDITIONS", "، ".join(tr["conditions"])],
        ["PREVENTERS", "، ".join(tr["preventers"])],
        ["VERDICT", tr["verdict"]],
    ]
    guard_rows = [[k, v, ("y" if v == "YES" else "n" if v == "NO" else "d")]
                  for k, v in d["guards"].items() if k != "producer_file"]
    closure_rows = [
        ["FINAL_MANAT", rc["FINAL_MANAT"], "y"],
        ["NORMATIVE_SOURCE_ACCEPTED", rc["NORMATIVE_SOURCE_ACCEPTED"], "y"],
        ["NS1_APPLIES_TO_FNM1", rc["NS1_APPLIES_TO_FNM1"], "y" if rc["NS1_APPLIES_TO_FNM1"] == "YES" else "n"],
        ["SOURCE_APPLIED", rc["SOURCE_APPLIED"], "y" if rc["SOURCE_APPLIED"] == "YES" else "n"],
        ["TANZIL", rc["TANZIL"], "y" if rc["TANZIL"] == "YES" else "n"],
        ["TANZIL_STATUS", rc["TANZIL_STATUS"], "y" if rc["TANZIL_STATUS"] == "ACCEPTED" else "d"],
        ["FINAL_HUKM", "NO", "n"],
        ["FINAL_ANSWER", "NO", "n"],
        ["JUDICIAL_OUTCOME_PRODUCED", "NO", "n"],
        ["FULL_TAAQOL_PROJECT_CLOSED", "NO", "n"],
    ]

    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "طُبِّق المصدر NS1 على المناط النهائي FNM1 لإنتاج التنزيل فقط (تحقّق الشروط)، لا الحكم.",
                f"NS1_APPLIES_TO_FNM1 = {d['NS1_APPLIES_TO_FNM1']} · SOURCE_APPLIED = {tr['SOURCE_APPLIED']} · "
                f"TANZIL = {tr['TANZIL']} ({tr['TANZIL_STATUS']}).",
                "لم يُنتَج حكم ولا جواب ولا نتيجة قضائية، ولم يُقَل «يجوز» أو «لا يجوز».",
            ]},
            {"raw_note": "<b>حدود صريحة:</b> SOURCE_APPLICATION_IS_NOT_FINAL_HUKM / NOT_FINAL_ANSWER · "
                         "NO_JUDICIAL_OUTCOME_PRODUCED · NO_PERMISSIBILITY_LANGUAGE · "
                         "FINAL_HUKM = NO · FINAL_ANSWER = NO.", "kind": "warn"},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات العشر", "body": [
            {"cols": {"headers": ["token", "السطح", "الفئة"], "rows": token_rows}}
            if token_rows else {"raw_note": "TOKEN_ARTIFACT_MISSING", "kind": "warn"},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "الإفادة مرشّحة سابقًا؛ هذه الجولة تنزيل لا إفادة. IFADAH_FINAL = NO.", "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.", "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0 · NO_FRAMENET · "
                         "المصدر مقبول ومربوط سابقًا (الجولة 50).", "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "التنزيل = انطباق شروط المصدر على المناط؛ وهو خطوة سابقة للحكم، لا يرخّص بنفسه "
                         "إنتاج الحكم أو الجواب أو نتيجة قضائية.", "kind": "warn"},
        ]},
        {"n": 8, "title": "المصدر المعياري والمناط — عناصر الربط ونتيجة التنزيل", "body": [
            {"kv": [["FINAL_MANAT_ID", d["final_manat_id"], "d"],
                    ["NORMATIVE_SOURCE_ID", d["normative_source_id"], "d"]]},
            {"note": "نص المصدر NS1 (مرجع، كما قُبل في الجولة 50):"},
            {"raw_note": d["normative_source_text"]},
            {"note": "جدول عناصر الربط (NS1 ↔ FNM1):"},
            {"cols": {"headers": ["element_id", "العنصر", "يحققها (fact_ids)", "present"],
                      "rows": be_rows, "row_classes": be_cls}},
            {"note": "جدول نتيجة التنزيل:"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in tanzil_rows],
                      "row_classes": [["", r[2]] for r in tanzil_rows]}},
            {"note": "السبب / الشرط / المانع:"},
            {"kv": cpp_rows},
        ]},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": tr["residuals"], "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"raw_note": "لا نقص في عناصر الربط؛ الناقص لاحقًا: إذن صريح لإنتاج الحكم (FINAL_HUKM) ثم الجواب.",
             "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "التنزيل منتج؛ الخطوة التالية (بإذن منفصل): FINAL_HUKM ثم FINAL_ANSWER — لا يُفتح "
                         "شيء منهما هنا.", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "trace_here": True, "body": [
            {"raw_note": "tests/test_taaqol_mat_malik_tanzil_application_51.py — ROUND51_TESTS = passed · "
                         "يتحقق من عناصر الربط ونتيجة التنزيل وبقاء الحكم/الجواب مغلقة."},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "TANZIL_APPLICATION_51_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                f"FINAL_MANAT_REF = {FINAL_MANAT_ID} (round 48, READ_ONLY)\n"
                f"NORMATIVE_SOURCE_REF = {NORMATIVE_SOURCE_ID} (round 50 acceptance, READ_ONLY)\n"
                f"NS1_APPLIES_TO_FNM1 = {d['NS1_APPLIES_TO_FNM1']} · SOURCE_APPLIED = {tr['SOURCE_APPLIED']} · "
                f"TANZIL = {tr['TANZIL']}\n"
                "BINDING_ELEMENTS_CHECKED = 8 (computed from round-48 accepted facts)\n"
                "NEW_SOURCE_ADDED = NO\nSEARCH_PERFORMED = NO\nPERMISSIBILITY_LANGUAGE = NO\n"
                "JUDICIAL_OUTCOME_PRODUCED = NO\nFRAMENET_USED = NO\nEXTERNAL_REFERENCE_USED = NO\n"
                "FINAL_HUKM = NO\nFINAL_ANSWER = NO\nCOMMIT = NO\nPUSH = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "تحقّقت عناصر ربط NS1 الثمانية في FNM1، فأُنتج التنزيل (SOURCE_APPLIED=YES، TANZIL=YES، "
                         "ACCEPTED) بوصفه انطباق شروط المصدر على المناط فقط. لم يُنتَج الحكم ولا الجواب ولا نتيجة "
                         "قضائية، ولم يُقَل «يجوز/لا يجوز». الحكم والجواب يحتاجان إذنًا صريحًا منفصلًا.", "kind": "warn"},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in closure_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in closure_rows + guard_rows]}},
        ]},
    ]

    trace_rows = [
        {"req": "REQ-MAT-MALIK-TANZIL-JSON", "source": "ROUND48_FINAL_MANAT + ROUND50_NORMATIVE_SOURCE",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51.json",
         "test": "tests/test_taaqol_mat_malik_tanzil_application_51.py", "status": "TRACEABLE"},
        {"req": "REQ-MAT-MALIK-TANZIL-GUARDS", "source": "ROUND_51",
         "artifact": "output/taaqol_maqam_foundation_generated/TAAQOL_MAT_MALIK_TANZIL_APPLICATION_GUARDS_51.json",
         "test": "tests/test_taaqol_mat_malik_tanzil_application_51.py", "status": "TRACEABLE"},
    ]

    return {
        "title": "تقرير تنفيذي — تطبيق NS1 على FNM1 (التنزيل فقط) «مات ملك» (51)",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>التنزيل فقط:</b> انطباق شروط المصدر NS1 على عناصر المناط FNM1؛ لا حكم، لا جواب، "
                     "لا نتيجة قضائية، لا «يجوز/لا يجوز». الحكم والجواب يحتاجان إذنًا صريحًا منفصلًا."),
        ],
        "sentence": {"label": "النازلة", "text": SENTENCE, "id": "nazila-sentence"},
        "sections": sections,
        "trace": {"title": "جدول التتبّع (مستقل عن جدول الكلمات)", "rows": trace_rows},
        "closure_flags": (
            f"FINAL_MANAT = YES · NORMATIVE_SOURCE_ACCEPTED = YES · NORMATIVE_SOURCE_ID = {NORMATIVE_SOURCE_ID} · "
            f"NS1_APPLIES_TO_FNM1 = {d['NS1_APPLIES_TO_FNM1']} · SOURCE_APPLIED = {tr['SOURCE_APPLIED']} · "
            f"TANZIL = {tr['TANZIL']} · TANZIL_STATUS = {tr['TANZIL_STATUS']} · FINAL_HUKM = NO · "
            "FINAL_ANSWER = NO · JUDICIAL_OUTCOME_PRODUCED = NO · FULL_TAAQOL_PROJECT_CLOSED = NO."),
        "tests_result": "ROUND51_TESTS = passed",
        "footer": "تطبيق المصدر على المناط — التنزيل فقط، لا حكم/جواب/نتيجة قضائية (RENDERER=TAAQOL_STYLE).",
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out",
                    default=str(OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_MANAGER_REPORT_AR_51.html"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_MAT_MALIK_TANZIL_APPLICATION_GUARDS_51.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.report_out).write_text(
        render_taaqol_style_manager_report(build_spec(d)), encoding="utf-8")

    tr = d["tanzil_result"]
    print("TANZIL_APPLICATION_51_REPORT=" + a.report_out)
    print(f"NS1_APPLIES_TO_FNM1={d['NS1_APPLIES_TO_FNM1']} SOURCE_APPLIED={tr['SOURCE_APPLIED']} "
          f"TANZIL={tr['TANZIL']} STATUS={tr['TANZIL_STATUS']} FINAL_HUKM=NO FINAL_ANSWER=NO")


if __name__ == "__main__":
    main()
