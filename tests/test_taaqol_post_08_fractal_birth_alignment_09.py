#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POST_08_FRACTAL_BIRTH_REVIEW_ALIGNMENT_AND_MANAGER_REPORTS_FIX_09 — alignment guard test.

Proves round-08 output is aligned with FRACTAL_BIRTH_REVIEW: two manager reports exist, the frozen
law holds, the two branches are defined, GateDecision is kept separate from child BirthStatus, the
four-axes+ProducerFile model is present, the maqām inventory excludes the current case (path B), the
reference policy still needs an owner decision, and manāṭ/tanzīl/answer are corrected to
FORBIDDEN_ANCESTOR_UNBORN. Artifacts only; no ruling; no score change.
"""
import json
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
RM = GEN / "roadmap"
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_POST_08_FRACTAL_BIRTH_ALIGNMENT_09.csv"
ALIGN_JSON = GEN / "TAAQOL_NAZILA_FRACTAL_BIRTH_ALIGNMENT_09.json"
REPORT1 = RM / "TAAQOL_NAZILA_MANAGER_REPORT_1_CODE_OUTPUT_AR_08.html"
REPORT2 = RM / "TAAQOL_NAZILA_MANAGER_REPORT_2_FRACTAL_BIRTH_AR_08.html"


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_two_manager_reports_exist_nonempty():
    assert REPORT1.exists() and REPORT1.stat().st_size > 500
    assert REPORT2.exists() and REPORT2.stat().st_size > 500
    assert _matrix()["MANAGER_REPORTS_COUNT"] == "2"


def test_report_titles():
    assert "ما أنتجه الكود فعلًا" in REPORT1.read_text(encoding="utf-8")
    assert "قانون الولادة الفركتالية" in REPORT2.read_text(encoding="utf-8")


def test_frozen_law_and_branches():
    m = _matrix()
    assert m["NO_DESCENDANT_BIRTH_WITHOUT_PARENT_CLOSURE"] == "YES"
    assert m["FACT_BRANCH_DEFINED"] == "YES"
    assert m["NORMATIVE_BRANCH_DEFINED"] == "YES"
    assert m["BRANCHES_MEET_ONLY_AT_TAHQIQ_MANAT_AND_TANZIL"] == "YES"


def test_gate_decision_separated_from_birth_status():
    m = _matrix()
    assert m["GATE_DECISION_NOT_CHILD_BIRTH_STATUS"] == "YES"
    assert m["GATE_EVALUATION"] == "BORN"
    assert m["GATE_DECISION"] == "DEFER"
    assert m["CHILD_CANDIDATE"] == "UNBORN"
    assert m["BIRTH_LICENSE"] == "DENIED_PENDING_EVIDENCE"


def test_four_axes_model_and_producer_file():
    m = _matrix()
    assert m["FOUR_AXES_STATUS_MODEL"] == "YES"
    assert m["PRODUCER_FILE_REQUIRED_FOR_MEASURED_STATE"] == "YES"
    j = json.loads(ALIGN_JSON.read_text(encoding="utf-8"))
    for a in j["axes"]:
        for k in ("ImplementationStatus", "BirthStatus", "GateDecision", "ClosureStatus", "ProducerFile"):
            assert k in a, (a["layer"], k)
        # a state with a producer file must be MEASURED; without => ASSERTED_NOT_MEASURED
        assert a["measured"] == ("MEASURED" if a["ProducerFile"] else "ASSERTED_NOT_MEASURED")


def test_maqam_inventory_decision_path_b():
    m = _matrix()
    assert m["MAQAM_INVENTORY_EXCLUDES_CURRENT_CASE"] == "YES"
    assert m["CURRENT_NAZILA_MAQAM_FITS_INVENTORY"] == "NO"
    assert m["MAQAM_6_OWNER_RATIFIED"] == "NO"
    assert m["MAQAM_CLASSIFICATION_GATE_DECISION"] == "DEFER"
    assert m["FACTUAL_CLAIM_BIRTH_STATUS"] == "FORBIDDEN_PARENT_DEFERRED"


def test_reference_policy_decision_required():
    assert _matrix()["REFERENCE_POLICY_DECISION_REQUIRED"] == "YES"


def test_manat_tanzil_answer_corrected_to_forbidden():
    m = _matrix()
    assert m["MANAT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["TANZIL_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["ANSWER_AUDIT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["FINAL_ANSWER_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    # no born tanzil while ancestor unborn -> the 07 tanzil json is reconceptualized, not born
    assert m["TANZIL_07_JSON_RECONCEPTUALIZED_AS"] == "TANZIL_READINESS_OBSTRUCTION_REPORT"


def test_no_born_tanzil_when_factual_claim_unborn():
    j = json.loads(ALIGN_JSON.read_text(encoding="utf-8"))
    fc = next(a for a in j["axes"] if a["layer"] == "FACTUAL_CLAIM")
    tz = next(a for a in j["axes"] if a["layer"] == "TANZIL")
    assert fc["BirthStatus"] == "IMPLEMENTED_BUT_UNBORN"
    assert tz["BirthStatus"] == "FORBIDDEN_ANCESTOR_UNBORN"


def test_verdicts_and_flags_unchanged():
    m = _matrix()
    assert m["FINAL_HUKM_ISSUED"] == "NO"
    assert m["FINAL_ANSWER_ALLOWED"] == "NO"
    assert m["REPORT_SOURCE"] == "CODE_AND_ARTIFACTS_ONLY"
    assert m["LLM_FREE_TEXT_OUTPUT"] == "NO"
    assert m["ILLUSTRATIVE_DEMO"] == "NO"
    assert m["DOCUMENT"] == "80.0"
    assert m["DAL_MADLUL"] == "90.0"
    for k in ("SCORE_CHANGED", "RUNTIME_CHANGED", "GATES_OPENED", "EIGHT_REBUILT", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_no_external_refs_reports():
    for p in (REPORT1, REPORT2):
        assert not re.search(r"https?://|//cdn", p.read_text(encoding="utf-8")), p.name


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
