#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NORMATIVE_SOURCE_BIRTH_07_MANAGER_TYPO_AND_CANONICAL_LABEL_FIX — typo guard.

Fails if a known typo ever appears in any round-06/07 manager report or matrix, and asserts the
correct literal labels are present. No verdict change; documentary guard only.
"""
import pathlib

OUT = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_maqam_foundation_generated")

BAD = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT",
       "BINDING_GSTE", "IMPERFPECT", "RATIFISD"]
CORRECT_BINDING = "ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED"
CORRECT_VERBAL = "FI3L/VERBAL_IMPERFECT"

# every round-06/07 report + matrix produced in this maqam path
TARGETS = [
    "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06.html",
    "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06_FIXED.html",
    "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06_MATRIX.csv",
    "NORMATIVE_SOURCE_BIRTH_MANAGER_REPORT_AR_07.html",
    "NORMATIVE_SOURCE_BIRTH_07_MATRIX.csv",
]


def _existing():
    return [OUT / t for t in TARGETS if (OUT / t).exists()]


def test_targets_exist():
    assert len(_existing()) == len(TARGETS), "all round-06/07 reports+matrices must exist"


def test_no_typo_in_any_report_or_matrix():
    for p in _existing():
        text = p.read_text(encoding="utf-8")
        for bad in BAD:
            assert bad not in text, f"typo '{bad}' found in {p.name}"


def test_correct_binding_label_present_in_fixed06():
    fixed = OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06_FIXED.html"
    t = fixed.read_text(encoding="utf-8")
    assert CORRECT_BINDING in t
    assert CORRECT_VERBAL in t
    assert (CORRECT_VERBAL + " (ARTIFACT_ANOMALY)") in t


def test_round06_07_verdicts_unchanged():
    m6 = {r.split(",", 1)[0]: r.split(",", 1)[1]
          for r in (OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06_MATRIX.csv").read_text(encoding="utf-8").splitlines() if "," in r}
    m7 = {r.split(",", 1)[0]: r.split(",", 1)[1]
          for r in (OUT / "NORMATIVE_SOURCE_BIRTH_07_MATRIX.csv").read_text(encoding="utf-8").splitlines() if "," in r}
    assert m6["MAQAM_6_OWNER_RATIFIED"] == "YES"
    assert m6["FACTUAL_CLAIM_BIRTH_STATUS"] == "BORN_BUT_DEFERRED"
    assert m7["NORMATIVE_SOURCE_BIRTH_STATUS"] == "UNBORN"
    for k in ("NORMATIVE_HUKM_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m7[k] == "NO", k
