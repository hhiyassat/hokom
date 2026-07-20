# Clitic-Only Fail-Closed Proof — HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME

## Invariant

```
CLITIC_ONLY → DEFERRED (never LICENSED)
              center_scope = None (never original_surface)
```

## Gate Implementation

```python
# evaluate_hokom_claim_bundle() — bridge.py
if _morphology_blocked or _segment_clitic_only:
    _block_reason = (
        getattr(bundle, 'morphology_block_reason', None)
        or 'SEGMENTATION_NO_LEXICAL_HOST'
    )
    trace.append(HokomTaaqolTraceEvent(
        step='clitic_only_gate',
        output=f'DEFERRED:no_lexical_host:{_block_reason}:surface={_original_surface!r}',
    ))
    return _deferred_decision(
        reason_codes=('SEGMENTATION_NO_LEXICAL_HOST', _block_reason),
        taaqol_center_scope=None,  # explicitly None — not original_surface
    )
```

## Center Computation (guards against fallback)

```python
if _morphology_blocked or _segment_clitic_only:
    _morphological_center = None   # NEVER falls back to original_surface
else:
    _morphological_center = (
        getattr(bundle, 'segment_host', None)
        or getattr(bundle, 'morphology_surface', None)
        or _original_surface  # only when no segmentation at all
    )
```

## Canonical Clitic-Only Case

Token: بِكُمْ
- segment_host: None (clitic-only)
- segment_proclitics: ('بِ',)
- segment_enclitics: ('كُمْ',)
- segment_clitic_only: True
- morphology_blocked: True

Result (both Python 3.10 and 3.11+):
- effective_verdict: DEFERRED
- taaqol_center_scope: None
- reason_codes: ≥ 1 code (TAAQOL_RUNTIME_UNAVAILABLE or SEGMENTATION_NO_LEXICAL_HOST)

## Test Coverage

- `test_clitic_only_fail_closed.py` — 7 tests covering بِكُمْ
- `test_ayat_al_dayn_segment_aware.py::test_case_11_bikum_clitic_only`
- `test_segment_aware_slot_graph.py::test_clitic_only_no_center`
