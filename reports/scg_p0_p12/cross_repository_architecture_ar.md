# الهندسة المعمارية للمستودعات المتقاطعة — SCG P0–P12
## HOKOM-SALEH-QIYAS-SCG-CROSS-REPOSITORY-OWNERSHIP-RESOLUTION-07
### القسم 8 — تعريف البنية المعمارية الصحيحة

---

## 1. الأنظمة الثلاثة المستقلة

تتألف منظومة SCG P0–P12 من ثلاثة أنظمة مستقلة لكل منها ملكيته وحدوده الصارمة:

| النظام | الملكية | المستودع | الدور |
|--------|---------|----------|-------|
| Hokom | مستودع Hokom | `hokom/` | خط أنابيب الصرف العربي (P0–P5 كمساهمة) |
| Saleh/Qiyas | مستودع Saleh | `fractal/algebra/Saleh-` | سلسلة المرشحين الكنونيين P0–P12 |
| Taaqol | مورّد Taaqol | `hokom/vendor/Taaqol-GPT/` | طبقة الحكم والترخيص |

---

## 2. خط أنابيب Hokom — الحدود والمخرجات

**الوصف:** خط أنابيب Hokom هو محرك تحليل صرفي وحيد الرمز (single-token). يُنفَّذ رمز عربي واحد في كل تشغيل.

**المراحل الداخلية (11 حافة — 12 مرحلة):**

```
NORMALIZE → SEGMENT → NORM_ATOMIC → BOUNDARY → ROOT_CAND
→ PHASE_4A → PHASE_4B → PHASE_4C → PHASE_4D
→ WORD_CLASS → PHASE_5 → TAAQOL_SGA
```

**البوابات:** 11 بوابة `_scg_gate()` تستدعي `TaaqolJudgmentEnforcer` — تُوقف التنفيذ عند: `BLOCKED | REJECTED | FORBIDDEN_LEAP | DEFERRED | INVALID`.

**الحد الأقصى لمخرج Hokom:** `MufradWordCandidate` (P5 في السجل الكنوني Saleh/Qiyas). لا يمكن لـ Hokom إنتاج `VerbalSignifiedCandidate` (P6) أو أعلى بشكل مباشر.

**الإسهام في SCG P6–P8 (كمصدر للبيانات فقط):**
- تنتج Hokom الجيومتريا الصرفية (CV، n_consonants، cadence، gemination) في `MufradWordCandidate.trace`
- يقرأ محول P6 في Saleh/Qiyas هذه الجيومتريا من أثر P5 لتمييز VerbalSignifiedCandidate
- Hokom **ليست** المنتج المباشر لـ P6–P8؛ هي **مزودة بيانات** (evidence provider)

---

## 3. سجل Saleh/Qiyas — المرشحون الكنونيون

**الملف المرجعي:** `src/qiyas_core/slot_geometry_core/master_registry_seed.py`
**الرمز:** `build_p12_implemented_registry()` → `MasterLayerRegistry`
**المستودع:** `fractal/algebra/Saleh-` (remote: https://github.com/sonaiso/Saleh-.git)
**HEAD:** `d24f44a`
**الحالة:** 19 طبقة — جميعها `implemented`

### سلسلة المرشحين الكنونيين:

```
P0: UnicodeCandidate
  → TypedCodePoint
  → GlyphClassificationCandidate

P1: LetterIdentityCarrier
    HarakaMarkIdentityCarrier
    ConditionedTypedSequence
    PositionCarrier
    SlotCandidate

P2: RegistryProjectionCandidate

P3: RootStemCandidate

P4: JamidMushtaqCandidate

P5: MufradWordCandidate           ◄── نقطة تسليم Hokom / Saleh-Qiyas

P6: VerbalSignifiedCandidate      ◄── رمز واحد (single-word)
P7: CompositionReadinessCandidate ◄── رمز واحد
P8: AmilMamulCandidate            ◄── رمز واحد

P9: SentenceGeometryCandidate     ◄── أول طبقة متعددة الوحدات (>=2 كلمات)
P10: RelationGeometryCandidate
P11: IrabGeometryCandidate
P12: IfadahCandidate              ◄── طرفي (TERMINAL)
```

### الحد الفاصل P8/P9 — الأهم معماريًا:

| المستوى | الجدوى من Hokom | السبب |
|---------|----------------|-------|
| P6 | ممكن (كمزود بيانات) | يقرأ جيومتريا P5 من Hokom |
| P7 | ممكن (كمزود بيانات) | يقرأ جيومتريا P6 |
| P8 | ممكن (كمزود بيانات) | يقرأ جيومتريا P7 |
| P9 | **مستحيل** | يتطلب >=2 كلمة مستقلة لكل منها AmilMamulCandidate مقبول |
| P10–P12 | **مستحيل** | يتطلب P9 كمدخل |

---

## 4. دور Taaqol

**الوظيفة:** طبقة الحكم والترخيص — تُطبّق على كل عبور مرحلي في Hokom.

**التحقق الرئيسي في السياق الحالي:**
- `IfadahCandidate → Action` هي **قفزة محظورة** (FORBIDDEN_LEAP) — القانون الدستوري
- `RelationCandidate` و`RelationClosure`: `hokom_eligibility='FORBIDDEN'` في السجل
- `IfadahCandidate`: `hokom_eligibility='FORBIDDEN'` في السجل
- فشل Taaqol → إغلاق فوري بـ BLOCKED (fail-closed)

---

## 5. البنية المعمارية الصحيحة (الكاملة)

```
┌──────────────────────────────────────────────────────────┐
│                    SALEH/QIYAS                           │
│  run_qiyas.py → PipelineLayers.build()                   │
│                                                          │
│  [نص عربي متعدد الكلمات]                                  │
│       ↓                                                  │
│  SequenceContextTokenizer                                │
│       ↓ (لكل رمز)                                         │
│  P0: UnicodeLayerAdapter                                 │
│  P0: TypedCodePointLayerAdapter                          │
│  P1: LetterIdentityLayerAdapter                          │
│  P1: HarakaFunctionLayerAdapter                          │
│  P1: PositionLayerAdapter                                │
│  P1: ConditionedTypedSequenceLayerAdapter                │
│  P1: SlotLayerAdapter                                    │
│  P2: RegistryProjectionLayerAdapter                      │
│  P3: RootStemLayerAdapter                                │
│  P4: JamidMushtaqLayerAdapter                            │
│  P5: MufradWordLayerAdapter                              │
│  P6: VerbalSignifiedLayerAdapter                         │
│  P7: CompositionReadinessLayerAdapter                    │
│  P8: AmilMamulLayerAdapter          ←─ SentenceUnit لكل كلمة
│       ↓ (جمع >=2 وحدة)                                   │
│  P9: SentenceGeometryLayerAdapter                        │
│  P10: RelationGeometryLayerAdapter                       │
│  P11: IrabGeometryLayerAdapter                           │
│  P12: IfadahSpeechForceLayerAdapter                      │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                      HOKOM                               │
│  hokom_pipeline.py → run_token(token)                    │
│                                                          │
│  [رمز عربي واحد]                                          │
│  NORMALIZE → SEGMENT → NORM_ATOMIC → BOUNDARY           │
│  → ROOT_CAND → PHASE_4A → PHASE_4B → PHASE_4C           │
│  → PHASE_4D → WORD_CLASS → PHASE_5 → TAAQOL_SGA         │
│                                                          │
│  مخرج: MufradWordCandidate (P5) + Taaqol حكم            │
│  ↓                                                       │
│  [اختياريًا: تُمرر جيومتريا P5 إلى Saleh/Qiyas P6–P8]  │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                      TAAQOL                              │
│  TaaqolJudgmentEnforcer                                  │
│  - يحكم على كل بوابة في Hokom (11 بوابة)                │
│  - fail-closed: أي فشل → BLOCKED                        │
│  - IfadahCandidate→Action = FORBIDDEN_LEAP               │
└──────────────────────────────────────────────────────────┘
```

---

## 6. حالة حوكمة الحالة الراهنة

| المتغير | القيمة |
|---------|--------|
| `MACOS_VALIDATION_AUTHORIZED` | `NO` |
| `HOKOM_SCG_P0_P12_CONFORMANCE` | `OPEN` |
| `CLOSURE_VERDICT` | `OPEN` |
| `CANONICAL_REGISTRY_MODEL` | `SET_A` |
| `CANONICAL_REGISTRY_SOURCE_FILE` | `src/qiyas_core/slot_geometry_core/master_registry_seed.py` |
| `CANONICAL_REGISTRY_SOURCE_SYMBOL` | `build_p12_implemented_registry()` |
| `REGISTRY_SOURCE_MISMATCH_RESOLVED` | `YES` |
| `SENTENCE_LEVEL_WITNESS_FOUND` | `NO` |
| `VERIFIED_WITNESS_COUNT` | `0` |
| `CORPUS_ADEQUATE_FOR_P6_P12` | `NO` |
| `SENTENCE_ORCHESTRATOR_FOUND` | `YES (fractal/algebra/Saleh-/run_qiyas.py)` |
| `CANONICAL_RUNNER_STATUS` | `REJECTING — 23 unauthorized paths (HEAD_DIFF_VIOLATION)` |
| `SENTENCE_CORPUS_REQUIRED` | `YES — corpus P9+ coverage = 0/150` |

---

## 7. الإجراءات المطلوبة للإغلاق

1. **إنشاء مستودع جمل عربية** محتوٍ على >=2 كلمة لكل حالة مع تعليقات P8 ذهبية
2. **تشغيل Saleh/Qiyas** `run_qiyas.py` على الجمل للتحقق من P9–P12
3. **ترخيص المسارات** غير المرخصة (23 ملف) عبر تعديل دستوري لمانيفست الإغلاق
4. **لا يُسمح بتعديل** الـ canonical runner أو تخفيف أي معيار للموافقة على الالتزامات الحالية

---

*توليد هذا المستند: HOKOM-SALEH-QIYAS-SCG-CROSS-REPOSITORY-OWNERSHIP-RESOLUTION-07 — القسم 8 + 12*
*التاريخ: 2026-07-26*
*حالة الإغلاق: OPEN*
