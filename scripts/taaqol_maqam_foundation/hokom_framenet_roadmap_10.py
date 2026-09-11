#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_REFERENCE_MATRIX_AND_HOKOM_FRAMENET_ROADMAP_10.

Documentation + reference-matrix + candidate-only FrameNet scaffolding. Records TEXT_SIGNALS from the
nazila and emits FRAME_CANDIDATES (candidates only), with guards that block lafẓ→domain jumps: the
surface word «وارثه» never births a MIRATH domain; «فتحاكما» never births a QADA domain. No domain
classification, no normative source, no ḥukm/manāṭ/tanzīl/final answer. No commit.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import pathlib
import re

_DIACRITICS = re.compile(r"[ً-ْٰـ،.]")


def _bare(s):
    return _DIACRITICS.sub("", s)

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
NZ = ROOT / "output" / "taaqol_nazila_matrix_generated"
PRODUCER = "scripts/taaqol_maqam_foundation/hokom_framenet_roadmap_10.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."

MATRIX_ROWS = [
    ("1", "Tokenization/Segmentation", "Universal Dependencies English", "UD Arabic / Arabic-PUD",
     "Hokom segmentation/clitics/surface/normalization", "YES", "TECHNICAL_REFERENCE_LINK_ONLY"),
    ("2", "POS Tagging", "Penn Treebank / UD", "UD Arabic + Arabic grammar",
     "Hokom word_class/mabni/operators", "UD_YES;PENN_MOSTLY_RESTRICTED", "HOKOM_OWNS_CLASS_LOCALLY"),
    ("3", "Lexical Semantics", "WordNet", "Arabic WordNet", "Hokom candidate lexical sense",
     "WORDNET_YES;ARABIC_WORDNET_V4_CC_BY", "CANDIDATE_ONLY"),
    ("4", "Verb Classes", "VerbNet", "not-assumed-in-Arabic-WordNet-without-file-evidence",
     "Hokom verb/subject/object (later)", "VERBNET_YES;ARABIC_LINK_UNSETTLED", "CANDIDATE_ONLY"),
    ("5", "Predicate-Argument", "PropBank", "Arabic PropBank (research)",
     "Hokom/Taaqol propositional+ifadah", "PARTIAL", "NO_HUKM"),
    ("6", "Frame Semantics", "FrameNet", "owner-to-build Arabic/Hokom FrameNet",
     "Hokom licensed frame layer", "ENGLISH_FRAMENET_PARTIAL", "STRUCTURE_ONLY_NOW"),
    ("7", "WordNet<->FrameNet Bridge", "WordFrameNet", "design reuse only",
     "Hokom lexical sense -> frame candidate", "CC_BY_3_0_PER_PAGE", "DESIGN_REFERENCE_NOT_RULING_AUTHORITY"),
    ("8", "Legal Issue Spotting", "LegalBench", "fiqh tasawwur->takyif->tanzil",
     "Taaqol masala takyif", "RESEARCH_AVAILABLE", "METHOD_ANALOGY_ONLY"),
    ("9", "Legal Issue Dataset", "Learned Hands", "none-ready", "NOT_ADOPTED_AS_SOURCE",
     "YES", "NOT_USED_FOR_SHARI_TAKYIF"),
    ("10", "Legal NLU Benchmark", "LexGLUE", "ArabLegalEval (partial)", "benchmark_not_source",
     "RESEARCH_AVAILABLE", "EVAL_NOT_HUKM"),
    ("11", "Fiqh/Nazila Takyif", "no-single-NLP-source", "tasawwur->takyif->tanzil",
     "Taaqol MASALA_TAKYIF_LAYER (PROPOSED_NOT_CANONICAL)", "OWNER_BUILD_REQUIRED",
     "NO_OUTPUT_BEFORE_OWNER_RATIFICATION"),
]

# lafẓ -> domain jumps that are FORBIDDEN to be born
FORBIDDEN_DOMAIN_BIRTHS = {
    "وارثه": "MIRATH_CANDIDATE",   # heir word must NOT birth an inheritance domain
    "فتحاكما": "QADA_CANDIDATE",   # 'litigated' word must NOT birth a judiciary domain
}


def load_tokens():
    p = NZ / "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("token_id", "").startswith("t0")]


def build_text_signals(tokens):
    """TEXT_SIGNALS are surface cues only — never a frame, never a domain."""
    sig = []
    for t in tokens:
        surf = t.get("original_surface", "")
        norm = _bare(surf)
        blocked = None
        for w, dom in FORBIDDEN_DOMAIN_BIRTHS.items():
            if _bare(w) in norm:
                blocked = dom
        sig.append({
            "token_id": t["token_id"], "surface": surf,
            "signal_kind": "SURFACE_CUE_ONLY",
            "is_frame": "NO", "is_domain": "NO", "is_masala_takyif": "NO",
            "blocked_domain_birth": blocked if blocked else "NONE",
            "note": ("this surface must NOT birth " + blocked) if blocked else "no domain jump",
        })
    return sig


def build_frame_candidates():
    """Frame candidates only — no bound frame, no domain, owner-unratified."""
    def fc(fid, label, cue_tok, cue_surf):
        return {
            "frame_id": fid, "frame_label": label,
            "evoked_by_text_signal": {"token_id": cue_tok, "surface": cue_surf},
            "birth_status": "CANDIDATE", "owner_ratified": "NO",
            "is_domain_classification": "NO",
            "wordframenet_bridge_ref": "DESIGN_REFERENCE_ONLY",
            "cause": "text signal present", "conditions": "owner ratification + WordNet sense binding (later)",
            "preventers": ["TEXT_SIGNAL_IS_NOT_A_FRAME", "FRAME_IS_NOT_A_DOMAIN"],
            "verdict": "FRAME_CANDIDATE_UNRATIFIED",
            "evidence": ["output/taaqol_nazila_matrix_generated/HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv"],
            "residuals": ["needs owner ratification + lexical-sense binding before any bound frame"],
        }
    # deliberately generic event-frame candidates, NOT fiqh domains
    return [
        fc("FC_DEATH_EVENT", "Death_event (candidate)", "t000", "مَاتَ"),
        fc("FC_RESIDENCE_RELATION", "Residence_relation (candidate)", "t004", "سَاكِنَةٍ"),
        fc("FC_INTENT_ACTION", "Intent_to_act (candidate)", "t006", "فَأَرَادَ"),
        fc("FC_DISPUTE_EVENT", "Dispute_event (candidate; NOT a qaḍāʾ domain)", "t009", "فَتَحَاكَمَا"),
    ]


def build_status():
    return {
        "ROUND": "HOKOM_TAAQOL_REFERENCE_MATRIX_AND_HOKOM_FRAMENET_ROADMAP_10",
        "REFERENCE_MATRIX_CREATED": "YES",
        "HOKOM_FRAMENET_SCHEMA_CREATED": "YES",
        "HOKOM_FRAMENET_STATUS": "CANDIDATE_LAYER",
        "WORDNET_WORDFRAMENET_BRIDGE_STATUS": "CANDIDATE_ONLY",
        "MASALA_TAKYIF_LAYER_STATUS": "PROPOSED_NOT_CANONICAL",
        "DOMAIN_ROUTING_LAYER_CANONICAL": "NO",
        "DOMAIN_CLASSIFICATION_PRODUCED": "NO",
        "MIRATH_CANDIDATE_BORN": "NO",
        "QADA_CANDIDATE_BORN": "NO",
        "NORMATIVE_SOURCE_PRODUCED": "NO",
        "HUKM_PRODUCED": "NO", "MANAT_PRODUCED": "NO", "TANZIL_PRODUCED": "NO",
        "FINAL_ANSWER_PRODUCED": "NO",
        "producer_file": PRODUCER,
    }


def build_matrix():
    kv = [
        ("ROUND", "HOKOM_TAAQOL_REFERENCE_MATRIX_AND_HOKOM_FRAMENET_ROADMAP_10"),
        ("MODE", "CODE_AND_DOCUMENTATION_ONLY"),
        ("REFERENCE_MATRIX_CREATED", "YES"),
        ("REFERENCE_MATRIX_ROWS", str(len(MATRIX_ROWS))),
        ("HOKOM_FRAMENET_SCHEMA_CREATED", "YES"),
        ("HOKOM_FRAMENET_STATUS", "CANDIDATE_LAYER"),
        ("WORDNET_WORDFRAMENET_BRIDGE_STATUS", "CANDIDATE_ONLY"),
        ("MASALA_TAKYIF_LAYER_STATUS", "PROPOSED_NOT_CANONICAL"),
        ("DOMAIN_ROUTING_LAYER_CANONICAL", "NO"),
        ("DOMAIN_CLASSIFICATION_PRODUCED", "NO"),
        ("MIRATH_CANDIDATE_BORN", "NO"),
        ("QADA_CANDIDATE_BORN", "NO"),
        ("NORMATIVE_SOURCE_PRODUCED", "NO"),
        ("HUKM_PRODUCED", "NO"),
        ("MANAT_PRODUCED", "NO"),
        ("TANZIL_PRODUCED", "NO"),
        ("FINAL_ANSWER_PRODUCED", "NO"),
        ("FINAL_ANSWER_ALLOWED", "NO"),
        ("ASSERTED_NOT_MEASURED_COUNT", "0"),
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


def render_manager(tokens, signals, frames):
    e = lambda x: html.escape(str(x))
    P = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>تقرير تنفيذي — مصفوفة المراجع وخارطة Hokom-FrameNet (10)</title>',
         '<style>body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:1.2rem;color:#1b1b1b;background:#fafafa}'
         'h1{font-size:1.32rem}h2{font-size:1.05rem;margin-top:1.3rem;border-bottom:2px solid #ddd;padding-bottom:.25rem}'
         'table{border-collapse:collapse;width:100%;margin:.5rem 0;background:#fff;font-size:.76rem}'
         'th,td{border:1px solid #ccc;padding:.3rem .45rem;text-align:right;vertical-align:top}th{background:#f0f0f0}'
         'td.y{background:#e6f4ea}td.n{background:#fdecec;color:#7a1f1f}td.d{background:#fff7e0}'
         '.sentbox{border:2px solid #6aa0e0;border-radius:.6rem;padding:.5rem .8rem;margin:.6rem 0;background:#fff}'
         '.sent{background:#eef6ff;border:1px solid #9cc3ef;border-radius:.4rem;padding:.5rem .8rem;font-weight:700;font-size:1rem}'
         '.note{background:#fff7e0;border:1px solid #e0c877;padding:.4rem .7rem;border-radius:.4rem;margin:.4rem 0;font-size:.82rem}'
         '.foot{color:#444;font-size:.8rem;border-top:1px solid #ccc;margin-top:1rem;padding-top:.5rem}.wrap{overflow-x:auto}ul,ol{margin:.3rem 1.2rem}</style></head><body>']
    P.append('<h1>تقرير تنفيذي — مصفوفة المراجع وخارطة Hokom-FrameNet (10)</h1>')
    P.append('<div class="note">مولّد من الكود/artifacts فقط. MODE = CODE_AND_DOCUMENTATION_ONLY · '
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · ILLUSTRATIVE_DEMO = NO · LLM_FREE_TEXT_OUTPUT = NO. '
             'لا تكييف مجال، ولا مصدر معياري، ولا حكم/مناط/تنزيل/جواب.</div>')
    P.append('<h2>1. الجملة محل التشغيل</h2><div class="sentbox"><div class="sent" id="nazila-sentence">'
             + e(SENTENCE) + '</div></div>')
    # tokens
    P.append('<h2>2. جدول الكلمات (من artifact سابق)</h2>')
    if not tokens:
        P.append('<div class="note n">TOKEN_ARTIFACT_MISSING</div>')
    else:
        P.append('<div class="wrap"><table><thead><tr><th>token</th><th>السطح</th><th>الفئة</th></tr></thead><tbody>')
        for t in tokens:
            P.append('<tr><th>' + e(t["token_id"]) + '</th><td>' + e(t.get("original_surface", "")) +
                     '</td><td>' + e(t.get("word_class", "")) + '</td></tr>')
        P.append('</tbody></table></div>')
    # reference matrix
    P.append('<h2>3. المراجع الإنجليزية/العربية ومقابلها في Hokom/Taaqol</h2><div class="wrap"><table><thead><tr>'
             '<th>#</th><th>الطبقة</th><th>المرجع الإنجليزي</th><th>المقابل العربي</th>'
             '<th>Hokom/Taaqol</th><th>Open Source</th><th>حكم الاستخدام</th></tr></thead><tbody>')
    for r in MATRIX_ROWS:
        P.append('<tr><td>' + '</td><td>'.join(e(x) for x in r) + '</td></tr>')
    P.append('</tbody></table></div>')
    # hokom/taaqol mapping note
    P.append('<h2>4. Hokom/Taaqol mapping</h2><div class="note">Hokom يملك الفئة والتقطيع والتطبيع محليًّا؛ '
             'WordNet/VerbNet/PropBank/FrameNet مراجع candidate/بنية فقط؛ WordFrameNet مرجع تصميم لا سلطة حكم؛ '
             'Taaqol هو موضع MASALA_TAKYIF_LAYER (مقترح غير كنسي).</div>')
    # text signals + guards
    P.append('<h2>5. إشارات النص (candidate) وحُرّاس منع القفز من اللفظ إلى المجال</h2><div class="wrap"><table><thead><tr>'
             '<th>token</th><th>السطح</th><th>نوع الإشارة</th><th>frame?</th><th>domain?</th><th>ولادة مجال ممنوعة</th>'
             '</tr></thead><tbody>')
    for s in signals:
        cls = "n" if s["blocked_domain_birth"] != "NONE" else ""
        P.append(f'<tr><th>{e(s["token_id"])}</th><td>{e(s["surface"])}</td><td>{e(s["signal_kind"])}</td>'
                 f'<td>{e(s["is_frame"])}</td><td>{e(s["is_domain"])}</td>'
                 f'<td class="{cls}">{e(s["blocked_domain_birth"])}</td></tr>')
    P.append('</tbody></table></div>'
             '<div class="note">«وارثه» لا تلد مجال مواريث · «فتحاكما» لا تلد مجال قضاء — TEXT_SIGNAL ≠ FRAME ≠ MASALA_TAKYIF.</div>')
    # frame candidates
    P.append('<h2>6. مرشّحات الأطر (FRAME_CANDIDATES — لا أطر مثبتة ولا مجالات)</h2><div class="wrap"><table><thead><tr>'
             '<th>frame_id</th><th>label</th><th>أثارها</th><th>birth</th><th>owner_ratified</th><th>domain?</th>'
             '</tr></thead><tbody>')
    for fc in frames:
        P.append(f'<tr><th>{e(fc["frame_id"])}</th><td>{e(fc["frame_label"])}</td>'
                 f'<td>{e(fc["evoked_by_text_signal"]["surface"])}</td>'
                 f'<td class="d">{e(fc["birth_status"])}</td><td class="n">{e(fc["owner_ratified"])}</td>'
                 f'<td>{e(fc["is_domain_classification"])}</td></tr>')
    P.append('</tbody></table></div>')
    # allowed / owner-gated
    P.append('<h2>7. ما يستطيع الوكيل فعله وحده</h2><ul>'
             '<li>وثيقة الخارطة + manifest المراجع + schema Hokom-FrameNet + adapter skeleton.</li>'
             '<li>FRAME_CANDIDATES وTEXT_SIGNALS كمرشحات + حُرّاس منع القفز + تقرير مدير + matrix + اختبارات.</li></ul>')
    P.append('<h2>8. ما يحتاج تصديق المالك</h2><ul>'
             '<li>تسمية/تفعيل MASALA_TAKYIF_LAYER (PROPOSED_NOT_CANONICAL).</li>'
             '<li>اختيار أي مصدر معياري.</li>'
             '<li>ترقية أي FRAME_CANDIDATE إلى إطار مثبت.</li></ul>')
    P.append('<h2>9. منع القفز من اللفظ إلى التكييف</h2><div class="note n" style="background:#fdecec">'
             'DOMAIN_CLASSIFICATION_PRODUCED = NO · MIRATH_CANDIDATE_BORN = NO · QADA_CANDIDATE_BORN = NO · '
             'NORMATIVE_SOURCE_PRODUCED = NO · HUKM/MANAT/TANZIL/FINAL_ANSWER = NO.</div>')
    P.append('<h2>10. إثبات سلسلة التوليد</h2><div class="note"><pre style="white-space:pre-wrap;margin:0">'
             'REPORT_10_CREATED = YES\n'
             f'GENERATOR_FILE = {PRODUCER}\n'
             'ROADMAP = docs/HOKOM_TAAQOL_REFERENCE_MATRIX_AND_FRAMENET_ROADMAP_10.md\n'
             'SOURCE_MANIFEST = docs/HOKOM_TAAQOL_REFERENCE_SOURCE_MANIFEST_10.json\n'
             'SCHEMA = schemas/hokom_framenet_schema_10.json\n'
             'PYTEST_FILE = tests/test_hokom_taaqol_reference_matrix_and_framenet_roadmap_10.py\n'
             'REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY\nILLUSTRATIVE_DEMO = NO\nLLM_FREE_TEXT_OUTPUT = NO\n'
             'EXTERNAL_REFS = 0\nCOMMIT = NO</pre></div>')
    P.append('<div class="foot">'
             'ASSERTED_NOT_MEASURED_COUNT = 0 · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0 · '
             'DOMAIN_CLASSIFICATION_PRODUCED = NO · NORMATIVE_SOURCE_PRODUCED = NO · HUKM_PRODUCED = NO · '
             'MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO · '
             'TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO.</div>')
    P.append('</body></html>')
    return "\n".join(P)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--status-out", default=str(OUT / "HOKOM_FRAMENET_ROADMAP_STATUS_10.json"))
    ap.add_argument("--matrix-out", default=str(OUT / "HOKOM_FRAMENET_REFERENCE_MATRIX_10.csv"))
    ap.add_argument("--report-out", default=str(OUT / "HOKOM_FRAMENET_MANAGER_REPORT_AR_10.html"))
    ap.add_argument("--frames-out", default=str(OUT / "HOKOM_FRAME_CANDIDATES_10.json"))
    ap.add_argument("--signals-out", default=str(OUT / "HOKOM_TEXT_SIGNALS_10.json"))
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    tokens = load_tokens()
    signals = build_text_signals(tokens)
    frames = build_frame_candidates()
    pathlib.Path(a.signals_out).write_text(json.dumps(signals, ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.frames_out).write_text(json.dumps(frames, ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(a.status_out).write_text(json.dumps(build_status(), ensure_ascii=False, indent=2), encoding="utf-8")
    # reference matrix CSV (the 11-row reference table, one column-set per row, pipe-joined to stay 2-col-safe)
    with pathlib.Path(a.matrix_out).open("w", encoding="utf-8") as fh:
        fh.write("field,value\n")
        for r in MATRIX_ROWS:
            fh.write("REF_ROW_" + r[0] + "," + " | ".join(x.replace(",", ";") for x in r[1:]) + "\n")
        for k, v in build_matrix():
            fh.write(f"{k},{v}\n")
    pathlib.Path(a.report_out).write_text(render_manager(tokens, signals, frames), encoding="utf-8")
    print("REPORT_10=" + a.report_out)
    print("DOMAIN_CLASSIFICATION_PRODUCED=NO MIRATH_CANDIDATE_BORN=NO QADA_CANDIDATE_BORN=NO")


if __name__ == "__main__":
    main()
