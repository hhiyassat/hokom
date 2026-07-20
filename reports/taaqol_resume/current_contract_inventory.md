# Current Contract Inventory — HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME

Generated: 2026-07-20
Starting HEAD: b992d7e

## 1. HokomLinguisticClaimBundle construction

File: `pipeline/taaqol_integration/claim_adapter.py`
Function: `bundle_from_hokom_result()` line 37
Called from: `hokom_pipeline.py` line 539

## 2. claim_adapter call site

File: `hokom_pipeline.py` line 537–540
```python
from pipeline.taaqol_integration.claim_adapter import bundle_from_hokom_result
from pipeline.taaqol_integration.live.bridge import evaluate_hokom_claim_bundle
_claim_bundle = bundle_from_hokom_result(_hokom_result_partial)
_taaqol_decision = evaluate_hokom_claim_bundle(_claim_bundle)
```

## 3. evaluate_hokom_claim_bundle() call site

File: `hokom_pipeline.py` line 540

## 4. _build_slot_graph() Center construction

File: `pipeline/taaqol_integration/live/bridge.py`
Function: `_build_slot_graph()` (line 112)
Center built at approximately line 165:
```python
center = Center(
    identity_claim=anchor,
    domain='hokom_morphology',
    scope=morphological_center,   # FIXED: was 'surface' (= original_surface)
    trace_ref=trace_ref,
)
```
`morphological_center` = `bundle.segment_host or bundle.morphology_surface or original_surface`

## 5. Center.scope field (AFTER fix)

`Center.scope = bundle.segment_host` (canonical morphological host from P0 segmentation)
Previously: `Center.scope = bundle.original_surface` (WRONG — full token with clitics)

## 6. SegmentBundle in claim bundle

YES — `HokomLinguisticClaimBundle.segment_bundle` (Amendment No. 2+3)
Also exposed as individual fields:
- `segment_host`, `segment_proclitics`, `segment_definite_article`
- `segment_enclitics`, `segment_clitic_only`, `segment_verdict`

## 7. Proclitics/article/enclitics reaching bridge

- proclitics: YES — `bundle.segment_proclitics` (Amendment No. 3)
- article: YES — `bundle.segment_definite_article` (Amendment No. 3)
- enclitics: YES — `bundle.segment_enclitics` (Amendment No. 3)

## 8. host=None handling

`evaluate_hokom_claim_bundle()` has an explicit clitic-only gate (before SlotGraph build):
- `morphology_blocked=True` OR `segment_clitic_only=True` → immediate DEFERRED return
- `taaqol_center_scope=None` in that decision
- reason_codes include `('SEGMENTATION_NO_LEXICAL_HOST', ...)`
- Effective verdict: DEFERRED (never LICENSED)

## 9. original_surface in bridge

`original_surface` appears as:
- `_original_surface` local variable (provenance only)
- Stored in `HokomTaaqolTraceEvent.output` for traceability
- Used in `anchor = claim_id or f'hokom:{original_surface}'` (TraceRef anchor)
- NEVER used as `Center.scope` (the core invariant)

## 10. effective_verdict composition

`compose_effective_verdict(upstream_verdict, taaqol_verdict)` in `decision_composition.py`
Monotonic: BLOCK + anything → BLOCKED; DEFER + anything → DEFERRED unless taaqol=LICENSED and upstream=ACCEPT

## 11. Live call count

On Python 3.10 (Linux container): DEFERRED after import failure — SlotGraph, Gamma, TransitionGate NOT called.
On Python 3.11+ (macOS): 1 × SlotGraph, 1 × Gamma, 1 × TransitionGate per token.
Architecture: sequential, no parallelism.
