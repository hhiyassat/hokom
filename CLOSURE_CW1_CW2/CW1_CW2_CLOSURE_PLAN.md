# CW1 + CW2 — Reproducible Baseline + Single Root Authority — PLAN

Standing rule honored: **do not commit until review** (§24). This plan is
Phase-A: decision + curated inventory + exact proposed commits. Three items are
`OWNER_DECISION_REQUIRED` and are NOT executed here (corpus commit, production
`p4_verdict` rename, branch creation/commits).

## Proposed branch
`feature/closure-cw1-cw2-foundation-01` off `closure/hokom-taaqol-final-production-01`
(never commit to the protected closure branch). H2RS work → its own branch on `/fractal`.

## CW1 — accepted-apparatus disposition
| component | current | disposition |
|---|---|---|
| `pre_segmentation_root_path_gate/` | untracked | **KEEP_AS_AUDIT_TOOL** — built to fix a **misdiagnosed** cycle; NOT wired to production; keep as governance/audit, do NOT productize as a routing replacement (§5) |
| `segmentation_to_p3_entry/` | untracked | **KEEP_AS_AUDIT_TOOL** (same; valuable for lineage/conservation, not a production gate) |
| `gres_p3_open_ownership_audit/` | untracked | **OBSOLETE_AFTER_AUDIT_CORRECTION** — its "circular dependency" premise was corrected; keep FINDINGS.md as history, mark superseded |
| `gres_p3_rebaseline/` | untracked | **KEEP_AS_AUDIT_TOOL** — corpus-manifest governance is independently valuable |
| `wave11_layer_integration/` | untracked | **KEEP_AND_PRODUCTIZE (CW4)** — L5/L6 boundary; defer wiring to CW4 |
| `provider/` (H2RS, /fractal) | untracked | **KEEP_AS_COMPARISON_ONLY** — root field is proposal/evidence, not authority (CW2) |
| H2RS 62,591 ledger (`/tmp/h2rs_p3_run1`) | /tmp | **OBSOLETE** as canonical — noncanonical diagnostic (non-production engine) |
| pre-seg / P3-entry universes (`/tmp/*`) | /tmp | **REGENERABLE_ARTIFACT** — replace /tmp freeze with committed manifest + regen command + verify test |
| `wave11_ancestry.py` | untracked stray | **OWNER_DECISION_REQUIRED** — track it (needs maqayis_v2/word_tree — CW4) |
| `pipeline/taaqol_integration/maqayis_v2/` | untracked | **OWNER_DECISION_REQUIRED** — vendor/package (CW4) |
| `data/quran-uthmani.txt` | gitignored | **OWNER_DECISION_REQUIRED** — see corpus strategy |
| `CLOSURE_CW1_CW2/` (this) | untracked | **KEEP_AND_COMMIT** — decision + ownership test |

## CW1 — corpus reproducibility (§7, OWNER_DECISION_REQUIRED)
`data/quran-uthmani.txt` = Tanzil Uthmani, sha256 `1130fc9f…471ff`, 77,374 tokens, gitignored.
Options (pick one):
- **A. Commit it** (un-ignore) if licensing permits — simplest fresh-clone repro.
- **B. SHA-pinned materialization**: a committed `fetch_corpus.py` that downloads Tanzil to a pinned SHA + a verify test. Needs an approved source URL.
- **C. Reference an immutable committed asset** elsewhere in the org.
Recommendation: **A** if licensing allows (Tanzil is redistributable under its terms); else **B**. Record `CORPUS_ID=HOKOM_QURAN_UTHMANI_TANZIL`, SHA, command, provenance, count.

## CW1 — /tmp freeze replacement
Replace each `/tmp/*` freeze with: committed `*.freeze.json` (manifest: source SHA, command, expected count, expected output SHA) + a regen-and-verify test. The universes become `REGENERATED_ON_DEMAND_FROM_PINNED_INPUTS`. **Do not** canonize the H2RS ledger (CW2 loser engine).

## CW1 — frozen-token discipline (§9)
| token | verdict |
|---|---|
| `IFADAH…LAYER5_FROZEN…`, `IRAB…LAYER6…` | KEEP (assert-enforced) |
| `SEGMENTATION_INPUT_UNIVERSE=FROZEN`, `P3_ENTRY_UNIVERSE=FROZEN`, `PRE_SEGMENTATION_CORPUS_GATE_FROZEN` | **DOWNGRADE** → `REGENERABLE_VERIFIED` (add enforcing regen test; drop "FROZEN" until committed) |
| `H2RS_P3_ROOT_PROVIDER_CORPUS_GATE_FROZEN` | **RETRACT** → noncanonical (non-production engine, CW2) |

## CW1 — naming correction (§10, OWNER_DECISION_REQUIRED — production edit)
Rename `p4_verdict` → `phonological_slot_verdict` in exactly **3 files**:
`pipeline/pre_root/host_routing.py`, `pipeline/pre_root/pre_root_decision.py`, `hokom_pipeline.py`.
Pure rename (no behavior change); update the 3 callers + any test/doc referencing it. This removes the naming drift that caused the false-cycle diagnosis. Held for approval (production change).

## CW1 — L5 "18/18" claim (§11)
Test file **does not exist** on disk. Resolution: **retract "18/18"** and mark L5 test coverage as `TESTS_ABSENT` in the handoff/manifest; optionally author a NEW suite against the frozen L5 contract, labeled new (not recovered). Do **not** conflate. (Documentation-only.)

## CW2 — root authority: **CLOSED by decision** (see `P3_ROOT_AUTHORITY_DECISION.md`)
Owner = `pipeline/p3_candidate`. H2RS = comparison-only. root_by_alignment = audit-only.
Structural test `test_single_root_authority.py` (4/4) enforces `AUTHORITIES_ACTIVE=1`.
**Corpus re-run through the chosen owner (§17):** the production P3 already runs per-token
live in `hokom_pipeline`; a batch run over the P3-entry universe through `resolve_root_pipeline`
(not H2RS) is the canonical corpus run — proposed as the first commit's accompanying script,
held with the corpus decision.

## Proposed commits (feature branch, held for approval)
1. `CLOSURE_CW1_CW2/` — decision + ownership regression test (this).
2. corpus reproducibility (option A/B) + manifest + verify test.
3. committed regenable universes + freeze manifests + regen tests (drop /tmp).
4. `p4_verdict → phonological_slot_verdict` rename (3 files) + updated callers/tests.
5. token downgrades/retractions + L5 claim retraction (docs).
6. curated move of KEEP audit tools into a tracked `audit/` area with READMEs.

## NOT in this wave
CW3 (Wave11 deps), CW4 (P6–P12 + L5/L6/L7 wiring), CW5 (coverage). No production behavior change beyond the held rename.
