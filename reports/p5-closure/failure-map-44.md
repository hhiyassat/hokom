# P5 Closure — خريطة الـ44 فشلاً
## HEAD: ac77edf | Suite: `python -m pytest test_hokom.py tests/ -q`

---

## أسباب الجذر (Root Causes)

| رمز | التسمية | الملف |
|-----|---------|-------|
| RC1 | CWD_POLLUTION_IS_OP_OVERRIDE | `pipeline/p5_lexical/mabni_inventory.py` → `_load_mabniyat_dir('')` |
| RC2 | CATALOG_IS_OP_FALSE_GROUP8 | `data/operators_catalog_split_vocalized_corrected.csv` |
| RC3 | BARE_INDEX_AMBIGUITY_KAM | `_by_bare['كم']` = {كَمْ, كُمْ} — مُسبَّب من RC1 |
| RC4 | BARE_INDEX_UNICODE_COLLISION_KAAYYIN | `_by_bare['كأين']` = {كَأَيِّنْ_A, كَأَيِّنْ_B} — مُسبَّب من RC1 |
| RC5 | _verdict_from_DEFER_BARE_PROMOTION | `pipeline/p5_lexical/mabni_projection.py` → `_verdict_from` |
| RC6 | _verdict_from_MISSING_OPERATOR_DEFERRED_GROUP8 | `_verdict_from` — لا مسار OPERATOR_DEFERRED للأسماء (is_op=False) في DEFER |
| RC7 | PIPELINE_ATTACHMENT_CONDITION | `hokom_pipeline.py` سطر 91: `... if isinstance(mabni, MabniOpen) else None` |
| RC8 | MISSING_CATALOG_ENTRIES | `data/02_mabniyat/*.json` — TANIKA, DHANIKA, THAMM_KAF, HAHUNA_KAF غائبة |
| RC9 | MADD_YAA_SUKUN_COMPATIBILITY | `mabniyat_attachment.py` → `_diacritics_compatible` — سكون صريح على ياء المدّ |
| RC10 | GOVERNANCE_DEFER_PROPAGATION | `mabniyat_attachment.py` → `recognize_token` — لا يحترم P4=DEFER |

### سلسلة التبعية:
```
RC1 → RC3 (كم غامضة: كُمْ مصدره mabniyat_catalog من CWD)
RC1 → RC4 (كأين: تصادم Unicode من تحميل مزدوج)
RC1 → إخفاق Phase-1 لأدوات المجموعة 2 (إِنَّ etc.)
```

---

## الخريطة الكاملة — 44 فشلاً

| # | معرّف الاختبار | المتوقع | الفعلي | رمز السبب |
|---|--------------|---------|--------|-----------|
| 1 | `TestP5MabniBoundary::test_hatta_operator_boundary` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 2 | `TestSurfaceRepresentation::test_inna_found_in_inventory` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 3 | `TestMonotonicity::test_a_p5_operator_deferred_not_boundary` | ≠OPERATOR_BOUNDARY | OPERATOR_BOUNDARY | RC5 |
| 4 | `TestMonotonicity::test_all_vocalized_operators_structural_accept[إِنَّ]` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 5 | `TestMonotonicity::test_all_vocalized_operators_structural_accept[أَنَّ]` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 6 | `TestMonotonicity::test_all_vocalized_operators_structural_accept[كَأَنَّ]` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 7 | `TestMonotonicity::test_all_vocalized_operators_structural_accept[لَكِنَّ]` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 8 | `TestMonotonicity::test_all_vocalized_operators_structural_accept[لَعَلَّ]` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 9 | `TestMonotonicity::test_all_vocalized_operators_structural_accept[لَمَّا]` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 10 | `TestMonotonicity::test_all_vocalized_operators_structural_accept[كَمْ]` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 + RC2 |
| 11 | `TestMonotonicity::test_all_vocalized_operators_structural_accept[حَتَّى]` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC1 |
| 12 | `TestMonotonicity::test_defer_structural_verdict_never_operator_boundary[أ]` | ≠OPERATOR_BOUNDARY | OPERATOR_BOUNDARY | RC5 |
| 13 | `TestMonotonicity::test_inna_closed_function_word` | Closed Function Word | Bound Nominal | RC1 |
| 14 | `TestMonotonicity::test_kam_numerical_operator_class` | Numerical Operator | Bound Nominal | RC1 + RC2 |
| 15 | `TestMonotonicity::test_kam_unvocalized_operator_deferred` | MabniBoundary(OPERATOR_DEFERRED) | MabniOpen | RC3 |
| 16 | `TestMonotonicity::test_kam_vocalized_operator_boundary` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC2 |
| 17 | `TestMonotonicity::test_lexical_class_independent_of_operator_status` | Closed Function Word | Bound Nominal | RC1 |
| 18 | `TestMonotonicity::test_numerical_operators_remain_operator_boundary` | OPERATOR_BOUNDARY أو OPERATOR_DEFERRED | MABNI_BOUNDARY | RC2 |
| 19 | `TestP4Aggregation::test_kaayyin_unvocalized_operator_deferred` | MabniBoundary(OPERATOR_DEFERRED) | MabniOpen | RC4 |
| 20 | `TestP4Aggregation::test_kaayyin_vocalized_operator_boundary` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC2 |
| 21 | `TestP4Aggregation::test_kadha_unvocalized_operator_deferred` | OPERATOR_DEFERRED | MABNI_BOUNDARY | RC6 |
| 22 | `TestP4Aggregation::test_kadha_vocalized_operator_boundary` | OPERATOR_BOUNDARY | MABNI_BOUNDARY | RC2 |
| 23 | `TestP4Aggregation::test_uluf_unvocalized_operator_deferred` | OPERATOR_DEFERRED | OPERATOR_BOUNDARY | RC5 |
| 24 | `TestBareIndex::test_defer_bare_a_yields_operator_deferred` | OPERATOR_DEFERRED | OPERATOR_BOUNDARY | RC5 |
| 25 | `TestBareIndex::test_defer_bare_kaayyin_yields_operator_deferred` | MabniBoundary(OPERATOR_DEFERRED) | MabniOpen | RC4 |
| 26 | `TestBareIndex::test_defer_bare_kadha_yields_operator_deferred` | OPERATOR_DEFERRED | MABNI_BOUNDARY | RC6 |
| 27 | `TestBareIndex::test_defer_bare_kam_yields_operator_deferred` | MabniBoundary(OPERATOR_DEFERRED) | MabniOpen | RC3 |
| 28 | `TestBareIndex::test_defer_bare_structural_verdict_never_becomes_accept` | ≠OPERATOR_BOUNDARY | OPERATOR_BOUNDARY | RC5 |
| 29 | `TestBareIndex::test_defer_bare_uluf_yields_operator_deferred` | OPERATOR_DEFERRED | OPERATOR_BOUNDARY | RC5 |
| 30 | `TestBareIndex::test_shadda_kaayyin_bare_maps_uniquely` | entries ≠ [] | [] | RC4 |
| 31 | `TestBareIndex::test_unique_bare_kaayyin` | entries ≠ [] | [] | RC4 |
| 32 | `TestBareIndex::test_unique_bare_kam` | entries ≠ [] | [] | RC3 |
| 33 | `TestBareIndex::test_unique_bare_returns_correct_operator_id` | entries ≠ [] | [] | RC3 |
| 34 | `TestBareIndex::test_vocalized_forms_retain_accept_after_bare_fix` | OPERATOR_BOUNDARY (كَمْ) | MABNI_BOUNDARY | RC2 |
| 35 | `TestFalseSuffixScanResolution::test_alladhina_sukun_madd_yaa_resolves_to_mabni_boundary` | att ≠ None | att=None | RC7 + RC9 |
| 36 | `TestFalseSuffixScanResolution::test_dhanika_whole_token_mabni_boundary_no_kaf_suffix` | att ≠ None | att=None | RC7 + RC8 |
| 37 | `TestFalseSuffixScanResolution::test_hahuna_standalone_still_works` | att ≠ None | att=None | RC7 |
| 38 | `TestFalseSuffixScanResolution::test_hahunaka_whole_token_mabni_boundary` | att ≠ None | att=None | RC7 + RC8 |
| 39 | `TestFalseSuffixScanResolution::test_no_regression_dhalika_no_kaf_stripped` | att ≠ None | att=None | RC7 |
| 40 | `TestFalseSuffixScanResolution::test_tanika_whole_token_mabni_boundary_no_kaf_suffix` | att ≠ None | att=None | RC7 + RC8 |
| 41 | `TestFalseSuffixScanResolution::test_thamm_kaf_whole_token_mabni_boundary` | att ≠ None | att=None | RC7 + RC8 |
| 42 | `TestFalseSuffixScanResolution::test_thamm_standalone_still_works` | att ≠ None | att=None | RC7 |
| 43 | `TestGovernanceFixes::test_g4_dhalika_hum_defer_verdict_is_deferred` | segmentation_verdict=DEFERRED | SEGMENTED | RC10 |
| 44 | `TestGovernanceFixes::test_g4_dhalika_hum_defer_host_route_is_mabni_deferred` | host_route=MABNI_DEFERRED | OPERATOR_BOUNDARY | RC10 |

---

## توزيع الأسباب

| رمز السبب | عدد الفشل | الفئة |
|-----------|-----------|-------|
| RC1 (CWD Pollution) | 13 | IMPLEMENTATION_DEFECT |
| RC2 (is_op=False Group 8) | 8 | CATALOG_DATA_DEFECT (يحتاج قرار عقد) |
| RC3 (كم bare ambiguity) ← RC1 | 4 | BARE_INDEX_COLLISION (مُسبَّب من RC1) |
| RC4 (كأين Unicode collision) ← RC1 | 5 | BARE_INDEX_COLLISION (مُسبَّب من RC1) |
| RC5 (_verdict_from bare DEFER) | 6 | IMPLEMENTATION_DEFECT |
| RC6 (DEFER+is_op=False→MABNI) | 2 | IMPLEMENTATION_DEFECT (يحتاج قرار عقد RC2) |
| RC7 (pipeline attachment cond.) | 8 | IMPLEMENTATION_DEFECT |
| RC8 (missing catalog entries) | 4 | DATA_SOURCE_ISSUE |
| RC9 (madd-yaa sukun compat.) | 1 | IMPLEMENTATION_DEFECT |
| RC10 (DEFER propagation) | 2 | IMPLEMENTATION_DEFECT |

**ملاحظة**: مجموع الأسباب > 44 لأن بعض الفشل له سببان (RC1+RC2 أو RC7+RC8).

---

## ترتيب الإصلاح (dependency order)

```
RC1  →  حل RC3, RC4 (الـ CWD هو مصدرهما)
RC2  →  حل RC6 (بعد تحديد is_operator الكنسي)
RC5  →  مستقل (إصلاح _verdict_from)
RC7  →  مستقل (إصلاح شرط pipeline)
RC8  →  مستقل (إضافة مداخل للكتالوج)
RC9  →  مستقل (إصلاح _diacritics_compatible)
RC10 →  مستقل (إصلاح recognize_token DEFER handling)
```

**قرار مطلوب قبل المضي**: RC2 — هل كَمْ/كَأَيِّنْ/كَذَا/كَيْتَ تُعامَل كـ is_operator=True؟ (راجع جدول العقد الدلالي)
