# سجل المتطلبات قبل التوسع (الجولة 32 — تأسيسي فقط)

**قاعدة المالك:** الأسئلة التي ظهرت في جولة المناط ليست قانونًا كنسيًا لأنها من معرفة الوكيل. قبل التوسع خارج النازلة تُحوَّل إلى: قواعد بيانات / مصادر / قرارات مالك / بوابات سبب-شرط-مانع.

النازلة (النطاق الوحيد الآن): «مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا.»

**READY_FOR_EXPANSION = NO · لا حكم · لا مناط · لا تنزيل · لا جواب.**

## الأسئلة العشرة ⇐ متطلبات (لا وقائع)
- `REQ01_NO_CHILD` [FACT_REQUIREMENT] ⇐ هل ثبت أن الميت لا ولد له؟
  - لماذا: شرط الكلالة يتوقف على انتفاء الولد؛ لا يُفترض من معرفة الوكيل.
  - السجل/القاعدة: `factual_claim_registry` · المصدر: OWNER_SUPPLIED_FACT | حصر إرث موثّق · قرار المالك: تصديق واقعة انتفاء الولد
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ02_OTHER_HEIRS` [DATABASE_REQUIREMENT] ⇐ هل يوجد ورثة آخرون؟
  - لماذا: ترتيب الفروض والباقي يتوقف على حصر الورثة.
  - السجل/القاعدة: `inheritance_condition_registry` · المصدر: OWNER_SUPPLIED_FACT | حصر إرث · قرار المالك: اعتماد قائمة الورثة
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ03_HEIR_CAPACITY` [FACT_REQUIREMENT] ⇐ ما صفة الوارث الذي يريد الطرد؟
  - لماذا: جنبة الدعوى وصفة المدّعي تحدّدان موقع عبء الإثبات.
  - السجل/القاعدة: `factual_claim_registry` · المصدر: OWNER_SUPPLIED_FACT · قرار المالك: تحديد صفة الوارث
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ04_HOUSE_STATUS` [DATABASE_REQUIREMENT] ⇐ هل البيت كله تركة أم فيه حق/انتفاع/إذن سابق؟
  - لماذا: صفة المحل (تركة/حق/انتفاع) شرط لدخوله في القسمة أو خروجه.
  - السجل/القاعدة: `possession_yad_registry` · المصدر: سند ملكية/وقف/إذن (OWNER_SUPPLIED) · قرار المالك: تصديق صفة البيت
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ05_PRIOR_PERMISSION` [FACT_REQUIREMENT] ⇐ هل كان سكن الأخت بإذن المالك قبل موته؟
  - لماذا: الإذن السابق يقوّي جنبة بقاء اليد؛ واقعة تحتاج إثباتًا.
  - السجل/القاعدة: `possession_yad_registry` · المصدر: إقرار/بينة/قرينة (OWNER_SUPPLIED) · قرار المالك: تصديق واقعة الإذن
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ06_HAND_CREDIBLE` [GATE_REQUIREMENT] ⇐ هل يد الأخت معتبرة أم تكذبها قرائن؟
  - لماذا: اعتبار اليد بوابة سبب/شرط/مانع لا يقرّرها الوكيل من معرفته.
  - السجل/القاعدة: `possession_yad_registry` · المصدر: قرائن/بينة (OWNER_SUPPLIED) · قرار المالك: بوابة تقييم اليد مقابل القرائن
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ07_CLAIM_CONTENT` [FACT_REQUIREMENT] ⇐ ما الدعوى المحددة للوارث؟
  - لماذا: محل النزاع لا يُنشأ من الوكيل بل يُزوَّد.
  - السجل/القاعدة: `factual_claim_registry` · المصدر: صحيفة دعوى/إقرار (OWNER_SUPPLIED) · قرار المالك: اعتماد نص الدعوى
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ08_DEFENSE_CONTENT` [FACT_REQUIREMENT] ⇐ ما جواب الأخت؟
  - لماذا: موقف المدّعى عليه واقعة تُزوَّد لا تُفترض.
  - السجل/القاعدة: `factual_claim_registry` · المصدر: جواب/إقرار/إنكار (OWNER_SUPPLIED) · قرار المالك: اعتماد نص الجواب
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ09_EVIDENCE` [GATE_REQUIREMENT] ⇐ ما البينة؟
  - لماذا: عبء الإثبات بوابة (بينة/يمين) لا يقرّرها الوكيل.
  - السجل/القاعدة: `proof_burden_registry` · المصدر: بينة/شهود/وثائق (OWNER_SUPPLIED) · قرار المالك: بوابة عبء الإثبات
  - default_if_missing = DEFER · expansion_blocker = YES
- `REQ10_QARINA_STRENGTH` [GATE_REQUIREMENT] ⇐ هل توجد قرائن أقوى من مجرد اليد؟
  - لماذا: موازنة القرائن مقابل اليد بوابة مانع، لا معرفة وكيل.
  - السجل/القاعدة: `possession_yad_registry` · المصدر: قرائن مقارنة (OWNER_SUPPLIED) · قرار المالك: بوابة موازنة القرائن
  - default_if_missing = DEFER · expansion_blocker = YES

## السجلات الواجب بناؤها قبل التوسع
- `factual_claim_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: REQ01_NO_CHILD، REQ03_HEIR_CAPACITY، REQ07_CLAIM_CONTENT، REQ08_DEFENSE_CONTENT) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `owner_supplied_fact_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `source_requirement_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `normative_source_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `domain_candidate_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `hukm_candidate_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `manat_candidate_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `tanzil_requirement_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `proof_burden_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: REQ09_EVIDENCE) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `possession_yad_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: REQ04_HOUSE_STATUS، REQ05_PRIOR_PERMISSION، REQ06_HAND_CREDIBLE، REQ10_QARINA_STRENGTH) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `inheritance_condition_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: REQ02_OTHER_HEIRS) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `residual_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES
- `owner_ratification_registry` → MUST_BE_BUILT_BEFORE_EXPANSION (يغذّيه: —) · creates_fact=NO · creates_source=NO · owner_ratification=YES

---
*لا يجوز استعمال هذه الأسئلة كأسئلة تشغيل عامة قبل تسجيلها؛ وكل متطلب بلا سجل/مصدر/قرار مالك = DEFER.*
