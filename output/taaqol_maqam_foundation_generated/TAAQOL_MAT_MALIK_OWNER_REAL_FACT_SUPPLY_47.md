# تزويد وتصديق المالك للوقائع التسع الواقعية (TAAQOL_MAT_MALIK_OWNER_REAL_FACT_SUPPLY_47)

**المالك يزوّد ويصدّق الوقائع التسع كوقائع للحالة الواقعية — لا حكم، لا تنزيل، لا جواب.**

> النازلة: مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا.
> SOURCE = OWNER_SUPPLIED_REAL_CASE_FACTS_ROUND_47 (ليست من النص ولا من سيناريو الجولة 44)

## الوقائع التسع المصدّقة
- MF1_NO_CHILD — هل ثبت أن الميت لا ولد له؟ → ACCEPT_REAL_CASE_FACT (owner_value=«لا ولد للميت.», ratification=YES)
- MF2_NO_OTHER_HEIRS — هل ثبت عدم وجود ورثة آخرين مؤثرين في المسألة؟ → ACCEPT_REAL_CASE_FACT (owner_value=«لا ورثة آخرون مؤثرون في هذه المسألة غير المذكورين في الواقعة.», ratification=YES)
- MF3_HEIR_IDENTITY_AND_STATUS — هل ثبتت هوية الوارث الطالب للطرد وصفته الإرثية؟ → ACCEPT_REAL_CASE_FACT (owner_value=«طالب الطرد وارث ذو صفة إرثية في الواقعة.», ratification=YES)
- MF4_HOUSE_OWNERSHIP — هل ثبت أن البيت ملك للميت؟ → ACCEPT_REAL_CASE_FACT (owner_value=«البيت ملك للميت.», ratification=YES)
- MF5_HOUSE_IS_ESTATE — هل ثبت أن البيت داخل في التركة؟ → ACCEPT_REAL_CASE_FACT (owner_value=«البيت داخل في التركة.», ratification=YES)
- MF6_PRIOR_RESIDENCE_PERMISSION — هل ثبت أن سكن الأخت كان بإذن سابق معتبر؟ → ACCEPT_REAL_CASE_FACT (owner_value=«سكن الأخت كان بإذن سابق معتبر.», ratification=YES)
- MF7_SISTER_YAD_STATUS — هل ثبتت يد الأخت على السكن ظاهراً؟ → ACCEPT_REAL_CASE_FACT (owner_value=«يد الأخت على السكن قائمة ظاهراً إلى حين نظر القضاء.», ratification=YES)
- MF8_EVIDENCE_OR_BAYYINA — هل ثبت وجود أو عدم وجود بينة فورية كافية لطالب الطرد؟ → ACCEPT_REAL_CASE_FACT (owner_value=«لا توجد بينة فورية كافية لطالب الطرد توجب إخراجها قبل نظر القضاء.», ratification=YES)
- MF9_LITIGATION_OUTCOME — هل ثبت محل التحاكم أو نتيجته الإجرائية أو القضائية؟ → ACCEPT_REAL_CASE_FACT (owner_value=«محل التحاكم هو طلب طرد الأخت من السكن.», ratification=YES)

## إعادة فحص بوابة المناط الواقعي الكامل
- NINE_FACTS_ACCEPTED_COUNT = 9
- NINE_FACTS_DEFER_COUNT = 0
- NINE_FACTS_BLOCK_COUNT = 0
- REAL_WORLD_FULL_MANAT_GATE_PASS = YES
- REAL_WORLD_FULL_MANAT_READY = YES
- STOP_BEFORE_TANZIL = NO

> FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO (إذن هذه الجولة محصور في إثبات الوقائع وفتح الجاهزية فقط).

---
*الوقائع التسع مقبولة كوقائع واقعية بتصديق المالك؛ جاهزية المناط الواقعي الكامل مفتوحة، والتنزيل والحكم والجواب تحتاج إذنًا صريحًا منفصلًا.*
