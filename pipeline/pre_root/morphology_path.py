#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/pre_root/morphology_path.py — تصنيف المسار الصرفي (Axis 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُصنّف الكلمة إلى مسار صرفي بناءً على الشواهد البنيوية فقط.

القيود الصارمة:
  - لا استثناءات نصية خاصة بكلمات (no word-specific exceptions)
  - لا قواميس كلمات — فقط الشواهد البنيوية
  - لا باب، لا وزن، لا مصدر في هذه الطبقة
  - لا تغيير على الجذر أو مسار HR2S

المدخل: host_surface (بعد فصل الـ) + BoundaryKind + phones (اختياري)
المخرج: MorphologyPath
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from boundary.models import BoundaryKind


# ══════════════════════════════════════════════════════════════════════════════
# 1.  MorphologyPath — التصنوف
# ══════════════════════════════════════════════════════════════════════════════

class MorphologyPath(str, Enum):
    """
    المسار الصرفي المُقدَّر قبل إرسال المضيف إلى HR2S.

    كلّ قيمة هي str للتوافق مع to_dict() والمقارنة النصية.

    VERBAL_ROOT_PATH:
        شواهد واضحة للفعل: بادئة مضارع (يَ/تَ/نَ/أَ) + بنية ثلاثية،
        أو تاء التأنيث الساكنة (فَعَلَتْ)، أو COMPRESSED_VERB_CANDIDATE.

    NOMINAL_MORPHOLOGY_PATH:
        شواهد اسمية صريحة: تنوين رفع/نصب/جر، تاء التأنيث المربوطة بإعراب،
        مثنى، جمع مذكر سالم، جمع مؤنث سالم.

    DERIVED_NOMINAL_PATH:
        مشتق اسمي يمكن أن يحمل جذرًا: مصدر، صفة مشبهة، اسم مفعول/فاعل.
        (يُستنتج من بنية الحركات دون تحديد الوزن)

    FUNCTIONAL_PATH:
        كلمة وظيفية مؤكدة (inventory hit: CLOSED_FUNCTION_WORD أو
        POSSIBLE_FUNCTION_WORD).

    AMBIGUOUS_MORPHOLOGY_PATH:
        لا يمكن الحسم بنيويًا — تباس في البادئة أو غياب شواهد كافية.
        → يُنتج DEFER في القرار النهائي.

    NO_MORPHOLOGY_PATH:
        بنية غير صالحة للتحليل الصرفي (UNDERLICENSED_SHORT_SURFACE، فارغة).
    """

    VERBAL_ROOT_PATH          = "verbal_root_path"
    NOMINAL_MORPHOLOGY_PATH   = "nominal_morphology_path"
    DERIVED_NOMINAL_PATH      = "derived_nominal_path"
    FUNCTIONAL_PATH           = "functional_path"
    AMBIGUOUS_MORPHOLOGY_PATH = "ambiguous_morphology_path"
    NO_MORPHOLOGY_PATH        = "no_morphology_path"


# ══════════════════════════════════════════════════════════════════════════════
# 2.  ثوابت بنيوية — بدون استثناءات كلمات
# ══════════════════════════════════════════════════════════════════════════════

# بادئات المضارع (الحرف + الفتحة) — شاهد على VERBAL_ROOT_PATH
# لا تُستخدم الحروف وحدها لأن ي/ت/ن تظهر في أسماء أيضًا
_MUDARIC_PREFIX_PAIRS: frozenset[str] = frozenset({
    'يَ', 'تَ', 'نَ', 'أَ',   # مع فتحة
    'يُ', 'تُ', 'نُ', 'أُ',   # مع ضمة (مبني للمجهول)
})

# لواحق تاء التأنيث الساكنة في الماضي — شاهد على VERBAL_ROOT_PATH
_VERBAL_FEMININE_TAILS: tuple[str, ...] = ('تْ',)

# لواحق اسمية صريحة — شاهد على NOMINAL_MORPHOLOGY_PATH
# (تاء تأنيث + إعراب، مثنى، جمع سالم)
_NOMINAL_TAILS: tuple[str, ...] = (
    'ةً', 'ةٌ', 'ةِ', 'ةُ',   # تاء التأنيث المربوطة بإعراب
    'انِ', 'انُ',               # مثنى رفع
    'يْنِ',                     # مثنى جر/نصب
    'ونَ', 'ينَ',               # جمع مذكر سالم
    'اتٌ', 'اتِ', 'اتُ', 'اتً',  # جمع مؤنث سالم
)

# حركات التنوين — شاهد على الاسمية إذا كانت في نهاية الكلمة
_TANWIN_CHARS: frozenset[str] = frozenset('ًٌٍ')

# ألف المد الداخلي — شاهد على الجمع الكسري (أَفْعَالُ)
_ALEF_PLAIN: str = 'ا'   # U+0627 — ألف المد (بدون همزة)

# علامات الإعراب القصيرة (رفع أو جر بدون تنوين) — شاهد اسمي
_CASE_MARKERS: frozenset[str] = frozenset('ُِ')   # ضمة وكسرة

# حروف المد التي لا تُعدّ صامتًا بعد بادئة المضارع
# نَوْمِ: نَ + و (مد) → ليس مضارعًا. نَذْهَبُ: نَ + ذ (صامت) → مضارع.
_LONG_VOWEL_LETTERS: frozenset[str] = frozenset('واي')


# ══════════════════════════════════════════════════════════════════════════════
# 3.  المُصنِّف
# ══════════════════════════════════════════════════════════════════════════════

def classify_morphology_path(
    host_surface: str,
    boundary_kind: 'BoundaryKind',
    phones: list | None = None,
) -> MorphologyPath:
    """
    صنّف المسار الصرفي للمضيف بناءً على الشواهد البنيوية.

    يُطبَّق بعد فصل أداة التعريف؛ المدخل هو السطح المُضيف فقط.
    لا تعديل على الجذر، لا باب، لا وزن.

    Parameters
    ----------
    host_surface  : السطح المُضيف (بعد إزالة الـ والسوابق الأخرى)
    boundary_kind : BoundaryKind من boundary/models.py
    phones        : قائمة Phone من cell_builder إن توفرت (اختياري؛ غير مُستخدَم حاليًا)

    Returns
    -------
    MorphologyPath
    """
    from boundary.models import BoundaryKind

    # ── لا سطح — بنية فارغة ──────────────────────────────────────────────────
    if not host_surface:
        return MorphologyPath.NO_MORPHOLOGY_PATH

    # ── كلمة وظيفية مُؤكَّدة من الجرد ─────────────────────────────────────
    if boundary_kind in (
        BoundaryKind.CLOSED_FUNCTION_WORD,
        BoundaryKind.POSSIBLE_FUNCTION_WORD,
    ):
        return MorphologyPath.FUNCTIONAL_PATH

    # ── بنية غير صالحة ──────────────────────────────────────────────────────
    if boundary_kind is BoundaryKind.UNDERLICENSED_SHORT_SURFACE:
        return MorphologyPath.NO_MORPHOLOGY_PATH

    # ── سطح غير فعلي من الجرد ──────────────────────────────────────────────
    if boundary_kind is BoundaryKind.NON_VERBAL_SURFACE:
        return MorphologyPath.NOMINAL_MORPHOLOGY_PATH

    # ── التباس بنيوي — AMBIGUOUS أو CLITICIZED ──────────────────────────────
    if boundary_kind is BoundaryKind.AMBIGUOUS:
        return MorphologyPath.AMBIGUOUS_MORPHOLOGY_PATH

    if boundary_kind is BoundaryKind.CLITICIZED_SURFACE:
        return MorphologyPath.AMBIGUOUS_MORPHOLOGY_PATH

    # ── شاهد 0: جمع كسر (أَفْعَالُ) — قبل أي فحص بادئة ────────────────────
    # يُعطى الأولوية لأن أَ قد تبدأ جمعًا كسريًا لا فعلًا مضارعًا
    if _is_broken_plural_candidate(host_surface):
        return MorphologyPath.NOMINAL_MORPHOLOGY_PATH

    # ── الشواهد الاسمية — قبل فحص البادئة المضارعية ─────────────────────────
    # الأولوية لأن لواحق كـ ينَ / ونَ / اتٌ قاطعة في الاسمية بغض النظر عن البادئة.
    # مثال: نَاءِمِينَ تبدأ بـ نَ (مضارع) لكن تنتهي بـ ينَ (جمع مذكر سالم) → NOMINAL.

    # شاهد 1: لواحق اسمية صريحة
    if _ends_with_nominal_tail(host_surface):
        return MorphologyPath.NOMINAL_MORPHOLOGY_PATH

    # شاهد 2: تنوين في نهاية السطح (كلمة منونة ليست فعلًا)
    if host_surface and host_surface[-1] in _TANWIN_CHARS:
        return MorphologyPath.NOMINAL_MORPHOLOGY_PATH

    # ── الشواهد الفعلية ──────────────────────────────────────────────────────
    # شاهد 3: بادئة مضارع حقيقية (بادئة + صامت لا حرف مد)
    # نَوْمِ: نَ + و (حرف مد) → ليس مضارعًا. نَذْهَبُ: نَ + ذ (صامت) → مضارع.
    if _is_mudaric_surface(host_surface):
        return MorphologyPath.VERBAL_ROOT_PATH

    # شاهد 4: تاء التأنيث الساكنة في نهاية الفعل الماضي (فَعَلَتْ)
    if host_surface.endswith(_VERBAL_FEMININE_TAILS):
        return MorphologyPath.VERBAL_ROOT_PATH

    # شاهد 5: COMPRESSED_VERB_CANDIDATE (قُلْ، قِفْ)
    if boundary_kind is BoundaryKind.COMPRESSED_VERB_CANDIDATE:
        return MorphologyPath.VERBAL_ROOT_PATH

    # ── علامة إعراب قصيرة بلا تنوين — شاهد اسمي ثانوي ─────────────────────
    # بعد استبعاد المضارع والمعلوم الفعلية، الكسرة أو الضمة في النهاية
    # تُرجِّح الاسمية (خَالِدُ، نَوْمِ، أُمِّ، ...).
    if host_surface and host_surface[-1] in _CASE_MARKERS and len(host_surface) >= 4:
        return MorphologyPath.NOMINAL_MORPHOLOGY_PATH

    # ── مرشح للجذر بدون شاهد واضح ──────────────────────────────────────────
    # ROOT_ELIGIBLE وحدها لا تكفي للجزم بالفعلية — HR2S هو من يُحسم الأمر.
    # القرار: AMBIGUOUS — لا VERBAL. (إصلاح: كانت تُعطي VERBAL_ROOT_PATH)
    if boundary_kind is BoundaryKind.ROOT_ELIGIBLE:
        return MorphologyPath.AMBIGUOUS_MORPHOLOGY_PATH

    # ── احتياط ───────────────────────────────────────────────────────────────
    return MorphologyPath.AMBIGUOUS_MORPHOLOGY_PATH


# ══════════════════════════════════════════════════════════════════════════════
# 4.  دوال مساعدة
# ══════════════════════════════════════════════════════════════════════════════

def _ends_with_nominal_tail(surface: str) -> bool:
    """هل ينتهي السطح بلاحقة اسمية معروفة؟"""
    for tail in _NOMINAL_TAILS:
        if surface.endswith(tail):
            return True
    return False


def _is_mudaric_surface(surface: str) -> bool:
    """
    هل يبدأ السطح ببادئة مضارع حقيقية؟

    المضارع الحقيقي = بادئة (يَ/تَ/نَ/أَ + ضمائرها المضمومة) + صامت لا حرف مد.
    نَوْمِ: نَ + و (حرف مد) → False (ليس مضارعًا).
    نَذْهَبُ: نَ + ذ (صامت) → True (مضارع).
    نَاءِمِينَ: نَ + ا (حرف مد) → False (مشتق اسمي).

    القيد: يُطبَّق بعد فحص اللواحق الاسمية لأن اللاحقة الاسمية القاطعة
    (ينَ، ونَ، ...) تتغلب على البادئة في تحديد المسار.

    إصلاح Class C1 (HOKOM-AYAT-AL-DAYN-WORD-CLASS-AND-SUBCLASS-ROUTING-CORRECTION-01):
      حارس 1 — ألف مقصورة في النهاية (ى U+0649):
        الألف المقصورة علامة اسمية أو حرفية حصرًا (أُخْرَى، كُبْرَى، حَتَّى، بَلَى).
        لا يمكن أن تنتهي صيغة فعل مضارع متصرف بألف مقصورة → False.
      حارس 2 — شدّة في الموضع 3 (ّ U+0651) بعد الصامت الأول للجذر:
        النمط أَلَّا / أَلَّمْ / أَلَّ: بادئة (أَ/إِ) + لام + شدّة → حرف لا فعل.
        الأفعال المشددة تضع الشدّة في موضع أبعد (يُفَعِّلُ: الشدّة في موضع 6).
        أَلَّفَ (فعل ثلاثي مزيد ماضٍ) يستوفي هذا الشرط لكن يسلك مسار AMBIGUOUS
        ثم يؤكده Phase4A، فلا خسارة في التصنيف النهائي.
    """
    if len(surface) < 4:
        return False
    if surface[:2] not in _MUDARIC_PREFIX_PAIRS:
        return False
    # حارس 1: ألف مقصورة في النهاية → ليست فعلًا مضارعًا
    if surface[-1] == 'ى':   # ى (alef maqsura)
        return False
    # حارس 2: نمط أَلَّ / إِلَّ — حرف/جسيمة، لا فعل
    # يُغطّي: أَلَّا (أَنْ + لَا)، إِلَّا (حرف استثناء).
    # الشدّة على اللام قد تأتي في الموضع 3 أو 4 حسب ترتيب الحركات في يونيكود،
    # لذلك يُفحَص النطاق surface[2:6] بدلًا من موضع ثابت.
    # القيد: 'أَ'/'إِ' + لام + شدّة — لا يطال 'أَكْتُبُ' أو 'تَرْضَوْنَ'.
    if (len(surface) >= 5
            and surface[:2] in ('أَ', 'إِ')
            and surface[2] == 'ل'
            and 'ّ' in surface[2:6]):
        return False
    # الحرف التالي للبادئة (موضع 2) يجب أن يكون صامتًا (لا حرف مد)
    return surface[2] not in _LONG_VOWEL_LETTERS


def _is_broken_plural_candidate(surface: str) -> bool:
    """
    هل يتطابق السطح مع نمط الجمع الكسري (أَفْعَالُ وأشكاله)؟

    الشواهد البنيوية:
      1. يبدأ بهمزة (أ/إ/ا) — موقع صدر الكلمة في كثير من جموع الكسر
      2. يحتوي ألف مد داخلي (ا) في الموضع 3 أو ما بعده — علامة الجمع الكسري
      3. ينتهي بعلامة إعراب قصيرة (ُ أو ِ) — رفع أو جر بدون تنوين

    لا يلتقط:
      - أَفْعَالَ (فتحة في النهاية — مع مفعول به أو خبر)
      - أَفَعَلَ (فعل ماضٍ رباعي) — ينتهي بفتحة
      - أَفْعَلُ (مضارع I) — لا ألف داخلي

    القانون: لا استثناءات كلمات — فقط الأنماط البنيوية.
    """
    if len(surface) < 5:
        return False
    # يبدأ بهمزة (أ = U+0623، إ = U+0625، ا = U+0627 مع حركة)
    if surface[0] not in ('أ', 'إ', 'ا'):
        return False
    # يحتوي ألف مد داخلي بعد المقطع الأول (موضع ≥ 3)
    if _ALEF_PLAIN not in surface[3:]:
        return False
    # ينتهي بعلامة إعراب قصيرة (ضمة رفع أو كسرة جر)
    if surface[-1] not in _CASE_MARKERS:
        return False
    return True
