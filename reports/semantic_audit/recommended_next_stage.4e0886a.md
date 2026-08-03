# Recommended Next Stage

## Basis for Recommendation

The largest defect cluster by token count is VERB_PREFIX_NOT_STRIPPED_QUADRILITERAL (13 tokens of E-class FALSE_DEFER for root extraction) combined with GEMINATE_COUNTED_TWICE (4 tokens) and PATTERN_EXTENSION_COUNTED_AS_RADICAL (14 tokens). Together these three clusters account for 31 tokens and share the same root cause: the consonant counter in pre_root and root_candidate does not correctly strip inflectional and pattern elements before counting root consonants.

However, the highest-severity single cluster is CVV_PLUS_V_PLURAL_VERB_BLOCK (10 FALSE_BLOCK tokens including overlaps) because BLOCK completely prevents downstream processing, while FALSE_DEFER only prevents root extraction with word_class potentially still assigned.

The recommended next stage targets the FALSE_BLOCK defects first because:
1. They are the most severe (complete processing failure, not just root deferral)
2. They have a single concentrated owner (slot_engine P3)
3. Fixing two slot patterns (CVV+V and +V) unlocks 10 tokens in one implementation point

---

STAGE_NAME: HOKOM-SLOT-ENGINE-PLURAL-VERB-UNLOCK-01

CANONICAL_OWNER: slot_engine (P3 Cell Construction / slot licensing table)

AFFECTED_TOKENS: 10
  آمَنُوا[003], فَاكْتُبُوهُ[010], وَاسْتَشْهِدُوا[052], وَامْرَأَتَانِ[061],
  دُعُوا[077], تَسْأَمُوا[079], تَرْتَابُوا[095], وَأَشْهِدُوا[108],
  تَفْعَلُوا[117], وَاتَّقُوا[121]

DEFECT_TYPE: IMPLEMENTATION_GAP (slot pattern licensing)

DEFECT_SUBCLUSTERS:
  1. CVV+V_PLURAL_VERB_BLOCK: 6 pure tokens (003,077,079,095,108,117)
     Cause: واو الجماعة suffix -ُوا produces slot CVV+V which is not in the licensed set
  2. HAMZAT_AL_WASL_PLUS_V_BLOCK: 4 tokens (010,052,061,121)
     Cause: hamzat al-wasl after proclitic stripping produces +V initial slot which is not licensed
     Note: tokens 010,052,121 have BOTH defects; 061 has only +V defect

CONTRACTS_TO_ADD:
  - Slot pattern CVV+V must be licensed for word-final position (واو الجماعة context)
  - Slot pattern +V must be licensed for word-initial position (hamzat al-wasl context)
  - The hamzat al-wasl marker from the segmenter must be propagated to the slot engine

FILES_TO_MODIFY:
  - The slot pattern licensing table (likely in hokom_pipeline.py or a slot_patterns.* config file)
  - The P3 Cell Construction module that validates slot patterns
  - Possibly the segmenter output contract to include a hamzat_al_wasl=True flag on affected hosts

REGRESSION_RISK: LOW
  - Adding new licensed patterns does not break existing ACCEPT tokens
  - All 10 currently-BLOCKED tokens are identical corpus forms (no edge cases in existing passing tokens)
  - CVV+V is structurally distinct from currently-passing patterns (no false-positive risk)
  - Regression suite should add positive tests for all 10 tokens and negative tests ensuring truly malformed patterns still BLOCK

CLOSURE_CRITERIA:
  1. All 10 currently-BLOCKED tokens must return verdict=ACCEPT after the fix
  2. Word class assignment must proceed for all 10 tokens (no WORD_CLASS_BLOCKED)
  3. The 6 pure CVV+V tokens (آمَنُوا, دُعُوا, تَسْأَمُوا, تَرْتَابُوا, وَأَشْهِدُوا, تَفْعَلُوا) must produce FI3L word_class
  4. وَامْرَأَتَانِ[061] must produce ISM word_class (it is a noun, not a verb)
  5. Root extraction may still be deferred (quadriliteral issue is a separate cluster), but must not be BLOCKED
  6. No currently-passing tokens may regress to BLOCK
  7. Regression suite run twice with identical results (reproducibility gate)

OUT_OF_SCOPE:
  - Root extraction for the 10 tokens (separate cluster: VERB_PREFIX_NOT_STRIPPED_QUADRILITERAL)
  - Word class disambiguation for ambiguous patterns (separate stage)
  - لفظ الجلالة protection (ALLAH_UNPROTECTED cluster — separate catalog stage)
  - Taaqol integration (blocked by Python version constraint)
  - Any changes to the mabni catalog, operator catalog, or governance files
  - Dual suffix stripping (شَهِيدَيْنِ, رَجُلَيْنِ — separate LEGITIMATE_DEFER tokens)

SECONDARY_RECOMMENDATION (follow-on stage):
  After slot engine unlock, the next highest-impact stage is:
  HOKOM-PRE-ROOT-VERB-PREFIX-STRIPPING-01 targeting the 13-token VERB_PREFIX_NOT_STRIPPED cluster.
  This would use the unlocked tokens as input and would enable root extraction for all imperfect verb forms.
