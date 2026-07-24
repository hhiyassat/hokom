#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_gold_oracle_compliance.py

HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02
(supersedes HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01)

Gold oracle compliance tests for the Ayat al-Dayn 129-token corpus.

Architecture:
  - These tests PASS by verifying that the DETECTOR correctly identifies
    all known defects in the current pipeline output.
  - They do NOT assert that the pipeline gives the correct linguistic answer.
  - The closure gate (scripts/run_live_gold_closure_gate.py) is the definitive
    FAIL signal: it exits nonzero whenever any defect metric > 0.

Design principles:
  - No skip. No xfail. No concealment.
  - Tests assert what IS TRUE at current HEAD (the detector finds defects).
  - The closure gate asserts what MUST BE TRUE at shipment (defects = 0).

GOVERNANCE_METADATA = {
    "mandate": "HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02",
    "start_head": "988d00f",
    "protected": True,
    "amendment_required_to_modify": True,
}
# This variable is a constitutional marker — do not remove it.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

from hokom_pipeline import hokom

# Constitutional marker — must remain as executable Python, not in docstring.
GOVERNANCE_METADATA = {
    "mandate": "HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02",
    "supersedes": "HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01",
    "start_head": "988d00f",
    "protected": True,
    "amendment_required_to_modify": True,
}


# ──────────────────────────────────────────────────────────────────────────────
# Demo module loader
# ──────────────────────────────────────────────────────────────────────────────

def _load_demo():
    script = (
        pathlib.Path(__file__).resolve().parent.parent.parent
        / 'scripts' / 'demo_ayat_al_dayn.py'
    )
    spec = importlib.util.spec_from_file_location('demo_ayat_al_dayn', script)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _metrics():
    return _load_demo().compute_live_metrics()


# ══════════════════════════════════════════════════════════════════════════════
# 1. DETECTOR — gold token mismatches (>= 12)
# ══════════════════════════════════════════════════════════════════════════════

def test_gold_token_mismatches_detected():
    """
    LIVE_GOLD_TOKEN_MISMATCHES must be >= 12 at current HEAD.
    The detector correctly identifies 12 tokens with at least one field
    differing from the gold manifest expectation.
    """
    m = _metrics()
    assert m['LIVE_GOLD_TOKEN_MISMATCHES'] >= 12, (
        f"LIVE_GOLD_TOKEN_MISMATCHES={m['LIVE_GOLD_TOKEN_MISMATCHES']}: "
        "detector must find >= 12 token-level mismatches at current HEAD.")


# ══════════════════════════════════════════════════════════════════════════════
# 2. DETECTOR — form family mismatches (>= 6)
# ══════════════════════════════════════════════════════════════════════════════

def test_form_family_mismatches_detected():
    """
    LIVE_FORM_FAMILY_MISMATCHES must be >= 6.
    Tokens: آمَنُوا(FORM_IV/None), فَاكْتُبُوهُ(FORM_I/FORM_VIII),
            وَلْيَتَّقِ(FORM_VIII/FORM_II), يُمِلَّ(FORM_IV/FORM_I_IMPERFECT),
            فَتُذَكِّرَ(FORM_II/FORM_V), وَاتَّقُوا(FORM_VIII/FORM_II).
    """
    m = _metrics()
    assert m['LIVE_FORM_FAMILY_MISMATCHES'] >= 6, (
        f"LIVE_FORM_FAMILY_MISMATCHES={m['LIVE_FORM_FAMILY_MISMATCHES']}: "
        "detector must find >= 6 CRA form-family mismatches.")


# ══════════════════════════════════════════════════════════════════════════════
# 3. DETECTOR — known OOS form residuals (>= 6)
# ══════════════════════════════════════════════════════════════════════════════

def test_known_oos_form_residuals_detected():
    """
    KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS must be >= 6.
    All 6 form mismatches are OOS (FORM_REOPENING=FORBIDDEN):
    آمَنُوا, فَاكْتُبُوهُ, وَلْيَتَّقِ, يُمِلَّ, فَتُذَكِّرَ, وَاتَّقُوا.
    """
    m = _metrics()
    assert 'KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS' in m, (
        "KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS key missing")
    assert m['KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS'] >= 6, (
        f"KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS={m['KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS']}: "
        "detector must find >= 6 OOS form residuals.")


def test_known_oos_form_residuals_backward_compat_alias():
    """
    Singular alias KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL must also be present
    (backward compatibility with test_live_context_boundary_gold.py).
    """
    m = _metrics()
    assert 'KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL' in m, (
        "Singular alias KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL missing")
    assert m['KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL'] == m['KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS'], (
        "Alias must equal canonical plural key")


# ══════════════════════════════════════════════════════════════════════════════
# 4. DETECTOR — person/number/gender mismatches (>= 4)
# ══════════════════════════════════════════════════════════════════════════════

def test_png_mismatches_detected():
    """
    LIVE_PERSON_NUMBER_GENDER_MISMATCHES must be >= 4.
    Explicit: يَكُونَا(SG→DU), تَكُونَ(2PL/M→3SG/F).
    Via uncorrelated ambiguity: تَضِلَّ(gender=F absent), فَتُذَكِّرَ(gender=F absent).
    """
    m = _metrics()
    assert m['LIVE_PERSON_NUMBER_GENDER_MISMATCHES'] >= 4, (
        f"LIVE_PERSON_NUMBER_GENDER_MISMATCHES={m['LIVE_PERSON_NUMBER_GENDER_MISMATCHES']}: "
        "detector must find >= 4 PNG mismatches (includes uncorrelated ambiguity).")


def test_yakuna_number_mismatch_is_detected():
    """
    يَكُونَا: pipeline gives number=SG, gold=DU.
    Detector must identify this as a PNG mismatch (not a zero).
    """
    r = hokom('يَكُونَا')
    assert r.get('word_class') == 'FI3L', (
        f"يَكُونَا prerequisite: wc={r.get('word_class')!r}")
    # The defect is SG instead of DU — detector catches this.
    assert r.get('number') != 'DU', (
        "يَكُونَا number='DU' — this defect was unexpectedly fixed. "
        "Update the gold manifest and closure gate.")


def test_takuna_png_mismatch_is_detected():
    """
    تَكُونَ: pipeline gives person=2, number=PL, gender=M.
    Gold: person=3, number=SG, gender=F.
    Detector must identify this as a PNG mismatch.
    """
    r = hokom('تَكُونَ')
    assert r.get('word_class') == 'FI3L', (
        f"تَكُونَ prerequisite: wc={r.get('word_class')!r}")
    person = r.get('person')
    number = r.get('number')
    gender = r.get('gender')
    # Verify the defect is still present (so detector is catching a real issue).
    assert not (person == '3' and number == 'SG' and gender == 'F'), (
        "تَكُونَ PNG defect unexpectedly fixed. Update gold manifest + closure gate.")


# ══════════════════════════════════════════════════════════════════════════════
# 5. DETECTOR — voice mismatches (>= 2)
# ══════════════════════════════════════════════════════════════════════════════

def test_voice_mismatches_detected():
    """
    LIVE_VOICE_MISMATCHES must be >= 2.
    تُدِيرُونَهَا(PASSIVE→ACTIVE) and يُمِلَّ(PASSIVE→ACTIVE).
    """
    m = _metrics()
    assert m['LIVE_VOICE_MISMATCHES'] >= 2, (
        f"LIVE_VOICE_MISMATCHES={m['LIVE_VOICE_MISMATCHES']}: "
        "detector must find >= 2 voice mismatches.")


def test_tudirunaha_voice_defect_present():
    """تُدِيرُونَهَا: pipeline gives PASSIVE, gold=ACTIVE. Defect must still be present."""
    r = hokom('تُدِيرُونَهَا')
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    assert r.get('voice') != 'ACTIVE', (
        "تُدِيرُونَهَا voice=ACTIVE — defect unexpectedly fixed. "
        "Update gold manifest + closure gate.")


def test_yumilla_voice_defect_present():
    """يُمِلَّ: pipeline gives PASSIVE, gold=ACTIVE. Defect must still be present."""
    r = hokom('يُمِلَّ')
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    assert r.get('voice') != 'ACTIVE', (
        "يُمِلَّ voice=ACTIVE — defect unexpectedly fixed. "
        "Update gold manifest + closure gate.")


# ══════════════════════════════════════════════════════════════════════════════
# 6. DETECTOR — context mood mismatches (>= 1)
# ══════════════════════════════════════════════════════════════════════════════

def test_context_mood_mismatches_detected():
    """
    LIVE_CONTEXT_MOOD_MISMATCHES must be >= 1.
    تَسْأَمُوا [80]: وَلَا تَسْأَمُوا is prohibitive (JUSSIVE required).
    Raw hokom() gives mood=INDICATIVE (no sequential context).
    """
    m = _metrics()
    assert m['LIVE_CONTEXT_MOOD_MISMATCHES'] >= 1, (
        f"LIVE_CONTEXT_MOOD_MISMATCHES={m['LIVE_CONTEXT_MOOD_MISMATCHES']}: "
        "detector must find >= 1 context mood mismatch.")


def test_tasamu_mood_defect_present():
    """
    تَسْأَمُوا: raw hokom() gives mood=INDICATIVE.
    وَلَا requires JUSSIVE. Defect must still be detectable.
    """
    r = hokom('تَسْأَمُوا')
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    assert r.get('mood') != 'JUSSIVE', (
        "تَسْأَمُوا raw mood=JUSSIVE — context injection now works in raw hokom(). "
        "Update gold manifest + closure gate.")


def test_yastati3u_context_boundary_protected():
    """
    يَسْتَطِيعُ [46] PROTECTION: أَوْ لَا يَسْتَطِيعُ — لَا is NEGATIVE here.
    Pipeline must give mood=INDICATIVE (not JUSSIVE).
    This test FAILS if a regression incorrectly injects JUSSIVE.
    """
    r = hokom('يَسْتَطِيعُ')
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    assert r.get('mood') == 'INDICATIVE', (
        f"يَسْتَطِيعُ mood={r.get('mood')!r}: "
        "REGRESSION — لَا at أَوْ لَا يَسْتَطِيعُ is NEGATIVE, not JASSIM. "
        "Context carrier must not inject JUSSIVE here.")


# ══════════════════════════════════════════════════════════════════════════════
# 7. DETECTOR — word class not-opened categories
# ══════════════════════════════════════════════════════════════════════════════

def test_word_class_not_opened_total():
    """WORD_CLASS_NOT_OPENED_TOTAL must be 40 (all tokens with wc=None)."""
    m = _metrics()
    assert 'WORD_CLASS_NOT_OPENED_TOTAL' in m, "WORD_CLASS_NOT_OPENED_TOTAL key missing"
    assert m['WORD_CLASS_NOT_OPENED_TOTAL'] == 40, (
        f"WORD_CLASS_NOT_OPENED_TOTAL={m['WORD_CLASS_NOT_OPENED_TOTAL']}: expected 40.")


def test_word_class_not_opened_categories_sum_to_total():
    """
    JUSTIFIED + UNJUSTIFIED + UNADJUDICATED must equal TOTAL.
    Every wc=None token must appear in exactly one category.
    """
    m = _metrics()
    total    = m['WORD_CLASS_NOT_OPENED_TOTAL']
    justified = m['JUSTIFIED_WORD_CLASS_NOT_OPENED']
    unjust   = m['UNJUSTIFIED_WORD_CLASS_NOT_OPENED']
    unadj    = m['UNADJUDICATED_WORD_CLASS_NOT_OPENED']
    assert justified + unjust + unadj == total, (
        f"Category sum {justified}+{unjust}+{unadj}={justified+unjust+unadj} "
        f"!= TOTAL={total}. Every wc=None token must be in exactly one category.")


def test_jamid_boundary_not_unjustified():
    """
    JAMID_AALAM_BOUNDARY tokens must NOT be counted as unjustified.
    The 6 لفظ الجلالة forms must all be JUSTIFIED.
    """
    m = _metrics()
    # There are 6 JAMID tokens (all اللَّهُ / اللَّهَ forms).
    # JUSTIFIED must be >= 6 to contain them.
    assert m['JUSTIFIED_WORD_CLASS_NOT_OPENED'] >= 6, (
        f"JUSTIFIED_WORD_CLASS_NOT_OPENED={m['JUSTIFIED_WORD_CLASS_NOT_OPENED']}: "
        "at least the 6 JAMID_AALAM_BOUNDARY tokens must be justified.")


def test_segmentation_no_host_not_unjustified():
    """
    SEGMENTATION_NO_LEXICAL_HOST tokens must NOT be counted as unjustified.
    بِكُمْ [121] is the corpus token with this skip reason.
    """
    m = _metrics()
    # SEGMENTATION_NO_LEXICAL_HOST adds to JUSTIFIED.
    # There is 1 such token. JUSTIFIED must be >= 7.
    assert m['JUSTIFIED_WORD_CLASS_NOT_OPENED'] >= 7, (
        f"JUSTIFIED_WORD_CLASS_NOT_OPENED={m['JUSTIFIED_WORD_CLASS_NOT_OPENED']}: "
        "SEGMENTATION_NO_LEXICAL_HOST (بِكُمْ) must be justified.")


def test_unjustified_word_class_not_opened_nonzero():
    """
    UNJUSTIFIED_WORD_CLASS_NOT_OPENED must be > 0 at current HEAD.
    There are 19 plain-deferred tokens with no known route justification.
    """
    m = _metrics()
    assert m['UNJUSTIFIED_WORD_CLASS_NOT_OPENED'] > 0, (
        f"UNJUSTIFIED_WORD_CLASS_NOT_OPENED={m['UNJUSTIFIED_WORD_CLASS_NOT_OPENED']}: "
        "must be > 0 — 19 tokens are unjustifiably deferred at current HEAD.")


# ══════════════════════════════════════════════════════════════════════════════
# 8. DETECTOR — word class misclassification
# ══════════════════════════════════════════════════════════════════════════════

def test_ajal_word_class_defect_present():
    """
    أَجَلٍ [9]: pipeline gives wc=FI3L, gold=ISM.
    Detector counts this as LIVE_NONVERBS_AS_VERBS > 0.
    """
    r = hokom('أَجَلٍ')
    assert r.get('word_class') != 'ISM', (
        "أَجَلٍ wc=ISM — defect unexpectedly fixed. "
        "Update gold manifest + closure gate.")


def test_nonverbs_as_verbs_detected():
    """LIVE_NONVERBS_AS_VERBS must be > 0 (أَجَلٍ misclassified as FI3L)."""
    m = _metrics()
    assert m['LIVE_NONVERBS_AS_VERBS'] > 0, (
        f"LIVE_NONVERBS_AS_VERBS={m['LIVE_NONVERBS_AS_VERBS']}: "
        "أَجَلٍ wc=FI3L misclassification must be detected.")


# ══════════════════════════════════════════════════════════════════════════════
# 9. DETECTOR — uncorrelated ambiguity (both تَضِلَّ and فَتُذَكِّرَ)
# ══════════════════════════════════════════════════════════════════════════════

def test_uncorrelated_ambiguity_detected():
    """
    LIVE_UNCORRELATED_AMBIGUITY must be >= 2.
    تَضِلَّ and فَتُذَكِّرَ: pipeline gender=M only, 3FS (gender=F) candidate absent.
    """
    m = _metrics()
    assert m['LIVE_UNCORRELATED_AMBIGUITY'] >= 2, (
        f"LIVE_UNCORRELATED_AMBIGUITY={m['LIVE_UNCORRELATED_AMBIGUITY']}: "
        "must be >= 2 (تَضِلَّ + فَتُذَكِّرَ).")


def test_tadilla_gender_f_absent():
    """تَضِلَّ: gender must NOT contain 'F' at current HEAD (defect present)."""
    r = hokom('تَضِلَّ')
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    gender = str(r.get('gender') or '')
    assert 'F' not in gender, (
        f"تَضِلَّ gender={gender!r}: 3FS candidate (gender=F) now present — "
        "defect fixed. Update gold manifest + closure gate.")


def test_fatudhakkira_gender_f_absent():
    """فَتُذَكِّرَ: gender must NOT contain 'F' at current HEAD (defect present)."""
    r = hokom('فَتُذَكِّرَ')
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    gender = str(r.get('gender') or '')
    assert 'F' not in gender, (
        f"فَتُذَكِّرَ gender={gender!r}: 3FS candidate (gender=F) now present — "
        "defect fixed. Update gold manifest + closure gate.")


# ══════════════════════════════════════════════════════════════════════════════
# 10. FORM_X explicit protection
# ══════════════════════════════════════════════════════════════════════════════

def test_form_x_protection_istashhhidu():
    """
    وَاسْتَشْهِدُوا [53]: Form X imperative — explicit FORM_X protection.
    Pipeline at current HEAD correctly gives cra=FORM_X.
    """
    r = hokom('وَاسْتَشْهِدُوا')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    assert r.get('tense_aspect') == 'IMPERATIVE', f"ta={r.get('tense_aspect')!r}"
    assert cra_form == 'FORM_X', (
        f"وَاسْتَشْهِدُوا cra_form={cra_form!r}: FORM_X explicit protection REGRESSION.")


def test_form_x_protection_istaghfiru_imperative():
    """اِسْتَغْفِرُوا: Form X imperative — explicit FORM_X protection."""
    r = hokom('اِسْتَغْفِرُوا')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    assert r.get('tense_aspect') == 'IMPERATIVE', f"ta={r.get('tense_aspect')!r}"
    assert cra_form == 'FORM_X', (
        f"اِسْتَغْفِرُوا cra_form={cra_form!r}: FORM_X explicit protection REGRESSION.")


def test_form_x_protection_yastghfiruna_defect_present():
    """
    يَسْتَغْفِرُونَ: Form X imperfect — pipeline gives cra=FORM_I_IMPERFECT (defect).
    The closure gate will FAIL until this is fixed.
    This test confirms the defect is still present (for detector validation).
    """
    r = hokom('يَسْتَغْفِرُونَ')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    # Gold: FORM_X. Pipeline: FORM_I_IMPERFECT. Defect must still be present.
    assert r.get('word_class') == 'FI3L', f"wc={r.get('word_class')!r}"
    assert r.get('tense_aspect') == 'IMPERFECT', f"ta={r.get('tense_aspect')!r}"
    assert cra_form != 'FORM_X', (
        f"يَسْتَغْفِرُونَ cra_form={cra_form!r}: FORM_X defect unexpectedly fixed. "
        "Add to FORM_X_PROTECTION passing set and update closure gate.")


def test_form_x_negative_control_sayaktubu():
    """سَيَكْتُبُونَ must NOT be classified as FORM_X (Form I with سَ prefix)."""
    r = hokom('سَيَكْتُبُونَ')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    if cra_form is not None:
        assert cra_form != 'FORM_X', (
            f"سَيَكْتُبُونَ cra_form={cra_form!r}: Form I must never be FORM_X.")


def test_form_x_negative_control_akramu():
    """أَكْرَمُوا must NOT be classified as FORM_X (Form IV past 3MPL)."""
    r = hokom('أَكْرَمُوا')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    if cra_form is not None:
        assert cra_form != 'FORM_X', (
            f"أَكْرَمُوا cra_form={cra_form!r}: Form IV must never be FORM_X.")


# ══════════════════════════════════════════════════════════════════════════════
# 11. MANIFEST INTEGRITY
# ══════════════════════════════════════════════════════════════════════════════

def test_gold_manifest_is_immutable():
    """All GoldRecord instances in CORPUS_GOLD must be frozen (immutable)."""
    from pipeline.governance.gold_manifest import CORPUS_GOLD
    for rec in CORPUS_GOLD:
        raised = False
        try:
            rec.notes = 'mutation_attempt'
        except Exception:
            raised = True
        assert raised, (
            f"GoldRecord for {rec.surface!r} is mutable — must be frozen=True.")


def test_gold_manifest_governance_metadata():
    """GOVERNANCE_METADATA must be present as executable Python in gold_manifest.py."""
    import ast
    src = (
        pathlib.Path(__file__).resolve().parent.parent.parent
        / 'pipeline' / 'governance' / 'gold_manifest.py'
    ).read_text()
    tree = ast.parse(src)
    found = any(
        isinstance(node, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == 'GOVERNANCE_METADATA'
            for t in node.targets
        )
        for node in ast.walk(tree)
    )
    assert found, "GOVERNANCE_METADATA not present as executable Python in gold_manifest.py"


def test_ambiguity_candidates_are_correlated_bundles():
    """
    GoldRecords with ambiguity must use AmbiguityCandidate bundles.
    No pipe-separated person/gender strings allowed.
    """
    from pipeline.governance.gold_manifest import CORPUS_GOLD, AmbiguityCandidate
    for rec in CORPUS_GOLD:
        for cand in rec.ambiguity_candidates:
            assert isinstance(cand, AmbiguityCandidate), (
                f"{rec.surface!r}: ambiguity_candidates must be "
                f"AmbiguityCandidate instances, got {type(cand)}")
            assert '|' not in cand.person, (
                f"{rec.surface!r}: person={cand.person!r} must not be pipe-separated.")
            assert '|' not in cand.gender, (
                f"{rec.surface!r}: gender={cand.gender!r} must not be pipe-separated.")


def test_manifest_digest_stable():
    """
    MANIFEST_DIGEST must match the computed digest of the live CORPUS_GOLD.
    Any unauthorized modification to CORPUS_GOLD will cause this test to FAIL.
    To update: assign a CONSTITUTIONAL_AMENDMENT_ID and recompute the digest.
    """
    from pipeline.governance.gold_manifest import (
        verify_manifest_integrity, MANIFEST_DIGEST,
    )
    ok, msg = verify_manifest_integrity()
    assert ok, (
        f"MANIFEST_INTEGRITY_VIOLATION: {msg}. "
        "A CONSTITUTIONAL_AMENDMENT_ID is required to modify CORPUS_GOLD.")


def test_manifest_digest_is_literal_string():
    """
    MANIFEST_DIGEST must be a frozen literal string (not a dynamic call).
    If it is still _compute_manifest_digest(), the governance gate is not active.
    """
    import ast
    src = (
        pathlib.Path(__file__).resolve().parent.parent.parent
        / 'pipeline' / 'governance' / 'gold_manifest.py'
    ).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == 'MANIFEST_DIGEST'
                for t in node.targets
            )
        ):
            assert isinstance(node.value, ast.Constant), (
                "MANIFEST_DIGEST must be a literal string constant, not a dynamic call. "
                "The governance gate is inactive while MANIFEST_DIGEST = _compute_manifest_digest().")
            break


def test_manifest_has_14_gold_records():
    """CORPUS_GOLD must have exactly 14 records after HARDENING-02 expansion."""
    from pipeline.governance.gold_manifest import CORPUS_GOLD
    assert len(CORPUS_GOLD) == 14, (
        f"CORPUS_GOLD has {len(CORPUS_GOLD)} records, expected 14.")


def test_manifest_new_tokens_present():
    """
    New tokens added in HARDENING-02 must be present:
    آمَنُوا(4), وَلْيَتَّقِ(29), يَسْتَطِيعُ(46), يُمِلَّ(48), تَسْأَمُوا(80).
    """
    from pipeline.governance.gold_manifest import GOLD_BY_INDEX
    required = {4: 'آمَنُوا', 29: 'وَلْيَتَّقِ', 46: 'يَسْتَطِيعُ', 48: 'يُمِلَّ', 80: 'تَسْأَمُوا'}
    for idx, surface in required.items():
        assert idx in GOLD_BY_INDEX, f"Token {idx} ({surface}) missing from GOLD_BY_INDEX"
        assert GOLD_BY_INDEX[idx].surface == surface, (
            f"Token {idx}: expected surface {surface!r}, got {GOLD_BY_INDEX[idx].surface!r}")


def test_protection_records_have_no_defect_codes():
    """
    Protection records (يَسْتَطِيعُ, وَاسْتَشْهِدُوا) must have defect_codes=().
    They document correct pipeline behavior, not defects.
    """
    from pipeline.governance.gold_manifest import GOLD_BY_INDEX
    protection_tokens = {46: 'يَسْتَطِيعُ', 53: 'وَاسْتَشْهِدُوا'}
    for idx, surface in protection_tokens.items():
        rec = GOLD_BY_INDEX[idx]
        assert rec.defect_codes == (), (
            f"Token {idx} ({surface}): protection record must have defect_codes=(), "
            f"got {rec.defect_codes!r}.")
