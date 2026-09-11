#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FACTUAL_CLAIM_PASSAGE_AND_NORMATIVE_SOURCE_BIRTH_09 — guard test.

Owner supplied neither a factual-claim passage license nor a normative source, so passage = BLOCK,
normative source = UNBORN, and ḥukm/manāṭ/tanzīl/answer are forbidden. A sharper information request is
produced. maqām source is NOT a normative source. No ruling; no typos; artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REPORT = OUT / "FACTUAL_CLAIM_PASSAGE_NORMATIVE_SOURCE_MANAGER_REPORT_AR_09.html"
MATRIX = OUT / "FACTUAL_CLAIM_PASSAGE_NORMATIVE_SOURCE_09_MATRIX.csv"
REQ = OUT / "ADDITIONAL_INFORMATION_REQUEST_FACTUAL_CLAIM_AND_NORMATIVE_SOURCE_09.md"
FORBIDDEN = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]
NODES = ["NAZILA_FACTUAL_CLAIM_PASSAGE_09.json", "NAZILA_NORMATIVE_SOURCE_BIRTH_09.json",
         "NAZILA_NORMATIVE_HUKM_BIRTH_09.json", "NAZILA_ILLAH_MANAT_BIRTH_09.json",
         "NAZILA_TANZIL_BIRTH_09.json", "NAZILA_ANSWER_AUDIT_BIRTH_09.json"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def _n(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_outputs_exist():
    for p in [REPORT, MATRIX, REQ] + [OUT / n for n in NODES]:
        assert p.exists() and p.stat().st_size > 0, p.name


def test_stable_facts():
    m = _m()
    assert m["IFADAH_PRODUCED_BY_CODE"] == "YES"
    assert m["MAQAM_6_OWNER_RATIFIED"] == "YES"
    assert m["REFERENCE_POLICY_OWNER_RATIFIED"] == "YES"
    assert m["FACTUAL_CLAIM_BIRTH_STATUS"] == "BORN_BUT_DEFERRED"


def test_passage_blocked_without_owner_license():
    m = _m()
    assert m["OWNER_PASSAGE_LICENSE_SUPPLIED"] == "NO"
    assert m["FACTUAL_CLAIM_PASSAGE_STATUS"] == "BLOCK"
    assert _n("NAZILA_FACTUAL_CLAIM_PASSAGE_09.json")["FACTUAL_CLAIM_PASSAGE_STATUS"] == "BLOCK"


def test_normative_source_unborn_and_not_maqam():
    m = _m()
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "UNBORN"
    assert m["MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE"] == "NO"
    ns = _n("NAZILA_NORMATIVE_SOURCE_BIRTH_09.json")
    assert ns["normative_authority_present"] == "NO"
    assert "MAQAM_THEORY_SOURCE_IS_NOT_NORMATIVE_SOURCE" in ns["preventers"]


def test_no_child_born_before_parent():
    m = _m()
    assert m["NORMATIVE_HUKM_BIRTH_STATUS"] == "FORBIDDEN_PARENT_UNBORN"
    assert m["MANAT_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["TANZIL_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"
    assert m["ANSWER_AUDIT_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"


def test_no_ruling_or_final_answer():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED",
              "FINAL_ANSWER_PRODUCED", "FINAL_ANSWER_ALLOWED", "FINAL_HUKM_ISSUED"):
        assert m[k] == "NO", k


def test_sharper_info_request():
    t = REQ.read_text(encoding="utf-8")
    assert "FACTUAL_CLAIM_PASSAGE_LICENSE = GRANTED" in t
    assert "FACTUAL_CLAIM_PASSAGE_LICENSE = DENIED" in t
    for item in ("NORMATIVE_AUTHORITY", "NORMATIVE_SOURCE_TEXT", "NORMATIVE_SOURCE_SCOPE",
                 "NORMATIVE_EVIDENCE", "NORMATIVE_LINK_LICENSE"):
        assert item in t, item
    assert _m()["ADDITIONAL_INFORMATION_REQUEST_PRODUCED"] == "YES"


def test_prior_verdicts_unchanged():
    m = _m()
    assert m["ROUND_06_VERDICTS_CHANGED"] == "NO"
    assert m["ROUND_07_VERDICTS_CHANGED"] == "NO"
    assert m["ROUND_08_VERDICTS_CHANGED"] == "NO"


def test_report_ar05_16sections_sentence_tokens():
    t = REPORT.read_text(encoding="utf-8")
    assert _m()["MANAGER_REPORT_CANONICAL_FORMAT"] == "MAQAM_AR_05_STYLE"
    nums = [int(x) for x in re.findall(r"<h2>(\d+)\.", t)]
    assert nums == list(range(1, 15)), nums
    assert 'id="nazila-sentence"' in t
    for i in range(10):
        assert f">t00{i}<" in t, i


def test_no_typos_no_external_refs_no_commit():
    blob = REPORT.read_text(encoding="utf-8") + MATRIX.read_text(encoding="utf-8")
    for bad in FORBIDDEN:
        assert bad not in blob, bad
    assert not re.search(r"https?://|//cdn", REPORT.read_text(encoding="utf-8"))
    m = _m()
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert m["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
