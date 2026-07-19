"""
pipeline/word_class — Canonical ISM / FI3L / HARF word class engine.

HOKOM-WORD-CLASS-OWNERSHIP-01
"""
from .engine import classify_word_class
from .models import (
    WORD_CLASS_ENGINE_ID,
    WORD_CLASS_CANONICAL_OWNER,
    WORD_CLASS_OWNERSHIP_VERSION,
    WORD_CLASS_CANONICAL_ENTRYPOINT,
    WordClass,
    WordClassVerdict,
    LexicalSubclass,
    EvidenceType,
    ContradictionType,
    WordClassEvidence,
    WordClassContradiction,
    WordClassCandidate,
    WordClassRequest,
    WordClassResult,
    WordClassTraceEvent,
    WordClassResidual,
    WordClassOwnershipGate,
)

__all__ = [
    'classify_word_class',
    'WORD_CLASS_ENGINE_ID',
    'WORD_CLASS_CANONICAL_OWNER',
    'WORD_CLASS_OWNERSHIP_VERSION',
    'WORD_CLASS_CANONICAL_ENTRYPOINT',
    'WordClass',
    'WordClassVerdict',
    'LexicalSubclass',
    'EvidenceType',
    'ContradictionType',
    'WordClassEvidence',
    'WordClassContradiction',
    'WordClassCandidate',
    'WordClassRequest',
    'WordClassResult',
    'WordClassTraceEvent',
    'WordClassResidual',
    'WordClassOwnershipGate',
]
