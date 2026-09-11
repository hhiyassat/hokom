#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSERT_PROPOSITION_MAQAM_CLAIM_LAYER_BEFORE_NORMATIVE_HUKM_08 — documentary + kernel guard test.

Proves: the fractal-birth kernel enforces NoDescendantBirthWithoutParentClosure; with the maqam
DEFERRED, the factual claim, normative ḥukm, manāṭ, tanzīl and final answer are NOT born; two
code-generated Arabic manager reports exist; nothing is authored; no ruling; no score change.
"""
import json
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path("/Users/husseinhiyassat/hokom/scripts")))
import taaqol_fractal_birth_kernel as K  # noqa: E402

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
RM = GEN / "roadmap"
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_PROPOSITION_MAQAM_CLAIM_08.csv"
REPORT1 = RM / "TAAQOL_NAZILA_MANAGER_REPORT_1_CODE_OUTPUT_AR_08.html"
REPORT2 = RM / "TAAQOL_NAZILA_MANAGER_REPORT_2_FRACTAL_BIRTH_AR_08.html"
JSONS = {
    "prop": GEN / "PROPOSITIONAL_CONTENT_CANDIDATE_08.json",
    "maqam": GEN / "MAQAM_CLASSIFICATION_08.json",
    "factual": GEN / "FACTUAL_CLAIM_CANDIDATE_08.json",
    "normhukm": GEN / "NORMATIVE_HUKM_BIRTH_08.json",
}
CHAIN = "IFADAH → PROPOSITIONAL_CONTENT → MAQAM_CLASSIFICATION → FACTUAL_CLAIM → NORMATIVE_HUKM_BIRTH"


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


# ---- kernel law ----
def test_kernel_has_four_states_and_law():
    assert K.BIRTH_STATES == ("UNIMPLEMENTED", "IMPLEMENTED_BUT_UNBORN",
                              "BORN_BUT_DEFERRED", "CERTIFIED")
    assert K.LAW_NAME == "NoDescendantBirthWithoutParentClosure"


def test_law_forbids_birth_without_parent_closure():
    assert K.no_descendant_birth_without_parent_closure(K.CERTIFIED) == K.BIRTH_ALLOWED
    assert K.no_descendant_birth_without_parent_closure(K.BORN_BUT_DEFERRED) == K.FORBIDDEN_PARENT_DEFERRED
    assert K.no_descendant_birth_without_parent_closure(K.IMPLEMENTED_BUT_UNBORN) == K.FORBIDDEN_ANCESTOR_UNBORN
    assert K.no_descendant_birth_without_parent_closure(K.UNIMPLEMENTED) == K.FORBIDDEN_ANCESTOR_UNBORN


# ---- the nazila chain: descendants must not be born ----
def test_maqam_deferred_and_not_authored():
    m = _matrix()
    assert m["MAQAM_CLASSIFICATION"] == "DEFER"
    assert m["MAQAM_CHOSEN"] == "NONE_NOT_AUTHORED"
    assert m["MAQAM_AUTHORED_BY_AGENT"] == "NO"
    j = json.loads(JSONS["maqam"].read_text(encoding="utf-8"))
    assert j["authored_by_agent"] == "NO"
    assert j["ratified_maqam_rule"] == "UNIMPLEMENTED"


def test_factual_claim_not_born():
    m = _matrix()
    assert m["FACTUAL_CLAIM_BIRTH"] == "FORBIDDEN_PARENT_DEFERRED"
    j = json.loads(JSONS["factual"].read_text(encoding="utf-8"))
    assert j["birth_state"] == "IMPLEMENTED_BUT_UNBORN"
    assert j["claim_text"] == "NOT_BORN_NOT_AUTHORED"


def test_manat_tanzil_answer_not_born_when_ancestor_unborn():
    m = _matrix()
    assert m["NORMATIVE_HUKM_BIRTH"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["MANAT_BIRTH"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["TANZIL_BIRTH"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["FINAL_ANSWER"] == "FORBIDDEN_ANCESTOR_UNBORN"


def test_no_final_ruling():
    m = _matrix()
    assert m["FINAL_HUKM_ISSUED"] == "NO"
    assert m["FINAL_ANSWER_ALLOWED"] == "NO"


# ---- two manager reports ----
def test_report1_exists_nonempty_and_code_output():
    assert REPORT1.exists() and REPORT1.stat().st_size > 500
    t = REPORT1.read_text(encoding="utf-8")
    assert "ما أنتجه الكود فعلًا" in t
    assert "REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY" in t or "REPORT_1_SOURCE = CODE_AND_ARTIFACTS_ONLY" in t
    assert "LLM_FREE_TEXT_OUTPUT = NO" in t and "ILLUSTRATIVE_DEMO = NO" in t
    assert "FINAL_HUKM_ISSUED = NO" in t


def test_report2_exists_nonempty_and_fractal_law():
    assert REPORT2.exists() and REPORT2.stat().st_size > 500
    t = REPORT2.read_text(encoding="utf-8")
    assert "قانون الولادة الفركتالية" in t
    assert CHAIN in t
    assert "NoDescendantBirthWithoutParentClosure" in t
    for st in ("UNIMPLEMENTED", "IMPLEMENTED_BUT_UNBORN", "BORN_BUT_DEFERRED", "CERTIFIED"):
        assert st in t, st
    assert "LLM_FREE_TEXT_OUTPUT = NO" in t and "ILLUSTRATIVE_DEMO = NO" in t


def test_matrix_two_reports_indicators():
    m = _matrix()
    assert m["MANAGER_REPORT_1_CREATED"] == "YES"
    assert m["MANAGER_REPORT_1_PATH"] == "roadmap/TAAQOL_NAZILA_MANAGER_REPORT_1_CODE_OUTPUT_AR_08.html"
    assert m["MANAGER_REPORT_2_CREATED"] == "YES"
    assert m["MANAGER_REPORT_2_PATH"] == "roadmap/TAAQOL_NAZILA_MANAGER_REPORT_2_FRACTAL_BIRTH_AR_08.html"
    assert m["MANAGER_REPORTS_COUNT"] == "2"
    assert m["MANAGER_REPORTS_ARE_CODE_GENERATED"] == "YES"
    assert m["REPORT_1_SOURCE"] == "CODE_AND_ARTIFACTS_ONLY"
    assert m["REPORT_2_SOURCE"] == "CODE_AND_ARTIFACTS_ONLY"


def test_scores_unchanged_and_flags():
    m = _matrix()
    assert m["DOCUMENT"] == "80.0"
    assert m["DAL_MADLUL"] == "90.0"
    for k in ("SCORE_CHANGED", "RUNTIME_CHANGED", "GATES_OPENED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_all_four_json_valid_not_authored():
    for name, p in JSONS.items():
        assert p.exists(), name
        obj = json.loads(p.read_text(encoding="utf-8"))
        assert obj.get("authored_by_agent") == "NO", name


def test_no_external_refs_both_reports():
    for p in (REPORT1, REPORT2):
        assert not re.search(r"https?://|//cdn", p.read_text(encoding="utf-8")), p.name


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
