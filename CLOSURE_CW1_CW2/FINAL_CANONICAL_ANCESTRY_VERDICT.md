# FINAL CANONICAL ANCESTRY & COHERENCE — VERDICT

Branch `feature/closure-cw1-cw2-foundation-01` @ `f8410dd`. No push / PR / merge /
tag. Protected closure ref untouched. Scope = `LINGUISTIC_STRUCTURAL_JUDGMENT`
(no fiqh / no tafsir / no shar'i hukm). Success criterion = **ACCOUNTED FOR**, not
"21/21 CERTIFIED" (§30).

## What is BUILT and PROVEN (executable)

| # | Deliverable | Evidence |
|---|-------------|----------|
| 1 | 6 typed proof-carrying certificates (P8→P12 + ancestry) over the REAL `HOKOM_CANONICAL_PIPELINE` runtime; verdict from `StageTrace.stage_status`+`ConstitutionalJudgment`, never a bare bool | `canonical_bridge/certificates.py` |
| 2 | P8→P12 wired with real evidence (hokom P0–P5 → `WordInput.hokom_evidence_by_stage`); no fabricated upstream facts | `canonical_bridge/bridge.py` |
| 3 | Executable **no-jump**: a CERTIFIED successor requires a permitting (CERTIFIED/NA) predecessor | `_no_jump`; test `test_no_jump_law_...` |
| 4 | One `CanonicalRunManifest` — **asserts `hokom_sha != UNKNOWN`** — + artifact-coherence verifier where run_id/hokom_sha/byte-sha mismatch = **FAIL, not warn** | `build_run_manifest` / `verify_artifact_coherence` |
| 5 | Positive-control (NA at P8, closed-class `مِنْ`) + honest DEFER cascade verticals | `run_canonical_ancestry_vertical.py` |
| 6 | Test matrix — 7/7 pass | `canonical_bridge/tests/test_canonical_certificates.py` |
| 7 | Regenerated ONE coherent artifact stamped to real HEAD (`hokom_sha == HEAD f8410dd`); `ALL_ARTIFACTS_SAME_RUN_MANIFEST` | regenerator output |
| 8 | Clean-clone (detached worktree @ HEAD) + determinism: **byte-identical run_id + body-sha** across trees | `git worktree` proof |
| 9 | Every applicable stage ACCOUNTED FOR (`unexplained = 0`); RES-ANCESTRY-01 no-jump = CLOSED | accounting + ancestry |

Ownership (§22): P8–P12 fact owner = `HOKOM_CANONICAL_PIPELINE`; root fact owner =
`pipeline/p3_candidate` (single authority); `ayat_al_dayn.build_gold_relations` =
`COMPARISON_ONLY / REGRESSION_ORACLE` — **not** used to certify (using it would be
importing the answer backward, forbidden). AMN L5/L6/L7 kernels = COMPARISON/LEGACY.

## Verdict

```
RES-ANCESTRY-01  = CLOSED
    (typed ancestry + executable no-jump + coherent single-manifest artifacts
     + determinism + clean-clone reproducibility + honest residuals; unexplained=0)

CANONICAL_CLOSURE = NOT_CLOSED  (blocked by exactly ONE root cause, below)
```

The ancestry, coherence, no-jump, manifest, determinism and reproducibility
machinery is closed and honest. What is **not** demonstrated is a **positive**
certified P8→P12 vertical: every vertical DEFERs at P9–P12 because no real
sentence-level evidence exists to certify against — and §19/§25/§29-J require at
least one genuine CERTIFIED chain. A DEFER-only engine is accounted-for but has not
shown it can certify when evidence supports it.

## The ONE root cause (owner decision required)

- **Root cause:** No runtime producer of **cross-token (sentence-level) government
  evidence** (`amil → mamul` units). Production `hokom()` is word-level; the P8–P12
  canonical adapters are real but receive no sentence-level evidence, so they can
  only DEFER. The sole cross-token relation source is a **gold oracle**
  (`COMPARISON_ONLY`) that must not be used as certifying authority.
- **Owner:** `HOKOM_CANONICAL_PIPELINE` (`src/hokom/canonical/pipeline.py` — the P8
  `amil_mamul` adapter + a new sentence-level government analyzer feeding it).
- **Executable evidence:** `run_canonical_ancestry_vertical.py` → every vertical
  `certified=0, deferred=4, not_applicable=1`; `res_ancestry_01=CLOSED` but
  `chain_verdict=CLOSED_WITH_HONEST_DEFER` (no positive link).
- **Decision:** Authorize building the sentence-level government **evidence
  producer** (a real analyzer, NOT the gold oracle). This is **authorized-in-scope**
  linguistic-structural engineering with **no new theory** (the government theory is
  already in the P8 adapter; only runtime evidence *production* is missing). It is
  NOT the previously-dissolved fiqh blocker.

Once that producer feeds real `amil_mamul_units`, the existing certificate chain
will emit a genuine positive P8→P12 vertical with the SAME typed contracts, no-jump
law, manifest and coherence checks already proven here — flipping
`CANONICAL_CLOSURE` to `VERIFIED_CLOSED` without any change to the closure machinery.
