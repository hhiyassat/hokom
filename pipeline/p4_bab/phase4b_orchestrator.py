#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_bab/phase4b_orchestrator.py — Phase 4B Orchestrator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

المدخل الرئيس: project_bab_with_licensing()

يغلّف project_bab() ويُنتج Phase4BResult.

المسارات:
  direct_accept  — مرشّح واحد، دليل كافٍ → ACCEPT
  deferred       — غامض أو دليل غير كافٍ → DEFER
  blocked        — تناقض → BLOCK
  not_opened     — Phase4A لم يُقبَل
  not_applicable — وزن اسمي أو مسار اسمي

القانون الأساسي:
  final_directive يأتي دائمًا من BabProjection.directive
  أو من حكم المسار المغلق ('NOT_OPENED'/'NOT_APPLICABLE').
  source_path يصف المسار — لا يحدد الحكم.

Fix 5/6: morphology_path parameter gates nominal words as NOT_APPLICABLE.
Fix 8:   Resolved residuals (defer:root:*) are filtered when Phase4A
         accepted via hypothesis_relicensing.
Fix 9:   All residual_codes tuples are deduplicated (order-preserving).
"""

from __future__ import annotations

from typing import Any, Optional

from .bab_projection import project_bab
from .models import BabProjection, Phase4BResult

# Nominal morphology path values that gate Bab analysis
_NOMINAL_PATH_VALUES = frozenset({
    'nominal_morphology_path',
})


def deduplicate_residuals(residuals: tuple) -> tuple:
    """Return a deduplicated (order-preserving) copy of residuals tuple."""
    return tuple(dict.fromkeys(residuals))


def _partition_residuals(
    residuals: tuple,
    phase4a_result: Any,
) -> tuple:
    """
    Filter out residuals that were resolved by Phase4A relicensing.

    When Phase4A accepted via hypothesis_relicensed, all defer:root:*
    residuals generated before relicensing are RESOLVED (not active).
    They should not propagate to Phase4B/C/D as if they were open issues.
    """
    source_path = str(getattr(phase4a_result, 'source_path', '') or '')
    final_dir   = str(getattr(phase4a_result, 'final_directive', '') or '').upper()

    if source_path == 'hypothesis_relicensed' and final_dir == 'ACCEPT':
        # Remove pre-relicensing defer:root:* residuals — they are resolved.
        residuals = tuple(r for r in residuals if not r.startswith('defer:root:'))

    return residuals


def project_bab_with_licensing(
    phase4a_result: Any,
    root_refinement: Any = None,
    morphology_path: Optional[str] = None,
) -> Phase4BResult:
    """
    أسقِط Phase4AResult إلى Phase4BResult عبر BabProjection.

    phase4a_result  : Phase4AResult (من pipeline.p4_wazn.phase4a_orchestrator)
    root_refinement : RootHostRefinement (اختياري — للتتبع فقط، لا يؤثر في الحكم)
    morphology_path : str | None — MorphologyPath.value من PreRootDecision.
                      إذا كان 'nominal_morphology_path' → NOT_APPLICABLE مباشرة.

    الإرجاع: Phase4BResult
    """
    # الحكم المبدئي من Phase4A
    initial_directive = str(getattr(phase4a_result, 'final_directive', '') or '').upper()

    # ── حالة NOT_OPENED المباشرة (Phase4A لم يُقبَل) ────────────────────────
    if initial_directive != 'ACCEPT':
        ev  = tuple(getattr(phase4a_result, 'evidence_ids',   ()) or ())
        tr  = tuple(getattr(phase4a_result, 'trace_ids',      ()) or ())
        res = tuple(getattr(phase4a_result, 'residual_codes', ()) or ())
        res = deduplicate_residuals(res)

        return Phase4BResult(
            initial_wazn_directive = initial_directive,
            final_directive        = 'NOT_OPENED',
            bab_projection         = None,
            final_bab              = None,
            source_path            = 'not_opened',
            evidence_ids           = ev,
            trace_ids              = tr + ('p4b:not_opened',),
            residual_codes         = res + ('bab:not_opened:phase4a_not_accept',),
        )

    # Fix 5/6: Nominal morphology path → NOT_APPLICABLE for Bab analysis.
    # Nouns should not enter the verbal Bab analysis even if their refined
    # host surface looks like a فَعَلَ (FA_A_LA) verb form.
    if morphology_path in _NOMINAL_PATH_VALUES:
        ev  = tuple(getattr(phase4a_result, 'evidence_ids',   ()) or ())
        tr  = tuple(getattr(phase4a_result, 'trace_ids',      ()) or ())
        res = tuple(getattr(phase4a_result, 'residual_codes', ()) or ())
        res = _partition_residuals(res, phase4a_result)
        res = deduplicate_residuals(res)

        return Phase4BResult(
            initial_wazn_directive = initial_directive,
            final_directive        = 'NOT_APPLICABLE',
            bab_projection         = None,
            final_bab              = None,
            source_path            = 'not_applicable',
            evidence_ids           = ev,
            trace_ids              = tr + ('p4b:not_applicable:nominal_morphology_path',),
            residual_codes         = res + ('defer:bab:nominal_morphology_path',),
        )

    # ── إسقاط الباب ─────────────────────────────────────────────────────────
    bab_proj = project_bab(phase4a_result)

    # Fix 8: Filter resolved residuals before propagating.
    # Fix 9: Deduplicate.
    bab_residuals = _partition_residuals(bab_proj.residual_codes, phase4a_result)
    bab_residuals = deduplicate_residuals(bab_residuals)

    # ── تحديد source_path من directive/stage_state ──────────────────────────
    source_path    = _source_path_from_projection(bab_proj)
    final_dir      = _final_directive_from_projection(bab_proj)

    return Phase4BResult(
        initial_wazn_directive = initial_directive,
        final_directive        = final_dir,
        bab_projection         = bab_proj,
        final_bab              = bab_proj.selected_bab,
        source_path            = source_path,
        evidence_ids           = bab_proj.evidence_ids,
        trace_ids              = bab_proj.trace_ids,
        residual_codes         = bab_residuals,
    )


def _source_path_from_projection(bab_proj: BabProjection) -> str:
    """اشتق source_path من BabProjection."""
    directive   = bab_proj.directive
    stage_state = bab_proj.stage_state

    if stage_state == 'NOT_APPLICABLE':
        return 'not_applicable'
    if stage_state == 'NOT_OPENED':
        return 'not_opened'
    if directive == 'ACCEPT':
        return 'direct_accept'
    if directive == 'BLOCK':
        return 'blocked'
    return 'deferred'


def _final_directive_from_projection(bab_proj: BabProjection) -> str:
    """اشتق final_directive من BabProjection."""
    stage_state = bab_proj.stage_state

    if stage_state == 'NOT_APPLICABLE':
        return 'NOT_APPLICABLE'
    if stage_state == 'NOT_OPENED':
        return 'NOT_OPENED'
    return bab_proj.directive
