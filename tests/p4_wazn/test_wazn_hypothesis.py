#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_wazn_hypothesis.py — WaznHypothesis P4A-α (فرضية الوزن)

اختبارات T1–T10:
  - رتابة: BLOCK/ACCEPT → None
  - DEFER بلا إشارة زيادة → None
  - كشف MIM_ZIYADAH (مَحَبَّ / مَسْرُورَ)
  - كشف ALIF_WASL+SIN+TA (يَسْتَطِيعُ)
  - الهويات الممنوعة لا تظهر في proposed_root_after
  - ثقة HIGH عند 3 حروف بعد الميم
  - WaznHypothesis مُجمَّد (frozen)
  - لا استيراد من hr2s
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn.hypothesis import WaznHypothesis, build_wazn_hypothesis


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات بناء RootCandidate مصغّرة (لا تستدعي from_projection)
# ══════════════════════════════════════════════════════════════════════════════

def _make_rc(directive: str, surface: str = 'مَحَبَّةِ',
             host_surface: str = 'مَحَبَّةِ',
             residual_codes: tuple = ()) -> RootCandidate:
    return RootCandidate(
        surface=surface,
        host_surface=host_surface,
        directive=directive,
        canonical_root=('ح', 'ب', 'ب') if directive == 'ACCEPT' else None,
        root_profile={},
        evidence_ids=(),
        trace_ids=(),
        residual_codes=residual_codes,
    )


_ZIYADAH_RESIDUAL = ('defer:root_refinement:internal_ziyadah_not_resolved',)


# ══════════════════════════════════════════════════════════════════════════════
# T1: BLOCK → None
# ══════════════════════════════════════════════════════════════════════════════

class TestBlockReturnsNone:
    def test_block_root_candidate_returns_none(self):
        rc = _make_rc('BLOCK', surface='مِنْ', host_surface='مِنْ')
        result = build_wazn_hypothesis(
            refined_host='مِنْ',
            root_candidate=rc,
            removed_markers=(),
            residual_codes=(),
        )
        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
# T2: ACCEPT → None
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptReturnsNone:
    def test_accept_root_candidate_returns_none(self):
        rc = _make_rc('ACCEPT', surface='ضَرَبَ', host_surface='ضَرَبَ')
        result = build_wazn_hypothesis(
            refined_host='ضَرَبَ',
            root_candidate=rc,
            removed_markers=(),
            residual_codes=(),
        )
        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
# T3: DEFER بلا إشارة زيادة → None
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferNoZiyadahSignal:
    def test_defer_no_ziyadah_signal_returns_none(self):
        rc = _make_rc('DEFER', surface='قَالَ', host_surface='قَالَ',
                      residual_codes=('defer:root:hollow_underlying_radical_unresolved',))
        result = build_wazn_hypothesis(
            refined_host='قَالَ',
            root_candidate=rc,
            removed_markers=(),
            residual_codes=('defer:root:hollow_underlying_radical_unresolved',),
        )
        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
# T4: DEFER مع بادئة مَ + رمز تحفظ الزيادة → WaznHypothesis بـ MIM_ZIYADAH
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferMimPrefixHypothesis:
    def test_defer_mim_prefix_produces_hypothesis(self):
        rc = _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مَحَبَّ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        assert isinstance(result, WaznHypothesis)
        assert 'MIM_ZIYADAH' in result.ziyadah_detected

    def test_mim_prefix_proposed_root_is_trilateral(self):
        rc = _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مَحَبَّ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        assert result.proposed_root_after is not None
        assert len(result.proposed_root_after) == 3


# ══════════════════════════════════════════════════════════════════════════════
# T5: مَسْرُورَ → MIM_ZIYADAH (مَفْعُول)
# ══════════════════════════════════════════════════════════════════════════════

class TestMasruurMimZiyadah:
    def test_masruur_mim_ziyadah(self):
        rc = _make_rc('DEFER', surface='مَسْرُورَةٌ', host_surface='مَسْرُورَةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مَسْرُورَ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        assert 'MIM_ZIYADAH' in result.ziyadah_detected
        if result.proposed_root_after is not None:
            assert len(result.proposed_root_after) == 3


# ══════════════════════════════════════════════════════════════════════════════
# T6: يَسْتَطِيعُ → ALIF_WASL + SIN + TA
# ══════════════════════════════════════════════════════════════════════════════

class TestYastatiuHypothesis:
    def test_yastatiiu_hypothesis(self):
        rc = _make_rc('DEFER', surface='يَسْتَطِيعُ', host_surface='يَسْتَطِيعُ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='يَسْتَطِيعُ',
            root_candidate=rc,
            removed_markers=(),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        detected = result.ziyadah_detected
        has_ista = (
            'ALIF_WASL' in detected
            or 'SIN' in detected
            or 'TA' in detected
            or 'ISTA_PREFIX' in detected
        )
        assert has_ista, f"expected ista-pattern in {detected}"

    def test_ista_prefix_proposed_root(self):
        rc = _make_rc('DEFER', surface='يَسْتَطِيعُ', host_surface='يَسْتَطِيعُ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='يَسْتَطِيعُ',
            root_candidate=rc,
            removed_markers=(),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        if result.proposed_root_after is not None:
            assert len(result.proposed_root_after) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# T7: proposed_root_after لا يحتوي هوية ممنوعة
# ══════════════════════════════════════════════════════════════════════════════

_PROHIBITED_IDENTITIES = frozenset({"ا", "ى", "أ", "إ", "ؤ", "ئ", "آ"})


class TestNoProhibitedIdentity:
    def test_proposed_root_no_prohibited_identity(self):
        rc = _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مَحَبَّ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        if result.proposed_root_after is not None:
            for ch in result.proposed_root_after:
                assert ch not in _PROHIBITED_IDENTITIES, (
                    f"prohibited identity {ch!r} in proposed_root_after")


# ══════════════════════════════════════════════════════════════════════════════
# T8: ثقة HIGH عند 3 حروف أساسية بعد الميم
# ══════════════════════════════════════════════════════════════════════════════

class TestHighConfidenceThreeConsonants:
    def test_mim_prefix_three_consonant_high_confidence(self):
        rc = _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مَحَبَّ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        assert result.confidence == 'HIGH'


# ══════════════════════════════════════════════════════════════════════════════
# T9: WaznHypothesis مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestHypothesisIsFrozen:
    def test_hypothesis_is_frozen(self):
        rc = _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مَحَبَّ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        with pytest.raises((AttributeError, TypeError)):
            result.confidence = "LOW"  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# T10: لا استيراد من hr2s في hypothesis.py
# ══════════════════════════════════════════════════════════════════════════════

class TestNoHr2sImport:
    def test_no_hr2s_import_in_hypothesis_module(self):
        src = (pathlib.Path(__file__).parent.parent.parent
               / 'pipeline' / 'p4_wazn' / 'hypothesis.py')
        tree = ast.parse(src.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith('hr2s'), (
                    f"forbidden import from hr2s: {node.module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith('hr2s'), (
                        f"forbidden import of hr2s: {alias.name}")


# ══════════════════════════════════════════════════════════════════════════════
# T11: Pattern C — مُفْتَعِل (MIM_ZIYADAH + IFTIEAL_TA)
# ══════════════════════════════════════════════════════════════════════════════

class TestMuftalPattern:
    """Pattern C: مُفْتَعِل — ميم زائدة + تاء افتعال داخلية."""

    def test_muftaris_produces_muftal_hypothesis(self):
        """الْمُفْتَرِسَةُ: مُفْتَرِسَ → مُفْتَعِل → (ف،ر،س)."""
        rc = _make_rc('DEFER', surface='الْمُفْتَرِسَةُ',
                      host_surface='الْمُفْتَرِسَةُ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مُفْتَرِسَ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        assert result.proposed_wazn == 'مُفْتَعِل'
        assert 'MIM_ZIYADAH' in result.ziyadah_detected
        assert 'IFTIEAL_TA' in result.ziyadah_detected

    def test_muftaris_proposed_root_fa_ayn_lam(self):
        rc = _make_rc('DEFER', surface='الْمُفْتَرِسَةُ',
                      host_surface='الْمُفْتَرِسَةُ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مُفْتَرِسَ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        assert result.proposed_root_after == ('ف', 'ر', 'س')

    def test_muftaris_confidence_high(self):
        rc = _make_rc('DEFER', surface='الْمُفْتَرِسَةُ',
                      host_surface='الْمُفْتَرِسَةُ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مُفْتَرِسَ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        assert result.confidence == 'HIGH'

    def test_muftal_not_triggered_for_simple_mim(self):
        """مَحَبَّ: ميم بسيطة (بلا تاء عند موضع 1) → Pattern A، لا Pattern C."""
        rc = _make_rc('DEFER', surface='مَحَبَّةٌ', host_surface='مَحَبَّةٌ',
                      residual_codes=_ZIYADAH_RESIDUAL)
        result = build_wazn_hypothesis(
            refined_host='مَحَبَّ',
            root_candidate=rc,
            removed_markers=('NOMINAL_TA_MARBUTA',),
            residual_codes=_ZIYADAH_RESIDUAL,
        )
        assert result is not None
        # Pattern A (MIM_ZIYADAH فقط) — ليس مُفْتَعِل
        assert 'IFTIEAL_TA' not in result.ziyadah_detected
