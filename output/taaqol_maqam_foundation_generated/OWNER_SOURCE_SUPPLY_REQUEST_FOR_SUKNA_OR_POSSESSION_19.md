# طلب تزويد مالك — مصدر السُّكنى/الحيازة/الطرد (الجولة 19)

**PROVIDE_SUKNA_SOURCE = YES · ALLOW_NORMATIVE_HUKM_CANDIDATE = NO · KEEP_COMPOSITE · THIS_NAZILA_ONLY**

سدًّا لثغرة الجولة 18: `SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE` غير مغطّى بالمصادر الثلاثة المولودة.

يُطلب من المالك تزويد مصدرٍ (أو أكثر) يخدم واحدًا أو أكثر مما يلي:

- حق السكنى (`SUKNA_RIGHT`)
- الحيازة أو اليد (`POSSESSION_OR_YAD`)
- منع الطرد (`PREVENT_EXPULSION`)
- الضرر (`DARAR`)
- حق الانتفاع (`USUFRUCT_RIGHT`)
- علاقة الأخت الساكنة بالبيت بعد موت المالك (`SISTER_RESIDENCE_RELATION_POST_DEATH`)

لكل مصدر يزوّده المالك، الحقول الستة (فارغة للتعبئة):

```text
SUKNA_SOURCE_1:
AUTHORITY = ____
TEXT = ____
SCOPE = ____   # يجب أن يُقيّد نفسه: لا ينتج الحكم وحده
EVIDENCE = ____   # سلسلة استشهاد نصية فقط، بلا رابط حيّ
LINK_LICENSE_TO_DOMAIN_OR_FACTUAL_CLAIM = YES/NO
OWNER_RATIFICATION = YES/NO
```

**ملاحظة على «لا ضرر ولا ضرار»:** لا يُعتمد مصدرًا إلا إذا كان `OWNER_SUPPLIED` وصادق المالك على مرجعيّته صراحةً (سبق التنبيه على تضعيف طريق ابن ماجه في نفس الصفحة)؛ الوكيل لا يعتمده ولا يصادقه من عنده.

*حتى يزوّد المالك الحقول ويصرّح بالولادة لاحقًا: SUKNA_SOURCE_BORN = NO · لا حكم/مناط/تنزيل/جواب.*
