#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
glyph_classification.py — SHIM (R-1 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/p0_unicode/glyph_classification.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p0_unicode.glyph_classification import (  # noqa: F401
    BaseGlyphClass,
    GlyphJudgment,
    GlyphTrace,
    MarkClass,
    MarkState,
    build_glyph_traces,
    classify_base_glyph,
    classify_combining_mark,
    is_mudaric_form,
    is_verbal_dual_host,
    last_base_glyph,
    p0_licensed,
)

__all__ = [
    "BaseGlyphClass",
    "GlyphJudgment",
    "GlyphTrace",
    "MarkClass",
    "MarkState",
    "build_glyph_traces",
    "classify_base_glyph",
    "classify_combining_mark",
    "is_mudaric_form",
    "is_verbal_dual_host",
    "last_base_glyph",
    "p0_licensed",
]
