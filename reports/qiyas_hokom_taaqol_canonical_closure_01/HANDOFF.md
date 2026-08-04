# QIYAS-HOKOM-TAAQOL-MAQAYIS-CGPS01-FULL-MAXIMUM-CANONICAL-CLOSURE-01
# Implementation Session Handoff — Taaqol Slice

**Session type:** Implementation (T0–T4).
**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`.
**IMPLEMENTATION_CONTENT_HEAD (of this handoff document):** `<to be recorded in the next commit — see binding manifest>`.
**Session did NOT author:** any tag move; any push; any merge; any change to `vendor/Taaqol-GPT`; any change to `hokom-maqayis-v1`, `hokom-cgps01-2a6af17`, `hokom-cgps01-integration`.

The historical tag `hokom-canonical-gate-27-closed` is untouched.

## 1. What this session did

| Phase | Concern | Commit(s) |
|---|---|---|
| T0 | Preflight + `.claude/` gitignore | `32506a6` |
| T3 | RelationClosure/Ifadah residual propagation (removed hardcoded `residual_ids: []`) | `ca65c43` |
| T1 | Live integrity measurement framework + 21 mutation-proof tests | `2c3a78f` |
| T2 | Wave07 test suite (17 tests) — typed REFUSED for Hukm/Tanzil/Mafhum, three end-to-end BLOCK tests via real vendor codes, missing-predecessor + wrong-type coverage, §W6.6 docstring correction | `3d0be17` |
| T4 | Real-Ayat rerun + live integrity snapshot + closure summary | `f748208` |
| T4 (docs) | Wave07 typed ledger + handoff | (this commit) |
| — (docs) | Two-step report binding manifest | (next commit, per REPAIR F pattern) |

## 2. What this session did NOT do

Per the campaign directive:

* **Phase T5** — fresh strictly read-only audit against the final HEAD. The directive is explicit: an implementation session cannot issue the final VERIFIED_CLOSED verdict; only a separately-started fresh audit session may. The owner should launch that session against the HEAD produced by this branch.
* **Phase XI** — AnswerAudit + GPT R1–R8 deterministic engine. Provider adapter infrastructure does not yet exist in Hokom's production tree; this phase would require substantial new implementation (ModelClient test double, provider protocol wiring, 10+ behaviour paths). Left as a dedicated future session so this Taaqol slice can be audited on its own merits first.
* **Phase S** — 19-layer SCG/Qiyas chain audit. Requires independent discovery of the SCG registry and per-layer runtime verification.
* **Phase M** — Maqayis independent audit against `hokom-maqayis-v1` (HEAD `e7e63f55`). Directive §11 requires a fresh session in that worktree.
* **Phase C** — CGPS01 audit against `hokom-cgps01-2a6af17` (HEAD `aaec561c`, tag `cgps01/verified-closed-aaec561`) and `hokom-cgps01-integration` (HEAD `0953b476`). Read-only audit; separate session per §12.
* **Phase I** — typed integration contracts (Maqayis→Hokom, CGPS01→C13, Hokom→Taaqol). Depends on M + C completion.
* **Phase E13** — target/adapter/schema/report registry inventory (G0, LGE, X0R, USM, L1, provider adapters, etc.).
* **Phase E14** — repository-wide coverage matrix.
* **Phase V** — full vertical execution across every component. Requires all prior phases.
* **Phase E15-A/B/C** — canonical rebind, deterministic canonical gate, final independent audit. Owner-driven.
* **Owner release package** — prepared only after Phase E15-C returns `VERIFIED_CLOSED`.

## 3. Verification the owner-audit session should perform

Focused Taaqol integration scope (this session's blast radius):

1. Repository preflight:
   * HEAD is on `closure/hokom-taaqol-final-production-01`.
   * `git status --porcelain=v2 --untracked-files=all` returns zero bytes.
   * `vendor/Taaqol-GPT` HEAD is `05c6668dfb95d9238cff5df1d8bc73d0664bccb3`, clean.
   * Sibling worktrees `hokom-maqayis-v1`, `hokom-cgps01-2a6af17`, `hokom-cgps01-integration` are clean; their HEADs are unchanged from the reaudit-02 baseline.

2. Live integrity framework:
   * Read `pipeline/taaqol_integration/integrity_measurement.py` end-to-end.
   * Verify every counter in `DECLARED_COUNTERS` is backed by a `SourceAntiPatternRule`, a `RuntimeRecordRule`, or a `structural_counters` derivation.
   * Verify the AST-based verdict-construction detector does not match docstring pseudocode (`test_baseline_production_source_scan_all_zero` proves this at test time).
   * Run `tests/taaqol_integration/test_integrity_counters_live.py` — expect 21 pass.

3. Wave07 test suite:
   * Run `tests/taaqol_integration/test_c13_wave07_typed_closure_completion.py` — expect 17 pass, including three end-to-end BLOCK tests (`test_w7_10`, `test_w7_11`, `test_w7_12`).
   * Verify each BLOCK test asserts `out.classification == BLOCK`, `out.blocked is True`, `out.failure_code == <real vendor BLOCK code>`, `out.trace_ref`.

4. Residual propagation:
   * Grep `residual_ids: []` in `pipeline/taaqol_integration/evidence_producers/wave06_downstream_chain_typed.py` — expect only one match at the `ifv is None` branch (labelled "extraction unavailable").
   * Inspect `RUN1_TYPED_DOWNSTREAM_EXECUTION.json` — the `relation_closure` and `ifadah` per-stage records under each span should have non-empty `residual_ids`.

5. Deterministic double-run:
   * Run the full selected suite (7 test files: Wave03 supplement + relation_closure + Wave04 + Wave05 + Wave06 + Wave07 + integrity_counters_live) twice under `PYTHONHASHSEED=0 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -W error`.
   * Verify node-ID sha256 identical between runs; 0 failed / 0 errors / 0 warnings / 0 new skips.

6. Report binding:
   * Verify the binding manifest at `reports/qiyas_hokom_taaqol_canonical_closure_01/BINDING_MANIFEST.json` records the correct `IMPLEMENTATION_CONTENT_HEAD`, `REPORT_COMMIT_HEAD`, and `REPORT_BINDING_HEAD`.
   * Re-hash each bound artifact and compare against the manifest's `sha256` field.

7. Constitutional discipline:
   * Confirm `hokom-canonical-gate-27-closed` still points to its historical commit (`git rev-parse hokom-canonical-gate-27-closed`).
   * Confirm no push occurred (compare `origin/closure/hokom-taaqol-final-production-01` against local HEAD — they should differ).

## 4. Allowed reaudit verdicts

Per the directive:

* `VERIFIED_CLOSED` — all listed sub-verdicts pass; Wave07 slice is closed.
* `PARTIALLY_VERIFIED` — some gap remains; return only the proven open defects to a bounded remediation session on this same branch.
* `NOT_CLOSED` — a foundational failure was found; escalate.
* `AUDIT_ABORTED_REPOSITORY_IDENTITY_MISMATCH` — if HEAD / branch / vendor pin does not match this handoff.

## 5. What this slice does not close for the FULL campaign

Even if reaudit returns `VERIFIED_CLOSED` for the Taaqol integration slice, the full campaign verdict remains **NOT YET CLOSED** because Phases XI, S, M, C, I, E13, E14, V, E15-A/B/C are all pending. The owner should either:

* schedule the next slice (XI or S is the natural continuation), or
* declare the Taaqol integration slice sufficient for the current release and defer the remaining phases to a later campaign.

## 6. Discovery output for the owner

A prior read-only discovery (see conversation) found that `vendor/Taaqol-GPT` `origin/main` has advanced from our pin `05c6668` to `bc9d1ea` (30 commits, 3 new subsystems: `runtime/`, `x0r/`, `usm/`). The vendor's new `StageExecutionRecord.__post_init__` invariants would close several Hokom-side compensating patterns at the type level. That vendor pin bump is **not** performed in this session and is left as a separate decision.

---

No tag moved. No push. No merge. No cross-worktree write.
