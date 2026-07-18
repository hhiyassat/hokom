#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_mushtaqat/models.py — نماذج بيانات Phase 4D (MushtaqProjection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يعرّف البنى القانونية لطبقة المشتقات (Phase 4D):

  MushtaqCandidate  — مرشّح مشتق مفرد مع مصدره وشواهده.
  MushtaqProjection — إسقاط المشتقات الكامل على السطح.
  Phase4DResult     — المخرج الكامل من Phase 4D.

المبدأ الحاكم:
  قبول الجذر + الوزن + الباب + المصدر لا يستلزم تلقائيًا قبول المشتقات.
  كل مشتق يحتاج:
    1. شرط قابلية مستقل
    2. وزن مشتق مرخّص
    3. قيد التعدية المناسب
    4. فحص حاجز مستقل

أنواع التوجيه لكل مشتق:
  ACCEPT       — وزن مشتق مقبول، شروط متحققة.
  DEFER        — معلومات غير كافية (تعدية مجهولة، باب غامض).
  BLOCK        — ممنوع صريحًا (فعل لازم لاسم مفعول، وزن اسمي).
  NOT_APPLICABLE — الوزن اسمي أو الشرط لا ينطبق أصلًا.

التوجيه الكلي (final_directive في Phase4DResult):
  ACCEPT         — جميع المشتقات المحسوبة مقبولة.
  PARTIAL_ACCEPT — بعض مقبولة وبعض مؤجلة/محجوبة.
  DEFER          — لا مشتقات مقبولة، وبعضها مؤجل.
  BLOCK          — جميع المشتقات محجوبة.
  NOT_OPENED     — Phase4A لم يقبل.
  NOT_APPLICABLE — الوزن اسمي.

قوانين العقد:
  - ACCEPT / PARTIAL_ACCEPT يستوجب accepted_mushtaqat ≠ {}.
  - DEFER / BLOCK / NOT_OPENED يستوجب accepted_mushtaqat = {}.
  - جميع الأنواع frozen وقابلة للتسلسل عبر to_dict().
  - candidates_by_type قابل للوصول عبر property (لا dict field).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1.  أنواع المشتقات المعرّفة
# ══════════════════════════════════════════════════════════════════════════════

MUSHTAQ_TYPES = frozenset({
    'ISM_FA3IL',
    'ISM_MAF3UL',
    'SIFA_MUSHABBAHA',
    'SIYAG_MUBALAGHAH',
    'ISM_ZAMAN',
    'ISM_MAKAN',
    'ISM_ALA',
    'TAFDHIL',
})

VALID_DIRECTIVES = frozenset({
    'ACCEPT', 'PARTIAL_ACCEPT', 'DEFER', 'BLOCK',
    'NOT_OPENED', 'NOT_APPLICABLE',
})


# ══════════════════════════════════════════════════════════════════════════════
# 2.  مرشّح المشتق
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MushtaqCandidate:
    """مرشّح مشتق واحد مع مصدره وشواهده.

    mushtaq_type           : ISM_FA3IL | ISM_MAF3UL | SIFA_MUSHABBAHA | ...
    mushtaq_pattern        : وزن المشتق (مثال: فَاعِل, مَفْعُول).
    source_type            : STRUCTURAL_INFERENCE | LEXICAL_LICENSED | SAMI3I_REQUIRED.
    transitivity_constraint: TRANSITIVE | INTRANSITIVE | UNCONSTRAINED | UNKNOWN.
    confidence             : HIGH | MEDIUM | DEFER_REQUIRED.
    evidence_ids           : شواهد الاختيار.
    trace_ids              : مسار التحليل.
    residual_codes         : رموز التحفظ.
    """
    mushtaq_type:            str
    mushtaq_pattern:         str
    source_type:             str   # STRUCTURAL_INFERENCE | LEXICAL_LICENSED | SAMI3I_REQUIRED
    transitivity_constraint: str   # TRANSITIVE | INTRANSITIVE | UNCONSTRAINED | UNKNOWN
    confidence:              str   # HIGH | MEDIUM | DEFER_REQUIRED
    evidence_ids:            tuple
    trace_ids:               tuple
    residual_codes:          tuple

    def to_dict(self) -> dict:
        return {
            'mushtaq_type':            self.mushtaq_type,
            'mushtaq_pattern':         self.mushtaq_pattern,
            'source_type':             self.source_type,
            'transitivity_constraint': self.transitivity_constraint,
            'confidence':              self.confidence,
            'evidence_ids':            list(self.evidence_ids),
            'trace_ids':               list(self.trace_ids),
            'residual_codes':          list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  إسقاط المشتقات
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MushtaqProjection:
    """مخرج إسقاط المشتقات من Phase 4D.

    directive          : ACCEPT | PARTIAL_ACCEPT | DEFER | BLOCK | NOT_OPENED | NOT_APPLICABLE
    stage_state        : OPENED | NOT_OPENED | NOT_APPLICABLE
    applicability      : APPLICABLE | NOT_APPLICABLE | UNKNOWN
    all_candidates     : جميع المرشحات (flat tuple) — استخدم candidates_by_type للوصول بالنوع.
    accepted_mushtaqat : mushtaq_type → pattern (للمقبولات فقط).
    deferred_mushtaqat : أنواع مؤجلة.
    blocked_mushtaqat  : أنواع محجوبة.
    source_wazn        : wazn_id المصدر من Phase4A.
    bab_id             : bab_id من Phase4B أو None.
    canonical_root     : الجذر الكنوني أو None.
    evidence_ids       : شواهد.
    trace_ids          : مسار.
    residual_codes     : تحفظات.
    """
    directive:          str          # ACCEPT | PARTIAL_ACCEPT | DEFER | BLOCK | NOT_OPENED | NOT_APPLICABLE
    stage_state:        str          # OPENED | NOT_OPENED | NOT_APPLICABLE
    applicability:      str          # APPLICABLE | NOT_APPLICABLE | UNKNOWN
    all_candidates:     tuple        # tuple[MushtaqCandidate, ...]
    accepted_mushtaqat: tuple        # tuple of (type_str, pattern_str) pairs
    deferred_mushtaqat: tuple        # tuple[str, ...]
    blocked_mushtaqat:  tuple        # tuple[str, ...]
    source_wazn:        Optional[str]
    bab_id:             Optional[str]
    canonical_root:     Optional[tuple]
    evidence_ids:       tuple
    trace_ids:          tuple
    residual_codes:     tuple

    @property
    def candidates_by_type(self) -> dict:
        """أعِد قاموسًا من mushtaq_type → tuple[MushtaqCandidate, ...]."""
        result: dict = {}
        for c in self.all_candidates:
            if c.mushtaq_type not in result:
                result[c.mushtaq_type] = []
            result[c.mushtaq_type].append(c)
        return {k: tuple(v) for k, v in result.items()}

    @property
    def accepted_mushtaqat_dict(self) -> dict:
        """أعِد قاموسًا من mushtaq_type → pattern للمقبولات فقط."""
        return dict(self.accepted_mushtaqat)

    def to_dict(self) -> dict:
        cbt = self.candidates_by_type
        return {
            'directive':          self.directive,
            'stage_state':        self.stage_state,
            'applicability':      self.applicability,
            'candidates_by_type': {
                t: [c.to_dict() for c in cs]
                for t, cs in cbt.items()
            },
            'accepted_mushtaqat': dict(self.accepted_mushtaqat),
            'deferred_mushtaqat': list(self.deferred_mushtaqat),
            'blocked_mushtaqat':  list(self.blocked_mushtaqat),
            'source_wazn':        self.source_wazn,
            'bab_id':             self.bab_id,
            'canonical_root':     (list(self.canonical_root)
                                   if self.canonical_root is not None else None),
            'evidence_ids':       list(self.evidence_ids),
            'trace_ids':          list(self.trace_ids),
            'residual_codes':     list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 4.  نتيجة Phase 4D الكاملة
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Phase4DResult:
    """المخرج الكامل من Phase 4D.

    initial_masdar_directive : directive Phase4C (أو SKIP إن كان Phase4C None).
    final_directive          : ACCEPT | PARTIAL_ACCEPT | DEFER | BLOCK | NOT_OPENED | NOT_APPLICABLE.
    mushtaq_projection       : MushtaqProjection | None.
    accepted_mushtaqat       : mushtaq_type → pattern (للمقبولات فقط).
    source_path              : وصف المسار.
    evidence_ids             : شواهد.
    trace_ids                : مسار.
    residual_codes           : تحفظات.
    """
    initial_masdar_directive: str
    final_directive:          str
    mushtaq_projection:       Optional[MushtaqProjection]
    accepted_mushtaqat:       tuple        # tuple of (type_str, pattern_str) pairs
    source_path:              str
    evidence_ids:             tuple
    trace_ids:                tuple
    residual_codes:           tuple

    @property
    def accepted_mushtaqat_dict(self) -> dict:
        """أعِد قاموسًا من mushtaq_type → pattern."""
        return dict(self.accepted_mushtaqat)

    def to_dict(self) -> dict:
        return {
            'initial_masdar_directive': self.initial_masdar_directive,
            'final_directive':          self.final_directive,
            'mushtaq_projection':       (self.mushtaq_projection.to_dict()
                                         if self.mushtaq_projection is not None else None),
            'accepted_mushtaqat':       dict(self.accepted_mushtaqat),
            'source_path':              self.source_path,
            'evidence_ids':             list(self.evidence_ids),
            'trace_ids':                list(self.trace_ids),
            'residual_codes':           list(self.residual_codes),
        }
