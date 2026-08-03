# 10 — FAILURE AND RESIDUAL TAXONOMY

**Document ID:** `R0-10-FAILURE`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY

---

## 1. Phase States (constitutional)

| State | Meaning |
|---|---|
| `NOT_STARTED` | Phase not yet attempted |
| `REQUIREMENTS_READY` | Requirements package complete, implementation not started |
| `IMPLEMENTED` | Code written but not verified |
| `FOCUSED_VERIFIED` | Unit tests pass in isolation |
| `INTEGRATED_VERIFIED` | Integration tests pass with upstream stages |
| `CANONICAL_VERIFIED` | Full 129-token corpus run produces expected output |
| `CLOSED` | Phase closure certificate emitted and validated |
| `DEFERRED` | Intentional deferral — documented reason, no OWNER_DECISION_REQUIRED |
| `BLOCKED` | Cannot proceed — external dependency not met |
| `INVALID` | Implementation violates a constitutional invariant |
| `ROLLED_BACK` | Implementation reverted — see rollback certificate |

---

## 2. Active Blockers (as of R0)

| Blocker ID | Layer | is_active | Severity | Root Cause | Fix Phase |
|---|---|---|---|---|---|
| `registry_load_failure` | P2_REGISTRY_PROJECTION | TRUE | BLOCKER | `hokom_evidence["registry_matches"]` is None | E0 |
| `weight_layer_not_integrated` | P3–P5 + full weight chain | TRUE | BLOCKER | LicensingBoundaryVerdict not produced | E0 |
| `type_mismatch_licensing_boundary` | weight/ adapter | TRUE | BLOCKER | HokomLinguisticClaimBundle ≠ LicensingBoundaryVerdict | E0 |
| `phonological_not_reached` | P0_PHONOLOGICAL | TRUE | DEFERRED | No phonological analysis in Hokom | BLOCKED_NO_PHONOLOGY |
| `lafzi_blocked_no_phonology` | lafzi_b7_integration | TRUE | BLOCKED | Requires phonological evidence | BLOCKED_NO_PHONOLOGY |
| `wadi_blocked_classification` | wadi_c8_integration | TRUE | BLOCKED | WADI domain not classified | OWNER_DECISION_REQUIRED |
| `live_provider_not_authorized` | GPT Reasonableness R1–R8 | TRUE | DEFERRED | LIVE_PROVIDER_ALLOWED = 0 | OWNER_DECISION_REQUIRED |
| `relation_candidate_single_token` | RelationCandidate (Stage 5) | TRUE | CONSTITUTIONAL | Single token cannot produce RelationCandidate | MULTI_TOKEN_SCOPE (E7) |
| `parity_not_proven` | vendor submodule | TRUE | WARNING | GitHub SHA unreachable | OWNER_DECISION_REQUIRED |

---

## 3. FAIL-CLOSED Contract

**Source:** `pipeline/taaqol_integration/live/bridge.py` — `_deferred_decision()`

```
import failure → DEFERRED
Never LICENSED on import failure
```

This contract is **inviolable**. Any bypass constitutes INVALID state.

Implementation requirement: every adapter wrapping a Taaqol import must:
1. Catch `ImportError` and `ModuleNotFoundError`
2. Call `_deferred_decision()` — never return `LICENSED`
3. Log the failure with trace_id and vendor_sha

---

## 4. Residual Taxonomy

| Residual Class | Severity | Propagation | Resolution |
|---|---|---|---|
| `BLOCKER` | Fatal for current stage | Stops downstream stages | Must be resolved before CLOSED |
| `DEFERRED_INTENTIONAL` | Non-fatal | Documented in certificate | Owner must acknowledge |
| `DEFERRED_PHONOLOGICAL` | Non-fatal | Only affects LAFZI/WADI | Blocked — not required for main chain |
| `SCHEMA_DRIFT_RISK` | Warning | If vendor SHA diverges | Parity report must be updated |
| `SYNTHETIC_ID_FORBIDDEN` | Fatal | Any stage producing synthetic trace_id | Automatic INVALID |
| `STUB_FORBIDDEN` | Fatal | Any stub returning LICENSED | Automatic INVALID |
| `HR2S_FORBIDDEN_RUNTIME` | Fatal | HR2S used at runtime | Automatic INVALID |

---

## 5. Verdict Taxonomy

| Verdict | Meaning | Valid When |
|---|---|---|
| `LICENSED` | Token passed full chain with valid evidence | weight chain complete, no blocker |
| `DEFERRED` | Token cannot be adjudicated at this time | weight layer not integrated; import failure; phonological gap |
| `NOT_APPLICABLE` | Stage not applicable for this token class | HARF at non-HARF stage; slot NOT_APPLICABLE |
| `REFUSED` | Registry explicitly refuses this token | RegistryLookupState.REFUSED |
| `BLOCKED` | Upstream dependency not met | P3/P4/P5 when P2 blocked |

**Current corpus state (from live run):**
- 73 tokens: `effective_verdict = LICENSED` (Taaqol core 7-ops complete, weight layer not reached)
- 56 tokens: `effective_verdict = DEFERRED` (weight layer not integrated)
- 8 tokens: `pipeline_verdict = DEFER` (Hokom upstream chose not to emit claim)

---

## 6. Invalid State Triggers (automatic — no override)

1. `trace_id` is synthetic (does not come from live PipelineTrace)
2. Import failure returns `LICENSED`
3. `RegistryEntry.non_meaning_proof` is empty string
4. `rank > REGISTRY_RANK_CEILING`
5. HR2S used at runtime
6. Stub code returns a non-DEFERRED verdict
7. Phase closure certificate emitted without all required fields
8. `blocking_residuals` is non-empty in closure certificate

---

## 7. Phase Certificate Failure Protocol

If a phase closure gate fails:
1. Phase state → `BLOCKED` (not `CLOSED`)
2. Emit `PHASE_BLOCK_RECORD.json` with: phase_id, gate_id, failure_reason, blocking_residuals
3. Do not advance to next phase
4. Report to OWNER — await instruction
5. No rollback without OWNER_DECISION
