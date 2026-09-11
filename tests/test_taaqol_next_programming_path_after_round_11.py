#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UPDATE_NEXT_PROGRAMMING_PATH_AFTER_ROUND_11 — documentation-order guard test.

Verifies the corrected "ما يلزم برمجته بعد ذلك" ordering (1..8) in the round-11 manager report and the
next-path matrix, that no descendant precedes its parent, and that round-11 verdicts are untouched.
Artifacts only; no score/gate/runtime change.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
RM = GEN / "roadmap"
MANAGER = RM / "TAAQOL_NAZILA_FACT_TO_NORMATIVE_BIRTH_MANAGER_REPORT_AR_11.html"
TECH = RM / "TAAQOL_NAZILA_FACT_TO_NORMATIVE_BIRTH_CLOSURE_11_REPORT.md"
MATRIX = GEN / "TAAQOL_NAZILA_NEXT_PROGRAMMING_PATH_AFTER_ROUND_11_MATRIX.csv"
CLOSURE_MATRIX = GEN / "TAAQOL_NAZILA_FACT_TO_NORMATIVE_BIRTH_CLOSURE_11_MATRIX.csv"

EXPECTED_STEPS = [
    "MAQAM_CLASSIFICATION_OWNER_RATIFICATION",
    "REFERENCE_POLICY_DECISION",
    "FACTUAL_CLAIM_BIRTH",
    "NORMATIVE_SOURCE_BIRTH",
    "NORMATIVE_HUKM_BIRTH",
    "ILLAH_MANAT",
    "TANZIL",
    "ANSWER_AUDIT",
]


def _matrix(p):
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in p.read_text(encoding="utf-8").splitlines() if "," in r}


def test_matrix_step_order_1_to_8():
    m = _matrix(MATRIX)
    for i, step in enumerate(EXPECTED_STEPS, start=1):
        assert m[f"NEXT_PATH_STEP_{i}"] == step, i


def test_manager_section_present_and_ordered():
    t = MANAGER.read_text(encoding="utf-8")
    assert "ما يلزم برمجته بعد ذلك" in t
    # restrict to the ordered <ol> block so the explanatory note above it does not skew positions
    ol = t[t.rindex("<ol>"):t.rindex("</ol>")]
    markers = ["MAQAM_6 = MASALA_MUSAWWARA_LIL_ISTIFTA", "ASSUMED_FACT_REFERENCE = HYPOTHETICAL_MARKED_REFERENCE",
               "factual_claim_birth", "normative_source_birth", "normative_hukm_birth",
               "illah / manat", "tanzil", "answer_audit"]
    positions = [ol.find(mk) for mk in markers]
    assert all(p != -1 for p in positions), positions
    assert positions == sorted(positions), positions


def test_ordering_flags():
    m = _matrix(MATRIX)
    for k in ("MAQAM_FIRST", "REFERENCE_POLICY_SECOND",
              "FACTUAL_CLAIM_AFTER_MAQAM_AND_REFERENCE",
              "NORMATIVE_SOURCE_AFTER_FACTUAL_CLAIM",
              "NORMATIVE_HUKM_AFTER_NORMATIVE_SOURCE",
              "MANAT_AFTER_NORMATIVE_HUKM", "TANZIL_AFTER_MANAT",
              "ANSWER_AUDIT_AFTER_TANZIL"):
        assert m[k] == "YES", k


def test_nothing_ratified_or_generated_this_round():
    m = _matrix(MATRIX)
    assert m["MAQAM_6_OWNER_RATIFIED"] == "NO"
    assert m["MAQAM_6_MADE_RATIFIED_THIS_ROUND"] == "NO"
    assert m["REFERENCE_POLICY_DECISION_REQUIRED"] == "YES"
    assert m["ASSUMED_FACT_REFERENCE_MADE_RATIFIED_THIS_ROUND"] == "NO"
    for k in ("FACTUAL_CLAIM_GENERATED_THIS_ROUND", "NORMATIVE_SOURCE_GENERATED_THIS_ROUND",
              "NORMATIVE_HUKM_GENERATED_THIS_ROUND", "MANAT_TANZIL_ANSWER_GENERATED_THIS_ROUND"):
        assert m[k] == "NO", k


def test_round_11_verdicts_unchanged():
    m = _matrix(MATRIX)
    assert m["ROUND_11_VERDICTS_CHANGED"] == "NO"
    # cross-check the round-11 closure matrix still carries the same verdicts
    c = _matrix(CLOSURE_MATRIX)
    assert c["MAQAM_6_OWNER_RATIFIED"] == "NO"
    assert c["FACTUAL_CLAIM_BIRTH_STATUS"] == "FORBIDDEN_PARENT_DEFERRED"
    assert c["MANAT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert c["FINAL_HUKM_ISSUED"] == "NO"


def test_no_change_flags():
    m = _matrix(MATRIX)
    assert m["FINAL_HUKM_ISSUED"] == "NO"
    assert m["FINAL_ANSWER_ALLOWED"] == "NO"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_tech_report_has_ordered_section():
    t = TECH.read_text(encoding="utf-8")
    assert "ما يلزم برمجته بعد ذلك" in t
    for mk in ("factual_claim_birth", "normative_source_birth", "normative_hukm_birth",
               "tanzil", "answer_audit"):
        assert mk in t, mk


def test_manager_no_external_refs():
    assert not re.search(r"https?://|//cdn", MANAGER.read_text(encoding="utf-8"))


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
