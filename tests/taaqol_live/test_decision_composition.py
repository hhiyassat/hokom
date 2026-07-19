"""
All 7 (+ extras) monotonic composition cases.
No Taaqol import required — passes on Python 3.10+.
"""
from __future__ import annotations

from pipeline.taaqol_integration.live.decision_composition import compose_effective_verdict


# ── Case 1: Upstream BLOCKED → always BLOCKED ─────────────────────────────────

def test_upstream_blocked_stays_blocked():
    assert compose_effective_verdict('BLOCKED', 'LICENSED') == 'BLOCKED'


def test_upstream_block_stays_blocked():
    assert compose_effective_verdict('BLOCK', 'LICENSED') == 'BLOCKED'


def test_upstream_blocked_stays_blocked_even_if_taaqol_licensed():
    assert compose_effective_verdict('BLOCKED', 'LICENSED') == 'BLOCKED'


def test_upstream_blocked_stays_blocked_if_taaqol_deferred():
    assert compose_effective_verdict('BLOCKED', 'DEFERRED') == 'BLOCKED'


def test_upstream_blocked_stays_blocked_if_taaqol_blocked():
    assert compose_effective_verdict('BLOCKED', 'BLOCKED') == 'BLOCKED'


def test_upstream_blocked_stays_blocked_if_taaqol_residual():
    assert compose_effective_verdict('BLOCKED', 'RESIDUAL') == 'BLOCKED'


# ── Case 2-3: Upstream DEFERRED ───────────────────────────────────────────────

def test_upstream_deferred_stays_deferred_if_taaqol_deferred():
    assert compose_effective_verdict('DEFERRED', 'DEFERRED') == 'DEFERRED'


def test_upstream_deferred_becomes_blocked_if_taaqol_blocked():
    assert compose_effective_verdict('DEFERRED', 'BLOCKED') == 'BLOCKED'


def test_upstream_deferred_cannot_become_licensed():
    result = compose_effective_verdict('DEFERRED', 'LICENSED')
    assert result != 'LICENSED', \
        f"Taaqol must not upgrade DEFERRED to LICENSED, got {result!r}"


def test_upstream_deferred_stays_deferred_if_taaqol_licensed():
    assert compose_effective_verdict('DEFERRED', 'LICENSED') == 'DEFERRED'


def test_upstream_deferred_cannot_become_residual():
    # DEFERRED + RESIDUAL → DEFERRED (residual cannot upgrade deferred)
    result = compose_effective_verdict('DEFERRED', 'RESIDUAL')
    assert result == 'DEFERRED'


def test_upstream_defer_alias():
    # 'DEFER' is alias for 'DEFERRED'
    assert compose_effective_verdict('DEFER', 'LICENSED') == 'DEFERRED'


# ── Cases 4-5: Upstream RESIDUAL ─────────────────────────────────────────────

def test_upstream_residual_stays_residual():
    assert compose_effective_verdict('RESIDUAL', 'RESIDUAL') == 'RESIDUAL'


def test_upstream_residual_becomes_blocked_if_taaqol_blocked():
    assert compose_effective_verdict('RESIDUAL', 'BLOCKED') == 'BLOCKED'


def test_upstream_residual_cannot_become_licensed():
    result = compose_effective_verdict('RESIDUAL', 'LICENSED')
    assert result != 'LICENSED', \
        f"Taaqol must not upgrade RESIDUAL to LICENSED, got {result!r}"


def test_upstream_residual_stays_residual_if_taaqol_deferred():
    assert compose_effective_verdict('RESIDUAL', 'DEFERRED') == 'RESIDUAL'


# ── Case 6: Upstream ACCEPTED → Taaqol decides ───────────────────────────────

def test_upstream_accepted_follows_taaqol_licensed():
    assert compose_effective_verdict('ACCEPTED', 'LICENSED') == 'LICENSED'


def test_upstream_accepted_follows_taaqol_deferred():
    assert compose_effective_verdict('ACCEPTED', 'DEFERRED') == 'DEFERRED'


def test_upstream_accepted_follows_taaqol_blocked():
    assert compose_effective_verdict('ACCEPTED', 'BLOCKED') == 'BLOCKED'


def test_upstream_accepted_follows_taaqol_residual():
    assert compose_effective_verdict('ACCEPTED', 'RESIDUAL') == 'RESIDUAL'


def test_upstream_accept_alias():
    # 'ACCEPT' is alias for 'ACCEPTED'
    assert compose_effective_verdict('ACCEPT', 'LICENSED') == 'LICENSED'


def test_upstream_licensed_follows_taaqol():
    assert compose_effective_verdict('LICENSED', 'LICENSED') == 'LICENSED'
    assert compose_effective_verdict('LICENSED', 'DEFERRED') == 'DEFERRED'
    assert compose_effective_verdict('LICENSED', 'BLOCKED') == 'BLOCKED'


# ── Case 7: Unknown / NOT_APPLICABLE upstream ─────────────────────────────────

def test_unknown_upstream_defaults_to_deferred():
    result = compose_effective_verdict('UNKNOWN_STATE', 'LICENSED')
    assert result == 'DEFERRED'


def test_not_applicable_upstream_defaults_to_deferred():
    result = compose_effective_verdict('NOT_APPLICABLE', 'LICENSED')
    assert result == 'DEFERRED'


def test_not_applicable_blocked_by_taaqol():
    result = compose_effective_verdict('NOT_APPLICABLE', 'BLOCKED')
    assert result == 'BLOCKED'


# ── REJECTED and FORBIDDEN_LEAP map to BLOCKED ───────────────────────────────

def test_rejected_taaqol_maps_to_blocked():
    result = compose_effective_verdict('ACCEPTED', 'REJECTED')
    assert result == 'BLOCKED'


def test_forbidden_leap_taaqol_maps_to_blocked():
    result = compose_effective_verdict('ACCEPTED', 'FORBIDDEN_LEAP')
    assert result == 'BLOCKED'


# ── Determinism ───────────────────────────────────────────────────────────────

def test_composition_is_deterministic():
    """Same inputs always produce same output."""
    for up, tq in [
        ('ACCEPTED', 'LICENSED'),
        ('BLOCKED', 'LICENSED'),
        ('DEFERRED', 'BLOCKED'),
        ('RESIDUAL', 'RESIDUAL'),
    ]:
        r1 = compose_effective_verdict(up, tq)
        r2 = compose_effective_verdict(up, tq)
        assert r1 == r2, f"Non-deterministic: {up!r} + {tq!r} → {r1!r} then {r2!r}"
