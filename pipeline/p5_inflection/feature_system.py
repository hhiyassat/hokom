#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/feature_system.py

Surface-level feature extraction for Arabic verbs.
Identifies person / number / gender / tense / mood / voice
by diacriticized pattern matching on the surface string.

No root knowledge required — operates on the surface alone.
"""
from __future__ import annotations
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# Arabic character constants
# ──────────────────────────────────────────────────────────────────────────────
FATHA        = 'َ'   # َ
DAMMA        = 'ُ'   # ُ
KASRA        = 'ِ'   # ِ
SUKUUN       = 'ْ'   # ْ
SHADDA       = 'ّ'   # ّ
TANWIN_FATH  = 'ً'   # ً
TANWIN_KASR  = 'ٍ'   # ٍ
TANWIN_DAMM  = 'ٌ'   # ٌ
TATWEEL      = 'ـ'   # ـ

WAW          = 'و'   # و
YAA          = 'ي'   # ي
ALIF         = 'ا'   # ا
ALIF_MAKSURA = 'ى'   # ى
TA           = 'ت'   # ت
HA_MARBUTA   = 'ة'   # ة
NUN          = 'ن'   # ن
HA           = 'ه'   # ه
HAMZA        = 'ء'   # ء
HAMZA_ABOVE  = 'أ'   # أ
HAMZA_BELOW  = 'إ'   # إ
HAMZA_ON_WAW = 'ؤ'   # ؤ
HAMZA_ON_YAA = 'ئ'   # ئ
ALIF_MADD    = 'آ'   # آ
ALIF_WASL    = 'ٱ'   # ٱ  (alif wasla — Unicode)

DIACRITICS = frozenset([
    FATHA, DAMMA, KASRA, SUKUUN, SHADDA,
    TANWIN_FATH, TANWIN_KASR, TANWIN_DAMM,
])

# Imperfect prefixes (bare letter)
IMPERFECT_PREFIX_LETTERS = frozenset([YAA, TA, HAMZA_ABOVE, HAMZA, NUN])
# أ U+0623 and ء U+0621 both appear as أ in prefixes


def strip_diacritics(s: str) -> str:
    """Remove all diacritics, returning bare consonants + matres."""
    return ''.join(c for c in s if c not in DIACRITICS)


def _bare(s: str) -> str:
    return strip_diacritics(s)


# ── Conjunction prefix stripping ──────────────────────────────────────────────

def _strip_conjunction_prefix(surface: str) -> str:
    """
    Strip leading وَ (waw+fatha) or فَ (fa+fatha) conjunction prefix.
    Requires at least 3 chars remaining after the strip so we don't
    consume an entire short word.
    """
    if len(surface) >= 4:          # prefix (2 chars) + at least 2 remaining
        first, second = surface[0], surface[1]
        if first in ('و', 'ف') and second == FATHA:
            return surface[2:]
    return surface


def _strip_lam_amr(surface: str) -> tuple:
    """
    Strip lam al-amr (لْ = lam + sukuun) from start of surface.
    Returns (stripped_surface, lam_amr_found: bool).
    Lam al-amr is always vowelless (sukuun).
    """
    if len(surface) >= 4:      # لْ (2 chars) + verb (≥2 chars)
        if surface[0] == 'ل' and surface[1] == SUKUUN:
            return surface[2:], True
    return surface, False


# ── Governing-particle sets (for multi-word input mood injection) ─────────────

# Prohibitive / conditional particles that govern the JUSSIVE
_JUSSIVE_PARTICLE_FORMS: frozenset = frozenset({
    'لَا',    # laa naahiya (prohibitive)
    'لَمْ',   # lam (past negation, jussive)
    'لَمَّا',  # lamma (past negation, jussive)
    'إِنْ',   # in (conditional)
    'وَلَا',  # wa-laa naahiya (compound prohibitive)
    'فَلَا',  # fa-laa naahiya (compound prohibitive)
    'لَا تَ', # laa + verb (alternative split)
    'وَإِنْ', # wa-in (compound conditional, jussive)
    'فَإِنْ', # fa-in (compound conditional, jussive)
})

# Particles that govern the SUBJUNCTIVE
_SUBJUNCTIVE_PARTICLE_FORMS: frozenset = frozenset({
    'أَنْ',   # an
    'لَنْ',   # lan (future negation)
    'كَيْ',   # kay
    'حَتَّى', # hatta
    'أَلَّا',  # alla = an + la (subjunctive + negation)
    'لِ',    # li-
    'لِيَ',   # liya
    'فَأَنْ', # fa-an
})


def _chars_and_diacs(s: str) -> list[tuple[str, list[str]]]:
    """
    Parse surface into list of (base_char, [diacritics]) pairs.
    Diacritics are attached to the immediately preceding base character.
    """
    result: list[tuple[str, list[str]]] = []
    for ch in s:
        if ch in DIACRITICS:
            if result:
                result[-1][1].append(ch)
        else:
            result.append((ch, []))
    return result


def _has_imperfect_prefix(s: str) -> Optional[str]:
    """
    Return the prefix letter if surface starts with an imperfect prefix.

    Automatically strips a leading conjunction prefix (وَ/فَ) before analysis.

    Detects:
      يَ/تَ/أَ/نَ  (active, fatha on prefix)
      يُ/تُ/أُ/نُ  (passive/augmented, damma on prefix)
      Geminated roots: prefix + C1 + C2+SHADDA (e.g. تَضِلَّ, يَرُدُّ)
      Hollow roots:    prefix + C1[damma/kasra] + و/ي + C3 (e.g. يَكُونُ, تَبِيعُ)
      Dual imperfect:  ends in ونا  (NOT past نا suffix)
      Augmented forms: 5+ bare chars with fatha prefix
    """
    # Strip conjunction prefix before all detection
    s = _strip_conjunction_prefix(s)

    if len(s) < 3:
        return None
    pairs = _chars_and_diacs(s)
    if len(pairs) < 3:
        return None

    first_char, first_diacs = pairs[0]
    if first_char not in IMPERFECT_PREFIX_LETTERS:
        return None

    has_fatha = FATHA in first_diacs
    has_damma = DAMMA in first_diacs

    if not has_fatha and not has_damma:
        return None  # prefix must carry a vowel

    # ── Classic test: fatha on prefix + sukuun on C1 ─────────────────────────
    if has_fatha and len(pairs) >= 2:
        _, second_diacs = pairs[1]
        if SUKUUN in second_diacs:
            return first_char

    # ── Damma on prefix (passive / augmented Form II-X) ──────────────────────
    if has_damma and len(pairs) >= 3:
        return first_char

    # ── Geminated root: prefix + C1 + C2+SHADDA ─────────────────────────────
    # e.g. تَضِلَّ (ت+ض[kasra]+ل[shadda]), يَرُدُّ (ي+ر[damma]+د[shadda])
    # SHADDA at pairs[2] is the doubling of C3=C2 for geminate roots.
    if (has_fatha or has_damma) and len(pairs) >= 3:
        if SHADDA in pairs[2][1]:
            return first_char

    # ── Hollow root: prefix + C1[damma/kasra] + و/ي/ا + C3 ──────────────────
    # e.g. يَكُونُ (ي+ك[DAMMA]+و+ن), تَبِيعُ (ت+ب[KASRA]+ي+ع)
    # C1 with damma/kasra distinguishes hollow imperfect from past Form IV
    # (أَقَامَ: C1 has fatha — NOT caught here → correctly stays PAST).
    if has_fatha and len(pairs) >= 4:
        _, c1_diacs = pairs[1]
        if DAMMA in c1_diacs or KASRA in c1_diacs:
            c2_char = pairs[2][0]
            if c2_char in (WAW, YAA, ALIF):
                return first_char

    # ── Normalized expanded geminate: scan for C+SUKUUN + same-C ────────────
    # The normalizer expands SHADDA to C+SUKUUN+C (e.g. تَضِلَّ→تَضِلْلَ).
    # After that expansion, pairs[k]=C[SUKUUN] followed by pairs[k+1]=same-C
    # is the fingerprint of a geminated-root imperfect.
    # This check runs AFTER the SHADDA check (SHADDA in pairs[2]) so that
    # original (non-normalized) forms are already caught above.
    if (has_fatha or has_damma) and len(pairs) >= 4:
        for k in range(1, len(pairs) - 1):
            c_k, d_k = pairs[k]
            c_k1, _  = pairs[k + 1]
            if c_k == c_k1 and SUKUUN in d_k and c_k not in DIACRITICS:
                return first_char

    # ── Extended: augmented forms (Form V-X) with 5+ bare chars ─────────────
    if has_fatha and len(pairs) >= 4:
        bare = strip_diacritics(s)
        if bare.endswith('وا'):
            return None  # past 3M_PL — not imperfect

        # Past-person suffixes — but exclude dual imperfect in -ونا
        # (يَكُونَا: bare='يكونا', ends in 'نا', but 'ن' is C3 not past suffix)
        _PAST_BARE_SUFFIXES = ('تم', 'تما', 'تنّ', 'تن', 'نا', 'تا')
        if not bare.endswith('ونا'):
            if any(bare.endswith(sfx) for sfx in _PAST_BARE_SUFFIXES):
                return None  # past tense with person/number suffix

        if len(bare) >= 5 and first_char in (YAA, TA, NUN):
            return first_char

    return None


def identify_tense(surface: str) -> Optional[str]:
    """
    Identify tense/aspect from surface.

    Returns one of: 'PAST' | 'IMPERFECT' | 'IMPERATIVE' | None.

    Handles:
      - Multi-word: recurse on last token (the verb)
      - Conjunction prefix وَ/فَ: stripped before classification
      - Lam al-amr لْ: stripped → IMPERFECT (JUSSIVE mood governed externally)
      - Form VIII assimilation imperative: اتَّقُوا (SHADDA on C1 + DAMMA on C2)
      - All other imperatives: hamzat al-wasl + C+sukuun
      - Imperfect: prefix letter يَ/تَ/أَ/نَ detected by _has_imperfect_prefix
      - Default: PAST
    """
    if not surface:
        return None

    # Multi-word input: take the final token as the verb
    parts = surface.split()
    if len(parts) >= 2:
        return identify_tense(parts[-1])

    # Strip conjunction prefix before classification
    stripped = _strip_conjunction_prefix(surface)

    # Lam al-amr (لْ): strips to an imperfect jussive stem
    stripped_lam, has_lam_amr = _strip_lam_amr(stripped)
    if has_lam_amr:
        return 'IMPERFECT'

    # ── Disambiguation: أَشْهِدُوا — Form IV imperative 2MP ──────────────────
    # When the stripped surface starts with أَ/ءَ (hamza+fatha, i.e. would look
    # like a 1SG imperfect prefix) + C+sukuun + ... + -وا (2MP/3MP suffix),
    # the -وا plural suffix rules out 1SG imperfect (which is always singular).
    # Such forms can ONLY be Form IV imperative (2MP).
    _pairs_stripped = _chars_and_diacs(stripped)
    if _pairs_stripped:
        _fc, _fd = _pairs_stripped[0]
        if _fc in (HAMZA, HAMZA_ABOVE) and FATHA in _fd:
            if len(_pairs_stripped) >= 2 and SUKUUN in _pairs_stripped[1][1]:
                _bare_stripped = strip_diacritics(stripped)
                if _bare_stripped.endswith('وا'):
                    return 'IMPERATIVE'

    # Imperfect: prefix letter detected on stripped surface
    prefix = _has_imperfect_prefix(stripped)
    if prefix is not None:
        return 'IMPERFECT'

    # Imperative: work on the stripped (conjunction-free) surface
    pairs = _chars_and_diacs(stripped)
    if not pairs:
        return 'PAST'

    first_char, first_diacs = pairs[0]
    if first_char in (ALIF, ALIF_WASL):
        if len(pairs) >= 3:
            second_char, second_diacs = pairs[1]
            # Classic imperative: hamzat al-wasl + C+sukuun (اِكْتُبْ, اُكْتُبُوا)
            # Guard 1: exclude definite article لْ (الْحَقُّ, الْأُخْرَى)
            # Guard 2: exclude dual nouns ending in ان (امرأتانِ, رجلانِ …).
            #   The dual nominative marker -ān cannot end a verb imperative.
            if SUKUUN in second_diacs and second_char != 'ل':
                _bare_chk = strip_diacritics(stripped)
                if not (_bare_chk.endswith('ان') and len(_bare_chk) > 4):
                    return 'IMPERATIVE'
            # Form VIII assimilation: اتَّقُوا — SHADDA on C1 (assimilation ت+ت→تّ)
            # + DAMMA on C2 (thematic vowel of the stem)
            if SHADDA in second_diacs and len(pairs) >= 4:
                _, third_diacs = pairs[2]
                if DAMMA in third_diacs:
                    return 'IMPERATIVE'

    # Default: PAST
    return 'PAST'


# ──────────────────────────────────────────────────────────────────────────────
# Past-tense feature extraction
# ──────────────────────────────────────────────────────────────────────────────

def extract_past_features(surface: str) -> dict:
    """
    Extract (person, number, gender, voice) from a past-tense surface.

    Returns a dict with keys: person, number, gender, voice, mood.
    Defaults: person=3, number=SG, gender=M (3rd masc sing = citation form).
    """
    bare = _bare(surface)

    # Voice detection (passive past: C1 has DAMMA)
    pairs = _chars_and_diacs(surface)
    voice = 'ACTIVE'
    if pairs and DAMMA in pairs[0][1] and len(pairs) >= 2 and KASRA in pairs[1][1]:
        voice = 'PASSIVE'  # فُعِلَ pattern

    # ── Suffix-based person/number/gender detection ───────────────────────────
    # Check suffixes in decreasing length to be unambiguous

    # 2nd person suffixes (contain تُنَّ, تُمَا, تُمْ, تِ, تَ, تُ)
    if bare.endswith('تنّ') or (surface.endswith('تُنَّ')):
        return {'person': '2', 'number': 'PL', 'gender': 'F', 'voice': voice, 'mood': None}

    if bare.endswith('تما') or surface.endswith('تُمَا'):
        return {'person': '2', 'number': 'DU', 'gender': 'M', 'voice': voice, 'mood': None}

    if bare.endswith('تم') or surface.endswith('تُمْ'):
        return {'person': '2', 'number': 'PL', 'gender': 'M', 'voice': voice, 'mood': None}

    # 1st person plural: ends in نا
    if bare.endswith('نا'):
        return {'person': '1', 'number': 'PL', 'gender': 'M', 'voice': voice, 'mood': None}

    # 3rd masc plural: ends in وا
    if bare.endswith('وا'):
        return {'person': '3', 'number': 'PL', 'gender': 'M', 'voice': voice, 'mood': None}

    # 3rd fem plural: ends in نَ (bare: ن, but not preceded by و or ي)
    if surface.endswith('ْنَ') or (bare.endswith('ن') and not bare.endswith('ون') and not bare.endswith('ين') and not bare.endswith('ان')):
        # Check it's a proper 3F_PL suffix (after C3+sukuun)
        if surface.endswith('ْنَ'):
            return {'person': '3', 'number': 'PL', 'gender': 'F', 'voice': voice, 'mood': None}

    # 3rd fem dual: ends in تا (with fatha on ta)
    if bare.endswith('تا') and not bare.endswith('ستا'):
        if surface.endswith('َتَا') or surface.endswith('تَا'):
            return {'person': '3', 'number': 'DU', 'gender': 'F', 'voice': voice, 'mood': None}

    # 3rd masc dual: ends in ا (bare, but NOT وا/تا/نا)
    if bare.endswith('ا') and not bare.endswith('وا') and not bare.endswith('نا') and not bare.endswith('تا'):
        return {'person': '3', 'number': 'DU', 'gender': 'M', 'voice': voice, 'mood': None}

    # 2nd fem singular: ends in تِ
    if surface.endswith('ْتِ') or surface.endswith('تِ'):
        return {'person': '2', 'number': 'SG', 'gender': 'F', 'voice': voice, 'mood': None}

    # 2nd masc singular: ends in تَ
    if surface.endswith('ْتَ') or surface.endswith('تَ'):
        # Make sure not a 3F_SG verb ending in تَا
        if not bare.endswith('تا'):
            return {'person': '2', 'number': 'SG', 'gender': 'M', 'voice': voice, 'mood': None}

    # 1st singular: ends in تُ
    if surface.endswith('ْتُ') or surface.endswith('تُ'):
        return {'person': '1', 'number': 'SG', 'gender': 'M', 'voice': voice, 'mood': None}

    # 3rd fem singular: ends in تْ
    if surface.endswith('َتْ') or surface.endswith('تْ'):
        return {'person': '3', 'number': 'SG', 'gender': 'F', 'voice': voice, 'mood': None}

    # Default: 3rd masc singular
    return {'person': '3', 'number': 'SG', 'gender': 'M', 'voice': voice, 'mood': None}


# ──────────────────────────────────────────────────────────────────────────────
# Imperfect-tense feature extraction
# ──────────────────────────────────────────────────────────────────────────────

def extract_imperfect_features(surface: str) -> dict:
    """
    Extract (person, number, gender, mood, voice) from an imperfect-tense surface.

    Returns a dict with keys: person, number, gender, mood, voice.
    """
    if not surface:
        return {'person': '3', 'number': 'SG', 'gender': 'M', 'mood': 'INDICATIVE', 'voice': 'ACTIVE'}

    pairs = _chars_and_diacs(surface)
    bare  = _bare(surface)

    # ── Prefix → person/gender (initial) ─────────────────────────────────────
    first_char = pairs[0][0] if pairs else ''

    # Person from prefix
    if first_char in (HAMZA_ABOVE, HAMZA):
        person_from_prefix = '1'
        gender_from_prefix = 'M'
        number_from_prefix = 'SG'
    elif first_char == NUN:
        person_from_prefix = '1'
        gender_from_prefix = 'M'
        number_from_prefix = 'PL'
    elif first_char == YAA:
        person_from_prefix = '3'
        gender_from_prefix = 'M'
        number_from_prefix = 'SG'  # refined by suffix
    elif first_char == TA:
        person_from_prefix = '2'   # could be 3F too; refined by suffix
        gender_from_prefix = 'M'
        number_from_prefix = 'SG'
    else:
        person_from_prefix = '3'
        gender_from_prefix = 'M'
        number_from_prefix = 'SG'

    # ── Voice detection ───────────────────────────────────────────────────────
    # Basic rule: DAMMA on imperfect prefix → PASSIVE (يُفْعَلُ).
    # Override for augmented forms (Form II, V, etc.): these also carry DAMMA
    # on the prefix in ACTIVE voice (يُفَعِّلُ, يُتَفَعَّلُ …).  Detect the
    # doubled-consonant that marks Form II/V:
    #   Original form (SHADDA): C + [KASRA + SHADDA] → ACTIVE
    #                           C + [FATHA + SHADDA] → PASSIVE
    #   Normalizer-expanded:    C[SUKUUN] + same-C[KASRA] → ACTIVE
    #                           C[SUKUUN] + same-C[FATHA] → PASSIVE
    voice = 'ACTIVE'
    if pairs and DAMMA in pairs[0][1]:
        voice = 'PASSIVE'   # default when prefix has damma
        # Scan for doubled-consonant to override for FORM_II/V active
        for k in range(1, len(pairs)):
            c_k, d_k = pairs[k]
            if SHADDA in d_k:
                # Original SHADDA form: vowel on same cell as SHADDA
                if KASRA in d_k:
                    voice = 'ACTIVE'
                elif FATHA in d_k:
                    voice = 'PASSIVE'
                break
            if SUKUUN in d_k and k + 1 < len(pairs):
                c_k1, d_k1 = pairs[k + 1]
                if c_k == c_k1 and c_k not in DIACRITICS:
                    # Normalizer-expanded geminate: vowel on second occurrence
                    if KASRA in d_k1:
                        voice = 'ACTIVE'
                    elif FATHA in d_k1:
                        voice = 'PASSIVE'
                    break

    # ── Suffix → number/gender/mood ───────────────────────────────────────────
    # Indicative suffixes with ن
    if bare.endswith('ون'):
        # يَفْعُلُونَ / تَفْعُلُونَ
        gender = 'M'
        number = 'PL'
        mood   = 'INDICATIVE'
        person = person_from_prefix
        # تَ prefix with ون → 2M_PL
        if first_char == TA:
            person = '2'
        return {'person': person, 'number': number, 'gender': gender, 'mood': mood, 'voice': voice}

    if bare.endswith('ين'):
        # تَفْعُلِينَ → 2F_SG indicative
        return {'person': '2', 'number': 'SG', 'gender': 'F', 'mood': 'INDICATIVE', 'voice': voice}

    if bare.endswith('ان'):
        # يَفْعُلَانِ / تَفْعُلَانِ → DU indicative
        person = person_from_prefix
        gender = gender_from_prefix
        if first_char == TA:
            # Could be 3F_DU or 2M_DU/2F_DU
            # Without more context, default to 3F_DU when starts with ت after يَ/تَ
            gender = 'M'  # ambiguous; caller can refine
            person = '2'
        else:
            gender = 'M'
        return {'person': person, 'number': 'DU', 'gender': gender, 'mood': 'INDICATIVE', 'voice': voice}

    if bare.endswith('ن') and not bare.endswith('ون') and not bare.endswith('ين') and not bare.endswith('ان'):
        # يَفْعُلْنَ / تَفْعُلْنَ → F_PL (jussive/indicative)
        mood = 'INDICATIVE'   # نَ suffix appears in both indicative and jussive
        person = person_from_prefix
        if first_char == YAA:
            return {'person': '3', 'number': 'PL', 'gender': 'F', 'mood': mood, 'voice': voice}
        elif first_char == TA:
            return {'person': '2', 'number': 'PL', 'gender': 'F', 'mood': mood, 'voice': voice}
        return {'person': person, 'number': 'PL', 'gender': 'F', 'mood': mood, 'voice': voice}

    # Subjunctive/Jussive suffixes (long vowel dropped)
    if bare.endswith('وا') and not bare.endswith('هوا'):
        # يَفْعُلُوا → 3M_PL or 2M_PL subjunctive/jussive
        person = person_from_prefix
        if first_char == TA:
            person = '2'
        mood = _detect_mood_from_stem_ending(surface, bare)
        return {'person': person, 'number': 'PL', 'gender': 'M', 'mood': mood, 'voice': voice}

    if bare.endswith('و') and len(bare) >= 5 and not bare.endswith('هو'):
        # Plural waw with alif dropped before an object-pronoun enclitic:
        # يَكْتُبُوهُ → host=يَكْتُبُو (bare='يكتبو').
        # Guard len>=5 to exclude 4-char hollow imperfect SG (يَدعُو, bare='يدعو').
        person = person_from_prefix
        if first_char == TA:
            person = '2'
        mood = _detect_mood_from_stem_ending(surface, bare)
        return {'person': person, 'number': 'PL', 'gender': 'M', 'mood': mood, 'voice': voice}

    if bare.endswith('ي') and first_char == TA and not bare.endswith('اي'):
        # تَفْعُلِي → 2F_SG subjunctive/jussive
        return {'person': '2', 'number': 'SG', 'gender': 'F', 'mood': 'SUBJUNCTIVE', 'voice': voice}

    if (bare.endswith('ا')
            and not bare.endswith('نا')
            and not bare.endswith('تا')
            and not bare.endswith('وا')
            and not bare.endswith('ها')):    # exclude pronoun هَا attached to verb
        # يَفْعُلَا / تَفْعُلَا → DU subjunctive
        person = person_from_prefix
        if first_char == TA:
            person = '2'
        return {'person': person, 'number': 'DU', 'gender': 'M', 'mood': 'SUBJUNCTIVE', 'voice': voice}

    # ── No suffix → detect mood from stem-final vowel (C3 diacritic) ─────────
    mood = _detect_mood_from_stem_ending(surface, bare)

    return {
        'person': person_from_prefix,
        'number': number_from_prefix,
        'gender': gender_from_prefix,
        'mood': mood,
        'voice': voice,
    }


# Common attached pronoun suffixes (bare, without diacritics) — these follow
# the verb stem. Strip them before mood detection so we reach the stem's final C.
_ATTACHED_PRONOUN_BARE = frozenset([
    'هم', 'هن', 'ها', 'هو', 'هي', 'ه',
    'كم', 'كن', 'ك',
    'نا', 'ني', 'ي',
    'هما', 'كما',
])


def _strip_pronoun_for_mood(surface: str) -> str:
    """
    Return surface with a trailing attached pronoun removed (if detectable),
    so mood can be detected from the verb stem's final consonant.
    Returns the unmodified surface if no pronoun suffix is found.
    """
    bare = strip_diacritics(surface)
    # Try longest match first
    for pron in sorted(_ATTACHED_PRONOUN_BARE, key=len, reverse=True):
        if bare.endswith(pron) and len(bare) > len(pron) + 2:
            # Strip suffix chars from end of surface (including diacritics)
            # Count how many base chars to strip
            chars_to_strip = len(pron)
            result_chars = []
            stripped = 0
            for ch in reversed(surface):
                if ch not in DIACRITICS:
                    if stripped < chars_to_strip:
                        stripped += 1
                        continue
                    else:
                        result_chars.insert(0, ch)
                else:
                    if stripped < chars_to_strip:
                        continue  # skip diacritics of stripped consonants
                    else:
                        result_chars.insert(0, ch)
            return ''.join(result_chars)
    return surface


def _detect_mood_from_stem_ending(surface: str, bare: str) -> str:
    """
    Detect mood from the last diacritic on the stem's final consonant.
    Indicative → ُ, Subjunctive → َ, Jussive → ْ or absent.

    Strips attached pronouns first so we see the verb stem's actual ending.
    """
    # Strip pronoun before examining mood
    stem_surface = _strip_pronoun_for_mood(surface)
    pairs = _chars_and_diacs(stem_surface)
    if not pairs:
        return 'INDICATIVE'

    # Work backwards to find the last significant diacritic on a consonant
    for base_char, diacs in reversed(pairs):
        if base_char in DIACRITICS:
            continue
        if DAMMA in diacs:
            return 'INDICATIVE'
        if FATHA in diacs:
            return 'SUBJUNCTIVE'
        if SUKUUN in diacs:
            return 'JUSSIVE'

    return 'INDICATIVE'   # default


# ──────────────────────────────────────────────────────────────────────────────
# Imperative feature extraction
# ──────────────────────────────────────────────────────────────────────────────

def extract_imperative_features(surface: str) -> dict:
    """Extract features from an imperative verb surface."""
    bare = _bare(surface)

    # Imperative default: 2nd person.
    # mood=NOT_APPLICABLE: the imperative is a mood in itself; there is no
    # indicative/subjunctive/jussive distinction on the mood axis for imperatives.
    features = {
        'person': '2',
        'number': 'SG',
        'gender': 'M',
        'mood': 'NOT_APPLICABLE',
        'voice': 'ACTIVE',
    }

    if bare.endswith('وا'):
        features['number'] = 'PL'
    elif bare.endswith('و') and len(bare) >= 5:
        # Plural waw with alif dropped before an object-pronoun enclitic:
        # اكْتُبُوهُ → host=اكْتُبُو (bare='اكتبو').
        # Guard len>=5 to exclude short forms.
        features['number'] = 'PL'
    elif bare.endswith('ي'):
        features['gender'] = 'F'
    elif bare.endswith('ا'):
        features['number'] = 'DU'
    elif bare.endswith('ن'):
        features['number'] = 'PL'
        features['gender'] = 'F'

    return features


# ──────────────────────────────────────────────────────────────────────────────
# Top-level dispatcher
# ──────────────────────────────────────────────────────────────────────────────

def extract_all_features(surface: str) -> dict:
    """
    Extract all inflectional features from a verbal surface.

    Handles multi-word inputs where a governing particle precedes the verb:
      - Jussive particles (لَا, لَمْ, إِنْ, وَلَا, فَلَا …) → JUSSIVE mood on IMPERFECT
      - Subjunctive particles (أَنْ, لَنْ, كَيْ, حَتَّى, أَلَّا …) → SUBJUNCTIVE mood

    Also handles:
      - Conjunction prefix (وَ/فَ) stripping before feature extraction
      - Lam al-amr (وَلْ/فَلْ prefix) → IMPERFECT + JUSSIVE mood

    Returns:
      tense_aspect, mood, voice, person, number, gender
    """
    # ── Multi-word: detect governing particle ────────────────────────────────
    parts = surface.split()
    if len(parts) >= 2:
        particle = parts[0]
        verb_part = ' '.join(parts[1:])
        # Particle governs mood of the following verb
        if particle in _JUSSIVE_PARTICLE_FORMS:
            feats = extract_all_features(verb_part)
            if feats.get('tense_aspect') == 'IMPERFECT':
                feats = dict(feats)
                feats['mood'] = 'JUSSIVE'
            return feats
        if particle in _SUBJUNCTIVE_PARTICLE_FORMS:
            feats = extract_all_features(verb_part)
            if feats.get('tense_aspect') == 'IMPERFECT':
                feats = dict(feats)
                feats['mood'] = 'SUBJUNCTIVE'
            return feats
        # No governing particle: analyse verb_part normally (fall through)
        return extract_all_features(verb_part)

    # ── Single-word: strip conjunction, check lam al-amr ────────────────────
    stripped_conj = _strip_conjunction_prefix(surface)
    stripped_lam, has_lam_amr = _strip_lam_amr(stripped_conj)

    tense = identify_tense(surface)

    if tense == 'IMPERFECT':
        # Use the bare-verb surface (after stripping conjunction) for feature extraction
        feats = extract_imperfect_features(stripped_conj)
        # Post-check: recover plural number when واو الجماعة is followed by an
        # object-pronoun enclitic (e.g. تَكْتُبُوهَا, تَكْتُبُوهُ).
        # extract_imperfect_features may return SG when bare ends in 'و' + pronoun.
        if feats.get('number') == 'SG':
            _imp_bare = strip_diacritics(stripped_conj)
            for _pron in sorted(_ATTACHED_PRONOUN_BARE, key=len, reverse=True):
                _trigger = 'و' + _pron
                if _imp_bare.endswith(_trigger) and len(_imp_bare) > len(_trigger) + 2:
                    feats = dict(feats)
                    feats['number'] = 'PL'
                    break
        mood = feats.get('mood', 'INDICATIVE')
        # Lam al-amr overrides mood to JUSSIVE regardless of suffix pattern
        if has_lam_amr:
            mood = 'JUSSIVE'
        return {
            'tense_aspect': 'IMPERFECT',
            'mood': mood,
            'voice': feats.get('voice', 'ACTIVE'),
            'person': feats.get('person'),
            'number': feats.get('number'),
            'gender': feats.get('gender'),
        }
    elif tense == 'IMPERATIVE':
        feats = extract_imperative_features(stripped_conj)
        # Post-check: recover plural number when واو الجماعة is followed by an
        # object-pronoun enclitic in the FULL surface (e.g. اكْتُبُوهُ → 'اكتبوه').
        # extract_imperative_features only sees the bare without diacritics; the
        # 'وا' → 'و' contraction before pronouns hides the plural marker.
        # Check: bare of stripped_conj ends in 'و' + known pronoun bare.
        _imp_bare = strip_diacritics(stripped_conj)
        if feats.get('number') == 'SG':
            for _pron in sorted(_ATTACHED_PRONOUN_BARE, key=len, reverse=True):
                _trigger = 'و' + _pron
                if _imp_bare.endswith(_trigger) and len(_imp_bare) > len(_trigger) + 2:
                    feats = dict(feats)
                    feats['number'] = 'PL'
                    break
        return {
            'tense_aspect': 'IMPERATIVE',
            # mood=NOT_APPLICABLE: the imperative is inherently a mood category;
            # indicative/subjunctive/jussive distinctions do not apply.
            'mood': 'NOT_APPLICABLE',
            'voice': 'ACTIVE',
            'person': feats.get('person'),
            'number': feats.get('number'),
            'gender': feats.get('gender'),
        }
    else:  # PAST or None
        feats = extract_past_features(surface)
        return {
            'tense_aspect': 'PAST',
            # Past tense has no indicative/subjunctive/jussive distinction.
            'mood': 'NOT_APPLICABLE',
            'voice': feats.get('voice', 'ACTIVE'),
            'person': feats.get('person'),
            'number': feats.get('number'),
            'gender': feats.get('gender'),
        }
