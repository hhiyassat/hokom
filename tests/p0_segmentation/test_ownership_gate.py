#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/p0_segmentation/test_ownership_gate.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ownership gate closure tests for HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01.

These tests verify the structural ownership guarantees:
- No HR2S runtime dependency
- No parallel engines
- Canonical entrypoint
- Host contract (no empty string)
- Clitic-only supported
"""
import pytest
import sys


class TestOwnershipGateStatus:
    def test_gate_is_closed(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.is_closed()

    def test_gate_status_closed(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.status == 'CLOSED'

    def test_no_hr2s_runtime_deps(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.hr2s_runtime_dependencies == 0

    def test_no_parallel_engines(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.parallel_engines == 0

    def test_host_contract_verified(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.host_contract_verified is True

    def test_clitic_only_supported(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.clitic_only_supported is True

    def test_ambiguity_governed(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.ambiguity_governed is True

    def test_lexical_precedence_verified(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.lexical_precedence_verified is True

    def test_inflection_separation_verified(self):
        from pipeline.p0_segmentation.models import SegmentationOwnershipGate
        gate = SegmentationOwnershipGate()
        assert gate.inflection_separation_verified is True


class TestNoHR2SImport:
    def test_engine_no_hr2s(self):
        """Importing and running the engine must NOT import HR2S."""
        # Clear any cached modules
        hr2s_before = {m for m in sys.modules if 'hr2s' in m.lower()}

        from pipeline.p0_segmentation.models import SegmentationRequest
        from pipeline.p0_segmentation.engine import segment_token

        req = SegmentationRequest(
            request_id='gate-test',
            original_surface='بِالْعَدْلِ',
            normalized_surface='بِالْعَدْلِ',
        )
        segment_token(req)

        hr2s_after = {m for m in sys.modules if 'hr2s' in m.lower()}
        new_hr2s = hr2s_after - hr2s_before
        assert not new_hr2s, f'HR2S imported at runtime: {new_hr2s}'

    def test_models_no_hr2s_import(self):
        """Models module must not IMPORT HR2S (runtime dependency)."""
        import sys
        # Importing models should not bring in hr2s as a runtime dep
        before = set(sys.modules.keys())
        import pipeline.p0_segmentation.models  # noqa: F401
        after = set(sys.modules.keys())
        new_mods = after - before
        hr2s_mods = {m for m in new_mods if 'hr2s' in m.lower()}
        assert not hr2s_mods, f'models.py imported HR2S at runtime: {hr2s_mods}'

    def test_engine_no_taaqol_runtime(self):
        """Engine must not import Taaqol bridge at runtime."""
        import sys
        from pipeline.p0_segmentation.models import SegmentationRequest
        from pipeline.p0_segmentation.engine import segment_token
        req = SegmentationRequest(
            request_id='gate-taaqol-test',
            original_surface='بِدَيْنٍ',
            normalized_surface='بِدَيْنٍ',
        )
        before = set(sys.modules.keys())
        segment_token(req)
        after = set(sys.modules.keys())
        new_mods = after - before
        taaqol_mods = {m for m in new_mods if 'taaqol' in m.lower() or 'bridge' in m.lower()}
        assert not taaqol_mods, f'engine imported Taaqol at runtime: {taaqol_mods}'


class TestHostContractInvariant:
    """The host field must never be an empty string (must be None for clitic-only)."""

    @pytest.mark.parametrize("surface", [
        'بِكُمْ', 'بِهِمْ', 'وَكَاتِبٌ', 'فَعَدْلٌ',
        'بِدَيْنٍ', 'وَلْيَكْتُبْ', 'مِنْهُ',
    ])
    def test_host_never_empty_string(self, surface):
        from pipeline.p0_segmentation.models import SegmentationRequest
        from pipeline.p0_segmentation.engine import segment_token
        req = SegmentationRequest(
            request_id=f'contract:{surface}',
            original_surface=surface,
            normalized_surface=surface,
        )
        b = segment_token(req)
        assert b.host != '', f'{surface}: host is empty string, must be None'


class TestCanonicalEntrypoint:
    def test_entrypoint_name(self):
        from pipeline.p0_segmentation.models import SEGMENTATION_CANONICAL_ENTRYPOINT
        assert SEGMENTATION_CANONICAL_ENTRYPOINT == 'segment_token'

    def test_entrypoint_exists(self):
        from pipeline.p0_segmentation import segment_token
        assert callable(segment_token)

    def test_entrypoint_returns_bundle(self):
        from pipeline.p0_segmentation import segment_token, SegmentationRequest, SegmentBundle
        req = SegmentationRequest(
            request_id='ep-test',
            original_surface='بِالْعَدْلِ',
            normalized_surface='بِالْعَدْلِ',
        )
        result = segment_token(req)
        assert isinstance(result, SegmentBundle)


class TestSerializationContract:
    def test_bundle_is_frozen(self):
        from pipeline.p0_segmentation import segment_token, SegmentationRequest
        req = SegmentationRequest(
            request_id='ser-test',
            original_surface='بِدَيْنٍ',
            normalized_surface='بِدَيْنٍ',
        )
        b = segment_token(req)
        with pytest.raises(Exception):
            b.host = 'modified'

    def test_bundle_to_dict(self):
        import dataclasses
        from pipeline.p0_segmentation import segment_token, SegmentationRequest
        req = SegmentationRequest(
            request_id='ser-test',
            original_surface='بِدَيْنٍ',
            normalized_surface='بِدَيْنٍ',
        )
        b = segment_token(req)
        d = dataclasses.asdict(b)
        assert isinstance(d, dict)
        assert 'host' in d
        assert 'proclitics' in d
        assert 'engine_id' in d
        assert d['engine_id'] == 'HOKOM_CLITIC_SEGMENTER'
