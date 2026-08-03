# Hokom Golden Rules

**Canonical filename:** `golden_rules.md`  
**Purpose:** Preserve the correct linguistic, architectural, governance, and closure rules already established in Hokom so that later implementation phases cannot silently weaken or replace them.

---

## 1. Status and authority

This file is a protected engineering reference.

A rule recorded here must not be changed, weakened, removed, or reinterpreted by an ordinary implementation phase.

Any change requires:

- an explicit `CONSTITUTIONAL_AMENDMENT_ID`;
- the old rule;
- the proposed new rule;
- a technical and linguistic rationale;
- the affected contracts and tests;
- the old and new manifest digests;
- an approved semantic-diff declaration.

A matching recomputed digest alone does not authorize a rule change.

---

## 2. Ownership boundaries

### 2.1 Hokom ownership

Hokom owns the Arabic linguistic values supplied to the algebraic layer, including:

- word class and canonical subclass;
- root and radical analysis;
- wazn and form-family analysis;
- masdar and derivatives;
- inflectional features;
- contextual mood and agreement evidence;
- explicit ambiguity and deferral reasons.

### 2.2 Taaqol ownership

Taaqol owns:

- abstract Slot Geometry Algebra;
- Gamma;
- TransitionGate;
- DomainTransitionLicense;
- algebraic claim evaluation.

A downstream Taaqol verdict cannot repair an incorrect linguistic value supplied by Hokom.

This file must not be used to modify Taaqol, SGA, Gamma, TransitionGate, or DomainTransitionLicense.

---

## 3. Monotonic semantic evolution

Permitted state transitions:

```text
UNKNOWN   -> FILLED | DEFERRED | AMBIGUOUS
AMBIGUOUS -> FILLED when sufficient evidence resolves it
DEFERRED  -> FILLED only by the registered canonical owner
FILLED(A) -> FILLED(A) is idempotent
```

Forbidden without an explicit constitutional amendment:

```text
FILLED(A) -> FILLED(B)
TERMINAL_BOUNDARY -> downstream linguistic analysis
NOT_APPLICABLE -> another semantic value
non-owner -> write to an owned semantic field
context carrier -> create a new word class
```

A later layer may refine only fields it owns and only when the upstream record is eligible for refinement.

---

## 4. Terminal-boundary immutability

A terminal boundary is immutable downstream.

After a terminal boundary is emitted, the record must not reach:

- verbal tense detection;
- inflection extraction;
- root analysis;
- wazn analysis;
- verbal word-class reconciliation;
- contextual mood refinement.

The sequential context carrier may refine only an already valid, non-terminal `FI3L` record.

It must never change:

```text
ISM -> FI3L
HARF -> FI3L
JAMID -> FI3L
MABNI -> FI3L
boundary-stopped -> FI3L
word-class-deferred -> FI3L
```

---

## 5. Lafz al-Jalalah protection

All licensed forms of lafz al-Jalalah must remain intercepted by the existing closed:

```text
JAMID_AALAM_BOUNDARY
```

Examples include:

```text
اللَّهُ
اللَّهَ
اللَّهِ
وَاللَّهُ
بِاللَّهِ
لِلَّهِ
```

Required invariants:

```text
boundary_type = JAMID_AALAM_BOUNDARY
terminal = true
root = None
word_class != FI3L
no tense
no mood
no person
no number
no gender
no voice
no verbal claim licensed
```

No contextual or Phase 5 logic may override this boundary.

---

## 6. Closed shadda rule

The existing shadda representation is closed and must not be reopened.

Normalized gemination may represent shadda as a doubled consonant. Any rule that needs shadda evidence must support the canonical normalized representation instead of introducing a second shadda engine or altering the closed contract.

Assimilated forms must be distinguished through augmentation and assimilation geometry, not by reopening shadda ownership.

---

## 7. Segmentation and host preservation

Clitics, inflectional suffixes, and object pronouns must remain distinct.

The analysis must preserve morphology such as:

```text
فَ + اُكْتُبُوا + هُ
وَ + اِسْتَشْهِدُوا
سَ + يَ + اِسْتَـ + غ ف ر + ون
```

When the orthographic alif after plural waw is dropped before an enclitic, the plural morpheme must still be recovered.

Examples:

```text
اُكْتُبُوهُ
اُكْتُبُوهَا
تَكْتُبُوهُ
تَكْتُبُوهَا
تُدِيرُونَهَا
```

A segmentation result must not discard evidence needed by the canonical morphology owner.

---

## 8. Word-class rules

### 8.1 Tanwin

A nominal surface ending in a tanwin diacritic:

```text
ٌ  ٍ  ً
```

is nominal evidence and must be evaluated before an incompatible verbal route.

Example:

```text
أَجَلٍ -> ISM
```

### 8.2 Dual nouns

A bare form ending in the nominative dual suffix `ان`, when supported by nominal geometry, must not be classified as an imperative verb.

Example:

```text
وَامْرَأَتَانِ -> ISM, dual, feminine
```

### 8.3 Known nominal and functional cases

Clear nominal or functional records must not remain unclassified merely because a broad route deferred.

Examples requiring a specific owner or terminal reason include:

```text
رَبَّهُ
مِنْهُ
فَلَيْسَ
فَإِنْ
وَإِنْ
فَإِنَّهُ
كَمَا
بَيْنَكُمْ
الْحَقُّ
عِنْدَ
الْأُخْرَى
```

`WORD_CLASS_DEFERRED` alone is not a justification.

---

## 9. Word-class accounting

Every blank word class must belong to exactly one category:

```text
JUSTIFIED
UNJUSTIFIED
UNADJUDICATED
```

Each classification record must include:

- token index;
- surface;
- category;
- reason code;
- constitutional owner;
- terminal-boundary proof when categorized as justified.

Required accounting invariant:

```text
TOTAL = JUSTIFIED + UNJUSTIFIED + UNADJUDICATED
```

No blank record may be omitted or counted more than once.

Broad labels such as `OPERATOR_BOUNDARY` or `WORD_CLASS_DEFERRED` do not automatically prove justification.

---

## 10. Form-family rules

### 10.1 FORM X

FORM X must be protected explicitly, not incidentally.

Required morphology:

```text
سَيَسْتَغْفِرُونَ:
سَ + يَ + اِسْتَـ + غ ف ر + ون
```

Required protected probes:

```text
سَيَسْتَغْفِرُونَ -> FORM_X, VERBAL_IMPERFECT
يَسْتَغْفِرُونَ   -> FORM_X, VERBAL_IMPERFECT
اِسْتَغْفِرُوا    -> FORM_X, VERBAL_IMPERATIVE
وَاسْتَشْهِدُوا   -> FORM_X, VERBAL_IMPERATIVE
```

Negative controls:

```text
سَيَكْتُبُونَ -> FORM_I_IMPERFECT, not FORM_X
أَكْرَمُوا    -> FORM_IV, not FORM_X
```

The future particle and imperfect prefix must be stripped in the correct order before detecting the derivational augment.

### 10.2 FORM IV past

A valid past form with the `أَفْعَلَ` augmentation must be classified as FORM IV, not FORM I.

Example:

```text
آمَنُوا -> FORM_IV
```

### 10.3 FORM I imperative

An alif-wasla imperative is not automatically FORM VIII.

Example:

```text
فَاكْتُبُوهُ -> FORM_I, root كتب
```

FORM VIII requires actual inserted/assimilated `ت` evidence.

### 10.4 Assimilated FORM VIII

An assimilated FORM VIII must not be classified as FORM II merely because the normalized surface contains gemination.

Examples:

```text
وَاتَّقُوا -> FORM_VIII
وَلْيَتَّقِ -> FORM_VIII
```

### 10.5 FORM II imperfect

The imperfect prefix `تُـ` is inflectional and must not be confused with the derivational `تَـ` of FORM V.

Example:

```text
فَتُذَكِّرَ -> FORM_II, not FORM_V
```

### 10.6 FORM IV imperfect

Example:

```text
تُدِيرُونَهَا -> FORM_IV
```

The canonical lexical relation is:

```text
أَدَارَ -> يُدِيرُ -> تُدِيرُونَ
root = دور
```

It must not be emitted as FORM I with root `دير`.

---

## 11. Voice rules

Voice must be inferred from internal vowel geometry, not from the damma of the imperfect prefix alone.

Examples:

```text
يُفَعِّلُ -> ACTIVE
يُفَعَّلُ -> PASSIVE
```

Required active cases include:

```text
وَيُعَلِّمُكُمُ
يُمِلَّ
تُدِيرُونَهَا
```

The prefix damma alone does not license `PASSIVE`.

---

## 12. Number and suffix rules

### 12.1 Plural waw before enclitics

Plural waw before an object pronoun must yield plural number even when the orthographic alif is absent.

### 12.2 Dual imperfect

A hollow imperfect ending in dual `ـا`, without plural-waw evidence, must be recognized as dual.

Example:

```text
يَكُونَا -> number=DUAL
```

### 12.3 Suffix-free hollow imperfect

A suffix-free hollow imperfect beginning with `تَـ` is not plural merely because the surface contains a long vowel.

Example:

```text
تَكُونَ -> SG before contextual agreement resolution
```

---

## 13. Context and mood rules

The demo and production pipeline must use a typed sequential context carrier. It may carry:

- previous token;
- governing particle;
- governing scope;
- coordination state;
- expected mood;
- evidence provenance;
- subject/lookahead agreement evidence.

It must not concatenate arbitrary strings as a substitute for typed context.

### 13.1 Subjunctive governors

Examples:

```text
أَنْ تَكْتُبُوهُ     -> SUBJUNCTIVE
أَلَّا تَكْتُبُوهَا  -> SUBJUNCTIVE
أَلَّا تَرْتَابُوا   -> SUBJUNCTIVE
أَنْ تَضِلَّ          -> SUBJUNCTIVE
فَتُذَكِّرَ           -> remains under the relevant coordinated scope
```

### 13.2 Jussive governors

Examples:

```text
لَا الناهية + مضارع  -> JUSSIVE
إِنْ الشرطية + مضارع -> JUSSIVE
لَمْ + مضارع         -> JUSSIVE
لِ الأمر + مضارع     -> JUSSIVE
```

### 13.3 Negative versus prohibitive `لا`

Not every `لا` is prohibitive.

Example:

```text
أَوْ لَا يَسْتَطِيعُ
```

Here `لا` is negative, so:

```text
يَسْتَطِيعُ -> INDICATIVE
```

The carrier must distinguish semantic/syntactic scope, not classify every `لا` as jussive-governing.

---

## 14. Correlated ambiguity

Ambiguity must be represented as correlated candidate bundles.

Correct representation:

```json
[
  {"person": "2", "number": "SG", "gender": "M", "reading": "2MS"},
  {"person": "3", "number": "SG", "gender": "F", "reading": "3FS"}
]
```

Incorrect representation:

```text
person = 2|3
gender = M|F
```

Independent unions create invalid cross-products such as `2FS` or `3MS`.

The exported record must contain either:

- a resolved person/number/gender bundle; or
- structured correlated candidates.

---

## 15. Subject-based agreement resolution

In the live verse context:

```text
تَضِلَّ ... إِحْدَاهُمَا
فَتُذَكِّرَ إِحْدَاهُمَا
تَكُونَ تِجَارَةٌ حَاضِرَةٌ
```

the subject/lookahead evidence resolves the reading to:

```text
person=3
number=SG
gender=F
```

If the owning syntax layer cannot yet resolve the agreement, the system must preserve explicit correlated ambiguity and keep closure open. It must not license a false 2MS or export independent pipe strings as if they were a resolved analysis.

---

## 16. Gold-oracle field completeness

Every protected GoldRecord must define an explicit policy for every relevant field:

```text
REQUIRED_EXACT
REQUIRED_ONE_OF
REQUIRED_CORRELATED_CANDIDATES
NOT_APPLICABLE
NOT_ASSERTED_WITH_REASON
```

No field may be silently omitted from comparison.

Fields include, when applicable:

- word class;
- word-class subclass;
- canonical root;
- form family;
- wazn;
- person;
- number;
- gender;
- tense/aspect;
- mood;
- voice;
- boundary state;
- pipeline scope and deferral reason.

Removing one required field comparison must make governance fail.

---

## 17. Protected gold manifest

Protected expectations must be independent of engine output.

Protection requires:

- a canonical manifest digest;
- commit/artifact binding;
- a separate amendment record;
- old and new expectation diffs;
- amendment ID;
- rationale;
- affected contract;
- governance tests.

A developer must not:

- rewrite an expectation to match faulty engine output;
- remove an assertion because its owner is inconvenient;
- recalculate a digest and treat that alone as authorization;
- classify a known mismatch as zero by excluding it.

A known out-of-scope mismatch remains a blocking residual unless an authorized separate phase owns and fixes it.

---

## 18. Semantic regression firewall

Every implementation phase must declare:

- baseline head;
- candidate head;
- intended tokens;
- intended fields;
- intended reason codes.

Compare the canonical live corpus and protected probes field by field.

Required closure values:

```text
UNEXPECTED_SEMANTIC_DIFFS = 0
CLOSED_CONTRACT_REGRESSIONS = 0
TERMINAL_BOUNDARY_OVERRIDES = 0
```

A change to a previously correct field outside the declared impact set must fail the phase.

---

## 19. Test architecture

Permanent default tests must remain green.

Use:

```text
synthetic malformed fixture -> detector finds defect -> pytest PASS
live pipeline -> closure gate decides open/closed
```

Do not leave deliberately failing tests on `main`.

Do not weaken a protected assertion merely to restore a green suite.

---

## 20. Closure gate

The closure gate must operate on the exact unfiltered in-memory records used to generate the CSV.

It must verify that CSV serialization matches those records.

Required closure metrics include:

```text
LIVE_GOLD_TOKEN_MISMATCHES
LIVE_FORM_FAMILY_MISMATCHES
LIVE_PERSON_NUMBER_GENDER_MISMATCHES
LIVE_VOICE_MISMATCHES
LIVE_CONTEXT_MOOD_MISMATCHES
LIVE_UNCORRELATED_AMBIGUITY
LIVE_NONVERBS_AS_VERBS
LIVE_VERBS_AS_NOUNS
KNOWN_OUT_OF_SCOPE_FORM_RESIDUALS
LIVE_JAMID_BOUNDARY_VIOLATIONS
UNJUSTIFIED_WORD_CLASS_NOT_OPENED
UNEXPECTED_SEMANTIC_DIFFS
CLOSED_CONTRACT_REGRESSIONS
TERMINAL_BOUNDARY_OVERRIDES
CSV_IN_MEMORY_DIVERGENCES
```

All closure-blocking metrics must be zero.

Focused tests are not closure evidence by themselves.

A phase is not closed while:

- any test fails;
- any protected gold field mismatches;
- the canonical macOS Python 3.12.4 full suite is not proven green;
- regenerated JSON, CSV, and HTML do not match the in-memory records;
- the separate-process closure gate exits nonzero.

---

## 21. Canonical execution environment

Canonical closure execution:

```text
macOS
Python 3.12.4
.venv-py312
```

A report containing environment failures cannot be declared closed until the canonical environment passes.

---

## 22. Current observed nonconformities at `b0fca1e`

This section records observed defects. These are not golden rules and must not be converted into accepted expectations.

### 22.1 `يَسْتَطِيعُ`

Current live CSV:

```text
mood=JUSSIVE
```

Required:

```text
mood=INDICATIVE
```

### 22.2 `تُدِيرُونَهَا`

Current live CSV:

```text
root=دير
form_family=FORM_I_IMPERFECT
```

Required:

```text
root=دور
form_family=FORM_IV
```

### 22.3 `أَجَلٍ`

Current live CSV:

```text
word_class=ISM
word_class_subclass=ISM_FA3IL
```

Required:

```text
word_class=ISM
word_class_subclass=LEXICAL_NOUN
```

### 22.4 Context-resolved agreement

Current CSV exports:

```text
تَضِلَّ       -> person=2|3, gender=M|F
فَتُذَكِّرَ   -> person=2|3, gender=M|F
تَكُونَ       -> person=2|3, gender=M|F
```

Required live-context result:

```text
person=3
number=SG
gender=F
```

or, before resolution, structured correlated candidates.

### 22.5 Word-class accounting

The current claim:

```text
TOTAL=21
JUSTIFIED=21
UNJUSTIFIED=0
```

requires re-audit.

At minimum inspect:

```text
رَبَّهُ
مِنْهُ
فَلَيْسَ
فَإِنْ
وَإِنْ
فَإِنَّهُ
كَمَا
```

No row is justified without a specific owner and terminal proof.

### 22.6 Full-suite evidence

The reported:

```text
986 passed, 3 failures
```

is not canonical closure.

Required evidence:

```text
full macOS Python 3.12.4 suite = 0 failures
fresh output SHA-256
separate-process closure gate = 0
```

---

## 23. Maintenance rule

Every future linguistic phase must:

1. read this file before implementation;
2. cite which golden rules it touches;
3. declare intended semantic changes;
4. leave all unrelated golden rules unchanged;
5. append only newly proven rules;
6. never rewrite historical rules silently;
7. update this file only with amendment metadata when changing an existing protected rule.

---

## 24. Review of `RULES.md` and rule-adoption policy

**Reviewed source:** `RULES.md`, documented on 2026-05-23 as a broad reference for an earlier rule-based engine.

The source contains four distinct kinds of statements. They must not be treated as one authority class:

```text
ACTIVE_CONFIRMED
    A rule already used and protected by the current Hokom architecture.

ACTIVE_CONSTRAINT
    A correct constraint that governs current implementation even when the
    exact historical function, filename, catalog, or algorithm is no longer used.

POTENTIAL_NOT_YET_OWNED
    A linguistically plausible or correct rule that is not yet owned,
    implemented, integrated, or closed in the current Hokom pipeline.

HISTORICAL_OR_REJECTED
    A historical implementation detail, stale path/count, over-broad heuristic,
    or statement that conflicts with a current closed contract.
```

Rules imported from `RULES.md` do not inherit canonical status merely because they were previously implemented.

A rule becomes active golden law only when all of the following are known:

```text
canonical owner
typed input and output
evidence requirement
boundary conditions
negative controls
general tests
semantic regression impact
closure commit
```

Unowned rules remain potential rules and must not be used by runtime code as implicit evidence.

Historical filenames, line numbers, dataset sizes, and engine names are provenance only. They are not current architecture contracts.

---

## 25. Adopted active rules from `RULES.md`

The following rules are adopted because they agree with the current Hokom contracts and are already used, required, or explicitly protected.

### 25.1 Preserve original and analytical surfaces

The pipeline must preserve at least:

```text
original_surface
canonical_normalized_surface
segmented_host_surface
morphology_surface
```

Normalization must never destroy the ability to reconstruct or audit the original token.

A comparison-oriented normalization is not permission to overwrite the original Qur'anic or user-provided surface.

### 25.2 Unicode and non-letter normalization

Canonical normalization may:

- apply Unicode canonical normalization;
- remove tatweel from the analytical representation;
- normalize the ordering of combining marks;
- remove non-letter Qur'anic recitation marks from the analytical representation.

It must preserve the original surface and record any transformation provenance.

Recitation marks are not Arabic root letters or pattern radicals.

### 25.3 Preserve linguistically significant letter identities

The analytical pipeline must preserve evidence carried by:

```text
أ إ ؤ ئ ء
ى
ة
```

The following are forbidden as unconditional normalization:

```text
all hamzas -> و
ى -> ي
ة -> ت
```

Any later canonical relation between these letters requires evidence from the owning morphological or lexical layer.

### 25.4 Original hamza is not a weak radical

An original hamza must remain a hamza in root extraction unless a separately owned rule proves otherwise.

Protected example:

```text
تَسْأَمُوا
root = س أ م
not س م و
```

Hamza-seat normalization may unify presentation for comparison, but it must not erase radical identity.

### 25.5 Strict segmentation-before-morphology order

The following ordering constraint is active:

```text
normalize while preserving original
-> segment proclitics, host, inflectional suffixes, and enclitics
-> apply terminal lexical/functional boundaries
-> determine eligible linguistic path
-> analyze root and form through their canonical owners
-> derive inflection and contextual refinements
```

Therefore:

```text
no root extraction before segmentation
no form matching on an unsegmented full token
no blind suffix stripping before suffix type is licensed
no contextual refinement before a valid base analysis exists
```

Root and form owners may exchange typed evidence, but neither may bypass segmentation or terminal boundaries.

### 25.6 Typed clitic separation

The segmenter must distinguish at least:

```text
conjunction or discourse proclitic
prepositional proclitic
definite article
future particle
imperfect prefix
inflectional subject suffix
nominal number suffix
object or possessive enclitic
```

A shared surface ending such as `ون`, `ين`, `وا`, or `ان` must not be assigned a type without word-class and inflectional evidence.

Suffix matching may be longest-first, but length alone is not a linguistic verdict.

### 25.7 Conservative one-letter stripping

One-letter prefixes and suffixes must not be removed merely because they appear in a static list.

The stripping operation requires:

```text
minimum viable host
compatible word-class path
compatible form or inflection geometry
no terminal closed-class match
no lexical-root conflict
```

This applies especially to:

```text
و ف ب ك ل س أ ت ي ن ه ك ي
```

### 25.8 Future `سـ` policy

Strip initial `سـ` as a future particle only when there is affirmative evidence that it precedes an imperfect form.

Required structure:

```text
optional conjunction
+ سَ
+ one of the licensed imperfect prefixes
+ viable imperfect host
```

The imperfect prefix set includes:

```text
أ ن ي ت
```

The rule must protect:

1. root-initial `س`;
2. nominal `س`;
3. the derivational `س` inside FORM X;
4. words whose remaining host is not a valid imperfect candidate.

Protected contrast:

```text
سَيَكْتُبُونَ
    سَ + يَكْتُبُونَ   -> future + FORM I imperfect

سَيَسْتَغْفِرُونَ
    سَ + يَ + اِسْتَـ + غ ف ر + ون
    only the first س is the future particle

سَأَلَ
    root-initial س; no future stripping

اِسْتَغْفَرَ
    س belongs to FORM X; no future stripping
```

A successful FORM X analysis obtained accidentally through rule order is not explicit protection.

### 25.9 Closed-class and terminal-boundary priority

Known closed functional items and terminal lexical items must be checked before root and form speculation.

A terminal boundary may produce:

```text
NOT_OPENED
NOT_APPLICABLE
DEFERRED with a typed reason
```

for later fields.

It must not be treated as a failed root candidate.

### 25.10 Tanwin as nominal evidence

Tanwin must be detected and recorded before it is removed from the morphology surface.

It is strong nominal evidence, but it does not by itself determine the nominal subclass.

Protected contrast:

```text
أَجَلٍ -> ISM
```

does not imply:

```text
أَجَلٍ -> ISM_FA3IL
```

The subclass still requires its own evidence.

### 25.11 Definite article as nominal evidence

A valid definite article is nominal evidence.

The article's sukun or lam must not be interpreted as an imperative or jussive marker.

Article handling must preserve the host and must respect the closed shadda contract for sun-letter assimilation.

### 25.12 Form alignment as typed evidence

Pattern alignment may map radical placeholders to surface letters:

```text
ف -> R1
ع -> R2
ل -> R3
```

and an explicitly licensed fourth radical slot for quadriliterals.

However:

- alignment is evidence, not an unrestricted root generator;
- the candidate pattern must already be licensed for the path;
- weak-root recovery requires separate evidence;
- a mismatch must defer or produce candidates rather than fabricate a root.

### 25.13 Weak-root recovery must be evidence-based

The old heuristic of inserting `و` by default into a hollow root is not golden law.

For hollow, defective, assimilated, or lafif roots, restoration requires one or more canonical evidence sources, such as:

```text
trusted audited root inventory
licensed paradigm relation
present/past contrast
masdar evidence
lexical contract
canonical weak-root rule with sufficient evidence
```

Without sufficient evidence, return a typed ambiguity or deferral.

Protected example:

```text
أَدَارَ -> يُدِيرُ
root = د و ر
```

must be licensed through the hollow FORM IV relation, not by treating surface `دير` as the final root.

### 25.14 External resources are comparison layers unless explicitly canonical

A corpus, lexicon, or external analyzer must not silently replace the Hokom verdict.

Its use must be declared as one of:

```text
CANONICAL_TRUSTED_INPUT
EVIDENCE_SOURCE
AUDIT_COMPARISON_ONLY
TEST_GOLD_ONLY
```

For the current project:

- `audited_roots.csv` is the canonical trusted root inventory according to its current contract;
- corpus hints such as `root_hint`, `lemma_hint`, or `ambiguity_expected` are not runtime seeds;
- external comparison resources may identify disagreements but may not auto-correct runtime output.

### 25.15 Word-class indicators are evidence, not absolute shortcuts

The following are active evidence classes:

Nominal evidence:

```text
definite article
tanwin
licensed prepositional government
vocative relation
nominal number and agreement geometry
```

Verbal evidence:

```text
future particle before a valid imperfect
لم / لن / لام الأمر before a valid imperfect
past subject suffix
feminine past suffix
imperative geometry
licensed imperfect prefix plus compatible host
```

Functional evidence:

```text
closed functional inventory
operator catalog
typed boundary owner
```

No single weak heuristic may overwrite stronger contradictory evidence or a terminal boundary.

### 25.16 Operator-driven mood rules currently used

The following operator relations are active where the context carrier proves their scope:

```text
أَنْ / أَلَّا -> SUBJUNCTIVE
لَمْ          -> JUSSIVE
لام الأمر     -> JUSSIVE
لا الناهية    -> JUSSIVE
إِنْ الشرطية  -> JUSSIVE in its licensed scope
```

`لا النافية` does not govern jussive.

The operator's identity, scope, and relation to the target verb must be typed evidence. Surface adjacency alone is insufficient for long or coordinated scope.

### 25.17 Lafz al-Jalalah is a singular lexical boundary and is mu'rab

The current Hokom contract supersedes the older statement that lafz al-Jalalah is “neither mabni nor mu'rab.”

Current rule:

```text
lafz al-Jalalah is mu'rab
it is not mabni
it is intercepted by JAMID_AALAM_BOUNDARY
it does not enter root, form, jamid/mushtaq, or verbal analysis
```

Its prefixed forms remain members of the same protected lexical boundary after canonical segmentation.

### 25.18 Data-driven catalogs, not runtime token exceptions

Reusable lexical inventories and operator inventories should be stored in canonical data contracts rather than as exact-token branches embedded in general runtime logic.

This does not permit using a corpus answer column as runtime evidence.

A data record must declare its ownership and evidence semantics.

### 25.19 Pause and recitation symbols are not linguistic runtime evidence

Qur'anic pause and recitation marks may be preserved for display and used for evaluation or comparison.

They must not become hidden ground truth that determines clause boundaries, word class, root, form, or semantic relations unless a future explicit constitutional phase grants that ownership.

---

## 26. Correct potential rules not yet active or not yet closed

The following rules are retained as **potential rules**. They are linguistically useful, but this document does not claim they are currently implemented, integrated, or owned by Hokom.

A potential rule must not be called by runtime code until a dedicated phase defines its typed contract.

### 26.1 Clause segmentation without pause-mark leakage

Potential contract:

```text
ClauseSegmenter is rule-based from linguistic evidence.
Qur'anic pause marks are evaluation/reference evidence only.
```

Needed before activation:

- clause-boundary owner;
- operator-scope integration;
- coordination behavior;
- quotation and parenthetical scope;
- tests with and without pause marks proving identical linguistic analysis.

### 26.2 Full nominal case and mark assignment

Potential rules include:

```text
singular nominative -> damma
dual nominative -> alif
dual accusative/genitive -> ya
sound masculine plural nominative -> waw
sound masculine plural accusative/genitive -> ya
sound feminine plural accusative -> kasra where licensed
jussive imperfect -> sukun or deletion according to paradigm
```

These require:

- a canonical i'rab owner;
- indeclinability and diptote contracts;
- five-verbs handling;
- defective and weak-ending behavior;
- visible versus estimated marks;
- construction-level government.

They must not be inferred solely from the final surface vowel.

### 26.3 Syntactic-role assignment

Potential roles:

```text
فاعل
نائب فاعل
مبتدأ
خبر
مفعول به
حال
تمييز
مضاف إليه
نعت
عطف
بدل
```

Activation requires a sentence-level dependency or relation owner and must not be implemented as nearest-neighbor guesses.

### 26.4 Subject agreement and word order

Potential rules include:

- canonical VSO subject relation;
- agreement differences between VSO and SVO;
- feminine agreement conditions;
- delayed-subject resolution;
- subject-versus-topic distinction.

The simplified statement “a preceding subject is always mubtada and the verb is its khabar” is not adopted as a universal rule.

### 26.5 Passive and نائب الفاعل syntax

Potential syntax rule:

```text
a licensed passive verb opens a نائب الفاعل relation
```

The passive verdict must first come from form-specific vocalic geometry. Syntax may consume it but must not invent it.

### 26.6 Kana, Inna, and Zann families

Potential operator families:

```text
كان وأخواتها
إن وأخواتها
ظن وأخواتها
```

Activation requires:

- canonical family inventories;
- scope;
- cancellation/suspension behavior;
- complement typing;
- case effects;
- ambiguity with lexical uses.

### 26.7 Conditional constructions

Potential expansion beyond currently used mood injection:

```text
condition operator
condition clause
response clause
two-verb jussive relation
non-jussive conditional operators
فاء جواب الشرط
```

The list of operators and their effects must come from the current official operator catalog, not stale counts or historical filenames.

### 26.8 Semantic meanings of particles

Potential semantic inventories include multiple meanings of:

```text
ب
ل
من
عن
على
في
ك
```

Such meanings require contextual licenses. A preposition surface must not select one meaning without evidence.

### 26.9 Tadmin

Potential principle:

```text
تضمين requires a relation between the overt verb and an implied meaning,
a contextual indicator, and no contradiction with the clause.
```

It must not be used as an unrestricted repair mechanism for unexpected government.

### 26.10 Anaphora and pronoun resolution

Potential evidence includes:

```text
gender
number
person
definiteness
syntactic accessibility
semantic compatibility
speech frame
```

The closest compatible noun is not automatically the antecedent.

### 26.11 Speech frame and quotation tracking

Potential scope:

```text
speaker
addressee
quoted clause
nested speech
reported speech
```

This requires sentence and discourse ownership and must not alter morphology.

### 26.12 Taqdim, takhir, exclusivity, warning, and other constructions

Potential construction families include:

```text
تقديم المعمول
تقديم الخبر
التحذير
الإغراء
الاختصاص
الاشتغال
التنازع
التفصيل بأما
القسم
التعجب
```

Each construction needs independent positive evidence and negative controls.

### 26.13 Living-root versus descriptive-root distinction

Potential distinction:

```text
descriptive/etymological root
productive living derivational root
```

This is promising but not active until the project defines:

- the owner;
- whether both roots can coexist;
- evidence thresholds;
- effects on derivatives;
- serialization and Taaqol slots.

### 26.14 Sun-letter and moon-letter phonology

Potential explicit phonological output may represent:

```text
written definite article
pronounced assimilation
sun/moon letter class
surface shadda evidence
```

It must preserve the written article and comply with the closed shadda contract.

It must not delete shadda from the canonical linguistic record merely to simplify comparison.

### 26.15 Hamzat al-wasl pronunciation restoration

Potential pronunciation rule may infer initial kasra or damma in licensed imperative paradigms.

It must not be activated from a single “third-letter vowel” heuristic without:

```text
word class
imperative evidence
paradigm
form family
root type
negative controls
```

Orthographic normalization and pronunciation reconstruction are separate owners.

### 26.16 Jamid versus mushtaq classification beyond closed contracts

Potential extension may classify lexical nouns and derivatives.

It must not equate:

```text
concrete noun = jamid
pattern-looking noun = mushtaq
```

The existing Hokom masdar and derivative owners remain authoritative for their closed scopes.

### 26.17 External authority-comparison reports

Potential audit workflow:

```text
Hokom analysis
-> compare with an external resource
-> classify disagreement
-> human or canonical adjudication
```

Useful disagreement classes include:

```text
root match / form mismatch
form match / root mismatch
segmentation disagreement
hamza-normalization disagreement
weak-root restoration disagreement
word-class disagreement
```

The external answer remains non-runtime unless separately promoted through governance.

---

## 27. Historical, unsafe, or rejected statements from `RULES.md`

The following must not be copied into active code or golden tests as written.

### 27.1 Historical paths and counts

Do not treat these as current truth:

- `clean_code/...` paths;
- historical line numbers;
- fixed counts such as 102 operators, 200+ closed items, or 243 semantic rules;
- references to old `wazn_matcher_v2/v3`, `i3rab_engine`, `samarrai_analyzer`, or earlier segmenter ownership.

They may be useful migration clues only.

### 27.2 Automatic deletion of shadda after the definite article

Rejected as a general rule:

```text
ال + sun letter + shadda -> delete shadda
```

A comparison key may normalize evidence, but the canonical record must preserve the closed shadda and assimilation information.

### 27.3 Automatic hamzat al-wasl reconstruction from the third letter alone

Rejected as a complete rule.

It may be one piece of evidence inside a licensed imperative paradigm, not a universal normalization operation.

### 27.4 Blind stripping of taa marbuta

Rejected:

```text
ة -> generic feminine suffix stripping
```

Taa marbuta is part of the surface host and may distinguish lexemes and patterns. Any morphological decomposition requires owner-specific evidence.

### 27.5 Default waw insertion for hollow roots

Rejected:

```text
surface alif in a hollow candidate -> insert و by default
```

The result may be waw or ya, and sometimes the candidate path itself is wrong.

### 27.6 “Every closed-class word is mabni”

Rejected as an unrestricted equation between inventory membership and grammatical building status.

Closed functional classification, mabni status, lexical boundaries, and i'rab behavior are separate typed claims.

### 27.7 Old lafz al-Jalalah status

Rejected:

```text
lafz al-Jalalah is neither mabni nor mu'rab
```

The current closed contract states that it is mu'rab and not mabni, while remaining protected by `JAMID_AALAM_BOUNDARY`.

### 27.8 “Everything that is not a noun or verb is a particle”

Rejected as an implementation rule.

Failure to prove noun or verb is not proof of particle. The result may be:

```text
DEFERRED
AMBIGUOUS
NOT_OPENED
terminal lexical boundary
```

### 27.9 Concrete-noun source as sufficient jamid proof

Rejected as a universal rule.

Concrete meaning, derivational productivity, etymological root, and canonical jamid classification are not identical claims.

### 27.10 External corpus as automatic runtime ground truth

Rejected.

A corpus may be canonical only for explicitly declared columns and scopes.

Historical annotations and hints must not become hidden runtime seeds.

### 27.11 Word-class determination from one sign alone

Rejected examples:

```text
starts with ت -> imperfect verb
ends with ان -> dual noun
starts with أَ -> FORM IV past
contains shadda -> FORM II
```

Each may contribute evidence but requires compatible geometry and negative controls.

### 27.12 Surface pipe strings as ambiguity

Rejected:

```text
person=2|3
gender=M|F
```

unless accompanied by structured correlated candidate bundles and a clear statement that the pipe fields are display summaries only.

### 27.13 Pause marks as clause truth

Rejected as runtime behavior.

Pause marks may not silently determine syntactic or semantic relations.

---

## 28. Promotion procedure for potential rules

To promote a rule from section 26 into the active golden sections:

1. Assign a unique phase ID.
2. Name the canonical owner.
3. Define typed inputs, outputs, states, and reasons.
4. Identify conflicts with existing closed contracts.
5. Provide positive, negative, ambiguous, and boundary cases.
6. Prohibit corpus-answer seeding and exact-token runtime exceptions.
7. Implement a live-path test.
8. Add the rule to the protected gold manifest where applicable.
9. Run the semantic regression firewall.
10. Run the full canonical macOS Python 3.12.4 suite.
11. Regenerate and verify artifacts.
12. Append the promoted rule with:
   - phase ID;
   - closure commit;
   - tests;
   - old and new document digests.

Until all steps pass:

```text
POTENTIAL_NOT_YET_OWNED != ACTIVE_GOLDEN_RULE
```

