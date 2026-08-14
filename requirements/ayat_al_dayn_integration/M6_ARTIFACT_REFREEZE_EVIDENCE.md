# M6 — FINAL CANONICAL ARTIFACT RE-FREEZE (owner-authorized 2026-08-14/15)

Governed re-freeze of the canonical Ayat al-Dayn artifacts onto the approved
Taaqol vendor `bc9d1ea5` (see [M5_VENDOR_GOVERNED_UPGRADE_REFREEZE.json]).

## Authorization condition — PROVENANCE-ONLY, ZERO LINGUISTIC DELTA (proven)

Regenerating `reports/ayat_al_dayn_demo/ayat_al_dayn_results.csv` at the approved
vendor changed its SHA:

```
OLD (SUPERSEDED) CANONICAL_CSV_SHA = f9d2410e22f6964c79867048b8f899d4d86632f33f5634422e90b1544fd52fa4
NEW (APPROVED)   CANONICAL_CSV_SHA = 886e38640ff7bff7a87e44034b5fca26550fea1b66b6ce06c24ae14623aacbc3
```

Column-by-column diff of the 129 rows (old frozen CSV vs regenerated CSV):

```
COLUMNS_CHANGED  = { claim_key: 37, evaluation_id: 37 }
LINGUISTIC_DELTA = 0
VERDICT          = PROVENANCE_ONLY_ZERO_LINGUISTIC_DELTA
```

- Only `claim_key` and `evaluation_id` changed, in the 37 Taaqol-evaluated rows.
  These are Taaqol evaluation-identity fields that hash in the vendor state; they
  changed legitimately with the governed upgrade `05c6668d → bc9d1ea5`.
- Every linguistic column is byte-identical: `original_surface`,
  `normalized_surface`, `segment_host`, `word_class`, `word_class_verdict`,
  `pipeline_verdict`, `root`/`wazn`/`bab`/`masdar` (where present), slot fields.
- Deterministic: the regenerated CSV produced SHA `886e3864…` identically in the
  final audit run and an independent re-run.

## Binding (non-self-referential)

- `LINGUISTIC_BASE_HEAD  = d3d04d233215a4760acfb6909403257349982f77` (governed re-baseline; supersedes b19cd9a)
- `AUDITED_ARTIFACT_HEAD = 24aba909d91132ea8f395d52853d2a2eeaf0700d` (the immutable commit that regenerated the canonical artifacts)
- Manifest: `reports/canonical_gate/closure_manifest.24aba90.json`
  (`artifact_commit = 24aba909…`, digests of the 3 canonical files). The test
  binds to the immutable `AUDITED_ARTIFACT_HEAD`, not the moving HEAD — resolving
  the circular binding.
- `SUPERSEDED`: prior canonical CSV SHA `f9d2410e…` and linguistic base `b19cd9a…`
  are retained as historical (SUPERSEDED_*), not erased.
