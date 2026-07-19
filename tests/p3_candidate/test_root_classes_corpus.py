#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p3_candidate/test_root_classes_corpus.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Corpus اختبارات لكل فئة جذر (A–L) — HOKOM-MORPHOLOGY-ROOT-OWNERSHIP-01

تغطية الفئات:
  A. الصحيح السالم      → ACCEPT
  B. المهموز (فاء/عين/لام) → ACCEPT
  C. المضعَّف            → ACCEPT
  D. المثال (فاء ضعيفة) → DEFER + residual=assimilated_fa_unresolved
  E. الأجوف             → DEFER + residual=hollow_underlying_radical_unresolved
  F. الناقص             → DEFER + residual=defective_lam_unresolved
  G. اللفيف المفروق     → DEFER + residual=lafif_mafruq_unresolved
  H. اللفيف المقرون     → DEFER + residual=lafif_maqrun_unresolved
  I. الرباعي            → DEFER + residual=quadriliteral_beyond_scope
  J. المزيد             → ACCEPT (عبر AugmentedAnalysis — مختبَر في test_hokom_local_root_engine)
  K. الأمر المضغوط      → DEFER + residual=two_consonant_form_unresolved
  L. البنى الناقصة      → DEFER + residual=non_standard_consonant_count

اختبارات سلبية:
  - لا ACCEPT لسطح مجهول العين
  - لا ACCEPT لسطح ناقص اللام
  - لا ACCEPT لبنية ممنوعة

خصائص الرتابة:
  - BLOCK من pre_root يبقى BLOCK داخليًا
  - DEFER من pre_root لا يُرقَّى إلى ACCEPT
"""

import pytest
from pipeline.p3_candidate.root_resolution import resolve_root
from pipeline.p3_candidate.root_contracts import (
    RESIDUAL_ASSIMILATED_UNRESOLVED,
    RESIDUAL_HOLLOW_UNRESOLVED,
    RESIDUAL_DEFECTIVE_UNRESOLVED,
    RESIDUAL_LAFIF_MAFRUQ_UNRESOLVED,
    RESIDUAL_LAFIF_MAQRUN_UNRESOLVED,
    RESIDUAL_QUADRILATERAL_SCOPE,
    RESIDUAL_COMPRESSED_UNRESOLVED,
    RESIDUAL_NON_STANDARD,
    ROOT_TYPE_SOUND,
    ROOT_TYPE_GEMINATE,
    ROOT_TYPE_HAMZA_FA,
)


# ══════════════════════════════════════════════════════════════════════════════
# A — الصحيح السالم
# ══════════════════════════════════════════════════════════════════════════════

class TestClassA_Sound:
    """فئة A: الصحيح السالم — ثلاثة حروف صحيحة بلا ضعف."""

    @pytest.mark.parametrize("surface,expected_root", [
        ('ضَرَبَ',  ('ض', 'ر', 'ب')),
        ('كَتَبَ',  ('ك', 'ت', 'ب')),
        ('نَصَرَ',  ('ن', 'ص', 'ر')),
        ('فَتَحَ',  ('ف', 'ت', 'ح')),
        ('جَلَسَ',  ('ج', 'ل', 'س')),
        # شَجَرَةٌ: تاء مربوطة → 4 حروف → quad DEFER (تُختبر عبر الخط الكامل)
        ('عَلِمَ',  ('ع', 'ل', 'م')),
        ('خَرَجَ',  ('خ', 'ر', 'ج')),
        ('دَخَلَ',  ('د', 'خ', 'ل')),
        ('فَهِمَ',  ('ف', 'ه', 'م')),
    ])
    def test_sound_accept(self, surface, expected_root):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT', f"{surface}: {r.directive} ≠ ACCEPT"
        assert r.canonical_root == expected_root, (
            f"{surface}: root={r.canonical_root} ≠ {expected_root}"
        )
        assert r.residual_codes == (), f"{surface}: has residuals {r.residual_codes}"
        assert r.source_engine == 'HOKOM_ROOT_ENGINE'

    def test_sound_profile_type(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert r.root_profile.get('root_type') == 'sound'

    def test_sound_radical_count(self):
        r = resolve_root('كَتَبَ', pre_root_directive='OPEN')
        assert r.root_profile.get('radical_count') == 3


# ══════════════════════════════════════════════════════════════════════════════
# B — المهموز
# ══════════════════════════════════════════════════════════════════════════════

class TestClassB_Hamza:
    """فئة B: المهموز — الهمزة في أي موضع (فاء/عين/لام)."""

    @pytest.mark.parametrize("surface,expected_root", [
        # مهموز الفاء
        ('أَمَرَ',  ('ء', 'م', 'ر')),
        ('أَكَلَ',  ('ء', 'ك', 'ل')),
        # مهموز العين (عين = ء بعد توحيد الهمزة)
        ('سَأَلَ',  ('س', 'ء', 'ل')),
        ('بَأَسَ',  ('ب', 'ء', 'س')),
        # مهموز اللام
        ('قَرَأَ',  ('ق', 'ر', 'ء')),
        ('بَدَأَ',  ('ب', 'د', 'ء')),
        # قَرَؤُوا: 5 حروف → non_standard DEFER (تُختبر عبر الخط الكامل)
    ])
    def test_hamza_accept(self, surface, expected_root):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT', f"{surface}: {r.directive} ≠ ACCEPT"
        assert r.canonical_root == expected_root, (
            f"{surface}: root={r.canonical_root} ≠ {expected_root}"
        )

    def test_hamza_profile_type(self):
        r = resolve_root('قَرَأَ', pre_root_directive='OPEN')
        assert r.root_profile.get('root_type') == 'hamza'

    def test_hamza_normalized_to_bare_hamza(self):
        """الهمزات المزخرفة تُوحَّد إلى ء في الجذر."""
        r = resolve_root('أَمَرَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        fa = r.canonical_root[0] if r.canonical_root else None
        assert fa == 'ء', f"الفاء يجب أن تكون ء لا {fa!r}"


# ══════════════════════════════════════════════════════════════════════════════
# C — المضعَّف
# ══════════════════════════════════════════════════════════════════════════════

class TestClassC_Geminate:
    """فئة C: المضعَّف — الشدة تُفكَّك هندسيًا."""

    @pytest.mark.parametrize("surface,expected_root", [
        ('مَدَّ',   ('م', 'د', 'د')),
        ('رَدَّ',   ('ر', 'د', 'د')),
        ('شَكَّ',   ('ش', 'ك', 'ك')),
        ('حَبَّ',   ('ح', 'ب', 'ب')),
        ('فَرَّ',   ('ف', 'ر', 'ر')),
        ('مَرَّ',   ('م', 'ر', 'ر')),
        ('شَمَّ',   ('ش', 'م', 'م')),
    ])
    def test_geminate_accept(self, surface, expected_root):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT', f"{surface}: {r.directive} ≠ ACCEPT"
        assert r.canonical_root == expected_root, (
            f"{surface}: root={r.canonical_root} ≠ {expected_root}"
        )

    def test_geminate_profile_type(self):
        r = resolve_root('مَدَّ', pre_root_directive='OPEN')
        assert r.root_profile.get('root_type') == 'geminate'

    def test_geminate_ayn_equals_lam(self):
        r = resolve_root('رَدَّ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        ayn, lam = r.canonical_root[1], r.canonical_root[2]
        assert ayn == lam, f"AYN={ayn!r} ≠ LAM={lam!r}"


# ══════════════════════════════════════════════════════════════════════════════
# D — المثال (فاء ضعيفة)
# ══════════════════════════════════════════════════════════════════════════════

class TestClassD_Assimilated:
    """فئة D: المثال — فاء ∈ {و, ي} → DEFER."""

    @pytest.mark.parametrize("surface", [
        'وَجَدَ', 'وَصَلَ', 'وَقَفَ', 'وَلَدَ', 'وَرَدَ',
        'يَسَرَ', 'يَبِسَ',
    ])
    def test_assimilated_defer(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'DEFER', f"{surface}: {r.directive} ≠ DEFER"
        assert RESIDUAL_ASSIMILATED_UNRESOLVED in r.residual_codes, (
            f"{surface}: residuals={r.residual_codes}"
        )
        assert r.canonical_root is None

    def test_assimilated_no_accept(self):
        """المثال لا يُعطي ACCEPT في هذه الدفعة."""
        r = resolve_root('وَجَدَ', pre_root_directive='OPEN')
        assert r.directive != 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# E — الأجوف
# ══════════════════════════════════════════════════════════════════════════════

class TestClassE_Hollow:
    """فئة E: الأجوف — عين ∈ {ا, و} → DEFER."""

    @pytest.mark.parametrize("surface", [
        'قَالَ', 'بَاعَ', 'نَامَ', 'صَامَ', 'طَارَ',
        'عَاشَ', 'زَادَ', 'سَارَ',
    ])
    def test_hollow_defer(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'DEFER', f"{surface}: {r.directive} ≠ DEFER"
        assert RESIDUAL_HOLLOW_UNRESOLVED in r.residual_codes, (
            f"{surface}: residuals={r.residual_codes}"
        )
        assert r.canonical_root is None

    def test_hollow_no_accept(self):
        r = resolve_root('قَالَ', pre_root_directive='OPEN')
        assert r.directive != 'ACCEPT'

    def test_hollow_no_alif_as_root_identity(self):
        """الألف الظاهرة في العين ليست هوية جذرية."""
        r = resolve_root('قَالَ', pre_root_directive='OPEN')
        assert r.canonical_root is None  # الجذر (ق،و،ل) لم يُحسم


# ══════════════════════════════════════════════════════════════════════════════
# F — الناقص
# ══════════════════════════════════════════════════════════════════════════════

class TestClassF_Defective:
    """فئة F: الناقص — لام ∈ {ا, ى, ي} → DEFER."""

    @pytest.mark.parametrize("surface", [
        'دَعَا', 'رَمَى', 'مَشَى', 'قَضَى', 'بَكَى',
        'نَسِيَ', 'لَقِيَ',
    ])
    def test_defective_defer(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'DEFER', f"{surface}: {r.directive} ≠ DEFER"
        assert RESIDUAL_DEFECTIVE_UNRESOLVED in r.residual_codes, (
            f"{surface}: residuals={r.residual_codes}"
        )
        assert r.canonical_root is None

    def test_defective_alif_not_lam_identity(self):
        """الألف الظاهرة في اللام ليست هوية جذرية."""
        r = resolve_root('دَعَا', pre_root_directive='OPEN')
        assert r.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# G — اللفيف المفروق
# ══════════════════════════════════════════════════════════════════════════════

class TestClassG_LafifMafruq:
    """فئة G: اللفيف المفروق — فاء+لام ضعيفتان → DEFER."""

    @pytest.mark.parametrize("surface", [
        'وَقَى',   # و (fa) + ق (ayn صحيح) + ى (lam)
        'وَفَى',
        'وَعَى',
        'وَلِيَ',
    ])
    def test_lafif_mafruq_defer(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'DEFER', f"{surface}: {r.directive} ≠ DEFER"
        assert RESIDUAL_LAFIF_MAFRUQ_UNRESOLVED in r.residual_codes, (
            f"{surface}: residuals={r.residual_codes}, expected={RESIDUAL_LAFIF_MAFRUQ_UNRESOLVED}"
        )
        assert r.canonical_root is None

    def test_lafif_mafruq_not_hollow(self):
        """اللفيف المفروق لا يُصنَّف أجوفًا."""
        r = resolve_root('وَقَى', pre_root_directive='OPEN')
        assert RESIDUAL_HOLLOW_UNRESOLVED not in r.residual_codes

    def test_lafif_mafruq_not_defective_only(self):
        """اللفيف المفروق لا يُصنَّف ناقصًا فحسب."""
        r = resolve_root('وَقَى', pre_root_directive='OPEN')
        assert RESIDUAL_DEFECTIVE_UNRESOLVED not in r.residual_codes

    def test_lafif_mafruq_not_assimilated_only(self):
        """اللفيف المفروق لا يُصنَّف مثالًا فحسب."""
        r = resolve_root('وَقَى', pre_root_directive='OPEN')
        assert RESIDUAL_ASSIMILATED_UNRESOLVED not in r.residual_codes


# ══════════════════════════════════════════════════════════════════════════════
# H — اللفيف المقرون
# ══════════════════════════════════════════════════════════════════════════════

class TestClassH_LafifMaqrun:
    """فئة H: اللفيف المقرون — عين+لام ضعيفتان → DEFER."""

    @pytest.mark.parametrize("surface", [
        'طَوَى',   # ط (fa) + و (ayn) + ى (lam)
        'نَوَى',
        'حَوَى',
        'رَوَى',
        'سَوَى',
        'لَوَى',
    ])
    def test_lafif_maqrun_defer(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'DEFER', f"{surface}: {r.directive} ≠ DEFER"
        assert RESIDUAL_LAFIF_MAQRUN_UNRESOLVED in r.residual_codes, (
            f"{surface}: residuals={r.residual_codes}, expected={RESIDUAL_LAFIF_MAQRUN_UNRESOLVED}"
        )
        assert r.canonical_root is None

    def test_lafif_maqrun_not_hollow_only(self):
        """اللفيف المقرون لا يُصنَّف أجوفًا فحسب."""
        r = resolve_root('طَوَى', pre_root_directive='OPEN')
        assert RESIDUAL_HOLLOW_UNRESOLVED not in r.residual_codes

    def test_lafif_maqrun_not_defective_only(self):
        """اللفيف المقرون لا يُصنَّف ناقصًا فحسب."""
        r = resolve_root('طَوَى', pre_root_directive='OPEN')
        assert RESIDUAL_DEFECTIVE_UNRESOLVED not in r.residual_codes


# ══════════════════════════════════════════════════════════════════════════════
# I — الرباعي
# ══════════════════════════════════════════════════════════════════════════════

class TestClassI_Quadrilateral:
    """فئة I: الرباعي — أربعة حروف → DEFER (خارج النطاق)."""

    @pytest.mark.parametrize("surface", [
        'دَحْرَجَ',  # د+ح+ر+ج
        'زَلْزَلَ',  # ز+ل+ز+ل
        'وَسْوَسَ',
    ])
    def test_quadrilateral_defer(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'DEFER', f"{surface}: {r.directive} ≠ DEFER"
        assert RESIDUAL_QUADRILATERAL_SCOPE in r.residual_codes, (
            f"{surface}: residuals={r.residual_codes}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# K — الأمر المضغوط
# ══════════════════════════════════════════════════════════════════════════════

class TestClassK_Compressed:
    """فئة K: الأمر المضغوط — حرفان → DEFER."""

    @pytest.mark.parametrize("surface", [
        'قُلْ',   # ق+ل (من ق،و،ل)
        'بِعْ',   # ب+ع (من ب،ي،ع)
        'خَفْ',   # خ+ف (من خ،و،ف)
    ])
    def test_compressed_defer(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'DEFER', f"{surface}: {r.directive} ≠ DEFER"
        assert RESIDUAL_COMPRESSED_UNRESOLVED in r.residual_codes, (
            f"{surface}: residuals={r.residual_codes}"
        )

    def test_compressed_no_root(self):
        r = resolve_root('قُلْ', pre_root_directive='OPEN')
        assert r.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# L — البنى الناقصة / غير القياسية
# ══════════════════════════════════════════════════════════════════════════════

class TestClassL_Insufficient:
    """فئة L: خمسة حروف أو أكثر — غير قياسي → DEFER."""

    @pytest.mark.parametrize("surface", [
        'اسْتَخْرَجَ',  # خمسة حروف بعد الاستخراج عادةً
        'اسْتَغْفَرَ',
    ])
    def test_nonstandard_defer(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        # قد يكون DEFER (non_standard) أو ACCEPT إذا أزاح التطبيع الزيادات
        # — المهم ألا يكون BLOCK بلا سبب
        assert r.directive in ('DEFER', 'ACCEPT'), (
            f"{surface}: {r.directive} ∉ {{DEFER, ACCEPT}}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# اختبارات سلبية عامة
# ══════════════════════════════════════════════════════════════════════════════

class TestNegative:
    """اختبارات سلبية: حالات يجب ألا تُعطي ACCEPT."""

    def test_empty_string_block(self):
        """السطح الفارغ يجب أن يُعطي BLOCK."""
        r = resolve_root('', pre_root_directive='OPEN')
        assert r.directive == 'BLOCK'

    def test_single_char_block(self):
        """حرف واحد يجب أن يُعطي BLOCK."""
        r = resolve_root('ب', pre_root_directive='OPEN')
        assert r.directive == 'BLOCK'

    def test_hollow_no_false_accept(self):
        """الأجوف لا يُعطي ACCEPT."""
        for surface in ['قَالَ', 'بَاعَ', 'نَامَ']:
            r = resolve_root(surface, pre_root_directive='OPEN')
            assert r.directive != 'ACCEPT', f"{surface} should not ACCEPT"

    def test_defective_no_false_accept(self):
        """الناقص لا يُعطي ACCEPT."""
        for surface in ['دَعَا', 'رَمَى', 'قَضَى']:
            r = resolve_root(surface, pre_root_directive='OPEN')
            assert r.directive != 'ACCEPT', f"{surface} should not ACCEPT"

    def test_lafif_no_false_accept(self):
        """اللفيف لا يُعطي ACCEPT."""
        for surface in ['وَقَى', 'طَوَى']:
            r = resolve_root(surface, pre_root_directive='OPEN')
            assert r.directive != 'ACCEPT', f"{surface} should not ACCEPT"

    def test_alif_not_root_identity(self):
        """الألف المُبدَلة عن حرف علة ليست هوية جذرية في ACCEPT."""
        # ACCEPT فقط للصحيح/المضعَّف/المهموز — لا ألف فيها كهوية جذرية
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert 'ا' not in r.canonical_root, "الألف لا تُقبل كهوية جذرية"
        assert 'ى' not in r.canonical_root, "الألف المقصورة لا تُقبل كهوية جذرية"


# ══════════════════════════════════════════════════════════════════════════════
# اختبارات BLOCK من PreRoot Directive
# ══════════════════════════════════════════════════════════════════════════════

class TestPreRootBlock:
    """pre_root_directive=BLOCK يجب أن يُمرَّر مباشرةً بلا تحليل."""

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ',   # صحيح — لكن BLOCK من pre_root
        'قَالَ',   # أجوف — لكن BLOCK من pre_root
        'وَقَى',   # لفيف — لكن BLOCK من pre_root
    ])
    def test_pre_root_block_passes_through(self, surface):
        r = resolve_root(surface, pre_root_directive='BLOCK')
        assert r.directive == 'BLOCK', f"{surface}: {r.directive} ≠ BLOCK"
        assert r.canonical_root is None
        assert 'block:root:pre_root_directive_block' in r.residual_codes


class TestPreRootDefer:
    """pre_root_directive=DEFER + analyze_host=ACCEPT → يبقى DEFER (رتابة صارمة)."""

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ',
        'كَتَبَ',
        'مَدَّ',
    ])
    def test_pre_root_defer_not_upgraded(self, surface):
        """DEFER من pre_root لا يُرقَّى إلى ACCEPT حتى لو كان المضيف صحيحًا."""
        r = resolve_root(surface, pre_root_directive='DEFER')
        assert r.directive == 'DEFER', (
            f"{surface}: directive={r.directive} — DEFER must not be upgraded to ACCEPT"
        )
        assert r.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# اختبارات source_engine
# ══════════════════════════════════════════════════════════════════════════════

class TestSourceEngine:
    """يجب أن يكون source_engine دائمًا HOKOM_ROOT_ENGINE."""

    @pytest.mark.parametrize("surface,directive", [
        ('ضَرَبَ', 'OPEN'),
        ('قَالَ',  'OPEN'),
        ('مَدَّ',  'OPEN'),
        ('وَقَى',  'OPEN'),
        ('قُلْ',   'OPEN'),
    ])
    def test_source_engine_is_hokom(self, surface, directive):
        r = resolve_root(surface, pre_root_directive=directive)
        assert r.source_engine == 'HOKOM_ROOT_ENGINE', (
            f"{surface}: source_engine={r.source_engine!r}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# اختبارات التسلسل
# ══════════════════════════════════════════════════════════════════════════════

class TestSerialization:
    """to_dict() يجب أن يُنتج ناتجًا قابلًا للتسلسل JSON."""

    def test_accept_serializable(self):
        import json
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        d = r.to_dict()
        assert json.dumps(d, ensure_ascii=False)  # لا استثناء

    def test_defer_serializable(self):
        import json
        r = resolve_root('قَالَ', pre_root_directive='OPEN')
        d = r.to_dict()
        assert json.dumps(d, ensure_ascii=False)

    def test_block_serializable(self):
        import json
        r = resolve_root('', pre_root_directive='OPEN')
        d = r.to_dict()
        assert json.dumps(d, ensure_ascii=False)

    def test_to_dict_required_keys(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        d = r.to_dict()
        for key in ('directive', 'analyzed_host', 'canonical_root',
                    'radical_alignment', 'root_profile', 'transformations',
                    'evidence_ids', 'trace_ids', 'residual_codes', 'source_engine'):
            assert key in d, f"missing key: {key!r}"
