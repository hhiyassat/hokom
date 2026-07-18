#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
relation_contract.py — SHIM (R-6 refactoring)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The canonical implementation has moved to:
  pipeline/contracts/relation_contract.py

This file exists solely to preserve import compatibility for existing code
and tests that import from the root-level module. All names are re-exported
unchanged. Do not add logic here.
"""

from pipeline.contracts.relation_contract import *  # noqa: F401,F403
from pipeline.contracts.relation_contract import (  # noqa: F401
    RelationContract,
    make_contract,
)

__all__ = [
    "RelationContract",
    "make_contract",
]
