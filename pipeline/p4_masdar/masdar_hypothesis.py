#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_masdar/masdar_hypothesis.py — توليد مرشحات المصدر
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يولّد قائمة MasdarCandidate من bab_id و wazn_id وبيانات Phase4A/B.

المنطق:
  - إن كان bab_id صيغة مزيدة (BAB_FORM_II–BAB_FORM_X):
      ابحث في catalog بـ bab_id → مرشح STRUCTURAL_INFERENCE
  - إن كان bab_id مجردًا (BAB_I_NASARA–BAB_VI_HASIBA):
      لا تنبؤ هيكلي → مرشح SAMI3I_REQUIRED فارغ النمط
  - إن كان bab_id = None لكن wazn_id يحدد صيغة مزيدة بشكل فريد:
      استخدم wazn_id للبحث في catalog → مرشح STRUCTURAL_INFERENCE
  - لا تُضمِّن أشكالًا سطحية محددة لجذور بعينها.
"""

from __future__ import annotations

from pipeline.p4_masdar.masdar_catalog import (
    get_masdar_by_bab,
    get_masdar_by_wazn,
)
from pipeline.p4_masdar.models import MasdarCandidate

# أبواب مجرد معروفة
_MUJARRAD_BAB_IDS = frozenset({
    "BAB_I_NASARA",
    "BAB_II_DARABA",
    "BAB_III_FATAHA",
    "BAB_IV_SAMIA",
    "BAB_V_KARUMA",
    "BAB_VI_HASIBA",
})

# أبواب مزيدة معروفة
_MAZID_BAB_IDS = frozenset({
    "BAB_FORM_II",
    "BAB_FORM_III",
    "BAB_FORM_IV",
    "BAB_FORM_V",
    "BAB_FORM_VI",
    "BAB_FORM_VII",
    "BAB_FORM_VIII",
    "BAB_FORM_IX",
    "BAB_FORM_X",
})


def generate_masdar_candidates(
    bab_id: str | None,
    wazn_id: str | None,
    wazn_family: str | None,
    canonical_root: tuple | None,
    evidence_ids: tuple,
    trace_ids: tuple,
) -> list[MasdarCandidate]:
    """
    ولّد مرشحات المصدر من المعطيات المتوفرة.

    Args:
        bab_id         : معرّف الباب من Phase4B أو None.
        wazn_id        : معرّف الوزن من Phase4A.
        wazn_family    : عائلة الوزن (triliteral_bare_verb | form_II_verb | ...).
        canonical_root : الجذر الكنوني أو None.
        evidence_ids   : شواهد لتمريرها للمرشحات.
        trace_ids      : مسار لتمريره للمرشحات.

    Returns:
        قائمة MasdarCandidate (فارغة إن لم يُعثر على مرشح صالح).
    """
    candidates: list[MasdarCandidate] = []

    # ── المسار 1: bab_id موجود ───────────────────────────────────────────────
    if bab_id is not None:
        # أ. باب مجرد: سماعي
        if bab_id in _MUJARRAD_BAB_IDS:
            defn = get_masdar_by_bab(bab_id)
            candidates.append(MasdarCandidate(
                masdar_id      = f"MASDAR_SAMI3I_{bab_id}",
                masdar_surface = None,
                masdar_pattern = None,
                source_type    = "SAMI3I_REQUIRED",
                confidence     = "DEFER_REQUIRED",
                evidence_ids   = evidence_ids + ('sami3i_required',),
                trace_ids      = trace_ids,
                residual_codes = ('sami3i_required',),
            ))
            return candidates

        # ب. باب مزيد: استنتاج هيكلي
        if bab_id in _MAZID_BAB_IDS:
            defn = get_masdar_by_bab(bab_id)
            if defn is not None and defn.masdar_pattern is not None:
                candidates.append(MasdarCandidate(
                    masdar_id      = defn.masdar_id,
                    masdar_surface = defn.masdar_pattern,   # النمط هو الشكل في السياق الهيكلي
                    masdar_pattern = defn.masdar_pattern,
                    source_type    = "STRUCTURAL_INFERENCE",
                    confidence     = "HIGH",
                    evidence_ids   = evidence_ids + tuple(defn.evidence_required),
                    trace_ids      = trace_ids,
                    residual_codes = (),
                ))
            return candidates

        # ج. bab_id غير مصنَّف: حاول via wazn
        # (يتسقط إلى المسار 2 أدناه)

    # ── المسار 2: bab_id غير موجود، ابحث عبر wazn_id ────────────────────────
    if wazn_id is not None:
        defn = get_masdar_by_wazn(wazn_id)
        if defn is not None:
            if defn.source_type == "SAMI3I_REQUIRED":
                candidates.append(MasdarCandidate(
                    masdar_id      = f"MASDAR_SAMI3I_{wazn_id}",
                    masdar_surface = None,
                    masdar_pattern = None,
                    source_type    = "SAMI3I_REQUIRED",
                    confidence     = "DEFER_REQUIRED",
                    evidence_ids   = evidence_ids + ('sami3i_required',),
                    trace_ids      = trace_ids,
                    residual_codes = ('sami3i_required',),
                ))
            elif defn.masdar_pattern is not None:
                candidates.append(MasdarCandidate(
                    masdar_id      = defn.masdar_id,
                    masdar_surface = defn.masdar_pattern,
                    masdar_pattern = defn.masdar_pattern,
                    source_type    = "STRUCTURAL_INFERENCE",
                    confidence     = "MEDIUM",   # MEDIUM: wazn-based not bab-confirmed
                    evidence_ids   = evidence_ids + tuple(defn.evidence_required),
                    trace_ids      = trace_ids,
                    residual_codes = ('bab_unconfirmed',),
                ))
            return candidates

    # ── المسار 3: لا bab_id ولا wazn_id قابل للحل ──────────────────────────
    # إن كانت العائلة معروفة كمجردة → سماعي
    if wazn_family == "triliteral_bare_verb":
        candidates.append(MasdarCandidate(
            masdar_id      = "MASDAR_SAMI3I_BARE_VERB",
            masdar_surface = None,
            masdar_pattern = None,
            source_type    = "SAMI3I_REQUIRED",
            confidence     = "DEFER_REQUIRED",
            evidence_ids   = evidence_ids + ('sami3i_required',),
            trace_ids      = trace_ids,
            residual_codes = ('sami3i_required', 'bab_unknown'),
        ))

    return candidates
