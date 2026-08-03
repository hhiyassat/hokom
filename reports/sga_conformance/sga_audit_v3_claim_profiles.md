# SGA Conformance Audit — Claim Profiles
## HOKOM-TAAQOL-SLOT-GEOMETRY-ALGEBRA-CONFORMANCE-01

### Claim Slots Built by Bridge (_build_slot_graph)

The bridge at `pipeline/taaqol_integration/live/bridge.py` builds exactly 1 or 2 slots:

| Slot | Condition | SlotState (initial) | Rank |
|------|-----------|---------------------|------|
| domain_claim | Always present | FILLED (directive=ACCEPT) or BROKEN (BLOCK/DEFER) | HYPOTHESIS (ACCEPT) or CANDIDATE (non-ACCEPT) |
| word_class_claim | Only if bundle.lexical_class is not None | FILLED or BROKEN | HYPOTHESIS (ACCEPT) or CANDIDATE |

### Claim Slots Absent (SGA Violations T-03 through T-07)

The following claim types carried in HokomLinguisticClaimBundle are NOT projected into SlotGraph slots:

| Missing Slot | Bundle Field | Violation |
|---|---|---|
| ROOT_CLAIM | root_claim | T-03 |
| PATTERN_CLAIM | wazn_claim / form_claim | T-04 |
| BAB_CLAIM | (verb stem class) | T-05 |
| MASDAR_CLAIM | masdar_claim | T-06 |
| DERIVATIVE_CLAIM | mushtaq_claims | T-07 |

### Claim ID Contract

| Field | Expected | Actual | Status |
|-------|----------|--------|--------|
| claim_id format | Deterministic content-hash | `f'hokom:{token_id or uuid4().hex[:12]}:{surface}'` | VIOLATION T-11 |
| token_id source | Deterministic | `uuid.uuid4().hex[:16]` in hokom_pipeline.py line ~999 | Non-deterministic |

### EvidenceContract Mapping

The bridge maps `bundle.evidence_ids` to EvidenceSource items with rank heuristics:
- Strings containing 'cert' → Rank.CERTIFICATE
- Strings containing 'strong' or 'corpus' → Rank.STRONG
- Strings containing 'licensed' or 'attested' → Rank.LICENSED
- Default → Rank.CANDIDATE

RankLattice.meet() is called through TransitionGate.decide(), not applied manually.

### Bundle Input Fields (HokomLinguisticClaimBundle)

All fields carried but not fully projected:
- claim_id, token_id, original_surface, normalized_surface, refined_host
- lexical_class, part_of_speech
- root_claim, wazn_claim, form_claim, masdar_claim, mushtaq_claims (NOT slotted)
- inflection_claim, attachment_claims
- domain_directive (ACCEPT/BLOCK/DEFER)
- evidence_ids, trace_ids
- active_residuals (block:/defer: prefixes → ResidualKind)
- resolved_residuals
- segment_host, segment_proclitics, segment_definite_article, segment_enclitics
- segment_clitic_only, segment_verdict
