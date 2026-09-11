# طلب تصديق مالك — تطبيق مرشّح المناط (تمهيد الجولة 25)

استُخرجت مرشّحات المناط التالية من مرشّحات الحكم (candidate فقط، لا مناط نهائي):

- `MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS` ← HC1_SISTER_SHARE · النطاق: مرشح مناط لجهة الميراث/التركة فقط؛ لا يحسم مقدار النصيب ولا الاستحقاق النهائي.
- `MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN` ← HC2_CLAIM_BURDEN_OF_PROOF · النطاق: مرشح مناط لجهة القضاء/الإثبات فقط؛ ينظّم الإجراء لا موضوع الحق، ولا يُلزم قضائيًّا.
- `MC3_STANDING_HAND_STATE_BEFORE_EXPULSION` ← HC3_POSSESSION_STAYS_PENDING_EXAMINATION · النطاق: مرشح مناط لجهة الحيازة/اليد وبقاء الحال؛ الحيازة ليست ملكية نهائية.
- `MC4_COMPOSITE_MANAT_LINK_NO_OUTCOME` ← HC4_COMPOSITE_LINK_NO_OUTCOME · النطاق: مرشح مناط مركّب فقط؛ لا يختزل المجال ولا يحسم النازلة ولا يرتّب أولوية نهائية.

**تنبيه دور:** المصدر ≠ مناط/حكم، والحيازة ≠ ملكية نهائية، والمركّب باقٍ، والوكيل لا يصادق/يختر مصدرًا ولا يُنتج مناطًا نهائيًا.

المطلوب الآن أن يحدّد المالك صراحةً (الافتراض: لا شيء يُفتح):

1. هل يُصرّح بتنقيح/تحقيق المناط (فحص الشروط والموانع الواقعية)؟
   `ALLOW_MANAT_APPLICATION = YES | NO`
2. هل يُصرّح بالتنزيل على الواقعة؟  `ALLOW_TANZIL = YES | NO`
3. هل يُصرّح بالحكم النهائي/الجواب؟  `ALLOW_FINAL_HUKM = YES | NO` · `ALLOW_FINAL_ANSWER = YES | NO`
4. النطاق:  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`

*حتى تصريح صريح: FINAL_MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_HUKM_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*
