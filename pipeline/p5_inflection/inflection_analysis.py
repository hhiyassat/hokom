#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/inflection_analysis.py

Inflectional analysis: given a surface (+ optional root/bab context),
produce an InflectionalAnalysis with features and lemma.

Key function:
  analyze_surface(surface, root, bab_id, form_family, wazn_id) → InflectionalAnalysis
"""
from __future__ import annotations
from typing import Optional

from .models import InflectionalAnalysis, Directive
from .feature_system import (
    extract_all_features,
    identify_tense,
    strip_diacritics,
    FATHA, KASRA, DAMMA, SUKUUN, SHADDA,
    WAW, YAA, ALIF, ALIF_MAKSURA,
)
from .verb_classifier import classify_root
from .surface_realization import BAB_VOWELS, WAZN_TO_PAST_VOWEL

# ──────────────────────────────────────────────────────────────────────────────
# Paradigm ID catalog
# ──────────────────────────────────────────────────────────────────────────────

PARADIGM_FOR_ROOT_CLASS = {
    'SOUND':           'SOUND_MUJARRAD',
    'HOLLOW_WAW':      'HOLLOW_WAW',
    'HOLLOW_YAA':      'HOLLOW_YAA',
    'DEFECTIVE_WAW':   'DEFECTIVE_WAW',
    'DEFECTIVE_YAA':   'DEFECTIVE_YAA',
    'ASSIMILATED_WAW': 'ASSIMILATED_WAW',
    'ASSIMILATED_YAA': 'ASSIMILATED_YAA',
    'GEMINATED':       'GEMINATED',
    'HAMZATED_C1':     'HAMZATED_C1',
    'HAMZATED_C2':     'HAMZATED_C2',
    'HAMZATED_C3':     'HAMZATED_C3',
    'LAFIF_MAFRUQ':    'LAFIF_MAFRUQ',
    'LAFIF_MAQRUN':    'LAFIF_MAQRUN',
    'AUGMENTED':       'AUGMENTED_II_X',
}


def _build_mujarrad_lemma(root: tuple, wazn_id: Optional[str],
                           bab_id: Optional[str]) -> Optional[str]:
    """
    Reconstruct the 3M_SG past (= lemma) from root + wazn/bab context.
    """
    if root is None or len(root) < 3:
        return None

    C1, C2, C3 = root[0], root[1], root[2]
    root_class = classify_root(root)

    # Determine past vowel on C2
    bab_v = BAB_VOWELS.get(bab_id) if bab_id else None
    Vp = bab_v[0] if bab_v else WAZN_TO_PAST_VOWEL.get(wazn_id, FATHA)

    if root_class == 'SOUND':
        return f'{C1}{FATHA}{C2}{Vp}{C3}{FATHA}'

    elif root_class in ('HOLLOW_WAW', 'HOLLOW_YAA'):
        # قَالَ / بَاعَ
        return f'{C1}{FATHA}{ALIF}{C3}{FATHA}'

    elif root_class == 'DEFECTIVE_WAW':
        # دَعَا
        return f'{C1}{FATHA}{C2}{FATHA}{ALIF}'

    elif root_class == 'DEFECTIVE_YAA':
        # رَمَى
        return f'{C1}{FATHA}{C2}{FATHA}{ALIF_MAKSURA}'

    elif root_class == 'ASSIMILATED_WAW':
        # وَعَدَ — C1=و stays in past
        return f'{C1}{FATHA}{C2}{Vp}{C3}{FATHA}'

    elif root_class == 'GEMINATED':
        # مَدَّ
        return f'{C1}{FATHA}{C2}{SHADDA}{FATHA}'

    elif root_class in ('HAMZATED_C1', 'HAMZATED_C2', 'HAMZATED_C3'):
        # قَرَأَ / أَكَلَ (mostly regular in past)
        return f'{C1}{FATHA}{C2}{Vp}{C3}{FATHA}'

    return f'{C1}{FATHA}{C2}{Vp}{C3}{FATHA}'


def _extract_imperfect_prefix_surface(surface: str) -> Optional[str]:
    """Return the imperfect prefix string (e.g., 'يَ', 'تَ', 'أَ', 'نَ')."""
    from .feature_system import _chars_and_diacs, IMPERFECT_PREFIX_LETTERS
    if not surface:
        return None
    pairs = _chars_and_diacs(surface)
    if not pairs:
        return None
    first_char, first_diacs = pairs[0]
    if first_char in IMPERFECT_PREFIX_LETTERS and FATHA in first_diacs:
        if len(pairs) >= 2 and SUKUUN in pairs[1][1]:
            return first_char + FATHA
    return None


def _extract_affixes(surface: str, tense: str) -> tuple:
    """Return the detected prefixes and suffixes as string tuples."""
    prefix = _extract_imperfect_prefix_surface(surface)
    prefixes = (prefix,) if prefix else ()
    suffixes = ()

    bare = strip_diacritics(surface)

    if tense == 'IMPERFECT':
        if bare.endswith('ون'):
            suffixes = ('ونَ',)
        elif bare.endswith('ين'):
            suffixes = ('ينَ',)
        elif bare.endswith('ان'):
            suffixes = ('انِ',)
        elif bare.endswith('وا'):
            suffixes = ('وا',)
        elif bare.endswith('ي') and not bare.endswith('اي'):
            suffixes = ('ي',)
        elif bare.endswith('ا') and not bare.endswith('نا') and not bare.endswith('وا'):
            suffixes = ('ا',)
        elif bare.endswith('ن') and not bare.endswith('ون') and not bare.endswith('ين') and not bare.endswith('ان'):
            suffixes = ('نَ',)
    elif tense == 'PAST':
        if bare.endswith('وا'):
            suffixes = ('وا',)
        elif bare.endswith('نا'):
            suffixes = ('نَا',)
        elif bare.endswith('تم') and surface.endswith('تُمَا'):
            suffixes = ('تُمَا',)
        elif bare.endswith('تم'):
            suffixes = ('تُمْ',)
        elif bare.endswith('ت') and surface.endswith('تْ'):
            suffixes = ('تْ',)
        elif bare.endswith('تا'):
            suffixes = ('تَا',)
        elif bare.endswith('ا') and not bare.endswith('نا') and not bare.endswith('وا') and not bare.endswith('تا'):
            suffixes = ('ا',)
        elif bare.endswith('ت') and surface.endswith('تَ'):
            suffixes = ('تَ',)
        elif bare.endswith('ت') and surface.endswith('تِ'):
            suffixes = ('تِ',)
        elif bare.endswith('ت') and surface.endswith('تُ'):
            suffixes = ('تُ',)
        elif bare.endswith('ن') and not bare.endswith('ان'):
            suffixes = ('نَ',)

    return prefixes, suffixes


def _detect_bab_from_imperfect(surface: str, root: Optional[tuple]) -> Optional[str]:
    """
    Detect the mujarrad bab from an imperfect surface by examining C2 vowel.
    Returns bab_id string or None.
    """
    if root is None or len(root) < 3:
        return None

    from .feature_system import _chars_and_diacs
    pairs = _chars_and_diacs(surface)
    if len(pairs) < 4:
        return None

    # In sound imperfect: prefix(0) + C1+sukuun(1) + C2+Vi(2) + C3+c3_diac(3)
    # pairs[0] = prefix (يَ/تَ/...)
    # pairs[1] = C1 with sukuun
    # pairs[2] = C2 with Vi
    # pairs[3] = C3 with c3_diac
    if len(pairs) >= 3:
        c2_pair = pairs[2]
        _, c2_diacs = c2_pair
        if DAMMA in c2_diacs:
            return 'BAB_I_NASARA'   # يَفْعُلُ
        elif KASRA in c2_diacs:
            return 'BAB_II_DARABA'  # يَفْعِلُ or BAB_VI_HASIBA
        elif FATHA in c2_diacs:
            # Could be BAB_III or BAB_IV — check C2 vowel in PAST context
            return 'BAB_III_FATAHA'  # most common

    return None


def analyze_surface(
    surface: str,
    root: Optional[tuple] = None,
    bab_id: Optional[str] = None,
    form_family: Optional[str] = None,
    wazn_id: Optional[str] = None,
    attached_pronoun_surface: Optional[str] = None,
) -> InflectionalAnalysis:
    """
    Analyze a verbal surface and return InflectionalAnalysis.

    surface: the verb surface to analyze (after pronoun stripping if applicable)
    root: canonical root tuple or None
    bab_id: Phase4B bab_id string or None
    form_family: augmented form family ('FORM_II' etc.) or None
    wazn_id: Phase4A wazn_id or None
    attached_pronoun_surface: the pronoun suffix that was stripped (or None)
    """
    if not surface:
        return InflectionalAnalysis(
            directive=Directive.DEFER,
            lemma_surface=None,
            features=(),
            paradigm_id=None,
            affixes=(),
            evidence_ids=('analyze:empty_surface',),
            trace_ids=(),
            residual_codes=('defer:inflection:empty_surface',),
        )

    # ── Feature extraction ────────────────────────────────────────────────────
    all_feats = extract_all_features(surface)
    tense  = all_feats.get('tense_aspect')
    mood   = all_feats.get('mood')
    voice  = all_feats.get('voice')
    person = all_feats.get('person')
    number = all_feats.get('number')
    gender = all_feats.get('gender')

    # ── Root class + paradigm ID ──────────────────────────────────────────────
    root_class  = classify_root(root) if root else None
    is_augmented = (
        root_class == 'AUGMENTED'
        or (form_family is not None and form_family.startswith('FORM_'))
        or (bab_id is not None and bab_id.startswith('BAB_FORM_'))
    )

    if is_augmented:
        paradigm_id = f'AUGMENTED_{form_family or "II_X"}'
    else:
        paradigm_id = PARADIGM_FOR_ROOT_CLASS.get(root_class) if root_class else None

    # ── Bab detection from imperfect surface ─────────────────────────────────
    detected_bab = bab_id
    if tense == 'IMPERFECT' and bab_id is None and not is_augmented:
        detected_bab = _detect_bab_from_imperfect(surface, root)

    # ── Lemma construction ────────────────────────────────────────────────────
    lemma = None
    if root and not is_augmented:
        lemma = _build_mujarrad_lemma(root, wazn_id, detected_bab or bab_id)

    # ── Affixes ───────────────────────────────────────────────────────────────
    prefixes, suffixes = _extract_affixes(surface, tense or 'PAST')
    all_affixes = prefixes + suffixes
    if attached_pronoun_surface:
        all_affixes = all_affixes + (attached_pronoun_surface,)

    # ── Build feature tuple ───────────────────────────────────────────────────
    features_dict = {
        'tense_aspect': tense,
        'mood': mood,
        'voice': voice,
        'person': person,
        'number': number,
        'gender': gender,
        'detected_bab': detected_bab,
        'root_class': root_class,
    }
    features_tuple = tuple(sorted(features_dict.items()))

    evidence_ids = ('analyze:surface_pattern_match',)
    if detected_bab and detected_bab != bab_id:
        evidence_ids = evidence_ids + ('analyze:bab_detected_from_imperfect',)

    return InflectionalAnalysis(
        directive=Directive.ACCEPT,
        lemma_surface=lemma,
        features=features_tuple,
        paradigm_id=paradigm_id,
        affixes=all_affixes,
        evidence_ids=evidence_ids,
        trace_ids=(),
        residual_codes=(),
    )
