#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p1_atomic_structure/cell_builder.py — بناء الخلايا الصوتية
Canonical location (R-4 refactoring).
The root-level syllabifier.py is now a shim that re-exports from here
and from slot_engineering.

يحتوي على:
  - ثوابت Unicode للحروف العربية والحركات
  - Phone: بنية الوحدة الصوتية
  - parse_phones(): تحليل النص إلى phones
  - syllabify(): تقطيع phones إلى خانات

الاعتماد على:
  .slot_engineering: جداول SLOT_TRANS وأدوات الحكم البنيوي
"""

import sys

from .slot_engineering import (
    SLOT_TRANS,
    VALID_S,
    PREFIX_S,
    WORD_FINAL_ONLY,
    _gate,
    _can_extend_with_mutaharrik,
    word_gate,
    HAMZAT_AL_WASL_PATTERN,
    ALEF_FARQA_PATTERN,
)

# ══════════════════════════════════════════════════════════════════════════════
# 1.  ثوابت Unicode
# ══════════════════════════════════════════════════════════════════════════════

FATHA    = 'َ'
DAMMA    = 'ُ'
KASRA    = 'ِ'
SUKUN    = 'ْ'
SHADDA   = 'ّ'
TANWIN_F = 'ً'
TANWIN_D = 'ٌ'
TANWIN_K = 'ٍ'
TATWEEL  = 'ـ'

SHORT_VOWELS   = {FATHA, DAMMA, KASRA}
TANWIN         = {TANWIN_F, TANWIN_D, TANWIN_K}
ALL_DIACRITICS = SHORT_VOWELS | TANWIN | {SUKUN, SHADDA,
                  'ٓ', 'ٔ', 'ٕ', 'ٰ'}

VOWEL_LETTERS_ALWAYS = {'ا', 'ى'}
VOWEL_LETTERS_COND   = {'و', 'ي'}
VOWEL_LETTERS        = VOWEL_LETTERS_ALWAYS | VOWEL_LETTERS_COND

ALEF_MADDA = 'آ'   # → ء(فتحة) + ا

ARABIC_BASE = (
    set(chr(c) for c in range(0x0621, 0x063B)) |
    set(chr(c) for c in range(0x0641, 0x064B))
)


# ══════════════════════════════════════════════════════════════════════════════
# 2.  هيكل Phone
# ══════════════════════════════════════════════════════════════════════════════

class Phone:
    def __init__(self, char: str, diacritics: list[str]):
        self.char       = char
        self.diacritics = diacritics

    def is_vowel_letter(self) -> bool:
        if self.char in VOWEL_LETTERS_ALWAYS:
            return True
        if self.char in VOWEL_LETTERS_COND:
            return not any(d in (SHORT_VOWELS | TANWIN) for d in self.diacritics)
        return False

    def is_mutaharrik(self) -> bool:
        if self.is_vowel_letter():
            return False
        return any(d in (SHORT_VOWELS | TANWIN) for d in self.diacritics)

    def is_sakin(self) -> bool:
        if self.is_vowel_letter():
            return False
        return not self.is_mutaharrik()

    def surface(self) -> str:
        return self.char + ''.join(self.diacritics)

    def __repr__(self):
        return f'Phone({self.char!r},{self.diacritics!r})'


# ══════════════════════════════════════════════════════════════════════════════
# 3.  تحليل النص إلى phones
# ══════════════════════════════════════════════════════════════════════════════

def parse_phones(text: str) -> list[Phone]:
    phones: list[Phone] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == ' ':
            phones.append(Phone(' ', []))
            i += 1
            continue
        if ch == ALEF_MADDA:
            phones.append(Phone('ء', [FATHA]))
            phones.append(Phone('ا', []))
            i += 1
            continue
        if ch == TATWEEL or ch not in (ARABIC_BASE | VOWEL_LETTERS):
            i += 1
            continue
        j = i + 1
        diacritics: list[str] = []
        while j < len(text) and text[j] in ALL_DIACRITICS:
            diacritics.append(text[j])
            j += 1
        if SHADDA in diacritics:
            rest = [d for d in diacritics if d != SHADDA]
            phones.append(Phone(ch, [SUKUN]))
            phones.append(Phone(ch, rest))
        else:
            phones.append(Phone(ch, diacritics))
        i = j
    return phones


# ══════════════════════════════════════════════════════════════════════════════
# 4.  Slot Engineering — آلة الخانات (بناء الخلايا)
# ══════════════════════════════════════════════════════════════════════════════

def syllabify(phones: list[Phone]) -> list[dict]:
    """
    Slot Engineering Algebra syllabifier.

    قاعدة الإشباع (Saturation):
      لا تُغلق الخانة ولا يُفتح Slot جديد حتى يثبت أن الخانة الحالية
      أصبحت SATURATED — أي أن العنصر القادم لا يمكن استيعابه فيها ضمن
      الأنماط المرخصة.

      Open(Slot_{i+1})  ⟺  Saturated(Slot_i)

    حالتا الخانة:
      COMPLETE   — الحالة الحالية ∈ S (نمط مرخص، لكن قد تمتد)
      SATURATED  — العنصر القادم لا يمكن ضمه → أغلق Slot الحالي

    لكل phone:
      متحرك   → إذا كانت الخانة الحالية COMPLETE تصبح SATURATED → أغلق ثم افتح CV
      حرف علة → يمد النواة: CV → CVV
      ساكن    → يضيف كوداً: CV → CVC  أو  CVV → CVVC  إلخ

    القرار: ACCEPT | DEFER | BLOCK  لكل خانة وللكلمة كلها.
    """
    slots: list[dict] = []

    # حالة الخانة الجارية
    slot_phones:  list[Phone] = []
    slot_pattern: str         = ''

    def close_slot(reason: str = 'WORD_END', extra_violation: str = '',
                   saturation_reason: str = '') -> None:
        """
        أغلق الخانة الجارية وأضفها إلى القائمة.

        reason:
          SATURATED    — أُغلقت لأن العنصر القادم لا يُستوعَب (المتحرك يُشبِع)
          WORD_END     — أُغلقت لانتهاء الكلمة
          BLOCK_ORPHAN — خانة في حالة PREFIX عند ورود متحرك (حرف ساكن يتيم)
          BLOCK_SAKIN  — ساكن لا يجد خانة تستوعبه

        saturation_reason:
          نص يشرح سبب الإشباع (يُملأ فقط عند reason=SATURATED)
        """
        nonlocal slot_phones, slot_pattern
        if not slot_phones:
            return
        surface  = ''.join(p.surface() for p in slot_phones)
        decision = _gate(slot_pattern)

        # حالة الخانة لحظة الإغلاق
        status_at_close = (
            'COMPLETE' if slot_pattern in VALID_S else
            'PREFIX'   if slot_pattern in PREFIX_S else
            'BLOCK'
        )

        viols = []
        if extra_violation:
            viols.append(extra_violation)
        if decision == 'BLOCK':
            viols.append(f"BLOCK — نمط غير مرخص [{slot_pattern}]")
        elif decision == 'DEFER':
            viols.append(f"DEFER — خانة غير مكتملة [{slot_pattern}]")

        slots.append({
            'surface':           surface,
            'pattern':           slot_pattern,
            'gate':              decision,
            'violations':        viols,
            'status_at_close':   status_at_close,   # COMPLETE | PREFIX | BLOCK
            'close_reason':      reason,             # SATURATED | WORD_END | BLOCK_*
            'saturation_reason': saturation_reason,  # why SATURATED (empty otherwise)
        })
        slot_phones  = []
        slot_pattern = ''

    def extend(elem: str, phone: Phone) -> bool:
        """أضف عنصر C أو V للخانة. أعِد True عند النجاح."""
        nonlocal slot_pattern
        nxt = SLOT_TRANS.get(slot_pattern, {}).get(elem)
        if nxt is not None:
            slot_phones.append(phone)
            slot_pattern = nxt
            return True
        return False

    # -- Lookahead helpers (HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01) --

    def _next_is_sakin(ph_idx):
        """Is the next non-space phone sakin? (hamzat al-wasl test)"""
        for j in range(ph_idx + 1, len(phones)):
            p = phones[j]
            if p.char != ' ':
                return p.is_sakin()
        return False

    def _is_last_real_phone(ph_idx):
        """Is this the last non-space phone? (alef al-farqa test)"""
        for j in range(ph_idx + 1, len(phones)):
            if phones[j].char != ' ':
                return False
        return True

    for _ph_idx, phone in enumerate(phones):

        # ── فراغ بين الكلمات ───────────────────────────────────────────────
        if phone.char == ' ':
            close_slot('WORD_END')
            slots.append({'surface': ' ', 'pattern': '', 'gate': '',
                          'violations': [], 'status_at_close': '',
                          'close_reason': '', 'saturation_reason': ''})
            continue

        # ── متحرك ─────────────────────────────────────────────────────────
        if phone.is_mutaharrik():
            if slot_pattern == '':
                pass
            elif not _can_extend_with_mutaharrik(slot_pattern):
                if slot_pattern in VALID_S:
                    sat_reason = (
                        f"next symbol '{phone.surface()}' starts a new syllable onset "
                        f"— its C+V cannot legally extend {slot_pattern}"
                    )
                    close_slot('SATURATED', saturation_reason=sat_reason)
                else:
                    close_slot('BLOCK_ORPHAN')

            slot_phones  = [phone]
            slot_pattern = 'CV'

        # ── حرف علة: يمد النواة V → VV ─────────────────────────────────────
        elif phone.is_vowel_letter():
            if not extend('V', phone):
                # -- HAMZAT_AL_WASL_SKIP (HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01)
                # Conditions: initial slot (slot_pattern='') + bare alef (alef char) + next sakin.
                # Hamzat al-wasl is phonologically silent in connected speech.
                # Treating it as V yields '+V' (BLOCK) for all waw-al-jamaa verbs.
                # NOT licensed: alef in non-initial position, or next phone non-sakin.
                if (slot_pattern == ''
                        and phone.char == 'ا'
                        and _next_is_sakin(_ph_idx)):
                    slots.append({
                        'surface':           phone.surface(),
                        'pattern':           HAMZAT_AL_WASL_PATTERN,
                        'gate':              '',
                        'violations':        [],
                        'status_at_close':   HAMZAT_AL_WASL_PATTERN,
                        'close_reason':      'HAMZAT_AL_WASL_SKIP',
                        'saturation_reason': '',
                    })
                    # slot_phones and slot_pattern remain '' for the real onset

                # -- ALEF_FARQA_BOUNDARY (HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01)
                # Conditions: current slot CVV + bare alef + last real phone.
                # The final alef of waw-al-jamaa suffix is alef al-farqa:
                # purely orthographic, zero phonological content.
                # NOT licensed: alef after CVV in non-final position, or slot != CVV.
                elif (slot_pattern == 'CVV'
                      and phone.char == 'ا'
                      and _is_last_real_phone(_ph_idx)):
                    close_slot('ALEF_FARQA_BOUNDARY')
                    slots.append({
                        'surface':           phone.surface(),
                        'pattern':           ALEF_FARQA_PATTERN,
                        'gate':              '',
                        'violations':        [],
                        'status_at_close':   ALEF_FARQA_PATTERN,
                        'close_reason':      'ALEF_FARQA_BOUNDARY',
                        'saturation_reason': '',
                    })

                else:
                    slot_phones.append(phone)
                    slot_pattern += '+V'

        # ── ساكن: يضيف كوداً C ──────────────────────────────────────────────
        else:
            if not extend('C', phone):
                close_slot('BLOCK_SAKIN', f"BLOCK — ساكن في غير موضعه [{phone.surface()}]")
                slot_phones  = [phone]
                slot_pattern = 'C'

    close_slot('WORD_END')
    return slots


# ══════════════════════════════════════════════════════════════════════════════
# 5.  تحليل كلمة كاملة
# ══════════════════════════════════════════════════════════════════════════════

def analyze_word(word: str) -> dict:
    phones  = parse_phones(word)
    slots   = syllabify(phones)
    verdict, word_viols = word_gate(slots)

    return {
        'original':        word,
        'syllables':       slots,
        'word_violations': word_viols,
        'verdict':         verdict,
    }


# ══════════════════════════════════════════════════════════════════════════════
# 6.  العرض
# ══════════════════════════════════════════════════════════════════════════════

W = 80

GATE_ICON = {'ACCEPT': '✓', 'DEFER': '⏸', 'BLOCK': '✗', '': ''}

def display(result: dict):
    syls = [s for s in result['syllables'] if s['surface'] != ' ']

    surface_line = ' | '.join(s['surface']  for s in syls)
    pattern_line = ' | '.join(s['pattern']  for s in syls)
    gate_line    = ' | '.join(
        f"{GATE_ICON.get(s['gate'],'')} {s['gate']}" for s in syls
    )

    verdict  = result['verdict']
    w_viols  = result['word_violations']
    s_viols  = [v for s in syls for v in s['violations']]
    all_viols = s_viols + w_viols

    print()
    print('─' * W)
    print(f"  الكلمة   : {result['original']}")
    print(f"  التقطيع  : {surface_line}")
    print(f"  الأنماط  : {pattern_line}")
    print(f"  البوابات : {gate_line}")
    print(f"  الحكم    : {GATE_ICON.get(verdict,'')} {verdict}")
    if all_viols:
        print(f"  ⚠ تفاصيل:")
        for v in all_viols:
            print(f"     • {v}")
    print('─' * W)


# ══════════════════════════════════════════════════════════════════════════════
# 7.  نماذج اختبار
# ══════════════════════════════════════════════════════════════════════════════

EXAMPLES = [
    ("كِتَابٌ",     "CV|CVV|CV      — ACCEPT"),
    ("مَكْتُوبٌ",   "CVC|CVV|CV     — ACCEPT"),
    ("مُدَرِّسٌ",   "CV|CVC|CV|CV   — ACCEPT (شدة)"),
    ("قُرْآنٌ",     "CVC|CVV|CV     — ACCEPT (آ)"),
    ("بَيْتْ",      "CVCC           — ACCEPT (CC في الآخر)"),
    ("يَكْتُبُ",    "CVC|CV|CV      — ACCEPT"),
    ("الْمُلُوكِ",  "CVC|CV|CVV|CV  — ACCEPT (بعد التطبيع: ءَلْمُلُوكِ)"),
]


def run_examples():
    print('\n' + '═' * W)
    print('   Slot Engineering — نماذج الاختبار')
    print('═' * W)
    for word, note in EXAMPLES:
        result = analyze_word(word)
        display(result)
        print(f'   [{note}]')


def interactive():
    print('\n' + '═' * W)
    print('   Slot Engineering Algebra — المُقطِّع')
    print('   أدخل كلمة مشكولة | q للخروج | ex للنماذج')
    print('═' * W)
    while True:
        try:
            user = input('\n  أدخل كلمة: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n  وداعًا.'); break
        if not user: continue
        if user.lower() == 'q': print('  وداعًا.'); break
        if user.lower() == 'ex': run_examples(); continue
        display(analyze_word(user))


def main():
    if len(sys.argv) > 1:
        for word in ' '.join(sys.argv[1:]).split():
            display(analyze_word(word))
    else:
        run_examples()
        interactive()


if __name__ == '__main__':
    main()
