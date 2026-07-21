#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
functional_lexical_lookup.py — Unified Functional Lexical Lookup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-MABNI-FUNCTIONAL-CATALOG-OWNERSHIP-01 — Commit 2/5

Provides a unified lookup for ALL functional-word categories:
  - Operator boundary (حروف المعاني / الأدوات) → OPERATOR_BOUNDARY
  - Mabni ISM boundary (ضمائر / موصولات / استفهام) → MABNI_BOUNDARY
  - Category ambiguity (collision between vocalized forms) → FUNCTIONAL_AMBIGUITY

Architecture:
  1. Loads data/operators_catalog_split_vocalized_corrected.csv as primary source.
  2. Builds two indices:
       vocalized_index : exact vocalized form  → FunctionalEntry
       bare_index      : shadda-preserving bare → list[FunctionalEntry]
  3. Supplements catalog with hardcoded relative-pronoun entries (MABNI_BOUNDARY)
     since no separate CSV file exists for them yet.
  4. Lookup order:
       a) Exact vocalized match      (highest priority, unambiguous)
       b) Bare match — unique form   (no shadda-stripping collision)
       c) Compound: strip known proclitic, check remainder
       d) Collision: bare match → multiple vocalized forms → AMBIGUITY
       e) None                        (not a functional word)

Collision policy:
  A bare form that maps to multiple distinct vocalized entries with
  different owners MUST NOT silently pick the first candidate.
  It returns FunctionalLookupResult(collision=True, ...).
  Root path is still closed (ambiguity does not open the root engine).

Question-word override:
  The following words appear in the operators catalog as is_operator=True
  (group 7 — conditional/jazim) but are fundamentally ISM mabni in Arabic
  traditional grammar (أسماء الاستفهام / أسماء الشرط = declining nouns).
  They are classified here as MABNI_BOUNDARY:
    مَنْ, مَا, أَيْنَ, كَيْفَ, كَمْ, أَيّ, مَتَى, أَنَّى

Provenance fields on every result:
  matched_form, match_type, source_file, collision_candidates
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Arabic diacritics ─────────────────────────────────────────────────────────
_ARABIC_DIACRITICS     = frozenset('ًٌٍَُِّْٰ')
_SHADDA                = 'ّ'   # ّ
_DIACRITICS_NO_SHADDA  = _ARABIC_DIACRITICS - {_SHADDA}


def _strip_all(s: str) -> str:
    """Strip all diacritics including shadda."""
    return ''.join(c for c in s if c not in _ARABIC_DIACRITICS)


def _strip_except_shadda(s: str) -> str:
    """Strip all diacritics except shadda (preserves إِنَّ vs إِنْ distinction)."""
    return ''.join(c for c in s if c not in _DIACRITICS_NO_SHADDA)


# ── Question words: grammatically ISM mabni (أسماء الاستفهام / الشرط) ────────
# These appear in the operators catalog with is_operator=True but are
# classified here as MABNI_BOUNDARY (they are declining nouns, not particles).
#
# IMPORTANT: The override is matched against the VOCALIZED form (not bare-stripped),
# to avoid collision between مَنْ (man, who) and مِنْ (min, from/of).
# Both strip to 'من' but only مَنْ is a question/relative pronoun.
_QUESTION_WORDS_VOCALIZED: frozenset[str] = frozenset({
    'مَنْ',    # who (question / relative / conditional)
    'مَا',     # what / which (relative / conditional)
    'أَيْنَ',  # where
    'كَيْفَ',  # how
    'كَمْ',    # how many / how much
    'أَيّ',    # which (conditional / interrogative noun)
    'مَتَى',   # when
    'أَنَّى',  # whence / how
    'مَهْمَا', # whatever / however much
})

# ── Known two-character proclitic prefixes (for compound lookup) ─────────────
# Used as fallback when segment_host is not found as a standalone form.
# These are the standard clitic prefixes the P0 segmenter may leave attached
# when it cannot split (e.g. لِمَا where لِ stays joined to مَا).
_PROCLITIC_PREFIXES: tuple[str, ...] = (
    'وَ', 'فَ', 'بِ', 'لِ', 'كَ',   # common conjunctions + prepositions
    'وَال', 'فَال', 'بِال', 'لِل',    # with definite article
)


# ══════════════════════════════════════════════════════════════════════════════
# Data model
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FunctionalEntry:
    """Single catalog entry for a functional word."""
    vocalized:   str            # exact form as stored in catalog
    owner:       str            # OPERATOR_BOUNDARY | MABNI_BOUNDARY
    category:    str            # Arabic group name
    group_num:   int
    is_operator: bool
    source_file: str
    word_class:  str            # HARF (operator) | ISM (mabni)


@dataclass
class FunctionalLookupResult:
    """
    Result returned by lookup().

    When collision=True, owner is None and collision_candidates is populated.
    Root path is still CLOSED even on collision (ambiguity ≠ not-found).
    """
    owner:               Optional[str]         # OPERATOR_BOUNDARY | MABNI_BOUNDARY | None
    collision:           bool      = False
    matched_form:        str       = ''
    match_type:          str       = ''        # VOCALIZED | BARE | COMPOUND | HARDCODED
    source_file:         str       = ''
    collision_candidates: list      = field(default_factory=list)
    category:            str       = ''
    word_class:          str       = ''        # HARF | ISM


# ── Hardcoded supplemental entries (no CSV file for these yet) ────────────────
# Relative pronouns (الأسماء الموصولة) and disconnected pronouns (الضمائر المنفصلة).
# All are MABNI_BOUNDARY, word_class=ISM.
_HARDCODED_MABNI: list[dict] = [
    # Relative pronouns — مفرد
    {'vocalized': 'الَّذِي',   'category': 'اسم موصول مفرد مذكر',   'group_num': 0},
    {'vocalized': 'الَّتِي',   'category': 'اسم موصول مفرد مؤنث',   'group_num': 0},
    # Relative pronouns — مثنى
    {'vocalized': 'اللَّذَيْنِ', 'category': 'اسم موصول مثنى مذكر', 'group_num': 0},
    {'vocalized': 'اللَّتَيْنِ', 'category': 'اسم موصول مثنى مؤنث', 'group_num': 0},
    # Relative pronouns — جمع
    {'vocalized': 'الَّذِينَ',  'category': 'اسم موصول جمع مذكر',   'group_num': 0},
    {'vocalized': 'اللَّاتِي',  'category': 'اسم موصول جمع مؤنث',   'group_num': 0},
    {'vocalized': 'اللَّوَاتِي', 'category': 'اسم موصول جمع مؤنث',  'group_num': 0},
    # Disconnected pronouns — ضمائر منفصلة
    {'vocalized': 'هُوَ',   'category': 'ضمير منفصل غائب مذكر مفرد',  'group_num': 0},
    {'vocalized': 'هِيَ',   'category': 'ضمير منفصل غائب مؤنث مفرد',  'group_num': 0},
    {'vocalized': 'هُمَا',  'category': 'ضمير منفصل غائب مثنى',        'group_num': 0},
    {'vocalized': 'هُمْ',   'category': 'ضمير منفصل غائب مذكر جمع',    'group_num': 0},
    {'vocalized': 'هُنَّ',  'category': 'ضمير منفصل غائب مؤنث جمع',    'group_num': 0},
    {'vocalized': 'أَنَا',  'category': 'ضمير منفصل متكلم مفرد',        'group_num': 0},
    {'vocalized': 'نَحْنُ', 'category': 'ضمير منفصل متكلم جمع',         'group_num': 0},
    {'vocalized': 'أَنْتَ', 'category': 'ضمير منفصل مخاطب مذكر مفرد',  'group_num': 0},
    {'vocalized': 'أَنْتِ', 'category': 'ضمير منفصل مخاطب مؤنث مفرد',  'group_num': 0},
    {'vocalized': 'أَنْتُمَا', 'category': 'ضمير منفصل مخاطب مثنى',    'group_num': 0},
    {'vocalized': 'أَنْتُمْ', 'category': 'ضمير منفصل مخاطب مذكر جمع', 'group_num': 0},
    {'vocalized': 'أَنْتُنَّ', 'category': 'ضمير منفصل مخاطب مؤنث جمع', 'group_num': 0},
    # Question words explicitly as ISM mabni
    {'vocalized': 'كَيْفَ',  'category': 'اسم استفهام حال',    'group_num': 0},
    {'vocalized': 'أَيْنَ',  'category': 'اسم استفهام مكان',   'group_num': 0},
    {'vocalized': 'مَتَى',   'category': 'اسم استفهام زمان',   'group_num': 0},
    {'vocalized': 'كَمْ',    'category': 'اسم استفهام عدد',    'group_num': 0},
    {'vocalized': 'مَنْ',    'category': 'اسم استفهام للعاقل', 'group_num': 0},
    {'vocalized': 'مَا',     'category': 'اسم استفهام/موصول لغير العاقل', 'group_num': 0},
    {'vocalized': 'أَيّ',    'category': 'اسم استفهام وشرط',   'group_num': 0},
]

# Compound operator forms that the P0 segmenter may leave unsplit.
# These are added as OPERATOR_BOUNDARY entries.
_COMPOUND_OPERATORS: list[dict] = [
    {'vocalized': 'لِمَا',  'category': 'حرف جر مع ما الموصولة', 'group_num': 1},
    {'vocalized': 'بِمَا',  'category': 'حرف جر مع ما الموصولة', 'group_num': 1},
    {'vocalized': 'فِيمَا', 'category': 'حرف جر مع ما الموصولة', 'group_num': 1},
    {'vocalized': 'عَمَّا', 'category': 'حرف جر مع ما الموصولة', 'group_num': 1},
    {'vocalized': 'مِمَّا', 'category': 'حرف جر مع ما الموصولة', 'group_num': 1},
    {'vocalized': 'كَمَا',  'category': 'حرف جر مع ما الموصولة', 'group_num': 1},
]


# ══════════════════════════════════════════════════════════════════════════════
# FunctionalLexicalIndex
# ══════════════════════════════════════════════════════════════════════════════

class FunctionalLexicalIndex:
    """
    Builds and queries a two-tier index (vocalized + bare) over all functional words.

    Thread safety: build once at module load, treat as read-only thereafter.
    """

    def __init__(self):
        self._vocalized: dict[str, FunctionalEntry]       = {}  # exact → entry
        self._bare:      dict[str, list[FunctionalEntry]] = {}  # bare → entries

    # ── Build ──────────────────────────────────────────────────────────────────

    def _owner_from_entry(self, vocalized: str, is_operator: bool, group_num: int) -> tuple[str, str]:
        """
        Determine (owner, word_class) for a catalog row.

        Precedence:
          1. Vocalized question-word override  →  MABNI_BOUNDARY / ISM
             Matched against _QUESTION_WORDS_VOCALIZED (exact vocalized form).
             This avoids the مَنْ/مِنْ bare collision: both strip to 'من' but
             only مَنْ (man, fatha) is a question/relative pronoun.
          2. is_operator=False       →  MABNI_BOUNDARY / ISM
          3. is_operator=True        →  OPERATOR_BOUNDARY / HARF
        """
        if vocalized in _QUESTION_WORDS_VOCALIZED:
            return 'MABNI_BOUNDARY', 'ISM'
        if not is_operator:
            return 'MABNI_BOUNDARY', 'ISM'
        return 'OPERATOR_BOUNDARY', 'HARF'

    def _add(self, entry: FunctionalEntry) -> None:
        # Vocalized index: first registration wins (catalog order = priority)
        if entry.vocalized not in self._vocalized:
            self._vocalized[entry.vocalized] = entry

        # Bare-except-shadda index: all entries
        bare_key = _strip_except_shadda(entry.vocalized)
        if bare_key:
            self._bare.setdefault(bare_key, []).append(entry)

    def load_csv(self, path: str) -> 'FunctionalLexicalIndex':
        """Load from operators_catalog_split_vocalized_corrected.csv."""
        source = Path(path).name
        with open(path, encoding='utf-8-sig', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                surface = row.get('Operator', '').strip()
                if not surface:
                    continue
                is_op_str = (row.get('is_operator') or 'True').strip()
                is_op     = is_op_str.lower() not in ('false', '0', 'no')
                try:
                    grp = int(row.get('Group Number', '0').strip() or '0')
                except ValueError:
                    grp = 0
                owner, wc = self._owner_from_entry(surface, is_op, grp)
                self._add(FunctionalEntry(
                    vocalized   = surface,
                    owner       = owner,
                    category    = row.get('Arabic Group Name', '').strip(),
                    group_num   = grp,
                    is_operator = is_op,
                    source_file = source,
                    word_class  = wc,
                ))
        return self

    def load_hardcoded_mabni(self) -> 'FunctionalLexicalIndex':
        """Add hardcoded relative pronouns and disconnected pronouns."""
        for rec in _HARDCODED_MABNI:
            self._add(FunctionalEntry(
                vocalized   = rec['vocalized'],
                owner       = 'MABNI_BOUNDARY',
                category    = rec['category'],
                group_num   = rec.get('group_num', 0),
                is_operator = False,
                source_file = 'hardcoded:relative_pronouns_and_question_words',
                word_class  = 'ISM',
            ))
        return self

    def load_compound_operators(self) -> 'FunctionalLexicalIndex':
        """Add compound operator forms that the segmenter may leave unsplit."""
        for rec in _COMPOUND_OPERATORS:
            self._add(FunctionalEntry(
                vocalized   = rec['vocalized'],
                owner       = 'OPERATOR_BOUNDARY',
                category    = rec['category'],
                group_num   = rec.get('group_num', 1),
                is_operator = True,
                source_file = 'hardcoded:compound_operators',
                word_class  = 'HARF',
            ))
        return self

    # ── Lookup ────────────────────────────────────────────────────────────────

    def lookup(self, segment_host: str) -> Optional[FunctionalLookupResult]:
        """
        Resolve segment_host against the functional index.

        Returns FunctionalLookupResult or None (not a functional word).

        Lookup order:
          1. Exact vocalized match
          2. Bare-except-shadda unique match (shadda distinguishes إنَّ/إنْ)
          3. Compound prefix stripping + recursive lookup on remainder
          4. Bare collision → FUNCTIONAL_AMBIGUITY (still closes root)
          5. None → not a functional word
        """
        if not segment_host:
            return None

        # ── Step 1: exact vocalized ──────────────────────────────────────────
        if segment_host in self._vocalized:
            e = self._vocalized[segment_host]
            return FunctionalLookupResult(
                owner         = e.owner,
                collision     = False,
                matched_form  = e.vocalized,
                match_type    = 'VOCALIZED',
                source_file   = e.source_file,
                category      = e.category,
                word_class    = e.word_class,
            )

        # ── Step 2: bare-except-shadda unique match ──────────────────────────
        bare_key = _strip_except_shadda(segment_host)
        if bare_key and bare_key in self._bare:
            entries         = self._bare[bare_key]
            unique_vocalized = list(dict.fromkeys(e.vocalized for e in entries))
            unique_owners   = list(dict.fromkeys(e.owner for e in entries))

            if len(unique_vocalized) == 1:
                # Unambiguous bare match
                e = entries[0]
                return FunctionalLookupResult(
                    owner         = e.owner,
                    collision     = False,
                    matched_form  = e.vocalized,
                    match_type    = 'BARE',
                    source_file   = e.source_file,
                    category      = e.category,
                    word_class    = e.word_class,
                )
            # Multiple distinct vocalized forms under same bare key
            # → collision; root is still closed
            return FunctionalLookupResult(
                owner                = None,
                collision            = True,
                matched_form         = segment_host,
                match_type           = 'COLLISION',
                source_file          = entries[0].source_file if entries else '',
                collision_candidates = unique_vocalized,
                category             = 'FUNCTIONAL_CATEGORY_AMBIGUITY',
                word_class           = '',
            )

        # ── Step 3: compound prefix stripping ────────────────────────────────
        compound_result = self._lookup_compound(segment_host)
        if compound_result is not None:
            return compound_result

        # ── Step 4: full-strip bare fallback (less precise) ──────────────────
        bare_full = _strip_all(segment_host)
        if bare_full and bare_full != bare_key and bare_full in self._bare:
            entries          = self._bare[bare_full]
            unique_vocalized = list(dict.fromkeys(e.vocalized for e in entries))
            if len(unique_vocalized) == 1:
                e = entries[0]
                return FunctionalLookupResult(
                    owner         = e.owner,
                    collision     = False,
                    matched_form  = e.vocalized,
                    match_type    = 'BARE',
                    source_file   = e.source_file,
                    category      = e.category,
                    word_class    = e.word_class,
                )
            if len(unique_vocalized) > 1:
                return FunctionalLookupResult(
                    owner                = None,
                    collision            = True,
                    matched_form         = segment_host,
                    match_type           = 'COLLISION',
                    source_file          = entries[0].source_file if entries else '',
                    collision_candidates = unique_vocalized,
                    category             = 'FUNCTIONAL_CATEGORY_AMBIGUITY',
                    word_class           = '',
                )

        return None

    def _lookup_compound(self, host: str) -> Optional[FunctionalLookupResult]:
        """
        Try to resolve host as (proclitic_prefix + functional_remainder).

        Used when the P0 segmenter does not split a compound such as لِمَا
        into its proclitic (لِ) and host (مَا).

        Only returns a result if the remainder is unambiguously found in the
        functional index as OPERATOR_BOUNDARY.  (A mabni remainder here means
        the proclitic may have fused with the host — we decline to claim owner.)
        """
        for prefix in _PROCLITIC_PREFIXES:
            # Exact prefix match
            if host.startswith(prefix) and len(host) > len(prefix):
                remainder = host[len(prefix):]
                res = self.lookup(remainder)
                if res is not None and not res.collision:
                    return FunctionalLookupResult(
                        owner         = 'OPERATOR_BOUNDARY',
                        collision     = False,
                        matched_form  = remainder,
                        match_type    = 'COMPOUND',
                        source_file   = res.source_file,
                        category      = res.category,
                        word_class    = 'HARF',
                    )
            # Bare prefix match (for diacritically-varied proclitics)
            bare_host   = _strip_all(host)
            bare_prefix = _strip_all(prefix)
            if (bare_host.startswith(bare_prefix)
                    and len(bare_host) > len(bare_prefix)):
                remainder_bare = bare_host[len(bare_prefix):]
                # Find a matching remainder in full-bare index
                if remainder_bare in self._bare:
                    entries = self._bare[remainder_bare]
                    unique  = list(dict.fromkeys(e.vocalized for e in entries))
                    if len(unique) == 1:
                        e = entries[0]
                        return FunctionalLookupResult(
                            owner         = 'OPERATOR_BOUNDARY',
                            collision     = False,
                            matched_form  = e.vocalized,
                            match_type    = 'COMPOUND',
                            source_file   = e.source_file,
                            category      = e.category,
                            word_class    = 'HARF',
                        )
        return None


# ══════════════════════════════════════════════════════════════════════════════
# Module-level singleton
# ══════════════════════════════════════════════════════════════════════════════

_INDEX: Optional[FunctionalLexicalIndex] = None


def _get_index() -> FunctionalLexicalIndex:
    """Return the module singleton, loading it on first call."""
    global _INDEX
    if _INDEX is None:
        _INDEX = FunctionalLexicalIndex()
        # ── Primary catalog (operators CSV) ──────────────────────────────────
        _csv = Path(__file__).resolve().parents[2] / 'data' / \
               'operators_catalog_split_vocalized_corrected.csv'
        if _csv.exists():
            _INDEX.load_csv(str(_csv))
        # ── Supplemental: relative pronouns, disconnected pronouns ───────────
        _INDEX.load_hardcoded_mabni()
        # ── Supplemental: compound operators (لِمَا, بِمَا, …) ───────────────
        _INDEX.load_compound_operators()
    return _INDEX


def lookup(segment_host: str) -> Optional[FunctionalLookupResult]:
    """
    Public API.  Resolve segment_host against the unified functional index.

    Called with segment_host (after P0 clitic stripping), NOT original_surface.
    Returns FunctionalLookupResult or None.
    """
    return _get_index().lookup(segment_host)


def reset_index() -> None:
    """Reset the singleton (for test isolation). Not for production use."""
    global _INDEX
    _INDEX = None


# ══════════════════════════════════════════════════════════════════════════════
# CLI smoke test
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    _tests = [
        'مَا', 'مِنْ', 'مَنْ', 'إِذَا', 'إِذًا', 'إِنَّ', 'إِنْ', 'أَنَّ', 'أَنْ',
        'الَّذِي', 'الَّذِينَ', 'هُوَ', 'أَيْنَ', 'كَيْفَ', 'كَمْ', 'أَيّ',
        'لِمَا', 'بِمَا', 'فِيمَا', 'عَمَّا',
        'حَقُّ', 'كَاتِبٌ', 'يَكْتُبُ',   # negative controls → should return None
    ]
    idx = _get_index()
    print(f"\n  Functional index: {len(idx._vocalized)} vocalized entries")
    print()
    for tok in _tests:
        r = lookup(tok)
        if r is None:
            print(f"  None          {tok!r}")
        elif r.collision:
            print(f"  COLLISION     {tok!r}  candidates={r.collision_candidates}")
        else:
            print(f"  {r.owner:<20} {tok!r:20} [{r.match_type}] wc={r.word_class}")
