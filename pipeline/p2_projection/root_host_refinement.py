#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_projection/root_host_refinement.py — Root Host Refinement (Phase 3.10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

طبقة تنقية المضيف بين PreRootDecision وHR2SRootAdapter.

الموقع في السلسلة:
  AttachmentProjection (P5)
  → PreRootDecision
  → RootHostRefinement   ← هذه الطبقة
  → HR2SRootAdapter
  → RootProjection P2
  → RootCandidate P3

المسؤولية الوحيدة:
  إزالة اللواحق الطرفية اليقينية فقط — لا أكثر:
    1. تاء التأنيث في الفعل الماضي (verbal_root_path + تْ/تِ)
    2. التاء المربوطة النهائية (nominal_morphology_path + ة)،
       وتحقيقها في حالة الإضافة (تُ/تِ الطرفية بعد حرف متحرك).

القيود الصارمة (لا خرق):
  - لا استثناءات نصية خاصة بكلمات — فقط الشواهد البنيوية.
  - لا تُحذف ميم الاشتقاق، ولا حروف المضارعة، ولا السوابق، ولا أي حرف داخلي.
  - لا تُنتج canonical_root ولا wazn.
  - لا تُحوّل DEFER إلى OPEN — التوجيه موروث من PreRoot كما هو.

قواعد الرتابة:
  PreRoot BLOCK → directive=BLOCK → لا حذف إطلاقًا.
  PreRoot DEFER → directive=DEFER → الحذف يعمل لكن لا يُرفع إلى OPEN.
  PreRoot OPEN  → directive=OPEN  → الحذف يعمل → HR2S يحلّل refined_host.
"""

from __future__ import annotations

from dataclasses import dataclass

from pipeline.p0_unicode.glyph_classification import build_glyph_traces


# ══════════════════════════════════════════════════════════════════════════════
# 1.  الثوابت البنيوية
# ══════════════════════════════════════════════════════════════════════════════

_TA_PLAIN:   str = 'ت'   # U+062A — التاء المبسوطة
_TA_MARBUTA: str = 'ة'   # U+0629 — التاء المربوطة
_MEEM:       str = 'م'   # U+0645 — ميم (قد تكون ميم اشتقاق داخلية)

# رموز اللواحق المُزالة
PAST_FEMININE_TA: str = 'PAST_FEMININE_TA'
NOMINAL_TA_MARBUTA: str = 'NOMINAL_TA_MARBUTA'

# رمز التحفظ عند بقاء زيادة داخلية غير محلولة (خارج النطاق الحالي)
_RESIDUAL_INTERNAL_ZIYADAH = 'defer:root_refinement:internal_ziyadah_not_resolved'


# ══════════════════════════════════════════════════════════════════════════════
# 2.  النموذج المُجمَّد
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RootHostRefinement:
    """
    نتيجة تنقية المضيف قبل إرساله إلى HR2S.

    Attributes
    ----------
    input_host       : المضيف قبل التنقية (كما ورد من PreRoot).
    refined_host     : المضيف بعد التنقية (يُرسَل إلى HR2S عند OPEN).
    removed_prefixes : سوابق مُزالة — فارغة دائمًا في النطاق الحالي.
    removed_suffixes : لواحق مُزالة — PAST_FEMININE_TA | NOMINAL_TA_MARBUTA.
    retained_markers : علامات مُحتفَظ بها (تحقيق سطحي للّاحقة المُزالة إن وُجدت).
    evidence_ids     : شواهد قرار التنقية.
    trace_ids        : مسار التنفيذ الداخلي.
    directive        : OPEN | DEFER | BLOCK — موروث من PreRoot دون تعديل.
    residual_codes   : رموز التحفظ (زيادة داخلية غير محلولة، ...).
    """
    input_host:       str
    refined_host:     str
    removed_prefixes: tuple[str, ...]
    removed_suffixes: tuple[str, ...]
    retained_markers: tuple[str, ...]
    evidence_ids:     tuple[str, ...]
    trace_ids:        tuple[str, ...]
    directive:        str
    residual_codes:   tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            'input_host':       self.input_host,
            'refined_host':     self.refined_host,
            'removed_prefixes': list(self.removed_prefixes),
            'removed_suffixes': list(self.removed_suffixes),
            'retained_markers': list(self.retained_markers),
            'evidence_ids':     list(self.evidence_ids),
            'trace_ids':        list(self.trace_ids),
            'directive':        self.directive,
            'residual_codes':   list(self.residual_codes),
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  نقطة الدخول
# ══════════════════════════════════════════════════════════════════════════════

def refine_root_host(
    host: str,
    *,
    morphology_path: str,
    pre_root_directive: str,
) -> RootHostRefinement:
    """
    نقِّ المضيف بإزالة اللواحق الطرفية اليقينية ضمن النطاق المحدَّد فقط.

    Parameters
    ----------
    host               : المضيف قبل التنقية (host_surface من PreRoot).
    morphology_path    : قيمة MorphologyPath.value (مثل 'verbal_root_path').
    pre_root_directive : 'OPEN' | 'DEFER' | 'BLOCK' — من PreRoot.

    Returns
    -------
    RootHostRefinement
    """
    directive = pre_root_directive
    trace_ids: list[str] = ['step:root_host_refinement:enter']

    # ── رتابة BLOCK: لا حذف إطلاقًا ──────────────────────────────────────────
    if directive == 'BLOCK':
        trace_ids.append('step:blocked_no_refinement')
        return RootHostRefinement(
            input_host       = host,
            refined_host     = host,
            removed_prefixes = (),
            removed_suffixes = (),
            retained_markers = (),
            evidence_ids     = ('root_refinement_blocked_by_pre_root',),
            trace_ids        = tuple(trace_ids),
            directive        = directive,
            residual_codes   = (),
        )

    traces = build_glyph_traces(host)
    trace_ids.append('step:glyph_traces_built')

    removed_suffixes: tuple[str, ...] = ()
    evidence_ids: list[str] = []
    residual_codes: list[str] = []
    retained_markers: tuple[str, ...] = ()
    refined_host = host

    # ── 1. تاء التأنيث في الفعل الماضي ───────────────────────────────────────
    if morphology_path == 'verbal_root_path' and _is_past_feminine_ta(traces):
        refined_host      = _reconstruct(traces[:-1])
        retained_markers  = (_glyph_surface(traces[-1]),)
        removed_suffixes  = (PAST_FEMININE_TA,)
        evidence_ids.append('terminal_feminine_ta_after_past_host')
        trace_ids.append('step:removed_past_feminine_ta')

    # ── 2. التاء المربوطة النهائية (وتحقيقها في الإضافة) ─────────────────────
    elif morphology_path == 'nominal_morphology_path':
        _kind = _nominal_terminal_ta_kind(traces)
        if _kind is not None:
            refined_host     = _reconstruct(traces[:-1])
            retained_markers = (_glyph_surface(traces[-1]),)
            removed_suffixes = (NOMINAL_TA_MARBUTA,)
            evidence_ids.append(_kind)
            trace_ids.append('step:removed_nominal_ta_marbuta')

            # تحفّظ: زيادة داخلية غير محلولة (ميم اشتقاق داخلية — خارج النطاق)
            if _has_unresolved_internal_ziyadah(traces[:-1]):
                residual_codes.append(_RESIDUAL_INTERNAL_ZIYADAH)
                trace_ids.append('step:internal_ziyadah_deferred')

    # ── لا تغيير ─────────────────────────────────────────────────────────────
    if not removed_suffixes:
        evidence_ids.append('no_terminal_suffix_to_refine')
        trace_ids.append('step:no_change')

    return RootHostRefinement(
        input_host       = host,
        refined_host     = refined_host,
        removed_prefixes = (),
        removed_suffixes = removed_suffixes,
        retained_markers = retained_markers,
        evidence_ids     = tuple(evidence_ids),
        trace_ids        = tuple(trace_ids),
        directive        = directive,
        residual_codes   = tuple(residual_codes),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 4.  الكواشف البنيوية
# ══════════════════════════════════════════════════════════════════════════════

def _is_past_feminine_ta(traces: list) -> bool:
    """
    هل ينتهي المضيف بتاء تأنيث الفعل الماضي (تْ / تِ)؟

    الشروط اليقينية:
      - آخر حرف أصلي هو ت.
      - عليه سكون (تْ) أو كسرة التقاء الساكنين (تِ) — لا تنوين.
      - الحرف الذي قبله متحرك (يحمل فتحة/ضمة/كسرة)، لا ساكنًا.
      - يبقى قبل التاء ≥ 3 حروف مرخّصة.

    يمنع الانزلاق في: بَيْت (تنوين)، وَقْت (ق ساكنة قبل التاء)، ...
    """
    if len(traces) < 4:            # ≥ 3 حروف + التاء
        return False
    last = traces[-1]
    if last.nfc_base != _TA_PLAIN:
        return False
    if last.has_tanwin:
        return False
    if not (last.has_sukun or last.has_kasra):
        return False
    prev = traces[-2]
    return bool(prev.has_short_vowel)


def _nominal_terminal_ta_kind(traces: list):
    """
    صنِّف التاء الطرفية في المسار الاسمي.

    Returns
    -------
    None                                            — لا تاء طرفية مؤهَّلة.
    'terminal_ta_marbuta_after_nominal_host'        — ة صريحة.
    'terminal_ta_marbuta_construct_after_nominal_host' — تحقيق مبسوط في الإضافة (تُ/تِ).
    """
    if len(traces) < 3:
        return None
    last = traces[-1]

    # التاء المربوطة الصريحة
    if last.nfc_base == _TA_MARBUTA:
        return 'terminal_ta_marbuta_after_nominal_host'

    # تحقيق التاء المربوطة مبسوطةً في الإضافة (عَمَّتُ، شَجَرَتِ ...)
    # نفس قيد منع الانزلاق: الحرف قبل التاء متحرك، ولا تنوين.
    if last.nfc_base == _TA_PLAIN and len(traces) >= 4:
        if last.has_tanwin:
            return None
        if not (last.has_short_vowel or last.has_sukun):
            return None
        if traces[-2].has_short_vowel:
            return 'terminal_ta_marbuta_construct_after_nominal_host'
    return None


def _has_unresolved_internal_ziyadah(refined_traces: list) -> bool:
    """
    هل يحمل المضيف المُنقَّى زيادة داخلية غير محلولة (ميم اشتقاق)؟

    شاهد بنيوي محافظ (لا استثناءات كلمات):
      - يبدأ بميم متحركة (مَ/مُ/مِ) — موقع ميم الاشتقاق.
      - يتبقّى ≥ 4 حروف أصلية بعد إزالة اللاحقة — بنية مشتق لا جذر مجرَّد.

    مثال: مَحَبْبَ (م ح ب ب) → True (ميم اشتقاق داخلية لم تُحلّ بعد).
    مقابل: شِدْدَ / عَمْمَ / غَابَ (3 حروف، لا ميم صدرية) → False.
    """
    if len(refined_traces) < 4:
        return False
    first = refined_traces[0]
    return first.nfc_base == _MEEM and bool(first.has_short_vowel)


# ══════════════════════════════════════════════════════════════════════════════
# 5.  أدوات إعادة البناء
# ══════════════════════════════════════════════════════════════════════════════

def _glyph_surface(trace) -> str:
    """أعِد بناء السطح الخام لحرف واحد (الحرف + علاماته)."""
    return trace.raw_base + ''.join(trace.raw_marks)


def _reconstruct(traces: list) -> str:
    """أعِد بناء السطح الخام من سلسلة حروف مُتبقّية."""
    return ''.join(_glyph_surface(t) for t in traces)
