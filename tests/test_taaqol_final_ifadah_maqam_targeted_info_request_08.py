#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL_IFADAH_MAQAM_AND_TARGETED_INFORMATION_REQUEST_FOR_TANZIL_08 — guard test.

Ends not at a dry NORMATIVE_SOURCE=UNBORN but at a specific targeted information request. Ifādah is
produced by code; maqam + reference ratified; factual_claim BORN_BUT_DEFERRED with a MISSING passage
license; normative source UNBORN; tanzīl FORBIDDEN_MISSING_REQUIREMENTS; two concrete info-request
docs produced. maqām source is NOT a normative source. No ruling; no typos; artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REPORT = OUT / "FINAL_IFADAH_MAQAM_TARGETED_INFO_REQUEST_MANAGER_REPORT_AR_08.html"
MATRIX = OUT / "FINAL_IFADAH_MAQAM_TARGETED_INFO_REQUEST_08_MATRIX.csv"
IFADAH = OUT / "NAZILA_IFADAH_AND_FACTUAL_CLAIM_PASSAGE_08.json"
TANZIL = OUT / "NAZILA_TANZIL_READINESS_AFTER_INFO_REQUEST_08.json"
REQ_FC = OUT / "ADDITIONAL_INFORMATION_REQUEST_FOR_FACTUAL_CLAIM_PASSAGE_08.md"
REQ_NS = OUT / "ADDITIONAL_INFORMATION_REQUEST_FOR_NORMATIVE_SOURCE_08.md"
FINAL = OUT / "FINAL_IFADAH_MAQAM_TARGETED_INFO_REQUEST_08.json"
FORBIDDEN = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_outputs_exist():
    for p in (REPORT, MATRIX, IFADAH, TANZIL, REQ_FC, REQ_NS, FINAL):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_report_ar05_format_16_sections():
    t = REPORT.read_text(encoding="utf-8")
    assert '<html lang="ar" dir="rtl">' in t
    nums = [int(x) for x in re.findall(r"<h2>(\d+)\.", t)]
    assert nums == list(range(1, 17)), nums
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f">t00{i}<" in t, i


def test_ifadah_present_and_maqam_reference_ratified():
    m = _m()
    assert m["IFADAH_PRODUCED_BY_CODE"] == "YES"
    assert m["IFADAH_MISSING"] == "NO"
    assert m["MAQAM_6_OWNER_RATIFIED"] == "YES"
    assert m["MAQAM_6"] == "MASALA_MUSAWWARA_LIL_ISTIFTA"
    assert m["REFERENCE_POLICY_OWNER_RATIFIED"] == "YES"
    assert m["REFERENCE_POLICY_DECISION_REQUIRED"] == "NO"


def test_factual_claim_born_but_deferred_missing_passage():
    m = _m()
    assert m["FACTUAL_CLAIM_BIRTH_STATUS"] == "BORN_BUT_DEFERRED"
    assert m["FACTUAL_CLAIM_PASSAGE_LICENSE"] == "MISSING_OWNER_DECISION"
    assert m["ADDITIONAL_INFORMATION_FOR_FACTUAL_CLAIM_REQUIRED"] == "YES"


def test_normative_source_unborn_and_not_maqam():
    m = _m()
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "UNBORN"
    assert m["NORMATIVE_SOURCE_BLOCKER"] == "NO_RATIFIED_NORMATIVE_SOURCE"
    assert m["MAQAM_THEORY_SOURCE_IS_NORMATIVE_SOURCE"] == "NO"
    assert m["ADDITIONAL_INFORMATION_FOR_NORMATIVE_SOURCE_REQUIRED"] == "YES"


def test_tanzil_forbidden_missing_requirements():
    m = _m()
    assert m["TANZIL_BIRTH_STATUS"] == "FORBIDDEN_MISSING_REQUIREMENTS"
    assert m["ADDITIONAL_INFORMATION_FOR_TANZIL_REQUIRED"] == "YES"
    tz = json.loads(TANZIL.read_text(encoding="utf-8"))
    assert "RATIFIED_NORMATIVE_SOURCE" in tz["missing_requirements"]


def test_targeted_info_request_is_specific():
    fc = REQ_FC.read_text(encoding="utf-8")
    assert "BORN_BUT_DEFERRED_WITH_PASSAGE_LICENSE" in fc
    assert "THIS_NAZILA_ONLY" in fc
    ns = REQ_NS.read_text(encoding="utf-8")
    for item in ("السلطة المعيارية", "النص المعياري", "نطاق النص", "دليل الاعتماد", "رخصة الربط"):
        assert item in ns, item
    assert _m()["ADDITIONAL_INFORMATION_REQUEST_PRODUCED"] == "YES"
    assert _m()["FINAL_CLOSURE_MODE"] == "TARGETED_INFORMATION_REQUEST_PRODUCED"


def test_no_ruling_produced():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED",
              "FINAL_ANSWER_PRODUCED", "FINAL_ANSWER_ALLOWED", "FINAL_HUKM_ISSUED"):
        assert m[k] == "NO", k


def test_prior_verdicts_unchanged():
    m = _m()
    assert m["ROUND_06_VERDICTS_CHANGED"] == "NO"
    assert m["ROUND_07_VERDICTS_CHANGED"] == "NO"


def test_traceability_filled_no_asserted():
    m = _m()
    assert m["ASSERTED_NOT_MEASURED_COUNT"] == "0"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    final = json.loads(FINAL.read_text(encoding="utf-8"))
    for r in final["traceability"]:
        assert r["status"] == "TRACEABLE", r["req"]
        assert r["artifact"] and r["test"], r["req"]


def test_no_typos_and_no_external_refs():
    t = REPORT.read_text(encoding="utf-8") + MATRIX.read_text(encoding="utf-8")
    for bad in FORBIDDEN:
        assert bad not in t, bad
    assert not re.search(r"https?://|//cdn", REPORT.read_text(encoding="utf-8"))


def test_no_commit_flags():
    m = _m()
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
