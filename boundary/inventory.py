"""
boundary/inventory.py — PR 3.7-pre: Internal Boundary Layer
Loads and queries the versioned closed-function-word inventory.

Lookup key is the NORMALIZED surface (after normalize_hamza).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

from boundary.models import BoundaryKind


# ══════════════════════════════════════════════════════════════════════════════
# 1.  Path to inventory file
# ══════════════════════════════════════════════════════════════════════════════

_INVENTORY_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "data", "boundary", "closed_function_words.json",
)


# ══════════════════════════════════════════════════════════════════════════════
# 2.  FunctionWordEntry
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FunctionWordEntry:
    normalized:        str
    surface_canonical: str
    word_class:        str
    kind:              BoundaryKind
    root_eligible:     bool
    note:              str


# ══════════════════════════════════════════════════════════════════════════════
# 3.  Inventory loading
# ══════════════════════════════════════════════════════════════════════════════

def _build_index(path: str) -> dict[str, FunctionWordEntry]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    index: dict[str, FunctionWordEntry] = {}
    for raw in data["entries"]:
        entry = FunctionWordEntry(
            normalized        = raw["normalized"],
            surface_canonical = raw["surface_canonical"],
            word_class        = raw["word_class"],
            kind              = BoundaryKind(raw["kind"]),
            root_eligible     = bool(raw["root_eligible"]),
            note              = raw.get("note", ""),
        )
        index[entry.normalized] = entry
    return index


def load_inventory(path: str | None = None) -> dict[str, FunctionWordEntry]:
    """Return the full inventory index (normalized → entry).

    Supply *path* to override the default location (useful in tests).
    """
    return _build_index(path or _INVENTORY_PATH)


# ══════════════════════════════════════════════════════════════════════════════
# 4.  Module-level singleton (lazy)
# ══════════════════════════════════════════════════════════════════════════════

_INDEX: Optional[dict[str, FunctionWordEntry]] = None


def _get_index() -> dict[str, FunctionWordEntry]:
    global _INDEX
    if _INDEX is None:
        _INDEX = load_inventory()
    return _INDEX


# ══════════════════════════════════════════════════════════════════════════════
# 5.  Public lookup
# ══════════════════════════════════════════════════════════════════════════════

def lookup_function_word(normalized: str) -> Optional[FunctionWordEntry]:
    """Look up *normalized* (post-normalize_hamza) in the inventory.

    Returns the entry if found, None otherwise.
    The caller is responsible for normalizing the surface before calling.
    """
    return _get_index().get(normalized)
