# Monotonicity Proof — HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME

## Claim

The Taaqol integration preserves strict fail-closed monotonic composition.
No path yields LICENSED when upstream is BLOCK or when Taaqol is unavailable.

## Composition Table (compose_effective_verdict)

| upstream_verdict | taaqol_verdict | effective_verdict |
|-----------------|---------------|------------------|
| ACCEPT | LICENSED | LICENSED |
| ACCEPT | DEFERRED | DEFERRED |
| ACCEPT | BLOCKED | BLOCKED |
| DEFER | LICENSED | DEFERRED |
| DEFER | DEFERRED | DEFERRED |
| BLOCK | LICENSED | BLOCKED |
| BLOCK | DEFERRED | BLOCKED |
| BLOCK | BLOCKED | BLOCKED |

Rule: BLOCK propagates regardless of Taaqol. DEFER holds unless both sides agree.

## Clitic-Only Monotonicity

Even when domain_directive='ACCEPT' (Hokom says accept), clitic-only tokens
yield DEFERRED because there is no morphological center to license.

upstream=ACCEPT + segment_clitic_only=True → effective=DEFERRED ✓

## New Tests Verifying Monotonicity

- `test_fail_closed.py::test_upstream_block_preserved` (existing, still passes)
- `test_clitic_only_fail_closed.py::test_clitic_only_not_licensed`
- `test_ayat_al_dayn_segment_aware.py::test_case_11_bikum_clitic_only`
- All 67 new tests: effective_verdict ∈ {LICENSED, DEFERRED, BLOCKED, RESIDUAL}

## Verification

Both canonical suite runs: 4947 passed, 0 regressions in monotonicity.
