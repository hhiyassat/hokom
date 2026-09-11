#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOSE_T003_BINDING_SCORE_B2_R3B_AND_CODE_MANAGER_REPORT_01 — documentary guard test.

Reads the round artifacts (final-closure matrix CSV + HTML view + code-generated manager report)
and asserts the closure guards. It does NOT import runtime, change score/gates, or open anything —
it only verifies the recorded artifacts are consistent and honor the guardrails.
"""
import csv
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_BINDING_SCORE_B2_R3B_FINAL_CLOSURE_01.csv"
VIEW = GEN / "TAAQOL_NAZILA_VIEW_BINDING_SCORE_B2_R3B_FINAL_CLOSURE_01.html"
MANAGER = GEN / "roadmap" / "TAAQOL_NAZILA_MANAGER_REPORT_AR_CODE_GENERATED_01.md"


def _matrix():
    rows = list(csv.reader(MATRIX.open(encoding="utf-8")))
    assert rows[0] == ["field", "value"], "matrix header must be exactly field,value"
    bad = [r for r in rows if len(r) != 2]
    assert not bad, f"matrix must be strict 2-column; offending: {bad}"
    return {r[0]: r[1] for r in rows[1:]}


def test_matrix_strict_field_value():
    assert _matrix()


def test_closure_verdicts():
    m = _matrix()
    assert m["BINDING_STATUS"] == "PENDING_BINDING_GATE"
    assert m["SCORE_STATUS"] == "SCORE_GATE_NOT_PRESENT"
    assert m["B2_STATUS"] == "DEFER_PENDING_DATASET"
    assert m["R3_B_STATUS"] == "DEFER"
    assert m["T003_BOUND_CLAIM"] == "NO"


def test_scores_and_count_unchanged():
    m = _matrix()
    assert m["DOCUMENT"] == "80.0"
    assert m["DAL_MADLUL"] == "90.0"
    assert m["PROJECT_TEXT_LICENSED_MADLUL_COUNT"] == "1"


def test_manager_report_code_generated_exists():
    m = _matrix()
    assert m["MANAGER_REPORT_AR_CODE_GENERATED"] == "YES"
    assert m["MANAGER_REPORT_AR_SOURCE"] == "ARTIFACTS_NOT_LLM_FREE_TEXT"
    assert MANAGER.exists(), "code-generated manager report must exist"


def test_manager_report_has_16_stages():
    txt = MANAGER.read_text(encoding="utf-8")
    stage_rows = [ln for ln in txt.splitlines() if ln.startswith("| المرحلة ")]
    # 16 data rows + 1 header row that also starts with "| المرحلة "
    assert len(stage_rows) == 17, f"expected header+16 stages, got {len(stage_rows)}"


def test_every_not_yet_stage_has_a_reason():
    txt = MANAGER.read_text(encoding="utf-8")
    data_rows = [ln for ln in txt.splitlines()
                 if ln.startswith("| المرحلة ") and "| ماذا تعني" not in ln]
    for ln in data_rows:
        if "NOT_YET" in ln:
            assert "لم تعمل بعد —" in ln, f"NOT_YET stage without reason: {ln}"


def test_no_executive_effect():
    m = _matrix()
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_OPENED", "COMMIT",
              "MANAT_OPENED", "TANZIL_OPENED", "ANSWER_AUDIT_OPENED", "TRANSFER_PERFORMED"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_html_has_no_external_refs():
    html = VIEW.read_text(encoding="utf-8")
    assert not re.search(r"https?://|//cdn", html)
