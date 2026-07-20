# SlotGraph Boundary Mapping — HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME

## Center Construction

```python
center = Center(
    identity_claim=anchor,       # = claim_id (includes original_surface)
    domain='hokom_morphology',
    scope=morphological_center,  # = segment_host (FIXED from original_surface)
    trace_ref=TraceRef(anchor=anchor, kind='hokom_claim'),
)
```

## Proclitic / Article / Enclitic Boundaries

The SegmentBundle fields are now wired to the claim bundle. The current bridge
uses them for the clitic-only gate but does NOT yet build explicit proclitic/enclitic
Slot objects in the SlotGraph. The SlotGraph currently models:

| Slot | Purpose | State |
|------|---------|-------|
| `domain_claim` | domain_directive (ACCEPT/DEFER/BLOCK) | FILLED or EMPTY |
| `word_class_claim` | ISM/FI3L/HARF (when available) | FILLED (optional) |

Proclitic/article/enclitic boundary expansion into Slots is the NEXT integration
step (not in scope for this resume phase). The fields are wired through so the
next phase can use them without pipeline changes.

## Clitic-Only Gate

```
if morphology_blocked OR segment_clitic_only:
    → DEFERRED (reason: SEGMENTATION_NO_LEXICAL_HOST)
    → No SlotGraph built
    → Center.scope = None (no morphological center exists)
```

## Canonical Examples

| Token | Proclitics | Host (Center.scope) | Enclitics |
|-------|-----------|---------------------|-----------|
| بِدَيْنٍ | ('بِ',) | دَيْنٍ | () |
| بِالْعَدْلِ | ('بِ',) | عَدْلِ | () |
| وَلْيَكْتُبْ | ('وَ','لْ') | يَكْتُبْ | () |
| مِنْهُ | () | مِنْ | ('هُ',) |
| لِلشَّهَادَةِ | ('لِ',) | شَّهَادَةِ | () |
| وَلِيُّهُ | () | وَلِيُّ | ('هُ',) |
| بِكُمْ | ('بِ',) | None (clitic-only) | ('كُمْ',) |
