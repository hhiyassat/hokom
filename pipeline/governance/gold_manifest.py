#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/gold_manifest.py

HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01

Immutable protected gold manifest for the Ayat al-Dayn 129-token corpus.

Design rules:
  - Frozen dataclasses only — no mutable state.
  - Correlated ambiguity bundles: person/number/gender grouped per reading.
    Never use independent person='2|3' + gender='M' strings.
  - form_family_out_of_scope=True marks KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS
    (FORM_REOPENING = FORBIDDEN — cannot fix without constitutional amendment).
  - FORM_X_PROTECTION is explicit, not incidental.
  - Negative controls are declared alongside the protection set.
  - GOVERNANCE_METADATA must remain as executable Python.

Any modification to this file requires a CONSTITUTIONAL_AMENDMENT_ID.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Constitutional marker — do not remove or move to a docstring.
GOVERNANCE_METADATA = {
    "mandate": "HOKOM-LIVE-GOLD-ORACLE-AND-METRICS-CORRECTION-01",
    "start_head": "40a3420",
    "protected": True,
    "amendment_required_to_modify": True,
}


# ──────────────────────────────────────────────────────────────────────────────
# Correlated ambiguity bundle
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AmbiguityCandidate:
    """
    One reading within a structurally ambiguous imperfect surface.

    person / number / gender form a CORRELATED triple — they must not be
    split into independent strings.  E.g. تَ-prefix imperfect:
      AmbiguityCandidate('2', 'SG', 'M', '2MS')
      AmbiguityCandidate('3', 'SG', 'F', '3FS')
    NOT: person='2|3', gender='M'
    """
    person: str
    number: str
    gender: str
    reading: str   # human label: '2MS', '3FS', '3MDU', …


# ──────────────────────────────────────────────────────────────────────────────
# Gold record
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GoldRecord:
    """
    Immutable gold standard for one token in the Ayat al-Dayn corpus.

    Fields that are None are not checked (the gold does not constrain them).
    When ambiguity_candidates is non-empty, it overrides person/number/gender
    as the authoritative reading set.
    """
    token_index: int
    surface: str

    # ── Pipeline output expectations ─────────────────────────────────────────
    word_class: Optional[str] = None
    tense_aspect: Optional[str] = None
    voice: Optional[str] = None
    number: Optional[str] = None
    gender: Optional[str] = None
    person: Optional[str] = None
    mood: Optional[str] = None

    # ── Correlated ambiguity (overrides person/number/gender when non-empty) ─
    ambiguity_candidates: tuple = ()

    # ── CRA form family ───────────────────────────────────────────────────────
    cra_form_family: Optional[str] = None

    # ── Known form-family residual (FORM_REOPENING=FORBIDDEN) ────────────────
    form_family_out_of_scope: bool = False

    # ── Defect codes (active at start_head = 40a3420) ────────────────────────
    defect_codes: tuple = ()

    notes: str = ''


# ──────────────────────────────────────────────────────────────────────────────
# Corpus gold records
# ──────────────────────────────────────────────────────────────────────────────

CORPUS_GOLD: tuple[GoldRecord, ...] = (

    GoldRecord(
        token_index=9,
        surface='أَجَلٍ',
        word_class='ISM',
        defect_codes=('WORD_CLASS_MISCLASSIFICATION',),
        notes='Tanwin kasra marks a common noun; must be ISM not FI3L. '
              'Pipeline at 40a3420: wc=FI3L, tense=PAST.',
    ),

    GoldRecord(
        token_index=11,
        surface='فَاكْتُبُوهُ',
        word_class='FI3L',
        tense_aspect='IMPERATIVE',
        person='2',
        number='PL',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_I',
        form_family_out_of_scope=True,
        defect_codes=('KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL',),
        notes='كَتَبَ = Form I imperative with obj-enclitic ه. '
              'CRA at 40a3420 gives FORM_VIII (اِفْتَعَلَ misfire). '
              'FORM_REOPENING=FORBIDDEN.',
    ),

    GoldRecord(
        token_index=53,
        surface='وَاسْتَشْهِدُوا',
        word_class='FI3L',
        tense_aspect='IMPERATIVE',
        person='2',
        number='PL',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_X',
        notes='Form X (اِسْتَفْعَلَ) imperative 2MPL. '
              'FORM_X explicit protection — incidental CRA success is not sufficient.',
    ),

    GoldRecord(
        token_index=59,
        surface='يَكُونَا',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        person='3',
        number='DU',
        gender='M',
        defect_codes=('NUMBER_MISMATCH',),
        notes='يَكُونَا: 3MDU jussive (dual alif suffix). '
              'Pipeline at 40a3420: number=SG (attachment strips وَنَا → host يَكَ → '
              'feature extraction on truncated stem).',
    ),

    GoldRecord(
        token_index=68,
        surface='تَضِلَّ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        # Correlated ambiguity — do NOT split into person='2|3' + gender='M'
        ambiguity_candidates=(
            AmbiguityCandidate(person='2', number='SG', gender='M', reading='2MS'),
            AmbiguityCandidate(person='3', number='SG', gender='F', reading='3FS'),
        ),
        defect_codes=('UNCORRELATED_AMBIGUITY',),
        notes='تَ prefix subjunctive: 2MS (أنتَ تَضِلَّ) or 3FS (هي تَضِلَّ). '
              'Pipeline at 40a3420: person=2|3 but gender=M only — '
              'the 3FS candidate (gender=F) is absent.',
    ),

    GoldRecord(
        token_index=70,
        surface='فَتُذَكِّرَ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        ambiguity_candidates=(
            AmbiguityCandidate(person='2', number='SG', gender='M', reading='2MS'),
            AmbiguityCandidate(person='3', number='SG', gender='F', reading='3FS'),
        ),
        cra_form_family='FORM_II',
        form_family_out_of_scope=True,
        defect_codes=('UNCORRELATED_AMBIGUITY', 'KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL'),
        notes='ذَكَّرَ = Form II imperfect. '
              'CRA at 40a3420 gives FORM_V. '
              'FORM_REOPENING=FORBIDDEN. '
              'gender=M only; 3FS candidate missing.',
    ),

    GoldRecord(
        token_index=99,
        surface='تَكُونَ',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        person='3',
        number='SG',
        gender='F',
        mood='SUBJUNCTIVE',
        defect_codes=('PERSON_NUMBER_GENDER_MISMATCH',),
        notes='إِلَّا أَنْ تَكُونَ تِجَارَةً: "unless it be a commercial transaction" '
              '— 3FS subjunctive. Pipeline at 40a3420: person=2, number=PL, gender=M '
              '(bare تكون endswith ون → plural path misfires).',
    ),

    GoldRecord(
        token_index=102,
        surface='تُدِيرُونَهَا',
        word_class='FI3L',
        tense_aspect='IMPERFECT',
        voice='ACTIVE',
        person='2',
        number='PL',
        gender='M',
        defect_codes=('VOICE_MISMATCH',),
        notes='Form IV active imperfect 2MPL (تُفْعِلُونَ pattern). '
              'Pipeline at 40a3420: voice=PASSIVE (damma on taa prefix '
              'triggers passive heuristic, Form IV active override missing).',
    ),

    GoldRecord(
        token_index=122,
        surface='وَاتَّقُوا',
        word_class='FI3L',
        tense_aspect='IMPERATIVE',
        person='2',
        number='PL',
        gender='M',
        voice='ACTIVE',
        cra_form_family='FORM_VIII',
        form_family_out_of_scope=True,
        defect_codes=('KNOWN_OUT_OF_SCOPE_FORM_RESIDUAL',),
        notes='اتَّقَى = Form VIII imperative (اِفْتَعَلَ, assimilation ت+و→تّ). '
              'CRA at 40a3420 gives FORM_II. '
              'FORM_REOPENING=FORBIDDEN.',
    ),
)

# ── Gold index for O(1) lookup ────────────────────────────────────────────────
GOLD_BY_INDEX: dict[int, GoldRecord] = {r.token_index: r for r in CORPUS_GOLD}
GOLD_BY_SURFACE: dict[str, tuple[GoldRecord, ...]] = {}
for _r in CORPUS_GOLD:
    GOLD_BY_SURFACE.setdefault(_r.surface, ())
    GOLD_BY_SURFACE[_r.surface] = GOLD_BY_SURFACE[_r.surface] + (_r,)


# ──────────────────────────────────────────────────────────────────────────────
# FORM_X explicit protection set
# ──────────────────────────────────────────────────────────────────────────────
# Incidental CRA success is not protection.
# These surfaces must pass form-level checks independently of whether
# they happen to appear in the live corpus run.

@dataclass(frozen=True)
class FormXRecord:
    surface: str
    expected_word_class: str
    expected_tense_aspect: str
    expected_cra_form: str
    notes: str = ''


FORM_X_PROTECTION: tuple[FormXRecord, ...] = (
    FormXRecord(
        surface='سَيَسْتَغْفِرُونَ',
        expected_word_class='FI3L',
        expected_tense_aspect='IMPERFECT',
        expected_cra_form='FORM_X',
        notes='سَ future prefix + Form X imperfect. Pipeline at 40a3420: wc=None '
              '(سَ prefix unsupported → UNJUSTIFIED_WORD_CLASS_NOT_OPENED).',
    ),
    FormXRecord(
        surface='يَسْتَغْفِرُونَ',
        expected_word_class='FI3L',
        expected_tense_aspect='IMPERFECT',
        expected_cra_form='FORM_X',
        notes='Form X imperfect 3MPL. Pipeline at 40a3420: cra_form=FORM_I_IMPERFECT '
              '(CRA does not recognise اِسْتَ as Form X marker).',
    ),
    FormXRecord(
        surface='اِسْتَغْفِرُوا',
        expected_word_class='FI3L',
        expected_tense_aspect='IMPERATIVE',
        expected_cra_form='FORM_X',
        notes='Form X imperative 2MPL. CRA at 40a3420: FORM_X ✓ (passing).',
    ),
    FormXRecord(
        surface='وَاسْتَشْهِدُوا',
        expected_word_class='FI3L',
        expected_tense_aspect='IMPERATIVE',
        expected_cra_form='FORM_X',
        notes='Form X imperative 2MPL (token 53 in corpus). '
              'CRA at 40a3420: FORM_X ✓ (passing).',
    ),
)

# Negative controls: these must NOT be classified as FORM_X.
FORM_X_NEGATIVE_CONTROLS: tuple[tuple[str, str], ...] = (
    ('سَيَكْتُبُونَ', 'FORM_I'),   # Form I imperfect; يَ prefix with سَ
    ('أَكْرَمُوا',    'FORM_IV'),  # Form IV past 3MPL
)

FORM_X_PROTECTION_INDEX: dict[str, FormXRecord] = {
    r.surface: r for r in FORM_X_PROTECTION
}


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def active_defect_surfaces() -> frozenset[str]:
    """Return surfaces with declared defects at start_head."""
    return frozenset(
        r.surface for r in CORPUS_GOLD if r.defect_codes
    )


def known_oos_surfaces() -> frozenset[str]:
    """Return surfaces with known out-of-scope form residuals."""
    return frozenset(
        r.surface for r in CORPUS_GOLD if r.form_family_out_of_scope
    )
