# MAQAM_ROUNDS_FINAL_COMMIT_MANIFEST_LOCKED

TASK = MAQAM_FINAL_COMMIT_MANIFEST_LOCK → adjusted by MAQAM_SELECTIVE_COMMIT_ADJUST_TO_CSV_IGNORE_POLICY
MODE = READ_ONLY_AUDIT + SINGLE_MANIFEST_WRITE (no add -f / no gitignore edit / no push / no reset / no delete)
REPO = /Users/husseinhiyassat/hokom · BRANCH = feature/closure-cw1-cw2-foundation-01 · HEAD = a5c43fb8f9d4cbb7756de1823d5405349193c17c
BASE = MAQAM_ROUNDS_COMMIT_MANIFEST_DRAFT.md + MAQAM_ROUNDS_DEFER_REVIEW_RESOLUTION.md

## CSV POLICY (owner decision)
```
CSV_POLICY_DECISION = KEEP_STAR_CSV_IGNORED
COMMIT_CSV_FILES = NO
FORCE_ADD_CSV = NO
MODIFY_GITIGNORE = NO
CSV_FILES_INCLUDED = NO
CSV_IGNORED_BY_POLICY = YES          # .gitignore line 10: *.csv
CSV_REGENERABLE_FROM_SCRIPTS_AND_JSON = YES
```

> قائمة INCLUDE_FOR_COMMIT النهائية = **226 ملفًّا** (بعد إسقاط ملفَّي csv التبعيّين اللذين تمنعهما `*.csv`).
> جميعها `??` (untracked) وموجودة على القرص. لا csv ضمن الالتزام. ملفّات الحوكمة/الـ manifest لهذه الجلسة تقع داخل `output/taaqol_maqam_foundation_generated/` فتُعَدّ ذاتيًّا.

---

## أ) مجموعات INCLUDE_FOR_COMMIT (حقول على مستوى المجموعة)

### G1 — مخرجات جولات المقام (بلا csv)
- path (glob): `output/taaqol_maqam_foundation_generated/**` **باستثناء `*.csv`**
- file_count: **144** (لا يشمل أي csv؛ الـ 26 مصفوفة `*_MATRIX.csv` متجاهَلة بسياسة `*.csv` — انظر القسم «د»)
- git porcelain status: `??`
- category: MAQAM_ROUND_OUTPUT + SESSION_GOVERNANCE_ARTIFACT
- inclusion_cause: نواتج جولات النازلة/المقام (تقارير AR + JSON + guards + residuals + owner-requests) + سجلّات حوكمة الجلسة.
- inclusion_conditions: نصّية/JSON/HTML؛ EXTERNAL_REFS=0؛ بلا روابط حيّة؛ **بلا csv**.
- preventers: لا ثنائيات، لا أسرار، لا csv (متجاهَل بالسياسة).
- final_verdict: **INCLUDE_FOR_COMMIT**

### G2 — مولّدات جولات المقام
- path (glob): `scripts/taaqol_maqam_foundation/**`
- file_count: **28** · status `??` · category MAQAM_ROUND_GENERATOR
- inclusion_cause: الكود المولِّد لـ G1 (ومنه تُعاد مصفوفات csv عند الحاجة).
- inclusion_conditions: مكتبة قياسية فقط.
- preventers: لا شيء.
- final_verdict: **INCLUDE_FOR_COMMIT**

### G3 — اختبارات جولات المقام (بادئة test_taaqol_)
- path (glob): `tests/test_taaqol_*`
- file_count: **43** · status `??` · category MAQAM_ROUND_TEST
- inclusion_cause: اختبارات دستورية/حراس الجولات 02..25.
- inclusion_conditions: تمرّ ضمن regression المقام.
- preventers: لا شيء.
- final_verdict: **INCLUDE_FOR_COMMIT**

مجموع المجموعات = 144 + 28 + 43 = **215**.

---

## ب) INCLUDE_FOR_COMMIT المفردة (11 ملفًّا — بعد إسقاط csv)

| # | path | status | category | inclusion_cause | inclusion_conditions | preventers | final_verdict |
|---|---|---|---|---|---|---|---|
| 1 | `tests/test_hokom_taaqol_reference_matrix_and_framenet_roadmap_10.py` | ?? | MAQAM_ROUND_TEST (10) | اختبار الجولة 10 (خارج glob G3) | يمرّ ضمن regression | لا شيء | INCLUDE_FOR_COMMIT |
| 2 | `docs/HOKOM_TAAQOL_REFERENCE_MATRIX_AND_FRAMENET_ROADMAP_10.md` | ?? | MAQAM_DOC (10) | وثيقة الجولة 10 | نصّية | لا شيء | INCLUDE_FOR_COMMIT |
| 3 | `docs/HOKOM_TAAQOL_REFERENCE_SOURCE_MANIFEST_10.json` | ?? | MAQAM_DOC (10) | manifest مراجع الجولة 10 | JSON؛ EXTERNAL_REFS=0 | لا شيء | INCLUDE_FOR_COMMIT |
| 4 | `docs/HOKOM_TAAQOL_MASALA_TAKYIF_RULES_CONSTITUTION_11.md` | ?? | MAQAM_DOC (11) | دستور التكييف (11) | نصّية | لا شيء | INCLUDE_FOR_COMMIT |
| 5 | `docs/MAQAM_CANONICAL_INTEGRATION_BLOCKER_REPORT_02.md` | ?? | MAQAM_DOC (02) | تقرير الجولة 02 | نصّية | لا شيء | INCLUDE_FOR_COMMIT |
| 6 | `docs/MAQAM_DEFERRED_CONSUMERS_CLOSURE_02.md` | ?? | MAQAM_DOC (02) | إغلاق مستهلكين مؤجّلين (02) | نصّية | لا شيء | INCLUDE_FOR_COMMIT |
| 7 | `docs/MAQAM_THEORY_SOURCE_MANIFEST.json` | ?? | MAQAM_SOURCE_MANIFEST | manifest SOURCE_1 (sha للـ PDF) | JSON فقط | لا يُدرَج الـ PDF | INCLUDE_FOR_COMMIT |
| 8 | `docs/MAQAM_THEORY_SOURCE_2_MANIFEST.json` | ?? | MAQAM_SOURCE_MANIFEST | manifest SOURCE_2 (مقتطف + hash) | JSON؛ لا FULL_PDF | لا مرفق ثنائي | INCLUDE_FOR_COMMIT |
| 9 | `docs/MAQAM_ARCHITECTURE_AND_OWNERSHIP.md` | ?? | MAQAM_DOC (bound) | مُشار إليه من `deferred_consumers.py` + `maqam6_reference_ratified_closure_06.py` | نصّية | لا شيء | INCLUDE_FOR_COMMIT |
| 10 | `docs/maqam_theory_sources/المقام_والقرينة_الحالية__OWNER_QUOTED_EXCERPT.md` | ?? | MAQAM_SOURCE (SOURCE_2 excerpt) | نص SOURCE_2 الوحيد المتاح | نصّي 2.6KB | لا شيء | INCLUDE_FOR_COMMIT |
| 11 | `output/taaqol_nazila_matrix_generated/PROPOSITIONAL_CONTENT_CANDIDATE_08.json` | ?? | NAZILA_DEP | مدخل جولتَي 06/08 | JSON (ليس csv) | لا يُدرَج باقي المجلد | INCLUDE_FOR_COMMIT |

مجموع المفردة = **11**.

---

## ج) الإجمالي المقفل

| المجموعة | العدد |
|---|---|
| G1 `output/taaqol_maqam_foundation_generated/**` (بلا csv) | 144 |
| G2 `scripts/taaqol_maqam_foundation/**` | 28 |
| G3 `tests/test_taaqol_*` | 43 |
| مفردة (11) | 11 |
| **FINAL_INCLUDE_COUNT** | **226** |

تحقّق: 144 + 28 + 43 + 11 = **226** ✓

---

## د) EXCLUDED_BY_CSV_POLICY (منقول من INCLUDE بقرار سياسة *.csv)

| path | سبب الاستبعاد |
|---|---|
| `output/taaqol_nazila_matrix_generated/HOKOM_NAZILA_LINGUISTIC_ANALYSIS_RESULT.csv` | تمنعه قاعدة `.gitignore:10 *.csv`؛ COMMIT_CSV_FILES=NO؛ قابل لإعادة التوليد |
| `output/taaqol_nazila_matrix_generated/TAAQOL_NAZILA_MANAT_RESULT.csv` | نفس السبب |

**ملاحظة المصفوفات:** يوجد **26 ملف `*_MATRIX.csv`** داخل `output/taaqol_maqam_foundation_generated/` (مصفوفة كل جولة) — كلها متجاهَلة بسياسة `*.csv` ولا تدخل هذا الالتزام. جميعها **قابلة لإعادة التوليد** بايت-مطابقةً من مولّدات `scripts/taaqol_maqam_foundation/*` عبر `--matrix-out` (تغطّيها اختبارات الجولات). لم يُستخدَم `git add -f` ولم يُعدَّل `.gitignore`.

---

## هـ) EXCLUDED_BY_OWNER_DECISION (2 — DEFER سابق)

| path | السبب |
|---|---|
| `docs/MAQAM_THEORY_CONSTITUTION.md` | لا تبعية تنفيذية مثبتة؛ لجولة دستور مستقلة لاحقًا |
| `docs/maqam_theory_sources/اساسيات_المقام.txt` | استخراج نصّي غير موثوق؛ لجولة مصادر مستقلة لاحقًا |

---

## و) الحراس الصريحة

```
OTHER_UNCLASSIFIED_INCLUDED = NO
VENDOR_INCLUDED = NO
NAZILA_MATRIX_WHOLE_DIR_INCLUDED = NO   # ملف JSON مفرد واحد فقط من ذلك المجلد
DEFER_REVIEW_INCLUDED = NO
DOCX_PDF_ZIP_INCLUDED = NO
VENV_INCLUDED = NO
DS_STORE_INCLUDED = NO
GOVERNANCE_TESTS_INCLUDED = NO
CSV_FILES_INCLUDED = NO
FORCE_ADD_USED = NO
GITIGNORE_MODIFIED = NO
```

---

## ز) أمر التحقّق الحاسم (قراءة فقط — يُعيد توليد قائمة الـ 226)

```bash
cd /Users/husseinhiyassat/hokom
{ git status --porcelain --untracked-files=all | awk '{ $1=""; sub(/^ /,""); print }' \
    | grep -E '^(output/taaqol_maqam_foundation_generated/|scripts/taaqol_maqam_foundation/|tests/test_taaqol_)';
  printf '%s\n' \
    tests/test_hokom_taaqol_reference_matrix_and_framenet_roadmap_10.py \
    docs/HOKOM_TAAQOL_REFERENCE_MATRIX_AND_FRAMENET_ROADMAP_10.md \
    docs/HOKOM_TAAQOL_REFERENCE_SOURCE_MANIFEST_10.json \
    docs/HOKOM_TAAQOL_MASALA_TAKYIF_RULES_CONSTITUTION_11.md \
    docs/MAQAM_CANONICAL_INTEGRATION_BLOCKER_REPORT_02.md \
    docs/MAQAM_DEFERRED_CONSUMERS_CLOSURE_02.md \
    docs/MAQAM_THEORY_SOURCE_MANIFEST.json \
    docs/MAQAM_THEORY_SOURCE_2_MANIFEST.json \
    docs/MAQAM_ARCHITECTURE_AND_OWNERSHIP.md \
    "docs/maqam_theory_sources/المقام_والقرينة_الحالية__OWNER_QUOTED_EXCERPT.md" \
    output/taaqol_nazila_matrix_generated/PROPOSITIONAL_CONTENT_CANDIDATE_08.json ; } \
  | grep -v '\.csv$' | sort -u | wc -l   # يجب = 226
```

---

ROUND = MAQAM_SELECTIVE_COMMIT_ADJUST_TO_CSV_IGNORE_POLICY_NO_PUSH
FINAL_INCLUDE_COUNT = 226
CSV_FILES_INCLUDED = NO
CSV_IGNORED_BY_POLICY = YES
FORCE_ADD_USED = NO
GITIGNORE_MODIFIED = NO
EXCLUDED_BY_OWNER_DECISION_COUNT = 2
EXCLUDED_BY_CSV_POLICY_COUNT = 2 (+26 matrix csv ignored)
MANIFEST_LOCKED = YES
COMMIT_CREATED = (pending tests)
PUSH_EXECUTED = NO
