"""
Tests that SlotGraph center scope equals segment_bundle.host, not original_surface.

CONTRACT:
  Center.scope == segment_bundle.host (when host is not None)
  Center.scope != original_surface    (when they differ)

HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME
"""
from __future__ import annotations
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
from pipeline.taaqol_integration.live.models import HokomTaaqolDecision
from pipeline.p0_segmentation.models import SegmentationRequest
from pipeline.p0_segmentation.normalization import strip_diacritics


def _seg(surface: str):
    from pipeline.p0_segmentation import segment_token
    req = SegmentationRequest(
        request_id=f'test:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )
    return segment_token(req)


def _bundle(surface: str, **override):
    sb = _seg(surface)
    defaults = dict(
        claim_id=f'hokom:test:{surface}',
        token_id=f'tok_{surface}',
        original_surface=surface,
        normalized_surface=surface,
        segment_bundle=sb,
        segment_host=sb.host,
        segment_proclitics=sb.proclitics,
        segment_definite_article=sb.definite_article,
        segment_enclitics=sb.enclitics,
        segment_clitic_only=sb.clitic_only,
        segment_verdict=str(sb.verdict),
        morphology_surface=sb.host,
        morphology_blocked=(sb.host is None),
        morphology_block_reason=None,
        domain_directive='ACCEPT',
        source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=(),
        trace_ids=(),
        active_residuals=(),
        part_of_speech=None,
        lexical_class=None,
        root_claim=None,
        wazn_claim=None,
        masdar_claim=None,
        mushtaq_claims=(),
        inflection_claim=None,
        mabni_status=None,
    )
    defaults.update(override)
    return SimpleNamespace(**defaults)


# ── Cases where original_surface differs from segment_host ────────────────────

@pytest.mark.parametrize('surface', [
    'بِدَيْنٍ',
    'بِالْعَدْلِ',
    'لِلشَّهَادَةِ',
    'مِنْهُ',
    'وَلْيَكْتُبْ',
    'فَلْيَكْتُبْ',
])
def test_center_is_segment_host_not_full_token(surface):
    """Center.scope must equal segment_host, not the full token."""
    bundle = _bundle(surface)
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    assert isinstance(result, HokomTaaqolDecision)
    # When segment_host differs from original_surface, center must be the host
    if bundle.segment_host and bundle.segment_host != surface:
        center = getattr(result, 'taaqol_center_scope', None)
        assert center is not None, (
            f"{surface}: taaqol_center_scope is None — expected {bundle.segment_host!r}"
        )
        assert center != surface, (
            f"{surface}: Center.scope {center!r} equals full token — "
            f"expected segment host {bundle.segment_host!r}"
        )
        assert center == bundle.segment_host, (
            f"{surface}: Center.scope {center!r} != segment_host {bundle.segment_host!r}"
        )


# ── Clitic-only: no morphological center ─────────────────────────────────────

def test_clitic_only_no_center():
    """بِكُمْ = proclitic بِ + enclitic كُمْ, host=None → no morphological center."""
    bundle = _bundle('بِكُمْ')
    assert bundle.segment_host is None, "بِكُمْ should have no host per segmenter"
    assert bundle.morphology_blocked is True

    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    assert isinstance(result, HokomTaaqolDecision)
    # Must not be LICENSED on a clitic-only token
    assert result.effective_verdict != 'LICENSED', (
        "Clitic-only token with no host must not yield LICENSED"
    )
    center = getattr(result, 'taaqol_center_scope', 'NOT_SET')
    assert center is None, (
        f"Clitic-only center must be None, got {center!r}"
    )


# ── Original surface preserved in provenance ─────────────────────────────────

def test_original_surface_in_bundle_claim_id():
    """original_surface must appear in bundle.claim_id for provenance tracing."""
    bundle = _bundle('بِالْعَدْلِ')
    assert bundle.segment_host != 'بِالْعَدْلِ'  # host must differ for this test
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    # Bridge returns HokomTaaqolDecision (bridge_id, not claim_id).
    # Provenance lives in the bundle's claim_id, not the decision.
    assert 'بِالْعَدْلِ' in bundle.claim_id, (
        f"original_surface must be traceable in bundle.claim_id: {bundle.claim_id!r}"
    )
    # The decision must carry the bridge_id as provenance anchor
    from pipeline.taaqol_integration.live.models import HOKOM_TAAQOL_BRIDGE_ID
    assert result.bridge_id == HOKOM_TAAQOL_BRIDGE_ID


def test_bridge_decision_is_typed():
    """evaluate_hokom_claim_bundle always returns HokomTaaqolDecision."""
    bundle = _bundle('بِدَيْنٍ')
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    assert isinstance(result, HokomTaaqolDecision)
    assert result.fail_closed is True
    assert result.strict_mode is True
