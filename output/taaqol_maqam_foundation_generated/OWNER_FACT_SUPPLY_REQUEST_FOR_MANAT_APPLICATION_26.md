# طلب تزويد وقائع من المالك — تحقيق المناط (تمهيد الجولة 26)

حُوِّلت البقايا الواقعية إلى الأسئلة التالية (answer_provided = NO؛ الوكيل لا يجيب):

- `Q01_NO_CHILD` [FACT_EXISTENCE]: هل ثبت أن الميت لا ولد له؟
  - نوع الجواب المتوقع: YES/NO/UNKNOWN · البينة المطلوبة: وثيقة وراثة/إقرار/بينة
- `Q02_OTHER_HEIRS` [FACT_EXISTENCE]: هل يوجد ورثة آخرون؟
  - نوع الجواب المتوقع: LIST/NONE/UNKNOWN · البينة المطلوبة: حصر إرث/بينة
- `Q03_HEIR_CAPACITY` [PARTY_IDENTITY]: ما صفة الوارث الذي يريد الطرد؟
  - نوع الجواب المتوقع: IDENTITY/UNKNOWN · البينة المطلوبة: بيان صفة/قرابة
- `Q04_HOUSE_STATUS` [PROPERTY_STATUS]: هل البيت كله تركة، أم فيه حق/انتفاع/إذن سابق؟
  - نوع الجواب المتوقع: ESTATE/RIGHT/PERMISSION/MIXED/UNKNOWN · البينة المطلوبة: سند ملكية/وقف/إذن
- `Q05_PRIOR_PERMISSION` [PRIOR_PERMISSION]: هل كان سكن الأخت بإذن المالك قبل موته؟
  - نوع الجواب المتوقع: YES/NO/UNKNOWN · البينة المطلوبة: إقرار/بينة/قرينة
- `Q06_HAND_CREDIBLE` [POSSESSION_STATUS]: هل يد الأخت معتبرة، أم تكذبها قرائن ظاهرة؟
  - نوع الجواب المتوقع: CREDIBLE/REBUTTED/UNKNOWN · البينة المطلوبة: قرائن/بينة
- `Q07_CLAIM_CONTENT` [CLAIM_CONTENT]: ما الدعوى المحددة للوارث؟
  - نوع الجواب المتوقع: CLAIM_TEXT/UNKNOWN · البينة المطلوبة: صحيفة دعوى/إقرار
- `Q08_DEFENSE_CONTENT` [DEFENSE_CONTENT]: ما جواب الأخت؟
  - نوع الجواب المتوقع: DEFENSE_TEXT/UNKNOWN · البينة المطلوبة: جواب/إقرار/إنكار
- `Q09_EVIDENCE` [EVIDENCE_OR_BAYYINA]: ما البينة المتاحة لكل طرف؟
  - نوع الجواب المتوقع: EVIDENCE_LIST/NONE/UNKNOWN · البينة المطلوبة: بينة/شهود/وثائق
- `Q10_QARINA_STRENGTH` [QARINA_ASSESSMENT]: هل توجد قرائن أقوى من مجرد اليد؟
  - نوع الجواب المتوقع: YES/NO/UNKNOWN · البينة المطلوبة: قرائن مقارنة
- `Q11_COMPLETENESS` [RESIDUAL_COMPLETENESS]: هل اكتملت صورة الواقعة عبر الأجزاء الأربعة (ميراث/تركة/دعوى/سُكنى) دون تعارض؟
  - نوع الجواب المتوقع: COMPLETE/INCOMPLETE/UNKNOWN · البينة المطلوبة: مراجعة اكتمال الأجوبة أعلاه

**تنبيه دور:** الوكيل لا يجيب عن الوقائع، ولا يحقّق المناط، ولا يصادق مصدرًا، والحيازة ليست ملكية نهائية، والمركّب باقٍ.

المطلوب من المالك/الجهة المختصة: تزويد أجوبة الوقائع والبينة لكل سؤال، ثم صراحةً:

- `MANAT_FACTS_SUPPLIED = YES | NO`
- `ALLOW_FINAL_MANAT = YES | NO`  (تحقيق المناط النهائي بعد استيفاء الأجوبة)
- `ALLOW_TANZIL = YES | NO`
- `ALLOW_FINAL_HUKM = YES | NO` · `ALLOW_FINAL_ANSWER = YES | NO`
- `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`

*حتى تصل الأجوبة والتصريح: FINAL_MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_HUKM_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*
