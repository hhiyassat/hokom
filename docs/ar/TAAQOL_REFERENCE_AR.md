# المرجع العربي الرسمي — Taaqol (taaqqul_slot_geometry)

**حالة الوثيقة:** مرجع موازٍ للقراءة فقط — مرحلة التدقيق  
**معرّف التدقيق:** HOKOM-TAAQOL-AUTHORITATIVE-STAGE-INVENTORY-AND-ARABIC-MIRROR-AUDIT-01  
**HEAD:** fe352dd  
**Taaqol vendor commit:** 3538173  

> **تحذير دستوري:** هذه الوثيقة شرحٌ عربي موازٍ. لا تُعدِّل المعرّفات البرمجية (أسماء الأصناف، الدوال، الوحدات، مفاتيح JSON، معرّفات الواجهة العامة).

---

## 1. تعريف Taaqol وغايته

**Taaqol** (`taaqqul_slot_geometry`) نظامٌ جبري مجرَّد يتحكّم في انتقالات تحليل الرموز العربية عبر الطبقات اللغوية. غايته الأساسية:

- فرض **النقاء الدالي**: الدوال تقبل قيمًا وتُعيد قيمًا — لا تحويل للحالة، لا كتابة في السجل داخل دوال النواة.
- ضمان **الانتقالات المشروعة فقط** بين طبقات التحليل.
- تحديد **سقوف الرتبة** لمنع ادعاءات الرتبة غير المشروعة.

---

## 2. الفصل بين ملكية Hokom وملكية Taaqol

| الملك | ما يمتلكه |
|-------|-----------|
| **Hokom** | تحليل اللغة العربية — الطبقات اللغوية الثماني عشرة (SlotSort 0–910) |
| **Taaqol** | الجبر المجرد — SlotGraph، Gamma، عقود الدليل، بوابات الانتقال، دلالاتها الداخلية |

**ثلاثة هياكل مستقلة يجب عدم مزجها:**

1. **طبقات Hokom اللغوية** — معرَّفة في `pipeline/sga/contracts.py` (SlotSort enum، 18 طبقة)
2. **مراحل Taaqol الداخلية** — الخطوات المرتَّبة داخل `gamma()` (10 خطوات) و`TransitionGate.decide()` (6 خطوات)
3. **عمليات الجسر** — مُغلِّفات تنظيم في `pipeline/taaqol_integration/live/bridge.py` تستدعي نواة Taaqol

> **قاعدة تدقيقية:** runtime_active=True على مستوى الرمز يُنسَخ عبر الـ18 صفًا لذلك الرمز. إنه شاهدٌ واحد على مستوى الرمز — وليس 18 شاهدًا مستقلًا على مراحل Taaqol.

---

## 3. قاموس المصطلحات الإنجليزي–العربي

| المعرّف الأصلي | الاسم العربي |
|----------------|--------------|
| `SlotGraph` | الرسم البياني للخانات |
| `SlotState` | حالة الخانة |
| `SlotState.EMPTY` | فارغة |
| `SlotState.FILLED` | مملوءة |
| `SlotState.BROKEN` | مكسورة |
| `Layer` | الطبقة |
| `Layer.TEXT_ENTRY` | إدخال النص |
| `Layer.SLOT` | مستوى الخانة |
| `Layer.CANDIDATE` | مستوى المرشح |
| `Layer.CERTIFICATE` | مستوى الشهادة |
| `GenerationSource` | مصدر التوليد |
| `GenerationSource.DECLARED_ENTRY` | الإدخال المُعلَن |
| `GenerationSource.CANDIDATE` | المرشح |
| `GenerationSource.TRANSITION_VERDICT` | حكم الانتقال |
| `gamma()` | دالة Gamma |
| `GammaResult` | نتيجة Gamma |
| `ClosureState` | حالة الإغلاق |
| `ClosureState.OPEN` | مفتوح |
| `ClosureState.MINIMALLY_CLOSED` | مغلق أدنى |
| `ClosureState.PERFORATED_CLOSED` | مغلق مُثقَّب |
| `ClosureState.BLOCKED` | مانع |
| `ClosureState.INVALID` | غير صالح |
| `ClosureState.FORBIDDEN_LEAP` | قفزة محظورة |
| `TransitionGate` | بوابة الانتقال |
| `TransitionGate.decide()` | دالة القرار |
| `TransitionVerdict` | حكم الانتقال |
| `TransitionState` | حالة الانتقال |
| `TransitionState.APPROVED` | مُوافَق |
| `TransitionState.DEFERRED` | مؤجَّل |
| `TransitionState.BLOCKED` | محجوب |
| `TransitionState.REJECTED` | مرفوض |
| `TransitionState.FORBIDDEN_LEAP` | قفزة محظورة |
| `Rank` | الرتبة |
| `Rank.ZERO` | صفر |
| `Rank.TRACE` | أثر |
| `Rank.CANDIDATE` | مرشح |
| `Rank.HYPOTHESIS` | فرضية |
| `Rank.LICENSED` | مُرخَّص |
| `Rank.STRONG` | قوي |
| `Rank.CERTIFICATE` | شهادة |
| `RankLattice` | شبكة الرتب |
| `RankLattice.meet()` | التقاطع (min) |
| `RankLattice.join()` | الاتحاد (max) |
| `EvidenceContract` | عقد الدليل |
| `EvidenceSource` | مصدر الدليل |
| `ResidualKind` | نوع البقية |
| `Residual` | البقية |
| `ResidualPolicy` | سياسة البقايا |
| `FailureCode` | رمز الفشل |
| `ForbiddenLineRegistry` | سجل الخطوط المحظورة |
| `CANONICAL_REGISTRY` | السجل القانوني |
| `TraceLedger` | دفتر التتبع |
| `TraceEntryCandidate` | مدخل التتبع المرشح |

---

## 4. السجل الحقيقي لمراحل Taaqol

**لا يوجد سجل مراحل أحادي رسمي في Taaqol.**  
`SINGLE_AUTHORITATIVE_STAGE_REGISTRY_FOUND=NO`

الكيانات موزَّعة عبر وحدات مصدر مستقلة:

| السجل الفرعي | الملف المصدر | العدد |
|--------------|--------------|-------|
| البنية الأساسية | `core/slot_graph.py` | 1 (SlotGraph) |
| حالات الخانة | `core/slot_graph.py` | 3 (SlotState) |
| طبقات التجريد | `core/slot_graph.py` | 4 (Layer) |
| مصادر التوليد | `core/slot_graph.py` | 3 (GenerationSource) |
| حالات الإغلاق | `core/closure_state.py` | 6 (ClosureState) |
| أحكام الانتقال | `core/transition_state.py` | 5 (TransitionState) |
| مستويات الرتبة | `core/rank_lattice.py` | 7 (Rank) |
| أنواع البقايا | `core/residual_policy.py` | 5 (ResidualKind) |
| رموز الفشل | `core/failure_taxonomy.py` | 65+ (FailureCode) |
| الخطوط المحظورة | `core/forbidden_lines.py` | 48+12 (CANONICAL_REGISTRY) |
| مراحل LGE | `lge/c1_*.py` إلى `lge/c5_*.py` | 5 (C1–C5) |

---

## 5. عمليات وقت التشغيل

عمليات الجسر الأربع (مُغلِّفات تنظيم في Hokom، **ليست كيانات Taaqol الأصيلة**):

| المعرّف الأصلي | الاسم العربي | الملف | الاستدعاءات | الناجحة | الفاشلة |
|----------------|--------------|-------|-------------|---------|---------|
| `slot_graph_construction` | بناء الرسم البياني للخانات | `bridge.py` | 129 | 128 | 1 |
| `gamma_evaluation` | تقييم Gamma | `bridge.py` | 128 | 128 | 0 |
| `evidence_contract_build` | بناء عقد الدليل | `bridge.py` | 128 | 128 | 0 |
| `transition_gate_decision` | قرار بوابة الانتقال | `bridge.py` | 128 | 128 | 0 |

**لاحظ:** هذه العمليات **مستبعَدة** من عدد الكيانات القابلة للتنفيذ لتجنب الازدواج مع الخطوات المرتَّبة التي تُنظِّمها.

---

## 6. SlotGraph

**المعرّف الأصلي:** `SlotGraph`  
**الاسم العربي:** الرسم البياني للخانات  
**المصدر:** `core/slot_graph.py`

الحامل المركزي الثابت (frozen dataclass). يحتوي على:
- `center` — مركز الخانة
- `slots` — الخانات
- `boundary` — `SlotBoundary`
- `residuals` — tuple من `Residual`
- `rank` — `Rank`
- `output_boundary` — `Layer`
- `generation_source` — `GenerationSource`

**مبدأ الثبات:** SlotGraph لا يُعدَّل في مكانه — يُنشَئ كائن جديد عند كل تحويل.

### حالات الخانة (SlotState)

| المعرّف الأصلي | الاسم العربي | الوصف |
|----------------|--------------|-------|
| `SlotState.EMPTY` | فارغة | الخانة لم تُملأ — غير مانعة |
| `SlotState.FILLED` | مملوءة | شرط للإغلاق الأدنى |
| `SlotState.BROKEN` | مكسورة | تُسبِّب الرفض الفوري في Γ خطوة 4 |

### طبقات التجريد (Layer)

| المعرّف الأصلي | القيمة | الاسم العربي |
|----------------|--------|--------------|
| `Layer.TEXT_ENTRY` | 1 | إدخال النص |
| `Layer.SLOT` | 2 | مستوى الخانة (المُستخدَم في جسر Hokom) |
| `Layer.CANDIDATE` | 3 | مستوى المرشح |
| `Layer.CERTIFICATE` | 4 | مستوى الشهادة (محجوز لـ CertificationGate) |

### مصادر التوليد (GenerationSource)

| المعرّف الأصلي | الاسم العربي | الرتبة المسموحة |
|----------------|--------------|----------------|
| `GenerationSource.DECLARED_ENTRY` | الإدخال المُعلَن | ≤ HYPOTHESIS |
| `GenerationSource.CANDIDATE` | المرشح | ≤ HYPOTHESIS |
| `GenerationSource.TRANSITION_VERDICT` | حكم الانتقال | حتى LICENSED+ |

> **قاعدة:** الوحيد المُرخَّص لرتبة LICENSED أو أعلى هو `TRANSITION_VERDICT`.

---

## 7. Gamma (دالة Γ)

**المعرّف الأصلي:** `gamma()`  
**الاسم العربي:** دالة Gamma  
**المصدر:** `core/gamma.py`  
**النمط:** دالة نقية — 10 خطوات مرتَّبة → `GammaResult`  
**المبدأ:** لا تلمس `TraceLedger` مطلقًا.

ترتيب الخطوات دستوري — لا يجوز تعديله.

| الخطوة | الاسم العربي | الشرط | الفشل → |
|--------|--------------|-------|---------|
| 1 | المركز والهوية | وجود المركز وصحة الهوية | `INVALID` |
| 2 | مرجع التتبع | وجود `TraceRef` في المركز | `INVALID` |
| 3 | المجال والنطاق والحدّ | اكتمال هوية الرسم البياني | `INVALID` |
| 4 | لا خانات مكسورة | أي خانة BROKEN | `INVALID` (فوري) |
| 5 | حدّ طبقة الإخراج | الإخراج ضمن الطبقة المُعلنة | `FORBIDDEN_LEAP` |
| 6 | لا بقايا مخفية | أي `HIDDEN_FORBIDDEN` | `INVALID` |
| 7 | لا بقايا مانعة | أي `BLOCKING` | `BLOCKED` |
| 8 | الخانات المطلوبة مملوءة | كل خانة مطلوبة = FILLED | `OPEN` |
| 9 | سقف الرتبة | الرتبة ≤ `ResidualCeiling` | `FORBIDDEN_LEAP` |
| 10 | حكم الإغلاق | — | `MINIMALLY_CLOSED` أو `PERFORATED_CLOSED` |

**تغطية الفروع من المتن (128 تقييمًا نشطًا):**

| الفرع | الحالة | الشواهد |
|-------|--------|---------|
| خطوة 8 → OPEN | مُشهَد | 7 رموز |
| خطوة 10 → MINIMALLY_CLOSED | مُشهَد (نتيجة فقط) | 50 رمزًا |
| خطوة 10 → PERFORATED_CLOSED | مُشهَد (نتيجة فقط) | 71 رمزًا |
| خطوات 1-7 و9 فروع الرفض | غير مُشهَد | 0 رموز |
| BLOCKED / INVALID / FORBIDDEN_LEAP | غير مُشهَد | 0 رموز |

> **تحذير تغطية — الخطوة 10:** مشاهدة نتيجة `MINIMALLY_CLOSED` أو `PERFORATED_CLOSED` تُثبت أن دالة `gamma()` بلغت الخطوة 10 وأعادت إحدى هاتين القيمتين. لكنها **لا تُثبت** تغطية الخطوة 10 بشاهد دخول وخروج مستقل. لإثبات تغطية الخطوة 10 يلزم: شاهد دخول (الخطوات 1–9 اجتازت جميعًا)، وشاهد خروج (قيمة `ClosureState` موثَّقة بمعرّف تقييم). العقد `TAAQOL-GAMMA-10-STEP-6-OUTCOME-COVERAGE-01` هو الجهة الوحيدة المُخوَّلة بإعلان هذه التغطية.

---

## 8. عقد الدليل

**المعرّف الأصلي:** `EvidenceContract`  
**الاسم العربي:** عقد الدليل  
**المصدر:** `core/evidence_contract.py`

| الكيان | الوصف |
|--------|-------|
| `EvidenceSource` | مصدر دليل واحد (frozen dataclass، 4 حقول) |
| `EvidenceContract` | مجموعة ثابتة من `EvidenceSource` |
| `evidence_rank` | ZERO إذا فارغ؛ min(rank, STRONG) لمصدر واحد؛ join لمصادر متعددة |

**`SINGLE_SOURCE_EVIDENCE_CEILING = STRONG`** — مصدر واحد لا يرفع الرتبة فوق STRONG.

**تغطية المتن:**
- عقد فارغ (no evidence): 55 رمزًا → DEFERRED بـ `GATE_REQUIRED`  
- عقد بمصادر: 73 رمزًا → استمر إلى خطوات البوابة 5 و6 → APPROVED

---

## 9. بوابة الانتقال

**المعرّف الأصلي:** `TransitionGate`  
**الاسم العربي:** بوابة الانتقال  
**المصدر:** `core/transition_gate.py`  
**المثيل في Hokom:** `HOKOM_TAAQOL_GATE = TransitionGate(name="HOKOM_TAAQOL_GATE", gate_rank=Rank.STRONG)`

**`TransitionGate.decide()`** — دالة نقية بـ6 خطوات مرتَّبة → `TransitionVerdict`

| الخطوة | الاسم العربي | الإجراء | النتيجة عند الرفض |
|--------|--------------|---------|------------------|
| 1 | استشارة Γ | تشغيل `gamma()` أولًا | ربط الرفض بـ `_GAMMA_REFUSAL_TO_TRANSITION` |
| 2 | سجل الخطوط المحظورة | `CANONICAL_REGISTRY.find(source, target)` | `FORBIDDEN_LEAP` |
| 3 | ادعاء رتبة غير مُبوَّبة | رتبة > HYPOTHESIS من غير `TRANSITION_VERDICT` | `REJECTED` |
| 4 | حضور الدليل | `evidence.sources` فارغ | `DEFERRED + GATE_REQUIRED` |
| 5 | جلسة الرتبة §8 | `meet(evidence_rank, identity_rank, gate_rank, residual_ceiling)` | — |
| 6 | الموافقة | إصدار `TransitionVerdict(state=APPROVED)` | — |

**`UNGATED_RANK_CEILING = HYPOTHESIS`** — بلا بوابة، الرتبة القصوى هي HYPOTHESIS.  
**`GATE_RANK_CEILING = STRONG`** — مع البوابة، الرتبة القصوى هي STRONG.

**تغطية الفروع من المتن:**

| الفرع | الحالة | الشواهد |
|-------|--------|---------|
| خطوة 1 رفض عبر OPEN→DEFERRED | مُشهَد | 7 رموز |
| خطوة 4 لا دليل→DEFERRED | مُشهَد | 48 رمزًا |
| خطوة 4..6 بدليل→APPROVED | مُشهَد (نتيجة فقط) | 73 رمزًا |
| خطوة 2 رفض (FORBIDDEN_LEAP) | غير مُشهَد | 0 |
| خطوة 3 رفض (REJECTED) | غير مُشهَد | 0 |

> **تحذير تغطية — الخطوات 4 و5 و6:** مشاهدة `TransitionState.APPROVED` تُثبت أن البوابة اجتازت الخطوات 1–6 وأصدرت موافقة. لكنها **لا تُثبت** تغطية كل خطوة بشاهد دخول وخروج مستقل. لإثبات التغطية الكاملة للخطوات الست يلزم: شاهد دخول لكل خطوة، وشاهد خروج بمعرّف تقييم وقيمة حكم. العقد `TAAQOL-TRANSITION-GATE-6-STEP-5-STATE-COVERAGE-01` هو الجهة الوحيدة المُخوَّلة بإعلان هذه التغطية.

---

## 10. الحالات النهائية

### حالات Gamma النهائية

| المعرّف الأصلي | الاسم العربي | نهائي؟ | شاهد في المتن؟ |
|----------------|--------------|--------|----------------|
| `ClosureState.BLOCKED` | مانع | نعم | لا |
| `ClosureState.INVALID` | غير صالح | نعم | لا |
| `ClosureState.FORBIDDEN_LEAP` | قفزة محظورة | نعم | لا |
| `ClosureState.OPEN` | مفتوح | لا (قابل للمعالجة) | نعم (7 رموز) |

### حالات بوابة الانتقال النهائية

| المعرّف الأصلي | الاسم العربي | نهائي؟ | شاهد في المتن؟ |
|----------------|--------------|--------|----------------|
| `TransitionState.REJECTED` | مرفوض | نعم | لا |
| `TransitionState.FORBIDDEN_LEAP` | قفزة محظورة | نعم | لا |
| `TransitionState.BLOCKED` | محجوب | نعم | لا |
| `TransitionState.DEFERRED` | مؤجَّل | لا (يتطلب بوابة إضافية) | نعم (55 رمزًا) |

---

## 11. الأحكام

### أحكام Gamma (ClosureState — 6 قيم)

| المعرّف الأصلي | الاسم العربي | شواهد المتن |
|----------------|--------------|-------------|
| `ClosureState.OPEN` | مفتوح | 7 رموز |
| `ClosureState.MINIMALLY_CLOSED` | مغلق أدنى | 50 رمزًا |
| `ClosureState.PERFORATED_CLOSED` | مغلق مُثقَّب | 71 رمزًا |
| `ClosureState.BLOCKED` | مانع | 0 |
| `ClosureState.INVALID` | غير صالح | 0 |
| `ClosureState.FORBIDDEN_LEAP` | قفزة محظورة | 0 |

### أحكام بوابة الانتقال (TransitionState — 5 قيم)

| المعرّف الأصلي | الاسم العربي | شواهد المتن |
|----------------|--------------|-------------|
| `TransitionState.APPROVED` | مُوافَق | 73 رمزًا |
| `TransitionState.DEFERRED` | مؤجَّل | 55 رمزًا |
| `TransitionState.BLOCKED` | محجوب | 0 |
| `TransitionState.REJECTED` | مرفوض | 0 |
| `TransitionState.FORBIDDEN_LEAP` | قفزة محظورة | 0 |

---

## 12. الانتقالات المسموحة

**المصدر:** `core/forbidden_lines.py — CANONICAL_REGISTRY`

السجل يُعرِّف الانتقالات **المحظورة** لا المسموحة. يشمل:
- 48 صفًا لقفزات الطبقات (29 قانونية + 13 ما قبل نص + 6 متسلسلة)
- 12 صفًا لنقل المصطلحات (السبب/القياس)

**`CANONICAL_REGISTRY`** — أقرب شيء إلى سجل انتقال رسمي في Taaqol. لم يُستدعَ في المتن الحالي (لا FORBIDDEN_LEAP مُشهَد).

---

## 13. التوقف المبكر

**التعريف في سياق Hokom:** 96 رمزًا تتوقف قبل الطبقة 70 (INFLECTIONAL) بسبب عقد `inflection_skipped`.

**تأثيره على Taaqol:** الجسر يُنتج SlotGraph بخانات أقل لتلك الرموز. gamma() تُقيَّم على SlotGraph ناقص خانات الإعراب. هذا سلوك صحيح — ليس إخفاقًا.

**الطبقات المُتَخطّاة لـ96 رمزًا:**
- INFLECTIONAL (70)، BAB (100)، MASDAR (110)، DERIVATIVE (120)، PARADIGM (140) → SKIPPED_BY_CONTRACT
- RADICAL (80)، PATTERN (90) → SKIPPED_BY_CONTRACT (76–77 رمزًا)

---

## 14. الفشل المغلق

**المعرّف الأصلي:** `FailureCode`  
**الاسم العربي:** رمز الفشل  
**المصدر:** `core/failure_taxonomy.py`

65+ رمز فشل موزَّعة على 13 فئة. المُشهَد في المتن:
- `SEGMENTATION_NO_LEXICAL_HOST` — الرمز الوحيد الذي أخفق في `slot_graph_construction` (1 رمز، مسار clitic_only_gate)

---

## 15. البقايا

**المعرّف الأصلي:** `Residual`  
**الاسم العربي:** البقية  
**المصدر:** `core/residual_policy.py`

### أنواع البقايا (ResidualKind)

| المعرّف الأصلي | الاسم العربي | سقف الرتبة | مانع؟ |
|----------------|--------------|------------|-------|
| `ResidualKind.BLOCKING` | مانعة | ZERO | نعم |
| `ResidualKind.HIDDEN_FORBIDDEN` | مخفية محظورة | ZERO | نعم |
| `ResidualKind.DEFERRABLE` | قابلة للتأجيل | HYPOTHESIS | لا |
| `ResidualKind.NON_BLOCKING` | غير مانعة | CERTIFICATE | لا |
| `ResidualKind.EXPLANATORY` | تفسيرية | CERTIFICATE | لا |

**`PERFORATING_KINDS`** = {BLOCKING, HIDDEN_FORBIDDEN, DEFERRABLE} — البقايا التي تُثقِّب الإغلاق.

---

## 16. علاقة مراحل Taaqol بطبقات Hokom

**المبدأ الدستوري:** لا يوجد تطابق مباشر بين طبقات Hokom الـ18 ومراحل Taaqol الداخلية. العلاقة عبر الجسر فقط.

| تصنيف طبقة Hokom | العدد | أمثلة |
|------------------|-------|--------|
| `HOKOM_NATIVE_LINGUISTIC_LAYER` | 6 | SURFACE_IDENTITY، NORMALIZATION، PHONOLOGICAL، SEGMENTATION، ARTICLE، LEXICAL_FUNCTIONAL |
| `BRIDGE_PROJECTION` | 7 | BOUNDARY، WORD_CLASS، INFLECTIONAL، RADICAL، PATTERN، MORPHOSYNTAX، EVIDENCE |
| `CONTRACT_DERIVED_LAYER` | 4 | BAB، MASDAR، DERIVATIVE، PARADIGM |
| `REPORT_ONLY_SYNTHETIC_LAYER` | 1 | RESIDUAL |
| `TAAQOL_NATIVE_STAGE` | 0 | — (لا توجد طبقة Hokom هي مرحلة Taaqol أصيلة) |

**ملاحظة حاسمة:** طبقة EVIDENCE (900) في تقرير Hokom تُظهر layer_state=NOT_REACHED لكل 129 رمزًا. هذا لا يعني أن `evidence_contract_build` لم تُنفَّذ — بل نُفِّذت لـ128 رمزًا نشطًا. الطبقة 900 هي إسقاط تقرير، وليست شاهدًا على تنفيذ عملية Taaqol.

---

## 17. شبكة الرتب (RankLattice)

**المعرّف الأصلي:** `Rank`  
**المصدر:** `core/rank_lattice.py`

| المعرّف الأصلي | القيمة | الاسم العربي |
|----------------|--------|--------------|
| `Rank.ZERO` | 0 | صفر |
| `Rank.TRACE` | 1 | أثر |
| `Rank.CANDIDATE` | 2 | مرشح |
| `Rank.HYPOTHESIS` | 3 | فرضية |
| `Rank.LICENSED` | 4 | مُرخَّص |
| `Rank.STRONG` | 5 | قوي |
| `Rank.CERTIFICATE` | 6 | شهادة |

- **`meet()`** = min(*ranks) — التقاطع
- **`join()`** = max(*ranks) — الاتحاد
- **`UNGATED_RANK_CEILING`** = HYPOTHESIS (3)
- **`GATE_RANK_CEILING`** = STRONG (5)

---

## 18. تقييم التغطية الرسمي

### تغطية الكيانات القابلة للتنفيذ

| المقياس | القيمة |
|---------|--------|
| `EXECUTABLE_ENTITY_COUNT` | 21 (مُشتق من CSV) |
| `GAMMA_ORDERED_STEP_COUNT` | 10 |
| `TRANSITION_GATE_ORDERED_STEP_COUNT` | 6 |
| `LGE_RUNTIME_STAGE_COUNT` | 5 |
| `EXECUTABLE_COUNT_RECONCILED` | YES |
| `EXECUTABLE_COUNT_DIVERGENCE` | 0 |

### تغطية الطبقات اللغوية (مُشتقّة من CSV)

| المقياس | القيمة |
|---------|--------|
| `HOKOM_LAYERS_FULLY_EXECUTED_FOR_ALL_TOKENS` | 4 (SURFACE_IDENTITY، NORMALIZATION، SEGMENTATION، BOUNDARY) |
| `HOKOM_LAYERS_WITH_ANY_EXECUTION_WITNESS` | 9 (4 كاملة + 5 جزئية) |
| `HOKOM_LAYERS_WITHOUT_EXECUTION_WITNESS` | 9 |

### تغطية Gamma (نتائج مقابل فروع)

| المقياس | القيمة |
|---------|--------|
| `GAMMA_CLOSURE_STATE_COUNT` | 6 |
| `GAMMA_CLOSURE_STATES_WITNESSED` | 3 (OPEN، MINIMALLY_CLOSED، PERFORATED_CLOSED) |
| `GAMMA_CLOSURE_STATE_COVERAGE` | 3/6 — PARTIAL |
| `GAMMA_ORDERED_STEP_COVERAGE` | NOT_PROVEN (خطوات الرفض لـ 1-7 و9 غير مُشهَدة) |
| `GAMMA_DECISION_PATH_COVERAGE` | NOT_PROVEN (الأثر لا يكشف الفرع الداخلي لكل خطوة) |

### تغطية بوابة الانتقال (نتائج مقابل فروع)

| المقياس | القيمة |
|---------|--------|
| `TRANSITION_STATE_COUNT` | 5 |
| `TRANSITION_STATES_WITNESSED` | 2 (APPROVED×73، DEFERRED×55) |
| `TRANSITION_STATE_COVERAGE` | 2/5 — PARTIAL |
| `TRANSITION_GATE_ORDERED_STEP_COVERAGE` | NOT_PROVEN (خطوتا الرفض 2 و3 غير مُشهَدتان) |
| `TRANSITION_GATE_DECISION_PATH_COVERAGE` | NOT_PROVEN |

### عمليات وقت التشغيل الأساسية

| المقياس | القيمة |
|---------|--------|
| `CORE_RUNTIME_OPERATION_COUNT` | 4 |
| `CORE_RUNTIME_OPERATIONS_INVOKED` | 4 |
| `LGE_RUNTIME_STAGE_COUNT` | 5 |
| `LGE_RUNTIME_STAGES_USED_BY_HOKOM` | 0 |

### الأحكام الدستورية النهائية

| المقياس | الحكم |
|---------|-------|
| `ALL_HOKOM_REPORT_LAYERS_REPRESENTED` | YES |
| `ALL_HOKOM_REPORT_LAYERS_EXECUTED` | NO |
| `ALL_TAAQOL_CORE_RUNTIME_OPERATIONS_INVOKED` | YES |
| `ALL_TAAQOL_GAMMA_OUTCOMES_COVERED` | NO |
| `ALL_TAAQOL_GAMMA_ORDERED_STEPS_COVERED` | NOT_PROVEN |
| `ALL_TAAQOL_GAMMA_DECISION_PATHS_COVERED` | NOT_PROVEN |
| `ALL_TAAQOL_TRANSITION_STATES_COVERED` | NO |
| `ALL_TAAQOL_TRANSITION_GATE_ORDERED_STEPS_COVERED` | NOT_PROVEN |
| `ALL_TAAQOL_TRANSITION_GATE_DECISION_PATHS_COVERED` | NOT_PROVEN |
| `ALL_TAAQOL_LGE_RUNTIMES_COVERED` | NO |
| `ALL_TAAQOL_EXECUTABLE_PATHS_COVERED` | NO |
| `ALL_TAAQOL_WITHOUT_EXCEPTION_COVERED` | NO |
| `TRACKED_WORKTREE_STATUS` | CLEAN |
| `UNTRACKED_AUDIT_FILE_COUNT` | 4 |
| `WORKTREE_STATUS` | DIRTY_UNTRACKED_DOCUMENTATION_ONLY |
| `CLOSURE_VERDICT` | **OPEN_PENDING_CATEGORY_SPECIFIC_COVERAGE_TESTS** |
