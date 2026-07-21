#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p1_atomic_structure/slot_engineering.py — جبر خانات المقاطع
Canonical location (R-4 refactoring).

يحتوي على:
  - جداول انتقال الخانات (SLOT_TRANS)
  - مجموعات الأنماط المرخصة (VALID_S, PREFIX_S, WORD_FINAL_ONLY)
  - دوال الحكم البنيوي على الخانات (_gate, word_gate)

لا يعتمد على أي ثوابت Unicode — يعمل بمصطلحات C / V / VV فقط.
المستهلك الرئيسي: cell_builder.syllabify() و word_gate.
"""

# ══════════════════════════════════════════════════════════════════════════════
# 1.  Slot Engineering Algebra — جداول الانتقال والقرار
# ══════════════════════════════════════════════════════════════════════════════

#  عنصر C  ← صامت (ساكن، أو بادئة المقطع في المتحرك)
#  عنصر V  ← حركة قصيرة أو حرف علة يمد النواة

SLOT_TRANS: dict[str, dict[str, str | None]] = {
    '':      {'C': 'C',     'V': None},    # لا تبدأ الخانة بـ V
    'C':     {'V': 'CV',    'C': None},    # C وحده → ينتظر V
    'CV':    {'V': 'CVV',   'C': 'CVC'},   # مشبعة ← يمكن الامتداد
    'CVV':   {'C': 'CVVC',  'V': None},    # مشبعة ← يمكن الامتداد
    'CVC':   {'C': 'CVCC',  'V': None},    # مشبعة ← يمكن الامتداد (آخر الكلمة)
    'CVVC':  {'C': 'CVVCC', 'V': None},    # مشبعة ← يمكن الامتداد (آخر الكلمة)
    'CVCC':  {},                            # طرفية مشبعة
    'CVVCC': {},                            # طرفية مشبعة
}

# S: الأنماط الستة المرخصة
VALID_S: set[str] = {'CV', 'CVV', 'CVC', 'CVVC', 'CVCC', 'CVVCC'}

# Prefix(S): بادئات الأنماط المرخصة (بما فيها ε)
PREFIX_S: set[str] = {'', 'C'} | VALID_S

# أنماط آخر الكلمة فقط
WORD_FINAL_ONLY: set[str] = {'CVCC', 'CVVCC'}


# ══════════════════════════════════════════════════════════════════════════════
# 2.  دوال الحكم البنيوي
# ══════════════════════════════════════════════════════════════════════════════

def _gate(state: str) -> str:
    """بوابة الحكم لخانة واحدة."""
    if state in VALID_S:   return 'ACCEPT'
    if state in PREFIX_S:  return 'DEFER'
    return 'BLOCK'


def _can_extend_with_mutaharrik(state: str) -> bool:
    """
    هل يمكن لمتحرك (وحدة C+V) أن يُمتَصَّ داخل الخانة الحالية؟

    المتحرك يضيف C ثم V — يجب أن تقبلهما الخانة معًا.
    إذا رفضت الخانة أحدهما أو كليهما → SATURATED.
    """
    after_c = SLOT_TRANS.get(state, {}).get('C')
    if after_c is None:
        return False                         # لا تقبل C → مشبعة
    after_cv = SLOT_TRANS.get(after_c, {}).get('V')
    return after_cv is not None              # True فقط إذا قبلت C ثم V


def word_gate(slots: list[dict]) -> tuple[str, list[str]]:
    """
    ∀i Slot_i ∈ S             → ACCEPT
    ∃i Slot_i ∉ S ∪ Prefix(S) → BLOCK
    آخر خانة ∈ Prefix(S) \\ S  → DEFER
    + CVCC / CVVCC في غير الآخر → BLOCK
    """
    real = [s for s in slots if s['surface'] != ' ']
    viols: list[str] = []

    if not real:
        return 'DEFER', viols

    # CVCC/CVVCC في غير آخر الكلمة
    for i, s in enumerate(real[:-1]):
        if s['pattern'] in WORD_FINAL_ONLY:
            viols.append(f"{s['pattern']} في غير آخر الكلمة (خانة {i+1})")

    # بوابات الخانات
    for s in real:
        if s['gate'] == 'BLOCK':
            viols += s['violations']
            return 'BLOCK', viols

    # DEFER: أي خانة DEFER → التحفظ يطغى (قانون: BLOCK > DEFER > ACCEPT)
    for s in real:
        if s['gate'] == 'DEFER':
            viols += s['violations']
            return 'DEFER', viols

    return 'ACCEPT', viols


# ══════════════════════════════════════════════════════════════════════════════
# 3.  Phonological Boundary Evidence Labels
#     (HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01)
# ══════════════════════════════════════════════════════════════════════════════

# همزة الوصل at word-initial position after clitic stripping:
# the ا is phonologically silent — it is the orthographic carrier for the
# prosthetic vowel used in citation form only.  After segmentation removes
# the proclitic, the segment_host begins with ا + sukun consonant.  The slot
# engine must not treat this ا as a phonological V (which would yield '+V').
HAMZAT_AL_WASL_PATTERN: str = 'HAMZAT_AL_WASL'

# ألف الفارقة at word-final position after واو الجماعة (وا suffix):
# the final ا is purely orthographic (zero phonological content).  Without
# this label the slot engine extends the CVV slot to 'CVV+V', which is not
# in VALID_S and causes a false BLOCK on all masculine plural verb forms.
ALEF_FARQA_PATTERN: str = 'ALEF_FARQA'

# The synthetic slot dict keys are identical to all other slot dicts so that
# word_gate() and downstream consumers (mabni_projection, slot_patterns list)
# can iterate without special-casing.  gate='' ensures the synthetic slots
# are invisible to word_gate's BLOCK and DEFER tests.
