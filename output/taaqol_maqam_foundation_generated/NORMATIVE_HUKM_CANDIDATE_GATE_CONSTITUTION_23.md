# دستور بوابة مرشّح الحكم المعياري (الجولة 23 — مرشّح فقط)

**ALLOW_NORMATIVE_HUKM_CANDIDATE = YES · ALLOW_FINAL_HUKM = NO · ALLOW_MANAT = NO · ALLOW_TANZIL = NO · ALLOW_FINAL_ANSWER = NO · KEEP_COMPOSITE · THIS_NAZILA_ONLY**

هذه الطبقة تفتح بوابة *مرشّح* الحكم فقط، لا الحكم النهائي. الانتقال بنيوي لا موضوعي.

## الشروط البنيوية لفتح المرشّح (لا الموضوعية)
- ALL_ROUND13_DOMAINS_COVERED = YES
- ALL_SOURCES_OWNER_RATIFIED = YES
- EACH_SOURCE_HAS_MAPPING_OR_SCOPE = YES
- MAPPING_SHAPE_COMPLETE = YES
- NO_RESIDUAL_BLOCKS_OPENING_CANDIDATE = YES
- RESIDUALS_BLOCK_FINAL_HUKM = YES

## قاعدة القرار
- verdict مسموح ∈ { ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY، DEFER_HUKM_CANDIDATE، BLOCK_HUKM_CANDIDATE }.
- verdict = FINAL_HUKM **ممنوع**.
- candidate_statement بصيغة مرشّح («مرشح حكم أولي يحتاج فحص الشروط والموانع...») لا فتوى ولا جواب.

## الحراس
SOURCE ≠ HUKM · SOURCE_MAPPING ≠ HUKM · DOMAIN_CANDIDATE ≠ FINAL_DOMAIN · HUKM_CANDIDATE ≠ FINAL_HUKM/MANAT/TANZIL/FINAL_ANSWER · KEEP_COMPOSITE remains active · AUTHORITY_LEAK_PREVENTED = YES.

## المرشّحات المولّدة (candidate فقط)
- `HC1_SISTER_SHARE` → ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY · مرشح حكم أولي يحتاج فحص الشروط والموانع في نصيب الأخت من التركة (شروط الكلالة، عدم وجود ولد وسائر الورثة، ترتيب الفروض والباقي)؛ لا يحدد مقدارًا نهائيًا.
- `HC2_CLAIM_BURDEN_OF_PROOF` → ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY · مرشح حكم أولي يحتاج فحص الشروط والموانع في دعوى الوارث وعبء الإثبات (اليمين على المدعى عليه، وقوة جنبة أقوى المتداعيين)؛ لا يحسم نتيجة النزاع.
- `HC3_POSSESSION_STAYS_PENDING_EXAMINATION` → ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY · مرشح حكم أولي يحتاج فحص الشروط والموانع في بقاء الساكن/ذي اليد حتى تُفحص الدعوى والقرائن، وأن مجرد دعوى الوارث لا تكفي وحدها لإخراجه؛ لا يثبت حق سكنى نهائيًا ولا ملكية.
- `HC4_COMPOSITE_LINK_NO_OUTCOME` → ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY · مرشح حكم مركّب أولي يربط أجزاء المسألة الثلاثة (نصيب الأخت، عبء الإثبات، بقاء ذي اليد حتى الفحص) دون أن يحسم النتيجة؛ يحفظ تعدد المجال المركّب.

## ما لا يُنتج
- مقدار نصيب نهائي · ملكية نهائية · حق سكنى نهائي · إلزام قضائي · جواب على النازلة.

---
*الحكم النهائي والمناط والتنزيل والجواب يحتاج تصديق المالك ورخصة لاحقة (الجولة 24 وما بعدها).*
