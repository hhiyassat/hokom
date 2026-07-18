#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p1_atomic_structure/span_alignment.py — P1 Position Carrier
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Canonical location (R-2 refactoring).
The root-level span_alignment.py is now a shim that re-exports from here.

Stable position tracking across all normalization layers.

Every normalized span must be projectable back to the original raw surface.
Additive — does not modify normalize() or any existing pipeline behavior.
No behaviour changes, no commits, no tag, no merge.

Governing rule (always in force):
    No normalization, shadda expansion, or prefix/suffix stripping may produce
    a span with no traceable origin in the raw surface.
    Every normalized position must be projectable back to a raw position.

Public API:
    SpanEntry           — one alignment record (raw span ↔ norm span)
    SpanAlignmentMap    — full map for a string; projects in both directions
    ComponentRole       — role enum for ComponentBoundary  (B-5)
    ComponentBoundary   — typed span with role and both coordinate systems (B-5)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# SpanEntry
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SpanEntry:
    """
    One alignment record mapping a raw codepoint span to a normalized span.

    Spans are half-open: [raw_start, raw_end) and [norm_start, norm_end).

    op values:
        IDENTITY   — raw and norm spans have equal length; content unchanged
        REPLACE    — raw and norm spans have equal length; content changed
                     e.g. أ (U+0623) → ء (U+0621): same length, different codepoint
        EXPAND     — norm span is longer than raw span
                     e.g. آ → ءَا (1 raw → 3 norm), or shadda expansion (3 raw → 4 norm)
        CONTRACT   — norm span is shorter than raw span (currently unused)
    """
    raw_start:  int
    raw_end:    int    # exclusive
    norm_start: int
    norm_end:   int    # exclusive
    op:         str    # 'IDENTITY' | 'REPLACE' | 'EXPAND' | 'CONTRACT'
    note:       str = ''


# ══════════════════════════════════════════════════════════════════════════════
# SpanAlignmentMap
# ══════════════════════════════════════════════════════════════════════════════

class SpanAlignmentMap:
    """
    Full alignment map for one string.

    Entries are non-overlapping in raw-space and in norm-space, stored in
    left-to-right raw order.  Together they cover [0, raw_len) and [0, norm_len).

    Projection rules:
        IDENTITY / REPLACE with equal lengths: precise sub-span projection
                (linear offset within the entry).
        EXPAND / CONTRACT / REPLACE with unequal lengths: conservative —
                the full raw or norm entry span is returned because sub-span
                mapping is not defined for length-changing transformations.

    Composition:
        self.compose(other) chains raw→mid (self) and mid→final (other)
        into a single raw→final map.  Precondition: self.norm_len == other.raw_len.
    """

    def __init__(
        self,
        raw_len:  int,
        norm_len: int,
        entries:  list[SpanEntry],
    ) -> None:
        self._raw_len  = raw_len
        self._norm_len = norm_len
        self._entries: list[SpanEntry] = list(entries)  # sorted by raw_start

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def raw_len(self) -> int:
        return self._raw_len

    @property
    def norm_len(self) -> int:
        return self._norm_len

    @property
    def entries(self) -> list[SpanEntry]:
        return list(self._entries)

    # ── Factory methods ───────────────────────────────────────────────────────

    @classmethod
    def identity(cls, length: int) -> 'SpanAlignmentMap':
        """Identity map for a string of given length (no transformations)."""
        if length == 0:
            return cls(0, 0, [])
        return cls(
            length, length,
            [SpanEntry(0, length, 0, length, 'IDENTITY', 'identity')],
        )

    @classmethod
    def from_entries(
        cls,
        raw_len:  int,
        norm_len: int,
        entries:  list[SpanEntry],
    ) -> 'SpanAlignmentMap':
        """Create from a pre-built list of SpanEntry objects."""
        return cls(raw_len, norm_len, entries)

    # ── Projection ────────────────────────────────────────────────────────────

    def project_to_norm(self, raw_start: int, raw_end: int) -> tuple[int, int]:
        """
        Return the normalized span corresponding to [raw_start, raw_end).

        For IDENTITY / same-length REPLACE entries: precise sub-span (linear offset).
        For EXPAND entries: returns the full entry's norm span (conservative but correct).

        If no entry overlaps, returns (raw_start, raw_end) as identity fallback.
        """
        n_start: Optional[int] = None
        n_end:   Optional[int] = None

        for e in self._entries:
            ovl_s = max(raw_start, e.raw_start)
            ovl_e = min(raw_end,   e.raw_end)
            if ovl_s >= ovl_e:
                continue

            raw_e_len  = e.raw_end  - e.raw_start
            norm_e_len = e.norm_end - e.norm_start

            if raw_e_len == norm_e_len:
                # Precise: linear offset within the entry
                offset_s = ovl_s - e.raw_start
                offset_e = ovl_e - e.raw_start
                this_ns = e.norm_start + offset_s
                this_ne = e.norm_start + offset_e
            else:
                # EXPAND or CONTRACT: return the full entry norm span
                this_ns = e.norm_start
                this_ne = e.norm_end

            if n_start is None or this_ns < n_start:
                n_start = this_ns
            if n_end is None or this_ne > n_end:
                n_end = this_ne

        if n_start is None:
            return (raw_start, raw_end)
        return (n_start, n_end)

    def project_to_raw(self, norm_start: int, norm_end: int) -> tuple[int, int]:
        """
        Return the raw span corresponding to [norm_start, norm_end).

        For IDENTITY / same-length entries: precise sub-span (linear offset).
        For EXPAND entries: returns the full entry's raw span (conservative).

        If no entry overlaps, returns (norm_start, norm_end) as identity fallback.
        """
        r_start: Optional[int] = None
        r_end:   Optional[int] = None

        for e in self._entries:
            ovl_s = max(norm_start, e.norm_start)
            ovl_e = min(norm_end,   e.norm_end)
            if ovl_s >= ovl_e:
                continue

            raw_e_len  = e.raw_end  - e.raw_start
            norm_e_len = e.norm_end - e.norm_start

            if raw_e_len == norm_e_len:
                # Precise: inverse linear offset
                offset_s = ovl_s - e.norm_start
                offset_e = ovl_e - e.norm_start
                this_rs = e.raw_start + offset_s
                this_re = e.raw_start + offset_e
            else:
                # EXPAND or CONTRACT: return the full raw span
                this_rs = e.raw_start
                this_re = e.raw_end

            if r_start is None or this_rs < r_start:
                r_start = this_rs
            if r_end is None or this_re > r_end:
                r_end = this_re

        if r_start is None:
            return (norm_start, norm_end)
        return (r_start, r_end)

    # ── Composition ───────────────────────────────────────────────────────────

    def compose(self, other: 'SpanAlignmentMap') -> 'SpanAlignmentMap':
        """
        Compose self (raw→mid) with other (mid→final) into raw→final.

        For each entry in self, project its norm (mid) span through other
        to find the final span.  The composed map preserves fine-grained
        per-char entries so that project_to_raw() can correctly union
        multiple raw chars that expand to the same final span.

        Precondition: self.norm_len == other.raw_len
        """
        composed: list[SpanEntry] = []
        for e in self._entries:
            # Map self's norm (= mid) span through other to get final span
            f_start, f_end = other.project_to_norm(e.norm_start, e.norm_end)

            raw_len   = e.raw_end  - e.raw_start
            final_len = f_end - f_start

            if final_len > raw_len:
                op = 'EXPAND'
            elif final_len < raw_len:
                op = 'CONTRACT'
            elif e.op == 'IDENTITY':
                # Check whether 'other' performed any transformation in this segment
                inner_changed = any(
                    o.op not in ('IDENTITY',)
                    for o in other._entries
                    if o.raw_start < e.norm_end and o.raw_end > e.norm_start
                )
                op = 'REPLACE' if inner_changed else 'IDENTITY'
            else:
                op = e.op   # REPLACE or CONTRACT, preserved

            composed.append(SpanEntry(
                raw_start  = e.raw_start,
                raw_end    = e.raw_end,
                norm_start = f_start,
                norm_end   = f_end,
                op         = op,
                note       = e.note,
            ))

        return SpanAlignmentMap(self._raw_len, other._norm_len, composed)

    # ── Debug ─────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f'SpanAlignmentMap(raw_len={self._raw_len}, '
            f'norm_len={self._norm_len}, '
            f'n_entries={len(self._entries)})'
        )

    def dump(self) -> str:
        """Return a human-readable table of entries for debugging."""
        lines = [
            f'SpanAlignmentMap raw={self._raw_len} → norm={self._norm_len}',
        ]
        for e in self._entries:
            delta = (e.norm_end - e.norm_start) - (e.raw_end - e.raw_start)
            sign  = f'+{delta}' if delta >= 0 else str(delta)
            lines.append(
                f'  raw[{e.raw_start},{e.raw_end}) '
                f'→ norm[{e.norm_start},{e.norm_end}) '
                f'{e.op:10} Δ={sign:4}  {e.note}'
            )
        return '\n'.join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# ComponentBoundary  (B-5)
# ══════════════════════════════════════════════════════════════════════════════

class ComponentRole(str, Enum):
    """
    Role of a span within a fully analyzed Arabic token.

    Roles are assigned during attachment recognition; they never affect
    P4 verdicts or the underlying morphological analysis.
    """
    HOST              = 'HOST'              # residual word form (→ HR2S)
    PREFIX            = 'PREFIX'            # recognized prefix operator (لِ, بِ, …)
    SUFFIX            = 'SUFFIX'            # recognized suffix mabni form (هُ, هُمْ, …)
    OPERATOR          = 'OPERATOR'          # standalone operator / function word
    MABNI             = 'MABNI'             # standalone mabni form (whole-token match)
    INFLECTIONAL_TAIL = 'INFLECTIONAL_TAIL' # e.g. نَ in يَسْتَطِيعُونَ


@dataclass(frozen=True)
class ComponentBoundary:
    """
    A typed, dual-coordinate span for one component of an analyzed token.

    Both raw_span and norm_span are (start, end) half-open intervals.

    Governing rule: raw_span must always be traceable to the original raw
    surface.  When no alignment map is available, raw_span == norm_span
    (best-effort — these are normalized coordinates, not true raw coordinates).
    """
    role:      ComponentRole
    raw_span:  tuple[int, int]   # coordinates in the original raw surface
    norm_span: tuple[int, int]   # coordinates in normalize()-output surface
    surface:   str               # matched surface characters (from norm)
    mabni_id:  Optional[str] = None
    notes:     str = ''
