# Segment-Aware Claim Contract — HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME

## Invariant

```
ORIGINAL_SURFACE_AS_CENTER_SCOPE = FORBIDDEN

Center.scope MUST be segment_host (lexical host after clitic segmentation).
original_surface is PROVENANCE ONLY — never morphological identity.
```

## HokomLinguisticClaimBundle Fields (Amendment No. 3)

| Field | Type | Source | Contract |
|-------|------|---------|----------|
| `segment_bundle` | SegmentBundle\|None | P0 segmentation output | Full segmentation result |
| `morphology_surface` | str\|None | segment_bundle.host | Convenience alias for segment_host |
| `morphology_blocked` | bool | host is None | True → no morphological analysis |
| `morphology_block_reason` | str\|None | pipeline | Reason code for blocking |
| `segment_host` | str\|None | segment_bundle.host | Canonical morphological center |
| `segment_proclitics` | tuple[str] | segment_bundle.proclitics | Left-boundary clitics |
| `segment_definite_article` | str\|None | segment_bundle.definite_article | ال boundary |
| `segment_enclitics` | tuple[str] | segment_bundle.enclitics | Right-boundary clitics |
| `segment_clitic_only` | bool | segment_bundle.clitic_only | True → host is None |
| `segment_verdict` | str\|None | str(segment_bundle.verdict) | SegmentationVerdict string |

## Bridge Contract

1. `_morphological_center` computed BEFORE Taaqol import (all paths see it)
2. Clitic-only gate BEFORE SlotGraph build (when Taaqol available)
3. `Center.scope = _morphological_center` (not original_surface)
4. `taaqol_center_scope` exposed in HokomTaaqolDecision output

## Provenance Chain

```
hokom(token) → _hokom_result_partial → bundle_from_hokom_result()
    → HokomLinguisticClaimBundle
        .original_surface   = full token (provenance)
        .segment_host       = lexical host (morphological center)
        .claim_id           = f'hokom:{token_id}:{original_surface}'
    → evaluate_hokom_claim_bundle()
        → Center.scope = segment_host (NOT original_surface)
        → HokomTaaqolDecision
            .taaqol_center_scope = segment_host
            .bridge_id = HOKOM_TAAQOL_LIVE_BRIDGE (provenance anchor)
```
