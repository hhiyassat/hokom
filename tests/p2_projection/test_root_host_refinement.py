#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p2_projection/test_root_host_refinement.py — Root Host Refinement (Phase 3.10)

يغطّي النطاق الأول فقط:
  1. تاء التأنيث في الفعل الماضي (تْ / تِ) على المسار الفعلي.
  2. التاء المربوطة النهائية (ة) وتحقيقها المبسوط في الإضافة على المسار الاسمي.
  3. منع الانزلاق: لا تُحذف تاء ساكنة داخلية (بَيْت، وَقْت).
  4. رتابة DEFER/BLOCK: لا رفع، ولا حذف عند BLOCK.
  5. عدم إنتاج canonical_root/wazn، وبقاء زيادة داخلية كتحفّظ.
"""

from __future__ import annotations

from pipeline.p2_projection.root_host_refinement import (
    RootHostRefinement,
    refine_root_host,
    PAST_FEMININE_TA,
    NOMINAL_TA_MARBUTA,
)


def refine(host, morphology_path='verbal_root_path', pre_root_directive='OPEN'):
    return refine_root_host(
        host,
        morphology_path=morphology_path,
        pre_root_directive=pre_root_directive,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1. تاء التأنيث في الفعل الماضي
# ══════════════════════════════════════════════════════════════════════════════

class TestPastFeminineTa:
    def test_taraka_sukun(self):
        r = refine('تَرَكَتْ', 'verbal_root_path', 'OPEN')
        assert r.refined_host == 'تَرَكَ'
        assert PAST_FEMININE_TA in r.removed_suffixes

    def test_rajaa_kasra_iltiqa(self):
        # كسرة التقاء الساكنين
        assert refine('رَجَعَتِ', 'verbal_root_path', 'OPEN').refined_host == 'رَجَعَ'

    def test_faghaara_sukun(self):
        assert refine('فَغَارَتْ', 'verbal_root_path', 'OPEN').refined_host == 'فَغَارَ'

    def test_evidence_id_present(self):
        r = refine('تَرَكَتْ', 'verbal_root_path', 'OPEN')
        assert 'terminal_feminine_ta_after_past_host' in r.evidence_ids

    def test_no_canonical_root_or_wazn(self):
        r = refine('تَرَكَتْ', 'verbal_root_path', 'OPEN')
        # RootHostRefinement لا ينتج canonical_root ولا wazn
        assert not hasattr(r, 'canonical_root')
        assert not hasattr(r, 'wazn')


# ══════════════════════════════════════════════════════════════════════════════
# 2. التاء المربوطة النهائية
# ══════════════════════════════════════════════════════════════════════════════

class TestNominalTaMarbuta:
    def test_shajara(self):
        r = refine('شَجَرَةِ', 'nominal_morphology_path', 'OPEN')
        assert r.refined_host == 'شَجَرَ'
        assert NOMINAL_TA_MARBUTA in r.removed_suffixes

    def test_amma_construct(self):
        # عَمْمَتُ — الصورة المُطبَّعة لـ عَمَّةُ (تحقيق مبسوط في الإضافة)
        assert refine('عَمْمَتُ', 'nominal_morphology_path', 'OPEN').refined_host == 'عَمْمَ'

    def test_shidda_normalized(self):
        # شِدْدَةِ — الصورة المُطبَّعة لـ شِدَّةِ
        assert refine('شِدْدَةِ', 'nominal_morphology_path', 'OPEN').refined_host == 'شِدْدَ'

    def test_ghaaba(self):
        assert refine('غَابَةِ', 'nominal_morphology_path', 'OPEN').refined_host == 'غَابَ'

    def test_mahabba_internal_ziyadah_residual(self):
        # مَحَبْبَةِ — الصورة المُطبَّعة لـ مَحَبَّةِ
        r = refine('مَحَبْبَةِ', 'nominal_morphology_path', 'OPEN')
        assert r.refined_host == 'مَحَبْبَ'
        assert NOMINAL_TA_MARBUTA in r.removed_suffixes
        assert 'defer:root_refinement:internal_ziyadah_not_resolved' in r.residual_codes

    def test_no_spurious_residual(self):
        # شِدْدَ لا يحمل ميم اشتقاق → لا تحفّظ
        assert refine('شِدْدَةِ', 'nominal_morphology_path', 'OPEN').residual_codes == ()


# ══════════════════════════════════════════════════════════════════════════════
# 3. منع الانزلاق — لا حذف
# ══════════════════════════════════════════════════════════════════════════════

class TestNoSlippage:
    def test_bayt_tanwin_preserved(self):
        # بَيْتٌ — التاء مسبوقة بساكن (ي) وتحمل تنوينًا → لا حذف
        assert refine('بَيْتٌ', 'verbal_root_path', 'OPEN').refined_host == 'بَيْتٌ'

    def test_waqt_sakin_before_ta(self):
        # وَقْتِ — ق ساكنة قبل التاء → لا حذف
        assert refine('وَقْتِ', 'nominal_morphology_path', 'OPEN').refined_host == 'وَقْتِ'

    def test_bint_sakin_before_ta(self):
        # بِنْتُ — ن ساكنة قبل التاء → لا حذف
        assert refine('بِنْتُ', 'nominal_morphology_path', 'OPEN').refined_host == 'بِنْتُ'

    def test_bayt_not_verbal_still_safe(self):
        # حتى على المسار الاسمي: بَيْتٌ لا يُمسّ
        assert refine('بَيْتٌ', 'nominal_morphology_path', 'OPEN').refined_host == 'بَيْتٌ'

    def test_no_removal_leaves_no_suffix(self):
        r = refine('وَقْتِ', 'nominal_morphology_path', 'OPEN')
        assert r.removed_suffixes == ()


# ══════════════════════════════════════════════════════════════════════════════
# 4. رتابة DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferMonotonicity:
    def test_defer_stays_defer(self):
        r = refine('عَطْفِ', 'nominal_morphology_path', 'DEFER')
        assert r.directive == 'DEFER'
        assert r.refined_host == 'عَطْفِ'   # لا ة → لا تغيير

    def test_defer_removal_still_works_but_no_upgrade(self):
        # الحذف يعمل تحت DEFER لكن التوجيه لا يُرفع إلى OPEN
        r = refine('شَجَرَةِ', 'nominal_morphology_path', 'DEFER')
        assert r.directive == 'DEFER'
        assert r.refined_host == 'شَجَرَ'


# ══════════════════════════════════════════════════════════════════════════════
# 5. رتابة BLOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestBlockMonotonicity:
    def test_block_no_removal(self):
        r = refine('مِنْ', 'nominal_morphology_path', 'BLOCK')
        assert r.directive == 'BLOCK'
        assert r.refined_host == 'مِنْ'   # لا حذف عند BLOCK

    def test_block_even_with_ta_marbuta(self):
        # حتى لو انتهى بـ ة: BLOCK يمنع الحذف
        r = refine('شَجَرَةِ', 'nominal_morphology_path', 'BLOCK')
        assert r.directive == 'BLOCK'
        assert r.refined_host == 'شَجَرَةِ'
        assert r.removed_suffixes == ()


# ══════════════════════════════════════════════════════════════════════════════
# 6. العقد العام
# ══════════════════════════════════════════════════════════════════════════════

class TestContract:
    def test_returns_dataclass(self):
        r = refine('تَرَكَتْ', 'verbal_root_path', 'OPEN')
        assert isinstance(r, RootHostRefinement)
        assert r.input_host == 'تَرَكَتْ'

    def test_removed_prefixes_always_empty_in_scope(self):
        r = refine('تَرَكَتْ', 'verbal_root_path', 'OPEN')
        assert r.removed_prefixes == ()

    def test_to_dict_serializable(self):
        r = refine('تَرَكَتْ', 'verbal_root_path', 'OPEN')
        d = r.to_dict()
        assert d['refined_host'] == 'تَرَكَ'
        assert d['directive'] == 'OPEN'
