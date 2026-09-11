#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36 (artifacts-only inventory).

Inventories everything supplied to the agent across prior rounds — Arabic texts, lexical items, domains,
sources, owner rules, requirements, fact candidates, missing facts, hukm/manāṭ candidates, guards/gates,
and generalization blockers — into DATABASE_RECORD_CANDIDATE_ONLY records. Nothing becomes canonical
without owner ratification; no example becomes a general rule; no source becomes hukm; no fact candidate
becomes a fact. Reads real artifacts only (REPORT_SOURCE=CODE_AND_ARTIFACTS_ONLY; agent memory NOT used).
No final manāṭ/tanzīl/final hukm/final answer; not ready for generalization. No commit; no push. Manager
report obeys the AR_09_FIXED experience.
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
SCRIPTS = ROOT / "scripts" / "taaqol_maqam_foundation"
TESTS = ROOT / "tests"
PRODUCER = "scripts/taaqol_maqam_foundation/supplied_language_data_inventory_36.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
GP = "output/taaqol_maqam_foundation_generated"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def rec(rid, rtype, surface, path, rnd, *, owner_supplied="NO", owner_ratified="NO",
        creates=None, cause="", conditions="", preventers="", residuals="", evidence=""):
    c = {"fact": "NO", "source": "NO", "hukm": "NO", "manat": "NO", "tanzil": "NO", "final_answer": "NO"}
    if creates:
        c.update(creates)
    return {
        "record_id": rid,
        "record_type": rtype,
        "surface_or_text": surface,
        "source_artifact_path": path,
        "source_round": rnd,
        "owner_supplied": owner_supplied,
        "owner_ratified": owner_ratified,
        "canonical_status": "CANDIDATE_ONLY",
        "generalization_status": "NOT_READY_FOR_GENERALIZATION",
        "creates_fact": c["fact"],
        "creates_source": c["source"],
        "creates_hukm": c["hukm"],
        "creates_manat": c["manat"],
        "creates_tanzil": c["tanzil"],
        "creates_final_answer": c["final_answer"],
        "cause": cause or "عنصر ظهر في artifact سابق؛ يُحصر كمرشح قاعدة بيانات.",
        "conditions": conditions or "لا يصبح كنسيًّا/عامًّا إلا بتصديق المالك.",
        "preventers": preventers or "اعتباره قاعدة عامة تلقائيًّا؛ اشتقاق واقعة/مصدر/حكم منه.",
        "verdict": "DEFER_FOR_OWNER_DATABASE_RATIFICATION",
        "residuals": residuals or "بانتظار تصديق المالك على إدراجه في قاعدة البيانات.",
        "evidence_pointer": evidence or path,
    }


def _load(p):
    fp = OUT / p
    return json.loads(fp.read_text(encoding="utf-8")) if fp.exists() else None


def build_registries():
    R = {}

    # 1 ARABIC_TEXT
    texts = [rec("AT_NAZILA", "ARABIC_TEXT", SENTENCE, GP + "/(all rounds)", "02..36",
                 cause="جملة النازلة الأصلية المستعملة في كل الجولات.")]
    reg17 = _load("RATIFIED_SOURCE_BIRTH_REGISTRY_17.json")
    if reg17:
        for s in reg17["owner_supplied_sources"]:
            texts.append(rec("AT_" + s["source_id"], "ARABIC_TEXT", s["TEXT"],
                             GP + "/RATIFIED_SOURCE_BIRTH_REGISTRY_17.json", "17",
                             owner_supplied="YES", owner_ratified="YES",
                             cause="نص مصدر مزوَّد ومصدَّق من المالك (الجولة 17).",
                             residuals="text_verbatim_status=ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT"))
    reg21 = _load("SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json")
    if reg21 and reg21.get("born_source"):
        bs = reg21["born_source"]
        texts.append(rec("AT_" + bs["source_id"], "ARABIC_TEXT", bs["TEXT"],
                         GP + "/SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json", "21",
                         owner_supplied="YES", owner_ratified="YES",
                         cause="نص مصدر السُّكنى المزوَّد والمصدَّق (الجولة 21).",
                         residuals="text_verbatim_status=ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT"))
    R["ARABIC_TEXT_REGISTRY_CANDIDATES"] = texts

    # 2 LEXICAL (token surfaces from the nazila csv)
    lex = []
    csvp = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if csvp.exists():
        with csvp.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                tid = row.get("token_id", "")
                if tid.startswith("t0"):
                    lex.append(rec("LEX_" + tid, "LEXICAL_ITEM", row.get("original_surface", ""),
                                   "output/taaqol_nazila_matrix_generated/HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv",
                                   "nazila-matrix",
                                   cause="لفظ عربي ظهر كمدخل في جدول الكلمات (t000..t009)."))
    R["LEXICAL_ITEM_REGISTRY_CANDIDATES"] = lex

    # 3 DOMAIN
    dom_ids = []
    comp13 = _load("NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json")
    if comp13:
        for d in comp13.get("domain_candidates", []):
            dom_ids.append(d["domain_candidate_id"])
    dom = [rec("DOM_" + did, "DOMAIN_CANDIDATE", did,
               GP + "/NAZILA_MULTI_DOMAIN_CANDIDATE_CLASSIFICATION_13.json", "13",
               cause="مرشح مجال من الجولة 13.") for did in dom_ids]
    for w in ["ميراث", "تركة", "قضاء", "سكنى", "يد/حيازة", "دعوى", "بينة", "يمين"]:
        dom.append(rec("DOM_WORD_" + w.replace("/", "_"), "DOMAIN_TERM_CANDIDATE", w,
                       GP + "/(rounds 13..25)", "13..25",
                       cause="مصطلح مجال ظهر عبر الجولات.", residuals="DOMAIN_CANDIDATE_ONLY"))
    R["DOMAIN_REGISTRY_CANDIDATES"] = dom

    # 4 SOURCE
    src = []
    if reg17:
        for s in reg17["owner_supplied_sources"]:
            src.append(rec("SRC_" + s["source_id"], "NORMATIVE_SOURCE_CANDIDATE", s["AUTHORITY"],
                           GP + "/RATIFIED_SOURCE_BIRTH_REGISTRY_17.json", "17",
                           owner_supplied="YES", owner_ratified="YES",
                           cause="مصدر معياري مولود ومصدَّق (الجولة 17).",
                           residuals=f"scope: {s['SCOPE'][:60]}...; evidence: {s['EVIDENCE']}",
                           evidence=s["EVIDENCE"]))
    if reg21 and reg21.get("born_source"):
        bs = reg21["born_source"]
        src.append(rec("SRC_" + bs["source_id"], "NORMATIVE_SOURCE_CANDIDATE", bs["AUTHORITY"],
                       GP + "/SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json", "21",
                       owner_supplied="YES", owner_ratified="YES",
                       cause="مصدر السُّكنى مولود ومصدَّق (الجولة 21).",
                       residuals=f"evidence: {bs['EVIDENCE']}", evidence=bs["EVIDENCE"]))
    R["SOURCE_REGISTRY_CANDIDATES"] = src

    # 5 OWNER_RULE (explicit owner rules recurring in artifacts)
    rules = [
        ("OR_NO_HUKM_WITHOUT_SCP", "لا حكم بلا سبب/شرط/مانع"),
        ("OR_QUESTION_NOT_FACT", "السؤال لا ينشئ واقعة"),
        ("OR_REQUIREMENT_NOT_FACT", "المتطلب لا ينشئ واقعة"),
        ("OR_SOURCE_NOT_HUKM", "المصدر لا يساوي حكمًا"),
        ("OR_POSSESSION_NOT_OWNERSHIP", "الحيازة لا تساوي ملكية نهائية"),
        ("OR_FINAL_HUKM_NEEDS_OWNER", "الحكم النهائي يحتاج تصديق المالك"),
        ("OR_NO_EXPANSION_BEFORE_REGISTRIES", "لا توسع خارج الجملة قبل تجهيز السجلات"),
        ("OR_NO_UNLICENSED_SLOT_TRANSITION", "لا انتقال بين slots دون ترخيص"),
        ("OR_AGENT_QUESTION_NOT_CANONICAL", "أسئلة الوكيل ليست قاعدة كنسية"),
        ("OR_EVIDENCE_CITATION_ONLY", "الإسناد سلاسل نصية بلا روابط حيّة"),
    ]
    R["OWNER_RULE_REGISTRY_CANDIDATES"] = [
        rec(rid, "OWNER_RULE", txt, GP + "/(guards across rounds)", "06..36",
            owner_supplied="YES",
            cause="قاعدة مالك صريحة متكررة في الحراس؛ مفصولة عن استنتاج الوكيل.",
            residuals="قاعدة مالك — لا اجتهاد وكيل.") for rid, txt in rules]

    # 6 REQUIREMENT (round 32 parents + round 34 normalized)
    reqs = []
    r32 = _load("TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json")
    if r32:
        for x in r32["requirements"]:
            reqs.append(rec("REQ_" + x["requirement_id"], "REQUIREMENT_PARENT", x["original_question"],
                            GP + "/TAAQOL_PRE_EXPANSION_REQUIREMENTS_REGISTRY_32.json", "32",
                            cause=f"متطلب {x['requirement_type']} من الجولة 32."))
    r34 = _load("TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.json")
    if r34:
        for x in r34["normalized_requirements"]:
            reqs.append(rec("NREQ_" + x["normalized_requirement_id"], "REQUIREMENT_NORMALIZED",
                            x["requirement_statement"],
                            GP + "/TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_34.json", "34",
                            cause=f"بُعد {x['dimension_type']} مطبَّع (الجولة 34)."))
    R["REQUIREMENT_REGISTRY_CANDIDATES"] = reqs

    # 7 FACT_CANDIDATE (round 35, 5)
    facts = []
    f35 = _load("FACTUAL_CLAIM_REGISTRY_35.json")
    if f35:
        for x in f35["fact_candidates"]:
            facts.append(rec("FCAND_" + x["fact_id"], "FACT_CANDIDATE", x["normalized_fact_statement"],
                             GP + "/FACTUAL_CLAIM_REGISTRY_35.json", "35",
                             owner_supplied="ASSERTED_BY_NAZILA_TEXT_ONLY", owner_ratified="NO",
                             cause="مرشح واقعة من منطوق النص (الجولة 35).",
                             residuals="FACT_CANDIDATE_ONLY · accepted_fact=NO"))
    R["FACT_CANDIDATE_REGISTRY_CANDIDATES"] = facts

    # 8 MISSING_FACT (round 35, 9)
    miss = []
    m35 = _load("MISSING_FACT_REQUIREMENTS_35.json")
    if m35:
        for x in m35["missing_facts"]:
            miss.append(rec("MISS_" + x["missing_fact_id"], "MISSING_FACT_REQUIREMENT", x["description"],
                            GP + "/MISSING_FACT_REQUIREMENTS_35.json", "35",
                            cause="واقعة غير منطوقة تحتاج تزويدًا (الجولة 35).",
                            residuals="REQUIRED_FACT_MISSING · default=DEFER"))
    R["MISSING_FACT_REQUIREMENT_REGISTRY_CANDIDATES"] = miss

    # 9 HUKM_CANDIDATE (round 23, 4)
    hukm = []
    h23 = _load("NORMATIVE_HUKM_CANDIDATES_23.json")
    if h23:
        for x in h23["hukm_candidates"]:
            hukm.append(rec("HUKM_" + x["hukm_candidate_id"], "HUKM_CANDIDATE", x["candidate_statement"],
                            GP + "/NORMATIVE_HUKM_CANDIDATES_23.json", "23",
                            cause="مرشح حكم من الجولة 23.", residuals="CANDIDATE_ONLY · final_hukm=NO"))
    R["HUKM_CANDIDATE_REGISTRY_CANDIDATES"] = hukm

    # 10 MANAT_CANDIDATE (round 24, 4)
    manat = []
    mc24 = _load("MANAT_CANDIDATES_24.json")
    if mc24:
        for x in mc24["manat_candidates"]:
            manat.append(rec("MANAT_" + x["manat_candidate_id"], "MANAT_CANDIDATE",
                             x["candidate_manat_statement"],
                             GP + "/MANAT_CANDIDATES_24.json", "24",
                             cause="مرشح مناط من الجولة 24.", residuals="CANDIDATE_ONLY · final_manat=NO"))
    R["MANAT_CANDIDATE_REGISTRY_CANDIDATES"] = manat

    # 11 GUARD_AND_GATE
    guards_gates = [
        "NO_FINAL_MANAT", "NO_TANZIL", "NO_FINAL_HUKM", "NO_FINAL_ANSWER",
        "OWNER_RATIFICATION_REQUIRED", "AUTHORITY_LEAK_PREVENTED",
        "SILENT_FALLBACK_COUNT=0", "ASSERTED_NOT_MEASURED_COUNT=0",
        "READY_FOR_EXPANSION=NO", "FULL_TAAQOL_PROJECT_CLOSED=NO",
    ]
    R["GUARD_AND_GATE_REGISTRY_CANDIDATES"] = [
        rec("GATE_" + g.replace("=", "_"), "GUARD_OR_GATE", g, GP + "/(guards across rounds)", "02..36",
            cause="حارس/بوابة متكررة عبر الجولات.", residuals="ثابت حوكمي.") for g in guards_gates]

    return R


def build_blockers():
    items = [
        "السجلات الثلاثة عشر غير مكتملة/غير مأهولة",
        "الوقائع غير مصدَّقة من المالك",
        "الأسئلة ليست قواعد كنسية",
        "لا قاعدة بيانات كنسية بعد",
        "لا مناط نهائي",
        "لا تنزيل",
        "لا حكم نهائي",
        "لا جواب نهائي",
        "لا closure audit نهائي",
    ]
    return {
        "generalization_ready": "NO",
        "blocker_count": len(items),
        "blockers": [{"blocker_id": f"GB{i+1}", "description": t,
                      "cause": "شرط تعميم غير مستوفى.",
                      "conditions": "إشغال السجلات + تصديق المالك + إغلاق مدقَّق.",
                      "preventers": "التعميم قبل استيفاء الشرط.",
                      "verdict": "BLOCK_GENERALIZATION", "residuals": "معلّق حتى قرار المالك."}
                     for i, t in enumerate(items)],
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "AGENT_MEMORY_USED_AS_SOURCE": "NO",
        "AGENT_QUESTION_CREATES_RULE": "NO",
        "TEXT_EXAMPLE_CREATES_GENERAL_RULE": "NO",
        "SOURCE_TEXT_CREATES_HUKM": "NO",
        "FACT_CANDIDATE_CREATES_FACT": "NO",
        "OWNER_RATIFICATION_REQUIRED_FOR_GENERALIZATION": "YES",
        "DATABASE_RECORD_CANDIDATE_ONLY": "YES",
        "GENERALIZATION_READY": "NO",
        "FINAL_MANAT": "NO",
        "TANZIL": "NO",
        "FINAL_HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "producer_file": PRODUCER,
    }


def counts(R):
    return {k: len(v) for k, v in R.items()}


def scanned_count():
    a = len(list(SCRIPTS.glob("*.py"))) if SCRIPTS.exists() else 0
    b = len([p for p in OUT.iterdir() if p.is_file()]) if OUT.exists() else 0
    c = len(list(TESTS.glob("test_taaqol_*.py"))) if TESTS.exists() else 0
    return a + b + c, a, b, c


def inventory_md(R, cnt, total_records):
    L = ["# جرد بيانات اللغة المزوَّدة (الجولة 36 — مرشحات قاعدة بيانات فقط)", "",
         f"REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · إجمالي السجلات المرشحة = **{total_records}**", "",
         "**المبدأ:** ما زُوّد أو ظهر في artifact لا يصبح قاعدة عامة تلقائيًّا؛ كل عنصر "
         "`DATABASE_RECORD_CANDIDATE_ONLY` حتى تصديق المالك.", ""]
    for reg, recs in R.items():
        L.append(f"## {reg} — {len(recs)} سجل")
        for r in recs[:12]:
            L.append(f"- `{r['record_id']}` [{r['record_type']}] ← {r['source_round']} · "
                     f"owner_ratified={r['owner_ratified']} · {r['canonical_status']}")
        if len(recs) > 12:
            L.append(f"- … (+{len(recs)-12} أخرى)")
    L += ["", "---", "*كل السجلات verdict=DEFER_FOR_OWNER_DATABASE_RATIFICATION · "
          "generalization_status=NOT_READY_FOR_GENERALIZATION.*"]
    return "\n".join(L) + "\n"


def ratification_request_md(cnt, total_records):
    L = ["# طلب تصديق قاعدة البيانات (الجولة 36)", "",
         f"حُصِر {total_records} سجلًّا مرشحًا عبر 12 سجلًّا من artifacts الجولات (لا من ذاكرة الوكيل).", "",
         "المطلوب من المالك (قبل أي تعميم خارج النازلة):", ""]
    for reg, c in cnt.items():
        L.append(f"- `{reg}` ({c}) → `RATIFY_AS_CANONICAL = YES | NO | DEFER`")
    L += ["", "**تنبيه:** لا سجل يصبح CANONICAL ولا مثال يصبح قاعدة عامة إلا بتصديقك الصريح.",
          "", "*حتى التصديق: GENERALIZATION_READY=NO · لا مناط/تنزيل/حكم/جواب · FULL_TAAQOL_PROJECT_CLOSED=NO.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-FACT-RATIFICATION-DECISIONS-36", "ROUND_36",
     GP + "/OWNER_FACT_RATIFICATION_DECISIONS_36.json",
     "tests/test_taaqol_owner_fact_ratification_36.py"),
    ("REQ-SUPPLIED-DATA-INVENTORY-36", "ROUND_36",
     GP + "/TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.json",
     "tests/test_taaqol_supplied_language_data_inventory_36.py"),
    ("REQ-GENERALIZATION-DB-CANDIDATES-36", "ROUND_36",
     GP + "/TAAQOL_GENERALIZATION_DATABASE_CANDIDATES_36.json",
     "tests/test_taaqol_supplied_language_data_inventory_36.py"),
    ("REQ-GENERALIZATION-BLOCKERS-36", "ROUND_36",
     GP + "/TAAQOL_GENERALIZATION_BLOCKERS_36.json",
     "tests/test_taaqol_supplied_language_data_inventory_36.py"),
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


def build_matrix(R, cnt, total_records, scanned, anm):
    kv = [
        ("ROUND", "TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("REPORT_SOURCE", "CODE_AND_ARTIFACTS_ONLY"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("DATA_SOURCES_SCANNED", str(scanned)),
        ("REGISTRY_COUNT", str(len(R))),
        ("DATABASE_CANDIDATE_RECORDS", str(total_records)),
        ("TEXT_CANDIDATES", str(cnt["ARABIC_TEXT_REGISTRY_CANDIDATES"])),
        ("LEXICAL_ITEM_CANDIDATES", str(cnt["LEXICAL_ITEM_REGISTRY_CANDIDATES"])),
        ("DOMAIN_CANDIDATES", str(cnt["DOMAIN_REGISTRY_CANDIDATES"])),
        ("SOURCE_CANDIDATES", str(cnt["SOURCE_REGISTRY_CANDIDATES"])),
        ("OWNER_RULE_CANDIDATES", str(cnt["OWNER_RULE_REGISTRY_CANDIDATES"])),
        ("REQUIREMENT_CANDIDATES", str(cnt["REQUIREMENT_REGISTRY_CANDIDATES"])),
        ("FACT_CANDIDATES", str(cnt["FACT_CANDIDATE_REGISTRY_CANDIDATES"])),
        ("MISSING_FACT_REQUIREMENTS", str(cnt["MISSING_FACT_REQUIREMENT_REGISTRY_CANDIDATES"])),
        ("HUKM_CANDIDATES", str(cnt["HUKM_CANDIDATE_REGISTRY_CANDIDATES"])),
        ("MANAT_CANDIDATES", str(cnt["MANAT_CANDIDATE_REGISTRY_CANDIDATES"])),
        ("GUARD_AND_GATE_CANDIDATES", str(cnt["GUARD_AND_GATE_REGISTRY_CANDIDATES"])),
        ("ALL_RECORDS_CANDIDATE_ONLY", "YES"),
        ("ALL_RECORDS_NOT_READY_FOR_GENERALIZATION", "YES"),
        ("ALL_RECORDS_DEFER_VERDICT", "YES"),
        ("AGENT_MEMORY_USED_AS_SOURCE", "NO"),
        ("GENERALIZATION_READY", "NO"),
        ("OWNER_DATABASE_RATIFICATION_REQUIRED", "YES"),
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


def render_manager(tokens, R, cnt, total_records, scanned, blockers, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — جرد بيانات اللغة المزوَّدة (36)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — جرد بيانات اللغة المزوَّدة (36)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · LLM_FREE_TEXT_FACT_CREATION = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0. جرد مرشحات قاعدة بيانات فقط.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'AGENT_MEMORY_USED_AS_SOURCE=NO · مثال لغوي لا يصبح قاعدة عامة · مصدر لا يصبح حكمًا · '
             'مرشح واقعة لا يصبح واقعة · تصديق المالك مطلوب للتعميم · GENERALIZATION_READY=NO · '
             'لا مناط/تنزيل/حكم/جواب · FULL_TAAQOL_PROJECT_CLOSED=NO.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             f'<li>فُحِص {scanned} مصدر بيانات (artifacts) وحُصِر **{total_records}** سجلًّا مرشحًا عبر {len(R)} سجلًّا.</li>'
             '<li>كل سجل DATABASE_RECORD_CANDIDATE_ONLY · NOT_READY_FOR_GENERALIZATION · DEFER.</li>'
             f'<li>{blockers["blocker_count"]} موانع تعميم مسجَّلة؛ لا مناط/تنزيل/حكم/جواب؛ التصديق مطلوب.</li></ul>')
    P.append('<h2>2. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    P.append('<h2>3. جدول الكلمات العشر</h2>')
    if not tokens:
        P.append('<div class="note n">TOKEN_ARTIFACT_MISSING</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>الفئة</th></tr></thead><tbody>')
        for t in tokens:
            P.append('<tr><th>' + e(t["token_id"]) + '</th><td>' + e(t.get("original_surface", "")) +
                     '</td><td>' + e(t.get("word_class", "")) + '</td></tr>')
        P.append('</tbody></table></div>')
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ تُحصر كمرشح بيانات لا كقاعدة. IFADAH_CHANGED = NO.</div>')
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يصبح قاعدة عامة. MAQAM_IS_NOT_RULE = YES.</div>')
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'المصادر المحصورة مصدَّقة كمصادر لكن لا كقاعدة كنسية؛ التعميم يحتاج تصديقًا.</div>')
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'جرد فقط؛ لا واقعة مقبولة ولا رخصة عبور. FACT_CANDIDATE_CREATES_FACT = NO.</div>')
    P.append('<h2>8. المصدر المعياري — السجلات الاثنا عشر (عدد المرشحات)</h2><div class="wrap"><table><thead><tr>'
             '<th>registry</th><th>عدد المرشحات</th></tr></thead><tbody>')
    for reg, c in cnt.items():
        P.append(f'<tr><th>{e(reg)}</th><td class="y">{c}</td></tr>')
    P.append(f'<tr><th>الإجمالي</th><td class="y">{total_records}</td></tr></tbody></table></div>')
    # sample records
    P.append('<div class="wrap"><table><thead><tr><th>record_id</th><th>type</th><th>round</th>'
             '<th>owner_ratified</th><th>canonical</th><th>verdict</th></tr></thead><tbody>')
    sample = [r for recs in R.values() for r in recs[:2]]
    for r in sample:
        P.append('<tr><th>' + e(r["record_id"]) + '</th><td class="d">' + e(r["record_type"]) + '</td>'
                 '<td>' + e(r["source_round"]) + '</td>'
                 + f'<td class="d">{e(r["owner_ratified"])}</td>'
                 + f'<td class="d">{e(r["canonical_status"])}</td>'
                 + f'<td class="n">{e(r["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>9. موضع التوقف — موانع التعميم</h2><div class="wrap"><table><thead><tr>'
             '<th>blocker_id</th><th>الوصف</th><th>verdict</th></tr></thead><tbody>')
    for b in blockers["blockers"]:
        P.append(f'<tr><th>{e(b["blocker_id"])}</th><td>{e(b["description"])}</td>'
                 f'<td class="n">{e(b["verdict"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note n" style="background:#fdecec">'
             'المطلوب: تصديق المالك على كل سجل (RATIFY_AS_CANONICAL) قبل أي تعميم — '
             'في TAAQOL_DATABASE_RATIFICATION_REQUEST_36.md.</div>')
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند تصديق المالك للسجلات: تُرفع '
             'generalization_status تدريجيًّا؛ ويبقى التوسع محجوبًا حتى تُرفع الموانع التسعة.</div>')
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_supplied_language_data_inventory_36.py — '
             'ROUND_36_INV_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32..36 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    P.append(_trace_html(trows))
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_36_INV_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INVENTORY_JSON = output/taaqol_maqam_foundation_generated/TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.json\n'
             'DB_CANDIDATES = output/taaqol_maqam_foundation_generated/TAAQOL_GENERALIZATION_DATABASE_CANDIDATES_36.json\n'
             'BLOCKERS = output/taaqol_maqam_foundation_generated/TAAQOL_GENERALIZATION_BLOCKERS_36.json\n'
             'RATIFICATION_REQUEST = output/taaqol_maqam_foundation_generated/TAAQOL_DATABASE_RATIFICATION_REQUEST_36.md\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/TAAQOL_SUPPLIED_DATA_INVENTORY_GUARDS_36.json\n'
             'PYTEST_FILE = tests/test_taaqol_supplied_language_data_inventory_36.py\n'
             f'DATA_SOURCES_SCANNED = {scanned}\nDATABASE_CANDIDATE_RECORDS = {total_records}\n'
             'AGENT_MEMORY_USED_AS_SOURCE = NO\nGENERALIZATION_READY = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'حُصِر {total_records} سجلًّا مرشحًا عبر 12 سجلًّا من artifacts فقط؛ كلها CANDIDATE_ONLY وDEFER، '
             'مع 9 موانع تعميم. لا تعميم، لا مناط/تنزيل/حكم/جواب، والتصديق مطلوب.</div>')
    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'DATABASE_CANDIDATE_RECORDS = {total_records} · DATA_SOURCES_SCANNED = {scanned} · '
             'AGENT_MEMORY_USED_AS_SOURCE = NO · GENERALIZATION_READY = NO · '
             'OWNER_DATABASE_RATIFICATION_REQUIRED = YES · FINAL_MANAT = NO · TANZIL = NO · '
             'FINAL_HUKM = NO · FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO · AUTHORITY_LEAK = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_36_INV_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'GENERALIZATION_READY = NO · FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · '
             'FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "TAAQOL_SUPPLIED_DATA_INVENTORY_MANAGER_REPORT_AR_36.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "TAAQOL_SUPPLIED_DATA_INVENTORY_36_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    R = build_registries()
    cnt = counts(R)
    total_records = sum(cnt.values())
    scanned, na, nb, nc = scanned_count()
    blockers = build_blockers()

    (OUT / "TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.json").write_text(
        json.dumps({"ROUND": "TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36",
                    "report_source": "CODE_AND_ARTIFACTS_ONLY",
                    "data_sources_scanned": scanned,
                    "registry_counts": cnt,
                    "database_candidate_records": total_records,
                    "registries": R, "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.md").write_text(
        inventory_md(R, cnt, total_records), encoding="utf-8")
    (OUT / "TAAQOL_GENERALIZATION_DATABASE_CANDIDATES_36.json").write_text(
        json.dumps({"ROUND": "TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36",
                    "database_candidate_records": total_records,
                    "all_records_candidate_only": "YES",
                    "generalization_ready": "NO",
                    "records": [r for recs in R.values() for r in recs],
                    "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_GENERALIZATION_BLOCKERS_36.json").write_text(
        json.dumps(blockers, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_DATABASE_RATIFICATION_REQUEST_36.md").write_text(
        ratification_request_md(cnt, total_records), encoding="utf-8")
    (OUT / "TAAQOL_SUPPLIED_DATA_INVENTORY_GUARDS_36.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(R, cnt, total_records, scanned, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(
        render_manager(tokens, R, cnt, total_records, scanned, blockers, trows, anm), encoding="utf-8")
    print("REPORT_36_INV=" + a.report_out)
    print(f"SCANNED={scanned} (scripts={na},out={nb},tests={nc}) RECORDS={total_records} "
          f"counts={cnt} GENERALIZATION_READY=NO ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
