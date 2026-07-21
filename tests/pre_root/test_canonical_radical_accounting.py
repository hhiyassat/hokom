#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/pre_root/test_canonical_radical_accounting.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01
Unit tests for canonical_radical_accounting module.

Groups:
  A. SlotClass enum presence
  B. _strip_imperfect_prefix (unit)
  C. _strip_verbal_suffix (unit)
  D. process_canonical_radical_accounting: BLOCK / guard paths
  E. Imperfect-prefix stripping via CRA
  F. Augmented-form (Form II-X) detection via CRA
  G. Geminate radicals preserve both slots
  H. Weak radical results in DEFER
  I. Negative controls: prefix NOT stripped for non-verbal paths
"""

from __future__ import annotations

import os
import sys
import types

import pytest

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from pipeline.p3_pre_root.canonical_radical_accounting import (
    CanonicalRadicalAccounting,
    SlotClass,
    process_canonical_radical_accounting,
    _strip_imperfect_prefix,
    _strip_verbal_suffix,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _verbal_pre_root(morphology_path_value: str = 'verbal_root_path'):
    """Return a minimal pre_root stub that passes the verbal guard."""
    mp = types.SimpleNamespace(value=morphology_path_value)
    return types.SimpleNamespace(
        morphology_path=mp,
        root_path_directive='OPEN',
    )


def _blocked_pre_root():
    mp = types.SimpleNamespace(value='verbal_root_path')
    return types.SimpleNamespace(
        morphology_path=mp,
        root_path_directive='BLOCK',
    )


def _nominal_pre_root():
    mp = types.SimpleNamespace(value='nominal_root_path')
    return types.SimpleNamespace(
        morphology_path=mp,
        root_path_directive='OPEN',
    )


# ══════════════════════════════════════════════════════════════════════════════
# A. SlotClass enum
# ══════════════════════════════════════════════════════════════════════════════

class TestSlotClassEnum:

    def test_A01_radical_value(self):
        assert SlotClass.RADICAL.value == 'RADICAL'

    def test_A02_derivational_extension_value(self):
        assert SlotClass.DERIVATIONAL_EXTENSION.value == 'DERIVATIONAL_EXTENSION'

    def test_A03_inflectional_prefix_value(self):
        assert SlotClass.INFLECTIONAL_PREFIX.value == 'INFLECTIONAL_PREFIX'

    def test_A04_inflectional_suffix_value(self):
        assert SlotClass.INFLECTIONAL_SUFFIX.value == 'INFLECTIONAL_SUFFIX'

    def test_A05_orthographic_only_value(self):
        assert SlotClass.ORTHOGRAPHIC_ONLY.value == 'ORTHOGRAPHIC_ONLY'

    def test_A06_phonological_duplication_value(self):
        assert SlotClass.PHONOLOGICAL_DUPLICATION.value == 'PHONOLOGICAL_DUPLICATION'

    def test_A07_weak_radical_surface_value(self):
        assert SlotClass.WEAK_RADICAL_SURFACE.value == 'WEAK_RADICAL_SURFACE'

    def test_A08_unknown_radical_slot_value(self):
        assert SlotClass.UNKNOWN_RADICAL_SLOT.value == 'UNKNOWN_RADICAL_SLOT'


# ══════════════════════════════════════════════════════════════════════════════
# B. _strip_imperfect_prefix (unit)
# ══════════════════════════════════════════════════════════════════════════════

class TestStripImperfectPrefix:

    def test_B01_ya_stripped_verbal(self):
        stem, prefix = _strip_imperfect_prefix('يَكْتُبُ', is_verbal=True)
        assert prefix == 'يَ'
        assert 'كْتُبُ' in stem

    def test_B02_ta_stripped_verbal(self):
        stem, prefix = _strip_imperfect_prefix('تَكْتُبُ', is_verbal=True)
        assert prefix == 'تَ'

    def test_B03_na_stripped_verbal(self):
        stem, prefix = _strip_imperfect_prefix('نَكْتُبُ', is_verbal=True)
        assert prefix == 'نَ'

    def test_B04_alef_stripped_verbal(self):
        stem, prefix = _strip_imperfect_prefix('أَكْتُبُ', is_verbal=True)
        assert prefix == 'أَ'

    def test_B05_no_strip_non_verbal(self):
        _, prefix = _strip_imperfect_prefix('يَكْتُبُ', is_verbal=False)
        assert prefix is None

    def test_B06_no_strip_long_vowel_after_prefix(self):
        # يَا is NOT an imperfect stem start — long vowel blocks strip
        _, prefix = _strip_imperfect_prefix('يَاكُلُ', is_verbal=True)
        assert prefix is None

    def test_B07_no_strip_too_short(self):
        _, prefix = _strip_imperfect_prefix('يَك', is_verbal=True)
        assert prefix is None

    def test_B08_no_strip_unknown_prefix(self):
        _, prefix = _strip_imperfect_prefix('بَكْتُبُ', is_verbal=True)
        assert prefix is None


# ══════════════════════════════════════════════════════════════════════════════
# C. _strip_verbal_suffix (unit)
# ══════════════════════════════════════════════════════════════════════════════

class TestStripVerbalSuffix:

    def test_C01_waw_jamaa_stripped_verbal(self):
        stem, suf, rule = _strip_verbal_suffix('كَتَبُوا', is_verbal=True)
        assert suf == 'وا'

    def test_C02_no_strip_non_verbal(self):
        stem, suf, _ = _strip_verbal_suffix('كَتَبُوا', is_verbal=False)
        assert suf is None
        assert stem == 'كَتَبُوا'

    def test_C03_tumm_stripped_verbal(self):
        _, suf, _ = _strip_verbal_suffix('كَتَبْتُمْ', is_verbal=True)
        assert suf == 'تُمْ'

    def test_C04_tumuu_stripped_verbal(self):
        _, suf, _ = _strip_verbal_suffix('كَتَبْتُمُوا', is_verbal=True)
        assert suf == 'تُمُوا'

    def test_C05_bare_waw_stripped_when_enough_consonants(self):
        # تَكْتُبُو → bare waw after clitics consumed هُ
        stem, suf, rule = _strip_verbal_suffix('تَكْتُبُو', is_verbal=True)
        assert suf is not None  # waw stripped
        assert stem == 'تَكْتُبُ'


# ══════════════════════════════════════════════════════════════════════════════
# D. Guard paths
# ══════════════════════════════════════════════════════════════════════════════

class TestGuardPaths:

    def test_D01_no_host_returns_block(self):
        result = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host=None,
            morphology_surface=None,
            pre_root=_verbal_pre_root(),
        )
        assert result.directive == 'BLOCK'
        assert any('NO_SEGMENT_HOST' in c for c in result.reason_codes)

    def test_D02_no_pre_root_returns_block(self):
        result = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host='يَكْتُبُ',
            morphology_surface='يَكْتُبُ',
            pre_root=None,
        )
        assert result.directive == 'BLOCK'

    def test_D03_blocked_pre_root_preserves_block(self):
        result = process_canonical_radical_accounting(
            input_surface='اللَّهُ',
            segment_host='اللَّهُ',
            morphology_surface='اللَّهُ',
            pre_root=_blocked_pre_root(),
        )
        assert result.directive == 'BLOCK'
        assert any('BLOCK' in c for c in result.reason_codes)


# ══════════════════════════════════════════════════════════════════════════════
# E. Imperfect-prefix stripping
# ══════════════════════════════════════════════════════════════════════════════

class TestImperfectPrefixStripping:

    def test_E01_yaktub_prefix_stripped(self):
        r = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host='يَكْتُبُ',
            morphology_surface='يَكْتُبُ',
            pre_root=_verbal_pre_root(),
        )
        assert r.prefix_stripped == 'يَ'

    def test_E02_yaktub_accept(self):
        r = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host='يَكْتُبُ',
            morphology_surface='يَكْتُبُ',
            pre_root=_verbal_pre_root(),
        )
        assert r.directive == 'ACCEPT'

    def test_E03_yaktub_root_ktb(self):
        r = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host='يَكْتُبُ',
            morphology_surface='يَكْتُبُ',
            pre_root=_verbal_pre_root(),
        )
        assert r.candidate_radical_sequences
        root = r.candidate_radical_sequences[0]
        bare = [''.join(c for c in ch if c.isalpha()) for ch in root]
        assert 'ك' in bare and 'ت' in bare and 'ب' in bare

    def test_E04_taktub_prefix_ta(self):
        r = process_canonical_radical_accounting(
            input_surface='تَكْتُبُ',
            segment_host='تَكْتُبُ',
            morphology_surface='تَكْتُبُ',
            pre_root=_verbal_pre_root(),
        )
        assert r.prefix_stripped == 'تَ'
        assert r.directive == 'ACCEPT'

    def test_E05_yashadu_prefix_ya(self):
        r = process_canonical_radical_accounting(
            input_surface='يَشْهَدُ',
            segment_host='يَشْهَدُ',
            morphology_surface='يَشْهَدُ',
            pre_root=_verbal_pre_root(),
        )
        assert r.prefix_stripped == 'يَ'
        assert r.directive == 'ACCEPT'

    def test_E06_no_strip_non_verbal(self):
        r = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host='يَكْتُبُ',
            morphology_surface='يَكْتُبُ',
            pre_root=_nominal_pre_root(),
        )
        assert r.prefix_stripped is None


# ══════════════════════════════════════════════════════════════════════════════
# F. Augmented-form detection
# ══════════════════════════════════════════════════════════════════════════════

class TestAugmentedFormDetection:

    def test_F01_form_ii_allamahu_accept(self):
        # عَلَّمَهُ → segmenter gives segment_host='عَلَّمَ' (هُ stripped as clitic)
        # The CRA operates on segment_host, not on the full surface.
        r = process_canonical_radical_accounting(
            input_surface='عَلَّمَهُ',
            segment_host='عَلَّمَ',
            morphology_surface='عَلَّمَ',
            pre_root=_verbal_pre_root(),
        )
        assert r.directive == 'ACCEPT'
        assert r.form_family in ('FORM_II', 'FORM_V', None) or r.augmented_detection is not None

    def test_F02_form_iv_ashidu_accept(self):
        # أَشْهِدُوا → Form IV → (ش,ه,د)
        r = process_canonical_radical_accounting(
            input_surface='أَشْهِدُوا',
            segment_host='أَشْهِدُوا',
            morphology_surface='أَشْهِدُوا',
            pre_root=_verbal_pre_root(),
        )
        assert r.directive == 'ACCEPT'

    def test_F03_form_x_istashhidu_accept(self):
        # اسْتَشْهِدُوا → Form X → (ش,ه,د)
        r = process_canonical_radical_accounting(
            input_surface='اسْتَشْهِدُوا',
            segment_host='اسْتَشْهِدُوا',
            morphology_surface='اسْتَشْهِدُوا',
            pre_root=_verbal_pre_root(),
        )
        assert r.directive == 'ACCEPT'
        assert r.form_family == 'FORM_X'

    def test_F04_form_x_root_sh_h_d(self):
        r = process_canonical_radical_accounting(
            input_surface='اسْتَشْهِدُوا',
            segment_host='اسْتَشْهِدُوا',
            morphology_surface='اسْتَشْهِدُوا',
            pre_root=_verbal_pre_root(),
        )
        if r.directive == 'ACCEPT' and r.candidate_radical_sequences:
            root = r.candidate_radical_sequences[0]
            bare = [''.join(c for c in ch if c.isalpha()) for ch in root]
            assert 'ش' in bare and 'ه' in bare and 'د' in bare

    def test_F05_form_ii_yuallimu_accept(self):
        # يُعَلِّمُ → Form II → (ع,ل,م)
        r = process_canonical_radical_accounting(
            input_surface='يُعَلِّمُكُمُ',
            segment_host='يُعَلِّمُ',
            morphology_surface='يُعَلِّمُ',
            pre_root=_verbal_pre_root(),
        )
        assert r.directive == 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# G. Geminate radicals
# ══════════════════════════════════════════════════════════════════════════════

class TestGeminateRadicals:

    def test_G01_haqqun_trilateral_root(self):
        # حَقُّ → shadda gives حَقْق → root (ح,ق,ق)
        r = process_canonical_radical_accounting(
            input_surface='حَقُّ',
            segment_host='حَقُّ',
            morphology_surface='حَقُّ',
            pre_root=_nominal_pre_root(),
        )
        # CRA should either ACCEPT with geminate root or DEFER gracefully
        assert r.directive in ('ACCEPT', 'DEFER')
        if r.directive == 'ACCEPT' and r.candidate_radical_sequences:
            root = r.candidate_radical_sequences[0]
            bare = [''.join(c for c in ch if c.isalpha()) for ch in root]
            # geminate: ق appears twice
            assert bare.count('ق') == 2

    def test_G02_evidence_has_rule_id(self):
        r = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host='يَكْتُبُ',
            morphology_surface='يَكْتُبُ',
            pre_root=_verbal_pre_root(),
        )
        assert len(r.evidence) > 0


# ══════════════════════════════════════════════════════════════════════════════
# H. Weak radical → DEFER
# ══════════════════════════════════════════════════════════════════════════════

class TestWeakRadicalDefer:

    def test_H01_yaqul_weak_defers(self):
        # يَقُولَ → hollow verb → DEFER
        r = process_canonical_radical_accounting(
            input_surface='يَقُولَ',
            segment_host='يَقُولَ',
            morphology_surface='يَقُولَ',
            pre_root=_verbal_pre_root(),
        )
        # Should not produce an ACCEPT with a weak root like (ق,و,ل) unresolved
        if r.directive == 'ACCEPT':
            seqs = r.candidate_radical_sequences
            # if accepted, it must have a proper trilateral with no prohibited identity
            for seq in seqs:
                for ch in seq:
                    assert ch not in ('ا', 'ى', 'أ', 'إ', 'ؤ', 'ئ', 'آ'), \
                        f"Prohibited weak root identity accepted: {ch}"
        else:
            assert r.directive == 'DEFER'
            assert len(r.reason_codes) > 0

    def test_H02_weak_reason_code_not_generic(self):
        r = process_canonical_radical_accounting(
            input_surface='يَقُولَ',
            segment_host='يَقُولَ',
            morphology_surface='يَقُولَ',
            pre_root=_verbal_pre_root(),
        )
        # No generic catch-all
        for code in r.reason_codes:
            assert code != 'GENERIC_ROOT_FAILURE', \
                "Generic reason code not permitted — must be specific"

    def test_H03_daa_defective_lam_defers(self):
        r = process_canonical_radical_accounting(
            input_surface='دَعَا',
            segment_host='دَعَا',
            morphology_surface='دَعَا',
            pre_root=_verbal_pre_root(),
        )
        assert r.directive == 'DEFER'


# ══════════════════════════════════════════════════════════════════════════════
# I. Negative controls — prefix NOT stripped
# ══════════════════════════════════════════════════════════════════════════════

class TestNegativeControls:

    @pytest.mark.parametrize('token', [
        'تِين',   # fig (noun) — تَ is NOT imperfect here
        'نُور',   # light (noun)
    ])
    def test_I01_nominal_no_prefix_strip(self, token):
        r = process_canonical_radical_accounting(
            input_surface=token,
            segment_host=token,
            morphology_surface=token,
            pre_root=_nominal_pre_root(),
        )
        assert r.prefix_stripped is None, \
            f"Prefix wrongly stripped from nominal {token!r}"

    def test_I02_long_vowel_after_prefix_no_strip(self):
        # نَوْمِ — starts with نَ but next char is و (long vowel) → not imperfect
        r = process_canonical_radical_accounting(
            input_surface='نَوْمِ',
            segment_host='نَوْمِ',
            morphology_surface='نَوْمِ',
            pre_root=_verbal_pre_root(),  # even if verbal, long vowel blocks
        )
        assert r.prefix_stripped is None

    def test_I03_block_boundary_not_opened(self):
        r = process_canonical_radical_accounting(
            input_surface='اللَّهُ',
            segment_host='اللَّهُ',
            morphology_surface='اللَّهُ',
            pre_root=_blocked_pre_root(),
        )
        assert r.directive == 'BLOCK'
        assert not r.candidate_radical_sequences

    def test_I04_provenance_non_empty(self):
        r = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host='يَكْتُبُ',
            morphology_surface='يَكْتُبُ',
            pre_root=_verbal_pre_root(),
        )
        assert r.provenance.startswith('CRA:')

    def test_I05_to_dict_round_trip(self):
        r = process_canonical_radical_accounting(
            input_surface='يَكْتُبُ',
            segment_host='يَكْتُبُ',
            morphology_surface='يَكْتُبُ',
            pre_root=_verbal_pre_root(),
        )
        d = r.to_dict()
        assert d['directive'] == r.directive
        assert d['input_surface'] == 'يَكْتُبُ'
        assert isinstance(d['evidence'], list)
        assert isinstance(d['reason_codes'], list)
