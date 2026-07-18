#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mabniyat_attachment.py — Attached Pronoun Recognition (Phase 5, Layer 2)
════════════════════════════════════════════════════════════════════════════

Recognizes attached suffix pronouns (and prefix operator allomorphs) in
tokens that return MABNI_NOT_FOUND from the whole-token mabniyat lookup.

Pipeline position:
    process_mabni(surface, p4_verdict)  → MABNI_NOT_FOUND
    → recognize_token(surface, p4_verdict)     ← this module
    → TokenAnalysis (host + attached_mabniyat)

P4 Monotonicity (absolute, inherited):
    The host's structural_verdict is never overridden.
    Attached suffix recognition is INFORMATIONAL — it adds detail
    but never changes the P4 verdict of the host or the whole token.

Ambiguity policy:
    If multiple licensed segmentations survive at the same suffix-depth,
    return segmentation_verdict='AMBIGUOUS' with all candidates listed.
    If one segmentation strips more suffixes than all others, prefer it
    (maximal suffix stripping principle — the shallower alternative leaves
    a morphologically marked form that cannot stand alone).

Connected-waw rule (depth guard):
    The allomorph و (waw al-jamaa without alif, occurs before a following
    pronoun) is excluded from top-level suffix matching.  It is only tried
    at recursion depth ≥ 1, i.e. after at least one other suffix has already
    been identified to its right.  This prevents false-positive matches on
    words like أَبُو where the final waw is part of the noun inflection, not
    a verbal person-marker.

Host validity rule:
    After stripping suffix(es), the remaining host must satisfy:
      (a) non-empty, AND
      (b) either a recognized prefix operator / allomorph, OR len(host) ≥ 3.
    Single- and two-character hosts that are not recognized operators are
    rejected to prevent spurious segmentations (e.g., مَا → مَ + ا is
    rejected because مَ has len 2 and is not an operator).

Scope constraints (immutable):
    • Works only in /Users/husseinhiyassat/hokom
    • Does not write to any file — catalog is read-only
    • Does not create commits, tags, or merges
    • Does not modify HR2S, DAL, LAFZI, P4 law, or licensed slot patterns
    • Does not modify JSON files under data/02_mabniyat/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import os
import re

import unicodedata
from mabniyat_layer import load_catalog, process_mabni
from glyph_classification import (
    build_glyph_traces as _gc_build_traces,
    last_base_glyph    as _gc_last_base,
    is_mudaric_form    as _gc_is_mudaric,
    is_verbal_dual_host as _gc_is_verbal_dual,
)

# Optional: operators catalog (mabni_layer).  Used in _classify_host to
# distinguish operator hosts (أَنَّ, إِنَّ, …) from ordinary mabni hosts.
# Imported lazily with a try/except so the module remains usable in
# environments where mabni_layer is not installed.
try:
    from mabni_layer import get_inventory as _get_ops_inventory
    _OPS_LAYER_AVAILABLE = True
except ImportError:
    _OPS_LAYER_AVAILABLE = False

# operator_id_map: provides get_profile(surface) → OperatorProfile(operator_id, ...)
# Used by G5 to extract the canonical operator_id from a surface lookup result.
try:
    from operator_id_map import get_profile as _get_ops_profile
    _OPS_PROFILE_AVAILABLE = True
except ImportError:
    _OPS_PROFILE_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# Allomorph tables
# ─────────────────────────────────────────────────────────────────────────────

# Suffix allomorphs not in the catalog but licensed by grammatical paradigm.
# Only consulted at recursion depth ≥ 1 (after at least one suffix already
# stripped), to avoid false positives on nominal-final waw (أَبُو, يَدْعُو).
#
# Key  = surface string to match (must appear at end of remaining host)
# Value = (canonical_mabni_id, explanatory_note)
_DEPTH_GUARDED_SUFFIX_ALLOMORPHS: dict[str, tuple[str, str]] = {
    'و': (
        'ATTACHED_PRONOUN_WAW_AL_JAMAA',
        'connected form: alif (ا) elides before a following suffix pronoun',
    ),
}

# Catalog ATTACHED suffix IDs that are only tried at recursion depth ≥ 1
# (same restriction as _DEPTH_GUARDED_SUFFIX_ALLOMORPHS, but for regular
# catalog rows rather than allomorphs).  Adding an ID here prevents its
# surface form from appearing in the top-level suffix index.
#
# G3 (governance fix): ALIF_AL_ITHNAYN is NO LONGER depth-guarded.
# Depth is not linguistic evidence.  The false-positive risk on حِينَمَا is
# handled by _is_verbal_dual_host() inside _strip_suffixes.  This allows
# genuine depth-0 dual forms (كَتَبَا, ذَهَبَا) to be recognized.
_DEPTH_GUARDED_CATALOG_IDS: set[str] = set()   # currently empty after G3 fix

# Suffix IDs that are valid as the NON-RIGHTMOST span in a multi-suffix
# segmentation (left member in compound stripping, e.g. كَتَبَاهُ).
# These are forms that grammatically mediate between a verb stem and a
# further pronoun suffix.  The WAW_AL_JAMAA allomorph و is handled via
# _DEPTH_GUARDED_SUFFIX_ALLOMORPHS (is_allomorph=True); the entries here
# cover catalog IDs that move to depth-0 after G3.
_MULTI_SPAN_VALID_IDS: set[str] = {
    'ATTACHED_PRONOUN_ALIF_AL_ITHNAYN',
    # ATTACHED_PRONOUN_WAW_AL_JAMAA allomorph و also qualifies but is
    # caught by the is_allomorph + _DEPTH_GUARDED_SUFFIX_ALLOMORPHS check.
}

# Prefix operator allomorphs: prepositions whose surface differs from the
# catalog entry because of vowel assimilation before haa-family pronouns.
#
# Key  = prefix surface present in the token
# Value = (operator_id label used in AttachedMabniSpan.mabni_id,
#           canonical catalog surface)
_PREFIX_ALLOMORPHS: dict[str, tuple[str, str]] = {
    'لَ': ('LI_ALLOMORPH', 'لِ'),   # kasra → fatha before هُ/هُمْ etc.
}

# Catalog prefix operators (single-char prepositions present in the operators
# catalog; looked up by surface, not loaded dynamically to keep this module
# self-contained with respect to the operators catalog).
_CATALOG_PREFIXES: dict[str, str] = {
    'لِ': 'LI',
    'بِ': 'BI',
    'كَ': 'KAF_PREP',
    'فَ': 'FA_PREP',
    'وَ': 'WA_PREP',
}

# Fix 2: Conjunctive proclitics (فَ/وَ) eligible for prefix-first fallback
# when the main suffix scanner finds no candidates.  Only فَ/وَ (conjunction/
# particle) are included — not لِ/بِ/كَ whose consonants can be root radicals.
_CONJUNCTIVE_PROCLITICS: frozenset[str] = frozenset({'فَ', 'وَ'})

# ─────────────────────────────────────────────────────────────────────────────
# Diacritics helper
# ─────────────────────────────────────────────────────────────────────────────

# DEPRECATED (Phase A): these constants are superseded by MarkClass/MarkState
# in glyph_classification.py — the single source of truth.
# They are retained for any remaining callers but must not be used in new code.
# Deletion deferred to the Phase A cleanup pass.
_DIACRITICS_RE = re.compile(r'[ً-ْٰـ]')   # DEPRECATED — use build_glyph_traces()
_FATHA  = 'َ'   # DEPRECATED — use MarkClass.FATHA
_KASRA  = 'ِ'   # DEPRECATED — use MarkClass.KASRA
_DAMMA  = 'ُ'   # DEPRECATED — use MarkClass.DAMMA
_SUKUN  = 'ْ'   # DEPRECATED — use MarkClass.SUKUN

# Letters that function as long-vowel markers (not root consonants when initial)
_LONG_VOWEL_INITIAL = {'ا', 'و', 'ي'}


def _last_base_char(s: str) -> str:
    """
    Return the rightmost non-diacritic Arabic character in *s*, or ''.

    Phase A: thin wrapper over last_base_glyph(build_glyph_traces(s))
    from glyph_classification — the single source of truth.
    """
    t = _gc_last_base(_gc_build_traces(s))
    return t.nfc_base if t is not None else ''


# ─────────────────────────────────────────────────────────────────────────────
# Host morphological class labels (for suffix licensing gates)
# ─────────────────────────────────────────────────────────────────────────────
# These labels classify the RESIDUAL HOST after suffix stripping.
# They exist only to license or reject a proposed attachment boundary;
# they are not final syntactic interpretations.
#
# HOST_VERBAL   — host is recognizably a verb form (mudāri' or māḍī)
# HOST_NOMINAL  — host is recognizably a nominal/adjectival form
# HOST_OPERATOR — host matches a known operator prefix/allomorph
# HOST_MABNI    — host matches a whole-token mabniyat entry
# HOST_AMBIGUOUS — morphological class is not decidable from the surface alone
# HOST_INVALID  — host is empty or structurally implausible
HOST_VERBAL    = 'HOST_VERBAL'
HOST_NOMINAL   = 'HOST_NOMINAL'
HOST_OPERATOR  = 'HOST_OPERATOR'
HOST_MABNI     = 'HOST_MABNI'
HOST_AMBIGUOUS = 'HOST_AMBIGUOUS'
HOST_INVALID   = 'HOST_INVALID'


def _is_mudaric_form(host: str) -> bool:
    """
    Return True if *host* looks like an Arabic mudāri' (imperfect) verb form.

    Phase A: thin wrapper over is_mudaric_form(build_glyph_traces(host))
    from glyph_classification — the single source of truth.

    Detection: يَ/تَ prefix + fatha on first glyph + sukun on second glyph.
    See glyph_classification.is_mudaric_form() for the authoritative logic.

    G1 CLOSED — NARROW MORPHOLOGICAL LICENSER for current licensed scope.
    See TODO_mabniyat.md for limitations (Forms IV–X not handled).
    """
    return _gc_is_mudaric(_gc_build_traces(host))


def _is_verbal_dual_host(host: str) -> bool:
    """
    Return True if *host* is a plausible past-tense verb form that can take
    ألف الاثنين (ATTACHED_PRONOUN_ALIF_AL_ITHNAYN).

    Phase A: thin wrapper over is_verbal_dual_host(build_glyph_traces(host))
    from glyph_classification — the single source of truth.

    Detection: fatha on first glyph, first glyph ≠ يَ, not definite-article initial.
    See glyph_classification.is_verbal_dual_host() for the authoritative logic.

    G3 CLOSED — TEMPORARY HOST LICENSING HEURISTIC. See TODO_mabniyat.md.
    """
    return _gc_is_verbal_dual(_gc_build_traces(host))


# ─────────────────────────────────────────────────────────────────────────────
# Verbal plural inflectional patterns
# ─────────────────────────────────────────────────────────────────────────────

# Maps a trailing surface pattern to (attached_mabni_id, inflectional_tail, note).
#
# These patterns consist of a GENUINE attached suffix immediately followed by
# an INFLECTIONAL ending that must NOT be classified as an attached pronoun.
# The regular suffix scanner cannot produce these results because it would
# classify the inflectional part as a pronominal suffix.  When the regular
# scanner returns no result, recognize_token tries these patterns as a fallback.
#
# ونَ → واو الجماعة (ATTACHED, depth-guarded و) + نون الرفع (INFLECTIONAL, not NUN_AL_NISWA)
#   يَسْتَطِيعُونَ = يَسْتَطِيعُ + و (WAW_AL_JAMAA) + نَ (inflectional)
_VERBAL_PLURAL_PATTERNS: dict[str, tuple[str, str, str]] = {
    'ونَ': (
        'ATTACHED_PRONOUN_WAW_AL_JAMAA',
        'نَ',
        'ونَ = واو الجماعة (attached) + نون الرفع (inflectional, not NUN_AL_NISWA)',
    ),
    # TODO G2 (deferred — linguistic ambiguity):
    # يَدْعُونَ is ambiguous between:
    #   (A) يَدْعُ + و (WAW_AL_JAMAA) + نَ (نون الرفع) — masc. plural (current treatment)
    #   (B) يَدْعُو (original-و root preserved) + نَ (NUN_AL_NISWA) — fem. plural
    # Resolving (A) vs (B) requires knowing whether و is radical (Hollow/Assimilated root)
    # or a grammatical plural marker.  Current code always resolves as (A) via the ونَ
    # fallback pattern, which is correct for MSA but does not capture the (B) reading.
    # A future morphological ambiguity policy should record both and return AMBIGUOUS/DEFER
    # when the root class cannot be determined from the surface.
    # Constraint: do NOT hard-code a word-specific exception for يَدْعُو here.
}


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HostAnalysis:
    """
    Full analysis of a residual host surface after suffix stripping.

    Returned by _analyze_host() in place of the former plain string.
    Callers use .route for routing decisions and .mabni_id / .operator_id
    for identity reporting (G5).

    Attributes
    ----------
    route : str
        Routing label: EMPTY | OPERATOR_BOUNDARY | MABNI_BOUNDARY |
        MABNI_DEFERRED | OPEN_TO_HR2S
    morpho_class : str
        Morphological class label used by suffix licensing gates:
        HOST_VERBAL | HOST_NOMINAL | HOST_OPERATOR | HOST_MABNI |
        HOST_AMBIGUOUS | HOST_INVALID
    mabni_id : str or None
        mabni_id from the mabniyat catalog if the host matched an entry.
    operator_id : str or None
        operator_id from the operators catalog if the host matched an entry.
    identity_status : str
        DUAL_LICENSED — found in both catalogs
        OPERATOR_ONLY — found only in operators catalog
        MABNI_ONLY    — found only in mabniyat catalog
        NONE          — found in neither (ordinary word or prefix)
    """
    route:            str
    morpho_class:     str   = HOST_AMBIGUOUS
    mabni_id:         Optional[str] = None
    operator_id:      Optional[str] = None
    identity_status:  str   = 'NONE'


@dataclass
class AttachedMabniSpan:
    """One recognized attached mabni form (suffix or prefix) within a token."""
    position:           str          # 'SUFFIX' | 'PREFIX'
    span_start:         int          # char index in normalize()-output (inclusive)
    span_end:           int          # char index in normalize()-output (exclusive)
    surface_matched:    str          # the characters from the token that matched
    catalog_surface:    str          # canonical surface_vocalized from catalog
    mabni_id:           str
    lexical_class:      str
    lexical_family:     str
    source_file:        str
    source_record_id:   str
    is_allomorph:       bool
    allomorph_of:       Optional[str]  # canonical mabni_id if is_allomorph
    notes:              str
    # Phase B (P1_POSITION_CARRIER): raw span in the pre-normalize() surface.
    # None when no alignment map was provided to recognize_token().
    raw_span:           Optional[tuple[int, int]] = None


@dataclass
class TokenAnalysis:
    """
    Full analysis of a token for attached mabniyat.

    Attributes
    ----------
    input_surface : str
        The original token surface passed in.
    structural_verdict : str
        P4 verdict from caller — never modified here.
    whole_token_verdict : str
        verdict from process_mabni(surface, p4_verdict).
    segmentation_verdict : str
        SEGMENTED           — exactly one best segmentation found
        NOT_SEGMENTED       — no attached forms recognized
        AMBIGUOUS           — multiple segmentations tied at max depth
        DEFERRED            — P4 was BLOCK; analysis not attempted
    host_surface : str
        The non-attached residual after stripping prefix+suffix spans.
        Empty string ('') when the token is entirely consumed by
        recognized prefix operator(s) and suffix form(s).
    host_route : str
        OPEN_TO_HR2S        — ordinary Arabic word (→ HR2S)
        MABNI_BOUNDARY      — recognized whole-token mabni form
        OPERATOR_BOUNDARY   — recognized prefix operator / allomorph
        MABNI_DEFERRED      — mabni form with P4=DEFER
        MABNI_BLOCKED       — mabni form with P4=BLOCK
        EMPTY               — no host remains after stripping
    prefix_operators : list[AttachedMabniSpan]
        Recognized prefix operators (position='PREFIX').
    attached_mabniyat : list[AttachedMabniSpan]
        Recognized attached suffix forms (position='SUFFIX'), in
        left-to-right order within the token.
    candidate_segmentations : list
        All surviving candidates when segmentation_verdict='AMBIGUOUS'.
        Each entry is a tuple (host, prefix_ops, suffix_spans, host_route).
    notes : str
        Audit notes.
    """
    input_surface:              str
    structural_verdict:         str
    whole_token_verdict:        str
    segmentation_verdict:       str
    host_surface:               str
    host_route:                 str
    prefix_operators:           list = field(default_factory=list)
    attached_mabniyat:          list = field(default_factory=list)
    candidate_segmentations:    list = field(default_factory=list)
    notes:                      str  = ''
    # ── Extended analysis fields ──────────────────────────────────────────────
    inflectional_tail:          str  = ''
    # The verbal or nominal ending that is NOT an attached pronoun but must
    # still be accounted for.  E.g. 'نَ' in يَسْتَطِيعُونَ (نون الرفع, not
    # NUN_AL_NISWA).  Empty string when no inflectional tail is present.
    original_residual_host:     str  = ''
    # Host surface derived from original_surface (before pipeline normalization).
    # Populated when original_surface is passed to recognize_token() and differs
    # from the normalized surface.  Useful for re-checking the host against
    # catalog entries that use original hamza/shadda forms.
    canonical_residual_host:    str  = ''
    # NFC-normalized form of host_surface.  Used internally by _analyze_host
    # for vocalized catalog lookups; exposed here for auditability.

    # ── G5: Dual lexical identity fields ─────────────────────────────────────
    host_mabni_id:              Optional[str] = None
    # mabni_id from the mabniyat catalog for the residual host, if it matched.
    # Populated even when host_route = OPERATOR_BOUNDARY — operator-first
    # routing does NOT erase a simultaneously licensed mabni identity.
    host_operator_id:           Optional[str] = None
    # operator_id from the operators catalog for the residual host, if matched.
    host_identity_status:       str  = 'NONE'
    # DUAL_LICENSED — host found in both operators and mabniyat catalogs
    # OPERATOR_ONLY — host found only in operators catalog
    # MABNI_ONLY    — host found only in mabniyat catalog
    # NONE          — ordinary word, prefix, or empty


# ─────────────────────────────────────────────────────────────────────────────
# Suffix index
# ─────────────────────────────────────────────────────────────────────────────

# Each entry: (surface_vocalized, row_dict_or_None, is_allomorph, allomorph_of_id)
_SuffixEntry = tuple  # (str, Optional[dict], bool, Optional[str])

_SUFFIX_INDEX_TOP:          Optional[list] = None   # no depth-guarded entries
_SUFFIX_INDEX_CONTINUATION: Optional[list] = None   # includes depth-guarded entries
_SUFFIX_CATALOG_PATH:       Optional[str]  = None


def _build_suffix_index(catalog_path: Optional[str]) -> tuple[list, list]:
    """
    Build two sorted suffix index lists from catalog ATTACHED rows.

    Returns
    -------
    (top_index, continuation_index) where continuation_index includes the
    depth-guarded allomorphs (connected waw).  Both are sorted longest-first.
    """
    cat = load_catalog(catalog_path)
    base: list[_SuffixEntry] = []

    for row in cat['all_rows']:
        if row['surface_kind'] != 'ATTACHED':
            continue
        # Depth-guarded catalog IDs are excluded from the top index;
        # they will be added to the continuation index below.
        if row.get('mabni_id') in _DEPTH_GUARDED_CATALOG_IDS:
            continue
        sv = row['surface_vocalized']
        if not sv.strip():
            continue
        base.append((sv, row, False, None))

    # Depth-guarded allomorphs go only into continuation
    extra: list[_SuffixEntry] = []
    for surface, (target_id, note) in _DEPTH_GUARDED_SUFFIX_ALLOMORPHS.items():
        target_row = cat['by_id'].get(target_id)
        extra.append((surface, target_row, True, target_id))

    # Depth-guarded catalog IDs also go only into continuation
    for dg_id in _DEPTH_GUARDED_CATALOG_IDS:
        dg_row = cat['by_id'].get(dg_id)
        if dg_row:
            sv = dg_row.get('surface_vocalized', '')
            if sv.strip():
                extra.append((sv, dg_row, False, None))

    key = lambda x: len(x[0])
    top          = sorted(base,         key=key, reverse=True)
    continuation = sorted(base + extra, key=key, reverse=True)
    return top, continuation


def _get_suffix_indices(catalog_path: Optional[str] = None) -> tuple[list, list]:
    global _SUFFIX_INDEX_TOP, _SUFFIX_INDEX_CONTINUATION, _SUFFIX_CATALOG_PATH
    if (_SUFFIX_INDEX_TOP is None
            or _SUFFIX_CATALOG_PATH != catalog_path):
        t, c = _build_suffix_index(catalog_path)
        _SUFFIX_INDEX_TOP          = t
        _SUFFIX_INDEX_CONTINUATION = c
        _SUFFIX_CATALOG_PATH       = catalog_path
    return _SUFFIX_INDEX_TOP, _SUFFIX_INDEX_CONTINUATION


def _reset_cache() -> None:
    """Clear the module-level index caches (used by tests after catalog reload)."""
    global _SUFFIX_INDEX_TOP, _SUFFIX_INDEX_CONTINUATION, _SUFFIX_CATALOG_PATH
    _SUFFIX_INDEX_TOP          = None
    _SUFFIX_INDEX_CONTINUATION = None
    _SUFFIX_CATALOG_PATH       = None


# ─────────────────────────────────────────────────────────────────────────────
# Host validity
# ─────────────────────────────────────────────────────────────────────────────

def _host_is_valid(host: str) -> bool:
    """
    Return True if `host` is a plausible Arabic residual after suffix stripping.

    Rules
    -----
    • Empty host → False
    • Recognized prefix operator or allomorph → True (even if short)
    • Otherwise must be ≥ 3 characters (minimum for a CV-C syllable unit)
    """
    if not host:
        return False
    if host in _PREFIX_ALLOMORPHS or host in _CATALOG_PREFIXES:
        return True
    return len(host) >= 3


# ─────────────────────────────────────────────────────────────────────────────
# Recursive suffix stripper
# ─────────────────────────────────────────────────────────────────────────────

def _strip_suffixes(
    surface: str,
    top_index: list,
    cont_index: list,
    depth: int = 0,
    max_depth: int = 3,
) -> list[tuple[str, list]]:
    """
    Recursively identify licensed suffix forms on the right of `surface`.

    Returns
    -------
    List of (host, [AttachedMabniSpan, ...]) for all valid segmentations.
    Suffix spans are in left-to-right order.  Span start/end indices are
    character offsets within the ORIGINAL full token (position 0 = start
    of `surface` at the first call, maintained recursively because the
    host always starts at position 0 of the current `surface` slice which
    itself starts at position 0 of the original).

    Depth semantics
    ---------------
    depth=0 : top-level — only `top_index` is used (no connected-waw allomorph)
    depth≥1 : continuation — `cont_index` is used (connected-waw allomorph allowed)
    """
    if max_depth == 0 or not surface:
        return []

    index = cont_index if depth > 0 else top_index
    results: list = []

    for sv, row, is_allomorph, allomorph_of in index:
        if not surface.endswith(sv):
            continue

        host = surface[: len(surface) - len(sv)]
        if not _host_is_valid(host):
            continue

        # ── Inflectional-vs-pronominal guards ────────────────────────────────
        # Determine the canonical mabni_id for guard checks (allomorphs
        # point to their target ID; regular entries use their own ID).
        mabni_chk = allomorph_of if is_allomorph else (
            row['mabni_id'] if row else ''
        )

        # ── Gate 1: NUN_AL_NISWA — Host Morphological Gate (G1) ──────────────
        # نَ is a pronominal attachment only when the host is morphologically
        # licensed as a verbal form for Nun al-Niswa.
        #
        # و: keep the blanket block because ونَ is handled by the verbal-plural
        # fallback pattern in _not_segmented().  Removing this block would
        # surface the G2 يَدْعُونَ ambiguity (radical-و vs WAW_AL_JAMAA);
        # that case is explicitly deferred (see _VERBAL_PLURAL_PATTERNS TODO).
        #
        # ي/ى: REPLACED — the former "any host ending in ي/ى → reject" rule
        # was too broad: it incorrectly rejected defective-verb forms such as
        # يَرْمِينَ (host يَرْمِي) and يَسْعَيْنَ (host يَسْعَيْ).
        # New rule: reject ONLY when the host is not recognizably a mudāri' form.
        #   يَرْمِي  → _is_mudaric_form() = True  → NUN_AL_NISWA allowed ✓
        #   يَسْعَيْ → _is_mudaric_form() = True  → allowed ✓
        #   نَاءِمِي → _is_mudaric_form() = False → blocked ✓
        #   ءَلْمَسَاكِي → False → blocked ✓
        if mabni_chk == 'ATTACHED_PRONOUN_NUN_AL_NISWA' and host:
            last_b = _last_base_char(host)
            if last_b == 'و':
                continue
            if last_b in ('ي', 'ى') and not _is_mudaric_form(host):
                continue

        # Guard I-B — ATTACHED_PRONOUN_TAU: تُ/تَ/تِ is pronominal ONLY when
        # the residual host does NOT end in ا (alef).
        # Pattern اتُ/اتَ/اتِ = جمع المؤنث السالم, not an attached pronoun.
        # الْحَيَوَانَاتُ → host ءَلْحَيَوَانَا ends in ا → rejected ✓
        if mabni_chk == 'ATTACHED_PRONOUN_TAU' and host:
            last_b = _last_base_char(host)
            if last_b == 'ا':
                continue

        # ── Gate 2: ALIF_AL_ITHNAYN — Host Morphological Gate (G3) ───────────
        # Depth-guarding was replaced by host validation (G3 governance fix).
        # ALIF_AL_ITHNAYN is now available at depth 0, but only when the host
        # is recognizably a past-tense verb form (māḍī).
        #   كَتَبَ → _is_verbal_dual_host() = True  → ALIF_AL_ITHNAYN allowed ✓
        #   ذَهَبَ → True                             → allowed ✓
        #   حِينَمَ → False (kasra on first letter)  → blocked ✓
        if mabni_chk == 'ATTACHED_PRONOUN_ALIF_AL_ITHNAYN' and host:
            if not _is_verbal_dual_host(host):
                continue
        # ── End inflectional/morphological guards ─────────────────────────────

        # Build the AttachedMabniSpan for this suffix
        span_s = len(host)          # offset in original (host always at pos 0)
        span_e = len(surface)

        if is_allomorph:
            target_row = row        # row is the catalog row of the target
            span = AttachedMabniSpan(
                position         = 'SUFFIX',
                span_start       = span_s,
                span_end         = span_e,
                surface_matched  = sv,
                catalog_surface  = (target_row['surface_vocalized']
                                    if target_row else sv),
                mabni_id         = allomorph_of,
                lexical_class    = (target_row['lexical_class']
                                    if target_row else 'ATTACHED_PRONOUN'),
                lexical_family   = (target_row['lexical_family']
                                    if target_row else 'ATTACHED_PRONOUN_SERIES'),
                source_file      = (target_row['source_file']
                                    if target_row else ''),
                source_record_id = (target_row['source_record_id']
                                    if target_row else ''),
                is_allomorph     = True,
                allomorph_of     = allomorph_of,
                notes            = _DEPTH_GUARDED_SUFFIX_ALLOMORPHS.get(sv, ('', ''))[1],
            )
        else:
            span = AttachedMabniSpan(
                position         = 'SUFFIX',
                span_start       = span_s,
                span_end         = span_e,
                surface_matched  = sv,
                catalog_surface  = sv,
                mabni_id         = row['mabni_id'],
                lexical_class    = row['lexical_class'],
                lexical_family   = row['lexical_family'],
                source_file      = row.get('source_file', ''),
                source_record_id = row.get('source_record_id', ''),
                is_allomorph     = False,
                allomorph_of     = None,
                notes            = row.get('notes', ''),
            )

        # Direct result: (host, [this_span])
        results.append((host, [span]))

        # Recurse into the host to find additional (leftward) suffixes
        sub = _strip_suffixes(host, top_index, cont_index,
                               depth=depth + 1, max_depth=max_depth - 1)
        for sub_host, sub_spans in sub:
            # sub_spans are already left-to-right; append current span at right
            results.append((sub_host, sub_spans + [span]))

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Prefix detection
# ─────────────────────────────────────────────────────────────────────────────

def _detect_prefix(host: str) -> tuple[Optional[AttachedMabniSpan], str]:
    """
    If `host` (the residual after suffix stripping) is a recognized prefix
    operator, return (span, '').  Otherwise return (None, host).

    The returned span has position='PREFIX' and span_start=0, span_end=len(host).
    """
    for surface, (op_id, canonical) in _PREFIX_ALLOMORPHS.items():
        if host == surface:
            span = AttachedMabniSpan(
                position         = 'PREFIX',
                span_start       = 0,
                span_end         = len(host),
                surface_matched  = host,
                catalog_surface  = canonical,
                mabni_id         = op_id,
                lexical_class    = 'Closed Function Word',
                lexical_family   = 'PREPOSITION',
                source_file      = 'operators_catalog_split_vocalized.csv',
                source_record_id = '',
                is_allomorph     = True,
                allomorph_of     = _CATALOG_PREFIXES.get(canonical, canonical),
                notes            = f'allomorph of {canonical}',
            )
            return span, ''

    if host in _CATALOG_PREFIXES:
        op_id = _CATALOG_PREFIXES[host]
        span = AttachedMabniSpan(
            position         = 'PREFIX',
            span_start       = 0,
            span_end         = len(host),
            surface_matched  = host,
            catalog_surface  = host,
            mabni_id         = op_id,
            lexical_class    = 'Closed Function Word',
            lexical_family   = 'PREPOSITION',
            source_file      = 'operators_catalog_split_vocalized.csv',
            source_record_id = '',
            is_allomorph     = False,
            allomorph_of     = None,
            notes            = 'single-char preposition prefix',
        )
        return span, ''

    return None, host


# ─────────────────────────────────────────────────────────────────────────────
# Host routing
# ─────────────────────────────────────────────────────────────────────────────

def _analyze_host(
    host: str,
    p4_verdict: str,
    catalog_path: Optional[str],
    original_host: Optional[str] = None,
) -> HostAnalysis:
    """
    Determine the route and full identity of the residual host surface.

    Uses VOCALIZED-ONLY catalog matching.  Bare fallback is intentionally
    skipped to prevent false positives (e.g. أُمِّ vs أَمْ in the bare index).

    Routing priority (operator-first per Guard V):
    1. Empty host          → EMPTY
    2. Known prefix/allomorph → OPERATOR_BOUNDARY
    3. Operators catalog (via original_host if normalized differs)
    4. Mabniyat catalog
    5. Prefix + core re-check (لِأَنَّ → لِ + أَنَّ ∈ operators)
    6. Fallback → OPEN_TO_HR2S

    G5: Both operator and mabni identities are ALWAYS looked up regardless of
    routing priority.  host_mabni_id and host_operator_id are populated
    independently; identity_status encodes whether zero, one, or both matched.
    Operator-first routing (OPERATOR_BOUNDARY) does NOT erase mabni identity.
    """
    if not host:
        return HostAnalysis(route='EMPTY', morpho_class=HOST_INVALID)

    if host in _PREFIX_ALLOMORPHS or host in _CATALOG_PREFIXES:
        return HostAnalysis(route='OPERATOR_BOUNDARY', morpho_class=HOST_OPERATOR,
                            identity_status='OPERATOR_ONLY')

    cat = load_catalog(catalog_path)

    # ── G5: probe BOTH catalogs independently ────────────────────────────────
    found_mabni_id:    Optional[str] = None
    found_operator_id: Optional[str] = None

    # 1. Mabniyat catalog (normalized surface)
    key_v = unicodedata.normalize('NFC', host)
    mabni_row = cat['by_vocalized'].get(key_v)
    if mabni_row:
        found_mabni_id = mabni_row.get('mabni_id')

    # 2. Mabniyat catalog (original surface, if different)
    if original_host and original_host != host:
        key_orig = unicodedata.normalize('NFC', original_host)
        row_orig = cat['by_vocalized'].get(key_orig)
        if row_orig:
            found_mabni_id = row_orig.get('mabni_id')

    # 3. Operators catalog (original surface preferred for أَنَّ type lookups)
    _probe_surface = original_host if (original_host and original_host != host) else host
    if _OPS_LAYER_AVAILABLE:
        try:
            ops_entries = _get_ops_inventory().lookup(_probe_surface)
            if ops_entries:
                if _OPS_PROFILE_AVAILABLE:
                    try:
                        prof = _get_ops_profile(ops_entries[0].surface_vocalized)
                        if prof:
                            found_operator_id = prof.operator_id
                    except Exception:
                        found_operator_id = ops_entries[0].surface_vocalized
                else:
                    found_operator_id = ops_entries[0].surface_vocalized
        except Exception:
            pass

    # Determine identity_status
    if found_operator_id and found_mabni_id:
        identity_status = 'DUAL_LICENSED'
    elif found_operator_id:
        identity_status = 'OPERATOR_ONLY'
    elif found_mabni_id:
        identity_status = 'MABNI_ONLY'
    else:
        identity_status = 'NONE'

    # ── Routing (operator-first) ───────────────────────────────────────────────

    # Operator lookup takes routing priority
    if found_operator_id:
        return HostAnalysis(
            route           = 'OPERATOR_BOUNDARY',
            morpho_class    = HOST_OPERATOR,
            mabni_id        = found_mabni_id,
            operator_id     = found_operator_id,
            identity_status = identity_status,
        )

    # Mabniyat catalog match
    if found_mabni_id:
        if p4_verdict == 'ACCEPT':
            return HostAnalysis(
                route           = 'MABNI_BOUNDARY',
                morpho_class    = HOST_MABNI,
                mabni_id        = found_mabni_id,
                operator_id     = None,
                identity_status = identity_status,
            )
        if p4_verdict == 'DEFER':
            return HostAnalysis(
                route           = 'MABNI_DEFERRED',
                morpho_class    = HOST_MABNI,
                mabni_id        = found_mabni_id,
                operator_id     = None,
                identity_status = identity_status,
            )

    # Guard V — Prefix + core re-check (لِأَنَّهُمْ → لِ + أَنَّ ∈ operators)
    all_prefix_surfaces = (
        list(_CATALOG_PREFIXES.keys()) + list(_PREFIX_ALLOMORPHS.keys())
    )
    for pfx in all_prefix_surfaces:
        pfx_len = len(pfx)
        if not (host.startswith(pfx) and len(host) > pfx_len):
            continue
        core_norm = unicodedata.normalize('NFC', host[pfx_len:])
        if cat['by_vocalized'].get(core_norm):
            return HostAnalysis(route='OPERATOR_BOUNDARY', morpho_class=HOST_OPERATOR,
                                identity_status='OPERATOR_ONLY')
        if original_host and original_host.startswith(pfx) and len(original_host) > pfx_len:
            raw_orig_core = original_host[pfx_len:]
            core_orig = unicodedata.normalize('NFC', raw_orig_core)
            if _OPS_LAYER_AVAILABLE:
                try:
                    if _get_ops_inventory().lookup(raw_orig_core):
                        return HostAnalysis(route='OPERATOR_BOUNDARY',
                                            morpho_class=HOST_OPERATOR,
                                            identity_status='OPERATOR_ONLY')
                except Exception:
                    pass
            if cat['by_vocalized'].get(core_orig):
                return HostAnalysis(route='OPERATOR_BOUNDARY', morpho_class=HOST_OPERATOR,
                                    identity_status='OPERATOR_ONLY')

    # Morphological class for ordinary words (used by callers for suffix gates)
    if _is_mudaric_form(host):
        morpho = HOST_VERBAL
    elif _is_verbal_dual_host(host):
        morpho = HOST_VERBAL
    else:
        morpho = HOST_AMBIGUOUS

    return HostAnalysis(
        route           = 'OPEN_TO_HR2S',
        morpho_class    = morpho,
        mabni_id        = None,
        operator_id     = None,
        identity_status = 'NONE',
    )


def _classify_host(
    host: str,
    p4_verdict: str,
    catalog_path: Optional[str],
    original_host: Optional[str] = None,
) -> str:
    """Backward-compatible wrapper: returns just the route string."""
    return _analyze_host(host, p4_verdict, catalog_path, original_host).route


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def _project_spans_to_raw(
    spans: list['AttachedMabniSpan'],
    alignment: object,
) -> list['AttachedMabniSpan']:
    """
    Phase B helper: project normalized span_start/span_end to raw coordinates.

    Returns a new list of AttachedMabniSpan with raw_span populated.
    alignment must be a SpanAlignmentMap from normalize_tracked().
    """
    import dataclasses
    result = []
    for sp in spans:
        raw_s, raw_e = alignment.project_to_raw(sp.span_start, sp.span_end)
        result.append(dataclasses.replace(sp, raw_span=(raw_s, raw_e)))
    return result


def recognize_token(
    surface: str,
    p4_structural_verdict: str,
    catalog_path: Optional[str] = None,
    original_surface: Optional[str] = None,
    alignment=None,
) -> TokenAnalysis:
    """
    Recognize attached mabniyat in a token.

    Calls process_mabni() first.  If the whole-token lookup succeeds (or
    returns MABNI_BLOCKED), returns immediately without suffix analysis.
    Otherwise performs greedy right-to-left suffix stripping.

    Parameters
    ----------
    surface : str
        Arabic surface token after pipeline normalization (hamza-collapsed,
        shadda-expanded).  Used for suffix scanning.
    p4_structural_verdict : str
        'ACCEPT' | 'DEFER' | 'BLOCK' from P4 slot engineering.
    catalog_path : str, optional
        Path to mabniyat_catalog_split_vocalized.csv; uses module default.
    original_surface : str, optional
        The pre-normalization surface (input_surface from the pipeline).
        When provided and different from ``surface``, the whole-token catalog
        lookup tries ``original_surface`` first.  This recovers entries whose
        catalog keys use the original hamza forms (أ/إ/آ) or shadda (ّ) that
        the normalizer converts to ء or doubled letters, preventing the suffix
        scanner from falsely segmenting standalone mabni tokens.
    alignment : SpanAlignmentMap, optional (Phase B)
        Alignment map from normalize_tracked() mapping raw surface positions
        to normalize()-output positions.  When provided, each AttachedMabniSpan
        in the result will have raw_span populated with precise raw coordinates.
        When None, raw_span remains None (Phase A behaviour, unchanged).

    Returns
    -------
    TokenAnalysis
    """
    # ── 1. P4 BLOCK: skip suffix analysis entirely ───────────────────────────
    # P4 Monotonicity law: BLOCK is the terminal structural verdict.
    # segmentation_verdict='BLOCKED' (distinct from DEFERRED, which applies
    # only to P4 DEFER).  This check runs before catalog lookup so that
    # MABNI_BLOCKED from process_mabni never short-circuits into the
    # whole-token branch below and incorrectly returns NOT_SEGMENTED.
    if p4_structural_verdict == 'BLOCK':
        return TokenAnalysis(
            input_surface           = surface,
            structural_verdict      = p4_structural_verdict,
            whole_token_verdict     = 'MABNI_BLOCKED',
            segmentation_verdict    = 'BLOCKED',
            host_surface            = surface,
            host_route              = 'OPEN_TO_HR2S',
            notes                   = 'P4 BLOCK — attachment analysis skipped',
        )

    # ── 2. Whole-token lookup ─────────────────────────────────────────────────
    # Try original_surface first (if it differs from normalized surface).
    # The mabniyat catalog is indexed on canonical Arabic forms with original
    # hamza (أ/إ/آ) and shadda (ّ).  The pipeline's normalize() converts these
    # to ء and doubled consonants, so a lookup on the normalized form misses
    # catalog entries — causing the suffix scanner to run on standalone mabnis
    # (FALSE_SUFFIX_SCAN).  Trying original_surface first recovers the match.
    whole = None
    if original_surface and original_surface != surface:
        _w = process_mabni(original_surface, p4_structural_verdict)
        if _w.verdict != 'MABNI_NOT_FOUND':
            whole = _w
    if whole is None:
        whole = process_mabni(surface, p4_structural_verdict)

    if whole.verdict != 'MABNI_NOT_FOUND':
        route_map = {
            'MABNI_BOUNDARY': 'MABNI_BOUNDARY',
            'MABNI_DEFERRED': 'MABNI_DEFERRED',
        }
        return TokenAnalysis(
            input_surface           = surface,
            structural_verdict      = p4_structural_verdict,
            whole_token_verdict     = whole.verdict,
            segmentation_verdict    = 'NOT_SEGMENTED',
            host_surface            = surface,
            host_route              = route_map.get(whole.verdict, 'OPEN_TO_HR2S'),
            prefix_operators        = [],
            attached_mabniyat       = [],
            candidate_segmentations = [],
            notes                   = f'whole-token match: {whole.mabni_id}',
        )

    # ── 3. Build suffix index and strip ──────────────────────────────────────
    top_idx, cont_idx = _get_suffix_indices(catalog_path)
    raw_segs = _strip_suffixes(surface, top_idx, cont_idx)

    def _not_segmented(note: str) -> TokenAnalysis:
        """Return a NOT_SEGMENTED result, trying verbal plural patterns first."""
        # ── 3a. Verbal plural pattern fallback ───────────────────────────────
        # The regular scanner cannot produce WAW_AL_JAMAA + inflectional نَ
        # because (a) the NUN_AL_NISWA guard rejects نَ when the host ends in
        # و, and (b) WAW_AL_JAMAA is depth-guarded (only tried after depth 0).
        # When the surface ends in a known verbal plural pattern (ونَ), we
        # produce the correct attached+inflectional decomposition here.
        cat = load_catalog(catalog_path)
        for vp_sfx, (waw_id, inf_tail, vp_note) in _VERBAL_PLURAL_PATTERNS.items():
            if not surface.endswith(vp_sfx):
                continue
            attached_sv = vp_sfx[:len(vp_sfx) - len(inf_tail)]   # 'و'
            host_cand   = surface[:len(surface) - len(vp_sfx)]
            if not _host_is_valid(host_cand):
                continue
            waw_row = cat['by_id'].get(waw_id)
            if not waw_row:
                continue
            # Derive original host candidate for enhanced catalog lookup
            orig_host_cand: Optional[str] = None
            if original_surface:
                vp_len = len(vp_sfx)   # ونَ is same in original + normalized
                if vp_len <= len(original_surface):
                    orig_host_cand = original_surface[:len(original_surface) - vp_len]
            span_s = len(host_cand)
            waw_span = AttachedMabniSpan(
                position         = 'SUFFIX',
                span_start       = span_s,
                span_end         = span_s + len(attached_sv),
                surface_matched  = attached_sv,
                catalog_surface  = waw_row['surface_vocalized'],
                mabni_id         = waw_id,
                lexical_class    = waw_row['lexical_class'],
                lexical_family   = waw_row['lexical_family'],
                source_file      = waw_row.get('source_file', ''),
                source_record_id = waw_row.get('source_record_id', ''),
                is_allomorph     = True,
                allomorph_of     = waw_id,
                notes            = vp_note,
            )
            vp_ha = _analyze_host(
                host_cand, p4_structural_verdict, catalog_path,
                original_host=orig_host_cand,
            )
            # Phase B: project waw_span to raw coordinates if alignment provided
            _vp_attached = ([waw_span] if alignment is None
                            else _project_spans_to_raw([waw_span], alignment))
            return TokenAnalysis(
                input_surface           = surface,
                structural_verdict      = p4_structural_verdict,
                whole_token_verdict     = whole.verdict,
                segmentation_verdict    = 'SEGMENTED',
                host_surface            = host_cand,
                host_route              = vp_ha.route,
                prefix_operators        = [],
                attached_mabniyat       = _vp_attached,
                candidate_segmentations = [],
                inflectional_tail       = inf_tail,
                original_residual_host  = orig_host_cand or '',
                canonical_residual_host = unicodedata.normalize('NFC', host_cand),
                host_mabni_id           = vp_ha.mabni_id,
                host_operator_id        = vp_ha.operator_id,
                host_identity_status    = vp_ha.identity_status,
                notes                   = vp_note,
            )
        # No verbal plural pattern matched — truly not segmented
        return TokenAnalysis(
            input_surface           = surface,
            structural_verdict      = p4_structural_verdict,
            whole_token_verdict     = whole.verdict,
            segmentation_verdict    = 'NOT_SEGMENTED',
            host_surface            = surface,
            host_route              = 'OPEN_TO_HR2S',
            notes                   = note,
        )

    if not raw_segs:
        # Fix 2: Conjunctive proclitic fallback ─────────────────────────────
        # فَغَارَتْ and similar: تْ (past-tense feminine suffix) is absent from
        # the suffix catalog, so the main scanner finds nothing.  If the surface
        # starts with a conjunctive proclitic (فَ/وَ) and the next consonant
        # carries a full vowel (not sukuun), strip the proclitic and route the
        # remainder to the root engine.
        # Guard: remainder ≥ 3 chars AND remainder[1] ≠ sukuun (prevents
        # stripping وَ from وَحْدَ where حْ has sukuun).
        for pfx_sv in _CONJUNCTIVE_PROCLITICS:
            if not surface.startswith(pfx_sv):
                continue
            remainder = surface[len(pfx_sv):]
            # Guard 1: remainder must be long enough to be a meaningful host
            if len(remainder) < 3:
                continue
            # Guard 2: second char of remainder (vowel position) must NOT be sukuun
            if remainder[1] == _SUKUN:
                continue
            # Build prefix operator span
            op_id = _CATALOG_PREFIXES[pfx_sv]
            pfx_span = AttachedMabniSpan(
                position         = 'PREFIX',
                span_start       = 0,
                span_end         = len(pfx_sv),
                surface_matched  = pfx_sv,
                catalog_surface  = pfx_sv,
                mabni_id         = op_id,
                lexical_class    = 'Closed Function Word',
                lexical_family   = 'CONJUNCTION',
                source_file      = 'operators_catalog_split_vocalized.csv',
                source_record_id = '',
                is_allomorph     = False,
                allomorph_of     = None,
                notes            = 'Fix2: conjunctive proclitic stripped from NOT_SEGMENTED host',
            )
            # Compute original-surface remainder
            orig_remainder: Optional[str] = None
            if original_surface and original_surface.startswith(pfx_sv):
                orig_remainder = original_surface[len(pfx_sv):]
            # Analyze the remainder as a standalone host
            rem_ha = _analyze_host(
                remainder, p4_structural_verdict, catalog_path,
                original_host=orig_remainder,
            )
            # Project prefix span to raw coords if alignment provided
            _pfx_ops = ([pfx_span] if alignment is None
                        else _project_spans_to_raw([pfx_span], alignment))
            return TokenAnalysis(
                input_surface           = surface,
                structural_verdict      = p4_structural_verdict,
                whole_token_verdict     = whole.verdict,
                segmentation_verdict    = 'SEGMENTED',
                host_surface            = remainder,
                host_route              = rem_ha.route,
                prefix_operators        = _pfx_ops,
                attached_mabniyat       = [],
                candidate_segmentations = [],
                original_residual_host  = orig_remainder or '',
                canonical_residual_host = unicodedata.normalize('NFC', remainder),
                host_mabni_id           = rem_ha.mabni_id,
                host_operator_id        = rem_ha.operator_id,
                host_identity_status    = rem_ha.identity_status,
                notes                   = f'Fix2: proclitic {pfx_sv!r} stripped; host={remainder!r}',
            )
        return _not_segmented('no suffix match')

    # ── 3b. Multi-span validity guard ────────────────────────────────────────
    # A segmentation with more than one suffix span is only accepted when at
    # least one non-rightmost span is either:
    #   (a) a depth-guarded allomorph (connected-waw و), OR
    #   (b) listed in _MULTI_SPAN_VALID_IDS (ALIF_AL_ITHNAYN after G3 fix).
    # This prevents coincidental sub-splits of whole licensed suffixes:
    #
    #   حُبِّنَا: نَ + ا (REJECTED — ا alone is not licensed as left-span here)
    #            نَا    (ACCEPTED — single licensed form)
    #
    #   فَقَدُوهُ: و + هُ (ACCEPTED — و is a depth-guarded allomorph)
    #   كَتَبَاهُ: ا + هُ (ACCEPTED — ا is in _MULTI_SPAN_VALID_IDS)
    def _valid_multi(spans):
        if len(spans) <= 1:
            return True
        # spans are left-to-right; check all except the rightmost
        for sp in spans[:-1]:
            if sp.is_allomorph and sp.surface_matched in _DEPTH_GUARDED_SUFFIX_ALLOMORPHS:
                return True
            if sp.mabni_id in (_DEPTH_GUARDED_CATALOG_IDS | _MULTI_SPAN_VALID_IDS):
                return True
        return False

    raw_segs = [(h, s) for h, s in raw_segs if _valid_multi(s)]

    if not raw_segs:
        return _not_segmented('no valid suffix match after multi-span guard')

    # ── 4. Enrich candidates with prefix detection + host routing ─────────────
    # Candidate tuple: (actual_host, prefix_ops, suffix_spans, host_route, orig_host)
    candidates: list[tuple] = []
    for raw_host, suffix_spans in raw_segs:
        prefix_span, actual_host = _detect_prefix(raw_host)
        prefix_ops = [prefix_span] if prefix_span else []

        # Compute the pre-normalization host for enhanced _classify_host lookup.
        # Suffix surfaces are identical in both original and normalized forms
        # (haa-family pronouns and most other ATTACHED forms do not contain
        # hamza or shadda, so their lengths are equal in both).  Therefore
        # the original host can be recovered by slicing original_surface from
        # the right by the same total suffix character count.
        orig_actual_host: Optional[str] = None
        if original_surface:
            total_sv = sum(len(sp.surface_matched) for sp in suffix_spans)
            if total_sv <= len(original_surface):
                orig_raw = original_surface[:len(original_surface) - total_sv]
                if prefix_span:
                    pfx_sv = prefix_span.surface_matched
                    if orig_raw.startswith(pfx_sv) and len(orig_raw) > len(pfx_sv):
                        orig_actual_host = orig_raw[len(pfx_sv):]
                    elif orig_raw == pfx_sv:
                        orig_actual_host = ''
                    else:
                        orig_actual_host = orig_raw
                else:
                    orig_actual_host = orig_raw

        # Use _analyze_host for full G5 identity data
        ha = _analyze_host(
            actual_host, p4_structural_verdict, catalog_path,
            original_host=orig_actual_host,
        )
        # Candidate tuple extended: (..., host_analysis)
        candidates.append((actual_host, prefix_ops, suffix_spans, ha.route,
                           orig_actual_host, ha))

    # ── 4b. Structural host guard (G4: P4 Monotonicity) ──────────────────────
    # Partition candidates into accepted and deferred sets.
    # MABNI_DEFERRED candidates are NOT discarded: when they are the only
    # survivors, we return a deferred TokenAnalysis that preserves structural
    # state rather than silently routing to OPEN_TO_HR2S.
    accepted_cands  = [c for c in candidates if c[3] != 'MABNI_DEFERRED']
    deferred_cands  = [c for c in candidates if c[3] == 'MABNI_DEFERRED']

    if not accepted_cands:
        if deferred_cands:
            # G4: all surviving segmentations have a deferred host.
            # Pick the deepest / longest-suffix candidate and return DEFERRED.
            # structural_verdict and host_route remain DEFER/MABNI_DEFERRED —
            # the token must NOT be routed to HR2S.
            best = max(deferred_cands,
                       key=lambda c: (len(c[2]),
                                      sum(len(s.surface_matched) for s in c[2])))
            d_host, d_pfx, d_sfx, d_route, d_orig, d_ha = best
            return TokenAnalysis(
                input_surface           = surface,
                structural_verdict      = p4_structural_verdict,
                whole_token_verdict     = whole.verdict,
                segmentation_verdict    = 'DEFERRED',
                host_surface            = d_host,
                host_route              = 'MABNI_DEFERRED',
                prefix_operators        = d_pfx,
                attached_mabniyat       = d_sfx,
                candidate_segmentations = [],
                original_residual_host  = d_orig or '',
                canonical_residual_host = unicodedata.normalize('NFC', d_host) if d_host else '',
                host_mabni_id           = d_ha.mabni_id,
                host_operator_id        = d_ha.operator_id,
                host_identity_status    = d_ha.identity_status,
                notes                   = 'DEFERRED: all candidates have MABNI_DEFERRED host; '
                                          'structural verdict preserved, not routed to HR2S',
            )
        return _not_segmented('all candidates rejected: REJECTED_STRUCTURAL_HOST')
    candidates = accepted_cands

    # ── 5. Deduplicate ────────────────────────────────────────────────────────
    seen: set = set()
    unique: list = []
    for c in candidates:
        key = (c[0], tuple(s.mabni_id for s in c[1]), tuple(s.mabni_id for s in c[2]))
        if key not in seen:
            seen.add(key)
            unique.append(c)

    # ── 6. Prefer maximal suffix stripping, then longest total suffix chars ────
    max_depth = max(len(c[2]) for c in unique)
    top = [c for c in unique if len(c[2]) == max_depth]

    if len(top) > 1:
        total_len = lambda c: sum(len(s.surface_matched) for s in c[2])
        max_char_len = max(total_len(c) for c in top)
        top = [c for c in top if total_len(c) == max_char_len]

    if len(top) == 1:
        actual_host, prefix_ops, suffix_spans, host_route, orig_host, ha = top[0]
        # Phase B: project spans to raw coordinates if alignment provided
        if alignment is not None:
            suffix_spans = _project_spans_to_raw(suffix_spans, alignment)
            prefix_ops   = _project_spans_to_raw(prefix_ops,   alignment)
        return TokenAnalysis(
            input_surface           = surface,
            structural_verdict      = p4_structural_verdict,
            whole_token_verdict     = whole.verdict,
            segmentation_verdict    = 'SEGMENTED',
            host_surface            = actual_host,
            host_route              = host_route,
            prefix_operators        = prefix_ops,
            attached_mabniyat       = suffix_spans,
            candidate_segmentations = [],
            original_residual_host  = orig_host or '',
            canonical_residual_host = unicodedata.normalize('NFC', actual_host) if actual_host else '',
            host_mabni_id           = ha.mabni_id,
            host_operator_id        = ha.operator_id,
            host_identity_status    = ha.identity_status,
            notes                   = (
                f'{len(suffix_spans)} suffix(es) recognized'
                + (f'; {len(prefix_ops)} prefix operator(s)' if prefix_ops else '')
            ),
        )

    # ── 7. Genuinely ambiguous at max depth ──────────────────────────────────
    return TokenAnalysis(
        input_surface           = surface,
        structural_verdict      = p4_structural_verdict,
        whole_token_verdict     = whole.verdict,
        segmentation_verdict    = 'AMBIGUOUS',
        host_surface            = '',
        host_route              = '',
        prefix_operators        = [],
        attached_mabniyat       = [],
        candidate_segmentations = [(h, p, s, r) for h, p, s, r, _, _ha in top],
        notes                   = f'{len(top)} competing segmentations at depth {max_depth}',
    )


# ─────────────────────────────────────────────────────────────────────────────
# Quick smoke-test when run directly
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    tests = [
        ('يُعَوِّضَهُمْ', 'ACCEPT'),
        ('فَقَدُوهُ',     'ACCEPT'),
        ('أُمِّهِمْ',    'ACCEPT'),
        ('حُبِّهَا',     'ACCEPT'),
        ('لَهُمْ',       'ACCEPT'),
        ('هُ',           'ACCEPT'),   # whole-token ATTACHED — should not recurse
        ('مَا',          'ACCEPT'),   # negative: maa → NOT_SEGMENTED
        ('أَبُو',        'ACCEPT'),   # negative: abuu → NOT_SEGMENTED (waw guard)
        ('عَلِمَ',       'ACCEPT'),   # negative: no suffix match
    ]
    print()
    for surface, p4 in tests:
        r = recognize_token(surface, p4)
        attached = [s.mabni_id for s in r.attached_mabniyat]
        prefix   = [s.mabni_id for s in r.prefix_operators]
        print(
            f"  {surface!r:22} P4={p4:6} "
            f"seg={r.segmentation_verdict:15} "
            f"host={r.host_surface!r:16} "
            f"route={r.host_route:20} "
            f"prefix={prefix} "
            f"attached={attached}"
        )
