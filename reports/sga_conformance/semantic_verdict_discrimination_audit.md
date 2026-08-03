# Semantic Verdict Discrimination Audit
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

**HEAD:** 02918a6  
**TAAQOL_VENDOR_SHA:** 35381739410071ac21dd96702ecbb2acb493f90d  
**Audit date:** 2026-07-21  
**Runtime:** STATIC_ANALYSIS (Python 3.10 sandbox — Taaqol import deferred; live results from macOS Python 3.12.4 per problem statement)

---

## Part 1: Taaqol Verdict Vocabulary

The Taaqol verdict vocabulary exposed to the bridge is **LICENSED / DEFERRED / BLOCKED / RESIDUAL**.

These are produced by two distinct mechanisms:

### 1.1 Gate-layer verdicts (from TransitionState → _map_transition_state_to_verdict)

TransitionState has five values: APPROVED, DEFERRED, BLOCKED, REJECTED, FORBIDDEN_LEAP.
Bridge mapping (bridge.py:355–364):

| TransitionState   | Taaqol Verdict |
|-------------------|----------------|
| APPROVED          | LICENSED       |
| DEFERRED          | DEFERRED       |
| BLOCKED           | BLOCKED        |
| REJECTED          | BLOCKED        |
| FORBIDDEN_LEAP    | BLOCKED        |

So the gate layer can produce: LICENSED, DEFERRED, or BLOCKED. It cannot produce RESIDUAL.

### 1.2 Composition-layer verdicts (from compose_effective_verdict)

RESIDUAL only emerges from `compose_effective_verdict()` (decision_composition.py) when:
- upstream_verdict is 'RESIDUAL' AND taaqol does not BLOCK
- This is NOT a Taaqol gate verdict; it is a Hokom composition verdict

---

## Part 2: Conditions for Each Verdict

### LICENSED
**Gate path:** gamma() → MINIMALLY_CLOSED or PERFORATED_CLOSED, then gate() → APPROVED.

**Required conditions (all must hold):**
1. Center.identity_claim is non-empty (gamma step 1)
2. Center.trace_ref.anchor is non-empty (gamma step 2)
3. boundary.domain is non-empty (gamma step 3a)
4. boundary.scope is non-empty (gamma step 3b)
5. No slot has value_state = BROKEN (gamma step 4)
6. output_boundary.output_layer <= output_boundary.declared_layer (gamma step 5)
7. No residual is HIDDEN_FORBIDDEN or invisible (gamma step 6)
8. No residual has kind = BLOCKING (gamma step 7)
9. All required slots are FILLED (gamma step 8)
10. graph.rank <= ResidualPolicy.ceiling(residuals) (gamma step 9)
11. Evidence surface is non-empty (gate step 4)
12. No forbidden straight-line registry match (gate step 2)
13. No ungated rank promotion (gate step 3)

**In bridge.py:** LICENSED is produced when domain_directive = 'ACCEPT', primary_slot is FILLED, evidence_ids is non-empty, no active blocking residuals, and the graph passes all gamma checks.

**Test claim (REQUIRES_LIVE_RUNTIME):**
```python
bundle = HokomLinguisticClaimBundle(
    claim_id='hokom:test:يَكْتُبُ',
    domain_directive='ACCEPT',
    evidence_ids=('root_catalog:kataba', 'structural:phone_count'),
    active_residuals=(),
    ...
)
```
Expected: taaqol_verdict='LICENSED', effective_verdict='LICENSED'

---

### DEFERRED
**Gate paths:**
- gamma() → OPEN (required slot not FILLED, i.e. domain_directive != ACCEPT) → gate returns DEFERRED
- gate step 4: evidence surface is empty → DEFERRED/GATE_REQUIRED
- Infrastructure failure: ImportError, SlotGraph construction error, Gamma error, Gate error → DEFERRED (fail-closed)
- Clitic-only token (no lexical host) → DEFERRED
- Upstream Hokom verdict is DEFER

**In bridge.py:** DEFERRED is produced by `_deferred_decision()` on any failure, or by gate returning DEFERRED when primary_slot is EMPTY (domain_directive != ACCEPT) or evidence is absent.

**Test claim (REQUIRES_LIVE_RUNTIME):**
```python
bundle = HokomLinguisticClaimBundle(
    claim_id='hokom:test:مَتَى',
    domain_directive='DEFER',      # primary_slot → EMPTY
    evidence_ids=('structural:phone_count',),
    active_residuals=(),
    ...
)
```
Expected: taaqol_verdict='DEFERRED', effective_verdict='DEFERRED'

Also: empty evidence case:
```python
bundle = HokomLinguisticClaimBundle(
    claim_id='hokom:test:test_empty_evidence',
    domain_directive='ACCEPT',
    evidence_ids=(),               # empty → gate step 4 → DEFERRED/GATE_REQUIRED
    active_residuals=(),
    ...
)
```
Expected: taaqol_verdict='DEFERRED', reason_code='GATE_REQUIRED'

---

### BLOCKED
**Gate paths:**
- gamma() → BLOCKED (step 7: any residual has kind=BLOCKING) → gate returns BLOCKED
- gamma() → INVALID (steps 1-6 fail) → gate returns REJECTED → mapped to BLOCKED
- gamma() → FORBIDDEN_LEAP (step 5 fails) → gate returns FORBIDDEN_LEAP → mapped to BLOCKED
- Upstream Hokom verdict is 'BLOCK'/'BLOCKED' → bridge adds BLOCKING residual → gamma step 7 → BLOCKED
- compose_effective_verdict: upstream BLOCKED → always BLOCKED

**In bridge.py:** BLOCKED is produced when:
- domain_directive = 'BLOCK'/'BLOCKED' → `Residual(name='hokom:upstream_block', kind=ResidualKind.BLOCKING)` appended → gamma step 7 → BLOCKED
- active_residuals contains 'block:*' prefix codes → BLOCKING residuals → BLOCKED
- compose_effective_verdict: upstream BLOCKED → BLOCKED regardless of taaqol verdict

**Test claim (REQUIRES_LIVE_RUNTIME):**
```python
bundle = HokomLinguisticClaimBundle(
    claim_id='hokom:test:block_test',
    domain_directive='BLOCK',      # → BLOCKING residual added → gamma BLOCKED
    evidence_ids=('structural:phone_count',),
    active_residuals=(),
    ...
)
```
Expected: taaqol_verdict='BLOCKED', effective_verdict='BLOCKED'

---

### RESIDUAL
**This is a composition-layer verdict only.** It cannot be produced by TransitionGate alone.

**Conditions:**
- upstream_verdict = 'RESIDUAL' (Hokom emits RESIDUAL verdict)
- taaqol does not BLOCK

STATIC_ANALYSIS: Hokom pipeline currently produces 'RESIDUAL' upstream verdict in some cases (constitutional_contracts.py line 54 confirms RESIDUAL as a valid OperationalStatus). When this occurs and taaqol_verdict is LICENSED or DEFERRED, compose_effective_verdict returns 'RESIDUAL'.

**Test claim (REQUIRES_LIVE_RUNTIME):**
```python
# Requires a Hokom token that produces verdict='RESIDUAL'
# Then compose_effective_verdict('RESIDUAL', 'LICENSED') → 'RESIDUAL'
# compose_effective_verdict('RESIDUAL', 'BLOCKED') → 'BLOCKED'
```

**Note:** RESIDUAL as a Taaqol verdict is a Hokom composition artifact, not a Taaqol gate verdict. Taaqol's TransitionState has no RESIDUAL value.

---

## Part 3: Four Test Claims

All four test claims would be constructed via `bundle_from_hokom_result()` and submitted to `evaluate_hokom_claim_bundle()`.

### Claim 1: LICENSED case
```python
result = {
    'original': 'يَكْتُبُ',
    'verdict': 'ACCEPT',
    'evidence_ids': ('root_catalog:kataba_trilateral', 'structural:phone_count'),
    'active_residuals': (),
    ...
}
bundle = bundle_from_hokom_result(result)
decision = evaluate_hokom_claim_bundle(bundle)
# REQUIRES_LIVE_RUNTIME: expected taaqol_verdict='LICENSED'
```

### Claim 2: DEFERRED case
```python
result = {
    'original': 'مَتَى',
    'verdict': 'DEFER',
    'evidence_ids': ('structural:phone_count',),
    'active_residuals': (),
    ...
}
bundle = bundle_from_hokom_result(result)
decision = evaluate_hokom_claim_bundle(bundle)
# REQUIRES_LIVE_RUNTIME: expected taaqol_verdict='DEFERRED' (primary_slot=EMPTY → gamma OPEN → gate DEFERRED)
```

### Claim 3: BLOCKED case
```python
result = {
    'original': 'OPERATOR_TOKEN',
    'verdict': 'BLOCK',
    'evidence_ids': ('structural:phone_count',),
    'active_residuals': (),
    ...
}
bundle = bundle_from_hokom_result(result)
decision = evaluate_hokom_claim_bundle(bundle)
# REQUIRES_LIVE_RUNTIME: expected taaqol_verdict='BLOCKED' (BLOCKING residual → gamma BLOCKED → gate BLOCKED)
```

### Claim 4: RESIDUAL case
```python
result = {
    'original': 'الْحَقُّ',
    'verdict': 'ACCEPT',
    'evidence_ids': ('root_catalog:haqqa', 'structural:phone_count'),
    'active_residuals': ('bab:mujarrad:imperfect_vowel_not_known', 'sami3i_required'),
    ...
}
bundle = bundle_from_hokom_result(result)
decision = evaluate_hokom_claim_bundle(bundle)
# REQUIRES_LIVE_RUNTIME: expected taaqol_verdict='LICENSED' or 'DEFERRED'
# For effective_verdict='RESIDUAL', upstream must be 'RESIDUAL': 
# compose_effective_verdict('RESIDUAL', 'LICENSED') → 'RESIDUAL'
```

NOTE_REQUIRES_LIVE_RUNTIME: All four claims above were constructed from static analysis only. Actual execution requires Python 3.11+ runtime (macOS confirmed: active=True for 3 tokens from run_taaqol_liveness_contracts). Distinct verdicts observed in macOS live run: LICENSED confirmed (gate_executed=True, active=True). DEFERRED confirmed (infrastructure path via sandbox). BLOCKED and RESIDUAL require specific test inputs not yet in the canonical gate probe set.

---

## Part 4: Violation Counter Analysis

### TAAQOL_ALL_LICENSED_COLLAPSE_VIOLATIONS: 0
- `_deferred_decision()` explicitly sets taaqol_verdict='DEFERRED', never 'LICENSED' (bridge.py:114)
- No failure path returns LICENSED
- ImportError → DEFERRED (bridge.py:460-469)
- SlotGraph error → DEFERRED (bridge.py:538-547)
- Gamma error → DEFERRED (bridge.py:573-582)
- Evidence error → DEFERRED (bridge.py:605-614)
- Gate error → DEFERRED (bridge.py:651-660)
- taaqol_runtime dict has no LICENSED fallback path

### TAAQOL_HARDCODED_VERDICT_VIOLATIONS: 0
- Verdict derives from gate_state_str which comes from Taaqol TransitionState (APPROVED, DEFERRED, BLOCKED, REJECTED, FORBIDDEN_LEAP)
- `_map_transition_state_to_verdict` is a lookup table over legitimate Taaqol values
- No literal 'LICENSED' assignment outside the mapping table
- The string 'LICENSED' appears in bridge.py only in: docstring, fail-closed comment, `if _UP in ('ACCEPT', 'LICENSED')` (checking input directive), and `rank = Rank.LICENSED` (evidence rank value, not verdict)

### GENERIC_PAYLOAD_LICENSED_VIOLATIONS: 0
- No GenericPayload concept in the bridge
- HokomLinguisticClaimBundle is a fully typed, schema-declared dataclass
- No fallback to generic/untyped payload that could become LICENSED without contract

### MISSING_SLOT_LICENSED_VIOLATIONS: 0
- Gamma step 8: if any required slot is not FILLED → ClosureState.OPEN → gate returns DEFERRED
- primary_slot is required=True; it is FILLED only when domain_directive in ('ACCEPT', 'LICENSED')
- DEFER/BLOCK/NOT_APPLICABLE → primary_slot = EMPTY → gamma OPEN → gate DEFERRED → cannot reach LICENSED

### EVIDENCELESS_LICENSED_VIOLATIONS: 0
- Gate step 4 (transition_gate.py:473-479): `if not evidence.sources: return DEFERRED/GATE_REQUIRED`
- An empty EvidenceContract (evidence_ids=[]) → evidence.sources=() → gate returns DEFERRED, never LICENSED
- This is structurally enforced: the gate cannot skip step 4

### OBSTACLE_IGNORED_VIOLATIONS: 0
- Gamma step 7 (gamma.py:200-207): if any residual.kind is BLOCKING → ClosureState.BLOCKED → gate BLOCKED
- Bridge maps upstream BLOCK directive to BLOCKING residual (bridge.py:250-257)
- Bridge maps 'block:*' active_residual codes to ResidualKind.BLOCKING (bridge.py:260-264)
- BLOCKING residuals always produce BLOCKED verdict; they cannot be bypassed

### VERDICT_TRACE_MISMATCH_VIOLATIONS: 1
- Gamma returns GammaResult with trace_event_candidate (TraceEntryCandidate) — never appended to TraceLedger (V-008)
- Gate returns TransitionVerdict with trace_event_candidate — never appended to TraceLedger (V-008)
- Bridge constructs its own HokomTaaqolTraceEvent list (plain strings)
- The verdict IS recorded via trace events but not in the constitutional Taaqol trace format
- COUNT: 1 (bridge trace exists but uses non-constitutional format, losing gamma/gate trace split)

### VERDICT_RANK_MISMATCH_VIOLATIONS: 1
- Input SlotGraph rank is heuristic (Rank.HYPOTHESIS for ACCEPT, Rank.CANDIDATE for DEFER/BLOCK)
- NOT derived from meet(evidence_rank, root_confidence_rank) via RankLattice
- Gate step 5 correctly computes: granted = RankLattice.meet(evidence.evidence_rank, input_graph.rank, gate_rank, ceiling)
- But the input_graph.rank entering the meet is heuristic → granted_rank may not reflect true evidence chain
- Example: ACCEPT with very weak evidence (Rank.CANDIDATE evidence) → meet(CANDIDATE, HYPOTHESIS, STRONG, CERTIFICATE) = CANDIDATE. Correct. But if input rank were derived from evidence meet, input would already be CANDIDATE or lower.
- COUNT: 1 (input rank heuristic; does not drift the verdict but drifts the rank computation path)

---

## Part 5: Discrimination Test Summary

The four-verdict space is semantically discriminated by the bridge:

| Verdict   | Source               | Blocked by gate? | Notes |
|-----------|----------------------|------------------|-------|
| LICENSED  | TransitionState.APPROVED | No          | Requires FILLED required slot + non-empty evidence + gamma closure |
| DEFERRED  | TransitionState.DEFERRED or failure | No  | Empty required slot, empty evidence, or infrastructure failure |
| BLOCKED   | TransitionState.BLOCKED/REJECTED/FORBIDDEN_LEAP | Yes | BLOCKING residual or gamma INVALID/FORBIDDEN_LEAP |
| RESIDUAL  | compose_effective_verdict only | N/A        | Upstream Hokom RESIDUAL + Taaqol non-BLOCK |

LICENSED cannot arise from: infrastructure failure, empty evidence, missing required slot, or BLOCKING residual.
BLOCKED cannot be overridden: compose_effective_verdict rules 1 and 4 prevent BLOCKED from being upgraded.
RESIDUAL is not a gate state: it is a composition-layer concept only.
