"""
bundle_contract.py — Authoritative documentation and validation for HokomClaimBundle.
evaluate_sga_bundle() accepts HokomClaimBundle ONLY.

HOKOM-TAAQOL-SGA-POST-CLOSURE-HARDENING-01 — HARDEN-03
"""
from __future__ import annotations

from pipeline.sga.contracts import HokomClaimBundle, SlotId, SlotState

BUNDLE_CONTRACT_VERSION = "1.0.0"

# Forbidden input types at the public bridge boundary.
# Raw primitives and legacy dicts must never be passed to evaluate_sga_bundle().
FORBIDDEN_INPUT_TYPES = (dict, tuple, list, str, bytes)


def validate_bundle(bundle: object) -> tuple[bool, list[str]]:
    """
    Validate that a bundle satisfies the HokomClaimBundle contract.
    Returns (is_valid, violations).

    This function is for diagnostic/testing use.
    For enforcement at the bridge boundary, use assert_valid_bundle_input().
    """
    violations: list[str] = []

    if not isinstance(bundle, HokomClaimBundle):
        return False, [
            f"WRONG_TYPE: expected HokomClaimBundle, got {type(bundle).__name__}"
        ]

    # claim_key must be non-empty SHA-256 hex (64 chars)
    if not bundle.claim_key or len(bundle.claim_key) != 64:
        violations.append(f"INVALID_CLAIM_KEY: length={len(bundle.claim_key)!r}")
    try:
        int(bundle.claim_key, 16)
    except (ValueError, TypeError):
        violations.append(f"INVALID_CLAIM_KEY_NOT_HEX: {bundle.claim_key!r}")

    # original_surface must be preserved and non-empty
    if not hasattr(bundle, 'surface') or bundle.surface is None:
        violations.append("MISSING_SURFACE_PROVENANCE")
    elif not bundle.surface.original_surface:
        violations.append("MISSING_ORIGINAL_SURFACE")

    # AMBIGUOUS slots must have selected=None and candidate_set with >1 candidates
    for slot in bundle.typed_slots:
        if slot.state == SlotState.AMBIGUOUS:
            if slot.candidate_set is None:
                violations.append(f"AMBIGUOUS_SLOT_{slot.slot_id.value}_NO_CANDIDATE_SET")
            elif slot.candidate_set.selected is not None:
                violations.append(
                    f"AMBIGUOUS_SLOT_{slot.slot_id.value}_HAS_SELECTION: "
                    f"selected={slot.candidate_set.selected!r}"
                )
            if slot.candidate_set is not None and len(slot.candidate_set.candidates) < 2:
                violations.append(
                    f"AMBIGUOUS_SLOT_{slot.slot_id.value}_INSUFFICIENT_CANDIDATES: "
                    f"count={len(slot.candidate_set.candidates)}"
                )

    # ORIGINAL_SURFACE typed slot must exist and not be UNKNOWN
    orig_slot = next(
        (s for s in bundle.typed_slots if s.slot_id == SlotId.ORIGINAL_SURFACE),
        None
    )
    if orig_slot is None:
        violations.append("ORIGINAL_SURFACE_TYPED_SLOT_MISSING")
    elif orig_slot.state == SlotState.UNKNOWN:
        violations.append("ORIGINAL_SURFACE_TYPED_SLOT_UNKNOWN")

    # profile_id must be a known profile
    from pipeline.sga.contracts import CLAIM_PROFILES
    if bundle.profile_id not in CLAIM_PROFILES:
        violations.append(f"UNKNOWN_PROFILE_ID: {bundle.profile_id!r}")

    return len(violations) == 0, violations


def assert_valid_bundle_input(obj: object) -> None:
    """
    Called at bridge entry or test boundary.
    Raises TypeError for any non-HokomClaimBundle input.

    This is the enforcement guard — fail-closed, no silent coercion.
    """
    if isinstance(obj, FORBIDDEN_INPUT_TYPES):
        raise TypeError(
            f"evaluate_sga_bundle() requires HokomClaimBundle, got {type(obj).__name__}. "
            "Raw dicts, tuples, strings, lists, bytes, and legacy payloads are forbidden "
            "at the live bridge boundary. Use build_claim_bundle() to produce a HokomClaimBundle."
        )
    if not isinstance(obj, HokomClaimBundle):
        raise TypeError(
            f"evaluate_sga_bundle() requires HokomClaimBundle, "
            f"got {type(obj).__name__}. "
            "Only HokomClaimBundle instances produced by build_claim_bundle() are accepted."
        )


def get_bundle_contract_version() -> str:
    """Return the current bundle contract schema version."""
    return BUNDLE_CONTRACT_VERSION


__all__ = [
    "BUNDLE_CONTRACT_VERSION",
    "FORBIDDEN_INPUT_TYPES",
    "validate_bundle",
    "assert_valid_bundle_input",
    "get_bundle_contract_version",
]
