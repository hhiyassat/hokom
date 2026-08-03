# SGA Conformance Audit — Identity and Trace
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### Claim Identity (Violation T-11)

**Expected**: `claim_id` is a deterministic content-hash (e.g. SHA-256 of normalized input fields).

**Actual** (claim_adapter.py):
```python
claim_id=f'hokom:{token_id or uuid.uuid4().hex[:12]}:{surface}'
token_id=token_id or uuid.uuid4().hex[:16]
```

- `uuid4()` is non-deterministic: two calls with identical inputs yield different IDs
- `claim_id` is NOT reproducible across runs
- `HokomClaimProjection` docstring says "deterministic from content hash" — this is a documentation-code mismatch
- `models.py` line 50 comment: `# deterministic from content hash` — INCORRECT

### Trace Architecture (Violation T-12)

**HokomTaaqolTraceEvent** (`models.py` lines 70–77):

```python
@dataclass(frozen=True)
class HokomTaaqolTraceEvent:
    step: str
    component: str      # 'SlotGraph' | 'Gamma' | 'TransitionGate'
    input_digest: str
    output: str         # opaque string — NOT structured
    strict_mode: bool
```

The `output` field is an opaque string. There is no typed representation of:
- Gamma's ClosureState (embedded in output string)
- TransitionGate's TransitionVerdict (embedded in output string)
- SlotGraph state snapshot

**TraceLedger** (vendor): `TraceEntryCandidate` is a frozen dataclass with PR-6 split:
- `consulted_gamma_state` (separate from)
- `gate_transition_state`

The HOKOM trace event does not mirror this split.

### Trace Ledger

`vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/trace_ledger.py`:
- TraceLedger is append-only
- TraceEntryCandidate is a frozen dataclass
- PR-6 split: consulted_gamma_state vs gate_transition_state are separate fields

### Liveness Contract (_rt dict)

The bridge correctly populates:
- `active`: bool — True iff full chain executed
- `kernel_loaded`: bool
- `slot_graph_created`: bool
- `gamma_executed`: bool
- `gate_executed`: bool
- `trace_event_count`: int
- `failure_code`: str or None
- `failure_detail`: str or None

This is carried in `HokomTaaqolDecision.taaqol_runtime` (Optional[dict]).

### Test Coverage

- `test_repo_root_resolves_correctly`: PASSED — confirms parents[3] in bridge source
- `test_vendor_sha_matches_pin`: PASSED — vendor pin matches 35381739410071ac21dd96702ecbb2acb493f90d
- `test_runtime_failure_is_not_semantic_defer`: PASSED
- `test_no_silent_fallback`: PASSED
- `test_live_pipeline_integration`: SKIPPED (requires Python 3.11+)
