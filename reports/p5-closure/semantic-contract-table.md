# P5 Closure — جدول العقد الدلالي الكنسي
## HOKOM-P5-CANONICAL-CONTRACT § Section 4
## الحالة: **APPROVED — SEMANTIC_CONTRACT_STATUS = APPROVED**

---

## القرار الجوهري

```
GROUP8_BOOLEAN_GLOBAL     = REJECTED
LICENSE_SPECIFIC_OPERATOR = REQUIRED
```

`is_operator` ليس خاصية للسطح وحده، بل خاصية للـ **LexicalLicense**:

```python
LexicalLicense {
    surface           # السطح المشكول
    lexical_kind      # kind الدخل
    sense_id          # معرّف المعنى/الاستعمال
    is_operator       # Boolean: هل يفتح علاقة تركيبية/دلالية؟
    relation_type     # نوع العلاقة التي يفتحها
    required_complement  # ما يتطلبه الترخيص لاستكماله
    case_effect       # هل يؤثر على الإعراب؟
    context_requirements # شروط تنشيط الترخيص
}
```

**القواعد الإلزامية**:
- الاسم قد يكون `is_operator=True` إذا فتح علاقة تركيبية أو دلالية
- الحرف لا يشترط أن يغير الإعراب حتى يكون operator
- لا تستخدم POS وحده لتحديد is_operator
- لا تجعل Group Number يفرض verdict موحدًا
- bare ambiguity لا تتحول إلى ACCEPT

---

## الأحكام الكنسية المعتمدة

### كَمْ
```
is_operator = True
relation    = TAMYIZ_QUANTITY
```
| الشكل | الحكم | الشرط |
|-------|-------|-------|
| كَمْ (مشكول، مرخَّص) | OPERATOR_BOUNDARY | structural_verdict = ACCEPT |
| كم (مجرد/ملتبس) | OPERATOR_DEFERRED | structural_verdict = DEFER |
| bare → bare ACCEPT مجرد | OPERATOR_DEFERRED | candidate محفوظ، لا ترقية إلى ACCEPT |

**تغيير الكتالوج**: `is_operator: False → True`

---

### كَأَيِّنْ
```
is_operator = True
relation    = TAMYIZ_QUANTITY
```
| الشكل | الحكم | الشرط |
|-------|-------|-------|
| كَأَيِّنْ (مشكول) | OPERATOR_BOUNDARY | structural_verdict = ACCEPT |
| كأين (مجرد/Unicode-ambiguous) | OPERATOR_DEFERRED | structural_verdict = DEFER |

**تغيير الكتالوج**: `is_operator: False → True`
**إصلاح إضافي**: Unicode collision في _by_bare بين نسختَي كَأَيِّنْ (RC4)

---

### كَذَا — ترخيصان منفصلان
```
لا يجوز إعطاء كَذَا حكمًا مطلقًا واحدًا اعتمادًا على السطح وحده.
```

**الترخيص أ — KADHA_NUMERIC_TAMYIZ**:
```
sense_id    = KADHA_NUMERIC_TAMYIZ
is_operator = True
relation    = TAMYIZ_QUANTITY
verdict     = OPERATOR_BOUNDARY (عند وجود سياق العدد/التمييز)
```

**الترخيص ب — KADHA_GENERIC_KINAYA**:
```
sense_id    = KADHA_GENERIC_KINAYA
is_operator = False
relation    = null
verdict     = MABNI_BOUNDARY (عند وجود سياق الكناية العامة)
```

**عند غياب السياق أو عدم كفايته**:
```
verdict = DEFER
```
حتى لو كانت مشكولة؛ لأن التشكيل لا يحسم أي الاستعمالين مقصود.

**تداعي على الاختبارات**: اختبارات كَذَا الحالية (test_kadha_vocalized_operator_boundary, test_kadha_unvocalized_operator_deferred) تحتاج إعادة كتابة بسياق. **لا تحديث لـ expected outputs قبل إنشاء التراخيص المنفصلة واختبارات السياق**.

---

### كَيْتَ
```
is_operator = False
relation    = null
verdict     = MABNI_BOUNDARY
```
لأنها كناية عن حديث أو شيء محكي، ليست عامل كمية يطلب تمييزًا.
**لا تغيير في الكتالوج**.

---

### هَلْ
```
ADD_TO_OPERATORS_CATALOG = True
is_operator = True
relation    = INTERROGATIVE_PREDICATION
case_effect = False
verdict     = OPERATOR_BOUNDARY (عند المطابقة المرخصة)
```
`هل` حرف استفهام يفتح علاقة تصديقية (يطلب الإجابة بنعم/لا) — operator بمعنى Hokom حتى دون تأثير إعرابي.
**تغيير الكتالوج**: إضافة صف جديد لهَلْ.

---

## خريطة العقد — الـ15 سطحاً (محدَّثة)

| السطح | is_op الكنسي | الملاحظة | verdict (ACCEPT) | verdict (DEFER) | تغيير مطلوب |
|-------|-------------|---------|-----------------|-----------------|-------------|
| كَمْ | **True** | TAMYIZ_QUANTITY | OPERATOR_BOUNDARY | OPERATOR_DEFERRED | RC2: catalog + RC1 + RC5 |
| كَأَيِّنْ | **True** | TAMYIZ_QUANTITY | OPERATOR_BOUNDARY | OPERATOR_DEFERRED | RC2: catalog + RC1 + RC4 + RC5 |
| كَذَا | **Dual** | Context-dependent | DEFER (no context) | DEFER | RC2: dual license + tests جديدة |
| كَيْتَ | False | محكي | MABNI_BOUNDARY | — | لا تغيير |
| مِائَةَ | True ✓ | عدد | OPERATOR_BOUNDARY ✓ | OPERATOR_DEFERRED | RC5 فقط |
| أَلْفَ | True ✓ | عدد | OPERATOR_BOUNDARY ✓ | OPERATOR_DEFERRED | RC5 فقط |
| أُلُوفَ | True ✓ | عدد | OPERATOR_BOUNDARY ✓ | OPERATOR_DEFERRED | RC5 فقط |
| مَلَايِينَ | True ✓ | عدد | OPERATOR_BOUNDARY ✓ | OPERATOR_DEFERRED | RC5 فقط |
| عَشَرَةَ | True ✓ | عدد | OPERATOR_BOUNDARY ✓ | — | لا تغيير |
| هَلْ | **True (جديد)** | INTERROGATIVE_PREDICATION | OPERATOR_BOUNDARY | — | إضافة ops_catalog |
| أَنَّى | True ✓ | شرط | OPERATOR_BOUNDARY | OPERATOR_DEFERRED | RC1 فقط |
| أَ | True ✓ | استفهام | OPERATOR_BOUNDARY ✓ | **OPERATOR_DEFERRED** | RC5 فقط |
| عَنْ | True ✓ | جر | OPERATOR_BOUNDARY ✓ | OPERATOR_DEFERRED | RC5 فقط |
| إِنَّ | True ✓ | توكيد | **OPERATOR_BOUNDARY** | OPERATOR_DEFERRED | RC1 فقط |
| ذَلِكَ | False ✓ | إشارة | MABNI_BOUNDARY ✓ | — | RC7 (attachment) |

---

## خارطة الطريق للإصلاحات (RC1–RC10) بعد القرار

### يمكن تنفيذها فوراً (لا تحتاج قرارًا إضافياً):

| RC | الملف | الإصلاح | يحل فشل # |
|----|-------|---------|-----------|
| RC1 | `pipeline/p5_lexical/mabni_inventory.py` | CWD guard في `_load_mabniyat_dir` | 1,2,4-9,11,13,17 |
| RC2-كَمْ | `data/operators_catalog_split_vocalized_corrected.csv` | is_operator: False→True لكَمْ | 10,14,15,16,18,32,33,34 |
| RC2-كَأَيِّنْ | نفس الملف | is_operator: False→True لكَأَيِّنْ | 19,20,25,30,31 |
| RC5 | `pipeline/p5_lexical/mabni_projection.py` | `_verdict_from`: DEFER+bare→OPERATOR_DEFERRED لا OPERATOR_BOUNDARY | 3,12,23,24,28,29 |
| RC7 | `hokom_pipeline.py` | attachment condition: MabniBoundary أيضاً | 35,37,39,42 |
| RC8 | `data/02_mabniyat/*.json` | إضافة TANIKA, DHANIKA, THAMM_KAF, HAHUNA_KAF | 36,38,40,41 |
| RC9 | `mabniyat_attachment.py` | `_diacritics_compatible`: sukun على madd-yaa متوافق | 35 |
| RC10 | `mabniyat_attachment.py` | `recognize_token`: P4=DEFER → segmentation_verdict=DEFERRED | 43,44 |

### تحتاج بنية جديدة (dual license لكَذَا):

| RC | الملف | الإصلاح | يحل فشل # |
|----|-------|---------|-----------|
| RC2-كَذَا | كود + كتالوج + اختبارات جديدة | LexicalLicense API + KADHA_NUMERIC_TAMYIZ + KADHA_GENERIC_KINAYA | 21,22,26 (بعد tests جديدة) |
| RC6 | `mabni_projection.py` | OPERATOR_DEFERRED لـ Group8 non-op (يتوقف على RC2-كَذَا) | 21,26 |

**ملاحظة**: فشل #21 و#22 و#26 (كَذَا) لا يُحسمان بالبنية الحالية — تحتاج dual license أولاً.

---

## العدد المتوقع للفشل بعد كل مجموعة إصلاحات

| بعد | الفشل المتبقي |
|-----|--------------|
| RC1 فقط | ~31 (تحل RC3, RC4 ضمنياً) |
| RC1 + RC2(كم+كأين) | ~22 |
| + RC5 | ~16 |
| + RC7 + RC8 + RC9 | ~8 |
| + RC10 | ~6 |
| + RC2(كَذَا dual license) | ~3 فشل متبقية (كَذَا context-dependent) |
| بعد tests كَذَا السياقية | **0** |

---

## الحالة النهائية

```
SEMANTIC_CONTRACT_STATUS   = APPROVED
GROUP8_BOOLEAN_GLOBAL      = REJECTED
LICENSE_SPECIFIC_OPERATOR  = REQUIRED
KADHA_DUAL_LICENSE         = REQUIRED (context-dependent)
HAL_ADD_TO_CATALOG         = REQUIRED
KAM_IS_OPERATOR            = True (معتمد)
KAAYYIN_IS_OPERATOR        = True (معتمد)
KAYTA_IS_OPERATOR          = False (معتمد)
```
