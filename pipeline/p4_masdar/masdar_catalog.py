#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_masdar/masdar_catalog.py — تحميل catalog المصادر والتحقق من صحته
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يحمّل data/masdar/masdar_catalog.json ويتحقق من صحته عند التحميل.
يرفع استثناءات صريحة عند:
  - masdar_id مكرر
  - family غير معروفة
  - حقول مطلوبة ناقصة
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional


_CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "masdar" / "masdar_catalog.json"

_VALID_FAMILIES     = frozenset({"MUJARRAD", "MAZID"})
_VALID_SOURCE_TYPES = frozenset({"LEXICAL_LICENSED", "STRUCTURAL_INFERENCE", "SAMI3I_REQUIRED"})

_REQUIRED_FIELDS = frozenset({
    "masdar_id", "family", "source_type",
    "verbal_only", "license_status", "evidence_required",
})


class MasdarCatalogError(ValueError):
    """يُرفع عند خلل في schema catalog المصادر."""
    pass


@dataclass(frozen=True)
class MasdarDefinition:
    """تعريف مصدر واحد من catalog."""
    masdar_id:         str
    bab_id:            Optional[str]
    wazn_id:           Optional[str]
    family:            str
    masdar_pattern:    Optional[str]
    source_type:       str
    verbal_only:       bool
    license_status:    str
    evidence_required: tuple
    notes:             str

    @property
    def is_sami3i(self) -> bool:
        return self.source_type == "SAMI3I_REQUIRED"

    @property
    def is_structural(self) -> bool:
        return self.source_type == "STRUCTURAL_INFERENCE"

    @property
    def is_lexical(self) -> bool:
        return self.source_type == "LEXICAL_LICENSED"


def _validate_and_parse(raw: dict) -> MasdarDefinition:
    """اعزِل حقول سجل واحد وتحقق من صحته."""
    missing = _REQUIRED_FIELDS - set(raw.keys())
    if missing:
        raise MasdarCatalogError(
            f"masdar entry {raw.get('masdar_id', '?')} missing fields: {sorted(missing)}"
        )
    family = raw["family"]
    if family not in _VALID_FAMILIES:
        raise MasdarCatalogError(
            f"masdar_id={raw['masdar_id']}: unknown family {family!r}. "
            f"Valid: {sorted(_VALID_FAMILIES)}"
        )
    source_type = raw["source_type"]
    if source_type not in _VALID_SOURCE_TYPES:
        raise MasdarCatalogError(
            f"masdar_id={raw['masdar_id']}: unknown source_type {source_type!r}. "
            f"Valid: {sorted(_VALID_SOURCE_TYPES)}"
        )
    return MasdarDefinition(
        masdar_id         = raw["masdar_id"],
        bab_id            = raw.get("bab_id"),
        wazn_id           = raw.get("wazn_id"),
        family            = family,
        masdar_pattern    = raw.get("masdar_pattern"),
        source_type       = source_type,
        verbal_only       = bool(raw.get("verbal_only", True)),
        license_status    = raw.get("license_status", "ACTIVE"),
        evidence_required = tuple(raw.get("evidence_required", [])),
        notes             = raw.get("notes", ""),
    )


@lru_cache(maxsize=1)
def load_masdar_catalog() -> dict[str, MasdarDefinition]:
    """
    حمّل catalog المصادر وتحقق منه. مُخزَّن مؤقتًا بعد أول استدعاء.

    Returns:
        dict[masdar_id → MasdarDefinition]

    Raises:
        MasdarCatalogError: عند أي خلل في البيانات.
        FileNotFoundError: إن لم يوجد ملف catalog.
    """
    try:
        raw_data = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Masdar catalog not found: {_CATALOG_PATH}")

    entries = raw_data.get("masadir", [])
    catalog: dict[str, MasdarDefinition] = {}

    for raw in entries:
        defn = _validate_and_parse(raw)
        if defn.masdar_id in catalog:
            raise MasdarCatalogError(
                f"Duplicate masdar_id in catalog: {defn.masdar_id!r}"
            )
        if defn.license_status != "ACTIVE":
            continue   # تجاهل المدخلات المُعطَّلة
        catalog[defn.masdar_id] = defn

    return catalog


# ── فهارس للبحث السريع ──────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _by_bab_id() -> dict[str, MasdarDefinition]:
    """فهرس: bab_id → MasdarDefinition (للمدخلات ذات bab_id)."""
    return {
        defn.bab_id: defn
        for defn in load_masdar_catalog().values()
        if defn.bab_id is not None
    }


@lru_cache(maxsize=1)
def _by_wazn_id() -> dict[str, MasdarDefinition]:
    """فهرس: wazn_id → MasdarDefinition (للمدخلات ذات wazn_id)."""
    result: dict[str, MasdarDefinition] = {}
    for defn in load_masdar_catalog().values():
        if defn.wazn_id is not None and defn.wazn_id not in result:
            result[defn.wazn_id] = defn
    return result


def get_masdar_by_bab(bab_id: str) -> Optional[MasdarDefinition]:
    """ابحث عن تعريف المصدر بواسطة bab_id."""
    return _by_bab_id().get(bab_id)


def get_masdar_by_wazn(wazn_id: str) -> Optional[MasdarDefinition]:
    """ابحث عن تعريف المصدر بواسطة wazn_id (بديل عند غياب bab_id)."""
    return _by_wazn_id().get(wazn_id)
