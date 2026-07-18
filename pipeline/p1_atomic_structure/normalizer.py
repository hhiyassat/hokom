#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p1_atomic_structure/normalizer.py — مُطبِّع النص العربي
Canonical location (R-2 refactoring).
The root-level normalizer.py is now a shim that re-exports from here.

المهام:
  0. الهمزة      →  أ / إ / آ / ؤ / ئ  =  ء (همزة مستقلة) + حركتها
  1. ال التعريف  →  ا في بداية الكلمة + ل  =  ءَ + ل
  2. الشدة       →  ح(ّ+حركة)  =  ح(ْ) + ح(حركة)
"""

# ── ثوابت ─────────────────────────────────────────────────────────────────
HAMZA  = 'ء'   # ء
FATHA  = 'َ'   # َ
DAMMA  = 'ُ'   # ُ
KASRA  = 'ِ'   # ِ
SUKUN  = 'ْ'   # ْ
SHADDA = 'ّ'   # ّ

SHORT_VOWELS   = {FATHA, DAMMA, KASRA}
TANWIN         = {'ً', 'ٌ', 'ٍ'}
# DEPRECATED (Phase A): parallel diacritic set — will consolidate into
# glyph_classification.MarkClass as the single source of truth.
# Do not expand this set; use build_glyph_traces() in new code.
ALL_DIACRITICS = SHORT_VOWELS | TANWIN | {SUKUN, SHADDA, 'ٓ', 'ٔ', 'ٕ', 'ٰ'}

ARABIC_BASE = (
    set(chr(c) for c in range(0x0621, 0x063B)) |
    set(chr(c) for c in range(0x0641, 0x064B))
)


# ── 0. الهمزة ─────────────────────────────────────────────────────────────

# صور الهمزة المُركَّبة → ء (همزة مستقلة U+0621)
# أ  U+0623  همزة على ألف  →  ء
# إ  U+0625  همزة تحت ألف →  ء
# آ  U+0622  ألف ممدودة   →  ءَ + ا  (تُعالَج هنا أيضًا)
# ؤ  U+0624  همزة على واو →  ء  (الواو تُسقط، الهمزة تحتفظ بحركتها)
# ئ  U+0626  همزة على ياء →  ء  (الياء تُسقط)

HAMZA_FORMS = {
    'أ': HAMZA,           # أَ → ءَ  /  أُ → ءُ  /  أْ → ءْ
    'إ': HAMZA,           # إِ → ءِ
    'ؤ': HAMZA,           # ؤُ → ءُ
    'ئ': HAMZA,           # ئِ → ءِ
}
ALEF_MADDA = 'آ'          # آ → ءَا


def normalize_hamza(text: str) -> str:
    """
    وحِّد صور الهمزة:
      أ / إ / ؤ / ئ  →  ء  (تبقى حركاتها)
      آ (ألف ممدودة) →  ءَا
    """
    out = []
    i   = 0
    while i < len(text):
        ch = text[i]

        if ch == ALEF_MADDA:
            out.append(HAMZA + FATHA + 'ا')
            i += 1
            continue

        if ch in HAMZA_FORMS:
            # استبدل الشكل المركب بـ ء المستقلة مع الاحتفاظ بالحركات
            j = i + 1
            diacritics = []
            while j < len(text) and text[j] in ALL_DIACRITICS:
                diacritics.append(text[j])
                j += 1
            out.append(HAMZA_FORMS[ch] + ''.join(diacritics))
            i = j
            continue

        out.append(ch)
        i += 1

    return ''.join(out)


# ── 1. ال التعريف ──────────────────────────────────────────────────────────

def normalize_al(text: str) -> str:
    """
    ال التعريف = ءَل  (همزة مفتوحة + لام)
    كل كلمة تبدأ بـ ا + ل  →  ءَ + ل
    """
    words = text.split(' ')
    result = []
    for word in words:
        if (len(word) >= 2
                and word[0] == 'ا'
                and word[1] == 'ل'):
            word = HAMZA + FATHA + word[1:]
        result.append(word)
    return ' '.join(result)


# ── 2. الشدة ───────────────────────────────────────────────────────────────

def normalize_shadda(text: str) -> str:
    """
    الشدة: حرف(ّ + حركة)  →  حرف(ْ) + حرف(حركة)
    مثال: رِّ  →  رْرِ
    """
    out = []
    i   = 0
    while i < len(text):
        ch = text[i]

        if ch in ARABIC_BASE:
            # اجمع الحركات التالية
            j = i + 1
            diacritics = []
            while j < len(text) and text[j] in ALL_DIACRITICS:
                diacritics.append(text[j])
                j += 1

            if SHADDA in diacritics:
                rest = [d for d in diacritics if d != SHADDA]
                out.append(ch + SUKUN)          # نسخة ساكنة
                out.append(ch + ''.join(rest))  # نسخة متحركة
            else:
                out.append(ch + ''.join(diacritics))

            i = j
        else:
            out.append(ch)
            i += 1

    return ''.join(out)


# ── Pipeline ────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = normalize_hamza(text)   # 0. أ / إ / آ / ؤ / ئ → ء
    text = normalize_al(text)      # 1. ال التعريف
    text = normalize_shadda(text)  # 2. الشدة
    return text


# ── Phase B: normalize_tracked() — additive wrappers ─────────────────────────
#
# These functions produce the same output as their non-tracked counterparts
# while also returning a SpanAlignmentMap that maps raw codepoint positions
# to normalized codepoint positions.
#
# Existing callers are NOT affected: they continue using normalize() as before.
# New callers that need position tracking call normalize_tracked() instead.
#
# Governing rule: every normalized position must be projectable back to a raw
# position via SpanAlignmentMap.project_to_raw().

def normalize_hamza_tracked(text: str) -> 'tuple[str, SpanAlignmentMap]':
    """
    Hamza normalization with position tracking.

    Wraps normalize_hamza() — output is identical.
    Returns (normalized_str, SpanAlignmentMap) where the map projects between
    raw codepoint positions and hamza-normalized positions.

    Transform types produced:
        REPLACE  — أ/إ/ؤ/ئ cluster (base + diacritics) → ء + same diacritics
                   (length preserved; only base codepoint changes)
        EXPAND   — آ (1 char) → ءَا (3 chars)
        IDENTITY — all other characters, emitted ONE ENTRY PER CHAR

    IMPORTANT: Identity characters are emitted one entry per character (not
    merged into runs).  This fine granularity is required for correct position
    projection through SpanAlignmentMap.compose() when downstream maps (e.g.
    normalize_shadda_tracked) contain EXPAND entries within what would otherwise
    be a coarse identity block.  Merging would cause the composed map to lose
    sub-span precision.
    """
    from .span_map import SpanAlignmentMap, SpanEntry

    out: list[str] = []
    entries: list[SpanEntry] = []
    raw_pos  = 0
    norm_pos = 0

    i = 0
    while i < len(text):
        ch = text[i]

        if ch == ALEF_MADDA:
            norm_chunk = HAMZA + FATHA + 'ا'   # 3 chars
            out.append(norm_chunk)
            entries.append(SpanEntry(
                raw_pos, raw_pos + 1,
                norm_pos, norm_pos + 3,
                'EXPAND', 'آ→ءَا',
            ))
            raw_pos  += 1
            norm_pos += 3
            i += 1
            continue

        if ch in HAMZA_FORMS:
            j = i + 1
            diacritics: list[str] = []
            while j < len(text) and text[j] in ALL_DIACRITICS:
                diacritics.append(text[j])
                j += 1
            chunk_len  = j - i   # same in raw and norm (only base changes)
            norm_chunk = HAMZA_FORMS[ch] + ''.join(diacritics)
            out.append(norm_chunk)
            entries.append(SpanEntry(
                raw_pos, raw_pos + chunk_len,
                norm_pos, norm_pos + chunk_len,
                'REPLACE', f'{ch}→ء',
            ))
            raw_pos  += chunk_len
            norm_pos += chunk_len
            i = j
            continue

        # IDENTITY char — ONE ENTRY PER CHAR (not merged into runs)
        out.append(ch)
        entries.append(SpanEntry(
            raw_pos, raw_pos + 1,
            norm_pos, norm_pos + 1,
            'IDENTITY', '',
        ))
        raw_pos  += 1
        norm_pos += 1
        i += 1

    return ''.join(out), SpanAlignmentMap.from_entries(raw_pos, norm_pos, entries)


def normalize_al_tracked(text: str) -> 'tuple[str, SpanAlignmentMap]':
    """
    Definite-article normalization with position tracking.

    Wraps normalize_al() — output is identical.
    Returns (normalized_str, SpanAlignmentMap).

    Transform types produced:
        EXPAND  — word-initial ا (1 char) → ء + َ (2 chars) when followed by ل
        IDENTITY — all other characters (including ل and the rest of the word)
    """
    from .span_map import SpanAlignmentMap, SpanEntry

    out: list[str] = []
    entries: list[SpanEntry] = []
    raw_pos  = 0
    norm_pos = 0

    # Split on single spaces, mirroring normalize_al() exactly.
    # We reconstruct the original spacing by tracking word boundaries manually.
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            # Space: IDENTITY
            out.append(' ')
            entries.append(SpanEntry(
                raw_pos, raw_pos + 1,
                norm_pos, norm_pos + 1,
                'IDENTITY', '',
            ))
            raw_pos  += 1
            norm_pos += 1
            i += 1
        else:
            # Non-space word: find end
            j = i
            while j < n and text[j] != ' ':
                j += 1
            word = text[i:j]
            word_len = j - i

            if (word_len >= 2 and word[0] == 'ا' and word[1] == 'ل'):
                # ال التعريف: ا → ء + َ (EXPAND by 1)
                out.append(HAMZA + FATHA + word[1:])
                entries.append(SpanEntry(
                    raw_pos, raw_pos + 1,
                    norm_pos, norm_pos + 2,
                    'EXPAND', 'ا→ءَ (ال التعريف)',
                ))
                raw_pos  += 1
                norm_pos += 2
                # ل and the rest of the word: IDENTITY
                rest_len = word_len - 1
                if rest_len > 0:
                    entries.append(SpanEntry(
                        raw_pos, raw_pos + rest_len,
                        norm_pos, norm_pos + rest_len,
                        'IDENTITY', '',
                    ))
                    raw_pos  += rest_len
                    norm_pos += rest_len
            else:
                # Whole word IDENTITY
                out.append(word)
                entries.append(SpanEntry(
                    raw_pos, raw_pos + word_len,
                    norm_pos, norm_pos + word_len,
                    'IDENTITY', '',
                ))
                raw_pos  += word_len
                norm_pos += word_len

            i = j

    return ''.join(out), SpanAlignmentMap.from_entries(raw_pos, norm_pos, entries)


def normalize_shadda_tracked(text: str) -> 'tuple[str, SpanAlignmentMap]':
    """
    Shadda-expansion normalization with position tracking.

    Wraps normalize_shadda() — output is identical.
    Returns (normalized_str, SpanAlignmentMap).

    Transform types produced:
        EXPAND   — base+shadda[+vowel] cluster (n chars) → base+ْ+base[+vowel]
                   (n+1 chars: +1 per shadda site, always net +1)
        IDENTITY — all other base+diacritic clusters and non-Arabic-base chars
    """
    from .span_map import SpanAlignmentMap, SpanEntry

    out: list[str] = []
    entries: list[SpanEntry] = []
    raw_pos  = 0
    norm_pos = 0

    i = 0
    while i < len(text):
        ch = text[i]

        if ch in ARABIC_BASE:
            # Collect all diacritics following this base char
            j = i + 1
            diacritics: list[str] = []
            while j < len(text) and text[j] in ALL_DIACRITICS:
                diacritics.append(text[j])
                j += 1

            raw_chunk_len = j - i  # base + n diacritics

            if SHADDA in diacritics:
                rest = [d for d in diacritics if d != SHADDA]
                norm_chunk     = ch + SUKUN + ch + ''.join(rest)
                norm_chunk_len = raw_chunk_len + 1   # net +1 per shadda
                out.append(norm_chunk)
                entries.append(SpanEntry(
                    raw_pos, raw_pos + raw_chunk_len,
                    norm_pos, norm_pos + norm_chunk_len,
                    'EXPAND', f'shadda: {ch}+ّ→{ch}+ْ+{ch}',
                ))
                raw_pos  += raw_chunk_len
                norm_pos += norm_chunk_len
            else:
                out.append(ch + ''.join(diacritics))
                entries.append(SpanEntry(
                    raw_pos, raw_pos + raw_chunk_len,
                    norm_pos, norm_pos + raw_chunk_len,
                    'IDENTITY', '',
                ))
                raw_pos  += raw_chunk_len
                norm_pos += raw_chunk_len

            i = j
        else:
            # Non-Arabic-base char: IDENTITY (space, punct, or orphaned diacritic)
            out.append(ch)
            entries.append(SpanEntry(
                raw_pos, raw_pos + 1,
                norm_pos, norm_pos + 1,
                'IDENTITY', '',
            ))
            raw_pos  += 1
            norm_pos += 1
            i += 1

    return ''.join(out), SpanAlignmentMap.from_entries(raw_pos, norm_pos, entries)


def normalize_tracked(text: str) -> 'tuple[str, SpanAlignmentMap]':
    """
    Full normalize() pipeline with position tracking.

    Applies normalize_hamza → normalize_al → normalize_shadda and composes
    the three SpanAlignmentMaps into a single raw→final map.

    Returns:
        (normalized_str, SpanAlignmentMap)
        where normalized_str == normalize(text)
        and SpanAlignmentMap.project_to_raw(norm_start, norm_end) returns
        the corresponding span in the original raw text.

    Existing callers that use normalize() are NOT affected.
    """
    h_str, h_map  = normalize_hamza_tracked(text)
    a_str, a_map  = normalize_al_tracked(h_str)
    f_str, f_map  = normalize_shadda_tracked(a_str)
    composed       = h_map.compose(a_map).compose(f_map)
    return f_str, composed


# Type hint forward reference used in the tracked functions above.
# SpanAlignmentMap is imported lazily inside each function to avoid
# adding a mandatory module-level import to normalizer.py.
try:
    from .span_map import SpanAlignmentMap as _SpanAlignmentMap  # noqa: F401
except ImportError:
    pass


# ── تشغيل ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    tests = [
        'الْمُلُوكِ',
        'مُدَرِّسٌ',
        'الْكِتَابُ',
        'بِالْقَلَمِ',
    ]
    for t in tests:
        n = normalize(t)
        changed = '← تغيَّر' if n != t else '← لم يتغير'
        print(f'  {t:20}  →  {n:25} {changed}')
