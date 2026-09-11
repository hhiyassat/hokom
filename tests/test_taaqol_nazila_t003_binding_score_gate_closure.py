#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T003_BINDING_AND_SCORE_GATE_IMMEDIATE_CLOSURE_01 — documentary guard test.

Reads the round artifacts (two-column matrix CSV + HTML view) and asserts the closure guards.
It does NOT import runtime, does NOT change score/gates, and does NOT open anything — it only
verifies that the recorded artifacts are internally consistent and honor the guardrails.
"""
import csv
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_T003_BINDING_AND_SCORE_GATE_CLOSURE_01.csv"
VIEW = GEN / "TAAQOL_NAZILA_VIEW_T003_BINDING_AND_SCORE_GATE_CLOSURE_01.html"

OWNER_TEXT = "الأنثى التي تشارك الشخص في الأبوين أو في أحدهما."


def _matrix():
    rows = list(csv.reader(MATRIX.open(encoding="utf-8")))
    assert rows[0] == ["field", "value"], "matrix header must be exactly field,value"
    # strict two-column
    bad = [r for r in rows if len(r) != 2]
    assert not bad, f"matrix must be strict 2-column; offending rows: {bad}"
    return {r[0]: r[1] for r in rows[1:]}


def test_matrix_strict_field_value():
    m = _matrix()
    assert m  # non-empty


def test_madlul_text_ar_literal_present():
    m = _matrix()
    assert m["madlul_text_ar"] == OWNER_TEXT
    # and the exact text appears in the HTML view too
    assert OWNER_TEXT in VIEW.read_text(encoding="utf-8")


def test_project_text_licensed_madlul_count_is_one():
    assert _matrix()["PROJECT_TEXT_LICENSED_MADLUL_COUNT"] == "1"


def test_binding_gate_search_performed_and_result_valid():
    m = _matrix()
    assert m["BINDING_GATE_SEARCH_PERFORMED"] == "YES"
    assert m["BINDING_RESULT"] in ("BOUND_NAZILA_ONLY", "PENDING_BINDING_GATE")


def test_if_no_binding_gate_then_no_bound_claim():
    m = _matrix()
    if m["BINDING_GATE_FOUND"] == "NO":
        assert m["T003_BOUND_CLAIM"] == "NO"
        html = VIEW.read_text(encoding="utf-8")
        # no positive "t003 ... BOUND" claim (allow "NOT BOUND" / "PENDING_BINDING" / "BINDING")
        bad = [x for x in re.findall(r"t003[^<]*>[^<]*BOUND", html)
               if not re.search(r"NOT BOUND|PENDING|DEFERRED|BINDING_GATE", x)]
        assert not bad, f"unexpected BOUND claim: {bad}"


def test_score_gate_search_performed_and_result_valid():
    m = _matrix()
    assert m["SCORE_GATE_SEARCH_PERFORMED"] == "YES"
    assert m["SCORE_RESULT"] in ("SCORE_CHANGED_BY_RATIFIED_GATE", "SCORE_GATE_NOT_PRESENT")


def test_if_no_score_gate_then_scores_unchanged():
    m = _matrix()
    if m["SCORE_GATE_FOUND"] == "NO":
        assert m["DOCUMENT"] == "80.0"
        assert m["DAL_MADLUL"] == "90.0"
        assert m["SCORE_CHANGED"] == "NO"


def test_no_executive_effect():
    m = _matrix()
    assert m["RUNTIME_CHANGED"] == "NO"
    assert m["GATES_OPENED"] == "NO"
    assert m["TRANSFER_PERFORMED"] == "NO"
    assert m["GLOSS_AR_TRANSFER"] == "0"
    assert m["SENSE_AUDIT_STARTED"] == "0"
    assert m["COMMIT"] == "NO"
    assert m["PROJECT_FINISHED"] == "NO"
    for k in ("B2_OPENED", "R3_B_OPENED", "MANAT_OPENED", "TANZIL_OPENED", "ANSWER_AUDIT_OPENED"):
        assert m[k] == "NO", k


def test_html_has_no_external_refs():
    html = VIEW.read_text(encoding="utf-8")
    assert not re.search(r"https?://|//cdn", html), "HTML view must have no external refs"
