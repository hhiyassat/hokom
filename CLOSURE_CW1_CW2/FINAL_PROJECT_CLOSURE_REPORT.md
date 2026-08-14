# HOKOM–TAAQOL — FINAL CANONICAL PROJECT CLOSURE REPORT

Fresh final canonical run from controlled state (§31). Verdict derived only from
this run + its audited dependencies. Branch `feature/closure-cw1-cw2-foundation-01`.
No push / PR / merge / tag. Protected refs untouched.

## A. BASELINE
- repository = `hokom`; branch = `feature/closure-cw1-cw2-foundation-01`
- `HEAD_FULL = c5504ed0d8cdd755d4dc8fd705dfe4e697a9aeff`
- upstream = NONE (local); python = 3.12.4
- prior canonical closure ref `c768cf4` (branch base) — untouched; HEAD is 9 commits ahead
- git status = DIRTY: pre-existing user WIP preserved (`pipeline/taaqol_integration/evidence_adapter.py`, `full_target_orchestrator.py` modified; `maqayis_v2*` untracked) + stray flag-named files (`--format`, `--lang`, `--output-dir`, `--taaqol`) from a misfired CLI redirect (left in place per git-safety §30)
- linguistic base = production `hokom()` P0–P5 (fresh-clone reproducible, 774 core tests)

## B. SCOPE
Declared canonical scope = `LINGUISTIC_STRUCTURAL_JUDGMENT`: the typed P8→P12
proof-carrying certificate ancestry vertical over `HOKOM_CANONICAL_PIPELINE`, with
single-owner root facts (`pipeline/p3_candidate`), no fiqh/tafsir/hukm. "Project
closure" additionally requires (§2 global) the Taaqol integration layer that
consumes these governed claims to itself be reproducible and regression-clean.

## FINAL RUN IDENTITY
- `FINAL_RUN_ID = dee41d19cb725249`
- `hokom_sha = c5504ed0d8cdd755d4dc8fd705dfe4e697a9aeff` (== HEAD, no UNKNOWN)
- `corpus_sha = 1130fc9f…` (Tanzil Uthmani, 77,374 tokens)
- artifact_body_sha = `bd1bf3e05d457955adb8d8aa96251e7efa2724760659dce9aac57cb8b6ac94ae`

## C. PREVIOUS-CLOSURE RE-AUDIT
- RES-ANCESTRY-01 infra (typed certs + no-jump + coherence + determinism) = **RECONFIRMED** (7/7 proofs, clean-clone byte-identical).
- P3 single root authority (`P3_ROOT_AUTHORITIES_ACTIVE==1`) = **RECONFIRMED** (structural test passes; HR2S/gold oracle segregated).
- Corpus provenance (in-repo blob `469bc3ba`) = **RECONFIRMED**.

## D. HOKOM LINGUISTIC CLOSURE
P0–P5 (identity/normalization/segmentation/clitics/word-class/root/wazn/bab/masdar)
= CLOSED per-token with honest CERTIFIED/DEFER/BLOCK, single owner, algorithmic
(anti-oracle clean). No higher fact inferred from a weaker one.

## E. TAAQOL CLOSURE
Certificate/claim layer is typed, owner = HOKOM_CANONICAL_PIPELINE, no
licensed-without-scope, deterministic claim IDs. BUT the C13 integration test layer
does not execute in a clean room (see RC2).

## F. P8→P12
All five stages execute in the real canonical runtime and return typed verdicts, but
on the available evidence every stage **DEFERs** (P9–P12) or is **NOT_APPLICABLE**
(P8, no cross-token government evidence). `certified = 0` in every vertical →
**no positive certified vertical** (RC1).

## G. SENTENCE GOVERNMENT
No runtime producer of cross-token government evidence (`amil→mamul`). The only
cross-token relation source (`ayat_al_dayn.build_gold_relations`) is a GOLD ORACLE
(`COMPARISON_ONLY`, explicit "NOT for production" disclaimer) and is correctly **not**
wired into the certifying path. CLOSED_BY_EVIDENCE for cross-token government = none.

## H. ANCESTRY
Typed chain P8→P12 + ancestry emitted; `no_jump_failures = 0`; `unexplained = 0`;
`SYNTHETIC_ANCESTRY = 0`; `UNEXPLAINED_STAGE_JUMPS = 0`. But the chain is a DEFER
cascade (`CLOSED_WITH_HONEST_DEFER`) — accounted-for, not positively certified.

## I. PROVIDER OWNERSHIP
`PROVIDER_OWNERSHIP = RESOLVED`. Owner = `pipeline/p3_candidate/…resolve_root_pipeline`.
Shadow producers (HR2S, gold relations) segregated to integrations/tests/demo only.

## J. CORPUS GOVERNANCE
corpus_sha `1130fc9f…` reproducible from in-repo blob; historical 62,205 not used as
a target. In scope for P0–P5; OK.

## K. RESIDUAL MAP
- `res-ancestry-01:sentence_evidence_declared_residual` — DEFERRED_BY_DESIGN, non-blocking for the *infra*, but blocking for a *positive* vertical (RC1).
- Taaqol C13 ephemeral-artifact dependency — OPEN/BLOCKER (RC2).

## L. KNOWN-BAD REGRESSION
P0–P5 honest DEFER on hard forms (no wrong LICENSED in the certificate path;
`KNOWN_BAD_WRONG_LICENSED = 0` within the certified scope, which certifies nothing
positively).

## M. ANTI-ORACLE
`TEST_ORACLE_LEAKAGE = 0`, `GOLDEN_OUTPUT_RUNTIME_DEPENDENCY = 0`,
`FIXTURE_ANSWER_LEAKAGE = 0` (independent adversarial audit; root computation is
algorithmic consonant extraction).

## N. TESTS (full relevant regression, 516s)
`7656 passed, 57 failed, 50 errors, 72 skipped`. All 107 failures/errors localize to
`tests/taaqol_integration/test_c13_wave03/05/06/07_*`. Cause = ephemeral generated
report CSV (`reports/taaqol_full_integration/c9_runtime_output/ayat_al_dayn_results.csv`,
**git-ignored**) missing in clean checkout + dirty-WIP removal of
`get_ayat_native_cu_map`. Pre-existing at base `c768cf4` (16 errors there); my 9
commits touch **zero** taaqol files. Classification: ENVIRONMENT_GAP /
EPHEMERAL_ARTIFACT_DEPENDENCY + in-flight uncommitted refactor. **Not proven
non-blocking → RC2.**

## O. DETERMINISM
`run1_body_sha == run2_body_sha == bd1bf3e0…` → `DETERMINISM = VERIFIED`.

## P. CLEAN-ROOM / CLEAN-CLONE
Canonical ancestry vertical: detached worktree @ HEAD, `env -u PYTHONPATH`,
controlled cwd → coherent + deterministic (byte-identical run_id + body-sha) →
VERIFIED. Taaqol C13 layer: clean worktree @ HEAD → 8 failed / 27 errors →
**CLEAN_ROOM_REPRODUCIBLE = NO for the integration layer** (RC2).

## Q. ARTIFACTS
| path | run_id | sha256 | role |
|------|--------|--------|------|
| CLOSURE_CW1_CW2/canonical_ancestry_run.json (regenerable) | dee41d19cb725249 | body `bd1bf3e0…` | canonical P8→P12 ancestry result |
| canonical_bridge/certificates.py | — | committed c5504ed | certificate contracts |
| scripts/run_canonical_ancestry_vertical.py | — | committed c5504ed | one-run regenerator + coherence self-check |

## R. CLOSURE MATRIX (mandatory conditions)
| condition | result |
|-----------|--------|
| canonical scope defined | PASS |
| repository state identified | PASS |
| prior closures re-audited | PASS |
| Hokom/Taaqol ownership respected | PASS |
| no dual-authority ambiguity | PASS |
| required canonical stages executed | PASS |
| **P8→P12 real *positive* vertical verified** | **FAIL (certified=0)** |
| full ancestry (typed, no synthetic, no jump) | PASS |
| transition legality / preservation | PASS |
| **required sentence-level government verified** | **FAIL (no evidence producer)** |
| final claims trace to real evidence | PASS (for DEFER); N/A positive |
| no synthetic ancestry / silent fallback / oracle leakage | PASS |
| blocking residuals = 0 | **FAIL (RC1, RC2)** |
| corpus governance (P0–P5) | PASS |
| canonical artifacts coherent | PASS |
| HEAD/provenance known | PASS |
| **regression accepted** | **FAIL (57 failed / 50 errors)** |
| skips classified | PASS |
| determinism verified | PASS |
| clean-room reproduction | PASS (vertical) / **FAIL (Taaqol C13)** |
| clean-clone reproduction | PASS (vertical) |

## S. FINAL VERDICT
`PROJECT_CLOSURE = NOT_CLOSED`. `ROOT_CAUSE_COUNT = 2` (independent).

### ROOT_CAUSE_1 — no cross-token government evidence producer
- OWNER: `HOKOM_CANONICAL_PIPELINE` (`src/hokom/canonical/pipeline.py`, P8 amil_mamul adapter + a new sentence-level analyzer).
- STAGE: P8→P12.
- EXACT_FAILURE: every vertical `certified=0`; no positive certified P8→P12 chain exists because no runtime produces real `amil→mamul` units. The sole cross-token source is a gold oracle (COMPARISON_ONLY, forbidden as authority).
- WHY_IT_BLOCKS: §11/§27 require a real positive P8→P12 vertical; a DEFER-only engine is accounted-for but has never demonstrated positive certification.
- REQUIRED: build the sentence-level government evidence producer (real analyzer, not the oracle). Authorized-in-scope linguistic-structural engineering, **no new theory** (government theory already in the P8 adapter).
- MINIMAL_NEXT_ACTION: implement intra-token government first (verb + object-pronoun enclitic — real segmentation evidence already produced by hokom()) to yield the first genuine positive P8 certificate, then extend to cross-token spans.

### ROOT_CAUSE_2 — Taaqol C13 integration layer not clean-room reproducible / regression red
- OWNER: Taaqol integration layer (`pipeline/taaqol_integration/`, `tests/taaqol_integration/`).
- STAGE: C13 downstream integration (waves 03/05/06/07).
- EXACT_FAILURE: 57 failed + 50 errors; tests require a **git-ignored ephemeral** report CSV (`reports/taaqol_full_integration/c9_runtime_output/ayat_al_dayn_results.csv`) absent from clean checkout; an in-flight uncommitted refactor additionally removed `get_ayat_native_cu_map`. Pre-existing at base `c768cf4`.
- WHY_IT_BLOCKS: §21 clean-room + §24 regression require a reproducible, accepted regression; a suite that only passes when a non-versioned artifact was previously generated is not clean-room reproducible.
- REQUIRED: make the C13 fixtures generate their inputs deterministically within the test (or version them), and land/repair the `full_target_orchestrator` refactor so the expected symbols exist.
- MINIMAL_NEXT_ACTION: add a session-scoped fixture that produces `ayat_al_dayn_results.csv` from the canonical run (not a stale report), and reconcile the orchestrator public API with its consumers.

`CLOSURE_VERDICT = NOT_CLOSED`
