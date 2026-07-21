# Stage Dependency Plan — HOKOM-TAAQOL-SLOT-GEOMETRY-CONSTITUTIONAL-IMPLEMENTATION

## Stage 0 (Complete): Baseline and Mapping
Output: reports/sga_implementation/{baseline.md, field_to_slot_mapping.csv, ownership_matrix.csv, gap_inventory.json}
Blockers found: NONE

## Stage 1 (This run): Typed Slot Foundation
Creates: pipeline/sga/contracts.py, tests/sga/test_contracts.py
Closes gaps: SlotId, SlotSort, SlotState, TypedSlot, CandidateSet, EvidenceReference,
             HokomResidualRecord, DomainTransitionLicense, ClaimProfile, HokomClaimBundle
Requires: None (pure Python, no Taaqol import)
Python compat: 3.10+ (str,Enum; no StrEnum)
Commits: 4 atomic

## Stage 2 (Future): Bridge Slot Projection
Adds ROOT_CLAIM, PATTERN_CLAIM, BAB_CLAIM slots to _build_slot_graph()
Closes: T-03, T-04, T-05, T-06, T-07
Requires: Stage 1 contracts.py

## Stage 3 (Future): Typed Phonological Slots
Creates PhonologicalSlot frozen dataclass
Wires syllabify() output to TypedSlot
Closes: T-02, T-08

## Stage 4 (Future): Claim ID Determinism
Replaces uuid4() in claim_adapter with compute_claim_key()
Closes: T-11

## Stage 5 (Future): AMBIGUOUS State Wiring
Wires functional_collision=True → AMBIGUOUS SlotState
Closes: T-10

## Stage 6 (Future): Trace Typing
Structured HokomTaaqolTraceEvent (gamma/gate state typed fields)
Closes: T-12

## Stage 7 (Future): Serialization Closure
Adds HokomTaaqolDecision.from_dict()
Closes: T-13, T-14
