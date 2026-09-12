#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for HUSSEIN SCRIPT — the neutral sentence structural report generator.

Proves the report is STRUCTURE-ONLY across three unrelated sentences: no domain decision, no hukm, no final
answer, and zero accepted facts. Also proves the file generation works and the alias entry point exists.
"""
import importlib.util
import json
import pathlib
import re

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
GEN = ROOT / "scripts" / "neutral_sentence_report_generator.py"
ALIAS = ROOT / "scripts" / "hussein_script.py"
OUT = ROOT / "output" / "neutral_sentence_reports"

SENTENCES = [
    "أنا عندي سكري وأريد أن آكل كيلو كنافة مع آيسكريم هل توافق؟",
    "مات ملك عن أخت ساكنة معه فتحاكما",
    "أريد شراء سيارة غدًا",
]


def _mod():
    spec = importlib.util.spec_from_file_location("neutral_gen", GEN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_files_exist():
    assert GEN.exists() and GEN.stat().st_size > 0
    assert ALIAS.exists() and ALIAS.stat().st_size > 0


def test_reports_are_structure_only():
    m = _mod()
    for s in SENTENCES:
        d = m.build_report(s)
        assert d["DOCUMENT_TYPE"] == "NEUTRAL_SENTENCE_STRUCTURAL_REPORT"
        assert d["INPUT_SENTENCE"] == s
        assert d["CONTENT_NEUTRAL"] == "YES"
        assert d["DOMAIN_DECISION"] == "NO"
        assert d["HUKM"] == "NO"
        assert d["FINAL_ANSWER"] == "NO"
        assert d["FACT_ACCEPTED_COUNT"] == 0
        assert d["known_facts"] == []
        assert d["verdict"] == "DEFER_STRUCTURAL_ONLY"
        # no candidate is ever an accepted fact
        for c in d["textual_claim_candidates"] + d["request_or_question_candidates"]:
            assert c["FACT_ACCEPTED"] == "NO"
        # guards
        for k in ("NO_DOMAIN_KNOWLEDGE", "NO_EXTERNAL_SOURCE", "NO_MEDICAL_ADVICE", "NO_FIQH_HUKM",
                  "NO_LEGAL_HUKM", "NO_FACT_ACCEPTANCE", "NO_FINAL_ANSWER", "REPORT_IS_STRUCTURE_ONLY"):
            assert d["guards"][k] == "YES", k


def test_tokens_are_naive_split():
    m = _mod()
    s = SENTENCES[2]
    d = m.build_report(s)
    assert d["token_count"] == len(s.split())
    assert [t["surface"] for t in d["tokens"]] == s.split()


def test_question_form_detected_structurally():
    m = _mod()
    # sentence 1 ends with a question mark -> at least one request/question candidate
    d1 = m.build_report(SENTENCES[0])
    assert len(d1["request_or_question_candidates"]) >= 1
    # sentence 2 has no question form -> only textual candidates
    d2 = m.build_report(SENTENCES[1])
    assert len(d2["request_or_question_candidates"]) == 0
    assert len(d2["textual_claim_candidates"]) >= 1


def test_file_generation_end_to_end():
    m = _mod()
    res = m.write_report(SENTENCES[0], str(OUT))
    for key in ("json", "md", "html"):
        p = pathlib.Path(res[key])
        assert p.exists() and p.stat().st_size > 0, key
    d = json.loads(pathlib.Path(res["json"]).read_text(encoding="utf-8"))
    assert d["DOMAIN_DECISION"] == "NO"
    assert d["HUKM"] == "NO"
    assert d["FINAL_ANSWER"] == "NO"
    assert d["FACT_ACCEPTED_COUNT"] == 0
    # html carries the closure flags and no live links
    htxt = pathlib.Path(res["html"]).read_text(encoding="utf-8")
    assert "CONTENT_NEUTRAL" in htxt and 'id="input-sentence"' in htxt
    assert "http://" not in htxt and "https://" not in htxt


def test_neutral_no_agreement_words_injected():
    m = _mod()
    # The tool must never emit an agreement/refusal/medical verdict of its own.
    d = m.build_report(SENTENCES[0])
    blob = json.dumps(d, ensure_ascii=False)
    for banned in ("نعم أوافق", "لا توافق", "يجب أن", "ممنوع طبيًا", "حرام", "حلال", "RECOMMENDED"):
        assert banned not in blob, banned


# ---- Rich Taaqol-style renderer reuse (round-44 shape, neutral content) ----

R44_HTML = (ROOT / "output" / "taaqol_maqam_foundation_generated"
            / "TAAQOL_OWNER_SUPPLIED_SCENARIO_FULL_MANAT_MANAGER_REPORT_AR_44.html")


def _rich_html():
    m = _mod()
    res = m.write_report(SENTENCES[0], str(OUT))
    return pathlib.Path(res["html"]).read_text(encoding="utf-8")


def test_html_is_rich_and_uses_taaqol_style_renderer():
    t = _rich_html()
    # renderer marker proves the shared generalized renderer was used
    assert "RENDERER=TAAQOL_STYLE" in t
    assert "taaqol-style-manager-report" in t
    # rich executive shape: exactly 14 numbered sections + tables + embedded trace + closure flags
    assert t.count("<h2") == 14, t.count("<h2")
    assert t.count("<table") >= 5
    assert "جدول التتبّع (مستقل عن جدول الوسوم)" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "نتيجة الاختبارات" in t
    # the round-44 CSS shell fingerprints
    assert ".sentbox" in t and 'id="input-sentence"' in t


def test_section_8_title_renamed():
    for s in SENTENCES:
        t = _rich_html_for(s)
        assert "8. المرشحات البنيوية" in t
        assert "8. المصدر المعياري" not in t


def test_html_exactly_14_h2_for_all_sentences():
    for s in SENTENCES:
        t = _rich_html_for(s)
        assert t.count("<h2") == 14, (s, t.count("<h2"))
        numbered = re.findall(r"<h2>(\d+)\.\s", t)
        assert numbered == [str(i) for i in range(1, 15)], (s, numbered)


# Owner-supplied diacritized examples (diabetes + engineering) — regenerated this round.
OWNER_EXAMPLES = [
    "أَنَا عِنْدِي سُكَّرِيٌّ، وَأُرِيدُ أَنْ آكُلَ كِيلُو كُنَافَةٍ مَعَ آيْسْكْرِيم، فَهَلْ تُوَافِقُ؟",
    "أَنَا مُهَنْدِسٌ، وَأُرِيدُ أَنْ أَحْذِفَ عَمُودًا مِنْ بِنَاءٍ قَائِمٍ دُونَ مُخَطَّطَاتٍ إِنْشَائِيَّةٍ، فَهَلْ تُوَافِقُ؟",
]


def test_md_template_parity_with_html():
    m = _mod()
    for s in SENTENCES + OWNER_EXAMPLES:
        res = m.write_report(s, str(OUT))
        md = pathlib.Path(res["md"]).read_text(encoding="utf-8")
        html = pathlib.Path(res["html"]).read_text(encoding="utf-8")
        # MD follows the executive 14-section topology, not the old flat template
        assert "## 8. المرشحات البنيوية" in md
        assert "## 8. Verdict" not in md
        assert "8. المصدر المعياري" not in md
        assert "## 1. Input" not in md              # old flat template markers gone
        assert "## 14. الخلاصة التنفيذية" in md
        # HTML parity
        assert "8. المرشحات البنيوية" in html
        assert "8. المصدر المعياري" not in html
        assert html.count("<h2") == 14
        # neutrality preserved in the JSON
        d = json.loads(pathlib.Path(res["json"]).read_text(encoding="utf-8"))
        assert d["FINAL_ANSWER"] == "NO" and d["DOMAIN_DECISION"] == "NO" and d["HUKM"] == "NO"
        assert d["FACT_ACCEPTED_COUNT"] == 0


def test_owner_examples_neutral_14_h2_no_domain_ruling():
    m = _mod()
    for s in OWNER_EXAMPLES:
        res = m.write_report(s, str(OUT))
        d = json.loads(pathlib.Path(res["json"]).read_text(encoding="utf-8"))
        assert d["DOMAIN_DECISION"] == "NO"
        assert d["HUKM"] == "NO"
        assert d["FINAL_ANSWER"] == "NO"
        assert d["FACT_ACCEPTED_COUNT"] == 0
        assert d["verdict"] == "DEFER_STRUCTURAL_ONLY"
        t = pathlib.Path(res["html"]).read_text(encoding="utf-8")
        assert t.count("<h2") == 14
        assert "8. المرشحات البنيوية" in t
        # no agreement/refusal/domain ruling injected
        for banned in ("أوافق", "لا أوافق", "حرام", "حلال", "ننصح", "يجب عليك", "ممنوع طبيًا",
                       "آمن هندسيًا", "الحكم النهائي"):
            assert banned not in t, (s, banned)


def test_rich_html_stays_neutral():
    t = _rich_html()
    assert "CONTENT_NEUTRAL = YES" in t
    assert "DOMAIN_DECISION = NO" in t
    assert "HUKM = NO" in t
    assert "FINAL_ANSWER = NO" in t
    assert "FACT_ACCEPTED_COUNT = 0" in t
    assert "DEFER_STRUCTURAL_ONLY" in t
    assert "http://" not in t and "https://" not in t


def _rich_html_for(sentence):
    m = _mod()
    res = m.write_report(sentence, str(OUT))
    return pathlib.Path(res["html"]).read_text(encoding="utf-8")


# Round-44 GENERATED content identifiers (never the user's input words).
R44_LEAK_TOKENS = ("FULL_SCENARIO_MANAT", "FSM1_", "OWNER_SUPPLIED_SCENARIO_RENDERING",
                   "SCN1_", "المناط الكامل لسيناريو", "MF1_NO_CHILD", "RENDERING_ATTRIBUTION",
                   "ACCEPTED_FOR_SCENARIO_ONLY")


def test_section_topology_matches_round44_for_all_sentences():
    for s in SENTENCES:
        t = _rich_html_for(s)
        numbered = re.findall(r"<h2>(\d+)\.\s", t)
        assert numbered == [str(i) for i in range(1, 15)], (s, numbered)  # SECTION_COUNT = 14, ordered
        assert "جدول التتبّع (مستقل عن جدول الوسوم)" in t  # TRACE_TABLE_PRESENT
        assert "13. إثبات سلسلة التوليد" in t  # GENERATION_CHAIN_SECTION_PRESENT
        assert "14. الخلاصة التنفيذية" in t  # EXECUTIVE_SUMMARY_SECTION_PRESENT


def test_rich_html_has_no_round44_content():
    for s in SENTENCES:
        t = _rich_html_for(s)
        for leaked in R44_LEAK_TOKENS:
            assert leaked not in t, (s, leaked)


def test_rich_html_has_no_code_opinion_or_ruling():
    t = _rich_html()
    # explicit neutrality statement present as negation only
    assert "لا رأي كود" in t
    for banned in ("أوافق", "لا أوافق", "حرام", "حلال", "ننصح", "يجب عليك"):
        assert banned not in t, banned


def test_round44_artifacts_not_modified():
    # We must not have touched the round-44 report; its signature content must remain intact.
    assert R44_HTML.exists()
    r = R44_HTML.read_text(encoding="utf-8")
    assert "FSM1_SISTER_RESIDENCE_IN_ESTATE_WITH_PERMISSION_AND_EXPULSION_DISPUTE" in r
    assert "RENDERING_ATTRIBUTION" in r
