# SGA Conformance Audit — Phonological Slots
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### Violation T-02: UNTYPED_SLOT

**File**: `pipeline/p1_atomic_structure/cell_builder.py`

`syllabify()` returns `list[dict]` where each dict has keys:
- `surface`: str
- `pattern`: str (CV, CVV, CVC, etc.)
- `gate`: str (ACCEPT/DEFER/BLOCK)
- `violations`: list
- `status_at_close`: str
- `close_reason`: str
- `saturation_reason`: str

**Phone class**: plain Python class — NOT a frozen dataclass.

### Non-Conformance

The phonological slot representation is entirely disconnected from taaqqul_slot_geometry:
- Not a `SlotGraph` or `Slot` instance
- `SlotState` enum is not used (EMPTY/FILLED/BROKEN)
- `gate` values are plain strings, not TransitionGate verdicts
- No EvidenceContract governs slot transitions
- No RankLattice rank is assigned
- No residuals are accumulated via ResidualKind

### Valid Slot Patterns

`pipeline/p1_atomic_structure/slot_engineering.py`:
```python
VALID_S = {'CV', 'CVV', 'CVC', 'CVVC', 'CVCC', 'CVVCC'}
```

This set is correct per Arabic syllable structure constraints and is used internally for gate decisions, but patterns are never registered in a Taaqol SlotGraph.

### Segment Host Invariant

`hokom_pipeline.py` enforces: `segment_host != original_surface` (clitic-stripping occurred). CRA (`canonical_radical_accounting.py`) operates on `segment_host` not `pre_root.host_surface`. These invariants are sound but phonological slot typing is still absent.

### Remediation

1. Define `PhonologicalSlot` as a frozen dataclass aligned with taaqqul_slot_geometry Slot interface
2. Replace `syllabify() -> list[dict]` with `syllabify() -> list[PhonologicalSlot]`
3. Or: build a proper SlotGraph from phonological analysis and submit it through Gamma
