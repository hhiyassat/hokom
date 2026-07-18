#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_candidate/root_resolution.py — Hokom Local Root Resolution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

المحرك المحلي لتحليل الجذر — Hokom مصدر الحقيقة.

هيكل القرار:
  pre_root_directive='BLOCK' → RootResolution(BLOCK) مباشرة (لا تحليل)
  pre_root_directive='OPEN'  → analyze_host_consonants() → ACCEPT|DEFER
  pre_root_directive='DEFER' → analyze_host_consonants() → إعادة DEFER محتمل

الرتابة:
  BLOCK  → لا جذر أبدًا (لا يُرقَّى داخليًا).
  DEFER  → لا جذر (يُرقَّى فقط من الخارج عبر آلية الترخيص).
  ACCEPT → جذر محلول (لا يُخفَّض داخليًا).

القيود:
  - source_engine='HOKOM_ROOT_ENGINE' دائمًا.
  - لا استيراد من hr2s الداخلي.
  - لا مسارات مطلقة.
  - لا استثناءات نصية خاصة بكلمات.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any, Optional

from pipeline.p3_candidate.root_rules import analyze_host_consonants


# ══════════════════════════════════════════════════════════════════════════════
# 1.  RootResolution — DTO المجمَّد
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RootResolution:
    """نتيجة محرك Hokom المحلي لتحليل الجذر.

    directive        : 'ACCEPT' | 'DEFER' | 'BLOCK'
    analyzed_host    : المضيف المُنقَّح الذي حُلِّل فعليًا (= refined_host).
    canonical_root   : الجذر الثلاثي الكنوني أو None.
    radical_alignment: ((موضع، هوية), ...) — ترتيب FA/AYN/LAM.
    root_profile     : بيانات وصفية للجذر (نوع، عدد حروف، مصدر المحرك).
    transformations  : التحولات المرخَّصة المطبَّقة (فارغة في هذه الدفعة).
    evidence_ids     : مرجعيات الشواهد (tuple).
    trace_ids        : مسارات التحليل (tuple).
    residual_codes   : رموز التحفظ — سبب DEFER/BLOCK أو فارغة عند ACCEPT.
    source_engine    : ثابت 'HOKOM_ROOT_ENGINE'.
    """
    directive:         str
    analyzed_host:     str
    canonical_root:    Optional[tuple]
    radical_alignment: tuple
    root_profile:      Mapping[str, Any]
    transformations:   tuple
    evidence_ids:      tuple
    trace_ids:         tuple
    residual_codes:    tuple
    source_engine:     str = 'HOKOM_ROOT_ENGINE'

    def to_dict(self) -> dict:
        """تسلسل JSON-compatible."""
        return {
            'directive':         self.directive,
            'analyzed_host':     self.analyzed_host,
            'canonical_root':    (list(self.canonical_root)
                                  if self.canonical_root is not None else None),
            'radical_alignment': [list(a) for a in self.radical_alignment],
            'root_profile':      dict(self.root_profile),
            'transformations':   list(self.transformations),
            'evidence_ids':      list(self.evidence_ids),
            'trace_ids':         list(self.trace_ids),
            'residual_codes':    list(self.residual_codes),
            'source_engine':     self.source_engine,
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2.  resolve_root — نقطة الدخول الوحيدة
# ══════════════════════════════════════════════════════════════════════════════

def resolve_root(
    refined_host: str,
    *,
    pre_root_directive: str,
    morphology_path: str = '',
    evidence_ids: tuple = (),
    trace_ids: tuple = (),
) -> RootResolution:
    """حلِّل الجذر من مضيف منقَّح.

    Parameters
    ----------
    refined_host       : المضيف بعد فصل اللواحق الطرفية (مثل تَرَكَ من تَرَكَتْ).
    pre_root_directive : 'OPEN' | 'DEFER' | 'BLOCK'
      BLOCK → تمرير مباشر بلا تحليل.
      OPEN/DEFER → استدعاء analyze_host_consonants().
    morphology_path    : سياق المسار الصرفي (اختياري).
    evidence_ids       : مرجعيات الشواهد.
    trace_ids          : مسارات التحليل.

    Returns
    -------
    RootResolution — المحرك المحلي مصدر الحقيقة دائمًا.
    """
    directive = str(pre_root_directive).strip().upper()

    # ── BLOCK: تمرير مباشر بلا تحليل ─────────────────────────────────────────
    if directive == 'BLOCK':
        return RootResolution(
            directive         = 'BLOCK',
            analyzed_host     = refined_host,
            canonical_root    = None,
            radical_alignment = (),
            root_profile      = {},
            transformations   = (),
            evidence_ids      = tuple(evidence_ids),
            trace_ids         = tuple(trace_ids),
            residual_codes    = ('block:root:pre_root_directive_block',),
        )

    # ── OPEN / DEFER: تحليل محلي ─────────────────────────────────────────────
    analysis_directive, canonical_root, residual_code, root_profile = (
        analyze_host_consonants(refined_host)
    )

    # رتابة DEFER من pre_root: إذا كان DEFER مسبقًا، يبقى DEFER حتى لو ACCEPT محليًا
    if directive == 'DEFER' and analysis_directive == 'ACCEPT':
        analysis_directive = 'DEFER'
        canonical_root = None
        residual_code = 'defer:root:pre_root_directive_defer'
        root_profile = {}

    # بناء توافق المواضع للجذور المقبولة
    radical_alignment: tuple
    if analysis_directive == 'ACCEPT' and canonical_root is not None:
        positions = ('FA', 'AYN', 'LAM')
        radical_alignment = tuple(
            (pos, ch) for pos, ch in zip(positions, canonical_root)
        )
    else:
        radical_alignment = ()

    residual_codes: tuple
    if residual_code:
        residual_codes = (residual_code,)
    else:
        residual_codes = ()

    return RootResolution(
        directive         = analysis_directive,
        analyzed_host     = refined_host,
        canonical_root    = canonical_root,
        radical_alignment = radical_alignment,
        root_profile      = root_profile,
        transformations   = (),
        evidence_ids      = tuple(evidence_ids),
        trace_ids         = tuple(trace_ids),
        residual_codes    = residual_codes,
    )
