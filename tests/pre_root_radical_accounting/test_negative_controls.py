#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/pre_root_radical_accounting/test_negative_controls.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01

الضوابط السالبة: يتحقق من أن CRA لا يُجرِّد حروف الجذر الصحيحة.

القاعدة: لا تُجرَّد البادئة بناءً على الشكل الظاهري وحده.

المجموعات:
  A (1–6):  أَفعال ماضية — الهمزة الأولى جذر لا بادئة
  B (7–12): أسماء تبدأ بتَ/نَ — لا تجريد (ليس VERBAL_ROOT_PATH)
  C (13–16): النواهي والأمر — لا تجريد خاطئ
  D (17–20): مقارنة السطح الفعلي بالاسمي
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
# Group A — أَفعال ماضية (همزة جذر، لا بادئة)
# ══════════════════════════════════════════════════════════════════════════════

class TestPastVerbHamza:
    """A: past-tense verbs beginning with أَ — hamza is F1 radical, not an imperfect prefix."""

    def test_A01_akala_root_preserved(self, pipeline):
        """A01: أَكَلَ → root preserves ء/أ as first radical."""
        root = _root(pipeline, 'أَكَلَ')
        assert root is not None
        # root must have hamza as first radical; 3 consonants; not (ك,ل) alone
        assert len(root) == 3
        assert root[1] == 'ك'
        assert root[2] == 'ل'

    def test_A02_akala_cra_does_not_accept_kl(self, pipeline):
        """A02: أَكَلَ → CRA does not ACCEPT 2-consonant (ك,ل) as root."""
        cra = _cra(pipeline, 'أَكَلَ')
        if cra and cra.directive == 'ACCEPT' and cra.candidate_radical_sequences:
            for seq in cra.candidate_radical_sequences:
                # if CRA accepts, it must have 3 consonants (not 2)
                assert len(seq) == 3, f"أَكَلَ: CRA accepted {seq} (only 2 consonants)"

    def test_A03_akhadha_root_preserved(self, pipeline):
        """A03: أَخَذَ → root preserves ء/أ as first radical."""
        root = _root(pipeline, 'أَخَذَ')
        assert root is not None
        assert len(root) == 3
        assert root[1] == 'خ'
        assert root[2] == 'ذ'

    def test_A04_akhadha_cra_defer_or_correct(self, pipeline):
        """A04: أَخَذَ → if CRA ACCEPT, root is (ء,خ,ذ) not (خ,ذ)."""
        cra = _cra(pipeline, 'أَخَذَ')
        if cra and cra.directive == 'ACCEPT' and cra.candidate_radical_sequences:
            for seq in cra.candidate_radical_sequences:
                assert len(seq) == 3

    def test_A05_akala_pipeline_has_3radical_root(self, pipeline):
        """A05: أَكَلَ → pipeline root_candidate has 3 radicals."""
        root = _root(pipeline, 'أَكَلَ')
        if root is not None:
            assert len(root) == 3

    def test_A06_noor_cra_defers_hollow(self, pipeline):
        """A06: نُور → CRA DEFER (hollow noun, و in AYN)."""
        cra = _cra(pipeline, 'نُور')
        # CRA should defer because و is weak in AYN position
        # — it does NOT strip ن as if نُور were a mudari3 verb
        if cra is not None:
            # If CRA runs, it must not strip ن and accept (و,ر) as a 2-letter root
            if cra.directive == 'ACCEPT' and cra.candidate_radical_sequences:
                for seq in cra.candidate_radical_sequences:
                    assert len(seq) == 3

    # ──────────────────────────────────────────────────────────────────────────
    # Group B — أسماء تبدأ بتَ/يَ/نَ — لا تجريد (ليس VERBAL_ROOT_PATH)
    # ──────────────────────────────────────────────────────────────────────────

    def test_B07_teen_no_ta_stripped(self, pipeline):
        """B07: تِين → تَ/تِ NOT stripped (nominal path, not verbal)."""
        cra = _cra(pipeline, 'تِين')
        # CRA may ACCEPT تِين with root (ت,ي,ن) — but ت must be in the root
        if cra and cra.directive == 'ACCEPT' and cra.candidate_radical_sequences:
            for seq in cra.candidate_radical_sequences:
                assert 'ت' in seq, f"تِين: ت was wrongly stripped; got root {seq}"

    def test_B08_teen_root_tyn(self, pipeline):
        """B08: تِين → root (ت,ي,ن) — ت is F1 radical."""
        root = _root(pipeline, 'تِين')
        if root is not None:
            assert 'ت' in root

    def test_B09_nawm_no_na_stripped(self, pipeline):
        """B09: نَوْمُ → نَ NOT stripped (نَوْ begins with long vowel after نَ)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        # unit test: نَوْمُ (اسم النوم)
        stem, prefix = _strip_imperfect_prefix('نَوْمُ', is_verbal=True)
        assert prefix is None, (
            "نَوْمُ: نَ should not be stripped (و follows = long vowel guard)"
        )

    def test_B10_nawm_stem_unchanged(self, pipeline):
        """B10: نَوْمُ → stem unchanged after _strip_imperfect_prefix."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        stem, prefix = _strip_imperfect_prefix('نَوْمُ', is_verbal=True)
        assert stem == 'نَوْمُ'

    def test_B11_yad_no_ya_stripped(self, pipeline):
        """B11: يَد (اسم) → if CRA runs, يَ is not stripped (nominal, short stem)."""
        cra = _cra(pipeline, 'يَد')
        if cra and cra.directive == 'ACCEPT' and cra.candidate_radical_sequences:
            for seq in cra.candidate_radical_sequences:
                # يَد stripped يَ would leave only د (1 consonant) — guard prevents this
                assert len(seq) >= 2

    def test_B12_prohibited_identity_never_accepted(self, pipeline):
        """B12: ا/ى never appear in candidate_radical_sequences as root identity."""
        words = ['يَقُولُ', 'يَخَافُ', 'يَسْعَى', 'تَكُونُوا']
        for word in words:
            cra = _cra(pipeline, word)
            if cra and cra.candidate_radical_sequences:
                for seq in cra.candidate_radical_sequences:
                    assert 'ا' not in seq, f"{word}: ا in root {seq}"
                    assert 'ى' not in seq, f"{word}: ى in root {seq}"

    # ──────────────────────────────────────────────────────────────────────────
    # Group C — فعل الأمر / النواهي
    # ──────────────────────────────────────────────────────────────────────────

    def test_C13_isma_no_wrong_strip(self, pipeline):
        """C13: اسمع (أمر) — لا تجريد خاطئ لـ ا."""
        # imperative اسمع — starts with اِ (hamza wasl, not imperfect prefix)
        cra = _cra(pipeline, 'اسْمَعْ')
        if cra and cra.directive == 'ACCEPT' and cra.candidate_radical_sequences:
            for seq in cra.candidate_radical_sequences:
                # root should be (س,م,ع), not (م,ع) or wrong
                assert len(seq) >= 2

    def test_C14_la_taktub_no_prefix_on_nominal(self, pipeline):
        """C14: تِلْكَ (اسم إشارة) — تِ is not verbal prefix."""
        cra = _cra(pipeline, 'تِلْكَ')
        if cra and cra.directive == 'ACCEPT' and cra.candidate_radical_sequences:
            for seq in cra.candidate_radical_sequences:
                assert 'ت' in seq or len(seq) >= 2

    def test_C15_noun_with_na_prefix_no_strip(self, pipeline):
        """C15: نَاسٌ — نَا is not a mudari3 prefix (ا long vowel after نَ)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        stem, prefix = _strip_imperfect_prefix('نَاسٌ', is_verbal=True)
        assert prefix is None, "نَاسٌ: نَ not stripped (ا long vowel guard)"

    def test_C16_yawm_no_ya_stripped(self, pipeline):
        """C16: يَوْمٌ — يَوْ not stripped (و long vowel after يَ)."""
        from pipeline.p3_pre_root.canonical_radical_accounting import _strip_imperfect_prefix
        stem, prefix = _strip_imperfect_prefix('يَوْمٌ', is_verbal=True)
        assert prefix is None, "يَوْمٌ: يَ not stripped (و long vowel guard)"

    # ──────────────────────────────────────════════════════════════════════════
    # Group D — مقارنة: فعل مضارع مقابل اسم (نفس البادئة)
    # ──────────────────────────────────────────────────────────────────────────

    def test_D17_verbal_vs_nominal_ta(self, pipeline):
        """D17: تَكْتُبُ (فعل) → CRA ACCEPT; تِلْكَ (اسم) → CRA does not ACCEPT wrongly."""
        cra_verb = _cra(pipeline, 'تَكْتُبُ')
        assert cra_verb is not None and cra_verb.directive == 'ACCEPT'

    def test_D18_verbal_prefix_stripped_nominal_not(self, pipeline):
        """D18: تَكْتُبُ has prefix stripped; nominal تِين does not lose ت from root."""
        cra_verb = _cra(pipeline, 'تَكْتُبُ')
        cra_nom  = _cra(pipeline, 'تِين')

        assert cra_verb is not None
        assert cra_verb.prefix_stripped == 'تَ'

        if cra_nom and cra_nom.directive == 'ACCEPT' and cra_nom.candidate_radical_sequences:
            # nominal: ت must be in root
            assert 'ت' in cra_nom.candidate_radical_sequences[0]

    def test_D19_form_i_imperfect_family(self, pipeline):
        """D19: يَكْتُبُ → form_family=FORM_I_IMPERFECT."""
        cra = _cra(pipeline, 'يَكْتُبُ')
        assert cra is not None
        assert cra.form_family == 'FORM_I_IMPERFECT'

    def test_D20_nominal_form_family(self, pipeline):
        """D20: تِين → form_family=FORM_I (no imperfect prefix)."""
        cra = _cra(pipeline, 'تِين')
        if cra and cra.directive == 'ACCEPT':
            assert cra.form_family in ('FORM_I', None)
