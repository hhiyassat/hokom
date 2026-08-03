from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class DalStatus(str, Enum):
    OBSERVED = "OBSERVED"
    HYPOTHESIZED = "HYPOTHESIZED"
    CANDIDATE = "CANDIDATE"
    DOMAIN_ACCEPTED = "DOMAIN_ACCEPTED"
    CONSTITUTIONALLY_LICENSED = "CONSTITUTIONALLY_LICENSED"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"

class MadlulStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    LICENSED = "LICENSED"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"
    AMBIGUOUS = "AMBIGUOUS"

@dataclass(frozen=True)
class DalClaim:
    """A typed 'dal' (signifier) claim. Never constructs meaning directly."""
    claim_id: str
    surface: str
    lexical_identity: str           # word form identity (NOT meaning)
    lexical_sense_candidate: Optional[str]    # pre-semantic sense ID
    contextual_usage: Optional[str]           # grammatical function
    status: DalStatus
    evidence_ids: tuple[str, ...]
    contradictions: tuple[str, ...]
    residuals: tuple[str, ...]
    source_module: str              # must be hokom module path

    def is_licensed(self) -> bool:
        return self.status == DalStatus.CONSTITUTIONALLY_LICENSED

@dataclass(frozen=True)
class MadlulCandidate:
    """A madlul (signified) candidate. Requires sense_id and lexical/corpus source."""
    candidate_id: str
    sense_id: str                  # lexical sense identifier — NOT free text
    source_type: str               # "LEXICAL_ENTRY" | "CORPUS_EVIDENCE" | "GRAMMATICAL_FUNCTION"
    source_reference: str          # path/ID of source
    ambiguity: bool                # True if multiple senses possible
    constraining_context: Optional[str]   # what would disambiguate
    status: MadlulStatus
    evidence_ids: tuple[str, ...]
    residuals: tuple[str, ...]

@dataclass(frozen=True)
class DalMadlulBinding:
    """A bound dal→madlul pair. Requires licensed dal + licensed madlul + binding evidence."""
    binding_id: str
    dal_claim: DalClaim
    madlul_candidate: MadlulCandidate
    binding_evidence: tuple[str, ...]
    ambiguity_resolved: bool
    residuals: tuple[str, ...]
    licensed: bool                 # True only if both parties licensed and binding evidenced
