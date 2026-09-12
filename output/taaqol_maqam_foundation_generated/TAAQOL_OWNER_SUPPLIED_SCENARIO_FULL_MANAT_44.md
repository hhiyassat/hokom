# المناط الكامل لسيناريو المالك (OWNER_SUPPLIED_SCENARIO_FULL_MANAT_44)

**مناط كامل لسيناريو مالك فقط — لا للحالة الواقعية المطلقة، ولا حكم ولا تنزيل.**

> النص الأصلي: مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا.
> SCENARIO_ID = SCN1_NO_CHILD_NO_OTHER_HEIRS_ESTATE_PERMISSION_NO_EXPULSION_EVIDENCE · SCENARIO_STATUS = OWNER_SUPPLIED_FOR_MANAT_TESTING · NOT_ORIGINAL_TEXT_FACT = YES

## أ. الوقائع النصية المقبولة (5)
- FC1_KING_DIED = «مات مالك» (from text)
- FC2_HAS_SISTER = «له أخت» (from text)
- FC3_SISTER_RESIDING_WITH_HIM = «الأخت ساكنة معه» (from text)
- FC4_HEIR_WANTED_EXPULSION = «وارثه أراد طردها» (from text)
- FC5_LITIGATION_OCCURRED = «وقع تحاكم بينهما» (from text)

## ب. سيناريو المالك للوقائع التسع (OWNER_SUPPLIED_SCENARIO_FACTS)
- MF1_NO_CHILD = YES → «لا ولد للميت ولا فرع وارث ظاهر في هذا السيناريو» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)
- MF2_NO_OTHER_HEIRS = YES → «لا ورثة آخرون في هذا السيناريو غير الأخت والوارث المذكور» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)
- MF3_HEIR_IDENTITY_AND_STATUS = الوارث المذكور وارث عصبة أو صاحب حق في التركة، دون تعيين تفصيلي → «الوارث المذكور له صفة إرثية في هذا السيناريو» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)
- MF4_HOUSE_OWNERSHIP = YES → «البيت ملك للميت في هذا السيناريو» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)
- MF5_HOUSE_IS_ESTATE = YES → «البيت كله داخل في التركة في هذا السيناريو» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)
- MF6_PRIOR_RESIDENCE_PERMISSION = YES → «سكن الأخت كان بإذن سابق من الميت في هذا السيناريو» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)
- MF7_SISTER_YAD_STATUS = VALID_YAD_PENDING_JUDICIAL_REVIEW → «يد الأخت على السكن يد قائمة معتبرة ظاهراً إلى حين نظر القضاء في هذا السيناريو» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)
- MF8_EVIDENCE_OR_BAYYINA = NO_EVIDENCE_FOR_EXPULSION → «لا بينة لدى طالب الطرد على سبب فوري يوجب إخراجها في هذا السيناريو» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)
- MF9_LITIGATION_OUTCOME = REQUEST_EXPULSION_DISPUTE → «محل التحاكم هو طلب طرد الأخت من السكن في هذا السيناريو» (SCENARIO, NOT_ORIGINAL_TEXT_FACT=YES)

## ج. المناط الكامل للسيناريو
- ID = FSM1_SISTER_RESIDENCE_IN_ESTATE_WITH_PERMISSION_AND_EXPULSION_DISPUTE
- RENDERING_ATTRIBUTION = OWNER_SUPPLIED_SCENARIO_RENDERING (ليست رأي الكود ولا استنتاجه ولا حكمه ولا واقعة نصية)
- صياغة المالك (سجل منظّم) = «وفاة مالك، ووجود أخت له ساكنة معه، مع افتراض عدم الولد وعدم ورثة آخرين في السيناريو، وكون البيت ملكاً للميت وداخلاً في التركة، وسكن الأخت فيه بإذن سابق، وقيام يدها على السكن ظاهراً، وطلب وارث ذي صفة إخراجها بلا بينة فورية كافية، ووقوع تحاكم في طلب الطرد.»
- NOT_CODE_OPINION = YES · NOT_INFERRED_BY_ENGINE = YES · NOT_TEXT_BOUND_FACT = YES · IS_STRUCTURED_RECORD_ONLY = YES
- MANAT_TYPE = OWNER_SUPPLIED_SCENARIO_FULL_FACTUAL_MANAT · STATUS = ACCEPTED_FOR_SCENARIO_ONLY
- FINAL_MANAT = NO · LICENSES_TANZIL = NO
- VERDICT = ACCEPT_FULL_SCENARIO_MANAT_ONLY

## د. تحديث المناطات المشروطة
- CMR1_INHERITANCE_MANAT_REQUIREMENT: STATUS = SATISFIED_FOR_SCENARIO (NOT_SATISFIED_FOR_ACTUAL_TEXT_ONLY)
- CMR2_PROPERTY_ESTATE_MANAT_REQUIREMENT: STATUS = SATISFIED_FOR_SCENARIO (NOT_SATISFIED_FOR_ACTUAL_TEXT_ONLY)
- CMR3_RESIDENCE_YAD_MANAT_REQUIREMENT: STATUS = SATISFIED_FOR_SCENARIO (NOT_SATISFIED_FOR_ACTUAL_TEXT_ONLY)
- CMR4_PROOF_DISPUTE_MANAT_REQUIREMENT: STATUS = SATISFIED_FOR_SCENARIO (NOT_SATISFIED_FOR_ACTUAL_TEXT_ONLY)

## هـ. إعادة الفحص
- TEXT_FACTS_ACCEPTED = 5 · SCENARIO_FACTS_ACCEPTED = 9
- SCENARIO_FACTUAL_FACTS_COMPLETE = YES · PHASE0_SCENARIO_GATE_PASS = YES
- PHASE0_ORIGINAL_TEXT_FULL_GATE_PASS = NO

---
*مناط كامل للسيناريو فقط؛ لا يثبت واقعًا خارج السيناريو، ولا يرخّص التنزيل ولا الحكم النهائي ولا الجواب النهائي؛ بوابة النص الأصلي الكاملة تبقى NO.*
