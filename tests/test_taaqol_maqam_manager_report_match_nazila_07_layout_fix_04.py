#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_MANAGER_REPORT_MATCH_NAZILA_07_LAYOUT_FIX_04 — layout-match guard test.

The round-03 maqām manager report is re-issued (as report 04) in the nazila-07 layout: correct h1,
14 ordered h2 sections, a stage table, a traceability table, a generation-chain block, y/n/d/note/foot/
wrap CSS, no FULL_PDF_PRESERVED claim (no full PDF), no ruling, external refs = 0, strict matrix.
Artifacts only.
"""
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REPORT = OUT / "MAQAM_SOURCE_2_FULL_PRESERVATION_MANAGER_REPORT_AR_04.html"
MATRIX = OUT / "MAQAM_MANAGER_REPORT_MATCH_NAZILA_07_LAYOUT_FIX_04_MATRIX.csv"


def _t():
    assert REPORT.exists()
    return REPORT.read_text(encoding="utf-8")


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_report_exists_nonempty():
    assert REPORT.exists() and REPORT.stat().st_size > 800


def test_h1_and_rtl_and_notes():
    t = _t()
    assert '<html lang="ar" dir="rtl">' in t
    assert "<h1>تقرير تنفيذي — إغلاق مصدر المقام الثاني وتتبّعه للمدير (04)</h1>" in t
    assert "MANAGER_REPORT_LAYOUT_REFERENCE = TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html" in t
    assert "إغلاق إداري مطلوب للمدير" in t


def test_14_h2_sections_in_order():
    nums = [int(x) for x in re.findall(r"<h2>(\d+)\.", _t())]
    assert nums == list(range(1, 15)), nums


def test_css_classes_present():
    t = _t()
    for c in ("td.y", "td.n", "td.d", ".note", ".foot", ".wrap"):
        assert c in t, c


def test_stage_table_present():
    t = _t()
    assert "أنتجها الكود؟" in t
    for row in ("SOURCE_2_PRESERVATION", "COREFERENCE_GATE", "ELLIPSIS_GATE", "RANK_GATE",
                "SPEECH_ACT_GATE", "CANONICAL_INTEGRATION", "NORMATIVE_OUTPUTS"):
        assert row in t, row


def test_traceability_table_present():
    t = _t()
    assert "requirement" in t and "producer_file" in t
    for req in ("REQ-COREFERENCE", "REQ-ELLIPSIS", "REQ-RANK", "REQ-SPEECH-ACT", "REQ-CANONICAL-BLOCKER"):
        assert req in t, req


def test_generation_chain_block():
    t = _t()
    for s in ("REPORT_04_CREATED = YES", "GENERATOR_FILE =", "PYTEST_FILE =", "MATRIX_FILE =",
              "AUDIT_JSON_FILE =", "SOURCE_MANIFEST_FILE = docs/MAQAM_THEORY_SOURCE_2_MANIFEST.json",
              "TRACEABILITY_FILE = docs/MAQAM_REQUIREMENTS_TRACEABILITY.csv",
              "REPORT_REPRODUCIBLE_FROM_GENERATOR = YES"):
        assert s in t, s


def test_no_full_pdf_claim_when_absent():
    m = _matrix()
    assert m["SOURCE_2_FULL_PDF_AVAILABLE"] == "NO"
    assert "FULL_PDF_PRESERVED" not in _t()


def test_no_ruling_or_final_answer():
    t = _t()
    assert "NORMATIVE_HUKM_PRODUCED = NO" in t
    assert "MANAT_PRODUCED = NO" in t
    assert "TANZIL_PRODUCED = NO" in t
    assert "FINAL_ANSWER_PRODUCED = NO" in t


def test_canonical_blocked_and_gates_status():
    t = _t()
    assert "CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE" in t
    assert "TEXT_ALONE_INFERS_ISTIFTA = NO" in t
    assert "EXAMPLE_CONTEXT_OWNER_RATIFICATION = NO" in t
    assert "NONE_NOT_AUTHORED" in t


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _t())


def test_matrix_flags():
    m = _matrix()
    assert m["MANAGER_REPORT_MATCHES_NAZILA_07_STYLE"] == "YES"
    assert m["MANAGER_REPORT_HAS_14_SECTIONS"] == "YES"
    assert m["MANAGER_REPORT_HAS_STAGE_TABLE"] == "YES"
    assert m["MANAGER_REPORT_HAS_TRACEABILITY_TABLE"] == "YES"
    assert m["MANAGER_REPORT_HAS_GENERATION_CHAIN"] == "YES"
    assert m["ASSERTED_NOT_MEASURED_COUNT"] == "0"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
