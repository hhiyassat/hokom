# Hokom — Plan / Phase Status Board

المسار التشغيلي المغلق:

```
P0–P4
→ P5 segmentation / lexical boundary
→ PreRootDecision
→ (OPEN) HR2SRootAdapter → ExternalRootAnalysis
→ RootProjection P2
→ RootCandidate P3
→ WaznProjection Phase 4A
```

## Refactoring (R-6 → R-10) — CLOSED
- R-6 relation_contract → `pipeline/contracts/` — CLOSED
- R-7 operator_projection → `pipeline/p5_lexical/` — CLOSED
- R-8 mabni_projection/inventory → `pipeline/p5_lexical/` — CLOSED
- R-9 attachment_projection → `pipeline/p2_projection/` — CLOSED
- R-10 RootProjection P2 + RootCandidate P3 — CLOSED

## Morphology phases

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 4A — Wazn Projection      | root→surface geometry, licensed pattern candidates, ziyadah, alignment, surface operations | **IMPLEMENTED** |
| Phase 4B — Bab Candidate        | باب الفعل / المضارع المقابل | NOT STARTED |
| Phase 4C — Masdar Projection    | المصدر | NOT STARTED |
| Phase 4D — Mushtaqat Licensing  | المشتقات | NOT STARTED |

### Phase 4A summary
- Source of truth: `pipeline/p4_wazn/` (models, wazn_catalog, alignment, ziyadah_audit,
  weak_operations, wazn_projection). Catalog: `data/wazn/wazn_catalog.json`.
- Consumes `RootCandidate` only. No HR2S call/import. `canonical_root` never mutated.
- Monotonicity enforced: Root DEFER/BLOCK ⇒ Wazn NOT_OPENED (no alignment).
- Reference suite: 658 passed, 52 subtests (590 preserved + 68 new).
  Phase 4A integration: 26 passed. Original node IDs removed: 0.
- Docs: `docs/morphology/PHASE_4A_WAZN_PROJECTION.md`.

> Phase 4B does not start before Phase 4A closure report is reviewed and approved.

## Phase 4A-α + P3.11 — CLOSED (2026-07-16)

- **P4A-α WaznHypothesis**: `pipeline/p4_wazn/hypothesis.py` — كشف الزيادة الداخلية (MIM_ZIYADAH, ALIF_WASL+SIN+TA) وبناء فرضية الوزن لحالات DEFER.
- **P3.11 Root Re-Licensing**: `pipeline/p3_candidate/root_relicensing.py` — بوابة ترخيص الجذر المقترح من WaznHypothesis.
- **Phase4A Orchestrator**: `pipeline/p4_wazn/phase4a_orchestrator.py` — تجميع السلسلة: BLOCK/ACCEPT/DEFER → فرضية → ترخيص → إسقاط.
- Reference suite: 683 passed, 52 subtests (646 preserved + 37 new).
- Docs: `docs/morphology/PHASE_4A_WAZN_HYPOTHESIS.md`, `docs/morphology/ROOT_RELICENSING_FROM_WAZN.md`.
- Report: `reports/phase4a_hypothesis/`.
