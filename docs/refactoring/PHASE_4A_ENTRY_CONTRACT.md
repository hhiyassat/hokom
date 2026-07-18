
# Phase 4A — Wazn Projection: Entry Contract (PR 4A.0)

**الحالة**: مسودة مرجعية — تُقرأ قبل البدء في أي تنفيذ لـ Phase 4A.
**المرحلة السابقة**: Phase 3.10 — Root Host Refinement (CLOSED)
**الخلاصة السريعة**: Phase 4A تقترح الوزن، لكنها لا تقبله نهائيًا إلا بعد عودة الجذر إلى حالة مرخصة.

---

## 1. المدخلات الرسمية

Phase 4A تستقبل حصريًا من الطبقات السابقة — لا تقرأ السطح الأصلي مباشرة.

```
original_host            : str
    # pre_root.host_surface — المضيف كما أنتجه PreRoot (بعد فصل الأداة)
    # مثال: 'تَرَكَتْ' / 'مَحَبَّةِ' / 'عَمْمَ'

refined_host             : str
    # root_refinement.refined_host — المضيف بعد إزالة اللواحق الطرفية
    # مثال: 'تَرَكَ' / 'مَحَبَّ' / 'عَمْمَ'
    # هذا هو السطح الفعلي الذي يحلله HR2S وستبني عليه Phase 4A

removed_morphological_markers : tuple[str, ...]
    # root_refinement.removed_suffixes
    # مثال: ('PAST_FEMININE_TA',) | ('NOMINAL_TA_MARBUTA',) | ()

root_candidate           : RootCandidate
    # P3 — directive + canonical_root + root_profile + residuals
    # ACCEPT → canonical_root مكتمل، يُبنى الوزن عليه
    # DEFER  → canonical_root=None، يُفرض بحث الوزن بحذر
    # BLOCK  → Phase 4A لا تعمل

root_profile             : Mapping[str, Any]
    # من RootProjection — بيانات وصفية من HR2S
    # قد تحتوي: root_class، weak_positions، radical_count، ...

residual_codes           : tuple[str, ...]
    # من RootHostRefinement + RootProjection
    # المهم: 'defer:root_refinement:internal_ziyadah_not_resolved'
    # يعني: هناك زيادة داخلية لم تُحسم بعد
```

---

## 2. قواعد الدخول

### 2.1 متى تعمل Phase 4A

```
root_candidate.directive == 'ACCEPT'
→ Phase 4A تعمل بالكامل: اقتراح وزن + محاذاة + تحقق

root_candidate.directive == 'DEFER'
→ Phase 4A تعمل بوضع محدود: تقترح فرضيات وزن لكن لا تنتج WaznCandidate نهائيًا
→ المخرج: WaznHypothesis (مقترح) لا WaznCandidate (مقبول)

root_candidate.directive == 'BLOCK'
→ Phase 4A لا تعمل
→ لا وزن، لا فرضية، لا مخرج
```

### 2.2 الخط الأحمر الرئيسي

> Phase 4A **لا تقبل وزنًا نهائيًا** إلا بعد أن يعود الجذر إلى حالة مرخصة:
> - جذر ثلاثي مكتمل: FA + AYN + LAM بدون UnknownRadical
> - أو جذر رباعي مُثبَت بشاهد مستقل
>
> إذا بقي أي موضع غير محلول → المخرج `WaznHypothesis` لا `WaznCandidate`.

---

## 3. نطاق Phase 4A

### 3.1 ما تفعله Phase 4A

```
✓ اقتراح وزن بناءً على refined_host + canonical_root
✓ محاذاة الجذر على الوزن (FA/AYN/LAM ↔ حروف الوزن)
✓ كشف حروف الزيادة الداخلية (ميم مَفْعَل، تاء افْتَعَل، الف انْفَعَل...)
✓ اقتراح حذف الزيادة الداخلية إذا أنتج جذرًا مرخصًا
✓ إنتاج WaznHypothesis عند DEFER أو عدم اليقين
✓ إنتاج WaznCandidate نهائي فقط عند يقين كامل
```

### 3.2 ما لا تفعله Phase 4A

```
✗ لا تقرأ السطح الأصلي أو normalized_surface مباشرة
✗ لا تُعيد تنفيذ boundary assessment
✗ لا تستدعي HR2S
✗ لا تُعدّل canonical_root أو refined_host
✗ لا تُنتج وزنًا استثنائيًا بالظن
✗ لا تتجاوز رتابة P3 (DEFER لا يصبح ACCEPT بدون جذر مكتمل)
✗ لا تحذف حروفًا داخلية بدون فرضية وزن صريحة
```

---

## 4. الحالات المؤجلة إلى Phase 4A

هذه الحالات تصل بـ`refined_host` وتنتظر محاذاة الوزن:

| السطح الأصلي | refined_host | الزيادة الداخلية | الوزن المتوقع |
|-------------|-------------|----------------|--------------|
| مَحَبَّةِ | مَحَبَّ | ميم مَفْعَلة | مَفَعَّلَة أو مَفْعَلة |
| مَسْرُورَةٌ | مَسْرُورَ | ميم + ر زائدة | اسم مفعول مَفْعُول |
| الْحَيَوَانَاتُ | حَيَوَانَ | ألف جمع | جمع تكسير |
| يَسْتَطِيعُونَ | يَسْتَطِيعُ | يَ + اسْتَ | يَسْتَفْعِل |
| الْمُفْتَرِسَةُ | مُفْتَرِسَ | مُ + ت + زيادة | مُفْتَعِل |

**ملاحظة**: `مَحَبَّ` و`مَسْرُور` سيصلان بـ`residual: defer:root_refinement:internal_ziyadah_not_resolved` — هذا الرمز هو إشارة Phase 4A للبدء بالبحث عن الوزن.

---

## 5. نموذج المخرج المقترح

```python
@dataclass(frozen=True)
class WaznHypothesis:
    """فرضية وزن — لم تُقبل بعد، تحتاج تحقق إضافي."""
    refined_host:         str
    proposed_wazn:        str            # 'مَفْعَلَة' | 'فَعَّلَ' | ...
    ziyadah_detected:     tuple[str, ...]  # ('MIM_ZIYADAH',) | ('ALIF_WASL', 'SIN', 'TA')
    proposed_root_after:  tuple[str, ...] | None  # الجذر بعد حذف الزيادة (إن نجح)
    confidence:           str            # 'HIGH' | 'MEDIUM' | 'LOW'
    evidence_ids:         tuple[str, ...]
    residual_codes:       tuple[str, ...]

@dataclass(frozen=True)
class WaznCandidate:
    """وزن مقبول — الجذر مكتمل والمحاذاة تامة."""
    refined_host:         str
    canonical_wazn:       str
    canonical_root:       tuple[str, ...]  # مكتمل، لا UnknownRadical
    ziyadah_removed:      tuple[str, ...]
    evidence_ids:         tuple[str, ...]
    source_hypothesis:    str            # 'WaznHypothesis'
```

---

## 6. الاختبارات الإلزامية لـ PR 4A.0

قبل أي تنفيذ، يجب كتابة هذه الاختبارات الفاشلة أولًا:

```python
# مدخل نظيف: ACCEPT + refined_host بلا زيادة
test_tarraka_accept()
# مدخل فيه زيادة داخلية: DEFER + residual
test_mahabbah_hypothesis_not_candidate()
# منع: BLOCK لا ينتج وزنًا
test_block_no_wazn()
# منع: DEFER لا ينتج WaznCandidate مباشرة
test_defer_no_final_candidate_without_root()
# رتابة: WaznCandidate لا ينتج إلا من WaznHypothesis مقبول
test_monotonicity_hypothesis_to_candidate()
```

---

## 7. السلسلة الكاملة بعد Phase 4A

```
AttachmentProjection (P5)
→ PreRootDecision
→ RootHostRefinement       [Phase 3.10 — CLOSED]
→ HR2SRootAdapter
→ RootProjection (P2)
→ RootCandidate (P3)
→ WaznHypothesis (P4A-α)   [Phase 4A — pending]
→ WaznCandidate (P4A-β)    [Phase 4A — pending]
```

---

## 8. شروط إغلاق Phase 4A

```
✓ WaznCandidate لا ينتج إلا من جذر مرخص كامل
✓ مَحَبَّ → WaznHypothesis أولًا، ثم WaznCandidate إذا حُسم الجذر
✓ مَسْرُور → نفس المسار
✓ يَسْتَطِيعُ → فرضية يَسْتَفْعِل، لا تُقبل إلا بعد تحقق
✓ 0 false ACCEPT
✓ 0 وزن نهائي من جذر ناقص
✓ baseline 681+ passed محفوظ
✓ 0 removed node IDs
```
