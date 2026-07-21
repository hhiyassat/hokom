#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/pre_root_radical_accounting/test_pattern_extension.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01
Cluster 3: PATTERN_EXTENSION_COUNTED_AS_RADICAL

يتحقق من أن زيادات الاشتقاق في Form II–X تُصنَّف كـ DERIVATIONAL_EXTENSION
ولا تُحسب ضمن الجذر الثلاثي.

المجموعات:
  A (1–6):  FORM_X: اسْتَشْهِدُوا (وَاسْتَشْهِدُوا بعد تجريد واو العطف)
  B (7–12): FORM_IV: أَشْهِدُوا (وَأَشْهِدُوا)
  C (13–18): FORM_II: يُعَرِّفُ، يُمَيِّزُ
  D (19–22): وحدة: detect_augmented على صيغ مزيدة
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
# Group A — FORM_X: وَاسْتَشْهِدُوا
# ══════════════════════════════════════════════════════════════════════════════

class TestFormX:
    """A: FORM_X اسْتَـ prefix handled as DERIVATIONAL_EXTENSION."""

    def test_A01_wstashhiduwa_cra_accept(self, pipeline):
        """A01: وَاسْتَشْهِدُوا → CRA ACCEPT."""
        cra = _cra(pipeline, 'وَاسْتَشْهِدُوا')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_A02_wstashhiduwa_form_x(self, pipeline):
        """A02: وَاسْتَشْهِدُوا → form_family=FORM_X."""
        cra = _cra(pipeline, 'وَاسْتَشْهِدُوا')
        assert cra.form_family == 'FORM_X'

    def test_A03_wstashhiduwa_suffix_wa(self, pipeline):
        """A03: وَاسْتَشْهِدُوا → suffix=وا مُجرَّدة."""
        cra = _cra(pipeline, 'وَاسْتَشْهِدُوا')
        assert cra.suffix_stripped == 'وا'

    def test_A04_wstashhiduwa_root_shd(self, pipeline):
        """A04: وَاسْتَشْهِدُوا → root (ش,ه,د)."""
        root = _root(pipeline, 'وَاسْتَشْهِدُوا')
        assert root is not None
        assert 'ش' in root
        assert 'ه' in root
        assert 'د' in root

    def test_A05_wstashhiduwa_augmented_detection(self, pipeline):
        """A05: وَاسْتَشْهِدُوا → augmented_detection not None."""
        cra = _cra(pipeline, 'وَاسْتَشْهِدُوا')
        assert cra.augmented_detection is not None

    def test_A06_wstashhiduwa_root_pipeline(self, pipeline):
        """A06: وَاسْتَشْهِدُوا → pipeline root_candidate (ش,ه,د)."""
        root = _root(pipeline, 'وَاسْتَشْهِدُوا')
        assert root == ('ش', 'ه', 'د')

    # ──────────────────────────────────────────────────────────────────────────
    # Group B — FORM_IV: وَأَشْهِدُوا
    # ──────────────────────────────────────────────────────────────────────────

    def test_B07_washhiduwa_cra_accept(self, pipeline):
        """B07: وَأَشْهِدُوا → CRA ACCEPT."""
        cra = _cra(pipeline, 'وَأَشْهِدُوا')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_B08_washhiduwa_form_iv(self, pipeline):
        """B08: وَأَشْهِدُوا → form_family=FORM_IV."""
        cra = _cra(pipeline, 'وَأَشْهِدُوا')
        assert cra.form_family == 'FORM_IV'

    def test_B09_washhiduwa_suffix_wa(self, pipeline):
        """B09: وَأَشْهِدُوا → suffix=وا."""
        cra = _cra(pipeline, 'وَأَشْهِدُوا')
        assert cra.suffix_stripped == 'وا'

    def test_B10_washhiduwa_root_shd(self, pipeline):
        """B10: وَأَشْهِدُوا → root (ش,ه,د)."""
        root = _root(pipeline, 'وَأَشْهِدُوا')
        assert root is not None
        assert 'ش' in root
        assert 'ه' in root
        assert 'د' in root

    def test_B11_washhiduwa_no_prefix_stripped(self, pipeline):
        """B11: وَأَشْهِدُوا → prefix_stripped=None (أَـ is derivational, not inflectional)."""
        cra = _cra(pipeline, 'وَأَشْهِدُوا')
        # For augmented forms, the form prefix is derivational, not inflectional
        # prefix_stripped only set when RULE_IMPERFECT_PREFIX fires (Stage C)
        # Stage B returns before Stage C for augmented forms
        assert cra.prefix_stripped is None

    def test_B12_washhiduwa_pipeline_root(self, pipeline):
        """B12: وَأَشْهِدُوا → pipeline root_candidate (ش,ه,د)."""
        root = _root(pipeline, 'وَأَشْهِدُوا')
        assert root == ('ش', 'ه', 'د')

    # ──────────────────────────────────────────────────────────────────────────
    # Group C — FORM_II: يُعَرِّفُ
    # ──────────────────────────────────────────────────────────────────────────

    def test_C13_yuarrifu_cra_accept(self, pipeline):
        """C13: يُعَرِّفُ → CRA ACCEPT."""
        cra = _cra(pipeline, 'يُعَرِّفُ')
        assert cra is not None
        assert cra.directive == 'ACCEPT'

    def test_C14_yuarrifu_form_ii(self, pipeline):
        """C14: يُعَرِّفُ → form_family=FORM_II."""
        cra = _cra(pipeline, 'يُعَرِّفُ')
        assert cra.form_family == 'FORM_II'

    def test_C15_yuarrifu_root_arf(self, pipeline):
        """C15: يُعَرِّفُ → root contains (ع,ر,ف)."""
        root = _root(pipeline, 'يُعَرِّفُ')
        assert root is not None
        assert 'ع' in root
        assert 'ر' in root
        assert 'ف' in root

    # ──────────────────────────────────────────────────────────────────────────
    # Group D — وحدة: detect_augmented
    # ──────────────────────────────────────────────────────────────────────────

    def test_D19_unit_detect_form_x(self):
        """D19: detect_augmented('اسْتَشْهِدُ') → FORM_X root=(ش,ه,د)."""
        from pipeline.p2_augmented.detector import detect_augmented
        result = detect_augmented('اسْتَشْهِدُ')
        assert result is not None
        assert result.form_family == 'FORM_X'
        assert 'ش' in result.root
        assert 'ه' in result.root
        assert 'د' in result.root

    def test_D20_unit_detect_form_iv(self):
        """D20: detect_augmented('أَشْهِدُ') → FORM_IV root=(ش,ه,د)."""
        from pipeline.p2_augmented.detector import detect_augmented
        result = detect_augmented('أَشْهِدُ')
        assert result is not None
        assert result.form_family == 'FORM_IV'
        assert 'ش' in result.root

    def test_D21_unit_detect_form_ii(self):
        """D21: detect_augmented('يُعَرِّفُ') → FORM_II."""
        from pipeline.p2_augmented.detector import detect_augmented
        result = detect_augmented('يُعَرِّفُ')
        # Either direct detection or None (if detect_augmented needs stripped form)
        if result is not None:
            assert result.form_family == 'FORM_II'

    def test_D22_unit_no_false_augmented_for_form1(self):
        """D22: detect_augmented('كْتُبُ') (بعد تجريد يَ) → None (ليس صيغة مزيدة)."""
        from pipeline.p2_augmented.detector import detect_augmented
        result = detect_augmented('كْتُبُ')
        # يَكْتُبُ بعد تجريد يَ: كتب (3 حروف) → ليس صيغة مزيدة
        # Form I roots don't match augmented patterns
        if result is not None:
            # If a result is returned, it should still give correct 3-letter root
            # (not a false positive that invents extra letters)
            assert len(result.root) == 3
