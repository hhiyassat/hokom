#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06 — guard test.

Owner-ratified MAQAM_6 + reference policy (this nazila only) → maqam ACCEPT/CERTIFIED, reference
ratified, factual_claim born-but-deferred (a factual claim, NOT a ruling). Normative branch stays
unborn (no ratified normative source) so ḥukm/manāṭ/tanzīl/final answer are forbidden. No full-PDF
claim, no canonical opening, report follows the AR_05 format. Artifacts only.
"""
import json
import re
import pathlib

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REPORT = OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_MANAGER_REPORT_AR_06.html"
MATRIX = OUT / "MAQAM_SOURCE_FULL_MAQAM6_AND_REFERENCE_RATIFIED_CLOSURE_06_MATRIX.csv"
NODE_FILES = [
    "NAZILA_MAQAM_CLASSIFICATION_06.json", "NAZILA_REFERENCE_POLICY_06.json",
    "MAQAM_CANONICAL_INTEGRATION_CONTRACT_06.json", "HOKOM_TAAQOL_TYPED_ADAPTERS_READINESS_06.json",
    "NAZILA_FACTUAL_CLAIM_BIRTH_06.json", "NAZILA_NORMATIVE_SOURCE_BIRTH_06.json",
    "NAZILA_NORMATIVE_HUKM_BIRTH_06.json", "NAZILA_ILLAH_MANAT_BIRTH_06.json",
    "NAZILA_TANZIL_BIRTH_06.json", "NAZILA_ANSWER_AUDIT_BIRTH_06.json",
]


def _m():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def _t():
    return REPORT.read_text(encoding="utf-8")


def _node(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_pdf_status_matches_reality_no_full_claim():
    m = _m()
    assert m["SOURCE_2_FULL_PDF_AVAILABLE"] == "NO"
    assert m["SOURCE_2_PRESERVATION_STATUS"] == "OWNER_SUPPLIED_PDF_CANDIDATE_NOT_VERIFIED"
    assert m["SOURCE_2_FULL_PDF_SHA256_RECORDED"] == "NO"
    assert "FULL_PDF_PRESERVED" not in _t()


def test_maqam6_ratified_by_owner_not_text():
    m = _m()
    assert m["MAQAM_6_OWNER_RATIFIED"] == "YES"
    assert m["MAQAM_CLASSIFICATION_GATE_DECISION"] == "ACCEPT"
    assert m["MAQAM_CLASSIFICATION_BIRTH_STATUS"] == "CERTIFIED"
    assert m["MAQAM_ACCEPTED_BY_OWNER_DECISION_NOT_TEXT_ALONE"] == "YES"
    assert m["MAQAM_6_SCOPE"] == "THIS_NAZILA_ONLY"


def test_reference_policy_ratified():
    m = _m()
    assert m["REFERENCE_POLICY_OWNER_RATIFIED"] == "YES"
    assert m["ASSUMED_FACT_REFERENCE"] == "HYPOTHETICAL_MARKED_REFERENCE"
    assert m["REFERENCE_POLICY_DECISION_REQUIRED"] == "NO"


def test_factual_claim_born_only_with_propositional_content_and_not_normative():
    fc = _node("NAZILA_FACTUAL_CLAIM_BIRTH_06.json")
    assert fc["PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS"] == "YES"
    assert fc["FACTUAL_CLAIM_BIRTH_STATUS"] in ("BORN_BUT_DEFERRED", "CERTIFIED")
    assert fc["is_normative"] == "NO"
    assert fc["kind"] == "FACTUAL_NAZILA_PICTURE_CLAIM_ONLY"


def test_normative_source_unborn_without_ratified_source():
    ns = _node("NAZILA_NORMATIVE_SOURCE_BIRTH_06.json")
    assert ns["NORMATIVE_SOURCE_BIRTH_STATUS"] == "UNBORN"
    assert ns["NORMATIVE_SOURCE_BLOCKER"] == "NO_RATIFIED_NORMATIVE_SOURCE"
    assert _m()["NORMATIVE_SOURCE_BIRTH_STATUS"] == "UNBORN"


def test_normative_hukm_forbidden_without_source():
    nh = _node("NAZILA_NORMATIVE_HUKM_BIRTH_06.json")
    assert nh["NORMATIVE_HUKM_PRODUCED"] == "NO"
    assert nh["BIRTH_LICENSE"] == "DENIED_PARENT_UNBORN"
    assert nh["NORMATIVE_HUKM_BIRTH_STATUS"] == "FORBIDDEN_ANCESTOR_UNBORN"


def test_no_hukm_manat_tanzil_answer():
    m = _m()
    for k in ("NORMATIVE_HUKM_PRODUCED", "MANAT_PRODUCED", "TANZIL_PRODUCED",
              "FINAL_ANSWER_PRODUCED", "FINAL_ANSWER_ALLOWED", "FINAL_HUKM_ISSUED"):
        assert m[k] == "NO", k


def test_canonical_blocked_without_contract():
    assert _m()["CANONICAL_INTEGRATION_STATUS"] == "BLOCKED_WITH_CAUSE"
    assert _m()["TYPED_ADAPTERS_STATUS"] == "BLOCKED_WITH_CAUSE"


def test_manager_report_follows_ar05_format():
    t = _t()
    assert REPORT.exists() and REPORT.stat().st_size > 1000
    assert _m()["MANAGER_REPORT_CANONICAL_FORMAT"] == "MAQAM_AR_05_STYLE"
    nums = [int(x) for x in re.findall(r"<h2>(\d+)\.", t)]
    assert nums == list(range(1, 22)), nums
    # sentence + token table + ifadah + propositional present (AR_05 spirit)
    assert 'id="nazila-sentence"' in t and "مَاتَ مَلِكٌ عَنْ أُخْتٍ" in t
    for i in range(10):
        assert f">t00{i}<" in t, f"t00{i}"
    assert "IFADAH_PRODUCED_BY_CODE = YES" in t
    assert "PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS" in t


def test_report_states_owner_decision_scope_and_text_alone():
    t = _t()
    assert "THIS_NAZILA_ONLY" in t
    assert "النص وحده لم يثبت" in t or "TEXT_ALONE_INFERS_ISTIFTA = NO" in t
    assert "هنا توقفت سلسلة الولادة" in t


def test_every_node_has_full_fields_and_measured():
    for name in NODE_FILES:
        d = _node(name)
        for f in ("CAUSE", "CONDITIONS", "PREVENTERS", "VERDICT", "EVIDENCE", "PRODUCER_FILE", "RESIDUALS"):
            assert f in d and d[f] not in (None, ""), (name, f)
        assert d["measured"] == "MEASURED", name
    assert _m()["ASSERTED_NOT_MEASURED_COUNT"] == "0"
    assert _m()["SILENT_FALLBACK_COUNT"] == "0"


def test_no_external_refs_and_no_commit():
    assert not re.search(r"https?://|//cdn", _t())
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
