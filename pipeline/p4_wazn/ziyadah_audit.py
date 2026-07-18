#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/ziyadah_audit.py — تدقيق الزيادة (Ziyadah Audit)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يدقّق: هل زيادات السطح — مقاسةً على وزن بعينه — مرخّصة؟

الزيادة لا تُقبل إلا إذا:
  1. موقعها موجود في تعريف الوزن (القالب).
  2. هويتها توافق الحرف المطلوب.
  3. لا تحل محل حرف جذري بلا عقد.
  4. لا تنتج ترتيبًا جذريًا مكسورًا.

النتائج:
  ACCEPT → كل الزيادات مرخّصة (السطح يطابق الوزن مطابقة نظيفة/تصريفية).
  DEFER  → يوجد أكثر من تفسير بنيوي ممكن (مثل التأنيث الاسمي غير المعقود).
  BLOCK  → توجد زيادة غير مرخّصة أو ترتيب مستحيل لهذا الوزن.

تنبيه: كون الحرف من حروف «سألتمونيها» لا يعني أنه زائد في كل موضع؛ الموقع
يحسمه القالب لا مجرد هوية الحرف.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .wazn_catalog import WaznDefinition
from .alignment import parse_cells, align_wazn, AlignmentAttempt


@dataclass(frozen=True)
class ZiyadahAuditResult:
    directive:      str            # 'ACCEPT' | 'DEFER' | 'BLOCK'
    wazn_id:        str
    ziyadah_slots:  tuple = ()
    weak_operations: tuple = ()
    notes:          tuple = ()
    reject_reason:  Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "directive":       self.directive,
            "wazn_id":         self.wazn_id,
            "ziyadah_slots":   list(self.ziyadah_slots),
            "weak_operations": list(self.weak_operations),
            "notes":           list(self.notes),
            "reject_reason":   self.reject_reason,
        }


def audit_ziyadah(
    normalized_host: str,
    canonical_root: tuple,
    wazn_definition: WaznDefinition,
) -> ZiyadahAuditResult:
    """دقّق زيادات المضيف على وزن بعينه.

    يعتمد على المحاذاة: القالب يحدّد المواقع المرخّصة للزيادة، فأي حرف زائد
    خارج تلك المواقع يكسر المطابقة ⇒ BLOCK لهذا الوزن.
    """
    cells = parse_cells(normalized_host)
    attempt: AlignmentAttempt = align_wazn(canonical_root, cells, wazn_definition)

    if attempt.matched:
        if attempt.trailing_kind in ("clean", "inflectional"):
            notes = ("all ziyadah licensed by wazn template",)
            if attempt.trailing_kind == "inflectional":
                notes = notes + ("trailing taa taanith sakina is inflectional, not ziyadah",)
            return ZiyadahAuditResult(
                directive="ACCEPT",
                wazn_id=wazn_definition.wazn_id,
                ziyadah_slots=attempt.ziyadah_slots,
                weak_operations=attempt.weak_operations,
                notes=notes,
            )
        # trailing_kind == 'nominal' → تأنيث اسمي يحتاج عقدًا مرخّصًا.
        return ZiyadahAuditResult(
            directive="DEFER",
            wazn_id=wazn_definition.wazn_id,
            ziyadah_slots=attempt.ziyadah_slots,
            weak_operations=attempt.weak_operations,
            notes=("nominal feminine taa marbuta requires a licensed nominal wazn",),
        )

    # لم يطابق: زيادة غير مرخّصة أو ترتيب/بنية مستحيلة لهذا الوزن.
    return ZiyadahAuditResult(
        directive="BLOCK",
        wazn_id=wazn_definition.wazn_id,
        reject_reason=attempt.reject_reason,
        notes=("host does not fit this wazn's licensed ziyadah positions",),
    )
