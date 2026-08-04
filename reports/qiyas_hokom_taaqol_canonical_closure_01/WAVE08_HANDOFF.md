# Wave08 Implementation Handoff — Vendor Pin Bump + Dual Carrier

**Wave:** 8 (successor to Wave07 at binding-commit `50c9961`).
**Scope:** owner-selected "bump-only, dual-adopt as carrier" — no
`DownstreamStageOutcome` replacement, no `run_native_corpus` adoption,
no AnswerAudit/GPT-R8 migration (those remain Phase XI of the parent
directive).
**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`.

## 1. What Wave08 delivered

| Wave08 commit | Concern |
|---|---|
| `42f119c` | Isolated vendor pin bump: `vendor/Taaqol-GPT` submodule pointer 05c6668 → bc9d1ea (single-file commit; no other changes) |
| `f7bb59e` | Sync `_VENDOR_SHA` constants + docstring metadata across 26 pipeline/script files (historical evidence scripts left unchanged) |
| `4d0dc7e` | New module `pipeline/taaqol_integration/vendor_execution_record_bridge.py` + 9-test file `tests/taaqol_integration/test_vendor_execution_record_bridge.py` — Hokom `DownstreamStageOutcome` converts to vendor `StageExecutionRecord` mirror; every vendor `__post_init__` invariant is verified by dedicated failing-input tests |
| `b7216dc` | Wave08 evidence: `WAVE08_VENDOR_STAGE_EXECUTION_RECORDS.json` (40 records across 5 spans × 8 stages, all EXECUTED, zero vendor rejections) + `WAVE08_CLOSURE_SUMMARY.md` + generator script |
| (this commit) | Wave08 typed ledger + handoff |
| (next commit) | Wave08 report-binding manifest (REPAIR F two-step protocol) |

## 2. Empirical proof of runtime compatibility

Re-executing the Wave07 evidence generator at the bumped pin produces **byte-identical** artifacts:

| Artifact | Wave07 binding sha256 (commit 50c9961) | Wave08 regenerated sha256 | Match |
|---|---|---|---|
| `RUN1_TYPED_DOWNSTREAM_EXECUTION.json` | `adbfc275…` | `adbfc275…` | ✓ |
| `RUN2_TYPED_DOWNSTREAM_EXECUTION.json` | `adbfc275…` | `adbfc275…` | ✓ |
| `INTEGRITY_SNAPSHOT.json` | `83f18a30…` | `83f18a30…` | ✓ |
| `DETERMINISM_COMPARE.json` | `444bee76…` | `444bee76…` | ✓ |

The Wave07 report-binding manifest at commit `50c9961` remains valid.

## 3. What Wave08 does NOT do

* **Does NOT delete `DownstreamStageOutcome`.** Both carriers coexist; every existing Hokom test asserts against the Hokom carrier as before.
* **Does NOT adopt vendor's `run_native_corpus`.** Vendor's own runtime is token-level (`span_id=None` throughout, no native verdict object attached to the record). Adopting it would surrender span-level composition authority to a runner that intentionally reaches only `PATH_CLASSIFICATION` on bare tokens. Hokom's span-level chain continues to be the semantic authority.
* **Does NOT migrate AnswerAudit or GPT-R8.** Vendor's own `LAW_TO_RUNTIME_COVERAGE_MATRIX.md` at bc9d1ea marks docs/46 (answer-audit) as `carrier-only in token runner` with residual `MODEL_CLIENT_REQUIRED`. `docs/56_GPT_R8_AUDIT_INTEGRATION_LAW.md` is law-only; the GPT-R8 runtime PR is not shipped upstream. Both remain the parent directive's Phase XI.
* **Does NOT remove old wrappers.** "Remove only after proof" (step 14) requires a bake-in period with the vendor mirror running in production. Wave08 has proven per-record compatibility; wrapper removal is a follow-up wave with its own reaudit.
* **Does NOT self-declare `VERIFIED_CLOSED`.**

## 4. What the reaudit session should verify

### 4.1 Repository state

* Branch is `closure/hokom-taaqol-final-production-01`.
* `vendor/Taaqol-GPT` submodule HEAD is `bc9d1ea5ef45970f5f3ec132441e30fd54b3da52`.
* `git status --porcelain=v2 --untracked-files=all` returns zero bytes.
* Sibling worktrees `hokom-maqayis-v1`, `hokom-cgps01-2a6af17`, `hokom-cgps01-integration` are clean; HEADs unchanged from reaudit-02 baseline.
* Historical tag `hokom-canonical-gate-27-closed` still points to `72be48f`.

### 4.2 Wave07 binding preservation

* All four Wave07-bound artifact sha256 values (see table §2) recompute equal to their Wave07 binding.
* This is the empirical evidence that the pin bump changed no vendor-observable behaviour.

### 4.3 Wave08 dual carrier

* `pipeline/taaqol_integration/vendor_execution_record_bridge.py` imports the vendor `StageExecutionRecord`, `StageApplicability`, `StageTransitionState`, `Rank`, `FailureCode` types from `taaqqul_slot_geometry.runtime` / `.core` at the bumped pin.
* All 9 tests in `tests/taaqol_integration/test_vendor_execution_record_bridge.py` pass.
* `reports/qiyas_hokom_taaqol_canonical_closure_01/WAVE08_VENDOR_STAGE_EXECUTION_RECORDS.json`: `all_spans_mirror_ok=true`, `rejections=[]`, vendor state distribution `{EXECUTED: 40}` across 5 spans × 8 stages.
* Vendor invariant proofs: tests W8.6 (rule 4), W8.7 (rule 7), W8.8 (rule 8) construct deliberately-invalid vendor records and confirm the vendor's own `__post_init__` raises `ValueError`.

### 4.4 SHA constant sync

* `grep -rn "05c6668" pipeline/ scripts/qiyas_canonical_closure_01_evidence.py scripts/qiyas_canonical_closure_01_wave08_evidence.py` returns zero hits (historical scripts `qiyas_taaqol_max_native_closure_evidence.py` and `qiyas_taaqol_remediation_02_evidence.py` are intentionally excluded and retain their historical SHAs).
* `grep -rn "bc9d1ea5ef45970f5f3ec132441e30fd54b3da52" pipeline/` returns the expected 23 references (24 including the assertion literal in `relation_candidate_adapter.py:274`).

### 4.5 Deterministic double-run (Wave03-08 + integrity + bridge)

* 8 test files, 94 tests total (85 pre-Wave08 + 9 Wave08 bridge tests).
* Under `PYTHONHASHSEED=0 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -W error`, both runs report identical `PASSED` node lists; 0 failed, 0 errors, 0 warnings, 0 new skips.

### 4.6 Constitutional discipline

* No push to remote (compare `origin/closure/hokom-taaqol-final-production-01` vs local HEAD).
* No tag created (`git tag --list 'wave08*'` empty).
* No merge to main (`git log main..HEAD` shows the Wave07 + Wave08 commits; `git log HEAD..main` empty).
* `vendor/Taaqol-GPT` `.git/` HEAD equals the bumped pin; no local edits to vendor source.

## 5. Allowed reaudit verdicts

* `VERIFIED_CLOSED` — Wave08 dual-carrier slice closed; full campaign still awaits Phase XI, S, M, C, I, E13, E14, V, E15.
* `PARTIALLY_VERIFIED` — return proven open defects to a bounded remediation session.
* `NOT_CLOSED` — escalation.
* `AUDIT_ABORTED_REPOSITORY_IDENTITY_MISMATCH` — if HEAD / branch / vendor pin does not match this handoff.

## 6. What Wave08 does NOT close for the FULL campaign

Even a `VERIFIED_CLOSED` Wave08 verdict does not close the parent campaign. Remaining phases:

* **XI** — AnswerAudit + GPT-R8 deterministic engine
* **S** — 19-layer SCG/Qiyas chain audit
* **M** — Maqayis independent audit
* **C** — CGPS01 audit
* **I** — typed integration contracts (Maqayis↔Hokom, CGPS01↔C13, Hokom↔Taaqol)
* **E13** — target/adapter/schema/report registry inventory
* **E14** — repository-wide coverage audit
* **V** — full vertical execution across all components
* **E15-A/B/C** — canonical rebind, deterministic canonical gate, final independent project audit
* **OWNER_RELEASE_PACKAGE**

---

No tag moved. No push. No merge. No cross-worktree write.
Vendor pin: `05c6668` → `bc9d1ea` (single commit).
