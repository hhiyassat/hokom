# طلب تصديق مالك على مرشحات الوقائع (الجولة 36)

النازلة: «مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا.»

المرشحات الخمسة من منطوق النص (الجولة 35) **معروضة للتصديق، لا مقبولة تلقائيًّا**. لكل مرشح أدخِل `OWNER_RATIFY = YES | NO | DEFER` (الافتراض DEFER):

- `FC1_KING_DIED` — مات مالك (شخص).
  - OWNER_RATIFY = ____   (FACT_ACCEPTED=YES فقط إذا YES)
- `FC2_HAS_SISTER` — للميت أخت.
  - OWNER_RATIFY = ____   (FACT_ACCEPTED=YES فقط إذا YES)
- `FC3_SISTER_RESIDING_WITH_HIM` — الأخت ساكنة معه.
  - OWNER_RATIFY = ____   (FACT_ACCEPTED=YES فقط إذا YES)
- `FC4_HEIR_WANTED_EXPULSION` — وارثه أراد طردها.
  - OWNER_RATIFY = ____   (FACT_ACCEPTED=YES فقط إذا YES)
- `FC5_LITIGATION_OCCURRED` — وقع تحاكم بينهما.
  - OWNER_RATIFY = ____   (FACT_ACCEPTED=YES فقط إذا YES)

**تنبيه:** لا واقعة تُقبل إلا بتصديقك الصريح؛ العرض ليس قبولًا، والوكيل لا يشتق واقعة من علمه.

*حتى تُصدّق الخمسة وتُزوّد التسع الناقصة: FACTUAL_FACTS_COMPLETE=NO · PHASE0_GATE_PASS=NO · لا مناط/تنزيل/حكم/جواب.*
