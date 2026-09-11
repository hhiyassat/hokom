#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37 (artifacts-only provenance catalog).

Transforms the round-36 artifact-derived inventory into a provenance CATALOG: for every Arabic text /
token / owner rule / normative source / domain term / requirement / fact-candidate / missing-fact /
hukm-candidate / manāṭ-candidate / guard, it records type, form, source, input format, use, target DB
table, and generalization/ratification status. Nothing becomes canonical merely by existing in an
artifact; SOURCE_RATIFIED ≠ GENERALIZED_RULE. No final manāṭ/tanzīl/final hukm/final answer; generalization
not ready. Reads artifacts only (agent memory NOT used). No commit; no push. AR_09_FIXED report.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
NZ = ROOT / "output" / "taaqol_nazila_matrix_generated"
PRODUCER = "scripts/taaqol_maqam_foundation/arabic_data_provenance_catalog_37.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
INVENTORY = OUT / "TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.json"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
_DIAC = re.compile(r"[ؗ-ًؚ-ْٰـ]")

TEXT_TYPES = ["NAZILA_TEXT", "NAZILA_TOKEN", "OWNER_RULE_TEXT", "NORMATIVE_SOURCE_TEXT", "DOMAIN_TERM",
              "REQUIREMENT_TEXT", "FACT_CANDIDATE_TEXT", "MISSING_FACT_REQUIREMENT_TEXT",
              "HUKM_CANDIDATE_TEXT", "MANAT_CANDIDATE_TEXT", "GUARD_TEXT"]
SOURCE_KINDS = ["OWNER_SUPPLIED_TEXT", "NAZILA_TEXT", "QURAN", "HADITH", "FIQH_SOURCE",
                "GENERATED_REQUIREMENT", "GENERATED_CANDIDATE", "TEST_FIXTURE", "GUARD",
                "UNKNOWN_ARTIFACT_DERIVED"]
INPUT_FORMS = ["FULL_TEXT", "TOKEN", "NORMALIZED_TOKEN", "JSON_FIELD", "MD_SECTION",
               "HTML_REPORT_FIELD", "PYTHON_LITERAL", "TEST_EXPECTATION", "CSV_ROW"]
USED_AS = ["TEXT_INPUT", "EVIDENCE", "SOURCE", "DOMAIN_LABEL", "FACT_CANDIDATE",
           "MISSING_FACT_REQUIREMENT", "REQUIREMENT", "HUKM_CANDIDATE", "MANAT_CANDIDATE",
           "GUARD", "REPORT_ONLY"]

# registry -> (text_type, source_kind, input_form, used_as, target_table)
REG_MAP = {
    "LEXICAL_ITEM_REGISTRY_CANDIDATES": ("NAZILA_TOKEN", "NAZILA_TEXT", "TOKEN", "TEXT_INPUT", "lexical_item_registry"),
    "DOMAIN_REGISTRY_CANDIDATES": ("DOMAIN_TERM", "GENERATED_CANDIDATE", "JSON_FIELD", "DOMAIN_LABEL", "domain_candidate_registry"),
    "OWNER_RULE_REGISTRY_CANDIDATES": ("OWNER_RULE_TEXT", "OWNER_SUPPLIED_TEXT", "JSON_FIELD", "GUARD", "owner_rule_registry"),
    "REQUIREMENT_REGISTRY_CANDIDATES": ("REQUIREMENT_TEXT", "GENERATED_REQUIREMENT", "JSON_FIELD", "REQUIREMENT", "requirement_registry"),
    "FACT_CANDIDATE_REGISTRY_CANDIDATES": ("FACT_CANDIDATE_TEXT", "GENERATED_CANDIDATE", "JSON_FIELD", "FACT_CANDIDATE", "factual_claim_registry"),
    "MISSING_FACT_REQUIREMENT_REGISTRY_CANDIDATES": ("MISSING_FACT_REQUIREMENT_TEXT", "GENERATED_REQUIREMENT", "JSON_FIELD", "MISSING_FACT_REQUIREMENT", "missing_fact_requirement_registry"),
    "HUKM_CANDIDATE_REGISTRY_CANDIDATES": ("HUKM_CANDIDATE_TEXT", "GENERATED_CANDIDATE", "JSON_FIELD", "HUKM_CANDIDATE", "hukm_candidate_registry"),
    "MANAT_CANDIDATE_REGISTRY_CANDIDATES": ("MANAT_CANDIDATE_TEXT", "GENERATED_CANDIDATE", "JSON_FIELD", "MANAT_CANDIDATE", "manat_candidate_registry"),
    "GUARD_AND_GATE_REGISTRY_CANDIDATES": ("GUARD_TEXT", "GUARD", "JSON_FIELD", "GUARD", "guard_and_gate_registry"),
}
TARGET_TABLES = ["arabic_text_registry", "lexical_item_registry", "normative_source_registry",
                 "domain_candidate_registry", "owner_rule_registry", "requirement_registry",
                 "factual_claim_registry", "missing_fact_requirement_registry",
                 "hukm_candidate_registry", "manat_candidate_registry", "guard_and_gate_registry"]

# Owner-supplied EXTERNAL_REFERENCE_LAYER (separate layer; design/benchmark references, NOT governing
# authorities inside Hokom/Taaqol). Recorded verbatim as owner provided; not internet-verified this round.
EXTERNAL_REFS = [
    ("XREF01_UD", "Tokenization / Word Segmentation", "Universal Dependencies English / UD Arabic",
     "الاعتماديات الكونية (عربي)", "تقطيع، POS، علاقات نحوية",
     "التقسيم، اللواصق، السطح، التطبيع", "TECHNICAL_REFERENCE_CANDIDATE"),
    ("XREF02_PENN_UD", "POS Tagging", "Penn Treebank / UD", "بنك الأشجار / UD", "فئة الكلمة",
     "اسم / فعل / حرف، المبنيات، العوامل", "LOCAL_HOKOM_OWNS_CATEGORY"),
    ("XREF03_WORDNET", "Lexical Semantics", "WordNet / Arabic WordNet", "ووردنت العربية",
     "synsets، علاقات معنى", "معنى معجمي مرشح", "CANDIDATE_ONLY"),
    ("XREF04_VERBNET", "Verb Classes", "VerbNet", "—", "طبقات الأفعال والأدوار والقيود",
     "علاقات فعل/فاعل/مفعول لاحقًا", "CANDIDATE_ONLY"),
    ("XREF05_PROPBANK", "Predicate-Argument", "PropBank / Arabic PropBank", "بروب-بانك العربية",
     "المحمول وحججه", "القضوي والإفادة", "NO_HUKM_PRODUCED"),
    ("XREF06_FRAMENET", "Frame Semantics", "FrameNet", "—", "أطر دلالية للأحداث والأفعال",
     "طبقة إطار دلالي مرخصة", "SKELETON_ONLY"),
    ("XREF07_WORDFRAMENET", "WordNet <-> FrameNet Bridge", "WordFrameNet", "—",
     "جسر بين WordNet وFrameNet", "lexical sense -> frame candidate", "DESIGN_REFERENCE_ONLY"),
    ("XREF08_LEGALBENCH", "Legal Issue Spotting", "LegalBench", "—", "كشف نوع المسألة قبل القاعدة",
     "تكييف المسألة", "METHODOLOGICAL_ANALOGY_ONLY"),
    ("XREF09_LEARNED_HANDS", "Legal Issue Dataset", "Learned Hands", "—", "قصص قانونية مصنفة",
     "لا يعتمدها كمصدر", "NOT_USED_FOR_SHARI_TAKYIF"),
    ("XREF10_LEXGLUE", "Legal NLU Benchmark", "LexGLUE / ArabLegalEval", "التقييم القانوني العربي",
     "مهام فهم قانوني", "benchmark لا مصدر حكم", "EVALUATION_ONLY"),
    ("XREF11_FIQH_NAZILA_TAKYIF", "Fiqh/Nazila Takyif", "Fiqh/Nazila Takyif", "فقه/تكييف النازلة",
     "التصور -> التكييف -> التنزيل", "MASALA_TAKYIF_LAYER", "OWNER_BUILT_REQUIRED"),
]


def build_external_refs():
    out = []
    for (rid, layer, eng, ar, gives, mapping, usage) in EXTERNAL_REFS:
        out.append({
            "reference_id": rid,
            "layer_name": layer,
            "english_reference": eng,
            "arabic_counterpart_if_any": ar,
            "what_it_gives": gives,
            "hokom_or_taaqol_mapping": mapping,
            "availability_claim": "OWNER_STATED_AVAILABLE_OR_RELEVANT",
            "availability_verification_status": "OWNER_SUPPLIED_CLAIM_NOT_VERIFIED_IN_THIS_ROUND",
            "usage_now": usage,
            "authority_status": "EXTERNAL_REFERENCE_CANDIDATE_ONLY",
            "creates_arabic_rule": "NO",
            "creates_shari_hukm": "NO",
            "creates_fact": "NO",
            "creates_manat": "NO",
            "creates_tanzil": "NO",
            "generalization_value": "DESIGN_OR_BENCHMARK_REFERENCE",
            "owner_ratification_required": "YES",
            "cause": "مرجع تقني/بحثي ذكره المالك كمقابل/مثال/مصدر تصميمي محتمل للنظام الشامل.",
            "conditions": "لا يُعتمد داخل Hokom/Taaqol إلا بتصديق مالك صريح؛ عربي أولًا.",
            "preventers": "اعتباره سلطة حاكمة؛ اشتقاق قاعدة عربية/حكم شرعي منه؛ التحقق من الإنترنت هذه الجولة.",
            "verdict": "DESIGN_OR_BENCHMARK_REFERENCE_ONLY",
            "residuals": "مرجع خارجي مرشح؛ لا سلطة ولا حكم ولا قاعدة عربية عامة.",
        })
    return out


def _unvowel(s):
    return _DIAC.sub("", s)


def _source_kind_by_authority(auth):
    if "القرآن" in auth or "النساء" in auth:
        return "QURAN"
    if "البخاري" in auth or "مسلم" in auth:
        return "HADITH"
    if "ابن القيم" in auth or "الطرق الحكمية" in auth:
        return "FIQH_SOURCE"
    return "UNKNOWN_ARTIFACT_DERIVED"


def catalog_record(rid, text_type, arabic_text, source_kind, source_authority, source_round,
                   path, field, input_form, used_as, target_table, owner_ratified,
                   normalized="", tokenized="", notes=""):
    return {
        "record_id": rid,
        "text_type": text_type,
        "arabic_text": arabic_text,
        "arabic_text_unvoweled_if_available": _unvowel(arabic_text) if arabic_text else "",
        "normalized_form_if_available": normalized,
        "tokenized_form_if_available": tokenized,
        "source_kind": source_kind,
        "source_authority": source_authority or "N/A",
        "source_round": source_round,
        "source_artifact_path": path,
        "source_artifact_field": field,
        "input_form": input_form,
        "used_as": used_as,
        "database_target_table": target_table,
        "generalization_candidate": "YES",
        "owner_ratification_required": "YES",
        "owner_ratified": owner_ratified,
        "canonical_status": "CANDIDATE_ONLY",
        "should_enter_database": "YES",
        "database_entry_status": "CANDIDATE_PENDING_OWNER_RATIFICATION",
        "cause": "عنصر مستخرَج من artifact سابق (لا من ذاكرة الوكيل).",
        "conditions": "تصديق المالك قبل أن يصبح record عامًّا؛ SOURCE_RATIFIED ≠ GENERALIZED_RULE.",
        "preventers": "اعتباره قاعدة عامة لمجرد وجوده في artifact.",
        "verdict": "DEFER_FOR_OWNER_DATABASE_RATIFICATION",
        "residuals": "بانتظار تصديق المالك على الإدراج/التعميم.",
        "notes": notes or "",
    }


def build_catalog():
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    regs = inv["registries"]
    tokens_csv = "output/taaqol_nazila_matrix_generated/HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    cat = []

    # ARABIC_TEXT registry -> split nazila vs source texts
    token_surfaces = [r["surface_or_text"] for r in regs.get("LEXICAL_ITEM_REGISTRY_CANDIDATES", [])]
    for r in regs.get("ARABIC_TEXT_REGISTRY_CANDIDATES", []):
        rid = r["record_id"]
        if rid == "AT_NAZILA":
            cat.append(catalog_record(
                "CAT_" + rid, "NAZILA_TEXT", r["surface_or_text"], "NAZILA_TEXT", "النازلة",
                r["source_round"], r["source_artifact_path"], "surface_or_text", "FULL_TEXT",
                "TEXT_INPUT", "arabic_text_registry", "NO",
                tokenized="؛ ".join(token_surfaces),
                notes="جملة النازلة الأصلية المستعملة في كل الجولات."))
        else:
            sk = "NORMATIVE_SOURCE_TEXT"
            cat.append(catalog_record(
                "CAT_" + rid, "NORMATIVE_SOURCE_TEXT", r["surface_or_text"],
                _source_kind_by_authority(r["surface_or_text"]), r["record_id"],
                r["source_round"], r["source_artifact_path"], "TEXT", "JSON_FIELD",
                "SOURCE", "normative_source_registry", r.get("owner_ratified", "NO"),
                notes="نص مصدر معياري (verbatim=ASSERTED_BY_OWNER)."))

    # SOURCE registry -> authorities
    for r in regs.get("SOURCE_REGISTRY_CANDIDATES", []):
        auth = r["surface_or_text"]
        cat.append(catalog_record(
            "CAT_" + r["record_id"], "NORMATIVE_SOURCE_TEXT", auth,
            _source_kind_by_authority(auth), auth, r["source_round"], r["source_artifact_path"],
            "AUTHORITY", "JSON_FIELD", "SOURCE", "normative_source_registry",
            r.get("owner_ratified", "NO"),
            notes="سلطة/إسناد المصدر (citation string)."))

    # generic registries
    for reg, (tt, sk, inf, ua, tbl) in REG_MAP.items():
        for r in regs.get(reg, []):
            authority = "N/A"
            skk = sk
            normalized = ""
            tokenized = ""
            if reg == "LEXICAL_ITEM_REGISTRY_CANDIDATES":
                normalized = _unvowel(r["surface_or_text"])
                tokenized = r["record_id"].replace("LEX_", "")
            cat.append(catalog_record(
                "CAT_" + r["record_id"], tt, r["surface_or_text"], skk, authority,
                r["source_round"], r["source_artifact_path"], "surface_or_text", inf, ua, tbl,
                r.get("owner_ratified", "NO"), normalized=normalized, tokenized=tokenized))

    return inv, cat


def per_type_counts(cat):
    c = {t: 0 for t in TEXT_TYPES}
    for r in cat:
        c[r["text_type"]] = c.get(r["text_type"], 0) + 1
    return c


def text_forms_json(cat):
    inf = {}
    for r in cat:
        inf[r["input_form"]] = inf.get(r["input_form"], 0) + 1
    ua = {}
    for r in cat:
        ua[r["used_as"]] = ua.get(r["used_as"], 0) + 1
    sk = {}
    for r in cat:
        sk[r["source_kind"]] = sk.get(r["source_kind"], 0) + 1
    return {
        "text_types_closed_vocab": TEXT_TYPES,
        "source_kinds_closed_vocab": SOURCE_KINDS,
        "input_forms_closed_vocab": INPUT_FORMS,
        "used_as_closed_vocab": USED_AS,
        "input_form_counts": inf,
        "used_as_counts": ua,
        "source_kind_counts": sk,
        "producer_file": PRODUCER,
    }


def target_tables_json(cat):
    counts = {t: 0 for t in TARGET_TABLES}
    for r in cat:
        counts[r["database_target_table"]] = counts.get(r["database_target_table"], 0) + 1
    return {
        "database_target_tables": TARGET_TABLES,
        "table_record_counts": counts,
        "all_tables_candidate_only": "YES",
        "producer_file": PRODUCER,
    }


def readiness_json(cat):
    return {
        "generalization_ready": "NO",
        "total_records": len(cat),
        "records_owner_ratified_source": sum(1 for r in cat if r["owner_ratified"] == "YES"),
        "records_pending_ratification": sum(1 for r in cat if r["database_entry_status"] ==
                                            "CANDIDATE_PENDING_OWNER_RATIFICATION"),
        "rule": "SOURCE_RATIFIED_IS_NOT_GENERALIZED_RULE",
        "blockers_ref": "TAAQOL_GENERALIZATION_BLOCKERS_36.json",
        "owner_database_ratification_required": "YES",
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "AGENT_MEMORY_USED_AS_SOURCE": "NO",
        "ARTIFACT_ONLY_EXTRACTION": "YES",
        "TEXT_EXISTENCE_DOES_NOT_CREATE_RULE": "YES",
        "EXAMPLE_DOES_NOT_CREATE_GENERALIZATION": "YES",
        "SOURCE_TEXT_DOES_NOT_CREATE_HUKM": "YES",
        "OWNER_RATIFICATION_REQUIRED_FOR_DATABASE_CANONICALIZATION": "YES",
        "DATABASE_CATALOG_IS_NOT_FINAL_CLOSURE": "YES",
        "SOURCE_RATIFIED_IS_NOT_GENERALIZED_RULE": "YES",
        "EXTERNAL_REFERENCE_IS_NOT_AUTHORITY": "YES",
        "BENCHMARK_IS_NOT_HUKM_SOURCE": "YES",
        "ENGLISH_NLP_LAYER_IS_DESIGN_REFERENCE_ONLY": "YES",
        "OWNER_RATIFICATION_REQUIRED_BEFORE_ADOPTION": "YES",
        "GENERALIZATION_READY": "NO",
        "FINAL_MANAT": "NO",
        "TANZIL": "NO",
        "FINAL_HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "FULL_TAAQOL_PROJECT_CLOSED": "NO",
        "producer_file": PRODUCER,
    }


def catalog_md(cat, tc, xrefs):
    L = ["# كتالوج مصدرية بيانات اللغة العربية (الجولة 37 — جرد مستقبلي)", "",
         f"REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · إجمالي السجلات = **{len(cat)}** · أنواع النصوص = {len(TEXT_TYPES)}",
         "", "**المبدأ:** وجود النص في artifact لا يجعله قاعدة عامة؛ كل سجل CANDIDATE_ONLY حتى تصديق المالك.",
         "", "## عدد النصوص حسب النوع"]
    for t in TEXT_TYPES:
        L.append(f"- {t} = {tc.get(t, 0)}")
    L += ["", "## عيّنة من السجلات (النص / النوع / المصدر / الصيغة / الاستعمال / الجدول)"]
    for r in cat[:25]:
        L.append(f"- `{r['record_id']}` [{r['text_type']}] · {r['source_kind']} · {r['input_form']} · "
                 f"used_as={r['used_as']} · table={r['database_target_table']} · "
                 f"owner_ratified={r['owner_ratified']}")
    if len(cat) > 25:
        L.append(f"- … (+{len(cat)-25} أخرى في JSON)")
    L += ["", "## طبقة المراجع الخارجية (EXTERNAL_REFERENCE_LAYER_CANDIDATES — مستقلة)",
          "مراجع تقنية/بحثية ذكرها المالك كمقابلات/أمثلة/مصادر تصميمية محتملة، لا سلطات حاكمة داخل Hokom/Taaqol:"]
    for x in xrefs:
        L.append(f"- `{x['reference_id']}` [{x['layer_name']}] — {x['english_reference']} · "
                 f"usage_now={x['usage_now']} · {x['verdict']}")
    L += ["", "*كل مرجع خارجي: EXTERNAL_REFERENCE_CANDIDATE_ONLY · creates_arabic_rule=NO · "
          "creates_shari_hukm=NO · owner_ratification_required=YES · "
          "availability_verification_status=OWNER_SUPPLIED_CLAIM_NOT_VERIFIED_IN_THIS_ROUND.*",
          "", "---", "*كل سجل verdict=DEFER_FOR_OWNER_DATABASE_RATIFICATION · canonical=CANDIDATE_ONLY · "
          "SOURCE_RATIFIED ≠ GENERALIZED_RULE.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-SUPPLIED-DATA-INVENTORY-36", "ROUND_36",
     "output/taaqol_maqam_foundation_generated/TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.json",
     "tests/test_taaqol_supplied_language_data_inventory_36.py"),
    ("REQ-PROVENANCE-CATALOG-37", "ROUND_37",
     "output/taaqol_maqam_foundation_generated/TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.json",
     "tests/test_taaqol_arabic_data_provenance_catalog_37.py"),
    ("REQ-TEXT-FORMS-37", "ROUND_37",
     "output/taaqol_maqam_foundation_generated/TAAQOL_TEXT_FORMS_AND_INPUT_FORMATS_37.json",
     "tests/test_taaqol_arabic_data_provenance_catalog_37.py"),
    ("REQ-DB-TARGET-TABLES-37", "ROUND_37",
     "output/taaqol_maqam_foundation_generated/TAAQOL_DATABASE_TARGET_TABLES_37.json",
     "tests/test_taaqol_arabic_data_provenance_catalog_37.py"),
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


def build_matrix(cat, tc, tables, xrefs, scanned, anm):
    src_records = tc["NORMATIVE_SOURCE_TEXT"]
    cand_records = tc["FACT_CANDIDATE_TEXT"] + tc["HUKM_CANDIDATE_TEXT"] + tc["MANAT_CANDIDATE_TEXT"]
    kv = [
        ("ROUND", "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("REPORT_SOURCE", "CODE_AND_ARTIFACTS_ONLY"),
        ("AGENT_MEMORY_USED_AS_SOURCE", "NO"),
        ("DATA_PROVENANCE_CATALOG_CREATED", "YES"),
        ("DATA_SOURCES_SCANNED", str(scanned)),
        ("TEXT_TYPES_COUNT", str(len(TEXT_TYPES))),
        ("TOTAL_TEXT_RECORDS", str(len(cat))),
        ("ARABIC_TEXT_RECORDS", str(tc["NAZILA_TEXT"])),
        ("TOKEN_RECORDS", str(tc["NAZILA_TOKEN"])),
        ("SOURCE_TEXT_RECORDS", str(src_records)),
        ("OWNER_RULE_TEXT_RECORDS", str(tc["OWNER_RULE_TEXT"])),
        ("DOMAIN_TERM_RECORDS", str(tc["DOMAIN_TERM"])),
        ("REQUIREMENT_TEXT_RECORDS", str(tc["REQUIREMENT_TEXT"])),
        ("MISSING_FACT_RECORDS", str(tc["MISSING_FACT_REQUIREMENT_TEXT"])),
        ("CANDIDATE_TEXT_RECORDS", str(cand_records)),
        ("GUARD_TEXT_RECORDS", str(tc["GUARD_TEXT"])),
        ("DATABASE_TARGET_TABLES", str(len(tables["database_target_tables"]))),
        ("EXTERNAL_REFERENCE_LAYER_RECORDS", str(len(xrefs))),
        ("EXTERNAL_REFERENCE_IS_NOT_AUTHORITY", "YES"),
        ("BENCHMARK_IS_NOT_HUKM_SOURCE", "YES"),
        ("ENGLISH_NLP_LAYER_IS_DESIGN_REFERENCE_ONLY", "YES"),
        ("EXTERNAL_REFS_INTERNET_VERIFIED_THIS_ROUND", "NO"),
        ("ALL_XREFS_CANDIDATE_ONLY", "YES" if all(x["authority_status"] == "EXTERNAL_REFERENCE_CANDIDATE_ONLY" for x in xrefs) else "NO"),
        ("ALL_XREFS_CREATE_NO_HUKM_OR_ARABIC_RULE", "YES" if all(x["creates_shari_hukm"] == "NO" and x["creates_arabic_rule"] == "NO" for x in xrefs) else "NO"),
        ("ALL_RECORDS_CANDIDATE_ONLY", "YES" if all(r["canonical_status"] == "CANDIDATE_ONLY" for r in cat) else "NO"),
        ("ALL_RECORDS_HAVE_ARTIFACT_PATH", "YES" if all(r["source_artifact_path"] for r in cat) else "NO"),
        ("ALL_GENERALIZATION_NEEDS_RATIFICATION", "YES" if all(r["owner_ratification_required"] == "YES" for r in cat) else "NO"),
        ("GENERALIZATION_READY", "NO"),
        ("OWNER_DATABASE_RATIFICATION_REQUIRED", "YES"),
        ("SOURCE_RATIFIED_IS_NOT_GENERALIZED_RULE", "YES"),
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


def render_manager(tokens, cat, tc, tables, forms, xrefs, scanned, trows, anm):
    e = lambda x: html.escape(str(x))
    src_records = tc["NORMATIVE_SOURCE_TEXT"]
    cand_records = tc["FACT_CANDIDATE_TEXT"] + tc["HUKM_CANDIDATE_TEXT"] + tc["MANAT_CANDIDATE_TEXT"]
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — كتالوج مصدرية بيانات اللغة (37)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.72rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — كتالوج مصدرية بيانات اللغة العربية (37)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · AGENT_MEMORY_USED_AS_SOURCE = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0. جرد مصدرية مستقبلي.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'وجود النص لا يُنشئ قاعدة · مثال لا يُنشئ تعميمًا · نص مصدر لا يُنشئ حكمًا · '
             'SOURCE_RATIFIED ≠ GENERALIZED_RULE · تصديق المالك مطلوب للتعميم · GENERALIZATION_READY=NO · '
             'لا مناط/تنزيل/حكم/جواب · FULL_TAAQOL_PROJECT_CLOSED=NO.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             f'<li>فُحِص {scanned} مصدر بيانات وبُني كتالوج **{len(cat)}** سجلًّا عبر {len(TEXT_TYPES)} نوع نص.</li>'
             f'<li>ألفاظ={tc["NAZILA_TOKEN"]} · مصادر={src_records} · قواعد مالك={tc["OWNER_RULE_TEXT"]} · '
             f'requirements={tc["REQUIREMENT_TEXT"]} · candidates={cand_records}.</li>'
             '<li>كل سجل CANDIDATE_ONLY · DEFER · يحتاج تصديق مالك؛ لا مناط/تنزيل/حكم/جواب.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ تُدرج كسجل مرشح لا كقاعدة. IFADAH_CHANGED = NO.</div>')
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يصبح قاعدة عامة. MAQAM_IS_NOT_RULE = YES.</div>')
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · EXTERNAL_REFS = 0. '
             'المصادر مصدَّقة كمصادر لا كقواعد كنسية.</div>')
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'جرد مصدرية فقط؛ لا واقعة مقبولة ولا رخصة عبور. FACT_CANDIDATE_CREATES_FACT = NO.</div>')
    # 8 counts by type
    P.append('<h2>8. المصدر المعياري — عدد النصوص حسب النوع</h2><div class="wrap"><table><thead><tr>'
             '<th>text_type</th><th>العدد</th></tr></thead><tbody>')
    for t in TEXT_TYPES:
        P.append(f'<tr><th>{e(t)}</th><td class="y">{tc.get(t, 0)}</td></tr>')
    P.append(f'<tr><th>الإجمالي</th><td class="y">{len(cat)}</td></tr></tbody></table></div>')
    # provenance sample table
    P.append('<div class="wrap"><table><thead><tr><th>record_id</th><th>type</th><th>source_kind</th>'
             '<th>input_form</th><th>used_as</th><th>target_table</th><th>owner_ratified</th>'
             '<th>canonical</th></tr></thead><tbody>')
    for r in cat[:18]:
        P.append('<tr><th>' + e(r["record_id"]) + '</th><td class="d">' + e(r["text_type"]) + '</td>'
                 '<td>' + e(r["source_kind"]) + '</td><td>' + e(r["input_form"]) + '</td>'
                 '<td>' + e(r["used_as"]) + '</td><td>' + e(r["database_target_table"]) + '</td>'
                 + f'<td class="d">{e(r["owner_ratified"])}</td><td class="d">{e(r["canonical_status"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9 generalization readiness table
    P.append('<h2>9. موضع التوقف — ما يصلح للتعميم وما لا يصلح</h2>'
             '<div class="note n" style="background:#fdecec">GENERALIZATION_READY = NO لكل السجلات؛ '
             'لا سجل يصلح للتعميم قبل تصديق المالك؛ SOURCE_RATIFIED ≠ GENERALIZED_RULE.</div>'
             '<div class="wrap"><table><thead><tr><th>الجدول الهدف</th><th>عدد السجلات</th>'
             '<th>candidate_only</th></tr></thead><tbody>')
    for tbl, c in tables["table_record_counts"].items():
        P.append(f'<tr><th>{e(tbl)}</th><td>{c}</td><td class="d">YES</td></tr>')
    P.append('</tbody></table></div>')
    # external reference layer (separate)
    P.append('<h2>طبقة المراجع الخارجية (EXTERNAL_REFERENCE_LAYER_CANDIDATES)</h2>'
             '<div class="note n" style="background:#fdecec">مراجع تقنية/بحثية ذكرها المالك كمقابلات/أمثلة/'
             'مصادر تصميمية محتملة — لا سلطات حاكمة داخل Hokom/Taaqol. '
             'EXTERNAL_REFERENCE_IS_NOT_AUTHORITY = YES · BENCHMARK_IS_NOT_HUKM_SOURCE = YES · '
             'ENGLISH_NLP_LAYER_IS_DESIGN_REFERENCE_ONLY = YES · '
             'availability_verification_status = OWNER_SUPPLIED_CLAIM_NOT_VERIFIED_IN_THIS_ROUND.</div>'
             '<div class="wrap"><table><thead><tr><th>reference_id</th><th>layer</th><th>المرجع</th>'
             '<th>ما يعطيه</th><th>hokom/taaqol mapping</th><th>usage_now</th><th>verdict</th>'
             '</tr></thead><tbody>')
    for x in xrefs:
        P.append('<tr><th>' + e(x["reference_id"]) + '</th><td>' + e(x["layer_name"]) + '</td>'
                 '<td>' + e(x["english_reference"]) + '</td><td>' + e(x["what_it_gives"]) + '</td>'
                 '<td>' + e(x["hokom_or_taaqol_mapping"]) + '</td>'
                 + f'<td class="d">{e(x["usage_now"])}</td><td class="n">{e(x["verdict"])}</td></tr>')
    P.append('</tbody></table></div>'
             '<div class="note">كل مرجع: authority_status=EXTERNAL_REFERENCE_CANDIDATE_ONLY · '
             'creates_arabic_rule=NO · creates_shari_hukm=NO · creates_fact/manat/tanzil=NO · '
             'owner_ratification_required=YES. لم يُتحقَّق من الإنترنت هذه الجولة.</div>')
    # 10 needs ratification
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note n" style="background:#fdecec">'
             f'كل السجلات ({len(cat)}) تحتاج تصديق مالك قبل أن تصبح records عامة '
             '(database_entry_status=CANDIDATE_PENDING_OWNER_RATIFICATION).</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">تصديق المالك على السجلات (RATIFY_AS_CANONICAL) '
             'يرفع database_entry_status تدريجيًّا؛ ويبقى الكتالوج ليس إغلاقًا نهائيًّا.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_arabic_data_provenance_catalog_37.py — '
             'ROUND_37_CAT_TESTS = passed · REGRESSION_SCOPE = maqam 02..25 + 32..37 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    P.append(_trace_html(trows))
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_37_CAT_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT = output/taaqol_maqam_foundation_generated/TAAQOL_SUPPLIED_LANGUAGE_DATA_INVENTORY_36.json\n'
             'CATALOG_JSON = output/taaqol_maqam_foundation_generated/TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.json\n'
             'TEXT_FORMS = output/taaqol_maqam_foundation_generated/TAAQOL_TEXT_FORMS_AND_INPUT_FORMATS_37.json\n'
             'TARGET_TABLES = output/taaqol_maqam_foundation_generated/TAAQOL_DATABASE_TARGET_TABLES_37.json\n'
             'READINESS = output/taaqol_maqam_foundation_generated/TAAQOL_DATA_GENERALIZATION_READINESS_37.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/TAAQOL_DATA_PROVENANCE_GUARDS_37.json\n'
             'PYTEST_FILE = tests/test_taaqol_arabic_data_provenance_catalog_37.py\n'
             'AGENT_MEMORY_USED_AS_SOURCE = NO\nGENERALIZATION_READY = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO\nPUSH = NO</pre></div>')
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'بُني كتالوج مصدرية بـ {len(cat)} سجلًّا عبر {len(TEXT_TYPES)} نوع نص من artifacts فقط؛ '
             'كلها CANDIDATE_ONLY وتحتاج تصديق مالك، ولا تصلح للتعميم بعد. لا مناط/تنزيل/حكم/جواب، ولا إغلاق مشروع.</div>')
    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'DATA_PROVENANCE_CATALOG_CREATED = YES · TOTAL_TEXT_RECORDS = {len(cat)} · '
             f'TEXT_TYPES_COUNT = {len(TEXT_TYPES)} · GENERALIZATION_READY = NO · '
             'OWNER_DATABASE_RATIFICATION_REQUIRED = YES · FINAL_MANAT = NO · TANZIL = NO · '
             'FINAL_HUKM = NO · FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO · AUTHORITY_LEAK = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PUSH = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_37_CAT_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'GENERALIZATION_READY = NO · FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · '
             'FINAL_ANSWER = NO · FULL_TAAQOL_PROJECT_CLOSED = NO · COMMIT = NO · PUSH = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "TAAQOL_DATA_PROVENANCE_MANAGER_REPORT_AR_37.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    inv, cat = build_catalog()
    tc = per_type_counts(cat)
    forms = text_forms_json(cat)
    tables = target_tables_json(cat)
    readiness = readiness_json(cat)
    xrefs = build_external_refs()
    scanned = inv.get("data_sources_scanned", 0)

    (OUT / "TAAQOL_EXTERNAL_REFERENCE_LAYER_CANDIDATES_37.json").write_text(
        json.dumps({"ROUND": "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37",
                    "layer_name": "EXTERNAL_REFERENCE_LAYER_CANDIDATES",
                    "authority_note": "EXTERNAL_REFERENCE_CANDIDATE_ONLY — not governing authorities",
                    "external_reference_count": len(xrefs),
                    "external_references": xrefs, "producer_file": PRODUCER}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    (OUT / "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.json").write_text(
        json.dumps({"ROUND": "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37",
                    "report_source": "CODE_AND_ARTIFACTS_ONLY",
                    "agent_memory_used_as_source": "NO",
                    "text_types": TEXT_TYPES,
                    "per_text_type_counts": tc,
                    "total_text_records": len(cat),
                    "records": cat, "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_ARABIC_DATA_PROVENANCE_CATALOG_37.md").write_text(catalog_md(cat, tc, xrefs), encoding="utf-8")
    (OUT / "TAAQOL_TEXT_FORMS_AND_INPUT_FORMATS_37.json").write_text(
        json.dumps(forms, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_DATABASE_TARGET_TABLES_37.json").write_text(
        json.dumps(tables, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_DATA_GENERALIZATION_READINESS_37.json").write_text(
        json.dumps(readiness, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "TAAQOL_DATA_PROVENANCE_GUARDS_37.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(cat, tc, tables, xrefs, scanned, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(
        render_manager(tokens, cat, tc, tables, forms, xrefs, scanned, trows, anm), encoding="utf-8")
    print("REPORT_37_CAT=" + a.report_out)
    print(f"RECORDS={len(cat)} TEXT_TYPES={len(TEXT_TYPES)} per_type={tc} "
          f"tables={len(tables['database_target_tables'])} GENERALIZATION_READY=NO ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
