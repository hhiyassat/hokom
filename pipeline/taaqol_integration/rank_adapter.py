"""
Rank authority: Hokom never determines native Taaqol rank.
This module enforces the boundary.
"""
from __future__ import annotations

FORBIDDEN_RANK_CLAIMS = frozenset([
    'LICENSED', 'CERTIFIED', 'PROVEN', 'COMPLETE',
    'RANK_1', 'RANK_2', 'RANK_3',
    'CONSTITUTIONAL', 'FINAL',
])


def assert_no_rank_injection(bundle_dict: dict) -> list:
    """
    Scan a serialized bundle for forbidden rank claims.
    Returns list of violations.
    """
    violations = []
    for key, val in bundle_dict.items():
        if isinstance(val, str) and val.upper() in FORBIDDEN_RANK_CLAIMS:
            violations.append(f'forbidden rank claim in {key!r}: {val!r}')
    return violations


def hokom_directive_is_not_rank(domain_directive: str) -> bool:
    """
    Explicit assertion: Hokom domain_directive ACCEPT != Taaqol LICENSED rank.
    Always returns True (this is a boundary assertion, not a computation).
    """
    # Hokom ACCEPT means: domain claim is coherent and complete
    # It does NOT mean: Taaqol has evaluated and licensed this claim
    return True  # the boundary always holds
