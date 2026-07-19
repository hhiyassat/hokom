"""
Determinism tests: same input → same output, every time.
No Taaqol import required — passes on Python 3.10+.
"""
from __future__ import annotations

from types import SimpleNamespace

from pipeline.taaqol_integration.live.projection import _deterministic_claim_id, project_bundle_to_claim
from pipeline.taaqol_integration.live.decision_composition import compose_effective_verdict
from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle


def _make_bundle(**kwargs):
    defaults = dict(
        claim_id='hokom:det_test:كَتَبَ',
        token_id='tok_det',
        original_surface='كَتَبَ',
        normalized_surface='كَتَبَ',
        domain_directive='ACCEPT',
        source_engine='HOKOM_ROOT_ENGINE',
        evidence_ids=('ev1', 'ev2'),
        trace_ids=('t1',),
        active_residuals=(),
        part_of_speech='FI3L',
        lexical_class='FI3L',
        root_claim=None,
        wazn_claim=None,
        masdar_claim=None,
        mushtaq_claims=(),
        inflection_claim=None,
        mabni_status=None,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ── claim_id determinism ──────────────────────────────────────────────────────

def test_claim_id_is_deterministic_across_calls():
    for _ in range(5):
        id1 = _deterministic_claim_id('كَتَبَ', 'ROOT', 'ك.ت.ب')
        id2 = _deterministic_claim_id('كَتَبَ', 'ROOT', 'ك.ت.ب')
        assert id1 == id2


def test_claim_id_no_randomness():
    ids = {_deterministic_claim_id('test', 'ROOT', 'val') for _ in range(10)}
    assert len(ids) == 1, f"claim_id is not deterministic: got {ids}"


# ── projection determinism ────────────────────────────────────────────────────

def test_projection_is_deterministic():
    bundle = _make_bundle()
    p1 = project_bundle_to_claim(bundle, 'ROOT', hokom_commit='abc', taaqol_commit='def')
    p2 = project_bundle_to_claim(bundle, 'ROOT', hokom_commit='abc', taaqol_commit='def')
    assert p1.claim_id == p2.claim_id
    assert p1.proposed_value == p2.proposed_value
    assert p1.upstream_verdict == p2.upstream_verdict


def test_projection_different_layers_produce_different_ids():
    bundle = _make_bundle()
    p_root = project_bundle_to_claim(bundle, 'ROOT')
    p_wc   = project_bundle_to_claim(bundle, 'WORD_CLASS')
    assert p_root.claim_id != p_wc.claim_id


def test_projection_different_surfaces_produce_different_ids():
    b1 = _make_bundle(original_surface='كَتَبَ')
    b2 = _make_bundle(original_surface='ذَهَبَ')
    p1 = project_bundle_to_claim(b1, 'ROOT')
    p2 = project_bundle_to_claim(b2, 'ROOT')
    assert p1.claim_id != p2.claim_id


# ── composition determinism ───────────────────────────────────────────────────

def test_composition_deterministic_accept_licensed():
    for _ in range(5):
        r = compose_effective_verdict('ACCEPT', 'LICENSED')
        assert r == 'LICENSED'


def test_composition_deterministic_blocked():
    for _ in range(5):
        r = compose_effective_verdict('BLOCKED', 'LICENSED')
        assert r == 'BLOCKED'


def test_composition_deterministic_deferred():
    for _ in range(5):
        r = compose_effective_verdict('DEFERRED', 'LICENSED')
        assert r == 'DEFERRED'


# ── bridge determinism ────────────────────────────────────────────────────────

def test_bridge_is_deterministic():
    """Same bundle → same taaqol_verdict across two calls."""
    bundle = _make_bundle()
    r1 = evaluate_hokom_claim_bundle(bundle)
    r2 = evaluate_hokom_claim_bundle(bundle)
    assert r1.taaqol_verdict == r2.taaqol_verdict
    assert r1.effective_verdict == r2.effective_verdict
    assert r1.upstream_verdict == r2.upstream_verdict
    assert r1.fail_closed == r2.fail_closed
    assert r1.strict_mode == r2.strict_mode


def test_bridge_block_directive_deterministic():
    bundle = _make_bundle(domain_directive='BLOCK')
    r1 = evaluate_hokom_claim_bundle(bundle)
    r2 = evaluate_hokom_claim_bundle(bundle)
    assert r1.effective_verdict == r2.effective_verdict
    assert r1.effective_verdict == 'BLOCKED'


def test_bridge_defer_directive_deterministic():
    bundle = _make_bundle(domain_directive='DEFER')
    r1 = evaluate_hokom_claim_bundle(bundle)
    r2 = evaluate_hokom_claim_bundle(bundle)
    assert r1.effective_verdict == r2.effective_verdict
    # DEFER upstream + any Taaqol verdict → never LICENSED
    assert r1.effective_verdict != 'LICENSED'
