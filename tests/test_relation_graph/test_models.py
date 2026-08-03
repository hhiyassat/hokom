from __future__ import annotations
import os, sys
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from pipeline.relation_graph.models import RelationType, RelationClosureState, RelationCandidate

def test_relation_types_exist():
    assert RelationType.VERB_AGENT == "VERB_AGENT"
    assert RelationType.VERB_OBJECT == "VERB_OBJECT"
    assert RelationType.PRONOUN_REFERENCE == "PRONOUN_REFERENCE"

def test_relation_closure_states():
    assert RelationClosureState.RELATION_CLOSED == "RELATION_CLOSED"
    assert RelationClosureState.RELATION_DEFERRED == "RELATION_DEFERRED"

def test_relation_candidate_creation():
    r = RelationCandidate(
        relation_id="AD-R01",
        clause_id="AD-C04",
        source_token_index=17,
        target_token_index=14,
        source_surface="كَاتِبٌ",
        target_surface="يَكْتُبْ",
        relation_type=RelationType.VERB_AGENT,
        evidence_ids=("rafaa_inflection",),
        confidence_rank=3,
        contradictions=(),
        residuals=("agreement_unverified",),
        status=RelationClosureState.RELATION_DEFERRED,
    )
    assert r.relation_id == "AD-R01"
    assert r.relation_type == RelationType.VERB_AGENT
