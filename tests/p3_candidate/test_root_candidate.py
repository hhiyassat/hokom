#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p3_candidate/test_root_candidate.py — RootCandidate P3 (R-10)

يغطّي رتابة P3: ACCEPT→ACCEPT، DEFER→DEFER، BLOCK→BLOCK،
لا ترقية/تخفيض، لا استدعاء HR2S، لا قراءة سطح، أخطاء العقد، JSON.
"""

from __future__ import annotations

import ast
import json
import pathlib

import pytest

from pipeline.p2_projection.root_projection import RootProjection
from pipeline.p3_candidate.root_candidate import (
    RootCandidate,
    RootCandidateContractError,
)


def _accept_projection():
    return RootProjection(
        input_surface='ضَرَبَ', analyzed_host='ضَرَبَ',
        directive='ACCEPT', stage_state='OPENED',
        canonical_root=('ض', 'ر', 'ب'),
        radicals=(), root_profile={'weakness': 'NONE'},
        unresolved_positions=(), evidence_ids=('ev:root:FA',),
        trace_ids=('root:msg',), residual_codes=(),
        source_version='1.0',
    )


def _defer_projection():
    return RootProjection(
        input_surface='قَالَ', analyzed_host='قَالَ',
        directive='DEFER', stage_state='DEFERRED',
        canonical_root=None,
        radicals=(), root_profile={}, unresolved_positions=('AYN',),
        evidence_ids=(), trace_ids=(),
        residual_codes=('defer:root:hollow_underlying_radical_unresolved',),
    )


def _block_projection():
    return RootProjection.not_opened(
        input_surface='مِنْ', analyzed_host='مِنْ', directive='BLOCK')


# ══════════════════════════════════════════════════════════════════════════════
# 1. رتابة الاشتقاق
# ══════════════════════════════════════════════════════════════════════════════

class TestMonotonicDerivation:
    def test_accept_projection_to_accept_candidate(self):
        c = RootCandidate.from_projection(_accept_projection())
        assert c.directive == 'ACCEPT'
        assert c.canonical_root == ('ض', 'ر', 'ب')

    def test_defer_projection_to_defer_candidate(self):
        c = RootCandidate.from_projection(_defer_projection())
        assert c.directive == 'DEFER'
        assert c.canonical_root is None

    def test_block_projection_to_block_candidate(self):
        c = RootCandidate.from_projection(_block_projection())
        assert c.directive == 'BLOCK'
        assert c.canonical_root is None

    def test_p3_does_not_promote_defer(self):
        c = RootCandidate.from_projection(_defer_projection())
        assert c.directive != 'ACCEPT'

    def test_p3_does_not_demote_accept(self):
        c = RootCandidate.from_projection(_accept_projection())
        assert c.directive == 'ACCEPT'


# ══════════════════════════════════════════════════════════════════════════════
# 2. حفظ الميتاداتا والمصدر
# ══════════════════════════════════════════════════════════════════════════════

class TestMetadataPreservation:
    def test_host_surface_from_projection(self):
        c = RootCandidate.from_projection(_accept_projection())
        assert c.host_surface == 'ضَرَبَ'

    def test_surface_from_projection_not_reread(self):
        c = RootCandidate.from_projection(_accept_projection())
        assert c.surface == 'ضَرَبَ'

    def test_evidence_trace_preserved(self):
        c = RootCandidate.from_projection(_accept_projection())
        assert c.evidence_ids == ('ev:root:FA',)
        assert c.trace_ids == ('root:msg',)

    def test_residual_preserved(self):
        c = RootCandidate.from_projection(_defer_projection())
        assert c.residual_codes == ('defer:root:hollow_underlying_radical_unresolved',)

    def test_source_projection_constant(self):
        c = RootCandidate.from_projection(_accept_projection())
        assert c.source_projection == 'RootProjection'


# ══════════════════════════════════════════════════════════════════════════════
# 3. أخطاء العقد
# ══════════════════════════════════════════════════════════════════════════════

class TestContractErrors:
    def test_accept_without_root_raises(self):
        bad = RootProjection(
            input_surface='x', analyzed_host='x', directive='ACCEPT',
            stage_state='OPENED', canonical_root=None, radicals=(),
            root_profile={}, unresolved_positions=(), evidence_ids=(),
            trace_ids=(), residual_codes=())
        with pytest.raises(RootCandidateContractError):
            RootCandidate.from_projection(bad)

    def test_accept_with_alef_identity_raises(self):
        bad = RootProjection(
            input_surface='x', analyzed_host='x', directive='ACCEPT',
            stage_state='OPENED', canonical_root=('ق', 'ا', 'ل'), radicals=(),
            root_profile={}, unresolved_positions=(), evidence_ids=(),
            trace_ids=(), residual_codes=())
        with pytest.raises(RootCandidateContractError):
            RootCandidate.from_projection(bad)

    def test_unknown_directive_raises(self):
        bad = RootProjection(
            input_surface='x', analyzed_host='x', directive='WEIRD',
            stage_state='OPENED', canonical_root=None, radicals=(),
            root_profile={}, unresolved_positions=(), evidence_ids=(),
            trace_ids=(), residual_codes=())
        with pytest.raises(RootCandidateContractError):
            RootCandidate.from_projection(bad)

    def test_block_with_root_raises(self):
        bad = RootProjection(
            input_surface='x', analyzed_host='x', directive='BLOCK',
            stage_state='NOT_OPENED', canonical_root=('م', 'ن', 'و'), radicals=(),
            root_profile={}, unresolved_positions=(), evidence_ids=(),
            trace_ids=(), residual_codes=())
        with pytest.raises(RootCandidateContractError):
            RootCandidate.from_projection(bad)


# ══════════════════════════════════════════════════════════════════════════════
# 4. JSON + نظافة الاستيراد (لا HR2S)
# ══════════════════════════════════════════════════════════════════════════════

class TestSerializationAndHygiene:
    def test_json_serializable(self):
        c = RootCandidate.from_projection(_accept_projection())
        rt = json.loads(json.dumps(c.to_dict()))
        assert rt['directive'] == 'ACCEPT'
        assert rt['canonical_root'] == ['ض', 'ر', 'ب']

    def test_no_hr2s_import_in_module(self):
        src = (pathlib.Path(__file__).parents[2] / 'pipeline' / 'p3_candidate'
               / 'root_candidate.py').read_text(encoding='utf-8')
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert (node.module or '').split('.')[0] != 'hr2s', node.module
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name.split('.')[0] != 'hr2s', a.name

    def test_module_has_no_surface_reader(self):
        # P3 لا يقرأ السطح مباشرة — لا استيراد لمطبّع/مقطّع/محرّك
        src = (pathlib.Path(__file__).parents[2] / 'pipeline' / 'p3_candidate'
               / 'root_candidate.py').read_text(encoding='utf-8')
        for banned in ('analyze_surface', 'from normalizer', 'from syllabifier',
                       'MorphologyEngine'):
            assert banned not in src, banned
