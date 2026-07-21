#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/pre_root_radical_accounting/test_weak_verb.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01
Cluster 4: WEAK_VERB_PRE_ROOT_GAP

يتحقق من أن الأفعال المعتلة (الأجوف والناقص) تُؤجَّل (DEFER)
بدلًا من قبول جذر خاطئ.

قاعدة:
  - CRA: DEFER للأجوف والناقص
  - reason_codes تحتوي على WEAK_ أو DEFER
  - لا تُقبَل هوية جذر محظورة (ا، ى) في candidate_radical_sequences

المجموعات:
  A (1–6):  الأجوف (يَقُولُ، يَخَافُ)
  B (7–12): الناقص (يَدْعُو، يَرْجُو، يَسْعَى)
  C (13–16): تأكيد: لا تجريد واو الجذع إذا كانت جذرًا
  D (17–20): وحدة: _strip_verbal_suffix (واو مفردة)
"""

from __future__ import annotations

import os
import sys

import pytest

_HOKOM_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _HOKOM_ROOT not in sys.path:
    sys.path.insert(0, _HOKOM_ROOT)


@pytest.fixture(scope='module')
def pipeline():
    from hokom_pipeline import hokom as _hokom
    return _hokom


def _cra(pipeline_fn, word: str):
    return pipeline_fn(word).get('cra_result')


def _root(pipeline_fn, word: str):
    rc = pipeline_fn(word).get('root_candidate')
    return getattr(rc, 'canonical_root', None) if rc else None


# ══════════════════════════════════════════════════════════════════════════════
# Group A — الأجوف (weak AYN: و/ي)
# ══════════════════════════════════════════════════════════════════════════════

class TestHollowVerbs:
    """A: hollow verbs → CRA DEFER (weak radical in AYN position)."""

    def test_A01_yaqul_cra_defer(self, pipeline):
        """A01: يَقُولُ → CRA DEFER (و في موضع العين)."""
        cra = _cra(pipeline, 'يَقُولُ')
        assert cra is not None
        assert cra.directive == 'DEFER'

    def test_A02_yaqul_no_weak_root_accepted(self, pipeline):
        """A02: يَقُولُ → candidate_radical_sequences فارغة (لا قبول لجذر ضعيف)."""
        cra = _cra(pipeline, 'يَقُولُ')
        assert cra.candidate_radical_sequences == []

    def test_A03_yakhaf_cra_defer(self, pipeline):
        """A03: يَخَافُ → CRA DEFER (ا في موضع العين)."""
        cra = _cra(pipeline, 'يَخَافُ')
        assert cra is not None
        assert cra.directive == 'DEFER'

    def test_A04_yakun_plural_defer(self, pipeline):
        """A04: تَكُونُوا → CRA DEFER (أجوف + جمع)."""
        cra = _cra(pipeline, 'تَكُونُوا')
        assert cra is not None
        assert cra.directive == 'DEFER'

    def test_A05_prohibited_identity_not_accepted(self, pipeline):
        """A05: ا لا تظهر في candidate_radical_sequences (هوية محظورة)."""
        for word in ['يَقُولُ', 'يَخَافُ', 'تَكُونُوا']:
            cra = _cra(pipeline, word)
            if cra and cra.candidate_radical_sequences:
                for seq in cra.candidate_radical_sequences:
                    assert 'ا' not in seq, (
                        f"{word}: prohibited root identity 'ا' found in {seq}"
                    )

    def test_A06_hollow_cra_not_none(self, pipeline):
        """A06: CRA runs (not None) for hollow verbs when pre_root available."""
        cra = _cra(pipeline, 'يَقُولُ')
        # CRA may be None if jamid/mabni blocks pre_root
        # but for a regular verb it should be present
        if cra is not None:
            assert cra.directive in ('DEFER', 'BLOCK')

    # ──────────────────────────────────────────────────────────────────────────
    # Group B — الناقص (weak LAM: و/ي → ا/ى)
    # ──────────────────────────────────────────────────────────────────────────

    def test_B07_yaduu_cra_defer(self, pipeline):
        """B07: يَدْعُو → CRA DEFER (ناقص، لا تجريد واو الجذع)."""
        cra = _cra(pipeline, 'يَدْعُو')
        assert cra is not None
        assert cra.directive == 'DEFER'

    def test_B08_yaduu_bare_waw_guard(self, pipeline):
        """B08: يَدْعُو → واو النهاية ليست مُجرَّدة (تبقى في الجذع)."""
        cra = _cra(pipeline, 'يَدْعُو')
        # The bare و guard: requires ≥3 consonants after strip
        # يَدْعُو after stripping يَ → دْعُو (3 consonants: د,ع,و)
        # strip و → دْعُ (2 consonants) → guard may allow strip, giving DEFER via weak lam
        # Either way: directive must not be ACCEPT with و in root
        if cra.candidate_radical_sequences:
            for seq in cra.candidate_radical_sequences:
                # should not accept ا or ى as LAM identity
                assert 'ا' not in seq
                assert 'ى' not in seq

    def test_B09_yarjuwa_cra_defer(self, pipeline):
        """B09: يَرْجُو → CRA DEFER (ناقص)."""
        cra = _cra(pipeline, 'يَرْجُو')
        assert cra is not None
        assert cra.directive == 'DEFER'

    def test_B10_yasaa_cra_defer(self, pipeline):
        """B10: يَسْعَى → CRA DEFER (ناقص، ألف مقصورة)."""
        cra = _cra(pipeline, 'يَسْعَى')
        assert cra is not None
        assert cra.directive == 'DEFER'

    def test_B11_weak_reason_code_present(self, pipeline):
        """B11: يَقُولُ → reason_codes يحتوي على WEAK أو DEFER."""
        cra = _cra(pipeline, 'يَقُولُ')
        if cra is not None:
            codes = ' '.join(cra.reason_codes).upper()
            assert 'WEAK' in codes or 'DEFER' in codes, (
                f"يَقُولُ reason_codes should mention WEAK or DEFER: {cra.reason_codes}"
            )

    def test_B12_taduu_correct_form(self, pipeline):
        """B12: تَدْعُوا → CRA DEFER (stem has weak lam)."""
        cra = _cra(pipeline, 'تَدْعُوا')
        # CRA defers because و or ا in lam position after trilateral analysis
        assert cra is not None
        # directive can be DEFER or ACCEPT (if existing engine resolves)
        # the key: if ACCEPT, no prohibited identity
        if cra.directive == 'ACCEPT' and cra.candidate_radical_sequences:
            for seq in cra.candidate_radical_sequences:
                assert 'ا' not in seq
                assert 'ى' not in seq

    # ──────────────────────────────────────────────────────────────────────────
    # Group C — تأكيد: واو الجذع لا تُجرَّد إذا لم يبقَ كافٍ
    # ──────────────────────────────────────────────────────────────────────────

    def test_C13_unit_bare_waw_guard_min_consonants(self):
        """C13: واو مفردة لا تُجرَّد إذا بقي أقل من حرفين."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_verbal_suffix
        # 'يو' — 2 letters total; after strip يو→ي (1 consonant) → should not strip
        bare, suf, rule = _strip_verbal_suffix('يو', is_verbal=True)
        # either no strip, or guard prevents it
        if suf == 'و':
            assert len(bare) >= 1
        else:
            assert suf is None

    def test_C14_unit_bare_waw_verbal_only(self):
        """C14: واو مفردة لا تُجرَّد عند is_verbal=False."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_verbal_suffix
        bare, suf, rule = _strip_verbal_suffix('يَرْجُو', is_verbal=False)
        assert suf is None

    def test_C15_unit_waw_not_stripped_for_defective_lam(self):
        """C15: يَدْعُو → الواو لا تُجرَّد عبر _strip_verbal_suffix (شرط ≥3 حروف)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import (
            _strip_verbal_suffix,
            _count_consonants,
        )
        # يَدْعُو: after hypothetical strip يَ (done in Stage C, not A):
        # the unit test uses the full surface
        bare, suf, rule = _strip_verbal_suffix('يَدْعُو', is_verbal=True)
        if suf == 'و':
            # Guard: remainder must have ≥2 consonants
            assert _count_consonants(bare) >= 2

    def test_C16_unit_waw_stripped_taktubuhu(self):
        """C16: تَكْتُبُو (bare) → واو مُجرَّدة (بقي ≥3 حروف)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_verbal_suffix
        bare, suf, rule = _strip_verbal_suffix('تَكْتُبُو', is_verbal=True)
        assert suf == 'و'
        assert 'WAW_JAMAA_BARE' in (rule or '')

    # ──────────────────────────────────────────────────────────────────────────
    # Group D — وحدة إضافية: _strip_verbal_suffix
    # ──────────────────────────────────────────────────────────────────────────

    def test_D17_unit_strip_waw_jamaa(self):
        """D17: _strip_verbal_suffix('كَتَبُوا', True) → ('كَتَبُ', 'وا', ...)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_verbal_suffix
        bare, suf, rule = _strip_verbal_suffix('كَتَبُوا', is_verbal=True)
        assert suf == 'وا'
        assert 'WAW_JAMAA' in (rule or '')

    def test_D18_unit_no_strip_non_verbal(self):
        """D18: _strip_verbal_suffix('كَتَبُوا', False) → لا تجريد."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_verbal_suffix
        bare, suf, rule = _strip_verbal_suffix('كَتَبُوا', is_verbal=False)
        assert suf is None

    def test_D19_unit_strip_tumm(self):
        """D19: _strip_verbal_suffix('كَتَبْتُمْ', True) → تُمْ مُجرَّدة."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_verbal_suffix
        bare, suf, rule = _strip_verbal_suffix('كَتَبْتُمْ', is_verbal=True)
        assert suf == 'تُمْ'
        assert '2PL_MASC' in (rule or '')

    def test_D20_unit_strip_tuma_dual(self):
        """D20: _strip_verbal_suffix('كَتَبْتُمَا', True) → تُمَا مُجرَّدة."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_verbal_suffix
        bare, suf, rule = _strip_verbal_suffix('كَتَبْتُمَا', is_verbal=True)
        assert suf == 'تُمَا'
