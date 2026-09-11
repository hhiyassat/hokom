#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NORMATIVE_SOURCE_BIRTH_07 (Part B) — guard test. maqām source is NOT a normative source."""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REPORT = OUT / "NORMATIVE_SOURCE_BIRTH_MANAGER_REPORT_AR_07.html"
MATRIX = OUT / "NORMATIVE_SOURCE_BIRTH_07_MATRIX.csv"
FIXED06 = OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06_FIXED.html"


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def _n(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_fixed06_present():
    assert FIXED06.exists() and FIXED06.stat().st_size > 1000


def test_report07_exists_ar05_format():
    assert REPORT.exists() and REPORT.stat().st_size > 1000
    t = REPORT.read_text(encoding="utf-8")
    assert _m()["MANAGER_REPORT_CANONICAL_FORMAT"] == "MAQAM_AR_05_STYLE"
    nums = [int(x) for x in re.findall(r"<h2>(\d+)\.", t)]
    assert nums == list(range(1, 15)), nums
    assert 'id="nazila-sentence"' in t


def test_prior_closures_carried():
    m = _m()
    assert m["MAQAM_6_OWNER_RATIFIED"] == "YES"
    assert m["REFERENCE_POLICY_OWNER_RATIFIED"] == "YES"
    assert m["FACTUAL_CLAIM_BIRTH_STATUS"] == "BORN_BUT_DEFERRED"


def test_maqam_source_not_normative_source():
    m = _m()
    assert m["MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE"] == "NO"
    ns = _n("NAZILA_NORMATIVE_SOURCE_BIRTH_07.json")
    assert ns["maqam_theory_source_is_normative_source"] == "NO"
    assert "MAQAM_THEORY_SOURCE_IS_NOT_NORMATIVE_SOURCE" in ns["preventers"]


def test_normative_source_unborn_without_ratified_source():
    m = _m()
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "UNBORN"
    assert m["NORMATIVE_SOURCE_BLOCKER"] == "NO_RATIFIED_NORMATIVE_SOURCE"
    for k in ("NORMATIVE_AUTHORITY_PRESENT", "NORMATIVE_SOURCE_TEXT_PRESENT",
              "NORMATIVE_SOURCE_SCOPE_PRESENT", "NORMATIVE_EVIDENCE_PRESENT",
              "NORMATIVE_LINK_LICENSE_PRESENT"):
        assert m[k] == "NO", k
    ns = _n("NAZILA_NORMATIVE_SOURCE_BIRTH_07.json")
    assert ns["gate_decision"] in ("BLOCK", "DEFER")
    assert ns["birth_status"] == "UNBORN"


def test_children_forbidden():
    assert _n("NAZILA_NORMATIVE_HUKM_BIRTH_07.json")["NORMATIVE_HUKM_BIRTH_STATUS"] == "FORBIDDEN_PARENT_UNBORN"
    im = _n("NAZILA_ILLAH_MANAT_BIRTH_07.json")
    assert im["ILLAH_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert im["MANAT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert _n("NAZILA_TANZIL_BIRTH_07.json")["TANZIL_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    aa = _n("NAZILA_ANSWER_AUDIT_BIRTH_07.json")
    assert aa["ANSWER_AUDIT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert aa["FINAL_ANSWER_PRODUCED"] == "NO" and aa["FINAL_ANSWER_ALLOWED"] == "NO"


def test_no_ruling_in_matrix():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "FINAL_ANSWER_PRODUCED", "FINAL_ANSWER_ALLOWED", "FINAL_HUKM_ISSUED"):
        assert m[k] == "NO", k
    assert m["MANAT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["TANZIL_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["NORMATIVE_HUKM_BIRTH_STATUS"] == "FORBIDDEN_PARENT_UNBORN"


def test_full_source2_fields_and_no_asserted():
    ns = _n("NAZILA_NORMATIVE_SOURCE_BIRTH_07.json")
    for f in ("node_name", "input_sources", "cause", "conditions", "preventers", "gate_decision",
              "birth_status", "evidence_files", "producer_file", "residuals", "verdict"):
        assert f in ns and ns[f] not in (None, "", []), f
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"
    assert _m()["SILENT_FALLBACK_COUNT"] == "0"


def test_no_external_refs_and_no_commit():
    assert not re.search(r"https?://|//cdn", REPORT.read_text(encoding="utf-8"))
    m = _m()
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
