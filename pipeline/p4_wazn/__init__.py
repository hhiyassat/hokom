#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn — Phase 4A: Wazn Projection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

طبقة مستقلة تُسقط الجذر المقبول (RootCandidate) على بنية السطح الصرفية
وتُنتج WaznProjection: مواقع الفاء/العين/اللام، الحروف الأصلية، الزيادات
المرشّحة، أثر الشدة/الهمزة/العلة، الأوزان الممكنة، والوزن المختار إن ثبت
وحيدًا.

هذه المرحلة:
  - تستهلك RootCandidate فقط (لا تستدعي HR2S، لا تعيد استخراج الجذر).
  - لا تستنتج الباب ولا تولّد المصدر أو المشتقات (ملك Phase 4B فصاعدًا).
  - لا تعدّل canonical_root إطلاقًا.

المدخل الرئيس: project_wazn(root_candidate, ...) → WaznProjection
"""

from .models import (
    WaznDirective,
    WaznStageState,
    RootSlot,
    AlignmentKind,
    WaznSlotAlignment,
    WaznCandidate,
    WaznProjection,
    WaznProjectionContractError,
    PROJECTION_VERSION,
)
from .wazn_projection import project_wazn

__all__ = [
    "WaznDirective",
    "WaznStageState",
    "RootSlot",
    "AlignmentKind",
    "WaznSlotAlignment",
    "WaznCandidate",
    "WaznProjection",
    "WaznProjectionContractError",
    "PROJECTION_VERSION",
    "project_wazn",
]

from .phase4a_orchestrator import Phase4AResult, project_wazn_with_relicensing
from .hypothesis import WaznHypothesis, ProposedRootResolution, build_wazn_hypothesis
from .ilaal import (
    WeakRadicalTransformation,
    TransformationTrace,
    IlaalHypothesis,
    IlaalResolution,
    LICENSED_TRANSFORMATIONS,
    apply_ilaal_resolution,
)

__all__ += [
    "Phase4AResult",
    "project_wazn_with_relicensing",
    "WaznHypothesis",
    "ProposedRootResolution",
    "build_wazn_hypothesis",
    "WeakRadicalTransformation",
    "TransformationTrace",
    "IlaalHypothesis",
    "IlaalResolution",
    "LICENSED_TRANSFORMATIONS",
    "apply_ilaal_resolution",
]
