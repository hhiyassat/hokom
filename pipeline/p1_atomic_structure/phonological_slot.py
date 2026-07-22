"""
Typed PhonologicalSlot — closes SGA violation T-02.
The existing syllabify() output (list[dict]) is wrapped, not rewritten.
No Arabic linguistic logic here — only structural wrapping.

HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION-01 — Stage 6
T-02 completion: full kind inference from syllabify() dict format.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Unicode diacritic constants (no Arabic logic — pattern matching only)
_SHADDA_CHAR  = 'ّ'   # ّ
_SUKUN_CHAR   = 'ْ'   # ْ
_TANWIN_F     = 'ً'   # ً
_TANWIN_D     = 'ٌ'   # ٌ
_TANWIN_K     = 'ٍ'   # ٍ
_TANWIN_CHARS = {_TANWIN_F, _TANWIN_D, _TANWIN_K}

# Phonological boundary markers exported by slot_engineering
_HAMZAT_AL_WASL_PATTERN = 'HAMZAT_AL_WASL'
_ALEF_FARQA_PATTERN     = 'ALEF_FARQA'


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
    gemination_type: Optional[str] = None       # GeminationType value from SGA contracts
    assimilation_gemination_type: Optional[str] = None  # solar assimilation provenance
    original_surface: Optional[str] = None     # provenance: original surface preserved


def _infer_kind_from_syllabify_dict(cell: dict) -> str:
    """
    Infer PhonologicalSlotKind from a syllabify() output dict.

    syllabify() dict fields used:
      status_at_close  — 'HAMZAT_AL_WASL' | 'ALEF_FARQA' | 'COMPLETE' | 'PREFIX' | 'BLOCK'
      close_reason     — 'HAMZAT_AL_WASL_SKIP' | 'ALEF_FARQA_BOUNDARY' | 'SATURATED' | ...
      pattern          — 'CV' | 'CVC' | 'CVV' | 'CVVC' | 'CVCC' | 'C' | ...
      surface          — actual surface string of the slot
      saturation_reason — free-text describing saturation
    """
    status      = cell.get("status_at_close", "")
    close_reason = cell.get("close_reason", "")
    pattern     = cell.get("pattern", "")
    surface     = cell.get("surface", "")

    # ── Phonological boundary markers ────────────────────────────────────
    if status == _HAMZAT_AL_WASL_PATTERN or close_reason == "HAMZAT_AL_WASL_SKIP":
        return "HAMZA"
    if status == _ALEF_FARQA_PATTERN or close_reason == "ALEF_FARQA_BOUNDARY":
        return "MADD"

    # ── Surface character detection ───────────────────────────────────────
    if _SHADDA_CHAR in surface:
        return "SHADDA"
    if _SUKUN_CHAR in surface:
        return "SUKUN"
    if any(c in surface for c in _TANWIN_CHARS):
        return "TANWIN"

    # ── Pattern inference ─────────────────────────────────────────────────
    # Long vowel syllable
    if "VV" in pattern:
        return "MADD"
    # Bare consonant (no vowel onset = sakin)
    if pattern == "C":
        return "SUKUN"
    # Standard CV-family syllables → classify by onset
    if pattern.startswith("CV"):
        return "CONSONANT"

    return "UNKNOWN"


def wrap_syllabify_output(raw_cells: list[dict]) -> tuple[PhonologicalSlot, ...]:
    """
    Wrap the existing list[dict] output from syllabify() into typed PhonologicalSlots.
    Does not recompute — adapter only.

    Handles two input shapes:
      1. syllabify() output dicts — keys: 'surface', 'pattern', 'gate',
         'status_at_close', 'close_reason', 'saturation_reason', 'violations'
      2. Phone-level test dicts — keys: 'character'|'letter'|'char', 'kind'|'type',
         'diacritic'|'haraka'|'vowel', 'gemination_type', 'assimilation_gemination_type',
         'original_surface'

    Priority for character:  letter > char > character > surface
    Priority for kind:       explicit 'kind'|'type' > inferred from syllabify fields
    """
    result = []
    for i, cell in enumerate(raw_cells):

        # ── Character: phone-level keys first, then syllabify surface ────
        char = (
            cell.get("letter")
            or cell.get("char")
            or cell.get("character")
            or cell.get("surface", "")
        )

        # ── Diacritic ────────────────────────────────────────────────────
        diac = cell.get("diacritic") or cell.get("haraka") or cell.get("vowel")

        # ── Kind: explicit takes priority, then infer from syllabify fields ──
        explicit_kind = cell.get("kind") or cell.get("type")
        if explicit_kind:
            kind_str = str(explicit_kind).upper()
        else:
            kind_str = _infer_kind_from_syllabify_dict(cell)

        try:
            kind = PhonologicalSlotKind(kind_str)
        except ValueError:
            kind = PhonologicalSlotKind.UNKNOWN

        # ── Gemination / assimilation provenance ─────────────────────────
        gemination_type = cell.get("gemination_type")
        assimilation_type = cell.get("assimilation_gemination_type")

        # Infer assimilation from saturation_reason if not explicit
        if not assimilation_type:
            sat_reason = str(cell.get("saturation_reason", "")).lower()
            if "assimilation" in sat_reason:
                assimilation_type = "ASSIMILATION_GEMINATION"

        # ── Original surface provenance ───────────────────────────────────
        orig_surface = cell.get("original_surface")

        result.append(PhonologicalSlot(
            position=i,
            character=char,
            kind=kind,
            diacritic=diac,
            gemination_type=gemination_type,
            assimilation_gemination_type=assimilation_type,
            original_surface=orig_surface,
        ))
    return tuple(result)


__all__ = [
    "PhonologicalSlotKind",
    "PhonologicalSlot",
    "wrap_syllabify_output",
]
