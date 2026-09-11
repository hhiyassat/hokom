#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_OWNER_RATIFIED_MASALA_TAKYIF_CANDIDATE_APPLICATION_12 — guard test.

Owner ratified the takyīf layer (this nazila only); this round applies it to emit candidate-only
takyīf. Every candidate is CANDIDATE_ONLY / domain_born=NO / normative_source_allowed=NO; no
ḥukm/manāṭ/tanzīl/final answer; no domain born; the report never asserts the nazila is finally mīrāth
or qaḍāʾ. DOMAIN_ROUTING_LAYER not canonical; old typos absent. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
RATIF = OUT / "MASALA_TAKYIF_LAYER_OWNER_RATIFICATION_12.json"
APPS = OUT / "MASALA_TAKYIF_CANDIDATE_APPLICATION_12.json"
GUARDS = OUT / "MASALA_TAKYIF_APPLICATION_GUARDS_12.json"
OWNER_REQ = OUT / "OWNER_RATIFICATION_REQUEST_FOR_DOMAIN_CLASSIFICATION_13.md"
MATRIX = OUT / "MASALA_TAKYIF_CANDIDATE_APPLICATION_12_MATRIX.csv"
REPORT = OUT / "MASALA_TAKYIF_CANDIDATE_APPLICATION_MANAGER_REPORT_AR_12.html"
TYPOS = ["BINDING_GSTE_NOT_RATIFISD", "VERBAL_IMPERFPECT"]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_files_exist():
    for p in (RATIF, APPS, GUARDS, OWNER_REQ, MATRIX, REPORT):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_json_valid():
    json.loads(RATIF.read_text(encoding="utf-8"))
    json.loads(APPS.read_text(encoding="utf-8"))
    json.loads(GUARDS.read_text(encoding="utf-8"))


def test_layer_ratified_this_nazila_only():
    r = json.loads(RATIF.read_text(encoding="utf-8"))
    assert r["MASALA_TAKYIF_LAYER_OWNER_RATIFIED"] == "YES"
    assert r["MASALA_TAKYIF_LAYER_SCOPE"] == "THIS_NAZILA_ONLY"
    assert r["DOMAIN_CLASSIFICATION_BIRTH_ALLOWED_NOW"] == "NO"
    assert r["NORMATIVE_SOURCE_SELECTION_ALLOWED_NOW"] == "NO"
    assert r["FINAL_ANSWER_ALLOWED_NOW"] == "NO"


def test_four_candidates_candidate_only():
    apps = json.loads(APPS.read_text(encoding="utf-8"))
    assert len(apps) == 4
    ids = {a["candidate_id"] for a in apps}
    assert {"MIRATH_RELATED_TAKYIF_CANDIDATE", "QADA_RELATED_TAKYIF_CANDIDATE",
            "TURKAH_RIGHTS_TAKYIF_CANDIDATE", "SUKNA_OR_POSSESSION_TAKYIF_CANDIDATE"} <= ids
    for a in apps:
        assert a["birth_status"] == "CANDIDATE_ONLY", a["candidate_id"]
        assert a["domain_born"] == "NO", a["candidate_id"]
        assert a["normative_source_allowed"] == "NO", a["candidate_id"]
        assert a["verdict"] in ("ACCEPT_AS_CANDIDATE_ONLY", "DEFER_AS_CANDIDATE_ONLY")
        assert "ACCEPT_AS_DOMAIN" not in a["verdict"]
        for f in ("cause", "conditions", "preventers", "evidence", "residuals"):
            assert a[f], (a["candidate_id"], f)


def test_no_domain_born():
    m = _m()
    assert m["DOMAIN_CLASSIFICATION_BORN"] == "NO"
    assert m["MIRATH_DOMAIN_BORN"] == "NO"
    assert m["QADA_DOMAIN_BORN"] == "NO"


def test_no_normative_source_or_ruling():
    m = _m()
    assert m["NORMATIVE_SOURCE_BIRTH_STATUS"] == "NOT_OPENED"
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k


def test_guards_enforced():
    g = json.loads(GUARDS.read_text(encoding="utf-8"))
    for k in ("WORD_PRESENT_DOES_NOT_BIRTH_DOMAIN", "FRAME_DOES_NOT_BIRTH_DOMAIN",
              "CANDIDATE_DOES_NOT_BIRTH_DOMAIN", "NO_NORMATIVE_SOURCE_SELECTION",
              "NO_HUKM", "NO_MANAT", "NO_TANZIL", "NO_FINAL_ANSWER"):
        assert g[k] == "YES", k


def test_report_has_sentence_tokens_candidates_owner_decision():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f"<th>t00{i}</th>" in t, i
    assert "قرار المالك في الجولة 12" in t
    assert "MASALA_TAKYIF_LAYER_OWNER_RATIFIED = YES" in t
    for cid in ("MIRATH_RELATED_TAKYIF_CANDIDATE", "QADA_RELATED_TAKYIF_CANDIDATE"):
        assert cid in t, cid


def test_report_does_not_finalize_domain():
    t = REPORT.read_text(encoding="utf-8")
    assert "مواريث نهائيًا" not in t
    assert "قضاء نهائيًا" not in t


def test_domain_routing_not_canonical_and_no_typos():
    m = _m()
    blob = REPORT.read_text(encoding="utf-8") + MATRIX.read_text(encoding="utf-8") + APPS.read_text(encoding="utf-8")
    for bad in TYPOS:
        assert bad not in blob, bad
    # DOMAIN_ROUTING_LAYER never used as a canonical layer name
    assert "DOMAIN_ROUTING_LAYER" not in REPORT.read_text(encoding="utf-8")


def test_prior_rounds_unchanged_no_commit():
    m = _m()
    assert m["PRIOR_ROUND_VERDICTS_CHANGED"] == "NO"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["ASSERTED_NOT_MEASURED_COUNT"] == "0"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert not re.search(r"https?://|//cdn", REPORT.read_text(encoding="utf-8"))


def test_owner_request_13_questions():
    t = OWNER_REQ.read_text(encoding="utf-8")
    for q in ("ALLOW_DOMAIN_BIRTH", "SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE",
              "ALLOW_NORMATIVE_SOURCE_REQUEST_NEXT"):
        assert q in t, q


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
