#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_DEFERRED_CONSUMERS_AND_CANONICAL_BLOCKER_CLOSURE_02 — guard test.

The four deferred maqām consumers are real measured gates; nazila pronouns are not asserted; ellipsis
is not freely reconstructed; rank is classified; text alone infers no istiftāʾ; an example context is
not an owner ratification; canonical stays BLOCKED_WITH_CAUSE; maqām produces no normative output.
Artifacts only.
"""
import json
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
DOCS = ROOT / "docs"
MATRIX = OUT / "MAQAM_DEFERRED_CONSUMERS_CLOSURE_02_MATRIX.csv"


def _j(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_source2_preserved_and_hashed():
    m = json.loads((DOCS / "MAQAM_THEORY_SOURCE_2_MANIFEST.json").read_text(encoding="utf-8"))
    assert m["author"] == "الدكتورة صالحة حاج يعقوب"
    assert len(m["stored_excerpt_sha256"]) == 64
    assert m["replaces_source_1"] == "NO" and m["used_with_source_1"] == "YES"
    assert (ROOT / m["stored_excerpt_path"]).exists()


def test_each_rule_has_source_location():
    rows = (DOCS / "MAQAM_REQUIREMENTS_TRACEABILITY.csv").read_text(encoding="utf-8").splitlines()
    for tag in ("SOURCE_2#A", "SOURCE_2#B", "SOURCE_2#C", "SOURCE_2#D"):
        assert any(tag in r for r in rows), tag


def test_coreference_defers_nazila_pronouns():
    g = _j("MAQAM_COREFERENCE_GATE_02.json")
    assert g["gate_decision"] == "DEFER"
    assert g["coreference_decision"] == "DEFER"
    assert g["asserted_bindings"] == []
    # the forbidden assertions must be listed as forbidden, never produced as bindings
    assert "ه(معه)=الملك" in g["forbidden_assertions"]
    assert g["measured"] == "MEASURED"


def test_ellipsis_no_free_reconstruction():
    g = _j("MAQAM_ELLIPSIS_GATE_02.json")
    assert g["gate_decision"] in ("DEFER", "REJECT")
    assert g["reconstructed_material"] == "NONE_NOT_AUTHORED"
    assert g["measured"] == "MEASURED"


def test_rank_classifies_three_types():
    g = _j("MAQAM_RANK_GATE_02.json")
    types = {f["rank_type"] for f in g["fixtures"]}
    assert "CONTEXTUALLY_LOCKED" in types and "PRESERVED" in types
    assert set(g["rank_type_values"]) == {"PRESERVED", "NON_PRESERVED", "CONTEXTUALLY_LOCKED"}
    # ضرب موسى عيسى must be contextually locked with ambiguity
    lock = next(f for f in g["fixtures"] if "موسى" in f["surface"])
    assert lock["rank_type"] == "CONTEXTUALLY_LOCKED" and lock["ambiguity_present"] == "YES"


def test_speech_act_text_alone_no_istifta():
    g = _j("MAQAM_SPEECH_ACT_GATE_02.json")
    ta = g["text_alone"]
    assert ta["gate_decision"] == "DEFER"
    assert ta["text_alone_infers_istifta"] == "NO"
    assert ta["istifta_certificate"] == "NONE"


def test_example_context_not_owner_ratification():
    g = _j("MAQAM_SPEECH_ACT_GATE_02.json")["example_context"]
    assert g["example_context_owner_ratification"] == "NO"
    assert "ISTIFTA_REQUEST" in g["candidates_within_example_scope"]
    assert g["scope"].endswith("/EXAMPLE")


def test_canonical_blocked_with_cause():
    g = _j("MAQAM_CANONICAL_BLOCKER_02.json")
    assert g["canonical_integration_status"] == "BLOCKED_WITH_CAUSE"
    assert g["gate_decision"] == "BLOCK"
    assert g["required_contracts"] and g["required_adapters"] and g["owner_decisions_needed"]
    assert (DOCS / "MAQAM_CANONICAL_INTEGRATION_BLOCKER_REPORT_02.md").exists()


def test_no_normative_output_and_no_asserted_not_measured():
    m = _matrix()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED", "FINAL_ANSWER_PRODUCED"):
        assert m[k] == "NO", k
    assert m["MAQAM_PRODUCES_NORMATIVE"] == "NO"
    assert m["ASSERTED_NOT_MEASURED_COUNT"] == "0"
    assert m["SILENT_FALLBACK_COUNT"] == "0"
    assert m["LLM_RUNTIME_FREE_TEXT"] == "NO"
    assert m["COMMIT"] == "NO"
    assert m["PROJECT_FINISHED"] == "NO"


def test_every_artifact_has_producer_and_evidence():
    for name in ("MAQAM_COREFERENCE_GATE_02.json", "MAQAM_ELLIPSIS_GATE_02.json",
                 "MAQAM_RANK_GATE_02.json", "MAQAM_CANONICAL_BLOCKER_02.json"):
        g = _j(name)
        assert g.get("producer_file") and g.get("evidence_file"), name
    sa = _j("MAQAM_SPEECH_ACT_GATE_02.json")
    for sub in ("text_alone", "example_context"):
        assert sa[sub].get("producer_file") and sa[sub].get("evidence_file"), sub


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
