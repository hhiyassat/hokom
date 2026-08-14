#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
canonical_bridge/government_producer.py — native cross-token GOVERNMENT
(عامل/معمول) evidence producer.

Produces REAL sentence-level government evidence from Hokom-owned facts, WITHOUT
any answer oracle. The first and canonical family implemented is jar→majrur
(حرف الجر → الاسم المجرور): a preposition governs the immediately following token
in the genitive.

Preposition detection uses the canonical mabniyat catalog
(`mabniyat_catalog_split_vocalized.csv`, `lexical_class == PREPOSITION`) — a
linguistic KNOWLEDGE BASE (the closed class of حروف الجر), NOT a per-sentence
answer table. This producer NEVER reads `ayat_al_dayn.build_gold_relations`
(that is COMPARISON_ONLY / a gold oracle).

Output feeds the existing canonical pipeline contract:
  * word-level P8 evidence  → WordInput.hokom_evidence_by_stage["P8_AMIL_MAMUL"]
      keys: amil_role ("amil"|"mamul"), amil_unit_id, unit_count, relation_class
  * sentence-level evidence → SentenceInput.sentence_hokom_evidence
      P9_SENTENCE_GEOMETRY: {amil_mamul_units, adjacency_relation}
      P10_RELATION_GEOMETRY: {relations}

Deterministic (catalog-driven, content order preserved; no randomness). Honest:
emits government evidence ONLY where a preposition is genuinely detected AND a
governed token follows; otherwise it emits nothing (the pipeline DEFERs).
"""
from __future__ import annotations

import csv
import os
import unicodedata
from typing import Any

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MABNIYAT_CSV = os.path.join(_REPO, "mabniyat_catalog_split_vocalized.csv")

RELATION_JAR_MAJRUR = "jar_majrur"
_DOMAIN = "linguistic_structural"


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").strip())


def _skeleton(s: str) -> str:
    """Diacritic-insensitive consonant skeleton (drop harakat, tatweel, spaces)."""
    d = unicodedata.normalize("NFD", _nfc(s))
    return "".join(c for c in d if not unicodedata.combining(c)
                   and c not in ("ـ", " "))


def load_preposition_skeletons(path: str = _MABNIYAT_CSV) -> frozenset[str]:
    """The closed class of حروف الجر from the canonical mabniyat catalog."""
    out: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("lexical_class") == "PREPOSITION":
                for col in ("surface_vocalized", "surface_bare"):
                    sk = _skeleton(row.get(col, ""))
                    if sk:
                        out.add(sk)
    return frozenset(out)


_PREP_SKELETONS: frozenset[str] | None = None


def _preps() -> frozenset[str]:
    global _PREP_SKELETONS
    if _PREP_SKELETONS is None:
        _PREP_SKELETONS = load_preposition_skeletons()
    return _PREP_SKELETONS


def is_preposition(surface: str) -> bool:
    """True iff the (standalone) token is a حرف جر in the canonical closed class."""
    return _skeleton(surface) in _preps()


def produce_government(tokens: list[str]) -> dict[str, Any]:
    """Native jar→majrur government evidence for a token sequence.

    Returns:
      word_evidence   — dict[int, dict]  per-word hokom_evidence_by_stage fragment
      sentence_evidence — dict            SentenceInput.sentence_hokom_evidence
      relations       — list[dict]        typed jar→majrur relations
      government_count — int              number of certified-eligible relations
    """
    n = len(tokens)
    word_evidence: dict[int, dict[str, Any]] = {}
    units: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []

    for i, tok in enumerate(tokens):
        if is_preposition(tok) and i + 1 < n and not is_preposition(tokens[i + 1]):
            amil_id, mamul_id = f"jar_w{i}", f"majrur_w{i + 1}"
            # word-level P8 evidence for the governing حرف الجر and the governed اسم
            word_evidence.setdefault(i, {})["P8_AMIL_MAMUL"] = {
                "amil_role": "amil", "amil_unit_id": amil_id,
                "unit_count": 2, "relation_class": RELATION_JAR_MAJRUR,
                "domain": _DOMAIN,
            }
            word_evidence.setdefault(i + 1, {})["P8_AMIL_MAMUL"] = {
                "amil_role": "mamul", "amil_unit_id": mamul_id,
                "unit_count": 2, "relation_class": RELATION_JAR_MAJRUR,
                "domain": _DOMAIN,
            }
            units.append({"unit_id": amil_id, "word_index": i,
                          "role": "amil", "candidate_id": amil_id})
            units.append({"unit_id": mamul_id, "word_index": i + 1,
                          "role": "mamul", "candidate_id": mamul_id})
            relations.append({"relation_type": RELATION_JAR_MAJRUR,
                              "amil_unit_id": amil_id, "mamul_unit_id": mamul_id,
                              "amil_index": i, "mamul_index": i + 1})

    sentence_evidence: dict[str, Any] = {}
    if units:
        sentence_evidence["P9_SENTENCE_GEOMETRY"] = {
            "amil_mamul_units": units, "adjacency_relation": "established"}
        sentence_evidence["P10_RELATION_GEOMETRY"] = {"relations": relations}
        # P11 irab: a noun governed by a حرف جر is genitive (مجرور). This is a
        # real irab POSITION (a possibility), not a final judgment — exactly what
        # the candidate-only P11 stage consumes. One position per majrur token.
        irab_positions = [
            {"word_id": r["mamul_index"], "possible_cases": ["genitive"],
             "governed_by": r["amil_unit_id"], "relation_class": RELATION_JAR_MAJRUR}
            for r in relations
        ]
        sentence_evidence["P11_IRAB_GEOMETRY"] = {"irab_positions": irab_positions}
        # P12 ifadah is intentionally NOT emitted: a bare جار ومجرور phrase is not
        # a complete utterance (لا تُفيد فائدة يحسن السكوت عليها) → honest DEFER.

    return {
        "word_evidence": word_evidence,
        "sentence_evidence": sentence_evidence,
        "relations": relations,
        "government_count": len(relations),
    }
