# Wave09 Implementation Handoff — AnswerAudit Deterministic Engine Closure

**Wave:** 9 (successor to Wave08 at binding-commit `3f46ca6`; post-audit remediation at `32a8e3b` verified via Phase A delta audit).
**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`.
**Scope:** Phases B (target inventory), C (contract audit), D (deterministic engine), E (real 5-span vertical), F (live integrity), G (evidence + ledger + handoff + binding).
**Deferred to next wave:** H (GPT-R8 gap audit), I (GPT-R8 native implementation), J (permit audit), K (complete DAG), L (full vertical), M-O (canonical manifest + gate + final audit).

## 1. What Wave09 delivered

| Commit | Concern |
|---|---|
| `b755db4` | Phase C + D: `deterministic_model_client.py` (3 test-only ModelClients) + `answer_audit_adapter.py` (thin bridge + `AnswerAuditOutcome`) + 21 deterministic tests (16 pass, 5 documented `TEST_NOT_APPLICABLE`) |
| `eaa9cec` | Phase E: `wave09_answer_audit_chain.py` (real 5-span vertical) + 10 real-vertical tests |
| `59d63cf` | Phase F: `answer_audit_integrity.py` (15 live counters) + 19 mutation-proof tests; also excluded `answer_audit_integrity.py` from source scans in `integrity_measurement.py` |
| `a38f057` | Wave09 evidence: `WAVE09_ANSWER_AUDIT_EXECUTION.json`, `WAVE09_ANSWER_AUDIT_INTEGRITY_SNAPSHOT.json`, `WAVE09_CLOSURE_SUMMARY.md`, `scripts/qiyas_canonical_closure_01_wave09_evidence.py` |
| (this commit) | Wave09 typed ledger + handoff |
| (next commit) | Wave09 report-binding manifest |

## 2. Native contract discovered (audit trail)

Read from `vendor/Taaqol-GPT/src/taaqqul_slot_geometry/audit/` at pin `bc9d1ea5ef45970f5f3ec132441e30fd54b3da52`:

| Contract | Value |
|---|---|
| `AnswerAudit` class | `audit/answer_audit.py:325` — impure shell wrapping pure kernel; owns ledger writes |
| `AnswerAudit.audit()` | `audit_audit.py:361-461` — signature `(prompt, claim_graph, gate, target_layer, evidence) -> AuditedAnswer` |
| `AnswerAudit.audit_with_reasonableness()` | `audit_audit.py:463-575` — Shape A GPT-R8 integration per docs/56 §4.1 |
| `AuditedAnswer` dataclass | `audit_audit.py:100-323` — frozen; certificate_allowed always False; birth invariants enforced |
| `ModelClient` protocol | `audit/model_client.py:33` — `runtime_checkable` with single method `complete(prompt: str) -> str` |
| `AuditReasonablenessStatus` | `audit/reasonableness_integration.py:42` — NOT_RUN / CARRIED / DEFERRED / R7_NOT_CONSUMED |
| Failure taxonomy | `core/failure_taxonomy.py` — vendor `FailureCode` StrEnum |

## 3. What Wave09 does NOT do

* **Does NOT** modify vendor source (`vendor/Taaqol-GPT` pin unchanged).
* **Does NOT** implement GPT-R8 runtime (still Phase I — deferred; `GPT_R8_LAW = PRESENT`, `GPT_R8_RUNTIME = NOT_SHIPPED` at bc9d1ea per vendor CLAUDE.md).
* **Does NOT** invoke a live provider (deterministic ModelClient only; test-only clients raise or return controlled payloads).
* **Does NOT** allow `certificate_allowed = True` on any outcome (docs/56 §2 B4 re-asserted at Hokom seam + verified by runtime counter).
* **Does NOT** construct `AuditedAnswer` directly (verified by AST scanner + zero-count assertion).
* **Does NOT** branch on provider text semantics (verified by regex scanner + tests W9.10..12).
* **Does NOT** self-declare `VERIFIED_CLOSED`.
* **Does NOT** modify sibling worktrees or Wave07/Wave08 binding manifests.

## 4. What the reaudit session should verify

### 4.1 Repository state
* HEAD on `closure/hokom-taaqol-final-production-01`.
* Vendor pin `bc9d1ea5ef45970f5f3ec132441e30fd54b3da52` unchanged.
* `git status --porcelain=v2 --untracked-files=all` returns zero bytes.
* Sibling worktrees `hokom-maqayis-v1`, `hokom-cgps01-2a6af17`, `hokom-cgps01-integration` clean at expected HEADs.
* Historical tag `hokom-canonical-gate-27-closed` untouched.
* Wave07 binding at `50c9961` and Wave08 binding at `3f46ca6` unchanged; bound artifact hashes recompute identical.

### 4.2 Native contract adoption
* `pipeline/taaqol_integration/audit_layer/answer_audit_adapter.py` imports `AnswerAudit`, `AuditedAnswer`, `ModelClient`, `AuditedTanzilBridgeVerdict`, `SlotGraph`, `EvidenceContract`, `TransitionGate`, `TraceLedger`, `Layer`, `Rank`, `FailureCode`, `Residual` from `taaqqul_slot_geometry.*` — the vendor's own bc9d1ea+ types, not shadows.
* No `AuditedAnswer(...)` constructor call anywhere in Hokom pipeline (AST scan; verified by test).
* Adapter's `to_vendor_stage_record`-style claim-graph construction uses `GenerationSource.TRANSITION_VERDICT` per docs/17 §1 source 3 (predecessor IS a licensed vendor verdict).

### 4.3 Deterministic engine substance
* Run `tests/taaqol_integration/test_answer_audit_deterministic.py` — expect 16 pass + 5 skipped (documented TEST_NOT_APPLICABLE with source references).
* Each `pytest.raises` in W9.16/W9.17/W9.18/W9.19/W9.20/W9.21 exercises the adapter's own boundary checks OR the AnswerAuditOutcome dataclass invariants — not circular.
* W9.2/W9.3/W9.4 verify that `TimeoutError`, `ConnectionError`, and `MalformedModelClient` (non-string payload) each convert to the corresponding `INTEGRATION_PROVIDER_*` typed marker, never to a fabricated success.

### 4.4 Real 5-span vertical
* Run `tests/taaqol_integration/test_answer_audit_real_vertical.py` — expect 10 pass.
* `WAVE09_ANSWER_AUDIT_EXECUTION.json`:
  * `answer_audit_native_call_count = 5`;
  * per-span records have distinct `prompt_fingerprint`/`response_fingerprint`/`output_fingerprint`;
  * every `predecessor_type = "AuditedTanzilBridgeVerdict"`;
  * every `native_result_type = "AuditedAnswer"`;
  * every `certificate_allowed = false`;
  * every `gate_state = "APPROVED"`, `successor_present = true`.

### 4.5 Live integrity
* Run `tests/taaqol_integration/test_answer_audit_integrity.py` — expect 19 pass.
* `WAVE09_ANSWER_AUDIT_INTEGRITY_SNAPSHOT.json`:
  * every declared counter (15 total) observed as 0 on the real corpus, except `ANSWER_AUDIT_NATIVE_CALL_COUNT = 5`;
  * meta counters `HARDCODED_ZERO_COUNTER_COUNT = UNMEASURED_COUNTER_COUNT = COUNTER_WITHOUT_MEASUREMENT_SITE_COUNT = 0`.
* Mutation proofs verify each source scanner and runtime rule flips non-zero on synthetic defect.

### 4.6 Deterministic double-run
* Wave03-06-07 + integrity + Wave08 bridge + Wave09 deterministic + Wave09 real-vertical + Wave09 integrity = 11 test files.
* Under `PYTHONHASHSEED=0 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -W error`, both runs must:
  * pass identically (0 failed, 0 errors, 0 warnings);
  * produce identical sorted node-ID lists (sha256 identity);
  * leave worktree strictly clean.

### 4.7 Constitutional discipline
* No push (compare `origin/closure/...` vs HEAD).
* No tag created (no `wave09*` refs).
* No merge to main.
* Vendor pin unchanged; no vendor edit.
* No sibling worktree write.

## 5. Allowed reaudit verdicts (per directive §G)

* `VERIFIED_CLOSED` — AnswerAudit deterministic engine slice closed.
* `PARTIALLY_VERIFIED` — return proven defects to bounded remediation.
* `NOT_CLOSED` — escalation.
* `AUDIT_ABORTED_REPOSITORY_IDENTITY_MISMATCH`.

## 6. What Wave09 does NOT close for the full Taaqol campaign

Even a `VERIFIED_CLOSED` Wave09 verdict does NOT close the full Taaqol closure target. Remaining phases:

* **H** — GPT-R8 law-to-runtime gap audit (fresh read-only session)
* **I** — GPT-R8 native implementation (Taaqol-branch first; then Hokom pointer bump)
* **J** — Permit audit (AnswerAudit + GPT-R8 + provider invocation permit requirements)
* **K** — Complete Taaqol native DAG audit (post-AnswerAudit + GPT-R8)
* **L** — Full Taaqol vertical execution (5 spans through GPT-R8 terminal)
* **M** — Taaqol canonical manifest
* **N** — Taaqol canonical gate (deterministic double-run of complete suite)
* **O** — Final independent Taaqol audit

## 7. Live-provider validation

`LIVE_PROVIDER_VALIDATION_STATUS = NOT_REQUIRED_FOR_DETERMINISTIC_ENGINE_CLOSURE` per Phase G. If credentials become available in a future session, a separate live-provider validation artifact can be added; that is a distinct classification, not a blocker for Wave09 closure.

---

No tag moved. No push. No merge. No cross-worktree write.
Vendor pin `bc9d1ea` unchanged. Wave07/Wave08 bindings unchanged.
