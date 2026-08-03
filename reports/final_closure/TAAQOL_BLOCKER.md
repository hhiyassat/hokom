# TAAQOL_STAGE_REGISTRY_COUNT_MISMATCH — BLOCKER

**Status:** ACTIVE  
**Date:** 2026-07-31  
**Severity:** BLOCKER — prevents TAAQOL_49_STAGE_CLOSURE = CLOSED  

## Finding

The Taaqol vendor constitution (`vendor/Taaqol-GPT/`) does **not** declare a 49-stage canonical pipeline.

The document `docs/49_META_LANGUAGE_BOUNDARY_COVENANT.md` is **PV-M0 — a law covenant**.  
The number 49 is a **document index** (document #49 in the vendor doc series), not a stage count.

**Expected (from mandate):** 49 stages  
**Proven from constitution:** 7 stages (core pipeline)  

## Constitutional Source

`vendor/Taaqol-GPT/docs/14_PR_CHAIN_ROADMAP.md` — the authoritative PR chain roadmap.  
The core pipeline is: `Trace → SlotGraph → Gamma → EvidenceContract → RankLattice → ResidualPolicy → TransitionGate`

## Impact

| Gate | Status |
|------|--------|
| TAAQOL_49_STAGE_CLOSURE | CANNOT_BE_CLOSED |
| HOKOM_19_STAGE_CLOSURE | CLOSED |
| Execution ledger | Operational (7 proven Taaqol stages documented) |
| Tests | Passing |

## Resolution Path

To close this blocker, the Taaqol constitutional source must declare:  
`CANONICAL_TAAQOL_STAGE_COUNT = 49` with each stage named and evidenced.

Until then: the blocker remains ACTIVE. The system operates on the proven 7-stage core.
