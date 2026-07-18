#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
span_alignment.py — SHIM (R-2 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/p1_atomic_structure/span_map.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p1_atomic_structure.span_map import (  # noqa: F401
    SpanEntry,
    SpanAlignmentMap,
    ComponentRole,
    ComponentBoundary,
)

__all__ = [
    "SpanEntry",
    "SpanAlignmentMap",
    "ComponentRole",
    "ComponentBoundary",
]
