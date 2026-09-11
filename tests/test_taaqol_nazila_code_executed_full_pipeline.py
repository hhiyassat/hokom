#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAZILA_ONLY_CODE_EXECUTED_FULL_PIPELINE_06 — documentary guard test.

Verifies the code-executed manager report: every stage value is read from a code-produced
artifact (not authored). manāṭ/ifādah/ḥukm ARE code-produced (deferral / partial); tanzīl and
the final answer are honestly NOT_PRODUCED_BY_CODE. No LLM-attributed result; no ruling.
Reads artifacts only; no runtime, no gate, no score change.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
HTML = GEN / "roadmap" / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_06.html"
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_CODE_EXECUTED_FULL_PIPELINE_06.csv"

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
WORDS = ["مَاتَ", "مَلِكٌ", "عَنْ", "أُخْتٍ", "سَاكِنَةٍ", "مَعَهُ",
         "فَأَرَادَ", "وَارِثُهُ", "طَرْدَهَا", "فَتَحَاكَمَا"]


def _html():
    assert HTML.exists(), "code-executed report must exist"
    return HTML.read_text(encoding="utf-8")


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_mode_flags_code_executed():
    m = _matrix()
    assert m["CODE_EXECUTED_OUTPUT"] == "YES"
    assert m["ILLUSTRATIVE_DEMO"] == "NO"
    assert m["LLM_FREE_TEXT_OUTPUT"] == "NO"
    assert m["REPORT_SOURCE"] == "CODE_AND_ARTIFACTS_ONLY"
    t = _html()
    assert "REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY" in t
    assert "ILLUSTRATIVE_DEMO = NO" in t


def test_all_ten_words_present():
    t = _html()
    for w in WORDS:
        assert w in t, w
    m = re.search(r'<div class="sent" id="nazila-sentence">(.*?)</div>', t, flags=re.S)
    assert m and m.group(1) == SENTENCE


def test_token_records_and_licensed_text():
    m = _matrix()
    assert m["TOTAL_NAZILA_TOKENS"] == "10"
    assert m["TOKENS_WITH_MADLUL_RECORD"] == "10"
    assert m["TOKENS_WITH_LICENSED_MADLUL_TEXT"] == "1"
    assert m["DAL_MADLUL_BOUND_COUNT"] == "9"


def test_early_stages_produced_by_code():
    m = _matrix()
    for k in ("TOKENIZATION_PRODUCED_BY_CODE", "SURFACE_PRODUCED_BY_CODE",
              "NORMALIZATION_PRODUCED_BY_CODE", "WORD_CLASS_PRODUCED_BY_CODE",
              "MABNI_OPERATOR_PRODUCED_BY_CODE", "MADLUL_RECORD_PRODUCED_BY_CODE",
              "BINDING_PRODUCED_BY_CODE", "SCORE_PRODUCED_BY_CODE"):
        assert m[k] == "YES", k


def test_manat_is_code_produced_deferral_not_authored():
    # code DID run the manāṭ gate; it produced a DEFER verdict — not an authored manāṭ
    m = _matrix()
    assert m["MANAT_GATE_PRODUCED_BY_CODE"] == "YES"
    assert m["MANAT_OPENED"] == "NO"
    assert m["MANAT_AUTHORED_BY_AGENT"] == "NO"
    assert m["MANAT_VERDICT"] == "MANAT_DEFERRED_NO_NORMATIVE_ILLAH_LOCUS"
    assert m["MANAT_FULL_NAZILA"] == "NO"


def test_ifadah_and_hukm_are_code_produced_partial():
    m = _matrix()
    assert m["IFADAH_PRODUCED_BY_CODE"] == "YES"
    assert m["IFADAH_AUTHORED_BY_AGENT"] == "NO"
    assert m["IFADAH_KIND"] == "PARTIAL_IFADAH"
    assert m["HUKM_PRODUCED_BY_CODE"] == "YES"
    assert m["HUKM_FULL_NAZILA"] == "NO"


def test_tanzil_not_produced_by_code():
    m = _matrix()
    assert m["TANZIL_PRODUCED_BY_CODE"] == "NO"
    assert m["TANZIL_STATUS"] == "NOT_PRODUCED_BY_CODE"
    assert m["TANZIL_REQUIRED"] == "IMPLEMENT_RATIFIED_TANZIL_ENGINE"
    assert m["TANZIL_AUTHORED_BY_AGENT"] == "NO"
    assert "NOT_PRODUCED_BY_CODE" in _html()


def test_final_answer_not_issued():
    m = _matrix()
    assert m["FINAL_ANSWER_PRODUCED_BY_CODE"] == "NO"
    assert m["FINAL_HUKM_ISSUED"] == "NO"
    assert "FINAL_HUKM_ISSUED = NO" in _html()


def test_no_result_attributed_to_llm():
    t = _html()
    assert "LLM_FREE_TEXT_OUTPUT = NO" in t
    # no phrase attributing an output to an LLM/GPT/model
    assert not re.search(r"(أنتج|قال|يرى)\s*(LLM|GPT|النموذج)", t)


def test_no_demo_language_except_negation():
    t = _html()
    for mobj in re.finditer(r"تمثيلي\S*", t):
        seg = t[max(0, mobj.start() - 8):mobj.start()]
        assert "ليس" in seg or "لا " in seg, seg
    for mobj in re.finditer(r"\bdemo\b", t, flags=re.I):
        seg = t[max(0, mobj.start() - 30):mobj.start() + 20]
        assert "ILLUSTRATIVE_DEMO = NO" in seg, seg


def test_scores_and_flags_unchanged():
    m = _matrix()
    assert m["DOCUMENT"] == "80.0"
    assert m["DAL_MADLUL"] == "90.0"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_OPENED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _html())


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
