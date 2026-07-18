"""
boundary/service.py — PR 3.7-pre: Internal Boundary Layer
Main entry point: assess_boundary(surface) -> RootEligibilityDecision.

Pipeline:
  1. normalize_hamza(surface)  → normalized
  2. Inventory lookup(normalized)
       hit  → return decision from inventory entry
       miss → structural path
  3. parse_phones(normalized)
  4. classify_by_structure(phones)
  5. Build RootEligibilityDecision

Design notes:
  • parse_phones already expands SHADDA internally (مَدَّ → م+د(sukun)+د).
    No separate normalize_shadda call is needed before phone parsing.
  • Inventory lookup uses the post-normalize_hamza form as the key so that
    إِلَى (surface) → ءِلَى (key) matches the inventory entry keyed on "ءِلَى".
  • BLOCK applies to the ROOT PATH only — the surface is not declared
    morphologically invalid; stage_state = NOT_OPENED, not REJECTED.
"""

from __future__ import annotations

from normalizer import normalize_hamza
from syllabifier import parse_phones

from boundary.eligibility import classify_by_structure
from boundary.inventory import lookup_function_word
from boundary.models import (
    BoundaryEvidence,
    BoundaryKind,
    RootEligibilityDecision,
    directive_for,
    stage_state_for,
)


# ══════════════════════════════════════════════════════════════════════════════
# Evidence sources (string constants for consistency)
# ══════════════════════════════════════════════════════════════════════════════

_SRC_INVENTORY          = "inventory"
_SRC_STRUCTURAL_COUNT   = "structural:phone_count"
_SRC_STRUCTURAL_PREFIX  = "structural:prefix_ambiguity"
_SRC_STRUCTURAL_COMPRESSED = "structural:compressed_verb"
_SRC_STRUCTURAL_ELIGIBLE   = "structural:root_eligible_structure"
_SRC_STRUCTURAL_UNDERLICENSED = "structural:underlicensed_short"
_SRC_STRUCTURAL_NON_VERBAL    = "structural:non_verbal_pattern"


# ══════════════════════════════════════════════════════════════════════════════
# Evidence notes by kind (used when inventory hit)
# ══════════════════════════════════════════════════════════════════════════════

_INVENTORY_NOTES: dict[BoundaryKind, str] = {
    BoundaryKind.CLOSED_FUNCTION_WORD:
        "Inventory confirms this as a function word with no root path.",
    BoundaryKind.POSSIBLE_FUNCTION_WORD:
        "Inventory flags this as a possible function word; root path blocked pending disambiguation.",
}


# ══════════════════════════════════════════════════════════════════════════════
# Structural evidence constructors
# ══════════════════════════════════════════════════════════════════════════════

def _structural_evidence(kind: BoundaryKind, n_phones: int) -> list[BoundaryEvidence]:
    """Build the evidence list for a structurally-derived kind."""
    if kind is BoundaryKind.COMPRESSED_VERB_CANDIDATE:
        return [
            BoundaryEvidence(
                source=_SRC_STRUCTURAL_COUNT,
                note=f"Phone count = {n_phones} (exactly 2).",
            ),
            BoundaryEvidence(
                source=_SRC_STRUCTURAL_COMPRESSED,
                note="Pattern: C(mutaharrik) + C(sakin) → compressed-verb candidate.",
            ),
        ]
    if kind is BoundaryKind.AMBIGUOUS:
        return [
            BoundaryEvidence(
                source=_SRC_STRUCTURAL_COUNT,
                note=f"Phone count = {n_phones} (exactly 3).",
            ),
            BoundaryEvidence(
                source=_SRC_STRUCTURAL_PREFIX,
                note="Phone[0] ∈ {ي،ت،ن،ء} with fatha AND phone[2] is vowel-letter → muḍāriʿ-prefix ambiguity.",
            ),
        ]
    if kind is BoundaryKind.ROOT_ELIGIBLE:
        return [
            BoundaryEvidence(
                source=_SRC_STRUCTURAL_COUNT,
                note=f"Phone count = {n_phones} (≥3).",
            ),
            BoundaryEvidence(
                source=_SRC_STRUCTURAL_ELIGIBLE,
                note="≥2 non-VL consonants present; surface passes root-eligible structure check.",
            ),
        ]
    if kind is BoundaryKind.UNDERLICENSED_SHORT_SURFACE:
        return [
            BoundaryEvidence(
                source=_SRC_STRUCTURAL_UNDERLICENSED,
                note=f"Phone count = {n_phones} — too short and does not match C+sukun compressed pattern.",
            ),
        ]
    if kind is BoundaryKind.NON_VERBAL_SURFACE:
        return [
            BoundaryEvidence(
                source=_SRC_STRUCTURAL_NON_VERBAL,
                note=f"Phone count = {n_phones} but insufficient consonant density for a verbal root surface.",
            ),
        ]
    # fallback
    return [BoundaryEvidence(source="structural:unknown", note=f"Kind={kind.value}")]


# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════

def assess_boundary(surface: str) -> RootEligibilityDecision:
    """Gate *surface* through the Internal Boundary Layer.

    Parameters
    ----------
    surface : str
        The Arabic surface form, fully diacritized (تَشْكِيل كامل).
        Hamza variants (أ/إ/ؤ/ئ/آ) are normalised internally.

    Returns
    -------
    RootEligibilityDecision
        The complete verdict including kind, directive, stage_state, and evidence.
    """
    normalized = normalize_hamza(surface)

    # ── Inventory path ────────────────────────────────────────────────────────
    entry = lookup_function_word(normalized)
    if entry is not None:
        kind      = entry.kind
        directive = directive_for(kind)
        state     = stage_state_for(directive)
        evidence  = [
            BoundaryEvidence(
                source=_SRC_INVENTORY,
                note=_INVENTORY_NOTES.get(kind, f"Inventory entry: {entry.note}"),
            )
        ]
        return RootEligibilityDecision(
            surface     = surface,
            normalized  = normalized,
            kind        = kind,
            directive   = directive,
            stage_state = state,
            evidence    = evidence,
            note        = entry.note or None,
        )

    # ── Structural path ───────────────────────────────────────────────────────
    phones   = parse_phones(normalized)
    kind     = classify_by_structure(phones)
    directive = directive_for(kind)
    state     = stage_state_for(directive)
    evidence  = _structural_evidence(kind, len(phones))

    return RootEligibilityDecision(
        surface     = surface,
        normalized  = normalized,
        kind        = kind,
        directive   = directive,
        stage_state = state,
        evidence    = evidence,
        note        = None,
    )
