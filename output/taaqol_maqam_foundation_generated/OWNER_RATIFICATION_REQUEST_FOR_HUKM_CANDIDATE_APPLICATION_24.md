# طلب تصديق مالك — تطبيق مرشّح الحكم (تمهيد الجولة 24)

فُتحت بوابة مرشّح الحكم وأُنتجت المرشّحات التالية (candidate فقط، لا حكم نهائي):

- `HC1_SISTER_SHARE` → ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY · النطاق: مرشح فقط لجهة الميراث/التركة، لا يُنتج نصيبًا نهائيًا ولا يحسم التركة.
- `HC2_CLAIM_BURDEN_OF_PROOF` → ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY · النطاق: مرشح فقط لجهة القضاء/الإثبات، ينظّم الإجراء لا موضوع الحق، ولا يُنتج إلزامًا قضائيًا.
- `HC3_POSSESSION_STAYS_PENDING_EXAMINATION` → ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY · النطاق: مرشح فقط لجهة الحيازة/اليد وبقاء الحال عند النزاع؛ الحيازة ليست ملكية نهائية.
- `HC4_COMPOSITE_LINK_NO_OUTCOME` → ACCEPT_AS_NORMATIVE_HUKM_CANDIDATE_ONLY · النطاق: مرشح مركّب فقط، لا يختزل المجال ولا يحسم النازلة ولا يرتّب أولوية نهائية بين الأجزاء.

**تنبيه دور:** المصدر ≠ الحكم، والحيازة ≠ الملكية النهائية، والمركّب باقٍ، والوكيل لا يصادق/يختر مصدرًا ولا يُنتج حكمًا نهائيًا.

المطلوب الآن أن يحدّد المالك صراحةً (الافتراض: لا شيء يُفتح):

1. هل يُصرّح بالانتقال إلى تطبيق مرشّح الحكم/فحص المناط؟
   `ALLOW_MANAT = YES | NO`
2. هل يُصرّح بالتنزيل على الواقعة؟  `ALLOW_TANZIL = YES | NO`
3. هل يُصرّح بالحكم النهائي/الجواب؟  `ALLOW_FINAL_HUKM = YES | NO` · `ALLOW_FINAL_ANSWER = YES | NO`
4. النطاق:  `SCOPE = THIS_NAZILA_ONLY | GENERAL_RULE`

*حتى تصريح صريح: FINAL_HUKM_PRODUCED = NO · MANAT_PRODUCED = NO · TANZIL_PRODUCED = NO · FINAL_ANSWER_PRODUCED = NO.*
