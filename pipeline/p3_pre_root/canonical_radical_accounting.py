#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p3_pre_root/canonical_radical_accounting.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOKOM-PRE-ROOT-CANONICAL-RADICAL-ACCOUNTING-OWNERSHIP-01

يُميِّز بين:
  - الجذر الحقيقي (RADICAL)
  - الزيادات الاشتقاقية (DERIVATIONAL_EXTENSION: است، أـ، فاعل، ...)
  - البادئات الصرفية (INFLECTIONAL_PREFIX: يَ/تَ/نَ/أَ في المضارع)
  - اللواحق الصرفية (INFLECTIONAL_SUFFIX: وا، تُمْ، ون، ...)
  - التضعيف الصوتي (PHONOLOGICAL_DUPLICATION: الشدة = حرف واحد لا اثنان)
  - الحرف الضعيف السطحي (WEAK_RADICAL_SURFACE: عين الأجوف، لام الناقص)

المعمار:
  يعمل على segment_host (بعد تجزئة السوابق الأدوية) — لا على pre_root.host_surface
  الذي قد يحتوي على السابقة الأدوية في بعض مسارات الربط.

خطوات المعالجة:
  أ. تجريد اللاحقة الصرفية الفعلية (وا، تُمْ، ون، ...)
  ب. كشف صيغة مزيدة (Form II–X) على الجذع المُجرَّد
  ج. تجريد بادئة المضارع (يَ/تَ/نَ/أَ) للفعل الثلاثي المجرد
  د. التحليل الثلاثي على الجذع النهائي

القيود الصارمة:
  - لا تُجرِّد البادئة بناءً على الشكل الظاهري وحده (يلزم VERBAL_ROOT_PATH)
  - لا تُجرِّد البادئة إذا كان الحرف التالي حرف مد (و/ا/ي)
  - لا تُسقط الشدة
  - لا تُسقط حرف العلة بلا أثر في reason_codes
  - لا تقبل الجذر لإرضاء عدد الحروف
  - لا تُلغي BLOCK من PreRoot
  - لا استثناءات نصية خاصة بكلمات
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Any


# ══════════════════════════════════════════════════════════════════════════════
# 1. الثوابت
# ══════════════════════════════════════════════════════════════════════════════

# بادئات المضارع المعروفة (حرف + حركة) — مرتبة: الأطول أولاً
_MUDARIC_PREFIX_PAIRS: frozenset[str] = frozenset({
    'يَ', 'يُ', 'يِ',
    'تَ', 'تُ', 'تِ',
    'نَ', 'نُ', 'نِ',
    'أَ', 'أُ', 'أِ',
})

# حروف المد — لا تكون الحرف الأول في جذع المضارع (نَوْمِ ليس مضارعًا)
_LONG_VOWEL_LETTERS: frozenset[str] = frozenset('واي')

# حروف الجذر الضعيفة وهوياتها الممنوعة في الإسقاط
# يشمل: واو وياء (ضعيفتان) + ألف وألف مقصورة (سطح الأجوف/الناقص)
# RootProjection._PROHIBITED_ROOT_IDENTITIES تمنع {ا، ى، أ، إ، ؤ، ئ، آ} →
# أي جذر يحتوي هذه يُؤجَّل (لا يُقبل) حتى تُحدَّد هويته الحقيقية.
_WEAK_ROOT_LETTERS: frozenset[str] = frozenset({'و', 'ي', 'ا', 'ى', 'أ', 'إ', 'ؤ', 'ئ', 'آ'})

# حروف التشكيل (للعد الحرفي)
_DIACRITICS: frozenset[str] = frozenset('ًٌٍَُِّْٰٕٓٔ')

# الحروف العربية الأصلية (لعد الحروف لا الحركات)
_ARABIC_LETTERS: frozenset[str] = frozenset(
    'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
    'أإآءةى'
    'اٱ'
)

# اللواحق الصرفية الفعلية المعروفة — (نص اللاحقة، معرف القاعدة)
# مرتبة: الأطول أولاً لتجنب المطابقة الجزئية
_VERBAL_SUFFIXES: List[tuple] = sorted(
    [
        ('تُمُوا', 'INFLECTIONAL_SUFFIX_2PL_MASC_WAW'),    # ككتبتموا
        ('تُمْ',   'INFLECTIONAL_SUFFIX_2PL_MASC_SUKUUN'), # كتبتمْ
        ('تُمَا',  'INFLECTIONAL_SUFFIX_2DUAL_MASC'),      # كتبتما
        ('تِنَّ',  'INFLECTIONAL_SUFFIX_2PL_FEM'),          # كتبتنَّ
        ('تُنَّ',  'INFLECTIONAL_SUFFIX_2PL_FEM_ALT'),      # كتبتنَّ (بديل)
        ('تُم',   'INFLECTIONAL_SUFFIX_2PL_MASC_PLAIN'),   # كتبتُم (بلا سكون)
        ('وا',    'INFLECTIONAL_SUFFIX_WAW_JAMAA'),         # واو الجماعة: كتبوا / يكتبوا
    ],
    key=lambda x: -len(x[0]),
)

# الحد الأدنى لعدد الحروف في الجذع بعد تجريد اللاحقة
_MIN_CONSONANTS_AFTER_SUFFIX_STRIP: int = 2


# ══════════════════════════════════════════════════════════════════════════════
# 2. نوع الخانة
# ══════════════════════════════════════════════════════════════════════════════

class SlotClass(str, Enum):
    """تصنيف الخانة الصرفية."""
    RADICAL                  = "RADICAL"
    DERIVATIONAL_EXTENSION   = "DERIVATIONAL_EXTENSION"
    INFLECTIONAL_PREFIX      = "INFLECTIONAL_PREFIX"
    INFLECTIONAL_SUFFIX      = "INFLECTIONAL_SUFFIX"
    ORTHOGRAPHIC_ONLY        = "ORTHOGRAPHIC_ONLY"
    PHONOLOGICAL_DUPLICATION = "PHONOLOGICAL_DUPLICATION"
    WEAK_RADICAL_SURFACE     = "WEAK_RADICAL_SURFACE"
    UNKNOWN_RADICAL_SLOT     = "UNKNOWN_RADICAL_SLOT"


# ══════════════════════════════════════════════════════════════════════════════
# 3. نموذج المخرجات
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class CanonicalRadicalAccounting:
    """
    محاسبة الجذر الكنسي لكلمة عربية.

    الحقول الأساسية:
      directive             : 'ACCEPT' | 'DEFER' | 'BLOCK'
      candidate_radical_sequences: [[C1,C2,C3], ...] — تسلسلات الجذر المحتملة
      canonical_stem        : الجذع بعد تجريد البادئة والّلاحقة
      prefix_stripped       : البادئة الصرفية المُجرَّدة (أو None)
      suffix_stripped       : اللاحقة الصرفية المُجرَّدة (أو None)
      suffix_rule           : معرف قاعدة اللاحقة
      form_family           : عائلة الصيغة ('FORM_I'، 'FORM_II'، ...، 'FORM_X')
      augmented_detection   : DetectionResult من detector.py (أو None)
      evidence              : شواهد القرار
      conflicts             : التعارضات
      reason_codes          : رموز السبب أو التحفظ
      provenance            : مصدر القرار ('CRA:...')
    """
    input_surface:               str
    segment_host:                str
    morphology_surface:          str
    word_class:                  Optional[str]
    route:                       Optional[str]
    canonical_stem:              str
    prefix_stripped:             Optional[str]
    suffix_stripped:             Optional[str]
    suffix_rule:                 Optional[str]
    form_family:                 Optional[str]
    candidate_radical_sequences: List[List[str]]
    augmented_detection:         Optional[Any]
    evidence:                    List[str]
    conflicts:                   List[str]
    directive:                   str
    reason_codes:                List[str]
    provenance:                  str

    def to_dict(self) -> dict:
        aug = self.augmented_detection
        return {
            'input_surface':               self.input_surface,
            'segment_host':                self.segment_host,
            'morphology_surface':          self.morphology_surface,
            'canonical_stem':              self.canonical_stem,
            'prefix_stripped':             self.prefix_stripped,
            'suffix_stripped':             self.suffix_stripped,
            'suffix_rule':                 self.suffix_rule,
            'form_family':                 self.form_family,
            'candidate_radical_sequences': self.candidate_radical_sequences,
            'augmented_detection': (
                {'form_family': aug.form_family, 'root': list(aug.root)}
                if aug is not None else None
            ),
            'evidence':     self.evidence,
            'conflicts':    self.conflicts,
            'directive':    self.directive,
            'reason_codes': self.reason_codes,
            'provenance':   self.provenance,
        }


# ══════════════════════════════════════════════════════════════════════════════
# 4. دوال مساعدة داخلية
# ══════════════════════════════════════════════════════════════════════════════

def _count_consonants(text: str) -> int:
    """عدِّ حروف العربية (غير التشكيل) في النص."""
    return sum(1 for c in text if c in _ARABIC_LETTERS)


def _is_verbal_path(pre_root: Any) -> bool:
    """
    هل يمتلك pre_root مسارًا صرفيًا فعليًا؟

    يعتمد على morphology_path.value (لا على نص الكلمة).
    """
    mp = getattr(pre_root, 'morphology_path', None)
    if mp is None:
        return False
    mp_val = mp.value if hasattr(mp, 'value') else str(mp)
    return 'verbal' in mp_val.lower()


def _strip_verbal_suffix(
    host:       str,
    is_verbal:  bool,
) -> tuple[str, Optional[str], Optional[str]]:
    """
    جرِّد اللاحقة الصرفية الفعلية المعروفة من نهاية المضيف.

    RULE_INFLECTIONAL_SUFFIX:
      تُطبَّق فقط عند is_verbal=True وعندما يبقى بعد التجريد
      ما لا يقل عن حرفين عربيين.

    تُعيد: (الجذع_المُجرَّد، اللاحقة_أو_None، معرف_القاعدة_أو_None)
    """
    if not is_verbal:
        return host, None, None

    for suffix, rule_id in _VERBAL_SUFFIXES:
        if host.endswith(suffix):
            remainder = host[: -len(suffix)]
            if _count_consonants(remainder) >= _MIN_CONSONANTS_AFTER_SUFFIX_STRIP:
                return remainder, suffix, rule_id

    # معالجة خاصة: واو مفردة في النهاية
    # الحالة: segmenter جرَّد الضمير المتصل (هُ) فأبقى على واو الجماعة المفردة.
    # مثال: تَكْتُبُوهُ → segment_host = 'تَكْتُبُو'
    # القيد: لا تُجرَّد الواو إذا كانت على الأرجح جذرًا (ناقص FALAحو)
    #   → نُجرِّدها فقط إذا بقي بعدها ≥ 3 حروف عربية (يضمن وجود جذر ثلاثي)
    if (is_verbal
            and len(host) >= 4
            and host.endswith('و')
            and not host.endswith('وا')
            and _count_consonants(host[:-1]) >= _MIN_CONSONANTS_AFTER_SUFFIX_STRIP):
        return host[:-1], 'و', 'INFLECTIONAL_SUFFIX_WAW_JAMAA_BARE'

    return host, None, None


def _strip_imperfect_prefix(
    stem:       str,
    is_verbal:  bool,
) -> tuple[str, Optional[str]]:
    """
    RULE_IMPERFECT_PREFIX: جرِّد بادئة المضارع عند توفر الشواهد.

    الشروط (جميعها يجب أن تتحقق):
      1. المسار الصرفي فعلي (is_verbal=True)
      2. السطح يبدأ بزوج بادئة مضارع معروف (يَ/تَ/نَ/أَ + حركة)
      3. الحرف العربي التالي ليس حرف مد (و/ا/ي) — لأن نَوْمِ (اسم) يبدأ بـ نَوْ
      4. يبقى بعد التجريد حرفان عربيان على الأقل

    لا تُجرِّد بناءً على الشكل الظاهري وحده — يلزم is_verbal=True.

    تُعيد: (الجذع_بعد_التجريد، البادئة_أو_None)
    """
    if not is_verbal or len(stem) < 4:
        return stem, None

    prefix_candidate = stem[:2]
    if prefix_candidate not in _MUDARIC_PREFIX_PAIRS:
        return stem, None

    # الحرف الثالث: يجب أن يكون صامتًا (لا حرف مد)
    # نَوْمِ: نَ + و (مد) → False (ليس مضارعًا، بل اسم)
    # نَذْهَبُ: نَ + ذ (صامت) → True (مضارع)
    third_char = stem[2] if len(stem) > 2 else ''
    if third_char in _LONG_VOWEL_LETTERS:
        return stem, None

    remainder = stem[2:]
    if _count_consonants(remainder) < _MIN_CONSONANTS_AFTER_SUFFIX_STRIP:
        return stem, None

    return remainder, prefix_candidate


# ══════════════════════════════════════════════════════════════════════════════
# 5. نقطة الدخول الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def process_canonical_radical_accounting(
    input_surface:      str,
    segment_host:       Optional[str],
    morphology_surface: Optional[str],
    pre_root:           Optional[Any],
    word_class:         Optional[Any] = None,
    route:              Optional[str] = None,
) -> CanonicalRadicalAccounting:
    """
    أجرِ المحاسبة الكنسية للجذر.

    يستخدم segment_host مصدرًا مرجعيًا (لا pre_root.host_surface) لأن
    pre_root.host_surface قد يحتوي على السابقة الأدوية في مسارات ربط بعينها
    (مثال: وَاسْتَشْهِدُوا → pre_root يرى 'وَاسْتَشْهِدَ' الخاطئة بينما
    segment_host يعطي 'اسْتَشْهِدُوا' الصحيحة).

    Parameters
    ----------
    input_surface      : السطح الأصلي للكلمة (ثابت طوال الدورة).
    segment_host       : المضيف بعد تجزئة السوابق الأدوية (P0 segmenter).
    morphology_surface : السطح المُطبَّع (normalize(segment_host)).
    pre_root           : PreRootDecision — يُعطي morphology_path و root_path_directive.
    word_class         : WordClassResult أو None (قد لا يكون متاحًا بعد).
    route              : مسار التوجيه من attachment.host_route.

    Returns
    -------
    CanonicalRadicalAccounting — القرار الكنسي مع الشواهد الكاملة.
    """
    _host   = segment_host   or ''
    _msurf  = morphology_surface or ''
    _wc_str = str(word_class) if word_class is not None else None

    # ── بناء نتيجة موحَّدة ─────────────────────────────────────────────────────
    def _build(
        directive:                   str,
        reason_codes:                List[str],
        provenance:                  str,
        canonical_stem:              str             = _host,
        prefix_stripped:             Optional[str]   = None,
        suffix_stripped:             Optional[str]   = None,
        suffix_rule:                 Optional[str]   = None,
        form_family:                 Optional[str]   = None,
        candidate_radical_sequences: Optional[List]  = None,
        augmented_detection:         Optional[Any]   = None,
        evidence:                    Optional[List]  = None,
        conflicts:                   Optional[List]  = None,
    ) -> CanonicalRadicalAccounting:
        return CanonicalRadicalAccounting(
            input_surface               = input_surface,
            segment_host                = _host,
            morphology_surface          = _msurf,
            word_class                  = _wc_str,
            route                       = route,
            canonical_stem              = canonical_stem,
            prefix_stripped             = prefix_stripped,
            suffix_stripped             = suffix_stripped,
            suffix_rule                 = suffix_rule,
            form_family                 = form_family,
            candidate_radical_sequences = candidate_radical_sequences or [],
            augmented_detection         = augmented_detection,
            evidence                    = evidence or [],
            conflicts                   = conflicts or [],
            directive                   = directive,
            reason_codes                = reason_codes,
            provenance                  = provenance,
        )

    # ── حارس 1: لا مضيف أو لا قرار ما قبل الجذر ──────────────────────────────
    if not _host or pre_root is None:
        return _build(
            directive    = 'BLOCK',
            reason_codes = ['CRA_GUARD:NO_SEGMENT_HOST_OR_PRE_ROOT'],
            provenance   = 'CRA:GUARD_NO_INPUT',
        )

    # ── حارس 2: الحد المغلق (BLOCK) يُحفظ دائمًا — لا يُفتح أبدًا ────────────
    _prd = getattr(pre_root, 'root_path_directive', None)
    if _prd == 'BLOCK':
        return _build(
            directive    = 'BLOCK',
            reason_codes = ['CRA_PRESERVE_BLOCK:PRE_ROOT_BOUNDARY'],
            provenance   = 'CRA:GUARD_BLOCK_PRESERVED',
        )

    is_verbal = _is_verbal_path(pre_root)
    evidence:  List[str] = []
    conflicts: List[str] = []

    # ════════════════════════════════════════════════════════════════════════
    # المرحلة أ — RULE_INFLECTIONAL_SUFFIX (للمسار الفعلي)
    # جرِّد اللاحقة الصرفية الفعلية من segment_host عند is_verbal=True
    # ════════════════════════════════════════════════════════════════════════
    bare_stem, suffix_stripped, suffix_rule = _strip_verbal_suffix(_host, is_verbal)
    if suffix_stripped is not None:
        evidence.append(f'RULE_INFLECTIONAL_SUFFIX:{suffix_rule}')

    # ════════════════════════════════════════════════════════════════════════
    # المرحلة ب — RULE_DERIVATIONAL_FAMILY
    # كشف صيغة مزيدة (Form II–X) على الجذع المُجرَّد من اللاحقة.
    #
    # خطوتان:
    #   ب.1) على الجذع الحالي (بعد تجريد اللاحقة إن كان المسار فعليًا)
    #   ب.2) إذا لم تنجح ب.1 وكان segment_host يحتوي لاحقة وا/تُمْ:
    #         جرِّد اللاحقة بلا قيد المسار الفعلي واكشف ثانيةً.
    #         يُعالِج حالة: المسار AMBIGUOUS لكن السطح من صيغة مزيدة.
    #         مثال: وَاسْتَشْهِدُوا → segment_host=اسْتَشْهِدُوا → pre_root=DEFER/AMBIGUOUS
    #         لكن اسْتَشْهِدُ (بعد تجريد وا) → FORM_X → ACCEPT(ش،ه،د).
    # ════════════════════════════════════════════════════════════════════════
    try:
        from pipeline.p2_augmented.detector import detect_augmented as _detect
        detection = _detect(bare_stem)
    except Exception:
        detection = None

    # ب.2: إذا لم تُنجح المرحلة ب.1 وكانت اللاحقة لم تُجرَّد بعد (is_verbal=False)
    if detection is None and suffix_stripped is None and not is_verbal:
        _bare2, _suf2, _rule2 = _strip_verbal_suffix(_host, is_verbal=True)  # force strip
        if _suf2 is not None:
            try:
                detection = _detect(_bare2)
            except Exception:
                detection = None
            if detection is not None:
                bare_stem       = _bare2
                suffix_stripped = _suf2
                suffix_rule     = _rule2
                evidence.append(f'RULE_INFLECTIONAL_SUFFIX:{_rule2}:AUGMENTED_FALLBACK')

    if detection is not None:
        form_family = detection.form_family
        root_chars  = detection.root   # tuple(C1, C2, C3) — بلا تشكيل
        evidence.append(f'RULE_AUGMENTED_DETECTION:{form_family}')

        # RULE_WEAK_RADICAL: حرف علة في الجذر → DEFER
        has_weak = any(c in _WEAK_ROOT_LETTERS for c in root_chars)
        if has_weak:
            evidence.append('RULE_WEAK_RADICAL:DETECTED_IN_AUGMENTED_ROOT')
            return _build(
                directive           = 'DEFER',
                reason_codes        = ['WEAK_RADICAL_IN_AUGMENTED_ROOT:DEFER'],
                provenance          = 'CRA:AUGMENTED_WEAK_RADICAL',
                canonical_stem      = bare_stem,
                suffix_stripped     = suffix_stripped,
                suffix_rule         = suffix_rule,
                form_family         = form_family,
                augmented_detection = detection,
                evidence            = evidence,
                conflicts           = conflicts,
            )

        # جذر قوي في صيغة مزيدة → ACCEPT
        evidence.append('RULE_AUGMENTED_ROOT_RESOLVED:STRONG_ROOT')
        return _build(
            directive                   = 'ACCEPT',
            reason_codes                = ['AUGMENTED_ROOT_ACCEPTED'],
            provenance                  = 'CRA:AUGMENTED_STRONG',
            canonical_stem              = bare_stem,
            suffix_stripped             = suffix_stripped,
            suffix_rule                 = suffix_rule,
            form_family                 = form_family,
            candidate_radical_sequences = [list(root_chars)],
            augmented_detection         = detection,
            evidence                    = evidence,
            conflicts                   = conflicts,
        )

    # ════════════════════════════════════════════════════════════════════════
    # المرحلة ج — RULE_IMPERFECT_PREFIX
    # جرِّد بادئة المضارع للفعل الثلاثي المجرد
    # شرط: VERBAL_ROOT_PATH + بادئة معروفة + صامت بعدها (لا حرف مد)
    # ════════════════════════════════════════════════════════════════════════
    stem_after_prefix, prefix_stripped = _strip_imperfect_prefix(bare_stem, is_verbal)
    if prefix_stripped is not None:
        evidence.append(
            f'RULE_IMPERFECT_PREFIX:STRIPPED_{prefix_stripped!r}:VERBAL_PATH_EVIDENCE'
        )
    form_family_tentative: Optional[str] = (
        'FORM_I_IMPERFECT' if prefix_stripped is not None else None
    )

    # ════════════════════════════════════════════════════════════════════════
    # المرحلة د — التحليل الثلاثي على الجذع النهائي
    # ════════════════════════════════════════════════════════════════════════
    try:
        from pipeline.p3_candidate.root_rules import analyze_host_consonants as _analyze
        analysis_directive, canonical_root, residual_code, _root_profile = (
            _analyze(stem_after_prefix)
        )
    except Exception:
        analysis_directive = 'DEFER'
        canonical_root     = None
        residual_code      = 'CRA_TRILATERAL_ANALYSIS_EXCEPTION'
        _root_profile      = {}

    if analysis_directive == 'ACCEPT' and canonical_root is not None:
        evidence.append('RULE_TRILATERAL_ROOT_RESOLVED')
        return _build(
            directive                   = 'ACCEPT',
            reason_codes                = ['TRILATERAL_ROOT_ACCEPTED'],
            provenance                  = 'CRA:TRILATERAL',
            canonical_stem              = stem_after_prefix,
            prefix_stripped             = prefix_stripped,
            suffix_stripped             = suffix_stripped,
            suffix_rule                 = suffix_rule,
            form_family                 = form_family_tentative or 'FORM_I',
            candidate_radical_sequences = [list(canonical_root)],
            evidence                    = evidence,
            conflicts                   = conflicts,
        )

    # DEFER: فعل ضعيف أو مضغوط أو رباعي أو غير قياسي
    reason = residual_code or 'TRILATERAL_ANALYSIS_DEFER'
    return _build(
        directive       = 'DEFER',
        reason_codes    = [reason],
        provenance      = 'CRA:DEFER',
        canonical_stem  = stem_after_prefix,
        prefix_stripped = prefix_stripped,
        suffix_stripped = suffix_stripped,
        suffix_rule     = suffix_rule,
        form_family     = form_family_tentative,
        evidence        = evidence,
        conflicts       = conflicts,
    )
