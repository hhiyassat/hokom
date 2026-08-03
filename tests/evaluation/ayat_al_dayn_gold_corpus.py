"""
ayat_al_dayn_gold_corpus.py — Evaluation corpus for Ayat al-Dayn.

EVALUATION USE ONLY. Not imported by production code.
Production code must NOT depend on this module.

Gold data is used ONLY to:
  1. Compare production output AFTER execution
  2. Build test fixtures for unit tests
  3. Document the expected structural analysis

Production engines must derive their output independently.
"""
from __future__ import annotations

# ================================================================
# GOLD CLAUSE SEGMENTATION — structural analysis
# Based on explicit Arabic grammar: operators, imperatives, conditionals
# NOT derived by running the engine — this is the evaluation target
# ================================================================
GOLD_CLAUSES: tuple[dict, ...] = (
    {"clause_id": "AD-C01", "token_start": 1,  "token_end": 4,
     "surface": "يَا أَيُّهَا الَّذِينَ آمَنُوا",
     "operators": ("يَا",), "main_predicate_candidates": ("آمَنُوا",),
     "boundary_type": "VOCATIVE", "status": "CANDIDATE"},
    {"clause_id": "AD-C02", "token_start": 5,  "token_end": 11,
     "surface": "إِذَا تَدَايَنْتُمْ بِدَيْنٍ إِلَى أَجَلٍ مُّسَمًّى",
     "operators": ("إِذَا",), "main_predicate_candidates": ("تَدَايَنْتُمْ",),
     "boundary_type": "CONDITIONAL", "status": "CANDIDATE"},
    {"clause_id": "AD-C03", "token_start": 12, "token_end": 13,
     "surface": "فَاكْتُبُوهُ",
     "operators": ("فَ",), "main_predicate_candidates": ("اكْتُبُوهُ",),
     "boundary_type": "CONJUNCTION", "status": "CANDIDATE"},
    {"clause_id": "AD-C04", "token_start": 14, "token_end": 18,
     "surface": "وَلْيَكْتُبْ بَيْنَكُمْ كَاتِبٌ بِالْعَدْلِ",
     "operators": ("وَ",), "main_predicate_candidates": ("يَكْتُبْ",),
     "boundary_type": "CONJUNCTION", "status": "CANDIDATE"},
    {"clause_id": "AD-C05", "token_start": 19, "token_end": 23,
     "surface": "وَلَا يَأْبَ كَاتِبٌ أَنْ يَكْتُبَ",
     "operators": ("وَ",), "main_predicate_candidates": ("يَأْبَ",),
     "boundary_type": "CONJUNCTION", "status": "CANDIDATE"},
    {"clause_id": "AD-C06", "token_start": 28, "token_end": 33,
     "surface": "وَلْيُمْلِلِ الَّذِي عَلَيْهِ الْحَقُّ",
     "operators": ("وَ",), "main_predicate_candidates": ("يُمْلِلِ",),
     "boundary_type": "CONJUNCTION", "status": "CANDIDATE"},
    {"clause_id": "AD-C07", "token_start": 50, "token_end": 54,
     "surface": "وَاسْتَشْهِدُوا شَهِيدَيْنِ مِنْ رِجَالِكُمْ",
     "operators": ("وَ",), "main_predicate_candidates": ("اسْتَشْهِدُوا",),
     "boundary_type": "CONJUNCTION", "status": "CANDIDATE"},
    {"clause_id": "AD-C08", "token_start": 67, "token_end": 70,
     "surface": "وَأَشْهِدُوا إِذَا تَبَايَعْتُمْ",
     "operators": ("وَ",), "main_predicate_candidates": ("أَشْهِدُوا",),
     "boundary_type": "CONJUNCTION", "status": "CANDIDATE"},
)

# ================================================================
# GOLD RELATION CANDIDATES — structural analysis only
# EVALUATION USE ONLY — compare AFTER engine produces its output
# ================================================================
GOLD_RELATIONS: tuple[dict, ...] = (
    {"relation_id": "AD-R01", "clause_id": "AD-C04",
     "source_token_index": 17, "target_token_index": 14,
     "source_surface": "كَاتِبٌ", "target_surface": "يَكْتُبْ",
     "relation_type": "VERB_AGENT",
     "evidence_ids": ("rafaa_inflection:katibun", "verbal_agreement:3sg_m"),
     "confidence_rank": 3, "residuals": ("agreement_gender_unverified",),
     "status": "RELATION_DEFERRED"},
    {"relation_id": "AD-R02", "clause_id": "AD-C04",
     "source_token_index": 18, "target_token_index": 14,
     "source_surface": "بِالْعَدْلِ", "target_surface": "يَكْتُبْ",
     "relation_type": "PREPOSITIONAL_ATTACHMENT",
     "evidence_ids": ("ba_preposition:bil_adl",),
     "confidence_rank": 3, "residuals": (), "status": "RELATION_DEFERRED"},
    {"relation_id": "AD-R03", "clause_id": "AD-C06",
     "source_token_index": 32, "target_token_index": 30,
     "source_surface": "الْحَقُّ", "target_surface": "عَلَيْهِ",
     "relation_type": "PREPOSITIONAL_ATTACHMENT",
     "evidence_ids": ("rfaa_inflection:alhaqqu",),
     "confidence_rank": 3, "residuals": ("subject_of_relative_clause_unverified",),
     "status": "RELATION_DEFERRED"},
    {"relation_id": "AD-R04", "clause_id": "AD-C07",
     "source_token_index": 52, "target_token_index": 50,
     "source_surface": "شَهِيدَيْنِ", "target_surface": "اسْتَشْهِدُوا",
     "relation_type": "VERB_OBJECT",
     "evidence_ids": ("nasb_inflection:shahidayni",),
     "confidence_rank": 3, "residuals": (), "status": "RELATION_DEFERRED"},
)


def get_gold_clauses() -> list[dict]:
    return list(GOLD_CLAUSES)


def get_gold_relations() -> list[dict]:
    return list(GOLD_RELATIONS)
