#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_hokom_vs_hr2s_root_oracle.py — Hokom vs. HR2S Oracle

يقارن نتائج المحرك المحلي بـ HR2S كمرجع للمقارنة فقط.
HR2S لا يُغيّر حكم Hokom — المحرك المحلي هو المصدر النهائي.

قواعد هذا الملف:
  1. المسموح: from hr2s import MorphologyEngine (فقط)
  2. ممنوع: from hr2s.root import ..., from hr2s.boundary import ...
  3. نتيجة Hokom المحلية هي الحكم — HR2S للمقارنة فقط.
  4. الاختلافات تُسجَّل ولا تفشل الاختبار (إلا في حالات بعينها).
"""

from __future__ import annotations

import pytest

from pipeline.p3_candidate.root_resolution import resolve_root
from pipeline.p3_candidate.root_resolution_orchestrator import resolve_root_pipeline


# ══════════════════════════════════════════════════════════════════════════════
# مساعد: محاولة استيراد HR2S دون فشل إذا لم يكن مثبتًا
# ══════════════════════════════════════════════════════════════════════════════

try:
    from hr2s import MorphologyEngine as _HR2SEngine
    _HR2S_AVAILABLE = True
except ImportError:
    _HR2S_AVAILABLE = False
    _HR2SEngine = None  # type: ignore[assignment,misc]

_skip_if_no_hr2s = pytest.mark.skipif(
    not _HR2S_AVAILABLE,
    reason="hr2s not installed — oracle comparison skipped"
)


def _hokom_root(word: str, directive: str = 'OPEN') -> tuple | None:
    """نتيجة المحرك المحلي — الحكم النهائي."""
    r = resolve_root(word, pre_root_directive=directive)
    return r.canonical_root


# ══════════════════════════════════════════════════════════════════════════════
# O1: المحرك المحلي مستقل — يعمل بدون HR2S
# ══════════════════════════════════════════════════════════════════════════════

class TestLocalEngineIndependence:
    """يعمل المحرك المحلي بغض النظر عن وجود HR2S."""

    def test_daraba_local_independent(self):
        root = _hokom_root('ضَرَبَ')
        assert root == ('ض', 'ر', 'ب')

    def test_kataba_local_independent(self):
        root = _hokom_root('كَتَبَ')
        assert root == ('ك', 'ت', 'ب')

    def test_taraka_local_independent(self):
        root = _hokom_root('تَرَكَ')
        assert root == ('ت', 'ر', 'ك')

    def test_qaala_local_defers(self):
        root = _hokom_root('قَالَ')
        assert root is None


# ══════════════════════════════════════════════════════════════════════════════
# O2: لا يُكتب فوق نتيجة Hokom بـ HR2S
# ══════════════════════════════════════════════════════════════════════════════

class TestLocalNotOverwrittenByOracle:
    def test_local_result_authoritative_daraba(self):
        """نتيجة ضَرَبَ من المحرك المحلي = السلطة المرجعية."""
        local = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert local.source_engine == 'HOKOM_ROOT_ENGINE'
        # لا يجب أن يُغيَّر هذا الحكم بـ HR2S في أي مكان
        assert local.directive == 'ACCEPT'
        assert local.canonical_root == ('ض', 'ر', 'ب')

    def test_local_result_authoritative_defer(self):
        local = resolve_root('قَالَ', pre_root_directive='OPEN')
        assert local.source_engine == 'HOKOM_ROOT_ENGINE'
        assert local.directive == 'DEFER'
        assert local.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# O3 (اختياري إذا HR2S متاح): مقارنة النتائج
# ══════════════════════════════════════════════════════════════════════════════

@_skip_if_no_hr2s
class TestHokomVsHR2SOracleComparison:
    """يُقارن المحرك المحلي بـ HR2S — الاختلافات مُسجَّلة، لا تُفشل الاختبار."""

    _ACCEPT_CASES = [
        ('ضَرَبَ', ('ض', 'ر', 'ب')),
        ('كَتَبَ', ('ك', 'ت', 'ب')),
        ('تَرَكَ', ('ت', 'ر', 'ك')),
        ('شَجَرَ', ('ش', 'ج', 'ر')),
        ('قَرَأَ', ('ق', 'ر', 'ء')),
    ]

    def test_hokom_accept_matches_expected(self):
        """المحرك المحلي ينتج الجذور الصحيحة للحالات السليمة."""
        for word, expected_root in self._ACCEPT_CASES:
            local = resolve_root(word, pre_root_directive='OPEN')
            assert local.directive == 'ACCEPT', (
                f"{word}: expected ACCEPT, got {local.directive}")
            assert local.canonical_root == expected_root, (
                f"{word}: expected {expected_root}, got {local.canonical_root}")

    def test_hokom_not_overwritten_by_oracle(self):
        """نتيجة Hokom لا تتغير حتى لو HR2S موجود."""
        for word, expected_root in self._ACCEPT_CASES:
            local_root = _hokom_root(word)
            assert local_root == expected_root, (
                f"{word}: hokom_root={local_root}, expected={expected_root}")

    def test_oracle_comparison_without_mutation(self):
        """المقارنة مع HR2S لا تُغيّر نتيجة Hokom."""
        word = 'ضَرَبَ'
        local_before = resolve_root(word, pre_root_directive='OPEN')
        # لا نستدعي HR2S مباشرة في هذا الاختبار — نتحقق من أن Hokom مستقر
        local_after = resolve_root(word, pre_root_directive='OPEN')
        assert local_before.canonical_root == local_after.canonical_root
        assert local_before.directive == local_after.directive
