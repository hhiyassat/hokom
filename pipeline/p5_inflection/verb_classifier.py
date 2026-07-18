#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/verb_classifier.py

Classify root type (SOUND, HOLLOW_WAW, etc.) from canonical root tuple.
Returns string constants from models.RootClass.
"""
from __future__ import annotations

WAW          = 'و'   # و
YAA          = 'ي'   # ي
ALIF_MAKSURA = 'ى'   # ى  (treated as defective C3)
HAMZA_CHARS  = frozenset('ءأإآؤئ')  # ء أ إ آ ؤ ئ
WEAK         = frozenset([WAW, YAA])


def classify_root(root: tuple) -> str:
    """
    Classify a canonical root tuple into a RootClass string.

    Handles 3-consonant roots only.  Returns 'SOUND' for 4-consonant roots
    (augmented roots are classified as AUGMENTED by the caller).

    Priority order:
      Geminated > Lafif > Hollow > Defective > Assimilated > Hamzated > Sound
    """
    if root is None or len(root) < 3:
        return 'SOUND'

    C1, C2, C3 = root[0], root[1], root[2]

    # ── Geminated: C2 == C3 (both non-weak identical consonants) ─────────────
    if C2 == C3 and C2 not in WEAK:
        return 'GEMINATED'

    # ── Lafif mafruq: C1 weak AND C3 weak ────────────────────────────────────
    if C1 in WEAK and C3 in WEAK:
        return 'LAFIF_MAFRUQ'

    # ── Lafif maqrun: C2 weak AND C3 weak ────────────────────────────────────
    if C2 in WEAK and C3 in WEAK:
        return 'LAFIF_MAQRUN'

    # ── Hollow: C2 is weak ────────────────────────────────────────────────────
    if C2 == WAW:
        return 'HOLLOW_WAW'
    if C2 == YAA:
        return 'HOLLOW_YAA'

    # ── Defective: C3 is weak ─────────────────────────────────────────────────
    if C3 == WAW:
        return 'DEFECTIVE_WAW'
    if C3 in (YAA, ALIF_MAKSURA):
        return 'DEFECTIVE_YAA'

    # ── Assimilated: C1 is weak ───────────────────────────────────────────────
    if C1 == WAW:
        return 'ASSIMILATED_WAW'
    if C1 == YAA:
        return 'ASSIMILATED_YAA'

    # ── Hamzated ──────────────────────────────────────────────────────────────
    if C1 in HAMZA_CHARS:
        return 'HAMZATED_C1'
    if C2 in HAMZA_CHARS:
        return 'HAMZATED_C2'
    if C3 in HAMZA_CHARS:
        return 'HAMZATED_C3'

    return 'SOUND'
