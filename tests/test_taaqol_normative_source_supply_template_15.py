#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_NORMATIVE_SOURCE_SUPPLY_TEMPLATE_AND_RATIFICATION_GATE_15 — guard test.

An owner-fill supply template for a normative source per domain candidate (composite kept). It is not a
source: not selected, not born, not ratified. No ḥukm/manāṭ/tanzīl/final answer. Manager report mirrors
the AR_09_FIXED functional layout. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
TMD = OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.md"
TJSON = OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15.json"
GUARDS = OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_GUARDS_15.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_NORMATIVE_SOURCE_BIRTH_16.md"
MATRIX = OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_15_MATRIX.csv"
REPORT = OUT / "NORMATIVE_SOURCE_SUPPLY_TEMPLATE_MANAGER_REPORT_AR_15.html"
FIELDS = ["AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"]
FOUR = {"MIRATH_RELATED_DOMAIN_CANDIDATE", "QADA_RELATED_DOMAIN_CANDIDATE",
        "TURKAH_RIGHTS_DOMAIN_CANDIDATE", "SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE"}
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (TMD, TJSON, GUARDS, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid_and_composite_kept():
    t = json.loads(TJSON.read_text(encoding="utf-8"))
    assert t["PRIMARY_DOMAIN_CANDIDATE"] == "KEEP_COMPOSITE"
    assert t["SOURCE_BIRTH_ALLOWED"] == "NO"
    assert t["SOURCE_REQUEST_REFINED_ALLOWED"] == "YES"
    assert t["required_fields"] == FIELDS
    assert t["normative_source_born"] == "NO"
    assert t["normative_source_ratified"] == "NO"


def test_five_fields_per_candidate():
    t = json.loads(TJSON.read_text(encoding="utf-8"))
    per = t["per_domain_supply_template"]
    assert len(per) == 4
    assert {d["domain_candidate_id"] for d in per} == FOUR
    for d in per:
        for f in FIELDS:
            assert f in d, (d["domain_candidate_id"], f)
        assert d["OWNER_RATIFICATION"] == "NO"


def test_template_md_has_five_fields_per_candidate():
    t = TMD.read_text(encoding="utf-8")
    for f in FIELDS:
        assert f in t, f
    assert t.count("OWNER_RATIFICATION = YES/NO") >= 4


def test_source_not_born_selected_or_ratified():
    m = _m()
    assert m["NORMATIVE_SOURCE_BORN"] == "NO"
    assert m["NORMATIVE_SOURCE_SELECTED"] == "NO"
    assert m["NORMATIVE_SOURCE_RATIFIED"] == "NO"
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "NOT_OPENED"
    assert m["TEMPLATE_IS_NOT_SOURCE"] == "YES"


def test_no_hukm_manat_tanzil_final():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("SOURCE_TEMPLATE_IS_NOT_SOURCE", "SOURCE_REQUIREMENT_IS_NOT_RATIFICATION",
              "COMPOSITE_DOMAIN_IS_NOT_NORMATIVE_SOURCE", "NO_NORMATIVE_SOURCE_BIRTH",
              "NO_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_report_mirrors_ar09_fixed_layout():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    # standalone traceability table (AR_09_FIXED signature) + closure flags + tests-result block
    assert "جدول التتبّع (مستقل عن جدول الكلمات)" in t
    assert "أعلام الإغلاق داخل التقرير" in t
    assert "ROUND_15_TESTS = passed" in t
    assert "قرار المالك في الجولة 15" in t
    for did in FOUR:
        assert did in t, did
    # explicit statements
    assert "NORMATIVE_SOURCE_BORN = NO" in t
    assert "NORMATIVE_SOURCE_SELECTED = NO" in t


def test_traceability_no_empty_cells():
    t = REPORT.read_text(encoding="utf-8")
    assert "<td></td>" not in t
    assert ">ASSERTED_NOT_MEASURED<" not in t
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"


def test_owner_request_16_fields():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("PRIMARY = KEEP_COMPOSITE | PICK_ONE", "ALLOW_NORMATIVE_SOURCE_BIRTH",
              "AUTHORITY", "TEXT", "SCOPE", "EVIDENCE", "LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM"):
        assert q in t, q


def test_no_typos_no_external_refs_no_commit():
    blob = REPORT.read_text(encoding="utf-8") + MATRIX.read_text(encoding="utf-8") + TJSON.read_text(encoding="utf-8")
    for bad in TYPOS:
        assert bad not in blob, bad
    assert "DOMAIN_ROUTING_LAYER" not in REPORT.read_text(encoding="utf-8")
    m = _m()
    assert m["PRIOR_ROUND_VERDICTS_CHANGED"] == "NO"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert not re.search(r"https?://|//cdn", REPORT.read_text(encoding="utf-8"))


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
