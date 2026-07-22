#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_candidate/compressed_form_candidates.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Extension module for generating candidate_radical_sequences for
two-consonant compressed forms (ajwaf imperative).

This module is NOT frozen.  It extends the CRA pipeline AFTER
analyze_host_consonants() returns DEFER for two-consonant surfaces,
without modifying frozen root_rules.py.

Triggered when:
  - analyze_host_consonants() returns residual_code ==
    'defer:root:two_consonant_form_unresolved'  (n == 2 surface)
  - The caller (canonical_radical_accounting.py) detects an empty
    candidate_radical_sequences and a two-consonant residual

Decision is based solely on:
  - The two surface consonants
  - The diacritic on C1 (from the normalized surface)

NOT on: root_hint, lemma_hint, ambiguity_expected, or any corpus field.

Invariants (T-10):
  - Returns a list of ≥2 candidate sequences, or None
  - canonical_root = None (caller must NOT set a selected root)
  - SlotState.AMBIGUOUS is emitted by adapt_root_radicals when ≥2 seqs present
"""

from __future__ import annotations

from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda


# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

# Weak middle radicals for ajwaf reconstruction
_WAW = 'و'
_YA  = 'ي'

# Diacritic Unicode codepoints (subset used for ajwaf classification)
_DAMMA = 'ُ'   # ُ  — damma  → WAW middle radical (primary)
_KASRA = 'ِ'   # ِ  — kasra  → YA  middle radical (primary)

# Full diacritic set (used to skip over vowel marks when scanning)
_DIACRITICS = frozenset('ًٌٍَُِّْٰٕٓٔ')


# ══════════════════════════════════════════════════════════════════════════════
# Internal helpers
# ══════════════════════════════════════════════════════════════════════════════

def _normalize(host: str) -> str:
    """Apply same normalization as root_rules.normalize_host."""
    return normalize_shadda(normalize_hamza(host))


def _extract_consonants(text: str) -> tuple:
    """Extract non-diacritic, non-space characters (mirrors root_rules)."""
    return tuple(ch for ch in text if ch not in _DIACRITICS and ch != ' ')


def _diacritic_after_first_consonant(normalized: str) -> str | None:
    """
    Return the diacritic character immediately following the first
    consonant in *normalized*, or None if absent / unclassifiable.

    Walk the normalized string; skip any leading diacritics, then treat
    the next character as C1, then read the immediately following
    diacritic (if any).
    """
    i = 0
    while i < len(normalized):
        ch = normalized[i]
        if ch in _DIACRITICS or ch == ' ':
            i += 1
            continue
        # ch is C1 — look at the next character
        if i + 1 < len(normalized) and normalized[i + 1] in _DIACRITICS:
            return normalized[i + 1]
        return None   # C1 found but no diacritic follows it
    return None


# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════

def generate_compressed_ajwaf_candidates(
    refined_host: str,
) -> list[list[str]] | None:
    """
    For a two-consonant compressed surface (ajwaf imperative), generate
    candidate triconsonantal radical sequences.

    Parameters
    ----------
    refined_host : stem after suffix/prefix stripping (stem_after_prefix
                   from canonical_radical_accounting), e.g. 'قُلْ', 'بِعْ'.

    Returns
    -------
    A list of exactly two [C1, Rmid, C2] sequences, or None if the surface
    does not qualify (wrong consonant count or unclassifiable diacritic).

    Invariant: returns None — not [] — when candidates cannot be produced,
    so the caller falls through to UNKNOWN rather than AMBIGUOUS-with-zero.

    Does NOT use root_hint, lemma_hint, or any corpus field.
    """
    normalized = _normalize(refined_host)
    consonants = _extract_consonants(normalized)

    if len(consonants) != 2:
        return None  # Only for two-consonant surfaces

    c1, c2 = consonants

    diacritic = _diacritic_after_first_consonant(normalized)

    if diacritic == _DAMMA:
        primary_mid   = _WAW
        alternate_mid = _YA
    elif diacritic == _KASRA:
        primary_mid   = _YA
        alternate_mid = _WAW
    else:
        # Fatha, sukun, missing, or ambiguous — cannot classify
        return None

    return [
        [c1, primary_mid,   c2],   # primary reconstruction
        [c1, alternate_mid, c2],   # alternate reconstruction
    ]
