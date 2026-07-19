#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_wazn_projection_contract.py — W5 WaznProjection Contract
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

اختبارات W5-1..W5-19:
  W5-1  : empty catalog → DEFER (لا يُطابق) (القاعدة 6)
  W5-2  : مَسْرُور → ACCEPT مَفْعُول (root س ر ر) (حالة مرجعية)
  W5-3  : مُفْتَرِس → DEFER (مُفْتَعِل غير موجود في catalog) (حالة مرجعية)
  W5-4  : يَسْتَطِيعُ عبر المنسّق → BLOCK (يَسْتَفْعِل ليس في catalog)
  W5-5  : قَالَ / نَامَ / بَاعَ → NOT_OPENED (RootCandidate DEFER)
  W5-6  : مِنْ / هِيَ → NOT_OPENED (RootCandidate BLOCK)
  W5-7  : W5 لا يستدعي HR2S (القاعدة 13)
  W5-8  : W5 لا يستدعي root resolution (القاعدة 14)
  W5-9  : W5 لا يستنتج الباب (القاعدة 15)
  W5-10 : ACCEPT → selected_wazn ضمن candidate_awzan (القاعدة 3)
  W5-11 : ACCEPT → candidate_awzan لا يزيد عن وزن واحد (القاعدة 4)
  W5-12 : مَحَبَّ → DEFER (وزن اسمي محتاج ترخيصًا) أو BLOCK
  W5-13 : WaznProjection مُجمَّد
  W5-14 : DEFER بلا selected_wazn → final_wazn=None
  W5-15 : ء تبقى ء في الإسقاط النهائي
  W5-16 : WaznProjection.to_dict() — حقول ACCEPT كاملة
  W5-17 : stage_state صحيح لكل directive
  W5-18 : تحقق من checksums الملفات المجمَّدة
  W5-19 : تحقق أن 20 اختبارًا سابقًا في test_wazn_projection.py لا تزال موجودة
"""

from __future__ import annotations

import hashlib
import inspect
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn import project_wazn
from pipeline.p4_wazn.models import WaznDirective, WaznStageState
from pipeline.p4_wazn.phase4a_orchestrator import project_wazn_with_relicensing


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

_ROOT = Path(__file__).resolve().parents[2]


def _rc(surface, host, directive, root, *, evidence=(), trace=(), residual=()):
    return RootCandidate(
        surface=surface,
        host_surface=host,
        directive=directive,
        canonical_root=root,
        root_profile={},
        evidence_ids=evidence,
        trace_ids=trace,
        residual_codes=residual,
        source_projection='RootProjection',
    )


def _rc_defer(surface):
    return _rc(surface, surface, 'DEFER', None,
               residual=('defer:root_refinement:internal_ziyadah_not_resolved',))


def _rc_block(surface):
    return _rc(surface, surface, 'BLOCK', None)


# ══════════════════════════════════════════════════════════════════════════════
# W5-1 : empty catalog → DEFER (القاعدة 6)
# ══════════════════════════════════════════════════════════════════════════════

class TestEmptyCatalogDefers:
    def test_empty_catalog_defers(self):
        """catalog فارغ → لا مطابقة → DEFER (بنية محتملة بلا وزن مرخَّص)."""
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')), catalog=())
        assert p.directive == WaznDirective.DEFER
        assert p.selected_wazn is None
        assert any('unlicensed' in r or 'defer' in r for r in p.residual_codes)

    def test_empty_catalog_candidate_awzan_empty_or_deferred(self):
        p = project_wazn(_rc('كَتَبَ', 'كَتَبَ', 'ACCEPT', ('ك', 'ت', 'ب')), catalog=())
        assert p.directive == WaznDirective.DEFER
        assert p.selected_wazn is None


# ══════════════════════════════════════════════════════════════════════════════
# W5-2 : مَسْرُور → ACCEPT مَفْعُول (root س ر ر) (حالة مرجعية)
# ══════════════════════════════════════════════════════════════════════════════

class TestMasruurReferenceCaseAccepts:
    def test_masruur_accepts(self):
        """مَسْرُور + root (س، ر، ر) → ACCEPT مَفْعُول."""
        p = project_wazn(_rc('مَسْرُور', 'مَسْرُور', 'ACCEPT', ('س', 'ر', 'ر')))
        assert p.directive == WaznDirective.ACCEPT

    def test_masruur_selected_mafuul(self):
        p = project_wazn(_rc('مَسْرُور', 'مَسْرُور', 'ACCEPT', ('س', 'ر', 'ر')))
        assert p.selected_wazn is not None
        assert p.selected_wazn.wazn_pattern == 'مَفْعُول'

    def test_masruur_selected_in_candidate_awzan(self):
        p = project_wazn(_rc('مَسْرُور', 'مَسْرُور', 'ACCEPT', ('س', 'ر', 'ر')))
        assert p.selected_wazn in p.candidate_awzan

    def test_masruur_canonical_root_preserved(self):
        p = project_wazn(_rc('مَسْرُور', 'مَسْرُور', 'ACCEPT', ('س', 'ر', 'ر')))
        assert p.canonical_root == ('س', 'ر', 'ر')

    def test_masruur_no_prohibited_radical(self):
        p = project_wazn(_rc('مَسْرُور', 'مَسْرُور', 'ACCEPT', ('س', 'ر', 'ر')))
        for a in p.root_slot_alignment:
            assert a.root_identity not in ('ا', 'ى')


# ══════════════════════════════════════════════════════════════════════════════
# W5-3 : مُفْتَرِس → DEFER (مُفْتَعِل غير موجود في catalog حاليًا)
# ══════════════════════════════════════════════════════════════════════════════

class TestMuftarisReferenceCaseDefers:
    def test_muftaris_defers_incomplete_catalog(self):
        """مُفْتَرِس (اسم فاعل VIII) → DEFER: مُفْتَعِل غير مرخَّص في catalog الحالي."""
        p = project_wazn(_rc('مُفْتَرِس', 'مُفْتَرِس', 'ACCEPT', ('ف', 'ر', 'س')))
        assert p.directive == WaznDirective.DEFER

    def test_muftaris_no_selected_wazn(self):
        p = project_wazn(_rc('مُفْتَرِس', 'مُفْتَرِس', 'ACCEPT', ('ف', 'ر', 'س')))
        assert p.selected_wazn is None

    def test_muftaris_canonical_root_preserved(self):
        p = project_wazn(_rc('مُفْتَرِس', 'مُفْتَرِس', 'ACCEPT', ('ف', 'ر', 'س')))
        assert p.canonical_root == ('ف', 'ر', 'س')


# ══════════════════════════════════════════════════════════════════════════════
# W5-4 : يَسْتَطِيعُ عبر المنسّق → يَسْتَفْعِل غير في catalog → BLOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestYastatiuOrchestratorDefer:
    def test_yastatiiu_via_orchestrator_wazn_defers(self):
        """يَسْتَطِيعُ: الجذر (ط، و، ع) محلول لكن يَسْتَفْعِل (mudaric X) غير في catalog.
        غياب وزن في catalog = نقص ترخيص → DEFER (لا BLOCK)."""
        rc = _rc_defer('يَسْتَطِيعُ')
        result = project_wazn_with_relicensing(rc)
        assert result.source_path == 'hypothesis_relicensed'
        assert result.relicensing_result is not None
        assert result.relicensing_result.directive == 'ACCEPT'
        assert result.wazn_projection is not None
        # نقص catalog → DEFER، لا BLOCK
        assert result.final_directive == 'DEFER'

    def test_yastatiiu_canonical_root_taa_waw_ayn(self):
        """الجذر المرخَّص = (ط، و، ع)."""
        rc = _rc_defer('يَسْتَطِيعُ')
        result = project_wazn_with_relicensing(rc)
        assert result.relicensing_result.canonical_root == ('ط', 'و', 'ع')

    def test_yastatiiu_wazn_defer_residual(self):
        """wazn_projection.residual يحتوي defer:wazn:catalog_pattern_not_licensed."""
        rc = _rc_defer('يَسْتَطِيعُ')
        result = project_wazn_with_relicensing(rc)
        assert result.wazn_projection is not None
        assert 'defer:wazn:catalog_pattern_not_licensed' in result.wazn_projection.residual_codes

    def test_yastatiiu_wazn_projection_canonical_root_set(self):
        """wazn_projection يحتفظ بالجذر حتى عند DEFER."""
        rc = _rc_defer('يَسْتَطِيعُ')
        result = project_wazn_with_relicensing(rc)
        if result.wazn_projection is not None:
            assert result.wazn_projection.canonical_root == ('ط', 'و', 'ع')


# ══════════════════════════════════════════════════════════════════════════════
# W5-5 : قَالَ / نَامَ / بَاعَ → NOT_OPENED (DEFER لا يفتح W5)
# ══════════════════════════════════════════════════════════════════════════════

class TestHollowVerbsNotOpened:
    @pytest.mark.parametrize("surface", ['قَالَ', 'نَامَ', 'بَاعَ'])
    def test_hollow_defer_not_opened(self, surface):
        p = project_wazn(_rc_defer(surface))
        assert p.directive == WaznDirective.DEFER
        assert p.stage_state == WaznStageState.NOT_OPENED
        assert p.selected_wazn is None
        assert p.candidate_awzan == ()


# ══════════════════════════════════════════════════════════════════════════════
# W5-6 : مِنْ / هِيَ → NOT_OPENED (BLOCK لا يفتح W5)
# ══════════════════════════════════════════════════════════════════════════════

class TestFunctionWordsNotOpened:
    @pytest.mark.parametrize("surface", ['مِنْ', 'هِيَ', 'أَنَّهُمْ'])
    def test_blocked_candidate_not_opened(self, surface):
        p = project_wazn(_rc_block(surface))
        assert p.directive == WaznDirective.BLOCK
        assert p.stage_state == WaznStageState.NOT_OPENED
        assert p.selected_wazn is None


# ══════════════════════════════════════════════════════════════════════════════
# W5-7 : W5 لا يستدعي HR2S (القاعدة 13)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoHr2sCall:
    def test_wazn_projection_source_has_no_hr2s_import(self):
        """wazn_projection.py لا يستورد من hr2s (import فعلي)."""
        import pipeline.p4_wazn.wazn_projection as mod
        src = inspect.getsource(mod)
        # نبحث عن import فعلي، لا مجرد ذِكر في تعليق
        assert 'import hr2s' not in src, (
            "wazn_projection.py must not import hr2s")
        assert 'from hr2s' not in src, (
            "wazn_projection.py must not import from hr2s")

    def test_wazn_projection_does_not_import_morphology_engine(self):
        import pipeline.p4_wazn.wazn_projection as mod
        src = inspect.getsource(mod)
        assert 'MorphologyEngine' not in src, (
            "wazn_projection.py must not use MorphologyEngine")

    def test_project_wazn_does_not_call_hr2s_at_runtime(self):
        """تأكيد وقت التشغيل: hr2s.morphology غير موجود في globals."""
        import pipeline.p4_wazn.wazn_projection as mod
        mod_globals = set(mod.__dict__.keys())
        assert 'MorphologyEngine' not in mod_globals
        # تشغيل فعلي
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        assert p.directive == WaznDirective.ACCEPT


# ══════════════════════════════════════════════════════════════════════════════
# W5-8 : W5 لا يستدعي root resolution (القاعدة 14)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoRootResolutionCall:
    def test_wazn_projection_does_not_import_root_resolution(self):
        """wazn_projection.py لا يستورد root_resolution."""
        import pipeline.p4_wazn.wazn_projection as mod
        src = inspect.getsource(mod)
        assert 'root_resolution' not in src, (
            "wazn_projection.py must not call root_resolution")

    def test_wazn_projection_does_not_call_resolve_morphology(self):
        import pipeline.p4_wazn.wazn_projection as mod
        src = inspect.getsource(mod)
        assert 'resolve_morphology' not in src

    def test_project_wazn_does_not_mutate_canonical_root(self):
        """project_wazn لا يُعيد حساب canonical_root — يستعمله كما هو."""
        root_in = ('ض', 'ر', 'ب')
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', root_in))
        assert p.canonical_root == root_in


# ══════════════════════════════════════════════════════════════════════════════
# W5-9 : W5 لا يستنتج الباب (القاعدة 15)
# ══════════════════════════════════════════════════════════════════════════════

class TestNoBabInference:
    def test_to_dict_has_no_bab_key(self):
        """to_dict() لا يحتوي على حقل باب."""
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        d = p.to_dict()
        assert 'bab' not in d, f"unexpected 'bab' in to_dict(): {list(d.keys())}"
        assert 'باب' not in d

    def test_wazn_projection_model_has_no_bab_attribute(self):
        from pipeline.p4_wazn.models import WaznProjection
        fields = {f.name for f in WaznProjection.__dataclass_fields__.values()}
        assert 'bab' not in fields
        assert 'verb_class' not in fields

    def test_wazn_candidate_model_has_no_bab_attribute(self):
        from pipeline.p4_wazn.models import WaznCandidate
        fields = {f.name for f in WaznCandidate.__dataclass_fields__.values()}
        assert 'bab' not in fields


# ══════════════════════════════════════════════════════════════════════════════
# W5-10 : ACCEPT → selected_wazn ضمن candidate_awzan (القاعدة 3)
# ══════════════════════════════════════════════════════════════════════════════

class TestSelectedWaznInCandidates:
    @pytest.mark.parametrize("surface,root,expected_pattern", [
        ('ضَرَبَ', ('ض', 'ر', 'ب'), 'فَعَلَ'),
        ('مَسْرُور', ('س', 'ر', 'ر'), 'مَفْعُول'),
        ('قَرَأَ', ('ق', 'ر', 'ء'), 'فَعَلَ'),
    ])
    def test_selected_wazn_in_candidate_awzan(self, surface, root, expected_pattern):
        p = project_wazn(_rc(surface, surface, 'ACCEPT', root))
        assert p.directive == WaznDirective.ACCEPT
        assert p.selected_wazn in p.candidate_awzan
        assert p.selected_wazn.wazn_pattern == expected_pattern


# ══════════════════════════════════════════════════════════════════════════════
# W5-11 : ACCEPT → candidate_awzan contains exactly selected_wazn (القاعدة 4)
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptHasSingleCandidate:
    def test_accept_single_candidate_awzan(self):
        """ACCEPT يضمن وزنًا مرخَّصًا واحدًا فقط."""
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        assert p.directive == WaznDirective.ACCEPT
        assert len(p.candidate_awzan) == 1
        assert p.candidate_awzan[0] is p.selected_wazn


# ══════════════════════════════════════════════════════════════════════════════
# W5-12 : مَحَبَّ / وزن اسمي → DEFER أو ACCEPT مَفْعَلَة
# ══════════════════════════════════════════════════════════════════════════════

class TestNominalWaznCase:
    def test_mahabb_defers_nominal_wazn(self):
        """مَحَبَّ + root (ح، ب، ب): الوزن مَفْعَلَة غير موجود (catalog لا يغطي النمط الاسمي).
        يجب أن يكون DEFER (نقص catalog) لا ACCEPT ولا BLOCK."""
        p = project_wazn(_rc('مَحَبَّ', 'مَحَبَّ', 'ACCEPT', ('ح', 'ب', 'ب')))
        assert p.directive == WaznDirective.DEFER
        assert p.selected_wazn is None
        # residual يُوثّق السبب
        assert any('unlicensed' in r or 'defer' in r for r in p.residual_codes)

    def test_mahabb_canonical_root_not_mutated(self):
        p = project_wazn(_rc('مَحَبَّ', 'مَحَبَّ', 'ACCEPT', ('ح', 'ب', 'ب')))
        assert p.canonical_root == ('ح', 'ب', 'ب')


# ══════════════════════════════════════════════════════════════════════════════
# W5-12b : structurally plausible + no catalog match → DEFER, never BLOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestMissingCatalogDefers:
    def test_known_root_plausible_host_missing_catalog_defers(self):
        """جذر معروف + مضيف بنيويًا ممكن + لا وزن في catalog → DEFER لا BLOCK."""
        # قَالَ مع جذر (ق، و، ل): الجذر ضعيف العين، السطح ممكن بنيويًا
        p = project_wazn(_rc('قَالَ', 'قَالَ', 'ACCEPT', ('ق', 'و', 'ل')))
        assert p.directive == WaznDirective.DEFER
        assert p.selected_wazn is None

    def test_weak_ayn_missing_catalog_defers(self):
        """نَامَ + root (ن، و، م): عين ضعيفة، مطابقة catalog غائبة → DEFER."""
        p = project_wazn(_rc('نَامَ', 'نَامَ', 'ACCEPT', ('ن', 'و', 'م')))
        assert p.directive == WaznDirective.DEFER

    def test_weak_root_structurally_plausible_residual_has_defer_code(self):
        """residual يحتوي على كود defer — لا block."""
        p = project_wazn(_rc('يَسْتَطِيعُ', 'يَسْتَطِيعُ', 'ACCEPT', ('ط', 'و', 'ع')))
        assert p.directive == WaznDirective.DEFER
        assert all('block' not in r for r in p.residual_codes)
        assert 'defer:wazn:catalog_pattern_not_licensed' in p.residual_codes

    def test_contradictory_alignment_blocks(self):
        """جذر لا يظهر في السطح + حروف غير زيادة → BLOCK (تناقض بنيوي)."""
        # root (ط، و، ع) مع surface كَتَبَ: لا ط ولا ع في السطح، كتب ليست زيادة
        p = project_wazn(_rc('كَتَبَ', 'كَتَبَ', 'ACCEPT', ('ط', 'و', 'ع')))
        assert p.directive == WaznDirective.BLOCK
        assert 'block:wazn:no_licensed_pattern' in p.residual_codes

    def test_strong_root_no_catalog_match_blocks(self):
        """جذر سليم (بلا و/ي) + لا مطابقة + لا بنية ممكنة → BLOCK."""
        # root (ض، ر، ب) مع surface مختلف تمامًا
        p = project_wazn(_rc('قَتَلَ', 'قَتَلَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        assert p.directive == WaznDirective.BLOCK


# ══════════════════════════════════════════════════════════════════════════════
# W5-13 : WaznProjection مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestWaznProjectionIsFrozen:
    def test_projection_is_frozen(self):
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        with pytest.raises((AttributeError, TypeError)):
            p.directive = WaznDirective.BLOCK  # type: ignore[misc]

    def test_wazn_candidate_is_frozen(self):
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        with pytest.raises((AttributeError, TypeError)):
            p.selected_wazn.wazn_id = 'HACKED'  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# W5-14 : DEFER → selected_wazn=None و final_wazn=None
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferHasNoSelectedWazn:
    def test_defer_no_selected_wazn(self):
        p = project_wazn(_rc_defer('قَالَ'))
        assert p.selected_wazn is None

    def test_block_no_selected_wazn(self):
        p = project_wazn(_rc_block('مِنْ'))
        assert p.selected_wazn is None

    def test_defer_from_empty_catalog_no_selected_wazn(self):
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')), catalog=())
        assert p.selected_wazn is None


# ══════════════════════════════════════════════════════════════════════════════
# W5-15 : ء تبقى ء في الإسقاط النهائي
# ══════════════════════════════════════════════════════════════════════════════

class TestHamzaPreservedInProjection:
    def test_hamza_in_lam_position_preserved(self):
        p = project_wazn(_rc('قَرَأَ', 'قَرَأَ', 'ACCEPT', ('ق', 'ر', 'ء')))
        assert p.canonical_root == ('ق', 'ر', 'ء')
        lam_aligns = [a for a in p.root_slot_alignment if a.root_identity == 'ء']
        assert lam_aligns, "ء must appear as root_identity in alignment"

    def test_hamza_in_fa_position_preserved(self):
        p = project_wazn(_rc('أَخَذَ', 'أَخَذَ', 'ACCEPT', ('ء', 'خ', 'ذ')))
        assert p.directive in (WaznDirective.ACCEPT, WaznDirective.DEFER)
        if p.directive == WaznDirective.ACCEPT:
            assert p.canonical_root[0] == 'ء'


# ══════════════════════════════════════════════════════════════════════════════
# W5-16 : to_dict() — حقول ACCEPT كاملة
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptToDictComplete:
    _REQUIRED_KEYS = {
        'input_surface', 'analyzed_host', 'normalized_host', 'canonical_root',
        'directive', 'stage_state', 'candidate_awzan', 'selected_wazn',
        'root_slot_alignment', 'ziyadah_slots', 'weak_operations',
        'unresolved_operations', 'inflectional_suffixes',
        'evidence_ids', 'trace_ids', 'residual_codes',
        'source_root_candidate', 'projection_version',
    }

    def test_accept_to_dict_has_required_keys(self):
        import json
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        d = p.to_dict()
        missing = self._REQUIRED_KEYS - set(d.keys())
        assert not missing, f"missing keys: {missing}"

    def test_accept_to_dict_json_serializable(self):
        import json
        p = project_wazn(_rc('مَسْرُور', 'مَسْرُور', 'ACCEPT', ('س', 'ر', 'ر')))
        json.dumps(p.to_dict(), ensure_ascii=False)

    def test_accept_directive_value_is_string(self):
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        d = p.to_dict()
        assert d['directive'] == 'ACCEPT'
        assert isinstance(d['directive'], str)


# ══════════════════════════════════════════════════════════════════════════════
# W5-17 : stage_state صحيح لكل directive
# ══════════════════════════════════════════════════════════════════════════════

class TestStageStateConsistency:
    def test_accept_stage_completed(self):
        p = project_wazn(_rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')))
        assert p.stage_state == WaznStageState.COMPLETED

    def test_defer_from_block_not_opened(self):
        p = project_wazn(_rc_block('مِنْ'))
        assert p.stage_state == WaznStageState.NOT_OPENED

    def test_defer_from_root_defer_not_opened(self):
        p = project_wazn(_rc_defer('قَالَ'))
        assert p.stage_state == WaznStageState.NOT_OPENED

    def test_defer_from_multiple_patterns_deferred(self):
        from pipeline.p4_wazn.wazn_catalog import WaznDefinition, TemplateCell
        tmpl = (TemplateCell('FA', 'FATHA'), TemplateCell('AIN', 'FATHA'),
                TemplateCell('LAM', 'FINAL'))
        def mk(wid, rank):
            return WaznDefinition(
                wazn_id=wid, pattern='فَعَلَ', root_arity=3, family='twin',
                applicable_surface_classes=('verb',), root_slots=('FA', 'AIN', 'LAM'),
                licensed_ziyadah_slots=(), licensed_shadda_behavior=(),
                licensed_weak_operations=(), evidence_rank=rank, source='test',
                template=tmpl)
        p = project_wazn(
            _rc('ضَرَبَ', 'ضَرَبَ', 'ACCEPT', ('ض', 'ر', 'ب')),
            catalog=(mk('A', 10), mk('B', 11)))
        assert p.stage_state == WaznStageState.DEFERRED


# ══════════════════════════════════════════════════════════════════════════════
# W5-18 : تحقق من checksums الملفات المجمَّدة
# ══════════════════════════════════════════════════════════════════════════════

_FROZEN_CHECKSUMS = {
    'pipeline/p3_candidate/root_profiles.py':            'c20a1bc6998516cc',
    'pipeline/p3_candidate/root_rules.py':               'a8e35225693f553d',
    'pipeline/p3_candidate/root_resolution.py':          'd87d07921d989c26',
    'pipeline/p3_candidate/root_resolution_orchestrator.py': '58ecd174a919cbe8',
    'pipeline/p2_projection/root_projection.py':         '7bca3605867e67ed',
}


@pytest.mark.parametrize("rel_path,expected_prefix", _FROZEN_CHECKSUMS.items())
def test_frozen_file_unchanged(rel_path, expected_prefix):
    full = _ROOT / rel_path
    actual = hashlib.sha256(full.read_bytes()).hexdigest()
    assert actual.startswith(expected_prefix), (
        f"FROZEN FILE MODIFIED: {rel_path}\n"
        f"  expected prefix : {expected_prefix}\n"
        f"  actual checksum : {actual}")


# ══════════════════════════════════════════════════════════════════════════════
# W5-19 : تحقق أن 20 اختبارًا سابقًا في test_wazn_projection.py لا تزال موجودة
# ══════════════════════════════════════════════════════════════════════════════

_PRIOR_W5_NODE_IDS = [
    "TestMonotonicityGate::test_defer_does_not_run_alignment",
    "TestMonotonicityGate::test_block_does_not_run_alignment",
    "TestMonotonicityGate::test_unknown_directive_raises",
    "TestAcceptContract::test_accept_without_root_raises",
    "TestAcceptContract::test_accept_with_alif_radical_raises",
    "TestAcceptContract::test_accept_with_alif_maqsura_radical_raises",
    "TestAcceptContract::test_unsupported_arity_raises",
    "TestSinglePatternAccept::test_darab_accepts_faala",
    "TestSinglePatternAccept::test_hamza_identity_preserved_in_projection",
    "TestSinglePatternAccept::test_shadda_no_false_radical",
    "TestSinglePatternAccept::test_mudaaf_duplication_by_alignment_not_root_mutation",
    "TestMultiplePatternsDefer::test_two_equal_patterns_defer",
    "TestMissingRootSlotBlocks::test_missing_final_radical_blocks",
    "TestExclusions::test_analyzed_host_used_not_full_surface",
    "TestExclusions::test_attached_pronoun_excluded",
    "TestExclusions::test_inflectional_suffix_separated_from_derivational_wazn",
    "TestSerializationAndPreservation::test_projection_json_serializable",
    "TestSerializationAndPreservation::test_evidence_preserved",
    "TestSerializationAndPreservation::test_trace_preserved",
    "TestSerializationAndPreservation::test_residuals_preserved_through_defer",
]


@pytest.mark.parametrize("node_id", _PRIOR_W5_NODE_IDS)
def test_prior_wazn_projection_node_preserved(node_id):
    """يتحقق أن جميع الـ 20 اختبارًا السابقة لا تزال موجودة."""
    prior_file = _ROOT / "tests" / "p4_wazn" / "test_wazn_projection.py"
    src = prior_file.read_text(encoding="utf-8")
    # استخرج اسم الفئة والدالة من node_id
    cls, func = node_id.split("::")
    assert f"class {cls}" in src, f"class {cls!r} removed from test_wazn_projection.py"
    assert f"def {func}" in src, f"def {func!r} removed from test_wazn_projection.py"
