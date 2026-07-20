#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jamid_aalam_boundary.py — الجامد والعلم: حاجز قبل مسار الجذر
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOKOM-JAMID-AALAM-LEXICAL-BOUNDARY-CLOSURE-01

Purpose:
  Intercepts segment_host BEFORE root admission to classify jawamid/aalam
  forms that must NOT enter the trilateral root engine.

  الله and its forms (اللَّهُ / اللَّهَ / اللَّهِ / and proclitic forms)
  are MU'RAB (inflected: مرفوع/منصوب/مجرور) — NOT MABNI.
  They must NEVER enter mabni_inventory or be handled via MabniBoundary.
  However, they are JAWAMID (specifically: اسم علم، اسم ذات) with NO licensed
  root/wazn in the primary analysis path.

Design:
  - Lookup on segment_host ONLY (never original_surface).
  - Normalize segment_host: strip vowel marks, preserve shadda (ّ) for
    precise matching. This allows اللّه to match اللَّهُ/اللَّهَ/اللَّهِ
    and لّه to match لَّهِ (the host of لِلَّهِ after لِ proclitic stripping).
  - Data-driven from jawamid.xlsx (Jawamid_Classification sheet) + minimal
    aalam_forms seed catalog.
  - Idempotent, no mutation.

Route name: JAMID_AALAM_BOUNDARY
  Distinct from: MABNI_BOUNDARY, OPERATOR_BOUNDARY.

Critical: الله is MU'RAB — this route MUST NOT add it to mabni_inventory.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

# ── Diacritic constants ───────────────────────────────────────────────────────

_ARABIC_DIACRITICS = frozenset('ًٌٍَُِّْٰ')
_SHADDA            = 'ّ'   # ّ U+0651 — الشدة


def _strip_vowels_keep_shadda(s: str) -> str:
    """
    Strip Arabic diacritics but preserve shadda (ّ).
    Used for lookup key normalization.

    Examples:
      'اللَّهُ' → 'اللّه'   (ُ and َ stripped, ّ kept)
      'لَّهِ'   → 'لّه'    (َ and ِ stripped, ّ kept)
      'كَاتِبٌ' → 'كاتب'   (all diacritics stripped, no shadda present)
    """
    return ''.join(c for c in s if c not in _ARABIC_DIACRITICS or c == _SHADDA)


def _strip_all_diacritics(s: str) -> str:
    """Strip all Arabic diacritics including shadda. Used for bare fallback lookup."""
    return ''.join(c for c in s if c not in _ARABIC_DIACRITICS)


# ── Result dataclasses ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class JamidAalamBoundary:
    """
    Returned when segment_host is identified as a jawamid/aalam form that
    must NOT enter the root engine.

    blocks_root_path=True closes root/wazn/bab/derivative admission.
    The form remains MU'RAB — i3rab (declension) is not affected.
    """
    input_surface:         str            # segment_host as received (immutable)
    matched_bare:          str            # normalized key used for lookup
    lexical_identity:      str            # canonical lemma (الله, إبراهيم, ...)
    jamid_category:        str            # اسم علم | اسم ذات | ...
    aalam_category:        Optional[str]  # divine_name | prophet_name | proper_name | None
    requires_root_pattern: bool           = False
    verdict:               str            = 'JAMID_AALAM_BOUNDARY'
    source:                str            = 'jawamid_index'
    blocks_root_path:      bool           = True


@dataclass(frozen=True)
class JamidAalamOpen:
    """
    Returned when segment_host is NOT a recognized jawamid/aalam form.
    Root admission proceeds normally through the existing pipeline.
    """
    input_surface: str
    verdict:       str = 'JAMID_AALAM_OPEN'
    source:        str = 'jawamid_index'


# ── Jawamid taxonomy loader ───────────────────────────────────────────────────

_JAWAMID_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / 'data' / 'jawamid' / 'jawamid.xlsx'
)


@lru_cache(maxsize=1)
def _load_jawamid_taxonomy() -> dict:
    """
    Load Jawamid_Classification sheet from jawamid.xlsx.

    Returns {category_name: {requires_root_pattern: bool, examples: str}}

    Root requirement rules (هل يُطلب له جذر/وزن؟):
      'نعم' (yes) → True
      'لا' or 'غالبًا لا' or 'لا في التحليل النحوي الأولي' → False
      'بحسب المشروع' → False (project default: closed)
    """
    try:
        import openpyxl
        wb = openpyxl.load_workbook(str(_JAWAMID_FILE), read_only=True, data_only=True)
        ws = wb['Jawamid_Classification']
        taxonomy: dict = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row[0]:
                continue
            category = str(row[1]).strip() if row[1] else ''
            examples = str(row[3]).strip() if row[3] else ''
            req_root = str(row[5]).strip() if row[5] else ''
            # Closed unless explicitly 'نعم' with no 'لا'
            requires = ('نعم' in req_root) and ('لا' not in req_root)
            taxonomy[category] = {
                'requires_root_pattern': requires,
                'examples':              examples,
            }
        wb.close()
        return taxonomy
    except Exception:
        return {}


# ── Aalam seed catalog ────────────────────────────────────────────────────────
#
# Keys:   _strip_vowels_keep_shadda(segment_host)  — shadda-normalized form.
# Values: (lexical_identity, jamid_category, aalam_category)
#
# الله forms (critical — all 7 mandatory cases derive from these two keys):
#   'اللّه'  → matches اللَّهُ / اللَّهَ / اللَّهِ (bare: اللَّه, vowel stripped)
#   'لّه'    → matches لَّهِ (the segment_host of لِلَّهِ after لِ proclitic stripped)
#              لّه = ل + ّ + ه  (unique: only اسم الجلالة produces this after ل-ج)
#
# Prophet / place name stubs (included for taxonomy completeness, not exhaustive):
#   These stubs demonstrate the data-driven architecture.
#   Full aalam coverage will be added in a dedicated aalam-index expansion task.
#
_AALAM_CATALOG: dict[str, tuple[str, str, Optional[str]]] = {
    # ── اسم الجلالة (divine name) ─────────────────────────────────────────────
    # Key matches ALL three case vowels of اللَّهُ/اللَّهَ/اللَّهِ
    'اللّه':  ('الله', 'اسم علم', 'divine_name'),
    # Key matches لَّهِ — the host after لِ proclitic stripping in لِلَّهِ
    # لّه = ل (lam) + ّ (shadda) + ه (ha)  [Unicode: لّه]
    'لّه':    ('الله', 'اسم علم', 'divine_name'),

    # ── أسماء الأنبياء (prophet names — stubs) ───────────────────────────────
    'ابراهيم': ('إبراهيم', 'اسم علم', 'prophet_name'),
    'اسماعيل': ('إسماعيل', 'اسم علم', 'prophet_name'),
    'يعقوب':   ('يعقوب',   'اسم علم', 'prophet_name'),
    'محمد':    ('محمد',    'اسم علم', 'prophet_name'),
    'موسى':    ('موسى',    'اسم علم', 'prophet_name'),
    'عيسى':    ('عيسى',    'اسم علم', 'prophet_name'),

    # ── أسماء الأماكن (place names — stubs) ──────────────────────────────────
    'مكة':     ('مكة',     'اسم علم', 'place_name'),
    'مدينة':   ('مدينة',   'اسم علم', 'place_name'),
    'بغداد':   ('بغداد',   'اسم علم', 'place_name'),
}

# Secondary bare map: strip_all_diacritics(key) → key, for bare fallback
_AALAM_BARE_MAP: dict[str, str] = {
    _strip_all_diacritics(k): k
    for k in _AALAM_CATALOG
}


def _lookup_aalam(
    normalized_key: str,
) -> tuple[str, str, Optional[str]] | None:
    """
    Look up normalized_key in aalam catalog.

    Strategy:
      1. Primary: exact match on shadda-normalized key.
      2. Fallback: strip all diacritics (including shadda) and re-lookup.

    Returns (lexical_identity, jamid_category, aalam_category) or None.
    """
    # Primary: shadda-normalized (preserves lam+shadda distinction)
    hit = _AALAM_CATALOG.get(normalized_key)
    if hit is not None:
        return hit
    # Bare fallback: strip shadda too
    bare = _strip_all_diacritics(normalized_key)
    fallback_key = _AALAM_BARE_MAP.get(bare)
    if fallback_key is not None:
        return _AALAM_CATALOG[fallback_key]
    return None


# ── Main processing function ──────────────────────────────────────────────────

def process_jamid_aalam(
    segment_host: str,
) -> JamidAalamBoundary | JamidAalamOpen:
    """
    Classify segment_host as JAMID_AALAM_BOUNDARY or JAMID_AALAM_OPEN.

    Protocol:
      1. Normalize segment_host: strip vowel marks, keep shadda.
      2. Look up normalized key in aalam catalog.
      3. If found: return JamidAalamBoundary (root path closed).
      4. If not found: return JamidAalamOpen (root path proceeds).

    INVARIANTS:
      - IDEMPOTENT: calling twice with same input yields same result.
      - NO MUTATION: segment_host is never modified.
      - INPUT: MUST be segment_host (after clitic stripping), NEVER original_surface.
      - ROUTE: verdict is always 'JAMID_AALAM_BOUNDARY' or 'JAMID_AALAM_OPEN'.
        Never reuses MABNI_BOUNDARY, OPERATOR_BOUNDARY, or any existing route name.
    """
    if not segment_host:
        return JamidAalamOpen(input_surface=segment_host or '')

    # Step 1: Normalize — strip vowels, keep shadda
    normalized_key = _strip_vowels_keep_shadda(segment_host)

    # Step 2: Lookup
    hit = _lookup_aalam(normalized_key)
    if hit is None:
        return JamidAalamOpen(input_surface=segment_host)

    lexical_identity, jamid_category, aalam_category = hit

    # Step 3: Load taxonomy for requires_root_pattern
    taxonomy = _load_jawamid_taxonomy()
    cat_data  = taxonomy.get(jamid_category, {})
    requires_root = cat_data.get('requires_root_pattern', False)

    return JamidAalamBoundary(
        input_surface         = segment_host,
        matched_bare          = normalized_key,
        lexical_identity      = lexical_identity,
        jamid_category        = jamid_category,
        aalam_category        = aalam_category,
        requires_root_pattern = requires_root,
        verdict               = 'JAMID_AALAM_BOUNDARY',
        source                = 'jawamid_index',
        blocks_root_path      = True,
    )
