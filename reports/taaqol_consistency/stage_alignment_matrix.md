# Stage Alignment Matrix

**Audit date:** 2026-07-21  
**Hokom HEAD:** b706ced  
**Taaqol PIN:** 35381739410071ac21dd96702ecbb2acb493f90d  

## Summary

All constitutional areas consumed by Hokom from Taaqol are ALIGNED.  
No ADAPTER_REQUIRED, HOKOM_CONTRACT_GAP, TAAQOL_CONTRACT_GAP, or OWNERSHIP_COLLISION rows exist.

| Taaqol Area | Module | Hokom Consumer | Status | Open Obligation |
|-------------|--------|----------------|--------|-----------------|
| Trace | core.trace_ledger | bridge (via GammaResult) | ALIGNED | NONE |
| SlotGraph | core.slot_graph | bridge._build_slot_graph() | ALIGNED | NONE |
| Gamma | core.gamma | bridge.gamma() call | ALIGNED | NONE |
| Rank | core.rank_lattice | bridge + admission_gate + native_continuation | ALIGNED | NONE |
| Evidence | core.evidence_contract | bridge._build_evidence_contract() | ALIGNED | NONE |
| Residuals | core.residual_policy | admission_gate | ALIGNED | NONE |
| TransitionGate | core.transition_gate | bridge.TransitionGate.decide() | ALIGNED | NONE |
| output_verdict (TransitionState) | core.transition_state | bridge._map_transition_state_to_verdict() | ALIGNED | NONE |
| serialization | core.* | models.py + projection.py | ALIGNED | NONE |
| failure_codes | core.failure_taxonomy | admission_gate | ALIGNED | NONE |
| GenericPayload/center_scope | core.slot_graph (Center) | bridge (segment_host) | ALIGNED | NONE |
| claim kind/source/provenance | core.slot_graph (GenerationSource) | bridge | ALIGNED | NONE |
| ForbiddenLineRegistry | core.forbidden_lines | NOT directly (gate internal) | ALIGNED_EXTENSION_UNUSED | NONE |
| weight carriers (PR-10) | weight.* | NOT consumed | NOT_CONSUMED | NONE |
| G0 bare-stem pipeline | g0_c1..g0_c6 | NOT consumed | NOT_CONSUMED | NONE (future milestone) |
| enriched_simulation_agent | enriched_simulation_agent/ | NOT consumed (PROHIBITED) | NOT_CONSUMED | NONE |

## TransitionState Mapping (Hokom Bridge)

| Taaqol TransitionState | Hokom taaqol_verdict |
|-----------------------|---------------------|
| APPROVED | LICENSED |
| DEFERRED | DEFERRED |
| BLOCKED | BLOCKED |
| REJECTED | DEFERRED |
| FORBIDDEN_LEAP | BLOCKED |

## Decision Composition (compose_effective_verdict)

| upstream_verdict | taaqol_verdict | effective_verdict |
|-----------------|---------------|------------------|
| ACCEPT | LICENSED | ACCEPT |
| ACCEPT | DEFERRED | ACCEPT |
| ACCEPT | BLOCKED | BLOCKED |
| DEFER | * | DEFER |
| BLOCK | * | BLOCK |

## Notes

1. All imports are fail-closed: ImportError → DEFERRED (not LICENSED). Zero silent fallbacks.  
2. No Taaqol source is patched or copied into Hokom.  
3. Python 3.11+ required at runtime for StrEnum. Sandbox (3.10) defers to DEFERRED path.  
4. The AnswerAudit path (PR-6 audit layer) is architecturally DEFERRED — Hokom is not a ModelClient.
