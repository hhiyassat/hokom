from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.relation_graph.ayat_al_dayn_relations import build_gold_relations
from pipeline.relation_graph.models import RelationClosureState

def test_gold_relations_not_empty():
    rels = build_gold_relations()
    assert len(rels) >= 3

def test_gold_relations_have_evidence():
    rels = build_gold_relations()
    for r in rels:
        assert len(r.evidence_ids) > 0, f"Relation {r.relation_id} missing evidence"

def test_gold_relations_are_deferred_not_closed():
    """Gold relations should be DEFERRED — they are candidates, not proven closed."""
    rels = build_gold_relations()
    for r in rels:
        assert r.status in (
            RelationClosureState.RELATION_DEFERRED,
            RelationClosureState.RELATION_CANDIDATE if hasattr(RelationClosureState, 'RELATION_CANDIDATE') else RelationClosureState.RELATION_DEFERRED,
        ), f"Gold relation {r.relation_id} should be DEFERRED, is {r.status}"

def test_ad_r01_is_verb_agent():
    rels = build_gold_relations()
    from pipeline.relation_graph.models import RelationType
    ad_r01 = next((r for r in rels if r.relation_id == "AD-R01"), None)
    assert ad_r01 is not None
    assert ad_r01.relation_type == RelationType.VERB_AGENT
