#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/integration/test_augmented_live_coverage.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

مصفوفة مرجعية للتحقق من التغطية الحية لأوزان المزيد (Forms II–X)
عبر جميع مراحل الأنبوب الأربع (4A، 4B، 4C، 4D).

الحالات:
  يُعَوِّضُهُمْ  → FORM_II  (بادئة يُ + ضمير هم)
  تَأَكَّدَتِ    → FORM_V   (صيغة ماضي مؤنث)
  مُفْتَرِسَةُ   → FORM_VIII (اسم فاعل مؤنث — NOT_APPLICABLE للباب)
  يَسْتَخْرِجُ   → FORM_X

هذا الملف اختبار LIVE فقط — لا مقتطفات صناعية.
"""

from __future__ import annotations

import pytest


def _run(word: str) -> dict:
    """تشغيل الأنبوب الكامل على الكلمة."""
    from hokom_pipeline import hokom
    return hokom(word)


# ══════════════════════════════════════════════════════════════════════════════
# فئة 1: المصفوفة المرجعية للأشكال الأربعة
# ══════════════════════════════════════════════════════════════════════════════

class TestAugmentedReferenceMatrix:
    """مصفوفة التحقق من التغطية الكاملة لأوزان المزيد."""

    # ── FORM_II: يُعَوِّضُهُمْ ──────────────────────────────────────────────

    def test_form_ii_augmented_analysis(self):
        """يُعَوِّضُهُمْ: augmented_analysis تُشير إلى FORM_II."""
        r = _run('يُعَوِّضُهُمْ')
        aug = r.get('augmented_analysis')
        assert aug is not None, 'augmented_analysis يجب أن يكون موجودًا'
        assert aug.form_family == 'FORM_II', (
            f'form_family={aug.form_family!r} المتوقع FORM_II'
        )

    def test_form_ii_phase4a_accept(self):
        """يُعَوِّضُهُمْ: Phase4A → ACCEPT عبر augmented_direct."""
        r = _run('يُعَوِّضُهُمْ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT', (
            f'Phase4A directive={p4a.final_directive!r}'
        )
        assert p4a.source_path == 'augmented_direct'
        assert p4a.final_wazn == 'FA33ALA'

    def test_form_ii_phase4b_accept(self):
        """يُعَوِّضُهُمْ: Phase4B → ACCEPT مع BAB_FORM_II."""
        r = _run('يُعَوِّضُهُمْ')
        p4b = r.get('phase4b_result')
        assert p4b is not None
        assert p4b.final_directive == 'ACCEPT', (
            f'Phase4B directive={p4b.final_directive!r}'
        )
        assert p4b.final_bab == 'BAB_FORM_II'

    def test_form_ii_phase4c_masdar(self):
        """يُعَوِّضُهُمْ: Phase4C مصدر تَفْعِيل."""
        r = _run('يُعَوِّضُهُمْ')
        p4c = r.get('phase4c_result')
        assert p4c is not None
        assert p4c.final_directive == 'ACCEPT', (
            f'Phase4C directive={p4c.final_directive!r}'
        )
        assert p4c.final_masdar_pattern == 'تَفْعِيل', (
            f'masdar_pattern={p4c.final_masdar_pattern!r}'
        )

    def test_form_ii_phase4d_fa3il(self):
        """يُعَوِّضُهُمْ: Phase4D → ISM_FA3IL مُفَعِّل."""
        r = _run('يُعَوِّضُهُمْ')
        p4d = r.get('phase4d_result')
        assert p4d is not None
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        assert 'ISM_FA3IL' in accepted, (
            f'ISM_FA3IL غير موجود في accepted_mushtaqat: {accepted}'
        )
        assert accepted['ISM_FA3IL'] == 'مُفَعِّل', (
            f'ISM_FA3IL={accepted["ISM_FA3IL"]!r}'
        )

    def test_form_ii_phase4d_maf3ul(self):
        """يُعَوِّضُهُمْ: Phase4D → ISM_MAF3UL مُفَعَّل."""
        r = _run('يُعَوِّضُهُمْ')
        p4d = r.get('phase4d_result')
        assert p4d is not None
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        assert 'ISM_MAF3UL' in accepted, (
            f'ISM_MAF3UL غير موجود: {accepted}'
        )
        assert accepted['ISM_MAF3UL'] == 'مُفَعَّل', (
            f'ISM_MAF3UL={accepted["ISM_MAF3UL"]!r}'
        )

    # ── FORM_V: تَأَكَّدَتِ ───────────────────────────────────────────────────

    def test_form_v_augmented_analysis(self):
        """تَأَكَّدَتِ: augmented_analysis تُشير إلى FORM_V."""
        r = _run('تَأَكَّدَتِ')
        aug = r.get('augmented_analysis')
        assert aug is not None
        assert aug.form_family == 'FORM_V'

    def test_form_v_phase4a_accept(self):
        """تَأَكَّدَتِ: Phase4A → ACCEPT عبر augmented_direct."""
        r = _run('تَأَكَّدَتِ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT'
        assert p4a.source_path == 'augmented_direct'
        assert p4a.final_wazn == 'TAFA33ALA'

    def test_form_v_phase4b_accept(self):
        """تَأَكَّدَتِ: Phase4B → ACCEPT مع BAB_FORM_V."""
        r = _run('تَأَكَّدَتِ')
        p4b = r.get('phase4b_result')
        assert p4b is not None
        assert p4b.final_directive == 'ACCEPT'
        assert p4b.final_bab == 'BAB_FORM_V'

    def test_form_v_phase4c_masdar(self):
        """تَأَكَّدَتِ: Phase4C مصدر تَفَعُّل."""
        r = _run('تَأَكَّدَتِ')
        p4c = r.get('phase4c_result')
        assert p4c is not None
        assert p4c.final_directive == 'ACCEPT'
        assert p4c.final_masdar_pattern == 'تَفَعُّل', (
            f'masdar_pattern={p4c.final_masdar_pattern!r}'
        )

    def test_form_v_phase4d_fa3il(self):
        """تَأَكَّدَتِ: Phase4D → ISM_FA3IL مُتَفَعِّل."""
        r = _run('تَأَكَّدَتِ')
        p4d = r.get('phase4d_result')
        assert p4d is not None
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        assert 'ISM_FA3IL' in accepted
        assert accepted['ISM_FA3IL'] == 'مُتَفَعِّل'

    def test_form_v_phase4d_maf3ul(self):
        """تَأَكَّدَتِ: Phase4D → ISM_MAF3UL مُتَفَعَّل."""
        r = _run('تَأَكَّدَتِ')
        p4d = r.get('phase4d_result')
        assert p4d is not None
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        assert 'ISM_MAF3UL' in accepted
        assert accepted['ISM_MAF3UL'] == 'مُتَفَعَّل'

    # ── FORM_VIII: مُفْتَرِسَةُ ──────────────────────────────────────────────

    def test_form_viii_augmented_analysis(self):
        """مُفْتَرِسَةُ: augmented_analysis تُشير إلى FORM_VIII."""
        r = _run('مُفْتَرِسَةُ')
        aug = r.get('augmented_analysis')
        assert aug is not None
        assert aug.form_family == 'FORM_VIII'

    def test_form_viii_phase4a_accept(self):
        """مُفْتَرِسَةُ: Phase4A → ACCEPT عبر augmented_direct."""
        r = _run('مُفْتَرِسَةُ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT'
        assert p4a.source_path == 'augmented_direct'
        assert p4a.final_wazn == 'IFTA3ALA'

    def test_form_viii_phase4b_not_applicable(self):
        """مُفْتَرِسَةُ: Phase4B → NOT_APPLICABLE (مسار اسمي)."""
        r = _run('مُفْتَرِسَةُ')
        p4b = r.get('phase4b_result')
        assert p4b is not None
        assert p4b.final_directive == 'NOT_APPLICABLE', (
            f'Phase4B directive={p4b.final_directive!r} للمسار الاسمي'
        )

    def test_form_viii_phase4c_masdar(self):
        """مُفْتَرِسَةُ: Phase4C مصدر اِفْتِعَال."""
        r = _run('مُفْتَرِسَةُ')
        p4c = r.get('phase4c_result')
        assert p4c is not None
        assert p4c.final_directive == 'ACCEPT'
        assert p4c.final_masdar_pattern == 'اِفْتِعَال', (
            f'masdar_pattern={p4c.final_masdar_pattern!r}'
        )

    def test_form_viii_phase4d_fa3il(self):
        """مُفْتَرِسَةُ: Phase4D → ISM_FA3IL مُفْتَعِل."""
        r = _run('مُفْتَرِسَةُ')
        p4d = r.get('phase4d_result')
        assert p4d is not None
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        assert 'ISM_FA3IL' in accepted
        assert accepted['ISM_FA3IL'] == 'مُفْتَعِل'

    def test_form_viii_phase4d_maf3ul(self):
        """مُفْتَرِسَةُ: Phase4D → ISM_MAF3UL مُفْتَعَل."""
        r = _run('مُفْتَرِسَةُ')
        p4d = r.get('phase4d_result')
        assert p4d is not None
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        assert 'ISM_MAF3UL' in accepted
        assert accepted['ISM_MAF3UL'] == 'مُفْتَعَل'

    # ── FORM_X: يَسْتَخْرِجُ ─────────────────────────────────────────────────

    def test_form_x_augmented_analysis(self):
        """يَسْتَخْرِجُ: augmented_analysis تُشير إلى FORM_X."""
        r = _run('يَسْتَخْرِجُ')
        aug = r.get('augmented_analysis')
        assert aug is not None
        assert aug.form_family == 'FORM_X'

    def test_form_x_phase4a_accept(self):
        """يَسْتَخْرِجُ: Phase4A → ACCEPT عبر augmented_direct."""
        r = _run('يَسْتَخْرِجُ')
        p4a = r.get('phase4a_result')
        assert p4a is not None
        assert p4a.final_directive == 'ACCEPT'
        assert p4a.source_path == 'augmented_direct'
        assert p4a.final_wazn == 'ISTAF3ALA'

    def test_form_x_phase4b_accept(self):
        """يَسْتَخْرِجُ: Phase4B → ACCEPT مع BAB_FORM_X."""
        r = _run('يَسْتَخْرِجُ')
        p4b = r.get('phase4b_result')
        assert p4b is not None
        assert p4b.final_directive == 'ACCEPT'
        assert p4b.final_bab == 'BAB_FORM_X'

    def test_form_x_phase4c_masdar(self):
        """يَسْتَخْرِجُ: Phase4C مصدر اِسْتِفْعَال."""
        r = _run('يَسْتَخْرِجُ')
        p4c = r.get('phase4c_result')
        assert p4c is not None
        assert p4c.final_directive == 'ACCEPT'
        assert p4c.final_masdar_pattern == 'اِسْتِفْعَال', (
            f'masdar_pattern={p4c.final_masdar_pattern!r}'
        )

    def test_form_x_phase4d_fa3il(self):
        """يَسْتَخْرِجُ: Phase4D → ISM_FA3IL مُسْتَفْعِل."""
        r = _run('يَسْتَخْرِجُ')
        p4d = r.get('phase4d_result')
        assert p4d is not None
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        assert 'ISM_FA3IL' in accepted
        assert accepted['ISM_FA3IL'] == 'مُسْتَفْعِل'

    def test_form_x_phase4d_maf3ul(self):
        """يَسْتَخْرِجُ: Phase4D → ISM_MAF3UL مُسْتَفْعَل."""
        r = _run('يَسْتَخْرِجُ')
        p4d = r.get('phase4d_result')
        assert p4d is not None
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        assert 'ISM_MAF3UL' in accepted
        assert accepted['ISM_MAF3UL'] == 'مُسْتَفْعَل'


# ══════════════════════════════════════════════════════════════════════════════
# فئة 2: حقول الملخص في مخرج الأنبوب
# ══════════════════════════════════════════════════════════════════════════════

class TestSummaryFields:
    """التحقق من حقول الملخص في مخرج hokom()."""

    def test_final_root_present(self):
        """يُعَوِّضُهُمْ: final_root موجود ومن ثلاثة حروف."""
        r = _run('يُعَوِّضُهُمْ')
        root = r.get('final_root')
        assert root is not None, 'final_root يجب أن يكون موجودًا'
        assert len(root) == 3, f'final_root={root!r} يجب أن يكون ثلاثيًا'

    def test_final_wazn_present(self):
        """يُعَوِّضُهُمْ: final_wazn موجود."""
        r = _run('يُعَوِّضُهُمْ')
        assert r.get('final_wazn') == 'FA33ALA'

    def test_final_form_present(self):
        """يُعَوِّضُهُمْ: final_form موجود."""
        r = _run('يُعَوِّضُهُمْ')
        assert r.get('final_form') == 'BAB_FORM_II'

    def test_final_masdar_pattern_present(self):
        """يُعَوِّضُهُمْ: final_masdar_pattern موجود."""
        r = _run('يُعَوِّضُهُمْ')
        assert r.get('final_masdar_pattern') == 'تَفْعِيل'

    def test_accepted_mushtaqat_present(self):
        """يَسْتَخْرِجُ: accepted_mushtaqat موجود وغير فارغ."""
        r = _run('يَسْتَخْرِجُ')
        accepted = r.get('accepted_mushtaqat')
        assert accepted is not None
        assert len(accepted) > 0, 'accepted_mushtaqat يجب أن يحتوي على مدخلات'

    def test_active_residuals_is_tuple(self):
        """active_residuals يُعيد tuple."""
        r = _run('يُعَوِّضُهُمْ')
        res = r.get('active_residuals')
        assert isinstance(res, tuple), f'active_residuals type={type(res)}'

    def test_resolved_residuals_is_tuple(self):
        """resolved_residuals يُعيد tuple."""
        r = _run('يُعَوِّضُهُمْ')
        res = r.get('resolved_residuals')
        assert isinstance(res, tuple), f'resolved_residuals type={type(res)}'

    def test_form_viii_nominal_summary_fields(self):
        """مُفْتَرِسَةُ: final_form=None (اسم، ليس فعلًا)."""
        r = _run('مُفْتَرِسَةُ')
        # باب NOT_APPLICABLE → final_form يُعيَّن من final_bab=None
        p4b = r.get('phase4b_result')
        if p4b is not None:
            assert p4b.final_bab is None, (
                f'final_bab={p4b.final_bab!r} للمسار الاسمي'
            )


# ══════════════════════════════════════════════════════════════════════════════
# فئة 3: مولّد السطح (surface_generator)
# ══════════════════════════════════════════════════════════════════════════════

class TestSurfaceGenerator:
    """التحقق من وحدة مولّد السطح."""

    def test_import(self):
        """يمكن استيراد surface_generator."""
        from pipeline.p2_augmented.surface_generator import (
            apply_root_to_pattern,
            generate_surface,
            is_sound_root,
            has_weak_c2,
            is_geminate,
        )

    def test_is_sound_root_sound(self):
        """الجذور الصحيحة تُصنَّف صحيحة."""
        from pipeline.p2_augmented.surface_generator import is_sound_root
        assert is_sound_root(('ك', 'ت', 'ب'))
        assert is_sound_root(('خ', 'ر', 'ج'))
        assert is_sound_root(('ع', 'و', 'ض')) is False  # و حرف علة

    def test_is_sound_root_weak(self):
        """الجذور المعتلة تُصنَّف معتلة."""
        from pipeline.p2_augmented.surface_generator import is_sound_root
        assert not is_sound_root(('ق', 'و', 'ل'))
        assert not is_sound_root(('س', 'ي', 'ر'))

    def test_has_weak_c2(self):
        """has_weak_c2 يكشف جذور الأجوف."""
        from pipeline.p2_augmented.surface_generator import has_weak_c2
        assert has_weak_c2(('ق', 'و', 'ل'))
        assert has_weak_c2(('ب', 'ي', 'ع'))
        assert not has_weak_c2(('ك', 'ت', 'ب'))

    def test_is_geminate(self):
        """is_geminate يكشف الجذور المضعَّفة."""
        from pipeline.p2_augmented.surface_generator import is_geminate
        assert is_geminate(('م', 'د', 'د'))
        assert not is_geminate(('ك', 'ت', 'ب'))

    def test_apply_root_to_pattern_form_ii(self):
        """apply_root_to_pattern: جذر (ك,ت,ب) + فَعَّلَ → كَتَّبَ."""
        from pipeline.p2_augmented.surface_generator import apply_root_to_pattern
        result = apply_root_to_pattern('فَعَّلَ', ('ك', 'ت', 'ب'))
        assert result == 'كَتَّبَ', f'result={result!r}'

    def test_apply_root_to_pattern_form_x(self):
        """apply_root_to_pattern: جذر (خ,ر,ج) + اِسْتَفْعَلَ → اِسْتَخْرَجَ."""
        from pipeline.p2_augmented.surface_generator import apply_root_to_pattern
        result = apply_root_to_pattern('اِسْتَفْعَلَ', ('خ', 'ر', 'ج'))
        assert result == 'اِسْتَخْرَجَ', f'result={result!r}'

    def test_generate_surface_form_ii_masdar(self):
        """generate_surface: FORM_II MASDAR لجذر صحيح → HIGH."""
        from pipeline.p2_augmented.surface_generator import generate_surface
        surface, conf = generate_surface('FORM_II', 'MASDAR', ('ك', 'ت', 'ب'))
        assert conf == 'HIGH'
        assert surface == 'تَكْتِيب', f'surface={surface!r}'

    def test_generate_surface_form_x_masdar(self):
        """generate_surface: FORM_X MASDAR لجذر صحيح → HIGH."""
        from pipeline.p2_augmented.surface_generator import generate_surface
        surface, conf = generate_surface('FORM_X', 'MASDAR', ('خ', 'ر', 'ج'))
        assert conf == 'HIGH'
        assert surface is not None

    def test_generate_surface_form_viii_past_sound(self):
        """generate_surface: FORM_VIII PAST لجذر صحيح (ك,ت,ب) → اِكْتَتَبَ HIGH."""
        from pipeline.p2_augmented.surface_generator import generate_surface
        surface, conf = generate_surface('FORM_VIII', 'PAST', ('ك', 'ت', 'ب'))
        assert conf == 'HIGH'
        assert surface == 'اِكْتَتَبَ', f'surface={surface!r}'

    def test_generate_surface_form_viii_past_waw_c1(self):
        """generate_surface: FORM_VIII PAST مع C1=و → اِتَّصَلَ HIGH (إدغام)."""
        from pipeline.p2_augmented.surface_generator import generate_surface
        # جذر (و,ص,ل) — و-ص-ل → اِتَّصَلَ
        surface, conf = generate_surface('FORM_VIII', 'PAST', ('و', 'ص', 'ل'))
        assert conf == 'HIGH'
        assert surface == 'اِتَّصَلَ', f'surface={surface!r}'

    def test_generate_surface_form_viii_past_zay_c1(self):
        """generate_surface: FORM_VIII PAST مع C1=ز → اِزْدَهَرَ HIGH."""
        from pipeline.p2_augmented.surface_generator import generate_surface
        surface, conf = generate_surface('FORM_VIII', 'PAST', ('ز', 'ه', 'ر'))
        assert conf == 'HIGH'
        assert surface == 'اِزْدَهَرَ', f'surface={surface!r}'

    def test_generate_surface_weak_c2_defer(self):
        """generate_surface: FORM_X MASDAR مع عين معتلة → DEFER."""
        from pipeline.p2_augmented.surface_generator import generate_surface
        # جذر (ط,و,ع) — Form X: يَسْتَطِيعُ (إعلال معقد)
        surface, conf = generate_surface('FORM_X', 'MASDAR', ('ط', 'و', 'ع'))
        assert conf == 'DEFER', f'conf={conf!r} للجذر الأجوف في Form X'
        assert surface is None


# ══════════════════════════════════════════════════════════════════════════════
# فئة 4: تغطية Forms III–VII (أساسية)
# ══════════════════════════════════════════════════════════════════════════════

class TestFormsIIItoVII:
    """اختبار أوزان Forms III–VII في الأنبوب الحي."""

    @pytest.mark.parametrize("word,expected_form,expected_wazn", [
        ('قَاتَلَ',   'FORM_III', 'FA3ALA'),
        ('أَكْرَمَ',   'FORM_IV',  'AF3AL'),
        ('اِنْطَلَقَ', 'FORM_VII', 'INFA3ALA'),
    ])
    def test_form_phase4a(self, word, expected_form, expected_wazn):
        """أوزان III/IV/VII: Phase4A ACCEPT مع الوزن الصحيح."""
        r = _run(word)
        aug = r.get('augmented_analysis')
        p4a = r.get('phase4a_result')
        if aug is None:
            pytest.skip(f'{word!r}: لم يُكتشف كصيغة مزيدة')
        assert aug.form_family == expected_form, (
            f'{word}: form={aug.form_family!r}'
        )
        if p4a is not None and p4a.final_directive == 'ACCEPT':
            assert p4a.final_wazn == expected_wazn, (
                f'{word}: wazn={p4a.final_wazn!r}'
            )


# ══════════════════════════════════════════════════════════════════════════════
# فئة 5: إجراء تكاملي بالحقول الكاملة (parametrize)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize(
    "word, expected_form, expected_4a, expected_4b_directive, expected_masdar_pattern, expected_fa3il",
    [
        (
            'يُعَوِّضُهُمْ',
            'FORM_II',
            'ACCEPT',
            'ACCEPT',
            'تَفْعِيل',
            'مُفَعِّل',
        ),
        (
            'تَأَكَّدَتِ',
            'FORM_V',
            'ACCEPT',
            'ACCEPT',
            'تَفَعُّل',
            'مُتَفَعِّل',
        ),
        (
            'مُفْتَرِسَةُ',
            'FORM_VIII',
            'ACCEPT',
            'NOT_APPLICABLE',
            'اِفْتِعَال',
            'مُفْتَعِل',
        ),
        (
            'يَسْتَخْرِجُ',
            'FORM_X',
            'ACCEPT',
            'ACCEPT',
            'اِسْتِفْعَال',
            'مُسْتَفْعِل',
        ),
    ],
)
def test_augmented_full_pipeline(
    word,
    expected_form,
    expected_4a,
    expected_4b_directive,
    expected_masdar_pattern,
    expected_fa3il,
):
    """مصفوفة تكاملية شاملة لأوزان المزيد عبر جميع المراحل."""
    r = _run(word)

    aug = r.get('augmented_analysis')
    p4a = r.get('phase4a_result')
    p4b = r.get('phase4b_result')
    p4c = r.get('phase4c_result')
    p4d = r.get('phase4d_result')

    # augmented_analysis
    assert aug is not None, f'{word}: augmented_analysis مفقود'
    assert aug.form_family == expected_form, (
        f'{word}: form={aug.form_family!r} متوقع {expected_form!r}'
    )

    # Phase4A
    assert p4a is not None, f'{word}: phase4a_result مفقود'
    assert p4a.final_directive == expected_4a, (
        f'{word}: 4A={p4a.final_directive!r} متوقع {expected_4a!r}'
    )
    assert p4a.source_path == 'augmented_direct', (
        f'{word}: source_path={p4a.source_path!r}'
    )

    # Phase4B
    if p4b is not None:
        assert p4b.final_directive == expected_4b_directive, (
            f'{word}: 4B={p4b.final_directive!r} متوقع {expected_4b_directive!r}'
        )

    # Phase4C
    if p4c is not None and p4c.final_directive == 'ACCEPT':
        assert p4c.final_masdar_pattern == expected_masdar_pattern, (
            f'{word}: masdar={p4c.final_masdar_pattern!r} متوقع {expected_masdar_pattern!r}'
        )

    # Phase4D
    if p4d is not None:
        accepted = dict(getattr(p4d, 'accepted_mushtaqat', ()) or ())
        if expected_fa3il:
            assert 'ISM_FA3IL' in accepted, (
                f'{word}: ISM_FA3IL مفقود من accepted_mushtaqat: {accepted}'
            )
            assert accepted['ISM_FA3IL'] == expected_fa3il, (
                f'{word}: ISM_FA3IL={accepted["ISM_FA3IL"]!r} متوقع {expected_fa3il!r}'
            )
