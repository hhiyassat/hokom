#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CREATE_MISSING_CODE_EXECUTED_MANAGER_REPORT_AR_07 — creation guard test.

Proves the official file TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html exists, is code/artifact
generated, follows the round-06 ten-section order, keeps the binding notions distinct, and shows
manāṭ/tanzīl/final-answer as FORBIDDEN_ANCESTOR_UNBORN (not born). Artifacts only; no ruling; no score
change.
"""
import re
import pathlib

GEN = pathlib.Path("/Users/husseinhiyassat/hokom/output/taaqol_nazila_matrix_generated")
RM = GEN / "roadmap"
REPORT = RM / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"
REPORT06 = RM / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_06.html"
MATRIX = GEN / "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07_MATRIX.csv"
SENTENCE = "مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا."


def _t():
    assert REPORT.exists()
    return REPORT.read_text(encoding="utf-8")


def _matrix():
    return {r.split(",", 1)[0]: r.split(",", 1)[1]
            for r in MATRIX.read_text(encoding="utf-8").splitlines() if "," in r}


def test_file_exists_nonempty_exact_name():
    assert REPORT.exists() and REPORT.stat().st_size > 500
    assert REPORT.name == "TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"


def test_no_external_refs():
    assert not re.search(r"https?://|//cdn", _t())


def test_sentence_verbatim():
    m = re.search(r'<div class="sent" id="nazila-sentence">(.*?)</div>', _t(), flags=re.S)
    assert m and m.group(1) == SENTENCE
    for w in SENTENCE.replace("،", " ").replace(".", " ").split():
        assert w in _t(), w


def test_h2_order_matches_06():
    ref = re.findall(r"<h2>(.*?)</h2>", REPORT06.read_text(encoding="utf-8"))
    new = re.findall(r"<h2>(.*?)</h2>", _t())
    assert len(ref) == 10 and new == ref, (new, ref)


def test_source_and_no_demo():
    t = _t()
    assert "REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY" in t
    assert "ILLUSTRATIVE_DEMO = NO" in t
    assert "LLM_FREE_TEXT_OUTPUT = NO" in t


def test_binding_notions_distinct():
    t = _t()
    assert "LEXICAL_DAL_MADLUL_BINDING_COUNT = 9" in t
    assert "ARABIC_TEXT_MADLUL_LICENSED_COUNT = 1" in t
    assert "ARABIC_TEXT_MADLUL_BOUND_COUNT = 0" in t
    assert "NO_ARABIC_TEXT_BOUND_WITHOUT_RATIFIED_GATE = YES" in t
    assert "TOKENS_WITH_MADLUL_RECORD = 10" in t
    assert "DOCUMENT = 80.0" in t and "DAL_MADLUL = 90.0" in t


def test_manat_tanzil_answer_forbidden_not_born():
    t = _t()
    assert "MANAT_BIRTH_STATUS = FORBIDDEN_ANCESTOR_UNBORN" in t
    assert "TANZIL_BIRTH_STATUS = FORBIDDEN_ANCESTOR_UNBORN" in t
    assert "FINAL_ANSWER_BIRTH_STATUS = FORBIDDEN_ANCESTOR_UNBORN" in t
    assert "TANZIL_CANDIDATE" not in t
    assert "ولادة المناط ممنوعة" in t


def test_no_final_ruling():
    t = _t()
    assert "FINAL_HUKM_ISSUED = NO" in t
    assert "FINAL_ANSWER_ALLOWED = NO" in t
    assert "FINAL_HUKM_ISSUED=YES" not in t.replace(" ", "")
    assert "FINAL_ANSWER_ALLOWED=YES" not in t.replace(" ", "")


def test_fractal_birth_markers():
    t = _t()
    for s in ("IFADAH_DOES_NOT_DIRECTLY_BIRTH_CLAIM = YES",
              "PROPOSITIONAL_CONTENT_ARTIFACT_EXISTS = YES",
              "MAQAM_CLASSIFICATION_GATE_DECISION = DEFER",
              "MAQAM_6_PROPOSED = MASALA_MUSAWWARA_LIL_ISTIFTA",
              "MAQAM_6_OWNER_RATIFIED = NO",
              "FACTUAL_CLAIM_BIRTH_STATUS = FORBIDDEN_PARENT_DEFERRED",
              "NORMATIVE_HUKM_BIRTH_GATE_EVALUATION = BORN",
              "NORMATIVE_HUKM_GATE_DECISION = DEFER",
              "NORMATIVE_HUKM_CHILD_CANDIDATE = UNBORN",
              "BIRTH_LICENSE = DENIED_PENDING_EVIDENCE",
              "GATE_DECISION_NOT_CHILD_BIRTH_STATUS = YES"):
        assert s in t, s


def test_matrix_flags():
    m = _matrix()
    assert m["REPORT_07_CREATED"] == "YES"
    assert m["REPORT_07_PATH"] == "roadmap/TAAQOL_NAZILA_CODE_EXECUTED_MANAGER_REPORT_AR_07.html"
    for k in ("SCORE_CHANGED", "RUNTIME_CHANGED", "GATES_CHANGED",
              "RESULTS_08_09_10_CHANGED", "COMMIT"):
        assert m[k] == "NO", k
    assert m["PROJECT_FINISHED"] == "NO"
    assert m["HTML_EXTERNAL_REFS"] == "0"


def test_t003_source_corrected_not_missing_owner():
    t = _t()
    # the corrected label must be shown; the stale artifact value only as provenance, never as the claim
    assert "ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED" in t
    assert "القيمة الخام" in t  # provenance note wrapping the raw artifact value
    m = _matrix()
    assert m["T003_MADLUL_SOURCE_DISPLAY"] == "ARABIC_TEXT_EXISTS_BUT_BINDING_GATE_NOT_RATIFIED"
    assert m["T003_MADLUL_SOURCE_RAW_ARTIFACT"] == "APPROVED_MADLUL_SOURCE_MISSING_OWNER_PENDING"


def test_t009_word_class_shown_as_artifact_anomaly():
    t = _t()
    assert "ARTIFACT_ANOMALY" in t
    assert "فعل ماضٍ" in t
    assert "HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv" in t
    m = _matrix()
    assert m["T009_WORD_CLASS_ARTIFACT_ANOMALY"] == "YES"
    assert m["ARTIFACT_NEVER_OVERWRITTEN"] == "YES"


def test_report_is_reproducible_from_generator():
    """Proof the file is generator-output (not hand-written): re-run the generator to a temp path
    and assert it is byte-identical to the on-disk official report."""
    import subprocess
    import tempfile
    gen = pathlib.Path("/Users/husseinhiyassat/hokom/scripts/generate_taaqol_code_executed_manager_report_ar_07.py")
    assert gen.exists()
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d) / "regen.html"
        mout = pathlib.Path(d) / "regen_matrix.csv"
        r = subprocess.run(["python3", str(gen), "--manager-report-ar-07-out", str(out),
                            "--matrix-out", str(mout)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert out.read_text(encoding="utf-8") == REPORT.read_text(encoding="utf-8")


def test_matrix_strict_two_columns():
    rows = [r for r in MATRIX.read_text(encoding="utf-8").splitlines() if r]
    assert rows[0] == "field,value"
    for r in rows:
        assert len(r.split(",")) == 2, r
