# MAQAM_ROUNDS_DEFER_REVIEW_RESOLUTION

TASK = MAQAM_MANIFEST_DEFER_REVIEW_RESOLUTION_ONLY
MODE = READ_ONLY_DEPENDENCY_AUDIT + SINGLE_APPENDIX_WRITE (no add / stage / commit / push / reset / checkout / clean / delete)
REPO = /Users/husseinhiyassat/hokom · BRANCH = feature/closure-cw1-cw2-foundation-01 · HEAD = a5c43fb8f9d4cbb7756de1823d5405349193c17c
BASE = output/taaqol_maqam_foundation_generated/MAQAM_ROUNDS_COMMIT_MANIFEST_DRAFT.md

> ملحق يحسم بنود DEFER_REVIEW الستة بقرارات مبنية على **دليل تبعية فعلي** (grep على مولّدات/اختبارات المقام). لا يُنفَّذ أي التزام.

---

## 1) tests/test_nazila_matrix_generator.py

| الحقل | القيمة |
|---|---|
| path | `tests/taaqol_integration/test_nazila_matrix_generator.py` |
| current_verdict | DEFER_REVIEW |
| dependency_evidence | يستورد من `scripts/build_taaqol_nazila_matrix.py` ويقرأ REFERENCE في `stage2-september-26/…`؛ **لا** يستهدف `scripts/taaqol_maqam_foundation/*`. ليس ضمن regression المقام (02..25). |
| cause | اختبار مسار النازلة الأقدم (HOKOM_TO_TAAQOL_NAZILA_ANALYSIS_PIPELINE_01)، لا جولات المقام. |
| conditions | كان سيُدرَج فقط لو استهدف مولّدات المقام أو لزم regressionها. |
| preventers | يجرّ تبعيات مسار مختلف (bridge + reference file خارج الحزمة). |
| new_verdict | **EXCLUDE** |
| notes | يُلتزم لاحقًا ضمن حزمة مسار النازلة المستقل إن رغب المالك، لا هنا. |

## 2) docs/MAQAM_THEORY_CONSTITUTION.md

| الحقل | القيمة |
|---|---|
| path | `docs/MAQAM_THEORY_CONSTITUTION.md` |
| current_verdict | DEFER_REVIEW |
| dependency_evidence | `grep` على `scripts/taaqol_maqam_foundation/` و`tests/`: **غير مُشار إليه** من أي مولّد أو اختبار. |
| cause | تنظير عام لنظرية المقام غير مربوط بـ artifact/test في هذه الحزمة. |
| conditions | يصير INCLUDE لو ربطه مولّد/اختبار مستقبلًا. |
| preventers | لا تبعية مباشرة الآن. |
| new_verdict | **DEFER_REVIEW** |
| notes | قرار المالك: قد يُضمّ كوثيقة أساس، لكنه ليس لازمًا لإعادة إنتاج الجولات. |

## 3) docs/MAQAM_ARCHITECTURE_AND_OWNERSHIP.md

| الحقل | القيمة |
|---|---|
| path | `docs/MAQAM_ARCHITECTURE_AND_OWNERSHIP.md` |
| current_verdict | DEFER_REVIEW |
| dependency_evidence | **مُشار إليه فعلًا** من `scripts/taaqol_maqam_foundation/deferred_consumers.py` و`maqam6_reference_ratified_closure_06.py`. |
| cause | يثبت ownership/gates تعتمده مولّدات جولتَي 02/06. |
| conditions | نصّي بلا روابط حيّة. |
| preventers | لا شيء. |
| new_verdict | **INCLUDE_CANDIDATE** |
| notes | التصحيح: **المعمارية** هي المربوطة (لا الدستور). |

## 4) docs/maqam_theory_sources/ (فُصِّل ملفًّا ملفًّا — لا إدراج للمجلد كاملًا)

| path | current | dependency_evidence | cause | conditions | preventers | new_verdict | notes |
|---|---|---|---|---|---|---|---|
| `docs/maqam_theory_sources/المقام_والقرينة_الحالية__OWNER_QUOTED_EXCERPT.md` | DEFER | مقتطف المالك لـ SOURCE_2 (مذكور في `MAQAM_THEORY_SOURCE_2_MANIFEST.json`) | نص المصدر-2 الوحيد المتاح (لا PDF كامل) | ملف نصّي صغير (2.6KB) | لا شيء | **INCLUDE_CANDIDATE** | يوثّق أن SOURCE_2 مقتطف لا PDF كامل. |
| `docs/maqam_theory_sources/اساسيات_المقام.pdf` | DEFER | ثنائي 354KB | مصدر SOURCE_1 | — | ملف ثنائي ثقيل (قاعدة استبعاد docx/pdf) | **EXCLUDE** | الـ sha محفوظ في `MAQAM_THEORY_SOURCE_MANIFEST.json`؛ لا داعي لالتزام الثنائي. |
| `docs/maqam_theory_sources/اساسيات_المقام.txt` | DEFER | استخراج نصّي من الـ PDF (42KB) | نص مستخرَج | — | الاستخراج غير موثوق (SOURCE_TEXT_EXTRACTION_UNCERTAIN — لا يُبنى عليه) | **DEFER_REVIEW** | قرار المالك؛ لا يُعتمد كمصدر حكم. |

المجلد كاملًا: **NOT INCLUDED**.

## 5) output/taaqol_nazila_matrix_generated/ (المجلد كاملًا ممنوع — إدراج التبعيات المفردة فقط)

| path | current | dependency_evidence | cause | conditions | preventers | new_verdict | notes |
|---|---|---|---|---|---|---|---|
| `output/taaqol_nazila_matrix_generated/HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv` | DEFER | يقرؤه كل مولّدات المقام (`load_tokens`) كمصدر جدول t000..t009 | تبعية إلزامية لإعادة إنتاج تقارير الجولات | CSV نصّي (4081 بايت) موجود | لا شيء | **INCLUDE_CANDIDATE** | العمود الفقري لجدول الكلمات العشر. |
| `output/taaqol_nazila_matrix_generated/PROPOSITIONAL_CONTENT_CANDIDATE_08.json` | DEFER | يُشار إليه من `maqam6_reference_ratified_closure_06.py` و`final_ifadah_targeted_info_request_08.py` | مدخل جولتَي 06/08 | JSON نصّي موجود | لا شيء | **INCLUDE_CANDIDATE** | — |
| `output/taaqol_nazila_matrix_generated/TAAQOL_NAZILA_MANAT_RESULT.csv` | DEFER | يُشار إليه من `normative_source_birth_07.py` | مدخل جولة 07 | CSV نصّي موجود | لا شيء | **INCLUDE_CANDIDATE** | — |
| باقي المجلد (`ARABIC_NET_*`, `*t003*`, `*REPAIR*`, `roadmap/**`, `*MADLUL*`, …) | DEFER | لا يُشار إليه من مولّدات/اختبارات المقام | مخرجات مسار النازلة الأقدم/الإصلاحات | — | خارج جولات 02..25 | **EXCLUDE** | NAZILA_MATRIX_WHOLE_DIR_INCLUDED = NO. |

## 6) مجموعة MADLUL / FRACTAL / scope (أسماء فعلية)

| path | current | dependency_evidence | cause | conditions | preventers | new_verdict | notes |
|---|---|---|---|---|---|---|---|
| `docs/FILE_HASH_IS_NOT_CONTENT_HASH.md` | DEFER | غير مُشار إليه من مولّدات/اختبارات المقام | ملاحظة تقنية عامة | — | لا صلة مباشرة بجولات الحكم/المناط | **EXCLUDE** | — |
| `docs/FRACTAL_BIRTH_REVIEW.md` | DEFER | يخص نواة `scripts/taaqol_fractal_birth_kernel.py` (مسار مجاور) | مراجعة fractal-birth | — | ليست جولات المقام المرقّمة | **EXCLUDE** | حزمة مستقلة إن رغب المالك. |
| `docs/HOKOM_CANONICAL_SCOPE_AND_AUTHORITY_BOUNDARY.md` | DEFER | حدود سلطة عامة | وثيقة حوكمة | — | غير خاصة بجولات 02..25 | **EXCLUDE** | — |
| `docs/MADLUL_TEXT_LAYER_HANDOFF.md` | DEFER | طبقة المدلول (مسار النازلة) | تسليم طبقة | — | غير مربوط بجولات الحكم/المناط الحالية | **EXCLUDE** | — |

---

## العدادات المحدَّثة (بعد الحسم)

| المقياس | قبل | بعد |
|---|---|---|
| INCLUDE_CANDIDATE_COUNT | 223 | **228** (+5: MAQAM_ARCHITECTURE + OWNER_QUOTED_EXCERPT + NAZILA CSV + PROPOSITIONAL_CONTENT_08 + MANAT_RESULT) |
| DEFER_REVIEW_COUNT | 6 | **2** (MAQAM_THEORY_CONSTITUTION.md · اساسيات_المقام.txt) |
| EXCLUDE (من الحسم) | — | tests/test_nazila_matrix_generator.py · اساسيات_المقام.pdf · باقي `taaqol_nazila_matrix_generated/**` · MADLUL/FRACTAL/FILE_HASH/SCOPE (4) — إضافةً إلى مجموعات EXCLUDE الكبرى في المسودّة |
| OTHER_UNCLASSIFIED_INCLUDED | NO | **NO** |
| VENDOR_INCLUDED | NO | **NO** |
| NAZILA_MATRIX_WHOLE_DIR_INCLUDED | — | **NO** (3 ملفات مفردة فقط) |
| COMMIT_CREATED | NO | **NO** |
| PUSH_EXECUTED | NO | **NO** |
| DESTRUCTIVE_COMMANDS | NO | **NO** |

### قائمة INCLUDE المفردة النهائية من مجلد النازلة (الوحيدة المسموح إدراجها من ذلك المجلد)
```
output/taaqol_nazila_matrix_generated/HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv
output/taaqol_nazila_matrix_generated/PROPOSITIONAL_CONTENT_CANDIDATE_08.json
output/taaqol_nazila_matrix_generated/TAAQOL_NAZILA_MANAT_RESULT.csv
```

### أوامر مراجعة (قراءة فقط، لا تُنفَّذ)
```bash
# إعادة إثبات تبعيات مجلد النازلة الثلاث:
grep -RhoP 'taaqol_nazila_matrix_generated/[A-Za-z0-9_./-]+' \
  /Users/husseinhiyassat/hokom/scripts/taaqol_maqam_foundation/ | sort -u
# إعادة إثبات ربط المعمارية (وليس الدستور):
grep -RIl 'MAQAM_ARCHITECTURE_AND_OWNERSHIP' /Users/husseinhiyassat/hokom/scripts/taaqol_maqam_foundation/
```

NEXT_SAFE_STEP = OWNER_COMMIT_DECISION (INCLUDE_CANDIDATE = 228 ملفًّا؛ DEFER_REVIEW = 2؛ لا vendor، لا other/unclassified، لا مجلد نازلة كامل)
