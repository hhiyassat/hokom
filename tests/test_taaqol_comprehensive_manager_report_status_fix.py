#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REBUILD_MANAGER_REPORT_WITH_EXECUTED_PIPELINE_CONTEXT_03 — documentary guard test.

Verifies the code-generated comprehensive manager report v03, whose display language
distinguishes: منجز / خارج الجولة / محكوم / ينتظر بوابة / ينتظر بيانات — and no longer
mislabels CV / peeling / root / wazn as "ليس بعد" (which read as failure to a manager).
Reads artifacts only; no runtime, no gate, no score change.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
HTML = GEN / "roadmap" / "TAAQOL_NAZILA_COMPREHENSIVE_MANAGER_REPORT_AR_CODE_GENERATED_03.html"
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_MANAGER_REPORT_STATUS_FIX_03.csv"

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
OWNER_TEXT = "الأنثى التي تشارك الشخص في الأبوين أو في أحدهما."
CV_PHRASE = "المقاطع الصوتية ليست موضع هذه الجولة"
ROOT_PHRASE = "الجذر ليس شرطًا لربط madlul_text_ar في t003"
WAZN_PHRASE = "محكوم — PRE_WEIGHT"


def _html():
    assert HTML.exists(), "comprehensive report v03 must exist"
    return HTML.read_text(encoding="utf-8")


def test_report_exists():
    assert HTML.exists()


def test_report_is_artifact_generated():
    assert "REPORT_SOURCE = ARTIFACTS_NOT_LLM_FREE_TEXT" in _html()


def test_no_not_yet_language_for_cv_peeling_root_wazn():
    # "ليس بعد" must not appear at all in v03: none of these stages qualifies
    # (they are done/bypassed, out-of-scope, or guarded — not "never opened, never run").
    assert "ليس بعد" not in _html()


def test_cv_peeling_root_wazn_not_shown_as_failure():
    t = _html()
    for phrase in (CV_PHRASE, ROOT_PHRASE, WAZN_PHRASE):
        assert phrase in t, phrase
    # they must carry positive/neutral wording, not failure words
    for bad in ("فشل", "أخفق", "معطوب"):
        assert bad not in t, bad
    # CV / peeling are framed as منجز/متجاوز (done/bypassed), not a gap
    assert "منجز/متجاوز" in t


def test_has_how_the_manager_reads_section():
    t = _html()
    assert "كيف يقرأ المدير" in t
    for token in ("منجز", "خارج الجولة", "ينتظر بوابة", "ينتظر بيانات"):
        assert token in t, token


def test_binding_waits_ratified_gate():
    assert "ينتظر بوابة مصدّقة" in _html()


def test_score_waits_ratified_score_gate():
    assert "ينتظر بوابة درجة مصدّقة" in _html()


def test_t003_not_bound():
    t = _html()
    assert "t003 NOT BOUND" in t
    bad = [x for x in re.findall(r"t003[^<]*BOUND", t)
           if "NOT BOUND" not in x and "غير BOUND" not in x]
    assert not bad, bad


def test_scores_and_project_flags_unchanged():
    t = _html()
    assert "DOCUMENT = 80.0" in t
    assert "DAL_MADLUL = 90.0" in t
    assert "PROJECT_FINISHED = NO" in t
    for kv in ("RUNTIME_CHANGED = NO", "SCORE_CHANGED = NO", "GATES_OPENED = NO", "COMMIT = NO"):
        assert kv in t, kv


def test_sentence_element_exact_and_clean():
    t = _html()
    m = re.search(r'<div class="sent" id="nazila-sentence">(.*?)</div>', t, flags=re.S)
    assert m and m.group(1) == SENTENCE
    for leak in ("لم يعمل", "ليس بعد", "ومعه"):
        assert leak not in m.group(1)


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _html())


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
