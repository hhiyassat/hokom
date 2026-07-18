#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p4_wazn/hypothesis.py — WaznHypothesis P4A-α (فرضية الوزن)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

يبني فرضية وزن لمضيف DEFER عبر كشف الزيادة الداخلية:
  - Pattern A: مَ/مُ بادئة بسيطة (MIM_ZIYADAH) → مَفْعَل / مَفْعُول
  - Pattern B: اسْتَ بادئة (ALIF_WASL + SIN + TA) → يَسْتَفْعِل
  - Pattern C: مُفْتَعِل (MIM_ZIYADAH + IFTIEAL_TA) — ت زيادة افتعال عند موضع 1 من القاعدة

القيود:
  - لا فرضية لـ ACCEPT أو BLOCK (رتابة صارمة).
  - لا استيراد من hr2s.
  - لا مسارات مطلقة.
  - proposed_root_after لا يحتوي ا/ى/أ/إ/ؤ/ئ/آ كهويات جذرية.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pipeline.p1_atomic_structure.normalizer import normalize_hamza, normalize_shadda


# ══════════════════════════════════════════════════════════════════════════════
# 1.  الثوابت
# ══════════════════════════════════════════════════════════════════════════════

# رمز التحفظ الدال على وجود زيادة داخلية غير محلولة
_ZIYADAH_RESIDUAL = 'defer:root_refinement:internal_ziyadah_not_resolved'

# حروف المد (ليست جذرية)
_LONG_VOWEL_LETTERS = frozenset({'و', 'ا', 'ي'})

# الهويات الجذرية الممنوعة
_PROHIBITED = frozenset({"ا", "ى", "أ", "إ", "ؤ", "ئ", "آ", "?", ""})

# العلامات الصوتية التي تُحذف عند استخراج الحروف الأساسية
_DIACRITICS = frozenset('ًٌٍَُِّْٰٕٓٔ')

# بادئات الميم المعروفة (مَ / مُ) — بعد التطبيع تكون بصيغة حرف + حركة
_MIM = 'م'
_FATHA = 'َ'
_DAMMA = 'ُ'

# بادئة اسْتَ: بعد التطبيع hamza+fatha+س+sukun+ت+fatha
# نكتشفها بالبحث عن نمط الحروف الأساسية
_ISTA_CONSONANTS = ('ء', 'س', 'ت')  # همزة الوصل + سين + تاء


# ══════════════════════════════════════════════════════════════════════════════
# 2.  نماذج البيانات
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class WaznHypothesis:
    """فرضية وزن — مقترح، لم يُرخَّص بعد."""
    refined_host: str                             # المضيف بعد التنقية
    proposed_wazn: str                            # 'مَفْعَلَة' | 'فَعَّلَ' | ...
    ziyadah_detected: tuple                       # ('MIM_ZIYADAH',) | ('ALIF_WASL','SIN','TA')
    proposed_root_after: Optional[tuple]          # الجذر بعد حذف الزيادة أو None
    confidence: str                               # 'HIGH' | 'MEDIUM' | 'LOW'
    evidence_ids: tuple
    residual_codes: tuple
    # محاذاة صريحة — تُملأ بكاشفات الأنماط
    radical_alignment: tuple = ()                 # tuple[(letter, role), ...] — دور كل حرف
    removed_elements: tuple = ()                  # tuple[(letter, reason), ...] — الزيادة المُحذوفة

    def to_proposed_root_resolution(self) -> 'ProposedRootResolution':
        """أنتج ProposedRootResolution صريحًا من هذه الفرضية."""
        return ProposedRootResolution(
            source='WaznHypothesis',
            proposed_root=self.proposed_root_after,
            wazn_pattern=self.proposed_wazn,
            ziyadah_removed=tuple(self.removed_elements),
            radical_alignment=self.radical_alignment,
            removed_elements=self.removed_elements,
            confidence=self.confidence,
            evidence_ids=self.evidence_ids,
            residual_codes=self.residual_codes,
        )


@dataclass(frozen=True)
class ProposedRootResolution:
    """الجذر المستخرج من WaznHypothesis — يُمرَّر لـ Root Re-Licensing.

    radical_alignment: خريطة صريحة لكل حرف في المضيف → دوره
        مثال لـ مُفْتَرِسَ:
          [('م','MIM_ZIYADAH'), ('ف','FA'), ('ت','IFTIEAL_TA'), ('ر','AYN'), ('س','LAM')]
    removed_elements: الحروف المحذوفة بالترتيب مع سبب الحذف
        مثال: [('م','MIM_ZIYADAH'), ('ت','IFTIEAL_TA')]
    """
    source: str                                   # 'WaznHypothesis'
    proposed_root: Optional[tuple]
    wazn_pattern: str
    ziyadah_removed: tuple
    radical_alignment: tuple                      # tuple[tuple[str, str], ...] — (letter, role)
    removed_elements: tuple                       # tuple[tuple[str, str], ...] — (letter, reason)
    confidence: str
    evidence_ids: tuple
    residual_codes: tuple


# ══════════════════════════════════════════════════════════════════════════════
# 3.  دوال مساعدة
# ══════════════════════════════════════════════════════════════════════════════

def _extract_base_consonants(text: str) -> tuple:
    """استخرج الحروف الأساسية فقط، متجاهلًا جميع الحركات والمسافات."""
    return tuple(ch for ch in text if ch not in _DIACRITICS and ch != ' ')


def _extract_root_from_mim_base(base_consonants: tuple) -> Optional[tuple]:
    """بعد حذف الميم: استخرج الجذر من الحروف الأساسية.

    يحذف حروف المد (و/ا/ي) باعتبارها زيادة، ويتحقق من عدم وجود هويات ممنوعة.
    """
    stripped = tuple(c for c in base_consonants if c not in _LONG_VOWEL_LETTERS)
    if len(stripped) == 3:
        if not any(c in _PROHIBITED for c in stripped):
            return stripped
    return None


def _normalize_host(host: str) -> str:
    """طبّع المضيف: توحيد الهمزة ثم توسيع الشدة."""
    return normalize_shadda(normalize_hamza(host))


def _has_ziyadah_signal(residual_codes: tuple, refined_host_consonants: tuple) -> bool:
    """هل توجد إشارة زيادة داخلية قابلة للتحليل؟"""
    # إشارة صريحة عبر رمز التحفظ
    if _ZIYADAH_RESIDUAL in residual_codes:
        return True
    # أو البادئة ذاتها تدل عليها (مَ/مُ أو اسْتَ)
    if not refined_host_consonants:
        return False
    first = refined_host_consonants[0]
    if first == _MIM:
        return True
    # كشف اسْتَ: الحروف الأولى (ء،س،ت) أو (س،ت) بعد يَ
    consonants = refined_host_consonants
    # يَ + اسْتَ
    if len(consonants) >= 4 and consonants[0] in ('ي', 'ت', 'ن', 'ء'):
        if consonants[1] == 'س' and consonants[2] == 'ت':
            return True
    # اسْتَ مباشرة
    if len(consonants) >= 3 and consonants[0] == 'ء' and consonants[1] == 'س' and consonants[2] == 'ت':
        return True
    if len(consonants) >= 3 and consonants[0] == 'س' and consonants[1] == 'ت':
        return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
# 4.  كاشفات الأنماط
# ══════════════════════════════════════════════════════════════════════════════

def _detect_muftal(normalized: str, all_consonants: tuple) -> Optional[WaznHypothesis]:
    """Pattern C: مُفْتَعِل — ميم زائدة + تاء افتعال داخلية.

    البنية: مُ + FA + ت(زيادة) + AYN + LAM
    مثال: مُفْتَرِسَ → (م،ف،ت،ر،س) → remove م وت → (ف،ر،س) = FA،AYN،LAM
    """
    if not normalized or all_consonants[0] != _MIM:
        return None
    if len(normalized) < 2 or normalized[1] not in (_FATHA, _DAMMA):
        return None

    base = all_consonants[1:]   # بعد الميم
    # يجب أن يكون 4 حروف أساسية: FA + ت + AYN + LAM
    if len(base) != 4:
        return None
    # الحرف عند موضع 1 (بعد FA) يجب أن يكون ت
    if base[1] != 'ت':
        return None

    fa, _, ayn, lam = base[0], base[1], base[2], base[3]
    proposed_root = (fa, ayn, lam)

    # تحقق: لا هويات ممنوعة
    if any(c in _PROHIBITED for c in proposed_root):
        return None
    # لا حروف مد كهوية جذرية (AYN/LAM ليست واو/ياء/ألف)
    if any(c in _LONG_VOWEL_LETTERS for c in proposed_root):
        return None

    alignment = (
        (_MIM, 'MIM_ZIYADAH'),
        (fa,   'FA'),
        ('ت',  'IFTIEAL_TA'),
        (ayn,  'AYN'),
        (lam,  'LAM'),
    )
    removed = ((_MIM, 'MIM_ZIYADAH'), ('ت', 'IFTIEAL_TA'))

    return WaznHypothesis(
        refined_host=normalized,
        proposed_wazn='مُفْتَعِل',
        ziyadah_detected=('MIM_ZIYADAH', 'IFTIEAL_TA'),
        proposed_root_after=proposed_root,
        confidence='HIGH',
        evidence_ids=('ev:hypothesis:muftal_pattern',),
        residual_codes=(),
        radical_alignment=tuple(alignment),
        removed_elements=tuple(removed),
    )


def _detect_mim_ziyadah(normalized: str, all_consonants: tuple) -> Optional[WaznHypothesis]:
    """Pattern A: مَ/مُ بادئة صرفية بسيطة (بدون تاء افتعال داخلية).

    يُجرَّب بعد Pattern C (مُفْتَعِل) حتى لا يُخطئ التصنيف.
    """
    if not normalized or all_consonants[0] != _MIM:
        return None

    # تحقق أن الميم متبوعة بحركة مناسبة (مَ / مُ)
    if len(normalized) < 2 or normalized[1] not in (_FATHA, _DAMMA):
        return None

    # base = ما بعد الميم
    base_consonants = all_consonants[1:]

    if len(base_consonants) < 2:
        return None

    # استخرج الجذر بحذف حروف المد
    proposed_root = _extract_root_from_mim_base(base_consonants)

    # تحديد الوزن المقترح والثقة
    clean_count = len(tuple(c for c in base_consonants if c not in _LONG_VOWEL_LETTERS))

    if clean_count == 3 and proposed_root is not None:
        confidence = 'HIGH'
    elif proposed_root is not None:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    # اختر وزنًا وصفيًا
    if normalized[1] == _FATHA:
        wazn_pattern = 'مَفْعَلَة'
    else:
        wazn_pattern = 'مُفْعَلَة'

    # بناء خريطة المحاذاة
    _ROOT_SLOTS = ('FA', 'AYN', 'LAM', 'LAM2')
    alignment_list = [(_MIM, 'MIM_ZIYADAH')]
    root_so_far = proposed_root or ()
    slot_idx = 0
    for c in base_consonants:
        if c in _LONG_VOWEL_LETTERS:
            alignment_list.append((c, 'PATTERN_LONG_VOWEL'))
        elif slot_idx < len(root_so_far):
            alignment_list.append((c, _ROOT_SLOTS[slot_idx]))
            slot_idx += 1
        else:
            alignment_list.append((c, 'UNRESOLVED'))

    removed = [(_MIM, 'MIM_ZIYADAH')]
    for c in base_consonants:
        if c in _LONG_VOWEL_LETTERS:
            removed.append((c, 'PATTERN_LONG_VOWEL'))

    return WaznHypothesis(
        refined_host=normalized,
        proposed_wazn=wazn_pattern,
        ziyadah_detected=('MIM_ZIYADAH',),
        proposed_root_after=proposed_root,
        confidence=confidence,
        evidence_ids=('ev:hypothesis:mim_ziyadah_prefix',),
        residual_codes=() if proposed_root is not None else ('residual:mim:root_extraction_failed',),
        radical_alignment=tuple(alignment_list),
        removed_elements=tuple(removed),
    )


def _detect_ista_prefix(normalized: str, all_consonants: tuple) -> Optional[WaznHypothesis]:
    """Pattern B: اسْتَ / يَسْتَ بادئة — عائلة يَسْتَفْعِل."""
    if len(all_consonants) < 4:
        return None

    # يَسْتَ: يَ + اسْتَ = (ي، ء، س، ت) أو (ي، س، ت) حسب التطبيع
    # بعد normalize_hamza: همزة الوصل تبقى ا، وبعد normalize_shadda لا تتغير
    # نبحث عن (س، ت) في موقع 1-2 أو 2-3
    offset = 0
    first = all_consonants[0]

    # إذا بدأت بحرف مضارعة (ي/ت/ن/ء)
    if first in ('ي', 'ت', 'ن', 'ء') and len(all_consonants) >= 4:
        if all_consonants[1] == 'س' and all_consonants[2] == 'ت':
            offset = 3  # يَ + اسْتَ = حذف يَ + اسْتَ (3 حروف بعد يَ)
        elif (all_consonants[1] in ('ء', 'ا') and
              all_consonants[2] == 'س' and all_consonants[3] == 'ت'):
            offset = 4
    # اسْتَ مباشرة بهمزة وصل
    elif first in ('ء', 'ا') and len(all_consonants) >= 3:
        if all_consonants[1] == 'س' and all_consonants[2] == 'ت':
            offset = 3
    # سين وتاء مباشرة (بدون همزة)
    elif first == 'س' and len(all_consonants) >= 2 and all_consonants[1] == 'ت':
        offset = 2

    if offset == 0:
        return None

    remaining = all_consonants[offset:]
    # أزل حروف المد
    root_consonants = tuple(c for c in remaining if c not in _LONG_VOWEL_LETTERS)

    if len(root_consonants) < 2:
        return None

    proposed_root: Optional[tuple] = None
    if len(root_consonants) == 3 and not any(c in _PROHIBITED for c in root_consonants):
        proposed_root = root_consonants
        confidence = 'HIGH'
    elif len(root_consonants) == 4 and not any(c in _PROHIBITED for c in root_consonants):
        proposed_root = root_consonants
        confidence = 'MEDIUM'
    else:
        confidence = 'MEDIUM'

    # ── بناء المحاذاة الصريحة ─────────────────────────────────────────────
    # أدوار حروف البادئة حسب الإزاحة والحرف الأول
    alignment_list = []
    removed = []

    _ista_roles: tuple
    if offset == 3:
        f = all_consonants[0]
        r0 = 'ALIF_WASL' if f in ('ء', 'ا') else 'MUDARIA_PREFIX'
        _ista_roles = (r0, 'SIN', 'TA')
    elif offset == 4:
        f = all_consonants[0]
        r0 = 'ALIF_WASL' if f in ('ء', 'ا') else 'MUDARIA_PREFIX'
        _ista_roles = (r0, 'ALIF_WASL', 'SIN', 'TA')
    else:  # offset == 2
        _ista_roles = ('SIN', 'TA')

    for i, role in enumerate(_ista_roles):
        letter = all_consonants[i]
        alignment_list.append((letter, role))
        removed.append((letter, role))

    # أدوار الحروف الجذرية بعد البادئة
    _ROOT_SLOTS = ('FA', 'AYN', 'LAM', 'LAM2')
    slot_idx = 0
    for c in remaining:
        if c in _LONG_VOWEL_LETTERS:
            alignment_list.append((c, 'AYN_LONG_VOWEL'))
        elif slot_idx < len(_ROOT_SLOTS):
            alignment_list.append((c, _ROOT_SLOTS[slot_idx]))
            slot_idx += 1
        else:
            alignment_list.append((c, 'UNRESOLVED'))

    return WaznHypothesis(
        refined_host=normalized,
        proposed_wazn='يَسْتَفْعِل',
        ziyadah_detected=('ALIF_WASL', 'SIN', 'TA'),
        proposed_root_after=proposed_root,
        confidence=confidence,
        evidence_ids=('ev:hypothesis:ista_prefix',),
        residual_codes=() if proposed_root is not None else ('residual:ista:root_extraction_failed',),
        radical_alignment=tuple(alignment_list),
        removed_elements=tuple(removed),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 5.  الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════════════════

def build_wazn_hypothesis(
    *,
    refined_host: str,
    root_candidate,
    removed_markers: tuple,
    residual_codes: tuple,
) -> Optional[WaznHypothesis]:
    """
    يبني فرضية وزن لمضيف DEFER.
    يعيد None إذا:
      - directive != 'DEFER'
      - لم تُكتشف زيادة داخلية قابلة للتحليل.
    لا يُنتج فرضية للـ ACCEPT أو BLOCK (رتابة صارمة).
    """
    directive = str(getattr(root_candidate, 'directive', '')).strip().upper()
    if directive != 'DEFER':
        return None

    # طبّع المضيف
    normalized = _normalize_host(refined_host)
    all_consonants = _extract_base_consonants(normalized)

    if not all_consonants:
        return None

    # تحقق من وجود إشارة زيادة
    if not _has_ziyadah_signal(residual_codes, all_consonants):
        return None

    # جرّب Pattern B أولًا (اسْتَ) لأن الميم قد تظهر في غير السياق الاشتقاقي
    # لكن اكشف الميم أولًا إذا كانت البادئة مَ/مُ
    first = all_consonants[0]

    if first == _MIM:
        # Pattern C أولًا (مُفْتَعِل) لأنها أكثر تحديدًا من Pattern A
        hyp = _detect_muftal(normalized, all_consonants)
        if hyp is not None:
            return hyp
        # Pattern A: مَفْعَل / مَفْعُول البسيط
        hyp = _detect_mim_ziyadah(normalized, all_consonants)
        if hyp is not None:
            return hyp

    # Pattern B: كشف اسْتَ (يَسْتَ)
    hyp = _detect_ista_prefix(normalized, all_consonants)
    if hyp is not None:
        return hyp

    return None
