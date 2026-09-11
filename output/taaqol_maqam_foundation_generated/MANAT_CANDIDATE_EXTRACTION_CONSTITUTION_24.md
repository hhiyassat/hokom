# دستور استخراج مرشّح المناط (الجولة 24 — مرشّح فقط)

**ALLOW_MANAT_CANDIDATE = YES · ALLOW_TANZIL = NO · ALLOW_FINAL_HUKM = NO · ALLOW_FINAL_ANSWER = NO · KEEP_COMPOSITE · THIS_NAZILA_ONLY**

تفتح هذه الطبقة بوابة *مرشّح* المناط فقط، لا المناط النهائي. الاستخراج من مرشّحات الحكم الأربعة (الجولة 23)، موضعَ التأثير في كل منها.

## قاعدة القرار
- verdict مسموح ∈ { ACCEPT_AS_MANAT_CANDIDATE_ONLY، DEFER_MANAT_CANDIDATE، BLOCK_MANAT_CANDIDATE }.
- verdict ∈ { FINAL_MANAT، FINAL_HUKM، TANZIL، FINAL_ANSWER } **ممنوع**.
- candidate_manat_statement بصيغة مرشّح («مرشح مناط أولي...») لا مناطًا نهائيًا ولا جوابًا.

## الحراس
HUKM_CANDIDATE ≠ FINAL_HUKM/FINAL_MANAT · MANAT_CANDIDATE ≠ FINAL_MANAT/TANZIL/FINAL_ANSWER · SOURCE ≠ MANAT/HUKM · POSSESSION ≠ FINAL_OWNERSHIP · KEEP_COMPOSITE remains active · AUTHORITY_LEAK_PREVENTED = YES.

## مرشّحات المناط المستخرجة (candidate فقط)
- `MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS` ← HC1_SISTER_SHARE · ACCEPT_AS_MANAT_CANDIDATE_ONLY · مرشح مناط أولي: موضع التأثير هو وجود أخت للميت وشروط استحقاقها في التركة؛ شروط الكلالة وسائر الورثة تبقى شرطًا/بقية لا حكمًا. لا يحدد استحقاقًا نهائيًا.
- `MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN` ← HC2_CLAIM_BURDEN_OF_PROOF · ACCEPT_AS_MANAT_CANDIDATE_ONLY · مرشح مناط أولي: موضع التأثير هو وجود دعوى من الوارث على عين/حق ووجود منازعة وعبء الإثبات؛ تنظيم الإثبات يبقى غير حاسم للحق. لا يفصل في موضوع الحق.
- `MC3_STANDING_HAND_STATE_BEFORE_EXPULSION` ← HC3_POSSESSION_STAYS_PENDING_EXAMINATION · ACCEPT_AS_MANAT_CANDIDATE_ONLY · مرشح مناط أولي: موضع التأثير هو كون الأخت ساكنة/ذات يد أو حال قائم قبل الطرد مع فحص القرائن؛ تبقى القاعدة: الحيازة ليست ملكية نهائية. لا يثبت حق سكنى نهائيًا.
- `MC4_COMPOSITE_MANAT_LINK_NO_OUTCOME` ← HC4_COMPOSITE_LINK_NO_OUTCOME · ACCEPT_AS_MANAT_CANDIDATE_ONLY · مرشح مناط مركّب أولي يربط مواضع التأثير: الميراث + التركة + الدعوى + السكنى/الحيازة، دون حسم النتيجة ودون ترتيب أولوية نهائية. يحفظ تعدد المجال المركّب.

## البقايا الواقعية العشر (residuals لا أحكام)
- هل ثبت أن الميت لا ولد له؟
- هل يوجد ورثة آخرون؟
- ما صفة الوارث الذي يريد الطرد؟
- هل البيت كله تركة أم فيه حق/انتفاع/إذن سابق؟
- هل سكن الأخت كان بإذن المالك قبل موته؟
- هل يد الأخت يد معتبرة أو تكذبها قرائن؟
- ما الدعوى المحددة للوارث؟
- ما جواب الأخت؟
- ما البينة؟
- هل توجد قرائن أقوى من مجرد اليد؟

## ما لا يُنتج
- مناط نهائي · تنزيل · حكم نهائي · جواب · مقدار نصيب · ملكية · حق سكنى نهائي · إلزام قضائي.

---
*المناط النهائي والتنزيل والحكم والجواب يحتاج فحص الشروط والموانع + تصديق المالك (الجولة 25 وما بعدها).*
