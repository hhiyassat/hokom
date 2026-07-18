#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_wazn_models.py — النموذج القانوني وقابلية التسلسل (Phase 4A)
"""

from __future__ import annotations

import json

import pytest

from pipeline.p4_wazn.models import (
    WaznDirective, WaznStageState, RootSlot, AlignmentKind,
    WaznSlotAlignment, WaznCandidate, WaznProjection,
    WaznProjectionContractError, PROJECTION_VERSION,
)


class TestEnums:
    def test_directive_values(self):
        assert {d.value for d in WaznDirective} == {"ACCEPT", "DEFER", "BLOCK"}

    def test_stage_state_values(self):
        assert {s.value for s in WaznStageState} == {
            "COMPLETED", "DEFERRED", "BLOCKED", "NOT_OPENED"}

    def test_root_slots_include_explicit_fourth(self):
        # الحرف الرابع صريح (ل2)، لا «لام ثالثة» غامضة.
        assert RootSlot.FA.value == "ف"
        assert RootSlot.AIN.value == "ع"
        assert RootSlot.LAM.value == "ل"
        assert RootSlot.FOURTH.value == "ل2"

    def test_alignment_kinds(self):
        vals = {a.value for a in AlignmentKind}
        assert "root_radical" in vals
        assert "ziyadah" in vals
        assert "inflectional" in vals
        assert "deleted_root_slot" in vals
        assert "unresolved" in vals


class TestContractError:
    def test_is_runtime_error(self):
        assert issubclass(WaznProjectionContractError, RuntimeError)


class TestSlotAlignmentSerialization:
    def test_to_dict_roundtrips_json(self):
        a = WaznSlotAlignment(
            surface_segment="ضَ", normalized_segment="ضَ", surface_index=0,
            root_slot=RootSlot.FA, root_identity="ض",
            alignment_kind=AlignmentKind.ROOT_RADICAL, operation_id=None,
            evidence_ids=("ev:1",), trace_ids=("tr:1",))
        d = a.to_dict()
        assert d["root_slot"] == "ف"
        assert d["alignment_kind"] == "root_radical"
        json.dumps(d)  # must not raise

    def test_none_root_slot_serializes(self):
        a = WaznSlotAlignment(
            surface_segment="ا", normalized_segment="ا", surface_index=1,
            root_slot=None, root_identity=None,
            alignment_kind=AlignmentKind.ZIYADAH, operation_id=None)
        assert a.to_dict()["root_slot"] is None


class TestProjectionSerialization:
    def _projection(self):
        sel = WaznCandidate(
            wazn_id="FA_A_LA", wazn_pattern="فَعَلَ", wazn_family="triliteral_bare_verb",
            alignment=(), root_slots_complete=True, confidence_rank=10,
            evidence_ids=("wazn:FA_A_LA:aligned",))
        return WaznProjection(
            input_surface="ضَرَبَ", analyzed_host="ضَرَبَ", normalized_host="ضَرَبَ",
            canonical_root=("ض", "ر", "ب"),
            directive=WaznDirective.ACCEPT, stage_state=WaznStageState.COMPLETED,
            candidate_awzan=(sel,), selected_wazn=sel,
            evidence_ids=("ev:root",), trace_ids=("tr:root",), residual_codes=())

    def test_projection_is_json_serializable(self):
        d = self._projection().to_dict()
        s = json.dumps(d, ensure_ascii=False)
        again = json.loads(s)
        assert again["directive"] == "ACCEPT"
        assert again["stage_state"] == "COMPLETED"
        assert again["canonical_root"] == ["ض", "ر", "ب"]
        assert again["selected_wazn"]["wazn_pattern"] == "فَعَلَ"
        assert again["projection_version"] == PROJECTION_VERSION

    def test_none_selected_serializes(self):
        p = WaznProjection(
            input_surface="مِنْ", analyzed_host="مِنْ", normalized_host="مِنْ",
            canonical_root=None,
            directive=WaznDirective.BLOCK, stage_state=WaznStageState.NOT_OPENED)
        d = p.to_dict()
        assert d["selected_wazn"] is None
        assert d["canonical_root"] is None
        json.dumps(d)
