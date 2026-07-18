#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_phase4a_orchestrator.py — Phase4A Orchestrator

اختبارات O1–O10:
  - BLOCK → source=='blocked'
  - ACCEPT → source=='direct'، لا فرضية
  - DEFER + لا فرضية → source=='deferred'
  - DEFER + فرضية + ترخيص ACCEPT → source=='hypothesis_relicensed'
  - DEFER + فرضية + ترخيص DEFER → source=='deferred'
  - رتابة: DEFER لا يصبح ACCEPT بدون ترخيص
  - Phase4AResult مُجمَّد
  - BLOCK → wazn_hypothesis=None
  - لا مسارات مطلقة في hypothesis.py
  - root_candidate محفوظ في النتيجة
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn.phase4a_orchestrator import Phase4AResult, project_wazn_with_relicensing


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

def _make_rc(directive: str, surface: str = 'مَحَبَّةٌ',
             host_surface: str = 'مَحَبَّةٌ',
             canonical_root=None,
             residual_codes: tuple = ()) -> RootCandidate:
    return RootCandidate(
        surface=surface,
        host_surface=host_surface,
        directive=directive,
        canonical_root=canonical_root,
        root_profile={},
        evidence_ids=(),
        trace_ids=(),
        residual_codes=residual_codes,
    )


_ZIYADAH_RESIDUAL = ('defer:root_refinement:internal_ziyadah_not_resolved',)


class _FakeRefinement:
    """محاكاة RootHostRefinement للاختبار."""
    def __init__(self, refined_host: str, removed_suffixes=(), residual_codes=()):
        self.refined_host = refined_host
        self.removed_suffixes = removed_suffixes
        self.residual_codes = residual_codes


# ══════════════════════════════════════════════════════════════════════════════
# O1: BLOCK → source == 'blocked'
# ══════════════════════════════════════════════════════════════════════════════

class TestBlockSourceBlocked:
    def test_block_root_candidate_source_blocked(self):
        rc = _make_rc('BLOCK', surface='مِنْ', host_surface='مِنْ')
        result = project_wazn_with_relicensing(rc)
        assert isinstance(result, Phase4AResult)
        assert result.source_path == 'blocked'


# ══════════════════════════════════════════════════════════════════════════════
# O2: ACCEPT → source == 'direct'، لا فرضية
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptDirect:
    def test_accept_root_candidate_direct(self):
        rc = _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ',
                      canonical_root=('ض', 'ر', 'ب'))
        result = project_wazn_with_relicensing(rc)
        assert result.source_path == 'direct_accept'
        assert result.wazn_hypothesis is None
        assert result.relicensing_result is None

    def test_accept_root_candidate_preserved(self):
        rc = _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ',
                      canonical_root=('ض', 'ر', 'ب'))
        result = project_wazn_with_relicensing(rc)
        assert result.root_candidate is rc


# ══════════════════════════════════════════════════════════════════════════════
# O3: DEFER + لا فرضية → source == 'deferred'
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferNoHypothesisDeferred:
    def test_defer_no_hypothesis_deferred(self):
        rc = _make_rc('DEFER', surface='قَالَ', host_surface='قَالَ',
                      residual_codes=('defer:root:hollow_underlying_radical_unresolved',))
        result = project_wazn_with_relicensing(rc)
        assert result.source_path == 'deferred'
        assert result.wazn_hypothesis is None


# ══════════════════════════════════════════════════════════════════════════════
# O4: DEFER + فرضية + ترخيص ACCEPT → source == 'hypothesis_relicensed'
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferHypothesisRelicensed:
    def test_defer_hypothesis_relicensed(self):
        """مَحَبَّ → MIM_ZIYADAH → (ح،ب،ب) → ACCEPT → hypothesis_relicensed."""
        rc = _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        refinement = _FakeRefinement(
            refined_host='مَحَبَّ',
            removed_suffixes=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        result = project_wazn_with_relicensing(rc, root_refinement=refinement)
        assert result.source_path == 'hypothesis_relicensed'
        assert result.wazn_hypothesis is not None
        assert result.relicensing_result is not None
        assert result.relicensing_result.directive == 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# O5: DEFER + فرضية + ترخيص DEFER → source == 'deferred'
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferHypothesisButRelicensingDefers:
    def test_defer_hypothesis_but_relicensing_defers(self):
        """فرضية LOW confidence → DEFER relicensing → deferred."""
        # نستخدم مضيف سيُنتج فرضية ذات ثقة منخفضة
        # نُعيد إنشاء الفرضية بشكل اصطناعي عبر mocking
        from unittest.mock import patch
        from pipeline.p4_wazn import hypothesis as hyp_module

        # أنشئ فرضية LOW confidence صناعية
        from pipeline.p4_wazn.hypothesis import WaznHypothesis
        low_hyp = WaznHypothesis(
            refined_host='مَحَبَّ',
            proposed_wazn='مَفْعَلَة',
            ziyadah_detected=('MIM_ZIYADAH',),
            proposed_root_after=('ح', 'ب', 'ب'),
            confidence='LOW',
            evidence_ids=(),
            residual_codes=(),
        )

        rc = _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        refinement = _FakeRefinement(
            refined_host='مَحَبَّ',
            removed_suffixes=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )

        import pipeline.p4_wazn.phase4a_orchestrator as orch_module
        with patch.object(orch_module, 'build_wazn_hypothesis', return_value=low_hyp):
            result = project_wazn_with_relicensing(rc, root_refinement=refinement)

        # LOW confidence → DEFER relicensing → لا ترقية
        assert result.source_path == 'deferred'


# ══════════════════════════════════════════════════════════════════════════════
# O6: رتابة — DEFER لا يصبح ACCEPT بدون بوابة الترخيص
# ══════════════════════════════════════════════════════════════════════════════

class TestMonotonicityNoDirectPromote:
    def test_monotonicity_no_direct_promote(self):
        """DEFER بلا فرضية → لا ACCEPT في المخرج."""
        rc = _make_rc('DEFER', surface='قَالَ', host_surface='قَالَ',
                      residual_codes=('defer:root:hollow',))
        result = project_wazn_with_relicensing(rc)
        assert result.source_path != 'direct_accept'
        assert result.source_path != 'hypothesis_relicensed'
        # DEFER بلا فرضية → wazn_projection=None → final_directive='DEFER'
        assert result.wazn_projection is None
        assert result.final_directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# O7: Phase4AResult مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase4AResultFrozen:
    def test_phase4a_result_frozen(self):
        rc = _make_rc('BLOCK', surface='مِنْ', host_surface='مِنْ')
        result = project_wazn_with_relicensing(rc)
        with pytest.raises((AttributeError, TypeError)):
            result.source_path = "direct_accept"  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# O8: BLOCK → wazn_hypothesis=None
# ══════════════════════════════════════════════════════════════════════════════

class TestBlockHasNoHypothesis:
    def test_block_has_no_hypothesis(self):
        rc = _make_rc('BLOCK', surface='مِنْ', host_surface='مِنْ')
        result = project_wazn_with_relicensing(rc)
        assert result.wazn_hypothesis is None


# ══════════════════════════════════════════════════════════════════════════════
# O9: لا مسارات مطلقة في hypothesis.py
# ══════════════════════════════════════════════════════════════════════════════

class TestNoAbsolutePathsInHypothesis:
    def test_no_absolute_paths_in_hypothesis(self):
        src = (pathlib.Path(__file__).parent.parent.parent
               / 'pipeline' / 'p4_wazn' / 'hypothesis.py')
        content = src.read_text(encoding='utf-8')
        # لا يجوز وجود مسار مطلق بادئ بـ /
        import re
        # بحث عن سلاسل نصية تبدأ بـ / (مسارات مطلقة) داخل كود Python
        # نستخدم AST للتحقق من القيم النصية
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if val.startswith('/') and len(val) > 2:
                    pytest.fail(f"absolute path found in hypothesis.py: {val!r}")


# ══════════════════════════════════════════════════════════════════════════════
# O10: root_candidate محفوظ في النتيجة
# ══════════════════════════════════════════════════════════════════════════════

class TestRootCandidatePreservedInResult:
    def test_root_candidate_preserved_in_result(self):
        rc = _make_rc('BLOCK', surface='مِنْ', host_surface='مِنْ')
        result = project_wazn_with_relicensing(rc)
        assert result.root_candidate is rc

    def test_root_candidate_preserved_accept(self):
        rc = _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ',
                      canonical_root=('ض', 'ر', 'ب'))
        result = project_wazn_with_relicensing(rc)
        assert result.root_candidate is rc
