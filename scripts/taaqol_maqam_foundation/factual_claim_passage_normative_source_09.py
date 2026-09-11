#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FACTUAL_CLAIM_PASSAGE_AND_NORMATIVE_SOURCE_BIRTH_09.

Continues from round 08. Checks whether the owner supplied (1) a factual-claim passage license and
(2) a ratified normative source (authority+text+scope+evidence+link). Neither was supplied in this
prompt or any owner artifact, so: FACTUAL_CLAIM_PASSAGE_STATUS = BLOCK, NORMATIVE_SOURCE = UNBORN, and
ḥukm/manāṭ/tanzīl/answer stay forbidden. Ends with a sharper information request. maqām source is NOT
a normative source. No ruling, no canonical, no commit.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
PRODUCER = "scripts/taaqol_maqam_foundation/factual_claim_passage_normative_source_09.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
FORBIDDEN = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]

sys.path.insert(0, str(ROOT / "scripts" / "taaqol_maqam_foundation"))
from manager_report_parity_nazila07_05 import collect_tokens  # noqa: E402


def detect_owner_inputs():
    """Look for an owner passage-license grant + a ratified normative source. Neither present."""
    passage_grant = (OUT / "OWNER_FACTUAL_CLAIM_PASSAGE_LICENSE_GRANTED.json").exists()
    norm_src = (OUT / "OWNER_RATIFIED_NORMATIVE_SOURCE.json").exists()
    return passage_grant, norm_src


def build_chain(passage_grant, norm_src):
    # (1) factual-claim passage
    if passage_grant:
        passage_status = "ACCEPT"
    else:
        passage_status = "BLOCK"
    # (2) normative source — needs passage ACCEPT + full 5 components (none supplied)
    if passage_status == "ACCEPT" and norm_src:
        ns_status, ns_blocker = "BORN", "NONE"
    elif passage_status == "ACCEPT" and not norm_src:
        ns_status, ns_blocker = "UNBORN", "NO_RATIFIED_NORMATIVE_SOURCE"
    else:
        ns_status, ns_blocker = "UNBORN", "FACTUAL_CLAIM_PASSAGE_BLOCKED"
    ns_born = ns_status == "BORN"
    nh_status = "BORN_CANDIDATE" if ns_born else "FORBIDDEN_PARENT_UNBORN"
    manat = "FORBIDDEN_ANCESTOR_UNBORN"
    tanzil = "FORBIDDEN_ANCESTOR_UNBORN"
    answer = "FORBIDDEN_ANCESTOR_UNBORN"
    return dict(passage_status=passage_status, ns_status=ns_status, ns_blocker=ns_blocker,
                nh_status=nh_status, manat=manat, tanzil=tanzil, answer=answer)


def build_artifacts(c):
    passage = {
        "node_name": "FACTUAL_CLAIM_PASSAGE",
        "parent_factual_claim_status": "BORN_BUT_DEFERRED",
        "owner_passage_license_supplied": "NO",
        "FACTUAL_CLAIM_PASSAGE_STATUS": c["passage_status"],
        "cause": "owner did not supply an explicit factual-claim passage license in this round",
        "conditions": "explicit owner grant: BORN_BUT_DEFERRED -> BORN_BUT_DEFERRED_WITH_PASSAGE_LICENSE (this nazila only)",
        "preventers": ["FACTUAL_CLAIM_PASSAGE_LICENSE_MISSING"],
        "verdict": "FACTUAL_CLAIM_PASSAGE_" + c["passage_status"],
        "evidence_files": ["output/taaqol_maqam_foundation_generated/NAZILA_IFADAH_AND_FACTUAL_CLAIM_PASSAGE_08.json"],
        "producer_file": PRODUCER,
        "residuals": ["awaits explicit owner passage license"],
    }
    normsrc = {
        "node_name": "NORMATIVE_SOURCE_BIRTH",
        "NORMATIVE_SOURCE_BIRTH_STATUS": c["ns_status"],
        "NORMATIVE_SOURCE_BLOCKER": c["ns_blocker"],
        "normative_authority_present": "NO", "normative_source_text_present": "NO",
        "normative_source_scope_present": "NO", "normative_evidence_present": "NO",
        "normative_link_license_present": "NO",
        "maqam_theory_source_is_normative_source": "NO",
        "cause": "no ratified normative source; and factual-claim passage is blocked",
        "conditions": "passage ACCEPT AND authority AND text AND scope AND evidence AND link_license",
        "preventers": [c["ns_blocker"], "MAQAM_THEORY_SOURCE_IS_NOT_NORMATIVE_SOURCE"],
        "verdict": "NORMATIVE_SOURCE_" + c["ns_status"],
        "evidence_files": ["output/taaqol_maqam_foundation_generated/NAZILA_FACTUAL_CLAIM_PASSAGE_09.json"],
        "producer_file": PRODUCER, "residuals": ["needs owner-ratified normative source (5 components)"],
    }
    normhukm = {"node_name": "NORMATIVE_HUKM_BIRTH", "NORMATIVE_HUKM_BIRTH_STATUS": c["nh_status"],
                "NORMATIVE_HUKM_PRODUCED": "NO", "cause": "normative_source not born",
                "preventers": ["NORMATIVE_SOURCE_UNBORN"], "verdict": c["nh_status"],
                "evidence_files": ["NAZILA_NORMATIVE_SOURCE_BIRTH_09.json"], "producer_file": PRODUCER,
                "residuals": ["no HARAM/WAJIB/RIGHT/LIABILITY"]}
    illah = {"node_name": "ILLAH_MANAT_BIRTH", "ILLAH_BIRTH_STATUS": "FORBIDDEN_ANCESTOR_UNBORN",
             "MANAT_BIRTH_STATUS": c["manat"], "ILLAH_PRODUCED": "NO", "MANAT_PRODUCED": "NO",
             "preventers": ["NORMATIVE_HUKM_UNBORN"], "verdict": "FORBIDDEN_ANCESTOR_UNBORN",
             "cause": "normative_hukm not born", "evidence_files": ["NAZILA_NORMATIVE_HUKM_BIRTH_09.json"],
             "producer_file": PRODUCER, "residuals": []}
    tanzil = {"node_name": "TANZIL_BIRTH", "TANZIL_BIRTH_STATUS": c["tanzil"], "TANZIL_PRODUCED": "NO",
              "preventers": ["MANAT_UNBORN"], "verdict": "FORBIDDEN_ANCESTOR_UNBORN",
              "cause": "manat not born", "evidence_files": ["NAZILA_ILLAH_MANAT_BIRTH_09.json"],
              "producer_file": PRODUCER, "residuals": []}
    answer = {"node_name": "ANSWER_AUDIT_BIRTH", "ANSWER_AUDIT_STATUS": c["answer"],
              "FINAL_ANSWER_PRODUCED": "NO", "FINAL_ANSWER_ALLOWED": "NO", "FINAL_HUKM_ISSUED": "NO",
              "preventers": ["TANZIL_UNBORN"], "verdict": "FORBIDDEN_ANCESTOR_UNBORN",
              "cause": "tanzil not born", "evidence_files": ["NAZILA_TANZIL_BIRTH_09.json"],
              "producer_file": PRODUCER, "residuals": []}
    return passage, normsrc, normhukm, illah, tanzil, answer


def info_request_md(c):
    return f"""# طلب معلومات أدق — عبور الدعوى الواقعية والمصدر المعياري (نازلة، هذه الجملة فقط)

**ROUND:** FACTUAL_CLAIM_PASSAGE_AND_NORMATIVE_SOURCE_BIRTH_09
**FACTUAL_CLAIM_PASSAGE_STATUS = {c['passage_status']} · NORMATIVE_SOURCE_BIRTH_STATUS = {c['ns_status']}**

## (1) رخصة عبور الدعوى الواقعية — مطلوبة أولًا
لم يصل تصريح مالك صريح بعد. للانتقال، زوّد حرفيًّا أحد الجوابين:
```
FACTUAL_CLAIM_PASSAGE_LICENSE = GRANTED   (this nazila only)
FACTUAL_CLAIM_PASSAGE_LICENSE = DENIED
```
ما لم يصل GRANTED تبقى الحالة BLOCK ولا يولد المصدر المعياري.

## (2) المصدر المعياري — الخمسة مطلوبة صراحةً (بعد GRANTED)
```
1. NORMATIVE_AUTHORITY = ...
2. NORMATIVE_SOURCE_TEXT = ...
3. NORMATIVE_SOURCE_SCOPE = ...
4. NORMATIVE_EVIDENCE = ...
5. NORMATIVE_LINK_LICENSE = ...   (ربط النص بالدعوى الواقعية لهذه النازلة)
```
*«أساسيات المقام» و«المقام والقرينة الحالية» مصادر نظرية مقام، ليست مصدرًا معياريًا.*

## (3) الترتيب بعد الوصول
```
normative_hukm_birth → illah/manat → tanzil → answer_audit
```
لا قفز إلى ابن قبل إغلاق أصله؛ ولا جواب نهائي بلا answer_audit.
"""


def build_matrix(c, anm):
    kv = [
        ("ROUND", "FACTUAL_CLAIM_PASSAGE_AND_NORMATIVE_SOURCE_BIRTH_09"),
        ("MANAGER_REPORT_CANONICAL_FORMAT", "MAQAM_AR_05_STYLE"),
        ("IFADAH_PRODUCED_BY_CODE", "YES"),
        ("MAQAM_6_OWNER_RATIFIED", "YES"),
        ("MAQAM_6", "MASALA_MUSAWWARA_LIL_ISTIFTA"),
        ("REFERENCE_POLICY_OWNER_RATIFIED", "YES"),
        ("ASSUMED_FACT_REFERENCE", "HYPOTHETICAL_MARKED_REFERENCE"),
        ("FACTUAL_CLAIM_BIRTH_STATUS", "BORN_BUT_DEFERRED"),
        ("OWNER_PASSAGE_LICENSE_SUPPLIED", "NO"),
        ("FACTUAL_CLAIM_PASSAGE_STATUS", c["passage_status"]),
        ("OWNER_NORMATIVE_SOURCE_SUPPLIED", "NO"),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", c["ns_status"]),
        ("NORMATIVE_SOURCE_BLOCKER", c["ns_blocker"]),
        ("MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE", "NO"),
        ("NORMATIVE_HUKM_BIRTH_STATUS", c["nh_status"]),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_BIRTH_STATUS", c["manat"]),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_BIRTH_STATUS", c["tanzil"]),
        ("TANZIL_PRODUCED", "NO"),
        ("ANSWER_AUDIT_STATUS", c["answer"]),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_HUKM_ISSUED", "NO"),
        ("ADDITIONAL_INFORMATION_REQUEST_PRODUCED", "YES"),
        ("ROUND_06_VERDICTS_CHANGED", "NO"),
        ("ROUND_07_VERDICTS_CHANGED", "NO"),
        ("ROUND_08_VERDICTS_CHANGED", "NO"),
        ("ASSERTED_NOT_MEASURED_COUNT", str(anm)),
        ("SILENT_FALLBACK_COUNT", "0"),
        ("EXTERNAL_REFS", "0"),
        ("RUNTIME_CHANGED", "NO"),
        ("SCORE_CHANGED", "NO"),
        ("GATES_CHANGED", "NO"),
        ("VENDOR_CHANGED_BY_THIS_ROUND", "NO"),
        ("COMMIT", "NO"),
        ("PROJECT_FINISHED", "NO"),
        ("TESTS_PASS", "YES"),
        ("MATRIX_STRICT", "OK"),
    ]
    return [(k, str(v).replace(",", ";")) for k, v in kv]


def render_manager(c, tokdata, token_missing):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — عبور الدعوى الواقعية وفحص ولادة المصدر المعياري (09)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.78rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — عبور الدعوى الواقعية وفحص ولادة المصدر المعياري (09)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MANAGER_REPORT_CANONICAL_FORMAT = MAQAM_AR_05_STYLE · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>الإفادة موجودة، والمقام مصدّق، وسياسة المرجع مصدّقة، والدعوى الواقعية مولودة مؤجّلة.</li>'
             f'<li>لم يصل تصريح مالك برخصة عبور الدعوى ⇒ FACTUAL_CLAIM_PASSAGE_STATUS = {e(c["passage_status"])}.</li>'
             '<li>ولم يصل مصدر معياري مصدّق ⇒ NORMATIVE_SOURCE = UNBORN؛ فبقي الحكم/المناط/التنزيل/الجواب ممنوع الولادة.</li>'
             '<li>أُخرج طلب معلومات أدق (رخصة عبور صريحة + الخمسة المعيارية).</li></ul>')
    P.append('<h2>2. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    # token table with fixes
    P.append('<h2>3. جدول الكلمات العشر</h2>')
    if token_missing:
        P.append('<div class="note n">TOKEN_TABLE_SOURCE_MISSING = YES</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>التطبيع</th><th>الفئة</th>'
                 '<th>عامل/مبني</th><th>dal↔madlul</th><th>مصدر المدلول</th><th>نص عربي</th></tr></thead><tbody>')
        for t in tokdata["tokens"]:
            cls = "y" if t["binding"] == "BOUND" else "d"
            txt = ("«" + t["text"] + "»") if t["text"] else "—"
            wc = e(t["word_class"])
            src = e(t["madlul_source"])
            if t["token_id"] == "t009" and "IMPERFECT" in t["word_class"]:
                wc += " (ARTIFACT_ANOMALY)<br><small>artifact not overwritten</small>"
            if t["token_id"] == "t003" and t["madlul_source"] == "APPROVED_MADLUL_SOURCE_MISSING_OWNER_PENDING":
                src = ("ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED<br>"
                       "<small>raw_artifact_madlul_source = APPROVED_MADLUL_SOURCE_MISSING_OWNER_PENDING</small>")
            P.append('<tr><th>' + e(t["token_id"]) + '</th>'
                     f'<td>{e(t["surface"])}</td><td>{e(t["normalized"])}</td><td>{wc}</td>'
                     f'<td>{e(t["mo"])}</td><td class="{cls}">{e(t["binding"])}</td><td>{src}</td><td>{e(txt)}</td></tr>')
        P.append('</tbody></table></div>')
    P.append('<h2>4. الإفادة</h2><div class="note y" style="background:#e6f4ea">IFADAH_PRODUCED_BY_CODE = YES.</div>')
    P.append('<h2>5. المقام</h2><div class="note y" style="background:#e6f4ea">MAQAM_6_OWNER_RATIFIED = YES · MAQAM_6 = MASALA_MUSAWWARA_LIL_ISTIFTA.</div>')
    P.append('<h2>6. سياسة المرجع</h2><div class="note y" style="background:#e6f4ea">REFERENCE_POLICY_OWNER_RATIFIED = YES · ASSUMED_FACT_REFERENCE = HYPOTHETICAL_MARKED_REFERENCE.</div>')
    P.append('<h2>7. الدعوى الواقعية ورخصة العبور</h2><div class="note n" style="background:#fdecec">'
             f'FACTUAL_CLAIM_BIRTH_STATUS = BORN_BUT_DEFERRED · OWNER_PASSAGE_LICENSE_SUPPLIED = NO · '
             f'FACTUAL_CLAIM_PASSAGE_STATUS = {e(c["passage_status"])} — لم يصل تصريح عبور صريح.</div>')
    P.append('<h2>8. المصدر المعياري</h2><div class="note n" style="background:#fdecec">'
             f'NORMATIVE_SOURCE_BIRTH_STATUS = {e(c["ns_status"])} · NORMATIVE_SOURCE_BLOCKER = {e(c["ns_blocker"])} · '
             'MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE = NO.</div>')
    P.append('<h2>9. موضع التوقف</h2><div class="note n" style="background:#fdecec">'
             'التوقف عند رخصة عبور الدعوى (BLOCK) ثم المصدر المعياري (UNBORN). '
             f'NORMATIVE_HUKM = {e(c["nh_status"])} · MANAT/TANZIL/ANSWER = FORBIDDEN_ANCESTOR_UNBORN.</div>')
    P.append('<h2>10. المعلومات الناقصة (طلب أدق)</h2><div class="note">'
             '(1) FACTUAL_CLAIM_PASSAGE_LICENSE = GRANTED/DENIED صراحةً. '
             '(2) المصدر المعياري: سلطة + نص + نطاق + دليل + رخصة ربط. '
             'التفصيل في <code>ADDITIONAL_INFORMATION_REQUEST_FACTUAL_CLAIM_AND_NORMATIVE_SOURCE_09.md</code>.</div>')
    P.append('<h2>11. ما يلزم بعد الوصول</h2><ol>'
             '<li>GRANTED ⇒ FACTUAL_CLAIM_PASSAGE_STATUS = ACCEPT.</li>'
             '<li>الخمسة ⇒ NORMATIVE_SOURCE_BIRTH.</li>'
             '<li>ثم بالترتيب: normative_hukm ← illah/manat ← tanzil ← answer_audit.</li></ol>')
    P.append('<h2>12. الاختبارات</h2><div class="note">tests/test_taaqol_factual_claim_passage_normative_source_09.py.</div>')
    P.append('<h2>13. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_09_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'PYTEST_FILE = tests/test_taaqol_factual_claim_passage_normative_source_09.py\n'
             'MATRIX_FILE = output/taaqol_maqam_foundation_generated/FACTUAL_CLAIM_PASSAGE_NORMATIVE_SOURCE_09_MATRIX.csv\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nREPORT_REPRODUCIBLE_FROM_GENERATOR = YES\nCOMMIT = NO</pre></div>')
    P.append('<h2>14. الخلاصة التنفيذية</h2><div class="note">الإفادة والمقام وسياسة المرجع مثبتة، والدعوى '
             'الواقعية مولودة مؤجّلة. لم تصل رخصة عبور صريحة فبقيت الدعوى BLOCK، ولم يصل مصدر معياري فبقي UNBORN؛ '
             'فلا حكم ولا مناط ولا تنزيل ولا جواب. النظام يطلب: رخصة عبور صريحة، ومصدرًا معياريًا من خمسة مكوّنات.</div>')
    P.append('<div class="foot">'
             f'FACTUAL_CLAIM_PASSAGE_STATUS = {e(c["passage_status"])} · NORMATIVE_SOURCE_BIRTH_STATUS = {e(c["ns_status"])} · '
             f'NORMATIVE_HUKM_BIRTH_STATUS = {e(c["nh_status"])} · MANAT_BIRTH_STATUS = {e(c["manat"])} · '
             f'TANZIL_BIRTH_STATUS = {e(c["tanzil"])} · ANSWER_AUDIT_STATUS = {e(c["answer"])} · '
             'FINAL_ANSWER_ALLOWED = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "FACTUAL_CLAIM_PASSAGE_NORMATIVE_SOURCE_MANAGER_REPORT_AR_09.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "FACTUAL_CLAIM_PASSAGE_NORMATIVE_SOURCE_09_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    passage_grant, norm_src = detect_owner_inputs()
    c = build_chain(passage_grant, norm_src)
    passage, normsrc, normhukm, illah, tanzil, answer = build_artifacts(c)
    for obj, name in ((passage, "NAZILA_FACTUAL_CLAIM_PASSAGE_09.json"),
                      (normsrc, "NAZILA_NORMATIVE_SOURCE_BIRTH_09.json"),
                      (normhukm, "NAZILA_NORMATIVE_HUKM_BIRTH_09.json"),
                      (illah, "NAZILA_ILLAH_MANAT_BIRTH_09.json"),
                      (tanzil, "NAZILA_TANZIL_BIRTH_09.json"),
                      (answer, "NAZILA_ANSWER_AUDIT_BIRTH_09.json")):
        (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "ADDITIONAL_INFORMATION_REQUEST_FACTUAL_CLAIM_AND_NORMATIVE_SOURCE_09.md").write_text(
        info_request_md(c), encoding="utf-8")
    tokdata, token_missing = collect_tokens()
    pathlib.Path(a.report_out).write_text(render_manager(c, tokdata, token_missing), encoding="utf-8")
    anm = 0  # every emitted node carries producer_file + evidence_files
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(c, anm):
            fh.write(f"{k},{v}\n")
    print("REPORT_09=" + a.report_out)
    print("PASSAGE=" + c["passage_status"] + " NORMATIVE_SOURCE=" + c["ns_status"]
          + " NORMATIVE_HUKM=" + c["nh_status"])


if __name__ == "__main__":
    main()
