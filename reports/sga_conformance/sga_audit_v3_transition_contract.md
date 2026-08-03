# SGA Conformance Audit — Transition Contract
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### TransitionGate.decide() — Canonical 6-Step Law

Defined in `vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/transition_gate.py`:

1. Validate input graph
2. Check target_layer legality
3. Run Gamma(input_graph) — get GammaResult
4. If evidence is empty → return DEFERRED / GATE_REQUIRED
5. Compute granted = RankLattice.meet(evidence_rank, identity_rank, gate_rank, ceiling)
6. Emit TransitionVerdict

### RankLattice

Defined in `vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/rank_lattice.py`:

```
Rank(IntEnum): ZERO=0, TRACE=1, CANDIDATE=2, HYPOTHESIS=3, LICENSED=4, STRONG=5, CERTIFICATE=6
RankLattice.meet(*ranks) = min(*ranks)
RankLattice.join(*ranks) = max(*ranks)
```

### Bridge Usage (CONFORMANT)

`pipeline/taaqol_integration/live/bridge.py` correctly:
- Builds EvidenceContract with EvidenceSource items
- Calls TransitionGate.decide(input_graph, target_layer, evidence_contract)
- Does NOT manually apply min/max — delegates to RankLattice.meet() via TransitionGate
- Maps domain_directive to Rank.HYPOTHESIS (ACCEPT) or Rank.CANDIDATE (non-ACCEPT) at construction

### SLOT_TRANS Transitions (VIOLATION T-08)

`pipeline/p1_atomic_structure/slot_engineering.py` — 8 transitions:

| From | To (implied) | Method |
|------|------|--------|
| All 8 SLOT_TRANS entries | Various | Raw dict lookup — NO TransitionGate, NO EvidenceContract, NO RankLattice |

These transitions operate entirely outside the Taaqol gate algebra. No DomainTransitionLicense is produced for any phonological slot transition.

### Gamma Function

Defined in `vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/gamma.py`:
- Pure function: `gamma(SlotGraph) -> GammaResult`
- 10-step ordered closure
- Step 7: BLOCKING residual → ClosureState.BLOCKED
- GammaResult.ClosureState: MINIMALLY_CLOSED, PERFORATED_CLOSED, BLOCKED, OPEN, INVALID, FORBIDDEN_LEAP

### Residual Routing in Bridge

- `BLOCK` directive → ResidualKind.BLOCKING
- `active_residuals` with `block:` prefix → ResidualKind.BLOCKING
- `active_residuals` with `defer:` prefix → ResidualKind.DEFERRABLE
- Residuals that are BLOCKING cause Gamma to return BLOCKED (step 7)
