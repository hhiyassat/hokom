#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/word_class/catalog.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Lookup helpers that bridge the mabniyat catalog into word class evidence.

Uses the existing mabniyat_catalog_split_vocalized.csv (loaded via
mabniyat_layer.load_catalog) as the canonical source for
DETACHED_PRONOUN, DEMONSTRATIVE, RELATIVE, etc.

B-04 fix: pronouns and demonstratives like هُوَ / هَذَا are NOT in the
operators catalog (pipeline/p5_lexical uses only operators CSV), but they
ARE in mabniyat_catalog_split_vocalized.csv, where mabniyat_layer finds
them.  This module exposes that catalog to the word class engine.
"""
from __future__ import annotations

import unicodedata
from typing import Optional

from .models import LexicalSubclass, EvidenceType, WordClassEvidence

# ── Mabniyat lexical_class → word class subclass mapping ─────────────────────

# These come from mabniyat_catalog_split_vocalized.csv column `lexical_class`.
_MABNIYAT_LEXICAL_CLASS_TO_SUBCLASS: dict[str, LexicalSubclass] = {
    'DETACHED_PRONOUN':   LexicalSubclass.PRONOUN,
    'ATTACHED_PRONOUN':   LexicalSubclass.PRONOUN,
    'DEMONSTRATIVE':      LexicalSubclass.DEMONSTRATIVE,
    'RELATIVE':           LexicalSubclass.RELATIVE,
    'RELATIVE_PRONOUN':   LexicalSubclass.RELATIVE,       # catalog alias
    'INTERROGATIVE_NOUN': LexicalSubclass.INTERROGATIVE_NOUN,
    'INTERROGATIVE_NAME': LexicalSubclass.INTERROGATIVE_NOUN,  # catalog alias
    'CONDITIONAL_NOUN':   LexicalSubclass.CONDITIONAL_NOUN,
    'CONDITIONAL_NAME':   LexicalSubclass.CONDITIONAL_NOUN,    # catalog alias (متى / مهما / أنى)
    'JAZM_NAME':          LexicalSubclass.CONDITIONAL_NOUN,    # catalog alias (jazm names)
    'ADVERBIAL_MABNI':    LexicalSubclass.ADVERBIAL_MABNI,
    'VERB_NAME':          LexicalSubclass.VERB_NAME,
    # These are ISM-class entries that block FI3L
    'NON_VERBAL_SURFACE': LexicalSubclass.LEXICAL_NOUN,
}

# Mabniyat lexical_class → EvidenceType mapping
_MABNIYAT_CLASS_TO_EVIDENCE_TYPE: dict[str, EvidenceType] = {
    'DETACHED_PRONOUN':   EvidenceType.LEXICAL_PRONOUN_ENTRY,
    'ATTACHED_PRONOUN':   EvidenceType.LEXICAL_PRONOUN_ENTRY,
    'DEMONSTRATIVE':      EvidenceType.LEXICAL_DEMONSTRATIVE_ENTRY,
    'RELATIVE':           EvidenceType.LEXICAL_RELATIVE_ENTRY,
    'RELATIVE_PRONOUN':   EvidenceType.LEXICAL_RELATIVE_ENTRY,
    'INTERROGATIVE_NOUN': EvidenceType.LEXICAL_INTERROGATIVE_NOUN,
    'INTERROGATIVE_NAME': EvidenceType.LEXICAL_INTERROGATIVE_NOUN,
    'CONDITIONAL_NOUN':   EvidenceType.LEXICAL_NOMINAL_ENTRY,
    'CONDITIONAL_NAME':   EvidenceType.LEXICAL_NOMINAL_ENTRY,
    'JAZM_NAME':          EvidenceType.LEXICAL_NOMINAL_ENTRY,
    'ADVERBIAL_MABNI':    EvidenceType.LEXICAL_ADVERBIAL_MABNI,
    'VERB_NAME':          EvidenceType.LEXICAL_VERB_NAME,
    'NON_VERBAL_SURFACE': EvidenceType.LEXICAL_NOMINAL_ENTRY,
}

# Operator catalog lexical_class → word class subclass (from mabni_projection.py)
_OPERATOR_LEXICAL_CLASS_TO_SUBCLASS: dict[str, LexicalSubclass] = {
    'Closed Function Word': LexicalSubclass.CLOSED_FUNCTION_WORD,
    'Numerical Operator':   LexicalSubclass.NUMERICAL_OPERATOR,
    'Verbal Operator':      LexicalSubclass.VERBAL_OPERATOR,
    'Phrase Operator':      LexicalSubclass.VERBAL_OPERATOR,
    'Cognition Verb':       LexicalSubclass.VERBAL_OPERATOR,
    'Bound Nominal':        LexicalSubclass.LEXICAL_NOUN,
}

# ISM subclasses (DETACHED_PRONOUN etc. are nominal word classes)
_ISM_MABNIYAT_CLASSES: frozenset[str] = frozenset({
    'DETACHED_PRONOUN',
    'ATTACHED_PRONOUN',
    'DEMONSTRATIVE',
    'RELATIVE',
    'RELATIVE_PRONOUN',   # catalog alias
    'INTERROGATIVE_NOUN',
    'INTERROGATIVE_NAME', # catalog alias
    'CONDITIONAL_NOUN',
    'CONDITIONAL_NAME',   # catalog alias — متى / مهما / أنى
    'JAZM_NAME',          # catalog alias — jazm conditional names
    'ADVERBIAL_MABNI',
    'VERB_NAME',
    'NON_VERBAL_SURFACE',
})

# Operator lexical classes that map to HARF
_HARF_OPERATOR_CLASSES: frozenset[str] = frozenset({
    'Closed Function Word',
    'Numerical Operator',
})

# Operator lexical classes that map to FI3L-like (verbal operators)
_VERBAL_OPERATOR_CLASSES: frozenset[str] = frozenset({
    'Verbal Operator',
    'Phrase Operator',
    'Cognition Verb',
})

# Derivative type → subclass mapping
_DERIVATIVE_TYPE_TO_SUBCLASS: dict[str, LexicalSubclass] = {
    'ISM_FA3IL':         LexicalSubclass.ISM_FA3IL,
    'ISM_MAF3UL':        LexicalSubclass.ISM_MAF3UL,
    'SIFA_MUSHABBAHA':   LexicalSubclass.SIFA_MUSHABBAHA,
    'SIYAG_MUBALAGHAH':  LexicalSubclass.MUBALGHA,
    'MUBALGHA':          LexicalSubclass.MUBALGHA,
    'ISM_ZAMAN':         LexicalSubclass.ISM_ZAMAN_MAKAN,
    'ISM_MAKAN':         LexicalSubclass.ISM_ZAMAN_MAKAN,
    'ISM_ZAMAN_MAKAN':   LexicalSubclass.ISM_ZAMAN_MAKAN,
    'ISM_ALA':           LexicalSubclass.ISM_ALA,
    'TAFDHIL':           LexicalSubclass.SIFA_MUSHABBAHA,
}


# ── Singleton catalog loader ───────────────────────────────────────────────────

_MABNIYAT_CATALOG: Optional[dict] = None


def _get_mabniyat_catalog() -> dict:
    """
    Load and cache mabniyat_catalog_split_vocalized.csv.
    Uses mabniyat_layer.load_catalog() which finds the file relative to
    its own __file__ (repo root).  Safe to call multiple times.
    """
    global _MABNIYAT_CATALOG
    if _MABNIYAT_CATALOG is None:
        try:
            from mabniyat_layer import load_catalog
            _MABNIYAT_CATALOG = load_catalog()
        except Exception:
            _MABNIYAT_CATALOG = {'by_id': {}, 'by_vocalized': {}, 'by_bare': {}, 'all_rows': []}
    return _MABNIYAT_CATALOG


def lookup_mabni_id(mabni_id: str) -> Optional[dict]:
    """Return the catalog row for a given mabni_id, or None."""
    cat = _get_mabniyat_catalog()
    return cat['by_id'].get(mabni_id)


def lexical_class_for_mabni_id(mabni_id: str) -> Optional[str]:
    """Return the lexical_class string from the mabniyat catalog for mabni_id."""
    row = lookup_mabni_id(mabni_id)
    if row is None:
        return None
    return row.get('lexical_class') or None


def mabni_id_for_vocalized(surface: str) -> str:
    """
    Look up a mabni_id from the mabniyat catalog by vocalized surface form.
    Returns the mabni_id string, or '' if not found.

    Used by _run_word_class_engine to synthesise attachment_mabni_id when a
    token arrives via MabniBoundary directly (commit 3 path) rather than via
    the segmenter attachment path.

    NFC-normalizes the input so that diacritic-ordering variants (e.g. أَنَّى
    with shadda-before-fatha vs fatha-before-shadda) resolve to the same key.
    The catalog indexes by NFC(surface_vocalized) via mabniyat_layer.normalize_key.
    """
    cat = _get_mabniyat_catalog()
    key = unicodedata.normalize('NFC', surface)
    row = cat.get('by_vocalized', {}).get(key)
    if row is not None:
        return row.get('mabni_id', '')
    return ''


def extract_mabni_id_from_notes(notes: str) -> str:
    """
    Extract mabni_id from attachment.notes of the form
    'whole-token match: HUWA' or 'whole-token match: HADHA'.
    Returns '' if the pattern is not found.
    """
    marker = 'whole-token match: '
    if notes and marker in notes:
        return notes[notes.index(marker) + len(marker):].strip()
    return ''


def get_ism_subclass_from_mabni_id(mabni_id: str) -> Optional[LexicalSubclass]:
    """
    Given a mabniyat catalog mabni_id, return the ISM subclass or None.
    Returns None if the mabni_id maps to a non-ISM class.
    """
    lex_class = lexical_class_for_mabni_id(mabni_id)
    if lex_class is None:
        return None
    return _MABNIYAT_LEXICAL_CLASS_TO_SUBCLASS.get(lex_class)


def get_evidence_type_for_mabni_id(mabni_id: str) -> EvidenceType:
    """
    Return the appropriate EvidenceType for a mabniyat catalog mabni_id.
    """
    lex_class = lexical_class_for_mabni_id(mabni_id)
    if lex_class is None:
        return EvidenceType.ATTACHMENT_MABNI
    return _MABNIYAT_CLASS_TO_EVIDENCE_TYPE.get(lex_class, EvidenceType.ATTACHMENT_MABNI)


def is_ism_mabni_class(mabni_id: str) -> bool:
    """Return True if mabni_id's lexical_class is nominal (ISM)."""
    lex_class = lexical_class_for_mabni_id(mabni_id)
    if lex_class is None:
        return False
    return lex_class in _ISM_MABNIYAT_CLASSES


def build_attachment_evidence(mabni_id: str) -> Optional[WordClassEvidence]:
    """
    Build a WordClassEvidence from a mabni_id, or None if not found.
    """
    row = lookup_mabni_id(mabni_id)
    if row is None:
        return None
    lex_class = row.get('lexical_class', '')
    ev_type = _MABNIYAT_CLASS_TO_EVIDENCE_TYPE.get(lex_class, EvidenceType.ATTACHMENT_MABNI)
    surface = row.get('surface_vocalized', mabni_id)
    return WordClassEvidence(
        evidence_type=ev_type,
        source='mabniyat_catalog_split_vocalized.csv',
        value=f'{mabni_id}:{lex_class}:{surface}',
        confidence='HIGH',
    )
