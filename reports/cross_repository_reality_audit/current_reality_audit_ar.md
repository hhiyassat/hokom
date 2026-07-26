# تقرير التدقيق الشامل للواقع الحالي والفجوات التكاملية
## HOKOM-SALEH-QIYAS-TAAQOL-CURRENT-REALITY-AND-INTEGRATION-GAP-AUDIT-01

**التاريخ:** 2026-07-26  
**النوع:** تدقيق قراءة فقط — لا تنفيذ، لا تعديل  
**الالتزام:** 912372f (التقارير الأصلية) → تصحيح v2

---

## النتيجة الإجمالية

```
CURRENT_REALITY_AUDIT         = COMPLETE
IMPLEMENTATION_AUTHORIZED     = NO
P0_P12_CLOSURE                = OPEN
OVERALL_HOKOM_PROJECT_CLOSURE = OPEN
```

---

## 1. خطوط الأساس المجمّدة

| المستودع | HEAD | الفرع | الحالة |
|----------|------|-------|--------|
| Hokom | 912372f | main | مجمّد — لا تعديل |
| Saleh/Qiyas | d24f44a | main | مجمّد — قراءة فقط |
| Taaqol (vendor) | 3538173 | — | مجمّد — لا تعديل |
| Arabic Verifier (parent) | c5f19845 | main | مجمّد — قراءة فقط |

---

## 2. الأنظمة الأربعة: الواقع المثبت

### أولًا: Hokom
- خط أنابيب تحليل صرفي وحيد الرمز (single-token)
- 12 مرحلة داخلية / 11 حافة / 11 بوابة `_scg_gate()`
- مخرج Hokom الأعلى: مكافئ P5 (حقول `phase5_result`, `word_class_result`, `final_root`, `final_wazn`, `sga_claim_bundle`) في dict خاص به — **ليس** كائن `MufradWordCandidate` من Saleh/Qiyas
- **السقف الأصلي الصحيح:** `P5_EQUIVALENT` — Hokom لا يُنشئ `AmilMamulCandidate`

### ثانيًا: Saleh/Qiyas
- يملك السجل الكنوني لـ 19 مرشحًا (جميعها `status=implemented`)
- يملك adapters لكل مرشح من P0 إلى P12
- يملك orchestrator في `run_qiyas.py::PipelineLayers` للتسلسل P9–P12
- **لا يستورد Hokom** ولا يستخدم Taaqol الحي — يملك `gamma.py` مستقلًا

### ثالثًا: Taaqol
- `TransitionGate.decide(input_graph: SlotGraph, target_layer: Layer, evidence: EvidenceContract) → TransitionVerdict`
- `gamma(graph: SlotGraph) → GammaResult` — تُستدعى داخليًا من `decide()` فقط
- **مربوط بـ Hokom داخليًا** عبر `sys.path` — لكن **منفصل عن Saleh/Qiyas**

### رابعًا: Arabic Verifier
- مستودع مستقل في `fractal/arabic-july/arabic_verifier/`
- نطاق `entrance_adapter`: P1–P4 فقط
- **معزول** — لا يستورده أي نظام

---

## 3. مصفوفة التكامل الحالية

```
Hokom → Taaqol            SOURCE_CONNECTED
                          (sys.path؛ 11 بوابة داخلية؛ preflight tested؛ macOS غير مُتحقق)

Hokom → Saleh/Qiyas       DISCONNECTED
Saleh/Qiyas → Taaqol      DISCONNECTED (gamma.py موازٍ — ليس Taaqol الحي)
Saleh/Qiyas → Hokom       DISCONNECTED
Arabic Verifier → الجميع  ISOLATED
```

---

## 4. الحواف الكنونية — العدد المُحسوم

| النوع | العدد |
|-------|-------|
| حافة الدخول (ROOT → P0_UNICODE_CANDIDATE) | 1 |
| الحواف الداخلية بين المرشحات | 18 |
| **المجموع الكلي للحواف الكنونية** | **19** |
| حدث الحارس الطرفي (enforce_terminal_guard) | 1 |
| **مجموع أحداث الحكم** | **20** |

قائمة الحواف التسع عشرة:
```
ROOT → P0_UNICODE_CANDIDATE
P0_UNICODE_CANDIDATE → P0_TYPED_CODEPOINT
P0_TYPED_CODEPOINT → P0_GLYPH_CLASSIFICATION
P0_TYPED_CODEPOINT → P1_LETTER_IDENTITY_CARRIER
P0_TYPED_CODEPOINT → P1_HARAKA_MARK_IDENTITY_CARRIER
P0_TYPED_CODEPOINT → P1_CONDITIONED_TYPED_SEQUENCE
P1_CONDITIONED_TYPED_SEQUENCE → P1_POSITION_CARRIER
P1_LETTER_IDENTITY_CARRIER → P1_SLOT_CANDIDATE
P1_SLOT_CANDIDATE → P2_REGISTRY_PROJECTION
P2_REGISTRY_PROJECTION → P3_ROOT_STEM_CLOSURE
P3_ROOT_STEM_CLOSURE → P4_JAMID_MUSHTAQ
P4_JAMID_MUSHTAQ → P5_MUFRAD_WORD_CONTRACTS
P5_MUFRAD_WORD_CONTRACTS → P6_VERBAL_SIGNIFIED_ALONE
P6_VERBAL_SIGNIFIED_ALONE → P7_COMPOSITION_READINESS
P7_COMPOSITION_READINESS → P8_AMIL_MAMUL
P8_AMIL_MAMUL → P9_SENTENCE_GEOMETRY
P9_SENTENCE_GEOMETRY → P10_RELATION_GEOMETRY
P10_RELATION_GEOMETRY → P11_IRAB_GEOMETRY
P11_IRAB_GEOMETRY → P12_IFADAH_SPEECH_FORCE
```

---

## 5. تصحيح سقف Hokom

| الادعاء السابق | التصحيح |
|----------------|---------|
| `HOKOM_CEILING=P8_AMIL_MAMUL` | `HOKOM_NATIVE_CEILING=P5_EQUIVALENT` |
| Hokom يُنشئ AmilMamulCandidate | Hokom **لا يُنشئ** AmilMamulCandidate — Saleh/Qiyas هو المُنشئ |
| P8 متعدد الوحدات | P8 **أحادي الكلمة** — P9 هو أول طبقة تجمع >=2 وحدة |

**P8 الحقيقية:**
- المدخل: `CompositionReadinessCandidate` (لكل كلمة على حدة)
- المُنشئ: `AmilMamulLayerAdapter` في Saleh/Qiyas
- المخرج: إمكانية علاقة هيكلية فقط (`STRUCTURAL_RELATION_POSSIBILITY`) — ليست حكمًا نحويًا
- حدّ الإدراج (ACCEPT): `n_consonants >= 3 AND vowel_count >= 3 AND has_cadence`

---

## 6. اكتشاف gamma.py في Saleh/Qiyas

| المعيار | Taaqol gamma | Saleh/Qiyas gamma |
|---------|-------------|------------------|
| التوقيع | `gamma(graph: SlotGraph)` | `gamma(candidate_type, candidate_fields, ..., layer_spec, target_boundary)` |
| النطاق الدلالي | SlotGraph | حقول المرشح + LayerSpec + TargetBoundary |
| قيم الحالة | نفسها (MINIMALLY_CLOSED / PERFORATED_CLOSED / OPEN / BLOCKED / FORBIDDEN_LEAP) | نفسها |
| التصنيف | **تطبيق موازٍ** — ليس أداة تحويل مرشح |

**السؤال الدستوري:** إذا كان Taaqol هو المرجع الوحيد للحكم، فإن وجود `gamma.py` في Saleh/Qiyas يمثل ازدواجية ملكية دستورية تستدعي قرارًا حوكميًا قبل أي تنفيذ.

---

## 7. حالة الكوربس

| الكوربس | الحالات | البنية | دعم P0–P5 | دعم P6–P12 |
|---------|---------|--------|-----------|------------|
| LCX (Hokom) | 150 | TOKEN_ONLY 100% | أدلة صرفية ✓ | صفر |
| Saleh/Qiyas tests | — | اختبارات وحدة | جزئي | صفر |
| Arabic Verifier | — | لا كوربس | — | — |

```
LCX_TOKEN_EVIDENCE_SUPPORT     = PRESENT
SCG_P0_P5_CANONICAL_GOLD       = NOT_YET_PROVEN
SCG_P6_P12_GOLD                = ABSENT
SENTENCE_LEVEL_WITNESS_FOUND   = NO
VERIFIED_WITNESS_COUNT         = 0
```

---

## 8. حالة الحوكمة

| المتغير | القيمة |
|---------|--------|
| `CANONICAL_RUNNER_STATUS` | REJECTING — 23 مسارًا غير مرخص |
| `CLOSURE_VERDICT` | OPEN |
| `MACOS_VALIDATION_AUTHORIZED` | NO |
| `GOLD_MANIFEST` | ثابت — يستدعي CONSTITUTIONAL_AMENDMENT_ID لأي تغيير |
| `STASH` | stash@{0} — غير مَسوس |

---

## 9. الفجوات المُرتّبة

### P0 — قواطع قبل التنفيذ
1. ✅ حسم عدد الحواف الكنونية: 19 حافة / 20 حدث حكم
2. ✅ حسم P8 وسقف Hokom الحقيقي: P5_EQUIVALENT
3. ✅ حسم `gamma.py`: تطبيق موازٍ (PARALLEL_IMPLEMENTATION)
4. ⏳ قرار حوكمي بشأن ازدواجية `gamma.py`

### P1 — التكامل الضروري
5. عقد typed لتسليم ناتج Hokom إلى Saleh/Qiyas
6. Adapter حي يستهلك ناتج Hokom في Saleh/Qiyas
7. ربط حواف Saleh/Qiyas بـ `TransitionGate.decide()` الحقيقي
8. منع أي فتح للمرشح الهدف قبل حكم Taaqol

### P2 — الجملة والمسار الأعلى
9. كوربس جُملي بـ>=2 كلمة مع gold P8 لكل وحدة
10. تشغيل P6–P12 من أدلة حقيقية
11. شهود حية لـ AmilMamul وSentenceGeometry وRelationGeometry وIrabGeometry وIfadahCandidate

### P3 — Arabic Verifier
12. تحديد claims التي تستدعي ترخيصًا
13. توصيل Arabic Verifier بهذه الادعاءات فقط

---

## 10. ترتيب التنفيذ المقترح

```
1. قرار دستوري: gamma.py الموازي — دمج في Taaqol أو إبقاؤه؟
2. عقد HokomTokenEvidenceBundle (أو ما يعادله) — Hokom→Saleh/Qiyas
3. Adapter حي في Saleh/Qiyas يستهلك العقد
4. ربط Saleh/Qiyas P6–P12 بـ TransitionGate.decide()
5. كوربس جُملي
6. تشغيل run_qiyas.py على الكوربس
7. ترخيص 23 مسارًا في canonical runner
```

---

*توليد: HOKOM-SALEH-QIYAS-TAAQOL-CURRENT-REALITY-AND-INTEGRATION-GAP-AUDIT-01*  
*التاريخ: 2026-07-26*  
*الإصدار: v2 مُصحَّح*  
*CURRENT_REALITY_AUDIT=COMPLETE / IMPLEMENTATION_AUTHORIZED=NO / P0_P12_CLOSURE=OPEN*
