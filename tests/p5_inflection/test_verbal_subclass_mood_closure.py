#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p5_inflection/test_verbal_subclass_mood_closure.py

HOKOM-AYAT-AL-DAYN-VERBAL-SUBCLASS-MOOD-AND-DEFERRED-ROUTING-CLOSURE-01

Gold-based closure tests for:
  1. Imperatives (must not be classified as PAST or DEFERRED)
  2. Imperfects (must not be classified as PAST)
  3. Deferred tokens that now have sufficient evidence
  4. Mood from syntactic/governing particles
  5. Non-verbs that must not be classified as FI3L

Invariants:
  KNOWN_GOLD_TOKEN_MISMATCHES         = 0
  IMPERATIVES_AS_PAST                 = 0
  IMPERATIVES_DEFERRED                = 0
  IMPERFECTS_AS_PAST                  = 0
  MOOD_CONTEXT_MISMATCHES             = 0
  NONVERBS_AS_VERBS                   = 0
"""
from __future__ import annotations
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _hokom(surface: str) -> dict:
    from hokom_pipeline import hokom
    return hokom(surface)


def _tense(surface: str) -> str | None:
    from pipeline.p5_inflection.feature_system import identify_tense
    return identify_tense(surface)


def _feats(surface: str) -> dict:
    from pipeline.p5_inflection.feature_system import extract_all_features
    return extract_all_features(surface)


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 1 — IMPERATIVES (must be FI3L:VERBAL_IMPERATIVE, person=2)
# ═════════════════════════════════════════════════════════════════════════════

def test_wastashhidu_is_form_x_imperative_second_person_plural():
    """وَاسْتَشْهِدُوا — Form X imperative 2MP; conjunction prefix وَ must be stripped."""
    result = _hokom('وَاسْتَشْهِدُوا')
    assert result.get('word_class') == 'FI3L', (
        f"وَاسْتَشْهِدُوا: expected FI3L, got {result.get('word_class')}")
    assert result.get('word_class_subclass') == 'VERBAL_IMPERATIVE', (
        f"وَاسْتَشْهِدُوا: expected VERBAL_IMPERATIVE, got {result.get('word_class_subclass')}")


def test_waashhidu_is_form_iv_imperative_second_person_plural():
    """وَأَشْهِدُوا — Form IV imperative 2MP."""
    result = _hokom('وَأَشْهِدُوا')
    assert result.get('word_class') == 'FI3L', (
        f"وَأَشْهِدُوا: expected FI3L, got {result.get('word_class')}")
    assert result.get('word_class_subclass') == 'VERBAL_IMPERATIVE', (
        f"وَأَشْهِدُوا: expected VERBAL_IMPERATIVE, got {result.get('word_class_subclass')}")


def test_faktubuhu_is_form_i_imperative():
    """فَاكْتُبُوهُ — Form I imperative 2MP with clitic -هُ; conjunction prefix فَ must be stripped."""
    result = _hokom('فَاكْتُبُوهُ')
    assert result.get('word_class') == 'FI3L', (
        f"فَاكْتُبُوهُ: expected FI3L, got {result.get('word_class')}")
    assert result.get('word_class_subclass') == 'VERBAL_IMPERATIVE', (
        f"فَاكْتُبُوهُ: expected VERBAL_IMPERATIVE, got {result.get('word_class_subclass')}")


def test_wattaqu_is_form_viii_imperative():
    """وَاتَّقُوا — Form VIII assimilation imperative 2MP (اتَّقى); SHADDA on C1 marks assimilation."""
    result = _hokom('وَاتَّقُوا')
    assert result.get('word_class') == 'FI3L', (
        f"وَاتَّقُوا: expected FI3L, got {result.get('word_class')}")
    assert result.get('word_class_subclass') == 'VERBAL_IMPERATIVE', (
        f"وَاتَّقُوا: expected VERBAL_IMPERATIVE, got {result.get('word_class_subclass')}")


# ─── feature_system sanity: identify_tense on stripped surfaces ───────────────

def test_identify_tense_wastashhidu():
    assert _tense('وَاسْتَشْهِدُوا') == 'IMPERATIVE'


def test_identify_tense_wattaqu():
    assert _tense('وَاتَّقُوا') == 'IMPERATIVE'


def test_identify_tense_faktubuhu():
    assert _tense('فَاكْتُبُوهُ') == 'IMPERATIVE'


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 2 — IMPERFECTS (must not be classified as PAST)
# ═════════════════════════════════════════════════════════════════════════════

def test_tadilla_is_feminine_imperfect_subjunctive():
    """تَضِلَّ — geminated root imperfect (ضلل), 3FSG or 2MSG SUBJUNCTIVE.
    The SHADDA at position 2 distinguishes it from a 3-char past."""
    feats = _feats('تَضِلَّ')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"تَضِلَّ: expected IMPERFECT, got {feats.get('tense_aspect')}")


def test_fatudhakkira_is_form_ii_feminine_imperfect_subjunctive():
    """فَتُذَكِّرَ — Form II passive/causative imperfect (ذكّر root)."""
    feats = _feats('فَتُذَكِّرَ')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"فَتُذَكِّرَ: expected IMPERFECT, got {feats.get('tense_aspect')}")


def test_wayuallimukumu_is_form_ii_imperfect_indicative():
    """وَيُعَلِّمُكُمُ — Form II imperfect 3MSG (علّم) with conjunction وَ and clitic -كُمُ."""
    feats = _feats('وَيُعَلِّمُكُمُ')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"وَيُعَلِّمُكُمُ: expected IMPERFECT, got {feats.get('tense_aspect')}")
    result = _hokom('وَيُعَلِّمُكُمُ')
    assert result.get('word_class') == 'FI3L', (
        f"وَيُعَلِّمُكُمُ: expected FI3L, got {result.get('word_class')}")
    assert result.get('word_class_subclass') == 'VERBAL_IMPERFECT', (
        f"وَيُعَلِّمُكُمُ: expected VERBAL_IMPERFECT, got {result.get('word_class_subclass')}")


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 3 — DEFERRED TOKENS WITH SUFFICIENT EVIDENCE
# ═════════════════════════════════════════════════════════════════════════════

def test_lam_command_opens_jussive_imperfect():
    """وَلْيَكْتُبْ — lam al-amr (لْ) + imperfect stem: must yield FI3L:VERBAL_IMPERFECT."""
    result = _hokom('وَلْيَكْتُبْ')
    assert result.get('word_class') == 'FI3L', (
        f"وَلْيَكْتُبْ: expected FI3L, got {result.get('word_class')}")
    assert result.get('word_class_subclass') == 'VERBAL_IMPERFECT', (
        f"وَلْيَكْتُبْ: expected VERBAL_IMPERFECT, got {result.get('word_class_subclass')}")


def test_fal_yaktubu_is_lam_amr_imperfect():
    """فَلْيَكْتُبْ — variant of lam al-amr with فَ conjunction prefix."""
    result = _hokom('فَلْيَكْتُبْ')
    assert result.get('word_class') == 'FI3L', (
        f"فَلْيَكْتُبْ: expected FI3L, got {result.get('word_class')}")
    assert result.get('word_class_subclass') == 'VERBAL_IMPERFECT', (
        f"فَلْيَكْتُبْ: expected VERBAL_IMPERFECT, got {result.get('word_class_subclass')}")


def test_yakunaa_is_imperfect_dual():
    """يَكُونَا — hollow root dual imperfect (كون); bare ends in 'نا' but is NOT past نا."""
    feats = _feats('يَكُونَا')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"يَكُونَا: expected IMPERFECT, got {feats.get('tense_aspect')}")


def test_takuna_is_hollow_imperfect():
    """تَكُونَ — hollow root imperfect 3FSG/2MSG SUBJUNCTIVE (كون)."""
    feats = _feats('تَكُونَ')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"تَكُونَ: expected IMPERFECT, got {feats.get('tense_aspect')}")


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 4 — MOOD FROM SYNTACTIC / GOVERNING PARTICLE CONTEXT
# ═════════════════════════════════════════════════════════════════════════════

def test_an_opens_subjunctive_imperfect():
    """أَنْ + imperfect → SUBJUNCTIVE mood."""
    feats = _feats('أَنْ تَكْتُبُوا')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"'أَنْ تَكْتُبُوا': expected IMPERFECT, got {feats.get('tense_aspect')}")
    assert feats.get('mood') == 'SUBJUNCTIVE', (
        f"'أَنْ تَكْتُبُوا': expected SUBJUNCTIVE, got {feats.get('mood')}")


def test_alla_opens_subjunctive_imperfect():
    """أَلَّا + imperfect → SUBJUNCTIVE mood (أَنْ + لَا compound)."""
    feats = _feats('أَلَّا تَرْتَابُوا')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"'أَلَّا تَرْتَابُوا': expected IMPERFECT, got {feats.get('tense_aspect')}")
    assert feats.get('mood') == 'SUBJUNCTIVE', (
        f"'أَلَّا تَرْتَابُوا': expected SUBJUNCTIVE, got {feats.get('mood')}")


def test_la_nahiya_opens_jussive():
    """لَا ناهية + imperfect → JUSSIVE mood."""
    feats = _feats('لَا تَسْأَمُوا')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"'لَا تَسْأَمُوا': expected IMPERFECT, got {feats.get('tense_aspect')}")
    assert feats.get('mood') == 'JUSSIVE', (
        f"'لَا تَسْأَمُوا': expected JUSSIVE, got {feats.get('mood')}")


def test_in_shart_opens_jussive():
    """إِنْ (conditional particle) + imperfect → JUSSIVE mood."""
    feats = _feats('إِنْ تَكْتُبْ')
    assert feats.get('tense_aspect') == 'IMPERFECT', (
        f"'إِنْ تَكْتُبْ': expected IMPERFECT, got {feats.get('tense_aspect')}")
    assert feats.get('mood') == 'JUSSIVE', (
        f"'إِنْ تَكْتُبْ': expected JUSSIVE, got {feats.get('mood')}")


def test_wala_nahiya_opens_jussive():
    """وَلَا تَسْأَمُوا — compound وَلَا ناهية → JUSSIVE; tests hokom() multi-word routing."""
    result = _hokom('وَلَا تَسْأَمُوا')
    assert result.get('tense_aspect') == 'IMPERFECT', (
        f"'وَلَا تَسْأَمُوا': expected IMPERFECT, got {result.get('tense_aspect')}")
    assert result.get('mood') == 'JUSSIVE', (
        f"'وَلَا تَسْأَمُوا': expected JUSSIVE, got {result.get('mood')}")


# ═════════════════════════════════════════════════════════════════════════════
# CLASS 5 — NON-VERB MUST NOT BE CLASSIFIED AS FI3L
# ═════════════════════════════════════════════════════════════════════════════

def test_aqsatu_is_not_a_verb():
    """أَقْسَطُ — elative adjective (اسم تفضيل) on أَفْعَلُ pattern; must be ISM, not FI3L."""
    result = _hokom('أَقْسَطُ')
    wc = result.get('word_class')
    assert wc != 'FI3L', (
        f"أَقْسَطُ: must NOT be FI3L (it is اسم تفضيل); got word_class={wc}")
    # Should be ISM or DEFERRED, never a verb
    assert wc in ('ISM', None, 'DEFERRED', 'HARF') or result.get('verdict') == 'DEFERRED', (
        f"أَقْسَطُ: expected ISM or DEFERRED, got {result}")


# ═════════════════════════════════════════════════════════════════════════════
# INVARIANT METRICS
# ═════════════════════════════════════════════════════════════════════════════

_IMPERATIVE_GOLD = [
    'وَاسْتَشْهِدُوا',
    'وَأَشْهِدُوا',
    'فَاكْتُبُوهُ',
    'وَاتَّقُوا',
]

_IMPERFECT_GOLD = [
    'تَضِلَّ',
    'فَتُذَكِّرَ',
    'وَيُعَلِّمُكُمُ',
    'يَكُونَا',
    'تَكُونَ',
    'وَلْيَكْتُبْ',
    'فَلْيَكْتُبْ',
    'فَلْيُمْلِلْ',
]

_NON_VERB_GOLD = [
    'أَقْسَطُ',
]


def test_imperatives_not_past():
    """IMPERATIVES_AS_PAST = 0: no gold imperative may map to VERBAL_PAST."""
    from hokom_pipeline import hokom
    bad = []
    for surface in _IMPERATIVE_GOLD:
        r = hokom(surface)
        if r.get('word_class_subclass') == 'VERBAL_PAST':
            bad.append(surface)
    assert bad == [], f"IMPERATIVES_AS_PAST != 0: {bad}"


def test_imperatives_not_deferred():
    """IMPERATIVES_DEFERRED = 0: no gold imperative may be DEFERRED."""
    from hokom_pipeline import hokom
    bad = []
    for surface in _IMPERATIVE_GOLD:
        r = hokom(surface)
        if r.get('verdict') == 'DEFERRED' or r.get('word_class') is None:
            bad.append(surface)
    assert bad == [], f"IMPERATIVES_DEFERRED != 0: {bad}"


def test_imperfects_not_past():
    """IMPERFECTS_AS_PAST = 0: no gold imperfect may map to VERBAL_PAST."""
    from pipeline.p5_inflection.feature_system import identify_tense
    bad = []
    for surface in _IMPERFECT_GOLD:
        t = identify_tense(surface)
        if t == 'PAST':
            bad.append(surface)
    assert bad == [], f"IMPERFECTS_AS_PAST != 0: {bad}"


def test_nonverbs_not_fi3l():
    """NONVERBS_AS_VERBS = 0: no gold non-verb may map to FI3L."""
    from hokom_pipeline import hokom
    bad = []
    for surface in _NON_VERB_GOLD:
        r = hokom(surface)
        if r.get('word_class') == 'FI3L':
            bad.append(surface)
    assert bad == [], f"NONVERBS_AS_VERBS != 0: {bad}"
