#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/pre_root/article_projection.py — فصل أداة التعريف «الـ» (Axis 1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يفصل أداة التعريف عن المضيف قبل إرسال المضيف إلى HR2S.

الحالتان المعالَجتان:
  1. قمرية (lunar):  الْأَطْفَالُ  → prefix='الْ'  (3 أحرف), host='أَطْفَالُ'
  2. شمسية (solar):  الشَّجَرَةِ   → prefix='ال'   (2 حرف), host='شَجَرَةِ'
                    اللام تندغم في الحرف الشمسي؛ الشدة محفوظة في المضيف

اكتشاف الحالة القمرية:
  يبدأ السطح بـ ا + ل + سكون (ْ)

اكتشاف الحالة الشمسية:
  يبدأ السطح بـ ا + ل + حرف من الحروف الشمسية الأربعة عشر

حالات خاصة لا تُعامَل كأداة تعريف:
  - «الله» و«اللهم»: تُعالَجهما طبقة المبني قبل الوصول هنا
  - كلمات تبدأ بـ «إ» أو «أ» (همزة قطع): لا تُشارك في نمط الـ

القانون:
  لا استثناءات كلمات.
  لا تغيير على الجذر أو بنية HR2S.
  الكشف يعتمد على نمط الأحرف الأول فقط.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pipeline.p2_projection.attachment_projection import AttachmentProjection, AttachmentRole


# ══════════════════════════════════════════════════════════════════════════════
# 1.  ثوابت
# ══════════════════════════════════════════════════════════════════════════════

_ALEF:   str = 'ا'   # U+0627 ARABIC LETTER ALEF
_LAM:    str = 'ل'   # U+0644 ARABIC LETTER LAM
_SUKUN:  str = 'ْ'   # U+0652 ARABIC SUKUN
_SHADDA: str = 'ّ'   # U+0651 ARABIC SHADDA

# الحروف الشمسية الأربعة عشر — يُدغم اللامُ في كل منها
# (الأبجدية الصحيحة دون حروف المد)
SOLAR_CONSONANTS: frozenset[str] = frozenset('تثدذرزسشصضطظلن')


# ══════════════════════════════════════════════════════════════════════════════
# 2.  نموذج النتيجة
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ArticleProjectionResult:
    """
    نتيجة فصل أداة التعريف.

    Attributes
    ----------
    has_article       : True إذا كُشفت أداة تعريف
    prefix_surface    : السطح المُستخرَج للأداة ('الْ' أو 'ال')، أو None
    host_surface      : السطح بعد الأداة (أو السطح كاملًا إن لم تُكشف)
    is_solar          : True إذا كانت الأداة شمسية
    prefix_projection : AttachmentProjection للأداة، أو None
    normalized_host   : المضيف للإرسال إلى HR2S (حاليًا = host_surface)
    evidence_id       : معرّف الشاهد (للتتبع)
    """
    has_article:       bool
    prefix_surface:    Optional[str]
    host_surface:      str
    is_solar:          bool
    prefix_projection: Optional[AttachmentProjection]
    normalized_host:   str
    evidence_id:       str

    def to_dict(self) -> dict:
        return {
            'has_article':       self.has_article,
            'prefix_surface':    self.prefix_surface,
            'host_surface':      self.host_surface,
            'is_solar':          self.is_solar,
            'prefix_projection': self.prefix_projection.to_dict()
                                  if self.prefix_projection else None,
            'normalized_host':   self.normalized_host,
            'evidence_id':       self.evidence_id,
        }


# ══════════════════════════════════════════════════════════════════════════════
# 3.  دوال الكشف الداخلية
# ══════════════════════════════════════════════════════════════════════════════

def _is_lunar_article(surface: str) -> bool:
    """
    هل يبدأ السطح بأداة تعريف قمرية؟
    النمط: الف + لام + سكون (ا ل ْ)
    """
    return (
        len(surface) >= 4        # الأداة 3 أحرف + حرف واحد على الأقل للمضيف
        and surface[0] == _ALEF
        and surface[1] == _LAM
        and surface[2] == _SUKUN
    )


def _is_solar_article(surface: str) -> bool:
    """
    هل يبدأ السطح بأداة تعريف شمسية؟
    النمط: الف + لام + حرف شمسي
    (الشدة على الحرف الشمسي اختيارية — تُكشف من المضيف)
    """
    return (
        len(surface) >= 3        # الأداة 2 حرف + حرف واحد على الأقل للمضيف
        and surface[0] == _ALEF
        and surface[1] == _LAM
        and surface[2] in SOLAR_CONSONANTS
    )


def _remove_assimilation_shadda(host: str) -> str:
    """
    أزِل شدة الإدغام من أول مقطع المضيف الشمسي.

    في العربية، عندما تسبق «ال» حرفًا شمسيًا، يندغم اللام في الحرف الشمسي
    فيظهر مشددًا: الشَّجَرَةِ ← ش + شدة من الإدغام.
    هذه الشدة لا تُمثِّل بنيةً صرفية في المضيف، فيُحذف قبل إرساله إلى HR2S.

    القاعدة: يُحذف أول ظهور للشدة (U+0651) داخل أول 4 أحرف من المضيف.
    أحرف أبعد من الحرف الرابع لا تُمسَّ (قد تكون شدودًا صرفيةً معجمية).

    مثال:
      شَّجَرَةِ  → شَجَرَةِ  (ش + شدة + فتحة → ش + فتحة)
      نَّاسُ    → نَاسُ    (ن + شدة → ن)
    """
    if not host or _SHADDA not in host[:4]:
        return host
    idx = host.index(_SHADDA)
    if idx < 4:
        return host[:idx] + host[idx + 1:]
    return host


# ══════════════════════════════════════════════════════════════════════════════
# 4.  project_article — الدالة العامة
# ══════════════════════════════════════════════════════════════════════════════

def project_article(surface: str) -> ArticleProjectionResult:
    """
    افصل أداة التعريف إن وُجدت.

    يعمل على السطح الأصلي (قبل التطبيع) للحفاظ على الحركات.
    يُعطي الأولوية لاكتشاف الحالة القمرية (السكون الصريح) قبل الشمسية.

    Parameters
    ----------
    surface : السطح الأصلي للكلمة (مع حركات كاملة إن توفرت)

    Returns
    -------
    ArticleProjectionResult
    """
    # ── حالة القمرية: الف + لام + سكون ──────────────────────────────────────
    if _is_lunar_article(surface):
        prefix  = surface[:3]       # 'الْ' (ا + ل + ْ)
        host    = surface[3:]
        proj    = AttachmentProjection(
            surface    = prefix,
            role       = AttachmentRole.DEFINITE_ARTICLE,
            span_start = 0,
            span_end   = 3,
            notes      = 'article:lunar:lam_sukun',
        )
        return ArticleProjectionResult(
            has_article       = True,
            prefix_surface    = prefix,
            host_surface      = host,
            is_solar          = False,
            prefix_projection = proj,
            normalized_host   = host,
            evidence_id       = 'article:lunar:lam_sukun_detected',
        )

    # ── حالة الشمسية: الف + لام + حرف شمسي ──────────────────────────────────
    if _is_solar_article(surface):
        prefix  = surface[:2]       # 'ال' (ا + ل)
        host    = surface[2:]       # يبدأ بالحرف الشمسي (+شدة اختيارية)
        # إعادة بناء الشكل الصرفي للمضيف: حذف شدة الإدغام من أول حرف شمسي.
        # مثال: شَّجَرَةِ → شَجَرَةِ (الشدة من الإدغام لا من الوزن الصرفي).
        normalized = _remove_assimilation_shadda(host)
        proj    = AttachmentProjection(
            surface    = prefix,
            role       = AttachmentRole.DEFINITE_ARTICLE,
            span_start = 0,
            span_end   = 2,
            notes      = (
                f'article:solar:assimilation_into_{surface[2]}'
                ':assimilation_shadda_reversed'
            ),
        )
        return ArticleProjectionResult(
            has_article       = True,
            prefix_surface    = prefix,
            host_surface      = normalized,   # الشكل الصرفي بدون شدة الإدغام
            is_solar          = True,
            prefix_projection = proj,
            normalized_host   = normalized,
            evidence_id       = 'article:solar:lam_assimilation_reversed',
        )

    # ── لا أداة تعريف ────────────────────────────────────────────────────────
    return ArticleProjectionResult(
        has_article       = False,
        prefix_surface    = None,
        host_surface      = surface,
        is_solar          = False,
        prefix_projection = None,
        normalized_host   = surface,
        evidence_id       = 'article:none',
    )
