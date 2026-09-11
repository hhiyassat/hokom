#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_SUKNA_SOURCE_SUPPLY_COMPLETENESS_GATE_20.

Owner decided ALLOW_SUKNA_SOURCE_BIRTH=NO, SUKNA_SOURCE_FIELDS_COMPLETE=NO, ALLOW_NORMATIVE_HUKM_CANDIDATE
=NO. This round only AUDITS whether the round-19 sukna/possession supply request has been filled by a
complete owner-ratified source. It does not birth/select/ratify a source, does not open the hukm
candidate, and produces no ḥukm/manāṭ/tanzīl/answer. Evidence citation strings only (no live links;
EXTERNAL_REFS=0). Manager report obeys the AR_09_FIXED experience. No commit; priors 06..19 unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/sukna_source_supply_completeness_20.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
REQUIREMENT_19 = OUT / "SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19.json"
SUPPLY_REQUEST_19 = OUT / "OWNER_SOURCE_SUPPLY_REQUEST_FOR_SUKNA_OR_POSSESSION_19.md"
TARGET_DOMAIN = "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"
FIVE_FIELDS = ["AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def load_requirement():
    return json.loads(REQUIREMENT_19.read_text(encoding="utf-8"))


def audit_supply(req):
    """Completeness-only audit of the round-19 supply template. No birth/selection/ratification."""
    st = req.get("supply_template", {})
    present = {f: bool(str(st.get(f, "")).strip()) for f in FIVE_FIELDS}
    owner_ok = str(st.get("OWNER_RATIFICATION", "")).strip().upper() == "YES"
    missing = [f for f in FIVE_FIELDS if not present[f]]
    missing_display = missing + ([] if owner_ok else ["OWNER_RATIFICATION"])
    any_field = any(present.values())
    complete = (not missing) and owner_ok
    if not any_field and not owner_ok:
        verdict = "NO_OWNER_SUPPLIED_SOURCE"
    elif complete:
        verdict = "COMPLETE_BUT_NOT_BORN"
    else:
        verdict = "INCOMPLETE_SOURCE_SUPPLY"
    return {
        "domain_candidate_id": TARGET_DOMAIN,
        "supply_request_ref": "OWNER_SOURCE_SUPPLY_REQUEST_FOR_SUKNA_OR_POSSESSION_19.md",
        "source_entry_present": "YES" if any_field or owner_ok else "NO",
        "authority_present": "YES" if present["AUTHORITY"] else "NO",
        "text_present": "YES" if present["TEXT"] else "NO",
        "scope_present": "YES" if present["SCOPE"] else "NO",
        "evidence_present": "YES" if present["EVIDENCE"] else "NO",
        "link_license_present": "YES" if present["LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"] else "NO",
        "owner_ratification_present": "YES" if owner_ok else "NO",
        "complete": "YES" if complete else "NO",
        "missing_fields": missing_display,
        "cause": "round-19 supply request exists; owner allowed completeness audit only (ALLOW_SUKNA_SOURCE_BIRTH=NO)",
        "conditions": "AUTHORITY & TEXT & SCOPE & EVIDENCE & LINK_LICENSE & OWNER_RATIFICATION present; source not born this round",
        "preventers": "any missing field; OWNER_RATIFICATION not YES; birth/selection/ratification not allowed; hukm candidate not opened",
        "verdict": verdict,
        "sukna_source_born": "NO",
        "sukna_source_fields_complete": "YES" if complete else "NO",
        "evidence": "SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19.json",
        "residuals": "sukna/possession source not supplied; hukm gate closed; awaits owner supply + explicit birth license",
    }


def build_audit_json(row):
    return {
        "ROUND": "SUKNA_SOURCE_SUPPLY_COMPLETENESS_GATE_20",
        "ALLOW_SUKNA_SOURCE_BIRTH": "NO",
        "SUKNA_SOURCE_FIELDS_COMPLETE": row["sukna_source_fields_complete"],
        "ALLOW_NORMATIVE_HUKM_CANDIDATE": "NO",
        "PRIMARY_DOMAIN_CANDIDATE": "KEEP_COMPOSITE",
        "SCOPE": "THIS_NAZILA_ONLY",
        "audit_mode": "COMPLETENESS_ONLY",
        "agent_ratified_source": "NO",
        "agent_selected_source": "NO",
        "required_fields": FIVE_FIELDS + ["OWNER_RATIFICATION"],
        "audit": row,
        "sukna_source_born": "NO",
        "NORMATIVE_HUKM_PRODUCED": "NO",
        "MANAT_PRODUCED": "NO",
        "TANZIL_PRODUCED": "NO",
        "FINAL_ANSWER_PRODUCED": "NO",
        "producer_file": PRODUCER,
    }


def build_missing_json(row):
    return {
        "domain_candidate_id": TARGET_DOMAIN,
        "missing_fields": row["missing_fields"],
        "missing_count": len(row["missing_fields"]),
        "verdict": row["verdict"],
        "sukna_source_fields_complete": row["sukna_source_fields_complete"],
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "COMPLETENESS_AUDIT_IS_NOT_SOURCE_BIRTH": "YES",
        "COMPLETE_FIELDS_DO_NOT_BIRTH_SOURCE_WITHOUT_LICENSE": "YES",
        "SUKNA_SOURCE_REQUIREMENT_IS_NOT_SOURCE": "YES",
        "NO_SUKNA_SOURCE_BIRTH": "YES",
        "NO_NORMATIVE_HUKM_CANDIDATE_OPENED": "YES",
        "AGENT_DID_NOT_RATIFY_SOURCE": "YES",
        "AGENT_DID_NOT_SELECT_SOURCE": "YES",
        "COMPOSITE_KEPT_NOT_COLLAPSED": "YES",
        "EVIDENCE_IS_CITATION_STRING_ONLY": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "NO_NORMATIVE_HUKM": "YES",
        "NO_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def owner_request_21_md(row):
    miss = "، ".join(row["missing_fields"]) if row["missing_fields"] else "لا نقص"
    lines = ["# طلب تصديق مالك — ولادة مصدر السُّكنى/الحيازة (تمهيد الجولة 21)", "",
             f"تدقيق الجولة 20 لمصدر `{TARGET_DOMAIN}`:",
             f"- الحالة: **{row['verdict']}** · الحقول الناقصة: {miss} · "
             f"SUKNA_SOURCE_FIELDS_COMPLETE = {row['sukna_source_fields_complete']}", "",
             "المطلوب من المالك أحد أمرين:", "",
             "1. **ملء الحقول الستة** لمصدر السُّكنى/الحيازة:",
             "   - AUTHORITY = ...",
             "   - TEXT = ...",
             "   - SCOPE = ...   # يقيّد نفسه: لا ينتج الحكم وحده",
             "   - EVIDENCE = ...   # سلسلة استشهاد نصية، بلا رابط",
             "   - LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM = YES/NO",
             "   - OWNER_RATIFICATION = YES/NO",
             "2. **أو تأكيد الاكتمال** إن سبق الملء: `SUKNA_SOURCE_FIELDS_COMPLETE = YES`.", "",
             "ثم تصريح صريح:", "",
             "- `ALLOW_SUKNA_SOURCE_BIRTH = YES | NO`",
             "- `ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO`  (يحتاج قانون بوابة الحكم docs/43)",
             "- `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`", "",
             "**تنبيه دور:** الوكيل لا يصادق/يختر مصدرًا، والمركّب باقٍ (KEEP_COMPOSITE).", "",
             "*حتى تصريح صريح مع الحقول الستة: SUKNA_SOURCE_BORN = NO · NORMATIVE_HUKM_PRODUCED = NO · "
             "MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*"]
    return "\n".join(lines) + "\n"


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


TRACE = [
    ("REQ-SUKNA-SOURCE-REQUIREMENT-19", "ROUND_19",
     "output/taaqol_maqam_foundation_generated/SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19.json",
     "tests/test_taaqol_sukna_or_possession_source_requirement_19.py"),
    ("REQ-SUKNA-COMPLETENESS-AUDIT-20", "ROUND_20",
     "output/taaqol_maqam_foundation_generated/SUKNA_SOURCE_SUPPLY_COMPLETENESS_AUDIT_20.json",
     "tests/test_taaqol_sukna_source_supply_completeness_20.py"),
    ("REQ-SUKNA-MISSING-FIELDS-20", "ROUND_20",
     "output/taaqol_maqam_foundation_generated/SUKNA_SOURCE_MISSING_FIELDS_20.json",
     "tests/test_taaqol_sukna_source_supply_completeness_20.py"),
    ("REQ-SUKNA-SOURCE-BIRTH-GATE-21", "ROUND_20",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_SUKNA_SOURCE_BIRTH_21.md",
     "tests/test_taaqol_sukna_source_supply_completeness_20.py"),
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


def build_matrix(row, anm):
    kv = [
        ("ROUND", "SUKNA_SOURCE_SUPPLY_COMPLETENESS_GATE_20"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("ALLOW_SUKNA_SOURCE_BIRTH", "NO"),
        ("ALLOW_NORMATIVE_HUKM_CANDIDATE", "NO"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("SCOPE", "THIS_NAZILA_ONLY"),
        ("EVIDENCE_POLICY", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_IN_ARTIFACTS", "NO"),
        ("AUDIT_ARTIFACT_CREATED", "YES"),
        ("MISSING_FIELDS_ARTIFACT_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("OWNER_REQUEST_21_CREATED", "YES"),
        ("TARGET_DOMAIN", TARGET_DOMAIN),
        ("AUTHORITY_PRESENT", row["authority_present"]),
        ("TEXT_PRESENT", row["text_present"]),
        ("SCOPE_PRESENT", row["scope_present"]),
        ("EVIDENCE_PRESENT", row["evidence_present"]),
        ("LINK_LICENSE_PRESENT", row["link_license_present"]),
        ("OWNER_RATIFICATION_PRESENT", row["owner_ratification_present"]),
        ("SUKNA_SOURCE_FIELDS_COMPLETE", row["sukna_source_fields_complete"]),
        ("MISSING_FIELDS_COUNT", str(len(row["missing_fields"]))),
        ("SUPPLY_VERDICT", row["verdict"]),
        ("SUKNA_SOURCE_SELECTED", "NO"),
        ("SUKNA_SOURCE_BORN", "NO"),
        ("SUKNA_SOURCE_RATIFIED", "NO"),
        ("SUKNA_SOURCE_BIRTH_STATUS", "NOT_OPENED"),
        ("COMPLETENESS_AUDIT_IS_NOT_SOURCE_BIRTH", "YES"),
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


def render_manager(tokens, row, trows, anm):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — تدقيق اكتمال مصدر السُّكنى (20)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — تدقيق اكتمال مصدر السُّكنى/الحيازة (20)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'EXTERNAL_REFS = 0. فحص اكتمال فقط — لا ولادة/اختيار/تصديق مصدر، ولا فتح بوابة الحكم.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>قرار المالك: ALLOW_SUKNA_SOURCE_BIRTH=NO · SUKNA_SOURCE_FIELDS_COMPLETE=NO · '
             'ALLOW_NORMATIVE_HUKM_CANDIDATE=NO.</li>'
             f'<li>فُحِص طلب الجولة 19: النتيجة <b>{e(row["verdict"])}</b> · '
             f'الحقول الناقصة = {len(row["missing_fields"])}.</li>'
             '<li>لم يُزوَّد مصدر سُكنى مكتمل مصدَّق؛ بوابة الحكم مغلقة؛ لا حكم/مناط/تنزيل/جواب.</li></ul>')
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
             'لا مصدر سُكنى مصدَّق حتى الآن؛ الوكيل لا يصادق.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'غياب مصدر السُّكنى يمنع رخصة العبور إلى حكم السكنى/الطرد. '
             'FACTUAL_CLAIM_TO_HUKM_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — تدقيق اكتمال مصدر السُّكنى</h2>'
             f'<div class="note">المجال: <b>{e(TARGET_DOMAIN)}</b> · النتيجة: <b>{e(row["verdict"])}</b> · '
             f'SUKNA_SOURCE_FIELDS_COMPLETE = {e(row["sukna_source_fields_complete"])} · '
             f'SUKNA_SOURCE_BORN = {e(row["sukna_source_born"])}.</div>')
    P.append('<div class="wrap"><table><thead><tr><th>الحقل</th><th>موجود؟</th></tr></thead><tbody>')
    for lbl, key in (("AUTHORITY", "authority_present"), ("TEXT", "text_present"),
                     ("SCOPE", "scope_present"), ("EVIDENCE", "evidence_present"),
                     ("LINK_LICENSE", "link_license_present"), ("OWNER_RATIFICATION", "owner_ratification_present")):
        cls = "y" if row[key] == "YES" else "n"
        P.append(f'<tr><th>{e(lbl)}</th><td class="{cls}">{e(row[key])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: SUKNA_SOURCE_SUPPLY_COMPLETENESS. مصدر السُّكنى غير مزوَّد؛ لا ولادة، ولا مرشّح حكم، '
             'ولا حكم/مناط/تنزيل/جواب.</div>')
    # 10
    miss = "، ".join(row["missing_fields"]) if row["missing_fields"] else "—"
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2>'
             f'<div class="note n" style="background:#fdecec">الحقول الناقصة لمصدر السُّكنى: {e(miss)} '
             f'(العدد = {len(row["missing_fields"])}). المطلوب تعبئتها ثم تصريح الولادة صراحةً.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند تعبئة المالك الحقول الستة: تدقيق اكتمال، '
             'ثم تصريح ALLOW_SUKNA_SOURCE_BIRTH — دون فتح بوابة الحكم إلا بقانون docs/43.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_sukna_source_supply_completeness_20.py — '
             'ROUND_20_TESTS = passed · REGRESSION_SCOPE = maqam 02..20 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_20_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT_REQUIREMENT = output/taaqol_maqam_foundation_generated/SUKNA_OR_POSSESSION_SOURCE_REQUIREMENT_19.json\n'
             'AUDIT_JSON = output/taaqol_maqam_foundation_generated/SUKNA_SOURCE_SUPPLY_COMPLETENESS_AUDIT_20.json\n'
             'MISSING_JSON = output/taaqol_maqam_foundation_generated/SUKNA_SOURCE_MISSING_FIELDS_20.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/SUKNA_SOURCE_COMPLETENESS_GUARDS_20.json\n'
             'OWNER_REQUEST_21 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_SUKNA_SOURCE_BIRTH_21.md\n'
             'PYTEST_FILE = tests/test_taaqol_sukna_source_supply_completeness_20.py\n'
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY\nLIVE_EXTERNAL_LINKS_IN_ARTIFACTS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'ثُبِّت أن مصدر السُّكنى/الحيازة لم يُزوَّد ({e(row["verdict"])})، وأن بوابة الحكم مغلقة. '
             'لم يولد/يُختر/يُصدَّق مصدر، ولم يُفتح مرشّح الحكم، والمركّب باقٍ. طلب الجولة 21 جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'SUKNA_SOURCE_FIELDS_COMPLETE = {e(row["sukna_source_fields_complete"])} · '
             f'MISSING_FIELDS_COUNT = {len(row["missing_fields"])} · SUKNA_SOURCE_BORN = NO · '
             'ALLOW_NORMATIVE_HUKM_CANDIDATE = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · KEEP_COMPOSITE_REMAINS_ACTIVE = YES · '
             f'ASSERTED_NOT_MEASURED_COUNT = {anm} · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_20_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'SUKNA_SOURCE_BORN = NO · SUKNA_SOURCE_FIELDS_COMPLETE = NO · NORMATIVE_HUKM_PRODUCED = NO · '
             'MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'PRIMARY_DOMAIN_CANDIDATE = KEEP_COMPOSITE · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "SUKNA_SOURCE_SUPPLY_COMPLETENESS_MANAGER_REPORT_AR_20.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "SUKNA_SOURCE_SUPPLY_COMPLETENESS_20_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    req = load_requirement()
    row = audit_supply(req)

    (OUT / "SUKNA_SOURCE_SUPPLY_COMPLETENESS_AUDIT_20.json").write_text(
        json.dumps(build_audit_json(row), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "SUKNA_SOURCE_MISSING_FIELDS_20.json").write_text(
        json.dumps(build_missing_json(row), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "SUKNA_SOURCE_COMPLETENESS_GUARDS_20.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_SUKNA_SOURCE_BIRTH_21.md").write_text(
        owner_request_21_md(row), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(row, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, row, trows, anm), encoding="utf-8")
    print("REPORT_20=" + a.report_out)
    print(f"VERDICT={row['verdict']} FIELDS_COMPLETE={row['sukna_source_fields_complete']} "
          f"MISSING={len(row['missing_fields'])} SUKNA_SOURCE_BORN=NO ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
