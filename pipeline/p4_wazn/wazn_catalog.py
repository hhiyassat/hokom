#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/wazn_catalog.py — تحميل catalog الأوزان والتحقق من صحته
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يحمّل data/wazn/wazn_catalog.json — قائمة محدودة مرخّصة من الأوزان لإثبات
العقد البنيوي في Phase 4A (ليست catalog شاملًا للعربية).

كل سجل يعرّف:
  wazn_id, pattern, root_arity, family, root_slots, licensed_ziyadah_slots,
  licensed_shadda_behavior, licensed_weak_operations, applicable_surface_classes,
  evidence_rank, source, template

template = تسلسل خانات المحاذاة المرخّصة؛ كل خانة إمّا علامة جذر
(FA/AIN/LAM/FOURTH) أو زيادة مرخّصة (ZIYADAH بحرف صريح أو تضعيف خانة جذر).

يُرفع WaznProjectionContractError عند أي خلل في schema (فشل صريح لا صامت).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .models import RootSlot, WaznProjectionContractError


# مسار الـcatalog — نسبي إلى جذر المستودع، لا مسار مطلق.
#   pipeline/p4_wazn/wazn_catalog.py → parents[2] = جذر المستودع.
_CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "wazn" / "wazn_catalog.json"

_VALID_ROLES  = frozenset({"FA", "AIN", "LAM", "FOURTH", "ZIYADAH"})
_ROOT_ROLES   = frozenset({"FA", "AIN", "LAM", "FOURTH"})
_VALID_VOWELS = frozenset({"FATHA", "DAMMA", "KASRA", "SUKUN", "FINAL", "MATER", "ANY"})
_SUPPORTED_ARITY = frozenset({3, 4})

# ترتيب خانات الجذر حسب الرتبة (لاستخراج هوية الحرف من canonical_root).
_ROOT_ROLE_INDEX = {"FA": 0, "AIN": 1, "LAM": 2, "FOURTH": 3}
_ROLE_TO_SLOT    = {"FA": RootSlot.FA, "AIN": RootSlot.AIN,
                    "LAM": RootSlot.LAM, "FOURTH": RootSlot.FOURTH}


@dataclass(frozen=True)
class TemplateCell:
    """خانة واحدة في قالب الوزن.

    role         : FA/AIN/LAM/FOURTH (خانة جذر) أو ZIYADAH.
    vowel        : الحركة المتوقّعة (FINAL=إعرابية تُهمَل، MATER=حرف مدّ).
    letter       : الحرف الصريح لخانة ZIYADAH الحرفية (وإلا None).
    geminate_of  : لخانة ZIYADAH تضعيفية: اسم دور الجذر الذي تضاعفه (وإلا None).
    """
    role:        str
    vowel:       str
    letter:      Optional[str] = None
    geminate_of: Optional[str] = None

    @property
    def is_root(self) -> bool:
        return self.role in _ROOT_ROLES

    @property
    def root_index(self) -> Optional[int]:
        return _ROOT_ROLE_INDEX.get(self.role)

    @property
    def root_slot(self) -> Optional[RootSlot]:
        return _ROLE_TO_SLOT.get(self.role)


@dataclass(frozen=True)
class WaznDefinition:
    wazn_id:                    str
    pattern:                    str
    root_arity:                 int
    family:                     str
    applicable_surface_classes: tuple
    root_slots:                 tuple
    licensed_ziyadah_slots:     tuple
    licensed_shadda_behavior:   tuple
    licensed_weak_operations:   tuple
    evidence_rank:              int
    source:                     str
    template:                   tuple  # tuple[TemplateCell, ...]

    def permits_geminate_root_idghaam(self) -> bool:
        return "geminate_root_idghaam" in self.licensed_shadda_behavior


# ══════════════════════════════════════════════════════════════════════════════
# التحقق من صحة السجل
# ══════════════════════════════════════════════════════════════════════════════

def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WaznProjectionContractError(f"invalid wazn catalog schema: {message}")


def _build_definition(raw: dict) -> WaznDefinition:
    for key in ("wazn_id", "pattern", "root_arity", "family",
                "applicable_surface_classes", "root_slots",
                "licensed_ziyadah_slots", "licensed_shadda_behavior",
                "licensed_weak_operations", "evidence_rank", "source", "template"):
        _require(key in raw, f"missing field {key!r} in {raw.get('wazn_id', raw)!r}")

    wazn_id = raw["wazn_id"]
    arity   = raw["root_arity"]
    _require(isinstance(arity, int) and arity in _SUPPORTED_ARITY,
             f"unsupported root_arity {arity!r} in {wazn_id!r}")

    template_raw = raw["template"]
    _require(isinstance(template_raw, list) and len(template_raw) > 0,
             f"empty/invalid template in {wazn_id!r}")

    cells: list[TemplateCell] = []
    root_roles_seen: list[str] = []
    for cell in template_raw:
        role = cell.get("role")
        _require(role in _VALID_ROLES, f"bad cell role {role!r} in {wazn_id!r}")
        vowel = cell.get("vowel", "ANY")
        _require(vowel in _VALID_VOWELS, f"bad vowel {vowel!r} in {wazn_id!r}")
        letter      = cell.get("letter")
        geminate_of = cell.get("geminate_of")
        if role == "ZIYADAH":
            _require(bool(letter) ^ bool(geminate_of),
                     f"ziyadah cell needs exactly one of letter/geminate_of in {wazn_id!r}")
            if geminate_of is not None:
                _require(geminate_of in _ROOT_ROLES,
                         f"geminate_of must name a root role in {wazn_id!r}")
        else:
            root_roles_seen.append(role)
        cells.append(TemplateCell(role=role, vowel=vowel,
                                  letter=letter, geminate_of=geminate_of))

    # عدد خانات الجذر في القالب يجب أن يساوي root_arity وبالترتيب الصحيح.
    expected_roles = ["FA", "AIN", "LAM", "FOURTH"][:arity]
    _require(root_roles_seen == expected_roles,
             f"root roles {root_roles_seen} != expected {expected_roles} in {wazn_id!r}")

    return WaznDefinition(
        wazn_id                    = wazn_id,
        pattern                    = raw["pattern"],
        root_arity                 = arity,
        family                     = raw["family"],
        applicable_surface_classes = tuple(raw["applicable_surface_classes"]),
        root_slots                 = tuple(raw["root_slots"]),
        licensed_ziyadah_slots     = tuple(raw["licensed_ziyadah_slots"]),
        licensed_shadda_behavior   = tuple(raw["licensed_shadda_behavior"]),
        licensed_weak_operations   = tuple(raw["licensed_weak_operations"]),
        evidence_rank              = int(raw["evidence_rank"]),
        source                     = raw["source"],
        template                   = tuple(cells),
    )


# ══════════════════════════════════════════════════════════════════════════════
# التحميل (مع تخزين مؤقّت)
# ══════════════════════════════════════════════════════════════════════════════

_CACHE: Optional[tuple] = None


def load_catalog(path: Optional[Path] = None) -> tuple:
    """حمّل ووثّق catalog الأوزان → tuple[WaznDefinition, ...]. لا تخزين مؤقّت هنا."""
    p = path if path is not None else _CATALOG_PATH
    _require(p.exists(), f"catalog file not found at {p!s}")
    with open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    _require(isinstance(data, dict) and "awzan" in data, "top-level 'awzan' missing")
    awzan = data["awzan"]
    _require(isinstance(awzan, list) and len(awzan) > 0, "'awzan' must be a non-empty list")

    defs = tuple(_build_definition(r) for r in awzan)

    ids = [d.wazn_id for d in defs]
    _require(len(ids) == len(set(ids)), f"duplicate wazn_id in catalog: {ids}")
    return defs


def get_catalog() -> tuple:
    """احصل على catalog الأوزان (يُحمَّل مرّة ويُخزَّن)."""
    global _CACHE
    if _CACHE is None:
        _CACHE = load_catalog()
    return _CACHE
