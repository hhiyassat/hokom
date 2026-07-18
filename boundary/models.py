"""
boundary/models.py — PR 3.7-pre: Internal Boundary Layer
Data types for root-path eligibility gating.

Hierarchy:
  BoundaryKind      — what kind of surface this is
  RootPathDirective — OPEN | DEFER | BLOCK
  StageState        — OPENED | DEFERRED | NOT_OPENED
  BoundaryEvidence  — one piece of evidence supporting the kind decision
  RootEligibilityDecision — the full gated verdict with provenance

Directive semantics (PR 3.7-fix):
  OPEN  — root engine may run and generate candidates
  DEFER — path acknowledged; root engine defers without form detection
          (structural ambiguity or possible function word — NOT inventory-confirmed)
  BLOCK — root path not opened; inventory-confirmed closed word or structural impossibility

Rule: الحجب البنيوي لا يُستعمل إلا عندما يمنع الشكل مسار الجذر قطعًا.
      التباس البادئة (AMBIGUOUS) لا يمنع الجذر — يؤجل الحكم فقط (DEFER).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1.  BoundaryKind — classification of the surface form
# ══════════════════════════════════════════════════════════════════════════════

class BoundaryKind(str, Enum):
    """Surface-level classification produced by the boundary gate."""

    ROOT_ELIGIBLE            = "ROOT_ELIGIBLE"
    """Surface passes all structural tests; root hypothesis engine may run."""

    CLOSED_FUNCTION_WORD     = "CLOSED_FUNCTION_WORD"
    """Inventory-confirmed function word with no plausible root path (مِنْ، هَلْ، فِي …)."""

    POSSIBLE_FUNCTION_WORD   = "POSSIBLE_FUNCTION_WORD"
    """Inventory entry whose root status is historically debated (عَلَى، إِلَى، مَتَى)."""

    COMPRESSED_VERB_CANDIDATE = "COMPRESSED_VERB_CANDIDATE"
    """Two-phone surface with C+sukun pattern; eligible for compressed-imperative root path (قُلْ، قِفْ …)."""

    CLITICIZED_SURFACE       = "CLITICIZED_SURFACE"
    """Surface carries a detected proclitic or enclitic that was not stripped before analysis."""

    UNDERLICENSED_SHORT_SURFACE = "UNDERLICENSED_SHORT_SURFACE"
    """Two-phone surface not matching C+sukun compressed pattern and not in inventory; too short for root hypothesis."""

    NON_VERBAL_SURFACE       = "NON_VERBAL_SURFACE"
    """Surface is structurally inconsistent with verbal morphology (e.g., broken plural pattern)."""

    AMBIGUOUS                = "AMBIGUOUS"
    """Surface matches a muḍāriʿ-prefix shape with a final vowel letter; cannot be gated without further context (تَقِي، يَقِي …)."""


# ══════════════════════════════════════════════════════════════════════════════
# 2.  RootPathDirective
# ══════════════════════════════════════════════════════════════════════════════

class RootPathDirective(str, Enum):
    """Instruction to the downstream root hypothesis engine."""

    OPEN  = "OPEN"
    """Root path is open; the engine may generate and evaluate candidates."""

    DEFER = "DEFER"
    """Path is acknowledged but root engine defers without running form detectors.
    Used for AMBIGUOUS and POSSIBLE_FUNCTION_WORD: not inventory-confirmed closed,
    but too ambiguous for form detection to proceed safely.
    stage_state = DEFERRED.  DEFER ≠ BLOCK: the word is not declared closed."""

    BLOCK = "BLOCK"
    """Root path is not opened.
    Used for CLOSED_FUNCTION_WORD (inventory-confirmed) and structural impossibilities
    (UNDERLICENSED_SHORT_SURFACE, NON_VERBAL_SURFACE).
    stage_state = NOT_OPENED.  The word is not rejected — only the root path is gated."""


# ══════════════════════════════════════════════════════════════════════════════
# 3.  StageState
# ══════════════════════════════════════════════════════════════════════════════

class StageState(str, Enum):
    OPENED     = "OPENED"
    """Root path is open and form detection may proceed."""

    DEFERRED   = "DEFERRED"
    """Root path acknowledged but deferred — structural ambiguity prevented form detection.
    Corresponds to RootPathDirective.DEFER."""

    NOT_OPENED = "NOT_OPENED"
    """Root stage was not entered — boundary blocked the path entirely.
    Corresponds to RootPathDirective.BLOCK."""


# ══════════════════════════════════════════════════════════════════════════════
# 4.  BoundaryEvidence
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class BoundaryEvidence:
    """One piece of evidence contributing to the boundary decision."""

    source: str
    """Where this evidence came from: 'inventory', 'structural:phone_count',
    'structural:prefix_ambiguity', 'structural:compressed_verb', etc."""

    note: str
    """Human-readable explanation of this evidence item."""

    def to_dict(self) -> dict:
        return {"source": self.source, "note": self.note}


# ══════════════════════════════════════════════════════════════════════════════
# 5.  RootEligibilityDecision
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class RootEligibilityDecision:
    """Full gated verdict for a single surface form."""

    surface:    str
    """Original surface as supplied by the caller (before normalization)."""

    normalized: str
    """Surface after normalize_hamza (the form used for inventory lookup and phone parsing)."""

    kind:       BoundaryKind
    directive:  RootPathDirective
    stage_state: StageState
    evidence:   list[BoundaryEvidence] = field(default_factory=list)
    note:       Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "surface":     self.surface,
            "normalized":  self.normalized,
            "kind":        self.kind.value,
            "directive":   self.directive.value,
            "stage_state": self.stage_state.value,
            "evidence":    [e.to_dict() for e in self.evidence],
            "note":        self.note,
        }


# ══════════════════════════════════════════════════════════════════════════════
# 6.  Derived helpers
# ══════════════════════════════════════════════════════════════════════════════

#: Kinds whose directive is OPEN — root path is accessible, form detection runs
OPEN_KINDS: frozenset[BoundaryKind] = frozenset({
    BoundaryKind.ROOT_ELIGIBLE,
    BoundaryKind.COMPRESSED_VERB_CANDIDATE,
})

#: Kinds whose directive is DEFER — path acknowledged but form detection skipped
#: Rule: structural ambiguity/incompleteness ≠ proven impossibility; DEFER not BLOCK.
#:
#: UNDERLICENSED_SHORT_SURFACE أُضيف هنا (PR 3.9-fix):
#:   حْدَ يبدأ بساكن — عجز بنيوي من أثر التجزئة، لا منع معجمي مُثبَت.
#:   DEFER يُقرّ بالبنية غير المكتملة ويُعلِّق الحكم، بينما BLOCK يحسم
#:   الاستحالة — وهذا لا يصح لسطح ناتج عن فصل وابقة.
DEFER_KINDS: frozenset[BoundaryKind] = frozenset({
    BoundaryKind.AMBIGUOUS,
    BoundaryKind.POSSIBLE_FUNCTION_WORD,
    BoundaryKind.UNDERLICENSED_SHORT_SURFACE,   # عجز بنيوي لا منع معجمي
})

#: Kinds whose directive is BLOCK — root path not opened
#: Only inventory-confirmed closed words (CLOSED_FUNCTION_WORD) and
#: surfaces whose non-verbal status is structurally established.
#: (UNDERLICENSED نُقل إلى DEFER — انظر الحاشية أعلاه)
BLOCK_KINDS: frozenset[BoundaryKind] = frozenset({
    BoundaryKind.CLOSED_FUNCTION_WORD,
    BoundaryKind.NON_VERBAL_SURFACE,
    BoundaryKind.CLITICIZED_SURFACE,
})


def directive_for(kind: BoundaryKind) -> RootPathDirective:
    if kind in OPEN_KINDS:
        return RootPathDirective.OPEN
    if kind in DEFER_KINDS:
        return RootPathDirective.DEFER
    return RootPathDirective.BLOCK


def stage_state_for(directive: RootPathDirective) -> StageState:
    if directive is RootPathDirective.OPEN:
        return StageState.OPENED
    if directive is RootPathDirective.DEFER:
        return StageState.DEFERRED
    return StageState.NOT_OPENED
