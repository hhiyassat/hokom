#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/phase5_orchestrator.py

Phase 5 — Paradigm/Inflection orchestrator.

project_inflection_with_licensing() is the main entry point.
It takes the surface + context from prior phases and returns a Phase5Result.

Architecture:
  1. Check applicability (verbal morphology path required)
  2. Classify root → root class → paradigm candidate
  3. Analyze surface → inflectional features
  4. Build InflectionalForm
  5. Return Phase5Result

Security constraints (inherited from task spec):
  • Never modifies Phase4 DTOs
  • No new fields on existing frozen dataclasses
  • Works only in /Users/husseinhiyassat/hokom
"""
from __future__ import annotations
from typing import Optional

from .models import (
    InflectionalForm, ParadigmCandidate, Phase5Result,
    Directive, RootClass, Tense, Mood, Voice,
)
from .verb_classifier import classify_root
from .inflection_analysis import analyze_surface, PARADIGM_FOR_ROOT_CLASS
from .feature_system import extract_all_features


# ──────────────────────────────────────────────────────────────────────────────
# Morphology paths that admit verbal inflection
# ──────────────────────────────────────────────────────────────────────────────
VERBAL_PATHS = frozenset([
    'verbal_root_path',
    'ambiguous_morphology_path',  # could be verbal
])

# Non-verbal paths — Phase5 returns NOT_APPLICABLE
NON_VERBAL_PATHS = frozenset([
    'nominal_morphology_path',
    'no_morphology_path',
])


# ──────────────────────────────────────────────────────────────────────────────
# NOT_APPLICABLE sentinel
# ──────────────────────────────────────────────────────────────────────────────

def _not_applicable(surface: str) -> Phase5Result:
    return Phase5Result(
        initial_directive=Directive.NOT_APPLICABLE,
        final_directive=Directive.NOT_APPLICABLE,
        paradigm_candidate=None,
        inflectional_form=None,
        source_path='not_applicable',
        evidence_ids=('p5:not_applicable:non_verbal_path',),
        trace_ids=(),
        residual_codes=(),
    )


def _defer_result(surface: str, reason: str) -> Phase5Result:
    return Phase5Result(
        initial_directive=Directive.DEFER,
        final_directive=Directive.DEFER,
        paradigm_candidate=None,
        inflectional_form=None,
        source_path='defer',
        evidence_ids=(),
        trace_ids=(),
        residual_codes=(f'defer:p5:{reason}',),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main orchestrator
# ──────────────────────────────────────────────────────────────────────────────

def project_inflection_with_licensing(
    surface: str,
    root: Optional[tuple] = None,
    bab_id: Optional[str] = None,
    form_family: Optional[str] = None,
    wazn_id: Optional[str] = None,
    morphology_path: Optional[str] = None,
    phase4a_result=None,
    phase4b_result=None,
    attachment=None,
) -> Phase5Result:
    """
    Project inflectional analysis onto a surface form.

    Parameters
    ----------
    surface        : Normalized surface string (post-attachment stripping if applicable).
    root           : Canonical root tuple (C1, C2, C3) or None.
    bab_id         : Phase4B bab_id (e.g., 'BAB_I_NASARA') or None.
    form_family    : Augmented form family ('FORM_II' etc.) or None.
    wazn_id        : Phase4A wazn_id ('FA_A_LA' etc.) or None.
    morphology_path: Pre-root morphology classification.
    phase4a_result : Phase4AResult (not modified).
    phase4b_result : Phase4BResult (not modified).
    attachment     : TokenAnalysis from mabniyat_attachment (not modified).

    Returns
    -------
    Phase5Result
    """
    if not surface:
        return _defer_result(surface, 'empty_surface')

    # ── 1. Check morphology path applicability ────────────────────────────────
    if morphology_path in NON_VERBAL_PATHS:
        return _not_applicable(surface)

    # ── 2. Extract surface features (always possible) ─────────────────────────
    all_feats = extract_all_features(surface)
    tense  = all_feats.get('tense_aspect')
    mood   = all_feats.get('mood')
    voice  = all_feats.get('voice', 'ACTIVE')
    person = all_feats.get('person')
    number = all_feats.get('number')
    gender = all_feats.get('gender')

    # If surface shows no verbal features AND we have a non-verbal morphology path,
    # return NOT_APPLICABLE. (Nominal path already caught above.)
    # For ambiguous path: allow processing.

    # ── 3. Root classification ────────────────────────────────────────────────
    root_class  = classify_root(root) if root else None
    is_augmented = (
        root_class == RootClass.AUGMENTED
        or (form_family is not None and form_family.startswith('FORM_'))
        or (bab_id is not None and bab_id.startswith('BAB_FORM_'))
    )

    if is_augmented:
        paradigm_id_str = f'AUGMENTED_{form_family or "II_X"}'
        source_path = 'augmented_paradigm'
    elif root_class is not None:
        paradigm_id_str = PARADIGM_FOR_ROOT_CLASS.get(root_class, 'SOUND_MUJARRAD')
        source_path = ('sound_paradigm' if root_class == RootClass.SOUND
                       else 'weak_paradigm')
    else:
        paradigm_id_str = None
        source_path = 'surface_only'

    # ── 4. Run inflection analysis ────────────────────────────────────────────
    # Handle attached pronoun context
    attached_pronoun_surface = None
    if attachment is not None:
        try:
            seg_v = attachment.segmentation_verdict
            if seg_v == 'SEGMENTED' and attachment.attached_mabniyat:
                # The surface we received was already stripped of pronouns
                # Record what was attached
                attached_pronoun_surface = ''.join(
                    sp.surface_matched for sp in attachment.attached_mabniyat
                )
        except AttributeError:
            pass

    analysis = analyze_surface(
        surface=surface,
        root=root,
        bab_id=bab_id,
        form_family=form_family,
        wazn_id=wazn_id,
        attached_pronoun_surface=attached_pronoun_surface,
    )

    # ── 5. Build ParadigmCandidate ────────────────────────────────────────────
    paradigm_candidate = None
    if paradigm_id_str is not None:
        paradigm_candidate = ParadigmCandidate(
            paradigm_id=paradigm_id_str,
            root_class=root_class or 'UNKNOWN',
            form_id=form_family,
            confidence='HIGH' if root_class else 'MEDIUM',
            evidence_ids=('p5:root_class_classified',),
            trace_ids=(),
            residual_codes=(),
        )

    # ── 6. Build InflectionalForm ─────────────────────────────────────────────
    inflection_type = 'FINITE_VERB' if tense in ('PAST', 'IMPERFECT') else (
        'IMPERATIVE_VERB' if tense == 'IMPERATIVE' else 'NOT_APPLICABLE'
    )

    prefixes_tuple: tuple = analysis.affixes[:len(analysis.affixes) - len(
        [a for a in analysis.affixes if len(a) <= 2 and any(c in 'يتأن' for c in a)]
    )]
    # Simpler: just use what analysis gives us
    prefixes_from_analysis = tuple(
        a for a in analysis.affixes
        if len(a) <= 2 and any(c in 'يتأن' for c in a) and len(a) >= 1
    )
    suffixes_from_analysis = tuple(
        a for a in analysis.affixes
        if a not in prefixes_from_analysis
    )

    inflectional_form = InflectionalForm(
        surface=surface,
        lemma_surface=analysis.lemma_surface,
        canonical_root=root,
        wazn_id=wazn_id,
        form_id=form_family,
        part_of_speech='VERB',

        tense_aspect=tense,
        mood=mood,
        voice=voice,

        person=person,
        number=number,
        gender=gender,

        inflection_type=inflection_type,
        suffixes=suffixes_from_analysis,
        prefixes=prefixes_from_analysis,

        removed_affixes=analysis.affixes,
        restored_vowels=(),
        paradigm_rule_ids=(paradigm_id_str,) if paradigm_id_str else (),

        evidence_ids=analysis.evidence_ids,
        trace_ids=analysis.trace_ids,
        residual_codes=analysis.residual_codes,
    )

    # ── 7. Determine final directive ──────────────────────────────────────────
    final_directive = analysis.directive

    return Phase5Result(
        initial_directive=Directive.ACCEPT,
        final_directive=final_directive,
        paradigm_candidate=paradigm_candidate,
        inflectional_form=inflectional_form,
        source_path=source_path,
        evidence_ids=analysis.evidence_ids,
        trace_ids=analysis.trace_ids,
        residual_codes=analysis.residual_codes,
    )
