#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_gold_oracle_compliance.py

HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01

Gold oracle compliance tests for the Ayat al-Dayn 129-token corpus.

These tests are written against the immutable gold manifest in
pipeline/governance/gold_manifest.py.  They are intentionally FAILING on
HEAD 40a3420 — each failure documents a known linguistic defect in the
current pipeline.  Do NOT skip or xfail them: they define the target state
for the next remediation pass.

GOVERNANCE_METADATA = {
    "mandate":  "HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01",
    "start_head": "40a3420",
    "protected": True,
    "amendment_required_to_modify": True,
}
# This variable is a constitutional marker.  Do not remove it.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

from hokom_pipeline import hokom

# Constitutional marker — must remain as executable Python, not in docstring.
GOVERNANCE_METADATA = {
    "mandate": "HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01",
    "start_head": "40a3420",
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


# ══════════════════════════════════════════════════════════════════════════════
# 1. WORD-CLASS MISCLASSIFICATION — أَجَلٍ [token 9]
# ══════════════════════════════════════════════════════════════════════════════

def test_ajal_is_ism_not_fi3l():
    """
    أَجَلٍ [token 9]: tanwin kasra marks a nominal.
    Gold: word_class = 'ISM'.
    Pipeline at 40a3420: word_class = 'FI3L', tense_aspect = 'PAST'.

    EXPECTED FAILURE at 40a3420.
    Fix: adjust morphology_path or word_class heuristics so tanwin suffix
    takes precedence over the verbal path.
    """
    r = hokom('أَجَلٍ')
    assert r.get('word_class') == 'ISM', (
        f"أَجَلٍ word_class={r.get('word_class')!r}: "
        "tanwin kasra nominal must be ISM, not FI3L. "
        f"tense_aspect={r.get('tense_aspect')!r}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. NUMBER MISMATCH — يَكُونَا [token 59]
# ══════════════════════════════════════════════════════════════════════════════

def test_yakuna_number_is_dual():
    """
    يَكُونَا [token 59]: dual alif suffix → number = DU (3MDU jussive).
    Pipeline at 40a3420: number = 'SG'.

    Root cause: attachment strips the وَنَا ending → feature extraction
    runs on truncated stem يَكَ → defaults to SG.

    EXPECTED FAILURE at 40a3420.
    """
    r = hokom('يَكُونَا')
    assert r.get('word_class') == 'FI3L', (
        f"يَكُونَا word_class={r.get('word_class')!r} — prerequisite")
    assert r.get('number') == 'DU', (
        f"يَكُونَا number={r.get('number')!r}: "
        "dual alif suffix يَكُونَا must give number='DU', not SG. "
        "Root cause: attachment/feature mismatch on hollow dual imperfect.")


# ══════════════════════════════════════════════════════════════════════════════
# 3. PERSON/NUMBER/GENDER MISMATCH — تَكُونَ [token 99]
# ══════════════════════════════════════════════════════════════════════════════

def test_takuna_is_3fs_subjunctive():
    """
    تَكُونَ [token 99]: إِلَّا أَنْ تَكُونَ تِجَارَةً
    Gold: person='3', number='SG', gender='F', mood='SUBJUNCTIVE'.
    Pipeline at 40a3420: person='2', number='PL', gender='M', mood='INDICATIVE'.

    Root cause: bare('تكون') ends with 'ون' → plural indicative path misfires.
    The ون here is the hollow verb stem (كون), not a plural marker.

    EXPECTED FAILURE at 40a3420.
    """
    r = hokom('تَكُونَ')
    assert r.get('word_class') == 'FI3L', (
        f"تَكُونَ word_class={r.get('word_class')!r} — prerequisite")
    person = r.get('person')
    number = r.get('number')
    gender = r.get('gender')
    assert person == '3' and number == 'SG' and gender == 'F', (
        f"تَكُونَ person={person!r} number={number!r} gender={gender!r}: "
        "إِلَّا أَنْ تَكُونَ تِجَارَةً = 3FS singular subjunctive. "
        "Pipeline at 40a3420 misfires on the ون in the hollow stem.")


# ══════════════════════════════════════════════════════════════════════════════
# 4. VOICE MISMATCH — تُدِيرُونَهَا [token 102]
# ══════════════════════════════════════════════════════════════════════════════

def test_tudirunaha_voice_is_active():
    """
    تُدِيرُونَهَا [token 102]: Form IV active imperfect 2MPL.
    Gold: voice = 'ACTIVE'.
    Pipeline at 40a3420: voice = 'PASSIVE'.

    Root cause: damma on تُ prefix triggers passive heuristic; the Form IV
    active override (doubled-C scan) does not fire for يُفْعِلُونَ pattern.

    EXPECTED FAILURE at 40a3420.
    """
    r = hokom('تُدِيرُونَهَا')
    assert r.get('word_class') == 'FI3L', (
        f"تُدِيرُونَهَا word_class={r.get('word_class')!r} — prerequisite")
    assert r.get('voice') == 'ACTIVE', (
        f"تُدِيرُونَهَا voice={r.get('voice')!r}: "
        "Form IV active imperfect must have voice='ACTIVE'. "
        "Pipeline at 40a3420 gives PASSIVE (damma prefix heuristic misfire).")


# ══════════════════════════════════════════════════════════════════════════════
# 5. UNCORRELATED AMBIGUITY — تَضِلَّ [token 68]
# ══════════════════════════════════════════════════════════════════════════════

def test_tadilla_ambiguity_is_correlated():
    """
    تَضِلَّ [token 68]: تَ prefix subjunctive → structurally ambiguous.
    Gold: two correlated candidates:
      (person='2', number='SG', gender='M', reading='2MS')
      (person='3', number='SG', gender='F', reading='3FS')

    Pipeline at 40a3420: person='2|3', gender='M' — the 3FS candidate
    (gender='F') is absent.  Ambiguity is NOT correlated.

    EXPECTED FAILURE at 40a3420.
    Fix: emit a correlated candidate bundle; do not encode as
    person='2|3' + gender='M' (one flat string + one gender losing 3FS).
    """
    r = hokom('تَضِلَّ')
    assert r.get('word_class') == 'FI3L'
    gender = r.get('gender') or ''
    # The 3FS candidate requires gender='F' to be present in the representation.
    assert 'F' in str(gender), (
        f"تَضِلَّ gender={gender!r}: "
        "correlated ambiguity requires the 3FS candidate (gender='F') "
        "to be expressed. Pipeline at 40a3420 gives gender='M' only.")


# ══════════════════════════════════════════════════════════════════════════════
# 6. UNCORRELATED AMBIGUITY + FORM MISMATCH — فَتُذَكِّرَ [token 70]
# ══════════════════════════════════════════════════════════════════════════════

def test_fatudhakkira_ambiguity_is_correlated():
    """
    فَتُذَكِّرَ [token 70]: Form II active imperfect with تُ prefix.
    Gold ambiguity candidates:
      (person='2', number='SG', gender='M', reading='2MS')
      (person='3', number='SG', gender='F', reading='3FS')

    Pipeline at 40a3420: gender='M' only — 3FS candidate absent.

    EXPECTED FAILURE at 40a3420.
    """
    r = hokom('فَتُذَكِّرَ')
    assert r.get('word_class') == 'FI3L'
    gender = r.get('gender') or ''
    assert 'F' in str(gender), (
        f"فَتُذَكِّرَ gender={gender!r}: "
        "correlated ambiguity: 3FS candidate (gender='F') must be present. "
        "Pipeline at 40a3420 gives gender='M' only.")


def test_fatudhakkira_cra_form_is_form_ii():
    """
    فَتُذَكِّرَ [token 70]: ذَكَّرَ = Form II (فَعَّلَ).
    Gold: cra_form_family = 'FORM_II'.
    Pipeline at 40a3420: cra_form_family = 'FORM_V'.
    FORM_REOPENING = FORBIDDEN → KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL.

    EXPECTED FAILURE at 40a3420.
    """
    r = hokom('فَتُذَكِّرَ')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    assert cra_form == 'FORM_II', (
        f"فَتُذَكِّرَ cra_form={cra_form!r}: "
        "ذَكَّرَ is Form II (فَعَّلَ). CRA at 40a3420 gives FORM_V. "
        "FORM_REOPENING=FORBIDDEN → KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL.")


# ══════════════════════════════════════════════════════════════════════════════
# 7. LIVE METRICS — required nonzero values
# ══════════════════════════════════════════════════════════════════════════════

def test_live_voice_mismatches_nonzero():
    """
    LIVE_VOICE_MISMATCHES must be > 0 at 40a3420.
    تُدِيرُونَهَا voice=PASSIVE vs gold ACTIVE is a counted mismatch.

    EXPECTED FAILURE if compute_live_metrics() omits LIVE_VOICE_MISMATCHES
    or reports 0.
    """
    mod = _load_demo()
    assert hasattr(mod, 'compute_live_metrics'), (
        "compute_live_metrics() not found in demo script")
    metrics = mod.compute_live_metrics()
    assert 'LIVE_VOICE_MISMATCHES' in metrics, (
        f"LIVE_VOICE_MISMATCHES key missing from metrics={list(metrics)}")
    assert metrics['LIVE_VOICE_MISMATCHES'] > 0, (
        f"LIVE_VOICE_MISMATCHES={metrics['LIVE_VOICE_MISMATCHES']}: "
        "تُدِيرُونَهَا voice=PASSIVE vs gold=ACTIVE must make this > 0.")


def test_live_png_mismatches_nonzero():
    """
    LIVE_PERSON_NUMBER_GENDER_MISMATCHES must be > 0 at 40a3420.
    يَكُونَا (SG vs DU) and تَكُونَ (2PL vs 3FS) are counted mismatches.

    EXPECTED FAILURE if metric is hard-coded to 0.
    """
    mod = _load_demo()
    metrics = mod.compute_live_metrics()
    assert metrics.get('LIVE_PERSON_NUMBER_GENDER_MISMATCHES', 0) > 0, (
        f"LIVE_PERSON_NUMBER_GENDER_MISMATCHES="
        f"{metrics.get('LIVE_PERSON_NUMBER_GENDER_MISMATCHES')!r}: "
        "يَكُونَا (SG→DU) and تَكُونَ (2PL→3FS) must make this > 0.")


def test_known_oos_form_residuals_key_and_value():
    """
    KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS (plural) must exist and be >= 3.
    Residuals: فَاكْتُبُوهُ (FORM_VIII→FORM_I), وَاتَّقُوا (FORM_II→FORM_VIII),
               فَتُذَكِّرَ (FORM_V→FORM_II).

    EXPECTED FAILURE if key name is singular KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL
    or value < 3.
    """
    mod = _load_demo()
    metrics = mod.compute_live_metrics()
    assert 'KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS' in metrics, (
        "KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS (plural) key missing. "
        f"Available: {list(metrics)}")
    assert metrics['KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS'] >= 3, (
        f"KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS="
        f"{metrics['KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS']}: "
        "must be >= 3 (فَاكْتُبُوهُ + وَاتَّقُوا + فَتُذَكِّرَ).")


def test_live_gold_token_mismatches_nonzero():
    """LIVE_GOLD_TOKEN_MISMATCHES must be > 0 (multiple defects at 40a3420)."""
    mod = _load_demo()
    metrics = mod.compute_live_metrics()
    assert metrics.get('LIVE_GOLD_TOKEN_MISMATCHES', 0) > 0, (
        f"LIVE_GOLD_TOKEN_MISMATCHES={metrics.get('LIVE_GOLD_TOKEN_MISMATCHES')!r} "
        "must be > 0 at 40a3420.")


# ══════════════════════════════════════════════════════════════════════════════
# 8. FORM_X EXPLICIT PROTECTION
# ══════════════════════════════════════════════════════════════════════════════

def test_form_x_protection_istashhhidu():
    """
    وَاسْتَشْهِدُوا [token 53]: Form X imperative.
    Gold: cra_form_family = 'FORM_X'.
    This is an EXPLICIT protection — incidental CRA success is not sufficient.
    """
    r = hokom('وَاسْتَشْهِدُوا')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    assert r.get('word_class') == 'FI3L', (
        f"وَاسْتَشْهِدُوا word_class={r.get('word_class')!r}")
    assert r.get('tense_aspect') == 'IMPERATIVE', (
        f"وَاسْتَشْهِدُوا tense={r.get('tense_aspect')!r}")
    assert cra_form == 'FORM_X', (
        f"وَاسْتَشْهِدُوا cra_form={cra_form!r}: "
        "Form X (اِسْتَفْعَلَ) imperative must have cra_form=FORM_X. "
        "Explicit protection — not incidental.")


def test_form_x_protection_istaghfiru_imperative():
    """
    اِسْتَغْفِرُوا: Form X imperative 2MPL.
    Gold: word_class='FI3L', tense_aspect='IMPERATIVE', cra_form='FORM_X'.
    Explicit FORM_X protection.
    """
    r = hokom('اِسْتَغْفِرُوا')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    assert r.get('word_class') == 'FI3L'
    assert r.get('tense_aspect') == 'IMPERATIVE'
    assert cra_form == 'FORM_X', (
        f"اِسْتَغْفِرُوا cra_form={cra_form!r}: FORM_X imperative explicit protection.")


def test_form_x_protection_yastghfiruna_imperfect():
    """
    يَسْتَغْفِرُونَ: Form X imperfect 3MPL.
    Gold: word_class='FI3L', tense_aspect='IMPERFECT', cra_form='FORM_X'.
    Pipeline at 40a3420: cra_form='FORM_I_IMPERFECT' (CRA misses اِسْتَ prefix).

    EXPECTED FAILURE at 40a3420.
    """
    r = hokom('يَسْتَغْفِرُونَ')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    assert r.get('word_class') == 'FI3L', (
        f"يَسْتَغْفِرُونَ word_class={r.get('word_class')!r}")
    assert r.get('tense_aspect') == 'IMPERFECT', (
        f"يَسْتَغْفِرُونَ tense={r.get('tense_aspect')!r}")
    assert cra_form == 'FORM_X', (
        f"يَسْتَغْفِرُونَ cra_form={cra_form!r}: "
        "Form X imperfect must have cra_form=FORM_X. "
        "Pipeline at 40a3420 gives FORM_I_IMPERFECT.")


def test_form_x_negative_control_sayaktubu():
    """
    سَيَكْتُبُونَ must NOT be classified as FORM_X.
    Negative control: Form I imperfect (كَتَبَ) with سَ future prefix.
    """
    r = hokom('سَيَكْتُبُونَ')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    # If wc is None (سَ prefix unsupported), that is a different defect.
    # But if cra gives a form, it must NOT be FORM_X.
    if cra_form is not None:
        assert cra_form != 'FORM_X', (
            f"سَيَكْتُبُونَ cra_form={cra_form!r}: "
            "Form I verb must never be classified as FORM_X.")


def test_form_x_negative_control_akramu():
    """
    أَكْرَمُوا must NOT be classified as FORM_X.
    Negative control: Form IV past 3MPL (أَكْرَمَ).
    """
    r = hokom('أَكْرَمُوا')
    cra = r.get('cra_result')
    cra_form = getattr(cra, 'form_family', None) if cra else None
    if cra_form is not None:
        assert cra_form != 'FORM_X', (
            f"أَكْرَمُوا cra_form={cra_form!r}: "
            "Form IV must never be classified as FORM_X.")


# ══════════════════════════════════════════════════════════════════════════════
# 9. GOLD MANIFEST INTEGRITY
# ══════════════════════════════════════════════════════════════════════════════

def test_gold_manifest_is_immutable():
    """
    All GoldRecord instances in CORPUS_GOLD must be frozen (immutable).
    Normal assignment must raise — not object.__setattr__ which bypasses frozen.
    """
    from pipeline.governance.gold_manifest import CORPUS_GOLD
    for rec in CORPUS_GOLD:
        raised = False
        try:
            rec.notes = 'mutation_attempt'  # normal assignment on frozen dataclass
        except Exception:
            raised = True
        assert raised, (
            f"GoldRecord for {rec.surface!r} is mutable — must be frozen=True.")


def test_gold_manifest_governance_metadata():
    """GOVERNANCE_METADATA must be present as executable Python in gold_manifest."""
    import ast
    import pathlib
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
    GoldRecords with ambiguity must use AmbiguityCandidate bundles, not
    flat strings like person='2|3'.
    """
    from pipeline.governance.gold_manifest import CORPUS_GOLD, AmbiguityCandidate
    for rec in CORPUS_GOLD:
        if rec.ambiguity_candidates:
            for cand in rec.ambiguity_candidates:
                assert isinstance(cand, AmbiguityCandidate), (
                    f"{rec.surface!r}: ambiguity_candidates must be "
                    f"AmbiguityCandidate instances, got {type(cand)}")
                # Each candidate must have all three fields
                assert '|' not in cand.person, (
                    f"{rec.surface!r}: candidate person={cand.person!r} "
                    "must not be a pipe-separated string — use separate candidates.")
                assert '|' not in cand.gender, (
                    f"{rec.surface!r}: candidate gender={cand.gender!r} "
                    "must not be a pipe-separated string.")
