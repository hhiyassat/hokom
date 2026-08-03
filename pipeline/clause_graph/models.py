from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ClauseBoundaryType(str, Enum):
    CONJUNCTION = "CONJUNCTION"         # و، ف، ثم
    CONDITIONAL = "CONDITIONAL"         # إذا، إن، لو
    RELATIVE = "RELATIVE"               # الذي، التي
    IMPERATIVE = "IMPERATIVE"           # فعل أمر
    NEGATION = "NEGATION"               # لا، لم، لن
    JUXTAPOSITION = "JUXTAPOSITION"     # implicit boundary
    APPOSITION = "APPOSITION"
    RELATIVE_ATTACHMENT = "RELATIVE_ATTACHMENT"


class ClauseStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"


@dataclass
class ClauseBoundary:
    boundary_id: str
    token_index: int               # boundary BEFORE this token
    boundary_type: ClauseBoundaryType
    operator_surface: Optional[str]
    evidence_ids: tuple
    confidence: float              # 0.0–1.0
    residuals: tuple


@dataclass
class ClauseCandidate:
    clause_id: str
    token_start: int               # inclusive
    token_end: int                 # inclusive
    surface: str                   # reconstructed surface
    boundary_evidence: tuple
    operators: tuple               # surfaces of operators
    main_predicate_candidates: tuple   # token surfaces
    argument_candidates: tuple
    references: tuple              # pronoun references
    active_residuals: tuple
    status: ClauseStatus
