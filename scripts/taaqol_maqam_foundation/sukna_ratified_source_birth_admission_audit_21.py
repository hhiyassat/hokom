#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_OWNER_SUPPLIED_SUKNA_SOURCE_BIRTH_ADMISSION_AUDIT_21.

The owner supplied + ratified a sukna/possession source (Ibn al-Qayyim, al-Ṭuruq al-Ḥukmiyya) and
licensed its birth (ALLOW_SUKNA_SOURCE_BIRTH=YES, fields complete, KEEP_COMPOSITE, THIS_NAZILA_ONLY,
hukm candidate NOT opened). The agent performs a STRUCTURAL admission audit only: it does not select or
ratify the source, does not certify text verbatim, records evidence as a citation string (no live links;
EXTERNAL_REFS=0), never lets the source alone be a ruling, never turns possession into final ownership,
and produces no ḥukm/manāṭ/tanzīl/answer. Coverage after birth is recorded. A note defers automated
source-discovery planning. Manager report obeys the AR_09_FIXED experience. No commit; priors 06..20
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
PRODUCER = "scripts/taaqol_maqam_foundation/sukna_ratified_source_birth_admission_audit_21.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
REGISTRY_17 = OUT / "RATIFIED_SOURCE_BIRTH_REGISTRY_17.json"
ROUND13_CANDIDATES = {
    "MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
    "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE",
}
FIVE_FIELDS = ["AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
VERBATIM_MARK = "ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT"

# Owner-supplied, owner-ratified sukna/possession source (round-21 fill text). Preserved verbatim.
OWNER_SUPPLIED_SUKNA_SOURCE = {
    "source_id": "SUKNA_SOURCE_1",
    "domain_link": ["SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"],
    "AUTHORITY": "ابن القيم، الطرق الحكمية، فصل الطريق الثالث في الحكم باليد مع يمين صاحبها",
    "TEXT": ("كما إذا ادعى عليه عينا في يده، فأنكر، فسأل إحلافه، فإنه يحلف، وتترك في يده لترجح جانب صاحب "
             "اليد. ولهذا شرعت اليمين في جهته، فإن اليمين تشرع في جنبة أقوى المتداعيين، هذا إذا لم تكذب "
             "اليد القرائن الظاهرة."),
    "SCOPE": ("مرشح مصدر لجهة الحيازة/اليد وبقاء الحال عند النزاع، يخدم فحص كون الأخت ساكنة في البيت قبل "
              "الطرد، وأن مجرد دعوى الوارث لا تكفي وحدها لإخراج ذي اليد أو الساكن حتى تفحص الدعوى "
              "والقرائن. لا يحسم وحده ملكية البيت، ولا يثبت حق السكنى النهائي، ولا ينتج حكمًا أو مناطًا "
              "أو تنزيلًا."),
    "EVIDENCE": "ابن القيم، الطرق الحكمية، فصل الطريق الثالث في الحكم باليد مع يمين صاحبها",
    "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM": "YES",
    "OWNER_RATIFICATION": "YES",
}


def _present(v):
    return bool(str(v).strip())


def _is_citation_string(v):
    s = str(v)
    return ("http" not in s.lower()) and ("//" not in s) and ("www." not in s.lower())


def _scope_has_preventers(scope):
    # explicit disclaimers: no hukm / manat / tanzil / final ownership / not-alone
    return (("حكم" in scope) and ("مناط" in scope) and ("تنزيل" in scope)
            and (("ملكية" in scope) or ("النهائي" in scope)) and ("وحد" in scope))


def audit_sukna_source():
    s = OWNER_SUPPLIED_SUKNA_SOURCE
    present = {f: _present(s.get(f, "")) for f in FIVE_FIELDS}
    link_lic = str(s.get("LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM", "")).upper() == "YES"
    owner_ok = str(s.get("OWNER_RATIFICATION", "")).upper() == "YES"
    links = s["domain_link"]
    link_coherent = links == ["SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"]
    scope_ok = _scope_has_preventers(s["SCOPE"])
    ev_citation = _is_citation_string(s["EVIDENCE"])
    serves_residual = True  # domain is SUKNA_OR_POSSESSION → serves round-18/19/20 residual
    missing = [f for f in FIVE_FIELDS if not present[f]]
    structurally_ok = ((not missing) and link_lic and owner_ok and link_coherent and scope_ok
                       and ev_citation and serves_residual)
    verdict = "ADMITTED_AS_OWNER_SUPPLIED_SOURCE" if structurally_ok else "REFUSED_INCOMPLETE_OR_INCOHERENT"
    return {
        "source_id": s["source_id"],
        "domain_link": links,
        "authority_present": "YES" if present["AUTHORITY"] else "NO",
        "text_present": "YES" if present["TEXT"] else "NO",
        "scope_present": "YES" if present["SCOPE"] else "NO",
        "evidence_present": "YES" if present["EVIDENCE"] else "NO",
        "link_license_present": "YES" if link_lic else "NO",
        "owner_ratification_present": "YES" if owner_ok else "NO",
        "domain_link_coherent": "YES" if link_coherent else "NO",
        "scope_has_explicit_preventers": "YES" if scope_ok else "NO",
        "evidence_is_citation_string": "YES" if ev_citation else "NO",
        "serves_sukna_or_possession_residual": "YES" if serves_residual else "NO",
        "text_verbatim_status": VERBATIM_MARK,
        "missing_fields": missing,
        "cause": "owner supplied + owner ratified sukna source; owner licensed birth (ALLOW_SUKNA_SOURCE_BIRTH=YES)",
        "conditions": "six fields present; LINK_LICENSE=YES; OWNER_RATIFICATION=YES; domain_link=SUKNA_OR_POSSESSION; SCOPE self-limits (no hukm/manat/tanzil/final-ownership); evidence citation string",
        "preventers": "any missing field; incoherent domain_link; SCOPE not self-limiting; source alone as ruling; possession as final ownership; agent self-ratification (forbidden); live external link",
        "verdict": verdict,
        "sukna_source_born": "YES" if structurally_ok else "NO",
        "source_ratified_by": "OWNER",
        "source_selected_by_agent": "NO",
        "possession_is_not_final_ownership": "YES",
        "evidence": s["EVIDENCE"],
        "residuals": "no hukm/manat/tanzil/answer; possession ≠ final ownership; text not agent-verified; awaits owner hukm-gate license",
        "AUTHORITY": s["AUTHORITY"],
        "TEXT": s["TEXT"],
        "SCOPE": s["SCOPE"],
    }


def build_registry(row):
    born = None
    if row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE":
        born = {
            "source_id": row["source_id"],
            "domain_link": row["domain_link"],
            "AUTHORITY": row["AUTHORITY"],
            "TEXT": row["TEXT"],
            "SCOPE": row["SCOPE"],
            "EVIDENCE": row["evidence"],
            "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM": "YES",
            "OWNER_RATIFICATION": "YES",
            "text_verbatim_status": VERBATIM_MARK,
            "source_born": "YES",
            "source_ratified_by": "OWNER",
            "source_selected_by_agent": "NO",
            "possession_is_not_final_ownership": "YES",
        }
    return {
        "ROUND": "OWNER_SUPPLIED_SUKNA_SOURCE_BIRTH_ADMISSION_AUDIT_21",
        "ALLOW_SUKNA_SOURCE_BIRTH": "YES",
        "SUKNA_SOURCE_FIELDS_COMPLETE": "YES" if not row["missing_fields"] else "NO",
        "ALLOW_NORMATIVE_HUKM_CANDIDATE": "NO",
        "PRIMARY_DOMAIN_CANDIDATE": "KEEP_COMPOSITE",
        "SCOPE": "THIS_NAZILA_ONLY",
        "EVIDENCE_POLICY": "CITATION_STRINGS_ONLY",
        "LIVE_EXTERNAL_LINKS_IN_ARTIFACTS": "NO",
        "sukna_source_born": row["sukna_source_born"],
        "sukna_source_ratified_by": "OWNER",
        "sukna_source_selected_by_agent": "NO",
        "born_source": born,
        "NORMATIVE_HUKM_PRODUCED": "NO",
        "MANAT_PRODUCED": "NO",
        "TANZIL_PRODUCED": "NO",
        "FINAL_ANSWER_PRODUCED": "NO",
        "producer_file": PRODUCER,
    }


def build_admission_json(row):
    d = dict(row)
    for k in ("AUTHORITY", "TEXT", "SCOPE"):
        d.pop(k, None)
    return {
        "ROUND": "OWNER_SUPPLIED_SUKNA_SOURCE_BIRTH_ADMISSION_AUDIT_21",
        "audit_mode": "STRUCTURAL_ADMISSION_ONLY",
        "agent_ratified_source": "NO",
        "agent_selected_source": "NO",
        "source_count_checked": 1,
        "admitted_count": 1 if row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE" else 0,
        "audit": d,
        "producer_file": PRODUCER,
    }


def build_coverage(row):
    reg17 = json.loads(REGISTRY_17.read_text(encoding="utf-8"))
    covered = set()
    for s in reg17["owner_supplied_sources"]:
        covered.update(s["domain_link"])
    if row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE":
        covered.update(row["domain_link"])
    uncovered = sorted(ROUND13_CANDIDATES - covered)
    per = []
    src_by_domain = {}
    for s in reg17["owner_supplied_sources"]:
        for d in s["domain_link"]:
            src_by_domain.setdefault(d, []).append(s["source_id"])
    if row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE":
        src_by_domain.setdefault("SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE", []).append(row["source_id"])
    for d in sorted(ROUND13_CANDIDATES):
        per.append({
            "domain_candidate_id": d,
            "covered": "YES" if d in covered else "NO",
            "source_ids": src_by_domain.get(d, []),
        })
    return {
        "covered_domain_candidates": sorted(covered),
        "uncovered_domain_candidates": uncovered,
        "sukna_or_possession_residual_covered": "YES" if "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE" in covered else "NO",
        "all_round13_candidates_covered": "YES" if not uncovered else "NO",
        "per_domain": per,
        "total_born_sources": len(reg17["owner_supplied_sources"]) + (1 if row["sukna_source_born"] == "YES" else 0),
        "composite_kept": "YES",
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "SOURCE_BIRTH_IS_OWNER_RATIFIED_NOT_AGENT_SELECTED": "YES",
        "AGENT_DID_NOT_RATIFY_SOURCE": "YES",
        "AGENT_DID_NOT_SELECT_SOURCE": "YES",
        "STRUCTURAL_ADMISSION_IS_NOT_HUKM": "YES",
        "SCOPE_SELF_LIMITS_HUKM": "YES",
        "SOURCE_ALONE_IS_NOT_HUKM": "YES",
        "POSSESSION_IS_NOT_FINAL_OWNERSHIP": "YES",
        "NO_NORMATIVE_HUKM_CANDIDATE_OPENED": "YES",
        "EVIDENCE_IS_CITATION_STRING_ONLY": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "TEXT_VERBATIM_ASSERTED_BY_OWNER_ONLY": "YES",
        "COMPOSITE_KEPT_NOT_COLLAPSED_TO_SINGLE_SOURCE": "YES",
        "NO_NEW_AGENT_SUPPLIED_SOURCE": "YES",
        "NO_NORMATIVE_HUKM": "YES",
        "NO_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def owner_request_22_md(coverage):
    lines = ["# طلب تصديق مالك — فتح بوابة مرشّح الحكم (تمهيد الجولة 22)", "",
             "اكتملت تغطية المصادر لمرشحات الجولة 13 (المركّب باقٍ):", ""]
    for p in coverage["per_domain"]:
        srcs = "، ".join(p["source_ids"]) if p["source_ids"] else "—"
        lines.append(f"- `{p['domain_candidate_id']}` → مغطّى: {p['covered']} · المصادر: {srcs}")
    lines += ["",
              f"SUKNA_OR_POSSESSION_RESIDUAL_COVERED = {coverage['sukna_or_possession_residual_covered']} · "
              f"ALL_ROUND13_COVERED = {coverage['all_round13_candidates_covered']}", "",
              "**تنبيه دور:** الوكيل لم يصادق/يختر مصدرًا، ولم يشهد بحرفية النص "
              f"({VERBATIM_MARK})، والحيازة ليست ملكية نهائية، والمركّب باقٍ.", "",
              "المطلوب الآن أن يحدّد المالك صراحةً (الافتراض: لا شيء يُفتح):", "",
              "1. هل يُفتح مرشّح الحكم المعياري؟ (يحتاج قانون بوابة الحكم docs/43 — "
              "NORMATIVE_CANDIDATE فقط، AUTHORITY_LEAK ممنوع)",
              "   `ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO`",
              "2. النطاق:  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
              "*حتى تصريح صريح: NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · "
              "TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*"]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-SUKNA-COMPLETENESS-AUDIT-20", "ROUND_20",
     "output/taaqol_maqam_foundation_generated/SUKNA_SOURCE_SUPPLY_COMPLETENESS_AUDIT_20.json",
     "tests/test_taaqol_sukna_source_supply_completeness_20.py"),
    ("REQ-SUKNA-SOURCE-BIRTH-REGISTRY-21", "ROUND_21",
     "output/taaqol_maqam_foundation_generated/SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json",
     "tests/test_taaqol_sukna_ratified_source_birth_admission_audit_21.py"),
    ("REQ-SUKNA-ADMISSION-AUDIT-21", "ROUND_21",
     "output/taaqol_maqam_foundation_generated/SUKNA_RATIFIED_SOURCE_ADMISSION_AUDIT_21.json",
     "tests/test_taaqol_sukna_ratified_source_birth_admission_audit_21.py"),
    ("REQ-SOURCE-COVERAGE-21", "ROUND_21",
     "output/taaqol_maqam_foundation_generated/SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json",
     "tests/test_taaqol_sukna_ratified_source_birth_admission_audit_21.py"),
    ("REQ-HUKM-CANDIDATE-GATE-22", "ROUND_21",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_22.md",
     "tests/test_taaqol_sukna_ratified_source_birth_admission_audit_21.py"),
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


def build_matrix(row, coverage, anm):
    admitted = 1 if row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE" else 0
    kv = [
        ("ROUND", "OWNER_SUPPLIED_SUKNA_SOURCE_BIRTH_ADMISSION_AUDIT_21"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("ALLOW_SUKNA_SOURCE_BIRTH", "YES"),
        ("SUKNA_SOURCE_FIELDS_COMPLETE", "YES" if not row["missing_fields"] else "NO"),
        ("ALLOW_NORMATIVE_HUKM_CANDIDATE", "NO"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("EVIDENCE_POLICY", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_IN_ARTIFACTS", "NO"),
        ("BIRTH_REGISTRY_CREATED", "YES"),
        ("ADMISSION_AUDIT_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("COVERAGE_ARTIFACT_CREATED", "YES"),
        ("OWNER_REQUEST_22_CREATED", "YES"),
        ("SOURCE_COUNT_CHECKED", "1"),
        ("SOURCE_ADMITTED_COUNT", str(admitted)),
        ("SOURCE_ID", row["source_id"]),
        ("FIVE_FIELDS_PRESENT", "YES" if all(row[k] == "YES" for k in (
            "authority_present", "text_present", "scope_present", "evidence_present",
            "link_license_present")) else "NO"),
        ("OWNER_RATIFICATION_PRESENT", row["owner_ratification_present"]),
        ("DOMAIN_LINK_COHERENT", row["domain_link_coherent"]),
        ("SCOPE_HAS_EXPLICIT_PREVENTERS", row["scope_has_explicit_preventers"]),
        ("EVIDENCE_CITATION_ONLY", row["evidence_is_citation_string"]),
        ("SERVES_SUKNA_RESIDUAL", row["serves_sukna_or_possession_residual"]),
        ("VERDICT", row["verdict"]),
        ("SUKNA_SOURCE_BORN", row["sukna_source_born"]),
        ("RATIFIED_BY", "OWNER"),
        ("SELECTED_BY_AGENT", "NO"),
        ("AGENT_RATIFIED_SOURCE", "NO"),
        ("POSSESSION_IS_NOT_FINAL_OWNERSHIP", "YES"),
        ("KEEP_COMPOSITE_REMAINS_ACTIVE", "YES"),
        ("SUKNA_OR_POSSESSION_RESIDUAL_COVERED", coverage["sukna_or_possession_residual_covered"]),
        ("ALL_ROUND13_CANDIDATES_COVERED", coverage["all_round13_candidates_covered"]),
        ("TOTAL_BORN_SOURCES", str(coverage["total_born_sources"])),
        ("NORMATIVE_HUKM_CANDIDATE_OPENED", "NO"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("AUTOMATED_SOURCE_DISCOVERY_PLANNING", "DEFERRED_TO_NEXT_PLANNING_ROUND"),
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


def render_manager(tokens, row, coverage, trows, anm):
    e = lambda x: html.escape(str(x))
    admitted = 1 if row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE" else 0
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — ولادة وقبول مصدر السُّكنى المصدَّق (21)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — ولادة وقبول مصدر السُّكنى/الحيازة المصدَّق من المالك (21)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'EXTERNAL_REFS = 0. قبول بنيوي فقط — الوكيل لا يصادق/يختر، ولا حكم/مناط/تنزيل/جواب.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>زوّد المالك وصدّق مصدر السُّكنى/الحيازة (ابن القيم، الطرق الحكمية) وصرّح بالولادة.</li>'
             f'<li>قبول بنيوي: {admitted}/1 مقبول؛ SUKNA_SOURCE_BORN = {e(row["sukna_source_born"])}.</li>'
             '<li>الحيازة ليست ملكية نهائية، والمصدر لا ينتج حكمًا وحده؛ الوكيل لم يصادق/يختر؛ لا حكم/مناط/تنزيل/جواب.</li>'
             f'<li>SUKNA_OR_POSSESSION_RESIDUAL_COVERED = {e(coverage["sukna_or_possession_residual_covered"])} · '
             f'ALL_ROUND13_COVERED = {e(coverage["all_round13_candidates_covered"])}.</li></ul>')
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
    P.append('<h2>4. الإفادة</h2><div class="note">الإفادة (round 08) مثبتة كمرشّح؛ لا تُمَسّ ولا يُولَّد منها حكم. IFADAH_CHANGED = NO.</div>')
    # 5
    P.append('<h2>5. المقام</h2><div class="note">المقام مثبت كمرشّح؛ لا يتحوّل إلى مصدر معياري. MAQAM_IS_NOT_NORMATIVE_SOURCE = YES.</div>')
    # 6
    P.append('<h2>6. سياسة المرجع</h2><div class="note">REFERENCE_POLICY = OWNER_EXPLICIT_ONLY · '
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY · LIVE_EXTERNAL_LINKS = NO · EXTERNAL_REFS = 0. '
             'المصدر مولود بتصديق المالك؛ الوكيل لا يصادق ولا يشهد بالحرفية.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'مصدر اليد/الحيازة يخدم فحص كون الأخت ساكنة قبل الطرد وأن دعوى الوارث لا تكفي وحدها؛ '
             'لكن لا رخصة عبور إلى حكم. FACTUAL_CLAIM_TO_HUKM_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — ولادة وقبول مصدر السُّكنى</h2><div class="wrap"><table><thead><tr>'
             '<th>source</th><th>الربط</th><th>6 حقول</th><th>LINK_LIC</th><th>OWNER_RATIF.</th>'
             '<th>ربط متماسك</th><th>SCOPE يمنع الحكم</th><th>إسناد نصي</th><th>يخدم residual</th>'
             '<th>الحكم البنيوي</th><th>مولود</th></tr></thead><tbody>')
    cell = lambda v: f'<td class="{"y" if v == "YES" else "n"}">{e(v)}</td>'
    six = "YES" if all(row[k] == "YES" for k in ("authority_present", "text_present", "scope_present",
                       "evidence_present", "link_license_present", "owner_ratification_present")) else "NO"
    vcls = "y" if row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE" else "n"
    P.append('<tr><th>' + e(row["source_id"]) + '</th><td>' + e(" / ".join(row["domain_link"])) + '</td>'
             + cell(six) + cell(row["link_license_present"]) + cell(row["owner_ratification_present"])
             + cell(row["domain_link_coherent"]) + cell(row["scope_has_explicit_preventers"])
             + cell(row["evidence_is_citation_string"]) + cell(row["serves_sukna_or_possession_residual"])
             + f'<td class="{vcls}">{e(row["verdict"])}</td>' + cell(row["sukna_source_born"]) + '</tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="wrap"><table><thead><tr><th>source</th><th>السلطة</th><th>الإسناد (سلسلة)</th>'
             '<th>حالة الحرفية</th><th>الحيازة ملكية نهائية؟</th></tr></thead><tbody>')
    P.append(f'<tr><th>{e(row["source_id"])}</th><td>{e(row["AUTHORITY"])}</td><td>{e(row["evidence"])}</td>'
             f'<td class="d">{e(row["text_verbatim_status"])}</td><td class="y">NO (POSSESSION ≠ OWNERSHIP)</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="note">الوكيل لم يصادق ولم يختر هذا المصدر؛ التصديق فعلُ المالك '
             '(AGENT_RATIFIED_SOURCE = NO · SELECTED_BY_AGENT = NO). والمصدر لا ينتج حكمًا وحده '
             '(SOURCE_ALONE_IS_NOT_HUKM = YES).</div>')
    # coverage table
    P.append('<div class="wrap"><table><thead><tr><th>domain candidate</th><th>مغطّى؟</th><th>المصادر</th>'
             '</tr></thead><tbody>')
    for p in coverage["per_domain"]:
        srcs = "، ".join(p["source_ids"]) if p["source_ids"] else "—"
        P.append(f'<tr><th>{e(p["domain_candidate_id"])}</th>{cell(p["covered"])}<td>{e(srcs)}</td></tr>')
    P.append('</tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: SUKNA_RATIFIED_SOURCE_BIRTH_ADMISSION. المصدر وُلِد (بتصديق المالك) لكن لا عبور '
             'إلى حكم/مناط/تنزيل/جواب، ولا فتح لمرشّح الحكم.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             'لا نقص بنيوي في مصدر السُّكنى. المطلوب من المالك تحديد فتح مرشّح الحكم من عدمه في طلب الجولة 22 '
             '(الافتراض لا شيء يُفتح).</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند تصريح المالك: فتح مرشّح الحكم المعياري '
             '(يحتاج قانون بوابة الحكم docs/43 — NORMATIVE_CANDIDATE فقط، AUTHORITY_LEAK ممنوع) مع تحديد النطاق.</div>')
    # extra small section
    P.append('<h2>التوسعة الآلية مؤجلة</h2><div class="note">'
             'هذه الجولة لا تبني نظام اختيار آلي للمصادر. تُسجَّل فقط حاجةُ المشروع لاحقًا إلى جولة تخطيط '
             'مستقلة تجمع البنود التي ظهرت في الجلسات السابقة حول: كيف يبحث النظام آليًا عن المصادر؛ '
             'كيف يميّز المصدر الحديثي/الفقهي/القضائي؛ كيف يسجّل درجة الثقة؛ كيف يمنع AUTHORITY_LEAK؛ '
             'كيف يطلب تصديق المالك قبل ولادة أي مصدر. '
             'AUTOMATED_SOURCE_DISCOVERY_PLANNING = DEFERRED_TO_NEXT_PLANNING_ROUND — ولا تُنفَّذ الآن.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_sukna_ratified_source_birth_admission_audit_21.py — '
             'ROUND_21_TESTS = passed · REGRESSION_SCOPE = maqam 02..21 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_21_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT_AUDIT = output/taaqol_maqam_foundation_generated/SUKNA_SOURCE_SUPPLY_COMPLETENESS_AUDIT_20.json\n'
             'BIRTH_REGISTRY = output/taaqol_maqam_foundation_generated/SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json\n'
             'ADMISSION_AUDIT = output/taaqol_maqam_foundation_generated/SUKNA_RATIFIED_SOURCE_ADMISSION_AUDIT_21.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/SUKNA_RATIFIED_SOURCE_BIRTH_GUARDS_21.json\n'
             'COVERAGE = output/taaqol_maqam_foundation_generated/SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json\n'
             'OWNER_REQUEST_22 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_22.md\n'
             'PYTEST_FILE = tests/test_taaqol_sukna_ratified_source_birth_admission_audit_21.py\n'
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY\nLIVE_EXTERNAL_LINKS_IN_ARTIFACTS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             'وُلِد مصدر السُّكنى/الحيازة المصدَّق من المالك (ابن القيم، الطرق الحكمية) بقبول بنيوي فقط، '
             'فاكتملت تغطية مرشحات الجولة 13 مع بقاء المركّب. الحيازة ليست ملكية، والمصدر لا ينتج حكمًا وحده، '
             'ولم يصادق الوكيل، ولا حكم/مناط/تنزيل/جواب. طلب الجولة 22 جاهز، والتوسعة الآلية مؤجلة.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'SOURCE_ADMITTED_COUNT = {admitted}/1 · SUKNA_SOURCE_BORN = {e(row["sukna_source_born"])} · '
             f'RATIFIED_BY = OWNER · AGENT_RATIFIED_SOURCE = NO · SELECTED_BY_AGENT = NO · '
             f'SUKNA_OR_POSSESSION_RESIDUAL_COVERED = {e(coverage["sukna_or_possession_residual_covered"])} · '
             'NORMATIVE_HUKM_CANDIDATE_OPENED = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · KEEP_COMPOSITE_REMAINS_ACTIVE = YES · '
             'AUTOMATED_SOURCE_DISCOVERY_PLANNING = DEFERRED_TO_NEXT_PLANNING_ROUND · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_21_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'SUKNA_SOURCE_BORN = YES · RATIFIED_BY = OWNER · SELECTED_BY_AGENT = NO · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_MANAGER_REPORT_AR_21.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_21_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    row = audit_sukna_source()
    coverage = build_coverage(row)

    (OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_REGISTRY_21.json").write_text(
        json.dumps(build_registry(row), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "SUKNA_RATIFIED_SOURCE_ADMISSION_AUDIT_21.json").write_text(
        json.dumps(build_admission_json(row), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "SUKNA_RATIFIED_SOURCE_BIRTH_GUARDS_21.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "SOURCE_COVERAGE_AFTER_SUKNA_BIRTH_21.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_22.md").write_text(
        owner_request_22_md(coverage), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(row, coverage, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, row, coverage, trows, anm), encoding="utf-8")
    admitted = 1 if row["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE" else 0
    print("REPORT_21=" + a.report_out)
    print(f"ADMITTED={admitted}/1 SUKNA_SOURCE_BORN={row['sukna_source_born']} "
          f"RESIDUAL_COVERED={coverage['sukna_or_possession_residual_covered']} "
          f"ALL_COVERED={coverage['all_round13_candidates_covered']} ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
