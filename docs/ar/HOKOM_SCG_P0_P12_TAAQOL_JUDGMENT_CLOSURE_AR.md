# HOKOM-SCG-P0-P12-CANONICAL-CONFORMANCE-OWNERSHIP-AND-TAAQOL-JUDGMENT-CLOSURE-01

---

```
DOCUMENT_TYPE          : EXECUTION_MANDATE
LANGUAGE               : AR
BASELINE_STATUS        : APPROVED_FOR_EXECUTION
CLOSURE_STATUS         : OPEN
TAQOOL_JUDGMENT_REQUIRED : YES
CANONICAL_CANDIDATE_COUNT : 19
CANONICAL_LEVEL_RANGE  : P0-P12
P13_ALLOWED            : NO
```

---

## 1. الهدف والنطاق

يحكم هذا التفويض مسار المرشحين SCG P0–P12 بالكامل.
يغطي تسعة عشر مرشحاً كنونيكالياً من `UnicodeCandidate` إلى `IfadahCandidate`، ويضمن:

1. إشباع عقود كل مرشح من المرشحين التسعة عشر بدون نسخ المحركات أو ازدواج الملكية.
2. أن كل انتقال في المسار P0→P12 يُحكم عليه بواسطة Taaqol حكماً حياً (**NO_CANONICAL_CANDIDATE_TRANSITION_WITHOUT_LIVE_TAAQOL_JUDGMENT**).
3. الفصل الصارم بين الطبقات الثلاث: طبقة Hokom اللغوية، وبيئة Taaqol التجريدية، وجسر الأوركسترا.

---

## 2. المرشحون التسعة عشر الكنونيكاليون (P0–P12)

| الرمز | المرشح | المستوى | المالك |
|-------|--------|---------|--------|
| P0 | `UnicodeCandidate` | P0 | HOKOM_NATIVE_OWNER |
| P1 | `NormalizationCandidate` | P1 | HOKOM_NATIVE_OWNER |
| P2 | `SegmentationCandidate` | P2 | HOKOM_NATIVE_OWNER |
| P3 | `BoundaryCandidate` | P3 | HOKOM_NATIVE_OWNER |
| P4a | `PatternCandidate` | P4a | SALEH_QIYAS_CANONICAL_OWNER |
| P4b | `BabCandidate` | P4b | SALEH_QIYAS_CANONICAL_OWNER |
| P5 | `InflectionCandidate` | P5 | HOKOM_NATIVE_OWNER |
| P6 | `WordClassCandidate` | P6 | HOKOM_NATIVE_OWNER |
| P7 | `RadicalCandidate` | P7 | ARABIC_VERIFIER_CANONICAL_OWNER |
| P8 | `MasdarCandidate` | P8 | SALEH_QIYAS_CANONICAL_OWNER |
| P9 | `DerivativeCandidate` | P9 | SALEH_QIYAS_CANONICAL_OWNER |
| P10 | `EvidenceCandidate` | P10 | TAAQOL_ABSTRACT_GATE_OWNER |
| P11 | `ResidualCandidate` | P11 | TAAQOL_ABSTRACT_GATE_OWNER |
| P12 | `IfadahCandidate` | P12 | HOKOM_NATIVE_OWNER |
| — | `MorphoSyntaxCandidate` | bridge | BRIDGE_ADAPTER_OWNED_BY_HOKOM |
| — | `ParadigmCandidate` | bridge | BRIDGE_ADAPTER_OWNED_BY_HOKOM |
| — | `PhonologicalCandidate` | derived | HOKOM_NATIVE_OWNER |
| — | `LexicalFunctionalCandidate` | derived | HOKOM_NATIVE_OWNER |
| — | `ArticleCandidate` | derived | HOKOM_NATIVE_OWNER |

**إجمالي المرشحين الكنونيكاليين: 19 (P0–P12 + الجسور والمشتقات)**
**P13_ALLOWED: NO**

---

## 3. سلطة Taaqol الحاكمة على المسار كله

### 3.1 القاعدة الدستورية

```
NO_CANONICAL_CANDIDATE_TRANSITION_WITHOUT_LIVE_TAAQOL_JUDGMENT
```

لا يجوز لأي انتقال بين مرشحَين متتاليين في مسار P0→P12 أن يتم بدون استدعاء Taaqol حياً (`gamma()` + `TransitionGate.decide()`). المحلي المباشر محظور.

### 3.2 ما يملكه Taaqol

Taaqol يملك حصرياً:

- `gamma()` — التقييم الهيكلي للـ SlotGraph (10 خطوات مرتّبة)
- `TransitionGate.decide()` — قرار قبول/رفض/تأجيل الانتقال (6 خطوات مرتّبة)
- `ForbiddenLineRegistry` — سجل الانتقالات المحظورة
- `Rank` + `ResidualKind` — سياسة حد الرتبة والمتبقيات
- `ClosureState` + `TransitionState` — الحالة الناتجة عن كل حكم

### 3.3 ما لا يملكه Taaqol

Taaqol **لا** يملك:

- أي منطق لغوي عربي (P0–P6، P8–P9، P12)
- أي نسخة من محركات Saleh/Qiyas أو Arabic Verifier
- أي تنفيذ لـ LGE (مراحل C1–C5 مستقلة عن جسر Hokom)

### 3.4 عقد الجسر لكل انتقال

كل انتقال `PX → PX+1` يجب أن يحمل:

```
taaqol_judgment_required  : YES
taaqol_request_mapping    : <حقول SlotGraph المرسلة>
taaqol_verdict_mapping    : <حقل TransitionState المستقبَل>
```

### 3.5 شروط الحكم

| حالة `TransitionState` | سلوك الجسر |
|----------------------|------------|
| `APPROVED` | تمرير المرشح للمرحلة التالية |
| `DEFERRED` | تعليق الانتقال + تسجيل الكود |
| `BLOCKED` | وقف الانتقال + إعادة BLOCKED |
| `REJECTED` | حذف المرشح من المسار |
| `FORBIDDEN_LEAP` | رفع خطأ دستوري — لا يصل الإنتاج هنا |

### 3.6 مبدأ FAIL_CLOSED

إذا أخفق استدعاء Taaqol بأي استثناء:
- الانتقال **محظور** (FAIL_CLOSED)
- لا silent fallback
- لا محلي بديل
- يُسجَّل الخطأ ويُوقف المرشح

### 3.7 الحرص الحالي (DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT)

عدد الحواف الكنونيكالية **مُكتشَف ديناميكياً** من مصدر Saleh/Qiyas — لا يُثبَّت يدوياً. المتطلب: عدد الحواف المُكتشَفة = عدد الحواف المُحكوم عليها بـ Taaqol.

```
DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT : <discovered_at_runtime>
TRANSITIONS_WITHOUT_TAAQOL_JUDGMENT        : 0   (required)
LOCAL_TRANSITION_DECISIONS                 : 0   (required)
```

### 3.8 تقرير إثبات الحكم الإلزامي

كل تشغيل كنونيكالي ينتج:

```
taaqol_transition_judgment_matrix:
  edge_id            : PX→PY
  source_candidate   : <class>
  target_candidate   : <class>
  taaqol_called      : YES|NO
  gamma_closure_state: <ClosureState>
  gate_verdict       : <TransitionState>
  failure_code       : <FailureCode|None>
```

### 3.9 اختبارات الحكم الإلزامية (17 تأكيداً)

```python
# 1.  كل حافة في المسار تستدعي Taaqol
assert all(e.taaqol_called for e in matrix)

# 2.  APPROVED → المرشح التالي موجود في المخرجات
assert all(e.target_present for e in matrix if e.gate_verdict == "APPROVED")

# 3.  DEFERRED → يُسجَّل failure_code ولا يُحذف المرشح
assert all(e.failure_code is not None for e in matrix if e.gate_verdict == "DEFERRED")

# 4.  BLOCKED → المسار يتوقف عند هذه الحافة
assert all(e.pipeline_halted for e in matrix if e.gate_verdict == "BLOCKED")

# 5.  REJECTED → المرشح لا يظهر في PX+1
assert all(not e.target_present for e in matrix if e.gate_verdict == "REJECTED")

# 6.  FORBIDDEN_LEAP → لا يصل الإنتاج هنا (لا حافة من هذا النوع في corpus)
assert all(e.gate_verdict != "FORBIDDEN_LEAP" for e in matrix)

# 7.  FAIL_CLOSED: استثناء Taaqol → وقف لا fallback
assert all(not e.fallback_used for e in matrix)

# 8.  لا حافة محلية (بدون Taaqol)
assert all(e.taaqol_called for e in matrix)

# 9.  عدد الحواف المُكتشَفة = عدد الحواف المُحكوم عليها
assert len(matrix) == discovered_edge_count

# 10. TRANSITIONS_WITHOUT_TAAQOL_JUDGMENT == 0
assert sum(1 for e in matrix if not e.taaqol_called) == 0

# 11. LOCAL_TRANSITION_DECISIONS == 0
assert local_decisions == 0

# 12. gamma_closure_state ليست None لأي حافة
assert all(e.gamma_closure_state is not None for e in matrix)

# 13. gate_verdict ليست None لأي حافة
assert all(e.gate_verdict is not None for e in matrix)

# 14. ClosureState حقيقية (ليست mock)
assert all(isinstance(e.gamma_closure_state, ClosureState) for e in matrix)

# 15. TransitionState حقيقية (ليست mock)
assert all(isinstance(e.gate_verdict, TransitionState) for e in matrix)

# 16. لا يوجد مسار يصل P12 بدون حكم Taaqol على جميع حوافه السابقة
for path in all_paths_to_p12:
    assert all(e.taaqol_called for e in path)

# 17. التقرير taaqol_transition_judgment_matrix مُنشأ وصالح
assert matrix is not None and len(matrix) > 0
```

---

## 4. نموذج الملكية (Ownership Model)

| النوع | الرمز | المعنى |
|-------|-------|--------|
| مالك Hokom الأصيل | `HOKOM_NATIVE_OWNER` | منطق Hokom الداخلي، لا تبعية خارجية |
| مالك Saleh/Qiyas | `SALEH_QIYAS_CANONICAL_OWNER` | يستدعي عبر واجهة؛ لا نسخ للتنفيذ |
| مالك Arabic Verifier | `ARABIC_VERIFIER_CANONICAL_OWNER` | يستدعي عبر واجهة؛ لا نسخ للمنطق |
| مالك Taaqol | `TAAQOL_ABSTRACT_GATE_OWNER` | يستدعي gamma + gate؛ لا منطق لغوي |
| جسر الأوركسترا | `BRIDGE_ADAPTER_OWNED_BY_HOKOM` | ORCHESTRATION_WRAPPER فقط |
| فجوة غير مملوكة | `UNOWNED_GAP` | يجب إغلاقها قبل الإنتاج |
| نسخة قديمة مكررة | `LEGACY_DUPLICATE` | يجب حذفها |

---

## 5. عقود المرشحين التسعة عشر

### P0 — UnicodeCandidate

```
OWNER              : HOKOM_NATIVE_OWNER
INPUT              : raw surface string
OUTPUT             : Unicode-normalized surface
TAAQOL_JUDGMENT    : YES (حافة P0→P1)
CONTRACT           :
  - تطبيع Unicode NFC/NFKC حسب السياسة
  - لا تعديل على الجذر أو الصرف
  - CLAIM_KEY حتمي وفريد
FORBIDDEN          :
  - لا fallback صامت على تطبيع غير مدعوم
  - لا تعديل على وزن الكلمة
```

### P1 — NormalizationCandidate

```
OWNER              : HOKOM_NATIVE_OWNER
INPUT              : UnicodeCandidate.surface
OUTPUT             : normalized surface (SHADDA-aware)
TAAQOL_JUDGMENT    : YES (حافة P1→P2)
CONTRACT           :
  - معالجة SHADDA في النطاق U+0640–U+065F
  - لا إزالة لحروف العلة إلا بعقد صريح
FORBIDDEN          :
  - لا تحويل للتشكيل يؤثر على الجذر
```

### P2 — SegmentationCandidate

```
OWNER              : HOKOM_NATIVE_OWNER
INPUT              : NormalizationCandidate.surface
OUTPUT             : (proclitics, host, enclitics)
TAAQOL_JUDGMENT    : YES (حافة P2→P3)
CONTRACT           :
  - تسلسل الـproclitics والـenclitics دقيق
  - HOST_SURFACE_PRESERVED
  - NO_ARTICLE_REATTACHMENT_ERROR
  - CLAIM_KEY_DETERMINISTIC
  - TYPED_BUNDLE_ONLY; NO_SILENT_FALLBACK
FORBIDDEN          :
  - لا دمج التحليل اللغوي في طبقة التقطيع
```

### P3 — BoundaryCandidate

```
OWNER              : HOKOM_NATIVE_OWNER
INPUT              : SegmentationCandidate
OUTPUT             : boundary markers (start/end/internal)
TAAQOL_JUDGMENT    : YES (حافة P3→P4a)
CONTRACT           :
  - ENCLOSING_SURFACE_PROVENANCE
  - حدود واضحة تفصل المقطعيات
FORBIDDEN          :
  - لا قرار لغوي في هذه الطبقة
```

### P4a — PatternCandidate (Saleh/Qiyas)

```
OWNER              : SALEH_QIYAS_CANONICAL_OWNER
INPUT              : BoundaryCandidate.host
OUTPUT             : wazn + bab_id + form_family
TAAQOL_JUDGMENT    : YES (حافة P4a→P4b)
CONTRACT           :
  - يستدعي محرك Saleh/Qiyas عبر الواجهة فقط
  - لا نسخ للتنفيذ داخل Hokom
  - p4a_wazn + bab_id حتميان ومُدققان
FORBIDDEN          :
  - لا تنفيذ صرفي محلي
  - لا نسخ منطق Saleh إلى Hokom
```

### P4b — BabCandidate (Saleh/Qiyas)

```
OWNER              : SALEH_QIYAS_CANONICAL_OWNER
INPUT              : PatternCandidate
OUTPUT             : bab details + augmentation markers
TAAQOL_JUDGMENT    : YES (حافة P4b→P5)
CONTRACT           :
  - p4b:attempted مُسجَّل في evidence
  - تفاصيل الباب مشتقة من Saleh/Qiyas
FORBIDDEN          :
  - لا تخمين للباب بدون استدعاء Saleh
```

### P5 — InflectionCandidate

```
OWNER              : HOKOM_NATIVE_OWNER
INPUT              : PatternCandidate + BabCandidate
OUTPUT             : feature bundle (tense, person, number, gender, voice, mood, form)
TAAQOL_JUDGMENT    : YES (حافة P5→P6)
CONTRACT           :
  - _has_imperfect_prefix() مع حراسة Form VI
  - identify_tense() مع حراسة الثنوي
  - extract_all_features() مع المطابقة الجمعية
  - morphology_surface (الضمائر مجرّدة) للاستخلاص في SEGMENTED
FORBIDDEN          :
  - لا إعادة فتح عقد SHADDA
  - لا hard-coded token list
  - لا تخفيض الـthresholds
```

### P6 — WordClassCandidate

```
OWNER              : HOKOM_NATIVE_OWNER
INPUT              : InflectionCandidate
OUTPUT             : FI3L | ISM | HARF | NOT_APPLICABLE
TAAQOL_JUDGMENT    : YES (حافة P6→P7)
CONTRACT           :
  - خطوات 1–9 كما في engine.py
  - حارس الـelative (bab_id=BAB_FORM_IV + p4a_wazn=AF3AL + C2=FATHA)
  - 8b/8c (imperative + lam al-amr) قبل _p4a_ok gate
  - Step 9b للمضارع على no_morphology_path
FORBIDDEN          :
  - لا إجبار على LICENSED
  - لا حكم محلي بديل عن Taaqol
```

### P7 — RadicalCandidate (Arabic Verifier)

```
OWNER              : ARABIC_VERIFIER_CANONICAL_OWNER
INPUT              : WordClassCandidate
OUTPUT             : root (C1–C4) + weak class
TAAQOL_JUDGMENT    : YES (حافة P7→P8)
CONTRACT           :
  - يستدعي Arabic Verifier عبر الواجهة
  - weak_class حتمي ومُدقَّق
  - لا نسخ المنطق داخل Hokom
FORBIDDEN          :
  - لا نسخ Arabic Verifier إلى Hokom
  - لا إضافة HR2S dependency
```

### P8 — MasdarCandidate (Saleh/Qiyas)

```
OWNER              : SALEH_QIYAS_CANONICAL_OWNER
INPUT              : RadicalCandidate
OUTPUT             : masdar + masdar weight
TAAQOL_JUDGMENT    : YES (حافة P8→P9)
CONTRACT           :
  - يستدعي Saleh/Qiyas عبر الواجهة
  - لا إعادة فتح عقد MASDAR
FORBIDDEN          :
  - MASDAR_REOPENING = FORBIDDEN
```

### P9 — DerivativeCandidate (Saleh/Qiyas)

```
OWNER              : SALEH_QIYAS_CANONICAL_OWNER
INPUT              : MasdarCandidate
OUTPUT             : derivative forms + provenance
TAAQOL_JUDGMENT    : YES (حافة P9→P10)
CONTRACT           :
  - DERIVATIVES_REOPENING = FORBIDDEN
  - AT_LEAST_ONE_OF_H11_H15_TYPED_IF_ANALYSIS_REACHES_DERIVATION
  - PROVENANCE_REQUIRED
FORBIDDEN          :
  - لا نسخ منطق الاشتقاق داخل Hokom
```

### P10 — EvidenceCandidate (Taaqol)

```
OWNER              : TAAQOL_ABSTRACT_GATE_OWNER
INPUT              : DerivativeCandidate
OUTPUT             : EvidenceContract (rank + source + §8 coherence)
TAAQOL_JUDGMENT    : YES (الطبقة هي Taaqol نفسها)
CONTRACT           :
  - SINGLE_SOURCE_EVIDENCE_CEILING = STRONG
  - §8 law: meet() للمصادر المتعددة
  - لا ترقية فوق المدخلات
FORBIDDEN          :
  - DEFERRED_TO_LICENSED_WITHOUT_EVIDENCE = FORBIDDEN
```

### P11 — ResidualCandidate (Taaqol)

```
OWNER              : TAAQOL_ABSTRACT_GATE_OWNER
INPUT              : EvidenceCandidate
OUTPUT             : ResidualBundle (kind + cap + perforating flag)
TAAQOL_JUDGMENT    : YES (الطبقة هي Taaqol نفسها)
CONTRACT           :
  - BLOCKING + HIDDEN_FORBIDDEN → cap = ZERO
  - DEFERRABLE → cap = HYPOTHESIS
  - NON_BLOCKING + EXPLANATORY → cap = CERTIFICATE
  - PERFORATING_KINDS = {NON_BLOCKING, DEFERRABLE, EXPLANATORY}
FORBIDDEN          :
  - لا silent fallback على kind غير معروف
```

### P12 — IfadahCandidate

```
OWNER              : HOKOM_NATIVE_OWNER
INPUT              : ResidualCandidate
OUTPUT             : final verdict (LICENSED | DEFERRED | BLOCKED | RESIDUAL | AMBIGUOUS)
TAAQOL_JUDGMENT    : YES (حافة P11→P12 محكومة بـ Taaqol؛ P12 هو المخرج النهائي)
CONTRACT           :
  - لا يُجبر الحكم على LICENSED
  - verdict مشتق من TransitionState الفعلية
  - لا تعديل على gold بدون CONSTITUTIONAL_AMENDMENT_ID
FORBIDDEN          :
  - P13_ALLOWED = NO
  - لا امتداد للمسار بعد P12
```

---

## 6. متطلبات التغطية الاختبارية لكل مرشح

لكل مرشح من التسعة عشر يجب أن تتوفر:

| الاختبار | المعنى |
|---------|--------|
| `INCOMING_TAAQOL_JUDGMENT_TEST` | تأكيد أن Taaqol يُستدعى قبل قبول المرشح |
| `OUTGOING_TAAQOL_JUDGMENT_TEST` | تأكيد أن Taaqol يُستدعى قبل التمرير للمرحلة التالية |
| `FAIL_CLOSED_TEST` | تأكيد أن استثناء Taaqol يوقف الانتقال (لا fallback) |
| `POST_TERMINAL_GUARD_TEST` | تأكيد أن لا انتقال بعد BLOCKED/REJECTED |

---

## 7. مصفوفة التغطية الإجمالية

| المرشح | INCOMING_TAAQOL | OUTGOING_TAAQOL | FAIL_CLOSED | POST_TERMINAL | حالة |
|--------|----------------|----------------|-------------|---------------|------|
| P0 UnicodeCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P1 NormalizationCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P2 SegmentationCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P3 BoundaryCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P4a PatternCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P4b BabCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P5 InflectionCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P6 WordClassCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P7 RadicalCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P8 MasdarCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P9 DerivativeCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| P10 EvidenceCandidate | N/A (Taaqol) | REQUIRED | REQUIRED | N/A | OPEN |
| P11 ResidualCandidate | N/A (Taaqol) | REQUIRED | REQUIRED | N/A | OPEN |
| P12 IfadahCandidate | REQUIRED | N/A (terminal) | REQUIRED | REQUIRED | OPEN |
| MorphoSyntaxCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| ParadigmCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| PhonologicalCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| LexicalFunctionalCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |
| ArticleCandidate | REQUIRED | REQUIRED | REQUIRED | N/A | OPEN |

---

## 8. ملفات الاختبار المطلوبة

| الملف | يغطي |
|-------|------|
| `tests/scg/test_taaqol_judgment_all_edges.py` | التأكيد 1–11 و16–17: كل حافة تستدعي Taaqol |
| `tests/scg/test_taaqol_fail_closed.py` | التأكيد 7–8: FAIL_CLOSED لكل مرشح |
| `tests/scg/test_taaqol_terminal_guards.py` | التأكيد 4–5 و16: وقف بعد BLOCKED/REJECTED |
| `tests/scg/test_taaqol_transition_determinism.py` | التأكيد 9 و14–15: حتمية الحكم ونوع الكائنات |

---

## 9. خطة الالتزامات الذرية (10 التزامات)

```bash
# 1. عقود P0–P3 + اختبارات Taaqol الحافة
git add pipeline/p0_unicode/ pipeline/p1_normalize/ pipeline/p2_segment/ pipeline/p3_boundary/
git commit -m "feat: satisfy P0-P3 candidate contracts with live Taaqol judgment"

# 2. عقود P4a–P4b (Saleh/Qiyas adapter)
git add pipeline/p4_pattern/ pipeline/p4_bab/
git commit -m "feat: satisfy P4a-P4b Saleh/Qiyas adapter contracts"

# 3. عقود P5–P6 (inflection + word class)
git add pipeline/p5_inflection/ pipeline/word_class/
git commit -m "feat: satisfy P5-P6 inflection and word-class contracts"

# 4. عقود P7 (Arabic Verifier adapter)
git add pipeline/p7_radical/
git commit -m "feat: satisfy P7 Arabic Verifier adapter contract"

# 5. عقود P8–P9 (masdar + derivative — Saleh/Qiyas)
git add pipeline/p8_masdar/ pipeline/p9_derivative/
git commit -m "feat: satisfy P8-P9 masdar and derivative Saleh/Qiyas contracts"

# 6. عقود P10–P11 (Evidence + Residual — Taaqol طبقات)
git add pipeline/p10_evidence/ pipeline/p11_residual/
git commit -m "feat: satisfy P10-P11 Taaqol evidence and residual contracts"

# 7. عقد P12 (Ifadah — terminal)
git add pipeline/p12_ifadah/
git commit -m "feat: satisfy P12 Ifadah terminal contract"

# 8. تطبيق الحكم الحي لـ Taaqol على كل حافة
git add pipeline/governance/taaqol_judgment_enforcer.py tests/scg/test_taaqol_judgment_all_edges.py
git commit -m "feat: require live Taaqol judgment on every SCG edge"

# 9. ملفات الاختبار الأخرى
git add tests/scg/test_taaqol_fail_closed.py tests/scg/test_taaqol_terminal_guards.py tests/scg/test_taaqol_transition_determinism.py
git commit -m "test: close Taaqol judgment policy coverage for SCG P0-P12"

# 10. التقارير والتوثيق
git add reports/scg_p0_p12/taaqol_transition_judgment_matrix.json docs/ar/HOKOM_SCG_P0_P12_TAAQOL_JUDGMENT_CLOSURE_AR.md
git commit -m "docs: record SCG P0-P12 Taaqol judgment closure"
```

---

## 10. شروط الإغلاق

```
ALL_NINETEEN_CANDIDATE_CONTRACTS_SATISFIED       : NOT_YET
ALL_CANONICAL_TRANSITIONS_JUDGED_BY_TAAQOL       : NOT_YET
TRANSITIONS_WITHOUT_TAAQOL_JUDGMENT              : 0   (required)
LOCAL_TRANSITION_DECISIONS                       : 0   (required)
DISCOVERED_CANONICAL_TRANSITION_EDGE_COUNT       : <discovered_at_runtime>
FAIL_CLOSED_VERIFIED_FOR_ALL_CANDIDATES          : NOT_YET
POST_TERMINAL_GUARD_VERIFIED                     : NOT_YET
TAAQOL_TRANSITION_JUDGMENT_MATRIX_GENERATED      : NOT_YET
NO_ENGINE_COPY_IN_HOKOM                          : REQUIRED
NO_OWNERSHIP_DUPLICATION                         : REQUIRED
SALEH_QIYAS_CALLED_VIA_INTERFACE_ONLY            : REQUIRED
ARABIC_VERIFIER_CALLED_VIA_INTERFACE_ONLY        : REQUIRED
VENDOR_MODIFICATIONS                             : 0   (required)
HR2S_DEPENDENCY_ADDED                            : NO  (required)
P13_CANDIDATES_CREATED                           : 0   (required)
CLOSURE_STATUS                                   : OPEN
```

---

## 11. المحظورات الدستورية المطلقة لهذا التفويض

```
ROOT_REOPENING              = FORBIDDEN
PATTERN_REOPENING           = FORBIDDEN
MASDAR_REOPENING            = FORBIDDEN
DERIVATIVES_REOPENING       = FORBIDDEN
INFLECTION_REOPENING        = FORBIDDEN
WORD_CLASS_REOPENING        = FORBIDDEN
PYTHON_RUNTIME_REOPENING    = FORBIDDEN
TAAQOL_REOPENING            = FORBIDDEN
SEGMENTATION_REOPENING      = FORBIDDEN
FORM_REOPENING              = FORBIDDEN
SILENT_FALLBACK             = FORBIDDEN
FORCE_OVERALL_VERDICT_LICENSED = FORBIDDEN
COPY_SALEH_QIYAS_INTO_HOKOM = FORBIDDEN
COPY_ARABIC_VERIFIER_INTO_HOKOM = FORBIDDEN
ADD_HR2S_DEPENDENCY         = FORBIDDEN
CREATE_TAG                  = FORBIDDEN
GIT_ADD_A_OR_DOT            = FORBIDDEN
MODIFY_GOLD_WITHOUT_AMENDMENT = FORBIDDEN
DEFERRED_TO_LICENSED_WITHOUT_EVIDENCE = FORBIDDEN
VENDOR_MODIFICATION         = FORBIDDEN
P13_ALLOWED                 = NO
```

---

## 12. الحكم الحالي

```
DOCUMENT_TYPE              : EXECUTION_MANDATE
BASELINE_STATUS            : APPROVED_FOR_EXECUTION
CLOSURE_STATUS             : OPEN
TAQOOL_JUDGMENT_REQUIRED   : YES
CANONICAL_CANDIDATE_COUNT  : 19
CANONICAL_LEVEL_RANGE      : P0-P12
P13_ALLOWED                : NO
ALL_CONTRACTS_SATISFIED    : NOT_YET
TAAQOL_JUDGMENT_ENFORCED   : NOT_YET
MANDATE_COMMIT             : PENDING
```
