# 00 — SCOPE AND BOUNDARIES

**Document ID:** `R0-00-SCOPE`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY

---

## 1. Target

Integrate all Taaqol-GPT components required for full constitutional analysis of آية الدين (البقرة:282), advancing from the current state (Taaqol core 7-ops CLOSED) through the full weight-layer vertical chain and GPT Reasonableness, with provenance-complete, type-correct, non-stubbed evidence at every stage.

**VENDOR_SHA (pinned):** `35381739410071ac21dd96702ecbb2acb493f90d`  
**HOKOM_HEAD (at ratification):** `8e37b738ece7183818189146912cb14e3dce3a07`  
**TARGET_MODE:** `PINNED_VENDOR_SHA` — no submodule update without OWNER_DECISION_REQUIRED

---

## 2. In Scope

| Item | Description |
|---|---|
| P2_REGISTRY_PROJECTION | Fix registry_load_failure blocker; wire RegistryEntry lookup |
| P3/P4/P5 continuation | After P2 unblocked, verify cascade opens |
| LicensingBoundaryVerdict adapter | Map Hokom P1 output → Taaqol weight-layer entry |
| DalOnly → ContractableUnit (Stages 1–4) | Full native weight-chain cascade |
| FormalShape registries (×6) | build_word_class_registry() and variants |
| MufradDalalah (Stage 7) | prove_mufrad_dalalah_closure() |
| RelationCandidate / RelationClosure (Stages 5/8) | Multi-token scope only — requires 2+ ContractableUnit |
| Ifadah → Hukm → Manat → Tanzil (Stages 9–12) | Full vertical chain on clause-level scopes |
| MantuqClosure / MafhumClosure (post-vertical) | After Hukm + Manat available |
| TanzilBridge + AnswerAudit (audit/) | After full vertical chain |
| GPT Reasonableness R1–R8 (gpt/) | Deterministic track; live provider = OWNER_DECISION_REQUIRED |
| DAL/LAFZI chain | Classified per inventory; integrated or BLOCKED with proof |
| WADI chain (C8) | Classified per inventory |
| DAL-A4 through DAL-A8 runtime gates | Classified per inventory |
| μ-chain, path_gate, weight_fit, coupled_dalalah | Classified per inventory |
| All carriers (CARRIER/SCHEMA) | instantiate + validate + serialize + version |
| All laws (LAW_ONLY) | invariant tests + forbidden transition tests |
| All adapters | field-map + continuity tests |

---

## 3. Out of Scope

| Item | Reason |
|---|---|
| `TAAQOL_PRODUCTION_READY = TRUE` | Forbidden claim — repo is Research Alpha |
| `FULL_ARABIC_LANGUAGE_COMPLETE` | This integration covers آية الدين slice only |
| Live LLM provider for GPT Reasonableness | OWNER_DECISION_REQUIRED; deterministic track is in scope |
| Submodule update (vendor/Taaqol-GPT) | OWNER_DECISION_REQUIRED |
| commit / tag / push / merge | AUTONOMOUS_COMMIT_MODE = 0 |
| Modifying frozen files | FROZEN_FILE_OVERRIDE = 0 |
| LAFZI/WADI if no phonological analysis in Hokom | Will be classified BLOCKED_NO_PHONOLOGY or NOT_APPLICABLE with proof |
| Fiqh rulings or fatwa generation | Hukm here = linguistic structural carrier, not religious ruling |

---

## 4. Claimed Completion Definitions

| Term | What it means |
|---|---|
| `P2_REGISTRY_INTEGRATION = CLOSED` | P2 adapter executes, produces RegistryProjectionCandidate, blocker inactive, P3 opens |
| `DAL_ONLY_NATIVE_STAGE = CLOSED` | prove_dal() called with real LicensingBoundaryVerdict, returns DalOnlyCandidate, no exceptions |
| `AYAT_AL_DAYN_RELATION_SLICE = CLOSED` | RelationCandidate proved on real 2+ ContractableUnit from آية الدين scope |
| `HOKOM_FULL_TAAQOL_TARGET_INTEGRATION = VERIFIED_CLOSED` | All E0–E15 gates met; all denominator items resolved |

**Forbidden before all gates met:** `TAAQOL COMPLETE` · `ALL STAGES DONE` · `FULL PROJECT CLOSED`

---

## 5. Constitutional Constraints (binding)

- No commit · No tag · No push · No merge  
- No HR2S at runtime  
- All trace_id from live PipelineTrace only — no synthetic IDs  
- Taaqol is sole constitutional governor  
- Saleh/Qiyas owns 19-stage SCG registry — no modification  
- Every typed carrier must carry non_meaning_proof if RegistryEntry  
- Every stage must emit PHASE_CLOSURE_CERTIFICATE.json before transition

---

## 6. Owner-Decision Boundaries (stop points)

1. TARGET_TAAQOL_SHA change or submodule update  
2. Any frozen file modification  
3. corpus change or new linguistic source adoption  
4. live LLM provider integration  
5. schema change affecting downstream stages (non-backward-compatible)  
6. commit / tag / push / merge authorization  
7. Constitution amendment  
