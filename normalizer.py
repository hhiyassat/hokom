#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalizer.py — SHIM (R-2 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/p1_atomic_structure/normalizer.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p1_atomic_structure.normalizer import (  # noqa: F401
    HAMZA,
    FATHA,
    DAMMA,
    KASRA,
    SUKUN,
    SHADDA,
    SHORT_VOWELS,
    TANWIN,
    ALL_DIACRITICS,
    ARABIC_BASE,
    HAMZA_FORMS,
    ALEF_MADDA,
    normalize_hamza,
    normalize_al,
    normalize_shadda,
    normalize,
    normalize_hamza_tracked,
    normalize_al_tracked,
    normalize_shadda_tracked,
    normalize_tracked,
)

__all__ = [
    "HAMZA",
    "FATHA",
    "DAMMA",
    "KASRA",
    "SUKUN",
    "SHADDA",
    "SHORT_VOWELS",
    "TANWIN",
    "ALL_DIACRITICS",
    "ARABIC_BASE",
    "HAMZA_FORMS",
    "ALEF_MADDA",
    "normalize_hamza",
    "normalize_al",
    "normalize_shadda",
    "normalize",
    "normalize_hamza_tracked",
    "normalize_al_tracked",
    "normalize_shadda_tracked",
    "normalize_tracked",
]
