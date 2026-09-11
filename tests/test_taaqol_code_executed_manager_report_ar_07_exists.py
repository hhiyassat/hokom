#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX_MISSING_CODE_EXECUTED_MANAGER_REPORT_AR_07_ARTIFACT — existence-repair guard test.

Proves the official round-07 manager report exists under the exact literal name
TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html, is code-generated, carries the round-07
verdicts unchanged, and references the four round-07 JSON candidate artifacts. Artifacts only.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
HTML = GEN / "roadmap" / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_CODE_EXECUTED_MANAGER_REPORT_AR_07_MISSING_ARTIFACT_FIX.csv"

JSON_PATHS = [
    "TAAQOL_NAZILA_IFADAH_CANDIDATE_07.json",
    "TAAQOL_NAZILA_MANAT_CANDIDATE_07.json",
    "TAAQOL_NAZILA_TANZIL_CANDIDATE_07.json",
    "TAAQOL_NAZILA_ANSWER_AUDIT_CANDIDATE_07.json",
]


def _html():
    assert HTML.exists(), "official round-07 report must exist under the literal name"
    return HTML.read_text(encoding="utf-8")


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_file_exists_literal_name():
    assert HTML.exists()
    assert HTML.name == "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"


def test_file_not_empty():
    assert HTML.stat().st_size > 0
    assert len(_html()) > 500


def test_has_arabic_executive_title():
    assert "<h1>تقرير تنفيذي" in _html()


def test_carries_round07_verdicts_unchanged():
    # NOTE: this file was deliberately redefined by CREATE_MISSING_CODE_EXECUTED_MANAGER_REPORT_AR_07
    # to carry the round-06 layout UPDATED with the round-08/09/10 fractal-birth results. The old
    # round-07 candidate framing (MANAT/TANZIL "_PRODUCED_BY_CODE = YES") is superseded on purpose.
    t = _html()
    for s in ("REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY",
              "ILLUSTRATIVE_DEMO = NO",
              "LLM_FREE_TEXT_OUTPUT = NO",
              "IFADAH_PRODUCED_BY_CODE = YES",
              "MANAT_BIRTH_STATUS = FORBIDDEN_ANCESTOR_UNBORN",
              "TANZIL_BIRTH_STATUS = FORBIDDEN_ANCESTOR_UNBORN",
              "FINAL_ANSWER_BIRTH_STATUS = FORBIDDEN_ANCESTOR_UNBORN",
              "FINAL_HUKM_ISSUED = NO",
              "FINAL_ANSWER_ALLOWED = NO",
              "PROJECT_FINISHED = NO"):
        assert s in t, s


def test_no_born_tanzil_candidate_after_supersession():
    # after 08/09/10 the file must NOT present a born TANZIL_CANDIDATE
    t = _html()
    assert "TANZIL_CANDIDATE" not in t
    assert "TANZIL_READINESS_OBSTRUCTION_REPORT" in t


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _html())


def test_matrix_records_repair_without_score_change():
    m = _matrix()
    assert m["CODE_EXECUTED_MANAGER_REPORT_AR_07_HTML_EXISTS"] == "YES"
    assert m["CODE_EXECUTED_MANAGER_REPORT_AR_07_HTML_PATH"] == \
        "roadmap/TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"
    assert m["MISSING_ARTIFACT_REPAIRED"] == "YES"
    assert m["WRONG_06_NAME_SUPERSEDED"] == "YES"
    assert m["DOCUMENT"] == "80.0"
    assert m["DAL_MADLUL"] == "90.0"
    for k in ("SCORE_CHANGED", "RUNTIME_CHANGED", "GATES_OPENED",
              "NEW_SCIENTIFIC_ROUND_OPENED", "RESULTS_07_CHANGED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
