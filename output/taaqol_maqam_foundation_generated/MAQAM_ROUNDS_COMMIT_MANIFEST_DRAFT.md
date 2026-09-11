# MAQAM_ROUNDS_COMMIT_MANIFEST_DRAFT

TASK = MAQAM_ROUNDS_COMMIT_MANIFEST_PREPARATION_ONLY
MODE = READ_ONLY_AUDIT + SINGLE_REPORT_WRITE (no add / stage / commit / push / reset / checkout / clean / delete)
REPO = /Users/husseinhiyassat/hokom
BRANCH = feature/closure-cw1-cw2-foundation-01
HEAD = a5c43fb8f9d4cbb7756de1823d5405349193c17c

> مسودّة manifest انتقائية لجولات المقام/النازلة. **لا يُنفَّذ أي التزام.** الغرض: مراجعة المالك قبل أي commit.
> ملاحظة: كل ملفّات المجموعات المقترحة حالتها في porcelain = `??` (untracked)، ما لم يُذكر خلاف ذلك.

---

## أ) مجموعات INCLUDE_CANDIDATE (متجانسة — على مستوى المجموعة)

### G1 — مخرجات جولات المقام
- path (glob): `output/taaqol_maqam_foundation_generated/**`
- file_count: **141**
- status: `??` (untracked, مجلد مطويّ في porcelain كسطر واحد)
- category: MAQAM_ROUND_OUTPUT (تقارير AR_05..AR_25 + JSON + matrices + guards + residuals + owner-requests + هذا الـ manifest + تقرير التجميد)
- inclusion_cause: نواتج مباشرة لجولات النازلة/المقام 02..25 المولَّدة بالكود.
- inclusion_conditions: أن تكون مولَّدة من `scripts/taaqol_maqam_foundation/*` وقابلة لإعادة التوليد؛ لا روابط حيّة؛ EXTERNAL_REFS=0.
- preventers: لا شيء ضمن المجموعة (لا بيانات ثقيلة ولا أسرار)؛ يُستبعَد أي ملف ثنائي لو ظهر.
- verdict: **INCLUDE_CANDIDATE**

### G2 — مولّدات جولات المقام
- path (glob): `scripts/taaqol_maqam_foundation/**`
- file_count: **28**
- status: `??`
- category: MAQAM_ROUND_GENERATOR (سكربتات build/render لكل جولة)
- inclusion_cause: الكود المصدر الذي يولّد G1؛ لازم لإعادة الإنتاج البايتية.
- inclusion_conditions: Python قياسي بلا تبعيات شبكة/قرص خارج WORKDIR.
- preventers: لا شيء.
- verdict: **INCLUDE_CANDIDATE**

### G3 — اختبارات جولات المقام (بادئة test_taaqol_)
- path (glob): `tests/test_taaqol_*`
- file_count: **43**
- status: `??`
- category: MAQAM_ROUND_TEST
- inclusion_cause: اختبارات دستورية/حراس لكل جولة (02..25) — تثبت عدم انتهاك الحدود.
- inclusion_conditions: تمرّ ضمن regression المقام (آخر تشغيل: 348 passed مرتين).
- preventers: لا شيء.
- verdict: **INCLUDE_CANDIDATE**

---

## ب) ملفات مُفردة خاضعة لحكم فردي

| path | status | category | inclusion_cause | inclusion_conditions | preventers | verdict |
|---|---|---|---|---|---|---|
| `tests/test_hokom_taaqol_reference_matrix_and_framenet_roadmap_10.py` | ?? | MAQAM_ROUND_TEST (جولة 10) | اختبار الجولة 10 (reference matrix/FrameNet) وإن اختلفت البادئة | يمرّ ضمن regression | لا شيء | **INCLUDE_CANDIDATE** |
| `tests/taaqol_integration/test_nazila_matrix_generator.py` | ?? | NAZILA_TOKEN_SOURCE_TEST | يختبر مولّد مصفوفة النازلة الذي ينتج جدول t000..t009 المعتمد في كل تقارير المقام | تأكيد أنه ضمن مسار النازلة لا مسار آخر | قد يجرّ تبعيات مسار النازلة الأقدم | **DEFER_REVIEW** |
| `docs/HOKOM_TAAQOL_REFERENCE_MATRIX_AND_FRAMENET_ROADMAP_10.md` | ?? | MAQAM_DOC (جولة 10) | وثيقة الجولة 10 | صلة صريحة بجولة مرقّمة | لا شيء | **INCLUDE_CANDIDATE** |
| `docs/HOKOM_TAAQOL_REFERENCE_SOURCE_MANIFEST_10.json` | ?? | MAQAM_DOC (جولة 10) | manifest مراجع الجولة 10 | JSON نصي بلا روابط حيّة | تحقّق من عدم وجود URLs | **INCLUDE_CANDIDATE** |
| `docs/HOKOM_TAAQOL_MASALA_TAKYIF_RULES_CONSTITUTION_11.md` | ?? | MAQAM_DOC (جولة 11) | دستور التكييف (جولة 11) | صلة صريحة بجولة مرقّمة | لا شيء | **INCLUDE_CANDIDATE** |
| `docs/MAQAM_CANONICAL_INTEGRATION_BLOCKER_REPORT_02.md` | ?? | MAQAM_DOC (جولة 02) | تقرير الجولة 02 | صلة صريحة | لا شيء | **INCLUDE_CANDIDATE** |
| `docs/MAQAM_DEFERRED_CONSUMERS_CLOSURE_02.md` | ?? | MAQAM_DOC (جولة 02) | إغلاق المستهلكين المؤجّلين (جولة 02) | صلة صريحة | لا شيء | **INCLUDE_CANDIDATE** |
| `docs/MAQAM_THEORY_SOURCE_MANIFEST.json` | ?? | MAQAM_SOURCE_MANIFEST | manifest مصدر نظرية المقام (SOURCE_1، PDF كامل + sha) | JSON نصي فقط (لا يشمل الـ PDF نفسه) | لا يُدرَج أي PDF مرفق | **INCLUDE_CANDIDATE** |
| `docs/MAQAM_THEORY_SOURCE_2_MANIFEST.json` | ?? | MAQAM_SOURCE_MANIFEST | manifest SOURCE_2 (مقتطف المالك + hash؛ لا PDF كامل) | JSON نصي فقط؛ لا ادعاء FULL_PDF | لا يُدرَج أي مرفق ثنائي | **INCLUDE_CANDIDATE** |
| `docs/MAQAM_THEORY_CONSTITUTION.md` | ?? | MAQAM_DOC | دستور نظرية المقام الأساس | تأكيد أنه نسخة الجولات الحالية لا مسودّة قديمة | لا شيء واضح | **DEFER_REVIEW** |
| `docs/MAQAM_ARCHITECTURE_AND_OWNERSHIP.md` | ?? | MAQAM_DOC | معمارية/ملكية المقام | تأكيد التوافق مع الحالة الراهنة | قد يكون أوسع من جولات النازلة | **DEFER_REVIEW** |
| `docs/maqam_theory_sources/` | ?? | MAQAM_SOURCE_MATERIAL (مجلد) | مواد مصدرية للمقام | فحص المحتوى (قد يضم PDF/ثنائيات) | يُرجَّح احتواؤه ملفّات ثقيلة/ثنائية | **DEFER_REVIEW** |
| `output/taaqol_nazila_matrix_generated/` | ?? | NAZILA_TOKEN_SOURCE (مجلد) | يحوي `HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv` (مصدر t000..t009) لكن يخلط مخرجات مسار النازلة الأقدم (ARABIC_NET/t003/إصلاحات) | فصل ملف CSV التبعية عن الباقي | خلط محتوى غير خاص بجولات 02..25 | **DEFER_REVIEW** |

---

## ج) مُستبعَد صراحةً (EXCLUDE)

| path/pattern | السبب |
|---|---|
| `.venv-taaqol/` | بيئة افتراضية — لا تُلتزم |
| `.DS_Store` (وكل نسخها) | ضجيج نظام ملفات |
| `.gitignore` (تعديل) | تغيير بنية التتبّع — قرار منفصل، خارج نطاق جولات المقام |
| `cl16_root_wazn/**` | مسار آخر (root/wazn) غير جولات المقام |
| `pipeline/**` | مسار خطّ المعالجة العام |
| `data/**` (docx/pdf/jsonl/i3rab…) | بيانات ثقيلة/ثنائية |
| `audit/**` | غير مرتبط مباشرة بجولات المقام |
| `csv_operator_*` (json/html) | كتالوج عوامل — مسار آخر |
| `docs/*.pdf`, `docs/*.crdownload`, `docs/*.docx`, `docs/*.zip` (منها `maqam.pdf`, `moqam.pdf.crdownload`, `TAAQOL_MAQAM_THEORY_IMPLEMENTATION_01.zip`, `HOKOM_TAAQOL_OUTPUT_CONTRACT_AR.docx`) | ملفّات ثنائية/تنزيلات ناقصة — تُستبعَد بحكم القاعدة |
| `"TAAQOL_MAQAM_THEORY_IMPLEMENTATION_01 (1).zip"` | أرشيف ثنائي |
| `docs/LAYER5_LAYER6_HOKOM_WAVE11_INTEGRATION_HANDOFF.md` (M) | مسار wave11 لا جولات المقام |
| `docs/B3_R1_R4_DESIGN.md`, `docs/PIPT_CONSTITUTION.md`, `docs/PROJECT_INDEPENDENT_ADVERSARIAL_DELIVERY_PROTOCOL_V1_1.md` | وثائق مسارات/بروتوكولات أخرى |
| `docs/governance/**`, `tests/governance/**` (6 اختبارات) | حوكمة عامة غير جولات النازلة |
| `vendor/**` وأي submodule entry | ممنوع لمس vendor/submodules |
| كل `other/unclassified` (≈845 ملفًا) | خارج نطاق جولات المقام صراحةً |

---

## د) ملفات DEFER_REVIEW أخرى (صلة محتملة غير مؤكّدة)

| path | السبب في التأجيل |
|---|---|
| `docs/FRACTAL_BIRTH_REVIEW.md` | نواة fractal-birth مرتبطة بمسار النازلة لكنها مسار مجاور لا جولات المقام المرقّمة |
| `docs/MADLUL_TEXT_LAYER_HANDOFF.md` | طبقة المدلول — صلة غير مباشرة |
| `docs/HOKOM_CANONICAL_SCOPE_AND_AUTHORITY_BOUNDARY.md` | حدود سلطة عامة — يراجعها المالك |
| `docs/FILE_HASH_IS_NOT_CONTENT_HASH.md` | ملاحظة تقنية عامة |
| `docs/B3_R1_R4_DESIGN.md` مذكور أعلاه كـ EXCLUDE | — |

---

## هـ) الملخص

| المقياس | القيمة |
|---|---|
| INCLUDE_CANDIDATE_COUNT | **223** (G1=141 + G2=28 + G3=43 + 11 ملف/وثيقة مفردة: test_10، docs 10/11/02×2، source manifests ×2) |
| EXCLUDE_COUNT | مجموعات كبيرة: ≈845 (other/unclassified) + ثنائيات docs + governance(6 tests + docs/governance) + vendor — لا تُدخَل |
| DEFER_REVIEW_COUNT | **6** (test_nazila_matrix_generator، MAQAM_THEORY_CONSTITUTION، MAQAM_ARCHITECTURE_AND_OWNERSHIP، docs/maqam_theory_sources/، output/taaqol_nazila_matrix_generated/، MADLUL/FRACTAL/scope كمجموعة مراجعة) |
| OTHER_UNCLASSIFIED_INCLUDED | **NO** |
| VENDOR_INCLUDED | **NO** |
| DESTRUCTIVE_COMMANDS | **NO** |
| COMMIT_CREATED | **NO** |
| PUSH_EXECUTED | **NO** |

تنبيه اتساق: العدّ التفصيلي (INCLUDE=223) يشمل 3 وثائق docs من الجولة 10/11/02 + وثيقتَي source-manifest + اختبار الجولة 10؛ أما تصنيف الجولة السابقة (docs=23) فكان مطويًّا على مستوى المجلد. الأرقام هنا على مستوى الملف.

---

## و) أوامر مقترحة للمراجعة فقط (لا تُنفَّذ)

```bash
# استعراض القوائم الدقيقة (قراءة فقط):
git -C /Users/husseinhiyassat/hokom status --porcelain --untracked-files=all \
  | awk '{ $1=""; sub(/^ /,""); print }' | grep -E '^output/taaqol_maqam_foundation_generated/'
git -C /Users/husseinhiyassat/hokom status --porcelain --untracked-files=all \
  | awk '{ $1=""; sub(/^ /,""); print }' | grep -E '^scripts/taaqol_maqam_foundation/'
git -C /Users/husseinhiyassat/hokom status --porcelain --untracked-files=all \
  | awk '{ $1=""; sub(/^ /,""); print }' | grep -E '^tests/test_taaqol_'

# فحص خلوّ مجموعات INCLUDE من روابط حيّة قبل أي التزام (قراءة فقط):
grep -RIl 'https\?://\|www\.' \
  /Users/husseinhiyassat/hokom/output/taaqol_maqam_foundation_generated \
  /Users/husseinhiyassat/hokom/scripts/taaqol_maqam_foundation || echo "NO_LIVE_LINKS"

# (لا يُنفَّذ الآن) staging انتقائي مقترح بعد موافقة المالك — للعرض فقط:
#   git -C /Users/husseinhiyassat/hokom add \
#     output/taaqol_maqam_foundation_generated scripts/taaqol_maqam_foundation 'tests/test_taaqol_*'
#   ثم مراجعة git status قبل أي commit — والالتزام قرار مالك منفصل.
```

---

NEXT_SAFE_STEP = OWNER_REVIEW_MANIFEST_BEFORE_COMMIT
