# P3_ROOT_AUTHORITY_DECISION (CW2)

**Decision: the single authoritative P3 root owner is the production engine
`pipeline/p3_candidate/root_resolution` (entrypoint `resolve_root_pipeline`).**
Decided by constitutional ownership + runtime connectivity, NOT by coverage,
recency, API, informal "official" labels, or test greenness.

## Comparison matrix
| criterion | A. production `pipeline/p3_candidate` | B. H2RS H1/H2 bridge | C. `root_by_alignment.py` |
|---|---|---|---|
| production runtime-connected | **YES** (`hokom_pipeline.py:600`) | NO | NO |
| input contract | P2 projection (`RootProjection`) | raw surface via qiyas bridge | vocalized word + awzan CSV |
| output contract | `RootCandidate` (directive ACCEPT/DEFER/BLOCK, canonical_root) | `MorphologyOwnerCertificate` (verdict+fields) | `AlignmentResult` (root,wazn) |
| consumed by P4A/P4C/P5 | **YES** | no | no |
| calls a foreign engine | **NO** ("لا استيراد من hr2s") | is the foreign engine | standalone |
| determinism | yes | yes (trace canonicalized) | yes |
| DEFER/BLOCK support | yes | yes | limited |
| repo location | committed pipeline (production) | untracked `provider/` (/fractal) | `/fractal/hussein/clean_code` (external) |
| migration cost if chosen | **zero (already owner)** | high (rewire hokom_pipeline + regression) | very high |

## Rationale (§12–§14)
Production `hokom_pipeline.hokom()` already calls **only** `resolve_root_pipeline`;
P4A/P4B/P4C/P4D + word_class + P5 already consume its `RootCandidate`; it imports
no foreign root engine. Choosing H2RS or root_by_alignment would require a real
production migration (rewire + regression) with no constitutional benefit —
§14 forbids choosing them "because they certified more / are newer / nicer API."
Therefore the incumbent production engine is the owner.

## Loser roles (no co-authority)
- **H2RS H1/H2 bridge + `MorphologyOwnerCertificate`** → `COMPARISON_ONLY / AUDIT`.
  Its root field is a **proposal/evidence**, not an authority. The earlier
  62,591-token / 8,175-CERTIFIED ledger (`fca3d472…`) is **NONCANONICAL
  diagnostic evidence** — it was produced by a non-production engine and must NOT
  be treated as the P3 root universe. A canonical corpus root run, if needed,
  goes through `pipeline/p3_candidate`.
- **`root_by_alignment.py`** → `AUDIT_ONLY`; retract any doc calling it "official."
  Its output cannot override P3.

## Enforcement
`CLOSURE_CW1_CW2/test_single_root_authority.py` (4/4 pass) is a **structural
regression test** that fails if a second root authority is imported into
production or if `hokom_pipeline` gains a competing root-producing call.

## Downstream one-root contract
`RootCandidate` (from `pipeline/p3_candidate`) is the single canonical root fact.
P4A/P4C/P5 consume it or its typed derivative; they do not choose among engines.

```
P3_ROOT_AUTHORITIES_ACTIVE = 1
CHOSEN_OWNER = pipeline/p3_candidate/root_resolution (resolve_root_pipeline)
H2RS_ROOT = COMPARISON_ONLY   ROOT_BY_ALIGNMENT = AUDIT_ONLY
```
