# REFACTORING_ARCHITECTURE.md
# خريطة إعادة هيكلة خط الأنابيب

**الحالة:** معتمدة — النسخة الثانية (بعد التصحيحات المعمارية الخمسة)  
**تاريخ الإعداد:** 2026-07-15  
**Baseline المرجعي:** انظر `reports/refactoring/baseline.json` — الرقم وحده لا يكفي

---

## مبادئ الهيكلة

1. **كل طبقة تستقبل مخرج الطبقة التي تسبقها مباشرة — ولا شيء آخر.**  
   P5 لا تستدعي regex على النص الخام. P2 لا تُعيد التطبيع بنفسها.

2. **لا تُضاف قاعدة صرفية أثناء الـ refactoring.**  
   النقل لا يغير الأحكام ولا الكتالوجات — يغير المكان فقط.

3. **shim إلزامي لكل ملف كود منقول حتى اختفاء آخر مستهلك.**  
   الملف القديم يصبح shim يستورد من الموقع الجديد ويُصدر نفس الأسماء بنفس الأنواع.

4. **الاختبارات تبقى في أماكنها الحالية خلال R-1 إلى R-13 (مراحل نقل الكود).**  
   نقل الاختبارات يغير node IDs ويُفشل diff الـ baseline دون أي تغيير وظيفي.  
   مرحلة مستقلة R-13T مخصصة لإعادة تنظيم الاختبارات بعد ثبات الكود.

5. **لا يُنشأ shim لملفات الاختبار** — في أي مرحلة.

6. **لا يُحذف الملف القديم قبل أن يُثبَت تكافؤه مع البديل وتحول كل مستهلكيه.**

7. **كل خطوة نقل كود تنتهي بـ `diff baseline_ids.txt current_ids.txt` فارغًا.**  
   هذا الشرط صالح فقط لمراحل R-1 إلى R-13 (كود فقط، لا نقل اختبارات).  
   مرحلة R-13T تستخدم مقارنة logical IDs (انظر أدناه).

---

## الهيكل الهدف

```
hokom/
├── pipeline/
│   ├── p0_unicode/
│   │   ├── glyph_classification.py   ← ينقل من: glyph_classification.py
│   │   ├── unicode_candidate.py      ← يُستخرج من: licensing.py §1
│   │   └── models.py                 ← GlyphTrace, GlyphClass, BaseGlyphClass, MarkClass …
│   │
│   ├── p1_atomic_structure/
│   │   ├── normalizer.py             ← ينقل من: normalizer.py
│   │   ├── span_map.py               ← ينقل من: span_alignment.py
│   │   ├── tokenizer.py              ← ينقل من: tokenizer.py
│   │   ├── letter_identity.py        ← يُستخرج من: licensing.py §2–4 (C/VL/حركات)
│   │   ├── cell_builder.py           ← يُستخرج من: syllabifier.py §parse_phones + §syllabify
│   │   ├── slot_engineering.py       ← يُستخرج من: syllabifier.py §word_gate + SLOT_TRANS
│   │   └── models.py                 ← NormalizationResult, PhoneSeq, CellSeq, SlotResult …
│   │
│   ├── p2_registry_projection/
│   │   ├── operator_projection.py    ← ينقل من: operator_id_map.py
│   │   ├── mabni_projection.py       ← يُستخرج من: mabni_layer.py
│   │   ├── attachment_projection.py  ← يُستخرج من: mabniyat_attachment.py
│   │   │                                مسؤوليته: توليد المرشحين وإرفاق الدليل والـ spans
│   │   │                                لا يختار فائزًا ولا يُصدر حكمًا
│   │   ├── root_projection.py        ← يُستخرج من: root_analysis.py §extract_radicals
│   │   └── models.py                 ← RegistryProjectionResult, AttachmentProjectionCandidate …
│   │
│   ├── p3_root_stem/
│   │   ├── root_candidate.py         ← يُستخرج من: root_analysis.py §analyze_lexeme + types
│   │   ├── root_stem_closure.py      ← جديد (PR 3.6+): توحيد الجذر عبر الأشكال
│   │   └── models.py                 ← RootProfile, UnknownRadical, LexemeAnalysis …
│   │
│   ├── p4_jamid_mushtaq/
│   │   ├── jamid_mushtaq_projection.py   ← جديد (wrapper في البداية)
│   │   ├── jamid_mushtaq_closure.py      ← جديد (wrapper في البداية)
│   │   └── models.py                     ← JamidMushtaqResult (انظر العقد أدناه)
│   │
│   ├── p5_mufrad_word/
│   │   ├── operator_boundary.py      ← يُستخرج من: mabniyat_attachment.py §operator path
│   │   ├── mabni_boundary.py         ← يُستخرج من: mabniyat_attachment.py §mabni path
│   │   ├── attachment_boundary.py    ← يُستخرج من: mabniyat_attachment.py
│   │   │                                يستقبل AttachmentProjectionCandidate من P2
│   │   │                                ويقرر: ACCEPT | DEFER | REJECT | COMPOSITE_BOUNDARY
│   │   │                                لا يُعيد توليد المرشحين ولا يمسح النص الخام
│   │   ├── host_analysis.py          ← يُستخرج من: mabniyat_attachment.py §_analyze_host
│   │   └── models.py                 ← TokenAnalysis, AttachedMabniSpan, HostAnalysis,
│   │                                    ComponentBoundary, WordAnalysis …
│   │
│   ├── contracts/
│   │   ├── relation_contract.py      ← ينقل من: relation_contract.py (ملف مستقل)
│   │   └── models.py                 ← RelationContract, Verdict, EvidenceAssessment …
│   │                                    تُستخدم في P5 والطبقات P7–P9 مستقبلًا
│   │
│   └── orchestrator.py               ← ينقل من: hokom_pipeline.py §hokom()
│
├── registries/
│   ├── operators/                    ← data + ينقل من: operator_id_map.py §_OPERATOR_PROFILES
│   ├── mabniyat/                     ← ينقل من: mabni_inventory.py + data/02_mabniyat/
│   ├── attachments/                  ← ينقل من: mabniyat_attachment.py §_ATTACH_CATALOG
│   └── root_classes/                 ← مستقبلاً (PR 3.6+)
│
├── reports/
│   └── refactoring/
│       ├── baseline.json             ← يُنشأ في R-0
│       ├── r1_snapshot.json          ← node IDs بعد R-1
│       ├── r2_snapshot.json
│       └── …                        ← snapshot بعد كل مرحلة
│
├── tests/
│   ├── unit/
│   │   ├── p0_unicode/
│   │   │   ├── test_glyph_classification.py  ← يُنقل من: tests/test_glyph_classification.py
│   │   │   └── test_unicode_candidate.py     ← جديد
│   │   ├── p1_atomic_structure/
│   │   │   ├── test_span_map.py              ← يُنقل من: tests/test_span_alignment.py
│   │   │   ├── test_cell_builder.py          ← يُستخرج من: test_hokom.py
│   │   │   └── test_slot_engineering.py      ← يُستخرج من: test_hokom.py
│   │   ├── p2_registry_projection/
│   │   │   └── test_root_projection.py       ← يُنقل من: tests/test_root_analysis.py
│   │   └── p5_mufrad_word/
│   │       └── test_token_analysis.py        ← يُستخرج من: test_hokom.py
│   │
│   ├── integration/
│   │   └── test_full_pipeline.py             ← يُستخرج من: test_hokom.py §integration
│   │
│   ├── regression/
│   │   ├── test_story_regression.py          ← يُستخرج من: test_hokom.py §story regression
│   │   ├── test_mabniyat_manifest.py         ← ينقل من: tests/integration/test_all_mabniyat_json_examples.py
│   │   └── test_governance_cases.py          ← يُستخرج من: test_hokom.py §governance
│   │
│   └── fixtures/
│
└── scripts/
    ├── run_pipeline.py
    ├── build_mabniyat_harness.py     ← ينقل من: scripts/build_mabniyat_test_harness.py
    └── governance_diagnostic.py     ← ينقل من: scripts/governance_diagnostic.py
```

---

## عقود الطبقات

### التدفق الكامل

```
P0  GlyphSequence
 ↓
P1  NormalizationResult → SlotEngineeringResult
 ↓
P2  RegistryProjectionResult
 ↓
P3  RootStemResult
 ↓
P4  JamidMushtaqResult
 ↓
P5  WordAnalysis
```

---

### P0 → P1

```python
@dataclass(frozen=True)
class GlyphSequence:
    raw_surface: str
    glyphs: tuple[GlyphTrace, ...]      # واحد لكل grapheme cluster
    raw_offsets: tuple[int, ...]        # إزاحة البداية لكل glyph في raw_surface
```

---

### P1 → P2

```python
@dataclass(frozen=True)
class NormalizationResult:
    raw_surface: str
    canonical_surface: str              # NFC
    normalized_surface: str             # بعد الهمزة + ال + الشدة
    span_map: SpanMap                   # raw ↔ normalized

@dataclass(frozen=True)
class SlotEngineeringResult:
    normalized_surface: str
    slots: tuple[SlotState, ...]        # CV / CVC / CVVC …
    verdict: Verdict                    # ACCEPT | DEFER | BLOCK
    residuals: tuple[str, ...]
    span_map: SpanMap
```

---

### P2 → P3

**ملاحظة attachment:**  
`attachment_projection` في P2 يولّد المرشحين فقط — لا يختار فائزًا.  
`attachment_boundary` في P5 يستقبل المرشحين ويُصدر الحكم.  
لا يوجد منطق توليد في P5، ولا منطق حكم في P2.

```python
@dataclass(frozen=True)
class AttachmentProjectionCandidate:
    prefix_candidates: tuple[PrefixCandidate, ...]
    suffix_candidates: tuple[SuffixCandidate, ...]
    residual_surface: str
    evidence: tuple[EvidenceAssessment, ...]
    spans: tuple[AttachedMabniSpan, ...]

@dataclass(frozen=True)
class RegistryProjectionResult:
    slot_result: SlotEngineeringResult
    operator_match: Optional[OperatorProfile]
    mabni_match: Optional[MabniEntry]
    attachment_candidates: tuple[AttachmentProjectionCandidate, ...]
    root_surface_analysis: Optional[SurfaceAnalysis]
    collisions: tuple[ProjectionCollision, ...]
    verdict: Verdict
    residuals: tuple[str, ...]
```

---

### P3 → P4

```python
@dataclass(frozen=True)
class RootStemResult:
    registry: RegistryProjectionResult
    root: Optional[tuple[str, str, str]]    # None إذا DEFER
    root_profile: Optional[RootProfile]
    lexeme_decision: str                    # ACCEPT | DEFER | REJECT
    evidence_chain: tuple[EvidenceAssessment, ...]
    residuals: tuple[str, ...]
```

---

### P4 → P5

```python
@dataclass(frozen=True)
class JamidMushtaqResult:
    root_stem: RootStemResult
    derivation_class: str               # JAMID | MUSHTAQ | UNKNOWN
    candidate_awzan: tuple[str, ...]    # أوزان مرشحة (قد تكون فارغة في البداية)
    verdict: Verdict
    evidence_chain: tuple[EvidenceAssessment, ...]
    residuals: tuple[str, ...]
```

**ملاحظة:** P4 يبدأ كـ passthrough يُعيد تمرير `RootStemResult` داخل `JamidMushtaqResult`  
مع `derivation_class='UNKNOWN'` و`verdict=DEFER`. يُملأ تدريجيًا بعد اكتمال الـ refactoring.  
موضعه المعماري ثابت منذ R-0 حتى لا يُبنى R-9 بافتراض أن P3 يتصل مباشرة بـ P5.

---

### P5 → خروج

```python
@dataclass(frozen=True)
class WordAnalysis:
    raw_surface: str
    decision: str           # OPERATOR_BOUNDARY | MABNI_BOUNDARY |
                            # COMPOSITE_BOUNDARY | OPEN_TO_HR2S |
                            # DEFERRED | BLOCKED
    token_analysis: Optional[TokenAnalysis]
    jamid_mushtaq: Optional[JamidMushtaqResult]
    residuals: tuple[str, ...]
    span_map: SpanMap
```

---

## Baseline المرجعي

### R-0: الإنشاء (قبل أي نقل) — مُنجَز

```bash
python3 -m pytest --collect-only -q tests/ --ignore=tests/integration \
  | grep "::" | sort > reports/refactoring/baseline_ids.txt

python3 -m pytest -q tests/ --ignore=tests/integration \
  > reports/refactoring/baseline_run.txt
```

الملفان موجودان:
- `reports/refactoring/baseline_ids.txt` — 272 node ID
- `reports/refactoring/baseline.json` — 272 passed, 52 subtests

---

### شرط الإغلاق لمراحل R-1 إلى R-13 (نقل كود فقط)

لأن الاختبارات لا تُنقل في هذه المراحل، يجب أن يبقى diff فارغًا:

```bash
python3 -m pytest --collect-only -q tests/ --ignore=tests/integration \
  | grep "::" | sort > /tmp/current_ids.txt

diff reports/refactoring/baseline_ids.txt /tmp/current_ids.txt
# يجب أن يكون الناتج: فارغًا تمامًا
```

الشرط الكامل:
- نفس node IDs بالمسارات الكاملة (diff فارغ)
- نفس نتائج التشغيل (passed/failed/skipped)
- الرقم الإجمالي مشتق — وليس الشرط الأساسي

---

### شرط الإغلاق لمرحلة R-13T (نقل الاختبارات)

نقل الاختبار يغير المسار في node ID لكن لا يغير اسم الدالة.  
المقارنة تكون على الجزء المنطقي (كل ما بعد أول `::`) لا على المسار:

```bash
# قبل نقل الاختبارات: استخرج الـ logical IDs من baseline
grep "::" reports/refactoring/baseline_ids.txt \
  | sed 's#^[^:]*::##' | sort \
  > reports/refactoring/baseline_logical_ids.txt

# بعد كل خطوة نقل اختبار:
python3 -m pytest --collect-only -q tests/ --ignore=tests/integration \
  | grep "::" | sed 's#^[^:]*::##' | sort \
  > /tmp/current_logical_ids.txt

diff reports/refactoring/baseline_logical_ids.txt /tmp/current_logical_ids.txt
# يجب أن يكون الناتج: فارغًا — نفس الأسماء، مهما تغيرت المسارات
```

بذلك:
- نقل `tests/test_glyph_classification.py` → `tests/unit/p0_unicode/test_glyph_classification.py`  
  يغير المسار لكن يُبقي `TestBuildGlyphTraces::test_empty_string` كما هو → diff فارغ ✓
- إضافة اختبار جديد أو حذف قائم → diff غير فارغ → يُمنع

---

## خريطة الملفات الحالية → الهدف

| الملف الحالي | الطبقة | الهدف | نوع العملية |
|---|---|---|---|
| `glyph_classification.py` | P0 | `pipeline/p0_unicode/glyph_classification.py` | نقل مباشر |
| `licensing.py §1 gate_unicode` | P0 | `pipeline/p0_unicode/unicode_candidate.py` | استخراج |
| `licensing.py §2–4` | P1 | `pipeline/p1_atomic_structure/letter_identity.py` | استخراج |
| `normalizer.py` | P1 | `pipeline/p1_atomic_structure/normalizer.py` | نقل مباشر |
| `span_alignment.py` | P1 | `pipeline/p1_atomic_structure/span_map.py` | نقل + إعادة تسمية |
| `tokenizer.py` | P1 | `pipeline/p1_atomic_structure/tokenizer.py` | نقل مباشر |
| `syllabifier.py §parse_phones` | P1 | `pipeline/p1_atomic_structure/cell_builder.py` | استخراج |
| `syllabifier.py §word_gate + SLOT_TRANS` | P1 | `pipeline/p1_atomic_structure/slot_engineering.py` | استخراج |
| `syllable_patterns.py` | P1 | `pipeline/p1_atomic_structure/slot_engineering.py` | يُدمج |
| `transitions.py` | P1 | `pipeline/p1_atomic_structure/slot_engineering.py` | يُدمج |
| `operator_id_map.py` | P2 | `pipeline/p2_registry_projection/operator_projection.py` | نقل مباشر |
| `mabni_layer.py §lookup` | P2 | `pipeline/p2_registry_projection/mabni_projection.py` | استخراج |
| `mabniyat_attachment.py §توليد مرشحين` | P2 | `pipeline/p2_registry_projection/attachment_projection.py` | استخراج |
| `root_analysis.py §extract_radicals` | P2 | `pipeline/p2_registry_projection/root_projection.py` | استخراج |
| `root_analysis.py §analyze_lexeme + types` | P3 | `pipeline/p3_root_stem/root_candidate.py` | استخراج |
| `mabni_layer.py §process_mabni` | P5 | `pipeline/p5_mufrad_word/mabni_boundary.py` | استخراج |
| `mabniyat_attachment.py §operator path` | P5 | `pipeline/p5_mufrad_word/operator_boundary.py` | استخراج |
| `mabniyat_attachment.py §حكم التقشير` | P5 | `pipeline/p5_mufrad_word/attachment_boundary.py` | استخراج |
| `mabniyat_attachment.py §_analyze_host` | P5 | `pipeline/p5_mufrad_word/host_analysis.py` | استخراج |
| `mabniyat_attachment.py §models` | P5 | `pipeline/p5_mufrad_word/models.py` | استخراج |
| `relation_contract.py` | Contracts | `pipeline/contracts/relation_contract.py` | نقل مباشر |
| `hokom_pipeline.py §hokom()` | Orch | `pipeline/orchestrator.py` | نقل مباشر |
| `sentence_pipeline.py` | Orch | `pipeline/orchestrator.py` أو مستقل | يُدمج أو يُفصل |
| `mabni_inventory.py` | Registry | `registries/mabniyat/inventory.py` | نقل مباشر |
| `build_mabniyat.py` | Scripts | `scripts/build_mabniyat_harness.py` | نقل مباشر |
| `src/arabic/phonology.py` | — | **يُحذف** بعد جدول التكافؤ (انظر أدناه) | حذف مشروط |

---

## ترتيب النقل

### R-0 — تثبيت baseline

```bash
mkdir -p reports/refactoring
python3 -m pytest --collect-only -q tests/ --ignore=tests/integration \
  | grep "::" | sort > reports/refactoring/baseline_ids.txt
python3 -m pytest -q tests/ --ignore=tests/integration \
  > reports/refactoring/baseline_run.txt
```

لا تبدأ R-1 قبل إنشاء هذين الملفين وتأكيد العدد: **272 passed, 52 subtests**.

---

### R-1 — P0: نقل glyph_classification

**الملفات (كود فقط — الاختبارات تبقى في موقعها):**
- يُنشأ: `pipeline/__init__.py`, `pipeline/p0_unicode/__init__.py`
- يُنقل كود: `glyph_classification.py` → `pipeline/p0_unicode/glyph_classification.py`
- يُنشأ shim كود: `glyph_classification.py` (استيراد + تصدير فقط، لا منطق)
- `tests/test_glyph_classification.py` — **يبقى كما هو** حتى R-13T

**التحقق:**
```bash
python3 -m pytest --collect-only -q tests/ --ignore=tests/integration \
  | grep "::" | sort > /tmp/r1.txt && diff reports/refactoring/baseline_ids.txt /tmp/r1.txt
# يجب أن يكون الناتج: فارغًا
```

---

### R-2 — P1-a: normalizer + span_map

**الملفات (كود فقط — الاختبارات تبقى في موقعها):**
- يُنشأ: `pipeline/p1_atomic_structure/__init__.py`
- يُنقل كود: `normalizer.py` → `pipeline/p1_atomic_structure/normalizer.py`
- يُنقل كود: `span_alignment.py` → `pipeline/p1_atomic_structure/span_map.py`
- يُنشأ shim كود: `normalizer.py`, `span_alignment.py`
- `tests/test_span_alignment.py` — **يبقى كما هو** حتى R-13T

---

### R-3 — P1-b: tokenizer

**الملفات:**
- يُنقل كود: `tokenizer.py` → `pipeline/p1_atomic_structure/tokenizer.py`
- يُنشأ shim كود: `tokenizer.py`

---

### R-4 — P1-c: cell_builder + slot_engineering

**الملفات (كود فقط — الاختبارات تبقى في موقعها):**
- يُستخرج من `syllabifier.py`:
  - `parse_phones`, `syllabify`, `Phone` → `pipeline/p1_atomic_structure/cell_builder.py`
  - `word_gate`, `SLOT_TRANS`, `VALID_S`, ثوابت → `pipeline/p1_atomic_structure/slot_engineering.py`
- يُدمج: `syllable_patterns.py`, `transitions.py` داخل `slot_engineering.py`
- يُنشأ shim كود: `syllabifier.py`
- اختبارات syllabifier في `test_hokom.py` — **تبقى كما هي** حتى R-13T

---

### R-5 — P1-d: تقسيم licensing

**الملفات:**
- §1 (gate_unicode) → `pipeline/p0_unicode/unicode_candidate.py`
- §2–4 (C/VL/حركات) → `pipeline/p1_atomic_structure/letter_identity.py`
- يُنشأ shim كود: `licensing.py`

---

### R-6 — Contracts: نقل relation_contract

**الملفات:**
- يُنشأ: `pipeline/contracts/__init__.py`
- يُنقل كود: `relation_contract.py` → `pipeline/contracts/relation_contract.py`
- يُنشأ shim كود: `relation_contract.py`

**سبب التبكير:** العقود تُستخدم في P5 وفي الطبقات P7–P9 المستقبلية. نقلها مبكرًا يمنع تضمينها في `p5_mufrad_word/models.py` ثم اضطرار استخراجها لاحقًا.

---

### R-7 — P2-a: operator_projection

**الملفات:**
- يُنشأ: `pipeline/p2_registry_projection/__init__.py`
- يُنقل كود: `operator_id_map.py` → `pipeline/p2_registry_projection/operator_projection.py`
- يُنشأ shim كود: `operator_id_map.py`

---

### R-8 — P2-b: mabni_projection + mabni_inventory

**الملفات:**
- يُنشأ: `registries/mabniyat/__init__.py`
- يُنقل كود: `mabni_inventory.py` → `registries/mabniyat/inventory.py`
- يُنشأ shim كود: `mabni_inventory.py`
- يُستخرج من `mabni_layer.py` → `pipeline/p2_registry_projection/mabni_projection.py`
- يُنشأ shim كود: `mabni_layer.py`

---

### R-9 — P2-c: attachment_projection (توليد فقط)

**تنبيه الفصل:** هذه المرحلة تنقل **منطق توليد المرشحين** فقط من `mabniyat_attachment.py`.  
منطق الحكم (ACCEPT/DEFER/COMPOSITE_BOUNDARY) يبقى في الملف القديم حتى R-11.

**الملفات:**
- يُستخرج من `mabniyat_attachment.py` §توليد مرشحين → `pipeline/p2_registry_projection/attachment_projection.py`
- يُنشأ `AttachmentProjectionCandidate` في `pipeline/p2_registry_projection/models.py`
- `mabniyat_attachment.py` يستورد `AttachmentProjectionCandidate` من الموقع الجديد

**التحقق الإضافي:** تأكد أن `attachment_projection.py` لا يستورد أي شيء من P5.

---

### R-10 — P2-d + P3: root_projection + root_stem

**الملفات (كود فقط — الاختبارات تبقى في موقعها):**
- يُستخرج: `extract_radicals` → `pipeline/p2_registry_projection/root_projection.py`
- يُستخرج: `analyze_lexeme` + كل الأنواع → `pipeline/p3_root_stem/root_candidate.py`
- يُنشأ shim كود: `root_analysis.py`
- `tests/test_root_analysis.py` — **يبقى كما هو** حتى R-13T

---

### R-11 — P4: إنشاء passthrough stub

**الملفات:**
- يُنشأ: `pipeline/p4_jamid_mushtaq/__init__.py`
- يُنشأ: `pipeline/p4_jamid_mushtaq/models.py` ← `JamidMushtaqResult` dataclass
- يُنشأ: `pipeline/p4_jamid_mushtaq/jamid_mushtaq_projection.py` ← passthrough

```python
# jamid_mushtaq_projection.py — stub حتى اكتمال P4 لغويًا
def project_jamid_mushtaq(root_stem: RootStemResult) -> JamidMushtaqResult:
    return JamidMushtaqResult(
        root_stem=root_stem,
        derivation_class='UNKNOWN',
        candidate_awzan=(),
        verdict=Verdict.DEFER,
        evidence_chain=(),
        residuals=('defer:p4:not_implemented',),
    )
```

**شرط الإغلاق:** stub يمر عبر سلسلة العقود دون أن يكسر أي اختبار.

---

### R-12 — P5: تفكيك mabniyat_attachment

**ترتيب الاستخراج الداخلي (إلزامي):**

1. `pipeline/p5_mufrad_word/models.py` — TokenAnalysis, HostAnalysis, ComponentBoundary, WordAnalysis  
   (لا تبعيات داخلية — أول ما يُنقل)
2. `pipeline/p5_mufrad_word/host_analysis.py` — `_analyze_host`
3. `pipeline/p5_mufrad_word/operator_boundary.py` — مسار operator
4. `pipeline/p5_mufrad_word/mabni_boundary.py` — مسار mabni
5. `pipeline/p5_mufrad_word/attachment_boundary.py` — يستقبل `AttachmentProjectionCandidate` من P2 ويُصدر الحكم
6. يُنشأ shim كود: `mabniyat_attachment.py` يُعيد تصدير كل شيء

**التحقق الإضافي:** تأكد أن `attachment_boundary.py` لا يستدعي أي توليد مرشحين — يستقبلها جاهزة من P2.

---

### R-13 — Orchestrator + scripts

**الملفات:**
- `hokom_pipeline.py §hokom()` → `pipeline/orchestrator.py`
- `sentence_pipeline.py` → يُدمج أو يُفصل داخل `pipeline/`
- `scripts/` → تُنقل بأسمائها الجديدة
- يُنشأ shim كود: `hokom_pipeline.py`

---

### R-13T — إعادة تنظيم الاختبارات (Test Layout)

**شرط البدء:** اكتمال R-13 (orchestrator) وثبات كامل الـ shims.

**طبيعة هذه المرحلة:** تغيير مسارات فقط — لا تغيير في منطق أي اختبار.

**خريطة النقل:**

| المصدر | الهدف |
|---|---|
| `tests/test_glyph_classification.py` | `tests/unit/p0_unicode/test_glyph_classification.py` |
| `tests/test_span_alignment.py` | `tests/unit/p1_atomic_structure/test_span_map.py` |
| `tests/test_root_analysis.py` | `tests/unit/p2_registry_projection/test_root_projection.py` |
| `test_hokom.py §syllabifier` | `tests/unit/p1_atomic_structure/test_cell_builder.py` + `test_slot_engineering.py` |
| `test_hokom.py §mabniyat` | `tests/unit/p5_mufrad_word/test_token_analysis.py` |
| `test_hokom.py §integration` | `tests/integration/test_full_pipeline.py` |
| `test_hokom.py §story regression` | `tests/regression/test_story_regression.py` |
| `test_hokom.py §governance` | `tests/regression/test_governance_cases.py` |
| `tests/integration/test_all_mabniyat_json_examples.py` | `tests/regression/test_mabniyat_manifest.py` |

**إجراء كل خطوة نقل داخل R-13T:**
```bash
# 1. نقل الملف
mv tests/test_glyph_classification.py tests/unit/p0_unicode/test_glyph_classification.py

# 2. تحقق من logical IDs
python3 -m pytest --collect-only -q tests/ --ignore=tests/integration \
  | grep "::" | sed 's#^[^:]*::##' | sort > /tmp/logical.txt
diff reports/refactoring/baseline_logical_ids.txt /tmp/logical.txt
# يجب: فارغ

# 3. تشغيل كامل
python3 -m pytest -q tests/
```

**لا يوجد `__init__.py` في مجلدات الاختبار** — pytest يكتشفها بـ `testpaths` في `pyproject.toml`.

**شرط إغلاق R-13T:**
```bash
diff reports/refactoring/baseline_logical_ids.txt \
  <(python3 -m pytest --collect-only -q tests/ | grep "::" | sed 's#^[^:]*::##' | sort)
# فارغ
```

---

### R-14 — حذف الـ shims + التنظيف النهائي

**شرط البدء لكل ملف:** لا يوجد `import` منه خارج الـ shim نفسه.

```bash
# مثال التحقق قبل حذف normalizer.py
grep -r "from normalizer import\|import normalizer" . \
  --include="*.py" --exclude-dir=__pycache__ \
  | grep -v "^./normalizer.py:"
# الناتج يجب أن يكون فارغًا
```

**ترتيب الحذف:**
```
# بعد R-4
syllable_patterns.py
transitions.py

# بعد R-5
licensing.py          (الـ shim)

# بعد R-6
relation_contract.py  (الـ shim)

# بعد R-7
operator_id_map.py    (الـ shim)

# بعد R-8
mabni_inventory.py    (الـ shim)
mabni_layer.py        (الـ shim)

# بعد R-10
root_analysis.py      (الـ shim)

# بعد R-1
glyph_classification.py  (الـ shim)

# بعد R-2
normalizer.py         (الـ shim)
span_alignment.py     (الـ shim)

# بعد R-3
tokenizer.py          (الـ shim)

# بعد R-4
syllabifier.py        (الـ shim)

# بعد R-12
mabniyat_attachment.py  (الـ shim)

# بعد R-13
hokom_pipeline.py     (الـ shim)
sentence_pipeline.py  (الـ shim)

# src/arabic/phonology.py — انظر إجراء الحذف الخاص أدناه
```

---

## إجراء حذف `src/arabic/phonology.py`

هذا الملف مُهمل منذ Phase A لكن لا يُحذف بدون تقرير تكافؤ مكتوب:

| الدالة القديمة | البديل الجديد | ملف البديل | مستهلكون متبقون |
|---|---|---|---|
| `parse_phonemes()` | `parse_phones()` | `cell_builder.py` | 0 |
| `classify_char()` | `classify_base_glyph()` | `glyph_classification.py` | 0 |
| `…` | `…` | `…` | 0 |

**شرط الحذف:** كل خانة "مستهلكون متبقون" = 0، ومُثبَت بـ `grep`.

```bash
grep -r "from src.arabic.phonology import\|from src.arabic import phonology\|import phonology" . \
  --include="*.py" --exclude-dir=__pycache__
# الناتج يجب أن يكون فارغًا
```

---

## شروط حذف أي ملف قديم (قائمة مرجعية)

لكل ملف يُراد حذفه:

- [ ] محتواه موجود بالكامل في الموقع الجديد
- [ ] الملف الجديد اجتاز اختباراته المستقلة
- [ ] لا يوجد `import` من الملف القديم خارج الـ shim (مثبَت بـ grep)
- [ ] الـ shim لا يحتوي منطقًا — استيراد وتصدير فقط
- [ ] `diff baseline_ids.txt current_ids.txt` لا يعطي فرقًا

---

## قواعد صارمة أثناء الـ refactoring

1. **لا تُضاف قواعد صرفية جديدة** — الكتالوجات تبقى كما هي.
2. **لا تُغيَّر الأحكام** — نفس الـ verdict لنفس المدخلات.
3. **لا تُعدَّل الـ JSON** تحت `data/02_mabniyat/`.
4. **لا تُنشأ commits أو tags**.
5. **لا تُنشأ shims لملفات الاختبار**.
6. **P4 يبقى stub حتى اكتمال الـ refactoring**.
7. **attachment: التوليد في P2، والحكم في P5، لا منطق مشترك**.
8. **contracts/ مستقلة عن P5 — لا تُدمج فيها**.

---

## خريطة التبعيات الحالية (للمرجع)

```
hokom_pipeline.py
  ├── tokenizer.py
  ├── normalizer.py
  ├── syllabifier.py
  ├── licensing.py → glyph_classification.py
  ├── mabni_layer.py
  │   ├── mabni_inventory.py
  │   ├── operator_id_map.py
  │   └── relation_contract.py
  └── mabniyat_attachment.py          ← 8 تبعيات — أعمق نقطة
      ├── mabni_layer.py
      ├── mabni_inventory.py
      ├── operator_id_map.py
      ├── normalizer.py
      ├── syllabifier.py
      ├── licensing.py
      ├── glyph_classification.py
      └── span_alignment.py

root_analysis.py
  ├── normalizer.py §normalize_hamza
  └── syllabifier.py §parse_phones
```

---

## التمييز الحاسم: P2 structural refactoring مقابل P2 morphological expansion

**ما يحدث في R-7 إلى R-10 (structural refactoring):**
- نقل الكود الموجود لـ operator/mabni/root/attachment إلى الهيكل الجديد
- لا تُضاف معرفة صرفية جديدة
- `root_projection` ينقل `extract_radicals` فقط — لا يضيف أوزانًا أو زيادات

**ما يحدث بعد اكتمال الـ refactoring (morphological expansion):**
- توسيع P2 لغويًا: أوزان، زيادات، نهايات صرفية، فئات جذور
- هذا هو "P2 Registry Projection (morphological)" في التسلسل الزمني

الصياغة الصحيحة للتسلسل:

```
الآن (Phase B مغلق)
      ↓
R-0 إلى R-14  Structural Refactoring
               (نقل كود موجود — لا معرفة جديدة)
      ↓
✓ Refactoring مكتمل — baseline_ids ثابت
      ↓
PR 3.6  Lafif resolution + IBL
      ↓
PR 3.7  Compressed imperatives
      ↓
P2 Morphological Expansion
   (أوزان / زيادات / نهايات صرفية / فئات جذور)
      ↓
P4 Linguistic Fill
   (جامد / مشتق / تصريف)
```

G2 (يَدْعُونَ disambiguation) لا يُحل حتى اكتمال P2 Morphological Expansion — ولا بأي استثناء نصي.
