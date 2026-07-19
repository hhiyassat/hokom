# Word Class Gap Matrix
## HOKOM-WORD-CLASS-OWNERSHIP-AUDIT-01
**HEAD**: 3cd85cf | **Date**: 2026-07-19

Legend: PRESENT / PARTIAL / ABSENT

---

## Gap Matrix — 17 Capabilities

| # | Capability | Status | Evidence | Gap Description |
|---|---|---|---|---|
| 1 | Top-level ISM/FI3L/HARF | ABSENT | No module produces ISM/FI3L/HARF for any token | No canonical three-way classifier exists anywhere in pipeline/ |
| 2 | Lexical subclass | PARTIAL | P5 lexical produces 6 mabni subclasses; p6_derivatives has ISM_FA3IL etc. | Mabni subclasses work; derivative subtypes are not projected to top-level ISM |
| 3 | Operator/non-operator separation | PRESENT | `MabniEntry.is_operator`, `_lexical_class()` in mabni_projection.py | Operators (OPERATOR_BOUNDARY) vs. Bound Nominal (MABNI_BOUNDARY) are correctly separated |
| 4 | Mabni independence | PARTIAL | `lexical_class` in `MabniBoundary` is independent of grammatical function | Mabni lexical class is set correctly; but mabni tokens are not labelled ISM/FI3L/HARF |
| 5 | Verbhood evidence | PARTIAL | `morphology_path=verbal_root_path` for يَكْتُبُ; `morphology_path=ambiguous` for كَتَبَ | Imperfect verb evidence works; past tense surface without taa of feminization is ambiguous, not verbal |
| 6 | Masdar→ISM projection | ABSENT | كِتَابَةٌ gets morph_path=nominal but no word_class=ISM | Masdar engine identifies masdar type but no ISM label is propagated upward |
| 7 | Derivative→ISM projection | ABSENT | كَاتِبٌ has form_family=FA3IL_PARTICIPLE but no ISM label | Derivative engine identifies derivative type; no ISM projection to top level |
| 8 | Tense-based verb subclass | PARTIAL | InflectionalForm.tense_aspect works for يَكْتُبُ (IMPERFECT) | Missing mabni guard: tense/mood/voice are assigned to operators (هَلْ=PAST is a bug) |
| 9 | Ambiguous surface handling | PARTIAL | `ambiguous_morphology_path` exists; residuals generated | No resolution engine exists; ambiguous tokens stay ambiguous without upgrade path |
| 10 | Serialization | PARTIAL | InflectionOwnershipGate.SERIALIZATION_ROUNDTRIP=PASS; mabni serializable | No word-class field in hokom() return dict; no round-trip contract for ISM/FI3L/HARF |
| 11 | Deterministic ordering | PARTIAL | InflectionOwnershipGate.DETERMINISM=VERIFIED for inflection | Word class itself has no determinism contract; multiple shadow classifiers can disagree |
| 12 | Residual governance | PARTIAL | residual_codes governed for masdar/derivative/inflection | No residual_codes defined for word-class failures (e.g., WORD_CLASS_AMBIGUOUS, WORD_CLASS_GAP) |
| 13 | Canonical entrypoint | ABSENT | No single function accepts a surface and returns a word-class verdict | Four separate subsystems each return partial information; no synthesis layer exists |
| 14 | Ownership gate | ABSENT | No WordClassOwnershipGate dataclass or equivalent exists | InflectionOwnershipGate exists for inflection; no analogue for word class |
| 15 | Pipeline integration | PARTIAL | hokom() collects mabni.lexical_class, pre_root.morphology_path, phase5_result | hokom() return dict has no top-level `word_class` key; consumers must synthesize from 4 fields |
| 16 | Demo display | PARTIAL | hokom_pipeline.py prints lexical_class for mabni tokens | Morphologically-open tokens display no word class; demo JSONL has P5_lexical_class but no ISM/FI3L/HARF |
| 17 | Taaqol handoff readiness | ABSENT | HokomLinguisticClaimBundle has lexical_class/part_of_speech fields | lexical_class=morphology_path string (semantic mismatch); part_of_speech always None; ISM/FI3L/HARF not provided |

---

## Critical Bugs Found

### Bug B-01: Inflection engine runs on OPERATOR_BOUNDARY tokens
**Severity**: HIGH  
**File**: `hokom_pipeline.py` (line ~350), `pipeline/p5_inflection/phase5_orchestrator.py`  
**Observed**: هَلْ→VERB/PAST, مِنْ→VERB/PAST, كَمْ→VERB/PAST  
**Root cause**: `project_inflection_with_licensing()` is called unconditionally; the morphology_path guard (`VERBAL_PATHS`/`NON_VERBAL_PATHS`) only applies when `morphology_path` is not None, but for mabni-boundary tokens `pre_root=None` so `morphology_path=None`, bypassing the guard.  
**Impact**: False VERB classifications in hokom() return dict and Taaqol claim bundle for all closed function words.

### Bug B-02: Taaqol claim adapter ignores P5 lexical_class
**Severity**: MEDIUM  
**File**: `pipeline/taaqol_integration/claim_adapter.py`  
**Observed**: `bundle_from_hokom_result()` sets `lexical_class` from `pre_root.morphology_path.value`, ignoring the `mabni.lexical_class` field from P5 lexical layer.  
**Impact**: Mabni tokens (هَلْ, مِنْ, etc.) have `lexical_class=None` in the Taaqol claim bundle even though their correct lexical class is known.

### Bug B-03: HokomLinguisticClaimBundle.part_of_speech always None
**Severity**: MEDIUM  
**File**: `pipeline/taaqol_integration/claim_adapter.py`  
**Root cause**: Code reads `pre_root.pos` but `PreRootDecision` has no `.pos` attribute — the field simply does not exist.  
**Impact**: `part_of_speech` is always None in every Taaqol claim bundle.

### Bug B-04: هُوَ and هَذَا classified as MORPHOLOGICALLY_OPEN
**Severity**: MEDIUM  
**Observed**: هُوَ → verdict=OPEN, lexical_class=None; هَذَا → verdict=OPEN  
**Root cause**: Pronouns and demonstratives may not be fully represented in the operators catalog with matching vocalization.  
**Impact**: Pronouns treated as morphologically analyzable words rather than closed mabni tokens.

---

## Coverage by Token Class

| Token class | ISM/FI3L/HARF | lexical_class | morph_path | part_of_speech | Notes |
|---|---|---|---|---|---|
| Closed function words (حروف) | ABSENT | PRESENT (via mabni) | None | BUG: VERB | هَلْ, مِنْ |
| Numerical operators | ABSENT | PRESENT (via mabni) | None | BUG: VERB | كَمْ, كَذَا |
| Verbal operators | ABSENT | PRESENT (via mabni) | None | N/A | كَانَ |
| Pronouns/demonstratives | ABSENT | ABSENT | None | BUG: VERB | هُوَ, هَذَا not in catalog |
| Past tense verbs | ABSENT | None | ambiguous | VERB (correct) | كَتَبَ |
| Imperfect verbs | ABSENT | None | verbal_root_path | VERB (correct) | يَكْتُبُ |
| Imperatives | ABSENT | None | N/A (BLOCK) | VERB (correct but BLOCKED) | اُكْتُبْ |
| FA3IL participles | ABSENT | None | nominal | None | كَاتِبٌ |
| MAF3UL participles | ABSENT | None | nominal | None | مَكْتُوبٌ |
| Triliteral nouns | ABSENT | None | nominal | None | مَجْلِسٌ, مَضْرِبٌ |
| Masdars | ABSENT | None | nominal | None | كِتَابَةٌ |
| Pattern nouns (FI3L) | ABSENT | None | nominal | None | كِتَابٌ |
