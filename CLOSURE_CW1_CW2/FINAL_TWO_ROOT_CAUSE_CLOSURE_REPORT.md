# HOKOM–TAAQOL — FINAL TWO-ROOT-CAUSE REMEDIATION + CLOSURE VERDICT

Branch `feature/closure-cw1-cw2-foundation-01` @ `abb8e05`. No push / PR / tag.
Protected refs untouched. Scope = `LINGUISTIC_STRUCTURAL_JUDGMENT`. Approved
Taaqol vendor = `05c6668d` (owner decision 2026-08-14).

## The two owner-defined root causes

### RC-A — native cross-token sentence government → RESOLVED  (`abb8e05`)
`canonical_bridge/government_producer.py` detects حروف الجر from the mabniyat
catalog (a linguistic KB — the closed class — **not** the `ayat_al_dayn` gold
oracle) and governs the following token as مجرور. It emits real P8/P9/P10/P11
sentence-level evidence.

- **Positive vertical** (`إِلَىٰ أَجَلٍ`, `عَلَى الْأَرْضِ`, `فِي قُلُوبِهِمْ`):
  P8→P12 all CERTIFIED, `no_jump_failures=0`, `unexplained=0`,
  **`REAL_NATIVE_CROSS_TOKEN_GOVERNMENT_CERTIFICATE_COUNT = 1`**.
- **Negative control** (no حرف جر): P8=NOT_APPLICABLE, P9–P12=DEFER, `gov=0` — no
  fabricated government.
- 12/12 `canonical_bridge` proofs pass; verified robust in isolation.

Owner criterion met: ≥1 genuine positive cross-token vertical **and** complete
accounting (`unexplained=0`), not a guessed CERTIFIED.

### RC-B — Taaqol canonical integration reproducibility → RESOLVED  (`f092683…4f935c2`)
- The root cause was a developer editable install (`~/Taaqol-GPT-main-reference`)
  **masking** the committed submodule (silently bumped to the unapproved
  `bc9d1ea5`). Per owner decision, authoritative vendor = `05c6668d`.
- Actions: submodule restored to `05c6668d`; 22 source provenance labels swept
  `bc9d1ea5→05c6668d`; the genuinely `bc9d1ea5`-dependent W8 layer gated as
  `DEFERRED_UNAPPROVED_VENDOR_FEATURE`; conftest regenerates the git-ignored c9
  CSV from canonical source + enforces in-repo vendor authority.
- c13/at-risk scope: **783 passed, 1 residual** (the orchestrator WIP item below).

## Final clean-clone regression (approved 05c6668d baseline)

`7686 passed, 45 failed, 27 errors, 82 skipped` (712s) — vs. the pre-work baseline
`7656 passed / 57 failed / 50 errors`: a net improvement (more passing, fewer
failing/erroring), and the 50 c13 collection errors are gone.

Clean-clone provisioning required (documented): `git submodule update --init
--recursive` (vendor) **and** `PYTHONPATH=<…/fractal/algebra/Saleh-/src>` (the
`qiyas_core` registry-snapshot generator `sys.exit(1)`s when this external sibling
is absent — a pre-existing coupling, not from this work).

### Failure classification (honest)
1. **Newer Taaqol wave requires the UNAPPROVED `bc9d1ea5` vendor (the primary,
   owner-anticipated incompatibility).** `e7_formal_shape`, `e8_maqam_relation`,
   `answer_audit` (W9), `vendor_execution_record_bridge` (W8, already quarantined),
   `c13_wave06`. W8 was confirmed to need vendor `runtime.execution_record`
   (present only in `bc9d1ea5`). These features **pass in isolation against the
   polluting editable install** (which carries `bc9d1ea5`-era files under a
   `05c6668d` git label) and **fail under the true approved `05c6668d` submodule** —
   exactly the masking the owner identified. This is a REAL current-runtime
   incompatibility, reported (not silently promoted to `bc9d1ea5`).
2. **Test-isolation / ordering effect.** These same tests pass when run in a small
   scope and fail in the full suite — an order-dependent vendor-module caching
   interaction between the editable-install pollution and the in-repo vendor
   authority shim. A definitive clean-clone verdict needs a hermetic environment
   with **no** editable install (vendor sourced only from the submodule).
3. **Governance/artifact tests** (`test_artifact_commit_binding`,
   `test_canonical_runtime_contract`): clean-clone artifact-staleness / env-shape
   checks, not canonical-logic defects.
4. **Orchestrator WIP residual** (`test_ayat_native_cu_map`): blocked solely on the
   committed `full_target_orchestrator.py _TARGET_TAAQOL_SHA=bc9d1ea5`, which lives
   in the user's uncommitted orchestrator WIP (already reverted to `05c6668d`
   there). Not touched per the no-WIP-absorption rule; self-resolves on WIP landing.

## VERDICT

```
PROJECT_CLOSURE = NOT_CLOSED
```

The two owner-defined engineering root causes are **RESOLVED** (RC-A native
government; RC-B reproducibility + vendor-authority reconciliation). Full-project
`VERIFIED_CLOSED` is blocked by items that are **governance / environment**, not new
linguistic engineering:

- **ROOT_CAUSE_1 (governance, owner-framed): the newer Taaqol evaluator wave
  genuinely depends on the unapproved `bc9d1ea5` vendor.** Restoring the approved
  `05c6668d` baseline is NOT technically impossible — the canonical path (P0–P5,
  `canonical_bridge` P8→P12, RC-A native government) and the pre-`bc9d1ea5` Taaqol
  all work on `05c6668d`. But `formal_shape`/`maqam`/`answer_audit`/`execution_record`
  need post-`05c6668d` vendor APIs. Per the owner's own decision, a `bc9d1ea5`
  upgrade is a **separate future governed cycle** (behavior audit + provenance audit
  + migration + refreeze + regression + approval), NOT this closure. These features
  are therefore **out of the approved-baseline closure scope, deferred**, and their
  tests must be gated as `DEFERRED_UNAPPROVED_VENDOR_FEATURE` (as W8 already is)
  before the approved baseline can be green.
  - OWNER: vendor governance. MINIMAL_NEXT_ACTION: either (a) gate the newer-wave
    tests on real vendor capability (`skipif` on the missing API) so the approved
    `05c6668d` baseline is honestly green, deferring the wave to the governed
    upgrade; or (b) authorize and execute the governed `bc9d1ea5` upgrade.

- **ROOT_CAUSE_2 (environment/infra): definitive clean-clone verification needs a
  hermetic env** — no conflicting editable install, vendor from submodule only,
  Saleh/`qiyas_core` provisioned. The current dev machine's editable install both
  masks the truth and induces order-dependent test outcomes.

- **Residual (owner-side WIP): the orchestrator `_TARGET_TAAQOL_SHA` line** — one
  test; resolves when the user's orchestrator WIP lands.

## What IS closed (green on the approved baseline)
P0–P5 foundation · single P3 root authority · corpus provenance · `canonical_bridge`
P8→P12 typed certificate chain · RC-A native government positive vertical · no-jump ·
determinism · artifact coherence · RC-B CSV reproducibility + vendor reconciliation ·
7686 passing tests.

`CLOSURE_VERDICT = NOT_CLOSED` (two owner-defined root causes resolved; remaining
blockers are vendor-governance + clean-env, per the owner's own framework).
