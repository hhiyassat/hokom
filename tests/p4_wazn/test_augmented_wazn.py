#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_augmented_wazn.py — اختبارات AugmentedWaznShortcut
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُغطي:
  - وحدة build_augmented_phase4a() لجميع الصيغ (II–X)
  - تكامل الأنبوب الحي: p4a + p4b + p4c + p4d لثلاث كلمات مرجعية
  - العقود: source_path='augmented_direct', wazn_id صحيح، final_directive='ACCEPT'
  - حالات الحافة: عائلة غير معروفة → DEFER دفاعي
"""

from __future__ import annotations

import types

import pytest

# ── دعم استيراد المشروع بلا conftest مركزي ─────────────────────────────────
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات وثوابت
# ══════════════════════════════════════════════════════════════════════════════

def _make_augmented_analysis(form_family, root, confidence='HIGH'):
    """بنِّ AugmentedRootAnalysis وهمي بالحقول المطلوبة."""
    from pipeline.p2_augmented.models import AugmentedRootAnalysis
    return AugmentedRootAnalysis(
        form_family      = form_family,
        trilateral_root  = tuple(root),
        past_surface     = 'فَعَّلَ',
        imperfect_prefix = None,
        confidence       = confidence,
        evidence_ids     = (f'test:aug:{form_family}',),
        trace_ids        = (f'trace:aug:{form_family}',),
        residual_codes   = (),
    )


def _make_root_candidate(root=('ف', 'ع', 'ل'), surface='فَعَّلَ', host='فَعَّلَ'):
    """بنِّ RootCandidate وهمي بالحقول المطلوبة."""
    return types.SimpleNamespace(
        surface         = surface,
        host_surface    = host,
        directive       = 'ACCEPT',
        canonical_root  = tuple(root),
        root_profile    = {'source_engine': 'HOKOM_AUGMENTED_ENGINE'},
        evidence_ids    = ('test:root:ev',),
        trace_ids       = ('test:root:tr',),
        residual_codes  = (),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1.  اختبارات بناء Phase4AResult مباشرة (build_augmented_phase4a)
# ══════════════════════════════════════════════════════════════════════════════

class TestBuildAugmentedPhase4A:
    """اختبارات وحدة build_augmented_phase4a()."""

    def setup_method(self):
        from pipeline.p4_wazn.augmented_wazn import build_augmented_phase4a
        self.build = build_augmented_phase4a

    # ── T01: FORM_II → FA33ALA ────────────────────────────────────────────
    def test_T01_form_ii_returns_accept(self):
        """FORM_II → final_directive='ACCEPT'."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert result.final_directive == 'ACCEPT'

    def test_T02_form_ii_source_path_augmented_direct(self):
        """FORM_II → source_path='augmented_direct'."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert result.source_path == 'augmented_direct'

    def test_T03_form_ii_final_wazn_fa33ala(self):
        """FORM_II → final_wazn='FA33ALA'."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'FA33ALA'

    def test_T04_form_ii_wazn_projection_accept(self):
        """FORM_II → wazn_projection.directive == ACCEPT."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        wp = result.wazn_projection
        assert wp is not None
        from pipeline.p4_wazn.models import WaznDirective
        assert wp.directive == WaznDirective.ACCEPT

    def test_T05_form_ii_selected_wazn_id(self):
        """FORM_II → wazn_projection.selected_wazn.wazn_id == 'FA33ALA'."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        sw = result.wazn_projection.selected_wazn
        assert sw is not None
        assert sw.wazn_id == 'FA33ALA'

    def test_T06_form_ii_wazn_family(self):
        """FORM_II → selected_wazn.wazn_family == 'form_II_verb'."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_II_verb'

    def test_T07_form_ii_root_slots_complete(self):
        """FORM_II → selected_wazn.root_slots_complete == True."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert result.wazn_projection.selected_wazn.root_slots_complete is True

    def test_T08_form_ii_canonical_root_in_wazn_projection(self):
        """FORM_II → wazn_projection.canonical_root == trilateral_root."""
        root = ('ع', 'و', 'ض')
        aug = _make_augmented_analysis('FORM_II', root)
        rc  = _make_root_candidate(root)
        result = self.build(aug, rc)
        assert result.wazn_projection.canonical_root == root

    def test_T09_form_v_wazn_id_tafa33ala(self):
        """FORM_V → final_wazn='TAFA33ALA'."""
        aug = _make_augmented_analysis('FORM_V', ('ك', 'ل', 'م'))
        rc  = _make_root_candidate(('ك', 'ل', 'م'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'TAFA33ALA'
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_V_verb'

    def test_T10_form_viii_wazn_id_ifta3ala(self):
        """FORM_VIII → final_wazn='IFTA3ALA'."""
        aug = _make_augmented_analysis('FORM_VIII', ('ف', 'ر', 'س'))
        rc  = _make_root_candidate(('ف', 'ر', 'س'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'IFTA3ALA'
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_VIII_verb'

    def test_T11_form_x_wazn_id_istaf3ala(self):
        """FORM_X → final_wazn='ISTAF3ALA'."""
        aug = _make_augmented_analysis('FORM_X', ('خ', 'ر', 'ج'))
        rc  = _make_root_candidate(('خ', 'ر', 'ج'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'ISTAF3ALA'
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_X_verb'

    def test_T12_form_iii_wazn_id_fa3ala(self):
        """FORM_III → final_wazn='FA3ALA'."""
        aug = _make_augmented_analysis('FORM_III', ('ق', 'ت', 'ل'))
        rc  = _make_root_candidate(('ق', 'ت', 'ل'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'FA3ALA'
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_III_verb'

    def test_T13_form_iv_wazn_id_af3al(self):
        """FORM_IV → final_wazn='AF3AL'."""
        aug = _make_augmented_analysis('FORM_IV', ('س', 'ل', 'م'))
        rc  = _make_root_candidate(('س', 'ل', 'م'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'AF3AL'
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_IV_verb'

    def test_T14_form_vi_wazn_id_tafa3ala(self):
        """FORM_VI → final_wazn='TAFA3ALA'."""
        aug = _make_augmented_analysis('FORM_VI', ('ج', 'م', 'ع'))
        rc  = _make_root_candidate(('ج', 'م', 'ع'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'TAFA3ALA'
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_VI_verb'

    def test_T15_form_vii_wazn_id_infa3ala(self):
        """FORM_VII → final_wazn='INFA3ALA'."""
        aug = _make_augmented_analysis('FORM_VII', ('ك', 'س', 'ر'))
        rc  = _make_root_candidate(('ك', 'س', 'ر'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'INFA3ALA'
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_VII_verb'

    def test_T16_form_ix_wazn_id_if3alla(self):
        """FORM_IX → final_wazn='IF3ALLA'."""
        aug = _make_augmented_analysis('FORM_IX', ('ح', 'م', 'ر'))
        rc  = _make_root_candidate(('ح', 'م', 'ر'))
        result = self.build(aug, rc)
        assert result.final_wazn == 'IF3ALLA'
        assert result.wazn_projection.selected_wazn.wazn_family == 'form_IX_verb'

    def test_T17_initial_root_directive_accept(self):
        """initial_root_directive == 'ACCEPT' لجميع الصيغ."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert result.initial_root_directive == 'ACCEPT'

    def test_T18_promoted_root_candidate_none(self):
        """promoted_root_candidate == None (لا ترخيص مطلوب)."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert result.promoted_root_candidate is None

    def test_T19_wazn_hypothesis_none(self):
        """wazn_hypothesis == None (لا حاجة لفرضية)."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert result.wazn_hypothesis is None

    def test_T20_evidence_includes_wazn_id(self):
        """evidence_ids تحتوي على معرف الوزن المباشر."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        ev = result.evidence_ids
        assert any('FA33ALA' in e for e in ev), (
            f'expected FA33ALA evidence, got {ev}'
        )

    def test_T21_trace_includes_augmented_direct(self):
        """trace_ids تحتوي على 'p4a:augmented_direct'."""
        aug = _make_augmented_analysis('FORM_V', ('ك', 'ل', 'م'))
        rc  = _make_root_candidate(('ك', 'ل', 'م'))
        result = self.build(aug, rc)
        assert 'p4a:augmented_direct' in result.trace_ids

    def test_T22_source_root_candidate_augmented_engine(self):
        """wazn_projection.source_root_candidate == 'HOKOM_AUGMENTED_ENGINE'."""
        aug = _make_augmented_analysis('FORM_X', ('خ', 'ر', 'ج'))
        rc  = _make_root_candidate(('خ', 'ر', 'ج'))
        result = self.build(aug, rc)
        assert result.wazn_projection.source_root_candidate == 'HOKOM_AUGMENTED_ENGINE'

    def test_T23_unknown_form_family_returns_defer(self):
        """عائلة غير معروفة → final_directive='DEFER' (دفاعي)."""
        # AugmentedRootAnalysis لا تقبل FORM_XI — نُحاكي الحالة مباشرةً
        # عبر AugmentedRootAnalysis مع form_family صالحة ثم نبدّل المعامل.
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        aug_bad = types.SimpleNamespace(
            form_family     = 'FORM_UNKNOWN',
            trilateral_root = ('ع', 'و', 'ض'),
            evidence_ids    = (),
            trace_ids       = (),
            residual_codes  = (),
        )
        rc = _make_root_candidate(('ع', 'و', 'ض'))
        from pipeline.p4_wazn.augmented_wazn import build_augmented_phase4a
        result = build_augmented_phase4a(aug_bad, rc)
        assert result.final_directive == 'DEFER'
        assert 'unknown_form' in result.source_path
        assert any('FORM_UNKNOWN' in c for c in result.residual_codes)

    def test_T24_result_is_phase4a_result(self):
        """النتيجة من نوع Phase4AResult (مجمّد)."""
        from pipeline.p4_wazn.phase4a_orchestrator import Phase4AResult
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        assert isinstance(result, Phase4AResult)

    def test_T25_result_is_frozen(self):
        """Phase4AResult لا يقبل التعديل."""
        aug = _make_augmented_analysis('FORM_VIII', ('ف', 'ر', 'س'))
        rc  = _make_root_candidate(('ف', 'ر', 'س'))
        result = self.build(aug, rc)
        with pytest.raises((AttributeError, TypeError)):
            result.final_directive = 'DEFER'  # type: ignore[misc]

    def test_T26_to_dict_serializable(self):
        """Phase4AResult.to_dict() يُرجع dict قابل للتسلسل."""
        aug = _make_augmented_analysis('FORM_II', ('ع', 'و', 'ض'))
        rc  = _make_root_candidate(('ع', 'و', 'ض'))
        result = self.build(aug, rc)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d['final_directive'] == 'ACCEPT'
        assert d['source_path'] == 'augmented_direct'
        assert d['final_wazn'] == 'FA33ALA'


# ══════════════════════════════════════════════════════════════════════════════
# 2.  اختبارات الأنبوب الحي (Live Pipeline)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope='module')
def pipeline():
    """Import hokom() once for the whole module."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from hokom_pipeline import hokom
    return hokom


class TestLivePipeline_AugmentedWazn:
    """اختبارات تكامل الأنبوب الحي للصيغ المزيدة."""

    # ──────────────────────────────────────────────────────────────────────────
    # FORM_II: يُعَوِّضُهُمْ
    # ──────────────────────────────────────────────────────────────────────────

    def test_L01_yu3awwidu_phase4a_accept(self, pipeline):
        """يُعَوِّضُهُمْ (FORM_II) → Phase4A ACCEPT."""
        r = pipeline('يُعَوِّضُهُمْ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT'

    def test_L02_yu3awwidu_source_path(self, pipeline):
        """يُعَوِّضُهُمْ → source_path='augmented_direct'."""
        r = pipeline('يُعَوِّضُهُمْ')
        p4a = r['phase4a_result']
        assert p4a.source_path == 'augmented_direct'

    def test_L03_yu3awwidu_wazn_id(self, pipeline):
        """يُعَوِّضُهُمْ → final_wazn='FA33ALA'."""
        r = pipeline('يُعَوِّضُهُمْ')
        p4a = r['phase4a_result']
        assert p4a.final_wazn == 'FA33ALA'

    def test_L04_yu3awwidu_phase4b_accept(self, pipeline):
        """يُعَوِّضُهُمْ → Phase4B ACCEPT (BAB_FORM_II)."""
        r = pipeline('يُعَوِّضُهُمْ')
        p4b = r.get('phase4b_result')
        assert p4b is not None
        assert p4b.final_directive == 'ACCEPT'
        assert p4b.final_bab == 'BAB_FORM_II'

    def test_L05_yu3awwidu_phase4c_accept(self, pipeline):
        """يُعَوِّضُهُمْ → Phase4C ACCEPT (masdar تَفْعِيل)."""
        r = pipeline('يُعَوِّضُهُمْ')
        p4c = r.get('phase4c_result')
        assert p4c is not None
        assert p4c.final_directive == 'ACCEPT'

    def test_L06_yu3awwidu_root(self, pipeline):
        """يُعَوِّضُهُمْ → root=(ع, و, ض)."""
        r = pipeline('يُعَوِّضُهُمْ')
        aug = r.get('augmented_analysis')
        assert aug is not None
        assert aug.form_family == 'FORM_II'
        rc = r.get('root_candidate')
        assert rc is not None
        assert rc.canonical_root == ('ع', 'و', 'ض')

    # ──────────────────────────────────────────────────────────────────────────
    # FORM_V: تَأَكَّدَتِ
    # ──────────────────────────────────────────────────────────────────────────

    def test_L07_taakkada_phase4a_accept(self, pipeline):
        """تَأَكَّدَتِ (FORM_V) → Phase4A ACCEPT."""
        r = pipeline('تَأَكَّدَتِ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT'

    def test_L08_taakkada_source_path(self, pipeline):
        """تَأَكَّدَتِ → source_path='augmented_direct'."""
        r = pipeline('تَأَكَّدَتِ')
        p4a = r['phase4a_result']
        assert p4a.source_path == 'augmented_direct'

    def test_L09_taakkada_wazn_id(self, pipeline):
        """تَأَكَّدَتِ → final_wazn='TAFA33ALA'."""
        r = pipeline('تَأَكَّدَتِ')
        p4a = r['phase4a_result']
        assert p4a.final_wazn == 'TAFA33ALA'

    def test_L10_taakkada_phase4b(self, pipeline):
        """تَأَكَّدَتِ → Phase4B ACCEPT (BAB_FORM_V)."""
        r = pipeline('تَأَكَّدَتِ')
        p4b = r.get('phase4b_result')
        assert p4b is not None
        assert p4b.final_directive == 'ACCEPT'
        assert p4b.final_bab == 'BAB_FORM_V'

    def test_L11_taakkada_masdar(self, pipeline):
        """تَأَكَّدَتِ → Phase4C ACCEPT (FORM_V masdar تَفَعُّل)."""
        r = pipeline('تَأَكَّدَتِ')
        p4c = r.get('phase4c_result')
        assert p4c is not None
        assert p4c.final_directive == 'ACCEPT'
        # FORM_V masdar pattern is تَفَعُّل
        pattern = getattr(p4c, 'final_masdar_pattern', None)
        if pattern is not None:
            assert 'تَفَعُّل' in pattern or 'فَعُّل' in pattern, (
                f'FORM_V masdar pattern expected تَفَعُّل got {pattern!r}'
            )

    # ──────────────────────────────────────────────────────────────────────────
    # FORM_VIII: مُفْتَرِسَةُ
    # ──────────────────────────────────────────────────────────────────────────

    def test_L12_muftarisa_phase4a_accept(self, pipeline):
        """مُفْتَرِسَةُ (FORM_VIII) → Phase4A ACCEPT."""
        r = pipeline('مُفْتَرِسَةُ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT'

    def test_L13_muftarisa_source_path(self, pipeline):
        """مُفْتَرِسَةُ → source_path='augmented_direct'."""
        r = pipeline('مُفْتَرِسَةُ')
        p4a = r['phase4a_result']
        assert p4a.source_path == 'augmented_direct'

    def test_L14_muftarisa_wazn_id(self, pipeline):
        """مُفْتَرِسَةُ → final_wazn='IFTA3ALA'."""
        r = pipeline('مُفْتَرِسَةُ')
        p4a = r['phase4a_result']
        assert p4a.final_wazn == 'IFTA3ALA'

    def test_L15_muftarisa_root(self, pipeline):
        """مُفْتَرِسَةُ → root=(ف, ر, س)."""
        r = pipeline('مُفْتَرِسَةُ')
        aug = r.get('augmented_analysis')
        assert aug is not None
        assert aug.form_family == 'FORM_VIII'
        rc = r.get('root_candidate')
        assert rc is not None
        assert rc.canonical_root == ('ف', 'ر', 'س')

    def test_L16_muftarisa_phase4c_accept(self, pipeline):
        """مُفْتَرِسَةُ → Phase4C ACCEPT (FORM_VIII masdar اِفْتِعَال)."""
        r = pipeline('مُفْتَرِسَةُ')
        p4c = r.get('phase4c_result')
        assert p4c is not None
        assert p4c.final_directive == 'ACCEPT'

    # ──────────────────────────────────────────────────────────────────────────
    # FORM_X: يَسْتَخْرِجُ
    # ──────────────────────────────────────────────────────────────────────────

    def test_L17_yastakhriju_phase4a_accept(self, pipeline):
        """يَسْتَخْرِجُ (FORM_X) → Phase4A ACCEPT via augmented_direct."""
        r = pipeline('يَسْتَخْرِجُ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT'
        assert p4a.source_path == 'augmented_direct'
        assert p4a.final_wazn == 'ISTAF3ALA'

    def test_L18_yastakhriju_phase4b_accept(self, pipeline):
        """يَسْتَخْرِجُ → Phase4B ACCEPT (BAB_FORM_X)."""
        r = pipeline('يَسْتَخْرِجُ')
        p4b = r.get('phase4b_result')
        assert p4b is not None
        assert p4b.final_directive == 'ACCEPT'
        assert p4b.final_bab == 'BAB_FORM_X'

    def test_L19_yastakhriju_phase4c_accept(self, pipeline):
        """يَسْتَخْرِجُ → Phase4C ACCEPT (FORM_X masdar اِسْتِفْعَال)."""
        r = pipeline('يَسْتَخْرِجُ')
        p4c = r.get('phase4c_result')
        assert p4c is not None
        assert p4c.final_directive == 'ACCEPT'

    # ──────────────────────────────────────────────────────────────────────────
    # FORM_V: تَكَلَّمَ (تحقق انتكاس)
    # ──────────────────────────────────────────────────────────────────────────

    def test_L20_takallama_phase4a_still_accept(self, pipeline):
        """تَكَلَّمَ (FORM_V) — لا انتكاس: Phase4A ACCEPT عبر augmented_direct."""
        r = pipeline('تَكَلَّمَ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT'
        assert p4a.source_path == 'augmented_direct'
        assert p4a.final_wazn == 'TAFA33ALA'


# ══════════════════════════════════════════════════════════════════════════════
# 3.  اختبار خريطة AUGMENTED_WAZN_MAP
# ══════════════════════════════════════════════════════════════════════════════

class TestAugmentedWaznMap:
    """تحقق من سلامة AUGMENTED_WAZN_MAP."""

    def setup_method(self):
        from pipeline.p4_wazn.augmented_wazn import AUGMENTED_WAZN_MAP
        self.wazn_map = AUGMENTED_WAZN_MAP

    def test_map_covers_all_forms(self):
        """الخريطة تغطي FORM_II حتى FORM_X."""
        expected = {f'FORM_{r}' for r in ['II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']}
        assert expected == set(self.wazn_map.keys())

    def test_map_entries_are_3_tuples(self):
        """كل إدخال هو ثلاثية (wazn_id, wazn_pattern, wazn_family)."""
        for form, entry in self.wazn_map.items():
            assert isinstance(entry, tuple), f'{form}: expected tuple'
            assert len(entry) == 3, f'{form}: expected 3-tuple'

    def test_map_wazn_ids_non_empty(self):
        """wazn_id غير فارغ لجميع الصيغ."""
        for form, (wazn_id, _, _) in self.wazn_map.items():
            assert wazn_id, f'{form}: wazn_id must not be empty'

    def test_map_families_verbal(self):
        """جميع عائلات الأوزان من العائلات الفعلية المزيدة."""
        for form, (_, _, family) in self.wazn_map.items():
            assert 'verb' in family, (
                f'{form}: expected verbal family, got {family!r}'
            )

    def test_form_ii_entry(self):
        """FORM_II = (FA33ALA, فَعَّلَ, form_II_verb)."""
        wazn_id, pattern, family = self.wazn_map['FORM_II']
        assert wazn_id == 'FA33ALA'
        assert family == 'form_II_verb'

    def test_form_viii_entry(self):
        """FORM_VIII = (IFTA3ALA, اِفْتَعَلَ, form_VIII_verb)."""
        wazn_id, pattern, family = self.wazn_map['FORM_VIII']
        assert wazn_id == 'IFTA3ALA'
        assert family == 'form_VIII_verb'
