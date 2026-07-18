#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_masdar/models.py — نماذج بيانات Phase 4C (MasdarProjection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يعرّف البنى القانونية لطبقة المصدر (Phase 4C):

  MasdarCandidate  — مرشّح مصدر مفرد مع مصدره وشواهده.
  MasdarProjection — إسقاط المصدر الكامل على السطح.
  Phase4CResult    — المخرج الكامل من Phase 4C.

المبدأ الحاكم:
  قبول الجذر + الوزن + الباب لا يستلزم تلقائيًا قبول المصدر.
  - المجرد: سماعي — يتطلب بحثًا معجميًا → DEFER / SAMI3I_REQUIRED
  - المزيد: قياسي هيكليًا → STRUCTURAL_INFERENCE / ACCEPT (مبدئي)

أنواع المصدر (source_type):
  LEXICAL_LICENSED     — مدخل معجمي مرخّص يؤكد المصدر.
  STRUCTURAL_INFERENCE — استنتاج هيكلي من صيغة مزيدة.
  SAMI3I_REQUIRED      — مجرد: الاستماع مطلوب، لا تنبؤ هيكلي.

قوانين العقد:
  - ACCEPT يستوجب selected_masdar ≠ None.
  - DEFER / BLOCK / NOT_OPENED يستوجب selected_masdar = None.
  - source_path مستقل عن final_directive.
  - جميع الأنواع frozen وقابلة للتسلسل عبر to_dict().
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1.  مرشّح المصدر
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MasdarCandidate:
    """مرشّح مصدر واحد مع مصدره وشواهده.

    masdar_id      : معرّف المصدر الفريد (مثال: MASDAR_FORM_II).
    masdar_surface : شكل المصدر السطحي (مثال: تَفْعِيل) أو None.
    masdar_pattern : وزن المصدر (مثال: فَعْل) أو None.
    source_type    : LEXICAL_LICENSED | STRUCTURAL_INFERENCE | SAMI3I_REQUIRED.
    confidence     : HIGH | MEDIUM | DEFER_REQUIRED.
    evidence_ids   : شواهد الاختيار.
    trace_ids      : مسار التحليل.
    residual_codes : رموز التحفظ.
    """
    masdar_id:      str
    masdar_surface: Optional[str]
    masdar_pattern: Optional[str]
    source_type:    str            # LEXICAL_LICENSED | STRUCTURAL_INFERENCE | SAMI3I_REQUIRED
    confidence:     str            # HIGH | MEDIUM | DEFER_REQUIRED
    evidence_ids:   tuple
    trace_ids:      tuple
    residual_codes: tuple

    def to_dict(self) -> dict:
        return {
            'masdar_id':      self.masdar_id,
            'masdar_surface': self.masdar_surface,
            'masdar_pattern': self.masdar_pattern,
            'source_type':    self.source_type,
            'confidence':     self.confidence,
            'evidence_ids':   list(self.evidence_ids),
            'trace_ids':      list(self.trace_ids),
            'residual_codes': list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2.  إسقاط المصدر
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MasdarProjection:
    """مخرج إسقاط المصدر من Phase 4C.

    directive              : ACCEPT | DEFER | BLOCK | NOT_OPENED | NOT_APPLICABLE
    stage_state            : OPENED | NOT_OPENED | NOT_APPLICABLE
    applicability          : APPLICABLE | NOT_APPLICABLE | UNKNOWN
    candidate_masadir      : المرشحون المحتملون.
    selected_masdar        : المصدر المختار عند ACCEPT، وإلا None.
    selected_masdar_pattern: وزن المصدر المختار أو None.
    source_type            : كيف تحدد المصدر أو None.
    source_wazn            : wazn_id المصدر من Phase4A.
    bab_id                 : bab_id المصدر من Phase4B أو None.
    canonical_root         : الجذر الكنوني أو None.
    evidence_ids           : شواهد.
    trace_ids              : مسار.
    residual_codes         : تحفظات.
    """
    directive:               str          # ACCEPT | DEFER | BLOCK | NOT_OPENED | NOT_APPLICABLE
    stage_state:             str          # OPENED | NOT_OPENED | NOT_APPLICABLE
    applicability:           str          # APPLICABLE | NOT_APPLICABLE | UNKNOWN
    candidate_masadir:       tuple        # tuple[MasdarCandidate, ...]
    selected_masdar:         Optional[str]
    selected_masdar_pattern: Optional[str]
    source_type:             Optional[str]
    source_wazn:             Optional[str]
    bab_id:                  Optional[str]
    canonical_root:          Optional[tuple]
    evidence_ids:            tuple
    trace_ids:               tuple
    residual_codes:          tuple

    def to_dict(self) -> dict:
        return {
            'directive':               self.directive,
            'stage_state':             self.stage_state,
            'applicability':           self.applicability,
            'candidate_masadir':       [c.to_dict() for c in self.candidate_masadir],
            'selected_masdar':         self.selected_masdar,
            'selected_masdar_pattern': self.selected_masdar_pattern,
            'source_type':             self.source_type,
            'source_wazn':             self.source_wazn,
            'bab_id':                  self.bab_id,
            'canonical_root':          (list(self.canonical_root)
                                        if self.canonical_root is not None else None),
            'evidence_ids':            list(self.evidence_ids),
            'trace_ids':               list(self.trace_ids),
            'residual_codes':          list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  نتيجة Phase 4C الكاملة
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Phase4CResult:
    """المخرج الكامل من Phase 4C.

    initial_bab_directive  : directive Phase4B (أو SKIP إن كان Phase4B None).
    final_directive        : الحكم النهائي (ACCEPT|DEFER|BLOCK|NOT_OPENED|NOT_APPLICABLE).
    masdar_projection      : MasdarProjection | None.
    final_masdar           : المصدر المختار عند ACCEPT، وإلا None.
    final_masdar_pattern   : وزن المصدر عند ACCEPT، وإلا None.
    source_path            : وصف المسار:
                               structural_accept  — صيغة مزيدة، استنتاج هيكلي.
                               lexical_accept     — مدخل معجمي مرخّص.
                               deferred           — مجرد أو باب غامض.
                               blocked            — تناقض من طبقة أعلى.
                               not_opened         — Phase4A لم يقبل.
                               not_applicable     — وزن اسمي لا فعلي.
    evidence_ids    : شواهد.
    trace_ids       : مسار.
    residual_codes  : تحفظات.
    """
    initial_bab_directive: str
    final_directive:       str
    masdar_projection:     Optional[MasdarProjection]
    final_masdar:          Optional[str]
    final_masdar_pattern:  Optional[str]
    source_path:           str
    evidence_ids:          tuple
    trace_ids:             tuple
    residual_codes:        tuple

    def to_dict(self) -> dict:
        return {
            'initial_bab_directive': self.initial_bab_directive,
            'final_directive':       self.final_directive,
            'masdar_projection':     (self.masdar_projection.to_dict()
                                      if self.masdar_projection is not None else None),
            'final_masdar':          self.final_masdar,
            'final_masdar_pattern':  self.final_masdar_pattern,
            'source_path':           self.source_path,
            'evidence_ids':          list(self.evidence_ids),
            'trace_ids':             list(self.trace_ids),
            'residual_codes':        list(self.residual_codes),
        }
