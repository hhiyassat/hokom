# HOKOM Golden Rules
# Canonical protected inventory of correct linguistic, architectural, governance, and closure rules.
# GOLDEN_RULES_DIGEST: sha256:7b45e54ed6f2968d5846363749a1861c7d69964305f873ef3d67a993b76ea668
# Last updated: HOKOM-GOLDEN-RULES-AND-LIVE-CLOSURE-CORRECTION-01

## 1. JAMID_AALAM_BOUNDARY
- All forms of لفظ الجلالة (اللَّهُ/اللَّهَ/اللَّهِ/بِاللَّهِ etc.) must remain JAMID_AALAM_BOUNDARY
- They must never be classified FI3L
- word_class=None, root=None, no verbal features
- Source: HOKOM-AYAT-AL-DAYN-LIVE-CONTEXT-BOUNDARY-SAFETY-AND-GOLD-REMEDIATION-01

## 2. FORM_X Recognition
- سَيَسْتَغْفِرُونَ → FI3L / VERBAL_IMPERFECT / FORM_X / root=غفر / person=3 / number=PL / gender=M / voice=ACTIVE / mood=INDICATIVE
- يَسْتَغْفِرُونَ → FI3L / VERBAL_IMPERFECT / FORM_X / root=غفر
- اِسْتَغْفِرُوا → FI3L / VERBAL_IMPERATIVE / FORM_X / person=2 / number=PL
- وَاسْتَشْهِدُوا → FI3L / VERBAL_IMPERATIVE / FORM_X
- Negative controls: سَيَكْتُبُونَ → FORM_I_IMPERFECT; أَكْرَمُوا → FORM_IV
- Source: HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02, HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 3. FORM_I Imperative with Object Enclitic
- فَاكْتُبُوهُ → FI3L / VERBAL_IMPERATIVE / FORM_I / root=كتب / person=2 / number=PL / gender=M / voice=ACTIVE / mood=NOT_APPLICABLE
- Proclitic فَ + alif-wasla + root-initial consonant ≠ FORM_VIII
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 4. Assimilated FORM_VIII
- وَاتَّقُوا → FI3L / VERBAL_IMPERATIVE / FORM_VIII / person=2 / number=PL
- وَلْيَتَّقِ → FI3L / VERBAL_IMPERFECT / FORM_VIII / person=3 / number=SG / mood=JUSSIVE
- Shadda at C2 after alif-wasla = assimilation marker, NOT FORM_II indicator
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 5. FORM_IV Past vs FORM_I
- آمَنُوا → FI3L / VERBAL_PAST / FORM_IV / root=ءمن / person=3 / number=PL / gender=M / voice=ACTIVE
- Hamza-fatha prefix on past-tense surface → FORM_IV (أَفْعَلَ pattern)
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 6. FORM_IV Active Voice (Imperfect)
- يُمِلَّ → FI3L / VERBAL_IMPERFECT / FORM_IV / person=3 / number=SG / gender=M / mood=SUBJUNCTIVE / voice=ACTIVE
- تُدِيرُونَهَا → FI3L / VERBAL_IMPERFECT / FORM_IV / root=دور / person=2 / number=PL / gender=M / mood=INDICATIVE / voice=ACTIVE
- Damma on imperfect prefix does NOT imply passive for FORM_IV; check internal vowel geometry
  (damma-prefix + kasra on C1 + hollow medial long-vowel → FORM_IV active)
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 7. Hollow Verb Dual Suffix
- يَكُونَا → FI3L / VERBAL_IMPERFECT / person=3 / number=DU / gender=M / mood=JUSSIVE / voice=ACTIVE
- Suffix ـَا on hollow verb imperfect = dual marker, not case ending
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 8. Prohibitive لا vs Negative لا
- وَلَا تَسْأَمُوا → mood=JUSSIVE (لا النَّاهِيَة — prohibitive, governs jussive)
- أَوْ لَا يَسْتَطِيعُ → يَسْتَطِيعُ mood=INDICATIVE (لا النَّافِيَة — negative, no jussive governance)
- لا after أَوْ / لَكِنْ / clause-internal disjunction = negative; لا at clause-start with imperative-semantics = prohibitive
- Source: HOKOM-LIVE-GOLD-ORACLE-COVERAGE-AND-GATE-HARDENING-02, HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 9. Contextual Mood (Sequential)
- وَلَا تَسْأَمُوا → JUSSIVE (prohibitive لا)
- أَلَّا تَرْتَابُوا → SUBJUNCTIVE (أَنْ + لا = أَلَّا)
- أَنْ تَكْتُبُوهُ → SUBJUNCTIVE
- أَلَّا تَكْتُبُوهَا → SUBJUNCTIVE
- وَإِنْ تَفْعَلُوا → JUSSIVE (conditional إِنْ)
- Source: HOKOM-AYAT-AL-DAYN-LIVE-CONTEXT-BOUNDARY-SAFETY-AND-GOLD-REMEDIATION-01

## 10. Correlated Ambiguity Representation
- تَضِلَّ: AmbiguityCandidate[{2,SG,M,'2MS'},{3,SG,F,'3FS'}]; in verse context إِحْدَاهُمَا resolves to 3FS
- فَتُذَكِّرَ: AmbiguityCandidate[{2,SG,M,'2MS'},{3,SG,F,'3FS'}]; in verse context resolves to 3FS
- Person/gender MUST NOT be represented as pipe-separated strings
- فَتُذَكِّرَ: imperfect تُـ is inflectional prefix (person marker), NOT FORM_V derivational تَـ
- فَتُذَكِّرَ cra_form_family=FORM_II (ذَكَّرَ), root=ذكر
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 11. ISM Subclass
- أَجَلٍ → ISM / word_class_subclass=LEXICAL_NOUN / root=ءجل
- Tanwin (ًٌٍ) on surface → ISM; but FA3IL-pattern ISM_FA3IL must not be inferred without active-participle morphology proof
- A bare-noun wazn (فَعَلَ / FA_A_LA) is NOT an active participle (فَاعِل); theoretical root-derivatives must not set the surface subclass
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 12. FORM_II Active vs FORM_V
- وَيُعَلِّمُكُمُ → FI3L / VERBAL_IMPERFECT / FORM_II / voice=ACTIVE
- تُـ prefix on FORM_II imperfect (تُفَعِّلُ) ≠ FORM_V تَفَعَّلَ derivational تَـ
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 13. ISM vs FI3L Routing
- وَامْرَأَتَانِ → ISM, not imperative/FI3L
- Dual feminine noun ending -تَانِ = nominal, not verbal
- Source: HOKOM-AYAT-AL-DAYN-PROTECTED-GOLD-REMEDIATION-01

## 14. Gold Oracle Field Policy
- Every GoldRecord must be compared on: word_class, word_class_subclass (when gold declares it), canonical_root (when gold declares it), cra_form_family (when gold declares it), person, number, gender, tense_aspect, mood, voice, ambiguity_candidates (as correlated bundles, not pipe strings)
- Policy labels: REQUIRED_EXACT, REQUIRED_ONE_OF, REQUIRED_CORRELATED_CANDIDATES, NOT_APPLICABLE, NOT_ASSERTED_WITH_REASON
- No field may be silently omitted from comparison
- Source: HOKOM-GOLDEN-RULES-AND-LIVE-CLOSURE-CORRECTION-01

## 15. Word-Class Justification
- JUSTIFIED: specific terminal boundary (JAMID_AALAM_BOUNDARY, SEGMENTATION_NO_LEXICAL_HOST) or OPERATOR_BOUNDARY from canonical operator owner
- UNJUSTIFIED: clear noun/verb/particle with no terminal boundary decision
- UNADJUDICATED: insufficient constitutional ownership decision
- TOTAL = JUSTIFIED + UNJUSTIFIED + UNADJUDICATED; no duplicates, no omissions
- Source: HOKOM-GOLD-MANIFEST-AMENDMENT-GUARD-PENETRATION-01

## 16. Manifest Digest Protection
- CORPUS_GOLD changes require CONSTITUTIONAL_AMENDMENT_ID — recomputed digest alone is insufficient
- AmendmentRecord requires: amendment_id, old/new_manifest_digest, changed_gold_key, old/new_expectation, rationale, affected_constitutional_contract
- Source: HOKOM-GOLD-MANIFEST-AMENDMENT-GUARD-PENETRATION-01

## 17. Golden Rules Digest Protection
- golden_rules.md is a canonical protected inventory; its SHA-256 digest is frozen in pipeline/governance/golden_rules_guard.py
- MODIFY or DELETE of an existing rule requires a GoldenRulesAmendmentRecord with a non-empty amendment_id — a recomputed digest alone is insufficient
- APPEND of a new rule with a valid amendment_id and rationale → ACCEPT
- Source: HOKOM-GOLDEN-RULES-AND-LIVE-CLOSURE-CORRECTION-01
