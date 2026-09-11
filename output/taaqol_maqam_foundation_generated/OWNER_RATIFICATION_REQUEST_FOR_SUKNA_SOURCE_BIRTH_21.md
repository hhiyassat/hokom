# طلب تصديق مالك — ولادة مصدر السُّكنى/الحيازة (تمهيد الجولة 21)

تدقيق الجولة 20 لمصدر `SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE`:
- الحالة: **NO_OWNER_SUPPLIED_SOURCE** · الحقول الناقصة: AUTHORITY، TEXT، SCOPE، EVIDENCE، LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM، OWNER_RATIFICATION · SUKNA_SOURCE_FIELDS_COMPLETE = NO

المطلوب من المالك أحد أمرين:

1. **ملء الحقول الستة** لمصدر السُّكنى/الحيازة:
   - AUTHORITY = ...
   - TEXT = ...
   - SCOPE = ...   # يقيّد نفسه: لا ينتج الحكم وحده
   - EVIDENCE = ...   # سلسلة استشهاد نصية، بلا رابط
   - LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM = YES/NO
   - OWNER_RATIFICATION = YES/NO
2. **أو تأكيد الاكتمال** إن سبق الملء: `SUKNA_SOURCE_FIELDS_COMPLETE = YES`.

ثم تصريح صريح:

- `ALLOW_SUKNA_SOURCE_BIRTH = YES | NO`
- `ALLOW_NORMATIVE_HUKM_CANDIDATE = YES | NO`  (يحتاج قانون بوابة الحكم docs/43)
- `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`

**تنبيه دور:** الوكيل لا يصادق/يختر مصدرًا، والمركّب باقٍ (KEEP_COMPOSITE).

*حتى تصريح صريح مع الحقول الستة: SUKNA_SOURCE_BORN = NO · NORMATIVE_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*
