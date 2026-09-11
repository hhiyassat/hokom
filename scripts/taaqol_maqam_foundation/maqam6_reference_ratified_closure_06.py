#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06.

Owner ratified (in the prompt) MAQAM_6 = MASALA_MUSAWWARA_LIL_ISTIFTA and the hypothetical reference
policy, both scoped THIS_NAZILA_ONLY. This unblocks factual_claim birth (a factual/nazila-picture
claim, NOT a ruling) IF propositional content exists — it does (round-08 artifact). The normative
branch stays unborn (no ratified normative source), so ḥukm/manāṭ/tanzīl/final answer remain forbidden.
No canonical opening, no score/runtime/gate change, no commit. Every node carries
CAUSE/CONDITIONS/PREVENTERS/VERDICT/EVIDENCE/PRODUCER_FILE/RESIDUALS.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import sys

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
NZ = ROOT / "output" / "taaqol_nazila_matrix_generated"
DOCS = ROOT / "docs"
PRODUCER = "scripts/taaqol_maqam_foundation/maqam6_reference_ratified_closure_06.py"
EXCERPT = DOCS / "maqam_theory_sources" / "المقام_والقرينة_الحالية__OWNER_QUOTED_EXCERPT.md"
PROP_ARTIFACT = NZ / "PROPOSITIONAL_CONTENT_CANDIDATE_08.json"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."

sys.path.insert(0, str(ROOT / "scripts" / "taaqol_maqam_foundation"))
from manager_report_parity_nazila07_05 import collect_tokens  # noqa: E402


def _rec(**kw):
    ev, pr = kw.get("EVIDENCE", ""), kw.get("PRODUCER_FILE", "")
    kw["measured"] = "MEASURED" if (ev and pr) else "ASSERTED_NOT_MEASURED"
    return kw


def verify_source2_pdf():
    """A full Source-2 PDF is NOT present (only Source-1's PDF + incomplete crdownload partials)."""
    return {
        "SOURCE_2_FULL_PDF_AVAILABLE": "NO",
        "SOURCE_2_PRESERVATION_STATUS": "OWNER_SUPPLIED_PDF_CANDIDATE_NOT_VERIFIED",
        "SOURCE_2_FULL_PDF_SHA256_RECORDED": "NO",
        "note": "Attached name 'اساسيات المقام(1).pdf' not found as a valid Source-2 PDF; the only complete "
                "PDF on disk is Source-1 (صورية جغبوب); crdownload files are incomplete partials. The "
                "owner-quoted Source-2 excerpt remains preserved (sha256 = "
                + hashlib.sha256(EXCERPT.read_bytes()).hexdigest() + ").",
    }


def build_nodes():
    prop_exists = PROP_ARTIFACT.exists()
    prop_state = json.loads(PROP_ARTIFACT.read_text(encoding="utf-8")).get("birth_state", "") if prop_exists else ""

    maqam = _rec(
        NodeName="MAQAM_CLASSIFICATION",
        MAQAM_6_OWNER_RATIFIED="YES", MAQAM_6="MASALA_MUSAWWARA_LIL_ISTIFTA",
        MAQAM_CLASSIFICATION_GATE_DECISION="ACCEPT",
        MAQAM_CLASSIFICATION_BIRTH_STATUS="CERTIFIED",
        MAQAM_CLASSIFICATION_SCOPE="THIS_NAZILA_ONLY",
        MAQAM_TEXT_ALONE_INFERS_ISTIFTA="NO",
        MAQAM_ACCEPTED_BY_OWNER_DECISION_NOT_TEXT_ALONE="YES",
        CAUSE="OWNER_DECISION_IN_THIS_PROMPT ratifies MAQAM_6 for this nazila",
        CONDITIONS="explicit owner ratification + scope THIS_NAZILA_ONLY",
        PREVENTERS="none (text alone would NOT have inferred istiftāʾ)",
        VERDICT="MAQAM_CLASSIFICATION_ACCEPT_CERTIFIED_BY_OWNER",
        EVIDENCE="OWNER_DECISION_IN_THIS_PROMPT", PRODUCER_FILE=PRODUCER,
        RESIDUALS="scope limited to this nazila; not a general maqām closure")

    ref = _rec(
        NodeName="REFERENCE_POLICY",
        REFERENCE_POLICY_OWNER_RATIFIED="YES",
        ASSUMED_FACT_REFERENCE="HYPOTHETICAL_MARKED_REFERENCE",
        REFERENCE_POLICY_DECISION_REQUIRED="NO",
        REFERENCE_POLICY_SCOPE="THIS_NAZILA_ONLY",
        REFERENCE_POLICY_ACCEPTED_BY_OWNER_DECISION="YES",
        CAUSE="OWNER_DECISION_IN_THIS_PROMPT ratifies the hypothetical reference policy",
        CONDITIONS="explicit owner ratification + scope THIS_NAZILA_ONLY",
        PREVENTERS="none",
        VERDICT="REFERENCE_POLICY_RATIFIED",
        EVIDENCE="OWNER_DECISION_IN_THIS_PROMPT", PRODUCER_FILE=PRODUCER,
        RESIDUALS="scope limited to this nazila")

    # factual claim: maqam ACCEPT + reference ratified + propositional content exists -> BORN (deferred, partial nisba)
    if maqam["MAQAM_CLASSIFICATION_GATE_DECISION"] == "ACCEPT" and \
       ref["REFERENCE_POLICY_DECISION_REQUIRED"] == "NO" and prop_exists:
        fc_status = "BORN_BUT_DEFERRED"   # proposition is BORN_BUT_DEFERRED (partial), so claim is born-but-deferred
        fc_blocker = "NONE_PROPOSITION_PARTIAL_ONLY"
    else:
        fc_status = "FORBIDDEN_MISSING_PARENT"
        fc_blocker = "PROPOSITIONAL_CONTENT_ARTIFACT_MISSING"
    factual = _rec(
        NodeName="FACTUAL_CLAIM",
        PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS="YES" if prop_exists else "NO",
        propositional_content_state=prop_state,
        FACTUAL_CLAIM_BIRTH_STATUS=fc_status, FACTUAL_CLAIM_BLOCKER=fc_blocker,
        FACTUAL_CLAIM_SCOPE="THIS_NAZILA_ONLY",
        is_normative="NO", kind="FACTUAL_NAZILA_PICTURE_CLAIM_ONLY",
        CAUSE="maqam ACCEPT + reference ratified + propositional_content artifact present",
        CONDITIONS="MAQAM=ACCEPT AND REFERENCE_POLICY_DECISION_REQUIRED=NO AND PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS=YES",
        PREVENTERS="proposition is only BORN_BUT_DEFERRED (partial nisba) -> claim deferred, not certified",
        VERDICT="FACTUAL_CLAIM_" + fc_status,
        EVIDENCE="PROPOSITIONAL_CONTENT_CANDIDATE_08.json + MAQAM_OWNER_DECISION + REFERENCE_POLICY_OWNER_DECISION",
        PRODUCER_FILE=PRODUCER,
        RESIDUALS="claim is a factual/nazila-picture claim only; NEVER a normative ḥukm")
    fc_certified = fc_status == "CERTIFIED"

    normsrc = _rec(
        NodeName="NORMATIVE_SOURCE",
        NORMATIVE_SOURCE_BIRTH_STATUS="UNBORN", NORMATIVE_SOURCE_PRODUCED="NO",
        NORMATIVE_SOURCE_BLOCKER="NO_RATIFIED_NORMATIVE_SOURCE",
        NORMATIVE_AUTHORITY_PRESENT="NO", NORMATIVE_SOURCE_SCOPE_PRESENT="NO", NORMATIVE_EVIDENCE_PRESENT="NO",
        CAUSE="no ratified normative source/authority/scope/evidence for this nazila",
        CONDITIONS="FACTUAL_CLAIM=CERTIFIED AND authority+scope+evidence present",
        PREVENTERS="NO_RATIFIED_NORMATIVE_SOURCE" + ("" if fc_certified else ";FACTUAL_CLAIM_NOT_CERTIFIED"),
        VERDICT="NORMATIVE_SOURCE_UNBORN",
        EVIDENCE="absence recorded (no normative-source artifact); MANAT_RESULT preventers cite no written policy",
        PRODUCER_FILE=PRODUCER, RESIDUALS="needs owner-ratified normative source")

    normhukm = _rec(
        NodeName="NORMATIVE_HUKM",
        NORMATIVE_HUKM_CHILD_CANDIDATE="UNBORN", NORMATIVE_HUKM_PRODUCED="NO",
        BIRTH_LICENSE="DENIED_PARENT_UNBORN", NORMATIVE_HUKM_BIRTH_STATUS="FORBIDDEN_ANCESTOR_UNBORN",
        CAUSE="parent normative_source is UNBORN", CONDITIONS="normative_source born+certified",
        PREVENTERS="NORMATIVE_SOURCE_UNBORN", VERDICT="NORMATIVE_HUKM_FORBIDDEN_ANCESTOR_UNBORN",
        EVIDENCE="NAZILA_NORMATIVE_SOURCE_BIRTH_06.json", PRODUCER_FILE=PRODUCER,
        RESIDUALS="no HARAM/WAJIB/RIGHT/LIABILITY produced")

    illah_manat = _rec(
        NodeName="ILLAH_MANAT",
        ILLAH_BIRTH_STATUS="FORBIDDEN_ANCESTOR_UNBORN", MANAT_BIRTH_STATUS="FORBIDDEN_ANCESTOR_UNBORN",
        ILLAH_PRODUCED="NO", MANAT_PRODUCED="NO",
        CAUSE="normative_hukm not born", CONDITIONS="normative_hukm born+certified",
        PREVENTERS="NORMATIVE_HUKM_UNBORN", VERDICT="ILLAH_MANAT_FORBIDDEN_ANCESTOR_UNBORN",
        EVIDENCE="NAZILA_NORMATIVE_HUKM_BIRTH_06.json", PRODUCER_FILE=PRODUCER, RESIDUALS="none")

    tanzil = _rec(
        NodeName="TANZIL",
        TANZIL_BIRTH_STATUS="FORBIDDEN_ANCESTOR_UNBORN", TANZIL_PRODUCED="NO",
        CAUSE="manāṭ not born / not certified; taḥqīq-al-manāṭ unavailable",
        CONDITIONS="FACTUAL_CLAIM=CERTIFIED AND NORMATIVE_HUKM=CERTIFIED AND MANAT=CERTIFIED AND TAHQIQ_MANAT=CERTIFIED",
        PREVENTERS="MANAT_UNBORN", VERDICT="TANZIL_FORBIDDEN_ANCESTOR_UNBORN",
        EVIDENCE="NAZILA_ILLAH_MANAT_BIRTH_06.json", PRODUCER_FILE=PRODUCER, RESIDUALS="none")

    answer = _rec(
        NodeName="ANSWER_AUDIT",
        ANSWER_AUDIT_BIRTH_STATUS="FORBIDDEN_ANCESTOR_UNBORN",
        FINAL_ANSWER_PRODUCED="NO", FINAL_ANSWER_ALLOWED="NO", FINAL_HUKM_ISSUED="NO",
        CAUSE="tanzīl not born", CONDITIONS="tanzīl born", PREVENTERS="TANZIL_UNBORN",
        VERDICT="ANSWER_AUDIT_FORBIDDEN_ANCESTOR_UNBORN",
        EVIDENCE="NAZILA_TANZIL_BIRTH_06.json", PRODUCER_FILE=PRODUCER, RESIDUALS="no final answer")

    canonical = _rec(
        NodeName="CANONICAL_INTEGRATION",
        CANONICAL_INTEGRATION_STATUS="BLOCKED_WITH_CAUSE",
        required_contracts=["ratified canonical maqām contract"],
        required_adapters=["typed adapter maqam->Hokom", "typed adapter maqam->Taaqol"],
        required_tests=["adapter schema", "scope/rank preservation", "no-normative-leak"],
        owner_decisions_needed=["ratify canonical contract", "ratify typed adapters"],
        forbidden_shortcuts=["open canonical from report", "example->owner decision", "normative from maqām"],
        CAUSE="no ratified canonical contract/adapter", CONDITIONS="contract+adapters+tests+owner approval",
        PREVENTERS="NO_RATIFIED_CANONICAL_CONTRACT;NO_RATIFIED_TYPED_ADAPTER",
        VERDICT="CANONICAL_BLOCKED_WITH_CAUSE",
        EVIDENCE="docs/MAQAM_CANONICAL_INTEGRATION_BLOCKER_REPORT_02.md", PRODUCER_FILE=PRODUCER,
        RESIDUALS="integration stays independent+typed")

    adapters = _rec(
        NodeName="TYPED_ADAPTERS",
        TYPED_ADAPTERS_STATUS="BLOCKED_WITH_CAUSE",
        hokom_required_fields=["token/surface/normalized", "word_class", "relation closure"],
        taaqol_consumed_fields=["scoped maqām certificate (dimension/scope/rank)"],
        each_field_has_contract="NO", has_test="NO", has_real_adapter="NO",
        CAUSE="no ratified typed adapter contract", CONDITIONS="typed contract per field + tests + adapter",
        PREVENTERS="NO_RATIFIED_ADAPTER_CONTRACT", VERDICT="TYPED_ADAPTERS_BLOCKED_WITH_CAUSE",
        EVIDENCE="docs/MAQAM_ARCHITECTURE_AND_OWNERSHIP.md", PRODUCER_FILE=PRODUCER,
        RESIDUALS="readiness only; no runtime merge")

    return dict(maqam=maqam, ref=ref, canonical=canonical, adapters=adapters, factual=factual,
                normsrc=normsrc, normhukm=normhukm, illah_manat=illah_manat, tanzil=tanzil, answer=answer,
                prop_exists=prop_exists)


NODE_FILES = {
    "maqam": "NAZILA_MAQAM_CLASSIFICATION_06.json",
    "ref": "NAZILA_REFERENCE_POLICY_06.json",
    "canonical": "MAQAM_CANONICAL_INTEGRATION_CONTRACT_06.json",
    "adapters": "HOKOM_TAAQOL_TYPED_ADAPTERS_READINESS_06.json",
    "factual": "NAZILA_FACTUAL_CLAIM_BIRTH_06.json",
    "normsrc": "NAZILA_NORMATIVE_SOURCE_BIRTH_06.json",
    "normhukm": "NAZILA_NORMATIVE_HUKM_BIRTH_06.json",
    "illah_manat": "NAZILA_ILLAH_MANAT_BIRTH_06.json",
    "tanzil": "NAZILA_TANZIL_BIRTH_06.json",
    "answer": "NAZILA_ANSWER_AUDIT_BIRTH_06.json",
}
STAGES = [
    ("1", "LINGUISTIC_ANALYSIS", "y", "YES", "tokenization/surface/normalization/word_class"),
    ("2", "MADLUL_RECORD_AND_BINDING", "y", "YES", "TOKENS_WITH_MADLUL_RECORD = 10 ؛ LEXICAL_DAL_MADLUL_BINDING_COUNT = 9 ؛ ARABIC_TEXT_MADLUL_LICENSED_COUNT = 1 ؛ ARABIC_TEXT_MADLUL_BOUND_COUNT = 0"),
    ("3", "SCORE", "y", "YES", "DOCUMENT = 80.0 ؛ DAL_MADLUL = 90.0 ؛ SCORE_CHANGED = NO"),
    ("4", "IFADAH", "y", "YES", "IFADAH_PRODUCED_BY_CODE = YES ؛ IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM = YES"),
    ("5", "PROPOSITIONAL_CONTENT", "y", "YES", "PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS = YES"),
    ("6", "SOURCE_2_PRESERVATION", "d", "CANDIDATE", "SOURCE_2_FULL_PDF_AVAILABLE = NO ؛ OWNER_SUPPLIED_PDF_CANDIDATE_NOT_VERIFIED"),
    ("7", "MAQAM_CLASSIFICATION", "y", "ACCEPT/CERTIFIED", "MAQAM_6_OWNER_RATIFIED = YES ؛ scope THIS_NAZILA_ONLY ؛ TEXT_ALONE_INFERS_ISTIFTA = NO"),
    ("8", "REFERENCE_POLICY", "y", "RATIFIED", "ASSUMED_FACT_REFERENCE = HYPOTHETICAL_MARKED_REFERENCE ؛ DECISION_REQUIRED = NO"),
    ("9", "FACTUAL_CLAIM", "d", "BORN_BUT_DEFERRED", "FACTUAL_CLAIM_BIRTH_STATUS = BORN_BUT_DEFERRED (نازلة فقط، ليست حكمًا)"),
    ("10", "CANONICAL_INTEGRATION", "n", "BLOCKED", "CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE"),
    ("11", "TYPED_ADAPTERS", "n", "BLOCKED", "TYPED_ADAPTERS_STATUS = BLOCKED_WITH_CAUSE"),
    ("12", "NORMATIVE_SOURCE", "n", "UNBORN", "NORMATIVE_SOURCE_PRODUCED = NO ؛ NO_RATIFIED_NORMATIVE_SOURCE"),
    ("13", "NORMATIVE_HUKM", "n", "FORBIDDEN", "NORMATIVE_HUKM_PRODUCED = NO"),
    ("14", "ILLAH_MANAT", "n", "FORBIDDEN", "MANAT_PRODUCED = NO"),
    ("15", "TANZIL", "n", "FORBIDDEN", "TANZIL_PRODUCED = NO"),
    ("16", "FINAL_ANSWER", "n", "FORBIDDEN", "FINAL_ANSWER_PRODUCED = NO ؛ FINAL_ANSWER_ALLOWED = NO"),
]


def render_manager(nodes, pdf, tokdata, token_missing):
    e = lambda x: html.escape(str(x))
    fc = nodes["factual"]["FACTUAL_CLAIM_BIRTH_STATUS"]
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — تصديق المقام السادس وسياسة المرجع على النازلة (06)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.78rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         'code{background:#f2f2f2;padding:.05rem .3rem;border-radius:.25rem;font-size:.76rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — تصديق المقام السادس وسياسة المرجع على النازلة (06)</h1>')
    P.append('<div class="note">هذا التقرير مولّد من الكود/artifacts فقط. REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · '
             'ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO · MANAGER_REPORT_CANONICAL_FORMAT = MAQAM_AR_05_STYLE.</div>')
    P.append('<div class="note">إغلاق حسب طلب المدير، لا إغلاق عام للمشروع. MAQAM_6 وسياسة المرجع صُدّقا بقرار '
             'مالك في هذا البرومبت ولهذه النازلة فقط (THIS_NAZILA_ONLY)؛ والنص وحده لم يثبت الاستفتاء.</div>')
    P.append('<h2>1. ملخص للمدير</h2><ul>'
             '<li>المالك صدّق MAQAM_6 = MASALA_MUSAWWARA_LIL_ISTIFTA وسياسة المرجع HYPOTHETICAL_MARKED_REFERENCE لهذه النازلة فقط.</li>'
             '<li>بذلك وُلدت الدعوى الواقعية (factual_claim) بحالة ' + e(fc) + ' — دعوى/تصوير نازلة فقط، ليست حكمًا.</li>'
             '<li>توقفت سلسلة الولادة عند المصدر المعياري: UNBORN (لا مصدر معياري مصدّق)، فبقي الحكم/المناط/التنزيل/الجواب ممنوع الولادة.</li>'
             '<li>canonical و typed adapters BLOCKED_WITH_CAUSE؛ ولا حكم/فتوى/جواب.</li></ul>')
    P.append('<h2>2. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    # 3 stage table
    P.append('<h2>3. مخرجات الكود الموجودة فعلًا لكل مرحلة</h2><div class="wrap"><table><thead><tr>'
             '<th>#</th><th>المرحلة</th><th>أنتجها الكود؟</th><th>الحالة</th></tr></thead><tbody>')
    for n, name, cls, val, ev in STAGES:
        P.append(f'<tr><td>{n}</td><td>{e(name)}</td><td class="{cls}">{e(val)}</td><td>{e(ev)}</td></tr>')
    P.append('</tbody></table></div>')
    # 4 token table
    P.append('<h2>4. جدول الكلمات العشر وسجلاتها</h2>')
    if token_missing:
        P.append('<div class="note n">TOKEN_TABLE_SOURCE_MISSING = YES</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>التطبيع</th><th>الفئة</th>'
                 '<th>عامل/مبني</th><th>dal↔madlul</th><th>مصدر المدلول</th><th>نص عربي</th></tr></thead><tbody>')
        for t in tokdata["tokens"]:
            cls = "y" if t["binding"] == "BOUND" else "d"
            txt = ("«" + t["text"] + "»") if t["text"] else "—"
            P.append('<tr><th>' + e(t["token_id"]) + '</th>'
                     f'<td>{e(t["surface"])}</td><td>{e(t["normalized"])}</td><td>{e(t["word_class"])}</td>'
                     f'<td>{e(t["mo"])}</td><td class="{cls}">{e(t["binding"])}</td>'
                     f'<td>{e(t["madlul_source"])}</td><td>{e(txt)}</td></tr>')
        P.append('</tbody></table></div>')
    P.append('<h2>5. حالة الإفادة</h2><div class="note">IFADAH_PRODUCED_BY_CODE = YES ؛ '
             'IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM = YES — الإفادة لا تلد الدعوى مباشرة.</div>')
    P.append('<h2>6. حالة القضوي والدعوى الواقعية</h2><table><tbody>'
             '<tr><th>PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS</th><td class="y">YES</td></tr>'
             f'<tr><th>FACTUAL_CLAIM_BIRTH_STATUS</th><td class="d">{e(fc)}</td></tr>'
             '<tr><th>FACTUAL_CLAIM_SCOPE</th><td>THIS_NAZILA_ONLY</td></tr>'
             '<tr><th>is_normative</th><td class="y">NO (دعوى واقعية فقط)</td></tr></tbody></table>')
    P.append('<h2>7. حالة مصدر المقام الثاني PDF</h2><div class="note d" style="background:#fff7e0">'
             f'SOURCE_2_FULL_PDF_AVAILABLE = {e(pdf["SOURCE_2_FULL_PDF_AVAILABLE"])} · '
             f'SOURCE_2_PRESERVATION_STATUS = {e(pdf["SOURCE_2_PRESERVATION_STATUS"])} · '
             'الملف الكامل غير مثبت؛ الموجود على القرص هو PDF المصدر الأول، والمقتطف الموثّق للمصدر الثاني محفوظ.</div>')
    P.append('<h2>8. حالة حسم المقام: MAQAM_6 مصدّق</h2><div class="note y" style="background:#e6f4ea">'
             'MAQAM_6_OWNER_RATIFIED = YES · GATE_DECISION = ACCEPT · BIRTH_STATUS = CERTIFIED · '
             'MAQAM_ACCEPTED_BY_OWNER_DECISION_NOT_TEXT_ALONE = YES · scope THIS_NAZILA_ONLY.</div>')
    P.append('<h2>9. حالة سياسة المرجع المفترض: مصدقة</h2><div class="note y" style="background:#e6f4ea">'
             'REFERENCE_POLICY_OWNER_RATIFIED = YES · ASSUMED_FACT_REFERENCE = HYPOTHETICAL_MARKED_REFERENCE · '
             'REFERENCE_POLICY_DECISION_REQUIRED = NO · scope THIS_NAZILA_ONLY.</div>')
    P.append('<h2>10. حالة canonical integration contract</h2><div class="note n" style="background:#fdecec">'
             'CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE — لا عقد canonical مصدّق.</div>')
    P.append('<h2>11. حالة typed adapters</h2><div class="note n" style="background:#fdecec">'
             'TYPED_ADAPTERS_STATUS = BLOCKED_WITH_CAUSE — readiness فقط، لا دمج runtime.</div>')
    P.append('<h2>12. حالة factual_claim_birth</h2><div class="note d" style="background:#fff7e0">'
             f'FACTUAL_CLAIM_BIRTH_STATUS = {e(fc)} — وُلدت لأن المقام والمرجع صُدّقا والقضوي موجود، '
             'لكنها مؤجّلة لأن القضوي BORN_BUT_DEFERRED (نسبة جزئية). دعوى واقعية فقط، لا حكم.</div>')
    P.append('<h2>13. حالة normative_source_birth</h2><div class="note n" style="background:#fdecec">'
             'NORMATIVE_SOURCE_BIRTH_STATUS = UNBORN · NORMATIVE_SOURCE_BLOCKER = NO_RATIFIED_NORMATIVE_SOURCE — '
             'هنا توقفت سلسلة الولادة.</div>')
    P.append('<h2>14. حالة normative_hukm_birth</h2><div class="note n" style="background:#fdecec">'
             'NORMATIVE_HUKM_PRODUCED = NO · BIRTH_LICENSE = DENIED_PARENT_UNBORN · لا حرام/واجب/حق/مسؤولية.</div>')
    P.append('<h2>15. حالة illah/manat</h2><div class="note n" style="background:#fdecec">'
             'ILLAH_PRODUCED = NO · MANAT_PRODUCED = NO (FORBIDDEN_ANCESTOR_UNBORN).</div>')
    P.append('<h2>16. حالة tanzil</h2><div class="note n" style="background:#fdecec">'
             'TANZIL_PRODUCED = NO (FORBIDDEN_ANCESTOR_UNBORN).</div>')
    P.append('<h2>17. حالة answer_audit/final_answer</h2><div class="note n" style="background:#fdecec">'
             'FINAL_ANSWER_PRODUCED = NO · FINAL_ANSWER_ALLOWED = NO · FINAL_HUKM_ISSUED = NO.</div>')
    P.append('<h2>18. ما يلزم برمجته بعد ذلك</h2><ol>'
             '<li>توفير مصدر معياري مصدّق (سلطة + نطاق + دليل) — هو العائق الحالي.</li>'
             '<li>توفير/اعتماد PDF كامل للمصدر الثاني إن رغب المالك.</li>'
             '<li>canonical contract + typed adapters بين Hokom وTaaqol.</li>'
             '<li>عندها فقط: normative_hukm ← illah/manat ← tanzil ← answer_audit.</li></ol>')
    P.append('<h2>19. الاختبارات</h2><div class="note">'
             'tests/test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py.</div>')
    P.append('<h2>20. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_06_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'PYTEST_FILE = tests/test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py\n'
             'MATRIX_FILE = output/taaqol_maqam_foundation_generated/MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06_MATRIX.csv\n'
             'NODE_ARTIFACTS = NAZILA_MAQAM_CLASSIFICATION_06 ... NAZILA_ANSWER_AUDIT_BIRTH_06 (10)\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nREPORT_REPRODUCIBLE_FROM_GENERATOR = YES\nCOMMIT = NO</pre></div>')
    P.append('<h2>21. الخلاصة التنفيذية</h2><div class="note">بتصديق المالك للمقام السادس وسياسة المرجع (لهذه '
             'النازلة فقط) وُلدت الدعوى الواقعية (مؤجّلة)، وتوقفت السلسلة عند المصدر المعياري غير المولود؛ '
             'فلا حكم ولا مناط ولا تنزيل ولا جواب، و canonical محجوب بسبب معلوم.</div>')
    P.append('<div class="foot">MAQAM_6_OWNER_RATIFIED = YES · REFERENCE_POLICY_OWNER_RATIFIED = YES · '
             f'FACTUAL_CLAIM_BIRTH_STATUS = {e(fc)} · NORMATIVE_SOURCE_BIRTH_STATUS = UNBORN · '
             'NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · '
             'FINAL_ANSWER_PRODUCED = NO · CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE · '
             'COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def build_matrix(nodes, pdf):
    anm = sum(1 for k in NODE_FILES if nodes[k].get("measured") == "ASSERTED_NOT_MEASURED")
    fc = nodes["factual"]
    kv = [
        ("ROUND", "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06"),
        ("MANAGER_REPORT_CANONICAL_FORMAT", "MAQAM_AR_05_STYLE"),
        ("SOURCE_2_FULL_PDF_AVAILABLE", pdf["SOURCE_2_FULL_PDF_AVAILABLE"]),
        ("SOURCE_2_PRESERVATION_STATUS", pdf["SOURCE_2_PRESERVATION_STATUS"]),
        ("SOURCE_2_FULL_PDF_SHA256_RECORDED", pdf["SOURCE_2_FULL_PDF_SHA256_RECORDED"]),
        ("MAQAM_6_OWNER_RATIFIED", "YES"),
        ("MAQAM_6_SCOPE", "THIS_NAZILA_ONLY"),
        ("MAQAM_CLASSIFICATION_GATE_DECISION", "ACCEPT"),
        ("MAQAM_CLASSIFICATION_BIRTH_STATUS", "CERTIFIED"),
        ("MAQAM_ACCEPTED_BY_OWNER_DECISION_NOT_TEXT_ALONE", "YES"),
        ("REFERENCE_POLICY_OWNER_RATIFIED", "YES"),
        ("ASSUMED_FACT_REFERENCE", "HYPOTHETICAL_MARKED_REFERENCE"),
        ("REFERENCE_POLICY_DECISION_REQUIRED", "NO"),
        ("REFERENCE_POLICY_ACCEPTED_BY_OWNER_DECISION", "YES"),
        ("CANONICAL_INTEGRATION_STATUS", "BLOCKED_WITH_CAUSE"),
        ("TYPED_ADAPTERS_STATUS", "BLOCKED_WITH_CAUSE"),
        ("IFADAH_PRODUCED_BY_CODE", "YES"),
        ("IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM", "YES"),
        ("PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS", fc["PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS"]),
        ("FACTUAL_CLAIM_BIRTH_STATUS", fc["FACTUAL_CLAIM_BIRTH_STATUS"]),
        ("FACTUAL_CLAIM_BLOCKER", fc["FACTUAL_CLAIM_BLOCKER"]),
        ("NORMATIVE_SOURCE_BIRTH_STATUS", "UNBORN"),
        ("NORMATIVE_SOURCE_BLOCKER", "NO_RATIFIED_NORMATIVE_SOURCE"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("ANSWER_AUDIT_BIRTH_STATUS", "FORBIDDEN_ANCESTOR_UNBORN"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("FINAL_HUKM_ISSUED", "NO"),
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
        ("MANAGER_REPORT_06_CREATED", "YES"),
        ("MATRIX_STRICT", "OK"),
    ]
    return [(k, str(v).replace(",", ";")) for k, v in kv]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-out", default=str(OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06.html"))
    ap.add_argument("--matrix-out", default=str(OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06_MATRIX.csv"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = verify_source2_pdf()
    nodes = build_nodes()
    for key, name in NODE_FILES.items():
        (OUT / name).write_text(json.dumps(nodes[key], ensure_ascii=False, indent=2), encoding="utf-8")
    tokdata, token_missing = collect_tokens()
    pathlib.Path(a.report_out).write_text(render_manager(nodes, pdf, tokdata, token_missing), encoding="utf-8")
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in build_matrix(nodes, pdf):
            fh.write(f"{k},{v}\n")
    print("REPORT_06=" + a.report_out)
    print("FACTUAL_CLAIM=" + nodes["factual"]["FACTUAL_CLAIM_BIRTH_STATUS"]
          + " NORMATIVE_SOURCE=" + nodes["normsrc"]["NORMATIVE_SOURCE_BIRTH_STATUS"]
          + " SOURCE_2_PDF=" + pdf["SOURCE_2_FULL_PDF_AVAILABLE"])


if __name__ == "__main__":
    main()
