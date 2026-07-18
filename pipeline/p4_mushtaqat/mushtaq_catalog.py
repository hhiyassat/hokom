#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_mushtaqat/mushtaq_catalog.py — تحميل catalog المشتقات والتحقق من صحته
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يحمّل data/mushtaqat/mushtaq_catalog.json ويتحقق من صحته عند التحميل.
يرفع استثناءات صريحة عند:
  - entry_id مكرر
  - mushtaq_type غير معروف
  - حقول مطلوبة ناقصة
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pipeline.p4_mushtaqat.models import MUSHTAQ_TYPES


_CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "mushtaqat" / "mushtaq_catalog.json"

_VALID_SOURCE_TYPES = frozenset({
    "STRUCTURAL_INFERENCE",
    "LEXICAL_LICENSED",
    "SAMI3I_REQUIRED",
})

_VALID_TRANSITIVITY = frozenset({
    "TRANSITIVE",
    "INTRANSITIVE",
    "UNCONSTRAINED",
    "UNKNOWN",
})

_REQUIRED_FIELDS = frozenset({
    "entry_id",
    "mushtaq_type",
    "wazn_family",
    "pattern",
    "source_type",
    "transitivity_constraint",
    "verbal_only",
    "license_status",
})


class MushtaqCatalogError(ValueError):
    """يُرفع عند خلل في schema catalog المشتقات."""
    pass


@dataclass(frozen=True)
class MushtaqDefinition:
    """تعريف مشتق واحد من catalog."""
    entry_id:                str
    mushtaq_type:            str
    wazn_family:             str
    pattern:                 str
    source_type:             str
    transitivity_constraint: str
    verbal_only:             bool
    license_status:          str
    evidence_required:       tuple
    notes:                   str


def _validate_and_parse(raw: dict) -> MushtaqDefinition:
    """اعزِل حقول سجل واحد وتحقق من صحته."""
    missing = _REQUIRED_FIELDS - set(raw.keys())
    if missing:
        raise MushtaqCatalogError(
            f"mushtaq entry {raw.get('entry_id', '?')} missing fields: {sorted(missing)}"
        )

    mushtaq_type = raw["mushtaq_type"]
    if mushtaq_type not in MUSHTAQ_TYPES:
        raise MushtaqCatalogError(
            f"entry_id={raw['entry_id']}: unknown mushtaq_type {mushtaq_type!r}. "
            f"Valid: {sorted(MUSHTAQ_TYPES)}"
        )

    source_type = raw["source_type"]
    if source_type not in _VALID_SOURCE_TYPES:
        raise MushtaqCatalogError(
            f"entry_id={raw['entry_id']}: unknown source_type {source_type!r}."
        )

    transitivity = raw["transitivity_constraint"]
    if transitivity not in _VALID_TRANSITIVITY:
        raise MushtaqCatalogError(
            f"entry_id={raw['entry_id']}: unknown transitivity_constraint {transitivity!r}."
        )

    return MushtaqDefinition(
        entry_id                = raw["entry_id"],
        mushtaq_type            = mushtaq_type,
        wazn_family             = raw["wazn_family"],
        pattern                 = raw["pattern"],
        source_type             = source_type,
        transitivity_constraint = transitivity,
        verbal_only             = bool(raw.get("verbal_only", True)),
        license_status          = raw.get("license_status", "ACTIVE"),
        evidence_required       = tuple(raw.get("evidence_required", [])),
        notes                   = raw.get("notes", ""),
    )


@lru_cache(maxsize=1)
def load_mushtaq_catalog() -> tuple:
    """
    حمّل catalog المشتقات وتحقق منه. مُخزَّن مؤقتًا بعد أول استدعاء.

    Returns:
        tuple[MushtaqDefinition, ...] — جميع التعريفات النشطة.

    Raises:
        MushtaqCatalogError: عند أي خلل في البيانات.
        FileNotFoundError: إن لم يوجد ملف catalog.
    """
    try:
        raw_data = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Mushtaq catalog not found: {_CATALOG_PATH}")

    # الـ catalog هو array مباشر (لا مغلّف)
    if isinstance(raw_data, list):
        entries_raw = raw_data
    elif isinstance(raw_data, dict):
        entries_raw = raw_data.get("mushtaqat", raw_data.get("entries", []))
    else:
        raise MushtaqCatalogError("mushtaq_catalog.json must be a JSON array or object with 'mushtaqat' key")

    seen_ids: set = set()
    result: list = []

    for raw in entries_raw:
        defn = _validate_and_parse(raw)
        if defn.entry_id in seen_ids:
            raise MushtaqCatalogError(
                f"Duplicate entry_id in mushtaq catalog: {defn.entry_id!r}"
            )
        seen_ids.add(defn.entry_id)

        if defn.license_status != "ACTIVE":
            continue  # تجاهل المدخلات المُعطَّلة

        result.append(defn)

    return tuple(result)


# ── فهارس للبحث السريع ──────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _index_by_type_and_family() -> dict:
    """
    فهرس: (mushtaq_type, wazn_family) → tuple[MushtaqDefinition, ...]
    """
    index: dict = {}
    for defn in load_mushtaq_catalog():
        key = (defn.mushtaq_type, defn.wazn_family)
        if key not in index:
            index[key] = []
        index[key].append(defn)
    return {k: tuple(v) for k, v in index.items()}


@lru_cache(maxsize=1)
def _index_by_wazn_family() -> dict:
    """فهرس: wazn_family → tuple[MushtaqDefinition, ...] (جميع أنواع المشتقات)."""
    index: dict = {}
    for defn in load_mushtaq_catalog():
        if defn.wazn_family not in index:
            index[defn.wazn_family] = []
        index[defn.wazn_family].append(defn)
    return {k: tuple(v) for k, v in index.items()}


def get_mushtaq_definitions(mushtaq_type: str, wazn_family: str) -> tuple:
    """
    أعِد تعريفات المشتق بالنوع وعائلة الوزن.

    Returns:
        tuple[MushtaqDefinition, ...] — قد تكون فارغة إن لم يُعثر على مطابقة.
    """
    return _index_by_type_and_family().get((mushtaq_type, wazn_family), ())


def get_all_for_wazn_family(wazn_family: str) -> tuple:
    """
    أعِد جميع تعريفات المشتقات لعائلة وزن معينة.

    Returns:
        tuple[MushtaqDefinition, ...] — قد تكون فارغة.
    """
    return _index_by_wazn_family().get(wazn_family, ())
