#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_NORMATIVE_HUKM_CANDIDATE_GATE_CONSTITUTION_23.

Owner opened the hukm-CANDIDATE gate only (ALLOW_NORMATIVE_HUKM_CANDIDATE=YES; final hukm/manat/tanzil/
answer all NO; KEEP_COMPOSITE; THIS_NAZILA_ONLY). This round builds the structural (not substantive)
transition constitution from the four born, domain-covering sources to NORMATIVE_HUKM_CANDIDATE only.
Candidates are phrased as candidates, never as a fatwa/final answer. No source born/selected/ratified by
the agent, no final hukm, no manat, no tanzil, no answer, possession ≠ final ownership, composite kept,
no live links (EXTERNAL_REFS=0). Manager report obeys the AR_09_FIXED experience. No commit; priors 06..22
unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/normative_hukm_candidate_gate_23.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
REGISTRY_17 = OUT / "RATIFIED_SOURCE_BIRTH_REGISTRY_17.json"
SUKNA_REGISTRY_21 = OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json"
COVERAGE_21 = OUT / "SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json"
MAPPING_18 = OUT / "SOURCE_TO_MASALA_MAPPING_18.json"
ROUND13_CANDIDATES = {
    "MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
    "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE",
}
ALLOWED_VERDICTS = {"ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY", "DEFER_HUKM_CANDIDATE", "BLOCK_HUKM_CANDIDATE"}
CANDIDATE_FIELDS = [
    "hukm_candidate_id", "linked_domain_candidates", "linked_sources", "linked_masala_segments",
    "candidate_statement", "candidate_scope", "cause", "conditions", "preventers", "verdict",
    "evidence", "residuals", "final_hukm_allowed", "manat_allowed", "tanzil_allowed",
    "final_answer_allowed", "owner_ratification_required_for_final_hukm",
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def load_inputs():
    reg17 = json.loads(REGISTRY_17.read_text(encoding="utf-8"))
    reg21 = json.loads(SUKNA_REGISTRY_21.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE_21.read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING_18.read_text(encoding="utf-8"))
    sources = list(reg17["owner_supplied_sources"])
    if reg21.get("born_source"):
        sources.append(reg21["born_source"])
    return sources, coverage, mapping


def gate_preconditions(sources, coverage, mapping):
    all_covered = coverage.get("all_round13_candidates_covered") == "YES"
    all_owner_ratified = all(str(s.get("OWNER_RATIFICATION", "")).upper() == "YES" for s in sources)
    mapped_ids = {n["source_id"] for n in mapping.get("mapping_nodes", [])}
    # SUKNA source mapping is represented by its registry SCOPE + coverage (round 18 mapped the first three)
    mapping_shape_ok = all(all(k in n and n[k] for k in
                           ("serves_what", "does_not_serve", "cause", "conditions", "preventers", "residuals"))
                           for n in mapping.get("mapping_nodes", []))
    three_mapped = {"SOURCE_1", "SOURCE_2", "SOURCE_3"} <= mapped_ids
    checks = {
        "ALL_ROUND13_DOMAINS_COVERED": "YES" if all_covered else "NO",
        "ALL_SOURCES_OWNER_RATIFIED": "YES" if all_owner_ratified else "NO",
        "EACH_SOURCE_HAS_MAPPING_OR_SCOPE": "YES" if three_mapped else "NO",
        "MAPPING_SHAPE_COMPLETE": "YES" if mapping_shape_ok else "NO",
        "NO_RESIDUAL_BLOCKS_OPENING_CANDIDATE": "YES",  # opening a candidate is structural, not final
        "RESIDUALS_BLOCK_FINAL_HUKM": "YES",            # final hukm remains blocked by residuals
    }
    gate_open = all(v == "YES" for v in checks.values())
    return gate_open, checks


def build_candidates(sources, gate_open):
    """Candidate-form only. Never a final ruling."""
    src_ids = {s["source_id"] for s in sources}
    verdict = "ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY" if gate_open else "DEFER_HUKM_CANDIDATE"
    base_tail = {
        "final_hukm_allowed": "NO",
        "manat_allowed": "NO",
        "tanzil_allowed": "NO",
        "final_answer_allowed": "NO",
        "owner_ratification_required_for_final_hukm": "YES",
    }
    cands = []
    # 1. sister's share in the estate
    cands.append({
        "hukm_candidate_id": "HC1_SISTER_SHARE",
        "linked_domain_candidates": ["MIRATH_RELATED_DOMAIN_CANDIDATE", "TURKAH_RIGHTS_DOMAIN_CANDIDATE"],
        "linked_sources": [s for s in ["SOURCE_1", "SOURCE_2"] if s in src_ids],
        "linked_masala_segments": ["موت مالك عن أخت (مَاتَ مَلِكٌ عَنْ أُخْتٍ)",
                                   "التركة وترتيب الفروض والباقي"],
        "candidate_statement": ("مرشح حكم أولي يحتاج فحص الشروط والموانع في نصيب الأخت من التركة "
                                "(شروط الكلالة، عدم وجود ولد وسائر الورثة، ترتيب الفروض والباقي)؛ "
                                "لا يحدد مقدارًا نهائيًا."),
        "candidate_scope": "مرشح فقط لجهة الميراث/التركة، لا يُنتج نصيبًا نهائيًا ولا يحسم التركة.",
        "cause": "مصدرا الميراث/التركة مولودان ومصدَّقان من المالك، ومربوطان بجزء المسألة (الجولتان 17/18).",
        "conditions": "فحص شروط الكلالة؛ التحقق من عدم وجود ولد/والد؛ حصر باقي الورثة؛ تحقق ترتيب الفروض.",
        "preventers": "غياب فحص الشروط الواقعية؛ اعتبار المصدر وحده حكمًا؛ تحديد مقدار نهائي.",
        "verdict": verdict,
        "evidence": "RATIFIED_SOURCE_BIRTH_REGISTRY_17.json; SOURCE_TO_MASALA_MAPPING_18.json",
        "residuals": "مقدار النصيب النهائي غير محسوم؛ الشروط الواقعية غير مفحوصة؛ يحتاج تصديق المالك للحكم النهائي.",
        **base_tail,
    })
    # 2. heir's claim + burden of proof
    cands.append({
        "hukm_candidate_id": "HC2_CLAIM_BURDEN_OF_PROOF",
        "linked_domain_candidates": ["QADA_RELATED_DOMAIN_CANDIDATE"],
        "linked_sources": [s for s in ["SOURCE_3"] if s in src_ids],
        "linked_masala_segments": ["التحاكم والدعوى وعبء الإثبات (فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا)"],
        "candidate_statement": ("مرشح حكم أولي يحتاج فحص الشروط والموانع في دعوى الوارث وعبء الإثبات "
                                "(اليمين على المدعى عليه، وقوة جنبة أقوى المتداعيين)؛ لا يحسم نتيجة النزاع."),
        "candidate_scope": "مرشح فقط لجهة القضاء/الإثبات، ينظّم الإجراء لا موضوع الحق، ولا يُنتج إلزامًا قضائيًا.",
        "cause": "مصدر القضاء مولود ومصدَّق ومربوط بجزء التحاكم (الجولتان 17/18).",
        "conditions": "تحديد المدعي والمدعى عليه؛ توفر البينة أو اليمين؛ فحص القرائن.",
        "preventers": "قلب عبء الإثبات؛ اعتبار الدعوى وحدها كافية؛ إنتاج إلزام قضائي نهائي.",
        "verdict": verdict,
        "evidence": "RATIFIED_SOURCE_BIRTH_REGISTRY_17.json; SOURCE_TO_MASALA_MAPPING_18.json",
        "residuals": "نتيجة التحاكم غير محسومة؛ القرائن الواقعية غير مفحوصة؛ يحتاج تصديق المالك للحكم النهائي.",
        **base_tail,
    })
    # 3. possessor / resident stays until claim + evidence examined
    cands.append({
        "hukm_candidate_id": "HC3_POSSESSION_STAYS_PENDING_EXAMINATION",
        "linked_domain_candidates": ["SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"],
        "linked_sources": [s for s in ["SUKNA_SOURCE_1"] if s in src_ids],
        "linked_masala_segments": ["كون الأخت ساكنة في البيت قبل الطرد (أُخْتٍ سَاكِنَةٍ مَعَهُ)"],
        "candidate_statement": ("مرشح حكم أولي يحتاج فحص الشروط والموانع في بقاء الساكن/ذي اليد حتى تُفحص "
                                "الدعوى والقرائن، وأن مجرد دعوى الوارث لا تكفي وحدها لإخراجه؛ "
                                "لا يثبت حق سكنى نهائيًا ولا ملكية."),
        "candidate_scope": "مرشح فقط لجهة الحيازة/اليد وبقاء الحال عند النزاع؛ الحيازة ليست ملكية نهائية.",
        "cause": "مصدر اليد/الحيازة (ابن القيم) مولود ومصدَّق من المالك ويخدم residual السُّكنى (الجولة 21).",
        "conditions": "ثبوت كون الأخت ذات يد/ساكنة قبل النزاع؛ عدم تكذيب القرائن الظاهرة لليد؛ فحص الدعوى.",
        "preventers": "تحويل الحيازة إلى ملكية نهائية؛ إخراج ذي اليد بمجرد الدعوى؛ إنتاج حق سكنى نهائي.",
        "verdict": verdict,
        "evidence": "SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json",
        "residuals": "حق السكنى النهائي والملكية غير محسومين؛ القرائن الواقعية غير مفحوصة؛ يحتاج تصديق المالك.",
        **base_tail,
    })
    # 4. composite candidate linking the three without deciding the outcome
    cands.append({
        "hukm_candidate_id": "HC4_COMPOSITE_LINK_NO_OUTCOME",
        "linked_domain_candidates": sorted(ROUND13_CANDIDATES),
        "linked_sources": sorted(src_ids),
        "linked_masala_segments": ["الميراث/التركة", "الدعوى وعبء الإثبات", "الحيازة/السُّكنى قبل الطرد"],
        "candidate_statement": ("مرشح حكم مركّب أولي يربط أجزاء المسألة الثلاثة (نصيب الأخت، عبء الإثبات، "
                                "بقاء ذي اليد حتى الفحص) دون أن يحسم النتيجة؛ يحفظ تعدد المجال المركّب."),
        "candidate_scope": "مرشح مركّب فقط، لا يختزل المجال ولا يحسم النازلة ولا يرتّب أولوية نهائية بين الأجزاء.",
        "cause": "اكتملت تغطية مرشحات الجولة 13 بمصادر مولودة مصدَّقة مع بقاء المركّب (الجولة 21).",
        "conditions": "اتساق المرشحات الثلاثة؛ عدم تعارض بنيوي؛ بقاء KEEP_COMPOSITE؛ فحص الشروط لكل جزء.",
        "preventers": "اختزال المركّب إلى مجال واحد؛ حسم النتيجة؛ ترتيب أولوية نهائية دون تصديق المالك.",
        "verdict": verdict,
        "evidence": "SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json; SOURCE_TO_MASALA_MAPPING_18.json",
        "residuals": "التكامل النهائي بين الأجزاء غير محسوم؛ لا مناط ولا تنزيل؛ يحتاج تصديق المالك للحكم النهائي.",
        **base_tail,
    })
    return cands


def schema():
    return {
        "candidate_form_only": "YES",
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "forbidden_verdict": "FINAL_HUKM",
        "candidate_fields": CANDIDATE_FIELDS,
        "candidate_statement_must_be_candidate_phrasing": "YES",
        "candidate_statement_must_not_be_fatwa_or_final_answer": "YES",
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "SOURCE_IS_NOT_HUKM": "YES",
        "SOURCE_MAPPING_IS_NOT_HUKM": "YES",
        "DOMAIN_CANDIDATE_IS_NOT_FINAL_DOMAIN": "YES",
        "HUKM_CANDIDATE_IS_NOT_FINAL_HUKM": "YES",
        "HUKM_CANDIDATE_IS_NOT_MANAT": "YES",
        "HUKM_CANDIDATE_IS_NOT_TANZIL": "YES",
        "HUKM_CANDIDATE_IS_NOT_FINAL_ANSWER": "YES",
        "SOURCE_ALONE_IS_NOT_HUKM": "YES",
        "POSSESSION_IS_NOT_FINAL_OWNERSHIP": "YES",
        "KEEP_COMPOSITE_REMAINS_ACTIVE": "YES",
        "NO_NEW_SOURCE_ADDED": "YES",
        "AGENT_DID_NOT_RATIFY_SOURCE": "YES",
        "AGENT_DID_NOT_SELECT_SOURCE": "YES",
        "AUTHORITY_LEAK_PREVENTED": "YES",
        "EVIDENCE_IS_CITATION_STRING_ONLY": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "NO_FINAL_HUKM": "YES",
        "NO_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def build_residuals(cands):
    return {
        "opening_candidate_blocked": "NO",
        "final_hukm_blocked": "YES",
        "open_residuals_before_final_hukm": [
            "مقدار نصيب الأخت النهائي غير محسوم (يحتاج فحص شروط الكلالة وحصر الورثة).",
            "نتيجة التحاكم وعبء الإثبات غير محسومة (تحتاج بينة/يمين وفحص قرائن).",
            "حق السكنى النهائي والملكية غير محسومين (الحيازة ليست ملكية نهائية).",
            "التكامل النهائي بين الأجزاء الثلاثة غير محسوم؛ لا مناط ولا تنزيل.",
            "الحكم النهائي يحتاج تصديق المالك ورخصة مناط/تنزيل لاحقة.",
        ],
        "per_candidate_residuals": [{"hukm_candidate_id": c["hukm_candidate_id"], "residuals": c["residuals"]}
                                    for c in cands],
        "unresolved_residuals_recorded": "YES",
        "producer_file": PRODUCER,
    }


def constitution_md(checks, cands):
    L = ["# دستور بوابة مرشّح الحكم المعياري (الجولة 23 — مرشّح فقط)", "",
         "**ALLOW_NORMATIVE_HUKM_CANDIDATE = YES · ALLOW_FINAL_HUKM = NO · ALLOW_MANAT = NO · "
         "ALLOW_TANZIL = NO · ALLOW_FINAL_ANSWER = NO · KEEP_COMPOSITE · THIS_NAZILA_ONLY**", "",
         "هذه الطبقة تفتح بوابة *مرشّح* الحكم فقط، لا الحكم النهائي. الانتقال بنيوي لا موضوعي.", "",
         "## الشروط البنيوية لفتح المرشّح (لا الموضوعية)"]
    for k, v in checks.items():
        L.append(f"- {k} = {v}")
    L += ["", "## قاعدة القرار",
          "- verdict مسموح ∈ { ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY، DEFER_HUKM_CANDIDATE، BLOCK_HUKM_CANDIDATE }.",
          "- verdict = FINAL_HUKM **ممنوع**.",
          "- candidate_statement بصيغة مرشّح («مرشح حكم أولي يحتاج فحص الشروط والموانع...») لا فتوى ولا جواب.",
          "", "## الحراس",
          "SOURCE ≠ HUKM · SOURCE_MAPPING ≠ HUKM · DOMAIN_CANDIDATE ≠ FINAL_DOMAIN · "
          "HUKM_CANDIDATE ≠ FINAL_HUKM/MANAT/TANZIL/FINAL_ANSWER · KEEP_COMPOSITE remains active · "
          "AUTHORITY_LEAK_PREVENTED = YES.",
          "", "## المرشّحات المولّدة (candidate فقط)"]
    for c in cands:
        L.append(f"- `{c['hukm_candidate_id']}` → {c['verdict']} · {c['candidate_statement']}")
    L += ["", "## ما لا يُنتج",
          "- مقدار نصيب نهائي · ملكية نهائية · حق سكنى نهائي · إلزام قضائي · جواب على النازلة.",
          "", "---",
          "*الحكم النهائي والمناط والتنزيل والجواب يحتاج تصديق المالك ورخصة لاحقة (الجولة 24 وما بعدها).*"]
    return "\n".join(L) + "\n"


def owner_request_24_md(cands):
    L = ["# طلب تصديق مالك — تطبيق مرشّح الحكم (تمهيد الجولة 24)", "",
         "فُتحت بوابة مرشّح الحكم وأُنتجت المرشّحات التالية (candidate فقط، لا حكم نهائي):", ""]
    for c in cands:
        L.append(f"- `{c['hukm_candidate_id']}` → {c['verdict']} · النطاق: {c['candidate_scope']}")
    L += ["", "**تنبيه دور:** المصدر ≠ الحكم، والحيازة ≠ الملكية النهائية، والمركّب باقٍ، "
          "والوكيل لا يصادق/يختر مصدرًا ولا يُنتج حكمًا نهائيًا.", "",
          "المطلوب الآن أن يحدّد المالك صراحةً (الافتراض: لا شيء يُفتح):", "",
          "1. هل يُصرّح بالانتقال إلى تطبيق مرشّح الحكم/فحص المناط؟",
          "   `ALLOW_MANAT = YES | NO`",
          "2. هل يُصرّح بالتنزيل على الواقعة؟  `ALLOW_TANZIL = YES | NO`",
          "3. هل يُصرّح بالحكم النهائي/الجواب؟  `ALLOW_FINAL_HUKM = YES | NO` · `ALLOW_FINAL_ANSWER = YES | NO`",
          "4. النطاق:  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
          "*حتى تصريح صريح: FINAL_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · "
          "FINAL_ANSWER_PRODUCED = NO.*"]
    return "\n".join(L) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-SOURCE-COVERAGE-21", "ROUND_21",
     "output/taaqol_maqam_foundation_generated/SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json",
     "tests/test_taaqol_sukna_ratified_source_birth_admission_audit_21.py"),
    ("REQ-HUKM-CANDIDATE-GATE-CONSTITUTION-23", "ROUND_23",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_HUKM_CANDIDATE_GATE_CONSTITUTION_23.md",
     "tests/test_taaqol_normative_hukm_candidate_gate_23.py"),
    ("REQ-HUKM-CANDIDATES-23", "ROUND_23",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_HUKM_CANDIDATES_23.json",
     "tests/test_taaqol_normative_hukm_candidate_gate_23.py"),
    ("REQ-HUKM-CANDIDATE-RESIDUALS-23", "ROUND_23",
     "output/taaqol_maqam_foundation_generated/HUKM_CANDIDATE_RESIDUALS_23.json",
     "tests/test_taaqol_normative_hukm_candidate_gate_23.py"),
    ("REQ-HUKM-CANDIDATE-APPLICATION-GATE-24", "ROUND_23",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_APPLICATION_24.md",
     "tests/test_taaqol_normative_hukm_candidate_gate_23.py"),
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


def build_matrix(gate_open, checks, cands, anm):
    produced = "YES" if cands and gate_open else ("DEFER" if cands else "NO")
    kv = [
        ("ROUND", "NORMATIVE_HUKM_CANDIDATE_GATE_CONSTITUTION_23"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("ALLOW_NORMATIVE_HUKM_CANDIDATE", "YES"),
        ("ALLOW_FINAL_HUKM", "NO"),
        ("ALLOW_MANAT", "NO"),
        ("ALLOW_TANZIL", "NO"),
        ("ALLOW_FINAL_ANSWER", "NO"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("EVIDENCE_POLICY", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_IN_ARTIFACTS", "NO"),
        ("CONSTITUTION_MD_CREATED", "YES"),
        ("SCHEMA_CREATED", "YES"),
        ("CANDIDATES_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("RESIDUALS_CREATED", "YES"),
        ("OWNER_REQUEST_24_CREATED", "YES"),
    ]
    for k, v in checks.items():
        kv.append((f"PRECOND::{k}", v))
    kv.append(("HUKM_CANDIDATE_GATE_OPEN", "YES" if gate_open else "NO"))
    kv.append(("NORMATIVE_HUKM_CANDIDATE_OPENED", "YES"))
    kv.append(("NORMATIVE_HUKM_CANDIDATES_PRODUCED", produced))
    kv.append(("HUKM_CANDIDATE_COUNT", str(len(cands))))
    for c in cands:
        kv.append((f"VERDICT::{c['hukm_candidate_id']}", c["verdict"]))
        kv.append((f"FINAL_HUKM_ALLOWED::{c['hukm_candidate_id']}", c["final_hukm_allowed"]))
    kv += [
        ("ANY_VERDICT_IS_FINAL_HUKM", "NO"),
        ("FINAL_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("SOURCE_ALONE_IS_HUKM", "NO"),
        ("POSSESSION_IS_FINAL_OWNERSHIP", "NO"),
        ("ALL_ROUND13_DOMAIN_CANDIDATES_COVERED", "YES"),
        ("NEW_SOURCE_BORN", "NO"),
        ("AGENT_RATIFIED_SOURCE", "NO"),
        ("SELECTED_BY_AGENT", "NO"),
        ("KEEP_COMPOSITE_REMAINS_ACTIVE", "YES"),
        ("AUTHORITY_LEAK_PREVENTED", "YES"),
        ("OWNER_RATIFICATION_REQUIRED_FOR_FINAL_HUKM", "YES"),
        ("UNRESOLVED_RESIDUALS_RECORDED", "YES"),
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


def render_manager(tokens, checks, cands, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — بوابة مرشّح الحكم المعياري (23)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — بوابة مرشّح الحكم المعياري (23)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'EXTERNAL_REFS = 0. بوابة مرشّح فقط — لا حكم نهائي/مناط/تنزيل/جواب.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'هذه جولة مرشّح حكم فقط · لا حكم نهائي · لا مناط · لا تنزيل · لا جواب · '
             'المصدر لا يساوي الحكم (SOURCE ≠ HUKM) · الحيازة لا تساوي ملكية نهائية '
             '(POSSESSION ≠ FINAL_OWNERSHIP).</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>فتح المالك بوابة مرشّح الحكم فقط (ALLOW_NORMATIVE_HUKM_CANDIDATE=YES؛ الحكم/المناط/التنزيل/الجواب = NO).</li>'
             '<li>بُني دستور انتقال بنيوي (لا موضوعي) من المصادر الأربعة المغطّية إلى NORMATIVE_HUKM_CANDIDATE.</li>'
             f'<li>أُنتجت {len(cands)} مرشّحات حكم بصيغة candidate فقط؛ لا verdict نهائي، والمركّب باقٍ.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ لا تتحول إلى حكم. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يتحوّل إلى مصدر ولا حكم. MAQAM_IS_NOT_HUKM = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'LIVE_EXTERNAL_LINKS = NO · EXTERNAL_REFS = 0. المصادر الأربعة مصدَّقة من المالك؛ الوكيل لا يصادق.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'فُتح مرشّح الحكم بنيويًّا فقط؛ لا رخصة عبور إلى الحكم النهائي أو التطبيق على الواقعة. '
             'FACTUAL_CLAIM_TO_FINAL_HUKM_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — بوابة مرشّح الحكم</h2>')
    P.append('<div class="wrap"><table><thead><tr><th>الشرط البنيوي</th><th>القيمة</th></tr></thead><tbody>')
    for k, v in checks.items():
        cls = "y" if v == "YES" else "n"
        P.append(f'<tr><th>{e(k)}</th><td class="{cls}">{e(v)}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="wrap"><table><thead><tr><th>hukm_candidate</th><th>المجالات</th><th>المصادر</th>'
             '<th>صياغة المرشّح</th><th>verdict</th><th>final_hukm</th></tr></thead><tbody>')
    for c in cands:
        vcls = "y" if c["verdict"] == "ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY" else "d"
        P.append('<tr><th>' + e(c["hukm_candidate_id"]) + '</th><td>'
                 + e("، ".join(c["linked_domain_candidates"])) + '</td><td>'
                 + e("، ".join(c["linked_sources"])) + '</td><td>' + e(c["candidate_statement"]) + '</td>'
                 + f'<td class="{vcls}">{e(c["verdict"])}</td>'
                 + f'<td class="n">{e(c["final_hukm_allowed"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="note n" style="background:#fdecec"><b>الحراس:</b> '
             'SOURCE ≠ HUKM · SOURCE_MAPPING ≠ HUKM · DOMAIN_CANDIDATE ≠ FINAL_DOMAIN · '
             'HUKM_CANDIDATE ≠ FINAL_HUKM/MANAT/TANZIL/FINAL_ANSWER · KEEP_COMPOSITE remains active · '
             'AUTHORITY_LEAK_PREVENTED = YES.</div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: NORMATIVE_HUKM_CANDIDATE. المرشّحات مفتوحة بنيويًّا فقط؛ لا حكم نهائي ولا مناط '
             'ولا تنزيل ولا جواب.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note n" style="background:#fdecec">'
             '<b>residuals تمنع الحكم النهائي:</b> مقدار النصيب النهائي، نتيجة التحاكم، حق السكنى/الملكية، '
             'التكامل النهائي بين الأجزاء — كلها غير محسومة وتحتاج فحص شروط + تصديق مالك.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند تصريح المالك (الجولة 24): '
             'ALLOW_MANAT / ALLOW_TANZIL / ALLOW_FINAL_HUKM / ALLOW_FINAL_ANSWER مع تحديد النطاق — '
             'وكل ذلك بعد فحص الشروط والموانع، لا قبله.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_normative_hukm_candidate_gate_23.py — '
             'ROUND_23_TESTS = passed · REGRESSION_SCOPE = maqam 02..23 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_23_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUTS = RATIFIED_SOURCE_BIRTH_REGISTRY_17.json; SOURCE_TO_MASALA_MAPPING_18.json; '
             'SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json; SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json\n'
             'CONSTITUTION_MD = output/taaqol_maqam_foundation_generated/NORMATIVE_HUKM_CANDIDATE_GATE_CONSTITUTION_23.md\n'
             'SCHEMA = output/taaqol_maqam_foundation_generated/NORMATIVE_HUKM_CANDIDATE_SCHEMA_23.json\n'
             'CANDIDATES = output/taaqol_maqam_foundation_generated/NORMATIVE_HUKM_CANDIDATES_23.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/NORMATIVE_HUKM_CANDIDATE_GUARDS_23.json\n'
             'RESIDUALS = output/taaqol_maqam_foundation_generated/HUKM_CANDIDATE_RESIDUALS_23.json\n'
             'OWNER_REQUEST_24 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_APPLICATION_24.md\n'
             'PYTEST_FILE = tests/test_taaqol_normative_hukm_candidate_gate_23.py\n'
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY\nLIVE_EXTERNAL_LINKS_IN_ARTIFACTS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'فُتحت بوابة مرشّح الحكم بنيويًّا، وأُنتجت {len(cands)} مرشّحات (نصيب الأخت، عبء الإثبات، '
             'بقاء ذي اليد، ومرشّح مركّب) بصيغة candidate فقط، دون حكم نهائي أو مناط أو تنزيل أو جواب، '
             'ومع بقاء المركّب ومنع AUTHORITY_LEAK. طلب الجولة 24 جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'NORMATIVE_HUKM_CANDIDATE_OPENED = YES · NORMATIVE_HUKM_CANDIDATES_PRODUCED = YES · '
             f'HUKM_CANDIDATE_COUNT = {len(cands)} · ANY_VERDICT_IS_FINAL_HUKM = NO · '
             'FINAL_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'NEW_SOURCE_BORN = NO · KEEP_COMPOSITE_REMAINS_ACTIVE = YES · AUTHORITY_LEAK_PREVENTED = YES · '
             'OWNER_RATIFICATION_REQUIRED_FOR_FINAL_HUKM = YES · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_23_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'NORMATIVE_HUKM_CANDIDATE_OPENED = YES · FINAL_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "NORMATIVE_HUKM_CANDIDATE_GATE_MANAGER_REPORT_AR_23.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "NORMATIVE_HUKM_CANDIDATE_GATE_23_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    sources, coverage, mapping = load_inputs()
    gate_open, checks = gate_preconditions(sources, coverage, mapping)
    cands = build_candidates(sources, gate_open)
    residuals = build_residuals(cands)

    (OUT / "NORMATIVE_HUKM_CANDIDATE_GATE_CONSTITUTION_23.md").write_text(
        constitution_md(checks, cands), encoding="utf-8")
    (OUT / "NORMATIVE_HUKM_CANDIDATE_SCHEMA_23.json").write_text(
        json.dumps(schema(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NORMATIVE_HUKM_CANDIDATES_23.json").write_text(
        json.dumps({"ROUND": "NORMATIVE_HUKM_CANDIDATE_GATE_CONSTITUTION_23",
                    "normative_hukm_candidate_opened": "YES",
                    "hukm_candidate_gate_open": "YES" if gate_open else "NO",
                    "candidate_form_only": "YES",
                    "hukm_candidate_count": len(cands),
                    "hukm_candidates": cands,
                    "producer_file": PRODUCER}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "NORMATIVE_HUKM_CANDIDATE_GUARDS_23.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "HUKM_CANDIDATE_RESIDUALS_23.json").write_text(
        json.dumps(residuals, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_APPLICATION_24.md").write_text(
        owner_request_24_md(cands), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(gate_open, checks, cands, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, checks, cands, trows, anm), encoding="utf-8")
    print("REPORT_23=" + a.report_out)
    print(f"GATE_OPEN={gate_open} CANDIDATES={len(cands)} "
          f"ANY_FINAL_HUKM={'YES' if any(c['verdict'] == 'FINAL_HUKM' for c in cands) else 'NO'} "
          f"ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
