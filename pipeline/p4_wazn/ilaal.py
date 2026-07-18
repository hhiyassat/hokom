#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/ilaal.py — Weak-Radical Transformation Licensing (Phase 4A-β)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

إعلال الجذر الضعيف — تحويل مُرخَّص وليس تبديلًا مباشرًا.

المبدأ:
  لا يُبدَّل ي → و أو ا → و تلقائيًا.
  كل تحويل يحتاج:
    1. موضع صريح في الوزن (FA / AYN / LAM).
    2. سياق صوتي مُرخِّص (كسرة / ضمة / فتحة).
    3. قاعدة مُدرَجة في LICENSED_TRANSFORMATIONS.
    4. أثر تحويلي موثَّق (TransformationTrace).

نماذج البيانات:
  IlaalHypothesis  — فرضية وسيطة تصف تحويلًا مُحتملًا (لم يُثبَّت بعد)
  IlaalResolution  — مخرج apply_ilaal_resolution(): ACCEPT | DEFER | BLOCK

القانون الأساسي:
  IlaalResolution.directive ∈ {'ACCEPT', 'DEFER', 'BLOCK'}
  IlaalResolution ACCEPT → proposed_root موجود + transformations ≠ ()
                            أو proposed_root_after كان محددًا مسبقًا (transformations=())
  IlaalResolution DEFER  → proposed_root = None + transformations = ()
  لا إنتاج canonical_root — الترخيص في P3.11 فقط.
  لا استيراد من hr2s.
  لا مسارات مطلقة.

حالات محسومة (4A-β الإصدار الثاني):
  ✓ يَسْتَطِيعُ + يَسْتَفْعِل: ي في موضع العين + كسرة → أصل و → (ط،و،ع)
  ✗ نَامَ / قَالَ / بَاعَ: ألف في عين الماضي → DEFER (غامض بدون مضارع)

حالات المنع المُثبَّتة:
  ✗ لا تبديل ي→و بدون وزن + سياق كسرة مُرخَّص
  ✗ لا فرض واو في الألف تلقائيًا (ا في العين → DEFER)
  ✗ لا يُعالَج بَاعَ (ب-ي-ع) كـ ب-و-ع
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda


# ══════════════════════════════════════════════════════════════════════════════
# 1.  ثوابت داخلية
# ══════════════════════════════════════════════════════════════════════════════

_DIACRITICS = frozenset('ًٌٍَُِّْٰٕٓٔ')
_LONG_VOWEL_LETTERS = frozenset({'و', 'ا', 'ي'})
_PROHIBITED = frozenset({"ا", "ى", "أ", "إ", "ؤ", "ئ", "آ", "?", ""})
_WEAK_LETTERS = frozenset({'ي', 'و', 'ا'})


def _extract_base_consonants(text: str) -> tuple:
    """استخرج الحروف الأساسية بحذف الحركات والمسافات."""
    return tuple(ch for ch in text if ch not in _DIACRITICS and ch != ' ')


def _normalize_host(host: str) -> str:
    """طبّع المضيف: توحيد الهمزة ثم توسيع الشدة."""
    return normalize_shadda(normalize_hamza(host))


# ══════════════════════════════════════════════════════════════════════════════
# 2.  نماذج البيانات
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class WeakRadicalTransformation:
    """قاعدة إعلال مُرخَّصة — بيانات، ليست كودًا.

    كل تبديل (و→ي مثلًا) مُمثَّل كقاعدة صريحة مع موضعها وسياقها؛
    التطبيق دائمًا عبر apply_ilaal_resolution() لا مباشرةً.
    """
    rule_id: str               # معرّف القاعدة: 'WAW_TO_YAA_KASRA_CONDITIONED'
    surface_form: str          # الصورة السطحية: 'ي'
    underlying_form: str       # الجذر الأصلي: 'و'
    position_class: str        # 'FA' | 'AYN' | 'LAM'
    conditioning_factor: str   # 'KASRA_ENVIRONMENT' | 'FATHA_ALIF' | 'DAMMA_ENVIRONMENT'
    confidence: str            # 'HIGH' | 'MEDIUM'


@dataclass(frozen=True)
class TransformationTrace:
    """أثر التحويل — يوثّق كل خطوة في الإعلال لأغراض المراجعة والمعالجة اللاحقة."""
    surface_realization: str   # الحرف الذي ظهر في السطح: 'ي'
    underlying_radical: str    # الجذر الأصلي المقترح: 'و'
    position: str              # موضع الجذر: 'AYN'
    cause: str                 # سبب الإعلال: 'kasra_conditioned_weak_radical_transformation'
    licensed_by: str           # rule_id القاعدة: 'WAW_TO_YAA_KASRA_CONDITIONED'
    wazn_context: str          # الوزن الذي أطلق التحويل: 'يَسْتَفْعِل'


@dataclass(frozen=True)
class IlaalHypothesis:
    """فرضية إعلال وسيطة — تصف تحويلًا مُحتملًا لم يُثبَّت بعد.

    تُبنى داخل apply_ilaal_resolution() لكل موضع جذري ضعيف مُرشَّح.
    لا تُمثَّل جذرًا مقبولًا — الترخيص في IlaalResolution ثم P3.11.

    surface_element    : الحرف الذي ظهر في السطح ('ي')
    underlying_candidate: الأصل المُقترح ('و')
    radical_position   : موضع الجذر في الوزن ('AYN')
    transformation_id  : معرّف القاعدة المُطابِقة ('WAW_TO_YAA_KASRA_CONDITIONED')
    wazn_context       : الوزن الذي فتح هذه الفرضية ('يَسْتَفْعِل')
    conditions_checked : الشروط التي تحققت ('KASRA_ENVIRONMENT',)
    """
    surface_element: str
    underlying_candidate: str
    radical_position: str
    transformation_id: str
    wazn_context: str
    conditions_checked: tuple
    evidence_ids: tuple
    residual_codes: tuple


@dataclass(frozen=True)
class IlaalResolution:
    """مخرج apply_ilaal_resolution() — عقد W3.

    الحقول الجوهرية:
      directive          : 'ACCEPT' | 'DEFER' | 'BLOCK'
      transformations    : tuple[TransformationTrace] — التحويلات المُنجَزة
      proposed_root      : الجذر المُشتَق بعد الإعلال، أو None
      unresolved_positions: المواضع التي لم تُحسَم بعد

    القوانين:
      ACCEPT + transformations=() → proposed_root_after كان محددًا مسبقًا (لا إعلال)
      ACCEPT + transformations≠() → إعلال مُنجَز + proposed_root مبني عليه
      DEFER → proposed_root=None + transformations=() + unresolved_positions≠()
      لا canonical_root — الترخيص حكر على P3.11.
    """
    directive: str                            # 'ACCEPT' | 'DEFER' | 'BLOCK'
    transformations: tuple                    # tuple[TransformationTrace, ...]
    proposed_root: Optional[tuple]            # الجذر المُقترح أو None
    unresolved_positions: tuple               # المواضع الغامضة
    failure_reason: Optional[str]             # سبب الفشل (للتشخيص)
    evidence_ids: tuple
    trace_ids: tuple
    residual_codes: tuple

    def to_dict(self) -> dict:
        """تسلسل JSON-safe."""
        return {
            'directive': self.directive,
            'proposed_root': list(self.proposed_root) if self.proposed_root else None,
            'transformations': [
                {
                    'surface_realization': t.surface_realization,
                    'underlying_radical': t.underlying_radical,
                    'position': t.position,
                    'cause': t.cause,
                    'licensed_by': t.licensed_by,
                    'wazn_context': t.wazn_context,
                }
                for t in self.transformations
            ],
            'unresolved_positions': list(self.unresolved_positions),
            'evidence_ids': list(self.evidence_ids),
            'trace_ids': list(self.trace_ids),
            'residual_codes': list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  سجل القواعد المُرخَّصة
# ══════════════════════════════════════════════════════════════════════════════

LICENSED_TRANSFORMATIONS: tuple = (
    # القاعدة: الواو يُبدَّل بياء إذا وقع في موضع العين وسبقته كسرة.
    # الاستدلال العكسي: رؤية ي في موضع العين بسياق كسرة → الأصل و.
    # شاهد: طَوَعَ → يَطُوعُ → يَطِيعُ ← الأصل: ط-و-ع
    # شاهد: يَسْتَطِيعُ: وزن يَسْتَفْعِل → عين الجذر بكسرة → ي في السطح ← و في الجذر
    WeakRadicalTransformation(
        rule_id='WAW_TO_YAA_KASRA_CONDITIONED',
        surface_form='ي',
        underlying_form='و',
        position_class='AYN',
        conditioning_factor='KASRA_ENVIRONMENT',
        confidence='HIGH',
    ),
)


# ══════════════════════════════════════════════════════════════════════════════
# 4.  خرائط السياق
# ══════════════════════════════════════════════════════════════════════════════

# سياق عين الجذر (الصوت المتوقع على العين) حسب الوزن
_WAZN_AYN_VOWEL_CONTEXT: dict = {
    'يَسْتَفْعِل': 'KASRA',      # يَسْتَ-فْ-عِ-ل   ← كسرة على العين
    'يَفْعِل':     'KASRA',      # يَ-فْ-عِ-ل
    'مُفْتَعِل':   'KASRA',      # مُ-فْ-تَ-عِ-ل
    'فَعِلَ':      'KASRA',      # فَ-عِ-لَ
    'فَعَلَ':      'FATHA_ALIF', # فَ-عَ-لَ → الألف في السطح غامضة (واو أو ياء)
    'فَعُلَ':      'DAMMA',      # فَ-عُ-لَ
}

# عدد حروف البادئة (الزيادة الصرفية) لكل نمط ziyadah_detected
_ZIYADAH_TO_PREFIX_COUNT: dict = {
    ('ALIF_WASL', 'SIN', 'TA'): 3,   # يَ + سْ + تَ = (ي،س،ت) → 3 حروف
    ('MIM_ZIYADAH',):            1,   # مَ/مُ = (م) → 1 حرف
    ():                          0,   # لا بادئة (فَعَلَ / فَعِلَ) — جذر مباشر
    # ('MIM_ZIYADAH','IFTIEAL_TA') → Pattern C محلول مسبقًا، proposed_root_after≠None دائمًا
}

# تحويل: سياق الوزن → عامل التكييف في القاعدة
_CONTEXT_TO_FACTOR: dict = {
    'KASRA':      'KASRA_ENVIRONMENT',
    'FATHA_ALIF': 'FATHA_ALIF',
    'DAMMA':      'DAMMA_ENVIRONMENT',
}


# ══════════════════════════════════════════════════════════════════════════════
# 5.  دوال مساعدة
# ══════════════════════════════════════════════════════════════════════════════

def _make_defer(reason: str, hypothesis, unresolved: tuple = ('AYN',)) -> IlaalResolution:
    """أنشئ IlaalResolution بحكم DEFER."""
    return IlaalResolution(
        directive='DEFER',
        transformations=(),
        proposed_root=None,
        unresolved_positions=unresolved,
        failure_reason=reason,
        evidence_ids=tuple(hypothesis.evidence_ids),
        trace_ids=('p4a:ilaal:deferred',),
        residual_codes=tuple(hypothesis.residual_codes) + (reason,),
    )


def _make_accept_passthrough(hypothesis) -> IlaalResolution:
    """الجذر محلول مسبقًا (proposed_root_after≠None) — ACCEPT بلا إعلال."""
    return IlaalResolution(
        directive='ACCEPT',
        transformations=(),
        proposed_root=tuple(hypothesis.proposed_root_after),
        unresolved_positions=(),
        failure_reason=None,
        evidence_ids=tuple(hypothesis.evidence_ids),
        trace_ids=('p4a:ilaal:passthrough_already_resolved',),
        residual_codes=tuple(hypothesis.residual_codes),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 6.  الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def apply_ilaal_resolution(hypothesis) -> IlaalResolution:
    """
    حاول حل الحرف الضعيف في WaznHypothesis عبر قواعد الإعلال المُرخَّصة.

    hypothesis: WaznHypothesis (duck-typing — لا استيراد دائري)

    العودة: IlaalResolution
      directive='ACCEPT' + transformations≠() + proposed_root → إعلال مُنجَز
      directive='ACCEPT' + transformations=() + proposed_root → محلول مسبقًا
      directive='DEFER'  + proposed_root=None                  → لا حل

    القيود الصارمة:
      - لا تبديل مباشر ي→و أو ا→و.
      - كل تحويل يُطابق قاعدة في LICENSED_TRANSFORMATIONS.
      - ألف في موضع العين من فَعَلَ → DEFER (غامض بدون دليل المضارع).
      - لا استيراد من hr2s.
      - لا canonical_root في المخرج.
    """

    # ── الجذر محلول مسبقًا → لا إعلال مطلوب ────────────────────────────────
    if hypothesis.proposed_root_after is not None:
        return _make_accept_passthrough(hypothesis)

    # ── تحديد سياق العين حسب الوزن ─────────────────────────────────────────
    wazn = hypothesis.proposed_wazn
    ayn_context = _WAZN_AYN_VOWEL_CONTEXT.get(wazn)

    if ayn_context is None:
        return _make_defer('defer:ilaal:unknown_wazn_ayn_context', hypothesis,
                           unresolved=('AYN:unknown_wazn_context',))

    # ── استخراج الحروف الأساسية بعد البادئة ─────────────────────────────────
    ziyadah_key = tuple(hypothesis.ziyadah_detected)
    prefix_count = _ZIYADAH_TO_PREFIX_COUNT.get(ziyadah_key)

    if prefix_count is None:
        return _make_defer('defer:ilaal:unknown_ziyadah_type', hypothesis,
                           unresolved=('AYN:unknown_ziyadah',))

    normalized = _normalize_host(hypothesis.refined_host)
    all_consonants = _extract_base_consonants(normalized)

    if len(all_consonants) <= prefix_count:
        return _make_defer('defer:ilaal:insufficient_base_consonants', hypothesis,
                           unresolved=('AYN:insufficient_consonants',))

    base = all_consonants[prefix_count:]

    # ── نتوقع ثلاثة حروف أساسية: FA + AYN + LAM ─────────────────────────────
    if len(base) != 3:
        return _make_defer('defer:ilaal:base_not_trilateral', hypothesis,
                           unresolved=('AYN:non_trilateral_base',))

    fa, ayn_surface, lam = base[0], base[1], base[2]

    # ── تحقق أن عين الجذر حرف ضعيف ─────────────────────────────────────────
    if ayn_surface not in _WEAK_LETTERS:
        return _make_defer('defer:ilaal:ayn_not_weak', hypothesis,
                           unresolved=())     # العين ليست ضعيفة → لا موضع غامض

    # ── الألف في موضع العين من ماضٍ → غامضة (حمى المنع) ──────────────────
    # الألف يمكن أن تكون أصلها واو (قَالَ، نَامَ) أو ياء (بَاعَ، سَارَ)
    # لا نستطيع الجزم بدون دليل المضارع → DEFER
    if ayn_surface == 'ا' and ayn_context == 'FATHA_ALIF':
        return _make_defer(
            'defer:ilaal:alif_ayn_ambiguous_without_mudaric', hypothesis,
            unresolved=('AYN:alif_ambiguous',),
        )

    # ── تحقق صحة FA وLAM ────────────────────────────────────────────────────
    for ch in (fa, lam):
        if ch in _PROHIBITED or ch in _LONG_VOWEL_LETTERS:
            return _make_defer('defer:ilaal:fa_or_lam_invalid', hypothesis,
                               unresolved=('AYN:fa_or_lam_invalid',))

    # ── بحث عن قاعدة مُرخَّصة مطابقة ────────────────────────────────────────
    target_factor = _CONTEXT_TO_FACTOR.get(ayn_context)
    matching_rules = [
        rule for rule in LICENSED_TRANSFORMATIONS
        if (rule.position_class == 'AYN'
            and rule.surface_form == ayn_surface
            and rule.conditioning_factor == target_factor)
    ]

    # تعدد القواعد → DEFER (غموض — لا نختار تعسفًا)
    if len(matching_rules) > 1:
        return _make_defer('defer:ilaal:multiple_rules_conflict', hypothesis,
                           unresolved=('AYN:ambiguous_multiple_rules',))

    if len(matching_rules) == 1:
        rule = matching_rules[0]
        underlying = rule.underlying_form
        proposed = (fa, underlying, lam)

        # تحقق نهائي من صحة الجذر
        if any(c in _PROHIBITED for c in proposed):
            return _make_defer(
                'defer:ilaal:proposed_root_contains_prohibited', hypothesis,
                unresolved=('AYN:prohibited_in_proposed',),
            )

        # بناء فرضية الإعلال الوسيطة (لأغراض التوثيق)
        ilaal_hyp = IlaalHypothesis(
            surface_element=ayn_surface,
            underlying_candidate=underlying,
            radical_position='AYN',
            transformation_id=rule.rule_id,
            wazn_context=wazn,
            conditions_checked=(target_factor,),
            evidence_ids=tuple(hypothesis.evidence_ids),
            residual_codes=(),
        )

        trace = TransformationTrace(
            surface_realization=ayn_surface,
            underlying_radical=underlying,
            position='AYN',
            cause='kasra_conditioned_weak_radical_transformation',
            licensed_by=rule.rule_id,
            wazn_context=wazn,
        )

        return IlaalResolution(
            directive='ACCEPT',
            transformations=(trace,),
            proposed_root=proposed,
            unresolved_positions=(),
            failure_reason=None,
            evidence_ids=tuple(hypothesis.evidence_ids) + (
                f'ev:ilaal:{rule.rule_id.lower()}',
            ),
            trace_ids=(f'p4a:ilaal:{rule.rule_id.lower()}:resolved',),
            residual_codes=tuple(hypothesis.residual_codes),
        )

    # لا قاعدة مطابقة
    return _make_defer('defer:ilaal:no_licensed_rule_matched', hypothesis,
                       unresolved=('AYN:no_rule',))


# ── حفظ backward-compat: IlaalHypothesis (الاسم القديم لمخرج apply_ilaal_resolution)
# اسم IlaalHypothesis الآن يُشير للفرضية الوسيطة (عقد W3 الجديد)
# الكود المستهلِك يجب أن يستخدم IlaalResolution مع apply_ilaal_resolution()
