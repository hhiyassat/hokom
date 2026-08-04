# QIYAS-...-CANONICAL-CLOSURE-01 — Wave08 Dual-Carrier Closure

**Status:** `IMPLEMENTED_PENDING_INDEPENDENT_AUDIT`
**Wave08 scope:** vendor pin bump (05c6668 → bc9d1ea) + dual-carrier StageExecutionRecord mirror.

## Vendor pin

Old (Wave07): `05c6668dfb95d9238cff5df1d8bc73d0664bccb3`
New (Wave08): `bc9d1ea5ef45970f5f3ec132441e30fd54b3da52` (`vendor/Taaqol-GPT` refs/heads/main @ bc9d1ea)

## Runtime compatibility empirical proof

The Wave07 typed-downstream artifact (RUN1/RUN2 JSON) regenerates BYTE-IDENTICAL at bc9d1ea:

* `RUN1_TYPED_DOWNSTREAM_EXECUTION.json` sha256 unchanged: `adbfc275f5984621cb7a959ff7bfcd1ceea71090c0a392370d74bf59444c966f`
* `RUN2_TYPED_DOWNSTREAM_EXECUTION.json` sha256 unchanged: identical
* `INTEGRITY_SNAPSHOT.json` sha256 unchanged: `83f18a305415a540ab42d7a1d0e77fafa3b47f0e09d2d6db4f16c24186f03268`
* `DETERMINISM_COMPARE.json` sha256 unchanged: `444bee766d7fbfd075c9d0f27ed9627b7ada0f072f2ea05dee41af300e1d215c`

Wave07 report-binding manifest (at commit 50c9961) therefore remains valid for its bound artifacts.

## Wave08 dual-carrier mirror over the real Ayat corpus

* Hokom spans processed: 5
* Vendor mirror spans built: 5
* All spans mirror_ok: True

### Vendor StageTransitionState distribution across all records

| State | Count |
|-------|-------|
| `EXECUTED` | 40 |

## Rejections

* Total vendor `__post_init__` rejections: 0

Zero rejections means every Hokom typed outcome round-tripped into a vendor StageExecutionRecord without violating any of vendor's 9 constructional invariants (residual monotonicity, remediation hints on DEFER, failure_code on BLOCK, applicability consistency, no implicit rank upgrade, executed→trace, etc.).

## Artifact hashes

- WAVE08_VENDOR_STAGE_EXECUTION_RECORDS.json — sha256=0159192a408b4c366f121d3ffb004f1ea23098e268e38add31cf8c8e3594c150

## What this Wave08 does NOT do

* Does NOT replace `DownstreamStageOutcome` — both carriers coexist.
* Does NOT adopt vendor's token-level `run_native_corpus` — Hokom retains span-level composition authority.
* Does NOT migrate AnswerAudit or GPT-R8 — vendor confirms both remain `MODEL_CLIENT_REQUIRED` / runtime-NOT-shipped.
* Does NOT self-declare `VERIFIED_CLOSED` — a fresh strictly read-only audit session must verify Wave08 HEAD.
