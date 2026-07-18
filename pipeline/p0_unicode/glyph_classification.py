#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p0_unicode/glyph_classification.py — P0 Glyph Classification Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Canonical location (R-1 refactoring).
The root-level glyph_classification.py is now a shim that re-exports from here.

Single source of truth for Arabic Unicode character typing.
Separates observation (GlyphTrace) from verdict (GlyphJudgment).

Public API:
  BaseGlyphClass            — what is the base character?
  MarkClass                 — what is the combining mark?
  MarkState                 — derived vowel/sukun state (not a codepoint)
  GlyphTrace                — immutable observation: one base glyph + its marks
  GlyphJudgment             — gate verdicts (always separate from observation)
  classify_base_glyph()     — BaseGlyphClass from one codepoint
  classify_combining_mark() — MarkClass from one combining mark codepoint
  build_glyph_traces()      — construct list[GlyphTrace] from a surface string
  p0_licensed()             — set of BaseGlyphClass values that pass P0

Governing distinction (always in force throughout Hokom):
  MarkClass.SUKUN   = علامة سكون مكتوبة صراحةً (U+0652)
  MarkState.ABSENT  = غياب أي علامة مكتوبة (بلا حركة، بلا سكون، بلا تنوين)
  These are DIFFERENT and must never be conflated in any gate or heuristic.

Phase A scope:
  - Defines classification types and lookup functions
  - Licenses ة (CONSONANT_TA_MARBUTA) at P0 — fixing the core bug
  - Does NOT perform the full normalize() pipeline; callers own that step
  - Span tracking: nfc_span is precise; original_span is best-effort
    (Phase B — P1_POSITION_CARRIER — will make original_span exact)
  - No commits, no behavior changes outside the ة licensing fix
"""

import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# BaseGlyphClass — the character (what is the base letter?)
# ══════════════════════════════════════════════════════════════════════════════

class BaseGlyphClass(str, Enum):
    """
    Classification of a single Arabic base codepoint.

    Describes the phonological and orthographic identity of the base character,
    independent of any combining marks written on it.
    """

    # ── Consonants ──────────────────────────────────────────────────────────

    CONSONANT_PLAIN = 'CONSONANT_PLAIN'
    """
    ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه
    The 25 canonical Arabic consonants (excluding ة, و, ي, and hamza forms).
    Always assigned role C at P1. Always pass P0.
    """

    CONSONANT_TA_MARBUTA = 'CONSONANT_TA_MARBUTA'
    """
    ة (U+0629 ARABIC LETTER TEH MARBUTA)
    Phonologically = ت in pausal position; structural role = C.
    Previously unlicensed at P0 — corrected in Phase A.
    Passes P0 after Phase A. P1 role = C (same as CONSONANT_PLAIN).
    Examples: اللَّيْلَةَ, ثَمَّةَ, رِسَالَةٌ
    """

    # ── Hamza forms ─────────────────────────────────────────────────────────

    HAMZA_ALONE = 'HAMZA_ALONE'
    """
    ء (U+0621 ARABIC LETTER HAMZA)
    Independent hamza with no seat letter.
    This is the canonical post-normalization form produced by normalize_hamza().
    All hamza composites (أ إ آ ؤ ئ) are reduced to this after normalize_hamza().
    Passes P0. P1 role = C.
    """

    HAMZA_ON_ALEF_ABOVE = 'HAMZA_ON_ALEF_ABOVE'
    """
    أ (U+0623 ARABIC LETTER ALEF WITH HAMZA ABOVE)
    Pre-normalization form. normalize_hamza() converts it to ء.
    If this reaches P0, normalization was skipped or failed.
    Does NOT pass P0 (normalize() must have been applied first).
    """

    HAMZA_ON_ALEF_BELOW = 'HAMZA_ON_ALEF_BELOW'
    """
    إ (U+0625 ARABIC LETTER ALEF WITH HAMZA BELOW)
    Pre-normalization form → ء after normalize_hamza().
    Does NOT pass P0.
    """

    HAMZA_ON_WAW = 'HAMZA_ON_WAW'
    """
    ؤ (U+0624 ARABIC LETTER WAW WITH HAMZA ABOVE)
    Pre-normalization form → ء after normalize_hamza().
    Does NOT pass P0.
    """

    HAMZA_ON_YA = 'HAMZA_ON_YA'
    """
    ئ (U+0626 ARABIC LETTER YEH WITH HAMZA ABOVE)
    Pre-normalization form → ء after normalize_hamza().
    Does NOT pass P0.
    """

    ALEF_MADDA = 'ALEF_MADDA'
    """
    آ (U+0622 ARABIC LETTER ALEF WITH MADDA ABOVE)
    Pre-normalization form. normalize_hamza() expands it to ءَا.
    Does NOT pass P0 (should not appear in normalized pipeline input).
    """

    # ── Long-vowel and semi-vowel letters ────────────────────────────────────

    LONG_VOWEL_ALEF = 'LONG_VOWEL_ALEF'
    """
    ا (U+0627 ARABIC LETTER ALEF)
    Always VL (vowel letter / مد nucleus extension).
    Passes P0. P1 role = VL.
    """

    ALIF_MAQSURA = 'ALIF_MAQSURA'
    """
    ى (U+0649 ARABIC LETTER ALEF MAKSURA)
    Word-final long-a vowel letter.
    Passes P0. P1 role = VL.
    """

    SEMI_VOWEL_WAW = 'SEMI_VOWEL_WAW'
    """
    و (U+0648 ARABIC LETTER WAW)
    Conditionally C (when bearing a short vowel) or VL (when bare).
    Passes P0. P1 role determined by presence/absence of haraka.
    """

    SEMI_VOWEL_YA = 'SEMI_VOWEL_YA'
    """
    ي (U+064A ARABIC LETTER YEH)
    Conditionally C (when bearing a short vowel) or VL (when bare).
    Passes P0. P1 role determined by presence/absence of haraka.
    """

    # ── Decoration / tatweel ─────────────────────────────────────────────────

    TATWEEL = 'TATWEEL'
    """
    ـ (U+0640 ARABIC TATWEEL / kashida)
    Purely decorative elongation; no phonological role.
    Should be stripped before phonological analysis.
    Does NOT pass P0 as a phonological unit.
    """

    # ── Error sentinel ────────────────────────────────────────────────────────

    UNKNOWN = 'UNKNOWN'
    """
    Any codepoint not in the Arabic classification map.
    An UNKNOWN base glyph is an error signal — it is never silently absorbed.
    Does NOT pass P0.
    """


# ══════════════════════════════════════════════════════════════════════════════
# MarkClass — the combining marks (what is written on the character?)
# ══════════════════════════════════════════════════════════════════════════════

class MarkClass(str, Enum):
    """
    Classification of a single Arabic combining mark codepoint.

    Marks are attached to a preceding base character; they never stand alone.
    This classification is separate from BaseGlyphClass.
    """

    FATHA          = 'FATHA'            # َ  U+064E  فتحة — short /a/
    DAMMA          = 'DAMMA'            # ُ  U+064F  ضمة  — short /u/
    KASRA          = 'KASRA'            # ِ  U+0650  كسرة — short /i/

    FATHATAN       = 'FATHATAN'         # ً  U+064B  تنوين فتح
    DAMMATAN       = 'DAMMATAN'         # ٌ  U+064C  تنوين ضم
    KASRATAN       = 'KASRATAN'         # ٍ  U+064D  تنوين كسر

    SUKUN          = 'SUKUN'
    """
    ْ  U+0652  سكون صريح مكتوب
    CRITICAL: this is NOT the same as an absent haraka.
    MarkClass.SUKUN = علامة مكتوبة  |  MarkState.ABSENT = غياب العلامة
    Never conflate these two.
    """

    SHADDA         = 'SHADDA'           # ّ  U+0651  شدة — gemination mark
    SUPERSCRIPT_ALEF = 'SUPERSCRIPT_ALEF'  # ٰ  U+0670  ألف خنجرية
    HAMZA_ABOVE    = 'HAMZA_ABOVE'      # ٔ  U+0654  همزة فوق (combining)
    HAMZA_BELOW    = 'HAMZA_BELOW'      # ٕ  U+0655  همزة تحت (combining)
    MADDA_ABOVE    = 'MADDA_ABOVE'      # ٓ  U+0653  مدة فوق (combining)

    UNKNOWN        = 'UNKNOWN'
    """Any combining mark not in the classification map — error signal."""


# ══════════════════════════════════════════════════════════════════════════════
# MarkState — derived vowel/sukun state (not a codepoint, a derivation)
# ══════════════════════════════════════════════════════════════════════════════

class MarkState(str, Enum):
    """
    Derived observation of the vowel/sukun state at a glyph position.

    Computed from the set of MarkClass values present on the glyph.
    This is NOT a codepoint classification — it is a derived property.

    The critical distinction that must be preserved throughout Hokom:

      EXPLICIT_SUKUN  ← sUKUN mark (U+0652) is WRITTEN
      ABSENT          ← no mark of any kind is written

    These must never be conflated. A word without tashkeel has ABSENT glyphs,
    not EXPLICIT_SUKUN glyphs, even though both are phonologically sakin.
    The distinction matters for compatibility checking and catalog matching.
    """

    EXPLICIT_VOWEL = 'EXPLICIT_VOWEL'
    """حرف متحرك: فتحة أو ضمة أو كسرة مكتوبة (with or without shadda)."""

    EXPLICIT_SUKUN = 'EXPLICIT_SUKUN'
    """
    حرف ساكن صريح: علامة سكون مكتوبة (U+0652).
    Distinct from ABSENT: the sukun mark is present in the text.
    """

    TANWIN = 'TANWIN'
    """تنوين: فتحتان أو ضمتان أو كسرتان (تنوين الفتح/الضم/الكسر)."""

    ABSENT = 'ABSENT'
    """
    لا علامة مكتوبة من أي نوع.
    Inferred from the absence of all other marks.
    → Do NOT confuse with EXPLICIT_SUKUN.
    In unvoweled text, almost every glyph has MarkState.ABSENT.
    """

    SHADDA_COMPOUND = 'SHADDA_COMPOUND'
    """
    شدة فقط — الحرف مضعَّف لكن الحركة غير مكتوبة.
    The vowel on the second copy is absent or determined by context.
    Distinct from EXPLICIT_VOWEL (which requires a written haraka alongside the shadda).
    """

    CONFLICTING = 'CONFLICTING'
    """
    علامات متضاربة في المدخل.
    Examples: fatha + kasra on same letter, shadda + sukun, two vowels.
    Signals malformed or corrupt input — never silently absorbed.
    """


# ══════════════════════════════════════════════════════════════════════════════
# Lookup tables
# ══════════════════════════════════════════════════════════════════════════════

_BASE_GLYPH_MAP: dict[str, BaseGlyphClass] = {
    # ── Hamza forms ───────────────────────────────────────────────────────
    'ء': BaseGlyphClass.HAMZA_ALONE,           # U+0621
    'آ': BaseGlyphClass.ALEF_MADDA,            # U+0622
    'أ': BaseGlyphClass.HAMZA_ON_ALEF_ABOVE,   # U+0623
    'ؤ': BaseGlyphClass.HAMZA_ON_WAW,          # U+0624
    'إ': BaseGlyphClass.HAMZA_ON_ALEF_BELOW,   # U+0625
    'ئ': BaseGlyphClass.HAMZA_ON_YA,           # U+0626
    # ── Long-vowel alef ───────────────────────────────────────────────────
    'ا': BaseGlyphClass.LONG_VOWEL_ALEF,       # U+0627
    # ── Plain consonants (U+0628–U+063A) ─────────────────────────────────
    'ب': BaseGlyphClass.CONSONANT_PLAIN,       # U+0628
    'ة': BaseGlyphClass.CONSONANT_TA_MARBUTA,  # U+0629  ← the Phase A fix
    'ت': BaseGlyphClass.CONSONANT_PLAIN,       # U+062A
    'ث': BaseGlyphClass.CONSONANT_PLAIN,       # U+062B
    'ج': BaseGlyphClass.CONSONANT_PLAIN,       # U+062C
    'ح': BaseGlyphClass.CONSONANT_PLAIN,       # U+062D
    'خ': BaseGlyphClass.CONSONANT_PLAIN,       # U+062E
    'د': BaseGlyphClass.CONSONANT_PLAIN,       # U+062F
    'ذ': BaseGlyphClass.CONSONANT_PLAIN,       # U+0630
    'ر': BaseGlyphClass.CONSONANT_PLAIN,       # U+0631
    'ز': BaseGlyphClass.CONSONANT_PLAIN,       # U+0632
    'س': BaseGlyphClass.CONSONANT_PLAIN,       # U+0633
    'ش': BaseGlyphClass.CONSONANT_PLAIN,       # U+0634
    'ص': BaseGlyphClass.CONSONANT_PLAIN,       # U+0635
    'ض': BaseGlyphClass.CONSONANT_PLAIN,       # U+0636
    'ط': BaseGlyphClass.CONSONANT_PLAIN,       # U+0637
    'ظ': BaseGlyphClass.CONSONANT_PLAIN,       # U+0638
    'ع': BaseGlyphClass.CONSONANT_PLAIN,       # U+0639
    'غ': BaseGlyphClass.CONSONANT_PLAIN,       # U+063A
    # ── Tatweel ───────────────────────────────────────────────────────────
    'ـ': BaseGlyphClass.TATWEEL,               # U+0640
    # ── Plain consonants (U+0641–U+0647) ─────────────────────────────────
    'ف': BaseGlyphClass.CONSONANT_PLAIN,       # U+0641
    'ق': BaseGlyphClass.CONSONANT_PLAIN,       # U+0642
    'ك': BaseGlyphClass.CONSONANT_PLAIN,       # U+0643
    'ل': BaseGlyphClass.CONSONANT_PLAIN,       # U+0644
    'م': BaseGlyphClass.CONSONANT_PLAIN,       # U+0645
    'ن': BaseGlyphClass.CONSONANT_PLAIN,       # U+0646
    'ه': BaseGlyphClass.CONSONANT_PLAIN,       # U+0647
    # ── Semi-vowel and vowel-letters (U+0648–U+064A) ─────────────────────
    'و': BaseGlyphClass.SEMI_VOWEL_WAW,        # U+0648
    'ى': BaseGlyphClass.ALIF_MAQSURA,          # U+0649
    'ي': BaseGlyphClass.SEMI_VOWEL_YA,         # U+064A
}

_MARK_CLASS_MAP: dict[str, MarkClass] = {
    'ً': MarkClass.FATHATAN,           # U+064B
    'ٌ': MarkClass.DAMMATAN,           # U+064C
    'ٍ': MarkClass.KASRATAN,           # U+064D
    'َ': MarkClass.FATHA,              # U+064E
    'ُ': MarkClass.DAMMA,              # U+064F
    'ِ': MarkClass.KASRA,              # U+0650
    'ّ': MarkClass.SHADDA,             # U+0651
    'ْ': MarkClass.SUKUN,              # U+0652  ← علامة مكتوبة صراحةً
    'ٓ': MarkClass.MADDA_ABOVE,        # U+0653  — preserved, not stripped in Phase A
    'ٔ': MarkClass.HAMZA_ABOVE,        # U+0654  — preserved, not stripped in Phase A
    'ٕ': MarkClass.HAMZA_BELOW,        # U+0655  — preserved, not stripped in Phase A
    'ٰ': MarkClass.SUPERSCRIPT_ALEF,   # U+0670
}

# Short vowels that determine EXPLICIT_VOWEL
_SHORT_VOWEL_MARKS = frozenset({MarkClass.FATHA, MarkClass.DAMMA, MarkClass.KASRA})
# Tanwin marks
_TANWIN_MARKS      = frozenset({MarkClass.FATHATAN, MarkClass.DAMMATAN, MarkClass.KASRATAN})

# P0-licensed BaseGlyphClass values (post-normalize() canonical forms)
# HAMZA_ON_* and ALEF_MADDA are NOT here: if they reach P0, normalize() was skipped.
# TATWEEL and UNKNOWN are never licensed as phonological units.
_P0_LICENSED: frozenset[BaseGlyphClass] = frozenset({
    BaseGlyphClass.CONSONANT_PLAIN,
    BaseGlyphClass.CONSONANT_TA_MARBUTA,   # ← Phase A: ة licensed
    BaseGlyphClass.HAMZA_ALONE,            # ء (post-normalization)
    BaseGlyphClass.LONG_VOWEL_ALEF,        # ا
    BaseGlyphClass.ALIF_MAQSURA,           # ى
    BaseGlyphClass.SEMI_VOWEL_WAW,         # و
    BaseGlyphClass.SEMI_VOWEL_YA,          # ي
})


# ══════════════════════════════════════════════════════════════════════════════
# Classification functions
# ══════════════════════════════════════════════════════════════════════════════

def classify_base_glyph(codepoint: str) -> BaseGlyphClass:
    """
    Classify a single Arabic base character codepoint.

    Args:
        codepoint: a single-character string

    Returns:
        BaseGlyphClass value; UNKNOWN if not in the Arabic classification map.

    Note: does NOT call normalize(). The caller is responsible for hamza
    normalization if needed. If أ / إ / آ / ؤ / ئ are passed pre-normalization,
    they return HAMZA_ON_* / ALEF_MADDA (correct but will fail P0).
    """
    return _BASE_GLYPH_MAP.get(codepoint, BaseGlyphClass.UNKNOWN)


def classify_combining_mark(codepoint: str) -> MarkClass:
    """
    Classify a single Arabic combining mark codepoint.

    Args:
        codepoint: a single combining mark character

    Returns:
        MarkClass value; UNKNOWN if not in the mark classification map.

    Decision on U+0653/0654/0655 (مدة / همزة فوق / همزة تحت):
        These are preserved in GlyphTrace as MADDA_ABOVE / HAMZA_ABOVE / HAMZA_BELOW.
        They are NOT stripped at this stage (per Phase A decision).
        The normalizer handles their phonological effect separately.
    """
    return _MARK_CLASS_MAP.get(codepoint, MarkClass.UNKNOWN)


def p0_licensed() -> frozenset[BaseGlyphClass]:
    """
    Return the set of BaseGlyphClass values that pass P0 (Unicode Candidate gate).

    This is the single source of truth for P0 licensing.
    licensing.py delegates to this function.
    """
    return _P0_LICENSED


# ══════════════════════════════════════════════════════════════════════════════
# MarkState derivation
# ══════════════════════════════════════════════════════════════════════════════

def _derive_mark_state(mark_classes: tuple[MarkClass, ...]) -> MarkState:
    """
    Derive the MarkState from a tuple of MarkClass values.

    Critical invariant: MarkClass.SUKUN → MarkState.EXPLICIT_SUKUN (never ABSENT).
    ABSENT is reserved for the complete absence of any written mark.
    """
    mc_set = set(mark_classes)

    has_vowel  = bool(mc_set & _SHORT_VOWEL_MARKS)
    has_tanwin = bool(mc_set & _TANWIN_MARKS)
    has_sukun  = MarkClass.SUKUN  in mc_set
    has_shadda = MarkClass.SHADDA in mc_set

    # ── Conflict detection ────────────────────────────────────────────────
    vowel_count = sum(1 for m in mc_set if m in _SHORT_VOWEL_MARKS)
    if vowel_count > 1:
        return MarkState.CONFLICTING                  # two different short vowels
    if has_vowel and has_sukun:
        return MarkState.CONFLICTING                  # vowel + sukun (malformed)
    if has_tanwin and has_sukun:
        return MarkState.CONFLICTING                  # tanwin + sukun (malformed)
    if has_vowel and has_tanwin:
        return MarkState.CONFLICTING                  # vowel + tanwin (malformed)
    if has_shadda and has_sukun and not has_vowel:
        return MarkState.CONFLICTING                  # shadda + sukun (malformed)

    # ── Normal classification (in priority order) ─────────────────────────
    if has_tanwin:
        return MarkState.TANWIN
    if has_vowel:
        return MarkState.EXPLICIT_VOWEL               # fatha/damma/kasra present
    if has_sukun:
        return MarkState.EXPLICIT_SUKUN               # ← WRITTEN sukun, NOT absent haraka
    if has_shadda and not has_vowel:
        return MarkState.SHADDA_COMPOUND              # shadda with no haraka
    return MarkState.ABSENT                           # no mark of any kind written


# ══════════════════════════════════════════════════════════════════════════════
# GlyphTrace — immutable observation of one base glyph + its marks
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class GlyphTrace:
    """
    Immutable observation of a single base glyph and its attached combining marks.

    Records both the raw input form and the NFC-normalized form.
    Separation principle: describes what was seen, not what the gates decided.
    Gate verdicts live in GlyphJudgment, not here.

    Span tracking (Phase A):
        nfc_span is precise.
        original_span is best-effort: exact when NFC does not change codepoint count,
        approximate otherwise. Phase B (P1_POSITION_CARRIER) will make it exact.
    """

    # ── Raw input identity ────────────────────────────────────────────────
    raw_base:    str              # exact base codepoint as arrived (before NFC)
    raw_marks:   tuple[str, ...]  # combining marks in arrival order (before NFC)

    # ── After NFC ─────────────────────────────────────────────────────────
    nfc_base:    str              # base after unicodedata.normalize('NFC', ...)
    nfc_marks:   tuple[str, ...]  # marks in NFC canonical order

    # ── Classification ─────────────────────────────────────────────────────
    base_class:    BaseGlyphClass           # classified from nfc_base
    mark_classes:  tuple[MarkClass, ...]    # classified from nfc_marks (same length as nfc_marks)
    mark_state:    MarkState                # derived from mark_classes

    # ── Shadda expansion (None if no shadda present) ──────────────────────
    shadda_sakin_copy:    Optional[str]
    """
    The sakin (sukun) copy produced by shadda gemination: base + ْ.
    Example: مِّ → shadda_sakin_copy = 'مْ' (first copy, always sakin).
    None if no SHADDA in mark_classes.
    """
    shadda_voweled_copy:  Optional[str]
    """
    The voweled copy produced by shadda gemination: base + vowel (if any).
    Example: مِّ → shadda_voweled_copy = 'مِ'; مّ → 'م' (bare, no vowel written).
    None if no SHADDA in mark_classes.
    """

    # ── Position ──────────────────────────────────────────────────────────
    position_in_token: int   # 0-indexed position among all base glyphs in this token
    is_final_position: bool  # True if this is the rightmost non-TATWEEL base glyph

    # ── Span alignment ────────────────────────────────────────────────────
    original_span: tuple[int, int]          # (start, end) in raw input string (best-effort)
    nfc_span:      tuple[int, int]          # (start, end) in NFC-normalized string (exact)

    # ── Convenience properties ────────────────────────────────────────────

    @property
    def has_fatha(self) -> bool:
        return MarkClass.FATHA in self.mark_classes

    @property
    def has_damma(self) -> bool:
        return MarkClass.DAMMA in self.mark_classes

    @property
    def has_kasra(self) -> bool:
        return MarkClass.KASRA in self.mark_classes

    @property
    def has_short_vowel(self) -> bool:
        return bool(set(self.mark_classes) & _SHORT_VOWEL_MARKS)

    @property
    def has_tanwin(self) -> bool:
        return bool(set(self.mark_classes) & _TANWIN_MARKS)

    @property
    def has_sukun(self) -> bool:
        """True iff a sukun mark (U+0652) is WRITTEN. Not the same as ABSENT haraka."""
        return MarkClass.SUKUN in self.mark_classes

    @property
    def has_shadda(self) -> bool:
        return MarkClass.SHADDA in self.mark_classes

    @property
    def has_superscript_alef(self) -> bool:
        return MarkClass.SUPERSCRIPT_ALEF in self.mark_classes

    @property
    def unlicensed_marks(self) -> tuple[MarkClass, ...]:
        """Marks classified as UNKNOWN (not in the mark classification map)."""
        return tuple(m for m in self.mark_classes if m == MarkClass.UNKNOWN)

    @property
    def absent_haraka(self) -> bool:
        """
        True iff no haraka, sukun, or tanwin is written.
        This is MarkState.ABSENT — DIFFERENT from EXPLICIT_SUKUN.
        """
        return self.mark_state == MarkState.ABSENT

    def p0_passes(self) -> bool:
        """True iff this glyph passes the P0 Unicode Candidate gate."""
        return self.base_class in _P0_LICENSED


# ══════════════════════════════════════════════════════════════════════════════
# GlyphJudgment — gate verdicts (always separate from GlyphTrace observation)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class GlyphJudgment:
    """
    Gate verdicts for one glyph position.

    Separation principle: GlyphTrace records what was seen;
    GlyphJudgment records what the gates decided.
    They are never merged into a single object.

    Verdict fields are None until the corresponding gate has run.
    """

    position_in_token: int   # matches GlyphTrace.position_in_token
    nfc_base:          str   # matches GlyphTrace.nfc_base (for cross-referencing)

    # P0 — Unicode Candidate
    p0_verdict: str          # 'PASS' | 'BLOCK'
    p0_reason:  str          # human-readable explanation

    # P1 — Character Licensing (C / VL)
    p1_verdict: Optional[str]   # 'C' | 'VL' | 'BLOCK' | None (before P1 runs)
    p1_reason:  Optional[str]

    # P2 — Diacritic Licensing
    p2_verdict: Optional[str]   # 'LICENSED' | 'BLOCK' | None
    p2_reason:  Optional[str]

    # P3 — Cell Construction
    p3_cell:    Optional[str]   # 'C' | 'CV' | 'V' | 'VV' | 'BLOCK' | None

    @classmethod
    def from_trace(cls, t: 'GlyphTrace') -> 'GlyphJudgment':
        """
        Construct a P0-only judgment from a GlyphTrace.
        P1/P2/P3 fields are left None (to be filled by licensing.py gates).
        """
        if t.base_class in _P0_LICENSED:
            verdict, reason = 'PASS', f'[{t.nfc_base}] ∈ P0_LICENSED ({t.base_class.value})'
        else:
            verdict = 'BLOCK'
            reason  = f'[{t.nfc_base!r}] ∉ P0_LICENSED ({t.base_class.value})'
        return cls(
            position_in_token = t.position_in_token,
            nfc_base          = t.nfc_base,
            p0_verdict        = verdict,
            p0_reason         = reason,
            p1_verdict        = None,
            p1_reason         = None,
            p2_verdict        = None,
            p2_reason         = None,
            p3_cell           = None,
        )


# ══════════════════════════════════════════════════════════════════════════════
# String walking helper
# ══════════════════════════════════════════════════════════════════════════════

def _walk_string(s: str) -> list[tuple[str, list[str], int, int]]:
    """
    Walk a Unicode string and collect (base_char, [marks], start_idx, end_idx) tuples.

    A "base char" is any character whose unicodedata.category does NOT start with 'M'
    (i.e., not a combining mark). Following combining marks (category 'M*') are
    attached to the preceding base character.

    Returns list of (base, marks_list, span_start, span_end) where:
        span_start = index of base in s
        span_end   = index after last mark (= start of next base)
    """
    result: list[tuple[str, list[str], int, int]] = []
    i = 0
    n = len(s)
    while i < n:
        ch    = s[i]
        start = i
        i    += 1
        marks: list[str] = []
        while i < n and unicodedata.category(s[i]).startswith('M'):
            marks.append(s[i])
            i += 1
        result.append((ch, marks, start, i))
    return result


# ══════════════════════════════════════════════════════════════════════════════
# build_glyph_traces() — main constructor
# ══════════════════════════════════════════════════════════════════════════════

def build_glyph_traces(s: str, alignment=None) -> list[GlyphTrace]:
    """
    Construct a list of GlyphTrace objects from a surface string.

    Processing:
        1. Apply unicodedata.normalize('NFC', s) internally.
        2. Walk the NFC string collecting (base, marks) pairs.
        3. Walk the raw string in parallel for original_span (best-effort).
        4. Classify each pair into BaseGlyphClass + MarkClass tuple + MarkState.
        5. Compute shadda expansion pairs where SHADDA is present.
        6. Set is_final_position=True on the rightmost non-TATWEEL glyph.

    Args:
        s: surface string as received (typically normalize()-output from the caller)
        alignment: optional SpanAlignmentMap (from normalize_tracked) that maps
            positions in the raw pre-normalize() surface to positions in `s`.
            When provided, GlyphTrace.original_span is populated with precise
            raw-surface coordinates rather than best-effort NFC coordinates.
            This is the Phase B (P1_POSITION_CARRIER) upgrade path.

    Returns:
        list[GlyphTrace], one per base character in the NFC-normalized form.
        An empty string returns [].

    Span tracking:
        nfc_span      — precise: position within NFC(s) (= NFC of normalize()-output)
        original_span — Phase A: best-effort (= nfc_span when NFC does not change count)
                        Phase B: exact raw-surface span when alignment is provided

    Callers are responsible for any higher-level normalization
    (normalize_hamza, normalize_al, normalize_shadda) before calling this
    function. normalize_tracked() in normalizer.py returns both the normalized
    string and the alignment map in one call.
    """
    if not s:
        return []

    nfc_s = unicodedata.normalize('NFC', s)

    nfc_units = _walk_string(nfc_s)
    raw_units = _walk_string(s)

    # Span pairing: 1:1 when lengths match; fallback to nfc positions otherwise
    same_length = (len(nfc_units) == len(raw_units))

    # Pre-scan: find the last base-glyph index that isn't TATWEEL
    last_non_tatweel = -1
    for idx, (nfc_base, _, _, _) in enumerate(nfc_units):
        if classify_base_glyph(nfc_base) != BaseGlyphClass.TATWEEL:
            last_non_tatweel = idx

    traces: list[GlyphTrace] = []
    position = 0  # counts all base glyphs including TATWEEL

    for idx, (nfc_base, nfc_marks_list, nfc_start, nfc_end) in enumerate(nfc_units):
        # Raw counterpart (positions within `s`, not the true pre-normalize raw)
        if same_length:
            raw_base, raw_marks_list, raw_start, raw_end = raw_units[idx]
        else:
            # NFC changed codepoint count — use NFC spans as fallback
            raw_base, raw_marks_list, raw_start, raw_end = (
                nfc_base, nfc_marks_list, nfc_start, nfc_end
            )

        b_class   = classify_base_glyph(nfc_base)
        m_tuples  = tuple(nfc_marks_list)
        m_classes = tuple(classify_combining_mark(m) for m in m_tuples)
        m_state   = _derive_mark_state(m_classes)

        # Shadda expansion
        shadda_sakin:   Optional[str] = None
        shadda_voweled: Optional[str] = None
        if MarkClass.SHADDA in m_classes:
            vowel_chars = ''.join(
                raw_m for raw_m, mc in zip(nfc_marks_list, m_classes)
                if mc in (_SHORT_VOWEL_MARKS | _TANWIN_MARKS)
            )
            shadda_sakin   = nfc_base + 'ْ'
            shadda_voweled = nfc_base + vowel_chars

        # Phase B: use alignment map to compute original_span precisely.
        # Phase A fallback: use raw_start/raw_end (positions within `s`).
        # Note: nfc_span is in NFC(s) coordinates. For Arabic text, NFC
        # of normalize()-output is typically codepoint-count-preserving,
        # so nfc_span ≈ span in `s`. The alignment map maps positions in `s`
        # to the true raw surface, so project_to_raw(nfc_start, nfc_end)
        # gives precise raw coordinates.
        if alignment is not None:
            orig_start, orig_end = alignment.project_to_raw(nfc_start, nfc_end)
        else:
            orig_start, orig_end = raw_start, raw_end

        traces.append(GlyphTrace(
            raw_base             = raw_base,
            raw_marks            = tuple(raw_marks_list),
            nfc_base             = nfc_base,
            nfc_marks            = m_tuples,
            base_class           = b_class,
            mark_classes         = m_classes,
            mark_state           = m_state,
            shadda_sakin_copy    = shadda_sakin,
            shadda_voweled_copy  = shadda_voweled,
            position_in_token    = position,
            is_final_position    = (idx == last_non_tatweel),
            original_span        = (orig_start, orig_end),
            nfc_span             = (nfc_start, nfc_end),
        ))
        position += 1

    return traces


# ══════════════════════════════════════════════════════════════════════════════
# Convenience accessors
# ══════════════════════════════════════════════════════════════════════════════

def last_base_glyph(traces: list[GlyphTrace]) -> Optional[GlyphTrace]:
    """
    Return the last non-TATWEEL GlyphTrace in a trace list, or None if empty.
    Replacement for mabniyat_attachment._last_base_char() (deprecated).
    """
    for t in reversed(traces):
        if t.base_class != BaseGlyphClass.TATWEEL:
            return t
    return None


def is_mudaric_form(traces: list[GlyphTrace]) -> bool:
    """
    True if the trace sequence looks like a mudāri' (imperfect) verb form.

    Detection via GlyphTrace (replaces mabniyat_attachment._is_mudaric_form):
      - First base glyph has nfc_base in {ي, ت}
      - First glyph has MarkState.EXPLICIT_VOWEL (fatha written)
      - Second base glyph exists and has MarkState.EXPLICIT_SUKUN

    This is a NARROW MORPHOLOGICAL LICENSER valid for the current licensed
    inventory. It will not correctly classify augmented verb forms (Forms IV–X).
    See G1 CLOSED note in TODO_mabniyat.md.
    """
    base_glyphs = [t for t in traces if t.base_class != BaseGlyphClass.TATWEEL]
    if len(base_glyphs) < 4:
        return False
    g0 = base_glyphs[0]
    g1 = base_glyphs[1]
    return (
        g0.nfc_base in ('ي', 'ت')
        and g0.mark_state == MarkState.EXPLICIT_VOWEL
        and g0.has_fatha
        and g1.mark_state == MarkState.EXPLICIT_SUKUN
    )


def is_verbal_dual_host(traces: list[GlyphTrace]) -> bool:
    """
    True if the trace sequence looks like a māḍī (past-tense) verbal host
    eligible for ALIF_AL_ITHNAYN attachment.

    Detection via GlyphTrace (replaces mabniyat_attachment._is_verbal_dual_host):
      - First base glyph is NOT a definite-article prefix:
        not (HAMZA_ALONE with fatha, followed immediately by ل)
      - First base glyph nfc_base ≠ ي
      - First base glyph has fatha (EXPLICIT_VOWEL)

    This is a TEMPORARY HOST LICENSING HEURISTIC. See G3 CLOSED note.
    """
    base_glyphs = [t for t in traces if t.base_class != BaseGlyphClass.TATWEEL]
    if len(base_glyphs) < 3:
        return False
    g0 = base_glyphs[0]

    # Block definite-article-initial forms: ءَلْ...
    if (g0.base_class == BaseGlyphClass.HAMZA_ALONE
            and g0.has_fatha
            and len(base_glyphs) > 1
            and base_glyphs[1].nfc_base == 'ل'):
        return False

    return (
        g0.nfc_base != 'ي'
        and g0.mark_state == MarkState.EXPLICIT_VOWEL
        and g0.has_fatha
    )


# ══════════════════════════════════════════════════════════════════════════════
# Module self-test
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    samples = [
        ('ة',   BaseGlyphClass.CONSONANT_TA_MARBUTA, 'Phase A fix: ة must be CONSONANT_TA_MARBUTA'),
        ('ت',   BaseGlyphClass.CONSONANT_PLAIN,       'ت stays CONSONANT_PLAIN'),
        ('ء',   BaseGlyphClass.HAMZA_ALONE,            'ء post-normalization hamza'),
        ('أ',   BaseGlyphClass.HAMZA_ON_ALEF_ABOVE,    'أ pre-normalization hamza'),
        ('ا',   BaseGlyphClass.LONG_VOWEL_ALEF,        'ا always VL'),
        ('ى',   BaseGlyphClass.ALIF_MAQSURA,           'ى alif maqsura'),
        ('و',   BaseGlyphClass.SEMI_VOWEL_WAW,         'و semi-vowel'),
        ('ي',   BaseGlyphClass.SEMI_VOWEL_YA,          'ي semi-vowel'),
        ('ـ',   BaseGlyphClass.TATWEEL,                'ـ tatweel'),
        ('X',   BaseGlyphClass.UNKNOWN,                'X unknown → error sentinel'),
    ]
    print('\n  BaseGlyphClass self-test:')
    all_ok = True
    for ch, expected, note in samples:
        got = classify_base_glyph(ch)
        ok  = got == expected
        icon = '✓' if ok else '✗'
        print(f'    {icon} {ch!r:4} → {got.value:30}  ({note})')
        if not ok:
            all_ok = False
            print(f'         expected: {expected.value}')

    print('\n  MarkState self-test (SUKUN vs ABSENT):')
    sukun_trace  = build_glyph_traces('مْ')[0]
    absent_trace = build_glyph_traces('م')[0]
    print(f'    مْ  mark_state = {sukun_trace.mark_state.value}   (has written sukun)')
    print(f'    م   mark_state = {absent_trace.mark_state.value}              (no mark written)')
    assert sukun_trace.mark_state  == MarkState.EXPLICIT_SUKUN, 'FAIL: مْ should be EXPLICIT_SUKUN'
    assert absent_trace.mark_state == MarkState.ABSENT,         'FAIL: م  should be ABSENT'
    print('    ✓ SUKUN vs ABSENT correctly distinguished')

    print('\n  ة P0 licensing:')
    ta_m_trace = build_glyph_traces('ة')[0]
    print(f'    ة → base_class={ta_m_trace.base_class.value}, p0_passes={ta_m_trace.p0_passes()}')
    assert ta_m_trace.p0_passes(), 'FAIL: ة should pass P0 after Phase A'
    print('    ✓ ة passes P0')

    print('\n  Shadda expansion:')
    shadda_traces = build_glyph_traces('مِّ')
    for t in shadda_traces:
        if t.has_shadda:
            print(f'    {t.nfc_base + "".join(t.nfc_marks)!r} → sakin={t.shadda_sakin_copy!r}  voweled={t.shadda_voweled_copy!r}')
    assert shadda_traces[0].shadda_sakin_copy   == 'مْ', 'FAIL: shadda_sakin_copy'
    assert shadda_traces[0].shadda_voweled_copy == 'مِ', 'FAIL: shadda_voweled_copy'
    print('    ✓ Shadda expansion correct')

    print(f'\n  {"All tests passed" if all_ok else "FAILURES DETECTED"}')
