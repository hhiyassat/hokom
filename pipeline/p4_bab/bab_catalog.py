#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_bab/bab_catalog.py — تحميل catalog الأبواب والتحقق من صحته
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يحمّل data/bab/bab_catalog.json ويتحقق من صحته عند التحميل.
يرفع استثناءات صريحة عند:
  - bab_id مكرر
  - family غير معروفة
  - حقول مطلوبة ناقصة
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional


_CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "bab" / "bab_catalog.json"

_VALID_FAMILIES = frozenset({"MUJARRAD", "MAZID"})
_VALID_VOWELS   = frozenset({"a", "i", "u"})

_REQUIRED_FIELDS = frozenset({
    "bab_id", "family", "past_pattern", "imperfect_pattern",
    "past_wazn_id", "past_ayn_vowel", "imperfect_ayn_vowel",
    "required_surface_evidence", "verbal_only", "license_status",
    "evidence_rank",
})


class BabCatalogError(ValueError):
    """يُرفع عند خلل في schema catalog الأبواب."""
    pass


@dataclass(frozen=True)
class BabDefinition:
    """تعريف باب واحد من catalog."""
    bab_id:                    str
    family:                    str
    past_pattern:              str
    imperfect_pattern:         str
    past_wazn_id:              str
    past_ayn_vowel:            str      # 'a' | 'i' | 'u'
    imperfect_ayn_vowel:       str      # 'a' | 'i' | 'u'
    root_class_constraints:    tuple
    required_surface_evidence: tuple    # ('paired_paradigm',) | ('wazn_id',)
    verbal_only:               bool
    license_status:            str
    evidence_rank:             int
    example_verb:              Optional[str] = None


def _validate_and_parse(raw: dict) -> BabDefinition:
    """اعزِل حقول سجل واحد وتحقق من صحته."""
    missing = _REQUIRED_FIELDS - set(raw.keys())
    if missing:
        raise BabCatalogError(
            f"bab entry {raw.get('bab_id', '?')} missing fields: {sorted(missing)}"
        )
    family = raw["family"]
    if family not in _VALID_FAMILIES:
        raise BabCatalogError(
            f"bab_id={raw['bab_id']}: unknown family {family!r}. "
            f"Valid: {sorted(_VALID_FAMILIES)}"
        )
    for vowel_field in ("past_ayn_vowel", "imperfect_ayn_vowel"):
        v = raw[vowel_field]
        if v not in _VALID_VOWELS:
            raise BabCatalogError(
                f"bab_id={raw['bab_id']}: invalid {vowel_field}={v!r}. "
                f"Valid: {sorted(_VALID_VOWELS)}"
            )
    return BabDefinition(
        bab_id                    = raw["bab_id"],
        family                    = raw["family"],
        past_pattern              = raw["past_pattern"],
        imperfect_pattern         = raw["imperfect_pattern"],
        past_wazn_id              = raw["past_wazn_id"],
        past_ayn_vowel            = raw["past_ayn_vowel"],
        imperfect_ayn_vowel       = raw["imperfect_ayn_vowel"],
        root_class_constraints    = tuple(raw.get("root_class_constraints", [])),
        required_surface_evidence = tuple(raw.get("required_surface_evidence", [])),
        verbal_only               = bool(raw.get("verbal_only", True)),
        license_status            = raw["license_status"],
        evidence_rank             = int(raw["evidence_rank"]),
        example_verb              = raw.get("example_verb"),
    )


@lru_cache(maxsize=1)
def get_bab_catalog() -> tuple[BabDefinition, ...]:
    """حمّل catalog الأبواب وتحقق منه. مُخزَّن بـ lru_cache."""
    with open(_CATALOG_PATH, encoding="utf-8") as fh:
        data = json.load(fh)

    raw_entries = data.get("abwab", [])
    if not isinstance(raw_entries, list):
        raise BabCatalogError("bab_catalog.json: 'abwab' must be a list")

    seen_ids: set[str] = set()
    definitions: list[BabDefinition] = []

    for raw in raw_entries:
        entry = _validate_and_parse(raw)
        if entry.bab_id in seen_ids:
            raise BabCatalogError(f"Duplicate bab_id: {entry.bab_id!r}")
        seen_ids.add(entry.bab_id)
        definitions.append(entry)

    return tuple(definitions)


def lookup_by_wazn_id(past_wazn_id: str) -> list[BabDefinition]:
    """أعِد كل الأبواب التي تطابق past_wazn_id."""
    return [b for b in get_bab_catalog() if b.past_wazn_id == past_wazn_id]


def lookup_by_vowels(
    past_ayn_vowel: str,
    imperfect_ayn_vowel: str,
) -> list[BabDefinition]:
    """أعِد الأبواب التي تطابق الحركتين (ماضٍ + مضارع)."""
    return [
        b for b in get_bab_catalog()
        if b.past_ayn_vowel == past_ayn_vowel
        and b.imperfect_ayn_vowel == imperfect_ayn_vowel
    ]
