# تطبيق المصدر NS1 على FNM1 — التنزيل فقط (TAAQOL_MAT_MALIK_TANZIL_APPLICATION_51)

**إنتاج التنزيل فقط: انطباق شروط NS1 على عناصر FNM1 — بلا حكم، بلا جواب، بلا نتيجة قضائية، بلا «يجوز/لا يجوز».**

> النازلة: مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا.
> المناط النهائي: FNM1_MAT_MALIK_SISTER_RESIDENCE_ESTATE_EXPULSION_DISPUTE
> المصدر المعياري: NS1_OWNER_RATIFIED_NO_EXPULSION_BEFORE_ADJUDICATION_RULE

## عناصر الربط (NS1 ↔ FNM1)
- BE1_EIN_IN_ESTATE — عين داخلة في التركة → present=YES (يحققها: MF4_HOUSE_OWNERSHIP، MF5_HOUSE_IS_ESTATE)
- BE2_RESIDING_IN_EIN — ساكنة في العين → present=YES (يحققها: FC3_SISTER_RESIDING_WITH_HIM)
- BE3_PRIOR_PERMISSION — السكن بإذن سابق معتبر → present=YES (يحققها: MF6_PRIOR_RESIDENCE_PERMISSION)
- BE4_YAD_STANDING — يد الساكنة قائمة ظاهرًا → present=YES (يحققها: MF7_SISTER_YAD_STATUS)
- BE5_EXPELLER_IS_HEIR — طالب الإخراج وارث ذو صفة → present=YES (يحققها: MF3_HEIR_IDENTITY_AND_STATUS، FC4_HEIR_WANTED_EXPULSION)
- BE6_NO_IMMEDIATE_BAYYINAH — لا توجد بينة فورية كافية لطالب الإخراج → present=YES (يحققها: MF8_EVIDENCE_OR_BAYYINA)
- BE7_DISPUTE_UNDER_ADJUDICATION — النزاع منظور أو محله التحاكم → present=YES (يحققها: FC5_LITIGATION_OCCURRED، MF9_LITIGATION_OUTCOME)
- BE8_REQUEST_EXPULSION_BEFORE_RULING — المطلوب الإخراج من السكن قبل نظر الحكم المختص → present=YES (يحققها: FC4_HEIR_WANTED_EXPULSION، MF9_LITIGATION_OUTCOME)

## نتيجة التنزيل
- NS1_APPLIES_TO_FNM1 = YES
- SOURCE_APPLIED = YES
- TANZIL = YES · TANZIL_STATUS = ACCEPTED
- VERDICT = ACCEPT_TANZIL_ONLY
- FINAL_HUKM = NO · FINAL_ANSWER = NO · JUDICIAL_OUTCOME = NOT_PRODUCED

## السبب/الشرط/المانع
- CAUSE = NORMATIVE_SOURCE_ACCEPTED_AND_BOUND_TO_FNM1
- CONDITIONS = FINAL_MANAT_ACCEPTED، NORMATIVE_SOURCE_ACCEPTED، BINDING_LICENSE_TO_FNM1_PRESENT، ALL_NS1_BINDING_ELEMENTS_PRESENT_IN_FNM1
- PREVENTERS = NONE_FOR_TANZIL_ONLY

## البقايا
- FINAL_HUKM_NOT_OPENED
- FINAL_ANSWER_NOT_OPENED
- JUDICIAL_OUTCOME_NOT_PRODUCED

---
*التنزيل = تحقّق شروط المصدر في المناط؛ لم يُنتَج الحكم ولا الجواب ولا النتيجة القضائية، ولم يُقَل «يجوز» أو «لا يجوز». الحكم والجواب يحتاجان إذنًا صريحًا منفصلًا.*
