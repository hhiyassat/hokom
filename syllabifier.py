#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
syllabifier.py — SHIM (R-4 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has been split into:
  pipeline/p1_atomic_structure/cell_builder.py   — Phone, parse_phones, syllabify
  pipeline/p1_atomic_structure/slot_engineering.py — SLOT_TRANS, VALID_S, word_gate

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p1_atomic_structure.cell_builder import (  # noqa: F401
    FATHA,
    DAMMA,
    KASRA,
    SUKUN,
    SHADDA,
    TANWIN_F,
    TANWIN_D,
    TANWIN_K,
    TATWEEL,
    SHORT_VOWELS,
    TANWIN,
    ALL_DIACRITICS,
    VOWEL_LETTERS_ALWAYS,
    VOWEL_LETTERS_COND,
    VOWEL_LETTERS,
    ALEF_MADDA,
    ARABIC_BASE,
    Phone,
    parse_phones,
    syllabify,
    analyze_word,
    display,
    GATE_ICON,
    EXAMPLES,
    run_examples,
    interactive,
    main,
)

from pipeline.p1_atomic_structure.slot_engineering import (  # noqa: F401
    SLOT_TRANS,
    VALID_S,
    PREFIX_S,
    WORD_FINAL_ONLY,
    word_gate,
)

__all__ = [
    # cell_builder exports
    "FATHA", "DAMMA", "KASRA", "SUKUN", "SHADDA",
    "TANWIN_F", "TANWIN_D", "TANWIN_K", "TATWEEL",
    "SHORT_VOWELS", "TANWIN", "ALL_DIACRITICS",
    "VOWEL_LETTERS_ALWAYS", "VOWEL_LETTERS_COND", "VOWEL_LETTERS",
    "ALEF_MADDA", "ARABIC_BASE",
    "Phone", "parse_phones", "syllabify",
    "analyze_word", "display", "GATE_ICON", "EXAMPLES",
    "run_examples", "interactive", "main",
    # slot_engineering exports
    "SLOT_TRANS", "VALID_S", "PREFIX_S", "WORD_FINAL_ONLY", "word_gate",
]
