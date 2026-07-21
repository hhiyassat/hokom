# HOKOM-TAAQOL-SGA-BASELINE — Stage 0

## Version Identity
- **HEAD**: 02918a6f9bd33f89352ca64ea70c432c2d16a05e
- **Branch**: main
- **Taaqol vendor SHA**: 35381739410071ac21dd96702ecbb2acb493f90d
- **Python (VM)**: 3.10.12 (canonical: 3.12.4 on macOS .venv-py312)
- **Taaqol import**: UNAVAILABLE on Python 3.10 (StrEnum requires 3.11+)
- **Bridge fail-closed**: YES — returns DEFERRED with TAAQOL_RUNTIME_UNAVAILABLE

## Test Suite State
- 5413 passed, 55 skipped, 13 failed
- All 13 failures are Python-version / venv / closure-manifest governance checks (expected in VM)
- Zero domain-logic failures

## Architecture Ownership Map
| Layer | Owner |
|-------|-------|
| SlotGraph, Gamma, TransitionGate, RankLattice, TraceLedger, EvidenceContract | TAAQOL (vendor) |
| Arabic linguistic domain, claim profiles, typed slots | HOKOM (to be created in pipeline/sga/contracts.py) |
| Mapping between domain and Taaqol API | BRIDGE (pipeline/taaqol_integration/live/bridge.py) |

## Existing Key Files
- pipeline/taaqol_integration/live/bridge.py — canonical entrypoint `evaluate_hokom_claim_bundle`
- pipeline/taaqol_integration/live/models.py — HokomTaaqolDecision, HokomTaaqolTraceEvent
- pipeline/taaqol_integration/claim_adapter.py — bundle_from_hokom_result
- pipeline/taaqol_integration/provider_models.py — HokomLinguisticClaimBundle
- pipeline/taaqol_integration/constitutional_contracts.py — ClaimProvenance, RealityDomain

## Missing (Stage 1 Creates)
- pipeline/sga/ (module does not exist)
- pipeline/sga/contracts.py (canonical typed slot definitions)
- tests/sga/ (test module does not exist)

## SGA Violation Summary (from prior audit)
- T-01 RESOLVED: repo root path bug fixed
- T-02..T-14 OPEN: 13 violations including untyped slots, missing claim slots, no AMBIGUOUS state,
  non-deterministic claim_id, opaque trace, missing serialization, untyped residuals

## Architectural Blocker Assessment
- Duplicate SlotGraph/TransitionGate in Hokom? NO
- Taaqol public API broken? NO (unavailable on Python 3.10, works on 3.11+)
- Bridge API cannot be extended? NO (extensible)
- Python < 3.11? YES in VM, NO on canonical macOS runtime
- **Stage 1 contracts.py requires only Python 3.10+ (str,Enum only, no StrEnum)**
- **DECISION: NO ARCHITECTURAL BLOCKER for Stage 1**
