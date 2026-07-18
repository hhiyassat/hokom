#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mabni_inventory.py — SHIM (R-8 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/p5_lexical/mabni_inventory.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p5_lexical.mabni_inventory import *  # noqa: F401,F403
from pipeline.p5_lexical.mabni_inventory import (  # noqa: F401
    MabniEntry,
    MabniInventory,
    get_inventory,
    _strip_diacritics,
    _bare_preserve_shadda,
)

__all__ = [
    "MabniEntry",
    "MabniInventory",
    "get_inventory",
]
