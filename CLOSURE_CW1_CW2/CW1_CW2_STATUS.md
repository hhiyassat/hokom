# CW1 + CW2 — Phase B Status

Branch `feature/closure-cw1-cw2-foundation-01` (off closure HEAD c768cf4; protected
ref untouched). No push/PR/merge/tag. Pre-existing dirty files (evidence_adapter.py,
full_target_orchestrator.py, .DS_Store) are **not** absorbed.

## CW2 — Single P3 root authority = CLOSED (decision + proof)
`P3_ROOT_AUTHORITY = pipeline/p3_candidate/root_resolution → resolve_root_pipeline`
(see `P3_ROOT_AUTHORITY_DECISION.md`). Proven:
- `test_single_root_authority.py` 4/4: `P3_ROOT_AUTHORITIES_ACTIVE = 1`; no foreign
  root authority imported in production; p3_candidate does not delegate to H2RS.
- Production `hokom()` sample (150 corpus tokens) via `resolve_root_pipeline`:
  ACCEPT 44 / DEFER 44 / BLOCK 1 / None(closed) 61; real roots (حمد, ملك, عبد, عين, قيم).

### Loser producers — demoted (no co-authority)
- **H2RS H1/H2 (`MorphologyOwnerCertificate`)** → `COMPARISON_ONLY`. Its root field is
  evidence, not authority. The earlier 62,591/8,175 ledger (`fca3d472…`) is
  **NONCANONICAL** — produced by a non-production engine; NOT canonized.
- **`root_by_alignment.py`** → `AUDIT_ONLY`; any doc calling it "official root
  authority" is retracted (its output cannot override P3).

### Canonical production-root corpus ledger — PENDING
The full 62,591 run through `resolve_root_pipeline` (~43 min @ ~24 tok/s) is scripted
and sampled; the frozen ledger awaits (a) the approved corpus source (CW1) and
(b) a dedicated run gate. It will replace the noncanonical H2RS ledger.

## CW1 — Reproducible baseline = BLOCKED on corpus source
Done:
- **Naming drift fixed:** `p4_verdict → phonological_slot_verdict` (3 production files
  + test); **behavior-neutral proven** (30/30 route decisions identical; test_pre_root
  99 passed). Removes the terminology collision that caused the earlier false-cycle
  diagnosis.
- **Corpus recipe (Strategy B):** `corpus_materialize.py` — SHA-pinned, count-verified,
  owner-supplied source; refuses on mismatch; STOPs `AUTHORITATIVE_CORPUS_
  MATERIALIZATION_SOURCE_REQUIRED` when no approved source is given.
- **Token discipline:** `H2RS_P3_ROOT_PROVIDER_CORPUS_GATE_FROZEN` = RETRACTED
  (non-production engine). SEGMENTATION_INPUT/P3_ENTRY/PRE_SEG "FROZEN" =
  DOWNGRADED to `REGENERABLE_VERIFIED` (regen from committed source + verify).
- **L5 "18/18" = RETRACTED** — the test file does not exist on disk; L5 coverage is
  `TESTS_ABSENT`. Any future suite must be labeled NEW, not recovered history.

Blocked (owner action):
- **`AUTHORITATIVE_CORPUS_MATERIALIZATION_SOURCE_REQUIRED`** — I cannot establish an
  approved, stable source URL / immutable asset (no verified source available; not
  permitted to invent one or substitute MASAQ). Until supplied,
  `FRESH_CLONE_CAN_REPRODUCE = NO`.

## RC comparison vs the 19-stage audit
| RC | original finding | action | status |
|---|---|---|---|
| RC2 — multiple root authorities | 3 producers; corpus certified by non-production engine | decision + structural test + demotion | **CLOSED** (`AUTHORITIES_ACTIVE=1`) |
| RC5 — naming/contract/doc drift | `p4_verdict`=phonological; L5 18/18; token overclaims | rename + retractions + downgrades | **CLOSED** |
| RC1 — uncommitted/ephemeral architecture | untracked/tmp; fresh-clone=NO; corpus gitignored | branch + commits + corpus harness | **PARTIAL** — closes on approved corpus source (CW1 blocker) |

## Verdicts
```
CW2_SINGLE_ROOT_AUTHORITY        = CLOSED (canonical ledger pending corpus source + run)
CW1_REPRODUCIBLE_BASELINE        = BLOCKED (AUTHORITATIVE_CORPUS_MATERIALIZATION_SOURCE_REQUIRED)
FRESH_CLONE_CAN_REPRODUCE        = NO (until corpus source approved)
P3_ROOT_AUTHORITIES_ACTIVE       = 1
```
