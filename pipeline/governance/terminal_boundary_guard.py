#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/terminal_boundary_guard.py

HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01

Runtime assertion utilities for terminal boundary immutability.

A record with a terminal boundary must NOT reach:
  - identify_tense
  - extract_all_features
  - verbal word-class reconciliation
  - root analysis
  - contextual mood refinement

These utilities provide:
  is_terminal_boundary(hokom_result)  — True if the result contains a terminal boundary
  assert_terminal_record_cannot_reach_inflection(hokom_result)  — raises if violated
"""
from __future__ import annotations

_TERMINAL_VERDICTS = frozenset({
    'JAMID_AALAM_BOUNDARY',
    'MABNI_BOUNDARY',
    'OPERATOR_BOUNDARY',
})

# Fields that must be None for a terminal-boundary record
_VERBAL_INFLECTION_FIELDS = frozenset({
    'tense_aspect',
    'person',
    'voice',
})


def is_terminal_boundary(hokom_result: dict) -> bool:
    """
    Return True if the hokom() result contains a recognized terminal boundary.

    Checks:
      - boundary_type key (primary surfaced field)
      - jamid_verdict key (JAMID_AALAM_BOUNDARY)
      - mabni_verdict / _route_v keys (MABNI_BOUNDARY, OPERATOR_BOUNDARY)
    """
    for key in ('boundary_type', 'jamid_verdict', 'mabni_verdict', '_route_v'):
        val = hokom_result.get(key)
        if val in _TERMINAL_VERDICTS:
            return True
    return False


def assert_terminal_record_cannot_reach_inflection(
    hokom_result: dict,
    surface: str = '',
) -> None:
    """
    Runtime assertion: if hokom_result has a terminal boundary,
    verbal inflection slots must all be None.

    Raises AssertionError with a traceable message if any verbal slot
    is non-None on a terminal record.

    This is a lightweight post-hoc assertion used in tests and
    optionally in pipeline audit runs.  It does NOT run inside the
    hot path; it is called from governance tests and the diff gate.
    """
    if not is_terminal_boundary(hokom_result):
        return  # Not a terminal record — no assertion needed

    boundary_label = (
        hokom_result.get('boundary_type')
        or hokom_result.get('jamid_verdict')
        or hokom_result.get('mabni_verdict')
        or hokom_result.get('_route_v')
        or 'TERMINAL'
    )

    violations = []
    for slot in _VERBAL_INFLECTION_FIELDS:
        val = hokom_result.get(slot)
        if val is not None:
            violations.append(f"{slot}={val!r}")

    # Also check word_class — a terminal record must not be FI3L
    wc = hokom_result.get('word_class')
    if wc == 'FI3L':
        violations.append(f"word_class={wc!r}")

    if violations:
        tok = f" ({surface!r})" if surface else ""
        raise AssertionError(
            f"TERMINAL_BOUNDARY_REACHED_INFLECTION{tok}: "
            f"boundary={boundary_label!r}, "
            f"violations={violations}. "
            f"The terminal boundary must prevent inflection analysis."
        )
