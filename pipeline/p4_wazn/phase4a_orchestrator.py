#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/phase4a_orchestrator.py — Phase 4A Orchestrator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يجمع:
  - WaznHypothesis      (P4A-α): كشف الزيادة الداخلية
  - IlaalResolution     (P4A-β): ترخيص الجذر الضعيف (إعلال)
  - Root Re-Licensing   (P3.11): التحقق النهائي من الجذر
  - project_wazn()             : إسقاط الوزن

المسارات:

  BLOCK
  → final_directive='BLOCK' / wazn_projection=None / NOT_OPENED

  ACCEPT
  → project_wazn(root_candidate)
  → final_directive = WaznProjection.directive
  → final_wazn = selected_wazn.wazn_id إن ACCEPT

  DEFER
  → إن لا فرضية وزنية:
      final_directive='DEFER' / wazn_projection=None
  → إن وُجدت فرضية:
      [P4A-β] apply_ilaal_resolution() إن proposed_root_after=None
      relicense_root_from_wazn_hypothesis()
      إن relicensing ACCEPT:
        promoted RootCandidate
        project_wazn(promoted)
        final_directive = WaznProjection.directive
      إن relicensing DEFER/BLOCK:
        final_directive='DEFER' / wazn_projection=None

القانون الأساسي:
  final_directive يأتي دائمًا من WaznProjection.directive.value
  أو من حكم المسار المغلق ('BLOCK'/'DEFER') مباشرة.
  source_path يصف المسار — لا يحدد الحكم.
  Root ACCEPT لا يضمن final_directive='ACCEPT' (يعتمد على الوزن).
  Relicensing ACCEPT لا يضمن final_directive='ACCEPT' (يعتمد على الوزن).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from pipeline.p3_candidate.root_candidate import RootCandidate
from pipeline.p3_candidate.root_relicensing import relicense_root_from_wazn_hypothesis
from pipeline.p4_wazn.hypothesis import WaznHypothesis, build_wazn_hypothesis
from pipeline.p4_wazn.ilaal import apply_ilaal_resolution
from pipeline.p4_wazn.wazn_projection import project_wazn


# ══════════════════════════════════════════════════════════════════════════════
# 1.  نموذج البيانات
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Phase4AResult:
    """المخرج الكامل من Phase 4A — يجمع الفرضية والإعلال والترخيص والإسقاط.

    الحقول الجوهرية:
      initial_root_directive  : directive RootCandidate المُدخَّل ('ACCEPT'|'DEFER'|'BLOCK')
      final_directive         : الحكم النهائي — يأتي من WaznProjection أو مسار مغلق
      source_path             : وصف المسار المُتبَّع ('direct_accept'|'hypothesis_relicensed'|
                                                     'deferred'|'blocked')

    القوانين:
      • final_directive مستقل عن source_path.
      • final_directive='ACCEPT' يستوجب wazn_projection.selected_wazn≠None.
      • final_directive='DEFER'|'BLOCK' يستوجب final_wazn=None.
      • promoted_root_candidate يُعيَّن فقط عند relicensing ACCEPT.
      • wazn_projection=None عند BLOCK أو DEFER بلا مسار وزني.
    """
    # ── الحكم ────────────────────────────────────────────────────────────────
    initial_root_directive: str        # 'ACCEPT' | 'DEFER' | 'BLOCK'
    final_directive:        str        # 'ACCEPT' | 'DEFER' | 'BLOCK'
    source_path:            str        # وصف المسار

    # ── المرشحون ─────────────────────────────────────────────────────────────
    root_candidate:           Any      # RootCandidate الأصلي (لا يتغير)
    promoted_root_candidate:  Optional[Any]   # RootCandidate مُرقَّى | None

    # ── مراحل الفرضية ────────────────────────────────────────────────────────
    wazn_hypothesis:    Optional[Any]  # WaznHypothesis | None
    ilaal_resolution:   Optional[Any]  # IlaalHypothesis | None
    relicensing_result: Optional[Any]  # RootRelicensingResult | None
    wazn_projection:    Optional[Any]  # WaznProjection | None

    # ── النتيجة النهائية ─────────────────────────────────────────────────────
    final_wazn: Optional[str]          # wazn_id عند ACCEPT, وإلا None

    # ── التتبع ───────────────────────────────────────────────────────────────
    evidence_ids:   tuple
    trace_ids:      tuple
    residual_codes: tuple

    # ── تسلسل JSON ───────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            'initial_root_directive': self.initial_root_directive,
            'final_directive':        self.final_directive,
            'source_path':            self.source_path,
            'final_wazn':             self.final_wazn,
            'root_candidate':         (self.root_candidate.to_dict()
                                       if hasattr(self.root_candidate, 'to_dict') else None),
            'promoted_root_candidate': (self.promoted_root_candidate.to_dict()
                                        if self.promoted_root_candidate is not None
                                        and hasattr(self.promoted_root_candidate, 'to_dict')
                                        else None),
            'wazn_projection':        (self.wazn_projection.to_dict()
                                       if self.wazn_projection is not None
                                       and hasattr(self.wazn_projection, 'to_dict')
                                       else None),
            'evidence_ids':           list(self.evidence_ids),
            'trace_ids':              list(self.trace_ids),
            'residual_codes':         list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 2.  مساعدات داخلية
# ══════════════════════════════════════════════════════════════════════════════

def _directive_str(wazn_proj) -> str:
    """استخرج directive كسلسلة نصية من WaznProjection."""
    d = wazn_proj.directive
    return d.value if hasattr(d, 'value') else str(d)


def _final_wazn(wazn_proj) -> Optional[str]:
    """اشتق wazn_id النهائي — None إلا إذا كان final_directive='ACCEPT'."""
    if _directive_str(wazn_proj) != 'ACCEPT':
        return None
    sw = getattr(wazn_proj, 'selected_wazn', None)
    return getattr(sw, 'wazn_id', None) if sw is not None else None


def _dedup(residuals: tuple) -> tuple:
    """Order-preserving deduplication of residuals (Fix 9)."""
    return tuple(dict.fromkeys(residuals))


def _aggregate(root_candidate, wazn_proj=None, relicensing=None, promoted=None):
    """اجمع evidence/trace/residual من طبقات المسار."""
    ev  = tuple(getattr(root_candidate, 'evidence_ids',   ()) or ())
    tr  = tuple(getattr(root_candidate, 'trace_ids',      ()) or ())
    res = tuple(getattr(root_candidate, 'residual_codes', ()) or ())

    # Track whether promoted root is trilateral for stale-residual filtering.
    _stale: frozenset = frozenset()

    if promoted is not None:
        ev  += tuple(getattr(promoted, 'evidence_ids',   ()) or ())
        tr  += tuple(getattr(promoted, 'trace_ids',      ()) or ())
        # Fix 8/10: When promoted root has exactly 3 radicals (trilateral),
        # filter out the pre-relicensing residuals from root_candidate, promoted,
        # AND wazn_proj — they are resolved by the relicensing acceptance.
        # The wazn_proj runs on the promoted root but the host surface may still
        # have extra consonants; defer:root:quadriliteral_beyond_scope emitted
        # by wazn_proj in that case is equally stale.
        promoted_root = getattr(promoted, 'canonical_root', None)
        promoted_res  = tuple(getattr(promoted, 'residual_codes', ()) or ())
        if promoted_root and len(promoted_root) == 3:
            # Fix 10: filter ONLY quadriliteral_beyond_scope — when relicensing
            # identifies a valid trilateral root, the "4-consonant" classification
            # is stale.  non_standard_consonant_count is kept: the surface IS still
            # augmented (beyond trilateral scope), and Fix 11 uses it as a signal.
            _stale = frozenset({
                'defer:root:quadriliteral_beyond_scope',
            })
            res          = tuple(r for r in res         if r not in _stale)
            promoted_res = tuple(r for r in promoted_res if r not in _stale)
        res += promoted_res

    if wazn_proj is not None:
        ev  += tuple(getattr(wazn_proj, 'evidence_ids',   ()) or ())
        tr  += tuple(getattr(wazn_proj, 'trace_ids',      ()) or ())
        wazn_res = tuple(getattr(wazn_proj, 'residual_codes', ()) or ())
        # Apply the same stale filter to wazn_proj residuals (Fix 8/10 extension).
        if _stale:
            wazn_res = tuple(r for r in wazn_res if r not in _stale)
        res += wazn_res

    if relicensing is not None:
        ev  += tuple(getattr(relicensing, 'evidence_ids',   ()) or ())
        tr  += tuple(getattr(relicensing, 'trace_ids',      ()) or ())
        res += tuple(getattr(relicensing, 'residual_codes', ()) or ())

    # Fix 9: Deduplicate residuals (order-preserving).
    res = _dedup(res)

    # Fix 11: Add companion code for augmented (mazid) forms that are beyond
    # trilateral scope.  When non_standard_consonant_count is still present
    # (i.e., NOT resolved by relicensing), annotate with a more specific code.
    if 'defer:root:non_standard_consonant_count' in res:
        res = _dedup(res + ('defer:root:augmented_form_beyond_scope',))

    return ev, tr, res


# ══════════════════════════════════════════════════════════════════════════════
# 3.  المدخل الرئيس
# ══════════════════════════════════════════════════════════════════════════════

def project_wazn_with_relicensing(
    root_candidate,
    *,
    root_refinement=None,
    catalog=None,
) -> Phase4AResult:
    """
    أسقِط RootCandidate مع دعم WaznHypothesis + Ilaal + Root Re-Licensing.

    root_candidate  : RootCandidate (P3)
    root_refinement : RootHostRefinement (P3.10) — اختياري
    catalog         : tuple[WaznDefinition] للاختبار؛ وإلا get_catalog()

    القانون: final_directive لا يُشتق من source_path.
    source_path يصف المسار المُتبَّع فقط.
    """
    directive = str(getattr(root_candidate, 'directive', '')).strip().upper()

    # ── BLOCK: لا شيء يُفتح ────────────────────────────────────────────────
    if directive == 'BLOCK':
        ev, tr, res = _aggregate(root_candidate)
        return Phase4AResult(
            initial_root_directive = 'BLOCK',
            final_directive        = 'BLOCK',
            source_path            = 'blocked',
            root_candidate         = root_candidate,
            promoted_root_candidate= None,
            wazn_hypothesis        = None,
            ilaal_resolution       = None,
            relicensing_result     = None,
            wazn_projection        = None,
            final_wazn             = None,
            evidence_ids           = ev,
            trace_ids              = tr,
            residual_codes         = res + ('block:wazn:root_candidate_blocked',),
        )

    # ── ACCEPT: مسار مباشر ─────────────────────────────────────────────────
    if directive == 'ACCEPT':
        wazn_proj = project_wazn(root_candidate, catalog=catalog)
        fdir      = _directive_str(wazn_proj)
        fwazn     = _final_wazn(wazn_proj)
        ev, tr, res = _aggregate(root_candidate, wazn_proj=wazn_proj)
        return Phase4AResult(
            initial_root_directive = 'ACCEPT',
            final_directive        = fdir,
            source_path            = 'direct_accept',
            root_candidate         = root_candidate,
            promoted_root_candidate= None,
            wazn_hypothesis        = None,
            ilaal_resolution       = None,
            relicensing_result     = None,
            wazn_projection        = wazn_proj,
            final_wazn             = fwazn,
            evidence_ids           = ev,
            trace_ids              = tr,
            residual_codes         = res,
        )

    # ── DEFER: مسار الفرضية + الإعلال ─────────────────────────────────────
    if root_refinement is not None:
        refined_host    = root_refinement.refined_host
        removed_markers = tuple(root_refinement.removed_suffixes)
        ref_residual    = tuple(root_refinement.residual_codes)
    else:
        refined_host    = root_candidate.host_surface
        removed_markers = ()
        ref_residual    = ()

    residual_codes = ref_residual + tuple(root_candidate.residual_codes)

    # حاول بناء فرضية
    hypothesis = build_wazn_hypothesis(
        refined_host=refined_host,
        root_candidate=root_candidate,
        removed_markers=removed_markers,
        residual_codes=residual_codes,
    )

    # لا فرضية → ابقَ في deferred (لا إسقاط وزن)
    if hypothesis is None:
        ev, tr, res = _aggregate(root_candidate)
        return Phase4AResult(
            initial_root_directive = 'DEFER',
            final_directive        = 'DEFER',
            source_path            = 'deferred',
            root_candidate         = root_candidate,
            promoted_root_candidate= None,
            wazn_hypothesis        = None,
            ilaal_resolution       = None,
            relicensing_result     = None,
            wazn_projection        = None,
            final_wazn             = None,
            evidence_ids           = ev,
            trace_ids              = tr,
            residual_codes         = res + ('defer:wazn:no_hypothesis_built',),
        )

    # ── P4A-β: محاولة حل الجذر الضعيف إن كان غير محلول ──────────────────
    ilaal_result = None
    hypothesis_to_relicense = hypothesis

    if hypothesis.proposed_root_after is None:
        ilaal_result = apply_ilaal_resolution(hypothesis)

        if (ilaal_result.directive == 'ACCEPT'
                and ilaal_result.proposed_root is not None):
            hypothesis_to_relicense = WaznHypothesis(
                refined_host        = hypothesis.refined_host,
                proposed_wazn       = hypothesis.proposed_wazn,
                ziyadah_detected    = hypothesis.ziyadah_detected,
                proposed_root_after = tuple(ilaal_result.proposed_root),
                confidence          = 'HIGH',
                evidence_ids        = ilaal_result.evidence_ids,
                residual_codes      = ilaal_result.residual_codes,
                radical_alignment   = hypothesis.radical_alignment,
                removed_elements    = hypothesis.removed_elements,
            )

    # ── P3.11: بوابة الترخيص ─────────────────────────────────────────────
    relicensing = relicense_root_from_wazn_hypothesis(
        hypothesis_to_relicense,
        ilaal_resolution=ilaal_result,
    )

    if relicensing.directive == 'ACCEPT' and hypothesis_to_relicense.proposed_root_after:
        # ارفع RootCandidate مع الجذر المُرخَّص
        promoted = RootCandidate(
            surface           = root_candidate.surface,
            host_surface      = root_candidate.host_surface,
            directive         = 'ACCEPT',
            canonical_root    = tuple(hypothesis_to_relicense.proposed_root_after),
            root_profile      = dict(root_candidate.root_profile),
            evidence_ids      = (tuple(root_candidate.evidence_ids)
                                 + tuple(relicensing.evidence_ids)),
            trace_ids         = (tuple(root_candidate.trace_ids)
                                 + ('p4a:hypothesis_relicensed',)),
            residual_codes    = (tuple(root_candidate.residual_codes)
                                 + tuple(relicensing.residual_codes)),
            source_projection = 'WaznHypothesisRelicensing',
        )
        wazn_proj = project_wazn(promoted, catalog=catalog)
        fdir      = _directive_str(wazn_proj)
        fwazn     = _final_wazn(wazn_proj)
        ev, tr, res = _aggregate(root_candidate, wazn_proj=wazn_proj,
                                 relicensing=relicensing, promoted=promoted)
        return Phase4AResult(
            initial_root_directive = 'DEFER',
            final_directive        = fdir,
            source_path            = 'hypothesis_relicensed',
            root_candidate         = root_candidate,
            promoted_root_candidate= promoted,
            wazn_hypothesis        = hypothesis_to_relicense,
            ilaal_resolution       = ilaal_result,
            relicensing_result     = relicensing,
            wazn_projection        = wazn_proj,
            final_wazn             = fwazn,
            evidence_ids           = ev,
            trace_ids              = tr,
            residual_codes         = res,
        )

    # الترخيص DEFER أو BLOCK → لا ترقية، لا إسقاط وزن
    ev, tr, res = _aggregate(root_candidate, relicensing=relicensing)
    return Phase4AResult(
        initial_root_directive = 'DEFER',
        final_directive        = 'DEFER',
        source_path            = 'deferred',
        root_candidate         = root_candidate,
        promoted_root_candidate= None,
        wazn_hypothesis        = hypothesis_to_relicense,
        ilaal_resolution       = ilaal_result,
        relicensing_result     = relicensing,
        wazn_projection        = None,
        final_wazn             = None,
        evidence_ids           = ev,
        trace_ids              = tr,
        residual_codes         = res + ('defer:wazn:relicensing_did_not_accept',),
    )
