# 14 — IMPLEMENTATION DEPENDENCY GRAPH

**Document ID:** `R0-14-DEPS`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY

---

## Linear Dependency Chain (strict order)

**CONSTITUTIONAL_RECONCILIATION_01 AMENDMENT (2026-08-01):**
Phase numbering corrected. E0 = SHAs only. E1–E4 are new phases inserted before
the original E1 (DalOnly), which is now E5. See SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01.md.

```
R0_REQUIREMENTS_READINESS (this package)
    ↓
E0: TARGET BASELINE FREEZE
    ├── VENDOR_SHA pinned: 35381739410071ac21dd96702ecbb2acb493f90d
    ├── HOKOM_HEAD: 8e37b738ece7183818189146912cb14e3dce3a07
    ├── Corpus SHA: 6bd635a05530965f13f76cf003f7738130badec6981bcb0e73f2465d386e1ed7
    ├── carrier_core.py + _schema_helpers.py (vendor API inventory)
    └── SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01.md
    ↓
E1: AYAT-AL-DAYN CANONICAL LEXICAL REGISTRY
    └── ayat_al_dayn_registry.py (74 ISM/FI3L entries; structural non_meaning_proof)
    ↓
E2: P2 REGISTRY PROJECTION
    ├── registry_adapter.py (imports AYAT_AL_DAYN_REGISTRY from E1)
    └── P2 blocker deactivated (registry_matches non-None)
    ↓
E3: HOKOM P3/P4/P5 CONTINUITY
    └── Trace real P2→P3 flow; identify blockers
    ↓
E4A: LICENSING BOUNDARY PRECONDITION GUARDS  ← CLOSED
    └── licensing_boundary_adapter.py (HARF/directive/empty-host guards)
    ↓
E4B: PRE-WEIGHT TYPED CARRIERS
    ├── Arabic diacritical text → (letter, haraka) pairs
    ├── SyllableCandidate → SyllableSequenceCandidate → WordBoundaryCandidate
    ├── WordCarrierCandidate → PathCandidate → RootStemCandidate
    ├── OriginalExtraMap → OperationTraceCandidate → PreWeightSurface
    └── WeightReadinessCandidate (μ_weight_readiness — all 8 stages)
    ↓
E4C: NATIVE LICENSING BOUNDARY
    ├── weigh(WeightReadinessCandidate) → WeightFitCandidate
    ├── omega_governance() → ResidualGovernanceVerdict (GRANTED)
    ├── BoundaryEvidence(LEXICAL, segment_host, ...)
    ├── assess_license(candidate, evidence, governance) → ELIGIBLE
    └── LicensingBoundaryVerdict produced
    ↓
E5: DAL-ONLY CHAIN
    ├── registry_closure.py (RegistryLookupResult produced)
    ├── dal_only.py (prove_dal() called with LicensingBoundaryVerdict)
    └── pre_weight.py
    ↓
E6: VerbalMadlul
    └── verbal_madlul.py
    ↓ (two parallel tracks from here)
    ├────────────────────────────────┐
    ↓ (single-token track)           ↓ (multi-token track — requires 2+ CU)
E7: FormalShape + MufradDalalah     E8: RelationCandidate
    ├── formal_shape.py (×6)             ├── relation_candidate.py
    ├── weight_fit.py, mu_chain.py       └── clause boundary mapping
    ├── mufrad_dalalah_closure.py        ↓
    ├── MaqamContextBoundary ← HERE    E9: RelationClosure
    └── LAFZI: BLOCKED                      ├── relation_closure.py
    ↓                                       ├── coupled_dalalah.py
    │                                       └── WADI: BLOCKED
    └────────────────────────────────┘  ↓
                                        E10: Ifadah → E11: Hukm → E12: Manat
                                        ↓
                                        E13: Tanzil (TERMINAL)
                                             ├── tanzil_candidate.py
                                             └── audit/tanzil_bridge.py
                                        ↓
                                        E14: MantuqClosure + MafhumClosure + Audit
                                             ├── mantuq_closure.py
                                             ├── mafhum_closure.py
                                             ├── audit/answer_audit.py
                                             ├── audit/reasonableness_integration.py
                                             └── chain_report.py
                                        ↓
                                        E15: GPT Reasonableness (parallel track)
                                             ├── gpt/R1–R8
                                             ├── gpt/context_builder.py
                                             ├── gpt/verdict_schema.py
                                             └── audit/model_client.py (LIVE_PROVIDER=ODR)
```

---

## Blocked Branches

| Branch | Blocking Condition | Resolution |
|---|---|---|
| LAFZI (lafzi_b7_integration.py, lafzi_madlul.py) | No phonological analysis in Hokom P0_PHONOLOGICAL | OWNER_DECISION_REQUIRED — document BLOCKED in E6 certificate |
| WADI (wadi_c8_integration.py, wadi_madlul.py) | WADI domain classification pending | OWNER_DECISION_REQUIRED — document BLOCKED in E8 certificate |
| Live LLM (gpt/model_client.py with provider) | LIVE_PROVIDER_ALLOWED = 0 | OWNER_DECISION_REQUIRED — deterministic track proceeds |

---

## Phase → Files Map

**CONSTITUTIONAL_RECONCILIATION_01 AMENDMENT (2026-08-01):** Phase numbering corrected.

| Phase | Files Implemented |
|---|---|
| E0 | SHA verification artifacts only; registry_contract.py (vendor API inventory); SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01.md |
| E1 | pipeline/taaqol_integration/e1_lexical_registry/ayat_al_dayn_registry.py (74 entries) |
| E2 | registry_adapter.py (A0 adapter — imports E1 registry; deactivates P2 blocker) |
| E3 | P3/P4/P5 flow trace; blocker documentation |
| E4A | licensing_boundary_adapter.py (precondition guards; DONE) |
| E4B | pre_weight chain adapter: Arabic decomposer + all 8 μ-stage carriers |
| E4C | licensing_boundary_adapter.py (full assess_license chain; weigh() integration) |
| E5 | dal_only.py, registry_closure.py, A2 adapter |
| E6 | verbal_madlul.py, A3 adapter |
| E7 | formal_shape.py (×6 variants), formal_style_candidate.py, weight_fit.py, mu_chain.py, mufrad_dalalah_closure.py, mufrad_semantic_slot_geometry.py, dalalah_candidates.py, maqam_context_boundary.py, weight_ontology_bridge_c1.py, weight_image.py, A6 + A7 adapters |
| E8 | relation_candidate.py, clause boundary mapping, A8 adapter |
| E9 | relation_closure.py, coupled_dalalah.py, A9 adapter, WADI BLOCKED documented |
| E10 | ifadah_candidate.py, A10 adapter |
| E11 | hukm_candidate.py, A11 adapter |
| E12 | manat_candidate.py, A12 adapter |
| E13 | tanzil_candidate.py, audit/tanzil_bridge.py, A13 adapter |
| E14 | mantuq_closure.py, mafhum_closure.py, audit/answer_audit.py, audit/reasonableness_integration.py, chain_report.py, A14 + A15 + A16 adapters |
| E15 | gpt/R1–R8, gpt/context_builder.py, gpt/verdict_schema.py, gpt/evidence_formatter.py, audit/model_client.py (deterministic), audit/successor.py, A20 adapter |

---

## Hard Constraints on Order

1. **E0 must be CLOSED before any E1–E15 code** — no production code before schema freeze  
2. **E4 must be CLOSED before E5 and E7** — ContractableUnit is the fork point  
3. **RelationCandidate (E7) requires 2+ ContractableUnit** — must have real clause scope, not mocked  
4. **Tanzil (E12) is TERMINAL** — no further vertical chain stages after E12 in the canonical registry  
5. **MantuqClosure (E13) requires both Hukm AND Manat** — cannot run on Hukm alone  
6. **GPT track (E15) is independent of E9–E12 vertical chain** but requires MufradDalalah output (E6)  
7. **LAFZI + WADI** — blocked branches must be documented in certificates; they do not block main chain progress
