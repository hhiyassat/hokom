#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_augmented/detector.py — augmented form pattern detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

خوارزمية اكتشاف أنماط أفعال المزيد (Form II–X) واستخلاص الجذر الثلاثي.

المراحل:
  1. التحقق من Form V / Form VI (بادئة تَ + نمط داخلي)
  2. فصل بادئة المضارع (يَ/يُ/نَ/أَ/...)
  3. إعادة التحقق من Form V / Form VI بعد الفصل
  4. مطابقة الهيكل العظمي الكامل (Form II–X)
  5. استخلاص حروف الجذر الثلاثي
  6. تحديد مستوى الثقة
"""

from __future__ import annotations

import re
from typing import Optional

from pipeline.p2_augmented.skeleton import (
    extract_skeleton,
    strip_imperfect_prefix,
    clean_root_letter,
    ALIF,
    ALIF_HAMZA_ABOVE,
    ALIF_HAMZA_BELOW,
    ALIF_MADDA,
    ALIF_WASLA,
)
from pipeline.p2_augmented.pattern_tables import WEAK_ROOT_LETTERS

# ── حارس FA3IL: اسم الفاعل من الثلاثي المجرد (فَاعِل) ──────────────────────
# C1(fatha) + ا + C2(kasra) + C3  — الكسرة على C2 تُمَيِّزه عن فَاعَلَ (Form III فتحة)
# Unicode: حروف عربية U+0621–U+064A U+0671–U+06B7، فتحة U+064E، كسرة U+0650
_FA3IL_RE = re.compile(
    r'[ء-يٱ-ڷ]'   # C1
    r'َ'                           # فتحة على C1
    r'ا'                           # ا (ألف)
    r'[ء-يٱ-ڷ]'   # C2
    r'ِ'                           # كسرة على C2 ← التمييز الجوهري
)

# ── أشكال الألف المقبولة كزيادة في بداية الكلمة ──────────────────────────────
_ALIF_FORMS = frozenset({ALIF, ALIF_HAMZA_ABOVE, ALIF_HAMZA_BELOW, ALIF_MADDA, ALIF_WASLA, 'ٱ'})
# الهمزة فقط كبادئة Form IV (أَفْعَلَ)
_HAMZA_PREFIX = frozenset({ALIF_HAMZA_ABOVE, ALIF_HAMZA_BELOW, ALIF_MADDA})
# حروف الزيادة المحددة
_NUN   = 'ن'
_TA    = 'ت'
_SIN   = 'س'
_MIM   = 'م'
# بادئة تاء Form V/VI
_TA_PREFIX_FORMS = frozenset({'تَ', 'تُ', 'تِ'})


# ══════════════════════════════════════════════════════════════════════════════
# نوع النتيجة الداخلية
# ══════════════════════════════════════════════════════════════════════════════

class DetectionResult:
    """نتيجة اكتشاف نمط فعل مزيد."""

    __slots__ = ('form_family', 'root', 'imperfect_prefix', 'confidence_hint')

    def __init__(
        self,
        form_family:      str,
        root:             tuple,
        imperfect_prefix: Optional[str],
        confidence_hint:  str = 'HIGH',
    ) -> None:
        self.form_family      = form_family
        self.root             = root            # (C1, C2, C3) — strings without diacritics
        self.imperfect_prefix = imperfect_prefix
        self.confidence_hint  = confidence_hint  # HIGH | MEDIUM | LOW


# ══════════════════════════════════════════════════════════════════════════════
# المساعدات الداخلية
# ══════════════════════════════════════════════════════════════════════════════

# الهمزات المحمولة → همزة مفردة (ء U+0621)
# مُقيَّدة بـ RootProjection._PROHIBITED_ROOT_IDENTITIES
_HAMZA_TO_BARE: dict[str, str] = {
    'أ': 'ء',   # hamza above alif → bare hamza
    'إ': 'ء',   # hamza below alif → bare hamza
    'آ': 'ء',   # alif madda → bare hamza
    'ؤ': 'ء',   # hamza on waw → bare hamza
    'ئ': 'ء',   # hamza on ya → bare hamza
}


def _clean(c: str) -> str:
    """
    نظِّف حرف جذر: أزِل التشكيل وحوِّل الهمزات المحمولة إلى همزة مفردة.

    RootProjection._PROHIBITED_ROOT_IDENTITIES تمنع {أ، إ، ؤ، ئ، آ} —
    الجذر الصحيح يُخزِّن الهمزة كـ ء (U+0621) المفردة.
    """
    clean = clean_root_letter(c)
    return _HAMZA_TO_BARE.get(clean, clean)


def _root_confidence(root: tuple) -> str:
    """
    حدد مستوى الثقة بناءً على طبيعة حروف الجذر:
      HIGH   : لا حروف علة في الجذر
      MEDIUM : يحتوي الجذر على حرف علة (و/ي) قد يكون أصليًا
      LOW    : أكثر من حرف علة أو حروف مبهمة
    """
    weak = sum(1 for c in root if c in WEAK_ROOT_LETTERS)
    if weak == 0:
        return 'HIGH'
    if weak == 1:
        return 'MEDIUM'
    return 'LOW'


def _check_form_v_vi(
    stem: str,
    imp_prefix: Optional[str],
) -> Optional[DetectionResult]:
    """
    تحقق من Form V (تَفَعَّلَ) أو Form VI (تَفَاعَلَ).

    يُستدعى مرتين: مرة بالسطح الأصلي، ومرة بعد فصل البادئة.
    stem: السطح بعد فصل بادئة مضارع خارجية (أو السطح الأصلي).
    """
    # هل يبدأ الجذع بتاء مضبوطة؟
    ta_prefix_found = None
    for tp in ('تَ',):  # HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01: only FATHA-ta is Form V/VI augment
        if stem.startswith(tp):
            ta_prefix_found = tp
            break

    if ta_prefix_found is None:
        return None

    # الجزء الداخلي بعد التاء+حركتها (حرفان: تَ)
    inner = stem[len(ta_prefix_found):]
    inner_skel = extract_skeleton(inner)

    # Form V: الجزء الداخلي ≡ Form II (3 حروف، الموضع[1] به شدة)
    if len(inner_skel) == 3 and inner_skel[1][1]:
        root = tuple(_clean(inner_skel[i][0]) for i in range(3))
        conf = _root_confidence(root)
        return DetectionResult('FORM_V', root, imp_prefix, conf)

    # Form VI: الجزء الداخلي ≡ Form III (4 حروف، الموضع[1] = ا)
    if len(inner_skel) == 4 and inner_skel[1][0] == ALIF:
        root = (
            _clean(inner_skel[0][0]),
            _clean(inner_skel[2][0]),
            _clean(inner_skel[3][0]),
        )
        conf = _root_confidence(root)
        return DetectionResult('FORM_VI', root, imp_prefix, conf)

    return None


# حروف بادئة المضارع — تُستخدَم في الكشف عن Form VIII المدغم (يَتَّقِ)
_IMPERFECT_PREFIX_LETTERS: frozenset[str] = frozenset('يتنأ')


def _match_skeleton(
    skel: list[tuple[str, bool]],
    imp_prefix: Optional[str],
    had_ta_strip: bool = False,
    raw_stem: str = '',
) -> Optional[DetectionResult]:
    """
    طابق الهيكل العظمي الكامل ضد أنماط Form II–X.

    الأولوية (من الأكثر خصوصية إلى الأقل):
      Form X past/participle (n=6)
      Form VII/VIII/IX past (n=5), Form X imperfect (n=5)
      Form VIII participle (n=5, مُ-prefix)
      Form IX past (n=4, alif+3+shadda)
      Form IV / Form III / Form VIII imperfect / Form VII imperfect (n=4)
      Form II (n=3, shadda on pos[1])
    """
    n = len(skel)

    # ── n=6: Form X ماضٍ أو اسم فاعل مُسْتَفْعِل ───────────────────────────
    if n == 6:
        # Form X past: alif-sin-ta-C1-C2-C3
        if (skel[0][0] in _ALIF_FORMS
                and skel[1][0] == _SIN
                and skel[2][0] == _TA):
            root = tuple(_clean(skel[i][0]) for i in (3, 4, 5))
            conf = _root_confidence(root)
            return DetectionResult('FORM_X', root, imp_prefix, conf)
        # Form X active participle: مُسْتَفْعِل → م-س-ت-C1-C2-C3
        if (skel[0][0] == _MIM
                and skel[1][0] == _SIN
                and skel[2][0] == _TA):
            root = tuple(_clean(skel[i][0]) for i in (3, 4, 5))
            conf = _root_confidence(root)
            return DetectionResult('FORM_X', root, imp_prefix, conf)

    # ── n=5 ────────────────────────────────────────────────────────────────────
    if n == 5:
        # Form X imperfect (after stripping يَ): سْتَـ … → sin-ta-C1-C2-C3
        if skel[0][0] == _SIN and skel[1][0] == _TA:
            root = tuple(_clean(skel[i][0]) for i in (2, 3, 4))
            conf = _root_confidence(root)
            return DetectionResult('FORM_X', root, imp_prefix, conf)

        # Form VII past: alif-nun-C1-C2-C3
        if skel[0][0] in _ALIF_FORMS and skel[1][0] == _NUN:
            root = tuple(_clean(skel[i][0]) for i in (2, 3, 4))
            conf = _root_confidence(root)
            return DetectionResult('FORM_VII', root, imp_prefix, conf)

        # Form VIII past: alif-C1-ta-C2-C3  (pos[0]=alif, pos[2]=ت)
        # HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01:
        # Form VIII augment alif has KASRA (اِ). Form I imperative wasla has no kasra
        # or has DAMMA (فَاكْتُبُوهُ host 'اكتبو' → plain alif, not Form VIII).
        _KASRA_CHAR = 'ِ'
        if skel[0][0] in _ALIF_FORMS and skel[2][0] == _TA:
            _alif_kasra = (
                raw_stem
                and len(raw_stem) >= 2
                and raw_stem[1] == _KASRA_CHAR
            )
            if _alif_kasra:
                root = (
                    _clean(skel[1][0]),
                    _clean(skel[3][0]),
                    _clean(skel[4][0]),
                )
                conf = _root_confidence(root)
                return DetectionResult('FORM_VIII', root, imp_prefix, conf)

        # Form VIII active participle: مُفْتَعِل → م-C1-ت-C2-C3
        if skel[0][0] == _MIM and skel[2][0] == _TA:
            root = (
                _clean(skel[1][0]),
                _clean(skel[3][0]),
                _clean(skel[4][0]),
            )
            conf = _root_confidence(root)
            return DetectionResult('FORM_VIII', root, imp_prefix, conf)

    # ── n=4 ────────────────────────────────────────────────────────────────────
    if n == 4:
        # Form IX past: alif-C1-C2-(C3+shadda)
        if skel[0][0] in _ALIF_FORMS and skel[3][1]:
            root = tuple(_clean(skel[i][0]) for i in (1, 2, 3))
            conf = _root_confidence(root)
            return DetectionResult('FORM_IX', root, imp_prefix, conf)

        # Form IV past: hamza-C1-C2-C3  (pos[0] in {أ إ آ})
        if skel[0][0] in _HAMZA_PREFIX:
            root = tuple(_clean(skel[i][0]) for i in (1, 2, 3))
            conf = _root_confidence(root)
            return DetectionResult('FORM_IV', root, imp_prefix, conf)

        # Form III past: C1-alif-C2-C3  (pos[1]=ا)
        if skel[1][0] == ALIF:
            root = (
                _clean(skel[0][0]),
                _clean(skel[2][0]),
                _clean(skel[3][0]),
            )
            conf = _root_confidence(root)
            return DetectionResult('FORM_III', root, imp_prefix, conf)

        # Form VII imperfect (after stripping يَ): نْـ C1-C2-C3 → nun prefix
        if skel[0][0] == _NUN:
            root = tuple(_clean(skel[i][0]) for i in (1, 2, 3))
            conf = _root_confidence(root)
            return DetectionResult('FORM_VII', root, imp_prefix, conf)

        # Form VIII imperfect (after stripping يَ): C1-ta-C2-C3
        # pos[1]=ت AND pos[0] not alif/mim (to avoid confusion with past/participle)
        if (skel[1][0] == _TA
                and skel[0][0] not in _ALIF_FORMS
                and skel[0][0] not in {_MIM, _NUN}):
            root = (
                _clean(skel[0][0]),
                _clean(skel[2][0]),
                _clean(skel[3][0]),
            )
            conf = _root_confidence(root)
            return DetectionResult('FORM_VIII', root, imp_prefix, conf)

    # ── n=3: Form II / Form VIII assimilation ──────────────────────────────────
    if n == 3:
        # HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01
        # Form II past: C1-(C2+shadda)-C3 — pos[0] must NOT be alif or imperfect prefix.
        # Form VIII assimilation past:  alif + (C1+ta merged → shadda) + C2
        #   (e.g. اتَّقَى → pos[0]=ا, pos[1]=تّ, pos[2]=ق)
        # Form VIII assimilation imperfect: prefix + (C1+ta → shadda) + C2
        #   (e.g. يَتَّقِ → pos[0]=ي, pos[1]=تّ, pos[2]=ق)
        if skel[1][1]:  # position 1 has shadda
            if skel[0][0] in _ALIF_FORMS:
                # alif + shadda → Form VIII past assimilation (وَاتَّقُوا)
                root = tuple(_clean(skel[i][0]) for i in (0, 1, 2))
                conf = _root_confidence(root)
                return DetectionResult('FORM_VIII', root, imp_prefix, conf)
            elif skel[0][0] in _IMPERFECT_PREFIX_LETTERS:
                # imperfect prefix + shadda → Form VIII imperfect assimilation (يَتَّقِ)
                root = tuple(_clean(skel[i][0]) for i in (0, 1, 2))
                conf = _root_confidence(root)
                return DetectionResult('FORM_VIII', root, imp_prefix, conf)
            else:
                # regular Form II (كَرَّمَ, ذَكَّرَ)
                root = tuple(_clean(skel[i][0]) for i in (0, 1, 2))
                conf = _root_confidence(root)
                return DetectionResult('FORM_II', root, imp_prefix, conf)

    return None


# ══════════════════════════════════════════════════════════════════════════════
# الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def detect_augmented(refined_host: str) -> Optional[DetectionResult]:
    """
    اكتشف نمط فعل مزيد من سطح المضيف المنقَّح.

    خوارزمية الكشف (بالترتيب):
      1. تحقق من Form V/VI بالسطح الأصلي (لاصطياد الماضي: تَفَعَّلَ)
      2. طابِق الهيكل العظمي للسطح الأصلي (لاصطياد Form IV/III/VII/VIII/IX/X)
         مع حارس نمط الميم: مُفْتَعِل يبدأ بـ 'مُ' (ضمة) لا 'مَ' (فتحة)
      3. حاوِل فصل بادئة مضارع (يَ/يُ/نَ/أَ/تَ/...)
      4. تحقق من Form V/VI بعد الفصل (لاصطياد المضارع: يَتَفَعَّلُ → تَفَعَّلُ)
      5. طابِق الهيكل العظمي للجذع بعد الفصل (Form X/VII/VIII imperfect)

    ملاحظة: الخطوة 2 قبل الفصل ضرورية لـ Form IV (أَفْعَلَ)
    لأن الهمزة في بداية أَفْعَلَ تتداخل مع بادئة المضارع الأولى (أَكْتُبُ).

    تُعيد DetectionResult أو None.
    """
    if not refined_host or len(refined_host) < 3:
        return None

    # ── الخطوة 1: تحقق من Form V/VI بالسطح الأصلي ──────────────────────────
    result = _check_form_v_vi(refined_host, imp_prefix=None)
    if result is not None:
        return result

    # ── حارس FA3IL: اسم الفاعل C1(فتحة)ا C2(كسرة)C3 — فَاعِل ─────────────────
    # _match_skeleton يُصنِّف C1-ا-C2-C3 (n=4) كـ FORM_III لأنه يعتمد الهيكل
    # العظمي (بدون حركات). الكسرة على C2 تُثبت أنه فَاعِل (Form I active participle)
    # لا فَاعَلَ (Form III verb) التي تحمل فتحة على C2.
    # نُعيد DetectionResult خاصًا ('FA3IL_PARTICIPLE') ليسلك مسار HOKOM_AUGMENTED_ENGINE
    # مع خريطة وزن FA3IL الصحيحة بدل FA3ALA الخاطئة.
    if _FA3IL_RE.search(refined_host):
        fa3il_skel = extract_skeleton(refined_host)
        if len(fa3il_skel) >= 4 and fa3il_skel[1][0] == ALIF:
            root = (
                _clean(fa3il_skel[0][0]),  # C1
                _clean(fa3il_skel[2][0]),  # C2
                _clean(fa3il_skel[3][0]),  # C3
            )
            conf = _root_confidence(root)
            return DetectionResult('FA3IL_PARTICIPLE', root, None, conf)

    # ── الخطوة 2: مطابقة الهيكل العظمي للسطح الأصلي ────────────────────────
    # تُعالج Form IV (أَفْعَلَ) قبل أن يُجرَّد أَ كبادئة مضارع.
    # تُعالج أيضًا Form III/VII/VIII/IX/X الماضي.
    orig_skel = extract_skeleton(refined_host)
    result = _match_skeleton(orig_skel, imp_prefix=None, raw_stem=refined_host)
    if result is not None:
        # حارس نمط الميم: اسم الفاعل مُفْتَعِل (Form VIII) يبدأ بـ 'مُ' (ضمة)،
        # بينما مَفْعَل / مَكْتَبَ (اسم مكان) يبدأ بـ 'مَ' (فتحة).
        # كذلك مُسْتَفْعِل (Form X) يبدأ بـ 'مُسْتَ' لا 'مَسْتَ'.
        if (orig_skel[0][0] == _MIM
                and result.form_family in ('FORM_VIII', 'FORM_X')
                and not refined_host.startswith('مُ')):
            result = None   # false positive — مَفْعَل ليس Form VIII/X
        if result is not None:
            return result

    # ── الخطوة 3: فصل بادئة المضارع ─────────────────────────────────────────
    stem, imp_prefix = strip_imperfect_prefix(refined_host)

    if imp_prefix is None or stem == refined_host:
        # لا بادئة وُجدت ولم يُطابق الهيكل الكامل → ليس فعلاً مزيدًا
        return None

    # ── الخطوة 4: تحقق من Form V/VI بعد الفصل ──────────────────────────────
    result = _check_form_v_vi(stem, imp_prefix=imp_prefix)
    if result is not None:
        return result

    # ── الخطوة 5: مطابقة الهيكل العظمي للجذع بعد الفصل ─────────────────────
    stem_skel = extract_skeleton(stem)

    # ── إصلاح C: n=3 مع همزة مفردة في الموضع 0 — Form IV بانكماش الهمزتين ──
    # HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01
    # آمَنَ = أَأَمَنَ (Form IV) بعد التطبيع: ءَمَنَ (ء = U+0621).
    # الهيكل n=3 مع ء في الموضع 0 بلا شدة = Form IV بانكماش الهمزتين.
    # الفرق عن Form I (أَكَلَ → ء,ك,ل): السياق هنا بعد تجريد اللاحقة
    # وفشل الخطوة 2 (لا صيغة معروفة على الجذع الكامل) → Form IV.
    _BARE_HAMZA = 'ء'   # U+0621
    if (len(stem_skel) == 3
            and stem_skel[0][0] == _BARE_HAMZA
            and not stem_skel[1][1]           # no shadda at pos[1]
            and not stem_skel[2][1]):         # no shadda at pos[2]
        root = tuple(_clean(stem_skel[i][0]) for i in (0, 1, 2))
        conf = _root_confidence(root)
        return DetectionResult('FORM_IV', root, imp_prefix, conf)

    # ── إصلاح E: n=2 مع شدة على الموضع 1 + بادئة ضمة → Form IV مضعَّف ───────
    # HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01
    # يُمِلَّ → بعد تجريد يُ: stem='مِلَّ', هيكل n=2 = [م, ل(شدة)].
    # البادئة يُ (ضمة) + C1(كسرة) + C2(شدة) = Form IV مضعَّف.
    # الفرق عن Form I مضعَّف (يَرُدُّ → رُدُّ): C1 لها ضمة لا كسرة.
    _KASRA_CHAR = 'ِ'
    _DAMMA_CHAR = 'ُ'
    if (len(stem_skel) == 2
            and stem_skel[1][1]              # shadda at pos[1]
            and imp_prefix is not None
            and imp_prefix[-1] == _DAMMA_CHAR   # damma on prefix (يُ/تُ/نُ/أُ)
            and len(stem) >= 2
            and stem[1] == _KASRA_CHAR):     # kasra on C1 = Form IV active marker
        root = (_clean(stem_skel[0][0]),
                _clean(stem_skel[1][0]),
                _clean(stem_skel[1][0]))     # geminate: C2 = C3
        conf = _root_confidence(root)
        return DetectionResult('FORM_IV', root, imp_prefix, conf)

    result = _match_skeleton(stem_skel, imp_prefix=imp_prefix, raw_stem=stem)
    return result
