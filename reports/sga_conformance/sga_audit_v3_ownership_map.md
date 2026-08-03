# SGA Conformance Audit — Ownership Map
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### Bridge Ownership Gate

| Field | Value |
|-------|-------|
| bridge_id | HOKOM_TAAQOL_LIVE_BRIDGE |
| integration_owner | HOKOM |
| integration_mode | STRICT |
| canonical_entrypoint | evaluate_hokom_claim_bundle |
| parallel_bridges | 0 |
| parallel_decision_engines | 0 |
| silent_fallbacks | 0 |
| fail_closed | True |
| strict_mode_active | True |
| slot_graph_wired | True |
| gamma_wired | True |
| transition_gate_wired | True |
| upstream_upgrades_forbidden | True |
| vendor_unmodified | True |
| status | CLOSED |

### File Ownership

| Module | Owner | Path |
|--------|-------|------|
| Canonical entrypoint | HOKOM | pipeline/taaqol_integration/live/bridge.py |
| Decision models | HOKOM | pipeline/taaqol_integration/live/models.py |
| Claim adapter | HOKOM | pipeline/taaqol_integration/claim_adapter.py |
| Pipeline driver | HOKOM | hokom_pipeline.py |
| Phonological slots | HOKOM | pipeline/p1_atomic_structure/cell_builder.py |
| Slot engineering algebra | HOKOM | pipeline/p1_atomic_structure/slot_engineering.py |
| Radical accounting | HOKOM | pipeline/p3_pre_root/canonical_radical_accounting.py |
| Functional lexical lookup | HOKOM | pipeline/p5_lexical/functional_lexical_lookup.py |
| Mabni inventory | HOKOM | pipeline/p5_lexical/mabni_inventory.py |
| Canonical gate (liveness) | HOKOM | scripts/canonical_gate.py |
| SlotGraph kernel | TAAQOL (vendor) | vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/slot_graph.py |
| Gamma function | TAAQOL (vendor) | vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/gamma.py |
| TransitionGate | TAAQOL (vendor) | vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/transition_gate.py |
| RankLattice | TAAQOL (vendor) | vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/rank_lattice.py |
| EvidenceContract | TAAQOL (vendor) | vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/evidence_contract.py |
| TraceLedger | TAAQOL (vendor) | vendor/Taaqol-GPT/src/taaqqul_slot_geometry/core/trace_ledger.py |

### Invariants Confirmed

- No parallel decision engines wired (TaaqolIntegrationOwnershipGate.parallel_decision_engines == 0)
- No silent fallbacks (silent_fallbacks == 0)
- Fail-closed confirmed: ImportError → DEFERRED, not LICENSED
- Vendor pin matches expected: 35381739410071ac21dd96702ecbb2acb493f90d
