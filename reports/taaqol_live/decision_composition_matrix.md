# Decision Composition Matrix — HOKOM-TAAQOL-LIVE-INTEGRATION-01

## Rule: Upstream CANNOT be upgraded by Taaqol (monotonic composition)

| Case | Upstream Verdict | Taaqol Verdict | Effective Verdict |
|------|-----------------|----------------|------------------|
| 1 | BLOCKED / BLOCK | any | BLOCKED |
| 2 | DEFERRED / DEFER | BLOCKED | BLOCKED |
| 3 | DEFERRED / DEFER | other | DEFERRED |
| 4 | RESIDUAL | BLOCKED | BLOCKED |
| 5 | RESIDUAL | other | RESIDUAL |
| 6 | ACCEPTED / ACCEPT / LICENSED / COMPLETE | APPROVED→LICENSED | LICENSED |
| 6 | ACCEPTED / ACCEPT / LICENSED / COMPLETE | DEFERRED | DEFERRED |
| 6 | ACCEPTED / ACCEPT / LICENSED / COMPLETE | BLOCKED | BLOCKED |
| 7 | unknown / NOT_APPLICABLE | BLOCKED | BLOCKED |
| 7 | unknown / NOT_APPLICABLE | other | DEFERRED |

## Special Taaqol Verdict Normalization

| Raw TransitionState | Normalized taaqol_verdict | Effective |
|--------------------|--------------------------|---------|
| APPROVED | LICENSED | depends on upstream |
| REJECTED | BLOCKED | always BLOCKED |
| FORBIDDEN_LEAP | BLOCKED | always BLOCKED |
