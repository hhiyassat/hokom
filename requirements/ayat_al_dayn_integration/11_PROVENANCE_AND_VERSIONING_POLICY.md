# 11 — PROVENANCE AND VERSIONING POLICY

**Document ID:** `R0-11-PROVENANCE`  
**Phase:** R0 — Requirements Package  
**Date:** 2026-08-01  
**Status:** REQUIREMENTS_READY

---

## 1. Pinned Identifiers

| Identifier | Value | Source | Mutability |
|---|---|---|---|
| `VENDOR_SHA` | `35381739410071ac21dd96702ecbb2acb493f90d` | `runtime_vendor_sha` column in live CSV — every row | FROZEN — OWNER_DECISION_REQUIRED to change |
| `HOKOM_HEAD` | `8e37b738ece7183818189146912cb14e3dce3a07` | git log at ratification | Recorded; Hokom may evolve but vendor is frozen |
| `TARGET_MODE` | `PINNED_VENDOR_SHA` | Constitution ratification order | Cannot change without amendment |
| `CORPUS_SHA256` | `6bd635a05530965f13f76cf003f7738130badec6981bcb0e73f2465d386e1ed7` | Corpus file hash | FROZEN for this phase |

---

## 2. Trace ID Policy

### Mandatory Rule
Every `trace_id` field in every artifact, adapter output, and phase certificate **must** come from a live `PipelineTrace` object. No exceptions.

### Forbidden Patterns
```python
# FORBIDDEN — synthetic prefix
trace_id = f"HOKOM_P5:{uuid.uuid4()}"
trace_id = f"HOKOM_TRACE:{token_index}"
trace_id = f"SYNTHETIC_{stage_id}"

# FORBIDDEN — hardcoded
trace_id = "test-trace-001"
trace_id = ""
trace_id = None
```

### Required Pattern
```python
# REQUIRED — from live PipelineTrace
pipeline_trace = PipelineTrace.from_run(run_id=...)
trace_id = pipeline_trace.trace_id  # This is the only valid source
```

**Violation:** Any artifact with a synthetic trace_id enters `INVALID` state automatically. No override. No exception.

---

## 3. VENDOR_SHA Embedding

Every produced artifact (adapter output, phase certificate, decision record) must embed `VENDOR_SHA`. This was verified in the live run — all 129 tokens in the CSV carry `runtime_vendor_sha = 35381739410071ac21dd96702ecbb2acb493f90d`.

Format for structured artifacts:
```json
{
  "vendor_sha": "35381739410071ac21dd96702ecbb2acb493f90d",
  "hokom_head": "8e37b738ece7183818189146912cb14e3dce3a07",
  "trace_id": "<from PipelineTrace>",
  "produced_at": "<ISO 8601 timestamp>"
}
```

---

## 4. Carrier Versioning

Every typed carrier (RegistryEntry, LicensingBoundaryVerdict, DalOnlyCandidate, etc.) must:

1. Be frozen (`frozen=True` or equivalent immutability)
2. Carry `trace_ref` linking to `PipelineTrace`
3. Carry `vendor_sha` or inherit it from the wrapping artifact
4. Carry a schema version field if the carrier is serialized to storage
5. Be validated against its schema invariants at construction time

### Schema Freeze Gate
A carrier schema is "frozen" when:
- Its field list is finalized (no additions without OWNER_DECISION_REQUIRED)
- Its invariants are documented in the relevant requirements file
- At least one test exists that verifies each invariant
- The carrier has been read from `registry_contract.py` and the field mapping is documented in `08_HOKOM_TAAQOL_ADAPTER_MATRIX.csv`

---

## 5. File Versioning

| File class | Version scheme | Notes |
|---|---|---|
| Requirements files (R0-*) | `R0-{NN}-{NAME}` — immutable at R0 close | Amendments require new version suffix |
| Phase certificates | `{PHASE_ID}_CLOSURE.json` — one per phase | Immutable at emit |
| Block records | `{PHASE_ID}_BLOCK_{TIMESTAMP}.json` | Append-only |
| Implementation files | Tracked by Hokom git HEAD | AUTONOMOUS_COMMIT_MODE = 0 |
| Vendor files | Tracked by VENDOR_SHA | VENDOR_UPDATE_ALLOWED = 0 |

---

## 6. Non-Modification Policy

The following files are **frozen** — no modification without OWNER_DECISION_REQUIRED:

1. `vendor/Taaqol-GPT/**` (entire submodule at pinned SHA)
2. Constitution file: `HOKOM_TAAQOL_MASTER_EXECUTION_CONSTITUTION_01.md`
3. This requirements package once R0 is CLOSED (any amendment = new R0_AMENDMENT document)
4. Phase closure certificates once emitted
5. Corpus: `reports/ayat_al_dayn_demo/ayat_al_dayn_taaqol_layers.csv`

---

## 7. Git Operations Policy (binding)

```
No commit
No tag
No push
No merge
No git reset --hard
No git clean
No git checkout .
No git restore .
No git stash
No git add .
No git add -A
No git commit -a
```

All implementation work is tracked through phase certificates only. Git state is the owner's responsibility.
