#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_THEORY_FOUNDATION_IMPLEMENTATION_WITH_TRACEABILITY — foundation guard test.

Exercises the real producers (foundation registries/guards + the existing maqām engine + the two
nazila runs). No test asserts a hand-written constant only; each goes through code. maqām never
produces a normative artifact; text alone never infers an istiftāʾ maqām.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "taaqol_maqam_theory_implementation_01" / "src"))

from taaqol_maqam_foundation import foundation as F  # noqa: E402

OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
DOCS = ROOT / "docs"


# ---------------- source governance ----------------
def test_source_manifest_recorded():
    m = json.loads((DOCS / "MAQAM_THEORY_SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
    assert m["source_type"] == "OWNER_PROVIDED_THEORY_SOURCE"
    assert m["rewritten_by_agent"] == "NO"
    assert m["summary_is_not_source"] == "YES"
    assert len(m["sha256"]) == 64
    assert m["page_count"] == 33 and m["page_count_matches_declared"] is True
    assert (ROOT / m["stored_file_path"]).exists()
    assert m["text_extraction_quality"] == "SOURCE_TEXT_EXTRACTION_UNCERTAIN"
    assert m["phrase_correction"]["to"] == "MAQAM_THEORY_FOUNDATION_IMPLEMENTATION_WITH_TRACEABILITY"


def test_traceability_csv_has_owner_and_deferred_rows():
    rows = (DOCS / "MAQAM_REQUIREMENTS_TRACEABILITY.csv").read_text(encoding="utf-8").splitlines()
    assert rows[0].startswith("requirement_id,")
    body = rows[1:]
    assert len(body) >= 12
    # PDF-body-dependent requirement must be deferred due to corruption
    assert any("DEFERRED_SOURCE_TEXT_CORRUPTION" in r for r in body)
    # owner-stated requirements must trace to the addendum/QIYAS, not to corrupted PDF verbatim
    assert any("OWNER_ADDENDUM_FINAL" in r for r in body)


# ---------------- registries ----------------
def test_core_dimensions_present():
    p = F.core_registry_payload()
    for k in ("SPEAKER", "ADDRESSEE", "PURPOSE", "REFERENCE_WORLD", "TIME", "PLACE",
              "SOCIAL_CUSTOM", "HISTORICAL_CONTEXT", "AUTHORITY_CONTEXT", "DISPUTE_CONTEXT"):
        assert k in p["core_dimensions"], k
    assert p["core_dimensions_policy"] == "VERSIONED_RATIFIED_SET"
    assert p["silent_dimension_drop"] == "FORBIDDEN"


def test_unknown_dimension_defers_not_dropped():
    reg = F.MaqamDimensionRegistry()
    # unknown -> DEFER (recorded), never dropped
    assert reg.resolve("MOON_PHASE") == F.RESOLVE_DEFER
    assert "MOON_PHASE" in reg.deferred
    # register under governance -> extension
    assert reg.register_extension("MOON_PHASE", "owner governance note") == F.RESOLVE_EXTENSION
    assert reg.resolve("MOON_PHASE") == F.RESOLVE_EXTENSION
    # no governance note -> deferred, not registered
    assert reg.register_extension("VIBE", "") == F.RESOLVE_DEFER
    # core stays core
    assert reg.resolve("SPEAKER") == F.RESOLVE_CORE


def test_rank_ladder_ordered_with_externally_supplied():
    ladder = F.RANK_LADDER
    assert ladder == ["GENERATED", "TEXTUAL_INFERENCE", "OBSERVED",
                      "EXTERNALLY_SUPPLIED", "OWNER_DECLARED", "RATIFIED"]
    assert F.EvidenceRankFull.TEXTUAL_INFERENCE < F.EvidenceRankFull.EXTERNALLY_SUPPLIED
    assert F.EvidenceRankFull.EXTERNALLY_SUPPLIED < F.EvidenceRankFull.OWNER_DECLARED
    assert F.EvidenceRankFull.OWNER_DECLARED < F.EvidenceRankFull.RATIFIED


def test_four_scholarly_branches_present():
    assert F.FOUR_BRANCHES == ("MAQAM_IN_LINGUISTS", "MAQAM_IN_RHETORICIANS",
                              "MAQAM_IN_USULIYYIN", "MAQAM_IN_TAFSIR")


# ---------------- maqam != normative guard ----------------
def test_maqam_not_normative():
    assert F.assert_maqam_not_normative("EARLY_INTERPRETATION") == "MAQAM_SCOPE_OK"
    for forbidden in ("NORMATIVE_SOURCE", "NORMATIVE_HUKM", "ILLAH", "MANAT", "TANZIL", "FINAL_ANSWER"):
        with pytest.raises(F.MaqamOverreachError):
            F.assert_maqam_not_normative(forbidden)


# ---------------- active scope match ----------------
def test_scope_mismatch_rejected():
    req = "ARABIC_UNDERSTANDING/FACTUAL_CLAIM_BIRTH"
    assert F.scope_within(req, req) is True
    assert F.scope_within(req + "/EXAMPLE", req) is True
    assert F.scope_within("ARABIC_UNDERSTANDING/EARLY_INTERPRETATION", req) is False
    assert F.scope_within("", req) is False


# ---------------- two nazila runs ----------------
def _run(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_run_a_no_istifta():
    a = _run("MAQAM_NAZILA_WITHOUT_OWNER_CONTEXT.json")
    assert a["OWNER_MAQAM_DECLARATION"] == "ABSENT"
    assert a["ISTIFTA_INFERRED_FROM_TEXT_ALONE"] == "NO"
    assert a["factual_claim_birth"]["decision"] == "DEFER"
    assert a["early_interpretation"]["decision"] == "ACCEPT"


def test_run_b_example_not_owner_decision():
    b = _run("MAQAM_NAZILA_EXAMPLE_CONTEXT.json")
    assert b["EXAMPLE_ONLY_NOT_OWNER_DECISION"] == "YES"
    # within the example scope a factual-claim maqām certificate may be born
    assert b["factual_claim_birth"]["decision"] == "ACCEPT"
    assert b["factual_claim_birth"]["maqam_certificate_birth"] == "BORN"


def test_normative_forbidden_in_both_runs():
    for name in ("MAQAM_NAZILA_WITHOUT_OWNER_CONTEXT.json", "MAQAM_NAZILA_EXAMPLE_CONTEXT.json"):
        d = _run(name)
        assert d["MAQAM_PRODUCES_NORMATIVE"] == "NO"
        assert d["normative_hukm_birth"].startswith("FORBIDDEN")
        assert d["manat_birth"].startswith("FORBIDDEN")
        assert d["tanzil_birth"].startswith("FORBIDDEN")
        assert d["final_answer_birth"].startswith("FORBIDDEN")


def test_runs_are_deterministic():
    # re-run the generator to a temp dir and compare the two run artifacts byte-for-byte
    import subprocess
    import tempfile
    gen = ROOT / "scripts" / "taaqol_maqam_foundation" / "run_nazila_foundation.py"
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(["python3", str(gen), "--out-dir", d], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        for name in ("MAQAM_NAZILA_WITHOUT_OWNER_CONTEXT.json", "MAQAM_NAZILA_EXAMPLE_CONTEXT.json"):
            assert (pathlib.Path(d) / name).read_text(encoding="utf-8") == (OUT / name).read_text(encoding="utf-8")


# ---------------- closure manifest honesty ----------------
def test_closure_manifest_no_overclaim():
    m = json.loads((OUT / "MAQAM_CLOSURE_MANIFEST.json").read_text(encoding="utf-8"))
    assert m["project_finished"] == "NO"
    assert m["maqam_canonical_closure_status"] == "NOT_CANONICALLY_CLOSED"
    assert m["normative_overreach_count"] == 0
    assert m["descendant_born_without_parent_count"] == 0
    for k in ("normative_hukm_produced", "manat_produced", "tanzil_produced", "final_answer_produced"):
        assert m[k] == "NO", k


def test_manager_report_no_external_refs():
    import re
    t = (OUT / "MAQAM_EXECUTIVE_MANAGER_REPORT_AR.html").read_text(encoding="utf-8")
    assert not re.search(r"https?://|//cdn", t)
    assert "MAQAM_IN_LINGUISTS" in t and "MAQAM_IN_TAFSIR" in t
