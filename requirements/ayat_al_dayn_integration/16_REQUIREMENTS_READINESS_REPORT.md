# 16 — REQUIREMENTS READINESS REPORT

**Document ID:** `R0-16-READINESS`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY

---

## R0 Closure Declaration

All 17 requirements files have been produced in `requirements/ayat_al_dayn_integration/`. R0 is CLOSED subject to G_R0_13 (phase closure certificate emission — see below).

---

## Files Status

| File | Status | Notes |
|---|---|---|
| 00_SCOPE_AND_BOUNDARIES.md | ✓ READY | Scope, constitutional constraints, ODR boundaries |
| 01_CANONICAL_CORPUS_MANIFEST.json | ✓ READY | 129 tokens, 73 LICENSED, 56 DEFERRED, 8 PIPELINE_DEFER |
| 02_HOKOM_STAGE_OWNERSHIP_MATRIX.csv | ✓ READY | All P0–GPT stages with owner, state, blocker |
| 03_TAAQOL_RUNTIME_INVENTORY.csv | ✓ READY | All 46 weight/ + 5 audit/ + 11 gpt/ files classified |
| 04_VENDOR_MAIN_PARITY_REPORT.md | ✓ READY | PARITY_VERDICT = NOT_PROVEN (non-blocking) |
| 05_P2_REGISTRY_CONTRACT.md | ✓ READY | Blocker root cause + PR-16C schema + adapter reqs |
| 06_LEXICAL_REGISTRY_SCHEMA.json | ✓ READY | Schema structure + token surfaces + lexical freeze policy |
| 07_LINGUISTIC_EVIDENCE_REQUIREMENTS.csv | ✓ READY | All evidence types with type mismatch analysis |
| 08_HOKOM_TAAQOL_ADAPTER_MATRIX.csv | ✓ READY | All 22 adapters with phases and current state |
| 09_CONTEXT_AND_MAQAM_REQUIREMENTS.md | ✓ READY | MaqamContextBoundary + clause boundaries |
| 10_FAILURE_AND_RESIDUAL_TAXONOMY.md | ✓ READY | All blockers, residuals, FAIL-CLOSED contract |
| 11_PROVENANCE_AND_VERSIONING_POLICY.md | ✓ READY | VENDOR_SHA policy + trace_id policy + git policy |
| 12_TEST_AND_EVALUATION_MATRIX.csv | ✓ READY | 32 tests across all phases |
| 13_STAGE_ACCEPTANCE_GATES.md | ✓ READY | R0 + E0–E15 gates |
| 14_IMPLEMENTATION_DEPENDENCY_GRAPH.md | ✓ READY | Full E0→E15 dependency chain + blocked branches |
| 15_MANAGER_DEMO_ACCEPTANCE_SCENARIO.md | ✓ READY | D0–D6 demo scenarios with falsifying conditions |
| 16_REQUIREMENTS_READINESS_REPORT.md | ✓ READY | This file |

---

## R0 Gate Status

| Gate | Status | Notes |
|---|---|---|
| G_R0_01 — All 17 files exist | ✓ 1 | Verified |
| G_R0_02 — Corpus = 129 tokens | ✓ 1 | Confirmed from live CSV |
| G_R0_03 — Runtime inventory complete | ✓ 1 | 46 weight/ + 5 audit/ + 11 gpt/ |
| G_R0_04 — P2 blocker root cause documented | ✓ 1 | File + line in 05_P2_REGISTRY_CONTRACT.md |
| G_R0_05 — All type mismatches in adapter matrix | ✓ 1 | 22 adapters in 08_HOKOM_TAAQOL_ADAPTER_MATRIX.csv |
| G_R0_06 — All active blockers documented | ✓ 1 | 9 blockers in 10_FAILURE_AND_RESIDUAL_TAXONOMY.md |
| G_R0_07 — Provenance policy complete | ✓ 1 | VENDOR_SHA + trace_id in 11_PROVENANCE_AND_VERSIONING_POLICY.md |
| G_R0_08 — Dependency graph complete | ✓ 1 | E0→E15 in 14_IMPLEMENTATION_DEPENDENCY_GRAPH.md |
| G_R0_09 — All ODR items listed | ✓ 1 | See ODR table below |
| G_R0_10 — VENDOR_SHA confirmed | ✓ 1 | `35381739410071ac21dd96702ecbb2acb493f90d` in all CSV rows |
| G_R0_11 — No implementation before R0 close | ✓ 1 | No production code written |
| G_R0_12 — Parity verdict explicit | ✓ 1 | NOT_PROVEN in 04_VENDOR_MAIN_PARITY_REPORT.md |
| G_R0_13 — Closure certificate emitted | ⟳ PENDING | Emitted immediately after this report |

---

## Open OWNER_DECISION_REQUIRED Items

| ODR ID | Item | Blocking | Notes |
|---|---|---|---|
| ODR_01 | GitHub SHA parity verification | Non-blocking | User must run curl against GitHub API |
| ODR_02 | Vendor submodule update authorization | Blocking (if update needed) | VENDOR_UPDATE_ALLOWED = 0 |
| ODR_03 | Live LLM provider for GPT Reasonableness | Non-blocking for E15 deterministic track | LIVE_PROVIDER_ALLOWED = 0 |
| ODR_04 | WADI domain classification | Non-blocking for main chain | wadi_c8_integration.py remains BLOCKED |
| ODR_05 | LAFZI / phonological analysis | Non-blocking for main chain | Requires Hokom phonological layer |
| ODR_06 | Corpus change or new source adoption | Blocking if triggered | CORPUS_SHA256 frozen |
| ODR_07 | Constitution amendment | Blocking | No amendment without explicit owner ratification |
| ODR_08 | git commit / tag / push / merge authorization | Blocking | AUTONOMOUS_COMMIT_MODE = 0 |

---

## Known Gaps (documented, not blocking R0)

| Gap | Description | Resolution Phase |
|---|---|---|
| TYPE_MISMATCH: HokomLinguisticClaimBundle ≠ LicensingBoundaryVerdict | Root cause of weight-layer deferred verdicts | E0 |
| registry_matches None | P2 blocker active — 56 tokens cannot advance | E0 |
| FormalShape 6-variant selection logic | Not yet implemented | E5 |
| Clause boundary mapping | Token-to-clause assignment for RelationCandidate | E7 |
| Chain report serialization format | chain_report.py format not yet defined | E14 |
| GPT prompt engineering for R1–R8 | Deterministic prompt templates not yet written | E15 |

---

## Corpus Summary

| Metric | Value |
|---|---|
| Total unique tokens | 129 |
| Source | البقرة 2:282 |
| pipeline_verdict = ACCEPT | 121 |
| pipeline_verdict = DEFER | 8 |
| taaqol_verdict = LICENSED | 73 |
| taaqol_verdict = DEFERRED | 56 |
| word_class HARF | 21 |
| word_class ISM | 54 |
| word_class FI3L | 33 |
| word_class empty | 21 |
| VENDOR_SHA in all rows | ✓ `35381739410071ac21dd96702ecbb2acb493f90d` |
| CORPUS_SHA256 | `6bd635a05530965f13f76cf003f7738130badec6981bcb0e73f2465d386e1ed7` |

---

## Next Phase

R0 → **E0: Registry Schema Freeze**

First implementation task: A0_REGISTRY_LOOKUP adapter — populate `hokom_evidence["registry_matches"]` to deactivate `registry_load_failure` blocker. This unblocks P3/P4/P5 cascade.

Second implementation task: A1_LICENSING_BOUNDARY adapter — produce `LicensingBoundaryVerdict` from `HokomLinguisticClaimBundle`. This fixes the type mismatch root cause.

No code begins until R0 closure certificate is emitted.
