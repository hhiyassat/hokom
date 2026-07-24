#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/extended_gold_policy.py

HOKOM-GOLDEN-RULES-AND-LIVE-CLOSURE-CORRECTION-01

Supplementary gold expectations for fields that the immutable gold_manifest.py
CORPUS_GOLD does not constrain (word_class_subclass, canonical_root, and the
context-resolved cra_form_family / mood for specific tokens).

gold_manifest.py is IMMUTABLE — changing its GoldRecord definitions or
CORPUS_GOLD entries requires a CONSTITUTIONAL_AMENDMENT_ID.  This module adds
NEW, additive expectations keyed by token_index WITHOUT touching gold_manifest.
The live oracle (scripts/demo_ayat_al_dayn.py::compute_live_metrics) checks both
the immutable gold_manifest fields AND these extended expectations, so that
false-zero closure (a green gate while the CSV still carries defects) is
impossible.

Field policy labels (Golden Rule 14):
  REQUIRED_EXACT                 — pipeline value must equal the expectation
  REQUIRED_CORRELATED_CANDIDATES — pipeline must supply matching correlated
                                   AmbiguityCandidate bundles (not pipe strings)
  NOT_ASSERTED_WITH_REASON       — deliberately not checked (reason recorded)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass(frozen=True)
class ExtendedGoldExpectation:
    """
    Additive gold expectation for one token, checked alongside gold_manifest.

    Any field left as None / () is not checked by this expectation.
    """
    token_index: int
    surface: str

    # REQUIRED_EXACT expectations
    word_class_subclass: Optional[str] = None
    canonical_root: Optional[Tuple[str, ...]] = None   # compared to final_root
    cra_form_family: Optional[str] = None

    # Context-sensitive mood (validated in the sequential run, not raw hokom()).
    context_mood: Optional[str] = None

    # REQUIRED_CORRELATED_CANDIDATES: each entry is a (person, number, gender)
    # triple that MUST appear as a correlated bundle in the pipeline's
    # ambiguity_candidates.  Pipe-string person/gender does NOT satisfy this.
    require_correlated_candidates: Tuple[Tuple[str, str, str], ...] = ()

    rationale: str = ''


# ──────────────────────────────────────────────────────────────────────────────
# Extended expectations for the Ayat al-Dayn corpus
# ──────────────────────────────────────────────────────────────────────────────

EXTENDED_GOLD: Tuple[ExtendedGoldExpectation, ...] = (

    # Token 9 — أَجَلٍ: bare noun (wazn فَعَلَ), NOT an active participle.
    ExtendedGoldExpectation(
        token_index=9,
        surface='أَجَلٍ',
        word_class_subclass='LEXICAL_NOUN',
        rationale='أَجَل is فَعَل (bare-noun wazn FA_A_LA); ISM_FA3IL (فَاعِل) must '
                  'not be inferred without active-participle morphology.',
    ),

    # Token 46 — يَسْتَطِيعُ: أَوْ لَا يَسْتَطِيعُ — لَا is negative (نَافِيَة).
    ExtendedGoldExpectation(
        token_index=46,
        surface='يَسْتَطِيعُ',
        context_mood='INDICATIVE',
        rationale='لَا after أَوْ is negative (نَافِيَة), not prohibitive; the '
                  'context carrier must NOT inject JUSSIVE here.',
    ),

    # Token 68 — تَضِلَّ: 2MS / 3FS correlated ambiguity.
    ExtendedGoldExpectation(
        token_index=68,
        surface='تَضِلَّ',
        require_correlated_candidates=(('2', 'SG', 'M'), ('3', 'SG', 'F')),
        rationale='تَ-prefix imperfect is 2MS or 3FS; both correlated readings '
                  'must be represented (not pipe strings).',
    ),

    # Token 70 — فَتُذَكِّرَ: 2MS / 3FS correlated ambiguity + FORM_II.
    ExtendedGoldExpectation(
        token_index=70,
        surface='فَتُذَكِّرَ',
        cra_form_family='FORM_II',
        require_correlated_candidates=(('2', 'SG', 'M'), ('3', 'SG', 'F')),
        rationale='ذَكَّرَ = FORM_II (تُـ is inflectional person prefix, not FORM_V '
                  'derivational تَـ); 2MS/3FS correlated ambiguity.',
    ),

    # Token 102 — تُدِيرُونَهَا: FORM_IV hollow active, root دور.
    ExtendedGoldExpectation(
        token_index=102,
        surface='تُدِيرُونَهَا',
        canonical_root=('د', 'و', 'ر'),
        cra_form_family='FORM_IV',
        rationale='تُدِيرُ = أَدَارَ FORM_IV hollow active imperfect; root دور '
                  '(medial و), not دير; damma prefix + kasra C1 → FORM_IV active.',
    ),
)

EXTENDED_GOLD_BY_INDEX = {e.token_index: e for e in EXTENDED_GOLD}


def _norm_root(root) -> Tuple[str, ...]:
    """Normalize a root (tuple/list/str) to a tuple of radical strings."""
    if root is None:
        return ()
    if isinstance(root, (tuple, list)):
        return tuple(str(c) for c in root)
    return tuple(str(root))


def check_extended_expectation(
    expectation: ExtendedGoldExpectation,
    result: dict,
    context_mood: Optional[str] = None,
) -> dict:
    """
    Compare a live pipeline result dict against one ExtendedGoldExpectation.

    Returns a dict of per-category mismatch counts (0 or 1 each):
      subclass, canonical_root, cra_form_family, context_mood, uncorrelated_ambiguity
    plus 'any' = 1 if any category mismatched.
    """
    out = {
        'subclass': 0,
        'canonical_root': 0,
        'cra_form_family': 0,
        'context_mood': 0,
        'uncorrelated_ambiguity': 0,
    }

    # word_class_subclass — REQUIRED_EXACT
    if expectation.word_class_subclass is not None:
        if result.get('word_class_subclass') != expectation.word_class_subclass:
            out['subclass'] = 1

    # canonical_root (final_root) — REQUIRED_EXACT
    if expectation.canonical_root is not None:
        live_root = _norm_root(result.get('final_root') or result.get('canonical_root'))
        if live_root != _norm_root(expectation.canonical_root):
            out['canonical_root'] = 1

    # cra_form_family — REQUIRED_EXACT
    if expectation.cra_form_family is not None:
        cra = result.get('cra_result')
        cra_form = getattr(cra, 'form_family', None) if cra is not None else None
        if cra_form != expectation.cra_form_family:
            out['cra_form_family'] = 1

    # context_mood — REQUIRED_EXACT (validated with the injected sequential mood)
    if expectation.context_mood is not None:
        effective = context_mood if context_mood is not None else result.get('mood')
        if effective != expectation.context_mood:
            out['context_mood'] = 1

    # REQUIRED_CORRELATED_CANDIDATES — structured bundle must contain every
    # required (person, number, gender) triple.  Pipe strings do NOT satisfy.
    if expectation.require_correlated_candidates:
        live_bundles = set()
        for c in (result.get('ambiguity_candidates') or ()):
            if isinstance(c, dict):
                live_bundles.add((c.get('person'), c.get('number'), c.get('gender')))
            else:
                live_bundles.add((
                    getattr(c, 'person', None),
                    getattr(c, 'number', None),
                    getattr(c, 'gender', None),
                ))
        for required in expectation.require_correlated_candidates:
            if tuple(required) not in live_bundles:
                out['uncorrelated_ambiguity'] = 1
                break

    out['any'] = 1 if any(out[k] for k in (
        'subclass', 'canonical_root', 'cra_form_family',
        'context_mood', 'uncorrelated_ambiguity',
    )) else 0
    return out
