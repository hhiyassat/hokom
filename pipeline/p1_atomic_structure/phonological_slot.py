"""
Typed PhonologicalSlot — closes SGA violation T-02.
The existing syllabify() output (list[dict]) is wrapped, not rewritten.
No Arabic linguistic logic here — only structural wrapping.

HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 — Stage 6
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PhonologicalSlotKind(str, Enum):
    CONSONANT     = "CONSONANT"
    SHORT_VOWEL   = "SHORT_VOWEL"
    LONG_VOWEL    = "LONG_VOWEL"
    SUKUN         = "SUKUN"
    SHADDA        = "SHADDA"
    MADD          = "MADD"
    TANWIN        = "TANWIN"
    HAMZA         = "HAMZA"
    UNKNOWN       = "UNKNOWN"


@dataclass(frozen=True)
class PhonologicalSlot:
    position: int
    character: str
    kind: PhonologicalSlotKind
    diacritic: Optional[str] = None
    is_root_bearer: bool = False
    gemination_type: Optional[str] = None  # GeminationType value from SGA contracts


def wrap_syllabify_output(raw_cells: list[dict]) -> tuple[PhonologicalSlot, ...]:
    """
    Wrap the existing list[dict] output from syllabify() into typed PhonologicalSlots.
    Does not recompute — adapter only.

    Accepted dict keys (tries each in order):
      character: 'letter' | 'char' | 'character'
      diacritic: 'diacritic' | 'haraka' | 'vowel'
      kind:      'kind' | 'type'
    """
    result = []
    for i, cell in enumerate(raw_cells):
        char = cell.get("letter") or cell.get("char") or cell.get("character", "")
        diac = cell.get("diacritic") or cell.get("haraka") or cell.get("vowel")
        kind_str = cell.get("kind") or cell.get("type") or "UNKNOWN"

        try:
            kind = PhonologicalSlotKind(kind_str.upper())
        except ValueError:
            kind = PhonologicalSlotKind.UNKNOWN

        result.append(PhonologicalSlot(
            position=i,
            character=char,
            kind=kind,
            diacritic=diac,
        ))
    return tuple(result)


__all__ = [
    "PhonologicalSlotKind",
    "PhonologicalSlot",
    "wrap_syllabify_output",
]
