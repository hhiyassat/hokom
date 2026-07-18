#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/wazn_projection.py — أوركسترا Phase 4A
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

المدخل الوحيد: project_wazn(root_candidate) → WaznProjection.

القواعد:
  - يستهلك RootCandidate فقط. لا HR2S، لا إعادة استخراج للجذر، لا تعديل canonical_root.
  - رتابة صارمة:
      RootCandidate BLOCK → Wazn BLOCK / NOT_OPENED (لا alignment).
      RootCandidate DEFER → Wazn DEFER / NOT_OPENED (لا alignment).
      RootCandidate ACCEPT → Wazn ACCEPT / DEFER / BLOCK.
  - يستعمل analyzed_host (لا السطح الكامل)، ولا يُدخل أداة تعريف ولا ضمائر.
  - يفصل اللواحق التصريفية عن الوزن الاشتقاقي.
  - لا يختار بابًا ولا يولّد مصدرًا/مشتقات (ملك Phase 4B فصاعدًا).
"""

from __future__ import annotations

from typing import Optional

from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda

from .models import (
    WaznDirective, WaznStageState, RootSlot, AlignmentKind,
    WaznSlotAlignment, WaznCandidate, WaznProjection,
    WaznProjectionContractError, PROJECTION_VERSION,
)
from .wazn_catalog import get_catalog, WaznDefinition
from .alignment import (
    parse_cells, align_wazn, AlignmentAttempt,
    is_ordered_subsequence, residual_letters_are_augment,
)
from . import weak_operations as wk


_SUPPORTED_ARITY = frozenset({3, 4})
_VALID_ROOT_DIRECTIVES = ("ACCEPT", "DEFER", "BLOCK")
_ROOT_SLOT_ORDER = {RootSlot.FA: 0, RootSlot.AIN: 1, RootSlot.LAM: 2, RootSlot.FOURTH: 3}

# حروف العلة الجذرية التي قد تتحول على السطح (إعلال و→ي، ي→أ...).
# غيابها من السطح لا يعني استحالة بنيوية — يعني نقص ترخيص في الـcatalog.
_WEAK_RADICALS = frozenset({"و", "ي"})


# ══════════════════════════════════════════════════════════════════════════════
# تطبيع خاص بالوزن — همزة + شدة فقط (لا أداة تعريف: لا نُعيد إدخالها هنا)
# ══════════════════════════════════════════════════════════════════════════════

def normalize_for_wazn(host: str) -> str:
    """طبّع المضيف لأغراض المحاذاة: توحيد الهمزة (→ء) وتوسيع الشدة فقط.

    لا يُطبَّق منطق أداة التعريف — Phase 4A لا تعرف «ال» ولا تُعيد إدخالها.
    """
    return normalize_shadda(normalize_hamza(host))


# ══════════════════════════════════════════════════════════════════════════════
# بنّاؤو الحالات
# ══════════════════════════════════════════════════════════════════════════════

def _not_opened(
    *, input_surface, analyzed_host, normalized_host, directive, residual_codes,
    evidence_ids, trace_ids,
) -> WaznProjection:
    return WaznProjection(
        input_surface=input_surface,
        analyzed_host=analyzed_host,
        normalized_host=normalized_host,
        canonical_root=None,
        directive=directive,
        stage_state=WaznStageState.NOT_OPENED,
        candidate_awzan=(),
        selected_wazn=None,
        root_slot_alignment=(),
        ziyadah_slots=(),
        weak_operations=(),
        unresolved_operations=(),
        inflectional_suffixes=(),
        evidence_ids=tuple(evidence_ids),
        trace_ids=tuple(trace_ids),
        residual_codes=tuple(residual_codes),
        source_root_candidate="RootCandidate",
        projection_version=PROJECTION_VERSION,
    )


def _candidate_from_attempt(attempt: AlignmentAttempt) -> WaznCandidate:
    return WaznCandidate(
        wazn_id=attempt.wazn.wazn_id,
        wazn_pattern=attempt.wazn.pattern,
        wazn_family=attempt.wazn.family,
        alignment=tuple(attempt.alignments) + tuple(attempt.inflectional_cells),
        root_slots_complete=attempt.root_slots_complete,
        ziyadah_slots=attempt.ziyadah_slots,
        deleted_root_slots=attempt.deleted_root_slots,
        weak_operations=attempt.weak_operations,
        confidence_rank=attempt.wazn.evidence_rank,
        evidence_ids=(f"wazn:{attempt.wazn.wazn_id}:aligned",),
        residual_codes=(),
    )


def _assert_accept_invariants(selected: WaznCandidate, canonical_root: tuple,
                              candidate_awzan: tuple, input_surface: str) -> None:
    """دفاع في العمق: تحقّق من عقود ACCEPT قبل إصداره."""
    if selected not in candidate_awzan:
        raise WaznProjectionContractError(
            f"selected_wazn not among candidate_awzan for {input_surface!r}")
    if not selected.root_slots_complete:
        raise WaznProjectionContractError(
            f"ACCEPT with an unresolved root slot for {input_surface!r}")
    # ترتيب الجذر محفوظ: خانات الجذر تظهر بترتيب ف→ع→ل(→ل2) وفهارس متصاعدة.
    root_aligns = [a for a in selected.alignment if a.root_slot is not None]
    order = [_ROOT_SLOT_ORDER[a.root_slot] for a in root_aligns]
    if order != sorted(order) or order != list(range(len(canonical_root))):
        raise WaznProjectionContractError(
            f"alignment does not preserve root order for {input_surface!r}: {order}")
    indices = [a.surface_index for a in root_aligns if a.surface_index is not None]
    if indices != sorted(indices):
        raise WaznProjectionContractError(
            f"root slots not in increasing surface order for {input_surface!r}")
    # لا هوية جذرية من ا/ى.
    for a in root_aligns:
        if wk.is_prohibited_radical(a.root_identity):
            raise WaznProjectionContractError(
                f"ACCEPT with prohibited radical identity {a.root_identity!r} "
                f"for {input_surface!r}")


# ══════════════════════════════════════════════════════════════════════════════
# المدخل الرئيس
# ══════════════════════════════════════════════════════════════════════════════

def project_wazn(
    root_candidate,
    *,
    normalized_host: Optional[str] = None,
    catalog: Optional[tuple] = None,
) -> WaznProjection:
    """أسقِط RootCandidate المقبول على بنية السطح وأنتج WaznProjection.

    root_candidate  : كائن RootCandidate (P3) — المدخل الوحيد المعتمد.
    normalized_host : اختياري؛ إن لم يُمرَّر يُشتق من analyzed_host عبر
                      normalize_for_wazn (همزة + شدة فقط).
    catalog         : اختياري؛ tuple[WaznDefinition] (للاختبار)، وإلا get_catalog().
    """
    directive = str(getattr(root_candidate, "directive", "")).strip().upper()
    input_surface = root_candidate.surface
    analyzed_host = root_candidate.host_surface
    canonical_root = root_candidate.canonical_root

    ev_root = tuple(getattr(root_candidate, "evidence_ids", ()) or ())
    tr_root = tuple(getattr(root_candidate, "trace_ids", ()) or ())
    res_root = tuple(getattr(root_candidate, "residual_codes", ()) or ())

    nh = normalized_host if normalized_host is not None else normalize_for_wazn(analyzed_host)

    if directive not in _VALID_ROOT_DIRECTIVES:
        raise WaznProjectionContractError(
            f"unknown RootCandidate directive {root_candidate.directive!r} "
            f"for {input_surface!r}")

    # ── رتابة: BLOCK/DEFER لا يفتحان alignment ────────────────────────────
    if directive == "BLOCK":
        return _not_opened(
            input_surface=input_surface, analyzed_host=analyzed_host,
            normalized_host=nh, directive=WaznDirective.BLOCK,
            residual_codes=res_root + ("block:wazn:root_candidate_blocked",),
            evidence_ids=ev_root, trace_ids=tr_root + ("wazn:not_opened:root_blocked",))
    if directive == "DEFER":
        return _not_opened(
            input_surface=input_surface, analyzed_host=analyzed_host,
            normalized_host=nh, directive=WaznDirective.DEFER,
            residual_codes=res_root + ("defer:wazn:root_candidate_not_resolved",),
            evidence_ids=ev_root, trace_ids=tr_root + ("wazn:not_opened:root_deferred",))

    # ── ACCEPT: العقد يشترط جذرًا محلولًا سليمًا ───────────────────────────
    if not canonical_root:
        raise WaznProjectionContractError(
            f"ACCEPT RootCandidate without a canonical_root for {input_surface!r}")
    for r in canonical_root:
        if wk.is_prohibited_radical(r):
            raise WaznProjectionContractError(
                f"ACCEPT root carries prohibited identity {r!r} (ا/ى) for {input_surface!r}")
    arity = len(canonical_root)
    if arity not in _SUPPORTED_ARITY:
        raise WaznProjectionContractError(
            f"unsupported root arity {arity} for {input_surface!r}")

    cat = catalog if catalog is not None else get_catalog()
    cells = parse_cells(nh)

    attempts = [align_wazn(canonical_root, cells, w)
                for w in cat if w.root_arity == arity]
    clean = [a for a in attempts if a.matched and a.trailing_kind in ("clean", "inflectional")]
    nominal = [a for a in attempts if a.matched and a.trailing_kind == "nominal"]

    trace = tr_root + ("wazn:opened",)

    # ── ACCEPT: مطابقة نظيفة وحيدة ─────────────────────────────────────────
    if len(clean) == 1:
        attempt = clean[0]
        selected = _candidate_from_attempt(attempt)
        candidate_awzan = (selected,)
        _assert_accept_invariants(selected, canonical_root, candidate_awzan, input_surface)

        root_align = tuple(a for a in selected.alignment
                           if a.alignment_kind == AlignmentKind.ROOT_RADICAL)
        infl_suffixes = tuple(a.surface_segment for a in selected.alignment
                              if a.alignment_kind == AlignmentKind.INFLECTIONAL)
        return WaznProjection(
            input_surface=input_surface,
            analyzed_host=analyzed_host,
            normalized_host=nh,
            canonical_root=tuple(canonical_root),
            directive=WaznDirective.ACCEPT,
            stage_state=WaznStageState.COMPLETED,
            candidate_awzan=candidate_awzan,
            selected_wazn=selected,
            root_slot_alignment=root_align,
            ziyadah_slots=selected.ziyadah_slots,
            weak_operations=selected.weak_operations,
            unresolved_operations=(),
            inflectional_suffixes=infl_suffixes,
            evidence_ids=ev_root + selected.evidence_ids,
            trace_ids=trace,
            residual_codes=res_root,
            source_root_candidate="RootCandidate",
            projection_version=PROJECTION_VERSION,
        )

    # ── DEFER: تعدد الأوزان المطابقة ───────────────────────────────────────
    if len(clean) > 1:
        candidates = tuple(_candidate_from_attempt(a) for a in
                           sorted(clean, key=lambda a: a.wazn.evidence_rank))
        return _deferred(input_surface, analyzed_host, nh, canonical_root,
                         candidates, ev_root, trace,
                         res_root + ("defer:wazn:multiple_licensed_patterns",))

    # ── DEFER: تأنيث اسمي يحتاج وزنًا مرخّصًا ───────────────────────────────
    if nominal:
        candidates = tuple(_candidate_from_attempt(a) for a in
                           sorted(nominal, key=lambda a: a.wazn.evidence_rank))
        return _deferred(input_surface, analyzed_host, nh, canonical_root,
                         candidates, ev_root, trace,
                         res_root + ("defer:wazn:nominal_feminine_requires_licensed_wazn",))

    # ── لا مطابقة: DEFER (زيادة محتملة) أم BLOCK (بنية مستحيلة)؟ ────────────
    if (is_ordered_subsequence(canonical_root, cells)
            and residual_letters_are_augment(canonical_root, cells)):
        return _deferred(input_surface, analyzed_host, nh, canonical_root,
                         (), ev_root, trace,
                         res_root + ("defer:wazn:unlicensed_but_structural_augment",))

    # ── جذر ضعيف: و/ي قد تتحول على السطح (إعلال مرخَّص) ──────────────────────
    # is_ordered_subsequence فشل لأن الحرف الضعيف لا يظهر بصورته الأصلية.
    # إذا كانت كل الحروف الزائدة من حروف الزيادة، فالبنية ممكنة لكن الوزن غير مرخَّص.
    # الحكم: DEFER (نقص بيانات) لا BLOCK (استحالة بنيوية).
    if any(r in _WEAK_RADICALS for r in canonical_root):
        if residual_letters_are_augment(canonical_root, cells):
            return _deferred(input_surface, analyzed_host, nh, canonical_root,
                             (), ev_root, trace,
                             res_root + ("defer:wazn:catalog_pattern_not_licensed",))

    # بنية مستحيلة: ترتيب مكسور أو حرف زائد غير من الزيادة أو غياب جذري.
    return WaznProjection(
        input_surface=input_surface,
        analyzed_host=analyzed_host,
        normalized_host=nh,
        canonical_root=tuple(canonical_root),
        directive=WaznDirective.BLOCK,
        stage_state=WaznStageState.BLOCKED,
        candidate_awzan=(),
        selected_wazn=None,
        root_slot_alignment=(),
        ziyadah_slots=(),
        weak_operations=(),
        unresolved_operations=(),
        inflectional_suffixes=(),
        evidence_ids=ev_root,
        trace_ids=trace,
        residual_codes=res_root + ("block:wazn:no_licensed_pattern",),
        source_root_candidate="RootCandidate",
        projection_version=PROJECTION_VERSION,
    )


def _deferred(input_surface, analyzed_host, nh, canonical_root,
              candidates, ev_root, trace, residual_codes) -> WaznProjection:
    return WaznProjection(
        input_surface=input_surface,
        analyzed_host=analyzed_host,
        normalized_host=nh,
        canonical_root=tuple(canonical_root),
        directive=WaznDirective.DEFER,
        stage_state=WaznStageState.DEFERRED,
        candidate_awzan=tuple(candidates),
        selected_wazn=None,
        root_slot_alignment=(),
        ziyadah_slots=(),
        weak_operations=(),
        unresolved_operations=(),
        inflectional_suffixes=(),
        evidence_ids=ev_root,
        trace_ids=trace,
        residual_codes=tuple(residual_codes),
        source_root_candidate="RootCandidate",
        projection_version=PROJECTION_VERSION,
    )
