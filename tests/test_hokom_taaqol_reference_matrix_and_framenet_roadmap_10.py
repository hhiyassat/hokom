#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOKOM_TAAQOL_REFERENCE_MATRIX_AND_HOKOM_FRAMENET_ROADMAP_10 — guard test.

Documentation + reference matrix + candidate-only Hokom-FrameNet. DOMAIN_ROUTING_LAYER is not a
canonical name; MASALA_TAKYIF_LAYER is PROPOSED_NOT_CANONICAL; Hokom-FrameNet stays a candidate layer;
the surface words «وارثه»/«فتحاكما» do NOT birth mīrāth/qaḍāʾ domains; no normative source; no
ḥukm/manāṭ/tanzīl/final answer; AR_05-style report with closure flags. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
DOCS = ROOT / "docs"
SCHEMAS = ROOT / "schemas"
ROADMAP = DOCS / "HOKOM_TAAQOL_REFERENCE_MATRIX_AND_FRAMENET_ROADMAP_10.md"
MANIFEST = DOCS / "HOKOM_TAAQOL_REFERENCE_SOURCE_MANIFEST_10.json"
SCHEMA = SCHEMAS / "hokom_framenet_schema_10.json"
STATUS = OUT / "HOKOM_FRAMENET_ROADMAP_STATUS_10.json"
MATRIX = OUT / "HOKOM_FRAMENET_REFERENCE_MATRIX_10.csv"
REPORT = OUT / "HOKOM_FRAMENET_MANAGER_REPORT_AR_10.html"
SIGNALS = OUT / "HOKOM_TEXT_SIGNALS_10.json"
FRAMES = OUT / "HOKOM_FRAME_CANDIDATES_10.json"


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_all_outputs_exist():
    for p in (ROADMAP, MANIFEST, SCHEMA, STATUS, MATRIX, REPORT, SIGNALS, FRAMES):
        assert p.exists() and p.stat().st_size > 0, p.name


def test_matrix_present_and_filled():
    m = _m()
    assert m["REFERENCE_MATRIX_CREATED"] == "YES"
    # 11 reference rows recorded
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r.startswith("REF_ROW_")]
    assert len(rows) == 11, len(rows)


def test_every_reference_has_availability_and_verdict():
    refs = json.loads(MANIFEST.read_text(encoding="utf-8"))["references"]
    assert len(refs) == 11
    for r in refs:
        assert r["open_source_available"], r["id"]
        assert r["usage_verdict"], r["id"]


def test_domain_routing_layer_not_canonical():
    m = _m()
    assert m["DOMAIN_ROUTING_LAYER_CANONICAL"] == "NO"
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert man["DOMAIN_ROUTING_LAYER_CANONICAL"] == "NO"


def test_masala_takyif_proposed_not_canonical():
    assert _m()["MASALA_TAKYIF_LAYER_STATUS"] == "PROPOSED_NOT_CANONICAL"
    assert json.loads(MANIFEST.read_text(encoding="utf-8"))["OWNER_RATIFICATION_REQUIRED"] == "YES"


def test_hokom_framenet_candidate_layer():
    assert _m()["HOKOM_FRAMENET_STATUS"] == "CANDIDATE_LAYER"
    assert _m()["WORDNET_WORDFRAMENET_BRIDGE_STATUS"] == "CANDIDATE_ONLY"
    for fc in json.loads(FRAMES.read_text(encoding="utf-8")):
        assert fc["birth_status"] == "CANDIDATE"
        assert fc["owner_ratified"] == "NO"
        assert fc["is_domain_classification"] == "NO"


def test_no_mirath_from_waritha():
    sigs = json.loads(SIGNALS.read_text(encoding="utf-8"))
    blocked = {s["blocked_domain_birth"] for s in sigs}
    assert "MIRATH_CANDIDATE" in blocked  # flagged as forbidden-to-birth, i.e. NOT born
    assert _m()["MIRATH_CANDIDATE_BORN"] == "NO"


def test_no_qada_from_fatahakama():
    sigs = json.loads(SIGNALS.read_text(encoding="utf-8"))
    blocked = {s["blocked_domain_birth"] for s in sigs}
    assert "QADA_CANDIDATE" in blocked
    assert _m()["QADA_CANDIDATE_BORN"] == "NO"


def test_no_normative_source_birth():
    assert _m()["NORMATIVE_SOURCE_PRODUCED"] == "NO"


def test_no_hukm_manat_tanzil_final():
    m = _m()
    for k in ("HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["DOMAIN_CLASSIFICATION_PRODUCED"] == "NO"


def test_report_ar05_closure_flags_and_sentence():
    t = REPORT.read_text(encoding="utf-8")
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for s in ("ASSERTED_NOT_MEASURED_COUNT = 0", "SILENT_FALLBACK_COUNT = 0",
              "TESTS_PASS = YES", "COMMIT = NO", "PROJECT_FINISHED = NO"):
        assert s in t, s
    assert not re.search(r"https?://|//cdn", t)


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
