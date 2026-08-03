# CONSTITUTIONAL RECONCILIATION — 01

**Document ID:** `CONSTITUTIONAL_RECONCILIATION_01`  
**Issued:** 2026-08-01  
**Authority:** HOKOM_TAAQOL_MASTER_EXECUTION_CONSTITUTION_01 (§2, §4, §5)  
**Status:** APPLIED

---

## Purpose

This document records all reclassifications, corrections, and scope changes
applied to previously emitted artifacts pursuant to the HOKOM × TAAQOL-GPT
Integration Master Execution Constitution (hereinafter: the Constitutional
Order), issued 2026-08-01.

No code was deleted. No frozen file was modified. Only:
- File headers updated to reflect correct phase labels
- Gate values corrected in the E0 certificate
- Requirements documents updated (files 09, 13, 14)
- New files emitted: SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01.md,
  E0_BASELINE_FREEZE.json, E1_LEXICAL_REGISTRY.json

---

## I. Phase Reclassification Map

| Old Label | Old Scope | New Phase | New Scope |
|---|---|---|---|
| E0_A0_REGISTRY_LOOKUP | Registry schema freeze + registry_matches fix | E1/E2 | E1 = registry content; E2 = P2 projection using E1 |
| E0_A1_LICENSING_BOUNDARY | LicensingBoundaryVerdict adapter (E0 scope) | E4A / E4C | E4A = precondition guards (DONE); E4C = full verdict chain |
| E0_G_E0_04=1 | Claimed: LicensingBoundaryVerdict produced | INCORRECT | Adapter returns BLOCKED_PHONOLOGICAL_CHAIN — verdict NOT produced |
| E0_G_E0_07 | MaqamContextBoundary in E0 | TRANSFERRED | MaqamContextBoundary → E7_FORMAL_SHAPE_AND_MUFRAD_DALALAH |

---

## II. Artifact Corrections

### II-A. E0_SCHEMA_FREEZE_PARTIAL.json

**Error:** `G_E0_04 = 1` with note claiming "LicensingBoundaryVerdict produced".  
**Fact:** `licensing_boundary_adapter.py` returns `BLOCKED_PHONOLOGICAL_CHAIN` for all
ISM/FI3L inputs (correct fail-closed behavior) but does NOT produce a
`LicensingBoundaryVerdict`. A BLOCKED adapter ≠ a closed gate.  
**Correction:** `G_E0_04 = 0` under old E0 gate definition.

**Error:** `G_E0_07 = 0` — "MaqamContextBoundary is E6+ scope. Gate G_E0_07 must
be redefined or removed from E0 acceptance criteria."  
**Correction:** G_E0_07 REMOVED from E0. Not a blocking residual — it is out-of-scope.
MaqamContextBoundary is E7 scope (requires SemanticSlotFrame).

**Correction applied:** See `E0_BASELINE_FREEZE.json` (new certificate under
reclassified E0 = TARGET BASELINE FREEZE).

### II-B. registry_adapter.py

**Old header:** "Phase: E0 — Registry Schema Freeze"  
**New header:** "Phase: E1/E2_PROVISIONAL_IMPLEMENTATION_ARTIFACT"  
**Reason:** File implements A0_REGISTRY_LOOKUP which is an E1/E2 deliverable
(E1 = registry content, E2 = P2 projection). Under the constitutional
reclassification, E0 contains no production implementation.

### II-C. licensing_boundary_adapter.py

**Old header:** "Phase: E0 — Registry Schema Freeze (interface definition)"  
**New header:** "Phase: E4A_PRECONDITION_GUARD_AND_TYPED_ENTRY_SURFACE"  
**Reason:** The precondition guards (HARF, directive, empty host, vendor check)
constitute E4A. The full verdict chain (ELIGIBLE) is E4C scope.

---

## III. Requirements Document Corrections

### III-A. 09_CONTEXT_AND_MAQAM_REQUIREMENTS.md

**Old §5 item 1:** "A17 runs in E0"  
**New §5 item 1:** "A17 runs in E7 (MaqamContextBoundary requires SemanticSlotFrame,
which is produced in E7_FORMAL_SHAPE_AND_MUFRAD_DALALAH)"

### III-B. 13_STAGE_ACCEPTANCE_GATES.md

- E0 gates completely redefined: BASELINE FREEZE (SHAs + source-derived
  dependency doc) — no implementation gates.
- E0 gate count: 7 (not 13).
- E1–E4 gates added (new phases).
- E4 split into E4A / E4B / E4C subphases.
- G_E0_07 (MaqamContextBoundary) REMOVED from E0; added to E7 gates.
- Old E5–E8 gates renumbered to E9–E12 under new phase ordering.
  (See SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01.md for full ordering.)

### III-C. 14_IMPLEMENTATION_DEPENDENCY_GRAPH.md

- E0 row: MaqamContextBoundary and A0/A1 adapters REMOVED.
  E0 now lists only SHA-verification and dependency-ordering artifacts.
- E1/E2/E3/E4A/E4B/E4C rows added.
- E5+ rows renumbered.

---

## IV. Source-Derived Ordering Confirmation

The WeightFitCandidate.source field is TYPE-ENFORCED to require a
WeightReadinessCandidate (verified by reading vendor/weight_fit.py line 85).

The WeightReadinessCandidate.surface field is TYPE-ENFORCED to require a
PreWeightSurface (verified by reading vendor/pre_weight.py line 370).

Therefore the source-derived dependency chain for a LICENSED verdict is:

```
Arabic text (diacritical) → (letter, haraka) decomposition
  → SyllableCandidate (μ_seq)
  → SyllableSequenceCandidate (μ_boundary)
  → WordBoundaryCandidate (μ_word_carrier)
  → WordCarrierCandidate (μ_path_gate)
  → PathCandidate (μ_root_stem)
  → RootStemCandidate (μ_original_extra)
  → OriginalExtraMap (μ_ops)
  → OperationTraceCandidate (μ_weight_readiness)
  → PreWeightSurface
  → WeightReadinessCandidate  ← required by WeightFitCandidate.source
  → WeightFitCandidate (weigh())
  → omega_governance() → ResidualGovernanceVerdict
  → BoundaryEvidence(LEXICAL, ...)
  → assess_license(candidate, evidence, governance) → LicensingBoundaryResult
  → LicensingBoundaryVerdict  ← required by prove_dal()
  → DalOnlyCandidate
```

This chain is E4B (μ chain) + E4C (licensing verdict) + E5 (DalOnly).
No phase ordering violation is permitted.

See: `SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01.md` for full details.

---

## V. Binding Constraints Carried Forward

- VENDOR_SHA = `35381739410071ac21dd96702ecbb2acb493f90d` — FROZEN
- HOKOM_HEAD = `8e37b738ece7183818189146912cb14e3dce3a07` — FROZEN
- Corpus SHA = `6bd635a05530965f13f76cf003f7738130badec6981bcb0e73f2465d386e1ed7` — FROZEN
- AUTONOMOUS_COMMIT_MODE = 0
- VENDOR_UPDATE_ALLOWED = 0
- FROZEN_FILE_OVERRIDE = 0
- LIVE_PROVIDER_ALLOWED = 0
- No commit. No tag. No push. No merge.

---

## VI. Remaining Blocking Items After Reconciliation

| Phase | Item | Status |
|---|---|---|
| E0 | VENDOR_SHA / HOKOM_HEAD / Corpus SHA frozen | CONFIRMED |
| E0 | Source-derived dependency ordering documented | DONE (SOURCE_DERIVED_DEPENDENCY_AMENDMENT_01.md) |
| E0 | Closure certificate | EMITTED (E0_BASELINE_FREEZE.json) |
| E1 | Registry: 74 entries built + tests | FILE CREATED; tests pending |
| E2 | registry_adapter.py → imports from E1 | PENDING |
| E3 | P3/P4/P5 continuity trace | NOT STARTED |
| E4A | Precondition guards | DONE (licensing_boundary_adapter.py) |
| E4B | μ chain (Arabic diacritical → WeightReadinessCandidate) | NOT STARTED |
| E4C | Full licensing verdict chain | NOT STARTED |

---

*Reconciliation applied by autonomous execution agent per §15 of the Constitutional Order.*
