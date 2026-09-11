#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAQAM_MANAGER_REPORT_LITERAL_NAZILA_07_PARITY_FIX_05 — functional-parity guard test.

Report 05 must reach functional parity with the nazila-07 manager report: 18 ordered h2 sections, the
nazila sentence, a ten-token table (t000..t009 from real artifacts), an IFADAH stage row + section, a
propositional/factual section, and a traceability table with NO empty artifact/test cells. No full-PDF
claim, no ruling, external refs = 0, byte-reproducible. Artifacts only.
"""
import re
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path("/Users/husseinhiyassat/hokom")
OUT = ROOT / "output" / "taaqol_maqam_foundation_generated"
REPORT = OUT / "MAQAM_SOURCE_2_FULL_PRESERVATION_MANAGER_REPORT_AR_05.html"
MATRIX = OUT / "MAQAM_MANAGER_REPORT_LITERAL_NAZILA_07_PARITY_FIX_05_MATRIX.csv"
GEN = ROOT / "scripts" / "taaqol_maqam_foundation" / "manager_report_parity_nazila07_05.py"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."


def _t():
    assert REPORT.exists()
    return REPORT.read_text(encoding="utf-8")


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_report_exists_nonempty():
    assert REPORT.exists() and REPORT.stat().st_size > 1000


def test_18_h2_sections_in_order():
    nums = [int(x) for x in re.findall(r"<h2>(\d+)\.", _t())]
    assert nums == list(range(1, 19)), nums


def test_sentence_section_literal():
    t = _t()
    m = re.search(r'<div class="sent" id="nazila-sentence">(.*?)</div>', t, flags=re.S)
    assert m and m.group(1) == SENTENCE


def test_token_table_has_ten_tokens():
    t = _t()
    assert _matrix()["HAS_TOKEN_TABLE"] == "YES"
    assert _matrix()["TOKEN_TABLE_SOURCE_MISSING"] == "NO"
    for i in range(10):
        assert f">t00{i}<" in t, f"t00{i}"


def test_stage_table_has_ifadah_prop_factual():
    t = _t()
    for row in ("IFADAH", "PROPOSITIONAL_CONTENT", "FACTUAL_CLAIM", "LINGUISTIC_ANALYSIS",
                "MADLUL_RECORD_AND_BINDING", "NORMATIVE_HUKM", "MANAT", "TANZIL", "FINAL_ANSWER"):
        assert row in t, row


def test_ifadah_section_present():
    t = _t()
    assert "حالة الإفادة: منتجة بالكود أم لا؟" in t
    assert "IFADAH_PRODUCED_BY_CODE = YES" in t
    assert "IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM = YES" in t


def test_propositional_and_factual_status():
    t = _t()
    assert "PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS" in t
    assert "FACTUAL_CLAIM_BIRTH_STATUS" in t and "FORBIDDEN_PARENT_DEFERRED" in t
    assert "REFERENCE_POLICY_DECISION_REQUIRED" in t


def test_traceability_no_empty_artifact_or_test_cells():
    m = _matrix()
    assert m["TRACEABILITY_ARTIFACT_COLUMNS_FILLED"] == "YES"
    assert m["TRACEABILITY_TEST_COLUMNS_FILLED"] == "YES"
    assert m["ASSERTED_NOT_MEASURED_COUNT"] == "0"
    t = _t()
    # each named requirement row must carry its artifact + test path
    for art in ("MAQAM_COREFERENCE_GATE_02.json", "MAQAM_ELLIPSIS_GATE_02.json",
                "MAQAM_RANK_GATE_02.json", "MAQAM_SPEECH_ACT_GATE_02.json",
                "MAQAM_CANONICAL_BLOCKER_02.json"):
        assert art in t, art
        assert (OUT / art).exists(), art
    assert "test_taaqol_maqam_deferred_consumers_02.py" in t
    assert (ROOT / "tests" / "test_taaqol_maqam_deferred_consumers_02.py").exists()


def test_no_full_pdf_claim():
    assert "FULL_PDF_PRESERVED" not in _t()


def test_no_ruling_or_final_answer():
    t = _t()
    for s in ("NORMATIVE_HUKM_PRODUCED = NO", "MANAT_PRODUCED = NO", "TANZIL_PRODUCED = NO",
              "FINAL_ANSWER_PRODUCED = NO", "CANONICAL_INTEGRATION_STATUS = BLOCKED_WITH_CAUSE"):
        assert s in t, s


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _t())


def test_report_reproducible_byte_identical():
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d) / "r.html"
        mout = pathlib.Path(d) / "m.csv"
        r = subprocess.run(["python3", str(GEN), "--report-out", str(out), "--matrix-out", str(mout)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert out.read_text(encoding="utf-8") == REPORT.read_text(encoding="utf-8")


def test_matrix_flags_and_strict():
    m = _matrix()
    assert m["MANAGER_REPORT_05_MATCHES_NAZILA_07_FUNCTIONAL_LAYOUT"] == "YES"
    assert m["HAS_IFADAH_SECTION"] == "YES" and m["HAS_IFADAH_STAGE_ROW"] == "YES"
    assert m["HAS_PROPOSITIONAL_CONTENT_SECTION"] == "YES" and m["HAS_FACTUAL_CLAIM_STATUS"] == "YES"
    assert m["REPORT_REPRODUCIBLE_FROM_GENERATOR"] == "YES"
    for k in ("RUNTIME_CHANGED", "SCORE_CHANGED", "GATES_CHANGED",
              "VENDOR_CHANGED_BY_THIS_ROUND", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
