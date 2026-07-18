# Phase 4A-α — Reference Cases (حالات مرجعية)

تتبّع كل كلمة مرجعية عبر السلسلة: refined_host → WaznHypothesis → RootRelicensing → WaznProjection.

---

## 1. مَحَبَّ (بعد إزالة ة)

**المدخل**:
- `refined_host = 'مَحَبَّ'`
- `removed_markers = ('NOMINAL_TA_MARBUTA',)`
- `residual_codes = ('defer:root_refinement:internal_ziyadah_not_resolved',)`

**WaznHypothesis** (Pattern A — مَفْعَلَة):
- `proposed_wazn = 'مَفْعَلَة'`
- `ziyadah_detected = ('MIM_ZIYADAH',)`
- `proposed_root_after = ('ح', 'ب', 'ب')` — الشدة مُوسَّعة → حَبَبَ
- `confidence = 'HIGH'`

**RootRelicensing**:
- `directive = 'ACCEPT'`
- `failure_reason = None`

**Phase4AResult.source**: `'hypothesis_relicensed'`

---

## 2. مَسْرُورَ (بعد إزالة ة)

**المدخل**:
- `refined_host = 'مَسْرُورَ'`
- `removed_markers = ('NOMINAL_TA_MARBUTA',)`

**WaznHypothesis** (Pattern A — مَفْعُول):
- `proposed_wazn = 'مَفْعَلَة'`
- `ziyadah_detected = ('MIM_ZIYADAH',)`
- `proposed_root_after = ('س', 'ر', 'ر')` — الواو (و) حذفت كحرف مد وزني (مَفْعُول)
- `confidence = 'HIGH'`

**RootRelicensing**:
- `directive = 'ACCEPT'`
- `failure_reason = None`

**Phase4AResult.source**: `'hypothesis_relicensed'`

---

## 3. يَسْتَطِيعُ

**المدخل**:
- `refined_host = 'يَسْتَطِيعُ'`
- `residual_codes = ('defer:root_refinement:internal_ziyadah_not_resolved',)`

**WaznHypothesis** (Pattern B — يَسْتَفْعِل):
- `proposed_wazn = 'يَسْتَفْعِل'`
- `ziyadah_detected = ('ALIF_WASL', 'SIN', 'TA')`
- `proposed_root_after = None` — بعد حذف يَسْتَ: (ط،ي،ع)، وبعد حذف حرف المد ي: (ط،ع) = 2 حروف فقط
- `confidence = 'MEDIUM'`

**RootRelicensing**:
- `directive = 'BLOCK'`
- `failure_reason = 'block:relicensing:no_proposed_root'`

**Phase4AResult.source**: `'deferred'`

**ملاحظة**: الياء في (ط،ي،ع) قد تكون عين الجذر الأجوف (طوع) أو حرف مد. لا يمكن الحسم بدون سياق المعالجة الإعلالية. يبقى DEFER ريثما يُحسم في P4A-β (معالجة الإعلال).

---

## 4. مُفْتَرِسَ (بعد إزالة ة) — تم الإصلاح

**المدخل**:
- `refined_host = 'مُفْتَرِسَ'`
- `removed_markers = ('NOMINAL_TA_MARBUTA',)`
- `residual_codes = ('defer:root_refinement:internal_ziyadah_not_resolved',)`

**WaznHypothesis** (Pattern C — مُفْتَعِل):
- `proposed_wazn = 'مُفْتَعِل'`
- `ziyadah_detected = ('MIM_ZIYADAH', 'IFTIEAL_TA')`
- `proposed_root_after = ('ف', 'ر', 'س')`
- `confidence = 'HIGH'`

**radical_alignment** (الخريطة الصريحة):
```
('م', 'MIM_ZIYADAH')
('ف', 'FA')
('ت', 'IFTIEAL_TA')
('ر', 'AYN')
('س', 'LAM')
```

**removed_elements**:
```
('م', 'MIM_ZIYADAH')
('ت', 'IFTIEAL_TA')
```

**RootRelicensing**:
- `directive = 'ACCEPT'`
- `proposed_root = ('ف', 'ر', 'س')`
- `failure_reason = None`

**Phase4AResult.source**: `'hypothesis_relicensed'`

**ملاحظة**: Pattern C (مُفْتَعِل) تكتشف ت الافتعال عند موضع 1 من القاعدة (بعد الميم). P4B يبدأ بعد استقرار الوزن — لا علاقة له بهذه الخطوة.

---

## 5. ضَرَبَ (ACCEPT — مسار مباشر)

**المدخل**:
- `directive = 'ACCEPT'`
- `canonical_root = ('ض', 'ر', 'ب')`

**WaznHypothesis**: None (لا فرضية للـ ACCEPT)
**RootRelicensing**: None
**WaznProjection**: `directive = ACCEPT`
**Phase4AResult.source**: `'direct'`

---

## 6. مِنْ (BLOCK — تخطّي)

**المدخل**:
- `directive = 'BLOCK'`

**WaznHypothesis**: None
**RootRelicensing**: None
**WaznProjection**: `directive = BLOCK`
**Phase4AResult.source**: `'blocked'`

---

## ملخص النتائج

| الكلمة | Pattern | proposed_root | relicensing | source |
|--------|---------|---------------|-------------|--------|
| مَحَبَّ | A (مَفْعَلَة) | (ح،ب،ب) | ACCEPT | hypothesis_relicensed |
| مَسْرُورَ | A (مَفْعُول) | (س،ر،ر) | ACCEPT | hypothesis_relicensed |
| يَسْتَطِيعُ | B (يَسْتَفْعِل) | None (إعلال) | BLOCK | deferred |
| مُفْتَرِسَ | C (مُفْتَعِل) | (ف،ر،س) | ACCEPT | hypothesis_relicensed |
| ضَرَبَ | — | (ض،ر،ب) | — | direct |
| مِنْ | — | — | — | blocked |
