# 13 — STAGE ACCEPTANCE GATES

**Document ID:** `R0-13-GATES`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY  
**Amendment:** CONSTITUTIONAL_RECONCILIATION_01 applied 2026-08-01

---

## Gate Format

Each gate is a boolean condition. A phase is CLOSED only when ALL its gates = 1. A phase certificate must enumerate every gate with its value.

---

## R0 Closure Gates (13 conditions)

| Gate ID | Condition | Current |
|---|---|---|
| G_R0_01 | All 17 requirements files exist in `requirements/ayat_al_dayn_integration/` | 1 (at R0 close) |
| G_R0_02 | `01_CANONICAL_CORPUS_MANIFEST.json` total_unique_tokens = 129 | 1 |
| G_R0_03 | `03_TAAQOL_RUNTIME_INVENTORY.csv` covers all weight/ + gpt/ + audit/ files | 1 |
| G_R0_04 | `05_P2_REGISTRY_CONTRACT.md` documents exact blocker root cause with file+line | 1 |
| G_R0_05 | `08_HOKOM_TAAQOL_ADAPTER_MATRIX.csv` covers all type mismatches | 1 |
| G_R0_06 | `10_FAILURE_AND_RESIDUAL_TAXONOMY.md` documents all active blockers | 1 |
| G_R0_07 | `11_PROVENANCE_AND_VERSIONING_POLICY.md` documents VENDOR_SHA + trace_id policy | 1 |
| G_R0_08 | `14_IMPLEMENTATION_DEPENDENCY_GRAPH.md` documents E0→E15 dependencies | 1 |
| G_R0_09 | All OWNER_DECISION_REQUIRED items listed in `16_REQUIREMENTS_READINESS_REPORT.md` | 1 |
| G_R0_10 | VENDOR_SHA = `35381739410071ac21dd96702ecbb2acb493f90d` confirmed in corpus CSV | 1 |
| G_R0_11 | No implementation code written before R0 CLOSED | 1 |
| G_R0_12 | `04_VENDOR_MAIN_PARITY_REPORT.md` states PARITY_VERDICT explicitly (NOT_PROVEN is valid) | 1 |
| G_R0_13 | Phase closure certificate `R0_REQUIREMENTS_READINESS.json` emitted with canonical_exit=0 | 1 (emitted) |

---

## E0 Closure Gates — TARGET BASELINE FREEZE

**CONSTITUTIONAL_RECONCILIATION_01:** E0 = SHAs + source-derived ordering. No implementation gates.
Old gates G_E0_01–G_E0_12 (implementation-based) are reclassified to E1/E2/E4.

| Gate ID | Condition |
|---|---|
| G_E0_01 | VENDOR_SHA = `35381739410071ac21dd96702ecbb2acb493f90d` confirmed and pinned in all artifacts |
| G_E0_02 | HOKOM_HEAD = `8e37b738ece7183818189146912cb14e3dce3a07` confirmed |
| G_E0_03 | Corpus SHA = `6bd635a05530965f13f76cf003f7738130badec6981bcb0e73f2465d386e1ed7` confirmed; corpus_size = 129 |
| G_E0_04 | All vendor public API signatures inventoried (`03_TAAQOL_RUNTIME_INVENTORY.csv` complete) |
| G_E0_05 | Frozen file list established — adapter stub files created (no lexical/semantic content) |
| G_E0_06 | Source-derived dependency ordering documented (`SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01.md`) |
| G_E0_07 | E0 phase closure certificate emitted (`E0_BASELINE_FREEZE.json`) |

**Reclassified items (NOT E0 gates):**
- `registry_matches` non-None → G_E2_02 (E2)
- P2→P3 cascade → G_E2_03 (E2)
- A1_LICENSING_BOUNDARY interface → G_E4A_01–G_E4A_06 (E4A)
- LicensingBoundaryVerdict produced → G_E4C_05 (E4C)
- T00/T26/T27 registry schema tests → G_E1_01–G_E1_07 (E1)
- FAIL-CLOSED registry → G_E1_07 (E1)
- No lexical content in E0 → G_E0_05 (confirmed: AYAT_AL_DAYN_REGISTRY=() in stub)
- MaqamContextBoundary → G_E7_04 (E7)

---

## E1 Closure Gates — AYAT-AL-DAYN CANONICAL LEXICAL REGISTRY

| Gate ID | Condition |
|---|---|
| G_E1_01 | `REGISTRY_SIZE = 74` (unique ISM/FI3L host surfaces from 129-token corpus) |
| G_E1_02 | All entries have `non_meaning_proof` non-empty and structural only (no semantic meaning) |
| G_E1_03 | All entries have `domain = DAL_ONLY` |
| G_E1_04 | All entries have `rank = CANDIDATE` (no promotion above ceiling) on Python 3.12+ |
| G_E1_05 | HARF tokens (21) absent from registry — HARF is not in DAL_ONLY domain |
| G_E1_06 | `AYAT_AL_DAYN_REGISTRY` accessible as `tuple` (74 entries on 3.12+, 0 on 3.10 fail-closed) |
| G_E1_07 | `BUILD_FAILURES = []` on Python 3.12+ — zero construction errors |
| G_E1_08 | `CORPUS_SHA` embedded in registry module constant |
| G_E1_09 | E1 phase closure certificate emitted |

---

## E2 Closure Gates — P2 REGISTRY PROJECTION

| Gate ID | Condition |
|---|---|
| G_E2_01 | `registry_adapter.py` imports `AYAT_AL_DAYN_REGISTRY` from `e1_lexical_registry.ayat_al_dayn_registry` |
| G_E2_02 | T03_P2_BLOCKER_DEACTIVATED passes — `registry_matches` non-None for all corpus tokens |
| G_E2_03 | T04_P2_TO_P3_CASCADE passes — P3 stage opens after E2 registry wired |
| G_E2_04 | FOUND / REFUSED / DEFERRED / IMPORT_FAILURE states all tested |
| G_E2_05 | E2 phase closure certificate emitted |

---

## E3 Closure Gates — HOKOM P3/P4/P5 CONTINUITY

| Gate ID | Condition |
|---|---|
| G_E3_01 | Actual P2→P3 flow traced on Python 3.12+ (no mocked inputs) |
| G_E3_02 | All real P3 blockers identified and documented |
| G_E3_03 | P4/P5 outputs reach the Taaqol adapter boundary without exception |
| G_E3_04 | E3 phase closure certificate emitted |

---

## E4 Closure Gates — LICENSING BOUNDARY INTEGRATION (E4A / E4B / E4C)

### E4A — Precondition Guard (CLOSED per CONSTITUTIONAL_RECONCILIATION_01)

| Gate ID | Condition |
|---|---|
| G_E4A_01 | `build_licensing_boundary_verdict()` defined with correct signature |
| G_E4A_02 | HARF guard: always `BLOCKED_HARF_NOT_APPLICABLE` (vendor-independent) |
| G_E4A_03 | Upstream BLOCK/DEFER guard: always `DEFERRED` (vendor-independent) |
| G_E4A_04 | Empty segment_host guard: `DEFERRED` (vendor-independent) |
| G_E4A_05 | FAIL-CLOSED: vendor ImportError → `IMPORT_FAILURE` (not ELIGIBLE) |
| G_E4A_06 | Structural guards fire BEFORE vendor import check (guard ordering enforced) |

**E4A STATUS: CLOSED** — all gates satisfied by `licensing_boundary_adapter.py`.

### E4B — Pre-Weight Typed Carriers

| Gate ID | Condition |
|---|---|
| G_E4B_01 | Arabic diacritical text decomposed to `(letter, haraka)` pairs (pure Python stdlib) |
| G_E4B_02 | `SyllableCandidate(units=tuple[tuple[str,str],...])` built from pairs |
| G_E4B_03 | All 8 μ-stages executed in order: μ_seq → μ_boundary → μ_word_carrier → μ_path_gate → μ_root_stem → μ_original_extra → μ_ops → μ_weight_readiness |
| G_E4B_04 | `WeightReadinessCandidate` produced (type-enforced via `__post_init__`) |
| G_E4B_05 | No stage skipped — each output type verified at birth |
| G_E4B_06 | Verified on Python 3.12+ |

### E4C — Native Licensing Boundary

| Gate ID | Condition |
|---|---|
| G_E4C_01 | `WeightFitCandidate` built with `source=WeightReadinessCandidate` (type-enforced) |
| G_E4C_02 | `omega_governance(residuals, rank)` → `ResidualGovernanceVerdict(state=GRANTED)` |
| G_E4C_03 | `BoundaryEvidence(kind=LEXICAL, attestation=segment_host, ...)` constructed |
| G_E4C_04 | `assess_license(candidate, evidence, governance)` → `LicensingBoundaryResult(state=ELIGIBLE)` |
| G_E4C_05 | `LicensingBoundaryVerdict` produced for ISM/FI3L corpus tokens |
| G_E4C_06 | HARF tokens produce `BLOCKED_HARF_NOT_APPLICABLE` (not ELIGIBLE) |
| G_E4C_07 | E4 phase closure certificate emitted |

---

## E5 Closure Gates — DAL-ONLY CHAIN

| Gate ID | Condition |
|---|---|
| G_E5_01 | `prove_dal(LicensingBoundaryVerdict)` → `DalOnlyCandidate` for ISM/FI3L tokens |
| G_E5_02 | Full corpus run: 73 LICENSED tokens produce `DalOnlyCandidate` |
| G_E5_03 | 8 PIPELINE_DEFER tokens remain DEFERRED |
| G_E5_04 | `DalOnlyCandidate` carries `trace_ref` from live `PipelineTrace` |
| G_E5_05 | VENDOR_SHA embedded in all `DalOnlyCandidate` artifacts |
| G_E5_06 | E5 phase closure certificate emitted |

---

## E6 Closure Gates — VERBAL MADLUL

| Gate ID | Condition |
|---|---|
| G_E6_01 | T07_VERBAL_MADLUL passes for FI3L corpus tokens |
| G_E6_02 | E6 phase closure certificate emitted |

---

## E7 Closure Gates — FORMAL SHAPE + MUFRAD DALALAH

| Gate ID | Condition |
|---|---|
| G_E7_01 | Formal shape assigned for all 6 registry variants per word_class |
| G_E7_02 | weight_fit + mu_chain + path_gate execute after FormalShape |
| G_E7_03 | T12_MUFRAD_DALALAH passes; full corpus run passes |
| G_E7_04 | MaqamContextBoundary instantiated for آية الدين scope (requires SemanticSlotFrame) |
| G_E7_05 | T28_LAFZI_BLOCKED passes — BLOCKED documented in certificate |
| G_E7_06 | E7 phase closure certificates emitted |

---

## E8–E9 Closure Gates (RelationCandidate / RelationClosure)

| Gate ID | Condition |
|---|---|
| G_E8_01 | T13_RELATION_CANDIDATE_MULTI passes — 2+ ContractableUnit |
| G_E8_02 | Clause boundary tokens defined for آية الدين scope |
| G_E9_01 | T14_RELATION_CLOSURE passes |
| G_E9_02 | `coupled_dalalah` executed after RelationClosure |
| G_E9_03 | T29_WADI_BLOCKED passes — BLOCKED documented in certificate |
| G_E9_04 | Phase closure certificates emitted |

---

## E10–E13 Closure Gates (Ifadah → Tanzil)

| Gate ID | Condition |
|---|---|
| G_E10_01 | T15_IFADAH passes |
| G_E11_01 | T16_HUKM passes — linguistic Hukm only, no fiqh |
| G_E12_01 | T17_MANAT passes |
| G_E13_01 | T18_TANZIL passes — TERMINAL marker verified |
| G_E13_02 | TanzilBridge (`audit/`) executes without exception |
| G_E13_LAST | Phase closure certificates emitted for E10–E13 |

---

## E14 Closure Gates (Closure + Audit)

| Gate ID | Condition |
|---|---|
| G_E14_01 | T19_MANTUQ_CLOSURE passes |
| G_E14_02 | T20_MAFHUM_CLOSURE passes |
| G_E14_03 | T21_ANSWER_AUDIT passes |
| G_E14_04 | `reasonableness_integration.py` executes (links GPT track) |
| G_E14_05 | Phase closure certificates emitted |

---

## E15 Closure Gates (GPT Reasonableness)

| Gate ID | Condition |
|---|---|
| G_E15_01 | T30_GPT_DETERMINISTIC passes — R1–R8 without live provider |
| G_E15_02 | Live provider authorization = OWNER_DECISION_REQUIRED (documented, not blocking) |
| G_E15_03 | `chain_report.py` chain report produced |
| G_E15_04 | E15 phase closure certificate emitted |

---

## HOKOM_FULL_TAAQOL_TARGET_INTEGRATION Final Gate

All of the following must be simultaneously true:

1. All E0–E15 closure certificates emitted with canonical_exit = 0  
2. All blocking_residuals = [] in all certificates  
3. All OWNER_DECISION_REQUIRED items documented (not necessarily resolved)  
4. Full corpus run on 129 tokens produces expected output at every stage  
5. No certificate carries a synthetic trace_id  
6. VENDOR_SHA matches in all certificates  

Only after this gate: the claim `HOKOM_FULL_TAAQOL_TARGET_INTEGRATION = VERIFIED_CLOSED` is valid.
