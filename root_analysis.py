#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
root_analysis.py — Arabic Triliteral Root Analysis
════════════════════════════════════════════════════════════════════════════
PR 3.4  Hollow (أجوف) root identification — AYN weak
PR 3.5  Defective (ناقص) final-radical restoration — LAM weak
        + Assimilated FA-yaiyya standalone fix (يَئِسَ pattern)

Governing constraints (always in force):
  ● No word-specific exceptions, no seeds, no word lists
  ● No bab, no paradigm, no masdar
  ● Every restoration carries an EvidenceAssessment
  ● Traces and residuals always preserved
  ● Lafif (multiple weak positions) is detected but not resolved here — DEFER to PR 3.6
  ● Functional surfaces that match a root pattern receive DEFER (not ACCEPT)
    because the Internal Boundary Layer (PR 3.6.5) is not yet implemented
  ● Visible ا/ى in final position are never declared root identities:
      دَعَا → LAM = UnknownRadical{و،ي}    (ا is a surface realisation, not the LAM)
      رَمَى → LAM = UnknownRadical{و،ي}    (ى is a surface realisation, not the LAM)
  ● JSON-serialisable output
  ● Independent of mabni layer, mabniyat_attachment, licensing, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# Local imports — syllabifier, normalizer, and boundary gate (PR 3.7-A)
from syllabifier import parse_phones, Phone, FATHA, KASRA, DAMMA, SUKUN
from normalizer import normalize_hamza
from boundary import assess_boundary
from boundary.models import BoundaryKind, RootPathDirective


# ══════════════════════════════════════════════════════════════════════════════
# §1  Enumerations
# ══════════════════════════════════════════════════════════════════════════════

class WeaknessType(str, Enum):
    SOUND      = 'SOUND'       # صحيح — all three radicals are true consonants
    ASSIMILATED = 'ASSIMILATED' # مثال — FA is و or ي
    HOLLOW     = 'HOLLOW'      # أجوف — AYN is weak (و or ي)
    DEFECTIVE  = 'DEFECTIVE'   # ناقص — LAM is weak (و or ي)
    DOUBLED    = 'DOUBLED'     # مضعف — AYN == LAM (same consonant)
    LAFIF      = 'LAFIF'       # لفيف — two or more weak positions (DEFER to PR 3.6)


class WeakPosition(str, Enum):
    FA  = 'FA'   # فاء الكلمة
    AYN = 'AYN'  # عين الكلمة
    LAM = 'LAM'  # لام الكلمة


class EvidenceSufficiency(str, Enum):
    SUFFICIENT   = 'SUFFICIENT'   # this evidence alone closes the radical identity
    CONTRIBUTORY = 'CONTRIBUTORY' # helps but requires additional support
    INSUFFICIENT = 'INSUFFICIENT' # inadmissible or unable to distinguish candidates


# ══════════════════════════════════════════════════════════════════════════════
# §2  Core data types
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class UnknownRadical:
    """
    A root position whose identity cannot yet be determined.

    candidates  — frozenset of candidate characters, e.g. frozenset({'و', 'ي'})
    position    — which root position this unknown occupies
    """
    candidates: frozenset
    position:   WeakPosition

    def __str__(self) -> str:
        return f'?{{{",".join(sorted(self.candidates))}}}'

    def to_dict(self) -> dict:
        return {
            'type':       'UnknownRadical',
            'candidates': sorted(self.candidates),
            'position':   self.position.value,
        }


@dataclass(frozen=True)
class EvidenceAssessment:
    """
    Assessment of one piece of evidence toward a radical identity claim.

    admissible      — is this evidence type permissible at all?
    supports_claim  — which identity does it support? (e.g. 'ي', 'و', 'و/ي', or None)
    sufficiency     — SUFFICIENT / CONTRIBUTORY / INSUFFICIENT
    source          — machine-readable code for the evidence type
    note            — human-readable explanation
    """
    admissible:     bool
    supports_claim: Optional[str]
    sufficiency:    EvidenceSufficiency
    source:         str
    note:           str = ''

    def to_dict(self) -> dict:
        return {
            'admissible':     self.admissible,
            'supports_claim': self.supports_claim,
            'sufficiency':    self.sufficiency.value,
            'source':         self.source,
            'note':           self.note,
        }


@dataclass(frozen=True)
class RootProfile:
    """
    Morphological profile for a root.

    weakness        — primary weakness classification
    weak_positions  — frozenset of WeakPosition values that are weak
    hamza_position  — 'FA' | 'AYN' | 'LAM' | None
    """
    weakness:       WeaknessType
    weak_positions: frozenset = frozenset()
    hamza_position: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'weakness':       self.weakness.value,
            'weak_positions': sorted(p.value for p in self.weak_positions),
            'hamza_position': self.hamza_position,
        }


@dataclass
class RootCandidate:
    """
    One root candidate produced from a single surface form.

    radicals   — 3-tuple of (str | UnknownRadical); str = identified consonant
    profile    — RootProfile for this candidate
    evidence   — list of EvidenceAssessment records used to reach this candidate
    decision   — 'ACCEPT' | 'DEFER' | 'REJECT'
    residuals  — list of residual codes (non-empty when decision != ACCEPT)
    note       — free-text annotation
    """
    radicals:  tuple
    profile:   RootProfile
    evidence:  list
    decision:  str
    residuals: list
    note:      str = ''

    def to_dict(self) -> dict:
        radicals_out = []
        for r in self.radicals:
            if isinstance(r, UnknownRadical):
                radicals_out.append(r.to_dict())
            else:
                radicals_out.append(r)
        return {
            'radicals':  radicals_out,
            'profile':   self.profile.to_dict(),
            'evidence':  [e.to_dict() for e in self.evidence],
            'decision':  self.decision,
            'residuals': list(self.residuals),
            'note':      self.note,
        }


@dataclass
class SurfaceAnalysis:
    """
    Result of analysing a single surface form.

    input_surface        — exactly as given by the caller
    normalized_surface   — after normalize_hamza()
    form_type            — detected morphological form type
    candidates           — list of RootCandidate (may be empty)
    decision             — 'ACCEPT' | 'DEFER' | 'BLOCK'
    residuals            — residual codes
    root_path_directive  — 'OPEN' | 'BLOCK' | None (from Internal Boundary Layer)
    boundary_kind        — BoundaryKind.value | None

    Decision semantics:
      ACCEPT — root identity closed with sufficient evidence
      DEFER  — root engine ran but could not close (UnknownRadical remains)
      BLOCK  — Internal Boundary Layer blocked the root path before form detection;
               the surface is not declared invalid, but the root stage was not opened
    """
    input_surface:        str
    normalized_surface:   str
    form_type:            str
    candidates:           list
    decision:             str
    residuals:            list
    root_path_directive:  Optional[str] = None   # 'OPEN' | 'BLOCK'
    boundary_kind:        Optional[str] = None   # BoundaryKind.value

    def to_dict(self) -> dict:
        d = {
            'input_surface':      self.input_surface,
            'normalized_surface': self.normalized_surface,
            'form_type':          self.form_type,
            'candidates':         [c.to_dict() for c in self.candidates],
            'decision':           self.decision,
            'residuals':          list(self.residuals),
        }
        if self.root_path_directive is not None:
            d['root_path_directive'] = self.root_path_directive
        if self.boundary_kind is not None:
            d['boundary_kind'] = self.boundary_kind
        return d


@dataclass
class LexemeAnalysis:
    """
    Result of analysing two or more surface forms together.

    forms          — list of input surfaces
    root           — closed root tuple (str, str, str) if decision == ACCEPT, else None
    profile        — RootProfile if decision == ACCEPT, else None
    decision       — 'ACCEPT' | 'DEFER' | 'REJECT'
    evidence_chain — ordered list of EvidenceAssessment records
    residuals      — residual codes
    """
    forms:          list
    root:           Optional[tuple]
    profile:        Optional[RootProfile]
    decision:       str
    evidence_chain: list
    residuals:      list

    def to_dict(self) -> dict:
        root_out = list(self.root) if self.root else None
        return {
            'forms':          list(self.forms),
            'root':           root_out,
            'profile':        self.profile.to_dict() if self.profile else None,
            'decision':       self.decision,
            'evidence_chain': [e.to_dict() for e in self.evidence_chain],
            'residuals':      list(self.residuals),
        }


# ══════════════════════════════════════════════════════════════════════════════
# §3  Constants
# ══════════════════════════════════════════════════════════════════════════════

WEAK_LETTERS          = frozenset({'و', 'ي'})
HAMZA                 = 'ء'
ALEF                  = 'ا'
ALEF_MAQSURA          = 'ى'
DEFECTIVE_PAST_FINALS = frozenset({ALEF, ALEF_MAQSURA})
MUDARIC_PREFIX_CHARS  = frozenset({'ي', 'ت', 'ن', HAMZA})

SHORT_VOWELS = frozenset({FATHA, KASRA, DAMMA})


# ══════════════════════════════════════════════════════════════════════════════
# §4  Internal helpers
# ══════════════════════════════════════════════════════════════════════════════

def _phones(surface: str) -> list[Phone]:
    """Parse surface into Phone list after hamza normalization."""
    return parse_phones(normalize_hamza(surface))


def _has_haraka(phone: Phone) -> bool:
    return bool(phone.diacritics) and phone.diacritics[0] in SHORT_VOWELS


def _haraka(phone: Phone) -> Optional[str]:
    """Return the short-vowel diacritic of this phone, or None."""
    if phone.diacritics and phone.diacritics[0] in SHORT_VOWELS:
        return phone.diacritics[0]
    return None


def _is_mudaric_prefix_phone(p: Phone) -> bool:
    """True if p looks like a mudaric prefix (ي/ت/ن/ء with fatha)."""
    return (
        not p.is_vowel_letter()
        and p.char in MUDARIC_PREFIX_CHARS
        and _haraka(p) == FATHA
    )


def _root_char(phone: Phone) -> str:
    """
    The root-identity character for a consonantal phone.
    Returns the normalized char (hamza already unified to ء by _phones()).
    """
    return phone.char


def _assess_final_vl(phone: Phone) -> EvidenceAssessment:
    """
    Evidence assessment for the final vowel-letter in a defective past form.

    ا   → admissible, INSUFFICIENT (doesn't distinguish و vs ي)
    ى   → admissible, CONTRIBUTORY  (suggests ي, the standard ى-final pattern)
    و/ي → admissible, SUFFICIENT    (LAM is visible)
    """
    ch = phone.char
    if ch == ALEF:
        return EvidenceAssessment(
            admissible=True,
            supports_claim=None,
            sufficiency=EvidenceSufficiency.INSUFFICIENT,
            source='ALEF_FINAL_PAST',
            note='ا النهائية تحقيق سطحي مشترك لـ و/ي — لا تُعيِّن الهوية',
        )
    if ch == ALEF_MAQSURA:
        return EvidenceAssessment(
            admissible=True,
            supports_claim='ي',
            sufficiency=EvidenceSufficiency.CONTRIBUTORY,
            source='ALEF_MAQSURA_FINAL',
            note='ى النهائية مساهم في ترجيح الياء — غير كافٍ وحده',
        )
    if ch in WEAK_LETTERS:
        return EvidenceAssessment(
            admissible=True,
            supports_claim=ch,
            sufficiency=EvidenceSufficiency.SUFFICIENT,
            source='VISIBLE_WEAK_FINAL',
            note=f'لام الجذر {ch} ظاهرة في موضع اللام',
        )
    # Should not reach here under normal flow
    return EvidenceAssessment(
        admissible=False,
        supports_claim=None,
        sufficiency=EvidenceSufficiency.INSUFFICIENT,
        source='UNKNOWN_FINAL',
        note=f'حرف نهائي غير معروف: {ch!r}',
    )


def _assess_hollow_ayn_vl(phone: Phone) -> EvidenceAssessment:
    """Evidence for the visible VL in the AYN position of a hollow present."""
    ch = phone.char
    if ch in WEAK_LETTERS:
        return EvidenceAssessment(
            admissible=True,
            supports_claim=ch,
            sufficiency=EvidenceSufficiency.SUFFICIENT,
            source='VISIBLE_HOLLOW_AYN',
            note=f'عين الجذر {ch} ظاهرة في موضع العين — تُغلق هوية العين',
        )
    return EvidenceAssessment(
        admissible=False,
        supports_claim=None,
        sufficiency=EvidenceSufficiency.INSUFFICIENT,
        source='UNKNOWN_AYN_VL',
        note=f'حرف علة في موضع العين غير معروف: {ch!r}',
    )


def _lafif_candidate_check(
    fa_char: str,
    ayn_char: str,
    lam_or_unknown,
) -> bool:
    """
    True if multiple positions appear weak — signals LAFIF (DEFER to PR 3.6).

    A position is "weak" if its identified character is و or ي.
    The LAM position is considered weak if it is an UnknownRadical or if the
    identified character is و or ي.

    Governing rule: و or ي in ANY position is an inherently weak radical,
    regardless of whether it appears consonantally or as a vowel letter on the
    surface. Two or more weak positions → LAFIF.
    """
    fa_weak  = fa_char  in WEAK_LETTERS
    ayn_weak = ayn_char in WEAK_LETTERS
    if isinstance(lam_or_unknown, UnknownRadical):
        lam_weak = True   # unknown → candidates contain weak letters
    else:
        lam_weak = lam_or_unknown in WEAK_LETTERS
    return sum([fa_weak, ayn_weak, lam_weak]) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# §5  Form-specific extractors
# ══════════════════════════════════════════════════════════════════════════════

# ── §5-A  Defective past  (فَعَلَ / فَعِلَ with final ا or ى)  ─────────────────
#
#  Pattern: exactly 3 phones
#    phone[0] — FA  : consonant with fatha
#    phone[1] — AYN : consonant with any short vowel
#    phone[2] — LAM : ا or ى (vowel letter, no diacritics)
#
#  Both دَعَا (→ UnknownRadical{و،ي}) and رَمَى (→ UnknownRadical{و،ي},
#  CONTRIBUTORY for ي) follow this path.

def _detect_defective_past(phones: list[Phone]) -> bool:
    if len(phones) != 3:
        return False
    p0, p1, p2 = phones
    return (
        not p0.is_vowel_letter()
        and _haraka(p0) == FATHA          # FA must carry fatha (Form I past)
        and not p1.is_vowel_letter()
        and _has_haraka(p1)               # AYN has a short vowel
        and p2.is_vowel_letter()
        and p2.char in DEFECTIVE_PAST_FINALS
    )


def _extract_defective_past(phones: list[Phone]) -> RootCandidate:
    p0, p1, p2 = phones
    fa_char  = _root_char(p0)
    ayn_char = _root_char(p1)
    lam_unknown = UnknownRadical(
        candidates=frozenset({'و', 'ي'}),
        position=WeakPosition.LAM,
    )

    ev_final = _assess_final_vl(p2)
    evidence = [ev_final]

    # Lafif check: if FA or AYN is itself weak → LAFIF
    if _lafif_candidate_check(fa_char, ayn_char, lam_unknown):
        profile = RootProfile(
            weakness=WeaknessType.LAFIF,
            weak_positions=frozenset(
                pos for pos, ch in [(WeakPosition.FA, fa_char), (WeakPosition.AYN, ayn_char)]
                if ch in WEAK_LETTERS
            ) | {WeakPosition.LAM},
        )
        return RootCandidate(
            radicals=(fa_char, ayn_char, lam_unknown),
            profile=profile,
            evidence=evidence,
            decision='DEFER',
            residuals=['defer:root:lafif_multiple_weak_positions'],
            note='أكثر من موضع اعتلال — يحتاج معالجة اللفيف (PR 3.6)',
        )

    profile = RootProfile(
        weakness=WeaknessType.DEFECTIVE,
        weak_positions=frozenset({WeakPosition.LAM}),
    )
    return RootCandidate(
        radicals=(fa_char, ayn_char, lam_unknown),
        profile=profile,
        evidence=evidence,
        decision='DEFER',
        residuals=['defer:root:defective_final_radical_unresolved'],
        note='لام الجذر المعتلة غير محددة — ادخل دليلًا زوجيًا أو معجميًا',
    )


# ── §5-B  Defective present  (يَفْعُلُ / يَفْعِلُ with final و or ي)  ──────────
#
#  Pattern: exactly 4 phones
#    phone[0] — prefix : يَ/تَ/نَ/ءَ (mudaric prefix with fatha)
#    phone[1] — FA     : consonant with SUKUN
#    phone[2] — AYN    : consonant with short vowel
#    phone[3] — LAM    : و or ي (vowel letter, visible → SUFFICIENT)
#
#  Guard: the و/ي at phone[3] must be the LAST phone (no suffix following).
#  يَدْعُونَ has 5 phones (phone[4]=نَ) → does not match → not defective.

def _detect_defective_pres(phones: list[Phone]) -> bool:
    if len(phones) != 4:
        return False
    p0, p1, p2, p3 = phones
    return (
        _is_mudaric_prefix_phone(p0)
        and not p1.is_vowel_letter()
        and p1.is_sakin()                 # FA has sukun
        and not p2.is_vowel_letter()
        and _has_haraka(p2)              # AYN has short vowel
        and p3.is_vowel_letter()
        and p3.char in WEAK_LETTERS       # LAM is و or ي (visible)
    )


def _extract_defective_pres(phones: list[Phone]) -> RootCandidate:
    p1, p2, p3 = phones[1], phones[2], phones[3]
    fa_char  = _root_char(p1)
    ayn_char = _root_char(p2)
    lam_char = p3.char  # و or ي — visible LAM

    ev_lam = _assess_final_vl(p3)  # returns SUFFICIENT for و/ي
    evidence = [ev_lam]

    # Lafif check: AYN = consonantal و/ي AND LAM = و/ي → LAFIF MAQRUN
    if _lafif_candidate_check(fa_char, ayn_char, lam_char):
        weak_pos = frozenset(
            pos for pos, ch in [
                (WeakPosition.FA, fa_char),
                (WeakPosition.AYN, ayn_char),
                (WeakPosition.LAM, lam_char),
            ]
            if ch in WEAK_LETTERS
        )
        profile = RootProfile(
            weakness=WeaknessType.LAFIF,
            weak_positions=weak_pos,
        )
        return RootCandidate(
            radicals=(fa_char, ayn_char, lam_char),
            profile=profile,
            evidence=evidence,
            decision='DEFER',
            residuals=['defer:root:lafif_multiple_weak_positions'],
            note='أكثر من موضع اعتلال — يحتاج معالجة اللفيف (PR 3.6)',
        )

    profile = RootProfile(
        weakness=WeaknessType.DEFECTIVE,
        weak_positions=frozenset({WeakPosition.LAM}),
    )
    # Root is closed: LAM is visible and SUFFICIENT
    return RootCandidate(
        radicals=(fa_char, ayn_char, lam_char),
        profile=profile,
        evidence=evidence,
        decision='ACCEPT',
        residuals=[],
        note='لام الجذر ظاهرة في المضارع — الجذر مُغلق (بدون باب أو تصريف)',
    )


# ── §5-C  Hollow past  (فَعَلَ with medial ا replacing AYN)  ──────────────────
#
#  Pattern: exactly 3 phones
#    phone[0] — FA  : consonant with fatha
#    phone[1] — AYN : ا (vowel letter in medial position — substitutes AYN)
#    phone[2] — LAM : consonant with fatha
#
#  بَاعَ/قَالَ: AYN is replaced by ا → UnknownRadical{و،ي}
#  The ا does not distinguish و from ي — EvidenceAssessment: INSUFFICIENT.

def _detect_hollow_past(phones: list[Phone]) -> bool:
    if len(phones) != 3:
        return False
    p0, p1, p2 = phones
    return (
        not p0.is_vowel_letter()
        and _haraka(p0) == FATHA
        and p1.is_vowel_letter()
        and p1.char == ALEF               # medial ا = AYN placeholder
        and not p2.is_vowel_letter()
        and _has_haraka(p2)
    )


def _extract_hollow_past(phones: list[Phone]) -> RootCandidate:
    p0, p1, p2 = phones
    fa_char  = _root_char(p0)
    lam_char = _root_char(p2)
    ayn_unknown = UnknownRadical(
        candidates=frozenset({'و', 'ي'}),
        position=WeakPosition.AYN,
    )

    ev_ayn = EvidenceAssessment(
        admissible=True,
        supports_claim=None,
        sufficiency=EvidenceSufficiency.INSUFFICIENT,
        source='ALEF_MEDIAL_HOLLOW_PAST',
        note='ا في موضع العين — تُثبت الإعلال لكنها لا تُعيِّن و/ي',
    )
    evidence = [ev_ayn]

    profile = RootProfile(
        weakness=WeaknessType.HOLLOW,
        weak_positions=frozenset({WeakPosition.AYN}),
    )
    return RootCandidate(
        radicals=(fa_char, ayn_unknown, lam_char),
        profile=profile,
        evidence=evidence,
        decision='DEFER',
        residuals=['defer:root:hollow_medial_radical_unresolved'],
        note='عين الجذر المعتلة غير محددة — ادخل دليلًا زوجيًا',
    )


# ── §5-D  Hollow present  (يَفْعُلُ with medial و/ي = AYN visible)  ───────────
#
#  Pattern: exactly 4 phones
#    phone[0] — prefix : mudaric يَ/تَ/نَ/ءَ
#    phone[1] — FA     : consonant WITH a short vowel (damma/kasra — NOT sukun)
#                        The short vowel migrated here because AYN is a VL.
#    phone[2] — AYN    : و or ي (vowel letter in MEDIAL position, before LAM)
#    phone[3] — LAM    : consonant with short vowel

def _detect_hollow_pres(phones: list[Phone]) -> bool:
    if len(phones) != 4:
        return False
    p0, p1, p2, p3 = phones
    return (
        _is_mudaric_prefix_phone(p0)
        and not p1.is_vowel_letter()
        and _has_haraka(p1)               # FA has short vowel (NOT sukun)
        and not p1.is_sakin()
        and p2.is_vowel_letter()
        and p2.char in WEAK_LETTERS       # AYN is visible و or ي
        and not p3.is_vowel_letter()
        and _has_haraka(p3)              # LAM has short vowel
    )


def _extract_hollow_pres(phones: list[Phone]) -> RootCandidate:
    p1, p2, p3 = phones[1], phones[2], phones[3]
    fa_char  = _root_char(p1)
    ayn_char = p2.char   # و or ي — visible AYN
    lam_char = _root_char(p3)

    ev_ayn = _assess_hollow_ayn_vl(p2)
    evidence = [ev_ayn]

    profile = RootProfile(
        weakness=WeaknessType.HOLLOW,
        weak_positions=frozenset({WeakPosition.AYN}),
    )
    return RootCandidate(
        radicals=(fa_char, ayn_char, lam_char),
        profile=profile,
        evidence=evidence,
        decision='ACCEPT',
        residuals=[],
        note='عين الجذر ظاهرة في المضارع — الجذر مُغلق (بدون باب أو تصريف)',
    )


# ── §5-E  Assimilated past with visible FA-yaiyya (يَئِسَ / يَبِسَ pattern)  ──
#
#  PR 3.4 standalone fix.
#
#  Pattern: exactly 3 phones, all consonantal (no VL), FA = ي
#    phone[0] — FA  : ي with fatha (consonantal — visible in past Form I)
#    phone[1] — AYN : any consonant with short vowel
#    phone[2] — LAM : any consonant with short vowel
#
#  Distinguishes يَئِسَ (past, FA=ي) from يَعِدُ (present, assimilated FA=و
#  deleted) because:
#    – يَعِدُ is 3 phones with NO VL but also no sukun pattern matching the
#      mudaric prefix rule; it falls through to UNRECOGNIZED for this PR.
#    – يَئِسَ: FA=ي WITH fatha, AYN=ء WITH kasra, LAM=س WITH fatha — all
#      short vowels, pattern FaCiCa (صيغة فَعِلَ past tense).
#
#  Hamza in AYN position is recorded as hamza_position='AYN' in the profile.

def _detect_assimilated_past_fa_yai(phones: list[Phone]) -> bool:
    if len(phones) != 3:
        return False
    p0, p1, p2 = phones
    return (
        not p0.is_vowel_letter()
        and p0.char == 'ي'
        and _haraka(p0) == FATHA
        and not p1.is_vowel_letter()
        and _has_haraka(p1)
        and not p2.is_vowel_letter()
        and _has_haraka(p2)
    )


def _extract_assimilated_past_fa_yai(phones: list[Phone]) -> RootCandidate:
    p0, p1, p2 = phones
    fa_char  = _root_char(p0)   # ي
    ayn_char = _root_char(p1)   # e.g. ء or ب
    lam_char = _root_char(p2)

    hamza_pos = 'AYN' if ayn_char == HAMZA else None

    profile = RootProfile(
        weakness=WeaknessType.ASSIMILATED,
        weak_positions=frozenset({WeakPosition.FA}),
        hamza_position=hamza_pos,
    )
    return RootCandidate(
        radicals=(fa_char, ayn_char, lam_char),
        profile=profile,
        evidence=[EvidenceAssessment(
            admissible=True,
            supports_claim='ي',
            sufficiency=EvidenceSufficiency.SUFFICIENT,
            source='VISIBLE_FA_YAI',
            note='فاء الجذر ي ظاهرة في الماضي — اعتلال المثال بالياء',
        )],
        decision='ACCEPT',
        residuals=[],
        note='فاء يائية ظاهرة — الجذر مُغلق',
    )


# ── §5-F  UNRECOGNIZED fallback  ──────────────────────────────────────────────

def _unrecognized_candidate(phones: list[Phone], reason: str) -> RootCandidate:
    return RootCandidate(
        radicals=(None, None, None),
        profile=RootProfile(weakness=WeaknessType.SOUND),
        evidence=[],
        decision='DEFER',
        residuals=[f'defer:root:{reason}'],
        note=reason,
    )


# ══════════════════════════════════════════════════════════════════════════════
# §6  Public API — extract_radicals()
# ══════════════════════════════════════════════════════════════════════════════

_FORM_DETECTORS = [
    # Order matters: more specific patterns first
    ('DEFECTIVE_PRESENT',         _detect_defective_pres,        _extract_defective_pres),
    ('HOLLOW_PRESENT',            _detect_hollow_pres,           _extract_hollow_pres),
    ('ASSIMILATED_PAST_FA_YAI',   _detect_assimilated_past_fa_yai, _extract_assimilated_past_fa_yai),
    ('DEFECTIVE_PAST',            _detect_defective_past,        _extract_defective_past),
    ('HOLLOW_PAST',               _detect_hollow_past,           _extract_hollow_past),
]


def _compressed_candidate(phones: list[Phone]) -> RootCandidate:
    """Build a RootCandidate for a 2-phone compressed surface (PR 3.7-B).

    The two visible phones are assigned to FA (phone[0]) and LAM (phone[1]).
    The medial AYN was elided and is recorded as an UnknownRadical with an
    empty candidate set — it cannot be recovered from the surface alone.

    Structural note: for assimilated verbs where FA was elided (قِفْ from وَقَفَ),
    the FA=phone[0] / LAM=phone[1] assignment is positionally incorrect, but the
    decision is DEFER so no root identity is asserted.  Exact position and radical
    identity require a paired form (PR 3.7-C) or a licensed registry entry.

    Governing constraint: لا يُرفع الحرف المحذوف إلى هوية جذرية.
    """
    fa_char  = phones[0].char
    lam_char = phones[1].char
    unknown_ayn = UnknownRadical(
        candidates=frozenset(),    # surface alone cannot determine the elided radical
        position=WeakPosition.AYN,
    )
    profile = RootProfile(
        weakness=WeaknessType.HOLLOW,
        weak_positions=frozenset({WeakPosition.AYN}),
    )
    evidence = [
        EvidenceAssessment(
            admissible=True,
            supports_claim='compressed_surface_detected',
            sufficiency=EvidenceSufficiency.INSUFFICIENT,
            source='structural:compressed_verb_candidate',
            note=(
                f'2-phone compressed surface: FA={fa_char}, LAM={lam_char}. '
                'AYN elision structurally assumed; exact position and identity '
                'require a paired form (PR 3.7-C).'
            ),
        )
    ]
    return RootCandidate(
        radicals=(fa_char, unknown_ayn, lam_char),
        profile=profile,
        evidence=evidence,
        decision='DEFER',
        residuals=['defer:root:compressed_form_unknown_medial_radical'],
        note='compressed surface: AYN position unknown — requires paired form for closure',
    )


def extract_radicals(surface: str) -> SurfaceAnalysis:
    """
    Analyse a single surface form and return root candidates.

    Pipeline (PR 3.7-A/fix):
      1. assess_boundary(surface)
         • BLOCK directive (CLOSED_FUNCTION_WORD or structural impossibility)
           → return decision='BLOCK'; root stage not opened.
         • DEFER directive (AMBIGUOUS or POSSIBLE_FUNCTION_WORD)
           → return decision='DEFER'; path acknowledged but form detection skipped.
           DEFER ≠ BLOCK: the word is not declared closed, only the judgment deferred.
         • COMPRESSED_VERB_CANDIDATE → _compressed_candidate(); decision=DEFER.
         • ROOT_ELIGIBLE → continue to _FORM_DETECTORS below.

      2. _FORM_DETECTORS (PR 3.4 + PR 3.5)
         • Hollow past / present, defective past / present, assimilated FA-yaiyya.
         • No-match → DEFER with 'unrecognized_surface_form'.

    Governing invariants:
      ● ا/ى final is NEVER a root identity (always UnknownRadical{و،ي}).
      ● No word-specific exceptions.
      ● Elided radicals in compressed forms remain UnknownRadical — not invented.
      ● BLOCK only for inventory-confirmed closed words and structural impossibilities.
      ● Structural ambiguity (AMBIGUOUS) → DEFER, not BLOCK.
      ● EvidenceAssessment records explain every claim.
    """
    # ── Stage 1: Internal Boundary Layer ─────────────────────────────────────
    boundary = assess_boundary(surface)
    norm   = boundary.normalized
    phones = parse_phones(norm)

    if boundary.directive == RootPathDirective.BLOCK:
        # Hard block: inventory-confirmed closed word or structural impossibility.
        # Root stage not opened — do not enter form detectors.
        return SurfaceAnalysis(
            input_surface=surface,
            normalized_surface=norm,
            form_type='BOUNDARY_BLOCKED',
            candidates=[],
            decision='BLOCK',
            residuals=[f'block:root:boundary_{boundary.kind.value.lower()}'],
            root_path_directive='BLOCK',
            boundary_kind=boundary.kind.value,
        )

    if boundary.directive == RootPathDirective.DEFER:
        # Soft defer: structurally ambiguous or possible function word.
        # Path acknowledged; form detectors NOT run (unsafe without paradigm context).
        # DEFER ≠ BLOCK: the surface is not declared root-ineligible.
        _DEFER_RESIDUALS = {
            BoundaryKind.AMBIGUOUS:              'ambiguous_prefix_form',
            BoundaryKind.POSSIBLE_FUNCTION_WORD: 'possible_function_word',
        }
        residual_key = _DEFER_RESIDUALS.get(boundary.kind, 'boundary_deferred')
        return SurfaceAnalysis(
            input_surface=surface,
            normalized_surface=norm,
            form_type='BOUNDARY_DEFERRED',
            candidates=[],
            decision='DEFER',
            residuals=[f'defer:root:{residual_key}'],
            root_path_directive='DEFER',
            boundary_kind=boundary.kind.value,
        )

    if boundary.kind == BoundaryKind.COMPRESSED_VERB_CANDIDATE:
        candidate = _compressed_candidate(phones)
        return SurfaceAnalysis(
            input_surface=surface,
            normalized_surface=norm,
            form_type='COMPRESSED_VERB_CANDIDATE',
            candidates=[candidate],
            decision='DEFER',
            residuals=list(candidate.residuals),
            root_path_directive='OPEN',
            boundary_kind=boundary.kind.value,
        )

    # ── Stage 2: Form detection (_FORM_DETECTORS) ─────────────────────────────
    for form_type, detect_fn, extract_fn in _FORM_DETECTORS:
        if detect_fn(phones):
            candidate = extract_fn(phones)
            return SurfaceAnalysis(
                input_surface=surface,
                normalized_surface=norm,
                form_type=form_type,
                candidates=[candidate],
                decision=candidate.decision,
                residuals=list(candidate.residuals),
                root_path_directive='OPEN',
                boundary_kind=boundary.kind.value,
            )

    # No pattern matched
    candidate = _unrecognized_candidate(phones, 'unrecognized_surface_form')
    return SurfaceAnalysis(
        input_surface=surface,
        normalized_surface=norm,
        form_type='UNRECOGNIZED',
        candidates=[candidate],
        decision='DEFER',
        residuals=['defer:root:unrecognized_surface_form'],
        root_path_directive='OPEN',
        boundary_kind=boundary.kind.value,
    )


# ══════════════════════════════════════════════════════════════════════════════
# §7  Public API — analyze_lexeme()
# ══════════════════════════════════════════════════════════════════════════════

def _resolve_unknown(unknown: UnknownRadical, value: str) -> str:
    """Replace an UnknownRadical with an identified char if value is a valid candidate."""
    if value in unknown.candidates:
        return value
    return unknown   # leave as UnknownRadical if candidate not supported


def analyze_lexeme(forms: list[str]) -> LexemeAnalysis:
    """
    Analyse two or more surface forms together to close root identity.

    Algorithm
    ─────────
    1. Run extract_radicals() on each form independently.
    2. Identify the consensus FA, AYN, LAM across all forms:
       – A position is ACCEPTED if all forms agree on the same consonant.
       – A position is RESOLVED from an UnknownRadical if any form provides
         SUFFICIENT evidence for a specific candidate AND no other form
         contradicts it.
    3. If all three positions are closed (identified strings, no UnknownRadical)
       and no LAFIF is flagged → decision = ACCEPT with the closed root.
    4. If any position remains unknown or any LAFIF is detected → DEFER.

    Governing rule: paired evidence from past + present is the standard
    closure mechanism for hollow and defective roots.
    """
    if not forms:
        return LexemeAnalysis(
            forms=[], root=None, profile=None,
            decision='DEFER',
            evidence_chain=[],
            residuals=['defer:root:no_forms_provided'],
        )

    surface_analyses = [extract_radicals(f) for f in forms]

    # Collect all evidence
    all_evidence: list[EvidenceAssessment] = []
    for sa in surface_analyses:
        for cand in sa.candidates:
            all_evidence.extend(cand.evidence)

    # Check for any LAFIF
    any_lafif = any(
        cand.profile.weakness == WeaknessType.LAFIF
        for sa in surface_analyses
        for cand in sa.candidates
    )
    if any_lafif:
        return LexemeAnalysis(
            forms=list(forms),
            root=None,
            profile=None,
            decision='DEFER',
            evidence_chain=all_evidence,
            residuals=['defer:root:lafif_multiple_weak_positions'],
        )

    # Try to close each position
    fa_candidates:  list[str] = []
    ayn_candidates: list[str] = []
    lam_candidates: list[str] = []

    for sa in surface_analyses:
        for cand in sa.candidates:
            r = cand.radicals
            if r == (None, None, None):
                continue

            fa, ayn, lam = r

            # FA
            if isinstance(fa, str):
                fa_candidates.append(fa)
            # AYN
            if isinstance(ayn, str):
                ayn_candidates.append(ayn)
            elif isinstance(ayn, UnknownRadical):
                pass  # will need resolution from another form
            # LAM
            if isinstance(lam, str):
                lam_candidates.append(lam)
            elif isinstance(lam, UnknownRadical):
                pass  # will need resolution from another form

    # Consensus check: all identified values must agree
    def _consensus(values: list[str]) -> Optional[str]:
        unique = set(values)
        if len(unique) == 1:
            return unique.pop()
        if len(unique) > 1:
            return None  # conflict
        return None  # empty — not identified

    fa_closed  = _consensus(fa_candidates)
    ayn_closed = _consensus(ayn_candidates)
    lam_closed = _consensus(lam_candidates)

    # All three must be closed
    if fa_closed and ayn_closed and lam_closed:
        # Determine weakness profile from closed root
        weak_positions = frozenset(
            pos for pos, ch in [
                (WeakPosition.FA,  fa_closed),
                (WeakPosition.AYN, ayn_closed),
                (WeakPosition.LAM, lam_closed),
            ]
            if ch in WEAK_LETTERS
        )
        n_weak = len(weak_positions)
        if n_weak >= 2:
            weakness = WeaknessType.LAFIF
        elif WeakPosition.LAM in weak_positions:
            weakness = WeaknessType.DEFECTIVE
        elif WeakPosition.AYN in weak_positions:
            weakness = WeaknessType.HOLLOW
        elif WeakPosition.FA in weak_positions:
            weakness = WeaknessType.ASSIMILATED
        else:
            weakness = WeaknessType.SOUND

        # Guard: LAFIF should have been caught above, but double-check
        if weakness == WeaknessType.LAFIF:
            return LexemeAnalysis(
                forms=list(forms),
                root=None,
                profile=None,
                decision='DEFER',
                evidence_chain=all_evidence,
                residuals=['defer:root:lafif_multiple_weak_positions'],
            )

        # Hamza position
        hamza_pos = None
        if fa_closed == HAMZA:
            hamza_pos = 'FA'
        elif ayn_closed == HAMZA:
            hamza_pos = 'AYN'
        elif lam_closed == HAMZA:
            hamza_pos = 'LAM'

        profile = RootProfile(
            weakness=weakness,
            weak_positions=weak_positions,
            hamza_position=hamza_pos,
        )
        return LexemeAnalysis(
            forms=list(forms),
            root=(fa_closed, ayn_closed, lam_closed),
            profile=profile,
            decision='ACCEPT',
            evidence_chain=all_evidence,
            residuals=[],
        )

    # At least one position unresolved
    residuals = ['defer:root:lexeme_closure_incomplete']
    if not fa_candidates:
        residuals.append('defer:root:fa_not_identified')
    if not ayn_candidates:
        residuals.append('defer:root:ayn_not_identified')
    if not lam_candidates:
        residuals.append('defer:root:lam_not_identified')

    return LexemeAnalysis(
        forms=list(forms),
        root=None,
        profile=None,
        decision='DEFER',
        evidence_chain=all_evidence,
        residuals=residuals,
    )
