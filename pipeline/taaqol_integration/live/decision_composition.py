"""
Monotonic verdict composition for Hokom-Taaqol live integration.

HOKOM-TAAQOL-LIVE-INTEGRATION-01

Constitutional rule: upstream Hokom verdicts CANNOT be upgraded by Taaqol.
  - Hokom BLOCKED  → always BLOCKED (Taaqol cannot un-block)
  - Hokom DEFERRED → BLOCKED or DEFERRED (Taaqol can block further, cannot license)
  - Hokom RESIDUAL → BLOCKED or RESIDUAL (same monotonic rule)
  - Hokom ACCEPTED/LICENSED → Taaqol decides (LICENSED / DEFERRED / BLOCKED / RESIDUAL)

This module is pure Python (no Taaqol imports). Passes on Python 3.10+.
"""
from __future__ import annotations

# Seven canonical cases (mandate §4)
_UPSTREAM_BLOCKED_STATES  = frozenset({'BLOCKED', 'BLOCK'})
_UPSTREAM_DEFERRED_STATES = frozenset({'DEFERRED', 'DEFER'})
_UPSTREAM_RESIDUAL_STATES = frozenset({'RESIDUAL'})
_UPSTREAM_ACCEPTED_STATES = frozenset({'ACCEPTED', 'LICENSED', 'ACCEPT', 'COMPLETE'})
_TAAQOL_BLOCKED_CODES     = frozenset({'BLOCKED', 'BLOCK', 'REJECTED', 'FORBIDDEN_LEAP'})


def compose_effective_verdict(upstream_verdict: str, taaqol_verdict: str) -> str:
    """
    Monotonic composition: upstream BLOCK/DEFER/RESIDUAL cannot be upgraded.

    Cases (in order):
    1. Hokom BLOCKED → BLOCKED always (Taaqol cannot lift a block)
    2. Hokom DEFERRED + Taaqol BLOCKED → BLOCKED
    3. Hokom DEFERRED + any other → DEFERRED (cannot be licensed)
    4. Hokom RESIDUAL + Taaqol BLOCKED → BLOCKED
    5. Hokom RESIDUAL + any other → RESIDUAL (cannot be licensed)
    6. Hokom ACCEPTED + Taaqol verdict → Taaqol verdict
    7. Unknown upstream → follow Taaqol (safe default)

    Returns one of: 'LICENSED' | 'DEFERRED' | 'BLOCKED' | 'RESIDUAL'
    """
    up = (upstream_verdict or 'DEFERRED').upper().strip()
    tq = (taaqol_verdict or 'DEFERRED').upper().strip()

    # Case 1: upstream BLOCKED → always BLOCKED
    if up in _UPSTREAM_BLOCKED_STATES:
        return 'BLOCKED'

    # Cases 2–3: upstream DEFERRED
    if up in _UPSTREAM_DEFERRED_STATES:
        if tq in _TAAQOL_BLOCKED_CODES:
            return 'BLOCKED'
        return 'DEFERRED'

    # Cases 4–5: upstream RESIDUAL
    if up in _UPSTREAM_RESIDUAL_STATES:
        if tq in _TAAQOL_BLOCKED_CODES:
            return 'BLOCKED'
        return 'RESIDUAL'

    # Case 6: Hokom ACCEPTED/LICENSED — Taaqol decides
    if up in _UPSTREAM_ACCEPTED_STATES:
        # Normalise Taaqol verdict to canonical form
        if tq in _TAAQOL_BLOCKED_CODES:
            return 'BLOCKED'
        if tq == 'LICENSED':
            return 'LICENSED'
        if tq == 'RESIDUAL':
            return 'RESIDUAL'
        return 'DEFERRED'

    # Case 7: NOT_APPLICABLE or unknown upstream → safe default is DEFERRED
    if tq in _TAAQOL_BLOCKED_CODES:
        return 'BLOCKED'
    return 'DEFERRED'


__all__ = ['compose_effective_verdict']
