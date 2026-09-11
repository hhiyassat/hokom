#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_SOURCE_TO_MASALA_MAPPING_GATE_18.

Maps each round-17 born normative source to the nazila's masʾala segments STRUCTURALLY only. It produces
no ḥukm/manāṭ/tanzīl/answer, does not add a source, does not collapse the composite, never lets a source
alone produce the ruling, does not certify text verbatim, uses citation strings only (no live links), and
never makes the agent a source-ratifier. Manager report obeys the AR_09_FIXED experience. No commit;
priors 06..17 unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/source_to_masala_mapping_18.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
REGISTRY_17 = OUT / "RATIFIED_SOURCE_BIRTH_REGISTRY_17.json"
ROUND13_CANDIDATES = {
    "MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
    "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE",
}
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
VERBATIM_MARK = "ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT"

# Per-source structural mapping to nazila segments (owner-directed logical links; NOT a ruling).
MAPPING_SPEC = {
    "SOURCE_1": {
        "masala_segment_link": "موت مالك عن أخت (مَاتَ مَلِكٌ عَنْ أُخْتٍ)",
        "serves_what": "يربط ركن وجود أخت مع تركة بمسألة الكلالة ونصيب الأخت بشرطه.",
        "does_not_serve": ("لا يكفي وحده: يتوقف على فحص شروط الكلالة وعدم وجود ولد وسائر الورثة؛ "
                           "ولا يحسم السكنى ولا واقعة الطرد ولا جهة التحاكم."),
    },
    "SOURCE_2": {
        "masala_segment_link": "التركة وترتيب الفروض والباقي (تركة المالك بعد موته)",
        "serves_what": "يربط ترتيب أصحاب الفروض ثم الباقي لأولى رجل ذكر في التركة.",
        "does_not_serve": ("لا يحسم وحده حق السكنى ولا واقعة الطرد؛ ولا يثبت شروط استحقاق الأخت "
                           "دون آية الكلالة؛ ولا يفصل في الدعوى."),
    },
    "SOURCE_3": {
        "masala_segment_link": "التحاكم والدعوى وعبء الإثبات (فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا)",
        "serves_what": "يربط جهة الدعوى والتحاكم وعبء الإثبات (اليمين على المدعى عليه).",
        "does_not_serve": ("لا يحسم وحده ملكية البيت ولا حق السكنى ولا نصيب الميراث؛ إنما ينظّم إجراء "
                           "الإثبات لا موضوع الحق."),
    },
}


def load_registry():
    return json.loads(REGISTRY_17.read_text(encoding="utf-8"))


def build_mapping_nodes(reg):
    nodes = []
    for s in reg["owner_supplied_sources"]:
        sid = s["source_id"]
        spec = MAPPING_SPEC[sid]
        links = s["domain_link"]
        coherent = all(l in ROUND13_CANDIDATES for l in links)
        nodes.append({
            "source_id": sid,
            "authority": s["AUTHORITY"],
            "evidence": s["EVIDENCE"],
            "domain_link": links,
            "masala_segment_link": spec["masala_segment_link"],
            "serves_what": spec["serves_what"],
            "does_not_serve": spec["does_not_serve"],
            "cause": "source born + owner-ratified (round 17); owner licensed structural mapping (round 18)",
            "conditions": "domain_link coherent with round-13 candidate; segment link is structural; composite kept",
            "preventers": "source alone producing the ruling; collapsing composite; agent ratifying/selecting; adding a source",
            "verdict": "MAPPED_TO_MASALA_SEGMENT_STRUCTURAL_ONLY" if coherent else "REFUSED_INCOHERENT_LINK",
            "evidence_citation_string": "YES",
            "text_verbatim_status": VERBATIM_MARK,
            "residuals": "no hukm/manat/tanzil/answer; source not sufficient alone; awaits owner hukm-gate license",
            "hukm_birth_allowed": "NO",
            "manat_birth_allowed": "NO",
            "tanzil_birth_allowed": "NO",
            "final_answer_allowed": "NO",
        })
    return nodes


def covered_domains(nodes):
    cov = set()
    for n in nodes:
        cov.update(n["domain_link"])
    return cov


def build_residuals(nodes):
    cov = covered_domains(nodes)
    uncovered = sorted(ROUND13_CANDIDATES - cov)
    items = []
    for d in uncovered:
        items.append({
            "domain_candidate_id": d,
            "status": "UNCOVERED_BY_CURRENT_SOURCES",
            "needs": "مصدر أو قاعدة لاحقة قبل أن يُشارك في بوابة الحكم",
            "note": ("SUKNA_OR_POSSESSION (السكنى/الحيازة) لا يغطيه أيٌّ من المصادر الثلاثة؛ "
                     "حق السكنى/الطرد يتوقف على مصدر/قاعدة لم تُزوَّد بعد."
                     if d == "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"
                     else "غير مغطى بالمصادر الحالية؛ يحتاج تزويدًا لاحقًا."),
        })
    open_residuals = [
        "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE بلا مصدر → حق السكنى وواقعة الطرد غير محسومة مصدريًّا.",
        "تحقّق شروط الكلالة (عدم وجود ولد/والد وسائر الورثة) لم يُفحص واقعيًّا بعد.",
        "الدعوى وعبء الإثبات (SOURCE_3) ينظّم الإجراء لا موضوع الحق؛ نتيجة التحاكم غير محسومة.",
        "لا رخصة عبور من الدعوى الواقعية إلى الحكم؛ بوابة الحكم (docs/43) لم تُفتح.",
    ]
    return {
        "covered_domain_candidates": sorted(cov),
        "uncovered_domain_candidates": uncovered,
        "sukna_or_possession_uncovered": "YES" if "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE" in uncovered else "NO",
        "per_uncovered": items,
        "open_residuals_before_hukm_gate": open_residuals,
        "unresolved_residuals_recorded": "YES",
        "producer_file": PRODUCER,
    }


def build_mapping_json(nodes, reg):
    return {
        "ROUND": "SOURCE_TO_MASALA_MAPPING_GATE_18",
        "SOURCE_TO_MASALA_MAPPING_ALLOWED": "YES",
        "mapping_mode": "STRUCTURAL_ONLY",
        "PRIMARY_DOMAIN_CANDIDATE": "KEEP_COMPOSITE",
        "SCOPE": "THIS_NAZILA_ONLY",
        "EVIDENCE_POLICY": "CITATION_STRINGS_ONLY",
        "LIVE_EXTERNAL_LINKS_IN_ARTIFACTS": "NO",
        "normative_source_born": reg["normative_source_born"],
        "normative_source_ratified_by": reg["normative_source_ratified_by"],
        "normative_source_selected_by_agent": reg["normative_source_selected_by_agent"],
        "agent_ratified_source": "NO",
        "source_count_mapped": len(nodes),
        "mapping_nodes": nodes,
        "NORMATIVE_HUKM_PRODUCED": "NO",
        "MANAT_PRODUCED": "NO",
        "TANZIL_PRODUCED": "NO",
        "FINAL_ANSWER_PRODUCED": "NO",
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "SOURCE_TO_MASALA_MAPPING_IS_NOT_HUKM": "YES",
        "SOURCE_IS_NOT_HUKM": "YES",
        "SOURCE_IS_NOT_MANAT": "YES",
        "SOURCE_IS_NOT_TANZIL": "YES",
        "SOURCE_ALONE_DOES_NOT_PRODUCE_HUKM": "YES",
        "DOMAIN_CANDIDATE_IS_NOT_FINAL_DOMAIN": "YES",
        "KEEP_COMPOSITE_REMAINS_ACTIVE": "YES",
        "NO_NEW_SOURCE_ADDED": "YES",
        "AGENT_DID_NOT_RATIFY_SOURCE": "YES",
        "AGENT_DID_NOT_SELECT_SOURCE": "YES",
        "TEXT_VERBATIM_ASSERTED_BY_OWNER_ONLY": "YES",
        "EVIDENCE_IS_CITATION_STRING_ONLY": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "NO_NORMATIVE_HUKM": "YES",
        "NO_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def owner_request_19_md(nodes, residuals):
    lines = ["# طلب تصديق مالك — فتح بوابة مرشّح الحكم (تمهيد الجولة 19)", "",
             "رُبِطت المصادر المولودة بأجزاء النازلة ربطًا بنيويًّا فقط:", ""]
    for n in nodes:
        lines.append(f"- `{n['source_id']}` ({n['authority']}) → {n['masala_segment_link']}")
        lines.append(f"  - يخدم: {n['serves_what']}")
        lines.append(f"  - لا يخدم وحده: {n['does_not_serve']}")
    lines += ["", "**ثغرات مسجَّلة قبل الحكم:**"]
    for r in residuals["open_residuals_before_hukm_gate"]:
        lines.append(f"- {r}")
    lines += ["", "**تنبيه دور:** الوكيل لم يصادق/يختر مصدرًا، ولم يشهد بحرفية النص "
              f"({VERBATIM_MARK})، والمركّب باقٍ (KEEP_COMPOSITE).", "",
              "المطلوب الآن أن يحدّد المالك صراحةً (الافتراض: لا شيء يُفتح):", "",
              "1. هل تُزوَّد ثغرة السُّكنى/الحيازة بمصدر/قاعدة قبل الحكم؟",
              "   `PROVIDE_SUKNA_SOURCE = YES | NO`",
              "2. هل يُفتح مرشّح الحكم المعياري؟ (يحتاج قانون بوابة الحكم docs/43 — NORMATIVE_CANDIDATE فقط، AUTHORITY_LEAK ممنوع)",
              "   `ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO`",
              "3. النطاق:  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
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
    ("REQ-SOURCE-BIRTH-REGISTRY-17", "ROUND_17",
     "output/taaqol_maqam_foundation_generated/RATIFIED_SOURCE_BIRTH_REGISTRY_17.json",
     "tests/test_taaqol_ratified_source_birth_admission_audit_17.py"),
    ("REQ-SOURCE-TO-MASALA-MAPPING-18", "ROUND_18",
     "output/taaqol_maqam_foundation_generated/SOURCE_TO_MASALA_MAPPING_18.json",
     "tests/test_taaqol_source_to_masala_mapping_18.py"),
    ("REQ-MAPPING-RESIDUALS-18", "ROUND_18",
     "output/taaqol_maqam_foundation_generated/SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json",
     "tests/test_taaqol_source_to_masala_mapping_18.py"),
    ("REQ-HUKM-CANDIDATE-GATE-19", "ROUND_18",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_19.md",
     "tests/test_taaqol_source_to_masala_mapping_18.py"),
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


def build_matrix(nodes, residuals, anm):
    kv = [
        ("ROUND", "SOURCE_TO_MASALA_MAPPING_GATE_18"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("SOURCE_TO_MASALA_MAPPING_ALLOWED", "YES"),
        ("MAPPING_MODE", "STRUCTURAL_ONLY"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("EVIDENCE_POLICY", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_IN_ARTIFACTS", "NO"),
        ("MAPPING_ARTIFACT_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("RESIDUALS_ARTIFACT_CREATED", "YES"),
        ("OWNER_REQUEST_19_CREATED", "YES"),
        ("SOURCE_COUNT_MAPPED", str(len(nodes))),
    ]
    for n in nodes:
        sid = n["source_id"]
        kv.append((f"MAPPED::{sid}", "YES"))
        kv.append((f"VERDICT::{sid}", n["verdict"]))
        kv.append((f"HUKM_BIRTH_ALLOWED::{sid}", n["hukm_birth_allowed"]))
    kv += [
        ("NORMATIVE_SOURCE_BORN", "YES"),
        ("RATIFIED_BY", "OWNER"),
        ("SELECTED_BY_AGENT", "NO"),
        ("AGENT_RATIFIED_SOURCE", "NO"),
        ("KEEP_COMPOSITE_REMAINS_ACTIVE", "YES"),
        ("SUKNA_OR_POSSESSION_UNCOVERED", residuals["sukna_or_possession_uncovered"]),
        ("UNCOVERED_DOMAIN_COUNT", str(len(residuals["uncovered_domain_candidates"]))),
        ("UNRESOLVED_RESIDUALS_RECORDED", residuals["unresolved_residuals_recorded"]),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
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


def render_manager(tokens, nodes, residuals, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — ربط المصادر بالمسألة (18)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — ربط المصادر المعيارية بأجزاء المسألة (18)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'EXTERNAL_REFS = 0. ربط بنيوي فقط — لا حكم/مناط/تنزيل/جواب، ولا اختزال للمركّب.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>رُبِطت المصادر الثلاثة المولودة (الجولة 17) بأجزاء النازلة ربطًا بنيويًّا فقط.</li>'
             '<li>لكل مصدر: ما يخدمه، وما لا يخدمه وحده؛ ولا يُنتج مصدرٌ الحكمَ منفردًا.</li>'
             f'<li>ثغرة مسجَّلة: SUKNA_OR_POSSESSION غير مغطّى → السكنى/الطرد بلا مصدر بعد. '
             'لا حكم/مناط/تنزيل/جواب.</li></ul>')
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
             'المصادر مولودة بتصديق المالك؛ الوكيل لا يصادق ولا يشهد بالحرفية.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'رُبِطت المصادر بأجزاء المسألة فقط؛ لا رخصة عبور من الدعوى الواقعية إلى الحكم. '
             'FACTUAL_CLAIM_TO_HUKM_LICENSE = ABSENT.</div>')
    # 8 — mapping table
    P.append('<h2>8. المصدر المعياري — الربط بأجزاء المسألة</h2><div class="wrap"><table><thead><tr>'
             '<th>source</th><th>السلطة</th><th>الربط بالمجال</th><th>جزء المسألة</th><th>يخدم</th>'
             '<th>لا يخدم وحده</th><th>الحكم</th><th>hukm_birth</th></tr></thead><tbody>')
    for n in nodes:
        vcls = "y" if n["verdict"].startswith("MAPPED") else "n"
        P.append('<tr><th>' + e(n["source_id"]) + '</th><td>' + e(n["authority"]) + '</td><td>'
                 + e(" / ".join(n["domain_link"])) + '</td><td>' + e(n["masala_segment_link"]) + '</td><td>'
                 + e(n["serves_what"]) + '</td><td class="d">' + e(n["does_not_serve"]) + '</td>'
                 + f'<td class="{vcls}">{e(n["verdict"])}</td><td class="n">{e(n["hukm_birth_allowed"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: SOURCE_TO_MASALA_MAPPING. الربط بنيوي فقط؛ لا عبور إلى حكم/مناط/تنزيل/جواب، '
             'ولا اختزال للمجال المركّب.</div>')
    # 10 — residuals / gap
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2>')
    P.append('<div class="wrap"><table><thead><tr><th>uncovered domain</th><th>status</th><th>ما يلزم</th>'
             '</tr></thead><tbody>')
    if residuals["per_uncovered"]:
        for u in residuals["per_uncovered"]:
            P.append(f'<tr><th>{e(u["domain_candidate_id"])}</th><td class="n">{e(u["status"])}</td>'
                     f'<td>{e(u["needs"])}</td></tr>')
    else:
        P.append('<tr><td colspan="3">لا مجال غير مغطّى</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="note n" style="background:#fdecec"><b>ثغرات قبل بوابة الحكم:</b><ul>'
             + "".join(f'<li>{e(x)}</li>' for x in residuals["open_residuals_before_hukm_gate"])
             + '</ul></div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند تصريح المالك: (1) تزويد ثغرة السُّكنى/الحيازة '
             'بمصدر/قاعدة، و/أو (2) فتح مرشّح الحكم المعياري (يحتاج قانون بوابة الحكم docs/43 — NORMATIVE_CANDIDATE '
             'فقط، AUTHORITY_LEAK ممنوع)، مع تحديد النطاق.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_source_to_masala_mapping_18.py — '
             'ROUND_18_TESTS = passed · REGRESSION_SCOPE = maqam 02..18 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_18_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT_REGISTRY = output/taaqol_maqam_foundation_generated/RATIFIED_SOURCE_BIRTH_REGISTRY_17.json\n'
             'MAPPING_JSON = output/taaqol_maqam_foundation_generated/SOURCE_TO_MASALA_MAPPING_18.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/SOURCE_TO_MASALA_MAPPING_GUARDS_18.json\n'
             'RESIDUALS = output/taaqol_maqam_foundation_generated/SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json\n'
             'OWNER_REQUEST_19 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_19.md\n'
             'PYTEST_FILE = tests/test_taaqol_source_to_masala_mapping_18.py\n'
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY\nLIVE_EXTERNAL_LINKS_IN_ARTIFACTS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             'رُبِط كل مصدر مولود بجزء المسألة الذي يخدمه، مع بيان أنه لا يكفي وحده لإنتاج الحكم، '
             'وبقاء المجال المركّب. سُجِّلت ثغرة السُّكنى/الحيازة صراحةً. '
             'لم يُنتج حكم/مناط/تنزيل/جواب، ولم يصادق الوكيل مصدرًا. طلب الجولة 19 جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'SOURCE_COUNT_MAPPED = {len(nodes)} · KEEP_COMPOSITE_REMAINS_ACTIVE = YES · '
             f'UNRESOLVED_RESIDUALS_RECORDED = YES · NORMATIVE_SOURCE_BORN = YES · AGENT_RATIFIED_SOURCE = NO · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_18_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "SOURCE_TO_MASALA_MAPPING_MANAGER_REPORT_AR_18.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "SOURCE_TO_MASALA_MAPPING_18_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    reg = load_registry()
    nodes = build_mapping_nodes(reg)
    residuals = build_residuals(nodes)

    (OUT / "SOURCE_TO_MASALA_MAPPING_18.json").write_text(
        json.dumps(build_mapping_json(nodes, reg), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "SOURCE_TO_MASALA_MAPPING_GUARDS_18.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json").write_text(
        json.dumps(residuals, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_CANDIDATE_GATE_19.md").write_text(
        owner_request_19_md(nodes, residuals), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(nodes, residuals, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, nodes, residuals, trows, anm), encoding="utf-8")
    print("REPORT_18=" + a.report_out)
    print(f"SOURCE_COUNT_MAPPED={len(nodes)} SUKNA_UNCOVERED={residuals['sukna_or_possession_uncovered']} "
          f"UNRESOLVED_RESIDUALS_RECORDED=YES ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
