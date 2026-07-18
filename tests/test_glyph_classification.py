#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_glyph_classification.py — Phase A unit tests for glyph_classification.py

Coverage:
  1. BaseGlyphClass — every codepoint in _BASE_GLYPH_MAP + unknowns
  2. MarkClass — every codepoint in _MARK_CLASS_MAP + unknowns
  3. MarkState derivation — all six states + conflict scenarios
  4. GlyphTrace construction via build_glyph_traces()
  5. GlyphJudgment.from_trace() — P0 pass/block
  6. P0 licensing — what passes and what doesn't
  7. Governing distinction: MarkClass.SUKUN ≠ MarkState.ABSENT
  8. Shadda expansion
  9. ة Phase A fix — must pass P0
  10. Hamza forms — pre-normalization forms blocked at P0
  11. Convenience accessors: last_base_glyph(), is_mudaric_form(), is_verbal_dual_host()
  12. Edge cases: empty string, tatweel, unknown codepoints
"""

import sys
import os
import unicodedata
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glyph_classification import (
    BaseGlyphClass,
    MarkClass,
    MarkState,
    GlyphTrace,
    GlyphJudgment,
    classify_base_glyph,
    classify_combining_mark,
    build_glyph_traces,
    p0_licensed,
    last_base_glyph,
    is_mudaric_form,
    is_verbal_dual_host,
)


# ══════════════════════════════════════════════════════════════════════════════
# 1. BaseGlyphClass classification
# ══════════════════════════════════════════════════════════════════════════════

class TestClassifyBaseGlyph(unittest.TestCase):

    def test_hamza_alone(self):
        self.assertEqual(classify_base_glyph('ء'), BaseGlyphClass.HAMZA_ALONE)

    def test_alef_madda(self):
        self.assertEqual(classify_base_glyph('آ'), BaseGlyphClass.ALEF_MADDA)

    def test_hamza_on_alef_above(self):
        self.assertEqual(classify_base_glyph('أ'), BaseGlyphClass.HAMZA_ON_ALEF_ABOVE)

    def test_hamza_on_waw(self):
        self.assertEqual(classify_base_glyph('ؤ'), BaseGlyphClass.HAMZA_ON_WAW)

    def test_hamza_on_alef_below(self):
        self.assertEqual(classify_base_glyph('إ'), BaseGlyphClass.HAMZA_ON_ALEF_BELOW)

    def test_hamza_on_ya(self):
        self.assertEqual(classify_base_glyph('ئ'), BaseGlyphClass.HAMZA_ON_YA)

    def test_long_vowel_alef(self):
        self.assertEqual(classify_base_glyph('ا'), BaseGlyphClass.LONG_VOWEL_ALEF)

    def test_ta_marbuta_phase_a_fix(self):
        """Phase A core fix: ة must classify as CONSONANT_TA_MARBUTA, not UNKNOWN."""
        self.assertEqual(classify_base_glyph('ة'), BaseGlyphClass.CONSONANT_TA_MARBUTA)

    def test_consonant_plain_ba(self):
        self.assertEqual(classify_base_glyph('ب'), BaseGlyphClass.CONSONANT_PLAIN)

    def test_consonant_plain_ta(self):
        """ت must stay CONSONANT_PLAIN — distinct from ة."""
        self.assertEqual(classify_base_glyph('ت'), BaseGlyphClass.CONSONANT_PLAIN)

    def test_consonant_plain_all_25(self):
        """All 25 canonical consonants classify as CONSONANT_PLAIN (excluding ة, و, ي, hamzas)."""
        consonants_25 = 'بتثجحخدذرزسشصضطظعغفقكلمنه'
        for ch in consonants_25:
            with self.subTest(ch=ch):
                self.assertEqual(classify_base_glyph(ch), BaseGlyphClass.CONSONANT_PLAIN,
                                 f'{ch!r} (U+{ord(ch):04X}) should be CONSONANT_PLAIN')

    def test_semi_vowel_waw(self):
        self.assertEqual(classify_base_glyph('و'), BaseGlyphClass.SEMI_VOWEL_WAW)

    def test_semi_vowel_ya(self):
        self.assertEqual(classify_base_glyph('ي'), BaseGlyphClass.SEMI_VOWEL_YA)

    def test_alif_maqsura(self):
        self.assertEqual(classify_base_glyph('ى'), BaseGlyphClass.ALIF_MAQSURA)

    def test_tatweel(self):
        self.assertEqual(classify_base_glyph('ـ'), BaseGlyphClass.TATWEEL)

    def test_unknown_latin(self):
        self.assertEqual(classify_base_glyph('X'), BaseGlyphClass.UNKNOWN)

    def test_unknown_digit(self):
        self.assertEqual(classify_base_glyph('5'), BaseGlyphClass.UNKNOWN)

    def test_unknown_space(self):
        self.assertEqual(classify_base_glyph(' '), BaseGlyphClass.UNKNOWN)

    def test_ta_marbuta_not_ta(self):
        """ة and ت are distinct — must NOT return the same class."""
        self.assertNotEqual(
            classify_base_glyph('ة'),
            classify_base_glyph('ت'),
        )


# ══════════════════════════════════════════════════════════════════════════════
# 2. MarkClass classification
# ══════════════════════════════════════════════════════════════════════════════

class TestClassifyCombiningMark(unittest.TestCase):

    def test_fatha(self):
        self.assertEqual(classify_combining_mark('َ'), MarkClass.FATHA)

    def test_damma(self):
        self.assertEqual(classify_combining_mark('ُ'), MarkClass.DAMMA)

    def test_kasra(self):
        self.assertEqual(classify_combining_mark('ِ'), MarkClass.KASRA)

    def test_fathatan(self):
        self.assertEqual(classify_combining_mark('ً'), MarkClass.FATHATAN)

    def test_dammatan(self):
        self.assertEqual(classify_combining_mark('ٌ'), MarkClass.DAMMATAN)

    def test_kasratan(self):
        self.assertEqual(classify_combining_mark('ٍ'), MarkClass.KASRATAN)

    def test_sukun(self):
        self.assertEqual(classify_combining_mark('ْ'), MarkClass.SUKUN)

    def test_shadda(self):
        self.assertEqual(classify_combining_mark('ّ'), MarkClass.SHADDA)

    def test_superscript_alef(self):
        self.assertEqual(classify_combining_mark('ٰ'), MarkClass.SUPERSCRIPT_ALEF)

    def test_hamza_above(self):
        """U+0654 — preserved in Phase A, not stripped."""
        self.assertEqual(classify_combining_mark('ٔ'), MarkClass.HAMZA_ABOVE)

    def test_hamza_below(self):
        """U+0655 — preserved in Phase A, not stripped."""
        self.assertEqual(classify_combining_mark('ٕ'), MarkClass.HAMZA_BELOW)

    def test_madda_above(self):
        """U+0653 — preserved in Phase A, not stripped."""
        self.assertEqual(classify_combining_mark('ٓ'), MarkClass.MADDA_ABOVE)

    def test_unknown_mark(self):
        # U+0300 COMBINING GRAVE ACCENT — not an Arabic mark
        self.assertEqual(classify_combining_mark('̀'), MarkClass.UNKNOWN)


# ══════════════════════════════════════════════════════════════════════════════
# 3. MarkState derivation
# ══════════════════════════════════════════════════════════════════════════════

class TestMarkStateDerivation(unittest.TestCase):
    """Test MarkState via build_glyph_traces() rather than the private function."""

    def _state(self, s: str) -> MarkState:
        """Get the MarkState of the first (and typically only) glyph."""
        traces = build_glyph_traces(s)
        self.assertTrue(traces, f'Expected at least one trace from {s!r}')
        return traces[0].mark_state

    def test_fatha_gives_explicit_vowel(self):
        self.assertEqual(self._state('بَ'), MarkState.EXPLICIT_VOWEL)

    def test_damma_gives_explicit_vowel(self):
        self.assertEqual(self._state('بُ'), MarkState.EXPLICIT_VOWEL)

    def test_kasra_gives_explicit_vowel(self):
        self.assertEqual(self._state('بِ'), MarkState.EXPLICIT_VOWEL)

    def test_sukun_gives_explicit_sukun(self):
        """Written sukun (U+0652) → EXPLICIT_SUKUN, not ABSENT."""
        self.assertEqual(self._state('بْ'), MarkState.EXPLICIT_SUKUN)

    def test_fathatan_gives_tanwin(self):
        self.assertEqual(self._state('بً'), MarkState.TANWIN)

    def test_dammatan_gives_tanwin(self):
        self.assertEqual(self._state('بٌ'), MarkState.TANWIN)

    def test_kasratan_gives_tanwin(self):
        self.assertEqual(self._state('بٍ'), MarkState.TANWIN)

    def test_no_mark_gives_absent(self):
        """No mark written → ABSENT (NOT the same as EXPLICIT_SUKUN)."""
        self.assertEqual(self._state('ب'), MarkState.ABSENT)

    def test_shadda_alone_gives_shadda_compound(self):
        self.assertEqual(self._state('بّ'), MarkState.SHADDA_COMPOUND)

    def test_shadda_with_vowel_gives_explicit_vowel(self):
        """Shadda + kasra → EXPLICIT_VOWEL (the vowel is what matters)."""
        self.assertEqual(self._state('بِّ'), MarkState.EXPLICIT_VOWEL)

    def test_fatha_plus_kasra_gives_conflicting(self):
        # Construct raw string with two conflicting vowels
        s = 'ب' + 'َ' + 'ِ'  # ba + fatha + kasra
        self.assertEqual(self._state(s), MarkState.CONFLICTING)

    def test_vowel_plus_sukun_gives_conflicting(self):
        s = 'ب' + 'َ' + 'ْ'  # ba + fatha + sukun
        self.assertEqual(self._state(s), MarkState.CONFLICTING)


# ══════════════════════════════════════════════════════════════════════════════
# 4. Governing distinction: SUKUN ≠ ABSENT
# ══════════════════════════════════════════════════════════════════════════════

class TestSukunVsAbsentDistinction(unittest.TestCase):
    """
    The most critical invariant in the entire system:
    MarkClass.SUKUN = علامة مكتوبة صراحةً ≠ غياب العلامة = MarkState.ABSENT
    """

    def test_sukun_written_is_explicit_sukun(self):
        t = build_glyph_traces('مْ')[0]
        self.assertEqual(t.mark_state, MarkState.EXPLICIT_SUKUN)
        self.assertIn(MarkClass.SUKUN, t.mark_classes)

    def test_no_mark_is_absent(self):
        t = build_glyph_traces('م')[0]
        self.assertEqual(t.mark_state, MarkState.ABSENT)
        self.assertNotIn(MarkClass.SUKUN, t.mark_classes)

    def test_sukun_state_is_not_absent(self):
        t_sukun  = build_glyph_traces('مْ')[0]
        t_absent = build_glyph_traces('م')[0]
        self.assertNotEqual(t_sukun.mark_state, t_absent.mark_state,
                            'EXPLICIT_SUKUN and ABSENT must be different states')

    def test_has_sukun_property_false_when_absent(self):
        t = build_glyph_traces('م')[0]
        self.assertFalse(t.has_sukun)
        self.assertTrue(t.absent_haraka)

    def test_has_sukun_property_true_when_written(self):
        t = build_glyph_traces('مْ')[0]
        self.assertTrue(t.has_sukun)
        self.assertFalse(t.absent_haraka)

    def test_absent_haraka_property_false_when_voweled(self):
        t = build_glyph_traces('مِ')[0]
        self.assertFalse(t.absent_haraka)

    def test_absent_haraka_property_false_when_sukun(self):
        t = build_glyph_traces('مْ')[0]
        self.assertFalse(t.absent_haraka)


# ══════════════════════════════════════════════════════════════════════════════
# 5. ة Phase A fix — P0 licensing
# ══════════════════════════════════════════════════════════════════════════════

class TestTaMarbutaP0Fix(unittest.TestCase):

    def test_ta_marbuta_classifies_correctly(self):
        t = build_glyph_traces('ة')[0]
        self.assertEqual(t.base_class, BaseGlyphClass.CONSONANT_TA_MARBUTA)

    def test_ta_marbuta_passes_p0(self):
        """Core Phase A fix: ة must pass P0."""
        t = build_glyph_traces('ة')[0]
        self.assertTrue(t.p0_passes(), 'ة must pass P0 after Phase A')

    def test_ta_marbuta_in_p0_licensed_set(self):
        self.assertIn(BaseGlyphClass.CONSONANT_TA_MARBUTA, p0_licensed())

    def test_ta_marbuta_judgment_pass(self):
        t = build_glyph_traces('ة')[0]
        j = GlyphJudgment.from_trace(t)
        self.assertEqual(j.p0_verdict, 'PASS')

    def test_ta_marbuta_with_fatha(self):
        """ةَ — ة with fatha: passes P0, mark_state = EXPLICIT_VOWEL."""
        traces = build_glyph_traces('ةَ')
        self.assertEqual(len(traces), 1)
        t = traces[0]
        self.assertEqual(t.base_class, BaseGlyphClass.CONSONANT_TA_MARBUTA)
        self.assertTrue(t.p0_passes())
        self.assertEqual(t.mark_state, MarkState.EXPLICIT_VOWEL)

    def test_ta_marbuta_with_dammatan(self):
        """ةٌ — final tanwin on ة: passes P0, mark_state = TANWIN."""
        traces = build_glyph_traces('ةٌ')
        t = traces[0]
        self.assertEqual(t.base_class, BaseGlyphClass.CONSONANT_TA_MARBUTA)
        self.assertTrue(t.p0_passes())
        self.assertEqual(t.mark_state, MarkState.TANWIN)

    def test_ta_marbuta_in_word_layla(self):
        """اللَّيْلَةَ — ة as final consonant in a real word."""
        # Use a simplified form without shadda complication: لَيْلَةَ
        traces = build_glyph_traces('لَيْلَةَ')
        final  = last_base_glyph(traces)
        self.assertIsNotNone(final)
        self.assertEqual(final.base_class, BaseGlyphClass.CONSONANT_TA_MARBUTA)
        self.assertTrue(final.p0_passes())
        self.assertTrue(final.is_final_position)

    def test_ta_marbuta_in_word_thamma(self):
        """ثَمَّةَ — ة in مَبنيّ form."""
        traces = build_glyph_traces('ثَمَّةَ')
        final  = last_base_glyph(traces)
        self.assertIsNotNone(final)
        self.assertEqual(final.base_class, BaseGlyphClass.CONSONANT_TA_MARBUTA)
        self.assertTrue(final.p0_passes())


# ══════════════════════════════════════════════════════════════════════════════
# 6. P0 licensing — what passes vs what doesn't
# ══════════════════════════════════════════════════════════════════════════════

class TestP0Licensing(unittest.TestCase):

    def _passes(self, ch: str) -> bool:
        return build_glyph_traces(ch)[0].p0_passes()

    def test_consonants_pass(self):
        for ch in 'بتثجحخدذرزسشصضطظعغفقكلمنه':
            with self.subTest(ch=ch):
                self.assertTrue(self._passes(ch), f'{ch!r} should pass P0')

    def test_ta_marbuta_passes(self):
        self.assertTrue(self._passes('ة'))

    def test_hamza_alone_passes(self):
        self.assertTrue(self._passes('ء'))

    def test_long_vowel_alef_passes(self):
        self.assertTrue(self._passes('ا'))

    def test_alif_maqsura_passes(self):
        self.assertTrue(self._passes('ى'))

    def test_semi_vowel_waw_passes(self):
        self.assertTrue(self._passes('و'))

    def test_semi_vowel_ya_passes(self):
        self.assertTrue(self._passes('ي'))

    def test_hamza_on_alef_above_blocked(self):
        """أ is pre-normalization — normalize() should have run first."""
        self.assertFalse(self._passes('أ'))

    def test_hamza_on_alef_below_blocked(self):
        self.assertFalse(self._passes('إ'))

    def test_hamza_on_waw_blocked(self):
        self.assertFalse(self._passes('ؤ'))

    def test_hamza_on_ya_blocked(self):
        self.assertFalse(self._passes('ئ'))

    def test_alef_madda_blocked(self):
        self.assertFalse(self._passes('آ'))

    def test_tatweel_blocked(self):
        self.assertFalse(self._passes('ـ'))

    def test_unknown_blocked(self):
        self.assertFalse(self._passes('X'))

    def test_judgment_pass(self):
        t = build_glyph_traces('ب')[0]
        j = GlyphJudgment.from_trace(t)
        self.assertEqual(j.p0_verdict, 'PASS')
        self.assertEqual(j.nfc_base, 'ب')

    def test_judgment_block(self):
        t = build_glyph_traces('أ')[0]
        j = GlyphJudgment.from_trace(t)
        self.assertEqual(j.p0_verdict, 'BLOCK')

    def test_judgment_p1_none_before_p1_runs(self):
        """P1/P2/P3 fields are None until the corresponding gate runs."""
        t = build_glyph_traces('ب')[0]
        j = GlyphJudgment.from_trace(t)
        self.assertIsNone(j.p1_verdict)
        self.assertIsNone(j.p2_verdict)
        self.assertIsNone(j.p3_cell)


# ══════════════════════════════════════════════════════════════════════════════
# 7. build_glyph_traces() — core construction
# ══════════════════════════════════════════════════════════════════════════════

class TestBuildGlyphTraces(unittest.TestCase):

    def test_empty_string(self):
        self.assertEqual(build_glyph_traces(''), [])

    def test_single_bare_char(self):
        traces = build_glyph_traces('م')
        self.assertEqual(len(traces), 1)
        t = traces[0]
        self.assertEqual(t.nfc_base, 'م')
        self.assertEqual(t.raw_base, 'م')
        self.assertEqual(t.mark_classes, ())
        self.assertEqual(t.mark_state, MarkState.ABSENT)
        self.assertEqual(t.position_in_token, 0)
        self.assertTrue(t.is_final_position)

    def test_single_voweled_char(self):
        traces = build_glyph_traces('مِ')
        self.assertEqual(len(traces), 1)
        t = traces[0]
        self.assertEqual(t.nfc_base, 'م')
        self.assertIn(MarkClass.KASRA, t.mark_classes)
        self.assertEqual(t.mark_state, MarkState.EXPLICIT_VOWEL)
        self.assertTrue(t.has_kasra)

    def test_two_char_word(self):
        traces = build_glyph_traces('هُوَ')
        # هُ وَ
        self.assertEqual(len(traces), 2)
        self.assertEqual(traces[0].nfc_base, 'ه')
        self.assertEqual(traces[0].mark_state, MarkState.EXPLICIT_VOWEL)
        self.assertTrue(traces[0].has_damma)
        self.assertEqual(traces[1].nfc_base, 'و')
        self.assertTrue(traces[1].has_fatha)
        self.assertTrue(traces[1].is_final_position)
        self.assertFalse(traces[0].is_final_position)

    def test_position_indices(self):
        traces = build_glyph_traces('ءَنَا')
        for i, t in enumerate(traces):
            self.assertEqual(t.position_in_token, i)

    def test_is_final_position(self):
        traces = build_glyph_traces('ءَنَا')
        self.assertFalse(traces[0].is_final_position)
        self.assertFalse(traces[1].is_final_position)
        self.assertTrue(traces[2].is_final_position)

    def test_nfc_span_coverage(self):
        nfc_s = unicodedata.normalize('NFC', 'كَتَبَ')
        traces = build_glyph_traces('كَتَبَ')
        # All NFC spans should cover the whole string collectively
        self.assertEqual(traces[0].nfc_span[0], 0)
        self.assertEqual(traces[-1].nfc_span[1], len(nfc_s))

    def test_nfc_span_non_overlapping(self):
        traces = build_glyph_traces('ذَهَبَ')
        for i in range(len(traces) - 1):
            self.assertEqual(traces[i].nfc_span[1], traces[i+1].nfc_span[0])

    def test_tatweel_not_final_position(self):
        """Tatweel at end: the non-tatweel before it should be is_final_position."""
        traces = build_glyph_traces('مـ')
        self.assertEqual(traces[0].base_class, BaseGlyphClass.CONSONANT_PLAIN)
        self.assertEqual(traces[1].base_class, BaseGlyphClass.TATWEEL)
        # The م at position 0 should be is_final_position since ـ is TATWEEL
        self.assertTrue(traces[0].is_final_position)
        self.assertFalse(traces[1].is_final_position)

    def test_nfc_normalization_applied_internally(self):
        """build_glyph_traces normalizes to NFC internally."""
        # Pre-NFC decomposed form of بَ (if any) should give same result as composed
        composed   = 'بَ'
        decomposed = unicodedata.normalize('NFD', 'بَ')
        t_comp = build_glyph_traces(composed)
        t_deco = build_glyph_traces(decomposed)
        self.assertEqual(t_comp[0].nfc_base,   t_deco[0].nfc_base)
        self.assertEqual(t_comp[0].mark_state, t_deco[0].mark_state)

    def test_mark_classes_length_matches_nfc_marks(self):
        traces = build_glyph_traces('مِّ')
        t = traces[0]
        self.assertEqual(len(t.mark_classes), len(t.nfc_marks))

    def test_superscript_alef_classified(self):
        """ٰ (U+0670) on a letter: classified as SUPERSCRIPT_ALEF."""
        s = 'رَحْمَٰنِ'  # الرحمن with superscript alef
        traces = build_glyph_traces(s)
        # Find the trace with superscript alef
        found = any(t.has_superscript_alef for t in traces)
        self.assertTrue(found, 'Expected at least one trace with SUPERSCRIPT_ALEF')

    def test_unlicensed_marks_empty_for_clean_input(self):
        traces = build_glyph_traces('مِّ')
        self.assertEqual(traces[0].unlicensed_marks, ())

    def test_hamza_above_preserved(self):
        """U+0654 on a letter is preserved as HAMZA_ABOVE, not stripped."""
        s = 'هٔ'  # ha + combining hamza above
        traces = build_glyph_traces(s)
        self.assertIn(MarkClass.HAMZA_ABOVE, traces[0].mark_classes)


# ══════════════════════════════════════════════════════════════════════════════
# 8. Shadda expansion
# ══════════════════════════════════════════════════════════════════════════════

class TestShaddaExpansion(unittest.TestCase):

    def test_shadda_with_kasra_expansion(self):
        """مِّ — shadda + kasra: sakin copy = مْ, voweled copy = مِ."""
        t = build_glyph_traces('مِّ')[0]
        self.assertTrue(t.has_shadda)
        self.assertEqual(t.shadda_sakin_copy,   'مْ')
        self.assertEqual(t.shadda_voweled_copy, 'مِ')

    def test_shadda_with_fatha_expansion(self):
        """مَّ — shadda + fatha."""
        t = build_glyph_traces('مَّ')[0]
        self.assertEqual(t.shadda_sakin_copy,   'مْ')
        self.assertEqual(t.shadda_voweled_copy, 'مَ')

    def test_shadda_with_damma_expansion(self):
        """مُّ — shadda + damma."""
        t = build_glyph_traces('مُّ')[0]
        self.assertEqual(t.shadda_sakin_copy,   'مْ')
        self.assertEqual(t.shadda_voweled_copy, 'مُ')

    def test_shadda_alone_expansion(self):
        """مّ — shadda with no vowel: sakin copy = مْ, voweled copy = م (bare)."""
        t = build_glyph_traces('مّ')[0]
        self.assertTrue(t.has_shadda)
        self.assertEqual(t.shadda_sakin_copy,   'مْ')
        self.assertEqual(t.shadda_voweled_copy, 'م')

    def test_no_shadda_copies_none(self):
        """A letter without shadda has None for shadda copies."""
        t = build_glyph_traces('مِ')[0]
        self.assertFalse(t.has_shadda)
        self.assertIsNone(t.shadda_sakin_copy)
        self.assertIsNone(t.shadda_voweled_copy)

    def test_shadda_mark_state(self):
        """مِّ has EXPLICIT_VOWEL (kasra written alongside shadda)."""
        t = build_glyph_traces('مِّ')[0]
        self.assertEqual(t.mark_state, MarkState.EXPLICIT_VOWEL)

    def test_shadda_alone_mark_state(self):
        """مّ without vowel → SHADDA_COMPOUND."""
        t = build_glyph_traces('مّ')[0]
        self.assertEqual(t.mark_state, MarkState.SHADDA_COMPOUND)


# ══════════════════════════════════════════════════════════════════════════════
# 9. Convenience accessors
# ══════════════════════════════════════════════════════════════════════════════

class TestConvenienceAccessors(unittest.TestCase):

    # ── last_base_glyph ───────────────────────────────────────────────────

    def test_last_base_glyph_simple(self):
        traces = build_glyph_traces('ذَهَبَ')
        last   = last_base_glyph(traces)
        self.assertIsNotNone(last)
        self.assertEqual(last.nfc_base, 'ب')

    def test_last_base_glyph_skips_tatweel(self):
        traces = build_glyph_traces('مـ')
        last   = last_base_glyph(traces)
        self.assertIsNotNone(last)
        self.assertEqual(last.nfc_base, 'م')  # tatweel skipped

    def test_last_base_glyph_empty(self):
        self.assertIsNone(last_base_glyph([]))

    # ── is_mudaric_form ────────────────────────────────────────────────────

    def test_mudaric_ya_prefix_with_sukun(self):
        """يَرْمِينَ — يَ prefix + fatha + sukun on ر → mudāri'."""
        traces = build_glyph_traces('يَرْمِينَ')
        self.assertTrue(is_mudaric_form(traces))

    def test_mudaric_ta_prefix_with_sukun(self):
        """تَكْتُبُ — تَ prefix + sukun on ك → mudāri'."""
        traces = build_glyph_traces('تَكْتُبُ')
        self.assertTrue(is_mudaric_form(traces))

    def test_nominal_plural_not_mudaric(self):
        """نَاءِمِينَ — starts with نَ, not يَ/تَ → not mudāri'."""
        traces = build_glyph_traces('نَاءِمِينَ')
        self.assertFalse(is_mudaric_form(traces))

    def test_short_word_not_mudaric(self):
        """Words shorter than 4 base glyphs → not mudāri'."""
        traces = build_glyph_traces('يَا')
        self.assertFalse(is_mudaric_form(traces))

    def test_ya_without_sukun_not_mudaric(self):
        """يَدَيْنِ — يَ prefix but second letter has fatha (not sukun) → not mudāri'."""
        traces = build_glyph_traces('يَدَيْنِ')
        self.assertFalse(is_mudaric_form(traces))

    # ── is_verbal_dual_host ────────────────────────────────────────────────

    def test_verbal_dual_madi(self):
        """كَتَبَا — first letter has fatha, not ي, not definite article → verbal dual host."""
        traces = build_glyph_traces('كَتَبَ')  # stripped form (before alif attachment)
        self.assertTrue(is_verbal_dual_host(traces))

    def test_verbal_dual_hamza_start(self):
        """ءَلْكِتَابُ — starts with ءَلْ (definite article) → NOT verbal dual."""
        traces = build_glyph_traces('ءَلْكِتَابُ')
        self.assertFalse(is_verbal_dual_host(traces))

    def test_verbal_dual_ya_start_blocked(self):
        """يَرْمِيَ — starts with يَ → blocked (mudāri' verbs use a different guard)."""
        traces = build_glyph_traces('يَرْمِيَ')
        self.assertFalse(is_verbal_dual_host(traces))

    def test_verbal_dual_short_word(self):
        """Words shorter than 4 base glyphs → not verbal dual."""
        traces = build_glyph_traces('قَدْ')
        self.assertFalse(is_verbal_dual_host(traces))

    def test_verbal_dual_kasra_first_blocked(self):
        """حِينَمَ — first letter has kasra (not fatha) → not verbal dual host."""
        traces = build_glyph_traces('حِينَمَ')
        self.assertFalse(is_verbal_dual_host(traces))


# ══════════════════════════════════════════════════════════════════════════════
# 10. GlyphTrace frozen / immutability
# ══════════════════════════════════════════════════════════════════════════════

class TestGlyphTraceFrozen(unittest.TestCase):

    def test_trace_is_frozen(self):
        t = build_glyph_traces('م')[0]
        with self.assertRaises((AttributeError, TypeError)):
            t.nfc_base = 'ب'  # type: ignore[misc]

    def test_judgment_is_frozen(self):
        t = build_glyph_traces('م')[0]
        j = GlyphJudgment.from_trace(t)
        with self.assertRaises((AttributeError, TypeError)):
            j.p0_verdict = 'TAMPERED'  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# 11. BaseGlyphClass / MarkClass str-enum interop
# ══════════════════════════════════════════════════════════════════════════════

class TestEnumStrInterop(unittest.TestCase):
    """str-Enum: enum values compare equal to their string equivalents."""

    def test_base_glyph_class_str_value(self):
        self.assertEqual(BaseGlyphClass.CONSONANT_PLAIN, 'CONSONANT_PLAIN')

    def test_mark_class_str_value(self):
        self.assertEqual(MarkClass.FATHA, 'FATHA')

    def test_mark_state_str_value(self):
        self.assertEqual(MarkState.ABSENT, 'ABSENT')

    def test_base_glyph_class_in_str_set(self):
        licensed = {g.value for g in p0_licensed()}
        self.assertIn('CONSONANT_PLAIN', licensed)
        self.assertIn('CONSONANT_TA_MARBUTA', licensed)


# ══════════════════════════════════════════════════════════════════════════════
# 12. Real Arabic mabniyat forms (integration-style)
# ══════════════════════════════════════════════════════════════════════════════

class TestRealArabicForms(unittest.TestCase):
    """Build traces for real mabniyat forms and assert key properties."""

    def _traces(self, s: str):
        return build_glyph_traces(s)

    def test_anna_post_normalize(self):
        """ءَنَّ (post-normalize form of أَنَّ): all base chars pass P0."""
        traces = self._traces('ءَنَّ')
        for t in traces:
            with self.subTest(nfc_base=t.nfc_base):
                self.assertTrue(t.p0_passes())

    def test_huwa(self):
        """هُوَ — two base glyphs both pass P0."""
        traces = self._traces('هُوَ')
        self.assertEqual(len(traces), 2)
        self.assertTrue(all(t.p0_passes() for t in traces))

    def test_allathi_post_normalize(self):
        """ءَلَّذِي — post-normalize relative pronoun."""
        traces = self._traces('ءَلَّذِي')
        for t in traces:
            self.assertTrue(t.p0_passes(), f'{t.nfc_base!r} failed P0')

    def test_hadha(self):
        """هَذَا — demonstrative pronoun."""
        traces = self._traces('هَذَا')
        self.assertEqual(len(traces), 3)
        self.assertTrue(all(t.p0_passes() for t in traces))

    def test_inna(self):
        """ءِنَّ — post-normalize particle إِنَّ."""
        traces = self._traces('ءِنَّ')
        for t in traces:
            self.assertTrue(t.p0_passes())

    def test_thamma_ta_marbuta(self):
        """ثَمَّةَ — particle ending in ة; ة must pass P0."""
        traces = self._traces('ثَمَّةَ')
        last = last_base_glyph(traces)
        self.assertIsNotNone(last)
        self.assertEqual(last.base_class, BaseGlyphClass.CONSONANT_TA_MARBUTA)
        self.assertTrue(last.p0_passes())


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    unittest.main(verbosity=2)
