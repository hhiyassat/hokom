# SGA Ownership Proof
**Stage**: HOKOM-TAAQOL-SGA-CONSTITUTIONAL-CONVERGENCE-01
**Commit**: ee418b6
**Integration Owner**: HOKOM
**Bridge Owner**: HOKOM (via TaaqolIntegrationOwnershipGate)

## Ownership Invariants

- `TaaqolIntegrationOwnershipGate.integration_owner == 'HOKOM'`
- `TaaqolIntegrationOwnershipGate.integration_mode == 'STRICT'`
- `parallel_bridges == 0`
- `parallel_decision_engines == 0`
- `silent_fallbacks == 0`
- `fail_closed == True`
- `strict_mode_active == True`

## Canonical Entrypoints

- `evaluate_hokom_claim_bundle(bundle: HokomLinguisticClaimBundle)` — legacy entrypoint
- `evaluate_sga_bundle(sga_bundle: HokomClaimBundle)` — T-03 typed SGA entrypoint (SGA_CANONICAL_ENTRYPOINT)

No other `evaluate_*` functions exist in the live bridge (enforced by `test_only_one_canonical_entrypoint`).

## Slot Ownership

All `TypedSlot.owner == 'HOKOM'`. Bridge sets slot values; Taaqol reads slot geometry.
Taaqol never mutates slot values — it only evaluates closure state.

## Commits Closing Tasks

| Task | Commit | Message |
|------|--------|---------|
| T-02 | 24eaa81 | feat(sga): complete typed phonological caller boundaries (T-02) |
| T-03 | a8751a6 | feat(sga): require HokomClaimBundle at live bridge boundary (T-03) |
| T-09 | c1cfbf7 | feat(sga): adapt H11-H15 morphology outputs to typed slots (T-09) |
| T-10 | 88f09ff | feat(sga): preserve ambiguous candidate sets through bridge (T-10) |

## Constitutional Violation Status

All violation counters: **0**
Bridge expressivity status: **FULL**
