# SGA Constitutional Closure Report
**Stage**: HOKOM-TAAQOL-SGA-CONSTITUTIONAL-CONVERGENCE-01
**Final HEAD**: ee418b6
**Closed**: 2026-07-22

## Tasks Closed

### T-02: Typed Phonological Caller Boundary
- **File**: `pipeline/p1_atomic_structure/phonological_slot.py`
- **File**: `pipeline/p1_atomic_structure/cell_builder.py`
- `wrap_syllabify_output()` handles the actual syllabify() dict format (`surface`, `pattern`, `gate`, `violations`, `status_at_close`, `close_reason`, `saturation_reason`)
- `analyze_word()` now includes `typed_syllables` in return dict
- `hokom_pipeline.py` calls `wrap_syllabify_output()` and stores result in `typed_phonological_slots`
- 22 tests in `tests/sga/test_phonological_slot.py`
- Commit: **24eaa81**

### T-03: HokomClaimBundle at Bridge Boundary
- **File**: `pipeline/taaqol_integration/live/bridge.py`
- **File**: `hokom_pipeline.py`
- `evaluate_sga_bundle(sga_bundle: HokomClaimBundle)` added as `SGA_CANONICAL_ENTRYPOINT`
- Rejects non-HokomClaimBundle with DEFERRED + OPAQUE_BRIDGE_INPUT reason code
- `hokom_pipeline.py` builds SGA bundle via `build_claim_bundle()` and calls `evaluate_sga_bundle()`
- `test_only_one_canonical_entrypoint` updated to allow exactly two entrypoints
- Commit: **a8751a6**

### T-09: H11-H15 Typed Adapters
- **File**: `pipeline/sga/adapters.py`
- Added: `adapt_bab()`, `adapt_masdar()`, `adapt_derivatives()`, `adapt_morphosyntax()`, `adapt_lemma_paradigm()`
- `build_claim_bundle()` now assembles 23 typed slots (H0-H15)
- `test_build_claim_bundle_slot_count` updated: 15 → 23
- Commit: **c1cfbf7**

### T-10: Preserve Ambiguous Candidate Sets
- **File**: `pipeline/sga/adapters.py`
- **File**: `pipeline/taaqol_integration/live/bridge.py`
- When `root_candidate` is a list with >1 entries: R1/R2/R3 remain UNKNOWN, `ROOT_CANDIDATE_SET` gets all candidates with `selected=None`, `HokomResidualRecord(code=AMBIGUOUS_CANDIDATE_SET)` emitted
- Bridge `_build_slot_graph()` passes AMBIGUOUS typed slots with all candidates in `allowed_potentials`, never picks first silently
- T-10 AMBIGUOUS residuals injected into `residuals_list` AFTER it is initialized (NameError bug fixed)
- Commit: **88f09ff**

## Test Suite Status (workspace Python 3.10.12)

- **5863 passed, 55 skipped, 132 subtests passed**
- **12 pre-existing failures** — all Python version checks requiring 3.11+/3.12.4
- **0 new failures** introduced by T-02/T-03/T-09/T-10

## Violation Counter Final State

| Counter | Value |
|---------|-------|
| UNTYPED_PHONOLOGICAL_CALLER_VIOLATIONS | 0 |
| RAW_BRIDGE_CALLER_VIOLATIONS | 0 |
| CLAIM_BUNDLE_BYPASS_VIOLATIONS | 0 |
| OPAQUE_BRIDGE_INPUT_VIOLATIONS | 0 |
| H11_ADAPTER_VIOLATIONS | 0 |
| H12_ADAPTER_VIOLATIONS | 0 |
| H13_ADAPTER_VIOLATIONS | 0 |
| H14_ADAPTER_VIOLATIONS | 0 |
| H15_ADAPTER_VIOLATIONS | 0 |
| AMBIGUITY_COLLAPSE_VIOLATIONS | 0 |
| AMBIGUOUS_CANDIDATE_SET_RESIDUALS_DROPPED | 0 |
| CLAIM_KEY_NONDETERMINISM_VIOLATIONS | 0 |
| **BRIDGE_EXPRESSIVITY_STATUS** | **FULL** |
