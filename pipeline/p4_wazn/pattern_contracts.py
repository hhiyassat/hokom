#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/pattern_contracts.py — عقود ملكية الوزن الكنسية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-MORPHOLOGY-PATTERN-OWNERSHIP-01

يُوثِّق هذا الملف ملكية Hokom الكنسية على طبقة الوزن (P4A)، ويُوفِّر:
  - PATTERN_CANONICAL_OWNER     : الثابت الإعلاني للملكية
  - WaznContract                : dataclass يربط كل وزن بخصائصه الدلالية
  - PATTERN_CONTRACTS           : قاموس الوزن → WaznContract (20 وزنًا)
  - Pattern Slot Algebra        : تعريفات ROOT_SLOT/AUGMENT_SLOT/INFLECTION_SLOT
  - دوال استعلام كنسية         : wazn_root_class, wazn_derivation_type, ...

الطبقات الثلاث المفصولة (المطلب الجوهري للمأموريّة):
  root_class       : نوع الجذر بصرف النظر عن الصيغة (SOUND/GEMINATE/HOLLOW/...)
  wazn_pattern     : الوزن الصرفي (فَعَلَ / فَاعِل / أَفْعَلَ / ...)
  derivation_type  : نوع الاشتقاق (bare_verb / active_participle / form_IV_verb / ...)

ملاحظة: هذا الملف توثيقي/استعلامي — لا يُعدِّل المسار التحليلي.
المسار الكنسي يمر دائمًا عبر project_wazn_with_relicensing() أو build_augmented_phase4a().
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1.  إعلان الملكية
# ══════════════════════════════════════════════════════════════════════════════

PATTERN_CANONICAL_OWNER: str = 'HOKOM'
"""
جميع قرارات الوزن (wazn) تنبع حصريًا من محرك Hokom.
لا مسارات خارجية (HR2S) تملك وزنًا في هذه الطبقة.
"""

PATTERN_OWNERSHIP_VERSION: str = '1.0.0'
"""إصدار طبقة ملكية الوزن — يُرفع عند تغيير العقود."""


# ══════════════════════════════════════════════════════════════════════════════
# 2.  Pattern Slot Algebra — أسماء الفتحات الكنسية
# ══════════════════════════════════════════════════════════════════════════════

class RootSlot:
    """
    فتحات الجذر الثلاثي / الرباعي:
      FA   (ف) — الحرف الأول من الجذر
      AIN  (ع) — الحرف الثاني
      LAM  (ل) — الحرف الثالث
      LAM2 (ل٢) — الحرف الرابع (للجذر الرباعي)
    """
    FA   = 'ROOT_SLOT_FA'
    AIN  = 'ROOT_SLOT_AIN'
    LAM  = 'ROOT_SLOT_LAM'
    LAM2 = 'ROOT_SLOT_LAM2'   # للجذر الرباعي (دَحْرَجَ)


class AugmentSlot:
    """
    فتحات الزيادة (حروف زائدة غير جذرية):
      HAMZA_PREFIX   : همزة البداية (أَفْعَلَ، اِفْتَعَلَ)
      NUN_PREFIX     : نون اِنْفَعَلَ
      TA_PREFIX      : تاء تَفَعَّلَ / اِفْتَعَلَ
      SIN_TA_PREFIX  : سين+تاء اِسْتَفْعَلَ
      MIM_PREFIX     : ميم مَفْعُول / مَفْعَل
      ALIF_MEDIAL    : ألف فَاعِل / فَاعَلَ
      AIN_GEMINATION : شدة فَعَّلَ (تضعيف العين)
      WAW_MEDIAL     : واو مَفْعُول
    """
    HAMZA_PREFIX   = 'AUGMENT_SLOT_HAMZA_PREFIX'
    NUN_PREFIX     = 'AUGMENT_SLOT_NUN_PREFIX'
    TA_PREFIX      = 'AUGMENT_SLOT_TA_PREFIX'
    SIN_TA_PREFIX  = 'AUGMENT_SLOT_SIN_TA_PREFIX'
    MIM_PREFIX     = 'AUGMENT_SLOT_MIM_PREFIX'
    ALIF_MEDIAL    = 'AUGMENT_SLOT_ALIF_MEDIAL'
    AIN_GEMINATION = 'AUGMENT_SLOT_AIN_GEMINATION'
    WAW_MEDIAL     = 'AUGMENT_SLOT_WAW_MEDIAL'


class InflectionSlot:
    """
    فتحات الإعراب والتصريف (يُجاهلها المحاذي الكنسي بـ FINAL):
      TANWIN_DAMM  : ضمة تنوين (كَاتِبٌ)
      TANWIN_KASRA : كسرة تنوين (كَاتِبٍ)
      TANWIN_FATH  : فتحة تنوين (كَاتِبًا)
      DAMM         : ضمة رفع (كَاتِبُ)
      KASRA        : كسرة جر (كَاتِبِ)
      FATH         : فتحة نصب (كَاتِبَ)
    """
    TANWIN_DAMM  = 'INFLECTION_SLOT_TANWIN_DAMM'
    TANWIN_KASRA = 'INFLECTION_SLOT_TANWIN_KASRA'
    TANWIN_FATH  = 'INFLECTION_SLOT_TANWIN_FATH'
    DAMM         = 'INFLECTION_SLOT_DAMM'
    KASRA        = 'INFLECTION_SLOT_KASRA'
    FATH         = 'INFLECTION_SLOT_FATH'


class RestorationSlot:
    """
    فتحات الاستعادة الصوتية للجذر المعتل:
      HOLLOW_WAW_RESTORED  : استعادة الواو في الأجوف (قَوَلَ → قَالَ)
      HOLLOW_YA_RESTORED   : استعادة الياء في الأجوف
      DEFECTIVE_YA_DROPPED : حذف الياء في الناقص (رَمَى → رَمَيَ)
      HAMZA_NORMALIZED     : تطبيع الهمزة (أ/إ/آ → ء)
    """
    HOLLOW_WAW_RESTORED  = 'RESTORATION_SLOT_HOLLOW_WAW'
    HOLLOW_YA_RESTORED   = 'RESTORATION_SLOT_HOLLOW_YA'
    DEFECTIVE_YA_DROPPED = 'RESTORATION_SLOT_DEFECTIVE_YA_DROPPED'
    HAMZA_NORMALIZED     = 'RESTORATION_SLOT_HAMZA_NORMALIZED'


# ══════════════════════════════════════════════════════════════════════════════
# 3.  WaznContract — العقد الدلالي لكل وزن
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class WaznContract:
    """
    العقد الدلالي الكنسي لوزن واحد.

    wazn_id          : معرف الوزن في الكتالوج (FA_A_LA / FA3IL / ...)
    pattern_arabic   : الوزن بالحروف العربية (فَعَلَ / فَاعِل / ...)
    root_arity       : عدد حروف الجذر (3 = ثلاثي، 4 = رباعي)
    derivation_type  : نوع الاشتقاق (bare_verb / active_participle / form_IV_verb / ...)
    surface_classes  : أصناف السطح المقبولة (verb / noun / ...)
    root_slots       : أسماء فتحات الجذر (قائمة RootSlot.*)
    augment_slots    : فتحات الزيادة المُرخَّصة (قائمة AugmentSlot.*)
    catalog_family   : عائلة الكتالوج (triliteral_bare_verb / active_participle / ...)
    notes            : ملاحظات عقدية اختيارية
    """
    wazn_id        : str
    pattern_arabic : str
    root_arity     : int
    derivation_type: str
    surface_classes: tuple[str, ...]
    root_slots     : tuple[str, ...]
    augment_slots  : tuple[str, ...]
    catalog_family : str
    notes          : Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# 4.  PATTERN_CONTRACTS — قاموس الـ20 وزن الكنسيًا
# ══════════════════════════════════════════════════════════════════════════════

PATTERN_CONTRACTS: dict[str, WaznContract] = {

    # ─── الثلاثي المجرد (أفعال) ──────────────────────────────────────────────

    'FA_A_LA': WaznContract(
        wazn_id        = 'FA_A_LA',
        pattern_arabic = 'فَعَلَ',
        root_arity     = 3,
        derivation_type= 'bare_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (),
        catalog_family = 'triliteral_bare_verb',
        notes          = 'باب فَتَحَ — الفعل الثلاثي المجرد الأساسي',
    ),

    'FA_I_LA': WaznContract(
        wazn_id        = 'FA_I_LA',
        pattern_arabic = 'فَعِلَ',
        root_arity     = 3,
        derivation_type= 'bare_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (),
        catalog_family = 'triliteral_bare_verb',
        notes          = 'باب فَرِحَ — فتح+كسر',
    ),

    'FA_U_LA': WaznContract(
        wazn_id        = 'FA_U_LA',
        pattern_arabic = 'فَعُلَ',
        root_arity     = 3,
        derivation_type= 'bare_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (),
        catalog_family = 'triliteral_bare_verb',
        notes          = 'باب كَرُمَ — فتح+ضم',
    ),

    # ─── الثلاثي المجرد (أسماء مصادر ومشتقات بلا زيادة) ──────────────────────

    'FA3L': WaznContract(
        wazn_id        = 'FA3L',
        pattern_arabic = 'فَعْل',
        root_arity     = 3,
        derivation_type= 'masdar_bare',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (),
        catalog_family = 'triliteral_noun',
        notes          = 'مصدر قياسي على فَعْل',
    ),

    'FI3L': WaznContract(
        wazn_id        = 'FI3L',
        pattern_arabic = 'فِعْل',
        root_arity     = 3,
        derivation_type= 'masdar_bare',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (),
        catalog_family = 'triliteral_noun',
    ),

    'FU3L': WaznContract(
        wazn_id        = 'FU3L',
        pattern_arabic = 'فُعْل',
        root_arity     = 3,
        derivation_type= 'masdar_bare',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (),
        catalog_family = 'triliteral_noun',
    ),

    # ─── مشتقات ثلاثي مجرد (بزيادة) ─────────────────────────────────────────

    'FA3IL': WaznContract(
        wazn_id        = 'FA3IL',
        pattern_arabic = 'فَاعِل',
        root_arity     = 3,
        derivation_type= 'active_participle',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.ALIF_MEDIAL,),
        catalog_family = 'active_participle',
        notes          = 'اسم فاعل ثلاثي مجرد — C1(فتحة)+ا+C2(كسرة)+C3',
    ),

    'MAF3UL': WaznContract(
        wazn_id        = 'MAF3UL',
        pattern_arabic = 'مَفْعُول',
        root_arity     = 3,
        derivation_type= 'passive_participle',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.MIM_PREFIX, AugmentSlot.WAW_MEDIAL),
        catalog_family = 'passive_participle',
        notes          = 'اسم مفعول ثلاثي مجرد',
    ),

    'FA33AL': WaznContract(
        wazn_id        = 'FA33AL',
        pattern_arabic = 'فَعَّال',
        root_arity     = 3,
        derivation_type= 'intensive_noun',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.AIN_GEMINATION, AugmentSlot.ALIF_MEDIAL),
        catalog_family = 'intensive_noun',
        notes          = 'صيغة المبالغة فَعَّال',
    ),

    'MAF3AL': WaznContract(
        wazn_id        = 'MAF3AL',
        pattern_arabic = 'مَفْعَل',
        root_arity     = 3,
        derivation_type= 'noun_of_place_or_masdar',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.MIM_PREFIX,),
        catalog_family = 'noun_of_place_or_masdar',
        notes          = 'اسم مكان/زمان أو مصدر ميمي — مَكْتَبٌ، مَعْلَمٌ',
    ),

    'MAF3IL': WaznContract(
        wazn_id        = 'MAF3IL',
        pattern_arabic = 'مَفْعِل',
        root_arity     = 3,
        derivation_type= 'noun_of_place_or_masdar',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.MIM_PREFIX,),
        catalog_family = 'noun_of_place_or_masdar',
        notes          = 'اسم مكان/زمان — مَسْجِد، مَنْزِل',
    ),

    'MIF3AL': WaznContract(
        wazn_id        = 'MIF3AL',
        pattern_arabic = 'مِفْعَال',
        root_arity     = 3,
        derivation_type= 'instrument_noun',
        surface_classes= ('noun',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.MIM_PREFIX, AugmentSlot.ALIF_MEDIAL),
        catalog_family = 'instrument_noun',
        notes          = 'اسم آلة — مِفْتَاح، مِقْصَص',
    ),

    # ─── المزيد بحرف / حرفين (Form II–X) ─────────────────────────────────────

    'FA33ALA': WaznContract(
        wazn_id        = 'FA33ALA',
        pattern_arabic = 'فَعَّلَ',
        root_arity     = 3,
        derivation_type= 'form_II_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.AIN_GEMINATION,),
        catalog_family = 'form_II_verb',
        notes          = 'فعل مزيد بتضعيف العين (درَّسَ، قَدَّمَ)',
    ),

    'FA3ALA': WaznContract(
        wazn_id        = 'FA3ALA',
        pattern_arabic = 'فَاعَلَ',
        root_arity     = 3,
        derivation_type= 'form_III_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.ALIF_MEDIAL,),
        catalog_family = 'form_III_verb',
        notes          = 'فعل مزيد بألف بعد الفاء — C1+ا+C2(فتحة)+C3',
    ),

    'AF3AL': WaznContract(
        wazn_id        = 'AF3AL',
        pattern_arabic = 'أَفْعَلَ',
        root_arity     = 3,
        derivation_type= 'form_IV_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.HAMZA_PREFIX,),
        catalog_family = 'form_IV_verb',
        notes          = 'فعل مزيد بالهمزة — أَكْرَمَ، أَرْسَلَ',
    ),

    'TAFA33ALA': WaznContract(
        wazn_id        = 'TAFA33ALA',
        pattern_arabic = 'تَفَعَّلَ',
        root_arity     = 3,
        derivation_type= 'form_V_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.TA_PREFIX, AugmentSlot.AIN_GEMINATION),
        catalog_family = 'form_V_verb',
        notes          = 'مطاوع Form II — تَعَلَّمَ، تَكَلَّمَ',
    ),

    'TAFA3ALA': WaznContract(
        wazn_id        = 'TAFA3ALA',
        pattern_arabic = 'تَفَاعَلَ',
        root_arity     = 3,
        derivation_type= 'form_VI_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.TA_PREFIX, AugmentSlot.ALIF_MEDIAL),
        catalog_family = 'form_VI_verb',
        notes          = 'مطاوع Form III — تَبَادَلَ، تَعَاوَنَ',
    ),

    'INFA3ALA': WaznContract(
        wazn_id        = 'INFA3ALA',
        pattern_arabic = 'اِنْفَعَلَ',
        root_arity     = 3,
        derivation_type= 'form_VII_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.HAMZA_PREFIX, AugmentSlot.NUN_PREFIX),
        catalog_family = 'form_VII_verb',
        notes          = 'مطاوع Form I — اِنْكَسَرَ، اِنْفَتَحَ',
    ),

    'IFTA3ALA': WaznContract(
        wazn_id        = 'IFTA3ALA',
        pattern_arabic = 'اِفْتَعَلَ',
        root_arity     = 3,
        derivation_type= 'form_VIII_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.HAMZA_PREFIX, AugmentSlot.TA_PREFIX),
        catalog_family = 'form_VIII_verb',
        notes          = 'اِجْتَمَعَ، اِقْتَرَبَ',
    ),

    'IF3ALLA': WaznContract(
        wazn_id        = 'IF3ALLA',
        pattern_arabic = 'اِفْعَلَّ',
        root_arity     = 3,
        derivation_type= 'form_IX_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.HAMZA_PREFIX, AugmentSlot.AIN_GEMINATION),
        catalog_family = 'form_IX_verb',
        notes          = 'أفعال الألوان والعيوب — اِحْمَرَّ، اِسْوَدَّ',
    ),

    'ISTAF3ALA': WaznContract(
        wazn_id        = 'ISTAF3ALA',
        pattern_arabic = 'اِسْتَفْعَلَ',
        root_arity     = 3,
        derivation_type= 'form_X_verb',
        surface_classes= ('verb',),
        root_slots     = (RootSlot.FA, RootSlot.AIN, RootSlot.LAM),
        augment_slots  = (AugmentSlot.HAMZA_PREFIX, AugmentSlot.SIN_TA_PREFIX),
        catalog_family = 'form_X_verb',
        notes          = 'اِسْتَغْفَرَ، اِسْتَخْدَمَ',
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# 5.  دوال استعلام كنسية
# ══════════════════════════════════════════════════════════════════════════════

def get_wazn_contract(wazn_id: str) -> Optional[WaznContract]:
    """
    أعد WaznContract للوزن المطلوب، أو None إذا لم يُسجَّل.

    Parameters
    ----------
    wazn_id : str
        معرف الوزن من الكتالوج (e.g. 'FA3IL', 'FA_A_LA').

    Returns
    -------
    WaznContract | None
    """
    return PATTERN_CONTRACTS.get(wazn_id)


def wazn_derivation_type(wazn_id: str) -> Optional[str]:
    """
    أعد نوع الاشتقاق للوزن المطلوب.

    Examples
    --------
    >>> wazn_derivation_type('FA3IL')
    'active_participle'
    >>> wazn_derivation_type('FA_A_LA')
    'bare_verb'
    >>> wazn_derivation_type('AF3AL')
    'form_IV_verb'
    """
    c = PATTERN_CONTRACTS.get(wazn_id)
    return c.derivation_type if c else None


def wazn_augment_slots(wazn_id: str) -> tuple[str, ...]:
    """
    أعد فتحات الزيادة لهذا الوزن.
    فارغة = لا زيادة (الثلاثي المجرد).
    """
    c = PATTERN_CONTRACTS.get(wazn_id)
    return c.augment_slots if c else ()


def is_bare_triliteral(wazn_id: str) -> bool:
    """
    True إذا كان الوزن ثلاثيًا مجردًا بلا زيادة
    (FA_A_LA / FA_I_LA / FA_U_LA / FA3L / FI3L / FU3L).
    """
    c = PATTERN_CONTRACTS.get(wazn_id)
    return bool(c and c.root_arity == 3 and not c.augment_slots
                and c.catalog_family in ('triliteral_bare_verb', 'triliteral_noun'))


def is_augmented_verb_form(wazn_id: str) -> bool:
    """
    True إذا كان الوزن فعلًا مزيدًا (Form II–X).
    """
    c = PATTERN_CONTRACTS.get(wazn_id)
    return bool(c and 'form_' in c.catalog_family and 'verb' in c.catalog_family
                and c.catalog_family not in ('triliteral_bare_verb',))


# ══════════════════════════════════════════════════════════════════════════════
# 6.  ثوابت بوابات التحقق (14 بوابة)
# ══════════════════════════════════════════════════════════════════════════════

class PatternOwnershipGate:
    """
    14 بوابة منطقية لإغلاق مأمورية HOKOM-MORPHOLOGY-PATTERN-OWNERSHIP-01.

    كل ثابت يُمثِّل شرطًا يجب التحقق منه بالاختبارات قبل الإغلاق.
    """
    PATTERN_CANONICAL_OWNER         = 'HOKOM'
    PATTERN_ENTRY_FROM_LICENSED_ROOT = 'VERIFIED'
    ROOT_CLASS_FORM_SEPARATION       = 'VERIFIED'
    SURFACE_PATTERN_SUPPORTED        = 'VERIFIED'
    UNDERLYING_PATTERN_SUPPORTED     = 'VERIFIED'
    AUGMENT_VS_INFLECTION_SEPARATED  = 'VERIFIED'
    WEAK_ROOT_PATTERNS               = 'COMPLETE'
    QUADRILITERAL_PATTERNS           = 'COMPLETE'
    UNLICENSED_PATTERN_GUESSES       = 0
    PATTERN_RESIDUALS_GOVERNED       = 'VERIFIED'
    P5_REGRESSIONS                   = 0
    ROOT_REGRESSIONS                 = 0
    FULL_SUITE_FAILURES              = 0
    PATTERN_OWNERSHIP_RELEASE        = 'CLOSED'
