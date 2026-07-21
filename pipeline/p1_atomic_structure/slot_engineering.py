#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p1_atomic_structure/slot_engineering.py — جبر خانات المقاطع
Canonical location (R-4 refactoring).

يحتوي على:
  - جداول انتقال الخانات (SLOT_TRANS)
  - مجموعات الأنماط المرخصة (VALID_S, PREFIX_S, WORD_FINAL_ONLY)
  - دوال الحكم البنيوي على الخانات (_gate, word_gate)
  - SLOT_TRANS_LICENSES: DomainTransitionLicense for each SLOT_TRANS entry (T-08 closure)

لا يعتمد على أي ثوابت Unicode — يعمل بمصطلحات C / V / VV فقط.
المستهلك الرئيسي: cell_builder.syllabify() و word_gate.
"""

# SGA contracts — imported lazily to avoid circular deps on non-SGA paths.
# SLOT_TRANS_LICENSES is populated at module load if contracts are available.
try:
    from pipeline.sga.contracts import DomainTransitionLicense, SlotId
    _SGA_CONTRACTS_AVAILABLE = True
except ImportError:
    _SGA_CONTRACTS_AVAILABLE = False
    DomainTransitionLicense = None  # type: ignore[assignment,misc]
    SlotId = None  # type: ignore[assignment,misc]

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


# ══════════════════════════════════════════════════════════════════════════════
# 4.  DomainTransitionLicense registry for each SLOT_TRANS entry (T-08 closure)
#
#     One license per SLOT_TRANS state. These are Hokom's domain-layer licenses
#     that describe which phonological slot transitions are structurally permitted.
#     Taaqol TransitionGate evaluates the constitutional verdict; these licenses
#     record the domain facts Hokom asserts at the phonological layer.
#
#     Naming: SLOT_TRANS_LICENSE_{FROM_STATE} (empty state → EPSILON)
# ══════════════════════════════════════════════════════════════════════════════

if _SGA_CONTRACTS_AVAILABLE:
    SLOT_TRANS_LICENSES: dict[str, DomainTransitionLicense] = {
        # State '' (EPSILON): empty slot boundary accepts first consonant only.
        # Invariant: no slot may begin with V.
        '': DomainTransitionLicense(
            license_id="DTL-SLOT_TRANS_EPSILON",
            cause="Empty slot boundary accepts initial consonant C; V is forbidden at slot start",
            input_slots=(SlotId.PHONOLOGICAL_CELLS,),
            output_slots=(SlotId.PHONOLOGICAL_CELLS,),
            condition_facts=("input_element=C",),
            obstacle_facts=("input_element=V:FORBIDDEN_AT_SLOT_START",),
            defeater_facts=(),
            evidence_refs=("SLOT_TRANS:epsilon:C->C",),
            residuals=(),
            stage="H2",
        ),
        # State 'C': single consonant prefix awaits vowel to become open syllable.
        # Cannot absorb a second consonant without a vowel (would not be in PREFIX_S).
        'C': DomainTransitionLicense(
            license_id="DTL-SLOT_TRANS_C",
            cause="Single consonant prefix C extends to open syllable CV on vowel input",
            input_slots=(SlotId.PHONOLOGICAL_CELLS,),
            output_slots=(SlotId.PHONOLOGICAL_CELLS,),
            condition_facts=("current_state=C", "input_element=V"),
            obstacle_facts=("input_element=C:DOUBLE_CONSONANT_CLUSTER_FORBIDDEN",),
            defeater_facts=(),
            evidence_refs=("SLOT_TRANS:C:V->CV",),
            residuals=(),
            stage="H2",
        ),
        # State 'CV': open short syllable — can extend to long vowel (CVV) or
        # close with consonant (CVC). Both are licensed.
        'CV': DomainTransitionLicense(
            license_id="DTL-SLOT_TRANS_CV",
            cause="Open syllable CV branches: V->CVV (long vowel) or C->CVC (closed)",
            input_slots=(SlotId.PHONOLOGICAL_CELLS,),
            output_slots=(SlotId.PHONOLOGICAL_CELLS,),
            condition_facts=("current_state=CV",),
            obstacle_facts=(),
            defeater_facts=(),
            evidence_refs=("SLOT_TRANS:CV:V->CVV", "SLOT_TRANS:CV:C->CVC"),
            residuals=(),
            stage="H2",
        ),
        # State 'CVV': long open syllable — can close with consonant (CVVC) only.
        # Second vowel extension is not permitted.
        'CVV': DomainTransitionLicense(
            license_id="DTL-SLOT_TRANS_CVV",
            cause="Long open syllable CVV closes to CVVC on consonant; second V extension forbidden",
            input_slots=(SlotId.PHONOLOGICAL_CELLS,),
            output_slots=(SlotId.PHONOLOGICAL_CELLS,),
            condition_facts=("current_state=CVV", "input_element=C"),
            obstacle_facts=("input_element=V:TRIPLE_VOWEL_EXTENSION_FORBIDDEN",),
            defeater_facts=(),
            evidence_refs=("SLOT_TRANS:CVV:C->CVVC",),
            residuals=(),
            stage="H2",
        ),
        # State 'CVC': closed short syllable — can extend at word-final only (CVCC).
        # Mid-word CVCC is a BLOCK (handled by word_gate).
        'CVC': DomainTransitionLicense(
            license_id="DTL-SLOT_TRANS_CVC",
            cause="Closed syllable CVC extends to geminate CVCC at word-final position only",
            input_slots=(SlotId.PHONOLOGICAL_CELLS,),
            output_slots=(SlotId.PHONOLOGICAL_CELLS,),
            condition_facts=("current_state=CVC", "input_element=C"),
            obstacle_facts=("input_element=V:POST_CLOSURE_VOWEL_FORBIDDEN",),
            defeater_facts=(),
            evidence_refs=("SLOT_TRANS:CVC:C->CVCC",),
            residuals=("WORD_FINAL_ONLY:CVCC",),
            stage="H2",
        ),
        # State 'CVVC': closed long syllable — can extend to super-heavy CVVCC
        # at word-final position only.
        'CVVC': DomainTransitionLicense(
            license_id="DTL-SLOT_TRANS_CVVC",
            cause="Closed long syllable CVVC extends to super-heavy CVVCC at word-final position only",
            input_slots=(SlotId.PHONOLOGICAL_CELLS,),
            output_slots=(SlotId.PHONOLOGICAL_CELLS,),
            condition_facts=("current_state=CVVC", "input_element=C"),
            obstacle_facts=("input_element=V:POST_CLOSURE_VOWEL_FORBIDDEN",),
            defeater_facts=(),
            evidence_refs=("SLOT_TRANS:CVVC:C->CVVCC",),
            residuals=("WORD_FINAL_ONLY:CVVCC",),
            stage="H2",
        ),
        # State 'CVCC': terminal saturated — no further extension licensed.
        # Any additional input is a structural violation (BLOCK).
        'CVCC': DomainTransitionLicense(
            license_id="DTL-SLOT_TRANS_CVCC",
            cause="Terminal saturated syllable CVCC: no further extension permitted",
            input_slots=(SlotId.PHONOLOGICAL_CELLS,),
            output_slots=(SlotId.PHONOLOGICAL_CELLS,),
            condition_facts=("current_state=CVCC", "state=TERMINAL_SATURATED"),
            obstacle_facts=("input_element=ANY:TERMINAL_EXTENSION_BLOCKED",),
            defeater_facts=(),
            evidence_refs=("SLOT_TRANS:CVCC:terminal",),
            residuals=("TERMINAL_SATURATED:CVCC",),
            stage="H2",
        ),
        # State 'CVVCC': super-heavy terminal — no further extension licensed.
        # Any additional input is a structural violation (BLOCK).
        'CVVCC': DomainTransitionLicense(
            license_id="DTL-SLOT_TRANS_CVVCC",
            cause="Super-heavy terminal syllable CVVCC: no further extension permitted",
            input_slots=(SlotId.PHONOLOGICAL_CELLS,),
            output_slots=(SlotId.PHONOLOGICAL_CELLS,),
            condition_facts=("current_state=CVVCC", "state=TERMINAL_SATURATED"),
            obstacle_facts=("input_element=ANY:TERMINAL_EXTENSION_BLOCKED",),
            defeater_facts=(),
            evidence_refs=("SLOT_TRANS:CVVCC:terminal",),
            residuals=("TERMINAL_SATURATED:CVVCC",),
            stage="H2",
        ),
    }
else:
    # SGA contracts unavailable — provide empty registry so imports don't fail.
    SLOT_TRANS_LICENSES: dict = {}
