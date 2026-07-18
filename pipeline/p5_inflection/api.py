#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/api.py — Public Phase 5 Inflection API

Two primary entry points:

  analyze_verb(surface, root, bab_id, form_family) → dict
    Analyze a verbal surface and return features as a dict.

  generate_verb(root, bab_id, tense, mood, voice, person, number, gender,
                form_family) → str | None
    Generate a verbal surface form from root + features.
"""
from __future__ import annotations
from typing import Optional

from .inflection_analysis import analyze_surface
from .surface_realization import realize_form, BAB_VOWELS, WAZN_TO_PAST_VOWEL
from .verb_classifier import classify_root


def analyze_verb(
    surface: str,
    root: Optional[tuple] = None,
    bab_id: Optional[str] = None,
    form_family: Optional[str] = None,
    wazn_id: Optional[str] = None,
) -> dict:
    """
    Public analysis API.

    Returns a dict with keys:
      tense_aspect, mood, voice, person, number, gender,
      lemma_surface, paradigm_id, root_class,
      directive, residual_codes
    """
    analysis = analyze_surface(
        surface=surface,
        root=root,
        bab_id=bab_id,
        form_family=form_family,
        wazn_id=wazn_id,
    )
    feats = analysis.features_dict
    return {
        'tense_aspect':  feats.get('tense_aspect'),
        'mood':          feats.get('mood'),
        'voice':         feats.get('voice'),
        'person':        feats.get('person'),
        'number':        feats.get('number'),
        'gender':        feats.get('gender'),
        'root_class':    feats.get('root_class'),
        'detected_bab':  feats.get('detected_bab'),
        'lemma_surface': analysis.lemma_surface,
        'paradigm_id':   analysis.paradigm_id,
        'directive':     analysis.directive,
        'residual_codes': analysis.residual_codes,
    }


def generate_verb(
    root: tuple,
    bab_id: Optional[str] = None,
    tense: str = 'PAST',
    mood: str = 'INDICATIVE',
    voice: str = 'ACTIVE',
    person: str = '3',
    number: str = 'SG',
    gender: str = 'M',
    form_family: Optional[str] = None,
    wazn_id: Optional[str] = None,
) -> Optional[str]:
    """
    Public generation API.

    Returns the surface string or None if generation is not supported
    (DEFER_REQUIRED cases).
    """
    root_class = classify_root(root) if root else 'SOUND'

    # Override root_class for augmented
    if form_family and form_family.startswith('FORM_'):
        root_class = 'AUGMENTED'
    elif bab_id and bab_id.startswith('BAB_FORM_'):
        root_class = 'AUGMENTED'

    surface, confidence, _residuals = realize_form(
        root=root,
        bab_id=bab_id,
        root_class=root_class,
        tense=tense,
        mood=mood,
        voice=voice,
        person=person,
        number=number,
        gender=gender,
        wazn_id=wazn_id,
    )

    if confidence == 'DEFER_REQUIRED':
        return None
    return surface
