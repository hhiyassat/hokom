#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_bab/bab_projection.py — إسقاط الباب على Phase4AResult
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

project_bab() — المدخل الوحيد.

منطق الإسقاط:
  1. إن Phase4A ليس ACCEPT → NOT_OPENED (stage_state=NOT_OPENED)
  2. إن الوزن اسمي → NOT_APPLICABLE (stage_state=NOT_APPLICABLE)
  3. أنتِج المرشحين عبر generate_bab_candidates()
  4. إن 0 مرشحين → DEFER (لا تطابق في catalog)
  5. إن 1 مرشح + confidence='HIGH' → ACCEPT
  6. إن 1 مرشح + confidence='DEFER_REQUIRED' → DEFER
  7. إن 1 مرشح + confidence='CONTRADICTION' → BLOCK
  8. إن > 1 مرشح (كلهم DEFER_REQUIRED) → DEFER
  9. إن > 1 مرشح (بعضهم CONTRADICTION) → BLOCK

عائلات الأوزان الفعلية من wazn_catalog:
  triliteral_bare_verb, form_II_verb, form_III_verb, form_IV_verb,
  form_V_verb, form_VI_verb, form_VII_verb, form_VIII_verb, form_X_verb
"""

from __future__ import annotations

from typing import Any

from .bab_hypothesis import generate_bab_candidates
from .bab_rules import is_verbal_family
from .models import BabCandidate, BabProjection


# ── تعيين عائلة wazn_catalog إلى wazn_family للـ generate_bab_candidates ─
_WAZN_FAMILY_MAP: dict[str, str] = {
    "triliteral_bare_verb": "triliteral_bare_verb",
    "form_II_verb":         "form_II_verb",
    "form_III_verb":        "form_III_verb",
    "form_IV_verb":         "form_IV_verb",
    "form_V_verb":          "form_V_verb",
    "form_VI_verb":         "form_VI_verb",
    "form_VII_verb":        "form_VII_verb",
    "form_VIII_verb":       "form_VIII_verb",
    "form_X_verb":          "form_X_verb",
}


def _not_opened(
    source_wazn: str | None,
    canonical_root: tuple | None,
    evidence_ids: tuple,
    trace_ids: tuple,
    residual_codes: tuple,
) -> BabProjection:
    """بنِّ BabProjection من نوع NOT_OPENED."""
    return BabProjection(
        directive       = 'NOT_OPENED',
        stage_state     = 'NOT_OPENED',
        candidate_abwab = (),
        selected_bab    = None,
        source_wazn     = source_wazn,
        canonical_root  = canonical_root,
        applicability   = 'UNKNOWN',
        evidence_ids    = evidence_ids,
        trace_ids       = trace_ids,
        residual_codes  = residual_codes,
    )


def _not_applicable(
    source_wazn: str | None,
    canonical_root: tuple | None,
    evidence_ids: tuple,
    trace_ids: tuple,
    residual_codes: tuple,
) -> BabProjection:
    """بنِّ BabProjection من نوع NOT_APPLICABLE (وزن اسمي)."""
    return BabProjection(
        directive       = 'NOT_OPENED',
        stage_state     = 'NOT_APPLICABLE',
        candidate_abwab = (),
        selected_bab    = None,
        source_wazn     = source_wazn,
        canonical_root  = canonical_root,
        applicability   = 'NOT_APPLICABLE',
        evidence_ids    = evidence_ids,
        trace_ids       = trace_ids,
        residual_codes  = residual_codes + ('bab:nominal:not_applicable',),
    )


def project_bab(
    phase4a_result: Any,
    evidence_ids: tuple = (),
    trace_ids:    tuple = (),
) -> BabProjection:
    """
    أسقِط الباب من Phase4AResult.

    phase4a_result : Phase4AResult (من phase4a_orchestrator)
    evidence_ids   : شواهد إضافية (اختياري)
    trace_ids      : مسار إضافي (اختياري)

    الإرجاع: BabProjection
    """
    # ── تجميع شواهد Phase4A ───────────────────────────────────────────────
    p4a_ev  = tuple(getattr(phase4a_result, 'evidence_ids',   ()) or ())
    p4a_tr  = tuple(getattr(phase4a_result, 'trace_ids',      ()) or ())
    p4a_res = tuple(getattr(phase4a_result, 'residual_codes', ()) or ())

    all_ev  = p4a_ev  + tuple(evidence_ids)
    all_tr  = p4a_tr  + tuple(trace_ids)
    all_res = p4a_res

    # ── الخطوة 1: Phase4A يجب أن يكون ACCEPT ────────────────────────────────
    final_directive = str(getattr(phase4a_result, 'final_directive', '') or '').upper()
    if final_directive != 'ACCEPT':
        return _not_opened(
            source_wazn     = getattr(phase4a_result, 'final_wazn', None),
            canonical_root  = _get_canonical_root(phase4a_result),
            evidence_ids    = all_ev,
            trace_ids       = all_tr + ('p4b:not_opened:phase4a_not_accept',),
            residual_codes  = all_res + ('bab:not_opened:phase4a_directive_not_accept',),
        )

    # ── الخطوة 2: احصل على wazn_id وعائلة الوزن ──────────────────────────
    past_wazn  = getattr(phase4a_result, 'final_wazn', None)
    wp         = getattr(phase4a_result, 'wazn_projection', None)
    sw         = getattr(wp, 'selected_wazn', None) if wp is not None else None
    wazn_fam   = getattr(sw, 'wazn_family', None) if sw is not None else None
    canonical  = _get_canonical_root(phase4a_result)

    # ── الخطوة 3: تحقق من الأهلية الفعلية ──────────────────────────────────
    if not is_verbal_family(wazn_fam):
        return _not_applicable(
            source_wazn    = past_wazn,
            canonical_root = canonical,
            evidence_ids   = all_ev,
            trace_ids      = all_tr + ('p4b:not_applicable:nominal_wazn',),
            residual_codes = all_res,
        )

    if past_wazn is None:
        # ACCEPT لكن لا wazn_id (حالة غير متوقعة) → DEFER
        return BabProjection(
            directive       = 'DEFER',
            stage_state     = 'OPENED',
            candidate_abwab = (),
            selected_bab    = None,
            source_wazn     = None,
            canonical_root  = canonical,
            applicability   = 'APPLICABLE',
            evidence_ids    = all_ev,
            trace_ids       = all_tr + ('p4b:defer:no_wazn_id',),
            residual_codes  = all_res + ('bab:defer:wazn_id_missing',),
        )

    # ── الخطوة 4: توليد المرشحين ─────────────────────────────────────────────
    candidates = generate_bab_candidates(
        past_wazn      = past_wazn,
        imperfect_wazn = None,
        canonical_root = canonical,
        evidence_ids   = all_ev,
        trace_ids      = all_tr,
        wazn_family    = wazn_fam,
    )

    # ── الخطوة 5: الحكم من المرشحين ──────────────────────────────────────────
    return _decide_from_candidates(
        candidates     = candidates,
        source_wazn    = past_wazn,
        canonical_root = canonical,
        evidence_ids   = all_ev,
        trace_ids      = all_tr,
        residual_codes = all_res,
    )


def _get_canonical_root(phase4a_result: Any) -> tuple | None:
    """استخرج canonical_root من Phase4AResult (عبر wazn_projection)."""
    wp = getattr(phase4a_result, 'wazn_projection', None)
    if wp is not None:
        cr = getattr(wp, 'canonical_root', None)
        if cr is not None:
            return tuple(cr)
    # fallback: من promoted أو root_candidate
    for attr in ('promoted_root_candidate', 'root_candidate'):
        rc = getattr(phase4a_result, attr, None)
        if rc is not None:
            cr = getattr(rc, 'canonical_root', None)
            if cr is not None:
                return tuple(cr)
    return None


def _decide_from_candidates(
    candidates:     list[BabCandidate],
    source_wazn:    str | None,
    canonical_root: tuple | None,
    evidence_ids:   tuple,
    trace_ids:      tuple,
    residual_codes: tuple,
) -> BabProjection:
    """حدِّد directive بناءً على قائمة المرشحين."""

    # ── لا مرشحين → DEFER ────────────────────────────────────────────────────
    if not candidates:
        return BabProjection(
            directive       = 'DEFER',
            stage_state     = 'OPENED',
            candidate_abwab = (),
            selected_bab    = None,
            source_wazn     = source_wazn,
            canonical_root  = canonical_root,
            applicability   = 'APPLICABLE',
            evidence_ids    = evidence_ids,
            trace_ids       = trace_ids + ('p4b:defer:no_candidates',),
            residual_codes  = residual_codes + ('bab:defer:no_catalog_match',),
        )

    # ── تحقق من وجود CONTRADICTION ───────────────────────────────────────────
    contradictions = [c for c in candidates if c.confidence == 'CONTRADICTION']
    if contradictions:
        return BabProjection(
            directive       = 'BLOCK',
            stage_state     = 'OPENED',
            candidate_abwab = tuple(candidates),
            selected_bab    = None,
            source_wazn     = source_wazn,
            canonical_root  = canonical_root,
            applicability   = 'APPLICABLE',
            evidence_ids    = evidence_ids,
            trace_ids       = trace_ids + ('p4b:block:contradiction',),
            residual_codes  = residual_codes + ('bab:block:vowel_contradiction',),
        )

    # ── مرشّح واحد HIGH → ACCEPT ─────────────────────────────────────────────
    if len(candidates) == 1 and candidates[0].confidence == 'HIGH':
        c = candidates[0]
        return BabProjection(
            directive       = 'ACCEPT',
            stage_state     = 'OPENED',
            candidate_abwab = (c,),
            selected_bab    = c.bab_id,
            source_wazn     = source_wazn,
            canonical_root  = canonical_root,
            applicability   = 'APPLICABLE',
            evidence_ids    = c.evidence_ids,
            trace_ids       = c.trace_ids,
            residual_codes  = residual_codes + c.residual_codes,
        )

    # ── أي حالة أخرى (DEFER_REQUIRED، أو أكثر من مرشح) → DEFER ─────────────
    return BabProjection(
        directive       = 'DEFER',
        stage_state     = 'OPENED',
        candidate_abwab = tuple(candidates),
        selected_bab    = None,
        source_wazn     = source_wazn,
        canonical_root  = canonical_root,
        applicability   = 'APPLICABLE',
        evidence_ids    = evidence_ids,
        trace_ids       = trace_ids + ('p4b:defer:ambiguous_or_insufficient',),
        residual_codes  = (residual_codes
                           + tuple(c.residual_codes[0] for c in candidates
                                   if c.residual_codes)[:1]),
    )
