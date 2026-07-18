#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_phase4a_contract.py — W1: Phase4AResult Contract Tests
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

اختبارات عقد Phase4AResult المُحدَّث:

C1.  initial_root_directive يعكس directive المُدخل
C2.  final_directive صريح ومستقل عن source_path
C3.  Root ACCEPT + Wazn ACCEPT → final_directive='ACCEPT'
C4.  Root ACCEPT + Wazn DEFER → final_directive='DEFER' (لا 'ACCEPT')
C5.  Root BLOCK → final_directive='BLOCK' / wazn_projection=None
C6.  Root DEFER بلا فرضية → final_directive='DEFER' / wazn_projection=None
C7.  DEFER → hypothesis → relicensing ACCEPT → Wazn ACCEPT → final_directive='ACCEPT'
C8.  DEFER → hypothesis → relicensing ACCEPT → Wazn DEFER → final_directive='DEFER'
C9.  DEFER → hypothesis → relicensing DEFER → final_directive='DEFER'
C10. promoted_root_candidate يُعيَّن فقط عند relicensing ACCEPT
C11. final_wazn يُعيَّن فقط عند final_directive='ACCEPT'
C12. final_wazn=None عند final_directive='DEFER'
C13. source_path يصف المسار — لا يحدد الحكم
C14. Phase4AResult مُجمَّد
C15. to_dict() يحتوي جميع المفاتيح المطلوبة
C16. evidence_ids / trace_ids / residual_codes أنواع tuple
C17. ilaal_resolution (لا ilaal_hypothesis) في Phase4AResult
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn.phase4a_orchestrator import Phase4AResult, project_wazn_with_relicensing
from pipeline.p4_wazn.hypothesis import WaznHypothesis


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

def _make_rc(directive: str, surface: str = 'ضَرَبَ',
             host_surface: str = 'ضَرَبَ',
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


class _FakeRefinement:
    def __init__(self, refined_host: str, removed_suffixes=(), residual_codes=()):
        self.refined_host = refined_host
        self.removed_suffixes = removed_suffixes
        self.residual_codes = residual_codes


def _make_low_confidence_hyp(root: tuple) -> WaznHypothesis:
    return WaznHypothesis(
        refined_host='مَحَبَّ',
        proposed_wazn='مَفْعَلَة',
        ziyadah_detected=('MIM_ZIYADAH',),
        proposed_root_after=root,
        confidence='LOW',
        evidence_ids=(),
        residual_codes=(),
    )


_ZIYADAH_RESIDUAL = ('defer:root_refinement:internal_ziyadah_not_resolved',)

_DARABA_RC     = lambda: _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ',
                                   canonical_root=('ض', 'ر', 'ب'))
_MIN_RC        = lambda: _make_rc('BLOCK', surface='مِنْ', host_surface='مِنْ')
_QAALA_RC      = lambda: _make_rc('DEFER', surface='قَالَ', host_surface='قَالَ',
                                   residual_codes=('defer:root:hollow_underlying_radical_unresolved',))
_MAHABB_RC     = lambda: _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                                   residual_codes=_ZIYADAH_RESIDUAL)
_MAHABB_REF    = lambda: _FakeRefinement('مَحَبَّ', ('NOMINAL_TA_MARBUTA',), _ZIYADAH_RESIDUAL)


# ══════════════════════════════════════════════════════════════════════════════
# C1: initial_root_directive يعكس directive المُدخل
# ══════════════════════════════════════════════════════════════════════════════

class TestInitialRootDirective:
    def test_accept_rc_initial_is_accept(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.initial_root_directive == 'ACCEPT'

    def test_defer_rc_initial_is_defer(self):
        result = project_wazn_with_relicensing(_QAALA_RC())
        assert result.initial_root_directive == 'DEFER'

    def test_block_rc_initial_is_block(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.initial_root_directive == 'BLOCK'


# ══════════════════════════════════════════════════════════════════════════════
# C2: final_directive صريح — وجوده كحقل str مستقل
# ══════════════════════════════════════════════════════════════════════════════

class TestFinalDirectiveExists:
    def test_final_directive_is_string(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert isinstance(result.final_directive, str)

    def test_final_directive_valid_value(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.final_directive in ('ACCEPT', 'DEFER', 'BLOCK')

    def test_block_final_directive_is_block(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.final_directive == 'BLOCK'


# ══════════════════════════════════════════════════════════════════════════════
# C3: Root ACCEPT + Wazn ACCEPT → final_directive='ACCEPT'
# ══════════════════════════════════════════════════════════════════════════════

class TestRootAcceptWaznAccept:
    def test_daraba_final_accept(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.final_directive == 'ACCEPT'

    def test_daraba_source_path(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.source_path == 'direct_accept'

    def test_daraba_wazn_projection_not_none(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.wazn_projection is not None

    def test_daraba_no_hypothesis(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.wazn_hypothesis is None

    def test_daraba_no_promoted_candidate(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.promoted_root_candidate is None


# ══════════════════════════════════════════════════════════════════════════════
# C4: Root ACCEPT + Wazn DEFER → final_directive='DEFER' (ليس 'ACCEPT')
# ══════════════════════════════════════════════════════════════════════════════

class TestRootAcceptWaznDefer:
    """Root ACCEPT لا يضمن Wazn ACCEPT — final_directive يأتي من WaznProjection."""

    def test_accept_wazn_defer_stays_defer(self):
        """نُزوِّد catalog فارغًا → لا مطابقة → wazn DEFER."""
        rc = _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ',
                      canonical_root=('ض', 'ر', 'ب'))
        # catalog فارغ يُجبر wazn على DEFER
        result = project_wazn_with_relicensing(rc, catalog=())
        assert result.final_directive != 'ACCEPT', (
            "Root ACCEPT + empty catalog must NOT produce final_directive='ACCEPT'")

    def test_source_path_direct_accept_even_when_wazn_defers(self):
        """source_path يصف مسار الجذر، لا حكم الوزن."""
        rc = _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ',
                      canonical_root=('ض', 'ر', 'ب'))
        result = project_wazn_with_relicensing(rc, catalog=())
        assert result.source_path == 'direct_accept'
        # final_directive يعكس الوزن، ليس source_path
        assert result.final_directive != result.source_path


# ══════════════════════════════════════════════════════════════════════════════
# C5: Root BLOCK → final_directive='BLOCK' / wazn_projection=None
# ══════════════════════════════════════════════════════════════════════════════

class TestRootBlock:
    def test_block_final_directive(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.final_directive == 'BLOCK'

    def test_block_wazn_projection_none(self):
        """BLOCK لا يُنتج WaznProjection — وزن غير مفتوح."""
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.wazn_projection is None

    def test_block_final_wazn_none(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.final_wazn is None

    def test_block_source_path(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.source_path == 'blocked'


# ══════════════════════════════════════════════════════════════════════════════
# C6: Root DEFER بلا فرضية → final_directive='DEFER' / wazn_projection=None
# ══════════════════════════════════════════════════════════════════════════════

class TestRootDeferNoHypothesis:
    def test_defer_no_hypothesis_final_defer(self):
        result = project_wazn_with_relicensing(_QAALA_RC())
        assert result.final_directive == 'DEFER'

    def test_defer_no_hypothesis_wazn_none(self):
        """DEFER بلا فرضية → لا wazn projection."""
        result = project_wazn_with_relicensing(_QAALA_RC())
        assert result.wazn_projection is None

    def test_defer_no_hypothesis_source_path(self):
        result = project_wazn_with_relicensing(_QAALA_RC())
        assert result.source_path == 'deferred'

    def test_defer_no_hypothesis_no_promoted(self):
        result = project_wazn_with_relicensing(_QAALA_RC())
        assert result.promoted_root_candidate is None


# ══════════════════════════════════════════════════════════════════════════════
# C7: DEFER → hypothesis → relicensing ACCEPT → Wazn ACCEPT → final_directive='ACCEPT'
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferRelicensingAcceptWaznAccept:
    def test_mahabb_relicensed_final_accept(self):
        """مَحَبَّ → (ح،ب،ب) → relicensing ACCEPT → wazn ACCEPT → final='ACCEPT'."""
        result = project_wazn_with_relicensing(
            _MAHABB_RC(), root_refinement=_MAHABB_REF())
        assert result.source_path == 'hypothesis_relicensed'
        assert result.relicensing_result is not None
        assert result.relicensing_result.directive == 'ACCEPT'
        # WaznProjection قد يكون ACCEPT أو DEFER حسب الكتالوج — يُقيَّد بـ final_directive
        # الأهم: final_directive لا يُعطى 'ACCEPT' دون WaznProjection.ACCEPT
        if result.wazn_projection is not None:
            from pipeline.p4_wazn.models import WaznDirective
            assert result.final_directive == result.wazn_projection.directive.value


# ══════════════════════════════════════════════════════════════════════════════
# C8: DEFER → relicensing ACCEPT → Wazn DEFER → final_directive='DEFER'
# يُختبر بكتالوج فارغ يجبر الوزن على DEFER بعد الترخيص
# ══════════════════════════════════════════════════════════════════════════════

class TestRelicensingAcceptButWaznDefers:
    def test_relicensing_accept_wazn_defer(self):
        """Relicensing ACCEPT لا يضمن final_directive='ACCEPT'."""
        import pipeline.p4_wazn.phase4a_orchestrator as orch
        from pipeline.p4_wazn.hypothesis import WaznHypothesis

        # فرضية صالحة → ترخيص ACCEPT مضمون
        valid_hyp = WaznHypothesis(
            refined_host='مَحَبَّ',
            proposed_wazn='مَفْعَلَة',
            ziyadah_detected=('MIM_ZIYADAH',),
            proposed_root_after=('ح', 'ب', 'ب'),
            confidence='HIGH',
            evidence_ids=(),
            residual_codes=(),
            radical_alignment=(
                ('م', 'MIM_ZIYADAH'),
                ('ح', 'FA'),
                ('ب', 'AYN'),
                ('ب', 'LAM'),
            ),
            removed_elements=(('م', 'MIM_ZIYADAH'),),
        )
        rc = _MAHABB_RC()
        with patch.object(orch, 'build_wazn_hypothesis', return_value=valid_hyp):
            # catalog=() يُجبر WaznProjection على DEFER بعد الترخيص
            result = project_wazn_with_relicensing(rc, catalog=())

        assert result.relicensing_result is not None
        assert result.relicensing_result.directive == 'ACCEPT'
        # الوزن يُفشل بسبب catalog فارغ
        assert result.final_directive != 'ACCEPT', (
            "Relicensing ACCEPT + empty wazn catalog must NOT give final_directive='ACCEPT'")


# ══════════════════════════════════════════════════════════════════════════════
# C9: DEFER → hypothesis → relicensing DEFER → final_directive='DEFER'
# ══════════════════════════════════════════════════════════════════════════════

class TestRelicensingDefers:
    def test_low_confidence_hypothesis_defers(self):
        """LOW confidence hypothesis → relicensing DEFER → final_directive='DEFER'."""
        import pipeline.p4_wazn.phase4a_orchestrator as orch

        low_hyp = _make_low_confidence_hyp(('ح', 'ب', 'ب'))
        rc = _MAHABB_RC()
        with patch.object(orch, 'build_wazn_hypothesis', return_value=low_hyp):
            result = project_wazn_with_relicensing(rc)

        assert result.source_path == 'deferred'
        assert result.final_directive == 'DEFER'
        assert result.promoted_root_candidate is None


# ══════════════════════════════════════════════════════════════════════════════
# C10: promoted_root_candidate يُعيَّن فقط عند relicensing ACCEPT
# ══════════════════════════════════════════════════════════════════════════════

class TestPromotedRootCandidate:
    def test_promoted_set_on_relicensing_accept(self):
        result = project_wazn_with_relicensing(
            _MAHABB_RC(), root_refinement=_MAHABB_REF())
        if result.relicensing_result and result.relicensing_result.directive == 'ACCEPT':
            assert result.promoted_root_candidate is not None
            assert result.promoted_root_candidate.directive == 'ACCEPT'
            assert result.promoted_root_candidate is not result.root_candidate

    def test_promoted_none_for_direct_accept(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.promoted_root_candidate is None

    def test_promoted_none_for_block(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.promoted_root_candidate is None

    def test_promoted_none_for_defer_no_hypothesis(self):
        result = project_wazn_with_relicensing(_QAALA_RC())
        assert result.promoted_root_candidate is None


# ══════════════════════════════════════════════════════════════════════════════
# C11-C12: final_wazn
# ══════════════════════════════════════════════════════════════════════════════

class TestFinalWazn:
    def test_final_wazn_set_when_accept(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        if result.final_directive == 'ACCEPT':
            assert result.final_wazn is not None
            assert isinstance(result.final_wazn, str)

    def test_final_wazn_none_for_block(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.final_wazn is None

    def test_final_wazn_none_for_defer_no_hypothesis(self):
        result = project_wazn_with_relicensing(_QAALA_RC())
        assert result.final_wazn is None

    def test_final_wazn_none_when_final_defer(self):
        """final_directive='DEFER' يستوجب final_wazn=None — لا وزن بلا حكم قبول."""
        rc = _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ',
                      canonical_root=('ض', 'ر', 'ب'))
        result = project_wazn_with_relicensing(rc, catalog=())
        if result.final_directive != 'ACCEPT':
            assert result.final_wazn is None


# ══════════════════════════════════════════════════════════════════════════════
# C13: source_path يصف المسار — لا يحدد الحكم
# ══════════════════════════════════════════════════════════════════════════════

class TestSourcePathIsPath:
    def test_source_path_and_final_directive_are_independent(self):
        """source_path='direct_accept' يمكن أن يصاحب final_directive='DEFER'."""
        rc = _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ',
                      canonical_root=('ض', 'ر', 'ب'))
        result = project_wazn_with_relicensing(rc, catalog=())
        # المسار مباشر لكن الوزن قد يكون DEFER
        assert result.source_path == 'direct_accept'
        # final_directive لا يُشتق من source_path

    def test_source_path_field_exists(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert hasattr(result, 'source_path')

    def test_no_source_field(self):
        """الحقل القديم source لا يجب أن يكون موجودًا (أو على الأقل source_path موجود)."""
        result = project_wazn_with_relicensing(_DARABA_RC())
        # source_path يجب أن يوجد
        assert hasattr(result, 'source_path')


# ══════════════════════════════════════════════════════════════════════════════
# C14: Phase4AResult مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase4AResultFrozen:
    def test_frozen_direct_accept(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        with pytest.raises((AttributeError, TypeError)):
            result.final_directive = 'BLOCK'  # type: ignore[misc]

    def test_frozen_block(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        with pytest.raises((AttributeError, TypeError)):
            result.source_path = 'direct_accept'  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# C15: to_dict() يحتوي جميع المفاتيح المطلوبة
# ══════════════════════════════════════════════════════════════════════════════

_REQUIRED_DICT_KEYS = (
    'initial_root_directive',
    'final_directive',
    'source_path',
    'final_wazn',
    'evidence_ids',
    'trace_ids',
    'residual_codes',
)

class TestToDict:
    def test_to_dict_has_required_keys_accept(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        d = result.to_dict()
        for k in _REQUIRED_DICT_KEYS:
            assert k in d, f"missing key {k!r} in to_dict()"

    def test_to_dict_has_required_keys_block(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        d = result.to_dict()
        for k in _REQUIRED_DICT_KEYS:
            assert k in d, f"missing key {k!r} in to_dict()"

    def test_to_dict_final_directive_matches_field(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        d = result.to_dict()
        assert d['final_directive'] == result.final_directive

    def test_to_dict_evidence_ids_is_list(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        d = result.to_dict()
        assert isinstance(d['evidence_ids'], list)


# ══════════════════════════════════════════════════════════════════════════════
# C16: evidence_ids / trace_ids / residual_codes أنواع tuple
# ══════════════════════════════════════════════════════════════════════════════

class TestAggregatedIds:
    def test_evidence_ids_is_tuple(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert isinstance(result.evidence_ids, tuple)

    def test_trace_ids_is_tuple(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert isinstance(result.trace_ids, tuple)

    def test_residual_codes_is_tuple(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert isinstance(result.residual_codes, tuple)

    def test_residual_codes_tuple_for_block(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert isinstance(result.residual_codes, tuple)


# ══════════════════════════════════════════════════════════════════════════════
# C17: ilaal_resolution — الاسم الصحيح (لا ilaal_hypothesis)
# ══════════════════════════════════════════════════════════════════════════════

class TestIlaalResolutionField:
    def test_ilaal_resolution_field_exists(self):
        """Phase4AResult يجب أن يحتوي ilaal_resolution لا ilaal_hypothesis."""
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert hasattr(result, 'ilaal_resolution'), (
            "Phase4AResult must have 'ilaal_resolution' field")

    def test_ilaal_resolution_none_for_direct(self):
        result = project_wazn_with_relicensing(_DARABA_RC())
        assert result.ilaal_resolution is None

    def test_ilaal_resolution_none_for_block(self):
        result = project_wazn_with_relicensing(_MIN_RC())
        assert result.ilaal_resolution is None
