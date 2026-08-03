# SGA Conformance Audit — Ambiguity Preservation
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### MISSING_AMBIGUITY_STATE — Violation T-10

### SlotState Enum

The vendor taaqqul_slot_geometry library defines:
```
SlotState: EMPTY | FILLED | BROKEN
```
There is NO `AMBIGUOUS` state. There is NO `NOT_APPLICABLE` state.

### Bridge Behavior

When Hokom produces an ambiguous morphological analysis (multiple competing parse paths):

1. The bundle DTO carries competing claims in `mushtaq_claims`, `wazn_claim`, etc.
2. `_build_slot_graph()` selects a single `domain_directive` (ACCEPT/BLOCK/DEFER) and builds at most 2 slots
3. No second slot is opened to represent the competing parse
4. No AMBIGUOUS state is set on any slot
5. No candidate_set is populated with competing hypotheses
6. Ambiguity is silently collapsed to the first-ranked parse

### Impact

- Taaqol gate algebra cannot arbitrate between competing morphological hypotheses
- BLOCKED verdict for one parse path cannot coexist with LICENSED verdict for another in the same graph
- Downstream consumers of HokomTaaqolDecision.taaqol_verdict receive a single resolved verdict with no indication that ambiguity was suppressed
- The `reason_codes` and `contradictions` tuples in HokomTaaqolDecision do not carry "AMBIGUITY_SUPPRESSED" codes

### Remediation

To preserve ambiguity through the gate:
1. Add an AMBIGUOUS slot type or use parallel BROKEN + FILLED slots with competing evidence contracts
2. Populate candidate_set in SlotGraph with all competing parse hypotheses
3. Let Gamma adjudicate; surface the ClosureState (PERFORATED_CLOSED for partial ambiguity, OPEN for unresolved)
4. Expose resolved vs. suppressed interpretations in HokomTaaqolDecision
