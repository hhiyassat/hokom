# خطة الاكتشاف الآلي للمصادر المعيارية (الجولة 22 — تخطيط فقط)

**PLANNING_ONLY = YES · AUTOMATED_SOURCE_DISCOVERY_EXECUTED = NO · NEW_SOURCE_BORN = NO · NORMATIVE_HUKM_CANDIDATE_OPENED = NO**

هذه وثيقة تسجّل *هندسة* الاكتشاف الآلي مستقبلًا، لا تنفيذه. لا بحث في الإنترنت، ولا مصدر جديد، ولا تصديق/اختيار مصدر، ولا حكم/مناط/تنزيل/جواب.

## 1. مصادر البحث الممكنة مستقبلًا
- القرآن الكريم
- كتب الحديث
- كتب الفقه
- كتب القضاء والسياسة الشرعية
- كتب القواعد الفقهية
- الموسوعات الفقهية
- قواعد بيانات حديثية أو فقهية إن وُجدت
- مصادر يزوّدها المالك فقط

## 2. أنواع المصدر
- `QURAN_AYAH`
- `HADITH`
- `FIQH_TEXT`
- `QADA_TEXT`
- `QAIDA_FIQHIYYA`
- `USUL_TEXT`
- `OWNER_SUPPLIED_TEXT`

## 3. مرحلة الترشيح الآلي
النظام لا يولّد مصدرًا مباشرة، بل ينتج `SOURCE_CANDIDATE_ONLY` (مرشّح فقط، ليس مصدرًا معياريًّا).

## 4. حقول كل مرشّح
- `source_candidate_id`
- `source_type`
- `authority_candidate`
- `text_candidate`
- `scope_candidate`
- `evidence_candidate`
- `domain_candidate_links`
- `served_needs`
- `not_served_needs`
- `confidence_basis`
- `risk_flags`
- `cause`
- `conditions`
- `preventers`
- `verdict`
- `residuals`

## 5. الحراس
- TEXT_SIGNAL ≠ SOURCE_CANDIDATE
- SOURCE_CANDIDATE ≠ NORMATIVE_SOURCE
- NORMATIVE_SOURCE ≠ HUKM
- SOURCE_DISCOVERY ≠ SOURCE_RATIFICATION
- AGENT_CANNOT_RATIFY_SOURCE = YES
- OWNER_RATIFICATION_REQUIRED = YES
- AUTHORITY_LEAK_PREVENTED = YES

## 6. قواعد المنع
- لا رابط حي داخل artifacts إذا EXTERNAL_REFS = 0.
- لا اعتماد نص ضعيف أو مختلف عليه دون علم مالك.
- لا استعمال حديث فيه تضعيف كعماد إلا بتصديق مالك صريح.
- لا نقل نص من باب إلى باب إلا برخصة تكييف.
- لا استعمال آية/حديث خارج نطاقه إلا مع SCOPE ومانع واضح.
- لا تحويل الحيازة إلى ملكية نهائية.
- لا تحويل المصدر إلى حكم.
- لا إغلاق المجال المركب دون قرار مالك.

## 7. طريقة الترتيب المستقبلية
رتّب المرشحات بحسب:
- قرب النص من residual
- نوع المصدر
- وضوح السلطة
- وضوح النص
- سلامة النطاق
- وجود مانع يمنع الحكم المباشر
- حاجة المالك للتصديق

## 8. سياسة الدليل
- EVIDENCE_POLICY_DEFAULT = CITATION_STRINGS_ONLY
- LIVE_EXTERNAL_LINKS_DEFAULT = NO
- EXTERNAL_REFS_DEFAULT = 0
- LINKS_ALLOWED_ONLY_BY_OWNER_DECISION = YES

## 9. سياسة الحرفية
TEXT_VERBATIM_STATUS ∈ {
  - ASSERTED_BY_OWNER_NOT_VERIFIED_BY_AGENT
  - VERIFIED_BY_AUTHORIZED_SOURCE_TOOL
  - NOT_VERIFIED
}
ولا يجوز للوكيل أن يدّعي حرفية نص شرعي من ذاكرته.

## 10. علاقة الخطة بالجولات السابقة
- ROUND_10: reference matrix + FrameNet roadmap
- ROUND_11: دستور التكييف
- ROUND_12: تطبيق مرشحات التكييف
- ROUND_13: المجال المركب
- ROUND_14: متطلبات المصدر
- ROUND_15: قالب تزويد المصدر
- ROUND_16: completeness audit
- ROUND_17: ولادة المصادر الثلاثة
- ROUND_18: mapping المصدر للمسألة
- ROUND_19_20: ثغرة السكنى (متطلب + تدقيق اكتمال)
- ROUND_21: ولادة مصدر السكنى وتغطية جميع المرشحات

## 11. مسودة المسار المستقبلي
- `FUTURE_ROUND_A` = SOURCE_DISCOVERY_CONNECTOR_DESIGN
- `FUTURE_ROUND_B` = SOURCE_CANDIDATE_RANKING_SCHEMA
- `FUTURE_ROUND_C` = OWNER_RATIFICATION_UI_OR_TEMPLATE
- `FUTURE_ROUND_D` = SOURCE_BIRTH_AFTER_OWNER_RATIFICATION
- `FUTURE_ROUND_E` = HUKM_CANDIDATE_GATE_AFTER_SOURCE_COVERAGE

---
*هذه الخطة لا تُنفَّذ الآن؛ كل ولادة مصدر مستقبلية تتطلب تصديق المالك صراحةً، وبوابة الحكم لا تُفتح إلا بقانون docs/43.*
