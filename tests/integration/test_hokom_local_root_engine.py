#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_hokom_local_root_engine.py — Integration: Hokom Root Engine

يختبر تسلسل Hokom المحلي الكامل:
  RootHostRefinement.refined_host
  → resolve_root()    → RootResolution
  → RootProjection    ← from_root_resolution()
  → RootCandidate     ← from_projection()

حالات host threading:
  تَرَكَتْهُمْ → original_host=تَرَكَتْ → refined_host=تَرَكَ → analyzed_host=تَرَكَ → root=(ت،ر،ك)
  شَجَرَةِ    → refined_host=شَجَرَ     → root=(ش،ج،ر)
"""

from __future__ import annotations

import pytest

from pipeline.p2_projection.root_host_refinement import refine_root_host
from pipeline.p3_candidate.root_resolution import resolve_root
from pipeline.p2_projection.root_projection import RootProjection
from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p3_candidate.root_resolution_orchestrator import (
    resolve_root_pipeline,
)


# ══════════════════════════════════════════════════════════════════════════════
# H1: تَرَكَتْهُمْ — host threading كامل
# ══════════════════════════════════════════════════════════════════════════════

class TestTarakathumHostThreading:
    """تَرَكَتْ (بعد فصل ضمير) → refined_host=تَرَكَ → root=(ت،ر،ك)."""

    def _resolve(self):
        return resolve_root_pipeline(
            original_host='تَرَكَتْ',
            refined_host='تَرَكَ',
            pre_root_directive='OPEN',
            morphology_path='verbal_root_path',
        )

    def test_root_is_ta_ra_kaf(self):
        rc = self._resolve()
        assert rc.canonical_root == ('ت', 'ر', 'ك')

    def test_host_surface_is_taraka(self):
        """host_surface في RootCandidate = refined_host = تَرَكَ (ليس الأصلي)."""
        rc = self._resolve()
        assert rc.host_surface == 'تَرَكَ'

    def test_directive_accept(self):
        rc = self._resolve()
        assert rc.directive == 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# H2: شَجَرَةِ → refined=شَجَرَ → root=(ش،ج،ر)
# ══════════════════════════════════════════════════════════════════════════════

class TestShajara:
    def _resolve(self):
        return resolve_root_pipeline(
            original_host='شَجَرَةِ',
            refined_host='شَجَرَ',
            pre_root_directive='OPEN',
            morphology_path='nominal_morphology_path',
        )

    def test_root_shin_jeem_ra(self):
        rc = self._resolve()
        assert rc.canonical_root == ('ش', 'ج', 'ر')

    def test_host_surface_is_shajara(self):
        rc = self._resolve()
        assert rc.host_surface == 'شَجَرَ'


# ══════════════════════════════════════════════════════════════════════════════
# H3: ACCEPT → RootProjection حاملة للجذر
# ══════════════════════════════════════════════════════════════════════════════

class TestRootProjectionCarriesRoot:
    def test_projection_analyzed_host_equals_refined(self):
        """RootProjection.analyzed_host = refined_host الممرَّر."""
        rc = resolve_root_pipeline(
            original_host='ضَرَبَ',
            refined_host='ضَرَبَ',
            pre_root_directive='OPEN',
        )
        # RootCandidate.host_surface = analyzed_host من Projection
        assert rc.host_surface == 'ضَرَبَ'

    def test_source_projection_is_local(self):
        """RootCandidate.source_projection تدل على المحرك المحلي."""
        rc = resolve_root_pipeline(
            original_host='ضَرَبَ',
            refined_host='ضَرَبَ',
            pre_root_directive='OPEN',
        )
        # source_projection يجب ألا تُشير إلى hr2s
        assert 'hr2s' not in rc.source_projection.lower(), (
            f"source_projection should be local, got: {rc.source_projection!r}")


# ══════════════════════════════════════════════════════════════════════════════
# H4: DEFER → لا جذر زائف في السلسلة
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferChain:
    def test_qaala_no_root_in_chain(self):
        rc = resolve_root_pipeline(
            original_host='قَالَ',
            refined_host='قَالَ',
            pre_root_directive='OPEN',
        )
        assert rc.directive == 'DEFER'
        assert rc.canonical_root is None

    def test_daa_no_root_in_chain(self):
        rc = resolve_root_pipeline(
            original_host='دَعَا',
            refined_host='دَعَا',
            pre_root_directive='OPEN',
        )
        assert rc.directive == 'DEFER'
        assert rc.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# H5: BLOCK → لا تحليل، لا جذر
# ══════════════════════════════════════════════════════════════════════════════

class TestBlockChain:
    def test_min_block_chain(self):
        rc = resolve_root_pipeline(
            original_host='مِنْ',
            refined_host='مِنْ',
            pre_root_directive='BLOCK',
        )
        assert rc.directive == 'BLOCK'
        assert rc.canonical_root is None

    def test_hiya_block_chain(self):
        rc = resolve_root_pipeline(
            original_host='هِيَ',
            refined_host='هِيَ',
            pre_root_directive='BLOCK',
        )
        assert rc.directive == 'BLOCK'


# ══════════════════════════════════════════════════════════════════════════════
# H6: النتيجة المحلية هي الموثوقة (لا HR2S)
# ══════════════════════════════════════════════════════════════════════════════

class TestLocalResultIsAuthoritative:
    def test_source_engine_is_hokom(self):
        """RootCandidate.root_profile يحفظ محرك Hokom المحلي."""
        rc = resolve_root_pipeline(
            original_host='كَتَبَ',
            refined_host='كَتَبَ',
            pre_root_directive='OPEN',
        )
        # source_engine يجب أن يكون HOKOM_ROOT_ENGINE
        assert rc.root_profile.get('source_engine') == 'HOKOM_ROOT_ENGINE', (
            f"expected HOKOM_ROOT_ENGINE in root_profile, got: {rc.root_profile}")

    def test_no_hr2s_dependency_in_pipeline(self):
        """يمكن تشغيل السلسلة بدون HR2S — المحرك المحلي مستقل."""
        # إذا كانت السلسلة تعمل هنا، فهي لا تحتاج HR2S
        rc = resolve_root_pipeline(
            original_host='ضَرَبَ',
            refined_host='ضَرَبَ',
            pre_root_directive='OPEN',
        )
        assert rc.directive == 'ACCEPT'
