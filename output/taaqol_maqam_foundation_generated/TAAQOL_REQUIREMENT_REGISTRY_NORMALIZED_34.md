# سجل المتطلبات المطبَّع (الجولة 34 — تطبيع فقط)

NORMALIZED_REQUIREMENT_ROW_COUNT = **40** (FACT=10 · SOURCE=10 · OWNER_DECISION=10 · GATE=10)

كل متطلب أصلي (10) قُسِّم إلى أربعة أبعاد مستقلة. **لا وقائع/مصادر/حكم/تنزيل/جواب**؛ الكل DEFER.

## REQ01_NO_CHILD — هل ثبت أن الميت لا ولد له؟
- `NR_REQ01_NO_CHILD_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ01_NO_CHILD_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ01_NO_CHILD_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: تصديق واقعة انتفاء الولد · default=DEFER
- `NR_REQ01_NO_CHILD_GATE` [GATE_REQUIREMENT] → سجل: `inheritance_condition_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ02_OTHER_HEIRS — هل يوجد ورثة آخرون؟
- `NR_REQ02_OTHER_HEIRS_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ02_OTHER_HEIRS_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ02_OTHER_HEIRS_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: اعتماد قائمة الورثة · default=DEFER
- `NR_REQ02_OTHER_HEIRS_GATE` [GATE_REQUIREMENT] → سجل: `inheritance_condition_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ03_HEIR_CAPACITY — ما صفة الوارث الذي يريد الطرد؟
- `NR_REQ03_HEIR_CAPACITY_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ03_HEIR_CAPACITY_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ03_HEIR_CAPACITY_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: تحديد صفة الوارث · default=DEFER
- `NR_REQ03_HEIR_CAPACITY_GATE` [GATE_REQUIREMENT] → سجل: `proof_burden_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ04_HOUSE_STATUS — هل البيت كله تركة أم فيه حق/انتفاع/إذن سابق؟
- `NR_REQ04_HOUSE_STATUS_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ04_HOUSE_STATUS_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ04_HOUSE_STATUS_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: تصديق صفة البيت · default=DEFER
- `NR_REQ04_HOUSE_STATUS_GATE` [GATE_REQUIREMENT] → سجل: `possession_yad_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ05_PRIOR_PERMISSION — هل كان سكن الأخت بإذن المالك قبل موته؟
- `NR_REQ05_PRIOR_PERMISSION_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ05_PRIOR_PERMISSION_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ05_PRIOR_PERMISSION_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: تصديق واقعة الإذن · default=DEFER
- `NR_REQ05_PRIOR_PERMISSION_GATE` [GATE_REQUIREMENT] → سجل: `possession_yad_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ06_HAND_CREDIBLE — هل يد الأخت معتبرة أم تكذبها قرائن؟
- `NR_REQ06_HAND_CREDIBLE_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ06_HAND_CREDIBLE_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ06_HAND_CREDIBLE_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: بوابة تقييم اليد مقابل القرائن · default=DEFER
- `NR_REQ06_HAND_CREDIBLE_GATE` [GATE_REQUIREMENT] → سجل: `possession_yad_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ07_CLAIM_CONTENT — ما الدعوى المحددة للوارث؟
- `NR_REQ07_CLAIM_CONTENT_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ07_CLAIM_CONTENT_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ07_CLAIM_CONTENT_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: اعتماد نص الدعوى · default=DEFER
- `NR_REQ07_CLAIM_CONTENT_GATE` [GATE_REQUIREMENT] → سجل: `proof_burden_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ08_DEFENSE_CONTENT — ما جواب الأخت؟
- `NR_REQ08_DEFENSE_CONTENT_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ08_DEFENSE_CONTENT_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ08_DEFENSE_CONTENT_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: اعتماد نص الجواب · default=DEFER
- `NR_REQ08_DEFENSE_CONTENT_GATE` [GATE_REQUIREMENT] → سجل: `proof_burden_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ09_EVIDENCE — ما البينة؟
- `NR_REQ09_EVIDENCE_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ09_EVIDENCE_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ09_EVIDENCE_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: بوابة عبء الإثبات · default=DEFER
- `NR_REQ09_EVIDENCE_GATE` [GATE_REQUIREMENT] → سجل: `proof_burden_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER
## REQ10_QARINA_STRENGTH — هل توجد قرائن أقوى من مجرد اليد؟
- `NR_REQ10_QARINA_STRENGTH_FACT` [FACT_REQUIREMENT] → سجل: `factual_claim_registry` · قرار المالك: تصديق الواقعة · default=DEFER
- `NR_REQ10_QARINA_STRENGTH_SOURCE` [SOURCE_REQUIREMENT] → سجل: `source_requirement_registry` · قرار المالك: اعتماد المصدر · default=DEFER
- `NR_REQ10_QARINA_STRENGTH_OWNER` [OWNER_DECISION_REQUIREMENT] → سجل: `owner_ratification_registry` · قرار المالك: بوابة موازنة القرائن · default=DEFER
- `NR_REQ10_QARINA_STRENGTH_GATE` [GATE_REQUIREMENT] → سجل: `possession_yad_registry` · قرار المالك: فتح البوابة بقرار مالك · default=DEFER

---
*التطبيع لا يُنشئ واقعة ولا مصدرًا؛ كل صف معلّق حتى إشغال السجل وتصديق المالك.*
