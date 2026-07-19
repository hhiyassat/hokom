#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_candidate/root_contracts.py — عقود الجذر الكنسية
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُعرِّف هذا الملف العقود الرسمية لمسار الجذر من P5 إلى الإغلاق.

العقود العشرة (HOKOM-MORPHOLOGY-ROOT-OWNERSHIP-01):

  1. SurfaceToken           — السطح الأصلي + المُطبَّع + الأجرد
  2. LicensedMorphologyInput — المدخل المرخَّص من P5 (MabniOpen فقط)
  3. MorphologicalStem      — المضيف بعد pre_root + root_host_refinement
  4. RadicalSlot            — موضع واحد في الجذر (FA/AYN/LAM + هوية)
  5. RootCandidate          — مرشح جذر واحد مع شواهد ومسار (موجود في root_candidate.py)
  6. RestoredRootCandidate  — مرشح مع عمليات استعادة مُسجَّلة
  7. LicensedRoot           — نتيجة نهائية ACCEPT مع جذر كامل
  8. DeferredRoot           — نتيجة نهائية DEFER مع سبب مُسمَّى
  9. BlockedRoot             — نتيجة نهائية BLOCK مع مانع قاطع
  10. RootResidual           — بقية مسماة قابلة للتطوير اللاحق

القانون المعماري:
  - هذا الملف يُعرِّف فقط — لا يستورد أي وحدة pipeline خارج p3_candidate.
  - الاستيراد الوحيد المسموح: stdlib (dataclasses, typing).
  - كل عقد مُجمَّد (frozen=True).
  - كل عقد يحمل to_dict() للتسلسل.

الثلاثة المحظورات العقدية:
  [C1] ثلاثة أحرف سطحية ≠ جذر (الهوية السطحية لا تُساوي الهوية الجذرية)
  [C2] stem ≠ root (المضيف ليس الجذر — الاستعادة مطلوبة)
  [C3] أول مرشح ≠ الحكم النهائي (الترتيب لا يُعطي الأولوية)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# الثوابت المشتركة
# ══════════════════════════════════════════════════════════════════════════════

# أدوار المواضع الجذرية
RADICAL_POSITION_FA  = 'FA'
RADICAL_POSITION_AYN = 'AYN'
RADICAL_POSITION_LAM = 'LAM'

# النتائج النهائية المسموحة
ROOT_VERDICT_ACCEPT   = 'ACCEPT'
ROOT_VERDICT_DEFER    = 'DEFER'
ROOT_VERDICT_BLOCK    = 'BLOCK'
ROOT_VERDICT_RESIDUAL = 'RESIDUAL'

# أنواع الجذور المدعومة في هذه الدفعة
ROOT_TYPE_SOUND    = 'sound'       # صحيح سالم
ROOT_TYPE_GEMINATE = 'geminate'    # مضعَّف
ROOT_TYPE_HAMZA_FA  = 'hamza_fa'  # مهموز الفاء
ROOT_TYPE_HAMZA_AYN = 'hamza_ayn' # مهموز العين
ROOT_TYPE_HAMZA_LAM = 'hamza_lam' # مهموز اللام
ROOT_TYPE_ASSIMILATED     = 'assimilated'      # مثال (فاء ضعيفة) — مُؤجَّل
ROOT_TYPE_HOLLOW_WAW      = 'hollow_waw'       # أجوف واوي — مُؤجَّل
ROOT_TYPE_HOLLOW_YAA      = 'hollow_yaa'       # أجوف يائي — مُؤجَّل
ROOT_TYPE_HOLLOW_UNKNOWN  = 'hollow_unknown'   # أجوف مجهول العين — مُؤجَّل
ROOT_TYPE_DEFECTIVE_WAW   = 'defective_waw'    # ناقص واوي — مُؤجَّل
ROOT_TYPE_DEFECTIVE_YAA   = 'defective_yaa'    # ناقص يائي — مُؤجَّل
ROOT_TYPE_DEFECTIVE_ALIF  = 'defective_alif'   # ناقص بألف مقصورة — مُؤجَّل
ROOT_TYPE_LAFIF_MAFRUQ    = 'lafif_mafruq'     # لفيف مفروق (فاء+لام ضعيفتان) — مُؤجَّل
ROOT_TYPE_LAFIF_MAQRUN    = 'lafif_maqrun'     # لفيف مقرون (عين+لام ضعيفتان) — مُؤجَّل
ROOT_TYPE_QUADRILATERAL   = 'quadrilateral'    # رباعي أصلي — خارج النطاق الحالي
ROOT_TYPE_UNKNOWN         = 'unknown'           # غير محدد

# رموز التحفظ القياسية
RESIDUAL_INSUFFICIENT_CONSONANTS = 'block:root:insufficient_consonants'
RESIDUAL_HOLLOW_UNRESOLVED       = 'defer:root:hollow_underlying_radical_unresolved'
RESIDUAL_DEFECTIVE_UNRESOLVED    = 'defer:root:defective_lam_unresolved'
RESIDUAL_ASSIMILATED_UNRESOLVED  = 'defer:root:assimilated_fa_unresolved'
RESIDUAL_LAFIF_MAFRUQ_UNRESOLVED = 'defer:root:lafif_mafruq_unresolved'
RESIDUAL_LAFIF_MAQRUN_UNRESOLVED = 'defer:root:lafif_maqrun_unresolved'
RESIDUAL_COMPRESSED_UNRESOLVED   = 'defer:root:two_consonant_form_unresolved'
RESIDUAL_QUADRILATERAL_SCOPE     = 'defer:root:quadriliteral_beyond_scope'
RESIDUAL_NON_STANDARD            = 'defer:root:non_standard_consonant_count'
RESIDUAL_PROHIBITED_RADICAL      = 'defer:root:prohibited_or_ambiguous_radical'
RESIDUAL_PRE_ROOT_DEFER          = 'defer:root:pre_root_directive_defer'

# عمليات الاستعادة المسموحة
RESTORATION_OP_RESTORE_HOLLOW_WAW      = 'RESTORE_HOLLOW_MEDIAL_WAW'
RESTORATION_OP_RESTORE_HOLLOW_YAA      = 'RESTORE_HOLLOW_MEDIAL_YAA'
RESTORATION_OP_RESTORE_DEFECTIVE_WAW   = 'RESTORE_DEFECTIVE_FINAL_WAW'
RESTORATION_OP_RESTORE_DEFECTIVE_YAA   = 'RESTORE_DEFECTIVE_FINAL_YAA'
RESTORATION_OP_RESTORE_INITIAL_WEAK    = 'RESTORE_INITIAL_WEAK_RADICAL'
RESTORATION_OP_EXPAND_GEMINATION       = 'EXPAND_GEMINATION'
RESTORATION_OP_RESTORE_COMPRESSED_IMP  = 'RESTORE_COMPRESSED_IMPERATIVE'
RESTORATION_OP_RESTORE_HAMZA           = 'RESTORE_HAMZA'
RESTORATION_OP_REMOVE_LICENSED_AFFIX   = 'REMOVE_LICENSED_AFFIX'

# طبقات الأدلة
EVIDENCE_SURFACE_IDENTITY      = 'surface_identity'
EVIDENCE_LICENSED_AFFIX        = 'licensed_affix_evidence'
EVIDENCE_PARADIGM              = 'paradigm_evidence'
EVIDENCE_CROSS_FORM            = 'cross_form_evidence'
EVIDENCE_LEXICAL_INVENTORY     = 'lexical_inventory_evidence'
EVIDENCE_DERIVATIONAL          = 'derivational_consistency'
EVIDENCE_CONTRADICTION         = 'contradiction_evidence'

# كفاءة الدليل
EVIDENCE_SUFFICIENT   = 'SUFFICIENT'
EVIDENCE_CONTRIBUTORY = 'CONTRIBUTORY'
EVIDENCE_INSUFFICIENT = 'INSUFFICIENT'


# ══════════════════════════════════════════════════════════════════════════════
# 1. SurfaceToken — السطح الأصلي وتمثيلاته
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SurfaceToken:
    """
    العقد الأول: تمثيل السطح قبل أي تحليل.

    القانون: لا يُسقَط التشكيل مبكرًا.
    كل تحويل تشكيلي يُسجَّل في normalization_trace.

    Attributes
    ----------
    original_surface    : السطح كما ورد من المدخل
    normalized_surface  : بعد توحيد الهمزة (normalize_hamza)
    bare_surface        : بعد إزالة التشكيل (للتطابق الأجرد فقط)
    cell_sequence       : تسلسل الخلايا (tuple من الحروف مع حركاتها)
    normalization_trace : مسار التحويل خطوة بخطوة
    """
    original_surface:    str
    normalized_surface:  str
    bare_surface:        str
    cell_sequence:       tuple[str, ...]
    normalization_trace: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            'original_surface':    self.original_surface,
            'normalized_surface':  self.normalized_surface,
            'bare_surface':        self.bare_surface,
            'cell_sequence':       list(self.cell_sequence),
            'normalization_trace': list(self.normalization_trace),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2. LicensedMorphologyInput — المدخل المرخَّص من P5
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class LicensedMorphologyInput:
    """
    العقد الثاني: ما يجوز دخوله إلى محرك الجذر.

    القانون: MABNI_BOUNDARY / OPERATOR_BOUNDARY / DEFERRED
             لا تدخل محرك الجذر أبداً.

    source_token     : SurfaceToken الأصلي
    p5_verdict       : حكم P5 (يجب أن يكون 'ACCEPT' أو حالة MabniOpen)
    p5_class         : 'MABNI_OPEN' — الصنف الوحيد المسموح
    host_surface     : المضيف المُستخرَج من P5
    admission_reason : سبب القبول
    """
    source_token:    SurfaceToken
    p5_verdict:      str          # 'ACCEPT' (verb/nominal) أو MabniOpen verdict
    p5_class:        str          # 'MABNI_OPEN' — وحده المسموح
    host_surface:    str
    admission_reason: str

    def to_dict(self) -> dict:
        return {
            'source_token':    self.source_token.to_dict(),
            'p5_verdict':      self.p5_verdict,
            'p5_class':        self.p5_class,
            'host_surface':    self.host_surface,
            'admission_reason': self.admission_reason,
        }

    def assert_licensed(self) -> None:
        """يُرفع RuntimeError إذا لم يكن المدخل مرخَّصًا."""
        if self.p5_class != 'MABNI_OPEN':
            raise RuntimeError(
                f"UnlicensedMorphologyInput: p5_class={self.p5_class!r} "
                f"— only MABNI_OPEN may enter the root engine"
            )


# ══════════════════════════════════════════════════════════════════════════════
# 3. MorphologicalStem — المضيف بعد ما قبل الجذر
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MorphologicalStem:
    """
    العقد الثالث: المضيف بعد pre_root + root_host_refinement.

    القانون [C2]: stem ≠ root — المضيف ليس الجذر.
    الاستعادة مطلوبة للوصول إلى الجذر.

    refined_host       : المضيف بعد فصل اللواحق الطرفية
    morphology_path    : المسار الصرفي (VERBAL/NOMINAL/...)
    pre_root_directive : 'OPEN' | 'DEFER' | 'BLOCK'
    removal_operations : العمليات المطبَّقة (tuple of dict)
    """
    refined_host:       str
    morphology_path:    str
    pre_root_directive: str
    removal_operations: tuple[dict, ...]

    def to_dict(self) -> dict:
        return {
            'refined_host':       self.refined_host,
            'morphology_path':    self.morphology_path,
            'pre_root_directive': self.pre_root_directive,
            'removal_operations': list(self.removal_operations),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 4. RadicalSlot — موضع واحد في الجذر
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RadicalSlot:
    """
    العقد الرابع: هوية موضع جذري واحد.

    position : 'FA' | 'AYN' | 'LAM'
    identity : الحرف الجذري المُعيَّن أو None إذا مجهول
    is_known : True إذا تمت تسمية الهوية الجذرية
    candidates : المرشحات المحتملة عند عدم المعرفة
    """
    position:   str            # FA / AYN / LAM
    identity:   Optional[str]  # الحرف الجذري أو None
    is_known:   bool
    candidates: tuple[str, ...]  # فارغة إذا is_known=True

    def to_dict(self) -> dict:
        return {
            'position':   self.position,
            'identity':   self.identity,
            'is_known':   self.is_known,
            'candidates': list(self.candidates),
        }

    @classmethod
    def known(cls, position: str, identity: str) -> "RadicalSlot":
        """أنشئ موضعًا جذريًا معروف الهوية."""
        return cls(position=position, identity=identity,
                   is_known=True, candidates=())

    @classmethod
    def unknown(cls, position: str, candidates: tuple[str, ...]) -> "RadicalSlot":
        """أنشئ موضعًا جذريًا مجهول الهوية مع مرشحات."""
        return cls(position=position, identity=None,
                   is_known=False, candidates=candidates)


# ══════════════════════════════════════════════════════════════════════════════
# 5. (RootCandidate موجود في root_candidate.py — يُشار إليه هنا)
# ══════════════════════════════════════════════════════════════════════════════
# from pipeline.p3_candidate.root_candidate import RootCandidate
# العقد الخامس: مرشح جذر مع directive + canonical_root + evidence + trace


# ══════════════════════════════════════════════════════════════════════════════
# 6. RestoredRootCandidate — مرشح مع عمليات استعادة
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RestorationOperation:
    """
    عملية استعادة مُسجَّلة (لا استعادة بلا تسجيل).

    القانون: لا حرف يُستعاد بلا عملية ودليل مُسجَّلَين.
    """
    operation_id:      str   # من ثوابت RESTORATION_OP_*
    locus:             str   # 'FA' | 'AYN' | 'LAM'
    before:            str   # الحرف/الشكل قبل الاستعادة
    after:             str   # الحرف/الشكل بعد الاستعادة
    rule:              str   # القاعدة المُطبَّقة
    required_evidence: str   # نوع الدليل المطلوب
    actual_evidence:   str   # الدليل الفعلي المتوفر
    confidence:        str   # SUFFICIENT | CONTRIBUTORY | INSUFFICIENT

    def to_dict(self) -> dict:
        return {
            'operation_id':      self.operation_id,
            'locus':             self.locus,
            'before':            self.before,
            'after':             self.after,
            'rule':              self.rule,
            'required_evidence': self.required_evidence,
            'actual_evidence':   self.actual_evidence,
            'confidence':        self.confidence,
        }


@dataclass(frozen=True)
class RestoredRootCandidate:
    """
    العقد السادس: مرشح جذر مع عمليات استعادة مُسجَّلة.

    القانون [C3]: هذا مرشح — لا حكم نهائي مباشرة.
    لا restored_candidate = licensed_root بلا تقييم دليل.

    candidate_id          : معرِّف فريد
    radicals              : tuple الحروف الجذرية
    surface_mapping       : ربط كل حرف جذري بموضعه السطحي
    slot_mapping          : tuple[RadicalSlot]
    removed_material      : المادة المُزالة (سوابق/لواحق)
    restored_material     : المادة المُستعادة
    restoration_operations: tuple[RestorationOperation]
    supporting_evidence   : أدلة داعمة
    contradicting_evidence: أدلة معارضة
    required_evidence     : الدليل المطلوب لتأكيد ACCEPT
    evidence_rank         : رتبة الدليل الإجمالية
    sufficiency           : SUFFICIENT | CONTRIBUTORY | INSUFFICIENT
    verdict               : ACCEPT | DEFER | BLOCK (مرشح، ليس نهائيًا)
    reason_codes          : رموز السبب
    named_residual        : اسم البقية إن وُجد
    trace                 : مسار التحليل
    """
    candidate_id:           str
    radicals:               Optional[tuple[str, ...]]
    surface_mapping:        tuple[dict, ...]
    slot_mapping:           tuple[RadicalSlot, ...]
    removed_material:       tuple[str, ...]
    restored_material:      tuple[str, ...]
    restoration_operations: tuple[RestorationOperation, ...]
    supporting_evidence:    tuple[str, ...]
    contradicting_evidence: tuple[str, ...]
    required_evidence:      tuple[str, ...]
    evidence_rank:          str
    sufficiency:            str
    verdict:                str
    reason_codes:           tuple[str, ...]
    named_residual:         Optional[str]
    trace:                  tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            'candidate_id':           self.candidate_id,
            'radicals':               list(self.radicals) if self.radicals else None,
            'surface_mapping':        list(self.surface_mapping),
            'slot_mapping':           [s.to_dict() for s in self.slot_mapping],
            'removed_material':       list(self.removed_material),
            'restored_material':      list(self.restored_material),
            'restoration_operations': [op.to_dict() for op in self.restoration_operations],
            'supporting_evidence':    list(self.supporting_evidence),
            'contradicting_evidence': list(self.contradicting_evidence),
            'required_evidence':      list(self.required_evidence),
            'evidence_rank':          self.evidence_rank,
            'sufficiency':            self.sufficiency,
            'verdict':                self.verdict,
            'reason_codes':           list(self.reason_codes),
            'named_residual':         self.named_residual,
            'trace':                  list(self.trace),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 7. LicensedRoot — نتيجة ACCEPT النهائية
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class LicensedRoot:
    """
    العقد السابع: النتيجة النهائية ACCEPT.

    شروط ACCEPT:
      - مرشح واحد مرخَّص أو مرشح متفوق بدليل كافٍ وقادحاته مردودة.
      - mapping كامل (FA/AYN/LAM كلها معروفة).
      - trace كامل.
      - لم تُنتهَك بوابة P5.
      - لا مانع غير محسوم.

    radicals     : tuple الحروف الثلاثة الجذرية (معروفة كلها)
    root_type    : نوع الجذر (sound/geminate/hamza_*/...)
    radical_slots: tuple[RadicalSlot] — الثلاثة مكتملة is_known=True
    source_engine: 'HOKOM_ROOT_ENGINE' (ثابت)
    trace        : مسار التحليل الكامل
    """
    radicals:      tuple[str, str, str]
    root_type:     str
    radical_slots: tuple[RadicalSlot, RadicalSlot, RadicalSlot]
    source_engine: str
    trace:         tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            'radicals':      list(self.radicals),
            'root_type':     self.root_type,
            'radical_slots': [s.to_dict() for s in self.radical_slots],
            'source_engine': self.source_engine,
            'trace':         list(self.trace),
        }

    def __post_init__(self):
        # العقد: جميع المواضع معروفة عند ACCEPT
        for slot in self.radical_slots:
            if not slot.is_known:
                raise RuntimeError(
                    f"LicensedRoot: slot {slot.position!r} is_known=False — "
                    f"ACCEPT requires all slots resolved"
                )
        if self.source_engine != 'HOKOM_ROOT_ENGINE':
            raise RuntimeError(
                f"LicensedRoot: source_engine={self.source_engine!r} — "
                f"only HOKOM_ROOT_ENGINE is the canonical owner"
            )


# ══════════════════════════════════════════════════════════════════════════════
# 8. DeferredRoot — نتيجة DEFER النهائية
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DeferredRoot:
    """
    العقد الثامن: النتيجة النهائية DEFER.

    يُستخدم عند:
      - تعدد المرشحين
      - نقص دليل الاستعادة
      - التباس حرف العلة
      - surface underlicensed
      - الحاجة إلى صيغة مقابلة أو سياق إضافي

    القانون: لا ACCEPT بعد DEFER بلا دليل جديد.

    defer_reason : سبب التأجيل (من RESIDUAL_* ثوابت)
    candidates   : المرشحات المحتملة (قد تكون فارغة)
    missing_evidence: ما يحتاج من دليل لرفع التأجيل
    """
    defer_reason:     str
    candidates:       tuple[RestoredRootCandidate, ...]
    missing_evidence: tuple[str, ...]
    trace:            tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            'defer_reason':     self.defer_reason,
            'candidates':       [c.to_dict() for c in self.candidates],
            'missing_evidence': list(self.missing_evidence),
            'trace':            list(self.trace),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 9. BlockedRoot — نتيجة BLOCK النهائية
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class BlockedRoot:
    """
    العقد التاسع: النتيجة النهائية BLOCK.

    يُستخدم عند:
      - مدخل غير مسموح من P5 (MABNI_BOUNDARY/OPERATOR_BOUNDARY)
      - تناقض بنيوي قاطع
      - إزالة غير قانونية مطلوبة للوصول إلى المرشح
      - بنية غير قابلة للجذر (0-1 حرف)

    block_reason : المانع القاطع (من RESIDUAL_* أو block:root:*)
    blocker_type : 'P5_GATE' | 'STRUCTURAL' | 'INSUFFICIENT_CONSONANTS' | 'UNLICENSED_REMOVAL'
    """
    block_reason: str
    blocker_type: str
    trace:        tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            'block_reason': self.block_reason,
            'blocker_type': self.blocker_type,
            'trace':        list(self.trace),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 10. RootResidual — بقية مسماة
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RootResidual:
    """
    العقد العاشر: بقية مسماة قابلة للتطوير اللاحق.

    لا تُدرج في الإغلاق النهائي لكن تُوثَّق.
    كل بقية لها:
      residual_id : معرِّف فريد
      surface     : السطح الذي أنتج هذه البقية
      reason      : السبب التقني
      root_class  : فئة الجذر (A-L)
      resolution  : ما يلزم لحسم هذه البقية
      governed    : True = محكوم ومعترف به، False = جديد غير محكوم
    """
    residual_id: str
    surface:     str
    reason:      str
    root_class:  str
    resolution:  str
    governed:    bool

    def to_dict(self) -> dict:
        return {
            'residual_id': self.residual_id,
            'surface':     self.surface,
            'reason':      self.reason,
            'root_class':  self.root_class,
            'resolution':  self.resolution,
            'governed':    self.governed,
        }


# ══════════════════════════════════════════════════════════════════════════════
# الخريطة الكاملة: عقد الدخول لكل فئة جذر
# ══════════════════════════════════════════════════════════════════════════════

ROOT_CLASS_CONTRACTS: dict[str, dict] = {
    'A_SOUND': {
        'label':       'الصحيح السالم',
        'verdict':     ROOT_VERDICT_ACCEPT,
        'conditions':  'ثلاثة حروف صحيحة، لا ضعيف، لا همزة',
        'residuals':   [],
        'scope':       'CURRENT_BATCH',
    },
    'B_HAMZA': {
        'label':       'المهموز (فاء/عين/لام)',
        'verdict':     ROOT_VERDICT_ACCEPT,
        'conditions':  'ء في أي موضع بعد توحيد الهمزة',
        'residuals':   [],
        'scope':       'CURRENT_BATCH',
    },
    'C_GEMINATE': {
        'label':       'المضعَّف',
        'verdict':     ROOT_VERDICT_ACCEPT,
        'conditions':  'عين=لام أو فاء=عين بعد فك الشدة هندسيًا',
        'residuals':   [],
        'scope':       'CURRENT_BATCH',
    },
    'D_ASSIMILATED': {
        'label':       'المثال (فاء ضعيفة)',
        'verdict':     ROOT_VERDICT_DEFER,
        'conditions':  'فاء ∈ {و, ي} — مؤجَّل للمرحلة التالية',
        'residuals':   [RESIDUAL_ASSIMILATED_UNRESOLVED],
        'scope':       'DEFERRED',
    },
    'E_HOLLOW': {
        'label':       'الأجوف (عين ضعيفة)',
        'verdict':     ROOT_VERDICT_DEFER,
        'conditions':  'عين ∈ {ا, و} — الجذر الأصلي غير محدد',
        'residuals':   [RESIDUAL_HOLLOW_UNRESOLVED],
        'scope':       'DEFERRED',
    },
    'F_DEFECTIVE': {
        'label':       'الناقص (لام ضعيفة)',
        'verdict':     ROOT_VERDICT_DEFER,
        'conditions':  'لام ∈ {ا, ى, ي} — الجذر الأصلي غير محدد',
        'residuals':   [RESIDUAL_DEFECTIVE_UNRESOLVED],
        'scope':       'DEFERRED',
    },
    'G_LAFIF_MAFRUQ': {
        'label':       'اللفيف المفروق (فاء+لام ضعيفتان)',
        'verdict':     ROOT_VERDICT_DEFER,
        'conditions':  'فاء ∈ _WEAK_FA و لام ∈ _WEAK_LAM — موضعان ضعيفان غير متجاورين',
        'residuals':   [RESIDUAL_LAFIF_MAFRUQ_UNRESOLVED],
        'scope':       'DEFERRED',
    },
    'H_LAFIF_MAQRUN': {
        'label':       'اللفيف المقرون (عين+لام ضعيفتان)',
        'verdict':     ROOT_VERDICT_DEFER,
        'conditions':  'عين ∈ _WEAK_AYN و لام ∈ _WEAK_LAM — موضعان ضعيفان متجاوران',
        'residuals':   [RESIDUAL_LAFIF_MAQRUN_UNRESOLVED],
        'scope':       'DEFERRED',
    },
    'I_QUADRILATERAL': {
        'label':       'الرباعي الأصلي',
        'verdict':     ROOT_VERDICT_DEFER,
        'conditions':  'أربعة حروف بعد الاستخراج — خارج النطاق الحالي',
        'residuals':   [RESIDUAL_QUADRILATERAL_SCOPE],
        'scope':       'OUT_OF_SCOPE',
    },
    'J_AUGMENTED': {
        'label':       'المزيد (زيادات مرخَّصة)',
        'verdict':     ROOT_VERDICT_ACCEPT,
        'conditions':  'trilateral_root من AugmentedAnalysis — مسار الفعل المزيد',
        'residuals':   [],
        'scope':       'CURRENT_BATCH_VIA_AUGMENTED',
    },
    'K_COMPRESSED': {
        'label':       'الأمر المضغوط',
        'verdict':     ROOT_VERDICT_DEFER,
        'conditions':  'حرفان فقط بعد الاستخراج — أجوف مضغوط محتمل',
        'residuals':   [RESIDUAL_COMPRESSED_UNRESOLVED],
        'scope':       'DEFERRED',
    },
    'L_INSUFFICIENT': {
        'label':       'بنى لا تكفي وحدها',
        'verdict':     ROOT_VERDICT_DEFER,
        'conditions':  'نمط غير قياسي — يحتاج صيغة مقابلة أو سياق',
        'residuals':   [RESIDUAL_NON_STANDARD],
        'scope':       'DEFERRED',
    },
}
