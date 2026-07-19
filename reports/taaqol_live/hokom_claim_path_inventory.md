# Hokom Claim Path Inventory — HOKOM-TAAQOL-LIVE-INTEGRATION-01

## Canonical Entrypoint

`evaluate_hokom_claim_bundle` in `pipeline.taaqol_integration.live.bridge`

## Claim Flow

1. **hokom(word)** — Full morphology pipeline (P0→P5 + Word Class + Phase 5) → `dict`
2. **bundle_from_hokom_result(result)** — `pipeline.taaqol_integration.claim_adapter` → `HokomLinguisticClaimBundle`
3. **evaluate_hokom_claim_bundle(bundle)** — `pipeline.taaqol_integration.live.bridge` → `HokomTaaqolDecision`
   - Step 1: Import taaqqul_slot_geometry (fail-closed on ImportError → DEFERRED)
   - Step 2: `_build_slot_graph(bundle)` → `SlotGraph`
   - Step 3: `gamma(slot_graph)` → `GammaResult`
   - Step 4: `_build_evidence_contract(bundle)` → `EvidenceContract`
   - Step 5: `TransitionGate("HOKOM_TAAQOL_GATE", Rank.STRONG).decide(graph, Layer.CANDIDATE, evidence)` → `TransitionVerdict`
   - Step 6: Map `TransitionState` → `taaqol_verdict` string
   - Step 7: `compose_effective_verdict(upstream, taaqol)` → `effective_verdict`

## Non-Wired Stages

- `p5_masdar`: NOT wired (claims never fabricated)
- `p6_derivatives`: NOT wired (claims never fabricated)

## Bundle → SlotGraph Mapping

| domain_directive | SlotState | Residual | Rank |
|-----------------|-----------|----------|------|
| ACCEPT | FILLED | none | HYPOTHESIS |
| BLOCK | EMPTY | BLOCKING | CANDIDATE |
| DEFER | EMPTY | none | CANDIDATE |
| other | EMPTY | none | CANDIDATE |
