#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p1_atomic_structure/tokenizer.py — مُجزِّئ النص العربي إلى كلمات
Canonical location (R-3 refactoring).
The root-level tokenizer.py is now a shim that re-exports from here.

المهام:
  1. تقسيم النص إلى كلمات (split on whitespace)
  2. تنظيف علامات الترقيم من أطراف الكلمة
  3. فصل الكلمة الصرفية عن الوحدات المتصلة (clitics)
     وَ / فَ / بِ / لِ / كَ  في بداية الكلمة
     ـهُ / ـهَا / ـهُمْ ...  في نهاية الكلمة  (مرحلة لاحقة)

المخرج: قائمة من Token(surface, kind)

قاعدة الأسبقية:
  قبل أي فصل clitic، يُتحقق من أن الجذع العاري (بلا تشكيل) للكلمة
  ليس موجودًا في كتالوج المبنيات. إن كان موجودًا، تُحفَظ الكلمة كوحدة واحدة.
  هذا يضمن أن العوامل المركبة كـ كَيْ وكَأَنَّ وكَمْ لا تُفصَل.

  التسلسل:
    1. جذع الكلمة في الكتالوج؟ → لا فصل (محمية معجميًا)
    2. الكلمة تبدأ بـ clitic مشكول؟ → فصل
    3. وإلا → token مفرد
"""

from __future__ import annotations
from dataclasses import dataclass
from typing      import TYPE_CHECKING

# ── علامات الترقيم ──────────────────────────────────────────────────────────
PUNCT = set('.,،؛:؟!()[]«»""\'\'…-–—\n\t')

# ── حروف التشكيل (لاستخدامها في بناء الجذع العاري) ──────────────────────────
# DEPRECATED (Phase A): parallel diacritic set — will consolidate into
# glyph_classification.MarkClass as the single source of truth.
# Do not expand this set; use build_glyph_traces() in new code.
_DIACRITICS: frozenset[str] = frozenset('ًٌٍَُِّْٰ')

# ── حروف الجر والعطف المتصلة (clitic prefixes) ──────────────────────────────
# يجب أن تحمل حركة كاملة في النص المشكول
CLITIC_PREFIXES: dict[str, str] = {
    'وَ':  'عطف',
    'بِ':  'جر',
    'لِ':  'جر/تعليل',
    'كَ':  'تشبيه',
}

# ── جذور البادئات العارية (بلا تشكيل) ──────────────────────────────────────
_CLITIC_BARE: frozenset[str] = frozenset(
    ''.join(c for c in p if c not in _DIACRITICS)
    for p in CLITIC_PREFIXES
)  # {'و', 'ب', 'ل', 'ك'}


# ── ذاكرة التخزين المؤقت للجذور المحمية ────────────────────────────────────
# يُبنى من الكتالوج عند أول استدعاء لـ split_clitic()
_PROTECTED_BARE_CACHE: 'frozenset[str] | None' = None


def _strip_diacritics(s: str) -> str:
    """أزِل جميع حروف التشكيل العربية."""
    return ''.join(c for c in s if c not in _DIACRITICS)


def _build_protected_bare() -> frozenset[str]:
    """
    ابنِ مجموعة الجذور العارية المحمية من الكتالوج.

    الشرط: الجذع العاري للمدخل يبدأ بجذع عارٍ لإحدى بادئات الـ clitic
           (ك، ب، ل، و) وله طول أكبر من البادئة.

    مثال:
      كَيْ    → جذع = كي  → يبدأ بـ ك → محمي
      كَأَنَّ → جذع = كأن → يبدأ بـ ك → محمي
      كَمْ    → جذع = كم  → يبدأ بـ ك → محمي
      بِئْسَ  → جذع = بئس → يبدأ بـ ب → محمي
      كَانَ   → جذع = كان → يبدأ بـ ك → محمي
    """
    from mabni_inventory import get_inventory
    inv       = get_inventory()
    protected = set()
    for entry in inv._entries:
        bare = _strip_diacritics(entry.surface_vocalized)
        if any(bare.startswith(cp) and len(bare) > len(cp)
               for cp in _CLITIC_BARE):
            protected.add(bare)
    return frozenset(protected)


def _get_protected_bare() -> frozenset[str]:
    """أعِد الجذور المحمية (مع تخزين مؤقت)."""
    global _PROTECTED_BARE_CACHE
    if _PROTECTED_BARE_CACHE is None:
        _PROTECTED_BARE_CACHE = _build_protected_bare()
    return _PROTECTED_BARE_CACHE


# ── هيكل الـ Token ───────────────────────────────────────────────────────────
@dataclass
class Token:
    surface:  str          # النص الظاهر
    kind:     str          # 'word' | 'clitic' | 'punct'
    original: str = ''     # الكلمة الأصلية قبل الفصل

    def __str__(self):
        return self.surface


# ── خطوات التوكِنَة ──────────────────────────────────────────────────────────

def strip_punct(word: str) -> tuple[str, str, str]:
    """أزِل علامات الترقيم من اليمين واليسار. أعِد (يسار، الكلمة، يمين)."""
    left, right = [], []
    i = 0
    while i < len(word) and word[i] in PUNCT:
        left.append(word[i]); i += 1
    j = len(word) - 1
    while j >= i and word[j] in PUNCT:
        right.insert(0, word[j]); j -= 1
    return ''.join(left), word[i:j+1], ''.join(right)


def split_clitic(word: str) -> list[Token]:
    """
    افصل الـ clitic المتصل في بداية الكلمة إن وُجد.
    مثال: وَالْكِتَابُ  →  [Token('وَ','clitic'), Token('الْكِتَابُ','word')]

    قاعدة الأسبقية:
      1. إذا كان الجذع العاري للكلمة في مجموعة الجذور المحمية من الكتالوج
         → لا فصل (كلمة مستقلة معجميًا).
         مثال: كَيْ → جذع = كي ∈ محمي → Token('كَيْ','word')
               كَأَنَّ → جذع = كأن ∈ محمي → Token('كَأَنَّ','word')
               كَمْ → جذع = كم ∈ محمي → Token('كَمْ','word')
      2. الكلمة تبدأ بـ clitic مشكول → فصل.
      3. وإلا → token مفرد.
    """
    # ── 1. تحقق من الحماية المعجمية (مشتق من الكتالوج) ──────────────────────
    bare_word = _strip_diacritics(word)
    if bare_word in _get_protected_bare():
        return [Token(surface=word, kind='word', original=word)]

    # ── 2. فصل clitic إن وُجد ────────────────────────────────────────────────
    for prefix, kind in CLITIC_PREFIXES.items():
        if word.startswith(prefix) and len(word) > len(prefix):
            rest = word[len(prefix):]
            return [
                Token(surface=prefix, kind='clitic', original=word),
                Token(surface=rest,   kind='word',   original=word),
            ]

    return [Token(surface=word, kind='word', original=word)]


def tokenize(text: str) -> list[Token]:
    """حوِّل النص إلى قائمة Tokens."""
    tokens: list[Token] = []

    for raw in text.split():
        left, word, right = strip_punct(raw)

        if left:
            tokens.append(Token(surface=left, kind='punct'))

        if word:
            tokens.extend(split_clitic(word))

        if right:
            tokens.append(Token(surface=right, kind='punct'))

    return tokens


def words_only(tokens: list[Token]) -> list[Token]:
    """أعِد الكلمات فقط (بدون ترقيم وبدون clitics مستقلة)."""
    return [t for t in tokens if t.kind in ('word', 'clitic')]


# ── تشغيل ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    tests = [
        'وَالْمُلُوكُ إِذَا دَخَلُوا قَرْيَةً أَفْسَدُوهَا',
        'بِالْقَلَمِ كَتَبَ الطَّالِبُ.',
        'فَالْكِتَابُ مُفِيدٌ',
        'كَيْ تَنْجَحَ كَأَنَّهُ حَقِيقِيٌّ كَمْ كِتَابًا',
    ]
    for text in tests:
        print(f'\n  النص: {text}')
        tokens = tokenize(text)
        for t in tokens:
            print(f'    [{t.kind:8}] {t.surface}')
