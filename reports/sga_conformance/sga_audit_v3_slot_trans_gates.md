# SGA Conformance Audit — SLOT_TRANS Gates
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### Violation T-08: UNLICENSED_TRANSITION

**File**: `pipeline/p1_atomic_structure/slot_engineering.py`

### SLOT_TRANS Dictionary

```python
SLOT_TRANS: dict[str, dict[str, str | None]]
```

8 entries covering Arabic syllable structure transitions (e.g. CV→CVC on consonant append, CVC→CVCC on cluster, etc.).

### _gate() Function

```python
def _gate(state: str) -> str:  # returns 'ACCEPT' | 'DEFER' | 'BLOCK'
```

This is a plain Python function. It does NOT:
- Construct an EvidenceContract
- Call TransitionGate.decide()
- Consult RankLattice
- Produce a DomainTransitionLicense
- Emit a TraceEntryCandidate to a TraceLedger

### Conformance Requirements

Per SGA, every slot state transition must:
1. Be submitted to TransitionGate.decide(input_graph, target_layer, evidence_contract)
2. Have an EvidenceContract with at least one EvidenceSource
3. Receive a Rank via RankLattice.meet(evidence_rank, identity_rank, gate_rank, ceiling)
4. Emit a TraceLedger entry documenting the transition

### All 8 SLOT_TRANS Transitions Are Non-Conformant

| Entry | Status |
|-------|--------|
| 1 | UNLICENSED — no TransitionGate |
| 2 | UNLICENSED — no TransitionGate |
| 3 | UNLICENSED — no TransitionGate |
| 4 | UNLICENSED — no TransitionGate |
| 5 | UNLICENSED — no TransitionGate |
| 6 | UNLICENSED — no TransitionGate |
| 7 | UNLICENSED — no TransitionGate |
| 8 | UNLICENSED — no TransitionGate |

### Remediation

1. For each SLOT_TRANS entry, build an EvidenceContract with phonological evidence
2. Call TransitionGate.decide() with a SlotGraph representing the pre-transition state
3. Accept the transition only if TransitionVerdict is LICENSED
4. Emit a TraceLedger entry for each transition attempt
5. Replace `_gate(state) -> str` with a function returning a typed TransitionVerdict
