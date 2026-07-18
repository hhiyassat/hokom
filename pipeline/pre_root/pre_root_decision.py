#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/pre_root/pre_root_decision.py — قرار ما قبل الجذر (نقطة الدخول)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يجمع الأعمدة الخمسة في قرار موحَّد:

  1. article_projection    → فصل أداة التعريف
  2. boundary.service      → تقييم البنية الصوتية للمضيف
  3. morphology_path       → تصنيف المسار الصرفي
  4. structural_aggregation → دمج الأحكام (BLOCK > DEFER > ACCEPT)
  5. host_routing          → الأولوية النهائية (OPERATOR > MABNI > MORPHOLOGY)

المخرج: PreRootDecision — نموذج بيانات مُجمَّد يُمرَّر إلى الطبقات اللاحقة.

علاقته بـ boundary/service.py:
  assess_pre_root() يستدعي assess_boundary() داخليًا على المضيف (لا على
  السطح الأصلي). بقية boundary/ لا تتأثر — لا تغيير على الكود الحالي.

علاقته بـ HR2S:
  root_path_directive = 'OPEN'   → الطبقة اللاحقة تستدعي HR2SRootAdapter
  root_path_directive = 'DEFER'  → HR2S لا يُستدعى
  root_path_directive = 'BLOCK'  → HR2S لا يُستدعى
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pipeline.p2_projection.attachment_projection import AttachmentProjection, AttachmentRole
from pipeline.pre_root.morphology_path    import MorphologyPath
from pipeline.pre_root.article_projection import (
    ArticleProjectionResult, project_article,
)
from pipeline.pre_root.structural_aggregation import (
    aggregate_structural_verdict,
    verdicts_from_directive,
    residuals_for_verdict,
)
from pipeline.pre_root.host_routing import (
    HostRoutingDecision, route_host, HostRoute,
)


# ══════════════════════════════════════════════════════════════════════════════
# 1.  PreRootDecision — النموذج المُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PreRootDecision:
    """
    القرار الكامل لطبقة ما قبل الجذر.

    Attributes
    ----------
    input_surface       : السطح الأصلي كما ورد من المُعالِج
    normalized_surface  : السطح بعد تطبيع الهمزة
    prefixes            : السوابق المُستخرَجة (الـ، حروف الجر، ...)
    host_surface        : المضيف بعد فصل السوابق (ما يُرسَل للتحليل)
    suffixes            : اللواحق المُتعرَّف عليها (فارغة حتى R-9)
    structural_verdict  : 'ACCEPT' | 'DEFER' | 'BLOCK' — الحكم المُجمَّع
    lexical_boundary    : BoundaryKind.value للمضيف
    morphology_path     : MorphologyPath — المسار الصرفي المُقدَّر
    root_path_directive : 'OPEN' | 'DEFER' | 'BLOCK' — التوجيه النهائي
    next_stage          : 'HR2S' | 'OPERATOR' | 'MABNI' | 'BLOCKED' | 'EMPTY'
    routing             : HostRoutingDecision — تفاصيل قرار التوجيه
    evidence_ids        : شواهد القرار
    residual_codes      : رموز التحفظ (إن وُجد DEFER أو BLOCK)
    trace_ids           : مسار التنفيذ الداخلي
    """
    input_surface:       str
    normalized_surface:  str
    prefixes:            tuple[AttachmentProjection, ...]
    host_surface:        str
    suffixes:            tuple[AttachmentProjection, ...]
    structural_verdict:  str
    lexical_boundary:    str
    morphology_path:     MorphologyPath
    root_path_directive: str
    next_stage:          str
    routing:             HostRoutingDecision
    evidence_ids:        tuple[str, ...]
    residual_codes:      tuple[str, ...]
    trace_ids:           tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            'input_surface':       self.input_surface,
            'normalized_surface':  self.normalized_surface,
            'prefixes':            [p.to_dict() for p in self.prefixes],
            'host_surface':        self.host_surface,
            'suffixes':            [s.to_dict() for s in self.suffixes],
            'structural_verdict':  self.structural_verdict,
            'lexical_boundary':    self.lexical_boundary,
            'morphology_path':     self.morphology_path.value,
            'root_path_directive': self.root_path_directive,
            'next_stage':          self.next_stage,
            'routing':             self.routing.to_dict(),
            'evidence_ids':        list(self.evidence_ids),
            'residual_codes':      list(self.residual_codes),
            'trace_ids':           list(self.trace_ids),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2.  assess_pre_root — نقطة الدخول
# ══════════════════════════════════════════════════════════════════════════════

def assess_pre_root(
    surface: str,
    *,
    p4_verdict: str = 'ACCEPT',
) -> PreRootDecision:
    """
    أنتِج قرار ما قبل الجذر لسطح عربي واحد.

    الخطوات:
      1. تطبيع الهمزة
      2. فصل أداة التعريف
      3. تقييم حدود المضيف (boundary/service.assess_boundary)
      4. تصنيف المسار الصرفي
      5. دمج الأحكام البنيوية
      6. توجيه المضيف بالأولوية

    Parameters
    ----------
    surface    : السطح الأصلي للكلمة
    p4_verdict : حكم P4 من طبقة الخانات — يُمرَّر إلى recognize_token
                 عند كشف المشغّلات المركبة (الافتراضي 'ACCEPT')

    Returns
    -------
    PreRootDecision
    """
    evidence_ids: list[str] = []
    trace_ids:    list[str] = []

    # ── 1. تطبيع الهمزة ──────────────────────────────────────────────────────
    try:
        from normalizer import normalize_hamza
        normalized = normalize_hamza(surface)
    except Exception:
        normalized = surface
    trace_ids.append('step:hamza_normalization')

    # ── 2. فصل أداة التعريف ──────────────────────────────────────────────────
    article: ArticleProjectionResult = project_article(surface)
    host    = article.host_surface
    evidence_ids.append(article.evidence_id)

    prefixes: tuple[AttachmentProjection, ...] = ()
    if article.prefix_projection is not None:
        prefixes = (article.prefix_projection,)
    trace_ids.append('step:article_projection')

    # ── 3. تقييم حدود المضيف ─────────────────────────────────────────────────
    boundary = _assess_host_boundary(host)
    boundary_kind_value = boundary.kind.value
    evidence_ids.extend(e.source for e in boundary.evidence)
    trace_ids.append('step:boundary_assessment')

    # ── 4. تصنيف المسار الصرفي ───────────────────────────────────────────────
    from pipeline.pre_root.morphology_path import classify_morphology_path
    morph_path = classify_morphology_path(host, boundary.kind)
    trace_ids.append('step:morphology_path_classification')

    # ── 5. دمج الأحكام البنيوية ───────────────────────────────────────────────
    verdicts_list = verdicts_from_directive(boundary.directive.value)
    # دمج حكم P4: إذا كان DEFER أو BLOCK يُضاف إلى التجميع البنيوي
    # هذا يضمن أن DEFER من P4 يُنتج structural_verdict=DEFER حتى لو قالت
    # الحدود ACCEPT (مثال: مضيف متبقٍّ لكلمة أعطى P4 حكم DEFER)
    if p4_verdict in ('DEFER', 'BLOCK'):
        verdicts_list.append(p4_verdict)
    structural_verdict = aggregate_structural_verdict(verdicts_list)
    trace_ids.append('step:structural_aggregation')

    # ── 6. توجيه المضيف بالأولوية ────────────────────────────────────────────
    # نُنفّذ route_host دائمًا لكشف المسار الصحيح (OPERATOR / MABNI / MORPHOLOGY).
    # ثم نُعدِّل root_path_directive وnext_stage وفق structural_verdict:
    #   BLOCK → next_stage='BLOCKED'  (عائق مُثبَت)
    #   DEFER → next_stage='DEFERRED' (مسار معلَّق لم يُرخَّص بعد)
    routing_candidate = route_host(host, p4_verdict=p4_verdict)

    if structural_verdict == 'BLOCK':
        routing = HostRoutingDecision(
            route               = routing_candidate.route,
            root_path_directive = 'BLOCK',
            next_stage          = 'BLOCKED',
            operator_id         = routing_candidate.operator_id,
            mabni_id            = routing_candidate.mabni_id,
            evidence_id         = routing_candidate.evidence_id or 'routing:structural_block',
            notes               = f'BLOCK من البنية: {boundary_kind_value}',
        )
    elif structural_verdict == 'DEFER':
        routing = HostRoutingDecision(
            route               = routing_candidate.route,
            root_path_directive = 'DEFER',
            next_stage          = 'DEFERRED',
            operator_id         = routing_candidate.operator_id,
            mabni_id            = routing_candidate.mabni_id,
            evidence_id         = routing_candidate.evidence_id or 'routing:structural_defer',
            notes               = f'DEFER من البنية: {boundary_kind_value}',
        )
    else:
        # ACCEPT — routing_candidate كامل بأولويته
        routing = routing_candidate

    evidence_ids.append(routing.evidence_id)
    trace_ids.append('step:host_routing')

    # ── القرار النهائي ────────────────────────────────────────────────────────
    root_path_directive = routing.root_path_directive
    next_stage          = routing.next_stage

    # ── تحديثات خاصة بمسار المشغّل المركب ───────────────────────────────────
    # عند route=CLOSED_OPERATOR_HOST:
    #   - host_surface يُصبح operator_host (الجزء الحاكم: أَنَّ)
    #   - الضمير المتصل (هُمْ) يُدرَج في suffixes بدور OPERATOR_COMPLEMENT_SUFFIX
    #   - morphology_path يُعاد تعيينه إلى FUNCTIONAL_PATH (المشغّل ليس جذرًا)
    final_host    = host
    final_suffixes: tuple = ()
    final_morph   = morph_path

    if routing.route == HostRoute.CLOSED_OPERATOR_HOST:
        final_morph = MorphologyPath.FUNCTIONAL_PATH
        # استخرج operator_host وsuffix من token_analysis إن أمكن
        _op_host, _op_suffix = _extract_operator_segments(host, routing)
        if _op_host:
            final_host = _op_host
        if _op_suffix:
            final_suffixes = (AttachmentProjection(
                surface    = _op_suffix,
                role       = AttachmentRole.OPERATOR_COMPLEMENT_SUFFIX,
                span_start = len(_op_host) if _op_host else len(host),
                span_end   = len(_op_host or host) + len(_op_suffix),
                notes      = 'operator:compound:suffix_segmented',
            ),)
        trace_ids.append('step:operator_host_segmentation')

    # رموز التحفظ: من التجميع البنيوي + من التوجيه
    residuals = list(residuals_for_verdict(structural_verdict))
    if structural_verdict == 'ACCEPT' and root_path_directive != 'OPEN':
        # التوجيه أغلق المسار (مشغّل أو مبني)
        residuals.append(f'block:pre_root:host_routed_to_{routing.route.lower()}')

    return PreRootDecision(
        input_surface       = surface,
        normalized_surface  = normalized,
        prefixes            = prefixes,
        host_surface        = final_host,
        suffixes            = final_suffixes,
        structural_verdict  = structural_verdict,
        lexical_boundary    = boundary_kind_value,
        morphology_path     = final_morph,
        root_path_directive = root_path_directive,
        next_stage          = next_stage,
        routing             = routing,
        evidence_ids        = tuple(evidence_ids),
        residual_codes      = tuple(residuals),
        trace_ids           = tuple(trace_ids),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 3.  دوال مساعدة
# ══════════════════════════════════════════════════════════════════════════════

def _extract_operator_segments(
    host: str,
    routing: 'HostRoutingDecision',
) -> 'tuple[str | None, str | None]':
    """
    استخرج (operator_host, suffix) من مضيف مشغّل مركب.

    المصدر: routing.notes يحتوي على 'host_surface' من recognize_token.
    الاحتياط: إذا تعذّر الاستخراج → (None, None) — يُبقي host كما هو.

    Returns
    -------
    (operator_host, complement_suffix)
    """
    try:
        from mabniyat_attachment import recognize_token
        ta = recognize_token(host, 'ACCEPT')
        if ta is None:
            return None, None
        op_host   = getattr(ta, 'host_surface', None) or getattr(ta, 'operator_host', None)
        op_suffix = getattr(ta, 'suffix_surface', None) or getattr(ta, 'attached_suffix', None)
        # التحقق: op_host يجب أن يكون جزءًا من host
        if op_host and host.startswith(op_host) and len(op_host) < len(host):
            suffix = host[len(op_host):]
            return op_host, suffix
        return op_host, op_suffix
    except Exception:
        return None, None


def _assess_host_boundary(host: str):
    """استدعِ assess_boundary على المضيف. أعِد قرارًا بسيطًا عند الفشل."""
    try:
        from boundary.service import assess_boundary
        return assess_boundary(host)
    except Exception:
        # احتياط: إذا فشل استيراد boundary → قرار DEFER
        from boundary.models import (
            RootEligibilityDecision, BoundaryKind,
            RootPathDirective, StageState, BoundaryEvidence,
        )
        return RootEligibilityDecision(
            surface     = host,
            normalized  = host,
            kind        = BoundaryKind.AMBIGUOUS,
            directive   = RootPathDirective.DEFER,
            stage_state = StageState.DEFERRED,
            evidence    = [BoundaryEvidence(
                source = 'pre_root:boundary_unavailable',
                note   = 'تعذّر استيراد boundary.service',
            )],
        )
