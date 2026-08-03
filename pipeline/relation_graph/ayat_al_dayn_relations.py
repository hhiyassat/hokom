"""
ayat_al_dayn_relations.py — Gold structural relation candidates for Ayat al-Dayn.

EVALUATION DATA — NOT for use by production engines.
This file contains hard-coded expected relation candidates based on grammatical
structural analysis. Production engines must NOT read this file at runtime to
derive their outputs — they must produce results independently.

Evaluation workflow:
  1. Run the production relation engine independently.
  2. Compare its output AFTER execution against get_gold_relations() here,
     or against tests/evaluation/ayat_al_dayn_gold_corpus.GOLD_RELATIONS.

This file is kept for backward compatibility with tests that import
build_gold_relations() directly. New tests should import from
tests/evaluation/ayat_al_dayn_gold_corpus instead.
"""
from __future__ import annotations
from .models import RelationCandidate, RelationType, RelationClosureState

# Gold structural relation candidates — based on explicit grammatical evidence
# NOT derived from word order alone; NOT free semantic inference
# EVALUATION USE ONLY — production engines must not read these at runtime
AYAT_AL_DAYN_GOLD_RELATIONS: tuple[dict, ...] = (
    {
        "relation_id": "AD-R01",
        "clause_id": "AD-C04",
        "source_token_index": 17,   # كَاتِبٌ (agent)
        "target_token_index": 14,   # يَكْتُبْ (verb)
        "source_surface": "كَاتِبٌ",
        "target_surface": "يَكْتُبْ",
        "relation_type": "VERB_AGENT",
        "evidence_ids": ("rafaa_inflection:katibun", "verbal_agreement:3sg_m"),
        "confidence_rank": 3,
        "residuals": ("agreement_gender_unverified",),
        "status": "RELATION_DEFERRED",
    },
    {
        "relation_id": "AD-R02",
        "clause_id": "AD-C04",
        "source_token_index": 18,   # بِالْعَدْلِ
        "target_token_index": 14,   # يَكْتُبْ
        "source_surface": "بِالْعَدْلِ",
        "target_surface": "يَكْتُبْ",
        "relation_type": "PREPOSITIONAL_ATTACHMENT",
        "evidence_ids": ("ba_preposition:bil_adl",),
        "confidence_rank": 3,
        "residuals": (),
        "status": "RELATION_DEFERRED",
    },
    {
        "relation_id": "AD-R03",
        "clause_id": "AD-C06",
        "source_token_index": 32,   # الْحَقُّ
        "target_token_index": 30,   # عَلَيْهِ
        "source_surface": "الْحَقُّ",
        "target_surface": "عَلَيْهِ",
        "relation_type": "PREPOSITIONAL_ATTACHMENT",
        "evidence_ids": ("rfaa_inflection:alhaqqu",),
        "confidence_rank": 3,
        "residuals": ("subject_of_relative_clause_unverified",),
        "status": "RELATION_DEFERRED",
    },
    {
        "relation_id": "AD-R04",
        "clause_id": "AD-C07",
        "source_token_index": 52,   # شَهِيدَيْنِ
        "target_token_index": 50,   # اسْتَشْهِدُوا
        "source_surface": "شَهِيدَيْنِ",
        "target_surface": "اسْتَشْهِدُوا",
        "relation_type": "VERB_OBJECT",
        "evidence_ids": ("nasb_inflection:shahidayni",),
        "confidence_rank": 3,
        "residuals": (),
        "status": "RELATION_DEFERRED",
    },
)


def build_gold_relations() -> list[RelationCandidate]:
    """
    Build RelationCandidate list from gold corpus.

    EVALUATION USE ONLY — kept for backward compatibility with tests.
    New tests should import from tests/evaluation/ayat_al_dayn_gold_corpus.
    Production engines must not call this function to derive their outputs.
    """
    relations = []
    for r in AYAT_AL_DAYN_GOLD_RELATIONS:
        relations.append(RelationCandidate(
            relation_id=r["relation_id"],
            clause_id=r["clause_id"],
            source_token_index=r["source_token_index"],
            target_token_index=r["target_token_index"],
            source_surface=r["source_surface"],
            target_surface=r["target_surface"],
            relation_type=RelationType(r["relation_type"]),
            evidence_ids=tuple(r.get("evidence_ids", ())),
            confidence_rank=r.get("confidence_rank", 2),
            contradictions=tuple(r.get("contradictions", ())),
            residuals=tuple(r.get("residuals", ())),
            status=RelationClosureState(r.get("status", "RELATION_DEFERRED")),
        ))
    return relations
