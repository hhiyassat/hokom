# SGA Conformance Decision
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

**HEAD:** 02918a6
**TAAQOL_VENDOR_SHA:** 35381739410071ac21dd96702ecbb2acb493f90d
**Audit date:** 2026-07-21
**Previous HEAD:** ce55f7b

---

## Executive Summary

**DECISION: SGA_ENFORCEMENT_REQUIRED**

14 open violations remain after the fix in 53e7932 (V-001 RESOLVED: bridge path corrected, live Taaqol evaluation confirmed on macOS Python 3.12.4). The bridge is now structurally live on the correct runtime, but semantic completeness, trace integrity, and sort accuracy require enforcement.

---

## Live Evaluation Status

**macOS Python 3.12.4 (confirmed per problem statement):**
- active=True, kernel_loaded=True, slot_graph_created=True
- gamma_executed=True, gate_executed=True
- trace_event_count=4 per token, failure_code=None
- TAAQOL_LIVE_EVALUATIONS: 3 (liveness probe tokens: يَكْتُبُ, الْحَقُّ, مَتَى)

**Sandbox Python 3.10 (this audit environment):**
- active=False, failure_code="TAAQOL_RUNTIME_UNAVAILABLE" (expected — StrEnum requires 3.11+)
- taaqol_verdict=None for all tokens (correct fail-closed behavior)
- BOUNDARY_REOPEN check: وَلَا, فَإِنْ, الَّذِي, اللَّهُ, مَتَى all return root=None (PASS)
- WRONG_SORT check: يَسْتَطِيعُ returns word_class='ISM' (FAIL — should be FI3L)

---

## Violation Counts (Re-counted from scratch at HEAD 02918a6)

```
SEMANTIC VERDICT DISCRIMINATION:
TAAQOL_ALL_LICENSED_COLLAPSE_VIOLATIONS:   0  (fail-closed; _deferred_decision never returns LICENSED)
TAAQOL_HARDCODED_VERDICT_VIOLATIONS:       0  (verdict from TransitionState via mapping table)
GENERIC_PAYLOAD_LICENSED_VIOLATIONS:       0  (no GenericPayload; bundle is fully typed)
MISSING_SLOT_LICENSED_VIOLATIONS:          0  (gamma step 8 enforces FILLED; EMPTY → OPEN → DEFERRED)
EVIDENCELESS_LICENSED_VIOLATIONS:          0  (gate step 4 enforces evidence; empty → DEFERRED/GATE_REQUIRED)
OBSTACLE_IGNORED_VIOLATIONS:               0  (gamma step 7; bridge maps upstream BLOCK → BLOCKING residual)
VERDICT_TRACE_MISMATCH_VIOLATIONS:         1  (V-008: gate TraceEntryCandidate never appended to TraceLedger)
VERDICT_RANK_MISMATCH_VIOLATIONS:          1  (V-014: input SlotGraph rank is heuristic 2-value)

SGA VIOLATION COUNTS:
UNTYPED_SLOT_VIOLATIONS:                   1  (V-002: cell_builder phonological slots are plain dicts)
UNLICENSED_TRANSITION_VIOLATIONS:          8  (V-003: 8 SLOT_TRANS entries + word_gate 3 branches ungated)
EVIDENCELESS_ACCEPTS:                      5  (V-004: word_gate ACCEPT without EvidenceContract at pipeline layer)
MISSING_REQUIRED_SLOT_VIOLATIONS:          5  (V-005: R1/R2/R3 radical, PATTERN, BAB, MASDAR, PARADIGM slots absent from SlotGraph)
OPAQUE_BRIDGE_PAYLOAD_VIOLATIONS:          7  (V-015: typed_slots, filled_slots, unresolved_slots, candidate_set, evidence_set, conditions+obstacles+defeaters absent)
TRACE_LOSS_VIOLATIONS:                     3  (V-007: uuid4 claim_id; V-008: TraceEntryCandidate not appended; V-009: trace_ids not converted)
SILENT_CANDIDATE_SELECTIONS:               1  (V-010: no AMBIGUOUS state for multiple candidates)
RESIDUAL_LOSS_VIOLATIONS:                  2  (V-011: synthetic slots not classified as Residuals; V-012: active_residuals plain strings + typed Residual lost on output)
OWNER_DUPLICATION_VIOLATIONS:              1  (V-013: Arabic evidence classification in bridge)
WRONG_SORT_VIOLATIONS:                     1  (V-006: يَسْتَطِيعُ word_class=ISM should be FI3L — confirmed sandbox probe)
RANK_DRIFT_VIOLATIONS:                     1  (V-014: input rank heuristic not lattice-meet)
BOUNDARY_REOPEN_VIOLATIONS:               0  (confirmed: وَلَا,فَإِنْ,الَّذِي,اللَّهُ,مَتَى all return root=None)
SERIALIZATION_CONTRACT_STATUS:             CONTRACT_MISSING
ALL_LICENSED_COLLAPSE_VIOLATIONS:          0
```

---

## SGA Chain Completeness (at HEAD 02918a6)

Required: `initial_state → typed_slots → candidates → cause → condition → obstacle → evidence → defeater → verdict → effect → residuals → trace`

Present: `initial_state (✓) → typed_slots (partial ✓ at bridge, ✗ at pipeline) → candidates (✗) → cause (✗) → condition (✗) → obstacle (✓ BLOCKING residual only) → evidence (✓ at gate layer) → defeater (✗) → verdict (✓ macOS; ✗ sandbox) → effect (✗) → residuals (partial ✗) → trace (partial ✗)`

Taaqol vendor: all 10 gamma steps + 6 gate steps ALIGNED.
Hokom bridge: structurally live on macOS Python 3.12.4, but 5 of 12 chain links absent or incomplete.

---

## Remediation Tasks (ordered by severity)

### Priority 1 — CRITICAL (semantic correctness)

**T-01: WRONG_SORT** (V-006)
File: `pipeline/word_class/engine.py`
Fix: When surface token matches verbal inflected pattern (يَسْتَفْعِلُ = Form X imperfect) and final_root exists, word_class must be FI3L. Finding an ACCEPTED_MASDAR for the root does not reclassify the verb token as ISM:MASDAR.

**T-02: MISSING_REQUIRED_SLOT** (V-005)
File: `pipeline/taaqol_integration/live/bridge.py:_build_slot_graph():194-246`
Fix: Add Slot objects for RADICAL_SLOT_R1/R2/R3 (from bundle.root_claim.canonical_root), PATTERN_SLOT (bundle.wazn_claim), BAB_SLOT (bundle.form_claim), MASDAR_SLOT (bundle.masdar_claim), PARADIGM_SLOT (bundle.inflection_claim.paradigm_id).

### Priority 2 — HIGH (trace integrity)

**T-03: TRACE_LOSS / uuid4** (V-007)
File: `pipeline/taaqol_integration/claim_adapter.py:185-186`
Fix: `claim_id = 'hokom:' + hashlib.sha256(f'{surface}:{normalized}'.encode('utf-8')).hexdigest()[:16] + ':' + surface`

**T-04: TRACE_LOSS / TraceLedger** (V-008)
File: `pipeline/taaqol_integration/live/bridge.py:evaluate_hokom_claim_bundle()`
Fix: `ledger = TraceLedger()` → append `gamma_result.trace_event_candidate` → append `gate_verdict.trace_event_candidate` → store `tuple(ledger.entries)` in HokomTaaqolDecision.

**T-05: OPAQUE_BRIDGE_PAYLOAD** (V-015)
File: `pipeline/taaqol_integration/live/models.py:HokomTaaqolDecision`
Fix: Add `typed_slots`, `taaqol_trace`, `evidence_contract`, `gamma_state_typed` fields.

### Priority 3 — MEDIUM

**T-06: EVIDENCELESS_ACCEPTS** (V-004) — `pipeline/p1_atomic_structure/slot_engineering.py:word_gate():99`
**T-07: UNLICENSED_TRANSITIONS** (V-003) — `pipeline/p1_atomic_structure/slot_engineering.py:23-32`
**T-08: RANK_DRIFT** (V-014) — `pipeline/taaqol_integration/live/bridge.py:281-285`
**T-09: OWNER_DUPLICATION** (V-013) — `pipeline/taaqol_integration/live/bridge.py:_build_evidence_contract():329-342`
**T-10: UNTYPED_SLOT** (V-002) — `pipeline/p1_atomic_structure/cell_builder.py`
**T-11: SILENT_CANDIDATE_SELECTION** (V-010) — `pipeline/taaqol_integration/live/bridge.py:_build_slot_graph()`
**T-12: RESIDUAL_LOSS** (V-011, V-012) — `cell_builder.py` + `hokom_pipeline.py` + `claim_adapter.py:74`
**T-13: TRACE_LOSS** (V-009) — `pipeline/taaqol_integration/claim_adapter.py:87-93`
**T-14: SERIALIZATION** — Add `HokomTaaqolDecision.from_dict()` + round-trip test

---

## Taaqol Vendor: ALIGNED

The Taaqol vendor (`vendor/Taaqol-GPT/src/taaqqul_slot_geometry/`) is constitutionally correct:
- Gamma: total, pure, ordered 10-step closure ✓
- TransitionGate: cause+condition+obstacle+evidence+defeater all present ✓
- TraceLedger: append-only, typed, purity-guarded ✓
- RankLattice: meet/join only keep or lower ✓
- ResidualPolicy: typed, ordered, ceiling computed correctly ✓
- EvidenceContract: typed sources, single-source ceiling enforced ✓
- No Arabic morphology in Taaqol ✓

TAAQOL VENDOR SGA VIOLATIONS: 0
