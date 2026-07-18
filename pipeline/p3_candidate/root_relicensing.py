#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_candidate/root_relicensing.py — Root Re-Licensing P3.11
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

بوابة إعادة الترخيص من WaznHypothesis.

شروط ACCEPT (كلها يجب أن تمر):
  1.  proposed_root_after ليس None
  2.  الجذر ثلاثي (len==3) أو رباعي (len==4)
  3.  لا هويات ممنوعة (ا/ى)
  4.  الهمزات المزخرفة (أ/إ/ؤ/ئ/آ) تُطبَّع إلى ء
  5.  جميع الحروف عربية صحيحة
  6.  الفرضية ليست LOW confidence
  7.  radical_alignment كامل (FA/AYN/LAM موجودة ومتطابقة مع الجذر)
  8.  لا تحول إعلالي بلا ترخيص صريح من IlaalResolution

الفرق بين DEFER وBLOCK:
  BLOCK = مانع قاطع: هوية ممنوعة، حرف غير عربي، تناقض هيكلي في المحاذاة.
  DEFER = نقص دليل: proposed_root=None، ثقة منخفضة، محاذاة ناقصة/غير محسوبة.

الرتابة:
  ACCEPT → يُرفع إلى project_wazn() مع الجذر المرخّص
  DEFER/BLOCK → لا WaznCandidate نهائي

W4 / W4.1:
  - canonical_root           : إعادة تسمية proposed_root
  - source_hypothesis_id     : إعادة تسمية source
  - source_resolution_id     : 'IlaalResolution' | None
  - to_dict()                : تسلسل JSON
  - ProposedRootResolution   : تُستهلك صراحةً عبر to_proposed_root_resolution()
  - بوابة radical_alignment  : W4.1
  - بوابة unknown_transformation : W4.1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1.  الثوابت
# ══════════════════════════════════════════════════════════════════════════════

# الهويات الممنوعة: ا وى فقط (الهمزات المزخرفة تُطبَّع إلى ء)
_PROHIBITED = frozenset({"ا", "ى", "?", "", None})

# الهمزات المزخرفة → ء
_HAMZA_VARIANTS: dict[str, str] = {
    "أ": "ء", "إ": "ء", "ؤ": "ء", "ئ": "ء", "آ": "ء",
}

# أدوار المواضع الجذرية في radical_alignment
_ROOT_ROLES = frozenset({
    'FA',
    'AYN', 'AYN_LONG_VOWEL', 'AYN_WEAK_SURFACE_YAA',
    'LAM', 'LAM2',
})
_AYN_ROLES = frozenset({'AYN', 'AYN_LONG_VOWEL', 'AYN_WEAK_SURFACE_YAA'})

# نطاق الحروف العربية الأساسية (U+0621–U+064A)
_ARABIC_BASE_MIN = 0x0621
_ARABIC_BASE_MAX = 0x064A


def _normalize_letter(ch: str) -> str:
    return _HAMZA_VARIANTS.get(ch, ch)


def _is_arabic_consonant(ch: str) -> bool:
    if not ch or len(ch) != 1:
        return False
    return _ARABIC_BASE_MIN <= ord(ch) <= _ARABIC_BASE_MAX


# ══════════════════════════════════════════════════════════════════════════════
# 2.  نموذج البيانات
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RootRelicensingResult:
    """نتيجة بوابة إعادة الترخيص من WaznHypothesis."""
    directive:            str              # 'ACCEPT' | 'DEFER' | 'BLOCK'
    canonical_root:       Optional[tuple]  # الجذر المرخَّص أو None
    source_hypothesis_id: str              # 'WaznHypothesis'
    source_resolution_id: Optional[str]   # 'IlaalResolution' | None
    failure_reason:       Optional[str]   # سبب الرفض أو None عند ACCEPT
    evidence_ids:         tuple
    trace_ids:            tuple
    residual_codes:       tuple

    def to_dict(self) -> dict:
        return {
            'directive':            self.directive,
            'canonical_root':       list(self.canonical_root) if self.canonical_root else None,
            'source_hypothesis_id': self.source_hypothesis_id,
            'source_resolution_id': self.source_resolution_id,
            'failure_reason':       self.failure_reason,
            'evidence_ids':         list(self.evidence_ids),
            'trace_ids':            list(self.trace_ids),
            'residual_codes':       list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def relicense_root_from_wazn_hypothesis(
    hypothesis,
    ilaal_resolution=None,
) -> RootRelicensingResult:
    """
    أعِد ترخيص الجذر المقترح من WaznHypothesis.

    hypothesis       : WaznHypothesis (duck-typing)
    ilaal_resolution : IlaalResolution | None
    """
    proposed   = hypothesis.proposed_root_after
    confidence = hypothesis.confidence
    ev         = tuple(hypothesis.evidence_ids)
    res        = tuple(hypothesis.residual_codes)
    src_res_id = 'IlaalResolution' if ilaal_resolution is not None else None

    def _defer(reason: str, root=None) -> RootRelicensingResult:
        return RootRelicensingResult(
            directive            = 'DEFER',
            canonical_root       = root,
            source_hypothesis_id = 'WaznHypothesis',
            source_resolution_id = src_res_id,
            failure_reason       = reason,
            evidence_ids         = ev,
            trace_ids            = (f'p3.11:defer:{reason.split(":")[-1]}',),
            residual_codes       = res + (reason,),
        )

    def _block(reason: str, root=None) -> RootRelicensingResult:
        return RootRelicensingResult(
            directive            = 'BLOCK',
            canonical_root       = root,
            source_hypothesis_id = 'WaznHypothesis',
            source_resolution_id = src_res_id,
            failure_reason       = reason,
            evidence_ids         = ev,
            trace_ids            = (f'p3.11:block:{reason.split(":")[-1]}',),
            residual_codes       = res + (reason,),
        )

    # ── 1. proposed_root_after يجب ألا يكون None ──────────────────────────
    if proposed is None:
        return _defer('defer:relicensing:proposed_root_extraction_incomplete')

    # ── 2. تطبيع الهمزات + تحويل إلى tuple ──────────────────────────────
    proposed = tuple(_normalize_letter(ch) for ch in proposed)

    # ── 3. الجذر ثلاثي أو رباعي ───────────────────────────────────────────
    if len(proposed) not in (3, 4):
        return _defer('defer:relicensing:non_trilateral_proposed_root', proposed)

    # ── 4. لا هويات ممنوعة (ا/ى) ─────────────────────────────────────────
    for ch in proposed:
        if ch in _PROHIBITED:
            return _block('block:relicensing:prohibited_root_identity', proposed)

    # ── 5. جميع الحروف عربية ─────────────────────────────────────────────
    for ch in proposed:
        if not _is_arabic_consonant(ch):
            return _block('block:relicensing:non_arabic_consonant_in_root', proposed)

    # ── 6. الثقة ليست LOW ────────────────────────────────────────────────
    if confidence == 'LOW':
        return _defer('defer:relicensing:low_confidence_hypothesis', proposed)

    # ── 7. استهلاك ProposedRootResolution + بوابة radical_alignment ──────
    #
    # نستدعي to_proposed_root_resolution() صراحةً (W4 — ProposedRootResolution use).
    # الدالة موجودة في WaznHypothesis بعد W2؛ نتعامل بـduck-typing.

    prs = None
    if callable(getattr(hypothesis, 'to_proposed_root_resolution', None)):
        prs = hypothesis.to_proposed_root_resolution()

    alignment = tuple(getattr(prs, 'radical_alignment', None) or ()) or \
                tuple(getattr(hypothesis, 'radical_alignment', None) or ())

    # 7a. المحاذاة يجب ألا تكون فارغة
    if not alignment:
        return _defer('defer:relicensing:alignment_not_computed', proposed)

    # 7b. يجب أن يكون في المحاذاة مواضع جذرية كافية (FA/AYN/LAM)
    root_role_entries = [(l, r) for l, r in alignment if r in _ROOT_ROLES]
    if len(root_role_entries) < len(proposed):
        return _defer('defer:relicensing:alignment_incomplete', proposed)

    # 7c. اتساق المحاذاة مع الجذر المقترح
    fa_letters  = [_normalize_letter(l) for l, r in alignment if r == 'FA']
    ayn_letters = [_normalize_letter(l) for l, r in alignment if r in _AYN_ROLES]
    lam_letters = [_normalize_letter(l) for l, r in alignment if r in ('LAM', 'LAM2')]

    # فاء الجذر يجب أن تتطابق
    if fa_letters:
        if fa_letters[0] != proposed[0]:
            return _block('block:relicensing:alignment_fa_contradiction', proposed)

    # لام الجذر يجب أن تتطابق
    if lam_letters and len(proposed) >= 3:
        if lam_letters[0] != proposed[-1]:
            return _block('block:relicensing:alignment_lam_contradiction', proposed)

    # عين الجذر: السطحي يمكن أن يختلف عن الأصل — لكن فقط بإذن IlaalResolution
    if ayn_letters and len(proposed) >= 2:
        surface_ayn    = ayn_letters[0]
        underlying_ayn = proposed[1]
        if surface_ayn != underlying_ayn:
            # لا إذن إعلال → تناقض
            if ilaal_resolution is None or ilaal_resolution.directive != 'ACCEPT':
                return _block('block:relicensing:ayn_surface_underlying_mismatch', proposed)
            # إذن موجود لكن لا تحول موثَّق → دليل ناقص
            if not getattr(ilaal_resolution, 'transformations', ()):
                return _defer(
                    'defer:relicensing:ayn_change_without_transformation_evidence',
                    proposed,
                )
            # ── 8. التحول يجب أن يكون معروفًا ────────────────────────────
            for trace in ilaal_resolution.transformations:
                if not getattr(trace, 'licensed_by', None):
                    return _block('block:root_relicensing:unknown_transformation_id', proposed)

    # ── ACCEPT ─────────────────────────────────────────────────────────────
    accept_ev = ev + ('p3.11:relicensed',)
    if ilaal_resolution is not None:
        accept_ev = accept_ev + tuple(
            getattr(ilaal_resolution, 'evidence_ids', ()) or ()
        )

    return RootRelicensingResult(
        directive            = 'ACCEPT',
        canonical_root       = proposed,
        source_hypothesis_id = 'WaznHypothesis',
        source_resolution_id = src_res_id,
        failure_reason       = None,
        evidence_ids         = accept_ev,
        trace_ids            = ('p3.11:accept',),
        residual_codes       = res,
    )
