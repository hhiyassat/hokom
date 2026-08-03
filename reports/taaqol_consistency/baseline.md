# Taaqol Consistency Audit — Baseline

**Stage:** HOKOM-TAAQOL-LATEST-CONSISTENCY-AND-FINALIZATION-01  
**Hokom HEAD:** b706ced  
**Hokom HEAD Full:** b706ced61b4eeb7438959d318987f4fd7cae0e8e  
**Timestamp:** 2026-07-21  
**Canonical Manifest:** reports/canonical_gate/closure_manifest.b706ced.json  

## Git State

| Field | Value |
|-------|-------|
| Hokom tracked clean | true |
| Hokom vendor clean | true |
| Untracked files | doc/*, reports/canonical_gate/*, reports/segmenter_comparison/*, reports/semantic_audit/, hokom_demo.jsonl |
| Taaqol submodule PIN | 35381739410071ac21dd96702ecbb2acb493f90d |
| Taaqol submodule (git submodule status) | 35381739410071ac21dd96702ecbb2acb493f90d vendor/Taaqol-GPT |

## Runtime

| Field | Value |
|-------|-------|
| Canonical runtime (macOS) | Python 3.12.4 |
| Sandbox runtime | Python 3.10.12 (Linux) |
| Taaqol requires-python | >=3.11 |
| Taaqol StrEnum provider | enum.StrEnum (3.11+) |

## Canonical Core (b706ced baseline)

| Metric | Value |
|--------|-------|
| run_1_passed | 5333 |
| run_2_passed | 5333 |
| failures | 0 |
| skips | 0 |
| node_ids_equal | true |
| outcomes_equal | true |

## Canonical Probes

| Metric | Value |
|--------|-------|
| total | 21 |
| failures | 0 |
| failing_probes | [] |

## Corpus Contracts

| Metric | Value |
|--------|-------|
| total_tokens | 129 |
| failures | 0 |
| violations | [] |

## Routing Contracts

| Metric | Value |
|--------|-------|
| total_tokens | 129 |
| POST_SEGMENTATION_ROUTING_VIOLATIONS | 0 |
| ROOT_AFTER_CLOSED_BOUNDARY | 0 |
| SURFACE_PROVENANCE_VIOLATIONS | 0 |
| ARTICLE_REATTACHMENT_VIOLATIONS | 0 |

## Jamid Aalam Contracts

| Metric | Value |
|--------|-------|
| total_tokens | 7 |
| JAMID_AALAM_BOUNDARY_VIOLATIONS | 0 |
| ROOT_AFTER_JAMID_AALAM_BOUNDARY | 0 |
| PROCLITIC_COUNTED_IN_AALAM_ROOT | 0 |
| JAMID_MISCLASSIFIED_AS_MABNI | 0 |
| MABNI_INVENTORY_MODIFIED | 0 |

## Artifacts

| Metric | Value |
|--------|-------|
| commit_bound | true |
| stale_artifacts | 0 |
| closure_eligible | true |
