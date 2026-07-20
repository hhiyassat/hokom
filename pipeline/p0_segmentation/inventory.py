#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p0_segmentation/inventory.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Canonical inventory of Arabic clitics for the Hokom Clitic Segmenter.

Proclitic definitions: (fully_vocalized, bare, kind, priority)
Inventory is deterministic and exhaustive for supported forms.
No HR2S runtime dependency.

HOKOM-CLITIC-SEGMENTATION-OWNERSHIP-01
"""

# ── Protected lexical entries ────────────────────────────────────────────────
# These tokens must NOT be decomposed by the general segmentation algorithm.
PROTECTED_WHOLE_TOKENS = frozenset({
    # لفظ الجلالة — Hokom lexical protection
    'اللَّهُ', 'اللَّهِ', 'اللَّهَ', 'اللَّه',
    'الله', 'اللهِ', 'اللهَ',
    # demonstratives and pronouns that look like they have proclitics but don't
    'هَذَا', 'هَذِهِ', 'هَؤُلَاءِ', 'هَذَانِ', 'هَاتَانِ',
    'هُوَ', 'هِيَ', 'هُمَا', 'هُمْ', 'هُنَّ',
    'الَّذِي', 'الَّتِي', 'الَّذِينَ', 'اللَّوَاتِي', 'اللَّاتِي',
    'الَّذَانِ', 'اللَّذَانِ',
    # dual accusative/genitive of الَّذِي (HOKOM-CONSTITUTIONAL-AMENDMENT-02 wiring fix)
    'اللَّذَيْنِ', 'الَلَّذَيْنِ',
    'ذَلِكَ', 'ذَلِكُمْ', 'تِلْكَ', 'أُولَئِكَ',
    'إِذَا', 'أَيُّهَا', 'أَيَّتُهَا',
})

# Whole-token operators that are not decomposed (their base is not split)
# They may however take enclitics (e.g., مِنْهُ).
WHOLE_TOKEN_OPERATORS = frozenset({
    'مِنْ', 'عَنْ', 'إِلَى', 'عَلَى', 'فِي', 'مَعَ', 'حَتَّى',
    'بَيْنَ', 'فَوْقَ', 'تَحْتَ', 'قَبْلَ', 'بَعْدَ', 'عِنْدَ',
    'لَدَى', 'لَدُنْ', 'إِنَّ', 'أَنَّ', 'كَأَنَّ', 'لَكِنَّ',
    'لَيْتَ', 'لَعَلَّ', 'لَوْ', 'لَوْلَا',
    'مَا', 'لَا', 'إِنْ', 'لَمَّا', 'قَدْ', 'لَنْ', 'هَلْ',
    'بَلْ', 'أَمَّا', 'ثُمَّ', 'أَوْ', 'أَمْ',
    'كَمَا',
    # bare forms (no diacritics) for lookup
    'من', 'عن', 'إلى', 'على', 'في', 'مع', 'حتى',
    'بين', 'فوق', 'تحت', 'قبل', 'بعد', 'عند',
    'لدى', 'لدن', 'إن', 'لما', 'قد', 'لن', 'هل',
    'بل', 'أما', 'ثم', 'أو', 'أم',
    'إنَّ', 'أنَّ', 'كأنَّ', 'لكنَّ',
    'ليت', 'لعل', 'لو', 'لولا',
    'ما', 'لا',
    'كما',
})

# ── Proclitic inventory ───────────────────────────────────────────────────────
# Each entry: (fully_vocalized_form, bare_form, kind, priority)
# Priority: lower = higher priority (tried first).
# NOTE: standalone كَ is NOT included — only supported in multi-proclitic context.
# Standalone لِ is supported only when followed by definite article OR when
# the remainder has >= 3 Arabic consonants.
PROCLITICS = [
    # Conjunctions (وَ فَ) — most common, highest priority
    ('وَ', 'و', 'CONJUNCTION', 1),
    ('فَ', 'ف', 'CONJUNCTION', 2),
    # Jussive lam — appears AFTER conjunction, handled in multi-proclitic
    # NOT here as standalone (لْ alone is too ambiguous)
    # Prepositions
    ('بِ', 'ب', 'PREPOSITION', 3),
    ('لِ', 'ل', 'PREPOSITION', 4),
    # Future particle سَ
    ('سَ', 'س', 'FUTURE_PARTICLE', 5),
]

# Licensed multi-proclitic sequences (ordered, tried before single proclitics)
# These are definitive combinations that are always tried first.
LICENSED_MULTI_PROCLITIC_SEQUENCES = [
    # وَ + لْ (jussive): وَلْيَكْتُبْ — conjunction + jussive lam
    ('ول', ['و', 'ل'], ['CONJUNCTION', 'JUSSIVE_LAM']),
    # فَ + لْ (jussive): فَلْيَكْتُبْ — conjunction + jussive lam
    ('فل', ['ف', 'ل'], ['CONJUNCTION', 'JUSSIVE_LAM']),
    # فَ + بِ: فَبِ
    ('فب', ['ف', 'ب'], ['CONJUNCTION', 'PREPOSITION']),
    # وَ + بِ: وَبِ
    ('وب', ['و', 'ب'], ['CONJUNCTION', 'PREPOSITION']),
    # وَ + لِ: وَلِ
    ('ول', ['و', 'ل'], ['CONJUNCTION', 'PREPOSITION']),   # duplicate bare, resolved by kind
    # فَ + لِ: فَلِ
    ('فل', ['ف', 'ل'], ['CONJUNCTION', 'PREPOSITION']),
    # وَ + كَ: وَكَ (preposition of comparison after conjunction)
    ('وك', ['و', 'ك'], ['CONJUNCTION', 'PREPOSITION']),
    # فَ + كَ: فَكَ
    ('فك', ['ف', 'ك'], ['CONJUNCTION', 'PREPOSITION']),
    # وَ + سَ: وَسَ (future + conjunction)
    ('وس', ['و', 'س'], ['CONJUNCTION', 'FUTURE_PARTICLE']),
    # فَ + سَ: فَسَ
    ('فس', ['ف', 'س'], ['CONJUNCTION', 'FUTURE_PARTICLE']),
]

# ── Definite article ─────────────────────────────────────────────────────────
# Solar letters (الحروف الشمسية): ت ث د ذ ر ز س ش ص ض ط ظ ل ن
SOLAR_LETTERS = frozenset('تثدذرزسشصضطظلن')
DEFINITE_ARTICLE_BARE = 'ال'
DEFINITE_ARTICLE_FORMS = ['الْ', 'ال']

# ── Enclitic (attached pronoun) inventory ───────────────────────────────────
# Each entry: (bare_form, kind)
# Ordered by bare length DESCENDING to prevent short-match errors.
# Critical: does NOT include واو الجماعة, ألف الاثنين, نون النسوة.
ENCLITICS = [
    # Length 4 bare
    ('هنّ', 'ATTACHED_PRONOUN'),   # 3rd person feminine plural
    ('كنّ', 'ATTACHED_PRONOUN'),   # 2nd person feminine plural
    ('هما', 'ATTACHED_PRONOUN'),   # 3rd person dual
    ('كما', 'ATTACHED_PRONOUN'),   # 2nd person dual
    # Length 3 bare
    ('هم',  'ATTACHED_PRONOUN'),   # 3rd person masculine plural هُمْ
    ('كم',  'ATTACHED_PRONOUN'),   # 2nd person masculine plural كُمْ
    ('نا',  'ATTACHED_PRONOUN'),   # 1st person plural نَا
    ('ني',  'ATTACHED_PRONOUN'),   # 1st person singular نِي
    # Length 2 bare
    ('ها',  'ATTACHED_PRONOUN'),   # 3rd person feminine singular هَا
    ('يَ',  'ATTACHED_PRONOUN'),   # 1st person singular يَ (after long vowel)
    ('يِ',  'ATTACHED_PRONOUN'),   # variant
    # Length 1 bare — must be last to prevent over-eager matching
    ('ه',   'ATTACHED_PRONOUN'),   # 3rd person masculine singular هُ / هِ
    ('ك',   'ATTACHED_PRONOUN'),   # 2nd person singular كَ / كِ
    ('ي',   'ATTACHED_PRONOUN'),   # 1st person singular (post-long-vowel)
]

# ── Inflectional suffixes (NOT clitics — NEVER separated) ───────────────────
# These are verbal/nominal inflectional endings, not enclitics.
INFLECTIONAL_SUFFIXES_NOT_CLITICS = frozenset({
    'وا',    # واو الجماعة (past verbal)
    'ون',    # واو الجماعة (imperfect indicative)
    'ين',    # feminine plural / 2ps feminine
    'ان',    # ألف الاثنين (dual nominative)
    'ين',    # dual genitive/accusative / feminine plural
    'ن',     # نون النسوة
    'تم',    # 2nd person masculine plural past
    'تن',    # 2nd person feminine plural past
    'ت',     # 3rd person feminine past OR 2nd person past
})

# Bare forms of inflectional suffixes that must never be treated as enclitics
INFLECTIONAL_BARE_SUFFIXES = frozenset({
    'وا', 'ون', 'ين', 'ان', 'ن', 'تم', 'تن',
})

# ── Words where initial letter is root-initial, not proclitic ───────────────
# Used as additional guard against over-segmentation.
# The engine's primary guard is MIN_HOST_CONSONANTS, but this set is explicit.
NON_SEPARABLE_INITIALS = frozenset({
    # ك initial
    'كاتب', 'كبير', 'كتاب', 'كريم', 'كلام',
    'كثير', 'كافر', 'كافر', 'كفر', 'كفر',
    # ف initial
    'فعل', 'فتح', 'فقير', 'فسوق', 'فهم',
    # و initial
    'وعد', 'وجد', 'ولد', 'وزن', 'وقف', 'وقى',
    # ل initial
    'لبس', 'لعب', 'لقي', 'لها',
    # س initial
    'سأل', 'سمع', 'سبق', 'سلم',
    # ب initial
    'باب', 'بيت', 'بكى',
})

# Minimum number of Arabic CONSONANTS in a remaining host after proclitic split
# Set to 3 for CONJUNCTION proclitics (prevents وَعَدَ → وَ + عَدَ)
# Set to 2 for PREPOSITION (allows بِدَيْنٍ → بِ + دَيْنٍ where دين=3 consonants)
# Set to 3 for FUTURE_PARTICLE (prevents سَأَلَ → سَ + أَلَ; future only attaches
#   to imperfect verbs which always have mudara3a prefix + >=2 root letters = >=3 cons)
MIN_HOST_CONSONANTS_CONJUNCTION = 3
MIN_HOST_CONSONANTS_PREPOSITION = 2
MIN_HOST_CONSONANTS_FUTURE      = 3

# Absolute minimum Arabic letters (consonants + vowel carriers) for any host
MIN_HOST_LENGTH_CHARS = 2
