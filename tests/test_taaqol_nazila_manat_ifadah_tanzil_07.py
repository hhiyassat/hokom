#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUILD_NAZILA_ONLY_CODE_PRODUCED_MANAT_IFADAH_TANZIL_07 — documentary guard test.

Verifies the code-built nazila candidates: ifādah/manāṭ/tanzīl candidates + answer-audit are
produced by code from artifacts (not authored), lexical binding (9) is separated from Arabic-text
binding (1 licensed / 0 bound), no final ruling is issued, and all four JSON artifacts are valid.
Reads artifacts only; no runtime, no gate, no score change.
"""
import json
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
HTML = GEN / "roadmap" / "TAAQOL_NAZILA_EXECUTIVE_MANAGER_MANAT_IFADAH_TANZIL_AR_07.html"
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_MANAT_IFADAH_TANZIL_07.csv"
JSONS = {
    "ifadah": GEN / "TAAQOL_NAZILA_IFADAH_CANDIDATE_07.json",
    "manat": GEN / "TAAQOL_NAZILA_MANAT_CANDIDATE_07.json",
    "tanzil": GEN / "TAAQOL_NAZILA_TANZIL_CANDIDATE_07.json",
    "answer": GEN / "TAAQOL_NAZILA_ANSWER_AUDIT_CANDIDATE_07.json",
}
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."
WORDS = ["مَاتَ", "مَلِكٌ", "عَنْ", "أُخْتٍ", "سَاكِنَةٍ", "مَعَهُ",
         "فَأَرَادَ", "وَارِثُهُ", "طَرْدَهَا", "فَتَحَاكَمَا"]


def _html():
    assert HTML.exists()
    return HTML.read_text(encoding="utf-8")


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_mode_flags():
    m = _matrix()
    assert m["CODE_EXECUTED_OUTPUT"] == "YES"
    assert m["ILLUSTRATIVE_DEMO"] == "NO"
    assert m["LLM_FREE_TEXT_OUTPUT"] == "NO"
    assert m["REPORT_SOURCE"] == "CODE_AND_ARTIFACTS_ONLY"
    assert m["PROJECT_CANONICAL_CLOSURE"] == "NO"


def test_ten_words_present():
    t = _html()
    for w in WORDS:
        assert w in t, w
    mo = re.search(r'<div class="sent" id="nazila-sentence">(.*?)</div>', t, flags=re.S)
    assert mo and mo.group(1) == SENTENCE


def test_binding_separation():
    m = _matrix()
    assert m["TOKENS_WITH_MADLUL_RECORD"] == "10"
    assert m["LEXICAL_DAL_MADLUL_BINDING_COUNT"] == "9"
    assert m["ARABIC_TEXT_MADLUL_LICENSED_COUNT"] == "1"
    assert m["ARABIC_TEXT_MADLUL_BOUND_COUNT"] == "0"
    assert m["NO_ARABIC_TEXT_BOUND_WITHOUT_RATIFIED_GATE"] == "YES"


def test_ifadah_candidate():
    m = _matrix()
    assert m["IFADAH_PRODUCED_BY_CODE"] == "YES"
    assert m["IFADAH_KIND"] == "NAZILA_IFADAH_CANDIDATE"
    assert m["IFADAH_CANONICAL_PROVEN"] == "NO"
    assert m["REFERENCE_RESOLUTION_STATUS"] == "DEFERRED_NO_RATIFIED_COREFERENCE_GATE"
    j = json.loads(JSONS["ifadah"].read_text(encoding="utf-8"))
    assert j["ifadah_kind"] == "NAZILA_IFADAH_CANDIDATE"
    assert j["authored_by_agent"] == "NO"
    assert len(j["slots"]) >= 8


def test_manat_candidate():
    m = _matrix()
    assert m["MANAT_PRODUCED_BY_CODE"] == "YES"
    assert m["MANAT_KIND"] == "NAZILA_MANAT_CANDIDATE"
    assert m["MANAT_NORMATIVE_ILLAH_PROVEN"] == "NO"
    assert m["MANAT_VERDICT"] == "DEFER"
    assert m["MANAT_PREVENTER"] == "NO_RATIFIED_NORMATIVE_ILLAH_RULE"
    j = json.loads(JSONS["manat"].read_text(encoding="utf-8"))
    assert j["authored_by_agent"] == "NO"
    assert "النقص_الحاكم" in j["extracted_elements"]


def test_tanzil_candidate():
    m = _matrix()
    assert m["TANZIL_PRODUCED_BY_CODE"] == "YES"
    assert m["TANZIL_KIND"] == "NAZILA_TANZIL_CANDIDATE"
    assert m["TANZIL_CANONICAL_PROVEN"] == "NO"
    assert m["TANZIL_FINAL_HUKM_ALLOWED"] == "NO"
    j = json.loads(JSONS["tanzil"].read_text(encoding="utf-8"))
    assert j["tanzil_final_hukm_allowed"] == "NO"
    assert j["missing_normative_rule"] == "NO_RATIFIED_NORMATIVE_ILLAH_RULE"
    assert j["authored_by_agent"] == "NO"


def test_answer_audit_candidate():
    m = _matrix()
    assert m["ANSWER_AUDIT_PRODUCED_BY_CODE"] == "YES"
    assert m["ANSWER_AUDIT_KIND"] == "FINAL_ANSWER_ELIGIBILITY_CHECK"
    assert m["FINAL_HUKM_ISSUED"] == "NO"
    assert m["FINAL_ANSWER_ALLOWED"] == "NO"
    assert m["FINAL_ANSWER_PREVENTER"] == "NO_RATIFIED_TANZIL_AND_NORMATIVE_HUKM_GATE"


def test_no_final_ruling_and_no_llm_attribution():
    t = _html()
    assert "FINAL_HUKM_ISSUED = NO" in t
    assert "FINAL_ANSWER_ALLOWED = NO" in t
    assert not re.search(r"(أنتج|قال|يرى|بحسب)\s*(LLM|GPT|النموذج)", t)


def test_no_demo_language_except_negation():
    t = _html()
    for mobj in re.finditer(r"تمثيلي\S*", t):
        seg = t[max(0, mobj.start() - 8):mobj.start()]
        assert "ليس" in seg or "لا " in seg, seg


def test_scores_unchanged():
    m = _matrix()
    assert m["DOCUMENT"] == "80.0"
    assert m["DAL_MADLUL"] == "90.0"
    for k in ("SCORE_CHANGED", "RUNTIME_CHANGED", "GATES_OPENED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_all_json_valid_and_present():
    for name, p in JSONS.items():
        assert p.exists(), name
        obj = json.loads(p.read_text(encoding="utf-8"))
        assert isinstance(obj, dict) and obj.get("authored_by_agent") == "NO", name


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _html())


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
