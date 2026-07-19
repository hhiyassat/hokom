#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_augmented/models.py — AugmentedRootAnalysis dataclass
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

نموذج بيانات نتيجة تحليل فعل مزيد.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ── عائلات الأوزان المدعومة ─────────────────────────────────────────────────
# FORM_II–FORM_X: أفعال مزيدة
# FA3IL_PARTICIPLE: اسم الفاعل من الثلاثي المجرد (فَاعِل) — يُعالَج هنا لأن
#   الهيكل العظمي C1-ا-C2-C3 يتداخل مع FORM_III في _match_skeleton.
FORM_FAMILIES = frozenset({
    'FORM_II', 'FORM_III', 'FORM_IV', 'FORM_V', 'FORM_VI',
    'FORM_VII', 'FORM_VIII', 'FORM_IX', 'FORM_X',
    'FA3IL_PARTICIPLE',   # فَاعِل — اسم فاعل ثلاثي مجرد (Form I derivative)
})

# ── مستويات الثقة ────────────────────────────────────────────────────────────
CONFIDENCE_LEVELS = frozenset({'HIGH', 'MEDIUM', 'LOW'})

# حروف العلة (يمكن أن تكون جذرًا ثلاثيًا مع ثقة متوسطة)
_WEAK_RADICALS = frozenset('وي')


@dataclass(frozen=True)
class AugmentedRootAnalysis:
    """
    نتيجة تحليل فعل مزيد (أفعال المزيد Form II–X).

    form_family       : 'FORM_II' | 'FORM_III' | ... | 'FORM_X'
    trilateral_root   : (C1, C2, C3) — حروف الجذر الثلاثي بلا حركات
    past_surface      : صيغة الماضي المشتقة (تقديرية)
    imperfect_prefix  : بادئة المضارع المُزالة (يُ/تَ/...) أو None
    confidence        : 'HIGH' | 'MEDIUM' | 'LOW'
    evidence_ids      : مرجعيات الشواهد
    trace_ids         : مسار التحليل
    residual_codes    : رموز التحفظ (عند MEDIUM/LOW)
    """
    form_family:      str
    trilateral_root:  tuple   # (str, str, str)
    past_surface:     str
    imperfect_prefix: Optional[str]
    confidence:       str
    evidence_ids:     tuple
    trace_ids:        tuple
    residual_codes:   tuple

    def __post_init__(self) -> None:
        if self.form_family not in FORM_FAMILIES:
            raise ValueError(f'unknown form_family: {self.form_family!r}')
        if self.confidence not in CONFIDENCE_LEVELS:
            raise ValueError(f'unknown confidence: {self.confidence!r}')
        if len(self.trilateral_root) != 3:
            raise ValueError(
                f'trilateral_root must have exactly 3 elements: {self.trilateral_root!r}'
            )

    def to_dict(self) -> dict:
        return {
            'form_family':      self.form_family,
            'trilateral_root':  list(self.trilateral_root),
            'past_surface':     self.past_surface,
            'imperfect_prefix': self.imperfect_prefix,
            'confidence':       self.confidence,
            'evidence_ids':     list(self.evidence_ids),
            'trace_ids':        list(self.trace_ids),
            'residual_codes':   list(self.residual_codes),
        }

    @property
    def has_weak_radical(self) -> bool:
        """True إذا احتوى الجذر على حرف علة (واو أو ياء)."""
        return any(c in _WEAK_RADICALS for c in self.trilateral_root)
