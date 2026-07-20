"""
Property tests: Center.scope must NEVER equal original_surface
when segment_host differs from original_surface.

HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME
"""
from __future__ import annotations
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.normalization import strip_diacritics


# Tokens where the segmenter splits off proclitics/enclitics from the host
SPLIT_CASES = [
    'بِدَيْنٍ',
    'بِالْعَدْلِ',
    'وَلْيَكْتُبْ',
    'فَلْيَكْتُبْ',
    'مِنْهُ',
    'لِلشَّهَادَةِ',
    'تَكْتُبُوهُ',
    'أَجَلِهِ',
]


def _seg(surface: str):
    from pipeline.p0_segmentation import segment_token
    req = SegmentationRequest(request_id=f'test:{surface}',
                               original_surface=surface, normalized_surface=surface)
    return segment_token(req)


def _make_bundle(surface: str):
    sb = _seg(surface)
    return SimpleNamespace(
        claim_id=f'hokom:test:{surface}',
        token_id='tok', original_surface=surface, normalized_surface=surface,
        segment_bundle=sb, segment_host=sb.host,
        segment_proclitics=sb.proclitics, segment_definite_article=sb.definite_article,
        segment_enclitics=sb.enclitics, segment_clitic_only=sb.clitic_only,
        segment_verdict=str(sb.verdict), morphology_surface=sb.host,
        morphology_blocked=(sb.host is None), morphology_block_reason=None,
        domain_directive='ACCEPT', source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=(), trace_ids=(), active_residuals=(),
        part_of_speech=None, lexical_class=None, root_claim=None,
        wazn_claim=None, masdar_claim=None, mushtaq_claims=(),
        inflection_claim=None, mabni_status=None,
    )


@pytest.mark.parametrize('surface', SPLIT_CASES)
def test_no_full_token_center_when_host_differs(surface):
    """Center.scope must not equal original_surface when segment_host differs."""
    bundle = _make_bundle(surface)
    if bundle.segment_host is None:
        pytest.skip(f"{surface}: host is None (clitic-only) — tested separately")
    if bundle.segment_host == surface:
        pytest.skip(f"{surface}: host == full token — not a split case")

    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)

    center = getattr(result, 'taaqol_center_scope', None)
    if center is not None:
        assert strip_diacritics(center) != strip_diacritics(surface), (
            f"VIOLATION: {surface}: Center.scope={center!r} equals full token. "
            f"Expected segment host {bundle.segment_host!r}"
        )
        # Must equal segment_host
        assert center == bundle.segment_host, (
            f"{surface}: center_scope={center!r} != segment_host={bundle.segment_host!r}"
        )


@pytest.mark.parametrize('surface', SPLIT_CASES)
def test_center_equals_segment_host(surface):
    """For split tokens, taaqol_center_scope must equal segment_host."""
    bundle = _make_bundle(surface)
    if bundle.segment_host is None or bundle.segment_host == surface:
        pytest.skip(f"{surface}: not a split case")

    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)

    center = getattr(result, 'taaqol_center_scope', None)
    assert center == bundle.segment_host, (
        f"{surface}: center_scope={center!r} must equal segment_host={bundle.segment_host!r}"
    )


def test_unsplit_token_center_equals_host():
    """For unsplit tokens (host == original_surface), center can equal both."""
    from pipeline.p0_segmentation import segment_token
    surface = 'كَاتِبٌ'
    sb = segment_token(SegmentationRequest(
        request_id='t', original_surface=surface, normalized_surface=surface
    ))
    assert sb.host == surface, f"كَاتِبٌ should not split: host={sb.host!r}"

    bundle = _make_bundle(surface)
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)

    center = getattr(result, 'taaqol_center_scope', None)
    if center is not None:
        assert center == surface, (
            f"كَاتِبٌ (unsplit): center={center!r} should equal surface={surface!r}"
        )
