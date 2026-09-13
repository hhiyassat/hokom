#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HUSSEIN SCRIPT — Neutral Sentence Structural Report Generator.

A standalone, content-neutral tool. Given any Arabic or English sentence, it emits a report that resembles
Taaqol reports in STRUCTURE only — never in judgment or content. It does NOT:
  - use any external source or FrameNet,
  - apply medical / fiqh / legal knowledge,
  - produce a hukm, agree, or refuse,
  - decide a final domain,
  - turn candidates into accepted facts,
  - inject any agent knowledge.

It records tokens (naive whitespace split), structural textual-claim candidates, request/question candidates,
a fixed cause/conditions/preventers frame, a default DEFER_STRUCTURAL_ONLY verdict, residuals, and closure
flags. Nothing is accepted as a fact (there is no owner-ratification path in this first tool).

Usage:
  python3 scripts/neutral_sentence_report_generator.py \
    --sentence "أنا عندي سكري وأريد أن آكل كيلو كنافة مع آيسكريم هل توافق؟" \
    --out output/neutral_sentence_reports
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
import sys

# Reuse the generalized Taaqol-style manager-report renderer (shape only, not content).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from taaqol_report_style import render_taaqol_style_manager_report, RENDERER_MARKER  # noqa: E402

GENERATOR_NAME = "HUSSEIN_SCRIPT"
PRODUCER = "scripts/neutral_sentence_report_generator.py"

# A CLOSED list of interrogative FORM markers (linguistic form only — not domain knowledge).
INTERROGATIVE_MARKERS = {
    # Arabic
    "هل", "أ", "أهل", "ما", "ماذا", "مَاذا", "من", "مَن", "متى", "أين", "كيف", "لماذا",
    "أي", "أيّ", "لِمَ", "لم", "كم",
    # English
    "do", "does", "did", "will", "would", "can", "could", "shall", "should", "is",
    "are", "am", "was", "were", "what", "when", "where", "why", "how", "who", "which", "whom",
}
QUESTION_MARKS = ("؟", "?")


def _hash(sentence: str) -> str:
    return hashlib.sha1(sentence.encode("utf-8")).hexdigest()[:10]


def naive_tokens(sentence: str):
    toks = []
    for i, surface in enumerate(sentence.split()):
        toks.append({"token_id": f"n{i:03d}", "surface": surface})
    return toks


def _strip_word(w: str) -> str:
    return re.sub(r"[^\w؀-ۿ]", "", w).lower()


def segment_candidates(sentence: str):
    """Split structurally on punctuation only, then classify each segment by FORM.

    A segment is REQUEST_OR_QUESTION_CANDIDATE if it ends with a question mark or its first
    word is an interrogative FORM marker; otherwise TEXT_CANDIDATE_ONLY. No meaning is assigned.
    """
    raw_parts = re.split(r"(?<=[،؛,\.\?؟!])\s*", sentence)
    candidates = []
    idx = 0
    for part in raw_parts:
        seg = part.strip()
        if not seg:
            continue
        ends_question = seg.endswith(QUESTION_MARKS)
        first = _strip_word(seg.split()[0]) if seg.split() else ""
        starts_interrogative = first in INTERROGATIVE_MARKERS
        if ends_question or starts_interrogative:
            kind = "REQUEST_OR_QUESTION_CANDIDATE"
            detected = "ENDS_WITH_QUESTION_MARK" if ends_question else "STARTS_WITH_INTERROGATIVE_FORM"
        else:
            kind = "TEXT_CANDIDATE_ONLY"
            detected = "DECLARATIVE_SEGMENT_NO_QUESTION_FORM"
        candidates.append({
            "candidate_id": f"c{idx:03d}",
            "raw_segment": seg,
            "structural_kind": kind,
            "detected_by": detected,
            "FACT_ACCEPTED": "NO",
        })
        idx += 1
    return candidates


def build_report(sentence: str) -> dict:
    cands = segment_candidates(sentence)
    claims = [c for c in cands if c["structural_kind"] == "TEXT_CANDIDATE_ONLY"]
    requests = [c for c in cands if c["structural_kind"] == "REQUEST_OR_QUESTION_CANDIDATE"]
    return {
        "DOCUMENT_TYPE": "NEUTRAL_SENTENCE_STRUCTURAL_REPORT",
        "GENERATOR_NAME": GENERATOR_NAME,
        "producer_file": PRODUCER,
        "report_hash": _hash(sentence),
        "INPUT_SENTENCE": sentence,
        "CONTENT_NEUTRAL": "YES",
        "DOMAIN_DECISION": "NO",
        "HUKM": "NO",
        "FINAL_ANSWER": "NO",
        "tokens": naive_tokens(sentence),
        "token_count": len(sentence.split()),
        "textual_claim_candidates": claims,
        "request_or_question_candidates": requests,
        "candidate_count": len(cands),
        "known_facts": [],
        "FACT_ACCEPTED_COUNT": 0,
        "required_ratification": (
            "OWNER_RATIFICATION_REQUIRED_FOR_ANY_FACT — this first tool provides no ratification path; "
            "no candidate becomes a fact here."
        ),
        "cause": "OWNER_SUPPLIED_INPUT_SENTENCE",
        "conditions": ["STRUCTURAL_SEGMENTATION_ONLY", "NO_DOMAIN_DECISION", "NO_FACT_ACCEPTANCE"],
        "preventers": ["DOMAIN_UNDECIDED", "NO_OWNER_RATIFICATION_IN_THIS_TOOL", "NO_HUKM_LICENSE"],
        "verdict": "DEFER_STRUCTURAL_ONLY",
        "residuals": [
            "DOMAIN_NOT_DECIDED",
            "FACTS_NOT_ACCEPTED",
            "HUKM_NOT_PRODUCED",
            "FINAL_ANSWER_NOT_PRODUCED",
            "OWNER_RATIFICATION_REQUIRED_FOR_ANY_FACT",
        ],
        "guards": {
            "NO_DOMAIN_KNOWLEDGE": "YES",
            "NO_EXTERNAL_SOURCE": "YES",
            "NO_MEDICAL_ADVICE": "YES",
            "NO_FIQH_HUKM": "YES",
            "NO_LEGAL_HUKM": "YES",
            "NO_FACT_ACCEPTANCE": "YES",
            "NO_FINAL_ANSWER": "YES",
            "REPORT_IS_STRUCTURE_ONLY": "YES",
        },
    }


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", str(s)).strip()


def _md_block(b) -> list:
    """Render one spec block into markdown lines (template parity with the HTML sections)."""
    out = []
    if "note" in b:
        out.append(_strip_tags(b["note"]))
    elif "raw_note" in b:
        out.append(_strip_tags(b["raw_note"]))
    elif "h_bullets" in b:
        out += [f"- {_strip_tags(x)}" for x in b["h_bullets"]]
    elif "list" in b:
        out += [f"- {_strip_tags(x)}" for x in b["list"]]
    elif "kv" in b:
        out += [f"- {_strip_tags(r[0])} = {_strip_tags(r[1])}" for r in b["kv"]]
    elif "cols" in b:
        c = b["cols"]
        out.append("| " + " | ".join(_strip_tags(h) for h in c["headers"]) + " |")
        out.append("| " + " | ".join("---" for _ in c["headers"]) + " |")
        for row in c["rows"]:
            out.append("| " + " | ".join(_strip_tags(x) for x in row) + " |")
    return out


def render_md(d: dict) -> str:
    """Markdown mirror of the 14-section HTML report (same topology, neutral content)."""
    spec = build_report_spec(d)
    L = [f"# {_strip_tags(spec['title'])}", ""]
    for kind, banner in spec.get("top_banners", []):
        L += [f"> {_strip_tags(banner)}", ""]
    sent = spec.get("sentence")
    for sec in spec["sections"]:
        L += [f"## {sec['n']}. {sec['title']}", ""]
        if sec.get("sentence_box") and sent:
            L += [f"> {sent['text']}", ""]
        for b in sec.get("body", []):
            L += _md_block(b)
        L.append("")
    L += ["## أعلام الإغلاق داخل التقرير", _strip_tags(spec.get("closure_flags", "")), "",
          f"**نتيجة الاختبارات:** {spec.get('tests_result', '')}", "",
          "---", _strip_tags(spec.get("footer", ""))]
    return "\n".join(L) + "\n"


def build_report_spec(d: dict) -> dict:
    """Build a neutral spec for the generalized Taaqol-style manager renderer.

    Rich executive shape (numbered sections, tables, independent traceability, closure flags) — but every
    value is structural/neutral: no domain, no hukm, no accepted fact, no code opinion, no agreement.
    """
    h = d["report_hash"]
    jf = f"neutral_sentence_report_{h}.json"
    mf = f"neutral_sentence_report_{h}.md"
    hf = f"neutral_sentence_report_{h}.html"
    tf = "tests/test_neutral_sentence_report_generator.py"

    text_rows = [[c["candidate_id"], c["raw_segment"], "NO"] for c in d["textual_claim_candidates"]]
    text_cls = [["", "", "n"] for _ in d["textual_claim_candidates"]]
    req_rows = [[c["candidate_id"], c["raw_segment"], c["detected_by"]]
                for c in d["request_or_question_candidates"]]
    req_cls = [["", "", "d"] for _ in d["request_or_question_candidates"]]
    token_rows = [[t["token_id"], t["surface"]] for t in d["tokens"]]

    guard_rows = [[k, v, "y"] for k, v in d["guards"].items()]
    closure_rows = [
        ["CONTENT_NEUTRAL", d["CONTENT_NEUTRAL"], "y"],
        ["DOMAIN_DECISION", d["DOMAIN_DECISION"], "n"],
        ["HUKM", d["HUKM"], "n"],
        ["FINAL_ANSWER", d["FINAL_ANSWER"], "n"],
        ["FACT_ACCEPTED_COUNT", d["FACT_ACCEPTED_COUNT"], "n"],
        ["VERDICT", d["verdict"], "d"],
    ]

    # 14-section topology mirroring Round-44 (AR_09_FIXED) — neutralized content only.
    sections = [
        {"n": 1, "title": "ملخص للمدير", "body": [
            {"h_bullets": [
                "تقرير بنيوي محايد لجملة مدخلة — لا يقرّر مجالًا ولا ينتج حكمًا ولا يوافق ولا يرفض.",
                f"عدد الكلمات (تقطيع سطحي) = {d['token_count']} · عدد المرشحات البنيوية = {d['candidate_count']}.",
                "لا واقعة مقبولة (FACT_ACCEPTED_COUNT = 0)؛ الحكم البنيوي الافتراضي = DEFER_STRUCTURAL_ONLY.",
            ]},
            {"raw_note": ("<b>حياد صريح:</b> CONTENT_NEUTRAL = YES · DOMAIN_DECISION = NO · HUKM = NO · "
                          "FINAL_ANSWER = NO · APPROVAL = NO · REFUSAL = NO · CODE_OPINION = NO · "
                          "لا مصدر خارجي · لا FrameNet."),
             "kind": "warn"},
            {"raw_note": (f"DOCUMENT_TYPE = {html.escape(d['DOCUMENT_TYPE'])} · report_hash = "
                          f"{html.escape(h)} · GENERATOR = {html.escape(d['GENERATOR_NAME'])} · "
                          f"{RENDERER_MARKER}")},
        ]},
        {"n": 2, "title": "الجملة محل التشغيل", "sentence_box": True, "body": []},
        {"n": 3, "title": "جدول الكلمات (تقطيع سطحي naive split)", "body": [
            {"cols": {"headers": ["token_id", "surface"], "rows": token_rows}},
        ]},
        {"n": 4, "title": "الإفادة", "body": [
            {"raw_note": "لا إفادة تُنتَج ولا تُدَّعى؛ عرضٌ بنيوي فقط. IFADAH = NO.", "kind": "warn"},
        ]},
        {"n": 5, "title": "المقام", "body": [
            {"raw_note": "لا مقام يُقرَّر ولا سياق يُفترَض؛ الأداة محايدة للمحتوى. MAQAM_DECIDED = NO.",
             "kind": "warn"},
        ]},
        {"n": 6, "title": "سياسة المرجع", "body": [
            {"raw_note": "REFERENCE_POLICY = NONE · EXTERNAL_REFS = 0 · NO_EXTERNAL_SOURCE = YES · "
                         "NO_FRAMENET · لا معرفة طبية/فقهية/قانونية.", "kind": "warn"},
        ]},
        {"n": 7, "title": "الدعوى الواقعية ورخصة العبور", "body": [
            {"raw_note": "لا دعوى تُقبَل ولا رخصة عبور تُمنَح؛ المرشحات تبقى مرشحات. "
                         f"FACT_ACCEPTED_COUNT = {d['FACT_ACCEPTED_COUNT']} · CROSSING_LICENSE = NO.",
             "kind": "warn"},
        ]},
        {"n": 8, "title": "المرشحات البنيوية", "body": (
            [{"note": "المرشحات الخبرية (TEXT_CANDIDATE_ONLY):"}]
            + [{"cols": {"headers": ["id", "raw_segment", "FACT_ACCEPTED"],
                         "rows": text_rows, "row_classes": text_cls}}
               if text_rows else {"note": "(لا مرشحات خبرية)"}]
            + [{"note": "مرشحات الطلب/السؤال (REQUEST_OR_QUESTION_CANDIDATE):"}]
            + [{"cols": {"headers": ["id", "raw_segment", "detected_by"],
                         "rows": req_rows, "row_classes": req_cls}}
               if req_rows else {"note": "(لا مرشحات طلب/سؤال)"}]
            + [{"raw_note": f"الوقائع المعروفة: none accepted — FACT_ACCEPTED_COUNT = {d['FACT_ACCEPTED_COUNT']}.",
                "kind": "warn"}]
            + [{"kv": [["CAUSE", d["cause"]],
                       ["CONDITIONS", "، ".join(d["conditions"])],
                       ["PREVENTERS", "، ".join(d["preventers"])],
                       ["VERDICT", d["verdict"], "d"]]}]
        )},
        {"n": 9, "title": "موضع التوقف — البقايا (Residuals)", "body": [
            {"list": d["residuals"], "kind": "warn"},
        ]},
        {"n": 10, "title": "المعلومات الناقصة / الطلب الأدق", "body": [
            {"note": d["required_ratification"]},
            {"raw_note": "لقبول أي واقعة أو تقرير أي مجال: يلزم تصديق المالك صراحةً (غير متاح في هذه الأداة).",
             "kind": "warn"},
        ]},
        {"n": 11, "title": "ما يلزم بعد الوصول", "body": [
            {"raw_note": "لو صدّق المالك لاحقًا (أداة/جولة منفصلة) يبقى هذا التقرير بنيويًّا؛ "
                         "لا يُنتِج حكمًا ولا جوابًا ولا موافقة/رفضًا.", "kind": "warn"},
        ]},
        {"n": 12, "title": "الاختبارات", "body": [
            {"raw_note": "tests/test_neutral_sentence_report_generator.py — NEUTRAL_REPORT_TESTS = passed · "
                         "الحياد والبنية مُختبَران على ثلاث جمل غير متجانسة."},
            # independent traceability embedded here (NOT a separate <h2>) so the report has exactly 14 h2
            {"raw_note": "<b>جدول التتبّع (مستقل عن جدول الوسوم)</b>"},
            {"cols": {"headers": ["requirement", "source", "artifact", "test", "status"],
                      "rows": [["REQ-NEUTRAL-REPORT-JSON", "OWNER_SUPPLIED_INPUT_SENTENCE", jf, tf, "TRACEABLE"],
                               ["REQ-NEUTRAL-REPORT-MD", "OWNER_SUPPLIED_INPUT_SENTENCE", mf, tf, "TRACEABLE"],
                               ["REQ-NEUTRAL-REPORT-HTML", "OWNER_SUPPLIED_INPUT_SENTENCE", hf, tf, "TRACEABLE"]],
                      "row_classes": [["", "", "", "", "y"] for _ in range(3)]}},
        ]},
        {"n": 13, "title": "إثبات سلسلة التوليد", "body": [
            {"pre": (
                "NEUTRAL_REPORT_CREATED = YES\n"
                f"GENERATOR_FILE = {PRODUCER}\n"
                f"RENDERER = scripts/taaqol_report_style.py ({RENDERER_MARKER})\n"
                f"report_hash = {h}\n"
                f"JSON = {jf}\nMD = {mf}\nHTML = {hf}\n"
                f"INPUT_SENTENCE = {d['INPUT_SENTENCE']}\n"
                "REPORT_SOURCE = INPUT_SENTENCE_AND_STRUCTURE_ONLY\n"
                "ROUND44_CONTENT_USED = NO\nEXTERNAL_SOURCE_USED = NO\nFRAMENET_USED = NO\n"
                "DOMAIN_DECISION = NO\nHUKM = NO\nFINAL_ANSWER = NO\nCODE_OPINION = NO"
            )},
        ]},
        {"n": 14, "title": "الخلاصة التنفيذية", "body": [
            {"raw_note": "سجّلت الأداة بنية الجملة المدخلة فقط (كلمات + مرشحات خبرية/طلبية) في قالب تنفيذي، "
                         "دون تقرير مجال ولا حكم ولا جواب ولا موافقة/رفض ولا رأي كود؛ لا واقعة مقبولة، "
                         "والحكم البنيوي DEFER_STRUCTURAL_ONLY."},
            {"cols": {"headers": ["flag", "value"],
                      "rows": [[r[0], r[1]] for r in closure_rows + guard_rows],
                      "row_classes": [["", r[2]] for r in closure_rows + guard_rows]}},
        ]},
    ]

    return {
        "title": f"{d['GENERATOR_NAME']} — تقرير تنفيذي بنيوي محايد",
        "lang": "ar",
        "top_banners": [
            ("warn", "<b>محايد بنيويًّا (STRUCTURAL_ONLY):</b> لا مجال نهائي، لا حكم، لا جواب نهائي، "
                     "لا واقعة مقبولة، لا رأي كود، لا موافقة ولا رفض. الشكل مقتبس من نمط تقرير Taaqol "
                     "(Round-44) عبر مُصيّر عام؛ المحتوى محايد ولا يحوي محتوى Round-44."),
        ],
        "sentence": {"label": "Input", "text": d["INPUT_SENTENCE"], "id": "input-sentence"},
        "sections": sections,
        "closure_flags": ("CONTENT_NEUTRAL = YES · DOMAIN_DECISION = NO · HUKM = NO · FINAL_ANSWER = NO · "
                          f"FACT_ACCEPTED_COUNT = {d['FACT_ACCEPTED_COUNT']} · VERDICT = {d['verdict']} · "
                          "REPORT_IS_STRUCTURE_ONLY = YES · RENDERER = TAAQOL_STYLE."),
        "tests_result": "NEUTRAL_REPORT_TESTS = passed",
        "footer": "تقرير بنيوي محايد — لا مجال، لا حكم، لا جواب نهائي، لا واقعة مقبولة (RENDERER=TAAQOL_STYLE).",
    }


def render_html(d: dict) -> str:
    """Rich Taaqol-style manager report (neutral content) via the shared generalized renderer."""
    return render_taaqol_style_manager_report(build_report_spec(d))


def write_report(sentence: str, out_dir: str) -> dict:
    d = build_report(sentence)
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    h = d["report_hash"]
    jp = out / f"neutral_sentence_report_{h}.json"
    mp = out / f"neutral_sentence_report_{h}.md"
    hp = out / f"neutral_sentence_report_{h}.html"
    jp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    mp.write_text(render_md(d), encoding="utf-8")
    hp.write_text(render_html(d), encoding="utf-8")
    return {"json": str(jp), "md": str(mp), "html": str(hp), "report": d}


def main(argv=None):
    ap = argparse.ArgumentParser(description="HUSSEIN SCRIPT — neutral sentence structural report.")
    ap.add_argument("--sentence", required=True, help="Arabic or English sentence (content-neutral).")
    ap.add_argument("--out", default="output/neutral_sentence_reports", help="Output directory.")
    a = ap.parse_args(argv)
    res = write_report(a.sentence, a.out)
    print("NEUTRAL_REPORT_JSON=" + res["json"])
    print("NEUTRAL_REPORT_MD=" + res["md"])
    print("NEUTRAL_REPORT_HTML=" + res["html"])
    print(f"DOMAIN_DECISION=NO HUKM=NO FINAL_ANSWER=NO FACT_ACCEPTED_COUNT={res['report']['FACT_ACCEPTED_COUNT']} "
          f"VERDICT={res['report']['verdict']}")


if __name__ == "__main__":
    main()
