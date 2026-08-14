#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/pre_root/host_routing.py — توجيه المضيف وإغلاق المشغلات المركبة (Axis 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُقرّر مسار المضيف وفق أولوية صارمة:

  EMPTY > CLOSED_OPERATOR_HOST > MABNI_HOST > MORPHOLOGY_PATH

التفصيل:
  EMPTY               → السطح فارغ بعد الفصل (لا مضيف)
  CLOSED_OPERATOR_HOST → المضيف (بعد فصل الضمائر) في جرد المشغّلات
                          مثال: أَنَّهُمْ → host=أَنَّ (INNA_SERIES) → BLOCKED
  MABNI_HOST          → المضيف في جرد المبنيات (ضمائر، مبهمات، ...)
                          → BLOCKED (لا جذر للمبني)
  MORPHOLOGY_PATH     → مضيف عادي → يُرسَل لتقييم الحدود ثم HR2S

قانون إغلاق المشغّل المركب:
  إذا كان المضيف (بعد تجريد الضمائر المتصلة) مشغّلًا معروفًا:
    root_path_directive = 'BLOCK'
    next_stage          = 'OPERATOR'
  لا يُستدعى HR2S.
  لا استثناءات نصية — الكشف يعتمد على جرد المشغّلات الحالي.

الاستيراد الكسول:
  يستورد recognize_token من mabniyat_attachment بشكل كسول لتجنب
  التبعيات الدائرية. يُعامَل الخطأ باحتياط: إذا تعذّر الاستيراد
  → MORPHOLOGY_PATH (لا يُوقَف التنفيذ).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1.  HostRoute — تصنوف مسارات التوجيه
# ══════════════════════════════════════════════════════════════════════════════

class HostRoute:
    """ثوابت مسارات التوجيه (str بدلًا من Enum للتوافق النصي)."""
    EMPTY                = 'EMPTY'
    CLOSED_OPERATOR_HOST = 'CLOSED_OPERATOR_HOST'
    MABNI_HOST           = 'MABNI_HOST'
    MORPHOLOGY_PATH      = 'MORPHOLOGY_PATH'


# ══════════════════════════════════════════════════════════════════════════════
# 2.  HostRoutingDecision — نتيجة التوجيه
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class HostRoutingDecision:
    """
    قرار توجيه المضيف بعد تطبيق الأولوية.

    Attributes
    ----------
    route              : أحد HostRoute.* — المسار المُختار
    root_path_directive: 'OPEN' | 'DEFER' | 'BLOCK'
    next_stage         : 'HR2S' | 'OPERATOR' | 'MABNI' | 'BLOCKED' | 'EMPTY'
    operator_id        : معرّف المشغّل إن كُشف (None غير ذلك)
    mabni_id           : معرّف المبني إن كُشف (None غير ذلك)
    evidence_id        : شاهد القرار
    notes              : ملاحظات
    """
    route:               str
    root_path_directive: str
    next_stage:          str
    operator_id:         Optional[str] = None
    mabni_id:            Optional[str] = None
    evidence_id:         str           = ''
    notes:               str           = ''

    def to_dict(self) -> dict:
        return {
            'route':               self.route,
            'root_path_directive': self.root_path_directive,
            'next_stage':          self.next_stage,
            'operator_id':         self.operator_id,
            'mabni_id':            self.mabni_id,
            'evidence_id':         self.evidence_id,
            'notes':               self.notes,
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  route_host — الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def route_host(
    host_surface: str,
    *,
    phonological_slot_verdict: str = 'ACCEPT',
) -> HostRoutingDecision:
    """
    قرّر مسار المضيف وفق الأولوية: EMPTY > OPERATOR > MABNI > MORPHOLOGY_PATH.

    يستخدم recognize_token() من mabniyat_attachment لكشف المشغّلات والمبنيات
    المركبة. يمرّر phonological_slot_verdict إلى recognize_token.

    Parameters
    ----------
    host_surface : السطح المُضيف (بعد فصل الـ)
    phonological_slot_verdict   : حكم P4 — 'ACCEPT' | 'DEFER' | 'BLOCK'
                   يُمرَّر إلى recognize_token للتوافق مع قانون P4

    Returns
    -------
    HostRoutingDecision
    """
    # ── EMPTY: لا مضيف بعد الفصل ─────────────────────────────────────────────
    if not host_surface or not host_surface.strip():
        return HostRoutingDecision(
            route               = HostRoute.EMPTY,
            root_path_directive = 'BLOCK',
            next_stage          = 'EMPTY',
            evidence_id         = 'routing:empty_host',
            notes               = 'لا مضيف بعد فصل السوابق',
        )

    # ── فحص المشغّل/المبني عبر recognize_token ───────────────────────────────
    token_analysis = _try_recognize(host_surface, phonological_slot_verdict)

    if token_analysis is not None:
        hr = token_analysis.host_route

        # مشغّل مركب: أَنَّهُمْ → أَنَّ + هُمْ → OPERATOR_BOUNDARY
        if hr == 'OPERATOR_BOUNDARY':
            op_id = _extract_operator_id(token_analysis)
            return HostRoutingDecision(
                route               = HostRoute.CLOSED_OPERATOR_HOST,
                root_path_directive = 'BLOCK',
                next_stage          = 'OPERATOR',
                operator_id         = op_id,
                evidence_id         = 'routing:operator_boundary_from_recognize_token',
                notes               = f'مضيف مشغّل: {token_analysis.host_surface!r}',
            )

        # مضيف مبني كامل (ضمير، مبهم، ...)
        if hr in ('MABNI_BOUNDARY', 'MABNI_DEFERRED', 'MABNI_BLOCKED'):
            mabni_id = _extract_mabni_id(token_analysis)
            return HostRoutingDecision(
                route               = HostRoute.MABNI_HOST,
                root_path_directive = 'BLOCK',
                next_stage          = 'MABNI',
                mabni_id            = mabni_id,
                evidence_id         = 'routing:mabni_host_from_recognize_token',
                notes               = f'مضيف مبني: {hr}',
            )

        # المضيف فارغ بعد التجريد
        if hr == 'EMPTY':
            return HostRoutingDecision(
                route               = HostRoute.EMPTY,
                root_path_directive = 'BLOCK',
                next_stage          = 'EMPTY',
                evidence_id         = 'routing:empty_after_segmentation',
                notes               = 'المضيف فارغ بعد تجريد الملحقات',
            )

    # ── المسار الصرفي العادي (OPEN_TO_ROOT_ENGINE أو تعذّر recognize_token) ────
    return HostRoutingDecision(
        route               = HostRoute.MORPHOLOGY_PATH,
        root_path_directive = 'OPEN',
        next_stage          = 'HOKOM_ROOT_ENGINE',
        evidence_id         = 'routing:morphology_path_open',
        notes               = 'مضيف مرشح للتحليل الصرفي',
    )


# ══════════════════════════════════════════════════════════════════════════════
# 4.  دوال مساعدة
# ══════════════════════════════════════════════════════════════════════════════

def _try_recognize(surface: str, phonological_slot_verdict: str):
    """
    استدعِ recognize_token بشكل كسول. أعد None عند أي خطأ.
    """
    try:
        from mabniyat_attachment import recognize_token
        return recognize_token(surface, phonological_slot_verdict)
    except Exception:
        return None


def _extract_operator_id(token_analysis) -> Optional[str]:
    """استخرج معرّف المشغّل من TokenAnalysis."""
    try:
        # G5: host_operator_id
        op_id = getattr(token_analysis, 'host_operator_id', None)
        if op_id:
            return op_id
        # أو من prefix_operators إن وُجدت
        prefix_ops = getattr(token_analysis, 'prefix_operators', [])
        if prefix_ops:
            return getattr(prefix_ops[0], 'mabni_id', None)
    except Exception:
        pass
    return None


def _extract_mabni_id(token_analysis) -> Optional[str]:
    """استخرج معرّف المبني من TokenAnalysis."""
    try:
        return getattr(token_analysis, 'host_mabni_id', None)
    except Exception:
        return None
