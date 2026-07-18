#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/augmented_wazn.py — Augmented wazn shortcut (Phase 4A)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When source_engine == 'HOKOM_AUGMENTED_ENGINE', the wazn is already known
from the form family. This module builds Phase4AResult directly — bypassing
WaznHypothesis alignment — using the known wazn_id for Forms II–X.

المدخل الوحيد: build_augmented_phase4a()
"""

from __future__ import annotations

from pipeline.p4_wazn.models import (
    WaznDirective,
    WaznStageState,
    WaznCandidate,
    WaznProjection,
    PROJECTION_VERSION,
)
from pipeline.p4_wazn.phase4a_orchestrator import Phase4AResult


# ══════════════════════════════════════════════════════════════════════════════
# 1.  خريطة الأوزان المزيدة المعروفة
# ══════════════════════════════════════════════════════════════════════════════

# Tuple: (wazn_id, wazn_pattern, wazn_family)
# wazn_id values MUST match entries in data/wazn/wazn_catalog.json
# and the _MAZID_WAZN_TO_BAB map in pipeline/p4_bab/bab_rules.py.
AUGMENTED_WAZN_MAP: dict[str, tuple[str, str, str]] = {
    'FORM_II':   ('FA33ALA',   'فَعَّلَ',       'form_II_verb'),
    'FORM_III':  ('FA3ALA',    'فَاعَلَ',      'form_III_verb'),
    'FORM_IV':   ('AF3AL',     'أَفْعَلَ',      'form_IV_verb'),
    'FORM_V':    ('TAFA33ALA', 'تَفَعَّلَ',     'form_V_verb'),
    'FORM_VI':   ('TAFA3ALA',  'تَفَاعَلَ',    'form_VI_verb'),
    'FORM_VII':  ('INFA3ALA',  'اِنْفَعَلَ',   'form_VII_verb'),
    'FORM_VIII': ('IFTA3ALA',  'اِفْتَعَلَ',   'form_VIII_verb'),
    'FORM_IX':   ('IF3ALLA',   'اِفْعَلَّ',    'form_IX_verb'),
    'FORM_X':    ('ISTAF3ALA', 'اِسْتَفْعَلَ', 'form_X_verb'),
}


# ══════════════════════════════════════════════════════════════════════════════
# 2.  الدالة الرئيسة
# ══════════════════════════════════════════════════════════════════════════════

def build_augmented_phase4a(
    augmented_analysis,
    root_candidate,
    root_refinement=None,
) -> Phase4AResult:
    """
    Build Phase4AResult directly from augmented_analysis (Form II–X).

    Bypasses WaznHypothesis and project_wazn() alignment since the wazn
    is structurally known from the detected form family.

    Args:
        augmented_analysis : AugmentedRootAnalysis (p2_augmented.models)
        root_candidate     : RootCandidate (p3_candidate) — already ACCEPT
        root_refinement    : RootHostRefinement | None (for tracing only)

    Returns:
        Phase4AResult with:
          final_directive = 'ACCEPT'
          source_path     = 'augmented_direct'
          final_wazn      = wazn_id (e.g. 'FA33ALA' for FORM_II)
    """
    form_family = augmented_analysis.form_family
    entry = AUGMENTED_WAZN_MAP.get(form_family)

    # ── عائلة غير معروفة → DEFER (دفاعي) ────────────────────────────────────
    if entry is None:
        ev  = tuple(getattr(root_candidate, 'evidence_ids', ()) or ())
        tr  = tuple(getattr(root_candidate, 'trace_ids', ()) or ())
        res = tuple(getattr(root_candidate, 'residual_codes', ()) or ())
        return Phase4AResult(
            initial_root_directive = 'ACCEPT',
            final_directive        = 'DEFER',
            source_path            = 'augmented_direct:unknown_form',
            root_candidate         = root_candidate,
            promoted_root_candidate= None,
            wazn_hypothesis        = None,
            ilaal_resolution       = None,
            relicensing_result     = None,
            wazn_projection        = None,
            final_wazn             = None,
            evidence_ids           = ev,
            trace_ids              = tr,
            residual_codes         = res + (
                f'defer:wazn:unknown_augmented_form:{form_family}',),
        )

    wazn_id, wazn_pattern, wazn_family = entry
    canonical_root = tuple(augmented_analysis.trilateral_root)

    # ── جمع الشواهد من جميع الطبقات ─────────────────────────────────────────
    ev  = tuple(getattr(augmented_analysis, 'evidence_ids', ()) or ())
    tr  = tuple(getattr(augmented_analysis, 'trace_ids',   ()) or ())
    res = tuple(getattr(augmented_analysis, 'residual_codes', ()) or ())

    # لا نكرر — root_candidate يحمل نفس شواهد augmented_analysis عادةً
    rc_ev  = tuple(getattr(root_candidate, 'evidence_ids', ()) or ())
    rc_tr  = tuple(getattr(root_candidate, 'trace_ids',   ()) or ())
    rc_res = tuple(getattr(root_candidate, 'residual_codes', ()) or ())

    # دمج + إزالة تكرار (مع حفظ الترتيب)
    ev  = tuple(dict.fromkeys(ev  + rc_ev))
    tr  = tuple(dict.fromkeys(tr  + rc_tr))
    res = tuple(dict.fromkeys(res + rc_res))

    # أضف شاهد الوزن المباشر
    ev = ev + (f'augmented:wazn:{wazn_id}:direct',)
    tr = tr + ('p4a:augmented_direct',)

    # ── بناء WaznCandidate ───────────────────────────────────────────────────
    # alignment = () — لا محاذاة حرفية (الوزن مستنتج من عائلة الصيغة لا المحاذاة)
    selected_wazn = WaznCandidate(
        wazn_id             = wazn_id,
        wazn_pattern        = wazn_pattern,
        wazn_family         = wazn_family,
        alignment           = (),
        root_slots_complete = True,
        ziyadah_slots       = (),
        deleted_root_slots  = (),
        weak_operations     = (),
        confidence_rank     = 0,
        evidence_ids        = (f'augmented:wazn:{wazn_id}:direct',),
        residual_codes      = (),
    )

    # ── بناء WaznProjection ──────────────────────────────────────────────────
    wazn_proj = WaznProjection(
        input_surface         = root_candidate.surface,
        analyzed_host         = root_candidate.host_surface,
        normalized_host       = root_candidate.host_surface,
        canonical_root        = canonical_root,
        directive             = WaznDirective.ACCEPT,
        stage_state           = WaznStageState.COMPLETED,
        candidate_awzan       = (selected_wazn,),
        selected_wazn         = selected_wazn,
        root_slot_alignment   = (),
        ziyadah_slots         = (),
        weak_operations       = (),
        unresolved_operations = (),
        inflectional_suffixes = (),
        evidence_ids          = ev,
        trace_ids             = tr,
        residual_codes        = res,
        source_root_candidate = 'HOKOM_AUGMENTED_ENGINE',
        projection_version    = PROJECTION_VERSION,
    )

    # ── بناء Phase4AResult ───────────────────────────────────────────────────
    return Phase4AResult(
        initial_root_directive  = 'ACCEPT',
        final_directive         = 'ACCEPT',
        source_path             = 'augmented_direct',
        root_candidate          = root_candidate,
        promoted_root_candidate = None,
        wazn_hypothesis         = None,
        ilaal_resolution        = None,
        relicensing_result      = None,
        wazn_projection         = wazn_proj,
        final_wazn              = wazn_id,
        evidence_ids            = ev,
        trace_ids               = tr,
        residual_codes          = res,
    )
