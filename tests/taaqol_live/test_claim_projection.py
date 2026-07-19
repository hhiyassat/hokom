"""
HokomClaimProjection construction and determinism tests.
No Taaqol import required — passes on Python 3.10+.
"""
from __future__ import annotations

import hashlib
from types import SimpleNamespace

from pipeline.taaqol_integration.live.models import HokomClaimProjection
from pipeline.taaqol_integration.live.projection import (
    _deterministic_claim_id,
    project_bundle_to_claim,
)


# ── Deterministic claim ID ────────────────────────────────────────────────────

def test_deterministic_claim_id_reproducible():
    id1 = _deterministic_claim_id('كَتَبَ', 'ROOT', 'ك.ت.ب')
    id2 = _deterministic_claim_id('كَتَبَ', 'ROOT', 'ك.ت.ب')
    assert id1 == id2


def test_deterministic_claim_id_length():
    cid = _deterministic_claim_id('test', 'ROOT', 'value')
    assert len(cid) == 16


def test_deterministic_claim_id_hex():
    cid = _deterministic_claim_id('test', 'ROOT', 'value')
    assert all(c in '0123456789abcdef' for c in cid)


def test_deterministic_claim_id_differs_by_layer():
    id_root = _deterministic_claim_id('كَتَبَ', 'ROOT', 'ك.ت.ب')
    id_pattern = _deterministic_claim_id('كَتَبَ', 'PATTERN', 'ك.ت.ب')
    assert id_root != id_pattern


def test_deterministic_claim_id_differs_by_value():
    id1 = _deterministic_claim_id('كَتَبَ', 'ROOT', 'ك.ت.ب')
    id2 = _deterministic_claim_id('كَتَبَ', 'ROOT', 'ك.ت.م')
    assert id1 != id2


def test_deterministic_claim_id_differs_by_surface():
    id1 = _deterministic_claim_id('كَتَبَ', 'ROOT', 'ك.ت.ب')
    id2 = _deterministic_claim_id('قَرَأَ', 'ROOT', 'ك.ت.ب')
    assert id1 != id2


# ── HokomClaimProjection is frozen ───────────────────────────────────────────

def test_claim_projection_is_frozen():
    import pytest
    proj = HokomClaimProjection(
        claim_id='abc',
        token_id='tok1',
        original_surface='كَتَبَ',
        normalized_surface='كَتَبَ',
        claim_layer='ROOT',
        claim_kind='ROOT_IDENTIFICATION_CLAIM',
        proposed_value='ك.ت.ب',
        upstream_verdict='ACCEPT',
        evidence_rank=4,
        supporting_evidence=('root_catalog:ك.ت.ب',),
        contradictions=(),
        boundaries_crossed=('P5_BOUNDARY',),
        source_engine='HOKOM_ROOT_ENGINE',
        source_owner='HOKOM',
        upstream_trace=(),
        residuals=(),
        provenance='hokom:abc123:taaqol:def456',
    )
    with pytest.raises((AttributeError, TypeError)):
        proj.claim_id = 'changed'  # type: ignore


def test_claim_projection_source_owner_is_hokom():
    proj = HokomClaimProjection(
        claim_id='abc',
        token_id='tok1',
        original_surface='test',
        normalized_surface='test',
        claim_layer='ROOT',
        claim_kind='ROOT_IDENTIFICATION_CLAIM',
        proposed_value='UNKNOWN',
        upstream_verdict='DEFER',
        evidence_rank=0,
        supporting_evidence=(),
        contradictions=(),
        boundaries_crossed=(),
        source_engine='HOKOM',
        source_owner='HOKOM',
        upstream_trace=(),
        residuals=(),
        provenance='hokom:x:taaqol:y',
    )
    assert proj.source_owner == 'HOKOM'


# ── project_bundle_to_claim ───────────────────────────────────────────────────

def _make_bundle(**kwargs):
    defaults = dict(
        claim_id='hokom:test:كَتَبَ',
        token_id='tok123',
        original_surface='كَتَبَ',
        normalized_surface='كَتَبَ',
        domain_directive='ACCEPT',
        source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=('root_catalog:ك.ت.ب', 'wazn:FA3ALA'),
        trace_ids=('trace:1',),
        active_residuals=(),
        part_of_speech='FI3L',
        lexical_class='FI3L',
        root_claim=None,
        wazn_claim=None,
        mabni_status=None,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_project_bundle_to_claim_returns_projection():
    bundle = _make_bundle()
    proj = project_bundle_to_claim(bundle, 'ROOT')
    assert isinstance(proj, HokomClaimProjection)


def test_project_bundle_to_claim_layer_correct():
    bundle = _make_bundle()
    proj = project_bundle_to_claim(bundle, 'WORD_CLASS')
    assert proj.claim_layer == 'WORD_CLASS'


def test_project_bundle_to_claim_source_owner_hokom():
    bundle = _make_bundle()
    proj = project_bundle_to_claim(bundle, 'ROOT')
    assert proj.source_owner == 'HOKOM'


def test_project_bundle_to_claim_upstream_verdict():
    bundle = _make_bundle(domain_directive='ACCEPT')
    proj = project_bundle_to_claim(bundle, 'ROOT')
    assert proj.upstream_verdict == 'ACCEPT'


def test_project_bundle_to_claim_surface():
    bundle = _make_bundle(original_surface='ذَهَبَ')
    proj = project_bundle_to_claim(bundle, 'ROOT')
    assert proj.original_surface == 'ذَهَبَ'


def test_project_bundle_to_claim_deterministic():
    bundle = _make_bundle()
    proj1 = project_bundle_to_claim(bundle, 'ROOT', hokom_commit='abc', taaqol_commit='def')
    proj2 = project_bundle_to_claim(bundle, 'ROOT', hokom_commit='abc', taaqol_commit='def')
    assert proj1.claim_id == proj2.claim_id


def test_project_bundle_provenance_format():
    bundle = _make_bundle()
    proj = project_bundle_to_claim(bundle, 'ROOT', hokom_commit='abc123', taaqol_commit='def456')
    assert proj.provenance == 'hokom:abc123:taaqol:def456'


def test_project_bundle_evidence_ids_preserved():
    bundle = _make_bundle(evidence_ids=('ev1', 'ev2'))
    proj = project_bundle_to_claim(bundle, 'ROOT')
    assert 'ev1' in proj.supporting_evidence
    assert 'ev2' in proj.supporting_evidence


def test_project_bundle_word_class_layer():
    bundle = _make_bundle(part_of_speech='ISM', domain_directive='ACCEPT')
    proj = project_bundle_to_claim(bundle, 'WORD_CLASS')
    assert proj.claim_layer == 'WORD_CLASS'
    assert proj.claim_kind == 'WORD_CLASS_CLAIM'
    assert proj.proposed_value == 'ISM'


def test_project_bundle_final_token_layer():
    bundle = _make_bundle(domain_directive='ACCEPT')
    proj = project_bundle_to_claim(bundle, 'FINAL_TOKEN')
    assert proj.claim_layer == 'FINAL_TOKEN'
    assert proj.claim_kind == 'FINAL_TOKEN_CLAIM'
