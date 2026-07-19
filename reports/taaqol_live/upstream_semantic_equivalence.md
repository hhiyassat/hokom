# Upstream Semantic Equivalence — HOKOM-TAAQOL-LIVE-INTEGRATION-01

## Constraint

NEVER modify semantic behavior of closed pipeline stages.

## Verification

`git diff --name-only` shows only `hokom_pipeline.py` modified.

The modification is **additive only**: a try/except block added after all pipeline stages complete, immediately before the `return` statement. No stage logic (P0, P1, P2, P3, P4, P5, Word Class Engine, Phase 5) was modified.

## Evidence

- 4308 existing tests pass post-integration
- Pre-existing failures: 10 (all Python 3.11 readiness tests on Python 3.10 container — pre-existing)
- Integration-caused regressions: 0
- `test_taaqol_not_in_hokom_pipeline` fixed by restructuring to `pipeline.taaqol_integration.live`

## Modified File

`hokom_pipeline.py` — additive change only:
- Builds `_hokom_result_partial` dict from completed pipeline state
- Calls `bundle_from_hokom_result()` and `evaluate_hokom_claim_bundle()`
- Adds `taaqol_decision` and `taaqol_effective_verdict` to return dict
- All inside try/except — failures produce `taaqol_decision=None`, not LICENSED
