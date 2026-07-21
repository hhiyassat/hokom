#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/pre_root_radical_accounting/test_geminate_dedup.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01
Cluster 2: GEMINATE_DEDUP_GAP

يتحقق من أن الشدة (التضعيف) تُعدُّ كحرف جذر واحد لا حرفين.
الشدة = PHONOLOGICAL_DUPLICATION — لا تُسقط ولا تُضاعف الجذر.

المجموعات:
  A (1–6):  ثلاثي مضعَّف (فعل مضارع بادئة يَ/تَ)
  B (7–10): Form II مضعَّف (يُفعِّل)
  C (11–15): وحدة: _count_consonants مع شدة
"""

from __future__ import annotations

import os
import sys

import pytest

_HOKOM_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _HOKOM_ROOT not in sys.path:
    sys.path.insert(0, _HOKOM_ROOT)


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
# Group A — ثلاثي مضعَّف (شَدَّ، مَدَّ، شَكَّ)
# ══════════════════════════════════════════════════════════════════════════════

class TestGeminateTriradical:
    """A: geminate roots get ACCEPT with 3-consonant root (FA3 not doubled)."""

    def test_A01_yashudd_cra_accept(self, pipeline):
        """A01: يَشُدُّ → CRA ACCEPT."""
        cra = _cra(pipeline, 'يَشُدُّ')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_A02_yashudd_root_shdd(self, pipeline):
        """A02: يَشُدُّ → root (ش,د,د) — ليس (ش,د,د,د) أو (ش,د)."""
        root = _root(pipeline, 'يَشُدُّ')
        assert root is not None
        assert len(root) == 3
        assert root == ('ش', 'د', 'د')

    def test_A03_yamudd_cra_accept(self, pipeline):
        """A03: يَمُدُّ → CRA ACCEPT."""
        cra = _cra(pipeline, 'يَمُدُّ')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_A04_yamudd_root_mdd(self, pipeline):
        """A04: يَمُدُّ → root (م,د,د)."""
        root = _root(pipeline, 'يَمُدُّ')
        assert root is not None
        assert len(root) == 3
        assert root == ('م', 'د', 'د')

    def test_A05_tashukkuwa_cra_accept(self, pipeline):
        """A05: تَشُكُّوا → CRA ACCEPT مع وا لاحقة."""
        cra = _cra(pipeline, 'تَشُكُّوا')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_A06_tashukkuwa_root_shkk(self, pipeline):
        """A06: تَشُكُّوا → root (ش,ك,ك) — الشدة على ك جذر واحد."""
        root = _root(pipeline, 'تَشُكُّوا')
        assert root is not None
        assert len(root) == 3
        assert root == ('ش', 'ك', 'ك')

    # ──────────────────────────────────────────────────────────────────────────
    # Group B — Form II مضعَّف (يُفَعِّل)
    # ──────────────────────────────────────────────────────────────────────────

    def test_B07_yuarrifu_cra_accept(self, pipeline):
        """B07: يُعَرِّفُ → CRA ACCEPT (FORM_II, شدة على ر)."""
        cra = _cra(pipeline, 'يُعَرِّفُ')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_B08_yuarrifu_form_ii(self, pipeline):
        """B08: يُعَرِّفُ → form_family=FORM_II."""
        cra = _cra(pipeline, 'يُعَرِّفُ')
        assert cra.form_family == 'FORM_II'

    def test_B09_yuarrifu_root_arf(self, pipeline):
        """B09: يُعَرِّفُ → root (ع,ر,ف)."""
        root = _root(pipeline, 'يُعَرِّفُ')
        assert root is not None
        assert 'ع' in root
        assert 'ر' in root
        assert 'ف' in root

    def test_B10_yashudd_prefix_stripped(self, pipeline):
        """B10: يَشُدُّ → prefix=يَ مُجرَّدة."""
        cra = _cra(pipeline, 'يَشُدُّ')
        assert cra.prefix_stripped == 'يَ'

    # ──────────────────────────────────────────────────────────────────────────
    # Group C — وحدة: _count_consonants
    # ──────────────────────────────────────────────────────────────────────────

    def test_C11_unit_count_with_shadda(self):
        """C11: الشدة لا تُعدُّ في _count_consonants."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _count_consonants
        # شُدُّ = ش + د + ّ (shadda on د) → 2 Arabic letters
        count = _count_consonants('شُدُّ')
        assert count == 2, f"Expected 2 consonants in شُدُّ, got {count}"

    def test_C12_unit_count_plain(self):
        """C12: _count_consonants('كتب') == 3."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _count_consonants
        assert _count_consonants('كتب') == 3

    def test_C13_unit_count_diacritics_ignored(self):
        """C13: _count_consonants('كَتَبَ') == 3 (harakat ignored)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _count_consonants
        assert _count_consonants('كَتَبَ') == 3

    def test_C14_unit_strip_suffix_geminate(self):
        """C14: _strip_verbal_suffix('تَشُكُّوا', True) → removes وا."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_verbal_suffix
        bare, suffix, rule = _strip_verbal_suffix('تَشُكُّوا', is_verbal=True)
        assert suffix == 'وا'
        assert bare.endswith('كُّ') or 'كُّ' in bare

    def test_C15_unit_geminate_root_3consonants(self):
        """C15: analyze_host_consonants بعد تجريد شُدُّ (بلا بادئة يَ) → ACCEPT (ش,د,د)."""
        from pipeline.p3_candidate.root_rules import analyze_host_consonants
        directive, root, residual, profile = analyze_host_consonants('شُدُّ')
        assert directive == 'ACCEPT'
        assert root == ('ش', 'د', 'د')
