#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_candidate/root_resolution_orchestrator.py — Hokom Root Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُشغِّل تسلسل Hokom المحلي الكامل:

  original_host (السطح الأصلي)
    → refined_host (بعد فصل اللواحق الطرفية، ممرَّر من الخارج)
      → RootResolution   (resolve_root — المحرك المحلي)
        → RootProjection  (from_root_resolution — P2)
          → RootCandidate  (from_projection — P3)

host threading (الخيط الرئيسي):
  refined_host → RootResolution.analyzed_host
              → RootProjection.analyzed_host
              → RootCandidate.host_surface

القيود:
  - لا استيراد من hr2s الداخلي.
  - لا مسارات مطلقة.
  - لا استثناءات نصية خاصة بكلمات.
  - HR2S = مرجع مقارنة فقط (لا يُستدعى من هنا).
"""

from __future__ import annotations

from pipeline.p3_candidate.root_resolution import resolve_root
from pipeline.p2_projection.root_projection import RootProjection
from pipeline.p3_candidate.root_candidate import RootCandidate


def resolve_root_pipeline(
    original_host: str,
    refined_host: str,
    pre_root_directive: str,
    morphology_path: str = '',
    evidence_ids: tuple = (),
    trace_ids: tuple = (),
) -> RootCandidate:
    """شغِّل تسلسل Hokom المحلي الكامل وأعد RootCandidate.

    Parameters
    ----------
    original_host       : السطح الأصلي (يُحفظ كـ input_surface في Projection).
    refined_host        : المضيف بعد فصل اللواحق (يسير كـ analyzed_host في السلسلة).
    pre_root_directive  : 'OPEN' | 'DEFER' | 'BLOCK'
    morphology_path     : سياق المسار الصرفي (اختياري).
    evidence_ids        : مرجعيات الشواهد.
    trace_ids           : مسارات التحليل.

    Returns
    -------
    RootCandidate — نتيجة المحرك المحلي، مع:
      .host_surface    = refined_host
      .canonical_root  = جذر أو None
      .directive       = 'ACCEPT' | 'DEFER' | 'BLOCK'
      .root_profile    = {'source_engine': 'HOKOM_ROOT_ENGINE', ...}
    """
    # ── 1: RootResolution (المحرك المحلي) ─────────────────────────────────────
    resolution = resolve_root(
        refined_host,
        pre_root_directive = pre_root_directive,
        morphology_path    = morphology_path,
        evidence_ids       = tuple(evidence_ids),
        trace_ids          = tuple(trace_ids),
    )

    # ── 2: RootProjection (إسقاط P2 من المحرك المحلي) ────────────────────────
    projection = RootProjection.from_root_resolution(
        resolution,
        input_surface = original_host,
    )

    # ── 3: RootCandidate (P3 — رتابة صارمة) ───────────────────────────────────
    return RootCandidate.from_projection(projection)
