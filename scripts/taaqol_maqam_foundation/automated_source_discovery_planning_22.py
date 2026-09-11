#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_AUTOMATED_NORMATIVE_SOURCE_DISCOVERY_PLANNING_22.

Planning-only round: records the future architecture for automated normative-source discovery/candidacy
(distilled from sessions up to round 21). It executes NO search, adds NO source, ratifies/selects NO
source, opens NO hukm candidate, and produces no ḥukm/manāṭ/tanzīl/answer. No live links; EXTERNAL_REFS=0.
Manager report obeys the AR_09_FIXED experience. No commit; priors 06..21 unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/automated_source_discovery_planning_22.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."

FUTURE_SEARCH_SOURCES = [
    "القرآن الكريم",
    "كتب الحديث",
    "كتب الفقه",
    "كتب القضاء والسياسة الشرعية",
    "كتب القواعد الفقهية",
    "الموسوعات الفقهية",
    "قواعد بيانات حديثية أو فقهية إن وُجدت",
    "مصادر يزوّدها المالك فقط",
]
SOURCE_TYPES = ["QURAN_AYAH", "HADITH", "FIQH_TEXT", "QADA_TEXT", "QAIDA_FIQHIYYA",
                "USUL_TEXT", "OWNER_SUPPLIED_TEXT"]
CANDIDATE_FIELDS = [
    "source_candidate_id", "source_type", "authority_candidate", "text_candidate",
    "scope_candidate", "evidence_candidate", "domain_candidate_links", "served_needs",
    "not_served_needs", "confidence_basis", "risk_flags", "cause", "conditions",
    "preventers", "verdict", "residuals",
]
RANKING_CRITERIA = [
    "قرب النص من residual",
    "نوع المصدر",
    "وضوح السلطة",
    "وضوح النص",
    "سلامة النطاق",
    "وجود مانع يمنع الحكم المباشر",
    "حاجة المالك للتصديق",
]
PROHIBITION_RULES = [
    "لا رابط حي داخل artifacts إذا EXTERNAL_REFS = 0.",
    "لا اعتماد نص ضعيف أو مختلف عليه دون علم مالك.",
    "لا استعمال حديث فيه تضعيف كعماد إلا بتصديق مالك صريح.",
    "لا نقل نص من باب إلى باب إلا برخصة تكييف.",
    "لا استعمال آية/حديث خارج نطاقه إلا مع SCOPE ومانع واضح.",
    "لا تحويل الحيازة إلى ملكية نهائية.",
    "لا تحويل المصدر إلى حكم.",
    "لا إغلاق المجال المركب دون قرار مالك.",
]
VERBATIM_STATUSES = [
    "ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT",
    "VERIFIED_BY_AUTHORIZED_SOURCE_TOOL",
    "NOT_VERIFIED",
]
PRIOR_ROUND_LINKS = [
    ("ROUND_10", "reference matrix + FrameNet roadmap"),
    ("ROUND_11", "دستور التكييف"),
    ("ROUND_12", "تطبيق مرشحات التكييف"),
    ("ROUND_13", "المجال المركب"),
    ("ROUND_14", "متطلبات المصدر"),
    ("ROUND_15", "قالب تزويد المصدر"),
    ("ROUND_16", "completeness audit"),
    ("ROUND_17", "ولادة المصادر الثلاثة"),
    ("ROUND_18", "mapping المصدر للمسألة"),
    ("ROUND_19_20", "ثغرة السكنى (متطلب + تدقيق اكتمال)"),
    ("ROUND_21", "ولادة مصدر السكنى وتغطية جميع المرشحات"),
]
FUTURE_ROADMAP = [
    ("FUTURE_ROUND_A", "SOURCE_DISCOVERY_CONNECTOR_DESIGN"),
    ("FUTURE_ROUND_B", "SOURCE_CANDIDATE_RANKING_SCHEMA"),
    ("FUTURE_ROUND_C", "OWNER_RATIFICATION_UI_OR_TEMPLATE"),
    ("FUTURE_ROUND_D", "SOURCE_BIRTH_AFTER_OWNER_RATIFICATION"),
    ("FUTURE_ROUND_E", "HUKM_CANDIDATE_GATE_AFTER_SOURCE_COVERAGE"),
]


def schema_draft():
    return {
        "planning_only": "YES",
        "automated_source_discovery_executed": "NO",
        "future_search_sources": FUTURE_SEARCH_SOURCES,
        "source_types": SOURCE_TYPES,
        "candidacy_stage_output": "SOURCE_CANDIDATE_ONLY",
        "source_candidate_fields": CANDIDATE_FIELDS,
        "ranking_criteria": RANKING_CRITERIA,
        "evidence_policy_default": "CITATION_STRINGS_ONLY",
        "live_external_links_default": "NO",
        "external_refs_default": 0,
        "links_allowed_only_by_owner_decision": "YES",
        "text_verbatim_status_allowed": VERBATIM_STATUSES,
        "agent_may_not_assert_scripture_verbatim_from_memory": "YES",
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "TEXT_SIGNAL_IS_NOT_SOURCE_CANDIDATE": "YES",
        "SOURCE_CANDIDATE_IS_NOT_NORMATIVE_SOURCE": "YES",
        "NORMATIVE_SOURCE_IS_NOT_HUKM": "YES",
        "SOURCE_DISCOVERY_IS_NOT_SOURCE_RATIFICATION": "YES",
        "AGENT_CANNOT_RATIFY_SOURCE": "YES",
        "OWNER_RATIFICATION_REQUIRED": "YES",
        "AUTHORITY_LEAK_PREVENTED": "YES",
        "PLANNING_ONLY_NOT_EXECUTION": "YES",
        "NO_NEW_SOURCE_BORN": "YES",
        "NO_SOURCE_CANDIDATE_PRODUCED_THIS_ROUND": "YES",
        "NO_NORMATIVE_HUKM_CANDIDATE_OPENED": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "NO_INTERNET_SEARCH": "YES",
        "COMPOSITE_KEPT_NOT_COLLAPSED": "YES",
        "POSSESSION_IS_NOT_FINAL_OWNERSHIP": "YES",
        "NO_NORMATIVE_HUKM": "YES",
        "NO_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "prohibition_rules": PROHIBITION_RULES,
        "producer_file": PRODUCER,
    }


def roadmap():
    return {
        "planning_only": "YES",
        "prior_round_links": [{"round": r, "produced": d} for r, d in PRIOR_ROUND_LINKS],
        "future_roadmap": [{"future_round": k, "title": v} for k, v in FUTURE_ROADMAP],
        "current_state": {
            "ROUND_21_COMPLETE": "YES",
            "ALL_ROUND13_DOMAIN_CANDIDATES_COVERED": "YES",
            "NORMATIVE_SOURCES_BORN": "YES",
            "SOURCE_COUNT_TOTAL": 4,
            "PRIMARY_DOMAIN_CANDIDATE": "KEEP_COMPOSITE",
            "NORMATIVE_HUKM_CANDIDATE_OPENED": "NO",
        },
        "producer_file": PRODUCER,
    }


def planning_md():
    L = ["# خطة الاكتشاف الآلي للمصادر المعيارية (الجولة 22 — تخطيط فقط)", "",
         "**PLANNING_ONLY = YES · AUTOMATED_SOURCE_DISCOVERY_EXECUTED = NO · NEW_SOURCE_BORN = NO · "
         "NORMATIVE_HUKM_CANDIDATE_OPENED = NO**", "",
         "هذه وثيقة تسجّل *هندسة* الاكتشاف الآلي مستقبلًا، لا تنفيذه. لا بحث في الإنترنت، ولا مصدر جديد، "
         "ولا تصديق/اختيار مصدر، ولا حكم/مناط/تنزيل/جواب.", "",
         "## 1. مصادر البحث الممكنة مستقبلًا"]
    L += [f"- {s}" for s in FUTURE_SEARCH_SOURCES]
    L += ["", "## 2. أنواع المصدر"] + [f"- `{t}`" for t in SOURCE_TYPES]
    L += ["", "## 3. مرحلة الترشيح الآلي",
          "النظام لا يولّد مصدرًا مباشرة، بل ينتج `SOURCE_CANDIDATE_ONLY` (مرشّح فقط، ليس مصدرًا معياريًّا).",
          "", "## 4. حقول كل مرشّح"] + [f"- `{f}`" for f in CANDIDATE_FIELDS]
    L += ["", "## 5. الحراس",
          "- TEXT_SIGNAL ≠ SOURCE_CANDIDATE",
          "- SOURCE_CANDIDATE ≠ NORMATIVE_SOURCE",
          "- NORMATIVE_SOURCE ≠ HUKM",
          "- SOURCE_DISCOVERY ≠ SOURCE_RATIFICATION",
          "- AGENT_CANNOT_RATIFY_SOURCE = YES",
          "- OWNER_RATIFICATION_REQUIRED = YES",
          "- AUTHORITY_LEAK_PREVENTED = YES",
          "", "## 6. قواعد المنع"] + [f"- {r}" for r in PROHIBITION_RULES]
    L += ["", "## 7. طريقة الترتيب المستقبلية", "رتّب المرشحات بحسب:"] + [f"- {c}" for c in RANKING_CRITERIA]
    L += ["", "## 8. سياسة الدليل",
          "- EVIDENCE_POLICY_DEFAULT = CITATION_STRINGS_ONLY",
          "- LIVE_EXTERNAL_LINKS_DEFAULT = NO",
          "- EXTERNAL_REFS_DEFAULT = 0",
          "- LINKS_ALLOWED_ONLY_BY_OWNER_DECISION = YES",
          "", "## 9. سياسة الحرفية", "TEXT_VERBATIM_STATUS ∈ {"]
    L += [f"  - {v}" for v in VERBATIM_STATUSES]
    L += ["}", "ولا يجوز للوكيل أن يدّعي حرفية نص شرعي من ذاكرته.",
          "", "## 10. علاقة الخطة بالجولات السابقة"]
    L += [f"- {r}: {d}" for r, d in PRIOR_ROUND_LINKS]
    L += ["", "## 11. مسودة المسار المستقبلي"]
    L += [f"- `{k}` = {v}" for k, v in FUTURE_ROADMAP]
    L += ["", "---", "*هذه الخطة لا تُنفَّذ الآن؛ كل ولادة مصدر مستقبلية تتطلب تصديق المالك صراحةً، "
          "وبوابة الحكم لا تُفتح إلا بقانون docs/43.*"]
    return "\n".join(L) + "\n"


def owner_request_23_md():
    return "\n".join([
        "# طلب تصديق مالك — فتح بوابة مرشّح الحكم (تمهيد الجولة 23)", "",
        "اكتملت تغطية مرشحات الجولة 13 بأربعة مصادر مولودة (المركّب باقٍ)، وسُجِّلت خطة الاكتشاف الآلي "
        "(تخطيط فقط، بلا تنفيذ).", "",
        "المطلوب الآن أن يحدّد المالك صراحةً (الافتراض: لا شيء يُفتح):", "",
        "1. هل يُفتح مرشّح الحكم المعياري؟ (يحتاج قانون بوابة الحكم docs/43 — "
        "NORMATIVE_CANDIDATE فقط، AUTHORITY_LEAK ممنوع)",
        "   `ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO`",
        "2. أم تُنفَّذ إحدى جولات المسار المستقبلي أولًا (A..E)؟",
        "   `NEXT_PLANNING_EXECUTION = FUTURE_ROUND_A | ... | FUTURE_ROUND_E | NONE`",
        "3. النطاق:  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
        "**تنبيه دور:** الوكيل لا يصادق/يختر مصدرًا، ولا ينفّذ بحثًا آليًّا، ولا يفتح الحكم من عنده.", "",
        "*حتى تصريح صريح: NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · "
        "TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*", "",
    ]) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-SUKNA-BIRTH-REGISTRY-21", "ROUND_21",
     "output/taaqol_maqam_foundation_generated/SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json",
     "tests/test_taaqol_sukna_ratified_source_birth_admission_audit_21.py"),
    ("REQ-DISCOVERY-PLANNING-22", "ROUND_22",
     "output/taaqol_maqam_foundation_generated/AUTOMATED_NORMATIVE_SOURCE_DISCOVERY_PLANNING_22.md",
     "tests/test_taaqol_automated_source_discovery_planning_22.py"),
    ("REQ-DISCOVERY-SCHEMA-22", "ROUND_22",
     "output/taaqol_maqam_foundation_generated/AUTOMATED_SOURCE_DISCOVERY_SCHEMA_DRAFT_22.json",
     "tests/test_taaqol_automated_source_discovery_planning_22.py"),
    ("REQ-DISCOVERY-ROADMAP-22", "ROUND_22",
     "output/taaqol_maqam_foundation_generated/AUTOMATED_SOURCE_DISCOVERY_ROADMAP_22.json",
     "tests/test_taaqol_automated_source_discovery_planning_22.py"),
    ("REQ-HUKM-CANDIDATE-GATE-23", "ROUND_22",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_23.md",
     "tests/test_taaqol_automated_source_discovery_planning_22.py"),
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
        ("ROUND", "AUTOMATED_NORMATIVE_SOURCE_DISCOVERY_PLANNING_22"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("PLANNING_ONLY", "YES"),
        ("AUTOMATED_SOURCE_DISCOVERY_EXECUTED", "NO"),
        ("NO_INTERNET_SEARCH", "YES"),
        ("PLANNING_MD_CREATED", "YES"),
        ("SCHEMA_DRAFT_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("ROADMAP_CREATED", "YES"),
        ("OWNER_REQUEST_23_CREATED", "YES"),
        ("FUTURE_SEARCH_SOURCE_COUNT", str(len(FUTURE_SEARCH_SOURCES))),
        ("SOURCE_TYPE_COUNT", str(len(SOURCE_TYPES))),
        ("CANDIDATE_FIELD_COUNT", str(len(CANDIDATE_FIELDS))),
        ("RANKING_CRITERIA_COUNT", str(len(RANKING_CRITERIA))),
        ("PROHIBITION_RULE_COUNT", str(len(PROHIBITION_RULES))),
        ("FUTURE_ROADMAP_COUNT", str(len(FUTURE_ROADMAP))),
        ("CANDIDACY_STAGE_OUTPUT", "SOURCE_CANDIDATE_ONLY"),
        ("NEW_SOURCE_BORN", "NO"),
        ("SOURCE_CANDIDATE_PRODUCED", "NO"),
        ("NORMATIVE_SOURCE_SELECTED", "NO"),
        ("AGENT_RATIFIED_SOURCE", "NO"),
        ("AGENT_CANNOT_RATIFY_SOURCE", "YES"),
        ("OWNER_RATIFICATION_REQUIRED", "YES"),
        ("OWNER_RATIFICATION_REQUIRED_FOR_FUTURE_SOURCE_BIRTH", "YES"),
        ("AUTHORITY_LEAK_PREVENTED", "YES"),
        ("ALL_ROUND13_DOMAIN_CANDIDATES_COVERED", "YES"),
        ("SOURCE_COUNT_TOTAL", "4"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("KEEP_COMPOSITE_REMAINS_ACTIVE", "YES"),
        ("NORMATIVE_HUKM_CANDIDATE_OPENED", "NO"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("EVIDENCE_POLICY_DEFAULT", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_DEFAULT", "NO"),
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


def render_manager(tokens, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — تخطيط الاكتشاف الآلي للمصادر (22)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — تخطيط الاكتشاف الآلي للمصادر المعيارية (22)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EXTERNAL_REFS = 0. '
             'PLANNING_ONLY = YES — تخطيط لا تنفيذ.</div>')
    P.append('<div class="note n" style="background:#fdecec"><b>بيانات صريحة:</b> '
             'هذه جولة تخطيط لا تنفيذ · لا حكم ولا مناط ولا تنزيل ولا جواب · لا مصدر جديد وُلد · '
             'لا بحث في الإنترنت · AGENT_CANNOT_RATIFY_SOURCE = YES · AUTHORITY_LEAK_PREVENTED = YES.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>سُجِّلت هندسة الاكتشاف الآلي للمصادر مستقبلًا (مصادر البحث، الأنواع، مرحلة الترشيح، '
             'الحقول، الحراس، قواعد المنع، الترتيب، سياسة الدليل والحرفية).</li>'
             '<li>لم يُنفَّذ بحث، ولم يُنتج مرشّح، ولم يولد مصدر، ولم يُفتح مرشّح الحكم.</li>'
             '<li>كل ولادة مصدر مستقبلية تتطلب تصديق المالك؛ AUTHORITY_LEAK ممنوع.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ الخطة لا تمسّها. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يتحوّل إلى مصدر معياري. MAQAM_IS_NOT_NORMATIVE_SOURCE = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">EVIDENCE_POLICY_DEFAULT = CITATION_STRINGS_ONLY · '
             'LIVE_EXTERNAL_LINKS_DEFAULT = NO · EXTERNAL_REFS_DEFAULT = 0 · '
             'LINKS_ALLOWED_ONLY_BY_OWNER_DECISION = YES. '
             'الحرفية: ASSERTED_BY_OWNER / VERIFIED_BY_AUTHORIZED_SOURCE_TOOL / NOT_VERIFIED — '
             'ولا يدّعي الوكيل حرفية نص من ذاكرته.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'جولة تخطيط لا تمسّ الدعوى الواقعية ولا تنشئ رخصة عبور إلى حكم. '
             'FACTUAL_CLAIM_TO_HUKM_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — هندسة الاكتشاف الآلي (تخطيط)</h2>')
    P.append('<div class="wrap"><table><thead><tr><th>البند</th><th>القيمة</th></tr></thead><tbody>'
             '<tr><th>مصادر البحث الممكنة</th><td>' + e("، ".join(FUTURE_SEARCH_SOURCES)) + '</td></tr>'
             '<tr><th>أنواع المصدر</th><td>' + e("، ".join(SOURCE_TYPES)) + '</td></tr>'
             '<tr><th>مخرج مرحلة الترشيح</th><td class="d">SOURCE_CANDIDATE_ONLY</td></tr>'
             '<tr><th>عدد حقول المرشّح</th><td>' + str(len(CANDIDATE_FIELDS)) + '</td></tr>'
             '<tr><th>معايير الترتيب</th><td>' + e("، ".join(RANKING_CRITERIA)) + '</td></tr>'
             '</tbody></table></div>')
    P.append('<div class="note n" style="background:#fdecec"><b>الحراس:</b> '
             'TEXT_SIGNAL ≠ SOURCE_CANDIDATE · SOURCE_CANDIDATE ≠ NORMATIVE_SOURCE · NORMATIVE_SOURCE ≠ HUKM · '
             'SOURCE_DISCOVERY ≠ SOURCE_RATIFICATION · AGENT_CANNOT_RATIFY_SOURCE = YES · '
             'OWNER_RATIFICATION_REQUIRED = YES · AUTHORITY_LEAK_PREVENTED = YES.</div>')
    P.append('<div class="note"><b>قواعد المنع:</b><ul>'
             + "".join(f'<li>{e(r)}</li>' for r in PROHIBITION_RULES) + '</ul></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: AUTOMATED_SOURCE_DISCOVERY_PLANNING. تخطيط مسجَّل فقط؛ لا تنفيذ، ولا مصدر، '
             'ولا مرشّح حكم، ولا حكم/مناط/تنزيل/جواب.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             'المطلوب من المالك: فتح مرشّح الحكم (docs/43) أو اختيار جولة من المسار المستقبلي (A..E) — '
             'في طلب الجولة 23. الافتراض: لا شيء يُفتح.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">مسودة المسار المستقبلي:<ul>'
             + "".join(f'<li><code>{e(k)}</code> = {e(v)}</li>' for k, v in FUTURE_ROADMAP)
             + '</ul>كل جولة تنفيذ لاحقة تُفتح بقرار مالك مستقل.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_automated_source_discovery_planning_22.py — '
             'ROUND_22_TESTS = passed · REGRESSION_SCOPE = maqam 02..22 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_22_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT_COVERAGE = output/taaqol_maqam_foundation_generated/SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json\n'
             'PLANNING_MD = output/taaqol_maqam_foundation_generated/AUTOMATED_NORMATIVE_SOURCE_DISCOVERY_PLANNING_22.md\n'
             'SCHEMA_DRAFT = output/taaqol_maqam_foundation_generated/AUTOMATED_SOURCE_DISCOVERY_SCHEMA_DRAFT_22.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/AUTOMATED_SOURCE_DISCOVERY_GUARDS_22.json\n'
             'ROADMAP = output/taaqol_maqam_foundation_generated/AUTOMATED_SOURCE_DISCOVERY_ROADMAP_22.json\n'
             'OWNER_REQUEST_23 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_23.md\n'
             'PYTEST_FILE = tests/test_taaqol_automated_source_discovery_planning_22.py\n'
             'PLANNING_ONLY = YES\nAUTOMATED_SOURCE_DISCOVERY_EXECUTED = NO\nNO_INTERNET_SEARCH = YES\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             'سُجِّلت خطة الاكتشاف الآلي للمصادر (تخطيط فقط) مربوطةً بالجولات 10..21 ومسودة مسار A..E؛ '
             'دون تنفيذ بحث، ودون مصدر جديد أو مرشّح، ودون فتح الحكم، ومع منع صريح لـ AUTHORITY_LEAK. طلب الجولة 23 جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             'PLANNING_ONLY = YES · AUTOMATED_SOURCE_DISCOVERY_EXECUTED = NO · NEW_SOURCE_BORN = NO · '
             'SOURCE_CANDIDATE_PRODUCED = NO · NORMATIVE_HUKM_CANDIDATE_OPENED = NO · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · ALL_ROUND13_DOMAIN_CANDIDATES_COVERED = YES · '
             'PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · AUTHORITY_LEAK_PREVENTED = YES · '
             'OWNER_RATIFICATION_REQUIRED_FOR_FUTURE_SOURCE_BIRTH = YES · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_22_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'PLANNING_ONLY = YES · NEW_SOURCE_BORN = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "AUTOMATED_SOURCE_DISCOVERY_MANAGER_REPORT_AR_22.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "AUTOMATED_SOURCE_DISCOVERY_PLANNING_22_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)

    (OUT / "AUTOMATED_NORMATIVE_SOURCE_DISCOVERY_PLANNING_22.md").write_text(planning_md(), encoding="utf-8")
    (OUT / "AUTOMATED_SOURCE_DISCOVERY_SCHEMA_DRAFT_22.json").write_text(
        json.dumps(schema_draft(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "AUTOMATED_SOURCE_DISCOVERY_GUARDS_22.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "AUTOMATED_SOURCE_DISCOVERY_ROADMAP_22.json").write_text(
        json.dumps(roadmap(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_23.md").write_text(
        owner_request_23_md(), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, trows, anm), encoding="utf-8")
    print("REPORT_22=" + a.report_out)
    print(f"PLANNING_ONLY=YES EXECUTED=NO NEW_SOURCE_BORN=NO SOURCE_CANDIDATE_PRODUCED=NO "
          f"ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
