#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/slot_ownership_registry.py

HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01

Canonical registry of semantic field ownership, terminal boundaries,
and monotonicity rules.

Each entry records:
  field_or_slot         — canonical field name in hokom() result dict
  canonical_owner       — the pipeline stage that has write authority
  terminal              — True → downstream stages must not overwrite
  allowed_source_states — set of states a field may transition FROM
  allowed_target_states — set of states a field may transition TO
  downstream_refinement_allowed — True only for AMBIGUOUS→FILLED transitions
  constitutional_contract — mandate ID that closed this rule

Pipeline evolution is MONOTONIC:
  UNKNOWN   → FILLED / DEFERRED / AMBIGUOUS        (allowed)
  AMBIGUOUS → FILLED (with evidence)               (allowed)
  DEFERRED  → FILLED (by registered owner only)    (allowed)
  FILLED(A) → FILLED(A)                            (idempotent — allowed)
  FILLED(A) → FILLED(B)                            (FORBIDDEN)
  TERMINAL_BOUNDARY → any further write            (FORBIDDEN)
  NOT_APPLICABLE → any further write               (FORBIDDEN)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Optional


@dataclass(frozen=True)
class FieldOwner:
    """One entry in the ownership registry."""
    field_or_slot:                str
    canonical_owner:              str
    terminal:                     bool
    allowed_source_states:        FrozenSet[str]
    allowed_target_states:        FrozenSet[str]
    downstream_refinement_allowed: bool   # AMBIGUOUS→FILLED by evidence
    constitutional_contract:      str


@dataclass(frozen=True)
class TerminalBoundary:
    """
    Describes a known terminal boundary value.
    Once a field is filled with a terminal_value, no further writes are allowed.
    """
    field_or_slot:   str
    terminal_value:  str
    owner:           str
    constitutional_contract: str


# ── Terminal boundary values ───────────────────────────────────────────────────

TERMINAL_BOUNDARIES: tuple[TerminalBoundary, ...] = (
    TerminalBoundary(
        field_or_slot='BOUNDARY_TYPE_SLOT',
        terminal_value='JAMID_AALAM_BOUNDARY',
        owner='jamid_aalam_boundary',
        constitutional_contract='HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01',
    ),
    TerminalBoundary(
        field_or_slot='BOUNDARY_TYPE_SLOT',
        terminal_value='MABNI_BOUNDARY',
        owner='mabni_layer',
        constitutional_contract='HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01',
    ),
    TerminalBoundary(
        field_or_slot='BOUNDARY_TYPE_SLOT',
        terminal_value='OPERATOR_BOUNDARY',
        owner='mabni_layer',
        constitutional_contract='HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01',
    ),
)

# Fast lookup set of all terminal values for a field
_TERMINAL_VALUES_BY_FIELD: dict[str, frozenset[str]] = {}
for _tb in TERMINAL_BOUNDARIES:
    _TERMINAL_VALUES_BY_FIELD.setdefault(_tb.field_or_slot, set()).add(_tb.terminal_value)
_TERMINAL_VALUES_BY_FIELD = {k: frozenset(v) for k, v in _TERMINAL_VALUES_BY_FIELD.items()}


# ── Ownership registry ─────────────────────────────────────────────────────────

OWNERSHIP_REGISTRY: dict[str, FieldOwner] = {}

def _reg(
    field_or_slot: str,
    canonical_owner: str,
    terminal: bool,
    allowed_source_states: tuple[str, ...],
    allowed_target_states: tuple[str, ...],
    downstream_refinement_allowed: bool,
    constitutional_contract: str,
) -> None:
    OWNERSHIP_REGISTRY[field_or_slot] = FieldOwner(
        field_or_slot=field_or_slot,
        canonical_owner=canonical_owner,
        terminal=terminal,
        allowed_source_states=frozenset(allowed_source_states),
        allowed_target_states=frozenset(allowed_target_states),
        downstream_refinement_allowed=downstream_refinement_allowed,
        constitutional_contract=constitutional_contract,
    )


_reg(
    field_or_slot='BOUNDARY_TYPE_SLOT',
    canonical_owner='jamid_aalam_boundary',
    terminal=True,
    allowed_source_states=('UNKNOWN',),
    allowed_target_states=('FILLED',),
    downstream_refinement_allowed=False,
    constitutional_contract='HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01',
)

_reg(
    field_or_slot='PATH_DIRECTIVE_SLOT',
    canonical_owner='pre_root',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'DEFERRED'),
    allowed_target_states=('FILLED', 'DEFERRED'),
    downstream_refinement_allowed=False,
    constitutional_contract='HOKOM-PRE-ROOT-OWNERSHIP-01',
)

_reg(
    field_or_slot='WORD_CLASS_SLOT',
    canonical_owner='word_class_engine',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'AMBIGUOUS', 'DEFERRED'),
    allowed_target_states=('FILLED', 'DEFERRED', 'AMBIGUOUS'),
    downstream_refinement_allowed=False,
    constitutional_contract='HOKOM-WORD-CLASS-OWNERSHIP-01',
)

_reg(
    field_or_slot='RADICAL_R1',
    canonical_owner='cra_engine',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'DEFERRED'),
    allowed_target_states=('FILLED', 'DEFERRED'),
    downstream_refinement_allowed=False,
    constitutional_contract='HOKOM-ROOT-ADMISSION-OWNERSHIP-01',
)

_reg(
    field_or_slot='RADICAL_R2',
    canonical_owner='cra_engine',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'DEFERRED'),
    allowed_target_states=('FILLED', 'DEFERRED'),
    downstream_refinement_allowed=False,
    constitutional_contract='HOKOM-ROOT-ADMISSION-OWNERSHIP-01',
)

_reg(
    field_or_slot='RADICAL_R3',
    canonical_owner='cra_engine',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'DEFERRED'),
    allowed_target_states=('FILLED', 'DEFERRED'),
    downstream_refinement_allowed=False,
    constitutional_contract='HOKOM-ROOT-ADMISSION-OWNERSHIP-01',
)

_reg(
    field_or_slot='RADICAL_R4',
    canonical_owner='cra_engine',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'DEFERRED'),
    allowed_target_states=('FILLED', 'DEFERRED'),
    downstream_refinement_allowed=False,
    constitutional_contract='HOKOM-ROOT-ADMISSION-OWNERSHIP-01',
)

_reg(
    field_or_slot='PATTERN_CANDIDATE_SET',
    canonical_owner='pre_root',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'DEFERRED'),
    allowed_target_states=('FILLED', 'DEFERRED', 'AMBIGUOUS'),
    downstream_refinement_allowed=True,
    constitutional_contract='HOKOM-ROOT-ADMISSION-OWNERSHIP-01',
)

_reg(
    field_or_slot='NUMBER_SLOT',
    canonical_owner='p5_inflection',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'AMBIGUOUS'),
    allowed_target_states=('FILLED',),
    downstream_refinement_allowed=True,
    constitutional_contract='HOKOM-INFLECTION-OWNERSHIP-01',
)

_reg(
    field_or_slot='GENDER_SLOT',
    canonical_owner='p5_inflection',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'AMBIGUOUS'),
    allowed_target_states=('FILLED',),
    downstream_refinement_allowed=True,
    constitutional_contract='HOKOM-INFLECTION-OWNERSHIP-01',
)

_reg(
    field_or_slot='TENSE',
    canonical_owner='p5_inflection',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'AMBIGUOUS'),
    allowed_target_states=('FILLED',),
    downstream_refinement_allowed=True,
    constitutional_contract='HOKOM-INFLECTION-OWNERSHIP-01',
)

_reg(
    field_or_slot='MOOD',
    canonical_owner='p5_inflection',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'AMBIGUOUS', 'FILLED'),
    allowed_target_states=('FILLED',),
    downstream_refinement_allowed=True,   # context carrier may refine AMBIGUOUS/FILLED mood
    constitutional_contract='HOKOM-INFLECTION-OWNERSHIP-01',
)

_reg(
    field_or_slot='PERSON',
    canonical_owner='p5_inflection',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'AMBIGUOUS'),
    allowed_target_states=('FILLED',),
    downstream_refinement_allowed=True,
    constitutional_contract='HOKOM-INFLECTION-OWNERSHIP-01',
)

_reg(
    field_or_slot='VOICE',
    canonical_owner='p5_inflection',
    terminal=False,
    allowed_source_states=('UNKNOWN', 'AMBIGUOUS'),
    allowed_target_states=('FILLED',),
    downstream_refinement_allowed=True,
    constitutional_contract='HOKOM-INFLECTION-OWNERSHIP-01',
)


def is_terminal_boundary_value(field: str, value: str) -> bool:
    """Return True if value is a terminal boundary value for field."""
    return value in _TERMINAL_VALUES_BY_FIELD.get(field, frozenset())


def get_owner(field: str) -> Optional[FieldOwner]:
    """Return the FieldOwner for a field, or None if unregistered."""
    return OWNERSHIP_REGISTRY.get(field)
