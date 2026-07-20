#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_inventory.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Inventory correctness tests.
HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import pytest
from pipeline.p0_segmentation.inventory import (
    PROTECTED_WHOLE_TOKENS,
    WHOLE_TOKEN_OPERATORS,
    PROCLITICS,
    LICENSED_MULTI_PROCLITIC_SEQUENCES,
    ENCLITICS,
    INFLECTIONAL_BARE_SUFFIXES,
    MIN_HOST_CONSONANTS_CONJUNCTION,
    MIN_HOST_CONSONANTS_PREPOSITION,
    MIN_HOST_CONSONANTS_FUTURE,
    MIN_HOST_LENGTH_CHARS,
)


class TestProtectedTokens:
    def test_allah_protected(self):
        assert 'الله' in PROTECTED_WHOLE_TOKENS or any('الله' in t for t in PROTECTED_WHOLE_TOKENS)

    def test_huwa_protected(self):
        assert 'هُوَ' in PROTECTED_WHOLE_TOKENS

    def test_hadhihi_protected(self):
        assert 'هَذِهِ' in PROTECTED_WHOLE_TOKENS

    def test_alladhi_protected(self):
        assert 'الَّذِي' in PROTECTED_WHOLE_TOKENS

    def test_protected_is_frozenset(self):
        assert isinstance(PROTECTED_WHOLE_TOKENS, frozenset)


class TestOperators:
    def test_min_in_operators(self):
        assert 'مِنْ' in WHOLE_TOKEN_OPERATORS

    def test_ala_in_operators(self):
        assert 'عَلَى' in WHOLE_TOKEN_OPERATORS

    def test_inna_in_operators(self):
        assert 'إِنَّ' in WHOLE_TOKEN_OPERATORS

    def test_la_in_operators(self):
        assert 'لَا' in WHOLE_TOKEN_OPERATORS or 'لا' in WHOLE_TOKEN_OPERATORS

    def test_operators_is_frozenset(self):
        assert isinstance(WHOLE_TOKEN_OPERATORS, frozenset)


class TestProclitics:
    def test_conjunction_waw(self):
        assert any(t[1] == 'و' and t[2] == 'CONJUNCTION' for t in PROCLITICS)

    def test_conjunction_fa(self):
        assert any(t[1] == 'ف' and t[2] == 'CONJUNCTION' for t in PROCLITICS)

    def test_preposition_ba(self):
        assert any(t[1] == 'ب' and t[2] == 'PREPOSITION' for t in PROCLITICS)

    def test_preposition_lam(self):
        assert any(t[1] == 'ل' and t[2] == 'PREPOSITION' for t in PROCLITICS)

    def test_future_particle_seen(self):
        assert any(t[1] == 'س' and t[2] == 'FUTURE_PARTICLE' for t in PROCLITICS)

    def test_standalone_kaf_not_in_proclitics(self):
        """Standalone كَ must NOT be in proclitics (only in multi-proclitic context)."""
        standalone_kaf = [t for t in PROCLITICS if t[1] == 'ك']
        assert not standalone_kaf, \
            f'Standalone كَ found in PROCLITICS: {standalone_kaf}'


class TestEnclitics:
    def test_hum_present(self):
        assert any(e[0] == 'هم' for e in ENCLITICS)

    def test_ha_present(self):
        assert any(e[0] == 'ها' for e in ENCLITICS)

    def test_kum_present(self):
        assert any(e[0] == 'كم' for e in ENCLITICS)

    def test_na_present(self):
        assert any(e[0] == 'نا' for e in ENCLITICS)

    def test_waw_al_jamaa_not_in_enclitics(self):
        """واو الجماعة (وا) must NOT be an enclitic."""
        bare_encs = {e[0] for e in ENCLITICS}
        assert 'وا' not in bare_encs, 'واو الجماعة wrongly in ENCLITICS'

    def test_alef_ithnin_not_in_enclitics(self):
        """ألف الاثنين (ان) must NOT be an enclitic."""
        bare_encs = {e[0] for e in ENCLITICS}
        assert 'ان' not in bare_encs, 'ألف الاثنين wrongly in ENCLITICS'

    def test_nun_niswah_not_in_enclitics(self):
        """نون النسوة (ن) as standalone must NOT be an enclitic."""
        bare_encs = {e[0] for e in ENCLITICS}
        # Single نون النسوة is ambiguous; full form ن should not be standalone enclitic
        # that could be confused with نون النسوة
        assert 'ن' not in bare_encs, 'نون standalone wrongly in ENCLITICS'


class TestInflectionalSuffixes:
    def test_waw_jamaa_blocked(self):
        assert 'وا' in INFLECTIONAL_BARE_SUFFIXES

    def test_waw_nominative_blocked(self):
        assert 'ون' in INFLECTIONAL_BARE_SUFFIXES

    def test_alef_ithnin_blocked(self):
        assert 'ان' in INFLECTIONAL_BARE_SUFFIXES


class TestMinHostConstants:
    def test_conjunction_min_is_3(self):
        assert MIN_HOST_CONSONANTS_CONJUNCTION == 3

    def test_preposition_min_is_2(self):
        assert MIN_HOST_CONSONANTS_PREPOSITION == 2

    def test_future_min_is_3(self):
        assert MIN_HOST_CONSONANTS_FUTURE == 3

    def test_absolute_min_is_2(self):
        assert MIN_HOST_LENGTH_CHARS == 2
