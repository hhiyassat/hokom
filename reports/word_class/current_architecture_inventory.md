# Current Architecture Inventory — Word Class
## HOKOM-WORD-CLASS-OWNERSHIP-AUDIT-01
**HEAD**: 3cd85cfba6b85f45bbf6431c1a37cf3cb606bdf3  
**Date**: 2026-07-19  
**Audit status**: READ-ONLY — no production code was modified

---

## 1. Summary

Hokom has **no canonical ISM/FI3L/HARF word-class engine**.  
Word-class-related information is scattered across four independent subsystems that each produce partial, incompatible labels. This is **CASE C: WORD_CLASS_SHADOW_ONLY**.

---

## 2. Layer Map

### Layer A — P5 Lexical (Mabni/Operator Boundary)
**File**: `pipeline/p5_lexical/mabni_projection.py`  
**Entry**: `process_mabni(input_surface, normalized_surface, slots, slot_verdict, violations)`  
**Output type**: `MabniBoundary | MabniOpen | MabniBlocked`

The only layer that produces a `lexical_class` field. Applies exclusively to mabni / operator tokens.

| lexical_class value | Groups | Example |
|---|---|---|
| `Closed Function Word` | 1–7, 9 | مِنْ، فِي، هَلْ |
| `Numerical Operator` | 8 | كَمْ، كَذَا |
| `Verbal Operator` | 10–12 | كَانَ، عَسَى، نِعْمَ |
| `Phrase Operator` | 10–12 (multi-word) | مَا زَالَ |
| `Cognition Verb` | 13 | ظَنَّ، حَسِبَ |
| `Bound Nominal` | any, is_operator=False | ضمائر |

For `MabniOpen` (not in catalog) → `lexical_class = None`.  
For `MabniBlocked` → `lexical_class = None`.

**Coverage**: mabni/operator tokens only. All morphologically open tokens get `lexical_class=None`.

---

### Layer B — Pre-Root MorphologyPath
**File**: `pipeline/pre_root/morphology_path.py`  
**Entry**: `classify_morphology_path(host_surface, boundary_kind, phones=None)`  
**Output type**: `MorphologyPath` (Enum)

| MorphologyPath value | Interpretation | Example |
|---|---|---|
| `verbal_root_path` | Clear verbal evidence | يَكْتُبُ |
| `nominal_morphology_path` | Clear nominal evidence | كَاتِبٌ، مَجْلِسٌ |
| `derived_nominal_path` | Derived nominal (defined but not assigned in trace) | — |
| `functional_path` | Operator/function word from boundary | — |
| `ambiguous_morphology_path` | Cannot determine from structure | كَتَبَ |
| `no_morphology_path` | Invalid/empty | — |

This is a **structural heuristic classifier**, not an ISM/FI3L/HARF engine. It gates downstream analysis but does not produce a canonical word-class label.

**Coverage**: morphologically-open tokens only (MabniOpen path). Null for mabni-boundary tokens.

---

### Layer C — P5 Inflection part_of_speech
**File**: `pipeline/p5_inflection/models.py`, `phase5_orchestrator.py`  
**Entry**: `project_inflection_with_licensing(surface, root, ...)`  
**Output field**: `InflectionalForm.part_of_speech`

| value | meaning |
|---|---|
| `VERB` | Finite or imperative verb form |
| `VERBAL_NOUN` | Verbal noun (masdar) |
| `PARTICIPLE` | Participle form |

**Critical bug detected**: The inflection engine runs unconditionally after P5, including on `OPERATOR_BOUNDARY` tokens. Live trace shows:
- هَلْ → inf_pos=VERB, tense=PAST (incorrect — هَلْ is a question particle)
- مِنْ → inf_pos=VERB, tense=PAST (incorrect — مِنْ is a preposition)
- كَمْ → inf_pos=VERB, tense=PAST (incorrect — كَمْ is a numerical operator)
- كَذَا → inf_pos=VERB, tense=DU/PAST (incorrect)

The inflection engine lacks a mabni-boundary guard, producing false VERB classifications for all closed function words.

**Coverage**: all tokens that reach this stage, including mabni-boundary tokens (incorrectly).

---

### Layer D — Taaqol Claim Adapter (lexical_class field)
**File**: `pipeline/taaqol_integration/claim_adapter.py`  
**Entry**: `bundle_from_hokom_result(result, token_id)`  
**Output field**: `HokomLinguisticClaimBundle.lexical_class`

The adapter sets `lexical_class` from `pre_root.morphology_path.value` (a string like `"nominal_morphology_path"`). This is **not** an ISM/FI3L/HARF classification — it is the raw morphology path string repurposed as a lexical class label.

The adapter also has a `part_of_speech` field populated from `pre_root.pos` (but `PreRootDecision` has no `.pos` attribute in the current code — the field always resolves to `None` in practice).

**Coverage**: only tokens with a `pre_root` result (morphologically open tokens). Mabni-boundary tokens get `lexical_class=None` in the bundle even though P5 lexical has a valid `lexical_class`.

---

## 3. Data Sources

| File | Role | Entries |
|---|---|---|
| `data/operators_catalog_split_vocalized_corrected.csv` | Operators/mabni catalog (primary) | ~150 operators |
| `data/02_mabniyat/*.csv` | Extended mabni catalog (pronouns, demonstratives…) | loaded from dir |
| `pipeline/p5_lexical/operator_projection.py` | operator_id / lexical_family map | 90+ entries |
| `data/boundary/closed_function_words.json` | Boundary service word catalog | separate from mabni |
| `data/mushtaqat/mushtaq_catalog.json` | Derivative type catalog | ISM_FA3IL, ISM_MAF3UL, etc. |
| `data/masdar/masdar_catalog.json` | Masdar catalog | MASDAR_ASLI, ISM_MASDAR, etc. |

---

## 4. Key Missing Items

1. **No ISM/FI3L/HARF engine** — no module anywhere in `pipeline/` produces a top-level three-way word-class verdict for all tokens.
2. **هُوَ and هَذَا are OPEN** — pronouns and demonstratives that should be lexically classified are missing from the operators catalog or are not producing a lexical class.
3. **Inflection engine runs on closed function words** — false VERB classifications for all `OPERATOR_BOUNDARY` tokens.
4. **Masdar not projected to ISM** — `كِتَابَةٌ` has `morph_path=nominal_morphology_path` but no word-class label.
5. **Derivatives not projected to ISM** — `كَاتِبٌ` has `form_family=FA3IL_PARTICIPLE` and `wazn=FA3IL` but no word-class label.
6. **Taaqol claim bundle** mixes morphology-path value with lexical class, creating a semantic mismatch.

---

## 5. Files Inventoried

| File | Contains word-class-related code |
|---|---|
| `pipeline/p5_lexical/mabni_projection.py` | `lexical_class`, `_lexical_class()`, `MabniBoundary` |
| `pipeline/p5_lexical/mabni_inventory.py` | `MabniEntry.is_operator`, catalog loader |
| `pipeline/p5_lexical/operator_projection.py` | `OperatorProfile`, `operator_id`, `lexical_family` |
| `pipeline/pre_root/morphology_path.py` | `MorphologyPath` enum, `classify_morphology_path()` |
| `pipeline/pre_root/pre_root_decision.py` | `PreRootDecision.morphology_path` |
| `pipeline/p5_inflection/models.py` | `InflectionalForm.part_of_speech`, `InflectionOwnershipGate` |
| `pipeline/p5_inflection/phase5_orchestrator.py` | `project_inflection_with_licensing()`, `VERBAL_PATHS` |
| `pipeline/taaqol_integration/provider_models.py` | `HokomLinguisticClaimBundle.lexical_class`, `.part_of_speech` |
| `pipeline/taaqol_integration/claim_adapter.py` | `bundle_from_hokom_result()`, lexical_class extraction |
| `hokom_pipeline.py` | orchestrates all layers, no word-class synthesis |
| `pipeline/p2_augmented/models.py` | `FA3IL_PARTICIPLE` form_family constant |
| `pipeline/p5_masdar/models.py` | `NON_VERBAL_ORIGIN` residual code |
| `pipeline/p6_derivatives/models.py` | `NON_VERBAL_ORIGIN`, derivative type constants |

---

## 6. Taaqol Vendor Status

`vendor/Taaqol-GPT` contains a full ISM/FI3L/HARF engine via `WordKindCandidate` with:
- `WordKindCandidate.ISM`, `WordKindCandidate.FI3L`, `WordKindCandidate.HARF`
- `word_class_closure_ref="word_class/ISM/closed"` references in tests
- `test_formal_shape_word_class.py` — full constitutional test suite for word class shapes

This vendor code is **NOT imported or activated** by Hokom. Python 3.10 vs 3.11+ incompatibility blocks strict-mode import.

**TAAQOL_STATUS**: NOT_STARTED (integration not yet activated).
