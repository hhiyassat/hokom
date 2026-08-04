# QIYAS-TAAQOL-MAXIMUM-NATIVE-CLOSURE-REMEDIATION-02 — Closure Summary

**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_REAUDIT`
**Determinism:** PASS (RUN1 == RUN2)

## Per-stage typed closure (ACCEPT / DEFER / BLOCK)

| Stage                   | Calls | ACCEPT | DEFER | BLOCK |
|-------------------------|-------|--------|-------|-------|
| ifadah                  |     5 |      5 |     0 |     0 |
| hukm                    |     5 |      5 |     0 |     0 |
| manat                   |     5 |      5 |     0 |     0 |
| tanzil                  |     5 |      5 |     0 |     0 |
| audited_tanzil_bridge   |     5 |      5 |     0 |     0 |
| mantuq                  |     5 |      5 |     0 |     0 |
| mafhum                  |     5 |      5 |     0 |     0 |

**unbridged_reachable_stage_count:** 0

## Vendor SHA

`05c6668dfb95d9238cff5df1d8bc73d0664bccb3` (vendor/Taaqol-GPT pinned)

## What changed vs the audited HEAD (b8e362f)

1. **REPAIR A** — `bridge_tanzil_to_audit` is now invoked; the   audit-layer stage that consumes `TanzilVerdict` closes 5/5   (`SURFACED`).
2. **REPAIR B** — every downstream stage returns a typed   `DownstreamStageOutcome` preserving `verdict_state`,   `failure_code`, `trace_ref`, and residuals. Vendor REFUSED   no longer collapses to None.
3. **REPAIR C** — Manat and Mantuq gained explicit typed-REFUSED   tests; audit bridge got ACCEPT + REFUSED tests.
4. **REPAIR D** — per-span artifact now records   input_stage / native_result_type / verdict_state / classification   / failure_code / trace_ref / residual_ids / failure_detail.
5. **REPAIR E** — Tanzil terminal claim corrected (audit-layer   bridge is the next reachable stage).
