#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/governance/golden_rules_guard.py

HOKOM-GOLDEN-RULES-AND-LIVE-CLOSURE-CORRECTION-01

Integrity + amendment guard for golden_rules.md — the canonical protected
inventory of established linguistic, architectural, governance, and closure
rules.

Design rules (mirror the gold_manifest.py amendment guard):
  - GOLDEN_RULES_DIGEST is a FROZEN literal string (SHA-256 of the canonical
    golden_rules.md content).  The canonical content normalizes the
    `# GOLDEN_RULES_DIGEST: sha256:...` header line to `sha256:PENDING`
    so the digest is stable regardless of the human-readable header value.
  - verify_golden_rules_integrity() recomputes the digest from the live file
    and compares it to the frozen literal.
  - A MODIFY or DELETE of an existing rule requires a non-empty amendment_id —
    a matching recomputed digest ALONE is NOT authorization.
  - An APPEND of a new rule with a valid amendment_id + rationale → ACCEPT.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
from dataclasses import dataclass
from typing import Optional

# ── Canonical path to golden_rules.md (repo root) ─────────────────────────────
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
GOLDEN_RULES_PATH = _REPO_ROOT / 'golden_rules.md'

# ── Header line pattern (normalized away before hashing) ──────────────────────
_DIGEST_HEADER_RE = re.compile(r'(# GOLDEN_RULES_DIGEST: sha256:)[^\n]*')
_DIGEST_HEADER_CANONICAL = r'\1PENDING'

# ── Frozen digest literal (SHA-256 of canonical golden_rules.md) ──────────────
# To update: assign a GoldenRulesAmendmentRecord.amendment_id, recompute with
# _compute_canonical_digest(), and update this literal in the SAME commit.
GOLDEN_RULES_DIGEST: str = (
    'sha256:7b45e54ed6f2968d5846363749a1861c7d69964305f873ef3d67a993b76ea668'
)


def _canonicalize(content: str) -> str:
    """Normalize the digest header line so the hash is self-consistent."""
    return _DIGEST_HEADER_RE.sub(_DIGEST_HEADER_CANONICAL, content)


def _compute_canonical_digest(content: Optional[str] = None) -> str:
    """Compute SHA-256 of the canonical golden_rules.md content."""
    if content is None:
        content = GOLDEN_RULES_PATH.read_text(encoding='utf-8')
    canonical = _canonicalize(content)
    return 'sha256:' + hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def verify_golden_rules_integrity() -> tuple[bool, str]:
    """
    Return (ok, message).  ok=True when golden_rules.md is unchanged since
    GOLDEN_RULES_DIGEST was frozen.
    """
    if not GOLDEN_RULES_PATH.exists():
        return False, f'GOLDEN_RULES_MISSING: {GOLDEN_RULES_PATH} does not exist.'
    computed = _compute_canonical_digest()
    if computed == GOLDEN_RULES_DIGEST:
        return True, 'GOLDEN_RULES_INTEGRITY_OK'
    return False, (
        f'GOLDEN_RULES_INTEGRITY_VIOLATION: expected={GOLDEN_RULES_DIGEST!r} '
        f'computed={computed!r}. A GoldenRulesAmendmentRecord with a non-empty '
        'amendment_id is required to modify golden_rules.md.'
    )


# ──────────────────────────────────────────────────────────────────────────────
# Amendment record + authorization gate
# ──────────────────────────────────────────────────────────────────────────────

_VALID_CHANGE_TYPES = frozenset({'APPEND', 'MODIFY', 'DELETE'})


@dataclass(frozen=True)
class GoldenRulesAmendmentRecord:
    """
    Explicit amendment record required for any change to golden_rules.md.

    A matching recomputed new_digest alone does NOT authorize a MODIFY/DELETE.
    change_type ∈ {'APPEND', 'MODIFY', 'DELETE'}.
    """
    amendment_id: str
    old_digest: str
    new_digest: str
    change_type: str
    old_rule_text: str
    new_rule_text: str
    rationale: str
    affected_contracts: str


def verify_golden_rules_amendment(
    amendment: GoldenRulesAmendmentRecord,
    proposed_content: str,
) -> tuple[str, str]:
    """
    Return ('ACCEPT', reason) or ('GOVERNANCE_REJECTED', reason).

    Rules:
      1. change_type must be one of APPEND / MODIFY / DELETE.
      2. amendment_id must be non-empty for ALL change types — a recomputed
         digest alone is insufficient (especially for MODIFY/DELETE of an
         existing rule).
      3. old_digest must equal the current frozen GOLDEN_RULES_DIGEST.
      4. new_digest must equal the recomputed digest of proposed_content.
      5. rationale must be non-empty.
      6. MODIFY requires both old_rule_text and new_rule_text to be non-empty.
         DELETE requires old_rule_text.  APPEND requires new_rule_text.
    """
    ct = (amendment.change_type or '').strip().upper()
    if ct not in _VALID_CHANGE_TYPES:
        return (
            'GOVERNANCE_REJECTED',
            f'INVALID_CHANGE_TYPE: {amendment.change_type!r} not in '
            f'{sorted(_VALID_CHANGE_TYPES)}.',
        )

    # Rule 2 — amendment_id is mandatory. This is the core protection:
    # a recomputed digest alone must NOT authorize a MODIFY/DELETE.
    if not (amendment.amendment_id or '').strip():
        return (
            'GOVERNANCE_REJECTED',
            'AMENDMENT_ID_MISSING: a governance-assigned amendment_id is '
            'required. A matching recomputed digest alone does not authorize '
            'a change to an existing golden rule.',
        )

    # Rule 3 — old digest must match the current frozen digest.
    if amendment.old_digest != GOLDEN_RULES_DIGEST:
        return (
            'GOVERNANCE_REJECTED',
            f'OLD_DIGEST_MISMATCH: amendment.old_digest={amendment.old_digest!r} '
            f'does not match frozen GOLDEN_RULES_DIGEST={GOLDEN_RULES_DIGEST!r}.',
        )

    # Rule 4 — new digest must match the proposed content.
    computed_new = _compute_canonical_digest(proposed_content)
    if amendment.new_digest != computed_new:
        return (
            'GOVERNANCE_REJECTED',
            f'NEW_DIGEST_MISMATCH: amendment.new_digest={amendment.new_digest!r} '
            f'does not match computed={computed_new!r}.',
        )

    # Rule 5 — rationale mandatory.
    if not (amendment.rationale or '').strip():
        return (
            'GOVERNANCE_REJECTED',
            'MISSING_RATIONALE: rationale must not be empty.',
        )

    # Rule 6 — change-type-specific text requirements.
    if ct == 'MODIFY':
        if not (amendment.old_rule_text or '').strip() or not (
            amendment.new_rule_text or ''
        ).strip():
            return (
                'GOVERNANCE_REJECTED',
                'MODIFY_REQUIRES_OLD_AND_NEW_RULE_TEXT: both old_rule_text and '
                'new_rule_text must be provided for a MODIFY.',
            )
    elif ct == 'DELETE':
        if not (amendment.old_rule_text or '').strip():
            return (
                'GOVERNANCE_REJECTED',
                'DELETE_REQUIRES_OLD_RULE_TEXT: old_rule_text must be provided.',
            )
    elif ct == 'APPEND':
        if not (amendment.new_rule_text or '').strip():
            return (
                'GOVERNANCE_REJECTED',
                'APPEND_REQUIRES_NEW_RULE_TEXT: new_rule_text must be provided.',
            )

    return (
        'ACCEPT',
        f'GOLDEN_RULES_AMENDMENT_AUTHORIZED: amendment_id='
        f'{amendment.amendment_id!r} change_type={ct}.',
    )
