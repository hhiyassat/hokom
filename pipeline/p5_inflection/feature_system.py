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

    Detects all patterns:
      يَ / تَ / أَ / نَ  (active imperfect: prefix has fatha)
      يُ / تُ / أُ / نُ  (passive imperfect or augmented: prefix has damma)

    Classic detection: fatha on prefix + sukuun on C1.
    Extended detection: damma on prefix (augmented/passive) OR
                        fatha on prefix + any consonant (augmented forms lack sukuun on C1).

    The extended rule accepts any surface where the first char is a mudaric
    prefix letter (ي/ت/أ/ن) with fatha or damma, followed by at least 2 more
    consonants — this covers all Arabic imperfect patterns including Form II–X.
    """
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

    # ── Classic test: fatha on prefix + sukuun on next consonant ─────────────
    if has_fatha and len(pairs) >= 2:
        _, second_diacs = pairs[1]
        if SUKUUN in second_diacs:
            return first_char

    # ── Damma on prefix (passive/augmented) ──────────────────────────────────
    if has_damma and len(pairs) >= 3:
        # Passive/augmented: يُفَعِّلُ, يُنْصَرُ, etc.
        return first_char

    # ── Extended: fatha on prefix but no sukuun on C1 (augmented forms II–X) ─
    # Forms like Form II: يُفَعِّلُ have damma (covered above).
    # For active augmented imperfect with fatha on prefix: e.g. يَتَفَعَّلُ (Form V)
    # يَ + تَ + فَعَّلُ: pairs[0]=(ي,fatha), pairs[1]=(ت,fatha) — no sukuun on C1
    if has_fatha and len(pairs) >= 4:
        bare = strip_diacritics(s)
        # Exclude clear past-tense forms by their 3M_PL suffix (وا).
        # Past 3M_PL (e.g. نَصَرُوا) also starts with نَ and has 5 bare chars
        # but is NOT imperfect. Imperfect 3M_PL subj/juss starts with يَ/تَ, not نَ.
        if bare.endswith('وا'):
            return None  # past 3M_PL — not imperfect
        if len(bare) >= 5 and first_char in (YAA, TA, NUN):
            return first_char

    return None


def identify_tense(surface: str) -> Optional[str]:
    """
    Identify tense/aspect from surface.

    Returns one of: 'PAST' | 'IMPERFECT' | 'IMPERATIVE' | None.

    Strategy:
      - يَ/تَ/أَ/نَ + C+sukuun → IMPERFECT
      - اِ/اُ + C+sukuun (no imperfect prefix) → IMPERATIVE
      - Otherwise → PAST (default for verbal surfaces)
    """
    if not surface:
        return None

    pairs = _chars_and_diacs(surface)
    if not pairs:
        return None

    # ── Imperfect: prefix letter + fatha + stem-C1 + sukuun ─────────────────
    prefix = _has_imperfect_prefix(surface)
    if prefix is not None:
        return 'IMPERFECT'

    # ── Imperative: hamzat al-wasl (اِ or اُ) + consonant + sukuun ──────────
    first_char, first_diacs = pairs[0]
    if first_char in (ALIF, ALIF_WASL):
        if len(pairs) >= 3:
            _, second_diacs = pairs[1]
            if SUKUUN in second_diacs:
                return 'IMPERATIVE'

    # ── Default: PAST ─────────────────────────────────────────────────────────
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

    # ── Voice detection (passive imperfect: يُفْعَلُ — prefix has damma) ──────
    voice = 'ACTIVE'
    if pairs and DAMMA in pairs[0][1]:
        voice = 'PASSIVE'

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

    # Imperative default: 2nd person
    features = {
        'person': '2',
        'number': 'SG',
        'gender': 'M',
        'mood': 'IMPERATIVE',
        'voice': 'ACTIVE',
    }

    if bare.endswith('وا'):
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

    Returns:
      tense_aspect, mood, voice, person, number, gender
    """
    tense = identify_tense(surface)

    if tense == 'IMPERFECT':
        feats = extract_imperfect_features(surface)
        return {
            'tense_aspect': 'IMPERFECT',
            'mood': feats.get('mood', 'INDICATIVE'),
            'voice': feats.get('voice', 'ACTIVE'),
            'person': feats.get('person'),
            'number': feats.get('number'),
            'gender': feats.get('gender'),
        }
    elif tense == 'IMPERATIVE':
        feats = extract_imperative_features(surface)
        return {
            'tense_aspect': 'IMPERATIVE',
            'mood': 'IMPERATIVE',
            'voice': 'ACTIVE',
            'person': feats.get('person'),
            'number': feats.get('number'),
            'gender': feats.get('gender'),
        }
    else:  # PAST or None
        feats = extract_past_features(surface)
        return {
            'tense_aspect': 'PAST',
            'mood': None,
            'voice': feats.get('voice', 'ACTIVE'),
            'person': feats.get('person'),
            'number': feats.get('number'),
            'gender': feats.get('gender'),
        }
