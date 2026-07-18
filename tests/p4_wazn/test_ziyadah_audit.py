#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p4_wazn/test_ziyadah_audit.py — تدقيق الزيادة (Phase 4A)
"""

from __future__ import annotations

import pytest

from pipeline.p4_wazn.ziyadah_audit import audit_ziyadah, ZiyadahAuditResult
from pipeline.p4_wazn.wazn_catalog import get_catalog
from pipeline.p4_wazn.wazn_projection import normalize_for_wazn


def _wazn(wid):
    return next(w for w in get_catalog() if w.wazn_id == wid)


class TestLicensedZiyadahAccept:
    def test_bare_verb_has_no_ziyadah(self):
        r = audit_ziyadah(normalize_for_wazn("ضَرَبَ"), ("ض", "ر", "ب"), _wazn("FA_A_LA"))
        assert r.directive == "ACCEPT"
        assert r.ziyadah_slots == ()

    def test_mafool_mim_and_waw_licensed(self):
        # مَسْرُور (مَفْعُول): م زائدة أمامية + و قبل اللام — كلاهما مرخّص بالموقع.
        r = audit_ziyadah(normalize_for_wazn("مَسْرُور"), ("س", "ر", "ر"), _wazn("MAF3UL"))
        assert r.directive == "ACCEPT"
        assert len(r.ziyadah_slots) == 2

    def test_faail_alif_licensed(self):
        r = audit_ziyadah(normalize_for_wazn("كَاتِب"), ("ك", "ت", "ب"), _wazn("FA3IL"))
        assert r.directive == "ACCEPT"


class TestUnlicensedZiyadahBlocks:
    def test_extra_mim_not_licensed_by_bare_verb(self):
        # فَعَلَ لا موقع زيادة فيه؛ مَضْرَبَ فيه م زائدة ⇒ BLOCK لهذا الوزن.
        r = audit_ziyadah(normalize_for_wazn("مَضْرَبَ"), ("ض", "ر", "ب"), _wazn("FA_A_LA"))
        assert r.directive == "BLOCK"
        assert r.reject_reason is not None

    def test_ziyadah_letter_in_wrong_position_blocks(self):
        # الميم حرف زيادة، لكنها ليست زائدة في موقع اللام من مَفْعُول.
        # سَمْرُوم ليس على مَفْعُول لجذر س ر ر.
        r = audit_ziyadah(normalize_for_wazn("سَرْرَبَ"), ("س", "ر", "ر"), _wazn("MAF3UL"))
        assert r.directive == "BLOCK"


class TestNominalDefer:
    def test_taa_marbuta_defers(self):
        # مَسْرُورَة: التاء المربوطة تأنيث اسمي يحتاج عقدًا مرخّصًا ⇒ DEFER.
        r = audit_ziyadah(normalize_for_wazn("مَسْرُورَة"), ("س", "ر", "ر"), _wazn("MAF3UL"))
        assert r.directive == "DEFER"


class TestResultSerialization:
    def test_to_dict(self):
        r = audit_ziyadah(normalize_for_wazn("ضَرَبَ"), ("ض", "ر", "ب"), _wazn("FA_A_LA"))
        import json
        json.dumps(r.to_dict())
        assert r.to_dict()["wazn_id"] == "FA_A_LA"
