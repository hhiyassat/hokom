# -*- coding: utf-8 -*-
"""
phonology.py — التعريفات الصوتية الأساسية للحروف العربية

DEPRECATED — DO NOT IMPORT
═══════════════════════════
هذا الملف معزول تمامًا عن خط أنابيب Hokom الحالي؛ لا يستورده أيُّ وحدة نشطة.
تم إنشاؤه في مرحلة استكشافية مبكرة وظلَّ يتيمًا منذ ذلك الحين.

المصدر الوحيد للحقيقة في تصنيف Unicode حاليًا هو:
    glyph_classification.py — BaseGlyphClass, MarkClass, MarkState, GlyphTrace

سيُحذف هذا الملف في مرحلة تنظيف Phase A (الخطوة 8 من الخطة التأسيسية).
حتى ذلك الحين: لا تضف imports منه في أي وحدة جديدة.

Phase A closure decision (2026-07): annotated DEPRECATED, deletion deferred.
"""

# ─────────────────────────────────────────────
# 1. الحروف الصامتة الخمسة والعشرون
# ─────────────────────────────────────────────
CONSONANTS: list[str] = [
    'ب', 'ت', 'ث', 'ج', 'ح', 'خ',
    'د', 'ذ', 'ر', 'ز', 'س', 'ش',
    'ص', 'ض', 'ط', 'ظ', 'ع', 'غ',
    'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه',
]
assert len(CONSONANTS) == 25

# ─────────────────────────────────────────────
# 2. حروف العلة الثلاثة
# ─────────────────────────────────────────────
VOWEL_LETTERS: list[str] = ['ا', 'و', 'ي']

# ─────────────────────────────────────────────
# 3. الحركات القصيرة الثلاث
# ─────────────────────────────────────────────
FATHA  = 'َ'   # َ  فتحة
DAMMA  = 'ُ'   # ُ  ضمة
KASRA  = 'ِ'   # ِ  كسرة

SHORT_VOWELS: dict[str, str] = {
    'فتحة': FATHA,
    'ضمة':  DAMMA,
    'كسرة': KASRA,
}

# ─────────────────────────────────────────────
# 4. السكون
# ─────────────────────────────────────────────
SUKUN = 'ْ'    # ْ  سكون

# ─────────────────────────────────────────────
# 5. الشدة
# ─────────────────────────────────────────────
SHADDA = 'ّ'   # ّ  شدة

# ─────────────────────────────────────────────
# 6. حكم الحرف من حيث الحركة والسكون
# ─────────────────────────────────────────────

def get_diacritic(char_with_diacritic: str) -> str | None:
    """
    أعِد الحركة أو السكون المصاحب للحرف إن وُجد، وإلا فـ None.
    المدخل: حرف + علامة (مثل 'بَ' أو 'بْ')
    """
    for ch in char_with_diacritic:
        if ch in SHORT_VOWELS.values() or ch == SUKUN:
            return ch
    return None


def is_sakin(char_with_diacritic: str) -> bool:
    """
    الحرف ساكن إذا:
      - حمل سكونًا صريحًا (ْ)
      - أو لم يحمل حركةً ولا سكونًا (خالٍ = ساكن بالأصل)
    """
    d = get_diacritic(char_with_diacritic)
    return d == SUKUN or d is None


def is_mutaharrik(char_with_diacritic: str) -> bool:
    """الحرف متحرك إذا حمل إحدى الحركات القصيرة الثلاث."""
    d = get_diacritic(char_with_diacritic)
    return d in SHORT_VOWELS.values()


# ─────────────────────────────────────────────
# 7. الحرف المشدد
# ─────────────────────────────────────────────

def expand_shadda(base_char: str, vowel: str) -> tuple[str, str]:
    """
    الحرف المشدد = تكرير الحرف:
      - النسخة الأولى: ساكنة  (base_char + SUKUN)
      - النسخة الثانية: تحمل حركة الشدة  (base_char + vowel)

    مثال: 'مَ' + شدة → ('مْ', 'مَ')
    """
    assert vowel in SHORT_VOWELS.values(), f"حركة غير معتبرة: {vowel!r}"
    first  = base_char + SUKUN   # ساكن
    second = base_char + vowel   # متحرك بحركة الشدة
    return first, second


# ─────────────────────────────────────────────
# 8. ال التعريف
# ─────────────────────────────────────────────

# ال التعريف = همزة مفتوحة + لام ساكنة
HAMZA     = 'ء'
AL_HAMZA  = HAMZA + FATHA   # ءَ
AL_LAM    = 'ل' + SUKUN     # لْ  (اللام ساكنة)

AL_TAAREEF = AL_HAMZA + AL_LAM   # ءَلْ

def attach_al(word: str) -> str:
    """
    أضف ال التعريف (ءَلْ) إلى أول الكلمة.
    ملاحظة: إدغام اللام الشمسية وأحكام الوصل تُعالج في طبقة لاحقة.
    """
    return AL_TAAREEF + word


# ─────────────────────────────────────────────
# مثال تشغيلي
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("الحروف الصامتة:", CONSONANTS)
    print("حروف العلة:", VOWEL_LETTERS)
    print("الحركات:", SHORT_VOWELS)
    print()

    test_chars = ['بَ', 'بْ', 'ب']
    for c in test_chars:
        print(f"  {c!r:6} | ساكن={is_sakin(c)} | متحرك={is_mutaharrik(c)}")

    print()
    first, second = expand_shadda('م', FATHA)
    print(f"  مَشدَّد: [{first!r}] + [{second!r}]")

    print()
    print(f"  ال التعريف: {AL_TAAREEF!r}")
    print(f"  كتاب مع ال: {attach_al('كتاب')!r}")
