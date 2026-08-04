# QIYAS-HOKOM-TAAQOL-MAQAYIS-CGPS01-FULL-MAXIMUM-CANONICAL-CLOSURE-01
# Closure Summary — Taaqol implementation slice

**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`
**Determinism (typed downstream):** PASS (RUN1 == RUN2)

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

## Live integrity snapshot (Phase T1 replacement for decorative counters)

| Counter | Observed | Domain |
|---------|----------|--------|
| `BLOCK_WITHOUT_REASON_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `DEFER_WITHOUT_RESIDUAL_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `DIRECT_TAAQOL_INJECTION_COUNT` | 0 | SOURCE_ANTI_PATTERN |
| `EXACT_SURFACE_BRANCH_COUNT` | 0 | SOURCE_ANTI_PATTERN |
| `EXCEPTION_AS_SUCCESS_COUNT` | 0 | STRUCTURAL_DERIVATION |
| `EXPECTED_VERDICT_MAP_COUNT` | 0 | SOURCE_ANTI_PATTERN |
| `GOLD_LOOKUP_COUNT` | 0 | SOURCE_ANTI_PATTERN |
| `HOKOM_FABRICATED_VERDICT_COUNT` | 0 | SOURCE_ANTI_PATTERN |
| `LOCALLY_CLOSEABLE_NATIVE_STAGE_COUNT` | 0 | STRUCTURAL_DERIVATION |
| `MISSING_PREDECESSOR_ACCEPT_COUNT` | 0 | STRUCTURAL_DERIVATION |
| `REFUSED_AS_ACCEPT_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `REFUSED_COLLAPSED_TO_NONE_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `REFUSED_WITHOUT_FAILURE_CODE_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `REFUSED_WITHOUT_REASON_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `REFUSED_WITHOUT_TRACE_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `RESIDUAL_UNACCOUNTED_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `SYNTHETIC_EVIDENCE_COUNT` | 0 | SOURCE_ANTI_PATTERN |
| `TOKEN_POSITION_BRANCH_COUNT` | 0 | SOURCE_ANTI_PATTERN |
| `TRACE_INCOMPLETE_COUNT` | 0 | RUNTIME_TYPED_OUTCOME |
| `UNBRIDGED_REACHABLE_STAGE_COUNT` | 0 | STRUCTURAL_DERIVATION |

**meta.HARDCODED_ZERO_COUNTER_COUNT:** 0
**meta.UNMEASURED_COUNTER_COUNT:** 0
**meta.COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT:** 0

## Vendor SHA

`05c6668dfb95d9238cff5df1d8bc73d0664bccb3` (vendor/Taaqol-GPT pinned)

## What changed vs the reaudit-02 HEAD (7febd11)

1. **T0** — `.claude/` harness-local files excluded from tracking
   (strict cleanliness gate now returns zero bytes).
2. **T1** — decorative 16-zero `integrity_counters` block
   replaced by a live measurement framework
   (`pipeline/taaqol_integration/integrity_measurement.py`) with
   7 AST/regex source scanners + 9 runtime-record predicates +
   4 structural derivations. Mutation-proof tests cover every rule.
3. **T2** — Wave07 test suite (17 tests) closes the typed-REFUSED
   coverage for Hukm/Tanzil/Mafhum, adds missing-predecessor and
   wrong-type paths, and adds THREE end-to-end BLOCK tests via
   real vendor codes: MANTUQ_BLOCKS_MAFHUM, TAHQIQ_OVERCLAIM,
   NO_MAFHUM_CROSS_DOMAIN_LEAP.
4. **T3** — RelationClosure and Ifadah residual under-reporting
   fixed. Real vendor residuals now propagate through the
   per-span artifact instead of being replaced by `[]`.
5. **T4** — this evidence + Wave07 typed ledger + report-binding
   manifest (two-step: content HEAD, report commit HEAD,
   binding manifest HEAD).

## Artifact hashes

- RUN1_TYPED_DOWNSTREAM_EXECUTION.json — sha256=8aa86ce4b15d70147bfd8a6cd5a6649c4d1fac14d47a08d314625c05b945e801
- RUN2_TYPED_DOWNSTREAM_EXECUTION.json — sha256=8aa86ce4b15d70147bfd8a6cd5a6649c4d1fac14d47a08d314625c05b945e801
- INTEGRITY_SNAPSHOT.json — sha256=43e7206716b4414925e60370b2c66d5991a006132a17f9660e2087e402e1d117

## No self-declared VERIFIED_CLOSED

Per the campaign directive, an implementation session must not
issue the final VERIFIED_CLOSED verdict. A fresh strictly
read-only audit session must be started by the owner against this
branch's HEAD after handoff.
