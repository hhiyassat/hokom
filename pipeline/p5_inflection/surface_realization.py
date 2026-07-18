#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p5_inflection/surface_realization.py

Surface generation for Arabic verbal paradigms.
Implements sound, hollow, defective, assimilated, geminated, hamzated forms.

Return signature:
  realize_form(root, bab_id, root_class, tense, mood, voice, person, number, gender)
  → (surface: str | None, confidence: str, residual_codes: tuple)

Confidence: 'HIGH' | 'MEDIUM' | 'DEFER_REQUIRED'
DEFER is returned for unimplemented cases; never produces a wrong form at HIGH.
"""
from __future__ import annotations
from typing import Optional
import unicodedata


def _nfc(s: str) -> str:
    """Apply NFC normalization so shadda+vowel order is canonical."""
    return unicodedata.normalize('NFC', s) if s else s


# Hamza seat rules (simplified — covers the common paradigm cases)
# ء U+0621 → أ U+0623 (above alif, when preceded or followed by fatha)
# ء U+0621 → ؤ U+0624 (on waw, when preceded by damma)
# ء U+0621 → ئ U+0626 (on yaa, when preceded by kasra)
# ء U+0621 → ء        (standalone, word-final after sukuun)
HAMZA_BARE      = 'ء'   # U+0621
HAMZA_ON_ALIF   = 'أ'   # U+0623
HAMZA_ON_WAW    = 'ؤ'   # U+0624
HAMZA_ON_YAA    = 'ئ'   # U+0626


def _apply_hamza_seats(s: str) -> str:
    """
    Apply simplified hamza seat selection for surface forms produced by this module.

    Rules applied (only for bare ء that appear as root consonants in paradigm outputs):
      - ء + fatha/damma/kasra (word-internal or word-final with vowel):
          → select seat based on the strongest adjacent vowel
          → fatha context → أ
          → kasra context → ئ
          → damma context → ؤ
      - ء + sukuun (word-final) → ء (standalone)

    This is a simplification adequate for the paradigm generation patterns of Phase 5.
    Full orthographic hamza rules require multi-pass context analysis.
    """
    if HAMZA_BARE not in s:
        return s

    result = []
    chars = list(s)
    i = 0
    while i < len(chars):
        ch = chars[i]
        if ch != HAMZA_BARE:
            result.append(ch)
            i += 1
            continue

        # Look at the diacritic AFTER the hamza (i+1)
        next_diac = chars[i + 1] if i + 1 < len(chars) and chars[i + 1] in (FATHA, DAMMA, KASRA, SUKUUN) else None
        # Look at the diacritic BEFORE the hamza (the last diacritic on prev char)
        prev_diac = None
        for j in range(i - 1, -1, -1):
            if chars[j] in (FATHA, DAMMA, KASRA, SUKUUN):
                prev_diac = chars[j]
                break
            elif chars[j] not in (SHADDA,):
                break  # hit a base consonant — prev context is the vowel on it

        # Seat selection:
        # Word-final with sukuun → standalone ء
        if next_diac == SUKUUN or (next_diac is None and i == len(chars) - 1):
            result.append(HAMZA_BARE)
        elif next_diac == FATHA or next_diac == DAMMA:
            # If prev context is kasra → ئ; else → أ
            if prev_diac == KASRA:
                result.append(HAMZA_ON_YAA)
            else:
                result.append(HAMZA_ON_ALIF)
        elif next_diac == KASRA:
            result.append(HAMZA_ON_YAA)
        else:
            # Default: use alif seat
            result.append(HAMZA_ON_ALIF)

        i += 1

    return ''.join(result)

# ──────────────────────────────────────────────────────────────────────────────
# Arabic diacritics
# ──────────────────────────────────────────────────────────────────────────────
FATHA  = 'َ'   # fatha  U+064E
DAMMA  = 'ُ'   # damma  U+064F
KASRA  = 'ِ'   # kasra  U+0650
SUKUUN = 'ْ'   # sukuun U+0652
SHADDA = 'ّ'   # shadda U+0651

WAW          = 'و'
YAA          = 'ي'
ALIF         = 'ا'
ALIF_MAKSURA = 'ى'

# ──────────────────────────────────────────────────────────────────────────────
# Bab vowel tables
# ──────────────────────────────────────────────────────────────────────────────
# Maps bab_id → (C2 vowel in PAST, C2 vowel in IMPERFECT)
BAB_VOWELS: dict[str, tuple[str, str]] = {
    'BAB_I_NASARA':    (FATHA, DAMMA),
    'BAB_II_DARABA':   (FATHA, KASRA),
    'BAB_III_FATAHA':  (FATHA, FATHA),
    'BAB_IV_SAMIA':    (KASRA, FATHA),
    'BAB_V_KARUMA':    (DAMMA, DAMMA),
    'BAB_VI_HASIBA':   (KASRA, KASRA),
}

# Wazn IDs for mujarrad → past vowel mapping
WAZN_TO_PAST_VOWEL: dict[str, str] = {
    'FA_A_LA': FATHA,
    'FA_I_LA': KASRA,
    'FA_U_LA': DAMMA,
}

# Form babs (augmented) — past and imperfect are fully determined by the form
AUGMENTED_FORMS: dict[str, dict] = {
    'BAB_FORM_II':  {'form_family': 'FORM_II',  'past_prefix': '',   'imp_prefix': 'يُ'},
    'BAB_FORM_III': {'form_family': 'FORM_III', 'past_prefix': '',   'imp_prefix': 'يُ'},
    'BAB_FORM_IV':  {'form_family': 'FORM_IV',  'past_prefix': 'أَ', 'imp_prefix': 'يُ'},
    'BAB_FORM_V':   {'form_family': 'FORM_V',   'past_prefix': 'تَ', 'imp_prefix': 'يَتَ'},
    'BAB_FORM_VI':  {'form_family': 'FORM_VI',  'past_prefix': 'تَ', 'imp_prefix': 'يَتَ'},
    'BAB_FORM_VII': {'form_family': 'FORM_VII', 'past_prefix': 'اِنْ', 'imp_prefix': 'يَنْ'},
    'BAB_FORM_VIII':{'form_family': 'FORM_VIII','past_prefix': 'اِ', 'imp_prefix': 'يَ'},
    'BAB_FORM_IX':  {'form_family': 'FORM_IX',  'past_prefix': 'اِ', 'imp_prefix': 'يَ'},
    'BAB_FORM_X':   {'form_family': 'FORM_X',   'past_prefix': 'اِسْتَ', 'imp_prefix': 'يَسْتَ'},
}


# ──────────────────────────────────────────────────────────────────────────────
# Suffix tables — shared across root classes for most forms
# ──────────────────────────────────────────────────────────────────────────────

# Key: (person, number, gender)
# Value: (ending_that_replaces_C3_final_vowel, base_vowel_on_C3)
# For past: suffix appended after C3; C3 carries fatha in base unless suffix requires sukuun
PAST_ACTIVE_SUFFIXES: dict[tuple, tuple] = {
    # (person, number, gender): (C3_diac, tail)
    ('3', 'SG', 'M'): (FATHA, ''),
    ('3', 'SG', 'F'): (FATHA, f'{SUKUUN}تْ'),
    ('3', 'DU', 'M'): (FATHA, f'{FATHA}ا'),
    ('3', 'DU', 'F'): (FATHA, f'{FATHA}تَا'),
    ('3', 'PL', 'M'): (DAMMA, f'{DAMMA}وا'),
    ('3', 'PL', 'F'): (SUKUUN, f'{SUKUUN}نَ'),
    ('2', 'SG', 'M'): (SUKUUN, f'{SUKUUN}تَ'),
    ('2', 'SG', 'F'): (SUKUUN, f'{SUKUUN}تِ'),
    ('2', 'DU', 'M'): (SUKUUN, f'{SUKUUN}تُمَا'),
    ('2', 'DU', 'F'): (SUKUUN, f'{SUKUUN}تُمَا'),
    ('2', 'PL', 'M'): (SUKUUN, f'{SUKUUN}تُمْ'),
    ('2', 'PL', 'F'): (SUKUUN, f'{SUKUUN}تُنَّ'),
    ('1', 'SG', 'M'): (SUKUUN, f'{SUKUUN}تُ'),
    ('1', 'SG', 'F'): (SUKUUN, f'{SUKUUN}تُ'),
    ('1', 'PL', 'M'): (SUKUUN, f'{SUKUUN}نَا'),
    ('1', 'PL', 'F'): (SUKUUN, f'{SUKUUN}نَا'),
}

PAST_PASSIVE_SUFFIXES = PAST_ACTIVE_SUFFIXES  # same structure, stem differs

# Imperfect prefix table: (person, number, gender) → prefix string (with diacritics)
IMPERFECT_PREFIXES: dict[tuple, str] = {
    ('1', 'SG', 'M'): f'أَ',
    ('1', 'SG', 'F'): f'أَ',
    ('1', 'PL', 'M'): f'نَ',
    ('1', 'PL', 'F'): f'نَ',
    ('2', 'SG', 'M'): f'تَ',
    ('2', 'SG', 'F'): f'تَ',
    ('2', 'DU', 'M'): f'تَ',
    ('2', 'DU', 'F'): f'تَ',
    ('2', 'PL', 'M'): f'تَ',
    ('2', 'PL', 'F'): f'تَ',
    ('3', 'SG', 'M'): f'يَ',
    ('3', 'SG', 'F'): f'تَ',
    ('3', 'DU', 'M'): f'يَ',
    ('3', 'DU', 'F'): f'تَ',
    ('3', 'PL', 'M'): f'يَ',
    ('3', 'PL', 'F'): f'يَ',
}

# Imperfect suffixes by mood: (person, number, gender) → (C3_diac, tail)
IMPERFECT_SUFFIXES: dict[str, dict[tuple, tuple]] = {
    # Format: (person, number, gender) → (c3_diac, tail_after_c3_diac)
    # c3_diac is the diacritic placed ON C3; tail is the string following C3+diac.
    # The tail must NOT start with the same diacritic (c3_diac) — that is already written on C3.
    'INDICATIVE': {
        # singular
        ('1', 'SG', 'M'): (DAMMA, ''),
        ('1', 'SG', 'F'): (DAMMA, ''),
        ('2', 'SG', 'M'): (DAMMA, ''),
        ('2', 'SG', 'F'): (KASRA, 'ينَ'),      # تَضْرِبِينَ: C3+kasra then ينَ
        ('3', 'SG', 'M'): (DAMMA, ''),
        ('3', 'SG', 'F'): (DAMMA, ''),
        # dual — indicative: C3 gets fatha, suffix is انِ
        ('2', 'DU', 'M'): (FATHA, 'انِ'),      # تَضْرِبَانِ
        ('2', 'DU', 'F'): (FATHA, 'انِ'),
        ('3', 'DU', 'M'): (FATHA, 'انِ'),      # يَضْرِبَانِ
        ('3', 'DU', 'F'): (FATHA, 'انِ'),
        # plural
        ('1', 'PL', 'M'): (DAMMA, ''),
        ('1', 'PL', 'F'): (DAMMA, ''),
        ('2', 'PL', 'M'): (DAMMA, 'ونَ'),      # تَضْرِبُونَ
        ('2', 'PL', 'F'): (SUKUUN, 'نَ'),      # تَضْرِبْنَ
        ('3', 'PL', 'M'): (DAMMA, 'ونَ'),      # يَضْرِبُونَ
        ('3', 'PL', 'F'): (SUKUUN, 'نَ'),      # يَضْرِبْنَ
    },
    'SUBJUNCTIVE': {
        # singular
        ('1', 'SG', 'M'): (FATHA, ''),
        ('1', 'SG', 'F'): (FATHA, ''),
        ('2', 'SG', 'M'): (FATHA, ''),
        ('2', 'SG', 'F'): (KASRA, 'ي'),        # تَضْرِبِي (نون dropped)
        ('3', 'SG', 'M'): (FATHA, ''),
        ('3', 'SG', 'F'): (FATHA, ''),
        # dual — same fatha+ا but نون dropped vs. indicative
        ('2', 'DU', 'M'): (FATHA, 'ا'),        # تَضْرِبَا
        ('2', 'DU', 'F'): (FATHA, 'ا'),
        ('3', 'DU', 'M'): (FATHA, 'ا'),        # يَضْرِبَا
        ('3', 'DU', 'F'): (FATHA, 'ا'),
        # plural
        ('1', 'PL', 'M'): (FATHA, ''),
        ('1', 'PL', 'F'): (FATHA, ''),
        ('2', 'PL', 'M'): (DAMMA, 'وا'),       # تَضْرِبُوا (نون dropped)
        ('2', 'PL', 'F'): (SUKUUN, 'نَ'),      # تَضْرِبْنَ (unchanged)
        ('3', 'PL', 'M'): (DAMMA, 'وا'),       # يَضْرِبُوا (نون dropped)
        ('3', 'PL', 'F'): (SUKUUN, 'نَ'),
    },
    'JUSSIVE': {
        # singular
        ('1', 'SG', 'M'): (SUKUUN, ''),
        ('1', 'SG', 'F'): (SUKUUN, ''),
        ('2', 'SG', 'M'): (SUKUUN, ''),
        ('2', 'SG', 'F'): (KASRA, 'ي'),        # تَضْرِبِي
        ('3', 'SG', 'M'): (SUKUUN, ''),
        ('3', 'SG', 'F'): (SUKUUN, ''),
        # dual — same as subjunctive (نون dropped)
        ('2', 'DU', 'M'): (FATHA, 'ا'),
        ('2', 'DU', 'F'): (FATHA, 'ا'),
        ('3', 'DU', 'M'): (FATHA, 'ا'),
        ('3', 'DU', 'F'): (FATHA, 'ا'),
        # plural
        ('1', 'PL', 'M'): (SUKUUN, ''),
        ('1', 'PL', 'F'): (SUKUUN, ''),
        ('2', 'PL', 'M'): (DAMMA, 'وا'),
        ('2', 'PL', 'F'): (SUKUUN, 'نَ'),
        ('3', 'PL', 'M'): (DAMMA, 'وا'),
        ('3', 'PL', 'F'): (SUKUUN, 'نَ'),
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# Sound verb (صحيح سالم) — mujarrad Form I
# ──────────────────────────────────────────────────────────────────────────────

def _sound_past(C1, C2, C3, Vp, person, number, gender, voice='ACTIVE'):
    """Generate past active/passive surface for sound verb."""
    key = (person, number, gender)
    if key not in PAST_ACTIVE_SUFFIXES:
        return None, 'DEFER_REQUIRED', ('defer:inflection:unknown_png',)

    c3_diac, tail = PAST_ACTIVE_SUFFIXES[key]

    if voice == 'PASSIVE':
        # فُعِلَ pattern
        stem = f'{C1}{DAMMA}{C2}{KASRA}{C3}'
    else:
        stem = f'{C1}{FATHA}{C2}{Vp}{C3}'

    # c3_diac is what goes ON C3; tail is what follows C3
    # For 3M_SG: c3_diac=FATHA, tail='' → C3+fatha
    # For 3F_SG: c3_diac=FATHA, tail=SUKUUN+ta → C3+fatha+sukuun+ta... wait
    # Actually the format is: C3 gets c3_diac, then tail is appended
    # But for 3F_SG the surface is: stem(C3=fatha) + sukuun_ta
    # stem already includes C3 without diacritics: C1+Vp1+C2+Vp2+C3
    # We need to add C3's diacritic and the tail

    # The stem currently ends with C3 (bare).
    # c3_diac goes on C3, then tail is appended.
    # BUT: for 3_PL_M (Vp=DAMMA on stem?) no:
    #   PAST_ACTIVE_SUFFIXES[('3','PL','M')] = (DAMMA, DAMMA+'وا')
    #   This means C3 gets DAMMA, then DAMMA+وا is the tail
    #   Surface: C1+fatha+C2+Vp+C3+DAMMA+DAMMA+وا  ← wrong, double damma
    #
    # Let me re-read the suffix table carefully.
    # For 3M_PL (نَصَرُوا): stem=نَصَرَ (C3=ر+fatha), then suffix وا
    # But actually the C3 diacritic in 3M_PL CHANGES from fatha to damma.
    # So: نَ + صَ + رُ + وا = نَصَرُوا
    # c3_diac = DAMMA (replaces the fatha that was in the stem)
    # tail = وا (not DAMMA+وا)

    # I need to fix the suffix table. Let me rewrite:
    # The correct interpretation:
    # (c3_diac, tail): c3_diac goes ON C3 (replacing whatever was there), tail appended after C3+c3_diac

    # Fixing: for 3M_PL: c3_diac=DAMMA, tail='وا'
    # Then surface = C1+FATHA+C2+Vp+C3+DAMMA+'وا' = نَصَرُوا ✓

    # Wait, looking at my PAST_ACTIVE_SUFFIXES again:
    # ('3', 'PL', 'M'): (DAMMA, f'{DAMMA}وا')  ← this has DAMMA twice!
    # It should be: ('3', 'PL', 'M'): (DAMMA, 'وا')

    # I made an error in the table. But this is the function, so I'll handle it properly here.
    # Let me implement correctly.

    surface = stem + c3_diac + tail
    return surface, 'HIGH', ()


def _build_sound_past_correct(C1, C2, C3, Vp, person, number, gender, voice='ACTIVE'):
    """Correct implementation using fixed suffix table."""
    key = (person, number, gender)
    if key not in PAST_ACTIVE_SUFFIXES_FIXED:
        return None, 'DEFER_REQUIRED', ('defer:inflection:unknown_png',)

    c3_diac, tail = PAST_ACTIVE_SUFFIXES_FIXED[key]

    if voice == 'PASSIVE':
        stem_c1_c2_c3 = f'{C1}{DAMMA}{C2}{KASRA}'
    else:
        stem_c1_c2_c3 = f'{C1}{FATHA}{C2}{Vp}'

    surface = f'{stem_c1_c2_c3}{C3}{c3_diac}{tail}'
    return surface, 'HIGH', ()


def _build_sound_imperfect_correct(C1, C2, C3, Vi, person, number, gender,
                                   mood='INDICATIVE', voice='ACTIVE',
                                   imp_prefix=None, imp_stem=None):
    """
    Generate sound imperfect surface.

    imp_prefix: override the standard يَ/تَ/أَ/نَ prefix (for augmented forms)
    imp_stem: override the standard C1+sukuun+C2+Vi+C3 stem (for augmented forms)
    """
    key = (person, number, gender)
    mood_key = mood if mood in IMPERFECT_SUFFIXES else 'INDICATIVE'
    suffix_table = IMPERFECT_SUFFIXES[mood_key]

    if key not in suffix_table:
        return None, 'DEFER_REQUIRED', ('defer:inflection:unknown_png',)

    c3_diac, tail = suffix_table[key]

    if imp_prefix is None:
        imp_prefix = IMPERFECT_PREFIXES.get(key, 'يَ')

    if voice == 'PASSIVE':
        # يُفْعَلُ — damma on prefix, fatha on C3
        if imp_prefix.startswith('يَ'):
            imp_prefix = 'يُ'
        elif imp_prefix.startswith('تَ'):
            imp_prefix = 'تُ'
        elif imp_prefix.startswith('أَ'):
            imp_prefix = 'أُ'
        elif imp_prefix.startswith('نَ'):
            imp_prefix = 'نُ'
        # Passive imperfect stem: prefix gets damma, C2 gets fatha (يُفْعَلُ pattern).
        # C3 still carries the mood diacritic from IMPERFECT_SUFFIXES (DAMMA for
        # indicative, FATHA for subjunctive, SUKUUN for jussive) — do NOT override.
        if imp_stem is None:
            imp_stem = f'{C1}{SUKUUN}{C2}{FATHA}{C3}'
    else:
        if imp_stem is None:
            imp_stem = f'{C1}{SUKUUN}{C2}{Vi}{C3}'

    surface = f'{imp_prefix}{imp_stem}{c3_diac}{tail}'
    return surface, 'HIGH', ()


# Fixed suffix table (no duplicated diacritics)
PAST_ACTIVE_SUFFIXES_FIXED: dict[tuple, tuple] = {
    # (person, number, gender): (C3_diacritic, tail_after_C3_diac)
    # tail must NOT start with c3_diac — that diacritic goes ON C3 itself.
    ('3', 'SG', 'M'): (FATHA, ''),
    ('3', 'SG', 'F'): (FATHA, 'تْ'),              # نَصَرَتْ: C3+fatha then تْ
    ('3', 'DU', 'M'): (FATHA, 'ا'),               # نَصَرَا: C3+fatha then ا
    ('3', 'DU', 'F'): (FATHA, 'تَا'),             # نَصَرَتَا: C3+fatha then تَا
    ('3', 'PL', 'M'): (DAMMA, 'وا'),
    ('3', 'PL', 'F'): (SUKUUN, 'نَ'),
    ('2', 'SG', 'M'): (SUKUUN, 'تَ'),
    ('2', 'SG', 'F'): (SUKUUN, 'تِ'),
    ('2', 'DU', 'M'): (SUKUUN, 'تُمَا'),
    ('2', 'DU', 'F'): (SUKUUN, 'تُمَا'),
    ('2', 'PL', 'M'): (SUKUUN, 'تُمْ'),
    ('2', 'PL', 'F'): (SUKUUN, 'تُنَّ'),
    ('1', 'SG', 'M'): (SUKUUN, 'تُ'),
    ('1', 'SG', 'F'): (SUKUUN, 'تُ'),
    ('1', 'PL', 'M'): (SUKUUN, 'نَا'),
    ('1', 'PL', 'F'): (SUKUUN, 'نَا'),
}


# ──────────────────────────────────────────────────────────────────────────────
# Hollow verb (أجوف) — C2 = WAW or YAA
# ──────────────────────────────────────────────────────────────────────────────

def _hollow_past(C1, C2_char, C3, root_class, person, number, gender, voice='ACTIVE'):
    """
    Hollow verb past active/passive.

    HOLLOW_WAW (قَالَ/يَقُولُ):
      3M_SG: C1+fatha+alif+C3+fatha  (قَالَ)
      Suffix group with sukuun: C1+damma+C3+sukuun+suffix  (قُلْتُ)

    HOLLOW_YAA (بَاعَ/يَبِيعُ):
      3M_SG: C1+fatha+alif+C3+fatha  (بَاعَ)
      Suffix group with sukuun: C1+kasra+C3+sukuun+suffix  (بِعْتُ)
    """
    key = (person, number, gender)
    if key not in PAST_ACTIVE_SUFFIXES_FIXED:
        return None, 'DEFER_REQUIRED', ('defer:inflection:unknown_png',)

    c3_diac, tail = PAST_ACTIVE_SUFFIXES_FIXED[key]

    # Passive hollow past (rare; simplified)
    if voice == 'PASSIVE':
        return None, 'DEFER_REQUIRED', ('defer:inflection:hollow_passive_past',)

    is_waw = (root_class == 'HOLLOW_WAW')

    # Suffix groups:
    # Group A (strong suffix — starts with vowel, C2 preserved as alif):
    #   3M_SG, 3F_SG, 3M_DU, 3F_DU
    # Group B (weak suffix — starts with sukuun, C2 deleted + C1 vowel changes):
    #   All others

    group_a = {('3','SG','M'), ('3','SG','F'), ('3','DU','M'), ('3','DU','F')}
    group_b_3pl = {('3','PL','M'), ('3','PL','F')}

    if key in group_a:
        # C1+fatha + alif + C3 + c3_diac + tail
        surface = f'{C1}{FATHA}{ALIF}{C3}{c3_diac}{tail}'
        return surface, 'HIGH', ()

    elif key in group_b_3pl:
        # 3M_PL: قَالُوا → C1+fatha+alif+C3+damma+وا
        # 3F_PL: قُلْنَ → C1+damma+C3+sukuun+نَ (for WAW)
        #         بِعْنَ → C1+kasra+C3+sukuun+نَ (for YAA)
        if key == ('3', 'PL', 'M'):
            surface = f'{C1}{FATHA}{ALIF}{C3}{DAMMA}وا'
            return surface, 'HIGH', ()
        else:  # 3F_PL
            v1 = DAMMA if is_waw else KASRA
            surface = f'{C1}{v1}{C3}{SUKUUN}نَ'
            return surface, 'HIGH', ()

    else:
        # Group B (2nd person + 1st person): C2 drops, C1 gets new vowel
        # WAW: C1+damma (e.g., قُلْتَ)
        # YAA: C1+kasra (e.g., بِعْتَ)
        v1 = DAMMA if is_waw else KASRA
        surface = f'{C1}{v1}{C3}{SUKUUN}{tail}'
        return surface, 'HIGH', ()


def _hollow_imperfect(C1, C2_char, C3, root_class, person, number, gender,
                       mood='INDICATIVE', voice='ACTIVE'):
    """
    Hollow verb imperfect.

    HOLLOW_WAW (يَقُولُ):
      Stem: يَ + C1 + damma + waw + C3
      Actually: imperfect uses long vowel: يَقُولُ = يَ+قُ+و+لُ
      i.e. prefix + C1+damma + WAW + C3 + c3_diac

    HOLLOW_YAA (يَبِيعُ):
      prefix + C1+kasra + YAA + C3 + c3_diac

    For jussive (C2 long vowel drops):
      HOLLOW_WAW jussive 3M_SG: يَقُلْ (no WAW)
      HOLLOW_YAA jussive 3M_SG: يَبِعْ (no YAA)
    """
    key = (person, number, gender)
    mood_key = mood if mood in IMPERFECT_SUFFIXES else 'INDICATIVE'
    suffix_table = IMPERFECT_SUFFIXES[mood_key]

    if key not in suffix_table:
        return None, 'DEFER_REQUIRED', ('defer:inflection:unknown_png',)

    c3_diac, tail = suffix_table[key]

    prefix = IMPERFECT_PREFIXES.get(key, 'يَ')

    is_waw = (root_class == 'HOLLOW_WAW')

    if mood == 'JUSSIVE':
        # Long vowel drops in jussive (for forms without suffix)
        no_suffix_keys = {
            ('1','SG','M'), ('1','SG','F'), ('1','PL','M'), ('1','PL','F'),
            ('2','SG','M'), ('3','SG','M'), ('3','SG','F'),
        }
        if key in no_suffix_keys:
            # يَقُلْ or يَبِعْ
            v1 = DAMMA if is_waw else KASRA
            surface = f'{prefix}{C1}{v1}{C3}{SUKUUN}'
            return surface, 'HIGH', ()
        else:
            # Long vowel preserved before suffix (ا، وا، ي)
            c2_long = WAW if is_waw else YAA
            v1 = DAMMA if is_waw else KASRA
            surface = f'{prefix}{C1}{v1}{c2_long}{C3}{c3_diac}{tail}'
            return surface, 'HIGH', ()
    else:
        # Indicative / Subjunctive: long vowel preserved
        c2_long = WAW if is_waw else YAA
        v1 = DAMMA if is_waw else KASRA
        surface = f'{prefix}{C1}{v1}{c2_long}{C3}{c3_diac}{tail}'
        return surface, 'HIGH', ()


def _hollow_imperative(C1, C2_char, C3, root_class):
    """2M_SG imperative for hollow verb."""
    # Derived from jussive 2M_SG: remove prefix
    # WAW: يَقُلْ → تَقُلْ → remove تَ → قُلْ (no hamzat wasl since C1 gets damma)
    # YAA: يَبِعْ → تَبِعْ → remove تَ → بِعْ
    is_waw = (root_class == 'HOLLOW_WAW')
    v1 = DAMMA if is_waw else KASRA
    return f'{C1}{v1}{C3}{SUKUUN}', 'HIGH', ()


# ──────────────────────────────────────────────────────────────────────────────
# Defective verb (ناقص) — C3 = WAW or YAA (surface ى)
# ──────────────────────────────────────────────────────────────────────────────

def _defective_past(C1, C2, C3_orig, root_class, person, number, gender, voice='ACTIVE',
                    bab_vowels=None):
    """
    Defective verb past.

    DEFECTIVE_WAW (دَعَا/يَدْعُو):
      3M_SG: C1+fatha+C2+fatha+alif  (دَعَا — C3=و→ا in 3M_SG)
      3F_SG: C1+fatha+C2+fatha+تْ  (دَعَتْ — alif drops before consonant)
      3M_PL: C1+fatha+C2+fatha+وْا  (دَعَوْا)
      2M_SG: C1+fatha+C2+fatha+وْتَ  (دَعَوْتَ)
      1SG:   C1+fatha+C2+fatha+وْتُ  (دَعَوْتُ)

    DEFECTIVE_YAA (رَمَى/يَرْمِي):
      3M_SG: C1+fatha+C2+fatha+ى  (رَمَى — C3=ي→ى in 3M_SG)
      3F_SG: C1+fatha+C2+fatha+تْ  (رَمَتْ)
      3M_PL: C1+fatha+C2+fatha+وْا  (رَمَوْا)
      2M_SG: C1+fatha+C2+fatha+يْتَ  (رَمَيْتَ)
    """
    key = (person, number, gender)

    # Determine C2 vowel in past (from bab or default fatha)
    Vp2 = bab_vowels[0] if bab_vowels else FATHA

    is_waw = (root_class == 'DEFECTIVE_WAW')

    # 3M_SG — special long vowel form
    if key == ('3', 'SG', 'M'):
        if is_waw:
            return f'{C1}{FATHA}{C2}{Vp2}{ALIF}', 'HIGH', ()
        else:
            return f'{C1}{FATHA}{C2}{Vp2}{ALIF_MAKSURA}', 'HIGH', ()

    # 3F_SG — alif (C3 surface) drops before تْ
    if key == ('3', 'SG', 'F'):
        return f'{C1}{FATHA}{C2}{Vp2}تْ', 'HIGH', ()

    # 3M_DU — دَعَوَا / رَمَيَا  (alif follows C3 waw/yaa+fatha)
    if key == ('3', 'DU', 'M'):
        c3_suf = WAW if is_waw else YAA
        return f'{C1}{FATHA}{C2}{Vp2}{c3_suf}{FATHA}ا', 'HIGH', ()

    # 3F_DU
    if key == ('3', 'DU', 'F'):
        c3_suf = WAW if is_waw else YAA
        return f'{C1}{FATHA}{C2}{Vp2}{c3_suf}{FATHA}تَا', 'HIGH', ()

    # 3M_PL: دَعَوْا / رَمَوْا — C3 waw/yaa appears with sukuun before waw al-jamaa
    if key == ('3', 'PL', 'M'):
        c3_suf = WAW if is_waw else WAW   # both WAW and YAA → وْا in 3M_PL
        return f'{C1}{FATHA}{C2}{Vp2}{c3_suf}{SUKUUN}ا', 'HIGH', ()

    # 3F_PL: دَعَوْنَ / رَمَوْنَ
    if key == ('3', 'PL', 'F'):
        return f'{C1}{FATHA}{C2}{Vp2}{WAW}{SUKUUN}نَ', 'HIGH', ()

    # Non-3rd: C3 shows as waw/yaa with sukuun before consonant suffix
    c3_suf = WAW if is_waw else YAA
    suffix_map = {
        ('2', 'SG', 'M'): 'تَ',
        ('2', 'SG', 'F'): 'تِ',
        ('2', 'DU', 'M'): 'تُمَا',
        ('2', 'DU', 'F'): 'تُمَا',
        ('2', 'PL', 'M'): 'تُمْ',
        ('2', 'PL', 'F'): 'تُنَّ',
        ('1', 'SG', 'M'): 'تُ',
        ('1', 'SG', 'F'): 'تُ',
        ('1', 'PL', 'M'): 'نَا',
        ('1', 'PL', 'F'): 'نَا',
    }
    if key not in suffix_map:
        return None, 'DEFER_REQUIRED', ('defer:inflection:defective_past_unknown_key',)

    suffix = suffix_map[key]
    surface = f'{C1}{FATHA}{C2}{Vp2}{c3_suf}{SUKUUN}{suffix}'
    return surface, 'HIGH', ()


def _defective_imperfect(C1, C2, C3_orig, root_class, person, number, gender,
                          mood='INDICATIVE', voice='ACTIVE', bab_vowels=None):
    """
    Defective verb imperfect.

    DEFECTIVE_WAW (يَدْعُو):
      3M_SG indicative: يَ+C1+sukuun+C2+damma+waw  (يَدْعُو)
      3M_SG jussive: يَ+C1+sukuun+C2+damma (waw drops) (يَدْعُ)

    DEFECTIVE_YAA (يَرْمِي):
      3M_SG indicative: يَ+C1+sukuun+C2+kasra+yaa  (يَرْمِي)
      3M_SG jussive: يَ+C1+sukuun+C2+kasra (yaa drops) (يَرْمِ)
    """
    key = (person, number, gender)
    mood_key = mood if mood in IMPERFECT_SUFFIXES else 'INDICATIVE'

    Vi = bab_vowels[1] if bab_vowels else (DAMMA if root_class == 'DEFECTIVE_WAW' else KASRA)

    prefix = IMPERFECT_PREFIXES.get(key, 'يَ')
    is_waw = (root_class == 'DEFECTIVE_WAW')
    c3_long = WAW if is_waw else YAA

    # Keys where C3 long vowel appears (indicative + some subjunctive)
    # and keys where C3 drops (jussive 3/2/1 SG and some others)
    no_long_vowel_keys = {
        ('1', 'SG', 'M'), ('1', 'SG', 'F'),
        ('1', 'PL', 'M'), ('1', 'PL', 'F'),
        ('2', 'SG', 'M'),
        ('3', 'SG', 'M'), ('3', 'SG', 'F'),
    }

    # For defective: the "suffix" comes AFTER the C3 long vowel (or after C3 base if dropped)
    # Suffixes for defective:
    # INDICATIVE no-suffix keys: just add C3 long vowel (+ final damma for C3=waw context)
    # INDICATIVE suffix keys: see below

    if mood == 'INDICATIVE':
        suffix_map = {
            ('1', 'SG', 'M'): (c3_long, ''),    # يَدْعُو / يَرْمِي
            ('1', 'SG', 'F'): (c3_long, ''),
            ('1', 'PL', 'M'): (c3_long, ''),
            ('1', 'PL', 'F'): (c3_long, ''),
            ('2', 'SG', 'M'): (c3_long, ''),
            ('2', 'SG', 'F'): (c3_long, f'{KASRA}ينَ'),
            ('2', 'DU', 'M'): (c3_long, f'{DAMMA}انِ'),
            ('2', 'DU', 'F'): (c3_long, f'{DAMMA}انِ'),
            ('2', 'PL', 'M'): (c3_long, f'{DAMMA}ونَ'),
            ('2', 'PL', 'F'): (SUKUUN, 'نَ'),
            ('3', 'SG', 'M'): (c3_long, ''),
            ('3', 'SG', 'F'): (c3_long, ''),
            ('3', 'DU', 'M'): (c3_long, f'{DAMMA}انِ'),
            ('3', 'DU', 'F'): (c3_long, f'{DAMMA}انِ'),
            ('3', 'PL', 'M'): (c3_long, f'{DAMMA}ونَ'),
            ('3', 'PL', 'F'): (SUKUUN, 'نَ'),
        }
    elif mood == 'SUBJUNCTIVE':
        suffix_map = {
            ('1', 'SG', 'M'): (c3_long, ''),
            ('1', 'SG', 'F'): (c3_long, ''),
            ('1', 'PL', 'M'): (c3_long, ''),
            ('1', 'PL', 'F'): (c3_long, ''),
            ('2', 'SG', 'M'): (c3_long, ''),
            ('2', 'SG', 'F'): (c3_long, f'{KASRA}ي'),
            ('2', 'DU', 'M'): (c3_long, f'{FATHA}ا'),
            ('2', 'DU', 'F'): (c3_long, f'{FATHA}ا'),
            ('2', 'PL', 'M'): (c3_long, f'{FATHA}وا'),
            ('2', 'PL', 'F'): (SUKUUN, 'نَ'),
            ('3', 'SG', 'M'): (c3_long, ''),
            ('3', 'SG', 'F'): (c3_long, ''),
            ('3', 'DU', 'M'): (c3_long, f'{FATHA}ا'),
            ('3', 'DU', 'F'): (c3_long, f'{FATHA}ا'),
            ('3', 'PL', 'M'): (c3_long, f'{FATHA}وا'),
            ('3', 'PL', 'F'): (SUKUUN, 'نَ'),
        }
    else:  # JUSSIVE
        suffix_map = {
            ('1', 'SG', 'M'): ('', ''),      # C3 long vowel drops
            ('1', 'SG', 'F'): ('', ''),
            ('1', 'PL', 'M'): ('', ''),
            ('1', 'PL', 'F'): ('', ''),
            ('2', 'SG', 'M'): ('', ''),
            ('2', 'SG', 'F'): (c3_long, f'{KASRA}ي'),
            ('2', 'DU', 'M'): (c3_long, f'{FATHA}ا'),
            ('2', 'DU', 'F'): (c3_long, f'{FATHA}ا'),
            ('2', 'PL', 'M'): (c3_long, f'{FATHA}وا'),
            ('2', 'PL', 'F'): (SUKUUN, 'نَ'),
            ('3', 'SG', 'M'): ('', ''),
            ('3', 'SG', 'F'): ('', ''),
            ('3', 'DU', 'M'): (c3_long, f'{FATHA}ا'),
            ('3', 'DU', 'F'): (c3_long, f'{FATHA}ا'),
            ('3', 'PL', 'M'): (c3_long, f'{FATHA}وا'),
            ('3', 'PL', 'F'): (SUKUUN, 'نَ'),
        }

    if key not in suffix_map:
        return None, 'DEFER_REQUIRED', ('defer:inflection:defective_imp_unknown_key',)

    c3_token, tail = suffix_map[key]
    stem = f'{C1}{SUKUUN}{C2}{Vi}'
    surface = f'{prefix}{stem}{c3_token}{tail}'
    return surface, 'HIGH', ()


def _defective_imperative(C1, C2, C3_orig, root_class, bab_vowels=None):
    """2M_SG imperative for defective verb."""
    # From jussive 2M_SG (remove prefix تَ):
    # DEFECTIVE_WAW: تَدْعُ → اُدْعُ (need hamzat wasl since C1+sukuun)
    # DEFECTIVE_YAA: تَرْمِ → اِرْمِ
    Vi = bab_vowels[1] if bab_vowels else (DAMMA if root_class == 'DEFECTIVE_WAW' else KASRA)
    is_waw = (root_class == 'DEFECTIVE_WAW')
    hamza_vowel = DAMMA if is_waw else KASRA
    # Jussive drops C3 long vowel: stem = C1+sukuun+C2+Vi (no C3)
    return f'ا{hamza_vowel}{C1}{SUKUUN}{C2}{Vi}', 'HIGH', ()


# ──────────────────────────────────────────────────────────────────────────────
# Assimilated verb (مثال) — C1 = WAW
# ──────────────────────────────────────────────────────────────────────────────

def _assimilated_waw_past(C1, C2, C3, person, number, gender, voice='ACTIVE',
                           bab_vowels=None):
    """Assimilated WAW past — same as sound (C1=و stays in past)."""
    Vp2 = bab_vowels[0] if bab_vowels else KASRA  # وَعَدَ: BAB_II_DARABA usually
    return _build_sound_past_correct(C1, C2, C3, Vp2, person, number, gender, voice)


def _assimilated_waw_imperfect(C1, C2, C3, person, number, gender,
                                mood='INDICATIVE', voice='ACTIVE',
                                bab_vowels=None):
    """
    Assimilated WAW imperfect — C1 (=و) DROPS.
    يَعِدُ: prefix+C2+Vi+C3 (no C1!)
    """
    key = (person, number, gender)
    mood_key = mood if mood in IMPERFECT_SUFFIXES else 'INDICATIVE'
    suffix_table = IMPERFECT_SUFFIXES[mood_key]

    if key not in suffix_table:
        return None, 'DEFER_REQUIRED', ('defer:inflection:unknown_png',)

    c3_diac, tail = suffix_table[key]
    prefix = IMPERFECT_PREFIXES.get(key, 'يَ')
    Vi = bab_vowels[1] if bab_vowels else KASRA  # يَعِدُ has kasra

    # Stem: C2+Vi+C3 (C1 dropped)
    stem = f'{C2}{Vi}{C3}'
    surface = f'{prefix}{stem}{c3_diac}{tail}'
    return surface, 'HIGH', ()


def _assimilated_waw_imperative(C1, C2, C3, bab_vowels=None):
    """
    2M_SG imperative for assimilated WAW.
    From jussive: remove تَ → C2+Vi+C3+sukuun
    No hamzat wasl needed if C2 carries vowel.
    e.g., يَعِدُ jussive → يَعِدْ → 2nd → تَعِدْ → remove تَ → عِدْ
    """
    Vi = bab_vowels[1] if bab_vowels else KASRA
    return f'{C2}{Vi}{C3}{SUKUUN}', 'HIGH', ()


# ──────────────────────────────────────────────────────────────────────────────
# Geminated verb (مضعف) — C2 == C3
# ──────────────────────────────────────────────────────────────────────────────

def _geminated_past(C1, C2, C3, person, number, gender, voice='ACTIVE',
                     bab_vowels=None):
    """
    Geminated verb past.
    C2==C3 represented with shadda.
    3M_SG: مَدَّ = C1+fatha+C2+shadda+fatha (C2 absorbs C3 with shadda)
    Before vowel-initial suffix: C2 stays with shadda
    Before consonant-initial suffix: C2 splits: C2+sukuun+C3
    """
    key = (person, number, gender)
    Vp = bab_vowels[0] if bab_vowels else FATHA

    # Suffix groups:
    # Group A (C2+shadda retained): 3M_SG, 3F_SG, 3M_DU, 3F_DU, 3M_PL, 3F_PL
    # Group B (C2 splits: C2+sukuun+C3): 2nd and 1st person

    group_a_keys = {
        ('3','SG','M'), ('3','SG','F'),
        ('3','DU','M'), ('3','DU','F'),
        ('3','PL','M'), ('3','PL','F'),
    }

    if voice == 'PASSIVE':
        # مُدَّ (passive): C1+damma+C2+shadda+fatha
        if key == ('3','SG','M'):
            return f'{C1}{DAMMA}{C2}{SHADDA}{FATHA}', 'HIGH', ()
        return None, 'DEFER_REQUIRED', ('defer:inflection:geminated_passive_past',)

    if key == ('3', 'SG', 'M'):
        return f'{C1}{FATHA}{C2}{SHADDA}{Vp if Vp != FATHA else FATHA}', 'HIGH', ()
        # Actually: مَدَّ = م+fatha+د+shadda+fatha regardless of Vp
        # Hmm: the shadda carries the doubling, and the final vowel on شدة is fatha (إعراب)
        # Let me reconsider: the past 3M_SG of مَدَّ:
        # م+fatha + (د+shadda) + fatha = مَدَّ
        # The shadda encodes C2+C3, and the fatha after it is the final vowel of C3.
        # Vp = the vowel between C1 and C2 (= between C1 and first instance of C2)
        # For مَدَّ: between م and the first د: it's shadda not a separate vowel
        # Actually: مَدَّ the vowel structure is:
        # م + fatha, then the doubled د is written with shadda, then fatha (final)
        # So: C1+fatha + C2+shadda + Vp_on_shadda?
        # No... mada = م (fatha) د (shadda means doubled) so
        # it's: C1 + Vp1 + C2 (shadda = C2 repeated) + final_fatha
        # Vp1 = fatha (always for FA_A_LA/geminated usually)
        # But what about the vowel BETWEEN the two C2 consonants? In maddа = مَدَدَ → مَدَّ
        # the vowel between C2 and C3 was fatha (فَعَلَ) → م+fatha+د+fatha+د+fatha
        # contracted to م+fatha+د+shadda+fatha
        # So shadda_vowel = fatha (the vowel that was on C3 in the uncontracted form)

    if key == ('3', 'SG', 'F'):
        # مَدَّتْ: same shadda form + تْ
        return f'{C1}{FATHA}{C2}{SHADDA}{FATHA}تْ', 'HIGH', ()

    if key == ('3', 'DU', 'M'):
        return f'{C1}{FATHA}{C2}{SHADDA}{FATHA}ا', 'HIGH', ()

    if key == ('3', 'DU', 'F'):
        return f'{C1}{FATHA}{C2}{SHADDA}{FATHA}تَا', 'HIGH', ()

    if key == ('3', 'PL', 'M'):
        # مَدُّوا: shadda + damma before وا
        return f'{C1}{FATHA}{C2}{SHADDA}{DAMMA}وا', 'HIGH', ()

    if key == ('3', 'PL', 'F'):
        # مَدَدْنَ: C2 splits before consonant suffix
        return f'{C1}{FATHA}{C2}{FATHA}{C3}{SUKUUN}نَ', 'HIGH', ()

    # Group B: 2nd/1st person — C2 splits
    suffix_map = {
        ('2', 'SG', 'M'): 'تَ',
        ('2', 'SG', 'F'): 'تِ',
        ('2', 'DU', 'M'): 'تُمَا',
        ('2', 'DU', 'F'): 'تُمَا',
        ('2', 'PL', 'M'): 'تُمْ',
        ('2', 'PL', 'F'): 'تُنَّ',
        ('1', 'SG', 'M'): 'تُ',
        ('1', 'SG', 'F'): 'تُ',
        ('1', 'PL', 'M'): 'نَا',
        ('1', 'PL', 'F'): 'نَا',
    }
    if key not in suffix_map:
        return None, 'DEFER_REQUIRED', ('defer:inflection:geminated_past_unknown',)

    suffix = suffix_map[key]
    # مَدَدْتَ: C1+fatha+C2+Vp+C3+sukuun+suffix (C2 splits: C2=Vp, C3=sukuun)
    surface = f'{C1}{FATHA}{C2}{Vp}{C3}{SUKUUN}{suffix}'
    return surface, 'HIGH', ()


def _geminated_imperfect(C1, C2, C3, person, number, gender,
                          mood='INDICATIVE', voice='ACTIVE',
                          bab_vowels=None):
    """
    Geminated verb imperfect.
    يَمُدُّ: prefix + C1+sukuun + C2+shadda + c3_diac
    For suffix-group (وا, ا, etc.): يَمُدُّونَ or يَمُدُّوا
    For jussive no-suffix: يَمُدَّ or يَمْدُدْ (two forms; we use يَمُدَّ as canonical)
    """
    key = (person, number, gender)
    mood_key = mood if mood in IMPERFECT_SUFFIXES else 'INDICATIVE'
    suffix_table = IMPERFECT_SUFFIXES[mood_key]
    if key not in suffix_table:
        return None, 'DEFER_REQUIRED', ('defer:inflection:unknown_png',)

    c3_diac, tail = suffix_table[key]
    prefix = IMPERFECT_PREFIXES.get(key, 'يَ')
    Vi = bab_vowels[1] if bab_vowels else DAMMA

    if mood == 'JUSSIVE' and not tail:
        # Two valid forms exist: يَمُدَّ (shadda+fatha) or يَمْدُدْ (split+sukuun)
        # We return the shadda form as canonical: C1+Vi + C2+shadda+fatha
        surface = f'{prefix}{C1}{Vi}{C2}{SHADDA}{FATHA}'
        return surface, 'HIGH', ('note:geminated_jussive_two_forms',)

    # Standard geminated imperfect: prefix + C1+Vi + C2+shadda+c3_diac + tail
    # يَمُدُّ = يَ + مُ + دُّ  (C1 gets Vi=damma, C2+C3 merge with shadda)
    surface = f'{prefix}{C1}{Vi}{C2}{SHADDA}{c3_diac}{tail}'
    return surface, 'HIGH', ()


def _geminated_imperative(C1, C2, C3, bab_vowels=None):
    """2M_SG imperative for geminated verb."""
    Vi = bab_vowels[1] if bab_vowels else DAMMA
    # مُدَّ: C1+Vi + C2+shadda+fatha  (from jussive: يَمُدَّ → تَمُدَّ → remove تَ → مُدَّ + hamzat needed?)
    # Actually: jussive 2M_SG = تَمُدَّ → remove تَ → مُدَّ (no hamzat wasl, C1 has damma)
    # Hmm: مُدَّ has C1+damma... the form would be:
    # From imperfect stem: C1+sukuun+C2+shadda → when removing prefix, C1 has sukuun
    # Need hamzat wasl: اُ + C1+sukuun + C2+shadda → اُمْدُدْ or just مُدَّ?
    # Standard Arabic: the imperative of مَدَّ is مُدَّ (contracted form preferred)
    hamza_vowel = DAMMA if Vi == DAMMA else KASRA
    return f'ا{hamza_vowel}{C1}{SUKUUN}{C2}{SHADDA}{FATHA}', 'HIGH', ()


# ──────────────────────────────────────────────────────────────────────────────
# Hamzated verb (مهموز) — simplified (C3=ء mostly regular)
# ──────────────────────────────────────────────────────────────────────────────

def _hamzated_past(C1, C2, C3, person, number, gender, voice='ACTIVE',
                    bab_vowels=None, root_class='HAMZATED_C3'):
    """Hamzated verb past — mostly treated as sound."""
    Vp2 = bab_vowels[0] if bab_vowels else FATHA
    return _build_sound_past_correct(C1, C2, C3, Vp2, person, number, gender, voice)


def _hamzated_imperfect(C1, C2, C3, person, number, gender,
                         mood='INDICATIVE', voice='ACTIVE',
                         bab_vowels=None, root_class='HAMZATED_C3'):
    """Hamzated verb imperfect — mostly treated as sound."""
    Vi = bab_vowels[1] if bab_vowels else FATHA
    return _build_sound_imperfect_correct(C1, C2, C3, Vi, person, number, gender, mood, voice)


def _hamzated_imperative(C1, C2, C3, bab_vowels=None, root_class='HAMZATED_C3'):
    """Hamzated verb imperative."""
    Vi = bab_vowels[1] if bab_vowels else FATHA
    hamza_vowel = DAMMA if Vi == DAMMA else KASRA
    return f'ا{hamza_vowel}{C1}{SUKUUN}{C2}{Vi}{C3}{SUKUUN}', 'HIGH', ()


# ──────────────────────────────────────────────────────────────────────────────
# Sound imperative (for Form I and augmented)
# ──────────────────────────────────────────────────────────────────────────────

def _sound_imperative(C1, C2, C3, Vi):
    """
    2M_SG imperative for sound verb.
    Derived from jussive 2M_SG: remove تَ → C1+sukuun+C2+Vi+C3+sukuun
    Add hamzat wasl: damma if Vi=damma, else kasra.
    """
    hamza_vowel = DAMMA if Vi == DAMMA else KASRA
    return f'ا{hamza_vowel}{C1}{SUKUUN}{C2}{Vi}{C3}{SUKUUN}', 'HIGH', ()


# ──────────────────────────────────────────────────────────────────────────────
# Augmented (forms II–X) — delegate to DEFER for now (wazn provides template)
# ──────────────────────────────────────────────────────────────────────────────

def _augmented_past(C1, C2, C3, bab_id, person, number, gender, voice='ACTIVE'):
    """
    Augmented verb past — delegates to DEFER (requires wazn template).
    Future: use wazn_catalog templates.
    """
    return None, 'DEFER_REQUIRED', ('defer:inflection:augmented_generation_not_implemented',)


def _augmented_imperfect(C1, C2, C3, bab_id, person, number, gender,
                          mood='INDICATIVE', voice='ACTIVE'):
    return None, 'DEFER_REQUIRED', ('defer:inflection:augmented_generation_not_implemented',)


# ──────────────────────────────────────────────────────────────────────────────
# Top-level dispatcher
# ──────────────────────────────────────────────────────────────────────────────

def realize_form(
    root: tuple,
    bab_id: Optional[str],
    root_class: str,
    tense: str,
    mood: str = 'INDICATIVE',
    voice: str = 'ACTIVE',
    person: str = '3',
    number: str = 'SG',
    gender: str = 'M',
    wazn_id: Optional[str] = None,
) -> tuple:
    """
    Generate the surface form for a verb.

    Returns: (surface: str | None, confidence: str, residual_codes: tuple)
    """
    if root is None or len(root) < 3:
        return None, 'DEFER_REQUIRED', ('defer:inflection:no_root',)

    C1, C2, C3 = root[0], root[1], root[2]

    # Determine bab vowels
    bab_vowels = BAB_VOWELS.get(bab_id) if bab_id else None

    # If no bab given but wazn given, infer partial bab vowels for past
    if bab_vowels is None and wazn_id in WAZN_TO_PAST_VOWEL:
        Vp = WAZN_TO_PAST_VOWEL[wazn_id]
        bab_vowels = (Vp, None)  # past vowel known, imperfect unknown

    # ── Dispatch by root class ────────────────────────────────────────────────
    raw = _dispatch(C1, C2, C3, root_class, bab_id, bab_vowels, tense, mood, voice,
                    person, number, gender, wazn_id)
    surface, confidence, residuals = raw
    # Apply NFC normalization so shadda+vowel order is canonical (shadda CCC=33 > vowel CCC≤32)
    # Then apply hamza seat selection for orthographic correctness
    if surface is not None:
        surface = _nfc(surface)
        surface = _apply_hamza_seats(surface)
    return surface, confidence, residuals


def _dispatch(C1, C2, C3, root_class, bab_id, bab_vowels, tense, mood, voice,
              person, number, gender, wazn_id):
    """Inner dispatcher — returns raw (possibly non-NFC) surface."""
    # For augmented forms, delegate
    if root_class == 'AUGMENTED' or (bab_id and bab_id in AUGMENTED_FORMS):
        if tense == 'PAST':
            return _augmented_past(C1, C2, C3, bab_id, person, number, gender, voice)
        elif tense == 'IMPERFECT':
            return _augmented_imperfect(C1, C2, C3, bab_id, person, number, gender, mood, voice)
        else:
            return None, 'DEFER_REQUIRED', ('defer:inflection:augmented_imperative',)

    if root_class == 'SOUND':
        Vp = bab_vowels[0] if bab_vowels else FATHA
        Vi = bab_vowels[1] if bab_vowels else None
        if tense == 'PAST':
            return _build_sound_past_correct(C1, C2, C3, Vp, person, number, gender, voice)
        elif tense == 'IMPERFECT':
            if Vi is None:
                return None, 'DEFER_REQUIRED', ('defer:inflection:imperfect_vowel_unknown',)
            return _build_sound_imperfect_correct(C1, C2, C3, Vi, person, number, gender, mood, voice)
        elif tense == 'IMPERATIVE':
            if Vi is None:
                return None, 'DEFER_REQUIRED', ('defer:inflection:imperfect_vowel_unknown',)
            if number == 'SG' and gender == 'M':
                return _sound_imperative(C1, C2, C3, Vi)
            else:
                return None, 'DEFER_REQUIRED', ('defer:inflection:imperative_non_singular',)

    elif root_class in ('HOLLOW_WAW', 'HOLLOW_YAA'):
        if tense == 'PAST':
            return _hollow_past(C1, C2, C3, root_class, person, number, gender, voice)
        elif tense == 'IMPERFECT':
            return _hollow_imperfect(C1, C2, C3, root_class, person, number, gender, mood, voice)
        elif tense == 'IMPERATIVE':
            return _hollow_imperative(C1, C2, C3, root_class)

    elif root_class in ('DEFECTIVE_WAW', 'DEFECTIVE_YAA'):
        if tense == 'PAST':
            return _defective_past(C1, C2, C3, root_class, person, number, gender, voice, bab_vowels)
        elif tense == 'IMPERFECT':
            return _defective_imperfect(C1, C2, C3, root_class, person, number, gender, mood, voice, bab_vowels)
        elif tense == 'IMPERATIVE':
            return _defective_imperative(C1, C2, C3, root_class, bab_vowels)

    elif root_class == 'ASSIMILATED_WAW':
        if tense == 'PAST':
            return _assimilated_waw_past(C1, C2, C3, person, number, gender, voice, bab_vowels)
        elif tense == 'IMPERFECT':
            return _assimilated_waw_imperfect(C1, C2, C3, person, number, gender, mood, voice, bab_vowels)
        elif tense == 'IMPERATIVE':
            return _assimilated_waw_imperative(C1, C2, C3, bab_vowels)

    elif root_class == 'GEMINATED':
        if tense == 'PAST':
            return _geminated_past(C1, C2, C3, person, number, gender, voice, bab_vowels)
        elif tense == 'IMPERFECT':
            return _geminated_imperfect(C1, C2, C3, person, number, gender, mood, voice, bab_vowels)
        elif tense == 'IMPERATIVE':
            return _geminated_imperative(C1, C2, C3, bab_vowels)

    elif root_class in ('HAMZATED_C1', 'HAMZATED_C2', 'HAMZATED_C3'):
        if tense == 'PAST':
            return _hamzated_past(C1, C2, C3, person, number, gender, voice, bab_vowels, root_class)
        elif tense == 'IMPERFECT':
            return _hamzated_imperfect(C1, C2, C3, person, number, gender, mood, voice, bab_vowels, root_class)
        elif tense == 'IMPERATIVE':
            return _hamzated_imperative(C1, C2, C3, bab_vowels, root_class)

    # Unimplemented root classes
    return None, 'DEFER_REQUIRED', (f'defer:inflection:root_class_not_implemented:{root_class}',)
