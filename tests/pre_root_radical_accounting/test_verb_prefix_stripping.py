#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/pre_root_radical_accounting/test_verb_prefix_stripping.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01
Cluster 1: VERB_PREFIX_NOT_STRIPPED

يتحقق من أن بادئات المضارع (يَ/تَ/نَ/أَ) تُجرَّد بشكل صحيح
عند وجود شاهد VERBAL_ROOT_PATH، ولا تُجرَّد للأسماء.

المجموعات:
  A (1–5):  بادئة يَ/تَ (أفعال مضارع)
  B (6–10): بادئة تَ مع لاحقة وا / واو مفردة
  C (11–15): بادئة نَ/أَ
  D (16–20): وحدة: _strip_imperfect_prefix
"""

from __future__ import annotations

import os
import sys

import pytest

_HOKOM_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _HOKOM_ROOT not in sys.path:
    sys.path.insert(0, _HOKOM_ROOT)


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope='module')
def pipeline():
    from hokom_pipeline import hokom as _hokom
    return _hokom


def _cra(pipeline_fn, word: str):
    return pipeline_fn(word).get('cra_result')


def _root(pipeline_fn, word: str):
    rc = pipeline_fn(word).get('root_candidate')
    return getattr(rc, 'canonical_root', None) if rc else None


# ══════════════════════════════════════════════════════════════════════════════
# Group A — بادئة يَ (يفعل)
# ══════════════════════════════════════════════════════════════════════════════

class TestYaPrefix:
    """A: يَـ stripped for imperfect verbs."""

    def test_A01_yaktub_cra_accept(self, pipeline):
        """A01: يَكْتُبُ → CRA ACCEPT."""
        cra = _cra(pipeline, 'يَكْتُبُ')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_A02_yaktub_prefix_stripped(self, pipeline):
        """A02: يَكْتُبُ → prefix=يَ stripped."""
        cra = _cra(pipeline, 'يَكْتُبُ')
        assert cra.prefix_stripped == 'يَ'

    def test_A03_yaktub_root_ktb(self, pipeline):
        """A03: يَكْتُبُ → root (ك,ت,ب)."""
        root = _root(pipeline, 'يَكْتُبُ')
        assert root == ('ك', 'ت', 'ب')

    def test_A04_yadhab_cra_accept(self, pipeline):
        """A04: يَذْهَبُ → CRA ACCEPT."""
        cra = _cra(pipeline, 'يَذْهَبُ')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_A05_yadhab_root_dhb(self, pipeline):
        """A05: يَذْهَبُ → root contains ذ,ه,ب."""
        root = _root(pipeline, 'يَذْهَبُ')
        assert root is not None
        assert 'ذ' in root
        assert 'ه' in root
        assert 'ب' in root

    # ──────────────────────────────────────────────────────────────────────────
    # Group B — بادئة تَ (تفعل) + لاحقة وا
    # ──────────────────────────────────────────────────────────────────────────

    def test_B06_taktub_cra_accept(self, pipeline):
        """B06: تَكْتُبُ → CRA ACCEPT."""
        cra = _cra(pipeline, 'تَكْتُبُ')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_B07_taktub_prefix_ta(self, pipeline):
        """B07: تَكْتُبُ → prefix=تَ."""
        cra = _cra(pipeline, 'تَكْتُبُ')
        assert cra.prefix_stripped == 'تَ'

    def test_B08_taktub_root_ktb(self, pipeline):
        """B08: تَكْتُبُ → root (ك,ت,ب)."""
        root = _root(pipeline, 'تَكْتُبُ')
        assert root == ('ك', 'ت', 'ب')

    def test_B09_tafalu_suffix_stripped(self, pipeline):
        """B09: تَفْعَلُوا → suffix وا stripped, prefix تَ stripped."""
        cra = _cra(pipeline, 'تَفْعَلُوا')
        assert cra is not None
        assert cra.directive == 'ACCEPT'
        assert cra.suffix_stripped == 'وا'
        assert cra.prefix_stripped == 'تَ'

    def test_B10_tafalu_root_fal(self, pipeline):
        """B10: تَفْعَلُوا → root (ف,ع,ل)."""
        root = _root(pipeline, 'تَفْعَلُوا')
        assert root == ('ف', 'ع', 'ل')

    # ──────────────────────────────────────────────────────────────────────────
    # Group C — بادئة تَ مع واو مفردة (هُ محذوف)
    # ──────────────────────────────────────────────────────────────────────────

    def test_C11_taktubuhu_cra_accept(self, pipeline):
        """C11: تَكْتُبُوهُ → CRA ACCEPT (واو مفردة مُجرَّدة)."""
        cra = _cra(pipeline, 'تَكْتُبُوهُ')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_C12_taktubuhu_bare_waw_stripped(self, pipeline):
        """C12: تَكْتُبُوهُ → suffix=و (INFLECTIONAL_SUFFIX_WAW_JAMAA_BARE)."""
        cra = _cra(pipeline, 'تَكْتُبُوهُ')
        assert cra.suffix_stripped == 'و'
        assert 'WAW_JAMAA_BARE' in (cra.suffix_rule or '')

    def test_C13_taktubuhu_root_ktb(self, pipeline):
        """C13: تَكْتُبُوهُ → root (ك,ت,ب)."""
        root = _root(pipeline, 'تَكْتُبُوهُ')
        assert root == ('ك', 'ت', 'ب')

    def test_C14_tasamuwa_cra_accept(self, pipeline):
        """C14: تَسْأَمُوا → CRA ACCEPT (همزة الجذر تُحفظ)."""
        cra = _cra(pipeline, 'تَسْأَمُوا')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_C15_tasamuwa_root_smh(self, pipeline):
        """C15: تَسْأَمُوا → root (س,ء,م)."""
        root = _root(pipeline, 'تَسْأَمُوا')
        assert root == ('س', 'ء', 'م')

    # ──────────────────────────────────────────────────────────────────────────
    # Group D — وحدة: _strip_imperfect_prefix
    # ──────────────────────────────────────────────────────────────────────────

    def test_D16_unit_strip_ya(self):
        """D16: _strip_imperfect_prefix('يَكْتُبُ', True) → ('كْتُبُ', 'يَ')."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        stem, prefix = _strip_imperfect_prefix('يَكْتُبُ', is_verbal=True)
        assert prefix == 'يَ'
        assert stem.startswith('كْ') or stem[0] == 'ك'

    def test_D17_unit_strip_ta(self):
        """D17: _strip_imperfect_prefix('تَكْتُبُ', True) → ('كْتُبُ', 'تَ')."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        stem, prefix = _strip_imperfect_prefix('تَكْتُبُ', is_verbal=True)
        assert prefix == 'تَ'

    def test_D18_unit_no_strip_non_verbal(self):
        """D18: _strip_imperfect_prefix('يَكْتُبُ', False) → no strip (is_verbal=False)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        stem, prefix = _strip_imperfect_prefix('يَكْتُبُ', is_verbal=False)
        assert prefix is None
        assert stem == 'يَكْتُبُ'

    def test_D19_unit_no_strip_long_vowel_after_prefix(self):
        """D19: نَوْمِ — حرف مد بعد بادئة → لا تجريد (اسم)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        stem, prefix = _strip_imperfect_prefix('نَوْمِ', is_verbal=True)
        assert prefix is None, "نَوْمِ should not have نَ stripped (و follows = long vowel)"

    def test_D20_unit_no_strip_too_short(self):
        """D20: يَبُ — too short after strip → لا تجريد."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        stem, prefix = _strip_imperfect_prefix('يَبُ', is_verbal=True)
        # after stripping يَ only 'بُ' remains (1 consonant) → should not strip
        assert prefix is None
