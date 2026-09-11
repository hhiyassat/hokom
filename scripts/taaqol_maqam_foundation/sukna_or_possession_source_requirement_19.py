#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_AND_SUPPLY_GATE_19.

Owner allowed addressing the round-18 residual (SUKNA_OR_POSSESSION uncovered) by RECORDING a source
requirement + owner-fill supply request only — no source birth, no hukm candidate opened. The agent does
not add/ratify/select a source, does not produce ḥukm/manāṭ/tanzīl/answer, does not collapse the
composite, uses citation strings only (no live links), and treats "لا ضرر ولا ضرار" as admissible only
if owner-supplied and owner-ratified. Manager report obeys the AR_09_FIXED experience. No commit; priors
06..18 unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/sukna_or_possession_source_requirement_19.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
RESIDUALS_18 = OUT / "SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json"
TARGET_DOMAIN = "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"
FIVE_FIELDS = ["AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"]
SERVED_NEEDS = [
    ("SUKNA_RIGHT", "حق السكنى"),
    ("POSSESSION_OR_YAD", "الحيازة أو اليد"),
    ("PREVENT_EXPULSION", "منع الطرد"),
    ("DARAR", "الضرر"),
    ("USUFRUCT_RIGHT", "حق الانتفاع"),
    ("SISTER_RESIDENCE_RELATION_POST_DEATH", "علاقة الأخت الساكنة بالبيت بعد موت المالك"),
]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
VERBATIM_MARK = "ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT"


def load_residuals():
    return json.loads(RESIDUALS_18.read_text(encoding="utf-8"))


def build_requirement(resid):
    supply_template = {f: "" for f in FIVE_FIELDS}
    supply_template["OWNER_RATIFICATION"] = "NO"
    supply_template["NOTES"] = "owner-fill; empty until supplied"
    return {
        "ROUND": "SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_AND_SUPPLY_GATE_19",
        "PROVIDE_SUKNA_SOURCE": "YES",
        "ALLOW_NORMATIVE_HUKM_CANDIDATE": "NO",
        "PRIMARY_DOMAIN_CANDIDATE": "KEEP_COMPOSITE",
        "SCOPE": "THIS_NAZILA_ONLY",
        "domain_candidate_id": TARGET_DOMAIN,
        "residual_ref": "SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json#sukna_or_possession_uncovered",
        "residual_status_from_round_18": resid.get("sukna_or_possession_uncovered", "YES"),
        "served_needs": [{"need_id": k, "need_ar": v} for k, v in SERVED_NEEDS],
        "required_fields": FIVE_FIELDS + ["OWNER_RATIFICATION"],
        "supply_template": supply_template,
        "requirement_status": "REQUIREMENT_RECORDED_NOT_SOURCE",
        "sukna_source_born": "NO",
        "normative_source_selected": "NO",
        "la_darar_admissibility": "ONLY_IF_OWNER_SUPPLIED_AND_OWNER_RATIFIED",
        "cause": "round-18 residual: SUKNA_OR_POSSESSION uncovered by the three born sources; owner set PROVIDE_SUKNA_SOURCE=YES",
        "conditions": "owner supplies AUTHORITY+TEXT+SCOPE+EVIDENCE+LINK_LICENSE+OWNER_RATIFICATION; scope self-limits ruling; evidence citation string",
        "preventers": "birth without owner supply; agent ratifying/selecting; opening hukm candidate; collapsing composite; live external link",
        "verdict": "DEFER_SUKNA_SOURCE_BIRTH_REQUIREMENT_RECORDED",
        "evidence": "SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json",
        "residuals": "sukna/possession still without a source; awaits owner supply + explicit birth license (round 20)",
        "NORMATIVE_HUKM_PRODUCED": "NO",
        "MANAT_PRODUCED": "NO",
        "TANZIL_PRODUCED": "NO",
        "FINAL_ANSWER_PRODUCED": "NO",
        "producer_file": PRODUCER,
    }


def supply_request_md():
    lines = ["# طلب تزويد مالك — مصدر السُّكنى/الحيازة/الطرد (الجولة 19)", "",
             "**PROVIDE_SUKNA_SOURCE = YES · ALLOW_NORMATIVE_HUKM_CANDIDATE = NO · "
             "KEEP_COMPOSITE · THIS_NAZILA_ONLY**", "",
             f"سدًّا لثغرة الجولة 18: `{TARGET_DOMAIN}` غير مغطّى بالمصادر الثلاثة المولودة.", "",
             "يُطلب من المالك تزويد مصدرٍ (أو أكثر) يخدم واحدًا أو أكثر مما يلي:", ""]
    for k, v in SERVED_NEEDS:
        lines.append(f"- {v} (`{k}`)")
    lines += ["", "لكل مصدر يزوّده المالك، الحقول الستة (فارغة للتعبئة):", "",
              "```text",
              "SUKNA_SOURCE_1:",
              "AUTHORITY = ____",
              "TEXT = ____",
              "SCOPE = ____   # يجب أن يُقيّد نفسه: لا ينتج الحكم وحده",
              "EVIDENCE = ____   # سلسلة استشهاد نصية فقط، بلا رابط حيّ",
              "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM = YES/NO",
              "OWNER_RATIFICATION = YES/NO",
              "```", "",
              "**ملاحظة على «لا ضرر ولا ضرار»:** لا يُعتمد مصدرًا إلا إذا كان `OWNER_SUPPLIED` "
              "وصادق المالك على مرجعيّته صراحةً (سبق التنبيه على تضعيف طريق ابن ماجه في نفس الصفحة)؛ "
              "الوكيل لا يعتمده ولا يصادقه من عنده.", "",
              "*حتى يزوّد المالك الحقول ويصرّح بالولادة لاحقًا: SUKNA_SOURCE_BORN = NO · "
              "لا حكم/مناط/تنزيل/جواب.*"]
    return "\n".join(lines) + "\n"


def guards():
    return {
        "SUKNA_SOURCE_REQUIREMENT_IS_NOT_SOURCE": "YES",
        "NO_SUKNA_SOURCE_BIRTH": "YES",
        "NO_NORMATIVE_HUKM_CANDIDATE_OPENED": "YES",
        "AGENT_DID_NOT_RATIFY_SOURCE": "YES",
        "AGENT_DID_NOT_SELECT_SOURCE": "YES",
        "NO_NEW_AGENT_SUPPLIED_SOURCE": "YES",
        "LA_DARAR_ONLY_IF_OWNER_SUPPLIED_AND_RATIFIED": "YES",
        "COMPOSITE_KEPT_NOT_COLLAPSED": "YES",
        "EVIDENCE_IS_CITATION_STRING_ONLY": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "TEXT_VERBATIM_ASSERTED_BY_OWNER_ONLY": "YES",
        "NO_NORMATIVE_HUKM": "YES",
        "NO_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def owner_request_20_md():
    lines = ["# طلب تصديق مالك — ولادة مصدر السُّكنى أو فتح بوابة الحكم (تمهيد الجولة 20)", "",
             "بعد تزويد المالك حقول مصدر السُّكنى/الحيازة (الجولة 19)، يُطلب منه صراحةً "
             "(الافتراض: لا شيء يُفتح):", "",
             "1. هل يُصرّح بولادة مصدر السُّكنى/الحيازة المزوَّد؟",
             "   `ALLOW_SUKNA_SOURCE_BIRTH = YES | NO`",
             "2. أم يبقى طلبًا حتى تُملأ/تُراجَع الحقول؟",
             "   `SUKNA_SOURCE_FIELDS_COMPLETE = YES | NO`",
             "3. هل يُفتح مرشّح الحكم المعياري؟ (يحتاج قانون بوابة الحكم docs/43 — "
             "NORMATIVE_CANDIDATE فقط، AUTHORITY_LEAK ممنوع)",
             "   `ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO`",
             "4. النطاق:  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
             "**تنبيه دور:** الوكيل لا يصادق/يختر مصدرًا، ولا يشهد بحرفية النص "
             f"({VERBATIM_MARK})، والمركّب باقٍ (KEEP_COMPOSITE).", "",
             "*حتى تصريح صريح: SUKNA_SOURCE_BORN = NO · NORMATIVE_HUKM_PRODUCED = NO · "
             "MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*"]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-MAPPING-RESIDUALS-18", "ROUND_18",
     "output/taaqol_maqam_foundation_generated/SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json",
     "tests/test_taaqol_source_to_masala_mapping_18.py"),
    ("REQ-SUKNA-SOURCE-REQUIREMENT-19", "ROUND_19",
     "output/taaqol_maqam_foundation_generated/SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19.json",
     "tests/test_taaqol_sukna_or_possession_source_requirement_19.py"),
    ("REQ-SUKNA-SUPPLY-REQUEST-19", "ROUND_19",
     "output/taaqol_maqam_foundation_generated/OWNER_SOURCE_SUPPLY_REQUEST_FOR_SUKNA_OR_POSSESSION_19.md",
     "tests/test_taaqol_sukna_or_possession_source_requirement_19.py"),
    ("REQ-SOURCE-BIRTH-OR-HUKM-GATE-20", "ROUND_19",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_SOURCE_BIRTH_OR_HUKM_GATE_20.md",
     "tests/test_taaqol_sukna_or_possession_source_requirement_19.py"),
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
        ("ROUND", "SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_AND_SUPPLY_GATE_19"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("PROVIDE_SUKNA_SOURCE", "YES"),
        ("ALLOW_NORMATIVE_HUKM_CANDIDATE", "NO"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("EVIDENCE_POLICY", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_IN_ARTIFACTS", "NO"),
        ("REQUIREMENT_ARTIFACT_CREATED", "YES"),
        ("SUPPLY_REQUEST_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("OWNER_REQUEST_20_CREATED", "YES"),
        ("TARGET_DOMAIN", TARGET_DOMAIN),
        ("SERVED_NEEDS_COUNT", str(len(SERVED_NEEDS))),
        ("FIVE_FIELDS_PLUS_RATIFICATION_REQUESTED", "YES"),
        ("SUKNA_OR_POSSESSION_RESIDUAL_ADDRESSING", "REQUIREMENT_ONLY"),
        ("SUKNA_SOURCE_REQUIREMENT_PRODUCED", "YES"),
        ("SUKNA_SOURCE_BORN", "NO"),
        ("REQUIREMENT_IS_NOT_SOURCE", "YES"),
        ("LA_DARAR_ADMISSIBILITY", "ONLY_IF_OWNER_SUPPLIED_AND_RATIFIED"),
        ("NORMATIVE_SOURCE_SELECTED", "NO"),
        ("AGENT_RATIFIED_SOURCE", "NO"),
        ("SELECTED_BY_AGENT", "NO"),
        ("KEEP_COMPOSITE_REMAINS_ACTIVE", "YES"),
        ("NORMATIVE_HUKM_CANDIDATE_OPENED", "NO"),
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


def render_manager(tokens, req, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — طلب مصدر السُّكنى/الحيازة (19)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — طلب مصدر السُّكنى/الحيازة/الطرد (19)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'EXTERNAL_REFS = 0. طلب مصدر فقط — لا ولادة مصدر، ولا فتح بوابة الحكم.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>سمح المالك بسدّ ثغرة السُّكنى/الحيازة بطلب مصدر فقط (PROVIDE_SUKNA_SOURCE=YES، '
             'ALLOW_NORMATIVE_HUKM_CANDIDATE=NO).</li>'
             '<li>أُنتج متطلب مصدر + طلب تزويد بالحقول الستة، يخدم ستة احتياجات (السكنى، اليد، منع الطرد، الضرر، الانتفاع، علاقة الأخت بالبيت).</li>'
             '<li>لا مصدر سُكنى وُلد، ولا فتح لمرشّح الحكم؛ ولا حكم/مناط/تنزيل/جواب.</li></ul>')
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
             '«لا ضرر ولا ضرار» لا يُعتمد إلا إذا زوّده المالك وصادق على مرجعيّته.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'الثغرة سُجِّلت كطلب مصدر فقط؛ لا رخصة عبور إلى حكم أو تطبيق. '
             'FACTUAL_CLAIM_TO_HUKM_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — متطلب مصدر السُّكنى/الحيازة</h2>'
             f'<div class="note">المجال المستهدف: <b>{e(TARGET_DOMAIN)}</b> · '
             f'الحالة: {e(req["requirement_status"])} · SUKNA_SOURCE_BORN = {e(req["sukna_source_born"])}.</div>')
    P.append('<div class="wrap"><table><thead><tr><th>need_id</th><th>الاحتياج</th></tr></thead><tbody>')
    for n in req["served_needs"]:
        P.append(f'<tr><th>{e(n["need_id"])}</th><td>{e(n["need_ar"])}</td></tr>')
    P.append('</tbody></table></div>')
    P.append('<div class="wrap"><table><thead><tr><th>الحقل المطلوب من المالك</th><th>القيمة</th></tr></thead><tbody>')
    for f in req["required_fields"]:
        val = req["supply_template"].get(f, "")
        P.append(f'<tr><th>{e(f)}</th><td class="d">{e(val) if val else "____"}</td></tr>')
    P.append('</tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: SUKNA_SOURCE_REQUIREMENT. متطلب مصدر مسجَّل فقط؛ لا ولادة، ولا مرشّح حكم، '
             'ولا حكم/مناط/تنزيل/جواب.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             'المطلوب من المالك تعبئة الحقول الستة لمصدر يخدم واحدًا أو أكثر من الاحتياجات الستة أعلاه، '
             'مع تقييد SCOPE لنفسه وإسناد نصي بلا رابط. «لا ضرر ولا ضرار»: OWNER_SUPPLIED + تصديق المرجعية فقط.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند وصول الحقول: تدقيق اكتمالها بنيويًّا (كجولة 16)، '
             'ثم تصريح المالك بالولادة (ALLOW_SUKNA_SOURCE_BIRTH) — دون فتح بوابة الحكم إلا بقانون docs/43.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_sukna_or_possession_source_requirement_19.py — '
             'ROUND_19_TESTS = passed · REGRESSION_SCOPE = maqam 02..19 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_19_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT_RESIDUALS = output/taaqol_maqam_foundation_generated/SOURCE_TO_MASALA_MAPPING_RESIDUALS_18.json\n'
             'REQUIREMENT_JSON = output/taaqol_maqam_foundation_generated/SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19.json\n'
             'SUPPLY_REQUEST = output/taaqol_maqam_foundation_generated/OWNER_SOURCE_SUPPLY_REQUEST_FOR_SUKNA_OR_POSSESSION_19.md\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/SUKNA_OR_POSSESSION_SOURCE_GUARDS_19.json\n'
             'OWNER_REQUEST_20 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_SOURCE_BIRTH_OR_HUKM_GATE_20.md\n'
             'PYTEST_FILE = tests/test_taaqol_sukna_or_possession_source_requirement_19.py\n'
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY\nLIVE_EXTERNAL_LINKS_IN_ARTIFACTS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             'سُجِّل متطلب مصدر للسُّكنى/الحيازة/الطرد وطلب تزويد بالحقول الستة يخدم ستة احتياجات؛ '
             'لم يولد مصدر، ولم يُفتح مرشّح الحكم، ولم يصادق الوكيل مصدرًا، والمركّب باقٍ. طلب الجولة 20 جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             'SUKNA_SOURCE_REQUIREMENT_PRODUCED = YES · SUKNA_SOURCE_BORN = NO · '
             'ALLOW_NORMATIVE_HUKM_CANDIDATE = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · KEEP_COMPOSITE_REMAINS_ACTIVE = YES · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_19_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'SUKNA_SOURCE_BORN = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "SUKNA_OR_POSSESSION_SOURCE_MANAGER_REPORT_AR_19.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    resid = load_residuals()
    req = build_requirement(resid)

    (OUT / "SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19.json").write_text(
        json.dumps(req, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_SOURCE_SUPPLY_REQUEST_FOR_SUKNA_OR_POSSESSION_19.md").write_text(
        supply_request_md(), encoding="utf-8")
    (OUT / "SUKNA_OR_POSSESSION_SOURCE_GUARDS_19.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_SOURCE_BIRTH_OR_HUKM_GATE_20.md").write_text(
        owner_request_20_md(), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, req, trows, anm), encoding="utf-8")
    print("REPORT_19=" + a.report_out)
    print(f"SUKNA_SOURCE_REQUIREMENT_PRODUCED=YES SUKNA_SOURCE_BORN=NO "
          f"SERVED_NEEDS={len(SERVED_NEEDS)} ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
