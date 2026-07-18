# تقرير التسليم — R-6 → R-10

Repository: /Users/husseinhiyassat/hokom
Date: 2026-07-16
Methodology per stage: plan → inspect → tests → implementation → focused tests → full baseline → node-ID diff → report

## Original baseline
- reports/refactoring/baseline_ids.txt = 446 original node IDs (pre-pre-root)
- Live reference baseline at start of R-6 = 546 passed, 52 subtests
  (command: `python3 -m pytest -q tests/ --ignore=tests/integration`)

## Current test total
- Reference suite: 590 passed, 52 subtests passed
  (546 preserved + 44 new R-10 unit tests in tests/p2_projection + tests/p3_candidate)
- New R-10 integration tests: tests/integration/test_root_pipeline_r10.py = 14 passed
- Total new R-10 coverage points: 58 (30 P2 unit + 14 P3 unit + 14 integration) ≥ 20 required
- Original node IDs removed across R-6..R-10: 0

## Stage status

### R-6 — relation_contract → pipeline/contracts/  — CLOSED
- Canonical: pipeline/contracts/relation_contract.py (RelationContract, make_contract)
- Old file relation_contract.py = shim (`from pipeline.contracts.relation_contract import *`)
- 546 passed / 52 subtests; 0 node IDs added/removed

### R-7 — operator_projection → pipeline/p5_lexical/  — CLOSED
- Canonical: pipeline/p5_lexical/operator_projection.py (OperatorProfile DTO, OPERATOR_PROFILE, get_profile)
- Old file operator_id_map.py = shim
- Operator contracts unchanged (blocks_root_path=True, opens_relation=True):
  لِ=LI بِ=BI وَ=WA مِنْ=MIN مَا=MA أَنْ=AN عَنْ=AN_JAR حَتَّى=HATTA لَا=LA — all OPERATOR_BOUNDARY / contract_state=OPEN
- 546 passed / 52 subtests; 0 node IDs added/removed

### R-8 — mabni_projection + mabni_inventory → pipeline/p5_lexical/  — CLOSED
- Canonical: pipeline/p5_lexical/mabni_inventory.py (repo-root data path via parents[2]; inventory byte-identical: 102 entries)
- Canonical: pipeline/p5_lexical/mabni_projection.py (process_mabni, MabniBoundary/MabniOpen/MabniBlocked, relation-contract binding)
- Old files mabni_inventory.py, mabni_layer.py = shims (mabni_layer forwards get_inventory)
- Inventory diff before/after: IDENTICAL
- 546 passed / 52 subtests; 0 node IDs added/removed

### R-9 — attachment_projection → pipeline/p2_projection/  — CLOSED
- Canonical single location: pipeline/p2_projection/attachment_projection.py
  (AttachmentRole taxonomy + AttachmentProjection DTO + INFLECTIONAL_SUBJECT_WAW_AL_JAMAA alias)
- Old file pipeline/pre_root/attachment_roles.py = shim; internal consumers (article_projection, pre_root_decision) point at canonical
- PreRootDecision still consumes projection; residual host passes through:
  أَنَّهُمْ → host=أَنَّ, هُمْ=operator_complement_suffix
  الْأَطْفَالُ → prefix=definite_article, host=أَطْفَالُ
  الشَّجَرَةِ → host=شَجَرَةِ (solar assimilation shadda stripped, no duplicated ش)
- 546 passed / 52 subtests; 0 node IDs added/removed

### R-10 — HR2S ↔ RootProjection P2 + RootCandidate P3  — CLOSED
- pipeline/p2_projection/root_projection.py: RootProjection (frozen), project_root / project_root_from_pre_root,
  RootProjectionContractError. Duck-typed on ExternalRootAnalysis — no internal hr2s import.
- pipeline/p3_candidate/root_candidate.py: RootCandidate (frozen), RootCandidate.from_projection,
  RootCandidateContractError. No HR2S call, no surface read.
- Import policy honored: only `from hr2s import MorphologyEngine` (inside the pre-existing adapter). HR2S not modified.

## Reference-word results (R-10)
HR2S engine is not installed in this workspace; HR2S-dependent cases are exercised with a
fake engine that matches the real public schema (identical to the existing adapter test),
so the projection contract is fully validated. Boundary short-circuit cases require no engine.

| word | pre-root/route | HR2S calls | directive | canonical_root | note |
|------|----------------|-----------|-----------|----------------|------|
| ضَرَبَ | OPEN | 1 | ACCEPT | (ض,ر,ب) | stage_state OPENED |
| قَرَأَ | OPEN | 1 | ACCEPT | (ق,ر,ء) | ء preserved, not أ |
| مَدَّ | OPEN | 1 | ACCEPT | (م,د,د) | doubled root |
| قَالَ | OPEN | 1 | DEFER | None | no (ق,ا,ل) |
| دَعَا | OPEN | 1 | DEFER | None | no ا identity (contract) |
| وَقَى | OPEN | 1 | DEFER | None | root_profile weakness=LAFIF_MAFRUQ preserved |
| قُلْ | OPEN | 1 | DEFER | None | UnknownRadical preserved, no ACCEPT |
| مِنْ | PreRoot BLOCK | 0 | BLOCK | None | stage_state NOT_OPENED |
| عَلَى | PreRoot DEFER | 0 | DEFER | None | no root hypothesis |
| أَنَّهُمْ | operator_host=أَنَّ → BLOCK | 0 | BLOCK | None | HR2S not called |
| الْأَطْفَالُ | OPEN | 1 | ACCEPT | (ط,ف,ل) | engine received أَطْفَالُ (no article in payload) |
| الشَّجَرَةِ | (host شَجَرَةِ) | — | — | — | analyzed_host شَجَرَةِ, no duplicated ش (R-9) |
| تَرَكَتْهُمْ | OPEN | 1 | ACCEPT | — | engine received تَرَكَتْ (suffix separated) |

## Contract errors implemented
- RootProjectionContractError: ACCEPT with no resolved root / UnknownRadical / ا|ى identity / unknown directive.
- RootCandidateContractError: same ACCEPT guards + BLOCK/DEFER-carrying-root + unknown directive.

## Constraints honored
- HR2S internals untouched; no root code copied into Hokom; only approved public import.
- No changes to DAL / LAFZI / P4 law / slot patterns / data/02_mabniyat JSON.
- No lexical text exceptions; no wazn/bab/masdar/derivation implemented.
- No commit/tag/merge created. boundary/models.py untouched. Original logical node IDs unchanged.
- Shim pattern applied for every moved code file (R-6..R-9). Tests not relocated (R-phase rule).
