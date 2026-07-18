#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_ilaal_contract.py — W3: IlaalResolution Contract

عقود W3 (الاختبارات ستفشل أولًا، ثم نُعدِّل ilaal.py):

  W3-1  : IlaalResolution قابلة للاستيراد           ← يفشل حتى التعديل
  W3-2  : directive ∈ {'ACCEPT','DEFER','BLOCK'}     ← يفشل (حاليًا 'RESOLVED')
  W3-3  : proposed_root — لا proposed_root_after     ← يفشل
  W3-4  : transformations: tuple[TransformationTrace]← يفشل (حاليًا Optional)
  W3-5  : unresolved_positions موجود                 ← يفشل
  W3-6  : trace_ids موجود                            ← يفشل
  W3-7  : to_dict() JSON-safe                        ← يفشل
  W3-8  : يَسْتَطِيعُ → ACCEPT + WAW_TO_YAA          ← يفشل (حاليًا RESOLVED)
  W3-9  : يَسْتَطِيعُ → proposed_root=('ط','و','ع')  ← يفشل (حاليًا proposed_root_after)
  W3-10 : يَسْتَطِيعُ → transformations non-empty    ← يفشل
  W3-11 : قَالَ → DEFER + proposed_root=None         ← يمر / يفشل (اسم الحقل)
  W3-12 : نَامَ / بَاعَ → DEFER                      ← يمر
  W3-13 : long vowel pattern (مَسْرُور) → ACCEPT, transformations=()   ← يفشل
  W3-14 : مَحَبَّ shadda ≠ إعلال → ACCEPT, transformations=()          ← يفشل
  W3-15 : ACCEPT يشترط named transformation_id في كل trace             ← يفشل
  W3-16 : ACCEPT يشترط evidence                     ← يفشل
  W3-17 : لا canonical_root في IlaalResolution       ← يمر
  W3-18 : IlaalResolution لا تُنشئ RootCandidate أو WaznCandidate
  W3-19 : IlaalResolution لا تُعدّل WaznHypothesis   ← يمر
  W3-20 : to_dict() يحتوي المفاتيح المطلوبة          ← يفشل
  W3-21 : evidence/trace/residuals محفوظة           ← جزئي
  W3-22 : IlaalHypothesis الوسيط قابل للاستيراد      ← يفشل
  W3-23 : IlaalHypothesis يحتوي الحقول المطلوبة      ← يفشل
  W3-24 : IlaalResolution مُجمَّد                    ← يمر (نوع مختلف)
  W3-25 : لا استيراد من hr2s (AST)                  ← يمر
  W3-26 : لا مسارات مطلقة (AST)                     ← يمر
  W3-27 : لا استيراد لـ project_wazn/WaznCandidate  ← يمر
"""

from __future__ import annotations

import ast
import json
import pathlib
from typing import Optional

import pytest

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn.hypothesis import WaznHypothesis


_ILAAL_SRC = (pathlib.Path(__file__).parent.parent.parent
              / 'pipeline' / 'p4_wazn' / 'ilaal.py')


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

def _ista_hyp(proposed_root_after=None, confidence='MEDIUM') -> WaznHypothesis:
    """WaznHypothesis يَسْتَفْعِل (يَسْتَطِيعُ)."""
    return WaznHypothesis(
        refined_host='يَسْتَطِيعُ',
        proposed_wazn='يَسْتَفْعِل',
        ziyadah_detected=('ALIF_WASL', 'SIN', 'TA'),
        proposed_root_after=proposed_root_after,
        confidence=confidence,
        evidence_ids=('ev:hypothesis:ista_prefix',),
        residual_codes=('residual:ista:root_extraction_failed',),
    )


def _fala_hyp(host: str, proposed_root_after=None) -> WaznHypothesis:
    """WaznHypothesis فَعَلَ (ماضٍ أجوف: قَالَ / نَامَ / بَاعَ)."""
    return WaznHypothesis(
        refined_host=host,
        proposed_wazn='فَعَلَ',
        ziyadah_detected=(),
        proposed_root_after=proposed_root_after,
        confidence='MEDIUM',
        evidence_ids=('ev:hypothesis:fala',),
        residual_codes=(),
    )


def _mafool_hyp(proposed_root: tuple) -> WaznHypothesis:
    """WaznHypothesis مَفْعُول (مَسْرُور): proposed_root_after محدد مسبقًا."""
    return WaznHypothesis(
        refined_host='مَسْرُور',
        proposed_wazn='مَفْعَلَة',    # أقرب ما يصف — Pattrn A simple
        ziyadah_detected=('MIM_ZIYADAH',),
        proposed_root_after=proposed_root,
        confidence='HIGH',
        evidence_ids=('ev:hypothesis:mim_ziyadah_prefix',),
        residual_codes=(),
    )


def _mahabb_hyp() -> WaznHypothesis:
    """WaznHypothesis مَحَبَّ (تضعيف — proposed_root_after محدد)."""
    return WaznHypothesis(
        refined_host='مَحَبَّ',
        proposed_wazn='مَفْعَلَة',
        ziyadah_detected=('MIM_ZIYADAH',),
        proposed_root_after=('ح', 'ب', 'ب'),
        confidence='HIGH',
        evidence_ids=('ev:hypothesis:mim_ziyadah_prefix',),
        residual_codes=(),
    )


# ══════════════════════════════════════════════════════════════════════════════
# W3-1: IlaalResolution قابلة للاستيراد  [يفشل حتى التعديل]
# ══════════════════════════════════════════════════════════════════════════════

class TestIlaalResolutionImportable:
    def test_ilaal_resolution_importable(self):
        """IlaalResolution يجب أن تُستورَد من ilaal.py."""
        try:
            from pipeline.p4_wazn.ilaal import IlaalResolution
        except ImportError as e:
            pytest.fail(f"IlaalResolution غير قابلة للاستيراد: {e}")

    def test_apply_ilaal_resolution_returns_ilaal_resolution(self):
        """apply_ilaal_resolution() يعيد IlaalResolution، لا IlaalHypothesis."""
        from pipeline.p4_wazn.ilaal import IlaalResolution, apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert isinstance(result, IlaalResolution), (
            f"النوع المُعاد: {type(result).__name__!r} — المطلوب: IlaalResolution"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W3-2: directive ∈ {'ACCEPT','DEFER','BLOCK'}  [يفشل — حاليًا 'RESOLVED']
# ══════════════════════════════════════════════════════════════════════════════

class TestIlaalResolutionDirectiveValues:
    def test_yastatiiu_directive_accept(self):
        """يَسْتَطِيعُ → ACCEPT (ليس 'RESOLVED')."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert result.directive == 'ACCEPT', (
            f"directive={result.directive!r} — المتوقع 'ACCEPT' (ليس 'RESOLVED'). "
            "قيم directive المعتمدة: ACCEPT | DEFER | BLOCK"
        )

    def test_qaala_directive_defer(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_fala_hyp('قَالَ'))
        assert result.directive == 'DEFER'

    def test_directive_set_is_bounded(self):
        """directive يجب أن يكون في {'ACCEPT','DEFER','BLOCK'}."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        cases = [
            _ista_hyp(), _fala_hyp('قَالَ'), _fala_hyp('نَامَ'), _mahabb_hyp(),
        ]
        valid = {'ACCEPT', 'DEFER', 'BLOCK'}
        for hyp in cases:
            r = apply_ilaal_resolution(hyp)
            assert r.directive in valid, (
                f"directive={r.directive!r} خارج القيم المعتمدة: {valid}"
            )

    def test_already_resolved_returns_accept_not_resolved(self):
        """الفرضية محلولة مسبقًا → ACCEPT (ليس 'RESOLVED')."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_mahabb_hyp())
        assert result.directive == 'ACCEPT', (
            f"directive={result.directive!r} — مَحَبَّ محلول مسبقًا يجب أن يُعيد ACCEPT"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W3-3: proposed_root — لا proposed_root_after  [يفشل]
# ══════════════════════════════════════════════════════════════════════════════

class TestProposedRootField:
    def test_proposed_root_field_exists(self):
        """IlaalResolution يحتوي 'proposed_root'، لا 'proposed_root_after'."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert hasattr(result, 'proposed_root'), (
            "IlaalResolution يفتقد حقل 'proposed_root' — "
            "يجب تغيير 'proposed_root_after' إلى 'proposed_root'"
        )
        assert not hasattr(result, 'proposed_root_after'), (
            "IlaalResolution لا تزال تحتوي 'proposed_root_after' — "
            "يجب حذف هذا الحقل القديم"
        )

    def test_yastatiiu_proposed_root_value(self):
        """يَسْتَطِيعُ → proposed_root = ('ط','و','ع')."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert result.proposed_root == ('ط', 'و', 'ع'), (
            f"proposed_root={result.proposed_root!r} — المتوقع: ('ط','و','ع')"
        )

    def test_defer_proposed_root_none(self):
        """DEFER → proposed_root = None."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_fala_hyp('قَالَ'))
        assert result.proposed_root is None


# ══════════════════════════════════════════════════════════════════════════════
# W3-4: transformations: tuple  [يفشل — حاليًا Optional[TransformationTrace]]
# ══════════════════════════════════════════════════════════════════════════════

class TestTransformationsTuple:
    def test_transformations_field_exists(self):
        """IlaalResolution يحتوي حقل 'transformations': tuple."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert hasattr(result, 'transformations'), (
            "IlaalResolution يفتقد حقل 'transformations' — "
            "يجب استبدال 'transformation_trace: Optional' بـ 'transformations: tuple'"
        )

    def test_transformations_is_tuple(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert isinstance(result.transformations, tuple), (
            f"transformations نوعه {type(result.transformations).__name__!r} — المطلوب tuple"
        )

    def test_yastatiiu_transformations_non_empty(self):
        """يَسْتَطِيعُ → transformations غير فارغة."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert len(result.transformations) > 0, (
            "يَسْتَطِيعُ يجب أن يُنتج على الأقل trace واحدة في transformations"
        )

    def test_defer_transformations_empty(self):
        """DEFER → transformations = ()."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_fala_hyp('قَالَ'))
        assert result.transformations == (), (
            f"DEFER يجب أن يُعيد transformations=() لا {result.transformations!r}"
        )

    def test_already_resolved_transformations_empty(self):
        """الفرضية محلولة مسبقًا (مَحَبَّ) → transformations = ()، لا إعلال."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_mahabb_hyp())
        assert result.transformations == (), (
            "مَحَبَّ محلول مسبقًا — لا يجب أن تكون هناك traces إعلال"
        )

    def test_transformation_trace_type_in_tuple(self):
        """عناصر transformations يجب أن تكون TransformationTrace."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution, TransformationTrace
        result = apply_ilaal_resolution(_ista_hyp())
        for trace in result.transformations:
            assert isinstance(trace, TransformationTrace), (
                f"عنصر في transformations من نوع {type(trace).__name__!r} — "
                "المطلوب TransformationTrace"
            )


# ══════════════════════════════════════════════════════════════════════════════
# W3-5: unresolved_positions موجود  [يفشل]
# ══════════════════════════════════════════════════════════════════════════════

class TestUnresolvedPositionsField:
    def test_unresolved_positions_field_exists(self):
        """IlaalResolution يحتوي حقل 'unresolved_positions': tuple."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert hasattr(result, 'unresolved_positions'), (
            "IlaalResolution يفتقد حقل 'unresolved_positions'"
        )

    def test_accept_unresolved_positions_empty(self):
        """ACCEPT → unresolved_positions = () (كل المواضع محلولة)."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert result.unresolved_positions == (), (
            f"ACCEPT → unresolved_positions يجب أن يكون (): {result.unresolved_positions!r}"
        )

    def test_defer_unresolved_positions_non_empty(self):
        """DEFER → unresolved_positions غير فارغة (موضع العين لا يزال غامضًا)."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_fala_hyp('قَالَ'))
        assert isinstance(result.unresolved_positions, tuple)
        # يجب أن يحتوي على موضع العين
        assert len(result.unresolved_positions) > 0, (
            "قَالَ DEFER → unresolved_positions يجب أن تحتوي على 'AYN' أو ما يعادله"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W3-6: trace_ids موجود  [يفشل]
# ══════════════════════════════════════════════════════════════════════════════

class TestTraceIdsField:
    def test_trace_ids_field_exists(self):
        """IlaalResolution يحتوي حقل 'trace_ids': tuple."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert hasattr(result, 'trace_ids'), (
            "IlaalResolution يفتقد حقل 'trace_ids'"
        )

    def test_trace_ids_is_tuple(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert isinstance(result.trace_ids, tuple)

    def test_accept_trace_ids_non_empty(self):
        """ACCEPT → trace_ids تحتوي مسار التحويل."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert len(result.trace_ids) > 0, (
            "ACCEPT → trace_ids يجب أن تحتوي على مسار الإعلال"
        )

    def test_trace_ids_are_ascii_strings(self):
        """trace_ids عناصرها سلاسل ASCII."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        for tid in result.trace_ids:
            assert isinstance(tid, str)
            assert tid.isascii() or ':' in tid  # معرّفات مسار نصية


# ══════════════════════════════════════════════════════════════════════════════
# W3-7: to_dict() JSON-safe  [يفشل]
# ══════════════════════════════════════════════════════════════════════════════

class TestToDictJsonSafe:
    def test_to_dict_method_exists(self):
        """IlaalResolution يحتوي to_dict()."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert hasattr(result, 'to_dict'), (
            "IlaalResolution يفتقد الدالة to_dict()"
        )
        assert callable(result.to_dict)

    def test_to_dict_returns_dict(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        d = result.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_json_serializable(self):
        """to_dict() يجب أن يكون قابلًا للتسلسل إلى JSON."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        for hyp in [_ista_hyp(), _fala_hyp('قَالَ'), _mahabb_hyp()]:
            result = apply_ilaal_resolution(hyp)
            try:
                json.dumps(result.to_dict())
            except (TypeError, ValueError) as e:
                pytest.fail(f"to_dict() غير قابل للتسلسل JSON: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# W3-8–10: يَسْتَطِيعُ → ACCEPT + WAW_TO_YAA + proposed_root=(ط،و،ع)
# ══════════════════════════════════════════════════════════════════════════════

class TestYastatiuAcceptChain:
    def test_yastatiiu_accept(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        assert apply_ilaal_resolution(_ista_hyp()).directive == 'ACCEPT'

    def test_yastatiiu_proposed_root_taa_waw_ayn(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert result.proposed_root == ('ط', 'و', 'ع')

    def test_yastatiiu_one_transformation_trace(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert len(result.transformations) == 1

    def test_yastatiiu_trace_position_ayn(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        trace = apply_ilaal_resolution(_ista_hyp()).transformations[0]
        assert trace.position == 'AYN'

    def test_yastatiiu_trace_surface_yaa(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        trace = apply_ilaal_resolution(_ista_hyp()).transformations[0]
        assert trace.surface_realization == 'ي'

    def test_yastatiiu_trace_underlying_waw(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        trace = apply_ilaal_resolution(_ista_hyp()).transformations[0]
        assert trace.underlying_radical == 'و'

    def test_yastatiiu_trace_licensed_by_rule_id(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        trace = apply_ilaal_resolution(_ista_hyp()).transformations[0]
        assert trace.licensed_by == 'WAW_TO_YAA_KASRA_CONDITIONED'

    def test_yastatiiu_unresolved_positions_empty(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        assert apply_ilaal_resolution(_ista_hyp()).unresolved_positions == ()


# ══════════════════════════════════════════════════════════════════════════════
# W3-11–12: قَالَ / نَامَ / بَاعَ → DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestHollowPastDeferChain:
    def test_qaala_defer(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        assert apply_ilaal_resolution(_fala_hyp('قَالَ')).directive == 'DEFER'

    def test_naama_defer(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        assert apply_ilaal_resolution(_fala_hyp('نَامَ')).directive == 'DEFER'

    def test_baaa_defer(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        assert apply_ilaal_resolution(_fala_hyp('بَاعَ')).directive == 'DEFER'

    def test_qaala_proposed_root_none(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        assert apply_ilaal_resolution(_fala_hyp('قَالَ')).proposed_root is None

    def test_hollow_past_transformations_empty(self):
        """ألف العين في الماضي → لا تحويل مُنجَز."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        for host in ('قَالَ', 'نَامَ', 'بَاعَ'):
            r = apply_ilaal_resolution(_fala_hyp(host))
            assert r.transformations == (), (
                f"{host}: DEFER transformations يجب أن يكون (): {r.transformations!r}"
            )

    def test_hollow_past_has_unresolved_position(self):
        """قَالَ: unresolved_positions تشمل موضع العين."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_fala_hyp('قَالَ'))
        assert len(result.unresolved_positions) > 0
        ayn_present = any('AYN' in p or 'ayn' in p.lower()
                          for p in result.unresolved_positions)
        assert ayn_present, (
            f"unresolved_positions لا تذكر AYN: {result.unresolved_positions}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W3-13: long vowel pattern (مَسْرُور) → ACCEPT, transformations=()
# ══════════════════════════════════════════════════════════════════════════════

class TestLongVowelPatternNotIlaal:
    def test_masroor_accept_no_transformation(self):
        """مَسْرُور: proposed_root=('س','ر','ر') محدد مسبقًا → ACCEPT, لا إعلال."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        hyp = _mafool_hyp(('س', 'ر', 'ر'))
        result = apply_ilaal_resolution(hyp)
        assert result.directive == 'ACCEPT'
        assert result.transformations == (), (
            "مَسْرُور: واو مَفْعُول هي حرف مد وزني لا إعلال → transformations=()"
        )

    def test_masroor_proposed_root_preserved(self):
        """مَسْرُور: proposed_root = ('س','ر','ر') كما هو."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_mafool_hyp(('س', 'ر', 'ر')))
        assert result.proposed_root == ('س', 'ر', 'ر')

    def test_long_vowel_not_weak_radical(self):
        """الواو في مَفْعُول ≠ جذر ضعيف → لا يستدعي WAW_TO_YAA_KASRA_CONDITIONED."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution, LICENSED_TRANSFORMATIONS
        result = apply_ilaal_resolution(_mafool_hyp(('س', 'ر', 'ر')))
        # لا trace ترجع إلى WAW_TO_YAA_KASRA_CONDITIONED
        for trace in result.transformations:
            assert trace.licensed_by != 'WAW_TO_YAA_KASRA_CONDITIONED', (
                "مَسْرُور: WAW_TO_YAA لا تُطبَّق على حروف المد الوزنية"
            )


# ══════════════════════════════════════════════════════════════════════════════
# W3-14: مَحَبَّ shadda ≠ إعلال → ACCEPT, transformations=()
# ══════════════════════════════════════════════════════════════════════════════

class TestShaddaNotIlaal:
    def test_mahabb_accept_no_transformation(self):
        """مَحَبَّ: التضعيف ليس إعلالًا → ACCEPT, transformations=()."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_mahabb_hyp())
        assert result.directive == 'ACCEPT'
        assert result.transformations == (), (
            "مَحَبَّ: الشدة هي تضعيف لا إعلال → transformations=()"
        )

    def test_mahabb_proposed_root_is_haa_baa_baa(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_mahabb_hyp())
        assert result.proposed_root == ('ح', 'ب', 'ب')


# ══════════════════════════════════════════════════════════════════════════════
# W3-15: ACCEPT يشترط named transformation_id في كل trace
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptRequiresNamedTransformationId:
    def test_accept_trace_has_nonempty_licensed_by(self):
        """كل TransformationTrace في ACCEPT يجب أن يحمل licensed_by مُسمًّى."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        for trace in result.transformations:
            assert trace.licensed_by and trace.licensed_by.strip(), (
                "TransformationTrace يجب أن يحمل licensed_by غير فارغة"
            )
            assert trace.licensed_by.isascii(), (
                f"licensed_by يجب أن يكون ASCII: {trace.licensed_by!r}"
            )

    def test_accept_trace_licensed_by_in_known_rules(self):
        """licensed_by يجب أن يكون معرّفًا في LICENSED_TRANSFORMATIONS."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution, LICENSED_TRANSFORMATIONS
        known_ids = {r.rule_id for r in LICENSED_TRANSFORMATIONS}
        result = apply_ilaal_resolution(_ista_hyp())
        for trace in result.transformations:
            assert trace.licensed_by in known_ids, (
                f"licensed_by={trace.licensed_by!r} غير معرَّف في LICENSED_TRANSFORMATIONS: "
                f"{known_ids}"
            )


# ══════════════════════════════════════════════════════════════════════════════
# W3-16: ACCEPT يشترط evidence
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptRequiresEvidence:
    def test_accept_evidence_ids_non_empty(self):
        """ACCEPT → evidence_ids غير فارغة."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert len(result.evidence_ids) > 0, (
            "ACCEPT يجب أن يحتوي على دليل في evidence_ids"
        )

    def test_accept_evidence_includes_ilaal_marker(self):
        """evidence_ids تحتوي مؤشر الإعلال."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert any('ilaal' in e.lower() or 'WAW' in e or 'waw' in e.lower()
                   for e in result.evidence_ids), (
            f"لا مؤشر إعلال في evidence_ids: {result.evidence_ids}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W3-17: لا canonical_root في IlaalResolution
# ══════════════════════════════════════════════════════════════════════════════

class TestNoCanonicalRoot:
    def test_ilaal_resolution_has_no_canonical_root(self):
        """IlaalResolution لا تحتوي حقل canonical_root."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        assert not hasattr(result, 'canonical_root'), (
            "IlaalResolution لا يجب أن تحتوي 'canonical_root' — "
            "الترخيص يتم فقط في RootRelicensing (P3.11)"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W3-18: لا RootCandidate أو WaznCandidate في ilaal.py (AST)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoRootOrWaznCreation:
    def test_no_root_candidate_import(self):
        """ilaal.py لا تستورد RootCandidate أو WaznCandidate."""
        content = _ILAAL_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        forbidden = {'RootCandidate', 'WaznCandidate', 'project_wazn', 'WaznProjection'}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert alias.name not in forbidden and alias.asname not in forbidden
                else:
                    for alias in node.names:
                        assert alias.name not in forbidden, (
                            f"ilaal.py تستورد {alias.name!r} — لا يُسمح بذلك"
                        )

    def test_no_wazn_projection_call(self):
        content = _ILAAL_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    assert node.func.id not in ('project_wazn', 'WaznCandidate',
                                                 'RootCandidate'), (
                        f"ilaal.py تستدعي {node.func.id}() مباشرة"
                    )


# ══════════════════════════════════════════════════════════════════════════════
# W3-19: IlaalResolution لا تُعدّل WaznHypothesis
# ══════════════════════════════════════════════════════════════════════════════

class TestIlaalDoesNotMutateHypothesis:
    def test_wazn_hypothesis_unchanged_after_ilaal(self):
        """WaznHypothesis لا تتغير بعد apply_ilaal_resolution()."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        hyp = _ista_hyp()
        original_host = hyp.refined_host
        original_wazn = hyp.proposed_wazn
        original_root = hyp.proposed_root_after
        apply_ilaal_resolution(hyp)
        assert hyp.refined_host == original_host
        assert hyp.proposed_wazn == original_wazn
        assert hyp.proposed_root_after == original_root

    def test_two_calls_same_result(self):
        """apply_ilaal_resolution() نتائجها حتمية — لا حالة داخلية."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        hyp = _ista_hyp()
        r1 = apply_ilaal_resolution(hyp)
        r2 = apply_ilaal_resolution(hyp)
        assert r1.directive == r2.directive
        assert r1.proposed_root == r2.proposed_root


# ══════════════════════════════════════════════════════════════════════════════
# W3-20: to_dict() يحتوي المفاتيح المطلوبة  [يفشل]
# ══════════════════════════════════════════════════════════════════════════════

class TestToDictRequiredKeys:
    _REQUIRED = {'directive', 'proposed_root', 'transformations',
                 'evidence_ids', 'trace_ids', 'residual_codes'}

    def test_accept_to_dict_keys(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        d = apply_ilaal_resolution(_ista_hyp()).to_dict()
        missing = self._REQUIRED - d.keys()
        assert not missing, f"مفاتيح مفقودة في to_dict(): {missing}"

    def test_defer_to_dict_keys(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        d = apply_ilaal_resolution(_fala_hyp('قَالَ')).to_dict()
        missing = self._REQUIRED - d.keys()
        assert not missing, f"مفاتيح مفقودة في to_dict() لـ DEFER: {missing}"

    def test_directive_in_to_dict(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        d = apply_ilaal_resolution(_ista_hyp()).to_dict()
        assert d['directive'] == 'ACCEPT'

    def test_proposed_root_in_to_dict(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        d = apply_ilaal_resolution(_ista_hyp()).to_dict()
        assert d['proposed_root'] == list(('ط', 'و', 'ع'))


# ══════════════════════════════════════════════════════════════════════════════
# W3-21: evidence/trace/residuals محفوظة
# ══════════════════════════════════════════════════════════════════════════════

class TestEvidenceChainPreserved:
    def test_original_evidence_ids_in_result(self):
        """evidence_ids الأصلية من WaznHypothesis محفوظة في IlaalResolution."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        hyp = _ista_hyp()
        result = apply_ilaal_resolution(hyp)
        for ev in hyp.evidence_ids:
            assert ev in result.evidence_ids, (
                f"evidence {ev!r} غائبة من result.evidence_ids: {result.evidence_ids}"
            )

    def test_original_residual_codes_preserved(self):
        """residual_codes الأصلية محفوظة."""
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        hyp = WaznHypothesis(
            refined_host='يَسْتَطِيعُ',
            proposed_wazn='يَسْتَفْعِل',
            ziyadah_detected=('ALIF_WASL', 'SIN', 'TA'),
            proposed_root_after=None,
            confidence='MEDIUM',
            evidence_ids=('ev:test:marker',),
            residual_codes=('residual:test:code',),
        )
        result = apply_ilaal_resolution(hyp)
        assert 'residual:test:code' in result.residual_codes


# ══════════════════════════════════════════════════════════════════════════════
# W3-22–23: IlaalHypothesis الوسيط  [يفشل — الحقول مختلفة]
# ══════════════════════════════════════════════════════════════════════════════

class TestIlaalHypothesisIntermediate:
    def test_ilaal_hypothesis_importable(self):
        """IlaalHypothesis (الوسيط الجديد) قابلة للاستيراد من ilaal.py."""
        try:
            from pipeline.p4_wazn.ilaal import IlaalHypothesis
        except ImportError as e:
            pytest.fail(f"IlaalHypothesis غير قابلة للاستيراد: {e}")

    def test_ilaal_hypothesis_has_surface_element(self):
        """IlaalHypothesis الجديدة تحتوي حقل 'surface_element'."""
        from pipeline.p4_wazn.ilaal import IlaalHypothesis
        fields = {f.name for f in IlaalHypothesis.__dataclass_fields__.values()}
        assert 'surface_element' in fields, (
            f"IlaalHypothesis يفتقد 'surface_element' — الحقول الموجودة: {fields}"
        )

    def test_ilaal_hypothesis_has_underlying_candidate(self):
        from pipeline.p4_wazn.ilaal import IlaalHypothesis
        fields = {f.name for f in IlaalHypothesis.__dataclass_fields__.values()}
        assert 'underlying_candidate' in fields, (
            f"IlaalHypothesis يفتقد 'underlying_candidate'"
        )

    def test_ilaal_hypothesis_has_radical_position(self):
        from pipeline.p4_wazn.ilaal import IlaalHypothesis
        fields = {f.name for f in IlaalHypothesis.__dataclass_fields__.values()}
        assert 'radical_position' in fields

    def test_ilaal_hypothesis_has_transformation_id(self):
        from pipeline.p4_wazn.ilaal import IlaalHypothesis
        fields = {f.name for f in IlaalHypothesis.__dataclass_fields__.values()}
        assert 'transformation_id' in fields

    def test_ilaal_hypothesis_has_wazn_context(self):
        from pipeline.p4_wazn.ilaal import IlaalHypothesis
        fields = {f.name for f in IlaalHypothesis.__dataclass_fields__.values()}
        assert 'wazn_context' in fields

    def test_ilaal_hypothesis_has_conditions_checked(self):
        from pipeline.p4_wazn.ilaal import IlaalHypothesis
        fields = {f.name for f in IlaalHypothesis.__dataclass_fields__.values()}
        assert 'conditions_checked' in fields

    def test_ilaal_hypothesis_is_frozen(self):
        """IlaalHypothesis مُجمَّد."""
        from pipeline.p4_wazn.ilaal import IlaalHypothesis
        ih = IlaalHypothesis(
            surface_element='ي',
            underlying_candidate='و',
            radical_position='AYN',
            transformation_id='WAW_TO_YAA_KASRA_CONDITIONED',
            wazn_context='يَسْتَفْعِل',
            conditions_checked=('KASRA_ENVIRONMENT',),
            evidence_ids=(),
            residual_codes=(),
        )
        with pytest.raises((AttributeError, TypeError)):
            ih.surface_element = 'و'  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# W3-24: IlaalResolution مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestIlaalResolutionFrozen:
    def test_ilaal_resolution_is_frozen(self):
        from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
        result = apply_ilaal_resolution(_ista_hyp())
        with pytest.raises((AttributeError, TypeError)):
            result.directive = 'DEFER'  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# W3-25: لا استيراد من hr2s (AST)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoHr2sImports:
    def test_no_hr2s_imports(self):
        content = _ILAAL_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert 'hr2s' not in alias.name
                else:
                    assert 'hr2s' not in (node.module or ''), (
                        f"ilaal.py تستورد من hr2s: {node.module}"
                    )


# ══════════════════════════════════════════════════════════════════════════════
# W3-26: لا مسارات مطلقة (AST)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoAbsolutePaths:
    def test_no_absolute_paths(self):
        content = _ILAAL_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if val.startswith('/') and len(val) > 2:
                    pytest.fail(f"مسار مطلق في ilaal.py: {val!r}")


# ══════════════════════════════════════════════════════════════════════════════
# W3-27: لا استيراد لـ project_wazn/WaznCandidate/RootCandidate (AST)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoCrossLayerImports:
    def test_no_wazn_projection_imports(self):
        content = _ILAAL_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ''
                assert 'wazn_projection' not in mod and 'wazn_catalog' not in mod, (
                    f"ilaal.py تستورد من طبقة الوزن: {mod}"
                )
