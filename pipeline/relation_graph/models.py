from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RelationType(str, Enum):
    VERB_AGENT = "VERB_AGENT"
    VERB_OBJECT = "VERB_OBJECT"
    PREDICATE_SUBJECT = "PREDICATE_SUBJECT"
    PREPOSITIONAL_ATTACHMENT = "PREPOSITIONAL_ATTACHMENT"
    ATTRIBUTE = "ATTRIBUTE"
    GENITIVE_ATTACHMENT = "GENITIVE_ATTACHMENT"
    CONJUNCTION = "CONJUNCTION"
    CONDITION = "CONDITION"
    CONDITION_RESULT = "CONDITION_RESULT"
    RELATIVE_ATTACHMENT = "RELATIVE_ATTACHMENT"
    PRONOUN_REFERENCE = "PRONOUN_REFERENCE"
    COMMAND_SCOPE = "COMMAND_SCOPE"
    NEGATION_SCOPE = "NEGATION_SCOPE"
    TEMPORAL_ATTACHMENT = "TEMPORAL_ATTACHMENT"


class RelationClosureState(str, Enum):
    RELATION_CLOSED = "RELATION_CLOSED"
    RELATION_PERFORATED = "RELATION_PERFORATED"
    RELATION_DEFERRED = "RELATION_DEFERRED"
    RELATION_BLOCKED = "RELATION_BLOCKED"
    RELATION_INVALID = "RELATION_INVALID"


@dataclass
class RelationCandidate:
    relation_id: str
    clause_id: str
    source_token_index: int
    target_token_index: int
    source_surface: str
    target_surface: str
    relation_type: RelationType
    evidence_ids: tuple
    confidence_rank: int       # 0-6 (Taaqol rank lattice)
    contradictions: tuple
    residuals: tuple
    status: RelationClosureState


@dataclass
class RelationClosureResult:
    relation_id: str
    closure_state: RelationClosureState
    licensed_parties: tuple
    relation_type: RelationType
    evidence: tuple
    contradictions: tuple
    residuals: tuple
    required_argument_complete: bool
    scope_closed: bool
