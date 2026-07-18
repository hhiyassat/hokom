#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_augmented/augmented_host_refinement.py — الواجهة العامة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

طبقة AugmentedHostRefinement — تكتشف أفعال المزيد وتُنتج AugmentedRootAnalysis
مباشرةً إذا كان السطح يطابق نمطًا مزيدًا (Form II–X).

موقع معماري:
  refined_host (من RootHostRefinement)
    ↓
  analyze_augmented_host()   ← هنا
    ├── إذا طابق نمطًا مزيدًا → AugmentedRootAnalysis
    └── وإلا → None (المحرك الثلاثي يأخذ الزمام)
"""

from __future__ import annotations

from typing import Optional

from pipeline.p2_augmented.models import AugmentedRootAnalysis
from pipeline.p2_augmented.detector import detect_augmented


# ── رمز التحفظ للجذر الضعيف ────────────────────────────────────────────────
_WEAK_RADICAL_CODE = 'note:augmented:weak_radical_in_root'
_LOW_CONF_CODE     = 'note:augmented:low_confidence_pattern'

# مصدر المحرك
SOURCE_ENGINE = 'HOKOM_AUGMENTED_ENGINE'


def analyze_augmented_host(
    refined_host:   str,
    original_host:  str,
    morphology_path: Optional[str] = None,
    evidence_ids:   tuple = (),
    trace_ids:      tuple = (),
) -> Optional[AugmentedRootAnalysis]:
    """
    حلِّل المضيف المنقَّح بحثًا عن نمط فعل مزيد (Form II–X).

    Parameters
    ----------
    refined_host    : سطح المضيف بعد التنقية (لاحقة تاء التأنيث مُزالة مسبقًا).
    original_host   : السطح الأصلي (للتسجيل).
    morphology_path : السياق الصرفي (اختياري — للتسجيل فقط).
    evidence_ids    : مرجعيات الشواهد المُورَثة.
    trace_ids       : مسارات التحليل المُورَثة.

    Returns
    -------
    AugmentedRootAnalysis إذا طابق السطح نمطًا مزيدًا، أو None.
    """
    if not refined_host:
        return None

    # ── اكتشاف النمط ─────────────────────────────────────────────────────────
    detection = detect_augmented(refined_host)
    if detection is None:
        return None

    # ── بناء رموز التحفظ ─────────────────────────────────────────────────────
    residuals: list[str] = []
    confidence = detection.confidence_hint

    # جذر يحتوي حرف علة → MEDIUM على الأقل + رمز تحفظ
    has_weak = any(c in 'وي' for c in detection.root)
    if has_weak and confidence == 'HIGH':
        confidence = 'MEDIUM'
    if has_weak:
        residuals.append(_WEAK_RADICAL_CODE)
    if confidence == 'LOW':
        residuals.append(_LOW_CONF_CODE)

    # ── رمز التتبع ───────────────────────────────────────────────────────────
    new_trace = f'augmented_host_refinement:{detection.form_family}:{refined_host}'
    all_trace_ids = tuple(trace_ids) + (new_trace,)

    # ── بناء AugmentedRootAnalysis ────────────────────────────────────────────
    return AugmentedRootAnalysis(
        form_family      = detection.form_family,
        trilateral_root  = tuple(detection.root),
        past_surface     = refined_host,   # السطح الذي استُخلص منه
        imperfect_prefix = detection.imperfect_prefix,
        confidence       = confidence,
        evidence_ids     = tuple(evidence_ids),
        trace_ids        = all_trace_ids,
        residual_codes   = tuple(residuals),
    )
