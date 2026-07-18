#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_weak_operations.py — قواعد السلامة الصرفية (Phase 4A)
"""

from __future__ import annotations

import pipeline.p4_wazn.weak_operations as wk


class TestProhibitedRadicalIdentities:
    def test_alif_is_prohibited(self):
        assert wk.is_prohibited_radical("ا")

    def test_alif_maqsura_is_prohibited(self):
        assert wk.is_prohibited_radical("ى")

    def test_carried_hamza_forms_prohibited(self):
        for ch in ("أ", "إ", "ؤ", "ئ", "آ"):
            assert wk.is_prohibited_radical(ch)

    def test_bare_hamza_is_allowed(self):
        # ء المفردة هوية جذرية سليمة — تُحفَظ كما هي.
        assert not wk.is_prohibited_radical("ء")

    def test_sound_consonant_allowed(self):
        for ch in ("ض", "ر", "ب", "ك", "ت"):
            assert not wk.is_prohibited_radical(ch)


class TestHamzaEquivalence:
    def test_bare_hamza_matches_carried(self):
        assert wk.hamza_equivalent("ء", "أ")
        assert wk.hamza_equivalent("أ", "ء")

    def test_non_hamza_not_equivalent(self):
        assert not wk.hamza_equivalent("ء", "ع")

    def test_none_not_equivalent(self):
        assert not wk.hamza_equivalent(None, "ء")


class TestLettersMatch:
    def test_identical_consonant(self):
        assert wk.letters_match("ض", "ض")

    def test_hamza_identity_matches_bare_hamza(self):
        assert wk.letters_match("ء", "ء")

    def test_hamza_identity_matches_surface_carried(self):
        # لو ظهرت أ في السطح، فهي allograph لهوية ء الجذرية.
        assert wk.letters_match("ء", "أ")

    def test_alif_never_matches_as_radical(self):
        # قاعدة السلامة: ا في السطح لا تُقابل هوية جذرية.
        assert not wk.letters_match("ا", "ا")

    def test_alif_maqsura_never_radical(self):
        assert not wk.letters_match("ى", "ى")

    def test_mismatch(self):
        assert not wk.letters_match("د", "ر")


class TestZiyadahLetters:
    def test_saaltumuniha_letters_recognized(self):
        for ch in ("ا", "و", "ي", "ن", "ت", "م", "س", "ل", "ه", "ء"):
            assert wk.is_ziyadah_letter(ch)

    def test_core_consonant_not_ziyadah(self):
        for ch in ("ض", "ر", "ب", "ج", "ط"):
            assert not wk.is_ziyadah_letter(ch)

    def test_taa_marbuta_detection(self):
        assert wk.is_taa_marbuta("ة")
        assert not wk.is_taa_marbuta("ت")


class TestOperationIds:
    def test_operation_ids_are_namespaced(self):
        assert wk.OP_MUDAAF_GEMINATION.startswith("op:")
        assert wk.OP_ZIYADAH_GEMINATION.startswith("op:")
        assert wk.OP_MUDAAF_GEMINATION != wk.OP_ZIYADAH_GEMINATION
