#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/wc_audit.py

HOKOM-GOLD-MANIFEST-AMENDMENT-GUARD-PENETRATION-01

Machine-readable word-class classification audit records.

Every token where word_class=None must appear in exactly one of:
  JUSTIFIED    — JAMID_AALAM_BOUNDARY, SEGMENTATION_NO_LEXICAL_HOST, OPERATOR_BOUNDARY
  UNJUSTIFIED  — plain WORD_CLASS_DEFERRED with no known route
  UNADJUDICATED — explicitly reserved; currently 0

This module is purely classificatory — it does not alter pipeline logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pipeline.governance.gold_manifest import (
    WC_JUSTIFIED_REASON_CODES,
    WC_JUSTIFIED_ROUTES,
)

CATEGORY_JUSTIFIED    = 'JUSTIFIED'
CATEGORY_UNJUSTIFIED  = 'UNJUSTIFIED'
CATEGORY_UNADJUDICATED = 'UNADJUDICATED'

_CONSTITUTIONAL_OWNER_DEFAULT = 'HOKOM-GOLD-MANIFEST-AMENDMENT-GUARD-PENETRATION-01'


@dataclass(frozen=True)
class WcClassificationRecord:
    """Machine-readable classification for one wc=None token."""
    token_index: int
    surface: str
    category: str                  # JUSTIFIED | UNJUSTIFIED | UNADJUDICATED
    reason_code: Optional[str]     # e.g. 'JAMID_AALAM_BOUNDARY'
    constitutional_owner: str      # mandate that declared this category


def classify_one(
    token_index: int,
    surface: str,
    result: dict,
    constitutional_owner: str = _CONSTITUTIONAL_OWNER_DEFAULT,
) -> WcClassificationRecord:
    """
    Classify a single wc=None token result into JUSTIFIED / UNJUSTIFIED / UNADJUDICATED.
    """
    skip_reason = result.get('inflection_skipped_reason') or ''
    route       = result.get('_route_v') or ''
    jamid       = result.get('jamid_verdict') or result.get('boundary_type') or ''

    if (
        skip_reason in WC_JUSTIFIED_REASON_CODES
        or jamid == 'JAMID_AALAM_BOUNDARY'
        or route in WC_JUSTIFIED_ROUTES
    ):
        reason = skip_reason or jamid or route or 'JUSTIFIED_ROUTE'
        return WcClassificationRecord(
            token_index=token_index,
            surface=surface,
            category=CATEGORY_JUSTIFIED,
            reason_code=reason,
            constitutional_owner=constitutional_owner,
        )

    return WcClassificationRecord(
        token_index=token_index,
        surface=surface,
        category=CATEGORY_UNJUSTIFIED,
        reason_code=skip_reason or 'WORD_CLASS_DEFERRED',
        constitutional_owner=constitutional_owner,
    )


def build_wc_classification_records(
    results_raw: list[tuple],
    constitutional_owner: str = _CONSTITUTIONAL_OWNER_DEFAULT,
) -> list[WcClassificationRecord]:
    """
    Return one WcClassificationRecord for every token where word_class is None.

    Args:
        results_raw: list of (token_index_or_surface, result_dict) pairs
                     as produced by the demo corpus runner.
        constitutional_owner: mandate ID to stamp on every record.

    Returns:
        Sorted list (by token_index) of WcClassificationRecord.
    """
    records: list[WcClassificationRecord] = []
    for item, result in results_raw:
        if result.get('word_class') is not None:
            continue
        # item may be (token_index, surface) tuple or just a surface string
        if isinstance(item, tuple):
            token_index, surface = item
        elif isinstance(item, int):
            token_index = item
            surface = result.get('surface', '')
        else:
            token_index = -1
            surface = str(item)
        records.append(
            classify_one(token_index, surface, result, constitutional_owner)
        )
    return sorted(records, key=lambda r: r.token_index)


def verify_wc_accounting(records: list[WcClassificationRecord], expected_total: int) -> tuple[bool, str]:
    """
    Verify:
      1. TOTAL = JUSTIFIED + UNJUSTIFIED + UNADJUDICATED
      2. No record appears in more than one category
      3. No record is omitted (len(records) == expected_total)

    Returns (ok, message).
    """
    total = len(records)
    if total != expected_total:
        return (False,
                f'RECORD_COUNT_MISMATCH: got {total}, expected {expected_total}.')

    # Check uniqueness by token_index
    seen_indices: set[int] = set()
    for rec in records:
        if rec.token_index in seen_indices:
            return (False,
                    f'DUPLICATE_RECORD: token_index={rec.token_index} appears more than once.')
        seen_indices.add(rec.token_index)

    counts = {CATEGORY_JUSTIFIED: 0, CATEGORY_UNJUSTIFIED: 0, CATEGORY_UNADJUDICATED: 0}
    for rec in records:
        if rec.category not in counts:
            return (False, f'UNKNOWN_CATEGORY: {rec.category!r} at token {rec.token_index}.')
        counts[rec.category] += 1

    cat_sum = sum(counts.values())
    if cat_sum != total:
        return (False,
                f'CATEGORY_SUM_MISMATCH: {counts} sums to {cat_sum}, total={total}.')

    return (True, f'WC_ACCOUNTING_OK: {counts}')
