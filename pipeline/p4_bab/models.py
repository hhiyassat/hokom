#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_bab/models.py — نماذج بيانات Phase 4B (BabProjection)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يعرّف البنى القانونية لطبقة الباب/صيغة الفعل (Phase 4B):

  BabCandidate  — مرشّح باب مفرد مع شواهده.
  BabProjection — إسقاط الباب الكامل على السطح.
  Phase4BResult — المخرج الكامل من Phase 4B.

كل الأنواع frozen وقابلة للتسلسل عبر to_dict().

قوانين العقد:
  • ACCEPT يستوجب exactly 1 candidate وselected_bab ≠ None.
  • DEFER / BLOCK يستوجب selected_bab = None.
  • NOT_OPENED يصدر عندما Phase4A لم ينتهِ بـ ACCEPT.
  • NOT_APPLICABLE يصدر لأوزان اسمية (غير فعلية).
  • source_path يصف المسار — لا يحدد الحكم.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1.  مرشّح الباب
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class BabCandidate:
    """مرشّح باب واحد مع شواهده.

    bab_id          : معرّف الباب في catalog (BAB_I_NASARA، BAB_FORM_VIII...).
    bab_family      : عائلة الباب (MUJARRAD | MAZID).
    past_wazn       : وزن الماضي (مأخوذ من catalog: FA_A_LA...).
    imperfect_wazn  : وزن المضارع أو None إن لم يُكتشف.
    confidence      : درجة الثقة (HIGH | MEDIUM | DEFER_REQUIRED).
    evidence_ids    : شواهد الاختيار.
    trace_ids       : مسار التحليل.
    residual_codes  : رموز التحفظ.
    """
    bab_id:         str
    bab_family:     str
    past_wazn:      Optional[str]
    imperfect_wazn: Optional[str]
    confidence:     str           # 'HIGH' | 'MEDIUM' | 'DEFER_REQUIRED'
    evidence_ids:   tuple
    trace_ids:      tuple
    residual_codes: tuple

    def to_dict(self) -> dict:
        return {
            'bab_id':         self.bab_id,
            'bab_family':     self.bab_family,
            'past_wazn':      self.past_wazn,
            'imperfect_wazn': self.imperfect_wazn,
            'confidence':     self.confidence,
            'evidence_ids':   list(self.evidence_ids),
            'trace_ids':      list(self.trace_ids),
            'residual_codes': list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2.  إسقاط الباب
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class BabProjection:
    """مخرج إسقاط الباب من Phase 4B.

    directive       : ACCEPT | DEFER | BLOCK | NOT_OPENED
    stage_state     : OPENED | NOT_OPENED | NOT_APPLICABLE
    candidate_abwab : المرشحون المحتملون.
    selected_bab    : الباب المختار عند ACCEPT، وإلا None.
    source_wazn     : wazn_id المصدر من Phase4A.
    canonical_root  : الجذر الكنوني من Phase4A.
    applicability   : APPLICABLE | NOT_APPLICABLE | UNKNOWN
    evidence_ids    : شواهد.
    trace_ids       : مسار.
    residual_codes  : تحفظات.
    """
    directive:        str          # ACCEPT | DEFER | BLOCK | NOT_OPENED
    stage_state:      str          # OPENED | NOT_OPENED | NOT_APPLICABLE
    candidate_abwab:  tuple        # tuple[BabCandidate, ...]
    selected_bab:     Optional[str]
    source_wazn:      Optional[str]
    canonical_root:   Optional[tuple]
    applicability:    str          # APPLICABLE | NOT_APPLICABLE | UNKNOWN
    evidence_ids:     tuple
    trace_ids:        tuple
    residual_codes:   tuple

    def to_dict(self) -> dict:
        return {
            'directive':       self.directive,
            'stage_state':     self.stage_state,
            'candidate_abwab': [c.to_dict() for c in self.candidate_abwab],
            'selected_bab':    self.selected_bab,
            'source_wazn':     self.source_wazn,
            'canonical_root':  (list(self.canonical_root)
                                if self.canonical_root is not None else None),
            'applicability':   self.applicability,
            'evidence_ids':    list(self.evidence_ids),
            'trace_ids':       list(self.trace_ids),
            'residual_codes':  list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  نتيجة Phase 4B الكاملة
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Phase4BResult:
    """المخرج الكامل من Phase 4B.

    initial_wazn_directive : directive Phase4A المُدخَّل.
    final_directive        : الحكم النهائي (ACCEPT|DEFER|BLOCK|NOT_OPENED|NOT_APPLICABLE).
    bab_projection         : BabProjection | None.
    final_bab              : bab_id عند ACCEPT، وإلا None.
    source_path            : وصف المسار:
                               direct_accept  — مرشّح واحد، دليل كافٍ.
                               deferred       — غامض أو دليل غير كافٍ.
                               blocked        — تناقض.
                               not_opened     — Phase4A لم يُقبَل.
                               not_applicable — وزن اسمي.
    evidence_ids    : شواهد.
    trace_ids       : مسار.
    residual_codes  : تحفظات.
    """
    initial_wazn_directive: str
    final_directive:        str
    bab_projection:         Optional[BabProjection]
    final_bab:              Optional[str]
    source_path:            str
    evidence_ids:           tuple
    trace_ids:              tuple
    residual_codes:         tuple

    def to_dict(self) -> dict:
        return {
            'initial_wazn_directive': self.initial_wazn_directive,
            'final_directive':        self.final_directive,
            'bab_projection':         (self.bab_projection.to_dict()
                                       if self.bab_projection is not None else None),
            'final_bab':              self.final_bab,
            'source_path':            self.source_path,
            'evidence_ids':           list(self.evidence_ids),
            'trace_ids':              list(self.trace_ids),
            'residual_codes':         list(self.residual_codes),
        }
