#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_SOURCE_2_FULL_PRESERVATION_TRACEABILITY_AND_MANAGER_CLOSURE_03 — closure guard test.

Administrative preservation + traceability + manager-report closure. The manager report exists,
is code-generated, and never claims a full PDF (none exists); Source-2 is hashed; every Source-2 rule
is traceable (untraced=0, asserted-not-measured=0); round-02 verdicts unchanged; canonical stays
BLOCKED_WITH_CAUSE; no normative/manāṭ/tanzīl/final output. Artifacts only.
"""
import json
import pathlib
import re

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
DOCS = ROOT / "docs"
MANAGER = OUT / "MAQAM_SOURCE_2_FULL_PRESERVATION_MANAGER_REPORT_AR_03.html"
MATRIX = OUT / "MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03_MATRIX.csv"
AUDIT = OUT / "MAQAM_SOURCE_2_FULL_PRESERVATION_CLOSURE_03.json"
MANIFEST = DOCS / "MAQAM_THEORY_SOURCE_2_MANIFEST.json"


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def _audit():
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def test_manager_report_exists_nonempty():
    assert MANAGER.exists() and MANAGER.stat().st_size > 500
    m = _matrix()
    assert m["MANAGER_REPORT_CREATED"] == "YES"
    assert m["MANAGER_REPORT_SOURCE"] == "CODE_AND_ARTIFACTS_ONLY"


def test_manager_is_arabic_and_has_closure_phrase():
    t = MANAGER.read_text(encoding="utf-8")
    assert "تقرير المدير" in t
    assert "إغلاق إداري مطلوب للمدير" in t
    assert len(re.findall(r"<h2>\d+\.", t)) == 14


def test_manager_does_not_claim_full_pdf():
    # a full PDF does NOT exist -> the token FULL_PDF_PRESERVED must not appear anywhere in the report
    t = MANAGER.read_text(encoding="utf-8")
    assert "FULL_PDF_PRESERVED" not in t
    assert _matrix()["SOURCE_2_FULL_PDF_AVAILABLE"] == "NO"
    assert _matrix()["SOURCE_2_PRESERVATION_STATUS"] == "OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED"


def test_manifest_has_sha256():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert len(m["SOURCE_SHA256"]) == 64
    assert m["FULL_PDF_AVAILABLE"] == "NO"
    assert m["SOURCE_PRESERVATION_STATUS"] == "OWNER_PASTED_MARKDOWN_OR_EXCERPT_PRESERVED"
    assert m["UNTRACED_REQUIREMENTS_COUNT"] == 0
    assert (ROOT / m["SOURCE_LOCAL_PATH"]).exists()


def test_source2_rules_all_traceable():
    a = _audit()
    rows = a["source_2_traceability"]
    assert {r["requirement_id"] for r in rows} == {
        "REQ-COREFERENCE", "REQ-ELLIPSIS", "REQ-RANK", "REQ-SPEECH-ACT", "REQ-CANONICAL-BLOCKER"}
    for r in rows:
        assert r["source_id"] and r["source_anchor"] and r["implemented_by"] and r["artifact_output"]
        assert r["status"] == "TRACEABLE", r["requirement_id"]
        assert (OUT / r["artifact_output"]).exists()
    assert a["SOURCE_2_UNTRACED_REQUIREMENTS_COUNT"] == 0
    assert a["ASSERTED_NOT_MEASURED_COUNT"] == 0


def test_traceability_csv_has_named_source2_rows():
    rows = (DOCS / "MAQAM_REQUIREMENTS_TRACEABILITY.csv").read_text(encoding="utf-8").splitlines()
    for req in ("REQ-COREFERENCE", "REQ-ELLIPSIS", "REQ-RANK", "REQ-SPEECH-ACT", "REQ-CANONICAL-BLOCKER"):
        assert any(r.startswith(req + ",") for r in rows), req


def test_round_02_verdicts_unchanged():
    m = _matrix()
    assert m["COREFERENCE_GATE_STATUS"] == "IMPLEMENTED"
    assert m["ELLIPSIS_GATE_STATUS"] == "IMPLEMENTED"
    assert m["RANK_GATE_STATUS"] == "IMPLEMENTED"
    assert m["SPEECH_ACT_GATE_STATUS"] == "IMPLEMENTED"


def test_canonical_still_blocked_and_no_normative():
    m = _matrix()
    assert m["CANONICAL_INTEGRATION_STATUS"] == "BLOCKED_WITH_CAUSE"
    assert m["CANONICAL_OPENED"] == "NO"
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED",
              "FINAL_HUKM_ISSUED", "FINAL_ANSWER_ALLOWED"):
        assert m[k] == "NO", k


def test_no_external_refs_in_manager():
    assert not re.search(r"https?://|//cdn", MANAGER.read_text(encoding="utf-8"))


def test_flags_no_change_no_commit():
    m = _matrix()
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert m["EXTERNAL_REFS"] == "0"


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
