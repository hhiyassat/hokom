#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mabni_layer.py — P5: Mabni / Operator Lookup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

القاعدة:
  Mabni(t) ⟺ Slots(t) ∈ S⁺  ∧  t ∈ MabniCatalog

قرارات الطبقة:
  MabniBoundary  — السطح صحيح مقطعيًا + موجود في الكتالوج → لا جذر ولا وزن
  MabniOpen      — السطح صحيح مقطعيًا + غير موجود في الكتالوج → مسار HR2S
  MabniBlocked   — السطح مرفوض مقطعيًا → يوقف المعالجة

نموذج التمثيل الرباعي:
  input_surface      — الرمز كما وصل من المُدخَل (ثابت، لا يُعدَّل)
  canonical_surface  — الهوية المعجمية/الكنونية (= input_surface حاليًا)
  normalized_surface — الشكل الداخلي للتحليل (توسيع شدة + توحيد همزة)
  matched_surface    — surface_vocalized من مدخل الكتالوج المطابق

الهوية المعجمية لـ P5 (لا نحو):
  operator_id    — معرِّف مستقر سطحي (INNA | LAM | KAY | …)
  lexical_family — أسرة معجمية حقيقية أو هوية ذاتية (INNA_SERIES | LAM | …)

Relation Contract:
  contract_id    = operator_id
  contract_state = 'OPEN' دائمًا
"""

from dataclasses import dataclass, field
from pipeline.p5_lexical.mabni_inventory      import MabniEntry, get_inventory, _strip_diacritics
from pipeline.p5_lexical.operator_projection  import get_profile, OperatorProfile
from pipeline.contracts.relation_contract     import RelationContract, make_contract


# ══════════════════════════════════════════════════════════════════════════════
# هياكل القرار
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class MabniBoundary:
    """
    السطح مرخَّص مقطعيًا + موجود في الكتالوج → حدّ مبني.

    P5 يُثبت الوجود الكتالوجي ويُعلن الهوية المعجمية وعقد العلاقة.
    العقد مفتوح — الطبقات اللاحقة هي التي تستوفيه.

    التمثيل الرباعي:
      input_surface      — الرمز كما أُدخل (ثابت)
      canonical_surface  — الهوية المعجمية (= input_surface حاليًا)
      normalized_surface — الشكل الداخلي للتحليل (ءِنْنَ ، ءَنْنَ …)
      matched_surface    — surface_vocalized من الكتالوج المطابق (إِنَّ ، وَ …)

    الهوية المعجمية:
      operator_id    — INNA | LAM | KAY | WA | LA | MIN | …
      lexical_family — INNA_SERIES | LAM | KAY | … (هوية ذاتية للمنفردات)

    function_candidates : داخلي فقط — لا تُعرض في P5
    relation_contract   : contract_id = operator_id ، contract_state = OPEN
    """
    input_surface:        str                # الرمز كما وصل
    canonical_surface:    str                # الهوية المعجمية
    normalized_surface:   str                # الشكل الداخلي (shadda مُوسَّعة)
    matched_surface:      str                # surface_vocalized من الكتالوج
    operator_id:          str                # معرِّف معجمي مستقر
    lexical_family:       str                # أسرة معجمية حقيقية أو ذاتية
    slots:                list[dict]
    slot_patterns:        list[str]
    entries:              list[MabniEntry]   # كل التطابقات — داخلي فقط
    function_candidates:  list[str]          # أغراض المداخل — داخلي، لا يُعرض في P5
    lexical_class:        str                # 'Closed Function Word' | 'Bound Nominal'
    relation_contract:    RelationContract   # عقد العلاقة المفتوحة
    structural_verdict:   str  = 'ACCEPT'   # حكم P4 الهيكلي (ACCEPT | DEFER) — ثابت من P4
    inventory_status:     str  = 'FOUND'    # وُجد في الكتالوج
    opens_relation:       bool = True        # الأداة تفتح علاقة تركيبية
    blocks_root_path:     bool = True
    verdict:              str  = 'OPERATOR_BOUNDARY'

    @property
    def source(self) -> str:
        seen: list[str] = []
        for e in self.entries:
            if e.source not in seen:
                seen.append(e.source)
        return ', '.join(seen)

    @property
    def group_numbers(self) -> list[int]:
        return list(dict.fromkeys(e.group_number for e in self.entries))


@dataclass
class MabniOpen:
    """
    السطح مرخَّص مقطعيًا + غير موجود في كتالوج المبنيات.
    Boundary = OPEN → يُمرَّر إلى HR2S (Root → Wazn → Stem).
    """
    input_surface:      str
    canonical_surface:  str
    normalized_surface: str
    slots:              list[dict]
    slot_patterns:      list[str]
    structural_verdict: str = 'ACCEPT'   # حكم P4 الهيكلي (ACCEPT | DEFER)
    verdict:            str = 'OPEN'
    note:               str = 'valid slots — not mabni → HR2S path'


@dataclass
class MabniBlocked:
    """بنية مقطعية فاسدة → لا يُكمل."""
    input_surface:      str
    normalized_surface: str
    reason:             str
    violations:         list[str] = field(default_factory=list)
    verdict:            str = 'BLOCK'


# ══════════════════════════════════════════════════════════════════════════════
# مساعدات داخلية
# ══════════════════════════════════════════════════════════════════════════════

# مجموعات الأفعال: تُميَّز عن حروف المعاني المغلقة
_VERBAL_GROUPS:   frozenset[int] = frozenset({10, 11, 12})
_COGNITION_GROUP: int            = 13
_NUMERICAL_GROUP: int            = 8   # التمييز والعدد


def _lexical_class(entries: list[MabniEntry]) -> str:
    """
    يُميِّز بين خمس فئات معجمية بناءً على رقم المجموعة والشكل السطحي:

      Group 1–7, 9  → 'Closed Function Word'   (حروف المعاني والأدوات المغلقة)
      Group 8        → 'Numerical Operator'     (أدوات العدد والتمييز)
      Group 10–12    → 'Verbal Operator'        (أفعال ناقصة / مقاربة / مدح وذم)
                       إلا المركّبات (مَا زَالَ …) → 'Phrase Operator'
      Group 13       → 'Cognition Verb'         (أفعال القلوب)

    الأساس المعماري (القرار الحاكم):
      الفئة المعجمية (lexical_class) مستقلة تمامًا عن الوظيفة العاملية.
      جميع الفئات الخمس تُنتج OPERATOR_BOUNDARY وتفتح عقد علاقة مفتوح.
      is_operator=True في الكتالوج لا يكفي وحده للتمييز —
      الأفعال كـ كَانَ وعَسَى ونِعْمَ لها is_operator=True أيضًا
      لكنها ليست من فئة الحروف المعجمية المغلقة.
    """
    groups = {e.group_number for e in entries}

    # أفعال القلوب (المجموعة 13) — الفحص قبل الأفعال الأخرى
    if _COGNITION_GROUP in groups:
        return 'Cognition Verb'

    # المشغّلات العبارية (مَا زَالَ / مَا بَرِحَ / مَا دَامَ …)
    # تُعرَّف بوجود مسافة في السطح المشكول، مع انتمائها للمجموعات الفعلية
    if (groups and groups.issubset(_VERBAL_GROUPS)
            and any(' ' in e.surface_vocalized for e in entries)):
        return 'Phrase Operator'

    # المشغّلات الفعلية البسيطة (مجموعات 10–12 بلا مسافة)
    if groups and groups.issubset(_VERBAL_GROUPS):
        return 'Verbal Operator'

    # أدوات العدد والتمييز (المجموعة 8)
    # ملاحظة: نستخدم any() لا issubset() لدعم الترخيص المزدوج (مثل كَذَا)
    # حيث قد تحمل إدخالات من مجموعتين (8: عامل كمي، و0: كناية عامة غير عامل)
    if any(e.group_number == _NUMERICAL_GROUP and e.is_operator for e in entries):
        return 'Numerical Operator'

    # حروف المعاني والأدوات المغلقة (مجموعات 1–7، 9)
    if any(e.is_operator for e in entries):
        return 'Closed Function Word'

    return 'Bound Nominal'


def _verdict_from(entries: list[MabniEntry], structural_verdict: str,
                  canonical: str = '') -> str:
    """
    الحكم المعجمي من P5 — مقيَّد بالحكم الهيكلي من P4 (قانون الرتابة الصارم).

      structural_verdict = 'ACCEPT' + is_operator → OPERATOR_BOUNDARY
      structural_verdict = 'ACCEPT' + not operator → MABNI_BOUNDARY
      structural_verdict = 'DEFER'  + is_operator → OPERATOR_DEFERRED
      structural_verdict = 'DEFER'  + not operator → MABNI_DEFERRED

    قانون الرتابة (مطلق — RC5):
      P4 ACCEPT → P5 يجوز له أن يُعلن OPERATOR_BOUNDARY
      P4 DEFER  → P5 لا يجوز له تحويل DEFER إلى ACCEPT أبدًا
                  حتى المُدخَل الأجرد يبقى مؤجَّلاً — لا ترقية تلقائية

    ملاحظة: canonical محفوظ في التوقيع للتوافق مع الاستدعاءات القائمة.
    """
    if structural_verdict == 'DEFER':
        if any(e.is_operator for e in entries):
            return 'OPERATOR_DEFERRED'
        return 'MABNI_DEFERRED'
    if any(e.is_operator for e in entries):
        return 'OPERATOR_BOUNDARY'
    return 'MABNI_BOUNDARY'


# ══════════════════════════════════════════════════════════════════════════════
# دالة المعالجة
# ══════════════════════════════════════════════════════════════════════════════

def process_mabni(
    input_surface:      str,
    normalized_surface: str,
    slots:              list[dict],
    slot_verdict:       str,
    violations:         'list[str] | None' = None,
) -> 'MabniBoundary | MabniOpen | MabniBlocked':
    """
    P5: Mabni / Operator Lookup

    المدخلات:
      input_surface      — الرمز كما وصل من المُدخَل (ثابت)
      normalized_surface — بعد normalize(): توسيع شدة + توحيد همزة
      slots              — نتيجة Slot Engineering (قائمة من dict)
      slot_verdict       — 'ACCEPT' | 'DEFER' | 'BLOCK'
      violations         — مخالفات الـ Slot

    المخرجات:
      MabniBoundary  إذا كان مقبولاً مقطعيًا + موجودًا في الكتالوج
      MabniOpen      إذا كان مقبولاً مقطعيًا + غير موجود في الكتالوج
      MabniBlocked   إذا كانت البنية المقطعية فاسدة

    قاعدة P5:
      لا يُسند وظيفة نحوية نهائية.
      يُعلن operator_id / lexical_family — هوية معجمية فقط.
      يُعلن RelationContract — عقد مفتوح تستوفيه الطبقات اللاحقة.

    البحث في الكتالوج:
      canonical_surface = input_surface (سياسة محافظة حالية).
      يُستخدم lookup_canonical(canonical, normalized) ثلاثي المراحل:
        Phase 1: direct Unicode match
        Phase 2: normalized form (توسيع شدة + همزة)
        Phase 3: bare form (حذف كل التشكيل) — للمداخل غير المشكولة

    قانون الرتابة (P4 → P5 monotonicity):
      P4 BLOCK  → MabniBlocked — لا يُرفع بأي ثمن
      P4 DEFER  → MabniBoundary(verdict='OPERATOR_DEFERRED') إن وُجد في الكتالوج
                  وجود الأداة في الكتالوج يُثبت هويتها المعجمية فقط،
                  ولا يُصلح الخانة البنيوية غير المكتملة ولا يمنحها ACCEPT بأثر رجعي.
      P4 ACCEPT → MabniBoundary(verdict='OPERATOR_BOUNDARY') إن وُجد في الكتالوج
    """
    canonical_surface = input_surface

    real_slots    = [s for s in slots if s.get('surface') != ' ']
    slot_patterns = [s['pattern'] for s in real_slots]

    # ── قاعدة 1: الـ Slot يحكم أولاً (BLOCK لا يُرفع) ───────────────────────
    if slot_verdict == 'BLOCK':
        return MabniBlocked(
            input_surface      = input_surface,
            normalized_surface = normalized_surface,
            reason             = 'invalid_slot_structure',
            violations         = violations or [],
        )

    # ── قاعدة 2: بحث في الكتالوج (ثلاثي المراحل) ────────────────────────────
    inventory = get_inventory()
    entries, matched_surface = inventory.lookup_canonical(
        canonical  = canonical_surface,
        normalized = normalized_surface,
    )

    if entries:
        profile   = get_profile(matched_surface)
        contract  = make_contract(profile.operator_id)
        candidates = list(dict.fromkeys(
            e.purpose for e in entries if e.purpose
        ))
        # قانون الرتابة: DEFER من P4 → OPERATOR_DEFERRED لا OPERATOR_BOUNDARY
        # (استثناء: المُدخَل الأجرد بلا تشكيل يُعامَل معجميًا بصرف النظر عن DEFER)
        lexical_verdict = _verdict_from(entries, slot_verdict, canonical=canonical_surface)
        return MabniBoundary(
            input_surface       = input_surface,
            canonical_surface   = canonical_surface,
            normalized_surface  = normalized_surface,
            matched_surface     = matched_surface,
            operator_id         = profile.operator_id,
            lexical_family      = profile.lexical_family,
            slots               = real_slots,
            slot_patterns       = slot_patterns,
            entries             = entries,
            function_candidates = candidates,
            lexical_class       = _lexical_class(entries),
            relation_contract   = contract,
            structural_verdict  = slot_verdict,
            verdict             = lexical_verdict,
        )

    # ── قاعدة 3: لا هوية مبنية → OPEN → HR2S (مع الحفاظ على حكم P4) ─────────
    return MabniOpen(
        input_surface      = input_surface,
        canonical_surface  = canonical_surface,
        normalized_surface = normalized_surface,
        slots              = real_slots,
        slot_patterns      = slot_patterns,
        structural_verdict = slot_verdict,
    )


# ══════════════════════════════════════════════════════════════════════════════
# أيقونات القرار
# ══════════════════════════════════════════════════════════════════════════════

VERDICT_ICON: dict[str, str] = {
    'OPERATOR_BOUNDARY':  '◈',
    'OPERATOR_DEFERRED':  '◌',
    'MABNI_BOUNDARY':    '◈',
    'MABNI_DEFERRED':    '◌',
    'OPEN':              '→',
    'BLOCK':             '✗',
}


# ══════════════════════════════════════════════════════════════════════════════
# اختبار
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    from syllabifier import parse_phones, syllabify, word_gate
    from normalizer  import normalize

    tests = ['وَ', 'بِ', 'كَ', 'لِ', 'مِنْ', 'أَنْ', 'إِلَى', 'فِي', 'عَنْ', 'حَتَّى',
             'إِنَّ', 'أَنَّ', 'لَكِنَّ', 'لَعَلَّ', 'رُبَّ', 'إِلَّا', 'كَيْ', 'كَمْ']
    print()
    for word in tests:
        norm   = normalize(word)
        phones = parse_phones(norm)
        slots  = syllabify(phones)
        verdict, viols = word_gate(slots)
        result = process_mabni(word, norm, slots, verdict, viols)

        icon = VERDICT_ICON.get(result.verdict, '?')
        if isinstance(result, MabniBoundary):
            rc = result.relation_contract
            print(f"  {icon} {word:12} → {result.verdict:22} [{' | '.join(result.slot_patterns)}]")
            print(f"       operator_id       : {result.operator_id}")
            print(f"       lexical_family    : {result.lexical_family}")
            print(f"       matched_surface   : {result.matched_surface}")
            print(f"       contract_id       : {rc.contract_id}")
            print(f"       contract_state    : {rc.contract_state}")
            print()
        elif isinstance(result, MabniOpen):
            print(f"  {icon} {word:12} → {result.verdict:22} [{' | '.join(result.slot_patterns)}]  → HR2S")
        else:
            print(f"  {icon} {word:12} → {result.verdict:22} {result.reason}")
