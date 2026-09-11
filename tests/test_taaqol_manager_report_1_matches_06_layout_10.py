#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX_MANAGER_REPORT_1_TO_MATCH_CODE_EXECUTED_REPORT_06_LAYOUT_10 — layout+content guard test.

Proves manager report 1 mirrors the round-06 CODE_EXECUTED report's ten section headings (same order),
updated with the 08/09 fractal-birth corrections: manāṭ/tanzīl/answer are shown as forbidden-birth
(not born candidates), the maqām is out of inventory (path B), the reference policy still needs a
decision, and no final ruling is issued. Artifacts only; no score change.
"""
import re
import json
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
RM = GEN / "roadmap"
REPORT1 = RM / "TAAQOL_NAZILA_MANAGER_REPORT_1_CODE_OUTPUT_AR_08.html"
REPORT06 = RM / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_06.html"
MATRIX = GEN / "TAAQOL_NAZILA_TWO_COLUMN_MATRIX_MANAGER_REPORT_1_MATCH_06_LAYOUT_10.csv"
MATCH_JSON = GEN / "TAAQOL_NAZILA_MANAGER_REPORT_1_MATCH_06_LAYOUT_10.json"

SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."


def _t():
    assert REPORT1.exists()
    return REPORT1.read_text(encoding="utf-8")


def _h2(text):
    return re.findall(r"<h2>(.*?)</h2>", text)


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_report1_exists_nonempty():
    assert REPORT1.exists() and REPORT1.stat().st_size > 500


def test_ten_headings_match_06_in_order():
    assert REPORT06.exists(), "reference report 06 must exist"
    ref = _h2(REPORT06.read_text(encoding="utf-8"))
    r1 = _h2(_t())
    assert len(ref) == 10
    assert r1 == ref, (r1, ref)


def test_layout_reference_markers():
    t = _t()
    assert "MANAGER_REPORT_1_LAYOUT_REFERENCE = TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_06.html" in t
    assert "MANAGER_REPORT_1_MATCHES_06_STRUCTURE = YES" in t


def test_sentence_verbatim():
    m = re.search(r'<div class="sent" id="nazila-sentence">(.*?)</div>', _t(), flags=re.S)
    assert m and m.group(1) == SENTENCE


def test_has_code_output_and_ten_token_tables():
    t = _t()
    assert "مخرجات الكود الموجودة فعلًا" in t
    for tok in [f"t00{i}" for i in range(10)]:
        assert ">" + tok + "<" in t, tok


def test_manat_tanzil_answer_shown_as_forbidden_not_born():
    t = _t()
    assert "MANAT_BIRTH_STATUS = FORBIDDEN_ANCESTOR_UNBORN" in t
    assert "TANZIL_BIRTH_STATUS = FORBIDDEN_ANCESTOR_UNBORN" in t
    assert "FINAL_ANSWER_ALLOWED = NO" in t and "FINAL_HUKM_ISSUED = NO" in t
    # the manāṭ sentence must state birth is forbidden because normative ḥukm is unborn
    assert "ولادة المناط ممنوعة" in t
    # no born tanzil candidate
    assert "TANZIL_CANDIDATE" not in t
    assert "TANZIL_READINESS_OBSTRUCTION_REPORT" in t


def test_maqam_and_reference_decisions_present():
    t = _t()
    assert "MAQAM_INVENTORY_EXCLUDES_CURRENT_CASE = YES" in t
    assert "MAQAM_6_OWNER_RATIFIED = NO" in t
    assert "REFERENCE_POLICY_DECISION_REQUIRED = YES" in t


def test_flags_and_scores():
    t = _t()
    assert "REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY" in t
    assert "ILLUSTRATIVE_DEMO = NO" in t
    assert "LLM_FREE_TEXT_OUTPUT = NO" in t
    assert "DOCUMENT = 80.0" in t and "DAL_MADLUL = 90.0" in t


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _t())


def test_match_json_records_ordered_match():
    j = json.loads(MATCH_JSON.read_text(encoding="utf-8"))
    assert j["headings_match_in_order"] is True
    assert j["section_count"] == 10
    assert j["results_08_09_changed"] == "NO"


def test_matrix_flags():
    m = _matrix()
    assert m["MANAGER_REPORT_1_MATCHES_06_STRUCTURE"] == "YES"
    assert m["SECTION_COUNT"] == "10"
    assert m["TANZIL_CANDIDATE_SHOWN_AS_BORN"] == "NO"
    for k in ("SCORE_CHANGED", "RUNTIME_CHANGED", "GATES_OPENED", "RESULTS_08_09_CHANGED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["DOCUMENT"] == "80.0" and m["DAL_MADLUL"] == "90.0"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
