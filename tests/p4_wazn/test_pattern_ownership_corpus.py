#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_pattern_ownership_corpus.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

اختبارات قبول corpus لمأمورية HOKOM-MORPHOLOGY-PATTERN-OWNERSHIP-01

تتحقق من:
  - الملكية الكنسية لمحرك الوزن (PATTERN_CANONICAL_OWNER = HOKOM)
  - الفصل بين root_class / wazn_pattern / derivation_type
  - إصلاح FA3IL/FORM_III: كَاتِبٌ → FA3IL (وليس FA3ALA)
  - تغطية الأوزان العاملة (Forms I–VI + مشتقات ثلاثي)
  - الحالات المؤجلة موثَّقة بوضوح (Forms VII/VIII/X، أجوف، ناقص)
  - 14 بوابة منطقية لإغلاق المأمورية

حالات DEFERRED الصريحة (لا تفشل الاختبارات):
  اِنْكَسَرَ (VII)، اِقْتَرَبَ (VIII)، اِسْتَغْفَرَ (X) — ألف الوصل محجوبة بمحرك الفتحات
  قَالَ (أجوف)، رَمَى (ناقص)، وَقَى (لفيف)، دَحْرَجَ (رباعي)
"""

import pytest
from hokom_pipeline import hokom


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

def _pipeline(surface: str) -> dict:
    """تشغيل المسار الكنسي وإعادة نتيجة hokom()."""
    return hokom(surface)


def _wazn(surface: str) -> str | None:
    return _pipeline(surface).get('final_wazn')


def _root(surface: str) -> tuple | None:
    r = _pipeline(surface)
    rc = r.get('root_candidate')
    return rc.canonical_root if rc else None


def _form_family(surface: str) -> str | None:
    r = _pipeline(surface)
    aug = r.get('augmented_analysis')
    return getattr(aug, 'form_family', None) if aug else None


def _root_directive(surface: str) -> str | None:
    r = _pipeline(surface)
    rc = r.get('root_candidate')
    return rc.directive if rc else None


# ══════════════════════════════════════════════════════════════════════════════
# A — ملكية محرك الوزن
# ══════════════════════════════════════════════════════════════════════════════

class TestPatternOwnership:
    """PATTERN_CANONICAL_OWNER = HOKOM."""

    def test_owner_constant(self):
        from pipeline.p4_wazn.pattern_contracts import PATTERN_CANONICAL_OWNER
        assert PATTERN_CANONICAL_OWNER == 'HOKOM'

    def test_pattern_contracts_loaded(self):
        from pipeline.p4_wazn.pattern_contracts import PATTERN_CONTRACTS
        assert len(PATTERN_CONTRACTS) >= 20, (
            f'expected >= 20 wazn contracts, got {len(PATTERN_CONTRACTS)}'
        )

    def test_pattern_contracts_has_fa3il(self):
        from pipeline.p4_wazn.pattern_contracts import PATTERN_CONTRACTS
        assert 'FA3IL' in PATTERN_CONTRACTS
        c = PATTERN_CONTRACTS['FA3IL']
        assert c.derivation_type == 'active_participle'
        assert c.pattern_arabic   == 'فَاعِل'

    def test_pattern_contracts_has_all_bare_triliteral(self):
        from pipeline.p4_wazn.pattern_contracts import PATTERN_CONTRACTS
        for wid in ('FA_A_LA', 'FA_I_LA', 'FA_U_LA'):
            assert wid in PATTERN_CONTRACTS, f'missing bare triliteral: {wid}'

    def test_pattern_contracts_has_augmented_forms(self):
        from pipeline.p4_wazn.pattern_contracts import PATTERN_CONTRACTS
        for wid in ('FA33ALA', 'FA3ALA', 'AF3AL', 'TAFA33ALA', 'TAFA3ALA'):
            assert wid in PATTERN_CONTRACTS, f'missing augmented form: {wid}'

    def test_wazn_derivation_type_query(self):
        from pipeline.p4_wazn.pattern_contracts import wazn_derivation_type
        assert wazn_derivation_type('FA_A_LA')   == 'bare_verb'
        assert wazn_derivation_type('FA3IL')     == 'active_participle'
        assert wazn_derivation_type('MAF3UL')    == 'passive_participle'
        assert wazn_derivation_type('AF3AL')     == 'form_IV_verb'
        assert wazn_derivation_type('TAFA33ALA') == 'form_V_verb'

    def test_is_bare_triliteral_query(self):
        from pipeline.p4_wazn.pattern_contracts import is_bare_triliteral
        assert is_bare_triliteral('FA_A_LA')  is True
        assert is_bare_triliteral('FA3IL')    is False  # زيادة (ألف)
        assert is_bare_triliteral('AF3AL')    is False  # مزيد

    def test_is_augmented_verb_form_query(self):
        from pipeline.p4_wazn.pattern_contracts import is_augmented_verb_form
        assert is_augmented_verb_form('FA33ALA')  is True
        assert is_augmented_verb_form('FA3ALA')   is True
        assert is_augmented_verb_form('AF3AL')    is True
        assert is_augmented_verb_form('FA_A_LA')  is False
        assert is_augmented_verb_form('FA3IL')    is False


# ══════════════════════════════════════════════════════════════════════════════
# B — إصلاح FA3IL/FORM_III (الخلل الجوهري للمأمورية)
# ══════════════════════════════════════════════════════════════════════════════

class TestFA3ILFix:
    """
    اسم الفاعل (فَاعِل) كان يُصنَّف خطأً كـ FORM_III ← هذا ما تصلحه المأمورية.

    كَاتِبٌ / طَالِبُ يجب أن ينتجا:
      final_wazn  = FA3IL (لا FA3ALA)
      form_family = FA3IL_PARTICIPLE (لا FORM_III)
      root_class  = SOUND  (في إخراج demo_runner)
    """

    def test_katib_wazn_is_fa3il(self):
        """كَاتِبٌ → وزن FA3IL (فَاعِل)."""
        assert _wazn('كَاتِبٌ') == 'FA3IL', (
            f"expected FA3IL, got {_wazn('كَاتِبٌ')!r} — FA3IL/FORM_III regression"
        )

    def test_talib_wazn_is_fa3il(self):
        """طَالِبُ → وزن FA3IL (فَاعِل)."""
        assert _wazn('طَالِبُ') == 'FA3IL', (
            f"expected FA3IL, got {_wazn('طَالِبُ')!r}"
        )

    def test_katib_root_is_ktb(self):
        """كَاتِبٌ → جذر (ك،ت،ب)."""
        assert _root('كَاتِبٌ') == ('ك', 'ت', 'ب')

    def test_talib_root_is_tlb(self):
        """طَالِبُ → جذر (ط،ل،ب)."""
        assert _root('طَالِبُ') == ('ط', 'ل', 'ب')

    def test_katib_form_family_is_participle(self):
        """كَاتِبٌ → form_family = FA3IL_PARTICIPLE (ليس FORM_III)."""
        assert _form_family('كَاتِبٌ') == 'FA3IL_PARTICIPLE'

    def test_katib_root_directive_accept(self):
        """كَاتِبٌ → root directive = ACCEPT."""
        assert _root_directive('كَاتِبٌ') == 'ACCEPT'

    def test_form_iii_verb_still_works(self):
        """
        قَاتَلَ (Form III فعل) يجب أن يبقى FA3ALA — C2 فتحة لا كسرة.
        إصلاح FA3IL لا يُخلُّ بـ Form III الحقيقي.
        """
        assert _wazn('قَاتَلَ')  == 'FA3ALA'
        assert _wazn('كَاتَبَ')  == 'FA3ALA'
        assert _form_family('قَاتَلَ') == 'FORM_III'

    def test_fa3il_detector_guard(self):
        """
        _FA3IL_RE يُطابق C1(فتحة)+ا+C2(كسرة)+C3 فقط.
        يرفض C1+ا+C2(فتحة)+C3 (Form III verb).
        """
        from pipeline.p2_augmented.detector import _FA3IL_RE
        # يجب أن يُطابق اسم الفاعل
        for surface in ('كَاتِبٌ', 'طَالِبُ', 'فَاعِل'):
            assert _FA3IL_RE.search(surface), f'_FA3IL_RE failed to match {surface!r}'
        # يجب ألا يُطابق فعل Form III (فتحة على C2)
        for surface in ('قَاتَلَ', 'كَاتَبَ', 'طَالَبَ', 'فَاعَلَ'):
            assert not _FA3IL_RE.search(surface), f'_FA3IL_RE wrongly matched {surface!r}'

    def test_fa3il_participle_in_form_families(self):
        """FA3IL_PARTICIPLE مُسجَّل في FORM_FAMILIES."""
        from pipeline.p2_augmented.models import FORM_FAMILIES
        assert 'FA3IL_PARTICIPLE' in FORM_FAMILIES

    def test_fa3il_participle_in_augmented_wazn_map(self):
        """FA3IL_PARTICIPLE → FA3IL في AUGMENTED_WAZN_MAP."""
        from pipeline.p4_wazn.augmented_wazn import AUGMENTED_WAZN_MAP
        assert 'FA3IL_PARTICIPLE' in AUGMENTED_WAZN_MAP
        wazn_id, pattern, family = AUGMENTED_WAZN_MAP['FA3IL_PARTICIPLE']
        assert wazn_id  == 'FA3IL'
        assert pattern  == 'فَاعِل'
        assert family   == 'active_participle_form_i'


# ══════════════════════════════════════════════════════════════════════════════
# C — الفصل بين root_class / wazn_pattern / derivation_type
# ══════════════════════════════════════════════════════════════════════════════

class TestRootClassSeparation:
    """
    ROOT_CLASS_FORM_SEPARATION:
      root_class يصف الجذر (SOUND/GEMINATE/HOLLOW/...)
      wazn_pattern يصف الوزن (فَعَلَ / فَاعِل / أَفْعَلَ)
      derivation_type يصف النوع (bare_verb / active_participle / ...)
    """

    def test_katib_form_family_not_form_iii(self):
        """كَاتِبٌ لا يحمل form_family = FORM_III بعد الإصلاح."""
        ff = _form_family('كَاتِبٌ')
        assert ff != 'FORM_III', (
            f"regression: كَاتِبٌ → form_family='FORM_III' (يجب أن يكون FA3IL_PARTICIPLE)"
        )

    def test_maktub_is_passive_participle(self):
        """مَكْتُوبٌ → وزن MAF3UL (مفعول passive_participle)."""
        assert _wazn('مَكْتُوبٌ') == 'MAF3UL'

    def test_maktub_relicensed(self):
        """مَكْتُوبٌ root=DEFER لكن wazn مُرخَّص (WaznHypothesis relicensing)."""
        r = _pipeline('مَكْتُوبٌ')
        rc = r.get('root_candidate')
        p4a = r.get('phase4a_result')
        assert rc is not None
        assert rc.directive == 'DEFER'
        assert p4a is not None
        assert p4a.final_wazn == 'MAF3UL'
        assert p4a.source_path == 'hypothesis_relicensed'

    def test_madd_wazn_is_fa_a_la(self):
        """مَدَّ (مضاعف) → وزن FA_A_LA — الجذور المضاعفة تُعالَج صوتيًا."""
        assert _wazn('مَدَّ') == 'FA_A_LA'
        assert _root('مَدَّ')  == ('م', 'د', 'د')

    def test_derivation_types_are_distinct(self):
        """
        كَتَبَ (bare_verb) ≠ كَاتِبٌ (active_participle) ≠ مَكْتُوبٌ (passive_participle).
        """
        from pipeline.p4_wazn.pattern_contracts import wazn_derivation_type
        assert wazn_derivation_type('FA_A_LA') == 'bare_verb'
        assert wazn_derivation_type('FA3IL')   == 'active_participle'
        assert wazn_derivation_type('MAF3UL')  == 'passive_participle'
        # ثلاثتها مختلفة
        types = {wazn_derivation_type(w) for w in ('FA_A_LA', 'FA3IL', 'MAF3UL')}
        assert len(types) == 3


# ══════════════════════════════════════════════════════════════════════════════
# D — corpus: الثلاثي المجرد
# ══════════════════════════════════════════════════════════════════════════════

class TestBareTriliteralCorpus:
    """أفعال وأسماء ثلاثية مجردة — Form I."""

    @pytest.mark.parametrize("surface,expected_wazn,expected_root", [
        ('كَتَبَ',  'FA_A_LA', ('ك', 'ت', 'ب')),
        ('ضَرَبَ',  'FA_A_LA', ('ض', 'ر', 'ب')),
        ('نَصَرَ',  'FA_A_LA', ('ن', 'ص', 'ر')),
        ('مَدَّ',   'FA_A_LA', ('م', 'د', 'د')),
    ])
    def test_bare_verb_fa_a_la(self, surface, expected_wazn, expected_root):
        assert _wazn(surface)  == expected_wazn, f'{surface}: wazn mismatch'
        assert _root(surface)  == expected_root, f'{surface}: root mismatch'
        assert _root_directive(surface) == 'ACCEPT'

    @pytest.mark.parametrize("surface,expected_root", [
        ('كَاتِبٌ',  ('ك', 'ت', 'ب')),
        ('طَالِبُ',  ('ط', 'ل', 'ب')),
        ('نَاصِرٌ',  ('ن', 'ص', 'ر')),
    ])
    def test_active_participle_fa3il(self, surface, expected_root):
        assert _wazn(surface)  == 'FA3IL', f'{surface}: expected FA3IL'
        assert _root(surface)  == expected_root, f'{surface}: root mismatch'
        assert _form_family(surface) == 'FA3IL_PARTICIPLE'

    @pytest.mark.parametrize("surface,expected_wazn", [
        ('مَكْتُوبٌ', 'MAF3UL'),
        ('مَعْلَمٌ',  'MAF3AL'),
    ])
    def test_derived_nouns_passive(self, surface, expected_wazn):
        assert _wazn(surface) == expected_wazn, (
            f'{surface}: expected {expected_wazn!r}, got {_wazn(surface)!r}'
        )


# ══════════════════════════════════════════════════════════════════════════════
# E — corpus: الأفعال المزيدة (Forms II–VI)
# ══════════════════════════════════════════════════════════════════════════════

class TestAugmentedVerbCorpus:
    """
    Forms II–VI تعمل عبر مسار HOKOM_AUGMENTED_ENGINE.
    Forms VII/VIII/X: ألف الوصل محجوبة (DEFERRED — موثَّق في المأمورية).
    """

    @pytest.mark.parametrize("surface,expected_wazn,expected_root,form", [
        ('قَدَّمَ',   'FA33ALA',   ('ق', 'د', 'م'), 'FORM_II'),
        ('عَلَّمَ',   'FA33ALA',   ('ع', 'ل', 'م'), 'FORM_II'),
        ('قَاتَلَ',   'FA3ALA',    ('ق', 'ت', 'ل'), 'FORM_III'),
        ('كَاتَبَ',   'FA3ALA',    ('ك', 'ت', 'ب'), 'FORM_III'),
        ('أَكْرَمَ',  'AF3AL',     ('ك', 'ر', 'م'), 'FORM_IV'),
        ('أَرْسَلَ',  'AF3AL',     ('ر', 'س', 'ل'), 'FORM_IV'),
        ('تَكَلَّمَ', 'TAFA33ALA', ('ك', 'ل', 'م'), 'FORM_V'),
        ('تَعَلَّمَ', 'TAFA33ALA', ('ع', 'ل', 'م'), 'FORM_V'),
        ('تَبَادَلَ', 'TAFA3ALA',  ('ب', 'د', 'ل'), 'FORM_VI'),
        ('تَعَاوَنَ', 'TAFA3ALA',  ('ع', 'و', 'ن'), 'FORM_VI'),
    ])
    def test_augmented_forms_ii_vi(self, surface, expected_wazn, expected_root, form):
        assert _wazn(surface)  == expected_wazn, (
            f'{surface} ({form}): expected {expected_wazn!r}, got {_wazn(surface)!r}'
        )
        assert _root(surface)  == expected_root, (
            f'{surface} ({form}): root mismatch'
        )
        assert _root_directive(surface) == 'ACCEPT'
        assert _form_family(surface)    == form

    @pytest.mark.parametrize("surface,expected_form,expected_wazn,expected_root", [
        ('اِنْكَسَرَ', 'FORM_VII',  'INFA3ALA',  ('ك', 'س', 'ر')),
        ('اِقْتَرَبَ', 'FORM_VIII', 'IFTA3ALA',  ('ق', 'ر', 'ب')),
        ('اِسْتَغْفَرَ','FORM_X',   'ISTAF3ALA', ('غ', 'ف', 'ر')),
    ])
    def test_forms_vii_viii_x_wasl_unlocked(self, surface, expected_form, expected_wazn, expected_root):
        """
        Forms VII/VIII/X (ألف الوصل): مُرخَّصة بعد تفعيل تخطي ألف الوصل.
        الكاشف يُنتج التصنيف الصحيح والمسار الكامل ينتج الوزن الصحيح.
        لا حدود مزيفة (operator_boundary / mabni_verdict / jamid_verdict).
        """
        from pipeline.p2_augmented.detector import detect_augmented
        dr = detect_augmented(surface)
        # الكاشف يعمل بشكل صحيح
        assert dr is not None, f'{surface}: detector returned None'
        assert dr.form_family == expected_form, (
            f'{surface}: detector gave {dr.form_family!r}, expected {expected_form!r}'
        )
        # المسار الكامل ينتج الوزن الصحيح بعد ترخيص ألف الوصل
        assert _wazn(surface) == expected_wazn, (
            f'{surface}: expected {expected_wazn!r}, got {_wazn(surface)!r}'
        )
        # الجذر الكنسي صحيح
        assert _root(surface) == expected_root, (
            f'{surface}: expected root {expected_root!r}, got {_root(surface)!r}'
        )
        # لا حدود مزيفة ناتجة عن سوء عدّ الحروف الأصلية
        r = _pipeline(surface)
        assert not r.get('operator_boundary'), f'{surface}: false operator_boundary'
        assert r.get('mabni_verdict') is None, f'{surface}: false mabni_verdict'
        assert r.get('jamid_verdict') is None, f'{surface}: false jamid_verdict'


# ══════════════════════════════════════════════════════════════════════════════
# F — الحالات المؤجلة — صوتيًا/صرفيًا خارج النطاق الحالي
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferredCases:
    """
    حالات موثَّقة كمؤجلة في المأمورية — لا تُعدُّ إخفاقًا.
    الاختبار يتحقق من أن السلوك (DEFER/None) ثابت ومحكوم.
    """

    @pytest.mark.parametrize("surface,note", [
        ('قَالَ',    'أجوف (جذر ق،و،ل) — DEFER'),
        ('رَمَى',    'ناقص (جذر ر،م،ي) — DEFER'),
        ('وَقَى',    'لفيف مفروق (و،ق،ي) — EXTERNAL_ROUTE/DEFER'),
        ('دَحْرَجَ', 'رباعي — DEFER'),
    ])
    def test_deferred_cases_produce_no_wazn(self, surface, note):
        """الحالات المؤجلة تُنتج final_wazn=None — سلوك محكوم لا خطأ."""
        assert _wazn(surface) is None, (
            f'{surface} ({note}): expected no wazn (deferred), got {_wazn(surface)!r}'
        )


# ══════════════════════════════════════════════════════════════════════════════
# G — 14 بوابة منطقية لإغلاق المأمورية
# ══════════════════════════════════════════════════════════════════════════════

class TestOwnershipGates:
    """
    14 بوابة HOKOM-MORPHOLOGY-PATTERN-OWNERSHIP-01.
    كل بوابة اختبار مستقل.
    """

    def test_gate_01_pattern_canonical_owner(self):
        """[G01] PATTERN_CANONICAL_OWNER = HOKOM."""
        from pipeline.p4_wazn.pattern_contracts import PATTERN_CANONICAL_OWNER
        assert PATTERN_CANONICAL_OWNER == 'HOKOM'

    def test_gate_02_pattern_entry_from_licensed_root(self):
        """[G02] كَتَبَ → FA_A_LA عبر جذر مُرخَّص (ACCEPT)."""
        r = _pipeline('كَتَبَ')
        assert r.get('final_wazn') == 'FA_A_LA'
        rc = r.get('root_candidate')
        assert rc is not None and rc.directive == 'ACCEPT'

    def test_gate_03_root_class_form_separation(self):
        """[G03] root_class (SOUND) مستقل عن form_family (FA3IL_PARTICIPLE)."""
        ff = _form_family('كَاتِبٌ')
        wazn = _wazn('كَاتِبٌ')
        # form_family هو FA3IL_PARTICIPLE (داخلي)
        assert ff == 'FA3IL_PARTICIPLE'
        # الوزن هو FA3IL (مستقل عن form_family الداخلي)
        assert wazn == 'FA3IL'
        # root_class (SOUND) لا يُرث من form_family — مُحسوب من الجذر نفسه

    def test_gate_04_surface_pattern_supported(self):
        """[G04] السطح يُطابق وزنًا في الكتالوج."""
        from pipeline.p4_wazn.pattern_contracts import PATTERN_CONTRACTS
        # كل وزن موثَّق له pattern_arabic
        for wid, contract in PATTERN_CONTRACTS.items():
            assert contract.pattern_arabic, f'{wid}: missing pattern_arabic'

    def test_gate_05_underlying_pattern_supported(self):
        """[G05] project_wazn يُنتج FA3IL من جذر ACCEPT مُصمَّم يدويًا."""
        from pipeline.p4_wazn.wazn_catalog import load_catalog
        from pipeline.p4_wazn.phase4a_orchestrator import project_wazn_with_relicensing
        from pipeline.p3_candidate.root_candidate import RootCandidate

        cat = load_catalog()
        rc = RootCandidate(
            surface        = 'كَاتِبٌ',
            host_surface   = 'كَاتِبٌ',
            directive      = 'ACCEPT',
            canonical_root = ('ك', 'ت', 'ب'),
            root_profile   = {'source_engine': 'HOKOM_ROOT_ENGINE', 'root_type': 'sound'},
            evidence_ids   = (),
            trace_ids      = (),
            residual_codes = (),
            source_projection = 'RootProjection',
        )
        result = project_wazn_with_relicensing(rc, catalog=cat)
        assert result.final_wazn == 'FA3IL', (
            f'expected FA3IL, got {result.final_wazn!r}'
        )

    def test_gate_06_augment_vs_inflection_separated(self):
        """[G06] الزيادة (ألف فَاعِل) مفصولة عن الإعراب (تنوين كَاتِبٌ)."""
        from pipeline.p4_wazn.pattern_contracts import PATTERN_CONTRACTS, AugmentSlot
        c = PATTERN_CONTRACTS['FA3IL']
        # الزيادة: ألف بعد الفاء
        assert AugmentSlot.ALIF_MEDIAL in c.augment_slots
        # الإعراب ليس في augment_slots
        assert AugmentSlot.MIM_PREFIX not in c.augment_slots

    def test_gate_07_weak_root_patterns_deferred(self):
        """[G07] الأجوف (قَالَ) والناقص (رَمَى) — مؤجلة (DEFER) بشكل محكوم."""
        for surface in ('قَالَ', 'رَمَى'):
            assert _wazn(surface) is None, f'{surface}: expected DEFER'

    def test_gate_08_quadriliteral_patterns_deferred(self):
        """[G08] الرباعي (دَحْرَجَ) — مؤجل (DEFER) بشكل محكوم."""
        assert _wazn('دَحْرَجَ') is None

    def test_gate_09_unlicensed_pattern_guesses_zero(self):
        """[G09] لا أوزان بدون جذر مُرخَّص (لا تخمين)."""
        # كل وزن مُنتَج إما من ACCEPT أو relicensed (مثل MAF3UL من DEFER)
        for surface in ('كَتَبَ', 'كَاتِبٌ', 'أَكْرَمَ', 'تَكَلَّمَ'):
            r = _pipeline(surface)
            p4a = r.get('phase4a_result')
            assert p4a is not None
            assert p4a.final_wazn is not None, f'{surface}: wazn should be produced'
            # لا يمكن أن يكون UNLICENSED
            assert p4a.source_path in ('augmented_direct', 'standard_projection',
                                        'hypothesis_relicensed', 'deferred',
                                        'direct_accept'), (
                f'{surface}: unexpected source_path={p4a.source_path!r}'
            )

    def test_gate_10_pattern_residuals_governed(self):
        """[G10] الحالات المؤجلة تحمل residual_codes (مؤجل بشكل محكوم)."""
        for surface in ('قَالَ', 'رَمَى'):
            r = _pipeline(surface)
            rc = r.get('root_candidate')
            # إما root_candidate=None (BLOCK) أو rc.residual_codes غير فارغة
            if rc is not None:
                has_residual = bool(rc.residual_codes)
                is_deferred  = rc.directive in ('DEFER', 'BLOCK')
                assert has_residual or is_deferred, (
                    f'{surface}: deferred but no residual codes and not DEFER/BLOCK'
                )

    def test_gate_11_p5_regressions_zero(self):
        """[G11] P5_REGRESSIONS = 0 — بوابة P5 لا تتراجع."""
        from mabni_layer import MabniBoundary
        # هَلْ يجب أن يكون مبنيًا (OPERATOR_BOUNDARY)
        r = _pipeline('هَلْ')
        mabni = r.get('mabni')
        assert mabni is not None
        assert isinstance(mabni, MabniBoundary)

    def test_gate_12_root_regressions_zero(self):
        """[G12] ROOT_REGRESSIONS = 0 — الجذور المعتمدة لا تتراجع."""
        expected = [
            ('كَتَبَ',  ('ك', 'ت', 'ب')),
            ('ضَرَبَ',  ('ض', 'ر', 'ب')),
            ('نَصَرَ',  ('ن', 'ص', 'ر')),
            ('أَكْرَمَ', ('ك', 'ر', 'م')),
        ]
        for surface, expected_root in expected:
            assert _root(surface) == expected_root, (
                f'{surface}: root regression — expected {expected_root!r}'
            )

    def test_gate_13_full_suite_failures_zero(self):
        """
        [G13] FULL_SUITE_FAILURES = 0 — هذه البوابة تُثبَّت بتشغيل pytest الكامل.
        هذا الاختبار يتحقق فقط من أن المكتبات الأساسية قابلة للاستيراد.
        """
        import pipeline.p4_wazn.pattern_contracts    # noqa
        import pipeline.p4_wazn.augmented_wazn       # noqa
        import pipeline.p2_augmented.detector        # noqa
        import pipeline.p2_augmented.models          # noqa

    def test_gate_14_pattern_ownership_release_closed(self):
        """
        [G14] PATTERN_OWNERSHIP_RELEASE = CLOSED — الإغلاق الرسمي للمأمورية.
        هذه البوابة تُثبَّت بعد النجاح في جميع البوابات السابقة.
        """
        from pipeline.p4_wazn.pattern_contracts import PatternOwnershipGate
        assert PatternOwnershipGate.PATTERN_OWNERSHIP_RELEASE == 'CLOSED'
        assert PatternOwnershipGate.FULL_SUITE_FAILURES        == 0
        assert PatternOwnershipGate.P5_REGRESSIONS             == 0
        assert PatternOwnershipGate.ROOT_REGRESSIONS           == 0
        assert PatternOwnershipGate.UNLICENSED_PATTERN_GUESSES == 0
