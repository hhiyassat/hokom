#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p3_candidate/test_root_properties.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

اختبارات الخصائص — HOKOM-MORPHOLOGY-ROOT-OWNERSHIP-01

تُثبت هذه الاختبارات الخصائص الإلزامية للمحرك الكنسي:

  P1. الحتمية: نفس المدخل → نفس المخرج دائمًا
  P2. الرتابة: DEFER/BLOCK لا يُرقَّيان داخليًا
  P3. الاكتمال: ACCEPT لا يحمل حقلًا None للجذر
  P4. الاستبعاد: DEFER/BLOCK لا يحملان canonical_root
  P5. المصدر: source_engine ثابت HOKOM_ROOT_ENGINE
  P6. التسلسل: to_dict() دائم ومتكامل
  P7. الترتيب: radical_alignment حتمي وغير فارغ عند ACCEPT
  P8. التطبيع المُضاعَف: normalize_host(normalize_host(x)) = normalize_host(x)
  P9. الأحرف الممنوعة: لا ا/ى كهوية جذرية في ACCEPT
  P10. العقد المُجمَّد: RootResolution لا يقبل التعديل
"""

import pytest
import unicodedata

from pipeline.p3_candidate.root_resolution import resolve_root
from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda
from pipeline.p3_candidate.root_rules import normalize_host


# ══════════════════════════════════════════════════════════════════════════════
# corpus مشترك لاختبارات الخصائص
# ══════════════════════════════════════════════════════════════════════════════

_CORPUS = [
    # صحيح
    ('ضَرَبَ',  'OPEN'),
    ('كَتَبَ',  'OPEN'),
    ('نَصَرَ',  'OPEN'),
    ('فَهِمَ',  'OPEN'),
    # مهموز
    ('قَرَأَ',  'OPEN'),
    ('أَمَرَ',  'OPEN'),
    ('سَأَلَ',  'OPEN'),
    # مضعَّف
    ('مَدَّ',   'OPEN'),
    ('رَدَّ',   'OPEN'),
    # أجوف
    ('قَالَ',  'OPEN'),
    ('بَاعَ',  'OPEN'),
    # ناقص
    ('دَعَا',  'OPEN'),
    ('رَمَى',  'OPEN'),
    # مثال
    ('وَجَدَ', 'OPEN'),
    # لفيف مفروق
    ('وَقَى',  'OPEN'),
    ('وَفَى',  'OPEN'),
    # لفيف مقرون
    ('طَوَى',  'OPEN'),
    ('نَوَى',  'OPEN'),
    # أمر مضغوط
    ('قُلْ',   'OPEN'),
    # BLOCK من pre_root
    ('ضَرَبَ', 'BLOCK'),
    # DEFER من pre_root
    ('كَتَبَ', 'DEFER'),
]


# ══════════════════════════════════════════════════════════════════════════════
# P1 — الحتمية
# ══════════════════════════════════════════════════════════════════════════════

class TestDeterminism:
    """P1: نفس المدخل → نفس المخرج في كل استدعاء."""

    @pytest.mark.parametrize("surface,directive", _CORPUS)
    def test_same_result_twice(self, surface, directive):
        r1 = resolve_root(surface, pre_root_directive=directive)
        r2 = resolve_root(surface, pre_root_directive=directive)
        assert r1 == r2, (
            f"{surface}/{directive}: النتيجة غير حتمية\n  r1={r1}\n  r2={r2}"
        )

    @pytest.mark.parametrize("surface,directive", _CORPUS)
    def test_same_result_third_time(self, surface, directive):
        r1 = resolve_root(surface, pre_root_directive=directive)
        r3 = resolve_root(surface, pre_root_directive=directive)
        assert r1 == r3


# ══════════════════════════════════════════════════════════════════════════════
# P2 — الرتابة (Monotonicity)
# ══════════════════════════════════════════════════════════════════════════════

class TestMonotonicity:
    """P2: BLOCK/DEFER لا يُرقَّيان — pre_root_directive ≥ analysis_directive."""

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'كَتَبَ', 'مَدَّ', 'قَرَأَ',
    ])
    def test_block_never_upgraded(self, surface):
        """pre_root=BLOCK → دائمًا BLOCK في النتيجة."""
        r = resolve_root(surface, pre_root_directive='BLOCK')
        assert r.directive == 'BLOCK', (
            f"{surface}: pre_root=BLOCK لكن directive={r.directive!r}"
        )

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'كَتَبَ', 'مَدَّ', 'قَرَأَ',
    ])
    def test_defer_not_upgraded_to_accept(self, surface):
        """pre_root=DEFER + analyze=ACCEPT → النتيجة DEFER (لا ترقية)."""
        r = resolve_root(surface, pre_root_directive='DEFER')
        assert r.directive == 'DEFER', (
            f"{surface}: pre_root=DEFER لكن directive={r.directive!r} — انتهاك الرتابة"
        )

    @pytest.mark.parametrize("surface", [
        'قَالَ', 'دَعَا', 'وَقَى', 'طَوَى',
    ])
    def test_defer_stays_defer(self, surface):
        """مدخل يُعطي DEFER في OPEN يجب أن يُعطي DEFER في DEFER أيضًا."""
        r_open  = resolve_root(surface, pre_root_directive='OPEN')
        r_defer = resolve_root(surface, pre_root_directive='DEFER')
        assert r_open.directive  == 'DEFER'
        assert r_defer.directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# P3 — اكتمال ACCEPT
# ══════════════════════════════════════════════════════════════════════════════

class TestAcceptCompleteness:
    """P3: عند ACCEPT، canonical_root يجب أن يكون tuple غير None بثلاثة حروف."""

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'كَتَبَ', 'قَرَأَ', 'مَدَّ', 'شَجَرَةٌ',
    ])
    def test_accept_has_root(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        if r.directive == 'ACCEPT':
            assert r.canonical_root is not None, f"{surface}: ACCEPT بلا جذر"
            assert len(r.canonical_root) == 3, (
                f"{surface}: canonical_root={r.canonical_root!r} — يجب 3 حروف"
            )

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'كَتَبَ', 'قَرَأَ',
    ])
    def test_accept_radical_alignment_nonempty(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert len(r.radical_alignment) == 3, (
            f"{surface}: radical_alignment={r.radical_alignment!r} — يجب 3 مواضع"
        )

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'كَتَبَ',
    ])
    def test_accept_alignment_positions(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        positions = {pos for pos, _ in r.radical_alignment}
        assert 'FA'  in positions
        assert 'AYN' in positions
        assert 'LAM' in positions


# ══════════════════════════════════════════════════════════════════════════════
# P4 — استبعاد DEFER/BLOCK
# ══════════════════════════════════════════════════════════════════════════════

class TestDeferBlockExclusion:
    """P4: DEFER/BLOCK لا يحملان canonical_root."""

    @pytest.mark.parametrize("surface,directive", [
        ('قَالَ',  'OPEN'),   # DEFER (hollow)
        ('دَعَا',  'OPEN'),   # DEFER (defective)
        ('وَقَى',  'OPEN'),   # DEFER (lafif)
        ('قُلْ',   'OPEN'),   # DEFER (compressed)
        ('',       'OPEN'),   # BLOCK (insufficient)
        ('ضَرَبَ', 'BLOCK'),  # BLOCK (pre_root)
        ('كَتَبَ', 'DEFER'),  # DEFER (pre_root)
    ])
    def test_defer_block_no_root(self, surface, directive):
        r = resolve_root(surface, pre_root_directive=directive)
        if r.directive in ('DEFER', 'BLOCK'):
            assert r.canonical_root is None, (
                f"{surface}/{directive}: {r.directive} يحمل canonical_root={r.canonical_root!r}"
            )


# ══════════════════════════════════════════════════════════════════════════════
# P5 — ثبات المصدر
# ══════════════════════════════════════════════════════════════════════════════

class TestSourceConstancy:
    """P5: source_engine = 'HOKOM_ROOT_ENGINE' دائمًا."""

    @pytest.mark.parametrize("surface,directive", _CORPUS)
    def test_source_engine_constant(self, surface, directive):
        r = resolve_root(surface, pre_root_directive=directive)
        assert r.source_engine == 'HOKOM_ROOT_ENGINE', (
            f"{surface}: source_engine={r.source_engine!r}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# P6 — التسلسل
# ══════════════════════════════════════════════════════════════════════════════

class TestSerialization:
    """P6: to_dict() حتمي ومتكامل ومتوافق مع JSON."""

    @pytest.mark.parametrize("surface,directive", _CORPUS)
    def test_to_dict_is_json_serializable(self, surface, directive):
        import json
        r = resolve_root(surface, pre_root_directive=directive)
        d = r.to_dict()
        out = json.dumps(d, ensure_ascii=False)
        assert isinstance(out, str)

    @pytest.mark.parametrize("surface,directive", _CORPUS)
    def test_to_dict_deterministic(self, surface, directive):
        """to_dict() مرتين = نفس الناتج."""
        import json
        r = resolve_root(surface, pre_root_directive=directive)
        d1 = json.dumps(r.to_dict(), ensure_ascii=False, sort_keys=True)
        d2 = json.dumps(r.to_dict(), ensure_ascii=False, sort_keys=True)
        assert d1 == d2

    def test_to_dict_roundtrip_canonical_root(self):
        """canonical_root يُسلسَل كـ list ويمكن استعادته."""
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        d = r.to_dict()
        assert isinstance(d['canonical_root'], list)
        assert tuple(d['canonical_root']) == r.canonical_root


# ══════════════════════════════════════════════════════════════════════════════
# P7 — الترتيب الحتمي لـ radical_alignment
# ══════════════════════════════════════════════════════════════════════════════

class TestAlignmentOrdering:
    """P7: ترتيب radical_alignment حتمي ومتسق."""

    def test_alignment_order_fa_ayn_lam(self):
        """يجب أن يكون الترتيب FA → AYN → LAM."""
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert r.radical_alignment[0][0] == 'FA'
        assert r.radical_alignment[1][0] == 'AYN'
        assert r.radical_alignment[2][0] == 'LAM'

    def test_alignment_matches_root(self):
        """حروف radical_alignment يجب أن تطابق canonical_root."""
        r = resolve_root('كَتَبَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        root_from_alignment = tuple(ch for _, ch in r.radical_alignment)
        assert root_from_alignment == r.canonical_root


# ══════════════════════════════════════════════════════════════════════════════
# P8 — التطبيع المُضاعَف (idempotence)
# ══════════════════════════════════════════════════════════════════════════════

class TestNormalizationIdempotence:
    """P8: تطبيع مرتين = تطبيع مرة."""

    @pytest.mark.parametrize("text", [
        'ضَرَبَ', 'قَرَأَ', 'مَدَّ', 'وَقَى', 'طَوَى', 'دَعَا',
    ])
    def test_normalize_host_idempotent(self, text):
        once  = normalize_host(text)
        twice = normalize_host(once)
        assert once == twice, (
            f"{text!r}: normalize_host(normalize_host(x)) ≠ normalize_host(x)\n"
            f"  once={once!r}  twice={twice!r}"
        )

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'قَرَأَ', 'مَدَّ', 'وَقَى',
    ])
    def test_resolve_root_idempotent(self, surface):
        """نتيجة resolve_root على normalized = نفس نتيجة على الأصل."""
        from pipeline.p3_candidate.root_rules import normalize_host as nh
        normalized = nh(surface)
        r1 = resolve_root(surface,    pre_root_directive='OPEN')
        r2 = resolve_root(normalized, pre_root_directive='OPEN')
        assert r1.directive       == r2.directive
        assert r1.canonical_root  == r2.canonical_root
        assert r1.residual_codes  == r2.residual_codes


# ══════════════════════════════════════════════════════════════════════════════
# P9 — الأحرف الممنوعة
# ══════════════════════════════════════════════════════════════════════════════

class TestProhibitedIdentities:
    """P9: لا ا/ى كهوية جذرية في canonical_root عند ACCEPT."""

    _PROHIBITED = frozenset({'ا', 'ى', 'أ', 'إ', 'ؤ', 'ئ', 'آ'})

    @pytest.mark.parametrize("surface", [
        'ضَرَبَ', 'كَتَبَ', 'نَصَرَ', 'قَرَأَ', 'مَدَّ', 'أَمَرَ', 'سَأَلَ',
    ])
    def test_no_prohibited_in_root(self, surface):
        r = resolve_root(surface, pre_root_directive='OPEN')
        if r.directive == 'ACCEPT':
            for ch in r.canonical_root:
                assert ch not in self._PROHIBITED, (
                    f"{surface}: الحرف {ch!r} ممنوع في canonical_root={r.canonical_root!r}"
                )


# ══════════════════════════════════════════════════════════════════════════════
# P10 — العقد المُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

class TestFrozenContract:
    """P10: RootResolution مُجمَّد — لا يقبل التعديل."""

    def test_resolution_is_frozen(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        with pytest.raises((AttributeError, TypeError)):
            r.directive = 'BLOCK'  # type: ignore[misc]

    def test_canonical_root_is_tuple_not_list(self):
        r = resolve_root('ضَرَبَ', pre_root_directive='OPEN')
        assert r.directive == 'ACCEPT'
        assert isinstance(r.canonical_root, tuple), (
            f"canonical_root is {type(r.canonical_root)!r} — يجب أن تكون tuple"
        )
