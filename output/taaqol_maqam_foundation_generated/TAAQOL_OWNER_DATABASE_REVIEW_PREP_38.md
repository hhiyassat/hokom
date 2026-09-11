# وثيقة مراجعة المالك لقاعدة البيانات (الجولة 38 — تحضير لا تصديق)

CATALOG_RECORDS = 123 · EXTERNAL_REFERENCE_RECORDS = 11 · OWNER_REVIEW_ROWS = **134**

**قرارات المالك المسموحة:** ACCEPT_AS_DATABASE_RECORD / DEFER / REJECT / NEEDS_SOURCE / NEEDS_FORMAT_FIX / NEEDS_OWNER_DEFINITION / NEEDS_EXTERNAL_VERIFICATION

الافتراض لكل صف: `owner_review_decision = DEFER` · `verdict = AWAITING_OWNER_REVIEW` · `canonical_status = CANDIDATE_ONLY`. لا اعتماد تلقائي، لا تعميم، لا حكم.

## 1. NAZILA_TEXT — 1 صف
- `CAT_AT_NAZILA` · used_as=TEXT_INPUT · table=arabic_text_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 2. NAZILA_TOKEN — 10 صف
- `CAT_LEX_t000` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t001` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t002` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t003` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t004` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t005` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t006` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t007` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t008` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_LEX_t009` · used_as=TEXT_INPUT · table=lexical_item_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 3. NORMATIVE_SOURCE_TEXT — 8 صف
- `CAT_AT_SOURCE_1` · used_as=SOURCE · table=normative_source_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_AT_SOURCE_2` · used_as=SOURCE · table=normative_source_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_AT_SOURCE_3` · used_as=SOURCE · table=normative_source_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_AT_SUKNA_SOURCE_1` · used_as=SOURCE · table=normative_source_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_SRC_SOURCE_1` · used_as=SOURCE · table=normative_source_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_SRC_SOURCE_2` · used_as=SOURCE · table=normative_source_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_SRC_SOURCE_3` · used_as=SOURCE · table=normative_source_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_SRC_SUKNA_SOURCE_1` · used_as=SOURCE · table=normative_source_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 4. OWNER_RULE_TEXT — 10 صف
- `CAT_OR_NO_HUKM_WITHOUT_SCP` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_QUESTION_NOT_FACT` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_REQUIREMENT_NOT_FACT` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_SOURCE_NOT_HUKM` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_POSSESSION_NOT_OWNERSHIP` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_FINAL_HUKM_NEEDS_OWNER` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_NO_EXPANSION_BEFORE_REGISTRIES` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_NO_UNLICENSED_SLOT_TRANSITION` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_AGENT_QUESTION_NOT_CANONICAL` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_OR_EVIDENCE_CITATION_ONLY` · used_as=GUARD · table=owner_rule_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 5. DOMAIN_TERM — 12 صف
- `CAT_DOM_MIRATH_RELATED_DOMAIN_CANDIDATE` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_QADA_RELATED_DOMAIN_CANDIDATE` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_TURKAH_RIGHTS_DOMAIN_CANDIDATE` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_SUKNA_OR_POSSESSION_DOMAIN_CANDIDATE` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_WORD_ميراث` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_WORD_تركة` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_WORD_قضاء` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_WORD_سكنى` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_WORD_يد_حيازة` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_WORD_دعوى` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_WORD_بينة` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_DOM_WORD_يمين` · used_as=DOMAIN_LABEL · table=domain_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 6. REQUIREMENT_TEXT — 50 صف
- `CAT_REQ_REQ01_NO_CHILD` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ02_OTHER_HEIRS` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ03_HEIR_CAPACITY` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ04_HOUSE_STATUS` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ05_PRIOR_PERMISSION` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ06_HAND_CREDIBLE` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ07_CLAIM_CONTENT` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ08_DEFENSE_CONTENT` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ09_EVIDENCE` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_REQ_REQ10_QARINA_STRENGTH` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_NREQ_NR_REQ01_NO_CHILD_FACT` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_NREQ_NR_REQ01_NO_CHILD_SOURCE` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_NREQ_NR_REQ01_NO_CHILD_OWNER` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_NREQ_NR_REQ01_NO_CHILD_GATE` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_NREQ_NR_REQ02_OTHER_HEIRS_FACT` · used_as=REQUIREMENT · table=requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- … (+35 صف في JSON)
## 7. FACT_CANDIDATE_TEXT — 5 صف
- `CAT_FCAND_FC1_KING_DIED` · used_as=FACT_CANDIDATE · table=factual_claim_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_FCAND_FC2_HAS_SISTER` · used_as=FACT_CANDIDATE · table=factual_claim_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_FCAND_FC3_SISTER_RESIDING_WITH_HIM` · used_as=FACT_CANDIDATE · table=factual_claim_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_FCAND_FC4_HEIR_WANTED_EXPULSION` · used_as=FACT_CANDIDATE · table=factual_claim_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_FCAND_FC5_LITIGATION_OCCURRED` · used_as=FACT_CANDIDATE · table=factual_claim_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 8. MISSING_FACT_REQUIREMENT_TEXT — 9 صف
- `CAT_MISS_MF1_NO_CHILD` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MISS_MF2_NO_OTHER_HEIRS` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MISS_MF3_HEIR_CAPACITY` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MISS_MF4_HOUSE_FINAL_OWNERSHIP` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MISS_MF5_HOUSE_ALL_ESTATE` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MISS_MF6_PRIOR_RESIDENCE_PERMISSION` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MISS_MF7_SISTER_HAND_VALIDITY` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MISS_MF8_EVIDENCE_PRESENT` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MISS_MF9_LITIGATION_OUTCOME` · used_as=MISSING_FACT_REQUIREMENT · table=missing_fact_requirement_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 9. HUKM_CANDIDATE_TEXT — 4 صف
- `CAT_HUKM_HC1_SISTER_SHARE` · used_as=HUKM_CANDIDATE · table=hukm_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_HUKM_HC2_CLAIM_BURDEN_OF_PROOF` · used_as=HUKM_CANDIDATE · table=hukm_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_HUKM_HC3_POSSESSION_STAYS_PENDING_EXAMINATION` · used_as=HUKM_CANDIDATE · table=hukm_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_HUKM_HC4_COMPOSITE_LINK_NO_OUTCOME` · used_as=HUKM_CANDIDATE · table=hukm_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 10. MANAT_CANDIDATE_TEXT — 4 صف
- `CAT_MANAT_MC1_SISTER_EXISTENCE_AND_ENTITLEMENT_CONDITIONS` · used_as=MANAT_CANDIDATE · table=manat_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MANAT_MC2_CLAIM_DISPUTE_AND_PROOF_BURDEN` · used_as=MANAT_CANDIDATE · table=manat_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MANAT_MC3_STANDING_HAND_STATE_BEFORE_EXPULSION` · used_as=MANAT_CANDIDATE · table=manat_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_MANAT_MC4_COMPOSITE_MANAT_LINK_NO_OUTCOME` · used_as=MANAT_CANDIDATE · table=manat_candidate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 11. GUARD_TEXT — 10 صف
- `CAT_GATE_NO_FINAL_MANAT` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_NO_TANZIL` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_NO_FINAL_HUKM` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_NO_FINAL_ANSWER` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_OWNER_RATIFICATION_REQUIRED` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_AUTHORITY_LEAK_PREVENTED` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_SILENT_FALLBACK_COUNT_0` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_ASSERTED_NOT_MEASURED_COUNT_0` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_READY_FOR_EXPANSION_NO` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `CAT_GATE_FULL_TAAQOL_PROJECT_CLOSED_NO` · used_as=GUARD · table=guard_and_gate_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
## 12. EXTERNAL_REFERENCE_LAYER_CANDIDATES — 11 صف
- `XREF01_UD` · used_as=TECHNICAL_REFERENCE_CANDIDATE · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF02_PENN_UD` · used_as=LOCAL_HOKOM_OWNS_CATEGORY · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF03_WORDNET` · used_as=CANDIDATE_ONLY · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF04_VERBNET` · used_as=CANDIDATE_ONLY · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF05_PROPBANK` · used_as=NO_HUKM_PRODUCED · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF06_FRAMENET` · used_as=SKELETON_ONLY · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF07_WORDFRAMENET` · used_as=DESIGN_REFERENCE_ONLY · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF08_LEGALBENCH` · used_as=METHODOLOGICAL_ANALOGY_ONLY · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF09_LEARNED_HANDS` · used_as=NOT_USED_FOR_SHARI_TAKYIF · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF10_LEXGLUE` · used_as=EVALUATION_ONLY · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE
- `XREF11_FIQH_NAZILA_TAKYIF` · used_as=OWNER_BUILT_REQUIRED · table=external_reference_registry · decision=DEFER · action=OWNER_REVIEW_AND_DECIDE

---
*OWNER_REVIEW_PREP_IS_NOT_RATIFICATION · كل صف بانتظار قرار المالك.*
