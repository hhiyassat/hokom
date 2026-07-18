#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tokenizer.py — SHIM (R-3 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/p1_atomic_structure/tokenizer.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p1_atomic_structure.tokenizer import (  # noqa: F401
    PUNCT,
    Token,
    strip_punct,
    split_clitic,
    tokenize,
    words_only,
)

__all__ = [
    "PUNCT",
    "Token",
    "strip_punct",
    "split_clitic",
    "tokenize",
    "words_only",
]
