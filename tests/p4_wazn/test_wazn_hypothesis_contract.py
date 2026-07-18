#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_wazn_hypothesis_contract.py — W2: WaznHypothesis Contract

عقود W2 (الاختبارات ستفشل أولًا، ثم نُعدِّل hypothesis.py):

  W2-1  : DEFER-only — لا فرضية لـ ACCEPT
  W2-2  : DEFER-only — لا فرضية لـ BLOCK
  W2-3  : لا حقل canonical_root في WaznHypothesis
  W2-4  : proposed_root_after هو فرضية — ليس جذرًا مؤكدًا
  W2-5  : refined_host محفوظ (قيمة مطبَّعة)
  W2-6  : لا تعديل نصي لـ refined_host (لا حذف حرفي)
  W2-7  : ziyadah_detected رموز أسكي — ليست حروفًا عربية
  W2-8  : WaznHypothesis مُجمَّد (frozen)
  W2-9  : حقل radical_alignment موجود وبنيته صحيحة  ← يفشل حتى التعديل
  W2-10 : حقل removed_elements موجود وبنيته صحيحة   ← يفشل حتى التعديل
  W2-11 : to_proposed_root_resolution() ينتج ProposedRootResolution ← يفشل
  W2-12 : Pattern A (مَحَبَّ) — محاذاة كاملة       ← يفشل حتى التعديل
  W2-13 : Pattern C (مُفْتَرِسَ) — محاذاة كاملة   ← يفشل حتى التعديل
  W2-14 : Pattern B (يَسْتَطِيعُ) — محاذاة جزئية  ← يفشل حتى التعديل
  W2-15 : ProposedRootResolution.proposed_root = proposed_root_after ← يفشل
  W2-16 : WaznHypothesis لا تستطيع استدعاء project_wazn مباشرة (AST)
  W2-17 : لا استيراد من hr2s داخل hypothesis.py (AST)
  W2-18 : لا مسارات مطلقة في hypothesis.py (AST)
"""

from __future__ import annotations

import ast
import pathlib
from typing import Optional

import pytest

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn.hypothesis import (
    WaznHypothesis,
    ProposedRootResolution,
    build_wazn_hypothesis,
)


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

_ZIYADAH_RES = ('defer:root_refinement:internal_ziyadah_not_resolved',)


def _rc(directive: str, surface: str = 'مَحَبَّ') -> RootCandidate:
    return RootCandidate(
        surface=surface,
        host_surface=surface,
        directive=directive,
        canonical_root=None,
        root_profile={},
        evidence_ids=(),
        trace_ids=(),
        residual_codes=_ZIYADAH_RES,
    )


def _build(refined_host: str, directive: str = 'DEFER',
           residual_codes: tuple = _ZIYADAH_RES) -> Optional[WaznHypothesis]:
    return build_wazn_hypothesis(
        refined_host=refined_host,
        root_candidate=_rc(directive, surface=refined_host),
        removed_markers=(),
        residual_codes=residual_codes,
    )


_HYP_SRC = (pathlib.Path(__file__).parent.parent.parent
             / 'pipeline' / 'p4_wazn' / 'hypothesis.py')


# ══════════════════════════════════════════════════════════════════════════════
# W2-1: DEFER-only — ACCEPT يُعيد None
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferOnlyAcceptReturnsNone:
    def test_accept_rc_returns_none(self):
        """build_wazn_hypothesis يعيد None لـ ACCEPT RootCandidate."""
        result = _build('مَحَبَّ', directive='ACCEPT')
        assert result is None

    def test_accept_with_ziyadah_residual_still_returns_none(self):
        """حتى مع رمز الزيادة، ACCEPT → None (الرتابة)."""
        rc = RootCandidate(
            surface='مَحَبَّ',
            host_surface='مَحَبَّ',
            directive='ACCEPT',
            canonical_root=('ح', 'ب', 'ب'),
            root_profile={},
            evidence_ids=(),
            trace_ids=(),
            residual_codes=_ZIYADAH_RES,
        )
        result = build_wazn_hypothesis(
            refined_host='مَحَبَّ',
            root_candidate=rc,
            removed_markers=(),
            residual_codes=_ZIYADAH_RES,
        )
        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
# W2-2: DEFER-only — BLOCK يُعيد None
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferOnlyBlockReturnsNone:
    def test_block_rc_returns_none(self):
        """build_wazn_hypothesis يعيد None لـ BLOCK RootCandidate."""
        result = _build('مِنْ', directive='BLOCK', residual_codes=())
        assert result is None

    def test_block_with_ziyadah_still_returns_none(self):
        """BLOCK + رمز زيادة → لا يزال None."""
        result = _build('مِنْ', directive='BLOCK', residual_codes=_ZIYADAH_RES)
        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
# W2-3: لا حقل canonical_root في WaznHypothesis
# ══════════════════════════════════════════════════════════════════════════════

class TestNoCanonicalRootField:
    def test_wazn_hypothesis_has_no_canonical_root_field(self):
        """WaznHypothesis لا تحتوي حقل canonical_root — يستخدم proposed_root_after."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert not hasattr(hyp, 'canonical_root'), (
            "WaznHypothesis لا يجب أن تحتوي حقل canonical_root — "
            "فقط proposed_root_after كمقترح غير مرخَّص"
        )

    def test_proposed_root_after_is_optional_tuple(self):
        """proposed_root_after إما tuple أو None — ليس كائن RootResolution."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert isinstance(hyp.proposed_root_after, (tuple, type(None)))


# ══════════════════════════════════════════════════════════════════════════════
# W2-4: proposed_root_after فرضية — ليس جذرًا مؤكدًا
# ══════════════════════════════════════════════════════════════════════════════

class TestProposedRootAfterIsHypothetical:
    def test_proposed_root_after_lacks_root_acceptance_status(self):
        """proposed_root_after مجرد tuple من الحروف — ليس RootResolution."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert hyp.proposed_root_after is not None
        # يجب أن يكون tuple بسيط، لا كائن معقد
        assert all(isinstance(c, str) for c in hyp.proposed_root_after)

    def test_proposed_root_after_has_no_directive_attribute(self):
        """proposed_root_after لا يحمل directive — ليس RootResolution."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert not hasattr(hyp.proposed_root_after, 'directive')

    def test_hollow_root_proposed_root_after_none(self):
        """في حالات الإعلال، proposed_root_after=None (معلق لـ P4A-β)."""
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        assert hyp.proposed_root_after is None, (
            "يَسْتَطِيعُ → الجذر المعتل (ط،و،ع) → proposed_root_after=None "
            "لأن الجذر الأوسط يحتاج إعلالًا لا تحله هذه المرحلة"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W2-5: refined_host محفوظ (مطبَّع وليس مقطوعًا)
# ══════════════════════════════════════════════════════════════════════════════

class TestRefinedHostPreserved:
    def test_refined_host_in_hypothesis_equals_normalized_input(self):
        """hypothesis.refined_host = النموذج المطبَّع للمدخل."""
        from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda
        input_host = 'مَحَبَّ'
        expected = normalize_shadda(normalize_hamza(input_host))
        hyp = _build(input_host)
        assert hyp is not None
        assert hyp.refined_host == expected

    def test_refined_host_length_not_shorter_than_root(self):
        """refined_host لم يُقطع — لا يقل عن طول proposed_root_after."""
        from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        normalized = normalize_shadda(normalize_hamza('مَحَبَّ'))
        # المضيف المخزَّن ≥ الجذر المقترح في الطول المنطقي
        root_len = len(hyp.proposed_root_after) if hyp.proposed_root_after else 0
        # عدد الحروف الأساسية في refined_host >= طول الجذر
        diacritics = frozenset('ًٌٍَُِّْٰٕٓٔ')
        consonant_count = sum(1 for c in hyp.refined_host if c not in diacritics and c != ' ')
        assert consonant_count >= root_len


# ══════════════════════════════════════════════════════════════════════════════
# W2-6: لا تعديل نصي (الزيادة ليست حذفًا من النص)
# ══════════════════════════════════════════════════════════════════════════════

class TestZiyadahNotTextualDeletion:
    def test_proposed_root_not_substring_of_refined_host(self):
        """proposed_root_after لا يُنتَج بحذف حروف من refined_host مباشرة.

        الجذر مُشتَق من تحليل صرفي، لا من str.replace أو text slicing.
        يُتحقق بالتأكد أن الجذر يحتوي حروفًا موجودة في المضيف (لا مُختلقة).
        """
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        # الجذر (ح،ب،ب) — كل حرف منه موجود في النموذج المطبَّع
        diacritics = frozenset('ًٌٍَُِّْٰٕٓٔ')
        host_chars = set(c for c in hyp.refined_host if c not in diacritics)
        for ch in (hyp.proposed_root_after or ()):
            assert ch in host_chars, (
                f"حرف جذري '{ch}' غير موجود في المضيف — "
                "يجب أن يكون الجذر مُشتَقًّا من الحروف الأصلية"
            )

    def test_refined_host_is_same_object_value_not_modified(self):
        """build_wazn_hypothesis لا يُعيد مضيفًا مُعدَّلًا — يُخزِّن قيمة محددة."""
        from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda
        input_host = 'مُفْتَرِسَ'
        hyp = _build(input_host)
        assert hyp is not None
        normalized = normalize_shadda(normalize_hamza(input_host))
        assert hyp.refined_host == normalized


# ══════════════════════════════════════════════════════════════════════════════
# W2-7: ziyadah_detected رموز أسكي — ليست حروفًا عربية
# ══════════════════════════════════════════════════════════════════════════════

class TestZiyadahDetectedIsSymbolic:
    def test_ziyadah_detected_contains_ascii_symbols_pattern_a(self):
        """Pattern A: ziyadah_detected = ('MIM_ZIYADAH',) — رمز ASCII."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        for marker in hyp.ziyadah_detected:
            assert marker.isascii(), (
                f"ziyadah_detected يجب أن يحتوي رموز ASCII فقط، ليس: {marker!r}"
            )
            assert marker.isupper() or '_' in marker, (
                f"الرمز يجب أن يكون UPPER_CASE: {marker!r}"
            )

    def test_ziyadah_detected_contains_ascii_symbols_pattern_b(self):
        """Pattern B: ziyadah_detected = ('ALIF_WASL','SIN','TA') — رموز ASCII."""
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        for marker in hyp.ziyadah_detected:
            assert marker.isascii(), f"ziyadah_detected: {marker!r} ليس ASCII"

    def test_ziyadah_detected_contains_ascii_symbols_pattern_c(self):
        """Pattern C: ziyadah_detected = ('MIM_ZIYADAH','IFTIEAL_TA') — رموز ASCII."""
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        for marker in hyp.ziyadah_detected:
            assert marker.isascii(), f"ziyadah_detected: {marker!r} ليس ASCII"

    def test_ziyadah_detected_does_not_contain_arabic_chars(self):
        """ziyadah_detected لا يحتوي حروفًا عربية — ليست نصوصًا مُحذوفة."""
        for host in ('مَحَبَّ', 'مُفْتَرِسَ', 'يَسْتَطِيعُ'):
            hyp = _build(host)
            assert hyp is not None
            for marker in hyp.ziyadah_detected:
                arabic_chars = set('ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
                assert not any(c in arabic_chars for c in marker), (
                    f"ziyadah_detected يحتوي حرفًا عربيًا في {host!r}: {marker!r}"
                )


# ══════════════════════════════════════════════════════════════════════════════
# W2-8: WaznHypothesis مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestWaznHypothesisFrozen:
    def test_wazn_hypothesis_is_frozen(self):
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        with pytest.raises((AttributeError, TypeError)):
            hyp.proposed_root_after = ('x', 'y', 'z')  # type: ignore[misc]

    def test_proposed_root_resolution_is_frozen(self):
        prs = ProposedRootResolution(
            source='WaznHypothesis',
            proposed_root=('ح', 'ب', 'ب'),
            wazn_pattern='مَفْعَلَة',
            ziyadah_removed=(('م', 'MIM_ZIYADAH'),),
            radical_alignment=(
                ('م', 'MIM_ZIYADAH'), ('ح', 'FA'), ('ب', 'AYN'), ('ب', 'LAM'),
            ),
            removed_elements=(('م', 'MIM_ZIYADAH'),),
            confidence='HIGH',
            evidence_ids=(),
            residual_codes=(),
        )
        with pytest.raises((AttributeError, TypeError)):
            prs.proposed_root = ('x', 'y', 'z')  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# W2-9: حقل radical_alignment موجود وبنيته صحيحة  [يفشل حتى التعديل]
# ══════════════════════════════════════════════════════════════════════════════

class TestRadicalAlignmentField:
    def test_radical_alignment_field_exists(self):
        """WaznHypothesis يجب أن يحتوي حقل radical_alignment."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert hasattr(hyp, 'radical_alignment'), (
            "WaznHypothesis يفتقد حقل 'radical_alignment' — "
            "يجب إضافته لتتبع دور كل حرف في المضيف"
        )

    def test_radical_alignment_is_tuple(self):
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert isinstance(hyp.radical_alignment, tuple)

    def test_radical_alignment_non_empty_for_pattern_a(self):
        """Pattern A (مَحَبَّ): radical_alignment غير فارغة."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert len(hyp.radical_alignment) > 0, (
            "radical_alignment فارغة لـ Pattern A — يجب أن تحتوي "
            "على (letter, role) لكل حرف في المضيف المطبَّع"
        )

    def test_radical_alignment_non_empty_for_pattern_c(self):
        """Pattern C (مُفْتَرِسَ): radical_alignment غير فارغة."""
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        assert len(hyp.radical_alignment) > 0

    def test_radical_alignment_non_empty_for_pattern_b(self):
        """Pattern B (يَسْتَطِيعُ): radical_alignment غير فارغة."""
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        assert len(hyp.radical_alignment) > 0

    def test_radical_alignment_entries_are_letter_role_pairs(self):
        """كل عنصر في radical_alignment هو (letter: str, role: str)."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        for entry in hyp.radical_alignment:
            assert isinstance(entry, tuple), f"عنصر ليس tuple: {entry!r}"
            assert len(entry) == 2, f"عنصر ليس زوجًا: {entry!r}"
            letter, role = entry
            assert isinstance(letter, str), f"الحرف ليس str: {letter!r}"
            assert isinstance(role, str), f"الدور ليس str: {role!r}"

    def test_radical_alignment_role_is_ascii(self):
        """أدوار radical_alignment رموز ASCII (FA, AYN, LAM, MIM_ZIYADAH, ...)."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        for _letter, role in hyp.radical_alignment:
            assert role.isascii(), f"الدور ليس ASCII: {role!r}"


# ══════════════════════════════════════════════════════════════════════════════
# W2-10: حقل removed_elements موجود وبنيته صحيحة  [يفشل حتى التعديل]
# ══════════════════════════════════════════════════════════════════════════════

class TestRemovedElementsField:
    def test_removed_elements_field_exists(self):
        """WaznHypothesis يجب أن يحتوي حقل removed_elements."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert hasattr(hyp, 'removed_elements'), (
            "WaznHypothesis يفتقد حقل 'removed_elements' — "
            "يجب إضافته لتوضيح ما حُذف من الزيادة"
        )

    def test_removed_elements_is_tuple(self):
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert isinstance(hyp.removed_elements, tuple)

    def test_removed_elements_non_empty_for_pattern_a(self):
        """Pattern A: removed_elements تشمل الميم على الأقل."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert len(hyp.removed_elements) > 0, (
            "removed_elements فارغة لـ Pattern A — يجب أن تحتوي على الميم"
        )
        # التحقق أن الميم موجودة
        letters = [e[0] for e in hyp.removed_elements]
        assert 'م' in letters, (
            f"الميم غائبة من removed_elements: {hyp.removed_elements}"
        )

    def test_removed_elements_non_empty_for_pattern_c(self):
        """Pattern C (مُفْتَرِسَ): removed_elements تشمل م وت."""
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        assert len(hyp.removed_elements) >= 2, (
            "Pattern C يجب أن يُزيل عنصرين: م (MIM_ZIYADAH) وت (IFTIEAL_TA)"
        )
        letters = {e[0] for e in hyp.removed_elements}
        assert 'م' in letters, "الميم غائبة من removed_elements لـ Pattern C"
        assert 'ت' in letters, "التاء غائبة من removed_elements لـ Pattern C"

    def test_removed_elements_entries_are_letter_reason_pairs(self):
        """كل عنصر في removed_elements هو (letter: str, reason: str)."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        for entry in hyp.removed_elements:
            assert isinstance(entry, tuple) and len(entry) == 2
            letter, reason = entry
            assert isinstance(letter, str)
            assert isinstance(reason, str) and reason.isascii()


# ══════════════════════════════════════════════════════════════════════════════
# W2-11: to_proposed_root_resolution() ينتج ProposedRootResolution  [يفشل]
# ══════════════════════════════════════════════════════════════════════════════

class TestToProposedRootResolution:
    def test_method_exists(self):
        """WaznHypothesis يجب أن يمتلك to_proposed_root_resolution()."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert hasattr(hyp, 'to_proposed_root_resolution'), (
            "WaznHypothesis يفتقد الدالة to_proposed_root_resolution() — "
            "يجب إضافتها لإنتاج ProposedRootResolution صريح"
        )

    def test_method_returns_proposed_root_resolution(self):
        """to_proposed_root_resolution() يعيد كائن ProposedRootResolution."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert isinstance(prs, ProposedRootResolution), (
            f"النوع المُعاد: {type(prs).__name__!r} — المطلوب: ProposedRootResolution"
        )

    def test_proposed_root_matches_proposed_root_after(self):
        """prs.proposed_root = hypothesis.proposed_root_after."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert prs.proposed_root == hyp.proposed_root_after

    def test_source_is_wazn_hypothesis(self):
        """prs.source = 'WaznHypothesis'."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert prs.source == 'WaznHypothesis'

    def test_wazn_pattern_matches(self):
        """prs.wazn_pattern = hypothesis.proposed_wazn."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert prs.wazn_pattern == hyp.proposed_wazn

    def test_radical_alignment_propagated(self):
        """prs.radical_alignment = hypothesis.radical_alignment."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert prs.radical_alignment == hyp.radical_alignment

    def test_hollow_case_proposed_root_none(self):
        """يَسْتَطِيعُ: prs.proposed_root = None (إعلال معلَّق)."""
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert prs.proposed_root is None


# ══════════════════════════════════════════════════════════════════════════════
# W2-12: Pattern A (مَحَبَّ) — محاذاة كاملة  [يفشل حتى التعديل]
# ══════════════════════════════════════════════════════════════════════════════

class TestPatternAAlignment:
    def test_mahabb_proposed_wazn(self):
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert hyp.proposed_wazn == 'مَفْعَلَة'

    def test_mahabb_proposed_root(self):
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert hyp.proposed_root_after == ('ح', 'ب', 'ب')

    def test_mahabb_ziyadah_detected(self):
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert 'MIM_ZIYADAH' in hyp.ziyadah_detected

    def test_mahabb_radical_alignment_starts_with_mim_ziyadah(self):
        """radical_alignment تبدأ بـ (م، MIM_ZIYADAH)."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert len(hyp.radical_alignment) > 0
        first_letter, first_role = hyp.radical_alignment[0]
        assert first_letter == 'م', f"أول حرف ليس م: {first_letter!r}"
        assert first_role == 'MIM_ZIYADAH', f"أول دور ليس MIM_ZIYADAH: {first_role!r}"

    def test_mahabb_removed_elements_contains_mim(self):
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        assert any(e[0] == 'م' and e[1] == 'MIM_ZIYADAH'
                   for e in hyp.removed_elements), (
            f"removed_elements لا تحتوي ('م','MIM_ZIYADAH'): {hyp.removed_elements}"
        )

    def test_mahabb_radical_alignment_contains_fa_ayn_lam(self):
        """radical_alignment تحتوي الخانات الجذرية FA, AYN, LAM."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        roles = {role for _letter, role in hyp.radical_alignment}
        assert 'FA'  in roles, f"FA غائبة من radical_alignment: {roles}"
        assert 'AYN' in roles, f"AYN غائبة من radical_alignment: {roles}"
        assert 'LAM' in roles, f"LAM غائبة من radical_alignment: {roles}"


# ══════════════════════════════════════════════════════════════════════════════
# W2-13: Pattern C (مُفْتَرِسَ) — محاذاة كاملة  [يفشل حتى التعديل]
# ══════════════════════════════════════════════════════════════════════════════

class TestPatternCAlignment:
    def test_muftarisa_proposed_wazn(self):
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        assert hyp.proposed_wazn == 'مُفْتَعِل'

    def test_muftarisa_proposed_root(self):
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        assert hyp.proposed_root_after == ('ف', 'ر', 'س')

    def test_muftarisa_ziyadah_detected(self):
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        assert 'MIM_ZIYADAH' in hyp.ziyadah_detected
        assert 'IFTIEAL_TA' in hyp.ziyadah_detected

    def test_muftarisa_radical_alignment_has_five_entries(self):
        """مُفْتَرِسَ → 5 حروف أساسية: م، ف، ت، ر، س."""
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        assert len(hyp.radical_alignment) == 5, (
            f"radical_alignment لها {len(hyp.radical_alignment)} عنصرًا — المتوقع 5: "
            f"{hyp.radical_alignment}"
        )

    def test_muftarisa_radical_alignment_roles(self):
        """ترتيب الأدوار: MIM_ZIYADAH، FA، IFTIEAL_TA، AYN، LAM."""
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        expected_roles = ('MIM_ZIYADAH', 'FA', 'IFTIEAL_TA', 'AYN', 'LAM')
        actual_roles = tuple(role for _letter, role in hyp.radical_alignment)
        assert actual_roles == expected_roles, (
            f"الأدوار المتوقعة: {expected_roles}\n"
            f"الأدوار الفعلية: {actual_roles}"
        )

    def test_muftarisa_radical_alignment_letters(self):
        """ترتيب الحروف: م، ف، ت، ر، س."""
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        expected_letters = ('م', 'ف', 'ت', 'ر', 'س')
        actual_letters = tuple(letter for letter, _role in hyp.radical_alignment)
        assert actual_letters == expected_letters, (
            f"الحروف المتوقعة: {expected_letters}\n"
            f"الحروف الفعلية: {actual_letters}"
        )

    def test_muftarisa_removed_has_mim_and_ta(self):
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        removed_map = {e[0]: e[1] for e in hyp.removed_elements}
        assert removed_map.get('م') == 'MIM_ZIYADAH', f"removed_elements: {hyp.removed_elements}"
        assert removed_map.get('ت') == 'IFTIEAL_TA', f"removed_elements: {hyp.removed_elements}"


# ══════════════════════════════════════════════════════════════════════════════
# W2-14: Pattern B (يَسْتَطِيعُ) — محاذاة جزئية  [يفشل حتى التعديل]
# ══════════════════════════════════════════════════════════════════════════════

class TestPatternBAlignment:
    def test_yastati_proposed_wazn(self):
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        assert hyp.proposed_wazn == 'يَسْتَفْعِل'

    def test_yastati_ziyadah_detected(self):
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        # ALIF_WASL هو رمز مجموعة الزيادة (السين والتاء تظهر كذلك)
        assert 'ALIF_WASL' in hyp.ziyadah_detected
        assert 'SIN' in hyp.ziyadah_detected
        assert 'TA' in hyp.ziyadah_detected

    def test_yastati_radical_alignment_exists(self):
        """radical_alignment غير فارغة حتى عند proposed_root_after=None."""
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        assert len(hyp.radical_alignment) > 0, (
            "radical_alignment فارغة لـ Pattern B — يجب أن تُظهر البادئة على الأقل"
        )

    def test_yastati_removed_elements_contain_prefix(self):
        """removed_elements تحتوي على أحرف البادئة (يَسْتَ)."""
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        assert len(hyp.removed_elements) >= 2, (
            "removed_elements يجب أن تحتوي على أحرف البادئة "
            f"(ALIF_WASL، SIN، TA): {hyp.removed_elements}"
        )

    def test_yastati_confidence_medium(self):
        """يَسْتَطِيعُ → proposed_root=None → confidence MEDIUM."""
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        assert hyp.confidence in ('MEDIUM', 'LOW')


# ══════════════════════════════════════════════════════════════════════════════
# W2-15: ProposedRootResolution.proposed_root = proposed_root_after  [يفشل]
# ══════════════════════════════════════════════════════════════════════════════

class TestProposedRootResolutionConsistency:
    def test_pattern_a_full_round_trip(self):
        """مَحَبَّ: round-trip كامل عبر to_proposed_root_resolution()."""
        hyp = _build('مَحَبَّ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert prs.proposed_root == ('ح', 'ب', 'ب')
        assert prs.wazn_pattern == 'مَفْعَلَة'
        assert prs.confidence == 'HIGH'

    def test_pattern_c_full_round_trip(self):
        """مُفْتَرِسَ: round-trip كامل."""
        hyp = _build('مُفْتَرِسَ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert prs.proposed_root == ('ف', 'ر', 'س')
        assert prs.wazn_pattern == 'مُفْتَعِل'
        assert prs.radical_alignment == hyp.radical_alignment

    def test_pattern_b_round_trip_none_root(self):
        """يَسْتَطِيعُ: round-trip مع proposed_root=None."""
        hyp = _build('يَسْتَطِيعُ')
        assert hyp is not None
        prs = hyp.to_proposed_root_resolution()
        assert prs.proposed_root is None
        assert prs.source == 'WaznHypothesis'


# ══════════════════════════════════════════════════════════════════════════════
# W2-16: hypothesis.py لا تستدعي project_wazn مباشرة (AST)
# ══════════════════════════════════════════════════════════════════════════════

class TestHypothesisCannotCallProjectWazn:
    def test_no_project_wazn_import_in_hypothesis(self):
        """hypothesis.py لا تستورد project_wazn — لا تجاوز بوابة الترخيص."""
        content = _HYP_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert 'project_wazn' not in alias.name, (
                        "hypothesis.py تستورد project_wazn مباشرة — "
                        "يتجاوز بوابة الترخيص!"
                    )
            elif isinstance(node, ast.ImportFrom):
                # تحقق من module والأسماء
                mod = node.module or ''
                assert 'wazn_projection' not in mod, (
                    f"hypothesis.py تستورد من wazn_projection: {mod}"
                )
                for alias in node.names:
                    assert alias.name != 'project_wazn', (
                        "hypothesis.py تستورد project_wazn — تجاوز للبوابة!"
                    )

    def test_no_wazn_projection_call_in_hypothesis(self):
        """لا نداء لـ project_wazn() أو WaznProjection() في hypothesis.py."""
        content = _HYP_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # تحقق من اسم الدالة المستدعاة
                if isinstance(node.func, ast.Name):
                    assert node.func.id not in ('project_wazn', 'WaznProjection'), (
                        f"hypothesis.py تستدعي {node.func.id}() مباشرة"
                    )
                elif isinstance(node.func, ast.Attribute):
                    assert node.func.attr not in ('project_wazn',), (
                        f"hypothesis.py تستدعي .{node.func.attr}() مباشرة"
                    )


# ══════════════════════════════════════════════════════════════════════════════
# W2-17: لا استيراد من hr2s (AST)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoHr2sImports:
    def test_no_hr2s_imports(self):
        content = _HYP_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert 'hr2s' not in alias.name
                else:
                    mod = node.module or ''
                    assert 'hr2s' not in mod, (
                        f"hypothesis.py تستورد من hr2s: {mod}"
                    )


# ══════════════════════════════════════════════════════════════════════════════
# W2-18: لا مسارات مطلقة في hypothesis.py (AST)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoAbsolutePaths:
    def test_no_absolute_paths(self):
        content = _HYP_SRC.read_text(encoding='utf-8')
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if val.startswith('/') and len(val) > 2:
                    pytest.fail(f"مسار مطلق في hypothesis.py: {val!r}")
