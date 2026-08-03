# التكليف التنفيذي الشامل إلى Qiyas / Claude

أنت Qiyas، والمطلوب منك تنفيذ ملكية دستورية وتنفيذية كاملة في مشروع Hokom–Taaqol، لا إجراء تعديل موضعي. نفّذ المهمة الحالية من البداية إلى النهاية: تدقيق قرائي، مطابقة مع الواقع البرمجي، تنفيذ الفجوات فقط، اختبارات، ثم تقرير نهائي. لا تسأل عن تفاصيل يمكن حسمها من المستودع والدستور، ولا تتوقف عند الخطة إذا كان التنفيذ ممكنًا.

الهدف:
إدماج «التعديل الدستوري الأول: منشأ الادعاء، بناء المفهوم، ترخيص الحكم، الأثر، المطابقة، والمراجعة» في المعمار الحالي دون إنشاء سجل طبقات موازٍ، ودون كسر SCG أو P0–P12 أو مخرجات Verifier أو سلم الأدلة أو ملكية Hokom الصرفية.

حقائق محصنة:
1. السجل الكنسي الحالي 19 طبقة موزعة على P0–P12؛ لا تعيد ترقيمه ولا تنشئ سجلًا موازيًا.
2. P12 نهائي من نوع IfadahCandidate ولا يفتح P13 ولا ينتج معنى أو حكمًا نهائيًا.
3. نطاق Hokom الحالي متوقف عند P5 ما لم يثبت المستودع أو تعليمات لاحقة خلاف ذلك؛ لا تفتح P6–P12 بحجة هذا التعديل.
4. سلسلة الحكم: الوضع → السبب → الشرط → المانع → العلة → القادح → الصحة → الفساد → البطلان → الأثر → البقايا.
5. Verifier يخرج Licensed / Blocked / Deferred / Residual.
6. افصل intrinsic_verdict عن operational_status وعن evidence_rank.
7. Rank(conclusion) ≤ min Rank(required premises).
8. المانع النشط يمنع Licensed، والدليل اللازم المفقود ينتج Deferred لا Batil.
9. الجذر والوزن والمصدر والمشتقات ملك Hokom؛ HR2S مصدر مرشح أو دليل فقط.
10. لا فعل أو معنى نهائي من Concept أو IfadahCandidate أو CandidateRule مباشرة.
11. لا زرع لأمثلة مخصوصة، ولا تعديل صامت، ولا ادعاء تنفيذ بمجرد وجود اسم أو وثيقة.

ترتيب مصادر الحقيقة عند التعارض:
الدستور والمواد المحصنة → سجل SCG → العقود والمخططات الكنسية → الاختبارات المعتمدة → التنفيذ الجاري → الوثائق التفسيرية.

المرحلة A — تدقيق قرائي إلزامي قبل أي كتابة:
- ثبت حالة المستودع والفرع وHEAD والملفات المعدلة.
- اكتشف المسارات الفعلية ولا تفترضها.
- اقرأ الدستور وسجل SCG والعقود والschemas والenums ومسارات Verifier وP12 والtrace/residuals.
- ابحث عن العقود أو المعاني القائمة: ClaimProvenance, ConceptContract, IfadahCandidate, RealityDomain, DomainBridge, Assessment, TransitionTrace, RepairDirective, CorrespondenceAssessment, AuthorityCheck، وسلسلة الوضع/السبب/الشرط/المانع/العلة/القادح/الصحة/الفساد/البطلان.
- ارسم تدفق البيانات الفعلي وحدد المالك لكل وظيفة.
- تحقق من ملكية الجذر والوزن والمصدر والمشتقات ومن حدود HR2S.
- شغّل الاختبارات قبل التعديل وسجل baseline وNode IDs إن أمكن.
- صنف كل مطلب: IMPLEMENTED / PARTIAL / MISSING / CONFLICT / DOCUMENTED_ONLY / OUT_OF_CURRENT_SCOPE.

المرحلة B — نفذ الفجوات دون ازدواج:
1. أضف التعديل الدستوري الأول واربطه بالدستور وفهرس الوثائق الحاكمة.
2. أعد استعمال الموجود الصحيح، ووسع الأنواع بدل إنشاء نسخ مكررة.
3. نفذ أو وحّد الحد الأدنى الدلالي للعقود التالية:
   - ClaimProvenance
   - ConceptContract
   - IfadahCandidate
   - RealityDomain
   - DomainBridge
   - Assessment بفصل intrinsic_verdict / operational_status / evidence_rank
   - TransitionTrace
   - RepairDirective
   - ApplicationAssessment
   - AuthorityCheck
   - CorrespondenceAssessment
4. إذا كان application/action/correspondence خارج نطاق P5، أضف العقود والحدود والاختبارات السلبية فقط، ولا تفعّل مسارًا يفتح طبقات لاحقة.
5. أضف invariants/validators لحفظ الهوية والمجال والدليل والرتبة والبقايا والأثر ومنع القفز.
6. لا تستخدم قيمًا مزروعة عند نقص البيانات؛ استخدم Unknown/Deferred/NotApplicable وفق نمط المشروع.
7. حافظ على التوافق العكسي للواجهات وJSON، واستخدم versioning أو adapters عند الحاجة.
8. لا تنقل المنطق الصرفي إلى HR2S ولا تسمح له بإصدار Licensed.
9. لا تنشئ P13 أو سجلًا من 11 مرحلة باسم SLGE.

المرحلة C — الاختبارات الإلزامية:
- حفظ ClaimProvenance وسلسلة التحويل.
- اكتمال ConceptContract وإظهار البقايا عند النقص.
- منع انتقال IfadahCandidate إلى final meaning/action.
- بقاء P12 terminal IfadahCandidate.
- حفظ قانون الرتبة وعدم رفعها بتكرار الدليل نفسه.
- active blocker يمنع Licensed.
- missing required evidence ينتج Deferred لا Batil.
- الفصل بين intrinsic verdict وoperational status في البيانات والserialization.
- انتشار residuals وعدم إسقاطها.
- اكتمال TransitionTrace.
- منع العبور بين المجالات بلا DomainBridge.
- RepairDirective يرجع إلى مالك سبب الفشل.
- HR2S output مرشح/دليل فقط.
- ملكية Hokom للجذر والوزن والمصدر والمشتقات.
- التوافق العكسي وعدم تراجع اختبارات P4/P5.
- أضف property/invariant tests حيث يناسب.

بوابة القبول:
لا تعتبر المهمة مكتملة إذا فشل baseline بلا تبرير، أو حُذف اختبار بلا سبب، أو نشأ نوع/سجل/مسار مكرر، أو فُتح P6–P12/P13، أو اختلطت الرتبة بالحالة، أو اختفت البقايا، أو تغيرت ملكية الصرف.

ضوابط Git:
لا تنشئ commit أو tag أو release أو PR ولا تدمج إلى main إلا إذا كانت تعليمات المستخدم الحالية تأمر بذلك صراحة. اترك التغييرات قابلة للمراجعة وقدم diff واضحًا.

التقرير النهائي الإلزامي:
VERDICT؛ Repository State؛ Baseline؛ Audit Findings؛ Ownership Map؛ Implemented Changes؛ No-Duplication Proof؛ Compatibility؛ Tests؛ Constitutional Invariants؛ Deferred Items؛ Diff Summary؛ Final Recommendation.

ابدأ الآن بالتدقيق القرائي، ثم نفذ كامل النطاق الممكن، ثم اختبر وقدم التقرير. لا تكتفِ بخطة أو ملخص.
