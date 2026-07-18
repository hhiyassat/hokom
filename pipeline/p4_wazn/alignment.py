#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/alignment.py — مقابلة الجذر بالسطح (root ↔ surface geometry)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يقابل canonical_root (من RootCandidate) ببنية المضيف المطبَّع وفق قالب وزن
مرخّص، محافظًا على:
  ف ↔ radical 1 ، ع ↔ radical 2 ، ل ↔ radical 3 (ول2 ↔ radical 4 في الرباعي).

قواعد صارمة:
  - المحاذاة ترتيبية ومحافظة على الهوية (لا تبديل، لا إسقاط بلا operation).
  - حرف المدّ (ا/و/ي) لا يُعدّ جذريًا لمجرد ظهوره؛ الواو/الياء الجذريتان
    تُؤخذان من RootCandidate فقط.
  - الشدة قد تكون تكرار حرف جذري (مضاعف) أو تضعيف عين الوزن — القالب يحسم ذلك.
  - كل حرف في المضيف يجب أن يُحسَب (جذر/زيادة/تصريف)، لا إسقاط صامت.

المخرج: AlignmentAttempt — محاولة مقابلة قالب وزن واحد بالسطح.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .models import RootSlot, AlignmentKind, WaznSlotAlignment
from .wazn_catalog import WaznDefinition, TemplateCell
from . import weak_operations as wk


# ── علامات التشكيل التي تُجمع مع الحرف الأساس ────────────────────────────────
_ALL_MARKS = wk.VOWEL_MARKS | wk.TANWIN | {wk.SHADDA, "ٓ", "ٔ", "ٕ", "ٰ"}


# ══════════════════════════════════════════════════════════════════════════════
# 1.  تقطيع السطح المطبَّع إلى خلايا (حرف أساس + حركته)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SurfaceCell:
    base:       str
    vowel:      Optional[str]   # 'FATHA'|'DAMMA'|'KASRA'|'SUKUN' أو None
    index:      int
    has_tanwin: bool
    raw:        str


def parse_cells(normalized_host: str) -> list:
    """قطّع السطح المطبَّع إلى خلايا (حرف أساس + حركاته). يتجاهل الفراغات."""
    cells: list = []
    i = 0
    n = len(normalized_host)
    while i < n:
        ch = normalized_host[i]
        if ch in _ALL_MARKS or ch == " ":
            i += 1
            continue
        j = i + 1
        diac: list = []
        while j < n and normalized_host[j] in _ALL_MARKS:
            diac.append(normalized_host[j])
            j += 1
        vowel = None
        for d in diac:
            if d in wk.VOWEL_MARKS:
                vowel = wk.VOWEL_NAME[d]
                break
        has_tanwin = any(d in wk.TANWIN for d in diac)
        cells.append(SurfaceCell(
            base=ch, vowel=vowel, index=i,
            has_tanwin=has_tanwin, raw=normalized_host[i:j],
        ))
        i = j
    return cells


# ══════════════════════════════════════════════════════════════════════════════
# 2.  توسيع قالب الوزن بحروف جذر بعينه
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class _ExpectedCell:
    letter:      Optional[str]      # الهوية المتوقّعة (حرف جذر أو زيادة حرفية)
    vowel:       str                # حركة القالب
    kind:        AlignmentKind
    root_slot:   Optional[RootSlot]
    root_index:  Optional[int]
    operation:   Optional[str] = None
    geminate_of: Optional[str] = None


def _expand_template(wazn: WaznDefinition, canonical_root: tuple) -> Optional[list]:
    """استبدل علامات الجذر في القالب بحروف canonical_root. None لو تعذّر."""
    if len(canonical_root) != wazn.root_arity:
        return None
    out: list = []
    for cell in wazn.template:
        if cell.is_root:
            idx = cell.root_index
            if idx is None or idx >= len(canonical_root):
                return None
            out.append(_ExpectedCell(
                letter=canonical_root[idx], vowel=cell.vowel,
                kind=AlignmentKind.ROOT_RADICAL, root_slot=cell.root_slot,
                root_index=idx,
            ))
        elif cell.geminate_of is not None:
            gidx = {"FA": 0, "AIN": 1, "LAM": 2, "FOURTH": 3}[cell.geminate_of]
            if gidx >= len(canonical_root):
                return None
            out.append(_ExpectedCell(
                letter=canonical_root[gidx], vowel=cell.vowel,
                kind=AlignmentKind.ZIYADAH, root_slot=None, root_index=None,
                operation=wk.OP_ZIYADAH_GEMINATION, geminate_of=cell.geminate_of,
            ))
        else:  # زيادة حرفية
            out.append(_ExpectedCell(
                letter=cell.letter, vowel=cell.vowel,
                kind=AlignmentKind.ZIYADAH, root_slot=None, root_index=None,
            ))
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 3.  نتيجة محاولة المحاذاة
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AlignmentAttempt:
    wazn:                WaznDefinition
    matched:             bool
    trailing_kind:       str  # 'clean'|'inflectional'|'nominal'|'reject'|'arity'|'short'
    alignments:          tuple = ()
    inflectional_cells:  tuple = ()
    ziyadah_slots:       tuple = ()
    weak_operations:     tuple = ()
    deleted_root_slots:  tuple = ()
    root_slots_complete: bool = False
    reject_reason:       Optional[str] = None


def _vowel_ok(required: str, cell: SurfaceCell) -> bool:
    if required in ("FINAL", "ANY", "MATER"):
        return True
    return cell.vowel == required


def _classify_trailing(trailing: list) -> tuple:
    """صنّف الخلايا الزائدة بعد قالب الوزن.

    → ('clean', ())                : لا زيادة.
    → ('inflectional', cells)      : تاء التأنيث الساكنة (لاحقة تصريفية).
    → ('nominal', cells)           : تاء مربوطة (تأنيث اسمي يحتاج عقدًا مرخّصًا).
    → ('reject', cells)            : زيادة غير مفسَّرة.
    """
    if not trailing:
        return ("clean", ())
    if all(c.base == wk.TA and c.vowel == "SUKUN" for c in trailing):
        return ("inflectional", tuple(trailing))
    if any(wk.is_taa_marbuta(c.base) for c in trailing):
        return ("nominal", tuple(trailing))
    return ("reject", tuple(trailing))


def align_wazn(canonical_root: tuple, cells: list, wazn: WaznDefinition) -> AlignmentAttempt:
    """حاول مقابلة قالب وزن واحد بخلايا السطح. لا يرفع استثناءً — يُعيد محاولة."""
    expected = _expand_template(wazn, canonical_root)
    if expected is None:
        return AlignmentAttempt(wazn=wazn, matched=False, trailing_kind="arity",
                                reject_reason="root arity != wazn arity")

    n = len(expected)
    if len(cells) < n:
        return AlignmentAttempt(wazn=wazn, matched=False, trailing_kind="short",
                                reject_reason="host shorter than wazn template")

    core = cells[:n]
    trailing = cells[n:]

    aligns: list = []
    ziyadah_slots: list = []
    weak_ops: list = []

    for k, (exp, cell) in enumerate(zip(expected, core)):
        # ── مطابقة الهوية ────────────────────────────────────────────────
        if exp.kind == AlignmentKind.ROOT_RADICAL:
            if not wk.letters_match(exp.letter, cell.base):
                return AlignmentAttempt(wazn=wazn, matched=False, trailing_kind="reject",
                                        reject_reason=f"root letter mismatch at slot {k}")
        else:  # ZIYADAH (حرفية أو تضعيفية)
            if not (cell.base == exp.letter or wk.hamza_equivalent(exp.letter, cell.base)):
                return AlignmentAttempt(wazn=wazn, matched=False, trailing_kind="reject",
                                        reject_reason=f"ziyadah letter mismatch at slot {k}")

        # ── مطابقة الحركة (مع رخصة إدغام المضاعف) ─────────────────────────
        operation = exp.operation
        vowel_ok = _vowel_ok(exp.vowel, cell)
        if (not vowel_ok
                and exp.kind == AlignmentKind.ROOT_RADICAL
                and cell.vowel == "SUKUN"
                and wazn.permits_geminate_root_idghaam()
                and k + 1 < n
                and expected[k + 1].kind == AlignmentKind.ROOT_RADICAL
                and expected[k + 1].letter == exp.letter):
            # مضاعف: أُدغِم الحرف الأول (سكون) في الثاني — عملية مرخّصة.
            vowel_ok = True
            operation = wk.OP_MUDAAF_GEMINATION
            if wk.OP_MUDAAF_GEMINATION not in weak_ops:
                weak_ops.append(wk.OP_MUDAAF_GEMINATION)
        if not vowel_ok:
            return AlignmentAttempt(wazn=wazn, matched=False, trailing_kind="reject",
                                    reject_reason=f"vowel mismatch at slot {k}")

        # امنع مطابقة زائفة للمضاعف: سكونُ إدغام حرفين جذريين متطابقين متجاورين
        # لا يجوز أن يُقرأ سكونَ وزنٍ ساكن العين (فَعْل) لا يرخّص الإدغام. الوزن الذي
        # يرخّص الإدغام (فَعَلَ) وحده يقبل المضاعف. هذا يمنع تعدّد المطابقة الزائف
        # (مَدَّ = مَدْدَ يطابق فَعَلَ بإدغام مرخّص، لا فَعْل).
        if (exp.kind == AlignmentKind.ROOT_RADICAL
                and cell.vowel == "SUKUN" and exp.vowel == "SUKUN"
                and k + 1 < n
                and expected[k + 1].kind == AlignmentKind.ROOT_RADICAL
                and expected[k + 1].letter == exp.letter
                and not wazn.permits_geminate_root_idghaam()):
            return AlignmentAttempt(
                wazn=wazn, matched=False, trailing_kind="reject",
                reject_reason=f"spurious geminate-root match at slot {k} "
                              f"(wazn does not license idghaam)")

        if exp.kind == AlignmentKind.ROOT_RADICAL:
            aligns.append(WaznSlotAlignment(
                surface_segment=cell.raw, normalized_segment=cell.raw,
                surface_index=cell.index, root_slot=exp.root_slot,
                root_identity=exp.letter, alignment_kind=AlignmentKind.ROOT_RADICAL,
                operation_id=operation,
            ))
        else:
            slot_desc = (f"ziyadah:gemination_of_{exp.geminate_of}"
                         if exp.geminate_of else f"ziyadah:{cell.base}@{k}")
            ziyadah_slots.append(slot_desc)
            if exp.operation and exp.operation not in weak_ops:
                weak_ops.append(exp.operation)
            aligns.append(WaznSlotAlignment(
                surface_segment=cell.raw, normalized_segment=cell.raw,
                surface_index=cell.index, root_slot=None, root_identity=None,
                alignment_kind=AlignmentKind.ZIYADAH, operation_id=exp.operation,
            ))

    # ── الخلايا الزائدة (تصريف / تأنيث اسمي / رفض) ─────────────────────────
    trailing_kind, trailing_cells = _classify_trailing(trailing)
    infl: list = []
    if trailing_kind == "inflectional":
        for c in trailing_cells:
            infl.append(WaznSlotAlignment(
                surface_segment=c.raw, normalized_segment=c.raw,
                surface_index=c.index, root_slot=None, root_identity=None,
                alignment_kind=AlignmentKind.INFLECTIONAL,
                operation_id="op:inflection:taa_taanith_sakina",
            ))
    elif trailing_kind == "reject":
        return AlignmentAttempt(wazn=wazn, matched=False, trailing_kind="reject",
                                reject_reason="unaccounted trailing letters")

    # كل خانات الجذر محاذاة؟
    root_slots_complete = all(
        a.alignment_kind == AlignmentKind.ROOT_RADICAL
        for a in aligns if a.root_slot is not None
    ) and sum(1 for a in aligns if a.root_slot is not None) == wazn.root_arity

    return AlignmentAttempt(
        wazn=wazn,
        matched=True,
        trailing_kind=trailing_kind,
        alignments=tuple(aligns),
        inflectional_cells=tuple(infl),
        ziyadah_slots=tuple(ziyadah_slots),
        weak_operations=tuple(weak_ops),
        deleted_root_slots=(),
        root_slots_complete=root_slots_complete,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 4.  تحليل بنيوي احتياطي عند عدم وجود مطابقة (DEFER أم BLOCK؟)
# ══════════════════════════════════════════════════════════════════════════════

def is_ordered_subsequence(root: tuple, cells: list) -> bool:
    """هل يظهر الجذر تسلسلًا مرتّبًا (subsequence) في حروف السطح؟ مع تكافؤ الهمزة."""
    it = iter(cells)
    for r in root:
        found = False
        for c in it:
            if wk.letters_match(r, c.base):
                found = True
                break
        if not found:
            return False
    return True


def residual_letters_are_augment(root: tuple, cells: list) -> bool:
    """هل كل الحروف الزائدة على الجذر من حروف الزيادة (أو تاء مربوطة)؟

    يُستخدم للتمييز: DEFER (زيادة محتملة غير مرخّصة) مقابل BLOCK (بنية مستحيلة).
    """
    # أزل حروف الجذر بالترتيب، ثم افحص الباقي.
    remaining = list(cells)
    for r in root:
        for idx, c in enumerate(remaining):
            if wk.letters_match(r, c.base):
                del remaining[idx]
                break
    for c in remaining:
        if not (wk.is_ziyadah_letter(c.base) or wk.is_taa_marbuta(c.base)):
            return False
    return True
