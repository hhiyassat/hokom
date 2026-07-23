#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/semantic_write_guard.py

HOKOM-CLOSED-CONTRACT-SEMANTIC-REGRESSION-FIREWALL-01

Guarded semantic write path.  Every attempted write to an owned semantic
field must go through SemanticWriteGuard.write() which enforces:

  1. Non-owner rejection (requesting_stage != canonical_owner)
  2. Filled-value immutability (FILLED(A) → FILLED(B) is FORBIDDEN)
  3. Terminal-boundary immutability (any write after terminal value)
  4. Monotonicity (UNKNOWN only goes to FILLED/DEFERRED/AMBIGUOUS, etc.)

Idempotent re-writes (FILLED(A) → FILLED(A)) are always accepted.
AMBIGUOUS → FILLED with evidence is always accepted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from pipeline.governance.slot_ownership_registry import (
    OWNERSHIP_REGISTRY,
    is_terminal_boundary_value,
    get_owner,
)


# ── Exceptions ─────────────────────────────────────────────────────────────────

class WriteRejected(Exception):
    """
    Raised when a guarded semantic write violates ownership or monotonicity.

    Attributes:
        field           — the field name that was attempted
        reason_code     — machine-readable reason (see REASON_CODES below)
        detail          — human-readable explanation
    """
    REASON_CODES = frozenset({
        'NON_OWNER_WRITE',
        'TERMINAL_BOUNDARY_OVERWRITE',
        'FILLED_VALUE_CHANGE',
        'INVALID_TRANSITION',
    })

    def __init__(
        self,
        field: str,
        reason_code: str,
        detail: str,
        requesting_stage: str,
        phase_id: str,
    ) -> None:
        self.field = field
        self.reason_code = reason_code
        self.detail = detail
        self.requesting_stage = requesting_stage
        self.phase_id = phase_id
        super().__init__(
            f"WriteRejected[{reason_code}] field={field!r} "
            f"stage={requesting_stage!r} phase={phase_id!r}: {detail}"
        )


# ── Write record ──────────────────────────────────────────────────────────────

@dataclass
class WriteRecord:
    field:            str
    old_state:        str
    old_value:        object
    new_state:        str
    new_value:        object
    requesting_stage: str
    evidence:         str
    phase_id:         str
    accepted:         bool = True


# ── Guard ─────────────────────────────────────────────────────────────────────

class SemanticWriteGuard:
    """
    Instance-level guarded write tracker.

    Usage:
        guard = SemanticWriteGuard()
        guard.write(field='WORD_CLASS_SLOT', old_state='UNKNOWN', old_value=None,
                    new_state='FILLED', new_value='FI3L',
                    requesting_stage='word_class_engine', evidence='...',
                    phase_id='p_word_class')
    """

    def __init__(self) -> None:
        # Current committed state per field: {field: (state, value)}
        self._committed: dict[str, tuple[str, object]] = {}
        self._history: list[WriteRecord] = []

    def write(
        self,
        *,
        field: str,
        old_state: str,
        old_value: object,
        new_state: str,
        new_value: object,
        requesting_stage: str,
        evidence: str,
        phase_id: str,
    ) -> WriteRecord:
        """
        Attempt a guarded write.  Raises WriteRejected on violation.
        Returns an accepted WriteRecord on success.

        Enforcement order:
          1. Owner check (non-owner → NON_OWNER_WRITE)
          2. Idempotent check (FILLED(A) → FILLED(A) → accepted)
          3. Terminal boundary check (any overwrite → TERMINAL_BOUNDARY_OVERWRITE)
          4. Filled-value immutability (FILLED(A) → FILLED(B) → FILLED_VALUE_CHANGE)
          5. Monotonicity check (invalid state transition)
        """
        owner_entry = get_owner(field)

        # ── 1. Owner check ─────────────────────────────────────────────────────
        if (
            owner_entry is not None
            and new_state == 'FILLED'
            and requesting_stage != owner_entry.canonical_owner
        ):
            # Allow context-carrier mood refinement (downstream_refinement_allowed)
            # only for AMBIGUOUS/FILLED → FILLED on MOOD field
            is_refinement = (
                owner_entry.downstream_refinement_allowed
                and old_state in ('AMBIGUOUS', 'FILLED')
                and new_state == 'FILLED'
            )
            if not is_refinement:
                rec = WriteRecord(
                    field=field, old_state=old_state, old_value=old_value,
                    new_state=new_state, new_value=new_value,
                    requesting_stage=requesting_stage, evidence=evidence,
                    phase_id=phase_id, accepted=False)
                self._history.append(rec)
                raise WriteRejected(
                    field=field,
                    reason_code='NON_OWNER_WRITE',
                    detail=(
                        f"Field {field!r} is owned by {owner_entry.canonical_owner!r}; "
                        f"write by {requesting_stage!r} is not permitted."
                    ),
                    requesting_stage=requesting_stage,
                    phase_id=phase_id,
                )

        # ── 2. Idempotent check ────────────────────────────────────────────────
        committed = self._committed.get(field)
        if committed is not None:
            c_state, c_value = committed
            if c_state == 'FILLED' and new_state == 'FILLED' and c_value == new_value:
                rec = WriteRecord(
                    field=field, old_state=old_state, old_value=old_value,
                    new_state=new_state, new_value=new_value,
                    requesting_stage=requesting_stage, evidence=evidence,
                    phase_id=phase_id, accepted=True)
                self._history.append(rec)
                return rec   # idempotent — accept silently

        # ── 3. Terminal boundary immutability ──────────────────────────────────
        if committed is not None:
            c_state, c_value = committed
            if c_state == 'FILLED' and isinstance(c_value, str):
                if is_terminal_boundary_value(field, c_value):
                    rec = WriteRecord(
                        field=field, old_state=old_state, old_value=old_value,
                        new_state=new_state, new_value=new_value,
                        requesting_stage=requesting_stage, evidence=evidence,
                        phase_id=phase_id, accepted=False)
                    self._history.append(rec)
                    raise WriteRejected(
                        field=field,
                        reason_code='TERMINAL_BOUNDARY_OVERWRITE',
                        detail=(
                            f"Field {field!r} is in terminal state "
                            f"{c_value!r}; downstream overwrite by "
                            f"{requesting_stage!r} is forbidden."
                        ),
                        requesting_stage=requesting_stage,
                        phase_id=phase_id,
                    )

        # ── 4. Filled-value immutability ───────────────────────────────────────
        if committed is not None:
            c_state, c_value = committed
            if (
                c_state == 'FILLED'
                and new_state == 'FILLED'
                and c_value != new_value
            ):
                # Check if downstream refinement is allowed (e.g. mood context)
                is_refinement = (
                    owner_entry is not None
                    and owner_entry.downstream_refinement_allowed
                )
                if not is_refinement:
                    rec = WriteRecord(
                        field=field, old_state=old_state, old_value=old_value,
                        new_state=new_state, new_value=new_value,
                        requesting_stage=requesting_stage, evidence=evidence,
                        phase_id=phase_id, accepted=False)
                    self._history.append(rec)
                    raise WriteRejected(
                        field=field,
                        reason_code='FILLED_VALUE_CHANGE',
                        detail=(
                            f"Field {field!r} is FILLED with {c_value!r}; "
                            f"attempting to change to {new_value!r} is "
                            f"FILLED(A)→FILLED(B) and forbidden."
                        ),
                        requesting_stage=requesting_stage,
                        phase_id=phase_id,
                    )

        # ── 5. Monotonicity ────────────────────────────────────────────────────
        if owner_entry is not None:
            if new_state not in owner_entry.allowed_target_states:
                rec = WriteRecord(
                    field=field, old_state=old_state, old_value=old_value,
                    new_state=new_state, new_value=new_value,
                    requesting_stage=requesting_stage, evidence=evidence,
                    phase_id=phase_id, accepted=False)
                self._history.append(rec)
                raise WriteRejected(
                    field=field,
                    reason_code='INVALID_TRANSITION',
                    detail=(
                        f"Field {field!r}: transition {old_state!r}→{new_state!r} "
                        f"not in allowed_target_states "
                        f"{owner_entry.allowed_target_states}."
                    ),
                    requesting_stage=requesting_stage,
                    phase_id=phase_id,
                )

        # ── Accept ─────────────────────────────────────────────────────────────
        self._committed[field] = (new_state, new_value)
        rec = WriteRecord(
            field=field, old_state=old_state, old_value=old_value,
            new_state=new_state, new_value=new_value,
            requesting_stage=requesting_stage, evidence=evidence,
            phase_id=phase_id, accepted=True)
        self._history.append(rec)
        return rec

    @property
    def history(self) -> list[WriteRecord]:
        return list(self._history)
