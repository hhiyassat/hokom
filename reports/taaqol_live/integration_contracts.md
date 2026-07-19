# Integration Contracts — HOKOM-TAAQOL-LIVE-INTEGRATION-01

## Absolute Constraints (Verified)

| Constraint | Status |
|-----------|--------|
| NEVER modify vendor/Taaqol-GPT | VERIFIED (git status clean) |
| NEVER use git add -A or git add . | PENDING (commit not yet made) |
| NEVER add skip/xfail to cover failures | VERIFIED |
| NEVER delete existing tests | VERIFIED |
| NEVER create shims or monkey patches | VERIFIED |
| NEVER create fallback returning LICENSED on Taaqol failure | VERIFIED (fail-closed → DEFERRED) |
| NEVER copy Taaqol code into Hokom | VERIFIED |
| NEVER modify semantic behavior of closed pipeline stages | VERIFIED (additive-only change) |
| NEVER fabricate claims from non-wired stages | VERIFIED |
| ONE commit at the very end | PENDING |

## Input Contract

`evaluate_hokom_claim_bundle(bundle)`:
- `bundle`: any object with `HokomLinguisticClaimBundle` fields
- `domain_directive`: 'ACCEPT' | 'BLOCK' | 'DEFER' | other
- No side effects, no I/O (except vendor import)

## Output Contract

Returns `HokomTaaqolDecision` (frozen dataclass):
- `bridge_id`: always `'HOKOM_TAAQOL_LIVE_BRIDGE'`
- `effective_verdict`: one of `'LICENSED' | 'DEFERRED' | 'BLOCKED' | 'RESIDUAL'`
- `fail_closed`: always `True`
- `strict_mode`: always `True`
- Never returns `None`
- Never raises (all errors caught, recorded in trace)

## Fail-Closed Contract

On ImportError (Python 3.10, missing package):
- `taaqol_verdict = 'DEFERRED'` (not LICENSED)
- `effective_verdict = compose_effective_verdict(upstream, 'DEFERRED')`
- BLOCKED upstream → still BLOCKED (monotonic)
- ACCEPT upstream → DEFERRED (not promoted)
