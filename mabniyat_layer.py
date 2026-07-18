#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mabniyat_layer.py — Governed Mabniyat Catalog Lookup (Phase 5)
═══════════════════════════════════════════════════════════════

Standalone module: no imports from existing hokom modules.

P4 Monotonicity Law (absolute):
  BLOCK  → MABNI_BLOCKED   (catalog match never overrides)
  DEFER  → MABNI_DEFERRED  (catalog match confirms identity; verdict stays DEFERRED)
  ACCEPT → MABNI_BOUNDARY  (catalog match confirms; verdict becomes BOUNDARY)
  not found → MABNI_NOT_FOUND (structural_verdict unchanged)
"""
from dataclasses import dataclass
from typing import Optional
import csv, unicodedata, os, re
from glyph_classification import build_glyph_traces as _build_glyph_traces

# ─────────────────────────────────────────────────────────
# Unicode utilities
# ─────────────────────────────────────────────────────────

# DEPRECATED (Phase A): parallel diacritic pattern — will consolidate into
# glyph_classification.MarkClass as the single source of truth.
# Do not expand this pattern; use build_glyph_traces() in new code.
DIACRITICS = re.compile(r'[ً-ٰٟـ]')

def strip_diacritics(s: str) -> str:
    """Remove Arabic diacritics (tashkeel) from a string."""
    return DIACRITICS.sub('', s)


def _parse_char_diac_pairs(s: str) -> list:
    """
    Split an NFC-normalized Arabic string into (base_char, diacritics) pairs.
    Each pair = one non-combining base character + all immediately following
    combining marks (diacritics).

    Phase A: now a thin wrapper over build_glyph_traces() from
    glyph_classification — the single source of truth for Unicode character
    typing.  The return type and contract are unchanged: callers receive the
    same list of (str, str) pairs as before.

    Example:
        'هُوِ' -> [('ه', 'ُ'), ('و', 'ِ')]
        'هو'   -> [('ه', ''),  ('و', '')]
    """
    return [
        (t.nfc_base, ''.join(t.nfc_marks))
        for t in _build_glyph_traces(s)
    ]


def _explicit_marks_compatible(input_surface: str, candidate_surface: str) -> bool:
    """
    Return True iff the explicit diacritics present in input_surface are
    compatible with candidate_surface.

    Rule: for every position where input has an explicit diacritic, that
    diacritic must match the candidate's diacritic at the same position.
    Positions where input has NO diacritics impose no constraint.

    Length mismatch -> always incompatible.

    Examples:
        input='هُوِ'  candidate='هُوَ'  -> INCOMPATIBLE (waw: kasra vs fatha)
        input='هو'    candidate='هُوَ'  -> COMPATIBLE   (no explicit marks)
        input='هُوَ'  candidate='هُوَ'  -> COMPATIBLE   (all match)
        input='هَوَ'  candidate='هُوَ'  -> INCOMPATIBLE (ha: fatha vs damma)
    """
    input_pairs = _parse_char_diac_pairs(input_surface)
    cand_pairs  = _parse_char_diac_pairs(candidate_surface)

    if len(input_pairs) != len(cand_pairs):
        return False

    for (ic, id_), (cc, cd_) in zip(input_pairs, cand_pairs):
        if ic != cc:
            return False
        if id_ and id_ != cd_:
            # One exception: sukun (ْ) on a long-vowel letter (ياء/واو) is
            # orthographically equivalent to no diacritic on the same letter
            # when the catalog has no constraint at that position.  This
            # handles forms like الَّذِيْنَ (explicit sukun on madd-yaa) vs
            # the catalog entry الَّذِينَ (no sukun), which are the same word.
            # This exception does NOT relax mismatches between two explicit
            # diacritics (e.g., kasra vs fatha on واو still fails).
            if id_ == 'ْ' and cd_ == '' and ic in ('ي', 'و'):
                continue   # sukun on ياء/واو vs empty — compatible
            return False

    return True


def normalize_key(s: str) -> str:
    """Unicode-order-invariant NFC lookup key."""
    return unicodedata.normalize('NFC', s)


# ─────────────────────────────────────────────────────────
# Result type
# ─────────────────────────────────────────────────────────

@dataclass
class MabniResult:
    """
    Result returned by process_mabni().

    verdict:
        MABNI_BOUNDARY  — found in catalog + P4 ACCEPT
        MABNI_DEFERRED  — found in catalog + P4 DEFER
        MABNI_BLOCKED   — P4 BLOCK (catalog never consulted)
        MABNI_NOT_FOUND — not in catalog

    structural_verdict:
        The P4 verdict as passed in — never modified by this layer.
    """
    verdict:            str
    structural_verdict: str
    mabni_id:           Optional[str]
    surface_kind:       Optional[str]
    lexical_class:      Optional[str]
    lexical_family:     Optional[str]
    blocks_root_path:   bool
    contract_state:     Optional[str]
    input_surface:      str
    matched_surface:    Optional[str]
    source_file:        Optional[str]


# ─────────────────────────────────────────────────────────
# Catalog loader
# ─────────────────────────────────────────────────────────

_CATALOG: Optional[dict] = None
_CATALOG_PATH: Optional[str] = None


def _default_catalog_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, 'mabniyat_catalog_split_vocalized.csv')


def load_catalog(path: str = None) -> dict:
    """
    Load mabniyat catalog into lookup dicts.

    Returns a dict with keys:
      'by_vocalized': dict[nfc(surface_vocalized) → row]
      'by_bare':      dict[bare(surface_vocalized) → row]
      'by_id':        dict[mabni_id → row]
      'all_rows':     list[row_dict]

    Both vocalized and bare lookups use the first (canonical) entry
    for each surface to avoid ambiguity.  Surface_kind=LATENT rows
    are excluded from token lookups (they have empty surfaces).
    """
    global _CATALOG, _CATALOG_PATH
    if path is None:
        path = _default_catalog_path()
    if _CATALOG is not None and _CATALOG_PATH == path:
        return _CATALOG

    by_vocalized: dict = {}
    by_bare:      dict = {}
    by_id:        dict = {}
    all_rows:     list = []

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            all_rows.append(r)
            mid = r['mabni_id']
            by_id[mid] = r

            sv = r['surface_vocalized']
            sk = r['surface_kind']

            # Only index overt/attached/phrase surfaces, not latent (empty)
            if sk == 'LATENT' or not sv.strip():
                continue

            key_v = normalize_key(sv)
            key_b = strip_diacritics(key_v)

            if key_v not in by_vocalized:
                by_vocalized[key_v] = r
            if key_b not in by_bare:
                by_bare[key_b] = r

    _CATALOG = {
        'by_vocalized': by_vocalized,
        'by_bare':      by_bare,
        'by_id':        by_id,
        'all_rows':     all_rows,
    }
    _CATALOG_PATH = path
    return _CATALOG


# ─────────────────────────────────────────────────────────
# Core lookup
# ─────────────────────────────────────────────────────────

def _lookup(surface: str, catalog: dict) -> Optional[dict]:
    """
    Three-phase lookup:
      Phase 1 — direct NFC match of surface_vocalized
      Phase 2 — bare (diacritic-stripped) match
    Returns the matched catalog row or None.
    """
    if not surface.strip():
        return None

    key_v = normalize_key(surface)
    row = catalog['by_vocalized'].get(key_v)
    if row:
        return row

    # Phase 2: bare match — only accepted when explicit diacritics in
    # input are compatible with the candidate (prevent هُوِ matching هُوَ).
    key_b = strip_diacritics(key_v)
    row = catalog['by_bare'].get(key_b)
    if row and _explicit_marks_compatible(key_v, row['surface_vocalized']):
        return row

    return None


# ─────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────

def process_mabni(surface: str, p4_structural_verdict: str) -> MabniResult:
    """
    Look up a surface form in the mabniyat catalog and apply P4 monotonicity.

    Parameters
    ----------
    surface : str
        The Arabic surface string to look up (may be vocalized or bare).
    p4_structural_verdict : str
        The verdict from P4 slot engineering: 'ACCEPT', 'DEFER', or 'BLOCK'.

    Returns
    -------
    MabniResult with one of four verdicts:
        MABNI_BLOCKED   — if p4_structural_verdict == 'BLOCK'
        MABNI_BOUNDARY  — found in catalog and p4 == 'ACCEPT'
        MABNI_DEFERRED  — found in catalog and p4 == 'DEFER'
        MABNI_NOT_FOUND — not found in catalog

    P4 Monotonicity (absolute):
        A catalog match NEVER promotes structural_verdict.
        BLOCK stays BLOCK regardless of catalog.
        DEFER stays DEFER even if the form is found.
    """
    # ── Rule 1: BLOCK is absolute — do not even consult catalog ──────────────
    if p4_structural_verdict == 'BLOCK':
        return MabniResult(
            verdict            = 'MABNI_BLOCKED',
            structural_verdict = 'BLOCK',
            mabni_id           = None,
            surface_kind       = None,
            lexical_class      = None,
            lexical_family     = None,
            blocks_root_path   = False,
            contract_state     = None,
            input_surface      = surface,
            matched_surface    = None,
            source_file        = None,
        )

    # ── Rule 2: Consult catalog ───────────────────────────────────────────────
    cat = load_catalog()
    matched = _lookup(surface, cat)

    if matched:
        blk = matched.get('blocks_root_path', 'True').lower() == 'true'
        verdict = ('MABNI_BOUNDARY' if p4_structural_verdict == 'ACCEPT'
                   else 'MABNI_DEFERRED')
        return MabniResult(
            verdict            = verdict,
            structural_verdict = p4_structural_verdict,
            mabni_id           = matched['mabni_id'],
            surface_kind       = matched['surface_kind'],
            lexical_class      = matched['lexical_class'],
            lexical_family     = matched['lexical_family'],
            blocks_root_path   = blk,
            contract_state     = matched.get('contract_state'),
            input_surface      = surface,
            matched_surface    = matched['surface_vocalized'],
            source_file        = matched.get('source_file'),
        )

    # ── Rule 3: Not found — pass through with original structural_verdict ─────
    return MabniResult(
        verdict            = 'MABNI_NOT_FOUND',
        structural_verdict = p4_structural_verdict,
        mabni_id           = None,
        surface_kind       = None,
        lexical_class      = None,
        lexical_family     = None,
        blocks_root_path   = False,
        contract_state     = None,
        input_surface      = surface,
        matched_surface    = None,
        source_file        = None,
    )


# ─────────────────────────────────────────────────────────
# Convenience helpers
# ─────────────────────────────────────────────────────────

def get_all_rows() -> list:
    """Return all catalog rows as list of dicts."""
    return load_catalog()['all_rows']

def get_by_id(mabni_id: str) -> Optional[dict]:
    """Return a catalog row by mabni_id."""
    return load_catalog()['by_id'].get(mabni_id)

def get_all_overt_surfaces() -> set:
    """Return all bare (diacritic-stripped) surfaces of OVERT/ATTACHED/PHRASE entries."""
    return set(load_catalog()['by_bare'].keys())


if __name__ == '__main__':
    tests = [
        ('هَذَا', 'ACCEPT'),
        ('بِ', 'ACCEPT'),
        ('الَّذِي', 'ACCEPT'),
        ('إِنَّ', 'ACCEPT'),
        ('نَعَمْ', 'ACCEPT'),
        ('هُوَ', 'DEFER'),
        ('هُوَ', 'BLOCK'),
        ('يَعْمَلُ', 'ACCEPT'),
        ('', 'ACCEPT'),
    ]
    print()
    for surface, p4 in tests:
        r = process_mabni(surface, p4)
        print(f"  {surface!r:20} P4={p4:6} → {r.verdict:18} id={r.mabni_id}")
