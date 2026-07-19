# Live Token Trace
## HOKOM-WORD-CLASS-OWNERSHIP-AUDIT-01
**HEAD**: 3cd85cf | **Date**: 2026-07-19  
**Method**: `hokom()` called on each token via `sys.path.insert(0,'.')` — read-only, no code modification

---

## Trace Table

| Token | P5_lexical_verdict | P5_lexical_class | morph_path | root | wazn | form_family | masdar | mushtaqat | inf_pos | tense | mood | voice | person | num | gender | Word Class Producible? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| هَلْ | OPERATOR_BOUNDARY | Closed Function Word | None | None | None | None | None | () | BUG:VERB | BUG:PAST | None | BUG:ACTIVE | BUG:3 | BUG:SG | BUG:M | HARF (via mabni) — no canonical label |
| مِنْ | OPERATOR_BOUNDARY | Closed Function Word | None | None | None | None | None | () | BUG:VERB | BUG:PAST | None | BUG:ACTIVE | BUG:3 | BUG:SG | BUG:M | HARF (via mabni) — no canonical label |
| مَنْ | OPERATOR_BOUNDARY | Closed Function Word | None | None | None | None | None | () | BUG:VERB | BUG:PAST | None | BUG:ACTIVE | BUG:3 | BUG:SG | BUG:M | HARF (via mabni) — no canonical label |
| هُوَ | OPEN | None | None | None | None | None | None | () | BUG:VERB | BUG:PAST | None | BUG:ACTIVE | BUG:3 | BUG:SG | BUG:M | ABSENT — pronoun not in catalog |
| هَذَا | OPEN | None | None | None | None | None | None | () | BUG:VERB | BUG:PAST | None | BUG:ACTIVE | BUG:3 | BUG:DU | BUG:M | ABSENT — demonstrative not in catalog |
| كَتَبَ | OPEN | None | ambiguous_morphology_path | (ك،ت،ب) | FA_A_LA | None | None | (ISM_FA3IL،ISM_MAKAN،ISM_ZAMAN،SIYAG_MUBALAGHAH) | VERB | PAST | None | ACTIVE | 3 | SG | M | FI3L (PAST) — not labelled |
| يَكْتُبُ | OPEN | None | verbal_root_path | None | None | None | None | () | VERB | IMPERFECT | INDICATIVE | ACTIVE | 3 | SG | M | FI3L (IMPERFECT) — not labelled |
| اُكْتُبْ | BLOCK | None | None | None | None | None | None | () | VERB | IMPERATIVE | IMPERATIVE | ACTIVE | 2 | SG | M | FI3L (IMPERATIVE) — BLOCKED at P5 |
| كَاتِبٌ | OPEN | None | nominal_morphology_path | (ك،ت،ب) | FA3IL | FA3IL_PARTICIPLE | None | () | None | None | None | None | None | None | None | ISM — not labelled |
| مَكْتُوبٌ | OPEN | None | nominal_morphology_path | (ك،ت،ب) | MAF3UL | None | None | () | None | None | None | None | None | None | None | ISM — not labelled |
| كِتَابٌ | OPEN | None | nominal_morphology_path | None | None | None | None | () | None | None | None | None | None | None | None | ISM — root deferred, not labelled |
| كِتَابَةٌ | OPEN | None | nominal_morphology_path | None | None | None | None | () | None | None | None | None | None | None | None | ISM (masdar) — root deferred, not labelled |
| مَجْلِسٌ | OPEN | None | nominal_morphology_path | (ج،ل،س) | MAF3IL | None | None | () | None | None | None | None | None | None | None | ISM — not labelled |
| مَضْرِبٌ | OPEN | None | nominal_morphology_path | (ض،ر،ب) | MAF3IL | None | None | () | None | None | None | None | None | None | None | ISM — not labelled |
| كَمْ | OPERATOR_BOUNDARY | Numerical Operator | None | None | None | None | None | () | BUG:VERB | BUG:PAST | None | BUG:ACTIVE | BUG:3 | BUG:SG | BUG:M | HARF (numerical) — no canonical label |
| كَذَا | OPERATOR_BOUNDARY | Numerical Operator | None | None | None | None | None | () | BUG:VERB | BUG:PAST | None | BUG:ACTIVE | BUG:3 | BUG:DU | BUG:M | HARF (numerical) — no canonical label |

---

## Key Observations

### 1. Zero tokens receive an ISM/FI3L/HARF label
Out of 16 tokens tested, **zero** receive a canonical top-level word-class label. The closest approximations are:
- `lexical_class="Closed Function Word"` for operator-boundary tokens (HARF-equivalent but different vocabulary)
- `morphology_path="verbal_root_path"` for يَكْتُبُ (FI3L-equivalent but structural heuristic)
- `morphology_path="nominal_morphology_path"` for كَاتِبٌ etc. (ISM-equivalent but structural heuristic)

### 2. Bug B-01 is live and widespread
All 5 OPERATOR_BOUNDARY tokens + 2 OPEN non-analyzed tokens (هُوَ، هَذَا) produce spurious VERB/tense features from the inflection engine. This affects 7 of 16 tokens (44%).

### 3. Pronouns and demonstratives are unclassified
هُوَ and هَذَا produce verdict=OPEN / lexical_class=None. They are not in the operators catalog or the match fails. These are مبنيات (indeclinable nominals) that should receive MABNI_BOUNDARY + lexical_class='Bound Nominal'.

### 4. Past-tense verb is ambiguous
كَتَبَ gets `morphology_path=ambiguous_morphology_path` because the surface has no unambiguous verbal marker (no imperfect prefix, no taa marbuta). The root and wazn are correctly resolved (ك،ت،ب / FA_A_LA) but the ambiguity stays at the morphology-path level.

### 5. Nominal tokens with root+wazn have no word class
كَاتِبٌ (FA3IL_PARTICIPLE, root=ك،ت،ب) and مَجْلِسٌ (MAF3IL, root=ج،ل،س) carry rich morphological analysis but no ISM label is synthesized.

### 6. اُكْتُبْ is BLOCKED but inflection still fires
The imperative form is blocked at P5 (hamzat al-wasl structure), yet the inflection engine still returns VERB/IMPERATIVE. This is consistent with Bug B-01 — the inflection engine is not gated on P5 verdict.

---

## Word Class Deducible (but not labelled)

| Token | Deducible class | Confidence | Evidence |
|---|---|---|---|
| هَلْ | HARF | HIGH | lexical_class=Closed Function Word |
| مِنْ | HARF | HIGH | lexical_class=Closed Function Word |
| مَنْ | HARF | HIGH | lexical_class=Closed Function Word |
| هُوَ | ISM (مضمر) | HIGH | Should be Bound Nominal — not in catalog |
| هَذَا | ISM (إشارة) | HIGH | Should be Bound Nominal — not in catalog |
| كَتَبَ | FI3L (ماضٍ) | MEDIUM | ambiguous path + FA_A_LA wazn |
| يَكْتُبُ | FI3L (مضارع) | HIGH | verbal_root_path |
| اُكْتُبْ | FI3L (أمر) | HIGH | inflection=IMPERATIVE (despite BLOCK) |
| كَاتِبٌ | ISM (مشتق) | HIGH | FA3IL_PARTICIPLE + nominal path |
| مَكْتُوبٌ | ISM (مشتق) | HIGH | MAF3UL + nominal path |
| كِتَابٌ | ISM (جامد) | MEDIUM | nominal path, root deferred |
| كِتَابَةٌ | ISM (مصدر) | MEDIUM | nominal path, root deferred |
| مَجْلِسٌ | ISM (جامد) | HIGH | MAF3IL + root + nominal path |
| مَضْرِبٌ | ISM (اسم مكان) | HIGH | MAF3IL + root + nominal path |
| كَمْ | HARF (عدد) | HIGH | lexical_class=Numerical Operator |
| كَذَا | HARF (كناية عدد) | HIGH | lexical_class=Numerical Operator |
