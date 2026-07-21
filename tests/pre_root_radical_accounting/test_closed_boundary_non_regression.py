#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/pre_root_radical_accounting/test_closed_boundary_non_regression.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01

يتحقق من أن CRA لا يفتح الحدود المغلقة أبدًا:
  - JAMID_AALAM_BOUNDARY: لفظ الجلالة → cra=None
  - BLOCK from pre_root → CRA يُعيد BLOCK
  - لا يُغيِّر root_candidate عند وجود JAMID
  - حارس NO_SEGMENT_HOST_OR_PRE_ROOT

المجموعات:
  A (1–7):  لفظ الجلالة (7 صيغ)
  B (8–12): BLOCK من PreRoot → CRA=BLOCK
  C (13–16): حارس: لا مضيف / لا pre_root
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


def _jamid(pipeline_fn, word: str):
    return pipeline_fn(word).get('jamid_verdict')


def _root(pipeline_fn, word: str):
    rc = pipeline_fn(word).get('root_candidate')
    return getattr(rc, 'canonical_root', None) if rc else None


# ══════════════════════════════════════════════════════════════════════════════
# Group A — لفظ الجلالة (7 صيغ)
# ══════════════════════════════════════════════════════════════════════════════

class TestJalalaBoundary:
    """A: لفظ الجلالة — jamid=JAMID_AALAM_BOUNDARY, cra=None, root=None."""

    _JALALA_FORMS = [
        'اللَّهُ',
        'اللَّهَ',
        'اللَّهِ',
        'وَاللَّهُ',
        'فَاللَّهُ',
        'بِاللَّهِ',
        'لِلَّهِ',
    ]

    @pytest.mark.parametrize('word', _JALALA_FORMS)
    def test_A_jamid_aalam(self, pipeline, word):
        """A: {word} → jamid_verdict=JAMID_AALAM_BOUNDARY."""
        jamid = _jamid(pipeline, word)
        assert jamid == 'JAMID_AALAM_BOUNDARY', (
            f"{word}: expected JAMID_AALAM_BOUNDARY, got {jamid!r}"
        )

    @pytest.mark.parametrize('word', _JALALA_FORMS)
    def test_A_cra_none_for_jalala(self, pipeline, word):
        """A: {word} → cra=None (CRA blocked by jamid gate)."""
        cra = _cra(pipeline, word)
        assert cra is None, (
            f"{word}: expected cra=None (blocked by JAMID), got {cra!r}"
        )

    @pytest.mark.parametrize('word', _JALALA_FORMS)
    def test_A_root_none_for_jalala(self, pipeline, word):
        """A: {word} → root=None (jamid boundary, no root resolution)."""
        root = _root(pipeline, word)
        assert root is None, (
            f"{word}: expected root=None, got {root!r}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Group B — BLOCK guard in CRA (unit)
    # ──────────────────────────────────────────────────────────────────────────

    def test_B08_block_guard_fires_for_block_directive(self):
        """B08: pre_root.root_path_directive='BLOCK' → CRA returns BLOCK."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )

        class _FakePreRoot:
            root_path_directive = 'BLOCK'
            morphology_path = None

        result = process_canonical_radical_accounting(
            input_surface='test',
            segment_host='test',
            morphology_surface='test',
            pre_root=_FakePreRoot(),
        )
        assert result.directive == 'BLOCK'
        assert 'CRA_PRESERVE_BLOCK' in ' '.join(result.reason_codes)

    def test_B09_block_never_opened_to_accept(self):
        """B09: BLOCK from pre_root is never overridden to ACCEPT."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )

        class _FakePreRoot:
            root_path_directive = 'BLOCK'
            morphology_path = None

        result = process_canonical_radical_accounting(
            input_surface='كتب',
            segment_host='كتب',
            morphology_surface='كتب',
            pre_root=_FakePreRoot(),
        )
        assert result.directive != 'ACCEPT'

    def test_B10_block_never_opened_augmented(self):
        """B10: BLOCK not overridden even for augmented-looking surface."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )

        class _FakePreRoot:
            root_path_directive = 'BLOCK'
            morphology_path = None

        result = process_canonical_radical_accounting(
            input_surface='استشهدوا',
            segment_host='استشهدوا',
            morphology_surface='استشهدوا',
            pre_root=_FakePreRoot(),
        )
        assert result.directive == 'BLOCK'

    def test_B11_block_candidate_sequences_empty(self):
        """B11: BLOCK → candidate_radical_sequences=[]."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )

        class _FakePreRoot:
            root_path_directive = 'BLOCK'
            morphology_path = None

        result = process_canonical_radical_accounting(
            input_surface='مِنْ',
            segment_host='مِنْ',
            morphology_surface='مِنْ',
            pre_root=_FakePreRoot(),
        )
        assert result.candidate_radical_sequences == []

    def test_B12_open_directive_passes_through(self):
        """B12: OPEN directive allows CRA to proceed (not short-circuit)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )

        class _FakePreRoot:
            root_path_directive = 'OPEN'
            class morphology_path:
                value = 'ambiguous'

        result = process_canonical_radical_accounting(
            input_surface='كتب',
            segment_host='كتب',
            morphology_surface='كتب',
            pre_root=_FakePreRoot(),
        )
        assert result.directive != 'BLOCK'

    # ──────────────────────────────────────────────────────────────────────────
    # Group C — حارس: لا مضيف / لا pre_root
    # ──────────────────────────────────────────────────────────────────────────

    def test_C13_guard_no_host(self):
        """C13: segment_host=None → CRA returns BLOCK."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )

        class _FakePreRoot:
            root_path_directive = 'OPEN'
            morphology_path = None

        result = process_canonical_radical_accounting(
            input_surface='test',
            segment_host=None,
            morphology_surface=None,
            pre_root=_FakePreRoot(),
        )
        assert result.directive == 'BLOCK'
        assert 'CRA_GUARD' in ' '.join(result.reason_codes)

    def test_C14_guard_empty_host(self):
        """C14: segment_host='' → CRA returns BLOCK."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )

        class _FakePreRoot:
            root_path_directive = 'OPEN'
            morphology_path = None

        result = process_canonical_radical_accounting(
            input_surface='test',
            segment_host='',
            morphology_surface='',
            pre_root=_FakePreRoot(),
        )
        assert result.directive == 'BLOCK'

    def test_C15_guard_no_pre_root(self):
        """C15: pre_root=None → CRA returns BLOCK."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )
        result = process_canonical_radical_accounting(
            input_surface='كتب',
            segment_host='كتب',
            morphology_surface='كتب',
            pre_root=None,
        )
        assert result.directive == 'BLOCK'
        assert 'CRA_GUARD' in ' '.join(result.reason_codes)

    def test_C16_block_provenance(self):
        """C16: BLOCK has provenance starting with 'CRA:'."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            process_canonical_radical_accounting,
        )
        result = process_canonical_radical_accounting(
            input_surface='test',
            segment_host=None,
            morphology_surface=None,
            pre_root=None,
        )
        assert result.provenance.startswith('CRA:')
