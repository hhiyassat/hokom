# Bridge Audit v2
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

**HEAD:** 02918a6  
**TAAQOL_VENDOR_SHA:** 35381739410071ac21dd96702ecbb2acb493f90d  
**Audit date:** 2026-07-21  
**Previous audit HEAD:** ce55f7b  
**Runtime:** STATIC_ANALYSIS (sandbox Python 3.10); live confirmed on macOS Python 3.12.4

---

## Change Log Since ce55f7b

| Commit  | Change                                                                 | Impact on Bridge |
|---------|------------------------------------------------------------------------|------------------|
| 53e7932 | fix(bridge): restore live Taaqol kernel execution                      | V-001 RESOLVED: _REPO_ROOT now correctly resolves to repo root. Bridge loads Taaqol on Python 3.11+. macOS confirmed: active=True, gate_executed=True, trace_event_count=4, failure_code=None. |
| 02918a6 | test(routing): assert closed route invariants for attached pronouns    | No bridge changes. Test-only commit. |

---

## Architecture Overview

```
hokom(token)
    → hokom_pipeline.py:_build_hokom_result()
        → bundle_from_hokom_result(result) [claim_adapter.py]
            → HokomLinguisticClaimBundle (typed)
        → evaluate_hokom_claim_bundle(bundle) [live/bridge.py]
            → _build_slot_graph(bundle, taaqol)
                → SlotGraph(center, slots=(domain_claim[, wc_slot]), boundary, residuals, rank, ...)
            → gamma(slot_graph) [Taaqol core]
                → GammaResult(state=ClosureState, rank=Rank, ...)
            → _build_evidence_contract(bundle, taaqol)
                → EvidenceContract(sources=(EvidenceSource, ...))
            → gate.decide(slot_graph, Layer.CANDIDATE, evidence) [Taaqol core]
                → TransitionVerdict(state=TransitionState, granted_rank=Rank, ...)
            → compose_effective_verdict(upstream, taaqol_verdict)
            → HokomTaaqolDecision(...)
    → result dict with 'taaqol_decision', 'taaqol_verdict', 'taaqol_runtime'
```

---

## Contract 1: multiple candidates → AMBIGUOUS state

**Status: CONTRACT_MISSING**

When CRA returns multiple candidate_radical_sequences, the pipeline selects one before the bridge sees it. The bridge receives a single resolved root_candidate. State=AMBIGUOUS is never set; candidate_set is never preserved in a SlotGraph.

Location: pipeline/p3_candidate/ resolves ambiguity before claim_adapter.py:46.

---

## Contract 2: absent serialization protocol

**Status: CONTRACT_MISSING**

HokomTaaqolDecision.to_dict() exists (models.py:122) but there is no corresponding from_dict() or round-trip test. No serialize/deserialize contract is defined anywhere in the integration.

---

## Contract 3: claim_key → deterministic SHA-256

**Status: VIOLATION (V-007)**

claim_adapter.py:185: `claim_id=f'hokom:{token_id or uuid.uuid4().hex[:12]}:{surface}'`

uuid.uuid4() is non-deterministic. Two calls with the same surface produce different claim_ids. The TraceRef anchor is therefore non-reproducible.

Required: `hashlib.sha256(f'{surface}:{normalized}'.encode('utf-8')).hexdigest()[:16]`

---

## Contract 4: evaluation_id → unique runtime identifier

**Status: ABSENT**

HokomTaaqolDecision has no `evaluation_id` field. There is no runtime UUID distinct from claim_key. The claim_key (when fixed to SHA-256) would be deterministic; evaluation_id should be a runtime uuid4 to distinguish repeated evaluations of the same claim.

---

## Contract 5: rank via Taaqol RankLattice public API

**Status: PARTIAL (V-014)**

- INPUT rank: heuristic (Rank.HYPOTHESIS=3 for ACCEPT, Rank.CANDIDATE=2 for DEFER/BLOCK). Not via RankLattice.
- GRANTED rank: correctly computed via RankLattice.meet(evidence_rank, input_rank, gate_rank, ceiling) at gate step 5.

The input rank entering the meet is heuristic — it does not reflect the true evidence chain meet as SGA requires.

---

## Contract 6: Hokom emits DomainTransitionLicense

**Status: ABSENT**

No DomainTransitionLicense type or equivalent in bridge output. HokomTaaqolDecision carries effective_verdict (string) and taaqol_verdict (string) but no typed DomainTransitionLicense wrapper.

---

## Contract 7: Taaqol owns TransitionGate final decision

**Status: ALIGNED**

The bridge calls `gate.decide(input_graph, target_layer, evidence)` and accepts the returned TransitionVerdict without override. `_map_transition_state_to_verdict` maps Taaqol's five TransitionState values to four string verdicts — no Hokom logic can override a BLOCKED verdict from the gate. compose_effective_verdict adds monotonic composition on top (upstream BLOCKED → always BLOCKED) but cannot upgrade a BLOCKED gate result to LICENSED.

---

## Bridge Pipeline Steps (with alignment status)

| Step | Component | API Used | Status |
|------|-----------|----------|--------|
| 1 | Build SlotGraph | taaqol.SlotGraph, taaqol.Center, taaqol.Slot, etc. | ALIGNED (typed API) but MISSING_REQUIRED_SLOT (only 2 slots built) |
| 2 | Run Gamma | from taaqqul_slot_geometry.core.gamma import gamma | ALIGNED (pure function, correct import) |
| 3 | Build EvidenceContract | taaqol.EvidenceContract, taaqol.EvidenceSource | ALIGNED (typed API) but OWNER_DUPLICATION (rank classification in bridge) |
| 4 | Run TransitionGate | taaqol.TransitionGate(name, gate_rank=Rank.STRONG).decide() | ALIGNED |
| 5 | Map verdict | _map_transition_state_to_verdict() | ALIGNED |
| 6 | Compose verdict | compose_effective_verdict() | ALIGNED |
| 7 | Build decision | HokomTaaqolDecision(...) | OPAQUE_BRIDGE_PAYLOAD — 7 fields missing |

---

## Fail-Closed Analysis

| Failure scenario | Result | Correct? |
|-----------------|--------|---------|
| Python < 3.11 (StrEnum unavailable) | DEFERRED:TAAQOL_RUNTIME_UNAVAILABLE | YES |
| _REPO_ROOT wrong path (FIXED in 53e7932) | DEFERRED:TAAQOL_RUNTIME_UNAVAILABLE | N/A (resolved) |
| SlotGraph construction exception | DEFERRED:SLOT_GRAPH_CONSTRUCTION_FAILED | YES |
| Gamma execution exception | DEFERRED:GAMMA_EVALUATION_FAILED | YES |
| Evidence contract exception | DEFERRED:EVIDENCE_CONTRACT_FAILED | YES |
| TransitionGate exception | DEFERRED:TRANSITION_GATE_FAILED | YES |
| Clitic-only token (no lexical host) | DEFERRED:SEGMENTATION_NO_LEXICAL_HOST | YES |
| General exception in hokom_pipeline.py bridge block | taaqol_decision=None (not LICENSED) | YES (line 761-764) |

All failure paths produce DEFERRED or leave taaqol_verdict=None. No failure path produces LICENSED. Fail-closed contract is satisfied.

---

## Liveness Contract (HOKOM-TAAQOL-LIVE-BRIDGE-RECOVERY-01)

The taaqol_runtime dict in HokomTaaqolDecision distinguishes runtime infrastructure failure from semantic evaluation outcome:

```
active=False + failure_code="TAAQOL_RUNTIME_UNAVAILABLE" → Python version / import failure
active=False + failure_code="SEGMENTATION_NO_LEXICAL_HOST" → clitic-only token  
active=True + gate_executed=True + failure_code=None → full chain executed, verdict is semantic
```

macOS confirmed (Python 3.12.4):
- active=True, kernel_loaded=True, slot_graph_created=True, gamma_executed=True, gate_executed=True
- trace_event_count=4 (slot_graph_construction, gamma_evaluation, evidence_contract_build, transition_gate_decision)
- failure_code=None

Sandbox (Python 3.10):
- active=False, failure_code="TAAQOL_RUNTIME_UNAVAILABLE" (expected — StrEnum requires 3.11+)
- taaqol_verdict=None (correct — no semantic verdict when runtime unavailable)

---

## Open Issues Requiring Remediation

Ordered by severity:

1. **V-006 WRONG_SORT** (pipeline/word_class/engine.py): يَسْتَطِيعُ → ISM:MASDAR, should be FI3L. Word class engine must gate against verbal patterns.
2. **V-005 MISSING_REQUIRED_SLOT** (bridge.py:_build_slot_graph): 5 linguistic slots not projected (R1/R2/R3, PATTERN, BAB, MASDAR, PARADIGM).
3. **V-015 OPAQUE_BRIDGE_PAYLOAD** (models.py:HokomTaaqolDecision): 7 SGA-required fields absent.
4. **V-007 TRACE_LOSS** (claim_adapter.py:185): uuid4 claim_id → replace with SHA-256.
5. **V-008 TRACE_LOSS** (bridge.py): TraceEntryCandidate from gamma/gate never appended to TraceLedger.
6. **V-014 RANK_DRIFT** (bridge.py:_build_slot_graph:281-285): input rank heuristic, not lattice-meet.
7. **V-013 OWNER_DUPLICATION** (bridge.py:_build_evidence_contract:329-342): Arabic evidence classification in bridge.
8. **V-004 EVIDENCELESS_ACCEPT** (slot_engineering.py:word_gate): ACCEPT without EvidenceContract at pipeline layer.
9. **V-003 UNLICENSED_TRANSITION** (slot_engineering.py:SLOT_TRANS): 8 state transitions lack formal gate.
10. **V-002 UNTYPED_SLOT** (cell_builder.py): phonological slots as plain dicts.
11. **V-010 SILENT_CANDIDATE_SELECTION** (bridge.py): no AMBIGUOUS state for multiple candidates.
12. **V-012 RESIDUAL_LOSS** (claim_adapter.py): active_residuals as plain strings; typed structure lost on output.
13. **V-011 RESIDUAL_LOSS** (cell_builder.py): HAMZAT_AL_WASL/ALEF_FARQA not classified as EXPLANATORY Residuals.
14. **V-009 TRACE_LOSS** (claim_adapter.py): hokom trace_ids never written to TraceLedger.
