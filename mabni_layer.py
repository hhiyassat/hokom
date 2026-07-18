#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mabni_layer.py — SHIM (R-8 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/p5_lexical/mabni_projection.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged (including get_inventory, forwarded from the mabni inventory layer).
Do not add logic here.
"""

from pipeline.p5_lexical.mabni_projection import *  # noqa: F401,F403
from pipeline.p5_lexical.mabni_projection import (  # noqa: F401
    MabniBoundary,
    MabniOpen,
    MabniBlocked,
    process_mabni,
    get_inventory,
    MabniEntry,
    VERDICT_ICON,
    _lexical_class,
    _verdict_from,
)

__all__ = [
    "MabniBoundary",
    "MabniOpen",
    "MabniBlocked",
    "process_mabni",
    "get_inventory",
    "MabniEntry",
    "VERDICT_ICON",
]
