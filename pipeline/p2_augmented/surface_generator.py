#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_augmented/surface_generator.py — مولّد السطح للأوزان المزيدة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُنتِج الصيغة السطحية العربية بإحلال حروف الجذر الثلاثي في قوالب الوزن
لأفعال المزيد (Forms II–X).

القانون:
  - الجذور الصحيحة (كل حروفها من الصوامت الأصيلة): إنتاج مباشر HIGH.
  - الجذور المعتلة (حرف علة في الجذر): إنتاج بثقة MEDIUM للأوزان التي
    تحافظ على حرف العلة كصامت (Form II الشدّة تحمي العين)؛ DEFER للباقي.
  - الجذور المضعَّفة (ع==ل): إنتاج بالشدة مباشرة.
  - Form VIII: معالجة إدغام خاص بـ C1.
  - لا تُنتِج شكلًا خاطئًا بثقة ACCEPT: الأفضل None مع DEFER.

واجهة عامة:
  apply_root_to_pattern(pattern, root)        → str | None
  generate_surface(form_family, slot, root)   → (surface, confidence)
  is_sound_root(root)                         → bool
  has_weak_c2(root)                           → bool
  is_geminate(root)                           → bool
"""

from __future__ import annotations

from typing import Optional

# ── حروف عربية ───────────────────────────────────────────────────────────────

# مواضع الجذر في قوالب فَعَلَ
FA  = 'ف'    # C1 الفاء
AIN = 'ع'    # C2 العين
LAM = 'ل'    # C3 اللام

# الحروف الصحيحة (الصوامت الأصيلة)
SOUND_CONSONANTS: frozenset[str] = frozenset(
    'بتثجحخدذرزسشصضطظغفقكلمنه'
)

# حروف العلة الجذرية
WEAK_CONSONANTS: frozenset[str] = frozenset('وي')

# الهمزة وأشكالها
HAMZA_VARIANTS: frozenset[str] = frozenset('ءأإآؤئ')

# ── تصنيف الجذر ─────────────────────────────────────────────────────────────

def is_sound_root(root: tuple) -> bool:
    """
    True إذا كانت جميع حروف الجذر صحيحة أو همزة.
    (الهمزة لها معالجة خاصة لكن تُعتبر صحيحة هنا بالنسبة لمعظم الأوزان.)
    """
    return all(c in SOUND_CONSONANTS or c in HAMZA_VARIANTS for c in root)


def has_weak_c2(root: tuple) -> bool:
    """True إذا كان C2 حرف علة (فعل أجوف)."""
    return len(root) >= 2 and root[1] in WEAK_CONSONANTS


def has_weak_c3(root: tuple) -> bool:
    """True إذا كان C3 حرف علة (فعل ناقص)."""
    return len(root) >= 3 and root[2] in WEAK_CONSONANTS


def is_geminate(root: tuple) -> bool:
    """True إذا كان C2 == C3 (جذر مضعَّف)."""
    return len(root) >= 3 and root[1] == root[2]


# ── قوالب الأوزان المزيدة ─────────────────────────────────────────────────────

# تعيين (عائلة_الصيغة, فئة_المشتق) → قالب الوزن
# القوالب تستخدم ف/ع/ل كرموز للجذر الثلاثي
AUGMENTED_SURFACE_PATTERNS: dict[str, str] = {
    # Form II — فعّل
    'FORM_II_PAST':         'فَعَّلَ',
    'FORM_II_IMPERFECT':    'يُفَعِّلُ',
    'FORM_II_MASDAR':       'تَفْعِيل',
    'FORM_II_ISM_FA3IL':    'مُفَعِّل',
    'FORM_II_ISM_MAF3UL':   'مُفَعَّل',

    # Form III — فاعل
    'FORM_III_PAST':        'فَاعَلَ',
    'FORM_III_IMPERFECT':   'يُفَاعِلُ',
    'FORM_III_MASDAR':      'مُفَاعَلَة',
    'FORM_III_ISM_FA3IL':   'مُفَاعِل',
    'FORM_III_ISM_MAF3UL':  'مُفَاعَل',

    # Form IV — أفعل
    'FORM_IV_PAST':         'أَفْعَلَ',
    'FORM_IV_IMPERFECT':    'يُفْعِلُ',
    'FORM_IV_MASDAR':       'إِفْعَال',
    'FORM_IV_ISM_FA3IL':    'مُفْعِل',
    'FORM_IV_ISM_MAF3UL':   'مُفْعَل',

    # Form V — تفعّل
    'FORM_V_PAST':          'تَفَعَّلَ',
    'FORM_V_IMPERFECT':     'يَتَفَعَّلُ',
    'FORM_V_MASDAR':        'تَفَعُّل',
    'FORM_V_ISM_FA3IL':     'مُتَفَعِّل',
    'FORM_V_ISM_MAF3UL':    'مُتَفَعَّل',

    # Form VI — تفاعل
    'FORM_VI_PAST':         'تَفَاعَلَ',
    'FORM_VI_IMPERFECT':    'يَتَفَاعَلُ',
    'FORM_VI_MASDAR':       'تَفَاعُل',
    'FORM_VI_ISM_FA3IL':    'مُتَفَاعِل',
    'FORM_VI_ISM_MAF3UL':   'مُتَفَاعَل',

    # Form VII — انفعل
    'FORM_VII_PAST':        'اِنْفَعَلَ',
    'FORM_VII_IMPERFECT':   'يَنْفَعِلُ',
    'FORM_VII_MASDAR':      'اِنْفِعَال',
    'FORM_VII_ISM_FA3IL':   'مُنْفَعِل',

    # Form VIII — افتعل
    'FORM_VIII_PAST':       'اِفْتَعَلَ',
    'FORM_VIII_IMPERFECT':  'يَفْتَعِلُ',
    'FORM_VIII_MASDAR':     'اِفْتِعَال',
    'FORM_VIII_ISM_FA3IL':  'مُفْتَعِل',
    'FORM_VIII_ISM_MAF3UL': 'مُفْتَعَل',

    # Form IX — افعلّ
    'FORM_IX_PAST':         'اِفْعَلَّ',
    'FORM_IX_IMPERFECT':    'يَفْعَلُّ',
    'FORM_IX_MASDAR':       'اِفْعِلَال',
    'FORM_IX_ISM_FA3IL':    'مُفْعَلّ',

    # Form X — استفعل
    'FORM_X_PAST':          'اِسْتَفْعَلَ',
    'FORM_X_IMPERFECT':     'يَسْتَفْعِلُ',
    'FORM_X_MASDAR':        'اِسْتِفْعَال',
    'FORM_X_ISM_FA3IL':     'مُسْتَفْعِل',
    'FORM_X_ISM_MAF3UL':    'مُسْتَفْعَل',
}


# ── Form VIII — قواعد الإدغام ─────────────────────────────────────────────────

# C1 ∈ {و, ي} → تاء الافتعال تدغم: اِتَّصَلَ (و-ص-ل), اِتَّعَظَ (و-ع-ظ)
_FORM_VIII_WAW_YAA_ASSIMILATION: frozenset[str] = frozenset('وي')

# C1 ∈ {ز} → اِزْدَ... : اِزْدَهَرَ (ز-ه-ر)
_FORM_VIII_ZAY_ASSIMILATION: frozenset[str] = frozenset({'ز'})

# C1 ∈ {ذ,د,ض,ط,ظ} → إدغام أصعب (محجوز للمستقبل)
_FORM_VIII_EMPHATIC_C1: frozenset[str] = frozenset('ذدضطظ')


def apply_form_viii(root: tuple) -> tuple[Optional[str], str]:
    """
    أنتِج صيغة ماضي Form VIII مع الإدغام الصحيح.

    Returns:
        (surface, confidence) — surface=None عند الإدغام المعقد.
    """
    if len(root) != 3:
        return None, 'DEFER'

    C1, C2, C3 = root

    # إدغام و/ي → تاء مشددة
    if C1 in _FORM_VIII_WAW_YAA_ASSIMILATION:
        surface = f'اِتَّ{C2}َ{C3}َ'
        return surface, 'HIGH'

    # إدغام ز → اِزْدَ
    if C1 in _FORM_VIII_ZAY_ASSIMILATION:
        surface = f'اِزْدَ{C2}َ{C3}َ'
        return surface, 'HIGH'

    # إدغام الأصوات التفخيمية — معقد، يُؤجَّل
    if C1 in _FORM_VIII_EMPHATIC_C1:
        return None, 'MEDIUM'

    # المعتاد: اِ + C1 + ْتَ + C2 + َ + C3 + َ
    surface = f'اِ{C1}ْتَ{C2}َ{C3}َ'
    return surface, 'HIGH'


# ── الإحلال الأساسي ──────────────────────────────────────────────────────────

def apply_root_to_pattern(
    pattern: str,
    root: tuple,
) -> Optional[str]:
    """
    أحلِل حروف الجذر (C1,C2,C3) في قالب وزن فَعَلَ.

    يُعيد السطح الناتج، أو None إذا كان التحويل غير آمن.

    ملاحظة:
      - يُحلِّل ف→C1، ع→C2، ل→C3 مباشرةً.
      - لا يعالج الإعلال (إعلال الجذر الأجوف أو الناقص): المُتصرِّف
        يعود بـ None عند الحاجة إلى إعلال.
      - الهمزة في C1 مع الأوزان التي تبدأ بـ أ- أو إ- قد تُنتِج
        همزتين متتاليتين؛ يُعالَج في generate_surface().
    """
    if len(root) != 3:
        return None

    C1, C2, C3 = root
    result = []
    for ch in pattern:
        if ch == FA:
            result.append(C1)
        elif ch == AIN:
            result.append(C2)
        elif ch == LAM:
            result.append(C3)
        else:
            result.append(ch)
    return ''.join(result)


# ── توليد السطح حسب العائلة والفئة ──────────────────────────────────────────

def generate_surface(
    form_family: str,
    slot: str,
    root: tuple,
) -> tuple[Optional[str], str]:
    """
    أنتِج الصيغة السطحية للجذر في عائلة الصيغة والفئة المحددة.

    Args:
        form_family : 'FORM_II' | 'FORM_III' | ... | 'FORM_X'
        slot        : 'PAST' | 'IMPERFECT' | 'MASDAR' | 'ISM_FA3IL' | 'ISM_MAF3UL'
        root        : (C1, C2, C3) — حروف الجذر بلا حركات

    Returns:
        (surface, confidence)
          surface    : السطح المولَّد أو None
          confidence : 'HIGH' | 'MEDIUM' | 'DEFER'

    الحالات الخاصة:
      - Form VIII ماضٍ: معالجة الإدغام عبر apply_form_viii().
      - جذور معتلة C2: DEFER للأوزان التي تتطلب إعلالًا؛ HIGH لـ Form II
        التي تحافظ على العلة بالشدة.
      - جذور مضعَّفة: إنتاج مباشر مع HIGH (الشدة تُدرج ضمنيًا في القالب).
      - جذور بهمزة: توليد مع HIGH (الهمزة تُكتب كما هي في C1).
    """
    if len(root) != 3:
        return None, 'DEFER'

    C1, C2, C3 = root

    # ── Form VIII ماضٍ: إدغام خاص ────────────────────────────────────────
    if form_family == 'FORM_VIII' and slot == 'PAST':
        return apply_form_viii(root)

    # ── ابحث في القاموس عن القالب ────────────────────────────────────────
    key = f'{form_family}_{slot}'
    pattern = AUGMENTED_SURFACE_PATTERNS.get(key)
    if pattern is None:
        return None, 'DEFER'

    # ── Form II مع عين معتلة: الشدة تُثبِّت العلة → HIGH ─────────────────
    # في فَعَّلَ، العين مُشددة فتبقى صامتًا حتى لو كانت و/ي.
    # مثال: قَوَّمَ (ق-و-م)، سَيَّرَ (س-ي-ر) — صحيح بلا إعلال.
    weak_c2 = C2 in WEAK_CONSONANTS
    weak_c3 = C3 in WEAK_CONSONANTS

    if weak_c2:
        if form_family in ('FORM_II', 'FORM_III'):
            # Form II/III: C2 تبقى صامتًا في معظم الصيغ
            confidence = 'MEDIUM'
        elif form_family == 'FORM_IV' and slot in ('MASDAR',):
            # إِفْعَال مع جذر أجوف → إِفَالَة بإعلال معقد → DEFER
            return None, 'DEFER'
        else:
            # الأوزان الأخرى مع عين معتلة → تتطلب إعلالًا → DEFER
            return None, 'DEFER'
    elif weak_c3:
        # الجذور الناقصة تتطلب تعاملًا خاصًا
        confidence = 'MEDIUM'
    else:
        confidence = 'HIGH'

    surface = apply_root_to_pattern(pattern, root)
    return surface, confidence


# ── دالة مساعدة: الحصول على قالب عائلة+فئة ─────────────────────────────────

def get_pattern(form_family: str, slot: str) -> Optional[str]:
    """أعِد قالب الوزن لعائلة وفئة محددة، أو None."""
    return AUGMENTED_SURFACE_PATTERNS.get(f'{form_family}_{slot}')
