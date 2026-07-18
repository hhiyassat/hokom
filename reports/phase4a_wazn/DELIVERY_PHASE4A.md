# تقرير الإغلاق المصحّح — Phase 4A — Wazn Projection

> نسخة مصحّحة تعالج ملاحظات المراجعة الثلاث (دقة قائمة الملفات، فحص المسارات
> المطلقة، مصفوفة الحالات الثماني عشرة) وتضيف إثبات ثبات الإخفاقات السابقة،
> والعدّ المفصول، وتأكيد تفرّد الوزن المختار.

```
Repository:   /Users/husseinhiyassat/hokom   (ليس مستودع git — لا branch/commit/tag/merge)
Working state: RootCandidate P3 → WaznProjection Phase 4A — implemented.
```

---

## 1. القائمة الدقيقة للملفات (جديد مقابل معدَّل)

**All production-code files under `pipeline/p4_wazn/` are new. No pre-existing runtime
implementation files were modified.**

الجديد — كود الإنتاج:
```
pipeline/p4_wazn/__init__.py
pipeline/p4_wazn/models.py
pipeline/p4_wazn/wazn_catalog.py
pipeline/p4_wazn/alignment.py
pipeline/p4_wazn/ziyadah_audit.py
pipeline/p4_wazn/weak_operations.py
pipeline/p4_wazn/wazn_projection.py
```
الجديد — بيانات الـcatalog:
```
data/wazn/wazn_catalog.json      (20 وزنًا)
```
الجديد — الاختبارات:
```
tests/p4_wazn/test_wazn_models.py
tests/p4_wazn/test_root_surface_alignment.py
tests/p4_wazn/test_ziyadah_audit.py
tests/p4_wazn/test_weak_operations.py
tests/p4_wazn/test_wazn_projection.py
tests/integration/test_wazn_pipeline_phase4a.py
```
الجديد — التوثيق والتقارير:
```
docs/morphology/PHASE_4A_WAZN_PROJECTION.md
docs/PLAN.md
reports/phase4a_wazn/*
```

**تصحيح دقّة سابق:** عبارة «nothing existing was modified» أُسقطت. الوضع الفعلي:
- `docs/PLAN.md` **لم يكن موجودًا** في شجرة العمل (فحص `ls` أعاد "No such file")،
  فأُنشئ. (ملاحظة: نص المهمة §20 استعمل «حدّث docs/PLAN.md» بافتراض وجوده، لكنه
  لم يكن موجودًا فعليًا — أُنشئ لا عُدِّل.)
- لم يُعدَّل أي ملف تنفيذي قائم (operator/mabni/root/HR2S/PreRoot).
- بيانات operator/mabni لم تُمسّ: الإضافة الوحيدة تحت `data/` هي `data/wazn/`؛
  `data/02_mabniyat/` و`operators_catalog_split_vocalized.csv` دون تغيير.

الصياغة المعتمدة:
```
All production-code files under pipeline/p4_wazn are new.
docs/PLAN.md was created (it did not previously exist).
No pre-existing runtime implementation files were modified.
No operator/mabni catalog data was modified.
```

---

## 2. فحص المسارات المطلقة (النتيجة الصريحة)

قاعدة المنع طُبِّقت على الشجرة الجديدة كاملةً (كود + catalog + اختبارات):
```
Absolute paths in pipeline/p4_wazn/                 : none
Absolute paths in data/wazn/                        : none
Absolute paths in tests/p4_wazn/ + integration test : none
```
(الـcatalog يُحمَّل بمسار نسبي: `Path(__file__).resolve().parents[2] / "data" / "wazn"`.)

---

## 3. مصفوفة الحالات المرجعية الثماني عشرة (النتائج الفعلية)

| surface | analyzed_host | canonical_root | root_dir | candidate_awzan | selected_wazn | wazn_dir | stage_state | residual_codes |
|---|---|---|---|---|---|---|---|---|
| ضَرَبَ | ضَرَبَ | ض·ر·ب | ACCEPT | فَعَلَ | فَعَلَ | ACCEPT | COMPLETED | — |
| قَرَأَ | قَرَأَ | ق·ر·ء | ACCEPT | فَعَلَ | فَعَلَ | ACCEPT | COMPLETED | — |
| مَدَّ | مَدَّ | م·د·د | ACCEPT | فَعَلَ | فَعَلَ | ACCEPT | COMPLETED | — |
| كَتَبَ | كَتَبَ | ك·ت·ب | ACCEPT | فَعَلَ | فَعَلَ | ACCEPT | COMPLETED | — |
| عَطْفِ | عَطْفِ | ع·ط·ف | ACCEPT | فَعْل | فَعْل | ACCEPT | COMPLETED | — |
| شِدَّةِ | شِدَّةِ | ش·د·د | ACCEPT | — | — | DEFER | DEFERRED | defer:wazn:unlicensed_but_structural_augment |
| مَحَبَّةِ | مَحَبَّةِ | ح·ب·ب | ACCEPT | — | — | DEFER | DEFERRED | defer:wazn:unlicensed_but_structural_augment |
| مَسْرُورَةٌ | مَسْرُورَةٌ | س·ر·ر | ACCEPT | مَفْعُول | — | DEFER | DEFERRED | defer:wazn:nominal_feminine_requires_licensed_wazn |
| نَائِمِينَ | نَائِم | — | DEFER | — | — | DEFER | NOT_OPENED | defer:root:x; defer:wazn:root_candidate_not_resolved |
| الْأَطْفَالُ | أَطْفَالُ | ط·ف·ل | ACCEPT | — | — | DEFER | DEFERRED | defer:wazn:unlicensed_but_structural_augment |
| الشَّجَرَةِ | شَجَرَةِ | ش·ج·ر | ACCEPT | فَعَلَ | — | DEFER | DEFERRED | defer:wazn:nominal_feminine_requires_licensed_wazn |
| تَرَكَتْهُمْ | تَرَكَتْ | ت·ر·ك | ACCEPT | فَعَلَ | فَعَلَ | ACCEPT | COMPLETED | — (inflectional: تْ) |
| قَالَ | قَالَ | — | DEFER | — | — | DEFER | NOT_OPENED | defer:root:x; defer:wazn:root_candidate_not_resolved |
| دَعَا | دَعَا | — | DEFER | — | — | DEFER | NOT_OPENED | defer:root:x; defer:wazn:root_candidate_not_resolved |
| وَقَى | وَقَى | — | DEFER | — | — | DEFER | NOT_OPENED | defer:root:x; defer:wazn:root_candidate_not_resolved |
| قُلْ | قُلْ | — | DEFER | — | — | DEFER | NOT_OPENED | defer:root:x; defer:wazn:root_candidate_not_resolved |
| مِنْ | مِنْ | — | BLOCK | — | — | BLOCK | NOT_OPENED | block:root:x; block:wazn:root_candidate_blocked |
| أَنَّهُمْ | أَنَّ | — | BLOCK | — | — | BLOCK | NOT_OPENED | block:root:x; block:wazn:root_candidate_blocked |

المصدر الآلي الكامل (بكل الحقول): `reports/phase4a_wazn/reference_matrix.json`
وتفاصيل المحاذاة لكل مرشّح: `reports/phase4a_wazn/wazn_candidates.json`.

الحالات الحرجة المطلوبة صراحةً — مثبتة:
```
ضَرَبَ → ACCEPT فَعَلَ                 قَالَ  → DEFER / NOT_OPENED
قَرَأَ → ACCEPT فَعَلَ (root=ق ر ء)     دَعَا  → DEFER / NOT_OPENED
مَدَّ  → ACCEPT فَعَلَ (root=م د د)     وَقَى  → DEFER / NOT_OPENED
كَتَبَ → ACCEPT فَعَلَ                 قُلْ   → DEFER / NOT_OPENED
                                       مِنْ    → BLOCK / NOT_OPENED
الْأَطْفَالُ → analyzed_host=أَطْفَالُ  أَنَّهُمْ → BLOCK / NOT_OPENED
الشَّجَرَةِ  → analyzed_host=شَجَرَةِ
تَرَكَتْهُمْ → analyzed_host=تَرَكَتْ
```

---

## 4. العدّ المفصول للاختبارات (كدلتا، لا كإجمالي محيطي)

مساهمة Phase 4A تُقاس كدلتا لأن المستودع يُعدَّل تزامنيًا (انظر §10):
```
Protected baseline preserved      : 590 pre-existing non-integration tests, 52 subtests
   → 0 removed from the phase-baseline snapshot (reports/phase4a_wazn/baseline.txt)
   → 0 original node IDs removed (reports/refactoring/baseline_ids.txt = 446)
Phase 4A NEW non-integration      : 68  (tests/p4_wazn/*) — the only IDs added by me
Phase 4A NEW integration          : 26  (tests/integration/test_wazn_pipeline_phase4a.py)
Phase 4A total new coverage       : 94
```
تحقّق الحساب لحظة قياس Phase 4A: `pytest tests/ --ignore=tests/integration` = **658**
= 590 baseline + 68 (خاصتي). الاختبارات التكاملية الـ26 خارج `--ignore=tests/integration`
(كحال اختبارات R-10)، فلا تعارض حسابي.

**تنبيه إجمالي متحرّك:** بعد ذلك القياس، أضاف *عاملٌ متزامن غير مرتبط* 23 اختبارًا في
`tests/p2_projection/test_root_host_refinement.py`، فصار الإجمالي المحيطي **681**
= 590 + 68 (خاصتي) + 23 (العامل الآخر). هذه الـ23 ليست من Phase 4A. لذلك يُعتمد
عدّي كدلتا (68/26)، لا كإجمالي محيطي متحرّك.

---

## 5. إثبات ثبات الإخفاقات السابقة (153)

`tests/integration/test_all_mabniyat_json_examples.py` — 153 fail / 628 pass.

**قياس قبل/بعد مباشر** (بإخراج حزمة `pipeline/p4_wazn` فعليًا من الشجرة):
```
WITH  pipeline/p4_wazn present   : 153 failed, 628 passed
WITHOUT pipeline/p4_wazn (moved) : 153 failed, 628 passed   ← مطابق تمامًا
(find_spec('pipeline.p4_wazn') = None أثناء القياس الثاني، ثم أُعيدت الحزمة وبقيت الـ94 خضراء)
```
- **نفس عدد الإخفاقات** قبل وبعد Phase 4A: 153 = 153.
- **نفس الفئات/الاختبارات:** كلها في ملف واحد وفي دالّتين فقط:
  `test_mabni_boundary_route` = 106 ، `test_operator_boundary_route` = 47.
- **لا imports من p4_wazn** في تلك المجموعة (grep = 0).
- **لا تغييرات في operator/mabni data** (الإضافة الوحيدة تحت `data/` هي `data/wazn/`).

الوصف المعتمد (لا نصف المستودع بأكمله بأنه أخضر):
```
Protected baseline and Phase 4A suites are green.
The broader repository retains 153 documented pre-existing integration failures
(test_all_mabniyat_json_examples.py), proven independent of Phase 4A.
```

---

## 6. تأكيد تفرّد الوزن المختار (selected_wazn uniqueness)

لكل حالة ACCEPT: `len(candidate_awzan) == 1` و`selected_wazn == candidate_awzan[0]`:
```
ضَرَبَ  ACCEPT candidates=1 selected=فَعَلَ  unique=True
قَرَأَ  ACCEPT candidates=1 selected=فَعَلَ  unique=True
مَدَّ   ACCEPT candidates=1 selected=فَعَلَ  unique=True
كَتَبَ  ACCEPT candidates=1 selected=فَعَلَ  unique=True
عَطْفِ  ACCEPT candidates=1 selected=فَعْل   unique=True
تَرَكَتْ ACCEPT candidates=1 selected=فَعَلَ  unique=True
ALL ACCEPT UNIQUE: True
```
وعند تعدّد المطابقة (اختبار `TWIN_A/TWIN_B` بقالبين متطابقين) ⇒ DEFER لا ACCEPT،
مع `selected_wazn=None`. أي: ACCEPT لا يصدر إلا بوزن واحد مثبت.

---

## 7. توضيح ملاحظة مَدَّ (تصحيح الصياغة)

الملاحظة مقبولة. التصحيح الدقيق:
- المُحاذي **يتجاهل الحركة الإعرابية النهائية** (`FINAL`)، فلا يستعمل فتحة `مَدْدَ`
  النهائية للترجيح. القول السابق بأن `مَدْدَ` «متجانس يُحسَم بترخيص الإدغام وحده» صياغة
  غير دقيقة وقد صُحِّحت.
- الآلية الحالية تستعمل **ترخيص الإدغام على مستوى الوزن** بوصفه *وكيلًا بنيويًا*:
  الأوزان ساكنة العين التي لا ترخّص الإدغام (فَعْل) تُرفَض للمضاعف المُدغَم، فيبقى
  فَعَلَ وحده. هذا صحيح لكنه **ليس الدليل الوحيد** على فعلية الوزن.
- العقد الأصحّ — كما ورد في المراجعة — يقوم على الفصل الصريح بين:
  `derivational geometry` و`inflectional/case-or-conjugational ending` و`surface_class`،
  ثم الترجيح على أساسها لا على الإدغام وحده.
- **الحالة:** هذا التمييز الأعمق **لم يُنفَّذ** في Phase 4A (خارج نطاق هذه الدفعة، وغير
  مطلوب للإغلاق حسب المراجعة). سُجِّل كبند تقوية مستقبلي (Phase 4A-hardening / مدخل
  محتمل إلى عقد `surface_class`). الوكيل الحالي كافٍ لإثبات العقد على مجموعة المرجع،
  والجذر `م د د` لا يُعدَّل والدال الثانية ليست زيادة.

---

## 8. عقود الطبقة (كما هي)

```
RootCandidate input contract : RootCandidate فقط (analyzed_host, canonical_root, ...)؛
                               لا HR2S، لا قراءة raw surface، canonical_root غير مُعدَّل.
WaznProjection output        : frozen، JSON-serializable، directive/stage_state + candidates/
                               selected + alignment + ziyadah + weak_ops + inflectional_suffixes
                               + evidence/trace/residuals محفوظة.
Ziyadah audit                : ACCEPT/DEFER/BLOCK حسب ترخيص الموقع في القالب.
Weak-operation               : op:weak:mudaaf_gemination_idghaam ، op:ziyadah:pattern_gemination.
Shadda                       : توسيع Cّ→Cْ+C؛ مضاعف=جذر+إدغام، تضعيف الوزن=زيادة، الجذر لا ينمو.
Hamza                        : أ/إ/ؤ/ئ/آ → ء؛ الهوية محفوظة ء.
Monotonicity                 : BLOCK→BLOCK/NOT_OPENED، DEFER→DEFER/NOT_OPENED، ACCEPT→{A,D,B}.
```

## 9. حدود المسؤولية

```
HR2S modified            : No
HR2S imported by p4_wazn : No (فحص import صريح)
Bab implemented          : No
Masdar implemented       : No
Mushtaqat implemented    : No
Commit/tag/merge         : No (ليس مستودع git)
Working tree             : ملفات جديدة فقط + إنشاء docs/PLAN.md؛ لا تعديل لأي ملف تنفيذي قائم.
```

## 10. إفصاح التزامن (Concurrency disclosure)

أثناء تنفيذ Phase 4A، رُصِد **عاملٌ آخر يعدّل المستودع نفسه تزامنيًا** (المستودع ليس
git، فلا عزل). نشاطه المرصود (طوابع ~10:42–10:43):
```
+ pipeline/p2_projection/root_host_refinement.py   (جديد — ميزة P2 منفصلة)
+ tests/p2_projection/test_root_host_refinement.py (جديد — 23 اختبارًا، ليست من Phase 4A)
~ hokom_pipeline.py                                (عُدِّل بواسطته)
```
أثر ذلك على Phase 4A: **لا شيء وظيفيًا.**
- عقد مدخلي (`pipeline/p3_candidate/root_candidate.py`، `pipeline/p2_projection/root_projection.py`)
  **لم يُمَسّ** (طوابعه من عمل R-10 ليلًا: 00:55–00:56).
- 0 من لقطة الـ590 حُذف؛ 0 من الأصول الـ446 حُذف.
- الـ94 اختبار الخاصة بي خضراء ومستقلة عن هذا التغيير (لا تشترك في ملف واحد).
الأثر الوحيد: الإجمالي المحيطي للاختبارات صار متحرّكًا (681 لحظة كتابة هذا التقرير)،
لذا يُعتمد عدّ Phase 4A كدلتا (68 غير تكاملي + 26 تكاملي)، لا كإجمالي مطلق.

**توصية:** ضمان كاتب واحد لهذه الشجرة في المرة الواحدة (لا git = لا مسار تراجع).

العمل ينتهي عند `RootCandidate P3 → WaznProjection Phase 4A`.
