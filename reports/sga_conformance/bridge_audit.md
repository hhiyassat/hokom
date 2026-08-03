# Bridge Audit
HEAD: ce55f7b
Bridge: pipeline/taaqol_integration/live/bridge.py
Entrypoint: evaluate_hokom_claim_bundle()

## Required Bridge Contract (SGA)

The bridge must:
1. Convert Hokom linguistic slots to Taaqol typed slots — never to opaque string
2. Preserve: claim_kind, center_scope, typed_slots, filled_slots, unresolved_slots, candidate_set, evidence_set, rank, conditions, obstacles, defeaters, residuals, source_engine, provenance, trace
3. Not perform any Arabic morphology itself
4. Not make routing decisions that belong to Hokom
5. Not make constitutional decisions that belong to Taaqol

## _REPO_ROOT BUG (CRITICAL)

**File**: pipeline/taaqol_integration/live/bridge.py:22
**Code**: `_REPO_ROOT = Path(__file__).parent.parent.parent`
**Actual value at HEAD**: `/sessions/.../hokom/pipeline/` (NOT repo root)
**Required value**: `/sessions/.../hokom/` (4 parents up, not 3)
**Effect**: `vendor_src = pipeline/vendor/Taaqol-GPT/src` does not exist.
**Consequence**: Every call to `evaluate_hokom_claim_bundle()` fails at import with `ImportError: No module named 'taaqqul_slot_geometry'`. The fail-closed handler catches it and returns `DEFERRED:TAAQOL_RUNTIME_UNAVAILABLE`. The bridge has NEVER successfully executed the SlotGraph→Gamma→Gate pipeline at HEAD ce55f7b.
**Confirmed by**: Runtime probe — all 6 test tokens return taaqol_effective_verdict='DEFERRED' with reason_codes=('TAAQOL_RUNTIME_UNAVAILABLE', 'ImportError:No module named taaqqul_slot_geometry').
**Fix**: Line 22: `_REPO_ROOT = Path(__file__).parent.parent.parent.parent`

## _build_slot_graph() — Slot Conversion Audit

### What it DOES produce (typed, SGA-compatible):
- `Center(identity_claim=claim_id, domain='hokom_morphology', scope=morphological_center, trace_ref=TraceRef(anchor=claim_id, kind='hokom_claim'))` — ALIGNED
- `SlotBoundary(domain='hokom_morphology', scope='arabic_morphology', refusal_codes=(FailureCode.BOUNDARY_MISSING,))` — ALIGNED (but single refusal code; should include more FailureCodes)
- `Slot(name='domain_claim', value_state=SlotState.FILLED, ...)` when ACCEPT — ALIGNED structure
- `EntryBoundary(declared_entry_kind='HOKOM_MORPHOLOGICAL_ANALYSIS', ...)` — ALIGNED
- `OutputBoundary(declared_layer=Layer.TEXT_ENTRY, output_layer=Layer.TEXT_ENTRY)` — ALIGNED
- `GenerationSource.DECLARED_ENTRY` — ALIGNED
- `Residual(name=..., kind=..., visible=True)` objects from active_residuals — ALIGNED structure (heuristic content)

### What it DOES NOT produce (violations):
- RADICAL_SLOT_R1/R2/R3 from final_root — MISSING
- PATTERN_SLOT from final_wazn — MISSING
- BAB_SLOT from final_form — MISSING
- MASDAR_SLOT from final_masdar — MISSING
- PARADIGM_SLOT from phase5_result — MISSING
- DERIVATIVE_SLOT from phase4d_result (mushtaqat) — MISSING
- Candidate set (multiple root candidates) — MISSING; only verdict string forwarded
- Per-slot cause/condition/obstacle/defeater — all absent (inherited from TransitionGate)

### Routing decisions inside bridge (OWNER_DUPLICATION violation):
- `if _UP in ('ACCEPT', 'LICENSED'): primary_value = 'ACCEPT'` — morphological routing in bridge
- `if _UP in ('BLOCK', 'BLOCKED'): residuals_list.append(Residual(name='hokom:upstream_block', kind=ResidualKind.BLOCKING, ...))` — domain decision in bridge

## _build_evidence_contract() — Evidence Conversion Audit

### Positive:
- Produces properly typed `EvidenceSource` objects with name, kind, rank, trace_ref
- EvidenceContract is validated by Taaqol __post_init__ on construction

### Violations:
- **OWNER_DUPLICATION**: Rank assignment by Arabic morphological term matching:
  ```python
  if any(k in eid_str for k in ('root_catalog', 'corpus', 'lexical')): rank = Rank.STRONG
  elif any(k in eid_str for k in ('wazn', 'bab', 'form')): rank = Rank.LICENSED
  elif any(k in eid_str for k in ('masdar', 'mushtaq', 'inflection')): rank = Rank.HYPOTHESIS
  ```
  This is Arabic morphological classification logic in the bridge.
- **RANK_DRIFT**: All EvidenceSource.trace_ref uses `TraceRef(anchor=claim_id, kind='evidence')` — the same claim_id for all evidence sources. Evidence from root_catalog and evidence from wazn catalog should have distinct trace anchors.

## HokomTaaqolDecision — Output Audit

### Required fields present:
- bridge_id, taaqol_commit, hokom_commit, strict_mode, fail_closed ✓
- gamma_result (string), transition_gate_result (string) — present but OPAQUE (strings not typed ClosureState/TransitionState)
- taaqol_verdict ('LICENSED'|'DEFERRED'|'BLOCKED') ✓
- reason_codes (tuple of strings) ✓
- residuals (tuple of strings — UNTYPED) ✗
- trace (tuple of HokomTaaqolTraceEvent — OPAQUE, not TraceEntryCandidate) ✗
- taaqol_center_scope (morphological center string) ✓

### Required fields ABSENT:
- typed_slots: tuple[Slot, ...] — not in HokomTaaqolDecision
- filled_slots — not present
- unresolved_slots — not present
- candidate_set — not present
- evidence_set (typed EvidenceContract) — not present
- conditions, obstacles, defeaters from gate — not present
- slot_graph_digest is non-deterministic (uses uuid4-based claim_id as input)

### OPAQUE_BRIDGE_PAYLOAD count: 7 (typed_slots, filled_slots/unresolved_slots, candidate_set, evidence_set, conditions, obstacles, defeaters)

## claim_adapter.py — Bundle Construction Audit

### Non-deterministic token_id:
- `claim_id = f'hokom:{token_id or uuid.uuid4().hex[:12]}:{surface}'` — non-deterministic
- `token_id = token_id or uuid.uuid4().hex[:16]` — non-deterministic
- Two calls with same input produce different claim_ids (confirmed by probe)
- This propagates into TraceRef.anchor making all trace entries non-reproducible

### Correct: evidence_ids collection (phase-level evidence aggregation) ✓
### Correct: domain_directive mapping ('ACCEPT'→'ACCEPT', 'BLOCK'→'BLOCK') ✓
### Correct: segment_host propagation for morphological center ✓

## compose_effective_verdict() — Verdict Composition Audit

Monotonic composition rule: upstream BLOCK cannot be upgraded. ALIGNED.
Seven canonical cases correctly implemented. ALIGNED.
Pure Python (no Taaqol imports) — correct separation. ALIGNED.

## Arabic Morphology in Bridge: OWNER_DUPLICATION

Taaqol vendor: ZERO Arabic morphology logic (confirmed by full vendor audit).
Hokom core pipeline: ZERO Taaqol constitutional logic.
Bridge: 3 instances of Arabic morphological term matching for rank assignment and routing.
These 3 instances should be moved to Hokom domain (pre-rank evidence before bridge handoff).

## Verdict

The bridge PARTIALLY satisfies the architectural contract:
- Constitutional typing (SlotGraph, Slot, Residual, EvidenceContract) ✓
- Fail-closed behavior ✓
- Monotonic verdict composition ✓
- Center scope invariant (segment_host, not original_surface) ✓

The bridge FAILS on:
- Operational: _REPO_ROOT bug makes it 100% non-functional at HEAD
- Coverage: 7 of 9+ required linguistic slot sorts not expressed
- Trace: TraceLedger never used; trace is opaque strings
- Determinism: non-deterministic claim_id
- Owner separation: 3 Arabic morphology classification instances in bridge
