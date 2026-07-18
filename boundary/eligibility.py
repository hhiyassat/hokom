"""
boundary/eligibility.py — PR 3.7-pre: Internal Boundary Layer
Pure structural rules for root-path eligibility.

These functions operate on a pre-parsed list[Phone] and have NO imports from
boundary.inventory or boundary.service — they are purely structural.

Rules:
  1. _is_compressed_verb_candidate — len==2, C(mutaharrik) + C(sakin)
  2. _is_ambiguous_prefix_form     — len==3, muḍāriʿ-prefix char with fatha + final VL
  3. _is_root_eligible_structure   — len>=3, ≥2 non-VL phones (default fallthrough)
"""

from __future__ import annotations

from syllabifier import Phone


# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

# Characters that can appear as the initial letter of a muḍāriʿ (present) prefix.
# و is intentionally excluded: وَقَى begins with و but it is a root consonant (FA),
# not a muḍāriʿ prefix in surface-form analysis.
_MUDARIC_PREFIX_CHARS: frozenset[str] = frozenset({'ي', 'ت', 'ن', 'ء'})

_FATHA = 'َ'


# ══════════════════════════════════════════════════════════════════════════════
# 1.  Compressed-verb candidate (قُلْ، قِفْ، عِدْ، زِنْ …)
# ══════════════════════════════════════════════════════════════════════════════

def _is_compressed_verb_candidate(phones: list[Phone]) -> bool:
    """Two-phone surface where FA is mutaharrik and LAM is sakin.

    This pattern corresponds to compressed imperatives (الأمر المضغوط) and
    compressed jussive forms of hollow/assimilated roots where one radical
    has been elided. The surface has exactly 2 phones: C(vowel) + C(sukun).

    Note: this rule fires ONLY when the surface is NOT in the inventory.
    Function particles like لَمْ/لَنْ also match this pattern and must be
    caught by inventory lookup before structural rules are applied.
    """
    if len(phones) != 2:
        return False
    fa, lam = phones[0], phones[1]
    return fa.is_mutaharrik() and lam.is_sakin()


# ══════════════════════════════════════════════════════════════════════════════
# 2.  Ambiguous prefix form (تَقِي، يَقِي …)
# ══════════════════════════════════════════════════════════════════════════════

def _is_ambiguous_prefix_form(phones: list[Phone]) -> bool:
    """Three-phone surface where the first phone looks like a muḍāriʿ prefix
    (char ∈ {ي،ت،ن،ء} with fatha) AND the last phone is a vowel letter.

    This pattern is ambiguous: the surface could be a 3rd-person muḍāriʿ
    of a defective root (يَقِي from وَقَى) OR a monosyllabic function word
    plus clitic. Cannot be resolved at the surface level without paradigm
    context; boundary returns AMBIGUOUS.
    """
    if len(phones) != 3:
        return False
    first, _, last = phones
    prefix_shaped = (
        first.char in _MUDARIC_PREFIX_CHARS
        and first.is_mutaharrik()
        and _FATHA in first.diacritics
    )
    final_vl = last.is_vowel_letter()
    return prefix_shaped and final_vl


# ══════════════════════════════════════════════════════════════════════════════
# 3.  Root-eligible structure (default path for len≥3)
# ══════════════════════════════════════════════════════════════════════════════

def _is_root_eligible_structure(phones: list[Phone]) -> bool:
    """Default check for surfaces with ≥3 phones.

    A surface is structurally root-eligible when it has at least 3 phones
    and at least 2 of them are non-VL consonants.  This admits trilateral
    roots with one vowel letter (hollow/defective), quadrilateral roots,
    and longer derived forms while excluding degenerate cases.
    """
    if len(phones) < 3:
        return False
    consonant_count = sum(1 for p in phones if not p.is_vowel_letter())
    return consonant_count >= 2


# ══════════════════════════════════════════════════════════════════════════════
# 4.  Public dispatcher (used by service.py)
# ══════════════════════════════════════════════════════════════════════════════

from boundary.models import BoundaryKind


def classify_by_structure(phones: list[Phone]) -> BoundaryKind:
    """Return the structural BoundaryKind for a phone list.

    This is called ONLY when inventory lookup returned None.
    Rules are applied in priority order:

    1. len < 2                       → UNDERLICENSED_SHORT_SURFACE
    2. len == 2 and C+sakin          → COMPRESSED_VERB_CANDIDATE
    3. len == 2 otherwise            → UNDERLICENSED_SHORT_SURFACE
    4. len >= 3 and ambiguous prefix → AMBIGUOUS
    5. len >= 3 and root-eligible    → ROOT_ELIGIBLE
    6. fallback                      → NON_VERBAL_SURFACE
    """
    n = len(phones)

    if n < 2:
        return BoundaryKind.UNDERLICENSED_SHORT_SURFACE

    if n == 2:
        if _is_compressed_verb_candidate(phones):
            return BoundaryKind.COMPRESSED_VERB_CANDIDATE
        return BoundaryKind.UNDERLICENSED_SHORT_SURFACE

    # n >= 3
    if _is_ambiguous_prefix_form(phones):
        return BoundaryKind.AMBIGUOUS

    if _is_root_eligible_structure(phones):
        return BoundaryKind.ROOT_ELIGIBLE

    return BoundaryKind.NON_VERBAL_SURFACE
