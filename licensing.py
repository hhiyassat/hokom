#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
licensing.py — SHIM (R-5 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has been split into:
  pipeline/p0_unicode/unicode_candidate.py   — GateResult, LAYER_NAMES, gate_unicode
  pipeline/p1_atomic_structure/letter_identity.py — gate_character/diacritic/cell, license_phone

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p0_unicode.unicode_candidate import (  # noqa: F401
    GateResult,
    LAYER_NAMES,
    CONSONANTS_25,
    LICENSED_CHARS,
    VOWEL_LETTERS_ALWAYS,
    VOWEL_LETTERS_COND,
    VOWEL_LETTERS_ALL,
    gate_unicode,
)

from pipeline.p1_atomic_structure.letter_identity import (  # noqa: F401
    FATHA,
    DAMMA,
    KASRA,
    SUKUN,
    SHADDA,
    TANWIN_F,
    TANWIN_D,
    TANWIN_K,
    SHORT_VOWELS,
    TANWIN,
    LICENSED_DIACRITICS,
    gate_character,
    gate_diacritic,
    gate_cell,
    license_phone,
)

__all__ = [
    # unicode_candidate
    "GateResult", "LAYER_NAMES",
    "CONSONANTS_25", "LICENSED_CHARS",
    "VOWEL_LETTERS_ALWAYS", "VOWEL_LETTERS_COND", "VOWEL_LETTERS_ALL",
    "gate_unicode",
    # letter_identity
    "FATHA", "DAMMA", "KASRA", "SUKUN", "SHADDA",
    "TANWIN_F", "TANWIN_D", "TANWIN_K",
    "SHORT_VOWELS", "TANWIN", "LICENSED_DIACRITICS",
    "gate_character", "gate_diacritic", "gate_cell", "license_phone",
]
