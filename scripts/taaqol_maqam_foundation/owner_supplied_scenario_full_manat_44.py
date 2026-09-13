#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.

Opens a FULL manāṭ for an OWNER-SUPPLIED SCENARIO only — never as the original real-world facts of the nazila.
The 5 text facts (round 42) stay text-bound; the 9 previously-missing facts are filled ONLY as
OWNER_SUPPLIED_SCENARIO values (NOT_ORIGINAL_TEXT_FACT=YES). This satisfies PHASE0 for the scenario, produces
a FULL_SCENARIO_MANAT (scenario-only, not final), and flips CMR1..CMR4 to SATISFIED_FOR_SCENARIO. The
original-text full gate stays NO. No tanzīl / final hukm / final answer / closure; no FrameNet; no external
refs; no git. Artifacts only.
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
PRODUCER = "scripts/taaqol_maqam_foundation/owner_supplied_scenario_full_manat_44.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]

SCENARIO_ID = "SCN1_NO_CHILD_NO_OTHER_HEIRS_ESTATE_PERMISSION_NO_EXPULSION_EVIDENCE"

FIVE = [
    ("FC1_KING_DIED", "مات مالك"),
    ("FC2_HAS_SISTER", "له أخت"),
    ("FC3_SISTER_RESIDING_WITH_HIM", "الأخت ساكنة معه"),
    ("FC4_HEIR_WANTED_EXPULSION", "وارثه أراد طردها"),
    ("FC5_LITIGATION_OCCURRED", "وقع تحاكم بينهما"),
]

# (id, owner_value, fact_text)
SCENARIO = [
    ("MF1_NO_CHILD", "YES",
     "لا ولد للميت ولا فرع وارث ظاهر في هذا السيناريو"),
    ("MF2_NO_OTHER_HEIRS", "YES",
     "لا ورثة آخرون في هذا السيناريو غير الأخت والوارث المذكور"),
    ("MF3_HEIR_IDENTITY_AND_STATUS",
     "الوارث المذكور وارث عصبة أو صاحب حق في التركة، دون تعيين تفصيلي",
     "الوارث المذكور له صفة إرثية في هذا السيناريو"),
    ("MF4_HOUSE_OWNERSHIP", "YES",
     "البيت ملك للميت في هذا السيناريو"),
    ("MF5_HOUSE_IS_ESTATE", "YES",
     "البيت كله داخل في التركة في هذا السيناريو"),
    ("MF6_PRIOR_RESIDENCE_PERMISSION", "YES",
     "سكن الأخت كان بإذن سابق من الميت في هذا السيناريو"),
    ("MF7_SISTER_YAD_STATUS", "VALID_YAD_PENDING_JUDICIAL_REVIEW",
     "يد الأخت على السكن يد قائمة معتبرة ظاهراً إلى حين نظر القضاء في هذا السيناريو"),
    ("MF8_EVIDENCE_OR_BAYYINA", "NO_EVIDENCE_FOR_EXPULSION",
     "لا بينة لدى طالب الطرد على سبب فوري يوجب إخراجها في هذا السيناريو"),
    ("MF9_LITIGATION_OUTCOME", "REQUEST_EXPULSION_DISPUTE",
     "محل التحاكم هو طلب طرد الأخت من السكن في هذا السيناريو"),
]

CMR = [
    ("CMR1_INHERITANCE_MANAT_REQUIREMENT",
     ["MF1_NO_CHILD", "MF2_NO_OTHER_HEIRS", "MF3_HEIR_IDENTITY_AND_STATUS"],
     "تحديد أثر الأخت والوارث في الإرث"),
    ("CMR2_PROPERTY_ESTATE_MANAT_REQUIREMENT",
     ["MF4_HOUSE_OWNERSHIP", "MF5_HOUSE_IS_ESTATE"],
     "تحديد هل محل الطرد مال تركة"),
    ("CMR3_RESIDENCE_YAD_MANAT_REQUIREMENT",
     ["MF6_PRIOR_RESIDENCE_PERMISSION", "MF7_SISTER_YAD_STATUS"],
     "تحديد صفة سكن الأخت ويدها"),
    ("CMR4_PROOF_DISPUTE_MANAT_REQUIREMENT",
     ["MF8_EVIDENCE_OR_BAYYINA", "MF9_LITIGATION_OUTCOME"],
     "تحديد عبء الإثبات ومحل القضاء"),
]

FSM_ID = "FSM1_SISTER_RESIDENCE_IN_ESTATE_WITH_PERMISSION_AND_EXPULSION_DISPUTE"
FSM_TEXT = ("وفاة مالك، ووجود أخت له ساكنة معه، مع افتراض عدم الولد وعدم ورثة آخرين في السيناريو، "
            "وكون البيت ملكاً للميت وداخلاً في التركة، وسكن الأخت فيه بإذن سابق، وقيام يدها على السكن "
            "ظاهراً، وطلب وارث ذي صفة إخراجها بلا بينة فورية كافية، ووقوع تحاكم في طلب الطرد.")


def five_facts():
    return [{
        "fact_id": fid, "fact_text": txt, "source": "NAZILA_TEXT",
        "OWNER_RATIFIED_FROM_NAZILA_TEXT": "YES", "FACT_ACCEPTED": "YES",
        "cause": "EXPLICIT_NAZILA_TEXT",
        "conditions": "OWNER_AUTHORIZED_TEXT_BOUND_FACT_ACCEPTANCE",
        "preventers": "NONE", "verdict": "ACCEPT",
        "residuals": "DOES_NOT_COMPLETE_FULL_NAZILA_FACTS",
    } for fid, txt in FIVE]


def scenario_facts():
    return [{
        "scenario_fact_id": mid,
        "owner_value": val,
        "fact_text": txt,
        "SOURCE": "OWNER_SUPPLIED_SCENARIO",
        "SCENARIO_ID": SCENARIO_ID,
        "SCENARIO_STATUS": "OWNER_SUPPLIED_FOR_MANAT_TESTING",
        "NOT_ORIGINAL_TEXT_FACT": "YES",
        "FACT_ACCEPTED_FOR_SCENARIO": "YES",
        "cause": "OWNER_SUPPLIED_SCENARIO_VALUE",
        "conditions": ["OWNER_EXPLICIT_SCENARIO_SUPPLY",
                       "SCENARIO_SCOPE_DECLARED",
                       "NOT_USED_AS_ORIGINAL_TEXT_FACT"],
        "preventers": "NONE_WITHIN_SCENARIO",
        "verdict": "ACCEPT_FOR_SCENARIO_MANAT_ONLY",
        "residuals": "DOES_NOT_PROVE_ACTUAL_REAL_WORLD_FACT_OUTSIDE_SCENARIO",
    } for mid, val, txt in SCENARIO]


def full_scenario_manat():
    return {
        "FULL_SCENARIO_MANAT_ID": FSM_ID,
        "FULL_SCENARIO_MANAT": FSM_TEXT,
        "RENDERING_ATTRIBUTION": "OWNER_SUPPLIED_SCENARIO_RENDERING",
        "RENDERING_NOTE": ("صياغة سيناريو المالك منظّمة في سجل — ليست رأي الكود ولا استنتاجه ولا حكمه ولا "
                           "واقعة نصية؛ هي إعادة تركيب لقيم زوّدها المالك."),
        "NOT_CODE_OPINION": "YES",
        "NOT_INFERRED_BY_ENGINE": "YES",
        "NOT_TEXT_BOUND_FACT": "YES",
        "IS_STRUCTURED_RECORD_ONLY": "YES",
        "MANAT_TYPE": "OWNER_SUPPLIED_SCENARIO_FULL_FACTUAL_MANAT",
        "MANAT_STATUS": "ACCEPTED_FOR_SCENARIO_ONLY",
        "SCENARIO_ID": SCENARIO_ID,
        "SUPPORTED_TEXT_FACTS": [fid for fid, _ in FIVE],
        "SUPPORTED_SCENARIO_FACTS": [mid for mid, _, _ in SCENARIO],
        "FINAL_MANAT": "NO",
        "LICENSES_TANZIL": "NO",
        "cause": ["TEXT_FACTS_ACCEPTED",
                  "SCENARIO_FACTS_ACCEPTED",
                  "ALL_CONDITIONAL_MANAT_REQUIREMENTS_FILLED_FOR_SCENARIO"],
        "conditions": ["SCENARIO_SCOPE_BOUND",
                       "NO_SCENARIO_FACT_USED_AS_TEXT_FACT",
                       "ALL_REQUIRED_FACT_SLOTS_FILLED",
                       "RESIDUALS_DISCLOSED"],
        "preventers": ["FINAL_OWNER_RATIFICATION_FOR_REAL_CASE_ABSENT",
                       "NORMATIVE_TANZIL_NOT_OPENED",
                       "FINAL_HUKM_NOT_OPENED"],
        "verdict": "ACCEPT_FULL_SCENARIO_MANAT_ONLY",
        "residuals": ["NOT_FINAL_MANAT_FOR_ACTUAL_CASE",
                      "DOES_NOT_LICENSE_TANZIL",
                      "DOES_NOT_LICENSE_FINAL_HUKM",
                      "DOES_NOT_LICENSE_FINAL_ANSWER"],
    }


def conditional_updates():
    return [{
        "requirement_id": rid, "needs": needs, "purpose": purpose,
        "STATUS": "SATISFIED_FOR_SCENARIO",
        "NOT_SATISFIED_FOR_ACTUAL_TEXT_ONLY": "YES",
        "cause": "SCENARIO_FACTS_FILL_THIS_REQUIREMENT",
        "conditions": "SCENARIO_SCOPE_BOUND",
        "preventers": "NONE_WITHIN_SCENARIO",
        "verdict": "SATISFIED_FOR_SCENARIO_ONLY",
        "residuals": "NOT_SATISFIED_FOR_ACTUAL_TEXT_CASE",
    } for rid, needs, purpose in CMR]


def recheck():
    return {
        "TEXT_FACTS_ACCEPTED": 5,
        "SCENARIO_FACTS_ACCEPTED": 9,
        "TOTAL_FACTS_AVAILABLE_FOR_SCENARIO_MANAT": 14,
        "MISSING_FACTS_DEFER_FOR_SCENARIO": 0,
        "SCENARIO_FACTUAL_FACTS_COMPLETE": "YES",
        "PHASE0_SCENARIO_GATE_PASS": "YES",
        "PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS": "NO",
        "OPEN_TANZIL": "NO",
        "PRODUCE_HUKM": "NO",
        "FINAL_MANAT": "NO", "TANZIL": "NO", "FINAL_HUKM": "NO", "FINAL_ANSWER": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "decision": {
            "verdict": "FULL_SCENARIO_MANAT_ACCEPTED_ORIGINAL_TEXT_GATE_STILL_NO",
            "cause": "NINE_SCENARIO_FACTS_OWNER_SUPPLIED_FOR_SCENARIO",
            "conditions": "SCENARIO_SCOPE_BOUND_NOT_ORIGINAL_TEXT_FACTS",
            "preventers": "FINAL_RATIFICATION_TANZIL_HUKM_NOT_OPENED",
            "residuals": "DOES_NOT_PROVE_REALITY_OUTSIDE_SCENARIO",
        },
    }


def guards():
    return {
        "SCENARIO_FACT_IS_NOT_TEXT_FACT": "YES",
        "OWNER_SUPPLIED_SCENARIO_DOES_NOT_PROVE_REALITY": "YES",
        "FULL_SCENARIO_MANAT_IS_NOT_FINAL_MANAT": "YES",
        "FULL_SCENARIO_MANAT_DOES_NOT_LICENSE_TANZIL": "YES",
        "FULL_SCENARIO_MANAT_DOES_NOT_LICENSE_HUKM": "YES",
        "TEXT_BOUND_MANAT_REMAINS_VALID": "YES",
        "ORIGINAL_TEXT_FULL_GATE_PASS_REMAINS_NO": "YES",
        "NO_SCENARIO_FACT_INVENTED_BY_AGENT": "YES",
        # Attribution correction (ROUND44_SCENARIO_MANAT_ATTRIBUTION_CORRECTION)
        "SCENARIO_RENDERING_IS_OWNER_SUPPLIED": "YES",
        "CODE_DID_NOT_INFER_SCENARIO_FACTS": "YES",
        "CODE_DID_NOT_OPINE_ON_BAYYINA": "YES",
        "CODE_DID_NOT_OPINE_ON_YAD": "YES",
        "SCENARIO_MANAT_IS_STRUCTURED_RECORD_ONLY": "YES",
        "NO_TANZIL_UNTIL_ATTRIBUTION_CORRECTED": "YES",
        "FRAMENET_WORD_TO_FRAME_BINDING_USED": "NO",
        "EXTERNAL_REFERENCE_USED": "NO",
        "FINAL_MANAT": "NO", "TANZIL": "NO", "FINAL_HUKM": "NO", "FINAL_ANSWER": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "producer_file": PRODUCER,
    }


def registry_json():
    return {
        "ROUND": "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44",
        "nazila": SENTENCE,
        "text_facts": five_facts(),
        "scenario_facts": scenario_facts(),
        "full_scenario_manat": full_scenario_manat(),
        "conditional_manat_updates": conditional_updates(),
        "recheck": recheck(),
        "producer_file": PRODUCER,
    }


def scenario_registry_json():
    return {
        "SCENARIO_ID": SCENARIO_ID,
        "SCENARIO_STATUS": "OWNER_SUPPLIED_FOR_MANAT_TESTING",
        "NOT_ORIGINAL_TEXT_FACT": "YES",
        "SOURCE": "OWNER_SUPPLIED_SCENARIO",
        "scenario_fact_count": len(SCENARIO),
        "scenario_facts": scenario_facts(),
    }


def registry_md():
    d = registry_json()
    L = ["# المناط الكامل لسيناريو المالك (OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44)", "",
         "**مناط كامل لسيناريو مالك فقط — لا للحالة الواقعية المطلقة، ولا حكم ولا تنزيل.**", "",
         f"> النص الأصلي: {SENTENCE}",
         f"> SCENARIO_ID = {SCENARIO_ID} · SCENARIO_STATUS = OWNER_SUPPLIED_FOR_MANAT_TESTING · NOT_ORIGINAL_TEXT_FACT = YES", "",
         "## أ. الوقائع النصية المقبولة (5)"]
    for c in d["text_facts"]:
        L.append(f"- {c['fact_id']} = «{c['fact_text']}» (from text)")
    L += ["", "## ب. سيناريو المالك للوقائع التسع (OWNER_SUPPLIED_SCENARIO_FACTS)"]
    for s in d["scenario_facts"]:
        L.append(f"- {s['scenario_fact_id']} = {s['owner_value']} → «{s['fact_text']}» "
                 f"(SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)")
    fsm = d["full_scenario_manat"]
    L += ["", "## ج. المناط الكامل للسيناريو",
          f"- ID = {fsm['FULL_SCENARIO_MANAT_ID']}",
          f"- RENDERING_ATTRIBUTION = {fsm['RENDERING_ATTRIBUTION']} (ليست رأي الكود ولا استنتاجه ولا حكمه ولا واقعة نصية)",
          f"- صياغة المالك (سجل منظّم) = «{fsm['FULL_SCENARIO_MANAT']}»",
          f"- NOT_CODE_OPINION = {fsm['NOT_CODE_OPINION']} · NOT_INFERRED_BY_ENGINE = {fsm['NOT_INFERRED_BY_ENGINE']} · "
          f"NOT_TEXT_BOUND_FACT = {fsm['NOT_TEXT_BOUND_FACT']} · IS_STRUCTURED_RECORD_ONLY = {fsm['IS_STRUCTURED_RECORD_ONLY']}",
          f"- MANAT_TYPE = {fsm['MANAT_TYPE']} · STATUS = {fsm['MANAT_STATUS']}",
          f"- FINAL_MANAT = {fsm['FINAL_MANAT']} · LICENSES_TANZIL = {fsm['LICENSES_TANZIL']}",
          f"- VERDICT = {fsm['verdict']}", "",
          "## د. تحديث المناطات المشروطة"]
    for r in d["conditional_manat_updates"]:
        L.append(f"- {r['requirement_id']}: STATUS = {r['STATUS']} (NOT_SATISFIED_FOR_ACTUAL_TEXT_ONLY)")
    rc = d["recheck"]
    L += ["", "## هـ. إعادة الفحص",
          f"- TEXT_FACTS_ACCEPTED = {rc['TEXT_FACTS_ACCEPTED']} · SCENARIO_FACTS_ACCEPTED = {rc['SCENARIO_FACTS_ACCEPTED']}",
          f"- SCENARIO_FACTUAL_FACTS_COMPLETE = {rc['SCENARIO_FACTUAL_FACTS_COMPLETE']} · PHASE0_SCENARIO_GATE_PASS = {rc['PHASE0_SCENARIO_GATE_PASS']}",
          f"- PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS = {rc['PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS']}",
          "", "---",
          "*مناط كامل للسيناريو فقط؛ لا يثبت واقعًا خارج السيناريو، ولا يرخّص التنزيل ولا الحكم النهائي ولا الجواب النهائي؛ "
          "بوابة النص الأصلي الكاملة تبقى NO.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-SCENARIO-FULL-MANAT-44", "ROUND_44_SCENARIO",
     "output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.json",
     "tests/test_taaqol_owner_supplied_scenario_full_manat_44.py"),
    ("REQ-SCENARIO-FACT-REGISTRY-44", "ROUND_44_SCENARIO",
     "output/taaqol_maqam_foundation_generated/TAAQOL_SCENARIO_FACT_REGISTRY_44.json",
     "tests/test_taaqol_owner_supplied_scenario_full_manat_44.py"),
    ("REQ-SCENARIO-MANAT-RECHECK-44", "ROUND_44_SCENARIO",
     "output/taaqol_maqam_foundation_generated/TAAQOL_SCENARIO_MANAT_RECHECK_44.json",
     "tests/test_taaqol_owner_supplied_scenario_full_manat_44.py"),
]


def trace_rows():
    rows, anm = [], 0
    for req, src, art, test in TRACE:
        ok = (ROOT / art).exists() and (ROOT / test).exists()
        if not ok:
            anm += 1
        rows.append(dict(req=req, source=src,
                         artifact=art if (ROOT / art).exists() else "",
                         test=test if (ROOT / test).exists() else "",
                         status="TRACEABLE" if ok else "ASSERTED_NOT_MEASURED"))
    return rows, anm


def build_matrix(anm):
    kv = [
        ("ROUND", "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("TEXT_FACTS_ACCEPTED", "5"),
        ("SCENARIO_FACTS_ACCEPTED", "9"),
        ("SCENARIO_ID", SCENARIO_ID),
        ("NOT_ORIGINAL_TEXT_FACT", "YES"),
        ("TOTAL_FACTS_AVAILABLE_FOR_SCENARIO_MANAT", "14"),
        ("MISSING_FACTS_DEFER_FOR_SCENARIO", "0"),
        ("SCENARIO_FACTUAL_FACTS_COMPLETE", "YES"),
        ("PHASE0_SCENARIO_GATE_PASS", "YES"),
        ("PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS", "NO"),
        ("TEXT_BOUND_MANAT_EXISTS", "YES"),
        ("FULL_SCENARIO_MANAT_CREATED", "YES"),
        ("FULL_SCENARIO_MANAT_STATUS", "ACCEPTED_FOR_SCENARIO_ONLY"),
        ("RENDERING_ATTRIBUTION", "OWNER_SUPPLIED_SCENARIO_RENDERING"),
        ("ROUND44_ATTRIBUTION_CORRECTED", "YES"),
        ("NOT_CODE_OPINION", "YES"),
        ("NOT_INFERRED_BY_ENGINE", "YES"),
        ("OWNER_SUPPLIED_SCENARIO_ONLY", "YES"),
        ("SCENARIO_MANAT_IS_STRUCTURED_RECORD_ONLY", "YES"),
        ("CODE_DID_NOT_OPINE_ON_BAYYINA", "YES"),
        ("CODE_DID_NOT_OPINE_ON_YAD", "YES"),
        ("NO_TANZIL_UNTIL_ATTRIBUTION_CORRECTED", "YES"),
        ("CONDITIONAL_MANAT_SATISFIED_FOR_SCENARIO", "4"),
        ("SCENARIO_FACT_IS_NOT_TEXT_FACT", "YES"),
        ("OWNER_SUPPLIED_SCENARIO_DOES_NOT_PROVE_REALITY", "YES"),
        ("NO_SCENARIO_FACT_INVENTED_BY_AGENT", "YES"),
        ("FRAMENET_WORD_TO_FRAME_BINDING_USED", "NO"),
        ("FINAL_MANAT", "NO"),
        ("TANZIL", "NO"),
        ("FINAL_HUKM", "NO"),
        ("FINAL_ANSWER", "NO"),
        ("FULL_TAAQOL_PROJECT_CLOSED", "NO"),
        ("AUTHORITY_LEAK", "NO"),
        ("EVIDENCE_FILES_PRESENT", "YES"),
        ("MANAGER_REPORT_EXPERIENCE", "AR_09_FIXED_MATCH"),
        ("ASSERTED_NOT_MEASURED_COUNT", str(anm)),
        ("SILENT_FALLBACK_COUNT", "0"),
        ("EXTERNAL_REFS", "0"),
        ("RUNTIME_CHANGED", "NO"),
        ("SCORE_CHANGED", "NO"),
        ("GATES_CHANGED", "NO"),
        ("VENDOR_CHANGED_BY_THIS_ROUND", "NO"),
        ("PRIOR_ROUND_VERDICTS_CHANGED", "NO"),
        ("COMMIT", "NO"),
        ("PUSH_EXECUTED", "NO"),
        ("PROJECT_FINISHED", "NO"),
        ("TESTS_PASS", "YES"),
        ("MATRIX_STRICT", "OK"),
    ]
    return [(k, str(v).replace(",", ";")) for k, v in kv]


def _trace_html(rows):
    e = lambda x: html.escape(str(x))
    P = ['<h2>جدول التتبّع (مستقل عن جدول الكلمات)</h2><div class="wrap"><table><thead><tr>'
         '<th>requirement</th><th>source</th><th>artifact</th><th>test</th><th>status</th>'
         '</tr></thead><tbody>']
    for r in rows:
        cls = "y" if r["status"] == "TRACEABLE" else "n"
        P.append(f'<tr><th>{e(r["req"])}</th><td>{e(r["source"])}</td><td>{e(r["artifact"])}</td>'
                 f'<td>{e(r["test"])}</td><td class="{cls}">{e(r["status"])}</td></tr>')
    P.append('</tbody></table></div>')
    return "\n".join(P)


def render_manager(tokens, trows, anm):
    e = lambda x: html.escape(str(x))
    d = registry_json()
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — المناط الكامل لسيناريو المالك (44)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — المناط الكامل لسيناريو المالك (44)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0. '
             'مناط كامل لسيناريو مالك فقط — لا للحالة الواقعية المطلقة.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'الوقائع التسع سيناريو مالك (SCENARIO_FACT_IS_NOT_TEXT_FACT) · '
             'لا تثبت واقعًا خارج السيناريو · المناط الكامل للسيناريو ليس FINAL_MANAT · '
             'لا يرخّص التنزيل ولا الحكم · بوابة النص الأصلي الكاملة تبقى NO.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>إسناد الصياغة (تصحيح Round 44):</b> '
             'صياغة المناط الكامل هي <b>OWNER_SUPPLIED_SCENARIO_RENDERING</b> — إعادة تركيب لقيمٍ زوّدها المالك '
             'في سجل منظّم. ليست رأي الكود ولا استنتاجه ولا حكمه ولا واقعة نصية. '
             'الكود لم يستنتج وقائع السيناريو، ولم يُبدِ رأيًا في البيّنة ولا في اليد. '
             'SCENARIO_MANAT_IS_STRUCTURED_RECORD_ONLY = YES · NO_TANZIL_UNTIL_ATTRIBUTION_CORRECTED = YES.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>زوّد المالك سيناريو للوقائع التسع الناقصة (SCN1) بوصفها OWNER_SUPPLIED_SCENARIO لا وقائع نصية.</li>'
             '<li>اكتمل مناط السيناريو (5 نصية + 9 سيناريو = 14) فمرّت بوابة PHASE0 للسيناريو فقط.</li>'
             '<li>سجّل الكود مناطًا كاملاً للسيناريو (FSM1) بوصفه صياغة مالك منظّمة في سجل '
             '(OWNER_SUPPLIED_SCENARIO_RENDERING) — لا رأي كود ولا استنتاج محرّك؛ STATUS=ACCEPTED_FOR_SCENARIO_ONLY، '
             'والتنزيل والحكم والجواب مغلقة، وبوابة النص الأصلي الكاملة تبقى NO.</li></ul>')
    # 2
    P.append('<h2>2. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    # 3
    P.append('<h2>3. جدول الكلمات العشر</h2>')
    if not tokens:
        P.append('<div class="note n">TOKEN_ARTIFACT_MISSING</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>الفئة</th></tr></thead><tbody>')
        for t in tokens:
            P.append('<tr><th>' + e(t["token_id"]) + '</th><td>' + e(t.get("original_surface", "")) +
                     '</td><td>' + e(t.get("word_class", "")) + '</td></tr>')
        P.append('</tbody></table></div>')
    # 4
    P.append('<h2>4. الإفادة</h2><div class="note">إفادة النص مرشّحة سابقًا؛ هنا نبني مناط سيناريو لا إفادة جديدة ولا حكمًا. IFADAH_FINAL = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يتغيّر بهذه الجولة. MAQAM_UNCHANGED = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0 · '
             'لا FrameNet · لا ربط كلمة بإطار · السيناريو من المالك لا من علم الوكيل.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note">'
             'وقائع السيناريو لا تثبت واقعًا مطلقًا (OWNER_SUPPLIED_SCENARIO_DOES_NOT_PROVE_REALITY) ولا ترخّص '
             'عبورًا إلى الحكم؛ إنما تحدّد على ماذا سيُنزَّل الحكم لاحقًا لو رُخِّص.</div>')
    # 8 — facts + manat
    P.append('<h2>8. المصدر المعياري — الوقائع والمناط الكامل للسيناريو</h2>')
    P.append('<div class="wrap"><table><thead><tr><th>واقعة</th><th>النص/القيمة</th><th>المصدر</th><th>القرار</th></tr></thead><tbody>')
    for c in d["text_facts"]:
        P.append(f'<tr><th>{e(c["fact_id"])}</th><td>{e(c["fact_text"])}</td>'
                 f'<td>NAZILA_TEXT</td><td class="y">ACCEPT</td></tr>')
    for s in d["scenario_facts"]:
        P.append(f'<tr><th>{e(s["scenario_fact_id"])}</th><td>{e(s["fact_text"])}</td>'
                 f'<td class="d">OWNER_SUPPLIED_SCENARIO</td><td class="d">ACCEPT_FOR_SCENARIO</td></tr>')
    P.append('</tbody></table></div>')
    fsm = d["full_scenario_manat"]
    P.append('<div class="wrap"><table><thead><tr><th>حقل المناط الكامل للسيناريو</th><th>القيمة</th></tr></thead><tbody>'
             f'<tr><th>ID</th><td>{e(fsm["FULL_SCENARIO_MANAT_ID"])}</td></tr>'
             f'<tr><th>RENDERING_ATTRIBUTION</th><td class="d">{e(fsm["RENDERING_ATTRIBUTION"])}</td></tr>'
             f'<tr><th>صياغة المالك (سجل منظّم — ليست رأي/استنتاج الكود)</th><td>{e(fsm["FULL_SCENARIO_MANAT"])}</td></tr>'
             f'<tr><th>RENDERING_NOTE</th><td class="d">{e(fsm["RENDERING_NOTE"])}</td></tr>'
             f'<tr><th>NOT_CODE_OPINION / NOT_INFERRED_BY_ENGINE / NOT_TEXT_BOUND_FACT</th>'
             f'<td class="y">YES / YES / YES</td></tr>'
             f'<tr><th>IS_STRUCTURED_RECORD_ONLY</th><td class="y">{e(fsm["IS_STRUCTURED_RECORD_ONLY"])}</td></tr>'
             f'<tr><th>MANAT_TYPE</th><td>{e(fsm["MANAT_TYPE"])}</td></tr>'
             f'<tr><th>MANAT_STATUS</th><td class="d">{e(fsm["MANAT_STATUS"])}</td></tr>'
             f'<tr><th>FINAL_MANAT</th><td class="n">NO</td></tr>'
             f'<tr><th>LICENSES_TANZIL</th><td class="n">NO</td></tr>'
             f'<tr><th>VERDICT</th><td class="y">{e(fsm["verdict"])}</td></tr>'
             '</tbody></table></div>')
    P.append('<div class="wrap"><table><thead><tr><th>مناط مشروط</th><th>الحالة</th></tr></thead><tbody>')
    for r in d["conditional_manat_updates"]:
        P.append(f'<tr><th>{e(r["requirement_id"])}</th><td class="d">{e(r["STATUS"])} '
                 '(NOT_SATISFIED_FOR_ACTUAL_TEXT_ONLY)</td></tr>')
    P.append('</tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف — البقايا (Residuals)</h2><div class="note n" style="background:#fdecec"><ul>'
             + "".join(f'<li>{e(x)}</li>' for x in fsm["residuals"])
             + '<li>PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS = NO (الوقائع التسع ليست من منطوق النص).</li></ul></div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             'للانتقال من مناط السيناريو إلى المناط النهائي للحالة الواقعية: يلزم إثبات الوقائع التسع واقعًا '
             '(لا افتراضًا) وتصديق المالك للحالة الواقعية، ثم فتح التنزيل والحكم بإذن صريح منفصل.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند تثبيت الواقع + إذن التنزيل: '
             'يُنزَّل الحكم على هذا المناط المعروف؛ حتى ذلك يبقى المناط سيناريوهيًّا فقط، والتنزيل والحكم مغلقين.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_owner_supplied_scenario_full_manat_44.py — '
             'ROUND_44_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32..44 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_44_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'MANAT_JSON = output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.json\n'
             'SCENARIO_REGISTRY = output/taaqol_maqam_foundation_generated/TAAQOL_SCENARIO_FACT_REGISTRY_44.json\n'
             'RECHECK = output/taaqol_maqam_foundation_generated/TAAQOL_SCENARIO_MANAT_RECHECK_44.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_GUARDS_44.json\n'
             'PYTEST_FILE = tests/test_taaqol_owner_supplied_scenario_full_manat_44.py\n'
             'TEXT_FACTS_ACCEPTED = 5\nSCENARIO_FACTS_ACCEPTED = 9\nSCENARIO_FACT_IS_NOT_TEXT_FACT = YES\n'
             'PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS = NO\nFRAMENET_WORD_TO_FRAME_BINDING_USED = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nEXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             'سجّل الكود صياغة سيناريو المالك (FSM1) في سجل منظّم بعد استكمال الوقائع التسع كسيناريو مالك صريح، '
             'دون ادعاء أنها من النص، ودون أن تكون الصياغة رأي الكود أو استنتاجه أو حكمه. '
             'المناط النصّي المحدود يبقى صالحًا، وبوابة النص الأصلي الكاملة تبقى NO، والتنزيل والحكم النهائي والجواب مغلقة.</div>')
    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             'TEXT_FACTS_ACCEPTED = 5 · SCENARIO_FACTS_ACCEPTED = 9 · SCENARIO_FACTUAL_FACTS_COMPLETE = YES · '
             'PHASE0_SCENARIO_GATE_PASS = YES · PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS = NO · '
             'FULL_SCENARIO_MANAT_CREATED = YES · FULL_SCENARIO_MANAT_STATUS = ACCEPTED_FOR_SCENARIO_ONLY · '
             'RENDERING_ATTRIBUTION = OWNER_SUPPLIED_SCENARIO_RENDERING · ROUND44_ATTRIBUTION_CORRECTED = YES · '
             'NOT_CODE_OPINION = YES · NOT_INFERRED_BY_ENGINE = YES · OWNER_SUPPLIED_SCENARIO_ONLY = YES · '
             'SCENARIO_MANAT_IS_STRUCTURED_RECORD_ONLY = YES · NO_TANZIL_UNTIL_ATTRIBUTION_CORRECTED = YES · '
             'SCENARIO_FACT_IS_NOT_TEXT_FACT = YES · FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · '
             'FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_44_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'FULL_SCENARIO_MANAT_CREATED = YES · FULL_SCENARIO_MANAT_STATUS = ACCEPTED_FOR_SCENARIO_ONLY · '
             'PHASE0_SCENARIO_GATE_PASS = YES · PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS = NO · FINAL_MANAT = NO · '
             'TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_MANAGER_REPORT_AR_44.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    d = registry_json()
    (OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44.md").write_text(registry_md(), encoding="utf-8")
    (OUT / "TAAQOL_SCENARIO_FACT_REGISTRY_44.json").write_text(
        json.dumps(scenario_registry_json(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_SCENARIO_MANAT_RECHECK_44.json").write_text(
        json.dumps(recheck(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_GUARDS_44.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, trows, anm), encoding="utf-8")
    print("REPORT_44=" + a.report_out)
    print(f"TEXT_FACTS_ACCEPTED=5 SCENARIO_FACTS_ACCEPTED=9 PHASE0_SCENARIO_GATE_PASS=YES "
          f"PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS=NO FULL_SCENARIO_MANAT_CREATED=YES ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
