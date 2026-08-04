"""
maqayis_uniqueness.py — corpus-wide ID uniqueness validator.

Addendum §B / defect list item 5: "complete corpus-wide ID uniqueness,
including passages, identities, residuals, and traces".

Prior to this module, uniqueness was checked only inside a single test
(test_cp12_all_entity_ids_unique). That test enumerated claims / origin
candidates / residuals / trace events from claim_result + identity_result
but did NOT cover:
  - SourcePassage IDs (from identity_result.passages)
  - RootIdentityCandidate IDs (from identity_result.candidates)
  - cross-category collisions across the full pipeline

This module exposes a public callable `validate_id_uniqueness()` that any
production caller (not only tests) can run over an
(import_result, identity_result, claim_result) triple to obtain a typed
UniquenessReport covering all six ID categories plus a cross-category
scan. Failures surface via structured Duplication records — the callable
never raises for policy failures (fail-open contract; the caller decides
what to do with a non-clean report).
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Tuple


@dataclass(frozen=True)
class Duplication:
    """One duplicated ID with its multiplicity."""

    id_value: str
    count: int


@dataclass(frozen=True)
class CategoryReport:
    """Per-category uniqueness report."""

    category: str
    total_ids: int
    unique_ids: int
    duplications: Tuple[Duplication, ...]

    @property
    def clean(self) -> bool:
        return not self.duplications


@dataclass(frozen=True)
class UniquenessReport:
    """Corpus-wide uniqueness report over all six categories + cross-scan."""

    passages: CategoryReport
    identities: CategoryReport
    claims: CategoryReport
    origins: CategoryReport
    residuals: CategoryReport
    traces: CategoryReport
    cross_category_collisions: Tuple[Duplication, ...]

    @property
    def clean(self) -> bool:
        return (
            self.passages.clean
            and self.identities.clean
            and self.claims.clean
            and self.origins.clean
            and self.residuals.clean
            and self.traces.clean
            and not self.cross_category_collisions
        )

    def all_duplications(self) -> Tuple[Tuple[str, Duplication], ...]:
        """Flatten every per-category duplication for reporting."""
        out = []
        for name, cat in (
            ("passages", self.passages),
            ("identities", self.identities),
            ("claims", self.claims),
            ("origins", self.origins),
            ("residuals", self.residuals),
            ("traces", self.traces),
        ):
            for d in cat.duplications:
                out.append((name, d))
        return tuple(out)


def _report(category: str, ids: list) -> CategoryReport:
    counter = Counter(ids)
    dups = tuple(
        Duplication(id_value=k, count=v)
        for k, v in sorted(counter.items())
        if v > 1
    )
    return CategoryReport(
        category=category,
        total_ids=len(ids),
        unique_ids=len(counter),
        duplications=dups,
    )


def validate_id_uniqueness(
    import_result: Any,
    identity_result: Any,
    claim_result: Any,
) -> UniquenessReport:
    """Scan every ID category emitted by the three pipeline results.

    Returns a typed UniquenessReport. `report.clean` is True iff every
    category is duplicate-free AND no ID appears in more than one
    category.

    Never raises for policy violations. Raises TypeError only for
    genuine input-shape failures.
    """
    if not hasattr(identity_result, "passages") or \
       not hasattr(identity_result, "candidates") or \
       not hasattr(claim_result, "claims") or \
       not hasattr(claim_result, "origin_candidates"):
        raise TypeError(
            "validate_id_uniqueness expects identity_result and claim_result "
            "with the documented Maqayis pipeline shapes"
        )

    passage_ids  = [p.id for p in identity_result.passages]
    identity_ids = [c.id for c in identity_result.candidates]
    claim_ids    = [c.id for c in claim_result.claims]
    origin_ids   = [o.id for o in claim_result.origin_candidates]

    # Residuals are emitted by BOTH pipelines — aggregate.
    residual_ids = (
        [r.id for r in identity_result.residuals]
        + [r.id for r in claim_result.residuals]
    )
    trace_ids = (
        [t.id for t in identity_result.trace_events]
        + [t.id for t in claim_result.trace_events]
    )

    passages   = _report("passages", passage_ids)
    identities = _report("identities", identity_ids)
    claims     = _report("claims", claim_ids)
    origins    = _report("origins", origin_ids)
    residuals  = _report("residuals", residual_ids)
    traces     = _report("traces", trace_ids)

    # Cross-category scan — an ID should never appear in more than one
    # category. This catches ID-generator bugs where two constructors
    # share a namespace.
    all_ids = (passage_ids + identity_ids + claim_ids
                + origin_ids + residual_ids + trace_ids)
    cross_dups = tuple(
        Duplication(id_value=k, count=v)
        for k, v in sorted(Counter(all_ids).items())
        if v > 1
    )
    # Filter cross-category duplications that are already reported within
    # a single category — those are captured per-category.
    per_category_dupset = set()
    for cat in (passages, identities, claims, origins, residuals, traces):
        per_category_dupset.update(d.id_value for d in cat.duplications)
    cross_only = tuple(d for d in cross_dups
                        if d.id_value not in per_category_dupset)

    return UniquenessReport(
        passages=passages,
        identities=identities,
        claims=claims,
        origins=origins,
        residuals=residuals,
        traces=traces,
        cross_category_collisions=cross_only,
    )


__all__ = [
    "Duplication",
    "CategoryReport",
    "UniquenessReport",
    "validate_id_uniqueness",
]
