# دستور نموذج تحقيق المناط (الجولة 25 — أسئلة فقط)

**ALLOW_MANAT_APPLICATION = YES · ALLOW_FINAL_MANAT = NO · ALLOW_TANZIL = NO · ALLOW_FINAL_HUKM = NO · ALLOW_FINAL_ANSWER = NO · KEEP_COMPOSITE · THIS_NAZILA_ONLY**

تحوّل هذه الطبقة البقايا الواقعية العشر (الجولة 24) إلى أسئلة تحقيق مناط منظّمة. **الوكيل لا يجيب عن الأسئلة**، ولا يحقّق المناط نهائيًّا، ولا ينزّل الحكم.

## قاعدة القرار
- verdict مسموح ∈ { ACCEPT_AS_MANAT_APPLICATION_QUESTION_ONLY، DEFER_...، BLOCK_... }.
- verdict ∈ { FINAL_MANAT، FINAL_HUKM، TANZIL، FINAL_ANSWER } **ممنوع**.
- answer_provided = NO لكل سؤال (الإجابة فعلُ المالك/الجهة المختصة، لا الوكيل).

## الحراس
MANAT_APPLICATION_QUESTION ≠ FINAL_MANAT · ANSWER_SLOT ≠ TANZIL · FACT_ANSWER ≠ HUKM · MANAT_CANDIDATE ≠ FINAL_MANAT · FINAL_MANAT ≠ FINAL_HUKM · SOURCE ≠ FACT_ANSWER · POSSESSION ≠ FINAL_OWNERSHIP · KEEP_COMPOSITE remains active · AUTHORITY_LEAK_PREVENTED = YES.

## أنواع الأسئلة المسموحة
- `FACT_EXISTENCE`
- `PARTY_IDENTITY`
- `PROPERTY_STATUS`
- `PRIOR_PERMISSION`
- `POSSESSION_STATUS`
- `CLAIM_CONTENT`
- `DEFENSE_CONTENT`
- `EVIDENCE_OR_BAYYINA`
- `QARINA_ASSESSMENT`
- `RESIDUAL_COMPLETENESS`

## الأسئلة المولّدة (answer_provided = NO)
- `Q01_NO_CHILD` [FACT_EXISTENCE] ← MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS · هل ثبت أن الميت لا ولد له؟
- `Q02_OTHER_HEIRS` [FACT_EXISTENCE] ← MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS · هل يوجد ورثة آخرون؟
- `Q03_HEIR_CAPACITY` [PARTY_IDENTITY] ← MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN · ما صفة الوارث الذي يريد الطرد؟
- `Q04_HOUSE_STATUS` [PROPERTY_STATUS] ← MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS، MC3_STANDING_HAND_STATE_BEFORE_EXPULSION · هل البيت كله تركة، أم فيه حق/انتفاع/إذن سابق؟
- `Q05_PRIOR_PERMISSION` [PRIOR_PERMISSION] ← MC3_STANDING_HAND_STATE_BEFORE_EXPULSION · هل كان سكن الأخت بإذن المالك قبل موته؟
- `Q06_HAND_CREDIBLE` [POSSESSION_STATUS] ← MC3_STANDING_HAND_STATE_BEFORE_EXPULSION · هل يد الأخت معتبرة، أم تكذبها قرائن ظاهرة؟
- `Q07_CLAIM_CONTENT` [CLAIM_CONTENT] ← MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN · ما الدعوى المحددة للوارث؟
- `Q08_DEFENSE_CONTENT` [DEFENSE_CONTENT] ← MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN · ما جواب الأخت؟
- `Q09_EVIDENCE` [EVIDENCE_OR_BAYYINA] ← MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN · ما البينة المتاحة لكل طرف؟
- `Q10_QARINA_STRENGTH` [QARINA_ASSESSMENT] ← MC3_STANDING_HAND_STATE_BEFORE_EXPULSION · هل توجد قرائن أقوى من مجرد اليد؟
- `Q11_COMPLETENESS` [RESIDUAL_COMPLETENESS] ← MC4_COMPOSITE_MANAT_LINK_NO_OUTCOME · هل اكتملت صورة الواقعة عبر الأجزاء الأربعة (ميراث/تركة/دعوى/سُكنى) دون تعارض؟

## ما لا يُنتج
- إجابات واقعية · مناط نهائي · تنزيل · حكم نهائي · جواب · مقدار نصيب · ملكية · حق سكنى نهائي · إلزام قضائي.

---
*تحقيق المناط النهائي يحتاج أجوبة المالك/الجهة المختصة + تصديقه (الجولة 26 وما بعدها).*
