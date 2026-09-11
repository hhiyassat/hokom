# HOKOM/TAAQOL — Reference Matrix + Hokom-FrameNet Roadmap (round 10)

**MODE = CODE_AND_DOCUMENTATION_ONLY · COMMIT = NO · PROJECT_FINISHED = NO**
No ḥukm, no manāṭ, no tanzīl, no final answer, no normative source, no domain classification. This is a
reference roadmap before any masʾala takyīf or normative-source selection.

## Governing naming rule
`DOMAIN_ROUTING_LAYER` is **not** an approved canonical name. The proposed provisional name is:
```
MASALA_TAKYIF_LAYER = طبقة تكييف المسألة
STATUS = PROPOSED_NOT_CANONICAL
OWNER_RATIFICATION_REQUIRED = YES
```

## Governing separations (no jump across layers)
```
TEXT_SIGNAL ≠ FRAME ≠ MASALA_TAKYIF ≠ NORMATIVE_SOURCE ≠ HUKM ≠ MANAT ≠ TANZIL ≠ FINAL_ANSWER
```
Every decision below carries CAUSE / CONDITIONS / PREVENTERS / VERDICT / EVIDENCE / RESIDUALS
(see the JSON artifacts for the machine-checked form).

## Sentence under operation
`مَاتَ مَلِكٌ عَنْ أُخْتٍ سَاكِنَةٍ مَعَهُ، فَأَرَادَ وَارِثُهُ طَرْدَهَا، فَتَحَاكَمَا.`

## Reference matrix
| # | الطبقة | المرجع الإنجليزي | ماذا يعطي؟ | المقابل العربي إن وجد | المقابل في Hokom / Taaqol | Open Source / Available | حكم الاستخدام الآن |
|--:|--------|------------------|-----------|------------------------|----------------------------|--------------------------|--------------------|
| 1 | Tokenization / Word Segmentation | Universal Dependencies English | تقطيع، POS، علاقات نحوية | UD Arabic / Arabic-PUD | Hokom: التقسيم، اللواصق، السطح، التطبيع | نعم | قابل للتوثيق/الربط كمرجع تقني |
| 2 | POS Tagging | Penn Treebank / UD | فئة الكلمة | UD Arabic + النحو العربي | Hokom: اسم/فعل/حرف، المبنيات، العوامل | UD متاح؛ Penn غالبًا مقيد | Hokom يملك الفئة محليًا |
| 3 | Lexical Semantics | WordNet | synsets، علاقات معنى | Arabic WordNet | Hokom: معنى معجمي مرشح | WordNet متاح؛ Arabic WordNet v4 متاح حسب GitHub/CC BY | candidate only |
| 4 | Verb Classes | VerbNet | طبقات الأفعال والأدوار والقيود | لا نعتمد أنه داخل Arabic WordNet إلا بدليل ملفي | Hokom: علاقات فعل/فاعل/مفعول لاحقًا | VerbNet متاح؛ الربط العربي غير محسوم | candidate only |
| 5 | Predicate-Argument | PropBank | المحمول وحججه | Arabic PropBank موجود بحثيًا | Hokom/Taaqol: القضوي والإفادة | بعضه متاح وبعض corpora مقيدة | لا ينتج حكمًا |
| 6 | Frame Semantics | FrameNet | أطر دلالية للأحداث والأفعال | المالك سيبني Arabic/Hokom FrameNet | Hokom: طبقة إطار دلالي مرخصة | English FrameNet متاح جزئيًا | يبنى كهيكل فقط الآن |
| 7 | WordNet ↔ FrameNet Bridge | WordFrameNet | جسر بين WordNet وFrameNet | يمكن الاستفادة منه تصميميًا | Hokom: lexical sense → frame candidate | متاح CC BY 3.0 حسب الصفحة | مرجع تصميم لا سلطة حكم |
| 8 | Legal Issue Spotting | LegalBench | كشف نوع المسألة قبل القاعدة | فقهيًا: التصور ثم التكييف ثم التنزيل | Taaqol: تكييف المسألة | متاح بحثيًا | تشبيه منهجي فقط |
| 9 | Legal Issue Dataset | Learned Hands | قصص قانونية مصنفة | لا مقابل فقهي جاهز | Taaqol لا يعتمدها كمصدر | متاح | لا يستعمل للتكييف الشرعي |
| 10 | Legal NLU Benchmark | LexGLUE | مهام فهم قانوني | ArabLegalEval جزئيًا | benchmark لا مصدر حكم | متاح بحثيًا | تقييم لا حكم |
| 11 | Fiqh/Nazila Takyif | لا يقابله مصدر NLP واحد | قريب من issue spotting بمنطق فقهي | التصور → التكييف → التنزيل | Taaqol: MASALA_TAKYIF_LAYER | يحتاج بناء مالك | لا ينتج إلا بعد تصديق |

## What Qiyas may do now (ALLOWED_NOW)
1. roadmap doc · 2. SOURCE_MANIFEST.json · 3. HOKOM_FRAMENET schema · 4. Arabic-WordNet/WordFrameNet
adapter skeleton · 5. FRAME_CANDIDATES (candidates only) · 6. record TEXT_SIGNALS from the nazila ·
7. guards blocking lafẓ→domain jumps · 8. AR_05 manager report · 9. strict output matrix · 10. tests.

## Forbidden now (FORBIDDEN_NOW)
Do not say the nazila is mīrāth; do not say it is qaḍāʾ; do not choose a normative source; produce no
ḥukm / manāṭ / tanzīl / final answer.

## Hokom-FrameNet build posture
`HOKOM_FRAMENET` is a **candidate layer** only (structure/schema now); frames are FRAME_CANDIDATES, and
the WordNet↔FrameNet (WordFrameNet) relation is a **design reference, not a ruling authority**
(`WORDNET_WORDFRAMENET_BRIDGE_STATUS = CANDIDATE_ONLY`).

## Owner-ratification gate
`MASALA_TAKYIF_LAYER` (naming + activation), any normative-source selection, and any promotion of a
FRAME_CANDIDATE to a bound frame all require explicit owner ratification.
