# Full-Token Center Prohibition Proof — HOKOM-TAAQOL-LIVE-INTEGRATION-01-RESUME

## Invariant

```
FULL_TOKEN_CENTER = FORBIDDEN when segment_host differs from original_surface
```

## Implementation

```python
# bridge.py — _build_slot_graph()
morphological_center = (
    getattr(bundle, 'segment_host', None)
    or getattr(bundle, 'morphology_surface', None)
    or _original_surface   # only when NO segmentation data at all
)
center = Center(
    scope=morphological_center,  # NEVER original_surface when host is available
    ...
)
```

## Proof by exhaustion — Ayat al-Dayn (129 tokens)

Run: 2026-07-20
Result: FULL_TOKEN_CENTER_VIOLATIONS = 0

Cases where split occurred (center differs from original_surface):
- بِدَيْنٍ: center='دَيْنٍ' ≠ 'بِدَيْنٍ' ✓
- بِالْعَدْلِ: center='عَدْلِ' ≠ 'بِالْعَدْلِ' ✓
- وَلْيَكْتُبْ: center='يَكْتُبْ' ≠ 'وَلْيَكْتُبْ' ✓
- فَلْيَكْتُبْ: center='يَكْتُبْ' ≠ 'فَلْيَكْتُبْ' ✓
- مِنْهُ: center='مِنْ' ≠ 'مِنْهُ' ✓
- لِلشَّهَادَةِ: center='شْشَهَادَةِ' ≠ 'لِلشَّهَادَةِ' ✓
- وَلَا: center='لَا' ≠ 'وَلَا' ✓
- أَجَلِهِ: center='ءَجَلِ' ≠ 'أَجَلِهِ' ✓
- [and 40+ more split cases] ✓

## Test coverage

- `test_no_full_token_center.py` — parametric coverage of 8 split cases
- `test_segment_aware_slot_graph.py` — parametric coverage of 6 split cases
- `test_ayat_al_dayn_segment_aware.py` — 17 canonical §16 cases
