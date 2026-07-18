#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_masdar/masdar_projection.py — إسقاط المصدر (Phase 4C)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ينتج MasdarProjection من Phase4AResult و Phase4BResult (الاختياري).

شروط الفتح:
  - Phase4A ACCEPT مطلوب.
  - phase4b_result قد يكون None (وزن لا باب — Phase4B لم يُفتح) أو
    Phase4BResult بأي directive.
  - Phase4B BLOCK → ينتشر BLOCK إلى المصدر.

التوجيهات:
  ACCEPT      — استنتاج هيكلي من صيغة مزيدة (FORM_II–FORM_X).
  DEFER       — باب مجرد (سماعي مطلوب) أو باب غامض أو أنماط متعددة.
  BLOCK       — BLOCK من Phase4B ينتشر، أو تناقض هيكلي.
  NOT_OPENED  — Phase4A لم يقبل.
  NOT_APPLICABLE — وزن اسمي لا فعلي.
"""

from __future__ import annotations

from pipeline.p4_masdar.masdar_hypothesis import generate_masdar_candidates
from pipeline.p4_masdar.masdar_rules import (
    assess_masdar_applicability,
    get_wazn_family_from_wazn_id,
)
from pipeline.p4_masdar.models import MasdarCandidate, MasdarProjection


def project_masdar(
    phase4a_result,
    phase4b_result=None,
    evidence_ids: tuple = (),
    trace_ids: tuple = (),
) -> MasdarProjection:
    """
    أنتِج MasdarProjection من Phase4AResult و Phase4BResult (الاختياري).

    Args:
        phase4a_result : Phase4AResult — مطلوب.
        phase4b_result : Phase4BResult | None — اختياري.
        evidence_ids   : شواهد إضافية.
        trace_ids      : مسار إضافي.

    Returns:
        MasdarProjection
    """
    # ── استخراج البيانات من Phase4A ────────────────────────────────────────
    p4a_directive = getattr(phase4a_result, 'final_directive', None)

    wazn_projection = getattr(phase4a_result, 'wazn_projection', None)
    selected_wazn   = getattr(wazn_projection, 'selected_wazn', None) if wazn_projection else None
    wazn_id         = getattr(selected_wazn, 'wazn_id', None) if selected_wazn else None
    canonical_root  = getattr(wazn_projection, 'canonical_root', None) if wazn_projection else None

    # استرجاع عائلة الوزن
    wazn_family = None
    if selected_wazn is not None:
        wazn_family = getattr(selected_wazn, 'wazn_family', None)
    if wazn_family is None and wazn_id is not None:
        wazn_family = get_wazn_family_from_wazn_id(wazn_id)

    # ── استخراج البيانات من Phase4B ────────────────────────────────────────
    p4b_directive = None
    bab_id        = None
    if phase4b_result is not None:
        p4b_directive = getattr(phase4b_result, 'final_directive', None)
        bab_id        = getattr(phase4b_result, 'final_bab', None)

    # ── تقييم القابلية ─────────────────────────────────────────────────────
    applicability = assess_masdar_applicability(
        phase4a_directive = p4a_directive,
        wazn_family       = wazn_family,
        phase4b_directive = p4b_directive,
    )

    # ── Phase4A لم تُقبَل → NOT_OPENED ──────────────────────────────────────
    if applicability == 'NOT_OPENED':
        return MasdarProjection(
            directive               = 'NOT_OPENED',
            stage_state             = 'NOT_OPENED',
            applicability           = 'NOT_OPENED',
            candidate_masadir       = (),
            selected_masdar         = None,
            selected_masdar_pattern = None,
            source_type             = None,
            source_wazn             = wazn_id,
            bab_id                  = bab_id,
            canonical_root          = canonical_root,
            evidence_ids            = evidence_ids,
            trace_ids               = trace_ids,
            residual_codes          = ('phase4a_not_accept',),
        )

    # ── الوزن اسمي → NOT_APPLICABLE ──────────────────────────────────────────
    if applicability == 'NOT_APPLICABLE':
        return MasdarProjection(
            directive               = 'NOT_APPLICABLE',
            stage_state             = 'NOT_APPLICABLE',
            applicability           = 'NOT_APPLICABLE',
            candidate_masadir       = (),
            selected_masdar         = None,
            selected_masdar_pattern = None,
            source_type             = None,
            source_wazn             = wazn_id,
            bab_id                  = bab_id,
            canonical_root          = canonical_root,
            evidence_ids            = evidence_ids,
            trace_ids               = trace_ids,
            residual_codes          = ('non_verbal_wazn',),
        )

    # ── Phase4B BLOCK ينتشر → BLOCK ──────────────────────────────────────────
    if p4b_directive == 'BLOCK':
        return MasdarProjection(
            directive               = 'BLOCK',
            stage_state             = 'OPENED',
            applicability           = applicability,
            candidate_masadir       = (),
            selected_masdar         = None,
            selected_masdar_pattern = None,
            source_type             = None,
            source_wazn             = wazn_id,
            bab_id                  = bab_id,
            canonical_root          = canonical_root,
            evidence_ids            = evidence_ids,
            trace_ids               = trace_ids,
            residual_codes          = ('phase4b_block_propagated',),
        )

    # ── توليد المرشحات ────────────────────────────────────────────────────────
    candidates = generate_masdar_candidates(
        bab_id         = bab_id,
        wazn_id        = wazn_id,
        wazn_family    = wazn_family,
        canonical_root = canonical_root,
        evidence_ids   = evidence_ids,
        trace_ids      = trace_ids,
    )

    # ── تقييم المرشحات ────────────────────────────────────────────────────────
    structural_candidates = [
        c for c in candidates
        if c.source_type == "STRUCTURAL_INFERENCE" and c.masdar_pattern is not None
    ]
    sami3i_candidates = [
        c for c in candidates
        if c.source_type == "SAMI3I_REQUIRED"
    ]

    # ACCEPT: مرشح هيكلي واحد واضح من صيغة مزيدة
    if len(structural_candidates) == 1:
        chosen = structural_candidates[0]
        return MasdarProjection(
            directive               = 'ACCEPT',
            stage_state             = 'OPENED',
            applicability           = applicability,
            candidate_masadir       = tuple(candidates),
            selected_masdar         = chosen.masdar_surface,
            selected_masdar_pattern = chosen.masdar_pattern,
            source_type             = chosen.source_type,
            source_wazn             = wazn_id,
            bab_id                  = bab_id,
            canonical_root          = canonical_root,
            evidence_ids            = evidence_ids + chosen.evidence_ids,
            trace_ids               = trace_ids + chosen.trace_ids,
            residual_codes          = chosen.residual_codes,
        )

    # DEFER: مجرد (سماعي مطلوب) أو باب غامض أو لا مرشح
    if sami3i_candidates or not candidates:
        residuals = ('sami3i_required',) if sami3i_candidates else ('no_masdar_candidate',)
        return MasdarProjection(
            directive               = 'DEFER',
            stage_state             = 'OPENED',
            applicability           = applicability,
            candidate_masadir       = tuple(candidates),
            selected_masdar         = None,
            selected_masdar_pattern = None,
            source_type             = (sami3i_candidates[0].source_type
                                       if sami3i_candidates else None),
            source_wazn             = wazn_id,
            bab_id                  = bab_id,
            canonical_root          = canonical_root,
            evidence_ids            = evidence_ids,
            trace_ids               = trace_ids,
            residual_codes          = residuals,
        )

    # DEFER: أنماط متعددة متساوية
    if len(structural_candidates) > 1:
        return MasdarProjection(
            directive               = 'DEFER',
            stage_state             = 'OPENED',
            applicability           = applicability,
            candidate_masadir       = tuple(candidates),
            selected_masdar         = None,
            selected_masdar_pattern = None,
            source_type             = 'STRUCTURAL_INFERENCE',
            source_wazn             = wazn_id,
            bab_id                  = bab_id,
            canonical_root          = canonical_root,
            evidence_ids            = evidence_ids,
            trace_ids               = trace_ids,
            residual_codes          = ('multiple_structural_patterns',),
        )

    # احتياط: DEFER
    return MasdarProjection(
        directive               = 'DEFER',
        stage_state             = 'OPENED',
        applicability           = applicability,
        candidate_masadir       = tuple(candidates),
        selected_masdar         = None,
        selected_masdar_pattern = None,
        source_type             = None,
        source_wazn             = wazn_id,
        bab_id                  = bab_id,
        canonical_root          = canonical_root,
        evidence_ids            = evidence_ids,
        trace_ids               = trace_ids,
        residual_codes          = ('masdar_unresolved',),
    )
