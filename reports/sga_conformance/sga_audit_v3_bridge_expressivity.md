# SGA Conformance Audit — Bridge Expressivity
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### BRIDGE_EXPRESSIVITY_STATUS: PARTIAL

### Present Expressivity

| Capability | Status | Evidence |
|------------|--------|----------|
| domain_claim slot | PRESENT | bridge.py `_build_slot_graph()` |
| word_class_claim slot | PRESENT (conditional) | bridge.py, only if lexical_class is not None |
| EvidenceContract with ranked sources | PRESENT | bridge.py `_build_evidence_contract()` |
| Residuals (BLOCKING/DEFERRABLE) | PRESENT | block:/defer: prefix routing |
| Fail-closed on ImportError | PRESENT | DEFERRED not LICENSED |
| Liveness contract dict (_rt) | PRESENT | active, kernel_loaded, slot_graph_created, gamma_executed, gate_executed, trace_event_count, failure_code, failure_detail |

### Absent Expressivity (Violations)

| Missing Capability | Violation | Impact |
|--------------------|-----------|--------|
| ROOT_CLAIM slot | T-03 | Root attestation not gate-governed |
| PATTERN_CLAIM slot | T-04 | Wazn/form not gate-governed |
| BAB_CLAIM slot | T-05 | Verb stem class not gate-governed |
| MASDAR_CLAIM slot | T-06 | Masdar not gate-governed |
| DERIVATIVE_CLAIM slot | T-07 | Mushtaq claims not gate-governed |
| Conditions field in SlotGraph | T-09 | Cannot express preconditions |
| Obstacles field in SlotGraph | T-09 | Cannot express contradictions beyond BLOCKING residuals |
| Defeaters field | T-09 | No undercutting defeater representation |
| candidate_set | T-09 | No competing hypothesis enumeration |
| Ambiguity pathway (AMBIGUOUS state) | T-10 | Ambiguous parses silently collapsed |

### Summary

The bridge expresses a binary ACCEPT/BLOCK/DEFER verdict over a maximally 2-slot graph. The full expressivity of the Taaqol Slot Geometry Algebra — multi-slot trees, conditions, obstacles, defeaters, candidate sets — is unused. Root, pattern, bab, masdar, and derivative claims are carried in the bundle DTO but discarded before SlotGraph construction.
