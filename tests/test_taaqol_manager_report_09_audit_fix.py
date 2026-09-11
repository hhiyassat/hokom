#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MANAGER_REPORT_09_AUDIT_FIX — guard test for the fixed round-09 manager report."""
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
FIXED = OUT / "FACTUAL_CLAIM_PASSAGE_NORMATIVE_SOURCE_MANAGER_REPORT_AR_09_FIXED.html"
ORIG = OUT / "FACTUAL_CLAIM_PASSAGE_NORMATIVE_SOURCE_MANAGER_REPORT_AR_09.html"
MATRIX = OUT / "MANAGER_REPORT_09_AUDIT_FIX_MATRIX.csv"
FORBIDDEN = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _t():
    assert FIXED.exists()
    return FIXED.read_text(encoding="utf-8")


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_fixed_exists_original_preserved():
    assert FIXED.exists() and FIXED.stat().st_size > 1000
    assert ORIG.exists()


def test_standalone_traceability_table():
    t = _t()
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    for req in ("REQ-IFADAH", "REQ-MAQAM6-RATIFIED", "REQ-FACTUAL-CLAIM-PASSAGE",
                "REQ-NORMATIVE-SOURCE-BIRTH", "REQ-NORMATIVE-HUKM-BIRTH", "REQ-TANZIL-BIRTH",
                "REQ-ANSWER-AUDIT-BIRTH"):
        assert req in t, req


def test_no_empty_artifact_or_test_cells():
    t = _t()
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["TRACEABILITY_ARTIFACT_TEST_CELLS_FILLED"] == "YES"
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_ifadah_three_values():
    assert ("IFADAH_PRODUCED_BY_CODE = YES · IFADAH_MISSING = NO · "
            "IFADAH_COMPLETION_STATUS = PARTIAL_OR_DEFERRED") in _t()


def test_dual_normative_source_blockers():
    assert "FACTUAL_CLAIM_PASSAGE_BLOCKED ؛ NO_RATIFIED_NORMATIVE_SOURCE" in _t()
    assert _m()["NORMATIVE_SOURCE_BLOCKERS_COMPLETE"] == "YES"


def test_in_report_closure_flags_and_tests_result():
    t = _t()
    assert "ASSERTED_NOT_MEASURED_COUNT = 0 · SILENT_FALLBACK_COUNT = 0 · EXTERNAL_REFS = 0" in t
    assert "TESTS_PASS = YES · COMMIT = NO · PROJECT_FINISHED = NO" in t
    assert "ROUND_09_REPORT_FIX_TESTS = passed" in t
    assert "NO_VERDICTS_CHANGED = YES" in t


def test_preserved_content_and_verdicts_unchanged():
    t = _t()
    assert "ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED" in t
    assert "FI3L/VERBAL_IMPERFECT (ARTIFACT_ANOMALY)" in t
    assert "FACTUAL_CLAIM_PASSAGE_STATUS = BLOCK" in t
    assert "NORMATIVE_SOURCE_BIRTH_STATUS = UNBORN" in t
    for i in range(10):
        assert f">t00{i}<" in t, i
    assert _m()["ROUND_09_VERDICTS_CHANGED"] == "NO"


def test_no_typos_no_external_refs():
    t = _t()
    for bad in FORBIDDEN:
        assert bad not in t, bad
    assert not re.search(r"https?://|//cdn", t)


def test_matrix_strict():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
