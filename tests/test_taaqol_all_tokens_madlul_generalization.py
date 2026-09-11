#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERALIZE_T003_MADLUL_TREATMENT_TO_ALL_NAZILA_TOKENS_05 — documentary guard test.

Proves the manager report generalizes the madlul contract to ALL ten nazila tokens:
every token gets a madlul record with the same structure; only license completeness
differs; t003 is NOT a special case; no token is BOUND; scores unchanged. Artifacts only.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
HTML = GEN / "roadmap" / "TAAQOL_NAZILA_COMPREHENSIVE_MANAGER_REPORT_AR_CODE_GENERATED_05.html"
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_ALL_TOKENS_MADLUL_GENERALIZATION_05.csv"

WORDS = ["مَاتَ", "مَلِكٌ", "عَنْ", "أُخْتٍ", "سَاكِنَةٍ", "مَعَهُ",
         "فَأَرَادَ", "وَارِثُهُ", "طَرْدَهَا", "فَتَحَاكَمَا"]
TOKENS = [f"t00{i}" for i in range(10)]


def _html():
    assert HTML.exists(), "v05 report must exist"
    return HTML.read_text(encoding="utf-8")


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_report_exists_and_is_artifact_generated():
    assert "REPORT_SOURCE = ARTIFACTS_NOT_LLM_FREE_TEXT" in _html()


def test_general_indicators():
    t = _html()
    for kv in (("TOTAL_NAZILA_TOKENS", "10"),
               ("TOKENS_WITH_MADLUL_RECORD", "10"),
               ("TOKENS_WITH_LICENSED_MADLUL_TEXT", "1"),
               ("TOKENS_WAITING_FOR_LICENSED_MADLUL_TEXT", "9"),
               ("TOKENS_BOUND", "0"),
               ("NO_TOKEN_BOUND_WITHOUT_RATIFIED_GATE", "YES"),
               ("GENERAL_MADLUL_TREATMENT_APPLIED_TO_ALL_TOKENS", "YES"),
               ("T003_IS_NOT_SPECIAL_CASE", "YES")):
        assert kv[0] in t, kv[0]
    m = _matrix()
    assert m["TOTAL_NAZILA_TOKENS"] == "10"
    assert m["TOKENS_WITH_MADLUL_RECORD"] == "10"
    assert m["TOKENS_WITH_LICENSED_MADLUL_TEXT"] == "1"
    assert m["TOKENS_WAITING_FOR_LICENSED_MADLUL_TEXT"] == "9"
    assert m["TOKENS_BOUND"] == "0"


def test_all_ten_words_in_madlul_layer():
    t = _html()
    assert "حالة كلمات النازلة في طبقة المدلول" in t
    for w in WORDS:
        assert w in t, w


def test_each_token_has_independent_verdict():
    m = _matrix()
    verdicts = {}
    for tok in TOKENS:
        row = m[f"TOKEN_{tok}_MADLUL"]
        mv = re.search(r"verdict=([A-Z_]+)", row)
        assert mv, tok
        verdicts[tok] = mv.group(1)
    # 1 licensed-text token pending binding, 9 deferred — each row carries its own verdict
    assert verdicts["t003"] == "PENDING_BINDING_GATE"
    assert sum(1 for v in verdicts.values() if v == "DEFER") == 9


def test_t003_is_not_a_special_case_heading():
    t = _html()
    headings = re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", t, flags=re.S)
    assert not any("t003" in h or "حالة t003" in h for h in headings), headings
    assert "حالة t003" not in t


def test_ukht_is_an_ordinary_row():
    # أُخْتٍ appears as a normal token row (a <th> cell) among the ten words
    t = _html()
    assert "<th>أُخْتٍ</th>" in t


def test_no_token_bound():
    t = _html()
    # only allowed BOUND occurrences: the constraint negation and the footer flag
    for x in re.findall(r"[^\s>]*BOUND[^<]*", t):
        assert ("إلا ببوابة" in x or "no token BOUND" in x or x.rstrip(".") == "BOUND"
                or x.startswith("TOKENS_BOUND") or x.startswith("NO_TOKEN_BOUND")), x
    assert _matrix()["TOKENS_BOUND"] == "0"


def test_no_agent_authored_meaning_for_the_nine():
    # the nine waiting tokens must show the waiting status, never an authored text
    m = _matrix()
    assert m["MADLUL_TEXT_AUTHORED_BY_AGENT"] == "NO"
    assert "WAITING_FOR_LICENSED_SOURCE_OR_OWNER_TEXT" in _html()


def test_scores_and_flags_unchanged():
    t = _html()
    assert "DOCUMENT = 80.0" in t and "DAL_MADLUL = 90.0" in t
    for kv in ("RUNTIME_CHANGED = NO", "SCORE_CHANGED = NO",
               "GATES_OPENED = NO", "TRANSFER_PERFORMED = NO", "COMMIT = NO"):
        assert kv in t, kv
    assert "PROJECT_FINISHED = NO" in t


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _html())


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
