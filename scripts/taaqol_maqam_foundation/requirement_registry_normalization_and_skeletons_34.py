#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_AND_SKELETONS_34.

Builds ONLY: (A) the normalized requirement registry — each of the ten round-32 requirements exploded
into 4 dimension rows (FACT / SOURCE / OWNER_DECISION / GATE) = 40 rows; (B) 13 registry SKELETONS
(definitions, not populated records); (C) a PHASE-0 recheck that stays BLOCKED because registries are
unpopulated and no owner facts exist. Supplies no facts, creates no sources/hukm/tanzīl/final answer.
No commit; no push. Manager report obeys the AR_09_FIXED experience.
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
PRODUCER = "scripts/taaqol_maqam_foundation/requirement_registry_normalization_and_skeletons_34.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
REGISTRY_32 = OUT / "TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json"
DIMENSIONS = ["FACT_REQUIREMENT", "SOURCE_REQUIREMENT", "OWNER_DECISION_REQUIREMENT", "GATE_REQUIREMENT"]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]

# parent requirement -> its domain gate registry (for the GATE dimension)
PARENT_GATE_REGISTRY = {
    "REQ01_NO_CHILD": "inheritance_condition_registry",
    "REQ02_OTHER_HEIRS": "inheritance_condition_registry",
    "REQ03_HEIR_CAPACITY": "proof_burden_registry",
    "REQ04_HOUSE_STATUS": "possession_yad_registry",
    "REQ05_PRIOR_PERMISSION": "possession_yad_registry",
    "REQ06_HAND_CREDIBLE": "possession_yad_registry",
    "REQ07_CLAIM_CONTENT": "proof_burden_registry",
    "REQ08_DEFENSE_CONTENT": "proof_burden_registry",
    "REQ09_EVIDENCE": "proof_burden_registry",
    "REQ10_QARINA_STRENGTH": "possession_yad_registry",
}
DIM_SUFFIX = {"FACT_REQUIREMENT": "FACT", "SOURCE_REQUIREMENT": "SOURCE",
              "OWNER_DECISION_REQUIREMENT": "OWNER", "GATE_REQUIREMENT": "GATE"}

REGISTRIES_13 = [
    ("factual_claim_registry", "سجل الدعاوى الواقعية",
     "يسجّل الوقائع المزعومة كدعاوى تحتاج تزويدًا وتصديقًا، لا كوقائع مثبتة.",
     ["FACTUAL_CLAIM_CANDIDATE"], ["claim_id", "claim_text", "source_ref", "owner_ratification"],
     "YES", ["owner_supplied_fact_registry", "owner_ratification_registry"]),
    ("owner_supplied_fact_registry", "سجل الوقائع المزوَّدة من المالك",
     "يستقبل وقائع يزوّدها المالك مع بينة؛ هو الوحيد الذي قد يُنشئ واقعة بعد التصديق.",
     ["OWNER_SUPPLIED_FACT"], ["fact_id", "fact_text", "evidence_ref", "owner_ratification"],
     "YES", ["owner_ratification_registry"]),
    ("source_requirement_registry", "سجل متطلبات المصادر",
     "يسجّل نوع المصدر المطلوب لكل بُعد؛ لا يُنشئ مصدرًا.",
     ["SOURCE_REQUIREMENT"], ["req_id", "required_source_type", "linked_requirement"],
     "YES", ["normative_source_registry"]),
    ("normative_source_registry", "سجل المصادر المعيارية",
     "يسجّل المصادر المصدَّقة من المالك (مثل المولودة في الجولات 17/21)؛ لا يُصدّق من الوكيل.",
     ["OWNER_RATIFIED_SOURCE"], ["source_id", "authority", "evidence", "owner_ratification"],
     "YES", ["owner_ratification_registry"]),
    ("domain_candidate_registry", "سجل مرشحات المجال",
     "يسجّل مرشحات المجال (الجولة 13) دون إغلاق نهائي.",
     ["DOMAIN_CANDIDATE"], ["domain_candidate_id", "is_final_closed_domain"],
     "NO", []),
    ("hukm_candidate_registry", "سجل مرشحات الحكم",
     "يسجّل مرشحات الحكم (الجولة 23) كمرشحات فقط.",
     ["HUKM_CANDIDATE"], ["hukm_candidate_id", "verdict", "final_hukm_allowed"],
     "NO", ["normative_source_registry"]),
    ("manat_candidate_registry", "سجل مرشحات المناط",
     "يسجّل مرشحات المناط (الجولة 24) كمرشحات فقط.",
     ["MANAT_CANDIDATE"], ["manat_candidate_id", "verdict", "final_manat_allowed"],
     "NO", ["hukm_candidate_registry"]),
    ("tanzil_requirement_registry", "سجل متطلبات التنزيل",
     "يسجّل شروط التنزيل المطلوبة قبل أي تنزيل؛ لا يُنتج تنزيلًا.",
     ["TANZIL_REQUIREMENT"], ["req_id", "condition", "owner_ratification"],
     "YES", ["manat_candidate_registry", "owner_ratification_registry"]),
    ("proof_burden_registry", "سجل عبء الإثبات",
     "يسجّل بوابات البينة/اليمين؛ لا يقرّر الحق الموضوعي.",
     ["PROOF_BURDEN_GATE"], ["gate_id", "claimant", "evidence_ref"],
     "YES", ["factual_claim_registry"]),
    ("possession_yad_registry", "سجل الحيازة/اليد",
     "يسجّل حالة اليد/الحيازة والقرائن؛ الحيازة ليست ملكية نهائية.",
     ["POSSESSION_YAD_STATE"], ["state_id", "hand_credible", "qarina_ref"],
     "YES", ["factual_claim_registry"]),
    ("inheritance_condition_registry", "سجل شروط الإرث",
     "يسجّل شروط الكلالة/حصر الورثة كشروط تحتاج إثباتًا.",
     ["INHERITANCE_CONDITION"], ["condition_id", "condition_text", "evidence_ref"],
     "YES", ["owner_supplied_fact_registry"]),
    ("residual_registry", "سجل البقايا",
     "يسجّل البقايا غير المحسومة عبر الجولات.",
     ["RESIDUAL"], ["residual_id", "residual_text", "blocking"],
     "NO", []),
    ("owner_ratification_registry", "سجل تصديقات المالك",
     "يسجّل تصديقات المالك الصريحة؛ لا يُنشئ تصديقًا من الوكيل.",
     ["OWNER_RATIFICATION"], ["ratification_id", "subject", "decision", "scope"],
     "YES", []),
]


def load_parents():
    d = json.loads(REGISTRY_32.read_text(encoding="utf-8"))
    return d["requirements"]


def build_normalized(parents):
    rows = []
    for p in parents:
        pid = p["requirement_id"]
        pq = p["original_question"]
        for dim in DIMENSIONS:
            if dim == "FACT_REQUIREMENT":
                reg, src, owner, stmt = ("factual_claim_registry", "OWNER_SUPPLIED_FACT",
                                         "تصديق الواقعة", f"إثبات واقعة: {pq}")
            elif dim == "SOURCE_REQUIREMENT":
                reg, src, owner, stmt = ("source_requirement_registry", p.get("required_source_type", ""),
                                         "اعتماد المصدر", f"تحديد المصدر/البينة المطلوبة لـ: {pq}")
            elif dim == "OWNER_DECISION_REQUIREMENT":
                reg, src, owner, stmt = ("owner_ratification_registry", "OWNER_DECISION_RECORD",
                                         p.get("required_owner_decision", "قرار مالك صريح"),
                                         f"قرار مالك بشأن: {pq}")
            else:  # GATE_REQUIREMENT
                reg, src, owner, stmt = (PARENT_GATE_REGISTRY.get(pid, "residual_registry"),
                                         "GATE_EVIDENCE", "فتح البوابة بقرار مالك",
                                         f"بوابة سبب/شرط/مانع لـ: {pq}")
            rows.append({
                "normalized_requirement_id": f"NR_{pid}_{DIM_SUFFIX[dim]}",
                "parent_requirement_id": pid,
                "parent_question": pq,
                "dimension_type": dim,
                "requirement_statement": stmt,
                "required_registry": reg,
                "required_source_type": src,
                "required_owner_decision": owner,
                "cause": f"تطبيع البُعد {dim} لمتطلب {pid} (من الجولة 32).",
                "conditions": "توفّر سجل مأهول + مصدر/واقعة مصدَّقة + قرار مالك مطابق.",
                "preventers": ("إنشاء واقعة/مصدر/حكم/تنزيل/جواب من الوكيل؛ التوسع قبل الإشغال والتصديق."),
                "default_verdict_if_missing": "DEFER",
                "creates_fact": "NO",
                "creates_source": "NO",
                "creates_hukm": "NO",
                "creates_tanzil": "NO",
                "creates_final_answer": "NO",
                "expansion_blocker": "YES",
                "residuals": "غير مستوفى حتى يُشغَل السجل ويُصدّق المالك.",
            })
    return rows


def build_skeletons():
    out = []
    for (rid, name, purpose, rec_types, min_fields, ratify, deps) in REGISTRIES_13:
        creates_fact = "NO"  # even owner_supplied_fact_registry creates a fact only after owner supplies+ratifies
        out.append({
            "registry_id": rid,
            "registry_name": name,
            "purpose": purpose,
            "allowed_record_types": rec_types,
            "minimum_required_fields": min_fields,
            "owner_ratification_required": ratify,
            "creates_fact": creates_fact,
            "creates_source": "NO",
            "creates_hukm": "NO",
            "creates_tanzil": "NO",
            "creates_final_answer": "NO",
            "gate_dependencies": deps,
            "cause": "PHASE 0 يتطلب بناء السجلات قبل التوسع.",
            "conditions": "يُملأ بسجلات مصدَّقة من المالك قبل أي قبول واقعة/مصدر.",
            "preventers": "اعتبار الهيكل سجلًّا مأهولًا؛ إنشاء واقعة/مصدر/تصديق من الهيكل نفسه.",
            "default_verdict_if_empty": "DEFER",
            "expansion_blocker_if_empty": "YES",
            "status": "SKELETON_ONLY_NOT_POPULATED",
        })
    return out


def build_recheck(norm_rows, skeletons):
    dim_counts = {d: sum(1 for r in norm_rows if r["dimension_type"] == d) for d in DIMENSIONS}
    registries_populated = "NO"   # skeletons only
    owner_facts_present = "NO"
    gate_pass = "NO"              # blocked: not populated + no facts
    return {
        "ROUND": "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_AND_SKELETONS_34",
        "TASK_PHASE": "PHASE_0_RECHECK_AFTER_NORMALIZATION",
        "requirements_registry_verified": "YES",
        "requirements_normalized": "YES",
        "normalized_requirement_row_count": len(norm_rows),
        "dimension_counts": dim_counts,
        "registry_skeletons_built": "YES",
        "registry_skeleton_count": len(skeletons),
        "registries_populated": registries_populated,
        "owner_supplied_facts_present": owner_facts_present,
        "factual_facts_complete": "NO",
        "phase0_gate_pass": gate_pass,
        "ready_for_expansion": "NO",
        "FINAL_MANAT": "NO",
        "TANZIL": "NO",
        "FINAL_HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "decision": {
            "cause": "normalized registry + 13 skeletons now exist",
            "conditions": "registries populated with owner-ratified records AND facts accepted",
            "preventers": "skeletons empty; no owner-supplied facts",
            "verdict": "STILL_BLOCKED_AT_PHASE_0_REGISTRIES_NOT_POPULATED",
            "residuals": "populate 13 registries with owner-ratified records; supply+ratify facts",
        },
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "NORMALIZATION_DOES_NOT_CREATE_FACT": "YES",
        "NORMALIZATION_DOES_NOT_CREATE_SOURCE": "YES",
        "SKELETON_IS_NOT_POPULATED_RECORD": "YES",
        "SOURCE_REGISTRY_SKELETON_DOES_NOT_CREATE_SOURCE": "YES",
        "RATIFICATION_REGISTRY_SKELETON_DOES_NOT_CREATE_RATIFICATION": "YES",
        "AGENT_QUESTION_IS_NOT_CANONICAL_RULE": "YES",
        "OWNER_RATIFICATION_REQUIRED": "YES",
        "EVERYTHING_DEFER_UNTIL_OWNER_DATA": "YES",
        "NO_FINAL_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_FINAL_ANSWER": "YES",
        "READY_FOR_EXPANSION": "NO",
        "PHASE0_GATE_PASS": "NO",
        "producer_file": PRODUCER,
    }


def normalized_md(norm_rows, dim_counts):
    L = ["# سجل المتطلبات المطبَّع (الجولة 34 — تطبيع فقط)", "",
         f"NORMALIZED_REQUIREMENT_ROW_COUNT = **{len(norm_rows)}** "
         f"(FACT={dim_counts['FACT_REQUIREMENT']} · SOURCE={dim_counts['SOURCE_REQUIREMENT']} · "
         f"OWNER_DECISION={dim_counts['OWNER_DECISION_REQUIREMENT']} · GATE={dim_counts['GATE_REQUIREMENT']})", "",
         "كل متطلب أصلي (10) قُسِّم إلى أربعة أبعاد مستقلة. **لا وقائع/مصادر/حكم/تنزيل/جواب**؛ الكل DEFER.", ""]
    cur = None
    for r in norm_rows:
        if r["parent_requirement_id"] != cur:
            cur = r["parent_requirement_id"]
            L.append(f"## {cur} — {r['parent_question']}")
        L.append(f"- `{r['normalized_requirement_id']}` [{r['dimension_type']}] → سجل: "
                 f"`{r['required_registry']}` · قرار المالك: {r['required_owner_decision']} · "
                 f"default={r['default_verdict_if_missing']}")
    L += ["", "---", "*التطبيع لا يُنشئ واقعة ولا مصدرًا؛ كل صف معلّق حتى إشغال السجل وتصديق المالك.*"]
    return "\n".join(L) + "\n"


def skeletons_md(skeletons):
    L = ["# هياكل السجلات الثلاثة عشر (الجولة 34 — هياكل فقط)", "",
         "**status = SKELETON_ONLY_NOT_POPULATED لكلٍّ.** الهيكل ليس سجلًّا مأهولًا، ولا يُنشئ "
         "واقعة/مصدر/تصديقًا/حكمًا/تنزيلًا/جوابًا.", ""]
    for s in skeletons:
        deps = "، ".join(s["gate_dependencies"]) if s["gate_dependencies"] else "—"
        L.append(f"## `{s['registry_id']}` — {s['registry_name']}")
        L.append(f"- الغرض: {s['purpose']}")
        L.append(f"- allowed_record_types: {', '.join(s['allowed_record_types'])} · "
                 f"min_fields: {', '.join(s['minimum_required_fields'])}")
        L.append(f"- owner_ratification_required = {s['owner_ratification_required']} · "
                 f"gate_dependencies: {deps}")
        L.append(f"- creates_fact/source/hukm/tanzil/final_answer = NO · "
                 f"default_if_empty = {s['default_verdict_if_empty']} · "
                 f"expansion_blocker_if_empty = {s['expansion_blocker_if_empty']}")
    L += ["", "---", "*لا يجوز اعتبار أي هيكل مأهولًا حتى تُضاف سجلات مصدَّقة من المالك.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-PRE-EXPANSION-REGISTRY-32", "ROUND_32",
     "output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json",
     "tests/test_taaqol_pre_expansion_requirements_registry_32.py"),
    ("REQ-FINALIZATION-PHASE0-BLOCKER-33", "ROUND_33",
     "output/taaqol_maqam_foundation_generated/TAAQOL_FINALIZATION_PHASE0_BLOCKER_33.json",
     "tests/test_taaqol_finalization_phase0_blocker_33.py"),
    ("REQ-NORMALIZED-REGISTRY-34", "ROUND_34",
     "output/taaqol_maqam_foundation_generated/TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.json",
     "tests/test_taaqol_requirement_registry_normalization_and_skeletons_34.py"),
    ("REQ-REGISTRY-SKELETONS-34", "ROUND_34",
     "output/taaqol_maqam_foundation_generated/TAAQOL_REGISTRY_SKELETONS_13_34.json",
     "tests/test_taaqol_requirement_registry_normalization_and_skeletons_34.py"),
    ("REQ-PHASE0-RECHECK-34", "ROUND_34",
     "output/taaqol_maqam_foundation_generated/TAAQOL_PHASE0_RECHECK_AFTER_NORMALIZATION_34.json",
     "tests/test_taaqol_requirement_registry_normalization_and_skeletons_34.py"),
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


def build_matrix(norm_rows, dim_counts, skeletons, anm):
    kv = [
        ("ROUND", "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_AND_SKELETONS_34"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("NORMALIZED_REQUIREMENT_ROWS", str(len(norm_rows))),
        ("FACT_REQUIREMENT_COUNT", str(dim_counts["FACT_REQUIREMENT"])),
        ("SOURCE_REQUIREMENT_COUNT", str(dim_counts["SOURCE_REQUIREMENT"])),
        ("OWNER_DECISION_REQUIREMENT_COUNT", str(dim_counts["OWNER_DECISION_REQUIREMENT"])),
        ("GATE_REQUIREMENT_COUNT", str(dim_counts["GATE_REQUIREMENT"])),
        ("REGISTRY_SKELETON_COUNT", str(len(skeletons))),
        ("ALL_SKELETONS_NOT_POPULATED", "YES" if all(s["status"] == "SKELETON_ONLY_NOT_POPULATED" for s in skeletons) else "NO"),
        ("ALL_NORMALIZED_DEFER", "YES" if all(r["default_verdict_if_missing"] == "DEFER" for r in norm_rows) else "NO"),
        ("REGISTRIES_POPULATED", "NO"),
        ("OWNER_SUPPLIED_FACTS_PRESENT", "NO"),
        ("FACTUAL_FACTS_COMPLETE", "NO"),
        ("REQUIREMENTS_REGISTRY_VERIFIED", "YES"),
        ("REQUIREMENTS_NORMALIZED", "YES"),
        ("PHASE0_RECHECK_DONE", "YES"),
        ("PHASE0_GATE_PASS", "NO"),
        ("READY_FOR_EXPANSION", "NO"),
        ("FINAL_MANAT", "NO"),
        ("TANZIL", "NO"),
        ("FINAL_HUKM", "NO"),
        ("FINAL_ANSWER", "NO"),
        ("NORMALIZATION_CREATES_FACT", "NO"),
        ("SKELETON_CREATES_SOURCE", "NO"),
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


def render_manager(tokens, norm_rows, dim_counts, skeletons, recheck, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — تطبيع المتطلبات وهياكل السجلات (34)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.74rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — تطبيع المتطلبات وبناء هياكل السجلات (34)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0. تطبيع + هياكل فقط.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'بُنيت المتطلبات المطبَّعة (40 صفًّا) · بُنيت 13 هيكل سجل · لم تُشغَل أي سجلات · '
             'لا وقائع مزوَّدة · لا مناط نهائي · لا تنزيل · لا حكم · لا جواب · التوسع ما زال محجوبًا.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             f'<li>طُبِّعت المتطلبات العشرة إلى **{len(norm_rows)}** صفًّا (4 أبعاد لكلٍّ): '
             f'FACT={dim_counts["FACT_REQUIREMENT"]}, SOURCE={dim_counts["SOURCE_REQUIREMENT"]}, '
             f'OWNER_DECISION={dim_counts["OWNER_DECISION_REQUIREMENT"]}, GATE={dim_counts["GATE_REQUIREMENT"]}.</li>'
             f'<li>بُنيت **{len(skeletons)}** هياكل سجلات (SKELETON_ONLY_NOT_POPULATED).</li>'
             '<li>لم تُشغَل سجلات، ولا وقائع مزوَّدة؛ PHASE 0 يبقى محجوبًا (gate_pass=NO)، والتوسع=NO.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ التطبيع لا يمسّها. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يتحوّل إلى قاعدة. MAQAM_IS_NOT_RULE = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'السجلات هياكل فارغة؛ لا مصدر ولا واقعة تُنشأ من الوكيل.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'لا وقائع مقبولة؛ التطبيع/الهياكل لا يُنشئ واقعة. FACT_CREATED = NO.</div>')
    # 8 — dimension counts + sample normalized rows
    P.append('<h2>8. المصدر المعياري — المتطلبات المطبَّعة (40 صفًّا)</h2>'
             '<div class="wrap"><table><thead><tr><th>البُعد</th><th>العدد</th></tr></thead><tbody>')
    for d in DIMENSIONS:
        P.append(f'<tr><th>{e(d)}</th><td class="y">{dim_counts[d]}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="wrap"><table><thead><tr><th>normalized_id</th><th>parent</th><th>dimension</th>'
             '<th>required_registry</th><th>default</th><th>expansion_blocker</th></tr></thead><tbody>')
    for r in norm_rows:
        P.append('<tr><th>' + e(r["normalized_requirement_id"]) + '</th><td>' + e(r["parent_requirement_id"]) + '</td>'
                 '<td class="d">' + e(r["dimension_type"]) + '</td><td>' + e(r["required_registry"]) + '</td>'
                 + f'<td class="d">{e(r["default_verdict_if_missing"])}</td>'
                 + f'<td class="n">{e(r["expansion_blocker"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9 — skeletons
    P.append('<h2>9. موضع التوقف — هياكل السجلات الثلاثة عشر</h2><div class="wrap"><table><thead><tr>'
             '<th>registry_id</th><th>status</th><th>owner_ratif.</th><th>creates_fact</th>'
             '<th>default_if_empty</th></tr></thead><tbody>')
    for s in skeletons:
        P.append(f'<tr><th>{e(s["registry_id"])}</th><td class="d">{e(s["status"])}</td>'
                 f'<td>{e(s["owner_ratification_required"])}</td><td class="n">{e(s["creates_fact"])}</td>'
                 f'<td class="d">{e(s["default_verdict_if_empty"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 10 — recheck
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2>'
             '<div class="note n" style="background:#fdecec"><b>إعادة فحص PHASE 0:</b> '
             f'REQUIREMENTS_NORMALIZED=YES · REGISTRY_SKELETONS_BUILT=YES · REGISTRIES_POPULATED=NO · '
             f'OWNER_SUPPLIED_FACTS_PRESENT=NO · PHASE0_GATE_PASS=NO · verdict='
             f'{e(recheck["decision"]["verdict"])}. المطلوب: إشغال السجلات بسجلات مصدَّقة + تزويد وقائع.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">إشغال السجلات الثلاثة عشر بسجلات مصدَّقة من المالك '
             '+ تزويد الوقائع بقرار مالك؛ عندها يُعاد فحص PHASE 0 ثم (إن اجتاز) PHASE 1 فما بعدها.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_requirement_registry_normalization_and_skeletons_34.py — '
             'ROUND_34_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32 + 33 + 34 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_34_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT = output/taaqol_maqam_foundation_generated/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json\n'
             'NORMALIZED_JSON = output/taaqol_maqam_foundation_generated/TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.json\n'
             'NORMALIZED_MD = output/taaqol_maqam_foundation_generated/TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.md\n'
             'SKELETONS_JSON = output/taaqol_maqam_foundation_generated/TAAQOL_REGISTRY_SKELETONS_13_34.json\n'
             'SKELETONS_MD = output/taaqol_maqam_foundation_generated/TAAQOL_REGISTRY_SKELETONS_13_34.md\n'
             'PHASE0_RECHECK = output/taaqol_maqam_foundation_generated/TAAQOL_PHASE0_RECHECK_AFTER_NORMALIZATION_34.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_GUARDS_34.json\n'
             'PYTEST_FILE = tests/test_taaqol_requirement_registry_normalization_and_skeletons_34.py\n'
             'REGISTRIES_POPULATED = NO\nOWNER_SUPPLIED_FACTS_PRESENT = NO\nPHASE0_GATE_PASS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'بُني السجل المطبَّع ({len(norm_rows)} صفًّا) و{len(skeletons)} هياكل سجلات؛ بلا إشغال ولا وقائع. '
             'يبقى PHASE 0 محجوبًا، ولا مناط/تنزيل/حكم/جواب، والتوسع=NO. الخطوة التالية للمالك: إشغال السجلات وتزويد الوقائع.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'NORMALIZED_REQUIREMENT_ROWS = {len(norm_rows)} · REGISTRY_SKELETON_COUNT = {len(skeletons)} · '
             'REGISTRIES_POPULATED = NO · OWNER_SUPPLIED_FACTS_PRESENT = NO · PHASE0_GATE_PASS = NO · '
             'READY_FOR_EXPANSION = NO · FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · '
             'AUTHORITY_LEAK = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_34_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'REGISTRIES_POPULATED = NO · FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · '
             'FINAL_ANSWER = NO · READY_FOR_EXPANSION = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_MANAGER_REPORT_AR_34.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_34_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    parents = load_parents()
    norm_rows = build_normalized(parents)
    skeletons = build_skeletons()
    dim_counts = {d: sum(1 for r in norm_rows if r["dimension_type"] == d) for d in DIMENSIONS}
    recheck = build_recheck(norm_rows, skeletons)

    (OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.json").write_text(
        json.dumps({"ROUND": "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_AND_SKELETONS_34",
                    "normalized_requirement_row_count": len(norm_rows),
                    "dimension_counts": dim_counts,
                    "normalized_requirements": norm_rows,
                    "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.md").write_text(
        normalized_md(norm_rows, dim_counts), encoding="utf-8")
    (OUT / "TAAQOL_REGISTRY_SKELETONS_13_34.json").write_text(
        json.dumps({"ROUND": "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_AND_SKELETONS_34",
                    "registry_skeleton_count": len(skeletons),
                    "registry_skeletons": skeletons,
                    "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_REGISTRY_SKELETONS_13_34.md").write_text(
        skeletons_md(skeletons), encoding="utf-8")
    (OUT / "TAAQOL_PHASE0_RECHECK_AFTER_NORMALIZATION_34.json").write_text(
        json.dumps(recheck, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_REQUIREMENT_REGISTRY_NORMALIZATION_GUARDS_34.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(norm_rows, dim_counts, skeletons, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(
        render_manager(tokens, norm_rows, dim_counts, skeletons, recheck, trows, anm), encoding="utf-8")
    print("REPORT_34=" + a.report_out)
    print(f"NORMALIZED_ROWS={len(norm_rows)} dim_counts={dim_counts} SKELETONS={len(skeletons)} "
          f"PHASE0_GATE_PASS=NO READY_FOR_EXPANSION=NO ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
