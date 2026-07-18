#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/models.py — النموذج القانوني لطبقة الوزن (Phase 4A)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يعرّف مفردات وأنواع WaznProjection:
  - WaznDirective / WaznStageState — القرار وحالة المرحلة.
  - RootSlot / AlignmentKind       — مفردات المحاذاة.
  - WaznSlotAlignment              — محاذاة خانة سطحية واحدة.
  - WaznCandidate                  — وزن مرشّح مع محاذاته الكاملة.
  - WaznProjection                 — المخرج النهائي (قابل للتسلسل JSON).
  - WaznProjectionContractError    — خطأ العقد (فشل صريح، لا BLOCK صامت).

كل الأنواع frozen وقابلة للتسلسل عبر to_dict().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Any, Optional


PROJECTION_VERSION = "phase4a-wazn-1"


# ══════════════════════════════════════════════════════════════════════════════
# 1.  خطأ العقد
# ══════════════════════════════════════════════════════════════════════════════

class WaznProjectionContractError(RuntimeError):
    """يُرفع عند خرق عقد WaznProjection. الفشل صريح دائمًا — لا fallback صامت إلى BLOCK.

    يُستخدم عند:
      - ACCEPT بلا canonical_root.
      - root arity غير مدعوم.
      - selected_wazn ليس ضمن candidate_awzan.
      - ACCEPT مع أكثر من وزن متساوٍ بالدليل.
      - ACCEPT مع root slot غير محلول.
      - ACCEPT مع radical identity = ا أو ى.
      - alignment لا يحفظ ترتيب الجذر.
      - schema catalog غير صالحة.
      - directive غير معروفة.
    """
    pass


# ══════════════════════════════════════════════════════════════════════════════
# 2.  المفردات (Enums)
# ══════════════════════════════════════════════════════════════════════════════

class WaznDirective(str, Enum):
    ACCEPT = "ACCEPT"
    DEFER  = "DEFER"
    BLOCK  = "BLOCK"


class WaznStageState(str, Enum):
    COMPLETED  = "COMPLETED"
    DEFERRED   = "DEFERRED"
    BLOCKED    = "BLOCKED"
    NOT_OPENED = "NOT_OPENED"


class RootSlot(str, Enum):
    FA     = "ف"
    AIN    = "ع"
    LAM    = "ل"
    FOURTH = "ل2"   # الحرف الجذري الرابع في الرباعي — تمثيل صريح لا لبس فيه


class AlignmentKind(str, Enum):
    ROOT_RADICAL      = "root_radical"       # حرف جذري أصلي محاذى لخانة وزن
    ZIYADAH           = "ziyadah"            # حرف زيادة مرخّص من الوزن
    INFLECTIONAL      = "inflectional"       # لاحقة تصريفية خارج أصل الوزن
    RESTORED_ROOT     = "restored_root"      # حرف جذري مستعاد (من RootCandidate فقط)
    SURFACE_ALLOMORPH = "surface_allomorph"  # صورة سطحية لحرف (إدغام/قلب مرخّص)
    DELETED_ROOT_SLOT = "deleted_root_slot"  # خانة جذرية محذوفة بعملية مرخّصة
    UNRESOLVED        = "unresolved"         # خانة لم تُحسم


# ══════════════════════════════════════════════════════════════════════════════
# 3.  محاذاة الخانة
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class WaznSlotAlignment:
    """محاذاة خانة سطحية واحدة بجزء من بنية الوزن.

    surface_segment    : المقطع السطحي (من analyzed_host) أو None لو خانة محذوفة.
    normalized_segment : المقطع بعد التطبيع (شدة/همزة) أو None.
    surface_index      : فهرس الحرف في المضيف المطبَّع أو None.
    root_slot          : خانة الجذر (ف/ع/ل/ل2) إن كان حرفًا جذريًا، وإلا None.
    root_identity      : هوية الحرف الجذري (من canonical_root) إن وُجدت.
    alignment_kind     : نوع المحاذاة.
    operation_id       : معرّف العملية الصرفية المرخّصة (إدغام/قلب...) أو None.
    evidence_ids       : شواهد.
    trace_ids          : مسار.
    """
    surface_segment:    Optional[str]
    normalized_segment: Optional[str]
    surface_index:      Optional[int]
    root_slot:          Optional[RootSlot]
    root_identity:      Optional[str]
    alignment_kind:     AlignmentKind
    operation_id:       Optional[str]
    evidence_ids:       tuple = ()
    trace_ids:          tuple = ()

    def to_dict(self) -> dict:
        return {
            "surface_segment":    self.surface_segment,
            "normalized_segment": self.normalized_segment,
            "surface_index":      self.surface_index,
            "root_slot":          (self.root_slot.value
                                   if self.root_slot is not None else None),
            "root_identity":      self.root_identity,
            "alignment_kind":     self.alignment_kind.value,
            "operation_id":       self.operation_id,
            "evidence_ids":       list(self.evidence_ids),
            "trace_ids":          list(self.trace_ids),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 4.  الوزن المرشّح
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class WaznCandidate:
    """وزن مرشّح واحد مع محاذاته الكاملة.

    wazn_id            : معرّف الوزن في الـcatalog.
    wazn_pattern       : النمط السطحي (فَعَلَ، مَفْعُول...).
    wazn_family        : عائلة الوزن.
    alignment          : تسلسل محاذاة الخانات.
    root_slots_complete: هل كل خانات الجذر محاذاة؟
    ziyadah_slots      : الخانات الزائدة المرخّصة (وصف).
    deleted_root_slots : خانات جذرية محذوفة (بعملية مرخّصة).
    weak_operations    : عمليات الإعلال/الإدغام المرخّصة.
    confidence_rank    : رتبة الدليل (أصغر = أقوى).
    evidence_ids       : شواهد.
    residual_codes     : تحفّظات هذا المرشّح.
    """
    wazn_id:             str
    wazn_pattern:        str
    wazn_family:         str
    alignment:           tuple  # tuple[WaznSlotAlignment, ...]
    root_slots_complete: bool
    ziyadah_slots:       tuple = ()
    deleted_root_slots:  tuple = ()
    weak_operations:     tuple = ()
    confidence_rank:     int = 0
    evidence_ids:        tuple = ()
    residual_codes:      tuple = ()

    def to_dict(self) -> dict:
        return {
            "wazn_id":             self.wazn_id,
            "wazn_pattern":        self.wazn_pattern,
            "wazn_family":         self.wazn_family,
            "alignment":           [a.to_dict() for a in self.alignment],
            "root_slots_complete": self.root_slots_complete,
            "ziyadah_slots":       list(self.ziyadah_slots),
            "deleted_root_slots":  list(self.deleted_root_slots),
            "weak_operations":     list(self.weak_operations),
            "confidence_rank":     self.confidence_rank,
            "evidence_ids":        list(self.evidence_ids),
            "residual_codes":      list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 5.  الإسقاط النهائي
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class WaznProjection:
    """مخرج Phase 4A — إسقاط الوزن على السطح.

    يحفظ الفصل بين:
      - analyzed_host  : السطح الاشتقاقي المستعمل (لا السطح الكامل).
      - normalized_host: صورته المطبَّعة (شدة/همزة موسّعة).
    ولا يخلط اللواحق التصريفية بأصل الوزن.
    """
    input_surface:   str
    analyzed_host:   str
    normalized_host: str
    canonical_root:  Optional[tuple]

    directive:   WaznDirective
    stage_state: WaznStageState

    candidate_awzan: tuple = ()          # tuple[WaznCandidate, ...]
    selected_wazn:   Optional[WaznCandidate] = None

    root_slot_alignment:   tuple = ()    # tuple[WaznSlotAlignment, ...]
    ziyadah_slots:         tuple = ()
    weak_operations:       tuple = ()
    unresolved_operations: tuple = ()
    inflectional_suffixes: tuple = ()    # اللواحق التصريفية المفصولة عن الوزن

    evidence_ids:   tuple = ()
    trace_ids:      tuple = ()
    residual_codes: tuple = ()

    source_root_candidate: str = "RootCandidate"
    projection_version:    str = PROJECTION_VERSION

    def to_dict(self) -> dict:
        return {
            "input_surface":         self.input_surface,
            "analyzed_host":         self.analyzed_host,
            "normalized_host":       self.normalized_host,
            "canonical_root":        (list(self.canonical_root)
                                      if self.canonical_root is not None else None),
            "directive":             self.directive.value,
            "stage_state":           self.stage_state.value,
            "candidate_awzan":       [c.to_dict() for c in self.candidate_awzan],
            "selected_wazn":         (self.selected_wazn.to_dict()
                                      if self.selected_wazn is not None else None),
            "root_slot_alignment":   [a.to_dict() for a in self.root_slot_alignment],
            "ziyadah_slots":         list(self.ziyadah_slots),
            "weak_operations":       list(self.weak_operations),
            "unresolved_operations": list(self.unresolved_operations),
            "inflectional_suffixes": list(self.inflectional_suffixes),
            "evidence_ids":          list(self.evidence_ids),
            "trace_ids":             list(self.trace_ids),
            "residual_codes":        list(self.residual_codes),
            "source_root_candidate": self.source_root_candidate,
            "projection_version":    self.projection_version,
        }
