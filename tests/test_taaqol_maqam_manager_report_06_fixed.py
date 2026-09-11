#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIX_MANAGER_06 (Part A) — fixed round-06 manager report guard test."""
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
FIXED = OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06_FIXED.html"
ORIG = OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06.html"
MATRIX06 = OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06_MATRIX.csv"


def _t():
    assert FIXED.exists()
    return FIXED.read_text(encoding="utf-8")


def test_fixed_report_exists_and_original_preserved():
    assert FIXED.exists() and FIXED.stat().st_size > 1000
    assert ORIG.exists(), "original round-06 report must NOT be deleted"


def test_has_standalone_traceability_table():
    t = _t()
    assert "جدول التتبع: القاعدة ← المصدر ← المنتج ← artifact ← الاختبار" in t
    for req in ("REQ-COREFERENCE", "REQ-ELLIPSIS", "REQ-RANK", "REQ-SPEECH-ACT",
                "REQ-CANONICAL-BLOCKER", "REQ-MAQAM6-RATIFIED", "REQ-REFERENCE-POLICY-RATIFIED",
                "REQ-FACTUAL-CLAIM-BIRTH", "REQ-NORMATIVE-SOURCE-BIRTH"):
        assert req in t, req


def test_no_empty_artifact_or_test_cells_in_traceability():
    # every traceability row must carry an existing artifact + test path (no ASSERTED_NOT_MEASURED)
    t = _t()
    assert "ASSERTED_NOT_MEASURED" not in t
    for art in ("MAQAM_COREFERENCE_GATE_02.json", "NAZILA_MAQAM_CLASSIFICATION_06.json",
                "NAZILA_NORMATIVE_SOURCE_BIRTH_07.json"):
        assert art in t, art
    for test in ("test_taaqol_maqam_deferred_consumers_02.py",
                 "test_taaqol_maqam_source_full_maqam6_reference_ratified_closure_06.py",
                 "test_taaqol_normative_source_birth_07.py"):
        assert test in t, test


def test_t003_display_fix_with_raw_note():
    t = _t()
    assert "ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED" in t
    assert "raw_artifact_madlul_source = APPROVED_MADLUL_SOURCE_MISSING_OWNER_PENDING" in t


def test_t009_artifact_anomaly_tag():
    t = _t()
    assert "FI3L/VERBAL_IMPERFECT (ARTIFACT_ANOMALY)" in t
    assert "artifact not overwritten" in t


def test_round06_verdicts_unchanged():
    m = {r.split(",", 1)[0]: r.split(",", 1)[1]
         for r in MATRIX06.read_text(encoding="utf-8").splitlines() if "," in r}
    assert m["MAQAM_6_OWNER_RATIFIED"] == "YES"
    assert m["FACTUAL_CLAIM_BIRTH_STATUS"] == "BORN_BUT_DEFERRED"
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "UNBORN"
    assert m["NORMATIVE_HUKM_PRODUCED"] == "NO"


def test_no_ruling_and_21_sections():
    t = _t()
    nums = [int(x) for x in re.findall(r"<h2>(\d+)\.", t)]
    assert nums == list(range(1, 22)), nums
    for s in ("NORMATIVE_HUKM_PRODUCED = NO", "MANAT_PRODUCED = NO", "TANZIL_PRODUCED = NO",
              "FINAL_ANSWER_PRODUCED = NO"):
        assert s in t, s


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _t())
