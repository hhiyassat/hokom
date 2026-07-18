#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_root_surface_alignment.py — مقابلة الجذر بالسطح (Phase 4A)
"""

from __future__ import annotations

import pytest

from pipeline.p4_wazn.alignment import (
    parse_cells, align_wazn, is_ordered_subsequence, residual_letters_are_augment,
)
from pipeline.p4_wazn.models import RootSlot, AlignmentKind
from pipeline.p4_wazn.wazn_catalog import get_catalog
import pipeline.p4_wazn.weak_operations as wk


def _wazn(wid):
    return next(w for w in get_catalog() if w.wazn_id == wid)


def _norm(host):
    from pipeline.p4_wazn.wazn_projection import normalize_for_wazn
    return normalize_for_wazn(host)


def _root_ids(attempt):
    return tuple(a.root_identity for a in attempt.alignments
                 if a.alignment_kind == AlignmentKind.ROOT_RADICAL)


class TestCellParsing:
    def test_shadda_expanded_into_two_cells(self):
        cells = parse_cells(_norm("مَدَّ"))
        assert [c.base for c in cells] == ["م", "د", "د"]
        assert cells[1].vowel == "SUKUN"   # الحرف الأول من المضاعف ساكن

    def test_hamza_normalized_to_bare(self):
        cells = parse_cells(_norm("قَرَأَ"))
        assert [c.base for c in cells] == ["ق", "ر", "ء"]


class TestOrderPreservation:
    def test_root_order_fa_ain_lam(self):
        attempt = align_wazn(("ض", "ر", "ب"), parse_cells(_norm("ضَرَبَ")), _wazn("FA_A_LA"))
        assert attempt.matched
        root_aligns = [a for a in attempt.alignments if a.root_slot is not None]
        assert [a.root_slot for a in root_aligns] == [RootSlot.FA, RootSlot.AIN, RootSlot.LAM]
        assert _root_ids(attempt) == ("ض", "ر", "ب")

    def test_indices_increasing(self):
        attempt = align_wazn(("ك", "ت", "ب"), parse_cells(_norm("كَتَبَ")), _wazn("FA_A_LA"))
        idxs = [a.surface_index for a in attempt.alignments if a.root_slot is not None]
        assert idxs == sorted(idxs)


class TestHamzaAlignment:
    def test_hamza_stays_bare_identity(self):
        attempt = align_wazn(("ق", "ر", "ء"), parse_cells(_norm("قَرَأَ")), _wazn("FA_A_LA"))
        assert attempt.matched
        assert _root_ids(attempt) == ("ق", "ر", "ء")
        # اللام هوية ء لا أ.
        lam = [a for a in attempt.alignments if a.root_slot == RootSlot.LAM][0]
        assert lam.root_identity == "ء"


class TestShaddaHandling:
    def test_mudaaf_both_daal_are_root(self):
        # مَدَّ: الدالان كلاهما جذري (م د د)، لا زيادة كاذبة.
        attempt = align_wazn(("م", "د", "د"), parse_cells(_norm("مَدَّ")), _wazn("FA_A_LA"))
        assert attempt.matched
        assert _root_ids(attempt) == ("م", "د", "د")
        assert wk.OP_MUDAAF_GEMINATION in attempt.weak_operations
        # لا زيادة في المضاعف.
        assert attempt.ziyadah_slots == ()

    def test_form_ii_second_ain_is_ziyadah_not_root(self):
        # عَلَّمَ (فَعَّل): اللام الثانية تضعيف عين الوزن (زيادة)، والجذر يبقى ع ل م.
        attempt = align_wazn(("ع", "ل", "م"), parse_cells(_norm("عَلَّمَ")), _wazn("FA33ALA"))
        assert attempt.matched
        assert _root_ids(attempt) == ("ع", "ل", "م")   # لا ع ل ل م
        ziyadah = [a for a in attempt.alignments if a.alignment_kind == AlignmentKind.ZIYADAH]
        assert len(ziyadah) == 1
        assert wk.OP_ZIYADAH_GEMINATION in attempt.weak_operations

    def test_non_idghaam_wazn_rejects_geminate_root(self):
        # فَعْل (لا يرخّص الإدغام) يجب ألا يطابق مضاعفًا مُدغَمًا.
        attempt = align_wazn(("م", "د", "د"), parse_cells(_norm("مَدَّ")), _wazn("FA3L"))
        assert not attempt.matched


class TestWeakAlifNeverRadical:
    def test_alif_in_faail_is_ziyadah(self):
        # كَاتِب (فَاعِل): الألف زيادة، لا حرف جذري.
        attempt = align_wazn(("ك", "ت", "ب"), parse_cells(_norm("كَاتِب")), _wazn("FA3IL"))
        assert attempt.matched
        assert _root_ids(attempt) == ("ك", "ت", "ب")
        alif_cell = [a for a in attempt.alignments if a.normalized_segment.startswith("ا")]
        assert alif_cell and alif_cell[0].alignment_kind == AlignmentKind.ZIYADAH
        assert alif_cell[0].root_slot is None

    def test_root_with_alif_identity_never_matches(self):
        # جذر يحمل ا لا يجوز أن يحاذى (قاعدة السلامة).
        attempt = align_wazn(("ق", "ا", "ل"), parse_cells(_norm("قَالَ")), _wazn("FA_A_LA"))
        assert not attempt.matched


class TestInflectionalTail:
    def test_trailing_taa_taanith_is_inflectional(self):
        # تَرَكَتْ: تاء التأنيث الساكنة لاحقة تصريفية خارج الوزن.
        attempt = align_wazn(("ت", "ر", "ك"), parse_cells(_norm("تَرَكَتْ")), _wazn("FA_A_LA"))
        assert attempt.matched
        assert attempt.trailing_kind == "inflectional"
        assert _root_ids(attempt) == ("ت", "ر", "ك")
        infl = attempt.inflectional_cells
        assert len(infl) == 1
        assert infl[0].alignment_kind == AlignmentKind.INFLECTIONAL


class TestStructuralHelpers:
    def test_ordered_subsequence_true(self):
        assert is_ordered_subsequence(("ط", "ف", "ل"), parse_cells(_norm("أَطْفَالُ")))

    def test_ordered_subsequence_false_when_missing(self):
        assert not is_ordered_subsequence(("ض", "ر", "ب"), parse_cells(_norm("ضَرَ")))

    def test_residual_letters_are_augment(self):
        # أطفال: الزائد (ء الهمزة، ا) من حروف الزيادة.
        assert residual_letters_are_augment(("ط", "ف", "ل"), parse_cells(_norm("أَطْفَالُ")))
