"""
Clitic-only constructions (host=None) must produce fail-closed DEFERRED,
never LICENSED.

HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME
"""
from __future__ import annotations
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
from pipeline.taaqol_integration.live.models import HokomTaaqolDecision
from pipeline.p0_segmentation.models import SegmentationRequest


def _seg(surface: str):
    from pipeline.p0_segmentation import segment_token
    req = SegmentationRequest(
        request_id=f'test:{surface}',
        original_surface=surface,
        normalized_surface=surface,
    )
    return segment_token(req)


def _clitic_bundle(surface: str):
    sb = _seg(surface)
    return SimpleNamespace(
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
        morphology_block_reason='SEGMENTATION_NO_LEXICAL_HOST' if sb.clitic_only else None,
        domain_directive='ACCEPT',
        source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=(),
        trace_ids=(),
        active_residuals=(),
        part_of_speech=None, lexical_class=None,
        root_claim=None, wazn_claim=None,
        masdar_claim=None, mushtaq_claims=(),
        inflection_claim=None, mabni_status=None,
    )


# ── بِكُمْ is the canonical clitic-only case per Hokom segmenter ──────────────

def test_bikum_is_clitic_only():
    """Verify that بِكُمْ is clitic-only per the canonical segmenter."""
    bundle = _clitic_bundle('بِكُمْ')
    assert bundle.segment_host is None, "بِكُمْ must have host=None (clitic-only)"
    assert bundle.segment_clitic_only is True


def test_clitic_only_not_licensed():
    """Clitic-only tokens must never produce LICENSED verdict."""
    bundle = _clitic_bundle('بِكُمْ')
    assert bundle.morphology_blocked is True  # pre-condition

    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    assert isinstance(result, HokomTaaqolDecision)
    assert result.effective_verdict != 'LICENSED', (
        f"بِكُمْ: clitic-only must not yield LICENSED, got {result.effective_verdict!r}"
    )
    assert result.taaqol_verdict != 'LICENSED'


def test_clitic_only_center_scope_is_none():
    """No morphological center for clitic-only tokens."""
    bundle = _clitic_bundle('بِكُمْ')
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    center = getattr(result, 'taaqol_center_scope', 'NOT_SET')
    assert center is None, (
        f"Clitic-only center_scope must be None, got {center!r}"
    )


def test_clitic_only_original_not_used_as_center():
    """Full token must not appear as center_scope for clitic-only."""
    bundle = _clitic_bundle('بِكُمْ')
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    center = getattr(result, 'taaqol_center_scope', None)
    assert center != 'بِكُمْ', (
        "Full token 'بِكُمْ' must never be used as Center.scope"
    )


def test_clitic_only_fail_closed_flag():
    """fail_closed must be True even for clitic-only path."""
    bundle = _clitic_bundle('بِكُمْ')
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    assert result.fail_closed is True


def test_clitic_only_reason_codes_non_empty():
    """reason_codes must document the clitic-only block."""
    bundle = _clitic_bundle('بِكُمْ')
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    # On Python 3.10: reason codes from import failure; on 3.11+: from clitic gate
    assert len(result.reason_codes) > 0, "reason_codes must be non-empty"


# ── A manually-constructed clitic-only bundle (host explicitly None) ──────────

def test_explicit_none_host_not_licensed():
    """Bundle with explicit segment_host=None must not yield LICENSED."""
    bundle = SimpleNamespace(
        claim_id='hokom:test:explicit_none',
        token_id='tok_none',
        original_surface='بِكُمْ',
        normalized_surface='بِكُمْ',
        segment_bundle=None,
        segment_host=None,
        segment_proclitics=('بِ',),
        segment_definite_article=None,
        segment_enclitics=('كُمْ',),
        segment_clitic_only=True,
        segment_verdict='SEGMENTATION_ACCEPTED',
        morphology_surface=None,
        morphology_blocked=True,
        morphology_block_reason='SEGMENTATION_NO_LEXICAL_HOST',
        domain_directive='ACCEPT',
        source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=(), trace_ids=(), active_residuals=(),
        part_of_speech=None, lexical_class=None,
        root_claim=None, wazn_claim=None, masdar_claim=None,
        mushtaq_claims=(), inflection_claim=None, mabni_status=None,
    )
    with patch.dict(__import__('sys').modules, {'taaqqul_slot_geometry': None}):
        result = evaluate_hokom_claim_bundle(bundle)
    assert result.effective_verdict != 'LICENSED'
    assert getattr(result, 'taaqol_center_scope', None) is None
