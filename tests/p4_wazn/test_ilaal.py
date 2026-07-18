#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_ilaal.py — Phase 4A-β: Weak-Radical Transformation Licensing

اختبارات I1–I15:
  - يَسْتَطِيعُ: ي في موضع العين + كسرة → واو الأصل → (ط،و،ع)
  - IlaalHypothesis مُجمَّد
  - TransformationTrace: position='AYN', surface='ي', underlying='و'
  - rule_id='WAW_TO_YAA_KASRA_CONDITIONED'
  - حالة DEFER: ألف في العين (ماضٍ) → غامضة
  - حالة DEFER: وزن غير معروف
  - الجذر المحلول لا يحتوي هوية ممنوعة
  - الحل ترفعه الثقة إلى HIGH
  - proposed_root_after ≠ None → ACCEPT مباشرة
  - anti-case: لا تبديل ي→و بدون وزن + كسرة
  - anti-case: ا في عين الفعل الماضي → DEFER
  - WeakRadicalTransformation مُجمَّد
  - أثر الإعلال موثَّق في evidence_ids
  - integration: يَسْتَطِيعُ عبر المنسّق → source='hypothesis_relicensed'
  - integration: جذر (ط،و،ع) في wazn_projection عبر المنسّق
"""

from __future__ import annotations

import pytest

from pipeline.p4_wazn.hypothesis import WaznHypothesis, build_wazn_hypothesis
from pipeline.p4_wazn.ilaal import (
    IlaalHypothesis,
    TransformationTrace,
    WeakRadicalTransformation,
    apply_ilaal_resolution,
    LICENSED_TRANSFORMATIONS,
)
from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn.phase4a_orchestrator import project_wazn_with_relicensing


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

def _make_ista_hypothesis(
    refined_host: str = 'يَسْتَطِيعُ',
    proposed_root_after=None,
    confidence: str = 'MEDIUM',
) -> WaznHypothesis:
    """فرضية يَسْتَفْعِل يدوية."""
    return WaznHypothesis(
        refined_host=refined_host,
        proposed_wazn='يَسْتَفْعِل',
        ziyadah_detected=('ALIF_WASL', 'SIN', 'TA'),
        proposed_root_after=proposed_root_after,
        confidence=confidence,
        evidence_ids=('ev:hypothesis:ista_prefix',),
        residual_codes=('residual:ista:root_extraction_failed',),
    )


def _make_fala_hypothesis(
    refined_host: str,
    proposed_root_after=None,
    confidence: str = 'MEDIUM',
) -> WaznHypothesis:
    """فرضية فَعَلَ (ماضٍ أجوف) يدوية — لا بادئة، ziyadah_detected=()."""
    return WaznHypothesis(
        refined_host=refined_host,
        proposed_wazn='فَعَلَ',
        ziyadah_detected=(),   # لا بادئة صرفية في فَعَلَ
        proposed_root_after=proposed_root_after,
        confidence=confidence,
        evidence_ids=('ev:hypothesis:fala',),
        residual_codes=('residual:fala:root_extraction_failed',),
    )


def _make_rc_defer(surface: str = 'يَسْتَطِيعُ') -> RootCandidate:
    return RootCandidate(
        surface=surface,
        host_surface=surface,
        directive='DEFER',
        canonical_root=None,
        root_profile={},
        evidence_ids=(),
        trace_ids=(),
        residual_codes=('defer:root_refinement:internal_ziyadah_not_resolved',),
    )


# ══════════════════════════════════════════════════════════════════════════════
# I1: يَسْتَطِيعُ → directive='ACCEPT'
# ══════════════════════════════════════════════════════════════════════════════

class TestYastatiuResolved:
    def test_yastatiiu_ilaal_directive_resolved(self):
        """يَسْتَطِيعُ + يَسْتَفْعِل + ي في موضع العين → ACCEPT."""
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'ACCEPT'

    def test_yastatiiu_ilaal_proposed_root(self):
        """الجذر المحلول = (ط،و،ع)."""
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.proposed_root == ('ط', 'و', 'ع')

    def test_yastatiiu_ilaal_no_failure_reason(self):
        """ACCEPT → failure_reason=None."""
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.failure_reason is None


# ══════════════════════════════════════════════════════════════════════════════
# I2: IlaalResolution مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestIlaalHypothesisIsFrozen:
    def test_ilaal_hypothesis_is_frozen(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        with pytest.raises((AttributeError, TypeError)):
            result.directive = 'DEFER'  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# I3: TransformationTrace — موضع + حرفان
# ══════════════════════════════════════════════════════════════════════════════

class TestTransformationTrace:
    def test_trace_position_is_ayn(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert len(result.transformations) > 0
        assert result.transformations[0].position == 'AYN'

    def test_trace_surface_is_yaa(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.transformations[0].surface_realization == 'ي'

    def test_trace_underlying_is_waw(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.transformations[0].underlying_radical == 'و'

    def test_trace_licensed_by_rule_id(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.transformations[0].licensed_by == 'WAW_TO_YAA_KASRA_CONDITIONED'

    def test_trace_wazn_context(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.transformations[0].wazn_context == 'يَسْتَفْعِل'

    def test_trace_cause_mentions_kasra(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert 'kasra' in result.transformations[0].cause


# ══════════════════════════════════════════════════════════════════════════════
# I4: WeakRadicalTransformation مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestWeakRadicalTransformationIsFrozen:
    def test_licensed_transformation_is_frozen(self):
        rule = LICENSED_TRANSFORMATIONS[0]
        with pytest.raises((AttributeError, TypeError)):
            rule.rule_id = 'MODIFIED'  # type: ignore[misc]

    def test_licensed_transformations_nonempty(self):
        assert len(LICENSED_TRANSFORMATIONS) >= 1

    def test_waw_to_yaa_rule_exists(self):
        rule_ids = {r.rule_id for r in LICENSED_TRANSFORMATIONS}
        assert 'WAW_TO_YAA_KASRA_CONDITIONED' in rule_ids


# ══════════════════════════════════════════════════════════════════════════════
# I5: DEFER — ألف في عين الماضي (بَاعَ / نَامَ / قَالَ)
# ══════════════════════════════════════════════════════════════════════════════

class TestAlifAynDefers:
    def test_naama_alif_ayn_defers(self):
        """نَامَ: ا في موضع العين لماضٍ → غامض بدون مضارع → DEFER."""
        hyp = _make_fala_hypothesis('نَامَ')
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'DEFER'

    def test_qaala_alif_ayn_defers(self):
        """قَالَ: ا في موضع العين لماضٍ → DEFER."""
        hyp = _make_fala_hypothesis('قَالَ')
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'DEFER'

    def test_baaa_alif_ayn_defers(self):
        """بَاعَ: لا يُفرض الواو (الجذر ب-ي-ع)؛ DEFER دون استنتاج."""
        hyp = _make_fala_hypothesis('بَاعَ')
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'DEFER'

    def test_alif_ayn_failure_reason(self):
        hyp = _make_fala_hypothesis('نَامَ')
        result = apply_ilaal_resolution(hyp)
        assert result.failure_reason is not None
        assert 'alif' in result.failure_reason or 'ambiguous' in result.failure_reason

    def test_no_root_proposed_when_alif_defers(self):
        hyp = _make_fala_hypothesis('قَالَ')
        result = apply_ilaal_resolution(hyp)
        assert result.proposed_root is None


# ══════════════════════════════════════════════════════════════════════════════
# I6: DEFER — وزن غير معروف
# ══════════════════════════════════════════════════════════════════════════════

class TestUnknownWaznDefers:
    def test_unknown_wazn_defers(self):
        hyp = WaznHypothesis(
            refined_host='مُفَعِّل',
            proposed_wazn='مُفَعِّل',   # وزن غير مُدرَج في خريطة السياق
            ziyadah_detected=('MIM_ZIYADAH',),
            proposed_root_after=None,
            confidence='MEDIUM',
            evidence_ids=(),
            residual_codes=(),
        )
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# I7: الجذر المحلول لا يحتوي هوية ممنوعة
# ══════════════════════════════════════════════════════════════════════════════

_PROHIBITED_IDENTITIES = frozenset({"ا", "ى", "أ", "إ", "ؤ", "ئ", "آ"})


class TestResolvedRootNoProhibited:
    def test_resolved_root_no_prohibited_identity(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'ACCEPT'
        assert result.proposed_root is not None
        for ch in result.proposed_root:
            assert ch not in _PROHIBITED_IDENTITIES, (
                f"prohibited identity {ch!r} in proposed_root")


# ══════════════════════════════════════════════════════════════════════════════
# I8: proposed_root_after ≠ None → ACCEPT مباشرة (بدون إعلال)
# ══════════════════════════════════════════════════════════════════════════════

class TestAlreadyResolvedPassthrough:
    def test_already_resolved_hypothesis_returns_resolved(self):
        """الفرضية محلولة مسبقًا → ACCEPT مباشرة، لا trace."""
        hyp = WaznHypothesis(
            refined_host='مَحَبَّ',
            proposed_wazn='مَفْعَلَة',
            ziyadah_detected=('MIM_ZIYADAH',),
            proposed_root_after=('ح', 'ب', 'ب'),
            confidence='HIGH',
            evidence_ids=('ev:hypothesis:mim_ziyadah_prefix',),
            residual_codes=(),
        )
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'ACCEPT'
        assert result.proposed_root == ('ح', 'ب', 'ب')

    def test_already_resolved_has_no_trace(self):
        hyp = WaznHypothesis(
            refined_host='مَحَبَّ',
            proposed_wazn='مَفْعَلَة',
            ziyadah_detected=('MIM_ZIYADAH',),
            proposed_root_after=('ح', 'ب', 'ب'),
            confidence='HIGH',
            evidence_ids=(),
            residual_codes=(),
        )
        result = apply_ilaal_resolution(hyp)
        assert result.transformations == ()


# ══════════════════════════════════════════════════════════════════════════════
# I9: أثر الإعلال موثَّق في evidence_ids
# ══════════════════════════════════════════════════════════════════════════════

class TestEvidenceIdCarried:
    def test_ilaal_evidence_in_evidence_ids(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'ACCEPT'
        # يجب أن يحتوي على دليل مرتبط بقاعدة الإعلال
        assert any('ilaal' in eid or 'WAW' in eid or 'kasra' in eid
                   for eid in result.evidence_ids), (
            f"no ilaal evidence in {result.evidence_ids}")

    def test_original_evidence_preserved(self):
        hyp = _make_ista_hypothesis()
        result = apply_ilaal_resolution(hyp)
        # الأدلة الأصلية محفوظة
        assert 'ev:hypothesis:ista_prefix' in result.evidence_ids


# ══════════════════════════════════════════════════════════════════════════════
# I10: Integration — يَسْتَطِيعُ عبر المنسّق → source='hypothesis_relicensed'
# ══════════════════════════════════════════════════════════════════════════════

class TestYastatiuOrchestratorIntegration:
    def _run_yastatiiu(self):
        rc = _make_rc_defer('يَسْتَطِيعُ')
        return project_wazn_with_relicensing(rc)

    def test_yastatiiu_source_hypothesis_relicensed(self):
        """يَسْتَطِيعُ → P4A-β يحل الإعلال → source='hypothesis_relicensed'."""
        result = self._run_yastatiiu()
        assert result.source_path == 'hypothesis_relicensed'

    def test_yastatiiu_wazn_hypothesis_not_none(self):
        result = self._run_yastatiiu()
        assert result.wazn_hypothesis is not None

    def test_yastatiiu_relicensing_accept(self):
        result = self._run_yastatiiu()
        assert result.relicensing_result is not None
        assert result.relicensing_result.directive == 'ACCEPT'

    def test_yastatiiu_ilaal_hypothesis_stored(self):
        """Phase4AResult يحتفظ بـ IlaalResolution."""
        result = self._run_yastatiiu()
        assert result.ilaal_resolution is not None
        assert result.ilaal_resolution.directive == 'ACCEPT'

    def test_yastatiiu_canonical_root_is_taa_waw_ayn(self):
        """الجذر النهائي = (ط،و،ع) في RootCandidate المُرقَّى."""
        result = self._run_yastatiiu()
        # الجذر المُرقَّى محفوظ في relicensing_result.canonical_root
        assert result.relicensing_result.canonical_root == ('ط', 'و', 'ع')
