#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p3_candidate/test_root_relicensing.py — Root Re-Licensing P3.11

اختبارات R1–R11:
  - جذر ثلاثي سليم → ACCEPT
  - proposed_root_after=None → DEFER (إعلال معلّق، لا مانع قاطع)
  - هوية ممنوعة (ا) → BLOCK
  - هوية ممنوعة (ى) → BLOCK
  - ثقة LOW → DEFER
  - جذر غير ثلاثي (len==2) → DEFER
  - ء محفوظة كهوية جذرية صالحة → ACCEPT
  - RootRelicensingResult مُجمَّد
  - ACCEPT بلا failure_reason
  - DEFER مع failure_reason (DEFER≠ absence of failure_reason)
  - BLOCK فقط للموانع القاطعة (هوية ممنوعة / حرف غير عربي)
"""

from __future__ import annotations

import pytest

from pipeline.p4_wazn.hypothesis import WaznHypothesis
from pipeline.p3_candidate.root_relicensing import (
    RootRelicensingResult,
    relicense_root_from_wazn_hypothesis,
)


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

def _make_alignment(proposed_root_after) -> tuple:
    """يولّد radical_alignment تلقائيًا لوزن مَفْعَلَة (م + FA/AYN/LAM)."""
    if not proposed_root_after or len(proposed_root_after) < 3:
        return ()
    r = proposed_root_after
    return (
        ('م', 'MIM_ZIYADAH'),
        (r[0], 'FA'),
        (r[1], 'AYN'),
        (r[2], 'LAM'),
    )


def _make_hypothesis(
    proposed_root_after=('ح', 'ب', 'ب'),
    confidence='HIGH',
    ziyadah=('MIM_ZIYADAH',),
    proposed_wazn='مَفْعَلَة',
    refined_host='مَحَبَّ',
) -> WaznHypothesis:
    # radical_alignment مطلوب للوصول إلى ACCEPT بعد W4.1
    alignment = _make_alignment(proposed_root_after)
    return WaznHypothesis(
        refined_host=refined_host,
        proposed_wazn=proposed_wazn,
        ziyadah_detected=ziyadah,
        proposed_root_after=proposed_root_after,
        confidence=confidence,
        evidence_ids=('ev:hypothesis:mim',),
        residual_codes=(),
        radical_alignment=alignment,
        removed_elements=(('م', 'MIM_ZIYADAH'),) if 'MIM_ZIYADAH' in ziyadah else (),
    )


# ══════════════════════════════════════════════════════════════════════════════
# R1: جذر ثلاثي سليم → ACCEPT
# ══════════════════════════════════════════════════════════════════════════════

class TestValidTrilateralAccepts:
    def test_valid_trilateral_root_accepts(self):
        hyp = _make_hypothesis(proposed_root_after=('ح', 'ب', 'ب'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'ACCEPT'

    def test_accept_carries_proposed_root(self):
        hyp = _make_hypothesis(proposed_root_after=('ك', 'ت', 'ب'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'ACCEPT'
        assert result.canonical_root == ('ك', 'ت', 'ب')


# ══════════════════════════════════════════════════════════════════════════════
# R2: proposed_root_after=None → DEFER (إعلال معلّق، لا مانع قاطع)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoneProposedRootDefers:
    def test_none_proposed_root_defers(self):
        """None = استخراج غير مكتمل (مثل: يَسْتَطِيعُ — إعلال معلّق) → DEFER لا BLOCK."""
        hyp = _make_hypothesis(proposed_root_after=None)
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'DEFER'
        assert result.failure_reason == 'defer:relicensing:proposed_root_extraction_incomplete'

    def test_none_root_has_failure_reason(self):
        hyp = _make_hypothesis(proposed_root_after=None)
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.failure_reason is not None


# ══════════════════════════════════════════════════════════════════════════════
# R3: ا في الجذر → BLOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestProhibitedIdentityBlocks:
    def test_prohibited_identity_blocks(self):
        hyp = _make_hypothesis(proposed_root_after=('ق', 'ا', 'ل'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'BLOCK'
        assert result.failure_reason == 'block:relicensing:prohibited_root_identity'

    def test_alif_hamza_normalized_to_hamza_accepts(self):
        """W4: أ تُطبَّع إلى ء قبل الفحص → ACCEPT (لا BLOCK)."""
        hyp = _make_hypothesis(proposed_root_after=('أ', 'خ', 'ذ'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        # أ → ء (هوية صالحة)؛ الممنوع هو ا/ى فقط
        assert result.directive == 'ACCEPT'
        assert result.canonical_root == ('ء', 'خ', 'ذ')


# ══════════════════════════════════════════════════════════════════════════════
# R4: ى في الجذر → BLOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestAlifMaqsuraIdentityBlocks:
    def test_alif_maqsura_identity_blocks(self):
        hyp = _make_hypothesis(proposed_root_after=('ر', 'م', 'ى'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'BLOCK'
        assert result.failure_reason == 'block:relicensing:prohibited_root_identity'


# ══════════════════════════════════════════════════════════════════════════════
# R5: ثقة LOW → DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestLowConfidenceDefers:
    def test_low_confidence_defers(self):
        hyp = _make_hypothesis(confidence='LOW')
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'DEFER'
        assert result.failure_reason == 'defer:relicensing:low_confidence_hypothesis'


# ══════════════════════════════════════════════════════════════════════════════
# R6: جذر غير ثلاثي (len==2) → DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestNonTrilateralDefers:
    def test_non_trilateral_defers(self):
        hyp = _make_hypothesis(proposed_root_after=('ق', 'ل'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'DEFER'
        assert result.failure_reason == 'defer:relicensing:non_trilateral_proposed_root'


# ══════════════════════════════════════════════════════════════════════════════
# R7: ء محفوظة كهوية جذرية صالحة → ACCEPT
# ══════════════════════════════════════════════════════════════════════════════

class TestHamzaPreservedAsValid:
    def test_hamza_preserved_as_valid(self):
        hyp = _make_hypothesis(proposed_root_after=('ق', 'ر', 'ء'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'ACCEPT'

    def test_hamza_in_fa_position(self):
        hyp = _make_hypothesis(proposed_root_after=('ء', 'م', 'ر'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# R8: RootRelicensingResult مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestResultIsFrozen:
    def test_result_is_frozen(self):
        hyp = _make_hypothesis()
        result = relicense_root_from_wazn_hypothesis(hyp)
        with pytest.raises((AttributeError, TypeError)):
            result.directive = "BLOCK"  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# R9: ACCEPT بلا failure_reason
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptHasNoFailureReason:
    def test_accept_has_no_failure_reason(self):
        hyp = _make_hypothesis(proposed_root_after=('ض', 'ر', 'ب'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'ACCEPT'
        assert result.failure_reason is None


# ══════════════════════════════════════════════════════════════════════════════
# R10: BLOCK فقط للموانع القاطعة
# ══════════════════════════════════════════════════════════════════════════════

class TestBlockOnlyForHardObstructions:
    def test_prohibited_identity_is_block(self):
        """هوية ممنوعة = مانع قاطع → BLOCK."""
        hyp = _make_hypothesis(proposed_root_after=('ق', 'ا', 'ل'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'BLOCK'
        assert result.failure_reason is not None

    def test_none_root_is_defer_not_block(self):
        """None = معلّق → DEFER (لا BLOCK)."""
        hyp = _make_hypothesis(proposed_root_after=None)
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'DEFER'

    def test_block_has_failure_reason_when_prohibited(self):
        hyp = _make_hypothesis(proposed_root_after=('ى', 'م', 'ن'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'BLOCK'
        assert result.failure_reason is not None
        assert 'block' in result.failure_reason


# ══════════════════════════════════════════════════════════════════════════════
# R11: يَسْتَطِيعُ — proposed_root=None → DEFER بسبب إعلال معلّق
# ══════════════════════════════════════════════════════════════════════════════

class TestYastatiuDefer:
    def test_yastatiiu_type_defers(self):
        """فرضية يَسْتَفْعِل بدون جذر محدد → DEFER (إعلال معلّق)."""
        hyp = WaznHypothesis(
            refined_host='يَسْتَطِيعُ',
            proposed_wazn='يَسْتَفْعِل',
            ziyadah_detected=('ALIF_WASL', 'SIN', 'TA'),
            proposed_root_after=None,
            confidence='MEDIUM',
            evidence_ids=('ev:hypothesis:ista_prefix',),
            residual_codes=(),
        )
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'DEFER'
        assert 'incomplete' in result.failure_reason or 'incomplete' in (result.failure_reason or '')
