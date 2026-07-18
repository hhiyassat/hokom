#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_projection/attachment_projection.py — الموقع الوحيد لإسقاط الملحقات (R-9)
(كان: pipeline/pre_root/attachment_roles.py — Axis 4)
تصنيف أدوار اللواحق والسوابق
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يُميّز بين صنفين رئيسيين من اللواحق:
  1. التصريف الإسنادي (inflectional) — يُغيّر الزمن أو المطابقة
     مثال: واو الجماعة في (فَعَلُوا)، نون الرفع في (يَفْعَلُونَ)
  2. الضمائر المتصلة (pronominal clitics) — تُحيل إلى مرجع خارجي
     مثال: ـهُ في (ضَرَبَهُ)، ـهُمْ في (رَأَيْتُهُمْ)

القانون:
  - الضمير المتصل لا يُدمج في بنية الجذر
  - اللاحقة التصريفية تُعدّ جزءًا من الإعراب وليست جذرًا

التوافق الخلفي:
  INFLECTIONAL_SUBJECT_WAW_AL_JAMAA = AttachmentRole.INFLECTIONAL_SUBJECT_SUFFIX
  (mabniyat_attachment.py يستخدم 'ATTACHED_PRONOUN_WAW_AL_JAMAA' كسلسلة نصية؛
   هذا التعريف لا يُغيّر تلك السلسلة — فقط يُضيف مقابلًا في التصنوف الجديد)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ══════════════════════════════════════════════════════════════════════════════
# 1.  AttachmentRole — تصنوف أدوار الملحقات
# ══════════════════════════════════════════════════════════════════════════════

class AttachmentRole(str, Enum):
    """
    دور الملحق (سابقة أو لاحقة) في البنية الصرفية.

    الفئتان الرئيسيتان:
      السوابق  (prefixes)  — تأتي قبل الجذر/المضيف
      اللواحق  (suffixes)  — تأتي بعد الجذر/المضيف، وتنقسم:
        • تصريف إسنادي (inflectional)  — يُغيّر المطابقة/الزمن
        • ضمير متصل (pronominal)        — يُحيل إلى مرجع

    كلّ قيمة هي str للتوافق مع to_dict() وعمليات المقارنة النصية.
    """

    # ─── سوابق ───────────────────────────────────────────────────────────────
    CLITIC_PREFIX              = "clitic_prefix"
    """فَـ، وَـ، بِـ، لِـ، كَـ — حروف العطف والجر كسوابق."""

    DEFINITE_ARTICLE           = "definite_article"
    """أداة التعريف «الـ» — قمرية أو شمسية."""

    # ─── لواحق تصريفية (inflectional suffixes) ───────────────────────────────
    INFLECTIONAL_SUBJECT_SUFFIX  = "inflectional_subject_suffix"
    """واو الجماعة (فَعَلُوا)، نون المضارع (يَفْعَلُونَ)، ونون التثنية.
    تُغيّر المطابقة الإسنادية وليست ضميرًا مستقلًا."""

    INFLECTIONAL_TENSE_SUFFIX    = "inflectional_tense_suffix"
    """نون التوكيد الثقيلة والخفيفة، تاء التأنيث الساكنة في الماضي (فَعَلَتْ).
    تُغيّر الزمن أو تُوكّده دون تغيير المرجع."""

    # ─── ضمائر متصلة (pronominal clitics) ──────────────────────────────────
    OBJECT_PRONOUN_SUFFIX        = "object_pronoun_suffix"
    """ـهُ، ـهَا، ـهُمْ، ـهُنَّ، ـكَ، ـنِي، ـنَا كضمير مفعول به.
    مثال: فَقَدُوهُ → هُ = OBJECT_PRONOUN_SUFFIX."""

    POSSESSIVE_PRONOUN_SUFFIX    = "possessive_pronoun_suffix"
    """ـهُ، ـهَا، ـهُمْ، ـكَ في سياق الإضافة (مضاف إليه).
    مثال: كِتَابُهُ → هُ = POSSESSIVE_PRONOUN_SUFFIX."""

    PREPOSITIONAL_PRONOUN_SUFFIX = "prepositional_pronoun_suffix"
    """ضمير متصل بحرف جر.
    مثال: بِهِ، لَهُمْ — الضمير بعد الجار."""

    OPERATOR_COMPLEMENT_SUFFIX   = "operator_complement_suffix"
    """ضمير لاحق لمشغّل (حرف مشبّه بالفعل).
    مثال: أَنَّهُمْ → هُمْ = OPERATOR_COMPLEMENT_SUFFIX لـ أَنَّ."""

    # ─── احتياط ──────────────────────────────────────────────────────────────
    UNKNOWN_ATTACHMENT           = "unknown_attachment"
    """ملحق تعذّر تصنيفه في الفئات السابقة."""


# ══════════════════════════════════════════════════════════════════════════════
# 2.  Alias للتوافق الخلفي
# ══════════════════════════════════════════════════════════════════════════════

# mabniyat_attachment.py يستخدم 'ATTACHED_PRONOUN_WAW_AL_JAMAA' كسلسلة نصية.
# هذا التعريف يُضيف مقابلًا في التصنوف الجديد بلا تغيير على الكود القديم.
INFLECTIONAL_SUBJECT_WAW_AL_JAMAA: AttachmentRole = AttachmentRole.INFLECTIONAL_SUBJECT_SUFFIX


# ══════════════════════════════════════════════════════════════════════════════
# 3.  AttachmentProjection — تمثيل ملحق واحد مُصنَّف
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AttachmentProjection:
    """
    تمثيل ملحق واحد (سابقة أو لاحقة) بعد التصنيف.

    Attributes
    ----------
    surface    : السطح المُطابَق (مع حركات إن توفرت)
    role       : دور الملحق في التصنيف الصرفي
    span_start : موضع البداية في السطح الأصلي (بالمحرف، inclusive)
    span_end   : موضع النهاية (exclusive)
    notes      : ملاحظات اختيارية للتتبع والاختبار
    """
    surface:    str
    role:       AttachmentRole
    span_start: int
    span_end:   int
    notes:      str = ''

    def to_dict(self) -> dict:
        return {
            'surface':    self.surface,
            'role':       self.role.value,
            'span_start': self.span_start,
            'span_end':   self.span_end,
            'notes':      self.notes,
        }
