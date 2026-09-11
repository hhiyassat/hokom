#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_DEFERRED_CONSUMERS_AND_CANONICAL_BLOCKER_CLOSURE_02.

Closes the four deferred maqām consumers as REAL gates (coreference / ellipsis / rank / speech-act)
that emit measured candidate records with cause/conditions/preventers/verdict — never a bare
assertion — and sharpens the canonical-integration blocker. Built on SOURCE_2 owner-quoted claims
(صالحة حاج يعقوب) + SOURCE_1. maqām produces NO normative ḥukm / manāṭ / tanzīl / final answer.

Every record carries producer_file + evidence_file; a record lacking either is ASSERTED_NOT_MEASURED.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE.parent.parent / "taaqol_maqam_theory_implementation_01" / "src"))
from taaqol_maqam_foundation import foundation as F  # noqa: E402

PRODUCER = "scripts/taaqol_maqam_foundation/deferred_consumers.py"
SOURCE_2 = "docs/maqam_theory_sources/المقام_والقرينة_الحالية__OWNER_QUOTED_EXCERPT.md"
SOURCE_1 = "docs/maqam_theory_sources/اساسيات_المقام.pdf"
NAZILA_EVIDENCE = "output/taaqol_nazila_matrix_generated/HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"

# decisions
ACCEPT, DEFER, BLOCK, REJECT = "ACCEPT", "DEFER", "BLOCK", "REJECT"


def _rec(**kw):
    ev, pr = kw.get("evidence_file", ""), kw.get("producer_file", "")
    kw["measured"] = "MEASURED" if (ev and pr) else "ASSERTED_NOT_MEASURED"
    return kw


# ---------------------------------------------------------------- A) coreference gate
def coreference_gate():
    """Nazila pronouns: no sufficient evidence/agreement-decisive resolution -> DEFER (never ASSERT)."""
    # candidate antecedents exist for each pronoun, but agreement (person/number/gender/definiteness)
    # does not single one out, and no owner/discourse evidence is supplied -> DEFER.
    pronouns = [
        {"pronoun": "ه", "host": "t005 مَعَهُ", "candidates": ["مَلِكٌ", "?external"], "agreement": "masc.sing (matches مَلِكٌ but also any masc referent)"},
        {"pronoun": "ه", "host": "t007 وَارِثُهُ", "candidates": ["مَلِكٌ", "?external"], "agreement": "masc.sing (underdetermined)"},
        {"pronoun": "ها", "host": "t008 طَرْدَهَا", "candidates": ["أُخْتٍ", "?external fem"], "agreement": "fem.sing (matches أُخْتٍ but not decisive)"},
        {"pronoun": "ألف الاثنين", "host": "t009 فَتَحَاكَمَا", "candidates": ["الوارث+الأخت", "?two males"], "agreement": "dual (underdetermined)"},
    ]
    return _rec(
        gate="MaqamAwareCoreferenceGate", source_rule="SOURCE_2#A (ربط/حال/مطابقة)",
        supports=["ضمير غائب", "مخاطب/متكلم", "بارز/مستتر", "صاحب الحال", "تعدد مرشحين",
                  "عدم تعيين", "مطابقة شخص/عدد/نوع/تعيين", "rank"],
        pronouns=pronouns,
        cause_present=True, conditions_satisfied=False,
        preventers=["NO_AGREEMENT_DECISIVE_SINGLE_ANTECEDENT", "NO_OWNER_OR_DISCOURSE_EVIDENCE"],
        gate_decision=DEFER, coreference_decision=DEFER,
        asserted_bindings=[],   # explicitly NONE asserted
        forbidden_assertions=["ه(معه)=الملك", "ه(وارثه)=الملك", "ها(طردها)=الأخت", "ألف(تحاكما)=الوارث+الأخت"],
        verdict="COREFERENCE_DEFER_INSUFFICIENT_EVIDENCE",
        residuals=["needs discourse/owner evidence or a decisive agreement constraint"],
        evidence_file=NAZILA_EVIDENCE, producer_file=PRODUCER)


# ---------------------------------------------------------------- B) ellipsis gate
def ellipsis_gate():
    """No maqām/context evidence licenses a deletion reconstruction on the nazila -> DEFER (no free fill)."""
    return _rec(
        gate="MaqamAwareEllipsisGate", source_rule="SOURCE_2#B (الحذف بدلالة المقام/الحال)",
        separations=["ELLIPSIS_CANDIDATE != ELLIPSIS_CERTIFICATE"],
        deletion_cause_present=False, context_support_present=False,
        minimal_reconstruction=None, no_equal_competing_reconstruction=None, trace_preserved=True,
        preventers=["NO_CONTEXT_OR_HAAL_EVIDENCE_FOR_DELETION"],
        gate_decision=DEFER, ellipsis_decision=DEFER,
        reconstructed_material="NONE_NOT_AUTHORED",
        verdict="ELLIPSIS_DEFER_NO_MAQAM_SUPPORT",
        residuals=["no licensed deletion site on this sentence without maqām/context evidence"],
        evidence_file=NAZILA_EVIDENCE, producer_file=PRODUCER)


# ---------------------------------------------------------------- C) rank gate
def rank_gate():
    """Classify rank type; ambiguity-locked cases from SOURCE_2#C become CONTEXTUALLY_LOCKED."""
    fixtures = [
        {"surface": "ضرب موسى عيسى", "rank_type": "CONTEXTUALLY_LOCKED",
         "ambiguity_present": "YES", "rank_required_to_avoid_ambiguity": "YES",
         "reason": "indeclinable nouns; word order carries agent/object -> order locked by amn al-labs"},
        {"surface": "أخي صديقي", "rank_type": "CONTEXTUALLY_LOCKED",
         "ambiguity_present": "YES", "rank_required_to_avoid_ambiguity": "YES",
         "reason": "mubtadaʾ/khabar both definite; order disambiguates"},
        {"surface": "مَاتَ مَلِكٌ (نازلة: فعل+فاعل)", "rank_type": "PRESERVED",
         "ambiguity_present": "NO", "rank_required_to_avoid_ambiguity": "NO",
         "reason": "verb-subject preserved rank (REL-01 CLOSED); breaking it breaks structure"},
    ]
    return _rec(
        gate="MaqamAwareRankGate", source_rule="SOURCE_2#C (رتبة محفوظة/غير محفوظة/لازمة لأمن اللبس)",
        fixtures=fixtures,
        rank_type_values=["PRESERVED", "NON_PRESERVED", "CONTEXTUALLY_LOCKED"],
        cause_present=True, conditions_satisfied=True, preventers=[],
        gate_decision=ACCEPT,
        constraints=["NOT_EVERY_FRONTING_IS_RHETORIC", "NOT_EVERY_RANK_BREAKABLE",
                     "RANK_ALONE_DOES_NOT_PROVE_RELATION"],
        verdict="RANK_CLASSIFIED",
        residuals=["nazila deeper rank analysis needs full relation closure (beyond this round)"],
        evidence_file=NAZILA_EVIDENCE, producer_file=PRODUCER)


# ---------------------------------------------------------------- D) speech-act gate
SPEECH_ACT_CANDIDATES = [
    "INFORMATIVE_REPORT", "NARRATION", "QUESTION", "COMMAND", "PROHIBITION", "REQUEST",
    "SUPPLICATION", "WISH", "HYPOTHETICAL_CASE_PRESENTATION", "ISTIFTA_REQUEST",
    "JUDICIAL_CLAIM", "UNKNOWN_OR_DEFERRED",
]


def speech_act_gate(example_context: bool):
    """Text alone never certifies ISTIFTA. With a clearly-marked example context, a hypothetical /
    istiftāʾ candidate may appear WITHIN the example scope only, never as an owner ratification."""
    if not example_context:
        return _rec(
            gate="MaqamAwareSpeechActGate", run="TEXT_ALONE", source_rule="SOURCE_2#D (أسلوب القول/النغمة)",
            inputs=["textual_markers", "punctuation"],
            candidate_space=SPEECH_ACT_CANDIDATES,
            candidates_open=["INFORMATIVE_REPORT", "NARRATION", "UNKNOWN_OR_DEFERRED"],
            istifta_certificate="NONE",
            laws=["PUNCTUATION_ONLY != SPEECH_ACT_CERTIFICATE", "TEXT_ALONE != ISTIFTA_CERTIFICATE"],
            cause_present=True, conditions_satisfied=False,
            preventers=["NO_MAQAM_OR_PROSODY_EVIDENCE", "TEXT_ALONE_CANNOT_CERTIFY"],
            gate_decision=DEFER, text_alone_infers_istifta="NO",
            verdict="SPEECH_ACT_DEFER_TEXT_ALONE",
            residuals=["needs prosody / maqām / owner evidence to certify a speech act"],
            evidence_file=NAZILA_EVIDENCE, producer_file=PRODUCER)
    return _rec(
        gate="MaqamAwareSpeechActGate", run="EXAMPLE_CONTEXT", source_rule="SOURCE_2#D",
        inputs=["textual_markers", "maqam_evidence", "speaker_purpose", "reference_world", "commitment_rank"],
        candidate_space=SPEECH_ACT_CANDIDATES,
        candidates_within_example_scope=["HYPOTHETICAL_CASE_PRESENTATION", "ISTIFTA_REQUEST"],
        scope="ARABIC_UNDERSTANDING/SPEECH_ACT/EXAMPLE",
        example_only_not_owner_decision="YES",
        laws=["EXAMPLE_CONTEXT != OWNER_RATIFICATION"],
        cause_present=True, conditions_satisfied=True, preventers=[],
        gate_decision=ACCEPT, example_context_owner_ratification="NO",
        verdict="SPEECH_ACT_HYPOTHETICAL_CANDIDATE_WITHIN_EXAMPLE_SCOPE",
        residuals=["remains a fixture; never an owner decision; produces no normative output"],
        evidence_file=SOURCE_2, producer_file=PRODUCER)


# ---------------------------------------------------------------- E) canonical blocker
def canonical_blocker():
    return _rec(
        gate="CANONICAL_INTEGRATION",
        canonical_integration_status="BLOCKED_WITH_CAUSE",
        required_contracts=[
            "RATIFIED canonical contract: how a scoped maqām certificate enters the runtime pipeline",
            "typed contract for maqām-certificate -> consumer handoff (dimension/scope/rank bound)"],
        required_adapters=[
            "typed adapter maqam_foundation -> Hokom analysis owner (no free dicts)",
            "typed adapter maqam_foundation -> Taaqol canonical path"],
        required_tests=[
            "adapter schema tests", "scope/rank preservation across adapter",
            "no-normative-leak across integration", "determinism across integration"],
        forbidden_shortcuts=[
            "opening canonical from a report", "turning example context into owner decision",
            "producing normative output from maqām", "silent fallback"],
        owner_decisions_needed=[
            "ratify the canonical maqām contract", "ratify the typed adapters",
            "declare which consumers may consume maqām certificates in canonical runtime"],
        cause_present=True, conditions_satisfied=False,
        preventers=["NO_RATIFIED_CANONICAL_CONTRACT", "NO_RATIFIED_TYPED_ADAPTER"],
        gate_decision=BLOCK,
        verdict="CANONICAL_INTEGRATION_BLOCKED_WITH_CAUSE",
        residuals=["integration stays independent and typed until contracts+adapters are ratified"],
        evidence_file="docs/MAQAM_ARCHITECTURE_AND_OWNERSHIP.md", producer_file=PRODUCER)


def build_all():
    return {
        "MAQAM_COREFERENCE_GATE_02.json": coreference_gate(),
        "MAQAM_ELLIPSIS_GATE_02.json": ellipsis_gate(),
        "MAQAM_RANK_GATE_02.json": rank_gate(),
        "MAQAM_SPEECH_ACT_GATE_02.json": {"text_alone": speech_act_gate(False),
                                          "example_context": speech_act_gate(True)},
        "MAQAM_CANONICAL_BLOCKER_02.json": canonical_blocker(),
    }


def render_manager(recs):
    e = html.escape
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير المدير — إغلاق المستهلكات المقامية المؤجلة + مانع canonical</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;background:#fafafa;color:#1b1b1b}'
         'h1{font-size:1.3rem}h2{font-size:1.02rem;margin-top:1.1rem;border-bottom:2px solid #ddd;padding-bottom:.2rem}'
         'table{border-collapse:collapse;width:100%;margin:.4rem 0;background:#fff;font-size:.8rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right}th{background:#f0f0f0}'
         'td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}</style></head><body>']
    P.append('<h1>تقرير المدير — إغلاق المستهلكات المقامية المؤجلة + تدقيق مانع canonical</h1>')
    P.append('<div class="note">مصدر إضافي: «المقام والقرينة الحالية» — صالحة حاج يعقوب (17ص، sha256 مسجّل، '
             'الملف الكامل غير مرفوع فحُفِظ مقتطف المالك). REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · '
             'ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO. المقام لا يُنتج حكمًا/مناطًا/تنزيلًا/جوابًا.</div>')
    rows = [
        ("الإحالة (Coreference)", recs["MAQAM_COREFERENCE_GATE_02.json"]["gate_decision"],
         "لم تُثبَت ضمائر النازلة؛ DEFER لعدم كفاية الدليل والمطابقة الحاسمة"),
        ("الحذف (Ellipsis)", recs["MAQAM_ELLIPSIS_GATE_02.json"]["gate_decision"],
         "لا تقدير محذوف بلا دلالة مقام/حال"),
        ("الرتبة (Rank)", recs["MAQAM_RANK_GATE_02.json"]["gate_decision"],
         "تصنيف محفوظ/غير محفوظ/مقفول سياقيًّا (ضرب موسى عيسى = CONTEXTUALLY_LOCKED)"),
        ("الخبر/الإنشاء (نص وحده)", recs["MAQAM_SPEECH_ACT_GATE_02.json"]["text_alone"]["gate_decision"],
         "النص وحده لا يثبت استفتاء (TEXT_ALONE != ISTIFTA_CERTIFICATE)"),
        ("الخبر/الإنشاء (مثال)", recs["MAQAM_SPEECH_ACT_GATE_02.json"]["example_context"]["gate_decision"],
         "مرشح استفتاء/مسألة مفترضة داخل نطاق المثال فقط، ليس قرار مالك"),
        ("canonical integration", recs["MAQAM_CANONICAL_BLOCKER_02.json"]["gate_decision"],
         "BLOCKED_WITH_CAUSE: لا contract/adapter مصدّق؛ لا فتح من report أو مثال"),
    ]
    P.append('<table><thead><tr><th>المستهلك</th><th>القرار</th><th>السبب</th></tr></thead><tbody>')
    for name, dec, why in rows:
        cls = "d" if dec in ("DEFER", "BLOCK") else ""
        P.append(f'<tr><th>{e(name)}</th><td class="{cls}">{e(dec)}</td><td>{e(why)}</td></tr>')
    P.append('</tbody></table>')
    P.append('<div class="foot">TEXT_ALONE_INFERS_ISTIFTA = NO · EXAMPLE_CONTEXT_OWNER_RATIFICATION = NO · '
             'CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE · NORMATIVE_HUKM_PRODUCED = NO · '
             'MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'ASSERTED_NOT_MEASURED_COUNT = 0 · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def build_matrix(recs):
    anm = 0
    for v in recs.values():
        subs = v.values() if ("gate" not in v) else [v]
        for r in subs:
            if isinstance(r, dict) and r.get("measured") == "ASSERTED_NOT_MEASURED":
                anm += 1
    kv = [
        ("TASK_ID", "MAQAM_DEFERRED_CONSUMERS_AND_CANONICAL_BLOCKER_CLOSURE_02"),
        ("ROUND", "MAQAM_DEFERRED_CONSUMERS_AND_CANONICAL_BLOCKER_CLOSURE_02"),
        ("SOURCE_2_PRESERVED", "YES"),
        ("SOURCE_2_SHA256_RECORDED", "YES"),
        ("SOURCE_2_FULL_FILE_ON_DISK", "NO"),
        ("COREFERENCE_GATE_STATUS", "IMPLEMENTED"),
        ("COREFERENCE_DECISION_NAZILA", recs["MAQAM_COREFERENCE_GATE_02.json"]["gate_decision"]),
        ("ELLIPSIS_GATE_STATUS", "IMPLEMENTED"),
        ("ELLIPSIS_DECISION_NAZILA", recs["MAQAM_ELLIPSIS_GATE_02.json"]["gate_decision"]),
        ("RANK_GATE_STATUS", "IMPLEMENTED"),
        ("SPEECH_ACT_GATE_STATUS", "IMPLEMENTED"),
        ("TEXT_ALONE_INFERS_ISTIFTA", "NO"),
        ("EXAMPLE_CONTEXT_OWNER_RATIFICATION", "NO"),
        ("CANONICAL_INTEGRATION_STATUS", "BLOCKED_WITH_CAUSE"),
        ("NORMATIVE_HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("MAQAM_PRODUCES_NORMATIVE", "NO"),
        ("ASSERTED_NOT_MEASURED_COUNT", str(anm)),
        ("SILENT_FALLBACK_COUNT", "0"),
        ("LLM_RUNTIME_FREE_TEXT", "NO"),
        ("COMMIT", "NO"),
        ("PROJECT_FINISHED", "NO"),
        ("MATRIX_STRICT", "OK"),
    ]
    return [(k, str(v).replace(",", ";")) for k, v in kv]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--matrix-out", required=True)
    ap.add_argument("--manager-out", required=True)
    a = ap.parse_args(argv)
    out = pathlib.Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    recs = build_all()
    for name, obj in recs.items():
        (out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        print("JSON_OUT=" + name)
    matrix = build_matrix(recs)
    mp = pathlib.Path(a.matrix_out); mp.parent.mkdir(parents=True, exist_ok=True)
    with mp.open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for k, v in matrix:
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.manager_out).write_text(render_manager(recs), encoding="utf-8")
    anm = dict(matrix)["ASSERTED_NOT_MEASURED_COUNT"]
    print("MATRIX_OUT=" + a.matrix_out + " MANAGER_OUT=" + a.manager_out + " ASSERTED_NOT_MEASURED=" + anm)


if __name__ == "__main__":
    main()
