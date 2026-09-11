#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOSE_MANAGER_REPORT_AR_07_WITH_GENERATION_PROOF — closure guard test.

Closes the AR-07 report: an in-report "إثبات سلسلة التوليد" section with the required literal lines,
the tests-section result lines, the corrected binding sentence + distinct binding counts, the
propositional-content wording, and the two review fixes preserved. Also confirms the manager reports 1
and 2 still exist. Artifacts only; no ruling; no score change.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
RM = GEN / "roadmap"
REPORT = RM / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"
REPORT06 = RM / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_06.html"
MATRIX = GEN / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07_CLOSURE_MATRIX.csv"
GENERATOR = pathlib.Path("/Users/husseinhiyassat/hokom/scripts/generate_taaqol_code_executed_manager_report_ar_07.py")
PYTEST_CREATED = pathlib.Path("/Users/husseinhiyassat/hokom/tests/test_taaqol_code_executed_manager_report_ar_07_created.py")
AR07_MATRIX = GEN / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07_MATRIX.csv"
REPORT1 = RM / "TAAQOL_NAZILA_MANAGER_REPORT_1_CODE_OUTPUT_AR_08.html"
REPORT2 = RM / "TAAQOL_NAZILA_MANAGER_REPORT_2_FRACTAL_BIRTH_AR_08.html"


def _t():
    assert REPORT.exists()
    return REPORT.read_text(encoding="utf-8")


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_generation_proof_section_literals():
    t = _t()
    assert "إثبات سلسلة التوليد" in t
    for s in ("REPORT_07_CREATED = YES",
              "GENERATOR_FILE = scripts/generate_taaqol_code_executed_manager_report_ar_07.py",
              "PYTEST_FILE = tests/test_taaqol_code_executed_manager_report_ar_07_created.py",
              "MATRIX_FILE = output/taaqol_nazila_matrix_generated/TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07_MATRIX.csv",
              "BYTE_IDENTICAL_REGENERATION = YES",
              "REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY",
              "ILLUSTRATIVE_DEMO = NO",
              "LLM_FREE_TEXT_OUTPUT = NO"):
        assert s in t, s


def test_tests_section_result_lines():
    t = _t()
    for s in ("PYTEST_RESULT = PASS", "REPORT_REPRODUCIBLE_FROM_GENERATOR = YES",
              "EXTERNAL_REFS = 0", "FINAL_HUKM_ISSUED = NO", "FINAL_ANSWER_ALLOWED = NO",
              "COMMIT = NO", "PROJECT_FINISHED = NO"):
        assert s in t, s


def test_binding_sentence_corrected_and_counts():
    t = _t()
    assert "الكود أنتج الربط المعجمي/الوظيفي لـ 9 كلمات" in t
    assert "ربط النص العربي فعده 0" in t or "ربط النص العربي فعدده 0" in t
    for s in ("LEXICAL_DAL_MADLUL_BINDING_COUNT = 9",
              "ARABIC_TEXT_MADLUL_LICENSED_COUNT = 1",
              "ARABIC_TEXT_MADLUL_BOUND_COUNT = 0",
              "NO_ARABIC_TEXT_BOUND_WITHOUT_RATIFIED_GATE = YES"):
        assert s in t, s


def test_propositional_content_not_born_claim():
    t = _t()
    assert "PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS = YES" in t
    assert "FACTUAL_CLAIM_BIRTH_STATUS = FORBIDDEN_PARENT_DEFERRED" in t
    assert "REASON = MAQAM_CLASSIFICATION_GATE_DECISION_DEFER" in t


def test_review_fixes_preserved():
    t = _t()
    assert "ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED" in t
    assert "ARTIFACT_ANOMALY" in t
    assert _matrix()["ARTIFACT_NEVER_OVERWRITTEN"] == "YES"


def test_h2_still_ten_matching_06():
    ref = re.findall(r"<h2>(.*?)</h2>", REPORT06.read_text(encoding="utf-8"))
    new = re.findall(r"<h2>(.*?)</h2>", _t())
    assert len(ref) == 10 and new == ref


def test_chain_files_present():
    assert GENERATOR.exists() and GENERATOR.stat().st_size > 0
    assert PYTEST_CREATED.exists() and PYTEST_CREATED.stat().st_size > 0
    assert AR07_MATRIX.exists() and AR07_MATRIX.stat().st_size > 0


def test_both_manager_reports_present():
    assert REPORT1.exists() and REPORT1.stat().st_size > 500
    assert REPORT2.exists() and REPORT2.stat().st_size > 500
    assert _matrix()["MANAGER_REPORTS_COUNT"] == "2"


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _t())


def test_closure_matrix_flags():
    m = _matrix()
    assert m["REPORT_07_CLOSURE"] == "PASS"
    assert m["BYTE_IDENTICAL_REGENERATION"] == "YES"
    assert m["H2_ORDER_MATCHES_06"] == "YES"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["FINAL_HUKM_ISSUED"] == "NO" and m["FINAL_ANSWER_ALLOWED"] == "NO"
    assert m["DOCUMENT"] == "80.0" and m["DAL_MADLUL"] == "90.0"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
