# M2 — FULL SEMANTIC ADAPTER AUDIT
## HOKOM × TAAQOL-GPT Migration — Phase M2

**Document ID:** `M2-SEMANTIC-AUDIT`
**Gate:** M2 — EXACT EXISTING-IMPLEMENTATION SEMANTIC AUDIT
**Date:** 2026-08-01
**Status:** M2_COMPLETE
**Supersedes:** §8A audit (ALL_KEEP_AS_IS verdict revoked — see mandatory corrections below)

**APPROVED_TARGET_SHA:** `05c6668dfb95d9238cff5df1d8bc73d0664bccb3`
**HOKOM_HEAD:** `8e37b738ece7183818189146912cb14e3dce3a07`
**Python environment:** 3.10.12 (sandbox); 3.12+ required for vendor runtime

---

## 0. MANDATORY CORRECTIONS TO §8A

The prior §8A audit issued `PREVIOUS_IMPL_AUDIT_VERDICT = ALL_KEEP_AS_IS` with:
- VENDOR_BACKED_SYMBOLS = 0 (INCORRECT — actual: 76 import aliases)
- All 154 symbols classified as HOKOM_ONLY (INCORRECT — symbol count was 124 hokom-defined; vendor aliases not counted)
- Single verdict axis (KEEP_AS_IS) — INSUFFICIENT per M2 requirements

**Corrected counts (M2):**
- TOTAL_HOKOM_SYMBOLS: 200 (76 vendor_import_alias + 124 hokom-defined)
- VENDOR_IMPORTED_SYMBOLS: 76
- HOKOM_ONLY_SYMBOLS: 124
- VENDOR_CALL_SITES: 40

**Root cause of §8A error:** AST traversal searched `tree.body` for `FunctionDef`/`Assign` only, missing vendor imports nested inside `try/except` blocks. All vendor imports in Hokom adapters are guarded by `try: ... except ImportError: pass` for fail-closed operation on Python 3.10.

---

## 1. AUDIT SCOPE

**Files audited:** 12
- `e1_lexical_registry/ayat_al_dayn_registry.py` (E1)
- `weight_layer/registry_adapter.py` (E2)
- `weight_layer/preweight_chain_adapter.py` (E4B)
- `weight_layer/licensing_boundary_adapter.py` (E4C)
- `weight_layer/dal_only_adapter.py` (E5)
- `weight_layer/verbal_madlul_adapter.py` (E6)
- `weight_layer/formal_shape_adapter.py` (E7 — formal shape)
- `weight_layer/mufrad_semantic_slot_adapter.py` (E7 — mufrad slot)
- `weight_layer/maqam_context_adapter.py` (E8 — maqam context)
- `weight_layer/relation_candidate_adapter.py` (E8 — relation candidate)
- `pipeline/taaqol_integration/__init__.py` (INFRA)
- `weight_layer/__init__.py` (INFRA)

**Symbols audited:** 200 total
- 76 vendor_import_alias (imported from taaqqul_slot_geometry.*)
- 124 hokom-defined (functions, classes, constants, typed_constants)

---

## 2. TWO-AXIS CLASSIFICATION REQUIREMENT

Per M2 mandate, every adapter receives two verdicts:

**AXIS 1 — VERSION_MIGRATION_DISPOSITION**: Does this adapter require changes to work with APPROVED_TARGET_SHA vs PINNED_SHA?
- `NO_CHANGE_NEEDED` — adapter code unchanged; weight/ contracts identical
- `SHA_STAMP_UPDATE_ONLY` — only _VENDOR_SHA constant needs updating (in M3)

**AXIS 2 — IMPLEMENTATION_SEMANTIC_DISPOSITION**: How complete is the semantic implementation?
- `KEEP_COMPLETE` — fully implemented, no limitations
- `KEEP_PARTIAL` — vendor call chain implemented but with acknowledged limitations
- `KEEP_FAIL_CLOSED_GUARD` — only fail-closed guard; no real implementation path
- `REFACTOR_FOR_SEMANTICS` — implementation has incorrect semantics requiring refactor
- `REPLACE_WITH_NATIVE` — vendor impl should be replaced with native
- `MOVE_TO_LATER_PHASE` — implementation belongs in a later phase
- `DELETE_OBSOLETE` — no longer needed

---

## 3. PER-ADAPTER AUDIT

### E1 — `e1_lexical_registry/ayat_al_dayn_registry.py`
**Vendor imports (4):** `RegistryEntry`, `RegistryDomain`, `REGISTRY_RANK_CEILING` from `weight.registry_contract`; `Rank` from `core.rank_lattice`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`
`_VENDOR_SHA = "35381739..."` must be updated to `"05c6668d..."` in M3. All vendor symbols byte-identical.

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `build_ayat_al_dayn_registry()` constructs 74 corpus entries using typed `_RegistryEntry(_RegistryDomain(...), ...)` calls
- On Python 3.10: vendor absent → `_REGISTRY_CONTRACT_AVAILABLE = False` → `AYAT_AL_DAYN_REGISTRY = ()` (empty tuple; fail-closed)
- On Python 3.12+: all 74 entries built correctly; `REGISTRY_SIZE = BUILT_SIZE` expected

**Limitations:**
- Not tested on 3.12+ with real vendor (NATIVE_RUNTIME_EXECUTED = 0; M1 pending)
- BUILD_FAILURE_COUNT not yet verified as 0 on 3.12+

---

### E2 — `weight_layer/registry_adapter.py`
**Vendor imports (4):** `lookup_registry_entry`, `RegistryDomain`, `RegistryLookupState`, `RegistryEntry` from `weight.registry_contract`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `_lookup_registry_entry(candidate_key=surface, domain=domain, registry=registry_tuple)` called correctly
- FOUND path → typed list with `{slot_id, root, match_confidence, domain, rank, non_meaning_proof, trace_ref}`
- EMPTY path → `[]`
- Module invariant: `registry_matches is never None` (P2 fix present)
- `_RegistryDomain` enum used for domain conversion from word_class hint

**Limitations:**
- E1 registry wired at module load only; dynamic registry swap not supported
- `_RegistryLookupState.FOUND` enum comparison requires 3.12+ vendor to be non-None

---

### E4B — `weight_layer/preweight_chain_adapter.py`
**Vendor imports (14):** `LetterStanding`, `OperationTraceCandidate`, `OriginalExtraMap`, `PathCandidate`, `PathKind`, `PreWeightSurface`, `RootStemCandidate`, `SyllableCandidate`, `SyllableSequenceCandidate`, `WeightReadinessCandidate`, `WordBoundaryCandidate`, `WordCarrierCandidate` from `weight.pre_weight`; `Rank` from `core.rank_lattice`; `TraceRef` from `core.slot_graph`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `decompose_arabic(text)` — pure Python, 3.10-compatible, always available; extracts Arabic codepoints correctly
- `build_weight_readiness_candidate()` — full 8-stage µ-chain:
  - µ_seq → µ_boundary → µ_word_carrier → µ_path_gate → µ_root_stem → µ_original_extra → µ_ops → µ_weight_readiness
- `_MU_CHAIN_AVAILABLE = True` on 3.12+; `False` on 3.10 → returns None

**Limitations:**
- Root letters accepted as external parameter; not extracted from Arabic morphology internally
- µ-chain on 3.12+ not yet executed with real corpus tokens (NATIVE_RUNTIME_EXECUTED = 0)

---

### E4C — `weight_layer/licensing_boundary_adapter.py`
**Vendor imports (12):** `LicensingBoundaryVerdict`, `LicensingBoundaryState`, `LicenseBoundaryKind`, `BoundaryEvidence`, `assess_license` from `weight.licensing_boundary`; `WeightFitCandidate`, `weigh`, `WeightFitState` from `weight.weight_fit`; `WeightReadinessCandidate` from `weight.pre_weight`; `omega_governance`, `OmegaGovernanceState` from `weight.mu_chain`; `Rank` from `core.rank_lattice`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- Full A1 chain: `_omega_governance(residuals=(), Rank.CANDIDATE)` → `_weigh(weight_readiness, governance)` → `_BoundaryEvidence(LEXICAL, host, CANDIDATE, domain)` → `_assess_license(fit_candidate, evidence, governance)`
- `A1_IMPLEMENTATION_STATE = "E4C_ASSESS_LICENSE_CHAIN_IMPLEMENTED"` on 3.12+
- Guards: upstream BLOCK/DEFER → DEFERRED; HARF → BLOCKED_HARF_NOT_APPLICABLE; empty host → DEFERRED

**Limitations:**
- `root_letters=""` passed to E4B (root not available at E4A entry point); affects mu-chain root_stem stage quality
- Not yet executed on 3.12+ with real corpus tokens

---

### E5 — `weight_layer/dal_only_adapter.py`
**Vendor imports (5):** `DalBoundaryState`, `DalBoundaryVerdict`, `DalOnlyCandidate`, `prove_dal` from `weight.dal_only`; `LicensingBoundaryVerdict` from `weight.licensing_boundary`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `_prove_dal(prior_verdict=licensing_verdict, signifier_identity=token_surface, phonetic_trace_ref=trace_id, graphic_trace_ref=graphic_trace_ref)` — all 4 params correct
- Upstream BLOCK/FAIL → returns None (fail-closed propagation)

**Limitations:**
- `graphic_trace_ref` uses `token_surface` as placeholder (no actual graphic trace derivation from corpus)
- Fail-closed on 3.10; not yet run on 3.12+

---

### E6 — `weight_layer/verbal_madlul_adapter.py`
**Vendor imports (14):** `MadlulBoundaryState`, `VerbalMadlulBoundaryVerdict`, `VerbalMadlulCandidate`, `prove_verbal_madlul`, `BindingState`, `DalMadlulBindingVerdict`, `bind_dal_madlul` from respective weight modules; `RegistryDomain`, `RegistryEntry`, `RegistryLookupResult`, `RegistryLookupState`, `lookup_registry_entry` from `weight.registry_contract`; `DalOnlyCandidate` from `weight.dal_only`; `Rank` from `core.rank_lattice`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `_prove_verbal_madlul(prior_dal, wad_usage_boundary, correspondence_candidate, inclusion_candidate, iltizam_condition, existence_carrier_candidate, event_carrier_candidate, relation_affordance_candidate)` — all 8 params present
- `_bind_dal_madlul(dal_candidate, madlul_candidate, dal_registry, madlul_registry)` — both registry lookups performed
- Registry lookups: `_lookup_registry_entry` called separately for dal and madlul contexts

**Limitations:**
- `correspondence_candidate`, `inclusion_candidate`, `iltizam_condition`, `existence_carrier_candidate`, `event_carrier_candidate`, `relation_affordance_candidate` all deferred/empty at corpus layer (not yet derived from Ayat al-Dayn evidence)
- Fail-closed on 3.10

---

### E7a — `weight_layer/formal_shape_adapter.py`
**Vendor imports (5):** `FormalShapeClosureState`, `build_word_class_registry` from `weight.formal_shape`; `FormalStyleFamily`, `FormalStyleState`, `prove_formal_style_candidate` from `weight.formal_style_candidate`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `_build_word_class_registry()` called to populate `FormalShapeRegistry`
- `_prove_formal_style_candidate(style_family, composition_evidence_ref, formal_closure_state, formal_closure_ref)` — all 4 params
- `FormalStyleFamily` enum correctly derived from word_class for ISM/FI3L/HARF cases

**Limitations:**
- `style_family` mapping may not cover all word class edge cases (dual, broken plural morphology)
- `formal_closure_ref` uses static corpus reference paths

---

### E7b — `weight_layer/mufrad_semantic_slot_adapter.py`
**Vendor imports (10):** `ContractableUnitState`, `prove_contractable_unit` from `weight.contractable_unit_geometry`; `FormalShapeClosureState` from `weight.formal_shape`; `KulliJuziiAxis`, `MufradSemanticState`, `ParticularitySource`, `SemanticCategory`, `WadEvidenceType`, `WadOriginDomain`, `prove_mufrad_semantic_slot_geometry` from `weight.mufrad_semantic_slot_geometry`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `_prove_contractable_unit(binding_candidate, admissible_roles, blocked_roles, path_profile, word_class_affordance, inflection_affordance, derivational_affordance)` — all 7 params
- `_prove_mufrad_semantic_slot_geometry(...)` — all 28 params including wad_scope, branch fields, kulli_juzii_axis, particularity_source, predication_test_passed
- `KulliJuziiAxis`, `SemanticCategory`, `WadOriginDomain`, `WadEvidenceType`, `ParticularitySource` enums used correctly

**Limitations:**
- `naql_readiness='deferred-to-naql-gate'` — constitutionally valid deferral
- `majaz_readiness='deferred-to-majaz-gate'` — constitutionally valid deferral
- `reference_resolution_status='deferred-to-context'` — constitutionally valid deferral
- `predication_test_passed` value derivation from corpus evidence not yet implemented

---

### E8a — `weight_layer/maqam_context_adapter.py`
**Vendor imports (6):** `DiscourseDomainType`, `LiteralConstraintType`, `MaqamContextState`, `UsageRegisterType`, `WadScopeType`, `prove_maqam_context_boundary` from `weight.maqam_context_boundary`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `_prove_maqam_context_boundary(...)` — all 26 params supplied
- Defaults: `discourse_domain_type=LUGHAWI`, `usage_register_type=HAQIQI`, `literal_constraint_type=UNCONSTRAINED`, `wad_scope_type=ORIGINAL` — correct for corpus layer
- `DiscourseDomainType`, `UsageRegisterType`, `LiteralConstraintType`, `WadScopeType` enums instantiated correctly

**Limitations:**
- `has_potential_qarina=False` always (qarina detection not implemented at corpus layer)
- Fail-closed on 3.10

---

### E8b — `weight_layer/relation_candidate_adapter.py`
**Vendor imports (2):** `RelationState`, `prove_relation_candidate` from `weight.relation_candidate`

**VERSION_MIGRATION_DISPOSITION:** `SHA_STAMP_UPDATE_ONLY`

**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_PARTIAL`

**ADAPTER_CLASSIFICATION:** `KEEP_PARTIAL`

**Evidence:**
- `_prove_relation_candidate(governor, dependent, relation_basis, governor_role_claim, dependent_role_claim)` — all 5 params
- Default roles `MUBTADA`/`KHABAR` correct for ISM nominal sentences in Ayat al-Dayn corpus

**Limitations:**
- `governor_role_claim`, `dependent_role_claim` use corpus-layer defaults; advanced syntactic role derivation deferred
- Fail-closed on 3.10

---

### INFRA — `__init__.py` files (×2)
**VERSION_MIGRATION_DISPOSITION:** `NO_CHANGE_NEEDED`
**IMPLEMENTATION_SEMANTIC_DISPOSITION:** `KEEP_COMPLETE`
No vendor dependency. No adapter implementation. No limitations.

---

## 4. SYMBOL-LEVEL COUNTS (M2 CORRECTED)

| Metric | Value |
|---|---|
| TOTAL_HOKOM_SYMBOLS | 200 |
| HOKOM_ONLY_SYMBOLS | 124 |
| VENDOR_IMPORTED_SYMBOLS (aliases) | 76 |
| VENDOR_CALL_SITES | 40 |
| TYPED_ADAPTER_BOUNDARIES | 25 |
| SEMANTICALLY_VERIFIED_ADAPTERS | 0 (M1/M5 pending) |
| FAIL_CLOSED_ONLY_ADAPTERS | 0 (all 10 have real call chain on 3.12+) |
| PARTIALLY_IMPLEMENTED_ADAPTERS | 10 |
| NATIVE_RUNTIME_CLOSED_ADAPTERS | 0 (M1 blocked by Python 3.10 environment) |
| UNREVIEWED_SYMBOLS | 0 |
| SHA_STAMP_UPDATE_NEEDED | 10 (one _VENDOR_SHA per adapter file) |

Detailed symbol table: `05B_HOKOM_IMPL_SYMBOL_AUDIT.csv`
File inventory: `05A_HOKOM_IMPL_FILE_INVENTORY.csv`
Summary counts: `05C_HOKOM_IMPL_AUDIT_SUMMARY.csv`

---

## 5. OPEN LIMITATIONS BY ADAPTER

| Phase | Adapter | Limitation | Severity |
|---|---|---|---|
| E1 | ayat_al_dayn_registry | Build failure count unverified on 3.12+ | LOW — expected 0 |
| E2 | registry_adapter | Dynamic registry swap not supported | LOW — corpus layer is static |
| E4B | preweight_chain_adapter | Root letters not morphologically extracted | MEDIUM — passed as param |
| E4C | licensing_boundary_adapter | root_letters="" at E4A entry | MEDIUM — affects mu-chain root_stem |
| E5 | dal_only_adapter | graphic_trace_ref = token_surface placeholder | MEDIUM — no graphic trace derivation |
| E6 | verbal_madlul_adapter | 6 madlul sub-fields deferred/empty | MEDIUM — constitutional deferral valid |
| E7a | formal_shape_adapter | style_family mapping edge cases (dual/broken plural) | LOW — main word classes covered |
| E7b | mufrad_semantic_slot_adapter | naql/majaz/reference all deferred | LOW — constitutionally valid at E7 |
| E8a | maqam_context_adapter | has_potential_qarina always False | LOW — corpus layer correctness |
| E8b | relation_candidate_adapter | role_claim derivation from corpus defaults only | LOW — ISM defaults correct |

---

## 6. M2 VERDICT

```
M2_STATUS                      = COMPLETE
TOTAL_HOKOM_SYMBOLS            = 200
VENDOR_IMPORTED_SYMBOLS        = 76   (was incorrectly 0 in §8A)
HOKOM_ONLY_SYMBOLS             = 124  (was incorrectly 154 in §8A)
VENDOR_CALL_SITES              = 40
SHA_STAMP_UPDATE_NEEDED        = 10   (all adapter _VENDOR_SHA constants)
VERSION_MIGRATION_DISPOSITION  = SHA_STAMP_UPDATE_ONLY for all 10 adapters (no functional change)
IMPL_SEMANTIC_DISPOSITION      = KEEP_PARTIAL for all 10 adapters; KEEP_COMPLETE for 2 INFRA files
NATIVE_RUNTIME_CLOSED          = 0    (M1 execution required on Python 3.12+)
M3_PRECONDITION                = BLOCKED_ON_M1 (vendor update only after reference suite passes)
```

All adapter call signatures match vendor function definitions as verified against APPROVED_TARGET_SHA.
All vendor contracts byte-identical between PINNED_SHA and APPROVED_TARGET_SHA for all Hokom-used modules.

---

*M3 proceeds after M1 (REFERENCE_FAILED=0, REFERENCE_VENDOR_TESTS_EXECUTED>0, COLLECTION_EXIT=0)*
