#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
operator_id_map.py — SHIM (R-7 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/p5_lexical/operator_projection.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.p5_lexical.operator_projection import *  # noqa: F401,F403
from pipeline.p5_lexical.operator_projection import (  # noqa: F401
    OperatorProfile,
    OPERATOR_PROFILE,
    get_profile,
    _bare_key,
    _fallback_profile,
    _SHADDA_INDEX,
    _DIACRITICS,
    _SHADDA,
)

__all__ = [
    "OperatorProfile",
    "OPERATOR_PROFILE",
    "get_profile",
]
