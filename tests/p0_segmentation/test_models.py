#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Model contract tests for the Hokom Clitic Segmenter.
HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
import pytest
from pipeline.p0_segmentation.models import (
    SEGMENTATION_ENGINE_ID,
    SEGMENTATION_CANONICAL_OWNER,
    SEGMENTATION_CONTRACT_VERSION,
    SEGMENTATION_CANONICAL_ENTRYPOINT,
    SegmentationVerdict,
    SegmentRole,
    SegmentKind,
    SegmentationRequest,
    Segment,
    SegmentEvidence,
    SegmentBundle,
    SegmentationOwnershipGate,
)


class TestOwnershipConstants:
    def test_engine_id(self):
        assert SEGMENTATION_ENGINE_ID == 'HOKOM_CLITIC_SEGMENTER'

    def test_canonical_owner(self):
        assert SEGMENTATION_CANONICAL_OWNER == 'HOKOM'

    def test_contract_version(self):
        assert SEGMENTATION_CONTRACT_VERSION == '1'

    def test_canonical_entrypoint(self):
        assert SEGMENTATION_CANONICAL_ENTRYPOINT == 'segment_token'


class TestSegmentationVerdictEnum:
    def test_all_verdicts_exist(self):
        assert SegmentationVerdict.SEGMENTATION_ACCEPTED
        assert SegmentationVerdict.SEGMENTATION_DEFERRED
        assert SegmentationVerdict.SEGMENTATION_BLOCKED
        assert SegmentationVerdict.SEGMENTATION_RESIDUAL

    def test_verdict_values(self):
        assert SegmentationVerdict.SEGMENTATION_ACCEPTED.value == 'SEGMENTATION_ACCEPTED'
        assert SegmentationVerdict.SEGMENTATION_DEFERRED.value == 'SEGMENTATION_DEFERRED'


class TestSegmentRoleEnum:
    def test_all_roles_exist(self):
        for role in ['PROCLITIC', 'DEFINITE_ARTICLE', 'HOST', 'ENCLITIC', 'CLITIC_ONLY', 'UNRESOLVED']:
            assert SegmentRole(role)


class TestSegmentKindEnum:
    def test_all_kinds_exist(self):
        expected = [
            'CONJUNCTION', 'PREPOSITION', 'FUTURE_PARTICLE', 'JUSSIVE_LAM',
            'RESUMPTION', 'INTERROGATIVE', 'DEFINITE_ARTICLE', 'ATTACHED_PRONOUN',
            'LEXICAL_HOST', 'VERBAL_HOST', 'NOMINAL_HOST', 'OPERATOR_HOST',
            'PROTECTED_HOST', 'UNRESOLVED',
        ]
        for kind in expected:
            assert SegmentKind(kind)


class TestSegmentationRequest:
    def test_basic_creation(self):
        req = SegmentationRequest(
            request_id='test-01',
            original_surface='بِالْعَدْلِ',
            normalized_surface='بِالْعَدْلِ',
        )
        assert req.request_id == 'test-01'
        assert req.original_surface == 'بِالْعَدْلِ'
        assert req.context_token_id is None
        assert req.upstream_evidence == ()

    def test_frozen(self):
        req = SegmentationRequest(
            request_id='test-01',
            original_surface='test',
            normalized_surface='test',
        )
        with pytest.raises(Exception):
            req.request_id = 'modified'


class TestOwnershipGate:
    def test_gate_defaults(self):
        gate = SegmentationOwnershipGate()
        assert gate.engine_id == SEGMENTATION_ENGINE_ID
        assert gate.canonical_owner == SEGMENTATION_CANONICAL_OWNER
        assert gate.hr2s_runtime_dependencies == 0
        assert gate.parallel_engines == 0
        assert gate.status == 'CLOSED'

    def test_is_closed(self):
        gate = SegmentationOwnershipGate()
        assert gate.is_closed() is True

    def test_to_dict(self):
        gate = SegmentationOwnershipGate()
        d = gate.to_dict()
        assert isinstance(d, dict)
        assert d['engine_id'] == SEGMENTATION_ENGINE_ID
        assert d['hr2s_runtime_dependencies'] == 0
        assert d['status'] == 'CLOSED'

    def test_gate_hr2s_zero(self):
        gate = SegmentationOwnershipGate()
        assert gate.hr2s_runtime_dependencies == 0

    def test_gate_no_parallel_engines(self):
        gate = SegmentationOwnershipGate()
        assert gate.parallel_engines == 0
