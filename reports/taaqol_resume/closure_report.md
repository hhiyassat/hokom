# Closure Report — HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME

**Date:** 2026-07-20
**Starting HEAD:** b992d7e
**Status:** CLOSED

## Summary

The Taaqol live governance integration now consumes the canonical Hokom
SegmentBundle and uses the lexical host (segment_host) as the morphological
center scope in the SlotGraph, replacing the incorrect use of original_surface.

## Files Changed

| File | Change |
|------|--------|
| `pipeline/taaqol_integration/provider_models.py` | Added Amendment No. 3: segment_host, segment_proclitics, segment_definite_article, segment_enclitics, segment_clitic_only, segment_verdict fields |
| `pipeline/taaqol_integration/live/models.py` | Added taaqol_center_scope field to HokomTaaqolDecision |
| `pipeline/taaqol_integration/claim_adapter.py` | Wired all segment fields through to HokomLinguisticClaimBundle |
| `hokom_pipeline.py` | Added segment fields to _hokom_result_partial; exposed taaqol_center_scope in return dict |
| `pipeline/taaqol_integration/live/bridge.py` | Fixed Center.scope to use segment_host; added clitic-only gate; taaqol_center_scope computed before import |

## Tests Added (67 total)

| File | Tests |
|------|-------|
| `tests/taaqol_live/test_segment_aware_slot_graph.py` | 8 |
| `tests/taaqol_live/test_clitic_only_fail_closed.py` | 7 |
| `tests/taaqol_live/test_no_full_token_center.py` | 16 |
| `tests/taaqol_live/test_no_parallel_bridge.py` | 6 |
| `tests/taaqol_live/test_ayat_al_dayn_segment_aware.py` | 30 |

## Closure Gates

All gates: PASS (see closure_gates.json)

- FULL_TOKEN_CENTER_PROHIBITED: 0 violations
- ORIGINAL_SURFACE_AS_CENTER: 0 violations
- CLITIC_ONLY_FAIL_CLOSED: 0 violations
- SILENT_FALLBACKS: 0
- PARALLEL_BRIDGES: 0
- VENDOR_MODIFICATIONS: 0
- SEGMENTATION_FILES_MODIFIED: 0
- AYAT_AL_DAYN: 129 tokens, 0 errors, 0 violations

## Canonical Suite

Run 1: 4947 passed, 50 skipped, 10 failed (Python 3.10 version-gate only)
Run 2: 4947 passed, 50 skipped, 10 failed (identical)
RUN_1_EQUALS_RUN_2: TRUE

The 10 failures are Python 3.10 runtime checks. They pass on Python 3.12 (macOS canonical).
No new failures introduced.

## Key Fix

Before: `Center(scope=bundle.original_surface, ...)` — full token including clitics
After:  `Center(scope=bundle.segment_host or bundle.morphology_surface or original_surface, ...)`

For بِدَيْنٍ: was 'بِدَيْنٍ', now 'دَيْنٍ' (lexical root of the debt concept)
For بِكُمْ: no center (clitic-only → DEFERRED, center_scope=None)
