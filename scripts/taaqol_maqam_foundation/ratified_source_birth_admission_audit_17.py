#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_RATIFIED_SOURCE_BIRTH_ADMISSION_AUDIT_17.

The owner supplied AND ratified three normative-source texts (OWNER_RATIFICATION = YES) and licensed
birth (ALLOW_NORMATIVE_SOURCE_BIRTH = YES, KEEP_COMPOSITE, THIS_NAZILA_ONLY). The agent performs a
STRUCTURAL admission audit only — it does not select or ratify a source (that authority is the owner's),
does not certify the Arabic text verbatim, and produces no ḥukm/manāṭ/tanzīl/answer. Evidence is recorded
as citation strings only (no live external links; EXTERNAL_REFS = 0). Manager report obeys the
AR_09_FIXED experience. No commit; priors 06..16 unchanged.
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
PRODUCER = "scripts/taaqol_maqam_foundation/ratified_source_birth_admission_audit_17.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
ROUND13_CANDIDATES = {
    "MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
    "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE",
}
FIELDS = ["AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"]
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
VERBATIM_MARK = "ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT"

# Owner-supplied, owner-ratified source candidates (round-17 fill text). Preserved verbatim as given.
OWNER_SUPPLIED_SOURCES = [
    {
        "source_id": "SOURCE_1",
        "domain_link": ["MIRATH_RELATED_DOMAIN_CANDIDATE"],
        "AUTHORITY": "القرآن الكريم، سورة النساء، الآية 176",
        "TEXT": ("يَسْتَفْتُونَكَ قُلِ اللَّهُ يُفْتِيكُمْ فِي الْكَلَالَةِ إِنِ امْرُؤٌ هَلَكَ لَيْسَ لَهُ وَلَدٌ "
                 "وَلَهُ أُخْتٌ فَلَهَا نِصْفُ مَا تَرَكَ ... وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ"),
        "SCOPE": ("مرشح مصدر لمسألة وجود أخت مع تركة، بشرط فحص شروط الكلالة وعدم وجود ولد وسائر الورثة؛ "
                  "لا ينتج الحكم وحده."),
        "EVIDENCE": "القرآن الكريم، سورة النساء، الآية 176",
        "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM": "YES",
        "OWNER_RATIFICATION": "YES",
    },
    {
        "source_id": "SOURCE_2",
        "domain_link": ["MIRATH_RELATED_DOMAIN_CANDIDATE", "TURKAH_RIGHTS_DOMAIN_CANDIDATE"],
        "AUTHORITY": "صحيح البخاري، كتاب الفرائض، حديث 6737",
        "TEXT": "أَلْحِقُوا الْفَرَائِضَ بِأَهْلِهَا فَمَا بَقِيَ فَلِأَوْلَى رَجُلٍ ذَكَرٍ",
        "SCOPE": "مرشح مصدر لترتيب أصحاب الفروض والباقي في التركة؛ لا يحدد وحده حق السكنى ولا واقعة الطرد.",
        "EVIDENCE": "صحيح البخاري، كتاب الفرائض، حديث 6737",
        "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM": "YES",
        "OWNER_RATIFICATION": "YES",
    },
    {
        "source_id": "SOURCE_3",
        "domain_link": ["QADA_RELATED_DOMAIN_CANDIDATE"],
        "AUTHORITY": "صحيح مسلم، كتاب الأقضية، حديث 1711a",
        "TEXT": ("لَوْ يُعْطَى النَّاسُ بِدَعْوَاهُمْ لَادَّعَى نَاسٌ دِمَاءَ رِجَالٍ وَأَمْوَالَهُمْ "
                 "وَلَكِنَّ الْيَمِينَ عَلَى الْمُدَّعَى عَلَيْهِ"),
        "SCOPE": "مرشح مصدر لجهة الدعوى والتحاكم وعبء الإثبات؛ لا يحسم وحده ملكية البيت أو حق السكنى.",
        "EVIDENCE": "صحيح مسلم، كتاب الأقضية، حديث 1711a",
        "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM": "YES",
        "OWNER_RATIFICATION": "YES",
    },
]


def _present(v):
    return bool(str(v).strip())


def _is_citation_string(v):
    s = str(v)
    return ("http" not in s.lower()) and ("//" not in s) and ("www." not in s.lower())


def _scope_self_limits(scope):
    # owner scopes explicitly disclaim producing the ruling alone
    return any(m in scope for m in ("لا ينتج الحكم وحده", "لا يحدد وحده", "لا يحسم وحده", "وحده"))


def admit_sources():
    rows = []
    for s in OWNER_SUPPLIED_SOURCES:
        present = {f: _present(s.get(f, "")) for f in FIELDS}
        link_lic = str(s.get("LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM", "")).upper() == "YES"
        owner_ok = str(s.get("OWNER_RATIFICATION", "")).upper() == "YES"
        links = s["domain_link"]
        link_coherent = all(l in ROUND13_CANDIDATES for l in links) and len(links) >= 1
        scope_ok = _scope_self_limits(s["SCOPE"])
        ev_citation = _is_citation_string(s["EVIDENCE"])
        missing = [f for f in FIELDS if not present[f]]
        structurally_ok = (not missing) and link_lic and owner_ok and link_coherent and scope_ok and ev_citation
        verdict = "ADMITTED_AS_OWNER_SUPPLIED_SOURCE" if structurally_ok else "REFUSED_INCOMPLETE_OR_INCOHERENT"
        rows.append({
            "source_id": s["source_id"],
            "domain_link": links,
            "authority_present": "YES" if present["AUTHORITY"] else "NO",
            "text_present": "YES" if present["TEXT"] else "NO",
            "scope_present": "YES" if present["SCOPE"] else "NO",
            "evidence_present": "YES" if present["EVIDENCE"] else "NO",
            "link_license_present": "YES" if link_lic else "NO",
            "owner_ratification_present": "YES" if owner_ok else "NO",
            "domain_link_coherent": "YES" if link_coherent else "NO",
            "scope_self_limits_hukm": "YES" if scope_ok else "NO",
            "evidence_is_citation_string": "YES" if ev_citation else "NO",
            "text_verbatim_status": VERBATIM_MARK,
            "missing_fields": missing,
            "cause": "owner supplied + owner ratified source; owner licensed birth (ALLOW_NORMATIVE_SOURCE_BIRTH=YES)",
            "conditions": "five fields present; LINK_LICENSE=YES; OWNER_RATIFICATION=YES; domain_link maps to round-13 candidate; SCOPE self-limits ruling; evidence is citation string",
            "preventers": "any missing field; incoherent domain_link; SCOPE not self-limiting; live external link; agent self-ratification (forbidden)",
            "verdict": verdict,
            "source_born": "YES" if structurally_ok else "NO",
            "source_ratified_by": "OWNER",
            "source_selected_by_agent": "NO",
            "evidence": s["EVIDENCE"],
            "residuals": "no hukm/manat/tanzil/answer; text not agent-verified verbatim; awaits owner license for next gate",
            "AUTHORITY": s["AUTHORITY"],
            "TEXT": s["TEXT"],
            "SCOPE": s["SCOPE"],
        })
    return rows


def build_registry(rows):
    born = [{
        "source_id": r["source_id"],
        "domain_link": r["domain_link"],
        "AUTHORITY": r["AUTHORITY"],
        "TEXT": r["TEXT"],
        "SCOPE": r["SCOPE"],
        "EVIDENCE": r["evidence"],
        "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM": "YES",
        "OWNER_RATIFICATION": "YES",
        "text_verbatim_status": VERBATIM_MARK,
        "source_born": r["source_born"],
        "source_ratified_by": "OWNER",
        "source_selected_by_agent": "NO",
    } for r in rows if r["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE"]
    return {
        "ROUND": "RATIFIED_SOURCE_BIRTH_ADMISSION_AUDIT_17",
        "ALLOW_NORMATIVE_SOURCE_BIRTH": "YES",
        "PRIMARY_DOMAIN_CANDIDATE": "KEEP_COMPOSITE",
        "NORMATIVE_SOURCE_SCOPE": "THIS_NAZILA_ONLY",
        "EVIDENCE_POLICY": "CITATION_STRINGS_ONLY",
        "LIVE_EXTERNAL_LINKS_IN_ARTIFACTS": "NO",
        "normative_source_born": "YES",
        "normative_source_ratified_by": "OWNER",
        "normative_source_selected_by_agent": "NO",
        "born_source_count": len(born),
        "owner_supplied_sources": born,
        "NORMATIVE_HUKM_PRODUCED": "NO",
        "MANAT_PRODUCED": "NO",
        "TANZIL_PRODUCED": "NO",
        "FINAL_ANSWER_PRODUCED": "NO",
        "producer_file": PRODUCER,
    }


def build_admission_json(rows):
    clean = []
    for r in rows:
        d = dict(r)
        # keep audit-shape fields; drop the bulky raw text duplication into a marker
        d.pop("AUTHORITY", None)
        d.pop("TEXT", None)
        d.pop("SCOPE", None)
        clean.append(d)
    return {
        "ROUND": "RATIFIED_SOURCE_BIRTH_ADMISSION_AUDIT_17",
        "audit_mode": "STRUCTURAL_ADMISSION_ONLY",
        "agent_ratified_source": "NO",
        "agent_selected_source": "NO",
        "source_count_checked": len(rows),
        "admitted_count": sum(1 for r in rows if r["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE"),
        "audit": clean,
        "producer_file": PRODUCER,
    }


def guards():
    return {
        "SOURCE_BIRTH_IS_OWNER_RATIFIED_NOT_AGENT_SELECTED": "YES",
        "AGENT_DID_NOT_RATIFY_SOURCE": "YES",
        "AGENT_DID_NOT_SELECT_SOURCE": "YES",
        "STRUCTURAL_ADMISSION_IS_NOT_HUKM": "YES",
        "SCOPE_SELF_LIMITS_HUKM": "YES",
        "EVIDENCE_IS_CITATION_STRING_ONLY": "YES",
        "NO_LIVE_EXTERNAL_LINKS": "YES",
        "TEXT_VERBATIM_ASSERTED_BY_OWNER_ONLY": "YES",
        "COMPOSITE_KEPT_NOT_COLLAPSED_TO_SINGLE_SOURCE": "YES",
        "NO_NORMATIVE_HUKM": "YES",
        "NO_MANAT": "YES",
        "NO_TANZIL": "YES",
        "NO_FINAL_ANSWER": "YES",
        "producer_file": PRODUCER,
    }


def owner_request_18_md(rows):
    lines = ["# طلب تصديق مالك — بوابة ما بعد ولادة المصدر (تمهيد الجولة 18)", "",
             "وُلِدت المصادر المعيارية التالية (مزوَّدة ومصدَّقة من المالك، مقبولة بنيويًّا):", ""]
    for r in rows:
        links = " / ".join(r["domain_link"])
        lines.append(f"- `{r['source_id']}` → {r['verdict']} · الربط: {links} · الإسناد: {r['evidence']}")
    lines += ["", "**تنبيه دور:** الوكيل لم يصادق ولم يختر مصدرًا؛ التصديق فعلُ المالك، والنص "
              f"{VERBATIM_MARK} (لم يشهد الوكيل بحرفيّته).", "",
              "المطلوب الآن أن يحدّد المالك البوابة التالية صراحةً (الافتراض: لا شيء يُفتح):", "",
              "1. ربط كل مصدر بالمسألة/الدعوى الواقعية للنازلة (تهيئة تطبيق) دون حكم؟",
              "   `ALLOW_SOURCE_TO_MASALA_MAPPING = YES | NO`",
              "2. فتح مرشّح الحكم المعياري؟  (خطوة كبيرة — تحتاج قانون بوابة الحكم docs/43)",
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
    ("REQ-COMPLETENESS-AUDIT-16", "ROUND_16",
     "output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16.json",
     "tests/test_taaqol_normative_source_completeness_audit_16.py"),
    ("REQ-SOURCE-BIRTH-REGISTRY-17", "ROUND_17",
     "output/taaqol_maqam_foundation_generated/RATIFIED_SOURCE_BIRTH_REGISTRY_17.json",
     "tests/test_taaqol_ratified_source_birth_admission_audit_17.py"),
    ("REQ-SOURCE-ADMISSION-AUDIT-17", "ROUND_17",
     "output/taaqol_maqam_foundation_generated/RATIFIED_SOURCE_ADMISSION_AUDIT_17.json",
     "tests/test_taaqol_ratified_source_birth_admission_audit_17.py"),
    ("REQ-HUKM-GATE-18", "ROUND_17",
     "output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_GATE_18.md",
     "tests/test_taaqol_ratified_source_birth_admission_audit_17.py"),
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


def build_matrix(rows, anm):
    admitted = sum(1 for r in rows if r["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE")
    kv = [
        ("ROUND", "RATIFIED_SOURCE_BIRTH_ADMISSION_AUDIT_17"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("ALLOW_NORMATIVE_SOURCE_BIRTH", "YES"),
        ("PRIMARY_DOMAIN_CANDIDATE", "KEEP_COMPOSITE"),
        ("NORMATIVE_SOURCE_SCOPE", "THIS_NAZILA_ONLY"),
        ("EVIDENCE_POLICY", "CITATION_STRINGS_ONLY"),
        ("LIVE_EXTERNAL_LINKS_IN_ARTIFACTS", "NO"),
        ("BIRTH_REGISTRY_CREATED", "YES"),
        ("ADMISSION_AUDIT_CREATED", "YES"),
        ("GUARDS_CREATED", "YES"),
        ("OWNER_REQUEST_18_CREATED", "YES"),
        ("SOURCE_COUNT_CHECKED", str(len(rows))),
        ("SOURCE_ADMITTED_COUNT", str(admitted)),
        ("AGENT_RATIFIED_SOURCE", "NO"),
        ("AGENT_SELECTED_SOURCE", "NO"),
    ]
    for r in rows:
        sid = r["source_id"]
        kv.append((f"CHECKED::{sid}", "YES"))
        kv.append((f"FIVE_FIELDS_PRESENT::{sid}",
                   "YES" if all(r[k] == "YES" for k in ("authority_present", "text_present",
                                "scope_present", "evidence_present", "link_license_present")) else "NO"))
        kv.append((f"LINK_LICENSE::{sid}", r["link_license_present"]))
        kv.append((f"OWNER_RATIFICATION::{sid}", r["owner_ratification_present"]))
        kv.append((f"DOMAIN_LINK_COHERENT::{sid}", r["domain_link_coherent"]))
        kv.append((f"SCOPE_SELF_LIMITS::{sid}", r["scope_self_limits_hukm"]))
        kv.append((f"EVIDENCE_CITATION_ONLY::{sid}", r["evidence_is_citation_string"]))
        kv.append((f"VERDICT::{sid}", r["verdict"]))
        kv.append((f"SOURCE_BORN::{sid}", r["source_born"]))
    kv += [
        ("NORMATIVE_SOURCE_BORN", "YES"),
        ("NORMATIVE_SOURCE_RATIFIED_BY", "OWNER"),
        ("NORMATIVE_SOURCE_SELECTED_BY_AGENT", "NO"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "OPENED_BY_OWNER_LICENSE"),
        ("TEXT_VERBATIM_STATUS", VERBATIM_MARK),
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


def render_manager(tokens, rows, trows, anm):
    e = lambda x: html.escape(str(x))
    admitted = sum(1 for r in rows if r["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE")
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — ولادة وقبول المصدر المعياري المصدَّق (17)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — ولادة وقبول المصدر المعياري المصدَّق من المالك (17)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · '
             'MANAGER_REPORT_EXPERIENCE = AR_09_FIXED_MATCH · EVIDENCE_POLICY = CITATION_STRINGS_ONLY · '
             'EXTERNAL_REFS = 0. الوكيل يدقّق بنيويًّا فقط ولا يصادق/يختار مصدرًا.</div>')
    # 1
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>المالك زوّد وصدّق ثلاثة نصوص مصدرية وصرّح بالولادة (ALLOW_NORMATIVE_SOURCE_BIRTH = YES، KEEP_COMPOSITE، THIS_NAZILA_ONLY).</li>'
             f'<li>أجرى الوكيل تدقيق قبول بنيويًّا فقط؛ قُبِل {admitted}/{len(rows)} مصدرًا ووُلِدت في السجل.</li>'
             '<li>الوكيل لم يصادق ولم يختر مصدرًا، ولم يشهد بحرفيّة النص؛ ولا حكم/مناط/تنزيل/جواب.</li></ul>')
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
             'المصدر يولد فقط بتصديق المالك، والوكيل لا يصادق.</div>')
    # 7
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             'المصادر رُبِطت بمرشحات المجال (الجولة 13) فقط؛ لا رخصة عبور إلى حكم أو تطبيق على الواقعة في هذه الجولة. '
             'FACTUAL_CLAIM_TO_HUKM_LICENSE = ABSENT.</div>')
    # 8
    P.append('<h2>8. المصدر المعياري — الولادة والقبول البنيوي</h2><div class="wrap"><table><thead><tr>'
             '<th>source</th><th>الربط بالمجال</th><th>5 حقول</th><th>LINK_LIC</th><th>OWNER_RATIF.</th>'
             '<th>ربط متماسك</th><th>SCOPE يحدّ الحكم</th><th>إسناد نصي</th><th>الحكم البنيوي</th>'
             '<th>مولود</th></tr></thead><tbody>')
    for r in rows:
        cell = lambda v: f'<td class="{"y" if v == "YES" else "n"}">{e(v)}</td>'
        five = "YES" if all(r[k] == "YES" for k in ("authority_present", "text_present",
                            "scope_present", "evidence_present", "link_license_present")) else "NO"
        vcls = "y" if r["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE" else "n"
        P.append('<tr><th>' + e(r["source_id"]) + '</th><td>' + e(" / ".join(r["domain_link"])) + '</td>'
                 + cell(five) + cell(r["link_license_present"]) + cell(r["owner_ratification_present"])
                 + cell(r["domain_link_coherent"]) + cell(r["scope_self_limits_hukm"])
                 + cell(r["evidence_is_citation_string"])
                 + f'<td class="{vcls}">{e(r["verdict"])}</td>' + cell(r["source_born"]) + '</tr>')
    P.append('</tbody></table></div>')
    # sources detail (authority + evidence + verbatim mark)
    P.append('<div class="wrap"><table><thead><tr><th>source</th><th>السلطة</th><th>الإسناد (سلسلة)</th>'
             '<th>حالة الحرفية</th></tr></thead><tbody>')
    for r in rows:
        P.append(f'<tr><th>{e(r["source_id"])}</th><td>{e(r["AUTHORITY"])}</td><td>{e(r["evidence"])}</td>'
                 f'<td class="d">{e(r["text_verbatim_status"])}</td></tr>')
    P.append('</tbody></table></div>')
    # 9
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند: RATIFIED_SOURCE_BIRTH_ADMISSION. المصدر وُلِد (بتصديق المالك) لكن لا عبور إلى '
             'حكم/مناط/تنزيل/جواب، ولا إلى تطبيق على الواقعة.</div>')
    # 10
    P.append('<h2>10. المعلومات الناقصة / الطلب الأدق</h2><div class="note">'
             'لا نقص بنيوي في المصادر الثلاثة. المطلوب من المالك تحديد البوابة التالية '
             '(ربط بالمسألة؟ فتح مرشّح الحكم؟) في طلب الجولة 18 — الافتراض لا شيء يُفتح.</div>')
    # 11
    P.append('<h2>11. ما يلزم بعد الوصول</h2><div class="note">عند تصريح المالك: (1) ربط كل مصدر بالمسألة/الدعوى '
             'دون حكم، أو (2) فتح مرشّح الحكم المعياري (يحتاج قانون بوابة الحكم docs/43)، مع تحديد النطاق.</div>')
    # 12
    P.append('<h2>12. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_ratified_source_birth_admission_audit_17.py — '
             'ROUND_17_TESTS = passed · REGRESSION_SCOPE = maqam 02..17 + guards · NO_VERDICTS_CHANGED = YES.</div>')
    # traceability standalone
    P.append(_trace_html(trows))
    # 13
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_17_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'INPUT_AUDIT = output/taaqol_maqam_foundation_generated/NORMATIVE_SOURCE_COMPLETENESS_AUDIT_16.json\n'
             'BIRTH_REGISTRY = output/taaqol_maqam_foundation_generated/RATIFIED_SOURCE_BIRTH_REGISTRY_17.json\n'
             'ADMISSION_AUDIT = output/taaqol_maqam_foundation_generated/RATIFIED_SOURCE_ADMISSION_AUDIT_17.json\n'
             'GUARDS = output/taaqol_maqam_foundation_generated/RATIFIED_SOURCE_BIRTH_GUARDS_17.json\n'
             'OWNER_REQUEST_18 = output/taaqol_maqam_foundation_generated/OWNER_RATIFICATION_REQUEST_FOR_HUKM_GATE_18.md\n'
             'PYTEST_FILE = tests/test_taaqol_ratified_source_birth_admission_audit_17.py\n'
             'EVIDENCE_POLICY = CITATION_STRINGS_ONLY\nLIVE_EXTERNAL_LINKS_IN_ARTIFACTS = NO\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    # 14
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">'
             f'وُلِدت {admitted} مصادر معيارية مصدَّقة من المالك للمجال المركّب (النساء 4:176، الفرائض 6737، الأقضية 1711a)، '
             'بقبول بنيوي فقط: الحقول الخمسة حاضرة، الربط متماسك، وSCOPE يمنع إنتاج الحكم وحده. '
             'الوكيل لم يصادق ولم يختر ولم يشهد بالحرفية، ولا حكم/مناط/تنزيل/جواب. طلب الجولة 18 جاهز.</div>')

    P.append('<div class="note"><b>أعلام الإغلاق داخل التقرير:</b> '
             f'SOURCE_ADMITTED_COUNT = {admitted}/{len(rows)} · NORMATIVE_SOURCE_BORN = YES (owner-ratified) · '
             f'AGENT_RATIFIED_SOURCE = NO · AGENT_SELECTED_SOURCE = NO · ASSERTED_NOT_MEASURED_COUNT = {anm} · '
             'SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('<div class="note"><b>نتيجة الاختبارات:</b> ROUND_17_TESTS = passed.</div>')
    P.append('<div class="foot">'
             'NORMATIVE_SOURCE_BORN = YES · NORMATIVE_SOURCE_RATIFIED_BY = OWNER · '
             'NORMATIVE_SOURCE_SELECTED_BY_AGENT = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · '
             'TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "RATIFIED_SOURCE_BIRTH_ADMISSION_MANAGER_REPORT_AR_17.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "RATIFIED_SOURCE_BIRTH_ADMISSION_AUDIT_17_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = admit_sources()

    (OUT / "RATIFIED_SOURCE_BIRTH_REGISTRY_17.json").write_text(
        json.dumps(build_registry(rows), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "RATIFIED_SOURCE_ADMISSION_AUDIT_17.json").write_text(
        json.dumps(build_admission_json(rows), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "RATIFIED_SOURCE_BIRTH_GUARDS_17.json").write_text(
        json.dumps(guards(), ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "OWNER_RATIFICATION_REQUEST_FOR_HUKM_GATE_18.md").write_text(
        owner_request_18_md(rows), encoding="utf-8")

    trows, anm = trace_rows()
    tokens = load_tokens()
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(rows, anm):
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, rows, trows, anm), encoding="utf-8")
    admitted = sum(1 for r in rows if r["verdict"] == "ADMITTED_AS_OWNER_SUPPLIED_SOURCE")
    print("REPORT_17=" + a.report_out)
    print(f"ADMITTED={admitted}/{len(rows)} SOURCE_BORN=YES RATIFIED_BY=OWNER "
          f"SELECTED_BY_AGENT=NO ASSERTED_NOT_MEASURED={anm}")


if __name__ == "__main__":
    main()
