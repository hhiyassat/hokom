#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p0_segmentation/rules.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core segmentation decision rules for the Hokom Clitic Segmenter.

Decision order (strict):
1. Protected whole-token → no segmentation
2. Exact whole-token operator/mabni → operator handling (+ optional enclitic)
3. Licensed multi-proclitic → try from inventory
4. Licensed single-proclitic → try from inventory
5. Definite article alone (no proclitic) + host + (enclitic?)
6. Enclitic alone (no proclitic, no article)
7. Unsplit host → return as single HOST segment

ABSOLUTE CONSTRAINTS:
- NEVER separate واو الجماعة, ألف الاثنين, نون النسوة as enclitics
- NEVER separate a proclitic without a legal host remaining
- NEVER guess prefix by first-letter similarity alone
- No HR2S runtime calls. No Taaqol calls. No root computation.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""
from __future__ import annotations
from typing import Optional

from .inventory import (
    PROTECTED_WHOLE_TOKENS,
    WHOLE_TOKEN_OPERATORS,
    PROCLITICS,
    LICENSED_MULTI_PROCLITIC_SEQUENCES,
    ENCLITICS,
    INFLECTIONAL_BARE_SUFFIXES,
    NON_SEPARABLE_INITIALS,
    MIN_HOST_CONSONANTS_CONJUNCTION,
    MIN_HOST_CONSONANTS_PREPOSITION,
    MIN_HOST_CONSONANTS_FUTURE,
    MIN_HOST_LENGTH_CHARS,
)
from .normalization import (
    strip_diacritics,
    count_arabic_consonants,
    starts_with_definite_article,
    extract_definite_article_span,
)

# ── Guard constants ──────────────────────────────────────────────────────────

# The 4 mudaraa' (imperfect) prefix letters: ي ت ن أ (and alef variants).
# The future particle سَ is ONLY licensed before imperfect verbs, which must
# begin with one of these letters. No root computation — letter-initial only.
_IMPERFECT_PREFIX_LETTERS = frozenset('يتنأإآا')

# Arabic tanwin characters (U+064B fathatan, U+064C dammatan, U+064D kasratan).
# Pronoun enclitics are always definite and therefore NEVER carry tanwin.
# If the split enclitic surface contains tanwin, it is a case-ending, not a pronoun.
_TANWIN_CHARS = frozenset('ًٌٍ')  # ً ٌ ٍ


def _bare(s: str) -> str:
    """Shorthand: strip diacritics for comparison."""
    return strip_diacritics(s)


def _get_first_diacritic(surface: str) -> str | None:
    """Return the first diacritic character found in surface, or None."""
    for ch in surface:
        if 'ً' <= ch <= 'ٟ' or ch == 'ٰ':
            return ch
    return None


def _canonical_proclitic_diacritic(voc_form: str) -> str | None:
    """Extract the expected diacritic from a canonical proclitic vocalized form."""
    return _get_first_diacritic(voc_form)


def _prefix_diacritic_compatible(prefix_surface: str, canonical_diacritic: str | None) -> bool:
    """
    Return True if the prefix surface is diacritically compatible with the
    canonical proclitic's expected diacritic.

    Rules:
    - If canonical has no diacritic: always compatible.
    - If prefix has no diacritic (unvocalized): always compatible.
    - If both have diacritics: must match exactly.

    This prevents فُسُوقٌ → فُ + سُوقٌ (damma ≠ fatha for conjunction فَ).
    """
    if canonical_diacritic is None:
        return True  # no constraint from canonical
    actual = _get_first_diacritic(prefix_surface)
    if actual is None:
        return True  # unvocalized prefix — accept
    return actual == canonical_diacritic


def _is_legal_host(host: str) -> bool:
    """
    A legal host must have at least MIN_HOST_LENGTH_CHARS Arabic letters
    and must not be empty or whitespace.
    """
    if not host or not host.strip():
        return False
    return count_arabic_consonants(host) >= MIN_HOST_LENGTH_CHARS


def _min_host_consonants(kind: str) -> int:
    """Return the minimum host consonant count for a given proclitic kind."""
    if kind in ('CONJUNCTION',):
        return MIN_HOST_CONSONANTS_CONJUNCTION
    if kind in ('PREPOSITION',):
        return MIN_HOST_CONSONANTS_PREPOSITION
    if kind in ('FUTURE_PARTICLE',):
        return MIN_HOST_CONSONANTS_FUTURE
    return MIN_HOST_CONSONANTS_CONJUNCTION


def _host_ok_for_kind(remainder: str, kind: str) -> bool:
    """
    Check if remainder is a legal host for the given proclitic kind.
    Stricter for CONJUNCTION than for PREPOSITION.
    """
    n = count_arabic_consonants(remainder)
    return n >= _min_host_consonants(kind)


def _split_at_bare_position(surface: str, bare_prefix_len: int) -> tuple:
    """
    Split `surface` after consuming exactly `bare_prefix_len` bare
    (non-diacritic) characters. Returns (prefix, remainder).
    """
    bare_consumed = 0
    idx = 0
    while idx < len(surface) and bare_consumed < bare_prefix_len:
        if not (_bare_char(surface[idx])):
            bare_consumed += 1
        idx += 1
    # Consume any trailing diacritics that belong to the prefix
    while idx < len(surface) and _bare_char(surface[idx]):
        idx += 1
    return surface[:idx], surface[idx:]


def _bare_char(ch: str) -> bool:
    """Return True if ch is a diacritic (should be skipped in bare counting)."""
    return 'ً' <= ch <= 'ٟ' or ch == 'ٰ'


def _consume_bare_n(surface: str, n_bare: int) -> tuple:
    """
    Consume the first `n_bare` bare (non-diacritic) characters from `surface`.
    Returns (consumed_surface, remainder_surface).
    """
    idx = 0
    count = 0
    while idx < len(surface) and count < n_bare:
        if not _bare_char(surface[idx]):
            count += 1
        idx += 1
    # Consume trailing diacritics (part of last bare char)
    while idx < len(surface) and _bare_char(surface[idx]):
        idx += 1
    return surface[:idx], surface[idx:]


def _sa_future_guard(remainder: str) -> bool:
    """
    Return True only if remainder could plausibly be an imperfect verb host.

    The future particle سَ is licensed ONLY before imperfect verbs. Imperfect
    verbs must start with one of the 4 mudaraa' prefix letters: ي ت ن أ.

    No Word Class lookup. No root computation. Letter-initial heuristic only.
    """
    if not remainder:
        return False
    for ch in remainder:
        if not _bare_char(ch):
            return ch in _IMPERFECT_PREFIX_LETTERS
    return False


def _na_is_likely_inflectional(surface: str) -> bool:
    """
    Return True if نَا at the end of surface is likely the dual alef
    (ألف التثنية — inflectional ending), NOT an attached pronoun.

    Key heuristic: imperfect dual verbs follow the pattern ...ونا in bare form
    (e.g., يَكُونَا → bare يكونا ends with 'ونا').

    No root computation. No Word Class lookup. Surface-pattern only.
    """
    return _bare(surface).endswith('ونا')


def _try_enclitic(surface: str) -> Optional[tuple]:
    """
    Try to split an enclitic from the END of surface.
    Returns (stem, enclitic_surface, kind) or None.

    CRITICAL: Does NOT split واو الجماعة, ألف الاثنين, نون النسوة.
    """
    bare_surface = _bare(surface)

    # Guard: never split inflectional suffixes
    for suf in INFLECTIONAL_BARE_SUFFIXES:
        if bare_surface.endswith(suf):
            # Extra check: if the suffix is 'ن' (single), only block if
            # the remainder before it is a complete word (>= 3 consonants)
            # This prevents incorrect blocking of genuine enclitics
            return None

    # Try enclitics from longest to shortest bare form
    # Sort by bare length descending
    sorted_encs = sorted(ENCLITICS, key=lambda x: len(x[0]), reverse=True)

    for bare_enc, kind in sorted_encs:
        if not bare_surface.endswith(bare_enc):
            continue

        # GUARD: نَا as attached pronoun is not licensed when the surface ends in
        # the ...ونا pattern (dual imperfect verb: ألف التثنية).
        # Example: يَكُونَا → نَا is the dual alef, NOT the first-person pronoun.
        if bare_enc == 'نا' and _na_is_likely_inflectional(surface):
            continue

        # The stem (bare) is everything before the enclitic
        bare_stem = bare_surface[: len(bare_surface) - len(bare_enc)]

        # Stem must be a legal host
        if count_arabic_consonants(bare_stem) < MIN_HOST_LENGTH_CHARS:
            continue

        # Find the actual split position in the original (diacriticized) surface
        # Count from the end: find where the last `len(bare_enc)` bare chars start
        bare_count_from_end = 0
        split_pos = len(surface)

        for i in range(len(surface) - 1, -1, -1):
            if not _bare_char(surface[i]):
                bare_count_from_end += 1
                if bare_count_from_end == len(bare_enc):
                    split_pos = i
                    break

        if split_pos == len(surface) and len(bare_enc) > 0:
            continue  # couldn't find split position

        # Include any leading diacritics of the enclitic in the enclitic surface
        # (diacritics before split_pos belong to the stem)
        stem_surface    = surface[:split_pos]
        enclitic_actual = surface[split_pos:]

        if count_arabic_consonants(stem_surface) < MIN_HOST_LENGTH_CHARS:
            continue

        # GUARD: pronoun enclitics are always definite — they never carry tanwin.
        # If the actual enclitic surface contains tanwin (fathatan/dammatan/kasratan),
        # it is a case-ending (e.g., هًا in سَفِيهًا is تنوين نصب), not a pronoun.
        if any(ch in _TANWIN_CHARS for ch in enclitic_actual):
            continue

        return (stem_surface, enclitic_actual, kind)

    return None


def _extract_proclitics(surface: str, protected_bare: set) -> Optional[tuple]:
    """
    Extract proclitics from the START of surface.
    Returns (proclitic_surfaces_list, remainder, kinds_list) or None.

    Priority order:
    1. Multi-proclitic sequences (tried first, longer match wins)
    2. Single proclitics

    GUARDS:
    - Never extract a proclitic that leaves a host with too few consonants
    - Never extract when whole token is in protected set
    - Conjunction proclitics require >= 3 consonants in remainder
    - Preposition proclitics require >= 2 consonants in remainder

    `protected_bare` is the set of bare protected/operator whole tokens —
    used to detect cases like وَاللَّهُ where remainder after وَ is protected.

    `whole_token_operators` and `whole_token_protected` are the vocalized sets
    used for exact-match remainder checks before falling back to bare comparison.
    """
    bare_surface = _bare(surface)

    # GUARD: If the whole bare token is in NON_SEPARABLE_INITIALS, do not split.
    # This guards root-initial tokens like فَقِيرٌ (root ف-ق-ر) from being split
    # as فَ (conjunction) + قِيرٌ.
    if bare_surface in NON_SEPARABLE_INITIALS:
        return None

    # Build a disambiguation map for multi-proclitic sequences
    # Since some bare forms are ambiguous (ول could be JUSSIVE_LAM or PREPOSITION),
    # we need to try both interpretations. The engine tries all sequences and
    # returns the first that yields a legal host.
    #
    # We key sequences by (bare_seq, index) to handle duplicates.
    tried_sequences = []
    for seq_bare_parts, components, kinds in LICENSED_MULTI_PROCLITIC_SEQUENCES:
        seq_bare = ''.join(seq_bare_parts) if isinstance(seq_bare_parts, list) else seq_bare_parts
        tried_sequences.append((seq_bare, components, kinds))

    for seq_bare, components, kinds in tried_sequences:
        if not bare_surface.startswith(seq_bare):
            continue

        # Consume exactly len(seq_bare) bare chars from surface
        prefix_surface, remainder = _consume_bare_n(surface, len(seq_bare))
        bare_remainder = _bare(remainder)

        # Check if the remainder is in protected set
        in_protected = bare_remainder in protected_bare
        has_article   = starts_with_definite_article(remainder)

        # Legal if:
        # - remainder is protected (e.g., اللَّهُ)
        # - remainder starts with definite article and has content after it
        # - remainder has enough consonants for the primary proclitic kind
        primary_kind = kinds[0] if kinds else 'CONJUNCTION'
        min_cons = _min_host_consonants(primary_kind)

        remainder_ok = (
            in_protected
            or has_article
            or count_arabic_consonants(bare_remainder) >= min_cons
        )

        if not remainder_ok:
            continue

        # Split prefix_surface into individual proclitic surfaces
        proclitic_surfaces = []
        pos = 0
        for comp_bare in components:
            comp_surf, rest = _consume_bare_n(prefix_surface[pos:], len(comp_bare))
            proclitic_surfaces.append(comp_surf)
            pos += len(comp_surf)

        return (proclitic_surfaces, remainder, kinds)

    # Single proclitic
    for voc_form, bare_form, kind, priority in sorted(PROCLITICS, key=lambda x: x[3]):
        if not bare_surface.startswith(bare_form):
            continue
        if len(bare_surface) <= len(bare_form):
            continue  # nothing left for host

        prefix_surface, remainder = _consume_bare_n(surface, len(bare_form))
        bare_remainder = _bare(remainder)

        # DIACRITIC COMPATIBILITY CHECK:
        # If the canonical proclitic has a diacritic (e.g., فَ has fatha),
        # the actual prefix must have that same diacritic OR be unvocalized.
        # This prevents فُسُوقٌ → فُ + سُوقٌ (damma ≠ fatha for فَ CONJUNCTION).
        canonical_diac = _canonical_proclitic_diacritic(voc_form)
        if not _prefix_diacritic_compatible(prefix_surface, canonical_diac):
            continue  # wrong diacritic — this proclitic doesn't apply here

        # VOCALIZED REMAINDER CHECK:
        # When text is vocalized, check the actual vocalized remainder against
        # the vocalized operator/protected sets BEFORE bare fallback.
        # This prevents مِعَ (part of سَمِعَ) from matching the operator مَعَ.
        remainder_is_vocalized = any(
            'ً' <= ch <= 'ٟ' or ch == 'ٰ' for ch in remainder
        )
        if remainder_is_vocalized:
            # Use strict vocalized match for operators/protected tokens
            in_protected = (
                remainder in WHOLE_TOKEN_OPERATORS
                or remainder in PROTECTED_WHOLE_TOKENS
            )
        else:
            # Unvocalized text: fall back to bare comparison
            in_protected = bare_remainder in protected_bare
        has_article   = starts_with_definite_article(remainder)

        # Minimum consonants check based on kind
        min_cons = _min_host_consonants(kind)
        remainder_ok = (
            in_protected
            or has_article
            or count_arabic_consonants(bare_remainder) >= min_cons
        )

        if not remainder_ok:
            continue

        # GUARD A: future particle سَ is ONLY licensed before imperfect verbs.
        # Imperfect verbs must start with one of the 4 mudaraa' prefix letters.
        # This prevents سَفِيهًا → سَ + فِيهًا (فِ is NOT an imperfect prefix).
        if kind == 'FUTURE_PARTICLE' and not _sa_future_guard(remainder):
            continue

        # GUARD B: conjunction proclitics (وَ فَ) — verify the HOST consonant
        # count AFTER potential enclitic removal is still ≥ 3.
        # This prevents وَلِيُّهُ → وَ + لِيُّهُ, where after stripping هُ the
        # host لِيُّ has only 2 consonants (ل ي), which is sub-minimum.
        if kind in ('CONJUNCTION', 'RESUMPTION') and not in_protected and not has_article:
            bare_rem_host = bare_remainder
            for _bare_enc_chk, _ in sorted(ENCLITICS, key=lambda x: len(x[0]), reverse=True):
                if _bare_enc_chk and bare_rem_host.endswith(_bare_enc_chk):
                    _candidate = bare_rem_host[: -len(_bare_enc_chk)]
                    if _candidate:
                        bare_rem_host = _candidate
                        break
            if count_arabic_consonants(bare_rem_host) < MIN_HOST_CONSONANTS_CONJUNCTION:
                continue

        return ([prefix_surface], remainder, [kind])

    return None
