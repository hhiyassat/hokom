# كتالوج مصدرية بيانات اللغة العربية (الجولة 37 — جرد مستقبلي)

REPORT_SOURCE = CODE_AND_ARTIFACTS_ONLY · إجمالي السجلات = **123** · أنواع النصوص = 11

**المبدأ:** وجود النص في artifact لا يجعله قاعدة عامة؛ كل سجل CANDIDATE_ONLY حتى تصديق المالك.

## عدد النصوص حسب النوع
- NAZILA_TEXT = 1
- NAZILA_TOKEN = 10
- OWNER_RULE_TEXT = 10
- NORMATIVE_SOURCE_TEXT = 8
- DOMAIN_TERM = 12
- REQUIREMENT_TEXT = 50
- FACT_CANDIDATE_TEXT = 5
- MISSING_FACT_REQUIREMENT_TEXT = 9
- HUKM_CANDIDATE_TEXT = 4
- MANAT_CANDIDATE_TEXT = 4
- GUARD_TEXT = 10

## عيّنة من السجلات (النص / النوع / المصدر / الصيغة / الاستعمال / الجدول)
- `CAT_AT_NAZILA` [NAZILA_TEXT] · NAZILA_TEXT · FULL_TEXT · used_as=TEXT_INPUT · table=arabic_text_registry · owner_ratified=NO
- `CAT_AT_SOURCE_1` [NORMATIVE_SOURCE_TEXT] · UNKNOWN_ARTIFACT_DERIVED · JSON_FIELD · used_as=SOURCE · table=normative_source_registry · owner_ratified=YES
- `CAT_AT_SOURCE_2` [NORMATIVE_SOURCE_TEXT] · UNKNOWN_ARTIFACT_DERIVED · JSON_FIELD · used_as=SOURCE · table=normative_source_registry · owner_ratified=YES
- `CAT_AT_SOURCE_3` [NORMATIVE_SOURCE_TEXT] · UNKNOWN_ARTIFACT_DERIVED · JSON_FIELD · used_as=SOURCE · table=normative_source_registry · owner_ratified=YES
- `CAT_AT_SUKNA_SOURCE_1` [NORMATIVE_SOURCE_TEXT] · UNKNOWN_ARTIFACT_DERIVED · JSON_FIELD · used_as=SOURCE · table=normative_source_registry · owner_ratified=YES
- `CAT_SRC_SOURCE_1` [NORMATIVE_SOURCE_TEXT] · QURAN · JSON_FIELD · used_as=SOURCE · table=normative_source_registry · owner_ratified=YES
- `CAT_SRC_SOURCE_2` [NORMATIVE_SOURCE_TEXT] · HADITH · JSON_FIELD · used_as=SOURCE · table=normative_source_registry · owner_ratified=YES
- `CAT_SRC_SOURCE_3` [NORMATIVE_SOURCE_TEXT] · HADITH · JSON_FIELD · used_as=SOURCE · table=normative_source_registry · owner_ratified=YES
- `CAT_SRC_SUKNA_SOURCE_1` [NORMATIVE_SOURCE_TEXT] · FIQH_SOURCE · JSON_FIELD · used_as=SOURCE · table=normative_source_registry · owner_ratified=YES
- `CAT_LEX_t000` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t001` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t002` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t003` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t004` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t005` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t006` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t007` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t008` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_LEX_t009` [NAZILA_TOKEN] · NAZILA_TEXT · TOKEN · used_as=TEXT_INPUT · table=lexical_item_registry · owner_ratified=NO
- `CAT_DOM_MIRATH_RELATED_DOMAIN_CANDIDATE` [DOMAIN_TERM] · GENERATED_CANDIDATE · JSON_FIELD · used_as=DOMAIN_LABEL · table=domain_candidate_registry · owner_ratified=NO
- `CAT_DOM_QADA_RELATED_DOMAIN_CANDIDATE` [DOMAIN_TERM] · GENERATED_CANDIDATE · JSON_FIELD · used_as=DOMAIN_LABEL · table=domain_candidate_registry · owner_ratified=NO
- `CAT_DOM_TURKAH_RIGHTS_DOMAIN_CANDIDATE` [DOMAIN_TERM] · GENERATED_CANDIDATE · JSON_FIELD · used_as=DOMAIN_LABEL · table=domain_candidate_registry · owner_ratified=NO
- `CAT_DOM_SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE` [DOMAIN_TERM] · GENERATED_CANDIDATE · JSON_FIELD · used_as=DOMAIN_LABEL · table=domain_candidate_registry · owner_ratified=NO
- `CAT_DOM_WORD_ميراث` [DOMAIN_TERM] · GENERATED_CANDIDATE · JSON_FIELD · used_as=DOMAIN_LABEL · table=domain_candidate_registry · owner_ratified=NO
- `CAT_DOM_WORD_تركة` [DOMAIN_TERM] · GENERATED_CANDIDATE · JSON_FIELD · used_as=DOMAIN_LABEL · table=domain_candidate_registry · owner_ratified=NO
- … (+98 أخرى في JSON)

## طبقة المراجع الخارجية (EXTERNAL_REFERENCE_LAYER_CANDIDATES — مستقلة)
مراجع تقنية/بحثية ذكرها المالك كمقابلات/أمثلة/مصادر تصميمية محتملة، لا سلطات حاكمة داخل Hokom/Taaqol:
- `XREF01_UD` [Tokenization / Word Segmentation] — Universal Dependencies English / UD Arabic · usage_now=TECHNICAL_REFERENCE_CANDIDATE · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF02_PENN_UD` [POS Tagging] — Penn Treebank / UD · usage_now=LOCAL_HOKOM_OWNS_CATEGORY · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF03_WORDNET` [Lexical Semantics] — WordNet / Arabic WordNet · usage_now=CANDIDATE_ONLY · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF04_VERBNET` [Verb Classes] — VerbNet · usage_now=CANDIDATE_ONLY · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF05_PROPBANK` [Predicate-Argument] — PropBank / Arabic PropBank · usage_now=NO_HUKM_PRODUCED · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF06_FRAMENET` [Frame Semantics] — FrameNet · usage_now=SKELETON_ONLY · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF07_WORDFRAMENET` [WordNet <-> FrameNet Bridge] — WordFrameNet · usage_now=DESIGN_REFERENCE_ONLY · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF08_LEGALBENCH` [Legal Issue Spotting] — LegalBench · usage_now=METHODOLOGICAL_ANALOGY_ONLY · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF09_LEARNED_HANDS` [Legal Issue Dataset] — Learned Hands · usage_now=NOT_USED_FOR_SHARI_TAKYIF · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF10_LEXGLUE` [Legal NLU Benchmark] — LexGLUE / ArabLegalEval · usage_now=EVALUATION_ONLY · DESIGN_OR_BENCHMARK_REFERENCE_ONLY
- `XREF11_FIQH_NAZILA_TAKYIF` [Fiqh/Nazila Takyif] — Fiqh/Nazila Takyif · usage_now=OWNER_BUILT_REQUIRED · DESIGN_OR_BENCHMARK_REFERENCE_ONLY

*كل مرجع خارجي: EXTERNAL_REFERENCE_CANDIDATE_ONLY · creates_arabic_rule=NO · creates_shari_hukm=NO · owner_ratification_required=YES · availability_verification_status=OWNER_SUPPLIED_CLAIM_NOT_VERIFIED_IN_THIS_ROUND.*

---
*كل سجل verdict=DEFER_FOR_OWNER_DATABASE_RATIFICATION · canonical=CANDIDATE_ONLY · SOURCE_RATIFIED ≠ GENERALIZED_RULE.*
