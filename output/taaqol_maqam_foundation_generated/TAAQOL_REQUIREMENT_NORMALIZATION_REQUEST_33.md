# طلب تطبيع سجل المتطلبات وبناء السجلات (تمهيد الجولة 33)

**PHASE 0 حاجز:** السلسلة النهائية (المناط الواقعي → المناط النهائي → التنزيل → الحكم → الجواب) لا تُفتح قبل أن تصير المتطلبات مدعومة بسجلات ومطبَّعة.

النازلة: «مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا.»

## الحالة المكتشَفة
- سجل المتطلبات (32): موجود وصحيح
- السجل المطبَّع (33): **غائب**
- السجلات المبنيّة: **0/13**
- وقائع مزوَّدة من المالك: **لا**
- READY_FOR_EXPANSION = **NO**

## المطلوب من المالك (قبل أي مناط نهائي)
1. بناء/تطبيع السجلات الثلاثة عشر (كلٌّ منها: `creates_fact=NO`، `creates_source=NO`، `owner_ratification=YES`):
   - `factual_claim_registry`
   - `owner_supplied_fact_registry`
   - `source_requirement_registry`
   - `normative_source_registry`
   - `domain_candidate_registry`
   - `hukm_candidate_registry`
   - `manat_candidate_registry`
   - `tanzil_requirement_registry`
   - `proof_burden_registry`
   - `possession_yad_registry`
   - `inheritance_condition_registry`
   - `residual_registry`
   - `owner_ratification_registry`
2. إنتاج `TAAQOL_REQUIREMENT_REGISTRY_NORMALIZED_33.json` (تطبيع المتطلبات العشرة على السجلات).
3. تزويد الوقائع بقرار مالك لكل متطلب (`OWNER_SUPPLIED_FACT` + مرجع/بينة + تصديق).

## التصريح المطلوب لاحقًا (لا يُفتح الآن)
- `ALLOW_REQUIREMENT_NORMALIZATION_33 = YES | NO`
- `BUILD_REGISTRIES = <list>`
- `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`

*حتى تُبنى السجلات ويُنتَج التطبيع 33: FINAL_MANAT = NO · TANZIL = NO · FINAL_HUKM = NO · FINAL_ANSWER = NO · لا مزامنة فرع (مرحلة لاحقة) · لا full project closure من نازلة واحدة.*
