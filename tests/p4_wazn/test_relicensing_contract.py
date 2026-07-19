#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_relicensing_contract.py — W4: RootRelicensing Contract

اختبارات W4-1 إلى W4-19:
  W4-1  : حقل canonical_root (مُعاد تسميته من proposed_root)
  W4-2  : حقل source_hypothesis_id (مُعاد تسميته من source)
  W4-3  : حقل source_resolution_id (جديد)
  W4-4  : to_dict() موجودة وتُعيد dict
  W4-5  : to_dict() تحتوي المفاتيح المطلوبة وآمنة من ناحية JSON
  W4-6  : ACCEPT → canonical_root صحيح (مَحَبَّ → ح ب ب)
  W4-7  : BLOCK → ا في الجذر
  W4-8  : BLOCK → ى في الجذر
  W4-9  : ACCEPT → ء (الهمزة الأصلية) مقبولة
  W4-10 : DEFER → ثقة LOW
  W4-11 : DEFER → proposed_root=None
  W4-12 : DEFER → جذر غير ثلاثي
  W4-13 : evidence/trace/residuals محفوظة عند ACCEPT
  W4-14 : RootRelicensingResult مُجمَّد
  W4-15 : مَسْرُور → canonical_root = ('س','ر','ر')
  W4-16 : يَسْتَطِيع → source_resolution_id = 'IlaalResolution'
  W4-17 : قَالَ (أجوف) → DEFER
  W4-18 : الملفات المجمدة لم تتغير
  W4-19 : لا node IDs مُحذوفة من test_phase4a_contract.py
"""

from __future__ import annotations

import ast
import json
import hashlib
import os
import sys
import importlib

import pytest

from pipeline.p3_candidate.root_relicensing import (
    RootRelicensingResult,
    relicense_root_from_wazn_hypothesis,
)
from pipeline.p4_wazn.hypothesis import WaznHypothesis
from pipeline.p4_wazn.ilaal import IlaalResolution, apply_ilaal_resolution


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات
# ══════════════════════════════════════════════════════════════════════════════

def _mahabb_hyp(
    proposed_root=('ح', 'ب', 'ب'),
    confidence='HIGH',
) -> WaznHypothesis:
    r = proposed_root or ()
    alignment = (
        ('م', 'MIM_ZIYADAH'),
        (r[0], 'FA'),
        (r[1], 'AYN'),
        (r[2], 'LAM'),
    ) if r and len(r) >= 3 else ()
    return WaznHypothesis(
        refined_host='مَحَبَّ',
        proposed_wazn='مَفْعَلَة',
        ziyadah_detected=('MIM_ZIYADAH',),
        proposed_root_after=proposed_root,
        confidence=confidence,
        evidence_ids=('ev:hypothesis:mim_ziyadah_prefix',),
        residual_codes=(),
        radical_alignment=alignment,
        removed_elements=(('م', 'MIM_ZIYADAH'),),
    )


def _masrur_hyp() -> WaznHypothesis:
    """مَسْرُور: مَفْعُول، جذر = ('س','ر','ر')."""
    return WaznHypothesis(
        refined_host='مَسْرُور',
        proposed_wazn='مَفْعُول',
        ziyadah_detected=('MIM_ZIYADAH',),
        proposed_root_after=('س', 'ر', 'ر'),
        confidence='HIGH',
        evidence_ids=('ev:hypothesis:mim_ziyadah_prefix',),
        residual_codes=(),
        # محاذاة مَفْعُول: م=زيادة, س=FA, ر=AYN, و=PATTERN_LONG_VOWEL, ر=LAM
        radical_alignment=(
            ('م', 'MIM_ZIYADAH'),
            ('س', 'FA'),
            ('ر', 'AYN'),
            ('و', 'PATTERN_LONG_VOWEL'),
            ('ر', 'LAM'),
        ),
        removed_elements=(('م', 'MIM_ZIYADAH'),),
    )


def _fala_hyp(host: str, proposed_root_after=None) -> WaznHypothesis:
    """فَعَلَ ماضٍ أجوف — proposed_root=None → DEFER بدون alignment."""
    return WaznHypothesis(
        refined_host=host,
        proposed_wazn='فَعَلَ',
        ziyadah_detected=(),
        proposed_root_after=proposed_root_after,
        confidence='MEDIUM',
        evidence_ids=('ev:hypothesis:fala',),
        residual_codes=('residual:fala:root_extraction_failed',),
    )


def _ista_hyp(host: str = 'يَسْتَطِيعُ') -> WaznHypothesis:
    """يَسْتَفْعِل — يَسْتَطِيعُ، مع radical_alignment لموضع العين."""
    # محاذاة النمط ب: ي=MUDARIA_PREFIX، س=SIN، ت=TA، ط=FA، ي=AYN_LONG_VOWEL، ع=LAM
    return WaznHypothesis(
        refined_host=host,
        proposed_wazn='يَسْتَفْعِل',
        ziyadah_detected=('ALIF_WASL', 'SIN', 'TA'),
        proposed_root_after=None,
        confidence='MEDIUM',
        evidence_ids=('ev:hypothesis:ista_prefix',),
        residual_codes=('residual:ista:root_extraction_failed',),
        radical_alignment=(
            ('ي', 'MUDARIA_PREFIX'),
            ('س', 'SIN'),
            ('ت', 'TA'),
            ('ط', 'FA'),
            ('ي', 'AYN_LONG_VOWEL'),
            ('ع', 'LAM'),
        ),
        removed_elements=(
            ('ي', 'MUDARIA_PREFIX'),
            ('س', 'SIN'),
            ('ت', 'TA'),
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# W4-1: حقل canonical_root
# ══════════════════════════════════════════════════════════════════════════════

class TestCanonicalRootField:
    def test_canonical_root_field_exists(self):
        """RootRelicensingResult يحتوي حقل 'canonical_root' (لا 'proposed_root')."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert hasattr(result, 'canonical_root'), (
            "RootRelicensingResult يفتقد حقل 'canonical_root' — "
            "يجب إعادة تسمية 'proposed_root' إلى 'canonical_root'"
        )

    def test_no_proposed_root_field(self):
        """الحقل القديم 'proposed_root' يجب ألا يبقى."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert not hasattr(result, 'proposed_root'), (
            "RootRelicensingResult لا يزال يحتوي 'proposed_root' — "
            "يجب حذفه بعد إعادة التسمية إلى 'canonical_root'"
        )

    def test_canonical_root_accept_value(self):
        """عند ACCEPT: canonical_root = الجذر المُمرَّر."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert result.directive == 'ACCEPT'
        assert result.canonical_root == ('ح', 'ب', 'ب')

    def test_canonical_root_defer_is_none(self):
        """عند DEFER (proposed=None): canonical_root = None."""
        result = relicense_root_from_wazn_hypothesis(_fala_hyp('قَالَ'))
        assert result.directive == 'DEFER'
        assert result.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# W4-2: حقل source_hypothesis_id
# ══════════════════════════════════════════════════════════════════════════════

class TestSourceHypothesisIdField:
    def test_source_hypothesis_id_exists(self):
        """RootRelicensingResult يحتوي حقل 'source_hypothesis_id'."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert hasattr(result, 'source_hypothesis_id'), (
            "RootRelicensingResult يفتقد 'source_hypothesis_id' — "
            "يجب إعادة تسمية 'source' إلى 'source_hypothesis_id'"
        )

    def test_no_plain_source_field(self):
        """الحقل القديم 'source' يجب ألا يبقى."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert not hasattr(result, 'source'), (
            "RootRelicensingResult لا يزال يحتوي 'source' — يجب حذفه"
        )

    def test_source_hypothesis_id_value(self):
        """source_hypothesis_id = 'WaznHypothesis' دائمًا."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert result.source_hypothesis_id == 'WaznHypothesis'


# ══════════════════════════════════════════════════════════════════════════════
# W4-3: حقل source_resolution_id
# ══════════════════════════════════════════════════════════════════════════════

class TestSourceResolutionIdField:
    def test_source_resolution_id_exists(self):
        """RootRelicensingResult يحتوي حقل 'source_resolution_id'."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert hasattr(result, 'source_resolution_id'), (
            "RootRelicensingResult يفتقد 'source_resolution_id' (حقل جديد)"
        )

    def test_source_resolution_id_none_without_ilaal(self):
        """بدون IlaalResolution: source_resolution_id = None."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert result.source_resolution_id is None

    def test_source_resolution_id_set_with_ilaal(self):
        """مع IlaalResolution: source_resolution_id = 'IlaalResolution'."""
        hyp = _ista_hyp()
        ilaal = apply_ilaal_resolution(hyp)
        assert ilaal.directive == 'ACCEPT', "شرط مسبق: يَسْتَطِيعُ يجب أن يُحل إعلاله"
        # نبني فرضية محدّثة بالجذر المحلول مع نسخ alignment من الأصل
        updated_hyp = WaznHypothesis(
            refined_host=hyp.refined_host,
            proposed_wazn=hyp.proposed_wazn,
            ziyadah_detected=hyp.ziyadah_detected,
            proposed_root_after=tuple(ilaal.proposed_root),
            confidence='HIGH',
            evidence_ids=ilaal.evidence_ids,
            residual_codes=ilaal.residual_codes,
            radical_alignment=hyp.radical_alignment,
            removed_elements=hyp.removed_elements,
        )
        result = relicense_root_from_wazn_hypothesis(updated_hyp, ilaal_resolution=ilaal)
        assert result.source_resolution_id == 'IlaalResolution'


# ══════════════════════════════════════════════════════════════════════════════
# W4-4: to_dict() موجودة
# ══════════════════════════════════════════════════════════════════════════════

class TestToDictExists:
    def test_to_dict_method_exists(self):
        """RootRelicensingResult تحتوي to_dict()."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert callable(getattr(result, 'to_dict', None)), (
            "RootRelicensingResult تفتقد to_dict() method"
        )

    def test_to_dict_returns_dict(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        d = result.to_dict()
        assert isinstance(d, dict)


# ══════════════════════════════════════════════════════════════════════════════
# W4-5: to_dict() مفاتيح مطلوبة + JSON-safe
# ══════════════════════════════════════════════════════════════════════════════

_REQUIRED_DICT_KEYS = {
    'directive',
    'canonical_root',
    'source_hypothesis_id',
    'source_resolution_id',
    'failure_reason',
    'evidence_ids',
    'trace_ids',
    'residual_codes',
}


class TestToDictContract:
    def test_to_dict_has_required_keys(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        d = result.to_dict()
        missing = _REQUIRED_DICT_KEYS - set(d.keys())
        assert not missing, f"to_dict() تفتقد المفاتيح: {missing}"

    def test_to_dict_json_serializable(self):
        """to_dict() لا تحتوي أنواع غير قابلة للتسلسل."""
        for hyp_fn in [_mahabb_hyp, _masrur_hyp]:
            result = relicense_root_from_wazn_hypothesis(hyp_fn())
            d = result.to_dict()
            try:
                json.dumps(d)
            except (TypeError, ValueError) as exc:
                pytest.fail(f"to_dict() ليست JSON-safe: {exc}")

    def test_to_dict_canonical_root_list_or_none(self):
        """canonical_root في to_dict() = list أو None."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        d = result.to_dict()
        assert isinstance(d['canonical_root'], list), (
            f"canonical_root يجب أن يكون list في to_dict()، وجد: {type(d['canonical_root'])}"
        )

    def test_to_dict_defer_canonical_root_none(self):
        """DEFER: to_dict() canonical_root = None."""
        result = relicense_root_from_wazn_hypothesis(_fala_hyp('قَالَ'))
        d = result.to_dict()
        assert d['canonical_root'] is None

    def test_to_dict_evidence_ids_list(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        d = result.to_dict()
        assert isinstance(d['evidence_ids'], list)

    def test_to_dict_directive_matches(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        d = result.to_dict()
        assert d['directive'] == result.directive


# ══════════════════════════════════════════════════════════════════════════════
# W4-6: ACCEPT → canonical_root صحيح
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptCanonicalRoot:
    def test_mahabb_accept_canonical_root(self):
        """مَحَبَّ → ACCEPT + canonical_root = ('ح','ب','ب')."""
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert result.directive == 'ACCEPT'
        assert result.canonical_root == ('ح', 'ب', 'ب')

    def test_masrur_accept_canonical_root(self):
        """مَسْرُور → ACCEPT + canonical_root = ('س','ر','ر')."""
        result = relicense_root_from_wazn_hypothesis(_masrur_hyp())
        assert result.directive == 'ACCEPT'
        assert result.canonical_root == ('س', 'ر', 'ر')

    def test_accept_no_failure_reason(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert result.failure_reason is None


# ══════════════════════════════════════════════════════════════════════════════
# W4-7: BLOCK → ا في الجذر
# ══════════════════════════════════════════════════════════════════════════════

class TestBlockAlifInRoot:
    def test_alif_waw_ayn_block(self):
        """ا في الجذر → BLOCK."""
        hyp = _mahabb_hyp(proposed_root=('ا', 'ل', 'م'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'BLOCK'

    def test_alif_canonical_root_preserved(self):
        """BLOCK: canonical_root يحفظ الجذر المُدخَّل."""
        hyp = _mahabb_hyp(proposed_root=('ا', 'ل', 'م'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.canonical_root == ('ا', 'ل', 'م')


# ══════════════════════════════════════════════════════════════════════════════
# W4-8: BLOCK → ى في الجذر
# ══════════════════════════════════════════════════════════════════════════════

class TestBlockYaaMaqsuraInRoot:
    def test_yaa_maqsura_blocks(self):
        """ى في الجذر → BLOCK."""
        hyp = _mahabb_hyp(proposed_root=('ر', 'ى', 'ع'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'BLOCK'


# ══════════════════════════════════════════════════════════════════════════════
# W4-9: ACCEPT → ء (الهمزة الأصلية) مقبولة
# ══════════════════════════════════════════════════════════════════════════════

class TestHamzaAccepted:
    def test_hamza_base_is_valid_root_letter(self):
        """ء (U+0621) هوية جذرية صالحة → ACCEPT."""
        # _mahabb_hyp يبني alignment تلقائيًا من proposed_root
        hyp = _mahabb_hyp(proposed_root=('ء', 'ل', 'م'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'ACCEPT', (
            f"ء يجب أن تُقبل كهوية جذرية، directive={result.directive!r}, "
            f"failure={result.failure_reason!r}"
        )

    def test_hamza_in_canonical_root(self):
        hyp = _mahabb_hyp(proposed_root=('ء', 'ل', 'م'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.canonical_root == ('ء', 'ل', 'م')


# ══════════════════════════════════════════════════════════════════════════════
# W4-10: DEFER → ثقة LOW
# ══════════════════════════════════════════════════════════════════════════════

class TestLowConfidenceDefers:
    def test_low_confidence_defers(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp(confidence='LOW'))
        assert result.directive == 'DEFER'

    def test_low_confidence_failure_reason(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp(confidence='LOW'))
        assert result.failure_reason is not None
        assert 'low_confidence' in result.failure_reason or 'LOW' in result.failure_reason


# ══════════════════════════════════════════════════════════════════════════════
# W4-11: DEFER → proposed_root=None
# ══════════════════════════════════════════════════════════════════════════════

class TestNoneRootDefers:
    def test_none_root_defers(self):
        result = relicense_root_from_wazn_hypothesis(_fala_hyp('قَالَ'))
        assert result.directive == 'DEFER'

    def test_none_root_canonical_root_is_none(self):
        result = relicense_root_from_wazn_hypothesis(_fala_hyp('قَالَ'))
        assert result.canonical_root is None


# ══════════════════════════════════════════════════════════════════════════════
# W4-12: DEFER → جذر غير ثلاثي
# ══════════════════════════════════════════════════════════════════════════════

class TestNonTrilateralDefers:
    def test_two_letter_root_defers(self):
        hyp = _mahabb_hyp(proposed_root=('ح', 'ب'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'DEFER'

    def test_five_letter_root_defers(self):
        hyp = _mahabb_hyp(proposed_root=('ح', 'ب', 'ب', 'ب', 'ب'))
        result = relicense_root_from_wazn_hypothesis(hyp)
        assert result.directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# W4-13: evidence/trace/residuals محفوظة
# ══════════════════════════════════════════════════════════════════════════════

class TestEvidencePreserved:
    def test_original_evidence_in_accept(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert 'ev:hypothesis:mim_ziyadah_prefix' in result.evidence_ids

    def test_relicensing_trace_in_accept(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert any('p3.11' in t for t in result.trace_ids), (
            f"لا يوجد trace p3.11 في {result.trace_ids}"
        )

    def test_evidence_ids_is_tuple(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert isinstance(result.evidence_ids, tuple)

    def test_trace_ids_is_tuple(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert isinstance(result.trace_ids, tuple)

    def test_residual_codes_is_tuple(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        assert isinstance(result.residual_codes, tuple)


# ══════════════════════════════════════════════════════════════════════════════
# W4-14: RootRelicensingResult مُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestRootRelicensingResultFrozen:
    def test_result_is_frozen(self):
        result = relicense_root_from_wazn_hypothesis(_mahabb_hyp())
        with pytest.raises((AttributeError, TypeError)):
            result.directive = 'DEFER'  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# W4-15: مَسْرُور → canonical_root = ('س','ر','ر')
# ══════════════════════════════════════════════════════════════════════════════

class TestMasrurCanonicalRoot:
    def test_masrur_canonical_root(self):
        result = relicense_root_from_wazn_hypothesis(_masrur_hyp())
        assert result.canonical_root == ('س', 'ر', 'ر'), (
            f"مَسْرُور: canonical_root المتوقع ('س','ر','ر')، وجد {result.canonical_root!r}"
        )

    def test_masrur_directive_accept(self):
        result = relicense_root_from_wazn_hypothesis(_masrur_hyp())
        assert result.directive == 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# W4-16: يَسْتَطِيع → source_resolution_id = 'IlaalResolution'
# ══════════════════════════════════════════════════════════════════════════════

def _ista_updated_hyp():
    """يَسْتَطِيعُ بعد حل الإعلال — alignment منسوخ من الأصل."""
    hyp = _ista_hyp()
    ilaal = apply_ilaal_resolution(hyp)
    assert ilaal.directive == 'ACCEPT', "شرط مسبق"
    return WaznHypothesis(
        refined_host=hyp.refined_host,
        proposed_wazn=hyp.proposed_wazn,
        ziyadah_detected=hyp.ziyadah_detected,
        proposed_root_after=tuple(ilaal.proposed_root),
        confidence='HIGH',
        evidence_ids=ilaal.evidence_ids,
        residual_codes=ilaal.residual_codes,
        radical_alignment=hyp.radical_alignment,
        removed_elements=hyp.removed_elements,
    ), ilaal


class TestYastatiiuSourceResolution:
    def test_yastatiiu_source_resolution_id(self):
        """يَسْتَطِيعُ عبر IlaalResolution → source_resolution_id='IlaalResolution'."""
        updated, ilaal = _ista_updated_hyp()
        result = relicense_root_from_wazn_hypothesis(updated, ilaal_resolution=ilaal)
        assert result.source_resolution_id == 'IlaalResolution'

    def test_yastatiiu_canonical_root(self):
        """يَسْتَطِيعُ → canonical_root = ('ط','و','ع')."""
        updated, ilaal = _ista_updated_hyp()
        result = relicense_root_from_wazn_hypothesis(updated, ilaal_resolution=ilaal)
        assert result.directive == 'ACCEPT'
        assert result.canonical_root == ('ط', 'و', 'ع')


# ══════════════════════════════════════════════════════════════════════════════
# W4-17: قَالَ (أجوف) → DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestHollowCasesDefer:
    def test_qaala_defers(self):
        """قَالَ: proposed_root=None (إعلال معلّق) → DEFER."""
        result = relicense_root_from_wazn_hypothesis(_fala_hyp('قَالَ'))
        assert result.directive == 'DEFER'

    def test_naama_defers(self):
        result = relicense_root_from_wazn_hypothesis(_fala_hyp('نَامَ'))
        assert result.directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# W4-18: الملفات المجمدة لم تتغير
# ══════════════════════════════════════════════════════════════════════════════

_PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

_FROZEN_FILES = {
    'pipeline/p3_candidate/root_profiles.py':
        'c20a1bc6998516cc',
    'pipeline/p3_candidate/root_rules.py':
        'a8e35225693f553d',
    'pipeline/p3_candidate/root_resolution.py':
        'd87d07921d989c26',
    'pipeline/p3_candidate/root_resolution_orchestrator.py':
        '58ecd174a919cbe8',
    'pipeline/p2_projection/root_projection.py':
        '7bca3605867e67ed',
}


class TestFrozenFilesUnchanged:
    @pytest.mark.parametrize('rel_path,expected_prefix', _FROZEN_FILES.items())
    def test_frozen_file_unchanged(self, rel_path, expected_prefix):
        """الملف المجمد لم يتغير منذ بداية HOKOM-WAZN-OWNERSHIP."""
        full_path = os.path.normpath(os.path.join(_PROJECT_ROOT, rel_path))
        with open(full_path, 'rb') as f:
            actual = hashlib.sha256(f.read()).hexdigest()[:16]
        assert actual == expected_prefix, (
            f"تغيّر ملف مجمد: {rel_path}\n"
            f"  المتوقع:  {expected_prefix}\n"
            f"  الفعلي: {actual}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# W4-19: لا node IDs مُحذوفة من test_phase4a_contract.py
# ══════════════════════════════════════════════════════════════════════════════

_PHASE4A_CONTRACT_NODE_IDS = {
    'test_accept_rc_initial_is_accept',
    'test_defer_rc_initial_is_defer',
    'test_block_rc_initial_is_block',
    'test_final_directive_is_string',
    'test_final_directive_valid_value',
    'test_block_final_directive_is_block',
    'test_daraba_final_accept',
    'test_daraba_source_path',
    'test_daraba_wazn_projection_not_none',
    'test_daraba_no_hypothesis',
    'test_daraba_no_promoted_candidate',
    'test_accept_wazn_defer_stays_defer',
    'test_source_path_direct_accept_even_when_wazn_defers',
    'test_block_final_directive',
    'test_block_wazn_projection_none',
    'test_block_final_wazn_none',
    'test_block_source_path',
    'test_defer_no_hypothesis_final_defer',
    'test_defer_no_hypothesis_wazn_none',
    'test_defer_no_hypothesis_source_path',
    'test_defer_no_hypothesis_no_promoted',
    'test_mahabb_relicensed_final_accept',
    'test_relicensing_accept_wazn_defer',
    'test_low_confidence_hypothesis_defers',
    'test_promoted_set_on_relicensing_accept',
    'test_promoted_none_for_direct_accept',
    'test_promoted_none_for_block',
    'test_promoted_none_for_defer_no_hypothesis',
    'test_final_wazn_set_when_accept',
    'test_final_wazn_none_for_block',
    'test_final_wazn_none_for_defer_no_hypothesis',
    'test_final_wazn_none_when_final_defer',
    'test_source_path_and_final_directive_are_independent',
    'test_source_path_field_exists',
    'test_no_source_field',
    'test_frozen_direct_accept',
    'test_frozen_block',
    'test_to_dict_has_required_keys_accept',
    'test_to_dict_has_required_keys_block',
    'test_to_dict_final_directive_matches_field',
    'test_to_dict_evidence_ids_is_list',
    'test_evidence_ids_is_tuple',
    'test_trace_ids_is_tuple',
    'test_residual_codes_is_tuple',
    'test_residual_codes_tuple_for_block',
    'test_ilaal_resolution_field_exists',
    'test_ilaal_resolution_none_for_direct',
    'test_ilaal_resolution_none_for_block',
}


class TestPhase4AContractNodeIdsPreserved:
    def test_no_node_ids_removed_from_phase4a_contract(self):
        """جميع test node IDs من test_phase4a_contract.py لا تزال موجودة."""
        contract_path = os.path.normpath(os.path.join(
            _PROJECT_ROOT, 'tests/p4_wazn/test_phase4a_contract.py'
        ))
        with open(contract_path, encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        found_ids = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
        }
        missing = _PHASE4A_CONTRACT_NODE_IDS - found_ids
        assert not missing, (
            f"node IDs مُحذوفة من test_phase4a_contract.py: {missing}"
        )
