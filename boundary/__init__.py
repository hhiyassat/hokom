"""
boundary — PR 3.7-pre: Internal Boundary Layer

Public API:
  assess_boundary(surface: str) -> RootEligibilityDecision

Types:
  BoundaryKind, RootPathDirective, StageState, BoundaryEvidence, RootEligibilityDecision
"""

from boundary.models import (
    BoundaryEvidence,
    BoundaryKind,
    BLOCK_KINDS,
    DEFER_KINDS,
    OPEN_KINDS,
    RootEligibilityDecision,
    RootPathDirective,
    StageState,
)
from boundary.service import assess_boundary

__all__ = [
    "assess_boundary",
    "BoundaryKind",
    "BLOCK_KINDS",
    "DEFER_KINDS",
    "OPEN_KINDS",
    "RootPathDirective",
    "StageState",
    "BoundaryEvidence",
    "RootEligibilityDecision",
]
