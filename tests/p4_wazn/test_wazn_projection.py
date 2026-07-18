#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_wazn_projection.py — أوركسترا الوزن (Phase 4A)

يغطّي متطلبات الوحدة (§16) من فتح المرحلة، الرتابة، العقود، والحفظ.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p4_wazn import project_wazn
from pipeline.p4_wazn.models import (
    WaznDirective, WaznStageState, AlignmentKind, WaznProjectionContractError,
)
from pipeline.p4_wazn.wazn_catalog import WaznDefinition, TemplateCell


def rc(surface, host, directive, root, *, evidence=("ev:root",),
       trace=("tr:root",), residual=()):
    return RootCandidate(
        surface=surface, host_surface=host, directive=directive,
        canonical_root=root, root_profile={"weakness": "NONE"},
        evidence_ids=evidence, trace_ids=trace, residual_codes=residual,
        source_projection="RootProjection")


# ── §16.1 / §16.2 — DEFER/BLOCK لا يفتحان alignment ──────────────────────────

class TestMonotonicityGate:
    def test_defer_does_not_run_alignment(self):
        with patch("pipeline.p4_wazn.wazn_projection.align_wazn") as spy:
            p = project_wazn(rc("قَالَ", "قَالَ", "DEFER", None))
        spy.assert_not_called()
        assert p.directive == WaznDirective.DEFER
        assert p.stage_state == WaznStageState.NOT_OPENED
        assert p.selected_wazn is None
        assert p.candidate_awzan == ()
        assert "defer:wazn:root_candidate_not_resolved" in p.residual_codes

    def test_block_does_not_run_alignment(self):
        with patch("pipeline.p4_wazn.wazn_projection.align_wazn") as spy:
            p = project_wazn(rc("مِنْ", "مِنْ", "BLOCK", None))
        spy.assert_not_called()
        assert p.directive == WaznDirective.BLOCK
        assert p.stage_state == WaznStageState.NOT_OPENED
        assert "block:wazn:root_candidate_blocked" in p.residual_codes

    def test_unknown_directive_raises(self):
        with pytest.raises(WaznProjectionContractError):
            project_wazn(rc("x", "x", "MAYBE", None))


# ── §16.3 — ACCEPT بلا جذر ⇒ خطأ عقد ────────────────────────────────────────

class TestAcceptContract:
    def test_accept_without_root_raises(self):
        with pytest.raises(WaznProjectionContractError):
            project_wazn(rc("ضَرَبَ", "ضَرَبَ", "ACCEPT", None))

    def test_accept_with_alif_radical_raises(self):
        # §16.13 — ا لا تُقبل هوية جذرية.
        with pytest.raises(WaznProjectionContractError):
            project_wazn(rc("قَالَ", "قَالَ", "ACCEPT", ("ق", "ا", "ل")))

    def test_accept_with_alif_maqsura_radical_raises(self):
        with pytest.raises(WaznProjectionContractError):
            project_wazn(rc("رَمَى", "رَمَى", "ACCEPT", ("ر", "م", "ى")))

    def test_unsupported_arity_raises(self):
        with pytest.raises(WaznProjectionContractError):
            project_wazn(rc("x", "xx", "ACCEPT", ("ب", "ب")))


# ── §16.11 — وزن واحد مرخّص ⇒ ACCEPT ────────────────────────────────────────

class TestSinglePatternAccept:
    def test_darab_accepts_faala(self):
        p = project_wazn(rc("ضَرَبَ", "ضَرَبَ", "ACCEPT", ("ض", "ر", "ب")))
        assert p.directive == WaznDirective.ACCEPT
        assert p.stage_state == WaznStageState.COMPLETED
        assert p.selected_wazn.wazn_pattern == "فَعَلَ"
        assert p.selected_wazn in p.candidate_awzan

    def test_hamza_identity_preserved_in_projection(self):
        # §16.5
        p = project_wazn(rc("قَرَأَ", "قَرَأَ", "ACCEPT", ("ق", "ر", "ء")))
        assert p.directive == WaznDirective.ACCEPT
        assert p.canonical_root == ("ق", "ر", "ء")
        lam = [a for a in p.root_slot_alignment if a.root_identity == "ء"]
        assert lam and lam[0].root_identity == "ء"

    def test_shadda_no_false_radical(self):
        # §16.6/§16.7 — canonical_root غير مُعدَّل، والتضعيف زيادة لا جذر.
        p = project_wazn(rc("عَلَّمَ", "عَلَّمَ", "ACCEPT", ("ع", "ل", "م")))
        assert p.canonical_root == ("ع", "ل", "م")
        assert p.selected_wazn.wazn_pattern == "فَعَّل"
        root_ids = tuple(a.root_identity for a in p.root_slot_alignment)
        assert root_ids == ("ع", "ل", "م")

    def test_mudaaf_duplication_by_alignment_not_root_mutation(self):
        p = project_wazn(rc("مَدَّ", "مَدَّ", "ACCEPT", ("م", "د", "د")))
        assert p.canonical_root == ("م", "د", "د")
        assert p.selected_wazn.wazn_pattern == "فَعَلَ"
        assert p.weak_operations  # عملية إدغام مسجّلة


# ── §16.10 — تعدد الأوزان ⇒ DEFER ───────────────────────────────────────────

class TestMultiplePatternsDefer:
    def _twin_catalog(self):
        tmpl = (TemplateCell("FA", "FATHA"), TemplateCell("AIN", "FATHA"),
                TemplateCell("LAM", "FINAL"))
        def mk(wid, rank):
            return WaznDefinition(
                wazn_id=wid, pattern="فَعَلَ", root_arity=3, family="twin",
                applicable_surface_classes=("verb",), root_slots=("FA", "AIN", "LAM"),
                licensed_ziyadah_slots=(), licensed_shadda_behavior=(),
                licensed_weak_operations=(), evidence_rank=rank, source="test",
                template=tmpl)
        return (mk("TWIN_A", 10), mk("TWIN_B", 11))

    def test_two_equal_patterns_defer(self):
        p = project_wazn(rc("ضَرَبَ", "ضَرَبَ", "ACCEPT", ("ض", "ر", "ب")),
                         catalog=self._twin_catalog())
        assert p.directive == WaznDirective.DEFER
        assert p.selected_wazn is None
        assert len(p.candidate_awzan) == 2
        assert "defer:wazn:multiple_licensed_patterns" in p.residual_codes


# ── §16.12 — غياب حرف جذري ⇒ BLOCK ──────────────────────────────────────────

class TestMissingRootSlotBlocks:
    def test_missing_final_radical_blocks(self):
        p = project_wazn(rc("ضَرَ", "ضَرَ", "ACCEPT", ("ض", "ر", "ب")))
        assert p.directive == WaznDirective.BLOCK
        assert p.stage_state == WaznStageState.BLOCKED
        assert "block:wazn:no_licensed_pattern" in p.residual_codes


# ── §16.14/§16.15/§16.16 — استبعاد أداة/ضمير/لاحقة تصريفية من الوزن ──────────

class TestExclusions:
    def test_analyzed_host_used_not_full_surface(self):
        # أداة التعريف مستبعدة: نعمل على analyzed_host (أَطْفَالُ) لا الْأَطْفَالُ.
        p = project_wazn(rc("الْأَطْفَالُ", "أَطْفَالُ", "ACCEPT", ("ط", "ف", "ل")))
        assert p.analyzed_host == "أَطْفَالُ"
        assert "ال" not in p.analyzed_host[:2] or p.analyzed_host.startswith("أ")
        assert p.input_surface == "الْأَطْفَالُ"

    def test_attached_pronoun_excluded(self):
        p = project_wazn(rc("تَرَكَتْهُمْ", "تَرَكَتْ", "ACCEPT", ("ت", "ر", "ك")))
        assert p.analyzed_host == "تَرَكَتْ"
        assert "هم" not in p.analyzed_host

    def test_inflectional_suffix_separated_from_derivational_wazn(self):
        p = project_wazn(rc("تَرَكَتْهُمْ", "تَرَكَتْ", "ACCEPT", ("ت", "ر", "ك")))
        assert p.directive == WaznDirective.ACCEPT
        assert p.selected_wazn.wazn_pattern == "فَعَلَ"
        # التاء التأنيث الساكنة لاحقة تصريفية، لا جزء من الوزن الاشتقاقي.
        assert any(s.strip("ْ") == "ت" or "ت" in s for s in p.inflectional_suffixes)
        root_ids = tuple(a.root_identity for a in p.root_slot_alignment)
        assert root_ids == ("ت", "ر", "ك")


# ── §16.17/§16.18/§16.19 — التسلسل والحفظ ───────────────────────────────────

class TestSerializationAndPreservation:
    def test_projection_json_serializable(self):
        p = project_wazn(rc("ضَرَبَ", "ضَرَبَ", "ACCEPT", ("ض", "ر", "ب")))
        json.dumps(p.to_dict(), ensure_ascii=False)

    def test_evidence_preserved(self):
        p = project_wazn(rc("ضَرَبَ", "ضَرَبَ", "ACCEPT", ("ض", "ر", "ب"),
                            evidence=("ev:root:A", "ev:root:B")))
        assert "ev:root:A" in p.evidence_ids and "ev:root:B" in p.evidence_ids

    def test_trace_preserved(self):
        p = project_wazn(rc("ضَرَبَ", "ضَرَبَ", "ACCEPT", ("ض", "ر", "ب"),
                            trace=("tr:root:X",)))
        assert "tr:root:X" in p.trace_ids

    def test_residuals_preserved_through_defer(self):
        p = project_wazn(rc("قَالَ", "قَالَ", "DEFER", None, residual=("defer:root:hollow",)))
        assert "defer:root:hollow" in p.residual_codes
